
from django.shortcuts import render
from .forms import UserInputForm
from azure.storage.blob import BlobServiceClient
import os

from mindee import PredictResponse,client,product,Client
from demodjango import settings
import pandas as pd
import io
from datetime import datetime
#import openpyxl
import json

# Load configuration from the JSON file
with open('D:\shreyash\pythonprojects\GitDjangoAtish\demodjangoatish\demoapp\config.json', 'r') as json_file:
    config = json.load(json_file)

columns = config["columns"]
AZURE_STORAGE_CONNECTION_STRING = config["AZURE_STORAGE_CONNECTION_STRING"]
Mindee_key = config["Mindee_key"]

# columns = ["Sr. No","SURNAME", "GIVEN NAME", "PASSPORT NO.", "SEX", "DATE OF BIRTH",
#                "DATE OF ISSUE", "DATE OF EXPIRY", "PLACE OF ISSUE", "ADDRESS1", "ADDRESS2", "ADDRESS3","STATUS"]
df = pd.DataFrame(columns=columns)

#from mindee.models import PredictResponse   

# Init a new client
mindee_client = Client(api_key=Mindee_key)





# Add the corresponding endpoint (document). Set the account_name to "mindee" if you are using OTS.
my_endpoint = mindee_client.create_endpoint(account_name="mindee", endpoint_name="indian_passport", version="1")

excel_link = None

def read_pdfs(request):
    global df
    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data
            container_name = user_input['container_name']
            directory_name = user_input['directory_name']

            if not container_exists(container_name) or not directory_exists(container_name, directory_name):
                return render(request, 'demoapp/error.html', {'error_message': 'Container or directory does not exist'})

           
            pdf_files = read_pdf_files(container_name, directory_name)
           
            try:
                for pdf_file in pdf_files:
                    file_path = Get_path(container_name, pdf_file)

                    input_doc = mindee_client.source_from_url(file_path)
                    # Parse the file.
                    result: PredictResponse = mindee_client.parse(product.GeneratedV1, input_doc, endpoint=my_endpoint)

                    # Check if passport number already exists in the Excel file
                    passport_number = result.document.inference.prediction.fields.get("id_number", "")
                    new_row_data = {
                        "Sr. No" : len(df) + 1,
                        "SURNAME": result.document.inference.prediction.fields.get("surname", ""),
                        "GIVEN NAME": result.document.inference.prediction.fields.get("given_names", ""),
                        "PASSPORT NO.": passport_number,
                        "SEX": result.document.inference.prediction.fields.get("gender", ""),
                        "DATE OF BIRTH": result.document.inference.prediction.fields.get("birth_date", ""),
                        "DATE OF ISSUE": result.document.inference.prediction.fields.get("issuance_date", ""),
                        "DATE OF EXPIRY": result.document.inference.prediction.fields.get("expiry_date", ""),
                        "PLACE OF ISSUE": result.document.inference.prediction.fields.get("issuance_place", ""),
                        "ADDRESS1": result.document.inference.prediction.fields.get("address1", ""),
                        "ADDRESS2": result.document.inference.prediction.fields.get("address2", ""),
                        "ADDRESS3": result.document.inference.prediction.fields.get("address3", ""),
                        "STATUS": "Active" if is_passport_active(result.document.inference.prediction.fields.get("expiry_date", "")) else "Inactive"
                    }
                    df = pd.concat([df, pd.DataFrame([new_row_data])], ignore_index=True)
                print(df)
                excel_bytes = io.BytesIO()
                df.to_excel(excel_bytes, index=False)
                excel_bytes.seek(0)
                # Generate Excel file name with current date and time
                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                EXCEL_FILE_NAME = f"Passport_{current_datetime}.xlsx"

                return_message = Generate_excel(container_name,directory_name,EXCEL_FILE_NAME,excel_bytes)
                print(excel_link)
                return render(request, 'demoapp/pdf_list.html', {'pdf_files': pdf_files,'return_message': return_message,'excel_link':excel_link})
            except Exception as e:
                print(e)
                return render(request, 'demoapp/error.html', {'error_message': e})
    else:
        form = UserInputForm()

    return render(request, 'demoapp/read_pdfs.html', {'form': form})

def container_exists(container_name):
    service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    return any(container.name == container_name for container in service_client.list_containers())

def directory_exists(container_name, directory_name):
    service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = service_client.get_container_client(container_name)
    return any(blob.name.startswith(directory_name) for blob in container_client.list_blobs())

def read_pdf_files(container_name, directory_name):
    service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = service_client.get_container_client(container_name)

    pdf_files = []
    for blob in container_client.list_blobs(name_starts_with=directory_name):
        if blob.name.lower().endswith('.pdf'):
            pdf_files.append(blob.name)

    return pdf_files

def Get_path(container_name, blob_name):
    service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = service_client.get_container_client(container_name)
    try:
        blob_client = container_client.get_blob_client(blob_name)
        download_path = blob_client.url       

        return download_path
    except Exception as e:
        print(e)
        
def Generate_excel(CONTAINER_NAME,DIRECTORY_NAME,EXCEL_FILE_NAME,excel_bytes):
    message=None
    global excel_link
    try:
        # Initialize BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Create directory within the container if it doesn't exist
        blob_prefix = DIRECTORY_NAME + '/'
        #container_client.upload_blob(blob_prefix, '')

        # Upload the Excel file to the specified directory in Blob Storage
        blob_client = container_client.get_blob_client(blob_prefix + EXCEL_FILE_NAME)
        blob_client.upload_blob(excel_bytes.getvalue(), overwrite=True)
        excel_link=blob_client.url

        message=f"Excel file uploaded to {CONTAINER_NAME}/{DIRECTORY_NAME}/{EXCEL_FILE_NAME}"
        
    except Exception as e:
        message=f"failed to upload excel"

    return message

def is_passport_active(expiry_date):
    # Convert the expiry date to a string
    expiry_date_str = str(expiry_date)

    # Convert the expiry date string to a datetime object
    expiry_datetime = datetime.strptime(expiry_date_str, "%Y-%m-%d")
    
    # Compare with the current date
    return expiry_datetime > datetime.now()