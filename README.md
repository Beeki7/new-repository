## Storebase POS – QR-based Retail Point of Sale

Storebase POS is a small, focused Point of Sale system for a women's clothing store.  
It provides product management with QR labels, QR-based checkout, inventory tracking, and basic sales analytics.

### 1. Project structure

At the top level:

- **`manage.py`**: Django management entry point (runserver, migrations, etc.).
- **`requirements.txt`**: Python dependencies (Django, QR code, Pillow).
- **`storebase_pos/`**: Django project configuration.
  - **`settings.py`**: Global settings (SQLite DB, apps, templates, static, media).
  - **`urls.py`**: Root URL routing; includes `pos` app URLs and media serving in development.
  - **`asgi.py` / `wsgi.py`**: Server entry points for ASGI/WSGI deployments.
- **`pos/`**: Main POS application.
  - **`models.py`**:
    - `Product`: product catalog; fields: `product_id`, `name`, `price`, `size`, `color`, `quantity`, `created_at`, `qr_code_image`.
      Automatically generates a PNG QR code containing `product_id` when created.
    - `Sale`: header for a sale (one row per completed checkout).
    - `SaleItem`: line items; fields: `sale`, `product`, `quantity`, `price`, `timestamp`.
  - **`views.py`**:
    - `dashboard`: analytics (daily/weekly/monthly/yearly revenue, best sellers, low stock).
    - `product_list`, `product_create`, `product_edit`, `product_delete`, `product_label`: product CRUD and printable QR label.
    - `checkout`: QR scanner checkout UI.
    - `api_get_product_by_code`: JSON lookup by `product_id` (used by QR scanner).
    - `api_complete_sale`: accepts a cart payload and creates `Sale` + `SaleItem` rows, updates inventory.
  - **`urls.py`**: URL patterns for products, checkout, APIs, and dashboard.
  - **`migrations/`**: Database migrations for the above models.
- **`templates/pos/`**: HTML templates using Tailwind CSS via CDN.
  - `base.html`: shared layout, navigation, mobile-friendly shell.
  - `dashboard.html`: analytics dashboard.
  - `product_list.html`: product listing and management.
  - `product_form.html`: add/edit product form.
  - `product_confirm_delete.html`: delete confirmation.
  - `product_label.html`: printable QR label page for each product.
  - `checkout.html`: QR scanner page, cart interface, and “Complete sale” flow.
- **`static/`**: Placeholder for static assets if you add custom CSS/JS later.
- **`media/`** (created at runtime): stores generated QR code images under `media/qrcodes/`.

### 2. Installation

#### 2.1. Clone and enter the project

```bash
cd /path/where/you/want/the/project
git clone <your-repo-url> storebase-pos   # or copy the folder into place
cd storebase-pos
```

If this is already on disk (e.g. via Cursor), just `cd` into the folder:

```bash
cd /Users/mirzied/storebase
```

#### 2.2. Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.3. Set up the SQLite database

```bash
python manage.py migrate
python manage.py createsuperuser  # optional, for Django admin
```

This creates `db.sqlite3` in the project root.

### 3. Running the development server

From the project root with the virtualenv activated:

```bash
python manage.py runserver
```

Then open the POS in your browser:

- POS UI: `http://127.0.0.1:8000/`
- Admin (optional): `http://127.0.0.1:8000/admin/`

### 4. Product management and QR label generation

1. **Open the products page**  
   Go to `http://127.0.0.1:8000/products/`.

2. **Create a new product**
   - Click **“New product”**.
   - Fill in:
     - **Product ID** (e.g. `DRESS-2024-0001`) – this is what the QR encodes.
     - **Name** (e.g. “Floral Summer Dress”).
     - **Price**, **Size**, **Color**, **Quantity**.
   - Click **“Save product”**.

3. **Automatic QR code**
   - When a product is saved the first time, the system generates a PNG QR code image containing `product_id`.
   - The image is stored at `media/qrcodes/<product_id>.png`.

4. **Print QR labels**
   - On the product list, click **“Label”** for a product.
   - A label page opens showing:
     - Product name, ID, size, color, price.
     - The generated QR code.
   - Click **“Print”** in the top-right of the page, then use your browser’s print dialogue to print onto label paper (or stickers).

### 5. QR-based checkout

1. **Open checkout page**  
   Go to `http://127.0.0.1:8000/checkout/` on a device with a camera (laptop, tablet, or phone).

2. **Allow camera access**  
   - The browser will ask for permission to use the camera.
   - Grant access; the live preview appears inside the **“Scan items”** box.

