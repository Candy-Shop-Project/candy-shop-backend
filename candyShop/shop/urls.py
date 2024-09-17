# shop/urls.py 
from django.urls import path
from .views import product_list, add_product

urlpatterns = [
    path('products/', product_list, name='product_list'), #endpoint to query all product entries
    path('add_product/', add_product, name='add-product'), #add a new product to db
]