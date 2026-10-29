# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application redox ",
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
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components
import sys
from PIL import Image
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application redox")
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
    "Historique",
    "Réaction d'oxydation",
    "Réaction de réduction",
    "Les couples redox",
    "La règle du gamma ",
    "Réaction d'oxydoréduction ",
    "Application dans le domaine du transport routier",
    "Application dans le domaine de la maintenance",
    "Application dans le domaine des travaux publics",
    "Application dans le domaine des géomètres"
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



bibliotheque_redox = {
    # --- HALOGÈNES ET DÉRIVÉS ---
    "F2 / F⁻": {
        "no_ox": "0", "no_red": "-I", "electrons": 2,
        "milieu_acide": r"\text{F}_2 + 2e^- \rightleftharpoons 2\text{F}^-",
        "milieu_basique": r"\text{F}_2 + 2e^- \rightleftharpoons 2\text{F}^-",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "Cl2 / Cl⁻": {
        "no_ox": "0", "no_red": "-I", "electrons": 2,
        "milieu_acide": r"\text{Cl}_2 + 2e^- \rightleftharpoons 2\text{Cl}^-",
        "milieu_basique": r"\text{Cl}_2 + 2e^- \rightleftharpoons 2\text{Cl}^-",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "Br2 / Br⁻": {
        "no_ox": "0", "no_red": "-I", "electrons": 2,
        "milieu_acide": r"\text{Br}_2 + 2e^- \rightleftharpoons 2\text{Br}^-",
        "milieu_basique": r"\text{Br}_2 + 2e^- \rightleftharpoons 2\text{Br}^-",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "I2 / I⁻": {
        "no_ox": "0", "no_red": "-I", "electrons": 2,
        "milieu_acide": r"\text{I}_2 + 2e^- \rightleftharpoons 2\text{I}^-",
        "milieu_basique": r"\text{I}_2 + 2e^- \rightleftharpoons 2\text{I}^-",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "ClO⁻ / Cl⁻ (Hypochlorite / Chlorure)": {
        "no_ox": "+I", "no_red": "-I", "electrons": 2,
        "milieu_acide": r"\text{ClO}^- + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{Cl}^- + 3\text{H}_2\text{O}",
        "milieu_basique": r"\text{ClO}^- + \text{H}_2\text{O} + 2e^- \rightleftharpoons \text{Cl}^- + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 3, "h2o_basique": 1
    },
    "ClO3⁻ / Cl⁻ (Chlorate / Chlorure)": {
        "no_ox": "+V", "no_red": "-I", "electrons": 6,
        "milieu_acide": r"\text{ClO}_3^- + 6\text{H}_3\text{O}^+ + 6e^- \rightleftharpoons \text{Cl}^- + 9\text{H}_2\text{O}",
        "milieu_basique": r"\text{ClO}_3^- + 3\text{H}_2\text{O} + 6e^- \rightleftharpoons \text{Cl}^- + 6\text{OH}^-",
        "h3o": 6, "oh": 6, "h2o_acide": 9, "h2o_basique": 3
    },
    "IO3⁻ / I2 (Iodate / Diode)": {
        "no_ox": "+V", "no_red": "0", "electrons": 10,
        "milieu_acide": r"2\text{IO}_3^- + 12\text{H}_3\text{O}^+ + 10e^- \rightleftharpoons \text{I}_2 + 18\text{H}_2\text{O}",
        "milieu_basique": r"2\text{IO}_3^- + 6\text{H}_2\text{O} + 10e^- \rightleftharpoons \text{I}_2 + 12\text{OH}^-",
        "h3o": 12, "oh": 12, "h2o_acide": 18, "h2o_basique": 6
    },

    # --- OXYGÈNE, HYDROGÈNE ET SOUFRE ---
    "O2 / H2O": {
        "no_ox": "0", "no_red": "-II", "electrons": 4,
        "milieu_acide": r"\text{O}_2 + 4\text{H}_3\text{O}^+ + 4e^- \rightleftharpoons 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{O}_2 + 2\text{H}_2\text{O} + 4e^- \rightleftharpoons 4\text{OH}^-",
        "h3o": 4, "oh": 4, "h2o_acide": 6, "h2o_basique": 2
    },
    "H2O2 / H2O (Eau oxygénée / Eau)": {
        "no_ox": "-I", "no_red": "-II", "electrons": 2,
        "milieu_acide": r"\text{H}_2\text{O}_2 + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons 4\text{H}_2\text{O}",
        "milieu_basique": r"\text{H}_2\text{O}_2 + 2e^- \rightleftharpoons 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 4, "h2o_basique": 0
    },
    "O2 / H2O2 (Dioxygène / Eau oxygénée)": {
        "no_ox": "0", "no_red": "-I", "electrons": 2,
        "milieu_acide": r"\text{O}_2 + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{H}_2\text{O}_2 + 2\text{H}_2\text{O}",
        "milieu_basique": r"\text{O}_2 + 2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{H}_2\text{O}_2 + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 2, "h2o_basique": 2
    },
    "H3O⁺ / H2": {
        "no_ox": "+I", "no_red": "0", "electrons": 2,
        "milieu_acide": r"2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{H}_2 + 2\text{H}_2\text{O}",
        "milieu_basique": r"2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{H}_2 + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 2, "h2o_basique": 2
    },
    "S4O6²⁻ / S2O3²⁻ (Tétrathionate / Thiosulfate)": {
        "no_ox": "+II.5", "no_red": "+II", "electrons": 2,
        "milieu_acide": r"\text{S}_4\text{O}_6^{2-} + 2e^- \rightleftharpoons 2\text{S}_2\text{O}_3^{2-}",
        "milieu_basique": r"\text{S}_4\text{O}_6^{2-} + 2e^- \rightleftharpoons 2\text{S}_2\text{O}_3^{2-}",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "SO4²⁻ / SO2 (Sulfate / Dioxyde de soufre)": {
        "no_ox": "+VI", "no_red": "+IV", "electrons": 2,
        "milieu_acide": r"\text{SO}_4^{2-} + 4\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{SO}_2 + 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{SO}_4^{2-} + 2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{SO}_2 + 4\text{OH}^-",
        "h3o": 4, "oh": 4, "h2o_acide": 6, "h2o_basique": 2
    },
    "SO2 / S (Dioxyde de soufre / Soufre)": {
        "no_ox": "+IV", "no_red": "0", "electrons": 4,
        "milieu_acide": r"\text{SO}_2 + 4\text{H}_3\text{O}^+ + 4e^- \rightleftharpoons \text{S} + 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{SO}_2 + 2\text{H}_2\text{O} + 4e^- \rightleftharpoons \text{S} + 4\text{OH}^-",
        "h3o": 4, "oh": 4, "h2o_acide": 6, "h2o_basique": 2
    },
    "S / H2S (Soufre / Hydrogène sulfuré)": {
        "no_ox": "0", "no_red": "-II", "electrons": 2,
        "milieu_acide": r"\text{S} + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{H}_2\text{S} + 2\text{H}_2\text{O}",
        "milieu_basique": r"\text{S} + 2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{H}_2\text{S} + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 2, "h2o_basique": 2
    },

    # --- AZOTE ET PHOSPHORE ---
    "NO3⁻ / NO (Nitrate / Monoxyde d'azote)": {
        "no_ox": "+V", "no_red": "+II", "electrons": 3,
        "milieu_acide": r"\text{NO}_3^- + 4\text{H}_3\text{O}^+ + 3e^- \rightleftharpoons \text{NO} + 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{NO}_3^- + 2\text{H}_2\text{O} + 3e^- \rightleftharpoons \text{NO} + 4\text{OH}^-",
        "h3o": 4, "oh": 4, "h2o_acide": 6, "h2o_basique": 2
    },
    "NO3⁻ / NO2 (Nitrate / Dioxyde d'azote)": {
        "no_ox": "+V", "no_red": "+IV", "electrons": 1,
        "milieu_acide": r"\text{NO}_3^- + 2\text{H}_3\text{O}^+ + 1e^- \rightleftharpoons \text{NO}_2 + 3\text{H}_2\text{O}",
        "milieu_basique": r"\text{NO}_3^- + \text{H}_2\text{O} + 1e^- \rightleftharpoons \text{NO}_2 + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 3, "h2o_basique": 1
    },
    "NO / N2O (Monoxyde d'azote / Protoxyde d'azote)": {
        "no_ox": "+II", "no_red": "+I", "electrons": 2,
        "milieu_acide": r"2\text{NO} + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{N}_2\text{O} + 3\text{H}_2\text{O}",
        "milieu_basique": r"2\text{NO} + \text{H}_2\text{O} + 2e^- \rightleftharpoons \text{N}_2\text{O} + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 3, "h2o_basique": 1
    },
    "N2 / NH4⁺ (Diazote / Ammonium)": {
        "no_ox": "0", "no_red": "-III", "electrons": 6,
        "milieu_acide": r"\text{N}_2 + 8\text{H}_3\text{O}^+ + 6e^- \rightleftharpoons 2\text{NH}_4^+ + 8\text{H}_2\text{O}",
        "milieu_basique": r"\text{N}_2 + 6\text{H}_2\text{O} + 6e^- \rightleftharpoons 2\text{NH}_3 + 6\text{OH}^-",
        "h3o": 8, "oh": 6, "h2o_acide": 8, "h2o_basique": 6
    },

    # --- MÉTAUX DE TRANSITION ACCENTUÉS ---
    "MnO4⁻ / Mn²⁺": {
        "no_ox": "+VII", "no_red": "+II", "electrons": 5,
        "milieu_acide": r"\text{MnO}_4^- + 8\text{H}_3\text{O}^+ + 5e^- \rightleftharpoons \text{Mn}^{2+} + 12\text{H}_2\text{O}",
        "milieu_basique": r"\text{MnO}_4^- + 4\text{H}_2\text{O} + 5e^- \rightleftharpoons \text{Mn(OH)}_4 + 4\text{OH}^-",
        "h3o": 8, "oh": 4, "h2o_acide": 12, "h2o_basique": 4
    },
    "MnO2 / Mn²⁺": {
        "no_ox": "+IV", "no_red": "+II", "electrons": 2,
        "milieu_acide": r"\text{MnO}_2 + 4\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{Mn}^{2+} + 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{MnO}_2 + 2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{Mn(OH)}_2 + 2\text{OH}^-",
        "h3o": 4, "oh": 2, "h2o_acide": 6, "h2o_basique": 2
    },
    "Cr2O7²⁻ / Cr³⁺": {
        "no_ox": "+VI", "no_red": "+III", "electrons": 6,
        "milieu_acide": r"\text{Cr}_2\text{O}_7^{2-} + 14\text{H}_3\text{O}^+ + 6e^- \rightleftharpoons 2\text{Cr}^{3+} + 21\text{H}_2\text{O}",
        "milieu_basique": r"\text{Cr}_2\text{O}_7^{2-} + 7\text{H}_2\text{O} + 6e^- \rightleftharpoons 2\text{Cr}^{3+} + 14\text{OH}^-",
        "h3o": 14, "oh": 14, "h2o_acide": 21, "h2o_basique": 7
    },
    "Fe³⁺ / Fe²⁺": {
        "no_ox": "+III", "no_red": "+II", "electrons": 1,
        "milieu_acide": r"\text{Fe}^{3+} + 1e^- \rightleftharpoons \text{Fe}^{2?}",
        "milieu_basique": r"\text{Fe(OH)}_3 + 1e^- \rightleftharpoons \text{Fe(OH)}_2 + \text{OH}^-",
        "h3o": 0, "oh": 1, "h2o_acide": 0, "h2o_basique": 0
    },
    "Fe²⁺ / Fe": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Fe}^{2+} + 2e^- \rightleftharpoons \text{Fe}",
        "milieu_basique": r"\text{Fe(OH)}_2 + 2e^- \rightleftharpoons \text{Fe} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Cu²⁺ / Cu⁺": {
        "no_ox": "+II", "no_red": "+I", "electrons": 1,
        "milieu_acide": r"\text{Cu}^{2+} + 1e^- \rightleftharpoons \text{Cu}^+",
        "milieu_basique": r"\text{Cu(OH)}_2 + 1e^- \rightleftharpoons \text{CuOH} + \text{OH}^-",
        "h3o": 0, "oh": 1, "h2o_acide": 0, "h2o_basique": 0
    },
    "Cu²⁺ / Cu": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Cu}^{2+} + 2e^- \rightleftharpoons \text{Cu}",
        "milieu_basique": r"\text{Cu(OH)}_2 + 2e^- \rightleftharpoons \text{Cu} + 2\text{OH}^-",

        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Ag⁺ / Ag": {
        "no_ox": "+I", "no_red": "0", "electrons": 1,
        "milieu_acide": r"\text{Ag}^+ + 1e^- \rightleftharpoons \text{Ag}",
        "milieu_basique": r"\text{Ag}_2\text{O} + \text{H}_2\text{O} + 2e^- \rightleftharpoons 2\text{Ag} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 1
    },
    "Zn²⁺ / Zn": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Zn}^{2+} + 2e^- \rightleftharpoons \text{Zn}",
        "milieu_basique": r"\text{Zn(OH)}_2 + 2e^- \rightleftharpoons \text{Zn} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Al³⁺ / Al": {
        "no_ox": "+III", "no_red": "0", "electrons": 3,
        "milieu_acide": r"\text{Al}^{3+} + 3e^- \rightleftharpoons \text{Al}",
        "milieu_basique": r"\text{Al(OH)}_3 + 3e^- \rightleftharpoons \text{Al} + 3\text{OH}^-",
        "h3o": 0, "oh": 3, "h2o_acide": 0, "h2o_basique": 0
    },
    "Ni²⁺ / Ni": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Ni}^{2+} + 2e^- \rightleftharpoons \text{Ni}",
        "milieu_basique": r"\text{Ni(OH)}_2 + 2e^- \rightleftharpoons \text{Ni} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Co²⁺ / Co": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Co}^{2+} + 2e^- \rightleftharpoons \text{Co}",
        "milieu_basique": r"\text{Co(OH)}_2 + 2e^- \rightleftharpoons \text{Co} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Co³⁺ / Co²⁺": {
        "no_ox": "+III", "no_red": "+II", "electrons": 1,
        "milieu_acide": r"\text{Co}^{3+} + 1e^- \rightleftharpoons \text{Co}^{2?}",
        "milieu_basique": r"\text{Co(OH)}_3 + 1e^- \rightleftharpoons \text{Co(OH)}_2 + \text{OH}^-",
        "h3o": 0, "oh": 1, "h2o_acide": 0, "h2o_basique": 0
    },
    "Pb²⁺ / Pb": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Pb}^{2+} + 2e^- \rightleftharpoons \text{Pb}",
        "milieu_basique": r"\text{Pb(OH)}_2 + 2e^- \rightleftharpoons \text{Pb} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "PbO2 / Pb²⁺": {
        "no_ox": "+IV", "no_red": "+II", "electrons": 2,
        "milieu_acide": r"\text{PbO}_2 + 4\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{Pb}^{2+} + 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{PbO}_2 + 2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{Pb(OH)}_2 + 2\text{OH}^-",
        "h3o": 4, "oh": 2, "h2o_acide": 6, "h2o_basique": 2
    },
    "Sn²⁺ / Sn": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Sn}^{2+} + 2e^- \rightleftharpoons \text{Sn}",
        "milieu_basique": r"\text{Sn(OH)}_2 + 2e^- \rightleftharpoons \text{Sn} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Sn⁴⁺ / Sn²⁺": {
        "no_ox": "+IV", "no_red": "+II", "electrons": 2,
        "milieu_acide": r"\text{Sn}^{4+} + 2e^- \rightleftharpoons \text{Sn}^{2?}",
        "milieu_basique": r"\text{Sn(OH)}_4 + 2e^- \rightleftharpoons \text{Sn(OH)}_2 + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Hg²⁺ / Hg": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Hg}^{2+} + 2e^- \rightleftharpoons \text{Hg}",
        "milieu_basique": r"\text{HgO} + \text{H}_2\text{O} + 2e^- \rightleftharpoons \text{Hg} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 1
    },
    "Au³⁺ / Au": {
        "no_ox": "+III", "no_red": "0", "electrons": 3,
        "milieu_acide": r"\text{Au}^{3+} + 3e^- \rightleftharpoons \text{Au}",
        "milieu_basique": r"\text{Au(OH)}_3 + 3e^- \rightleftharpoons \text{Au} + 3\text{OH}^-",
        "h3o": 0, "oh": 3, "h2o_acide": 0, "h2o_basique": 0
    },
    "Pt²⁺ / Pt": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Pt}^{2+} + 2e^- \rightleftharpoons \text{Pt}",
        "milieu_basique": r"\text{Pt(OH)}_2 + 2e^- \rightleftharpoons \text{Pt} + 2\text{OH}^-",
        "h3o": 0, "oh": 2, "h2o_acide": 0, "h2o_basique": 0
    },
    "Ti³⁺ / Ti²⁺": {
        "no_ox": "+III", "no_red": "+II", "electrons": 1,
        "milieu_acide": r"\text{Ti}^{3+} + 1e^- \rightleftharpoons \text{Ti}^{2?}",
        "milieu_basique": r"\text{Ti(OH)}_3 + 1e^- \rightleftharpoons \text{Ti(OH)}_2 + \text{OH}^-",
        "h3o": 0, "oh": 1, "h2o_acide": 0, "h2o_basique": 0
    },
    "V³⁺ / V²⁺": {
        "no_ox": "+III", "no_red": "+II", "electrons": 1,
        "milieu_acide": r"\text{V}^{3+} + 1e^- \rightleftharpoons \text{V}^{2?}",
        "milieu_basique": r"\text{V(OH)}_3 + 1e^- \rightleftharpoons \text{V(OH)}_2 + \text{OH}^-",
        "h3o": 0, "oh": 1, "h2o_acide": 0, "h2o_basique": 0
    },
        # --- COMPOSÉS ORGANIQUES ET DIVERS ---
    "CH3COOH / CH3CH2OH (Acide acétique / Éthanol)": {
        "no_ox": "0", "no_red": "-II", "electrons": 4,
        "milieu_acide": r"\text{CH}_3\text{COOH} + 4\text{H}_3\text{O}^+ + 4e^- \rightleftharpoons \text{CH}_3\text{CH}_2\text{OH} + 6\text{H}_2\text{O}",
        "milieu_basique": r"\text{CH}_3\text{COO}^- + 3\text{H}_2\text{O} + 4e^- \rightleftharpoons \text{CH}_3\text{CH}_2\text{OH} + 5\text{OH}^-",
        "h3o": 4, "oh": 5, "h2o_acide": 6, "h2o_basique": 3
    },
    "CO2 / H2C2O4 (Dioxyde de carbone / Acide oxalique)": {
        "no_ox": "+IV", "no_red": "+III", "electrons": 2,
        "milieu_acide": r"2\text{CO}_2 + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{H}_2\text{C}_2\text{O}_4 + 2\text{H}_2\text{O}",
        "milieu_basique": r"2\text{CO}_3^{2-} + 4\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{C}_2\text{O}_4^{2-} + 4\text{OH}^-",
        "h3o": 2, "oh": 4, "h2o_acide": 2, "h2o_basique": 4
    },
    "CO2 / CH4 (Dioxyde de carbone / Méthane)": {
        "no_ox": "+IV", "no_red": "-IV", "electrons": 8,
        "milieu_acide": r"\text{CO}_2 + 8\text{H}_3\text{O}^+ + 8e^- \rightleftharpoons \text{CH}_4 + 12\text{H}_2\text{O}",
        "milieu_basique": r"\text{CO}_2 + 6\text{H}_2\text{O} + 8e^- \rightleftharpoons \text{CH}_4 + 8\text{OH}^-",
        "h3o": 8, "oh": 8, "h2o_acide": 12, "h2o_basique": 6
    },
    "CH2O / CH3OH (Formaldéhyde / Méthanol)": {
        "no_ox": "0", "no_red": "-II", "electrons": 2,
        "milieu_acide": r"\text{CH}_2\text{O} + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{CH}_3\text{OH} + 2\text{H}_2\text{O}",
        "milieu_basique": r"\text{CH}_2\text{O} + 2\text{H}_2\text{O} + 2e^- \rightleftharpoons \text{CH}_3\text{OH} + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 2, "h2o_basique": 2
    },
    "O3 / O2 (Ozone / Dioxygène)": {
        "no_ox": "0", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{O}_3 + 2\text{H}_3\text{O}^+ + 2e^- \rightleftharpoons \text{O}_2 + 3\text{H}_2\text{O}",
        "milique_basique": r"\text{O}_3 + \text{H}_2\text{O} + 2e^- \rightleftharpoons \text{O}_2 + 2\text{OH}^-",
        "h3o": 2, "oh": 2, "h2o_acide": 3, "h2o_basique": 1
    },
    "Fe(CN)6³⁻ / Fe(CN)6⁴⁻": {
        "no_ox": "+III", "no_red": "+II", "electrons": 1,
        "milieu_acide": r"\text{Fe(CN)}_6^{3-} + 1e^- \rightleftharpoons \text{Fe(CN)}_6^{4-}",
        "milieu_basique": r"\text{Fe(CN)}_6^{3-} + 1e^- \rightleftharpoons \text{Fe(CN)}_6^{4-}",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    # --- MÉTAUX ALCALINS ET ALCALINO-TERREUX ---
    "Na⁺ / Na": {
        "no_ox": "+I", "no_red": "0", "electrons": 1,
        "milieu_acide": r"\text{Na}^+ + 1e^- \rightleftharpoons \text{Na}",
        "milieu_basique": r"\text{Na}^+ + 1e^- \rightleftharpoons \text{Na}",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "K⁺ / K": {
        "no_ox": "+I", "no_red": "0", "electrons": 1,
        "milieu_acide": r"\text{K}^+ + 1e^- \rightleftharpoons \text{K}",
        "milieu_basique": r"\text{K}^+ + 1e^- \rightleftharpoons \text{K}",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "Ca²⁺ / Ca": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Ca}^{2+} + 2e^- \rightleftharpoons \text{Ca}",
        "milieu_basique": r"\text{Ca}^{2+} + 2e^- \rightleftharpoons \text{Ca}",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    },
    "Mg²⁺ / Mg": {
        "no_ox": "+II", "no_red": "0", "electrons": 2,
        "milieu_acide": r"\text{Mg}^{2+} + 2e^- \rightleftharpoons \text{Mg}",
        "milieu_basique": r"\text{Mg}^{2+} + 2e^- \rightleftharpoons \text{Mg}",
        "h3o": 0, "oh": 0, "h2o_acide": 0, "h2o_basique": 0
    }
        }


def afficher_atelier_bilan_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Réaction d'oxydoréduction) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ
    questions_bilan6_sources = [
        {
            "id": "bil1",
            "q": "Les électrons libres peuvent-ils apparaître dans l'équation bilan finale d'oxydoréduction ?",
            "options": [
                "Non, ils doivent obligatoirement s'annuler",
                "Oui, toujours du côté des produits",
                "Oui, toujours du côté des réactifs",
            ],
            "rep": "Non, ils doivent obligatoirement s'annuler",
        },
        {
            "id": "bil2",
            "q": "Que doit-on faire si les deux demi-équations ne mettent pas en jeu le même nombre d'électrons ?",
            "options": [
                "Multiplier les lignes par des coefficients multiplicateurs",
                "Ajouter des protons pour compenser",
                "Ignorer les électrons restants",
            ],
            "rep": "Multiplier les lignes par des coefficients multiplicateurs",
        },
        {
            "id": "bil3",
            "q": "Une réaction d'oxydoréduction globale met toujours en relation :",
            "options": [
                "L'oxydant d'un couple et le réducteur d'un autre couple",
                "Deux oxydants ensemble",
                "Deux réducteurs ensemble",
            ],
            "rep": "L'oxydant d'un couple et le réducteur d'un autre couple",
        },
        {
            "id": "bil4",
            "q": "Dans l'action combinée, quelle entité chimique fournit le flux d'électrons ?",
            "options": ["Le réducteur", "L'oxydant", "L'eau distillée"],
            "rep": "Le réducteur",
        },
        {
            "id": "bil5",
            "q": "La règle stricte qui impose l'égalité des électrons échangés découle de la loi de :",
            "options": [
                "Conservation de la charge électrique",
                "Dilution des solutions",
                "L'attraction universelle",
            ],
            "rep": "Conservation de la charge électrique",
        },
    ]

    if "ordre_quiz_tab6_bil_aleatoire" not in st.session_state:
        random.shuffle(questions_bilan6_sources)
        st.session_state.ordre_quiz_tab6_bil_aleatoire = (
            questions_bilan6_sources
        )

    # 2. BASE DE DONNÉES DU TEXTE À TROUS
    if "champs_bil6_clean" not in st.session_state:
        st.session_state.champs_bil6_clean = [
            (
                "1. La réaction bilan résulte de l'association d'une oxydation et d'une ..........",
                ["Choisir...", "réduction", "hydrolyse"],
                "réduction",
                "bil6_t1",
            ),
            (
                "2. Le nombre d'électrons perdus par le réducteur doit être .......... à celui gagné.",
                ["Choisir...", "égal", "supérieur"],
                "égal",
                "bil6_t2",
            ),
            (
                "3. Les coefficients multiplicateurs servent à équilibrer les .......... transférés.",
                ["Choisir...", "électrons", "atomes"],
                "électrons",
                "bil6_t3",
            ),
            (
                "4. Dans le bilan global final écrit au propre, les électrons sont ..........",
                ["Choisir...", "éliminés", "doublés"],
                "éliminés",
                "bil6_t4",
            ),
            (
                "5. Ce transfert direct de charge valide la loi de conservation de la ..........",
                ["Choisir...", "charge", "vitesse"],
                "charge",
                "bil6_t5",
            ),
        ]

    # 3. RENDU DES COLONNES
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown(
            "##### Quiz Technique Équation Bilan (5 questions - 10 pts)"
        )
        for idx, q_data in enumerate(
            st.session_state.ordre_quiz_tab6_bil_aleatoire, 1
        ):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"bil_at6_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse de l'Atelier 6 (Texte à trous - 5 cases - 10 pts)"
        )
        
        # Vérification stricte que la liste existe dans le session_state
        if "champs_bil6_clean" in st.session_state:
            for ligne in st.session_state.champs_bil6_clean:
                # Extraction sécurisée par index pour éviter tout problème de déballage (unpacking)
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1] # Récupère le dernier élément (la clé)
                
                # Création des deux colonnes avec alignement vertical centré
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="center")
                
                with c_txt:
                    st.write(enonce)
                    
                with c_sel:
                    st.selectbox(
                        label=enonce,
                        options=choix,
                        key=f"{cle}_bil6_clean",
                        disabled=verrouille,
                        label_visibility="collapsed"
                    )


