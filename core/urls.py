from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # ==================== PAGES PRINCIPALES ====================
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # ==================== PANIER ====================
    path('cart/', views.CartView.as_view(), name='cart'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('api/cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    
    # ==================== FAVORIS ====================
    path('api/wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    
    # ==================== COMMANDES ====================
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('api/checkout/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('api/checkout/order/create/', views.create_order, name='create_order'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path(
        "api/orders/<int:pk>/cancel/",
        views.cancel_order,
        name="api_order_cancel"
    ),

    # ==================== PAIEMENT FEDAPAY ====================
    path('api/orders/<int:order_id>/confirm-payment/', views.confirm_order_payment, name='confirm_order_payment'),
    path('api/fedapay/webhook/', views.fedapay_webhook, name='fedapay_webhook'),

    
    # ==================== COMPTE UTILISATEUR ====================
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('account/register/', views.RegisterView.as_view(), name='register'),
    path('account/profile/', views.ProfileView.as_view(), name='profile'),
    path('account/addresses/', views.AddressListView.as_view(), name='address_list'),
    path('account/addresses/add/', views.AddressCreateView.as_view(), name='address_create'),
    path('account/addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_update'),
    path('account/addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('api/account/address/set-default/<str:address_type>/', views.set_default_address, name='set_default_address'),
    path('account/wishlist/', views.WishlistView.as_view(), name='wishlist'),
    
    # ==================== AVIS ====================
    path('products/<int:product_id>/review/', views.ReviewCreateView.as_view(), name='product_review_create'),
    path('services/<int:service_id>/review/', views.ReviewCreateView.as_view(), name='service_review_create'),
    path('api/reviews/<int:review_id>/like/', views.like_review, name='like_review'),
    
    # ==================== RÉSERVATIONS ====================
    # path('services/<int:service_id>/book/', views.BookingCreateView.as_view(), name='booking_create'),
    # path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    # path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    # path('api/bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    # path('booking/<int:pk>/payment/', views.BookingPaymentView.as_view(), name='booking_payment'),
    # path('booking/<int:booking_id>/confirm-payment/', views.confirm_booking_payment, name='confirm_booking_payment'),
    
    # ==================== RÉSERVATIONS ====================
    path('services/<int:service_id>/book/', views.BookingCreateView.as_view(), name='booking_create'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('api/bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:pk>/payment/', views.BookingPaymentView.as_view(), name='booking_payment'),
    path('api/bookings/<int:booking_id>/confirm-payment/', views.confirm_booking_payment, name='confirm_booking_payment'),
    
    # ==================== NEWSLETTER ====================
    path('api/newsletter/subscribe/', views.subscribe_newsletter, name='newsletter_subscribe'),
    path('api/newsletter/unsubscribe/', views.unsubscribe_newsletter, name='newsletter_unsubscribe'),
    
    # ==================== API POUR FRONTEND ====================
    path('api/products/<int:product_id>/variants/', views.get_product_variants, name='get_product_variants'),
    path('api/products/<int:product_id>/availability/', views.check_product_availability, name='check_product_availability'),
    path('api/services/<int:service_id>/available-dates/', views.get_available_dates, name='get_available_dates'),
    path('api/search/quick/', views.quick_search, name='quick_search'),
    
    # ==================== AUTHENTIFICATION ====================
    path('account/', include('django.contrib.auth.urls')),
    
    # ==================== REDIRECTIONS ====================
    path('favicon.png', RedirectView.as_view(url=static('favicon.png'))),


    # URLs pour les abonnements
    path('abonnements/', views.SubscriptionListView.as_view(), name='subscription'),
    path('abonnements/choisir/', views.SubscriptionChooseView.as_view(), name='subscription_choose'),
    path('abonnements/paiement/', views.SubscriptionPaymentView.as_view(), name='subscription_payment'),
    path('abonnements/confirmation/', views.SubscriptionConfirmationView.as_view(), name='subscription_confirmation'),
    path('abonnements/gestion/', views.SubscriptionManagementView.as_view(), name='subscription_management'),
    path('api/abonnements/subscribe/', views.subscribe_subscription, name='subscribe_subscription'),
]
handler404 = 'ecommerce.views.handler404'
handler500 = 'ecommerce.views.handler500'

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)