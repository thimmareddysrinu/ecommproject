from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Admin(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE ,related_name='useradmin')
    full_name=models.CharField(max_length=100)
    mobile=models.CharField(max_length=10)
    image=models.ImageField(upload_to='admins')

    def __str__(self):
        return self.user.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
   
    fullname = models.CharField(max_length=70)
    adress = models.CharField(max_length=120, null=True, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname


class Category(models.Model):
    title = models.CharField(max_length=170)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=170)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    market_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField()
    descripitation = models.TextField(max_length=300)
    warranty = models.CharField(max_length=70, null=True, blank=True)
    return_policy = models.CharField(max_length=70, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products')

    def __str__(self):
        return self.title
class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)   
    image=models.ImageField(upload_to="products/images/") 
    def __str__(self):
        return self.product.title

class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sub_total = models.PositiveIntegerField()
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return "Cart:" + str(self.cart.id) + "Cartproduct:" + str(self.id)


ORDER_STATUS = (
    ('ORDER RECEVIED', 'ORDER RECEVIED'),
    ('ORDER ON THE WAY', 'ORDER ON THE WAY'),
    ('ORDER PROCESSED', 'ORDER PROCESSED'),
    ('ORDER COMPLETED', 'ORDER COMPLETED'),
    ('ORDER CANCELLED', 'ORDER CANCELLED'),
)
METHOD = (
    ('CASH ON DELIEVERY','CASH ON DELIVERY'),
    ('RAZORPAY','RAZORPAY'),
)


class Order(models.Model):
   
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=45, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    paymentmethod=models.CharField(max_length=20, choices=METHOD, default="cash on delivery")
    completed_payment=models.BooleanField(default=False,null=True,blank=True)
    razorpay_order_id=models.CharField(max_length=100,null=True,blank=True)
    razorpay_payment_id=models.CharField(max_length=100,null=True,blank=True)
    razorpay_signature=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return "Order: " + str(self.id)
