from pythonServer.mongoStorage.mongoStorage import MongoStorage

mongoStorage = MongoStorage('missions')


def get_missions():
    return mongoStorage.get_all()

