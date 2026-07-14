from django.urls import path
from .views import *

app_name = 'properties'

urlpatterns = [
    path('', index_page, name='index'),
    path('catalog/', catalog_view, name='catalog'),
    path('catalog/<slug:slug>/', property_detail_view, name='detail'),
]