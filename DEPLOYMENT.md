# Deployment Guide - Inventory Management System

## 🚨 XAVFSIZLIK OGOHLANTIRISHI

Deployment qilishdan oldin **SHART**:

1. **.env faylidagi API keylarni xavfsizlashtiring**
   - Hozirgi `.env` faylidagi OPENAI_API_KEY va GEMINI_API_KEY'larni **ZUDLIK BILAN** bekor qiling
   - Gmail EMAIL_HOST_PASSWORD'ni ham xavfsiz saqlang
   - Yangi API keylar yarating va production uchun alohida saqlang

2. **.env.production faylini to'g'ri sozlang**
   - `.env.production.example` faylini `.env.production` ga nusxalang
   - Barcha qiymatlarni production muhiti uchun yangilang
   - **HECH QACHON** production .env faylini git'ga push qilmang!

## Tizim Talablari

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM (tavsiya etiladi: 8GB)
- 20GB+ bo'sh disk maydoni
- Linux/MacOS/Windows (Docker Desktop bilan)

## Deployment Jarayoni

### 1. Environment Variables Sozlash

Production uchun `.env.production` faylini yarating:

```bash
cd backend
cp .env.production.example .env.production
```

`.env.production` faylini tahrirlang va quyidagilarni o'zgartiring:

```bash
# SHART: O'zgartirish kerak
SECRET_KEY=<yangi-secret-key-generate-qiling>
DB_PASSWORD=<kuchli-parol>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email sozlamalari
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<gmail-app-password>

# API Keys (agar kerak bo'lsa)
OPENAI_API_KEY=<yangi-openai-key>
GEMINI_API_KEY=<yangi-gemini-key>

# Domain sozlamalari
FRONTEND_URL=https://yourdomain.com
REACT_APP_API_URL=https://yourdomain.com/api
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Secret Key Generatsiya Qilish

Django uchun yangi secret key yarating:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Production Deployment

#### A) Avtomatik Deploy (Tavsiya etiladi)

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Script quyidagilarni bajaradi:
- Environment tekshiradi
- Mavjud database'ni backup qiladi
- Docker container'larni build qiladi
- Migration'larni bajaradi
- Static fayllarni to'playdi

#### B) Qo'lda Deploy

```bash
# 1. Docker container'larni build qilish
docker-compose -f docker-compose.production.yml build

# 2. Container'larni ishga tushirish
docker-compose -f docker-compose.production.yml up -d

# 3. Migration'larni bajarish
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate

# 4. Static fayllarni to'plash
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput

# 5. Superuser yaratish (birinchi marta)
docker-compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### 4. SSL/HTTPS Sozlash (Tavsiya etiladi)

Let's Encrypt bilan SSL sertifikat olish:

```bash
# Certbot o'rnatish
sudo apt-get install certbot

# SSL sertifikat olish
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Sertifikatlarni nginx uchun nusxalash
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

`nginx/conf.d/default.conf` da SSL sozlamalarini yoqing (comment'larni olib tashlang).

### 5. Monitoring va Logs

Container loglarini ko'rish:

```bash
# Barcha loglar
docker-compose -f docker-compose.production.yml logs -f

# Faqat backend
docker-compose -f docker-compose.production.yml logs -f backend

# Faqat database
docker-compose -f docker-compose.production.yml logs -f db
```

### 6. Database Backup va Restore

#### Backup yaratish:

```bash
./scripts/backup.sh
```

Backup'lar `./backups/` papkasida saqlanadi.

#### Restore qilish:

```bash
./scripts/restore.sh ./backups/backup_20250112_120000.sql.gz
```

### 7. Yangilanishlarni Deploy Qilish

Yangi kod o'zgarishlarini deploy qilish:

```bash
# 1. Git'dan yangilanishlarni olish
git pull

# 2. Container'larni qayta build qilish
docker-compose -f docker-compose.production.yml build

# 3. Yangi container'larni ishga tushirish
docker-compose -f docker-compose.production.yml up -d

