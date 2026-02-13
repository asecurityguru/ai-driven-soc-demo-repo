# AI-Powered SOC Demo with Splunk + MCP

## Overview

This demo showcases AI-assisted Security Operations Center (SOC) workflows using:
- **Splunk Enterprise** (Docker) - SIEM platform with sample security data
- **MCP Server** - Bridge between Claude and Splunk
- **Claude Desktop/Cline** - AI assistant for SOC analysts

---

## Architecture

```
Claude Desktop (with MCP) 
    ↓
MCP Server (Python)
    ↓
Splunk Docker Container
    ↓
Security Events Sample Security Data
```

---

## Prerequisites

- Git installed
- Docker Desktop installed and running
- Python 3.10+
- Claude Desktop installed
- 8GB RAM minimum
- 20GB disk space

### 1. Install Docker Desktop for Windows

1. Download from: https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Ensure WSL 2 is enabled (Docker Desktop will prompt you)
4. Start Docker Desktop and wait for it to be running

### 2. Install Python

1. Download Python 3.10 or higher from: https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Verify installation:

```powershell
python --version
```

### 3. Install Git (Optional, for cloning)

Download from: https://git-scm.com/download/win

---

## Phase 1: Splunk Setup with Security Data

### Setup Workflow Overview

```
Step 1: Launch Splunk (Docker)
   ↓
Step 2: Generate sample security data (Python script)
   ↓
Step 3: Import data into Splunk (Web UI or HEC)
   ↓
Step 4: Verify data in Splunk (Search queries)
   ↓
Step 5: Setup Python environment (MCP server)
   ↓
Step 6: Configure Claude Desktop (MCP config)
   ↓
Step 7: Work as a SOC Engineer
```

---

## Step-by-Step Setup

### Step 1: Create Project Directory (Powershell commands on Windows)

```powershell
# Create directory
mkdir C:\splunk-mcp-soc-demo
cd C:\splunk-mcp-soc-demo

git clone https://github.com/asecurityguru/ai-driven-soc-demo-repo.git
cd ai-driven-soc-demo-repo

copy generate_sample_data.py,requirements.txt,splunk_mcp_server.py ..\ #Copying files from git repo to splunk-mcp-soc-demo directory

cd .. # Moving out of git repo

# Download all the files from the demo into this directory
# (Use the files provided or download them)
```

---

### Step 2: Launch Splunk Docker Container

**Note:** We're running without a volume mount for simplicity and reliability.

```powershell
# Run Splunk Enterprise
docker run -d `
  -p 8000:8000 `
  -p 8088:8088 `
  -p 8089:8089 `
  -e "SPLUNK_START_ARGS=--accept-license" `
  -e "SPLUNK_PASSWORD=Admin123!" `
  -e "SPLUNK_GENERAL_TERMS=--accept-sgt-current-at-splunk-com" `
  -e "SPLUNK_HEC_TOKEN=abcd1234-abcd-1234-abcd-1234abcd1234" `
  --name splunk `
  splunk/splunk:latest

# Wait for Splunk to start (takes 2-3 minutes)
Write-Host "Waiting for Splunk to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 180

# Check status
docker logs splunk | Select-String "Ansible playbook complete"
```

---

### Step 3: Verify Splunk Access

1. **Open browser:** http://localhost:8000
2. **Login with:**
   - Username: `admin`
   - Password: `Admin123!`

---

### Step 4: Generate Sample Security Data

Create realistic security events:

```powershell
# Generate sample security events (49 events)
python generate_sample_data.py
```

**What this creates:**
- `sample_security_events.json` with 49 realistic security events
- Attack scenarios: brute force, malware C2, data exfiltration, port scanning, privilege escalation
- Normal traffic baseline for comparison

**Expected output:**
```
✅ Generated 49 security events
📁 Saved to: sample_security_events.json

Event breakdown:
  - Brute Force Attacks: 12 events
  - Data Exfiltration: 1 event
  - Malware C2 Traffic: 5 events
  - Port Scanning: 9 events
  - Privilege Escalation: 1 event
  - Phishing: 1 event
  - Normal Traffic: 20 events
