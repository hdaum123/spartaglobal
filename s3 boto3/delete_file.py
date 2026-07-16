import boto3

bucket_name = "tech610-homaira-test-boto3-2026"
file_name = "test.txt"

s3 = boto3.client("s3")
s3.delete_object(Bucket=bucket_name, Key=file_name)

print("File deleted")
