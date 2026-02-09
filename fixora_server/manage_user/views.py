from django.shortcuts import render
def login_view(request):
    return render(request, 'manage_user/login.html')
