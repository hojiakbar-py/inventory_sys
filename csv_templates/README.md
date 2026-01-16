# CSV Import Shablonlari

Bu papkada CSV import uchun shablon fayllar mavjud.

## 📋 Equipment (Qurilmalar) Import

**Fayl:** `equipment_template.csv`

### Majburiy maydonlar:
- `inventory_number` - Inventar raqami (Noyob bo'lishi kerak, misol: INV-001, EQ-2024-001)
- `name` - Qurilma nomi
- `purchase_price` - Xarid narxi (raqam, misol: 15000000)
- `depreciation_rate` - Amortizatsiya stavkasi (0-100 orasida, misol: 20)

**Eslatma:** Agar `serial_number` berilmasa, avtomatik ravishda `SN-{inventory_number}` shaklida yaratiladi.

### Ixtiyoriy maydonlar:
- `category` - Kategoriya (masalan: Noutbuk, Printer, Monitor)
- `manufacturer` - Ishlab chiqaruvchi (masalan: Dell, HP, Samsung)
- `model` - Model nomi
- `serial_number` - Seriya raqami
- `purchase_date` - Xarid sanasi (YYYY-MM-DD formatida, misol: 2024-01-15)
- `warranty_expiry` - Kafolat muddati (YYYY-MM-DD formatida)
- `status` - Holati (WORKING, MAINTENANCE, RETIRED)
- `location` - Joylashuv
- `description` - Tavsif

### Status qiymatlari:
- `WORKING` - Ishlayapti
- `MAINTENANCE` - Ta'mirda
- `RETIRED` - Ishdan chiqqan

### Misol:
```csv
inventory_number,name,category,manufacturer,model,purchase_date,purchase_price,depreciation_rate
INV-001,Dell Latitude 5520,Noutbuk,Dell,Latitude 5520,2024-01-15,15000000,20
```

---

## 👥 Employees (Hodimlar) Import

**Fayl:** `employees_template.csv`

### Majburiy maydonlar:
- `employee_id` - Hodim ID (Noyob bo'lishi kerak, misol: EMP001, E-2024-001)
- `first_name` - Ism
- `last_name` - Familiya
- `position` - Lavozim

**Eslatma:** Agar `hire_date` berilmasa, bugungi sana avtomatik qo'llaniladi.

### Ixtiyoriy maydonlar:
- `department` - Bo'lim nomi
- `email` - Email manzil (to'g'ri formatda: user@company.uz)
- `phone` - Telefon raqam (+998XXXXXXXXX formatida)
- `hire_date` - Ishga kirgan sana (YYYY-MM-DD formatida)

### Email format:
- To'g'ri: `alisher@company.uz`
- Noto'g'ri: `alisher` yoki `alisher@`

### Telefon format:
- To'g'ri: `+998901234567`
- To'g'ri: `998901234567`
- To'g'ri: `901234567`
- Noto'g'ri: `+99890123` (qisqa)

### Misol:
```csv
employee_id,first_name,last_name,position,department,email,phone,hire_date
EMP001,Alisher,Rahimov,Senior Developer,IT Bo'lim,alisher@company.uz,+998901234567,2023-01-10
```

---

## 📝 Import qilish qoidalari

### 1. Fayl formati:
- ✅ CSV fayl (`.csv` kengaytmasi)
- ✅ UTF-8 kodlash
- ✅ Maksimal hajm: 5MB
- ✅ Birinchi qator - ustun nomlari (header)

### 2. Ma'lumot formati:
- Sanalar: `YYYY-MM-DD` (misol: 2024-01-15)
- Raqamlar: Vergulsiz (15000000, 20.5)
- Matn: Qo'shtirnoqda agar vergul bor bo'lsa ("IT Bo'lim, 3-xona")

### 3. Xatolarni tekshirish:
- Frontend: Fayl turi va hajmini tekshiradi
- Backend: Har bir qatorni validatsiya qiladi
- Xatolar: Aniq xabar bilan ko'rsatiladi

### 4. Import jarayoni:
1. CSV faylni yuklab oling
2. Ma'lumotlarni to'ldiring
3. "Qurilmalar" yoki "Hodimlar" sahifasiga o'ting
4. "Import CSV" tugmasini bosing
5. Faylni tanlang va yuklang
6. Natijalarni ko'ring (muvaffaqiyatli/xato)

---

## ⚠️ Muhim eslatmalar

1. **Inventar raqam (Equipment):**
   - Noyob bo'lishi kerak (takrorlanmasligi shart)
   - Har qanday format qabul qilinadi
   - Misol: INV-001, EQ-2024-001, ASSET-123

2. **Hodim ID (Employee):**
   - Noyob bo'lishi kerak (takrorlanmasligi shart)
   - Har qanday format qabul qilinadi
   - Misol: EMP001, E-2024-001, STAFF-A001

3. **Email:**
   - To'g'ri email formatida bo'lishi kerak
   - Takrorlanmasligi kerak (har bir hodim uchun)

4. **Telefon:**
   - O'zbekiston raqami formatida
   - +998 yoki 998 bilan boshlanishi mumkin
   - 9 raqam (998 dan keyin)

5. **Sanalar:**
   - Faqat YYYY-MM-DD formatida
   - Kelajakdagi sanalar: Kafolat muddati uchun qabul qilinadi
   - O'tmishdagi sanalar: Xarid sanasi, Ishga kirgan sana uchun

---

## 🔍 Xatolarni tuzatish

Agar import xato bersa:

1. **"Bu inventar raqam/hodim ID allaqachon mavjud"**
   - To'g'rilash: Noyob raqam/ID ishlating

2. **"Email formatida xatolik"**
   - To'g'rilash: `user@company.uz` formatida yozing

3. **"Telefon raqami formatida xatolik"**
   - To'g'rilash: `+998901234567` formatida yozing

4. **"Fayl hajmi katta"**
   - To'g'rilash: Faylni kichikroq qismlarga bo'ling (5MB dan kam)

---

## 📞 Yordam

Agar qo'shimcha savollar bo'lsa, IT bo'limiga murojaat qiling.

**Yaratilgan:** 2026-01-05
**Versiya:** 1.0
