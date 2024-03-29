# Generated by Django 4.2 on 2023-08-23 14:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='التصنيف')),
            ],
            options={
                'verbose_name': 'التصنيف',
                'verbose_name_plural': 'التصنيف',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name=' الاسم')),
                ('national_id', models.CharField(blank=True, max_length=14, null=True, verbose_name=' الرقم القومى')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name=' رقم التليفون ')),
                ('adress', models.CharField(blank=True, max_length=100, null=True, verbose_name='  العنوان ')),
                ('notes', models.CharField(blank=True, max_length=200, null=True, verbose_name='  ملاحظات ')),
            ],
            options={
                'verbose_name': '  عميل',
                'verbose_name_plural': ' العملاء',
            },
        ),
        migrations.CreateModel(
            name='InOutCommon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0, verbose_name=' الكمية')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, verbose_name=' التاريخ')),
                ('file', models.FileField(blank=True, null=True, upload_to='inbound_files/', verbose_name=' ملفات توثيق الورود')),
                ('notes', models.TextField(blank=True, max_length=1000, null=True, verbose_name=' ملاحظات')),
            ],
        ),
        migrations.CreateModel(
            name='Pill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid', models.IntegerField(blank=True, default=0, null=True, verbose_name=' المقدم')),
                ('discount', models.IntegerField(blank=True, default=0, null=True, verbose_name='الخصم')),
                ('date_added', models.DateTimeField(auto_now_add=True, null=True, verbose_name=' تاريخ البيع')),
                ('deposit_system', models.IntegerField(blank=True, default=0, null=True, verbose_name='نظام التقسيط')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='maindata.client', verbose_name='العميل')),
            ],
            options={
                'verbose_name': '   فاتورة',
                'verbose_name_plural': '  الفواتير',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name=' الاسم')),
                ('serial', models.CharField(blank=True, max_length=14, null=True, verbose_name=' الرقم المسلسل')),
                ('price', models.IntegerField(blank=True, null=True, verbose_name=' السعر')),
                ('discription', models.TextField(blank=True, max_length=200, null=True, verbose_name='  الوصف ')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maindata.category', verbose_name='التصنيف')),
            ],
            options={
                'verbose_name': '  منتج',
                'verbose_name_plural': ' المنتجات',
            },
        ),
        migrations.CreateModel(
            name='ProductSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(blank=True, max_length=100, null=True, verbose_name=' مصدر المنتج')),
            ],
            options={
                'verbose_name': 'مصدر',
                'verbose_name_plural': 'مصادر المنتجات',
            },
        ),
        migrations.CreateModel(
            name='Inbound',
            fields=[
                ('inoutcommon_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='maindata.inoutcommon')),
            ],
            options={
                'verbose_name': 'الوارد',
                'verbose_name_plural': 'الوارد',
            },
            bases=('maindata.inoutcommon',),
        ),
        migrations.CreateModel(
            name='SellProcess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, default=1, null=True, verbose_name=' الكمية')),
                ('pill', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maindata.pill', verbose_name='الفاتورة')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='maindata.product', verbose_name='المنتج')),
            ],
            options={
                'verbose_name': '  عنصر',
                'verbose_name_plural': ' محتوي الفاتورة',
            },
        ),
        migrations.CreateModel(
            name='MonthPay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthpaid', models.IntegerField(blank=True, null=True, verbose_name='القسط')),
                ('date_added', models.DateTimeField(auto_now_add=True, null=True, verbose_name=' تاريخ الاضافة')),
                ('pill', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maindata.pill', verbose_name='الفاتورة')),
            ],
            options={
                'verbose_name': '  دفعة',
                'verbose_name_plural': ' الاقساط',
            },
        ),
        migrations.AddField(
            model_name='inoutcommon',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maindata.product', verbose_name=' المنتج'),
        ),
        migrations.AddField(
            model_name='inoutcommon',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maindata.productsource', verbose_name=' المصدر'),
        ),
        migrations.CreateModel(
            name='Available',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available_quantity', models.IntegerField(default=0, verbose_name=' الكمية المتاحة')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maindata.product', verbose_name=' العنصر')),
            ],
            options={
                'verbose_name': 'كمية متاحة',
                'verbose_name_plural': 'كميات العناصر المتاحة',
            },
        ),
    ]