def afficher_atelier_gamma_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (La règle du gamma) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ
    questions_gamma5_sources = [
        {
            "id": "gam1",
            "q": "Quelle unité physique utilise-t-on pour exprimer le potentiel standard d'un couple redox ?",
            "options": ["Le Volt", "L'Ampère", "Le Joule"],
            "rep": "Le Volt",
        },
        {
            "id": "gam2",
            "q": "Où se situe l'oxydant le plus fort sur l'échelle verticale des potentiels standards ?",
            "options": [
                "Tout en haut à gauche",
                "Tout en bas à droite",
                "Au milieu exact de l'axe",
            ],
            "rep": "Tout en haut à gauche",
        },
        {
            "id": "gam3",
            "q": "La réaction spontanée se produit entre :",
            "options": [
                "L'oxydant le plus fort et le réducteur le plus fort",
                "L'oxydant le plus faible et le réducteur le plus faible",
                "Deux réducteurs face à face",
            ],
            "rep": "L'oxydant le plus fort et le réducteur le plus fort",
        },
        {
            "id": "gam4",
            "q": "Quelle lettre de l'alphabet grec a donné son nom à cette règle de lecture graphique ?",
            "options": ["Gamma (γ)", "Alpha (α)", "Delta (δ)"],
            "rep": "Gamma (γ)",
        },
        {
            "id": "gam5",
            "q": "Si le tracé sur l'échelle forme un Gamma inversé, la réaction est :",
            "options": [
                "Impossible spontanément",
                "Immédiate et explosive",
                "Parfaitement équilibrée",
            ],
            "rep": "Impossible spontanément",
        },
    ]

    if "ordre_quiz_tab5_gam_aleatoire" not in st.session_state:
        random.shuffle(questions_gamma5_sources)
        st.session_state.ordre_quiz_tab5_gam_aleatoire = (
            questions_gamma5_sources
        )

    # 2. BASE DE DONNÉES DU TEXTE À TROUS
    if "champs_gam5_clean" not in st.session_state:
        st.session_state.champs_gam5_clean = [
            (
                "1. L'échelle de classification s'appuie sur la mesure du potentiel ..........",
                ["Choisir...", "standard", "cinétique"],
                "standard",
                "gam5_t1",
            ),
            (
                "2. Plus le potentiel E0 est grand, plus le pouvoir .......... du corps augmente.",
                ["Choisir...", "oxydant", "réducteur"],
                "oxydant",
                "gam5_t2",
            ),
            (
                "3. À l'inverse, le réducteur le plus fort se trouve tout en .......... de l'axe.",
                ["Choisir...", "bas", "haut"],
                "bas",
                "gam5_t3",
            ),
            (
                "4. Lier graphiquement les réactifs valides dessine un .......... à l'endroit.",
                ["Choisir...", "gamma", "oméga"],
                "gamma",
                "gam5_t4",
            ),
            (
                "5. Cette méthode géométrique sert à valider la .......... d'une transformation.",
                ["Choisir...", "spontanéité", "vitesse"],
                "spontanéité",
                "gam5_t5",
            ),
        ]

    # 3. RENDU DES COLONNES
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique Règle du Gamma (5 questions - 10 pts)")
        for idx, q_data in enumerate(
            st.session_state.ordre_quiz_tab5_gam_aleatoire, 1
        ):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"gam_at5_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )
    with col_trous:
        st.markdown(
            "##### Synthèse de l'Atelier 5 (Texte à trous - 5 cases - 10 pts)"
        )
        
        # Parcours de la liste des champs de l'Atelier 5
        for ligne in st.session_state.champs_gam5_clean:
            # Extraction sécurisée par index pour éviter l'erreur de déballage
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            # Alignement en deux colonnes proportionnelles
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            
            with c_txt:
                st.write(enonce)
                
            with c_sel:
                st.selectbox(
                    label=enonce,
                    options=choix,
                    key=f"{cle}_gam5_clean",
                    disabled=verrouille,
                    label_visibility="collapsed"
                )


def afficher_atelier_couples_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Les couples redox) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ DES COUPLES
    questions_couples4_sources = [
        {
            "id": "cpl1",
            "q": "Quelle est la convention d'écriture internationale pour désigner un couple redox ?",
            "options": [
                "Oxydant / Réducteur",
                "Réducteur / Oxydant",
                "Acide / Base",
            ],
            "rep": "Oxydant / Réducteur",
        },
        {
            "id": "cpl2",
            "q": "Quel symbole mathématique utilise-t-on dans la demi-équation d'un couple pour signifier sa réversibilité ?",
            "options": [
                "Une double flèche (réversible)",
                "Une flèche simple vers la droite",
                "Un signe égal",
            ],
            "rep": "Une double flèche (réversible)",
        },
        {
            "id": "cpl3",
            "q": "Comment qualifie-t-on l'oxydant et le réducteur qui composent un même couple ?",
            "options": ["Conjugués", "Isomères", "Neutres"],
            "rep": "Conjugués",
        },
        {
            "id": "cpl4",
            "q": "Dans le couple Cu²⁺ / Cu, quelle est la nature physique de la forme réductrice ?",
            "options": [
                "Un solide métallique orange",
                "Un liquide bleu soluble",
                "Un gaz incolore",
            ],
            "rep": "Un solide métallique orange",
        },
        {
            "id": "cpl5",
            "q": "Quelle particule fait le lien exclusif entre les deux formes d'un couple redox ?",
            "options": ["L'électron", "Le proton", "Le neutron"],
            "rep": "L'électron",
        },
    ]

    if "ordre_quiz_tab4_cpl_aleatoire" not in st.session_state:
        random.shuffle(questions_couples4_sources)
        st.session_state.ordre_quiz_tab4_cpl_aleatoire = (
            questions_couples4_sources
        )

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DES COUPLES
    if "champs_cpl4_clean" not in st.session_state:
        st.session_state.champs_cpl4_clean = [
            (
                "1. Un couple chimique associe toujours l'oxydant et son .......... conjugué.",
                ["Choisir...", "réducteur", "solvant"],
                "réducteur",
                "cpl4_t1",
            ),
            (
                "2. Par convention, l'un s'écrit à gauche du slash et représente l'..........",
                ["Choisir...", "oxydant", "réducteur"],
                "oxydant",
                "cpl4_t2",
            ),
            (
                "3. La double flèche prouve le caractère .......... de l'échange électronique.",
                ["Choisir...", "réversible", "irréversible"],
                "réversible",
                "cpl4_t3",
            ),
            (
                "4. Dans le couple Fe²⁺ / Fe, l'entité Fe²⁺ est la forme ..........",
                ["Choisir...", "oxydée", "réduite"],
                "oxydée",
                "cpl4_t4",
            ),
            (
                "5. L'atome neutre de métal pur constitue toujours le .......... du couple.",
                ["Choisir...", "réducteur", "catalyseur"],
                "réducteur",
                "cpl4_t5",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique sur les Couples (5 questions - 10 pts)")
        for idx, q_data in enumerate(
            st.session_state.ordre_quiz_tab4_cpl_aleatoire, 1
        ):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"cpl_at4_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse de l'Atelier 4 (Texte à trous - 5 cases - 10 pts)"
        )
        for ligne in st.session_state.champs_cpl4_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns(
                [0.65, 0.35], vertical_alignment="bottom"
            )
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_cpl4_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )


def afficher_atelier_reduction_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Réaction de réduction) sur deux colonnes."""
    import random

    questions_reduction3_sources = [
        {
            "id": "red1",
            "q": "Quelle est la définition électronique exacte d'une réduction ?",
            "options": [
                "Un gain d'électrons",
                "Une perte d'électrons",
                "Un transfert de neutrons",
            ],
            "rep": "Un gain d'électrons",
        },
        {
            "id": "red2",
            "q": "Comment qualifie-t-on l'espèce de départ qui capture et accepte les électrons ?",
            "options": ["L'oxydant", "Le réducteur", "L'anion"],
            "rep": "L'oxydant",
        },
        {
            "id": "red3",
            "q": "Dans l'écriture standard d'une réduction, où se trouvent les électrons captés ?",
            "options": [
                "Du côté des réactifs (à gauche)",
                "Du côté des produits (à droite)",
                "Ils sont invisibles",
            ],
            "rep": "Du côté des réactifs (à gauche)",
        },
        {
            "id": "red4",
            "q": "Lors de la réduction des ions bleus Cu²⁺, quel solide métallique brillant obtient-on ?",
            "options": ["Le cuivre métallique", "Le zinc métallique", "Le fer blanc"],
            "rep": "Le cuivre métallique",
        },
        {
            "id": "red5",
            "q": "Que subit le nombre d'oxydation (n.o.) d'un atome lors d'une réduction ?",
            "options": [
                "Il diminue",
                "Il augmente",
                "Il double d'intensité",
            ],
            "rep": "Il diminue",
        },
    ]

    if "ordre_quiz_tab3_red_aleatoire" not in st.session_state:
        random.shuffle(questions_reduction3_sources)
        st.session_state.ordre_quiz_tab3_red_aleatoire = (
            questions_reduction3_sources
        )

    if "champs_red3_clean" not in st.session_state:
        st.session_state.champs_red_clean = [
            (
                "1. La réduction se définit toujours comme un .......... d'électrons.",
                ["Choisir...", "gain", "rejet"],
                "gain",
                "red3_t1",
            ),
            (
                "2. L'entité chimique qui capture ces charges négatives est l'..........",
                ["Choisir...", "oxydant", "réducteur"],
                "oxydant",
                "red3_t2",
            ),
            (
                "3. Les électrons absorbés figurent à gauche, du côté des ..........",
                ["Choisir...", "réactifs", "produits"],
                "réactifs",
                "red3_t3",
            ),
            (
                "4. En milieu acide, la réduction des ions H₃O⁺ libère le gaz ..........",
                ["Choisir...", "dihydrogène", "dioxygène"],
                "dihydrogène",
                "red3_t4",
            ),
            (
                "5. Un oxydant ayant capté ses électrons devient son réducteur ..........",
                ["Choisir...", "conjugué", "inverse"],
                "conjugué",
                "red3_t5",
            ),
        ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown(
            "##### Quiz Technique de la Réduction (5 questions - 10 pts)"
        )
        for idx, q_data in enumerate(
            st.session_state.ordre_quiz_tab3_red_aleatoire, 1
        ):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"red_at3_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse de l'Atelier 3 (Texte à trous - 5 cases - 10 pts)"
        )
        for ligne in st.session_state.champs_red_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns(
                [0.65, 0.35], vertical_alignment="bottom"
            )
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_red3_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )

def afficher_atelier_oxydation_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Réaction d'oxydation) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ DE L'OXYDATION
    questions_oxydation2_sources = [
        {
            "id": "ox1",
            "q": "Quelle est la définition électronique exacte d'une réaction d'oxydation ?",
            "options": [
                "Une perte d'électrons",
                "Un gain d'électrons",
                "Un gain de protons",
            ],
            "rep": "Une perte d'électrons",
        },
        {
            "id": "ox2",
            "q": "Comment appelle-t-on l'espèce chimique capable de fournir ou céder des électrons au cours de la réaction ?",
            "options": ["Le réducteur", "L'oxydant", "Le solvant"],
            "rep": "Le réducteur",
        },
        {
            "id": "ox3",
            "q": "Dans l'écriture universelle d'une demi-équation d'oxydation, de quel côté se situent les électrons libérés ?",
            "options": [
                "Du côté des produits (à droite)",
                "Du côté des réactifs (à gauche)",
                "Ils ne s'écrivent pas",
            ],
            "rep": "Du côté des produits (à droite)",
        },
        {
            "id": "ox4",
            "q": "Lors de l'oxydation du fer métallique neutre (Fe), en quel ion se transforme-t-on le plus couramment ?",
            "options": ["L'ion fer II (Fe²⁺)", "L'ion chlorure (Cl⁻)", "L'ion cuivre II (Cu²⁺)"],
            "rep": "L'ion fer II (Fe²⁺)",
        },
        {
            "id": "ox5",
            "q": "Combien d'électrons un atome de zinc (Zn) libère-t-il lorsqu'il subit une oxydation totale en ion Zn²⁺ ?",
            "options": ["2 électrons", "1 électron", "3 électrons"],
            "rep": "2 électrons",
        },
        {
            "id": "ox6",
            "q": "Quelle modification subit le degré ou nombre d'oxydation (n.o.) d'un élément lors d'une oxydation ?",
            "options": [
                "Il augmente",
                "Il diminue",
                "Il reste strictement identique",
            ],
            "rep": "Il augmente",
        },
        {
            "id": "ox7",
            "q": "Dans le phénomène de la rouille, quel métal subit l'oxydation destructive en premier lieu ?",
            "options": ["Le fer", "Le plastique", "L'or"],
            "rep": "Le fer",
        },
        {
            "id": "ox8",
            "q": "Quel qualificatif donne-t-on à un métal comme le zinc qui s'oxyde exprès pour sauver l'acier sous-jacent ?",
            "options": ["Sacrificiel", "Noble", "Passif"],
            "rep": "Sacrificiel",
        },
        {
            "id": "ox9",
            "q": "Une espèce chimique qui subit une oxydation devient instantanément :",
            "options": [
                "Son oxydant conjugué",
                "Son réducteur conjugué",
                "Une molécule neutre",
            ],
            "rep": "Son oxydant conjugué",
        },
        {
            "id": "ox10",
            "q": "Dans la nature, quel élément gazeux de l'air est le déclencheur le plus fréquent de l'oxydation des métaux ?",
            "options": ["Le dioxygène", "Le diazote", "L'hélium"],
            "rep": "Le dioxygène",
        },
    ]

    if "ordre_quiz_tab2_ox_aleatoire" not in st.session_state:
        random.shuffle(questions_oxydation2_sources)
        st.session_state.ordre_quiz_tab2_ox_aleatoire = (
            questions_oxydation2_sources
        )

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DE L'OXYDATION
    if "champs_ox2_clean" not in st.session_state:
        st.session_state.champs_ox2_clean = [
            (
                "1. Une oxydation se caractérise fondamentalement par une .......... d'électrons.",
                ["Choisir...", "perte", "captation"],
                "perte",
                "ox2_t1",
            ),
            (
                "2. L'espèce de départ qui fournit et cède ses électrons s'appelle le ..........",
                ["Choisir...", "réducteur", "oxydant"],
                "réducteur",
                "ox2_t2",
            ),
            (
                "3. Lors d'une oxydation, les électrons libérés figurent du côté des ..........",
                ["Choisir...", "produits", "réactifs"],
                "produits",
                "ox2_t3",
            ),
            (
                "4. Un atome métallique neutre perd ses charges et se transforme en ..........",
                ["Choisir...", "cation", "anion"],
                "cation",
                "ox2_t4",
            ),
            (
                "5. L'oxydation du fer engendre des ions fer II qui créent la ..........",
                ["Choisir...", "rouille", "peinture"],
                "rouille",
                "ox2_t5",
            ),
            (
                "6. Le zinc métallique s'oxyde pour jouer un rôle de protection ..........",
                ["Choisir...", "sacrificielle", "mécanique"],
                "sacrificielle",
                "ox2_t6",
            ),
            (
                "7. Au cours de l'oxydation, le nombre d'oxydation de l'élément ..........",
                ["Choisir...", "augmente", "chute"],
                "augmente",
                "ox2_t7",
            ),
            (
                "8. Un réducteur ayant perdu ses charges est converti en son .......... conjugué.",
                ["Choisir...", "oxydant", "acide"],
                "oxydant",
                "ox2_t8",
            ),
            (
                "9. L'attaque corrosive des structures en acier est provoquée par l'..........",
                ["Choisir...", "oxydation", "réduction"],
                "oxydation",
                "ox2_t9",
            ),
            (
                "10. Dans la demi-équation, la flèche pointe vers les électrons ..........",
                ["Choisir...", "produits", "absorbés"],
                "produits",
                "ox2_t10",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown(
            "##### Quiz Technique de l'Oxydation (10 questions - 10 pts)"
        )
        for idx, q_data in enumerate(
            st.session_state.ordre_quiz_tab2_ox_aleatoire, 1
        ):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"ox_at2_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)"
        )
        for ligne in st.session_state.champs_ox2_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns(
                [0.65, 0.35], vertical_alignment="bottom"
            )
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_ox2_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )


def afficher_atelier_histoire_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Historique) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ HISTORIQUE REDOX
    questions_redox1_sources = [
        {
            "id": "qr1",
            "q": "Quel célèbre chimiste français du 18e siècle a lié pour la première fois l'oxydation à la fixation de l'oxygène ?",
            "options": [
                "Antoine Lavoisier",
                "Louis Pasteur",
                "Dmitri Mendeleïev",
            ],
            "rep": "Antoine Lavoisier",
        },
        {
            "id": "qr2",
            "q": "À la fin du 18e siècle, quel nom donnait-on au produit de la fixation de l'oxygène sur un métal comme le fer ?",
            "options": ["Un oxyde", "Un sulfure", "Un hydrocarbure"],
            "rep": "Un oxyde",
        },
        {
            "id": "qr3",
            "q": "Que signifie historiquement le mot Réduction appliqué à un oxyde métallique ?",
            "options": [
                "Une diminution de la masse de matière",
                "Une baisse de la température",
                "Une réduction du volume de gaz",
            ],
            "rep": "Une diminution de la masse de matière",
        },
        {
            "id": "qr4",
            "q": "Quelle particule élémentaire, découverte à la fin du 19e siècle, a permis de redéfinir entièrement l'oxydoréduction ?",
            "options": ["L'électron", "Le proton", "Le neutron"],
            "rep": "L'électron",
        },
        {
            "id": "qr5",
            "q": "Quel physicien britannique a découvert l'électron en 1897, ouvrant la voie au modèle électronique ?",
            "options": ["J.J. Thomson", "Isaac Newton", "James Watt"],
            "rep": "J.J. Thomson",
        },
        {
            "id": "qr6",
            "q": "Quel scientifique a proposé la théorie des liaisons chimiques par partage d'électrons au début du 20e siècle ?",
            "options": ["Gilbert Lewis", "Walther Nernst", "Michael Faraday"],
            "rep": "Gilbert Lewis",
        },
        {
            "id": "qr7",
            "q": "En quelle année Alessandro Volta a-t-il inventé la première pile électrique associant le cuivre et le zinc ?",
            "options": ["1800", "1750", "1850"],
            "rep": "1800",
        },
        {
            "id": "qr8",
            "q": "Quel savant a formalisé en 1834 les lois de l'électrolyse reliant la chimie à la quantité d'électricité ?",
            "options": ["Michael Faraday", "Antoine Lavoisier", "J.J. Thomson"],
            "rep": "Michael Faraday",
        },
        {
            "id": "qr9",
            "q": "Selon la définition moderne, que subit une entité chimique lors d'une oxydation ?",
            "options": [
                "Une perte d'électrons",
                "Un gain d'électrons",
                "Une perte de protons",
            ],
            "rep": "Une perte d'électrons",
        },
        {
            "id": "qr10",
            "q": "Quelle grandeur physique (exprimée en Volts) permet aujourd'hui de classer le pouvoir des couples redox ?",
            "options": [
                "Le potentiel standard d'oxydoréduction",
                "La conductivité thermique",
                "La résistance ohmique",
            ],
            "rep": "Le potentiel standard d'oxydoréduction",
        },
    ]

    # Initialisation de l'ordre aléatoire des questions dans la session Streamlit
    if "ordre_quiz_tab1_redox_aleatoire" not in st.session_state:
        random.shuffle(questions_redox1_sources)
        st.session_state.ordre_quiz_tab1_redox_aleatoire = (
            questions_redox1_sources
        )

    # 2. BASE DE DONNÉES DU TEXTE À TROUS HISTORIQUE REDOX
    if "champs_redox1_clean" not in st.session_state:
        st.session_state.champs_redox1_clean = [
            (
                "1. Au 18e siècle, Lavoisier associe l'oxydation à la fixation de l'..........",
                ["Choisir...", "oxygène", "hydrogène"],
                "oxygène",
                "redox1_t1",
            ),
            (
                "2. La transformation inverse qui extrait le métal pur s'appelle la ..........",
                ["Choisir...", "réduction", "combustion"],
                "réduction",
                "redox1_t2",
            ),
            (
                "3. La découverte scientifique majeure de 1897 concerne l'..........",
                ["Choisir...", "électron", "neutron"],
                "électron",
                "redox1_t3",
            ),
            (
                "4. Le modèle moderne définit la réaction redox par un .......... de charge.",
                ["Choisir...", "transfert", "blocage"],
                "transfert",
                "redox1_t4",
            ),
            (
                "5. L'invention de la première pile au cuivre et zinc en 1800 revient à ..........",
                ["Choisir...", "Volta", "Faraday"],
                "Volta",
                "redox1_t5",
            ),
            (
                "6. Une entité chimique qui perd un ou plusieurs électrons subit une ..........",
                ["Choisir...", "oxydation", "nitration"],
                "oxydation",
                "redox1_t6",
            ),
            (
                "7. L'étude quantitative des réactions liées au courant est l'..........",
                ["Choisir...", "électrochimie", "thermodynamique"],
                "électrochimie",
                "redox1_t7",
            ),
            (
                "8. Gilbert Lewis a mis en évidence le partage des électrons de ..........",
                ["Choisir...", "valence", "noyau"],
                "valence",
                "redox1_t8",
            ),
            (
                "9. La tendance d'un oxydant à capter des électrons se mesure en ..........",
                ["Choisir...", "Volts", "Ampères"],
                "Volts",
                "redox1_t9",
            ),
            (
                "10. La protection des métaux contre la rouille évite leur ..........",
                ["Choisir...", "corrosion", "fusion"],
                "corrosion",
                "redox1_t10",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown(
            "##### Quiz Technique et Historique (10 questions - 10 pts)"
        )
        for idx, q_data in enumerate(
            st.session_state.ordre_quiz_tab1_redox_aleatoire, 1
        ):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"redox_at1_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)"
        )
        for ligne in st.session_state.champs_redox1_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns(
                [0.65, 0.35], vertical_alignment="bottom"
            )
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_redox1_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )

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
    st.header("Historique de la Chimie Redox")
    
    st.subheader("Pourquoi ce nom ?")
    st.write(
        "Le mot **Oxydation** vient historiquement de l'**Oxygène**. "
        "À la fin du 18e siècle, le chimiste Antoine Lavoisier étudie la combustion des corps dans l'air. "
        "Il constate que la fixation d'oxygène sur un métal (comme le fer) produit de la rouille, appelée alors un oxyde. "
        "À l'inverse, extraire l'oxygène d'un oxyde pour récupérer le métal pur a été nommé la **Réduction** (diminution de la masse de la matière)."
    )


    st.subheader("Comment la définition a-t-elle évolué ?")
    st.write(
        "Au fil des siècles, les chimistes ont observé des réactions totalement identiques "
        "à la corrosion ou à la combustion, mais qui ne faisaient intervenir **aucun atome d'oxygène**."
    )

    st.info(
        "Le grand virage scientifique a eu lieu au début du 20e siècle avec la découverte de l'électron "
        "par J.J. Thomson (1897) et la théorie de la liaison chimique de Gilbert Lewis. "
        "Les scientifiques ont compris que l'oxygène n'était qu'un intermédiaire. Le véritable moteur caché de la réaction, "
        "c'est l'**échange d'électrons**."
    )

    st.subheader("Les travaux historiques marquants")

    # --- SECTION LAVOISIER ---
    st.markdown(
        "- **1777 - Antoine Lavoisier :** Théorie de la combustion. Définition de l'oxydation par fixation de l'oxygène."
    )
    col_11, col_12 = st.columns(2)
    with col_11:
        if os.path.exists("Lavoisier.jpg"):
            st.image("Lavoisier.jpg", caption="Antoine Lavoisier")
        else:
            st.warning("L'image 'Lavoisier.jpg' est introuvable.")
    with col_12:
        if os.path.exists("lavoisier _composition_de_air.jpg"):
            st.image("lavoisier _composition_de_air.jpg", caption="En chauffant du mercure (seul métal à l’état liquide à température ordinaire, et à relativement faible température d’ébullition à 350 °C), Lavoisier voit apparaître des flocules rouges d’oxyde de mercure. L’oxygène de l’air de la cornue a réagi avec le mercure pour former l’oxyde : il ne reste plus dans l’air de la cornue que l’azote. Lavoisier remarque que cette substance n’est pas respirable : un animal ne peut y vivre (azote = a- zoos-, privatif de vie). Dans un second temps, Lavoisier fait chauffer les flocules rouges : c’est la réaction inverse, avec dégagement d’un gaz « éminemment respirable » (l’oxygène), qui ravive la flamme d’une bougie quasi éteinte")
        else:
            st.warning("L'image 'Lavoisier.jpg' est introuvable.")

    # --- SECTION VOLTA ---

    st.markdown(
        "- **1800 - Alessandro Volta :** Invention de la première pile électrique (Cuivre / Zinc). Début de l'électrochimie."
    )
    col_13, col_14 = st.columns(2)
    with col_13:
        if os.path.exists("Volta.jpg"):
            st.image("Volta.jpg", caption="Alessandro Volta")
        else:
            st.warning("L'image 'Volta.jpg' est introuvable.")
    with col_14:
        if os.path.exists("pile_volta.jpg"):
            st.image("pile_volta.jpg", caption="pile volta")
        else:
            st.warning("L'image 'Volta.jpg' est introuvable.")
            
    st.markdown(
        "- **1834 - Michael Faraday :** Établissement des lois de l'électrolyse, reliant la chimie à la quantité d'électricité.")
    # --- SECTION FARADAY ---
    col_15, col_16 = st.columns(2)
    with col_15:
        if os.path.exists("Faraday.jpg"):
            st.image("Faraday.jpg", caption="Michael Faraday")
        else:
            st.warning("L'image 'Faraday.jpg' est introuvable.")
    with col_16:
        if os.path.exists("electrolyse.jpg"):
            st.image("electrolyse.jpg", caption="Michael Faraday")
        else:
            st.warning("L'image 'Faraday.jpg' est introuvable.")

    st.markdown(
        "- **1920s - Extension moderne :** Définition définitive et universelle de l'oxydoréduction par transfert d'électrons."
    )

    st.divider()
    st.subheader("Pourquoi cette étude dans vos filières ?")
    st.write(
        "Que ce soit pour lutter contre la corrosion des châssis (Transport), protéger les structures métalliques (Maintenance), "
        "comprendre la dégradation du béton armé (Travaux Publics) ou préserver les repères topographiques extérieurs (Géomètres), "
        "toutes ces problématiques découlent directement des découvertes de ces scientifiques."
    )

    # --- APPLICATIONS MÉTIERS (4 COLONNES) ---
    col_17, col_18, col_19, col_20 = st.columns(4)
    with col_17:
        if os.path.exists("rouille_tp.jpg"):
            st.image("rouille_tp.jpg", caption="dégradation du béton armé")
        else:
            st.warning("L'image 'rouille_tp.jpg' est introuvable.")

    with col_18:
        if os.path.exists("rouille_routier.jpg"):
            st.image("rouille_routier.jpg", caption="corrosion des châssis")
        else:
            st.warning("L'image 'rouille_routier.jpg' est introuvable.")

    with col_19:
        if os.path.exists("rouille_mm.jpg"):
            st.image("rouille_mm.jpg", caption="dégradation structure")
        else:
            st.warning("L'image 'rouille_mm.jpg' est introuvable.")

    with col_20:
        if os.path.exists("rouille_geo.jpg"):
            st.image("rouille_geo.jpg", caption="repères topographiques")
        else:
            st.warning("L'image 'rouille_geo.jpg' est introuvable.")

    st.divider()

    st.write(
        "Découvrez l'évolution de la science à travers cette mise en scène historique."
    )

    # --- SECTION CARICATURE ET TEXTE BLEU ---
    col_graph_hist, col_bd_hist = st.columns(2)

    with col_graph_hist:
        st.write(
            "**La BD humoristique textuelle : La révolution invisible de l'électron**"
        )

        # Affichage du texte narratif dans l'encadré bleu d'information
        st.info(
            "**Case 1 :** Antoine Lavoisier, en perruque blanche dans son laboratoire de 1777, regarde un morceau de fer brûler sous une cloche de verre. Il note fièrement sur son cahier : 'Le fer s'associe avec l'oxygène de l'air pour devenir de la rouille. J'appelle cela l'oxydation ! C'est clair et limpide !'.\n\n"
            "**Case 2 :** Un siècle plus tard, en 1897, le physicien J.J. Thomson observe ses tubes à rayons cathodiques avec une loupe. Il sursaute sur sa chaise en découvrant une particule minuscule et s'écrie : 'Eurêka ! Il y a des grains d'électricité négative encore plus petits que les atomes ! Je vais les appeler les électrons !'.\n\n"
            "**Case 3 :** Réunion imaginaire au sommet de la chimie au début du 20e siècle. Gilbert Lewis montre un schéma à Lavoisier et lui explique : 'Mon cher Antoine, votre oxygène n'était qu'un intermédiaire ! Regardez de plus près : le fer rouille parce qu'il perd ses électrons. L'oxydation, c'est en réalité une fuite d'électrons !'.\n\n"
            "**Case 4 :** Un atome de fer moderne, équipé d'un bouclier protecteur, regarde les molécules d'oxygène passer au loin sans pouvoir l'atteindre. Il affiche un grand sourire et s'exclame : 'Merci la science ! Maintenant qu'on connaît le secret de nos électrons, les ingénieurs nous protègent contre la corrosion !'."
        )

    with col_bd_hist:
        if os.path.exists("historique_caricature.jpg"):
            st.image(
                "historique_caricature.jpg",
                caption="Illustration humoristique du changement de modèle scientifique en 4 cases",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'historique_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    if "suite_verrouille_tab1_redox" not in st.session_state:
        st.session_state.suite_verrouille_tab1_redox = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_redox

    # Affichage du module de questions specifique a l'histoire de la chimie redox
    afficher_atelier_histoire_verrouille(verrouille=verrou_at1)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique.",
        key="check_certif_redox1_final_net",
        disabled=verrou_at1,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1",
        key="btn_export_suite1_redox_official",
        use_container_width=True,
        disabled=verrou_at1,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not case_certif_stat1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatisee du Quiz
            score_q1 = 0.0
            if "ordre_quiz_tab1_redox_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_redox_aleatoire:
                    saisie = st.session_state.get(
                        f"redox_at1_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # Correction automatisee du Texte a trous
            score_t1 = 0.0
            if "champs_redox1_clean" in st.session_state:
                for ligne in st.session_state.champs_redox1_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if (
                        st.session_state.get(f"{cle}_redox1_clean", "Choisir...")
                        == attendu
                    ):
                        score_t1 += 1.0

            # Sauvegarde des scores et verrouillage
            st.session_state.score_suite1_redox_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_redox_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_redox = round(
                float(score_q1 + score_t1), 1
            )
            st.session_state.suite_verrouille_tab1_redox = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab1_redox", False):
        scr1_t1 = st.session_state.get("score_suite1_redox_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_redox_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_redox", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20"
        )

        html_export_redox1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Oxydoreduction - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #2563eb; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Chimie</h1>
                <p>Atelier 1 : Contexte historique de l'oxydoréduction et évolution des modèles</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab1_redox_aleatoire" in st.session_state:
            for num, q_item in enumerate(
                st.session_state.ordre_quiz_tab1_redox_aleatoire, 1
            ):
                saisie = st.session_state.get(
                    f"redox_at1_final_g_{q_item['id']}", "Choisir..."
                )
                attendu = q_item["rep"]
                v_lbl = (
                    "CORRECT"
                    if str(saisie).strip() == str(attendu).strip()
                    else "INCORRECT"
                )
                v_class = (
                    "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                )
                html_export_redox1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_redox1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_redox1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_redox1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(
                    f"{cle_variable}_redox1_clean", "Choisir..."
                )
                v_lbl_t = (
                    "CORRECT"
                    if str(saisie_texte).strip() == str(attendu_texte).strip()
                    else "INCORRECT"
                )
                v_class_t = (
                    "status-correct"
                    if v_lbl_t == "CORRECT"
                    else "status-incorrect"
                )
                html_export_redox1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_redox1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html_redox1 = preparer_nom_fichier(
            "Rapport_Histoire_Redox"
        ).replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_redox1,
            file_name=nom_fichier_html_redox1,
            mime="text/html",
        )


with tab2:
    st.header("La Réaction d'Oxydation")

    if os.path.exists("oxydation_intro.jpg"):
        st.image(
            "oxydation_intro.jpg",
            caption="Mise en évidence expérimentale de l'oxydation d'un métal",
            use_container_width=True,
        )
    else:
        st.warning(
            "L'image 'oxydation_intro.jpg' n'a pas été trouvée dans le dossier."
        )

    st.subheader("Qu'est-ce qu'une oxydation ?")
    st.write(
        "Selon la définition électronique moderne, une **oxydation** est une transformation chimique "
        "au cours de laquelle une espèce chimique **perd un ou plusieurs électrons**."
    )

    st.info(
        "L'espèce chimique qui perd ces électrons est appelée le **réducteur**. "
        "Le réducteur est donc le donneur d'électrons. Après avoir perdu ses électrons, le réducteur se transforme "
        "en son oxydant conjugué."
    )

    # =============================================================================
    # NOUVEAU MENU DÉROULANT INTERACTIF LIÉ À LA BIBLIOTHÈQUE REDOX
    # =============================================================================
    st.subheader("Générateur dynamique de demi-équations d'oxydation")
    st.write(
        "Sélectionnez un couple dans le menu pour transformer sa fiche de la bibliothèque en réaction d'oxydation pure :"
    )

    # Extraction des couples disponibles dans votre dictionnaire global
    liste_couples_dispo = list(bibliotheque_redox.keys())

    couple_choisi_ox = st.selectbox(
        "Choisir un couple à oxyder :",
        liste_couples_dispo,
        key="select_menu_oxydation_dynamique",
    )

    if couple_choisi_ox:
        data_couple = bibliotheque_redox[couple_choisi_ox]

        # Découpage du nom pour isoler la forme Ox et la forme Red
        nom_propre_couple = couple_choisi_ox.split("(")[0].strip()
        forme_ox_texte = nom_propre_couple.split("/")[0].strip()
        forme_red_texte = nom_propre_couple.split("/")[1].strip()

        col_menu1, col_menu2 = st.columns(2)
        with col_menu1:
            st.markdown(f"**Analyse du couple :** {couple_choisi_ox}")
            st.write(f"- Réducteur de départ : **{forme_red_texte}**")
            st.write(f"- Oxydant conjugué produit : **{forme_ox_texte}**")
            st.write(
                f"- Quantité d'électrons libérés : **{data_couple['electrons']} e⁻**"
            )
            st.write(f"- Degré d'oxydation de l'oxydant : {data_couple['no_ox']}")

        with col_menu2:
            st.markdown("**Équation de l'oxydation (Milieu Acide) :**")
            # Inversion logique de la chaîne pour écrire dans le sens Red -> Ox + ne-
            # Pour les métaux simples comme Cu, Zn, Fe, le rendu est direct.
            if data_couple["h3o"] == 0:
                st.latex(
                    rf"\text{{{forme_red_texte}}} \longrightarrow \text{{{forme_ox_texte}}} + {data_couple['electrons']}e^-"
                )
            else:
                # Modèle adapté pour les couples complexes avec molécules d'eau
                st.latex(
                    rf"\text{{{forme_red_texte}}} + {data_couple['h2o_acide']}\text{{H}}_2\text{{O}} \longrightarrow \text{{{forme_ox_texte}}} + {data_couple['h3o']}\text{{H}}_3\text{{O}}^+ + {data_couple['electrons']}e^-"
                )

    st.divider()

    st.subheader("La formulation mathématique et exemples types")

    # --- SECTION FORMULE GÉNÉRALE ---
    col_21, col_22 = st.columns(2)
    with col_21:
        st.markdown("**Équation générale d'une oxydation :**")
        st.write(
            "Le réducteur (Red) donne un oxydant (Ox) et libère une quantité 'n' d'électrons."
        )
        st.latex(r"\text{Réducteur} \longrightarrow \text{Oxydant} + n \cdot e^-")
    with col_22:
        if os.path.exists("formule_oxydation.jpg"):
            st.image(
                "formule_oxydation.jpg", caption="Mécanisme de perte d'électrons"
            )
        else:
            st.warning("L'image 'formule_oxydation.jpg' est introuvable.")

    # --- SECTION EXEMPLE DU FER (Récupéré de la bibliothèque) ---
    col_23, col_24 = st.columns(2)
    with col_23:
        st.markdown("**Exemple 1 : L'oxydation du fer métallique (Fe)**")
        st.write(
            "Dans un milieu humide ou agressif, un atome de fer solide se dégrade. "
            "Les données du couple de référence indiquent :"
        )
        # Extraction dynamique des données du couple Fe2+ / Fe
        if "Fe²⁺ / Fe" in bibliotheque_redox:
            un_couple = bibliotheque_redox["Fe²⁺ / Fe"]
            st.write(f"- Nombre d'électrons libérés : {un_couple['electrons']}")
            st.write(
                f"- Degré d'oxydation final de l'ion : {un_couple['no_ox']}"
            )
        # Transformation de la demi-équation de la bibliothèque (sens Oxydation : Red -> Ox + ne-)
        st.latex(r"\text{Fe} \longrightarrow \text{Fe}^{2+} + 2e^-")
    with col_24:
        if os.path.exists("oxydation_fer.jpg"):
            st.image(
                "oxydation_fer.jpg",
                caption="Formation des ions ferreux de la rouille",
            )
        else:
            st.warning("L'image 'oxydation_fer.jpg' est introuvable.")

    # --- SECTION EXEMPLE DU ZINC (Récupéré de la bibliothèque) ---
    col_25, col_26 = st.columns(2)
    with col_25:
        st.markdown("**Exemple 2 : L'oxydation du zinc (Zn)**")
        st.write(
            "Le zinc métallique, couramment utilisé pour la galvanisation et la protection des aciers, "
            "s'oxyde selon les paramètres de sa fiche technique :"
        )
        # Extraction dynamique des données du couple Zn2+ / Zn
        if "Zn²⁺ / Zn" in bibliotheque_redox:
            un_couple_zn = bibliotheque_redox["Zn²⁺ / Zn"]
            st.write(
                f"- Nombre d'électrons transférés : {un_couple_zn['electrons']}"
            )
            st.write(
                f"- Degré d'oxydation de la forme oxydée : {un_couple_zn['no_ox']}"
            )
        st.latex(r"\text{Zn} \longrightarrow \text{Zn}^{2+} + 2e^-")
    with col_26:
        if os.path.exists("oxydation_zinc.jpg"):
            st.image(
                "oxydation_zinc.jpg",
                caption="Oxydation sacrificielle du zinc de protection",
            )
        else:
            st.warning("L'image 'oxydation_zinc.jpg' est introuvable.")

    st.divider()

    st.write(
        "Découvrez le mécanisme intime de l'oxydation à travers cette mise en scène."
    )

    # --- SECTION CARICATURE ET TEXTE BLEU ---
    col_graph_ox, col_bd_ox = st.columns(2)

    with col_graph_ox:
        st.write(
            "**La BD humoristique textuelle : Le drame des électrons perdus**"
        )
        st.info(
            "**Case 1 :** Un atome de fer solide est tranquillement installé dans la structure métallique d'un châssis de camion. Il discute avec ses voisins métalliques : 'Tout va bien les gars, la cohésion est parfaite, on forme un bloc d'acier indestructible !'.\n\n"
            "**Case 2 :** Une goute d'eau salée chargée d'oxygène atterrit pile sur l'atome de fer. L'oxygène, très gourmand, attrape l'atome par le bras et lui crie : 'Hé toi ! Donne-moi tes charges ! Tes deux électrons de valence m'intéressent grandement !'.\n\n"
            "**Case 3 :** L'atome de fer, dépouillé de ses deux électrons de protection, commence à se dissoudre et à se détacher du réseau métallique. Il panique en se voyant changer de couleur : 'Oh non ! Je viens de subir une oxydation ! Je ne suis plus un métal solide, je me transforme en ion Fe2+ soluble ! C'est la liquéfaction !'.\n\n"
            "**Case 4 :** Le fer oxydé flotte désormais dans la solution sous forme de rouille friable, laissant un trou béant dans la poutre. Les atomes d'oxygène s'enfuient en ricanant avec leur butin électronique : 'Affaire classée ! Encore un réducteur de terrassé par notre pouvoir oxydant !'."
        )

    with col_bd_ox:
        if os.path.exists("oxydation_caricature.jpg"):
            st.image(
                "oxydation_caricature.jpg",
                caption="Illustration humoristique du mécanisme d'oxydation en 4 cases",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'oxydation_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    import os

    if "suite_verrouille_tab2_oxydation" not in st.session_state:
        st.session_state.suite_verrouille_tab2_oxydation = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_oxydation

    # Affichage du module de questions specifique a la reaction d'oxydation
    afficher_atelier_oxydation_verrouille(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur l'Oxydation.",
        key="check_certif_ox2_final_net",
        disabled=verrou_at2,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2",
        key="btn_export_suite2_ox_official",
        use_container_width=True,
        disabled=verrou_at2,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not case_certif_stat2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatisee du Quiz
            score_q2 = 0.0
            if "ordre_quiz_tab2_ox_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_ox_aleatoire:
                    saisie = st.session_state.get(
                        f"ox_at2_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # Correction automatisee du Texte a trous
            score_t2 = 0.0
            if "champs_ox2_clean" in st.session_state:
                for ligne in st.session_state.champs_ox2_clean:
                    cle_variable = ligne[-1]
                    attendu_valeur = ligne[2]
                    if (
                        st.session_state.get(f"{cle_variable}_ox2_clean", "Choisir...")
                        == attendu_valeur
                    ):
                        score_t2 += 1.0

            # Sauvegarde des scores et verrouillage
            st.session_state.score_suite2_ox_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_ox_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_ox = round(
                float(score_q2 + score_t2), 1
            )
            st.session_state.suite_verrouille_tab2_oxydation = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab2_oxydation", False):
        scr1_t2 = st.session_state.get("score_suite2_ox_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_ox_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_ox", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER OXYDATION SCELLÉ | Note de session : {tot_s_t2:.1f} / 20"
        )

        html_export_ox2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Oxydation - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b91c1c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #2563eb; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Chimie</h1>
                <p>Atelier 2 : Étude de la réaction d'oxydation et perte d'électrons</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2_ox_aleatoire" in st.session_state:
            for num, q_item in enumerate(
                st.session_state.ordre_quiz_tab2_ox_aleatoire, 1
            ):
                saisie = st.session_state.get(
                    f"ox_at2_final_g_{q_item['id']}", "Choisir..."
                )
                attendu = q_item["rep"]
                v_lbl = (
                    "CORRECT"
                    if str(saisie).strip() == str(attendu).strip()
                    else "INCORRECT"
                )
                v_class = (
                    "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                )
                html_export_ox2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ox2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_ox2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ox2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(
                    f"{cle_variable}_ox2_clean", "Choisir..."
                )
                v_lbl_t = (
                    "CORRECT"
                    if str(saisie_texte).strip() == str(attendu_texte).strip()
                    else "INCORRECT"
                )
                v_class_t = (
                    "status-correct"
                    if v_lbl_t == "CORRECT"
                    else "status-incorrect"
                )
                html_export_ox2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ox2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Utilisation securisee de os.path
        nom_brut = preparer_nom_fichier("Rapport_Atelier_Oxydation")
        nom_fichier_html_ox2 = os.path.basename(nom_brut).replace(
            ".txt", ".html"
        )

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_ox2,
            file_name=nom_fichier_html_ox2,
            mime="text/html",
        )



with tab3:
    st.header("La Réaction de Réduction")

    if os.path.exists("reduction_intro.jpg"):
        st.image(
            "reduction_intro.jpg",
            caption="Mise en évidence expérimentale de la réduction en laboratoire",
            use_container_width=True,
        )
    else:
        st.warning(
            "L'image 'reduction_intro.jpg' n'a pas été trouvée dans le dossier."
        )

    st.subheader("Qu'est-ce qu'une réduction ?")
    st.write(
        "Selon la définition électronique moderne, une **réduction** est une transformation chimique "
        "au cours de laquelle une espèce chimique **gagne un ou plusieurs électrons**."
    )

    st.info(
        "L'espèce chimique qui capte ces électrons est appelée l'**oxydant**. "
        "L'oxydant est donc le receveur d'électrons. Après avoir emmagasiné ces charges négatives, l'oxydant se transforme "
        "en son réducteur conjugué."
    )

    # Menu déroulant connecté à la bibliothèque redox
    st.subheader("Générateur dynamique de demi-équations de réduction")
    st.write(
        "Sélectionnez un couple dans le menu pour afficher sa réaction de réduction pure (sens du gain d'électrons) :"
    )

    liste_couples_dispo = list(bibliotheque_redox.keys())

    couple_choisi_red = st.selectbox(
        "Choisir un couple à réduire :",
        liste_couples_dispo,
        key="select_menu_reduction_dynamique",
    )

    if couple_choisi_red:
        data_couple = bibliotheque_redox[couple_choisi_red]

        # 1. On isole d'abord ce qui est avant la parenthèse pour ne garder que "MnO4⁻ / Mn²⁺"
        formules_brutes = couple_choisi_red.split("(")[0].strip()

        # 2. On sépare ensuite de manière sécurisée selon le premier slash trouvé
        partie_gauche, partie_droite = formules_brutes.split("/", 1)

        # 3. Nettoyage final des espaces blancs restants
        forme_ox_texte = partie_gauche.strip()
        forme_red_texte = partie_droite.strip()

        # Reste du rendu inchangé...
        col_menu1, col_menu2 = st.columns(2)
        with col_menu1:
            st.markdown(f"**Analyse du couple :** {couple_choisi_red}")
            st.write(f"- Oxydant de départ : **{forme_ox_texte}**")
            st.write(f"- Réducteur conjugué produit : **{forme_red_texte}**")
            st.write(
                f"- Quantité d'électrons captés : **{data_couple['electrons']} e⁻**"
            )
            st.write(
                f"- Décompte molécules d'eau associées : {data_couple['h2o_acide']} H2O"
            )

        with col_menu2:
            st.markdown("**Équation de la réduction (Milieu Acide) :**")
            # Affichage de la chaîne LaTeX directement extraite de la bibliothèque
            st.latex(data_couple["milieu_acide"])

    st.divider()

    st.write(
        "Découvrez le mécanisme intime de la réduction à travers cette mise en scène."
    )

    # --- SECTION CARICATURE ET TEXTE BLEU ---
    col_graph_red, col_bd_red = st.columns(2)

    with col_graph_red:
        st.write(
            "**La BD humoristique textuelle : Le sauvetage des ions égarés**"
        )
        st.info(
            "**Case 1 :** Un ion cuivre II (Cu2+) flotte tristement dans l'eau bleue d'un bécher. Privé de ses deux électrons de surface, il appelle à l'aide : 'Je me sens si vide et immatériel en tant qu'ion soluble... Si seulement quelqu'un pouvait me rendre nos charges !'.\n\n"
            "**Case 2 :** Une électrode de carbone reliée à un générateur électrique plonge dans la solution. Un flux massif de charges négatives arrive par le câble. L'électrode crie dans le liquide : 'Avis à la population ionique ! Distribution générale d'électrons frais en provenance de la borne négative !'.\n\n"
            "**Case 3 :** L'ion cuivre se précipite sur la surface métallique et intercepte deux électrons au passage. Un éclair d'énergie traverse sa structure : 'Ça y est ! C'est la réduction ! Mes orbitales se remplissent à nouveau, je quitte mon état d'ion dissous !'.\n\n"
            "**Case 4 :** L'atome de cuivre redevenu neutre s'accroche solidement à la paroi sous forme de métal solide et brillant. Il salue ses compagnons restés en solution : 'Opération réussie ! Grâce à ce gain d'électrons, je reprenne ma place de solide indestructible. L'oxydant a été réduit !'."
        )

    with col_bd_red:
        if os.path.exists("reduction_caricature.jpg"):
            st.image(
                "reduction_caricature.jpg",
                caption="Illustration humoristique du mécanisme de réduction en 4 cases",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'reduction_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    if "suite_verrouille_tab3_reduction" not in st.session_state:
        st.session_state.suite_verrouille_tab3_reduction = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_reduction

    afficher_atelier_reduction_verrouille(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Réduction.",
        key="check_certif_red3_final_net",
        disabled=verrou_at3,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3",
        key="btn_export_suite3_red_official",
        use_container_width=True,
        disabled=verrou_at3,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not case_certif_stat3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Note du Quiz (ramenée sur 10 pts : 2 pts par question)
            score_q3 = 0.0
            if "ordre_quiz_tab3_red_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_red_aleatoire:
                    saisie = st.session_state.get(
                        f"red_at3_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q3 += 2.0

            # Note du Texte à trous (ramenée sur 10 pts : 2 pts par case)
            score_t3 = 0.0
            if "champs_red3_clean" in st.session_state:
                for ligne in st.session_state.champs_red_clean:
                    cle_variable = ligne[-1]
                    attendu_valeur = ligne[2]
                    if (
                        st.session_state.get(
                            f"{cle_variable}_red3_clean", "Choisir..."
                        )
                        == attendu_valeur
                    ):
                        score_t3 += 2.0

            st.session_state.score_suite3_red_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_red_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_red = round(
                float(score_q3 + score_t3), 1
            )
            st.session_state.suite_verrouille_tab3_reduction = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab3_reduction", False):
        scr1_t3 = st.session_state.get("score_suite3_red_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_red_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_red", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER RÉDUCTION SCELLÉ | Note de session : {tot_s_t3:.1f} / 20"
        )

        html_export_red3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Réduction - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #15803d; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #2563eb; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Chimie</h1>
                <p>Atelier 3 : Étude de la réaction de réduction et gain d'électrons</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #15803d;">
                Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Synthèse de Cours : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
        </body>
        </html>
        """

        nom_brut = preparer_nom_fichier("Rapport_Atelier_Reduction")
        nom_fichier_html_red3 = os.path.basename(nom_brut).replace(
            ".txt", ".html"
        )

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_red3,
            file_name=nom_fichier_html_red3,
            mime="text/html",
        )



