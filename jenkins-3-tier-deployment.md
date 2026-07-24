# CI/CD Pipeline using Jenkins, GitHub & AWS EC2

> **Project:** Tic Tac Toe CI/CD Pipeline  
> **Repository:** `tech610-homaira-ttt-app-cicd-jenkins`

---

# Project Overview

The aim of this project was to create a fully automated **Continuous Integration and Continuous Deployment (CI/CD)** pipeline for the Sparta Global Tic Tac Toe application using **GitHub**, **Jenkins** and **AWS EC2**.

Before implementing CI/CD, every deployment required manual work. A developer would need to SSH into the production server, pull the latest code, install any dependencies and restart the application manually. This process is slow, repetitive and increases the likelihood of human error.

The objective of this project was to automate this entire process so that every code change follows the same deployment process.

The completed pipeline performs the following tasks automatically:

1. A developer pushes code to the **dev** branch.
2. GitHub immediately sends a webhook notification to Jenkins.
3. Jenkins automatically starts **Job 1**.
4. Job 1 installs dependencies and executes all automated tests.
5. If every test passes, **Job 2** automatically merges the **dev** branch into **main**.
6. Once the merge is complete, **Job 3** automatically deploys the tested application to the production EC2 instance.
7. Jenkins copies the latest application files directly to the server using **SCP**.
8. PM2 restarts the application.
9. The latest version immediately becomes available to users.

The entire deployment now requires no manual intervention after a developer pushes code to GitHub.

---

# Project Architecture

The overall CI/CD pipeline is shown below.

```text
                 Developer

                     │

             git push origin dev

                     │

                     ▼

             GitHub Repository

                     │

              GitHub Webhook

                     │

                     ▼

                Jenkins Server

                     │

        ┌────────────┼─────────────┐

        │            │             │

        ▼            ▼             ▼

     Job 1        Job 2         Job 3

     Testing      Merge        Deploy

        │            │             │

        └────────────┴─────────────┘

                     │

                     ▼

             AWS EC2 Production

                     │

                Node.js App

                     │

                    PM2

                     │

                  End User
```

Each Jenkins job has a single responsibility.

This separation makes troubleshooting significantly easier because each stage performs one specific task.

For example:

- If Job 1 fails, the issue is almost certainly related to the application or automated tests.
- If Job 2 fails, the issue is related to merging branches.
- If Job 3 fails, the problem is isolated to deployment rather than testing.

This modular approach follows good DevOps practices and keeps the pipeline easy to maintain.

---

# Repository Structure

The repository follows the structure below.

```text
tech610-homaira-ttt-app-cicd-jenkins/

│

├── app/

│   ├── public/

│   ├── test/

│   ├── server.js

│   ├── index.js

│   ├── package.json

│   ├── package-lock.json

│   └── ...

│

└── README.md
```

The application itself exists entirely inside the **app** directory.

For this reason Jenkins changes into the app directory before installing dependencies and executing tests.

```bash
cd app

npm ci

npm test
```

Using the correct working directory ensures Jenkins installs the correct dependencies and executes the correct test suite.

---

# Prerequisites

Before beginning the CI/CD pipeline the following components were already available.

- Existing GitHub repository.
- Existing Jenkins server.
- Existing Jenkins worker node.
- Existing Job 1 CI pipeline.
- Running AWS EC2 instance.
- Existing App AMI.
- Node.js installed.
- npm installed.
- PM2 installed.
- Nginx configured.
- GitHub Personal Access Token.
- AWS key pair.

Without these components Jenkins would not be able to build or deploy the application.

---

# Preparing the Production Environment

Before configuring Job 3, the production environment first needed to be prepared.

Rather than launching a completely fresh Ubuntu virtual machine every time a deployment was required, I launched my production instance using the **App AMI** that had been created during previous tasks.

Using the App AMI significantly reduced deployment time because it already contained every runtime dependency required to execute the application.

The AMI already included:

- Ubuntu 22.04
- Node.js 20
- npm
- PM2
- Nginx
- Application folder structure

This meant Jenkins only needed to deploy the updated application rather than configuring an entirely new server.

