# dashboard/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, UpdateView, View
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from datetime import datetime, timedelta

from core import models
from core.models import (
    Order, Booking, Product, Service, User, Review,
    NewsletterSubscriber, Payment, Cart, Wishlist,OrderItem
)


@method_decorator(staff_member_required, name='dispatch')
class DashboardHomeView(TemplateView):
    """Tableau de bord principal"""
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistiques du jour
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        # Commandes
        orders_today = Order.objects.filter(
            created_at__date=today
        ).count()
        orders_pending = Order.objects.filter(
            status='pending'
        ).count()
        orders_processing = Order.objects.filter(
            status='processing'
        ).count()
        orders_delivered_today = Order.objects.filter(
            status='delivered',
            updated_at__date=today
        ).count()

        # Chiffre d'affaires
        revenue_today = Order.objects.filter(
            created_at__date=today,
            payment_status='paid'
        ).aggregate(total=Sum('grand_total'))['total'] or 0

        revenue_month = Order.objects.filter(
            created_at__month=today.month,
            created_at__year=today.year,
            payment_status='paid'
        ).aggregate(total=Sum('grand_total'))['total'] or 0

        # Réservations
        bookings_today = Booking.objects.filter(
            date=today
        ).count()
        bookings_pending = Booking.objects.filter(
            status='pending'
        ).count()

        # Utilisateurs
        new_users_today = User.objects.filter(
            date_joined__date=today
        ).count()
        total_users = User.objects.count()

        # Newsletter
        newsletter_subscribers = NewsletterSubscriber.objects.filter(
            is_active=True
        ).count()

        # Produits en rupture
        out_of_stock = Product.objects.filter(
            is_active=True,
            track_quantity=True,
            quantity__lte=0,
            allow_backorder=False
        ).count()

        low_stock = Product.objects.filter(
            is_active=True,
            track_quantity=True,
            quantity__gt=0,
            quantity__lte=F('low_stock_threshold')
        ).count()

        context.update({
            'orders_today': orders_today,
            'orders_pending': orders_pending,
            'orders_processing': orders_processing,
            'orders_delivered_today': orders_delivered_today,
            'revenue_today': revenue_today,
            'revenue_month': revenue_month,
            'bookings_today': bookings_today,
            'bookings_pending': bookings_pending,
            'new_users_today': new_users_today,
            'total_users': total_users,
            'newsletter_subscribers': newsletter_subscribers,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
        })

        # Graphiques - Commandes des 7 derniers jours
        last_7_days = []
        orders_chart = []
        revenue_chart = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_orders = Order.objects.filter(
                created_at__date=day
            ).count()
            day_revenue = Order.objects.filter(
                created_at__date=day,
                payment_status='paid'
            ).aggregate(total=Sum('grand_total'))['total'] or 0

            last_7_days.append(day.strftime('%d/%m'))
            orders_chart.append(day_orders)
            revenue_chart.append(float(day_revenue))

        context['chart_labels'] = last_7_days
        context['chart_orders'] = orders_chart
        context['chart_revenue'] = revenue_chart

        # Dernières commandes
        context['recent_orders'] = Order.objects.order_by('-created_at')[:10]

        # Dernières réservations
        context['recent_bookings'] = Booking.objects.order_by('-created_at')[:10]

        top_products = OrderItem.objects.values(
            'product__id', 'product__name', 'product__slug'
        ).annotate(
            total_sold=Sum('quantity')
        ).filter(
            product__isnull=False
        ).order_by('-total_sold')[:5]

        context['top_products'] = top_products

        return context


