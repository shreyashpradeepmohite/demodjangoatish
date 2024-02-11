# from pathlib import Path
# from unicodedata import name
# from django.contrib import admin
# from django.urls import path,include
# from demoapp import views
# from .views import upload_file, success

# urlpatterns = [
#     path("", views.index,name="index"),
#     path('upload/', upload_file, name='upload_file'),
#     path('upload/success/', success, name='upload_success'),
# ]

# mydriveapp/urls.py
from django.urls import path
from .views import read_pdfs

urlpatterns = [
    path('read_pdfs/', read_pdfs, name='read_pdfs'),
    # Add any other URLs as needed
]
