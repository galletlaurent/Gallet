# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application trajectoire",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# Vos importations d'origine propres et saines se placent juste en dessous
from datetime import datetime
import math
import os
import random
import time
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application trajectoire")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)


if "identifie" not in st.session_state:
    st.session_state.identifie = False
if "nom_var" not in st.session_state:
    st.session_state.nom_var = ""
if "prenom_var" not in st.session_state:
    st.session_state.prenom_var = ""
if "classe_var" not in st.session_state:
    st.session_state.classe_var = ""
if "verrouille" not in st.session_state:
    st.session_state.verrouille = False
BASE_DIR = os.path.abspath(".")

def charger_image(nom_fichier):
    nom_fichier = os.path.basename(nom_fichier)
    # Python scanne automatiquement tous les dossiers présents à côté du script
    for element in os.listdir(BASE_DIR):
        chemin_dossier = os.path.join(BASE_DIR, element)
        if os.path.isdir(chemin_dossier) and element.startswith("image"):
            chemin_image = os.path.join(chemin_dossier, nom_fichier)
            if os.path.exists(chemin_image):
                try:
                    return Image.open(chemin_image)
                except Exception:
                    pass
                        
    # Sécurité si l'application est déjà masquée dans fichiers_systemes
    chemin_secours = os.path.join(BASE_DIR, "image", nom_fichier)
    if os.path.exists(chemin_secours):
        try: 
            return Image.open(chemin_secours)
        except Exception: 
            pass
    return None

# --- TOUS LES CORRECTIFS SÉCURISÉS (RERUN, COLUMNS, CONTAINER, IMAGE) ---

# 1. Sauvegarde STRICTE des fonctions d'origine AVANT modification
_vrai_st_rerun = st.rerun if hasattr(st, "rerun") else (st.experimental_rerun if hasattr(st, "experimental_rerun") else None)
_vrai_st_image = st.image
_vrai_st_columns = st.columns
_vrai_st_container = st.container

# 2. Correctif pour st.rerun
def safe_rerun():
    if _vrai_st_rerun is not None:
        try: 
            _vrai_st_rerun()
        except Exception:
            from streamlit.runtime.scriptrunner import RerunData, RerunException
            raise RerunException(RerunData())
st.rerun = safe_rerun

import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
mpl.rcParams['mathtext.default'] = 'regular'

# 3. Correctif pour st.image (Résolution de la boucle infinie)
def safe_image(image, *args, **kwargs):
    if "use_container_width" in kwargs:
        kwargs["use_column_width"] = kwargs.pop("use_container_width")
    if isinstance(image, str) and not image.startswith(("http://", "https://", "data:image")):
        nom_fichier = os.path.basename(image)
        img_pil = charger_image(nom_fichier)
        if img_pil is not None: 
            image = img_pil
    return _vrai_st_image(image, *args, **kwargs)  # Utilise la vraie fonction d'origine
st.image = safe_image

# 4. Interception pour st.columns (vertical_alignment)
def safe_columns(*args, **kwargs):
    if "vertical_alignment" in kwargs:
        kwargs.pop("vertical_alignment")
    return _vrai_st_columns(*args, **kwargs)
st.columns = safe_columns

# 5. Interception pour st.container (border)
def safe_container(*args, **kwargs):
    if "border" in kwargs:
        kwargs.pop("border")
    return _vrai_st_container(*args, **kwargs)
st.container = safe_container

# 6. Rétrocompatibilité st.toggle -> st.checkbox
if not hasattr(st, "toggle"):
    def safe_toggle(label, value=False, key=None, **kwargs):
        return st.checkbox(label, value=value, key=key)
    st.toggle = safe_toggle

# 7. Rétrocompatibilité st.dialog
if not hasattr(st, "dialog"):
    def safe_dialog(*args, **kwargs):
        return st.container()
    st.dialog = safe_dialog

# 8. Décorateur pour sécuriser l'état des widgets (Session State)
def securiser_widget_factory(fonction_origine):
    def safe_widget(*args, **kwargs):
        cle = kwargs.get("key")
        if cle and cle in st.session_state:
            kwargs.pop("value", None)
        return fonction_origine(*args, **kwargs)
    return safe_widget