3. **Scan product QR codes**
   - Point the camera at a product QR label.
   - When the QR code (containing `product_id`) is detected:
     - The frontend calls `/api/product/<product_id>/`.
     - The product is added to the cart on the right.
   - Scan the same product multiple times to add multiple units, or adjust quantities using `+` / `–` in the cart.

4. **Cart operations**
   - **Increase/Decrease quantity**: use `+` and `–` buttons for each line.
   - **Remove item**: click the small `x`.
   - **Clear cart**: click **“Clear cart”** above the cart list.

5. **Complete the sale**
   - When the cart is ready, click **“Complete sale”**.
   - The browser sends a JSON payload to `/api/complete-sale/`:
     - `items: [{ product_id, quantity }, ...]`
   - On the server:
     - A `Sale` record is created.
     - One `SaleItem` is created per cart item with:
       - `sale_id` (via FK to `Sale`),
       - `product_id` (via FK to `Product`),
       - `quantity`,
       - `price` (snapshot of current product price),
       - `timestamp`.
     - Product `quantity` is reduced by the sold amount.
     - If stock is insufficient, the sale is rejected with a clear error message.
   - On success, the cart is cleared and a confirmation is shown (e.g. `Sale #5 completed.`).

### 6. Inventory management

- **Automatic stock reduction**:  
  Every successful sale decrements `Product.quantity` for each item.

- **Remaining stock display**:  
  The products page (`/products/`) shows the current stock level for each item with color-coded badges:
  - Green: healthy stock.
  - Amber: low stock (≤ 5 units by default).
  - Red: out of stock (0 units).

- **Low stock alerts in dashboard**:  
  The dashboard (`/`) lists all products where `quantity` is below or equal to the low-stock threshold (5 by default).

### 7. Analytics dashboard

The dashboard (`/`) shows key sales metrics:

- **Daily revenue**: sum of `SaleItem.price * SaleItem.quantity` for sales since midnight.
- **Weekly revenue**: last 7 days.
- **Monthly revenue**: last 30 days.
- **Yearly revenue**: last 365 days.
- **Total products sold**: sum of `SaleItem.quantity` across all time.
- **Best selling products**:
  - Aggregated by product.
  - Sorted by total units sold (top 10 displayed).
- **Low stock alerts**:
  - All products with stock ≤ 5 units.
  - Highlighted rows for quick re-order decisions.
- **Daily revenue chart (last 14 days)**:
  - Simple bar-style visual built with Tailwind utility classes.

All analytics use Django ORM aggregations over the `SaleItem` table.

### 8. Printing labels

- Use the **“Label”** link on the product list to open the label view.
- The page has a simplified layout for printing:
  - The header/navigation is hidden in print mode.
  - The main content is a compact card suitable for sticker/label paper.
- Use your browser’s **Print** menu or `Ctrl/Cmd + P`, then choose:
  - The correct printer.
  - Paper size matching your labels.
  - “Background graphics” if you want QR code edges very crisp (optional).

### 9. Starting POS operations (end-to-end)

1. **Set up environment**
   - Create and activate the virtualenv.
   - Install dependencies.
   - Run migrations.

2. **Create products**
   - Navigate to `/products/`.
   - Add all your store’s items with meaningful `product_id` values.

3. **Print and attach labels**
   - For each product, open **“Label”** and print.
   - Attach labels to physical items (or hang tags).

4. **Use checkout in the store**
   - Open `/checkout/` on a tablet/laptop at the register.
   - Keep the page open during the day.

5. **Perform sales**
   - Scan each item’s QR at checkout.
   - Adjust quantities if necessary.
   - Click **“Complete sale”** to finalize.

6. **Monitor inventory and performance**
   - Use `/` (dashboard) daily or weekly to:
     - See revenue summaries.
     - Identify best-selling products.
     - Spot low stock items before they run out.

### 10. Notes on scaling to multiple shops

- **Database**: replace SQLite with PostgreSQL or MySQL when you need multi-store or cloud deployment.
- **Multi-store support**: add a `Store` model and attach products and sales to a store via foreign keys.
- **Authentication**: enable per-user logins with Django’s auth system and restrict actions based on roles (cashier, manager, admin).
- **Deployment**: run behind a production-grade WSGI/ASGI server (e.g. gunicorn + nginx) and use HTTPS, especially for in-store tablets.

This codebase is intentionally minimal and readable so it can be extended as your requirements grow.

