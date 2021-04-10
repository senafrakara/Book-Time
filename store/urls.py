from django.urls import path
from . import views
from .views import ProductDetail, FavoriteView, comment_delete, RemoveFavoriteList

urlpatterns = [
    # leave as empty string fo base url
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('update_cart/', views.updateCart, name="update_cart"),
    path('product_detail/<int:id>', ProductDetail, name="product_detail"),
    path('favorite/<int:id>', FavoriteView, name="favorite_product"),
    path('remove_favorites/<int:id>', RemoveFavoriteList, name="remove_favorites"),
    path('delete-comment/<int:id>', comment_delete, name='delete-comment'),
    path('search/', views.search, name='search'),
    path('aboutus/', views.aboutus, name='aboutus'),

    #kbr:
    path('contactus/', views.contactus, name='contactus'),
]
