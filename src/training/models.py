"""
Demand Forecasting Machine Learning Architectures.
Provides unified interface for Random Forest, Gradient Boosting, LightGBM, and Linear regressors.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge


class DemandForecaster:
    """
    Unified forecasting model wrapper supporting multiple regression backends.
    """

    SUPPORTED_MODELS = ["random_forest", "gradient_boosting", "lightgbm", "ridge"]

    def __init__(
        self,
        model_type: str = "gradient_boosting",
        hyperparameters: Optional[Dict[str, Any]] = None,
        feature_names: Optional[List[str]] = None,
    ):
        self.model_type = model_type.lower()
        self.hyperparameters = hyperparameters or {}
        self.feature_names = feature_names or []
        self.model = self._initialize_model()
        self.is_fitted = False

    def _initialize_model(self):
        params = self.hyperparameters.copy()

        if self.model_type == "random_forest":
            default_params = {"n_estimators": 50, "max_depth": 8, "random_state": 42, "n_jobs": 1}
            default_params.update(params)
            return RandomForestRegressor(**default_params)

        elif self.model_type == "gradient_boosting":
            default_params = {"n_estimators": 50, "max_depth": 4, "random_state": 42, "learning_rate": 0.05}
            default_params.update(params)
            return GradientBoostingRegressor(**default_params)

        elif self.model_type == "lightgbm":
            try:
                import lightgbm as lgb
                default_params = {
                    "n_estimators": 50,
                    "max_depth": 4,
                    "learning_rate": 0.05,
                    "random_state": 42,
                    "verbosity": -1,
                }
                default_params.update(params)
                return lgb.LGBMRegressor(**default_params)
            except ImportError:
                default_params = {"n_estimators": 50, "max_depth": 4, "random_state": 42, "learning_rate": 0.05}
                default_params.update(params)
                return GradientBoostingRegressor(**default_params)

        elif self.model_type == "ridge":
            default_params = {"alpha": 1.0, "random_state": 42}
            default_params.update(params)
            return Ridge(**default_params)

        else:
            raise ValueError(f"Unsupported model_type: '{self.model_type}'. Choose from {self.SUPPORTED_MODELS}")

    def fit(self, X: pd.DataFrame, y: Union[np.ndarray, pd.Series]) -> "DemandForecaster":
        """
        Fits the underlying estimator on feature matrix X and target y.
        """
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
            X_mat = X.to_numpy()
        else:
            X_mat = np.asarray(X)

        y_vec = np.asarray(y, dtype=float)

        self.model.fit(X_mat, y_vec)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generates demand forecasts and ensures non-negative output constraint.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict.")

        if isinstance(X, pd.DataFrame):
            if self.feature_names:
                # Align columns exactly with training feature set, filling any missing with 0.0
                aligned_df = pd.DataFrame(index=X.index)
                for col in self.feature_names:
                    aligned_df[col] = X[col].fillna(0.0) if col in X.columns else 0.0
                X_mat = aligned_df.to_numpy()
            else:
                X_mat = X.to_numpy()
        else:
            X_mat = np.asarray(X)

        raw_preds = self.model.predict(X_mat)
        # Supply chain constraint: demand cannot be negative
        return np.maximum(raw_preds, 0.0)

    def get_feature_importances(self) -> Dict[str, float]:
        """
        Returns feature importances mapped by column name.
        """
        if not self.is_fitted or not self.feature_names:
            return {}

        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            return {
                name: float(imp)
                for name, imp in sorted(zip(self.feature_names, importances), key=lambda x: x[1], reverse=True)
            }
        elif hasattr(self.model, "coef_"):
            coefs = np.abs(self.model.coef_)
            return {
                name: float(coef)
                for name, coef in sorted(zip(self.feature_names, coefs), key=lambda x: x[1], reverse=True)
            }
        return {}

