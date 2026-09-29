# Global Link Store 🛒 🇳🇵

[![Django](https://img.shields.io/badge/Django-6.0.5-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Celery](https://img.shields.io/badge/Celery-5.6.3-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-7.4-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![WeasyPrint](https://img.shields.io/badge/WeasyPrint-68.1-1B365D)](https://weasyprint.org/)
[![django-axes](https://img.shields.io/badge/django--axes-8.3.1-blue)](https://django-axes.readthedocs.io/)
[![WhiteNoise](https://img.shields.io/badge/WhiteNoise-6.12.0-yellow)](https://whitenoise.readthedocs.io/)

**Global Link Store** is a full-featured, enterprise-grade e-commerce platform engineered specifically for the Nepali electronics and consumer tech retail market. Built on **Django 6.0.5** and Python, it delivers a multi-dimensional variant and SKU inventory engine, hybrid session-to-user cart persistence, localized payment gateways (**eSewa v2** & **Khalti**), automated PDF invoice generation via **WeasyPrint**, background transactional email workflows powered by **Celery & Redis**, Google OAuth2 social authentication, brute-force defense with **django-axes**, and a custom staff management dashboard alongside Django's default admin.

---

## 📑 Table of Contents

1. [System Architecture & Tech Stack](#-system-architecture--tech-stack)
2. [Complete Feature Breakdown](#-complete-feature-breakdown)
   - [Storefront & Catalog](#1-storefront--product-catalog)
   - [Cart, Checkout & Local Payments](#2-cart-checkout--local-payment-gateways)
   - [Order Lifecycle & PDF Invoices](#3-order-lifecycle--pdf-invoicing)
   - [User Accounts & Authentication](#4-user-accounts--security)
   - [Staff Operations Dashboard (`/store-admin/`)](#5-staff-operations-dashboard-store-admin)
   - [Celery Asynchronous Tasks](#6-asynchronous-background-tasks-celery--redis)
   - [Technical & On-Page SEO](#7-technical--on-page-seo)
3. [Database Models & Schema Reference](#-database-models--schema-reference)
4. [Complete URL & Routing Map](#-complete-url--routing-map)
5. [Celery Tasks Reference](#-celery-tasks-reference)
6. [Project Directory Tree](#-project-directory-tree)
7. [Installation & Local Development](#-installation--local-development)
8. [Environment Variables Reference (`.env`)](#-environment-variables-reference-env)
9. [Payment Gateway Testing (eSewa & Khalti)](#-payment-gateway-testing-esewa--khalti)
10. [Staff Workflows & Management Guide](#-staff-workflows--management-guide)
11. [Production Deployment & cPanel Setup](#-production-deployment--cpanel-setup)
12. [License & Attribution](#-license--attribution)

---

## 🏗️ System Architecture & Tech Stack

```
                     ┌─────────────────────────────────────────┐
                     │            User / Browser               │
                     └────────────────────┬────────────────────┘
                                          │ HTTP/HTTPS
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │          Nginx / cPanel Apache          │
                     │  (Static/Media via WhiteNoise/Symlink)  │
                     └────────────────────┬────────────────────┘
                                          │ WSGI / Passenger
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │          Django Core Application        │
                     │  (Auth, Catalog, Cart, Checkout, Admin) │
                     └───────┬────────────────────┬────────────┘
                             │                    │
                Database Ops │                    │ Task Dispatch
                             ▼                    ▼
       ┌───────────────────────────────┐  ┌───────────────────────────────┐
       │     Database (SQLite/Postgres)│  │     Redis (Broker & Backend)  │
       └───────────────────────────────┘  └───────────────┬───────────────┘
                                                          │ Worker Queue
                                                          ▼
                                          ┌───────────────────────────────┐
                                          │    Celery Task Workers        │
                                          │ (Emails, Status Notifications)│
                                          └───────────────────────────────┘
```

| Layer | Component | Description |
| :--- | :--- | :--- |
| **Framework** | Django 6.0.5 | High-level Python web framework |
| **Runtime** | Python 3.11+ | Primary execution environment |
| **Async Queue** | Celery 5.6.3 | Distributed task queue for non-blocking I/O |
| **Task Broker** | Redis 7.4.0 | In-memory message broker & result backend |
| **PDF Generation** | WeasyPrint 68.1 | Renders CSS/HTML templates to vector PDF invoices |
| **Authentication** | Django Auth + Social Auth | Password auth + Google OAuth2 social pipeline |
| **Security** | django-axes 8.3.1 | Rate-limiting & brute-force IP lockout defense |
| **Static Storage** | WhiteNoise 6.12.0 | High-performance compressed static file handling |
| **Media Handling** | Pillow 12.2.0 | Image validation, resizing, and processing |
| **Local Payments** | eSewa ePay v2 + Khalti | Direct Nepali payment gateway integrations |

---

## 🌟 Complete Feature Breakdown

### 1. Storefront & Product Catalog
* **Hierarchical Category Tree**: Supports 3-tier deep navigation (Parent $\rightarrow$ Subcategory $\rightarrow$ Grandchild) rendered via responsive desktop mega-menus and mobile accordion drawers.
* **Multi-Dimensional Variants & SKUs**:
  * Product variant groups (e.g., *Color*, *RAM/Storage*, *Size*) with dynamic option choices.
  * Discrete `ProductSKU` instances tracking exact inventory quantities and individual price adjustments per combination.
* **Faceted Search & Catalog Filtering**:
  * Filter by category subtree, brand, price range slider, in-stock status, on-sale discount, and special product type badges (`featured`, `offer`, `new`).
  * Live filter tags (chips) with single-click dismiss and active state indicators.
* **Live Search Autocomplete**: Asynchronous navbar search querying product titles and brand names with instant dropdown previews.
* **Product Comparison Engine**:
  * Side-by-side comparison matrix for up to 3 products.
  * Compares pricing, stock, category, brand, and automatically aligns overlapping specification sections.
* **Verified Purchaser Reviews**:
  * 1 to 5 star rating submission with title and detailed feedback.
  * Verified Purchaser badge automatically granted if the logged-in user has a delivered order for that product.
  * Aggregated rating distribution bar charts (5★ down to 1★).
* **Interactive Hero Carousels & Banners**:
  * Left dual slider supporting both video background and image slides with custom target links.
  * Right promotional static banners (`right_top` and `right_bottom`).

### 2. Cart, Checkout & Local Payment Gateways
* **Hybrid Session/User Cart**:
  * Anonymous guest shoppers have their cart tracked by Django session keys.
  * When a guest registers, logs in, or signs in via Google OAuth2, the session cart automatically merges into their persistent database cart without losing items.
* **Smart Shipping Engine**:
  * **Kathmandu Valley**: Free delivery for orders $\ge$ Rs 5,000 (Rs 100 shipping fee if below threshold).
  * **Outside Kathmandu Valley**: Flat-rate Rs 200 delivery.
* **Local Payment Gateways**:
  1. **Cash on Delivery (COD)**: Instantly marks order as confirmed and reserves stock.
  2. **eSewa ePay v2**: Real-time HMAC-SHA256 signature calculation over transaction UUID, product code, and total amount; secure payload validation on callback.
  3. **Khalti v2**: Direct REST API initiation yielding payment `pidx`, with server-to-server transaction verification lookup.
* **Concurrency-Safe Stock Deduction**:
  * Stock is deducted using `select_for_update()` and database-level `F('stock') - quantity` expressions within atomic database transactions, preventing negative stock and race conditions.

### 3. Order Lifecycle & PDF Invoicing
* **Order Status Progression**:
  `pending` $\rightarrow$ `confirmed` $\rightarrow$ `shipped` $\rightarrow$ `delivered` $\rightarrow$ `cancelled` / `payment_failed`
* **Automated PDF Invoices**:
  * Rendered on the fly using **WeasyPrint** from `shop/invoice.html`.
  * Generates clean, printable invoices containing company info, tax details, item breakdown, and delivery address.
* **Customer Order Portal**:
  * Order history overview with itemized breakdowns.
  * Public order tracking page allowing users to inspect delivery progression via order number.
* **Wishlist**: Real-time AJAX toggle with badge counters updated across the top navigation and mobile drawer.

### 4. User Accounts & Security
* **Email Verification**: User registration creates an inactive account and sends a verification link with a secure UUID token that expires in 15 minutes.
* **Self-Service Password Reset**: Secure base64 user ID and token-based password reset via email.
* **Google OAuth2 Social Login**: One-click authentication with Google; automatically provisions a `UserProfile` and activates the user.
* **Address Book**: Multi-address management (Home, Work, etc.) with automatic primary default switching.
* **Brute-Force Attack Defense**: `django-axes` tracks failed login attempts and temporarily locks out attacking IP addresses.
* **Maintenance Mode**: Middleware-level toggle (`MAINTENANCE_MODE=True`) serving a 503 maintenance page to public visitors while allowing staff and superusers normal access.

### 5. Staff Operations Dashboard (`/store-admin/`)
A purpose-built operations portal for day-to-day store managers:
* **KPI Metrics Overview**: Summary of total orders, pending orders count, low-stock warnings ($\le 5$ units), and out-of-stock items.
* **Product & SKU Control Center**: Add/edit products, manage variant options, set SKU stock levels, upload gallery photos, and edit specifications.
* **Global Inventory Ledger**: Filterable table showing all SKUs across the entire store with quick stock adjustments.
* **Order Processing Hub**: Inspect customer orders, update shipping statuses, and view payment transaction references.
  * Changing status to `shipped` automatically triggers customer dispatch email.
  * Changing status to `delivered` automatically triggers delivery confirmation email.
* **Support Inbox**: View and manage customer contact messages and export/toggle newsletter subscribers.
* **Review Moderation**: Approve, edit, or unpublish customer reviews.
* **CMS Banners & Sliders**: Upload and reorder homepage hero slides and promotional banners without editing template code.

### 6. Asynchronous Background Tasks (Celery + Redis)
Offloads time-consuming I/O operations from the HTTP request cycle:
* `send_verification_email`: Dispatched on registration.
* `send_password_reset_email`: Dispatched on password reset request.
* `send_order_confirmation_email`: Dispatched to customer on order confirmation.
* `send_admin_order_notification`: Dispatched to `ADMIN_ORDER_EMAIL` on new order.
* `send_order_shipped_email`: Dispatched when staff marks an order as shipped.
* `send_order_delivered_email`: Dispatched when staff marks an order as delivered.

### 7. Technical & On-Page SEO
* **Schema.org Structured Data (JSON-LD)**:
  * `Product` schema with `Offer` (price in NPR, availability, condition) and `AggregateRating`.
  * `BreadcrumbList` schema representing nested categories.
  * `Organization` and `WebSite` schema with `SearchAction` for Google Sitelinks Searchbox.
* **Dynamic Canonical Tags**: Automatically strips filter query strings (`?min_price=...&sort=...`) to preserve crawl budget and prevent duplicate content penalties.
* **Dynamic XML Sitemaps (`/sitemap.xml`)**: Automatically generates indexed XML feeds for Products, Categories, Brands, and Static Pages.
* **Crawler Control (`/robots.txt`)**: Disallows internal paths (`/admin/`, `/store-admin/`, `/cart/`, `/checkout/`, search query parameters) and points crawlers to `sitemap.xml`.

---

## 🗄️ Database Models & Schema Reference

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    Category     │◀──────│     Product     │──────▶│      Brand      │
│  (Tree / Self)  │       │                 │       │                 │
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   ProductSKU    │       │ ProductVariant  │       │  ProductImage   │
│ (Stock/PriceAdj)│       │ (Groups/Options)│       │    (Gallery)    │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         │
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    CartItem     │──────▶│      Order      │◀──────│  ProductReview  │
│  (In User Cart) │       │  (Master Order) │       │ (Verified Badge)│
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │    OrderItem    │
                          │(Snapshot Line)  │
                          └─────────────────┘
```

### 1. `core` Models
* **`HeroSlide`**: `placement` (left/right), `media_type` (image/video), `image`, `video`, `url`, `active`, `order`.
* **`HeroBanner`**: `placement` (right_top/right_bottom), `title`, `subtitle`, `cta_label`, `link`, `background`, `image`, `active`, `order`.
* **`HomePageSettings`** (Singleton): `top_zone_background`.
* **`AboutSection`** (Singleton): `title`, `heading`, `description`, counters (`products_listed`, `orders_delivered`, `happy_customers`, `years_of_service`), `is_active`.
* **`ContactMessage`**: `user` (FK User, null=True), `name`, `email`, `phone`, `subject`, `message`, `ip_address`, `status` (`new`, `read`, `archived`), `created_at`.
* **`NewsletterSubscriber`**: `email` (unique), `name`, `is_active`, `subscribed_at`, `last_subscribed_at`.

### 2. `accounts` Models
* **`UserProfile`**: `user` (OneToOne), `phone`, `photo` (saved to `profiles/user_<id>/avatar.<ext>`).
* **`Address`**: `user` (FK), `label`, `full_name`, `phone`, `street`, `city`, `province`, `postal_code`, `is_default`.
* **`EmailVerification`**: `user` (OneToOne), `token` (UUID4), `created_at`.

### 3. `products` Models
* **`Category`**: `name`, `slug` (unique), `image`, `is_popular`, `parent` (self-referential FK).
* **`Brand`**: `name`, `slug` (unique), `logo`, `url`, `is_active`, `order`.
* **`Product`**: `title`, `slug` (unique), `category` (FK), `brand` (FK), `price`, `old_price`, `image`, `description`, `product_type` (`featured`, `offer`, `new`), `created_at`.
* **`ProductImage`**: `product` (FK), `image`, `order`.
* **`ProductVariantGroup`**: `product` (FK), `name` (e.g. "Color", "RAM").
* **`ProductVariantOption`**: `group` (FK), `value` (e.g. "Space Gray", "16GB").
* **`ProductSpecification`**: `product` (FK), `section`, `name`, `value`, `is_key`.
* **`ProductSKU`**: `product` (FK), `variant_combo` (comma-separated string), `stock`, `price_adjustment`.
* **`ProductReview`**: `product` (FK), `user` (FK), `rating` (1-5), `title`, `body`, `is_published`, `created_at`.

### 4. `shop` Models
* **`Cart`**: `user` (OneToOne, null=True), `session_key`, `created_at`, `updated_at`.
* **`CartItem`**: `cart` (FK), `product` (FK), `sku` (FK), `quantity`, `unit_price`, `variant_note`.
* **`Order`**: `order_number` (GLS-XXXXXXXXXX), `user` (FK), `email`, `status`, `payment_method` (`cod`, `esewa`, `khalti`), `payment_id`, `shipping_area` (`inside_valley`, `outside_valley`), shipping address fields, `subtotal`, `shipping_cost`, `total`, `notes`, `created_at`.
* **`OrderItem`**: `order` (FK), `product` (FK), `sku` (FK), `product_title`, `variant_note`, `quantity`, `unit_price`, `line_total`.
* **`WishlistItem`**: `user` (FK), `product` (FK), `created_at`.

---

## 🗺️ Complete URL & Routing Map

| URL Pattern | App / View Name | Description |
| :--- | :--- | :--- |
| **Global Routes** | | |
| `/` | `core:index` | Homepage with hero slider, featured products, categories |
| `/robots.txt` | `core:robots_txt` | Crawler policy and sitemap reference |
| `/sitemap.xml` | `django.contrib.sitemaps.views.sitemap` | Dynamic XML sitemaps index |
| `/contact/` | `core:contact` | Contact us form |
| `/refund-policy/` | `core:refund_policy` | Return and refund policy |
| `/terms/` | `core:terms` | Terms and conditions |
| `/newsletter/subscribe/` | `core:newsletter_subscribe` | Newsletter signup endpoint (AJAX/POST) |
| `/admin/` | `admin:index` | Django default superuser admin |
| **Authentication (`/accounts/`)** | | |
| `/accounts/login/` | `accounts:login` | User login (with session cart merge) |
| `/accounts/register/` | `accounts:register` | User registration (triggers verification email) |
| `/accounts/logout/` | `accounts:logout` | User logout |
| `/accounts/activate/<uidb64>/<token>/` | `accounts:activate` | Account activation link handler |
| `/accounts/password-reset/` | `accounts:password_reset` | Forgot password email request |
| `/accounts/password-reset/done/` | `accounts:password_reset_done` | Password reset sent confirmation |
| `/accounts/password-reset/confirm/<uidb64>/<token>/` | `accounts:password_reset_confirm` | Set new password form |
| `/accounts/password-reset/complete/` | `accounts:password_reset_complete` | Password reset finished |
| `/accounts/dashboard/` | `accounts:dashboard` | User overview dashboard |
| `/accounts/profile/` | `accounts:profile` | Edit user profile and avatar |
| `/accounts/addresses/` | `accounts:addresses` | Address book list |
| `/accounts/addresses/add/` | `accounts:address_add` | Add new shipping address |
| `/accounts/addresses/<pk>/edit/` | `accounts:address_edit` | Edit existing address |
| `/accounts/addresses/<pk>/delete/` | `accounts:address_delete` | Delete address |
| `/accounts/password/change/` | `accounts:change_password` | Change password for logged-in user |
| `/auth/` | `social:*` | Google OAuth2 social login routes |
| **Catalog (`/products/`)** | | |
| `/products/` | `products:list` | Filterable catalog grid with faceted sidebar |
| `/products/category/<slug>/` | `products:category` | Category-specific product listing |
| `/products/brand/<slug>/` | `products:brand` | Brand-specific product listing |
| `/products/compare/` | `products:compare` | Product comparison matrix (up to 3 products) |
| `/products/search/autocomplete/` | `products:search_autocomplete` | Live search JSON suggestion endpoint |
| `/products/<slug>/` | `products:detail` | Product detail page with variants, specs & gallery |
| `/products/<slug>/reviews/` | `products:submit_review` | Submit product review endpoint |
| **Shopping & Payments (`/`)** | | |
| `/cart/` | `shop:cart` | Shopping cart overview |
| `/cart/add/` | `shop:cart_add` | Add item to cart (Standard form) |
| `/cart/add/ajax/` | `shop:cart_add_ajax` | Add item to cart (AJAX endpoint) |
| `/cart/update/<item_id>/` | `shop:cart_update` | Update cart item quantity |
| `/cart/remove/<item_id>/` | `shop:cart_remove` | Remove item from cart |
| `/checkout/` | `shop:checkout` | Checkout form with shipping & payment options |
| `/payment/esewa/<order_id>/q/<status>/`| `shop:esewa_verify` | eSewa payment callback & verification |
| `/payment/khalti/verify/` | `shop:khalti_verify` | Khalti payment verification endpoint |
| `/orders/` | `shop:order_list` | User order history |
| `/orders/<order_number>/` | `shop:order_detail` | Detailed order summary |
| `/orders/<order_number>/invoice/` | `shop:order_invoice` | Downloadable PDF invoice |
| `/orders/<order_number>/track/` | `shop:order_tracking` | Public order status tracker |
| `/wishlist/` | `shop:wishlist` | User wishlist page |
| `/wishlist/toggle/<product_id>/` | `shop:wishlist_toggle` | Toggle product in wishlist (AJAX/POST) |
| **Staff Admin (`/store-admin/`)** | | |
| `/store-admin/` | `store_admin:dashboard_home` | KPI dashboard & metrics |
| `/store-admin/products/` | `store_admin:product_list` | Product catalog manager |
| `/store-admin/products/add/` | `store_admin:product_add` | Add new product |
| `/store-admin/products/<pk>/` | `store_admin:product_detail`| Product control center (SKUs, images, specs) |
| `/store-admin/inventory/` | `store_admin:inventory_list`| Global SKU inventory ledger |
| `/store-admin/orders/` | `store_admin:order_list` | Store order processing manager |
| `/store-admin/orders/<pk>/` | `store_admin:order_detail` | Update order status and tracking info |
| `/store-admin/customers/` | `store_admin:customer_list` | Customer accounts overview |
| `/store-admin/contact-messages/` | `store_admin:contact_list` | Contact inquiries inbox |
| `/store-admin/newsletter-subscribers/` | `store_admin:newsletter_list` | Newsletter subscribers manager |
| `/store-admin/product-reviews/` | `store_admin:review_list` | Customer reviews moderation |
| `/store-admin/hero-slides/` | `store_admin:heroslide_list`| Homepage slider manager |
| `/store-admin/hero-banners/` | `store_admin:herobanner_list`| Promotional banners manager |

---

## ⚡ Celery Tasks Reference

All background tasks are located in their respective apps and executed asynchronously via Redis:

```python
# Task Dispatch Flow Example:
# Order Placed -> Celery Worker Queue -> Redis -> Async Email Delivery
```

| Task | Location | Trigger | Parameters | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `send_verification_email` | `accounts.tasks` | Registration | `(user_id, token, domain, protocol)` | Sends 15-minute account activation link |
| `send_password_reset_email` | `accounts.tasks` | Password Reset | `(user_id, token, uidb64, domain, protocol)` | Sends secure password reset link |
| `send_order_confirmation_email` | `shop.tasks` | Order Placed | `(order_id)` | Sends customer HTML order receipt |
| `send_admin_order_notification` | `shop.tasks` | Order Placed | `(order_id)` | Alerts store owner of incoming order |
| `send_order_shipped_email` | `shop.tasks` | Status $\rightarrow$ `shipped` | `(order_id)` | Sends shipping notice with tracking details |
| `send_order_delivered_email` | `shop.tasks` | Status $\rightarrow$ `delivered` | `(order_id)` | Sends delivery completion notice |

---

## 📁 Project Directory Tree

```text
global_link_store/
├── accounts/                     # User management & authentication app
│   ├── migrations/               # Database migrations
│   ├── static/accounts/          # Account-specific styles and scripts
│   ├── templates/accounts/       # Login, register, profile, dashboard templates
│   │   ├── emails/               # Verification & password reset HTML templates
│   │   └── includes/             # Sub-navigation components
│   ├── forms.py                  # Account & address forms
│   ├── models.py                 # UserProfile, Address, EmailVerification
│   ├── pipeline.py               # Google OAuth2 cart-merging pipeline
│   ├── tasks.py                  # Celery email tasks
│   └── views.py                  # Authentication & address views
├── config/                       # Master project configuration
│   ├── celery.py                 # Celery app initialization
│   ├── settings.py               # Core project configuration
│   ├── urls.py                   # Master URL routing & sitemaps
│   └── wsgi.py                   # WSGI application entrypoint
├── core/                         # Content, homepage & brand assets
│   ├── middleware.py             # MaintenanceModeMiddleware
│   ├── models.py                 # HeroSlide, HeroBanner, ContactMessage, etc.
│   ├── static/                   # Global CSS, JS, fonts, and images
│   │   ├── css/                  # base.css, home.css, catalog.css, product.css
│   │   ├── js/                   # base.js, shop.js, compare.js, product.js
│   │   └── img/                  # Brand logos, banners, and default graphics
│   ├── templates/core/           # Base layout, homepage, legal & support templates
│   │   └── includes/             # Hero slider, product card, banners includes
│   └── views.py                  # Homepage, contact & robots.txt handlers
├── products/                     # Product catalog & inventory app
│   ├── catalog.py                # Faceted catalog query engine
│   ├── compare_utils.py          # Specification matrix comparison engine
│   ├── models.py                 # Category, Brand, Product, ProductSKU, etc.
│   ├── review_utils.py           # Rating math & verified purchaser badge logic
│   ├── sitemaps.py               # Product, Category, Brand & Static sitemaps
│   ├── templates/products/       # Catalog, detail, compare templates
│   └── views.py                  # Product list, detail, and autocomplete endpoints
├── shop/                         # Cart, checkout, payments & order app
│   ├── cart.py                   # Cart computations & atomic stock management
│   ├── models.py                 # Cart, CartItem, Order, OrderItem, WishlistItem
│   ├── tasks.py                  # Celery order notification tasks
│   ├── templates/shop/           # Cart, checkout, order tracking & PDF invoice
│   └── views.py                  # Checkout, eSewa, Khalti, & order invoice views
├── store_admin/                  # Custom staff operations dashboard
│   ├── templates/store_admin/    # Operations dashboard and control center UI
│   └── views.py                  # Catalog, order, inventory, & review management
├── media/                        # User-uploaded files (products, brands, avatars)
├── staticfiles/                  # Production collected static files
├── templates/                    # Global error templates (404.html, 500.html, 503)
├── manage.py                     # Django CLI executable
└── requirements.txt              # Project dependencies
```

---

## ⚙️ Installation & Local Development

### 1. Prerequisites
* **Python**: `3.11` or higher (`python3 --version`)
* **Redis Server**: `7.0+` (`redis-server --version`)
* **C Library Dependencies for WeasyPrint** (PDF Generation):
  ```bash
  # Debian / Ubuntu
  sudo apt-get update
  sudo apt-get install -y build-essential python3-dev python3-pip python3-setuptools \
                          libffi-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
                          libgdk-pixbuf2.0-0 shared-mime-info

  # macOS (Homebrew)
  brew install cairo pango gdk-pixbuf libffi
  ```

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone repository
git clone https://github.com/your-username/global_link_store.git
cd global_link_store

# Initialize virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure `.env`
Create a `.env` file in the root folder:
```bash
cp .env.example .env  # Or create .env manually with the reference below
```

### 4. Database Setup & Initial Superuser
```bash
# Run database migrations
python manage.py migrate

# Create superuser administrator account
python manage.py createsuperuser
```

### 5. Running the Application Stack
You will need **3 terminal windows** for full functionality:

**Terminal 1 — Redis Server:**
```bash
redis-server
```

**Terminal 2 — Celery Worker:**
```bash
celery -A config worker --loglevel=info
```

**Terminal 3 — Django Development Server:**
```bash
python manage.py runserver 0.0.0.0:8000
```

Access the application:
* **Storefront**: [http://localhost:8000](http://localhost:8000)
* **Custom Store Admin**: [http://localhost:8000/store-admin/](http://localhost:8000/store-admin/)
* **Django Superuser Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🔐 Environment Variables Reference (`.env`)

| Variable | Type | Default / Example | Purpose |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | String | `django-insecure-...` | Django cryptographic signing key |
| `DEBUG` | Boolean | `True` | Debug mode (`True` for local, `False` for prod) |
| `MAINTENANCE_MODE` | Boolean | `False` | Locks site with 503 maintenance page |
| `ALLOWED_HOSTS` | CSV | `localhost,127.0.0.1` | Allowed HTTP Host headers |
| `CSRF_TRUSTED_ORIGINS` | CSV | `http://localhost:8000` | Whitelisted origins for CSRF POST requests |
| `SITE_URL` | URL | `http://localhost:8000` | Canonical store URL |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` | String | `...apps.googleusercontent.com` | Google OAuth2 Client ID |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | String | `GOCSPX-...` | Google OAuth2 Client Secret |
| `CELERY_BROKER_URL` | URL | `redis://127.0.0.1:6379/0` | Redis connection URL for Celery broker |
| `CELERY_RESULT_BACKEND` | URL | `redis://127.0.0.1:6379/0` | Redis connection URL for task results |
| `CELERY_TASK_ALWAYS_EAGER` | Boolean | `False` | If `True`, runs tasks synchronously without Redis |
| `EMAIL_BACKEND` | String | `django.core.mail.backends.smtp.EmailBackend` | Email delivery backend |
| `EMAIL_HOST` | String | `smtp.gmail.com` | SMTP Server Host |
| `EMAIL_PORT` | Integer | `587` | SMTP Server Port |
| `EMAIL_USE_TLS` | Boolean | `True` | Enable TLS encryption |
| `EMAIL_HOST_USER` | Email | `shop@globallinkstore.com` | SMTP authentication username |
| `EMAIL_HOST_PASSWORD` | String | `app-password-here` | SMTP authentication password / App password |
| `DEFAULT_FROM_EMAIL` | String | `Global Link Store <shop@globallinkstore.com>` | Sender address for outgoing emails |
| `ESEWA_SECRET_KEY` | String | `8gBm/:&EnhH.1/q` | eSewa HMAC-SHA256 signature secret key |
| `ESEWA_PRODUCT_CODE` | String | `EPAYTEST` | eSewa merchant product code |
| `ESEWA_PAYMENT_URL` | URL | `https://rc-epay.esewa.com.np/api/epay/main/v2/form` | eSewa payment endpoint |
| `ESEWA_RETURN_URL` | URL | `http://localhost:8000/payment/esewa/` | eSewa payment return callback |
| `KHALTI_SECRET_KEY` | String | `key_live_...` or `test_secret_key_...` | Khalti authorization secret key |
| `KHALTI_INITIATE_URL` | URL | `https://dev.khalti.com/api/v2/epayment/initiate/` | Khalti payment initialization endpoint |
| `KHALTI_LOOKUP_URL` | URL | `https://dev.khalti.com/api/v2/epayment/lookup/` | Khalti transaction verification endpoint |
| `KHALTI_RETURN_URL` | URL | `http://localhost:8000/payment/khalti/verify/` | Khalti return callback URL |

---

## 💳 Payment Gateway Testing (eSewa & Khalti)

### 1. eSewa Sandbox Integration
* **Gateway URL**: `https://rc-epay.esewa.com.np/api/epay/main/v2/form`
* **Test Credentials**:
  * **eSewa ID**: `9849511111` or `9849511112`
  * **Password**: `Nepal@123`
  * **MPIN**: `1122`
  * **Token / OTP**: `123456`

### 2. Khalti Sandbox Integration
* **Gateway URL**: `https://dev.khalti.com/api/v2/epayment/initiate/`
* **Test Credentials**:
  * **Mobile Number**: `9800000000` / `9800000001`
  * **MPIN**: `1111`
  * **OTP**: `987654`

---

## 👨‍💼 Staff Workflows & Management Guide

### Creating a Product with Multi-Variant SKUs
1. Log in to `/store-admin/` and navigate to **Products** $\rightarrow$ **Add Product**.
2. Enter the base product title, category, brand, base price, and main cover image.
3. Open the newly created product in the **Product Control Center**:
   * **Variant Groups**: Create a group (e.g., *"Color"*), then add options (*"Midnight Black"*, *"Silver"*). Create a second group (e.g., *"Storage"*), then add options (*"256GB"*, *"512GB"*).
   * **SKUs**: Add discrete SKUs for each variant combo (e.g., `Color:Midnight Black,Storage:512GB`) specifying stock quantity and price adjustment (+Rs 15,000).
   * **Specifications**: Add key specs (Processor, Display, Battery) grouped by sections.
   * **Gallery**: Upload high-resolution secondary product images.

### Order Processing & Status Automation
1. When a new order arrives, its status starts as `pending` (or `confirmed` if paid via eSewa/Khalti/COD).
2. Open the order in `/store-admin/orders/<pk>/`.
3. Update the status to `shipped`: Celery immediately dispatches a branded shipping email to the customer.
4. Update the status to `delivered`: Celery dispatches a delivery confirmation email inviting the customer to leave a verified review.

---

## 🚀 Production Deployment & cPanel Setup

### 1. Static Asset Compression
Collect and compress static assets with WhiteNoise:
```bash
python manage.py collectstatic --noinput
```

### 2. cPanel / Passenger Deployment Checklist
* **Python App Path**: Set application root to `/home/<user>/global_link_store`.
* **WSGI File**: Point Passenger to `config/wsgi.py`.
* **Media Serving Symlink**: If media files are placed outside `public_html`, create a symlink:
  ```bash
  ln -s /home/<user>/global_link_store/media /home/<user>/public_html/media
  ```
* **Production Supervisor for Celery**:
  ```ini
  [program:globallink_celery]
  command=/home/<user>/virtualenv/global_link_store/3.11/bin/celery -A config worker --loglevel=info
  directory=/home/<user>/global_link_store
  user=<user>
  autostart=true
  autorestart=true
  redirect_stderr=true
  stdout_logfile=/home/<user>/logs/celery.log
  ```

---

## 📄 License & Attribution

Developed for **Global Link Store**, Lalitpur, Nepal.  
All rights reserved © 2026.
