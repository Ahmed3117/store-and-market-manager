
from django.db import models
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
import qrcode
from django.core.files import File
from io import BytesIO


class Client(models.Model):
    name = models.CharField(verbose_name = " الاسم",max_length=200,null=True,blank=True)
    national_id = models.CharField(verbose_name = " الرقم القومى",max_length=14 ,null=True,blank=True)
    phone_number = models.CharField(verbose_name = " رقم التليفون ",max_length=20,null=True,blank=True )
    adress = models.CharField(verbose_name = "  العنوان ",max_length=100,null=True,blank=True )
    notes = models.CharField(verbose_name = "  ملاحظات ",max_length=200,null=True,blank=True )
    class Meta:
        verbose_name_plural = ' العملاء'
        verbose_name='  عميل'

    def __str__(self) :
        return self.name

class Category(models.Model):
    name = models.CharField(verbose_name = "التصنيف",max_length=50)
    class Meta:
        verbose_name = "التصنيف"
        verbose_name_plural = "التصنيف"
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(verbose_name="المنتج", max_length=200, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="التصنيف")
    serial = models.CharField(verbose_name="الرقم المسلسل", max_length=14, null=True, blank=True)
    price = models.IntegerField(verbose_name="السعر", null=True, blank=True)
    description = models.TextField(verbose_name="الوصف", max_length=200, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'المنتجات'
        verbose_name = 'منتج'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate the QR code with the product's name
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.serial)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a BytesIO object
        buffer = BytesIO()
        img.save(buffer, format="PNG")

        # Save the QR code image as a FileField
        self.qr_code.save(f'{self.serial}_qrcode.png', File(buffer), save=False)
        
        super().save(*args, **kwargs)

class SellProcess(models.Model):
    pill = models.ForeignKey('Pill', on_delete=models.CASCADE, null=True,blank=True,verbose_name = "الفاتورة") 
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,blank=True,verbose_name = "المنتج") 
    quantity = models.IntegerField(verbose_name = " الكمية",default = 1,null=True,blank=True )
    date_added = models.DateTimeField(verbose_name = " تاريخ البيع",auto_now_add=True,null=True,blank=True) 

    def sellprocessprice(self):
        # sellprocessprice = int(self.product.price) * int(self.quantity)
        if self.product.price and self.quantity :
            return self.product.price * self.quantity
        
            
    
    sellprocessprice.short_description = " السعر"
    
    def save(self, *args, **kwargs):
        super(SellProcess, self).save(*args, **kwargs)
        try:
            available = Available.objects.get(product=self.product)
        except Available.DoesNotExist:
            available = Available.objects.create(product=self.product)
        
        in_sum = Inbound.objects.filter(product=self.product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        out_sum = SellProcess.objects.filter(product=self.product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        available.available_quantity = in_sum - out_sum
        available.save()

    def __str__(self) :
        return self.product.name 

    class Meta:
        verbose_name_plural = ' عمليات بيع'
        verbose_name='  عملية بيع'

class MonthPay(models.Model):
    pill = models.ForeignKey('Pill', on_delete=models.CASCADE, null=True,blank=True,verbose_name = "الفاتورة") 
    monthpaid = models.IntegerField(verbose_name = "القسط",null=True,blank=True)
    date_added = models.DateTimeField(verbose_name = " تاريخ الاضافة",auto_now_add=True,null=True,blank=True) 
    def __str__(self) :
        return str(self.pill.pk)
    class Meta:
        verbose_name_plural = ' الاقساط'
        verbose_name='  دفعة'

class Pill(models.Model):
    
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True,blank=True,verbose_name = "العميل") 
    paid = models.IntegerField(verbose_name = " المقدم",null=True,blank=True,default = 0)
    discount = models.IntegerField(verbose_name = "الخصم",default = 0 ,null=True,blank=True)
    date_added = models.DateTimeField(verbose_name = " تاريخ البيع",auto_now_add=True,null=True,blank=True) 
    deposit_system = models.IntegerField(verbose_name = "نظام التقسيط",default = 0 ,null=True,blank=True)
    
    def pillprice(self):
        sellprocesses = SellProcess.objects.filter(pill = self)
        pill_price = 0
        for process in sellprocesses :
            pill_price += process.sellprocessprice()
        return pill_price

    def charge(self):
        monthpays = MonthPay.objects.filter(pill = self)
        monthpays_price = 0
        for monthpay in monthpays :
            monthpays_price += monthpay.monthpaid
        charge = self.pillprice() - self.paid - monthpays_price - self.discount
        return charge
        
    def deposittotalpaid(self):
        monthpays = MonthPay.objects.filter(pill = self)
        monthpays_price = 0
        for monthpay in monthpays :
            monthpays_price += monthpay.monthpaid
        
        return monthpays_price

    def getpillnum(self):
        pill_num = self.pk
        return pill_num

    getpillnum.short_description = " رقم الفاتورة" 
    pillprice.short_description = " سعر الفاتورة" 
    charge.short_description = " الباقى" 
    deposittotalpaid.short_description = " المدفوع بالتقسيط" 
     
    def __str__(self) :
        try:
            return self.client.name
        except:
            return 'unknown client'

    class Meta:
        verbose_name_plural = '  الفواتير'
        verbose_name='   فاتورة'
        
class ProductSource(models.Model):
    source = models.CharField(max_length=100,null=True,blank=True,verbose_name = " مصدر المنتج")
    class Meta:
        verbose_name_plural = 'مصادر المنتجات'
        verbose_name = 'مصدر'
    def __str__(self):
        return self.source 

class InOutCommon(models.Model): 
    product = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name = " المنتج")
    quantity = models.IntegerField(default=0,verbose_name = " الكمية")
    date_added = models.DateTimeField(default=timezone.now ,verbose_name = " التاريخ")
    file = models.FileField(upload_to='inbound_files/', null=True,blank=True,verbose_name = " ملفات توثيق الورود")
    notes = models.TextField(max_length=1000,null=True,blank=True,verbose_name = " ملاحظات")
    source = models.ForeignKey(ProductSource, on_delete=models.CASCADE, null=True,blank=True,verbose_name = " المصدر")

class Inbound(InOutCommon):
    
    # place = models.ForeignKey(Place, on_delete=models.CASCADE, null=True,blank=True,verbose_name = " مكان التخزين")
    # source = place , product = item
    class Meta:
        verbose_name_plural = 'الوارد'
        verbose_name = 'الوارد'
    def save(self, *args, **kwargs):
        super(Inbound, self).save(*args, **kwargs)
        try:
            available = Available.objects.get(product=self.product)
        except Available.DoesNotExist:
            available = Available.objects.create(product=self.product)
        print(self.product.category)
        print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        available.category = self.product.category
        in_sum = Inbound.objects.filter(product=self.product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        out_sum = SellProcess.objects.filter(product=self.product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        available.available_quantity = in_sum - out_sum
        available.save()
    def product_category(self):
        return self.product.category
    product_category.short_description = 'التصنيف'
    def __str__(self):
        return self.product.name + str(self.quantity)

class Available(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,verbose_name = " التصنيف" , null = True , blank = True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name = " العنصر")
    available_quantity = models.IntegerField(default=0,verbose_name = " الكمية المتاحة")
    # def product_category(self):
    #     return self.product.category
    # product_category.short_description = 'التصنيف'
    class Meta:
        verbose_name_plural = 'كميات العناصر المتاحة'
        verbose_name = 'كمية متاحة'

    def __str__(self):
        return f"{self.product.name} ({self.available_quantity})"
