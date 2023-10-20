from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'cars', views.CarViewSet, basename='car')
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'manager-cars', views.ManagerCarViewSet, basename='manager-car')
router.register(r'accountant-summary', views.AccountantViewSet, basename='accountant-summary')

urlpatterns = [
    path('', views.home, name='home'),
    path('', include(router.urls)),
]
