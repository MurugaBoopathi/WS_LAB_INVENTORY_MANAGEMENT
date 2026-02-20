# 🚀 Lab Inventory Management Tool — Docker Deployment Guide

Complete step-by-step guide to deploy the Lab Inventory Management Tool using Docker on any system.

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Structure](#2-project-structure)
3. [Step 1 — Install Docker](#3-step-1--install-docker)
4. [Step 2 — Copy the Project](#4-step-2--copy-the-project)
5. [Step 3 — Configure the Application](#5-step-3--configure-the-application)
6. [Step 4 — Build the Docker Image](#6-step-4--build-the-docker-image)
7. [Step 5 — Run the Container](#7-step-5--run-the-container)
8. [Step 6 — Verify Deployment](#8-step-6--verify-deployment)
9. [Step 7 — Access the Application](#9-step-7--access-the-application)
10. [Managing the Application](#10-managing-the-application)
11. [Updating the Application](#11-updating-the-application)
12. [Troubleshooting](#12-troubleshooting)
13. [Quick Reference](#13-quick-reference)

---

## 1. Prerequisites

| Requirement          | Details                                      |
|----------------------|----------------------------------------------|
| **Operating System** | Windows 10/11, Windows Server 2019+, or Linux |
| **Docker**           | Docker Desktop (Windows/Mac) or Docker Engine (Linux) |
| **RAM**              | Minimum 2 GB free                            |
| **Disk Space**       | Minimum 1 GB free                            |
| **Network**          | Port 5000 available (or any port of your choice) |

---

## 2. Project Structure

Ensure your project folder has the following files:

```
ws_lab_inventory_management/
├── app/
│   ├── __init__.py
│   ├── data_manager.py
│   ├── email_service.py
│   ├── routes.py
│   ├── data/
│   │   ├── inventory.json
│   │   └── history.json
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── admin.html
│       ├── base.html
│       ├── dashboard.html
│       ├── history.html
│       └── login.html
├── config.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

---

## 3. Step 1 — Install Docker

### Windows (Docker Desktop)

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the prompts.
3. Restart your computer when prompted.
4. Launch **Docker Desktop** from the Start Menu.
5. Wait until the Docker icon in the system tray shows **"Docker Desktop is running"**.

### Linux (Docker Engine)

```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

### Verify Docker Installation

Open a terminal (PowerShell on Windows, Terminal on Linux) and run:

```bash
docker --version
```

Expected output (version may vary):
```
Docker version 28.4.0, build d8eb465
```

---

## 4. Step 2 — Copy the Project

Copy the entire project folder to the target server/system.

**Option A — USB / File Share:**
Copy the `ws_lab_inventory_management` folder to a location on the server, e.g.:
```
C:\Apps\lab-inventory\       (Windows)
/opt/lab-inventory/          (Linux)
```

**Option B — Git (if using version control):**
```bash
git clone <your-repo-url>
cd ws_lab_inventory_management
```

---

## 5. Step 3 — Configure the Application

Open `docker-compose.yml` and update the environment variables as needed:

### Required Changes:

```yaml
environment:
  # Change this to a random secure string in production
  - SECRET_KEY=your-unique-secret-key-here

  # SMTP Configuration (for email notifications)
  - SMTP_SERVER=rb-smtp.2mdc.net
  - SMTP_PORT=25
  - SMTP_USE_TLS=False
  - SMTP_USERNAME=
  - SMTP_PASSWORD=

  # Email Recipients (update with actual email IDs)
  - ADMIN_EMAIL=your-admin@bosch.com
  - MANAGER_EMAIL=your-manager@bosch.com
  - SENDER_EMAIL=lab-inventory-noreply@bosch.com
  - EMAIL_DOMAIN=@bosch.com

  # Admin Login Credentials (change the password!)
  - ADMIN_NT_ID=ADMIN
  - ADMIN_PASSWORD=YourSecurePassword123

  # Port (change if 5000 is already in use)
  - PORT=5000
```

### Change the Port (Optional):

If you want the app on a different port (e.g., 8080), update `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"    # Access via http://server-ip:8080
```

---

## 6. Step 4 — Build the Docker Image

Open a terminal and navigate to the project folder:

```bash
# Windows (PowerShell)
cd "C:\Apps\lab-inventory\ws_lab_inventory_management"

# Linux
cd /opt/lab-inventory/ws_lab_inventory_management
```

### Build Command:

**Standard build (direct internet access):**
```bash
docker build -t lab-inventory .
```

**Corporate proxy build (Bosch network or behind a proxy):**

If your system uses a corporate proxy and Docker cannot access the internet, use:

```bash
docker build --build-arg HTTP_PROXY=http://host.docker.internal:3128 --build-arg HTTPS_PROXY=http://host.docker.internal:3128 -t lab-inventory .
```

> **Note:** Replace `http://host.docker.internal:3128` with your actual proxy address.
> To find your proxy, run: `echo $env:HTTP_PROXY` (PowerShell) or `echo $HTTP_PROXY` (Linux).
> If the proxy is `http://127.0.0.1:PORT`, replace `127.0.0.1` with `host.docker.internal` for Docker.

### Expected Output:

```
[+] Building 16.4s (11/11) FINISHED
 => [1/6] FROM docker.io/library/python:3.11-slim
 => [2/6] WORKDIR /app
 => [3/6] COPY requirements.txt .
 => [4/6] RUN pip install --no-cache-dir -r requirements.txt
 => [5/6] COPY . .
 => [6/6] RUN addgroup --system appgroup && adduser ...
 => exporting to image
 => => naming to docker.io/library/lab-inventory
```

---

## 7. Step 5 — Run the Container

### Option A — Using `docker run` (simple):

```bash
docker run -d \
  --name lab-inventory-app \
  -p 5000:5000 \
  --restart unless-stopped \
  lab-inventory
```

### Option B — Using `docker-compose` (recommended, includes env vars & data persistence):

```bash
docker-compose up -d
```

> **Note:** If you see a warning about `version` being obsolete, you can safely ignore it.

---

## 8. Step 6 — Verify Deployment

### Check the container is running:

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE           COMMAND                  CREATED          STATUS                    PORTS                    NAMES
9bf26e8bece5   lab-inventory   "gunicorn --bind 0.0…"   14 seconds ago   Up 13 seconds (healthy)   0.0.0.0:5000->5000/tcp   lab-inventory-app
```

✅ Look for:
- **STATUS**: `Up ... (healthy)`
- **PORTS**: `0.0.0.0:5000->5000/tcp`

### Check application logs:

```bash
docker logs lab-inventory-app
```

Expected output:
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000 (1)
[INFO] Using worker: sync
[INFO] Booting worker with pid: 7
[INFO] Booting worker with pid: 8
[INFO] Booting worker with pid: 9
```

---

## 9. Step 7 — Access the Application

| From                     | URL                                  |
|--------------------------|--------------------------------------|
| **Same machine**         | http://localhost:5000                |
| **Other users on network** | http://`<server-ip>`:5000          |

To find the server IP:
```bash
# Windows
ipconfig | findstr "IPv4"

# Linux
hostname -I
```

### Login:
- **Admin:** NT ID = `ADMIN`, Password = `Admin@123` (or whatever you set)
- **Users:** Enter their NT ID (no password needed for regular users)

---

## 10. Managing the Application

### Daily Operations

| Action                   | Command                              |
|--------------------------|--------------------------------------|
| **View status**          | `docker ps`                          |
| **View logs**            | `docker logs lab-inventory-app`      |
| **View live logs**       | `docker logs -f lab-inventory-app`   |
| **Stop the app**         | `docker stop lab-inventory-app`      |
| **Start the app**        | `docker start lab-inventory-app`     |
| **Restart the app**      | `docker restart lab-inventory-app`   |
| **Remove the container** | `docker rm -f lab-inventory-app`     |

### Data Persistence

Inventory data (`inventory.json`, `history.json`) is stored in a Docker volume. Data **survives** container restarts and rebuilds.

| Action                           | Command                                          |
|----------------------------------|--------------------------------------------------|
| **List volumes**                 | `docker volume ls`                               |
| **Inspect data volume**          | `docker volume inspect ws_lab_inventory_management_inventory-data` |
| **⚠️ Delete data (irreversible)** | `docker-compose down -v`                        |

### Auto-Restart

The container is set to `restart: unless-stopped`, which means:
- ✅ It **auto-starts** after system reboot
- ✅ It **auto-restarts** if the app crashes
- ❌ It stays stopped **only** if you manually run `docker stop`

---

## 11. Updating the Application

When you make code changes and want to redeploy:

```bash
# Step 1: Navigate to the project folder
cd "C:\Apps\lab-inventory\ws_lab_inventory_management"

# Step 2: Stop and remove the old container
docker rm -f lab-inventory-app

# Step 3: Rebuild the image
docker build -t lab-inventory .
# (Add --build-arg for proxy if on corporate network)

# Step 4: Run the new container
docker run -d --name lab-inventory-app -p 5000:5000 --restart unless-stopped lab-inventory
```

**Or with docker-compose (simpler):**
```bash
docker-compose up -d --build
```

---

## 12. Troubleshooting

### ❌ "Docker Desktop is not running"
```
error during connect: ... open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```
**Fix:** Start Docker Desktop from the Start Menu, wait 30-60 seconds.

### ❌ "Port 5000 is already in use"
```
Bind for 0.0.0.0:5000 failed: port is already allocated
```
**Fix:** Either stop the other process using port 5000, or change the port:
```bash
docker run -d --name lab-inventory-app -p 8080:5000 --restart unless-stopped lab-inventory
```

### ❌ "Could not resolve / pip install fails" (Corporate Proxy)
```
Failed to establish a new connection: Name or service not known
```
**Fix:** Build with proxy arguments:
```bash
docker build --build-arg HTTP_PROXY=http://host.docker.internal:3128 --build-arg HTTPS_PROXY=http://host.docker.internal:3128 -t lab-inventory .
```

### ❌ Container starts but exits immediately
**Fix:** Check the logs:
```bash
docker logs lab-inventory-app
```

### ❌ Cannot access from other machines
**Fix:**
1. Check Windows Firewall — allow port 5000 inbound.
2. Verify the server IP: `ipconfig | findstr "IPv4"`
3. Test locally first: `http://localhost:5000`

---

## 13. Quick Reference

### Complete Deployment in 4 Commands

```bash
# 1. Navigate to project
cd "C:\Apps\lab-inventory\ws_lab_inventory_management"

# 2. Start Docker Desktop (Windows only, skip on Linux)
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 3. Wait for Docker to start, then build
docker build -t lab-inventory .

# 4. Run
docker run -d --name lab-inventory-app -p 5000:5000 --restart unless-stopped lab-inventory
```

### Access
```
http://localhost:5000
```

---

## 📌 Key Files Reference

| File                | Purpose                                              |
|---------------------|------------------------------------------------------|
| `Dockerfile`        | Instructions to build the Docker image               |
| `docker-compose.yml`| Deployment config with env vars & data persistence   |
| `.dockerignore`     | Files excluded from the Docker image                 |
| `requirements.txt`  | Python dependencies (Flask, gunicorn)                |
| `config.py`         | App configuration (reads from environment variables) |
| `run.py`            | Application entry point                              |

---

*Last updated: February 20, 2026*
*Maintainer: mpi2cob@bosch.com*
