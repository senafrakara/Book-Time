from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.db.models import Q
from .forms import CommentForm, SearchForm, ContactForm
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.core.mail import send_mail, BadHeaderError


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Product: ', productId)
    print('Action: ', action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # Thats mean is product needs to shipp
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def processOrder(request):
    print('data: ', request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer

        order = Order.objects.get(customer=customer, complete=False)


    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    # <--- Kübra
    name_on_card = data['payment_form']['name_on_card']
    credit_card_number = data['payment_form']['credit_card_number']
    expiration = data['payment_form']['expiration']
    ccv = data['payment_form']['ccv']

    try:
        card = Bank.objects.get(credit_card_number=credit_card_number)

    except:
        card = Bank.objects.create(name_on_card=name_on_card, credit_card_number=credit_card_number,
                                   expiration=expiration, cvv=ccv)

    # ----->

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']

        )

    card.balance -= total
    card.save()

    return JsonResponse('payment submitted...', safe=False)


def updateCart(request):
    if request.user.is_authenticated:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        customer = request.user.customer  # this is fixed
        order, created = Order.objects.get_or_create(customer=customer, complete=False)  # this is fixed
        res = not bool(cart)
        if not res:
            for i in cart:
                product = Product.objects.get(id=i)
                orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
                # orderItem.quantity = (orderItem.quantity + 1)
                orderItem.quantity += cart[i]['quantity']
                orderItem.save()
                #
                # if not product.digital:
                #     order['shipping'] = True
                # total = (product.price * cart[i]['quantity'])
                #
                # order['get_cart_total'] += total
                # order['get_cart_items'] += cart[i]['quantity']
                #
                # item = {
                #     'product': {
                #         'id': product.id,
                #         'name': product.name,
                #         'price': product.price,
                #         'imageURL': product.imageURL
                #     },
                #     'quantity': cart[i]['quantity'],
                #     'get_total': total,
                # }
                # items.append(item)
                #
                # if not product.digital:
                #     order['shipping'] = True
        else:
            pass

    else:
        return redirect('store')

    return JsonResponse('Item was added', safe=False)


def ProductDetail(request, id):
    product = get_object_or_404(Product, id=id)
    data = cartData(request)
    cartItems = data['cartItems']
    comments = product.comments.filter(active=True)
    new_comment = None
    comment_user = request.user

    if request.method == 'POST':
        form = CommentForm(data=request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment = Comment(commenter=comment_user,
                                  comment_content=form.cleaned_data['comment_content'],
                                  product=product)
            new_comment.save()


    else:
        form = CommentForm()

    favorite = False
    if product.favorites.filter(id=request.user.id).exists():
        favorite = True

    context = {'product': product,
               'cartItems': cartItems,
               'favorite': favorite,
               'comments': comments,
               'comment_form': form,
               'new_comment': new_comment}
    return render(request, 'store/product_detail.html', context=context)


def FavoriteView(request, id):
    product = get_object_or_404(Product, id=id)
    favorite = False
    if product.favorites.filter(id=request.user.id).exists():
        product.favorites.remove(request.user)
    else:
        product.favorites.add(request.user)
        favorite = True

    return HttpResponseRedirect(reverse('product_detail', args=[str(id)]))


def RemoveFavoriteList(request, id):
    product = get_object_or_404(Product, id=id)

    if product.favorites.filter(id=request.user.id).exists():
        product.favorites.remove(request.user)

    return HttpResponseRedirect(reverse('favorite_list'))


@login_required()
def comment_delete(request, id):
    comment = get_object_or_404(Comment, id=id)
    deleted_comment = None
    urll = comment.product.id
    if request.method == 'POST':
        deleted_comment = comment.delete()

    return redirect(f'/product_detail/{urll}')


def search(request):
    data = cartData(request)
    cartItems = data['cartItems']
    status = None
    if request.method == 'GET':
        name = request.GET.get('search')
        try:
            status = Product.objects.all().filter(
                Q(name__icontains=name) |
                Q(author__icontains=name)
            )
            return render(request, 'store/store.html', {'products': status, 'cartItems': cartItems,})
        except:
            return render(request, "store/store.html", {'products': status, 'cartItems': cartItems,})
    else:
        return render(request, 'store/store.html', {'cartItems': cartItems,})


def aboutus(request):
    data = cartData(request)
    cartItems = data['cartItems']
    return render(request, 'store/aboutus.html', {'cartItems': cartItems,})


def contactus(request):
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(username, from_email, message, ['senafrakara@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found. ')
            return render(request, 'store/contactus.html', {'username': username, 'cartItems': cartItems})
    return render(request, 'store/contactus.html', {'form': form, 'cartItems': cartItems,})
