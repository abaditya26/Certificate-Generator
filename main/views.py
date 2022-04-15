from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login

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
    user = UserModel.objects.filter(uid=request.user.username).get()
    certificate_list = CertificateRequestModel.objects.filter(student_id=request.user.username)
    return render(request, 'certificates.html', {'user': user, 'certificates': certificate_list})


def admin(request):
    user = AdminModel.objects.filter(uid=request.user.username).get()
    return render(request, 'admin.html', {'user': user})
