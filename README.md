## Storebase POS – QR asosidagi savdo tizimi

Storebase POS – ayollar kiyimlari do'koni uchun mo'ljallangan sodda, lekin kuchli savdo (POS) tizimi.  
Tizim mahsulotlarni boshqarish, QR yorliqlar, QR orqali savdo, ombor nazorati va savdo hisobotlarini taqdim etadi. Butun interfeys **o'zbek tilida** va valyuta **so'm (UZS)** ko'rinishida.

### 1. Project structure

Asosiy papkalar:

- **`manage.py`**: Django buyruqlari (runserver, migrate va hokazo) uchun kirish nuqtasi.
- **`requirements.txt`**: Python kutubxonalari (Django, QR code, Pillow).
- **`storebase_pos/`**: Django loyihasi konfiguratsiyasi.
  - **`settings.py`**: Umumiy sozlamalar (SQLite ma'lumotlar bazasi, ilovalar, shablonlar, static/media, til `uz`, vaqt mintaqasi `Asia/Tashkent`).
  - **`urls.py`**: Asosiy marshrutlash, `pos` ilovasining URL-larini o'z ichiga oladi.
  - **`asgi.py` / `wsgi.py`**: ASGI/WSGI serverlari uchun kirish nuqtalari.
- **`pos/`**: Asosiy POS ilovasi.
  - **`models.py`**:
    - `Product`: katalog modeli; maydonlar:
      - `id` (avtomatik),
      - `product_id` (QR ichiga yoziladigan identifikator),
      - `name`, `price`, `size`, `color`, `quantity`, `created_at`,
      - `qr_code` (yaratilgan PNG faylga yo'l).
    - `Sale`: bitta savdo uchun sarlavha; maydonlar:
      - `id`,
      - `created_at`,
      - `total_amount` (shu savdo bo'yicha umumiy summa).
    - `SaleItem`: savdo satrlari; maydonlar:
      - `sale` (FK → `Sale`),
      - `product` (FK → `Product`),
      - `quantity`,
      - `price`,
      - `timestamp`.
  - **`views.py`**:
    - `dashboard`: Boshqaruv paneli, quyidagilarni hisoblaydi: bugungi/haftalik/oylik/yillik savdo, eng ko'p sotilgan mahsulotlar, kam qolgan mahsulotlar, kunlik savdo grafigi.
    - `product_list`, `product_create`, `product_edit`, `product_delete`, `product_label`: mahsulotlar ro'yxati, qo'shish/tahrirlash/o'chirish, QR yorliq chiqarish.
    - `inventory`: ombordagi mahsulotlar sahifasi.
    - `checkout`: QR skaner asosidagi POS savdo sahifasi.
    - API'lar:
      - `api_product_detail` – `/api/product/<product_id>` uchun, mahsulot ma'lumotlarini qaytaradi.
      - `api_cart_add` – `/api/cart/add` uchun, POST `{product_id}` qabul qiladi va savatchaga qo'shish uchun mahsulot ma'lumotini qaytaradi.
      - `api_sale_complete` – `/api/sale/complete` uchun, POST `{items: [...]}` qabul qiladi, `Sale` + `SaleItem` yozuvlari yaratadi, `total_amount` maydonini to'ldiradi va ombor qoldig'ini kamaytiradi.
  - **`urls.py`**: Barcha yuqoridagi sahifalar va API yo'llari:
    - `/` – Boshqaruv paneli,
    - `/mahsulotlar/` – mahsulotlar,
    - `/ombor/` – ombor,
    - `/savdo/` – QR skaner POS sahifasi,
    - `/api/product/<product_id>`, `/api/cart/add`, `/api/sale/complete`.
  - **`admin.py`**:
    - `ProductAdmin`: qidiruv (nomi, product_id), o'lcham/rang bo'yicha filter, ombordagi miqdorni rang bilan ko'rsatish (kam qoldi va tugagan holatlari).
    - `SaleAdmin`: savdolar ro'yxati, ichida `SaleItem` inline ko'rinadi.
    - `SaleItemAdmin`: satrlar bo'yicha alohida ko'rinish.
  - **`templatetags/currency.py`**:
    - `uzs` filtri: `150000` → `150 000 UZS` ko'rinishiga keltiradi.
  - **`migrations/`**: ma'lumotlar bazasi migratsiyalari.
- **`templates/pos/`**: TailwindCSS asosidagi HTML shablonlari (hammasi o'zbek tilida).
  - `base.html`: umumiy skelet, navigatsiya: **Boshqaruv paneli**, **Mahsulotlar**, **Ombor**, **Savdo (QR)**.
  - `dashboard.html`: savdo statistikasi va Chart.js grafigi.
  - `product_list.html`: mahsulotlar ro'yxati, UZS ko'rinishida narx, "KAM QOLDI" belgilari.
  - `product_form.html`: mahsulot qo'shish/tahrirlash formasi.
  - `product_confirm_delete.html`: o'chirishni tasdiqlash.
  - `product_label.html`: bir sahifaga bir nechta QR yorliqlar chiqarish uchun sahifa.
  - `inventory.html`: ombor sahifasi (nomi, o'lcham, rang, narx, qoldiq).
  - `checkout.html`: QR skaner POS sahifasi, savatcha va "Savdoni yakunlash" tugmasi.
- **`static/`**: kerak bo'lsa qo'shimcha CSS/JS uchun.
- **`media/`**: ish vaqtida avtomatik yaratiladi, `qrcodes/` ichida QR rasmlari saqlanadi.

### 2. Installation

#### 2.1. Loyihani papkaga joylashtirish

```bash
cd /path/where/you/want/the/project
git clone <your-repo-url> storebase-pos   # or copy the folder into place
cd storebase-pos
```

Agar loyiha allaqachon kompyuteringizda bo'lsa (masalan, Cursor orqali), shu papkaga kiring:

```bash
cd /Users/mirzied/storebase
```

#### 2.2. Virtual muhit yaratish va kutubxonalarni o'rnatish

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.3. SQLite ma'lumotlar bazasini sozlash

```bash
python manage.py migrate
python manage.py createsuperuser  # optional, for Django admin
```

Bu amallar loyihaning ildizida `db.sqlite3` faylini yaratadi.

### 3. Serverni ishga tushirish

From the project root with the virtualenv activated:

```bash
python manage.py runserver
```

Keyin brauzerda quyidagilarni oching:

- POS interfeysi: `http://127.0.0.1:8000/`
- Admin (ixtiyoriy): `http://127.0.0.1:8000/admin/`

### 4. Mahsulot qo'shish va QR yorliq yaratish

1. **Mahsulotlar sahifasini ochish**  
   `http://127.0.0.1:8000/mahsulotlar/`

2. **Yangi mahsulot qo'shish**
   - Yuqoridagi **“Mahsulot qo'shish”** tugmasini bosing.
   - Quyidagi maydonlarni to'ldiring:
     - **Mahsulot ID** (masalan, `DRESS-2024-0001`) – aynan shu qiymat QR kodga yoziladi.
     - **Mahsulot nomi** (masalan, “Yozgi gulzor ko'ylak”).
     - **Narx (UZS)**, **O'lcham**, **Rang**, **Ombordagi miqdor**.
   - **“Saqlash”** tugmasini bosing.

3. **Avtomatik QR kod yaratish**
   - Mahsulot birinchi marta saqlanganda, tizim `product_id` bo'yicha PNG formatdagi QR rasm yaratadi.
   - Rasm `media/qrcodes/<product_id>.png` fayliga saqlanadi va `qr_code` maydoni orqali bog'lanadi.

4. **QR yorliqlarni chop etish**
   - Mahsulotlar ro'yxatida kerakli mahsulot yonidagi **“Yorliq”** tugmasini bosing.
   - `product_label.html` sahifasi ochiladi:
     - Har bir kichik blokda mahsulot nomi, o'lcham/rang, narx (UZS) va QR kod bo'ladi.
     - Bir sahifada bir nechta yorliq (grid tarzida) ko'rsatiladi.
   - Yuqoridagi **“Chop etish”** tugmasini bosing va brauzeringizning chop etish oynasidan foydalanib, yorliq/stiker qog'oziga chiqarib oling.

### 5. QR skaner asosidagi POS savdo

1. **Savdo sahifasini ochish**  
   `http://127.0.0.1:8000/savdo/` manzilini kamera mavjud qurilmada (noutbuk, planshet, telefon) oching.

2. **Kameraga ruxsat berish**  
   - Brauzer kamera uchun ruxsat so'raydi.
   - Ruxsat bering; sahifadagi **“QR skaner”** oynasida jonli video chiqadi.

3. **Mahsulot QR kodini skanerlash**
   - Kamerani yorliqqa qarating.
   - QR kod ichidagi `product_id` o'qilgach, frontend `/api/cart/add` API'iga:
     ```json
     { "product_id": "<QR dan o'qilgan qiymat>" }
     ```
     jo'natadi.
   - Server mahsulotni topib, JSON qaytaradi, frontend esa savatchaga **yangi satr qo'shadi yoki miqdorni oshiradi**.
   - Bir xil QR kodni qayta-qayta skanerlash – o'sha mahsulot miqdorini oshiradi (yangi satr emas).
   - Juda qisqa vaqtda bir necha marta o'qilganda tizim "dublikat kadr"larni e'tiborsiz qoldiradi (tez-tez bir kadrda qayta o'qishdan himoya).

4. **Savatcha funksiyalari**
   - Har bir satrda ko'rsatiladi:
     - Mahsulot nomi,
     - O'lcham, rang,
     - Miqdor,
     - Satr bo'yicha summa (UZS).
   - Tugmalar:
     - **`+`** – miqdorni oshirish.
     - **`-`** – miqdorni kamaytirish (0 bo'lsa satr o'chadi).
     - **“O'chirish”** – mahsulotni savatchadan butunlay olib tashlash.
     - **“Savatchani tozalash”** – barcha mahsulotlarni o'chirish.
   - Pastda:
     - **“Jami mahsulotlar soni”**,
     - **“Jami summa”** – `150000` → `150 000 UZS` tarzida formatlangan.

5. **Savdoni yakunlash**
   - **“Savdoni yakunlash”** tugmasini bosing.
   - Frontend `/api/sale/complete` ga quyidagi JSONni yuboradi:
     ```json
     {
       "items": [
         { "product_id": "DRESS-2024-0001", "quantity": 2 },
         { "product_id": "SKIRT-2024-0005", "quantity": 1 }
       ]
     }
     ```
   - Backend:
     - Yangi `Sale` yozuvini yaratadi.
     - Har bir mahsulot uchun `SaleItem` qo'shadi (`quantity`, `price`, `timestamp`).
     - Har bir mahsulotning `quantity` maydonini kamaytiradi.
     - Umumiy summani hisoblab, `Sale.total_amount` maydoniga yozadi.
     - Omborda mahsulot yetarli bo'lmasa, tegishli xabar (`"... uchun omborda yetarli mahsulot yo'q"`) bilan xatolik qaytaradi.
   - Muvaffaqiyatli holatda:
     - Savatcha tozalanadi.
     - Ekranda `Savdo #N yakunlandi. Umumiy summa: 150 000 UZS.` kabi xabar chiqadi.

### 6. Ombor boshqaruvi

- Har bir muvaffaqiyatli savdodan so'ng `Product.quantity` kamayadi.
- **Ombor sahifasi** (`/ombor/`):
  - Mahsulot nomi, o'lcham, rang, narx (UZS), qoldiq.
  - Qoldiq bo'yicha rangli belgi:
    - Yashil – yetarli zaxira.
    - Sariq – `<= 5` dona (ustida "KAM QOLDI" yozuvi).
    - Qizil – omborda qolmagan (`0`).
- **Boshqaruv paneli** (`/`):
  - Kam qolgan mahsulotlar alohida jadvalda ko'rsatiladi.

### 7. Hisobotlar va boshqaruv paneli

Bosh sahifa (`/`) quyidagilarni ko'rsatadi:

- **Bugungi savdo** – 00:00 dan hozirgacha bo'lgan tushum.
- **Haftalik savdo** – oxirgi 7 kun.
- **Oylik savdo** – oxirgi 30 kun.
- **Yillik savdo** – oxirgi 365 kun.
- **Umumiy tushum** – yillik savdoga teng.
- **Sotilgan mahsulotlar soni** – barcha `SaleItem.quantity` yig'indisi.
- **Eng ko'p sotilgan mahsulotlar** – "Top 10" ro'yxati.
- **Kam qolgan mahsulotlar** – `quantity <= 5`.
- **Chart.js grafigi** – oxirgi 14 kunlik kunlik savdo (UZS) bo'yicha diagramma.

### 8. Yorliqlarni chop etish

- Mahsulotlar sahifasida **“Yorliq”** tugmasini bosing.
- Ochilgan sahifada bir nechta bir xil yorliqlar grid tarzida ko'rinadi:
  - Mahsulot nomi,
  - O'lcham va rang,
  - Narx (UZS),
  - QR kod.
- **“Chop etish”** tugmasi orqali brauzerning chop etish oynasidan foydalaning:
  - Printerni tanlang.
  - Yorliq qog'oziga mos sahifa hajmini tanlang.
  - Kerak bo'lsa, "Background graphics" (fon grafika) ni yoqing.

### 9. POSni kundalik ishlatish (qadam-baqadam)

1. **Muhitni tayyorlash**
   - Virtual muhit yaratish.
   - `requirements.txt` bo'yicha kutubxonalarni o'rnatish.
   - `python manage.py migrate` bilan migratsiyalarni ishlatish.

2. **Mahsulotlarni kiritish**
   - `/mahsulotlar/` sahifasiga kiring.
   - Har bir mahsulot uchun **“Mahsulot qo'shish”** tugmasidan foydalaning.

3. **Yorliqlarni chop etish va yopishtirish**
   - Har bir mahsulot uchun **“Yorliq”** sahifasidan kerakli yorliqlarni chop eting.
   - Yorliqlarni kiyimlarga yoki teg'ga yopishtiring.

4. **Do'konda savdo qilish**
   - Kassadagi qurilmada `/savdo/` sahifasini oching va kun davomida ochiq qoldiring.
   - Xaridor kelganda, mahsulotlarning QR yorliqlarini ketma-ket skaner qiling.

5. **Savdoni yakunlash**
   - Savatchadagi miqdorlarni tekshiring, kerak bo'lsa qo'l bilan +/- tugmalari bilan sozlang.
   - **“Savdoni yakunlash”** tugmasini bosing.

6. **Ombor va hisobotlarni ko'rish**
   - `/ombor/` – ombordagi qoldiqlarni tez ko'rish.
   - `/` – savdo hisobotlari va eng ko'p sotilgan mahsulotlarni tahlil qilish.


### 10. Bir nechta do'konlarga kengaytirish bo'yicha eslatmalar

- **Database**: replace SQLite with PostgreSQL or MySQL when you need multi-store or cloud deployment.
- **Multi-store support**: add a `Store` model and attach products and sales to a store via foreign keys.
- **Authentication**: enable per-user logins with Django’s auth system and restrict actions based on roles (cashier, manager, admin).
- **Deployment**: run behind a production-grade WSGI/ASGI server (e.g. gunicorn + nginx) and use HTTPS, especially for in-store tablets.

Kod bazasi ataylab sodda va tushunarli yozilgan, shuning uchun keyinchalik bir nechta filiallar, qo'shimcha rollar (kassir, menejer, admin) va boshqa modullarni qo'shish oson bo'ladi.


