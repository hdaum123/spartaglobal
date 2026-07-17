# Terraform - EC2 Instance with Security Group

## Aim

The aim of this task was to use Terraform to provision an EC2 instance and configure a Security Group.

The Security Group was configured to:

- Allow SSH (22) from my public IP only.
- Allow HTTP (80) from anywhere.
- Allow port 3000 from anywhere.

The EC2 instance was also updated to use an existing AWS Key Pair and the newly created Security Group.

---

# Project Structure

```text
create-ec2-with-variable/
│
├── main.tf
├── security_group.tf
├── variables.tf
├── terraform.tfstate
├── .terraform.lock.hcl
└── .terraform/
```

---

# Provider Configuration

Terraform needs a provider to communicate with AWS.

```hcl
provider "aws" {
  region = "eu-west-1"
}
```

---

# Variables

Rather than hardcoding the AMI ID, a variable was used.

```hcl
variable "test_vm_ami_id" {
  default = "ami-0c1c30571d2dae5c9"
}
```

Using variables makes the configuration easier to maintain and reuse.

---

# Creating the Security Group

The Security Group was created in a separate file (`security_group.tf`).

```hcl
resource "aws_security_group" "allow_ports" {
  name        = "tech610-homaira-tf-allow-port-22-3000-80"
  description = "Allow SSH from my IP and ports 3000 and 80 from all"

  ingress {
    description = "Allow SSH from my IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["YOUR_PUBLIC_IP/32"]
  }

  ingress {
    description = "Allow port 3000 from all"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTP from all"
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
    Name = "tech610-homaira-tf-allow-port-22-3000-80"
  }
}
```

---

# Creating the EC2 Instance

The existing EC2 instance was updated to attach:

- the existing AWS Key Pair
- the Security Group created by Terraform

```hcl
resource "aws_instance" "test_vm" {
  ami           = var.test_vm_ami_id
  instance_type = "t3.micro"

  key_name = "tech610-homaira-key"

  vpc_security_group_ids = [
    aws_security_group.allow_ports.id
  ]

  tags = {
    Name        = "tech610-homaira-tf-first-vm"
    Environment = "test"
  }
}
```

---

# Terraform Workflow

Before deploying, the Terraform configuration was formatted.

```bash
terraform fmt
```

The configuration was then validated.

```bash
terraform validate
```

A deployment plan was generated.

```bash
terraform plan
```

Finally, the infrastructure was created.

```bash
terraform apply
```

After confirmation (`yes`), Terraform provisioned:

- EC2 Instance
- Security Group

and automatically attached the Security Group to the EC2 instance.

---

# Testing

The deployment was verified by:

- Checking the EC2 instance was running.
- Confirming the correct Key Pair was attached.
- Confirming the Security Group was attached.
- Verifying the inbound rules:
  - SSH (22) from my public IP only.
  - HTTP (80) from anywhere.
  - Port 3000 from anywhere.

SSH connectivity was also tested using the attached key pair.

---

# Cleaning Up

Once testing was complete, all Terraform-managed resources were removed using:

```bash
terraform destroy
```

---

# What I Learnt

- Terraform reads every `.tf` file in the same directory as one configuration.
- A provider allows Terraform to communicate with cloud providers such as AWS.
- Security Groups act as virtual firewalls.
- Terraform automatically understands dependencies between resources.
- The EC2 instance can reference a Security Group using:

```hcl
aws_security_group.allow_ports.id
```

which ensures the Security Group is created before the EC2 instance.

- The `key_name` must match an existing AWS EC2 Key Pair.
- `terraform fmt` formats Terraform code.
- `terraform validate` checks the configuration for errors.
- `terraform plan` previews infrastructure changes.
- `terraform apply` creates or updates infrastructure.
- `terraform destroy` removes Terraform-managed resources.
- The Terraform state file records the infrastructure Terraform manages so it knows what already exists.

---

# Commands Used

```bash
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```

---

# GitHub Files

Replace these with your own links.

- `main.tf`
- `security_group.tf`
- `variables.tf`
