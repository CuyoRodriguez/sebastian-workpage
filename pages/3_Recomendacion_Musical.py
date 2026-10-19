import base64
import mimetypes
from pathlib import Path
import unicodedata

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Recomendación Musical", layout="wide")


@st.cache_data
def load_music_library(
    csv_path: str,
    modified_time_ns: int,
) -> pd.DataFrame:
    library = pd.read_csv(csv_path, encoding="utf-8-sig")
    required_columns = {"Track name", "Artist name", "Playlist name"}
    missing_columns = required_columns.difference(library.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Faltan columnas requeridas en el CSV: {missing}.")
    library["Artist name"] = library["Artist name"].map(canonicalize_artist)
    library.drop_duplicates(
        subset=["Track name", "Artist name"],
        inplace=True,
    )
    return library


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(character for character in normalized if not unicodedata.combining(character)).casefold()


def canonicalize_artist(artist_name: object) -> object:
    if pd.isna(artist_name):
        return artist_name

    normalized = normalize_text(artist_name).replace("’", "'")
    if normalized in {"will wood", "will wood and the tapeworms"}:
        return "Will Wood"
    if normalized in {"jack stauber", "jack stauber's micropop"}:
        return "Jack Stauber"
    return artist_name


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


def select_music_genre(genre: str) -> None:
    st.session_state.music_genre_filter = genre
    st.session_state.selected_genre = genre


def select_music_artist(artist: str) -> None:
    st.session_state.selected_music_artist = artist


generos_config = [
    {
        "nombre": "Clásica",
        "clave": "Clásica",
        "img": "assets/genres/clasica.png",
        "grupo": "🎻 Instrumental, BSO & Ambient",
    },
    {
        "nombre": "Alternativa",
        "clave": "Alternativa",
        "img": "assets/genres/alternativa.png",
        "grupo": "🎸 Música Alternativa",
    },
    {
        "nombre": "Indie & Synth",
        "clave": "Indie",
        "img": "assets/genres/indie.png",
        "grupo": "✨ Indie, Synth & Psicodelia",
    },
    {
        "nombre": "Experimental",
        "clave": "Experimental",
        "img": "assets/genres/experimental.png",
        "grupo": "🎭 Experimental & Avant-Garde",
    },
    {
        "nombre": "Rock & Metal",
        "clave": "Rock",
        "img": "assets/genres/rock.png",
        "grupo": "🔥 Rock & Heavy Metal",
    },
    {
        "nombre": "Pop y otros",
        "clave": "Pop",
        "img": "assets/genres/pop.png",
        "grupo": "🎧 Pop, Variados & Otros",
    },
]
project_root = Path(__file__).resolve().parent.parent
genre_image_css = []
for index, genre_config in enumerate(generos_config):
    image_path = project_root / genre_config["img"]
    image_mime = mimetypes.guess_type(image_path.name)[0] or "image/png"
    image_data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    image_selector = (
        f'[class*="st-key-music_filter_{index}"] button::before, '
        f'[class*="st-key-genre_card_{index}"] button::before'
    )
    genre_image_css.append(
        f'{image_selector} {{ background-image: url("data:{image_mime};base64,{image_data}"); }}'
    )

css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div {
            background-color: #FA2D48;
        }

        section[data-testid="stSidebar"] * {
            color: #FFFFFF;
        }

        section[data-testid="stSidebar"] a {
            color: #FFFFFF;
        }

        [class*="st-key-music_filter_"] button,
        [class*="st-key-genre_card_"] button {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 12px !important;
            min-height: 53px !important;
            padding: 4px 16px 4px 4px !important;
            border: 2px solid #000000 !important;
            border-radius: 40px !important;
            background: #FFFFFF !important;
            color: #000000 !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            text-align: left !important;
            transition: box-shadow 160ms ease, transform 160ms ease !important;
        }

        [class*="st-key-music_filter_"] button::before,
        [class*="st-key-genre_card_"] button::before {
            content: "";
            display: block;
            flex: 0 0 45px;
            width: 45px;
            height: 45px;
            border-radius: 50%;
            border: 1px solid #000000;
            background-position: center;
            background-size: cover;
        }

        [class*="st-key-music_filter_"] button [data-testid="stMarkdownContainer"],
        [class*="st-key-genre_card_"] button [data-testid="stMarkdownContainer"] {
            flex: 1;
            text-align: center;
        }

        [class*="st-key-music_filter_"] button p,
        [class*="st-key-genre_card_"] button p {
            margin: 0 !important;
            color: #000000 !important;
            font-size: 16px !important;
            font-weight: 700 !important;
        }

        [class*="st-key-music_filter_"] button:hover,
        [class*="st-key-genre_card_"] button:hover {
            border-color: #000000 !important;
            background: #FFFFFF !important;
            color: #000000 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.16) !important;
            transform: translateY(-2px);
        }

        [class*="st-key-music_filter_"] button:hover p,
        [class*="st-key-genre_card_"] button:hover p {
            color: #000000 !important;
        }

        [data-testid="stBaseButton-primary"] {
            background-color: #FA2D48;
            border-color: #FA2D48;
            color: #FFFFFF;
        }

        [data-testid="stBaseButton-primary"]:hover {
            background-color: #D91F3A;
            border-color: #D91F3A;
            color: #FFFFFF;
        }

        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            color: #FA2D48;
            border-bottom: 2px solid #FA2D48;
        }

        [data-testid="stTabs"] [role="tab"]:hover {
            color: #D91F3A;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #222222 !important;
            border-radius: 18px !important;
            background-color: #FFFFFF;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }

        .music-page-header,
        .music-page-banner {
            border: 1px solid #222222;
            border-radius: 18px;
            background: #FFFFFF;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            margin: 0.5rem 0 1rem;
            padding: 1.15rem 1.5rem;
            text-align: center;
        }

        .music-page-header h1 {
            color: #FA2D48;
            font-size: clamp(1.8rem, 4vw, 2.6rem);
            margin: 0;
        }

        .music-page-banner p {
            color: #292929;
            font-size: 1.05rem;
            margin: 0;
        }

        .genre-icon {
            align-items: center;
            background: #FFF0F2;
            border: 1px solid rgba(250, 45, 72, 0.2);
            border-radius: 50%;
            display: flex;
            font-size: 1.5rem;
            height: 3rem;
            justify-content: center;
            margin: 0.4rem auto;
            width: 3rem;
        }

        .music-card {
            background: #FFFFFF;
            border: 1px solid #222222;
            border-left: 5px solid #FA2D48;
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            margin: 0.5rem 0 1rem;
            padding: 1.1rem 1.35rem;
        }

        .music-card h3 {
            color: #FA2D48;
            margin: 0 0 0.4rem;
        }

        .music-card p {
            color: #292929;
            margin: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"<style>{''.join(genre_image_css)}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="music-page-header"><h1>Recomendacion musical</h1></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="music-page-banner"><p>Recomendaciones musicales por parte del creador de la pagina</p></div>',
    unsafe_allow_html=True,
)

valid_genres = {genre["clave"] for genre in generos_config}
if st.session_state.get("selected_genre") not in valid_genres:
    st.session_state.selected_genre = None
if st.session_state.get("music_genre_filter") not in valid_genres:
    st.session_state.music_genre_filter = None

with st.sidebar:
    st.header("Mi Colección")
    st.caption("Explora por género")
    for index, genre in enumerate(generos_config):
        st.button(
            genre["nombre"],
            key=f"music_filter_{index}",
            use_container_width=True,
            on_click=select_music_genre,
            args=(genre["clave"],),
        )

csv_path = Path(__file__).resolve().parent.parent / "My Apple Music Library.csv"
classified_library: pd.DataFrame | None = None

try:
    modified_time_ns = csv_path.stat().st_mtime_ns
    library = load_music_library(
        str(csv_path),
        modified_time_ns,
    )
except FileNotFoundError:
    st.error(
        f"No se encontró **{csv_path.name}** en la raíz del proyecto: "
        f"`{csv_path.parent}`."
    )
except (OSError, UnicodeDecodeError, pd.errors.ParserError, ValueError) as error:
    st.error(f"No se pudo cargar la biblioteca musical: {error}")
else:
    classified_library = add_genre_group(library)

recommendation_tab, artist_tab = st.tabs(["🎧 Géneros", "🎤 Artistas"])

with recommendation_tab:
    st.subheader("Explora por género")
    for row_start in range(0, len(generos_config), 3):
        genre_columns = st.columns(3)
        row_genres = generos_config[row_start : row_start + 3]
        for offset, (column, genre) in enumerate(zip(genre_columns, row_genres)):
            index = row_start + offset
            with column:
                st.button(
                    genre["nombre"],
                    key=f"genre_card_{index}",
                    use_container_width=True,
                    on_click=select_music_genre,
                    args=(genre["clave"],),
                )

    if classified_library is None:
        st.info("Agrega el CSV de tu biblioteca a la raíz del proyecto para ver canciones.")
    else:
        selected_genre = st.session_state.music_genre_filter
        if selected_genre is None:
            st.info("Seleccione un genero para ver las recomendaciones")
        else:
            selected_config = next(
                genre for genre in generos_config
                if genre["clave"] == selected_genre
            )
            visible_library = classified_library[
                classified_library["Genre_Group"] == selected_config["grupo"]
            ]
            st.markdown(
                f'<div class="music-card"><h3>{selected_config["nombre"]}</h3>'
                f"<p>{len(visible_library):,} canciones deduplicadas en esta selección.</p></div>",
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                st.dataframe(
                    visible_library[
                        [
                            "Track name",
                            "Artist name",
                            "Album",
                            "Genre_Group",
                            "Playlist name",
                        ]
                    ],
                    hide_index=True,
                    use_container_width=True,
                )

with artist_tab:
    if classified_library is None:
        st.markdown(
            """
            <div class="music-card">
              <h3>Datos de artistas</h3>
              <p>El resumen estará disponible cuando el CSV de la biblioteca se encuentre en la raíz del proyecto.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        artistas_excluidos = [
            "The Living Tombstone",
            "Hitoshizuku & Yama",
            "ALI",
            "Creepy Nuts",
            "平野義久",
            "Various Artists",
            "Varios Artistas",
            "C418",
            "Bruno Wen-li",
            "Arctic Monkeys",
            "Artic Monkeys",
            "Safari Riot",
            "Epic Mountain",
            "Lemon Demon",
            "Lorien Testard",
            "Lonen Testard",
        ]
        artistas_excluidos_normalizados = {
            normalize_text(artist) for artist in artistas_excluidos
        }
        filtered_library = classified_library[
            ~classified_library["Artist name"].map(
                lambda artist: normalize_text(artist)
                in artistas_excluidos_normalizados
            )
        ]
        artist_counts = (
            filtered_library["Artist name"]
            .dropna()
            .value_counts()
            .rename_axis("Artist name")
            .reset_index(name="Track count")
        )
        frequent_artists = artist_counts[artist_counts["Track count"] >= 15]
        st.subheader("Artistas con 15 o más canciones")

        if frequent_artists.empty:
            st.info("No hay artistas con 15 o más canciones en la biblioteca.")
        else:
            artists = frequent_artists["Artist name"].tolist()
            for row_start in range(0, len(artists), 3):
                artist_columns = st.columns(3)
                for offset, (column, artist) in enumerate(
                    zip(artist_columns, artists[row_start : row_start + 3])
                ):
                    index = row_start + offset
                    with column:
                        with st.container(border=True):
                            icon_column, label_column = st.columns([0.3, 0.7])
                            with icon_column:
                                st.markdown(
                                    '<div class="genre-icon">🎤</div>',
                                    unsafe_allow_html=True,
                                )
                            with label_column:
                                st.button(
                                    artist,
                                    key=f"artist_card_{index}",
                                    use_container_width=True,
                                    on_click=select_music_artist,
                                    args=(artist,),
                                )

        selected_artist = st.session_state.get("selected_music_artist")
        eligible_artists = set(frequent_artists["Artist name"])
        if selected_artist not in eligible_artists:
            selected_artist = None
            st.session_state.selected_music_artist = None
        if selected_artist is None:
            st.info("Selecciona una tarjeta de artista para ver sus canciones.")
        else:
            artist_tracks = filtered_library[
                filtered_library["Artist name"] == selected_artist
            ]
            st.markdown(
                f'<div class="music-card"><h3>{selected_artist}</h3>'
                f"<p>{len(artist_tracks):,} canciones de este artista.</p></div>",
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                st.dataframe(
                    artist_tracks[
                        [
                            "Track name",
                            "Artist name",
                            "Album",
                            "Genre_Group",
                            "Playlist name",
                        ]
                    ],
                    hide_index=True,
                    use_container_width=True,
                )

if st.button("⬅️ Página Central", type="primary"):
    st.switch_page("app.py")
