from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login


# Create your views here.
def homepage(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(username=email, password=password)
        if user is not None:
            print("User Logged in successfully")
            login(request, user)
            return redirect('./dash')
        else:
            print("User Invalid")
            messages.info(request, "User Credentials Not Match")
    return render(request, 'homepage.html')
