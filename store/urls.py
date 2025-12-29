from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # User Profile
    path('profile/', views.profile, name='profile'),
    
    # Address Management
    path('addresses/', views.address_list, name='address_list'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('razorpay/callback/', views.razorpay_payment_callback, name='razorpay_callback'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('orders/', views.order_list, name='order_list'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Returns
    path('return/<int:order_item_id>/', views.request_return, name='request_return'),
    
    # Reviews
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    
    # Contact & Newsletter
    path('contact/', views.contact, name='contact'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
]
