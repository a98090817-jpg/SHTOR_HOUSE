import json
import mimetypes
import secrets
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import requests

from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import http_date
from django.utils.text import slugify
from django.views.decorators.http import require_GET, require_POST
from .activity import build_user_directory, notify_admin
from .forms import AdminMessageForm, EmailOrUsernameLoginForm, ProductForm, QuoteRequestForm, CustomUserCreationForm
from .models import (
    AdminMessage,
    AdminNotification,
    ConcurrentLoginSlot,
    Favorite,
    Product,
    QuoteRequest,
    SiteVisitCounter,
)
from .visit_counter import increment_visit_count

# Katalogdagi saralash turlari. Birinchi variant — standart ko'rinish.
DEFAULT_SORT = 'featured'
SORT_OPTIONS = [
    ('featured', 'Featured'),
    ('newest', 'Newest'),
    ('price_asc', 'Price: low to high'),
    ('price_desc', 'Price: high to low'),
    ('name_asc', 'Name: A–Z'),
    ('name_desc', 'Name: Z–A'),
]
SORT_ORDERINGS = {
    'featured': ('-is_featured', '-created_at'),
    'newest': ('-created_at',),
    'price_asc': ('price', '-created_at'),
    'price_desc': ('-price', '-created_at'),
    'name_asc': ('name', '-created_at'),
    'name_desc': ('-name', '-created_at'),
}

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


def _product_image_url(product):
    """Mahsulot rasmining ishonchli manzili.

    Avval bazadagi nusxa, keyin diskdagi fayl, oxirida tashqi URL ishlatiladi.
    """
    if product.image_data:
        return reverse('product_image', args=[product.pk])
    if product.image:
        return product.image.url
    return product.image_url


def _parse_price(value):
    """Narx filtrini xavfsiz songa aylantiradi.

    Bo'sh, noto'g'ri yoki manfiy qiymat e'tiborsiz qoldiriladi.
    """
    if value is None:
        return None
    cleaned = str(value).replace(',', '.').strip()
    if not cleaned:
        return None
    try:
        amount = Decimal(cleaned)
        if not amount.is_finite() or amount < 0:
            return None
        return amount.quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError):
        return None


def _format_price(value):
    """Decimal narxni input uchun qulay ko'rinishda qaytaradi."""
    if value is None:
        return ''
    text = format(value, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def home(request):
    category = (request.GET.get('category') or '').strip() or None
    if category and category not in dict(Product.CATEGORY_CHOICES):
        category = None
    query = (request.GET.get('q') or '').strip()

    active_sort = (request.GET.get('sort') or DEFAULT_SORT).strip().lower()
    if active_sort not in SORT_ORDERINGS:
        active_sort = DEFAULT_SORT

    min_price = _parse_price(request.GET.get('min_price'))
    max_price = _parse_price(request.GET.get('max_price'))
    # Foydalanuvchi "dan" va "gacha" ni almashtirib yuborsa ham filtr ishlaydi.
    if min_price is not None and max_price is not None and min_price > max_price:
        min_price, max_price = max_price, min_price

    has_price_filter = min_price is not None or max_price is not None
    has_filters = has_price_filter or active_sort != DEFAULT_SORT

    products = Product.objects.filter(is_active=True).order_by(*SORT_ORDERINGS[active_sort])
    carousel_products = (
        Product.objects.filter(is_active=True)
        .filter(Q(image__gt='') | Q(image_url__gt='') | Q(image_data__isnull=False))
        .order_by('-is_featured', '-created_at')[:24]
    )
    showcase_items = [
        {
            'image_url': _product_image_url(product),
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

    # Saytga tashrif buyurganlar soni — baza + lokal fayl + tashqi zaxira.
    # Qiymat hech qachon kamaymaydi va 0 ga tushmaydi.
    visits_count = increment_visit_count()

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

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)

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
        'site_visit_count': visits_count,
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
        'sort_options': SORT_OPTIONS,
        'active_sort': active_sort,
        'min_price': _format_price(min_price),
        'max_price': _format_price(max_price),
        'has_price_filter': has_price_filter,
        'has_filters': has_filters,
    })


