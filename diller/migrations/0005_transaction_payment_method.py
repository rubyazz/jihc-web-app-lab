# Generated by Django 3.2.20 on 2023-11-28 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diller', '0004_transaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_method',
            field=models.CharField(choices=[('credit', 'Credit'), ('cash', 'Cash')], default='cash', max_length=10),
        ),
    ]