@method_decorator(staff_member_required, name='dispatch')
class OrderManagementView(ListView):
    """Gestion des commandes"""
    model = Order
    template_name = 'dashboard/orders/list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')

        # Filtres
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search) |
                Q(shipping_address__first_name__icontains=search) |
                Q(shipping_address__last_name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.ORDER_STATUS_CHOICES
        context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES

        # Compteurs par statut
        context['counts'] = {
            'all': Order.objects.count(),
            'pending': Order.objects.filter(status='pending').count(),
            'processing': Order.objects.filter(status='processing').count(),
            'shipped': Order.objects.filter(status='shipped').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
        }

        # Filtres actifs
        for key in ['status', 'payment_status', 'date_from', 'date_to', 'search']:
            context[key] = self.request.GET.get(key, '')

        return context


@method_decorator(staff_member_required, name='dispatch')
class OrderDetailView(UpdateView):
    """Détail et mise à jour d'une commande"""
    model = Order
    template_name = 'dashboard/orders/detail.html'
    fields = ['status', 'payment_status', 'tracking_number', 'shipping_method']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.ORDER_STATUS_CHOICES
        context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES
        return context

    def get_success_url(self):
        messages.success(self.request, f'Commande #{self.object.order_number} mise à jour')
        return reverse_lazy('dashboard_order_detail', kwargs={'pk': self.object.pk})


@method_decorator(staff_member_required, name='dispatch')
class BookingManagementView(ListView):
    """Gestion des réservations"""
    model = Booking
    template_name = 'dashboard/bookings/list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = Booking.objects.all().order_by('-date', '-start_time')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(date=date)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search) |
                Q(service__name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Booking.BOOKING_STATUS_CHOICES
        context['today'] = timezone.now().date()

        # Compteurs
        context['counts'] = {
            'all': Booking.objects.count(),
            'pending': Booking.objects.filter(status='pending').count(),
            'confirmed': Booking.objects.filter(status='confirmed').count(),
            'today': Booking.objects.filter(date=timezone.now().date()).count(),
        }

        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductManagementView(ListView):
    """Gestion des produits"""
    model = Product
    template_name = 'dashboard/products/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search)
            )

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__id=category)

        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'in_stock':
            queryset = queryset.filter(quantity__gt=0)
        elif stock_status == 'out_of_stock':
            queryset = queryset.filter(quantity__lte=0)
        elif stock_status == 'low_stock':
            queryset = queryset.filter(
                quantity__gt=0,
                quantity__lte=models.F('low_stock_threshold')
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Category
        context['categories'] = Category.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class PostCreateView(TemplateView):
    """Interface unifiée pour créer des posts (produits, services, blog)"""
    template_name = 'dashboard/posts/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.kwargs.get('post_type', 'product')
        
        from core.models import Category, Brand
        context['categories'] = Category.objects.filter(is_active=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        
        return context


# ==================== API ENDPOINTS ====================

@staff_member_required
@csrf_exempt
def update_order_status(request, order_id):
    """API pour mettre à jour le statut d'une commande"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = get_object_or_404(Order, id=order_id)
            
            new_status = data.get('status')
            if new_status and new_status in dict(Order.ORDER_STATUS_CHOICES):
                order.status = new_status
                order.save()
                
                # Créer une notification
                from core.models import Notification
                Notification.objects.create(
                    user=order.user,
                    type='order_status',
                    title=f'Commande #{order.order_number}',
                    message=f'Votre commande est maintenant {order.get_status_display()}',
                    related_id=order.id,
                    related_type='order'
                )
                
                return JsonResponse({
                    'success': True,
                    'status': order.get_status_display()
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})


@staff_member_required
@csrf_exempt
def update_booking_status(request, booking_id):
    """API pour mettre à jour le statut d'une réservation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            booking = get_object_or_404(Booking, id=booking_id)
            
            new_status = data.get('status')
            if new_status and new_status in dict(Booking.BOOKING_STATUS_CHOICES):
                booking.status = new_status
                booking.save()
                
                return JsonResponse({
                    'success': True,
                    'status': booking.get_status_display()
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})


@staff_member_required
def dashboard_stats_api(request):
    """API pour les statistiques en temps réel"""
    today = timezone.now().date()
    
    # Commandes en attente
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Réservations aujourd'hui
    bookings_today = Booking.objects.filter(date=today).count()
    
    # Chiffre d'affaires du jour
    revenue_today = Order.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Nouveaux utilisateurs aujourd'hui
    new_users = User.objects.filter(date_joined__date=today).count()
    
    return JsonResponse({
        'pending_orders': pending_orders,
        'bookings_today': bookings_today,
        'revenue_today': float(revenue_today),
        'new_users': new_users,
        'timestamp': timezone.now().isoformat()
    })


@staff_member_required
def quick_product_create(request):
    """Création rapide de produit (AJAX)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            product = Product.objects.create(
                name=data.get('name'),
                slug=data.get('name').lower().replace(' ', '-'),
                sku=data.get('sku', f"PRD-{timezone.now().strftime('%Y%m%d%H%M%S')}"),
                price=data.get('price', 0),
                description=data.get('description', ''),
                short_description=data.get('short_description', ''),
                quantity=data.get('quantity', 0),
                is_active=data.get('is_active', True)
            )
            
            return JsonResponse({
                'success': True,
                'id': product.id,
                'name': product.name,
                'redirect_url': reverse_lazy('dashboard_product_edit', kwargs={'pk': product.id})
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})