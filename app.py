import os
import stripe
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

# Importamos las herramientas que acabamos de crear
from motor_matematicas import resolver_calculo, resolver_sistema_ecuaciones

# Importar tu base de datos y modelos (Asegúrate de tener esto en tu models.py)
from models import db, Usuario, Historial # Ajusta estos nombres si los llamaste distinto

# Cargar variables de entorno (Llaves de Stripe y Secret Key)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'llave_desarrollo_local')

# Configuración de Base de Datos SQLite (Local) / PostgreSQL (Producción en un futuro)
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
# EL NÚCLEO DEL SAAS: HERRAMIENTAS PREMIUM
# ==========================================

@app.route('/matematicas', methods=['GET', 'POST'])
def matematicas():
    # Verificamos si el usuario inició sesión (ajusta esto según tu sistema de login)
    if 'usuario_id' not in session:
        flash("Por favor inicia sesión para usar la calculadora.", "warning")
        return redirect(url_for('login')) # Asumiendo que tienes una ruta 'login'
        
    usuario_actual = Usuario.query.get(session['usuario_id'])
    
    resultado = None
    pasos = None
    grafica = None
    error = None

    if request.method == 'POST':
        # Recogemos los datos del formulario HTML
        operacion = request.form.get('operacion') # 'derivada', 'integral', 'limite', 'sistema'
        expresion = request.form.get('expresion')
        variable = request.form.get('variable', 'x')
        limite_val = request.form.get('limite_val', None)

        # 1. Llamamos a nuestro motor de cálculo
        if operacion in ['derivada', 'integral', 'limite']:
            respuesta = resolver_calculo(operacion, expresion, variable, limite_val)
        elif operacion == 'sistema':
            eq2 = request.form.get('expresion2') # Para sistemas necesitamos una segunda ecuación
            var2 = request.form.get('variable2', 'y')
            respuesta = resolver_sistema_ecuaciones(expresion, eq2, variable, var2)
        else:
            respuesta = {"exito": False, "error": "Operación no soportada."}

        # 2. Manejamos la respuesta
        if respuesta['exito']:
            resultado_limpio = respuesta['resultado_limpio']
            
            # EL MURO DE PAGO (PAYWALL)
            if usuario_actual.es_premium:
                # Si pagó, le damos el procedimiento completo y la gráfica
                pasos = respuesta['pasos']
                grafica = respuesta['grafica']
            else:
                # Si no es premium, solo mostramos el resultado final y un mensaje de bloqueo
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
# RUTAS DE PAGOS (STRIPE)
# ==========================================

@app.route('/checkout')
def checkout():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    try:
        # Creamos una sesión de pago en Stripe por $49 MXN
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': 'Suscripción Calculadora Pro Premium',
                        'description': 'Acceso total a procedimientos paso a paso y gráficas.',
                    },
                    'unit_amount': 4900, # Stripe maneja centavos (4900 = $49.00 MXN)
                },
                'quantity': 1,
            }],
            mode='payment', # Cambia a 'subscription' si vas a hacer cargos mensuales automáticos
            success_url=url_for('pago_exitoso', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('index', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return f"Error al conectar con Stripe: {str(e)}"

@app.route('/pago_exitoso')
def pago_exitoso():
    # Aquí verificamos que el pago se hizo y actualizamos la base de datos
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        usuario.es_premium = True
        db.session.commit()
        flash("¡Pago exitoso! Ahora tienes acceso a todas las funciones Premium.", "success")
    return redirect(url_for('matematicas'))

if __name__ == '__main__':
    # Creación de tablas de la DB si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)