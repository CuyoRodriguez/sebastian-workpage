from pathlib import Path
import unicodedata
from io import BytesIO

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Recomendación Musical", layout="wide")


@st.cache_data
def load_music_library(csv_content: bytes) -> pd.DataFrame:
    library = pd.read_csv(BytesIO(csv_content), encoding="utf-8-sig")
    required_columns = {"Artist name", "Playlist name"}
    missing_columns = required_columns.difference(library.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Faltan columnas requeridas en el CSV: {missing}.")
    return library


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(character for character in normalized if not unicodedata.combining(character)).casefold()


def classify_genre_group(artist_name: object, playlist_name: object) -> str:
    artist = normalize_text(artist_name)
    playlist = normalize_text(playlist_name)

    if any(
        name in artist
        for name in (
            "the strokes",
            "cage the elephant",
            "radiohead",
            "foster the people",
            "arctic monkeys",
            "interpol",
            "declan mckenna",
        )
    ) or any(term in playlist for term in ("alternative", "rock alternativo")):
        return "🎸 Música Alternativa"

    if any(
        name in artist
        for name in (
            "gorillaz",
            "inner wave",
            "everything everything",
            "saint motel",
            "l'imperatrice",
            "peach pit",
            "daft punk",
            "temples",
            "mgmt",
            "metronomy",
            "crumb",
            "tame impala",
            "the buttertones",
        )
    ):
        return "✨ Indie, Synth & Psicodelia"

    if any(
        name in artist
        for name in (
            "will wood",
            "fish in a birdcage",
            "jack stauber",
            "tally hall",
            "idkhow",
            "lemon demon",
        )
    ):
        return "🎭 Experimental & Avant-Garde"

    if any(
        name in artist
        for name in ("c418", "epic mountain", "lorien testard", "waveshaper")
    ) or any(
        term in playlist
        for term in (
            "orchestra",
            "orchestral",
            "orquesta",
            "piano",
            "classical",
            "clasica",
            "minecraft",
            "kurzgesagt",
            "fromsoftware",
            "from software",
        )
    ):
        return "🎻 Instrumental, BSO & Ambient"

    if any(
        name in artist
        for name in (
            "avenged sevenfold",
            "rammstein",
            "muse",
            "rush",
            "slipknot",
            "system of a down",
        )
    ) or any(term in playlist for term in ("metal", "a7x", "guitar hero")):
        return "🔥 Rock & Heavy Metal"

    return "🎧 Pop, Variados & Otros"


def add_genre_group(library: pd.DataFrame) -> pd.DataFrame:
    classified = library.copy()
    classified["Genre_Group"] = classified.apply(
        lambda track: classify_genre_group(
            track["Artist name"],
            track["Playlist name"],
        ),
        axis=1,
    )
    return classified


css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    [data-testid="stBaseButton-primary"] {
        background-color: #B23A48;
        border-color: #B23A48;
        color: #FFFFFF;
    }

    [data-testid="stBaseButton-primary"]:hover {
        background-color: #8B2635;
        border-color: #8B2635;
        color: #FFFFFF;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #B23A48;
        border-bottom: 2px solid #B23A48;
    }

    [data-testid="stTabs"] [role="tab"]:hover {
        color: #8B2635;
    }

    .music-card {
        background: #FFF5F5;
        border-left: 5px solid #B23A48;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(139, 38, 53, 0.10);
        margin: 0.5rem 0 1rem;
        padding: 1rem 1.25rem;
    }

    .music-card h3 {
        color: #8B2635;
        margin: 0 0 0.4rem;
    }

    .music-card p {
        color: #4A3336;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Recomendación Musical")

recommendation_tab, artist_tab = st.tabs(["🎧 Recomendaciones", "🎤 Artistas"])
csv_path = Path(__file__).resolve().parent.parent / "My Apple Music Library.csv"
classified_library: pd.DataFrame | None = None

with recommendation_tab:
    if csv_path.is_file():
        csv_content = csv_path.read_bytes()
    else:
        st.caption("Selecciona el archivo CSV exportado de Apple Music.")
        uploaded_csv = st.file_uploader(
            "My Apple Music Library.csv",
            type="csv",
            key="apple_music_library",
        )
        csv_content = uploaded_csv.getvalue() if uploaded_csv is not None else None

    if csv_content is None:
        st.info(
            "Coloca **My Apple Music Library.csv** en la carpeta principal del "
            "proyecto o selecciónalo arriba para clasificar tu biblioteca."
        )
    else:
        try:
            classified_library = add_genre_group(load_music_library(csv_content))
        except (OSError, UnicodeDecodeError, pd.errors.ParserError, ValueError) as error:
            st.error(f"No se pudo cargar la biblioteca musical: {error}")
        else:
            st.markdown(
                f'<div class="music-card"><h3>Biblioteca clasificada</h3>'
                f"<p>{len(classified_library):,} pistas organizadas por género.</p></div>",
                unsafe_allow_html=True,
            )
            st.dataframe(
                classified_library,
                hide_index=True,
                use_container_width=True,
            )

with artist_tab:
    if classified_library is None:
        st.markdown(
            """
            <div class="music-card">
              <h3>Datos de artistas</h3>
              <p>Carga la biblioteca en la pestaña Recomendaciones para ver el resumen de artistas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        artist_summary = (
            classified_library.groupby(["Artist name", "Genre_Group"], dropna=False)
            .size()
            .reset_index(name="Pistas")
            .sort_values("Pistas", ascending=False)
            .head(25)
        )
        st.markdown(
            '<div class="music-card"><h3>Artistas de tu biblioteca</h3>'
            "<p>Artistas con más pistas, junto con su grupo de género asignado.</p></div>",
            unsafe_allow_html=True,
        )
        st.dataframe(artist_summary, hide_index=True, use_container_width=True)

if st.button("⬅️ Página Central", type="primary"):
    st.switch_page("app.py")
