from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login

from main.models import UserModel


def sign_out(request):
    logout(request)
    return redirect('/')


# Create your views here.
def homepage(request):
    if request.user.is_authenticated:
        if not request.user.has_usable_password():
            return redirect("/logout")
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
    if not request.user.is_authenticated:
        return redirect("/login")
    if not request.user.has_usable_password():
        return redirect("/logout")
    user = UserModel.objects.filter(uid=request.user.username).get()
    return render(request, 'dashboard.html', {'user': user})


def certificates(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if not request.user.has_usable_password():
        return redirect("/logout")
    user = UserModel.objects.filter(uid=request.user.username).get()
    return render(request, 'certificates.html', {'user': user})
