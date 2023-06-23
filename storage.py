from pymongo import MongoClient
import threading
from settings import password

class DataBase:
    def __init__(self):
        self._cluster = MongoClient('mongodb+srv://konstantingalanin:4pG-xkL-YKq-Hs4@cluster0.3ng34f7.mongodb.net/memorizer?retryWrites=true&w=majority')
        self._db = self._cluster['memorizer']
        self._users_collection = self._db['themes']

        print('db inited successfully')
    
    def user_reg(self,message):
        user = str(message.chat.id)
        lock = threading.Lock()
        lock.acquire()
        try:
            if self._users_collection.count_documents({'_id': user}) == 0:
                self._users_collection.insert_one({
                    '_id' : user,
                    'themes' : {},
                    'remember_btn' : False,
                    'word_to_del' : False,
                    'descript_to_show' : False,
                    'examined_themes' : []
                })
        except Exception as error:
            print(error)
        finally:
            lock.release()
    
    
    def theme_reg(self,message,start): #186
        user = str(message.chat.id)
        message_text = message.text
        lock = threading.Lock()
        lock.acquire()
        try:
            if self._users_collection.count_documents({'_id':user,f'themes.{message_text}': {'$exists': True}}) == 0 and self._users_collection.count_documents({'_id':user,f'examined_themes.{message_text}': {'$exists': True}}) == 0:
                self._users_collection.update_one(
                    {'_id': user},
                    {'$set': {f'themes.{message_text}': {
                    'start':start,
                    'index': -1,
                    'btn_pressed': True,
                    'description': ''
                }}})
                return False
            else:
                return True
        except Exception as error:
            print(error)
        finally:
            lock.release()

    def read_all_id(self): # Поменять на every
        lock = threading.Lock()
        lock.acquire()
        try:
            cursor = self._users_collection.find({}, {"_id": 1})
            id_list = [doc["_id"] for doc in cursor]
            return id_list
        except Exception as error:
            print(error)
        finally:
            lock.release()

    def collection_exist(self,user):
        lock = threading.Lock()
        lock.acquire()
        try:
            document = self._users_collection.find_one({'_id':user})
            if document:
                return True
            else:
                return False
        except Exception as error:
            print(error)
        finally:
            lock.release()

    def read_inf(self,user,flag,message_text = None):
        lock = threading.Lock()
        lock.acquire()
        try:
            document = self._users_collection.find_one({'_id':user})
            if flag == 'remember_btn':
                return document['remember_btn']
            if flag == 'word_to_del':
                return document['word_to_del']
            if flag == 'descript_to_show':
                return document['descript_to_show']   
            if flag == 'examined_themes':
                examined_themes = [theme for theme in document['examined_themes']]
                return examined_themes
            if flag == 'themes':
                themes = [theme for theme in document['themes'].keys()]
                # print(dict(document['themes']))
                return themes
            if flag == 'start':
                return document['themes'][message_text]['start']
            if flag == 'index':
                return document['themes'][message_text]['index']
            if flag == 'btn_pressed':
                return document['themes'][message_text]['btn_pressed']
            if flag == 'description':
                return document['themes'][message_text]['description']
        except Exception as error:
            print(error)
        finally:
            lock.release()


    def edit_inf(self,user,flag,value,message_text = None):
        lock = threading.Lock()
        lock.acquire()
        try:
            if flag == 'delete_examined':
                update_query = {'$pull': {'examined_themes':value}}
            elif flag == 'add_to_examined':
                update_query = {'$push': {'examined_themes':value}}
            elif flag == 'delete_current':
                update_query = {"$unset": {f'themes.{value}': 1}}
            elif flag == 'remember_btn':
                update_query = {"$set": {'remember_btn': value}}
            elif flag == 'word_to_del':
                update_query = {"$set": {'word_to_del': value}}
            elif flag == 'descript_to_show':
                update_query = {"$set": {'descript_to_show': value}}
            elif flag == 'description':
                update_query = {"$set": {f'themes.{message_text}.description': value}}
            elif flag == 'index':
                update_query = {"$set": {f'themes.{message_text}.index': value}}
            elif flag == 'btn_pressed':
                update_query = {"$set": {f'themes.{message_text}.btn_pressed': value}}
            elif flag == 'start':
                update_query = {"$set": {f'themes.{message_text}.start': value}}
            self._users_collection.update_one({'_id': user},update_query)
        except Exception as error:
            print(error)
        finally:
            lock.release()