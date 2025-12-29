// Main JavaScript for FlugEde E-Commerce

$(document).ready(function () {
    // Search Suggestions
    let searchTimeout;
    $('#searchInput').on('keyup', function () {
        clearTimeout(searchTimeout);
        const query = $(this).val();

        if (query.length >= 2) {
            searchTimeout = setTimeout(function () {
                $.ajax({
                    url: '/search-suggestions/',
                    data: { 'q': query },
                    success: function (data) {
                        displaySearchSuggestions(data.suggestions);
                    }
                });
            }, 300);
        } else {
            $('#searchSuggestions').hide();
        }
    });

    function displaySearchSuggestions(suggestions) {
        const container = $('#searchSuggestions');
        container.empty();

        if (suggestions.length > 0) {
            suggestions.forEach(function (item) {
                const suggestionItem = $('<a>')
                    .attr('href', item.url)
                    .addClass('suggestion-item')
                    .html(`
                        <div style="display: flex; align-items: center; gap: 1rem; padding: 0.75rem; border-bottom: 1px solid var(--border-color); transition: var(--transition-fast);">
                            ${item.image ? `<img src="${item.image}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 0.5rem;">` : ''}
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: var(--text-primary);">${item.name}</div>
                                <div style="color: var(--primary-light); font-weight: 700;">₹${item.price}</div>
                            </div>
                        </div>
                    `);
                container.append(suggestionItem);
            });

            container.css({
                'position': 'absolute',
                'top': '100%',
                'left': 0,
                'right': 0,
                'background': 'var(--bg-card)',
                'border': '1px solid var(--border-color)',
                'border-radius': '0.5rem',
                'margin-top': '0.5rem',
                'box-shadow': 'var(--shadow-lg)',
                'z-index': 1000,
                'max-height': '400px',
                'overflow-y': 'auto'
            }).show();

            $('.suggestion-item').hover(
                function () { $(this).css('background', 'var(--bg-tertiary)'); },
                function () { $(this).css('background', 'transparent'); }
            );
        } else {
            container.hide();
        }
    }

    // Close suggestions when clicking outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.search-container').length) {
            $('#searchSuggestions').hide();
        }
    });

    // Prevent form submission when clicking suggestions
    $(document).on('click', '.suggestion-item', function (e) {
        // Let the link work normally
        $('#searchSuggestions').hide();
    });

    // Newsletter Subscription
    $('#newsletterForm').on('submit', function (e) {
        e.preventDefault();
        const email = $(this).find('input[name="email"]').val();
        const csrfToken = $(this).find('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            url: '/subscribe/',
            method: 'POST',
            data: {
                'email': email,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (data) {
                if (data.success) {
                    showNotification('success', data.message);
                    $('#newsletterForm')[0].reset();
                } else {
                    showNotification('error', 'Subscription failed. Please try again.');
                }
            },
            error: function () {
                showNotification('error', 'An error occurred. Please try again.');
            }
        });
    });

    // Cart Update
    $('.cart-quantity-input').on('change', function () {
        const itemId = $(this).data('item-id');
        const quantity = $(this).val();
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            url: `/cart/update/${itemId}/`,
            method: 'POST',
            data: {
                'quantity': quantity,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (data) {
                if (data.success) {
                    location.reload();
                } else {
                    showNotification('error', data.message);
                }
            }
        });
    });

    // Apply Coupon (Checkout)
    $('#applyCouponBtn').on('click', function () {
        const couponCode = $('#couponCode').val();
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        if (!couponCode) {
            showNotification('warning', 'Please enter a coupon code first.');
            return;
        }

        $.ajax({
            url: '/apply-coupon/',
            method: 'POST',
            data: {
                'coupon_code': couponCode,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (data) {
                if (data.success) {
                    showNotification('success', data.message);
                    $('#discountAmount')
                        .text(`₹${data.discount}`)
                        .attr('data-value', data.discount);
                    // Recalculate total
                    updateTotal();
                } else {
                    showNotification('error', data.message);
                    $('#discountAmount')
                        .text('₹0.00')
                        .attr('data-value', '0');
                    updateTotal();
                }
            }
        });
    });

    // Recalculate total on checkout page
    function updateTotal() {
        const subtotal = parseFloat($('#subtotalAmount').data('value')) || 0;
        const shipping = parseFloat($('#shippingAmount').data('value')) || 0;
        const tax = parseFloat($('#taxAmount').data('value')) || 0;
        const discount = parseFloat($('#discountAmount').data('value')) || 0;

        const total = subtotal + shipping + tax - discount;
        if (!isNaN(total) && $('#totalAmount').length) {
            $('#totalAmount').text(`₹${total.toFixed(2)}`);
        }
    }

    // Notification System
    function showNotification(type, message) {
        const alertClass = type === 'success' ? 'alert-success' :
            type === 'error' ? 'alert-error' :
                type === 'warning' ? 'alert-warning' : 'alert-info';

        const icon = type === 'success' ? 'check-circle' :
            type === 'error' ? 'exclamation-circle' :
                type === 'warning' ? 'exclamation-triangle' : 'info-circle';

        const notification = $(`
            <div class="alert ${alertClass}" style="position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 300px; animation: slideInRight 0.3s ease;">
                <i class="fas fa-${icon}"></i>
                ${message}
            </div>
        `);

        $('body').append(notification);

        setTimeout(function () {
            notification.fadeOut(300, function () {
                $(this).remove();
            });
        }, 3000);
    }

    // Image Gallery (Product Detail)
    $('.product-thumbnail').on('click', function () {
        const newSrc = $(this).data('image');
        $('#mainProductImage').attr('src', newSrc);
        $('.product-thumbnail').removeClass('active');
        $(this).addClass('active');
    });

    // Quantity Selector
    $('.qty-btn-minus').on('click', function () {
        const input = $(this).siblings('.qty-input');
        const currentVal = parseInt(input.val());
        if (currentVal > 1) {
            input.val(currentVal - 1).trigger('change');
        }
    });

    $('.qty-btn-plus').on('click', function () {
        const input = $(this).siblings('.qty-input');
        const currentVal = parseInt(input.val());
        const maxVal = parseInt(input.attr('max'));
        if (currentVal < maxVal) {
            input.val(currentVal + 1).trigger('change');
        }
    });

    // Smooth Scroll
    $('a[href^="#"]').on('click', function (e) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 800);
        }
    });

    // Dropdown Menu
    $('.dropdown').hover(
        function () {
            $(this).find('.dropdown-menu').stop(true, true).fadeIn(200);
        },
        function () {
            $(this).find('.dropdown-menu').stop(true, true).fadeOut(200);
        }
    );

    // Update Cart Count
    function updateCartCount() {
        $.ajax({
            url: '/api/cart-count/',
            success: function (data) {
                $('#cartCount').text(data.count);
            }
        });
    }

    // Initialize
    if ($('#cartCount').length) {
        // updateCartCount();
    }

    // Add to Cart Animation
    $('.btn-add-to-cart').on('click', function (e) {
        const btn = $(this);
        const originalText = btn.html();

        btn.html('<i class="fas fa-spinner fa-spin"></i> Adding...');
        btn.prop('disabled', true);

        setTimeout(function () {
            btn.html('<i class="fas fa-check"></i> Added!');
            setTimeout(function () {
                btn.html(originalText);
                btn.prop('disabled', false);
            }, 1000);
        }, 500);
    });

    // Star Rating
    $('.star-rating').on('click', '.star', function () {
        const rating = $(this).data('rating');
        $('#ratingInput').val(rating);

        $(this).parent().find('.star').each(function (index) {
            if (index < rating) {
                $(this).removeClass('far').addClass('fas');
            } else {
                $(this).removeClass('fas').addClass('far');
            }
        });
    });

    // Filter Toggle (Mobile)
    $('#filterToggle').on('click', function () {
        $('.filter-sidebar').toggleClass('show');
    });

    // Price Range Slider
    if ($('#priceRange').length) {
        const priceRange = $('#priceRange');
        const minPrice = $('#minPrice');
        const maxPrice = $('#maxPrice');

        priceRange.on('input', function () {
            const value = $(this).val();
            maxPrice.text(`₹${value}`);
        });
    }
});

// Add CSS for dropdown menu
const style = document.createElement('style');
style.textContent = `
    .dropdown {
        position: relative;
    }
    
    .dropdown-menu {
        display: none;
        position: absolute;
        top: 100%;
        right: 0;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        box-shadow: var(--shadow-lg);
        min-width: 200px;
        margin-top: 0.5rem;
        z-index: 1000;
    }
    
    .dropdown-menu a {
        display: block;
        padding: 0.75rem 1rem;
        color: var(--text-secondary);
        transition: var(--transition-fast);
        border-bottom: 1px solid var(--border-color);
    }
    
    .dropdown-menu a:last-child {
        border-bottom: none;
    }
    
    .dropdown-menu a:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        padding-left: 1.25rem;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
