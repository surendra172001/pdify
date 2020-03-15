import pymongo
import dns

cluster = pymongo.MongoClient(
        "mongodb+srv://admin:admin1234@cluster0-xd8hk.mongodb.net/test?retryWrites=true&w=majority")

db = cluster["mydb"]

def checkLogin(username, password):
    collection = db["users"]
    results = collection.find_one({"username": username, "password": password})
    return results

def doRegister(name, username, email, password):
    collection = db["users"]
    collection.insert_one({"name": name, "username": username, "email": email, "password": password})

def usernameExists(username):
    collection = db["users"]
    results = collection.find_one({"username": username})
    if(results):
        return True
    return False