# Kompaniya Inventarizatsiya Tizimi (QR Kod bilan)

Django va React yordamida yaratilgan hodim va qurilma inventarizatsiya tizimi. Har bir qurilma va hodim uchun QR kod generatsiya qilinadi.

## Asosiy Xususiyatlar

### QR Kod Tizimi
- Har bir qurilma va hodimga avtomatik QR kod yaratiladi
- QR kodlar hodim stolida joylashtiriladi
- Skaner orqali qurilma va hodim ma'lumotlarini ko'rish
- Real-time inventarizatsiya tekshiruvi

### Qurilma Boshqaruvi
- Kompyuter, printer, monitor va boshqa qurilmalar
- Seriya raqami, inventar raqami
- Xarid sanasi, narxi, kafolat muddati
- Holati: Mavjud, Tayinlangan, Ta'mirlashda, Foydalanishdan chiqarilgan

### Hodim Boshqaruvi
- Bo'lim, lavozim, hodim ID
- Hodimga tayinlangan qurilmalar ro'yxati
- QR kod orqali hodim ma'lumotlari

### Tayinlash Tarixi
- Qurilma kimda turganini kuzatish
- Qachondan beri foydalanyapti
- Tayinlash va qaytarish tarixi
- Qurilma holati

### Inventarizatsiya Tekshiruvi
- Oxirgi inventarizatsiya sanasi
- Qurilma joylashuvi
- Holati (ishlayaptimi)
- Hodim tasdigi

### Ta'mirlash Tarixi
- Ta'mirlash, yangilash yozuvlari
- Xarajatlar
- Ta'mirlash sanasi

## Texnologiyalar

### Backend
- Django 5.0
- Django REST Framework
- qrcode library (QR kod generatsiya)
- SQLite (rivojlantirish uchun)
- Python 3.13

### Frontend (Kelajakda yangilanadi)
- React 18
- React Router
- Axios
- QR kod skaner
- Modern CSS

## O'rnatish va ishga tushirish

### Backend (Django)

1. Backend papkasiga o'ting:
```bash
cd backend
```

2. Virtual environmentni faollashtiring:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Agar kerakli paketlar o'rnatilmagan bo'lsa:
```bash
pip install -r requirements.txt
```

4. Migratsiyalar allaqachon qo'llanilgan. Server ishga tushirish:
```bash
python manage.py runserver
```

Backend http://localhost:8000 da ishlaydi.

### Admin Panel

- URL: http://localhost:8000/admin
- Login: `admin`
- Parol: `admin123`

### Test Ma'lumotlari

