O‘ZBEKISTON RESPUBLIKASI OLIY TAʼLIM, FAN VA INNOVATSIYALAR VAZIRLIGI
"TOSHKENT IRRIGATSIYA VA QISHLOQ XO‘JALIGI MEXANIZATSIYALASH MUHANDISLARI INISTITUTI" MILLIY TADQIQOT UNIVERSITETI
“Ekologiya va huquq” fakulteti

INDIVIDUAL
LOYIHA

Mavzu: “Inventory System” axborot-tahlil tizimi – korporativ aktivlarni boshqarishda raqamli transformatsiya va sun'iy intellekt integratsiyasi

    Dasturiy injinering 313 – guruh talabasi
Topshirdi:	     						         Hojiakbar Habibullayev
                                     




Toshkent–2026 
MUNDARIJA
KIRISH	4
1-BOB. LOYIHA G'OYASI VA TALABLARNING TIZIMLI TAHLILI	6
1.1. Mavzu dolzarbligi va muammo qo'yilishi	6
1.2. Loyiha maqsadi va strategik vazifalar	8
1.3. Asosiy foydalanuvchi rollari: Huquqlar matritsasi	10
1.4. Funktsional talablar spetsifikatsiyasi	13
1.5. Nofunktsional talablar va sifat atributlari	16
1.6. Bozordagi analoglar tahlili (SWOT)	18
1.7. Foydalanish ssenariylari (UML Use-Case)	20
2-BOB. TIZIM ARXITEKTURASI VA TEXNOLOGIK STEK	23
2.1. Ko'p qatlamli (Clean Architecture) yondashuv	23
2.2. Backend: Django ekotizimi va Service Layer patterni	26
2.3. Frontend: React, Virtual DOM va State Management	29
2.4. Ma'lumotlar bazasi optimizatsiyasi: PostgreSQL, JSONB, Indekslar	32
2.5. Ma'lumotlar almashinuvi: REST API va Serializatsiya	35
2.6. DevOps infratuzilmasi: Docker konteynerizatsiyasi	37
2.7. Tashqi integratsiyalar: Google Gemini AI va SMTP	40
3-BOB. MA'LUMOTLAR MODELI VA BAZA TUZILMASI	42
3.1. Tashkiliy tuzilma: Filial va Bo'lim ierarxiyasi	42
3.2. HR moduli: Xodimlar va raqamli identifikatsiya (QR)	45
3.3. Aktivlar moduli: Uskuna, Kategoriya va Xususiyatlar	47
3.4. Jarayonlar moduli: Biriktirish (Assignment) va Qaytarish	50
3.5. Audit va Tekshiruv: Inventarizatsiya va Loglar	53
3.6. ER Diagramma va relyatsion bog'liqliklar tahlili	55
4-BOB. FUNKTSIONAL MODULLAR VA BIZNES MANTIQ	57
4.1. Autentifikatsiya (JWT) va Sessiya boshqaruvi	57
4.2. Uskunalar bilan ishlash (CRUD) va hayot sikli	60
4.3. Biznes jarayoni: Uskunani biriktirish tranzaksiyasi	63
4.4. AI Moduli: Hujjatlarni intellektual skanerlash	66
4.5. Ma'lumotlar importi va eksporti (CSV/Excel)	69
4.6. Admin panel va kontent boshqaruvi	72
4.7. Qidiruv va Filtrlar tizimi	75
5-BOB. ALGORITMLAR VA MATEMATIK MODELLAR	78
5.1. Amortizatsiya (Eskirish) hisoblash algoritmi	78
5.2. Kafolat muddati va statuslarni avtomatik aniqlash	80
5.3. Ierarxik daraxt algoritmlari (Recursion)	82
5.4. Xavfsiz identifikatorlar va QR kod generatsiyasi	84
6-BOB. FOYDALANUVCHI INTERFEYSI VA UX	86
6.1. Web interfeys dizayn tamoyillari (Material UI)	86
6.2. Dashboard va vizualizatsiya komponentlari	89
6.3. Mobil moslashuvchanlik va PWA	91
7-BOB. TESTLASH, SIFAT NAZORATI VA DEBUGGING	93
7.1. Unit testlar: Izolyatsiya qilingan tekshiruvlar	93
7.2. Integratsion testlar: API va Baza hamkorligi	95
7.3. Manual va Yuklama (Load) testlash	97
8-BOB. XAVFSIZLIK VA AXBOROT MUHOFAZASI	99
8.1. Autentifikatsiya xavfsizligi (OTP, Password Hashing)	99
8.2. Tarmoq xavfsizligi (CORS, SSL/TLS, Rate Limiting)	101
8.3. Audit va Monitoring (Logging)	103
9-BOB. DEPLOY VA EKSPLUATATSIYA	105
9.1. Docker Compose orkestratsiyasi	105
9.2. Nginx konfiguratsiyasi va statik fayllar	107
9.3. Zaxira nusxalash (Backup) strategiyalari	109
XULOSA	111
FOYDALANILGAN ADABIYOTLAR	113
ILOVALAR	114
 
