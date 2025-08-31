import boto3

from ..core.config import settings

R2_ACCOUNT_ID = settings.r2_account_id
R2_ACCESS_KEY_ID = settings.r2_access_key_id
R2_SECRET_ACCESS_KEY = settings.r2_secret_access_key

# Construct the R2 endpoint URL
R2_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Initialize the S3 client
r2_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)
