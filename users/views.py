import self as self
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect

from store.models import Customer, User, Product, Order, OrderItem, ShippingAddress
from store.utils import cartData
from .forms import RegistrationForm, CustomerForm
from django.contrib.auth import authenticate, login
from django.contrib import messages


# Create your views here.


def register(request):
    if request.method == 'POST':
        # eğer post yaratılmış kişi içini doldurmuş ve save demişse yani post metodu request edilmişse, is_valid true dönüyorsa onu db ye kaydeder bilgileri
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # if form data is valid then save it into the database
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request, username=username, password=password)
            name = request.POST['first_name']
            surname = request.POST['last_name']
            email = request.POST['email']

            values = {
                'name': name,
                'surname': surname,
                'email': email,
                'user': user
            }
            error_message = None
            customer = Customer(name=name, surname=surname, email=email, user=user)
            customer.save()

            login(request, user)
            return redirect('store')

    else:
        # eğer post request edilmemişse yani form yaratılmamışsa boş bir form yaratılır burada da. Hem save edilmesi hem de yaratılması için aynı metod kullanılıyor yani
        form = RegistrationForm()

    # context dictionary is created in here and it will contain the name form that contains the value for this form that we've created above here
    # and once we create that this we can pass this in as the third argument in the below return statement
    # so we can actually access the form within our template and this template is register.html within our users dictionary
    context = {'form': form}
    return render(request, 'users/register.html', context)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            #   messages.info(request, 'Your password has been changed successfully!')
            return redirect('store')

        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {
        'form': form
    })


def Profile(request):
    data = cartData(request)
    cartItems = data['cartItems']
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form, 'cartItems': cartItems}
    return render(request, 'users/user_profile.html', context)


def favorite_list(request):
    data = cartData(request)
    cartItems = data['cartItems']
    new = Product.objects.filter(favorites=request.user)
    return render(request, 'users/favorite_list.html',
                  {'new': new, 'cartItems': cartItems})


def my_order_list(request):
    customer = request.user.customer
    data = cartData(request)
    cartItems = data['cartItems']
    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
    context = {'orders': orders, 'cartItems': cartItems}
    return render(request, 'users/my_orders_list.html', context)


def order_detail(request, id):
    data = cartData(request)
    cartItems = data['cartItems']
    customer = request.user.customer
    order = Order.objects.get(id=id, customer=customer)
    shippingAddress = ShippingAddress.objects.get(customer=customer, order=order)
    orderItems = OrderItem.objects.filter(order=order)
    context = {'order': order, 'orderItems': orderItems, 'cartItems': cartItems, 'shippingAddress': shippingAddress}

    return render(request, 'users/order_detail.html', context)
