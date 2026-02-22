import logging
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
bucket_name = os.getenv("SUPABASE_BUCKET")

print(f"URL: {url}")
print(f"Bucket: {bucket_name}")

if not url or not key:
    print("Missing credentials")
    exit(1)

try:
    client = create_client(url, key)
    buckets = client.storage.list_buckets()
    print("Buckets found:")
    for b in buckets:
        print(f"- {b.name}")
    
    if any(b.name == bucket_name for b in buckets):
        print(f"Bucket '{bucket_name}' exists!")
    else:
        print(f"Bucket '{bucket_name}' NOT FOUND. Available buckets: {[b.name for b in buckets]}")
        # Try to create it?
        # client.storage.create_bucket(bucket_name, options={'public': True})
except Exception as e:
    print(f"Error: {e}")