If a completely new Ubuntu image had been launched instead, Job 3 would first need to install:

- Node.js
- npm
- PM2
- Git
- Application dependencies

before deployment could even begin.

Launching from the App AMI reduced deployment time from several minutes to only a few seconds.

---

# Creating and Using the App AMI

One of the most useful decisions during this project was creating an Application AMI.

An AMI (Amazon Machine Image) is effectively a snapshot of a configured EC2 instance.

Instead of rebuilding the production server from scratch every time, AWS can launch an identical copy using the saved image.

My App AMI already contained:

- Ubuntu 22.04
- Node.js
- PM2
- Nginx
- Working application directory

The deployment therefore became much simpler.

Instead of Jenkins configuring an entire server, Job 3 simply needed to:

1. Connect to the EC2 instance.
2. Copy the updated application files.
3. Install any updated Node packages.
4. Restart PM2.

This dramatically reduced deployment complexity and ensured every deployment used a consistent environment.

This approach closely mirrors how production environments are often managed in industry, where infrastructure is prepared in advance and deployments focus only on delivering the latest application code.

---

# Security Groups

The production EC2 instance required a Security Group that allowed both users and Jenkins to access the server.

Initially, SSH access only allowed connections from my own public IP address.

This worked for connecting manually from my laptop but caused Job 3 to fail because Jenkins was attempting to SSH into the instance from a different machine.

To allow Jenkins to deploy successfully, the SSH rule was temporarily opened during development.

The Security Group therefore allowed:

| Port | Purpose |
|------|----------|
| 22 | SSH |
| 80 | HTTP |
| 3000 | Node.js testing |

Once Jenkins successfully connected, deployments were able to complete automatically.

> **Note**
>
> Allowing SSH from anywhere was only used during development and testing.
> In a production environment, SSH access should instead be restricted to the Jenkins worker or a trusted IP range.

---
# Preparing Jenkins

Before configuring the CI/CD pipeline, Jenkins required several components to be configured so it could communicate securely with both GitHub and the AWS EC2 instance.

Unlike a local development environment, Jenkins cannot automatically access GitHub repositories or SSH into remote servers. Authentication must therefore be configured before any jobs can run successfully.

For this project, Jenkins required two separate credentials:

1. GitHub authentication
2. SSH authentication for the EC2 deployment server

Keeping these credentials separate improves security because each credential has a single responsibility.

---

# Jenkins Credentials

## GitHub Credentials

The first credential created was used to allow Jenkins to communicate with GitHub.

Credential Type:

```
Username with Password
```

The username was my GitHub username and the password field contained my GitHub Personal Access Token (PAT).

This credential is used whenever Jenkins needs to:

- Clone the repository
- Fetch updates
- Push merged code back to GitHub

Without this credential Jenkins would fail during the Git checkout stage because GitHub no longer allows password authentication over HTTPS.

Example repository:

```text
https://github.com/hdaum123/tech610-homaira-ttt-app-cicd-jenkins.git
```

Within each Jenkins job this credential was selected inside the Git Source Code Management section.

---

## SSH Credentials

Job 3 required an additional credential because Jenkins needed to SSH directly into my production EC2 instance.

Unlike GitHub authentication, this uses public key authentication.

Credential Type

```
SSH Username with private key
```

Username

```
ubuntu
```

Private Key

```
homaira-tech610-key.pem
```

Description

```
SSH key for App EC2 deployment
```

This credential allows Jenkins to authenticate with the EC2 instance without requiring a password.

It is only used during deployment.

---

# GitHub Webhook

One of the most important components of the pipeline is the GitHub webhook.

Without a webhook the pipeline would need to be started manually every time code changed.

Instead, GitHub automatically informs Jenkins whenever new commits are pushed.

Webhook URL

```text
http://<jenkins-server>/github-webhook/
```

Content Type

```text
application/json
```

Events

```
Just the push event
```

This means every push immediately generates an HTTP POST request to Jenkins.

The overall process becomes:

```text
Developer

↓

git push origin dev

↓

GitHub

↓

Webhook

↓

Jenkins

↓

Job 1
```

