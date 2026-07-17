# Terraform - Deploying the App VM (Part 1)

## Aim

The aim of this task was to use Terraform to deploy the application EC2 instance using my custom AMI.

Terraform was responsible for:

- Creating the application Security Group.
- Creating the EC2 instance.
- Using my existing AWS Key Pair.
- Using my custom App AMI.
- Automatically fetching my public IP address for SSH access.
- Running user data to start the application.
- Outputting the public IP address after deployment.

---

# Project Structure

```text
terraform-app-deployment/
│
├── main.tf
├── variables.tf
├── security-groups.tf
├── outputs.tf
└── app-user-data.sh
```

---

# Provider Configuration

Terraform uses providers to communicate with cloud platforms.

For this deployment the AWS were configured.


provider "aws" {
  region = var.aws_region
}
```

---

# Automatically Fetching My Public IP

Instead of manually updating my IP address whenever it changed, Terraform retrieves it automatically using the HTTP provider.

```hcl
data "http" "my_ip" {
  url = "https://ipv4.icanhazip.com"
}
```

The returned value is later used inside the Security Group to allow SSH access only from my current machine.

---

# Variables

To make the configuration reusable, the EC2 values were stored as variables.

```hcl
variable "aws_region" {
  default = "eu-west-1"
}

variable "app_ami_id" {
  default = "YOUR_CUSTOM_APP_AMI"
}

variable "instance_type" {
  default = "t3.micro"
}

variable "key_name" {
  default = "tech610-homaira-key"
}

variable "app_instance_name" {
  default = "tech610-homaira-tf-app-vm"
}

variable "app_security_group_name" {
  default = "tech610-homaira-tf-app-sg"
}

variable "environment" {
  default = "test"
}
```

Using variables makes the Terraform configuration easier to update without modifying the main infrastructure code.

---

# Creating the Application Security Group

Terraform creates a Security Group that allows:

- SSH (22) from my public IP only.
- HTTP (80) from anywhere.
- Port 3000 from anywhere.

```hcl
resource "aws_security_group" "app_sg" {

  name        = var.app_security_group_name
  description = "Allow SSH, HTTP and App traffic"

  ingress {
    description = "SSH from my current IP"

    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = [
      "${chomp(data.http.my_ip.response_body)}/32"
    ]
  }

  ingress {
    description = "Application"

    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"

    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {

    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]

  }

  tags = {
    Name = var.app_security_group_name
  }

}
```

Using `chomp()` removes the newline character returned by the website before Terraform adds `/32`.

---

# Creating the EC2 Instance

The application EC2 instance uses:

- Custom App AMI
- Existing AWS Key Pair
- Security Group created by Terraform
- User Data script

```hcl
resource "aws_instance" "app_vm" {

  ami           = var.app_ami_id
  instance_type = var.instance_type

  key_name = var.key_name

  vpc_security_group_ids = [
    aws_security_group.app_sg.id
  ]

  user_data = file("${path.module}/app-user-data.sh")

  tags = {

    Name        = var.app_instance_name
    Environment = var.environment

  }

}
```

Terraform automatically creates the Security Group first before creating the EC2 instance because the instance depends on it.

---

# User Data

The EC2 instance uses a user data script to automatically start the application when the instance launches.

Example:

```bash
#!/bin/bash

cd /tech610-tic-tac-toe/app

pm2 delete all || true

pm2 start index.js

pm2 save
```

Since the custom AMI already contains the application and dependencies, the user data only needs to start the application.

---

# Outputs

Terraform outputs useful information after deployment.

```hcl
output "app_public_ip" {
  value = aws_instance.app_vm.public_ip
}

output "app_url" {
  value = "http://${aws_instance.app_vm.public_ip}"
}
```

This makes it easy to SSH into the instance or open the application in a browser.

---

# Deployment Workflow

Format Terraform files.

```bash
terraform fmt
```

Initialise Terraform.

```bash
terraform init
```

Validate the configuration.

```bash
terraform validate
```

Preview the deployment.

```bash
terraform plan
```

Create the infrastructure.

```bash
terraform apply
```

Display the outputs.

```bash
terraform output
```

---

# Testing

After deployment I verified:

- The EC2 instance was running.
- The correct Key Pair was attached.
- The Security Group had the correct inbound rules.
- SSH access worked.
- The application loaded successfully in the browser.

SSH connection:

```bash
ssh -i ~/.ssh/<private-key>.pem ubuntu@<public-ip>
```

Application:

```text
http://<public-ip>
```

or

```text
http://<public-ip>:3000
```

depending on the Nginx configuration.

---

# Cleaning Up

When testing was complete the infrastructure was removed using:

```bash
terraform destroy
```

---

# What I Learnt

- Terraform can automatically retrieve my current public IP using a data source.
- Data sources allow Terraform to read information without creating resources.
- Variables make Terraform configurations easier to reuse.
- Security Groups can reference dynamically retrieved values.
- User data allows EC2 instances to configure themselves during launch.
- Outputs provide useful deployment information such as public IP addresses.
- Terraform automatically creates resources in the correct order by understanding dependencies.
- Using a custom AMI significantly reduces deployment time because the software is already installed.

---

# Files Used

- `main.tf`
- `variables.tf`
- `security-groups.tf`
- `outputs.tf`
- `app-user-data.sh`

---

# Commands Used

```bash
terraform fmt
terraform init
terraform validate
terraform plan
terraform apply
terraform output
terraform destroy
```

---

# GitHub

Replace with your repository links.

- `main.tf`
- `variables.tf`
- `security-groups.tf`
- `outputs.tf`
- `app-user-data.sh`
