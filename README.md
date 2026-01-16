# 📦 Inventory Management System

Django REST Framework va React asosida qurilgan zamonaviy inventarizatsiya boshqaruv tizimi.

Modern inventory management system built with Django REST Framework and React.

## 🚀 Xususiyatlar / Features

- ✅ **Jihozlar boshqaruvi** - Equipment management with full CRUD operations
- ✅ **Hodimlar va tayinlashlar** - Employee management and equipment assignments
- ✅ **QR kod generatsiya** - QR code generation for equipment tracking
- ✅ **AI asosida nakladnoy skanerlash** - AI-powered invoice/document scanning (Google Gemini)
- ✅ **Email bildirginomalari** - Email notifications for assignments
- ✅ **Dashboard statistika** - Real-time dashboard with statistics
- ✅ **Texnik xizmat ko'rsatish** - Maintenance tracking and scheduling
- ✅ **PostgreSQL ma'lumotlar bazasi** - PostgreSQL database support

## 🛠️ Texnologiyalar / Tech Stack

### Backend
- Python 3.11+
- Django 5.0
- Django REST Framework
- PostgreSQL
- Google Gemini AI
- OpenAI API

### Frontend
- React 18
- Axios
- React Router

## 📋 Talablar / Requirements

- Python 3.11 yoki yuqori
- PostgreSQL 12 yoki yuqori
- Node.js 18 yoki yuqori
- npm yoki yarn

## ⚙️ O'rnatish / Installation

### 1. Repository'ni klonlash / Clone Repository

```bash
git clone <your-repository-url>
cd inventory-sys
```

### 2. Backend sozlash / Backend Setup

```bash
# Virtual environment yaratish
# Create virtual environment
cd backend
python -m venv venv

# Virtual environment'ni faollashtirish
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Kerakli kutubxonalarni o'rnatish
# Install dependencies
pip install -r requirements.txt

# .env faylini yaratish
# Create .env file
copy .env.example .env
# yoki Linux/Mac uchun: cp .env.example .env

# .env faylini tahrirlang va barcha qiymatlarni kiriting!
# Edit .env file and fill in all values!
# Muhim: SECRET_KEY, DB_PASSWORD, va API kalitlarni o'zgartiring
# Important: Change SECRET_KEY, DB_PASSWORD, and API keys
```

### 3. PostgreSQL sozlash / PostgreSQL Setup

```bash
# PostgreSQL'ga ulanish
# Connect to PostgreSQL
psql -U postgres

# Ma'lumotlar bazasi yaratish
# Create database
CREATE DATABASE inventory_db;

# Chiqish
# Exit
\q
```

### 4. Database migratsiyalari / Database Migrations

```bash
# Migratsiyalarni yaratish
# Create migrations
python manage.py makemigrations

# Migratsiyalarni bajarish
# Run migrations
python manage.py migrate

# Superuser yaratish
# Create superuser
python manage.py createsuperuser
```

### 5. Backend serverni ishga tushirish / Run Backend Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Backend http://localhost:8000 da ishga tushadi

### 6. Frontend sozlash / Frontend Setup

Yangi terminal oching:

```bash
cd frontend

# Paketlarni o'rnatish
# Install packages
npm install

# Development serverni ishga tushirish
# Run development server
npm start
```

Frontend http://localhost:3000 da ishga tushadi

## 🔑 Environment Variables

`.env` faylida quyidagi o'zgaruvchilarni to'ldiring:

### Django Settings
- `SECRET_KEY` - Django secret key (yarating: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG` - Debug rejimi (development: True, production: False)
- `ALLOWED_HOSTS` - Ruxsat berilgan hostlar

### Database
- `DB_NAME` - Ma'lumotlar bazasi nomi (default: inventory_db)
- `DB_USER` - PostgreSQL foydalanuvchi
- `DB_PASSWORD` - PostgreSQL parol (kuchli parol kiriting!)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)

### Email (Gmail)
- `EMAIL_HOST_USER` - Gmail manzilingiz
- `EMAIL_HOST_PASSWORD` - Gmail App Password (https://myaccount.google.com/apppasswords)

### AI API Keys
- `OPENAI_API_KEY` - OpenAI API key (https://platform.openai.com/api-keys)
- `GEMINI_API_KEY` - Google Gemini API key (https://makersuite.google.com/app/apikey)

## 📱 API Endpoints

### Authentication
- `POST /api/auth/login/` - Tizimga kirish
- `POST /api/auth/logout/` - Tizimdan chiqish

### Equipment
- `GET /api/equipment/` - Barcha jihozlar ro'yxati
- `POST /api/equipment/` - Yangi jihoz qo'shish
- `GET /api/equipment/{id}/` - Jihoz ma'lumotlari
- `PUT /api/equipment/{id}/` - Jihozni yangilash
- `DELETE /api/equipment/{id}/` - Jihozni o'chirish
- `GET /api/equipment/{id}/qr_code/` - QR kod olish

### Employees
- `GET /api/employees/` - Barcha hodimlar
- `POST /api/employees/` - Yangi hodim qo'shish
- `GET /api/employees/{id}/` - Hodim ma'lumotlari
- `PUT /api/employees/{id}/` - Hodimni yangilash
- `DELETE /api/employees/{id}/` - Hodimni o'chirish

### Assignments
- `GET /api/assignments/` - Barcha tayinlashlar
- `POST /api/assignments/` - Jihozni tayinlash
- `GET /api/assignments/{id}/` - Tayinlash ma'lumotlari
- `POST /api/assignments/{id}/return/` - Jihozni qaytarish
- `GET /api/assignments/dashboard_stats/` - Dashboard statistika

### Maintenance
- `GET /api/maintenance/` - Texnik xizmat ro'yxati
- `POST /api/maintenance/` - Yangi texnik xizmat
- `PUT /api/maintenance/{id}/` - Texnik xizmatni yangilash

### Document Scanning
- `POST /api/scan-nakladnoy/` - Nakladnoy rasmini skanerlash (AI)

## 🔒 Xavfsizlik / Security

- ⚠️ `.env` faylini **HECH QACHON** Git'ga commit qilmang!
- ⚠️ Production'da `DEBUG=False` qiling
- ⚠️ Kuchli parollar ishlating
- ⚠️ API kalitlarni maxfiy saqlang
- ⚠️ `ALLOWED_HOSTS` ni production'da aniq domenlar bilan to'ldiring

## 📝 Development

### Code Style
- Backend: PEP 8 standartiga rioya qiling
- Frontend: ESLint konfiguratsiyasiga amal qiling

### Testing
```bash
# Backend testlar
cd backend
python manage.py test

# Frontend testlar
cd frontend
npm test
```

## 🐛 Muammolarni hal qilish / Troubleshooting

### Database xatosi: "no such column"
Migratsiyalarni qayta bajaring:
```bash
python manage.py migrate --run-syncdb
```

### CORS xatosi
`.env` faylidagi `CORS_ALLOWED_ORIGINS` ga frontend URL'ni qo'shing

### Email yuborilmayapti
- Gmail'da 2-Step Verification yoqilganligini tekshiring
- App Password to'g'ri kiritilganligini tekshiring

## 📄 License

MIT License

## 👨‍💻 Muallif / Author

[Your Name]

## 🤝 Hissa qo'shish / Contributing

Pull requestlar qabul qilinadi! Katta o'zgarishlar uchun avval issue oching.

---

**Eslatma:** Production muhitga o'tkazishdan oldin barcha xavfsizlik sozlamalarini tekshiring!
