# 🚀 INVENTORY-SYS PRODUCTION TAYYORLASH VAZIFALARI

> **Maqsad:** Loyihani xavfsiz va ishonchli production muhitiga chiqarish
> **Yaratilgan:** 2026-01-23
> **Oxirgi yangilanish:** 2026-01-23

---

## 📋 VAZIFALAR RO'YXATI

### 🔴 KRITIK (Darhol bajarilishi shart)

- [x] **1. SECRET_KEY yangilash** ✅
  - Yangi xavfsiz kalit generatsiya qilindi
  - `.env.production` faylga qo'shildi

- [x] **2. Database parolini o'zgartirish** ✅
  - 32 belgili kuchli parol yaratildi
  - `.env.production` faylda saqlandi

- [x] **3. Hardcoded IP va URL larni olib tashlash** ✅
  - `docker-compose.yml` dan IP lar olib tashlandi
  - Environment variable lar ishlatilmoqda

- [x] **4. Production settings yaratish** ✅
  - `docker-compose.prod.yml` yaratildi
  - `nginx/nginx.prod.conf` yaratildi
  - Health check endpoint qo'shildi (`/api/health/`)

- [x] **5. Frontend production build** ✅
  - `frontend/Dockerfile` multi-stage build bilan
  - Nginx orqali serve qilinadi

---

### 🟠 YUQORI MUHIMLIK (Bajarildi)

- [x] **6. Testlar yozish** ✅
  - Model testlari (`test_models.py`)
  - Authentication testlari (`test_auth.py`)
  - API endpoint testlari (`test_api.py`)
  - Pytest konfiguratsiya (`pytest.ini`, `conftest.py`)

- [x] **7. Sentry konfiguratsiya** ✅
  - `settings.py` da Sentry integratsiyasi qo'shildi
  - `.env.production` da SENTRY_DSN qo'shildi

- [x] **8. Database backup strategiyasi** ✅
  - `scripts/backup.sh` - avtomatik backup
  - `scripts/restore.sh` - restore skript
  - Daily/Weekly/Monthly retention policy

---

### 🟡 PRODUCTION OLDIDAN (Sizdan kerak)

- [ ] **9. Domain sozlash**
  - `.env.production` da domenni kiriting
  - ALLOWED_HOSTS ni yangilang
  - CORS_ALLOWED_ORIGINS ni yangilang

- [ ] **10. SSL sertifikat olish** (ixtiyoriy)
  - Let's Encrypt yoki boshqa sertifikat
  - `nginx/ssl/` papkasiga joylashtirish
  - `nginx.prod.conf` da HTTPS yoqish

- [ ] **11. Email sozlamalarini yangilash**
  - `.env.production` da EMAIL_HOST_USER
  - Gmail App Password olish

- [ ] **12. Sentry DSN olish**
  - https://sentry.io dan ro'yxatdan o'ting
  - Django loyiha yarating
  - DSN ni `.env.production` ga qo'shing

---

## 📂 YARATILGAN FAYLLAR

| Fayl | Maqsad |
|------|--------|
| `docker-compose.prod.yml` | Production docker konfiguratsiya |
| `nginx/nginx.prod.conf` | Nginx reverse proxy + rate limiting |
| `backend/.env.production` | Backend production sozlamalari |
| `frontend/.env.production` | Frontend production sozlamalari |
| `backend/pytest.ini` | Pytest konfiguratsiya |
| `backend/conftest.py` | Test fixtures |
| `backend/inventory/tests/test_models.py` | Model testlari |
| `backend/inventory/tests/test_auth.py` | Auth testlari |
| `backend/inventory/tests/test_api.py` | API testlari |
| `scripts/backup.sh` | Database backup skript |
| `scripts/restore.sh` | Database restore skript |

---

## 🧪 TESTLARNI ISHGA TUSHIRISH

```bash
cd backend

# Barcha testlarni ishga tushirish
python manage.py test inventory.tests

# Yoki pytest bilan
pytest

# Coverage bilan
pytest --cov=inventory
```

---

## 💾 DATABASE BACKUP

```bash
# Docker container ichida
docker-compose exec backend /scripts/backup.sh daily

# Yoki cron bilan avtomatik
# Crontab ga qo'shing:
0 2 * * * docker-compose -f /path/to/docker-compose.prod.yml exec -T backend /scripts/backup.sh daily
0 3 * * 0 docker-compose -f /path/to/docker-compose.prod.yml exec -T backend /scripts/backup.sh weekly
0 4 1 * * docker-compose -f /path/to/docker-compose.prod.yml exec -T backend /scripts/backup.sh monthly
```

---

## 🚀 PRODUCTION GA CHIQARISH

### 1. Serverda loyihani clone qiling:
```bash
git clone <your-repo-url>
cd inventory-sys
```

### 2. `.env.production` fayllarini sozlang:
```bash
# Backend - quyidagilarni o'zgartiring:
# - ALLOWED_HOSTS (domeningiz)
# - CORS_ALLOWED_ORIGINS (domeningiz)
# - EMAIL sozlamalari
# - SENTRY_DSN (ixtiyoriy)
nano backend/.env.production

# Frontend
# - REACT_APP_API_URL (domeningiz)
nano frontend/.env.production
```

### 3. Docker orqali ishga tushiring:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 4. Tekshiring:
```bash
# Loglarni ko'ring
docker-compose -f docker-compose.prod.yml logs -f

# Health check
curl http://localhost/api/health/

# Testlarni ishga tushiring
docker-compose -f docker-compose.prod.yml exec backend pytest
```

---

## 📊 PROGRESS

| Holat | Soni |
|-------|------|
| ✅ Bajarildi | 8 |
| 🔄 Jarayonda | 0 |
| ⏳ Kutilmoqda | 4 (sizdan kerak) |

---

## ⚠️ MUHIM ESLATMALAR

1. **`.env.production` fayllarini HECH QACHON git'ga push qilmang!**
2. **Parollarni xavfsiz joyda saqlang**
3. **Testlarni production'dan oldin ishga tushiring**
4. **Database backup larni muntazam oling**
5. **Sentry orqali xatolarni kuzating**

---

## 🔗 FOYDALI HAVOLALAR

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Sentry Django Integration](https://docs.sentry.io/platforms/python/integrations/django/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Boshlash sanasi:** 2026-01-23
**Oxirgi yangilanish:** 2026-01-23
