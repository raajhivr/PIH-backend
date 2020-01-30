from django.urls import path

from . import views

urlpatterns = [
    path('products', views.all_products, name='all_products'),
    path('selectedProducts',views.selected_products, name='selected_products')
]