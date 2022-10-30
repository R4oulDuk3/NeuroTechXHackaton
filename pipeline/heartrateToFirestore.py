import os

from common.consts import project_id, subscription_id
from common.settings import get_settings

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\gavrilov\\PycharmProjects\\neuroTechx\\creds\\neurotechxhackaton-2a3116995da0.json"
import firebase_admin
from firebase_admin import firestore
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
app = firebase_admin.initialize_app()
db = firestore.client()
# collectionName="userHeartRate"

subscription_path = subscriber.subscription_path(project_id, subscription_id)


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message.ack()
    msg_data = eval(message.data.decode('utf-8'))
    db.collection(get_settings(db)['mode']).add(msg_data)


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")
timeout = 20.0

while (True):
    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.
