# 🚀 Tez Deploy Qo'llanmasi

1-2 soatda production'ga deploy qilish uchun qisqa qo'llanma.

## ⚡ 5 Daqiqalik Setup

### 1. API Keylarni Xavfsizlashtiring (SHART!)

```bash
# ZUDLIK BILAN: Eski keylarni bekor qiling
# - OpenAI: https://platform.openai.com/api-keys
# - Gemini: https://makersuite.google.com/app/apikey
# - Gmail: https://myaccount.google.com/apppasswords

# Yangi keylar yarating
```

### 2. Production Environment

```bash
cd backend
cp .env.production.example .env.production
nano .env.production
```

To'ldiring:
```bash
SECRET_KEY=<python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=yourserver.com
DB_PASSWORD=<kuchli-parol>
OPENAI_API_KEY=<yangi-key>
GEMINI_API_KEY=<yangi-key>
FRONTEND_URL=https://yourserver.com
```

### 3. Deploy!

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🖥️ Server Setup (Ubuntu/Debian)

### VPS Tayyorlash (10 daqiqa)

```bash
# SSH orqali serverga kiring
ssh root@yourserver.com

# System yangilash
apt update && apt upgrade -y

# Docker o'rnatish
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose o'rnatish
apt install docker-compose-plugin -y

# Firewall sozlash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Git o'rnatish
apt install git -y
```

### Loyihani Klonlash

```bash
# Yangi user yaratish (tavsiya)
adduser deploy
usermod -aG docker deploy
su - deploy

# Loyihani klonlash
git clone https://github.com/yourusername/inventory-sys.git
cd inventory-sys
```

### Environment Sozlash

```bash
cd backend
cp .env.production.example .env.production

# Edit configuration
nano .env.production
```

Asosiy sozlamalar:
- `SECRET_KEY` - Yangi generate qiling
- `ALLOWED_HOSTS` - Server IP yoki domain
- `DB_PASSWORD` - Kuchli parol
- `FRONTEND_URL` - https://yourdomain.com
- API keylar

### Deploy

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🌐 Domain va SSL (15 daqiqa)

### Domain DNS Sozlamalari

```
A Record: @ -> your-server-ip
A Record: www -> your-server-ip
```

### SSL Sertifikat (Let's Encrypt)

```bash
# Certbot o'rnatish
apt install certbot -y

# Vaqtinchalik nginx to'xtatish
docker-compose -f docker-compose.production.yml stop nginx

# SSL olish
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# SSL fayllarni nusxalash
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

### Nginx SSL Yoqish

```bash
nano nginx/conf.d/default.conf
```

Comment'larni olib tashlang:
```nginx
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/privkey.pem;
```

HTTP -> HTTPS redirect'ni yoqing.

```bash
# Nginx restart
docker-compose -f docker-compose.production.yml restart nginx
```

## ✅ Tekshirish

```bash
# Container'lar ishlaydimi?
docker ps

# Sayt ochilmoqda?
curl http://yourserver.com/health

# API ishlayaptimi?
curl http://yourserver.com/api/

# Admin panel?
curl http://yourserver.com/admin/
```

Browser'da:
- `https://yourdomain.com` - Frontend
- `https://yourdomain.com/admin` - Admin panel
- `https://yourdomain.com/api` - API

## 📊 Post-Deployment

### Superuser Yaratish

```bash
docker-compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

### Backup Automation

```bash
# Crontab sozlash
crontab -e

# Har kuni soat 2 da backup
0 2 * * * cd /home/deploy/inventory-sys && ./scripts/backup.sh
```

### Monitoring

```bash
# Resource monitoring
docker stats

# Logs
docker-compose -f docker-compose.production.yml logs -f backend
```

## 🔧 Muammolarni Hal Qilish

### Container ishlamaydi

```bash
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs backend
```

### Database xatosi

```bash
docker-compose -f docker-compose.production.yml restart db
docker-compose -f docker-compose.production.yml logs db
```

### Static fayllar yo'q

```bash
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
docker-compose -f docker-compose.production.yml restart nginx
```

## 📝 Checklist

Deployment oldidan:

- [ ] API keylar yangilangan va xavfsiz
- [ ] `.env.production` to'liq to'ldirilgan
- [ ] DEBUG=False
- [ ] Server firewall sozlangan
- [ ] Domain DNS sozlangan
- [ ] SSL sertifikat o'rnatilgan

Deployment keyin:

- [ ] Barcha service'lar running
- [ ] HTTPS ishlayapti
- [ ] Admin panel accessible
- [ ] API responses correct
- [ ] Backup script sozlangan
- [ ] Monitoring yoqilgan

## 🆘 Yordam

Muammo bo'lsa:

1. `docker-compose logs -f` - Loglarni ko'ring
2. `docker ps` - Container statusini tekshiring
3. [DEPLOYMENT.md](DEPLOYMENT.md) - To'liq qo'llanma
4. [SECURITY.md](SECURITY.md) - Xavfsizlik

## ⚡ Performance Tips

- Minimum 2GB RAM (4GB tavsiya)
- SSD disk (HDD emas)
- Backup'lar uchun 20GB+ joy
- CDN (agar global users bo'lsa)

---

**Eslatma**: Bu minimal deployment. Production uchun to'liq [DEPLOYMENT.md](DEPLOYMENT.md) ni o'qing!
