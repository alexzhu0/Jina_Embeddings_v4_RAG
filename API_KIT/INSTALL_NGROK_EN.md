# 🌐 ngrok Installation & Configuration Guide

## 📋 Overview

Due to GitHub's file size limitations (25MB), the `ngrok.exe` file cannot be directly included in the repository. Please follow these steps to manually download and configure ngrok.

## 📥 Download ngrok

### Method 1: Official Download (Recommended)
1. Visit [ngrok official website](https://ngrok.com/download)
2. Select Windows version for download
3. After extraction, place `ngrok.exe` file in `API_KIT/ngrok-v3-stable-windows-amd64/` directory

### Method 2: Direct Download Link
```bash
# Download Windows version
curl -o ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip

# Extract to specified directory
unzip ngrok.zip -d API_KIT/ngrok-v3-stable-windows-amd64/
```

## 🔧 Configure ngrok

### 1. Register ngrok Account
1. Visit [ngrok official website](https://ngrok.com/)
2. Register a free account
3. Get your authtoken

### 2. Configure authtoken
```bash
# Enter ngrok directory
cd API_KIT/ngrok-v3-stable-windows-amd64

# Configure authtoken (replace with your actual token)
ngrok.exe authtoken YOUR_AUTHTOKEN_HERE
```

### 3. Test ngrok
```bash
# Test if ngrok works properly
ngrok.exe http 8000
```

## 🚀 Usage

After configuration is complete, you can:

### Auto Start (Recommended)
```bash
# Use one-click startup script
start_all.bat
```

### Manual Start
```bash
# Start ngrok separately
start_ngrok.bat

# Or use direct command
cd API_KIT/ngrok-v3-stable-windows-amd64
ngrok.exe http 8000
```

## 📁 Directory Structure

After configuration, the directory structure should look like:
```
API_KIT/
└── ngrok-v3-stable-windows-amd64/
    ├── ngrok.exe          # Your downloaded ngrok executable
    └── .ngrok2/           # ngrok configuration directory (auto-generated)
        └── ngrok.yml      # ngrok configuration file
```

## 🔒 Security Notes

- **authtoken Protection**: Please keep your authtoken secure, don't expose it in public code
- **Free Limitations**: ngrok free version has connection and bandwidth limitations
- **HTTPS Support**: ngrok provides free HTTPS tunnels

## 🆘 Troubleshooting

### Common Issues

1. **ngrok.exe doesn't exist**
   - Confirm ngrok.exe is downloaded to correct directory
   - Check file permissions are correct

2. **authtoken not configured**
   - Run `ngrok.exe authtoken YOUR_TOKEN` to configure
   - Check if `~/.ngrok2/ngrok.yml` file exists

3. **Port conflicts**
   - Confirm API service is running on port 8000
   - Can modify to other port: `ngrok.exe http other_port`

4. **Network connection issues**
   - Check firewall settings
   - Confirm network connection is normal

### Get Help

If you encounter issues, please:
1. Check ngrok official documentation
2. Check detailed instructions in API_KIT/README.md
3. Submit Issues in the project

---

**Note**: This is a one-time configuration. After completion, you can use all API_KIT features normally. 