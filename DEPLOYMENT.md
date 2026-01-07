# Production Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Environment Configuration
- [ ] Create `.env` file (copy from `.env.example`)
- [ ] Generate new SECRET_KEY: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Configure `DJANGO_ALLOWED_HOSTS` with your domain(s)
- [ ] Set up database URL (if using PostgreSQL)

### Security
- [ ] Review security settings in `settings.py`
- [ ] Run `python manage.py check --deploy`
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Set up fail2ban or similar
- [ ] Review CORS settings if using API

### Database
- [ ] Backup current SQLite database (if migrating)
- [ ] Set up PostgreSQL (recommended for production)
- [ ] Run all migrations: `python manage.py migrate`
- [ ] Verify all data migrated correctly
- [ ] Set up automated database backups

### Static & Media Files
- [ ] Run `python manage.py collectstatic`
- [ ] Configure cloud storage (AWS S3, CloudFlare R2, etc.) for media files
- [ ] Test image uploads
- [ ] Set up CDN for static files (optional but recommended)

### Application
- [ ] Install production dependencies: `pip install -r requirements.txt`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test all major features
- [ ] Check error pages (404, 500)
- [ ] Verify email settings (if implemented)

### Server Configuration
- [ ] Install and configure Gunicorn
- [ ] Set up Nginx or Apache as reverse proxy
- [ ] Configure SSL/TLS certificates (Let's Encrypt)
- [ ] Set up systemd service for auto-restart
- [ ] Configure logging
- [ ] Set up log rotation

### Monitoring
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure uptime monitoring
- [ ] Set up performance monitoring
- [ ] Configure alerting
- [ ] Set up log aggregation

### Backup Strategy
- [ ] Database backup schedule (daily minimum)
- [ ] Media files backup
- [ ] Configuration files backup
- [ ] Test restore procedure
- [ ] Document backup locations

## Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.13 python3.13-venv python3-pip postgresql nginx -y

# Create application user
sudo useradd -m -s /bin/bash darknetwork
sudo su - darknetwork
```

### 2. Application Setup
```bash
# Clone/upload your code
cd /home/darknetwork
# Upload your code here

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
nano .env  # Edit with your production values
```

### 3. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE darknetwork;
CREATE USER darknetwork WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE darknetwork TO darknetwork;
\q

# Update .env with database URL
# DATABASE_URL=postgresql://darknetwork:password@localhost/darknetwork

# Run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Gunicorn Setup
```bash
# Test Gunicorn
gunicorn project4.wsgi:application --bind 0.0.0.0:8000

# Create systemd service
sudo nano /etc/systemd/system/darknetwork.service
```

Add this content:
```ini
[Unit]
Description=DarkNetwork Django Application
After=network.target

[Service]
User=darknetwork
Group=www-data
WorkingDirectory=/home/darknetwork/darkNetwork
Environment="PATH=/home/darknetwork/darkNetwork/venv/bin"
EnvironmentFile=/home/darknetwork/darkNetwork/.env
ExecStart=/home/darknetwork/darkNetwork/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/darknetwork/darkNetwork/gunicorn.sock \
    project4.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable darknetwork
sudo systemctl start darknetwork
sudo systemctl status darknetwork
```

### 5. Nginx Setup
```bash
sudo nano /etc/nginx/sites-available/darknetwork
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/darknetwork/darkNetwork/staticfiles/;
    }

    location /media/ {
        alias /home/darknetwork/darkNetwork/network/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/darknetwork/darkNetwork/gunicorn.sock;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/darknetwork /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL/HTTPS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Post-Deployment

### Testing
- [ ] Visit your domain in browser
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Test creating posts
- [ ] Test image uploads
- [ ] Test all major features
- [ ] Check mobile responsiveness
- [ ] Test with different browsers

### Performance
- [ ] Run performance tests
- [ ] Check page load times
- [ ] Optimize database queries if needed
- [ ] Configure caching if needed
- [ ] Set up CDN if needed

### Documentation
- [ ] Document deployment process
- [ ] Document server credentials (securely)
- [ ] Document backup procedures
- [ ] Update README with production URL
- [ ] Document any custom configurations

## Ongoing Maintenance

### Daily
- [ ] Check error logs
- [ ] Monitor uptime
- [ ] Check for security alerts

### Weekly
- [ ] Review application logs
- [ ] Check disk space
- [ ] Review performance metrics
- [ ] Check backup success

### Monthly
- [ ] Update dependencies (security patches)
- [ ] Review and optimize database
- [ ] Test backup restoration
- [ ] Review security settings

### Quarterly
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Update Django if new version available
- [ ] Review and update documentation

### Annually
- [ ] Major dependency updates
- [ ] Infrastructure review
- [ ] Disaster recovery test
- [ ] Security penetration testing

## Troubleshooting

### Service won't start
```bash
sudo systemctl status darknetwork
sudo journalctl -u darknetwork -n 50
```

### 502 Bad Gateway
```bash
# Check Gunicorn socket
ls -l /home/darknetwork/darkNetwork/gunicorn.sock
sudo systemctl restart darknetwork
sudo systemctl restart nginx
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart darknetwork
```

### Database connection errors
```bash
# Check PostgreSQL
sudo systemctl status postgresql
# Verify credentials in .env
```

## Emergency Procedures

### Site Down
1. Check systemd service: `sudo systemctl status darknetwork`
2. Check Nginx: `sudo systemctl status nginx`
3. Check logs: `sudo journalctl -u darknetwork -n 100`
4. Restart services if needed

### Database Corruption
1. Stop application: `sudo systemctl stop darknetwork`
2. Restore from latest backup
3. Verify data integrity
4. Restart application

### Security Breach
1. Take site offline immediately
2. Change all passwords and keys
3. Review access logs
4. Restore from known-good backup
5. Patch vulnerability
6. Document incident

## Rollback Procedure

If deployment fails:
```bash
# Stop services
sudo systemctl stop darknetwork

# Restore previous version
cd /home/darknetwork/darkNetwork
git checkout previous-commit  # or restore from backup

# Restore database
python manage.py migrate

# Restart services
sudo systemctl start darknetwork
sudo systemctl restart nginx
```

---

**Remember:** Always test in a staging environment first!
