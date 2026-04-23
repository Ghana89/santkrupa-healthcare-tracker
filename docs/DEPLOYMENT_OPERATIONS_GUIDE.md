# Multi-Tenant System Deployment & Operations Guide
## Production-Ready Checklist

---

## 1. Pre-Deployment Verification

### 1.1 Code Quality Checks

```bash
# Run tests
python manage.py test --settings=santkrupa_hospital.settings

# Check code coverage
coverage run --source='hospital' manage.py test
coverage report

# Lint code
pylint hospital/
flake8 hospital/

# Security checks
python manage.py check --deploy

# Static files
python manage.py collectstatic --noinput --check

# Database migrations
python manage.py makemigrations --check --dry-run
```

### 1.2 Security Audit

```
SECURITY CHECKLIST:
├── [ ] SECRET_KEY is environment variable (not in code)
├── [ ] DEBUG = False in production
├── [ ] ALLOWED_HOSTS properly configured
├── [ ] HTTPS enforced (SECURE_SSL_REDIRECT = True)
├── [ ] CSRF protection enabled
├── [ ] CORS properly configured
├── [ ] SQL injection prevention (use ORM)
├── [ ] XSS protection (template escaping)
├── [ ] CSRF tokens in forms
├── [ ] Passwords hashed (Django default)
├── [ ] Database credentials secured
├── [ ] API keys in environment variables
├── [ ] Rate limiting configured
├── [ ] Audit logging enabled
├── [ ] Data encryption at rest
└── [ ] TLS 1.2+ enforced
```

### 1.3 Performance Baseline

```bash
# Database query count check
python manage.py shell
>>> from django.test.utils import override_settings
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
```

---

## 2. Database Setup (PostgreSQL)

### 2.1 PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev

# macOS
brew install postgresql@15

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### 2.2 Database & User Creation

```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database
CREATE DATABASE santkrupa_hospital;
CREATE USER django_user WITH PASSWORD 'strong_password_here';

-- Grant privileges
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET default_transaction_deferrable TO on;
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE santkrupa_hospital TO django_user;

-- Connect to database and create extensions
\c santkrupa_hospital
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search

-- Verify
\du  # List users
\l   # List databases
```

### 2.3 Django Settings Update

```python
# santkrupa_hospital/settings/production.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'santkrupa_hospital',
        'USER': 'django_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30s query timeout
        }
    }
}
```

### 2.4 Migration Strategy

```bash
# 1. Backup existing SQLite database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# 2. Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# 3. Verify migration
python manage.py migrate --plan

# 4. Run migrations with transaction rollback capability
python manage.py migrate --transaction-safe

# 5. Post-migration checks
python manage.py check
python manage.py test
```

---

## 3. Redis Setup (Caching & Sessions)

### 3.1 Redis Installation

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### 3.2 Django Redis Configuration

```python
# settings/production.py

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # Graceful degradation
        },
        'KEY_PREFIX': 'santkrupa',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Session backend using Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 900  # 15 minutes
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

### 3.3 Cache Invalidation Strategy

```python
# hospital/utils/cache.py

from django.core.cache import cache
from django.views.decorators.cache import cache_page


def invalidate_clinic_cache(clinic_id):
    """Invalidate all cache for a clinic"""
    patterns = [
        f'clinic_{clinic_id}_*',
        f'patients_clinic_{clinic_id}_*',
        f'doctors_clinic_{clinic_id}_*',
    ]
    cache.delete_many(cache.keys(pattern) for pattern in patterns)


def cache_patient_list(clinic_id, duration=3600):
    """Cache patient list"""
    cache_key = f'patients_clinic_{clinic_id}_list'
    return cache.get_or_set(
        cache_key,
        lambda: Patient.objects.filter(clinic_id=clinic_id),
        duration
    )


# Usage in views
@cache_page(60)  # Cache for 60 seconds
def dashboard(request):
    """Cached dashboard view"""
    pass
