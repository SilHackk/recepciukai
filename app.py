from __future__ import annotations

import textwrap
from pathlib import Path

import streamlit as st

from src.data_loader import ensure_dataset
from src.nlp_utils import parse_pantry_lines
from src.recommender import RecipeEngine

st.set_page_config(page_title="Maisto receptų generatorius", page_icon="🍳", layout="wide")

DATA_PATH = Path("data/13k-recipes.csv")

@st.cache_resource(show_spinner=False)
def get_engine() -> RecipeEngine:
    ensure_dataset(DATA_PATH)
    return RecipeEngine(DATA_PATH)


def main() -> None:
    st.title("🍳 Maisto receptų generatorius")
    st.caption(
        "Įvesk turimus ingredientus, o sistema suras receptus iš atviro duomenų rinkinio ir parodys, ko dar galėtų trūkti."
    )

    with st.sidebar:
        st.header("Nustatymai")
        top_k = st.slider("Kiek receptų rodyti", 1, 8, 4)
        max_missing = st.slider("Leidžiamas trūkstamų ingredientų skaičius", 0, 5, 2)
        st.markdown("### Ką daro NLP dalis?")
        st.markdown(
            "- **Regex** ištraukia kiekius ir vienetus\n"
            "- **Tokenizacija + leksikonas** normalizuoja ingredientus\n"
            "- **TF-IDF** suranda panašiausius receptus\n"
            "- **Fuzzy matching** leidžia atpažinti artimus pavadinimus"
        )

    default_input = textwrap.dedent(
        """
        2 kiaušiniai
        200 g miltai
        250 ml pienas
        30 g sviestas
        1 šaukšt cukrus
        žiupsnis druska
        """
    ).strip()

    pantry_text = st.text_area(
        "Turimi ingredientai (po vieną eilutėje, galima su kiekiais)",
        value=default_input,
        height=220,
        help="Pvz.: 500 g vištiena, 2 pomidorai, 100 ml grietinė",
    )

    if st.button("Generuoti receptus", type="primary"):
        pantry_items = parse_pantry_lines(pantry_text)
        if not pantry_items:
            st.warning("Neradau ingredientų. Įvesk bent vieną eilutę.")
            st.stop()

        st.subheader("Atpažinti ingredientai")
        st.write([f"{p.original} → {p.name}" for p in pantry_items])

        engine = get_engine()
        results = engine.suggest(pantry_items, top_k=top_k, max_missing=max_missing)

        if not results:
            st.error("Pagal šiuos ingredientus receptų neradau. Pabandyk pridėti daugiau bazinių produktų.")
            st.stop()

        st.subheader("Siūlomi receptai")
        for i, rec in enumerate(results, start=1):
            with st.container(border=True):
                st.markdown(f"### {i}. {rec.title}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Padengimas", f"{rec.coverage:.0%}")
                c2.metric("TF-IDF panašumas", f"{rec.similarity:.2f}")
                c3.metric("Trūksta", str(len(rec.missing)))

                st.markdown("**Turi:** " + (", ".join(rec.matched[:10]) if rec.matched else "—"))
                st.markdown("**Reikėtų nusipirkti:** " + (", ".join(rec.missing) if rec.missing else "nieko"))

                with st.expander("Ingredientai"):
                    st.write(rec.ingredients)
                with st.expander("Gaminimo instrukcija"):
                    st.write(rec.instructions)

    with st.expander("Demo scenarijus atsiskaitymui"):
        st.markdown(
            "1. Paleisti programą.\n"
            "2. Įvesti ingredientus lietuviškai su kiekiais.\n"
            "3. Parodyti, kaip regex ištraukia kiekius ir normalizuoja pavadinimus.\n"
            "4. Palyginti skirtingus `max_missing` nustatymus.\n"
            "5. Parodyti, kad siūlomi receptai remiasi atviru duomenų rinkiniu."
        )


if __name__ == "__main__":
    main()
