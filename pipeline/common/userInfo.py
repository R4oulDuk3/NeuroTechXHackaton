from common.delete import delete_collection

settingCollectionName = "userInfo"


def get_user_info(db):
    docs = db.collection(settingCollectionName).get()
    user_info = docs[-1].to_dict()
    return user_info


def update_user_info(db, user_info):
    delete_collection(db.collection(settingCollectionName),100)
    db.collection(settingCollectionName).add(user_info)