```

---

## 4. Celery Setup (Async Tasks)

### 4.1 Celery Installation

```bash
pip install celery redis
```

### 4.2 Configuration

```python
# santkrupa_hospital/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'santkrupa_hospital.settings')

app = Celery('santkrupa_hospital')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# settings/production.py
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
```

### 4.3 Async Tasks

```python
# hospital/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_prescription_email(self, prescription_id):
    """Send prescription to patient email"""
    try:
        from hospital.models import Prescription
        
        prescription = Prescription.objects.get(id=prescription_id)
        
        # Generate PDF
        from hospital.utils.pdf import generate_prescription_pdf
        pdf_content = generate_prescription_pdf(prescription)
        
        # Send email
        send_mail(
            subject=f'Prescription for {prescription.patient.patient_name}',
            message='Please find your prescription attached',
            from_email='noreply@santkrupahospital.com',
            recipient_list=[prescription.patient.user.email],
            html_message=render_to_string('emails/prescription.html', {
                'prescription': prescription
            }),
            attachments=[('prescription.pdf', pdf_content, 'application/pdf')]
        )
        
        logger.info(f"Prescription email sent for prescription {prescription_id}")
    
    except Exception as exc:
        logger.error(f"Error sending prescription email: {exc}")
        self.retry(exc=exc, countdown=60)  # Retry after 60 seconds


@shared_task
def generate_daily_reports():
    """Generate daily reports for all clinics"""
    from hospital.models import Clinic
    from hospital.utils.reports import generate_clinic_report
    
    for clinic in Clinic.objects.filter(is_active=True):
        try:
            report = generate_clinic_report(clinic)
            # Send to admin
            send_mail(
                subject=f'Daily Report - {clinic.name}',
                message='Daily report attached',
                from_email='reports@santkrupahospital.com',
                recipient_list=[clinic.admin.email],
                attachments=[('report.pdf', report, 'application/pdf')]
            )
        except Exception as e:
            logger.error(f"Error generating report for {clinic.name}: {e}")


# Periodic tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'generate-daily-reports': {
        'task': 'hospital.tasks.generate_daily_reports',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

---

## 5. Docker & Containerization

### 5.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "santkrupa_hospital.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120"]
```

### 5.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.9'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=santkrupa_hospital
      - DB_USER=django_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn santkrupa_hospital.wsgi:application --bind 0.0.0.0:8000 --workers 4"

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=santkrupa_hospital
      - POSTGRES_USER=django_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A santkrupa_hospital worker -l info
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=santkrupa_hospital
      - DB_USER=django_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A santkrupa_hospital beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=santkrupa_hospital
      - DB_USER=django_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### 5.3 Deploy Docker

```bash
# Build and start
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

---

## 6. Web Server Setup (Nginx)

### 6.1 Nginx Configuration

```nginx
# /etc/nginx/sites-available/santkrupa_hospital

upstream django_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name santkrupahospital.com www.santkrupahospital.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name santkrupahospital.com www.santkrupahospital.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/santkrupahospital.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/santkrupahospital.com/privkey.pem;
    
    # SSL config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Client limits
    client_max_body_size 10M;
    client_body_timeout 30s;
    client_header_timeout 30s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;
    
    # Static files
    location /static/ {
        alias /var/www/santkrupa_hospital/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/santkrupa_hospital/media/;
        expires 7d;
    }
    
    # Django app
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 60s;
    }
}
```

### 6.2 Enable Nginx Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/santkrupa_hospital \
           /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## 7. SSL Certificate Setup

### 7.1 Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d santkrupahospital.com -d www.santkrupahospital.com

# Auto-renewal (already configured, verify)
sudo systemctl status certbot.timer

