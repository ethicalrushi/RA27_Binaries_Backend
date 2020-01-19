from django.db import models
import uuid
from user.models import User,Farms,Warehouse,FoodGrain,Location
import datetime

# Create your models here.
"""
Add an image field
"""

#add default date
class Produce(models.Model):
    type=models.ForeignKey(FoodGrain,on_delete=models.CASCADE, related_name='produce')
    farmer=models.ForeignKey(User,on_delete=models.CASCADE, related_name='produce')
    grade=models.CharField(max_length=50)
    quantity=models.FloatField()
    price=models.FloatField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='produce')
    date=models.DateField( default=datetime.date.today)

    def __str__(self):
        return self.farmer.name

#add default date
class StorageTransaction(models.Model):
    transno=models.CharField(max_length=50,null=True, blank=True)
    warehouse=models.ForeignKey(Warehouse,on_delete=models.CASCADE)
    farmer = models.ForeignKey(User,on_delete=models.CASCADE)
    produce=models.ForeignKey(Produce,on_delete=models.CASCADE)
    quantity = models.FloatField()
    cost = models.FloatField()
    farmerprice = models.FloatField(null=True, blank=True)
    date = models.DateField( default=datetime.date.today)
    valid = models.BooleanField(default=True)
    invoice=models.FileField(null=True,blank=True)

    def __str__(self):
        return self.farmer.name+'-'+self.produce.type.type+'-'+str(self.quantity)


class TransactionSale(models.Model):
    CHOICES = (
        ("1", "From Produce"),
        ("2", "From Warehouse"),
        ("3", "From both"),
    )
    transno = models.CharField(max_length=200,null=True, blank=True)
    approved=models.BooleanField(default=False)
    type=models.CharField(max_length=1,choices = CHOICES)
    seller=models.ForeignKey(User,on_delete=models.CASCADE, related_name='sale_seller')
    buyer=models.ForeignKey(User,on_delete=models.CASCADE, related_name='sale_buyer')
    produce=models.ForeignKey(Produce, blank=True, null=True, on_delete=models.CASCADE)
    foodgrain=models.ForeignKey(FoodGrain, blank=True, null=True, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, blank=True, null=True, on_delete=models.CASCADE)
    quantity=models.FloatField()
    price=models.FloatField()
    invoice=models.FileField(null=True,blank=True)
    # dprice=models.FloatField()

    def __str__(self):
        return str(self.quantity) + ' ' + str(self.price)

"""
Add a completely new delivery model, with a new user role.
"""
# class Delivery(models.Model):
#     name=models.CharField(max_length=50)
#     cont = models.CharField(max_length=50)
#     cost=models.FloatField()
#     loc=models.ForeignKey(Location,on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name

def creatransno():
    import random 
    return str(round(random.random()*10**12))


class Bid(models.Model):
    isActive = models.BooleanField(default = True)
    transno=models.CharField(max_length=50,unique=True,default=creatransno)
    buyer=models.ForeignKey(User,on_delete=models.CASCADE, related_name='bids')
    type=models.ForeignKey(FoodGrain,on_delete=models.CASCADE)
    quantity=models.FloatField()
    nbids = models.IntegerField(default = 0) #price
    description=models.TextField()
    deadline=models.DateField()

    

    def __str__(self):
        return self.transno

class PlaceBid(models.Model):
    bid=models.ForeignKey(Bid,on_delete=models.CASCADE)
    farmer=models.ForeignKey(User,on_delete=models.CASCADE, related_name='placed_bids')
    price=models.FloatField()
    description=models.TextField()

    def __str__(self):
        return str(self.bid)
