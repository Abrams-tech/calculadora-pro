import matplotlib
matplotlib.use('Agg') # Evita que el servidor colapse
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

def generar_grafica_trayectoria(v0, angulo_rad, t_vuelo):
    """
    Genera la curva parabólica del proyectil basándose en la velocidad y el ángulo.
    """
    try:
        g = 9.81
        # Generar puntos de tiempo desde 0 hasta el tiempo de vuelo
        t_vals = np.linspace(0, float(t_vuelo), 200)
        
        # Fórmulas de posición en X y Y
        x_vals = v0 * np.cos(angulo_rad) * t_vals
        y_vals = (v0 * np.sin(angulo_rad) * t_vals) - (0.5 * g * t_vals**2)
        
        # Asegurar que el último punto de Y sea exactamente 0 (suelo)
        y_vals[-1] = 0

        # Crear gráfico estilizado
        plt.figure(figsize=(7, 4))
        plt.plot(x_vals, y_vals, color='#007bff', linewidth=3, label='Trayectoria del proyectil')
        plt.fill_between(x_vals, y_vals, color='#007bff', alpha=0.1) # Sombra bajo la curva
        
        plt.axhline(0, color='black', linewidth=1)
        plt.grid(color='gray', linestyle='--', linewidth=0.3, alpha=0.7)
        plt.title("Gráfica de Trayectoria (Movimiento Parabólico)", fontsize=12, fontweight='bold')
        plt.xlabel("Distancia Horizontal (m)")
        plt.ylabel("Altura (m)")
        plt.legend()
        
        # Guardar en memoria RAM
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        plt.close()
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None

def resolver_tiro_parabolico(velocidad_inicial_str, angulo_grados_str):
    """
    Calcula los componentes, altura máxima, alcance y tiempo de vuelo paso a paso.
    """
    try:
        v0 = float(velocidad_inicial_str)
        angulo_deg = float(angulo_grados_str)
        g = 9.81
        
        # Convertir ángulo a radianes para las funciones de Python
        angulo_rad = np.radians(angulo_deg)
        
        # Componentes de la velocidad
        v0x = v0 * np.cos(angulo_rad)
        v0y = v0 * np.sin(angulo_rad)
        
        # Cálculos físicos oficiales
        t_altura_max = v0y / g
        altura_max = (v0y**2) / (2 * g)
        t_vuelo = 2 * t_altura_max
        alcance_max = v0x * t_vuelo
        
        # Estructurar el procedimiento analítico paso a paso
        pasos = [
            f"1. **Componentes de la velocidad inicial:**",
            f"   * $V_{{0x}} = V_0 \\cdot \\cos(\\theta) = {v0} \\cdot \\cos({angulo_deg}^\\circ) = {v0x:.2f}\\,\\text{{m/s}}$",
            f"   * $V_{{0y}} = V_0 \\cdot \\sin(\\theta) = {v0} \\cdot \\sin({angulo_deg}^\\circ) = {v0y:.2f}\\,\\text{{m/s}}$",
            f"2. **Tiempo para alcanzar la altura máxima ($t_{{hmax}}$):**",
            f"   * $t = \\frac{{V_{{0y}}}}{{g}} = \\frac{{{v0y:.2f}}}{{{g}}} = {t_altura_max:.2f}\\,\\text{{segundos}}$",
            f"3. **Altura Máxima alcanzada ($Y_{{max}}$):**",
            f"   * $Y_{{max}} = \\frac{{V_{{0y}}^2}}{{2g}} = \\frac{{{v0y:.2f}^2}}{{2 \\cdot {g}}} = {altura_max:.2f}\\,\\text{{metros}}$",
            f"4. **Tiempo total de vuelo ($t_{{total}}$):**",
            f"   * $t_{{total}} = 2 \\cdot t_{{hmax}} = 2 \\cdot {t_altura_max:.2f} = {t_vuelo:.2f}\\,\\text{{segundos}}$",
            f"5. **Alcance Horizontal Máximo ($X_{{max}}$):**",
            f"   * $X_{{max}} = V_{{0x}} \\cdot t_{{total}} = {v0x:.2f} \\cdot {t_vuelo:.2f} = {alcance_max:.2f}\\,\\text{{metros}}$"
        ]
        
        # Generar su respectiva gráfica
        grafica = generar_grafica_trajectory(v0, angulo_rad, t_vuelo)
        
        resultado_resumido = f"Alcance: {alcance_max:.2f}m | Altura Máx: {altura_max:.2f}m | Tiempo Vuelo: {t_vuelo:.2f}s"
        
        return {
            "exito": True,
            "resultado_limpio": resultado_resumido,
            "pasos": pasos,
            "grafica": grafica
        }
    except Exception as e:
        return {"exito": False, "error": f"Error en los datos de entrada. Asegúrate de usar solo números. Detalles: {str(e)}"}