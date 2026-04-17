from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from bson import ObjectId
import json

# These will be set by app.py at runtime
mongo = None
bcrypt = Bcrypt()

def init_mongo(mongo_instance):
    """Initialize mongo reference from app"""
    global mongo
    mongo = mongo_instance

def get_db():
    """Get MongoDB database instance - works within app context"""
    if mongo is None:
        return None
    return mongo.db


def get_utc_now():
    """Get current UTC time"""
    return datetime.utcnow()


class User(UserMixin):
    def __init__(self, **kwargs):
        super().__init__()
        self._id = kwargs.get('_id')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password_hash = kwargs.get('password_hash')
        self.created_at = kwargs.get('created_at') or get_utc_now()

    @property
    def id(self):
        return self._id

    def get_id(self):
        return str(self._id) if self._id else None

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            '_id': self.id,
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        return User(**data)


class Trip:
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.user_id = kwargs.get('user_id')
        self.title = kwargs.get('title')
        self.destination = kwargs.get('destination')
        self.origin = kwargs.get('origin')
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.duration_days = kwargs.get('duration_days')
        self.form_data = kwargs.get('form_data', {})
        self.result_data = kwargs.get('result_data', {})
        self.status = kwargs.get('status', 'pending')
        self.created_at = kwargs.get('created_at') or get_utc_now()

    def set_form_data(self, data: dict):
        self.form_data = data

    def get_form_data(self) -> dict:
        return self.form_data if self.form_data else {}

    def set_result_data(self, data: dict):
        self.result_data = data

    def get_result_data(self) -> dict:
        return self.result_data if self.result_data else {}

    def to_dict(self):
        return {
            '_id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'destination': self.destination,
            'origin': self.origin,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'duration_days': self.duration_days,
            'form_data': self.form_data,
            'result_data': self.result_data,
            'status': self.status,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        return Trip(**data)


# Query helpers
class UserManager:
    @staticmethod
    def create(name, email, password_hash):
        db = get_db()
        user_doc = {
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'created_at': get_utc_now()
        }
        try:
            result = db.users.insert_one(user_doc)
            user_doc['_id'] = result.inserted_id
            return User.from_dict(user_doc)
        except Exception as e:
            if 'E11000 duplicate key error' in str(e):
                return None  # Email already exists
            raise

    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_doc = db.users.find_one({'_id': user_id})
        return User.from_dict(user_doc) if user_doc else None

    @staticmethod
    def find_by_email(email):
        db = get_db()
        user_doc = db.users.find_one({'email': email.lower()})
        return User.from_dict(user_doc) if user_doc else None


class TripManager:
    @staticmethod
    def create(user_id, title, destination, origin, start_date, end_date, duration_days, form_data, status='pending'):
        db = get_db()
        trip_doc = {
            'user_id': user_id,
            'title': title,
            'destination': destination,
            'origin': origin,
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': duration_days,
            'form_data': form_data,
            'result_data': {},
            'status': status,
            'created_at': get_utc_now()
        }
        result = db.trips.insert_one(trip_doc)
        trip_doc['_id'] = result.inserted_id
        return Trip.from_dict(trip_doc)

    @staticmethod
    def find_by_id(trip_id):
        db = get_db()
        if isinstance(trip_id, str):
            trip_id = ObjectId(trip_id)
        trip_doc = db.trips.find_one({'_id': trip_id})
        return Trip.from_dict(trip_doc) if trip_doc else None

    @staticmethod
    def find_by_user_id(user_id):
        db = get_db()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        trips = db.trips.find({'user_id': user_id}).sort('created_at', -1)
        return [Trip.from_dict(t) for t in trips]

    @staticmethod
    def update(trip_id, **kwargs):
        db = get_db()
        if isinstance(trip_id, str):
            trip_id = ObjectId(trip_id)
        db.trips.update_one({'_id': trip_id}, {'$set': kwargs})
