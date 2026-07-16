import boto3

bucket_name = "tech610-homaira-test-boto3-2026"
file_name = "test.txt"

s3 = boto3.client("s3")
s3.upload_file(file_name, bucket_name, file_name)

print("File uploaded")
