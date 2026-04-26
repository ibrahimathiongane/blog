import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    with app.app_context():
        from app import db
        db.create_all()
    app.run()
