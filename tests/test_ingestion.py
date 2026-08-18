import pytest
from src.ingestion.config import load_config
from src.ingestion.registry import load_registry

def test_load_config():
    cfg = load_config("configs/ingestion.yaml")
    assert cfg["aws_region"] == "us-east-1"
    assert "bucket_name" in cfg
    
def test_load_registry():
    reg = load_registry("configs/datasets.yaml")
    assert "sales" in reg
    assert "products" in reg
    assert reg["sales"]["primary_key"] == "transaction_id"

def test_missing_config():
    with pytest.raises(FileNotFoundError):
        load_config("configs/nonexistent.yaml")
