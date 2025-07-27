from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Receipt, WalletPass, UserQuery
from .serializers import ReceiptSerializer, WalletPassSerializer, UserQuerySerializer
from django.conf import settings
from google.cloud import storage, firestore
import os
import requests
import json
import google.generativeai as genai
from google.generativeai import types
import base64
from django.contrib.auth.models import User

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from .firebase_init import db

from google.auth import crypt
from google.auth import jwt
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Tool, Part, FunctionDeclaration
import matplotlib
matplotlib.use('Agg') # Use a non-interactive backend for servers
import matplotlib.pyplot as plt
import io


try:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-south1")
    vertexai.init(project=project_id, location=location)
except Exception as e:
    print(f"Vertex AI initialization failed: {e}")


# import base64

# class ReceiptViewSet(viewsets.ModelViewSet):
    # queryset = Receipt.objects.all()
    # serializer_class = ReceiptSerializer

    # @action(detail=False, methods=['post'])
    # def upload(self, request):
    #     file = request.FILES.get('file')
    #     if not file:
    #         return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

    #     # Upload to Google Cloud Storage
    #     bucket_name = os.getenv('GCS_BUCKET_NAME') or getattr(settings, 'GCS_BUCKET_NAME', None)
    #     if not bucket_name:
    #         return Response({'error': 'GCS_BUCKET_NAME not set in .env.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     storage_client = storage.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    #     bucket = storage_client.bucket(bucket_name)
    #     blob = bucket.blob(file.name)
    #     blob.upload_from_file(file, content_type=file.content_type)
        
    #     file_url = blob.public_url
    #     print(file_url)  # Debugging line to check the file URL


    #     print('hello')

    #     # Trigger Gemini for receipt analysis
    #     api_key = os.getenv('GEMINI_API_KEY')
    #     print(api_key)  # Debugging line to check the API ke

    #     # Replace with your actual API key
    #     # genai.configure(api_key="YOUR_API_KEY")

    #     # Assuming blob_public_url is available from your blob storage

    #     # model = genai.GenerativeModel('gemini-pro-vision') # Or 'gemini-1.5-flash', 'gemini-1.5-pro' for more advanced capabilities

    #     # prompt_text = """
    #     # Extract the following information from this receipt and return it as a JSON object.
    #     # If a field is not found, use null or 0.0 for numerical values.

    #     # {
    #     # "vendor_name": "string",
    #     # "date": "YYYY-MM-DD",
    #     # "total_amount": "float",
    #     # "subtotal": "float",
    #     # "tax_amount": "float",
    #     # "other_fees": "float",
    #     # "items": [
    #     #     {
    #     #     "item_name": "string",
    #     #     "quantity": "integer",
    #     #     "unit_price": "float",
    #     #     "line_total": "float"
    #     #     }
    #     # ]
    #     # }
    #     # """

    #     # try:
    #     #     image_part = types.Part.from_uri(file_uri=file_url, mime_type="image/jpeg") # Adjust mime_type if needed
    #     #     response = model.generate_content([prompt_text, image_part])

    #     #     # Attempt to parse the text response as JSON
    #     #     extracted_data = json.loads(response.text)
    #     #     print(json.dumps(extracted_data, indent=2))

    #     # except Exception as e:
    #     #     print(f"Error processing image: {e}")



    #     # Analyze the uploaded image using Gemini Vision (base64 inline_data)
    #     import base64
    #     gemini_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key=' + api_key
    #     # Read the file again for base64 encoding (file pointer is at end after upload)
    #     file.seek(0)
    #     file_bytes = file.read()
    #     file_b64 = base64.b64encode(file_bytes).decode('utf-8')
    #     payload = {
    #         "contents": [{
    #             "parts": [
    #                 {"text": "Extract all receipt data as JSON (items, prices, taxes, total, date, merchant, etc)."},
    #                 {"inline_data": {"mime_type": file.content_type, "data": file_b64}}
    #             ]
    #         }]
    #     }

    #     gemini_response = requests.post(gemini_url, json=payload)
    #     print("Gemini response status:", gemini_response.status_code)
    #     print("Gemini response content:", gemini_response.text)
    #     gemini_data = gemini_response.json()
    #     extracted_json = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

    #     print(extracted_json)

    #     #Save to Firestore
    #     firestore_client = firestore.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    #     doc_ref = firestore_client.collection('receipts').document()
    #     doc_ref.set({
    #         'user_id': str(request.user.id),
    #         'image_url': file_url,
    #         'extracted_data': extracted_json
    #     })

    #     # Save to Receipt model
    #     receipt = Receipt.objects.create(user=request.user, image_url=file_url, data_json=extracted_json)
    #     return Response({'message': 'File uploaded and analyzed.', 'file_url': file_url, 'receipt_id': receipt.id, 'extracted_data': extracted_json}, status=status.HTTP_201_CREATED)


# class ReceiptViewSet(viewsets.ModelViewSet):
#     queryset = Receipt.objects.all()
#     serializer_class = ReceiptSerializer

#     @action(detail=False, methods=['post'])
#     def upload(self, request):
#         file = request.FILES.get('file')
#         if not file:
#             return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Upload to Google Cloud Storage
#         bucket_name = os.getenv('GCS_BUCKET_NAME') or getattr(settings, 'GCS_BUCKET_NAME', None)
#         if not bucket_name:
#             return Response({'error': 'GCS_BUCKET_NAME not set in .env.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         storage_client = storage.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
#         bucket = storage_client.bucket(bucket_name)
#         blob = bucket.blob(file.name)
#         blob.upload_from_file(file, content_type=file.content_type)

#         file_url = blob.public_url
#         print(f"File uploaded to GCS: {file_url}")

#         # Analyze the uploaded image using Gemini Vision (base64 inline_data)
#         api_key = os.getenv('GEMINI_API_KEY')
#         if not api_key:
#             return Response({'error': 'GEMINI_API_KEY not set in .env.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         gemini_model = 'gemini-1.5-flash'  # Use a current model
#         gemini_url = f'https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}'

#         file.seek(0)  # Reset file pointer
#         file_bytes = file.read()
#         file_b64 = base64.b64encode(file_bytes).decode('utf-8')
        
#         extraction_prompt = """
#         Analyze the receipt image and extract its data into a valid JSON object.
#         Use the following schema. Do not add any extra text or markdown formatting like ```json.
#         If a value is not present, use null. For dates, use YYYY-MM-DD format if possible.

#         {
#           "merchant_name": "string",
#           "transaction_date": "string",
#           "total_amount": float,
#           "items": [
#             {
#               "name": "string",
#               "quantity": integer,
#               "price": float
#             }
#           ]
#         }
#         """

#         payload = {
#             "contents": [{
#                 "parts": [
#                     {"text": extraction_prompt},
#                     {"inline_data": {"mime_type": file.content_type, "data": file_b64}}
#                 ]
#             }]
#         }

#         try:
#             gemini_response = requests.post(gemini_url, json=payload)
#             gemini_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#             print(f"Gemini response status: {gemini_response.status_code}")
#             print(f"Gemini response content: {gemini_response.text}")
#             gemini_data = gemini_response.json()
#             extracted_json = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
#             print(f"Extracted JSON: {extracted_json}")

#         except requests.exceptions.RequestException as e:
#             print(f"Gemini API error: {e}")
#             extracted_json = None  # Set to None in case of error
#             return Response({'error': f"Gemini API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # --- Save to Django Model (Replaces Firestore) ---
#             receipt = Receipt.objects.create(
#                 user=request.user, 
#                 image_url=file_url, 
#                 data_json=extracted_data # Assumes 'data_json' is a JSONField in your Receipt model
#             )
            
#             return Response({
#                 'message': 'File uploaded and data extracted successfully.',
#                 'receipt_id': receipt.id,
#                 'extracted_data': extracted_data
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             print(f"An error occurred during upload/extraction: {e}")
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
#         # # Save to Firestore
#         # try:
#         #     # Use a service account

#         #     # Get base path of current file
#         #     # BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#         #     # # Construct the relative path to service account JSON
#         #     # SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, '..', 'credentials', 'service-account.json')

#         #     # # Load credentials
#         #     # cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
#         #     # # cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
#         #     # firebase_admin.initialize_app(cred, options={
#         #     #     'projectId': 'project-raseed-466711',
#         #     #     'databaseId': 'raseed-database-backend'  # Specify your database ID here
#         #     # })

#         #     # db = firestore.client()

#         #     doc_ref = db.collection("receipts").document()  # Let Firestore generate the ID

#         #     doc_ref.set({
#         #         "image_url": file_url,
#         #         "extracted_data": extracted_json
#         #     })
#         #     print(f"Data saved to Firestore with document ID: {doc_ref.id}")
#         #     return Response({'message': 'File uploaded and analyzed.', 'file_url': file_url, 'extracted_data': extracted_json}, status=status.HTTP_201_CREATED)

#         # except Exception as e:
#         #     print(f"Firestore error: {e}")
#         #     return Response({'error': f"Firestore error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

#         # # Save to Receipt model (if you still need this)
#         # # receipt = Receipt.objects.create(user=request.user, image_url=file_url, data_json=extracted_json)

#         # return Response({
#         #     'message': 'File uploaded and analyzed.',
#         #     'file_url': file_url,
#         #     #'receipt_id': receipt.id,  # Remove if not saving to Receipt model
#         #     'extracted_data': extracted_json
#         # }, status=status.HTTP_201_CREATED)