```

---

### Step 5: Import Data into Splunk via Web UI

#### 1. Open Splunk Web UI

```
URL: http://localhost:8000

Login credentials:
  Username: admin
  Password: Admin123!
```

#### 2. Upload the Data

- Click **"Settings"** → **"Add Data"**
- Click **"Upload"**
- Click **"Select File"** and choose `sample_security_events.json`
- Click **"Next"**

#### 3. Configure Source Type (IMPORTANT!)

On the **"Set Source Type"** page:

- **Source Type:** Select **"_json"** from dropdown
- Click **"Advanced"** to expand settings
- **LINE_BREAKER field:**
  - ⚠️ If you see a weird value like `\N+01+`, **DELETE IT**
  - Leave it **blank** or set to: `([\r\n]+)`
- **Event Breaks:** Should be **"Every Line"**
- Click **"Next"** (NOT "Save As")

#### 4. Set Input Settings

- **Index:** Select **"main"**
- Click **"Review"**

#### 5. Submit

- Review settings
- Click **"Submit"**
- You should see: **"File has been uploaded successfully"**

#### 6. Verify Data Import

Click **"Start Searching"** or go to **Search & Reporting**, then run:

**Count events:**
```spl
index=main | stats count
```

**Expected result:** Should show **49** (or more if you uploaded multiple times)

**View sample events:**
```spl
index=main | head 10
```

---

### Step 6: Setup Python Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 7: Test MCP Server

```powershell
# Test the MCP server (press Ctrl+C to stop)
python splunk_mcp_server.py
```

**If you see no errors, the MCP server is working!** Press `Ctrl+C` to stop.

---

## Step 8: Configure Claude Desktop

### 8.1: Install Claude Desktop

**Download:** https://claude.ai/download

---

### 8.2: Determine Your Claude Desktop Installation Type (Powershell commands for Windows)

**Windows - Check which version you have:**

```powershell
# Option 1: Check for Microsoft Store version
Test-Path "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc"

# If returns TRUE = You have Microsoft Store version
# If returns FALSE = You have Direct Download version
```

**Or check manually:**

```powershell
# Search for Claude executable
Get-ChildItem -Path "$env:LOCALAPPDATA" -Recurse -Filter "Claude.exe" -ErrorAction SilentlyContinue | Select-Object FullName

# If path contains "Packages\Claude_pzs8sxrjxfjjc" = Microsoft Store version
# If path contains "Programs\Claude" = Direct Download version
```

**macOS/Linux:**

```bash
# Check config location
ls ~/Library/Application\ Support/Claude/claude_desktop_config.json

# If exists = Standard installation
# If not exists = Check alternate locations
```

---

### 8.3: Configure Based on Your Installation Type (Powershell commands for Windows)

#### 🏪 For Microsoft Store Version (Windows)

# Step 1: Check if the directory exists
Test-Path "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude"

# If it returns FALSE, create the directory first:
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude"

# Verify the directory in explorer
explorer "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude"

# Step 2: Now create the config file
notepad "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json"

# Notepad will ask: "Do you want to create a new file?" - Click YES
```

# Step 3: Add this configuration in the Notepad file (replace path with your actual path):

**If file is EMPTY or NEW:**

```json
{
  "mcpServers": {
    "splunk-soc": {
      "command": "C:\\splunk-mcp-soc-demo\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\splunk-mcp-soc-demo\\splunk_mcp_server.py"
      ],
      "env": {
        "SPLUNK_HOST": "localhost",
        "SPLUNK_PORT": "8089",
        "SPLUNK_USERNAME": "admin",
        "SPLUNK_PASSWORD": "Admin123!"
      }
    }
  }
}
```

**If file ALREADY HAS CONTENT** (e.g., preferences):

```json
{
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "sidebarMode": "chat"
  },
  "mcpServers": {
    "splunk-soc": {
      "command": "C:\\splunk-mcp-soc-demo\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\splunk-mcp-soc-demo\\splunk_mcp_server.py"
      ],
      "env": {
        "SPLUNK_HOST": "localhost",
        "SPLUNK_PORT": "8089",
        "SPLUNK_USERNAME": "admin",
        "SPLUNK_PASSWORD": "Admin123!"
      }
    }
  }
}
```

