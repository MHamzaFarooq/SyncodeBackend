import firebase_admin
from firebase_admin import credentials, firestore
from . import settings
def initialize_firebase():
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db
    except Exception as e:
        print(f'Error initializing firebase: {e}')
        return None
    

# Create a database instance
db = initialize_firebase()



