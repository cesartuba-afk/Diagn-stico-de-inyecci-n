"""
Asistente de diagnóstico de inyección (PyWebIO + Pydroid3)
- Paneles grises translúcidos para textos sobre la imagen (intro/acciones/descarga)
- Emojis en UI
- Evaluación completa + puntaje + acciones
- Informe TXT descargable
- Botón flotante WhatsApp (verde)
- Auto abre navegador
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple
import urllib.parse

from pywebio import start_server
from pywebio.input import input, radio, input_group, checkbox, textarea, NUMBER
from pywebio.output import put_markdown, put_table, put_text, put_file, put_html, clear

# -----------------------------
# Referencias (rangos típicos)
# -----------------------------
REFS: Dict[str, Tuple[float, float]] = {
    "nafta_mpi_presion": (3.0, 4.0),
    "gdi_baja": (4.0, 6.0),
    "gdi_riel_arranque": (40, 60),
    "gdi_riel_marcha": (50, 150),
    "diesel_arranque": (250, 300),
    "diesel_ralenti": (250, 350),
    "vacuo_ralenti_inhg": (18, 22),
    "contrapresion_psi_2500": (0, 2),
    "bateria_repo_v": (12.4, 12.8),
    "bateria_arranque_min": (9.6, 99),       # sólo mínimo importa
    "alternador_v": (13.8, 14.5),
}

# -----------------------------
# Imagen de fondo (Unsplash)
# -----------------------------
UNSPLASH_MAIN = "https://unsplash.com/photos/V2BBsqfOp8c/download?force=true&w=1920"

# -----------------------------
# CSS visual
# -----------------------------
def put_theme_css():
    put_html(f"""
    <style>
        body {{
            background:
                linear-gradient(rgba(0,0,0,0.52), rgba(0,0,0,0.52)),
                url('{UNSPLASH_MAIN}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: Arial, Helvetica, sans-serif;
            min-height: 100vh;
            color: #111;
        }}
        .webio-container {{
            background: rgba(255,255,255,0.92) !important;
            border-radius: 14px;
            padding: 20px;
            margin: 24px auto;
            max-width: 980px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.35);
            color: #111 !important;
        }}
        .webio-output {{
            background: rgba(255,255,255,0.96) !important;
            color: #111 !important;
            padding: 12px !important;
            border-radius: 10px !important;
            margin-bottom: 12px !important;
            border: 1px solid rgba(0,0,0,0.16) !important;
        }}
        h1, .hero-title {{
            color: #fff !important;
            text-shadow: 1px 1px 4px rgba(0,0,0,.85);
            margin: 4px 0 10px 0;
        }}
        h2 {{ color:#111 !important; margin-top:10px; }}
        input[type="text"], input[type="number"], textarea, select {{
            background: #fff !important;
            color: #111 !important;
            border-radius: 8px !important;
            border: 1px solid rgba(0,0,0,0.28) !important;
        }}
        table {{
            background: rgba(255,255,255,0.96) !important;
            color: #111 !important;
            border-radius: 10px !important;
        }}
        th, td {{ color:#111 !important; border-color: rgba(0,0,0,.22) !important; }}

        /* Paneles */
        .section-card{{
            background: rgba(255,255,255,0.94);
            color:#111 !important;
            border:1px solid rgba(0,0,0,0.15);
            border-radius:12px;
            padding:14px 16px;
            margin:14px 0;
            box-shadow:0 8px 22px rgba(0,0,0,0.20);
        }}
        /* NUEVO: panel gris translúcido para textos sobre la foto */
        .glass-gray {{
            background: rgba(33,37,41,0.55);      /* gris oscuro translúcido */
            color: #fff !important;
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 12px;
            padding: 12px 16px;
            margin: 12px 0;
            box-shadow: 0 8px 22px rgba(0,0,0,.35);
            text-shadow: 0 1px 2px rgba(0,0,0,.6);
        }}
        .glass-gray h3, .glass-gray h4, .glass-gray p, .glass-gray a {{
            color:#fff !important;
        }}

        .badge {{ display:inline-block; padding:3px 8px; border-radius:999px; color:#fff; font-weight:700; font-size:12px }}
        .ok   {{ background:#22c55e; }}
        .warn {{ background:#f59e0b; }}
        .crit {{ background:#ef4444; }}
        .btn-primary {{ background-color:#2d6cdf !important; color:#fff !important; }}
        .btn-warning {{ background-color:#f5d142 !important; color:#111 !important; }}

        /* Botón flotante WhatsApp */
        .wa-fab {{
            position: fixed; right: 16px; bottom: 16px; z-index: 9999;
            width: 60px; height: 60px; border-radius: 50%;
            background-color: #25D366 !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            display: flex; align-items: center; justify-content: center;
            transition: transform .08s ease-in-out;
        }}
        .wa-fab:hover {{ transform: scale(1.08); }}
        .wa-fab svg {{ width: 34px; height: 34px; fill: #fff; }}
    </style>
    """)

# -----------------------------
# Botón WhatsApp
# -----------------------------
def put_whatsapp_button(phone_e164: str, default_msg: str = "Hola, tengo una consulta sobre el diagnóstico"):
    msg = urllib.parse.quote(default_msg)
    wa_url = f"https://wa.me/{phone_e164}?text={msg}"
    put_html(f"""
    <a class="wa-fab" href="{wa_url}" target="_blank" rel="noopener" aria-label="WhatsApp">
      <svg viewBox="0 0 32 32" aria-hidden="true">
        <path d="M19.1 17.6c-.3-.1-1.6-.8-1.8-.9s-.4-.1-.5.1-.6.9-.8 1c-.1.1-.3.1-.6 0-1.5-.6-2.5-1.3-3.4-3-.3-.5.3-.5.8-1.7.1-.1 0-.3 0-.5s-.5-1.2-.7-1.6c-.2-.4-.4-.3-.6-.3h-.5c-.2 0-.5.1-.7.3-.8.8-1.1 1.9-1.1 3 .0 1.8 1.3 3.6 3.1 4.7 2.1 1.3 3.6 1.5 4.3 1.3.7-.1 1.6-.7 1.8-1.3.2-.6.2-1.1.2-1.2 0-.1-.1-.1-.3-.2zM16 3C9.4 3 4 8.4 4 15c0 2.5.8 4.8 2.1 6.7L5 29l7.5-1.9c1.8 1 3.8 1.6 6 1.6 6.6 0 12-5.4 12-12S22.6 3 16 3zm0 22.1c-2.1 0-4-.6-5.6-1.7l-.4-.2-4.5 1.1 1.2-4.4-.3-.5C5.5 17.6 5 16.3 5 15 5 9.9 9.1 5.9 14.2 5.9c5.1 0 9.2 4 9.2 9.1.1 5.1-4 9.1-7.4 10.1z"/>
      </svg>
    </a>
    """)

# -----------------------------
# Utilidades de evaluación
# -----------------------------
def ref_str(clave: str) -> str:
    lo, hi = REFS[clave]
    if clave == "bateria_arranque_min":
        return f">= {lo}"
    if clave == "contrapresion_psi_2500":
        return f"<= {hi}"
    return f"{lo}-{hi}"

def en_rango(valor: float, clave_ref: str):
    lo, hi = REFS[clave_ref]
    if clave_ref == "bateria_arranque_min":
        ok = valor >= lo
        return ok, ("✅ OK" if ok else "⚠️ BAJO")
    if clave_ref == "contrapresion_psi_2500":
        ok = valor <= hi
        return ok, ("✅ OK" if ok else "❌ ALTO")
    ok = lo <= valor <= hi
    return ok, ("✅ OK" if ok else ("⚠️ BAJO" if valor < lo else "❌ ALTO"))

def ponderacion(key: str) -> int:
    pesos = {
        "v_bat_arr": 25, "cr_arr": 25,
        "pbaja": 20, "gdi_arr": 20, "mpi_pr": 20,
        "cr_idle": 15, "gdi_run": 10,
        "vac_inhg": 10, "contra_psi": 15,
        "v_alt": 10, "v_bat_repo": 5,
    }
    return pesos.get(key, 5)

def evaluar_pack(pack: Dict[str, float], tipo: str):
    desc = {
        "v_bat_repo": "🔋 Batería en reposo (V)",
        "v_bat_arr": "🔑 Batería en arranque (V)",
        "v_alt": "⚡ Alternador a ralenti (V)",
        "vac_inhg": "🌬️ Vacío ralenti (inHg)",
        "contra_psi": "💨 Contrapresión 2500 rpm (psi)",
        "cr_arr": "🛠️ CR arranque (bar)",
        "cr_idle": "🛠️ CR ralenti (bar)",
        "pbaja": "⛽ Presión baja (bar)",
        "gdi_arr": "⚙️ GDI riel arranque (bar)",
        "gdi_run": "⚙️ GDI riel marcha (bar)",
        "mpi_pr": "⛽ Presión riel MPI (bar)",
    }
    kref = {
        "v_bat_repo": "bateria_repo_v",
        "v_bat_arr": "bateria_arranque_min",
        "v_alt": "alternador_v",
        "vac_inhg": "vacuo_ralenti_inhg",
        "contra_psi": "contrapresion_psi_2500",
        "cr_arr": "diesel_arranque",
        "cr_idle": "diesel_ralenti",
        "pbaja": "gdi_baja",
        "gdi_arr": "gdi_riel_arranque",
        "gdi_run": "gdi_riel_marcha",
        "mpi_pr": "nafta_mpi_presion",
    }

    hall: List[Dict[str, Any]] = []
    score = 0
    for k, v in pack.items():
        if k not in kref or v is None:
            continue
        ok, estado = en_rango(v, kref[k])
        if not ok:
            score += ponderacion(k)
        hall.append({
            "key": k,
            "label": desc.get(k, k),
            "valor": str(v),
            "ref": ref_str(kref[k]),
            "estado": estado,
            "ok": ok,
        })
    score = max(0, min(100, score))
    return hall, score

def construir_diagnostico(h: List[Dict[str, Any]], score: int, tipo: str):
    p = [x for x in h if not x["ok"]]
    acciones: List[str] = []
    causas: List[str] = []
    def has(key): return any(x for x in p if x["key"] == key)

    # Eléctrico
    if has("v_bat_arr"):
        causas.append("🔋 Batería baja en arranque")
        acciones.append("Probar batería bajo carga y revisar caídas de tensión del arranque")
    if has("v_alt"):
        causas.append("⚡ Alternador fuera de rango")
        acciones.append("Probar alternador/regulador y conexiones")

    # Aire/Escape
    if has("vac_inhg"):
        causas.append("🌬️ Vacío bajo en ralenti")
        acciones.append("Revisar fugas de admisión o compresión (humo, compresión/leak-down)")
    if has("contra_psi"):
        causas.append("💨 Contrapresión de escape alta")
        acciones.append("Revisar catalizador/escape por obstrucción")

    # Combustible
    if "Diesel" in tipo:
        if has("cr_arr"):
            causas.append("🛠️ Presión CR insuficiente en arranque")
            acciones.append("Revisar circuito de baja, IMV/SCV, retornos e inyectores")
        if has("cr_idle"):
            causas.append("🛠️ Presión CR fuera de rango en ralenti")
            acciones.append("Comparar presión objetivo vs real; evaluar fugas/controles")
    elif "GDI" in tipo:
        if has("pbaja"):
            causas.append("⛽ Presión de baja insuficiente")
            acciones.append("Revisar bomba de tanque, filtro y caudal")
        if has("gdi_arr"):
            causas.append("⚙️ Presión GDI insuficiente en arranque")
            acciones.append("Evaluar bomba de alta, válvula/SCV y fugas")
        if has("gdi_run"):
            causas.append("⚙️ Presión GDI fuera de rango en marcha")
            acciones.append("Correlacionar con objetivo; revisar restricciones")
    else:
        if has("mpi_pr"):
            causas.append("⛽ Presión MPI fuera de rango")
            acciones.append("Revisar bomba/filtro/regulador; prueba de presión sostenida")

    if not p:
        diag = "Parámetros en rango. Si persiste el síntoma, continuar con pruebas específicas."
    else:
        diag = "; ".join(causas)

    if score >= 70:
        diag = "🟥 **CRÍTICO**: " + diag
        nivel = "crit"
    elif score >= 40:
        diag = "🟧 **MODERADO**: " + diag
        nivel = "warn"
    else:
        diag = "🟩 **LEVE**: " + diag
        nivel = "ok"
    return diag, acciones, nivel

def build_txt(info: Dict[str, Any]) -> bytes:
    v = info.get("vehiculo", {}) or {}
    L: List[str] = []
    L.append("INFORME DE DIAGNOSTICO DE INYECCION")
    L.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L.append("")
    L.append("Vehiculo")
    L.append(f"  Marca/Modelo: {str(v.get('marca') or '')}")
    L.append(f"  Anio/Motor: {str(v.get('anio_motor') or '')}")
    L.append(f"  Patente/VIN: {str(v.get('patente') or '')}")
    L.append(f"  Combustible: {str(v.get('combustible') or '')}")
    L.append("")
    L.append("Mediciones")
    for m in info.get("mediciones", []):
        L.append(f"  - {m}")
    L.append("")
    L.append("Diagnostico")
    L.append(f"  {info.get('diagnostico_preliminar','')}")
    L.append("")
    L.append("Acciones sugeridas")
    for a in info.get("acciones", []):
        L.append(f"  - {a}")
    return ("\n".join(L)).encode("utf-8")

# -----------------------------
# Asistente (flujo)
# -----------------------------
def wizard():
    clear()
    put_theme_css()
    put_whatsapp_button("5491172379474", "Hola, vengo del asistente de diagnóstico")

    put_markdown("# 🔧 Asistente de diagnóstico de inyección 🚗")
    # Intro en panel gris translúcido
    put_html('<div class="glass-gray"><p>Ingresá los datos para generar un diagnóstico preliminar.</p></div>')

    # Datos vehículo
    datos = input_group("📋 Datos del vehículo", [
        input("🚙 Marca y modelo", name="marca"),
        input("📅 Año / Motor", name="anio_motor"),
        input("🔑 Patente / VIN (opcional)", name="patente"),
        radio("⛽ Combustible", options=["Nafta MPI", "Nafta GDI", "Diesel Common-Rail"], name="combustible"),
    ]) or {}

    # Síntomas y DTC (opcionales)
    sintomas_sel = checkbox("🧩 Síntomas presentes (opcional)", options=[
        "Arranque difícil en frío",
        "Ralenti inestable",
        "Tironeos en aceleración",
        "Pérdida de potencia en alta",
        "Consumo elevado / mezcla rica",
        "Humo (diesel)",
        "No arranca",
    ])
    dtc_txt = textarea("💾 DTC y Freeze Frame (uno por línea, opcional)", rows=4)

    # Mediciones comunes
    comunes = input_group("⚡ Mediciones comunes", [
        input("🔋 Voltaje batería en reposo (V)", type=NUMBER, name="v_bat_repo"),
        input("🔑 Voltaje durante arranque (V)", type=NUMBER, name="v_bat_arr"),
        input("⚡ Voltaje alternador a ralenti (V)", type=NUMBER, name="v_alt"),
        input("🌬️ Vacío en ralenti (inHg)", type=NUMBER, name="vac_inhg"),
        input("💨 Contrapresión a 2500 rpm (psi)", type=NUMBER, name="contra_psi"),
    ]) or {}

    # Específicos por tipo
    tipo = datos.get("combustible") or "Nafta MPI"
    if "Diesel" in tipo:
        espec = input_group("🛠️ Mediciones Diesel", [
            input("Presión riel al dar arranque (bar)", type=NUMBER, name="cr_arr"),
            input("Presión riel en ralenti (bar)", type=NUMBER, name="cr_idle"),
        ]) or {}
    elif "GDI" in tipo:
        espec = input_group("⚙️ Mediciones Nafta GDI", [
            input("Presión de baja (bar)", type=NUMBER, name="pbaja"),
            input("Presión riel GDI en arranque (bar)", type=NUMBER, name="gdi_arr"),
            input("Presión riel GDI en marcha (bar)", type=NUMBER, name="gdi_run"),
        ]) or {}
    else:
        espec = input_group("⛽ Mediciones Nafta MPI", [
            input("Presión de riel (bar)", type=NUMBER, name="mpi_pr"),
        ]) or {}

    # Combinar
    pack: Dict[str, Any] = {}
    pack.update(comunes or {})
    pack.update(espec or {})

    # Evaluación
    hallazgos, score = evaluar_pack(pack, tipo)
    diag, acciones, nivel = construir_diagnostico(hallazgos, score, tipo)

    # Resultados
    clear()
    put_theme_css()
    put_whatsapp_button("5491172379474", "Hola, vengo del asistente de diagnóstico")

    put_markdown("## 📊 Resultado del análisis")
    filas = [["📌 Parámetro", "📏 Valor", "📖 Referencia", "✅ Estado"]]
    for h in hallazgos:
        filas.append([h["label"], h["valor"], h["ref"], h["estado"]])
    put_table(filas)

    # Panel: Puntaje + Diagnóstico (panel blanco)
    put_html(f'''
      <div class="section-card">
        <div class="badge {nivel}" style="margin-bottom:8px;">Puntaje de riesgo: {score}/100</div>
        <h3>🩺 Diagnóstico preliminar</h3>
        <p>{diag}</p>
      </div>
    ''')

    # Panel gris translúcido: Acciones sugeridas
    if acciones:
        put_html('<div class="glass-gray">')
        put_markdown("### 🧪 Acciones sugeridas")
        put_table([["Sugerencia"]] + [[a] for a in acciones])
        put_html('</div>')

    # Panel gris translúcido: Informe descargable
    informe = {
        "vehiculo": datos,
        "sintomas": sintomas_sel or [],
        "dtc": [l for l in (dtc_txt or "").splitlines() if l.strip()],
        "mediciones": [f"{h['label']}: {h['valor']} (ref {h['ref']}) → {h['estado']}" for h in hallazgos],
        "diagnostico_preliminar": diag,
        "acciones": acciones,
    }
    nombre = f"informe_inyeccion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    put_html('<div class="glass-gray">')
    put_markdown("### ⬇️ Descargar informe")
    put_file(nombre, build_txt(informe))
    put_html('</div>')

# -----------------------------
# Main
# -----------------------------
def main():
    wizard()

if __name__ == "__main__":
    start_server(main, host="0.0.0.0", port=8080, debug=True, auto_open_webbrowser=True)