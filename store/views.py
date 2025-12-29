from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
import random
import razorpay
import json
import hmac
import hashlib
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from decimal import Decimal
from .models import (
    Category, Brand, Product, ProductImage, ProductSpecification,
    UserProfile, Address, Cart, CartItem, Wishlist, Coupon,
    Order, OrderItem, OrderStatusHistory, ReturnRequest,
    Review, ReviewImage, Newsletter, ContactMessage
)


# Home Page
def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    brands = Brand.objects.filter(is_active=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'brands': brands,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'store/home.html', context)


# Product Listing
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    # Filtering
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['price', '-price', 'name', '-name', '-created_at']:
        products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': category_slug,
        'current_brand': brand_slug,
    }
    return render(request, 'store/product_list.html', context)


# Product Detail
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has purchased this product
    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__order_status='delivered'
        ).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_review': can_review,
    }
    return render(request, 'store/product_detail.html', context)


# Search with AJAX
def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query),
            is_active=True
        )[:5]
        
        suggestions = [{
            'name': p.name,
            'url': f'/product/{p.slug}/',
            'price': str(p.final_price),
            'image': p.images.filter(is_primary=True).first().image.url if p.images.filter(is_primary=True).exists() else ''
        } for p in products]
        
        return JsonResponse({'suggestions': suggestions})
    return JsonResponse({'suggestions': []})


# User Registration
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        Cart.objects.create(user=user)
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'store/register.html')


# User Login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'store/login.html')


# User Logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# Forgot Password
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['forgot_pwd_otp'] = otp
            request.session['forgot_pwd_email'] = email
            
            # Send Email
            subject = 'Password Reset OTP - FlugEde'
            message = f'Hi {user.username},\n\nYour OTP for password reset is: {otp}\n\nValid for 10 minutes.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            messages.success(request, 'OTP sent to your email address.')
            return redirect('verify_otp')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            
    return render(request, 'store/forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_session = request.session.get('forgot_pwd_otp')
        
        if otp_session and otp_entered == otp_session:
            request.session['forgot_pwd_verified'] = True
            messages.success(request, 'OTP verified successfully.')
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            
    return render(request, 'store/verify_otp.html')


def reset_password(request):
    if not request.session.get('forgot_pwd_verified'):
        messages.warning(request, 'Please verify your OTP first.')
        return redirect('forgot_password')
        
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            email = request.session.get('forgot_pwd_email')
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Cleanup session
                if 'forgot_pwd_otp' in request.session: del request.session['forgot_pwd_otp']
                if 'forgot_pwd_email' in request.session: del request.session['forgot_pwd_email']
                if 'forgot_pwd_verified' in request.session: del request.session['forgot_pwd_verified']
                
                messages.success(request, 'Password reset successfully! Please login.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('forgot_password')
        else:
            messages.error(request, 'Passwords do not match.')
            
    return render(request, 'store/reset_password.html')


# User Profile
@login_required
def profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        
        profile.phone = request.POST.get('phone')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {'profile': profile}
    return render(request, 'store/profile.html', context)


# Address Management
@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'store/address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address_line1=request.POST.get('address_line1'),
            address_line2=request.POST.get('address_line2', ''),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            pincode=request.POST.get('pincode'),
            address_type=request.POST.get('address_type', 'home'),
            is_default=request.POST.get('is_default') == 'on'
        )
        messages.success(request, 'Address added successfully!')
        return redirect('address_list')
    
    return render(request, 'store/add_address.html')


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.full_name = request.POST.get('full_name')
        address.phone = request.POST.get('phone')
        address.address_line1 = request.POST.get('address_line1')
        address.address_line2 = request.POST.get('address_line2', '')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.pincode = request.POST.get('pincode')
        address.address_type = request.POST.get('address_type')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        
        messages.success(request, 'Address updated successfully!')
        return redirect('address_list')
    
    return render(request, 'store/edit_address.html', {'address': address})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('address_list')


# Cart Management
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {'cart': cart}
    return render(request, 'store/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} quantity updated in cart!')
        else:
            messages.warning(request, 'Not enough stock available!')
    else:
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'success': True, 'message': 'Cart updated!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid quantity!'})
    
    return JsonResponse({'success': False})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('cart')