Tizim quyidagi test ma'lumotlar bilan ta'minlangan:
- 4 ta bo'lim (IT, Buxgalteriya, Marketing, HR)
- 5 ta hodim (har biri o'z QR kodiga ega)
- 5 ta qurilma kategoriyasi
- 8 ta qurilma (har biri o'z QR kodiga ega)
- 6 ta tayinlash
- 3 ta inventarizatsiya tekshiruvi
- 2 ta ta'mirlash yozuvi

## API Endpointlari

### Asosiy endpointlar:
- `GET /api/departments/` - Barcha bo'limlar
- `GET /api/employees/` - Barcha hodimlar
- `GET /api/equipment-categories/` - Qurilma kategoriyalari
- `GET /api/equipment/` - Barcha qurilmalar
- `GET /api/assignments/` - Tayinlashlar
- `GET /api/inventory-checks/` - Inventarizatsiya tekshiruvlari
- `GET /api/maintenance-records/` - Ta'mirlash yozuvlari

### Qurilma maxsus endpointlari:
- `POST /api/equipment/{id}/assign/` - Hodimga tayinlash
- `POST /api/equipment/{id}/return_equipment/` - Qaytarib olish
- `POST /api/equipment/{id}/inventory_check/` - Inventarizatsiya tekshiruvi
- `GET /api/equipment/{id}/scan/` - QR kod orqali ma'lumot olish

### QR Kod Skanerlash:
- `POST /api/qr-scan/scan/` - QR koddan ma'lumot olish
  - Request: `{"qr_data": "EQUIPMENT:INV-001"}` yoki `{"qr_data": "EMPLOYEE:EMP001"}`
  - Response: Qurilma yoki hodim ma'lumotlari

### Dashboard:
- `GET /api/assignments/dashboard_stats/` - Dashboard statistikasi

## QR Kod Formati

### Qurilma QR kodi:
```
EQUIPMENT:INV-001
```

### Hodim QR kodi:
```
EMPLOYEE:EMP001
```

QR kod skanerlanganda, tizim avtomatik ravishda qurilma yoki hodim ma'lumotlarini ko'rsatadi.

## Loyiha Tuzilishi

```
inventory-sys/
├── backend/                   # Django backend
│   ├── inventory/            # Asosiy ilova
│   │   ├── models.py         # Ma'lumotlar modellari
│   │   │   ├── Department   - Bo'limlar
│   │   │   ├── Employee     - Hodimlar
│   │   │   ├── EquipmentCategory - Qurilma kategoriyalari
│   │   │   ├── Equipment    - Qurilmalar
│   │   │   ├── Assignment   - Tayinlashlar
│   │   │   ├── InventoryCheck - Inventarizatsiya
│   │   │   └── MaintenanceRecord - Ta'mirlash
│   │   ├── serializers.py   # DRF serializerlar
│   │   ├── views.py         # API viewlar
│   │   ├── urls.py          # URL marshrutlar
│   │   └── admin.py         # Admin panel
│   ├── media/               # QR kodlar va rasmlar
│   │   ├── qr_codes/
│   │   │   ├── employees/  - Hodim QR kodlari
│   │   │   └── equipment/  - Qurilma QR kodlari
│   │   └── equipment/      - Qurilma rasmlari
│   ├── manage.py
│   └── requirements.txt
│
└── frontend/                 # React frontend (kelajakda)
```

## Qurilma Tayinlash Jarayoni

1. **Yangi qurilma qo'shish**:
   - Admin panelda yoki API orqali qurilma yaratiladi
   - Avtomatik QR kod generatsiya qilinadi
   - QR kodning rasmini yuklab oling

2. **Hodimga tayinlash**:
   - API: `POST /api/equipment/{id}/assign/`
   - Request: `{"employee_id": 1, "condition": "Yaxshi holatda", "notes": "Ish uchun"}`
   - Qurilma holati "ASSIGNED" ga o'zgaradi

3. **QR kod joylash**:
   - QR kodning rasmini chop eting
   - Hodim stolida joylashtiring

4. **Inventarizatsiya tekshiruvi**:
   - QR kodni skanerlang
   - Qurilma ma'lumotlarini ko'ring:
     - Hozir kimda turgani
     - Qachondan beri
     - Oxirgi inventarizatsiya
     - To'liq tarix

5. **Qaytarib olish**:
   - API: `POST /api/equipment/{id}/return_equipment/`
   - Request: `{"condition": "Yaxshi", "notes": "Qaytarildi"}`
   - Qurilma holati "AVAILABLE" ga o'zgaradi

## Kelajakda Qo'shilishi Mumkin

- React frontend (Dashboard, QR skaner, Forms)
- Telefon ilovasi (QR skaner bilan)
- QR kod printer integratsiyasi
- Excel/PDF hisobotlar
- Email bildirishnomalar (kafolat tugaganda)
- Mobil responsiv interfeys
- Real-time inventarizatsiya dashboard
- Barcode skaner integratsiyasi

## Foydalanish Misollari

### 1. QR Koddan Qurilma Ma'lumotlarini Olish

```bash
curl -X POST http://localhost:8000/api/qr-scan/scan/ \
  -H "Content-Type: application/json" \
  -d '{"qr_data": "EQUIPMENT:INV-001"}'
```

Javob:
```json
{
  "type": "equipment",
  "data": {
    "id": 1,
    "name": "Lenovo ThinkPad T14",
    "current_assignment": {
      "employee": "Anvar Karimov",
      "employee_id": "EMP001",
      "department": "IT bo'limi",
      "assigned_date": "2025-12-23T...",
      "days_assigned": 0
    },
    "last_inventory_check": {
      "check_date": "2025-12-23T...",
      "checked_by": "admin",
      "condition": "Yaxshi holatda",
      "is_functional": true
    },
    ...
  }
}
```

### 2. Hodim QR Kodi

```bash
curl -X POST http://localhost:8000/api/qr-scan/scan/ \
  -H "Content-Type: application/json" \
  -d '{"qr_data": "EMPLOYEE:EMP001"}'
```

Javob hodim ma'lumotlari va unga tayinlangan barcha qurilmalar ro'yxatini qaytaradi.

## Deployment

Production muhitga deploy qilish uchun:

1. **Tez boshlash**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - 1-2 soatda deploy qilish
2. **To'liq qo'llanma**: [DEPLOYMENT.md](DEPLOYMENT.md) - Batafsil ko'rsatmalar
3. **Xavfsizlik**: [SECURITY.md](SECURITY.md) - API keylar va parollar
4. **Xulosa**: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - Barcha o'zgarishlar

### Quick Deploy

```bash
# 1. API keylarni xavfsizlashtiring (SHART!)
# 2. Production environment sozlang
cd backend
cp .env.production.example .env.production
nano .env.production

# 3. Deploy!
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## Production Arxitektura

```
                    ┌─────────────┐
                    │   Nginx     │  (Port 80/443)
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
       ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
       │ React   │    │ Django  │   │  Media  │
       │Frontend │    │ Backend │   │ /Static │
       │ (Nginx) │    │(Gunicorn)   │  Files  │
       └─────────┘    └────┬────┘   └─────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
          ┌─────▼────┐ ┌───▼────┐ ┌──▼─────┐
          │PostgreSQL│ │ Redis  │ │ Celery │
          │ Database │ │ Cache  │ │(optional)
          └──────────┘ └────────┘ └────────┘
```

## Docker Services

- **nginx**: Reverse proxy, SSL termination, static files
- **frontend**: React app (production build)
- **backend**: Django + DRF API (Gunicorn)
- **db**: PostgreSQL 15 database
- **redis**: Caching va session storage

## Muallif

Kompaniya Inventarizatsiya Tizimi - 2025

## Litsenziya

Bu loyiha ochiq kodli dastur emas. Barcha huquqlar himoyalangan.
