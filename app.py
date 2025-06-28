from app import create_app, db
from flask_migrate import Migrate

migrate = Migrate()

app = create_app()
migrate.init_app(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Gunicorn expects a variable named 'app' in this file to run the app
# The create_app() returns the Flask app instance, so assign it to 'app'
