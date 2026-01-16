# ✅ Production Deployment Checklist

Har bir qadamni belgilang. Barcha belgiler qo'yilgandan keyin deploy qilishingiz mumkin.

## 🔐 Xavfsizlik (SHART!)

### API Keys va Secrets

- [ ] **OPENAI_API_KEY** - Eski key bekor qilindi va yangi yaratildi
- [ ] **GEMINI_API_KEY** - Eski key bekor qilindi va yangi yaratildi
- [ ] **EMAIL_HOST_PASSWORD** - Yangi Gmail App Password yaratildi
- [ ] **SECRET_KEY** - Yangi Django secret key generate qilindi
- [ ] **DB_PASSWORD** - Kuchli database parol (20+ chars)
- [ ] Barcha yangi keylar `.env.production` ga qo'shildi
- [ ] Eski `.env` fayli git'dan o'chirildi

### Git Xavfsizligi

- [ ] `.gitignore` fayli to'g'ri sozlangan
- [ ] `.env`, `.env.production` git'da yo'q
- [ ] Git tarixida sensitive data yo'q
- [ ] Pre-commit hook o'rnatilgan (ixtiyoriy)

## 🌐 Environment Configuration

### Backend Environment (.env.production)

- [ ] `SECRET_KEY` - Yangi va unique
- [ ] `DEBUG=False` - Production uchun o'chirilgan
- [ ] `ALLOWED_HOSTS` - To'g'ri domain/IP
- [ ] `DB_ENGINE` - PostgreSQL
- [ ] `DB_NAME` - Database nomi
- [ ] `DB_USER` - Database user
- [ ] `DB_PASSWORD` - Kuchli parol
- [ ] `DB_HOST=db` - Docker service nomi
- [ ] `DB_PORT=5432` - PostgreSQL porti
- [ ] `CORS_ALLOWED_ORIGINS` - Production URL'lar
- [ ] `EMAIL_*` - Email sozlamalari to'g'ri
- [ ] `FRONTEND_URL` - Production frontend URL
- [ ] `REACT_APP_API_URL` - Production API URL

### Optional Settings

- [ ] `REDIS_URL` - Agar caching kerak bo'lsa
- [ ] `SENTRY_DSN` - Error tracking uchun
- [ ] `CELERY_BROKER_URL` - Background tasks uchun

## 🖥️ Server Setup

### VPS/Server Requirements

- [ ] Server xarid qilindi (minimal: 2GB RAM, 2 CPU)
- [ ] Server OS: Ubuntu 20.04+ yoki Debian 11+
- [ ] Root/sudo access mavjud
- [ ] SSH key-based authentication sozlangan

### Server Preparation

- [ ] System yangilandi: `apt update && apt upgrade -y`
- [ ] Docker o'rnatildi: `curl -fsSL https://get.docker.com | sh`
- [ ] Docker Compose o'rnatildi
- [ ] Git o'rnatildi: `apt install git -y`
- [ ] UFW firewall sozlandi va yoqildi
- [ ] Port 22 (SSH) ochiq
- [ ] Port 80 (HTTP) ochiq
- [ ] Port 443 (HTTPS) ochiq

### DNS va Domain

- [ ] Domain xarid qilindi (yoki IP ishlatiladi)
- [ ] DNS A record: `@` -> server IP
- [ ] DNS A record: `www` -> server IP
- [ ] DNS propagation tugallandi (24 soat)

## 📦 Deployment Files

### Files Check

- [ ] `docker-compose.production.yml` mavjud
- [ ] `backend/Dockerfile.production` mavjud
- [ ] `frontend/Dockerfile` mavjud
- [ ] `nginx/nginx.conf` mavjud
- [ ] `nginx/conf.d/default.conf` mavjud
- [ ] `scripts/deploy.sh` executable
- [ ] `scripts/backup.sh` executable
- [ ] `scripts/restore.sh` executable

### Configuration Files

- [ ] `backend/.env.production` to'liq to'ldirilgan
- [ ] Nginx config'da domain to'g'ri
- [ ] Docker compose'da volume path'lar to'g'ri
- [ ] Resource limits maqbul (RAM, CPU)

## 🚀 Initial Deployment

### Build va Start

- [ ] Loyiha server'ga clone qilindi
- [ ] `.env.production` yaratildi va to'ldirildi
- [ ] `./scripts/deploy.sh` muvaffaqiyatli ishladi
- [ ] Barcha container'lar running: `docker ps`

