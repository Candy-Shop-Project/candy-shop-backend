# shop/urls.py 
from django.urls import path
from .views import product_list, add_product, delete_product, update_product, add_category, individual_product, search_product, get_multiple_products

urlpatterns = [
    path('products/', product_list, name='product_list'), #endpoint to query all product entries
    path('add_product/', add_product, name='add-product'), #add a new product to db
    path('add_category/', add_category, name='add_category'),  # endpoint to add new categories (pass json in body {"name": "category"})
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'), # delete product by id, passed from frontend
    path('update_product/<int:product_id>/', update_product, name='update_product'), # update product by id, passed from frontend
    path('individual_product/<int:product_id>/', individual_product, name='individual_product'), # retrive specific product, with product_id passed with url from client
    path('search_product/', search_product, name='search_product'), # search in product table using query
    path('get_multiple_products/', get_multiple_products, name='get_multiple_products'),
]