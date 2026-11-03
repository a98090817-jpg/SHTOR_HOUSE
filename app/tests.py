from django.contrib.auth import get_user_model
import base64
from pathlib import Path
import sqlite3
import tempfile
from unittest.mock import patch
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from PIL import Image
from contextlib import closing
from zipfile import ZipFile

from .models import ConcurrentLoginSlot, Product, QuoteRequest


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Luxe Silk Curtain',
            category='living_room',
            color='Ivory',
            material='Silk',
            price=420.00,
            description='Elegant light-filtering curtain for premium interiors.',
            is_featured=True,
        )

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(str(self.product), 'Luxe Silk Curtain')

    def test_home_page_lists_products(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Luxe Silk Curtain')
        self.assertContains(response, 'data-i18n="heroTitle"')
        self.assertContains(response, 'data-i18n="benefitsTitle"')
        self.assertContains(response, 'class="gallery-card tall" data-reveal-item')
        self.assertContains(response, '<strong data-registered-user-count>0</strong>')
        self.assertContains(response, 'https://www.instagram.com/shtor_house?exln=MWRrajd1ejF4Y3JnaA==')
        self.assertContains(response, 'https://t.me/Shtor_House_Shop')
        self.assertContains(response, 'https://maps.google.com/maps?q=41.331773,69.251642&amp;z=15&amp;output=embed')
        self.assertContains(response, 'https://www.google.com/maps?q=41.331773,69.251642')
        self.assertContains(response, 'data-maintenance-modal')
        self.assertContains(response, 'data-curtain-assistant')
        self.assertContains(response, 'app/css/ai_assistant.css')
        self.assertContains(response, 'app/js/ai_assistant.js')

    def test_registered_customer_count_excludes_staff_and_inactive_accounts(self):
        user_model = get_user_model()
        user_model.objects.create_user(username='registered-customer', password='StrongPass123!')
        user_model.objects.create_user(
            username='inactive-customer',
            password='StrongPass123!',
            is_active=False,
        )
        user_model.objects.create_user(
            username='staff-account',
            password='StrongPass123!',
            is_staff=True,
        )
        user_model.objects.create_user(
            username='superuser-account',
            password='StrongPass123!',
            is_superuser=True,
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, '<strong data-registered-user-count>1</strong>')

    def test_promo_carousel_uses_uploaded_product_images(self):
        image = SimpleUploadedFile(
            'promo-curtain.png',
            base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
            ),
            content_type='image/png',
        )
        with tempfile.TemporaryDirectory() as media_directory:
            with override_settings(MEDIA_ROOT=media_directory):
                product = Product.objects.create(
                    name='Carousel Curtain',
                    category='bedroom',
                    color='Ivory',
                    material='Linen',
                    price=250,
                    description='Curtain for the home-page carousel.',
                    image=image,
                )

                response = self.client.get(reverse('home'))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'data-promo-track')
                self.assertContains(response, 'data-promo-next')
                self.assertContains(response, 'Carousel Curtain')
                self.assertContains(response, product.image.url)
                self.assertEqual(response.content.count(b'data-curtain-ticker-row'), 1)
                self.assertContains(response, 'data-ticker-toggle')

    def test_home_page_uses_local_curtain_images_without_catalog_products(self):
        with tempfile.TemporaryDirectory() as media_directory:
            products_directory = Path(media_directory) / 'products'
            products_directory.mkdir()
            (products_directory / 'curtain-sample.jpg').write_bytes(b'curtain' * 3000)
            (products_directory / 'jalyuzi.jpg').write_bytes(b'jalyuzi' * 3000)
            with override_settings(MEDIA_ROOT=media_directory):
                response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-curtain-ticker')
        self.assertContains(response, '/media/products/jalyuzi.jpg')
        self.assertContains(response, 'Curtain style 02')
        self.assertEqual(response.content.count(b'data-curtain-ticker-row'), 1)
        self.assertEqual(response.content.count(b'data-registered-user-count'), 1)

    def test_product_detail_instagram_link_uses_shtor_house_account(self):
        response = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<title>{self.product.name} | SHTOR HOUSE</title>', html=True)
        self.assertContains(response, 'https://www.instagram.com/shtor_house?exln=MWRrajd1ejF4Y3JnaA==')
        self.assertContains(response, 'https://t.me/Shtor_House_Shop')

    def test_quote_request_creation(self):
        form_data = {
            'full_name': 'Ali Valiyev',
            'phone': '+998901234567',
            'email': 'ali@example.com',
            'product': self.product.id,
            'message': 'I want this model for my apartment.',
        }
        response = self.client.post(reverse('quote_request'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(QuoteRequest.objects.count(), 1)

    def test_register_page_renders(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create account')
        self.assertContains(response, 'Register | SHTOR HOUSE')

    def test_login_page_renders_reference_flow(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in | SHTOR HOUSE')
        self.assertContains(response, 'Continue to your SHTOR HOUSE account.')
        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, 'Forgot password?')
        self.assertContains(response, 'data-password-toggle')
        self.assertContains(response, 'aria-label="Show password"')
        self.assertContains(response, 'id="id_password"')
        self.assertContains(response, 'data-curtain-assistant')

    @override_settings(GOOGLE_CLIENT_ID='', GOOGLE_CLIENT_SECRET='')
    def test_google_login_reports_missing_configuration(self):
        response = self.client.get(reverse('google_login'))
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)

    @override_settings(
        GOOGLE_CLIENT_ID='test-client-id',
        GOOGLE_CLIENT_SECRET='test-client-secret',
        GOOGLE_REDIRECT_URI='http://127.0.0.1:8000/auth/google/callback/',
    )
    def test_google_callback_uses_bearer_token_and_creates_user(self):
        session = self.client.session
        session['google_oauth_state'] = 'state-123'
        session.save()

        def fake_urlopen(request, timeout=None):
            if request.full_url == 'https://oauth2.googleapis.com/token':
                class TokenResponse:
                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc, tb):
                        return False

                    def read(self):
                        return b'{"access_token": "google-token-123", "token_type": "Bearer"}'

                return TokenResponse()

            if request.full_url == 'https://openidconnect.googleapis.com/v1/userinfo':
                self.assertEqual(request.headers.get('Authorization'), 'Bearer google-token-123')

                class UserInfoResponse:
                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc, tb):
                        return False

                    def read(self):
                        return b'{"sub": "google-sub-123", "email": "google-user@example.com", "email_verified": true, "picture": "https://example.com/avatar.jpg"}'

                return UserInfoResponse()

            raise AssertionError(f'Unexpected URL: {request.full_url}')

        with patch('app.views.urlopen', side_effect=fake_urlopen):
            response = self.client.get(reverse('google_callback'), {'state': 'state-123', 'code': 'auth-code'})

        self.assertRedirects(response, reverse('home'))
        user = get_user_model().objects.get(email='google-user@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)
        self.assertEqual(self.client.session['google_profile_picture'], 'https://example.com/avatar.jpg')

    @override_settings(
        GOOGLE_CLIENT_ID='test-client-id',
        GOOGLE_CLIENT_SECRET='test-client-secret',
        GOOGLE_REDIRECT_URI='http://127.0.0.1:8000/auth/google/callback/',
    )
    def test_google_callback_rejects_missing_state_without_contacting_google(self):
        with patch('app.views.urlopen') as urlopen_mock:
            response = self.client.get(
                reverse('google_callback'),
                {'state': 'untrusted-state', 'code': 'auth-code'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google sign-in session expired. Please try again.')
        urlopen_mock.assert_not_called()
        self.assertNotIn('_auth_user_id', self.client.session)

    @override_settings(
        GOOGLE_CLIENT_ID='test-client-id',
        GOOGLE_CLIENT_SECRET='test-client-secret',
        GOOGLE_REDIRECT_URI='http://127.0.0.1:8000/auth/google/callback/',
    )
    def test_google_callback_handles_provider_cancellation(self):
        session = self.client.session
        session['google_oauth_state'] = 'state-123'
        session.save()

        with patch('app.views.urlopen') as urlopen_mock:
            response = self.client.get(
                reverse('google_callback'),
                {'state': 'state-123', 'error': 'access_denied'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google sign-in was cancelled.')
        urlopen_mock.assert_not_called()

    @override_settings(
        GOOGLE_CLIENT_ID='test-client-id',
        GOOGLE_CLIENT_SECRET='test-client-secret',
        GOOGLE_REDIRECT_URI='http://127.0.0.1:8000/auth/google/callback/',
    )
    def test_google_callback_handles_invalid_token_response(self):
        session = self.client.session
        session['google_oauth_state'] = 'state-123'
        session.save()

        class InvalidTokenResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"error": "invalid_grant"}'

        with patch('app.views.urlopen', return_value=InvalidTokenResponse()):
            response = self.client.get(
                reverse('google_callback'),
                {'state': 'state-123', 'code': 'expired-code'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google sign-in could not be completed.')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_can_login_with_email(self):
        user = get_user_model().objects.create_user(
            username='parda-owner',
            email='owner@example.com',
            password='StrongPass123!',
        )
        response = self.client.post(
            reverse('login'),
            {'username': 'owner@example.com', 'password': 'StrongPass123!'},
        )
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_user_can_login_with_different_username_case(self):
        user = get_user_model().objects.create_user(
            username='PardaCase',
            password='StrongPass123!',
        )
        response = self.client.post(
            reverse('login'),
            {'username': 'pardacase', 'password': 'StrongPass123!'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_user_can_logout_and_return_home(self):
        user = get_user_model().objects.create_user(username='logout-user', password='StrongPass123!')
        self.client.force_login(user)
        self.client.get(reverse('home'))
        self.assertEqual(
            ConcurrentLoginSlot.objects.filter(session_key__isnull=False).count(),
            1,
        )
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(
            ConcurrentLoginSlot.objects.filter(session_key__isnull=False).count(),
            0,
        )

    def test_only_ten_concurrent_login_sessions_are_allowed(self):
        clients = []
        for index in range(11):
            user = get_user_model().objects.create_user(
                username=f'capacity-user-{index}',
                password='StrongPass123!',
            )
            client = Client()
            client.force_login(user)
            response = client.get(reverse('home'))
            clients.append(client)

            if index < 10:
                self.assertEqual(response.status_code, 200)
                self.assertIn('_auth_user_id', client.session)
            else:
                self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)
                self.assertNotIn('_auth_user_id', client.session)

        self.assertEqual(
            ConcurrentLoginSlot.objects.filter(session_key__isnull=False).count(),
            10,
        )

    def test_logout_frees_a_slot_for_another_user(self):
        clients = []
        for index in range(10):
            user = get_user_model().objects.create_user(
                username=f'full-capacity-user-{index}',
                password='StrongPass123!',
            )
            client = Client()
            client.force_login(user)
            self.assertEqual(client.get(reverse('home')).status_code, 200)
            clients.append(client)

        clients[0].post(reverse('logout'))
        new_user = get_user_model().objects.create_user(
            username='replacement-user',
            password='StrongPass123!',
        )
        replacement_client = Client()
        replacement_client.force_login(new_user)

        response = replacement_client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', replacement_client.session)

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reset password')

    def test_product_create_requires_login(self):
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_home_page_has_product_plus_action(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'class="add-product-plus"')

    def test_staff_can_open_product_create(self):
        user = get_user_model().objects.create_user(username='staff-owner', password='StrongPass123!', is_staff=True)
        self.client.force_login(user)
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Product | SHTOR HOUSE')
        self.assertContains(response, '/static/app/css/style.css')
        self.assertContains(response, 'Add curtain')
        self.assertContains(response, 'id="id_image"')
        self.assertContains(response, 'accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"')
        for field_id in (
            'id_name', 'id_material', 'id_length_meters', 'id_price',
            'id_color', 'id_origin', 'id_category', 'id_description',
            'id_is_featured', 'id_is_active',
        ):
            self.assertContains(response, f'id="{field_id}"')

    def test_regular_user_cannot_open_product_create(self):
        user = get_user_model().objects.create_user(username='regular-user', password='StrongPass123!')
        self.client.force_login(user)
        response = self.client.get(reverse('product_create'))
        self.assertRedirects(response, reverse('home'))

    def test_regular_user_cannot_delete_product(self):
        user = get_user_model().objects.create_user(username='regular-delete-user', password='StrongPass123!')
        self.client.force_login(user)
        response = self.client.post(reverse('product_delete', args=[self.product.slug]))
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_staff_can_delete_product(self):
        user = get_user_model().objects.create_user(username='delete-owner', password='StrongPass123!', is_staff=True)
        self.client.force_login(user)
        response = self.client.post(reverse('product_delete', args=[self.product.slug]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_staff_can_add_product_with_image_and_return_home(self):
        user = get_user_model().objects.create_user(username='catalog-owner', password='StrongPass123!', is_staff=True)
        self.client.force_login(user)
        image = SimpleUploadedFile(
            'curtain.png',
            base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='),
            content_type='image/png',
        )
        response = self.client.post(reverse('product_create'), {
            'name': 'New Curtain',
            'category': 'living_room',
            'color': 'Ivory',
            'material': 'Linen',
            'length_meters': '4.00',
            'origin': 'Turkey',
            'price': '500',
            'description': 'New curtain description',
            'image': image,
            'is_featured': 'on',
            'is_active': 'on',
        })
        self.assertRedirects(response, reverse('home'))
        created = Product.objects.get(name='New Curtain')
        self.assertEqual(created.origin, 'Turkey')
        self.assertEqual(created.length_meters, 4)
        self.assertEqual(created.material, 'Linen')
        self.assertEqual(created.color, 'Ivory')
        self.assertEqual(created.category, 'living_room')
        self.assertEqual(created.description, 'New curtain description')
        self.assertTrue(created.is_featured)
        self.assertTrue(created.is_active)
        self.assertTrue(created.image.name.startswith('products/curtain'))
        self.assertTrue(created.image.name.endswith('.webp'))
        with created.image.open('rb') as normalized_image:
            with Image.open(normalized_image) as image:
                self.assertEqual(image.size, (1200, 1500))

    def test_uploaded_product_image_url_is_rendered_on_home_page(self):
        user = get_user_model().objects.create_user(
            username='media-owner',
            password='StrongPass123!',
            is_staff=True,
        )
        self.client.force_login(user)
        image = SimpleUploadedFile(
            'media-curtain.png',
            base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
            ),
            content_type='image/png',
        )

        response = self.client.post(reverse('product_create'), {
            'name': 'Media URL Curtain',
            'category': 'living_room',
            'color': 'Ivory',
            'material': 'Linen',
            'length_meters': '3.00',
            'origin': 'Turkey',
            'price': '300',
            'description': 'Curtain image media URL test.',
            'image': image,
            'is_active': 'on',
        })
        self.assertRedirects(response, reverse('home'))

        product = Product.objects.get(name='Media URL Curtain')
        try:
            self.assertTrue(product.image.storage.exists(product.image.name))
            home_response = self.client.get(reverse('home'))
            self.assertContains(home_response, product.image.url)
        finally:
            product.image.delete(save=False)

    def test_backup_site_includes_database_snapshot_and_media(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            media_root = root / 'media'
            media_root.mkdir()
            (media_root / 'backup-check.txt').write_text('media backup', encoding='utf-8')
            output_dir = root / 'backups'
            database_path = root / 'site.sqlite3'
            with closing(sqlite3.connect(database_path)) as database:
                database.execute('CREATE TABLE app_product (id INTEGER PRIMARY KEY)')
                database.commit()

            with override_settings(
                MEDIA_ROOT=media_root,
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': database_path,
                    },
                },
            ):
                call_command('backup_site', output_dir=output_dir)

            archives = list(output_dir.glob('shtor-house-backup-*.zip'))
            self.assertEqual(len(archives), 1)
            with ZipFile(archives[0]) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('db.sqlite3', archive.namelist())
                self.assertIn('media/backup-check.txt', archive.namelist())
                snapshot_path = root / 'snapshot.sqlite3'
                snapshot_path.write_bytes(archive.read('db.sqlite3'))

            with closing(sqlite3.connect(snapshot_path)) as snapshot:
                table_names = {
                    row[0]
                    for row in snapshot.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
            self.assertIn('app_product', table_names)

    def test_product_image_is_required(self):
        user = get_user_model().objects.create_user(username='image-owner', password='StrongPass123!', is_staff=True)
        self.client.force_login(user)
        response = self.client.post(reverse('product_create'), {
            'name': 'No Image Curtain', 'category': 'living_room', 'color': 'Ivory',
            'material': 'Linen', 'length_meters': '2', 'origin': 'Turkey',
            'price': '200', 'description': 'Missing image',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_user_can_register(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())

    def test_home_page_filters_by_category(self):
        bedroom_product = Product.objects.create(
            name='Sleepy Linen',
            category='bedroom',
            color='Blush',
            material='Linen',
            price=390.00,
            description='Soft bedroom curtain.',
            is_featured=True,
        )
        Product.objects.create(
            name='Urban Light',
            category='living_room',
            color='Stone',
            material='Cotton',
            price=310.00,
            description='Simple living room curtain.',
        )

        response = self.client.get(reverse('home') + '?category=bedroom')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, bedroom_product.name)
        self.assertNotContains(response, 'Urban Light')

    def test_home_page_has_single_catalog_without_whatsapp_button(self):
        Product.objects.create(
            name='Featured Classic',
            category='living_room',
            color='Cream',
            material='Cotton',
            price=410.00,
            description='Featured classic curtain.',
            is_featured=True,
        )

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CURTAIN CATALOG')
        self.assertContains(response, 'Featured Classic')
        self.assertNotContains(response, 'wa.me')
