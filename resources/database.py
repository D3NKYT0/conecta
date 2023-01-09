from config import _auth
from pymongo import MongoClient as Client


class Database(object):
    def __init__(self, app):
        self.app = app
        self._connect = Client(_auth['URI'], connectTimeoutMS=30000)
        self._database = self._connect[_auth['DB_NAME']]

    def cd(self, collections):  # atualizado no banco de dados
        return self._database[collections]
