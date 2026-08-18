from .schema_validator import validate_schema

def validate_contract(file_path, registry_entry):
    # Enforce basic constraints from registry
    return validate_schema(file_path, registry_entry)