KIRISH

**Mavzuning dolzarbligi:**
XXI asr – raqamli texnologiyalar asri. O'zbekiston Respublikasi Prezidentining "Raqamli O'zbekiston — 2030" strategiyasini tasdiqlash va uni samarali amalga oshirish chora-tadbirlari to'g'risidagi farmonida iqtisodiyotning barcha tarmoqlarini raqamlashtirish, ish jarayonlarini avtomatlashtirish va inson omilini kamaytirish ustuvor vazifa qilib belgilangan.
Har qanday yirik korxona, universitet yoki davlat tashkilotining faoliyati uning moddiy-texnik bazasiga tayanadi. Minglab kompyuterlar, mebellar, laboratoriya jihozlari va transport vositalari – bularning barchasi "aktivlar" deb ataladi. Afsuski, ko'plab tashkilotlarda bu aktivlarning hisobi hali ham an'anaviy usullarda – qog'oz jurnallarda yoki lokal Excel fayllarda yuritilmoqda.

**Muammoning mohiyati:**
An'anaviy yondashuv quyidagi jiddiy muammolarni keltirib chiqaradi:
1.  **Ma'lumotlarning tarqoqligi:** Har bir bo'lim (masalan, IT, Xo'jalik bo'limi, Buxgalteriya) o'zining alohida hisobini yuritadi. Natijada, "Kimda qaysi noutbuk bor?" degan oddiy savolga javob topish uchun uch xil jurnalni solishtirishga to'g'ri keladi.
2.  **Inventarizatsiya murakkabligi:** Yillik yoppasiga tekshirish (reviziya) jarayoni haftalab, ba'zan oylab vaqt oladi. Minglab buyumlarni qo'lda sanash, inventar raqamlarini solishtirish jarayonida xatoliklar ehtimoli 30-40% ni tashkil etadi.
3.  **Tarixning yo'qolishi:** Uskuna necha marta ta'mirlangani, oldin kim tomonidan ishlatilgani, qachon sotib olingani haqidagi ma'lumotlar vaqt o'tishi bilan yo'qoladi.
4.  **O'g'rilik va talon-taroj:** Nazoratning sustligi tufayli qimmatbaho uskunalar yo'qolishi yoki shaxsiy maqsadlarda ishlatilishi holatlari uchraydi.

