# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(page_title="Hub Maths-sciences ", layout="wide")

st.title("Portail des Applications de Mathématiques et de sciences de M Laurent GALLET")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)


st.write("Bienvenue. Utilisez la barre de recherche globale ou parcourez les onglets par niveau.")

# 1. Base de donnees de vos applications (A completer avec vos 50 liens)
# Structure : {"nom": "Nom affiche", "url": "Lien de l app", "niveau": "2nde" ou "1ere" ou "Tale", "theme": "Theme associe"}
applications = [
    {"nom": "Coordonnees d un vecteur", "url": "https://streamlit.app", "niveau": "2nde", "theme": "Geometrie"},
    {"nom": "Calcul de longueurs et distances", "url": "https://streamlit.app", "niveau": "2nde", "theme": "Geometrie"},
    {"nom": "Calcul de frequences statistiques", "url": "https://streamlit.app", "niveau": "2nde", "theme": "Statistiques"},
    {"nom": "Arbres de probabilite conditionnelle", "url": "https://streamlit.app", "niveau": "2nde", "theme": "Probabilites"},
    
    {"nom": "Calcul du nombre derive graphiquement", "url": "https://streamlit.app", "niveau": "1ere", "theme": "Derivees"},
    {"nom": "Equation de la tangente a une courbe", "url": "https://streamlit.app", "niveau": "1ere", "theme": "Derivees"},
    {"nom": "Suites arithmetiques et geometriques", "url": "https://streamlit.app", "niveau": "1ere", "theme": "Suites"},
    
    {"nom": "Proprietes algebriques du logarithme", "url": "https://streamlit.app", "niveau": "Tale", "theme": "Logarithmes"},
    {"nom": "Ajustement affine et moindres carres", "url": "https://streamlit.app", "niveau": "Tale", "theme": "Statistiques"}
]

# 2. Barre de recherche globale
recherche = st.text_input("Rechercher une application par mot-clé (ex: vecteur, dérivée, statistique...)", "")

# 3. Logique de filtrage et d affichage
if recherche:
    st.subheader("Résultats de la recherche")
    # On filtre la liste en ignorant les majuscules/minuscules
    resultats = [app for app in applications if recherche.lower() in app["nom"].lower() or recherche.lower() in app["theme"].lower()]
    
    if resultats:
        for app in resultats:
            st.markdown(f"**[{app['nom']}]({app['url']})** — Niveau : {app['niveau']} | Theme : {app['theme']}")
    else:
        st.warning("Aucune application ne correspond à votre recherche.")

else:
    # Si la recherche est vide, on affiche l organisation par onglets normaux
    onglet_2nde et CAP, onglet_1ere, onglet_tale = st.tabs(["SECONDE BAC PRO ET CAP", "PREMIERE BAC PRO", "TERMINALE BAC PRO"])

    # Affichage Seconde
    with onglet_2nde:
        st.info("Applications dédiées au programme de Seconde et CAP.")
        apps_2nde = [app for app in applications if app["niveau"] == "2nde et CAP"]
        themes_2nde = set([app["theme"] for app in apps_2nde])
        
        for theme in themes_2nde:
            with st.expander(theme):
                for app in apps_2nde:
                    if app["theme"] == theme:
                        st.markdown(f"[{app['nom']}]({app['url']})")

    # Affichage Premiere
    with onglet_1ere:
        st.info("Applications dédiées au programme de Première.")
        apps_1ere = [app for app in applications if app["niveau"] == "1ère"]
        themes_1ere = set([app["theme"] for app in apps_1ere])
        
        for theme in themes_1ere:
            with st.expander(theme):
                for app in apps_1ere:
                    if app["theme"] == theme:
                        st.markdown(f"[{app['nom']}]({app['url']})")

    # Affichage Terminale
    with onglet_tale:
        st.info("Applications dédiées au programme de Terminale.")
        apps_tale = [app for app in applications if app["niveau"] == "Tale"]
        themes_tale = set([app["theme"] for app in apps_tale])
        
        for theme in themes_tale:
            with st.expander(theme):
                for app in apps_tale:
                    if app["theme"] == theme:
                        st.markdown(f"[{app['nom']}]({app['url']})")
