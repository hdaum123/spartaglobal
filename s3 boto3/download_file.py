import boto3

bucket_name = "tech610-homaira-test-boto3-2026"
file_name = "test.txt"
download_name = "downloaded_test.txt"

s3 = boto3.client("s3")
s3.download_file(bucket_name, file_name, download_name)

print("File downloaded")
