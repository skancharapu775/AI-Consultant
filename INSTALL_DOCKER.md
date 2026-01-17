# How to Install Docker

This guide will help you install Docker Desktop on your operating system.

## macOS Installation

### Option 1: Using Homebrew (Recommended)

If you have Homebrew installed:

```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop
open -a Docker
```

### Option 2: Direct Download

1. **Download Docker Desktop for Mac**
   - Go to: https://www.docker.com/products/docker-desktop
   - Click "Download for Mac"
   - Choose the version for your Mac:
     - **Apple Silicon (M1/M2/M3)**: Download "Mac with Apple Silicon"
     - **Intel Mac**: Download "Mac with Intel chip"

2. **Install Docker Desktop**
   - Open the downloaded `.dmg` file
   - Drag Docker.app to your Applications folder
   - Open Docker from Applications
   - Follow the setup wizard

3. **Verify Installation**
   ```bash
   docker --version
   docker compose version
   ```

## Windows Installation

### Prerequisites
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- OR Windows 11 64-bit
- WSL 2 feature enabled (Docker will help you enable this)

### Steps

1. **Download Docker Desktop for Windows**
   - Go to: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"
   - Download the installer

2. **Run the Installer**
   - Double-click `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - Make sure "Use WSL 2 instead of Hyper-V" is checked (recommended)

3. **Restart Your Computer**
   - Docker will prompt you to restart

4. **Start Docker Desktop**
   - Launch Docker Desktop from Start menu
   - Accept the service agreement
   - Wait for Docker to start (whale icon in system tray)

5. **Verify Installation**
   ```powershell
   docker --version
   docker compose version
   ```

## Linux Installation

### Ubuntu/Debian

```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### Fedora/RHEL/CentOS

```bash
# Install prerequisites
sudo dnf install -y dnf-plugins-core

# Add Docker repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
```

## Verify Installation

After installation, verify Docker is working:

```bash
# Check Docker version
docker --version
# Should show: Docker version 24.x.x or similar

# Check Docker Compose version
docker compose version
# Should show: Docker Compose version v2.x.x or similar

# Test Docker with a simple command
docker run hello-world
# Should download and run a test container
```

## Troubleshooting

### macOS Issues

**"Docker Desktop is not running"**
- Open Docker Desktop from Applications
- Wait for the whale icon to appear in the menu bar
- Make sure it shows "Docker Desktop is running"

**Permission Denied Errors**
- Make sure Docker Desktop is running
- Try restarting Docker Desktop

### Windows Issues

**WSL 2 not installed**
- Docker Desktop installer will guide you
- Or install manually: https://docs.microsoft.com/windows/wsl/install

**"Docker Desktop failed to start"**
- Check Windows features: Enable "Virtual Machine Platform" and "Windows Subsystem for Linux"
- Restart your computer
- Try running Docker Desktop as Administrator

### Linux Issues

**Permission Denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

**Docker daemon not running**
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

## Next Steps

Once Docker is installed:

1. **Verify Docker is running**
   ```bash
   docker ps
   # Should show empty list or running containers (not an error)
   ```

2. **Continue with AI Consultant setup**
   - Follow the instructions in `SETUP.md`
   - Create your `.env` file
   - Run `docker-compose up --build`

## Resources

- **Official Docker Documentation**: https://docs.docker.com/get-docker/
- **Docker Desktop Download**: https://www.docker.com/products/docker-desktop
- **Docker Compose Documentation**: https://docs.docker.com/compose/

## Quick Check Commands

Run these to verify everything is set up correctly:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Check if Docker daemon is running
docker ps

# Check Docker info
docker info
```

All commands should run without errors if Docker is properly installed and running.