# =============================================================================
# FONCTIONS GLOBALES DE VALIDATION DE L'IDENTITÉ
# =============================================================================
def valider_saisie():
    """Vérifie les informations d'identification saisies par l'élève,

    les normalise en mémoire et verrouille définitivement le formulaire.
    """
    # Nettoyage et normalisation des textes saisis en session
    nom_clean = str(st.session_state.get("nom_var", "")).strip().upper()
    prenom_clean = str(st.session_state.get("prenom_var", "")).strip().capitalize()
    classe_clean = str(st.session_state.get("classe_var", "")).strip().upper()

    # Filtre de sécurité : empêche de valider si un champ est vide ou non modifié
    if not nom_clean or not prenom_clean or not classe_clean or nom_clean in ["NOM", "ELEVE", "INCONNU"]:
        st.error("Erreur : Veuillez compléter entièrement vos données d'identification avant de valider.")
        st.session_state.verrouille = False
    else:
        # Enregistrement des valeurs propres et verrouillage de la session
        st.session_state.nom_var = nom_clean
        st.session_state.prenom_var = prenom_clean
        st.session_state.classe_var = classe_clean
        st.session_state.verrouille = True
        
        st.success(f"Identification réussie pour : {nom_clean} {prenom_clean} ({classe_clean}).")
        st.rerun()

def valider_session():
    """Fonction passerelle de sécurité pour l'ouverture des droits d'ateliers."""
    valider_saisie()

# =============================================================================
# PRÉPARATION DU NOM DE FICHIER ET CONFIGURATION DES ONGLETS
# =============================================================================
def preparer_nom_fichier(nom_onglet):
    """Génère un nom de fichier standardisé et unique pour l'export des rapports."""
    from datetime import datetime

    # Récupération et formatage des chaînes sans espaces
    nom_propre = str(st.session_state.get("nom_var", "ELEVE")).replace(" ", "_")
    prenom_propre = str(st.session_state.get("prenom_var", "PRENOM")).replace(" ", "_")
    classe_propre = str(st.session_state.get("classe_var", "GROUPE")).replace(" ", "_")

    # Horodatage dynamique à la seconde près
    maintenant = datetime.now()
    heure_actuelle = maintenant.strftime("%H-%M-%S")
    date_texte = maintenant.strftime("%Y-%m-%d_%Hh%M")

    # Assemblage de la chaîne finale pour le téléchargement
    return f"{nom_propre}_{prenom_propre}_{classe_propre}_{date_texte}_{heure_actuelle}_{nom_onglet}.txt"


onglets = st.tabs([
    "Identification",
    "Force de pesanteur",
    "Force magnétique",
    "Force électrique",
    "Force gravitationnelle",
    "Force centrifuge",
    "Force de rappel d'un ressort",
    "Force de frottement fluide",
    "Force centripède",
    "Force d'Archimède",
    "Force de friction",
    "Force de tension d'une corde",
    "Force d'e propulsion",
    "Force de résistance aérodynamique",
    "Force d'impact d'un choc routier",
    "Force d'arrachement d'un vérin",
    "Force de freinage hydraulique"  
])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]
tab6 = onglets[6] 
tab7 = onglets[7] 
tab8 = onglets[8]
tab9 = onglets[9] 
tab10 = onglets[10]
tab11 = onglets[11]
tab12 = onglets[12] 
tab13 = onglets[13]
tab14 = onglets[14]
tab15 = onglets[15] 
tab16 = onglets[16]



