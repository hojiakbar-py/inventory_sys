# Inventarni Boshqarish Tizimi

Ushbu qo'llanma `inventory-sys` loyihasini ishga tushurish uchun mo'ljallangan.

---

## Ishga tushurish bo'yicha qo'llanma (O'zbekcha)

### 1. Docker orqali tezkor ishga tushurish (Eng oson usul)

Bu usul loyihani eng tez va oson ishga tushurish imkonini beradi. Kompyuteringizda **Docker** va **Docker Compose** o'rnatilgan bo'lishi kerak.

1.  **Loyihani yuklab oling:**
    ```bash
    git clone https://github.com/hojiakbar-py/inventory_sys.git
    cd inventory_sys
    ```

2.  **Konfiguratsiya faylini yarating:**
    `backend/` papkasida `.env.example` faylidan nusxa olib, `.env` nomli yangi fayl yarating.
    ```bash
    # Windows
    copy backend\.env.example backend\.env

    # Linux/Mac
    cp backend/.env.example backend/.env
    ```
    Endi `backend/.env` faylini ochib, kerakli ma'lumotlarni to'ldiring (masalan, ma'lumotlar bazasi paroli, API kalitlari). Batafsil ma'lumot uchun pastdagi **Environment Variables** bo'limiga qarang. **HECH BO'LMAGANDA `SECRET_KEY` va ma'lumotlar bazasi sozlamalarini to'ldirishingiz kerak.**

3.  **Docker-ni ishga tushuring:**
    Asosiy papkadan (root directory) quyidagi buyruqni bajaring:
    ```bash
    docker-compose up --build -d
    ```

4.  **Tayyor!**
    Tizim to'liq ishga tushgandan so'ng, uni brauzeringizda ochishingiz mumkin:
    -   **Frontend (React):** [http://localhost:3000](http://localhost:3000)
    -   **Backend (Django API):** [http://localhost:8000](http://localhost:8000)

### 2. Qo'lda o'rnatish

Agar loyihani Docker'siz, o'zingizning kompyuteringizda to'g'ridan-to'g'ri ishga tushurmoqchi bo'lsangiz, pastdagi ingliz tilidagi batafsil qo'llanmaga rioya qiling (**Quick Start** bo'limi).

---
<hr>

# Inventory Management System

Modern inventory and equipment management system built with Django REST Framework and React.

Zamonaviy inventarizatsiya va jihozlarni boshqarish tizimi - Django REST Framework va React asosida qurilgan.

------

## Features

- **Equipment Management** - Complete CRUD operations for equipment tracking
- **Employee Management** - Employee database with assignment history
- **Equipment Assignment** - Track equipment assigned to employees
- **QR Code Generation** - Generate QR codes for quick equipment identification
- **AI Document Scanning** - Scan invoices/documents using Google Gemini AI
- **Email Notifications** - Automated email alerts for assignments
- **Dashboard Statistics** - Real-time analytics and reporting
- **Maintenance Tracking** - Schedule and track equipment maintenance

## Tech Stack

**Backend:**
- Python 3.11+
- Django 5.0
- Django REST Framework
- PostgreSQL
- Google Gemini AI
- OpenAI API

**Frontend:**
- React 18
- Axios
- React Router

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Node.js 18+
- npm or yarn

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/hojiakbar-py/inventory_sys.git
cd inventory_sys
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env and configure:
# - SECRET_KEY (generate new one)
# - Database credentials
# - Email settings
# - AI API keys
```

#### 3. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE inventory_db;
\q

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend will run at `http://localhost:8000`

#### 4. Frontend Setup

Open new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run at `http://localhost:3000`

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

### Required Settings

```bash
# Django
SECRET_KEY=your-secret-key-here  # Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Gmail SMTP (for notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Get from: https://myaccount.google.com/apppasswords

# AI APIs (optional)
OPENAI_API_KEY=your-openai-key  # https://platform.openai.com/api-keys
GEMINI_API_KEY=your-gemini-key  # https://makersuite.google.com/app/apikey
```

---

## API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | User login |
| POST | `/api/auth/logout/` | User logout |

### Equipment

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/equipment/` | List all equipment |
| POST | `/api/equipment/` | Create equipment |
| GET | `/api/equipment/{id}/` | Get equipment details |
| PUT | `/api/equipment/{id}/` | Update equipment |
| DELETE | `/api/equipment/{id}/` | Delete equipment |
| GET | `/api/equipment/{id}/qr_code/` | Generate QR code |

### Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/` | List all employees |
| POST | `/api/employees/` | Create employee |
| GET | `/api/employees/{id}/` | Get employee details |
| PUT | `/api/employees/{id}/` | Update employee |
| DELETE | `/api/employees/{id}/` | Delete employee |

### Assignments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assignments/` | List all assignments |
| POST | `/api/assignments/` | Assign equipment |
| GET | `/api/assignments/{id}/` | Get assignment details |
| POST | `/api/assignments/{id}/return/` | Return equipment |
| GET | `/api/assignments/dashboard_stats/` | Get dashboard statistics |

### Maintenance

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/maintenance/` | List maintenance records |
| POST | `/api/maintenance/` | Create maintenance record |
| PUT | `/api/maintenance/{id}/` | Update maintenance record |

### Document Scanning

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scan-nakladnoy/` | Scan invoice with AI |

---

## Development

### Running Tests

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Code Style

- **Backend:** Follow PEP 8 standards
- **Frontend:** Use ESLint configuration

---

## Troubleshooting

### Database Migration Error

If you encounter "no such column" errors:

```bash
python manage.py migrate --run-syncdb
```

### CORS Error

Add your frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`:

```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Email Not Sending

1. Enable 2-Step Verification in Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character App Password in `.env`

---

## Docker Support

Run with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Django backend
- React frontend

---

## Security

- Never commit `.env` file to Git
- Use strong passwords for database and admin accounts
- Keep API keys confidential
- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` for production domains

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License

---

## Author

Hojiakbar Habibullayev

## Support

For issues and questions, please open an issue on GitHub.
