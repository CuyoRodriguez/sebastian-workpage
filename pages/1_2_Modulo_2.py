from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


st.set_page_config(page_title="Módulo 2 - Control Digital", layout="wide")


def select_deliverable(deliverable: str) -> None:
    st.session_state.module_2_selected_deliverable = deliverable


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

if st.session_state.get("module_2_selected_deliverable") == "Evidencia 2":
    st.title(
        "Evidencia 2: Modelado por Mínimos Cuadrados y Control Proporcional Discreto"
    )
else:
    st.title("Módulo 2: Análisis de Sistemas de Control Discreto")

st.page_link(
    "pages/1_Control_Digital.py",
    label="Volver a Control Digital",
    icon="↩️",
)

deliverables = [
    "Actividad 6",
    "Actividad 7",
    "Actividad 8",
    "Actividad 9",
    "Actividad 10",
    "Evidencia 2",
]

if "module_2_selected_deliverable" not in st.session_state:
    st.session_state.module_2_selected_deliverable = ""

for row_start in range(0, len(deliverables), 3):
    columns = st.columns(3, gap="large")
    for column, deliverable in zip(columns, deliverables[row_start : row_start + 3]):
        with column:
            with st.container(border=True):
                st.button(
                    deliverable,
                    key=f"module_2_{deliverable.lower().replace(' ', '_')}",
                    use_container_width=True,
                    on_click=select_deliverable,
                    args=(deliverable,),
                )

if st.session_state.module_2_selected_deliverable != "Evidencia 2":
    if st.session_state.module_2_selected_deliverable:
        st.info("Contenido en desarrollo.")
