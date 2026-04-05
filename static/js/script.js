document.addEventListener('DOMContentLoaded', function() {
    // ==================== CONSTANTES ET VARIABLES GLOBALES ====================
    const CART_KEY = 'luxious_beauty_cart';
    const WISHLIST_KEY = 'luxious_beauty_wishlist';
    let cartItems = JSON.parse(localStorage.getItem(CART_KEY)) || [];
    let wishlistItems = JSON.parse(localStorage.getItem(WISHLIST_KEY)) || [];

    // ==================== INITIALISATION DES COMPOSANTS ====================
    initAccessibility();
    initSliders();
    initTabs();
    initProductCategories();
    initMobileMenu();
    initCart();
    initWishlist();
    initModals();
    initQuickView();
    initQuickBook();
    initNewsletter();

    // ==================== FONCTIONS D'INITIALISATION ====================

    // Accessibilité
    function initAccessibility() {
        // Contraste élevé
        const contrastBtn = document.getElementById('high-contrast');
        if (contrastBtn) {
            contrastBtn.addEventListener('click', toggleContrast);
        }

        // Taille du texte
        const fontIncrease = document.getElementById('font-increase');
        const fontDecrease = document.getElementById('font-decrease');
        
        if (fontIncrease && fontDecrease) {
            fontIncrease.addEventListener('click', () => adjustFontSize(1));
            fontDecrease.addEventListener('click', () => adjustFontSize(-1));
        }
    }

    // Sliders
    function initSliders() {
        // Hero Slider
        const heroSlider = new Swiper('.hero-slider', {
            loop: true,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });

        // Promo Slider
        const promoSlider = new Swiper('.promo-slider', {
            slidesPerView: 1,
            spaceBetween: 20,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            breakpoints: {
                640: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
                1280: {
                    slidesPerView: 4,
                }
            }
        });

        // Brands Slider
        const brandsSlider = new Swiper('.brands-slider', {
            slidesPerView: 2,
            spaceBetween: 20,
            autoplay: {
                delay: 2500,
                disableOnInteraction: false,
            },
            breakpoints: {
                640: {
                    slidesPerView: 3,
                },
                768: {
                    slidesPerView: 4,
                },
                1024: {
                    slidesPerView: 5,
                },
                1280: {
                    slidesPerView: 6,
                }
            }
        });

        // Testimonials Slider
        const testimonialsSlider = new Swiper('.testimonials-slider', {
            loop: true,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            autoplay: {
                delay: 6000,
                disableOnInteraction: false,
            },
            breakpoints: {
                640: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 3,
                    spaceBetween: 30,
                }
            }
        });
    }

    // Onglets de services
    function initTabs() {
        const tabButtons = document.querySelectorAll('[role="tab"]');
        const tabPanels = document.querySelectorAll('[role="tabpanel"]');

        if (tabButtons.length === 0 || tabPanels.length === 0) return;

        // Fonction pour gérer le clic sur un onglet
        function handleTabClick(event) {
            const clickedTab = event.currentTarget;
            const tabId = clickedTab.getAttribute('data-tab');
            
            // Désactiver tous les onglets
            tabButtons.forEach(tab => {
                tab.setAttribute('aria-selected', 'false');
                tab.classList.remove('active');
            });
            
            // Activer l'onglet cliqué
            clickedTab.setAttribute('aria-selected', 'true');
            clickedTab.classList.add('active');
            
            // Masquer tous les panels
            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                panel.setAttribute('hidden', '');
            });
            
            // Afficher le panel correspondant
            const activePanel = document.getElementById(`${tabId}-tab`);
            if (activePanel) {
                activePanel.classList.add('active');
                activePanel.removeAttribute('hidden');
            }
        }

        // Ajouter les écouteurs d'événements
        tabButtons.forEach(tab => {
            tab.addEventListener('click', handleTabClick);
        });
    }

    // Catégories de produits
    function initProductCategories() {
        const categoryButtons = document.querySelectorAll('.product-categories [role="tab"]');
        
        if (categoryButtons.length === 0) return;

        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Retirer la classe active de tous les boutons
                categoryButtons.forEach(btn => {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-selected', 'false');
                });
                
                // Ajouter la classe active au bouton cliqué
                this.classList.add('active');
                this.setAttribute('aria-selected', 'true');
                
                // Ici vous pourriez ajouter le code pour filtrer les produits
                // Par exemple, en fonction d'un attribut data-category
                const category = this.textContent.trim();
                filterProducts(category);
            });
        });
    }

    // Menu mobile
    function initMobileMenu() {
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        const mainNav = document.querySelector('.main-nav');
        
        if (menuToggle && mainNav) {
            menuToggle.addEventListener('click', function() {
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                this.setAttribute('aria-expanded', !isExpanded);
                mainNav.classList.toggle('active');
                document.body.classList.toggle('menu-open');
            });
        }
    }

    // Panier
    function initCart() {
        updateCartCount();
        
        // Ajouter au panier
        const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productCard = this.closest('.product-card');
                addToCart(productCard);
            });
        });
    }

    // Liste de souhaits
    function initWishlist() {
        const wishlistButtons = document.querySelectorAll('.product-wishlist');
        wishlistButtons.forEach(button => {
            // Vérifier si le produit est déjà dans la liste de souhaits
            const productCard = button.closest('.product-card');
            const productId = productCard ? productCard.querySelector('.quick-view-btn').getAttribute('data-product') : null;
            
            if (productId && wishlistItems.includes(productId)) {
                button.innerHTML = '<i class="fas fa-heart"></i>';
                button.classList.add('active');
            }
            
            button.addEventListener('click', function() {
                toggleWishlist(productCard);
            });
        });
    }

    // Modales
    function initModals() {
        // Fermer les modales lorsqu'on clique sur le fond ou le bouton de fermeture
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === this || e.target.classList.contains('close-modal')) {
                    closeModal(this.id);
                }
            });
        });
        
        // Empêcher la propagation du clic à l'intérieur de la modale
        document.querySelectorAll('.modal-content').forEach(content => {
            content.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
    }

    // Vue rapide des produits
    function initQuickView() {
        const quickViewButtons = document.querySelectorAll('.quick-view-btn');
        quickViewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-product');
                openQuickView(productId);
            });
        });
    }

    // Réservation rapide
    function initQuickBook() {
        const quickBookButtons = document.querySelectorAll('.quick-book-btn');
        quickBookButtons.forEach(button => {
            button.addEventListener('click', function() {
                const serviceId = this.getAttribute('data-service');
                openQuickBook(serviceId);
            });
        });
    }

    // Newsletter
    function initNewsletter() {
        const newsletterForm = document.querySelector('.newsletter-form');
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const emailInput = this.querySelector('input[type="email"]');
                const consentCheckbox = this.querySelector('input[type="checkbox"]');
                
                if (emailInput && consentCheckbox) {
                    if (consentCheckbox.checked) {
                        // Ici vous pourriez envoyer l'email à votre serveur
                        showToast('Merci pour votre inscription à notre newsletter !', 'success');
                        emailInput.value = '';
                        consentCheckbox.checked = false;
                    } else {
                        showToast('Veuillez accepter de recevoir nos offres.', 'error');
                    }
                }
            });
        }
    }

    // ==================== FONCTIONNALITÉS PRINCIPALES ====================

    // Accessibilité - Contraste élevé
    function toggleContrast() {
        document.body.classList.toggle('high-contrast');
        const isHighContrast = document.body.classList.contains('high-contrast');
        localStorage.setItem('highContrast', isHighContrast);
    }

    // Accessibilité - Taille du texte
    function adjustFontSize(change) {
        const html = document.documentElement;
        const currentSize = parseFloat(window.getComputedStyle(html, null).getPropertyValue('font-size'));
        const newSize = currentSize + (change * 1);
        
        // Limites min et max
        if (newSize >= 12 && newSize <= 24) {
            html.style.fontSize = newSize + 'px';
            localStorage.setItem('fontSize', newSize);
        }
    }

    // Filtrage des produits
    function filterProducts(category) {
        const products = document.querySelectorAll('.product-card');
        
        products.forEach(product => {
            // Dans une implémentation réelle, vous auriez un attribut data-category sur chaque produit
            // Pour cet exemple, nous allons simplement tout afficher si "Tous" est sélectionné
            if (category === 'Tous') {
                product.style.display = 'block';
            } else {
                // Ici vous filtreriez selon la catégorie
                // Pour l'exemple, nous affichons tous les produits
                product.style.display = 'block';
            }
        });
    }

    // Panier - Ajouter un produit
    function addToCart(productCard) {
        if (!productCard) return;
        
        const productId = productCard.querySelector('.quick-view-btn').getAttribute('data-product');
        const productTitle = productCard.querySelector('.product-title').textContent;
        const productPrice = parseFloat(productCard.querySelector('.current-price').textContent.replace(',', '.').replace(/[^\d.-]/g, ''));
        const productImage = productCard.querySelector('.product-image img').src;
        
        // Vérifier si le produit est déjà dans le panier
        const existingItem = cartItems.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cartItems.push({
                id: productId,
                title: productTitle,
                price: productPrice,
                image: productImage,
                quantity: 1
            });
        }
        
        // Mettre à jour le stockage local
        localStorage.setItem(CART_KEY, JSON.stringify(cartItems));
        
        // Mettre à jour le compteur du panier
        updateCartCount();
        
        // Afficher une notification
        showToast(`${productTitle} a été ajouté à votre panier`, 'success');
        
        // Ouvrir le panier (optionnel)
        // openCartModal();
    }

    // Panier - Mettre à jour le compteur
    function updateCartCount() {
        const cartCountElements = document.querySelectorAll('.cart-count');
        const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
        
        cartCountElements.forEach(element => {
            element.textContent = totalItems;
        });
    }

    // Panier - Ouvrir la modale du panier
    function openCartModal() {
        const modal = document.getElementById('cart-modal');
        if (!modal) return;
        
        const cartItemsContainer = modal.querySelector('.cart-items');
        const cartTotalElement = modal.querySelector('.cart-total');
        
        // Vider le conteneur
        cartItemsContainer.innerHTML = '';
        
        // Si le panier est vide
        if (cartItems.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart">Votre panier est vide</p>';
            cartTotalElement.textContent = '0,0000 FCFA';
            return;
        }
        
        // Ajouter chaque article du panier
        let total = 0;
        
        cartItems.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'cart-item';
            itemElement.innerHTML = `
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.title}">
                </div>
                <div class="cart-item-details">
                    <h4>${item.title}</h4>
                    <div class="cart-item-price">${item.price.toFixed(2)}00 FCFA</div>
                    <div class="cart-item-quantity">
                        <button class="quantity-btn minus" data-id="${item.id}">-</button>
                        <span>${item.quantity}</span>
                        <button class="quantity-btn plus" data-id="${item.id}">+</button>
                    </div>
                </div>
                <button class="remove-item" data-id="${item.id}" aria-label="Supprimer">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            
            cartItemsContainer.appendChild(itemElement);
            total += item.price * item.quantity;
        });
        
        // Mettre à jour le total
        cartTotalElement.textContent = total.toFixed(2) + '00 FCFA';
        
        // Ajouter les écouteurs d'événements pour les boutons
        modal.querySelectorAll('.quantity-btn.minus').forEach(btn => {
            btn.addEventListener('click', function() {
                updateCartItemQuantity(this.getAttribute('data-id'), -1);
            });
        });
        
        modal.querySelectorAll('.quantity-btn.plus').forEach(btn => {
            btn.addEventListener('click', function() {
                updateCartItemQuantity(this.getAttribute('data-id'), 1);
            });
        });
        
        modal.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', function() {
                removeCartItem(this.getAttribute('data-id'));
            });
        });
        
        // Ouvrir la modale
        openModal('cart-modal');
    }

    // Panier - Mettre à jour la quantité d'un article
    function updateCartItemQuantity(productId, change) {
        const itemIndex = cartItems.findIndex(item => item.id === productId);
        
        if (itemIndex !== -1) {
            cartItems[itemIndex].quantity += change;
            
            // Supprimer si la quantité est <= 0
            if (cartItems[itemIndex].quantity <= 0) {
                cartItems.splice(itemIndex, 1);
            }
            
            // Mettre à jour le stockage local
            localStorage.setItem(CART_KEY, JSON.stringify(cartItems));
            
            // Mettre à jour l'affichage
            updateCartCount();
            openCartModal(); // Rafraîchir la modale
        }
    }

    // Panier - Supprimer un article
    function removeCartItem(productId) {
        cartItems = cartItems.filter(item => item.id !== productId);
        
        // Mettre à jour le stockage local
        localStorage.setItem(CART_KEY, JSON.stringify(cartItems));
        
        // Mettre à jour l'affichage
        updateCartCount();
        openCartModal(); // Rafraîchir la modale
        
        showToast('Produit supprimé du panier', 'info');
    }

    // Liste de souhaits - Basculer un produit
    function toggleWishlist(productCard) {
        if (!productCard) return;
        
        const productId = productCard.querySelector('.quick-view-btn').getAttribute('data-product');
        const wishlistButton = productCard.querySelector('.product-wishlist');
        
        // Vérifier si le produit est déjà dans la liste
        const index = wishlistItems.indexOf(productId);
        
        if (index === -1) {
            // Ajouter à la liste
            wishlistItems.push(productId);
            wishlistButton.innerHTML = '<i class="fas fa-heart"></i>';
            wishlistButton.classList.add('active');
            showToast('Produit ajouté à vos favoris', 'success');
        } else {
            // Retirer de la liste
            wishlistItems.splice(index, 1);
            wishlistButton.innerHTML = '<i class="far fa-heart"></i>';
            wishlistButton.classList.remove('active');
            showToast('Produit retiré de vos favoris', 'info');
        }
        
        // Mettre à jour le stockage local
        localStorage.setItem(WISHLIST_KEY, JSON.stringify(wishlistItems));
    }

    // Modales - Ouvrir une modale
   // Modales - Ouvrir une modale
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.classList.add('modal-open');
        }
    }

    // Modales - Fermer une modale
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            document.body.classList.remove('modal-open');
        }
    }

    // Vue rapide - Ouvrir la vue rapide d'un produit
    function openQuickView(productId) {
        // Dans une implémentation réelle, vous pourriez faire une requête AJAX
        // pour obtenir les détails complets du produit. Pour cet exemple,
        // nous allons utiliser des données factices.
        
        const mockProducts = {
            '1': {
                title: 'Crème Hydratante Intense',
                brand: 'Marque Luxe',
                price: 59.90,
                oldPrice: 75.00,
                description: 'Une crème hydratante riche et nourrissante pour les peaux sèches à très sèches. Formulée avec de l\'acide hyaluronique et des céramides pour une hydratation intense et durable.',
                image: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                rating: 4.5,
                reviews: 128,
                details: '<ul><li>Hydratation 72h</li><li>Peaux sèches à très sèches</li><li>Sans parfum</li><li>Testé dermatologiquement</li></ul>'
            },
            '2': {
                title: 'Sérum Vitaminé Éclat',
                brand: 'Pure Beauty',
                price: 45.00,
                description: 'Un sérum léger à base de vitamines C et E pour un teint éclatant et uniforme. Réduit les taches pigmentaires et prévient les signes de vieillissement.',
                image: 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                rating: 4,
                reviews: 87,
                details: '<ul><li>Vitamines C et E</li><li>Uniformise le teint</li><li>Texture légère</li><li>Adapté à tous les types de peau</li></ul>'
            },
            '3': {
                title: 'Masque Doré Anti-Âge',
                brand: 'Gold Therapy',
                price: 59.90,
                oldPrice: 79.90,
                description: 'Un masque luxueux infusé à l\'or 24 carats et au collagène pour un effet lifting immédiat et une peau visiblement plus jeune.',
                image: 'https://images.unsplash.com/photo-1595341595379-cf0f2f6ddd9a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                rating: 5,
                reviews: 215,
                details: '<ul><li>Or 24 carats</li><li>Effet lifting immédiat</li><li>Collagène marin</li><li>Utilisation 1-2 fois par semaine</li></ul>'
            },
            '4': {
                title: 'Huile de Massage Relaxante',
                brand: 'Essence Divine',
                price: 39.90,
                description: 'Une huile de massage aux huiles essentielles de lavande et de camomille pour détendre les muscles et apaiser l\'esprit. Parfaite pour un massage relaxant ou une routine d\'auto-massage.',
                image: 'https://images.unsplash.com/photo-1600956054489-a23507c64a36?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80',
                rating: 4.5,
                reviews: 142,
                details: '<ul><li>Huiles essentielles de lavande et camomille</li><li>Texture non grasse</li><li>Absorption rapide</li><li>Convient pour le corps et le visage</li></ul>'
            }
        };
        
        const product = mockProducts[productId];
        if (!product) return;
        
        const modal = document.getElementById('quick-view-modal');
        if (!modal) return;
        
        // Remplir la modale avec les données du produit
        modal.querySelector('.product-image img').src = product.image;
        modal.querySelector('.product-image img').alt = product.title;
        modal.querySelector('.product-title').textContent = product.title;
        modal.querySelector('.product-brand').textContent = product.brand;
        
        // Gérer le prix et l'ancien prix
        const priceElement = modal.querySelector('.product-price .current-price');
        priceElement.textContent = product.price.toFixed(2) + '00 FCFA';
        
        const oldPriceElement = modal.querySelector('.product-price .old-price');
        if (product.oldPrice) {
            oldPriceElement.textContent = product.oldPrice.toFixed(2) + '00 FCFA';
            oldPriceElement.style.display = 'inline';
        } else {
            oldPriceElement.style.display = 'none';
        }
        
        // Évaluation
        const ratingElement = modal.querySelector('.product-rating');
        ratingElement.innerHTML = '';
        ratingElement.setAttribute('aria-label', `${product.rating} étoiles sur 5`);
        
        // Ajouter les étoiles pleines
        for (let i = 1; i <= Math.floor(product.rating); i++) {
            ratingElement.innerHTML += '<i class="fas fa-star" aria-hidden="true"></i>';
        }
        
        // Ajouter une demi-étoile si nécessaire
        if (product.rating % 1 >= 0.5) {
            ratingElement.innerHTML += '<i class="fas fa-star-half-alt" aria-hidden="true"></i>';
        }
        
        // Ajouter les étoiles vides
        const emptyStars = 5 - Math.ceil(product.rating);
        for (let i = 0; i < emptyStars; i++) {
            ratingElement.innerHTML += '<i class="far fa-star" aria-hidden="true"></i>';
        }
        
        // Ajouter le nombre d'avis
        ratingElement.innerHTML += `<span class="rating-count">(${product.reviews})</span>`;
        
        // Description et détails
        modal.querySelector('.product-description').innerHTML = product.description;
        modal.querySelector('.product-details').innerHTML = product.details;
        
        // Bouton "Ajouter au panier"
        const addToCartBtn = modal.querySelector('.add-to-cart-btn');
        addToCartBtn.setAttribute('data-product-id', productId);
        addToCartBtn.addEventListener('click', function() {
            // Trouver la carte du produit correspondante
            const productCard = document.querySelector(`.quick-view-btn[data-product="${productId}"]`).closest('.product-card');
            addToCart(productCard);
            closeModal('quick-view-modal');
        });
        
        // Ouvrir la modale
        openModal('quick-view-modal');
    }

    // Réservation rapide - Ouvrir le formulaire de réservation
    function openQuickBook(serviceId) {
        // Dans une implémentation réelle, vous pourriez faire une requête AJAX
        // pour obtenir les détails du service. Pour cet exemple,
        // nous allons utiliser des données factices.
        
        const mockServices = {
            '1': {
                title: 'Soin Hydratant Intense',
                duration: '60 min',
                price: 89,
                description: 'Un soin profondément hydratant pour les peaux sèches, avec un masque nourrissant et un massage du visage relaxant.'
            },
            '2': {
                title: 'Soin Anti-âge Premium',
                duration: '75 min',
                price: 120,
                description: 'Redensifie et repulpe la peau en profondeur avec des actifs haute performance et des techniques de massage spécialisées.'
            },
            '3': {
                title: 'Soin Éclat Instantané',
                duration: '45 min',
                price: 65,
                description: 'Un teint frais et lumineux en une seule séance grâce à des peelings doux et des soins éclaircissants.'
            }
        };
        
        const service = mockServices[serviceId];
        if (!service) return;
        
        const modal = document.getElementById('quick-book-modal');
        if (!modal) return;
        
        // Remplir la modale avec les données du service
        modal.querySelector('.service-title').textContent = service.title;
        modal.querySelector('.service-duration').textContent = service.duration;
        modal.querySelector('.service-price').textContent = service.price + '00 FCFA';
        modal.querySelector('.service-description').textContent = service.description;
        
        // Configurer le formulaire de réservation
        const bookingForm = modal.querySelector('.booking-form');
        bookingForm.setAttribute('data-service-id', serviceId);
        
        // Ouvrir la modale
        openModal('quick-book-modal');
    }

    // Afficher une notification toast
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Animation d'apparition
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Disparaître après 3 secondes
        setTimeout(() => {
            toast.classList.remove('show');
            
            // Supprimer après l'animation
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // ==================== GESTION DES ÉVÉNEMENTS ====================

    // Lier le panier dans la navigation
    document.querySelectorAll('a[href="#"], .cart-count').forEach(element => {
        element.addEventListener('click', function(e) {
            if (this.classList.contains('cart-count') || this.parentElement.classList.contains('cart-count')) {
                e.preventDefault();
                openCartModal();
            }
        });
    });
});

// ==================== STYLES DYNAMIQUES ====================

// Ajouter des styles dynamiques pour les fonctionnalités JS
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    /* Styles pour les modales */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        z-index: 1000;
        overflow-y: auto;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .modal.show {
        opacity: 1;
    }
    
    .modal-content {
        background: white;
        margin: 5% auto;
        padding: 20px;
        width: 90%;
        max-width: 800px;
        border-radius: 8px;
        position: relative;
        transform: translateY(-20px);
        transition: transform 0.3s;
    }
    
    .modal.show .modal-content {
        transform: translateY(0);
    }
    
    .close-modal {
        position: absolute;
        top: 15px;
        right: 15px;
        font-size: 24px;
        cursor: pointer;
        background: none;
        border: none;
    }
    
    /* Styles pour le panier */
    .cart-item {
        display: flex;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid #eee;
    }
    
    .cart-item-image {
        width: 80px;
        margin-right: 15px;
    }
    
    .cart-item-image img {
        width: 100%;
        height: auto;
    }
    
    .cart-item-details {
        flex-grow: 1;
    }
    
    .cart-item-quantity {
        display: flex;
        align-items: center;
        margin: 5px 0;
    }
    
    .quantity-btn {
        width: 25px;
        height: 25px;
        border: 1px solid #ddd;
        background: #f9f9f9;
        cursor: pointer;
    }
    
    .cart-item-quantity span {
        margin: 0 10px;
    }
    
    .remove-item {
        background: none;
        border: none;
        color: #ff6b6b;
        cursor: pointer;
        font-size: 16px;
    }
    
    /* Styles pour les notifications toast */
    .toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        background: #333;
        color: white;
        border-radius: 4px;
        opacity: 0;
        transition: opacity 0.3s, bottom 0.3s;
        z-index: 1100;
    }
    
    .toast.show {
        opacity: 1;
        bottom: 30px;
    }
    
    .toast-success {
        background: #4CAF50;
    }
    
    .toast-error {
        background: #F44336;
    }
    
    .toast-info {
        background: #2196F3;
    }
    
    /* Menu mobile ouvert */
    body.menu-open {
        overflow: hidden;
    }
    
    /* Modale ouverte */
    body.modal-open {
        overflow: hidden;
    }
    
    /* Contraste élevé */
    body.high-contrast {
        --primary-color: #000;
        --secondary-color: #fff;
        --text-color: #000;
        --background-color: #fff;
        --accent-color: #ffff00;
    }
    
    body.high-contrast * {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }
    
    body.high-contrast a,
    body.high-contrast button {
        border: 2px solid var(--text-color) !important;
    }
    
    body.high-contrast .btn {
        background-color: var(--accent-color) !important;
        color: #000 !important;
    }
`;
document.head.appendChild(dynamicStyles);

// ==================== MODALES MANQUANTES DANS LE HTML ====================

// Créer les modales manquantes si elles n'existent pas déjà
if (!document.getElementById('cart-modal')) {
    const cartModal = document.createElement('div');
    cartModal.id = 'cart-modal';
    cartModal.className = 'modal';
    cartModal.innerHTML = `
        <link rel="stylesheet" href="https://unpkg.com/swiper/swiper-bundle.min.css" />
        <script src="https://unpkg.com/swiper/swiper-bundle.min.js"></script>
        <script src="script.js"></script>

        <div class="modal-content">
            <button class="close-modal">&times;</button>
            <h2>Votre Panier</h2>
            <div class="cart-items"></div>
            <div class="cart-summary">
                <div class="cart-total">0,0000 FCFA</div>
                <button class="btn checkout-btn">Passer la commande</button>
            </div>
        </div>
    `;
    document.body.appendChild(cartModal);
}

if (!document.getElementById('quick-view-modal')) {
    const quickViewModal = document.createElement('div');
    quickViewModal.id = 'quick-view-modal';
    quickViewModal.className = 'modal';
    quickViewModal.innerHTML = `
        <div class="modal-content">
            <button class="close-modal">&times;</button>
            <div class="product-details-container">
                <div class="product-image">
                    <img src="" alt="">
                </div>
                <div class="product-info">
                    <span class="product-brand"></span>
                    <h3 class="product-title"></h3>
                    <div class="product-rating"></div>
                    <div class="product-price">
                        <span class="current-price"></span>
                        <span class="old-price"></span>
                    </div>
                    <p class="product-description"></p>
                    <div class="product-actions">
                        <button class="add-to-cart-btn">Ajouter au panier</button>
                    </div>
                </div>
            </div>
            <div class="product-specs">
                <h4>Détails du produit</h4>
                <div class="product-details"></div>
            </div>
        </div>
    `;
    document.body.appendChild(quickViewModal);
}

if (!document.getElementById('quick-book-modal')) {
    const quickBookModal = document.createElement('div');
    quickBookModal.id = 'quick-book-modal';
    quickBookModal.className = 'modal';
    quickBookModal.innerHTML = `
        <div class="modal-content">
            <button class="close-modal">&times;</button>
            <h2>Réserver <span class="service-title"></span></h2>
            <div class="service-meta">
                <span class="service-duration"></span>
                <span class="service-price"></span>
            </div>
            <p class="service-description"></p>
            <form class="booking-form">
                <div class="form-group">
                    <label for="booking-date">Date</label>
                    <input type="date" id="booking-date" required>
                </div>
                <div class="form-group">
                    <label for="booking-time">Heure</label>
                    <input type="time" id="booking-time" required>
                </div>
                <div class="form-group">
                    <label for="booking-name">Nom complet</label>
                    <input type="text" id="booking-name" required>
                </div>
                <div class="form-group">
                    <label for="booking-email">Email</label>
                    <input type="email" id="booking-email" required>
                </div>
                <div class="form-group">
                    <label for="booking-phone">Téléphone</label>
                    <input type="tel" id="booking-phone" required>
                </div>
                <button type="submit" class="btn">Confirmer la réservation</button>
            </form>
        </div>
    `;
    document.body.appendChild(quickBookModal);
}