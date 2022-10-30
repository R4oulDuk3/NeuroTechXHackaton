settingCollectionName = "Settings"


def get_settings(db):
    docs = db.collection(settingCollectionName).get()
    settings = docs[0].to_dict()
    return settings
