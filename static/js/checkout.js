document.addEventListener('DOMContentLoaded', function() {
    // Constantes
    const CART_KEY = 'luxious_beauty_cart';
    const ORDER_KEY = 'luxious_beauty_order';
    const WHATSAPP_NUMBER = '22890712928';
    
    // Éléments du DOM
    const orderItemsContainer = document.getElementById('order-items');
    const subtotalElement = document.querySelector('.order-summary .subtotal');
    const totalElement = document.querySelector('.order-summary .total-price');
    const discountElement = document.querySelector('.order-summary .discount');
    const paymentTabs = document.querySelectorAll('.payment-tab');
    const paymentMethods = document.querySelectorAll('.payment-method');
    const mobileForm = document.getElementById('mobile-form');
    const payoneerForm = document.getElementById('payoneer-form');
    const deliveryForm = document.getElementById('delivery-form');
    const confirmationModal = document.getElementById('confirmation-modal');
    const whatsappBtn = document.getElementById('whatsapp-btn');
    
    // Variables
    let cartItems = JSON.parse(localStorage.getItem(CART_KEY)) || [];
    let order = JSON.parse(localStorage.getItem(ORDER_KEY)) || null;
    let discount = 0;
    let discountCode = '';
    
    // Initialisation
    loadOrderSummary();
    setupPaymentTabs();
    
    // Si nous revenons sur cette page après une commande, afficher la confirmation
    if (order) {
        showConfirmation(order);
    }
    
    // Écouteurs d'événements
    if (mobileForm) {
        mobileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processPayment('mobile');
        });
    }
    
    if (payoneerForm) {
        payoneerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processPayment('payoneer');
        });
    }
    
    if (deliveryForm) {
        deliveryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processPayment('delivery');
        });
    }
    
    if (whatsappBtn) {
        whatsappBtn.addEventListener('click', sendWhatsAppConfirmation);
    }
    
    // Fonctions
    
    // Charger le récapitulatif de commande
    function loadOrderSummary() {
        // Vider le conteneur
        orderItemsContainer.innerHTML = '';
        
        if (cartItems.length === 0) {
            orderItemsContainer.innerHTML = '<p class="empty-cart">Votre panier est vide</p>';
            subtotalElement.textContent = '0,00 FCFA';
            totalElement.textContent = '0,00 FCFA';
            discountElement.textContent = '-0,00 FCFA';
            return;
        }
        
        let subtotal = 0;
        
        // Ajouter chaque article du panier
        cartItems.forEach(item => {
            const itemTotal = item.price * item.quantity;
            subtotal += itemTotal;
            
            const orderItem = document.createElement('div');
            orderItem.className = 'order-item';
            orderItem.innerHTML = `
                <div class="order-item-img">
                    <img src="${item.image}" alt="${item.title}" loading="lazy">
                </div>
                <div class="order-item-info">
                    <h4 class="order-item-title">${item.title}</h4>
                    <div class="order-item-brand">${item.brand || 'Luxious Beauty'}</div>
                    <div class="order-item-price">${formatPrice(item.price)} FCFA</div>
                    <div class="order-item-qty">Quantité: ${item.quantity}</div>
                </div>
            `;
            
            orderItemsContainer.appendChild(orderItem);
        });
        
        // Calculer le total après réduction
        const totalAfterDiscount = subtotal - discount;
        
        // Mettre à jour les totaux
        subtotalElement.textContent = formatPrice(subtotal) + ' FCFA';
        totalElement.textContent = formatPrice(totalAfterDiscount) + ' FCFA';
        discountElement.textContent = discount > 0 ? `-${formatPrice(discount)} FCFA` : '-0,00 FCFA';
    }
    
    // Configurer les onglets de paiement
    function setupPaymentTabs() {
        paymentTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Désactiver tous les onglets et contenus
                paymentTabs.forEach(t => t.classList.remove('active'));
                paymentMethods.forEach(m => m.classList.remove('active'));
                
                // Activer l'onglet cliqué
                this.classList.add('active');
                
                // Afficher le contenu correspondant
                const method = this.getAttribute('data-method');
                document.getElementById(`${method}-payment`).classList.add('active');
            });
        });
    }
    
    // Traiter le paiement
    function processPayment(method) {
        // Simuler un traitement de paiement
        // En production, vous utiliseriez une API de paiement réelle
        
        // Créer un objet commande
        const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const total = subtotal - discount;
        
        order = {
            id: generateOrderId(),
            date: new Date().toISOString(),
            items: [...cartItems],
            subtotal: subtotal,
            discount: discount,
            total: total,
            paymentMethod: method,
            status: method === 'delivery' ? 'pending' : 'paid'
        };
        
        // Ajouter des détails spécifiques à la méthode de paiement
        if (method === 'mobile') {
            const provider = document.getElementById('mobile-provider').value;
            const number = document.getElementById('mobile-number').value;
            
            order.paymentDetails = {
                provider: provider,
                number: number
            };
        } else if (method === 'payoneer') {
            const email = document.getElementById('payoneer-email').value;
            
            order.paymentDetails = {
                email: email
            };
        } else if (method === 'delivery') {
            const address = document.getElementById('delivery-address').value;
            const time = document.getElementById('delivery-time').value;
            
            order.deliveryDetails = {
                address: address,
                preferredTime: time
            };
        }
        
        // Sauvegarder la commande
        localStorage.setItem(ORDER_KEY, JSON.stringify(order));
        
        // Vider le panier (sauf pour paiement à la livraison)
        if (method !== 'delivery') {
            localStorage.removeItem(CART_KEY);
            cartItems = [];
        }
        
        // Afficher la confirmation
        showConfirmation(order);
    }
    
    // Afficher la modale de confirmation
    function showConfirmation(order) {
        if (!order) return;
        
        // Remplir les détails de la commande
        document.getElementById('order-number').textContent = order.id;
        document.getElementById('order-amount').textContent = formatPrice(order.total) + ' FCFA';
        
        let paymentMethodText = '';
        switch(order.paymentMethod) {
            case 'mobile':
                paymentMethodText = `Mobile Money (${order.paymentDetails.provider})`;
                document.getElementById('confirmation-message').textContent = 
                    'Votre paiement a été effectué avec succès. Un SMS de confirmation vous a été envoyé.';
                break;
            case 'payoneer':
                paymentMethodText = 'Payoneer';
                document.getElementById('confirmation-message').textContent = 
                    'Votre paiement a été effectué avec succès. Vous recevrez un email de confirmation.';
                break;
            case 'delivery':
                paymentMethodText = 'Paiement à la livraison';
                document.getElementById('confirmation-message').textContent = 
                    'Votre commande a été confirmée. Vous paierez lorsque vous recevrez vos articles.';
                break;
        }
        
        document.getElementById('payment-method').textContent = paymentMethodText;
        
        // Ouvrir la modale
        confirmationModal.classList.add('show');
        document.body.classList.add('modal-open');
    }
    
    // Envoyer la confirmation par WhatsApp
    function sendWhatsAppConfirmation() {
        if (!order) return;
        
        // Créer le message
        let message = `Bonjour,\n\nJe confirme ma commande n°${order.id} chez Luxious Beautyland.\n\n`;
        message += `Détails de la commande :\n`;
        
        order.items.forEach(item => {
            message += `- ${item.title} (x${item.quantity}) : ${formatPrice(item.price * item.quantity)} FCFA\n`;
        });
        
        message += `\nSous-total : ${formatPrice(order.subtotal)} FCFA\n`;
        
        if (order.discount > 0) {
            message += `Réduction : -${formatPrice(order.discount)} FCFA\n`;
        }
        
        message += `Total : ${formatPrice(order.total)} FCFA\n\n`;
        message += `Méthode de paiement : ${document.getElementById('payment-method').textContent}\n\n`;
        message += `Merci !`;
        
        // Encoder le message pour l'URL
        const encodedMessage = encodeURIComponent(message);
        
        // Ouvrir WhatsApp
        window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodedMessage}`, '_blank');
    }
    
    // Générer un ID de commande
    function generateOrderId() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const random = Math.floor(1000 + Math.random() * 9000);
        
        return `CMD-${year}${month}${day}-${random}`;
    }
    
    // Formater le prix
    function formatPrice(price) {
        return parseFloat(price).toFixed(2).replace('.', ',');
    }
});

// Fermer la modale lorsqu'on clique en dehors
document.addEventListener('click', function(e) {
    const modal = document.getElementById('confirmation-modal');
    if (e.target === modal) {
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    }
});