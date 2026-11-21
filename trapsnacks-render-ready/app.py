# app.py
# Builds the application, connects all the parts, and starts the server.
# Run it with:  python app.py

from flask import Flask, render_template
from flask_login import current_user
from flask_socketio import join_room

from config import Config
from extensions import csrf, db, login_manager, socketio
from models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Connect the helper objects from extensions.py to this app
    db.init_app(app)
    socketio.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_routes.login'
    login_manager.login_message = 'Please log in first.'

    # ROUTES LAYER: one Blueprint (Routes class) per feature
    from routes.auth_routes import auth_routes
    from routes.order_routes import order_routes
    from routes.order_status_routes import order_status_routes
    from routes.edit_order_routes import edit_order_routes
    from routes.cancel_order_routes import cancel_order_routes
    from routes.kitchen_routes import kitchen_routes
    from routes.rider_routes import rider_routes
    from routes.delivery_display_routes import delivery_display_routes
    from routes.new_rider_routes import new_rider_routes
    from routes.edit_rider_routes import edit_rider_routes
    from routes.remove_rider_routes import remove_rider_routes

    for blueprint in (auth_routes, order_routes, order_status_routes, edit_order_routes,
                      cancel_order_routes, kitchen_routes, rider_routes, delivery_display_routes,
                      new_rider_routes, edit_rider_routes, remove_rider_routes):
        app.register_blueprint(blueprint)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    with app.app_context():
        db.create_all()          # creates the tables the first time
    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@socketio.on('connect')
def on_connect(auth=None):
    """Each screen joins 'rooms' so the server can send it only the updates it needs."""
    if not current_user.is_authenticated:
        return False                                   # refuse the live connection
    join_room(current_user.role)                       # 'cashier', 'chef', 'owner' or 'rider'
    if current_user.role in ('cashier', 'owner'):
        join_room('staff')                             # both use the delivery screen (FR 5)
    if current_user.role == 'rider':
        join_room(f'rider_{current_user.rider_id}')    # a private room for one rider


# Expose the Flask application to Gunicorn on Render.
app = create_app()


if __name__ == '__main__':
    print('TrapSnacks is running. On this computer open http://127.0.0.1:5000')
    print('On other devices on the same Wi-Fi open http://<this-computer-IP>:5000')
    # host='0.0.0.0' lets tablets and phones on the same Wi-Fi connect.
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
