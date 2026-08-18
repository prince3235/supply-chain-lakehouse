import yaml
import os
from pathlib import Path

def load_config(config_path="configs/data_generation.yaml", profile="small"):
    """
    Load data generation configuration from YAML.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
        
    if "global" not in config_data:
        raise ValueError("Missing 'global' section in configuration.")
    if "profiles" not in config_data:
        raise ValueError("Missing 'profiles' section in configuration.")
    if profile not in config_data["profiles"]:
        raise ValueError(f"Profile '{profile}' not found in configuration.")
    if "quality" not in config_data:
        raise ValueError("Missing 'quality' section in configuration.")
        
    # Merge global, profile-specific, and quality settings
    merged_config = {}
    merged_config.update(config_data["global"])
    merged_config.update(config_data["profiles"][profile])
    merged_config["quality"] = config_data["quality"]
    
    return merged_config
