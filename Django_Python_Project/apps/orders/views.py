from django.shortcuts import render

def order_create(request):
    pass

def checkout(request):
    return render(request, "Django_Python_Project\\templates\\orders\\checkout.html")

def order_detail(request):
    return render(request, "Django_Python_Project\\templates\\orders\\order_detail.html")

def order_list(request):
    return render(request, "Django_Python_Project\\templates\\orders\\orderlist.html")