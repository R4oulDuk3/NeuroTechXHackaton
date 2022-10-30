import os

from common.consts import CALIBRATION_MODE, userHeartRate60secAverageCollection
from common.settings import get_settings
import firebase_admin
from firebase_admin import firestore

from common.userInfo import get_user_info, update_user_info

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".\\creds\\neurotechxhackaton-2a3116995da0.json"
app = firebase_admin.initialize_app()
db = firestore.client()
lowEndBPM = 60
highEndBpm = 100

calibrationCollectionName = "Callibration"

userHeartRateCollectionName = "userHeartRate"
ref = db.collection(userHeartRateCollectionName)
query = ref.order_by("timestamp", direction=firestore.Query.ASCENDING).limit_to_last(60)


def calc_heartrate_info(docs):
    sum_bpm = 0
    for doc in docs:
        sum_bpm += doc.to_dict()['bpm']
    return sum_bpm / len(docs)


def update_user_avg_heartrate(user_info, avg_hr, heartrate_cnt):
    new_avg = (user_info['gatheredHeartRateCount'] * user_info['AvgHeartRate'] + avg_hr * heartrate_cnt) / (
            user_info['gatheredHeartRateCount'] + heartrate_cnt)
    new_user_info = {
        'gatheredHeartRateCount': user_info['gatheredHeartRateCount'] + heartrate_cnt,
        'AvgHeartRate': new_avg
    }
    print(new_user_info)
    update_user_info(db, new_user_info)


def get_new_heartrate_batch(collection):
    docs = db.collection(collection).order_by("timestamp", direction=firestore.Query.ASCENDING).limit_to_last(60).get()
    return docs


while True:
    heart_rates = get_new_heartrate_batch(get_settings(db)['mode'])
    avg_hr = calc_heartrate_info(heart_rates)
    user_info = get_user_info(db)
    print("avg_hr")
    print(avg_hr)
    if get_settings(db)['mode'] == CALIBRATION_MODE:
        if lowEndBPM < avg_hr < highEndBpm:
            update_user_avg_heartrate(user_info, avg_hr, len(heart_rates))
    else:
        isPanicAttack = False
        if avg_hr > user_info['AvgHeartRate'] * 1.5:
            # SIGNAL PANIC ATTACK
            isPanicAttack = True
        new_doc = {
            'startTimestamp': heart_rates[0].to_dict()['timestamp'],
            'endTimestamp': heart_rates[-1].to_dict()['timestamp'],
            'avg_hr': avg_hr,
            'isPanicAttack': isPanicAttack
        }
        db.collection(userHeartRate60secAverageCollection).add(new_doc)
