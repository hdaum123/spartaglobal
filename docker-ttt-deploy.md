# Docker – Running the Sparta NodeJS Application in a Docker Container

## Overview

The aim of this task was to containerise the Sparta NodeJS application using Docker, build a reusable Docker image, push it to Docker Hub, and ensure that anyone could run the application using a single Docker command.

Unlike the previous Nginx task, this application required Node.js and npm dependencies, so the Dockerfile needed to install the application dependencies before starting the application.

---

# Learning Objectives

By completing this task I learned how to:

- Containerise a NodeJS application.
- Create a Dockerfile for a Node application.
- Build Docker images.
- Install application dependencies inside a Docker image.
- Understand Docker build context.
- Run containers exposing port 3000.
- Push Docker images to Docker Hub.
- Troubleshoot Docker build errors.

---

# Project Structure

The project was organised as follows:

```
docker-run-sparta-app/
│
└── app/
    │
    └── app/
        │
        ├── Dockerfile
        ├── package.json
        ├── package-lock.json
        ├── index.js
        ├── app.js
        ├── server.js
        ├── logger.js
        ├── metrics.js
        ├── public/
        ├── seeds/
        └── test/
```

> **Note:** The Dockerfile was created in the same directory as `package.json` and `package-lock.json`.

---

# Step 1 – Navigate to the Application Folder

Navigate to the folder containing the application files.

```bash
cd ~/docker-run-sparta-app/app/app
```

Verify the contents:

```bash
ls
```

Expected output:

```
app.js
index.js
package.json
package-lock.json
public/
seeds/
server.js
...
```

---

# Step 2 – Create the Dockerfile

Create a file called:

```
Dockerfile
```

The Dockerfile used:

```dockerfile
FROM node:20

WORKDIR /app

COPY package.json package-lock.json ./

COPY seeds ./seeds

RUN npm ci --omit=dev

COPY . .

USER node

EXPOSE 3000

CMD ["node", "index.js"]
```

---

# Dockerfile Explanation

## FROM

```dockerfile
FROM node:20
```

Uses the official Node.js version 20 image from Docker Hub.

This image already contains:

- Node.js
- npm

meaning there is no need to install Node manually.

---

## WORKDIR

```dockerfile
WORKDIR /app
```

Creates the `/app` directory inside the container and sets it as the working directory.

All remaining commands execute from this directory.

---

## COPY package files

```dockerfile
COPY package.json package-lock.json ./
```

Only copies the dependency files.

This allows Docker to cache dependency installation.

If application code changes but dependencies remain the same, Docker does not need to reinstall npm packages.

---

## COPY seeds

```dockerfile
COPY seeds ./seeds
```

This copies the `seeds` folder before running `npm ci`.

This step was required because the application contains a **postinstall** script which automatically executes:

```
node seeds/seed.js
```

Without copying the `seeds` folder first, Docker could not locate the file and the build failed.

---

## Install Dependencies

```dockerfile
RUN npm ci --omit=dev
```

Installs production dependencies.

`npm ci` is preferred over `npm install` because:

- it installs exact dependency versions
- it is faster
- it produces consistent builds

`--omit=dev` excludes development dependencies from the image.

---

## Copy the Application

```dockerfile
COPY . .
```

Copies all remaining application files into the container.

These include:

- index.js
- server.js
- public
- logger.js
- metrics.js

---

## USER

```dockerfile
USER node
```

Runs the application as the built-in `node` user instead of the root user.

This improves container security.

---

## EXPOSE

```dockerfile
EXPOSE 3000
```

Documents that the application listens on port **3000**.

---

## CMD

```dockerfile
CMD ["node","index.js"]
```

Starts the NodeJS application when the container launches.

---

# Step 3 – Build the Docker Image

Build the image.

```bash
docker build -t hdaum123/tech610-tttapp:1.2.0 .
```

### Explanation

| Option | Description |
|---------|-------------|
| docker build | Builds a Docker image |
| -t | Assigns an image name and version |
| hdaum123/tech610-tttapp | Docker Hub repository |
| 1.2.0 | Image version |
| . | Uses the current folder as the build context |

Docker automatically:

- reads the Dockerfile
- downloads the Node image
- installs dependencies
- copies the application
- creates the finished image

---

# Step 4 – Verify the Image

Check the image exists.

```bash
docker images
```

Expected output:

```
REPOSITORY                     TAG
hdaum123/tech610-tttapp        1.2.0
```

---

# Step 5 – Run the Container

Start the application.

```bash
docker run -d -p 3000:3000 --name tech610-tttapp hdaum123/tech610-tttapp:1.2.0
```

### Explanation

- `docker run` creates and starts a container.
- `-d` runs in detached mode.
- `-p 3000:3000` maps host port 3000 to container port 3000.
- `--name tech610-tttapp` assigns the container a friendly name.

---

# Step 6 – Verify the Application

Open:

```
http://localhost:3000
```

The Sparta application should load successfully.

Running containers can also be checked using:

```bash
docker ps
```

---

# Step 7 – Push to Docker Hub

Login:

```bash
docker login
```

Push the image:

```bash
docker push hdaum123/tech610-tttapp:1.2.0
```

Docker uploads each image layer.

Once complete, the image becomes publicly available on Docker Hub.

---

# Final Deliverable

Anyone can run the application using:

```bash
docker run -d -p 3000:3000 hdaum123/tech610-tttapp:1.2.0
```

The application will then be available at:

```
http://localhost:3000
```

---

# Blockers Encountered

## Build Failure During npm ci

During the Docker build, the following error occurred:

```
Error: Cannot find module '/app/seeds/seed.js'
```

### Cause

The application's `package.json` contained a **postinstall** script.

When Docker executed:

```dockerfile
RUN npm ci --omit=dev
```

npm automatically executed:

```bash
node seeds/seed.js
```

However, the `seeds` folder had not yet been copied into the container.

---

## Resolution

The Dockerfile was updated to copy the `seeds` directory before running `npm ci`.

```dockerfile
COPY seeds ./seeds

RUN npm ci --omit=dev
```

After making this change the Docker image built successfully.

---

# Common Docker Commands

## Build

```bash
docker build -t image:tag .
```

Builds a Docker image.

---

## View Images

```bash
docker images
```

Lists local Docker images.

---

## Run

```bash
docker run -d -p 3000:3000 image:tag
```

Runs a container.

---

## Running Containers

```bash
docker ps
```

Shows running containers.

---

## Stop Container

```bash
docker stop container-name
```

Stops a running container.

---

## Remove Container

```bash
docker rm container-name
```

Deletes a stopped container.

---

## Push Image

```bash
docker push username/repository:tag
```

Uploads the image to Docker Hub.

---

## Pull Image

```bash
docker pull username/repository:tag
```

Downloads an image from Docker Hub.

---

# Key Learning Outcomes

Throughout this task I learned:

- How to containerise a NodeJS application.
- How Docker builds images using a Dockerfile.
- Why Docker caches layers to speed up builds.
- Why `package.json` and `package-lock.json` are copied before the rest of the application.
- Why `npm ci` is preferred for production builds.
- Why applications should run as a non-root user.
- How to expose application ports.
- How to publish Docker images to Docker Hub.
- How to troubleshoot Docker build failures caused by application dependencies.
- How to create reusable, portable application images that can run consistently on any machine with Docker installed.
```