Because the webhook starts Job 1 automatically, developers never need to log into Jenkins simply to start a build.

---

# Creating Job 1

Job Name

```text
homaira-ttt-job1-ci-test
```

This is the Continuous Integration stage of the pipeline.

Its only responsibility is to verify that the application still works.

Job 1 should never merge code.

Job 1 should never deploy code.

Its only responsibility is testing.

Keeping responsibilities separate makes debugging much easier.

---

# Source Code Management

Repository

```text
https://github.com/hdaum123/tech610-homaira-ttt-app-cicd-jenkins.git
```

Credentials

```
homaira-jenkins-2-gh-ttt-app
```

Branch

```text
*/dev
```

Using the dev branch ensures developers can safely make changes without immediately affecting production.

Only after testing has completed successfully should those changes ever reach the main branch.

---

# Build Trigger

Instead of selecting Poll SCM, this project used GitHub Webhooks.

Inside Job 1 the following option was enabled.

```
GitHub hook trigger for GITScm polling
```

This allows GitHub to notify Jenkins immediately whenever code changes.

Using webhooks is significantly more efficient than polling because Jenkins only runs when there is actually new code to test.

---

# Build Environment

No special build environment was required for Job 1.

Unlike Job 3, no SSH authentication is necessary because the job only communicates with GitHub.

---

# Build Step

The build step changes into the application directory before installing dependencies.

```bash
cd app

npm ci

npm test
```

Each command has a specific purpose.

## cd app

Moves Jenkins into the application directory.

The repository contains more than just application files, therefore Jenkins must execute commands inside the correct folder.

---

## npm ci

Installs dependencies using the exact versions stored inside package-lock.json.

Unlike npm install, npm ci removes the existing node_modules folder before installing packages.

This guarantees every Jenkins build starts from a clean state.

This makes builds reproducible.

Using npm install could produce slightly different dependency versions over time.

For automated pipelines this inconsistency should be avoided.

---

## npm test

Executes the complete automated test suite.

Every application route, HTML page and API response is validated.

If even a single assertion fails, Jenkins immediately marks the build as failed.

This behaviour is extremely important because it prevents broken code progressing further through the pipeline.

For example, while testing the deployment pipeline I changed the homepage title.

Although the application still worked correctly, one automated test expected the original HTML structure.

Because the assertion failed, Job 1 correctly stopped the pipeline before any merge or deployment occurred.

This demonstrated that the CI pipeline was working exactly as intended.

---

# Verifying Job 1

A successful build should display:

```
Finished: SUCCESS
```

The Console Output should also show:

- Repository cloned successfully
- npm ci completed successfully
- All automated tests passed

If any test fails the final output becomes:

```
Finished: FAILURE
```

When this occurs:

- Job 2 should not start.
- Job 3 should not start.
- No deployment should occur.

This is one of the biggest advantages of Continuous Integration because production is protected from broken code.

---

# Why Job 1 Exists

At first it seemed unnecessary to have a separate testing job before merging.

However, after working through the pipeline it became clear why separating each responsibility is so important.

If testing, merging and deployment all occurred inside a single Jenkins job, troubleshooting failures would become much more difficult.

By separating the stages:

- Job 1 only tests.
- Job 2 only merges.
- Job 3 only deploys.

Any failure immediately points towards the stage responsible.

This modular approach makes the pipeline significantly easier to maintain and closely reflects how CI/CD pipelines are implemented within industry.

# Creating Job 2 – Automatic Merge

Once Job 1 had been successfully configured and was able to run the automated test suite, the next stage of the pipeline was to automatically merge the tested code into the `main` branch.

The purpose of Job 2 is **not** to test the application again.

It is **not** responsible for deployment either.

Its only responsibility is to take code that has already passed every automated test and merge it into the production branch.

Separating this into its own Jenkins job follows the principle of giving every stage of the pipeline a single responsibility.

The overall pipeline now becomes:

```text
Developer

↓

Push to dev

↓

Job 1

Tests

↓

Job 2

Merge dev → main

↓

Job 3

Deploy
```

