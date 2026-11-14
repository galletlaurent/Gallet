# -*- coding: utf-8 -*-

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Application la lumière et les couleurs ",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# Vos importations d'origine propres et saines se placent juste en dessous
from datetime import datetime
from itertools import combinations, product
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

# 1. CATALOGUE TECHNIQUE DES SELS MÉTALLIQUES (Test de flamme 400-900 nm)
if "catalogue_metaux" not in st.session_state:
    st.session_state.catalogue_metaux = {
        "Lithium (Li)": {
            "couleur": "#dc2626",
            "descr": "Rouge carmin eclatant (Raies visibles et IR thermique)",
            "raies": [
                (460.3, "#1d4ed8", 0.15),
                (610.3, "#ff6b00", 0.30),
                (670.8, "#ff0000", 0.95),
                (812.6, "#450a0a", 0.10),
            ],
        },
        "Sodium (Na)": {
            "couleur": "#f59e0b",
            "descr": "Jaune orange intense (Doublet D visible et raies proches IR)",
            "raies": [
                (589.0, "#ffcc00", 0.95),
                (589.6, "#ff9900", 0.90),
                (818.3, "#450a0a", 0.12),
                (819.4, "#450a0a", 0.15),
            ],
        },
        "Potassium (K)": {
            "couleur": "#c084fc",
            "descr": "Violet pale / Doublet Infrarouge critique et dominant a 766-769 nm",
            "raies": [
                (404.4, "#4c0519", 0.50),
                (766.5, "#450a0a", 0.95),
                (769.9, "#450a0a", 0.85),
            ],
        },
        "Cuivre (Cu)": {
            "couleur": "#06b6d4",
            "descr": "Vert-Cyan caracteristique (Raies oxydes et atomiques IR)",
            "raies": [
                (510.5, "#00ffcc", 0.40),
                (515.3, "#00ff66", 0.50),
                (521.8, "#15803d", 0.60),
                (793.3, "#450a0a", 0.15),
                (809.2, "#450a0a", 0.20),
            ],
        },
        "Bore (B)": {
            "couleur": "#22c55e",
            "descr": "Vert vif eclatant (Serie visible et proche IR)",
            "raies": [
                (546.0, "#16a34a", 0.30),
                (548.0, "#15803d", 0.40),
                (745.4, "#450a0a", 0.12),
            ],
        },
    }

if "produits_indices" not in st.session_state:
    st.session_state.produits_indices = {
        "Air (n = 1.00)": 1.00,
        "Eau (n = 1.33)": 1.33,
        "Plexiglas / PMMA (n = 1.49)": 1.49,
        "Kérosène / Fioul (n = 1.44)": 1.44,
        "Cyclohexane (n = 1.43)": 1.43,
        "Huile Moteur 10W40 (n = 1.47)": 1.47,
        "Huile Hydraulique HV46 (n = 1.46)": 1.46,
        "Liquide de Frein DOT4 (n = 1.44)": 1.44,
        "Liquide de Refroidissement / Glycol (n = 1.38)": 1.38,
        "Huile de Coupe / Soluble Usinage (n = 1.41)": 1.41,
        "Gazole / Diesel (n = 1.45)": 1.45,
    }

# 2. CATALOGUE TECHNIQUE DES SOURCES LUMINEUSES ET SIGNATURES SPECTRALES
if "lampes_data" not in st.session_state:
    st.session_state.lampes_data = {
        "Lumière du Soleil": {
            "type": "continu",
            "couleur_source": "#FFFDE7",
            "descr": "SPECTRE CONTINU (Étoile de type G2V avec raies de Fraunhofer)",
            "raies": [
                (400.0, "#7C3AED", 0.30),
                (445.0, "#2563EB", 0.50),
                (490.0, "#06B6D4", 0.70),
                (550.0, "#22C55E", 0.95),
                (590.0, "#EAB308", 0.90),
                (640.0, "#F97316", 0.75),
                (700.0, "#EF4444", 0.50),
                (760.0, "#450a0a", 0.30),
                (850.0, "#450a0a", 0.15),
            ],
        },
        "Lampe Halogène": {
            "type": "continu_chaude",
            "couleur_source": "#FFE082",
            "descr": "SPECTRE CONTINU (Filament de tungstène sous enveloppe quartz)",
            "raies": [
                (420.0, "#4F46E5", 0.15),
                (460.0, "#3B82F6", 0.30),
                (510.0, "#10B981", 0.45),
                (560.0, "#84CC16", 0.65),
                (600.0, "#F97316", 0.85),
                (650.0, "#EF4444", 0.95),
                (750.0, "#450a0a", 0.95),
                (850.0, "#450a0a", 0.99),
            ],
        },
        "Lampe à Incandescence Standard": {
            "type": "continu_chaude",
            "couleur_source": "#FFD54F",
            "descr": "SPECTRE CONTINU THERMIQUE FILAMENT STANDARD",
            "raies": [
                (430.0, "#4338CA", 0.10),
                (470.0, "#1D4ED8", 0.22),
                (520.0, "#047857", 0.40),
                (570.0, "#A3E635", 0.60),
                (610.0, "#EA580C", 0.80),
                (660.0, "#DC2626", 0.90),
                (740.0, "#450a0a", 0.95),
                (840.0, "#450a0a", 0.96),
            ],
        },
        "Corps Noir Élevé (5000K)": {
            "type": "continu",
            "couleur_source": "#F8FAFC",
            "descr": "SPECTRE CONTINU THÉORIQUE ÉQUILIBRE PLANCKIEN",
            "raies": [
                (410.0, "#6366F1", 0.60),
                (450.0, "#2563EB", 0.85),
                (500.0, "#06B6D4", 0.95),
                (550.0, "#22C55E", 0.90),
                (600.0, "#EAB308", 0.75),
                (650.0, "#EF4444", 0.60),
                (720.0, "#450a0a", 0.40),
                (820.0, "#450a0a", 0.20),
            ],
        },
        "Tube Fluorescent (Bureau)": {
            "type": "mixte",
            "couleur_source": "#F5F5F5",
            "descr": "SPECTRE MIXTE (Fonds thermique et raies de décharge)",
            "raies": [
                (436.0, "#311B92", 0.12),
                (487.0, "#00838F", 0.29),
                (546.0, "#2E7D32", 0.49),
                (611.0, "#E65100", 0.70),
            ],
        },
        "Ampoule Fluocompacte": {
            "type": "raies",
            "couleur_source": "#E0F2F1",
            "descr": "SPECTRE DE RAIES / BANDES FLUORESCENTES",
            "raies": [
                (436.0, "#311B92", 0.12),
                (487.0, "#00838F", 0.31),
                (544.0, "#2E7D32", 0.48),
                (587.0, "#FF8F00", 0.62),
                (611.0, "#C62828", 0.70),
            ],
        },
        "LED Blanche (Froide)": {
            "type": "led_froide",
            "couleur_source": "#E0F2F1",
            "descr": "SPECTRE MIXTE (Pic Bleu intense + cloche d'émission Jaune)",
            "raies": [
                (450.0, "#0000FF", 0.98),
                (520.0, "#00FF00", 0.35),
                (560.0, "#FFFF00", 0.55),
                (600.0, "#FF8000", 0.48),
                (645.0, "#FF0000", 0.30),
            ],
        },
        "Lampe au Deutérium (D2)": {
            "type": "raies",
            "couleur_source": "#EDE7F6",
            "descr": "SPECTRE DE LABO ATOMIQUE LOURD",
            "raies": [(486.0, "#00ffcc", 0.25), (656.1, "#ff0000", 0.80)],
        },
        "Lampe au Mercure (Hg)": {
            "type": "raies",
            "couleur_source": "#E0F7FA",
            "descr": "SPECTRE DE RAIES INTENSE UV-VISIBLE",
            "raies": [
                (404.7, "#4c0519", 0.02),
                (435.8, "#2563eb", 0.12),
                (546.1, "#22c55e", 0.49),
                (578.0, "#eab308", 0.59),
            ],
        },
        "Lampe au Sodium (Na)": {
            "type": "raies",
            "couleur_source": "#FFF3E0",
            "descr": "SPECTRE DE RAIES (DOUBLET D DE FRAUNHOFER)",
            "raies": [(589.0, "#ffcc00", 0.95), (589.6, "#ff9900", 0.90)],
        },
        "Lampe à l'Hélium (He)": {
            "type": "raies",
            "couleur_source": "#FFE0B2",
            "descr": "SPECTRE DE RAIES ATOMIQUE SIMPLE",
            "raies": [
                (447.1, "#1d4ed8", 0.16),
                (501.6, "#06b6d4", 0.34),
                (587.6, "#f59e0b", 0.63),
                (667.8, "#dc2626", 0.89),
            ],
        },
        "Lampe au Néon (Ne)": {
            "type": "raies",
            "couleur_source": "#FFCCBC",
            "descr": "SPECTRE DE RAIES TRÈS RICHE DANS LE ROUGE",
            "raies": [
                (585.2, "#f59e0b", 0.62),
                (614.3, "#ea580c", 0.71),
                (640.2, "#dc2626", 0.80),
                (692.9, "#991b1b", 0.97),
            ],
        },
        "Lampe à l'Argon (Ar)": {
            "type": "raies",
            "couleur_source": "#E8EAF6",
            "descr": "SPECTRE DE GAZ DE DÉCHARGE BLEUTÉ",
            "raies": [
                (420.0, "#581c87", 0.45),
                (430.0, "#4338ca", 0.30),
                (450.0, "#2563eb", 0.25),
                (488.0, "#06b6d4", 0.40),
                (696.5, "#991b1b", 0.50),
            ],
        },
        "Lampe au Krypton (Kr)": {
            "type": "raies",
            "couleur_source": "#F1F5F9",
            "descr": "SPECTRE ATOMIQUE KRYPTON COHÉRENT",
            "raies": [
                (431.9, "#4338ca", 0.15),
                (557.0, "#22c55e", 0.60),
                (587.1, "#f59e0b", 0.45),
                (642.1, "#dc2626", 0.35),
            ],
        },
        "Lampe au Xénon (Xe)": {
            "type": "raies",
            "couleur_source": "#E2E8F0",
            "descr": "SPECTRE DE DÉCHARGE FLASH CONTINU/RAIES",
            "raies": [
                (462.7, "#2563eb", 0.40),
                (467.1, "#3b82f6", 0.50),
                (473.4, "#06b6d4", 0.35),
                (529.2, "#22c55e", 0.20),
                (680.6, "#dc2626", 0.45),
            ],
        },
        "Lampe au Cadmium (Cd)": {
            "type": "raies",
            "couleur_source": "#D1C4E9",
            "descr": "SPECTRE DE RAIES MÉTALLIQUES STABLES",
            "raies": [
                (467.8, "#2563eb", 0.22),
                (479.9, "#06b6d4", 0.29),
                (508.6, "#22c55e", 0.36),
            ],
        },
        "Lampe au Zinc (Zn)": {
            "type": "raies",
            "couleur_source": "#ECEFF1",
            "descr": "SPECTRE DE RAIES VAPEUR MÉTAL HAUTE PRESSION",
            "raies": [
                (468.0, "#2563eb", 0.15),
                (472.2, "#1d4ed8", 0.20),
                (481.1, "#06b6d4", 0.35),
                (636.2, "#dc2626", 0.50),
            ],
        },
        "Lampe au Lithium (Li)": {
            "type": "raies",
            "couleur_source": "#FEE2E2",
            "descr": "SPECTRE D'ALCALIN LABO VIF (3 RAIES PHYSIQUES)",
            "raies": [
                (460.3, "#1d4ed8", 0.10),
                (610.3, "#ff6b00", 0.30),
                (670.8, "#ff0000", 0.90),
            ],
        },
        "Lampe au Potassium (K)": {
            "type": "raies",
            "couleur_source": "#F3E8FF",
            "descr": "SPECTRE ALCALIN DE LABO STABLE (SANS ERREUR 693 NM)",
            "raies": [
                (404.4, "#4c0519", 0.40),
                (766.5, "#450a0a", 0.95),
                (769.9, "#450a0a", 0.85),
            ],
        },
        "Lampe au Thallium (Tl)": {
            "type": "raies",
            "couleur_source": "#DCFCE7",
            "descr": "SPECTRE A RAIE VERTE UNIQUE PRÉPONDÉRANTE",
            "raies": [(535.0, "#22c55e", 0.95)],
        },
        "Vapeur d'Iode (I2 - Moléculaire)": {
            "type": "raies",
            "couleur_source": "#FAE8FF",
            "descr": "SPECTRE DE BANDES MOLÉCULAIRES DISCRETES",
            "raies": [
                (520.0, "#16a34a", 0.30),
                (535.0, "#15803d", 0.45),
                (550.0, "#84cc16", 0.50),
                (565.0, "#eab308", 0.40),
            ],
        },
    }

