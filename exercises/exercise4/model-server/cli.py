"""
Module that contains the command line app.
"""
import os
import sys
import time
import argparse
import json
from google.cloud import storage
import tensorflow as tf

# Generate the inputs arguments parser
parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument("-o", "--opp", default="default")

def main(args=None):
    parse_args, unknown = parser.parse_known_args(args=args)
    print("Args:", parse_args)

    if parse_args.opp == "test_bucket_access":
        print("Testing bucket access..")

        # Get GCP project id and bucket from environment variable
        GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
        GCP_BUCKET = os.environ["GCP_BUCKET"]

        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.get_bucket(GCP_BUCKET)
        blobs = bucket.list_blobs(prefix="", delimiter="/")
        for blob in blobs:
            print(blob)

    else:
        print("No opp passed")

if __name__ == "__main__":
    main()