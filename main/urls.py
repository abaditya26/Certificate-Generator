from django.urls import path
from django.views.generic import TemplateView

from main import views

urlpatterns = [
    path('', views.homepage),
    path('logout', views.sign_out),
    path('dash', views.dash),
    path('certificates', views.certificates),

    path('view_certificate', views.view_certificate, name="View certificate in PDF"),
    # Admin
    path('admin', views.admin),
    path('admin_view_certificates', views.admin_certificates_page),
    path('admin_certificate_req', views.certificate_request_details),
    path('users', views.user_list),
    path('details', views.details)
]
