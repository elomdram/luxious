from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count, Sum
from django.forms.models import modelform_factory
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
import json
from datetime import datetime, timedelta
from django.urls import reverse_lazy 
import urllib.parse
from .models import (
    User, Address, Category, Brand, Product, ProductImage, ProductVariant,
    VariantOption, ProductAttribute, Service, Cart, CartItem, Wishlist,
    Order, OrderItem, Payment, Booking, Review, Coupon, NewsletterSubscriber,
    Page, BlogPost, SiteSetting
)
from .forms import CustomUserCreationForm, AddressForm, ReviewForm, BookingForm
from django.contrib.auth import login, logout, authenticate
from urllib.parse import quote
# ==================== UTILS ====================

def ajax_required(f):
    """Décorateur pour n'autoriser que les requêtes AJAX"""
    def wrap(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(status=400)
        return f(request, *args, **kwargs)
    return wrap

# ==================== VIEWS PRINCIPALES ====================

from django.contrib.auth.views import LoginView, LogoutView

class CustomLoginView(LoginView):
    template_name = 'account/login.html'

class CustomLogoutView(LogoutView):
    template_name = 'account/logout.html'

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_featured=True, is_active=True)[:8]
        context['latest_products'] = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
        context['services'] = Service.objects.filter(is_active=True)[:4]
        context['blog_posts'] = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:3]
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filtrage par catégorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            descendants = category.get_descendants(include_self=True)
            queryset = queryset.filter(categories__in=descendants)
        
        # Filtrage par marque
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            brand = get_object_or_404(Brand, slug=brand_slug)
            queryset = queryset.filter(brand=brand)
        
        # Filtrage par prix
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Recherche
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        # Tri
        sort_by = self.request.GET.get('sort_by', 'created_at')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'popularity':
            # Implémentation basique de la popularité
            queryset = queryset.annotate(review_count=Count('reviews')).order_by('-review_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        
        # Ajouter les paramètres de filtrage au contexte
        for key in ['category', 'brand', 'min_price', 'max_price', 'q', 'sort_by']:
            context[key] = self.request.GET.get(key, '')
        
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Produits similaires
        context['related_products'] = Product.objects.filter(
            categories__in=product.categories.all(),
            is_active=True
        ).exclude(id=product.id).distinct()[:4]
        
        # Avis
        context['reviews'] = Review.objects.filter(
            product=product, 
            is_approved=True
        ).order_by('-created_at')[:10]
        
        # Note moyenne
        context['average_rating'] = context['reviews'].aggregate(Avg('rating'))['rating__avg'] or 0
        
        return context

class ServiceListView(ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        
        # Recherche
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        # Filtre par catégorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtre par durée
        duration = self.request.GET.get('duration')
        if duration:
            duration_list = duration.split(',')
            queryset = queryset.filter(duration__in=duration_list)
        
        # Filtre par prix
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtre par réservation obligatoire
        if self.request.GET.get('requires_booking'):
            queryset = queryset.filter(requires_booking=True)
        
        # Tri
        sort_by = self.request.GET.get('sort_by', '-created_at')
        valid_sort_fields = ['name', '-name', 'price', '-price', 'duration', '-duration', 'created_at', '-created_at']
        
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Catégories avec comptage
        context['categories'] = Category.objects.filter(
            is_active=True, 
            services__isnull=False
        ).annotate(
            service_count=Count('services')
        ).distinct()
        
        # Services en vedette (exemple : avec le plus de réservations)
        context['featured_services'] = Service.objects.filter(
            is_active=True
        ).annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')[:3]
        
        # Choix de durée
        context['duration_choices'] = Service.DURATION_CHOICES
        
        # Statistiques
        context['total_services'] = Service.objects.filter(is_active=True).count()
        context['categories_count'] = Category.objects.filter(
            is_active=True, 
            services__isnull=False
        ).count()
        
        # Mode d'affichage (grille/liste)
        context['view_mode'] = self.request.GET.get('view', 'grid')
        
        # Paramètres de filtrage pour les templates
        for key in ['q', 'category', 'min_price', 'max_price', 'sort_by']:
            context[key] = self.request.GET.get(key, '')
        
        return context

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        
        # Services similaires - filtrer ceux qui n'ont pas de slug
        context['related_services'] = Service.objects.filter(
            category=service.category,
            is_active=True
        ).exclude(id=service.id).exclude(
            slug__isnull=True
        ).exclude(
            slug=''
        )[:3]
        
        # Avis
        context['reviews'] = Review.objects.filter(
            service=service, 
            is_approved=True
        ).order_by('-created_at')[:10]
        
        # Note moyenne
        context['average_rating'] = context['reviews'].aggregate(Avg('rating'))['rating__avg'] or 0
        
        return context
# ==================== PANIER & WISHLIST ====================

class CartView(TemplateView):
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart()
        context['cart'] = cart
        return context
    
    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

@require_POST
@ajax_required
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        service_id = data.get('service_id')
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        
        # Récupérer le panier
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        # Ajouter l'article au panier
        if product_id:
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # Vérifier le stock
            if product.track_quantity and product.quantity < quantity and not product.allow_backorder:
                return JsonResponse({
                    'success': False,
                    'message': 'Stock insuffisant pour ce produit.'
                })
            
            # Vérifier si l'article existe déjà dans le panier
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=ProductVariant.objects.filter(id=variant_id).first() if variant_id else None,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                
        elif service_id:
            service = get_object_or_404(Service, id=service_id, is_active=True)
            
            # Vérifier si le service existe déjà dans le panier
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                service=service,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        else:
            return JsonResponse({
                'success': False,
                'message': 'Aucun produit ou service spécifié.'
            })
        
        # Mettre à jour le nombre d'articles dans le panier
        cart_items_count = cart.items.count()
        
        return JsonResponse({
            'success': True,
            'message': 'Article ajouté au panier.',
            'cart_items_count': cart_items_count,
            'cart_total': cart.total
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'ajout au panier: {str(e)}'
        })

@require_POST
@ajax_required
def update_cart_item(request, item_id):
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Vérifier que l'utilisateur a le droit de modifier cet article
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                raise PermissionDenied
        else:
            if cart_item.cart.session_key != request.session.session_key:
                raise PermissionDenied
        
        # Vérifier le stock pour les produits
        if cart_item.product and cart_item.product.track_quantity:
            if quantity > cart_item.product.quantity and not cart_item.product.allow_backorder:
                return JsonResponse({
                    'success': False,
                    'message': 'Stock insuffisant pour cette quantité.'
                })
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Recalculer les totaux
        cart = cart_item.cart
        cart_items = cart.items.all()
        
        items_html = render_to_string('cart/partials/cart_items.html', {'cart': cart})
        totals_html = render_to_string('cart/partials/cart_totals.html', {'cart': cart})
        
        return JsonResponse({
            'success': True,
            'item_total': cart_item.total,
            'cart_total': cart.total,
            'items_count': cart.items_count,
            'items_html': items_html,
            'totals_html': totals_html
        })
        
    except PermissionDenied:
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'avez pas la permission de modifier cet article.'
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        })

