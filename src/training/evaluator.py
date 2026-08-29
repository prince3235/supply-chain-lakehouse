"""
Champion vs Challenger Model Evaluation & Promotion Gate.
Enforces rigorous quality thresholds before allowing models into Production.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.training.registry import ModelRegistry, ModelStage


@dataclass
class PromotionDecision:
    promoted: bool
    status: str  # "PROMOTED", "REJECTED", "INITIAL_PROMOTION"
    reason: str
    champion_version: Optional[int]
    challenger_version: int
    champion_metrics: Optional[Dict[str, float]]
    challenger_metrics: Dict[str, float]
    improvement_pct: Optional[float]


class ChampionChallengerEvaluator:
    """
    Evaluates new candidate models against the active Production Champion.
    """

    def __init__(
        self,
        registry: ModelRegistry,
        min_improvement_pct: float = 3.0,
        max_allowable_bias_pct: float = 15.0,
        max_allowable_wape: float = 50.0,
    ):
        self.registry = registry
        self.min_improvement_pct = min_improvement_pct
        self.max_allowable_bias_pct = max_allowable_bias_pct
        self.max_allowable_wape = max_allowable_wape

    def evaluate_and_promote(
        self,
        model_name: str,
        challenger_version: int,
        auto_promote: bool = True,
    ) -> PromotionDecision:
        """
        Executes Champion vs Challenger decision gate.
        """
        versions = self.registry.get_all_versions(model_name)
        challenger_meta = None
        for v in versions:
            if v["version"] == challenger_version:
                challenger_meta = v
                break

        if not challenger_meta:
            raise ValueError(f"Challenger version {challenger_version} not found for model '{model_name}'.")

        challenger_metrics = challenger_meta.get("metrics", {})
        chall_wape = challenger_metrics.get("wape", 999.0)
        chall_bias = abs(challenger_metrics.get("forecast_bias_pct", 0.0))

        # Check basic sanity thresholds
        if chall_wape > self.max_allowable_wape:
            return PromotionDecision(
                promoted=False,
                status="REJECTED",
                reason=f"Challenger WAPE ({chall_wape}%) exceeds maximum allowable threshold ({self.max_allowable_wape}%).",
                champion_version=None,
                challenger_version=challenger_version,
                champion_metrics=None,
                challenger_metrics=challenger_metrics,
                improvement_pct=None,
            )

        if chall_bias > self.max_allowable_bias_pct:
            return PromotionDecision(
                promoted=False,
                status="REJECTED",
                reason=f"Challenger Forecast Bias ({chall_bias}%) exceeds threshold ({self.max_allowable_bias_pct}%).",
                champion_version=None,
                challenger_version=challenger_version,
                champion_metrics=None,
                challenger_metrics=challenger_metrics,
                improvement_pct=None,
            )

        champion_meta = self.registry.get_production_model(model_name)

        # Case 1: No existing production model exists (Initial Launch)
        if not champion_meta:
            if auto_promote:
                self.registry.transition_stage(model_name, challenger_version, ModelStage.PRODUCTION)
            return PromotionDecision(
                promoted=True,
                status="INITIAL_PROMOTION",
                reason="No active Champion found. Challenger promoted as initial Production baseline.",
                champion_version=None,
                challenger_version=challenger_version,
                champion_metrics=None,
                challenger_metrics=challenger_metrics,
                improvement_pct=100.0,
            )

        # Case 2: Active Champion exists -> Compare performance
        champ_metrics = champion_meta.get("metrics", {})
        champ_wape = champ_metrics.get("wape", 999.0)
        champ_ver = champion_meta["version"]

        if champ_wape <= 0.0:
            improvement_pct = 0.0
        else:
            improvement_pct = round(((champ_wape - chall_wape) / champ_wape) * 100.0, 2)

        if improvement_pct >= self.min_improvement_pct:
            if auto_promote:
                self.registry.transition_stage(model_name, challenger_version, ModelStage.PRODUCTION)
            return PromotionDecision(
                promoted=True,
                status="PROMOTED",
                reason=f"Challenger achieved {improvement_pct}% WAPE reduction over Champion v{champ_ver}.",
                champion_version=champ_ver,
                challenger_version=challenger_version,
                champion_metrics=champ_metrics,
                challenger_metrics=challenger_metrics,
                improvement_pct=improvement_pct,
            )
        else:
            return PromotionDecision(
                promoted=False,
                status="REJECTED",
                reason=f"Challenger improvement ({improvement_pct}%) did not meet required threshold ({self.min_improvement_pct}%).",
                champion_version=champ_ver,
                challenger_version=challenger_version,
                champion_metrics=champ_metrics,
                challenger_metrics=challenger_metrics,
                improvement_pct=improvement_pct,
            )
