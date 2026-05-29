import os
import uuid
import boto3

BUCKET = os.environ.get("CLOUDFLARE_R2_BUCKET", "diavolo-assets")
ENDPOINT = os.environ.get("CLOUDFLARE_R2_ENDPOINT", "")

TIPOS_PERMITIDOS = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/quicktime", "video/x-msvideo",
}


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=os.environ.get("CLOUDFLARE_R2_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("CLOUDFLARE_R2_SECRET_KEY"),
        region_name="auto",
    )


def _build_key(instagram_username: str, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"clientes/{instagram_username}/{uuid.uuid4().hex}.{ext}"


def _build_public_url(key: str) -> str:
    return f"{ENDPOINT}/{BUCKET}/{key}"


def upload_file(file_data: bytes, key: str, content_type: str) -> str:
    """Sube bytes a R2 y devuelve la URL pública."""
    client = get_r2_client()
    client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=file_data,
        ContentType=content_type,
    )
    return _build_public_url(key)


def delete_file(key: str) -> None:
    """Elimina un objeto de R2."""
    client = get_r2_client()
    client.delete_object(Bucket=BUCKET, Key=key)
