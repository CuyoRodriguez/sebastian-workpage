from pathlib import Path

import control
import numpy as np
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Control Digital - Sebastián Enríquez",
    layout="wide",
)

css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

st.title("Módulo de Control Digital - Sebastián Enríquez")

if st.button("⬅️ Página Central"):
    st.switch_page("app.py")

st.write(
    "Espacio de trabajo para estudiar sistemas discretos, analizar su comportamiento "
    "en frecuencia y evaluar su estabilidad."
)

z_tab, frequency_tab, stability_tab = st.tabs(
    [
        "Transformada Z y Discretización",
        "Respuesta en Frecuencia / Diagramas de Bode",
        "Análisis de Estabilidad (Jury / Lugar de las Raíces)",
    ]
)

with z_tab:
    st.subheader("Respuesta al escalón de un sistema discreto")
    st.write(
        "Ejemplo: sistema de primer orden "
        r"$G(z) = \frac{0.2}{z - 0.8}$ con periodo de muestreo $T_s = 1$ s."
    )

    system = control.TransferFunction([0.2], [1, -0.8], dt=1)
    time, response = control.step_response(system)
    response = np.asarray(response).squeeze()

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=time,
            y=response,
            mode="lines+markers",
            name="Respuesta al escalón",
            line={"color": "#2463a6", "width": 3},
            marker={"size": 7},
        )
    )
    figure.update_layout(
        title="Respuesta al escalón unitario",
        xaxis_title="Tiempo (s)",
        yaxis_title="Salida",
        template="plotly_white",
        margin={"l": 20, "r": 20, "t": 55, "b": 20},
    )
    st.plotly_chart(figure, use_container_width=True)
    st.caption("Modelo discreto: G(z) = 0.2 / (z - 0.8), con Ts = 1 s.")

with frequency_tab:
    st.subheader("Respuesta en frecuencia")
    st.info(
        "Utiliza esta pestaña para explorar la respuesta en frecuencia y los "
        "diagramas de Bode de sistemas discretos."
    )

with stability_tab:
    st.subheader("Estabilidad de sistemas discretos")
    st.info(
        "Utiliza esta pestaña para analizar estabilidad mediante el criterio de "
        "Jury y el lugar de las raíces."
    )
