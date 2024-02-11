# from django.db import models

# class UploadedFile(models.Model):
#     pdf_file = models.FileField(upload_to='pdf_files/')
#     text_content = models.TextField()

# class PDFFile(models.Model):
#     title = models.CharField(max_length=255)
#     pdf_file = models.FileField(upload_to='pdf_files/')
    
# class UserInput(models.Model):
    
#     # email = models.EmailField()
#     # password = models.CharField(max_length=255)
#     Container_Name = models.CharField(max_length=1000)    
#     Directory_Name = models.CharField(max_length=1000)

# mydriveapp/models.py
# mydriveapp/models.py
from django.db import models

class UserInput(models.Model):   
    container_name = models.CharField(max_length=255)
    directory_name = models.CharField(max_length=255)
