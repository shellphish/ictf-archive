#!/usr/bin/env python3
"""
Upload large challenge files to S3.

Usage:
    python upload_challenge_data.py <challenge-name> <file-or-directory>

Examples:
    python upload_challenge_data.py baby-rev ./binary.elf
    python upload_challenge_data.py where-is-waldo ./data/

Files are publicly accessible at:
    https://ictf-challenge-data.s3.us-west-2.amazonaws.com/<challenge-name>/<filename>

Requires: pip install boto3
"""

import argparse
import os
import sys

import boto3

BUCKET = "ictf-challenge-data"
REGION = "us-west-2"


def upload_file(s3, local_path, s3_key):
    size = os.path.getsize(local_path)
    size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024 * 1024 else f"{size / 1024:.1f} KB"
    print(f"  Uploading {local_path} ({size_str}) -> {s3_key}")
    s3.upload_file(local_path, BUCKET, s3_key)


def main():
    parser = argparse.ArgumentParser(description="Upload challenge data to S3")
    parser.add_argument("challenge", help="Challenge name (used as S3 prefix)")
    parser.add_argument("source", help="File or directory to upload")
    parser.add_argument("--list", action="store_true", help="List existing files for this challenge")
    args = parser.parse_args()

    s3 = boto3.client("s3", region_name=REGION)
    prefix = args.challenge.strip("/")

    if args.list:
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=f"{prefix}/")
        for obj in resp.get("Contents", []):
            size = obj["Size"]
            size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024 * 1024 else f"{size / 1024:.1f} KB"
            url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{obj['Key']}"
            print(f"  {url}  ({size_str})")
        return

    source = args.source
    if not os.path.exists(source):
        print(f"Error: {source} does not exist")
        sys.exit(1)

    uploaded = []

    if os.path.isdir(source):
        print(f"Uploading directory: {source} -> s3://{BUCKET}/{prefix}/")
        for root, _, files in os.walk(source):
            for fname in files:
                local_path = os.path.join(root, fname)
                rel_path = os.path.relpath(local_path, source)
                s3_key = f"{prefix}/{rel_path}"
                upload_file(s3, local_path, s3_key)
                uploaded.append(s3_key)
    else:
        filename = os.path.basename(source)
        s3_key = f"{prefix}/{filename}"
        upload_file(s3, source, s3_key)
        uploaded.append(s3_key)

    print(f"\nDone. Public URL(s):")
    for key in uploaded:
        print(f"  https://{BUCKET}.s3.{REGION}.amazonaws.com/{key}")


if __name__ == "__main__":
    main()