else:
    st.markdown(
        "En este informe se identifican los parámetros de un sistema discreto "
        "a partir de datos de entrada y salida, se construye su función de "
        "transferencia y se evalúa la estabilidad en lazo cerrado con control "
        "proporcional. Los datos de ejemplo son editables."
    )

    tabs = st.tabs(
        [
            "📊 1. Datos y Mínimos Cuadrados",
            "📐 2. Función de Transferencia G(z)",
            "🎛️ 3. Control Proporcional y Estabilidad",
            "📝 4. Conclusiones y Rúbrica",
        ]
    )

    with tabs[0]:
        st.markdown(
            "Dataset sintético reproducible de **15 semestres**. "
            "La entrada $x[n]$ es el presupuesto de tutorías (miles de USD) "
            "y la salida $y[n]$ es la cantidad de graduados."
        )
        budget = np.array(
            [3.2, 4.1, 3.7, 5.0, 4.6, 6.2, 5.4, 7.1, 6.5, 8.0, 7.3, 9.2, 8.4, 10.1, 9.5],
            dtype=float,
        )
        graduates = np.empty(15, dtype=float)
        graduates[0] = 12
        disturbances = np.array(
            [0, 1, -1, 0, 2, -1, 1, 0, -2, 1, 0, 2, -1, 1, 0],
            dtype=float,
        )
        for sample in range(1, len(graduates)):
            graduates[sample] = round(
                0.62 * graduates[sample - 1]
                + 1.35 * budget[sample]
                + disturbances[sample]
            )

        st.dataframe(
            {
                "Semestre n": np.arange(1, 16),
                "Presupuesto x[n] (miles USD)": budget,
                "Graduados y[n]": graduates.astype(int),
            },
            hide_index=True,
            use_container_width=True,
        )

        structure = st.radio(
            "Selecciona la estructura del modelo",
            [
                "Estructura 1 (1er orden)",
                "Estructura 2 (2do orden con retardo)",
            ],
            horizontal=True,
            key="evidence_2_structure",
        )
        if structure == "Estructura 1 (1er orden)":
            st.latex(
                r"y[n]=i\,y[n-1]+j\,x[n]+e[n],"
                r"\qquad \theta=[i\ \ j]^T"
            )
            model_order = 1
            sample_indices = np.arange(1, len(graduates))
            regressors = np.column_stack(
                (graduates[:-1], budget[1:])
            )
            target = graduates[1:]
            coefficient_names = ["î", "ĵ"]
        else:
            st.latex(
                r"y[n]=i_1y[n-1]+i_2y[n-2]+j_1x[n-1]+j_2x[n-2]+e[n],"
                r"\qquad \theta=[i_1\ i_2\ j_1\ j_2]^T"
            )
            model_order = 2
            sample_indices = np.arange(2, len(graduates))
            regressors = np.column_stack(
                (
                    graduates[1:-1],
                    graduates[:-2],
                    budget[1:-1],
                    budget[:-2],
                )
            )
            target = graduates[2:]
            coefficient_names = ["î₁", "î₂", "ĵ₁", "ĵ₂"]

        model_coefficients: np.ndarray | None = None
        if np.linalg.matrix_rank(regressors) < regressors.shape[1]:
            st.error(
                "La matriz de regresores no tiene rango completo; no se puede "
                "invertir ΦᵀΦ para estos datos."
            )
        else:
            try:
                model_coefficients = (
                    np.linalg.inv(regressors.T @ regressors)
                    @ regressors.T
                    @ target
                )
            except np.linalg.LinAlgError as error:
                st.error(f"No fue posible calcular la inversa de ΦᵀΦ: {error}")
            else:
                predicted = regressors @ model_coefficients
                mse = float(np.mean((target - predicted) ** 2))
                coefficient_columns = st.columns(len(model_coefficients) + 1)
                for column, name, coefficient in zip(
                    coefficient_columns,
                    coefficient_names,
                    model_coefficients,
                ):
                    column.metric(f"Coeficiente {name}", f"{coefficient:.5g}")
                coefficient_columns[-1].metric("MSE", f"{mse:.5g}")

                figure, axis = plt.subplots(figsize=(9, 4.5))
                axis.plot(
                    np.arange(1, 16),
                    graduates,
                    linestyle="none",
                    marker="o",
                    label="Graduados reales",
                )
                axis.plot(
                    sample_indices + 1,
                    predicted,
                    linestyle="--",
                    marker="s",
                    label="Predicción OLS",
                )
                axis.set(
                    title="Graduados reales y predicción del modelo",
                    xlabel="Semestre n",
                    ylabel="Cantidad de graduados",
                    xticks=np.arange(1, 16),
                )
                axis.grid(True, alpha=0.3)
                axis.legend()
                figure.tight_layout()
                st.pyplot(figure)
                plt.close(figure)

    with tabs[1]:
        st.markdown(
            r"""
            Aplicando la transformada Z con condiciones iniciales nulas, la
            función de transferencia se obtiene a partir de la estructura
            seleccionada y de los coeficientes estimados.
            """
        )
        if model_coefficients is None:
            st.warning("Corrige los datos en la primera pestaña para estimar G(z).")
        elif model_order == 1:
            estimated_i, estimated_j = model_coefficients
            poles = np.array([estimated_i])
            st.latex(
                rf"\hat{{G}}(z)=\frac{{\hat{{j}}z}}{{z-\hat{{i}}}}"
                rf"=\frac{{{estimated_j:.6g}z}}{{z-({estimated_i:.6g})}}"
            )
            stability_text = (
                "estable" if abs(estimated_i) < 1 else "inestable o marginal"
            )
            st.markdown(
                f"- **Polo estimado:** $z={estimated_i:.6g}$."
                f"\n- **Estabilidad sin controlar:** {stability_text}."
            )
        else:
            estimated_i1, estimated_i2, estimated_j1, estimated_j2 = model_coefficients
            poles = np.roots([1, -estimated_i1, -estimated_i2])
            st.latex(
                rf"\hat{{G}}(z)=\frac{{\hat{{j}}_1z+\hat{{j}}_2}}"
                rf"{{z^2-\hat{{i}}_1z-\hat{{i}}_2}}"
                rf"=\frac{{{estimated_j1:.6g}z+({estimated_j2:.6g})}}"
                rf"{{z^2-({estimated_i1:.6g})z-({estimated_i2:.6g})}}"
            )
            pole_values = ", ".join(f"{pole:.5g}" for pole in poles)
            st.markdown(
                f"- **Polos estimados:** $z={pole_values}$."
                f"\n- **Cero estimado:** $z={-estimated_j2 / estimated_j1:.6g}$."
                if not np.isclose(estimated_j1, 0)
                else f"- **Polos estimados:** $z={pole_values}$."
            )
        st.caption(
            "El modelo representa el conjunto sintético de 15 semestres y "
            "su orden depende de la estructura seleccionada."
        )

    with tabs[2]:
        st.markdown(
            r"""
            Para realimentación unitaria negativa
            $x[n]=K_p(r[n]-y[n])$, los polos de lazo cerrado se calculan con
            el denominador $1+K_pG(z)$. El sistema discreto es estable si todos
            los polos quedan estrictamente dentro del círculo unitario.
            """
        )
        if model_coefficients is None:
            st.warning(
                "Corrige los datos en la primera pestaña para analizar la estabilidad."
            )
        else:
            proportional_gain = st.number_input(
                "Ganancia proporcional Kₚ",
                value=1.0,
                step=0.1,
                key="evidence_2_kp",
            )
            if model_order == 1:
                estimated_i, estimated_j = model_coefficients
                closed_loop_denominator = 1 + proportional_gain * estimated_j
                if np.isclose(closed_loop_denominator, 0):
                    st.error(
                        "La ganancia seleccionada cancela el término de mayor "
                        "grado del denominador; no se puede evaluar un polo finito."
                    )
                    closed_loop_poles = np.array([np.inf])
                    closed_loop_numerator = ""
                else:
                    closed_loop_poles = np.array(
                        [estimated_i / closed_loop_denominator]
                    )
                    closed_loop_numerator = (
                        rf"\frac{{K_p\hat{{j}}z}}{{(1+K_p\hat{{j}})z-\hat{{i}}}}"
                        rf"=\frac{{{proportional_gain:.5g}({estimated_j:.5g})z}}"
                        rf"{{({closed_loop_denominator:.5g})z-({estimated_i:.5g})}}"
                    )
            else:
                estimated_i1, estimated_i2, estimated_j1, estimated_j2 = model_coefficients
                closed_loop_poles = np.roots(
                    [
                        1,
                        proportional_gain * estimated_j1 - estimated_i1,
                        proportional_gain * estimated_j2 - estimated_i2,
                    ]
                )
                closed_loop_numerator = (
                    rf"\frac{{K_p(\hat{{j}}_1z+\hat{{j}}_2)}}"
                    rf"{{z^2+(K_p\hat{{j}}_1-\hat{{i}}_1)z"
                    rf"+(K_p\hat{{j}}_2-\hat{{i}}_2)}}"
                    rf"=\frac{{{proportional_gain:.5g}"
                    rf"(({estimated_j1:.5g})z+({estimated_j2:.5g}))}}"
                    rf"{{z^2+({proportional_gain * estimated_j1 - estimated_i1:.5g})z"
                    rf"+({proportional_gain * estimated_j2 - estimated_i2:.5g})}}"
                )
            is_stable = bool(np.all(np.abs(closed_loop_poles) < 1))
            st.latex(r"\hat{T}(z)=" + closed_loop_numerator)
            poles_text = ", ".join(f"{pole:.5g}" for pole in closed_loop_poles)
            st.metric("Polos de lazo cerrado", poles_text)
            st.metric(
                "Estabilidad",
                "Estable" if is_stable else "Inestable o marginal",
            )
            if is_stable:
                st.success(
                    "El polo queda dentro del círculo unitario: "
                    "$|z_{cl}|<1$."
                )
            else:
                st.error(
                    "El polo no queda estrictamente dentro del círculo unitario; "
                    "ajusta Kₚ para cumplir $|z_{cl}|<1$."
                )

    with tabs[3]:
        st.markdown(
            """
            ### Conclusiones

            - Los parámetros del modelo se estiman minimizando el error cuadrático
              entre la salida medida y la predicha.
            - El modelo identificado permite obtener una función de transferencia
              discreta y relacionar la ganancia proporcional con la ubicación del polo.
            - La estabilidad depende de que el polo de lazo cerrado permanezca
              estrictamente dentro del círculo unitario.
            - Los resultados dependen de la calidad, excitación y longitud de los
              datos, así como de que el modelo de primer orden con retardo represente
              adecuadamente al proceso.
            """
        )
        st.markdown("### Rúbrica de autoevaluación")
        rubric = [
            ("Preparación y explicación de datos", 25),
            ("Estimación por mínimos cuadrados e interpretación", 30),
            ("Obtención de G(z) y análisis del polo", 25),
            ("Evaluación de Kₚ, estabilidad y conclusiones", 20),
        ]
        earned_points = 0
        for index, (criterion, weight) in enumerate(rubric):
            if st.checkbox(
                f"{criterion} ({weight} %)",
                key=f"evidence_2_rubric_{index}",
            ):
                earned_points += weight
        st.progress(earned_points / 100, text=f"Autoevaluación: {earned_points}/100 %")
        st.caption(
            "Marca cada criterio solo cuando esté sustentado por cálculos y "
            "evidencias verificables en tu entrega."
        )