3. **Save the file**

4. **Restart Claude Desktop:**

```powershell
# Kill all Claude processes
Get-Process | Where-Object {$_.Name -like "*Claude*"} | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 3

# Restart Claude Desktop from Start Menu
```

5. **Verify:** Look for MCP server in developer settings in Claude Desktop


---

#### 💻 For Direct Download Version (Windows)

**Config File Location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Steps:**

1. **Create/Edit config file:**

```powershell
# Open with notepad
notepad "$env:APPDATA\Claude\claude_desktop_config.json"

# Or navigate to folder
explorer "$env:APPDATA\Claude"
```

2. **Add this configuration:**

```json
{
  "mcpServers": {
    "splunk-soc": {
      "command": "C:\\splunk-mcp-soc-demo\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\splunk-mcp-soc-demo\\splunk_mcp_server.py"
      ],
      "env": {
        "SPLUNK_HOST": "localhost",
        "SPLUNK_PORT": "8089",
        "SPLUNK_USERNAME": "admin",
        "SPLUNK_PASSWORD": "Admin123!"
      }
    }
  }
}
```

3. **Save and restart Claude Desktop**

4. **Verify:** 

**Logs Location:**
```powershell
explorer "$env:APPDATA\Claude\logs"
```

---

#### 🍎 For macOS

**Config File Location:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Steps:**

1. **Edit config file:**

```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. **Add this configuration:**

```json
{
  "mcpServers": {
    "splunk-soc": {
      "command": "/full/path/to/splunk-mcp-soc-demo/venv/bin/python",
      "args": [
        "/full/path/to/splunk-mcp-soc-demo/splunk_mcp_server.py"
      ],
      "env": {
        "SPLUNK_HOST": "localhost",
        "SPLUNK_PORT": "8089",
        "SPLUNK_USERNAME": "admin",
        "SPLUNK_PASSWORD": "Admin123!"
      }
    }
  }
}
```

3. **Save** (Ctrl+X, then Y, then Enter)

4. **Restart Claude Desktop**

---

#### 🐧 For Linux

**Config File Location:**
```
~/.config/Claude/claude_desktop_config.json
```

**Steps:**

1. **Edit config file:**

```bash
nano ~/.config/Claude/claude_desktop_config.json
```

2. **Add configuration** (same format as macOS above)

3. **Save and restart**

---

## Step 9: Testing the Integration

Once Claude Desktop is restarted and showing the 🔌 icon, try these prompts:

### 1. Event Search and Triage (Comprehensive Time-Based Searches)
```
Get all critical and high severity alerts from [timeframe] using:
search index=* (severity=critical OR severity=high) | table _time, * | sort -_time

Show me all security events from the last 24 hours with full details using:
search index=* earliest=-24h | table _time, * | sort -_time | head 100
```

### 2. Statistical Aggregation 
```
Get count and breakdown of critical/high severity alerts by category and action:
search index=* (severity=critical OR severity=high) | stats count by severity, category, action | sort -count

Show me alert statistics grouped by severity, category, and whether they were blocked:
search index=* severity=* | stats count by severity, action, category | sort -severity, -count
```

### 3. Indicator-Based Hunting
```
Find all events related to IP 185.220.101.45 across all time:
search index=* (src_ip="185.220.101.45" OR dest_ip="185.220.101.45") | table _time, * | sort -_time

Show me all activity for user bwilson in the last 24 hours:
search index=* user="bwilson" | table _time, * | sort -_time

Find all traffic involving host 192.168.1.40:
search index=* (src_ip="192.168.1.40" OR dest_ip="192.168.1.40") | table _time, * | sort -_time
```

### 4. Brute Force Detection
```
Are there any brute force attacks happening? Show me accounts with multiple failed login attempts.
```

### 5. Correlation Queries
```
Show me all events involving the same destination IP across different sources:
search index=* dest_ip=* | stats count by dest_ip, src_ip, signature | where count > 1 | sort -count

Find users involved in multiple critical incidents:
search index=* severity=critical user=* | stats count by user, category | sort -count.
```

### 6. Security Metrics
```
Give me a security operations summary for the last 24 hours with key metrics.
```

---
