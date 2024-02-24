

from django.contrib import admin
from .models import SellProcess,Pill,MonthPay,Product,Client,Category,ProductSource,Inbound,Available
from django.urls import reverse
from django.utils.html import format_html
from django.template.context_processors import csrf
from django.utils.translation import gettext_lazy as _
from rangefilter.filter import DateRangeFilter
# from django.db.models import Q

# from django.db.models import When, Value, BooleanField

# annotated_objects = MyModel.objects.annotate(
#     active_status=Case(
#         When(is_active=True, then=Value(True)),
#         default=Value(False),
#         output_field=BooleanField(),
#     )
# )

# كشف المديونيات    
# class depitFilter(admin.SimpleListFilter):
    # title = _('كشف المديونيات')
    # parameter_name = 'FinishedORNot'

    # def lookups(self, request, model_admin):
    #     return (
    #         ('depit', _('المديونين')),
    #         ('notdepit', _('الغير مديونين')),
    #     )

#     def queryset(self, request, queryset):

#         if self.value() == 'depit':
#             print(queryset)
#             print("qqqqqqqqqqqqqqqqqqqqqqq")
#             q = list(queryset)
#             count=0
#             for pill in queryset : 
#                 count+=1
#                 if pill.charge != 0 :
#                     print(count)
#                     q.pop(1)

#             return queryset
#         elif self.value() == 'notdepit':
#             queryset = Puill.objects.filter(Q(charge = 0))
#             return queryset
#         else:
#             return queryset
from django.db.models import F, ExpressionWrapper, IntegerField ,OuterRef, Subquery
    
