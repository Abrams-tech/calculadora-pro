import os
import stripe
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

# Importamos las herramientas de ambos motores lógicos
from motor_matematicas import resolver_calculo, resolver_sistema_ecuaciones
from motor_fisica import resolver_tiro_parabolico

# Importar tu base de datos y modelos (Asegúrate de tener esto en tu models.py)
from models import db, Usuario, Historial 

# Cargar variables de entorno (Llaves de Stripe y Secret Key)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'llave_desarrollo_local')

# Configuración de Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/plataforma_educativa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Configuración de Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')


# ==========================================
# RUTAS PRINCIPALES Y AUTENTICACIÓN
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

# (Aquí irían tus rutas de /login y /registro que ya tienes configuradas)


# ==========================================
# MOTOR DE MATEMÁTICAS
# ==========================================

@app.route('/matematicas', methods=['GET', 'POST'])
def matematicas():
    # Verificamos si el usuario inició sesión
    if 'usuario_id' not in session:
        flash("Por favor inicia sesión para usar la calculadora.", "warning")
        return redirect(url_for('login')) 
        
    usuario_actual = Usuario.query.get(session['usuario_id'])
    
    # 🌟 TU PASE VIP DE CREADOR 🌟
    # ¡IMPORTANTE! Cambia este texto por el correo con el que te vas a registrar en tu app
    if usuario_actual.email == "m41abrams@.com":
        usuario_actual.es_premium = True

    resultado = None
    pasos = None
    grafica = None
    error = None

    if request.method == 'POST':
        operacion = request.form.get('operacion') 
        expresion = request.form.get('expresion')
        variable = request.form.get('variable', 'x')
        limite_val = request.form.get('limite_val', None)

        if operacion in ['derivada', 'integral', 'limite']:
            respuesta = resolver_calculo(operacion, expresion, variable, limite_val)
        elif operacion == 'sistema':
            eq2 = request.form.get('expresion2') 
            var2 = request.form.get('variable2', 'y')
            respuesta = resolver_sistema_ecuaciones(expresion, eq2, variable, var2)
        else:
            respuesta = {"exito": False, "error": "Operación no soportada."}

        if respuesta['exito']:
            resultado_limpio = respuesta['resultado_limpio']
            
            # EL MURO DE PAGO (PAYWALL)
            if usuario_actual.es_premium:
                pasos = respuesta['pasos']
                grafica = respuesta['grafica']
            else:
                pasos = ["Para ver el procedimiento analítico paso a paso y la gráfica interactiva, actualiza a Premium."]
            
            # Guardamos la consulta en el historial del usuario
            nuevo_registro = Historial(
                usuario_id=usuario_actual.id,
                tema=operacion,
                problema=expresion,
                resultado=resultado_limpio
            )
            db.session.add(nuevo_registro)
            db.session.commit()
            
            resultado = resultado_limpio
        else:
            error = respuesta['error']

    return render_template('motor_matematicas.html', 
                           resultado=resultado, 
                           pasos=pasos, 
                           grafica=grafica, 
                           error=error,
                           es_premium=usuario_actual.es_premium)


# ==========================================
# MOTOR DE FÍSICA
# ==========================================

@app.route('/fisica', methods=['GET', 'POST'])
def fisica():
    if 'usuario_id' not in session:
        flash("Por favor inicia sesión para usar el simulador.", "warning")
        return redirect(url_for('login'))
        
    usuario_actual = Usuario.query.get(session['usuario_id'])
    
    # 🌟 TU PASE VIP DE CREADOR 🌟
    # ¡IMPORTANTE! Cambia este texto por el correo con el que te vas a registrar en tu app
    if usuario_actual.email == "m41abrams@gmail.com":
        usuario_actual.es_premium = True

    resultado = None
    pasos = None
    grafica = None
    error = None

    if request.method == 'POST':
        velocidad = request.form.get('velocidad')
        angulo = request.form.get('angulo')
        
        respuesta = resolver_tiro_parabolico(velocidad, angulo)
        
        if respuesta['exito']:
            resultado_limpio = respuesta['resultado_limpio']
            
            if usuario_actual.es_premium:
                pasos = respuesta['pasos']
                grafica = respuesta['grafica']
            else:
                pasos = ["Para ver el desglose analítico de las ecuaciones vectoriales paso a paso y la trayectoria gráfica del proyectil, actualiza a Premium."]
            
            # Guardamos la consulta en el historial del usuario
            nuevo_registro = Historial(
                usuario_id=usuario_actual.id,
                tema="Tiro Parabólico",
                problema=f"V={velocidad}m/s, Ang={angulo}°",
                resultado=resultado_limpio
            )
            db.session.add(nuevo_registro)
            db.session.commit()

            resultado = resultado_limpio
        else:
            error = respuesta['error']

    return render_template('motor_fisica.html', 
                           resultado=resultado, 
                           pasos=pasos, 
                           grafica=grafica, 
                           error=error,
                           es_premium=usuario_actual.es_premium)


# ==========================================
# RUTAS DE PAGOS (STRIPE)
# ==========================================

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
                        'name': 'Suscripción Calculadora Pro Premium',
                        'description': 'Acceso total a procedimientos paso a paso y gráficas.',
                    },
                    'unit_amount': 4900, # 4900 centavos = $49.00 MXN
                },
                'quantity': 1,
            }],
            mode='payment', 
            success_url=url_for('pago_exitoso', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('index', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return f"Error al conectar con Stripe: {str(e)}"

@app.route('/pago_exitoso')
def pago_exitoso():
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        usuario.es_premium = True
        db.session.commit()
        flash("¡Pago exitoso! Ahora tienes acceso a todas las funciones Premium.", "success")
    return redirect(url_for('matematicas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)