import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from typing import Optional

class FirebaseConfig:
    def __init__(self):
        self.db: Optional[firestore.Client] = None
        self.bucket: Optional[storage.Bucket] = None
        self.initialize()

    def initialize(self):
        """Initialize Firebase services"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to get service account from environment or file
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT', 'firebase-service-account.json')

                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                else:
                    # Use default credentials (for deployment)
                    cred = credentials.ApplicationDefault()

                firebase_admin.initialize_app(cred, {
                    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'parking-detection-system.appspot.com')
                })

            self.db = firestore.client()
            self.bucket = storage.bucket()
            print("Firebase initialized successfully")

        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            self.db = None
            self.bucket = None

    def is_available(self) -> bool:
        """Check if Firebase services are available"""
        return self.db is not None and self.bucket is not None

# Global Firebase instance
firebase_config = FirebaseConfig()
