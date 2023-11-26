from django.contrib import admin
from .models import Car, Client, Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'client', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('car__model', 'client__firstName', 'client__lastName')

admin.site.register(Transaction, TransactionAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstName', 'lastName', 'age', 'gender', 'email', 'phoneNumber')
    search_fields = ('firstName', 'lastName', 'email', 'phoneNumber')

admin.site.register(Client, ClientAdmin)

class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'year', 'price', 'isSold')
    search_fields = ('model', 'year')
    actions = ['make_sold']

    def make_sold(modeladmin, request, queryset):
        queryset.update(isSold=True)
    
    make_sold.short_description = "Mark selected cars as sold"

admin.site.register(Car, CarAdmin)
