# (Lo que ya tienes arriba en models.py)
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    es_premium = db.Column(db.Boolean, default=False)

# ---> PEGA ESTO JUSTO ABAJO <---
class Historial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    materia = db.Column(db.String(50), nullable=False)
    ecuacion = db.Column(db.String(100), nullable=False)
    resultado = db.Column(db.Text, nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('historiales', lazy=True))