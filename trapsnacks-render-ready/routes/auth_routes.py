# routes/auth_routes.py
# LoginScreen + AuthRoutes: login, logout, and the role check used by every other routes file.

from functools import wraps
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from models import User

auth_routes = Blueprint('auth_routes', __name__)

HOME_PAGE = {'cashier': '/cashier', 'chef': '/kitchen', 'rider': '/rider', 'owner': '/deliveries'}


def roles_required(*roles):
    """Put @roles_required('cashier') above a route so only those roles can use it (Security 2)."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator


def run_service(action, success_code=200):
    """Runs a service call. A ValueError (a broken rule) becomes a message for the screen."""
    try:
        result = action()
        return jsonify(ok=True, data=result), success_code
    except ValueError as error:
        return jsonify(ok=False, error=str(error)), 400


@auth_routes.get('/')
def home():
    if current_user.is_authenticated:
        return redirect(HOME_PAGE[current_user.role])
    return redirect(url_for('auth_routes.login'))


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username', '').strip()).first()
        if user and check_password_hash(user.password_hash, request.form.get('password', '')):
            login_user(user)
            return redirect(HOME_PAGE[user.role])
        flash('Wrong username or password.', 'danger')
    return render_template('login.html')


@auth_routes.get('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_routes.login'))
