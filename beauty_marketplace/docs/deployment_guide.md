# Beauty Product Marketplace - Deployment Guide

## Overview

This guide provides instructions for deploying the Beauty Product Marketplace application to a production environment. The application is built with Django and requires specific configurations for optimal performance and security.

## Prerequisites

Before deploying, ensure you have:

1. A server with Ubuntu 20.04 or later (recommended)
2. Domain name configured with DNS pointing to your server
3. SSL certificate (Let's Encrypt recommended)
4. PostgreSQL database server
5. Python 3.8 or later
6. Git installed

## Server Setup

### 1. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Software

```bash
# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Redis (for caching)
sudo apt install redis-server -y

# Install system dependencies
sudo apt install build-essential libpq-dev python3-dev -y
```

### 3. Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE beautymarket;
CREATE USER beautymarket_user WITH PASSWORD 'your_secure_password';
ALTER ROLE beautymarket_user SET client_encoding TO 'utf8';
ALTER ROLE beautymarket_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE beautymarket_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE beautymarket TO beautymarket_user;
\q
```

## Application Deployment

### 1. Clone Repository

```bash
# Create project directory
sudo mkdir -p /var/www/beautymarket
sudo chown $USER:$USER /var/www/beautymarket

# Clone your repository (replace with your actual repository URL)
git clone https://github.com/yourusername/beautymarket.git /var/www/beautymarket

# Navigate to project directory
cd /var/www/beautymarket
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database settings
DATABASE_URL=postgresql://beautymarket_user:your_secure_password@localhost/beautymarket

# Django settings
SECRET_KEY=your_very_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email settings (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your_email_password

# Payment gateway settings
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
PAYSTACK_PUBLIC_KEY=your_paystack_public_key
PAYSTACK_SECRET_KEY=your_paystack_secret_key

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. Run Django Setup

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Load initial data (if you have fixtures)
python manage.py loaddata initial_data.json
```

## Web Server Configuration

### 1. Configure Gunicorn

Create a Gunicorn configuration file `gunicorn.conf.py`:

```python
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

Create a systemd service file `/etc/systemd/system/beautymarket.service`:

```ini
[Unit]
Description=BeautyMarket Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/beautymarket
ExecStart=/var/www/beautymarket/venv/bin/gunicorn --config gunicorn.conf.py beauty_marketplace.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=beautymarket

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start beautymarket
sudo systemctl enable beautymarket
```

### 2. Configure Nginx

Create an Nginx configuration file `/etc/nginx/sites-available/beautymarket`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect all HTTP requests to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificate configuration (adjust paths as needed)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Main location block
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/beautymarket/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/beautymarket/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Security: deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/beautymarket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate Setup

Install Certbot for Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Monitoring and Maintenance

### 1. Set Up Log Rotation

Create `/etc/logrotate.d/beautymarket`:

```
/var/log/beautymarket/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload beautymarket
    endscript
}
```

### 2. Set Up Automated Backups

Create a backup script `/home/ubuntu/backup_beautymarket.sh`:

```bash
#!/bin/bash

# Backup script for BeautyMarket
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/home/ubuntu/backups"
DB_NAME="beautymarket"
DB_USER="beautymarket_user"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/beautymarket_db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/beautymarket_media_$DATE.tar.gz /var/www/beautymarket/media/

# Remove backups older than 30 days
find $BACKUP_DIR -name "beautymarket_*" -mtime +30 -delete
```

Make it executable and set up a cron job:

```bash
chmod +x /home/ubuntu/backup_beautymarket.sh

# Add to crontab (runs daily at 2 AM)
crontab -e
# Add this line:
# 0 2 * * * /home/ubuntu/backup_beautymarket.sh
```

## Deployment Verification

After deployment, verify that everything is working:

1. Check that the application is accessible at your domain
2. Verify that static files are loading correctly
3. Test user registration and login
4. Test product listing and search functionality
5. Test shopping cart and checkout process
6. Test community features (chat, posts)
7. Test admin panel functionality
8. Verify that emails are being sent
9. Check that payments are processed correctly
10. Confirm that SSL is working properly

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure all files are owned by the correct user
   ```bash
   sudo chown -R www-data:www-data /var/www/beautymarket
   ```

2. **Database Connection Issues**: Check database credentials in .env file

3. **Static Files Not Loading**: Run collectstatic again
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Nginx Configuration Errors**: Test configuration
   ```bash
   sudo nginx -t
   ```

5. **Gunicorn Service Issues**: Check service status
   ```bash
   sudo systemctl status beautymarket
   ```

### Monitoring Commands

```bash
# Check application logs
sudo journalctl -u beautymarket -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check system resources
htop
df -h
```

## Scaling Considerations

For high-traffic deployments, consider:

1. Using a load balancer with multiple application servers
2. Implementing a CDN for static assets
3. Using Redis for caching and session storage
4. Setting up database replication
5. Implementing database connection pooling
6. Using a message queue for background tasks

## Security Best Practices

1. Keep all software updated regularly
2. Use strong, unique passwords for all accounts
3. Implement proper firewall rules
4. Regularly backup data
5. Monitor logs for suspicious activity
6. Use security headers in Nginx configuration
7. Implement rate limiting for API endpoints
8. Regularly review and update SSL certificates

This deployment guide should help you get your Beauty Product Marketplace running in a production environment. Remember to customize all configuration files with your specific settings and requirements.
