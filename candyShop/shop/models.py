from django.db import models

# category model -- (Related to Product model) --
class Category(models.Model):
    name = models.CharField(max_length=30, unique=True) # unique name for each category

    def __str__(self):
        return self.name

# main product model
class Product(models.Model):
    name = models.CharField(max_length=100) # product name
    description = models.TextField() # product description
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_id = models.CharField(max_length=100, blank=True, null=True)  # stripe price id
    image_url = models.URLField(max_length=200) # image URL storage
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', default=1) # category model relation (id). Defaults to 1 for previous data entries, or if new product created but no value for category provided
    created_at = models.DateTimeField(auto_now_add=True)  # timestamp for product creation
    updated_at = models.DateTimeField(auto_now=True)  # timestamp for the last update

    def __str__(self):
        return self.name