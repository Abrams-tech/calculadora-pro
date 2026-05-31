import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

def generar_grafica_trayectoria(v0, angulo_rad, t_vuelo):
    try:
        g = 9.81
        t_vals = np.linspace(0, float(t_vuelo), 200)
        x_vals = v0 * np.cos(angulo_rad) * t_vals
        y_vals = (v0 * np.sin(angulo_rad) * t_vals) - (0.5 * g * t_vals**2)
        y_vals[-1] = 0

        plt.figure(figsize=(7, 4))
        plt.plot(x_vals, y_vals, color='#007bff', linewidth=3, label='Trayectoria del proyectil')
        plt.fill_between(x_vals, y_vals, color='#007bff', alpha=0.1)
        plt.axhline(0, color='black', linewidth=1)
        plt.grid(color='gray', linestyle='--', linewidth=0.3, alpha=0.7)
        plt.title("Movimiento Parabólico")
        plt.xlabel("Distancia (m)")
        plt.ylabel("Altura (m)")
        plt.legend()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        plt.close()
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None

def resolver_tiro_parabolico(velocidad_inicial_str, angulo_grados_str):
    try:
        v0 = float(velocidad_inicial_str)
        angulo_deg = float(angulo_grados_str)
        g = 9.81
        angulo_rad = np.radians(angulo_deg)
        
        v0x = v0 * np.cos(angulo_rad)
        v0y = v0 * np.sin(angulo_rad)
        t_altura_max = v0y / g
        altura_max = (v0y**2) / (2 * g)
        t_vuelo = 2 * t_altura_max
        alcance_max = v0x * t_vuelo
        
        pasos = [
            f"1. **Velocidad inicial:** $V_{{0x}}={v0x:.2f}$ m/s, $V_{{0y}}={v0y:.2f}$ m/s",
            f"2. **Tiempo a altura máxima:** $t={t_altura_max:.2f}$ s",
            f"3. **Altura Máxima:** $Y_{{max}}={altura_max:.2f}$ m",
            f"4. **Tiempo total de vuelo:** $t_{{total}}={t_vuelo:.2f}$ s",
            f"5. **Alcance Horizontal Máximo:** $X_{{max}}={alcance_max:.2f}$ m"
        ]
        
        grafica = generar_grafica_trayectoria(v0, angulo_rad, t_vuelo)
        resultado_resumido = f"Alcance: {alcance_max:.2f}m | Altura Máx: {altura_max:.2f}m | Tiempo Vuelo: {t_vuelo:.2f}s"
        
        return {"exito": True, "resultado_limpio": resultado_resumido, "pasos": pasos, "grafica": grafica}
    except Exception as e:
        return {"exito": False, "error": f"Error: {str(e)}"}