# AWS S3 Management Using AWS CLI and Python Boto3

## Aim

The aim of this task was to use an Ubuntu EC2 instance to create and manage Amazon S3 resources using both the AWS CLI and Python Boto3.

## Install AWS CLI dependencies

Update and upgrade the EC2 instance:

```bash
sudo apt update
sudo apt upgrade -y
```

Install `unzip`:

```bash
sudo apt install unzip -y
```

Download and install AWS CLI version 2:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Check the installation:

```bash
aws --version
```

## Authenticate using AWS CLI

Run:

```bash
aws configure
```

Enter:

```text
AWS Access Key ID: value from the provided CSV file
AWS Secret Access Key: value from the provided CSV file
Default region name: eu-west-1
Default output format: json
```

Do not include access keys in the documentation or Python scripts.

Test the authentication:

```bash
aws sts get-caller-identity
aws s3 ls
```

Boto3 uses the credentials saved by `aws configure`, so the keys do not need to be written in the scripts.

## Manipulate S3 using AWS CLI

Create a bucket:

```bash
aws s3 mb s3://tech610-homaira-first-bucket
```

List buckets:

```bash
aws s3 ls
```

Create a test file:

```bash
echo "This is the first line in a test file" > test.txt
```

Upload it:

```bash
aws s3 cp test.txt s3://tech610-homaira-first-bucket
```

List objects:

```bash
aws s3 ls s3://tech610-homaira-first-bucket
```

Download it:

```bash
aws s3 cp s3://tech610-homaira-first-bucket/test.txt downloaded_test.txt
```

Delete it:

```bash
aws s3 rm s3://tech610-homaira-first-bucket/test.txt
```

Delete all objects when needed:

```bash
aws s3 rm s3://tech610-homaira-first-bucket --recursive
```

Delete the empty bucket:

```bash
aws s3 rb s3://tech610-homaira-first-bucket
```

## Set up Python and Boto3

Create and enter the project folder:

```bash
mkdir tech610-homaira-s3-boto3-task
cd tech610-homaira-s3-boto3-task
```

Install virtual-environment support:

```bash
sudo apt install python3-venv -y
```

Create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Boto3:

```bash
pip install boto3
```

Check it:

```bash
python -c "import boto3; print(boto3.__version__)"
```

## Boto3 scripts

The scripts use this bucket name:

```text
tech610-homaira-test-boto3-2026
```

S3 bucket names must be globally unique, so change the name in every script if necessary.

### `list_buckets.py`

Lists all S3 buckets available to the authenticated AWS account.

```bash
python list_buckets.py
```

### `create_bucket.py`

Creates the Boto3 test bucket in `eu-west-1`.

```bash
python create_bucket.py
```

### `upload_file.py`

Uploads `test.txt` from the EC2 instance to the bucket.

```bash
python upload_file.py
```

### `download_file.py`

Downloads `test.txt` and saves it as `downloaded_test.txt`.

```bash
python download_file.py
cat downloaded_test.txt
```

### `delete_file.py`

Deletes `test.txt` from the bucket.

```bash
python delete_file.py
```

### `delete_bucket.py`

Deletes the bucket. The bucket must be empty first.

```bash
python delete_bucket.py
```