# 4. Migration'larni bajarish
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate
```

## Server Konfiguratsiyasi

### Recommended Server Specs

- **Minimal**: 2 CPU, 4GB RAM, 20GB SSD
- **Tavsiya etiladi**: 4 CPU, 8GB RAM, 50GB SSD
- **Ko'p foydalanuvchi uchun**: 8 CPU, 16GB RAM, 100GB SSD

### Firewall Sozlamalari

```bash
# UFW firewall (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Docker Resource Limits

`docker-compose.production.yml` da resource limit'lar sozlangan:

- **Backend**: 2 CPU, 2GB RAM
- **Database**: 1 CPU, 1GB RAM
- **Frontend**: 0.5 CPU, 512MB RAM
- **Redis**: 0.5 CPU, 512MB RAM
- **Nginx**: 1 CPU, 512MB RAM

## Muammolarni Hal Qilish

### Container ishga tushmaydi

```bash
# Container statusini tekshirish
docker-compose -f docker-compose.production.yml ps

# Loglarni ko'rish
docker-compose -f docker-compose.production.yml logs backend

# Container'ni qayta ishga tushirish
docker-compose -f docker-compose.production.yml restart backend
```

### Database ulanish xatosi

```bash
# Database container ishlayotganini tekshirish
docker ps | grep inventory_db

# Database loglarini ko'rish
docker-compose -f docker-compose.production.yml logs db

# Database'ga qo'lda ulanish
docker exec -it inventory_db psql -U inventory_user -d inventory_db
```

### Static fayllar ko'rinmaydi

```bash
# Static fayllarni qayta to'plash
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput --clear

# Nginx'ni qayta ishga tushirish
docker-compose -f docker-compose.production.yml restart nginx
```

### Disk maydoni tugaydi

```bash
# Eski Docker image'larni tozalash
docker system prune -a

# Eski backup'larni o'chirish (7 kundan eski)
find ./backups -name "*.sql.gz" -mtime +7 -delete

# Log fayllarni tozalash
docker-compose -f docker-compose.production.yml exec backend find /app/logs -name "*.log" -mtime +30 -delete
```

## Production Checklist

- [ ] `.env.production` fayli to'g'ri sozlangan
- [ ] SECRET_KEY yangilangan (dev key'dan farqli)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS to'g'ri sozlangan
- [ ] Database parollari kuchli
- [ ] SSL sertifikat o'rnatilgan
- [ ] Email sozlamalari to'g'ri
- [ ] Backup script ishlamoqda
- [ ] Monitoring sozlangan
- [ ] Firewall sozlangan
- [ ] API key'lar production uchun yangi yaratilgan
- [ ] .env fayllar git'ga qo'shilmagan

## Performance Optimization

### Database Optimization

```sql
-- Database index'larni tekshirish
docker exec -it inventory_db psql -U inventory_user -d inventory_db

-- Vacuum analyze
VACUUM ANALYZE;

-- Index'lar haqida ma'lumot
SELECT * FROM pg_stat_user_indexes;
```

### Redis Cache

Backend'da caching yoqilgan. Cache'ni tozalash:

```bash
docker exec -it inventory_redis redis-cli FLUSHALL
```

### Gunicorn Workers

Backend worker'lar soni: `(2 x CPU cores) + 1`

Hozirgi sozlama: 4 workers, 2 threads

O'zgartirish uchun `docker-compose.production.yml` da:

```yaml
command: gunicorn ... --workers 8 --threads 4
```

## Monitoring va Analytics

### Health Check

```bash
# Backend health
curl http://localhost/api/health/

# Frontend health
curl http://localhost/health

# Database health
docker exec inventory_db pg_isready -U inventory_user
```

### Resource Monitoring

```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Logs size
du -sh nginx/logs/ backend/logs/
```

## Qo'shimcha Havolalar

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
- [Nginx Security](https://www.nginx.com/blog/nginx-security-best-practices/)

## Yordam

Muammo yuzaga kelsa:

1. Loglarni tekshiring: `docker-compose logs -f`
2. Container statusini ko'ring: `docker-compose ps`
3. GitHub Issues'da muammo yarating
4. Dokumentatsiyani qayta o'qing

---

**Eslatma**: Production deployment xavfsizlik va barqarorlikka jiddiy yondashishni talab qiladi. Barcha tavsiyalarga amal qiling!