@require_POST
@ajax_required
def remove_cart_item(request, item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        # Vérifier que l'utilisateur a le droit de supprimer cet article
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                raise PermissionDenied
        else:
            if cart_item.cart.session_key != request.session.session_key:
                raise PermissionDenied
        
        cart = cart_item.cart
        cart_item.delete()
        
        # Recalculer les totaux
        cart_items = cart.items.all()
        
        items_html = render_to_string('cart/partials/cart_items.html', {'cart': cart})
        totals_html = render_to_string('cart/partials/cart_totals.html', {'cart': cart})
        
        return JsonResponse({
            'success': True,
            'cart_total': cart.total,
            'items_count': cart.items_count,
            'items_html': items_html,
            'totals_html': totals_html
        })
        
    except PermissionDenied:
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'avez pas la permission de supprimer cet article.'
        }, status=403)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        })

@require_POST
@ajax_required
def toggle_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        service_id = data.get('service_id')
        
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Vous devez être connecté pour ajouter aux favoris.',
                'login_required': True
            })
        
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            if wishlist.products.filter(id=product_id).exists():
                wishlist.products.remove(product)
                added = False
            else:
                wishlist.products.add(product)
                added = True
                
        elif service_id:
            service = get_object_or_404(Service, id=service_id)
            if wishlist.services.filter(id=service_id).exists():
                wishlist.services.remove(service)
                added = False
            else:
                wishlist.services.add(service)
                added = True
        else:
            return JsonResponse({
                'success': False,
                'message': 'Aucun produit ou service spécifié.'
            })
        
        return JsonResponse({
            'success': True,
            'added': added,
            'message': 'Ajouté aux favoris.' if added else 'Retiré des favoris.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

# ==================== COMMANDES ====================

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer le panier de l'utilisateur
        cart = get_object_or_404(Cart, user=self.request.user)
        context['cart'] = cart
        
        # Adresses de l'utilisateur
        context['addresses'] = Address.objects.filter(user=self.request.user)
        
        # Méthodes de paiement disponibles
        context['payment_methods'] = dict(Order.PAYMENT_METHOD_CHOICES)
        
        return context

@require_POST
@ajax_required
@login_required
def apply_coupon(request):
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')
        
        if not coupon_code:
            return JsonResponse({
                'success': False,
                'message': 'Veuillez entrer un code promo.'
            })
        
        coupon = get_object_or_404(Coupon, code=coupon_code.upper())
        
        # Vérifier si le coupon est valide
        if not coupon.is_valid(user=request.user):
            return JsonResponse({
                'success': False,
                'message': 'Ce code promo n\'est pas valide ou a expiré.'
            })
        
        # Récupérer le panier
        cart = get_object_or_404(Cart, user=request.user)
        
        # Calculer la réduction
        discount_amount = 0
        if coupon.discount_type == 'percentage':
            discount_amount = cart.total * coupon.discount_value / 100
            if coupon.maximum_discount and discount_amount > coupon.maximum_discount:
                discount_amount = coupon.maximum_discount
        elif coupon.discount_type == 'fixed':
            discount_amount = coupon.discount_value
        elif coupon.discount_type == 'free_shipping':
            discount_amount = 0  # Géré séparément
        
        # Préparer la réponse
        response_data = {
            'success': True,
            'message': 'Code promo appliqué avec succès.',
            'coupon_code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_amount': float(discount_amount),
            'free_shipping': coupon.discount_type == 'free_shipping'
        }
        
        # Stocker le coupon en session pour l'utiliser lors de la commande
        request.session['applied_coupon'] = {
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'discount_amount': float(discount_amount),
            'free_shipping': coupon.discount_type == 'free_shipping'
        }
        
        return JsonResponse(response_data)
        
    except Coupon.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Code promo invalide.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'application du code promo: {str(e)}'
        })

