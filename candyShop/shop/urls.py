# shop/urls.py 
from django.urls import path
from .views import product_list, add_product, delete_product, update_product, add_category

urlpatterns = [
    path('products/', product_list, name='product_list'), #endpoint to query all product entries
    path('add_product/', add_product, name='add-product'), #add a new product to db
    path('add_category/', add_category, name='add_category'),  # endpoint to add new categories (pass json in body {"name": "category"})
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'), # delete product by id, passed from frontend
    path('update_product/<int:product_id>/', update_product, name='update_product'), # update product by id, passed from frontend
]