By the time Job 2 begins, Jenkins has already confirmed that every automated test passed successfully.

This means the merge process can happen with confidence that the application is in a working state.

---

# Why Use a Development Branch?

One of the biggest changes introduced by CI/CD is separating development from production.

Instead of committing directly to `main`, every change is first pushed to the `dev` branch.

This provides several advantages.

- Developers can work safely without affecting production.
- Every code change is automatically tested.
- Broken code never reaches the production branch.
- Multiple developers can contribute simultaneously without risking the live application.

Only after the tests complete successfully should the code be merged into `main`.

For this project the workflow became:

```text
Developer

↓

git push origin dev

↓

Job 1

↓

Tests Pass

↓

Job 2

↓

Merge into main
```

If the tests fail, the merge never occurs.

---

# Creating Job 2

Job Name

```text
homaira-job2-ci-merge
```

This job was configured as a **Freestyle Project**.

Although Jenkins provides several different project types, a Freestyle Project was sufficient because the merge process only required a Git checkout followed by Git Publisher.

---

# Source Code Management

Repository

```text
https://github.com/hdaum123/tech610-homaira-ttt-app-cicd-jenkins.git
```

Credentials

```text
homaira-jenkins-2-gh-ttt-app
```

Branch

```text
*/dev
```

Even though the purpose of Job 2 is to merge into `main`, Jenkins still checks out the **dev** branch.

This is because the code being merged should always originate from the branch that has just passed testing.

Checking out `main` would defeat the purpose of the pipeline because Jenkins would no longer be deploying the code that was actually tested.

---

# Build Trigger

Unlike Job 1, Job 2 does **not** use a GitHub webhook.

Instead, Job 2 is started automatically by Job 1.

Inside Job 1 the following Post-build Action was configured:

```text
Build other projects

↓

homaira-job2-ci-merge

↓

Trigger only if build is stable
```

This ensures Job 2 will only begin when Job 1 finishes with:

```text
Finished: SUCCESS
```

If Job 1 fails, Job 2 never starts.

This is one of the most important protections within the pipeline because it prevents untested code from reaching the production branch.

---

# Why Use Git Publisher?

Initially I experimented with several different ways of automatically merging the branches.

However, the task specifically required using the **Git Publisher** plugin inside Jenkins.

Git Publisher allows Jenkins to push changes back to GitHub after the build has completed successfully.

For this project it performs the merge from:

```text
dev
```

into

```text
main
```

without requiring any manual Git commands.

This makes the entire merge process completely automatic.

---

# Configuring Git Publisher

Inside **Post-build Actions** the following plugin was selected.

```text
Git Publisher
```

The plugin was configured to push changes back to GitHub after a successful build.

This required Jenkins to authenticate using the previously created GitHub Personal Access Token credential.

Without this credential Git Publisher would not have permission to update the remote repository.

---

# Authentication

The Git Publisher plugin uses the same GitHub credential configured inside Source Code Management.

Credential

```text
homaira-jenkins-2-gh-ttt-app
```

This credential allows Jenkins to:

- Read the repository.
- Push updates.
- Complete the automatic merge.

Using a Personal Access Token is significantly more secure than using passwords and is now the recommended authentication method for GitHub.

---

# Verifying Job 2

Once Job 1 completed successfully, Jenkins automatically started Job 2.

A successful Job 2 build should display:

```text
Finished: SUCCESS
```

The Console Output should also show that:

- The repository was checked out successfully.
- Git Publisher completed successfully.
- The merge from `dev` into `main` completed.
- The updated `main` branch was pushed back to GitHub.

After the build finishes, opening GitHub should show that the latest commit now exists on both the `dev` and `main` branches.

This confirms that the merge has completed successfully.

---

# Triggering Job 3

The final responsibility of Job 2 is starting the deployment stage.

Inside **Post-build Actions** another action was added:

```text
Build other projects
```

Project

```text
homaira-job3-cd-deploy
```

Condition

```text
Trigger only if build is stable
```

This creates the final pipeline:

```text
Developer

↓

GitHub

↓

Webhook

↓

Job 1

↓

Job 2

↓

Job 3
```

