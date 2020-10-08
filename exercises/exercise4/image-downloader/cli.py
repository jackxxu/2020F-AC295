"""
Module that contains the command line app.
"""
import os
import sys
import time
import shutil
import argparse
import json
import tempfile
from google.cloud import storage
from downloader import download_google_images

# Generate the inputs arguments parser
parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument("-o", "--opp", default="default")
parser.add_argument("-b", "--bucket", default="default")
parser.add_argument("-p", "--projectid", default="default")
parser.add_argument("-l", "--labels", default="tomatoes,bell peppers")
parser.add_argument("-n", "--num", type=int, default=10)

def main(args=None):
    parse_args, unknown = parser.parse_known_args(args=args)
    print("Args:", parse_args)

    if parse_args.opp == "test_bucket_access":
        print("Testing bucket access..")

        # GCP Storage bucket
        storage_client = storage.Client(project=parse_args.projectid)
        bucket = storage_client.get_bucket(parse_args.bucket)

        # Test Write access
        test_file = "test-image-downloader.txt"
        with open(test_file, "w") as f:
            f.write("I have access!")

        blob = bucket.blob(test_file)
        print('Uploading file', test_file)
        blob.upload_from_filename(test_file)
        os.remove(test_file)
    elif parse_args.opp == "download_images":
        print("Downloading images from Google")
        labels = parse_args.labels.split(',')
        print("num:",parse_args.num)
        print("labels:",labels)
        download_google_images(search_term_list = labels, num_images_requested = parse_args.num)
    elif parse_args.opp == "upload_to_bucket":
        print("Uploading dataset to GCP Bucket")

        # Zip the dataset folder
        dataset_file = "dataset"
        shutil.make_archive(dataset_file, 'zip', "dataset")
        dataset_file += ".zip"

        # GCP Storage bucket
        storage_client = storage.Client(project=parse_args.projectid)
        bucket = storage_client.get_bucket(parse_args.bucket)

        # Upload to bucket
        blob = bucket.blob(dataset_file)
        print('Uploading file', dataset_file)
        blob.upload_from_filename(dataset_file)

    else:
        print("No --opp passed")

if __name__ == "__main__":
    main()