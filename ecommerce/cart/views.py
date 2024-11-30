from django.shortcuts import render, redirect
from cart.models import Cart
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.contrib.auth import login
from cart.models import Payment, Order_details
from shop.models import Product
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import razorpay

@login_required
def addtocart(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    c, created = Cart.objects.get_or_create(product=p, user=u)
    if not created:
        c.quantity += 1
    c.save()
    p.stock -= 1
    p.save()
    return redirect('cart:cart_view')

# @login_required
# def cart_view(request):
#     u = request.user
#     c = Cart.objects.filter(user=u)
#     total = sum(item.quantity * item.product.price for item in c)
#     context = {'cart': c, 'total_price': total}
#     return render(request, 'cart.html', context)
@login_required
def remove_from_cart(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    try:
        c = Cart.objects.get(product=p, user=u)
        c.quantity -= 1
        if c.quantity <= 0:
            c.delete()
        else:
            c.save()
        p.stock += 1
        p.save()
    except Cart.DoesNotExist:
        pass
    return redirect('cart:cart_view')
@login_required
def delete_item(request, i):
    p = Product.objects.get(id=i)
    u = request.user
    try:
        c = Cart.objects.get(product=p, user=u)
        p.stock += c.quantity
        p.save()
        c.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cart:cart_view')
from django.db.models import F, Sum

# @login_required
# def cart_view(request):
#     u = request.user
#     cart_items = Cart.objects.filter(user=u).annotate(total_price=F('quantity') * F('product__price'))
#     # total = cart_items.aggregate(total=Sum('total_price'))['total'] or 0
#     total = sum(item.subtotal for item in cart_items)
#     context = {'cart': cart_items, 'total_price': total}
#     return render(request, 'cart.html', context)

@login_required
def cart_view(request):
    u = request.user
    # Annotate each cart item with a calculated subtotal
    cart_items = Cart.objects.filter(user=u).annotate(subtotal=F('quantity') * F('product__price'))

    # Aggregate the total price
    total = cart_items.aggregate(total_price=Sum('subtotal'))['total_price'] or 0

    context = {
        'cart': cart_items,  # cart_items now includes the annotated `subtotal`
        'total_price': total,
    }
    return render(request, 'cart.html', context)
# @login_required
# def orderform(request):
#     if(request.method=="POST"):
#         address = request.POST['a']
#         phone = request.POST['p']
#         pin = request.POST['pi']
#         u=request.user
#         c=Cart.objects.filter(user=u)
#         total=0
#         for i in c:
#             total+=i.quantity*i.product.price
#         total=int(total*100)
#         print(total)
#         client = razorpay.Client(auth=('rzp_test_aHTNFYvnGizpHp','3QMBjGjK1BRAEs6XcFrHnv3P')) #creates a client connection
#         #using razorpay id and secret code
#         response_payment = client.order.create(dict(amount=total,currency="INR"))#creates an order with razorpay using razorpay client
#         print(response_payment)
#         order_id = response_payment['id']
#
#         status = response_payment['status']
#
#         if (status == "created"):
#             p = Payment.objects.create(name=u.username, amount=total, order_id=order_id)
#             p.save()
#             for i in c:
#                 p = Payment.objects.create(name=u.username, amount=total, order_id=order_id)
#                 p.save()
#                 for i in c:
#                     o = Order_details.objects.create(product=i.product, user=u, no_of_items=i.quantity, address=address,
#                                                      phone=phone, pin=pin, order_id=order_id)
#                     o.save()
#
#             return render(request,'payment.html')
#         return render(request,'orderform.html')


@login_required
def orderform(request):
    if (request.method == "POST"):
        address = request.POST['a']
        phone = request.POST['p']
        pin = request.POST['pi']
        u = request.user
        c = Cart.objects.filter(user=u)
        total = 0
        for i in c:
            total += i.quantity * i.product.price
        total = int(total * 100)

        client = razorpay.Client(auth=('rzp_test_dVrWySYZeHoiH1', 'MIKQkSGzNErgrSyoUtlPqiwQ'))  # Creates a client connection
        # using razorpay id and secret code

        response_payment = client.order.create(dict(amount=total, currency="INR"))  # creates an order with
        # razorpay using razorpay client
        print(response_payment)
        order_id = response_payment['id']

        status = response_payment['status']

        if (status == "created"):
            p = Payment.objects.create(name=u.username, amount=total, order_id=order_id)
            p.save()
            for i in c:
                o = Order_details.objects.create(product=i.product, user=u, no_of_items=i.quantity, address=address,
                                                 phone=phone, pin=pin, order_id=order_id)
                o.save()
        response_payment['name'] = u.username
        context = {'payment': response_payment}
        return render(request, 'payment.html', context)

    return render(request, 'orderform.html')

@csrf_exempt
def payment_status(request,u):
    user = User.objects.get(username=u)
    if not request.user.is_authenticated:
        login(request,user)

    if(request.method=="POST"):
        response=request.POST
        print(response)
        param_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature'],

            }

        client = razorpay.Client(auth=('rzp_test_dVrWySYZeHoiH1', 'MIKQkSGzNErgrSyoUtlPqiwQ'))
        print(client)
        try:

            status = client.utility.verify_payment_signtaure(param_dict)
            print(status)
# to retrive a particular record frompayment table matching with razorpay response oder id
            p=Payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id=response['razorpay_payment_id']
            p.paid=True
            p.save()
#to retrive a particular record fro payment table matching with razorpay response order id
            o=Order_details.objects.filter(order_id=response['razorpay_order_id'])
            for i in o:
                i.payment_status="completed"
                i.save()


            c=Cart.objects.filter(user=user)
            c.delete()







        except:
            pass

    return render(request,'payment_status.html',{'status':status})






