from django.shortcuts import render, HttpResponse, redirect
from apps.egg.models import *
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# Create your views here.

def index(request):
    print("Reloading *******")
    if 'count' in request.session:
        request.session['count']=request.session['count']
    else:
        request.session['count'] = 0
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
        request.session['count'] = len(Cart.objects.filter(user = user))
        # need to fix cart
        context = {
            'items':Item.objects.all(),
            'cart':Cart.objects.filter(user = user)
        }
        return render(request, 'egg/index.html', context)
        #return render(request, 'egg/home.html', context)
    else: 
        context = {
            'items':Item.objects.all()
            # possible solution to page (1,2,3,etc) numbers
            # 'items':Item.objects.all().reverse().order_by('-id')[7:11]
        }
        return render(request, 'egg/index.html', context)
        #return render(request, 'egg/home.html',context)

def loginorregister(request):
    return render(request, 'egg/login.html')

def register(request):
    print('begin of views.register')
    errors = User.objects.basic_validator(request.POST)
    if errors:
        for e in errors:
            messages.error(request,e,extra_tags="register")
        return redirect('/loginorregister/')
    else:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        conf = request.POST['passconf']
        encoded = request.POST['password'].encode('utf-8')
        print('check encoded='+str(encoded))
        pwHash = bcrypt.hashpw(encoded,bcrypt.gensalt())
        decoded = pwHash.decode('utf-8')
        print('check decoded='+decoded)
        #hash1 = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        User.objects.create(first_name = first_name, last_name = last_name, email = email, password = decoded)
        user = User.objects.get(first_name = first_name, last_name = last_name, email = email, password = decoded)
        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['id']=user.id
        return redirect('/')


def login(request):
    errors = User.objects.login_validator(request.POST)
    if errors:
        for e in errors:
            messages.error(request,e,extra_tags="login")
        return redirect('/loginorregister/')
    else:
        print('login success!')
        user = User.objects.get(email=request.POST['login_email'])
        request.session['first_name'] = user.first_name
        request.session['last_name'] = user.last_name
        request.session['id']=user.id
        return redirect('/')
        

def itemDisplay(request,number):
    this_type = Item.objects.get(id=int(number)).item_type
    print('the type is')
    print(this_type)
    this_rating = float(Item.objects.get(id=int(number)).rating)
    print('float=')
    print(this_rating)
    stars=[]
    halfstar=[]
    while this_rating>=1:
        this_rating-=1
        stars.append(1)
    while this_rating>0:
        this_rating-=0.5
        halfstar.append(1)
    print(stars)
    print(halfstar)
    context={
        "item":Item.objects.get(id=int(number)),
        "similars":Item.objects.filter(item_type=this_type).exclude(id=int(number)),
        "stars":stars,
        "halfstar":halfstar
    }
    return render(request,'egg/item.html',context)


def create(request):
    print('Start of create...')
    print('request.POST='+str(request.POST))
    if 'part' in request.POST and 'manuf' in request.POST and 'search_box' in request.POST:
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'), manufacturer__in=request.POST.getlist(u'manuf'), model_number__startswith=request.POST['search_box'])
        }
        
    elif 'part' in request.POST and 'search_box' in request.POST and 'manuf' not in request.POST :
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'), model_number__startswith=request.POST['search_box'])
        }
    elif 'manuf' in request.POST and 'search_box' in request.POST and 'part' not in request.POST :
        context = {
        'item':Item.objects.filter(manufacturer__in=request.POST.getlist(u'manuf'), model_number__startswith=request.POST['search_box'])
        }
    elif 'part' in request.POST and 'manuf' in request.POST and 'search_box' not in request.POST:
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'), manufacturer__in=request.POST.getlist(u'manuf'))
        }
    elif 'search_box' in request.POST and 'part' not in request.POST and 'manuf' not in request.POST:
        print('in request.post.search_box')
        print(request.POST['search_box'])
        context = {
            #'item':Item.objects.filter(model_number__startswith=request.POST['search_box']) # search by model
            'item':Item.objects.filter(name__startswith=request.POST['search_box']) # try search directly by name
        }
    elif 'part' in request.POST and 'manuf' not in request.POST and 'search_box' not in request.POST:
        print('only part in the request.POST')
        context = {
        'item':Item.objects.filter(item_type__in=request.POST.getlist(u'part'))
        }
    elif 'manuf' in request.POST and 'part' not in request.POST and 'search_box' not in request.POST:
        print('only manuf in the request.POST')
        context = {
        'item':Item.objects.filter(manufacturer__in=request.POST.getlist(u'manuf'))
        }
    else:
        print('none of the above caught it...')
        return render(request, 'egg/filter.html', context = {'item':Item.objects.all()})
    return render(request, 'egg/filter.html', context)