@require_GET
def product_image(request, pk):
    """Mahsulot rasmini bazadan (yoki diskdan) uzatadi.

    Rasm bazada saqlangani uchun har qanday qurilma va har qanday server
    holatida ham ko'rinadi.
    """
    product = get_object_or_404(Product, pk=pk)

    if product.image_data is not None:
        data = bytes(product.image_data)
        content_type = product.image_content_type or 'image/webp'
    elif product.image:
        try:
            product.image.open('rb')
            data = product.image.read()
        except (FileNotFoundError, OSError, ValueError):
            raise Http404('Image file is missing')
        content_type = mimetypes.guess_type(product.image.name)[0] or 'image/webp'
    else:
        raise Http404('Product has no image')

    if not data:
        raise Http404('Product image is empty')

    response = HttpResponse(data, content_type=content_type)
    response['Content-Length'] = str(len(data))
    # Brauzer rasmni uzoq saqlaydi; ?v=... parametri yangi rasmda URL ni o'zgartiradi.
    response['Cache-Control'] = 'public, max-age=604800'
    if product.image_stored_at:
        response['Last-Modified'] = http_date(product.image_stored_at.timestamp())
    return response


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = QuoteRequestForm(initial={'product': product.id})

    # Ko'rishlar soni — faqat oddiy foydalanuvchilar va sahifa ochilganda.
    # Adminning o'z tekshiruvlari statistikani shishirib yubormaydi.
    if request.method == 'GET' and not request.user.is_staff:
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['login_method'] = 'password'
            request.session['login_notification_kind'] = 'register'
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()

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
    created = False
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
                created = True
    except IntegrityError:
        user = user_model.objects.filter(email__iexact=email).first()
        if not user:
            raise

    if not user.is_active:
        messages.error(request, 'This account has been blocked by an administrator.')
        return redirect('login')

    request.session['login_method'] = 'google'
    request.session['login_notification_kind'] = 'register' if created else 'login'
    login(request, user)
    # OAuth state uchun qo'yilgan 10 daqiqalik muddatni bekor qilamiz:
    # aks holda Google bilan kirgan foydalanuvchi 10 daqiqada chiqib ketadi.
    request.session.set_expiry(None)
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


