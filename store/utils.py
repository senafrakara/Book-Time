import json
from .models import *


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'items': items, 'order': order, 'cartItems': cartItems}


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart: ', cart)
    items = []
    # admin logout olunca cart bilgileri sıfırlar
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)

            if not product.digital:
                order['shipping'] = True
        except:
            pass

    # cartitems için yapılan işlem ve for döngüsü sepetteki görüntü için yaspıldı, sepetteki ürün sayısı için

    return {'cartItems': cartItems, 'order': order, 'items': items}


# {} bu dictionary demek


def guestOrder(request, data):
    print('User is not logged in')

    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    surname = data['form']['surname']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    try:
        customer = Customer.objects.get(email=email)

    except:
        customer = Customer.objects.create(email=email, name=name, surname=surname)
    # customer, created = Customer.objects.get_or_create(
    #     email=email,
    #     # customer ın mailini kaydetti, eğer kayıt olmadan tekrar bi daha alışveriş yapacak olursa ve aynı maili kullanırsa bu maille attach edecek yeni bir customer oluşturmaycak
    # )
    # customer.name = name
    # customer.surname = surname
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order
