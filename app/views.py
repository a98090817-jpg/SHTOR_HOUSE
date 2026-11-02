import json
import secrets
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from .forms import EmailOrUsernameLoginForm, ProductForm, QuoteRequestForm
from .models import Favorite, Product

CURTAIN_INSPIRATION_ITEMS = [
    {
        'image_url': 'https://images.unsplash.com/photo-1578337834535-357ad7dccdfd?auto=format&fit=crop&w=800&q=80',
        'name': 'Ruby velvet curtains',
        'category': 'living_room',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1609423433459-a65b330ef5da?auto=format&fit=crop&w=800&q=80',
        'name': 'Classic window blinds',
        'category': 'office',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1691036562132-56a310d4b789?auto=format&fit=crop&w=800&q=80',
        'name': 'Soft sheer curtains',
        'category': 'bedroom',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80',
        'name': 'Bedroom drapes',
        'category': 'bedroom',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1617596225496-1d9da33a144b?auto=format&fit=crop&w=800&q=80',
        'name': 'Modern linen curtains',
        'category': 'living_room',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1643949914872-317d6047f107?auto=format&fit=crop&w=800&q=80',
        'name': 'Layered curtains and blinds',
        'category': 'custom',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1535126320463-c5c1b26b3e66?auto=format&fit=crop&w=800&q=80',
        'name': 'Light-filtering blinds',
        'category': 'office',
    },
    {
        'image_url': 'https://images.unsplash.com/photo-1528822855841-e8bf3134cdc9?auto=format&fit=crop&w=800&q=80',
        'name': 'Elegant sheer panels',
        'category': 'living_room',
    },
]