def admin_dashboard(request):
    """Adminlar uchun sayt statistikasi.

    Faqat `is_staff` foydalanuvchilarga ochiq. Tashrif hisoblagichi bu yerda
    oshirilmaydi — dashboard ochish sayt tashrifi sifatida hisoblanmaydi.
    """
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={reverse("admin_dashboard")}')
    if not request.user.is_staff:
        messages.error(request, 'Only an administrator can open the dashboard.')
        return redirect('home')

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    today = timezone.localdate()
    chart_start = today - timedelta(days=6)

    user_model = get_user_model()
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_requests = QuoteRequest.objects.count()
    requests_last_7 = QuoteRequest.objects.filter(created_at__gte=week_ago).count()
    total_users = user_model.objects.filter(is_staff=False).count()
    users_last_7 = user_model.objects.filter(
        is_staff=False, date_joined__gte=week_ago
    ).count()
    total_favorites = Favorite.objects.count()
    user_directory, user_stats = build_user_directory(limit=6)
    visits_count = max(
        SiteVisitCounter.objects.filter(pk=1)
        .values_list('count', flat=True)
        .first()
        or 0,
        int(getattr(settings, 'VISIT_COUNTER_BASELINE', 0)),
    )

    top_viewed = list(
        Product.objects.filter(is_active=True)
        .order_by('-view_count', '-created_at')[:8]
    )
    top_requested = list(
        Product.objects.annotate(request_total=Count('quote_requests'))
        .filter(request_total__gt=0)
        .order_by('-request_total', '-created_at')[:8]
    )
    recent_requests = (
        QuoteRequest.objects.select_related('product')
        .order_by('-created_at')[:12]
    )
    recent_products = list(Product.objects.order_by('-created_at')[:8])

    for product in top_viewed + top_requested + recent_products:
        product.preview_url = _product_image_url(product)

    # Oxirgi 7 kundagi so'rovlar diagrammasi (kunma-kun).
    daily_rows = (
        QuoteRequest.objects.filter(created_at__date__gte=chart_start)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Count('id'))
    )
    daily_map = {row['day']: row['total'] for row in daily_rows}
    request_series = []
    for offset in range(7):
        day = chart_start + timedelta(days=offset)
        total = daily_map.get(day, 0)
        request_series.append({'date': day, 'total': total})
    max_daily = max((item['total'] for item in request_series), default=0) or 1
    for item in request_series:
        item['percent'] = (
            max(8, round(item['total'] * 74 / max_daily)) if item['total'] else 0
        )

    category_labels = dict(Product.CATEGORY_CHOICES)
    category_rows = list(
        Product.objects.filter(is_active=True)
        .values('category')
        .annotate(total=Count('id'))
        .order_by('-total', 'category')
    )
    for row in category_rows:
        row['label'] = category_labels.get(row['category'], row['category'])
        row['percent'] = round(row['total'] * 100 / max(active_products, 1))

    return render(request, 'app/dashboard.html', {
        'total_products': total_products,
        'active_products': active_products,
        'total_requests': total_requests,
        'requests_last_7': requests_last_7,
        'total_users': total_users,
        'users_last_7': users_last_7,
        'total_favorites': total_favorites,
        'visits_count': visits_count,
        'top_viewed': top_viewed,
        'top_requested': top_requested,
        'recent_requests': recent_requests,
        'recent_products': recent_products,
        'request_series': request_series,
        'category_rows': category_rows,
        'user_directory': user_directory,
        'user_stats': user_stats,
        'google_users': user_stats['google_users'],
        'password_users': user_stats['password_users'],
        'blocked_users': user_stats['blocked_users'],
        'google_logins': user_stats['google_logins'],
        'unread_notifications': AdminNotification.objects.filter(is_read=False).count(),
    })

def _staff_guard(request, next_url):
    """Administrator bo'lmagan foydalanuvchilarni sahifadan qaytaradi."""
    if not request.user.is_authenticated:
        return redirect(f'/login/?next={next_url}')
    if not request.user.is_staff:
        messages.error(request, 'Only an administrator can open this page.')
        return redirect('home')
    return None


def admin_users(request):
    """Foydalanuvchilar ro'yxati: kirish usuli, sevimlilari va blok holati."""
    guard = _staff_guard(request, reverse('admin_users'))
    if guard:
        return guard

    users, stats = build_user_directory()
    active_filter = (request.GET.get('filter') or 'all').strip().lower()
    if active_filter == 'google':
        users = [user for user in users if user.login_method == 'google']
    elif active_filter == 'password':
        users = [user for user in users if user.login_method == 'password']
    elif active_filter == 'blocked':
        users = [user for user in users if user.is_blocked]
    else:
        active_filter = 'all'

    return render(request, 'app/users.html', {
        'users': users,
        'user_stats': stats,
        'active_filter': active_filter,
        'google_users': stats['google_users'],
        'password_users': stats['password_users'],
        'blocked_users': stats['blocked_users'],
        'google_logins': stats['google_logins'],
    })


@require_POST
def admin_user_toggle_block(request, user_id):
    """Foydalanuvchini bloklaydi yoki blokdan chiqaradi."""
    guard = _staff_guard(request, reverse('admin_users'))
    if guard:
        return guard

    user_model = get_user_model()
    target = get_object_or_404(user_model, pk=user_id)
    if target.is_staff or target.is_superuser:
        messages.error(request, 'Staff accounts cannot be blocked.')
    elif target.pk == request.user.pk:
        messages.error(request, 'You cannot block your own account.')
    else:
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        if not target.is_active:
            # Bloklangan foydalanuvchining band login slotini bo'shatamiz.
            ConcurrentLoginSlot.objects.filter(user=target).update(
                user=None, session_key=None, expires_at=None
            )
        if target.is_active:
            messages.success(request, 'The user has been unblocked.')
        else:
            messages.success(request, 'The user has been blocked.')

    if request.POST.get('next') == 'notifications':
        return redirect('admin_notifications')
    return redirect('admin_users')


