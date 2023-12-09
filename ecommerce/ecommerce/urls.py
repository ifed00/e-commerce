"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, include

import integration_app.views
from .settings import MEDIA_ROOT, MEDIA_URL

account_patterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('password_change', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('signup', integration_app.views.SignUpView.as_view(), name='signup')
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('integration_app.urls')),
    path('accounts/', include(account_patterns)),
    path('profile', integration_app.views.ProfileView.as_view(), name='profile'),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
