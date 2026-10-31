# -*- coding: utf-8 -*-

import streamlit as st
import urllib.parse
import qrcode
import io

st.set_page_config(page_title="Hub Maths-sciences", layout="wide")

st.markdown("""
<style>
@media print {
    /* Libère les structures globales */
    html, body, .main, .block-container, 
    [data-testid="stApp"], 
    [data-testid="stAppViewContainer"], 
    [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"] {
        height: auto !important;
        overflow: visible !important;
        position: static !important;
        max-height: none !important;
        display: block !important;
    }
    
    /* Force la grille de colonnes à rester fluide */
    [data-testid="stHorizontalBlock"] {
        height: auto !important;
        overflow: visible !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }

    /* COMPACTION DES VIGNETTES : Réduit l'espace pour faire remonter la 5ème ligne */
    [data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 2px !important;
        padding: 4px !important;
    }
    
    /* Réduit la taille des images des QR Codes pour qu'elles tiennent sur la feuille */
    [data-testid="stImage"] img {
        max-height: 2.6cm !important;
        width: auto !important;
        margin: 0 auto !important;
    }

    /* Cache toute l'interface Streamlit globale et les boutons système */
    header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], .stAppDeployButton,
    .stAppToolbar, [data-testid="stManageAppButton"], iframe, footer + div, .viewerBadge_v1, .stCheckbox, .stRadio {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* Cache les titres et les zones de sélection */
    h1, p, .stTextInput, .stSelectbox, .stAlert {
        display: none !important;
    }
    
    /* Masque les boutons de téléchargement */
    .stDownloadButton {
        display: none !important;
    }
    
    /* Optimise les marges de la feuille A4 */
    .main .block-container {
        padding-top: 0.2cm !important;
        padding-bottom: 0.2cm !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("Portail des Applications de Mathématiques et de sciences de M Laurent GALLET")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

st.write("Bienvenue. Utilisez la barre de recherche globale ou parcourez les onglets par niveau.")

# 1. Base de donnees de vos applications
applications = [
    {"nom": "Centre de gravité", "url": "https://gallet-2a4zeklerrjrjxnxtap4hi.streamlit.app/", "niveau": "2nde", "theme": "Mécanique"},
    {"nom": "Concentration massique", "url": "https://gallet-nrfrpirw9ug39kesvvhzbm.streamlit.app/", "niveau": "2nde", "theme": "Chimie"},
    {"nom": "Le pH", "url": "https://gallet-2xkb5zlhdnonzmkahcmk3u.streamlit.app/", "niveau": "2nde", "theme": "Le pH"},
    {"nom": "Le son", "url": "https://gallet-9jgaebu6y4zett7edtpvqk.streamlit.app/", "niveau": "2nde", "theme": "Acoustique"},
    {"nom": "Equilibre", "url": "https://gallet-cr4ukp49u8usybpxsspkah.streamlit.app/", "niveau": "2nde", "theme": "Mécanique"},
    {"nom": "Les surfaces", "url": "https://gallet-quursprfackhldk38vbpcq.streamlit.app/", "niveau": "2nde", "theme": "Géométrie"},
    {"nom": "Le GNR", "url": "https://gallet-feturstpnya3ttgjvxauor.streamlit.app/", "niveau": "2nde", "theme": "Chimie"},
    {"nom": "L'intensité électrique", "url": "https://gallet-kzezbtr8bl6us9b2j2x6yq.streamlit.app/", "niveau": "2nde", "theme": "Electricité"},
    {"nom": "Modèle moléculaire", "url": "https://gallet-gubus3nzsnjigcweyvrapz.streamlit.app/", "niveau": "2nde", "theme": "Chimie"},


     
    {"nom": "Concentration molaire", "url": "https://gallet-hjkhuxhwzuzcdgz6bcgbzy.streamlit.app/", "niveau": "1ere", "theme": "Chimie"},
    {"nom": "Dosage du vinaigre", "url": "https://gallet-cnvqzzejzkeku7pm4j5puq.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de l'aspirine", "url": "https://gallet-pjzvshvljnxmclc5gu7pog.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
    {"nom": "Dosage de l'eau oxygénée", "url": "https://gallet-eey6ai4fdzqu8ebpzekuck.streamlit.app/", "niveau": "1ere", "theme": "Dosages"},
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
    {"nom": "Archimède", "url": "https://gallet-2mzeqnw2v4g2cg5kbbtvue.streamlit.app/", "niveau": "1ere", "theme": "Mécanique"},
    {"nom": "Les caractéristiques d'un son", "url": "https://gallet-9jgaebu6y4zett7edtpvqk.streamlit.app/", "niveau": "1ere", "theme": "Acoustique"},
    {"nom": "Equilibre en rotation", "url": "https://gallet-ewwlykgfb5esjm3bh5cojw.streamlit.app/", "niveau": "1ere", "theme": "Mécanique"},
    {"nom": "Les vecteurs du plan", "url": "https://gallet-hl85fritysafgola2uxzc5.streamlit.app/", "niveau": "1ere", "theme": "Géométrie analytique"},
     
    {"nom": "Archimède", "url": "https://gallet-2mzeqnw2v4g2cg5kbbtvue.streamlit.app/", "niveau": "Tale", "theme": "Mécanique"},
    {"nom": "La propagation du son", "url": "https://gallet-9jgaebu6y4zett7edtpvqk.streamlit.app/", "niveau": "Tale", "theme": "Acoustique"},
    {"nom": "Le pH", "url": "https://gallet-2xkb5zlhdnonzmkahcmk3u.streamlit.app/", "niveau": "Tale", "theme": "Le pH"}
]




def generer_qrcode_image(url_app):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url_app)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def afficher_app_avec_qrcode(nom_app, url_app):
    st.markdown(f"**[{nom_app}]({url_app})**")
    with st.expander(f"Afficher le QR Code pour : {nom_app}"):
        byte_im = generer_qrcode_image(url_app)
        st.image(byte_im, width=180)

# 2. INTERRUPTEUR DE MODE IMPRESSION
mode_impression = st.checkbox("Activer le Mode Impression (Pour imprimer proprement vos planches de QR Codes en 5x5)")

if mode_impression:
    st.warning("Mode Impression activé. Sélectionnez la feuille à imprimer ci-dessous puis faites Ctrl + P.")
    
    filtre_niveau = st.selectbox("Sélectionner le niveau à imprimer :", ["Tous les niveaux", "Seconde et CAP", "Première", "Terminale"])
    if filtre_niveau == "Seconde et CAP":
        apps_recap = [app for app in applications if app["niveau"] in ["2nde", "CAP"]]
    elif filtre_niveau == "Première":
        apps_recap = [app for app in applications if app["niveau"] == "1ere"]
    elif filtre_niveau == "Terminale":
        apps_recap = [app for app in applications if app["niveau"] == "Tale"]
    else:
        apps_recap = applications

    taille_lot = 20  # Grille de 5 colonnes sur 4 lignes (Idéal pour éviter les coupures en bas de page A4)
    total_apps = len(apps_recap)
    
    if total_apps > taille_lot:
        # Calcul automatique du nombre de pages nécessaires
        import math
        nb_pages = math.ceil(total_apps / taille_lot)
        
        # Création de la liste des choix de pages (Feuille 1, Feuille 2, Feuille 3...)
        choix_pages = [f"Feuille {i+1} (Applications {i*taille_lot+1} à {min((i+1)*taille_lot, total_apps)})" for i in range(nb_pages)]
        
        page_selectionnee = st.radio(
            "Sélectionnez la feuille à charger avant de faire Ctrl + P :",
            choix_pages,
            horizontal=True
        )
        
        # Récupération de l'index de la page sélectionnée pour découper la liste
        index_page = choix_pages.index(page_selectionnee)
        lot_a_afficher = apps_recap[index_page * taille_lot : (index_page + 1) * taille_lot]
    else:
        lot_a_afficher = apps_recap

    # Affichage de la grille (Maximum 20 éléments à la fois sur l'écran pour tenir sur un A4 complet)
    nb_colonnes = 5
    cols = st.columns(nb_colonnes)
    for index, app in enumerate(lot_a_afficher):
        col_active = cols[index % nb_colonnes]
        with col_active:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; font-weight: bold; min-height: 40px; font-size: 13px;'>{app['nom']}</div>", unsafe_allow_html=True)
                st.caption(f"{app['niveau']} | {app['theme']}")
                byte_im = generer_qrcode_image(app["url"])
                st.image(byte_im, use_container_width=True)
else:
    # AFFICHAGE CLASSIQUE POUR LES ÉLÈVES
    recherche = st.text_input("Rechercher une application par mot-clé (ex: vecteur, dérivée, statistique...)", "")

    if recherche:
        st.subheader("Résultats de la recherche")
        resultats = [app for app in applications if recherche.lower() in app["nom"].lower() or recherche.lower() in app["theme"].lower()]
        if resultats:
            for app in resultats:
                afficher_app_avec_qrcode(app["nom"], app["url"])
                st.write(f"Niveau : {app['niveau']} | Thème : {app['theme']}")
                st.markdown("---")
        else:
            st.warning("Aucune application ne correspond à votre recherche.")
    else:
        onglet_2nde_CAP, onglet_1ere, onglet_tale = st.tabs(["SECONDE BAC PRO ET CAP", "PREMIERE BAC PRO", "TERMINALE BAC PRO"])

        with onglet_2nde_CAP:
            st.info("Applications dédiées au programme de Seconde et CAP.")
            apps_2nde = [app for app in applications if app["niveau"] in ["2nde", "CAP"]]
            themes_2nde = sorted(list(set([app["theme"] for app in apps_2nde])))
            for theme in themes_2nde:
                with st.expander(theme):
                    for app in apps_2nde:
                        if app["theme"] == theme:
                            afficher_app_avec_qrcode(app["nom"], app["url"])

        with onglet_1ere:
            st.info("Applications dédiées au programme de Première.")
            apps_1ere = [app for app in applications if app["niveau"] == "1ere"]
            themes_1ere = sorted(list(set([app["theme"] for app in apps_1ere])))
            for theme in themes_1ere:
                with st.expander(theme):
                    for app in apps_1ere:

                        if app["theme"] == theme:
                            afficher_app_avec_qrcode(app["nom"], app["url"])

        with onglet_tale:
            st.info("Applications dédiées au programme de Terminale.")
            apps_tale = [app for app in applications if app["niveau"] == "Tale"]
            themes_tale = sorted(list(set([app["theme"] for app in apps_tale])))
            for theme in themes_tale:
                with st.expander(theme):
                    for app in apps_tale:
                        if app["theme"] == theme:
                            afficher_app_avec_qrcode(app["nom"], app["url"])



                        
