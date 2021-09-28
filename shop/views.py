from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from paytm import checksum
MERCHANT_KEY = 'kbzk1DSbJiv_O3p5';

# Create your views here.
def index(request):
    #products= Product.objects.all()
    #print(products)
    #n= len(products)
    #nSlides= n//4+ceil((n/4)-(n//4))
    #params={'no._of_slides':nSlides, 'range':range(1,nSlides), 'products':products}
    #allProds = [[products, range(1, nSlides), nSlides],
                #[products, range(1, nSlides), nSlides]]
    allProds=[]
    catprods= Product.objects.values('category', 'id')
    cats= {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n = len(prod)
        nSlides= n//4+ceil((n/4)-(n//4))
        allProds.append([prod, range(1,nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request,'shop/index.html', params)

def searchMatch(query, item):
    if query.lower() in item.product_name.lower() or query.lower() in item.category.lower() or query.lower() in item.desc.lower():
        return True
    else:
        return False

def search(request):
    query= request.GET.get('search')
    allProds=[]
    catprods= Product.objects.values('category', 'id')
    cats= {item['category'] for item in catprods}
    for cat in cats:
        prodtemp= Product.objects.filter(category=cat)
        prod= [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides= n//4+ceil((n/4)-(n//4))
        if n!=0:
            allProds.append([prod, range(1,nSlides), nSlides])
    params = {'allProds': allProds, 'msg':''}
    if len(allProds)==0:
        params= {'msg': 'Please enter a Valid product'}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank= False
    if request.method=='POST':
        name= request.POST.get('name', '')
        email= request.POST.get('email', '')
        phone= request.POST.get('phone', '')
        desc= request.POST.get('desc', '')
        contact= Contact(name=name, email=email, phone= phone, desc= desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

def checkout(request):
    if request.method=="POST":
        items_json= request.POST.get('itemsJson', '')
        name=request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email=request.POST.get('email', '')
        address=request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city=request.POST.get('city', '')
        state=request.POST.get('state', '')
        zip_code=request.POST.get('zip_code', '')
        phone=request.POST.get('phone', '')

        order = Orders(items_json= items_json, name=name, email=email, address= address, city=city, state=state, zip_code=zip_code, phone=phone, amount= amount)
        order.save()
        update= OrderUpdate(order_id= order.order_id, update_desc='The Order has been placed')
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})
        # request paytm to send money back
        param_dict= {
            'MID': 'WorldP64425807474247',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
        }
        param_dict['CHECKSUMHASH']= checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/checkout.html')

def productview(request,myid):
    product = Product.objects.filter(id= myid)
    return render(request, 'shop/prodview.html', {'product':product[0]})

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    Verify = checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if Verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
