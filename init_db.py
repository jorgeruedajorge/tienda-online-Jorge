from app import app

from models import db


with app.app_context():

    # Crear tablas que todavía no existan
    db.create_all()

    print("Tablas creadas correctamente.")