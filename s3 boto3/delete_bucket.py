import boto3

bucket_name = "tech610-homaira-test-boto3-2026"

s3 = boto3.client("s3")
s3.delete_bucket(Bucket=bucket_name)

print("Bucket deleted")