# home page header drop down click ajax functions
def findGPU(request):
    print('start of findGPU')
    print('reqest.POST[data]='+str(request.POST['data']))
    if (request.POST['data']=='manuf=amd'):
        context={
            'item':Item.objects.filter(manufacturer='amd')
        }
    else:
        context={
            'item':Item.objects.filter(manufacturer='nvidia')
        }
    
    return render(request, 'egg/filter.html', context)

# find CPU by brands
def findCPU(request):
    print('start of findCPU')
    print('reqest.POST[data]='+str(request.POST['data']))
    if (request.POST['data']=='manuf=intel'):
        context={
            'item':Item.objects.filter(manufacturer='intel')
        }
    else:
        context={
            'item':Item.objects.filter(manufacturer='amd')
        }
    
    return render(request, 'egg/filter.html', context)

# RAM by brands
def findRAM(request):
    print('start of findRAM')
    print('reqest.POST[data]='+str(request.POST['data']))
    if (request.POST['data']=='manuf=corsair'):
        context={
            'item':Item.objects.filter(manufacturer='corsair')
        }
    else:
        context={
            'item':Item.objects.filter(manufacturer='gskill')
        }
    
    return render(request, 'egg/filter.html', context)

def additem(request):
    if 'id' in request.session:
        request.session['count']+=1
        user = User.objects.get(id=request.session['id'])
        item = Item.objects.get(id = request.POST['item_id'])
        try:
            item = Item.objects.get(id = request.POST['item_id'])
            my_cart = Cart.objects.get(user = user, item = item)
            my_cart.quantity += 1
            my_cart.save()
        except:
            Cart.objects.create(user = user, item=item)
        return redirect('/')
    else:
        if 'cart' in request.session:
            request.session['count']+=1
            if 'item_id' not in request.POST:
                return HttpResponse('403 forbidden!')
            else:
                temp_cart = request.session['cart']
                temp_post = int(request.POST['item_id'])
                temp_cart.append(temp_post)
                request.session['cart'] = temp_cart
        else:
            if 'item_id' not in request.POST:
                return HttpResponse('403 forbidden!')
            else:
                request.session['count']+=1
                request.session['cart'] = []
                temp_cart = request.session['cart']
                temp_post = int(request.POST['item_id'])
                temp_cart.append(temp_post)
                request.session['cart'] = temp_cart
        return redirect('/')
        # need to ad logic here for session cart
    
#in top right cart picture, trash button click#
def delItem(request,number):
    print('start of delItem...')
    print('the number is= '+ number)
    if 'id' in request.session:
        # get the user,
        user = User.objects.get(id=request.session['id'])
        print('check if found user:'+str(user))
        # find this cart that contains the item, remove it, the current logic 
        # if not perfect, we created single cart for each item, but it works still
        carts = Cart.objects.filter(user=user)
        for c in carts:
            print('************************************')
            print('cart='+str(c))
            if(c.id==int(number)):
                c.delete()
    return redirect('/')

