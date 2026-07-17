# Terraform - Deploying the App & Database VMs (Part 2)

## Aim

The aim of this task was to use Terraform to deploy a complete two-tier application consisting of:

- An application EC2 instance.
- A database EC2 instance.
- Separate Security Groups for each instance.
- Custom AMIs for both the application and database.
- User data to automatically start the required services.
- Automatic configuration of the application to communicate with the database using its private IP address.

---

# Project Structure

```text
terraform-app-deployment/
│
├── main.tf
├── variables.tf
├── security-groups.tf
├── outputs.tf
├── app-user-data.sh
└── db-user-data.sh
```

---

# Architecture

```text
                 Internet
                     │
                     │
            ┌────────────────┐
            │    App VM       │
            │ Custom App AMI  │
            └────────────────┘
              │ 22
              │ 80
              │ 3000
              │
              │ MongoDB (27017)
              ▼
            ┌────────────────┐
            │ Database VM     │
            │ Custom DB AMI   │
            └────────────────┘
```

The application communicates with the database using the database instance's private IP address.

---

# Variables

Additional variables were added for the database instance.

```hcl
variable "db_ami_id" {
  description = "Custom database AMI"
  default     = "YOUR_CUSTOM_DB_AMI"
}

variable "db_instance_name" {
  default = "tech610-homaira-tf-db-vm"
}

variable "db_security_group_name" {
  default = "tech610-homaira-tf-db-sg"
}
```

Using variables keeps the Terraform configuration reusable and easier to maintain.

---

# Application Security Group

The application Security Group allows:

| Port | Source | Purpose |
|------|---------|---------|
|22|My Public IP|SSH|
|80|0.0.0.0/0|HTTP|
|3000|0.0.0.0/0|Application|

Terraform automatically retrieves my current public IP using the HTTP provider.

---

# Database Security Group

A second Security Group was created for the database.

Unlike the application Security Group, MongoDB is **not** exposed to the internet.

Instead, only the application Security Group is allowed to connect on port 27017.

Example:

```hcl
resource "aws_security_group" "db_sg" {

  name = var.db_security_group_name

  ingress {

    description = "MongoDB from App VM"

    from_port = 27017
    to_port   = 27017
    protocol  = "tcp"

    security_groups = [
      aws_security_group.app_sg.id
    ]

  }

  ingress {

    description = "SSH"

    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = [
      "${chomp(data.http.my_ip.response_body)}/32"
    ]

  }

  egress {

    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]

  }

}
```

This provides a more secure deployment because the database only accepts traffic from the application.

---

# Deploying the Database VM

Terraform creates a second EC2 instance using the custom database AMI.

```hcl
resource "aws_instance" "db_vm" {

  ami           = var.db_ami_id
  instance_type = var.instance_type

  key_name = var.key_name

  vpc_security_group_ids = [
    aws_security_group.db_sg.id
  ]

  user_data = file("${path.module}/db-user-data.sh")

  tags = {

    Name        = var.db_instance_name
    Environment = var.environment

  }

}
```

---

# Database User Data

Since the custom AMI already contained MongoDB, the user data only ensures the service starts when the instance boots.

```bash
#!/bin/bash

sudo systemctl enable mongod
sudo systemctl start mongod
```

---

# Updating the Application VM

The application now needs the database private IP address.

Terraform inserts this automatically using `templatefile()`.

```hcl
user_data = templatefile("${path.module}/app-user-data.sh", {

  db_private_ip = aws_instance.db_vm.private_ip

})
```

Terraform understands that the database must be created before generating the application user data.

---

# Application User Data

The application exports the MongoDB connection string before starting.

```bash
#!/bin/bash

export MONGODB_URI=mongodb://${db_private_ip}:27017/tictactoe

cd /tech610-tic-tac-toe/app

pm2 delete all || true

pm2 start index.js

pm2 save

sudo nginx -t

sudo systemctl restart nginx
```

---

# Outputs

Terraform outputs useful deployment information.

```hcl
output "app_public_ip" {

  value = aws_instance.app_vm.public_ip

}

output "db_private_ip" {

  value = aws_instance.db_vm.private_ip

}

output "app_url" {

  value = "http://${aws_instance.app_vm.public_ip}"

}
```

---

# Deployment Workflow

Format the Terraform files.

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

Deploy the infrastructure.

```bash
terraform apply
```

Display the outputs.

```bash
terraform output
```

---

# Testing

After deployment the following checks were completed:

- Verified both EC2 instances were running.
- Confirmed the correct Security Groups were attached.
- Confirmed the application Security Group allowed ports 22, 80 and 3000.
- Confirmed the database Security Group only allowed MongoDB traffic from the application Security Group.
- SSH'd into both instances.
- Verified MongoDB was running.
- Verified PM2 was running the application.
- Accessed the application successfully through the public IP.

---

# Cleaning Up

Once testing was complete the infrastructure was removed using:

```bash
terraform destroy
```

---

# What I Learnt

- Terraform can deploy multiple EC2 instances within the same configuration.
- Separate Security Groups improve security by restricting access between application tiers.
- Security Groups can reference other Security Groups instead of public IP ranges.
- `templatefile()` allows Terraform to insert values such as private IP addresses into user data scripts.
- User data can automatically start services during instance launch.
- Outputs provide useful deployment information such as public and private IP addresses.
- Using custom AMIs significantly speeds up deployments because the software is already installed.
- Terraform automatically creates resources in the correct order by understanding dependencies between resources.

---

# Files Used

- `main.tf`
- `variables.tf`
- `security-groups.tf`
- `outputs.tf`
- `app-user-data.sh`
- `db-user-data.sh`

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

