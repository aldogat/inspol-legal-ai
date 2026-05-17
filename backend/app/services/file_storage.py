import boto3
import io
from app.core.config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
)

async def save_file_to_minio(file, tenant_id: str) -> str:
    key = f"{tenant_id}/{file.filename}"
    content = await file.read()
    await file.seek(0)  # no cerramos, solo rebobinamos
    s3.upload_fileobj(io.BytesIO(content), settings.MINIO_BUCKET, key)
    return key