def admin_notifications_page(request):
    """Administrator bildirishnomalarining to'liq ro'yxati."""
    guard = _staff_guard(request, reverse('admin_notifications'))
    if guard:
        return guard

    base = AdminNotification.objects.select_related(
        'user', 'product', 'admin_message'
    ).order_by('-created_at')
    counts = {'all': base.count(), 'unread': base.filter(is_read=False).count()}
    for kind_value, _label in AdminNotification.KIND_CHOICES:
        counts[kind_value] = base.filter(kind=kind_value).count()

    active_filter = (request.GET.get('kind') or 'all').strip().lower()
    if active_filter == 'unread':
        notifications = base.filter(is_read=False)
    elif active_filter in dict(AdminNotification.KIND_CHOICES):
        notifications = base.filter(kind=active_filter)
    else:
        active_filter = 'all'
        notifications = base

    return render(request, 'app/notifications.html', {
        'notifications': list(notifications[:200]),
        'notification_counts': counts,
        'active_filter': active_filter,
        'unread_notifications': counts['unread'],
    })


@require_POST
def admin_notifications_mark_read(request):
    """Barcha bildirishnomalarni o'qilgan deb belgilaydi."""
    guard = _staff_guard(request, reverse('admin_notifications'))
    if guard:
        return guard

    updated = AdminNotification.objects.filter(is_read=False).update(is_read=True)
    if updated:
        messages.success(request, 'All notifications have been marked as read.')
    else:
        messages.info(request, 'There are no unread notifications.')

    if request.POST.get('next') == 'dashboard':
        return redirect('admin_dashboard')
    return redirect('admin_notifications')


def contact_admin(request):
    """Foydalanuvchining administratorga shaxsiy xabar yuborish sahifasi."""
    product = None
    product_slug = request.POST.get('product') or request.GET.get('product')
    if product_slug:
        product = Product.objects.filter(slug=product_slug, is_active=True).first()

    initial = {}
    if request.user.is_authenticated:
        initial['full_name'] = request.user.get_full_name() or request.user.username
        initial['email'] = request.user.email

    if request.method == 'POST':
        form = AdminMessageForm(request.POST)
        if form.is_valid():
            admin_message = form.save(commit=False)
            if request.user.is_authenticated:
                admin_message.user = request.user
            admin_message.product = product
            admin_message.save()
            if not request.user.is_staff:
                notify_admin(
                    'message',
                    user=request.user if request.user.is_authenticated else None,
                    sender_name=admin_message.full_name,
                    product=product,
                    admin_message=admin_message,
                )
            messages.success(
                request, 'Your message has been sent to the administrator.'
            )
            if product:
                return redirect('product_detail', slug=product.slug)
            return redirect('home')
    else:
        form = AdminMessageForm(initial=initial)

    return render(request, 'app/contact_admin.html', {
        'form': form,
        'product': product,
    })


@require_POST
def toggle_favorite(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'ok': False, 'login_required': True,
             'message': 'Sevimlilarga qo‘shish uchun tizimga kiring.'},
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
        if not request.user.is_staff:
            notify_admin(
                'favorite',
                user=request.user,
                sender_name=request.user.username,
                product=product,
            )
    count = Favorite.objects.filter(user=request.user).count()
    return JsonResponse({'ok': True, 'is_favorite': is_favorite, 'count': count})


ASSISTANT_MAX_MESSAGE_LENGTH = 1000
ASSISTANT_MAX_HISTORY = 8

