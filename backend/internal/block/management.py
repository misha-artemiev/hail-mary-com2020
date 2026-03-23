"""Block storage management module."""

import asyncio
from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from minio import Minio, S3Error
from PIL import Image

from internal.settings.env import block_settings

PROFILE_IMAGES_BUCKET = "profileimages"
BUNDLE_IMAGES_BUCKET = "bundleimages"
MAX_SIZE = 5 * 1024 * 1024  # 5mb


async def process_image(file: UploadFile) -> bytes:
    """Confirm image and compress.

    Args:
        file: uploaded file

    Returns:
        compressed image

    Raises:
        HTTPException: if not jpeg or larger then 5mb
    """
    if file.content_type != "image/jpeg":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "only jpeg images are accepted"
        )
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="image must be under 5mb")
    image = Image.open(BytesIO(file_bytes))
    output = BytesIO()
    image.save(output, format="JPEG", quality=85, optimize=True)
    return output.getvalue()


class BlockManagement:
    """Block storage management class."""

    client: Minio

    def initialise(self) -> None:
        """Initialise block storage connection."""
        self.client = Minio(
            endpoint=block_settings.url_port,
            access_key=block_settings.access_key,
            secret_key=block_settings.secret_key,
            secure=False,
        )
        if not self.client.bucket_exists(PROFILE_IMAGES_BUCKET):
            self.client.make_bucket(PROFILE_IMAGES_BUCKET)
        if not self.client.bucket_exists(BUNDLE_IMAGES_BUCKET):
            self.client.make_bucket(BUNDLE_IMAGES_BUCKET)

    async def upload_profile_image(self, user_id: int, file: UploadFile) -> None:
        """Change user profile image.

        Args:
            user_id: user id
            file: uploaded file
        """
        image_bytes = await process_image(file)
        await asyncio.to_thread(
            self.client.put_object,
            bucket_name=PROFILE_IMAGES_BUCKET,
            object_name=f"{user_id}.jpeg",
            data=BytesIO(image_bytes),
            length=len(image_bytes),
            content_type="image/jpeg",
        )

    async def upload_bundle_image(self, bundle_id: int, file: UploadFile) -> None:
        """Change bundle image.

        Args:
            bundle_id: bundle id
            file: uploaded file
        """
        image_bytes = await process_image(file)
        await asyncio.to_thread(
            self.client.put_object,
            bucket_name=BUNDLE_IMAGES_BUCKET,
            object_name=f"{bundle_id}.jpeg",
            data=BytesIO(image_bytes),
            length=len(image_bytes),
            content_type="image/jpeg",
        )

    def get_profile_image(self, user_id: int) -> bytes:
        """Get user profile image.

        Args:
            user_id: user id

        Returns:
            image bytes

        Raises:
            HTTPException: if failed to get image
        """
        try:
            image = self.client.get_object(PROFILE_IMAGES_BUCKET, f"{user_id}.jpeg")
            try:
                return image.read()
            finally:
                image.close()
                image.release_conn()
        except S3Error as err:
            if err.code == "NoSuchKey":
                raise HTTPException(status.HTTP_404_NOT_FOUND, "image not found")
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get image"
            )

    def get_bundle_image(self, bundle_id: int) -> bytes:
        """Get bundle image.

        Args:
            bundle_id: bundle id

        Returns:
            image bytes

        Raises:
            HTTPException: if failed to get image
        """
        try:
            image = self.client.get_object(BUNDLE_IMAGES_BUCKET, f"{bundle_id}.jpeg")
            try:
                return image.read()
            finally:
                image.close()
                image.release_conn()
        except S3Error as err:
            if err.code == "NoSuchKey":
                raise HTTPException(status.HTTP_404_NOT_FOUND, "image not found")
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get image"
            )


block_management = BlockManagement()
