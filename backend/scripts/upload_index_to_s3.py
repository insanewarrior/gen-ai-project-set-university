"""Upload FAISS index files to S3 for Lambda consumption."""

import os
import sys
from pathlib import Path

import boto3

INDEX_DIR = Path("backend/data/faiss_index")
S3_KEY_PREFIX = "faiss_index"

FILES = [
    "index.faiss",
    "index_metadata.json",
]


def main():
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        print("ERROR: S3_BUCKET environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    s3 = boto3.client("s3")

    for filename in FILES:
        local_path = INDEX_DIR / filename
        if not local_path.exists():
            print(f"ERROR: {local_path} does not exist. Run build_faiss_index.py first.", file=sys.stderr)
            sys.exit(1)

        s3_key = f"{S3_KEY_PREFIX}/{filename}"
        print(f"Uploading {local_path} → s3://{bucket}/{s3_key} ...")
        s3.upload_file(str(local_path), bucket, s3_key)
        print(f"  ✓ Uploaded s3://{bucket}/{s3_key}")

    print(f"\nAll {len(FILES)} files uploaded to s3://{bucket}/{S3_KEY_PREFIX}/")


if __name__ == "__main__":
    main()
