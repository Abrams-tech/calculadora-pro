import matplotlib
matplotlib.use('Agg') # Fundamental para que el servidor de Render no colapse
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from sympy import symbols, sympify, diff, integrate, limit, Eq, solve, latex, lambdify

def generar_grafica_base64(funcion_sympy, variable, x_min=-10, x_max=10):
    """
    Convierte una expresión de SymPy en una gráfica PNG codificada en Base64.
    """
    try:
        # Convertir a una función que NumPy pueda entender rápidamente
        funcion_numerica = lambdify(variable, funcion_sympy, "numpy")
        
        # Generar los puntos de la gráfica
        x_vals = np.linspace(x_min, x_max, 400)
        y_vals = funcion_numerica(x_vals)
        
        # Crear la figura con diseño limpio y profesional
        plt.figure(figsize=(7, 4))
        plt.plot(x_vals, y_vals, color='#28a745', linewidth=2.5, label=f'f({variable})')
        plt.axhline(0, color='black', linewidth=0.8) # Eje X
        plt.axvline(0, color='black', linewidth=0.8) # Eje Y
        plt.grid(color='gray', linestyle='--', linewidth=0.3, alpha=0.7)
        plt.legend()
        plt.title("Representación Gráfica")
        
        # Guardar en memoria RAM sin abrir ventanas
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        plt.close()
        buffer.seek(0)
        
        # Convertir a texto para enviarlo al HTML
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return imagen_base64
    except Exception as e:
        # Si la función es muy compleja y no se puede graficar, evitamos que la app se caiga
        return None

def resolver_calculo(operacion, expresion_str, variable_str='x', valor_limite=None):
    """
    Motor central para Derivadas, Integrales y Límites.
    operacion debe ser: 'derivada', 'integral', o 'limite'
    """
    try:
        var = symbols(variable_str)
        expr = sympify(expresion_str) # Convierte el texto del usuario a matemáticas reales
        pasos = []
        grafica = None

        if operacion == 'derivada':
            resultado = diff(expr, var)
            pasos.append(f"1. Identificamos la función principal: $f({variable_str}) = {latex(expr)}$")
            pasos.append(f"2. Aplicamos las reglas de derivación respecto a la variable ${variable_str}$.")
            pasos.append(f"3. Simplificamos la expresión resultante.")
            pasos.append(f"**Resultado Final:** $\\frac{{d}}{{d{variable_str}}} = {latex(resultado)}$")
            grafica = generar_grafica_base64(expr, var)

        elif operacion == 'integral':
            resultado = integrate(expr, var)
            pasos.append(f"1. Planteamos la integral indefinida: $\\int ({latex(expr)}) \\, d{variable_str}$")
            pasos.append(f"2. Aplicamos los teoremas de integración correspondientes (directa, sustitución o por partes).")
            pasos.append(f"3. Evaluamos y agregamos la constante de integración.")
            pasos.append(f"**Resultado Final:** $\\int f({variable_str}) = {latex(resultado)} + C$")
            grafica = generar_grafica_base64(expr, var)

        elif operacion == 'limite':
            if not valor_limite:
                raise ValueError("Se requiere un valor al cual tiende el límite.")
            val = sympify(valor_limite)
            resultado = limit(expr, var, val)
            pasos.append(f"1. Planteamos el límite de la función: $\\lim_{{{variable_str} \\to {latex(val)}}} ({latex(expr)})$")
            pasos.append(f"2. Evaluamos la expresión sustituyendo el valor. Si hay indeterminación $\\frac{{0}}{{0}}$ o $\\frac{{\\infty}}{{\\infty}}$, aplicamos la regla de L'Hôpital o factorización.")
            pasos.append(f"**Resultado Final:** El límite converge a ${latex(resultado)}$")
            
            # Graficamos alrededor del punto de interés para que el alumno vea la convergencia
            if val.is_real:
                centro = float(val)
                grafica = generar_grafica_base64(expr, var, centro - 5, centro + 5)
            else:
                grafica = generar_grafica_base64(expr, var)

        return {
            "exito": True,
            "resultado_limpio": str(resultado),
            "pasos": pasos,
            "grafica": grafica
        }

    except Exception as e:
        return {"exito": False, "error": f"Error matemático: Revisa la sintaxis de tu expresión. Detalles: {str(e)}"}

def resolver_sistema_ecuaciones(eq1_str, eq2_str, var1_str='x', var2_str='y'):
    """
    Resuelve sistemas de ecuaciones de 2x2.
    """
    try:
        v1, v2 = symbols(f'{var1_str} {var2_str}')
        # Igualamos las expresiones a cero internamente para que SymPy las resuelva
        eq1 = Eq(sympify(eq1_str), 0)
        eq2 = Eq(sympify(eq2_str), 0)
        
        resultado = solve((eq1, eq2), (v1, v2))
        pasos = []
        
        pasos.append(f"1. Planteamos el sistema de ecuaciones igualado a cero:")
        pasos.append(f"   Ecuación 1: ${latex(eq1)}$")
        pasos.append(f"   Ecuación 2: ${latex(eq2)}$")
        pasos.append(f"2. Aplicamos un método de resolución (Sustitución, Igualación o Eliminación).")
        
        if not resultado:
            pasos.append("**Resultado Final:** El sistema no tiene solución real o las líneas son paralelas.")
        else:
            res_v1 = resultado.get(v1, "No definido")
            res_v2 = resultado.get(v2, "No definido")
            pasos.append(f"**Resultado Final:** ${var1_str} = {latex(res_v1)}$, ${var2_str} = {latex(res_v2)}$")

        return {
            "exito": True,
            "resultado_limpio": str(resultado),
            "pasos": pasos,
            "grafica": None # En el futuro se pueden graficar las dos rectas que se cruzan
        }
    except Exception as e:
         return {"exito": False, "error": f"Error al resolver el sistema. Asegúrate de despejar todo hacia un lado. Detalles: {str(e)}"}