No deployment can ever occur unless both previous stages have completed successfully.

---

# Testing Job 2

To verify that Job 2 was working correctly, a small change was made to the **dev** branch.

For example, the homepage was updated with a deployment timestamp.

After committing the change, it was pushed using:

```bash
git checkout dev

git add .

git commit -m "Testing CI/CD pipeline"

git push origin dev
```

Within a few seconds the GitHub webhook automatically triggered Job 1.

Once Job 1 completed successfully, Job 2 automatically started.

Finally, Git Publisher merged the latest changes into the `main` branch without any manual intervention.

This demonstrated that the Continuous Integration stage of the pipeline was working exactly as expected.

---

# Lessons Learned

One of the biggest things I learned while configuring Job 2 was understanding the separation of responsibilities within a CI/CD pipeline.

Initially it was difficult to understand why Jenkins needed three separate jobs instead of one.

After completing the project it became clear that each job performs a single task:

- Job 1 validates the code.
- Job 2 manages the source code.
- Job 3 performs the deployment.

Keeping these responsibilities separate makes the pipeline easier to maintain, easier to debug and significantly safer than combining everything into one large Jenkins job.

# Creating Job 3 – Continuous Deployment

After successfully completing the Continuous Integration stage, the final task was to automate the deployment of the application to a production EC2 instance.

This is the final stage of the pipeline and is responsible for delivering the latest tested version of the application to users.

Unlike Job 1 and Job 2, Job 3 interacts directly with the production server. Because of this, extra care must be taken to ensure only tested code reaches this stage.

The complete deployment flow now becomes:

```text
Developer

↓

Push to dev

↓

GitHub Webhook

↓

Job 1
Run Tests

↓

Job 2
Merge dev → main

↓

Job 3
Deploy to EC2

↓

Users access the updated application
```

At this point in the pipeline:

- The application has already passed all automated tests.
- The latest code has already been merged into the `main` branch.
- Jenkins can safely deploy the tested application to production.

---

# Why We Did Not Use Git Clone

One of the task requirements was **not** to perform a `git clone` on the production server.

Instead, Jenkins copies the code that already exists inside its workspace.

This approach has several advantages:

- Jenkins deploys the exact version it has already tested.
- The production server does not require direct access to GitHub.
- Deployments are faster because only the application files are copied.
- The production environment becomes more secure as Git credentials are not required on the server.

For this reason, the deployment uses **SCP** rather than Git.

---

# Preparing the Production EC2 Instance

Rather than launching a fresh Ubuntu instance, I launched my production server using the **App AMI** that I had created in a previous task.

Using the App AMI saved a significant amount of time because it already contained:

- Ubuntu 22.04 LTS
- Node.js 20
- npm
- PM2
- Nginx
- The application directory (`/tech610-tic-tac-toe/app`)

Because these dependencies were already installed, Job 3 only needed to copy the latest application files and restart the application.

If I had launched a completely new EC2 instance, I would first have needed to install Node.js, npm, PM2, configure Nginx and create the application directory before deployment could begin.

Using an App AMI makes deployments faster and ensures every production server is built from the same known configuration.

---

# Security Group Configuration

The EC2 instance required a Security Group that allowed both users and Jenkins to connect.

The following inbound rules were configured during testing:

| Port | Purpose |
|------|---------|
| 22 | SSH access for Jenkins |
| 80 | HTTP access for users |
| 3000 | Node.js testing |

Initially, the SSH rule only allowed connections from my home IP address.

Although this allowed me to SSH into the instance manually, Jenkins could not connect because the deployment was being performed from the Jenkins worker node rather than my laptop.

To allow Job 3 to work, the SSH rule was temporarily opened during development.

> **Note:** For a production environment, SSH should be restricted to the Jenkins worker or a trusted IP range rather than allowing access from anywhere.

---

# Creating the SSH Credential

Unlike Job 1 and Job 2, which only needed GitHub credentials, Job 3 required a second credential so Jenkins could SSH into the EC2 instance.

The credential was created with the following settings:

**Kind**

```text
SSH Username with private key
```

**Username**

