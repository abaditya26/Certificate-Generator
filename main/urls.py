from django.urls import path
from django.views.generic import TemplateView

from main import views

urlpatterns = [
    path('', views.homepage),
    path('logout', views.sign_out),
    path('dash', views.dash),
    path('certificates', views.certificates),
    # Admin
    path('admin', views.admin),
    path('admin_view_certificates', views.admin_certificates_page),
]
