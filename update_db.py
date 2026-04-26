from app import create_app, db
import os

app = create_app()
with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Done.")
