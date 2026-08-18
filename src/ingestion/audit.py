import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_audit(batch_id, dataset, operation, status, **kwargs):
    ctx = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    logging.info(f"batch_id={batch_id} dataset={dataset} operation={operation} status={status} {ctx}")