st.title("Application la lumière et les couleurs")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)
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
# INITIALISATION SECURISEE DU SESSION STATE (A l'ouverture de l'application)
# =============================================================================
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
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")

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

# Déclaration officielle des 10 onglets de navigation
onglets = st.tabs([
    "Identification",
    "Historique",
    "La loupe",
    "La lunette astronomique",
    "La lunette de Galilée",
    "Le microscope",
    "L'appareil photographique",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier",
    "Application dans le domaine géomètre topographe"
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


def afficher_questions_optique9(verrouille=False):
    col_double_quiz_opt9, col_double_trous_opt9 = st.columns(2)

    with col_double_quiz_opt9:
        st.markdown("##### Quiz sur le microscope (10 questions) - Optique 9 (10 pts)")
        if "ordre_questions_opt9" not in st.session_state:
            questions_opt9_base = [
                ("q1", "Dans un microscope, la premiere lentille convergente tres puissante pres de l'objet s'appelle l' :"),
                ("q2", "La distance fixe separent le foyer image de l'objectif F'1 et le foyer objet de l'oculaire F2 est appelee l' :"),
                ("q3", "L'image intermediaire A1B1 creee par l'objectif du microscope est une image :"),
                ("q4", "La seconde lentille (l'oculaire) joue le role d'une loupe. Elle observe l'image intermédiaire placee :"),
                ("q5", "Pour un confort visuel maximal de l'observateur (oeil au repos sans accommoder), l'image finale doit se former :"),
                ("q6", "Le grandissement transversal de l'objectif d'un microscope est une grandeur physique de signe :"),
                ("q7", "Le grossissement total G du microscope est egal au produit du grossissement de l'oculaire par :"),
                ("q8", "Si le grandissement de l'objectif vaut -10 et le grossissement de l'oculaire vaut 4, le grossissement total vaut :"),
                ("q9", "Par rapport a l'objet micro-optique reel place sur la platine, l'image finale observee est :"),
                ("q10", "La puissance d'un microscope s'exprime couramment en dioptries ou par son grossissement commercial note :")
            ]
            import random
            random.shuffle(questions_opt9_base)
            st.session_state.ordre_questions_opt9 = questions_opt9_base

        dict_quiz_opt9 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt9, 1):
            cle_qo9 = f"col_g_quiz_opt9_{q_id}"
            cle_opts_unique = f"opts_opt9_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Objectif (de tres courte distance focale)", "Oculaire", "Condenseur de champ"]
                elif q_id == "q2": copie_opts = ["Intervalle optique Delta", "Distance focale totale", "Longueur mecanique du tube"]
                elif q_id == "q3": copie_opts = ["Reelle, renversee et tres agrandie", "Virtuelle, droite et plus petite", "Virtuelle et renversee"]
                elif q_id == "q4": copie_opts = ["Pile dans son plan focal objet (foyer F2)", "Sur son centre optique O2", "A l'infini en aval"]
                elif q_id == "q5": copie_opts = ["A l'infini", "Sur la lentille objectif", "Au niveau du cercle oculaire"]
                elif q_id == "q6": copie_opts = ["Negatif (car l'image intermediaire est renversee)", "Positif", "Nul"]
                elif q_id == "q7": copie_opts = ["Le grandissement de l'objectif", "La vergence de l'objectif", "La distance focale de l'oculaire"]
                elif q_id == "q8": copie_opts = ["-40", "40", "-2.5"]
                elif q_id == "q9": copie_opts = ["Renversee et fortement agrandie", "Droite et agrandie", "Renversee et plus petite"]
                elif q_id == "q10": copie_opts = ["Un nombre suivi de la lettre X (ex: x40)", "Un angle en radians", "Une valeur en metres"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo9, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt9[f"{q_id}_opt9"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo9, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt9:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 9 (10 pts)")
        
        co9_1, co9_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_1: st.write("Le microscope compose utilise deux systemes convergents. Le premier est l'")
        with co9_2: t1 = st.selectbox("", ["Choisir...", "Objectif", "Oculaire", "Miroir"], key="opt9_t1", disabled=verrouille, label_visibility="collapsed")
        
        co9_3, co9_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_3: st.write("de tres courte focale, qui genere une image intermediaire reelle. Le second est l'")
        with co9_4: t2 = st.selectbox("", ["Choisir...", "Oculaire", "Objectif", "Prisme"], key="opt9_t2", disabled=verrouille, label_visibility="collapsed")

        co9_5, co9_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_5: st.write("qui fait office de loupe pour observer cette derniere. La distance fixe F'1F2 s'appelle l'")
        with co9_6: t3 = st.selectbox("", ["Choisir...", "Intervalle optique", "Axe de visée", "Diametre utile"], key="opt9_t3", disabled=verrouille, label_visibility="collapsed")

        co9_7, co9_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_7: st.write("L'image finale de la structure cellulaire ou micro-mecanique est ainsi rejetee a l'infini.")

        dict_trous_opt9 = {
            "t1_opt9": t1, "t2_opt9": t2, "t3_opt9": t3
        }

    return dict_quiz_opt9, dict_trous_opt9

def afficher_questions_optique8(verrouille=False):
    col_double_quiz_opt8, col_double_trous_opt8 = st.columns(2)

    with col_double_quiz_opt8:
        st.markdown("##### Quiz sur la lunette de Galilee (10 questions) - Optique 8 (10 pts)")
        if "ordre_questions_opt8" not in st.session_state:
            questions_opt8_base = [
                ("q1", "Quelle est la principale difference de constitution entre la lunette de Galilee et celle de Kepler :"),
                ("q2", "L'oculaire utilise dans une lunette de Galilee possede une distance focale f'2 :"),
                ("q3", "Pour qu'une lunette de Galilee soit afocale, le foyer image F'1 de l'objectif doit etre confondu avec :"),
                ("q4", "Par rapport a la lunette de Kepler, l'image finale observee a travers la lunette de Galilee est :"),
                ("q5", "L'encombrement de l'instrument (distance O1O2) d'une lunette de Galilee afocale est egal a :"),
                ("q6", "La distance separent les deux lentilles O1O2 d'une lunette de Galilee est necessairement :"),
                ("q7", "Le grossissement nominal G d'une lunette afocale est calculé par G = - f'1 / f'2. Pour Galilee, G est :"),
                ("q8", "Si l'objectif fait f'1 = 60 cm et l'oculaire f'2 = -15 cm, le grossissement G vaut :"),
                ("q9", "Quel est l'inconvenient principal d'une lunette de Galilee par rapport a une lunette de Kepler :"),
                ("q10", "Dans quel instrument grand public retrouve-t-on couramment le systeme optique de Galilee :")
            ]
            import random
            random.shuffle(questions_opt8_base)
            st.session_state.ordre_questions_opt8 = questions_opt8_base

        dict_quiz_opt8 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt8, 1):
            cle_qo8 = f"col_g_quiz_opt8_{q_id}"
            cle_opts_unique = f"opts_opt8_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["L'oculaire de Galilee est une lentille divergente", "L'objectif de Galilee est une lentille divergente", "Galilee comporte trois miroirs prismatiques"]
                elif q_id == "q2": copie_opts = ["Strictement negative (f'2 < 0)", "Strictement positive (f'2 > 0)", "Rigoureusement nulle"]
                elif q_id == "q3": copie_opts = ["Le foyer objet F2 de l'oculaire divergent", "Le foyer image F'2 de l'oculaire divergent", "Le centre optique O2"]
                elif q_id == "q4": copie_opts = ["Droite (dans le meme sens que l'astre)", "Renversee (haut-bas)", "Inclinee a 90 degres"]
                elif q_id == "q5": copie_opts = ["f'1 + f'2 (ce qui donne une soustraction car f'2 est negatif)", "f'1 - f'2 (ce qui donne une addition)", "f'1 * f'2"]
                elif q_id == "q6": copie_opts = ["Plus courte que celle de Kepler", "Plus longue que celle de Kepler", "Rigoureusement identique"]
                elif q_id == "q7": copie_opts = ["Positif (l'image finale est droite)", "Negatif (l'image finale est inversee)", "Nul"]
                elif q_id == "q8": copie_opts = ["4.0 (car f'2 est negatif)", "-4.0", "0.25"]
                elif q_id == "q9": copie_opts = ["Un champ visuel tres etroit", "Une image totalement floue au centre", "Une perte totale de luminosite"]
                elif q_id == "q10": copie_opts = ["Les jumelles de theatre (ou de spectacle)", "Les microscopes biologiques", "Les telemetres de topographie"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo8, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt8[f"{q_id}_opt8"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo8, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt8:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 8 (10 pts)")
        
        co8_1, co8_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_1: st.write("La lunette de Galilee se distingue par l'utilisation d'un oculaire de nature")
        with co8_2: t1 = st.selectbox("", ["Choisir...", "Divergente", "Convergente", "Prismatique"], key="opt8_t1", disabled=verrouille, label_visibility="collapsed")
        
        co8_3, co8_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_3: st.write("Pour obtenir la configuration afocale, le foyer image de l'objectif coincide avec le foyer")
        with co8_4: t2 = st.selectbox("", ["Choisir...", "Objet F2", "Image F'2", "Central O2"], key="opt8_t2", disabled=verrouille, label_visibility="collapsed")

        co8_5, co8_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_5: st.write("de l'oculaire. L'avantage majeur de ce montage est de generer une image finale")
        with co8_6: t3 = st.selectbox("", ["Choisir...", "Droite", "Inversee", "Virtuelle pure"], key="opt8_t3", disabled=verrouille, label_visibility="collapsed")

        co8_7, co8_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_7: st.write("ce qui dispense de l'utilisation d'un vehicule de redressement. Son grossissement est")
        with col_double_trous_opt8: st.write("calcule positivement par le rapport des focales.")

        dict_trous_opt8 = {
            "t1_opt8": t1, "t2_opt8": t2, "t3_opt8": t3
        }

    return dict_quiz_opt8, dict_trous_opt8



def afficher_questions_optique7(verrouille=False):
    col_double_quiz_opt7, col_double_trous_opt7 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES SUR LA LUNETTE ---
    with col_double_quiz_opt7:
        st.markdown("##### Quiz sur la lunette astronomique (10 questions) - Optique 7 (10 pts)")
        if "ordre_questions_opt7" not in st.session_state:
            questions_opt7_base = [
                ("q1", "Dans une lunette astronomique, la premiere lentille qui reçoit les rayons de l'astre est l' :"),
                ("q2", "La seconde lentille devant laquelle l'observateur place son oeil s'appelle l' :"),
                ("q3", "Une lunette astronomique est dite 'afocale' si l'image d'un objet situe a l'infini se forme :"),
                ("q4", "Pour qu'une lunette soit parfaitement afocale, il faut que le foyer image F'1 de l'objectif soit confondu avec :"),
                ("q5", "Quelle est la nature de l'image intermediaire A1B1 creee entre l'objectif et l'oculaire :"),
                ("q6", "L'image finale de l'astre observee par l'etudiant a travers la lunette afocale est situee :"),
                ("q7", "Le grossissement G d'une lunette afocale est donne par le rapport des distances focales :"),
                ("q8", "Si l'objectif a une focale f'1 = 100 cm et l'oculaire f'2 = 5 cm, le grossissement G de la lunette vaut :"),
                ("q9", "Par rapport a l'astre reel pointe dans le ciel, l'image finale observee a travers la lunette est :"),
                ("q10", "Le cercle oculaire correspond a la zone ou la luminosite est maximale. Il est l'image de :")
            ]
            import random
            random.shuffle(questions_opt7_base)
            st.session_state.ordre_questions_opt7 = questions_opt7_base

        dict_quiz_opt7 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt7, 1):
            cle_qo7 = f"col_g_quiz_opt7_{q_id}"
            cle_opts_unique = f"opts_opt7_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Objectif (de grande distance focale)", "Oculaire (de courte distance focale)", "Miroir parabolique"]
                elif q_id == "q2": copie_opts = ["Oculaire", "Objectif", "Diaphragme de champ"]
                elif q_id == "q3": copie_opts = ["A l'infini (confort de vision sans fatigue pour l'oeil)", "Sur le centre optique O1", "Entre les deux lentilles"]
                elif q_id == "q4": copie_opts = ["Le foyer objet F2 de l'oculaire", "Le foyer image F'2 de l'oculaire", "Le centre optique O2"]
                elif q_id == "q5": copie_opts = ["Reelle et renversee (situee dans le plan focal commun)", "Virtuelle et droite", "Reelle et droite"]
                elif q_id == "q6": copie_opts = ["A l'infini (pas besoin d'accommoder)", "A la distance minimale de vision distincte", "Pile sur la lentille oculaire"]
                elif q_id == "q7": copie_opts = ["G = f'1 / f'2", "G = f'2 / f'1", "G = f'1 * f'2"]
                elif q_id == "q8": copie_opts = ["20", "200", "0.05"]
                elif q_id == "q9": copie_opts = ["Renversee (haut-bas et droite-gauche)", "Droite (dans le meme sens)", "Inclinee a 45 degres"]
                elif q_id == "q10": copie_opts = ["L'objectif par l'oculaire", "L'oculaire par l'objectif", "L'astre par l'oculaire"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo7, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt7[f"{q_id}_opt7"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo7, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE DU DOUBLE SYSTÈME AFOCAL ---
    with col_double_trous_opt7:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 7 (10 pts)")
        
        co7_1, co7_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_1: st.write("La lunette astronomique est composee de deux lentilles convergentes. La premiere est l'")
        with co7_2: t1 = st.selectbox("", ["Choisir...", "Objectif", "Oculaire", "Inverseur"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")
        
        co7_3, co7_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_3: st.write("de grande distance focale, et la seconde, proche de l'oeil, est l'")
        with co7_4: t2 = st.selectbox("", ["Choisir...", "Oculaire", "Objectif", "Prisme"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

        co7_5, co7_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_5: st.write("Lorsque le foyer image de la premiere coincide avec le foyer objet de la seconde, le systeme est")
        with co7_6: t3 = st.selectbox("", ["Choisir...", "Afocal", "Convergent", "Divergent"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

        co7_7, co7_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_7: st.write("L'image d'un astre lointain sort alors a l'infini, permettant d'observer sans fatigue. Le")
        with co7_8: t4 = st.selectbox("", ["Choisir...", "Grossissement", "Grandissement", "Champ"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")
        
        st.write("de l'appareil correspond au rapport de la focale de l'objectif sur celle de l'oculaire.")

        dict_trous_opt7 = {
            "t1_opt7": t1, "t2_opt7": t2, "t3_opt7": t3, "t4_opt7": t4
        }

    return dict_quiz_opt7, dict_trous_opt7

def dessiner_microscope_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    try:
        val_ech_x = float(st.session_state.get("var_echelle_x_choix", "1"))
        val_ech_y = float(st.session_state.get("var_echelle_y_choix", "1"))
    except:
        val_ech_x, val_ech_y = 1.0, 1.0

    base_echelle_x = 3.5
    echelle_x = base_echelle_x * val_ech_x
    
    w = 680
    h = 260
    y0 = h / 2.0  

    fig, ax = plt.subplots(figsize=(10, 3.8), facecolor="#0f172a")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.05)
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    choix_obj = st.session_state.get("var_choix_objectif", "X10")        
    h_obj_physique = st.session_state.get("slide_mic_ab", 15.0)
    
    if choix_obj == "X4":
        f1_brute = 45.0
    elif choix_obj == "X40":
        f1_brute = 15.0
    elif choix_obj == "X100":
        f1_brute = 6.0
    else:
        f1_brute = 30.0

    f1 = f1_brute * echelle_x
    f2 = st.session_state.get("slide_mic_f2", 40.0) * echelle_x
    h_obj = h_obj_physique * val_ech_y
    
    tube_pixels_bruts = st.session_state.get("slide_mic_tube", 320.0)
    tube_pixels = tube_pixels_bruts * val_ech_x

    x_obj = 160.0
    x_ocu = x_obj + tube_pixels 

    pos_A_cm = st.session_state.get("slide_mic_xa", 42.0)
    xa = (x_obj - f1) - ((pos_A_cm - 20.0) * 1.5)

    if xa >= (x_obj - f1):
        xa = x_obj - f1 - 8.0

    d_objet_L1 = xa - x_obj
    d_image_L1 = (f1 * d_objet_L1) / (f1 + d_objet_L1) if (f1 + d_objet_L1) != 0 else f1 * 10
    xa1 = x_obj + d_image_L1  

    grandissement_obj = d_image_L1 / d_objet_L1 if d_objet_L1 != 0 else -1.0
    # Forçage du signe négatif pour orienter la flèche intermédiaire vers le bas
    h_image_interm = - abs(h_obj * grandissement_obj)

    xf1 = x_obj - f1
    xf_prime1 = x_obj + f1
    xf2 = x_ocu - f2
    xf_prime2 = x_ocu + f2
    x_fin_rayons = x_ocu + 110.0

    pente_sortie_vrais_rayons = abs(h_image_interm) / f2 if f2 != 0 else 0

    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5, zorder=1)
    ax.text(w - 25, y0 + 14, "Axe", color="#64748b", fontsize=7, style="italic", ha="right")

    ax.plot([xf1, xf1], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf1, y0 + 16, "F1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")
    ax.plot([xf_prime1, xf_prime1], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf_prime1, y0 + 16, "F'1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")

    ax.plot([xf2, xf2], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf2, y0 + 16, "F2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")
    ax.plot([xf_prime2, xf_prime2], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf_prime2, y0 + 16, "F'2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")

    ax.plot([x_obj, x_obj], [15, h - 15], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_obj - 6, x_obj, x_obj + 6], [23, 15, 23], color="#3b82f6", lw=2)
    ax.plot([x_obj - 6, x_obj, x_obj + 6], [h - 23, h - 15, h - 23], color="#3b82f6", lw=2)
    ax.text(x_obj - 12, y0 + 14, "O1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right")

    # Oculaire O2 avec coordonnees verticales completes
    ax.plot([x_ocu, x_ocu], [15, h - 15], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [23, 15, 23], color="#3b82f6", lw=2)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [h - 23, h - 15, h - 23], color="#3b82f6", lw=2)
    ax.text(x_ocu + 12, y0 + 14, "O2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="left")

    # Objet réel AB (Violet)
    ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2.5), zorder=4)
    ax.text(xa, y0 + 14, "A", color="#a855f7", fontsize=7, fontweight="bold", ha="center")
    ax.text(xa, y0 - h_obj - 5, "B", color="#a855f7", fontsize=7, fontweight="bold", ha="center")

    # Marche des rayons
    pente_entree_bleu = h_obj / (x_obj - xa) if (x_obj - xa) != 0 else 0
    y_impact_ocu_bleu = y0 + (x_ocu - x_obj) * pente_entree_bleu
    ax.annotate("", xy=(x_obj, y0), xytext=(xa, y0 - h_obj), arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5), zorder=4)
    ax.plot([x_obj, x_ocu], [y0, y_impact_ocu_bleu], color="#2563eb", lw=1.5, zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_bleu, y_impact_ocu_bleu + (x_fin_rayons - x_ocu) * pente_sortie_vrais_rayons], color="#2563eb", lw=1.5, zorder=4)

    y_impact_obj_jaune = y0 - h_obj
    ax.annotate("", xy=(x_obj, y_impact_obj_jaune), xytext=(xa, y_impact_obj_jaune), arrowprops=dict(arrowstyle="->", color="#eab308", lw=1.5), zorder=4)
    pente_jaune_cours = (y0 - y_impact_obj_jaune) / (xf_prime1 - x_obj) if (xf_prime1 - x_obj) != 0 else 0
    y_impact_ocu_jaune = y_impact_obj_jaune + (x_ocu - x_obj) * pente_jaune_cours
    ax.plot([x_obj, x_ocu], [y_impact_obj_jaune, y_impact_ocu_jaune], color="#eab308", lw=1.5, zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_jaune, y_impact_ocu_jaune + (x_fin_rayons - x_ocu) * pente_sortie_vrais_rayons], color="#eab308", lw=1.5, zorder=4)

    pente_entree_rose = h_obj / (xf1 - xa) if (xf1 - xa) != 0 else 0
    y_impact_obj_rose = y0 + (x_obj - xf1) * pente_entree_rose
    y_impact_ocu_rose = y0 - h_image_interm
    ax.annotate("", xy=(xf1, y0), xytext=(xa, y0 - h_obj), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=1.5), zorder=4)
    ax.plot([xf1, x_obj], [y0, y_impact_obj_rose], color="#ec4899", lw=1.5, zorder=4)
    ax.plot([x_obj, x_ocu], [y_impact_obj_rose, y_impact_ocu_rose], color="#ec4899", lw=1.5, zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_rose, y_impact_ocu_rose + (x_fin_rayons - x_ocu) * pente_sortie_vrais_rayons], color="#ec4899", lw=1.5, zorder=4)

    # RECALCUL DE SÉCURITÉ DE L'INTERSECTION POUR LES GRANDS ANGLES
    if xa1 >= x_ocu or xa1 <= x_obj:
        xa1 = xf2

    # TRACÉ DE A1B1 CORRECTEMENT ORIENTÉ VERS LE BAS
    ax.annotate("", xy=(xa1, y0 - h_image_interm), xytext=(xa1, y0), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2.5), zorder=5)
    ax.text(xa1, y0 - 12, "A1", color="#10b981", fontsize=8, fontweight="bold", ha="center")
    ax.text(xa1, y0 - h_image_interm + 14, "B1", color="#10b981", fontsize=8, fontweight="bold", ha="center")

    x_oeil = x_fin_rayons + 15.0
    y_oeil = y_impact_ocu_bleu + (x_fin_rayons - x_ocu) * pente_sortie_vrais_rayons * 0.5
    ax.add_patch(patches.Arc((x_oeil, y_oeil), 20, 28, angle=90, theta1=0, theta2=180, edgecolor="#cbd5e1", lw=2, zorder=5))
    ax.add_patch(patches.Ellipse((x_oeil - 1.5, y_oeil), 7, 10, facecolor="#3b82f6", edgecolor="#1e3a8a", zorder=5))
    ax.add_patch(patches.Ellipse((x_oeil - 1.5, y_oeil), 3, 6, facecolor="black", edgecolor="black", zorder=5))

    grossissement_commercial = abs(grandissement_obj) * (250.0 / (st.session_state.get("slide_mic_f2", 40.0)))
    st.session_state.opt9_txt_panneau_bas = (
        f"• Grandissement Objectif γ1 = {grandissement_obj:.2f}\n"
        f"• Intervalle optique Δ = {tube_pixels_bruts:.1f} px\n"
        f"• Grossissement G = {grossissement_commercial:.2f}x\n"
        f"• Tube O1O2 = {x_ocu - x_obj:.1f} px"
    )

    ax.text(20, 20, "INSTRUMENTATION LAB : MICROSCOPE COMPOSÉ", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    return fig


def dessiner_lunette_galilee_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    echelle_x = 3.5
    w = 680
    h = 260
    y0 = h / 2.0  

    fig, ax = plt.subplots(figsize=(10, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    f1_brute = st.session_state.get("slide_gal_f1", 80.0)
    f2_brute = st.session_state.get("slide_gal_f2_abs", 30.0)
    h_inc = st.session_state.get("slide_gal_inc", 20.0)

    f1 = f1_brute * echelle_x
    f2 = f2_brute * echelle_x

    angle_theta = h_inc / 100.0
    taille_image_interm_cm = f1_brute * angle_theta
    h_image_dessin = taille_image_interm_cm * echelle_x

    x_obj = 220.0
    x_ocu = x_obj + f1 - f2
    xf_commun = x_obj + f1  

    xf1 = x_obj - f1       
    xf_prime2 = x_ocu - f2 

    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5, zorder=1)
    ax.text(w - 25, y0 + 14, "Axe", color="#64748b", fontsize=7, style="italic", ha="right")

    ax.plot([xf1, xf1], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf1, y0 + 16, "F1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")

    ax.plot([xf_prime2, xf_prime2], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf_prime2, y0 + 16, "F'2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")

    ax.plot([xf_commun, xf_commun], [y0 - 6, y0 + 6], color="white", lw=2, zorder=2)
    ax.text(xf_commun, y0 - 14, "F'1", color="#38bdf8", fontsize=7, fontweight="bold", ha="center")
    ax.text(xf_commun, y0 + 16, "F2", color="#38bdf8", fontsize=7, fontweight="bold", ha="center")

    ax.plot([x_obj, x_obj], [15, h - 15], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_obj - 6, x_obj, x_obj + 6], [23, 15, 23], color="#3b82f6", lw=2)
    ax.plot([x_obj - 6, x_obj, x_obj + 6], [h - 23, h - 15, h - 23], color="#3b82f6", lw=2)
    ax.text(x_obj - 12, y0 + 14, "O1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right")

    # L2 : Oculaire divergent avec coordonnées de flèches rentrantes (RÉPARÉ)
    ax.plot([x_ocu, x_ocu], [40, h - 40], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [40, 48, 40], color="#3b82f6", lw=2)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [h - 40, h - 48, h - 40], color="#3b82f6", lw=2)
    ax.text(x_ocu + 12, y0 + 14, "O2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="left")

    pente_entree = h_inc / f1
    pente_output = h_image_dessin / f2  
    x_fin_rayons = x_ocu + 120.0
    x_image_finale = 50.0

    ax.annotate("", xy=(x_obj, y0), xytext=(15, y0 - (x_obj - 15) * pente_entree), arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5), zorder=4)
    pente_inter_bleu = h_image_dessin / f1
    y_impact_ocu_bleu = y0 + (x_ocu - x_obj) * pente_inter_bleu
    ax.plot([x_obj, x_ocu], [y0, y_impact_ocu_bleu], color="#2563eb", lw=1.5, zorder=4)
    ax.plot([x_ocu, xf_commun], [y_impact_ocu_bleu, y0 + h_image_dessin], color="#22c55e", lw=1.5, linestyle="--", zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_bleu, y_impact_ocu_bleu + (x_fin_rayons - x_ocu) * pente_output], color="#2563eb", lw=1.5, zorder=4)

    y_impact_obj_jaune = y0 - h_image_dessin
    ax.annotate("", xy=(x_obj, y_impact_obj_jaune), xytext=(15, y_impact_obj_jaune - (x_obj - 15) * pente_entree), arrowprops=dict(arrowstyle="->", color="#eab308", lw=1.5), zorder=4)
    pente_inter_jaune = (2.0 * h_image_dessin) / f1
    y_impact_ocu_jaune = y_impact_obj_jaune + (x_ocu - x_obj) * pente_inter_jaune
    ax.plot([x_obj, x_ocu], [y_impact_obj_jaune, y_impact_ocu_jaune], color="#eab308", lw=1.5, zorder=4)
    ax.plot([x_ocu, xf_commun], [y_impact_ocu_jaune, y_0 + h_image_dessin if 'y_0' in locals() else y0 + h_image_dessin], color="#22c55e", lw=1.5, linestyle="--", zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_jaune, y_impact_ocu_jaune + (x_fin_rayons - x_ocu) * pente_output], color="#eab308", lw=1.5, zorder=4)

    y_impact_obj_rose = y0 + h_image_dessin
    ax.annotate("", xy=(x_obj, y_impact_obj_rose), xytext=(15, y_impact_obj_rose + (15 - x_obj) * pente_entree), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=1.5), zorder=4)
    y_impact_ocu_rose = y_impact_obj_rose
    ax.plot([x_obj, x_ocu], [y_impact_obj_rose, y_impact_ocu_rose], color="#ec4899", lw=1.5, zorder=4)
    ax.plot([x_ocu, xf_commun], [y_impact_ocu_rose, y_impact_obj_rose], color="#22c55e", lw=1.5, linestyle="--", zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_rose, y_impact_ocu_rose + (x_fin_rayons - x_ocu) * pente_output], color="#ec4899", lw=1.5, zorder=4)

    ax.plot([xf_commun, xf_commun], [y0, y0 + h_image_dessin], color="#10b981", lw=2, linestyle="--", zorder=5)
    ax.text(xf_commun + 12, y0 + (h_image_dessin / 2.0), "A1B1 (Virt.)", color="#10b981", fontsize=7, fontweight="bold", ha="left", va="center")

    y_prolongement_jaune = y_impact_ocu_jaune - (x_ocu - x_image_finale) * pente_output
    y_prolongement_bleu  = y_impact_ocu_bleu - (x_ocu - x_image_finale) * pente_output
    y_prolongement_rose  = y_impact_ocu_rose - (x_ocu - x_image_finale) * pente_output

    ax.plot([x_ocu, x_image_finale], [y_impact_ocu_jaune, y_prolongement_jaune], color="#ef4444", lw=1.2, linestyle=":")
    ax.plot([x_ocu, x_image_finale], [y_impact_ocu_bleu, y_prolongement_bleu], color="#ef4444", lw=1.2, linestyle=":")
    ax.plot([x_ocu, x_image_finale], [y_impact_ocu_rose, y_prolongement_rose], color="#ef4444", lw=1.2, linestyle=":")

    x_oeil = x_fin_rayons + 15.0
    y_oeil = y_impact_ocu_bleu + (x_fin_rayons - x_ocu) * pente_output
    ax.add_patch(patches.Arc((x_oeil, y_oeil), 20, 28, angle=90, theta1=0, theta2=180, edgecolor="#cbd5e1", lw=2, zorder=5))
    ax.add_patch(patches.Ellipse((x_oeil - 1.5, y_oeil), 7, 10, facecolor="#3b82f6", edgecolor="#1e3a8a", zorder=5))
    ax.add_patch(patches.Ellipse((x_oeil - 1.5, y_oeil), 3, 6, facecolor="black", edgecolor="black", zorder=5))

    grossissement = f1_brute / f2_brute
    st.session_state.opt8_txt_panneau_bas = (
        f"• Focale Objectif f'1 = {f1_brute:.1f} cm\n"
        f"• Focale Oculaire |f'2| = {f2_brute:.1f} cm\n"
        f"• Grossissement G = {grossissement:.2f} (Image Droite)\n"
        f"• Distance O1O2 = {x_ocu - x_obj:.1f} cm"
    )

    ax.text(20, 20, "INSTRUMENTATION : LUNETTE AFOCALE DE GALILÉE", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    return fig


def dessiner_lunette_astronomique_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    echelle_x = 3.5
    w = 680
    h = 260
    y0 = h / 2.0  

    fig, ax = plt.subplots(figsize=(10, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    f1_brute = st.session_state.get("slide_lnt_f1", 80.0)
    f2_brute = st.session_state.get("slide_lnt_f2", 30.0)
    h_inc = st.session_state.get("slide_lnt_inc", 20.0)

    angle_theta = h_inc / 100.0  
    taille_image_interm_cm = f1_brute * angle_theta
    h_image_dessin = taille_image_interm_cm * echelle_x

    f1 = f1_brute * echelle_x
    f2 = f2_brute * echelle_x

    x_obj = 100.0                  
    x_ocu = x_obj + f1 + f2       
    xf_commun = x_obj + f1        

    xf1 = x_obj - f1       
    xf_prime2 = x_ocu + f2 

    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5, zorder=1)
    ax.text(w - 25, y0 + 14, "Axe", color="#64748b", fontsize=7, style="italic", ha="right")

    ax.plot([xf1, xf1], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf1, y0 + 16, "F1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")

    ax.plot([xf_commun, xf_commun], [y0 - 6, y0 + 6], color="white", lw=2, zorder=2)
    ax.text(xf_commun, y0 - 14, "F'1", color="#38bdf8", fontsize=7, fontweight="bold", ha="center")
    ax.text(xf_commun, y0 + 16, "F2", color="#38bdf8", fontsize=7, fontweight="bold", ha="center")

    ax.plot([xf_prime2, xf_prime2], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5, zorder=2)
    ax.text(xf_prime2, y0 + 16, "F'2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center")

    # L1 : Objectif avec coordonnées de flèches complètes
    ax.plot([x_obj, x_obj], [15, h - 15], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_obj - 6, x_obj, x_obj + 6], [23, 15, 23], color="#3b82f6", lw=2)
    ax.plot([x_obj - 6, x_obj, x_obj + 6], [h - 23, h - 15, h - 23], color="#3b82f6", lw=2)
    ax.text(x_obj - 12, y0 + 14, "O1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right")

    # L2 : Oculaire avec coordonnées de flèches complètes
    ax.plot([x_ocu, x_ocu], [40, h - 40], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [48, 40, 48], color="#3b82f6", lw=2)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [h - 48, h - 40, h - 48], color="#3b82f6", lw=2)
    ax.text(x_ocu + 12, y0 + 14, "O2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="left")

    pente_entree = h_inc / f1
    pente_output = h_image_dessin / f2
    x_fin_rayons = x_ocu + 120.0

    ax.annotate("", xy=(x_obj, y0), xytext=(15, y0 - (x_obj - 15) * pente_entree), arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5), zorder=4)
    y_impact_ocu_bleu = y0 + (x_ocu - x_obj) * (h_image_dessin / f1)
    ax.plot([x_obj, x_ocu], [y0, y_impact_ocu_bleu], color="#2563eb", lw=1.5, zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_bleu, y_impact_ocu_bleu - (x_fin_rayons - x_ocu) * pente_output], color="#2563eb", lw=1.5, zorder=4)

    y_impact_obj_jaune = y0 - h_image_dessin
    ax.annotate("", xy=(x_obj, y_impact_obj_jaune), xytext=(15, y_impact_obj_jaune - (x_obj - 15) * pente_entree), arrowprops=dict(arrowstyle="->", color="#eab308", lw=1.5), zorder=4)
    y_impact_ocu_jaune = y_impact_obj_jaune + (x_ocu - x_obj) * ((2.0 * h_image_dessin) / f1)
    ax.plot([x_obj, x_ocu], [y_impact_obj_jaune, y_impact_ocu_jaune], color="#eab308", lw=1.5, zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_ocu_jaune, y_impact_ocu_jaune - (x_fin_rayons - x_ocu) * pente_output], color="#eab308", lw=1.5, zorder=4)

    y_impact_obj_rose = y0 + h_image_dessin
    ax.annotate("", xy=(x_obj, y_impact_obj_rose), xytext=(15, y_impact_obj_rose + (15 - x_obj) * pente_entree), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=1.5), zorder=4)
    ax.plot([x_obj, x_ocu], [y_impact_obj_rose, y_impact_obj_rose], color="#ec4899", lw=1.5, zorder=4)
    ax.plot([x_ocu, x_fin_rayons], [y_impact_obj_rose, y_impact_obj_rose - (x_fin_rayons - x_ocu) * pente_output], color="#ec4899", lw=1.5, zorder=4)

    ax.annotate("", xy=(xf_commun, y0 + h_image_dessin), xytext=(xf_commun, y0), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2.5), zorder=5)
    ax.text(xf_commun - 12, y0 + (h_image_dessin / 2.0), "A1B1", color="#10b981", fontsize=7, fontweight="bold", ha="right", va="center")

    x_oeil = x_fin_rayons + 15.0
    y_oeil = y_impact_ocu_bleu - (x_fin_rayons - x_ocu) * pente_output

    arc_cornee = patches.Arc((x_oeil, y_oeil), 20, 28, angle=90, theta1=0, theta2=180, edgecolor="#cbd5e1", lw=2, zorder=5)
    ax.add_patch(arc_cornee)
    
    iris_oval = patches.Ellipse((x_oeil - 1.5, y_oeil), 7, 10, facecolor="#3b82f6", edgecolor="#1e3a8a", zorder=5)
    pupille_oval = patches.Ellipse((x_oeil - 1.5, y_oeil), 3, 6, facecolor="black", edgecolor="black", zorder=5)
    ax.add_patch(iris_oval)
    ax.add_patch(pupille_oval)

    ax.plot([x_oeil - 8, x_oeil - 12], [y_oeil - 12, y_oeil - 17], color="#cbd5e1", lw=1.2)
    ax.plot([x_oeil - 3, x_oeil - 5], [y_oeil - 14, y_oeil - 20], color="#cbd5e1", lw=1.2)
    ax.plot([x_oeil - 8, x_oeil - 12], [y_oeil + 12, y_oeil + 17], color="#cbd5e1", lw=1.2)
    ax.plot([x_oeil - 3, x_oeil - 5], [y_oeil + 14, y_oeil + 20], color="#cbd5e1", lw=1.2)

    grossissement = - (f1_brute / f2_brute)
    st.session_state.opt7_txt_panneau_bas = (
        f"• Focale Objectif f'1 = {f1_brute:.1f} cm\n"
        f"• Focale Oculaire f'2 = {f2_brute:.1f} cm\n"
        f"• Grossissement G = {grossissement:.2f}\n"
        f"• Taille Image Interm. = {taille_image_interm_cm:.1f} cm"
    )

    ax.text(20, 20, "INSTRUMENTATION : LUNETTE AFOCALE DE KEPLER", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    return fig
   
    
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
            key="btn_validation_identite_maitre",
            disabled=st.session_state.get("verrouille", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("verrouille", False):
                st.rerun()

                
def valider_session():
    nom = st.session_state.nom_var.strip()
    prenom = st.session_state.prenom_var.strip()
    groupe = st.session_state.classe_var.strip()  # Correspond à votre champ groupe/classe

    if not nom or not prenom or not groupe:
        st.warning(
            "Identification incomplète : Veuillez remplir l'ensemble des champs avant de commencer vos manipulations."
        )
    else:
        st.session_state.verrouille = True
        st.success(
            f"Session Ouverte : Bienvenue {prenom} {nom}.\nVotre session de TP pour le groupe {groupe} est désormais active."
        )



with tab1:
    st.subheader("L'histoire des appareils optique")

with tab2:
    st.subheader("La loupe")

with tab3:
    st.subheader("La lunette astronomique")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel du Modele de la Lunette Afocale :</p>
        <ul>
            <li><strong>Configuration afocale :</strong> La distance entre les deux lentilles est egale a la somme de leurs distances focales ($d = O_1O_2 = f'_1 + f'_2$).</li>
            <li><strong>Grossissement de l'instrument :</strong> Le grossissement nominal se calcule par la relation $G = \\frac{f'_1}{f'_2}$.</li>
            <li><strong>Confort visuel :</strong> L'image finale sortant de l'oculaire est rejetee a l'infini, permettant a l'oeil du marin ou de l'astronome d'observer l'astre sans aucune fatigue (pas d'accommodation).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt7_verrouille" not in st.session_state: st.session_state.opt7_verrouille = False

    # =========================================================================
    # ARCHITECTURE DOUBLE COLONNE : COMMANDES LAB / VISUALISATION GRAPHIQUE
    # =========================================================================
    col_g_kepler, col_d_kepler = st.columns([1.2, 2.2])

    # --- PANNEAU DE GAUCHE : PARAMÈTRES ET CONSOLE DE CALCULS ---
    with col_g_kepler:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>PARAMETRES DE LA LUNETTE</p>", unsafe_allow_html=True)
            
            # Récupération de vos trois curseurs d'origines convertis en réglettes web
            f_obj = st.slider("Focale Objectif f'1 (cm) :", min_value=1.0, max_value=110.0, value=80.0, step=1.0, key="slide_lnt_f1", disabled=st.session_state.opt7_verrouille)
            f_ocu = st.slider("Focale Oculaire f'2 (cm) :", min_value=1.0, max_value=100.0, value=30.0, step=1.0, key="slide_lnt_f2", disabled=st.session_state.opt7_verrouille)
            inc_rayons = st.slider("Inclinaison des rayons (cm) :", min_value=-100.0, max_value=100.0, value=20.0, step=1.0, key="slide_lnt_inc", disabled=st.session_state.opt7_verrouille)

        # PANNEAU DE RAPPORTS (CONVERTION DU CADRE JAUNE D'ORIGINE DE GAUCHE72)
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>RAPPORT D'ANALYSE OPTIQUE</p>", unsafe_allow_html=True)
            
            # Moteur mathématique de session synchrone
            try:
                grossissement = - (f_obj / f_ocu)
                distance_lentilles = f_obj + f_ocu
            except:
                grossissement = 0.0
                distance_lentilles = 0.0

            txt_kepler = (
                f"Lunette Astronomique :\n"
                f"• Grossissement G = {grossissement:.2f}\n"
                f"• Distance O1O2 = {distance_lentilles:.1f} cm\n"
                f"• Systeme Afocal : Verifie\n"
                f"• Nature : Image Inversee"
            )
            st.text(txt_kepler)

    # --- PANNEAU DE DROITE : ESPACE GRAPHIQUE POUR LA MARCHE DES RAYONS ---
    with col_d_kepler:
        st.subheader("Marche des faisceaux lumineux dans l'instrument")
        
        # RECONNEXION SUR LA FONCTION MAÎTRESSE CORRIGÉE SANS AUCUN EMOJI
        fig_lunette_kepler = dessiner_lunette_astronomique_matplotlib()
        st.pyplot(fig_lunette_kepler, use_container_width=True)

        # Optionnel : Ajout de la boite de donnees techniques sous la lunette
        st.info(st.session_state.get("opt7_txt_panneau_bas", "Ajustez les curseurs pour initialiser la marche des faisceaux."))
    # =========================================================================
    # SEPLOYEMENT DES QUESTIONNAIRES ET DU SCELLE DE FIN DE L'ATELIER 7
    # =========================================================================
    st.write("---")
    dict_q7, dict_t7 = afficher_questions_optique7(verrouille=st.session_state.get("opt7_verrouille", False))

    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION AUTOMATIQUE SUR 20 POINTS
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 7")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt7 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 7.", 
        key="check_certif_opt7_officiel_20pts", 
        disabled=st.session_state.get("opt7_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_opt7_official_20pts", use_container_width=True, disabled=st.session_state.get("opt7_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt7: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Moteur de correction automatique du Quiz (Partie 1)
            attendus_qo7_v = {
                "q1": "Objectif (de grande distance focale)", "q2": "Oculaire", 
                "q3": "A l'infini (confort de vision sans fatigue pour l'oeil)", 
                "q4": "Le foyer objet F2 de l'oculaire", "q5": "Reelle et renversee (situee dans le plan focal commun)", 
                "q6": "A l'infini (pas besoin d'accommoder)", "q7": "G = f'1 / f'2", 
                "q8": "20", "q9": "Renversee (haut-bas et droite-gauche)", "q10": "L'objectif par l'oculaire"
            }
            score_quiz_opt7 = sum([1.0 for qk, qv in attendus_qo7_v.items() if st.session_state.get(f"col_g_quiz_opt7_{qk}") == qv])

            # Moteur de correction automatique du Texte a trous (Partie 2)
            score_trous_opt7 = 0.0
            if st.session_state.get("opt7_t1") == "Objectif": score_trous_opt7 += 2.5
            if st.session_state.get("opt7_t2") == "Oculaire": score_trous_opt7 += 2.5
            if st.session_state.get("opt7_t3") == "Afocal": score_trous_opt7 += 2.5
            if st.session_state.get("opt7_t4") == "Grossissement": score_trous_opt7 += 2.5

            st.session_state.score_opt7_p1 = round(score_quiz_opt7, 1)
            st.session_state.score_opt7_p2 = round(score_trous_opt7, 1)
            st.session_state.score_final_opt7 = round(score_quiz_opt7 + score_trous_opt7, 1)
            st.session_state.opt7_verrouille = True
            st.rerun()

    # BLOC PERMANENT D'EXPORTATION DU BILAN HTML APRÈS VERROUILLAGE
    if st.session_state.get("opt7_verrouille", False):
        scr1 = st.session_state.get("score_opt7_p1", 0.0)
        scr2 = st.session_state.get("score_opt7_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt7", 0.0)

        from datetime import timedelta
        from datetime import datetime
        timestamp_opt7 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 7 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo7_v = {
            "q1": "Objectif (de grande distance focale)", "q2": "Oculaire", 
            "q3": "A l'infini (confort de vision sans fatigue pour l'oeil)", 
            "q4": "Le foyer objet F2 de l'oculaire", "q5": "Reelle et renversee (situee dans le plan focal commun)", 
            "q6": "A l'infini (pas besoin d'accommoder)", "q7": "G = f'1 / f'2", 
            "q8": "20", "q9": "Renversee (haut-bas et droite-gauche)", "q10": "L'objectif par l'oculaire"
        }
        attendus_to7_v = {"t1": "Objectif", "t2": "Oculaire", "t3": "Afocal", "t4": "Grossissement"}

        html_export_opt7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 7 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}

                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 7</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 4 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LA LUNETTE KEPLERIENNE (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">N°</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo7_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt7_{q_id}", "Choisir...")
            attendu = attendus_qo7_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS (TEXTE A TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">N°</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_t, (t_key, t_val) in enumerate(attendus_to7_v.items(), 1):
            saisie = st.session_state.get(f"opt7_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique7_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 7 SUR VOTRE ORDINATEUR",
            data=html_export_opt7,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )
        
with tab4:
    st.subheader("La lunette de Galilée")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel du Modele de la Lunette de Galilee :</p>
        <ul>
            <li><strong>Association Optique :</strong> Elle associe un <strong>objectif convergent</strong> ($f'_1 > 0$) et un <strong>oculaire divergent</strong> ($f'_2 < 0$).</li>
            <li><strong>Condition Afocale :</strong> Le foyer image de l'objectif et le foyer objet de l'oculaire sont confondus ($F'_1 = F_2$). La distance separent les verres est reduite : $d = f'_1 - |f'_2|$.</li>
            <li><strong>Propriete d'image :</strong> Contrairement au systeme de Kepler, la lunette de Galilee fournit une <strong>image finale droite</strong> (redressee, dans le meme sens que l'objet).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt8_verrouille" not in st.session_state: 
        st.session_state.opt8_verrouille = False

    # =========================================================================
    # ARCHITECTURE DOUBLE COLONNE : INTERFACE / SCHÉMA TECHNIQUE
    # =========================================================================
    col_g_galilee, col_d_galilee = st.columns([1.2, 2.2])

    # --- PANNEAU DE GAUCHE : PARAMÈTRES ET RAPPORTS DE CALCULS ---
    with col_g_galilee:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>PARAMETRES GALILEE</p>", unsafe_allow_html=True)
            
            # Curseurs web connectes au session_state
            f1_gal = st.slider("Focale Objectif f'1 (cm) :", min_value=1.0, max_value=100.0, value=80.0, step=1.0, key="slide_gal_f1", disabled=st.session_state.opt8_verrouille)
            f2_gal_abs = st.slider("Focale Oculaire |f'2| (cm) :", min_value=1.0, max_value=100.0, value=30.0, step=1.0, key="slide_gal_f2_abs", disabled=st.session_state.opt8_verrouille)
            inc_rayons_gal = st.slider("Inclinaison des rayons (cm) : ", min_value=-50.0, max_value=50.0, value=20.0, step=1.0, key="slide_gal_inc", disabled=st.session_state.opt8_verrouille)

            # Forcage de la valeur negative de l'oculaire pour le moteur physique
            st.session_state.slide_gal_f2 = - float(f2_gal_abs)

        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>RAPPORT D'ANALYSE OPTIQUE</p>", unsafe_allow_html=True)
            
            try:
                grossissement_g = - (f1_gal / (-f2_gal_abs))
                dist_g = f1_gal - f2_gal_abs
            except:
                grossissement_g = 0.0
                dist_g = 0.0

            txt_panneau_galilee = (
                f"Lunette de Galilee :\n"
                f"• Grossissement G = {grossissement_g:.2f}\n"
                f"• Distance O1O2 = {dist_g:.1f} cm\n"
                f"• Systeme Afocal : Verifie\n"
                f"• Image Finale : Droite"
            )
            st.text(txt_panneau_galilee)

    # --- PANNEAU DE DROITE : TRACÉ DU SCHÉMA DE DE DE LA LUNETTE ---
    with col_d_galilee:
        st.subheader("Banc d'optique virtuel")
        
        # Appel synchrone de la figure Matplotlib de Galilee creee au morceau 2
        fig_lunette_galilee = dessiner_lunette_galilee_matplotlib()
        st.pyplot(fig_lunette_galilee, use_container_width=True)
        
        st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        st.info(st.session_state.get("opt8_txt_panneau_bas", "Ajustez les sliders pour tracer la trajectoire."))

    # =========================================================================
    # DEPLOYEMENT EN LIT DE PAGE DU QUIZ ET DU TEXTE A TROUS
    # =========================================================================
    st.write("---")
    dict_q8, dict_t8 = afficher_questions_optique8(verrouille=st.session_state.get("opt8_verrouille", False))

    # =========================================================================
    # ZONE DE CALCUL DE NOTE ET PRODUCTION DU RAPPORT HTML
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 8")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt8 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 8.", 
        key="check_certif_opt8_officiel_20pts", 
        disabled=st.session_state.get("opt8_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8", key="btn_export_opt8_official_20pts", use_container_width=True, disabled=st.session_state.get("opt8_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt8: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Correction Automatique de la Partie 1
            attendus_qo8_v = {
                "q1": "L'oculaire de Galilee est une lentille divergente", "q2": "Strictement negative (f'2 < 0)", 
                "q3": "Le foyer objet F2 de l'oculaire divergent", "q4": "Droite (dans le meme sens que l'astre)", 
                "q5": "f'1 + f'2 (ce qui donne une soustraction car f'2 est negatif)", "q6": "Plus courte que celle de Kepler", 
                "q7": "Positif (l'image finale est droite)", "q8": "4.0 (car f'2 est negatif)", 
                "q9": "Un champ visuel tres etroit", "q10": "Les jumelles de theatre (ou de spectacle)"
            }
            score_quiz_opt8 = sum([1.0 for qk, qv in attendus_qo8_v.items() if st.session_state.get(f"col_g_quiz_opt8_{qk}") == qv])

            # Correction Automatique de la Partie 2
            score_trous_opt8 = 0.0
            if st.session_state.get("opt8_t1") == "Divergente": score_trous_opt8 += 3.33
            if st.session_state.get("opt8_t2") == "Objet F2": score_trous_opt8 += 3.33
            if st.session_state.get("opt8_t3") == "Droite": score_trous_opt8 += 3.34

            st.session_state.score_opt8_p1 = round(score_quiz_opt8, 1)
            st.session_state.score_opt8_p2 = round(min(10.0, score_trous_opt8), 1)
            st.session_state.score_final_opt8 = round(score_quiz_opt8 + min(10.0, score_trous_opt8), 1)
            st.session_state.opt8_verrouille = True
            st.rerun()

    if st.session_state.get("opt8_verrouille", False):
        scr1 = st.session_state.get("score_opt8_p1", 0.0)
        scr2 = st.session_state.get("score_opt8_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt8", 0.0)

        from datetime import timedelta
        from datetime import datetime
        timestamp_opt8 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 8 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo8_v = {
            "q1": "L'oculaire de Galilee est une lentille divergente", "q2": "Strictement negative (f'2 < 0)", 
            "q3": "Le foyer objet F2 de l'oculaire divergent", "q4": "Droite (dans le meme sens que l'astre)", 
            "q5": "f'1 + f'2 (ce qui donne une soustraction car f'2 est negatif)", "q6": "Plus courte que celle de Kepler", 
            "q7": "Positif (l'image finale est droite)", "q8": "4.0 (car f'2 est negatif)", 
            "q9": "Un champ visuel tres etroit", "q10": "Les jumelles de theatre (ou de spectacle)"
        }
        attendus_to8_v = {"t1": "Divergente", "t2": "Objet F2", "t3": "Droite"}

        html_export_opt8 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 8 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 8</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ LUNETTE GALILÉENNE (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">N°</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo8_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt8_{q_id}", "Choisir...")
            attendu = attendus_qo8_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS (TEXTE A TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">N°</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_t, (t_key, t_val) in enumerate(attendus_to8_v.items(), 1):
            saisie = st.session_state.get(f"opt8_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique8_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 8 SUR VOTRE ORDINATEUR",
            data=html_export_opt8,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )

        
with tab5:
    st.header("Le microscope")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel du Modele Optique du Microscope :</p>
        <ul>
            <li><strong>Grandissement de l'objectif (L1) :</strong> $\\gamma_1 = - \\frac{\\Delta}{f'_1}$ &nbsp;(avec $\\Delta$ l'intervalle optique entre $F'_1$ et $F_2$).</li>
            <li><strong>Grossissement de l'oculaire (L2) :</strong> $G_{c2} = \\frac{0.25}{f'_2}$ &nbsp;(avec distance minimale de visee standard a $25\\text{ cm}$).</li>
            <li><strong>Grossissement total de l'instrument :</strong> $G = \\gamma_1 \\cdot G_{c2} = - \\frac{\\Delta \\cdot 0.25}{f'_1 \\cdot f'_2}$.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt9_verrouille" not in st.session_state: st.session_state.opt9_verrouille = False

    # Architecture double colonne
    col_g_mic, col_d_mic = st.columns([1.2, 2.2])

    # --- PANNEAU DE GAUCHE : INTERFACE DE COMMANDE DE LA TOURELLE ---
    with col_g_mic:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:2px;'>PARAMETRES DU MICROSCOPE</p>", unsafe_allow_html=True)
            
            # Reconversion des Radiobuttons de la tourelle
            st.radio("Objectif choisi (Tourelle) :", ["X4", "X10", "X40", "X100"], index=1, key="var_choix_objectif", disabled=st.session_state.opt9_verrouille)
            
            # Curseurs physiques d'origines (DoubleVar)
            st.slider("1. Taille Objet AB (mm) :", min_value=5.0, max_value=25.0, value=15.0, step=0.5, key="slide_mic_ab", disabled=st.session_state.opt9_verrouille)
            st.slider("2. Position Objet A (cm) :", min_value=5.0, max_value=55.0, value=42.0, step=0.1, key="slide_mic_xa", disabled=st.session_state.opt9_verrouille)
            st.slider("3. Focale Oculaire f'2 (mm) :", min_value=20.0, max_value=60.0, value=40.0, step=1.0, key="slide_mic_f2", disabled=st.session_state.opt9_verrouille)
            st.slider("4. Longueur du tube (pixels) :", min_value=240.0, max_value=420.0, value=320.0, step=5.0, key="slide_mic_tube", disabled=st.session_state.opt9_verrouille)

            # Matrices de choix d'echelles X et Y d'origines
            st.write("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
            st.radio("Echelle selon X :", ["1", "0.1", "0.01", "0.001", "0.0001"], index=0, key="var_echelle_x_choix", horizontal=True, disabled=st.session_state.opt9_verrouille)
            st.radio("Echelle selon Y :", ["1", "0.1", "0.01", "0.001", "0.0001"], index=0, key="var_echelle_y_choix", horizontal=True, disabled=st.session_state.opt9_verrouille)

        # CADRAN DE RÉSULTATS DYNAMIQUE (CONVERSION DU CADRE DE GAUCHE92)
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>CADRAN DE RESULTATS</p>", unsafe_allow_html=True)
            
            # Matrice de calcul synchrone lue par le session_state
            obj_factor = st.session_state.get("var_choix_objectif", "X10")
            f1_val = 40.0 if obj_factor == "X4" else (16.0 if obj_factor == "X10" else (4.0 if obj_factor == "X40" else 1.6))
            delta_tube = st.session_state.get("slide_mic_tube", 320.0)
            f2_val = st.session_state.get("slide_mic_f2", 40.0)
            
            try:
                gamma1 = - (delta_tube / f1_val)
                gc2 = 250.0 / f2_val
                g_total = gamma1 * gc2
            except:
                gamma1 = gc2 = g_total = 0.0

            txt_microscope = (
                f"Microscope Compose ({obj_factor}) :\n"
                f"• Focale Objectif f'1 = {f1_val:.1f} mm\n"
                f"• Intervalle Optique = {delta_tube:.1f} px\n"
                f"• Grandissement Obj. = {gamma1:.2f}\n"
                f"• Grossissement Ocu.  = {gc2:.2f}\n"
                f"• Grossissement Total = {g_total:.2f}\n"
                f"• Image Definitive    = Inversee"
            )
            st.text(txt_microscope)

    # --- PANNEAU DE DROITE : SÉQUENTIEL GRAPHISQUE ---
    with col_d_mic:
        st.subheader("Marche des rayons et formation de l'image intermediaire")
        
        # APPEL ET RENDU DE LA GRAPHISQUE VECTORIELLE DU MICROSCOPE SANS EMOJI
        fig_microscope = dessiner_microscope_matplotlib()
        st.pyplot(fig_microscope, use_container_width=True)

        st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        st.info(st.session_state.get("opt9_txt_panneau_bas", "Ajustez les sliders pour tracer la trajectoire."))
    # =========================================================================
    # INJECTION DES QUESTIONNAIRES ET PROCESSUS DE NOTATION FINALE SUR 20 PTS
    # =========================================================================
    st.write("---")
    dict_q9, dict_t9 = afficher_questions_optique9(verrouille=st.session_state.get("opt9_verrouille", False))

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 9")

    case_certif_opt9 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 9.", 
        key="check_certif_opt9_officiel_20pts", 
        disabled=st.session_state.get("opt9_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9", key="btn_export_opt9_official_20pts", use_container_width=True, disabled=st.session_state.get("opt9_verrouille", False)):
        if not st.session_state.get("verrouille", False): st.error("Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt9: st.error("Cochez la case de certification.")
        else:
            attendus_qo9_v = {
                "q1": "Objectif (de tres courte distance focale)", "q2": "Oculaire", "q3": "Reelle, renversee et tres agrandie",
                "q4": "Pile sur le foyer objet F2 de l'oculaire", "q5": "Le foyer image F'1 de l'objectif et le foyer objet F2 de l'oculaire",
                "q6": "gamma1 = - delta / f'1", "q7": "Gc2 = 0.25 / f'2", "q8": "Du grandissement de l'objectif par le grossissement de l'oculaire",
                "q9": "-40 (l'image est inversee et 40 fois plus grande)", "q10": "Inversee et virtuelle"
            }
            score_quiz_opt9 = sum([1.0 for qk, qv in attendus_qo9_v.items() if st.session_state.get(f"col_g_quiz_opt9_{qk}") == qv])

            score_trous_opt9 = 0.0
            if st.session_state.get("opt9_t1") == "Objectif": score_trous_opt9 += 3.33
            if st.session_state.get("opt9_t2") == "Oculaire": score_trous_opt9 += 3.33
            if st.session_state.get("opt9_t3") == "Optique": score_trous_opt9 += 3.34

            st.session_state.score_opt9_p1 = round(score_quiz_opt9, 1)
            st.session_state.score_opt9_p2 = round(min(10.0, score_trous_opt9), 1)
            st.session_state.score_final_opt9 = round(score_quiz_opt9 + min(10.0, score_trous_opt9), 1)
            st.session_state.opt9_verrouille = True
            st.rerun()

with tab6:
    st.subheader("L'appareil photographique")
    
with tab7:
    st.subheader("Application le domaine de la maintenance")

with tab8:
    st.subheader("Application le domaine  les travaux publics")

with tab9:
    st.subheader("Application le domaine du transport routier")

with tab10:
    st.subheader("Application le domaine  géomètre topographe")
