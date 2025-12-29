# 🛍️ FlugEde - Premium E-Commerce Platform

> A full-featured, modern e-commerce web application for selling electronic gadgets and devices. Built with Django, featuring a stunning dark-themed UI with glassmorphism effects, comprehensive product management, advanced search, and seamless Razorpay payment integration.

![Django](https://img.shields.io/badge/Django-6.0-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## ✨ Key Features

### 🔐 User Authentication & Management

- ✅ Email-based user registration with verification
- ✅ Secure login/logout with password hashing
- ✅ Password reset via OTP
- ✅ User profile management
- ✅ Multiple saved delivery addresses
- ✅ Wishlist functionality
- ✅ Order history tracking

### 📱 Product Management

- **Comprehensive Catalog**
  - Multiple categories and brands
  - Advanced filtering (price, features, brand)
  - Featured products showcase
  - New arrivals section
  - Product search with auto-suggestions
- **Detailed Product Pages**
  - High-quality image gallery
  - Technical specifications table
  - Warranty information
  - Stock status indicators
  - Customer reviews and ratings
  - Similar product recommendations

### 🛒 Shopping Cart & Checkout

- ✅ Add/remove items with instant updates
- ✅ Modify quantities
- ✅ Auto price recalculation with GST (18%)
- ✅ Shipping charge calculation
- ✅ Coupon/discount code support
- ✅ Address selection at checkout
- ✅ Two payment methods (COD + Online)

### 💳 Payment Integration

- ✅ **Razorpay Integration** (Live & Test Mode)
  - Secure payment gateway
  - Multiple payment methods (Cards, UPI, Net Banking, Wallets)
  - HMAC-SHA256 signature verification
  - Real-time payment confirmation
  - Automatic order status updates

### 📦 Order Management

- ✅ Order creation and tracking
- ✅ Order status history
- ✅ Order cancellation
- ✅ Return requests
- ✅ Email notifications
- ✅ Delivery date tracking

### ⭐ Additional Features

- ✅ Product reviews and ratings
- ✅ Wishlist management
- ✅ Newsletter subscription
- ✅ Contact form
- ✅ Admin dashboard
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark theme with glassmorphism UI

---

## 🛠️ Tech Stack

### Backend

- **Framework**: Django 6.0
- **Language**: Python 3.12
- **Database**: SQLite3 (Development) / PostgreSQL (Production)
- **Payment Gateway**: Razorpay Python SDK
- **Email**: Django's built-in email backend

### Frontend

- **HTML5** with Django Templates
- **CSS3** with responsive design
- **JavaScript** with jQuery 3.6.0
- **Icons**: Font Awesome 6.0
- **UI Design**: Glassmorphism + Dark Theme

### Development Tools

- **ORM**: Django ORM
- **Authentication**: Django built-in auth
- **Admin Panel**: Django Admin
- **Environment**: Python Virtual Environment

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (3.12 recommended)
- **pip** (Python package manager)
- **Git**
- **Razorpay Account** (for payment integration)
- **Email Service** (Gmail or SMTP server for notifications)

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/flugede.git
cd flugede
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - uses SQLite by default)
# DATABASE_URL=postgresql://user:password@localhost:5432/flugede

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Razorpay Configuration (Get from Razorpay Dashboard)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
```

### 5. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: **http://localhost:8000**

---

## 📖 Usage Guide

### For Users

1. **Register/Login**: Create account or sign in
2. **Browse Products**: Search or filter electronic gadgets
3. **Add to Cart**: Select items and add to shopping cart
4. **Checkout**: Choose delivery address and payment method
5. **Payment**: Use test card `4111111111111111` in test mode
6. **Track Order**: View order status in your profile

### For Admin

1. Access Admin Panel: **http://localhost:8000/admin**
2. Manage Products, Categories, Brands
3. View and process orders
4. Manage coupons and discounts
5. View customer reviews

---

## 🔧 Configuration Guide

### Razorpay Setup

1. Sign up at [Razorpay](https://razorpay.com)
2. Get API Keys from Dashboard → Settings → API Keys
3. Copy `Key ID` and `Key Secret` to `.env` file
4. Use test credentials for development

**Test Card Details**:

- Card Number: `4111111111111111`
- Expiry: Any future date (e.g., 12/25)
- CVV: Any 3 digits (e.g., 123)

### Email Configuration

1. Enable 2-Step Verification on Gmail
2. Generate App Password
3. Add to `.env` as `EMAIL_HOST_PASSWORD`

---

## 📁 Project Structure

```
flugede/
├── flugede/                    # Django project settings
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── store/                      # Main app (models, views, templates)
│   ├── models.py               # Database models
│   ├── views.py                # View logic
│   ├── urls.py                 # App URL patterns
│   ├── templates/store/        # HTML templates
│   ├── static/                 # CSS, JS, Images
│   └── management/             # Custom commands
├── media/                      # User uploaded files
├── static/                     # Static files
├── staticfiles/                # Collected static files
├── manage.py                   # Django management
├── requirements.txt            # Dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🧪 Testing