**Taklif etilayotgan yechim:**
"Inventory System" – bu korxona resurslarini boshqarishning (Enterprise Asset Management - EAM) zamonaviy, avtomatlashtirilgan tizimidir. Loyiha nafaqat hisob-kitobni yuritish, balki jarayonlarni aqlli boshqarish imkonini beradi.
Tizimning asosiy innovatsion jihatlari:
*   **QR-kod texnologiyasi:** Har bir buyumga unikal QR-kod yopishtiriladi. Uni oddiy smartfon orqali skanerlash orqali buyum haqidagi barcha ma'lumot (tarix, narx, mas'ul shaxs) bir soniyada ekranda paydo bo'ladi.
*   **Sun'iy Intellekt (AI):** Hujjatlarni (nakladnoy, schet-faktura) qo'lda kiritish o'rniga, ularni rasmga olib yuklash kifoya. Tizim Google Gemini AI yordamida rasmni tahlil qiladi va ma'lumotlarni avtomatik bazaga kiritadi.
*   **Bulutli texnologiyalar:** Tizim web-asosli bo'lib, unga dunyoning istalgan nuqtasidan, istalgan qurilmadan kirish mumkin.

1-BOB. LOYIHA G'OYASI VA TALABLARNING TIZIMLI TAHLILI

1.1. Mavzu dolzarbligi va muammo qo‘yilishi
Zamonaviy biznesda "Vaqt – bu pul" tamoyili amal qiladi. IT-infratuzilmani boshqarish bo'limi xodimlari o'z vaqtini qog'oz to'ldirishga emas, balki real muammolarni hal qilishga sarflashlari kerak.
Statistik ma'lumotlarga ko'ra, avtomatlashtirilmagan inventar tizimiga ega kompaniyalar yiliga o'z aktivlarining 5-7% ini yo'qotadilar. O'zbekiston sharoitida, bu milliardlab so'm zararni anglatishi mumkin.
Bundan tashqari, aktivlarning amortizatsiyasi (eskirishi) va kafolat muddatlarini kuzatib borish moliyaviy rejalashtirish uchun krit is ahamiyatga ega. "Inventory System" aynan shu bo'shliqni to'ldiradi.

1.2. Loyiha maqsadi va strategik vazifalar
**Loyiha maqsadi:** Korxona moddiy-texnik resurslarini hisobga olish, boshqarish va monitoring qilish jarayonlarini to'liq raqamlashtirish orqali ish samaradorligini oshirish va xarajatlarni kamaytirish.

**Strategik vazifalar:**
1.  **Yagona Axborot Mako'ni:** Barcha filiallar va bo'limlar uchun markazlashgan ma'lumotlar bazasini yaratish.
2.  **Jarayonlarni Optimallashtirish:** Uskunani biriktirish va qaytarish vaqtini 15 daqiqadan 2 daqiqagacha qisqartirish.
3.  **Shaffoflik:** Har bir aktivning "hayot yo'li"ni (Audit Trail) shakllantirish – qachon kelgan, kim ishlatgan, qachon ta'mirlangan.
4.  **Qaror qabul qilishni qo'llab-quvvatlash:** Rahbariyatga real vaqt rejimida statistik ma'lumotlar (Dashboard) taqdim etish.
5.  **Integratsiya:** Kelajakda 1C:Buxgalteriya va HR tizimlari bilan integratsiya qilish imkoniyatini yaratish.

1.3. Asosiy foydalanuvchi rollari: Huquqlar matritsasi
Tizimda xavfsizlik va ma'lumotlar yaxlitligini ta'minlash maqsadida qat'iy rollar tizimi (Role-Based Access Control) joriy etilgan.

| Rol | Ruxsat etilganamallar | Ruxsat etilmagan amallar |
| :--- | :--- | :--- |
| **Super Admin** | Tizimni to'liq boshqarish, barcha filiallarni ko'rish, foydalanuvchilarni yaratish/o'chirish, konfiguratsiyani o'zgartirish. | - |
| **Branch Manager** (Filial rahbari) | Faqat o'z filialidagi uskuna va xodimlarni boshqarish, hisobotlar olish. | Boshqa filial ma'lumotlarini o'zgartirish, tizim sozlamalari. |
| **Inventory Clerk** (Omborchi) | Uskuna qabul qilish, biriktirish, QR kod chop etish. | Xodimlarni o'chirish, filial ma'lumotlarini tahrirlash. |
| **IT Support** (Texnik) | Ta'mirlash (Maintenance) statuslarini o'zgartirish, nosozliklarni qayd etish. | Uskuna narxini o'zgartirish, yangi xodim qo'shish. |
| **Employee** (Xodim) | O'ziga biriktirilgan uskunalarni ko'rish, profilini QR kod orqali ulashish. | Boshqalarning uskunalarini ko'rish, hech qanday o'zgartirish kiritish. |