### Database Setup

- [ ] Migrations bajarildi
- [ ] Superuser yaratildi
- [ ] Test data yuklandi (agar kerak bo'lsa)

### Static Files

- [ ] Static files to'plandi
- [ ] Media directory yaratildi
- [ ] Permissions to'g'ri

## 🔒 SSL/HTTPS (Tavsiya etiladi)

### Let's Encrypt Setup

- [ ] Certbot o'rnatildi
- [ ] SSL sertifikat olindi
- [ ] Sertifikat nginx'ga nusxalandi
- [ ] Nginx config'da SSL yoqildi
- [ ] HTTP -> HTTPS redirect yoqildi
- [ ] Nginx restart qilindi
- [ ] HTTPS ishlayapti

### SSL Auto-renewal

- [ ] Certbot auto-renewal sozlangan
- [ ] Cron job tekshirildi

## ✅ Testing

### Functionality Tests

- [ ] Frontend ochiladi: `https://yourdomain.com`
- [ ] API ishlayapti: `https://yourdomain.com/api/`
- [ ] Admin panel accessible: `https://yourdomain.com/admin/`
- [ ] Login ishlayapti
- [ ] QR code generation ishlayapti
- [ ] File upload ishlayapti
- [ ] Email yuborish ishlayapti (test qiling)

### Performance Tests

- [ ] Sahifa 3 sekunddan tez ochiladi
- [ ] API response time 500ms dan kam
- [ ] Static files cache ishlayapti
- [ ] Gzip compression yoqilgan

### Security Tests

- [ ] HTTPS majburiy
- [ ] Admin panel faqat HTTPS
- [ ] CORS to'g'ri ishlayapti
- [ ] Rate limiting ishlayapti
- [ ] Security headers mavjud

## 📊 Monitoring va Maintenance

### Logging

- [ ] Container logs accessible: `docker-compose logs`
- [ ] Nginx access logs ishlayapti
- [ ] Nginx error logs ishlayapti
- [ ] Django logs yozilmoqda

### Backup Strategy

- [ ] Backup script ishlayapti
- [ ] Birinchi backup yaratildi
- [ ] Backup restore test qilindi
- [ ] Cron job backup uchun sozlangan
- [ ] Backup storage yetarli (20GB+)

### Monitoring Tools (Optional)

- [ ] Sentry error tracking sozlangan
- [ ] Uptime monitoring (UptimeRobot, Pingdom)
- [ ] Resource monitoring (RAM, CPU, Disk)
- [ ] Email alerts sozlangan

## 🔄 Post-Deployment

### Documentation

- [ ] Admin credentials xavfsiz saqlangan
- [ ] Database credentials documented
- [ ] Server access details saqlangan
- [ ] Deployment process documented

### Team Access

- [ ] SSH keys team members uchun
- [ ] Admin panel access berildi
- [ ] Backup access ajratildi
- [ ] Emergency contacts documented

### Maintenance Plan

- [ ] Weekly backup schedule
- [ ] Monthly security updates
- [ ] Quarterly performance review
- [ ] Incident response plan

## 📝 Final Verification

### Production Readiness

- [ ] DEBUG=False confirmed
- [ ] Secret keys unique va xavfsiz
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] Security headers configured
- [ ] SSL/HTTPS working
- [ ] Backups automated
- [ ] Monitoring active

### Launch Checklist

- [ ] Stakeholder approval
- [ ] Team notified
- [ ] Support plan ready
- [ ] Rollback plan ready
- [ ] Success criteria defined
- [ ] Launch communication sent

## 🎉 GO LIVE!

Barcha checkbox'lar belgilangandan keyin:

```bash
# Final check
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs --tail=50

# Monitor
docker stats

# Celebrate! 🎊
```

---

## 🆘 Emergency Contacts

- **Server Provider**: ___________________
- **Domain Provider**: ___________________
- **Database Admin**: ___________________
- **Lead Developer**: ___________________

## 📚 Important Links

- Server: `https://___________________`
- Admin Panel: `https://___________________/admin`
- API Docs: `https://___________________/api`
- Monitoring: `https://___________________`
- Logs: `ssh user@server "docker-compose logs"`

---

**Last Updated**: ___________________
**Deployed By**: ___________________
**Deployment Date**: ___________________
**Version**: ___________________
