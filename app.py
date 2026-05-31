import os
import stripe
import sympy as sp
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

from motor_matematicas import resolver_calculo, resolver_sistema_ecuaciones, resolver_matriz
from motor_fisica import resolver_tiro_parabolico
from models import db, Usuario, Historial 
from sympy import sympify

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'llave_desarrollo_local')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plataforma_educativa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
CORREO_ADMIN = "m41abrams@gmail.com" 

@app.route('/')
def index(): return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if Usuario.query.filter_by(email=email).first():
            flash(f"El correo {email} ya está registrado.", "error")
            return redirect(url_for('registro'))
        nuevo_usuario = Usuario(email=email, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("¡Registro exitoso! Inicia sesión.", "success")
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.password == password: 
            session['usuario_id'] = usuario.id
            if usuario.email == CORREO_ADMIN: flash("¡Bienvenido Modo Creador! Acceso VIP.", "success")
            else: flash("Sesión iniciada.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Correo o contraseña incorrectos.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    usuario_actual = Usuario.query.get(session['usuario_id'])
    if not usuario_actual:
        session.clear()
        return redirect(url_for('login'))
    if usuario_actual.email == CORREO_ADMIN: usuario_actual.es_premium = True
    consultas_usuario = Historial.query.filter_by(usuario_id=usuario_actual.id).order_by(Historial.id.desc()).all()
    return render_template('dashboard.html', usuario=usuario_actual, historial=consultas_usuario)
# ... (aquí arriba están tus rutas de login, registro, dashboard, etc.) ...

# Pega la función traductora aquí:
def preparar_ecuacion_para_sympy(ecuacion_cruda):
    if not ecuacion_cruda:
        return ""
    eq = ecuacion_cruda.replace('^', '**')
    eq = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)
    eq = re.sub(r'(\d)\(', r'\1*(', eq)
    eq = re.sub(r'([a-zA-Z])\(', r'\1*(', eq)
    eq = re.sub(r'\)\(', r')*(', eq)
    eq = eq.replace(' ', '')
    return eq

# (Aquí abajo sigue tu ruta)
@app.route('/matematicas', methods=['GET', 'POST'])
def matematicas():
    # ... (aquí debe ir tu validación de if 'usuario_id' not in session... si la tienes)
    es_premium = True # Cambia esto por tu lógica real de usuario.es_premium

    if request.method == 'POST':
        materia = request.form.get('materia')
        ecuacion_cruda = request.form.get('ecuacion')
        
        # 1. Pasamos la ecuación por el traductor
        ecuacion_limpia = preparar_ecuacion_para_sympy(ecuacion_cruda)
        
        try:
            x = sp.Symbol('x')
            expr = sp.sympify(ecuacion_limpia)
            resultado_final = ""
            pasos = []
            
            if materia == "Álgebra (Ecuaciones)":
                soluciones = sp.solve(expr, x)
                resultado_final = f"$$x = {sp.latex(soluciones)}$$"
                pasos.append(f"1. Ecuación original: $${sp.latex(expr)} = 0$$")
                pasos.append(f"2. Solución: $${sp.latex(soluciones)}$$")

            elif materia == "Cálculo (Derivadas)":
                derivada = sp.diff(expr, x)
                resultado_final = f"$$f'(x) = {sp.latex(derivada)}$$"
                pasos.append(f"1. Función original: $$f(x) = {sp.latex(expr)}$$")
                pasos.append(f"2. Derivada: $$f'(x) = {sp.latex(derivada)}$$")

            elif materia == "Cálculo (Integrales)":
                integral = sp.integrate(expr, x)
                resultado_final = f"$$\\int f(x) dx = {sp.latex(integral)} + C$$"
                pasos.append(f"1. Función original: $$f(x) = {sp.latex(expr)}$$")
                pasos.append(f"2. Integral: $$\\int f(x) dx = {sp.latex(integral)} + C$$")

            return render_template('motor_matematicas.html', 
                                   resultado=resultado_final, 
                                   pasos=pasos, 
                                   es_premium=es_premium)
                                   
        except Exception as e:
            error_msg = f"No se pudo procesar la expresión '{ecuacion_cruda}'. Verifica la sintaxis."
            return render_template('motor_matematicas.html', error=error_msg, es_premium=es_premium)

    return render_template('motor_matematicas.html', es_premium=es_premium)
@app.route('/fisica', methods=['GET', 'POST'])

def fisica():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    usuario_actual = Usuario.query.get(session['usuario_id'])
    if not usuario_actual:
        session.clear()
        return redirect(url_for('login'))
    if usuario_actual.email == CORREO_ADMIN: usuario_actual.es_premium = True

    resultado, pasos, grafica, error = None, None, None, None

    if request.method == 'POST':
        velocidad = request.form.get('velocidad')
        angulo = request.form.get('angulo')
        respuesta = resolver_tiro_parabolico(velocidad, angulo)
        if respuesta['exito']:
            resultado_limpio = respuesta['resultado_limpio']
            if usuario_actual.es_premium: pasos, grafica = respuesta['pasos'], respuesta['grafica']
            else: pasos = ["Actualiza a Premium para ver la trayectoria gráfica."]
            db.session.add(Historial(usuario_id=usuario_actual.id, tema="Tiro Parabólico", problema=f"V={velocidad}, Ang={angulo}°", resultado=resultado_limpio))
            db.session.commit()
            resultado = resultado_limpio
        else: error = respuesta['error']

    return render_template('motor_fisica.html', resultado=resultado, pasos=pasos, grafica=grafica, error=error, es_premium=usuario_actual.es_premium)

@app.route('/checkout')
def checkout():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price_data': {'currency': 'mxn', 'product_data': {'name': 'Calculadora Pro Premium'}, 'unit_amount': 4900}, 'quantity': 1}],
            mode='payment', 
            success_url=url_for('pago_exitoso', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('dashboard', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e: return f"Error con Stripe: {str(e)}"

@app.route('/pago_exitoso')
def pago_exitoso():
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario:
            usuario.es_premium = True
            db.session.commit()
            flash("¡Pago exitoso! Funciones Premium activadas.", "success")
    return redirect(url_for('dashboard'))



# ... (aquí arriba terminan tus otras rutas como la de matemáticas o dashboard) ...

# ---> PEGA AQUÍ LA RUTA DEL HISTORIAL <---
@app.route('/historial')
def historial():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    usuario = Usuario.query.get(session['usuario_id'])
    
    if not usuario.es_premium:
        flash("El historial de problemas es una función exclusiva de la versión Premium.", "warning")
        return redirect(url_for('dashboard'))
        
    registros = Historial.query.filter_by(usuario_id=usuario.id).order_by(Historial.id.desc()).all()
    return render_template('historial.html', registros=registros, usuario=usuario)

# (Esto es lo que ya tienes al final de tu archivo)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)