```text
ubuntu
```

**Private Key**

```
homaira-tech610-key.pem
```

This private key was the same key pair used when launching the EC2 instance.

Jenkins uses this key to authenticate with the server securely without requiring a password.

---

# Finding the Private Key

One blocker I encountered was locating my private key.

At first, I believed the `.pem` file had been deleted because it was no longer inside my Downloads folder.

Instead of creating a new EC2 instance, I searched my machine using Git Bash:

```bash
find /c/Users -type f \( -iname "*.pem" -o -iname "*homaira*key*" \)
```

This located the key inside my `.ssh` directory.

After finding it, I copied the contents of the file using 'cat' into Jenkins when creating the SSH Username with Private Key credential.

---

# Build Environment

Inside Job 3, the **SSH Agent** build environment option was enabled.

The credential selected was:

```text
homaira-ec2-deploy-key
```

The SSH Agent plugin loads the private key into memory for the duration of the build.

This means Jenkins can authenticate with the EC2 instance without exposing the private key inside the deployment script.

The console output confirms this by displaying messages similar to:

```text
[ssh-agent] Started
Identity added
Using credentials homaira-ec2-deploy-key
```

Seeing these messages is a good indication that the SSH authentication has been configured correctly.

---

# Deployment Script

The deployment itself is performed inside an **Execute Shell** build step.

```bash
ssh -o StrictHostKeyChecking=no ubuntu@<EC2_PUBLIC_IP> \
"sudo mkdir -p /tech610-tic-tac-toe/app && sudo chown -R ubuntu:ubuntu /tech610-tic-tac-toe"

scp -o StrictHostKeyChecking=no -r app/* \
ubuntu@<EC2_PUBLIC_IP>:/tech610-tic-tac-toe/app/

ssh -o StrictHostKeyChecking=no ubuntu@<EC2_PUBLIC_IP> \
"cd /tech610-tic-tac-toe/app && npm ci && (pm2 restart index || pm2 start index.js) && pm2 save"
```

Each part of this script performs a specific task.

### Step 1 – Prepare the Directory

```bash
sudo mkdir -p /tech610-tic-tac-toe/app
```

Creates the application directory if it does not already exist.

```bash
sudo chown -R ubuntu:ubuntu /tech610-tic-tac-toe
```

Ensures the `ubuntu` user owns the deployment directory.

This became necessary after I encountered a **Permission denied** error because the directory had originally been created by `root`.

Changing the ownership allowed Jenkins to overwrite the application files successfully.

### Step 2 – Copy the Application

```bash
scp -o StrictHostKeyChecking=no -r app/* \
ubuntu@<EC2_PUBLIC_IP>:/tech610-tic-tac-toe/app/
```

Copies the latest tested application directly from the Jenkins workspace to the production server.

Initially, I attempted to use:

```bash
app/.
```

However, this caused an `scp: error: unexpected filename: .` error.

Changing the source to:

```bash
app/*
```

resolved the issue and allowed the deployment to complete successfully.

### Step 3 – Install Dependencies and Restart the Application

```bash
npm ci
```

Installs the exact dependencies defined in `package-lock.json`.

```bash
pm2 restart index || pm2 start index.js
```

Attempts to restart the existing application.

If PM2 has not yet started the application, it automatically starts a new process instead.

```bash
pm2 save
```

Saves the PM2 process list so the application will automatically restart if the EC2 instance reboots.

---

# Verifying Job 3

A successful deployment can be confirmed in several ways.

Inside Jenkins:

- The build status should display **SUCCESS**.
- The console output should show the SSH Agent starting.
- The console output should show the repository being checked out.
- The `scp` command should complete without errors.
- PM2 should restart successfully.

Finally, opening the EC2 Public IP address in a web browser should display the updated version of the application.

To fully test the pipeline, I performed two separate deployments by making visible changes to the application's homepage, committing them to the `dev` branch and confirming that both updates appeared on the live website after the pipeline completed.

This confirmed that the deployment process was repeatable and reliable rather than only working once.

# Testing the Complete CI/CD Pipeline

