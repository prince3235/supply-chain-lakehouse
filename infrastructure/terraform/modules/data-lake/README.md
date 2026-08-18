# AWS S3 Data Lake Foundation

This module provisions the foundational S3 Data Lake for the Supply Chain Lakehouse.

## Security Features
- **BucketOwnerEnforced**: Disables ACLs, meaning all objects are owned by the bucket owner.
- **Public Access Block**: Completely blocks all public access to the bucket.
- **Secure Transport Policy**: Denies all HTTP requests, strictly enforcing HTTPS for data transit.
- **SSE-S3 Encryption**: Automatically encrypts all objects at rest.

## Cost Controls
- **Lifecycle Policies**: Incomplete multipart uploads are aborted after 7 days, and noncurrent versions expire after a configurable period (30 days default in dev).
- **Simple Encryption**: Avoids the extra costs associated with KMS for standard environments unless explicitly required.

## Data Lake Logical Zones (Prefixes)
S3 does not use physical folders, but we will organize data conceptually into the following logical prefixes for future phases:

- `landing/`: Temporary source landing area for incoming raw files.
- `raw/`: Immutable original source representation (history).
- `bronze/`: Future Delta Lake raw tables.
- `silver/`: Future cleaned and validated datasets.
- `gold/`: Future business-ready aggregations and facts.
- `features/`: Future ML feature datasets.
- `quarantine/`: Invalid, rejected, or corrupted data that failed validation.
- `checkpoints/`: Future pipeline checkpoint metadata (Spark Structured Streaming).
- `artifacts/`: Data or ML artifacts.

*Note: We do not create empty placeholder objects for these prefixes. They are created on-the-fly when data processing pipelines (Bronze/Silver/Gold) write to them.*
