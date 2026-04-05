# dashboard/urls.py
from django.urls import path
from . import views

# app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardHomeView.as_view(), name='dashboard_home'),
    
    # Commandes
    path('orders/', views.OrderManagementView.as_view(), name='dashboard_order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='dashboard_order_detail'),
    
    # Réservations
    path('bookings/', views.BookingManagementView.as_view(), name='dashboard_booking_list'),
    
    # Produits
    path('products/', views.ProductManagementView.as_view(), name='dashboard_product_list'),
    
    # Création de posts
    path('posts/create/<str:post_type>/', views.PostCreateView.as_view(), name='dashboard_post_create'),
    
    # API Endpoints
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('api/bookings/<int:booking_id>/status/', views.update_booking_status, name='update_booking_status'),
    path('api/products/quick-create/', views.quick_product_create, name='quick_product_create'),
]