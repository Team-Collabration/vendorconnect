# VendorConnect — Digital Marketplace for India's Street Food Supply Chain

<div align="center">

![Django](https://img.shields.io/badge/Django-Backend-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Razorpay](https://img.shields.io/badge/Razorpay-Payments-02042B?style=for-the-badge&logo=razorpay&logoColor=white)

**Empowering India's street food vendors by connecting them directly with trusted, affordable raw material suppliers — no middlemen, no delays, full transparency.**

[![Django REST](https://img.shields.io/badge/Django%20REST-API%20Framework-ff1709?style=flat-square)](https://www.django-rest-framework.org/)
[![Maps API](https://img.shields.io/badge/Google%20Maps-Location%20Services-4285F4?style=flat-square&logo=googlemaps&logoColor=white)](https://developers.google.com/maps)
[![Razorpay](https://img.shields.io/badge/Razorpay-Payment%20Gateway-02042B?style=flat-square)](https://razorpay.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Source%20Code-181717?style=flat-square&logo=github)](https://github.com/Team-Collabration/vendorconnect)

🎬 **[Watch Demo](https://drive.google.com/file/d/1J_paaNMBf6qVHG-UM-G75Ff-BOwu0HX6/view?usp=sharing)** &nbsp;|&nbsp; 💻 **[GitHub Repository](https://github.com/Team-Collabration/vendorconnect.git)**

</div>

---

## 📌 Overview

**VendorConnect** is a full-stack web platform that digitizes the raw material procurement process for India's street food vendors. By bridging the gap between local vendors and verified suppliers, VendorConnect eliminates intermediaries, promotes fair pricing, and builds a transparent and efficient supply chain ecosystem.

From supplier discovery and real-time price comparison to secure payments and AI-driven demand forecasting — VendorConnect handles the entire sourcing workflow in one place.

> *"Technology-driven procurement for the backbone of India's food economy."*

---

## 🌍 Problem Statement

Street food vendors across India face critical challenges in sourcing raw materials:

| Challenge | Impact |
|-----------|--------|
| 🔗 Dependence on middlemen | Higher costs, lack of transparency |
| 📉 No real-time price comparison | Vendors overpay without awareness |
| 🤝 Unreliable or unverified suppliers | Inconsistent quality and supply |
| 📦 Limited access to bulk discounts | Reduced profit margins |
| 🕐 Manual, slow procurement process | Delays and operational inefficiency |

**VendorConnect solves all of the above** — through automation, digitization, and a data-driven marketplace.

---

## ✨ Features

### 👤 For Vendors

| Feature | Description |
|---------|-------------|
| 🗺️ **Find Verified Suppliers** | Discover nearby suppliers through Google Maps integration |
| 💰 **Real-Time Price Comparison** | Instantly compare rates across multiple suppliers |
| 📦 **Bulk Order Placement** | Place large orders efficiently through an intuitive interface |
| 💳 **Secure Payments** | Razorpay-powered payment gateway for safe online transactions |
| 🔔 **Smart Notifications** | Instant alerts for price changes, new offers, and order updates |
| ⭐ **Reviews & Ratings** | Community-driven supplier accountability and transparency |
| 📊 **Order & Price Tracking** | Unified dashboard for purchase history, delivery status, and market trends |

### 🏭 For Suppliers

| Feature | Description |
|---------|-------------|
| 🛒 **Product Management** | Add, edit, and remove products with live pricing and availability control |
| 📣 **Business Expansion** | Reach verified vendors via automated recommendation and discovery |
| 💬 **Direct Chat** | Built-in messaging for quotations and vendor communication |
| 🗺️ **Delivery Zone Management** | Define delivery regions using map-based zone selection |
| 🔔 **Vendor Notifications** | Instant alerts on new inquiries and order placements |
| 🤖 **AI Demand Forecasting** | Predict market demand for specific products using AI models |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│              HTML  ·  CSS  ·  JavaScript                     │
│                                                              │
│    ┌─────────────┐   ┌──────────────┐   ┌───────────────┐   │
│    │ Vendor UI   │   │ Supplier UI  │   │ Admin Panel   │   │
│    └──────┬──────┘   └──────┬───────┘   └───────┬───────┘   │
└───────────┼─────────────────┼───────────────────┼───────────┘
            │                 │                   │
            └─────────────────┼───────────────────┘
                              │  HTTP / REST API
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                       BACKEND (Django)                       │
│                   Django REST Framework                      │
│                                                              │
│   ┌──────────────┐  ┌────────────┐  ┌─────────────────────┐ │
│   │  Auth &      │  │  Order &   │  │  Notification &     │ │
│   │  User Mgmt   │  │  Product   │  │  Chat Service       │ │
│   └──────────────┘  └────────────┘  └─────────────────────┘ │
│                                                              │
│   ┌──────────────┐  ┌────────────┐  ┌─────────────────────┐ │
│   │  Razorpay    │  │ Maps API   │  │  AI Demand          │ │
│   │  Integration │  │ Integration│  │  Forecasting Module │ │
│   └──────────────┘  └────────────┘  └─────────────────────┘ │
│                                                              │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   SQLite DB     │
                          │  (candidates,   │
                          │   orders,       │
                          │   products,     │
                          │   reviews)      │
                          └─────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Backend** | Django, Django REST Framework |
| **Database** | SQLite |
| **Payment Gateway** | Razorpay API |
| **Maps & Location** | Google Maps API |
| **AI Module** | Demand Forecasting (ML-based) |
| **Version Control** | Git, GitHub |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- Git
- A modern web browser

### 1. Clone the Repository

```bash
git clone https://github.com/Team-Collabration/vendorconnect.git
cd vendorconnect
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Admin Access)

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

---

## 📱 User Flows

### Vendor Journey
```
Register / Login
      ↓
Browse Verified Suppliers (Maps)
      ↓
Compare Prices Across Suppliers
      ↓
Place Bulk Order
      ↓
Secure Payment via Razorpay
      ↓
Track Delivery & Order Status
      ↓
Submit Review & Rating
```

### Supplier Journey
```
Register / Login
      ↓
Add Products & Set Pricing
      ↓
Define Delivery Zones (Maps)
      ↓
Receive Vendor Inquiries (Chat)
      ↓
Accept & Fulfill Orders
      ↓
View AI Demand Predictions
      ↓
Expand Reach via Discovery Engine
```

---

## 🤖 AI — Market Demand Forecasting

VendorConnect includes an AI-powered demand prediction module for suppliers:

- Analyzes **historical order data** to forecast demand for individual products
- Helps suppliers plan **inventory and pricing** ahead of seasonal demand
- Reduces waste and stockouts through **data-driven restocking alerts**
- Outputs demand curves per product over configurable time horizons

---

## 📊 Dashboard Highlights

**Vendor Dashboard**
- Real-time price tracker across all connected suppliers
- Order history with full status timeline
- Saved suppliers and wishlist products
- Notification center for offers and alerts

**Supplier Dashboard**
- Active product listings with pricing controls
- Incoming order queue with acceptance workflow
- Delivery zone map view
- AI demand prediction chart per product
- Vendor rating and review aggregation

---

## 🔒 Security

- Django's built-in **CSRF protection** on all form submissions
- **Razorpay webhook signature verification** for payment integrity
- **Role-based access control** — vendors and suppliers see only their own data
- Passwords stored using Django's **PBKDF2 hashing** with salt
- All API keys managed via environment variables — never hardcoded

---

## 🗺️ Roadmap

- [ ] **AI-Powered Vendor–Supplier Matching** — Personalized recommendations based on pricing, reliability, and order history
- [ ] **Collaborative Bulk Ordering** — Vendors can form groups for shared purchasing and collective discounts
- [ ] **Multi-Language Support** — Hindi, Tamil, Telugu, and other regional languages
- [ ] **Mobile App** — React Native app for vendors on the go
- [ ] **Multi-Currency Support** — Expand beyond INR for cross-border sourcing
- [ ] **Logistics Integration** — Partner with delivery services for last-mile tracking

---

## 🌟 Vision

To build a **transparent, technology-driven, and inclusive digital marketplace** that empowers local vendors, simplifies sourcing, and strengthens India's street food supply chain ecosystem — putting fair trade and financial access directly into the hands of small-scale businesses.

---

## 🔗 Links

| Resource | Link |
|----------|------|
| 🎬 Demo Video | [Watch on Google Drive](https://drive.google.com/file/d/1J_paaNMBf6qVHG-UM-G75Ff-BOwu0HX6/view?usp=sharing) |
| 💻 Source Code | [github.com/Team-Collabration/vendorconnect](https://github.com/Team-Collabration/vendorconnect.git) |

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: describe your change'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️**

*Empowering vendors. Connecting suppliers. Strengthening India's food economy.*

⭐ Star this repo if VendorConnect inspired you!

</div>
