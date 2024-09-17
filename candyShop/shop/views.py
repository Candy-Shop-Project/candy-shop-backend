from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

# get products for main page
@api_view(['GET'])
@permission_classes([AllowAny])  # allow anyone to access this view
def product_list(request):
    try:
        products = Product.objects.all()  # query all products from heroku db
        serializer = ProductSerializer(products, many=True)  # serialize queryset
        return Response(serializer.data)  # JSON response
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# view to handle POST requests for creating a new product
@api_view(['POST'])
@permission_classes([AllowAny])  # allows anyone to access this view(change later)
def add_product(request):
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)  # deserialize data
        if serializer.is_valid():  # validate data
            serializer.save()  # save data to heroku database using django ORM
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # return the created product data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # return validation errors


# view to handle DELETE requests for deleting a product
@api_view(['DELETE'])
@permission_classes([AllowAny]) # change later
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