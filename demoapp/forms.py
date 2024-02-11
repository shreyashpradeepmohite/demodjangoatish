# from django import forms
# from .models import UserInput #,UploadedFile, PDFFile

# # class UploadFileForm(forms.ModelForm):
# #     class Meta:
# #         model = UploadedFile
# #         fields = ['pdf_file', 'text_content']
        
# # class PDFUploadForm(forms.ModelForm):
# #     class Meta:
# #         model = PDFFile
# #         fields = ['title', 'pdf_file']

# class UserInputForm(forms.ModelForm):
#     class Meta:
#         model = UserInput
#         fields = ['Container_Name', 'Directory_Name']

# mydriveapp/forms.py

# mydriveapp/forms.py
from django import forms
from .models import UserInput

class UserInputForm(forms.ModelForm):
    class Meta:
        model = UserInput
        fields = ['container_name', 'directory_name']

