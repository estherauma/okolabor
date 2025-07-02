import firebase_admin
from firebase_admin import credentials, messaging
from decouple import config

cred_path = config("FIREBASE_SERVICE_ACCOUNT_KEY_FILE_PATH")

if not firebase_admin._apps and cred_path:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def send_push_notification(tokens, title, body, data=None):
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            tokens=tokens,
            data=data or {},
        )

        response = messaging.send_each_for_multicast(message)

        if response.failure_count > 0:
            responses = response.responses
            failed_tokens = []
            for idx, resp in enumerate(responses):
                if not resp.success:
                    failed_tokens.append(tokens[idx])
            print("List of tokens that caused failures: {0}".format(failed_tokens))
        return response
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return None
