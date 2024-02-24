# from django.shortcuts import render,redirect
# from django.urls import reverse
# from .models import Branch, Holiday, Level, Person, Unit
# # import openpyxl



# import itertools
# def addpersonsbyexcel(request):
#     if request.method == "POST":
#         excel_file = request.FILES["excelfile"]
#         wb = openpyxl.load_workbook(excel_file)
#         worksheet = wb["Sheet1"]
#         data_rows = itertools.islice(worksheet.iter_rows(), 1, None)

#         level_dict = {level.id: level for level in Level.objects.all()}
#         unit_dict = {unit.id: unit for unit in Unit.objects.all()}
#         branch_dict = {branch.id: branch for branch in Branch.objects.all()}

#         for row in data_rows:
#             name = row[0].value
#             national_id = row[1].value
#             military_number = row[2].value
#             level_id = row[3].value
#             mainunit_id = row[4].value
#             branch_id = row[5].value
#             if name and military_number:
#                 level = level_dict.get(level_id) or Level.objects.first()
#                 mainunit = unit_dict.get(mainunit_id) or Unit.objects.first()
#                 branch = branch_dict.get(branch_id) or Branch.objects.first()
#                 person, created = Person.objects.get_or_create(
#                     military_number=military_number,
#                     defaults={
#                         "name": name,
#                         "national_id": national_id,
#                         "level": level,
#                         "mainunit": mainunit,
#                         "branch": branch,
#                     }
#                 )
#                 if not created:
#                     person.name = name
#                     person.national_id = national_id
#                     person.level = level
#                     person.mainunit = mainunit
#                     person.branch = branch
#                     person.save()

#     return redirect(reverse("admin:maindata_person_changelist"))


from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import Pill,MonthPay,SellProcess,Available,Category,Product
import json
import qrcode
from io import BytesIO

def addmonth(request, pk):
    if request.method == 'POST':

        data = json.loads(request.body)
        print(data)
        pill_id = data.get('pill_id')
        monthpaid = data.get('monthpaid')
        
        pill = Pill.objects.get(id=pill_id)
        MonthPay.objects.create(pill=pill, monthpaid=monthpaid)
        return redirect(request.path)
    return redirect(request.path)




def invoice(request, pk):
    pill = Pill.objects.get(id=pk)
    paid_monthes = MonthPay.objects.filter(pill = pill)
    sellprocesses = SellProcess.objects.filter(pill = pill)
    supposed_paid_month = 0 # الشهرية المفترض دفعها
    if pill.deposit_system != 0 :
        supposed_paid_month = (pill.pillprice() - pill.paid)/pill.deposit_system
    context = {
        'pill':pill,
        'paid_monthes':paid_monthes,
        'sellprocesses':sellprocesses,
        'supposed_paid_month':supposed_paid_month,
        }
    return render(request,'maindata/invoice.html' ,context)

def releaseqrcodegenerator(request):
    return render(request,'maindata/releaseqrcodegenerator.html')


def generateqrcode(request):
    data = request.POST.get('data')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="#ffffff")

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Create an HttpResponse with the image content
    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Content-Disposition"] = 'attachment; filename="qrcode.png"'

    return response



def showproductqrcodepage(request):
    return render(request,'maindata/qrcode_products.html')

def calculate_total_price(request):
    if request.method == 'POST':

        products_json = request.POST.get('products')
        products_serial_list = json.loads(products_json)
        
        print(products_serial_list)
        total_price = 0
        for serial in products_serial_list :
            pro_serial = 'serial' + str(serial)
            product_serial = request.POST.get(pro_serial)
            pro_quantity = 'quantity' + str(serial)
            product_quantity = request.POST.get(pro_quantity)
            print("lllllllllllllllllllllllllllllllllllllllllllllllllllll")
            print(product_quantity)
            product = Product.objects.get(serial = product_serial)
            total_price += product.price * int(product_quantity)
            
        # Return the total price as a JSON response
        response_data = {'total_price': total_price}
        return JsonResponse(response_data)

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def receiveqrcodeproductdata(request):
    if request.method == 'POST':
        # Handle form data here
        data = request.POST
        # the printed data : 
        # <QueryDict: {'csrfmiddlewaretoken': ['WSHhXUob4ZG31e1XAdNp2h1EmbzoRcPxYBw7BISzw11bsMoRUgKi34u7GyBMkIZZ'],
        #              'serial333333': ['333333'], 'quantity333333': ['1'], 
        #              'pillcheck': ['on'], 'products': ['["333333"]']}>
        # print("kkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        print(data)
        products_json = request.POST.get('products')
        products_serial_list = json.loads(products_json)
        pill = None
        print(data.get('pillcheck'))
        if data.get('pillcheck') == 'on':
            pill = Pill.objects.create()
            pill.save()
            print(pill)
            print("gggggggggggggggggggggggggggggggggggggggg")
            admin_url = reverse("admin:maindata_pill_change", args=[pill.id])
            # client_name = request.POST.get(client_name)
            # national_id = request.POST.get(national_id)
            # phone_number = request.POST.get(phone_number)
            # adress = request.POST.get(adress)
        
           
        for serial in products_serial_list :
            pro_serial = 'serial' + str(serial)
            product_serial = request.POST.get(pro_serial)
            pro_quantity = 'quantity' + str(serial)
            product_quantity = request.POST.get(pro_quantity)
            try:
                product = Product.objects.get(serial = product_serial)
                sellprocess = SellProcess.objects.create(product = product , quantity = product_quantity)
                if pill is not None :
                    sellprocess.pill = pill
                sellprocess.save()    
            except:
                return JsonResponse({'error': 'this product is not exist'}, status=400)
        if pill is not None:
            response_data = {'message': 'Form data processed successfully', 'admin_url': admin_url}
        else:
            response_data = {'message': 'Form data processed successfully'}

        return JsonResponse(response_data)
        
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def report(request):
    # get available products
    available_data = Available.objects.all()
    # # get categories
    # categories = Category.objects.all()

    # data = {
    #     "categories" : {

    #     }
    # }
    # for category in categories :
    #     data["categories"][category] = [product for product in category.product_set.all()]
    # print(data)

    pill_data = {
        
    }
    context = {    
        # "categories" : categories,
        "available_data" : available_data,
    }
    return render(request,'maindata/report.html',context)

from django.db.models import Q
def printqrcodes(request):
    # Retrieve query parameters
    category_filter = request.GET.get('category')
    categorynull = request.GET.get('category__isnull')
    search_filter = request.GET.get('search')
    q_filter = request.GET.get('q')

    # Construct the queryset based on the filters
    products = Product.objects.all()

    
    if categorynull == 'True':
        # Handle the case where category__isnull=True
        products = products.filter(category__isnull=True)
    if category_filter:
        # Filter by category ID
        products = products.filter(category__id=category_filter)

    if search_filter:
        # Search across name, category, and serial using OR operator
        products = products.filter(
            Q(name__icontains=search_filter) |
            Q(category__name__icontains=search_filter) |
            Q(serial__icontains=search_filter)
        )

    if q_filter:
        # Include additional filtering based on the 'q' parameter, if needed
        products = products.filter(serial__icontains=q_filter)

    context = {
        'products': products,
    }
    
    return render(request,'maindata/printqrcodes.html',context)








###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################
from .forms import QRCodeForm


def qr_code_reader(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['data']
            print(data)
            
            
    else:
        form = QRCodeForm()

    return render(request, 'maindata/qr_code_reader.html', {'form': form})


###########################################################################
###########################################################################
###########################################################################
###########################################################################
###########################################################################