Once all three Jenkins jobs had been configured, the next stage was to verify that the entire pipeline worked from start to finish without any manual intervention.

The objective of testing was not simply to check whether each job could be run individually, but to confirm that a single push to the `dev` branch would automatically trigger the complete CI/CD workflow.

The expected pipeline was:

```text
Developer

↓

git push origin dev

↓

GitHub Webhook

↓

Job 1
Continuous Integration
(Testing)

↓

Job 2
Automatic Merge
(dev → main)

↓

Job 3
Continuous Deployment

↓

AWS EC2

↓

Updated Application
```

To verify the pipeline, I made a visible change to the homepage of the application.

Initially, I attempted to change the application title:

```html
<h1 class="retro-title">
    Tic Tac Toe CI/CD Test
</h1>
```

Although the application still loaded correctly, the automated tests failed because one of the assertions expected the original page structure.

This demonstrated one of the main advantages of Continuous Integration.

Rather than allowing modified code to be merged automatically, Jenkins immediately stopped the pipeline because one of the tests had failed.

Instead of changing the page title, I added a deployment message elsewhere on the page so the homepage visibly changed without breaking the automated tests.

After committing and pushing the change to the `dev` branch, the following sequence occurred automatically.

## Stage 1 – GitHub Webhook

As soon as the commit reached GitHub, the webhook sent an HTTP POST request to Jenkins.

Unlike polling, no manual action was required.

Jenkins immediately started Job 1.

---

## Stage 2 – Job 1

Job 1 cloned the latest version of the repository from the `dev` branch.

The build then executed:

```bash
cd app

npm ci

npm test
```

The console output confirmed that:

- The repository cloned successfully.
- Dependencies installed correctly.
- Every automated test passed.
- The build finished successfully.

A successful Job 1 should always end with:

```text
Finished: SUCCESS
```

If any automated test fails, the pipeline immediately stops.

No merge occurs.

No deployment occurs.

This prevents broken code reaching production.

---

## Stage 3 – Job 2

After Job 1 completed successfully, Jenkins automatically started Job 2.

Job 2 performed the merge from:

```text
dev
```

into

```text
main
```

using the Git Publisher plugin.

Once the merge completed successfully, the updated `main` branch became visible within GitHub.

Again, the Jenkins console confirmed the build completed with:

```text
Finished: SUCCESS
```

Only after Job 2 completed successfully was Job 3 allowed to begin.

---

## Stage 4 – Job 3

Job 3 automatically deployed the application.

The Jenkins console output confirmed each stage of deployment.

Typical output included:

```text
SSH Agent started

↓

Identity added

↓

Repository checked out

↓

SCP completed successfully

↓

PM2 restarted application

↓

Finished: SUCCESS
```

Seeing this output confirmed that Jenkins had:

- Authenticated successfully using the SSH Agent.
- Connected to the production EC2 instance.
- Copied the latest application files.
- Restarted the application successfully.

Finally, opening the EC2 Public IP address showed the updated homepage.

This confirmed that the deployment had completed successfully.

---

# Testing the Pipeline a Second Time

To ensure the pipeline was reliable rather than working only once, the deployment process was repeated.

A second visible homepage change was made.

The updated application was committed and pushed to the `dev` branch.

Again, the following sequence occurred automatically:

```text
Webhook

↓

Job 1

↓

Job 2

↓

Job 3

↓

Homepage Updated
```

Seeing the second deployment complete successfully demonstrated that the pipeline was reliable and repeatable.

This was important because production deployments must consistently produce the same result every time.

---

# Troubleshooting

Throughout this project I encountered several issues while configuring the pipeline.

Rather than simply recording the solution, I wanted to understand why each problem occurred so that I could recognise similar issues in the future.

---

## Understanding the CI/CD Flow

### Problem

Initially, understanding the relationship between Job 1, Job 2 and Job 3 was confusing.

I found it difficult to understand why three separate Jenkins jobs were required instead of placing every step inside a single job.

### Solution

After working through the project, it became clear that each Jenkins job has one responsibility.

Job 1

- Tests code.

Job 2

- Merges branches.

Job 3

- Deploys code.

