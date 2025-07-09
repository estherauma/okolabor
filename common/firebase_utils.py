from common.logger import AppLogger
import firebase_admin
from firebase_admin import credentials, messaging
from decouple import config

cred_path = config("FIREBASE_SERVICE_ACCOUNT_KEY_FILE_PATH")

if not firebase_admin._apps and cred_path:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def send_push_notification(tokens, title, body, data=None):
    logger = AppLogger(log_file='logs/debug.log')
    logger.debug(f"Sending push notification to {len(tokens)} tokens: {title} - {body}")

    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            tokens=tokens,
            data=data or {},
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="default",
                    channel_id="default"  # Must match the one created in the app
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default"
                    )
                )
            ),
        )

        response = messaging.send_each_for_multicast(message)
        logger.debug(f"Push notification sent to {len(tokens)} tokens.")
        if response.failure_count > 0:
            responses = response.responses
            failed_tokens = []
            for idx, resp in enumerate(responses):
                if not resp.success:
                    failed_tokens.append(tokens[idx])
            logger.warning("List of tokens that caused failures: {0}".format(failed_tokens))
        return response
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return None
