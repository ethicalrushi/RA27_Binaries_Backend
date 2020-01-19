from django.views.generic import View
from django.shortcuts import render
from datetime import date
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework import viewsets, permissions,generics
from .models import *
from user.models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  
from collections import defaultdict
from .sms import send_sms

from rest_framework import status
import traceback
import http 
from decouple import config

@api_view(['post'])
def PlaceOrderView(req):
    
    foodgrain = FoodGrain.objects.get(id=req.data['foodgrain_id'])
    buyer = req.user
    farmer = User.objects.get(contact=req.data['farmer_contact'])
    quantity = req.data['quantity']

    ts = TransactionSale.objects.create(
        type= '1',
        seller= farmer,
        buyer = buyer,
        quantity = quantity,
        foodgrain = foodgrain,
        price = foodgrain.price,
    )
    obj = TransactionSaleSerializer(ts).data
    message = buyer.name+ " wants to buy "+str(2)+"kg of "+foodgrain.type+" from you. Contact- "+str(buyer.contact) 
    send_sms(farmer.contact, message)

    return Response(obj)

class TotalBidListView(generics.ListCreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

class ActiveBidListView(generics.ListAPIView):
    queryset = Bid.objects.filter(isActive = True)
    serializer_class = BidSerializer


class BidDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

@api_view(['post'])
def CreateBidView(req):
    type = FoodGrain.objects.get(type=req.data['foodgrain'])
    quantity = req.data['quantity']
    description = req.data['description']
    deadline = datetime.datetime(2020,2,2)

    queryset = PlaceBid.objects.create(
        buyer = req.user,
        type = type,
        quantity= int(quantity),
        nbids=0,
        description=description,
        deadline=deadline
    )

    return Response(BidSerializer(queryset).data)
    


@api_view(['get'])
@permission_classes([IsAuthenticated])
def ProduceListView(req):

    queryset = req.user.produce.all()
    obj = ProduceSerializer(queryset,many=True).data

    return Response(obj)

@permission_classes([IsAuthenticated])
@api_view(['post'])
def report_produce(request):
    farmer = request.user
    foodgrain = FoodGrain.objects.get(id=request.data['fid'])
    grade = request.data['grade']
    quantity= request.data['quantity']
    price= request.data['price']

    location = farmer.farms.all()[0].location
    print('reached')

    produce = Produce.objects.create(farmer=farmer,type=foodgrain,grade=grade,quantity=quantity,location=location,price=price)
    produce.save()
    poduceserializer = ProduceSerializer(produce).data
    return Response(poduceserializer)

class StorageTransactionListView(generics.ListCreateAPIView):
    queryset = StorageTransaction.objects.filter(valid = True)
    serializer_class = StorageTransactionSerializer

@api_view(['post'])
def createStorageTransaction(request):
    warehouse = Warehouse.objects.get(id=request.data['warehouse'])
    produce = Produce.objects.get(id=request.data['produce'])
    farmer = request.user
    quantity = request.data['quantity']
    cost = warehouse.price
    # transno = random.randint(1,1000000)
    storagetransaction = StorageTransaction.objects.create(
        warehouse = warehouse,
        produce = produce,
        farmer = farmer,
        quantity = quantity,
        cost = cost,
        farmerprice = produce.price
    )
    storagetransaction.save()

    produce.quantity -= quantity
    produce.save()

    warehouse.free_space -= quantity
    warehouse.save()
    print('saved')

    # data = StorageTransactionSerializer(storagetransaction).data
    # print(data)

    return Response({"flag":True,}, status=status.HTTP_200_OK)

@api_view(['get'])
@permission_classes([IsAuthenticated])
def TransactionSaleListView(req):
    queryset = TransactionSale.objects.filter(buyer=req.user)
    data = TransactionSaleSerializer(queryset,many=True).data

    return Response(data)


class ProduceListFilter(APIView):


    def get(self, request):
        num = request.GET['num']
        type = request.GET['type']
        type = FoodGrain.objects.get(id = type)
        queryset = Produce.objects.filter(type = type)
        ans = []
        for i in queryset:
            if i.quantity>int(num):
                ans.append(i.id)
        return Response({'produce':ans})

class ApproveOrder(APIView):
    def get(self, request, pk):
        id_ = pk
        obj = TransactionSale.objects.get(id = id_)
        if obj.produce.quantity >= obj.quantity:
            obj.approved = True
            obj.produce.quantity-=obj.quantity
            obj.produce.save()
            mess = "Order Approved"
        else:
            obj.valid = False
            mess = "Not Enough Produce"
        obj.save()
        return Response({'message':mess})


@api_view(['get'])
def BuyerOrdersListView(req):
    queryset = [x for x in req.user.sale_buyer.all()]
    data =TransactionSaleSerializer(queryset,many=True).data

    for i in range(len(queryset)):
        data[i]['foodgraintype']=queryset[0].foodgrain.type
        data[i]['seller']=queryset[0].seller.name
        data[i]['buyer']=queryset[0].buyer.name

    return Response(data)


@api_view(['get'])
def FarmerOrdersListView(req):
    queryset = [x for x in req.user.sale_seller.all()]
    data =TransactionSaleSerializer(queryset,many=True).data

    for i in range(len(queryset)):
        data[i]['foodgraintype']=queryset[i].foodgrain.type
        data[i]['seller']=queryset[i].seller.name
        data[i]['buyer']=queryset[i].buyer.name

    return Response(data)

@api_view(['post'])
def ApproveFarmerOrderView(req,id):
    tsale = req.user.sale_seller.get(id=int(id))
    get_from = req.data['get_from']
    quanity_to_delete = tsale.quantity

    produce = req.user.produce.all()
    produce = produce[0] if produce else None

    strans = req.user.storagetransaction_set.all()
    strans = strans[0] if  strans else None

    if get_from=='produce' and produce:
        tsale.produce = produce
        temp = min(produce.quantity,quanity_to_delete)
        quanity_to_delete -= temp
        produce.quantity -= temp
        produce.save()

        if quanity_to_delete and warehouse:
            strans.quantity -= quanity_to_delete
            strans.save()

    elif strans:
        tsale.warehouse = strans.warehouse
        temp = min(strans.quantity,quanity_to_delete)
        quanity_to_delete -= temp
        strans.quantity -= temp
        strans.save()

        if quanity_to_delete and produce:
            produce.quantity -= quanity_to_delete
            produce.save()


    tsale.approved=True
    tsale.save()


    return Response(True)


@api_view(['get'])
def RejectFarmerOrderView(req,id):
    req.user.sale_seller.get(id=int(id)).delete()
    return Response(True)


def gen_mess(user, arr):
    print(arr)
    if arr[0]=='report':    # type quant price grade
        loc = Location(xloc = 0, yloc = 0)
        loc.save()
        type = FoodGrain.objects.get(type = arr[1])
        prdc = Produce(
            type = type,
            farmer=user,
            grade=arr[4],
            quantity=int(arr[2]),
            price=int(arr[3]),
            location = loc,
            date=date.today()
        )
        prdc.save()
        message = "Produce saved"

    elif arr[0] == 'store':
        type = FoodGrain.objects.get(type = arr[1])
        queryset = Warehouse.objects.filter(foodgrain = type , free_space__gt = int(arr[2]))
        message=""
        for i in queryset:
            message+="Name : " +i.name +"\\n"+"Free Space : " + str(i.free_space)+"\\n"+"Total Space"+str(i.total_space)+""  

    elif arr[0] == 'approve' or arr[0] == 'decline':
        order = TransactionSale.objects.get(transno = int(arr[1]))
        if arr[0] == 'approve':
            order.approve = True
            message = "Order number "+arr[1]+" Approved"
        else:
            order.approve = False
            message = "Order number "+arr[1]+" Decline"
        order.save()

    elif arr[0]=="getbid" or arr[0] =="किसान":
            queryset = Bid.objects.all()
            message = ''
            for i in queryset:
                message += "Bid no : "+str(i.transno) + "//n" + "FoodGrain : "+i.type.type + "//n"+"Quantity : "+str(i.quantity) +"//n"+"Description : "+i.description

    elif arr[0]=="bid":
            transno=Bid.objects.get(transno=arr[1])
            bidval=PlaceBid(
                        bid=transno,
                        farmer=user,
                        price=float(arr[2]),
                        description=arr[3],


            )
            bidval.save()
            message="Bid Placed Successfully"

    elif arr[0] == "weather":
            message = "Weather report for following Month : Mostly Sunny , Expected light showers on 5,6 and 7 February"
    else:
        message = "PLease follow the standard format"

    print(message)
    return message

from transaction.sms import send_sms

@api_view(['POST'])
def message(request):
    contact = request.data['contact']
    message = request.data['message']
    newcontact = contact[3:]
    print(contact, message)
    message=message.lower()
    try:
        user = User.objects.get(contact = newcontact)
    except:
        message = "Rishabh's private message"
        print("Rishabh's private message")
    else:
        arr = message.split(' ')
        mess = gen_mess(user,arr)
        send_sms(newcontact,mess)
        print(user)
        print(message)
    return Response({'message':message})


class GetCenterDetails(APIView):
    def get(self, request, pk):
        id_ = pk
        centre = Centre.objects.get(id = id_)
        loc = Location.objects.filter(centre = centre)
        farms = [farm.id for farm in Farms.objects.all() if farm.location in loc]
        farmers = [Farms.objects.get(id = i).farmer.id for i in farms]
        produce = [prdc.id for prdc in Produce.objects.all() if prdc.location in loc]
        warehouses = [warehouse.id for warehouse in Warehouse.objects.all() if warehouse.location in loc]
        storage_transactions = [st for st in StorageTransaction.objects.all() if st.warehouse.location in loc]
        sale_transactions = [st for st in TransactionSale.objects.all() if st.seller.id in farmers]
        quant = defaultdict(lambda : 0)
        storage_revenue = defaultdict(lambda : 0)
        sale_revenue = defaultdict(lambda : 0)
        print(produce, storage_transactions, sale_transactions)
        for i in produce:
            quant[Produce.objects.get(id = i).type.id]+=Produce.objects.get(id = i).quantity
            
        for i in storage_transactions:
            quant[i.produce.type.id]+=i.quantity
            storage_revenue[i.produce.type.id] += i.cost
        for i in sale_transactions:
            sale_revenue[i.produce.type.id] += i.price
        
        return Response({'farms' : farms, 'farmers' : farmers, 'produce' : produce , 'warehouses':  warehouses, 'quant' : quant, 'storage_revenue': storage_revenue, 'sale_revenue':sale_revenue})


@api_view(['get'])
def farmerDashboardGraphView(req):
    import random
    result = []

    months = ['jan','feb','mar','apr','jun','jul','aug','sep','oct','nov','dec']
    for month in months:
        result.append([month,round(random.random()*100,2),round(random.random()*100,2),round(random.random()*100,2)])
    
    return Response(result)



@api_view(['get'])
def PastBidList(req):
        user = req.user
        bids = Bid.objects.filter(buyer = user)
        bids = BidSerializer(bids,many=True).data
        return Response(bids)

class FarmerPlacedbids(APIView):
    def get(self, request):
        user = request.user
        placedbids = PlaceBid.objects.filter(farmer = user)
        return Response(placedbids)



@api_view(['get'])
def FarmerActiveBidList(request):
    user = request.user
    activeplacedbids = Bid.objects.filter(isActive = True)
    obj = BidSerializer(activeplacedbids,many=True).data
    return Response(obj)


@api_view(['GET', 'POST'])
def FarmerPlaceBid(request):    
    farmer = request.user
    bid = Bid.objects.get(id=int(request.data['bidno']))
    PlaceBid(bid = bid, 
    farmer = farmer, 
    price = int(request.data['price']), 
    description = request.data['description']).save()
    return Response(True)
    

@api_view(['GET'])
def FarmerResponseBidList(request, pk):    
    bid = Bid.objects.get(id = pk)
    return Response(bid.placedbids.objects.all())


@api_view(['GET'])
def ApproveBid(request, pk):  
    placedBid = PlaceBid.objects.get(id = pk)  
    bid = placedBid.bid
    """transno = models.CharField(max_length=200,null=True, blank=True)
    approved=models.BooleanField(default=False)
    type=models.CharField(max_length=1,choices = CHOICES)
    seller=models.ForeignKey(User,on_delete=models.CASCADE, related_name='sale_seller')
    buyer=models.ForeignKey(User,on_delete=models.CASCADE, related_name='sale_buyer')
    produce=models.ForeignKey(Produce, blank=True, null=True, on_delete=models.CASCADE)
    foodgrain=models.ForeignKey(FoodGrain, blank=True, null=True, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, blank=True, null=True, on_delete=models.CASCADE)
    quantity=models.FloatField()
    price=models.FloatField()"""
    transno = Random.randint(1, 10**6)
    approved = True
    type = bid.type.name
    seller = placedBid.farmer
    buyer = bid.buyer
    foodgrain = bid.type
    quantity = placedBid.quantity
    price = placedBid.price
    TransactionSale(transno = transno, approved =approved, type = type, seller =seller, buyer = buyer, foodgrain = foodgrain, quantity = quantity, price = price).save()
    return Response("Transaction Done")

@api_view(['post'])
def createBid(req):
    bid = Bid.objects.create(
        buyer=req.user,
        type=FoodGrain.objects.get(type=req.data['foodgrain']),
        quantity=int(req.data['quantity']),
        description=req.data['description'],
        deadline='2020-02-01'
    )

@api_view(['get'])
def get_farmer_storage_warehouse(request):
    farmer = request.user
    print(farmer.name)
    storagetransactions = StorageTransaction.objects.filter(farmer=farmer)
    print(storagetransactions)
    # warehouses = [st.warehouse.id for st in storagetransactions]
    # queryset = Warehouse.objects.filter(pk__in = warehouses)
    data = StorageTransactionSerializer(storagetransactions,many=True).data
    return Response(data)


class DefCentreView(APIView):
    def get(self, request):
        id_ = 1
        centre = Centre.objects.get(id = id_)
        loc = Location.objects.filter(centre = centre)
        farms = [farm.id for farm in Farms.objects.all() if farm.location in loc]
        farmers = [Farms.objects.get(id = i).farmer.contact for i in farms]
        print(centre.def_crops)
        message = "Centre : "+str(id_)+" is facing a shortage of " + ', '.join(centre.def_crops.all())
        for num in farmers:
            #send_sms(num, message)
            print(num, message)
        return Response(message)
    # obj = BidSerializer(bid)

    # return Response(obj.data)
