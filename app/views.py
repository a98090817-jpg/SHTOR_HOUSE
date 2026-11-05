import json
import secrets
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
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from .forms import EmailOrUsernameLoginForm, ProductForm, QuoteRequestForm, CustomUserCreationForm
from .models import Favorite, Product, SiteVisitCounter

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

    # Saytga tashrif buyurganlar soni — har bir kirishda bazada +1.
    try:
        SiteVisitCounter.objects.get_or_create(pk=1)
    except IntegrityError:
        pass
    SiteVisitCounter.objects.filter(pk=1).update(count=F('count') + 1)
    visits_count = (
        SiteVisitCounter.objects.filter(pk=1)
        .values_list('count', flat=True)
        .first()
        or 0
    )

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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