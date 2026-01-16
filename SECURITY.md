# 🔒 Xavfsizlik Qo'llanmasi

## ⚠️ KRITIK: API Key va Parollar Xavfsizligi

### Hozirgi Muammo

Loyihangizda quyidagi sensitive ma'lumotlar `.env` faylida ochiq turgan:

1. **OPENAI_API_KEY**: `sk-proj-8Uy3_uew55RXPnWAv00_...`
2. **GEMINI_API_KEY**: `AIzaSyD9zEDbx2b2KSbQe7RtBYwK0EIhxGfU0MU`
3. **EMAIL_HOST_PASSWORD**: `dhssxouvithwltfv`
4. **SECRET_KEY**: Django secret key

### 🚨 ZUDLIK BILAN AMALGA OSHIRING

#### 1. API Keylarni Bekor Qiling

**OpenAI API Key:**
1. https://platform.openai.com/api-keys ga kiring
2. Eski key'ni toping va DELETE qiling
3. Yangi key yarating

**Google Gemini API Key:**
1. https://makersuite.google.com/app/apikey ga kiring
2. Eski key'ni DELETE qiling
3. Yangi key yarating

**Gmail App Password:**
1. https://myaccount.google.com/apppasswords ga kiring
2. Eski parolni o'chiring
3. Yangi app password yarating

#### 2. Yangi Environment Variables

Production uchun **YANGI** `.env.production` yarating:

```bash
cd backend
cp .env.production.example .env.production
nano .env.production  # yoki boshqa editor
```

**MUHIM**:
- Yangi key'larni faqat `.env.production` ga qo'shing
- `.env` faylni GIT'ga HECH QACHON push qilmang!
- Production serverdagi `.env.production` ni xavfsiz saqlang

#### 3. Git Tarixini Tozalash

Agar `.env` fayli git tarixida mavjud bo'lsa:

```bash
# Git tarixdan sensitive fayllarni o'chirish
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (EHTIYOT BILAN!)
git push origin --force --all
```

**YAXSHIROQ VARIANT**: Yangi repository yarating va faqat kodlarni ko'chiring.

## Environment Variables Xavfsizlik Amaliyotlari

### Development vs Production

**Development (.env)**:
- Faqat local development uchun
- Test API key'lar
- Debug mode yoqilgan
- Lokal database

**Production (.env.production)**:
- Real API key'lar
- Debug mode o'chirilgan
- Production database
- Kuchli parollar

### Parol Kuchliligi

```bash
# Kuchli parol yaratish (Linux/Mac)
openssl rand -base64 32

# Django SECRET_KEY yaratish
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# PostgreSQL parol yaratish
openssl rand -base64 24 | tr -d "=+/" | cut -c1-25
```

## Docker Secrets (Tavsiya etiladi)

Production uchun Docker Secrets ishlatish:

```bash
# Secret yaratish
echo "my-secret-password" | docker secret create db_password -

# docker-compose.yml da ishlatish
services:
  db:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

## Git Xavfsizligi

### .gitignore Sozlamalari

Quyidagilar `.gitignore` da bo'lishi SHART:

```gitignore
# Environment variables
.env
.env.local
.env.production
.env.*.local

# API Keys
*.key
*.pem
*.p12

# Credentials
credentials.json
secrets.yaml

# Database
*.sqlite3
*.db

# Logs
*.log
logs/
```

### Pre-commit Hook (Tavsiya)

`.git/hooks/pre-commit` yarating:

```bash
#!/bin/bash

# Check for sensitive files
if git diff --cached --name-only | grep -E "\.env$|\.key$|credentials"; then
    echo "ERROR: Attempting to commit sensitive files!"
    exit 1
fi

# Check for API keys in code
if git diff --cached | grep -E "sk-[a-zA-Z0-9]{48}|AIza[a-zA-Z0-9]{35}"; then
    echo "ERROR: API key detected in commit!"
    exit 1
fi

exit 0
```

```bash
chmod +x .git/hooks/pre-commit
```

## Database Xavfsizligi

### PostgreSQL Sozlamalari

```yaml
# docker-compose.production.yml
db:
  environment:
    - POSTGRES_PASSWORD=${DB_PASSWORD}  # .env dan
  ports:
    - "127.0.0.1:5432:5432"  # Faqat localhost
```

### Backup Encryption

Backup'larni encrypt qilish:

```bash
# Backup yaratish va encrypt qilish
./scripts/backup.sh
gpg --symmetric --cipher-algo AES256 backups/backup_*.sql.gz

# Decrypt qilish
gpg --decrypt backups/backup_*.sql.gz.gpg > backup.sql.gz
```

## Django Xavfsizlik Sozlamalari

### settings_production.py

```python
# Debug o'chirilgan
DEBUG = False

# Xavfsizlik headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# CSRF sozlamalari
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# Allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

## Nginx Xavfsizlik

### SSL/TLS Konfiguratsiyasi

```nginx
# TLS versions
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### Rate Limiting

```nginx
# API rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    # ...
}
```

## API Key Management

### Environment Variables Hierarchy

```
1. Docker Secrets (Eng xavfsiz)
2. External Secrets Manager (AWS Secrets Manager, Vault)
3. .env.production files (Minimal, faqat server'da)
4. Environment variables (Container ichida)
```

### API Key Rotation Strategy

1. **Har 90 kunda** API key'larni yangilang
2. Eski key'ni bekor qiling
3. Yangi key'ni `.env.production` ga qo'shing
4. Container'larni restart qiling

```bash
# Update API key
nano backend/.env.production  # Yangi key qo'shing

# Restart backend
docker-compose -f docker-compose.production.yml restart backend
```

## Monitoring va Alerting

### Failed Login Attempts

Django settings'da:

```python
# settings_production.py
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour
```

### Log Monitoring

Suspicious activity'larni monitor qiling:

```bash
# Failed login attempts
docker-compose logs backend | grep "Authentication failed"

# Unusual API requests
docker-compose logs nginx | grep "403\|404\|500"
```

## Checklist

### Deployment Oldidan

- [ ] Barcha API key'lar yangilangan
- [ ] `.env` fayli git'da yo'q
- [ ] `.gitignore` to'g'ri sozlangan
- [ ] Pre-commit hook o'rnatilgan
- [ ] SECRET_KEY production uchun yangi yaratilgan
- [ ] Database parollari kuchli (20+ characters)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS to'g'ri
- [ ] SSL sertifikat o'rnatilgan
- [ ] Firewall sozlangan
- [ ] Backup strategy mavjud

### Production'da

- [ ] SSH access faqat key-based
- [ ] Root login o'chirilgan
- [ ] UFW/iptables sozlangan
- [ ] Automatic security updates yoqilgan
- [ ] Log rotation sozlangan
- [ ] Monitoring tools o'rnatilgan
- [ ] Incident response plan mavjud

## Incident Response

Agar API key leak bo'lsa:

1. **ZUDLIK BILAN** key'ni bekor qiling
2. Yangi key yarating
3. Production'ni yangilang
4. Loglarni tekshiring (abuse bo'lganmi?)
5. Billing'ni monitor qiling

## Qo'shimcha Resurslar

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/5.0/topics/security/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Git Secrets](https://github.com/awslabs/git-secrets)

---

**ESLATMA**: Xavfsizlik - bu bir martalik jarayon emas, doimiy amaliyotdir!
