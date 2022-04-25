import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.utils.datastructures import MultiValueDictKeyError

from main.models import UserModel, CertificateRequestModel, AdminModel


def sign_out(request):
    logout(request)
    return redirect('/')


def validate_admin_sign_in(request):
    if request.user.is_staff:
        return True
    else:
        return False


def validate_sign_in(request):
    if not request.user.is_authenticated:
        return False
    else:
        if not request.user.has_usable_password():
            logout(request)
            return False
        else:
            return True


# Create your views here.
def homepage(request):
    if validate_sign_in(request):
        return redirect("/dash")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('./dash')
        else:
            print("User Invalid")
            messages.info(request, "User Credentials Not Match")
    return render(request, 'homepage.html')


def dash(request):
    if not validate_sign_in(request):
        return redirect("/")
    if validate_admin_sign_in(request):
        return redirect("/admin")
    user = UserModel.objects.filter(uid=request.user.username).first()
    certificate_list = CertificateRequestModel.objects.filter(student_id=request.user.username)
    return render(request, 'dashboard.html', {'user': user, 'certificates': certificate_list})


def certificates(request):
    if not validate_sign_in(request):
        return redirect("/")
    if validate_admin_sign_in(request):
        return redirect("/admin")
    if request.method == "POST":
        print(request.POST["certificate"])
        # return
    user = UserModel.objects.filter(uid=request.user.username).get()
    certificate_list = CertificateRequestModel.objects.filter(student_id=request.user.username)
    return render(request, 'certificates.html', {'user': user, 'certificates': certificate_list})


def admin(request):
    try:
        user = AdminModel.objects.filter(uid=request.user.username).get()
        certificate_list = CertificateRequestModel.objects.filter(approved=False).filter(status="pending").order_by('request_date')
        if len(certificate_list) == 0:
            no_certificates = True
        else:
            no_certificates = False
        return render(request, 'admin.html',
                      {'user': user, 'certificates': certificate_list, 'no_certificates': no_certificates})
    except AdminModel.DoesNotExist:
        return redirect('/')


def admin_certificates_page(request):
    certificate_list = CertificateRequestModel.objects.order_by('request_date').order_by('approved').all()
    return render(request, 'admin_view_certificates.html', {'certificates': certificate_list})


def certificate_request_details(request):
    if request.method == "POST":
        certificate = CertificateRequestModel.objects.filter(id=request.POST["id"]).get()
        certificate.comment = request.POST["comment"]
        certificate.last_update_date = datetime.date.today()
        try:
            if request.POST["accept"]:
                certificate.approved = True
                certificate.status = "approved"
        except MultiValueDictKeyError:
            certificate.approved = False
            certificate.status = "rejected"
        certificate.save()
    try:
        certificate = CertificateRequestModel.objects.filter(id=request.GET["c_id"]).get()
        user = UserModel.objects.filter(uid=certificate.student_id).get()
        return render(request, 'cer_details.html', {'user': user, 'certificate': certificate})
    except UserModel.DoesNotExist:
        print("Error")
    except CertificateRequestModel.DoesNotExist:
        print("Np Certificate Found")
    return redirect('/')