# Manual renewal
sudo certbot renew --dry-run  # Test
sudo certbot renew           # Actual
```

---

## 8. Monitoring & Logging

### 8.1 Application Logging

```python
# settings/production.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/santkrupa_hospital/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'hospital': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create log directory
import os
log_dir = '/var/log/santkrupa_hospital'
os.makedirs(log_dir, exist_ok=True)
```

### 8.2 Sentry Error Tracking

```python
# settings/production.py

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of requests
    send_default_pii=False,
    environment=os.environ.get('ENVIRONMENT', 'production'),
)
```

### 8.3 System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor disk usage
df -h

# Monitor database
sudo -u postgres psql santkrupa_hospital -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database ORDER BY pg_database_size(datname) DESC;"

# Monitor Redis
redis-cli INFO

# Monitor Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 9. Backup & Disaster Recovery

### 9.1 Database Backups

```bash
# Manual backup
pg_dump santkrupa_hospital > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql santkrupa_hospital < backup.sql

# Automated backup script
#!/bin/bash
# /usr/local/bin/backup_database.sh

BACKUP_DIR="/backups/santkrupa_hospital"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Daily backup
pg_dump santkrupa_hospital | gzip > \
  $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Delete old backups (older than 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Cron job
# Add to crontab: 0 2 * * * /usr/local/bin/backup_database.sh
```

### 9.2 Media Backups

```bash
# Manual backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz /var/www/santkrupa_hospital/media/

# S3 backup
aws s3 sync /var/www/santkrupa_hospital/media/ s3://santkrupa-backups/media/

# Cron job for daily sync
# 0 3 * * * aws s3 sync /var/www/santkrupa_hospital/media/ s3://santkrupa-backups/media/
```

---

## 10. Production Deployment Checklist

```
PRE-DEPLOYMENT:
├── [ ] All tests passing
├── [ ] Code reviewed
├── [ ] Security audit completed
├── [ ] Database migrations prepared
├── [ ] Backup taken
├── [ ] Deployment plan reviewed
└── [ ] Rollback plan documented

DEPLOYMENT:
├── [ ] Docker image built
├── [ ] Environment variables configured
├── [ ] Database migrations run
├── [ ] Static files collected
├── [ ] SSL certificate installed
├── [ ] Nginx configured
├── [ ] Supervisor/systemd services started
├── [ ] Health checks passing
├── [ ] Logging configured
├── [ ] Monitoring enabled
└── [ ] Backup job scheduled

POST-DEPLOYMENT:
├── [ ] Verify all services running
├── [ ] Test critical workflows
├── [ ] Monitor error logs
├── [ ] Load test
├── [ ] Performance baseline
├── [ ] Security scan
├── [ ] Backup verification
└── [ ] Documentation updated
```

---

## 11. Troubleshooting

### Common Issues

```
ISSUE: Connection timeout to database
SOLUTION:
  1. Check if PostgreSQL is running: systemctl status postgresql
  2. Verify credentials in settings
  3. Check firewall: sudo ufw allow 5432

ISSUE: Redis connection failed
SOLUTION:
  1. Restart Redis: redis-cli shutdown && redis-server
  2. Check Redis port: redis-cli ping
  3. Verify REDIS_URL in settings

ISSUE: Static files not found (404)
SOLUTION:
  1. Collect static: python manage.py collectstatic
  2. Check Nginx static path
  3. Verify permissions: chmod -R 755 staticfiles/

ISSUE: High CPU usage
SOLUTION:
  1. Check Django processes: ps aux | grep python
  2. Review slow queries: django-extensions shell_plus --print-sql
  3. Analyze Redis: redis-cli --stat
```

---

## 12. Ongoing Maintenance

### Weekly Tasks
- [ ] Check error logs for issues
- [ ] Monitor database size
- [ ] Verify backups completed successfully
- [ ] Review performance metrics

### Monthly Tasks
- [ ] Database maintenance (VACUUM, ANALYZE)
- [ ] Security updates
- [ ] Dependency updates
- [ ] Performance tuning review

### Quarterly Tasks
- [ ] Security audit
- [ ] Disaster recovery drill
- [ ] Capacity planning
- [ ] Architecture review

---

