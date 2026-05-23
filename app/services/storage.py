"""
Storage service for file upload and management using Cloudinary.
"""
import cloudinary
import cloudinary.uploader
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import StorageError

logger = get_logger(__name__)

# Initialize Cloudinary client
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


class StorageService:
    """Service for managing file storage operations with Cloudinary."""

    @staticmethod
    def upload_file(file_bytes: bytes, filename: str) -> str:
        """
        Upload a file to Cloudinary storage.

        Args:
            file_bytes: File content as bytes
            filename: Original filename

        Returns:
            Secure URL of the uploaded file

        Raises:
            StorageError: If upload fails
        """
        try:
            logger.info(f"Uploading file: {filename}")
            upload_result = cloudinary.uploader.upload(
                file_bytes,
                resource_type="auto",
                public_id=f"knowledge_base/{filename}"
            )
            secure_url = upload_result.get("secure_url")
            logger.info(f"File uploaded successfully: {filename} -> {secure_url}")
            return secure_url
        except Exception as e:
            logger.error(f"Failed to upload file {filename}: {str(e)}", exc_info=True)
            raise StorageError(f"Failed to upload file: {str(e)}")

    @staticmethod
    def delete_file(file_url: str) -> None:
        """
        Delete a file from Cloudinary storage.

        Args:
            file_url: Secure URL of the file to delete

        Note:
            This is a fail-safe operation that logs errors but doesn't raise exceptions.
            Deletion failures are non-critical as they only affect storage cleanup.
        """
        try:
            # Extract public_id from secure URL
            public_id = "knowledge_base/" + file_url.split("/knowledge_base/")[-1].split(".")[0]
            logger.info(f"Deleting file with public_id: {public_id}")
            cloudinary.uploader.destroy(public_id)
            logger.info(f"File deleted successfully: {public_id}")
        except Exception as e:
            # Fail-safe deletion: log but don't raise
            logger.warning(f"Failed to delete file {file_url}: {str(e)}")
