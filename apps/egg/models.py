from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = []
        if len(postData['first_name']) <2 or str.isalpha(postData['first_name']) == False:
            errors.append('First Name should be at least 2 characters and must be letters only')
        if len(postData['last_name']) <2 or str.isalpha(postData['last_name']) == False:
            errors.append('Last name should be at least 2 characters and must be letters only')
        if not EMAIL_REGEX.match(postData['email']):
            errors.append('Email is not a valid format')
        if postData['password'] != postData['passconf']:
            errors.append('Passwords must match')
        if len(postData['password'])<8:
            errors.append('Password must be at least 8 characters')
        if len(User.objects.filter(email = postData['email'])) == 1:
            errors.append('Email already in system')
        return errors

    def login_validator(self, postData):
        errors = []
        if len(postData['login_email'])<2:
            errors.append("Email needs at least 2 characters")
        
        if len(postData['login_password'])<2:
            errors.append("Password needs at least 2 characters")

        if not EMAIL_REGEX.match(postData['login_email']):
            errors.append('Email is not a valid format')

        try:
            user = User.objects.get(email = postData['login_email'])
            inputpw = postData['login_password']
            print('before decode inputpw='+inputpw)
            encoded = inputpw.encode('utf-8')
            print('after encode encoded='+str(encoded))
            if not bcrypt.checkpw(encoded, user.password.encode('utf-8')):
                errors.append('Try again')
        except ObjectDoesNotExist:
            errors.append('Try again-user not found')
        
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

    def __str__(self):
        return self.first_name+' '+self.last_name
        
class Item(models.Model):
    model_number = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=2, decimal_places = 1)
    price = models.DecimalField(max_digits=5, decimal_places = 2)
    item_type = models.CharField(max_length=255)
    picture = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return 'model_number='+self.model_number+'\nname='+self.name+'\nmanufacturer='+self.manufacturer+'\ndescription='+self.description+'\nrating='+str(self.rating)+'\nprice='+str(self.price)+'\nitem_type='+self.item_type+'\npicture='+self.picture

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'cart')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'cart')
    quantity = models.IntegerField(default = 1)

    def __str__(self):
        return 'cart.id='+str(self.id)+'\ncart.user='+str(self.user)+'\ncart.item.id='+str(self.item.id)+'\ncart.quantity='+str(self.quantity)

class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'orderhistory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'orderhistory')
    quantity = models.IntegerField(default = 1)
    created_at = models.DateTimeField(auto_now_add = True)

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'order')
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'order')
    
#     shippingAdr = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add = True)
#     updated_at = models.DateTimeField(auto_now = True)