with tab0:
    st.subheader("Identification de l'élève")
    st.write("Veuillez renseigner vos informations pour déverrouiller l'accès aux ateliers pratiques.")
    
    col_ident_1, col_ident_2 = st.columns(2)
    
    with col_ident_1:
        # Les champs de texte lisent et écrivent directement dans le Session State
        # Ils se bloquent automatiquement dès que le bouton OK a été cliqué
        nom_brut = st.text_input(
            "Nom de famille :",
            value=st.session_state.get("nom_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="widget_saisie_nom_maitre"
        )
        
        prenom_brut = st.text_input(
            "Prénom :",
            value=st.session_state.get("prenom_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="widget_saisie_prenom_maitre"
        )
        
        classe_brut = st.text_input(
            "Groupe / Classe :",
            value=st.session_state.get("classe_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="widget_saisie_classe_maitre"
        )
        
        # Synchronisation et normalisation immédiate des chaînes de texte
        st.session_state.nom_var = nom_brut.strip().upper()
        st.session_state.prenom_var = prenom_brut.strip().capitalize()
        st.session_state.classe_var = classe_brut.strip().upper()
        
        st.write("")
        
        # Bouton maître de validation d'accès
        if st.button(
            "Valider mes informations (OK)", 
            key="btn_validation_identité_maitre",
            disabled=st.session_state.get("vérrouillé", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("vérrouillé", False):
                st.rerun()

with tab1:
    st.set_page_config(page_title="Physique Interactive : Force de Pesanteur", layout="wide")

    histp1, histp2 = st.columns(2)
    with histp1:
        st.subheader("Historique")
        try:
            st.image("histpesanteur.jpg", caption="la pesanteur.",width=600)
        except Exception:
            st.error("Fichier impesanteur.jpg introuvable.")
    with histp2:
        try:
        st.subheader("BD humoristique")
            st.image("humpesanteur.jpg", caption="la pesanteur.",width=600)
        except Exception:
            st.error("Fichier impesanteur.jpg introuvable.")
            
    st.title("Laboratoire Interactif : La Force de Pesanteur (Le Poids)")
    st.write("Modifiez la masse et la gravité pour observer l'évolution de la force de pesanteur.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_pesanteur.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo de démonstration au format AVI (ex: chute d'un objet ou balance)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_pesanteur.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")
        try:
            st.image("pesanteur.jpg", caption="la pesanteur.",width=600)
        except Exception:
            st.error("Fichier pesanteur.jpg introuvable.")

            
    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Dictionnaire des gravités de référence dans le système solaire (en m/s²)
        dict_gravite = {
            "Lune (1.62 m/s²)": 1.62,
            "Mars (3.71 m/s²)": 3.71,
            "Terre (9.81 m/s²)": 9.81,
            "Neptune (11.15 m/s²)": 11.15,
            "Jupiter (24.79 m/s²)": 24.79
        }
        
        # Sélection de la planète / astre
        astre_selectionne = st.selectbox("Choisir l'astre de référence :", list(dict_gravite.keys()), index=2)
        g_astre = dict_gravite[astre_selectionne]
        
        # Curseur pour faire varier la masse de 0 à 100 kg
        masse = np.linspace(0, 100, 100)
        
        # Formule du poids : P = m * g
        poids = masse * g_astre
        
        data_chart = pd.DataFrame({
            "Masse (kg)": masse,
            "Poids / Force de Pesanteur (Newtons)": poids
        })
        
        # Affichage du graphique interactif
        st.line_chart(data_chart, x="Masse (kg)", y="Poids / Force de Pesanteur (Newtons)")
        
        # Affichage d'une valeur fixe pour l'exemple (ex: pour 50 kg)
        poids_50kg = 50 * g_astre
        st.metric(label=f"Poids d'un objet de 50 kg sur cet astre", value=f"{poids_50kg:.2f} N")

with tab2:
    st.set_page_config(page_title="Physique Interactive : Force Magnétique", layout="wide")

    histmagne1, histmagne2 = st.columns(2)
    with histmagne1:
        st.subheader("Historique")
    with histmagne2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force Magnétique (Loi de Lorentz)")
    st.write("Modifiez l'intensité du champ magnétique et la charge de la particule pour observer l'évolution de la force magnétique.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_magnetique.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo de démonstration au format AVI (ex: déviation d'un faisceau d'électrons ou aimant)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_magnetique.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Curseurs interactifs
        # Charge en Coulombs (échelle en micro-Coulombs pour des valeurs perceptibles)
        charge_micro = st.slider("Charge de la particule (q en micro-Coulombs)", min_value=1.0, max_value=500.0, value=50.0, step=5.0)
        # Champ magnétique en Teslas (1 Tesla est un champ très puissant)
        champ_B = st.slider("Intensité du champ magnétique (B en Teslas)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        
        # Conversion de la charge en Coulombs (1 micro-Coulomb = 1e-6 C)
        q_coulomb = charge_micro * 1e-6
        
        # Variation de la vitesse de la particule de 0 à 100 000 m/s
        vitesse = np.linspace(0, 100000, 500)
        
        # Formule de la force magnétique (perpendiculaire) : F = q * v * B
        force_mag = q_coulomb * vitesse * champ_B
        
        data_chart = pd.DataFrame({
            "Vitesse (m/s)": vitesse,
            "Force Magnétique (Newtons)": force_mag
        })
        
        # Affichage du graphique interactif
        st.line_chart(data_chart, x="Vitesse (m/s)", y="Force Magnétique (Newtons)")
        
        # Calcul et affichage de la force à une vitesse de 50 000 m/s
        force_50k = q_coulomb * 50000 * champ_B
        st.metric(label="Force Magnétique (à v = 50 000 m/s)", value=f"{force_50k:.4f} N")

with tab3:
    st.set_page_config(page_title="Physique Interactive : Force Électrique", layout="wide")

    histelec1, histelec2 = st.columns(2)
    with histelec1:
        st.subheader("Historique")
    with histelec2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force Électrique (Loi de Coulomb)")
    st.write("Modifiez les charges électriques pour observer l'évolution de la force en fonction de la distance.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_electrique.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo de démonstration au format AVI (ex: électrostatique ou ballons qui se repoussent)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_electrique.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Constante de Coulomb
        k = 8.9875517923e9
        
        # Curseurs interactifs pour les charges en micro-Coulombs
        charge_1 = st.slider("Valeur de la charge q1 (en micro-Coulombs)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
        charge_2 = st.slider("Valeur de la charge q2 (en micro-Coulombs)", min_value=1.0, max_value=50.0, value=20.0, step=1.0)
        
        # Conversion des micro-Coulombs en Coulombs (1 uC = 1e-6 C)
        q1_c = charge_1 * 1e-6
        q2_c = charge_2 * 1e-6
        
        # Variation de la distance de 0.05 mètre (5 cm) à 2 mètres
        distance = np.linspace(0.05, 2.0, 300)
        
        # Formule de Coulomb : F = k * |q1 * q2| / d^2
        force_elec = k * (q1_c * q2_c) / (distance ** 2)
        
        data_chart = pd.DataFrame({
            "Distance (mètres)": distance,
            "Force Électrique (Newtons)": force_elec
        })
        
        # Affichage du graphique interactif
        st.line_chart(data_chart, x="Distance (mètres)", y="Force Électrique (Newtons)")
        
        # Calcul et affichage de la force à une distance proche (10 cm = 0.1 m)
        force_10cm = k * (q1_c * q2_c) / (0.1 ** 2)
        st.metric(label="Force Électrique à une distance de 10 cm", value=f"{force_10cm:.2f} N")


with tab4:
    st.set_page_config(page_title="Physique Interactive : Force Gravitationnelle", layout="wide")

    histgrav1, histgrav2 = st.columns(2)
    with histgrav1:
        st.subheader("Historique")
    with histgrav2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force Gravitationnelle")
    st.write("Modifiez les masses et la distance pour observer l'évolution de l'attraction gravitationnelle.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_gravite.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo de démonstration au format AVI (ex: chute libre ou orbite)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_gravite.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Constante de gravitation universelle
        G = 6.6743e-11
        
        # Curseurs interactifs pour les masses (valeurs élevées pour obtenir des Newtons perceptibles)
        masse_1 = st.slider("Masse du premier corps (m1 en millions de tonnes)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        masse_2 = st.slider("Masse du second corps (m2 en millions de tonnes)", min_value=1.0, max_value=100.0, value=50.0, step=1.0)
        
        # Conversion des valeurs des curseurs en kilogrammes (1 million de tonnes = 1e9 kg)
        m1_kg = masse_1 * 1e9
        m2_kg = masse_2 * 1e9
        
        # Variation de la distance de 10 à 500 mètres
        distance = np.linspace(10, 500, 200)
        
        # Formule de Newton : F = G * (m1 * m2) / d^2
        force = G * (m1_kg * m2_kg) / (distance ** 2)
        
        data_chart = pd.DataFrame({
            "Distance (mètres)": distance,
            "Force Gravitationnelle (Newtons)": force
        })
        
        # Affichage du graphique interactif
        st.line_chart(data_chart, x="Distance (mètres)", y="Force Gravitationnelle (Newtons)")
        
        # Calcul et affichage de la force à une distance proche (10 mètres)
        force_max = G * (m1_kg * m2_kg) / (10 ** 2)
        st.metric(label="Force Gravitationnelle Maximale (à 10 mètres)", value=f"{force_max:.2f} N")


with tab5:
    st.set_page_config(page_title="Physique Interactive : Force Centrifuge", layout="wide")

    histgcentfu1, histcentfu2 = st.columns(2)
    with histcentfu1:
        st.subheader("Historique")
    with histcentfu2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force Centrifuge")
    st.write("Modifiez les paramètres à l'aide des curseurs pour voir l'impact direct sur la force apparente.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_centrifuge.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo de démonstration au format AVI")
        except FileNotFoundError:
            st.warning("Fichier 'demo_centrifuge.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Curseurs interactifs
        masse = st.slider("Masse de l'objet (m en kg)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="masse_centrifuge")
        rayon = st.slider("Rayon de rotation (r en mètres)", min_value=0.5, max_value=3.0, value=1.5, step=0.1)
        
        vitesse_angulaire = np.linspace(0, 10, 100)
        force = masse * (vitesse_angulaire ** 2) * rayon
        
        data_chart = pd.DataFrame({
            "Vitesse Angulaire (rad/s)": vitesse_angulaire,
            "Force Centrifuge (Newtons)": force
        })
        
        st.line_chart(data_chart, x="Vitesse Angulaire (rad/s)", y="Force Centrifuge (Newtons)")
        
        force_max = masse * (10 ** 2) * rayon
        st.metric(label="Force Centrifuge Maximale (à 10 rad/s)", value=f"{force_max:.2f} N")


with tab6:
    st.set_page_config(page_title="Physique Interactive : Loi de Hooke", layout="wide")

    histgressort1, histressort2 = st.columns(2)
    with histressort1:
        st.subheader("Historique")
    with histressort2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : Force de Rappel d'un Ressort")
    st.write("Modifiez la raideur du ressort pour observer la force générée selon son allongement.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_ressort.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: oscillation ou étirement d'un ressort)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_ressort.avi' introuvable. Vidéo alternative :")
            st.video("https://www.youtube.com/watch?v=dKBCNUfZSQk")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Curseur pour la raideur du ressort k
        raideur_k = st.slider("Raideur du ressort (k en N/m)", min_value=10, max_value=500, value=100, step=10)
        
        # Allongement de 0 à 0.5 mètre (50 cm)
        allongement_x = np.linspace(0, 0.5, 100)
        force_ressort = raideur_k * allongement_x
        
        data_chart = pd.DataFrame({
            "Allongement (mètres)": allongement_x,
            "Force de Rappel (Newtons)": force_ressort
        })
        
        st.line_chart(data_chart, x="Allongement (mètres)", y="Force de Rappel (Newtons)")
        
        force_max = raideur_k * 0.5
        st.metric(label="Force pour un étirement de 50 cm", value=f"{force_max:.2f} N")


with tab7:
    st.set_page_config(page_title="Physique Interactive : Frottement Fluide", layout="wide")

    histfrotflu1, histfrotflu2 = st.columns(2)
    with histfrotflu1:
        st.subheader("Historique")
    with histfrotflu2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force de Frottement Fluide")
    st.write("Modifiez le coefficient de frottement pour observer la résistance du fluide en fonction de la vitesse.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_frottement.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: parachute ou bille dans l'huile)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_frottement.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Curseur pour le coefficient de traînée c
        c_coefficient = st.slider("Coefficient de friction (c en kg/s)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        
        # Plage de vitesse de 0 à 50 m/s
        vitesse = np.linspace(0, 50, 200)
        force_frottement = c_coefficient * vitesse
        
        data_chart = pd.DataFrame({
            "Vitesse (m/s)": vitesse,
            "Force de Frottement (Newtons)": force_frottement
        })
        
        st.line_chart(data_chart, x="Vitesse (m/s)", y="Force de Frottement (Newtons)")
        
        force_a_30ms = c_coefficient * 30
        st.metric(label="Force de résistance à 30 m/s", value=f"{force_a_30ms:.2f} N")


with tab8:
    st.set_page_config(page_title="Physique Interactive : Force Centripète", layout="wide")

    histcentipede1, histcentipede2 = st.columns(2)
    with histcentipede1:
        st.subheader("Historique")
    with histcentipede2:
        st.subheader("BD humoristique")


    st.title("Laboratoire Interactif : La Force Centripète")
    st.write("Modifiez la masse et le rayon de la trajectoire pour observer la force requise pour maintenir le mouvement circulaire.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_centripete.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: objet tournant au bout d'une ficelle)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_centripete.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        masse = st.slider("Masse de l'objet (m en kg)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="masse_centripete")
        rayon = st.slider("Rayon du virage (r en mètres)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
        
        # Variation de la vitesse linéaire de 0 à 20 m/s
        vitesse = np.linspace(0, 20, 150)
        force_centripete = (masse * (vitesse ** 2)) / rayon
        
        data_chart = pd.DataFrame({
            "Vitesse (m/s)": vitesse,
            "Force Centripète (Newtons)": force_centripete
        })
        
        st.line_chart(data_chart, x="Vitesse (m/s)", y="Force Centripète (Newtons)")
        
        force_a_15ms = (masse * (15 ** 2)) / rayon
        st.metric(label="Force Centripète requise à 15 m/s", value=f"{force_a_15ms:.2f} N")


with tab9:
    st.set_page_config(page_title="Physique Interactive : Poussée d'Archimède", layout="wide")

    histarchi1, histarchi2 = st.columns(2)
    with histarchi1:
        st.subheader("Historique")
    with histarchi2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactive : La Poussée d'Archimède")
    st.write("Modifiez le volume de l'objet et le fluide pour observer la force d'Archimède s'exerçant de bas en haut.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_archimede.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: objet flottant ou mesure avec un dynamomètre)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_archimede.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Dictionnaire des masses volumiques des fluides courants (en kg/m³)
        dict_fluides = {
            "Huile d'olive (920 kg/m³)": 920,
            "Eau douce (1000 kg/m³)": 1000,
            "Eau de mer (1025 kg/m³)": 1025,
            "Glycérine (1260 kg/m³)": 1260
        }
        
        # Constante de pesanteur sur Terre
        g = 9.81
        
        # Sélection du fluide via une boîte de choix
        fluide_selectionne = st.selectbox("Choisir le fluide environnant :", list(dict_fluides.keys()), index=1)
        rho_fluide = dict_fluides[fluide_selectionne]
        
        # Curseur pour le volume maximal de l'objet (converti pour l'affichage en Litres)
        volume_max_litres = st.slider("Volume total disponible de l'objet (en Litres)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
        
        # Génération d'une plage de volume immergé allant de 0 au volume maximum (en m³, 1 L = 0.001 m³)
        volume_immerge_m3 = np.linspace(0, volume_max_litres * 0.001, 150)
        
        # Formule d'Archimède : Fa = rho * V * g
        poussee_archimede = rho_fluide * volume_immerge_m3 * g
        
        # Conversion de l'axe X en Litres pour une lecture plus intuitive par les élèves
        volume_immerge_litres = volume_immerge_m3 * 1000
        
        data_chart = pd.DataFrame({
            "Volume Immergé (Litres)": volume_immerge_litres,
            "Poussée d'Archimède (Newtons)": poussee_archimede
        })
        
        # Affichage du graphique interactif
        st.line_chart(data_chart, x="Volume Immergé (Litres)", y="Poussée d'Archimède (Newtons)")
        
        # Calcul de la force maximale lorsque l'objet est totalement immergé
        force_max = rho_fluide * (volume_max_litres * 0.001) * g
        st.metric(label="Poussée d'Archimède maximale (objet 100% immergé)", value=f"{force_max:.2f} N")

with tab10:
    st.set_page_config(page_title="Physique Interactive : Friction Solide", layout="wide")

    histfric1, histfric2 = st.columns(2)
    with histfric1:
        st.subheader("Historique")
    with histfric2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force de Friction Solide")
    st.write("Sélectionnez les matériaux en contact et modifiez la masse pour observer la transition entre frottement statique et cinétique.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        
        # Intégrer la vidéo locale au format AVI
        try:
            video_file = open("demo_friction.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: bloc tiré par un dynamomètre ou plan incliné)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_friction.avi' introuvable. Affichage d'une vidéo de démonstration alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Dictionnaire des coefficients de frottement (statique, cinétique) selon les surfaces
        dict_surfaces = {
            "Acier sur Glace (Très faible : 0.10 / 0.05)": (0.10, 0.05),
            "Bois sur Bois (Moyen : 0.50 / 0.30)": (0.50, 0.30),
            "Pneu sur Asphalte sec (Élevé : 0.90 / 0.70)": (0.90, 0.70),
        }
        
        # Sélection du couple de matériaux
        interface_choisie = st.selectbox("Nature des surfaces en contact :", list(dict_surfaces.keys()), index=1)
        mu_s, mu_c = dict_surfaces[interface_choisie]
        
        # Curseur pour la masse du bloc en kilogrammes
        masse = st.slider("Masse du bloc (m en kg)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
        
        # Calcul de la force normale N (Poids = m * g sur une surface plane)
        g = 9.81
        N = masse * g
        
        # Génération d'une plage de force de traction appliquée (de 0 à 150 Newtons)
        force_traction = np.linspace(0, 150, 300)
        
        # Calcul du seuil de glissement (Force statique maximale)
        seuil_statique = mu_s * N
        force_friction_effective = []
        
        for f in force_traction:
            if f < seuil_statique:
                # Tant que l'objet ne bouge pas, la friction équilibre exactement la traction
                force_friction_effective.append(f)
            else:
                # Dès que ça glisse, la friction retombe et stagne à la valeur cinétique
                force_friction_effective.append(mu_c * N)
                
        data_chart = pd.DataFrame({
            "Force de Traction appliquée (Newtons)": force_traction,
            "Force de Friction mesurée (Newtons)": force_friction_effective
        })
        
        # Affichage du graphique interactif
        st.line_chart(data_chart, x="Force de Traction appliquée (Newtons)", y="Force de Friction mesurée (Newtons)")
        
        # Affichage des métriques clés
        st.metric(label="Force nécessaire pour démarrer le mouvement (Seuil statique)", value=f"{seuil_statique:.2f} N")


with tab11:
    st.set_page_config(page_title="Physique Interactive : Tension de Corde", layout="wide")

    histcorde1, histcorde2 = st.columns(2)
    with histcorde1:
        st.subheader("Historique")
    with histcorde2:
        st.subheader("BD humoristique")


    st.title("Laboratoire Interactif : La Force de Tension (Machine d'Atwood)")
    st.write("Modifiez la masse fixe et faites varier la masse suspendue pour observer l'évolution de la tension du câble.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_tension.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: poulie, ascenseur ou contrepoids)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_tension.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        g = 9.81
        masse_fixe = st.slider("Masse de référence m1 (en kg)", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
        
        # Faire varier la seconde masse de 0 à 50 kg
        masse_variable = np.linspace(0.1, 50, 200)
        
        # Formule de la tension dans une machine d'Atwood
        tension = (2 * masse_fixe * masse_variable) / (masse_fixe + masse_variable) * g
        
        data_chart = pd.DataFrame({
            "Masse Variable m2 (kg)": masse_variable,
            "Tension du Câble (Newtons)": tension
        })
        
        st.line_chart(data_chart, x="Masse Variable m2 (kg)", y="Tension du Câble (Newtons)")
        
        # Équilibre parfait quand m1 = m2
        tension_equilibre = masse_fixe * g
        st.metric(label=f"Tension à l'équilibre statique (si m2 = {masse_fixe} kg)", value=f"{tension_equilibre:.2f} N")



with tab12:
    st.set_page_config(page_title="Physique Interactive : Force de Poussée", layout="wide")

    histpropulsion1, histpropulsion2 = st.columns(2)
    with histpropulsion1:
        st.subheader("Historique")
    with histpropulsion2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force de Poussée (Propulsion)")
    st.write("Modifiez le débit de matière éjectée pour observer la force de poussée en fonction de la vitesse d'éjection.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_poussee.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: ballon qui se dégonfle ou hélice)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_poussee.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        debit_massique = st.slider("Débit de matière éjectée (qm en kg/s)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        
        # Vitesse d'éjection du fluide de 0 à 1000 m/s
        vitesse_ejection = np.linspace(0, 1000, 200)
        poussee = debit_massique * vitesse_ejection
        
        data_chart = pd.DataFrame({
            "Vitesse d'Éjection (m/s)": vitesse_ejection,
            "Force de Poussée (Newtons)": poussee
        })
        
        st.line_chart(data_chart, x="Vitesse d'Éjection (m/s)", y="Force de Poussée (Newtons)")
        
        poussee_max = debit_massique * 1000
        st.metric(label="Force de poussée maximale (à 1000 m/s)", value=f"{poussee_max:.2f} N")


with tab13:
    st.set_page_config(page_title="Physique Interactive : Traînée Aérodynamique", layout="wide")

    histaero1, histaero2 = st.columns(2)
    with histaero1:
        st.subheader("Historique")
    with histaero2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : La Force de Traînée Aérodynamique")
    st.write("Modifiez le profil de l'objet pour observer la résistance de l'air à haute vitesse.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_trainee.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: soufflerie ou voiture en mouvement)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_trainee.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Masse volumique de l'air au niveau de la mer (kg/m3)
        rho_air = 1.225
        
        dict_profils = {
            "Profil aérodynamique / Goutte (Cx = 0.05)": 0.05,
            "Voiture moderne standard (Cx = 0.30)": 0.30,
            "Plaque plane face au flux (Cx = 1.20)": 1.20
        }
        
        profil_choisi = st.selectbox("Forme géométrique de l'objet :", list(dict_profils.keys()), index=1)
        cx = dict_profils[profil_choisi]
        
        surface = st.slider("Surface frontale exposée (S en m²)", min_value=0.1, max_value=4.0, value=1.5, step=0.1)
        
        # Vitesse de 0 à 130 km/h (convertie de 0 à 36 m/s pour la formule)
        vitesse_ms = np.linspace(0, 36, 150)
        trainee = 0.5 * rho_air * surface * cx * (vitesse_ms ** 2)
        
        # Conversion en km/h pour l'affichage public
        vitesse_kmh = vitesse_ms * 3.6
        
        data_chart = pd.DataFrame({
            "Vitesse (km/h)": vitesse_kmh,
            "Force de Traînée (Newtons)": trainee
        })
        
        st.line_chart(data_chart, x="Vitesse (km/h)", y="Force de Traînée (Newtons)")
        
        force_a_130 = 0.5 * rho_air * surface * cx * (36 ** 2)
        st.metric(label="Résistance de l'air à 130 km/h", value=f"{force_a_130:.2f} N")

with tab14:
    st.set_page_config(page_title="Sécurité Routière : Force d'Impact", layout="wide")

    histchoc1, histchoc2 = st.columns(2)
    with histchoc1:
        st.subheader("Historique")
    with histchoc2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : Force d'Impact d'un Accident de la Route")
    st.write("Ajustez la masse du véhicule et observez la croissance exponentielle de la force de collision avec la vitesse.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_choc.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: crash-test ou freinage manqué)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_choc.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Choix du véhicule (Voiture standard vs Camion TP chargé)
        masse_kg = st.slider("Masse totale du véhicule (en kg)", min_value=1000, max_value=40000, value=1500, step=500, key="masse_choc_routier")

        # Distance de déformation de la carrosserie / zone d'impact en mètres (ex: 0.8 mètre)
        distance_arret = st.slider("Distance de déformation lors du choc (en mètres)", min_value=0.2, max_value=2.0, value=0.8, step=0.1)
        
        # Plage de vitesse de 0 à 130 km/h (convertie en m/s pour la formule)
        vitesse_kmh = np.linspace(5, 130, 150)
        vitesse_ms = vitesse_kmh / 3.6
        
        # Formule de la force d'impact moyenne
        force_impact = (masse_kg * (vitesse_ms ** 2)) / (2 * distance_arret)
        
        # Conversion en tonnes-force pour marquer les esprits des conducteurs
        force_tonnes = force_impact / 9810.0
        
        data_chart = pd.DataFrame({
            "Vitesse initiale (km/h)": vitesse_kmh,
            "Force équivalente de l'impact (en Tonnes)": force_tonnes
        })
        
        st.line_chart(data_chart, x="Vitesse initiale (km/h)", y="Force équivalente de l'impact (en Tonnes)")
        
        # Exemple marquant à 50 km/h en agglomération
        v_50_ms = 50 / 3.6
        impact_50 = ((masse_kg * (v_50_ms ** 2)) / (2 * distance_arret)) / 9810.0
        st.metric(label="Poids d'impact équivalent lors d'un choc à 50 km/h", value=f"{impact_50:.1f} Tonnes")


with tab15:
    st.set_page_config(page_title="TP : Force de Vérin Hydraulique", layout="wide")

    histverin1, histverin2 = st.columns(2)
    with histverin1:
        st.subheader("Historique")
    with histverin2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : Force d'Arrachement de Vérin (Pelle Hydraulique)")
    st.write("Modifiez le diamètre de l'alésage du vérin pour voir la force maximale disponible pour creuser.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_verin.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: mouvement de godet ou levage de benne)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_verin.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Diamètre d'alésage du vérin (gros engins TP)
        alesage_mm = st.slider("Diamètre d'alésage du vérin (en mm)", min_value=50, max_value=250, value=120, step=5)
        surface_m2 = np.pi * ((alesage_mm / 1000.0) ** 2) / 4.0
        
        # Variation de la pression de la pompe hydraulique de 0 à 350 Bars (pression TP classique)
        pression_bar = np.linspace(0, 350, 150)
        pression_pa = pression_bar * 100000
        
        # Force en Newtons, convertie en Kilonewtons (kN) pour le secteur des TP
        force_kn = (pression_pa * surface_m2) / 1000.0
        
        data_chart = pd.DataFrame({
            "Pression Hydraulique (Bars)": pression_bar,
            "Force du Vérin (kN)": force_kn
        })
        
        st.line_chart(data_chart, x="Pression Hydraulique (Bars)", y="Force du Vérin (kN)")
        
        # Affichage de la capacité de levage équivalente en tonnes à la pression maximale de 350 Bars
        charge_tonnes = ((350 * 100000) * surface_m2) / (9.81 * 1000.0)
        st.metric(label="Capacité de poussée max (à 350 Bars)", value=f"{charge_tonnes:.1f} Tonnes")


with tab16:
    st.set_page_config(page_title="Maintenance : Freinage Hydraulique", layout="wide")

    histfrein1, histfrein2 = st.columns(2)
    with histfrein1:
        st.subheader("Historique")
    with histfrein2:
        st.subheader("BD humoristique")

    st.title("Laboratoire Interactif : Force de Freinage Hydraulique")
    st.write("Modifiez le diamètre des pistons et la pression du circuit pour calculer la force de freinage appliquée au disque.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Démonstration Expérimentale")
        try:
            video_file = open("demo_freinage.avi", "rb")
            video_bytes = video_file.read()
            st.video(video_bytes, format="video/x-msvideo")
            st.caption("Votre vidéo au format AVI (ex: purge de freins ou banc d'essai d'un camion)")
        except FileNotFoundError:
            st.warning("Fichier 'demo_freinage.avi' introuvable. Vidéo alternative :")
            st.video("https://youtube.com")

    with col2:
        st.subheader("Paramètres Physiques et Graphique")
        
        # Diamètre du piston converti en surface (A = pi * r²)
        diametre_mm = st.slider("Diamètre des pistons de l'étrier (en mm)", min_value=30.0, max_value=90.0, value=60.0, step=2.0)
        rayon_m = (diametre_mm / 2.0) / 1000.0
        surface_piston = np.pi * (rayon_m ** 2)
        
        # Coefficient de friction des plaquettes de frein (usées vs neuves)
        mu_plaquette = st.slider("Coefficient de friction des plaquettes (mu)", min_value=0.1, max_value=0.6, value=0.4, step=0.05)
        
        # Variation de la pression hydraulique de 0 à 120 Bars (1 Bar = 100 000 Pa)
        pression_bar = np.linspace(0, 120, 200)
        pression_pa = pression_bar * 100000
        
        # Force de freinage pour un étrier à 2 pistons
        force_freinage = pression_pa * (surface_piston * 2) * mu_plaquette
        
        data_chart = pd.DataFrame({
            "Pression du Circuit (Bars)": pression_bar,
            "Force de Freinage (Newtons)": force_freinage
        })
        
        st.line_chart(data_chart, x="Pression du Circuit (Bars)", y="Force de Freinage (Newtons)")
        
        # Calcul à une pression standard de freinage d'urgence (80 Bars)
        force_a_80bars = (80 * 100000) * (surface_piston * 2) * mu_plaquette
        st.metric(label="Force de serrage à 80 Bars", value=f"{force_a_80bars:.2f} N")