@require_POST
@ajax_required
@login_required
def create_order(request):
    try:
        data = json.loads(request.body)
        
        # Récupérer le panier
        cart = get_object_or_404(Cart, user=request.user)
        
        if cart.items.count() == 0:
            return JsonResponse({
                'success': False,
                'message': 'Votre panier est vide.'
            })
        
        # Récupérer les adresses
        shipping_address_id = data.get('shipping_address_id')
        billing_address_id = data.get('billing_address_id')
        
        shipping_address = get_object_or_404(Address, id=shipping_address_id, user=request.user)
        billing_address = get_object_or_404(Address, id=billing_address_id, user=request.user)
        
        # Récupérer la méthode de paiement
        payment_method = data.get('payment_method')
        if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES).keys():
            return JsonResponse({
                'success': False,
                'message': 'Méthode de paiement invalide.'
            })
        
        # Calculer les totaux
        items_total = cart.total
        shipping_total = 0  # À implémenter selon la logique de livraison
        tax_total = 0  # À implémenter selon la logique fiscale
        
        # Appliquer les réductions de coupon
        discount_total = 0
        free_shipping = False
        
        applied_coupon = request.session.get('applied_coupon')
        if applied_coupon:
            if applied_coupon['discount_type'] == 'free_shipping':
                free_shipping = True
                shipping_total = 0
            else:
                discount_total = applied_coupon['discount_amount']
        
        if not free_shipping:
            # Calculer les frais de port (à implémenter selon la logique métier)
            shipping_total = 10  # Exemple fixe
        
        grand_total = items_total + shipping_total + tax_total - discount_total
        
        # Créer la commande
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            items_total=items_total,
            shipping_total=shipping_total,
            tax_total=tax_total,
            discount_total=discount_total,
            grand_total=grand_total
        )
        
        # Créer les articles de commande
        for cart_item in cart.items.all():
            product_name = cart_item.product.name if cart_item.product else cart_item.service.name
            sku = cart_item.product.sku if cart_item.product else cart_item.service.slug
            price = cart_item.price
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                service=cart_item.service,
                variant=cart_item.variant,
                product_name=product_name,
                sku=sku,
                price=price,
                quantity=cart_item.quantity,
                total=cart_item.total
            )
        
        # Vider le panier
        cart.items.all().delete()
        
        # Supprimer le coupon de la session
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        
        return JsonResponse({
            'success': True,
            'message': 'Commande créée avec succès.',
            'order_id': order.id,
            'order_number': order.order_number,
            'redirect_url': reverse('order_detail', kwargs={'pk': order.id})
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création de la commande: {str(e)}'
        })

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# ==================== COMPTE UTILISATEUR ====================

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'account/profile.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'gender', 'newsletter_subscribed']
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user