Keeping each responsibility separate makes debugging much easier because each stage performs only one task.

---

## Locating the Private Key

### Problem

While configuring Job 3 I could not locate my AWS PEM file.

Without this file Jenkins could not SSH into the EC2 instance.

### Solution

Instead of creating another key pair, I searched my local machine.

```bash
find /c/Users -type f \
\( -iname "*.pem" -o -iname "*homaira*key*" \)
```

This successfully located the private key inside my `.ssh` directory.

The key was then added to Jenkins as an SSH Username with Private Key credential.

---

## Permission Denied During Deployment

### Problem

The first deployment failed with:

```text
Permission denied
```

when SCP attempted to overwrite the application files.

### Cause

The application directory had previously been created by `root`.

Jenkins connected using the `ubuntu` user and therefore did not have permission to modify the existing files.

### Solution

The ownership of the deployment directory was changed.

```bash
sudo chown -R ubuntu:ubuntu /tech610-tic-tac-toe
```

After changing the ownership, SCP successfully copied the application.

---

## SCP Error

### Problem

Initially the deployment used:

```bash
app/.
```

This caused Jenkins to display:

```text
scp: error: unexpected filename: .
```

### Solution

Changing the source to:

```bash
app/*
```

resolved the issue immediately.

---

## Security Group Configuration

### Problem

Initially, SSH access only allowed my own public IP address.

This meant I could connect manually but Jenkins could not.

### Solution

The Security Group was updated so Jenkins could connect to the EC2 instance.

Once Jenkins was able to SSH into the server, Job 3 completed successfully.

---

## Automated Test Failure

### Problem

While testing the pipeline I changed the homepage title.

Although the application worked correctly, one automated test expected the original page structure.

Job 1 therefore failed.

### Solution

Instead of modifying the title, I added the deployment message elsewhere on the page.

The tests passed successfully and the deployment continued.

This demonstrated that the CI stage correctly prevented untested changes reaching production.

---

# Benefits of the Pipeline

Implementing CI/CD provides several advantages.

## Technical Benefits

- Every commit is automatically tested.
- Broken code is prevented from reaching production.
- Jenkins performs deployments consistently.
- The production environment always receives the tested version.
- Deployments become repeatable.
- Human error is significantly reduced.

---

## Business Benefits

From an organisational perspective, CI/CD provides several important advantages.

Developers spend less time performing manual deployments and more time writing code.

Automated testing reduces the likelihood of production failures.

Deployments become faster and more reliable.

Teams gain greater confidence when releasing new features because every deployment follows exactly the same process.

This ultimately improves software quality while reducing operational costs.

---

# Future Improvements

Although the pipeline successfully meets the project requirements, there are several improvements that could be made in the future.

- Restrict SSH access so only the Jenkins worker can connect to the production server.
- Replace SCP with `rsync` to reduce deployment times by transferring only changed files.
- Implement automatic rollback if a deployment fails.
- Containerise the application using Docker.
- Provision the entire infrastructure using Terraform rather than manually creating EC2 instances.
- Introduce staging and production environments to support more advanced deployment strategies.

---

# Conclusion

This project successfully demonstrated the implementation of a complete CI/CD pipeline using **GitHub**, **Jenkins** and **AWS EC2**.

By separating the workflow into three dedicated Jenkins jobs, each stage of the pipeline became easier to understand, maintain and troubleshoot.

Using an **App AMI** significantly simplified the deployment process because all runtime dependencies had already been installed. This allowed Job 3 to focus solely on transferring the latest tested application and restarting the service using PM2.

One of the biggest lessons learned throughout this project was that automation is not simply about reducing manual work—it is about creating a reliable, repeatable deployment process that consistently produces the same outcome.

The final pipeline allows a developer to push code to the `dev` branch and, without any further manual intervention, automatically:

1. Run automated tests.
2. Merge the tested code into `main`.
3. Deploy the latest version to AWS EC2.
4. Restart the application.
5. Make the updated application available to users.

This demonstrates the core principles of Continuous Integration and Continuous Deployment and provides a strong foundation for more advanced DevOps practices in future projects.
