from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='app/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('quote/', views.quote_request, name='quote_request'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('favorite/<slug:slug>/', views.toggle_favorite, name='toggle_favorite'),
]
