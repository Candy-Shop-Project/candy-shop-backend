from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# env import
import environ


#initialise environ
env = environ.Env()
environ.Env.read_env()

# get products for main page, filter logic included
@api_view(['GET'])
@permission_classes([AllowAny])  # allow anyone to access this view
def product_list(request):
    try:
        category_name = request.GET.get('category')  # get category (if available) from query parameter

        # if category exist
        if category_name:
            category = Category.objects.get(name=category_name)
            products = Product.objects.filter(category=category)  # filter products by category
        else:
            products = Product.objects.all()  # query all products if no category is specified

        serializer = ProductSerializer(products, many=True)  # serialize the queryset
        return Response(serializer.data)  # return the serialized data as JSON response to frontend
    
    # if specified category doesnt exist
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    # other error handling
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# create new category for product
# View to handle POST requests for creating a new category
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # allows anyone to access this view (change later)
def add_category(request):
    serializer = CategorySerializer(data=request.data)  # deserialize the incoming data

    if serializer.is_valid():  # check if data is valid
        serializer.save()  # save the category to database
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # return created category data
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # return validation errors


# view to handle POST requests for creating a new product
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # allows anyone to access this view(change later)
def add_product(request):
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)  # deserialize data
        if serializer.is_valid():  # validate data
            serializer.save()  # save data to heroku database using django ORM
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # return the created product data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # return validation errors


# view to handle DELETE requests for deleting a product
@api_view(['DELETE'])
@permission_classes([IsAuthenticated]) # change later
def delete_product(request, product_id):
    try:
        # try to retrive data from db by id provided with request
        product = Product.objects.get(id=product_id)
        product.delete() # delete product from db if row with id was found
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT) # success message response
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND) # if no row with such id found
    except Exception as e:
        return Response({"error" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # other server error

# view to handle UPDATE requests for updating specific product with id
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_product(request, product_id):
    try:
        # retirve product from the database
        product = Product.objects.get(id=product_id)

        # pass product and incoming data from request to serializer, also allow partial updates
        serializer = ProductSerializer(product, data=request.data, partial=True)


        if serializer.is_valid():
            serializer.save() # save only fields which were updated
            return Response(serializer.data, status=status.HTTP_200_OK) # returns updates product data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # return if error occurs

    except Product.DoesNotExist:
        return Response({"error" : "Product not found"}, status=status.HTTP_404_NOT_FOUND) # 404 if product by id not found

    except Exception as e:
        return Response({"error" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # if other than 404 error occurs


# view to handle fetch from shop database for specific product with unique id (request from frontend)
@api_view(['GET'])
@permission_classes([AllowAny])
def individual_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id) # retrive product from db
        
        serializer = ProductSerializer(product) # serialize to send to client
        
        return Response(serializer.data, status=status.HTTP_200_OK) # return serialized data
    
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND) # as previously used (404)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # same for 500

# searchbar view
@api_view(['GET'])
@permission_classes([AllowAny])
def search_product(request):
    try:
        # get search query parameter
        search_query = request.GET.get('search_product', '')

        # if search query is provided, filter products by name using not case sensetive
        if search_query:
            products = Product.objects.filter(name__icontains=search_query)  # if partial match
        else:
            products = Product.objects.none()  # if no query provided, return empty queryset

        # if no products found
        if not products.exists():
            return Response({"message": "No products found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# retrive products by their ids (for cart frontend fetch). Pass ids in request body {"id" : [103, 105, 184 etc...]}
@api_view(['POST'])
@permission_classes([AllowAny])
def get_multiple_products(request):
    try:
        ids_list = request.data.get('ids', [])
        if not isinstance(ids_list, list) or not ids_list:
            return Response(
                {"error": "'ids' must be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # limit number of input ids to prevent abuse
        MAX_IDS = 100
        if len(ids_list) > MAX_IDS:
            return Response(
                {"error": f"Too many IDs provided. Maximum allowed is {MAX_IDS}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # convert all ids to integers and filter out invalid ones
        valid_ids = []
        for id_value in ids_list:
            try:
                valid_id = int(id_value)
                if valid_id > 0:
                    valid_ids.append(valid_id)
            except (ValueError, TypeError):
                continue  # skip invalid ids

        if not valid_ids:
            return Response(
                {"error": "No valid IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(id__in=valid_ids)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # log the exception internally
        return Response(
            {"error": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )