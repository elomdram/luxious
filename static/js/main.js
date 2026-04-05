(function() {
    'use strict';
    
    // Utility functions
    const AppUtils = {
        // Format price with thousands separator
        formatPrice: function(price) {
            return new Intl.NumberFormat('fr-FR', {
                maximumFractionDigits: 0,
                minimumFractionDigits: 0
            }).format(price) + ' FCFA';
        },
        
        // Parse price string to number
        parsePrice: function(priceStr) {
            return parseFloat(priceStr.replace(/[^\d]/g, '')) || 0;
        },
        
        // Safe number conversion
        toNumber: function(value) {
            const num = parseFloat(value);
            return isNaN(num) ? 0 : num;
        },
        
        // Show notification
        showNotification: function(message, type = 'success') {
            // Check if notification container exists
            let container = document.getElementById('notification-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'notification-container';
                container.className = 'fixed top-4 right-4 z-50 space-y-2';
                document.body.appendChild(container);
            }
            
            const notification = document.createElement('div');
            notification.className = `px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 ${
                type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
            }`;
            notification.innerHTML = message;
            
            container.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 3000);
        },
        
        // Update cart count in header
        updateCartCount: function(count) {
            document.querySelectorAll('.cart-count, [data-cart-count]').forEach(el => {
                el.textContent = count;
                if (count === 0) {
                    el.classList.add('hidden');
                } else {
                    el.classList.remove('hidden');
                }
            });
        }
    };
    
    // Fonction pour attendre que le DOM soit chargé
    function initApp() {
        console.log('App initialized');
        
        // Mobile Menu Toggle
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', function(e) {
                e.preventDefault();
                const mobileMenu = document.getElementById('mobile-menu');
                if (mobileMenu) {
                    mobileMenu.classList.toggle('hidden');
                }
            });
        }
        
        // User Menu Toggle
        const userMenuToggle = document.getElementById('user-menu-toggle');
        if (userMenuToggle) {
            userMenuToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const userMenu = document.getElementById('user-menu');
                if (userMenu) {
                    userMenu.classList.toggle('hidden');
                }
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(event) {
                const userMenu = document.getElementById('user-menu');
                if (userMenu && userMenuToggle && !userMenu.classList.contains('hidden')) {
                    if (!userMenuToggle.contains(event.target) && !userMenu.contains(event.target)) {
                        userMenu.classList.add('hidden');
                    }
                }
            });
        }
        
        // Search Toggle
        const searchToggle = document.getElementById('search-toggle');
        if (searchToggle) {
            searchToggle.addEventListener('click', function(e) {
                e.preventDefault();
                const searchBar = document.getElementById('search-bar');
                if (searchBar) {
                    searchBar.classList.toggle('hidden');
                    if (!searchBar.classList.contains('hidden')) {
                        const searchInput = searchBar.querySelector('input');
                        if (searchInput) {
                            setTimeout(function() {
                                searchInput.focus();
                            }, 100);
                        }
                    }
                }
            });
        }
        
        // Back to Top Button
        const backToTop = document.getElementById('back-to-top');
        if (backToTop) {
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300) {
                    backToTop.classList.remove('hidden');
                } else {
                    backToTop.classList.add('hidden');
                }
            });
            
            backToTop.addEventListener('click', function(e) {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
        
        // Newsletter Form
        const newsletterForm = document.getElementById('newsletter-form');
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const emailInput = this.querySelector('input[name="email"]');
                const messageDiv = document.getElementById('newsletter-message');
                const csrfToken = this.querySelector('input[name="csrfmiddlewaretoken"]');
                
                if (!emailInput || !emailInput.value) {
                    if (messageDiv) {
                        messageDiv.innerHTML = '<div class="text-red-500">Veuillez entrer une adresse email.</div>';
                    }
                    return;
                }
                
                const email = emailInput.value;
                const token = csrfToken ? csrfToken.value : '';
                
                fetch('/api/newsletter/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': token,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ email: email })
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (messageDiv) {
                        if (data.success) {
                            messageDiv.innerHTML = '<div class="text-green-500">' + (data.message || 'Merci de vous être abonné!') + '</div>';
                            if (emailInput) {
                                emailInput.value = '';
                            }
                        } else {
                            messageDiv.innerHTML = '<div class="text-red-500">' + (data.message || 'Erreur lors de l\'abonnement') + '</div>';
                        }
                    }
                })
                .catch(function(error) {
                    console.error('Newsletter error:', error);
                    if (messageDiv) {
                        messageDiv.innerHTML = '<div class="text-red-500">Une erreur est survenue. Veuillez réessayer.</div>';
                    }
                });
            });
        }
        
        // Add to cart functionality
        const addToCartForms = document.querySelectorAll('.add-to-cart-form');
        if (addToCartForms.length > 0) {
            addToCartForms.forEach(function(form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(this);
                    const data = {};
                    formData.forEach(function(value, key) {
                        data[key] = value;
                    });
                    
                    // Convert quantity to number
                    if (data.quantity) {
                        data.quantity = parseInt(data.quantity) || 1;
                    }
                    
                    fetch('/api/cart/add/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': data.csrfmiddlewaretoken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(function(response) {
                        return response.json();
                    })
                    .then(function(data) {
                        if (data.success) {
                            // Update cart count
                            AppUtils.updateCartCount(data.cart_items_count || 0);
                            AppUtils.showNotification(data.message || 'Article ajouté au panier', 'success');
                            
                            // Optionally animate the cart icon
                            const cartIcon = document.querySelector('.fa-shopping-cart');
                            if (cartIcon) {
                                cartIcon.classList.add('scale-125', 'text-primary');
                                setTimeout(() => {
                                    cartIcon.classList.remove('scale-125', 'text-primary');
                                }, 200);
                            }
                        } else {
                            AppUtils.showNotification(data.message || 'Erreur lors de l\'ajout au panier', 'error');
                        }
                    })
                    .catch(function(error) {
                        console.error('Add to cart error:', error);
                        AppUtils.showNotification('Erreur lors de l\'ajout au panier', 'error');
                    });
                });
            });
        }
        
        // Quantity input handlers for product pages
        const quantityInputs = document.querySelectorAll('.quantity-input');
        quantityInputs.forEach(input => {
            const minusBtn = input.parentElement?.querySelector('.quantity-minus');
            const plusBtn = input.parentElement?.querySelector('.quantity-plus');
            
            if (minusBtn) {
                minusBtn.addEventListener('click', () => {
                    let value = parseInt(input.value) || 1;
                    if (value > 1) {
                        input.value = value - 1;
                        input.dispatchEvent(new Event('change'));
                    }
                });
            }
            
            if (plusBtn) {
                plusBtn.addEventListener('click', () => {
                    let value = parseInt(input.value) || 1;
                    const max = parseInt(input.getAttribute('max')) || Infinity;
                    if (value < max) {
                        input.value = value + 1;
                        input.dispatchEvent(new Event('change'));
                    }
                });
            }
            
            input.addEventListener('change', function() {
                let value = parseInt(this.value) || 1;
                const min = parseInt(this.getAttribute('min')) || 1;
                const max = parseInt(this.getAttribute('max')) || Infinity;
                
                if (value < min) value = min;
                if (value > max) value = max;
                
                this.value = value;
            });
        });
        
        // Toggle wishlist
        const wishlistButtons = document.querySelectorAll('.toggle-wishlist');
        if (wishlistButtons.length > 0) {
            wishlistButtons.forEach(function(button) {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const productId = this.dataset.productId;
                    const serviceId = this.dataset.serviceId;
                    const csrfToken = this.dataset.csrfToken;
                    
                    fetch('/api/wishlist/toggle/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({
                            product_id: productId,
                            service_id: serviceId
                        })
                    })
                    .then(function(response) {
                        return response.json();
                    })
                    .then(function(data) {
                        if (data.success) {
                            if (data.login_required) {
                                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                            } else {
                                if (data.added) {
                                    button.classList.add('text-red-500');
                                    button.classList.remove('text-gray-400');
                                    AppUtils.showNotification('Ajouté aux favoris', 'success');
                                } else {
                                    button.classList.remove('text-red-500');
                                    button.classList.add('text-gray-400');
                                    AppUtils.showNotification('Retiré des favoris', 'success');
                                }
                            }
                        } else {
                            AppUtils.showNotification(data.message || 'Erreur', 'error');
                        }
                    })
                    .catch(function(error) {
                        console.error('Wishlist error:', error);
                        AppUtils.showNotification('Erreur lors de l\'opération', 'error');
                    });
                });
            });
        }
        
        // Product image gallery
        const mainImage = document.getElementById('main-product-image');
        const thumbnails = document.querySelectorAll('.product-thumbnail');
        
        if (mainImage && thumbnails.length > 0) {
            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    const newSrc = this.dataset.fullImage || this.src;
                    mainImage.src = newSrc;
                    
                    // Update active state
                    thumbnails.forEach(t => t.classList.remove('border-2', 'border-primary'));
                    this.classList.add('border-2', 'border-primary');
                });
            });
        }
        
        // Quick view functionality
        const quickViewButtons = document.querySelectorAll('.quick-view-btn');
        if (quickViewButtons.length > 0) {
            quickViewButtons.forEach(btn => {
                btn.addEventListener('click', async function(e) {
                    e.preventDefault();
                    const productId = this.dataset.productId;
                    
                    try {
                        const response = await fetch(`/api/products/${productId}/quick-view/`);
                        const data = await response.json();
                        
                        if (data.success) {
                            // Show modal with product details
                            showQuickViewModal(data.product);
                        }
                    } catch (error) {
                        console.error('Quick view error:', error);
                    }
                });
            });
        }
        
        // Function to show quick view modal
        function showQuickViewModal(product) {
            // Implementation depends on your modal system
            console.log('Quick view:', product);
        }
    }
    
    // Attendre que le DOM soit chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initApp);
    } else {
        // DOM est déjà chargé
        initApp();
    }
    
    // Export utilities for use in other scripts
    window.AppUtils = AppUtils;
})();