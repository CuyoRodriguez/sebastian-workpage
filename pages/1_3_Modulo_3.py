from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Módulo 3 - Control Digital", layout="wide")

css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Control Digital")
    st.page_link("app.py", label="Página Central", icon="🏠", use_container_width=True)
    st.page_link(
        "pages/2_Calculadoras.py",
        label="Calculadoras de la materia",
        icon="🧮",
        use_container_width=True,
    )
    st.page_link(
        "pages/1_1_Modulo_1.py",
        label="Módulo 1. Sistemas de control discretos",
        icon="📦",
        use_container_width=True,
    )
    st.page_link(
        "pages/1_2_Modulo_2.py",
        label="Módulo 2. Análisis de sistemas de control discreto",
        icon="📦",
        use_container_width=True,
    )
    st.page_link(
        "pages/1_3_Modulo_3.py",
        label="Módulo 3. Algoritmos de diseño y sintonización de controladores digitales",
        icon="📦",
        use_container_width=True,
    )

st.title("Módulo 3: Algoritmos de Diseño y Sintonización")
st.page_link(
    "pages/1_Control_Digital.py",
    label="Volver a Control Digital",
    icon="↩️",
)


def select_deliverable(deliverable: str) -> None:
    st.session_state.module_3_selected_deliverable = deliverable


deliverables = ["Actividad 10", "Actividad 11", "Actividad 12", "Actividad 13"]
if "module_3_selected_deliverable" not in st.session_state:
    st.session_state.module_3_selected_deliverable = ""

for row_start in range(0, len(deliverables), 3):
    columns = st.columns(3, gap="large")
    for column, deliverable in zip(columns, deliverables[row_start : row_start + 3]):
        with column:
            with st.container(border=True):
                st.button(
                    deliverable,
                    key=f"module_3_{deliverable.lower().replace(' ', '_')}",
                    use_container_width=True,
                    on_click=select_deliverable,
                    args=(deliverable,),
                )

if st.session_state.module_3_selected_deliverable == "Actividad 10":
    tabs = st.tabs(
        [
            "📐 Funciones de Transferencia",
            "📊 Comparación Gráfica",
            "📝 Análisis de Resultados",
        ]
    )

    with tabs[0]:
        st.subheader("Función de transferencia analógica continua")
        st.latex(r'G(s) = \frac{s^2 + 0.3s}{s^2 + 0.5s - 0.14}')
        st.markdown("Discretización con periodo de muestreo $T = 1.0$ s:")
        columns = st.columns(3)
        with columns[0]:
            st.markdown("**Mapeo de Polos y Ceros**")
            st.latex(
                r'H_a(z) = \frac{z^2 - 1.7408z + 0.7408}{z^2 - 1.7180z + 0.6065}'
            )
        with columns[1]:
            st.markdown("**Retenedor de Orden Cero (ZOH)**")
            st.latex(
                r'H_b(z) = \frac{z^2 - 1.8187z + 0.8187}{z^2 - 1.7180z + 0.6065}'
            )
        with columns[2]:
            st.markdown("**Transformación Tustin**")
            st.latex(
                r'H_c(z) = \frac{4.6z^2 - 8z + 3.4}{4.86z^2 - 8.28z + 2.86}'
            )

    with tabs[1]:
        st.info("La comparación gráfica de las funciones discretizadas está en desarrollo.")

    with tabs[2]:
        st.info("El análisis de resultados de la Actividad 10 está en desarrollo.")
elif st.session_state.module_3_selected_deliverable:
    st.info("Contenido en desarrollo.")
