from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify

class TechnoAdmin(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email    = models.EmailField()

    def __str__(self):
        return self.username



class NewCategory(MPTTModel):
    title = models.CharField(max_length=355)
    category_keywords = models.CharField(max_length=355)
    category_description = models.TextField()
    icon = models.CharField(max_length=355)
    slug = models.SlugField(max_length=255)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['title']
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)    

    def __str__(self):
        return f"{self.title} {self.category_keywords}"






class Tag(models.Model):
    tag = models.CharField(max_length=255)

class Color(models.Model):
    color = models.CharField(max_length=255)    

class Product(models.Model):
    in_cart = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, default='Unknown')
    slug = models.SlugField(max_length=255, unique=True)
    product_count = models.IntegerField()
    sku = models.CharField(max_length=255)
    stock_status = models.CharField(max_length=255, choices=[('0', 'In stock'), ('1', 'Out of stock')])
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ForeignKey kullanarak kategori ilişkileri
    parent_category = models.ForeignKey(NewCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='parent_products')
    sub_category = models.ForeignKey(NewCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_products')
    sub_sub_category = models.ForeignKey(NewCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_sub_products')

    description = models.TextField()
    primary_photo = models.ImageField(upload_to='product_photos/')
    photo1 = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    photo2 = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    photo3 = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    photo4 = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    
    tags = models.ManyToManyField(Tag)
    colors = models.ManyToManyField(Color)

    def __str__(self):
        return self.title




class Contact(models.Model):
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    comment = models.TextField()

    def __str__(self):
        return self.name + ' ' + self.lastname