from flask import session, json, jsonify
from flask_redis import FlaskRedis
from flask_session import Session
from bson import ObjectId
import hashlib, binascii, os, sys, datetime, time

from models.user import commonUser
sys.path.append("..")


class JSONEncoder(json.JSONEncoder):  #klasa za pretvorbu Mongo objekata u string
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return (datetime.datetime.min + o).time().isoformat()
        else:
            return json.JSONEncoder.default(self, o)





class Auth:
    def __init__(self, app):
        self.app = app

    def config(self, sessionLifetime): #konfiguracija sesije
        self.app.config["SESSION_TYPE"] = 'redis' #za spremanje sesije - redis
        self.app.config["SECRET_KEY"] = os.urandom(24)
        self.app.config["SESSION_PERMANENT"] = False
        self.app.config["PERMANENT_SESSION_LIFETIME"] = sessionLifetime
        Session(self.app)

        
    def setSession(self, userData): #postavljanje sesije
        session['sessionUser'] = userData
        return {'auth': True, 'userData': json.loads(userData)}

    def getSession(self): #provjera sesije
        data = session.get('sessionUser')

        if data:
            return jsonify({'auth': True, 'userData': json.loads(data)})
        else:
            self.clearSession() #preventing sending empty session key to browser
            return jsonify({'auth': False})

    def clearSession(self): #brisanje sesije
        session.clear()
        return jsonify({'authCleared': True})





class SignUp:
    def __init__(self, session, dbCollection):
        self.session = session
        self.dbCollection = dbCollection
    
    def registerUser(self, data):
        self.session.clearSession() #preventing sending empty session key to browser

        if not data['email']:
            return {
                'success': False,
                'error': 'Email required'
            }
        if not data['password']:
            return {
                'success': False,
                'error': 'Password required'
            }

        data['password'] = self.hash_password(data['password'])
        savedUser = commonUser(data).save(self.dbCollection)
        if not savedUser['success']:
            return savedUser
        
        registeredUser = JSONEncoder().encode(savedUser['data'])
        
        return self.session.setSession(registeredUser)


    def loginUser(self, data):
        self.session.clearSession() #preventing sending empty session key to browser

        if not data['email']:
            return {
                'success': False,
                'error': 'Email required.'
            }
        if not data['password']:
            return {
                'success': False,
                'error': 'Password required.'
            }

        user = self.dbCollection.find_one({'email' : data['email']})
        if not user:
            return {
                'success': False,
                'error': 'Wrong email address.'
            }

        if not self.verify_password(user['password'], data['password']):
            return {
                'success': False,
                'error': 'Passwords does not match.'
            }
        else:
            del user['password']
            loggedUser = JSONEncoder().encode(user)
            return self.session.setSession(loggedUser)
            



    def hash_password(self, password): #enkripcija lozinke

        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')


    def verify_password(self, stored_password, provided_password): #provjera lozinke

        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password