def home(request):
    user_model = get_user_model()
    category = request.GET.get('category')
    query = (request.GET.get('q') or '').strip()
    products = Product.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    carousel_products = (
        Product.objects.filter(is_active=True)
        .filter(Q(image__gt='') | Q(image_url__gt=''))
        .order_by('-is_featured', '-created_at')[:24]
    )
    showcase_items = [
        {
            'image_url': product.image.url if product.image else product.image_url,
            'name': product.name,
            'category': product.category,
        }
        for product in carousel_products
    ]
    if not showcase_items:
        media_products = Path(settings.MEDIA_ROOT) / 'products'
        if media_products.is_dir():
            showcase_images = sorted(
                (
                    image_path for image_path in media_products.iterdir()
                    if image_path.is_file()
                    and image_path.stat().st_size > 10000
                    and (
                        image_path.name.lower().startswith('curtain')
                        or image_path.name.lower() == 'jalyuzi.jpg'
                    )
                ),
                key=lambda image_path: (
                    image_path.name.lower() != 'jalyuzi.jpg',
                    image_path.name.lower(),
                ),
            )[:24]
            showcase_items.extend([
                {
                    'image_url': default_storage.url(f'products/{image_path.name}'),
                    'name': (
                        'Jalyuzi' if image_path.name.lower() == 'jalyuzi.jpg'
                        else f'Curtain style {index:02d}'
                    ),
                    'category': 'custom',
                }
                for index, image_path in enumerate(showcase_images, start=1)
            ])
    if len(showcase_items) < 8:
        showcase_items.extend(
            CURTAIN_INSPIRATION_ITEMS[:max(0, 8 - len(showcase_items))]
        )
    registered_user_count = user_model.objects.filter(
        is_active=True,
        is_staff=False,
        is_superuser=False,
    ).count()

    if category:
        products = products.filter(category=category)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(color__icontains=query)
            | Q(material__icontains=query)
            | Q(origin__icontains=query)
            | Q(description__icontains=query)
        )

    form = QuoteRequestForm()
    filtered_queryset = Product.objects.filter(is_active=True)
    if category:
        filtered_queryset = filtered_queryset.filter(category=category)
    form.fields['product'].queryset = filtered_queryset
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        form.fields['product'].queryset = filtered_queryset
        if form.is_valid():
            form.save()
            messages.success(request, 'Your quote request has been submitted successfully.')
            return redirect('home')

    featured_products = products.filter(is_featured=True)[:3]

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(user=request.user, product__in=products)
            .values_list('product_id', flat=True)
        )

    return render(request, 'app/home.html', {
        'products': products,
        'featured_products': featured_products,
        'carousel_products': carousel_products,
        'showcase_items': showcase_items,
        'registered_user_count': registered_user_count,
        'form': form,
        'categories': [
            ('all', 'All'),
            ('living_room', 'Living Room'),
            ('bedroom', 'Bedroom'),
            ('kitchen', 'Kitchen'),
            ('office', 'Office'),
            ('custom', 'Custom'),
        ],
        'active_category': category or 'all',
        'search_query': query,
        'favorite_ids': favorite_ids,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = QuoteRequestForm(initial={'product': product.id})

    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your request has been sent successfully.')
            return redirect('product_detail', slug=product.slug)

    is_favorite = (
        request.user.is_authenticated
        and Favorite.objects.filter(user=request.user, product=product).exists()
    )

    return render(request, 'app/product_detail.html', {
        'product': product,
        'form': form,
        'is_favorite': is_favorite,
    })


def product_delete(request, slug):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/product/{slug}/delete/')
    if not request.user.is_staff:
        messages.error(request, 'Only an administrator can delete products.')
        return redirect('home')
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'app/register.html', {'form': form})


def login_view(request):
    from django.contrib.auth.views import LoginView

    return LoginView.as_view(
        template_name='app/login.html',
        authentication_form=EmailOrUsernameLoginForm,
        redirect_authenticated_user=True,
    )(request)


def google_login(request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(request, 'Google sign-in is not configured yet.')
        return redirect('login')

    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    request.session.set_expiry(600)
    query = urlencode({
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'online',
        'prompt': 'select_account',
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{query}')


def google_callback(request):
    expected_state = request.session.pop('google_oauth_state', None)
    received_state = request.GET.get('state')
    if (
        not isinstance(expected_state, str)
        or not isinstance(received_state, str)
        or not secrets.compare_digest(received_state, expected_state)
    ):
        messages.error(request, 'Google sign-in session expired. Please try again.')
        return redirect('login')

    if request.GET.get('error'):
        if request.GET.get('error') == 'access_denied':
            messages.error(request, 'Google sign-in was cancelled.')
        else:
            messages.error(request, 'Google sign-in could not be completed.')
        return redirect('login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google sign-in was cancelled.')
        return redirect('login')
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(request, 'Google sign-in is not configured yet.')
        return redirect('login')

    token_payload = urlencode({
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }).encode()
    token_request = Request('https://oauth2.googleapis.com/token', data=token_payload, method='POST')
    try:
        with urlopen(token_request, timeout=10) as response:
            token_data = json.loads(response.read().decode())
        if not isinstance(token_data, dict):
            raise ValueError('Google returned an invalid token response.')
        access_token = token_data.get('access_token')
        token_type = token_data.get('token_type', '')
        if not isinstance(access_token, str) or not access_token or token_type.lower() != 'bearer':
            raise ValueError('Google returned an invalid access token.')
        user_request = Request(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        with urlopen(user_request, timeout=10) as response:
            google_user = json.loads(response.read().decode())
        if not isinstance(google_user, dict):
            raise ValueError('Google returned invalid profile data.')
    except (HTTPError, URLError, OSError, ValueError, UnicodeError, json.JSONDecodeError):
        messages.error(request, 'Google sign-in could not be completed.')
        return redirect('login')

    email = google_user.get('email')
    if (
        not isinstance(email, str)
        or not email.strip()
        or google_user.get('email_verified') is not True
        or not isinstance(google_user.get('sub'), str)
        or not google_user['sub']
    ):
        messages.error(request, 'Google did not provide a verified email address.')
        return redirect('login')

    user_model = get_user_model()
    email = email.strip()
    try:
        with transaction.atomic():
            user = user_model.objects.filter(email__iexact=email).first()
            if not user:
                base_username = (slugify(email.split('@')[0]) or 'google-user')[:140]
                username = base_username
                suffix = 1
                while user_model.objects.filter(username__iexact=username).exists():
                    username = f'{base_username[:140 - len(str(suffix)) - 1]}-{suffix}'
                    suffix += 1
                user = user_model.objects.create_user(username=username, email=email)
    except IntegrityError:
        user = user_model.objects.filter(email__iexact=email).first()
        if not user:
            raise

    if not user.is_active:
        messages.error(request, 'Google sign-in could not be completed.')
        return redirect('login')

    login(request, user)
    profile_picture = google_user.get('picture')
    if isinstance(profile_picture, str) and profile_picture:
        request.session['google_profile_picture'] = profile_picture
    else:
        request.session.pop('google_profile_picture', None)
    return redirect('home')


def product_create(request):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/product/create/')
    if not request.user.is_staff:
        messages.error(request, 'Only an administrator can add products.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'{product.name} was added successfully.')
            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'app/product_create.html', {'form': form})


def quote_request(request):
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your request has been sent successfully.')
            return redirect('home')

    return redirect('home')


def wishlist_page(request):
    # Foydalanuvchining sevimli pardalari sahifasi.
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/wishlist/')

    favorites = (
        Favorite.objects.filter(user=request.user, product__is_active=True)
        .select_related('product')
        .order_by('-created_at')
    )
    favorite_ids = {fav.product_id for fav in favorites}
    products = [fav.product for fav in favorites]

    return render(request, 'app/wishlist.html', {
        'products': products,
        'favorite_ids': favorite_ids,
    })

@require_POST
def toggle_favorite(request, slug):
    # AJAX: mahsulotni sevimlilarga qo'shish yoki olib tashlash.
    if not request.user.is_authenticated:
        return JsonResponse(
            {'ok': False, 'login_required': True,
             'message': 'Sevimlilarga qo\u2018shish uchun tizimga kiring.'},
            status=401,
        )

    product = get_object_or_404(Product, slug=slug)
    favorite = Favorite.objects.filter(user=request.user, product=product)
    if favorite.exists():
        favorite.delete()
        is_favorite = False
    else:
        Favorite.objects.create(user=request.user, product=product)
        is_favorite = True
    count = Favorite.objects.filter(user=request.user).count()
    return JsonResponse({'ok': True, 'is_favorite': is_favorite, 'count': count})