class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'account/address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'account/address_form.html'
    fields = ['first_name', 'last_name', 'company', 'street', 'complement', 
              'postal_code', 'city', 'country', 'phone', 
              'is_default_shipping', 'is_default_billing']
    success_url = reverse_lazy('address_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse_lazy('home')
class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'account/address_form.html'
    fields = ['first_name', 'last_name', 'company', 'street', 'complement', 
              'postal_code', 'city', 'country', 'phone', 
              'is_default_shipping', 'is_default_billing']
    success_url = reverse_lazy('address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'account/address_confirm_delete.html'
    success_url = reverse_lazy('address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

@require_POST
@ajax_required
@login_required
def set_default_address(request, address_type):
    try:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        if address_type == 'shipping':
            # Réinitialiser les autres adresses de livraison par défaut
            Address.objects.filter(user=request.user, is_default_shipping=True).update(is_default_shipping=False)
            address.is_default_shipping = True
            request.user.default_shipping_address = address
            
        elif address_type == 'billing':
            # Réinitialiser les autres adresses de facturation par défaut
            Address.objects.filter(user=request.user, is_default_billing=True).update(is_default_billing=False)
            address.is_default_billing = True
            request.user.default_billing_address = address
            
        else:
            return JsonResponse({
                'success': False,
                'message': 'Type d\'adresse invalide.'
            })
        
        address.save()
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Adresse par défaut mise à jour.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

class WishlistView(LoginRequiredMixin, ListView):
    template_name = 'account/wishlist.html'
    context_object_name = 'wishlist_items'
    
    def get_queryset(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return {
            'products': wishlist.products.all(),
            'services': wishlist.services.all()
        }

# ==================== AVIS ====================

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'title', 'comment']
    template_name = 'reviews/review_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        product_id = self.kwargs.get('product_id')
        service_id = self.kwargs.get('service_id')
        
        if product_id:
            form.instance.product = get_object_or_404(Product, id=product_id)
        elif service_id:
            form.instance.service = get_object_or_404(Service, id=service_id)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        if self.object.product:
            return reverse_lazy('product_detail', kwargs={'slug': self.object.product.slug})
        else:
            return reverse_lazy('service_detail', kwargs={'slug': self.object.service.slug})

@require_POST
@ajax_required
@login_required
def like_review(request, review_id):
    try:
        review = get_object_or_404(Review, id=review_id)
        
        # Vérifier si l'utilisateur a déjà liké cet avis
        if request.user in review.likes.all():
            review.likes.remove(request.user)
            liked = False
        else:
            review.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': review.likes.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

# ==================== RÉSERVATIONS ====================
from django.urls import reverse

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['date', 'start_time', 'participants', 'notes']
    template_name = 'bookings/booking_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        service = get_object_or_404(Service, id=self.kwargs['service_id'])
        initial['service'] = service
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = get_object_or_404(Service, id=self.kwargs['service_id'])
        context['available_services'] = Service.objects.filter(
            is_active=True
        ).exclude(id=self.kwargs['service_id'])[:3]
        return context
    
    def form_valid(self, form):
        service = get_object_or_404(Service, id=self.kwargs['service_id'])
        
        # Sauvegarder d'abord la réservation avec le statut "pending"
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.service = service
        booking.price = service.price
        booking.total = service.price * form.cleaned_data['participants']
        
        # Calculate end time based on service duration
        start_time = form.cleaned_data['start_time']
        duration = service.duration
        hours = duration // 60
        minutes = duration % 60
        
        from datetime import timedelta
        end_time = (datetime.combine(form.cleaned_data['date'], start_time) + 
                   timedelta(hours=hours, minutes=minutes)).time()
        
        booking.end_time = end_time
        booking.status = 'pending'
        booking.payment_status = 'pending'
        booking.save()
        
        # Générer l'URL complète de l'image du service
        service_image_url = None
        if service.image:
            service_image_url = self.request.build_absolute_uri(service.image.url)
        else:
            # Image par défaut
            service_image_url = self.request.build_absolute_uri('/static/images/service-default.jpg')
        
        # Préparer le message WhatsApp complet
        phone_number = "22890712928"  # Numéro WhatsApp de l'entreprise
        whatsapp_message = self._generate_whatsapp_message(booking, service_image_url)
        
        # Handle AJAX requests
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response_data = {
                'success': True,
                'booking_id': booking.id,
                'whatsapp_url': f'https://wa.me/{phone_number}?text={whatsapp_message}',
                'redirect_url': reverse('booking_payment', kwargs={'pk': booking.id})
            }
            return JsonResponse(response_data)
        
        # Pour les requêtes non-AJAX, rediriger vers la page de paiement
        self.object = booking
        return redirect('booking_payment', pk=booking.id)
    
    def _generate_whatsapp_message(self, booking, service_image_url):
        """Génère le message WhatsApp complet avec toutes les informations de la réservation"""
        
        # Informations utilisateur
        user = booking.user
        user_full_name = user.get_full_name() or user.username
        user_phone = user.phone or 'Non renseigné'
        user_email = user.email
        user_address = self._get_user_address(user)
        
        # Dates formatées
        booking_date = booking.date.strftime('%d/%m/%Y')
        booking_time = booking.start_time.strftime('%H:%M')
        booking_end_time = booking.end_time.strftime('%H:%M')
        created_at = booking.created_at.strftime('%d/%m/%Y à %H:%M')
        
        # Calcul du délai d'annulation
        cancel_deadline = (booking.date - timedelta(days=1)).strftime('%d/%m/%Y à 23:59')
        
        message = f"""
*🆕 NOUVELLE DEMANDE DE RÉSERVATION - LUXIOUS BEAUTYLAND*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📋 RÉSERVATION #{booking.id}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🛍️ SERVICE RÉSERVÉ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷️ *Nom :* {booking.service.name}
📝 *Description :* {booking.service.short_description[:200]}...
⏱️ *Durée :* {booking.service.duration} minutes
👥 *Max participants :* {booking.service.max_participants} personne(s)
💰 *Prix unitaire :* {booking.service.price} FCFA
📸 *Image du service :* {service_image_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📅 DÉTAILS DE LA RÉSERVATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📆 *Date :* {booking_date}
⏰ *Heure de début :* {booking_time}
⌛ *Heure de fin :* {booking_end_time}
👥 *Nombre de participants :* {booking.participants}
💰 *Prix total :* {booking.total} FCFA
📝 *Notes :* {booking.notes or 'Aucune note'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*👤 INFORMATIONS CLIENT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔 *Nom complet :* {user_full_name}
📧 *Email :* {user_email}
📱 *Téléphone :* {user_phone}
🏠 *Adresse :* {user_address}
📅 *Date d'inscription :* {user.date_joined.strftime('%d/%m/%Y')}
⭐ *Statut :* {'Client vérifié' if user.email_verified else 'Client non vérifié'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*💰 INFORMATIONS DE PAIEMENT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 *Montant total :* {booking.total} FCFA
💳 *Devise :* XOF (Franc CFA)
⏳ *Statut paiement :* En attente
📊 *Statut réservation :* En attente de confirmation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📌 POLITIQUE D'ANNULATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ *Annulation gratuite jusqu'au :* {cancel_deadline}
❌ *Frais d'annulation après ce délai :* 50% du montant
🚫 *No-show :* 100% du montant

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📱 MOYENS DE PAIEMENT DISPONIBLES*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ *Mobile Money :*
   • MTN Money : +228 90 71 29 28
   • Moov Money : +228 90 71 29 28
   
2️⃣ *Paiement à l'agence*
3️⃣ *Virement bancaire*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*⏱️ TIMELINE DE LA RÉSERVATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *Création :* {created_at}
🔄 *Dernière modification :* {booking.updated_at.strftime('%d/%m/%Y à %H:%M')}
⏳ *Statut actuel :* En attente de paiement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*ℹ️ POUR VALIDER CETTE RÉSERVATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ Confirmer la disponibilité du créneau
2️⃣ Encaisser le paiement selon le moyen choisi
3️⃣ Mettre à jour le statut dans le système
4️⃣ Envoyer la confirmation au client

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Généré automatiquement par Luxious Beautyland - {created_at}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()
        
        return message.replace('\n', '%0A').replace(' ', '%20')
    
    def _get_user_address(self, user):
        """Récupère l'adresse par défaut de l'utilisateur"""
        try:
            if user.default_shipping_address:
                addr = user.default_shipping_address
                return f"{addr.street}, {addr.city}, {addr.country} - {addr.phone}"
            elif user.addresses.exists():
                addr = user.addresses.first()
                return f"{addr.street}, {addr.city}, {addr.country} - {addr.phone}"
            else:
                return "Aucune adresse renseignée"
        except:
            return "Adresse non disponible"
    
    def get_success_url(self):
        return reverse('booking_payment', kwargs={'pk': self.object.id})

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Booking.objects.filter(user=self.request.user)
        
        # Filtrage par statut
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Recherche
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(service__name__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        # Tri
        sort_by = self.request.GET.get('sort', '-date')
        if sort_by in ['date', '-date', 'total', '-total']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-date', '-start_time')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_bookings = Booking.objects.filter(user=self.request.user)
        
        # Statistiques
        context['confirmed_count'] = user_bookings.filter(status='confirmed').count()
        context['pending_count'] = user_bookings.filter(status='pending').count()
        context['completed_count'] = user_bookings.filter(status='completed').count()
        context['cancelled_count'] = user_bookings.filter(status='cancelled').count()
        
        # Réservations à venir
        today = timezone.now().date()
        context['upcoming_count'] = user_bookings.filter(
            date__gte=today,
            status__in=['pending', 'confirmed']
        ).count()
        
        # Date du jour pour le calendrier
        context['today'] = today
        
        return context

class BookingPaymentView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_payment.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        
        # Générer l'URL complète de l'image du service
        service_image_url = None
        if booking.service.image:
            service_image_url = self.request.build_absolute_uri(booking.service.image.url)
        else:
            service_image_url = self.request.build_absolute_uri('/static/images/service-default.jpg')
        
        # Générer le lien WhatsApp complet
        phone_number = "22890712928"
        whatsapp_message = self._generate_whatsapp_message(booking, service_image_url)
        context['whatsapp_url'] = f'https://wa.me/{phone_number}?text={whatsapp_message}'
        
        # Informations client pour le template
        context['user_full_name'] = booking.user.get_full_name() or booking.user.username
        context['user_phone'] = booking.user.phone or 'Non renseigné'
        context['user_address'] = self._get_user_address(booking.user)
        
        return context

    def _generate_whatsapp_message(self, booking, service_image_url):
        """Génère un message WhatsApp sans emojis et l'encode pour URL"""

        # Sécuriser l'URL de l'image
        if service_image_url and not service_image_url.startswith('http'):
            service_image_url = self.request.build_absolute_uri(service_image_url)

        # Informations utilisateur avec fallback
        user_name = booking.user.get_full_name() or booking.user.username or "Client"
        user_phone = booking.user.phone or "Non renseigné"
        user_email = booking.user.email or "Non renseigné"

        # Formatage date et heure
        booking_date = booking.date.strftime('%d/%m/%Y')
        booking_time = booking.start_time.strftime('%H:%M')

        # Construction du message
        message = (
            f"*RESERVATION #{booking.id}*\n\n"
            f"*Service:* {booking.service.name}\n"
            f"Duree: {booking.service.duration} min\n"
            f"Prix unitaire: {booking.service.price} FCFA\n"
            f"Image: {service_image_url}\n\n"
            f"*RENDEZ-VOUS*\n"
            f"Date: {booking_date}\n"
            f"Heure: {booking_time}\n"
            f"Participants: {booking.participants}\n"
            f"Total: {booking.total} FCFA\n\n"
            f"*CLIENT*\n"
            f"Nom: {user_name}\n"
            f"Telephone: {user_phone}\n"
            f"Email: {user_email}\n\n"
            f"*PAIEMENT*\n"
            f"Montant: {booking.total} FCFA\n"
            f"Mobile Money: +22890712928\n"
            f"Statut: En attente\n\n"
            f"Merci de confirmer le paiement."
        )

        # Encodage propre pour WhatsApp
        return quote(message)



    def _get_user_address(self, user):
        """Récupère l'adresse par défaut de l'utilisateur"""
        try:
            if user.default_shipping_address:
                addr = user.default_shipping_address
                return f"{addr.street}, {addr.city}, {addr.country} - {addr.phone}"
            elif user.addresses.exists():
                addr = user.addresses.first()
                return f"{addr.street}, {addr.city}, {addr.country} - {addr.phone}"
            else:
                return "Aucune adresse renseignée"
        except:
            return "Adresse non disponible"

@require_POST
@ajax_required
@login_required
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Vérifier si l'annulation est possible (au moins 24h à l'avance)
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(booking.date, booking.start_time)
        )
        
        if timezone.now() > booking_datetime - timezone.timedelta(hours=24):
            return JsonResponse({
                'success': False,
                'message': 'Impossible d\'annuler moins de 24 heures avant le rendez-vous.'
            })
        
        booking.status = 'cancelled'
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Réservation annulée avec succès.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

# ==================== BLOG ====================

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by('-published_at')

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)

