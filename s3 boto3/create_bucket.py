import boto3

bucket_name = "tech610-homaira-test-boto3-2026"
region = "eu-west-1"

s3 = boto3.client("s3", region_name=region)

s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={"LocationConstraint": region}
)

print("Bucket created")
