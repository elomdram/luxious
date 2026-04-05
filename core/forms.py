# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date
import re

from .models import (
    User, Address, Product, Service, Review, Booking, 
    NewsletterSubscriber, Order, Coupon, BlogPost, Page,Category,Brand
)

# ==================== FORMULAIRES UTILISATEUR ====================

from django.contrib.auth.forms import AuthenticationForm

class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label
            })

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone")
    birth_date = forms.DateField(
        required=False, 
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=[('', '---------'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        required=False,
        label="Genre"
    )
    newsletter_subscribed = forms.BooleanField(
        required=False, 
        initial=True,
        label="S'abonner à la newsletter"
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name', 'phone', 'birth_date', 
            'gender', 'newsletter_subscribed'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un utilisateur avec cette adresse email existe déjà.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Validation basique du numéro de téléphone
            phone_regex = r'^\+?[0-9\s\-\(\)]{10,20}$'
            if not re.match(phone_regex, phone):
                raise ValidationError("Format de numéro de téléphone invalide.")
        return phone
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 13:
                raise ValidationError("Vous devez avoir au moins 13 ans pour vous inscrire.")
            if age > 120:
                raise ValidationError("Date de naissance invalide.")
        return birth_date
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.birth_date = self.cleaned_data.get('birth_date')
        user.gender = self.cleaned_data.get('gender')
        user.newsletter_subscribed = self.cleaned_data.get('newsletter_subscribed', False)
        
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Adresse email")
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="Mot de passe actuel (pour confirmer les modifications)"
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="Nouveau mot de passe"
    )
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="Confirmation du nouveau mot de passe"
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'birth_date', 'gender', 'newsletter_subscribed'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'phone': 'Téléphone',
            'birth_date': 'Date de naissance',
            'gender': 'Genre',
            'newsletter_subscribed': 'Recevoir la newsletter',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Un utilisateur avec cette adresse email existe déjà.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_regex = r'^\+?[0-9\s\-\(\)]{10,20}$'
            if not re.match(phone_regex, phone):
                raise ValidationError("Format de numéro de téléphone invalide.")
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        current_password = cleaned_data.get('current_password')
        
        # Vérifier si l'utilisateur veut changer son mot de passe
        if new_password1 or new_password2 or current_password:
            if not current_password:
                raise ValidationError({
                    'current_password': "Le mot de passe actuel est requis pour changer le mot de passe."
                })
            
            if not self.instance.check_password(current_password):
                raise ValidationError({
                    'current_password': "Le mot de passe actuel est incorrect."
                })
            
            if new_password1 != new_password2:
                raise ValidationError({
                    'new_password2': "Les mots de passe ne correspondent pas."
                })
            
            if len(new_password1) < 8:
                raise ValidationError({
                    'new_password1': "Le mot de passe doit contenir au moins 8 caractères."
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Mettre à jour le mot de passe si fourni
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        return user

# ==================== FORMULAIRES ADRESSE ====================

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'first_name', 'last_name', 'company', 'street', 'complement',
            'postal_code', 'city', 'country', 'phone',
            'is_default_shipping', 'is_default_billing'
        ]
        widgets = {
            'complement': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'company': 'Entreprise (optionnel)',
            'street': 'Adresse',
            'complement': 'Complément d\'adresse',
            'postal_code': 'Code postal',
            'city': 'Ville',
            'country': 'Pays',
            'phone': 'Téléphone',
            'is_default_shipping': 'Utiliser comme adresse de livraison par défaut',
            'is_default_billing': 'Utiliser comme adresse de facturation par défaut',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Définir la valeur par défaut pour le pays
        if not self.instance.pk:
            self.fields['country'].initial = "Togo"
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_regex = r'^\+?[0-9\s\-\(\)]{10,20}$'
            if not re.match(phone_regex, phone):
                raise ValidationError("Format de numéro de téléphone invalide.")
        return phone
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            # Validation basique du code postal
            postal_regex = r'^[0-9A-Za-z\s\-]{3,10}$'
            if not re.match(postal_regex, postal_code):
                raise ValidationError("Format de code postal invalide.")
        return postal_code
    
    def save(self, commit=True):
        address = super().save(commit=False)
        if self.user:
            address.user = self.user
        
        if commit:
            address.save()
            
            # Gérer les adresses par défaut
            if address.is_default_shipping:
                Address.objects.filter(user=self.user, is_default_shipping=True).exclude(pk=address.pk).update(is_default_shipping=False)
                self.user.default_shipping_address = address
                self.user.save()
            
            if address.is_default_billing:
                Address.objects.filter(user=self.user, is_default_billing=True).exclude(pk=address.pk).update(is_default_billing=False)
                self.user.default_billing_address = address
                self.user.save()
        
        return address

# ==================== FORMULAIRES COMMANDE ====================

class CheckoutForm(forms.Form):
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label=None,
        label="Adresse de livraison",
        widget=forms.RadioSelect
    )
    billing_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label=None,
        label="Adresse de facturation",
        widget=forms.RadioSelect
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('mobile_money', 'Mobile Money'),
            ('payoneer', 'Payoneer'),
            ('cash_delivery', 'Paiement à la livraison'),
            ('credit_card', 'Carte de crédit'),
        ],
        label="Méthode de paiement",
        widget=forms.RadioSelect
    )
    use_same_address = forms.BooleanField(
        required=False,
        initial=True,
        label="Utiliser la même adresse pour la livraison et la facturation"
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notes supplémentaires pour la commande...'}),
        label="Notes (optionnel)"
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label="J'accepte les conditions générales de vente"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        if user:
            addresses = Address.objects.filter(user=user)
            self.fields['shipping_address'].queryset = addresses
            self.fields['billing_address'].queryset = addresses
            
            # Définir les valeurs par défaut
            if addresses.filter(is_default_shipping=True).exists():
                self.fields['shipping_address'].initial = addresses.filter(is_default_shipping=True).first()
            elif addresses.exists():
                self.fields['shipping_address'].initial = addresses.first()
            
            if addresses.filter(is_default_billing=True).exists():
                self.fields['billing_address'].initial = addresses.filter(is_default_billing=True).first()
            elif addresses.exists():
                self.fields['billing_address'].initial = addresses.first()
    
    def clean(self):
        cleaned_data = super().clean()
        use_same_address = cleaned_data.get('use_same_address')
        
        if use_same_address:
            cleaned_data['billing_address'] = cleaned_data.get('shipping_address')
        
        return cleaned_data

class CouponApplyForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        label="Code promo",
        widget=forms.TextInput(attrs={'placeholder': 'Entrez votre code promo'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.cart = kwargs.pop('cart', None)
        super().__init__(*args, **kwargs)
    
    def clean_code(self):
        code = self.cleaned_data.get('code').upper().strip()
        
        try:
            coupon = Coupon.objects.get(code=code)
            
            # Vérifier la validité du coupon
            if not coupon.is_valid(user=self.user, cart=self.cart):
                raise ValidationError("Ce code promo n'est pas valide ou a expiré.")
            
            return code
        except Coupon.DoesNotExist:
            raise ValidationError("Code promo invalide.")

# ==================== FORMULAIRES AVIS ====================

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[
                (1, '1 étoile'),
                (2, '2 étoiles'),
                (3, '3 étoiles'),
                (4, '4 étoiles'),
                (5, '5 étoiles'),
            ]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Partagez votre expérience...'}),
        }
        labels = {
            'rating': 'Note',
            'title': 'Titre de votre avis',
            'comment': 'Commentaire',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        self.service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Vérifier qu'un produit ou service est spécifié
        if not self.product and not self.service:
            raise ValidationError("Un produit ou service doit être spécifié.")
        
        # Vérifier si l'utilisateur a déjà laissé un avis pour ce produit/service
        if self.user:
            existing_review = Review.objects.filter(
                user=self.user,
                product=self.product,
                service=self.service
            ).exists()
            
            if existing_review:
                if self.product:
                    raise ValidationError("Vous avez déjà laissé un avis pour ce produit.")
                else:
                    raise ValidationError("Vous avez déjà laissé un avis pour ce service.")
        
        return cleaned_data

# ==================== FORMULAIRES RÉSERVATION ====================

class BookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
        label="Date"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Heure de début"
    )
    
    class Meta:
        model = Booking
        fields = ['date', 'start_time', 'participants', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Informations supplémentaires...'}),
        }
        labels = {
            'participants': 'Nombre de participants',
            'notes': 'Notes (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        
        if self.service:
            self.fields['participants'].initial = 1
            self.fields['participants'].max_value = self.service.max_participants
    
    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        
        if selected_date < date.today():
            raise ValidationError("La date ne peut pas être dans le passé.")
        
        # Vérifier que la date n'est pas trop éloignée (max 3 mois)
        max_date = date.today() + timezone.timedelta(days=90)
        if selected_date > max_date:
            raise ValidationError("Les réservations ne peuvent pas dépasser 3 mois à l'avance.")
        
        return selected_date
    
    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        selected_date = self.cleaned_data.get('date')
        
        if selected_date and start_time:
            # Vérifier que l'horaire n'est pas dans le passé si c'est aujourd'hui
            if selected_date == date.today():
                current_time = timezone.now().time()
                if start_time < current_time:
                    raise ValidationError("L'horaire ne peut pas être dans le passé.")
            
            # Vérifier les horaires d'ouverture (exemple: 8h-18h)
            if start_time < datetime.strptime('08:00', '%H:%M').time():
                raise ValidationError("L'établissement ouvre à 8h00.")
            
            if start_time > datetime.strptime('18:00', '%H:%M').time():
                raise ValidationError("L'établissement ferme à 18h00.")
        
        return start_time
    
    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        
        if self.service and participants > self.service.max_participants:
            raise ValidationError(
                f"Ce service accepte maximum {self.service.max_participants} participants."
            )
        
        if participants < 1:
            raise ValidationError("Le nombre de participants doit être d'au moins 1.")
        
        return participants
    
    def clean(self):
        cleaned_data = super().clean()
        selected_date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        
        if selected_date and start_time and self.service:
            # Vérifier les conflits de réservation
            duration = self.service.duration
            end_time = self.calculate_end_time(start_time, duration)
            
            conflicting_bookings = Booking.objects.filter(
                service=self.service,
                date=selected_date,
                status__in=['pending', 'confirmed'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if conflicting_bookings.exists():
                raise ValidationError(
                    "Ce créneau horaire n'est pas disponible. Veuillez choisir un autre horaire."
                )
        
        return cleaned_data
    
    def calculate_end_time(self, start_time, duration_minutes):
        """Calcule l'heure de fin à partir de l'heure de début et de la durée"""
        start_datetime = datetime.combine(date.today(), start_time)
        end_datetime = start_datetime + timezone.timedelta(minutes=duration_minutes)
        return end_datetime.time()
    
    def save(self, commit=True):
        booking = super().save(commit=False)
        
        if self.user:
            booking.user = self.user
        if self.service:
            booking.service = self.service
            booking.price = self.service.price
            booking.total = self.service.price * self.cleaned_data.get('participants', 1)
            
            # Calculer l'heure de fin
            duration = self.service.duration
            start_time = self.cleaned_data.get('start_time')
            if start_time:
                booking.end_time = self.calculate_end_time(start_time, duration)
        
        if commit:
            booking.save()
        
        return booking

# ==================== FORMULAIRES NEWSLETTER ====================

class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Votre adresse email'})
        }
        labels = {
            'email': 'Email'
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Vérifier si l'email est déjà abonné et actif
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("Cette adresse email est déjà abonnée à notre newsletter.")
        
        return email
    
    def save(self, commit=True):
        # Si l'email existe déjà mais est désactivé, le réactiver
        email = self.cleaned_data['email']
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
        except NewsletterSubscriber.DoesNotExist:
            subscriber = super().save(commit=False)
        
        if commit:
            subscriber.save()
        
        return subscriber

class NewsletterUnsubscribeForm(forms.Form):
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'placeholder': 'Votre adresse email'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("Cette adresse email n'est pas abonnée à notre newsletter.")
        
        return email

# ==================== FORMULAIRES RECHERCHE ====================

class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Rechercher des produits, services, articles...',
            'class': 'search-input'
        }),
        label=""
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[],
        label="Catégorie"
    )
    
    min_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Prix min'}),
        label="Prix minimum"
    )
    
    max_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Prix max'}),
        label="Prix maximum"
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Trier par'),
            ('created_at', 'Plus récents'),
            ('price_asc', 'Prix croissant'),
            ('price_desc', 'Prix décroissant'),
            ('name', 'Nom A-Z'),
            ('popularity', 'Popularité'),
        ],
        label="Trier par"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamiquement charger les catégories
        from .models import Category
        categories = Category.objects.filter(is_active=True, parent__isnull=True)
        category_choices = [('', 'Toutes les catégories')] + [(cat.slug, cat.name) for cat in categories]
        self.fields['category'].choices = category_choices

# ==================== FORMULAIRES ADMIN/STAFF ====================

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'short_description', 'sku', 'price',
            'compare_price', 'cost', 'product_type', 'categories', 'brand',
            'quantity', 'low_stock_threshold', 'track_quantity', 'allow_backorder',
            'is_active', 'is_featured', 'requires_shipping', 'weight',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'name', 'slug', 'description', 'short_description', 'price', 'duration',
            'category', 'is_active', 'image', 'requires_booking', 'max_participants'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'excerpt', 'content', 'author', 'image',
            'categories', 'is_published', 'meta_title', 'meta_description'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title', 'slug', 'content', 'is_active', 'meta_title', 'meta_description']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code', 'discount_type', 'discount_value', 'minimum_order', 'maximum_discount',
            'usage_limit', 'valid_from', 'valid_to', 'is_active', 'products', 'categories'
        ]
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'products': forms.SelectMultiple(attrs={'class': 'select2'}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        
        if valid_from and valid_to:
            if valid_from >= valid_to:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")
        
        if discount_type == 'percentage' and discount_value:
            if discount_value > 100:
                raise ValidationError("La remise en pourcentage ne peut pas dépasser 100%.")
        
        return cleaned_data

# ==================== FORMULAIRES CONTACT ====================

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Votre nom")
    email = forms.EmailField(label="Votre email")
    subject = forms.CharField(max_length=200, label="Sujet")
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label="Message"
    )
    phone = forms.CharField(max_length=20, required=False, label="Téléphone (optionnel)")
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_regex = r'^\+?[0-9\s\-\(\)]{10,20}$'
            if not re.match(phone_regex, phone):
                raise ValidationError("Format de numéro de téléphone invalide.")
        return phone

# ==================== FORMULAIRES FILTRES ====================

class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True, parent__isnull=True),
        required=False,
        empty_label="Toutes les catégories",
        label="Catégorie"
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les marques",
        label="Marque"
    )
    min_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Min'}),
        label="Prix min"
    )
    max_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Max'}),
        label="Prix max"
    )
    in_stock = forms.BooleanField(
        required=False,
        label="En stock seulement"
    )
    is_featured = forms.BooleanField(
        required=False,
        label="Produits en vedette"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Réorganiser l'ordre des champs si nécessaire
        self.order_fields(['category', 'brand', 'min_price', 'max_price', 'in_stock', 'is_featured'])

class ServiceFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True, services__isnull=False).distinct(),
        required=False,
        empty_label="Toutes les catégories",
        label="Catégorie"
    )
    requires_booking = forms.BooleanField(
        required=False,
        label="Nécessite réservation"
    )
    max_participants = forms.IntegerField(
        required=False,
        min_value=1,
        label="Participants maximum"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['category', 'requires_booking', 'max_participants'])