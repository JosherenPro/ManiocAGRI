import os
import uuid
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
bucket_name = "produits_images"

if not url or not key:
    print("Missing Supabase credentials in .env")
    exit(1)

client = create_client(url, key)

print(f"Testing upload to bucket: {bucket_name}")

# Create a dummy text file to upload as a test
test_file_content = b"This is a test image for ManiocAgri Supabase integration"
test_filename = f"test_upload_{uuid.uuid4().hex[:8]}.txt"
path = f"products/{test_filename}"

try:
    print(f"Uploading file: {path}...")
    res = client.storage.from_(bucket_name).upload(
        path=path,
        file=test_file_content,
        file_options={"content-type": "text/plain"}
    )
    print(f"Upload response: {res}")
    
    # Get public URL
    public_url = client.storage.from_(bucket_name).get_public_url(path)
    print(f"SUCCESS! Public URL: {public_url}")
    
    # Verify download URL works (optional, requires requests/httpx to actually fetch)
    print("\nTo verify, you can open this URL in your browser.")
    print("If it downloads the test file, the bucket is working correctly.")
    
except Exception as e:
    print(f"\nFAILED to upload to bucket '{bucket_name}':")
    print(str(e))
    print("\nPossible reasons:")
    print("1. The bucket does not exist.")
    print("2. The Row Level Security (RLS) policies block the upload.")
    print("3. The service key is invalid.")
