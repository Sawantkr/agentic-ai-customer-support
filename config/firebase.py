import os

import firebase_admin
from firebase_admin import credentials


def initialize_firebase():

    if firebase_admin._apps:
        return firebase_admin.get_app()

    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH"
    )

    if not service_account_path:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_PATH "
            "is not configured."
        )

    cred = credentials.Certificate(
        service_account_path
    )

    return firebase_admin.initialize_app(
        cred
    )