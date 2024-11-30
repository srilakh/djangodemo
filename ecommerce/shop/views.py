from django.shortcuts import render,get_object_or_404,redirect
from shop.models import Category
from shop.models import Product
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User




# Create your views here.
def categories(request):
    c = Category.objects.all()
    context = {'cat': c}
    return render(request,'categories.html',context)

# def products(request):
#     products = Product.objects.all()
#     c = {'products':products}
#     return render(request,'products.html',c)
def products(request, category_id=None):
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    categories = Category.objects.all()
    context = {'products': products, 'categories': categories}
    return render(request, 'products.html', context)
# def product_detail(request, id):
#     product = Product.objects.get(id)
#     c = {'product': product}
#     return render(request, 'product_detail.html', c)
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    context = {'product': product}
    return render(request, 'product_detail.html', context)
def products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    categories = Category.objects.all()
    c = {'products': products,
         'categories': categories,
         'selected_category_id': category_id,

         }
    return render(request, 'products.html', c)


def register(request):
    if request.method == "POST":
        n = request.POST['n']
        u = request.POST['u']
        p = request.POST['p']
        cp = request.POST['cp']
        e = request.POST['e']


        if p == cp:
            # Create the user without confirmpassword
            user = User.objects.create_user(first_name=n, username=u, password=p, email=e)
            user.save()
            return redirect('shop:categories')
        else:
            return HttpResponse("Passwords do not match")
    return render(request, 'register.html')

def user_login(request):
    if request.method == "POST":
        u = request.POST['u']
        p = request.POST['p']
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('shop:categories')
        else:
            return HttpResponse("Invalid credentials")
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('shop:login')
