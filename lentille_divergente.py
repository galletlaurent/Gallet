# -*- coding: utf-8 -*-

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Application lentille divergente ",
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

st.title("Application lentille divergente")
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
    " Historique",
    " Les lenitlles divergentes : définition et régles de tracé des rayons",
    " Les lentilles divergentes",
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

def afficher_questions_optique6(verrouille=False):
    col_double_quiz_opt6, col_double_trous_opt6 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES SUR LES LENTILLES DIVERGENTES ---
    with col_double_quiz_opt6:
        st.markdown("##### Quiz sur les lentilles divergentes (10 questions) - Optique 6 (10 pts)")
        if "ordre_questions_opt6" not in st.session_state:
            questions_opt6_base = [
                ("q1", "D'un point de vue geometrique, une lentille mince est qualifiee de divergente si ses bords sont :"),
                ("q2", "Le symbole d'une lentille divergente sur un schema optique est represente par :"),
                ("q3", "La distance focale f' d'une lentille divergente est une grandeur physique :"),
                ("q4", "Par consequent, la vergence C d'une lentille divergente s'exprime par une valeur :"),
                ("q5", "Un rayon incident parallele a l'axe optique ressort de la lentille divergente en semblant provenir de :"),
                ("q6", "Un rayon incident dont le prolongement passe par le foyer objet F ressort de la lentille :"),
                ("q7", "Pour un objet reel AB place avant la lentille divergente, l'image A'B' obtenue est toujours :"),
                ("q8", "Le grandissement gamma pour une lentille divergente avec un objet reel est toujours :"),
                ("q9", "Si une lentille divergente a une distance focale f' = -50 cm, sa vergence C vaut :"),
                ("q10", "Dans la relation de conjugaison de Descartes, la formule reste-t-elle identique a celle des convergentes :")
            ]
            import random
            random.shuffle(questions_opt6_base)
            st.session_state.ordre_questions_opt6 = questions_opt6_base

        dict_quiz_opt6 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt6, 1):
            cle_qo6 = f"col_g_quiz_opt6_{q_id}"
            cle_opts_unique = f"opts_opt6_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Plus epais que son centre", "Plus minces que son centre", "Rigoureusement plats"]
                elif q_id == "q2": copie_opts = ["Une fleche double retournee (pointes vers le centre)", "Une fleche double standard", "Un trait vertical simple"]
                elif q_id == "q3": copie_opts = ["Toujours negative (f' < 0)", "Toujours positive (f' > 0)", "Nulle"]
                elif q_id == "q4": copie_opts = ["Negative (en dioptries)", "Positive (en dioptries)", "Variable selon la position"]
                elif q_id == "q5": copie_opts = ["Le foyer image virtuel F' situe en amont", "Le foyer objet virtuel F situe en aval", "Le centre optique O"]
                elif q_id == "q6": copie_opts = ["Parallele a l'axe optique", "En passant par le foyer image F'", "Sans aucune deviation"]
                elif q_id == "q7": copie_opts = ["Virtuelle, droite et plus petite", "Reelle, renversee et plus grande", "Virtuelle, renversee et plus petite"]
                elif q_id == "q8": copie_opts = ["Positif et inferieur a 1 (0 < g < 1)", "Negatif", "Superieur a 1"]
                elif q_id == "q9": copie_opts = ["-2.00 δ", "+2.00 δ", "-0.02 δ"]
                elif q_id == "q10": copie_opts = ["Oui, ce sont les valeurs numeriques de f' et x qui changent de signe", "Non, la formule devient 1/x' + 1/x = -1/f'", "Non, les inverses deviennent des carres"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo6, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt6[f"{q_id}_opt6"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo6, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE DES LENTILLES DIVERGENTES ---
    with col_double_trous_opt6:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 6 (10 pts)")
        
        co6_1, co6_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co6_1: st.write("Une lentille mince possede des bords plus epais que son centre. Elle est qualifiee de")
        with co6_2: t1 = st.selectbox("", ["Choisir...", "Divergente", "Convergente", "Plane"], key="opt6_t1", disabled=verrouille, label_visibility="collapsed")
        
        co6_3, co6_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co6_3: st.write("Sa distance focale f' et sa vergence C ont la particularite d'etre de signe")
        with co6_4: t2 = st.selectbox("", ["Choisir...", "Negatif", "Positif", "Neutre"], key="opt6_t2", disabled=verrouille, label_visibility="collapsed")

        co6_5, co6_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co6_5: st.write("Un rayon incident parallele a l'axe ressort en s'eloignant de celui-ci : son prolongement passe par le foyer")
        with co6_6: t3 = st.selectbox("", ["Choisir...", "Image F'", "Objet F", "Central O"], key="opt6_t3", disabled=verrouille, label_visibility="collapsed")

        co6_7, co6_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co6_7: st.write("Pour un objet reel, la fleche de l'image obtenue est toujours droite, plus petite et de nature")
        with co6_8: t4 = st.selectbox("", ["Choisir...", "Virtuelle", "Reelle", "Infinie"], key="opt6_t4", disabled=verrouille, label_visibility="collapsed")

        dict_trous_opt6 = {
            "t1_opt6": t1, "t2_opt6": t2, "t3_opt6": t3, "t4_opt6": t4
        }

    return dict_quiz_opt6, dict_trous_opt6

def mettre_a_jour_graphique_lentille_divergente_matplotlib():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(-0.06, 0.06)
    ax.set_ylim(-0.06, 0.06)

    ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
    ax.axhline(0, color="#cbd5e1", lw=1)
    ax.axvline(0, color="#cbd5e1", lw=1)
    
    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)

    ax.set_xlabel("1/x (cm^-1)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_ylabel("1/x' (cm^-1)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_title("Relation de Descartes Divergente : 1/x' = f(1/x)", color="#38bdf8", fontsize=8, style="italic")

    m_inv_x = st.session_state.get("mesures_inv_x2", [])
    m_inv_xp = st.session_state.get("mesures_inv_xprime2", [])
    
    if m_inv_x:
        ax.scatter(m_inv_x, m_inv_xp, color="#10b981", marker="x", s=50, lw=2, zorder=5)

    return fig


def mettre_a_jour_lentille_divergente_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    w, h = 1500, 280
    x0, y0 = 750.0, 140.0  

    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(15, w - 15)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    x_obj = st.session_state.get("slide_len2_x", -80.0)
    f_prime = st.session_state.get("slide_len2_f", -100.0) # Valeur negative pour une divergente
    h_obj = st.session_state.get("slide_len2_ab", 40.0)
    
    xa = x0 + x_obj                          
    xf = x0 - f_prime  # Foyer objet réel (a droite, valeur positive apres soustraction)
    xf_prime = x0 + f_prime  # Foyer image virtuel (a gauche, valeur negative)

    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5)
    ax.text(w - 25, y0 + 14, "Axe optique", color="#64748b", fontsize=7, style="italic", ha="right")

    # REPARATION DES FLÈCHES DE LA LENTILLE DIVERGENTE (FLECHES VERS L'INTÉRIEUR)
    ax.plot([x0, x0], [20, h - 20], color="#3b82f6", lw=3)
    
    # Flèche inversée tout en haut (pointant vers le centre)
    ax.plot([x0 - 10, x0, x0 + 10], [10, 25, 10], color="#3b82f6", lw=3)
    
    # Flèche inversée tout en bas (pointant vers le centre)
    ax.plot([x0 - 10, x0, x0 + 10], [h - 10, h - 25, h - 10], color="#3b82f6", lw=3)
    
    ax.text(x0 + 15, 25, "Lentille Divergente (L)", color="#38bdf8", fontsize=8, fontweight="bold", ha="left")
    ax.text(x0 - 12, y0 + 14, "O", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right")

    ax.plot([xf, xf], [y0 - 5, y0 + 5], color="#cbd5e1", lw=2)
    ax.text(xf, y0 + 14, "F", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")
    ax.plot([xf_prime, xf_prime], [y0 - 5, y0 + 5], color="#cbd5e1", lw=2)
    ax.text(xf_prime, y0 + 14, "F'", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

    ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
    ax.text(xa + 8, y0 + 14, "A", color="#ef4444", fontsize=8, fontweight="bold")
    ax.text(xa + 8, y0 - h_obj - 6, "B", color="#ef4444", fontsize=8, fontweight="bold")

    denominateur = x_obj + f_prime
    vergence_c_box = 100.0 / f_prime

    chk_b = st.session_state.get("chk_rayon2_bleu", True)
    chk_j = st.session_state.get("chk_rayon2_jaune", True)
    chk_r = st.session_state.get("chk_rayon2_rose", True)
    chk_img = st.session_state.get("chk_afficher_image2_verte", True)

    x_image = (f_prime * x_obj) / denominateur
    grandissement = x_image / x_obj
    h_image = h_obj * grandissement
    xa_prime = x0 + x_image
    taille_image_cm = abs(h_obj * grandissement)

    msg_lentille = "IMAGE VIRTUELLE : En amont (droite et plus petite)."
    couleur_msg = "#38bdf8"
    couleur_image = "#a855f7"

    # 1. RAYON CENTRAL (Bleu)
    if chk_b:
        ax.plot([xa, x0], [y0 - h_obj, y0], color="#2563eb", lw=1.5)
        ax.plot([x0, w - 40], [y0, y0 + (w - 40 - x0) * (y0 - (y0 - h_obj)) / (x0 - xa)], color="#2563eb", lw=1.5)

    # 2. RAYON PARALLÈLE REPARÉ (Jaune) : Arrive horizontal, diverge aligne sur F'
    if chk_j:
        ax.plot([xa, x0], [y0 - h_obj, y0 - h_obj], color="#eab308", lw=1.5)
        # Calcul de la pente divergente reelle a partir du foyer image virtuel F'
        pente_j = (y0 - h_obj - y0) / (x0 - xf_prime)
        x_end_j = w - 20
        y_end_j = y0 - h_obj + (x_end_j - x0) * pente_j
        ax.plot([x0, x_end_j], [y0 - h_obj, y_end_j], color="#eab308", lw=1.5)
        ax.plot([x0, xf_prime], [y0 - h_obj, y0], color="#eab308", lw=1.5, linestyle="--")

    # 3. RAYON FOCAL REPARÉ (Rose) : Vise F, ressort horizontalement parallele
    if chk_r:
        pente_r = (y0 - (y0 - h_obj)) / (xf - xa)
        h_impact_r = y0 - h_obj + (x0 - xa) * pente_r
        ax.plot([xa, x0], [y0 - h_obj, h_impact_r], color="#ec4899", lw=1.5)
        ax.plot([x0, w - 20], [h_impact_r, h_impact_r], color="#ec4899", lw=1.5)
        ax.plot([x0, xf], [h_impact_r, y0], color="#ec4899", lw=1.5, linestyle="--")
        ax.plot([x0, xa_prime], [h_impact_r, h_impact_r], color="#ec4899", lw=1.5, linestyle="--")

    if chk_img:
        ax.annotate("", xy=(xa_prime, y0 - h_image), xytext=(xa_prime, y0), arrowprops=dict(arrowstyle="->", color=couleur_image, lw=2.5))
        ax.text(xa_prime + 8, y0 + 14, "A'", color=couleur_image, fontsize=7, fontweight="bold")
        ax.text(xa_prime + 8, y0 - h_image - 6, "B'", color=couleur_image, fontsize=7, fontweight="bold")

    txt_box_lentille = (
        f"Lentille Divergente :\n"
        f"• Objet x = {x_obj:.1f} cm\n"
        f"• Taille AB = {h_obj:.1f} cm\n"
        f"• Focale f' = {f_prime:.1f} cm\n"
        f"• Image x' = {x_image:.1f} cm\n"
        f"• Taille A'B' = {taille_image_cm:.1f} cm\n"
        f"• Vergence C = {vergence_c_box:.2f} δ\n"
        f"• Grandissement g = {grandissement:.2f}"
    )

    ax.text(20, 20, "OPTIQUE : LENTILLES MINCES DIVERGENTES", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(20, 35, msg_lentille, color=couleur_msg, fontsize=7, fontweight="bold", ha="left")

    st.session_state.opt6_txt_box_lentille = txt_box_lentille
    return fig

def ajouter_mesure_lentille_divergente_streamlit():
    import math
    x_obj = st.session_state.get("slide_len2_x", -80.0)
    f_prime = st.session_state.get("slide_len2_f", -100.0)
    
    denom = x_obj + f_prime
    if abs(denom) < 0.01:
        return 

    x_image = (f_prime * x_obj) / denom

    inv_x = 1.0 / x_obj
    inv_xprime = 1.0 / x_image
    inv_fpcalcul = inv_xprime - inv_x

    if "mesures_inv_x2" not in st.session_state: st.session_state.mesures_inv_x2 = []
    if "mesures_inv_xprime2" not in st.session_state: st.session_state.mesures_inv_xprime2 = []
    
    st.session_state.mesures_inv_x2.append(round(inv_x, 4))
    st.session_state.mesures_inv_xprime2.append(round(inv_xprime, 4))

def reinitialiser_mesures_lentille_divergente_streamlit():
    st.session_state.mesures_inv_x2 = []
    st.session_state.mesures_inv_xprime2 = []


def mettre_a_jour_graphique_lentille_matplotlib():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(-0.06, 0.06)
    ax.set_ylim(-0.06, 0.06)

    ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
    ax.axhline(0, color="#cbd5e1", lw=1)
    ax.axvline(0, color="#cbd5e1", lw=1)
    
    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)

    ax.set_xlabel("1/x (cm^-1)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_ylabel("1/x' (cm^-1)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_title("Relation de Descartes : 1/x' = f(1/x)", color="#38bdf8", fontsize=8, style="italic")

    m_inv_x = st.session_state.get("mesures_inv_x", [])
    m_inv_xp = st.session_state.get("mesures_inv_xprime", [])
    
    if m_inv_x:
        ax.scatter(m_inv_x, m_inv_xp, color="#10b981", marker="x", s=50, lw=2, zorder=5)

    return fig

def mettre_a_jour_lentille_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    w, h = 1500, 280
    x0, y0 = 750.0, 140.0  

    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(15, w - 15)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    x_obj = st.session_state.get("slide_len_x", -80.0)
    f_prime = st.session_state.get("slide_len_f", 50.0)
    h_obj = st.session_state.get("slide_len_ab", 40.0)
    
    xa = x0 + x_obj                          
    xf = x0 - f_prime                        
    xf_prime = x0 + f_prime                  

    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5)
    ax.text(w - 25, y0 + 14, "Axe optique", color="#64748b", fontsize=7, style="italic", ha="right")

    ax.plot([x0, x0], [20, h - 20], color="#38bdf8", lw=3)
    ax.plot([x0 - 8, x0, x0 + 8], [30, 20, 30], color="#38bdf8", lw=3)
    ax.plot([x0 - 8, x0, x0 + 8], [h - 30, h - 20, h - 30], color="#38bdf8", lw=3)
    ax.text(x0 + 10, 25, "Lentille (L)", color="#38bdf8", fontsize=8, fontweight="bold", ha="left")
    ax.text(x0 - 12, y0 + 14, "O", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right")

    ax.plot([xf, xf], [y0 - 5, y0 + 5], color="#cbd5e1", lw=2)
    ax.text(xf, y0 + 14, "F", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")
    ax.plot([xf_prime, xf_prime], [y0 - 5, y0 + 5], color="#cbd5e1", lw=2)
    ax.text(xf_prime, y0 + 14, "F'", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

    ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
    ax.text(xa + 8, y0 + 14, "A", color="#ef4444", fontsize=8, fontweight="bold")
    ax.text(xa + 8, y0 - h_obj - 6, "B", color="#ef4444", fontsize=8, fontweight="bold")

    denominateur = x_obj + f_prime
    vergence_c_box = 100.0 / f_prime

    chk_b = st.session_state.get("chk_rayon_bleu", True)
    chk_j = st.session_state.get("chk_rayon_jaune", True)
    chk_r = st.session_state.get("chk_rayon_rose", True)
    chk_img = st.session_state.get("chk_afficher_image_verte", True)

    if abs(denominateur) < 0.01:
        msg_lentille = "OBJET SUR LE FOYER F : L'image est rejetee a l'infini."
        couleur_msg = "#ef4444"
        
        if chk_j:
            ax.plot([xa, x0], [y0 - h_obj, y0 - h_obj], color="#eab308", lw=1.5)
            ax.plot([x0, w - 20], [y0 - h_obj, y0 - h_obj + (w - 20 - x0) * (h_obj / f_prime)], color="#eab308", lw=1.5)
        if chk_b:
            ax.plot([xa, w - 40], [y0 - h_obj, y0 + (w - 40 - x0) * (h_obj / x_obj)], color="#2563eb", lw=1.5)
        
        txt_box_lentille = (
            f"Lentille :\n"
            f"• Objet x = {x_obj:.1f} cm\n"
            f"• Taille AB = {h_obj:.1f} cm\n"
            f"• Focale f' = {f_prime:.1f} cm\n"
            f"• Image x' = Infini\n"
            f"• Vergence C = {vergence_c_box:.2f} δ\n"
            f"• Grandissement g = Infini"
        )
    else:
        x_image = (f_prime * x_obj) / denominateur
        grandissement = x_image / x_obj
        h_image = h_obj * grandissement
        xa_prime = x0 + x_image
        taille_image_cm = abs(h_obj * grandissement)

        if x_image > 0:
            msg_lentille = "IMAGE REELLE : Apres la lentille (inversee)."
            couleur_msg = "#10b981"
            couleur_image = "#10b981"
        else:
            msg_lentille = "IMAGE VIRTUELLE : Effet loupe (droite)."
            couleur_msg = "#38bdf8"
            couleur_image = "#a855f7"

        if chk_b:
            ax.plot([xa, x0], [y0 - h_obj, y0], color="#2563eb", lw=1.5)
            ax.plot([x0, w - 40], [y0, y0 + (w - 40 - x0) * (y0 - (y0 - h_obj)) / (x0 - xa)], color="#2563eb", lw=1.5)
            if x_image < 0:
                ax.plot([x0, xa_prime], [y0, y0 - h_image], color="#2563eb", lw=1.5, linestyle="--")

        if chk_j:
            ax.plot([xa, x0], [y0 - h_obj, y0 - h_obj], color="#eab308", lw=1.5)
            ax.plot([x0, xf_prime], [y0 - h_obj, y0], color="#eab308", lw=1.5)
            ax.plot([xf_prime, w - 20], [y0, y0 + (w - 20 - xf_prime) * (h_obj / f_prime)], color="#eab308", lw=1.5)
            if x_image < 0:
                hauteur_proj_j = y0 - h_obj + (h_obj / f_prime) * x_image
                ax.plot([x0, xa_prime], [y0 - h_obj, hauteur_proj_j], color="#eab308", lw=1.5, linestyle="--")

        if chk_r:
            if x_image > 0:
                ax.plot([xa, xf], [y0 - h_obj, y0], color="#ec4899", lw=1.5)
                ax.plot([xf, x0], [y0, y0 - h_image], color="#ec4899", lw=1.5)
                ax.plot([x0, w - 20], [y0 - h_image, y0 - h_image], color="#ec4899", lw=1.5)
            else:
                h_impact_y = y0 - (h_obj * (x0 - xf)) / (xa - xf) if (xa - xf) != 0 else y0 - h_obj
                ax.plot([xf, xa], [y0, y0 - h_obj], color="#ec4899", lw=1.5, linestyle="--")
                ax.plot([xa, x0], [y0 - h_obj, h_impact_y], color="#ec4899", lw=1.5)
                ax.plot([x0, w - 20], [h_impact_y, h_impact_y], color="#ec4899", lw=1.5)
                ax.plot([x0, xa_prime], [h_impact_y, h_impact_y], color="#ec4899", lw=1.5, linestyle="--")

        if chk_img:
            ax.annotate("", xy=(xa_prime, y0 - h_image), xytext=(xa_prime, y0), arrowprops=dict(arrowstyle="->", color=couleur_image, lw=2.5))
            ax.text(xa_prime + 8, y0 + 14, "A'", color=couleur_image, fontsize=7, fontweight="bold")
            ax.text(xa_prime + 8, y0 - h_image - 6, "B'", color=couleur_image, fontsize=7, fontweight="bold")

        txt_box_lentille = (
            f"Lentille :\n"
            f"• Objet x = {x_obj:.1f} cm\n"
            f"• Taille AB = {h_obj:.1f} cm\n"
            f"• Focale f' = {f_prime:.1f} cm\n"
            f"• Image x' = {x_image:.1f} cm\n"
            f"• Taille A'B' = {taille_image_cm:.1f} cm\n"
            f"• Vergence C = {vergence_c_box:.2f} δ\n"
            f"• Grandissement g = {grandissement:.2f}"
        )

    ax.text(20, 20, "OPTIQUE : LENTILLES MINCES CONVERGENTES", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(20, 35, msg_lentille, color=couleur_msg, fontsize=7, fontweight="bold", ha="left")

    st.session_state.opt5_txt_box_lentille = txt_box_lentille
    return fig

def reinitialiser_mesures_lentille_streamlit():
    st.session_state.mesures_inv_x = []
    st.session_state.mesures_inv_xprime = []

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









with tab3:
    st.header(" Lentilles Minces Divergentes & Applications Visuelles")
    
    if "opt6_verrouille" not in st.session_state: st.session_state.opt6_verrouille = False
    if "mesures_inv_x2" not in st.session_state: st.session_state.mesures_inv_x2 = []
    if "mesures_inv_xprime2" not in st.session_state: st.session_state.mesures_inv_xprime2 = []

    col_g_widgets, col_d_rendu = st.columns([1.2, 2.2])

    # --- PANNEAU DE GAUCHE : LES PANNEAUX DE COMMANDES ---
    with col_g_widgets:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>CONTRÔLES DE LA LENTILLE DIVERGENTE</p>", unsafe_allow_html=True)
            
            height_ab2 = st.slider("Hauteur de l'objet AB (cm)  :", min_value=10.0, max_value=100.0, value=40.0, step=1.0, key="slide_len2_ab", disabled=st.session_state.opt6_verrouille)
            pos_x2 = st.slider("Position de l'objet x (cm)  :", min_value=-600.0, max_value=-10.0, value=-80.0, step=1.0, key="slide_len2_x", disabled=st.session_state.opt6_verrouille)
            f_prime2 = st.slider("Distance focale f' (cm)  :", min_value=-500.0, max_value=-100.0, value=-150.0, step=1.0, key="slide_len2_f", disabled=st.session_state.opt6_verrouille)

            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            st.markdown("##### Affichage des rayons :")
            
            chk_b2 = st.checkbox("Rayon central (O) ", value=True, key="chk_rayon2_bleu", disabled=st.session_state.opt6_verrouille)
            chk_j2 = st.checkbox("Rayon parallele (F') ", value=True, key="chk_rayon2_jaune", disabled=st.session_state.opt6_verrouille)
            chk_r2 = st.checkbox("Rayon focal (F) ", value=True, key="chk_rayon2_rose", disabled=st.session_state.opt6_verrouille)
            chk_img2 = st.checkbox("Afficher l'image A'B' ", value=True, key="chk_afficher_image2_verte", disabled=st.session_state.opt6_verrouille)

            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("CAPTURER LA MESURE ", key="btn_capt_mesure_len2", use_container_width=True, disabled=st.session_state.opt6_verrouille):
                    ajouter_mesure_lentille_divergente_streamlit()
                    st.rerun()
            with col_b2:
                if st.button("EFFACER ", key="btn_clear_len2", use_container_width=True, disabled=st.session_state.opt6_verrouille):
                    reinitialiser_mesures_lentille_divergente_streamlit()
                    st.rerun()

        with st.container(border=True):
            try:
                vergence2 = 100.0 / f_prime2
                x_img_c2 = (f_prime2 * pos_x2) / (pos_x2 + f_prime2)
                grandissement2 = x_img_c2 / pos_x2
                taille_img2 = abs(height_ab2 * grandissement2)
            except:
                x_img_c2 = vergence2 = grandissement2 = taille_img2 = 0.0

            st.markdown("**Console de calculs de la lentille :**")
            st.text(
                f"• Objet x = {pos_x2:.1f} cm\n"
                f"• Taille AB = {height_ab2:.1f} cm\n"
                f"• Focale f' = {f_prime2:.1f} cm\n"
                f"• Image x' = {x_img_c2:.1f} cm\n"
                f"• Taille A'B' = {taille_img2:.1f} cm\n"
                f"• Vergence C = {vergence2:.2f} δ\n"
                f"• Grandissement γ = {grandissement2:.2f}"
            )

    # --- PANNEAU DE DROITE : SÉQUENTIEL VERTICAL DEMANDÉ ---
    with col_d_rendu:
        st.subheader("Banc d'optique virtuel")
        fig_banc2 = mettre_a_jour_lentille_divergente_matplotlib()
        st.pyplot(fig_banc2, use_container_width=True)
        
        st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Tableau des points enregistres (Espace de Descartes)")
        
        import pandas as pd
        if st.session_state.mesures_inv_x2:
            df_lentille2 = pd.DataFrame({
                "Essai": [f"Essai {idx}" for idx in range(1, len(st.session_state.mesures_inv_x2) + 1)],
                "1/x (cm^-1)": st.session_state.mesures_inv_x2,
                "1/x' (cm^-1)": st.session_state.mesures_inv_xprime2,
                "1/x' - 1/x (cm^-1)": [round(xp - x, 4) for x, xp in zip(st.session_state.mesures_inv_x2, st.session_state.mesures_inv_xprime2)]
            })
            st.dataframe(df_lentille2, use_container_width=True, hide_index=True)
        else:
            st.caption("Tableau vide. Deplacez les curseurs de la lentille et cliquez sur Capturer la mesure.")

        st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        st.subheader("Relation de Descartes")
        fig_courbe2 = mettre_a_jour_graphique_lentille_divergente_matplotlib()
        st.pyplot(fig_courbe2, use_container_width=True)

    st.write("---")
    dict_q6, dict_t6 = afficher_questions_optique6(verrouille=st.session_state.get("opt6_verrouille", False))


    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION AUTOMATIQUE SUR 20 POINTS - ATELIER 6
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 6")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt6 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 6.", 
        key="check_certif_opt6_officiel_20pts", 
        disabled=st.session_state.get("opt6_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_opt6_official_20pts", use_container_width=True, disabled=st.session_state.get("opt6_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt6: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Moteur de correction automatique du Quiz (10 Pts)
            attendus_qo6_v = {
                "q1": "Plus epais que son centre", "q2": "Une fleche double retournee (pointes vers le centre)", 
                "q3": "Toujours negative (f' < 0)", "q4": "Negative (en dioptries)", 
                "q5": "Le foyer image virtuel F' situe en amont", "q6": "Parallele a l'axe optique", 
                "q7": "Virtuelle, droite et plus petite", "q8": "Positif et inferieur a 1 (0 < g < 1)", 
                "q9": "-2.00 δ", "q10": "Oui, ce sont les valeurs numeriques de f' et x qui changent de signe"
            }
            score_quiz_opt6 = sum([1.0 for qk, qv in attendus_qo6_v.items() if st.session_state.get(f"col_g_quiz_opt6_{qk}") == qv])

            # Moteur de correction automatique du Texte a trous (10 Pts)
            score_trous_opt6 = 0.0
            if st.session_state.get("opt6_t1") == "Divergente": score_trous_opt6 += 2.5
            if st.session_state.get("opt6_t2") == "Negatif": score_trous_opt6 += 2.5
            if st.session_state.get("opt6_t3") == "Image F'": score_trous_opt6 += 2.5
            if st.session_state.get("opt6_t4") == "Virtuelle": score_trous_opt6 += 2.5

            st.session_state.score_opt6_p1 = round(score_quiz_opt6, 1)
            st.session_state.score_opt6_p2 = round(score_trous_opt6, 1)
            st.session_state.score_final_opt6 = round(score_quiz_opt6 + score_trous_opt6, 1)
            st.session_state.opt6_verrouille = True
            st.rerun()

    # AFFICHAGE ET IMPRESSION DU RAPPORT EN SÉCURITÉ APRES LE SCELLE
    if st.session_state.get("opt6_verrouille", False):
        scr1 = st.session_state.get("score_opt6_p1", 0.0)
        scr2 = st.session_state.get("score_opt6_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt6", 0.0)

        from datetime import timedelta
        timestamp_opt6 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 6 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo6_v = {
            "q1": "Plus epais que son centre", "q2": "Une fleche double retournee (pointes vers le centre)", 
            "q3": "Toujours negative (f' < 0)", "q4": "Negative (en dioptries)", 
            "q5": "Le foyer image virtuel F' situe en amont", "q6": "Parallele a l'axe optique", 
            "q7": "Virtuelle, droite et plus petite", "q8": "Positif et inferieur a 1 (0 < g < 1)", 
            "q9": "-2.00 δ", "q10": "Oui, ce sont les valeurs numeriques de f' et x qui changent de signe"
        }
        attendus_to6_v = {"t1": "Divergente", "t2": "Negatif", "t3": "Image F'", "t4": "Virtuelle"}

        html_export_opt6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 6 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 6</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 4 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LA DIVERGENCE (10 PTS)</div>
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

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo6_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt6_{q_id}", "Choisir...")
            attendu = attendus_qo6_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt6 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt6 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to6_v.items(), 1):
            saisie = st.session_state.get(f"opt6_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt6 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt6 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique6_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 6 SUR VOTRE ORDINATEUR",
            data=html_export_opt6,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )















