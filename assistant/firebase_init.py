import os
import firebase_admin
from firebase_admin import credentials, firestore

# Get the directory of the current file (assistant/)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory by going up one level
BASE_DIR = os.path.dirname(CURRENT_DIR)

# Construct the absolute path to the service account key
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'credentials', 'service-account.json')

# Only initialize the app if it hasn't been initialized yet
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred, {
        'projectId': 'project-raseed-466711',  # Replace with your actual project ID
        # 'databaseURL': 'https://<your-database-name>.firebaseio.com'  # Not needed for Firestore
    })

db = firestore.client()