# ==================== PAGES STATIQUES ====================

class PageDetailView(DetailView):
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Page.objects.filter(is_active=True)

# ==================== NEWSLETTER ====================

@require_POST
@ajax_required
def subscribe_newsletter(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Veuillez fournir une adresse email.'
            })
        
        # Vérifier si l'email est déjà abonné
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if not created:
            if subscriber.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'Cet email est déjà abonné à notre newsletter.'
                })
            else:
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Merci de vous être abonné à notre newsletter!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@require_POST
@ajax_required
def unsubscribe_newsletter(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Veuillez fournir une adresse email.'
            })
        
        subscriber = get_object_or_404(NewsletterSubscriber, email=email)
        subscriber.is_active = False
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Vous avez été désabonné de notre newsletter.'
        })
        
    except NewsletterSubscriber.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cet email n\'est pas abonné à notre newsletter.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

# ==================== RECHERCHE ====================

class SearchView(TemplateView):
    template_name = 'search/search_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        
        if query:
            # Recherche dans les produits
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query),
                is_active=True
            )[:10]
            
            # Recherche dans les services
            services = Service.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query),
                is_active=True
            )[:10]
            
            # Recherche dans les articles de blog
            blog_posts = BlogPost.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                is_published=True
            )[:5]
            
            context.update({
                'query': query,
                'products': products,
                'services': services,
                'blog_posts': blog_posts,
                'results_count': products.count() + services.count() + blog_posts.count()
            })
        
        return context