ASSISTANT_SYSTEM_PROMPTS = {
    'uz': (
        "Siz SHTOR HOUSE parda do'konining aqlli va do'stona maslahatchisisiz.\n"
        "Asosiy vazifa: foydalanuvchi qaysi mavzuda yozsa ham, avval o'sha savolga 1-2 gapda qisqa, aniq va foydali javob bering; so'ng tabiiy tarzda pardalar, deraza bezash yoki interyer mavzusiga bog'lab, qisqa maslahat bering.\n"
        "Mutaxassisligingiz: klassik pardalar, tyul, blackout/dimout, rolikli va zebra (kun-tun) pardalar, rim pardalari, gorizontal va vertikal jalyuzilar, panel/yapon pardalari, mato tanlash, o'lchash, o'rnatish, parvarish va narx.\n"
        "Qoidalar:\n"
        "1. Har doim foydalanuvchi yozgan tilda javob bering (o'zbek, rus yoki ingliz).\n"
        "2. Javob qisqa bo'lsin — 80 so'zdan oshmasin; kerak bo'lsa 2-3 punktda yozing.\n"
        "3. Pardaga oid savollarda aniq, amaliy va xatosiz maslahat bering.\n"
        "4. Boshqa mavzudagi savolni rad etmang yoki chetga surib qo'ymang: 1-2 gapda qisqa javob bering, keyin \"Aytgancha, derazangiz uchun...\" kabi tabiiy o'tish bilan pardaga ulang.\n"
        "5. Narx haqida gapirsangiz, aniq narx o'lcham va mato turiga bog'liqligini ayting; buyurtma uchun +998 97 424 42 42 raqamini bering.\n"
        "6. Do'kon haqida: SHTOR HOUSE, Toshkent, telefon +998 97 424 42 42.\n"
        "7. Hech qachon \"men AI man\", \"javob bera olmayman\" yoki \"bu mavzu menga tegishli emas\" demang."
    ),
    'en': (
        "You are the smart, friendly curtain advisor for SHTOR HOUSE.\n"
        "Main job: whatever topic the user asks about, first give a short, accurate and useful answer in 1-2 sentences, then naturally connect it to curtains, window styling or interior advice.\n"
        "Your expertise: classic curtains, sheers, blackout/dimout, roller and zebra (day-night) shades, Roman shades, horizontal and vertical blinds, panel/Japanese curtains, fabric selection, measuring, installation, care and pricing.\n"
        "Rules:\n"
        "1. Always reply in the language the user writes in (Uzbek, Russian or English).\n"
        "2. Keep replies short — max 80 words; use 2-3 bullet points when helpful.\n"
        "3. For curtain-related questions, be practical, specific and accurate.\n"
        "4. Never reject or dismiss an unrelated question: answer it briefly in 1-2 sentences, then bridge naturally with a phrase like \"By the way, for your window...\".\n"
        "5. When asked about price, say the exact quote depends on size and fabric, and give +998 97 424 42 42 for orders.\n"
        "6. Store info: SHTOR HOUSE, Tashkent, phone +998 97 424 42 42.\n"
        "7. Never say \"I am an AI\", \"I cannot answer\" or \"that topic is not mine\"."
    ),
    'ru': (
        "Вы умный и дружелюбный консультант по шторам компании SHTOR HOUSE.\n"
        "Главная задача: на какой бы вопрос пользователь ни написал, сначала дайте короткий, точный и полезный ответ в 1-2 предложениях, затем естественно свяжите его со шторами, оформлением окон или интерьером.\n"
        "Ваша специализация: классические шторы, тюль, blackout/dimout, рулонные и зебра-шторы, римские шторы, горизонтальные и вертикальные жалюзи, панельные шторы, выбор ткани, замеры, установка, уход и цены.\n"
        "Правила:\n"
        "1. Всегда отвечайте на языке пользователя (узбекском, русском или английском).\n"
        "2. Ответ короткий — не более 80 слов; при необходимости 2-3 пункта.\n"
        "3. На вопросы о шторах отвечайте практично, конкретно и точно.\n"
        "4. Не отклоняйте вопрос не по теме: коротко ответьте в 1-2 предложениях, затем естественно перейдите к шторам фразой вроде \"Кстати, для вашего окна...\".\n"
        "5. Вопрос о цене: точная стоимость зависит от размера и ткани; для заказа дайте номер +998 97 424 42 42.\n"
        "6. О магазине: SHTOR HOUSE, Ташкент, телефон +998 97 424 42 42.\n"
        "7. Никогда не говорите \"я ИИ\", \"не могу ответить\" или \"эта тема не моя\"."
    ),
}