with tab4:
    st.header("Les Couples Redox")

    if os.path.exists("couples_intro.jpg"):
        st.image(
            "couples_intro.jpg",
            caption="Représentation de la dualité Oxydant / Réducteur",
            use_container_width=True,
        )
    else:
        st.warning(
            "L'image 'couples_intro.jpg' n'a pas été trouvée dans le dossier."
        )

    st.subheader("Qu'est-ce qu'un couple redox ?")
    st.write(
        "En chimie, un oxydant et un réducteur ne réagissent jamais seuls. "
        "Ils sont indissociables et forment ce que l'on appelle un **couple oxydant/réducteur** (ou couple redox). "
        "Par convention, un couple s'écrit toujours dans l'ordre suivant : **Oxydant / Réducteur**."
    )

    st.info(
        "La forme oxydée et la forme réduite d'un même élément chimique sont dites **conjuguées**. "
        "Le passage de l'une à l'autre se fait par un transfert réversible d'électrons, formalisé par une double flèche "
        "dans la demi-équation."
    )

    st.subheader("La formulation mathématique et exemples de couples")

    # --- SECTION FORMULE GÉNÉRALE ---
    col_41, col_42 = st.columns(2)
    with col_41:
        st.markdown("**Équation générale d'un couple redox :**")
        st.write(
            "La double flèche indique que la transformation peut se produire dans les deux sens "
            "(oxydation ou réduction selon les partenaires de la réaction)."
        )
        st.latex(r"\text{Oxydant} + n \cdot e^- \rightleftharpoons \text{Réducteur}")
    with col_42:
        if os.path.exists("formule_couple.jpg"):
            st.image(
                "formule_couple.jpg", caption="Schéma du transfert réversible"
            )
        else:
            st.warning("L'image 'formule_couple.jpg' est introuvable.")

    # --- SECTION EXEMPLE DU COUPLE CUIVRE ---
    col_43, col_44 = st.columns(2)
    with col_43:
        st.markdown("**Exemple 1 : Le couple Cu²⁺ / Cu**")
        st.write(
            "L'ion cuivre II (Cu²⁺) est l'oxydant conjugué du cuivre métallique (Cu), qui est le réducteur. "
            "Leur passage mutuel met en jeu deux électrons."
        )
        st.latex(r"\text{Cu}^{2+} + 2e^- \rightleftharpoons \text{Cu}")
    with col_44:
        if os.path.exists("couple_cuivre.jpg"):
            st.image(
                "couple_cuivre.jpg",
                caption="Forme ionique liquide (bleue) et forme métallique solide (orange)",
            )
        else:
            st.warning("L'image 'couple_cuivre.jpg' est introuvable.")

    # --- SECTION EXEMPLE DU COUPLE FER ---
    col_45, col_46 = st.columns(2)
    with col_45:
        st.markdown("**Exemple 2 : Le couple Fe²⁺ / Fe**")
        st.write(
            "Ce couple est au cœur des problématiques de corrosion. L'ion fer II (Fe²⁺) "
            "coexiste avec le fer solide (Fe) par le biais d'un échange de deux électrons."
        )
        st.latex(r"\text{Fe}^{2+} + 2e^- \rightleftharpoons \text{Fe}")
    with col_46:
        if os.path.exists("couple_fer.jpg"):
            st.image(
                "couple_fer.jpg",
                caption="Équilibre électrochimique des espèces du fer",
            )
        else:
            st.warning("L'image 'couple_fer.jpg' est introuvable.")

    st.divider()

    st.write(
        "Découvrez la notion de couple redox à travers cette mise en scène."
    )

    # --- SECTION CARICATURE ET TEXTE BLEU ---
    col_graph_couple, col_bd_couple = st.columns(2)

    with col_graph_couple:
        st.write(
            "**La BD humoristique textuelle : Le pacte indissociable du binôme**"
        )
        st.info(
            "**Case 1 :** Un ion Zinc (Zn2+) et un atome de Zinc métallique (Zn) sont assis sur le canapé d'un conseiller d'orientation chimique. Le conseiller leur dit : 'Vous devez faire un choix, vous ne pouvez pas rester indécis entre être un liquide ou un solide !'.\n\n"
            "**Case 2 :** L'atome de Zinc solide secoue la tête et répond : 'Impossible d'être séparés ! Nous sommes les deux faces d'une même pièce. S'il perd deux électrons, je deviens lui. Si je les récupère, il devient moi !'.\n\n"
            "**Case 3 :** Le conseiller regarde ses fiches, perplexe, et s'exclame : 'C'est une vraie colocation électronique ! Un coup à gauche avec les électrons, un coup à droite sans les électrons... Comment écrivez-vous cette alliance ?'.\n\n"
            "**Case 4 :** Le binôme brandit un panneau arborant une double flèche parfaitement équilibrée. Le Zinc solide conclut fièrement : 'Nous écrivons Oxydant / Réducteur avec une double flèche au milieu. Nous sommes un couple redox, liés pour le pire et pour le meilleur !'."
        )

    with col_bd_couple:
        if os.path.exists("couple_caricature.jpg"):
            st.image(
                "couple_caricature.jpg",
                caption="Illustration humoristique de la notion de couple en 4 cases",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'couple_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    if "suite_verrouille_tab4_couples" not in st.session_state:
        st.session_state.suite_verrouille_tab4_couples = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_couples

    # Appel de la fonction de l'atelier
    afficher_atelier_couples_verrouille(verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur les Couples.",
        key="check_certif_cpl4_final_net",
        disabled=verrou_at4,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4",
        key="btn_export_suite4_cpl_official",
        use_container_width=True,
        disabled=verrou_at4,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not case_certif_stat4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Note du Quiz (2 pts par question)
            score_q4 = 0.0
            if "ordre_quiz_tab4_cpl_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_cpl_aleatoire:
                    saisie = st.session_state.get(
                        f"cpl_at4_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q4 += 2.0

            # Note du Texte à trous (2 pts par case)
            score_t4 = 0.0
            if "champs_cpl4_clean" in st.session_state:
                for ligne in st.session_state.champs_cpl4_clean:
                    cle_variable = ligne[-1]
                    attendu_valeur = ligne[2]
                    if (
                        st.session_state.get(
                            f"{cle_variable}_cpl4_clean", "Choisir..."
                        )
                        == attendu_valeur
                    ):
                        score_t4 += 2.0

            st.session_state.score_suite4_cpl_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_cpl_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_cpl = round(
                float(score_q4 + score_t4), 1
            )
            st.session_state.suite_verrouille_tab4_couples = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab4_couples", False):
        scr1_t4 = st.session_state.get("score_suite4_cpl_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_cpl_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_cpl", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER COUPLES SCELLÉ | Note de session : {tot_s_t4:.1f} / 20"
        )

        html_export_cpl4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Couples Redox - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4f46e5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Chimie</h1>
                <p>Atelier 4 : Étude de la notion de couple Oxydant / Réducteur</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4f46e5;">
                Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Synthèse de Cours : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
        </body>
        </html>
        """

        nom_brut = preparer_nom_fichier("Rapport_Atelier_Couples")
        nom_fichier_html_cpl4 = os.path.basename(nom_brut).replace(
            ".txt", ".html"
        )

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_cpl4,
            file_name=nom_fichier_html_cpl4,
            mime="text/html",
        )


with tab5:


    # --- SECTION DU TRACÉ DU GAMMA ---
    col_51, col_52 = st.columns(2)
    with col_51:

        # Utilisation stricte de la bibliothèque os pour sécuriser l'image d'en-tête
        st.subheader("Prévoir la spontanéité d'une réaction")
        st.write(
            "Tous les oxydants n'ont pas la même force pour capter des électrons, et tous les réducteurs "
            "n'ont pas la même facilité à les céder. Pour prévoir si une réaction chimique va se produire "
            "naturellement, on classe les couples redox sur une échelle verticale selon leur **potentiel standard d'oxydoréduction (E⁰)** exprimé en Volts."
        )

        st.info(
            "L'axe vertical est orienté vers le haut par ordre de pouvoir oxydant croissant (et pouvoir réducteur décroissant). "
            "La **règle du gamma** stipule que la réaction chimique spontanée a toujours lieu entre **l'oxydant le plus fort** "
            "(situé en haut à gauche) et **le réducteur le plus fort** (situé en bas à droite)."
        )

        if os.path.exists("potentiel_echelle.jpg"):
            st.image(
                "potentiel_echelle.jpg",
                caption="Exemple de potentiels ",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'potentiel_echelle.jpg' n'a pas été trouvée dans le dossier."
            )


        st.subheader("Tracé géométrique de la règle")
        
        st.markdown("**Méthode de lecture graphique :**")
        st.write(
            "En traçant une ligne reliant l'Oxydant 1 au Réducteur 2, puis en passant au travers "
            "pour rejoindre l'Oxydant 2 et le Réducteur 1, on dessine la lettre grecque **Gamma (γ)**."
        )
        st.write(
            "Si le sens du tracé suit le produit d'un Gamma à l'endroit, la réaction est thermodynamiquement "
            "spontanée et possible. Si le tracé dessine un Gamma inversé, la réaction est impossible sans apport extérieur d'énergie."
        )
    with col_52:
        st.header("La Règle du Gamma")
        if os.path.exists("gamma_intro.jpg"):
            st.image(
                "gamma_intro.jpg",
                caption="Échelle des potentiels standards d'oxydoréduction ",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'gamma_intro.jpg' n'a pas été trouvée dans le dossier."
            )

        
        if os.path.exists("regle_gamma_trace.jpg"):
            st.image(
                "regle_gamma_trace.jpg",
                caption="Tracé de la lettre Gamma (γ) sur l'échelle des potentiels",
            )
        else:
            st.warning("L'image 'regle_gamma_trace.jpg' est introuvable.")

    st.divider()

    st.write(
        "Découvrez le principe de la règle du gamma à travers cette mise en scène."
    )

    # --- SECTION CARICATURE ET TEXTE BLEU ---
    col_graph_gamma, col_bd_gamma = st.columns(2)

    with col_graph_gamma:
        st.write(
            "**La BD humoristique textuelle : Le duel des forces de l'échelle**"
        )
        st.info(
            "**Case 1 :** L'ion Cuivre II (Cu2+) trône fièrement tout en haut de l'échelle des potentiels, gonflant ses muscles moléculaires. Tout en bas, le Zinc solide (Zn) le regarde d'un air défiant en ajustant ses gants : 'Hé le cuivre ! Je te vois faire le fier là-haut, mais sache que j'ai une réserve d'électrons prêts à sauter !'.\n\n"
            "**Case 2 :** L'ion Cu2+ rigole et répond : 'Parfait ! Viens te frotter à moi ! Je suis un oxydant puissant, j'adore capter les charges. Mon potentiel E0 est bien plus élevé que le tien, tu n'as aucune chance de les garder !'.\n\n"
            "**Case 3 :** Un arbitre chimiste arrive avec un grand marqueur noir et dessine une ligne courbe qui part du Cu2+, plonge vers le Zinc solide, remonte vers l'ion Zinc naissant et termine sur le Cuivre métallique. L'arbitre s'écrie : 'Le tracé est impeccable ! Ça dessine un magnifique alphabet grec !'.\n\n"
            "**Case 4 :** Le Zinc solide s'est oxydé et le Cuivre s'est matérialisé en métal rouge au tapis. L'arbitre lève le bras du vainqueur et conclut : 'Victoire par KO technique ! La lettre Gamma a parlé, la réaction spontanée a balayé les réactifs !'."
        )

    with col_bd_gamma:
        if os.path.exists("gamma_caricature.jpg"):
            st.image(
                "gamma_caricature.jpg",
                caption="Illustration humoristique de la règle du Gamma en 4 cases",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'gamma_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
    if "suite_verrouille_tab5_gamma" not in st.session_state:
        st.session_state.suite_verrouille_tab5_gamma = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_gamma

    # Rendu du module d'évaluation
    afficher_atelier_gamma_verrouille(verrouille=verrou_at5)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Règle du Gamma.",
        key="check_certif_gam5_final_net",
        disabled=verrou_at5,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5",
        key="btn_export_suite5_gam_official",
        use_container_width=True,
        disabled=verrou_at5,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not case_certif_stat5:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Note du Quiz (2 pts par réponse juste)
            score_q5 = 0.0
            if "ordre_quiz_tab5_gam_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_gam_aleatoire:
                    saisie = st.session_state.get(
                        f"gam_at5_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q5 += 2.0

            # Note du Texte à trous (2 pts par case juste)
            score_t5 = 0.0
            if "champs_gam5_clean" in st.session_state:
                for ligne in st.session_state.champs_gam5_clean:
                    cle_variable = ligne[-1]
                    attendu_valeur = ligne
                    if (
                        st.session_state.get(
                            f"{cle_variable}_gam5_clean", "Choisir..."
                        )
                        == attendu_valeur
                    ):
                        score_t5 += 2.0

            st.session_state.score_suite5_gam_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_gam_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_gam = round(
                float(score_q5 + score_t5), 1
            )
            st.session_state.suite_verrouille_tab5_gamma = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab5_gamma", False):
        scr1_t5 = st.session_state.get("score_suite5_gam_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_gam_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_gam", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER GAMMA SCELLÉ | Note de session : {tot_s_t5:.1f} / 20"
        )

        html_export_gam5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Regre du Gamma - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4f46e5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Chimie</h1>
                <p>Atelier 5 : Application de la règle du Gamma et spontanéité des réactions</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4f46e5;">
                Quiz Technique : <strong>{scr1_t5:.1f} / 10</strong><br>
                Synthèse de Cours : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>
        </body>
        </html>
        """

        # Utilisation de os.path pour l'export sain du fichier .html
        nom_brut = preparer_nom_fichier("Rapport_Atelier_Gamma")
        nom_fichier_html_gam5 = os.path.basename(nom_brut).replace(
            ".txt", ".html"
        )

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_gam5,
            file_name=nom_fichier_html_gam5,
            mime="text/html",
        )


with tab6:
    st.header("Réaction d'Oxydoréduction")

    # Utilisation stricte de la bibliothèque os pour sécuriser l'image d'en-tête
    if os.path.exists("bilan_redox_intro.jpg"):
        st.image(
            "bilan_redox_intro.jpg",
            caption="Le transfert global d'électrons entre le réducteur et l'oxydant",
            use_container_width=True,
        )
    else:
        st.warning(
            "L'image 'bilan_redox_intro.jpg' n'a pas été trouvée dans le dossier."
        )

    st.subheader("L'Équation Bilan Globale")
    st.write(
        "Une réaction d'oxydoréduction est l'association simultanée d'une demi-réaction d'oxydation "
        "et d'une demi-réaction de réduction. Les électrons ne peuvent pas exister à l'état libre en solution : "
        "tous les électrons cédés par le réducteur doivent être intégralement captés par l'oxydant."
    )

    st.info(
        "Pour écrire l'équation bilan, on additionne membre à membre les deux demi-équations après avoir "
        "multiplié chacune d'elles par un coefficient approprié, de manière à ce que le nombre d'électrons "
        "libérés soit rigoureusement égal au nombre d'électrons captés. Les électrons s'annulent alors et n'apparaissent plus dans le bilan final."
    )

    st.subheader("Méthode d'ajustement des coefficients")

    # --- SECTION DE L'ADDITION MEMBRE À MEMBRE ---
    col_61, col_62 = st.columns(2)
    with col_61:
        st.markdown("**Exemple classique : Fer métallique et ions Cuivre II**")
        st.write(
            "Le fer se fait oxyder en libérant 2 électrons, tandis que l'ion cuivre II se fait réduire en captant 2 électrons. "
            "Comme le nombre d'électrons échangés est identique (2 d'un côté, 2 de l'autre), l'addition est directe."
        )
        st.markdown("**Équation finale sans électrons libres :**")
        st.latex(
            r"\text{Zn (s)} + \text{Cu}^{2+}\text{ (aq)} \longrightarrow \text{Zn}^{2+}\text{ (aq)} + \text{Cu (s)}"
        )
    with col_62:
        if os.path.exists("bilan_addition_methode.jpg"):
            st.image(
                "bilan_addition_methode.jpg",
                caption="Méthodologie de simplification des électrons par addition",
            )
        else:
            st.warning("L'image 'bilan_addition_methode.jpg' est introuvable.")

    st.divider()

    st.write(
        "Découvrez le principe de la réaction d'oxydoréduction globale à travers cette mise en scène."
    )

    # --- SECTION CARICATURE ET TEXTE BLEU ---
    col_graph_bilan, col_bd_bilan = st.columns(2)

    with col_graph_bilan:
        st.write(
            "**La BD humoristique textuelle : Le grand traité de paix électronique**"
        )
        st.info(
            "**Case 1 :** Dans le bécher, l'agitation est totale. Le Zinc solide crie en jetant deux électrons dans la solution : 'Je n'en veux plus, ils me pèsent ! Je m'oxyde !'. Les deux électrons flottent sans abri, créant une étincelle de tension dans le liquide.\n\n"
            "**Case 2 :** L'ion Cuivre II (Cu2+) aperçoit les charges orphelines, fonce dessus en ouvrant grand ses liaisons et s'exclame : 'Quelle aubaine ! Exactement ce qu'il me fallait pour me réduire et me stabiliser sous forme de métal solide !'.\n\n"
            "**Case 3 :** Un inspecteur de la ligue de protection des particules passe au crible les réactifs avec une balance de pesée et déclare : 'Le compte est bon. Deux électrons perdus à gauche, deux électrons gagnés à droite. Aucun électron n'a fui la pièce !'.\n\n"
            "**Case 4 :** Les électrons disparus des équations finales laissent place à un magnifique dépôt rouge de cuivre pur. Les deux couples signent le registre de la réaction bilan et concluent en chœur : 'Plus d'électricité statique, la neutralité est totale, l'oxydoréduction a fusionné nos destins !'."
        )

    with col_bd_bilan:
        if os.path.exists("bilan_caricature.jpg"):
            st.image(
                "bilan_caricature.jpg",
                caption="Illustration humoristique de l'équation bilan globale en 4 cases",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'bilan_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    if "suite_verrouille_tab6_bilan" not in st.session_state:
        st.session_state.suite_verrouille_tab6_bilan = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_bilan

    # Rendu du module d'évaluation
    afficher_atelier_bilan_verrouille(verrouille=verrou_at6)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Équation Bilan.",
        key="check_certif_bil6_final_net",
        disabled=verrou_at6,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6",
        key="btn_export_suite6_bil_official",
        use_container_width=True,
        disabled=verrou_at6,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not case_certif_stat6:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Note du Quiz (2 pts par réponse juste)
            score_q6 = 0.0
            if "ordre_quiz_tab6_bil_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_bil_aleatoire:
                    saisie = st.session_state.get(
                        f"bil_at6_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q6 += 2.0

            # Note du Texte à trous (2 pts par case juste)
            score_t6 = 0.0
            if "champs_bil6_clean" in st.session_state:
                for ligne in st.session_state.champs_bil6_clean:
                    cle_variable = ligne[-1]
                    attendu_valeur = ligne
                    if (
                        st.session_state.get(
                            f"{cle_variable}_bil6_clean", "Choisir..."
                        )
                        == attendu_valeur
                    ):
                        score_t6 += 2.0

            st.session_state.score_suite6_bil_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_bil_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_bil = round(
                float(score_q6 + score_t6), 1
            )
            st.session_state.suite_verrouille_tab6_bilan = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab6_bilan", False):
        scr1_t6 = st.session_state.get("score_suite6_bil_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_bil_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6_bil", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER BILAN SCELLÉ | Note de session : {tot_s_t6:.1f} / 20"
        )

        html_export_bil6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Equation Bilan - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Chimie</h1>
                <p>Atelier 6 : Équation bilan globale d'oxydoréduction</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Quiz Technique : <strong>{scr1_t6:.1f} / 10</strong><br>
                Synthèse de Cours : <strong>{scr2_t6:.1f} / 10</strong><br>
                Note Totale : <strong>{tot_s_t6:.1f} / 20</strong>
            </p>
        </body>
        </html>
        """

        # Utilisation de os.path pour l'export sain du fichier .html
        nom_brut = preparer_nom_fichier("Rapport_Atelier_Bilan")
        nom_fichier_html_bil6 = os.path.basename(nom_brut).replace(
            ".txt", ".html"
        )

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_bil6,
            file_name=nom_fichier_html_bil6,
            mime="text/html",
        )


with tab7:
    st.header("Application dans le domaine du transport routier")

    # 1. BANQUE DE DONNÉES DYNAMIQUE PAR CAS (ÉNONCÉ, BD, QUIZ, TROUS)
    if "banque_complete_routier" not in st.session_state:
        st.session_state.banque_complete_routier = {
            "routier_cas1": {
                "titre": " Corrosion par le sel de déneigement sur les châssis",
                "texte": "En hiver, le salage des routes apporte une quantité massive d'ions chlorure. L'humidité stagnante sur les longerons en acier crée un milieu conducteur agressif. Le fer métallique solide du châssis subit une oxydation destructrice et cède ses électrons au dioxygène de l'air humide, entraînant la formation de cloques de rouille.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Un camion de 44 tonnes roule de nuit sous une tempête de neige. Derrière lui, une saleuse projette du sel. Le chauffeur sourit : 'Super, la route est bien dégagée !'.\n\n"
                    "**Case 2 :** Zoom sous le châssis en acier. Une boue salée recouvre les longerons. Les ions Chlorure (Cl⁻) ricanent : 'La peinture a sauté ici ! Installez l'autoroute à électrons !'.\n\n"
                    "**Case 3 :** Les atomes de fer perdent leurs électrons face au dioxygène : 'Oh non ! Le sel rend l'eau trop conductrice, la fuite de nos charges est trop rapide ! On s'oxyde en ions Fe²⁺ !'.\n\n"
                    "**Case 4 :** Au printemps, le mécanicien tape sur le châssis et de la rouille tombe : 'Encore un coup de l'oxydoréduction hivernale... Il va falloir souder un renfort !'."
                ),
                "quiz": [
                    {"id": "rA1", "q": "Qui est le réducteur métallique qui se détériore sur le châssis ?", "options": ["Le fer solide", "Le dioxygène", "L'ion chlorure"], "rep": "Le fer solide"},
                    {"id": "rA2", "q": "Qui est l'oxydant gazeux présent dans l'air humide responsable de l'attaque ?", "options": ["Le dioxygène", "Le diazote", "Le dioxyde de carbone"], "rep": "Le dioxygène"},
                    {"id": "rA3", "q": "Combien d'électrons sont transférés par chaque atome de fer lors de cette oxydation ?", "options": ["2 électrons", "1 électron", "4 électrons"], "rep": "2 électrons"},
                    {"id": "rA4", "q": "Combien d'électrons capte le dioxygène pour se réduire en milieu acide ?", "options": ["4 électrons", "2 électrons", "1 électron"], "rep": "4 électrons"},
                    {"id": "rA5", "q": "Quelle couleur prend le produit de corrosion friable sur le châssis ?", "options": ["Orange / Brun (Rouille)", "Bleu azur", "Vert"], "rep": "Orange / Brun (Rouille)"},
                    {"id": "rA6", "q": "Quelle est la teinte de la tôle d'acier saine avant l'action du sel ?", "options": ["Gris métallique brillant", "Noir opaque", "Rouge"], "rep": "Gris métallique brillant"},
                    {"id": "rA7", "q": "Quel est le rôle des ions chlorures apportés par le sel de déneigement ?", "options": ["Augmenter la conductivité de l'eau", "Bloquer les électrons", "Dissoudre le plastique"], "rep": "Augmenter la conductivité de l'eau"},
                    {"id": "rA8", "q": "La transformation subie par le fer solide (perte d'électrons) est une :", "options": ["Oxydation", "Réduction", "Précipitation"], "rep": "Oxydation"},
                    {"id": "rA9", "q": "En perdant ses charges négatives, l'atome de fer du camion devient un :", "options": ["Cation Fe²⁺", "Anion Fe²⁻", "Gaz libre"], "rep": "Cation Fe²⁺"},
                    {"id": "rA10", "q": "Le milieu aqueux salé formé sous le châssis constitue un bon :", "options": ["Électrolyte", "Isolant électrique", "Catalyseur neutre"], "rep": "Électrolyte"}
                ],
                "trous": [
                    ("1. Dans ce cas, le fer solide du châssis joue le rôle de ..........", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_rA1"),
                    ("2. Le dioxygène de l'air capte les électrons lors d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_rA2"),
                    ("3. Chaque atome de fer libère un total de .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_rA3"),
                    ("4. Le sel ne réagit pas mais rend le milieu très ..........", ["Choisir...", "conducteur", "isolant"], "conducteur", "t_rA4"),
                    ("5. La dégradation du fer se manifeste par de la .......... orange.", ["Choisir...", "rouille", "calamine"], "rouille", "t_rA5"),
                    ("6. L'atome neutre de fer se transforme en un .......... soluble.", ["Choisir...", "ion", "gaz"], "ion", "t_rA6"),
                    ("7. L'éclat d'un châssis métallique sain est de couleur ..........", ["Choisir...", "grise", "brune"], "grise", "t_rA7"),
                    ("8. Les électrons migrent à travers l'humidité depuis le ..........", ["Choisir...", "métal", "gaz"], "métal", "t_rA8"),
                    ("9. La réduction de l'oxydant produit des molécules d'..........", ["Choisir...", "eau", "sel"], "eau", "t_rA9"),
                    ("10. L'égalisation des charges élimine les électrons du .......... final.", ["Choisir...", "bilan", "solvant"], "bilan", "t_rA10")
                ]
            },
            "routier_cas2": {
                "titre": " Attaque acide des bennes de transport de produits chimiques",
                "texte": "Une benne en acier transporte des résidus industriels acides mal neutralisés. Les ions hydronium H₃O⁺ attaquent les parois intérieures de la cuve de transport. Le fer solide s'oxyde et se dissout, tandis que les ions acides subissent une réduction immédiate provoquant un dégagement de dihydrogène gazeux sous pression.",
                "couple_ox": "H3O⁺ / H2",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Une citerne routière transporte une solution acide. Le manomètre de sécurité indique une mystérieuse montée de pression : 'C'est bizarre, le volume de gaz augmente !'.\n\n"
                    "**Case 2 :** À l'intérieur de la cuve, le revêtement est endommagé. Les ions acides H₃O⁺ se ruent sur l'acier : 'Regardez, le fer est à nu ! À l'attaque, piquons-lui ses charges !'.\n\n"
                    "**Case 3 :** Les atomes de fer portent leurs électrons et se dissolvent : 'Au secours, les acides nous oxydent en ions Fe²⁺ ! Notre paroi s'amincit !'.\n\n"
                    "**Case 4 :** En captant les électrons, les ions hydronium se transforment en bulles de dihydrogène gazeux (H₂) : 'Liberté ! On passe à l'état gazeux, attention à la pression dans la benne !'."
                ),
                "quiz": [
                    {"id": "rB1", "q": "Qui est le réducteur de la benne qui se fait dissoudre par la solution ?", "options": ["Le fer solide", "L'ion hydronium H₃O⁺", "Le gaz dihydrogène"], "rep": "Le fer solide"},
                    {"id": "rB2", "q": "Qui est l'oxydant acide responsable de la destruction de la paroi ?", "options": ["L'ion hydronium H₃O⁺", "Le fer solide", "L'eau neutre"], "rep": "L'ion hydronium H₃O⁺"},
                    {"id": "rB3", "q": "Quel gaz inflammable se dégage sous pression dans la citerne ?", "options": ["Le dihydrogène", "Le dioxygène", "Le chlore"], "rep": "Le dihydrogène"},
                    {"id": "rB4", "q": "Combien d'électrons cède un atome de fer lors de cette attaque acide ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "rB5", "q": "Quel type de milieu chimique (pH inférieur à 7) cause cette panne ?", "options": ["Un milieu acide", "Un milieu basique", "Un milieu neutre"], "rep": "Un milieu acide"},
                    {"id": "rB6", "q": "Quelle est la couleur de la paroi d'acier intacte à l'intérieur de la benne ?", "options": ["Gris brillant", "Rouge rouille", "Jaune"], "rep": "Gris brillant"},
                    {"id": "rB7", "q": "Que subit la tôle métallique lors de sa transformation en ions Fe²⁺ ?", "options": ["Une oxydation", "Une réduction", "Une évaporation"], "rep": "Une oxydation"},
                    {"id": "rB8", "q": "La transformation de l'ion H₃O⁺ en gaz H₂ constitue une :", "options": ["Réduction", "Oxydation", "Combustion"], "rep": "Réduction"},
                    {"id": "rB9", "q": "En s'oxydant, l'atome de fer neutre devient un ion de charge :", "options": ["Positive (Fe²⁺)", "Négative (Fe²⁻)", "Neutre"], "rep": "Positive (Fe²⁺)"},
                    {"id": "rB10", "q": "La formation du gaz H₂ fait courir au transport un risque de :", "options": ["Surpression et explosion", "Gel du liquide", "Liquéfaction"], "rep": "Surpression et explosion"}
                ],
                "trous": [
                    ("1. La paroi de la benne en fer subit une .......... destructive.", ["Choisir...", "oxydation", "réduction"], "oxydation", "t_rB1"),
                    ("2. Les ions hydronium de l'acide subissent une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_rB2"),
                    ("3. Le fer métallique joue le rôle de .......... dans ce transport.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_rB3"),
                    ("4. L'agression provient d'un liquide de nature ..........", ["Choisir...", "acide", "basique"], "acide", "t_rB4"),
                    ("5. La réduction des protons génère un dégagement de ..........", ["Choisir...", "dihydrogène", "dioxygène"], "dihydrogène", "t_rB5"),
                    ("6. Chaque atome de fer transfère un total de .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_rB6"),
                    ("7. L'acier sain non attaqué présente une couleur ..........", ["Choisir...", "grise", "orange"], "grise", "t_rB7"),
                    ("8. Le fer solide détruit passe en solution sous forme d'..........", ["Choisir...", "ion", "précipité"], "ion", "t_rB8"),
                    ("9. Les électrons quittent le métal pour réduire l'..........", ["Choisir...", "acide", "sel"], "acide", "t_rB9"),
                    ("10. L'égalisation des charges permet d'écrire l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_rB10")
                    ]
                    },      
            "routier_cas3": {
                "titre": " Protection par anodes en zinc sur les remorques porte-engins",
                "texte": "Pour préserver les essieux et structures basses des remorques porte-engins, les constructeurs installent des blocs de zinc. Lors d'une agression saline, le zinc s'oxyde en premier à la place du fer de la structure. Le zinc se sacrifie pour empêcher la réduction de l'oxygène sur l'acier.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Zn²⁺ / Zn",
                "bd": (
                    "**Case 1 :** Une remorque porte-engins revient d'une mission en zone côtière, couverte de boue saline. Le technicien sourit : 'Heureusement qu'on a fixé ces blocs de métal en dessous !'.\n\n"
                    "**Case 2 :** L'eau salée attaque la structure. Le bloc de zinc s'interpose devant l'acier : 'Pas touche au fer ! C'est moi le plus réducteur ici, j'envoie mes électrons !'.\n\n"
                    "**Case 3 :** Le zinc subit une oxydation et se dissout lentement : 'Je perds mes électrons et je deviens l'ion Zn²⁺, je me sacrifie pour la remorque !'.\n\n"
                    "**Case 4 :** L'acier de la remorque reste intact et brillant, tandis que l'oxygène est réduit sans faire de rouille. L'acier remercie : 'Merci l'anode sacrificielle !'."
                ),
                "quiz": [
                    {"id": "rC1", "q": "Quel métal se sacrifie et joue le rôle de réducteur actif ici ?", "options": ["Le zinc", "Le fer", "Le cuivre"], "rep": "Le zinc"},
                    {"id": "rC2", "q": "Quel métal est protégé de la rouille grâce à cette méthode ?", "options": ["Le fer (acier)", "Le zinc", "L'aluminium"], "rep": "Le fer (acier)"},
                    {"id": "rC3", "q": "Qui est l'oxydant de l'air humide que le zinc doit neutraliser ?", "options": ["Le dioxygène", "Le diazote", "L'ion zinc"], "rep": "Le dioxygène"},
                    {"id": "rC4", "q": "Combien d'électrons un atome de zinc libère-t-il en s'oxydant en ion Zn²⁺ ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "rC5", "q": "Quelle est la couleur d'origine du bloc de zinc protecteur sain ?", "options": ["Gris mat / bleuté", "Rouge cuivre", "Transparent"], "rep": "Gris mat / bleuté"},
                    {"id": "rC6", "q": "Quel qualificatif donne-t-on à cette méthode de protection de l'acier ?", "options": ["Protection sacrificielle", "Passivation acide", "Vernis étanche"], "rep": "Protection sacrificielle"},
                    {"id": "rC7", "q": "Pourquoi le zinc réagit-il à la place du fer de la remorque ?", "options": ["Il est plus réducteur que le fer", "Il est plus noble", "Il est plus lourd"], "rep": "Il est plus réducteur que le fer"},
                    {"id": "rC8", "q": "Quelle transformation subit le zinc en donnant ses charges ?", "options": ["Une oxydation", "Une réduction", "Une fusion"], "rep": "Une oxydation"},
                    {"id": "rC9", "q": "La captation des électrons par le dioxygène constitue la demi-réaction de :", "options": ["Réduction", "Oxydation", "Liquéfaction"], "rep": "Réduction"},
                    {"id": "rC10", "q": "En s'oxydant, l'atome de zinc solide produit des ions :", "options": ["Zn²⁺", "Fe²⁺", "Cl⁻"], "rep": "Zn²⁺"}
                ],
                "trous": [
                    ("1. Le zinc métallique cède ses électrons, c'est le .......... de la remorque.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_rC1"),
                    ("2. Le dioxygène capte ces électrons au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_rC2"),
                    ("3. Le zinc se dégrade pour assurer une protection ..........", ["Choisir...", "sacrificielle", "acide"], "sacrificielle", "t_rC3"),
                    ("4. Chaque atome de zinc sacrifie un total de .......... électrons.", ["Choisir...", "deux", "trois"], "deux", "t_rC4"),
                    ("5. Grâce au zinc, l'acier de la structure conserve sa teinte ..........", ["Choisir...", "grise", "orange"], "grise", "t_rC5"),
                    ("6. L'atome neutre de zinc solide se transforme en un .......... Zn²⁺.", ["Choisir...", "ion", "gaz"], "ion", "t_rC6"),
                    ("7. L'humidité saline environnante joue le rôle d'.......... conducteur.", ["Choisir...", "électrolyte", "isolant"], "électrolyte", "t_rC7"),
                    ("8. Le potentiel E0 du zinc est plus bas, il est donc plus .......... que le fer.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_rC8"),
                    ("9. Le dioxygène se réduit en produisant des molécules d'..........", ["Choisir...", "eau", "zinc"], "eau", "t_rC9"),
                    ("10. L'absence d'électrons libres caractérise l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_rC10")
                ]
            }
        }
    # =============================================================================
    # 2. INITIALISATION DU CAS PROFESSIONNEL PAR DÉFAUT
    # =============================================================================
    if "choix_id_routier" not in st.session_state:
        st.session_state.choix_id_routier = "routier_cas1"

    # =============================================================================
    # 3. INTERACTION DU BOUTON : FORCER LE CHANGEMENT VERS UN AUTRE CAS
    # =============================================================================
    col_btn_gen, _ = st.columns([0.3, 0.7])
    with col_btn_gen:
        if st.button(
            "GÉNÉRER UN EXERCICE AU HASARD",
            key="btn_generer_exercice_aleatoire_t7",
            use_container_width=True,
        ):
            # Liste absolue des cas programmés dans votre dictionnaire
            options_totale = ["routier_cas1", "routier_cas2", "routier_cas3"]
            cas_en_cours = st.session_state.choix_id_routier

            # On filtre pour exclure le cas en cours et forcer le changement réel
            choix_restants = [c for c in options_totale if c != cas_en_cours]
            st.session_state.choix_id_routier = random.choice(choix_restants)

            # Déverrouillage immédiat des formulaires pour la nouvelle partie
            st.session_state.verrou_routier_bilan = False
            st.session_state.verrou_routier_at = False
            st.session_state.suite_verrouille_tab7_routier = False

            # Nettoyage des anciennes notes enregistrées
            if "score_routier_partie_bilan" in st.session_state:
                del st.session_state["score_routier_partie_bilan"]

            # Force le rechargement immédiat de la page
            st.rerun()

    st.write("---")

    # =============================================================================
    # 4. AFFECTATION DES VARIABLES DU CAS CHOISI POUR LE RENDU DE L'INTERFACE
    # =============================================================================
    id_cas = st.session_state.choix_id_routier
    cas_routier = st.session_state.banque_complete_routier[id_cas]

    # Tri persistant des questions du quiz pour éviter les mélanges intempestifs
    if f"quiz_melange_{id_cas}" not in st.session_state:
        liste_q = list(cas_routier["quiz"])
        random.shuffle(liste_q)
        st.session_state[f"quiz_melange_{id_cas}"] = liste_q

    questions_cas_optimales = st.session_state[f"quiz_melange_{id_cas}"]

    # =============================================================================
    # 5. AFFICHAGE DES TEXTES DE L'ÉNONCÉ ET DE L'IMAGE TECHNIQUE
    # =============================================================================
    # Extraction et affichage du titre et du texte du cas actif
    st.subheader(cas_routier["titre"])
    st.write(cas_routier["texte"])

    # Chargement sécurisé de l'image de constat technique sur le terrain
    image_routier = f"{id_cas}.jpg"
    if os.path.exists(image_routier):
        st.image(
            image_routier,
            caption="Constat visuel de la dégradation sur le matériel de transport",
        )
    else:
        st.warning(
            f"L'image '{image_routier}' n'a pas été trouvée à la racine de l'application."
        )

    st.divider()

    # =============================================================================
    # 6. RENDU DE LA CARICATURE (DOUBLE COLONNE : TEXTE BLEU + IMAGE BD)
    # =============================================================================
    col_g_rt, col_b_rt = st.columns(2)

    with col_g_rt:
        st.write("**La BD humoristique textuelle adaptée à votre situation**")
        # Affichage de la bande dessinée spécifique au cas dans l'encadré bleu
        st.info(cas_routier["bd"])

    with col_b_rt:
        image_bd = f"bd_{id_cas}.jpg"
        if os.path.exists(image_bd):
            st.image(
                image_bd,
                caption="Illustration caricaturale du mécanisme chimique",
                use_container_width=True,
            )
        else:
            st.warning(
                f"L'illustration caricaturale '{image_bd}' est introuvable."
            )

    st.divider()



    # =============================================================================
    # ACTIVITÉ INTERACTIVE : GÉNÉRATEUR D'ÉQUATION BILAN (10 POINTS)
    # =============================================================================
    st.subheader("Générateur d'équation bilan du transport (Note sur 10 points)")
    st.write(
        "Sélectionnez les bons éléments et équilibrez l'équation finale par rapport à l'énoncé ci-dessus :"
    )

    if "verrou_routier_bilan" not in st.session_state:
        st.session_state.verrou_routier_bilan = False
    v_routier = st.session_state.verrou_routier_bilan

    # 1. PREMIÈRE LIGNE DE SÉLECTION : LES COUPLES ET DEMI-ÉQUATIONS
    col_rb1, col_rb2 = st.columns(2)
    with col_rb1:
        choix_rc_ox = st.selectbox(
            "Sélectionnez le couple de l'oxydant :",
            ["Choisir...", "O2 / H2O", "H3O⁺ / H2", "Fe²⁺ / Fe"],
            disabled=v_routier,
            key="rc_ox_sel",
        )
        choix_rdemi_ox = st.selectbox(
            "Sélectionnez la bonne écriture de l'oxydation :",
            [
                "Choisir...",
                "Fe -> Fe²⁺ + 2e⁻",
                "Zn -> Zn²⁺ + 2e⁻",
                "2H2O -> O2 + 4H3O⁺ + 4e⁻",
            ],
            disabled=v_routier,
            key="rdemi_ox_sel",
        )

    with col_rb2:
        choix_rc_red = st.selectbox(
            "Sélectionnez le couple du réducteur :",
            ["Choisir...", "Fe²⁺ / Fe", "Zn²⁺ / Zn", "O2 / H2O"],
            disabled=v_routier,
            key="rc_red_sel",
        )
        choix_rdemi_red = st.selectbox(
            "Sélectionnez la bonne écriture de la réduction :",
            [
                "Choisir...",
                "O2 + 4H3O⁺ + 4e⁻ -> 6H2O",
                "2H3O⁺ + 2e⁻ -> H2 + 2H2O",
                "Fe²⁺ + 2e⁻ -> Fe",
            ],
            disabled=v_routier,
            key="rdemi_red_sel",
        )

    # 2. DEUXIÈME LIGNE DE SÉLECTION : L'ÉQUATION BILAN GLOBALE FINALE
    st.markdown("**Équilibrez l'équation bilan globale finale :**")

    # Découpage strict en colonnes proportionnelles pour reproduire fidèlement la mise en page
    col_re1, col_re2, col_re3, col_re4, col_re5, col_re6, col_re7 = st.columns(
        [0.15, 0.25, 0.05, 0.25, 0.05, 0.25, 0.25], vertical_alignment="center"
    )

    with col_re1:
        r_coef_1 = st.selectbox(
            "Coef", ["Choisir...", "1", "2"], key="rc1", disabled=v_routier
        )
    with col_re2:
        r_reactif_1 = st.selectbox(
            "Réactif 1",
            ["Choisir...", "Fe", "Zn", "O2"],
            key="rr1",
            disabled=v_routier,
        )
    with col_re3:
        st.write("**+**")
    with col_re4:
        r_reactif_2 = st.selectbox(
            "Réactif 2",
            ["Choisir...", "O2", "H3O⁺", "H2O"],
            key="rr2",
            disabled=v_routier,
        )
    with col_re5:
        st.write("**→**")
    with col_re6:
        r_prod_1 = st.selectbox(
            "Produit 1",
            ["Choisir...", "Fe²⁺", "Zn²⁺", "H2"],
            key="rp1",
            disabled=v_routier,
        )
    with col_re7:
        r_prod_2 = st.selectbox(
            "Produit 2",
            ["Choisir...", "H2O", "H2", "Fe²⁺"],
            key="rp2",
            disabled=v_routier,
        )

    # 3. SCRIPT DE CORRECTION AUTOMATISÉE ET ATTRIBUTION DES POINTS
    if st.button(
        "VALIDER L'ÉQUATION BILAN [10 PTS]",
        key="btn_v_rb_routier_officiel",
        disabled=v_routier,
    ):
        if (
            choix_rc_ox == "Choisir..."
            or choix_rc_red == "Choisir..."
            or r_reactif_1 == "Choisir..."
            or r_reactif_2 == "Choisir..."
            or r_coef_1 == "Choisir..."
            or r_prod_1 == "Choisir..."
            or r_prod_2 == "Choisir..."
        ):
            st.error("Action refusée : Veuillez remplir tous les choix avant de valider.")
        else:
            r_score = 0.0

            # Vérification de l'identification des couples (4 points)
            if choix_rc_ox == cas_routier["couple_ox"]:
                r_score += 2.0
            if choix_rc_red == cas_routier["couple_red"]:
                r_score += 2.0

            # Vérification des réactifs, produits et coefficients stœchiométriques (6 points)
            if (
                id_cas == "routier_cas1"
                and r_coef_1 == "2"
                and r_reactif_1 == "Fe"
                and r_reactif_2 == "O2"
                and r_prod_1 == "Fe²⁺"
                and r_prod_2 == "H2O"
            ):
                r_score += 6.0
            elif (
                id_cas == "routier_cas2"
                and r_coef_1 == "1"
                and r_reactif_1 == "Fe"
                and r_reactif_2 == "H3O⁺"
                and r_prod_1 == "Fe²⁺"
                and r_prod_2 == "H2"
            ):
                r_score += 6.0
            elif (
                id_cas == "routier_cas3"
                and r_coef_1 == "2"
                and r_reactif_1 == "Zn"
                and r_reactif_2 == "O2"
                and r_prod_1 == "Zn²⁺"
                and r_prod_2 == "H2O"
            ):
                r_score += 6.0

            st.session_state.score_routier_partie_bilan = r_score
            st.session_state.verrou_routier_bilan = True
            st.rerun()

    if st.session_state.get("verrou_routier_bilan"):
        st.info(
            f"Note enregistrée pour l'équation bilan : {st.session_state.get('score_routier_partie_bilan', 0.0)} / 10"
        )

    st.divider()


    # Mélange persistant des questions du quiz propre au cas actif
    if f"quiz_melange_{id_cas}" not in st.session_state:
        liste_q = list(cas_routier["quiz"])
        random.shuffle(liste_q)
        st.session_state[f"quiz_melange_{id_cas}"] = liste_q

    questions_cas_optimales = st.session_state[f"quiz_melange_{id_cas}"]

    if "suite_verrouille_tab7_routier" not in st.session_state:
        st.session_state.suite_verrouille_tab7_routier = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_routier

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat7 = st.checkbox(
        "Je certifie avoir complété toutes les activités adaptées de cet Atelier (Bilan et Questionnaire).",
        key="check_certif_routier7_scelle",
        disabled=verrou_at7,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7",
        key="btn_exp_t7_final_official",
        disabled=verrou_at7,
        use_container_width=True,
    ):
        if st.session_state.get("nom_var", "Nom") in [
            "Nom",
            "",
        ] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error(
                "Action refusée : Saisissez votre identité dans l'onglet 'Identification'."
            )
        elif not st.session_state.get("verrou_routier_bilan", False):
            st.error(
                "Action refusée : Vous devez valider l'Équation Bilan ci-dessus au préalable."
            )
        elif not case_certif_stat7:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Note du Générateur d'Équation Bilan (déjà enregistrée sur 10 pts)
            note_b = float(
                st.session_state.get("score_routier_partie_bilan", 0.0)
            )

            # 2. Correction automatisée du Quiz Technique (10 pts)
            score_q7 = 0.0
            for q in questions_cas_optimales:
                saisie_q = st.session_state.get(
                    f"routier_quiz_{q['id']}", "Choisir..."
                )
                if str(saisie_q).strip() == str(q["rep"]).strip():
                    score_q7 += 1.0

            # 3. Correction automatisée de la Synthèse à trous (10 pts)
            score_t7 = 0.0
            for t in cas_routier["trous"]:
                cle_t = t[-1]
                attendu_t = t[2]
                saisie_t = st.session_state.get(
                    f"{cle_t}_routier_clean", "Choisir..."
                )
                if str(saisie_t).strip() == str(attendu_t).strip():
                    score_t7 += 1.0

            # 4. Enregistrement des notes globales de session sur 30 points
            st.session_state.score_t7_bilan_final = round(note_b, 1)
            st.session_state.score_t7_atelier_final = round(
                float(score_q7 + score_t7), 1
            )
            st.session_state.score_final_global_t7 = round(
                float(note_b + score_q7 + score_t7), 1
            )
            st.session_state.suite_verrouille_tab7_routier = True
            st.rerun()

    # --- COMPILATION DU RAPPORT INDIVIDUEL SCELLÉ HTML ---
    if "suite_verrouille_tab7_routier" not in st.session_state:
        st.session_state.suite_verrouille_tab7_routier = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_routier

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat7 = st.checkbox(
        "Je certifie avoir complété toutes les activités adaptées de cet Atelier (Bilan et Questionnaire).",
        key="check_certif_routier7_scelle_officiel",
        disabled=verrou_at7,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7",
        key="btn_exp_t7_final_official_ajuste",
        disabled=verrou_at7,
        use_container_width=True,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not st.session_state.get("verrou_routier_bilan", False):
            st.error("Action refusée : Vous devez valider l'Équation Bilan ci-dessus au préalable.")
        elif not case_certif_stat7:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Note du Générateur d'Équation Bilan (sur 10 pts)
            note_b = float(st.session_state.get("score_routier_partie_bilan", 0.0))

            # 2. Correction automatisée du Quiz Technique (10 pts)
            score_q7 = 0.0
            for q in questions_cas_optimales:
                saisie_q = st.session_state.get(f"routier_quiz_{q['id']}", "Choisir...")
                if str(saisie_q).strip() == str(q["rep"]).strip():
                    score_q7 += 1.0

            # 3. CORRECTION OPTIMISÉE : Comparaison directe avec la variable textuelle 'attendu_t'
            score_t7 = 0.0
            for t in cas_routier["trous"]:
                enonce_t, choix_t, attendu_t, cle_t = t  # Déballage propre des 4 éléments du dictionnaire
                saisie_t = st.session_state.get(f"{cle_t}_routier_clean", "Choisir...")
                if str(saisie_t).strip() == str(attendu_t).strip():
                    score_t7 += 1.0

            # 4. Enregistrement des notes globales de session sur 30 points
            st.session_state.score_t7_bilan_final = round(note_b, 1)
            st.session_state.score_t7_atelier_final = round(float(score_q7 + score_t7), 1)
            st.session_state.score_final_global_t7 = round(float(note_b + score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_routier = True
            st.rerun()

    # --- COMPILATION DU RAPPORT INDIVIDUEL SCELLÉ HTML POUR LE TRANSPORT ---
    if st.session_state.get("suite_verrouille_tab7_routier", False):
        not_b = st.session_state.get("score_t7_bilan_final", 0.0)
        not_at = st.session_state.get("score_t7_atelier_final", 0.0)
        not_tot = st.session_state.get("score_final_global_t7", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRANSPORT ROUTIER SCELLÉ | Note globale enregistrée : {not_tot:.1f} / 30")

        equation_eleve_texte = f"{r_coef_1} {r_reactif_1} + {r_reactif_2} -> {r_prod_1} + {r_prod_2}"
        bd_html_format = cas_routier["bd"].replace("\n\n", "<br><br>")

        html_export_routier = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Transport Routier - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #2563eb; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                .enonce-box {{ background-color: #f1f5f9; border-left: 4px solid #1e3a8a; padding: 15px; margin-bottom: 20px; font-size: 13px; line-height: 1.5; }}
                .bd-box {{ background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 20px; font-size: 13px; font-style: italic; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Individuel Officiel</h1>
                <p>Filière professionnelle : Transport Routier et Logistique</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite7}</p>
                <div class="score-badge">SCORE FINAL<br><span style="font-size: 32px;">{not_tot:.1f}</span> / 30</div>
            </div>
            
            <div class="sub-title">Énoncé de l'étude de cas évaluée</div>
            <div class="enonce-box">
                <strong>{cas_routier['titre']}</strong><br><br>
                {cas_routier['texte']}
            </div>

            <div class="sub-title">La Caricature Pédagogique Associée</div>
            <div class="bd-box">
                {bd_html_format}
            </div>

            <div class="sub-title">Synthèse des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                1. Modélisation de l'Équation Bilan Globale : <strong>{not_b:.1f} / 10</strong><br>
                2. Questionnaire Technique de Synthèse (Quiz + Trous) : <strong>{not_at:.1f} / 20</strong><br>
                <strong>Note totale consolidée : {not_tot:.1f} / 30</strong>
            </p>

            <div class="sub-title">Activité 1 : Vérification de la configuration d'Équation Bilan</div>
            <table>
                <thead>
                    <tr><th>Paramètre d'Éléments</th><th>Saisie Réalisée Élève</th><th>Attendu Académique</th></tr>
                </thead>
                <tbody>
                    <tr><td>Couple de l'Oxydant sélectionné</td><td>{choix_rc_ox}</td><td>{cas_routier['couple_ox']}</td></tr>
                    <tr><td>Couple du Réducteur sélectionné</td><td>{choix_rc_red}</td><td>{cas_routier['couple_red']}</td></tr>
                    <tr><td>Équation globale équilibrée</td><td><code>{equation_eleve_texte}</code></td><td>Validation par script automatique</td></tr>
                </tbody>
            </table>

            <div class="sub-title">Activité 2 : Correction détaillée du Quiz Technique (10 pts)</div>
            <table>
                <thead><tr><th>N°</th><th>Question Technique Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        for num, q_item in enumerate(questions_cas_optimales, 1):
            saisie = st.session_state.get(f"routier_quiz_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_routier += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_routier += """
                </tbody>
            </table>
            
            <div class="sub-title">Activité 3 : Correction détaillée de la Synthèse à trous (10 pts)</div>
            <table>
                <thead><tr><th>N°</th><th>Phrase complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        for num, t_item in enumerate(cas_routier["trous"], 1):
            enonce_t, _, attendu_t, cle_t = t_item
            saisie_t = st.session_state.get(f"{cle_t}_routier_clean", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_routier += f"<tr><td>{num}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_routier += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_brut = preparer_nom_fichier("Rapport_Application_Transport")
        nom_propre_html_t7 = os.path.basename(nom_fichier_brut).replace(".txt", ".html")

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel Transport Routier (.html)",
            data=html_export_routier,
            file_name=nom_propre_html_t7,
            mime="text/html",
            key="download_btn_t7_final",
        )




            

with tab8:
    st.header("Application dans le domaine de la maintenance")

    # =============================================================================
    # 1. BANQUE DE DONNÉES DYNAMIQUE PAR CAS POUR LA MAINTENANCE
    # =============================================================================
    if "banque_complete_maint" not in st.session_state:
        st.session_state.banque_complete_maint = {
            "maint_cas1": {
                "titre": " Corrosion perforante sur une canalisation de gaz enterrée",
                "texte": "Lors d'un audit de maintenance préventive, un technicien constate une chute de pression sur une conduite forcée en acier enterrée. Après excavation, il découvre une perforation nette entourée de rouille. En raison d'un défaut de la gaine isolante, le fer solide de la canalisation s'est oxydé en cédant ses électrons au dioxygène dissous dans l'eau du sol humide, transformant le métal rigide en ions Fe²⁺ solubles.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Un technicien de maintenance en bleu de travail inspecte une vanne de distribution de gaz. Le manomètre indique une chute de pression catastrophique. Il s'exclame : 'Alerte ! Fuite indétectable sur le secteur Nord ! Le débit s'effondre !'.\n\n"
                    "**Case 2 :** Après excavation du sol, le technicien découvre la conduite en acier. Elle présente une perforation nette entourée de rouille épaisse. En grattant, il trouve un vieux câble rompu qui flotte dans la boue humide et s'interproge : 'Mais qui a coupé cette liaison électrique ? Ce n'est pas une simple usure mécanique...'.\n\n"
                    "**Case 3 :** Zoom à l'échelle microscopique sous la terre humide. Les atomes de fer de la conduite hurlent en perdant leurs électrons : 'À l'aide ! Le milieu est trop acide ! Sans le courant de protection, on s'oxyde tous en ions Fe2+ ! Le métal fout le camp dans le sol !'.\n\n"
                    "**Case 4 :** Le technicien remplace le tronçon percé et s'apprête à concevoir un système de protection durable. L'analyse du courant de passivation montre que l'oxydoréduction des sols agressifs doit être neutralisée au plus vite pour sceller la canalisation."
                ),
                "quiz": [
                    {"id": "mA1", "q": "Qui est le réducteur métallique de départ qui subit la perforation sur la conduite ?", "options": ["Le fer solide", "Le dioxygène", "L'eau du sol"], "rep": "Le fer solide"},
                    {"id": "mA2", "q": "Qui est l'oxydant responsable de la capture des électrons de l'acier enterré ?", "options": ["Le dioxygène", "Le diazote", "L'ion fer II"], "rep": "Le dioxygène"},
                    {"id": "mA3", "q": "Combien d'électrons sont transférés par chaque atome de fer lors de cette oxydation ?", "options": ["2 électrons", "1 électron", "4 électrons"], "rep": "2 électrons"},
                    {"id": "mA4", "q": "Combien d'électrons capte le dioxygène pour se réduire en milieu acide ?", "options": ["4 électrons", "2 électrons", "6 électrons"], "rep": "4 électrons"},
                    {"id": "mA5", "q": "Quelle couleur prend l'oxyde de fer hydraté accumulé autour de la fuite ?", "options": ["Orange / Brun (Rouille)", "Bleu azur", "Vert"], "rep": "Orange / Brun (Rouille)"},
                    {"id": "mA6", "q": "Quelle est la couleur ou l'éclat de la canalisation en acier saine avant l'attaque ?", "options": ["Gris métallique brillant", "Noir mat", "Jaune laiton"], "rep": "Gris métallique brillant"},
                    {"id": "mA7", "q": "Quel type de milieu environnemental (humidité du sol) favorise cette dégradation ?", "options": ["Un milieu conducteur", "Un milieu isolant", "Un milieu totalement sec"], "rep": "Un milieu conducteur"},
                    {"id": "mA8", "q": "La transformation subie par le fer de la conduite (perte d'électrons) est une :", "options": ["Oxydation", "Réduction", "Précipitation"], "rep": "Oxydation"},
                    {"id": "mA9", "q": "En perdant ses charges négatives, l'atome de fer de la conduite devient un :", "options": ["Cation Fe²⁺", "Anion Fe²⁻", "Atome neutre"], "rep": "Cation Fe²⁺"},
                    {"id": "mA10", "q": "La transformation de l'oxydant qui capte les électrons s'appelle une :", "options": ["Réduction", "Oxydation", "Fusion"], "rep": "Réduction"}
                ],
                "trous": [
                    ("1. Dans ce cas, le fer solide de la canalisation agit comme le ..........", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_mA1"),
                    ("2. Le dioxygène dissous capte les électrons au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_mA2"),
                    ("3. Au cours de la dégradation, chaque atome de fer libère .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_mA3"),
                    ("4. L'humidité du sol environnant constitue un milieu liquide ..........", ["Choisir...", "conducteur", "isolant"], "conducteur", "t_mA4"),
                    ("5. La dégradation de la paroi de fer produit de la .......... friable.", ["Choisir...", "rouille", "calamine"], "rouille", "t_mA5"),
                    ("6. L'atome métallique neutre se transforme en un .......... Fe²⁺ soluble.", ["Choisir...", "ion", "gaz"], "ion", "t_mA6"),
                    ("7. L'éclat d'une canalisation en acier saine présente une teinte ..........", ["Choisir...", "grise", "brune"], "grise", "t_mA7"),
                    ("8. Les électrons quittent la tôle pour équilibrer la charge du ..........", ["Choisir...", "bilan", "solvant"], "bilan", "t_mA8"),
                    ("9. La réduction complète du dioxygène engendre des molécules d'..........", ["Choisir...", "eau", "gaz"], "eau", "t_mA9"),
                    ("10. L'égalisation des charges élimine les électrons de l'.......... finale.", ["Choisir...", "équation", "atmosphère"], "équation", "t_mA10")
                ]
            },
            "maint_cas2": {
                "titre": " Attaque acide par détartrage non inhibé sur un échangeur thermique",
                "texte": "Une équipe de maintenance réalise le nettoyage chimique d'un échangeur en acier à l'aide d'une solution acide pour éliminer le calcaire. Faute d'ajout d'un inhibiteur de corrosion, les ions hydronium H₃O⁺ attaquent directement le fer de la structure. Le fer solide s'oxyde et se dissout, provoquant un dégagement de dihydrogène gazeux.",
                "couple_ox": "H3O⁺ / H2",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Un technicien injecte une solution de détartrage acide dans le circuit d'un échangeur thermique. Soudain, un sifflement retentit au niveau de la purge d'air.\n\n"
                    "**Case 2 :** L'acide a dissous le calcaire mais s'attaque maintenant à la paroi métallique nue. Les ions hydronium H₃O⁺ s'exclament : 'Le fer n'est plus protégé, dépouillons-le de ses charges !'.\n\n"
                    "**Case 3 :** Les atomes de fer perdent leurs électrons et passent en solution : 'À l'aide, l'acide nous oxyde en ions Fe²⁺ ! La paroi de l'échangeur s'amincit à toute vitesse !'.\n\n"
                    "**Case 4 :** En absorbant les électrons, les ions hydronium se réduisent en bulles de dihydrogène gazeux (H₂). Le technicien coupe la pompe : 'Vite ! Stoppons l'oxydoréduction avant la perforation !'."
                ),
                "quiz": [
                    {"id": "mB1", "q": "Qui est le réducteur métallique qui subit la dissolution lors du détartrage ?", "options": ["Le fer solide", "L'ion hydronium", "Le gaz dihydrogène"], "rep": "Le fer solide"},
                    {"id": "mB2", "q": "Qui est l'oxydant acide responsable de la dégradation de la paroi ?", "options": ["L'ion hydronium H₃O⁺", "Le fer solide", "L'eau neutre"], "rep": "L'ion hydronium H₃O⁺"},
                    {"id": "mB3", "q": "Quel gaz inflammable se dégage dans le circuit de l'échangeur ?", "options": ["Le dihydrogène", "Le dioxygène", "Le diazote"], "rep": "Le dihydrogène"},
                    {"id": "mB4", "q": "Combien d'électrons cède un atome de fer lors de cette attaque acide ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "mB5", "q": "Quel type de milieu chimique (pH inférieur à 7) caractérise la solution de détartrage ?", "options": ["Un milieu acide", "Un milieu basique", "Un milieu neutre"], "rep": "Un milieu acide"},
                    {"id": "mB6", "q": "Quelle est la couleur de la tôle d'acier intacte à l'intérieur du circuit ?", "options": ["Gris métallique", "Rouge brique", "Vert"], "rep": "Gris métallique"},
                    {"id": "mB7", "q": "Que subit le fer métallique lors de sa transformation en ions Fe²⁺ ?", "options": ["Une oxydation", "Une réduction", "Une évaporation"], "rep": "Une oxydation"},
                    {"id": "mB8", "q": "La transformation de l'ion hydronium en gaz dihydrogène constitue une :", "options": ["Réduction", "Oxydation", "Combustion"], "rep": "Réduction"},
                    {"id": "mB9", "q": "En s'oxydant, l'atome de fer de l'échangeur devient un ion de charge :", "options": ["Positive (Fe²⁺)", "Négative (Fe²⁻)", "Neutre"], "rep": "Positive (Fe²⁺)"},
                    {"id": "mB10", "q": "L'égalisation des charges impose d'établir une équation dite :", "options": ["Bilan globale", "Partielle d'oxydation", "D'isomérisation"], "rep": "Bilan globale"}
                ],
                "trous": [
                    ("1. La paroi en fer de l'échangeur subit une .......... chimique.", ["Choisir...", "oxydation", "réduction"], "oxydation", "t_mb1"),
                    ("2. Les ions hydronium de la solution acide subissent une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_mb2"),
                    ("3. Le fer métallique joue le rôle de .......... dans ce détartrage.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_mb3"),
                    ("4. L'agression du circuit provient d'un liquide de nature ..........", ["Choisir...", "acide", "basique"], "acide", "t_mb4"),
                    ("5. La réduction des protons génère un dégagement de ..........", ["Choisir...", "dihydrogène", "dioxygène"], "dihydrogène", "t_mb5"),
                    ("6. Chaque atome de fer libère un total de .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_mb6"),
                    ("7. L'acier sain non attaqué présente une couleur ..........", ["Choisir...", "grise", "orange"], "grise", "t_mb7"),
                    ("8. Le fer solide détruit passe en solution sous forme d'.......... Fe²⁺.", ["Choisir...", "ion", "précipité"], "ion", "t_mb8"),
                    ("9. Les électrons quittent le métal pour réduire l'..........", ["Choisir...", "acide", "sel"], "acide", "t_mb9"),
                    ("10. L'égalisation des charges permet d'écrire l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_mb10")
                ]
            },
            "maint_cas3": {
                "titre": " Protection cathodique par anode sacrificielle en zinc sur un réservoir d'eau",
                "texte": "Pour préserver les parois intérieures d'un réservoir de stockage d'eau industrielle, le service de maintenance fixe un bloc de zinc. En présence d'eau conductrice, le zinc s'oxyde préférentiellement à la place de l'acier de la cuve, se sacrifiant pour empêcher la réduction du dioxygène sur le fer.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Zn²⁺ / Zn",
                "bd": (
                    "**Case 1 :** Un technicien de maintenance inspecte l'intérieur d'une cuve de stockage d'eau. Il sourit en voyant les parois intactes : 'Excellent, aucun point de rouille à signaler après un an !'.\n\n"
                    "**Case 2 :** L'eau du réservoir attaque la structure. Le bloc de zinc vissé s'interpose devant l'acier : 'Pas touche au fer ! C'est moi le plus réducteur ici, j'envoie mes électrons en premier !'.\n\n"
                    "**Case 3 :** Le zinc subit une oxydation et se dissout lentement : 'Je perds mes électrons de valence et je deviens l'ion Zn²⁺, je me sacrifie pour préserver la cuve !'.\n\n"
                    "**Case 4 :** L'acier du réservoir reste parfaitement gris et robuste, tandis que l'oxygène est réduit de façon inoffensive. La maintenance valide : 'L'anode sacrificielle a fonctionné !'."
                ),
                "quiz": [
                    {"id": "mC1", "q": "Quel métal se sacrifie et joue le rôle de réducteur actif ici ?", "options": ["Le zinc", "Le fer", "Le plomb"], "rep": "Le zinc"},
                    {"id": "mC2", "q": "Quel métal est préservé de la corrosion grâce à cette méthode ?", "options": ["Le fer (acier)", "Le zinc", "L'aluminium"], "rep": "Le fer (acier)"},
                    {"id": "mC3", "q": "Qui est l'oxydant de l'eau que le zinc doit neutraliser ?", "options": ["Le dioxygène", "Le diazote", "L'ion zinc"], "rep": "Le dioxygène"},
                    {"id": "mC4", "q": "Combien d'électrons un atome de zinc libère-t-il en s'oxydant en ion Zn²⁺ ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "mC5", "q": "Quelle est la couleur d'origine du bloc de zinc protecteur sain ?", "options": ["Gris mat / bleuté", "Rouge cuivre", "Jaune"], "rep": "Gris mat / bleuté"},
                    {"id": "mC6", "q": "Quel nom donne-t-on à cette méthode de préservation des métaux ?", "options": ["Protection sacrificielle", "Passivation acide", "Vernis étanche"], "rep": "Protection sacrificielle"},
                    {"id": "mC7", "q": "Pourquoi le zinc réagit-il à la place du fer de la cuve ?", "options": ["Il est plus réducteur que le fer", "Il est plus noble", "Il est plus lourd"], "rep": "Il est plus réducteur que le fer"},
                    {"id": "mC8", "q": "Quelle transformation subit le zinc en fournissant ses électrons ?", "options": ["Une oxydation", "Une réduction", "Une fusion"], "rep": "Une oxydation"},
                    {"id": "mC9", "q": "La captation des électrons mobiles par le dioxygène constitue une :", "options": ["Réduction", "Oxydation", "Liquéfaction"], "rep": "Réduction"},
                    {"id": "mC10", "q": "En s'oxydant, l'atome de zinc solide produit des ions :", "options": ["Zn²⁺", "Fe²⁺", "Cl⁻"], "rep": "Zn²⁺"}
                ],
                "trous": [
                    ("1. Le zinc de la pastille cède ses électrons, c'est le .......... du système.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_mC1"),
                    ("2. Le dioxygène capte ces électrons au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_mC2"),
                    ("3. Le zinc s'use lentement pour assurer une protection ..........", ["Choisir...", "sacrificielle", "mécanique"], "sacrificielle", "t_mC3"),
                    ("4. Chaque atome de zinc sacrifie un total de .......... électrons.", ["Choisir...", "deux", "trois"], "deux", "t_mC4"),
                    ("5. Grâce au zinc, la cuve centrale en acier conserve sa couleur ..........", ["Choisir...", "grise", "orange"], "grise", "t_mC5"),
                    ("6. L'atome de zinc solide se transforme en un .......... soluble Zn²⁺.", ["Choisir...", "ion", "gaz"], "ion", "t_mC6"),
                    ("7. L'eau industrielle du réservoir joue le rôle d'un .......... conducteur.", ["Choisir...", "électrolyte", "isolant"], "électrolyte", "t_mC7"),
                    ("8. Le potentiel E0 du zinc est plus bas, il est plus .......... que le fer.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_rC8"),
                    ("9. Le dioxygène se réduit en produisant des molécules d'..........", ["Choisir...", "eau", "zinc"], "eau", "t_mC9"),
                    ("10. L'absence d'électrons libres caractérise l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_mC10")
                ]
            }
        }

    # =============================================================================
    # INITIALISATION ET SÉLECTION DU CAS ACTIF DE MAINTENANCE
    # =============================================================================
    if "choix_id_maint" not in st.session_state:
        st.session_state.choix_id_maint = "maint_cas1"

    id_cas_maint = st.session_state.choix_id_maint
    cas_maint = st.session_state.banque_complete_maint[id_cas_maint]

    if f"quiz_melange_{id_cas_maint}" not in st.session_state:
        liste_q_maint = list(cas_maint["quiz"])
        random.shuffle(liste_q_maint)
        st.session_state[f"quiz_melange_{id_cas_maint}"] = liste_q_maint

    questions_maint_optimales = st.session_state[f"quiz_melange_{id_cas_maint}"]

    # =============================================================================
    # BOUTON DE GÉNÉRATION D'EXERCICE ALÉATOIRE FORCÉ
    # =============================================================================
    col_btn_maint, _ = st.columns([0.3, 0.7])
    with col_btn_maint:
        if st.button(
            "GÉNÉRER UN EXERCICE AU HASARD",
            key="btn_generer_exercice_aleatoire_t8",
            use_container_width=True,
        ):
            options_maint = ["maint_cas1", "maint_cas2", "maint_cas3"]
            cas_en_cours = st.session_state.choix_id_maint

            # Filtrage pour forcer un changement d'exercice réel
            choix_restants = [c for c in options_maint if c != cas_en_cours]
            st.session_state.choix_id_maint = random.choice(choix_restants)

            # Réinitialisation complète des validations et formulaires
            st.session_state.verrou_maint_bilan = False
            st.session_state.verrou_maint_at = False
            st.session_state.suite_verrouille_tab8_maint = False

            if "score_maint_partie_bilan" in st.session_state:
                del st.session_state["score_maint_partie_bilan"]
            st.rerun()

    st.write("---")

    # =============================================================================
    # AFFICHAGE DE L'ÉNONCÉ ET DE L'IMAGE TECHNIQUE DU CAS ACTIF
    # =============================================================================
    st.subheader(cas_maint["titre"])
    st.write(cas_maint["texte"])

    image_maint = f"{id_cas_maint}.jpg"
    if os.path.exists(image_maint):
        st.image(
            image_maint,
            caption="Constat d'anomalie sur le réseau de maintenance",
        )
    else:
        st.warning(
            f"L'image '{image_maint}' est introuvable à la racine de l'application."
        )

    st.divider()

    # =============================================================================
    # RENDU DE LA CARICATURE (DOUBLE COLONNE : TEXTE BLEU + IMAGE)
    # =============================================================================
    col_g_maint, col_b_maint = st.columns(2)
    with col_g_maint:
        st.write("**La BD humoristique textuelle adaptée à votre situation**")
        st.info(cas_maint["bd"])
    with col_b_maint:
        image_bd_maint = f"bd_{id_cas_maint}.jpg"
        if os.path.exists(image_bd_maint):
            st.image(
                image_bd_maint,
                caption="Illustration caricaturale du mécanisme",
                use_container_width=True,
            )
        else:
            st.warning(f"L'image '{image_bd_maint}' est introuvable.")

    st.divider()

    st.subheader("Générateur d'équation bilan de maintenance (Note sur 10 points)")
    st.write("Sélectionnez les bons éléments et équilibrez l'équation globale par rapport à votre énoncé :")

    if "verrou_maint_bilan" not in st.session_state:
        st.session_state.verrou_maint_bilan = False
    v_maint = st.session_state.verrou_maint_bilan

    # Ligne de sélection des couples et des demi-équations
    col_mb1, col_mb2 = st.columns(2)
    with col_mb1:
        choix_m_ox = st.selectbox("Sélectionnez le couple de l'oxydant :", ["Choisir...", "O2 / H2O", "H3O⁺ / H2", "Fe²⁺ / Fe"], disabled=v_maint, key="m_ox_sel")
        choix_m_demi_ox = st.selectbox("Sélectionnez la bonne écriture de l'oxydation :", ["Choisir...", "Fe -> Fe²⁺ + 2e⁻", "Zn -> Zn²⁺ + 2e⁻", "2H2O -> O2 + 4H3O⁺ + 4e⁻"], disabled=v_maint, key="m_demi_ox_sel")
    with col_mb2:
        choix_m_red = st.selectbox("Sélectionnez le couple du réducteur :", ["Choisir...", "Fe²⁺ / Fe", "Zn²⁺ / Zn", "O2 / H2O"], disabled=v_maint, key="m_red_sel")
        choix_m_demi_red = st.selectbox("Sélectionnez la bonne écriture de la réduction :", ["Choisir...", "O2 + 4H3O⁺ + 4e⁻ -> 6H2O", "2H3O⁺ + 2e⁻ -> H2 + 2H2O", "Fe²⁺ + 2e⁻ -> Fe"], disabled=v_maint, key="m_demi_red_sel")

    # Alignement parfait pour la construction stœchiométrique
    st.markdown("**Équilibrez l'équation bilan globale finale :**")
    col_me1, col_me2, col_me3, col_me4, col_me5, col_me6, col_me7 = st.columns([0.15, 0.25, 0.05, 0.25, 0.05, 0.25, 0.25], vertical_alignment="center")
    with col_me1: m_coef_1 = st.selectbox("Coef", ["Choisir...", "1", "2"], key="mc1", disabled=v_maint)
    with col_me2: m_reactif_1 = st.selectbox("Réactif 1", ["Choisir...", "Fe", "Zn", "O2"], key="mr1", disabled=v_maint)
    with col_me3: st.write("**+**")
    with col_me4: m_reactif_2 = st.selectbox("Réactif 2", ["Choisir...", "O2", "H3O⁺", "H2O"], key="mr2", disabled=v_maint)
    with col_me5: st.write("**→**")
    with col_me6: m_prod_1 = st.selectbox("Produit 1", ["Choisir...", "Fe²⁺", "Zn²⁺", "H2"], key="mp1", disabled=v_maint)
    with col_me7: m_prod_2 = st.selectbox("Produit 2", ["Choisir...", "H2O", "H2", "Fe²⁺"], key="mp2", disabled=v_maint)

    if st.button("VALIDER L'ÉQUATION BILAN [10 PTS]", key="btn_v_mb_maint", disabled=v_maint):
        if choix_m_ox == "Choisir..." or choix_m_red == "Choisir..." or m_reactif_1 == "Choisir..." or m_reactif_2 == "Choisir...":
            st.error("Action refusée : Veuillez remplir tous les choix.")
        else:
            m_score = 0.0
            if choix_m_ox == cas_maint["couple_ox"]: m_score += 2.0
            if choix_m_red == cas_maint["couple_red"]: m_score += 2.0

            # Vérification par rapport au cas de maintenance tiré au sort
            if id_cas_maint == "maint_cas1" and m_coef_1 == "2" and m_reactif_1 == "Fe" and m_reactif_2 == "O2" and m_prod_1 == "Fe²⁺" and m_prod_2 == "H2O":
                m_score += 6.0
            elif id_cas_maint == "maint_cas2" and m_coef_1 == "1" and m_reactif_1 == "Fe" and m_reactif_2 == "H3O⁺" and m_prod_1 == "Fe²⁺" and m_prod_2 == "H2":
                m_score += 6.0
            elif id_cas_maint == "maint_cas3" and m_coef_1 == "2" and m_reactif_1 == "Zn" and m_reactif_2 == "O2" and m_prod_1 == "Zn²⁺" and m_prod_2 == "H2O":
                m_score += 6.0

            st.session_state.score_maint_partie_bilan = m_score
            st.session_state.verrou_maint_bilan = True
            st.rerun()

    if st.session_state.get("verrou_maint_bilan"):
        st.info(f"Note enregistrée pour l'équation bilan : {st.session_state.get('score_maint_partie_bilan', 0.0)} / 10")

    st.divider()


    if "verrou_maint_at" not in st.session_state:
        st.session_state.verrou_maint_at = False
    v_maint_at = st.session_state.verrou_maint_at

    col_mq, col_mt = st.columns(2)

    with col_mq:
        st.markdown("##### Quiz Technique Maintenance (10 questions - 10 pts)")
        for idx, q_data in enumerate(questions_maint_optimales, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                label=q_data["q"],
                options=["Choisir..."] + q_data["options"],
                key=f"maint_quiz_{q_data['id']}",
                disabled=v_maint_at,
                label_visibility="collapsed"
            )

    with col_mt:
        st.markdown("##### Synthèse de la Conduite à trous (10 cases - 10 pts)")
        for ligne in cas_maint["trous"]:
            enonce, choix, attendu, cle = ligne

            # Correctif d'alignement parfait sur deux blocs
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="center")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    label=enonce,
                    options=choix,
                    key=f"{cle}_maint_clean",
                    disabled=v_maint_at,
                    label_visibility="collapsed"
                )
    if "suite_verrouille_tab8_maint" not in st.session_state:
        st.session_state.suite_verrouille_tab8_maint = False
    verrou_at8 = st.session_state.suite_verrouille_tab8_maint

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 8")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat8 = st.checkbox(
        "Je certifie avoir complété toutes les activités de cet Atelier Maintenance (Bilan et Questionnaire).",
        key="check_certif_maint8_scelle_ajuste",
        disabled=verrou_at8,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8",
        key="btn_exp_t8_final_official_ajuste",
        disabled=verrou_at8,
        use_container_width=True,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not st.session_state.get("verrou_maint_bilan", False):
            st.error("Action refusée : Vous devez valider l'Équation Bilan ci-dessus au préalable.")
        elif not case_certif_stat8:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Note du Générateur d'Équation Bilan (sur 10 pts)
            note_b_maint = float(st.session_state.get("score_maint_partie_bilan", 0.0))

            # 2. Correction automatisée du Quiz Technique (10 pts)
            score_q8 = 0.0
            for q in questions_maint_optimales:
                saisie_q = st.session_state.get(f"maint_quiz_{q['id']}", "Choisir...")
                if str(saisie_q).strip() == str(q["rep"]).strip():
                    score_q8 += 1.0

            # 3. CORRECTION OPTIMISÉE : Comparaison directe avec la variable textuelle 'attendu_t'
            score_t8 = 0.0
            for t in cas_maint["trous"]:
                enonce_t, choix_t, attendu_t, cle_t = t  # Déballage propre des 4 éléments du tuple
                saisie_t = st.session_state.get(f"{cle_t}_maint_clean", "Choisir...")
                if str(saisie_t).strip() == str(attendu_t).strip():
                    score_t8 += 1.0

            # 4. Enregistrement des notes globales de session sur 30 points
            st.session_state.score_t8_bilan_final = round(note_b_maint, 1)
            st.session_state.score_t8_atelier_final = round(float(score_q8 + score_t8), 1)
            st.session_state.score_final_global_t8 = round(float(note_b_maint + score_q8 + score_t8), 1)
            st.session_state.suite_verrouille_tab8_maint = True
            st.rerun()

    # --- COMPILATION DU RAPPORT INDIVIDUEL SCELLÉ HTML POUR LA MAINTENANCE ---
    if st.session_state.get("suite_verrouille_tab8_maint", False):
        not_b_m = st.session_state.get("score_t8_bilan_final", 0.0)
        not_at_m = st.session_state.get("score_t8_atelier_final", 0.0)
        not_tot_m = st.session_state.get("score_final_global_t8", 0.0)
        timestamp_suite8 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MAINTENANCE SCELLÉ | Note globale enregistrée : {not_tot_m:.1f} / 30")

        equation_eleve_maint_texte = f"{m_coef_1} {m_reactif_1} + {m_reactif_2} -> {m_prod_1} + {m_prod_2}"
        bd_html_maint_format = cas_maint["bd"].replace("\n\n", "<br><br>")

        html_export_maint = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Maintenance - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b91c1c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #2563eb; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                .enonce-box {{ background-color: #f1f5f9; border-left: 4px solid #b91c1c; padding: 15px; margin-bottom: 20px; font-size: 13px; line-height: 1.5; }}
                .bd-box {{ background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 20px; font-size: 13px; font-style: italic; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Individuel Officiel</h1>
                <p>Filière professionnelle : Maintenance Industrielle et Réseaux</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite8}</p>
                <div class="score-badge">SCORE FINAL<br><span style="font-size: 32px;">{not_tot_m:.1f}</span> / 30</div>
            </div>
            
            <div class="sub-title">Énoncé de l'étude de cas évaluée</div>
            <div class="enonce-box">
                <strong>{cas_maint['titre']}</strong><br><br>
                {cas_maint['texte']}
            </div>

            <div class="sub-title">La Caricature Pédagogique Associée</div>
            <div class="bd-box">
                {bd_html_maint_format}
            </div>

            <div class="sub-title">Synthèse des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                1. Équation Bilan de Diagnostic : <strong>{not_b_m:.1f} / 10</strong><br>
                2. Questionnaire Technique de Synthèse (Quiz + Trous) : <strong>{not_at_m:.1f} / 20</strong><br>
                <strong>Note totale consolidée : {not_tot_m:.1f} / 30</strong>
            </p>

            <div class="sub-title">Activité 1 : Vérification de la configuration d'Équation Bilan</div>
            <table>
                <thead>
                    <tr><th>Paramètre d'Éléments</th><th>Saisie Réalisée Élève</th><th>Attendu Académique</th></tr>
                </thead>
                <tbody>
                    <tr><td>Couple de l'Oxydant sélectionné</td><td>{choix_m_ox}</td><td>{cas_maint['couple_ox']}</td></tr>
                    <tr><td>Couple du Réducteur sélectionné</td><td>{choix_m_red}</td><td>{cas_maint['couple_red']}</td></tr>
                    <tr><td>Équation globale équilibrée</td><td><code>{equation_eleve_maint_texte}</code></td><td>Validation par script automatique</td></tr>
                </tbody>
            </table>

            <div class="sub-title">Activité 2 : Correction détaillée du Quiz Technique (10 pts)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Technique Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(questions_maint_optimales, 1):
            saisie = st.session_state.get(f"maint_quiz_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_maint += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_maint += """
                </tbody>
            </table>
            
            <div class="sub-title">Activité 3 : Correction détaillée de la Synthèse à trous (10 pts)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, t_item in enumerate(cas_maint["trous"], 1):
            enonce_t, _, attendu_t, cle_t = t_item
            saisie_t = st.session_state.get(f"{cle_t}_maint_clean", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_maint += f"<tr><td>{num}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_maint += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Utilisation de la bibliothèque os pour nettoyer proprement le nom du fichier d'export
        nom_fichier_brut_maint = preparer_nom_fichier("Rapport_Application_Maintenance")
        nom_propre_html_t8 = os.path.basename(nom_fichier_brut_maint).replace(
            ".txt", ".html"
        )

        # Rendu du bouton de téléchargement officiel scellé
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel Maintenance (.html)",
            data=html_export_maint,
            file_name=nom_propre_html_t8,
            mime="text/html",
            key="download_btn_t8_final",
        )


with tab9:
    st.header("Application dans le domaine des travaux publics")

    # =============================================================================
    # 1. BANQUE DE DONNÉES DYNAMIQUE PAR CAS POUR LES TRAVAUX PUBLICS
    # =============================================================================
    if "banque_complete_tp" not in st.session_state:
        st.session_state.banque_complete_tp = {
            "tp_cas1": {
                "titre": " Carbonatation des armatures d'un pont en béton armé",
                "texte": "Le dioxyde de carbone de l'air s'infiltre dans les pores du béton. Le pH s'effondre, détruisant la couche de passivation du fer solide. Les armatures en fer s'oxydent au contact de l'eau et du dioxygène atmosphérique en ions fer II, ce qui fait éclater le béton sous l'effet de la poussée mécanique de la rouille.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Un chef de chantier en casque de protection inspecte le tablier d'un pont routier en béton armé. Des fissures courent le long de la structure. Il s'écrie : 'Alerte ! Le béton éclate de partout ! Les armatures gonflent en sous-sol !'.\n\n"
                    "**Case 2 :** Un ingénieur s'approche avec un burin, casse un morceau de béton et découvre le fer de renfort complètement transformé en gangue de rouille orange friable : 'La carbonatation a frappé ! Le béton a perdu son acidité protectrice !'.\n\n"
                    "**Case 3 :** À l'intérieur du matériau, les atomes de fer sont attaqués par l'oxygène et l'humidité infiltrés. Ils hurlent en perdant leur cohésion : 'L'eau conduit trop bien les charges ! On perd nos électrons de valence pour devenir des ions solubles !'.\n\n"
                    "**Case 4 :** Le fer métallique s'est oxydé en ions Fe²⁺ et a gonflé sous forme de rouille, brisant les liaisons du ciment. L'ingénieur prépare un mortier de réparation à haute densité : 'On stoppe les infiltrations !'."
                ),
                "quiz": [
                    {"id": "tpA1", "q": "Qui est le réducteur métallique de départ qui se détériore dans le béton du pont ?", "options": ["Le fer solide", "Le dioxygène", "Le dioxyde de carbone"], "rep": "Le fer solide"},
                    {"id": "tpA2", "q": "Qui est l'oxydant de l'air infiltré responsable de la dégradation des armatures ?", "options": ["Le dioxygène", "Le diazote", "Le calcaire"], "rep": "Le dioxygène"},
                    {"id": "tpA3", "q": "Combien d'électrons sont transférés par chaque atome de fer lors de cette oxydation ?", "options": ["2 électrons", "1 électron", "4 électrons"], "rep": "2 électrons"},
                    {"id": "tpA4", "q": "Combien d'électrons capte le dioxygène pour se réduire en milieu acide ?", "options": ["4 électrons", "2 électrons", "6 électrons"], "rep": "4 électrons"},
                    {"id": "tpA5", "q": "Quelle couleur prend le produit de corrosion friable qui fait éclater les structures ?", "options": ["Orange / Brun (Rouille)", "Bleu azur", "Jaune laiton"], "rep": "Orange / Brun (Rouille)"},
                    {"id": "tpA6", "q": "Quelle modification chimique du béton déclenche la perte de protection des armatures ?", "options": ["Une chute de pH (carbonatation)", "Une hausse de température", "Une évaporation de l'eau"], "rep": "Une chute de pH (carbonatation)"},
                    {"id": "tpA7", "q": "Quel type de milieu environnemental (humidité des pores) favorise cette dégradation ?", "options": ["Un milieu conducteur", "Un milieu isolant", "Un milieu totalement sec"], "rep": "Un milieu conducteur"},
                    {"id": "tpA8", "q": "La transformation subie par le fer solide (perte d'électrons) est une :", "options": ["Oxydation", "Réduction", "Précipitation"], "rep": "Oxydation"},
                    {"id": "tpA9", "q": "En perdant ses charges négatives, l'atome de fer des structures devient un :", "options": ["Cation Fe²⁺", "Anion Fe²⁻", "Atome neutre"], "rep": "Cation Fe²⁺"},
                    {"id": "tpA10", "q": "La transformation de l'oxydant qui capte les électrons s'appelle une :", "options": ["Réduction", "Oxydation", "Sublimation"], "rep": "Réduction"}
                ],
                "trous": [
                    ("1. Dans ce cas, le fer solide des armatures agit comme le ..........", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_tpA1"),
                    ("2. Le dioxygène infiltré capte les électrons au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_tpA2"),
                    ("3. Au cours de la dégradation, chaque atome de fer libère .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_tpA3"),
                    ("4. L'humidité dans les pores du béton constitue un milieu liquide ..........", ["Choisir...", "conducteur", "isolant"], "conducteur", "t_tpA4"),
                    ("5. La dégradation interne du fer produit de la .......... volumineuse.", ["Choisir...", "rouille", "calamine"], "rouille", "t_tpA5"),
                    ("6. L'atome métallique neutre se transforme en un .......... Fe²⁺ soluble.", ["Choisir...", "ion", "gaz"], "ion", "t_tpA6"),
                    ("7. L'éclat d'une armature en acier saine présente une teinte ..........", ["Choisir...", "grise", "brune"], "grise", "t_tpA7"),
                    ("8. Les électrons quittent la tôle pour équilibrer la charge du ..........", ["Choisir...", "bilan", "solvant"], "bilan", "t_tpA8"),
                    ("9. La réduction complète du dioxygène engendre des molécules d'..........", ["Choisir...", "eau", "gaz"], "eau", "t_tpA9"),
                    ("10. L'égalisation des charges élimine les électrons de l'.......... finale.", ["Choisir...", "équation", "atmosphère"], "équation", "t_tpA10")
                ]
            },
            "tp_cas2": {
                "titre": " Attaque par les eaux acides des fondations de soutènement",
                "texte": "Les fondations en acier d'un réseau de soutènement de tranchée sont immergées dans une nappe phréatique polluée par des rejets acides. Les ions hydronium H₃O⁺ attaquent directement le fer métallique des palplanches, provoquant sa dissolution corrosive sous forme d'ions Fe²⁺ et un dégagement continu de dihydrogène gazeux.",
                "couple_ox": "H3O⁺ / H2",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Un chef de chantier observe les palplanches en acier plantées dans une tranchée. Le sol de fondation est gorgé d'eaux d'infiltration industrielles très acides.\n\n"
                    "**Case 2 :** Les ions hydronium H₃O⁺ attaquent la base métallique des parois de soutènement : 'Le fer est à nu dans cette nappe phréatique ! À l'attaque, dérobons ses charges !'.\n\n"
                    "**Case 3 :** Les atomes de fer perdent leurs électrons de cohésion et se dissolvent : 'Au secours, l'acidité nous sature et nous oxyde en ions Fe²⁺ ! La base de nos fondations s'effrite !'.\n\n"
                    "**Case 4 :** En absorbant les électrons, les ions hydronium se réduisent en gaz. Le terrassier s'étonne : 'Regardez toutes ces bulles de dihydrogène (H₂) qui s'échappent de la boue !'."
                ),
                "quiz": [
                    {"id": "tpB1", "q": "Qui est le réducteur métallique des fondations qui subit la dissolution acide ?", "options": ["Le fer solide", "L'ion hydronium", "Le gaz dihydrogène"], "rep": "Le fer solide"},
                    {"id": "tpB2", "q": "Qui est l'oxydant acide responsable de la destruction de la palplanche ?", "options": ["L'ion hydronium H₃O⁺", "Le fer solide", "L'eau neutre"], "rep": "L'ion hydronium H₃O⁺"},
                    {"id": "tpB3", "q": "Quel gaz inflammable se dégage sous forme de bulles au fond de la fouille ?", "options": ["Le dihydrogène", "Le dioxygène", "Le diazote"], "rep": "Le dihydrogène"},
                    {"id": "tpB4", "q": "Combien d'électrons cède un atome de fer lors de cette attaque acide ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "tpB5", "q": "Quel type de milieu chimique (pH inférieur à 7) caractérise cette eau d'infiltration ?", "options": ["Un milieu acide", "Un milieu basique", "Un milieu neutre"], "rep": "Un milieu acide"},
                    {"id": "tpB6", "q": "Quelle est la couleur de la palplanche d'acier intacte avant l'immersion ?", "options": ["Gris métallique", "Rouge rouille", "Jaune"], "rep": "Gris métallique"},
                    {"id": "tpB7", "q": "Que subit le matériau métallique lors de sa transformation en ions Fe²⁺ ?", "options": ["Une oxydation", "Une réduction", "Une évaporation"], "rep": "Une oxydation"},
                    {"id": "tpB8", "q": "La transformation de l'ion hydronium en gaz dihydrogène constitue une :", "options": ["Réduction", "Oxydation", "Combustion"], "rep": "Réduction"},
                    {"id": "tpB9", "q": "En s'oxydant, l'atome de fer solide des Travaux Publics devient un ion de charge :", "options": ["Positive (Fe²⁺)", "Négative (Fe²⁻)", "Neutre"], "rep": "Positive (Fe²⁺)"},
                    {"id": "tpB10", "q": "L'égalisation des charges impose d'établir une équation dite :", "options": ["Bilan globale", "Partielle d'oxydation", "D'isomérisation"], "rep": "Bilan globale"}
                ],
                "trous": [
                    ("1. La paroi en fer de la fondation subit une .......... destructrice.", ["Choisir...", "oxydation", "réduction"], "oxydation", "t_tpB1"),
                    ("2. Les ions hydronium de la solution marécageuse subissent une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_tpB2"),
                    ("3. Le fer métallique joue le rôle de .......... dans cette réaction de terrain.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_tpB3"),
                    ("4. L'agression chimique des palplanches provient d'un fluide de nature ..........", ["Choisir...", "acide", "basique"], "acide", "t_tpB4"),
                    ("5. La réduction des protons de l'acide génère un dégagement de ..........", ["Choisir...", "dihydrogène", "dioxygène"], "dihydrogène", "t_tpB5"),
                    ("6. Chaque atome de fer transfère à l'environnement un total de .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_tpB6"),
                    ("7. L'acier sain non altéré présente une couleur métallique ..........", ["Choisir...", "grise", "orange"], "grise", "t_tpB7"),
                    ("8. Le fer solide détruit passe en solution sous forme d'.......... Fe²⁺.", ["Choisir...", "ion", "solide"], "ion", "t_tpB8"),
                    ("9. Les électrons quittent le jalon de visée pour réduire l'..........", ["Choisir...", "acide", "sel"], "acide", "t_tpB9"),
                    ("10. Le croisement des charges électriques permet d'écrire l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_tpB10")
                ]
            },
            "tp_cas3": {
                "titre": " Galvanisation des structures métalliques de pylônes",
                "texte": "Pour protéger les structures de soutènement contre les intempéries agressives, les ingénieurs des travaux publics réalisent une galvanisation au zinc. En cas de rayure profonde, le zinc métallique s'oxyde préférentiellement pour bloquer la réduction de l'oxygène, agissant comme une anode sacrificielle.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Zn²⁺ / Zn",
                "bd": (
                    "**Case 1 :** Un chef de chantier inspecte les pylônes de soutènement en acier d'un pont suspendu. Malgré les embruns, la base reste intacte : 'Excellent, la structure ne montre aucune trace de rouille !'.\n\n"
                    "**Case 2 :** Une rayure profonde entaille le revêtement. Le zinc de galvanisation s'interpose devant l'acier : 'Pas touche au fer ! C'est moi le plus réducteur ici, j'envoie mes électrons !'.\n\n"
                    "**Case 3 :** Le zinc subit une oxydation et se dissout lentement : 'Je perds mes électrons de surface et je deviens l'ion Zn²⁺, je me sacrifie pour préserver l'ouvrage d'art !'.\n\n"
                    "**Case 4 :** L'acier du pylône reste parfaitement gris et robuste, tandis que le dioxygène est réduit de façon inoffensive. Les ingénieurs valident : 'La protection sacrificielle a fonctionné !'."
                ),
                "quiz": [
                    {"id": "tpC1", "q": "Quel métal se sacrifie et joue le rôle de réducteur actif pour protéger le pylône ?", "options": ["Le zinc", "Le fer", "Le plomb"], "rep": "Le zinc"},
                    {"id": "tpC2", "q": "Quel métal est préservé de la corrosion destructrice grâce à cette méthode ?", "options": ["Le fer (acier)", "Le zinc", "L'aluminium"], "rep": "Le fer (acier)"},
                    {"id": "tpC3", "q": "Qui est l'oxydant de l'air humide que le zinc de galvanisation doit neutraliser ?", "options": ["Le dioxygène", "Le diazote", "L'ion zinc"], "rep": "Le dioxygène"},
                    {"id": "tpC4", "q": "Combien d'électrons un atome de zinc libère-t-il en s'oxydant en ion Zn²⁺ ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "tpC5", "q": "Quelle est la couleur d'origine de la couche de zinc de galvanisation saine ?", "options": ["Gris mat / bleuté", "Rouge cuivre", "Jaune"], "rep": "Gris mat / bleuté"},
                    {"id": "tpC6", "q": "Quel nom donne-t-on à cette méthode de préservation des métaux ?", "options": ["Protection sacrificielle", "Passivation acide", "Vernis étanche"], "rep": "Protection sacrificielle"},
                    {"id": "tpC7", "q": "Pourquoi le zinc réagit-il à la place du fer de la structure du pylône ?", "options": ["Il est plus réducteur que le fer", "Il est plus noble", "Il est plus lourd"], "rep": "Il est plus réducteur que le fer"},
                    {"id": "tpC8", "q": "Quelle transformation subit le zinc en fournissant ses électrons de valence ?", "options": ["Une oxydation", "Une réduction", "Une fusion"], "rep": "Une oxydation"},
                    {"id": "tpC9", "q": "La captation des électrons mobiles par le dioxygène constitue une :", "options": ["Réduction", "Oxydation", "Liquéfaction"], "rep": "Réduction"},
                    {"id": "tpC10", "q": "En s'oxydant, la couche métallique de zinc produit des ions de formule :", "options": ["Zn²⁺", "Fe²⁺", "Cl⁻"], "rep": "Zn²⁺"}
                ],
                "trous": [
                    ("1. Le zinc de galvanisation cède ses électrons, c'est le .......... du système.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_tpC1"),
                    ("2. Le dioxygène capte ces électrons au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_tpC2"),
                    ("3. Le zinc s'use lentement pour assurer une protection ..........", ["Choisir...", "sacrificielle", "mécanique"], "sacrificielle", "t_tpC3"),
                    ("4. Chaque atome de zinc sacrifie un total de .......... électrons.", ["Choisir...", "deux", "trois"], "deux", "t_tpC4"),
                    ("5. Grâce au zinc, l'acier sous-jacent conserve sa couleur ..........", ["Choisir...", "grise", "orange"], "grise", "t_tpC5"),
                    ("6. L'atome de zinc solide se transforme en un .......... soluble Zn²⁺.", ["Choisir...", "ion", "gaz"], "ion", "t_tpC6"),
                    ("7. L'humidité atmosphérique ou les embruns jouent le rôle d'un .......... conducteur.", ["Choisir...", "électrolyte", "isolant"], "électrolyte", "t_tpC7"),
                    ("8. Le potentiel E0 du zinc est plus bas, il est plus .......... que le fer.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_tpC8"),
                    ("9. Le dioxygène se réduit en produisant des molécules d'..........", ["Choisir...", "eau", "zinc"], "eau", "t_tpC9"),
                    ("10. L'absence d'électrons libres caractérise l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_tpC10")
                ]
            }
        }

    # =============================================================================
    # INITIALISATION ET SÉLECTION DU CAS ACTIF DE TRAVAUX PUBLICS
    # =============================================================================
    if "choix_id_tp" not in st.session_state:
        st.session_state.choix_id_tp = "tp_cas1"

    id_cas_tp = st.session_state.choix_id_tp
    cas_tp = st.session_state.banque_complete_tp[id_cas_tp]
    if f"quiz_melange_{id_cas_tp}" not in st.session_state:
        liste_q_tp = list(cas_tp["quiz"])
        random.shuffle(liste_q_tp)
        st.session_state[f"quiz_melange_{id_cas_tp}"] = liste_q_tp

    questions_tp_optimales = st.session_state[f"quiz_melange_{id_cas_tp}"]

    # =============================================================================
    # BOUTON DE GÉNÉRATION D'EXERCICE ALÉATOIRE FORCÉ
    # =============================================================================
    col_btn_tp, _ = st.columns([0.3, 0.7])
    with col_btn_tp:
        if st.button(
            "GÉNÉRER UN EXERCICE AU HASARD",
            key="btn_generer_exercice_aleatoire_t9",
            use_container_width=True,
        ):
            options_tp = ["tp_cas1", "tp_cas2", "tp_cas3"]
            cas_en_cours = st.session_state.choix_id_tp

            # Filtrage pour forcer un changement d'exercice réel
            choix_restants = [c for c in options_tp if c != cas_en_cours]
            st.session_state.choix_id_tp = random.choice(choix_restants)

            # Réinitialisation complète des validations et formulaires
            st.session_state.verrou_tp_bilan = False
            st.session_state.verrou_tp_at = False
            st.session_state.suite_verrouille_tab9_tp = False

            if "score_tp_partie_bilan" in st.session_state:
                del st.session_state["score_tp_partie_bilan"]
            st.rerun()

    st.write("---")

    # =============================================================================
    # AFFICHAGE DE L'ÉNONCÉ ET DE L'IMAGE TECHNIQUE DU CAS ACTIF
    # =============================================================================
    st.subheader(cas_tp["titre"])
    st.write(cas_tp["texte"])

    image_tp = f"{id_cas_tp}.jpg"
    if os.path.exists(image_tp):
        st.image(
            image_tp,
            caption="Constat d'état des structures sur le chantier de travaux publics",
        )
    else:
        st.warning(
            f"L'image '{image_tp}' est introuvable à la racine de l'application."
        )

    st.divider()

    # =============================================================================
    # RENDU DE LA CARICATURE (DOUBLE COLONNE : TEXTE BLEU + IMAGE)
    # =============================================================================
    col_g_tp, col_b_tp = st.columns(2)
    with col_g_tp:
        st.write("**La BD humoristique textuelle adaptée à votre situation**")
        st.info(cas_tp["bd"])
    with col_b_tp:
        image_bd_tp = f"bd_{id_cas_tp}.jpg"
        if os.path.exists(image_bd_tp):
            st.image(
                image_bd_tp,
                caption="Illustration caricaturale du cas",
                use_container_width=True,
            )
        else:
            st.warning(f"L'image '{image_bd_tp}' est introuvable.")

    st.divider()
    st.subheader("Générateur d'équation bilan de travaux publics (Note sur 10 points)")
    st.write("Sélectionnez les bons éléments et équilibrez l'équation globale par rapport à l'énoncé :")

    if "verrou_tp_bilan" not in st.session_state:
        st.session_state.verrou_tp_bilan = False
    v_tp_bilan = st.session_state.verrou_tp_bilan

    # Ligne de sélection des couples et des demi-équations
    col_tpb1, col_tpb2 = st.columns(2)
    with col_tpb1:
        choix_tp_ox = st.selectbox("Sélectionnez le couple de l'oxydant :", ["Choisir...", "O2 / H2O", "H3O⁺ / H2", "Fe²⁺ / Fe"], disabled=v_tp_bilan, key="tp_ox_sel")
        choix_tp_demi_ox = st.selectbox("Sélectionnez la bonne écriture de l'oxydation :", ["Choisir...", "Fe -> Fe²⁺ + 2e⁻", "Zn -> Zn²⁺ + 2e⁻", "2H2O -> O2 + 4H3O⁺ + 4e⁻"], disabled=v_tp_bilan, key="tp_demi_ox_sel")
    with col_tpb2:
        choix_tp_red = st.selectbox("Sélectionnez le couple du réducteur :", ["Choisir...", "Fe²⁺ / Fe", "Zn²⁺ / Zn", "O2 / H2O"], disabled=v_tp_bilan, key="tp_red_sel")
        choix_tp_demi_red = st.selectbox("Sélectionnez la bonne écriture de la réduction :", ["Choisir...", "O2 + 4H3O⁺ + 4e⁻ -> 6H2O", "2H3O⁺ + 2e⁻ -> H2 + 2H2O", "Fe²⁺ + 2e⁻ -> Fe"], disabled=v_tp_bilan, key="tp_demi_red_sel")

    # Alignement parfait pour la construction stœchiométrique
    st.markdown("**Équilibrez l'équation bilan globale finale :**")
    col_tpe1, col_tpe2, col_tpe3, col_tpe4, col_tpe5, col_tpe6, col_tpe7 = st.columns([0.15, 0.25, 0.05, 0.25, 0.05, 0.25, 0.25], vertical_alignment="center")
    with col_tpe1: tp_coef_1 = st.selectbox("Coef", ["Choisir...", "1", "2"], key="tpc1", disabled=v_tp_bilan)
    with col_tpe2: tp_reactif_1 = st.selectbox("Réactif 1", ["Choisir...", "Fe", "Zn", "O2"], key="tpr1", disabled=v_tp_bilan)
    with col_tpe3: st.write("**+**")
    with col_tpe4: tp_reactif_2 = st.selectbox("Réactif 2", ["Choisir...", "O2", "H3O⁺", "H2O"], key="tpr2", disabled=v_tp_bilan)
    with col_tpe5: st.write("**→**")
    with col_tpe6: tp_prod_1 = st.selectbox("Produit 1", ["Choisir...", "Fe²⁺", "Zn²⁺", "H2"], key="tpp1", disabled=v_tp_bilan)
    with col_tpe7: tp_prod_2 = st.selectbox("Produit 2", ["Choisir...", "H2O", "H2", "Fe²⁺"], key="tpp2", disabled=v_tp_bilan)

    if st.button("VALIDER L'ÉQUATION BILAN [10 PTS]", key="btn_v_mb_tp", disabled=v_tp_bilan):
        if choix_tp_ox == "Choisir..." or choix_tp_red == "Choisir..." or tp_reactif_1 == "Choisir..." or tp_reactif_2 == "Choisir...":
            st.error("Action refusée : Veuillez remplir tous les choix.")
        else:
            tp_score = 0.0
            if choix_tp_ox == cas_tp["couple_ox"]: tp_score += 2.0
            if choix_tp_red == cas_tp["couple_red"]: tp_score += 2.0

            # Vérification par rapport au cas de travaux publics tiré au sort
            if id_cas_tp == "tp_cas1" and tp_coef_1 == "2" and tp_reactif_1 == "Fe" and tp_reactif_2 == "O2" and tp_prod_1 == "Fe²⁺" and tp_prod_2 == "H2O":
                tp_score += 6.0
            elif id_cas_tp == "tp_cas2" and tp_coef_1 == "1" and tp_reactif_1 == "Fe" and tp_reactif_2 == "H3O⁺" and tp_prod_1 == "Fe²⁺" and tp_prod_2 == "H2":
                tp_score += 6.0
            elif id_cas_tp == "tp_cas3" and tp_coef_1 == "2" and tp_reactif_1 == "Zn" and tp_reactif_2 == "O2" and tp_prod_1 == "Zn²⁺" and tp_prod_2 == "H2O":
                tp_score += 6.0

            st.session_state.score_tp_partie_bilan = tp_score
            st.session_state.verrou_tp_bilan = True
            st.rerun()

    if st.session_state.get("verrou_tp_bilan"):
        st.info(f"Note enregistrée pour l'équation bilan : {st.session_state.get('score_tp_partie_bilan', 0.0)} / 10")

    st.divider()
    if "verrou_tp_at" not in st.session_state:
        st.session_state.verrou_tp_at = False
    v_tp_at = st.session_state.verrou_tp_at

    col_tpq, col_tpt = st.columns(2)

    with col_tpq:
        st.markdown("##### Quiz Technique Ouvrage d'Art (10 questions - 10 pts)")
        for idx, q_data in enumerate(questions_tp_optimales, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                label=q_data["q"],
                options=["Choisir..."] + q_data["options"],
                key=f"tp_quiz_{q_data['id']}",
                disabled=v_tp_at,
                label_visibility="collapsed"
            )

    with col_tpt:
        st.markdown("##### Synthèse du Chantier à trous (10 cases - 10 pts)")
        for ligne in cas_tp["trous"]:
            enonce, choix, attendu, cle = ligne

            # Correctif d'alignement parfait sur deux blocs
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="center")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    label=enonce,
                    options=choix,
                    key=f"{cle}_tp_clean",
                    disabled=v_tp_at,
                    label_visibility="collapsed"
                )
    if "suite_verrouille_tab9_tp" not in st.session_state:
        st.session_state.suite_verrouille_tab9_tp = False
    verrou_at9 = st.session_state.suite_verrouille_tab9_tp

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 9")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat9 = st.checkbox(
        "Je certifie avoir complété toutes les activités de cet Atelier Travaux Publics (Bilan et Questionnaire).",
        key="check_certif_tp9_scelle_final",
        disabled=verrou_at9,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9",
        key="btn_exp_t9_final_official_ajuste",
        disabled=verrou_at9,
        use_container_width=True,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not st.session_state.get("verrou_tp_bilan", False):
            st.error("Action refusée : Vous devez valider l'Équation Bilan ci-dessus au préalable.")
        elif not case_certif_stat9:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Note du Générateur d'Équation Bilan (sur 10 pts)
            note_b_tp = float(st.session_state.get("score_tp_partie_bilan", 0.0))

            # 2. Correction automatisée du Quiz Technique (10 pts)
            score_q9 = 0.0
            for q in questions_tp_optimales:
                saisie_q = st.session_state.get(f"tp_quiz_{q['id']}", "Choisir...")
                if str(saisie_q).strip() == str(q["rep"]).strip():
                    score_q9 += 1.0

            # 3. CORRECTION OPTIMISÉE : Comparaison directe avec la variable textuelle 'attendu_t'
            score_t9 = 0.0
            for t in cas_tp["trous"]:
                enonce_t, choix_t, attendu_t, cle_t = t  # Déballage propre des 4 éléments
                saisie_t = st.session_state.get(f"{cle_t}_tp_clean", "Choisir...")
                if str(saisie_t).strip() == str(attendu_t).strip():
                    score_t9 += 1.0

            # 4. Enregistrement des notes globales de session sur 30 points
            st.session_state.score_tp_bilan_final = round(note_b_tp, 1)
            st.session_state.score_tp_atelier_final = round(float(score_q9 + score_t9), 1)
            st.session_state.score_final_global_tp = round(float(note_b_tp + score_q9 + score_t9), 1)
            st.session_state.suite_verrouille_tab9_tp = True
            st.rerun()
    # --- COMPILATION DU RAPPORT INDIVIDUEL SCELLÉ HTML POUR LES TP ---
    if st.session_state.get("suite_verrouille_tab9_tp", False):
        not_b_t = st.session_state.get("score_tp_bilan_final", 0.0)
        not_at_t = st.session_state.get("score_tp_atelier_final", 0.0)
        not_tot_t = st.session_state.get("score_final_global_tp", 0.0)
        timestamp_suite9 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRAVAUX PUBLICS SCELLÉ | Note globale enregistrée : {not_tot_t:.1f} / 30")

        equation_eleve_tp_texte = f"{tp_coef_1} {tp_reactif_1} + {tp_reactif_2} -> {tp_prod_1} + {tp_prod_2}"
        bd_html_tp_format = cas_tp["bd"].replace("\n\n", "<br><br>")

        html_export_tp = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Travaux Publics - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #2563eb; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                .enonce-box {{ background-color: #f1f5f9; border-left: 4px solid #0f172a; padding: 15px; margin-bottom: 20px; font-size: 13px; line-height: 1.5; }}
                .bd-box {{ background-color: #f8fafc; border-left: 4px solid #334155; padding: 15px; margin-bottom: 20px; font-size: 13px; font-style: italic; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Individuel Officiel</h1>
                <p>Filière professionnelle : Infrastructures et Travaux Publics</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite9}</p>
                <div class="score-badge">SCORE FINAL<br><span style="font-size: 32px;">{not_tot_t:.1f}</span> / 30</div>
            </div>
            
            <div class="sub-title">Énoncé de l'étude de cas évaluée</div>
            <div class="enonce-box">
                <strong>{cas_tp['titre']}</strong><br><br>
                {cas_tp['texte']}
            </div>

            <div class="sub-title">La Caricature Pédagogique Associée</div>
            <div class="bd-box">
                {bd_html_tp_format}
            </div>

            <div class="sub-title">Synthèse des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                1. Équation Bilan de Chantier : <strong>{not_b_t:.1f} / 10</strong><br>
                2. Questionnaire Technique de Synthèse (Quiz + Trous) : <strong>{not_at_t:.1f} / 20</strong><br>
                <strong>Note totale consolidée : {not_tot_t:.1f} / 30</strong>
            </p>

            <div class="sub-title">Activité 1 : Vérification de la configuration d'Équation Bilan</div>
            <table>
                <thead>
                    <tr><th>Paramètre d'Éléments</th><th>Saisie Réalisée Élève</th><th>Attendu Académique</th></tr>
                </thead>
                <tbody>
                    <tr><td>Couple de l'Oxydant sélectionné</td><td>{choix_tp_ox}</td><td>{cas_tp['couple_ox']}</td></tr>
                    <tr><td>Couple du Réducteur sélectionné</td><td>{choix_tp_red}</td><td>{cas_tp['couple_red']}</td></tr>
                    <tr><td>Équation globale équilibrée</td><td><code>{equation_eleve_tp_texte}</code></td><td>Validation par script automatique</td></tr>
                </tbody>
            </table>

            <div class="sub-title">Activité 2 : Correction détaillée du Quiz Technique (10 pts)</div>
            <table>
                <thead><tr><th>N°</th><th>Question Technique Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        for num, q_item in enumerate(questions_tp_optimales, 1):
            saisie = st.session_state.get(f"tp_quiz_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_tp += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tp += """
                </tbody>
            </table>
            
            <div class="sub-title">Activité 3 : Correction détaillée de la Synthèse à trous (10 pts)</div>
            <table>
                <thead><tr><th>N°</th><th>Phrase complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        for num, t_item in enumerate(cas_tp["trous"], 1):
            enonce_t, _, attendu_t, cle_t = t_item
            saisie_t = st.session_state.get(f"{cle_t}_tp_clean", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_tp += f"<tr><td>{num}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tp += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_brut_tp = preparer_nom_fichier("Rapport_Application_Travaux_Publics")
        nom_propre_html_t9 = os.path.basename(nom_fichier_brut_tp).replace(".txt", ".html")

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel Travaux Publics (.html)",
            data=html_export_tp,
            file_name=nom_propre_html_t9,
            mime="text/html",
            key="download_btn_t9_final",
        )

with tab10:
    st.header("Application dans le domaine des géomètres")

    # =============================================================================
    # 1. BANQUE DE DONNÉES DYNAMIQUE PAR CAS POUR LES GÉOMÈTRES
    # =============================================================================
    if "banque_complete_geo" not in st.session_state:
        st.session_state.banque_complete_geo = {
            "geo_cas1": {
                "titre": " Oxydation des repères topographiques métalliques en bronze",
                "texte": "Les géomètres installent des repères fixes en bronze scellés dans le sol pour le chaînage topographique. Exposé aux intempéries et à l'air humide, le cuivre contenu dans le bronze subit une oxydation progressive. Il cède ses électrons au dioxygène de l'air pour former une patine de carbonate de cuivre qui altère la lisibilité des gravures de précision.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Cu²⁺ / Cu",
                "bd": (
                    "**Case 1 :** Un géomètre installe son tachéomètre au-dessus d'un repère en bronze scellé dans une roche depuis des décennies. En regardant dans l'objectif, il plisse les yeux : 'Impossible de lire le point central, la gravure est complètement recouverte d'une couche verte !'.\n\n"
                    "**Case 2 :** Zoom sur le repère en bronze. L'humidité de l'air et le dioxygène entourent le métal. Les molécules d'oxygène s'approchent en souriant : 'Regardez-moi ce joli cuivre tout propre, c'est l'heure de lui soutirer ses charges de surface !'.\n\n"
                    "**Case 3 :** Les atomes de cuivre de surface cèdent deux électrons chacun et se détachent du bloc métallique : 'Aïe, nous subissons une oxydation en ions Cu²⁺ ! Notre éclat métallique brillant disparaît, on verdit à vue d'œil !'.\n\n"
                    "**Case 4 :** Le fer métallique s'est oxydé en ions Cu²⁺ et a verdi sous forme de vert-de-gris. Le géomètre sort une brosse métallique et un produit protecteur isolant pour nettoyer le repère : 'On protège la référence de nivellement !'."
                ),
                "quiz": [
                    {"id": "gA1", "q": "Qui est le réducteur de départ constitutif du repère qui subit l'altération ?", "options": ["Le cuivre solide", "Le dioxygène", "L'eau de pluie"], "rep": "Le cuivre solide"},
                    {"id": "gA2", "q": "Qui est l'oxydant de l'air humide responsable de l'oxydation du repère ?", "options": ["Le dioxygène", "Le diazote", "Le dioxyde de soufre"], "rep": "Le dioxygène"},
                    {"id": "gA3", "q": "Combien d'électrons sont transférés par chaque atome de cuivre lors de cette réaction ?", "options": ["2 électrons", "1 électron", "4 électrons"], "rep": "2 électrons"},
                    {"id": "gA4", "q": "Quelle couleur prend le produit d'oxydation (vert-de-gris) qui recouvre le repère ?", "options": ["Vert / Bleu clair", "Rouge brique", "Noir intense"], "rep": "Vert / Bleu clair"},
                    {"id": "gA5", "q": "Quelle est la couleur d'origine du métal cuivreux sain avant son altération ?", "options": ["Rouge orangé brillant", "Gris argenté", "Jaune vif"], "rep": "Rouge orangé brillant"},
                    {"id": "gA6", "q": "Quelle transformation subit le cuivre métallique lorsqu'il cède ses électrons ?", "options": ["Une oxydation", "Une réduction", "Une fusion"], "rep": "Une oxydation"},
                    {"id": "gA7", "q": "La captation des électrons par le dioxygène gazeux constitue une demi-réaction de :", "options": ["Réduction", "Oxydation", "Sublimation"], "rep": "Réduction"},
                    {"id": "gA8", "q": "En perdant ses charges négatives, l'atome de cuivre neutre devient un :", "options": ["Cation Cu²⁺", "Anion Cu²⁻", "Atome de fer"], "rep": "Cation Cu²⁺"},
                    {"id": "gA9", "q": "Quel type de milieu environnemental (humidité) favorise le transfert des électrons ?", "options": ["Un milieu conducteur", "Un milieu isolant", "Un milieu stérile"], "rep": "Un milieu conducteur"},
                    {"id": "gA10", "q": "Dans l'écriture universelle du couple, la forme s'écrit sous la configuration :", "options": ["Oxydant / Réducteur", "Réducteur / Oxydant", "Acide / Base"], "rep": "Oxydant / Réducteur"}
                ],
                "trous": [
                    ("1. Le cuivre solide constitutif du repère topographique agit comme le ..........", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_gA1"),
                    ("2. Le dioxygène gazeux capte les charges au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_gA2"),
                    ("3. Chaque atome de cuivre cède un nombre de .......... électrons de valence.", ["Choisir...", "deux", "quatre"], "deux", "t_gA3"),
                    ("4. La patine protectrice ou vert-de-gris présente une couleur ..........", ["Choisir...", "verte", "orange"], "verte", "t_gA4"),
                    ("5. Avant d'être oxydé par l'air, le cuivre pur possède une teinte ..........", ["Choisir...", "orangée", "grise"], "orangée", "t_gA5"),
                    ("6. L'atome de métal neutre se transforme en un .......... soluble Cu²⁺.", ["Choisir...", "ion", "gaz"], "ion", "t_gA6"),
                    ("7. L'humidité de l'air ambiant joue le rôle d'un fluide ..........", ["Choisir...", "conducteur", "isolant"], "conducteur", "t_gA7"),
                    ("8. Les électrons quittent le pôle métallique pour réduire le ..........", ["Choisir...", "gaz", "métal"], "gaz", "t_gA8"),
                    ("9. La réduction de l'oxydant produit des molécules d'..........", ["Choisir...", "eau", "cuivre"], "eau", "t_gA9"),
                    ("10. L'absence d'électrons libres caractérise l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_gA10")
                ]
            },
            "geo_cas2": {
                "titre": " Attaque acide des jalons d'arpentage en acier en zone marécageuse",
                "texte": "Lors de relevés de limites de propriété en milieu marécageux acide, les jalons de visée en acier entrent en contact avec des eaux stagnantes chargées d'ions hydronium H₃O⁺. Ce milieu agressif déclenche l'oxydation du fer de la tige, provoquant sa dissolution et un dégagement de dihydrogène.",
                "couple_ox": "H3O⁺ / H2",
                "couple_red": "Fe²⁺ / Fe",
                "bd": (
                    "**Case 1 :** Un géomètre-expert plante un jalon de visée métallique dans le sol humide d'un marécage pour délimiter une parcelle. Le terrain dégage une forte odeur de décomposition organique.\n\n"
                    "**Case 2 :** L'eau du marais est très acide. Les ions hydronium H₃O⁺ encerclent la pointe du jalon en acier : 'Hé regardez, le métal n'est pas protégé ici ! Volons-lui ses électrons !'.\n\n"
                    "**Case 3 :** Les atomes de fer perdent leurs électrons de cohésion et se dissolvent : 'Au secours, nous subissons une oxydation en ions Fe²⁺ ! La pointe de notre jalon est en train de se dissoudre dans la boue !'.\n\n"
                    "**Case 4 :** En absorbant les électrons du fer, les ions hydronium se transforment en gaz et s'échappent en bouillonnant. Le géomètre remarque de petites bulles de dihydrogène (H₂) remonter à la surface."
                ),
                "quiz": [
                    {"id": "gB1", "q": "Qui est le réducteur métallique qui subit la dissolution au fond du marais ?", "options": ["Le fer solide", "L'ion hydronium", "Le gaz dihydrogène"], "rep": "Le fer solide"},
                    {"id": "gB2", "q": "Qui est l'oxydant acide responsable de la destruction de la pointe du jalon ?", "options": ["L'ion hydronium H₃O⁺", "Le fer solide", "L'eau neutre"], "rep": "L'ion hydronium H₃O⁺"},
                    {"id": "gB3", "q": "Quel dégagement gazeux se produit suite à la réduction en milieu acide ?", "options": ["Le dihydrogène", "Le dioxygène", "Le diazote"], "rep": "Le dihydrogène"},
                    {"id": "gB4", "q": "Combien d'électrons un atome de fer cède-t-il lors de cette oxydation ?", "options": ["2 électrons", "1 électron", "4 électrons"], "rep": "2 électrons"},
                    {"id": "gB5", "q": "Quel type de milieu chimique (pH inférieur à 7) caractérise l'eau du marécage ?", "options": ["Un milieu acide", "Un milieu basique", "Un milieu neutre"], "rep": "Un milieu acide"},
                    {"id": "gB6", "q": "Quelle est la couleur de la tige de fer saine avant d'être plantée dans la boue ?", "options": ["Gris métallique", "Rouge", "Jaune"], "rep": "Gris métallique"},
                    {"id": "gB7", "q": "La transformation subie par le fer solide (perte d'électrons) constitue une :", "options": ["Oxydation", "Réduction", "Précipitation"], "rep": "Oxydation"},
                    {"id": "gB8", "q": "La capture des électrons par les ions hydronium constitue une :", "options": ["Réduction", "Oxydation", "Combustion"], "rep": "Réduction"},
                    {"id": "gB9", "q": "En s'oxydant, l'atome de fer solide des Travaux Publics devient un ion de charge :", "options": ["Positive (Fe²⁺)", "Négative (Fe²⁻)", "Neutre"], "rep": "Positive (Fe²⁺)"},
                    {"id": "gB10", "q": "L'égalisation des charges impose d'établir une équation dite :", "options": ["Bilan globale", "Partielle d'oxydation", "D'isomérisation"], "rep": "Bilan globale"}
                ],
                "trous": [
                    ("1. Le fer solide du jalon d'arpentage subit une .......... destructive.", ["Choisir...", "oxydation", "réduction"], "oxydation", "t_gB1"),
                    ("2. Les ions hydronium de la solution marécageuse subissent une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_gB2"),
                    ("3. Le fer métallique joue le rôle de .......... dans cette réaction de terrain.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_gB3"),
                    ("4. L'agression chimique des jalons provient d'un liquide de nature ..........", ["Choisir...", "acide", "basique"], "acide", "t_gB4"),
                    ("5. La réduction des protons de l'acide génère un dégagement de ..........", ["Choisir...", "dihydrogène", "dioxygène"], "dihydrogène", "t_gB5"),
                    ("6. Chaque atome de fer libère un total de .......... électrons.", ["Choisir...", "deux", "quatre"], "deux", "t_gB6"),
                    ("7. L'acier sain non altéré présente une couleur métallique ..........", ["Choisir...", "grise", "orange"], "grise", "t_gB7"),
                    ("8. Le fer solide détruit passe en solution sous forme d'.......... Fe²⁺.", ["Choisir...", "ion", "solide"], "ion", "t_gB8"),
                    ("9. Les électrons quittent le jalon de visée pour réduire l'..........", ["Choisir...", "acide", "sel"], "acide", "t_gB9"),
                    ("10. Le croisement des charges électriques permet d'écrire l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_gB10")
                ]
            },
            "geo_cas3": {
                "titre": " Protection cathodique des repères de niveau par pastilles de zinc",
                "texte": "Pour éviter le remplacement fréquent des repères métalliques fixés en extérieur, les géomètres utilisent des pastilles de zinc fixées à la base. En présence d'humidité saline, le zinc s'oxyde préférentiellement et protège le fer de la tige centrale par effet d'anode sacrificielle.",
                "couple_ox": "O2 / H2O",
                "couple_red": "Zn²⁺ / Zn",
                "bd": (
                    "**Case 1 :** Un géomètre vérifie un repère de haute précision fixé sur un mur extérieur en bord de mer. Le bloc est soumis aux embruns salés mais ne présente aucune trace de rouille.\n\n"
                    "**Case 2 :** L'eau salée s'infiltre. La pastille de zinc se place devant la tige d'acier : 'Pas de panique la structure, je suis plus réducteur que toi, j'envoie mes électrons en premier !'.\n\n"
                    "**Case 3 :** Le zinc subit une oxydation et se dissout lentement : 'Je perds mes électrons de surface et je deviens l'ion Zn²⁺, je me sacfifie pour préserver le nivellement !'.\n\n"
                    "**Case 4 :** L'acier de la tige centrale reste parfaitement gris et intact. Le géomètre valide la mesure : 'La protection sacrificielle fonctionne à merveille, le point zéro reste stable !'."
                ),
                "quiz": [
                    {"id": "gC1", "q": "Quel métal se sacrifie et joue le rôle de réducteur actif pour protéger le repère ?", "options": ["Le zinc", "Le fer", "Le plomb"], "rep": "Le zinc"},
                    {"id": "gC2", "q": "Quel métal est préservé de la corrosion grâce à cette méthode ?", "options": ["Le fer (acier)", "Le zinc", "Le cuivre"], "rep": "Le fer (acier)"},
                    {"id": "gC3", "q": "Qui est l'oxydant de l'air humide marin que le zinc doit neutraliser ?", "options": ["Le dioxygène", "Le diazote", "L'ion zinc"], "rep": "Le dioxygène"},
                    {"id": "gC4", "q": "Combien d'électrons un atome de zinc libère-t-on en s'oxydant en ion Zn²⁺ ?", "options": ["2 électrons", "1 électron", "3 électrons"], "rep": "2 électrons"},
                    {"id": "gC5", "q": "Quelle est la couleur d'origine de la pastille de zinc protectrice saine ?", "options": ["Gris mat", "Rouge orangé", "Jaune métallique"], "rep": "Gris mat"},
                    {"id": "gC6", "q": "Quel nom donne-t-on à cette méthode de préservation des métaux ?", "options": ["Protection sacrificielle", "Passivation acide", "Peinture étanche"], "rep": "Protection sacrificielle"},
                    {"id": "gC7", "q": "Pourquoi le zinc réagit-il à la place du fer de la tige de nivellement ?", "options": ["Il est plus réducteur que le fer", "Il est plus noble", "Il est plus dur"], "rep": "Il est plus réducteur que le fer"},
                    {"id": "gC8", "q": "Quelle transformation subit le zinc en fournissant ses électrons ?", "options": ["Une oxydation", "Une réduction", "Une fusion"], "rep": "Une oxydation"},
                    {"id": "gC9", "q": "La captation des électrons mobiles par le dioxygène de l'air constitue une :", "options": ["Réduction", "Oxydation", "Liquéfaction"], "rep": "Réduction"},
                    {"id": "gC10", "q": "En s'oxydant, la pastille métallique de zinc produit des ions de formule :", "options": ["Zn²⁺", "Fe²⁺", "Cu²⁺"], "rep": "Zn²⁺"}
                ],
                "trous": [
                    ("1. Le zinc de la pastille cède ses électrons, c'est le .......... du système.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_gC1"),
                    ("2. Le dioxygène capte ces électrons au cours d'une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "t_gC2"),
                    ("3. Le zinc s'use lentement pour assurer une protection ..........", ["Choisir...", "sacrificielle", "mécanique"], "sacrificielle", "t_gC3"),
                    ("4. Chaque atome de zinc sacrifie un total de .......... électrons.", ["Choisir...", "deux", "trois"], "deux", "t_gC4"),
                    ("5. Grâce au zinc, la tige centrale en acier conserve sa couleur ..........", ["Choisir...", "grise", "orange"], "grise", "t_gC5"),
                    ("6. L'atome de zinc solide se transforme en un .......... soluble Zn²⁺.", ["Choisir...", "ion", "gaz"], "ion", "t_gC6"),
                    ("7. L'humidité saline des embruns joue le rôle d'un .......... conducteur.", ["Choisir...", "électrolyte", "isolant"], "électrolyte", "t_gC7"),
                    ("8. Le potentiel E0 du zinc est plus bas, il est plus .......... que le fer.", ["Choisir...", "réducteur", "oxydant"], "réducteur", "t_gB8"),
                    ("9. Le dioxygène se réduit en produisant des molécules d'..........", ["Choisir...", "eau", "zinc"], "eau", "t_gC9"),
                    ("10. L'absence d'électrons libres caractérise l'équation ..........", ["Choisir...", "bilan", "partielle"], "bilan", "t_gC10")
                ]
            }
        }

    # =============================================================================
    # INITIALISATION ET SÉLECTION DU CAS ACTIF POUR LES GÉOMÈTRES
    # =============================================================================
    if "choix_id_geo" not in st.session_state:
        st.session_state.choix_id_geo = "geo_cas1"

    id_cas_geo = st.session_state.choix_id_geo
    cas_geo = st.session_state.banque_complete_geo[id_cas_geo]

    if f"quiz_melange_{id_cas_geo}" not in st.session_state:
        liste_q_geo = list(cas_geo["quiz"])
        random.shuffle(liste_q_geo)
        st.session_state[f"quiz_melange_{id_cas_geo}"] = liste_q_geo

    questions_geo_optimales = st.session_state[f"quiz_melange_{id_cas_geo}"]

    # =============================================================================
    # BOUTON DE GÉNÉRATION D'EXERCICE ALÉATOIRE FORCÉ
    # =============================================================================
    col_btn_geo, _ = st.columns([0.3, 0.7])
    with col_btn_geo:
        if st.button(
            "GÉNÉRER UN EXERCICE AU HASARD",
            key="btn_generer_exercice_aleatoire_t10",
            use_container_width=True,
        ):
            options_geo = ["geo_cas1", "geo_cas2", "geo_cas3"]
            cas_en_cours = st.session_state.choix_id_geo

            # Filtrage pour forcer un changement d'exercice réel
            choix_restants = [c for c in options_geo if c != cas_en_cours]
            st.session_state.choix_id_geo = random.choice(choix_restants)

            # Réinitialisation complète des validations et formulaires
            st.session_state.verrou_geo_bilan = False
            st.session_state.verrou_geo_at = False
            st.session_state.suite_verrouille_tab10_geo = False

            if "score_geo_partie_bilan" in st.session_state:
                del st.session_state["score_geo_partie_bilan"]
            st.rerun()

    st.write("---")

    # =============================================================================
    # AFFICHAGE DE L'ÉNONCÉ ET DE L'IMAGE TECHNIQUE DU CAS ACTIF
    # =============================================================================
    st.subheader(cas_geo["titre"])
    st.write(cas_geo["texte"])

    image_geo = f"{id_cas_geo}.jpg"
    if os.path.exists(image_geo):
        st.image(
            image_geo,
            caption="Constat d'état du matériel topographique sur le terrain",
        )
    else:
        st.warning(
            f"L'image '{image_geo}' est introuvable à la racine de l'application."
        )

    st.divider()

    # =============================================================================
    # RENDU DE LA CARICATURE (DOUBLE COLONNE : TEXTE BLEU + IMAGE)
    # =============================================================================
    col_g_geo, col_b_geo = st.columns(2)
    with col_g_geo:
        st.write("**La BD humoristique textuelle adaptée à votre situation**")
        st.info(cas_geo["bd"])
    with col_b_geo:
        image_bd_geo = f"bd_{id_cas_geo}.jpg"
        if os.path.exists(image_bd_geo):
            st.image(
                image_bd_geo,
                caption="Illustration caricaturale du cas",
                use_container_width=True,
            )
        else:
            st.warning(f"L'image '{image_bd_geo}' est introuvable.")

    st.divider()

    st.subheader("Générateur d'équation bilan du domaine des géomètres (Note sur 10 points)")
    st.write("Sélectionnez les bons éléments et équilibrez l'équation globale par rapport à votre énoncé :")

    if "verrou_geo_bilan" not in st.session_state:
        st.session_state.verrou_geo_bilan = False
    v_geo_bilan = st.session_state.verrou_geo_bilan

    # Ligne de sélection des couples et des demi-équations
    col_geob1, col_geob2 = st.columns(2)
    with col_geob1:
        choix_geo_ox = st.selectbox("Sélectionnez le couple de l'oxydant :", ["Choisir...", "O2 / H2O", "H3O⁺ / H2", "Fe²⁺ / Fe"], disabled=v_geo_bilan, key="geo_ox_sel")
        choix_geo_demi_ox = st.selectbox("Sélectionnez la bonne écriture de l'oxydation :", ["Choisir...", "Fe -> Fe²⁺ + 2e⁻", "Zn -> Zn²⁺ + 2e⁻", "Cu -> Cu²⁺ + 2e⁻"], disabled=v_geo_bilan, key="geo_demi_ox_sel")
    with col_geob2:
        choix_geo_red = st.selectbox("Sélectionnez le couple du réducteur :", ["Choisir...", "Fe²⁺ / Fe", "Zn²⁺ / Zn", "Cu²⁺ / Cu"], disabled=v_geo_bilan, key="geo_red_sel")
        choix_geo_demi_red = st.selectbox("Sélectionnez la bonne écriture de la réduction :", ["Choisir...", "O2 + 4H3O⁺ + 4e⁻ -> 6H2O", "2H3O⁺ + 2e⁻ -> H2 + 2H2O", "Cu²⁺ + 2e⁻ -> Cu"], disabled=v_geo_bilan, key="geo_demi_red_sel")

    # Alignement parfait pour la construction stœchiométrique
    st.markdown("**Équilibrez l'équation bilan globale finale :**")
    col_gee1, col_gee2, col_gee3, col_gee4, col_gee5, col_gee6, col_gee7 = st.columns([0.15, 0.25, 0.05, 0.25, 0.05, 0.25, 0.25], vertical_alignment="center")
    with col_gee1: geo_coef_1 = st.selectbox("Coef", ["Choisir...", "1", "2"], key="geoc1", disabled=v_geo_bilan)
    with col_gee2: geo_reactif_1 = st.selectbox("Réactif 1", ["Choisir...", "Fe", "Zn", "Cu", "O2"], key="geor1", disabled=v_geo_bilan)
    with col_gee3: st.write("**+**")
    with col_gee4: geo_reactif_2 = st.selectbox("Réactif 2", ["Choisir...", "O2", "H3O⁺", "H2O"], key="geor2", disabled=v_geo_bilan)
    with col_gee5: st.write("**→**")
    with col_gee6: geo_prod_1 = st.selectbox("Produit 1", ["Choisir...", "Fe²⁺", "Zn²⁺", "Cu²⁺", "H2"], key="geop1", disabled=v_geo_bilan)
    with col_gee7: geo_prod_2 = st.selectbox("Produit 2", ["Choisir...", "H2O", "H2", "Cu²⁺"], key="geop2", disabled=v_geo_bilan)

    if st.button("VALIDER L'ÉQUATION BILAN [10 PTS]", key="btn_v_mb_geo_final", disabled=v_geo_bilan):
        if choix_geo_ox == "Choisir..." or choix_geo_red == "Choisir..." or geo_reactif_1 == "Choisir..." or geo_reactif_2 == "Choisir...":
            st.error("Action refusée : Veuillez remplir tous les choix.")
        else:
            geo_score = 0.0
            if choix_geo_ox == cas_geo["couple_ox"]: geo_score += 2.0
            if choix_geo_red == cas_geo["couple_red"]: geo_score += 2.0

            # Vérification par rapport au cas de géomètres tiré au sort
            if id_cas_geo == "geo_cas1" and geo_coef_1 == "2" and geo_reactif_1 == "Cu" and geo_reactif_2 == "O2" and geo_prod_1 == "Cu²⁺" and geo_prod_2 == "H2O":
                geo_score += 6.0
            elif id_cas_geo == "geo_cas2" and geo_coef_1 == "1" and geo_reactif_1 == "Fe" and geo_reactif_2 == "H3O⁺" and geo_prod_1 == "Fe²⁺" and geo_prod_2 == "H2":
                geo_score += 6.0
            elif id_cas_geo == "geo_cas3" and geo_coef_1 == "2" and geo_reactif_1 == "Zn" and geo_reactif_2 == "O2" and geo_prod_1 == "Zn²⁺" and geo_prod_2 == "H2O":
                geo_score += 6.0

            st.session_state.score_geo_partie_bilan = geo_score
            st.session_state.verrou_geo_bilan = True
            st.rerun()

    if st.session_state.get("verrou_geo_bilan"):
        st.info(f"Note enregistrée pour l'équation bilan : {st.session_state.get('score_geo_partie_bilan', 0.0)} / 10")

    st.divider()
    if "verrou_geo_at" not in st.session_state:
        st.session_state.verrou_geo_at = False
    v_geo_at = st.session_state.verrou_geo_at

    col_geoq, col_geot = st.columns(2)

    with col_geoq:
        st.markdown("##### Quiz Technique Géomètres (10 questions - 10 pts)")
        for idx, q_data in enumerate(questions_geo_optimales, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                label=q_data["q"],
                options=["Choisir..."] + q_data["options"],
                key=f"geo_quiz_{q_data['id']}",
                disabled=v_geo_at,
                label_visibility="collapsed"
            )

    with col_geot:
        st.markdown("##### Synthèse Technique à trous (10 cases - 10 pts)")
        for ligne in cas_geo["trous"]:
            enonce, choix, attendu, cle = ligne

            # Correctif d'alignement parfait sur deux blocs
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="center")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    label=enonce,
                    options=choix,
                    key=f"{cle}_geo_clean",
                    disabled=v_geo_at,
                    label_visibility="collapsed"
                )

    if "suite_verrouille_tab10_geo" not in st.session_state:
        st.session_state.suite_verrouille_tab10_geo = False
    verrou_at10 = st.session_state.suite_verrouille_tab10_geo

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 10")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat10 = st.checkbox(
        "Je certifie avoir complété toutes les activités de cet Atelier Géomètres (Bilan et Questionnaire).",
        key="check_certif_geo10_scelle",
        disabled=verrou_at10,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 10",
        key="btn_exp_t10_final_official",
        disabled=verrou_at10,
        use_container_width=True,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not st.session_state.get("verrou_geo_bilan", False):
            st.error("Action refusée : Vous devez valider l'Équation Bilan ci-dessus au préalable.")
        elif not case_certif_stat10:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Note du Générateur d'Équation Bilan (sur 10 pts)
            note_b_geo = float(st.session_state.get("score_geo_partie_bilan", 0.0))

            # 2. Correction automatisée du Quiz Technique (10 pts)
            score_q10 = 0.0
            for q in questions_geo_optimales:
                saisie_q = st.session_state.get(f"geo_quiz_{q['id']}", "Choisir...")
                if str(saisie_q).strip() == str(q["rep"]).strip():
                    score_q10 += 1.0

            # 3. CORRECTION OPTIMISÉE : Comparaison directe avec la variable 'attendu'
            score_t10 = 0.0
            for t in cas_geo["trous"]:
                enonce_t, choix_t, attendu_t, cle_t = t  # Extraction propre des 4 éléments
                saisie_t = st.session_state.get(f"{cle_t}_geo_clean", "Choisir...")
                if str(saisie_t).strip() == str(attendu_t).strip():
                    score_t10 += 1.0

            # 4. Enregistrement des notes globales de session sur 30 points
            st.session_state.score_geo_bilan_final = round(note_b_geo, 1)
            st.session_state.score_geo_atelier_final = round(float(score_q10 + score_t10), 1)
            st.session_state.score_final_global_geo = round(float(note_b_geo + score_q10 + score_t10), 1)
            st.session_state.suite_verrouille_tab10_geo = True
            st.rerun()

    # --- COMPILATION DU RAPPORT INDIVIDUEL SCELLÉ HTML POUR LES GÉOMÈTRES ---
    if st.session_state.get("suite_verrouille_tab10_geo", False):
        not_b_g = st.session_state.get("score_geo_bilan_final", 0.0)
        not_at_g = st.session_state.get("score_geo_atelier_final", 0.0)
        not_tot_g = st.session_state.get("score_final_global_geo", 0.0)
        timestamp_suite10 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER GÉOMÈTRES SCELLÉ | Note globale enregistrée : {not_tot_g:.1f} / 30")

        equation_eleve_geo_texte = f"{geo_coef_1} {geo_reactif_1} + {geo_reactif_2} -> {geo_prod_1} + {geo_prod_2}"
        bd_html_geo_format = cas_geo["bd"].replace("\n\n", "<br><br>")

        html_export_geo = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Géomètres - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #10b981; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                .enonce-box {{ background-color: #f1f5f9; border-left: 4px solid #0f172a; padding: 15px; margin-bottom: 20px; font-size: 13px; line-height: 1.5; }}
                .bd-box {{ background-color: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; margin-bottom: 20px; font-size: 13px; font-style: italic; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Individuel Officiel</h1>
                <p>Filière professionnelle : Topographie et Géomètres-Experts</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite10}</p>
                <div class="score-badge">SCORE FINAL<br><span style="font-size: 32px;">{not_tot_g:.1f}</span> / 30</div>
            </div>
            
            <div class="sub-title">Énoncé de l'étude de cas évaluée</div>
            <div class="enonce-box">
                <strong>{cas_geo['titre']}</strong><br><br>
                {cas_geo['texte']}
            </div>

            <div class="sub-title">La Caricature Pédagogique Associée</div>
            <div class="bd-box">
                {bd_html_geo_format}
            </div>

            <div class="sub-title">Synthèse des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                1. Équation Bilan de Terrain : <strong>{not_b_g:.1f} / 10</strong><br>
                2. Questionnaire Technique de Synthèse (Quiz + Trous) : <strong>{not_at_g:.1f} / 20</strong><br>
                <strong>Note totale consolidée : {not_tot_g:.1f} / 30</strong>
            </p>

            <div class="sub-title">Activité 1 : Vérification de la configuration d'Équation Bilan</div>
            <table>
                <thead>
                    <tr><th>Paramètre d'Éléments</th><th>Saisie Réalisée Élève</th><th>Attendu Académique</th></tr>
                </thead>
                <tbody>
                    <tr><td>Couple de l'Oxydant sélectionné</td><td>{choix_geo_ox}</td><td>{cas_geo['couple_ox']}</td></tr>
                    <tr><td>Couple du Réducteur sélectionné</td><td>{choix_geo_red}</td><td>{cas_geo['couple_red']}</td></tr>
                    <tr><td>Équation globale équilibrée</td><td><code>{equation_eleve_geo_texte}</code></td><td>Validation par script automatique</td></tr>
                </tbody>
            </table>

            <div class="sub-title">Activité 2 : Correction détaillée du Quiz Technique (10 pts)</div>
            <table>
                <thead><tr><th>N°</th><th>Question Technique Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        for num, q_item in enumerate(questions_geo_optimales, 1):
            saisie = st.session_state.get(f"geo_quiz_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_geo += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_geo += """
                </tbody>
            </table>
            
            <div class="sub-title">Activité 3 : Correction détaillée de la Synthèse à trous (10 pts)</div>
            <table>
                <thead><tr><th>N°</th><th>Phrase complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        for num, t_item in enumerate(cas_geo["trous"], 1):
            enonce_t, _, attendu_t, cle_t = t_item
            saisie_t = st.session_state.get(f"{cle_t}_geo_clean", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_geo += f"<tr><td>{num}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_geo += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_brut_geo = preparer_nom_fichier("Rapport_Application_Geometres")
        nom_propre_html_t10 = os.path.basename(nom_fichier_brut_geo).replace(".txt", ".html")

        st.download_button(
            label="Télécharger le rapport d'évaluation officiel Géomètres (.html)",
            data=html_export_geo,
            file_name=nom_propre_html_t10,
            mime="text/html",
            key="download_btn_t10_final",
        )


















































