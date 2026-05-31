from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Quitamos el nombre obligatorio para que coincida con el formulario de registro actual
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # Alineado con app.py
    es_premium = db.Column(db.Boolean, default=False) # Alineado con app.py
    historial = db.relationship('Historial', backref='usuario', lazy=True)

class Historial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(50), nullable=False) # Agregamos el tema (ej. Tiro Parabólico)
    problema = db.Column(db.String(200), nullable=False)
    resultado = db.Column(db.String(500), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)