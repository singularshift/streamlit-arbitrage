from google.cloud import storage
import sys

def list_gcs_files(bucket_name):
    """Lists all files in the specified GCS bucket."""
    client = storage.Client()
    blobs = client.list_blobs(bucket_name)

    for blob in blobs:
        print(blob.name)

def main():
    if len(sys.argv) != 2:
        print("Usage: list-gcs <BUCKET_NAME>")
        sys.exit(1)

    bucket_name = sys.argv[1]
    list_gcs_files(bucket_name)

if __name__ == "__main__":
    main()