1.4. Funktsional talablar spetsifikatsiyasi
Tizim quyidagi funktsional modullardan iborat bo'lishi shart:
1.  **Aktivlar Boshqaruvi (Asset Management):**
    *   Yangi aktiv yaratish (Nom, Model, Seriya raqam, Narx).
    *   Aktivni tahrirlash va o'chirish (Soft delete - arxivlash).
    *   Kategoriyalarga ajratish (Daraxtsimon struktura).
    *   Rasmlar yuklash (Avtomatik o'lchamni o'zgartirish bilan).
2.  **Harakatlar Boshqaruvi (Operations):**
    *   Check-in/Check-out (Berish/Qaytarish).
    *   Inventarizatsiya (Rejali tekshiruv).
    *   Ta'mirlashga yuborish.
3.  **Hujjatlar va Hisobotlar:**
    *   Topshirish-qabul qilish dalolatnomasini PDF shaklda generatsiya qilish.
    *   Excel/CSV formatida eksport.
    *   QR kod stikerlarini chop etish (A4 formatda 24 ta yoki bitta).
4.  **AI Integratsiya (Smart Scan):**
    *   Kameradan olingan faktura rasmini tanib olish.
    *   JSON formatida ma'lumotlarni ajratib olish (OCR).

1.5. Nofunktsional talablar va sifat atributlari
*   **Ishlash tezligi (Performance):** 100 000 ta yozuv bo'lganda ham qidiruv natijalari 0.5 soniyadan kechikmasligi kerak.
*   **Ishonchlilik (Reliability):** Ma'lumotlar bazasi har kuni avtomatik zaxiralanadi (Backup).
*   **Xavfsizlik (Security):** Barcha parollar PBKDF2 bn xeshlangan. Sessiyalar JWT orqali himoyalangan.
*   **Moslashuvchanlik (Scalability):** Tizim Docker konteynerlarida ishlagani uchun, yuklama oshganda serverlarni ko'paytirish (Horizontal Scaling) oson.

2-BOB. TIZIM ARXITEKTURASI VA TEXNOLOGIK STEK

