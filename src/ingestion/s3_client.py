import boto3
import time
from .exceptions import S3UploadError

class S3Client:
    def __init__(self, region_name):
        self.s3 = boto3.client("s3", region_name=region_name)
        
    def upload_file(self, local_path, bucket, key, metadata, max_retries=3):
        attempt = 0
        while attempt < max_retries:
            try:
                self.s3.upload_file(
                    local_path, bucket, key,
                    ExtraArgs={"Metadata": metadata}
                )
                return
            except Exception as e:
                attempt += 1
                time.sleep(2 ** attempt)
        raise S3UploadError(f"Failed to upload {local_path} to s3://{bucket}/{key}")