class UnpaidPillsFilter(admin.SimpleListFilter):
    title = _('كشف المديونيات')
    parameter_name = 'FinishedORNot'

    def lookups(self, request, model_admin):
        return (
            ('depit', _('المديونين')),
            ('notdepit', _('الغير مديونين')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'depit':
            unpaid_pill_ids = [pill.id for pill in queryset if pill.charge() > 0]
            return queryset.filter(id__in=unpaid_pill_ids)
        if self.value() == 'notdepit':
            paid_pill_ids = [pill.id for pill in queryset if pill.charge() <= 0]
            return queryset.filter(id__in=paid_pill_ids)
         


class QuantityRangeFilter(admin.SimpleListFilter):
    title = 'كمية ما بين'
    parameter_name = 'quantity_range'

    def lookups(self, request, model_admin):
        # Define the lookup choices for the filter
        return (
            ('0-100', '0 - 100'),
            ('101-200', '101 - 200'),
            ('201-500', '201 - 500'),
            ('501+', '501 او اكثر'),
        )

    def queryset(self, request, queryset):
        # Apply the filter to the queryset
        if self.value():
            range_start, range_end = self.value().split('-')
            if range_end == '+':
                try:
                    queryset = queryset.filter(quantity__gte=int(range_start))
                except:
                    queryset = queryset.filter(available_quantity__gte=int(range_start))
            else:
                try:
                    queryset = queryset.filter(quantity__range=(int(range_start), int(range_end)))
                except:
                    queryset = queryset.filter(available_quantity__range=(int(range_start), int(range_end)))

        return queryset

admin.site.register(Category)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('category','name','serial','price','qr_code','qr_code_download_link')
    search_fields = ('category__name','name','serial')
    list_filter = ('category',)
    ordering = ('category','serial','name')
    list_per_page = 10
    list_editable = ('name','serial','price')
    def qr_code_download_link(self, obj):
        if obj.qr_code:
            return format_html('<a class="button rounded " href="{}" download> تحميل</a>', obj.qr_code.url)

        else:
            return "لا يوجد"

    qr_code_download_link.short_description = 'تحميل'
    
admin.site.register(Product,ProductAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name','national_id','phone_number','adress','notes')
    search_fields = ('name','national_id','phone_number')
    ordering = ('name','national_id')
    list_per_page = 10
    list_editable = ('national_id','phone_number','adress','notes')
    # list_display_links
admin.site.register(Client,ClientAdmin)



class ProductSourceAdmin(admin.ModelAdmin):
    list_display = ('source',)
    list_filter = ('source',)
    search_fields = ('source',)
    ordering = ('source',)
    list_per_page = 10


admin.site.register(ProductSource, ProductSourceAdmin)


class SellProcessAdmin(admin.StackedInline):
    model = SellProcess

class MonthPayAdmin(admin.StackedInline):
    model = MonthPay



from django.template.loader import render_to_string
from django.utils.html import format_html
from django.middleware.csrf import get_token

class PillAdmin(admin.ModelAdmin):
    autocomplete_fields = ['client']
    # raw_id_fields = ('client',)
    list_display = ('client','getpillnum','pillprice','paid','deposittotalpaid','discount','charge','addmonthbutton','monthdetails','printpill')
    search_fields = ('pk','client__name')
    ordering = ('pk','client')
    # list_filter = ('date_added',UnpaidPillsFilter)
    list_filter = (
        ('date_added', DateRangeFilter),  # Add DateRangeFilter for the 'created_at' field
        'date_added',
        UnpaidPillsFilter
    )
    list_per_page = 10 
    list_editable = ('paid',)
    change_list_template = 'admin/maindata/Pill/change_list.html'

    inlines = [SellProcessAdmin]
    
    def monthdetails(self, obj):
        pill_id = obj.id
        url = reverse('admin:maindata_monthpay_changelist')
        url += f'?pill_id={pill_id}'
        return format_html('<a class="button rounded " href="{}">تفاصيل التقسيط</a>', url)
   
    def printpill(self, obj):
        pill_id = obj.id
        url = reverse('maindata:invoice', args=[pill_id])

        return format_html('<a class="button rounded " href="{}">الفاتورة </a>', url)
    
    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context=extra_context)
    
    def addmonthbutton(self, obj):
        pill_id = obj.id
        url = reverse('maindata:addmonth', args=[pill_id])
        csrf_token = get_token(self.request)

        modal_html = render_to_string('admin/maindata/Pill/addmonth.html', {
            'pill_id': pill_id,
            'url': url,
            'csrf_token': csrf_token,
        })

        return format_html(modal_html)
    monthdetails.short_description = 'تفاصيل التقسيط'
    addmonthbutton.short_description = 'اضف شهرية'
    printpill.short_description = 'طباعة فاتورة'
    class Meta:
        model = Pill

admin.site.register(Pill,PillAdmin)

@admin.register(SellProcess)
class SellProcessAdmin(admin.ModelAdmin):
    list_display = ('product','quantity','sellprocessprice')
    search_fields = ('product__name',)
    
    list_per_page = 10 
    list_editable = ('quantity',)
    

# admin.site.unregister(SellProcess)

@admin.register(MonthPay)
class MonthPayAdmin(admin.ModelAdmin):
    list_display = ('pill','monthpaid','date_added')
    search_fields = ('pill',)
    list_filter = ('date_added',)
    list_per_page = 10 
    list_editable = ('monthpaid',)


@admin.register(Inbound)
class InboundAdmin(admin.ModelAdmin):
    list_display = ('product','product_category','source', 'quantity', 'date_added','file')
    list_filter = ('product__category','product','source__source', 'date_added', QuantityRangeFilter)
    # change_list_template = 'admin/change_list.html'
    search_fields = ('product__category__name','product__name','notes')
    ordering = ('product','source', 'quantity', 'date_added')
    list_per_page = 10
    list_editable = ()
    # change_list_template = 'admin/zakah/Inbound/change_list.html'
    def DisableEditFields(self, request, queryset):
        self.list_editable = ()
    def EnableEditFields(self, request, queryset):
        self.list_editable = ('source', 'quantity', 'date_added','file')

    DisableEditFields.short_description = "الغاء التعديل"  
    EnableEditFields.short_description = " تعديل"  
    actions = ['EnableEditFields','DisableEditFields']
# @admin.register(Outbound)
# class OutbounddAdmin(admin.ModelAdmin):
#     list_display = ('product','product_category','source','quantity', 'date_added','file')
#     list_filter = ('product__category','product','source__source', 'quantity', 'date_added', QuantityRangeFilter)
#     # change_list_template = 'admin/change_list.html'
#     search_fields = ('product__category__name','product__name')
#     ordering = ('product','source','quantity', 'date_added')
#     list_per_page = 10
#     list_editable = ()
#     def DisableEditFields(self, request, queryset):
#         self.list_editable = ()
#     def EnableEditFields(self, request, queryset):
#         self.list_editable = ('source','quantity', 'date_added','file')

#     DisableEditFields.short_description = "الغاء التعديل"  
#     EnableEditFields.short_description = " تعديل"  
#     actions = ['EnableEditFields','DisableEditFields']

@admin.register(Available)
class AvailabledAdmin(admin.ModelAdmin):
    list_display = ('product','category', 'available_quantity')
    list_filter = ('product__name','category' , QuantityRangeFilter)
    # change_list_template = 'admin/change_list.html'
    search_fields = ('product__name','product__category__name')
    ordering = ('product', 'available_quantity')
    list_per_page = 10
    # change_list_template = 'admin/zakah/Inbound/change_list.html'
  
