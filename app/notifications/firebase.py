from pathlib import Path

import firebase_admin
from firebase_admin import credentials


BASE_DIR = Path(__file__).resolve().parent

SERVICE_ACCOUNT_KEY = BASE_DIR / "credentials" / "medocr-f6ddc-firebase-adminsdk-fbsvc-0bdd169219.json"


def initialize_firebase():
    """
    Initialize Firebase Admin SDK only once.
    """

    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred = credentials.Certificate(str(SERVICE_ACCOUNT_KEY))

    return firebase_admin.initialize_app(cred)