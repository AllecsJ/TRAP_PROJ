# TrapSnacks: Deploy to Render (testing)

1. Push these files to your private GitHub repository.
2. In Render, choose **New > Web Service** and select your repository's `main` branch.
3. Select **Python** runtime, **Free** instance and repository root as the Root Directory (leave blank).
4. Build command: `pip install -r requirements.txt`
5. Start command: `python init_db.py && gunicorn --worker-class gthread --workers 1 --threads 20 --bind 0.0.0.0:$PORT app:app`
6. Environment variables:
   - `SECRET_KEY`: generate a random secret of at least 32 characters (Render can generate a secret value).
   - `ADMIN_USERNAME`: choose your initial owner username (for example `owner`).
   - `ADMIN_PASSWORD`: choose a unique strong password of at least 12 characters. Do not use the demo credentials in `seed.py`.
   - `DEMO_MENU`: set to `1` to automatically add demo menu items on a fresh database (optional; does not overwrite existing menu).
   - `PYTHON_VERSION` (optional): use a supported Python version matching your environment.
7. Deploy. Visit `https://<your-service>.onrender.com/login` and sign in with your chosen owner account.

## Database warning

This project uses SQLite (`instance/trapsnacks.db`) by default. Render Free's filesystem is ephemeral: orders, users and other data may disappear on restart, sleep/wake replacement, or redeployment. The startup initializer recreates the owner account and, if enabled, demo menu items when needed; it does not run `seed.py` and does not restore prior orders. Treat it as disposable test data. For durable use, move to a persistent external database and add the corresponding Python driver.

## Notes

- Do not run `python seed.py` on a database you want to keep: it drops all tables and creates publicly known demo passwords.
- Use a single Gunicorn worker because Flask-SocketIO rooms and state are in-process. Threads provide simultaneous connections.
- The free instance spins down after inactivity. Expect cold-start delays and WebSocket reconnects.
- Keep this repo private and never commit passwords or your SECRET_KEY.