# Wishlist
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'{product_name} removed from wishlist!')
    return redirect('wishlist')


# Checkout
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    addresses = request.user.addresses.all()
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        coupon_code = request.POST.get('coupon_code', '')
        # Validate address selection to avoid 404 when missing/invalid
        if not address_id:
            messages.error(request, 'Please select a delivery address before placing your order.')
            return redirect('checkout')

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, 'Selected address was not found. Please choose a valid address.')
            return redirect('checkout')
        
        # Calculate totals
        subtotal = cart.subtotal
        shipping_charge = Decimal('50.00') if subtotal < 500 else Decimal('0.00')
        tax = subtotal * Decimal('0.18')  # 18% GST
        discount = Decimal('0.00')
        coupon = None
        
        # Apply coupon
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid() and subtotal >= coupon.min_purchase_amount:
                    if coupon.discount_type == 'percentage':
                        discount = (subtotal * coupon.discount_value) / 100
                        if coupon.max_discount_amount:
                            discount = min(discount, coupon.max_discount_amount)
                    else:
                        discount = coupon.discount_value
                    coupon.used_count += 1
                    coupon.save()
            except Coupon.DoesNotExist:
                messages.warning(request, 'Invalid coupon code!')
        
        total = subtotal + shipping_charge + tax - discount
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal=subtotal,
            shipping_charge=shipping_charge,
            tax=tax,
            discount=discount,
            total=total,
            coupon=coupon,
            payment_method=payment_method,
            expected_delivery_date=timezone.now().date() + timedelta(days=7)
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.final_price,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price,
                warranty_period=cart_item.product.warranty_period,
                return_deadline=timezone.now().date() + timedelta(days=7)
            )
            
            # Update stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order placed successfully'
        )
        
        # Handle payment method
        if payment_method == 'cod':
            # Cash on Delivery - no payment needed
            order.payment_status = 'pending'
            order.order_status = 'confirmed'
            order.save()
            cart.items.all().delete()
            messages.success(request, f'Order placed successfully! Order Number: {order.order_number}')
            return redirect('order_success', order_number=order.order_number)
        elif payment_method == 'razorpay':
            # Online payment via Razorpay
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                messages.warning(request, 'Razorpay payment gateway is not configured. Please select Cash on Delivery or configure Razorpay API keys.')
                order.delete()
                return redirect('checkout')
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(total * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': order.order_number,
                'notes': {
                    'order_id': str(order.id),
                    'user_id': str(request.user.id),
                }
            })
            
            # Save Razorpay order ID
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            
            # Return JSON response with Razorpay order details
            return JsonResponse({
                'success': True,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': int(total * 100),
                'currency': 'INR',
                'order_id': order.id,
                'order_number': order.order_number,
            })
        else:
            messages.error(request, 'Invalid payment method selected.')
            order.delete()
            return redirect('checkout')
    
    context = {
        'cart': cart,
        'addresses': addresses,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID if settings.RAZORPAY_KEY_ID else '',
    }
    return render(request, 'store/checkout.html', context)


# Apply Coupon (AJAX)
@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        cart = get_object_or_404(Cart, user=request.user)
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid() and cart.subtotal >= coupon.min_purchase_amount:
                if coupon.discount_type == 'percentage':
                    discount = (cart.subtotal * coupon.discount_value) / 100
                    if coupon.max_discount_amount:
                        discount = min(discount, coupon.max_discount_amount)
                else:
                    discount = coupon.discount_value
                
                return JsonResponse({
                    'success': True,
                    'discount': str(discount),
                    'message': 'Coupon applied successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Coupon is not valid or minimum purchase amount not met!'
                })
        except Coupon.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Invalid coupon code!'
            })
    
    return JsonResponse({'success': False})


# Orders
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.order_status in ['pending', 'confirmed']:
        order.order_status = 'cancelled'
        order.save()
        
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes='Order cancelled by user'
        )
        
        messages.success(request, 'Order cancelled successfully!')
    else:
        messages.error(request, 'This order cannot be cancelled!')
    
    return redirect('order_detail', order_id=order.id)


