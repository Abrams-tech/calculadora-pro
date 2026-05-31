import sympy as sp

def resolver_ecuacion_lineal(ecuacion_str):
    try:
        x = sp.symbols('x')
        if '=' in ecuacion_str:
            izq, der = ecuacion_str.split('=')
            eq = sp.Eq(sp.sympify(izq), sp.sympify(der))
        else:
            eq = sp.Eq(sp.sympify(ecuacion_str), 0)
        
        procedimiento = []
        procedimiento.append(f"\\text{{Ecuación inicial: }} {sp.latex(eq)}")
        
        eq_simplificada = sp.simplify(eq.lhs - eq.rhs)
        procedimiento.append(f"\\text{{Simplificación matemática: }} {sp.latex(eq_simplificada)} = 0")
        
        solucion = sp.solve(eq, x)
        if len(solucion) == 0:
            procedimiento.append("\\text{Sin solución en el campo real.}")
        else:
            procedimiento.append(f"\\text{{Resultado desglosado: }} x = {sp.latex(solucion[0])}")
        
        return procedimiento
    except Exception:
        return ["\\text{Sintaxis incorrecta. Intenta estructurar la expresión como: 3*x - 12 = 0.}"]

def calcular_derivada(funcion_str):
    try:
        x = sp.symbols('x')
        expr = sp.sympify(funcion_str)
        
        procedimiento = []
        procedimiento.append(f"\\text{{Función a derivar: }} f(x) = {sp.latex(expr)}")
        
        derivada = sp.diff(expr, x)
        
        procedimiento.append("\\text{Aplicando las reglas de derivación...}")
        procedimiento.append(f"\\text{{Resultado: }} f'(x) = {sp.latex(derivada)}")
        
        return procedimiento
    except Exception:
        return ["\\text{Sintaxis incorrecta. Intenta escribirla así: 3*x**2 + 5*x - 2}"]