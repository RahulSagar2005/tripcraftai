import os
import json
import threading
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from config import Config
from models import bcrypt, User, UserManager, Trip, TripManager, init_mongo, get_db
from agents.orchestrator import run_all_agents

app = Flask(__name__)
app.config.from_object(Config)

# Use direct MongoClient for better Atlas support
mongo_client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=10000)
db = mongo_client[Config.DB_NAME]

# Wrap for flask-pymongo compatibility
class MongoWrapper:
    def __init__(self, db_instance):
        self._db = db_instance

    @property
    def db(self):
        return self._db

mongo = MongoWrapper(db)
bcrypt.init_app(app)

# Initialize mongo reference in models module
init_mongo(mongo)

login_manager = LoginManager(app)

login_manager.login_view = 'auth'
login_manager.login_message = 'Please sign in to access this page.'

# Initialize MongoDB indexes on first request
_initialized = False

def init_db_indexes():
    """Initialize MongoDB indexes on first request"""
    global _initialized
    if _initialized:
        return
    try:
        db = get_db()
        db.users.create_index('email', unique=True)
        db.trips.create_index('user_id')
        db.trips.create_index([('created_at', -1)])
        _initialized = True
        print("[MongoDB] Indexes created successfully")
    except Exception as e:
        print(f"[MongoDB] Index note: {e}")

@app.before_request
def before_request():
    # Skip heavy init for health checks so liveness probes never block.
    if request.path == '/health':
        return
    init_db_indexes()


@login_manager.user_loader
def load_user(user_id):
    return UserManager.find_by_id(user_id)


# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        return redirect(url_for('plan'))
    return render_template('auth.html')


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400

        if UserManager.find_by_email(email):
            return jsonify({'success': False, 'message': 'Email already registered.'}), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = UserManager.create(name=name, email=email, password_hash=password_hash)
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('plan')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Signup failed: {str(e)}'}), 500


@app.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        user = UserManager.find_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('plan')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Signin failed: {str(e)}'}), 500


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ─── Main Pages ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plan')
@login_required
def plan():
    return render_template('plan.html', user=current_user)


@app.route('/my-plans')
@login_required
def my_plans():
    trips = TripManager.find_by_user_id(current_user.id)
    return render_template('my_plans.html', trips=trips, user=current_user)


# ─── Trip Submission ───────────────────────────────────────────────────────────

@app.route('/create-trip', methods=['POST'])
@login_required
def create_trip():
    try:
        form_data = request.get_json()
        if not form_data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        # Validate required fields
        required_fields = ['destination', 'origin', 'start_date', 'end_date']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Create trip record
        trip = TripManager.create(
            user_id=current_user.id,
            title=f"Trip to {form_data.get('destination', 'Unknown')}",
            destination=form_data.get('destination', ''),
            origin=form_data.get('origin', ''),
            start_date=form_data.get('start_date', ''),
            end_date=form_data.get('end_date', ''),
            duration_days=int(form_data.get('duration_days', 5)),
            form_data=form_data,
            status='processing'
        )
        trip_id = str(trip.id)

        # Run agents in background thread
        def process_trip(trip_id, form_data):
            with app.app_context():
                try:
                    results = run_all_agents(form_data)
                    TripManager.update(trip_id, result_data=results, status='done' if results.get('status') == 'success' else 'error')
                except Exception as e:
                    TripManager.update(trip_id, result_data={'error': str(e)}, status='error')

        thread = threading.Thread(target=process_trip, args=(trip_id, form_data))
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'trip_id': trip_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Trip creation failed: {str(e)}'}), 500


@app.route('/trip-status/<trip_id>')
@login_required
def trip_status(trip_id):
    try:
        trip = TripManager.find_by_id(trip_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        # Check user owns this trip
        if str(trip.user_id) != str(current_user.id):
            return jsonify({'error': 'Access denied'}), 403
        return jsonify({'status': trip.status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/trip/<trip_id>')
@login_required
def trip_result(trip_id):
    try:
        trip = TripManager.find_by_id(trip_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        # Check user owns this trip
        if str(trip.user_id) != str(current_user.id):
            return jsonify({'error': 'Access denied'}), 403
        form_data = trip.get_form_data()
        result_data = trip.get_result_data()
        return render_template('result.html', trip=trip, form_data=form_data, result=result_data, user=current_user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/processing/<trip_id>')
@login_required
def processing(trip_id):
    try:
        trip = TripManager.find_by_id(trip_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        # Check user owns this trip
        if str(trip.user_id) != str(current_user.id):
            return jsonify({'error': 'Access denied'}), 403
        return render_template('processing.html', trip=trip, user=current_user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Health Check (used by Railway / Render) ─────────────────────────────────

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Production: gunicorn (set in Procfile) binds 0.0.0.0:$PORT
    # Local dev: respect PORT env var so the same code works in both
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