# Return Request
@login_required
def request_return(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__user=request.user)
    
    if request.method == 'POST':
        ReturnRequest.objects.create(
            order_item=order_item,
            user=request.user,
            reason=request.POST.get('reason'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Return request submitted successfully!')
        return redirect('order_detail', order_id=order_item.order.id)
    
    return render(request, 'store/request_return.html', {'order_item': order_item})


# Reviews
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased this product
    order_item = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__order_status='delivered'
    ).first()
    
    if not order_item:
        messages.error(request, 'You can only review products you have purchased!')
        return redirect('product_detail', slug=product.slug)
    
    if request.method == 'POST':
        Review.objects.create(
            product=product,
            user=request.user,
            order_item=order_item,
            rating=request.POST.get('rating'),
            title=request.POST.get('title'),
            comment=request.POST.get('comment'),
            is_verified_purchase=True
        )
        messages.success(request, 'Review submitted successfully! It will be visible after approval.')
        return redirect('product_detail', slug=product.slug)
    
    return render(request, 'store/add_review.html', {'product': product})


# Contact
def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    
    return render(request, 'store/contact.html')


# Newsletter Subscription
def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        Newsletter.objects.get_or_create(email=email)
        return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
    return JsonResponse({'success': False})


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


# Razorpay Payment Callback
@csrf_exempt
@login_required
def razorpay_payment_callback(request):
    if request.method == 'POST':
        try:
            # Get payment details from Razorpay
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            order_id = request.POST.get('order_id')
            
            # Get order from database
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # Verify payment signature
            if settings.RAZORPAY_KEY_SECRET:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                # Verify signature
                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                }
                
                try:
                    client.utility.verify_payment_signature(params_dict)
                    
                    # Payment verified - update order
                    order.razorpay_payment_id = razorpay_payment_id
                    order.razorpay_signature = razorpay_signature
                    order.payment_status = 'completed'
                    order.order_status = 'confirmed'
                    order.save()
                    
                    # Clear cart
                    cart, created = Cart.objects.get_or_create(user=request.user)
                    cart.items.all().delete()
                    
                    # Create status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='confirmed',
                        notes='Payment completed via Razorpay'
                    )
                    
                    messages.success(request, f'Payment successful! Order Number: {order.order_number}')
                    return redirect('order_success', order_number=order.order_number)
                    
                except razorpay.errors.SignatureVerificationError:
                    # Payment signature verification failed
                    order.payment_status = 'failed'
                    order.save()
                    messages.error(request, 'Payment verification failed. Please try again.')
                    return redirect('checkout')
            else:
                messages.error(request, 'Payment gateway is not configured.')
                return redirect('checkout')
                
        except Exception as e:
            messages.error(request, f'An error occurred during payment processing: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')


@csrf_exempt
def verify_payment(request):
    """Verify Razorpay payment sent from frontend (JSON) and finalize order."""
    if request.method != 'POST':
        return JsonResponse({'status': 'fail', 'message': 'Invalid method'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'fail', 'message': 'Invalid JSON'}, status=400)

    razorpay_order_id = payload.get('razorpay_order_id')
    razorpay_payment_id = payload.get('razorpay_payment_id')
    razorpay_signature = payload.get('razorpay_signature')

    if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
        return JsonResponse({'status': 'fail', 'message': 'Missing payment parameters'}, status=400)

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({'status': 'fail', 'message': 'Razorpay not configured'}, status=500)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_payment_signature(params_dict)

        # find local order and update
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.payment_status = 'completed'
        order.order_status = 'confirmed'
        order.save()

        # clear cart for the user
        cart, _ = Cart.objects.get_or_create(user=order.user)
        cart.items.all().delete()

        OrderStatusHistory.objects.create(
            order=order,
            status='confirmed',
            notes='Payment completed via Razorpay'
        )

        return JsonResponse({'status': 'ok'})

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'status': 'fail', 'message': 'Signature verification failed'}, status=400)
    except Order.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': str(e)}, status=500)
