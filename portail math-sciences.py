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
    # Assurez-vous que la valeur de "niveau" correspond exactement au texte filtré ci-dessus
    {"nom": "Centre de gravité", "url": "https://gallet-2a4zeklerrjrjxnxtap4hi.streamlit.app/", "niveau": "2nde et CAP", "theme": "Mécanique"},
    {"nom": "Concentration massique", "url": "https://gallet-nrfrpirw9ug39kesvvhzbm.streamlit.app/", "niveau": "2nde et CAP", "theme": "Chimie"},
    {"nom": "Concentration massique", "url": "https://gallet-nrfrpirw9ug39kesvvhzbm.streamlit.app/", "niveau": "2nde et CAP", "theme": "Chimie"},
    {"nom": "Le pH", "url": "https://gallet-2xkb5zlhdnonzmkahcmk3u.streamlit.app/", "niveau": "2nde et CAP", "theme": "Le pH"},

    {"nom": "Concentration molaire", "url": "https://https://gallet-hjkhuxhwzuzcdgz6bcgbzy.streamlit.app//", "niveau": "1ere", "theme": "Chimie"},
    {"nom": "Dosage du vinaigre", "url": "https://gallet-cnvqzzejzkeku7pm4j5puq.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de l'aspirine", "url": "https://gallet-pjzvshvljnxmclc5gu7pog.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de l'eau oxygénée", "url": "https://gallet-eey6ai4fdzqu8ebpzekuck.streamlit.app//", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de l'hydrazine", "url": "https://gallet-z35dnirce4hiv2khzfphb8.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de la dureté de l'eau", "url": "https://gallet-cznmv37ujadksvptwdxeuz.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage du lait", "url": "https://gallet-feahuy25zmovt3qce4vf34.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage d'une huile", "url": "https://gallet-vpydhmebcktmmlt2pbbbtp.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de la vitamine C", "url": "https://gallet-cark2tuk7yfemq93qqoan4.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage des ions chlorure", "url": "https://gallet-fyfgnfq2jyudca8xo2ztuv.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage du dioxyde de soufre", "url": "https://gallet-itvb7kcysrpcuxfrgttwle.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage du javel", "url": "https://gallet-rzry8qnwveczjbgcvcmwb2.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage général", "url": "https://gallet-faznqoc3cgdrhuydemsfpx.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Le pH", "url": "https://gallet-2xkb5zlhdnonzmkahcmk3u.streamlit.app/", "niveau": "1ere", "theme": "Le pH"},    


    

    {"nom": "Le pH", "url": "https://gallet-2xkb5zlhdnonzmkahcmk3u.streamlit.app/", "niveau": "Tale", "theme": "Le pH"}

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
    onglet_2nde_CAP, onglet_1ere, onglet_tale = st.tabs(["SECONDE BAC PRO ET CAP", "PREMIERE BAC PRO", "TERMINALE BAC PRO"])

    # Affichage Seconde
    with onglet_2nde_CAP:
        st.info("Applications dédiées au programme de Seconde et CAP.")
        
        # Correction ici : acceptation automatique de "2nde" OU de "CAP"
        apps_2nde = [app for app in applications if app["niveau"] in ["2nde", "CAP"]]
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
