from flask.ext.bcrypt import generate_password_hash, check_password_hash
from flask import request, redirect, url_for, session, abort
from functools import wraps
from stalkerweb import mongo, app
import pymongo

def is_valid_email_login(email, password):
    uinfo = mongo.db.users.find_one({'email': email})
    if uinfo:
        if check_password_hash(uinfo['hash'], password):
            return True
        else:
            return False
    else:
        return False

def is_valid_login(username, password):
    uinfo = mongo.db.users.find_one({'username': username})
    if uinfo:
        if check_password_hash(uinfo['hash'], password):
            return True
        else:
            return False
    else:
        return False

def add_user(username, password, email):
    pw_hash = generate_password_hash(password)
    try:
        uid = mongo.db.users.insert({'username': username, 'hash': pw_hash,
                                     'email': email})
        return True
    except pymongo.errors.DuplicateKeyError:
        return False

def change_pass(username, password):
    pw_hash = generate_password_hash(password)
    try:
        q = mongo.db.users.update({'username': username}, {"$set": {'hash': pw_hash}}, upsert=False)
        print q
        if q['updatedExisting']:
            return True
        else:
            return False
    except Exception as err:
        print err
        return False
        
def remove_user(username):
    try:
        q = mongo.db.users.remove({'username': username}, safe=True)
        if q['n'] == 1:
            return True
        else:
            return False
    except Exception as err:
        print err
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-API-KEY'):
            if not session.get('logged_in', False):
                return redirect(url_for('signin', next=request.url))
            return f(*args, **kwargs)
        else:
            if request.headers.get('X-API-KEY') == app.config['API_KEY']:
                return f(*args, **kwargs)
            else:
                abort(403)
    return decorated_function
