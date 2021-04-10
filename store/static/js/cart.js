var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId', productId, 'Action:', action)
        console.log('USER: ', user)
        if (user == 'AnonymousUser') {
            console.log('User is not authenticated')
            addCookieItem(productId, action)
        } else {
            UpdateUserOrder(productId, action)
        }
    })
}

function addCookieItem(productId, action) {
    console.log('User is not authenticated 2....')

    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': 1}
            //js objesi oluşturuldu {'quantit'} derken ve 1 olarak eşitlendi yani o üründen 1 tane eklendi
        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove') {

        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            console.log('Remove item')
            delete cart[productId]
        }

    }
    console.log('Cart: ', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}

function UpdateUserOrder(productID, action) {
    console.log('User is logged in, sending data...')
    var url = '/update_item/'
    console.log('CART: ', cart)

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,

        },
        body: JSON.stringify({'productId': productID, 'action': action})
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('data', data)
            location.reload()
            // reload the page
        })
}

var logoutbtn = document.getElementById('logout')

logoutbtn.addEventListener('click', function () {
    // var productId = this.dataset.product
    // var action = this.dataset.action
    // console.log('productId', productId, 'Action:', action)
    console.log('USER: ', user)
    cart = {}
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    window.location.href = "{% url 'store' %}"

})

var loginbtn = document.getElementById('login-page-button')

loginbtn.addEventListener('click', function () {



})



