document.addEventListener('DOMContentLoaded', function() {
    // Constantes
    const CART_KEY = 'luxious_beauty_cart';
    
    // Éléments du DOM
    const cartItemsList = document.getElementById('cart-items-list');
    const emptyCartMessage = document.querySelector('.empty-cart-message');
    const subtotalElement = document.querySelector('.subtotal');
    const totalElement = document.querySelector('.total-price');
    const discountElement = document.querySelector('.discount');
    const checkoutBtn = document.getElementById('checkout-btn');
    const cartCountElement = document.getElementById('cart-count');
    const clearCartBtn = document.getElementById('clear-cart');
    const updateCartBtn = document.getElementById('update-cart');
    const promoForm = document.getElementById('promo-form');
    const couponInput = document.querySelector('.promo-input');
    
    // Variables
    let cartItems = JSON.parse(localStorage.getItem(CART_KEY)) || [];
    let discount = 0;
    let discountCode = '';
    
    // Initialisation
    updateCartDisplay();
    updateCartCount();
    
    // Écouteurs d'événements
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', clearCart);
    }
    
    if (updateCartBtn) {
        updateCartBtn.addEventListener('click', updateQuantitiesFromInputs);
    }
    
    if (promoForm) {
        promoForm.addEventListener('submit', applyCoupon);
    }
    
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', proceedToCheckout);
    }
    
    // Fonction pour mettre à jour l'affichage du panier
    function updateCartDisplay() {
        // Vider la liste des articles
        cartItemsList.innerHTML = '';
        
        if (cartItems.length === 0) {
            // Afficher le message de panier vide
            emptyCartMessage.style.display = '';
            checkoutBtn.disabled = true;
            clearCartBtn.style.display = 'none';
            updateCartBtn.style.display = 'none';
            subtotalElement.textContent = '0,00 FCFA';
            totalElement.textContent = '0,00 FCFA';
            discountElement.textContent = '-0,00 FCFA';
            return;
        }
        
        // Masquer le message de panier vide
        emptyCartMessage.style.display = 'none';
        checkoutBtn.disabled = false;
        clearCartBtn.style.display = 'flex';
        updateCartBtn.style.display = 'inline-flex';
        
        let subtotal = 0;
        
        // Ajouter chaque article du panier
        cartItems.forEach(item => {
            const itemTotal = item.price * item.quantity;
            subtotal += itemTotal;
            
            const cartItemRow = document.createElement('tr');
            cartItemRow.className = 'cart-items-list';
            cartItemRow.innerHTML = `
                <td class="Product-col" data-label="Produit">
                    <div class="cart-Product">
                        <div class="cart-Product-img">
                            <img src="${item.image}" alt="${item.title}" loading="lazy">
                        </div>
                        <div class="cart-Product-info">
                            <h3>${item.title}</h3>
                            <div class="cart-Product-brand">${item.brand || 'Luxious Beauty'}</div>
                        </div>
                    </div>
                </td>
                <td class="price-col" data-label="Prix">
                    <div class="Product-price">${formatPrice(item.price)} FCFA</div>
                    ${item.originalPrice ? `<div class="original-price">${formatPrice(item.originalPrice)} FCFA</div>` : ''}
                </td>
                <td class="quantity-col" data-label="Quantité">
                    <div class="quantity-selector">
                        <button class="quantity-btn minus" data-id="${item.id}">
                            <i class="fas fa-minus"></i>
                        </button>
                        <input type="number" class="quantity-input" value="${item.quantity}" min="1" data-id="${item.id}">
                        <button class="quantity-btn plus" data-id="${item.id}">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </td>
                <td class="total-col" data-label="Total">
                    <div class="Product-total">${formatPrice(itemTotal)} FCFA</div>
                </td>
                <td class="action-col" data-label="Action">
                    <button class="cart-Product-remove" data-id="${item.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            
            cartItemsList.appendChild(cartItemRow);
        });
        
        // Calculer le total après réduction
        const totalAfterDiscount = subtotal - discount;
        
        // Mettre à jour les totaux
        subtotalElement.textContent = formatPrice(subtotal) + ' FCFA';
        totalElement.textContent = formatPrice(totalAfterDiscount) + ' FCFA';
        discountElement.textContent = discount > 0 ? `-${formatPrice(discount)} FCFA` : '-0,00 FCFA';
        
        // Ajouter les écouteurs d'événements pour les boutons
        document.querySelectorAll('.quantity-btn.minus').forEach(btn => {
            btn.addEventListener('click', function() {
                updateCartItemQuantity(this.getAttribute('data-id'), -1);
            });
        });
        
        document.querySelectorAll('.quantity-btn.plus').forEach(btn => {
            btn.addEventListener('click', function() {
                updateCartItemQuantity(this.getAttribute('data-id'), 1);
            });
        });
        
        document.querySelectorAll('.cart-Product-remove').forEach(btn => {
            btn.addEventListener('click', function() {
                removeCartItem(this.getAttribute('data-id'));
            });
        });
        
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', function() {
                const newQuantity = parseInt(this.value);
                if (newQuantity > 0) {
                    updateCartItemQuantity(this.getAttribute('data-id'), 0, newQuantity);
                } else {
                    this.value = 1;
                }
            });
        });
    }
    
    // Fonction pour mettre à jour la quantité d'un article
    function updateCartItemQuantity(ProductId, change, newQuantity = null) {
        const itemIndex = cartItems.findIndex(item => item.id === ProductId);
        
        if (itemIndex !== -1) {
            if (newQuantity !== null) {
                cartItems[itemIndex].quantity = newQuantity;
            } else {
                cartItems[itemIndex].quantity += change;
            }
            
            // Supprimer si la quantité est <= 0
            if (cartItems[itemIndex].quantity <= 0) {
                cartItems.splice(itemIndex, 1);
                showToast('Produit supprimé du panier', 'info');
            }
            
            // Mettre à jour le localStorage
            saveCart();
            
            // Mettre à jour l'affichage
            updateCartDisplay();
            updateCartCount();
        }
    }
    
    // Fonction pour mettre à jour les quantités depuis les inputs
    function updateQuantitiesFromInputs() {
        const quantityInputs = document.querySelectorAll('.quantity-input');
        let updated = false;
        
        quantityInputs.forEach(input => {
            const ProductId = input.getAttribute('data-id');
            const newQuantity = parseInt(input.value);
            const currentItem = cartItems.find(item => item.id === ProductId);
            
            if (currentItem && currentItem.quantity !== newQuantity) {
                currentItem.quantity = newQuantity;
                updated = true;
            }
        });
        
        if (updated) {
            saveCart();
            updateCartDisplay();
            updateCartCount();
            showToast('Panier mis à jour', 'success');
        }
    }
    
    // Fonction pour supprimer un article du panier
    function removeCartItem(ProductId) {
        cartItems = cartItems.filter(item => item.id !== ProductId);
        saveCart();
        updateCartDisplay();
        updateCartCount();
        showToast('Produit supprimé du panier', 'info');
    }
    
    // Fonction pour vider le panier
    function clearCart() {
        if (cartItems.length === 0) return;
        
        if (confirm('Êtes-vous sûr de vouloir vider votre panier ?')) {
            cartItems = [];
            discount = 0;
            discountCode = '';
            couponInput.value = '';
            saveCart();
            updateCartDisplay();
            updateCartCount();
            showToast('Panier vidé', 'info');
        }
    }
    
    // Fonction pour appliquer un coupon de réduction
    function applyCoupon(e) {
        e.preventDefault();
        const couponCode = couponInput.value.trim();
        
        if (!couponCode) {
            showToast('Veuillez entrer un code promo', 'error');
            return;
        }
        
        // Simulation de vérification de code promo
        // En Production, vous feriez une requête à votre backend
        if (couponCode === 'BEAUTY20') {
            discount = calculateDiscount(20); // 20% de réduction
            this.discountCode = couponCode;
            showToast('Code promo appliqué : 20% de réduction !', 'success');
            updateCartDisplay();
        } else if (couponCode === 'LUXIOUS10') {
            discount = calculateDiscount(10); // 10% de réduction
            this.discountCode = couponCode;
            showToast('Code promo appliqué : 10% de réduction !', 'success');
            updateCartDisplay();
        } else {
            discount = 0;
            this.discountCode = '';
            showToast('Code promo invalide', 'error');
            updateCartDisplay();
        }
    }
    
    // Fonction pour calculer la réduction
    function calculateDiscount(percentage) {
        const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        return (subtotal * percentage) / 100;
    }
    
    // Fonction pour passer à la caisse
    function proceedToCheckout(e) {
        e.preventDefault();
        if (cartItems.length === 0) {
            showToast('Votre panier est vide', 'error');
            return;
        }
        
        // Sauvegarder le panier dans le localStorage
        localStorage.setItem('cartItems', JSON.stringify(cartItems));
        
        // Redirection vers la page de paiement
        window.location.href = 'checkout.html';
    }
    
    // Fonction pour mettre à jour le compteur du panier
    function updateCartCount() {
        const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
        const itemText = totalItems === 1 ? 'article' : 'articles';
        cartCountElement.textContent = `${totalItems} ${itemText}`;
    }
    
    // Fonction pour sauvegarder le panier dans le localStorage
    function saveCart() {
        localStorage.setItem(CART_KEY, JSON.stringify(cartItems));
    }
    
    // Fonction pour formater le prix
    function formatPrice(price) {
        return parseFloat(price).toFixed(2).replace('.', ',');
    }
    
    // Fonction pour afficher une notification toast
    function showToast(message, type = 'info') {
        // Supprimer les toasts existants
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
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
    
    // Styles dynamiques pour les toasts
    const toastStyles = document.createElement('style');
    toastStyles.textContent = `
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
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .toast.show {
            opacity: 1;
            bottom: 30px;
        }
        
        .toast-success {
            background: var(--success-color);
        }
        
        .toast-error {
            background: var(--error-color);
        }
        
        .toast-info {
            background: var(--primary-color);
        }
    `;
    document.head.appendChild(toastStyles);
});

// Exemple de fonction pour ajouter un produit au panier (à utiliser depuis d'autres pages)
function addToCart(Product) {
    const CART_KEY = 'luxious_beauty_cart';
    let cartItems = JSON.parse(localStorage.getItem(CART_KEY)) || [];
    
    // Vérifier si le produit est déjà dans le panier
    const existingItem = cartItems.find(item => item.id === Product.id);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cartItems.push({
            id: Product.id,
            title: product.title,
            brand: product.brand,
            price: Product.price,
            originalPrice: product.originalPrice,
            image: product.image,
            quantity: 1
        });
    }
    
    // Mettre à jour le localStorage
    localStorage.setItem(CART_KEY, JSON.stringify(cartItems));
    
    // Afficher une notification
    showToast(`${product.title} a été ajouté à votre panier`, 'success');
    
    // Mettre à jour le compteur du panier si nous sommes sur la page panier
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
        const itemText = totalItems === 1 ? 'article' : 'articles';
        cartCountElement.textContent = `${totalItems} ${itemText}`;
    }
}

// Fonction utilitaire pour afficher des toasts depuis d'autres pages
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