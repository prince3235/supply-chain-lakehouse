from .s3_client import S3Client
from .partitioning import get_s3_key

def upload(client, local_path, bucket, dataset_config, checksum, batch_id):
    prefix = dataset_config["destination_prefix"]
    key = get_s3_key(prefix, local_path)
    
    metadata = {
        "dataset": dataset_config["source"].split("/")[-1],
        "checksum": checksum,
        "batch_id": batch_id
    }
    
    client.upload_file(local_path, bucket, key, metadata)
    return f"s3://{bucket}/{key}"
