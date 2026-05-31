from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    historial = db.relationship('Historial', backref='usuario', lazy=True)

class Historial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problema = db.Column(db.String(200), nullable=False)
    resultado = db.Column(db.String(500), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)