import os
import stripe
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Historial
from motor_matematicas import resolver_ecuacion_lineal, calcular_derivada
from motor_fisica import resolver_tiro_parabolico, resolver_caida_libre, resolver_mrua
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'llave_super_secreta_123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///plataforma_educativa.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
db.init_app(app)

with app.app_context():
    db.create_all()

def aplicar_muro_de_pago(pasos):
    es_premium = False
    if session.get('usuario_id'):
        user = Usuario.query.get(session['usuario_id'])
        if user and user.is_premium:
            es_premium = True
            
    if not es_premium and len(pasos) > 2:
        return [pasos[0], "BLOQUEO_PREMIUM", pasos[-1]]
    return pasos

def registrar_historial(problema, resultado):
    if 'usuario_id' in session:
        try:
            item = Historial(problema=problema, resultado=resultado, usuario_id=session['usuario_id'])
            db.session.add(item)
            db.session.commit()
        except Exception:
            db.session.rollback()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        return render_template('registro.html')
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if Usuario.query.filter_by(email=email).first():
        return render_template('registro.html', error="El correo electrónico ya se encuentra en uso.")
        
    hashed_pwd = generate_password_hash(password, method='pbkdf2:sha256')
    nuevo_usuario = Usuario(nombre=nombre, email=email, password_hash=hashed_pwd)
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    session['usuario_id'] = nuevo_usuario.id
    session['usuario_nombre'] = nuevo_usuario.nombre
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form.get('email')
    password = request.form.get('password')
    usuario = Usuario.query.filter_by(email=email).first()
    
    if usuario and check_password_hash(usuario.password_hash, password):
        session['usuario_id'] = usuario.id
        session['usuario_nombre'] = usuario.nombre
        return redirect(url_for('index'))
    return render_template('login.html', error="Credenciales inválidas de acceso.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/historial')
def ver_historial():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('historial.html', registros=usuario.historial)

@app.route('/checkout')
def checkout():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': 'Acceso Premium Completo',
                        'description': 'Desbloqueo algorítmico de procedimientos avanzados paso a paso.',
                    },
                    'unit_amount': 4900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'pago-exitoso',
            cancel_url=request.host_url,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)

@app.route('/pago-exitoso')
def pago_exitoso():
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario:
            usuario.is_premium = True
            db.session.commit()
    return redirect(url_for('index'))

# --- RUTAS DE APIS (MOTORES) ---

@app.route('/api/resolver', methods=['POST'])
def resolver():
    datos = request.get_json()
    ecuacion = datos.get('ecuacion')
    pasos = resolver_ecuacion_lineal(ecuacion)
    if pasos and "Sintaxis" not in pasos[0]:
        registrar_historial(f"Álgebra: {ecuacion}", pasos[-1])
    return jsonify({"status": "success", "procedimiento": aplicar_muro_de_pago(pasos)})

@app.route('/api/matematicas/derivada', methods=['POST'])
def derivada():
    datos = request.get_json()
    funcion = datos.get('funcion')
    pasos = calcular_derivada(funcion)
    if pasos and "Sintaxis" not in pasos[0]:
        registrar_historial(f"Derivada: {funcion}", pasos[-1])
    return jsonify({"status": "success", "procedimiento": aplicar_muro_de_pago(pasos)})

@app.route('/api/fisica/parabolico', methods=['POST'])
def fisica_parabolico():
    datos = request.get_json()
    try:
        v0 = float(datos.get('velocidad', 0))
        angulo = float(datos.get('angulo', 0))
    except ValueError:
        return jsonify({"status": "error", "procedimiento": ["\\text{Estructura numérica inválida.}"]})
    pasos = resolver_tiro_parabolico(v0, angulo)
    registrar_historial(f"Tiro Parabólico (v0={v0}m/s, θ={angulo}°)", pasos[-1])
    return jsonify({"status": "success", "procedimiento": aplicar_muro_de_pago(pasos)})

@app.route('/api/fisica/caida-libre', methods=['POST'])
def fisica_caida():
    datos = request.get_json()
    try:
        h0 = float(datos.get('altura', 0))
    except ValueError:
        return jsonify({"status": "error", "procedimiento": ["\\text{Estructura numérica inválida.}"]})
    pasos = resolver_caida_libre(h0)
    registrar_historial(f"Caída Libre (h0={h0}m)", pasos[-1])
    return jsonify({"status": "success", "procedimiento": aplicar_muro_de_pago(pasos)})

@app.route('/api/fisica/mrua', methods=['POST'])
def fisica_mrua():
    datos = request.get_json()
    try:
        v0 = float(datos.get('v0', 0))
        a = float(datos.get('a', 0))
        t = float(datos.get('t', 0))
    except ValueError:
        return jsonify({"status": "error", "procedimiento": ["\\text{Ingresa solo números.}"]})
    
    pasos = resolver_mrua(v0, a, t)
    registrar_historial(f"MRUA (v0={v0}, a={a}, t={t})", pasos[-1])
    return jsonify({"status": "success", "procedimiento": aplicar_muro_de_pago(pasos)})

if __name__ == '__main__':
    app.run(debug=True)