from django.db import models

# create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100) # product name
    description = models.TextField() # product description
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=200) # image URL storage
    created_at = models.DateTimeField(auto_now_add=True)  # timestamp for product creation
    updated_at = models.DateTimeField(auto_now=True)  # timestamp for the last update

    def __str__(self):
        return self.name