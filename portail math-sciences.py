# -*- coding: utf-8 -*-

import streamlit as st
import urllib.parse
import qrcode
import io

st.set_page_config(page_title="Hub Maths-sciences", layout="wide")

# Injection de styles CSS spécifiques pour le masquage à l'impression
st.markdown("""
<style>
@media print {
    /* Libere absolument toutes les structures de Streamlit */
    html, body, .main, .block-container, 
    [data-testid="stApp"], 
    [data-testid="stAppViewContainer"], 
    [data-testid="stVerticalBlock"], 
    [data-testid="stVerticalBlockBorderWrapper"],
    .stTabs, [data-testid="stTabContent"] {
        height: auto !important;
        overflow: visible !important;
        position: static !important;
        max-height: none !important;
        display: block !important;
    }
    
    /* Force la grille de colonnes a rester fluide */
    [data-testid="stHorizontalBlock"] {
        height: auto !important;
        overflow: visible !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }

    /* Force un saut de page propre apres chaque lot de 25 */
    .saut-de-page {
        page-break-after: always !important;
        break-after: page !important;
    }

    /* SECURITE INTERNE : Evite de couper une vignette en deux */
    [data-testid="stColumn"] > div {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
    }

    /* Cache toute l'interface Streamlit globale et les boutons systeme */
    header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], .stAppDeployButton,
    .stAppToolbar, [data-testid="stManageAppButton"], iframe, footer + div, .viewerBadge_v1 {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Cache le titre du portail, la description et la barre de recherche */
    h1, p, .stTextInput, .stSelectbox, .stAlert, [data-testid="stTabs"] nav {
        display: none !important;
    }
    
    /* Masque les boutons individuels de téléchargement pour l'impression */
    .stDownloadButton {
        display: none !important;
    }
    
    /* Supprime les marges superflues pour maximiser l'espace A4 */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
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


# Fonction utilitaire pour generer l'image du QR Code en memoire
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

# 2. Barre de recherche globale
recherche = st.text_input("Rechercher une application par mot-clé (ex: vecteur, dérivée, statistique...)", "")

# 3. Logique de filtrage et d'affichage
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
    # Organisation par onglets normaux + Onglet Récapitulatif
    onglet_2nde_CAP, onglet_1ere, onglet_tale, onglet_recap = st.tabs([
        "SECONDE BAC PRO ET CAP", 
        "PREMIERE BAC PRO", 
        "TERMINALE BAC PRO", 
        "RECAPITULATIF QR CODES"
    ])

    # Affichage Seconde et CAP
    with onglet_2nde_CAP:
        st.info("Applications dédiées au programme de Seconde et CAP.")
        apps_2nde = [app for app in applications if app["niveau"] in ["2nde", "CAP"]]
        themes_2nde = sorted(list(set([app["theme"] for app in apps_2nde])))
        for theme in themes_2nde:
            with st.expander(theme):
                for app in apps_2nde:
                    if app["theme"] == theme:
                        afficher_app_avec_qrcode(app["nom"], app["url"])

    # Affichage Premiere
    with onglet_1ere:
        st.info("Applications dédiées au programme de Première.")
        apps_1ere = [app for app in applications if app["niveau"] == "1ere"]
        themes_1ere = sorted(list(set([app["theme"] for app in apps_1ere])))
        for theme in themes_1ere:
            with st.expander(theme):
                for app in apps_1ere:
                    if app["theme"] == theme:
                        afficher_app_avec_qrcode(app["nom"], app["url"])

    # Affichage Terminale
    with onglet_tale:
        st.info("Applications dédiées au programme de Terminale.")
        apps_tale = [app for app in applications if app["niveau"] == "Tale"]
        themes_tale = sorted(list(set([app["theme"] for app in apps_tale])))
        for theme in themes_tale:
            with st.expander(theme):
                for app in apps_tale:
                    if app["theme"] == theme:
                        afficher_app_avec_qrcode(app["nom"], app["url"])
    with onglet_recap:
        st.info("Page récapitulative. Utilisez Ctrl + P pour imprimer par lots de 25 QR codes par page.")
        
        filtre_niveau = st.selectbox("Filtrer le récapitulatif par niveau :", ["Tous les niveaux", "Seconde et CAP", "Première", "Terminale"])
        
        if filtre_niveau == "Seconde et CAP":
            apps_recap = [app for app in applications if app["niveau"] in ["2nde", "CAP"]]
        elif filtre_niveau == "Première":
            apps_recap = [app for app in applications if app["niveau"] == "1ere"]
        elif filtre_niveau == "Terminale":
            apps_recap = [app for app in applications if app["niveau"] == "Tale"]
        else:
            apps_recap = applications

        # On decoupe la liste en sous-groupes de 25 applications maximum
        taille_lot = 25
        lots_applications = [apps_recap[i:i + taille_lot] for i in range(0, len(apps_recap), taille_lot)]
        
        # On parcourt chaque lot de 25
        for num_lot, lot in enumerate(lots_applications):
            
            # Conteneur principal pour ce bloc de 25
            with st.container(key=f"lot_impression_{num_lot}"):
                nb_colonnes = 5
                cols = st.columns(nb_colonnes)
                
                # Remplissage de la grille 5x5 pour le lot en cours
                for index, app in enumerate(lot):
                    col_active = cols[index % nb_colonnes]
                    
                    with col_active:
                        with st.container(border=True):
                            st.markdown(f"<div style='text-align: center; font-weight: bold; min-height: 40px; font-size: 13px;'>{app['nom']}</div>", unsafe_allow_html=True)
                            st.caption(f"{app['niveau']} | {app['theme']}")
                            
                            byte_im = generer_qrcode_image(app["url"])
                            st.image(byte_im, use_container_width=True)
                            
                            nom_fichier = f"qrcode_{app['nom'].lower().replace(' ', '_')}.png"
                            st.download_button(
                                label="Télécharger",
                                data=byte_im,
                                file_name=nom_fichier,
                                mime="image/png",
                                key=f"dl_lot_{num_lot}_{index}"
                            )
            
            # Si ce n'est pas le tout dernier bloc, on injecte un saut de page pour l'imprimante
            if num_lot < len(lots_applications) - 1:
                st.markdown('<div class="saut-de-page"></div>', unsafe_allow_html=True)



































                        
