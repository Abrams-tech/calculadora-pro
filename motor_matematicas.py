import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from sympy import symbols, sympify, diff, integrate, limit, Eq, solve, latex, lambdify, Matrix

def generar_grafica_base64(funcion_sympy, variable, x_min=-10, x_max=10):
    try:
        funcion_numerica = lambdify(variable, funcion_sympy, "numpy")
        x_vals = np.linspace(x_min, x_max, 400)
        y_vals = funcion_numerica(x_vals)
        
        plt.figure(figsize=(7, 4))
        plt.plot(x_vals, y_vals, color='#28a745', linewidth=2.5, label=f'f({variable})')
        plt.axhline(0, color='black', linewidth=0.8)
        plt.axvline(0, color='black', linewidth=0.8)
        plt.grid(color='gray', linestyle='--', linewidth=0.3, alpha=0.7)
        plt.legend()
        plt.title("Representación Gráfica")
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        plt.close()
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None

def resolver_calculo(operacion, expresion_str, variable_str='x', valor_limite=None):
    try:
        var = symbols(variable_str)
        expr = sympify(expresion_str)
        pasos = []
        grafica = None

        if operacion == 'derivada':
            resultado = diff(expr, var)
            pasos.append(f"1. Función principal: $f({variable_str}) = {latex(expr)}$")
            pasos.append(f"2. Aplicamos reglas de derivación.")
            pasos.append(f"**Resultado Final:** $\\frac{{d}}{{d{variable_str}}} = {latex(resultado)}$")
            grafica = generar_grafica_base64(expr, var)

        elif operacion == 'integral':
            resultado = integrate(expr, var)
            pasos.append(f"1. Integral indefinida: $\\int ({latex(expr)}) \\, d{variable_str}$")
            pasos.append(f"2. Evaluamos y agregamos constante.")
            pasos.append(f"**Resultado Final:** $\\int f({variable_str}) = {latex(resultado)} + C$")
            grafica = generar_grafica_base64(expr, var)

        elif operacion == 'limite':
            val = sympify(valor_limite)
            resultado = limit(expr, var, val)
            pasos.append(f"1. Límite: $\\lim_{{{variable_str} \\to {latex(val)}}} ({latex(expr)})$")
            pasos.append(f"**Resultado Final:** Converge a ${latex(resultado)}$")
            centro = float(val) if val.is_real else 0
            grafica = generar_grafica_base64(expr, var, centro - 5, centro + 5)

        return {"exito": True, "resultado_limpio": str(resultado), "pasos": pasos, "grafica": grafica}
    except Exception as e:
        return {"exito": False, "error": f"Error matemático: {str(e)}"}

def resolver_sistema_ecuaciones(eq1_str, eq2_str, var1_str='x', var2_str='y'):
    try:
        v1, v2 = symbols(f'{var1_str} {var2_str}')
        eq1 = Eq(sympify(eq1_str), 0)
        eq2 = Eq(sympify(eq2_str), 0)
        resultado = solve((eq1, eq2), (v1, v2))
        pasos = [
            f"1. Sistema igualado a cero: ${latex(eq1)}$ y ${latex(eq2)}$",
            f"2. Aplicamos método analítico."
        ]
        if not resultado:
            pasos.append("**Resultado:** Sin solución real.")
        else:
            pasos.append(f"**Resultado Final:** ${var1_str} = {latex(resultado.get(v1))}$, ${var2_str} = {latex(resultado.get(v2))}$")
        return {"exito": True, "resultado_limpio": str(resultado), "pasos": pasos, "grafica": None}
    except Exception as e:
         return {"exito": False, "error": f"Error: {str(e)}"}

def resolver_matriz(matriz_datos, operacion_matriz):
    try:
        M = Matrix(matriz_datos)
        pasos = []
        pasos.append(f"1. **Matriz original:** $A = {latex(M)}$")
        
        if operacion_matriz == 'determinante':
            det = M.det()
            pasos.append(f"2. Aplicamos expansión para calcular el determinante.")
            pasos.append(f"**Resultado Final:** $\\det(A) = {latex(det)}$")
            resultado = f"Determinante = {det}"
            
        elif operacion_matriz == 'inversa':
            det = M.det()
            if det == 0:
                return {"exito": False, "error": "La matriz no tiene inversa porque su determinante es 0."}
            inv = M.inv()
            pasos.append(f"2. Calculamos el determinante: $\\det(A) = {latex(det)}$")
            pasos.append(f"3. Aplicamos: $A^{{-1}} = \\frac{{1}}{{\\det(A)}} \\times \\text{{Adj}}(A)$")
            pasos.append(f"**Resultado Final:** $A^{{-1}} = {latex(inv)}$")
            resultado = "Matriz Inversa Calculada (Ver pasos en PDF)"
            
        return {"exito": True, "resultado_limpio": str(resultado), "pasos": pasos, "grafica": None}
    except Exception as e:
        return {"exito": False, "error": f"Error matricial: {str(e)}"}