@require_GET
@ajax_required
def quick_search(request):
    query = request.GET.get('q', '')
    results = {}
    
    if query:
        # Produits
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:5]
        
        # Services
        services = Service.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:5]
        
        results = {
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': str(p.price),
                    'image': p.images.filter(is_default=True).first().image.url if p.images.filter(is_default=True).exists() else '',
                    'url': reverse_lazy('product_detail', kwargs={'slug': p.slug})
                } for p in products
            ],
            'services': [
                {
                    'id': s.id,
                    'name': s.name,
                    'price': str(s.price),
                    'image': s.image.url if s.image else '',
                    'url': reverse_lazy('service_detail', kwargs={'slug': s.slug})
                } for s in services
            ]
        }
    
    return JsonResponse(results)

# ==================== API POUR FRONTEND ====================

@require_GET
@ajax_required
def get_product_variants(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        variants = product.variants.all()
        
        variants_data = []
        for variant in variants:
            options = variant.options.all()
            options_data = {opt.name: opt.value for opt in options}
            
            variants_data.append({
                'id': variant.id,
                'sku': variant.sku,
                'price': str(variant.price) if variant.price else str(product.price),
                'compare_price': str(variant.compare_price) if variant.compare_price else str(product.compare_price),
                'quantity': variant.quantity,
                'weight': str(variant.weight) if variant.weight else str(product.weight),
                'options': options_data
            })
        
        return JsonResponse({
            'success': True,
            'variants': variants_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@require_GET
@ajax_required
def check_product_availability(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        variant_id = request.GET.get('variant_id')
        
        quantity_available = product.quantity
        is_available = True
        message = 'En stock'
        
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
            quantity_available = variant.quantity
        else:
            variant = None
        
        if product.track_quantity:
            if quantity_available <= 0:
                is_available = product.allow_backorder
                message = 'En rupture de stock' if not is_available else 'Précommande disponible'
            elif quantity_available < product.low_stock_threshold:
                message = f'Plus que {quantity_available} en stock'
        
        return JsonResponse({
            'success': True,
            'is_available': is_available,
            'quantity_available': quantity_available,
            'allows_backorder': product.allow_backorder,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })

@require_GET
@ajax_required
def get_available_dates(request, service_id):
    try:
        service = get_object_or_404(Service, id=service_id)
        
        # Récupérer les dates déjà réservées
        from datetime import date, timedelta
        today = date.today()
        end_date = today + timedelta(days=60)  # 2 mois à l'avance
        
        # Récupérer les créaux déjà réservés
        bookings = Booking.objects.filter(
            service=service,
            date__range=[today, end_date],
            status__in=['pending', 'confirmed']
        )
        
        # Convertir en format pour le frontend
        booked_dates = {}
        for booking in bookings:
            date_str = booking.date.isoformat()
            if date_str not in booked_dates:
                booked_dates[date_str] = []
            booked_dates[date_str].append({
                'start': booking.start_time.strftime('%H:%M'),
                'end': booking.end_time.strftime('%H:%M')
            })
        
        # Générer les dates disponibles (exemple simplifié)
        available_dates = []
        current_date = today
        
        while current_date <= end_date:
            # Exclure les weekends (à adapter selon les besoins)
            if current_date.weekday() < 5:  # 0-4 = Lundi-Vendredi
                available_dates.append(current_date.isoformat())
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'success': True,
            'available_dates': available_dates,
            'booked_slots': booked_dates,
            'duration': service.duration
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


# Vues pour les abonnements
class SubscriptionListView(TemplateView):
    template_name = 'subscription/subscription_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données nécessaires pour la page d'abonnement
        return context

class SubscriptionChooseView(LoginRequiredMixin, TemplateView):
    template_name = 'subscription/subscription_choose.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données nécessaires pour choisir un abonnement
        return context

class SubscriptionPaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'subscription/subscription_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données nécessaires pour le paiement
        return context

class SubscriptionConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'subscription/subscription_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données nécessaires pour la confirmation
        return context

class SubscriptionManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'subscription/subscription_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données nécessaires pour la gestion des abonnements
        return context

@require_POST
@ajax_required
@login_required
def subscribe_subscription(request):
    try:
        data = json.loads(request.body)
        plan = data.get('plan')
        payment_method = data.get('payment_method')
        
        # Traitez ici l'inscription à l'abonnement
        
        return JsonResponse({
            'success': True,
            'message': 'Abonnement souscrit avec succès',
            'redirect_url': reverse_lazy('subscription_confirmation')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la souscription: {str(e)}'
        })
   
# Ajoutez ces imports en haut du fichier
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import hashlib
import hmac

# ==================== PAIEMENT FEDAPAY ====================

@require_POST
@ajax_required
@login_required
def confirm_order_payment(request, order_id):
    """Confirme le paiement d'une commande après succès FedaPay"""
    try:
        data = json.loads(request.body)
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Mettre à jour la commande
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.paid_at = timezone.now()
        order.save()
        
        # Créer un enregistrement de paiement
        Payment.objects.create(
            order=order,
            payment_method='fedapay',
            amount=order.grand_total,
            status='completed',
            transaction_id=data.get('transaction_id'),
            payment_details=data
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Paiement confirmé avec succès',
            'redirect_url': reverse_lazy('order_detail', kwargs={'pk': order.id})
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la confirmation du paiement: {str(e)}'
        })

@require_POST
@ajax_required
@login_required
def confirm_booking_payment(request, booking_id):
    """API pour confirmer le paiement d'une réservation"""
    try:
        data = json.loads(request.body)
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Vérifier que la réservation est en attente
        if booking.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': 'Cette réservation ne peut plus être modifiée.'
            })
        
        # Mettre à jour la réservation
        payment_method = data.get('payment_method', 'fedapay')
        transaction_id = data.get('transaction_id')
        payment_status = data.get('payment_status', 'paid')
        
        booking.payment_status = payment_status
        booking.payment_method = payment_method
        booking.payment_reference = transaction_id
        
        if payment_status == 'paid':
            booking.status = 'confirmed'
            booking.payment_confirmed_at = timezone.now()
        
        booking.save()
        
        # Créer un enregistrement de paiement si nécessaire
        if payment_method == 'fedapay' and transaction_id:
            Payment.objects.create(
                order=None,  # Pas de commande associée
                payment_method='fedapay',
                amount=booking.total,
                currency='XOF',
                status='completed',
                transaction_id=transaction_id,
                payment_details=data
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Paiement confirmé avec succès !',
            'redirect_url': reverse('booking_detail', kwargs={'pk': booking.id})
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Réservation introuvable.'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Données invalides.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la confirmation: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def fedapay_webhook(request):
    """Webhook pour recevoir les notifications de paiement FedaPay"""
    try:
        # Vérifier la signature du webhook
        signature = request.headers.get('X-FedaPay-Signature')
        if not signature:
            return HttpResponse(status=400)
        
        payload = request.body
        secret = settings.FEDAPAY_WEBHOOK_SECRET  # À ajouter dans settings.py
        
        # Calculer la signature attendue
        expected_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return HttpResponse(status=401)
        
        # Traiter le webhook
        data = json.loads(payload)
        event_type = data.get('event')
        transaction = data.get('transaction', {})
        
        # Récupérer les métadonnées
        custom_metadata = transaction.get('custom_metadata', {})
        order_id = custom_metadata.get('order_id')
        booking_id = custom_metadata.get('booking_id')
        
        if event_type == 'transaction.completed':
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    order.paid_at = timezone.now()
                    order.save()
                    
                    Payment.objects.create(
                        order=order,
                        payment_method='fedapay',
                        amount=order.grand_total,
                        status='completed',
                        transaction_id=transaction.get('id'),
                        payment_details=transaction
                    )
                except Order.DoesNotExist:
                    pass
            
            if booking_id:
                try:
                    booking = Booking.objects.get(id=booking_id)
                    booking.payment_status = 'paid'
                    booking.status = 'confirmed'
                    booking.payment_confirmed_at = timezone.now()
                    booking.payment_method = 'fedapay'
                    booking.payment_reference = transaction.get('id')
                    booking.save()
                except Booking.DoesNotExist:
                    pass
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return HttpResponse(status=500)

@login_required
@require_POST
def cancel_order(request, pk):
    """Annuler une commande"""
    order = get_object_or_404(Order, pk=pk, user=request.user)

    if order.status not in ["pending", "confirmed"]:
        return JsonResponse({
            "success": False,
            "message": "Cette commande ne peut plus être annulée."
        }, status=400)

    # Si le paiement a été effectué, initier un remboursement
    if order.payment_status == 'paid':
        # Logique de remboursement à implémenter
        pass

    order.status = "cancelled"
    order.save()

    return JsonResponse({
        "success": True,
        "message": "Commande annulée avec succès."
    })

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)