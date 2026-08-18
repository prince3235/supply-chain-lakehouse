import yaml

def load_registry(path="configs/datasets.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)["datasets"]