2.1. Ko'p qatlamli (Clean Architecture) yondashuv
Loyiha arxitekturasi "Separation of Concerns" (Mas'uliyatlarni ajratish) tamoyiliga asoslangan. Bu kodning o'qilishi, testlanishi va kelajakda o'zgartirilishini osonlashtiradi.
Qatlamlar:
1.  **Presentation Layer (Frontend):** React komponentlari. Faqat ma'lumotni ko'rsatish va foydalanuvchi harakatlarini qabul qilish uchun javobgar.
2.  **API Layer (Backend Views):** HTTP so'rovlarni qabul qilish, validatsiya va javob qaytarish.
3.  **Service Layer (Business Logic):** Asosiy mantiq shu yerda joylashgan (masalan, `EquipmentService`, `AssignmentService`). API qatlami ma'lumotni shu yerga uzatadi.
4.  **Data Access Layer (ORM):** Ma'lumotlar bazasi bilan to'g'ridan-to'g'ri ishlash (Django Models).

2.2. Backend: Django ekotizimi va Service Layer patterni
Backend **Python 3.12** va **Django 5.0** da yozilgan.
Nega Service Layer ishlatildi?
Odatda Django loyihalarida biznes mantiq `views.py` yoki `models.py` da yoziladi. Lekin loyiha kattalashgani sari bu fayllar "semirib" ketadi ("Fat Models, Thin Views" ham ba'zan yetarli emas).
Shuning uchun `services.py` moduli yaratildi. Masalan, yangi filial yaratish logikasi `BranchService.create_branch` metodida joylashgan. Bu metod:
-   Tranzaksiyani ochadi (`transaction.atomic()`).
-   Validatsiya qiladi (ota-filial o'ziga teng emasligi).
-   Filialni yaratadi.
-   Audit log yozadi.
-   Xatolik bo'lsa, barchasini bekor qiladi.

2.3. Frontend: React, Virtual DOM va State Management
Foydalanuvchi interfeysi **React 18** da yaratilgan.
Asosiy texnologiyalar:
-   **Vite:** Loyihani tezkor yig'ish (build) uchun.
-   **React Router:** Sahifalararo o'tish (SPA - Single Page Application).
-   **TanStack Query (React Query):** Server holatini (Server State) boshqarish, keshlash va avtomatik yangilash uchun.
-   **Tailwind CSS:** Tezkor va moslashuvchan stil berish uchun.

2.4. Ma'lumotlar bazasi optimizatsiyasi: PostgreSQL
Ma'lumotlar bazasi sifatida **PostgreSQL 16** tanlandi.
Optimizatsiya choralari:
1.  **Indekslash (Indexing):** Ko'p qidiriladigan ustunlar (`inventory_number`, `serial_number`, `status`) uchun `B-Tree` indekslar yaratilgan. Bu qidiruv tezligini 100 barobargacha oshiradi.
2.  **JSONB:** Uskunalarning texnik parametrlari (`specifications`) JSONB formatida saqlanadi. Bu bizga har xil turdagi uskunalar (stol, kompyuter, mashina) uchun alohida ustunlar ochmasdan, bitta umumiy strukturada ishlash imkonini beradi.
3.  **Constraints:** Baza darajasida cheklovlar qo'yilgan (masalan, `unique=True` inventar raqami uchun).

3-BOB. MA'LUMOTLAR MODELI VA BAZA TUZILMASI

3.1. Tashkiliy tuzilma: Filial va Bo'lim ierarxiyasi
Tashkiliy tuzilma rekursiv bog'liqlik asosida qurilgan.
**Branch (Filial) modeli:**
-   `id`: Unikal ID.
-   `parent_branch`: O'ziga o'zi bog'langan (Self-referential ForeignKey). Bu daraxtsimon ierarxiyani (Bosh ofis -> Viloyat -> Tuman) hosil qiladi.
-   `manager`: Filial rahbari (OneToOne Employee bilan).
**Department (Bo'lim) modeli:**
-   Branch bilan `ForeignKey` orqali bog'langan.

3.2. HR moduli: Xodimlar va raqamli identifikatsiya
**Employee (Xodim) modeli:**
Loyiha xodimlar haqida faqat inventarizatsiya uchun kerakli ma'lumotlarni saqlaydi.
Muhim maydonlar:
-   `user`: Django User modeli bilan bog'liqlik (tizimga kirish uchun).
-   `qr_code`: Xodimning shaxsiy QR kodi saqlanadigan maydon (ImageField).
-   `current_equipment_count`: Hisoblangan maydon (denormalization emas, property), xodimda nechta uskuna borligini qaytaradi.

3.3. Aktivlar moduli: Uskuna, Kategoriya va Xususiyatlar
**Equipment (Uskuna) modeli:** Tizimning markaziy modeli.
-   `category`: `EquipmentCategory` ga bog'langan.
-   `status`: Enum (AVAILABLE, ASSIGNED, MAINTENANCE, DECOMMISSIONED).
-   `condition`: Enum (NEW, GOOD, FAIR, POOR).
-   `purchase_price` va `current_value`: Moliyaviy hisob-kitob uchun. `current_value` har safar amortizatsiya hisoblanganida yangilanadi.

3.4. Jarayonlar moduli: Biriktirish (Assignment)
Bu model eng ko'p biznes mantiqni o'z ichiga oladi.
**Assignment modeli:**
-   `equipment` (ForeignKey).
-   `employee` (ForeignKey).
-   `assigned_date` (Sana).
-   `return_date` (Sana, null=True). Agar bu maydon bo'sh bo'lsa, demak uskuna hali ham xodimda.
-   `expected_return_date`: Qaytarilishi kutilayotgan sana (muddati o'tganligini aniqlash uchun).

4-BOB. FUNKTSIONAL MODULLAR VA BIZNES MANTIQ

4.1. Autentifikatsiya (JWT) va Sessiya boshqaruvi
Tizimga kirish `Simple JWT` kutubxonasi orqali amalga oshiriladi.
1.  Foydalanuvchi login/parol yuboradi.
2.  Server tekshiradi va `access` (5 daqiqa) hamda `refresh` (1 kun) tokenlarini qaytaradi.
3.  Frontend `access` tokenni har bir so'rovda Header da yuboradi: `Authorization: Bearer <token>`.
4.  Agar `access` token muddati tugasa, Frontend avtomatik ravishda `refresh` token yordamida yangi token oladi (Token Rotation).

4.3. Biznes jarayoni: Uskunani biriktirish tranzaksiyasi
`AssignmentService.assign_equipment` metodi quyidagi qat'iy ketma-ketlikni bajaradi:
1.  `equipment.status` tekshiriladi. Agar `AVAILABLE` bo'lmasa, `ValidationError` qaytariladi.
2.  Tranzaksiya ochiladi (`transaction.atomic`).
3.  Yangi `Assignment` obyekti yaratiladi.
4.  `equipment.status` -> `ASSIGNED` ga o'zgartiriladi.
5.  `AuditLog` ga yozuv kiritiladi: "Admin Xodim A ga Uskuna B ni biriktirdi".
6.  Tranzaksiya yopiladi.

4.6. Admin panel va kontent boshqaruvi
Djangoning standart admin paneli (`admin.py`) kuchli moslashtirilgan.
-   **List Display:** Ro'yxatda nafaqat nom, balki status (rangli), kategoriya va narx ko'rinadi.
-   **Filters:** O'ng tomonda status, kategoriya, filial bo'yicha qulay filtrlar.
-   **Search:** Bir vaqtning o'zida ism, inventar raqam va seriya raqami bo'yicha qidiruv.
-   **Readonly Fields:** Audit uchun `created_at` va `updated_at` maydonlari o'zgartirib bo'lmaydigan qilingan.

5-BOB. ALGORITMLAR VA MATEMATIK MODELLAR

5.1. Amortizatsiya (Eskirish) hisoblash algoritmi
`inventory/utils.py` faylida `calculate_depreciation` funksiyasi mavjud.
Formula (To'g'ri chiziqli usul):
`Eskirish = Xarid_narxi * (Eskirish_foizi / 100) * Yillar`
`Hozirgi_qiymat = Max(0, Xarid_narxi - Eskirish)`
Bu funksiya har safar uskuna ko'rilganda yoki hisobot olinganda dinamik ravishda ishlaydi.

5.3. Ierarxik daraxt algoritmlari (Recursion)
Filiallar daraxtini qurish uchun rekursiv `build_tree` funksiyasi ishlatilgan (`BranchService` da).
Algoritm:
1.  Bosh ofis (Root) olinadi.
2.  Uning bolalari (Children) qidiriladi.
3.  Har bir bola uchun funksiya o'zini o'zi chaqiradi.
Natijada Frontendga tayyor shajara (Nested JSON) uzatiladi.

6-BOB. FOYDALANUVCHI INTERFEYSI VA UX

6.1. Web interfeys dizayn tamoyillari
Interfeysda **"3-Click Rule"** (3 marta bosish qoidasi) amal qiladi. Har qanday ma'lumotga maksimum 3 ta harakat bilan yetib borish mumkin.
Ranglar psixologiyasi:
-   Yashil: Mavjud (Available).
-   Ko'k: Biriktirilgan (Assigned).
-   Sariq: Ta'mirda (Maintenance).
-   Qizil: Hisobdan chiqarilgan (Decommissioned).

7-BOB. TESTLASH VA SIFAT NAZORATI

7.1. Unit testlar
Loyiha uchun keng qamrovli unit testlar yozilgan (`tests/` papkasida).
Misol uchun `test_assignment_flow`:
-   Uskuna yaratish.
-   Xodim yaratish.
-   Biriktirishga urinish (Muvaffaqiyatli).
-   O'sha uskunani yana boshqaga biriktirishga urinish (Xatolik kutish).
Bu testlar CI/CD jarayonida avtomatik ishlaydi va kod buzilmasligini kafolatlaydi.

8-BOB. XAVFSIZLIK VA AXBOROT MUHOFAZASI

8.1. Autentifikatsiya xavfsizligi
-   **OTP (One-Time Password):** Parolni tiklash uchun 6 xonali tasodifiy kod (`secrets.randbelow`) generatsiya qilinadi va emailga yuboriladi. Kod 5 daqiqa amal qiladi.
-   **Throttling:** Login API ga bir daqiqada 5 martadan ortiq noto'g'ri urinish bo'lsa, IP vaqtincha bloklanadi.

8.3. Audit va Monitoring
Har bir o'zgarish (Create, Update, Delete) `AuditLog` jadvalida saqlanadi:
-   Kim qildi? (User).
-   Nima qildi? (Action).
-   Qachon? (Timestamp).
-   Eski qiymat va Yangi qiymat (JSON formatida).

9-BOB. DEPLOY VA EKSPLUATATSIYA

9.1. Docker Compose orkestratsiyasi
Ishlab chiqarish (Production) muhitida tizim `docker-compose.prod.yml` orqali ishga tushadi.
-   `web`: Gunicorn server (WSGI).
-   `db`: PostgreSQL (ma'lumotlar `volume` da saqlanadi).
-   `nginx`: Statik fayllarni va rasmlarni keshlash va tarqatish uchun.

9.3. Zaxira nusxalash (Backup)
Baza har kuni `pg_dump` yordamida SQL faylga aylantiriladi va arxivlanadi. Bu fayllar 30 kun saqlanadi va avtomatik o'chiriladi.

XULOSA

Ushbu bitiruv malakaaviy ishi doirasida yaratilgan "Inventory System" axborot tizimi korxonalarning moddiy-texnik resurslarini boshqarishdagi mavjud muammolarni to'liq hal etadi. Tizimning ilmiy yangiligi shundaki, u an'anaviy hisob-kitobni zamonaviy AI va QR texnologiyalari bilan birlashtiradi.
Amaliy ahamiyati shundan iboratki, tizim ochiq kodli (Open Source) texnologiyalarda qurilgan bo'lib, litsenziya to'lovlarini talab qilmaydi va O'zbekiston korxonalari uchun iqtisodiy jihatdan eng maqbul yechim hisoblanadi.

FOYDALANILGAN ADABIYOTLAR
1.  Django 5.0 Official Documentation. https://docs.djangoproject.com/
2.  "Clean Architecture in Python" - Leonardo Giordani.
3.  React 18 & TanStack Query Docs.
4.  PostgreSQL 16 Administration Guide.
5.  Google Gemini API References.

ILOVALAR

**Ilova A: API Endpointlar Xaritasi**
-   `GET /api/v1/statistics/dashboard/` - Bosh sahifa statistikasi.
-   `POST /api/v1/inventory/scan-invoice/` - AI orqali skanerlash.
-   `GET /api/v1/users/me/` - Profil.

**Ilova B: Tizimdan skrinshotlar**
*(Bu yerda dastur interfeysidan rasmlar joylanadi)*
