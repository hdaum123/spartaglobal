# AWS Custom VPC -- 2-Tier Deployment Documentation

## Aim

The aim of this task was to deploy the Tic Tac Toe application using a
secure two-tier architecture inside a custom AWS VPC. The application
was deployed in a public subnet, while the MongoDB database was placed
in a private subnet to improve security.

------------------------------------------------------------------------

# What is a VPC?

A **Virtual Private Cloud (VPC)** is your own private network inside AWS
where your cloud resources are launched and managed.

AWS provides a **Default VPC** in every region, but for this task a
**Custom VPC** was created so the network, subnets and security could be
configured manually.

## Default VPC vs Custom VPC

``` text
AWS
└── My AWS Account
    ├── Default VPC
    │   ├── Subnet (AZ A)
    │   ├── Subnet (AZ B)
    │   └── Subnet (AZ C)
    │
    └── Custom VPC
        ├── Public Subnet (10.0.2.0/24)
        └── Private Subnet (10.0.3.0/24)
```

Availability Zones (AZs) are separate AWS data centres within the same
region.

------------------------------------------------------------------------

# Architecture

``` text
Internet
    │
Internet Gateway
    │
Public Route Table
    │
Public Subnet
    │
App VM
    │
Private IP
    │
Private Subnet
    │
MongoDB VM
```

Users access the application through the App VM, which communicates with
the database using its private network.

------------------------------------------------------------------------

# Why use a Custom VPC?

A custom VPC gives you control over:

-   Network configuration
-   Public and private subnets
-   Security
-   Internet access
-   Future scalability

------------------------------------------------------------------------

# Public vs Private Subnets

  Public Subnet                  Private Subnet
  ------------------------------ ---------------------------
  Accessible from the internet   No direct internet access
  Hosts the App VM               Hosts the DB VM
  Public IP enabled              Private IP only

Keeping the database in a private subnet helps prevent direct access
from the internet.

------------------------------------------------------------------------

# Step 1 -- Create the VPC

Open **VPC** from the AWS Console.

Go to **Your VPCs** → **Create VPC**.

Use:

-   **VPC only**
-   **Name:** `tech610-homaira-2tier-first-vpc`
-   **IPv4 CIDR:** `10.0.0.0/16`

Click **Create VPC**.

------------------------------------------------------------------------

# Step 2 -- Create the Subnets

Go to **Subnets** → **Create subnet** and select your VPC.

### Public Subnet

-   **Name:** `tech610-homaira-public-subnet`
-   **Availability Zone:** `eu-west-1a`
-   **CIDR:** `10.0.2.0/24`

Click **Add new subnet**.

### Private Subnet

-   **Name:** `tech610-homaira-private-subnet`
-   **Availability Zone:** `eu-west-1b`
-   **CIDR:** `10.0.3.0/24`

Click **Create subnet**.

------------------------------------------------------------------------

# Step 3 -- Create the Internet Gateway

Go to **Internet Gateways** → **Create internet gateway**.

Name it:

`tech610-homaira-2tier-first-vpc-ig`

After creating it, select **Attach to VPC**, choose your custom VPC and
attach it.

------------------------------------------------------------------------

# Step 4 -- Create the Public Route Table

Go to **Route Tables** → **Create route table**.

-   **Name:** `tech610-homaira-2tier-first-vpc-public-rt`
-   Select your VPC.

Open **Subnet Associations**, edit the associations and select **only
the public subnet**.

Then open **Routes** → **Edit routes** → **Add route**.

  Destination   Target
  ------------- ------------------
  `0.0.0.0/0`   Internet Gateway

Save the changes.

This allows the public subnet to communicate with the internet.

------------------------------------------------------------------------

# Step 5 -- Launch the Database VM

Launch your MongoDB AMI.

Network Settings:

-   Select your custom VPC.
-   Select the **Private Subnet**.
-   Leave **Auto-assign Public IP** disabled.

Create a new Security Group:

`tech610-homaira-2tier-allow-ssh-mongodb`

     Port Source
  ------- -------------------------------
       22 My IP (or course requirement)
    27017 10.0.2.0/24

Launch the instance.

------------------------------------------------------------------------

# Step 6 -- Launch the App VM

Launch your App AMI.

Network Settings:

-   Select your custom VPC.
-   Select the **Public Subnet**.
-   Enable **Auto-assign Public IP**.

Create a Security Group:

`tech610-homaira-2tier-allow-ssh-my-ip-http`

    Port Source
  ------ -----------
      22 My IP
      80 0.0.0.0/0

## User Data

``` bash
#!/bin/bash

export MONGODB_URI=mongodb://privateapi:27017/tictactoe

cd /tech610-tic-tac-toe/app

pm2 start index.js
```

This starts the application and connects it to the MongoDB database.

Launch the instance.

------------------------------------------------------------------------

# Testing

Once both instances are running:

1.  Copy the App VM public IP.
2.  Open:

``` text
http://<app-public-ip>
```

If everything has been configured correctly, the Tic Tac Toe application
should load successfully.

------------------------------------------------------------------------

# Cleaning Up

To avoid unnecessary AWS charges, delete the resources once testing has
been completed.

## Step 1 -- Terminate the EC2 Instances

Go to **EC2 → Instances**.

-   Terminate the **App VM**.
-   Terminate the **DB VM**.

## Step 2 -- Delete the VPC

Go to **VPC → Your VPCs**.

-   Select **tech610-homaira-2tier-first-vpc**.
-   Click **Actions → Delete VPC**.
-   Type **delete** to confirm.

Deleting the VPC also removes the associated subnets, route tables and
Internet Gateway attachment.
