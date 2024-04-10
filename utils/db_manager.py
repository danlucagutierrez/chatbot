
class DBManager():
    def __init__(self, db) -> None:
        self.db = db
        self.users = db.users

    def set_user(self, user_id, atributes):
        try:
            self.users.update_one({'_id': int(user_id)}, {'$set': atributes}, upsert=True)
        except Exception:
            print('Error comunicando con Mongo, verificar ip o certificado ssl')
    
    def get_user(self, user_id: int) -> dict | None:
        try:
            return self.users.find_one({'_id': int(user_id)})
        except Exception:
            print('Error comunicando con Mongo, verificar ip o certificado ssl')