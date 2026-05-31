import math

def resolver_tiro_parabolico(v0, angulo_grados):
    procedimiento = []
    g = 9.81
    angulo_rad = math.radians(angulo_grados)
    
    v0x = round(v0 * math.cos(angulo_rad), 2)
    v0y = round(v0 * math.sin(angulo_rad), 2)
    t_total = round((2 * v0y) / g, 2)
    y_max = round((v0y**2) / (2 * g), 2)
    x_max = round(v0x * t_total, 2)
    
    procedimiento.append(f"\\text{{Datos: }} v_0 = {v0} \\text{{ m/s}}, \\theta = {angulo_grados}^\\circ")
    procedimiento.append(f"\\text{{1. Descomposición vectorial: }} v_{{0x}} = {v0x} \\text{{ m/s}}, v_{{0y}} = {v0y} \\text{{ m/s}}")
    procedimiento.append(f"\\text{{2. Tiempo total de trayectoria: }} t = \\frac{{2 v_{{0y}}}}{{g}} = {t_total} \\text{{ s}}")
    procedimiento.append(f"\\text{{3. Cúspide de altura }} (y_{{max}}): \\frac{{v_{{0y}}^2}}{{2g}} = {y_max} \\text{{ m}}")
    procedimiento.append(f"\\text{{4. Desplazamiento máximo horizontal }} (x_{{max}}): v_{{0x}} \\cdot t = {x_max} \\text{{ m}}")
    return procedimiento

def resolver_caida_libre(h0):
    procedimiento = []
    g = 9.81
    t = round(math.sqrt((2 * h0) / g), 2)
    vf = round(g * t, 2)
    
    procedimiento.append(f"\\text{{Datos: Altura de caída }} h_0 = {h0} \\text{{ m}}")
    procedimiento.append(f"\\text{{1. Ecuación de tiempo de caída: }} t = \\sqrt{{\\frac{{2h_0}}{{g}}}} = {t} \\text{{ s}}")
    procedimiento.append(f"\\text{{2. Velocidad terminal en el impacto: }} v_f = g \\cdot t = {vf} \\text{{ m/s}}")
    return procedimiento

def resolver_mrua(v0, a, t):
    procedimiento = []
    
    vf = round(v0 + (a * t), 2)
    d = round((v0 * t) + (0.5 * a * (t**2)), 2)
    
    procedimiento.append(f"\\text{{Datos: }} v_0 = {v0} \\text{{ m/s}}, a = {a} \\text{{ m/s}}^2, t = {t} \\text{{ s}}")
    procedimiento.append(f"\\text{{1. Velocidad final }} (v_f): v_0 + a \\cdot t = {v0} + ({a})({t}) = {vf} \\text{{ m/s}}")
    procedimiento.append(f"\\text{{2. Distancia recorrida }} (d): v_0 t + \\frac{{1}}{{2}}at^2 = ({v0})({t}) + 0.5({a})({t}^2) = {d} \\text{{ m}}")
    
    return procedimiento