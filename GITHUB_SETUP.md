# GitHub Setup Guide

Step-by-step instructions to push this project to GitHub.

## Step 1: Configure Git (First Time Only)

```bash
cd ~/rss-mqtt-project

# Set your GitHub username and email
git config user.name "Your GitHub Username"
git config user.email "your.email@example.com"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `rss-mqtt-publisher`
3. Description: `Automated RSS feed aggregator that publishes to MQTT topics`
4. Choose **Private** (to keep it private)
5. **DO NOT** initialize with README, .gitignore, or license (we already have them)
6. Click **Create repository**

## Step 3: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd ~/rss-mqtt-project

# Add your repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/petermartis/rss-mqtt-project.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### If you have 2FA enabled on GitHub:

You'll need a Personal Access Token instead of password:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "RSS MQTT Publisher"
4. Select scopes: `repo` (all)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When pushing, use the token as your password

## Step 4: Verify Upload

Check your repository at:
```
https://github.com/petermartis/rss-mqtt-project
```

## Future Updates

After making changes:

```bash
cd ~/rss-mqtt-project

# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

## Cloning on Another Raspberry Pi

```bash
# Clone the repository
git clone https://github.com/petermartis/rss-mqtt-project.git
cd rss-mqtt-publisher

# Run installation
chmod +x install.sh
sudo ./install.sh
```

## Quick Backup Commands

### Save current configuration:
```bash
cd ~/rss-mqtt-project
cp ~/.newsboat/urls feeds.txt
cp ~/rss_mqtt_publisher.py .
git add .
git commit -m "Backup: $(date +%Y-%m-%d)"
git push
```

### Restore from GitHub:
```bash
cd ~/rss-mqtt-project
git pull
./install.sh
```

## Troubleshooting

### Authentication failed
- Use Personal Access Token if you have 2FA
- Check username/email are correct
- Verify repository exists and you have access

### Push rejected
```bash
# If remote has changes you don't have
git pull --rebase
git push
```

### Forgot to add files
```bash
git add <filename>
git commit --amend --no-edit
git push --force-with-lease
```
