# Domain Deployment Guide

This guide explains how to deploy the Wallet Scanner with a custom domain.

## Prerequisites

1. **VPS/Server** (Linux recommended - Ubuntu/Debian)
2. **Domain name** pointing to your server's IP
3. **Python 3.8+** installed
4. **Nginx** (for reverse proxy - recommended)
5. **SSL Certificate** (Let's Encrypt recommended for HTTPS)

## Step 1: Server Setup

### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install Certbot (for SSL certificates)
sudo apt install certbot python3-certbot-nginx -y
```

## Step 2: Deploy Application

### Upload Files to Server

```bash
# Create project directory
sudo mkdir -p /var/www/wallet-scanner
sudo chown $USER:$USER /var/www/wallet-scanner

# Upload your project files (use SCP, SFTP, or Git)
cd /var/www/wallet-scanner
# ... upload all project files here ...
```

### Install Python Dependencies

```bash
cd /var/www/wallet-scanner

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment

```bash
# Copy environment template
cp env_template.txt .env

# Edit .env file
nano .env
```

Update these values in `.env`:
```env
DOMAIN=yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
CORS_ORIGINS=https://yourdomain.com
HOST=127.0.0.1
PORT=5000
DEBUG=False
SECRET_KEY=your_random_secret_key_here
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(24))"
```

## Step 3: Configure Nginx

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/wallet-scanner
```

Copy the configuration from `nginx_example.conf` and update:
- Replace `yourdomain.com` with your actual domain
- Update the static file path if needed

### Enable Site

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/wallet-scanner /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Step 4: Setup SSL Certificate (HTTPS)

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure Nginx for HTTPS
# Follow the prompts to complete setup
```

## Step 5: Run Application with Gunicorn

### Create Systemd Service

```bash
sudo nano /etc/systemd/system/wallet-scanner.service
```

Add this content:
```ini
[Unit]
Description=Wallet Scanner Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/wallet-scanner
Environment="PATH=/var/www/wallet-scanner/venv/bin"
ExecStart=/var/www/wallet-scanner/venv/bin/gunicorn --config gunicorn_config.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start wallet-scanner

# Enable on boot
sudo systemctl enable wallet-scanner

# Check status
sudo systemctl status wallet-scanner

# View logs
sudo journalctl -u wallet-scanner -f
```

## Step 6: Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

## Alternative: Run Directly (Development/Testing)

For testing without Gunicorn:

```bash
cd /var/www/wallet-scanner
source venv/bin/activate
python app.py
```

## Windows Deployment

If deploying on Windows:

1. **Use IIS** or **Nginx for Windows** as reverse proxy
2. Run with Gunicorn or directly with Flask
3. Use Windows Task Scheduler to auto-start on boot

### Windows Service (using NSSM)

```bash
# Download NSSM (Non-Sucking Service Manager)
# Install as Windows service:
nssm install WalletScanner "C:\Python\python.exe" "C:\path\to\app.py"
```

## Verification

1. **Check DNS**: Ensure your domain points to server IP
   ```bash
   ping yourdomain.com
   ```

2. **Test HTTP**: Visit `http://yourdomain.com`

3. **Test HTTPS**: Visit `https://yourdomain.com`

4. **Check Logs**:
   ```bash
   # Application logs
   sudo journalctl -u wallet-scanner -f
   
   # Nginx logs
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

## Troubleshooting

### Application Not Starting
- Check Python path in systemd service
- Verify `.env` file exists and is configured
- Check logs: `sudo journalctl -u wallet-scanner -n 50`

### 502 Bad Gateway
- Ensure app is running: `sudo systemctl status wallet-scanner`
- Check Nginx proxy_pass port matches app port
- Verify firewall allows connections

### Domain Not Resolving
- Check DNS records (A record pointing to server IP)
- Wait for DNS propagation (can take up to 48 hours)
- Test with: `nslookup yourdomain.com`

### SSL Certificate Issues
- Ensure domain points to server before requesting certificate
- Check Nginx configuration
- Renew certificate: `sudo certbot renew`

## Security Recommendations

1. **Use HTTPS** (SSL/TLS)
2. **Set strong SECRET_KEY** in `.env`
3. **Restrict ALLOWED_HOSTS** to your domain only
4. **Use firewall** (UFW on Linux)
5. **Keep system updated**: `sudo apt update && sudo apt upgrade`
6. **Regular backups** of database and configuration
7. **Monitor logs** for suspicious activity

## Maintenance

### Update Application
```bash
cd /var/www/wallet-scanner
source venv/bin/activate
git pull  # if using Git
pip install -r requirements.txt
sudo systemctl restart wallet-scanner
```

### Renew SSL Certificate
```bash
# Certbot auto-renews, but you can test:
sudo certbot renew --dry-run
```

### View Application Logs
```bash
sudo journalctl -u wallet-scanner -f
```

## Support

For issues, check:
- Application logs: `sudo journalctl -u wallet-scanner`
- Nginx logs: `/var/log/nginx/error.log`
- System logs: `dmesg | tail`