### Run Tests

```bash
python manage.py test store
```

### Test Payment Flow

1. Go to checkout page
2. Select Razorpay as payment method
3. Use test card: `4111111111111111`
4. Payment should succeed (test mode)

---

## 🌐 Deployment

### Prepare for Production

```bash
# Set DEBUG=False in .env
DEBUG=False

# Update ALLOWED_HOSTS
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Use strong SECRET_KEY
SECRET_KEY=generate-a-new-strong-key

# Configure PostgreSQL
DATABASE_URL=postgresql://...

# Set email to production
EMAIL_HOST=smtp.gmail.com (or your SMTP server)
```

### Deploy on Heroku

```bash
# Install Heroku CLI
heroku login
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Push code
git push heroku main
```

### Deploy on PythonAnywhere

1. Create account at PythonAnywhere
2. Upload project files
3. Configure web app settings
4. Point domain to your app

---

## 📝 API Endpoints

### Authentication

- `POST /register/` - Register new user
- `POST /login/` - User login
- `GET /logout/` - User logout

### Products

- `GET /products/` - List all products
- `GET /product/<slug>/` - Product details
- `GET /search-suggestions/` - Search autocomplete

### Cart

- `POST /cart/add/<product_id>/` - Add to cart
- `POST /cart/update/<item_id>/` - Update quantity
- `POST /cart/remove/<item_id>/` - Remove from cart

### Orders

- `POST /checkout/` - Create order & payment
- `POST /verify-payment/` - Verify Razorpay payment
- `GET /orders/` - View user orders

---

## 🐛 Troubleshooting

### Database Issues

```bash
# Reset migrations
python manage.py migrate store zero
python manage.py migrate
```

### Static Files Not Loading

```bash
python manage.py collectstatic --clear --noinput
```

### Razorpay Payment Fails

- Verify API keys in `.env`
- Check browser console (F12) for errors
- Ensure test card is used in test mode

### Email Not Sending

- Enable "Less secure app access" on Gmail
- Use App Password instead of account password
- Check SMTP settings in `.env`

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Razorpay Documentation](https://razorpay.com/docs/)
- [Python Tutorial](https://python.org/doc)
- [Font Awesome Icons](https://fontawesome.com/icons)

---

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 💬 Support & Contact

- **Issues**: Use GitHub Issues for bug reports
- **Email**: your-email@example.com
- **Documentation**: Check project wiki for detailed guides

---

## 🙏 Acknowledgments

- Django community for the excellent framework
- Razorpay for secure payment integration
- Font Awesome for beautiful icons
- All contributors and testers

---

## 📊 Project Status

- ✅ MVP (Minimum Viable Product) - Complete
- ✅ Core Features - Implemented
- ✅ Payment Integration - Live
- 🚀 Production Ready - Yes
- 📈 Active Development - Yes

---

**Happy Selling! 🎉**

For questions or suggestions, feel free to reach out or open an issue on GitHub.