class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- Upload to Google Cloud Storage ---
            bucket_name = os.getenv('GCS_BUCKET_NAME')
            if not bucket_name:
                return Response({'error': 'GCS_BUCKET_NAME not set in .env.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            storage_client = storage.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(f"{request.user.id}/{file.name}") # User-specific folder
            blob.upload_from_file(file, content_type=file.content_type)
            file_url = blob.public_url
            print(f"File uploaded to GCS: {file_url}")

            # --- Analyze with Gemini ---
            api_key = os.getenv('GEMINI_API_KEY')
            gemini_model = 'gemini-1.5-flash'
            gemini_url = f'https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}'

            file.seek(0)
            file_b64 = base64.b64encode(file.read()).decode('utf-8')
            
            extraction_prompt = """
            Analyze the receipt image and extract its data into a valid JSON object.
            Use the following schema. Do not add any extra text or markdown formatting like ```json.
            If a value is not present, use null. For dates, use YYYY-MM-DD format if possible.

            {
              "merchant_name": "string",
              "transaction_date": "string",
              "total_amount": float,
              "items": [
                {
                  "name": "string",
                  "quantity": int,
                  "price": float
                }
              ]
            }
            """

            payload = {"contents": [{"parts": [{"text": extraction_prompt}, {"inline_data": {"mime_type": file.content_type, "data": file_b64}}]}]}

            gemini_response = requests.post(gemini_url, json=payload)
            gemini_response.raise_for_status()
            
            gemini_data = gemini_response.json()
            json_text = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
            
            # Clean the response and parse to JSON
            if json_text.strip().startswith("```json"):
                json_text = json_text.strip()[7:-3]
            
            extracted_data = json.loads(json_text)
            print(f"Extracted JSON: {extracted_data}")

            # --- Save to Django's SQLite Database ---
            default_user, created = User.objects.get_or_create(username='defaultuser')
            if created:
                default_user.set_password('password') # Set a default password
                default_user.save()

            
            receipt = Receipt.objects.create(
                user=default_user, 
                image_url=file_url, 
                data_json=extracted_data # Save the parsed JSON object
            )
            
            return Response({
                'message': 'File uploaded and data extracted successfully.',
                'receipt_id': receipt.id,
                'extracted_data': extracted_data
            }, status=status.HTTP_201_CREATED)

        except requests.exceptions.RequestException as e:
            print(f"Gemini API error: {e}")
            return Response({'error': f"Gemini API error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"An error occurred during upload/extraction: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ==============================================================================
#  AGENT TOOLS DEFINITION
#  These are the functions our Vertex AI Agent can use.
# ==============================================================================
def get_purchase_history() -> str:
    """
    Gets the default user's 10 most recent purchase receipts from the database to provide context for answering questions.
    
    Returns:
        A JSON string of the user's purchase history.
    """
    default_user, _ = User.objects.get_or_create(username='defaultuser')
    user_receipts = Receipt.objects.filter(user=default_user).order_by('-created_at')[:10]
    if not user_receipts.exists():
        return "The user has no purchase history."
    
    purchase_history = [receipt.data_json for receipt in user_receipts]
    return json.dumps(purchase_history)


def create_shopping_list_pass(items: list[str]) -> str:
    """
    Creates a Google Wallet pass with a shopping list for the default user.
    
    Args:
        items: A list of strings representing the items for the shopping list.
    Returns:
        A JSON string confirming the pass creation and containing pass details.
    """
    try:
        default_user, _ = User.objects.get_or_create(username='defaultuser')
        wallet_view = WalletPassViewSet()
        pass_data = wallet_view._create_pass_jwt(default_user, 'shopping_list', {'shopping_list': items})
        return json.dumps(pass_data)
    except Exception as e:
        return json.dumps({"error": str(e)})
# ==============================================================================




# class WalletPassViewSet(viewsets.ModelViewSet):
#     queryset = WalletPass.objects.all()
#     serializer_class = WalletPassSerializer

#     @action(detail=False, methods=['post'])
#     def create_pass(self, request):
#         user = request.user
#         pass_type = request.data.get('pass_type', 'receipt')
#         details = request.data.get('details', {})
#         api_key = os.getenv('GOOGLE_WALLET_API_KEY')
#         issuer_id = os.getenv('GOOGLE_WALLET_ISSUER_ID')
#         class_id = os.getenv('GOOGLE_WALLET_CLASS_ID')
#         if not (api_key and issuer_id and class_id):
#             return Response({'error': 'Google Wallet API config missing in .env.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # Create a unique pass ID
#         pass_id = f"{issuer_id}.{user.id}.{pass_type}.{WalletPass.objects.count()+1}"
#         url = f"https://walletobjects.googleapis.com/walletobjects/v1/genericObject?key={api_key}"
#         payload = {
#             "id": pass_id,
#             "classId": class_id,
#             "state": "ACTIVE",
#             "heroImage": details.get('image_url'),
#             "textModulesData": [
#                 {"header": k, "body": str(v)} for k, v in details.items()
#             ],
#             "linksModuleData": {
#                 "uris": details.get('links', [])
#             }
#         }
#         headers = {"Content-Type": "application/json"}
#         try:
#             resp = requests.post(url, data=json.dumps(payload), headers=headers)
#             data = resp.json()
#             pass_url = data.get('id', '')
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # Save to WalletPass model
#         wallet_pass = WalletPass.objects.create(user=user, pass_type=pass_type, pass_id=pass_id, pass_url=pass_url, details=details)
#         return Response({'message': 'Wallet pass created.', 'pass_id': pass_id, 'pass_url': pass_url}, status=status.HTTP_201_CREATED)

# class UserQueryViewSet(viewsets.ModelViewSet):
#     queryset = UserQuery.objects.all()
#     serializer_class = UserQuerySerializer

#     @action(detail=False, methods=['post'])
#     def ask(self, request):
#         user_query = request.data.get('query')
#         if not user_query:
#             return Response({'error': 'No query provided.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Call Gemini (Vertex AI) API
#         api_key = os.getenv('GEMINI_API_KEY')
#         if not api_key:
#             return Response({'error': 'GEMINI_API_KEY not set in .env.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=' + api_key
#         payload = {
#             "contents": [{"parts": [{"text": user_query}]}]
#         }
#         try:
#             response = requests.post(url, json=payload)
#             data = response.json()
#             answer = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # Save the query and response
#         user_query_obj = UserQuery.objects.create(user=request.user, query_text=user_query, response_text=answer)
#         return Response({'query': user_query, 'answer': answer}, status=status.HTTP_200_OK)

# class WalletPassViewSet(viewsets.ModelViewSet):
#     # ... (This ViewSet remains the same as the previous version) ...
#     queryset = WalletPass.objects.all()
#     serializer_class = WalletPassSerializer

#     def _create_pass_jwt(self, user, pass_type, details):
#         print("Creating Wallet Pass JWT for user")
#         issuer_id = os.getenv('GOOGLE_WALLET_ISSUER_ID')
#         class_id = os.getenv('GOOGLE_WALLET_CLASS_ID')
#         service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')

#         if not (issuer_id and class_id and service_account_email):
#             raise Exception('Google Wallet API config missing in .env.')

#         pass_id = f"{issuer_id}.{user.id}-{pass_type}-{WalletPass.objects.count()+1}"
        
#         text_modules = []
#         if 'shopping_list' in details:
#             items_body = "\n".join([f"• {item}" for item in details['shopping_list']])
#             text_modules.append({"header": "Shopping List", "body": items_body})
        
#         jwt_payload = { "iss": service_account_email, "aud": "google", "typ": "savetowallet", "origins": [], "payload": { "genericObjects": [{"id": pass_id, "classId": class_id, "cardTitle": {"defaultValue": {"language": "en", "value": "Raseed Shopping List"}}, "header": {"defaultValue": {"language": "en", "value": "Your Shopping List"}}, "textModulesData": text_modules }]}}
        
#         print("Wallet Pass JWT Payload Created:", jwt_payload)
#         WalletPass.objects.create(user=user, pass_type=pass_type, pass_id=pass_id, details=details)
        # return {"message": "Wallet pass creation triggered successfully.", "pass_payload": jwt_payload}


class WalletPassViewSet(viewsets.ModelViewSet):
    queryset = WalletPass.objects.all()
    serializer_class = WalletPassSerializer

    def _create_pass_jwt(self, user, pass_type, details):
        print("Creating and SIGNING Wallet Pass JWT for user")
        issuer_id = os.getenv('GOOGLE_WALLET_ISSUER_ID')
        class_id = os.getenv('GOOGLE_WALLET_CLASS_ID')
        service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
        service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        if not (issuer_id and class_id and service_account_email and service_account_file):
            raise Exception('Google Wallet API config missing or incomplete in .env.')

        pass_id = f"{issuer_id}.{user.id}-{pass_type}-{WalletPass.objects.count()+1}"
        
        text_modules = []
        if 'shopping_list' in details:
            items_body = "\n".join([f"• {item}" for item in details['shopping_list']])
            text_modules.append({"header": "Shopping List", "body": items_body})
        
        # This is the payload you were seeing before
        jwt_payload = {
            "iss": service_account_email,
            "aud": "google",
            "typ": "savetowallet",
            "origins": [], # Add your frontend URL here later
            "payload": {
                "genericObjects": [{
                    "id": pass_id,
                    "classId": class_id,
                    "cardTitle": {"defaultValue": {"language": "en", "value": "Raseed Shopping List"}},
                    "header": {"defaultValue": {"language": "en", "value": "Your Shopping List"}},
                    "textModulesData": text_modules
                }]
            }
        }
        
        # --- NEW: Sign the JWT Payload ---
        with open(service_account_file, 'r') as f:
            creds_json = json.load(f)
        
        # The signer uses the private key from your service account file
        signer = crypt.RSASigner.from_service_account_info(creds_json)
        signed_jwt = jwt.encode(signer, jwt_payload).decode('utf-8')
        
        # --- NEW: Construct the final "Save to Wallet" link ---
        save_url = f"https://pay.google.com/gp/v/save/{signed_jwt}"
        print(f"Generated Save to Wallet URL: {save_url}")

        WalletPass.objects.create(user=user, pass_type=pass_type, pass_id=pass_id, details=details)
        
        # Return the final URL instead of the raw payload
        return {"message": "Wallet pass created successfully.", "save_url": save_url}


class SpendingAnalysisViewSet(viewsets.ViewSet):
    """
    A dedicated viewset for providing on-the-fly spending analysis,
    including a data list for charts and text-based savings suggestions.
    """
    
    @action(detail=False, methods=['post'], url_path='analyze')
    def analyze(self, request):
        user_query = request.data.get('query')
        if not user_query:
            return Response({'error': 'A query is required for analysis.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 1: Fetch all purchase history for the user.
            default_user, _ = User.objects.get_or_create(username='defaultuser')
            all_receipts = Receipt.objects.filter(user=default_user)
            
            if not all_receipts.exists():
                return Response({'answer': "I can't analyze your spending because no receipts have been uploaded yet."}, status=status.HTTP_200_OK)

            purchase_history = [receipt.data_json for receipt in all_receipts]

            # Step 2: Use Gemini to categorize every item in the history.
            categorization_model = GenerativeModel("gemini-1.5-flash")
            categorization_prompt = f"""
            Analyze the user's purchase history. Your only task is to add a 'category' to each item.
            Assign a category from this list: ["food", "travel", "groceries", "clothes", "others"].
            Return ONLY a single, raw JSON object which is an array of all items from all receipts, with the category added. Do not use markdown.
            Example format:
            [
              {{"name": "Milk", "quantity": 1, "price": 3.50, "category": "groceries"}},
              {{"name": "T-Shirt", "quantity": 2, "price": 20.00, "category": "clothes"}}
            ]

            User's Purchase History:
            {json.dumps(purchase_history, indent=2)}
            """
            response = categorization_model.generate_content(categorization_prompt)
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:-3].strip()
            categorized_items = json.loads(json_text)

            # Step 3: Process the structured data to get summaries.
            items_per_category = {"food": 0, "travel": 0, "groceries": 0, "clothes": 0, "others": 0}
            spending_by_category = {"food": 0.0, "travel": 0.0, "groceries": 0.0, "clothes": 0.0, "others": 0.0}

            for item in categorized_items:
                category = item.get('category', 'others').lower()
                if category in items_per_category:
                    items_per_category[category] += int(item.get('quantity', 1))
                    spending_by_category[category] += float(item.get('price', 0.0)) * int(item.get('quantity', 1))

            # Step 4: Prepare the data list for the frontend chart.
            category_data = [
                {"category": k, "item_count": v} 
                for k, v in items_per_category.items() if v > 0
            ]

            # Step 5: Get text analysis from Gemini using the monetary spending summary.
            analysis_model = GenerativeModel("gemini-1.5-flash")
            analysis_prompt = f"""
            You are a helpful financial assistant. Based on the user's spending summary and their query, provide a concise analysis and savings suggestions.

            Spending Summary ($):
            {json.dumps({k: round(v, 2) for k, v in spending_by_category.items()}, indent=2)}

            User's Query:
            "{user_query}"

            Your Analysis:
            """
            response = analysis_model.generate_content(analysis_prompt)
            analysis_text = response.text

            # Step 6: Return the combined response with the data list.
            return Response({
                'analysis_text': analysis_text,
                'category_data': category_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Spending analysis error: {e}")
            return Response({'error': f"An error occurred during analysis: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UserQueryViewSet(viewsets.ModelViewSet):
    queryset = UserQuery.objects.all()
    serializer_class = UserQuerySerializer

    # --- Define the Agent (with simplified tools) ---
    agent_tool = Tool.from_function_declarations([
        FunctionDeclaration.from_func(get_purchase_history),
        FunctionDeclaration.from_func(create_shopping_list_pass),
    ])
    
    agent_model = GenerativeModel(
        "gemini-1.5-flash",
        tools=[agent_tool],
        system_instruction=[
           "You are an action-oriented assistant. Your task is to execute the user's request by calling the appropriate tool.",
            "For example, if the user wants a shopping list, call the `create_shopping_list_pass` tool.",
        ]
    )
    rag_model = GenerativeModel("gemini-1.5-flash")


    # @action(detail=False, methods=['post'])
    # def ask(self, request):
    #     default_user, _ = User.objects.get_or_create(username='defaultuser')
    #     user_query = request.data.get('query')
    #     if not user_query:
    #         return Response({'error': 'No query provided.'}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         # Start a chat session WITHOUT automatic function calling
    #         chat = self.agent_model.start_chat()
            
    #         # 1. First call to the model to get its decision
    #         response = chat.send_message(user_query)
    #         part = response.candidates[0].content.parts[0]

    #         # 2. Check if the model decided to call a tool
    #         if part.function_call.name:
    #             function_call = part.function_call
    #             tool_name = function_call.name
    #             tool_args = {key: value for key, value in function_call.args.items()}
                
    #             print(f"Agent wants to call tool: {tool_name} with args: {tool_args}")

    #             # 3. Execute the requested tool function
    #             if tool_name == "get_purchase_history":
    #                 tool_result = get_purchase_history()
    #             elif tool_name == "create_shopping_list_pass":
    #                 tool_result = create_shopping_list_pass(**tool_args)
    #             else:
    #                 tool_result = json.dumps({"error": f"Unknown tool requested: {tool_name}"})

    #             # 4. Second call: Send the tool's result back to the model
    #             response = chat.send_message(
    #                 Part.from_function_response(
    #                     name=tool_name,
    #                     response={"content": tool_result},
    #                 )
    #             )
            
    #         # The final answer is in the text of the last response
    #         final_answer = response.text

    #         # Save the query and response
    #         UserQuery.objects.create(user=default_user, query_text=user_query, response_text=final_answer)

    #         # Check if the final answer contains a wallet pass confirmation
    #         try:
    #             potential_json = json.loads(final_answer)
    #             if "pass_payload" in potential_json:
    #                 return Response(potential_json, status=status.HTTP_200_OK)
    #         except (json.JSONDecodeError, TypeError):
    #             pass # It's just a plain text answer, which is fine.

    #         return Response({'answer': final_answer}, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         print(f"Agent invocation error: {e}")
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_intent(self, user_query: str) -> dict:
        """
        A dedicated function to classify the user's intent.
        """
        # This model is configured with no tools, just for classification.
        intent_model = GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Analyze the user's query and classify its primary intent.
        Respond with ONLY a JSON object with one of two possible values for the "intent" key:
        1. "ASK_A_QUESTION": If the user is asking for information, a summary, or a calculation based on their history.
        2. "PERFORM_AN_ACTION": If the user query involves taking an action other than asking simple questions, like creating a shopping list or Google Wallet pass.

        User Query: "{user_query}"

        JSON Response:
        """
        

        
        response = intent_model.generate_content(prompt)
        try:
            print(f"Intent Model Response: {response.text}")  # Debugging line to see the model's response
              # Debugging line to see the model's response
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                # Removes the ```json at the start and the ``` at the end
                json_text = json_text[7:-3].strip()

            print(f"Cleaned JSON Response: {json_text}")

            return json.loads(json_text)
        except json.JSONDecodeError:
            # If the model fails to return clean JSON, default to a safe option.
            return {"intent": "ASK_A_QUESTION"}


    @action(detail=False, methods=['post'])
    def ask(self, request):
        default_user, _ = User.objects.get_or_create(username='defaultuser')
        user_query = request.data.get('query')
        if not user_query:
            return Response({'error': 'No query provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. First, determine the user's intent
            intent_data = self.get_intent(user_query)
            intent = intent_data.get("intent")
            print(f"Detected Intent: {intent}")

            final_answer = ""

            # 2. Execute the appropriate logic based on the intent
            if intent == "ASK_A_QUESTION":
                # --- RAG (Retrieval-Augmented Generation) Flow ---
                print("Executing RAG flow...")
                history_context = get_purchase_history()
                
                rag_prompt = f"""
                You are a helpful assistant. Based ONLY on the following purchase history, answer the user's question.
                If the history doesn't contain the answer, say so. Respond in the same language as the user's query.

                Purchase History:
                {history_context}

                User's Question:
                "{user_query}"
                """
                response = self.rag_model.generate_content(rag_prompt)
                final_answer = response.text

            elif intent == "PERFORM_AN_ACTION":
                # --- Agentic Tool-Calling Flow ---
                print("Executing Agentic Action flow...")
                # chat = self.agent_model.start_chat()
                # response = chat.send_message(user_query)
                # print(f"Agent Response: {response.text}")

                response = self.agent_model.generate_content(user_query)

                # print(f"Agent Response: {response.text}")

                
                part = response.candidates[0].content.parts[0]
                print(f"Agent Part: {part}")
                # Manual tool-calling loop
                if part.function_call and part.function_call.name:
                    function_call = part.function_call
                    tool_name = function_call.name
                    tool_args = {key: value for key, value in function_call.args.items()}
                    
                    if tool_name == "create_shopping_list_pass":
                        tool_result = create_shopping_list_pass(**tool_args)
                        # The result from the tool is the final answer for actions
                        final_answer = tool_result
                    else:
                        final_answer = json.dumps({"error": f"Unknown action tool: {tool_name}"})
                else:
                    # Fallback if the action agent doesn't call a tool
                    final_answer = response.text
            else:
                final_answer = "I'm sorry, I'm not sure how to handle that request."

            # --- Save and Return the Final Response ---
            UserQuery.objects.create(user=default_user, query_text=user_query, response_text=str(final_answer))

            try: # Check if the answer is a JSON object from a tool
                potential_json = json.loads(final_answer)
                return Response(potential_json, status=status.HTTP_200_OK)
            except (json.JSONDecodeError, TypeError): # It's a plain text answer
                return Response({'answer': final_answer}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Agent invocation error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






    # @action(detail=False, methods=['post'])
    # def ask(self, request):
    #     default_user, _ = User.objects.get_or_create(username='defaultuser')
    #     user_query = request.data.get('query')
    #     if not user_query:
    #         return Response({'error': 'No query provided.'}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         # Start a chat session with the agent
    #         chat = self.agent_model.start_chat(enable_automatic_function_calling=True)
            
    #         # Invoke the agent with the user's query directly
    #         response = chat.send_message(user_query)
            
    #         # The ADK handles the tool calling automatically. We just get the final text response.
    #         final_answer = response.text

    #         # Save the query and response
    #         UserQuery.objects.create(user=default_user, query_text=user_query, response_text=final_answer)

    #         # Check if the final answer contains a wallet pass confirmation
    #         try:
    #             potential_json = json.loads(final_answer)
    #             if "pass_payload" in potential_json:
    #                 return Response(potential_json, status=status.HTTP_200_OK)
    #         except (json.JSONDecodeError, TypeError):
    #             # It's just a plain text answer, which is fine.
    #             pass

    #         return Response({'answer': final_answer}, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         print(f"Agent invocation error: {e}")
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)