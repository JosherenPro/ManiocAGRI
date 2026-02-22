import logging
import uuid
import os
from typing import Optional
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_KEY  # Use service key for server-side uploads
        self.bucket_name = settings.SUPABASE_BUCKET
        self.client: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")

    async def upload_image(self, file_content: bytes, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Uploads an image to Supabase Storage and returns the public URL.
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None

        # Generate a unique path for the image
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        path = f"products/{unique_filename}"

        try:
            # Upload the file
            # Storage3 (used by supabase-py) upload is synchronous in current versions, 
            # but we can wrap it if needed or just use it.
            res = self.client.storage.from_(self.bucket_name).upload(
                path=path,
                file=file_content,
                file_options={"content-type": content_type}
            )
            
            # Get the public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(path)
            return public_url
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}")
            return None

    def delete_image(self, image_url: str):
        """
        Deletes an image from Supabase Storage given its public URL.
        """
        if not self.client or not image_url:
            return

        try:
            # Extract path from URL
            # Example: https://.../storage/v1/object/public/produits-images/products/uuid.jpg
            if self.bucket_name in image_url:
                path = image_url.split(f"{self.bucket_name}/")[-1]
                self.client.storage.from_(self.bucket_name).remove([path])
        except Exception as e:
            logger.error(f"Error deleting from Supabase: {e}")

supabase_storage = SupabaseStorageService()
