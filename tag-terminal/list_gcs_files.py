from google.cloud import storage
import sys

def list_gcs_files(bucket_name):
    """Lists all the blobs (files) in the specified GCS bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python list_gcs_files.py <BUCKET_NAME>")
        sys.exit(1)

    bucket_name = sys.argv[1]
    list_gcs_files(bucket_name)