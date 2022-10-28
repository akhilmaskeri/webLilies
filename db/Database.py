import os
from pymongo import MongoClient

DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_URL = os.environ.get("DATABASE_URL")

class DeviceIDMap():

    conn = f"mongodb+srv://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_URL}/?retryWrites=true&w=majority"

    def __init__(self):
        self.client = MongoClient(self.conn)
        self.db = self.client.torchdweb
        self.devices = self.db["user_deviceid_map"]

    def get_device_id(self, user_id):
        return self.devices.find_one({"user_id": user_id})

    def set_device_id(self, user_id, device_id):

        device = self.get_device_id(user_id)
        if device:
            self.devices.update_one({ "user_id": user_id }, {"$set": {"device_id": device_id}})
            return 

        self.devices.insert_one({"user_id": user_id, "device_id": device_id}) 

