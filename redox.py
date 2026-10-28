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

    # Insertion de votre image locale pour l'historique
    try:
        st.image(
            "historique.jpg", caption="Illustration historique des travaux de Lavoisier sur l'oxygène"  )
    except FileNotFoundError:
        st.warning("L'image 'historique.jpg' n'a pas été trouvée dans le dossier.")


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
    col_11, col_12 = st.columns(2)
    with col_11:
        st.markdown("- **1777 - Antoine Lavoisier :** Théorie de la combustion. Définition de l'oxydation par fixation de l'oxygène.")
    with col_12:
        try:
            st.image("Lavoisier.jpg", caption="Antoine Lavoisier")
        except Exception:
            st.warning("L'image 'Lavoisier.jpg' est introuvable.")

    col_13, col_14 = st.columns(2)
    with col_13:
        st.markdown("- **1800 - Alessandro Volta :** Invention de la première pile électrique (Cuivre / Zinc). Début de l'électrochimie.")
    with col_14:
        try:
            st.image("Volta.jpg", caption="Alessandro Volta")
        except Exception:
            st.warning("Volta.jpg' est introuvable.")


    col_15, col_16 = st.columns(2)
    with col_15:
        st.markdown("- **1834 - Michael Faraday :** Établissement des lois de l'électrolyse, reliant la chimie à la quantité d'électricité.")
    with col_16:
        try:
            st.image("Faraday.jpg", caption="Michael Faraday")
        except Exception:
            st.warning("Faraday.jpg' est introuvable.") 
            
    st.markdown("- **1920s - Extension moderne :** Définition définitive et universelle de l'oxydoréduction par transfert d'électrons.")

    st.divider()
    st.subheader("Pourquoi cette étude dans vos filières ?")
    st.write(
        "Que ce soit pour lutter contre la corrosion des châssis (Transport), protéger les structures métalliques (Maintenance), "
        "comprendre la dégradation du béton armé (Travaux Publics) ou préserver les repères topographiques extérieurs (Géomètres), "
        "toutes ces problématiques découlent directement des découvertes de ces scientifiques."
    )

    col_17, col_18, col_19, col_20= st.columns(4)
    with col_17:
        try:
            st.image("rouille_tp.jpg", caption="dégradation du béton armé")
        except Exception:
            st.warning("rouille_tp.jpg' est introuvable.")
    with col_18:
        try:
            st.image("rouille_routier.jpg", caption="corrosion des châssis")
        except Exception:
            st.warning("Volta.jpg' est introuvable.")
    with col_19:
        try:
            st.image("rouille_mm.jpg", caption="dégradation structure")
        except Exception:
            st.warning("rouille_tp.jpg' est introuvable.")
    with col_20:
        try:
            st.image("rouille_geo.jpg", caption="repères topographiques")
        except Exception:
            st.warning("Volta.jpg' est introuvable.")
    st.divider()
           
    st.write(
        "Découvrez l'évolution de la science à travers cette mise en scène historique."
    )

    # Découpage en deux colonnes pour l'histoire textuelle et l'image
    col_graph_hist, col_bd_hist = st.columns(2)

    with col_graph_hist:
        st.write(
            "**La BD humoristique textuelle : La révolution invisible de l'électron**"
        )

        # Affichage du texte narratif dans un encadré bleu (st.info)
        st.info(
            "**Case 1 :** Antoine Lavoisier, en perruque blanche dans son laboratoire de 1777, regarde un morceau de fer brûler sous une cloche de verre. Il note fièrement sur son cahier : 'Le fer s'associe avec l'oxygène de l'air pour devenir de la rouille. J'appelle cela l'oxydation ! C'est clair et limpide !'.\n\n"
            "**Case 2 :** Un siècle plus tard, en 1897, le physicien J.J. Thomson observe ses tubes à rayons cathodiques avec une loupe. Il sursaute sur sa chaise en découvrant une particule minuscule et s'écrie : 'Eurêka ! Il y a des grains d'électricité négative encore plus petits que les atomes ! Je vais les appeler les électrons !'.\n\n"
            "**Case 3 :** Réunion imaginaire au sommet de la chimie au début du 20e siècle. Gilbert Lewis montre un schéma à Lavoisier et lui explique : 'Mon cher Antoine, votre oxygène n'était qu'un intermédiaire ! Regardez de plus près : le fer rouille parce qu'il perd ses électrons. L'oxydation, c'est en réalité une fuite d'électrons !'.\n\n"
            "**Case 4 :** Un atome de fer moderne, équipé d'un bouclier protecteur, regarde les molécules d'oxygène passer au loin sans pouvoir l'atteindre. Il affiche un grand sourire et s'exclame : 'Merci la science ! Maintenant qu'on connaît le secret de nos électrons, les ingénieurs nous protègent contre la corrosion !'."
        )

    with col_bd_hist:
        # Intégration de votre image locale en 4 cases
        try:
            st.image(
                "historique_caricature.jpg",
                caption="Illustration humoristique du changement de modèle scientifique en 4 cases",
                use_container_width=True,
            )
        except Exception:
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