def cart(request):
    # registered customer, find his cart by userid, caculate total 
    # render page with total and cart
    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
        total = 0
        for i in Cart.objects.filter(user=user):
            total += i.item.price * i.quantity
        context={
            "cart":Cart.objects.filter(user=user),
            'total':total
        }
    else:
        if 'cart' not in request.session:  # guest customer logic 1. guest don't have a cart session yet, so starts with 0
            context = {
                'total':0
            }
            return render(request, 'egg/newcart.html', context)
        else:    
            # guest has cart session started,   
            total = 0
            quant = {}  # quant dictionary is { item.id: quantity }
            for i in request.session['cart']: # i is item id   session.cart store item.id
                print('request.session[cart]=')
                if i not in quant:
                    quant[i]=1
                else:
                    quant[i]+=1
                item = Item.objects.get(id=i)
                total += item.price         # total is calculated price 
            
            for key, value in quant.items():
                key = int(key)
                print('quant.key='+str(key))       # quant = { item.id : quantity }
                print('quant.value='+str(value))
            
            context = {
                "cart":Item.objects.filter(id__in=request.session['cart']), # the cart here actually are items filter by id
                "total":total,
                "quant":quant
            }
            print('.....before checking the cart.....')
            print(context["cart"])

    return render(request,'egg/newcart.html',context)

def purchase(request):
    # print(request.POST)
    if 'id' in request.session:
        try:
            user = User.objects.get(id=request.session['id'])
            for i in Cart.objects.filter(user = user):
                OrderHistory.objects.create(user = user, item = i.item, quantity = request.POST[i.item.name])
                cart = Cart.objects.filter(item = i.item)
                request.session['count'] = 0
                cart.delete()
            return redirect('/orderhistory')
        except:
            return redirect('/')
    else:
        request.session['purchase'] = request.session['cart']
        request.session['count'] = 0
        del request.session['cart']
        return redirect('/orderhistory')

# Render Checkout page only, click placeorder go to orderhistory for now
def checkout(request):

    if 'id' in request.session:
        user = User.objects.get(id=request.session['id'])
        total = 0
        for i in Cart.objects.filter(user=user):
            total += i.item.price * i.quantity
        context={
            "cart":Cart.objects.filter(user=user),
            'total':total
        }

    else:
        print('guest user checkout starting, check session[cart] ')
        print(request.session['cart'])
        total = 0
        quant = {}
        for i in request.session['cart']:
            if i not in quant:
                quant[i]=1
            else:
                quant[i]+=1
            item = Item.objects.get(id=i)
            total += item.price
        context={
            "cart":request.session['cart'],
            "total":total
            "quant":quant
        }
    
    return render(request,'egg/checkout.html',context)


#  after click place order go here:
def orderhistory(request):
    if 'id' not in request.session:
        if 'purchase' not in request.session:
            return redirect('/')
        else:
            total = 0
            quant = {}
            for i in request.session['purchase']:
                if i not in quant:
                    quant[i]=1
                else:
                    quant[i]+=1
                item = Item.objects.get(id=i)
                total += item.price
            
            for key, value in quant.items():
                key = int(key)
            context = {
                "orderhis" : Item.objects.filter(id__in=request.session['purchase']),
                "total":total,
                "quant":quant
            }
            return render(request,'egg/orderhistory.html', context)
    else:
        user = User.objects.get(id=request.session['id'])
        total = 0
        for i in OrderHistory.objects.filter(user=user):
            total += i.item.price * i.quantity
            print(total)
        context = {
            'orderhis': OrderHistory.objects.filter(user=user),
            'total':total
        }
        return render(request,'egg/orderhistory.html', context)
    
def clear(request):
    if 'first_name' in request.session:
        del request.session['first_name']
    if 'last_name' in request.session:
        del request.session['last_name']
    if 'id' in request.session:
        del request.session['id']
    if 'cart' in request.session:
        del request.session['cart']
    if 'purchase' in request.session:
        del request.session['purchase']
    if 'count' in request.session:
        del request.session['count']
    return redirect('/')