def _assistant_history_from_payload(raw_history):
    """Foydalanuvchi tarixini xavfsiz shaklga siqib oladi."""
    normalized = []
    for entry in raw_history:
        if not isinstance(entry, dict):
            continue
        role = entry.get('role')
        content = entry.get('content')
        if role not in ('user', 'assistant') or not isinstance(content, str):
            continue
        content = content.strip()[:ASSISTANT_MAX_MESSAGE_LENGTH]
        if content:
            normalized.append({'role': role, 'content': content})
        if len(normalized) >= ASSISTANT_MAX_HISTORY:
            break
    return normalized


def _gemini_reply(message, history, system_prompt):
    contents = [
        {'role': 'model' if entry['role'] == 'assistant' else 'user', 'parts': [{'text': entry['content']}]}
        for entry in history
    ]
    contents.append({'role': 'user', 'parts': [{'text': message}]})
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/{settings.GOOGLE_AI_MODEL}:generateContent',
        headers={'x-goog-api-key': settings.GOOGLE_AI_API_KEY},
        json={
            'system_instruction': {'parts': [{'text': system_prompt}]},
            'contents': contents,
            'generationConfig': {'temperature': 0.6, 'maxOutputTokens': 700},
        },
        timeout=25,
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get('candidates') or []
    parts = (candidates[0].get('content') or {}).get('parts') or []
    reply = ' '.join(part.get('text', '').strip() for part in parts).strip()
    if not reply:
        raise ValueError('Gemini returned an empty reply.')
    return reply


def _openai_reply(message, history, system_prompt):
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': message})
    response = requests.post(
        f'{settings.OPENAI_BASE_URL.rstrip("/")}/chat/completions',
        headers={'Authorization': f'Bearer {settings.OPENAI_API_KEY}'},
        json={
            'model': settings.OPENAI_MODEL,
            'messages': messages,
            'temperature': 0.6,
            'max_tokens': 700,
        },
        timeout=25,
    )
    response.raise_for_status()
    data = response.json()
    reply = (data.get('choices') or [])[0].get('message', {}).get('content', '').strip()
    if not reply:
        raise ValueError('OpenAI returned an empty reply.')
    return reply


@require_POST
def assistant_api(request):
    """Chat maslahatchisi uchun server endpoint (LLM mavjud bo‘lsa)."""
    provider = settings.AI_PROVIDER
    if provider == 'auto':
        if settings.GOOGLE_AI_API_KEY:
            provider = 'gemini'
        elif settings.OPENAI_API_KEY:
            provider = 'openai'
        else:
            provider = None

    if not provider:
        # Key yo‘q — chat frontend offline smart-botiga qaytadi.
        return JsonResponse({'ok': False, 'error': 'not_configured'}, status=503)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        message = (payload.get('message') or '').strip()[:ASSISTANT_MAX_MESSAGE_LENGTH]
        language = payload.get('language') if payload.get('language') in ASSISTANT_SYSTEM_PROMPTS else 'en'
        history = _assistant_history_from_payload(payload.get('history') or [])
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError) as error:
        return JsonResponse({'ok': False, 'error': 'bad_request'}, status=400)

    if not message:
        return JsonResponse({'ok': False, 'error': 'bad_request'}, status=400)

    system_prompt = ASSISTANT_SYSTEM_PROMPTS[language]
    try:
        if provider == 'gemini':
            reply = _gemini_reply(message, history, system_prompt)
        else:
            reply = _openai_reply(message, history, system_prompt)
    except (requests.RequestException, ValueError, KeyError, IndexError) as error:
        # Provayder xatosi — frontend offline javobga tushadi.
        return JsonResponse({'ok': False, 'error': 'upstream'}, status=502)

    return JsonResponse({'ok': True, 'reply': reply})