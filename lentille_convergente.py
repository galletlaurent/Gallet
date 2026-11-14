# -*- coding: utf-8 -*-

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Application lentille convergente ",
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

st.title("Application lentille convergente")
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
    "Les lentilles convergentes : définition et régles de tracé des rayons",
    "Les lentilles convergentes",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier",
    "Application dans le domaine dgéomètre topographe"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]
tab7 = onglets[7]



def afficher_questions_optique5(verrouille=False):
    col_double_quiz_opt5, col_double_trous_opt5 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES SUR LES LENTILLES ---
    with col_double_quiz_opt5:
        st.markdown("##### Quiz sur les lentilles convergentes (10 questions) - (10 pts)")
        if "ordre_questions_opt5" not in st.session_state:
            questions_opt5_base = [
                ("q1", "D'apres la relation de conjugaison de Descartes, la formule exacte est :"),
                ("q2", "Un rayon lumineux passant par le centre optique O d'une lentille mince :"),
                ("q3", "Un rayon incident parallele a l'axe optique ressort de la lentille en passant par :"),
                ("q4", "La vergence C d'une lentille est l'inverse de sa distance focale f'. Son unite est :"),
                ("q5", "Si l'objet AB est situe a une distance superieure a la distance focale (x > f'), l'image obtenue est :"),
                ("q6", "Si le grandissement gamma est negatif (gamma < 0), cela signifie geometriquement que l'image est :"),
                ("q7", "Lorsque l'objet AB est deplace et positionne pile sur le foyer objet F, l'image se forme :"),
                ("q8", "Une lentille mince est qualifiee de convergente si ses bords sont :"),
                ("q9", "Si la taille de l'image est deux fois plus grande que l'objet et de meme sens, gamma vaut :"),
                ("q10", "Lorsqu'on trace le graphique de 1/x' en fonction de 1/x, la courbe obtenue est une droite de pente :")
            ]
            import random
            random.shuffle(questions_opt5_base)
            st.session_state.ordre_questions_opt5 = questions_opt5_base

        dict_quiz_opt5 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt5, 1):
            cle_qo5 = f"col_g_quiz_opt5_{q_id}"
            cle_opts_unique = f"opts_opt5_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["1/x' - 1/x = 1/f'", "1/x' + 1/x = 1/f'", "1/f' - 1/x = 1/x'"]
                elif q_id == "q2": copie_opts = ["Continue en ligne droite sans subir de deviation", "Est devie en passant par le foyer image F'", "Est reflechi a 90 degres"]
                elif q_id == "q3": copie_opts = ["Le foyer image F'", "Le centre optique O", "Le foyer objet F"]
                elif q_id == "q4": copie_opts = ["La dioptrie (delta)", "Le metre (m)", "Le radian (rad)"]
                elif q_id == "q5": copie_opts = ["Reelle et renversee", "Virtuelle et droite", "Inexistante"]
                elif q_id == "q6": copie_opts = ["Renversee par rapport a l'objet", "Droite et dans le meme sens", "Plus petite que l'objet"]
                elif q_id == "q7": copie_opts = ["A l'infini", "Sur le centre optique O", "Pile sur le foyer image F'"]
                elif q_id == "q8": copie_opts = ["Plus minces que son centre", "Plus epais que son centre", "Rigoureusement plats"]
                elif q_id == "q9": copie_opts = ["+2.0", "-2.0", "+0.5"]
                elif q_id == "q10": copie_opts = ["1 (droite inclinee a 45 degres)", "-1", "Egale a la vergence C"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo5, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt5[f"{q_id}_opt5"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo5, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE DES LENTILLES (10 TROUS = 10 PTS) ---
    with col_double_trous_opt5:
        st.markdown("##### Synthese de cours (Texte a trous) - (10 pts)")
        
        co5_1, co5_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_1: st.write("1. Une lentille mince possede des bords plus minces que son centre. Elle est qualifiee de")
        with co5_2: t1 = st.selectbox("", ["Choisir...", "Convergente", "Divergente", "Cylindrique"], key="opt5_t1", disabled=verrouille, label_visibility="collapsed")
        
        co5_3, co5_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_3: st.write("2. Tout rayon incident parallele a l'axe optique ressort en convergeant vers le foyer")
        with co5_4: t2 = st.selectbox("", ["Choisir...", "Image F'", "Objet F", "Central O"], key="opt5_t2", disabled=verrouille, label_visibility="collapsed")

        co5_5, co5_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_5: st.write("3. La relation de conjugaison permet de calculer la position x' de l'image. Sa vergence s'exprime en")
        with co5_6: t3 = st.selectbox("", ["Choisir...", "Dioptries", "Metres", "Degres"], key="opt5_t3", disabled=verrouille, label_visibility="collapsed")

        co5_7, co5_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_7: st.write("4. Enfin, le rapport des dimensions entre l'image et l'objet definit le")
        with co5_8: t4 = st.selectbox("", ["Choisir...", "Grandissement", "Pouvoir separateur", "Facteur de forme"], key="opt5_t4", disabled=verrouille, label_visibility="collapsed")

        co5_9, co5_10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_9: st.write("5. Tout rayon passant par le centre optique O traverse la lentille sans aucune")
        with co5_10: t5 = st.selectbox("", ["Choisir...", "Deviation", "Reflexion", "Dispersion"], key="opt5_t5", disabled=verrouille, label_visibility="collapsed")

        co5_11, co5_12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_11: st.write("6. Tout rayon passant par le foyer objet F ressort de la lentille parallèlement à l'axe")
        with co5_12: t6 = st.selectbox("", ["Choisir...", "Optique", "Vertical", "Transversal"], key="opt5_t6", disabled=verrouille, label_visibility="collapsed")

        co5_13, co5_14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_13: st.write("7. La distance entre le centre optique O et le foyer image F' s'appelle la distance")
        with co5_14: t7 = st.selectbox("", ["Choisir...", "Focale", "Frontale", "Critique"], key="opt5_t7", disabled=verrouille, label_visibility="collapsed")

        co5_15, co5_16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_15: st.write("8. Lorsque l'image se projette sur un ecran derriere la lentille, elle est qualifiee de")
        with co5_16: t8 = st.selectbox("", ["Choisir...", "Reelle", "Virtuelle", "Droite"], key="opt5_t8", disabled=verrouille, label_visibility="collapsed")

        co5_17, co5_18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_17: st.write("9. Si le grandissement gamma est negatif, l'image obtenue sur l'ecran est")
        with co5_18: t9 = st.selectbox("", ["Choisir...", "Renversee", "Droite", "Infinie"], key="opt5_t9", disabled=verrouille, label_visibility="collapsed")

        co5_19, co5_20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_19: st.write("10. Lorsque l'objet est place exactement sur le foyer objet F, l'image se forme a l'")
        with co5_20: t10 = st.selectbox("", ["Choisir...", "Infini", "Origine", "Centre O"], key="opt5_t10", disabled=verrouille, label_visibility="collapsed")

        dict_trous_opt5 = {
            "t1_opt5": t1, "t2_opt5": t2, "t3_opt5": t3, "t4_opt5": t4, "t5_opt5": t5,
            "t6_opt5": t6, "t7_opt5": t7, "t8_opt5": t8, "t9_opt5": t9, "t10_opt5": t10
        }

    return dict_quiz_opt5, dict_trous_opt5







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

def ajouter_mesure_lentille_convergente_streamlit():
    import math
    x_obj = st.session_state.get("slide_len_x", -80.0)
    f_prime = st.session_state.get("slide_len_f", 50.0)
    
    denom = x_obj + f_prime
    if abs(denom) < 0.01:
        return 

    x_image = (f_prime * x_obj) / denom

    inv_x = 1.0 / x_obj
    inv_xprime = 1.0 / x_image
    inv_fpcalcul = inv_xprime - inv_x

    if "mesures_inv_x" not in st.session_state: st.session_state.mesures_inv_x = []
    if "mesures_inv_xprime" not in st.session_state: st.session_state.mesures_inv_xprime = []
    
    st.session_state.mesures_inv_x.append(round(inv_x, 4))
    st.session_state.mesures_inv_xprime.append(round(inv_xprime, 4))


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

def ajouter_mesure_lentille_convergente_streamlit():
    import math
    x = st.session_state.get("slide_len_x", -80.0)
    f_prime = st.session_state.get("slide_len_f", 50.0)
    
    if x != 0 and f_prime != 0:
        try:
            inv_x = 1.0 / x
            inv_f = 1.0 / f_prime
            inv_xp = inv_f + inv_x
        except:
            inv_x = inv_xp = inv_f = 0.0

        if "mesures_inv_x" not in st.session_state: st.session_state.mesures_inv_x = []
        if "mesures_inv_xprime" not in st.session_state: st.session_state.mesures_inv_xprime = []
        
        st.session_state.mesures_inv_x.append(round(inv_x, 5))
        st.session_state.mesures_inv_xprime.append(round(inv_xp, 5))

def reinitialiser_mesures_lentille_streamlit():
    st.session_state.mesures_inv_x = []
    st.session_state.mesures_inv_xprime = []

def afficher_atelier_hist_lentilles(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 1 (Histoire des lentilles)."""
    questions_hl = [
        {"id": "qhl1", "q": "Quelle est la plus ancienne lentille convergente connue, découverte en Assyrie (vers 750 av. J.-C.) ?", "options": ["La lentille de Nimrud en cristal de roche", "La lentille de Fresnel en verre moulé", "L'objectif photographique de Zeiss"], "rep": "La lentille de Nimrud en cristal de roche"},
        {"id": "qhl2", "q": "Quel savant arabe du XIe siècle a décrit le pouvoir grossissant des lentilles convexes dans son Traité d'optique ?", "options": ["Ibn al-Haytham (Alhazen)", "Archimède", "Pythagore"], "rep": "Ibn al-Haytham (Alhazen)"},
        {"id": "qhl3", "q": "Vers quelle année les premières lunettes de vue à lentilles convergentes (pour presbytes) sont-elles inventées en Italie ?", "options": ["Vers 1285 (fin du XIIIe siècle)", "En 1789", "En 1905"], "rep": "Vers 1285 (fin du XIIIe siècle)"},
        {"id": "qhl4", "q": "Quel savant a perfectionné la lunette astronomique en 1609 pour observer les satellites de Jupiter ?", "options": ["Galilée", "Isaac Newton", "Blaise Pascal"], "rep": "Galilée"},
        {"id": "qhl5", "q": "Quel astronome allemand a établi dès 1611 la théorie géométrique des lentilles minces convergentes dans son ouvrage Dioptrice ?", "options": ["Johannes Kepler", "Nicolas Copernic", "Tycho Brahe"], "rep": "Johannes Kepler"},
        {"id": "qhl6", "q": "Quel physicien français a inventé en 1822 les lentilles à échelons pour équiper les phares maritimes ?", "options": ["Augustin Fresnel", "René Descartes", "Louis Pasteur"], "rep": "Augustin Fresnel"},
        {"id": "qhl7", "q": "Pourquoi les lentilles convergentes étaient-elles appelées « verres ardents » dans l'Antiquité ?", "options": ["Parce qu'elles concentraient les rayons du Soleil en un point (le foyer) pour allumer un feu", "Parce qu'elles brillaient dans le noir", "Parce qu'elles étaient fabriquées dans la lave"], "rep": "Parce qu'elles concentraient les rayons du Soleil en un point (le foyer) pour allumer un feu"},
        {"id": "qhl8", "q": "De quel mot latin provient le nom « lentille » en optique ?", "options": ["Lens (qui désigne la graine de lentille, de forme biconvexe)", "Lux (la lumière)", "Lumen (le flux)"], "rep": "Lens (qui désigne la graine de lentille, de forme biconvexe)"},
        {"id": "qhl9", "q": "Quel défaut visuel lié à l'âge a été le premier corrigé par des lentilles convergentes au Moyen Âge ?", "options": ["La presbytie (difficulté à voir de près)", "La myopie", "Le daltonisme"], "rep": "La presbytie (difficulté à voir de près)"},
        {"id": "qhl10", "q": "Quelle formule algébrique moderne relie la position de l'objet x, celle de l'image x' et la distance focale f' ?", "options": ["La relation de conjugaison de Descartes (1/x' - 1/x = 1/f')", "La loi d'Ohm (U = R·I)", "La relation d'Einstein (E = mc²)"], "rep": "La relation de conjugaison de Descartes (1/x' - 1/x = 1/f')"},
    ]

    if "ordre_quiz_hl_aleatoire" not in st.session_state:
        random.shuffle(questions_hl)
        st.session_state.ordre_quiz_hl_aleatoire = questions_hl

    champs_hl = [
        ("1. Le mot lentille vient du latin ......... en raison de sa forme bombée.", ["Choisir...", "lens", "lux"], "lens", "hl_t1"),
        ("2. La lentille de ......... (750 av. J.-C.) est taillée dans du cristal de roche.", ["Choisir...", "Nimrud", "Alexandrie"], "Nimrud", "hl_t2"),
        ("3. Au XIe siècle, ......... étudie le grossissement des surfaces convexes.", ["Choisir...", "Alhazen", "Euclide"], "Alhazen", "hl_t3"),
        ("4. Les premières ......... de vue convergentes apparaissent en Italie vers 1285.", ["Choisir...", "lunettes", "caméras"], "lunettes", "hl_t4"),
        ("5. En 1609, ......... utilise une lunette pour observer les astres.", ["Choisir...", "Galilée", "Newton"], "Galilée", "hl_t5"),
        ("6. En 1611, Johannes ......... publie le traité Dioptrice.", ["Choisir...", "Kepler", "Descartes"], "Kepler", "hl_t6"),
        ("7. En 1822, Augustin ......... invente la lentille à échelons pour les phares.", ["Choisir...", "Fresnel", "Foucault"], "Fresnel", "hl_t7"),
        ("8. Une lentille convergente concentre les rayons solaires en son .........", ["Choisir...", "foyer", "bord"], "foyer", "hl_t8"),
        ("9. Au Moyen Âge, les verres convergents corrigeaient la .........", ["Choisir...", "presbytie", "surdité"], "presbytie", "hl_t9"),
        ("10. La formule de conjugaison porte le nom de René .........", ["Choisir...", "Descartes", "Pascal"], "Descartes", "hl_t10"),
    ]

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Historique des Lentilles (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_hl_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"hl_at1_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Historique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_hl:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


def dessiner_regles_trace_lentille_matplotlib():
    """Schéma pédagogique interactif des 3 rayons particuliers d'une lentille convergente."""
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 240)
    ax.invert_yaxis()
    ax.axis("off")

    x0, y0 = 300.0, 120.0
    f_px = st.session_state.get("slider_regles_f", 100.0)
    choix_rayon = st.session_state.get("radio_regles_rayon", "Tous les 3 rayons particuliers")

    # Axe optique
    ax.plot(list((20, 580)), list((y0, y0)), color="#cbd5e1", lw=1.3, ls="-.")
    ax.text(575, y0 + 14, "Axe optique", color="#94a3b8", fontsize=8, ha="right")

    # Lentille convergente (double flèche)
    ax.plot(list((x0, x0)), list((25, 215)), color="#38bdf8", lw=3)
    ax.plot(list((x0 - 8, x0, x0 + 8)), list((35, 25, 35)), color="#38bdf8", lw=3)
    ax.plot(list((x0 - 8, x0, x0 + 8)), list((205, 215, 205)), color="#38bdf8", lw=3)
    ax.text(x0 + 8, 30, "Lentille (L)", color="#38bdf8", fontsize=8.5, fontweight="bold")
    ax.text(x0 - 10, y0 + 14, "O", color="#cbd5e1", fontsize=8.5, fontweight="bold", ha="right")

    # Foyers F et F'
    xf = x0 - f_px
    xfp = x0 + f_px
    ax.scatter(list((xf, xfp)), list((y0, y0)), color="#fde047", s=45, zorder=5)
    ax.text(xf, y0 + 16, "F (Foyer objet)", color="#fde047", fontsize=8, fontweight="bold", ha="center")
    ax.text(xfp, y0 + 16, "F' (Foyer image)", color="#fde047", fontsize=8, fontweight="bold", ha="center")

    # Point objet B à gauche (x = 110, y = 65)
    xb, yb = 110.0, 65.0
    ax.annotate("", xy=(xb, yb), xytext=(xb, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
    ax.text(xb - 6, y0 + 14, "A", color="#ef4444", fontsize=8.5, fontweight="bold", ha="right")
    ax.text(xb - 6, yb, "B", color="#ef4444", fontsize=8.5, fontweight="bold", ha="right")

    # Calcul point image B'
    x_obj = xb - x0
    x_img = (f_px * x_obj) / (x_obj + f_px)
    h_obj = y0 - yb
    h_img = h_obj * (x_img / x_obj)
    xbp = x0 + x_img
    ybp = y0 - h_img

    # Règle 1 : Rayon parallèle à l'axe -> passe par F'
    if "1" in choix_rayon or "Tous" in choix_rayon:
        ax.annotate("", xy=(x0, yb), xytext=(xb, yb), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))
        pente1 = (y0 - yb) / f_px
        ax.annotate("", xy=(560, yb + pente1 * (560 - x0)), xytext=(x0, yb), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))

    # Règle 2 : Rayon passant par O -> non dévié
    if "2" in choix_rayon or "Tous" in choix_rayon:
        pente2 = (y0 - yb) / (x0 - xb)
        ax.annotate("", xy=(560, yb + pente2 * (560 - xb)), xytext=(xb, yb), arrowprops=dict(arrowstyle="->", color="#3b82f6", lw=2))

    # Règle 3 : Rayon passant par F -> ressort parallèle à l'axe
    if "3" in choix_rayon or "Tous" in choix_rayon:
        pente3 = (y0 - yb) / (xf - xb)
        y_hit3 = yb + pente3 * (x0 - xb)
        if 20 <= y_hit3 <= 220:
            ax.annotate("", xy=(x0, y_hit3), xytext=(xb, yb), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=2))
            ax.annotate("", xy=(560, y_hit3), xytext=(x0, y_hit3), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=2))

    # Image A'B'
    if 310 <= xbp <= 570:
        ax.annotate("", xy=(xbp, ybp), xytext=(xbp, y0), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2.5))
        ax.text(xbp + 6, y0 - 6, "A'", color="#22c55e", fontsize=8.5, fontweight="bold")
        ax.text(xbp + 6, ybp + 6, "B'", color="#22c55e", fontsize=8.5, fontweight="bold")

    ax.text(20, 18, "RÈGLES DE CONSTRUCTION GÉOMÉTRIQUE DES 3 RAYONS PARTICULIERS", color="#38bdf8", fontsize=9, fontweight="bold")
    return fig


def afficher_atelier_regles_lentilles(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 2 (Règles de tracé)."""
    questions_rl = [
        {"id": "qrl1", "q": "Comment reconnaît-on au toucher une lentille mince convergente ?", "options": ["Ses bords sont plus minces que son centre", "Ses bords sont plus épais que son centre", "Elle est totalement plate comme une vitre"], "rep": "Ses bords sont plus minces que son centre"},
        {"id": "qrl2", "q": "Quel est le symbole schématique normalisé d'une lentille mince convergente ?", "options": ["Un segment vertical terminé par deux flèches pointant vers l'extérieur", "Un segment terminé par des flèches inversées vers l'intérieur", "Un rectangle noir opaque"], "rep": "Un segment vertical terminé par deux flèches pointant vers l'extérieur"},
        {"id": "qrl3", "q": "Que fait un rayon lumineux incident passant par le centre optique O de la lentille ?", "options": ["Il traverse la lentille en ligne droite sans être dévié", "Il est réfléchi vers l'arrière", "Il ressort parallèlement à l'axe optique"], "rep": "Il traverse la lentille en ligne droite sans être dévié"},
        {"id": "qrl4", "q": "Par quel point remarquable ressort tout rayon incident parallèle à l'axe optique ?", "options": ["Par le foyer image F'", "Par le foyer objet F", "Par le bord supérieur de la lentille"], "rep": "Par le foyer image F'"},
        {"id": "qrl5", "q": "Comment ressort un rayon incident qui passe par le foyer objet F avant de toucher la lentille ?", "options": ["Il ressort parallèlement à l'axe optique", "Il passe par le centre optique O", "Il converge vers F'"], "rep": "Il ressort parallèlement à l'axe optique"},
        {"id": "qrl6", "q": "Comment sont placés le foyer objet F et le foyer image F' par rapport au centre optique O ?", "options": ["Ils sont symétriques par rapport au centre optique O (OF = OF')", "Ils sont tous les deux à droite de la lentille", "Ils sont confondus avec le point O"], "rep": "Ils sont symétriques par rapport au centre optique O (OF = OF')"},
        {"id": "qrl7", "q": "Combien de rayons particuliers suffit-il de tracer depuis un point objet B pour trouver la position exacte de son image B' ?", "options": ["2 rayons suffisent (le 3e sert de vérification)", "Il faut obligatoirement 10 rayons", "1 seul rayon suffit"], "rep": "2 rayons suffisent (le 3e sert de vérification)"},
        {"id": "qrl8", "q": "Si l'objet AB est perpendiculaire à l'axe optique avec A sur l'axe, où se situe le point image A' ?", "options": ["Également sur l'axe optique (projection orthogonale de B')", "Au-dessus de B'", "Sur le foyer F"], "rep": "Également sur l'axe optique (projection orthogonale de B')"},
        {"id": "qrl9", "q": "Quelle est l'unité légale de la distance focale f' dans les calculs de vergence C = 1 / f' ?", "options": ["Le mètre (m)", "Le centimètre (cm)", "Le degré (°)"], "rep": "Le mètre (m)"},
        {"id": "qrl10", "q": "Une lentille convergente de distance focale f' = 20 cm (0,20 m) possède une vergence C égale à :", "options": ["+ 5,0 dioptries (δ)", "+ 20 dioptries (δ)", "+ 0,20 dioptrie (δ)"], "rep": "+ 5,0 dioptries (δ)"},
    ]

    if "ordre_quiz_rl_aleatoire" not in st.session_state:
        random.shuffle(questions_rl)
        st.session_state.ordre_quiz_rl_aleatoire = questions_rl

    champs_rl = [
        ("1. Une lentille convergente a des bords plus ......... que son centre.", ["Choisir...", "minces", "épais"], "minces", "rl_t1"),
        ("2. L'axe de symétrie perpendiculaire à la lentille est l'axe .........", ["Choisir...", "optique", "vertical"], "optique", "rl_t2"),
        ("3. Le point central de la lentille noté O est le centre .........", ["Choisir...", "optique", "focal"], "optique", "rl_t3"),
        ("4. Tout rayon passant par le centre O n'est pas .........", ["Choisir...", "dévié", "transmis"], "dévié", "rl_t4"),
        ("5. Tout rayon parallèle à l'axe émerge en passant par le foyer ......... F'.", ["Choisir...", "image", "objet"], "image", "rl_t5"),
        ("6. Tout rayon passant par le foyer objet F ressort ......... à l'axe.", ["Choisir...", "parallèle", "perpendiculaire"], "parallèle", "rl_t6"),
        ("7. Les foyers F et F' sont ......... par rapport au centre O.", ["Choisir...", "symétriques", "confondus"], "symétriques", "rl_t7"),
        ("8. La distance OF' s'appelle la distance ......... f'.", ["Choisir...", "focale", "frontale"], "focale", "rl_t8"),
        ("9. L'inverse de la distance focale en mètres est la ......... C.", ["Choisir...", "vergence", "puissance"], "vergence", "rl_t9"),
        ("10. L'unité de la vergence d'une lentille est la ......... (δ).", ["Choisir...", "dioptrie", "candela"], "dioptrie", "rl_t10"),
    ]

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Définition & Règles de Tracé (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_rl_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"rl_at2_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Règles de Tracé (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_rl:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


BANQUES_LEN_MAINT = {
    0: {
        "questions": [
            {"id": "qlm0_1", "q": "Où doit être placée une pièce mécanique par rapport au foyer objet F d'une loupe d'atelier pour obtenir une image agrandie et droite ?", "options": ["Entre le centre optique O et le foyer objet F (x < f')", "Au-delà de deux fois la distance focale (x > 2f')", "Sur le foyer image F'"], "rep": "Entre le centre optique O et le foyer objet F (x < f')"},
            {"id": "qlm0_2", "q": "De quelle nature est l'image d'une micro-fissure observée à travers une loupe de maintenance ?", "options": ["Virtuelle, droite et agrandie", "Réelle, renversée et projetée sur l'établi", "Réelle et plus petite que l'objet"], "rep": "Virtuelle, droite et agrandie"},
            {"id": "qlm0_3", "q": "Quel est le signe du grandissement γ lorsque la loupe donne une image droite ?", "options": ["Positif (γ > +1)", "Négatif (γ < 0)", "Nul (γ = 0)"], "rep": "Positif (γ > +1)"},
            {"id": "qlm0_4", "q": "Si une loupe d'horloger-mécanicien a une distance focale f' = 5 cm (0,05 m), quelle est sa vergence C ?", "options": ["+ 20 dioptries (δ)", "+ 5 dioptries (δ)", "+ 0,05 dioptrie (δ)"], "rep": "+ 20 dioptries (δ)"},
            {"id": "qlm0_5", "q": "Que se passe-t-il si le technicien éloigne la loupe au-delà de sa distance focale (x > f') ?", "options": ["L'image devient réelle et renversée (à l'envers)", "L'image grossit 100 fois", "La loupe devient divergente"], "rep": "L'image devient réelle et renversée (à l'envers)"},
            {"id": "qlm0_6", "q": "Quel défaut optique sur les bords d'une loupe bon marché déforme les lignes droites d'un circuit imprimé ?", "options": ["L'aberration sphérique et chromatique", "La réflexion totale", "La diffraction acoustique"], "rep": "L'aberration sphérique et chromatique"},
            {"id": "qlm0_7", "q": "Pourquoi intègre-t-on un anneau de LED blanches autour d'une loupe d'inspection industrielle ?", "options": ["Pour éclairer uniformément la pièce sans ombre portée lors du contrôle visuel", "Pour chauffer la lentille", "Pour alimenter le capteur"], "rep": "Pour éclairer uniformément la pièce sans ombre portée lors du contrôle visuel"},
            {"id": "qlm0_8", "q": "Comment s'appelle le grossissement commercial G d'une loupe de focale f' (en mètres) pour un œil normal (d_m = 0,25 m) ?", "options": ["G = 0,25 / f' = C / 4", "G = f' × 100", "G = 1 / C"], "rep": "G = 0,25 / f' = C / 4"},
            {"id": "qlm0_9", "q": "Quel type de contrôle industriel réalise-t-on avec une loupe éclairante sur des soudures ou des engrenages ?", "options": ["Un Contrôle Non Destructif (CND) visuel direct", "Un essai de dureté Brinell", "Une analyse chimique"], "rep": "Un Contrôle Non Destructif (CND) visuel direct"},
            {"id": "qlm0_10", "q": "Où l'œil du technicien doit-il se placer pour obtenir le champ de vision maximal à travers une loupe ?", "options": ["Proche du foyer image F' de la loupe", "À 2 mètres de la loupe", "Sur le côté à 90°"], "rep": "Proche du foyer image F' de la loupe"},
        ],
        "trous": [
            ("1. Une loupe d'atelier est une lentille mince ......... de courte focale.", ["Choisir...", "convergente", "divergente"], "convergente", "lm_t1"),
            ("2. Pour voir une image droite, l'objet est placé entre O et le foyer ......... F.", ["Choisir...", "objet", "image"], "objet", "lm_t2"),
            ("3. L'image observée à travers une loupe est ......... et agrandie.", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "lm_t3"),
            ("4. Comme l'image est dans le même sens que l'objet, le grandissement γ est .........", ["Choisir...", "positif", "négatif"], "positif", "lm_t4"),
            ("5. Une loupe de focale f' = 5 cm possède une vergence de ......... dioptries.", ["Choisir...", "20", "5"], "20", "lm_t5"),
            ("6. Si l'objet s'éloigne au-delà de F, l'image devient .........", ["Choisir...", "renversée", "droite"], "renversée", "lm_t6"),
            ("7. L'inspection visuelle des soudures est un contrôle non .........", ["Choisir...", "destructif", "optique"], "destructif", "lm_t7"),
            ("8. Une couronne de ......... éclaire la pièce sans créer d'ombre.", ["Choisir...", "LED", "prismes"], "LED", "lm_t8"),
            ("9. Plus la distance focale f' est courte, plus le grossissement est .........", ["Choisir...", "fort", "faible"], "fort", "lm_t9"),
            ("10. Les bords d'une loupe convergente sont plus ......... que son centre.", ["Choisir...", "minces", "épais"], "minces", "lm_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qlm1_1", "q": "Dans un capteur de vision industrielle (caméra de contrôle qualité), quel rôle joue l'objectif à lentilles convergentes ?", "options": ["Former une image réelle et nette de la pièce sur le capteur CMOS", "Éclairer l'atelier en infrarouge", "Mesurer la masse de la pièce"], "rep": "Former une image réelle et nette de la pièce sur le capteur CMOS"},
            {"id": "qlm1_2", "q": "De quelle nature est l'image formée sur la matrice électronique d'une caméra industrielle ?", "options": ["Réelle et renversée", "Virtuelle et droite", "À l'infini"], "rep": "Réelle et renversée"},
            {"id": "qlm1_3", "q": "Comment réalise-t-on la « mise au point » (netteté) lorsque la distance entre la caméra et le tapis roulant change ?", "options": ["En ajustant la distance lentille-capteur x' pour vérifier 1/x' - 1/x = 1/f'", "En peignant la lentille en bleu", "En augmentant la tension du moteur"], "rep": "En ajustant la distance lentille-capteur x' pour vérifier 1/x' - 1/x = 1/f'"},
            {"id": "qlm1_4", "q": "Que se passe-t-il sur le capteur de la caméra si la bague de mise au point est mal réglée ?", "options": ["Un point objet forme une tache floue (cercle de confusion) au lieu d'un point net", "La caméra s'éteint", "L'image devient en noir et blanc"], "rep": "Un point objet forme une tache floue (cercle de confusion) au lieu d'un point net"},
            {"id": "qlm1_5", "q": "Pour observer un objet situé très loin de la caméra (x → -∞), à quelle distance de l'objectif se forme l'image nette ?", "options": ["Dans le plan focal image (x' = f')", "Sur le centre optique O", "À l'infini"], "rep": "Dans le plan focal image (x' = f')"},
            {"id": "qlm1_6", "q": "Quel composant mécanique intégré à l'objectif permet de régler la quantité de lumière et la profondeur de champ ?", "options": ["Le diaphragme (iris)", "Le fusible thermique", "Le prisme en coin de cube"], "rep": "Le diaphragme (iris)"},
            {"id": "qlm1_7", "q": "Pourquoi fermer légèrement le diaphragme d'une caméra de contrôle augmente-t-il la « profondeur de champ » ?", "options": ["Le faisceau lumineux est plus étroit, réduisant la taille de la tache floue si la pièce bouge en hauteur", "La distance focale f' devient infinie", "Le capteur chauffe moins"], "rep": "Le faisceau lumineux est plus étroit, réduisant la taille de la tache floue si la pièce bouge en hauteur"},
            {"id": "qlm1_8", "q": "Si une pièce de 20 mm donne une image de 4 mm sur le capteur CMOS, que vaut la valeur absolue du grandissement |γ| ?", "options": ["0,20 (image 5 fois plus petite)", "5,0", "20,0"], "rep": "0,20 (image 5 fois plus petite)"},
            {"id": "qlm1_9", "q": "Quelle précaution de maintenance préventive garantit la fiabilité d'un système de vision industrielle ?", "options": ["Nettoyer régulièrement la lentille frontale avec un chiffon microfibre optique sans solvant agressif", "Graisser la lentille avec de l'huile mécanique", "Frotter l'objectif avec du papier de verre fin"], "rep": "Nettoyer régulièrement la lentille frontale avec un chiffon microfibre optique sans solvant agressif"},
            {"id": "qlm1_10", "q": "Quelle relation mathématique permet au logiciel de convertir la taille en pixels sur le capteur en millimètres réels ?", "options": ["La relation de grandissement γ = A'B' / AB = x' / x", "La loi d'Ohm", "Le théorème de Bernoulli"], "rep": "La relation de grandissement γ = A'B' / AB = x' / x"},
        ],
        "trous": [
            ("1. L'objectif de la caméra forme une image ......... sur le capteur CMOS.", ["Choisir...", "réelle", "virtuelle"], "réelle", "lm_t1"),
            ("2. L'image projetée sur le capteur électronique est .........", ["Choisir...", "renversée", "droite"], "renversée", "lm_t2"),
            ("3. Régler la netteté de l'image s'appelle faire la mise au .........", ["Choisir...", "point", "foyer"], "point", "lm_t3"),
            ("4. Si l'objet est très loin, l'image se forme à la distance focale .........", ["Choisir...", "f'", "2f'"], "f'", "lm_t4"),
            ("5. Le ......... règle l'ouverture lumineuse et la profondeur de champ.", ["Choisir...", "diaphragme", "prisme"], "diaphragme", "lm_t5"),
            ("6. Le rapport taille image / taille objet s'appelle le ......... γ.", ["Choisir...", "grandissement", "grossissement"], "grandissement", "lm_t6"),
            ("7. Sur un capteur plus petit que la pièce, |γ| est ......... à 1.", ["Choisir...", "inférieur", "supérieur"], "inférieur", "lm_t7"),
            ("8. Une lentille sale provoque une image ......... et fausse le contrôle.", ["Choisir...", "floue", "nette"], "floue", "lm_t8"),
            ("9. La position du capteur x' obéit à la relation de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "lm_t9"),
            ("10. Le contrôle par caméra trie automatiquement les pièces non .........", ["Choisir...", "conformes", "lourdes"], "conformes", "lm_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qlm2_1", "q": "Quel composant optique focalise l'énergie d'un faisceau laser industriel (découpe, soudage, marquage) sur une surface minuscule ?", "options": ["Une lentille convergente de focalisation (en ZnSe ou silice fondue)", "Un miroir convexe divergent", "Une vitre dépolie"], "rep": "Une lentille convergente de focalisation (en ZnSe ou silice fondue)"},
            {"id": "qlm2_2", "q": "Où se situe le point de puissance maximale (le « point focal ») où le métal fond instantanément ?", "options": ["Au foyer image F' de la lentille convergente", "Sur le centre optique O", "À 10 mètres derrière la tôle"], "rep": "Au foyer image F' de la lentille convergente"},
            {"id": "qlm2_3", "q": "Pourquoi un faisceau laser parallèle doit-il être concentré par une lentille convergente pour découper de l'acier ?", "options": ["La concentration de toute l'énergie sur un diamètre de 0,1 mm multiplie la densité de puissance par 10 000", "La lentille change la couleur du laser en ultraviolet", "La lentille refroidit le métal"], "rep": "La concentration de toute l'énergie sur un diamètre de 0,1 mm multiplie la densité de puissance par 10 000"},
            {"id": "qlm2_4", "q": "Que se passe-t-il si la buse de découpe laser est déréglée en hauteur (tôle hors du foyer image F') ?", "options": ["Le faisceau s'élargit, la densité d'énergie chute et la découpe devient incomplète avec des bavures", "Le laser coupe deux fois plus vite", "La lentille se transforme en miroir"], "rep": "Le faisceau s'élargit, la densité d'énergie chute et la découpe devient incomplète avec des bavures"},
            {"id": "qlm2_5", "q": "Quel risque majeur encourent les lentilles de focalisation laser si des projections de métal fondu (grattons) les atteignent ?", "options": ["Les taches absorbent l'énergie laser, chauffent localement et font fissurer ou éclater la lentille", "La lentille devient plus convergente", "La distance focale double"], "rep": "Les taches absorbent l'énergie laser, chauffent localement et font fissurer ou éclater la lentille"},
            {"id": "qlm2_6", "q": "Quel élément consommable place-t-on juste sous la lentille convergente dans une tête laser pour la protéger ?", "options": ["Une lame de protection transparente (hublot consommable) et un jet de gaz sous pression", "Un carton noir", "Un filtre polarisant en plastique"], "rep": "Une lame de protection transparente (hublot consommable) et un jet de gaz sous pression"},
            {"id": "qlm2_7", "q": "Pourquoi utilise-t-on des lentilles en Séléniure de Zinc (ZnSe) plutôt qu'en verre ordinaire sur les lasers CO2 ?", "options": ["Le verre ordinaire est opaque à l'infrarouge lointain alors que le ZnSe est transparent", "Le verre ordinaire est trop lourd", "Le ZnSe coûte moins cher que le plastique"], "rep": "Le verre ordinaire est opaque à l'infrarouge lointain alors que le ZnSe est transparent"},
            {"id": "qlm2_8", "q": "Si la lentille a une focale f' = 127 mm, à quelle distance de la lentille doit se trouver la surface de la tôle ?", "options": ["À 127 mm (pile au foyer image F')", "À 254 mm", "À 10 mm"], "rep": "À 127 mm (pile au foyer image F')"},
            {"id": "qlm2_9", "q": "Quel contrôle de maintenance réalise-t-on après le remplacement d'une lentille de focalisation laser ?", "options": ["Un tir d'impact sur papier thermique pour vérifier le centrage et la finesse du point focal", "Un test de résistance au marteau", "Une mesure au voltmètre"], "rep": "Un tir d'impact sur papier thermique pour vérifier le centrage et la finesse du point focal"},
            {"id": "qlm2_10", "q": "Quelle règle de sécurité est impérative lors de la maintenance d'une tête optique laser ?", "options": ["Consigner la source laser et porter des lunettes filtrantes adaptées à la longueur d'onde", "Regarder directement dans la buse pour vérifier le point rouge", "Nettoyer la lentille à mains nues avec les doigts"], "rep": "Consigner la source laser et porter des lunettes filtrantes adaptées à la longueur d'onde"},
        ],
        "trous": [
            ("1. Une lentille convergente concentre un faisceau laser parallèle en son foyer ......... F'.", ["Choisir...", "image", "objet"], "image", "lm_t1"),
            ("2. La concentration de l'énergie augmente fortement la ......... de puissance.", ["Choisir...", "densité", "vitesse"], "densité", "lm_t2"),
            ("3. Si la tôle n'est pas au foyer F', la découpe présente des .........", ["Choisir...", "bavures", "reflets bleus"], "bavures", "lm_t3"),
            ("4. Une tache sur la lentille absorbe le laser et provoque sa ......... thermique.", ["Choisir...", "rupture", "dilatation douce"], "rupture", "lm_t4"),
            ("5. Un ......... de protection transparent protège la lentille des projections.", ["Choisir...", "hublot", "miroir"], "hublot", "lm_t5"),
            ("6. Un gaz sous ......... chasse les fumées loin de l'optique.", ["Choisir...", "pression", "vide"], "pression", "lm_t6"),
            ("7. Les lasers CO2 utilisent des lentilles spéciales en .........", ["Choisir...", "ZnSe", "carton"], "ZnSe", "lm_t7"),
            ("8. Il ne faut jamais toucher une lentille optique avec les .........", ["Choisir...", "doigts", "gants propres"], "doigts", "lm_t8"),
            ("9. On vérifie le centrage du faisceau par un tir sur papier .........", ["Choisir...", "thermique", "glacé"], "thermique", "lm_t9"),
            ("10. Le port de ......... de protection laser est obligatoire lors des essais.", ["Choisir...", "lunettes", "bouchons"], "lunettes", "lm_t10"),
        ]
    }
}


def mettre_a_jour_len_maint_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles convergentes adapté à la maintenance industrielle."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        dist_obj = st.session_state.get("slider_lm_s0", 3.5)
        f_loupe = 5.0
        x0, y0 = 330.0, 135.0
        echelle = 25.0

        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x0, x0)), list((35, 225)), color="#38bdf8", lw=3)
        ax.text(x0, 28, "Loupe (f' = 5,0 cm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        xf = x0 - f_loupe * echelle
        ax.scatter(xf, y0, color="#fde047", s=40)
        ax.text(xf, y0 + 14, "F", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        xa = x0 - dist_obj * echelle
        h_obj = 24.0
        ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
        ax.text(xa, y0 + 14, f"Fissure ({dist_obj:.1f} cm)", color="#fca5a5", fontsize=7.5, fontweight="bold", ha="center")

        if dist_obj < f_loupe:
            x_img = (f_loupe * (-dist_obj)) / (-dist_obj + f_loupe)
            gamma = x_img / (-dist_obj)
            xap = x0 + x_img * echelle
            h_img = h_obj * gamma
            if xap >= 25:
                ax.annotate("", xy=(xap, y0 - h_img), xytext=(xap, y0), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2.5, ls="--"))
                ax.text(xap, y0 + 14, f"Image virtuelle (×{gamma:.1f})", color="#86efac", fontsize=7.5, fontweight="bold", ha="center")
            ax.plot(list((xa, x0)), list((y0 - h_obj, y0 - h_obj)), color="#eab308", lw=1.5)
            ax.plot(list((x0, 520)), list((y0 - h_obj, y0 - h_obj + (520 - x0) * (h_obj / (f_loupe * echelle)))), color="#eab308", lw=1.5)
            ax.plot(list((xa, 520)), list((y0 - h_obj, y0 + (520 - x0) * (h_obj / (dist_obj * echelle)))), color="#3b82f6", lw=1.5)
            statut = f"EFFET LOUPE OK : Image droite agrandie γ = +{gamma:.2f} (Inspection nette)"
            c_stat = "#22c55e"
            diag = f"γ = +{gamma:.2f}"
        else:
            statut = "HORS CHAMP LOUPE : Rapprochez la loupe à moins de 5,0 cm de la pièce !"
            c_stat = "#ef4444"
            diag = "INVERSÉE"

        ax.text(25, 18, "MAINTENANCE VISUELLE : CONTRÔLE DE MICRO-FISSURES À LA LOUPE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.lm_mesure_courante = (f"x = -{dist_obj:.1f} cm", "f' = 5,0 cm", diag, "CONFORME" if dist_obj < f_loupe else "TROP LOIN")

    elif sujet_idx == 1:
        pos_capteur_mm = st.session_state.get("slider_lm_s1", 55.0)
        f_obj_mm = 50.0
        dist_piece_mm = 500.0
        x_net_mm = (f_obj_mm * (-dist_piece_mm)) / (-dist_piece_mm + f_obj_mm)

        x0, y0 = 260.0, 130.0
        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.add_patch(patches.Rectangle((40, 95), 16, 70, facecolor="#f97316", edgecolor="white"))
        ax.text(48, 85, "Pièce (500 mm)", color="#fdba74", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((x0, x0)), list((45, 215)), color="#38bdf8", lw=3.5)
        ax.text(x0, 36, "Objectif (f' = 50 mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        x_net_px = x0 + (x_net_mm - 40.0) * 10.0
        x_cap_px = x0 + (pos_capteur_mm - 40.0) * 10.0

        ax.plot(list((48, x0)), list((95, 70)), color="#eab308", lw=1.5)
        ax.plot(list((48, x0)), list((95, 190)), color="#eab308", lw=1.5)
        ax.plot(list((x0, x_net_px)), list((70, 155)), color="#22c55e", lw=1.8)
        ax.plot(list((x0, x_net_px)), list((190, 155)), color="#22c55e", lw=1.8)

        ax.plot(list((x_cap_px, x_cap_px)), list((65, 195)), color="#ef4444", lw=4)
        ax.text(x_cap_px, 56, f"Capteur CMOS ({pos_capteur_mm:.1f} mm)", color="#fca5a5", fontsize=7.5, fontweight="bold", ha="center")

        ecart_mm = abs(pos_capteur_mm - x_net_mm)
        if ecart_mm <= 0.8:
            statut = f"IMAGE NETTE SUR CAPTEUR (x' = {pos_capteur_mm:.1f} mm) : Contrôle dimensionnel validé !"
            c_stat = "#22c55e"
            diag = "NETTE (OK)"
        else:
            statut = f"IMAGE FLOUE (Écart {ecart_mm:.1f} mm) : Réglez le capteur vers {x_net_mm:.1f} mm."
            c_stat = "#ef4444"
            diag = "FLOUE"

        ax.text(25, 18, "VISION INDUSTRIELLE : MISE AU POINT D'UNE CAMÉRA DE CONTRÔLE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.lm_mesure_courante = (f"x' = {pos_capteur_mm:.1f} mm", f"Cible = {x_net_mm:.1f} mm", f"Écart = {ecart_mm:.1f} mm", diag)

    else:
        dist_tole_mm = st.session_state.get("slider_lm_s2", 120.0)
        f_laser_mm = 127.0
        x0, y0 = 200.0, 130.0

        ax.plot(list((x0, x0)), list((45, 215)), color="#38bdf8", lw=4)
        ax.text(x0, 36, "Lentille ZnSe (f' = 127 mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        xfp = x0 + f_laser_mm * 2.2
        x_tole = x0 + dist_tole_mm * 2.2

        for dy in [-55, -28, 0, 28, 55]:
            ax.plot(list((40, x0)), list((y0 + dy, y0 + dy)), color="#ef4444", lw=2)
            pente = -dy / (xfp - x0)
            ax.plot(list((x0, x_tole)), list((y0 + dy, y0 + dy + pente * (x_tole - x0))), color="#ef4444", lw=2)

        ax.plot(list((x_tole, x_tole)), list((50, 210)), color="#94a3b8", lw=5)
        ax.text(x_tole + 8, 130, f"Tôle acier\n({dist_tole_mm:.0f} mm)", color="#cbd5e1", fontsize=7.5, fontweight="bold", va="center")

        ecart_f = abs(dist_tole_mm - f_laser_mm)
        if ecart_f <= 2.0:
            statut = "POINT FOCAL EXACT (127 mm) : Densité d'énergie maximale, découpe nette !"
            c_stat = "#22c55e"
            diag = "DÉCOUPE NETTE"
        else:
            statut = f"DÉFOCALISÉ (Écart {ecart_f:.0f} mm) : Le spot est trop large, réglez la buse à 127 mm."
            c_stat = "#ef4444"
            diag = "BAVURES"

        ax.text(25, 18, "USINAGE LASER : FOCALISATION DU FAISCEAU AU FOYER IMAGE F'", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.lm_mesure_courante = (f"Buse = {dist_tole_mm:.0f} mm", "Focale = 127 mm", f"Écart = {ecart_f:.0f} mm", diag)

    return fig


def afficher_atelier_len_maint(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet de maintenance ci-dessus.")
        return
    banque = BANQUES_LEN_MAINT[sujet_idx]
    cle_ordre = f"ordre_quiz_lm_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Maintenance (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"lm_at4_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Maintenance (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")



BANQUES_LEN_TP = {
    0: {
        "questions": [
            {"id": "qltp0_1", "q": "Quel système optique composé de lentilles convergentes équipe la lunette d'un niveau optique de chantier ?", "options": ["Un objectif convergent et un oculaire convergent", "Un simple miroir plan opaque", "Un prisme dispersif en plastique"], "rep": "Un objectif convergent et un oculaire convergent"},
            {"id": "qltp0_2", "q": "Où l'objectif convergent du niveau optique forme-t-il l'image réelle de la mire graduée ?", "options": ["Sur le plan du réticule (fils stadimétriques) à l'intérieur de la lunette", "Sur le trépied", "Derrière l'œil de l'opérateur"], "rep": "Sur le plan du réticule (fils stadimétriques) à l'intérieur de la lunette"},
            {"id": "qltp0_3", "q": "Quel est le rôle de la molette de mise au point latérale sur un niveau optique de chantier ?", "options": ["Déplacer une lentille interne pour amener l'image de la mire exactement sur le réticule", "Changer la couleur du niveau", "Régler la hauteur du trépied"], "rep": "Déplacer une lentille interne pour amener l'image de la mire exactement sur le réticule"},
            {"id": "qltp0_4", "q": "Quel rôle joue l'oculaire situé du côté de l'œil du chef de chantier ?", "options": ["Il agit comme une loupe pour grossir l'image de la mire et les traits du réticule", "Il éclaire la mire à 100 mètres", "Il mesure la température de l'air"], "rep": "Il agit comme une loupe pour grossir l'image de la mire et les traits du réticule"},
            {"id": "qltp0_5", "q": "Comment calcule-t-on la distance horizontale D entre le niveau optique et la mire grâce aux fils stadimétriques ?", "options": ["D = 100 × (Lecture fil haut - Lecture fil bas)", "D = Lecture fil haut + Lecture fil bas", "D = Lecture centrale / 100"], "rep": "D = 100 × (Lecture fil haut - Lecture fil bas)"},
            {"id": "qltp0_6", "q": "Que signifie un « défaut de parallaxe » lorsque l'opérateur bouge légèrement l'œil devant l'oculaire ?", "options": ["L'image de la mire bouge par rapport aux fils du réticule car la mise au point est mal réglée", "La batterie de la mire est vide", "Le trépied s'enfonce dans la terre"], "rep": "L'image de la mire bouge par rapport aux fils du réticule car la mise au point est mal réglée"},
            {"id": "qltp0_7", "q": "Quel organe mécanique suspendu à l'intérieur du niveau optique maintient automatiquement l'axe de visée horizontal ?", "options": ["Le compensateur pendulaire optique", "Le niveau à mercure liquide", "Le frein à disque"], "rep": "Le compensateur pendulaire optique"},
            {"id": "qltp0_8", "q": "Quel est le grossissement typique de la lunette d'un niveau optique de chantier TP ?", "options": ["24× à 32×", "2×", "500×"], "rep": "24× à 32×"},
            {"id": "qltp0_9", "q": "Si le fil stadimétrique haut lit 1,650 m et le fil bas lit 1,250 m sur la mire, quelle est la distance D ?", "options": ["40,0 mètres (100 × 0,400 m)", "4,0 mètres", "125 mètres"], "rep": "40,0 mètres (100 × 0,400 m)"},
            {"id": "qltp0_10", "q": "Pourquoi le pare-soleil coulissant à l'avant de l'objectif est-il utile sur un chantier ensoleillé ?", "options": ["Il évite les reflets parasites sur la lentille frontale et améliore le contraste de la mire", "Il augmente la distance focale de 10 mètres", "Il protège contre la foudre"], "rep": "Il évite les reflets parasites sur la lentille frontale et améliore le contraste de la mire"},
        ],
        "trous": [
            ("1. La lunette de chantier associe un ......... convergent et un oculaire.", ["Choisir...", "objectif", "prisme"], "objectif", "ltp_t1"),
            ("2. L'image de la mire se forme sur le plan du ......... gradué.", ["Choisir...", "réticule", "trépied"], "réticule", "ltp_t2"),
            ("3. L'......... agit comme une loupe pour observer les graduations.", ["Choisir...", "oculaire", "interrupteur"], "oculaire", "ltp_t3"),
            ("4. On calcule la distance D en multipliant l'écart stadimétrique par .........", ["Choisir...", "100", "10"], "100", "ltp_t4"),
            ("5. Le ......... automatique garde l'axe optique parfaitement horizontal.", ["Choisir...", "compensateur", "variateur"], "compensateur", "ltp_t5"),
            ("6. La molette latérale permet de régler la ......... au point.", ["Choisir...", "mise", "vitesse"], "mise", "ltp_t6"),
            ("7. Si l'image bouge devant les fils quand on déplace l'œil, il y a .........", ["Choisir...", "parallaxe", "réflexion totale"], "parallaxe", "ltp_t7"),
            ("8. Une lunette de chantier grossit généralement environ ......... fois.", ["Choisir...", "24", "2"], "24", "ltp_t8"),
            ("9. On lit la cote altimétrique sur une ......... tenue verticalement.", ["Choisir...", "mire", "boussole"], "mire", "ltp_t9"),
            ("10. Les lentilles de l'objectif obéissent à la relation de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "ltp_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qltp1_1", "q": "Quel type de lentille convergente équipe les feux de balisage de chantier, les gyrophares d'engins et les phares côtiers ?", "options": ["Une lentille de Fresnel (à échelons concentriques)", "Une lentille biconcave divergente", "Une plaque d'acier poli"], "rep": "Une lentille de Fresnel (à échelons concentriques)"},
            {"id": "qltp1_2", "q": "Quel est l'avantage majeur d'une lentille de Fresnel par rapport à une lentille convergente classique de même diamètre ?", "options": ["Elle est beaucoup plus fine, légère et économique tout en gardant la même distance focale f'", "Elle fonctionne sans ampoule ni LED", "Elle absorbe 90 % de la lumière"], "rep": "Elle est beaucoup plus fine, légère et économique tout en gardant la même distance focale f'"},
            {"id": "qltp1_3", "q": "Où place-t-on la source lumineuse (LED ou lampe) par rapport à la lentille de Fresnel pour projeter un faisceau horizontal lointain ?", "options": ["Au foyer objet F de la lentille de Fresnel", "Collée contre la surface externe", "À l'infini derrière le feu"], "rep": "Au foyer objet F de la lentille de Fresnel"},
            {"id": "qltp1_4", "q": "Comment ressortent les rayons lumineux issus du foyer F après avoir traversé les anneaux concentriques d'une lentille de Fresnel ?", "options": ["Parallèles à l'axe optique (faisceau concentré à longue portée)", "Divergents dans toutes les directions", "Réfléchis vers l'arrière"], "rep": "Parallèles à l'axe optique (faisceau concentré à longue portée)"},
            {"id": "qltp1_5", "q": "Pourquoi conserve-t-on uniquement la courbure des surfaces sous forme d'anneaux dans une lentille de Fresnel ?", "options": ["Parce que c'est l'inclinaison des faces d'entrée et de sortie qui dévie les rayons, pas l'épaisseur centrale du verre", "Pour décorer le gyrophare", "Pour refroidir l'ampoule par convection"], "rep": "Parce que c'est l'inclinaison des faces d'entrée et de sortie qui dévie les rayons, pas l'épaisseur centrale du verre"},
            {"id": "qltp1_6", "q": "Quel matériau polymère léger est utilisé pour mouler les lentilles de Fresnel des feux de chantier ?", "options": ["Le PMMA (Plexiglas) ou le polycarbonate résistant aux chocs", "La fonte d'aluminium", "Le béton fibré"], "rep": "Le PMMA (Plexiglas) ou le polycarbonate résistant aux chocs"},
            {"id": "qltp1_7", "q": "Que se passe-t-il si l'ampoule d'un feu de balisage de chantier est décalée hors du foyer F de la lentille de Fresnel ?", "options": ["Le faisceau diverge vers le ciel ou le sol et perd sa portée de signalisation", "La lumière devient verte", "La fréquence de clignotement double"], "rep": "Le faisceau diverge vers le ciel ou le sol et perd sa portée de signalisation"},
            {"id": "qltp1_8", "q": "Dans quel autre équipement de travaux publics ou d'énergie trouve-t-on de grandes lentilles de Fresnel convergentes ?", "options": ["Les concentrateurs solaires thermiques et photovoltaïques", "Les marteaux-piqueurs pneumatiques", "Les pelleteuses à chenilles"], "rep": "Les concentrateurs solaires thermiques et photovoltaïques"},
            {"id": "qltp1_9", "q": "Quelle est la propriété optique principale d'une lentille de Fresnel utilisée en concentrateur solaire ?", "options": ["Elle fait converger les rayons parallèles du Soleil en son foyer image F' à très haute température", "Elle bloque les rayons infrarouges", "Elle disperse la lumière blanche"], "rep": "Elle fait converger les rayons parallèles du Soleil en son foyer image F' à très haute température"},
            {"id": "qltp1_10", "q": "En quelle année le physicien français Augustin Fresnel a-t-il mis au point cette lentille convergente à échelons ?", "options": ["1822", "1492", "1969"], "rep": "1822"},
        ],
        "trous": [
            ("1. Les feux de chantier utilisent une lentille convergente de .........", ["Choisir...", "Fresnel", "Newton"], "Fresnel", "ltp_t1"),
            ("2. Cette lentille est découpée en ......... concentriques pour réduire son poids.", ["Choisir...", "anneaux", "cubes"], "anneaux", "ltp_t2"),
            ("3. La LED est placée au foyer ......... F de la lentille.", ["Choisir...", "objet", "image"], "objet", "ltp_t3"),
            ("4. Les rayons émergents repartent ......... à l'axe optique.", ["Choisir...", "parallèles", "perpendiculaires"], "parallèles", "ltp_t4"),
            ("5. Le faisceau concentré augmente la ......... lumineuse de signalisation.", ["Choisir...", "portée", "masse"], "portée", "ltp_t5"),
            ("6. Les lentilles de chantier sont moulées en ......... résistant aux chocs.", ["Choisir...", "polycarbonate", "céramique"], "polycarbonate", "ltp_t6"),
            ("7. Utilisée à l'envers au Soleil, elle concentre la chaleur au foyer ......... F'.", ["Choisir...", "image", "objet"], "image", "ltp_t7"),
            ("8. Elle remplace avantageusement une lentille épaisse et très .........", ["Choisir...", "lourde", "souple"], "lourde", "ltp_t8"),
            ("9. Si la source quitte le foyer F, le faisceau ......... et éclaire moins loin.", ["Choisir...", "diverge", "s'éteint"], "diverge", "ltp_t9"),
            ("10. Chaque échelon dévie la lumière par ......... aux dioptres.", ["Choisir...", "réfraction", "aimantation"], "réfraction", "ltp_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qltp2_1", "q": "Dans un appareil photo de suivi de chantier ou un drone photogrammétrique TP, quelle lentille forme l'image du terrain sur le capteur ?", "options": ["Un objectif photographique convergent", "Un miroir plan", "Un prisme en coin de cube"], "rep": "Un objectif photographique convergent"},
            {"id": "qltp2_2", "q": "Si un drone vole à une altitude H = 100 m avec un objectif de focale f' = 20 mm (0,020 m), que vaut l'échelle (le grandissement |γ|) ?", "options": ["1 / 5 000 (soit |γ| = f' / H = 0,020 / 100 = 0,0002)", "1 / 20", "1 / 100"], "rep": "1 / 5 000 (soit |γ| = f' / H = 0,020 / 100 = 0,0002)"},
            {"id": "qltp2_3", "q": "Comment appelle-t-on la technique TP qui consiste à reconstituer un modèle 3D d'un terrassement à partir de photos prises sous plusieurs angles ?", "options": ["La photogrammétrie", "La calorimétrie", "L'électrolyse"], "rep": "La photogrammétrie"},
            {"id": "qltp2_4", "q": "Pour photographier un ouvrage d'art situé à grande distance (x → -∞), où se situe le capteur par rapport à l'objectif ?", "options": ["À la distance focale f' de l'objectif (x' ≈ f')", "À 2 × f'", "À 10 × f'"], "rep": "À la distance focale f' de l'objectif (x' ≈ f')"},
            {"id": "qltp2_5", "q": "Quel objectif choisit-on pour photographier un grand chantier dans son ensemble avec un large champ de vision ?", "options": ["Un objectif grand-angle (courte distance focale f', ex : 16 mm ou 24 mm)", "Un téléobjectif à très longue focale (400 mm)", "Un microscope"], "rep": "Un objectif grand-angle (courte distance focale f', ex : 16 mm ou 24 mm)"},
            {"id": "qltp2_6", "q": "Quel objectif utilise le conducteur de travaux pour inspecter un détail d'armature en haut d'un pylône de pont depuis le sol ?", "options": ["Un téléobjectif convergent à longue focale f' (fort grandissement)", "Un objectif grand-angle 12 mm", "Une vitre plane"], "rep": "Un téléobjectif convergent à longue focale f' (fort grandissement)"},
            {"id": "qltp2_7", "q": "De quelle nature est l'image du chantier formée sur le capteur numérique de l'appareil photo ?", "options": ["Réelle, renversée et fortement rétrécie", "Virtuelle et droite", "Plus grande que le chantier réel"], "rep": "Réelle, renversée et fortement rétrécie"},
            {"id": "qltp2_8", "q": "Pourquoi calibre-t-on précisément la distance focale f' d'une caméra de drone avant un levé de cubatures de terre ?", "options": ["Pour garantir l'exactitude géométrique du calcul des volumes de déblais et remblais", "Pour économiser la batterie du drone", "Pour rendre les nuages plus blancs"], "rep": "Pour garantir l'exactitude géométrique du calcul des volumes de déblais et remblais"},
            {"id": "qltp2_9", "q": "Si la distance focale f' de l'objectif double à altitude constante, comment évolue la taille de l'image d'un engin sur le capteur ?", "options": ["Elle double également (proportionnelle à f')", "Elle est divisée par 4", "Elle ne change pas"], "rep": "Elle double également (proportionnelle à f')"},
            {"id": "qltp2_10", "q": "Quelle formule relie la taille réelle de l'ouvrage AB, la taille sur le capteur A'B', la focale f' et la distance D ?", "options": ["A'B' / AB = f' / D", "A'B' = AB × D", "f' = AB + D"], "rep": "A'B' / AB = f' / D"},
        ],
        "trous": [
            ("1. La reconstitution 3D d'un chantier par photos s'appelle la .........", ["Choisir...", "photogrammétrie", "thermographie"], "photogrammétrie", "ltp_t1"),
            ("2. L'objectif du drone est une lentille mince .........", ["Choisir...", "convergente", "divergente"], "convergente", "ltp_t2"),
            ("3. Pour un chantier éloigné, l'image se forme au foyer ......... F'.", ["Choisir...", "image", "objet"], "image", "ltp_t3"),
            ("4. Un objectif à courte focale f' offre un champ de vision .........-angle.", ["Choisir...", "grand", "étroit"], "grand", "ltp_t4"),
            ("5. Un ......... à longue focale permet de zoomer sur un détail éloigné.", ["Choisir...", "téléobjectif", "microscope"], "téléobjectif", "ltp_t5"),
            ("6. L'image enregistrée sur le capteur est réelle et .........", ["Choisir...", "renversée", "droite"], "renversée", "ltp_t6"),
            ("7. Plus l'altitude H du drone augmente, plus le grandissement |γ| .........", ["Choisir...", "diminue", "augmente"], "diminue", "ltp_t7"),
            ("8. Le calibrage de la focale f' garantit le calcul exact des ......... de terre.", ["Choisir...", "volumes", "couleurs"], "volumes", "ltp_t8"),
            ("9. On a la relation de proportionnalité A'B' / AB ≈ f' / .........", ["Choisir...", "D", "2"], "D", "ltp_t9"),
            ("10. Le calcul des positions images repose sur la loi de .........", ["Choisir...", "Descartes", "Pascal"], "Descartes", "ltp_t10"),
        ]
    }
}


def mettre_a_jour_len_tp_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles convergentes adapté aux Travaux Publics."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        dist_mire_m = st.session_state.get("slider_ltp_s0", 40.0)
        lec_bas = 1.250
        ecart_m = dist_mire_m / 100.0
        lec_haut = lec_bas + ecart_m
        lec_niv = (lec_haut + lec_bas) / 2.0

        ax.add_patch(patches.Rectangle((45, 105), 65, 32, facecolor="#eab308", edgecolor="white", lw=1.5))
        ax.text(77, 94, "Niveau Optique\n(Lunette 24×)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        xm = 180.0 + (dist_mire_m / 80.0) * 350.0
        ax.add_patch(patches.Rectangle((xm, 45), 18, 175, facecolor="white", edgecolor="#94a3b8", lw=1.5))
        ax.text(xm + 9, 36, f"Mire ({dist_mire_m:.0f} m)", color="#cbd5e1", fontsize=7.5, fontweight="bold", ha="center")

        y_mid = 121.0
        dy_stad = (dist_mire_m / 80.0) * 55.0
        ax.plot(list((110, xm)), list((y_mid, y_mid)), color="#22c55e", lw=2)
        ax.plot(list((110, xm)), list((y_mid, y_mid - dy_stad)), color="#38bdf8", lw=1.3, ls="--")
        ax.plot(list((110, xm)), list((y_mid, y_mid + dy_stad)), color="#38bdf8", lw=1.3, ls="--")

        ax.text(25, 18, "TOPOGRAPHIE DE CHANTIER : LECTURE STADIMÉTRIQUE AU NIVEAU OPTIQUE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Fil haut = {lec_haut:.3f} m | Fil niveleur = {lec_niv:.3f} m | Fil bas = {lec_bas:.3f} m  =>  Distance D = {dist_mire_m:.1f} m", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.ltp_mesure_courante = (f"Haut = {lec_haut:.3f} m", f"Bas = {lec_bas:.3f} m", f"Écart = {ecart_m:.3f} m", f"D = {dist_mire_m:.1f} m")

    elif sujet_idx == 1:
        pos_led_mm = st.session_state.get("slider_ltp_s1", 80.0)
        f_fresnel_mm = 80.0
        x0, y0 = 240.0, 125.0

        ax.plot(list((x0, x0)), list((45, 205)), color="#38bdf8", lw=3)
        for y_ech in range(50, 205, 15):
            ax.plot(list((x0, x0 + 7)), list((y_ech, y_ech + 7)), color="#38bdf8", lw=1.5)
        ax.text(x0, 36, "Lentille de Fresnel (f' = 80 mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        x_led = x0 - pos_led_mm * 2.0
        ax.add_patch(patches.Circle((x_led, y0), 7, facecolor="#f59e0b", edgecolor="white", zorder=5))
        ax.text(x_led, y0 + 18, f"LED ({pos_led_mm:.0f} mm)", color="#fbbf24", fontsize=7.5, fontweight="bold", ha="center")

        ecart_led = pos_led_mm - f_fresnel_mm
        pente_sortie = -ecart_led * 0.008
        for dy in [-60, -30, 0, 30, 60]:
            ax.plot(list((x_led, x0)), list((y0, y0 + dy)), color="#fde047", lw=1.3, ls=":")
            y_end = (y0 + dy) + pente_sortie * (dy / 60.0) * 300.0
            c_f = "#22c55e" if abs(ecart_led) <= 2.0 else "#f59e0b"
            ax.annotate("", xy=(550, y_end), xytext=(x0 + 6, y0 + dy), arrowprops=dict(arrowstyle="->", color=c_f, lw=2))

        if abs(ecart_led) <= 2.0:
            statut = "FAISCEAU PARALLÈLE LONGUE PORTÉE : LED placée au foyer objet F (80 mm) !"
            c_stat = "#22c55e"
            diag = "PARALLÈLE (OK)"
        else:
            statut = f"FAISCEAU DÉRÉGLÉ (Écart {ecart_led:+.0f} mm) : Placez la LED exactement à 80 mm."
            c_stat = "#ef4444"
            diag = "DÉFOCALISÉ"

        ax.text(25, 18, "BALISAGE TP : COLLIMATION PAR LENTILLE CONVERGENTE DE FRESNEL", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.ltp_mesure_courante = (f"LED = {pos_led_mm:.0f} mm", "Foyer F = 80 mm", f"Écart = {ecart_led:+.0f} mm", diag)

    else:
        alt_drone_m = st.session_state.get("slider_ltp_s2", 80.0)
        focale_mm = st.session_state.get("slider_ltp_f_s2", 24.0)
        focale_m = focale_mm / 1000.0
        echelle_inv = int(round(alt_drone_m / focale_m))
        taille_engin_real_m = 10.0
        taille_capteur_mm = (taille_engin_real_m * focale_m / alt_drone_m) * 1000.0

        ax.add_patch(patches.Rectangle((40, 195), 520, 35, facecolor="#78350f", edgecolor="#92400e"))
        ax.add_patch(patches.Rectangle((260, 180), 80, 15, facecolor="#eab308", edgecolor="white"))
        ax.text(300, 212, "Engin de chantier (Longueur réelle AB = 10,0 m)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        y_drone = 180.0 - (alt_drone_m / 150.0) * 115.0
        ax.add_patch(patches.Rectangle((275, y_drone - 12), 50, 12, facecolor="#38bdf8", edgecolor="white"))
        ax.text(300, y_drone - 18, f"Drone TP (H = {alt_drone_m:.0f} m | f' = {focale_mm:.0f} mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        ax.plot(list((260, 300)), list((180, y_drone)), color="#22c55e", lw=1.4, ls="--")
        ax.plot(list((340, 300)), list((180, y_drone)), color="#22c55e", lw=1.4, ls="--")

        ax.text(25, 18, "PHOTOGRAMMÉTRIE DRONE TP : ÉCHELLE DE PRISE DE VUE (|γ| = f' / H)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Échelle image : 1 / {echelle_inv}  |  Taille de l'engin sur le capteur CMOS : A'B' = {taille_capteur_mm:.2f} mm", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.ltp_mesure_courante = (f"H = {alt_drone_m:.0f} m", f"f' = {focale_mm:.0f} mm", f"Échelle 1/{echelle_inv}", f"A'B' = {taille_capteur_mm:.2f} mm")

    return fig


def afficher_atelier_len_tp(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un chantier TP ci-dessus.")
        return
    banque = BANQUES_LEN_TP[sujet_idx]
    cle_ordre = f"ordre_quiz_ltp_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Travaux Publics (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"ltp_at5_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Travaux Publics (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")

BANQUES_LEN_TRANS = {
    0: {
        "questions": [
            {"id": "qltr0_1", "q": "Quel type de lentille convergente équipe les phares projecteurs modernes (lenticulaires / LED / Xénon) d'un véhicule ?", "options": ["Une lentille plan-convexe convergente à courte focale", "Une lentille biconcave divergente", "Une vitre plane dépolie"], "rep": "Une lentille plan-convexe convergente à courte focale"},
            {"id": "qltr0_2", "q": "Où est placée la source lumineuse (ou le foyer secondaire du réflecteur) par rapport à la lentille du phare projecteur ?", "options": ["Au foyer objet F de la lentille convergente", "Collée contre la glace externe du phare", "Derrière le coffre du véhicule"], "rep": "Au foyer objet F de la lentille convergente"},
            {"id": "qltr0_3", "q": "Comment ressortent les rayons lumineux issus du foyer F après avoir traversé la lentille convergente du phare ?", "options": ["Parallèles à l'axe optique pour éclairer loin sur la route", "Divergents vers le ciel uniquement", "Réfléchis vers le moteur"], "rep": "Parallèles à l'axe optique pour éclairer loin sur la route"},
            {"id": "qltr0_4", "q": "Quel élément mécanique situé près du foyer F coupe la moitié supérieure du faisceau en mode « feux de croisement » ?", "options": ["Un cache métallique (volet de coupure)", "Un filtre polarisant bleu", "Un prisme en coin de cube"], "rep": "Un cache métallique (volet de coupure)"},
            {"id": "qltr0_5", "q": "Quel avantage offre un phare lenticulaire convergent par rapport à un grand réflecteur parabolique ancien ?", "options": ["Un encombrement très compact et une coupure lumineuse très nette anti-éblouissement", "Il fonctionne sans batterie", "Il augmente la vitesse maximale du camion"], "rep": "Un encombrement très compact et une coupure lumineuse très nette anti-éblouissement"},
            {"id": "qltr0_6", "q": "Que se passe-t-il si le support de la lentille d'un phare se déboîte et s'éloigne du foyer F ?", "options": ["Le faisceau diverge ou converge trop tôt, réduisant fortement la visibilité nocturne", "Les feux passent automatiquement en plein phare", "La couleur devient verte"], "rep": "Le faisceau diverge ou converge trop tôt, réduisant fortement la visibilité nocturne"},
            {"id": "qltr0_7", "q": "Pourquoi les feux arrière et clignotants de poids lourds utilisent-ils des lentilles de Fresnel convergentes ?", "options": ["Pour concentrer la lumière des LED vers l'arrière tout en gardant un boîtier fin et léger", "Pour chauffer la remorque en hiver", "Pour bloquer la lumière du soleil"], "rep": "Pour concentrer la lumière des LED vers l'arrière tout en gardant un boîtier fin et léger"},
            {"id": "qltr0_8", "q": "Quel danger entraîne une lentille de phare fortement rayée ou encrassée par la boue ?", "options": ["Une diffusion parasite qui réduit la portée et éblouit les usagers arrivant en face", "Une hausse de la distance focale f'", "Une réflexion totale interne"], "rep": "Une diffusion parasite qui réduit la portée et éblouit les usagers arrivant en face"},
            {"id": "qltr0_9", "q": "Si la lentille frontale d'un projecteur a une distance focale f' = 40 mm (0,040 m), quelle est sa vergence C ?", "options": ["+ 25 dioptries (δ)", "+ 4 dioptries (δ)", "+ 0,4 dioptrie (δ)"], "rep": "+ 25 dioptries (δ)"},
            {"id": "qltr0_10", "q": "Quelle loi fondamentale de l'optique régit la déviation des rayons à l'entrée et à la sortie de la lentille du phare ?", "options": ["La loi de réfraction de Snell-Descartes", "La loi d'Ohm", "Le principe d'Archimède"], "rep": "La loi de réfraction de Snell-Descartes"},
        ],
        "trous": [
            ("1. Les phares projecteurs modernes utilisent une lentille mince .........", ["Choisir...", "convergente", "divergente"], "convergente", "ltr_t1"),
            ("2. La source lumineuse est placée au foyer ......... F de la lentille.", ["Choisir...", "objet", "image"], "objet", "ltr_t2"),
            ("3. Les rayons émergents repartent ......... à l'axe de la route.", ["Choisir...", "parallèles", "perpendiculaires"], "parallèles", "ltr_t3"),
            ("4. Un ......... métallique crée la coupure nette des feux de croisement.", ["Choisir...", "cache", "miroir"], "cache", "ltr_t4"),
            ("5. Ce dispositif évite d'......... les conducteurs arrivant en face.", ["Choisir...", "éblouir", "éclairer"], "éblouir", "ltr_t5"),
            ("6. Les feux arrière emploient souvent des lentilles fines de .........", ["Choisir...", "Fresnel", "Newton"], "Fresnel", "ltr_t6"),
            ("7. Une lentille de focale f' = 40 mm a une vergence de ......... dioptries.", ["Choisir...", "25", "40"], "25", "ltr_t7"),
            ("8. Une lentille sale provoque une ......... parasite de la lumière.", ["Choisir...", "diffusion", "absorption"], "diffusion", "ltr_t8"),
            ("9. Si la source s'écarte du foyer F, le faisceau ......... et éclaire moins loin.", ["Choisir...", "diverge", "s'éteint"], "diverge", "ltr_t9"),
            ("10. Le contrôle du faisceau en atelier s'effectue au .........", ["Choisir...", "régloscope", "périscope"], "régloscope", "ltr_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qltr1_1", "q": "Quel composant optique équipe la caméra frontale d'aide à la conduite (ADAS : lecture des panneaux, freinage d'urgence) derrière le pare-brise ?", "options": ["Un objectif convergent qui forme une image réelle de la route sur le capteur CMOS", "Un prisme dispersif", "Un miroir plan opaque"], "rep": "Un objectif convergent qui forme une image réelle de la route sur le capteur CMOS"},
            {"id": "qltr1_2", "q": "De quelle nature est l'image d'un panneau de limitation de vitesse formée sur le capteur électronique de la caméra ADAS ?", "options": ["Réelle, renversée et rétrécie", "Virtuelle et droite", "Plus grande que le panneau réel"], "rep": "Réelle, renversée et rétrécie"},
            {"id": "qltr1_3", "q": "Comment le calculateur ADAS estime-t-il la distance D d'un véhicule qui précède à partir de sa taille apparente A'B' sur le capteur ?", "options": ["Grâce à la relation de grandissement : D ≈ (AB × f') / A'B'", "En mesurant la température du pare-brise", "En comptant les tours de roue"], "rep": "Grâce à la relation de grandissement : D ≈ (AB × f') / A'B'"},
            {"id": "qltr1_4", "q": "Que se passe-t-il sur le capteur CMOS lorsqu'un camion devant soi freine et se rapproche rapidement (D diminue) ?", "options": ["La taille de son image A'B' sur le capteur augmente fortement, déclenchant l'alerte anticollision", "La taille de l'image diminue", "L'image disparaît"], "rep": "La taille de son image A'B' sur le capteur augmente fortement, déclenchant l'alerte anticollision"},
            {"id": "qltr1_5", "q": "Pourquoi un calibrage optique de la caméra ADAS est-il obligatoire après le remplacement d'un pare-brise ?", "options": ["Une infime variation d'angle ou de position de l'objectif fausse le calcul des distances et des trajectoires", "Pour recharger la batterie de la caméra", "Pour nettoyer l'intérieur du pare-brise"], "rep": "Une infime variation d'angle ou de position de l'objectif fausse le calcul des distances et des trajectoires"},
            {"id": "qltr1_6", "q": "Quel type d'objectif convergent équipe les caméras de recul à 180° des véhicules utilitaires et autobus ?", "options": ["Un objectif grand-angle à très courte distance focale f' (fisheye)", "Un téléobjectif à longue focale 300 mm", "Une loupe d'horloger"], "rep": "Un objectif grand-angle à très courte distance focale f' (fisheye)"},
            {"id": "qltr1_7", "q": "Où se forme l'image des objets lointains (à plus de 10 mètres) dans une caméra ADAS de focale f' = 8 mm ?", "options": ["Quasiment au foyer image F' (x' ≈ 8 mm)", "À 80 cm derrière le capteur", "Sur le capot du véhicule"], "rep": "Quasiment au foyer image F' (x' ≈ 8 mm)"},
            {"id": "qltr1_8", "q": "Quel défaut visuel affecte une caméra de recul si une goutte de boue ou de givre recouvre sa lentille convergente ?", "options": ["Les rayons ne convergent plus nettement : l'image devient floue et illisible", "La caméra zoom 10 fois", "L'image devient en relief 3D"], "rep": "Les rayons ne convergent plus nettement : l'image devient floue et illisible"},
            {"id": "qltr1_9", "q": "Si une voiture de largeur AB = 1,80 m donne une image de 0,90 mm sur un capteur avec f' = 10 mm, à quelle distance D se trouve-t-elle ?", "options": ["20 mètres (car D = 1,80 × 0,010 / 0,0009)", "2 mètres", "200 mètres"], "rep": "20 mètres (car D = 1,80 × 0,010 / 0,0009)"},
            {"id": "qltr1_10", "q": "Quelle fonction de sécurité routière repose directement sur la détection des lignes blanches par l'objectif convergent ADAS ?", "options": ["L'alerte de franchissement involontaire de ligne et le maintien dans la voie", "L'ouverture automatique du coffre", "Le réglage de la climatisation"], "rep": "L'alerte de franchissement involontaire de ligne et le maintien dans la voie"},
        ],
        "trous": [
            ("1. Les caméras ADAS utilisent un objectif ......... pour filmer la route.", ["Choisir...", "convergent", "divergent"], "convergent", "ltr_t1"),
            ("2. L'image formée sur le capteur CMOS est réelle et .........", ["Choisir...", "renversée", "droite"], "renversée", "ltr_t2"),
            ("3. Pour les objets lointains, l'image se forme au foyer ......... F'.", ["Choisir...", "image", "objet"], "image", "ltr_t3"),
            ("4. Plus un obstacle se rapproche, plus son image sur le capteur .........", ["Choisir...", "grandit", "rétrécit"], "grandit", "ltr_t4"),
            ("5. Le calculateur déduit la distance D grâce à la relation de .........", ["Choisir...", "grandissement", "réflexion"], "grandissement", "ltr_t5"),
            ("6. Après changement de pare-brise, un ......... optique de la caméra est obligatoire.", ["Choisir...", "calibrage", "graissage"], "calibrage", "ltr_t6"),
            ("7. Les caméras de recul utilisent une focale très ......... (grand-angle).", ["Choisir...", "courte", "longue"], "courte", "ltr_t7"),
            ("8. Le système ADAS permet le freinage d'......... automatique.", ["Choisir...", "urgence", "parking"], "urgence", "ltr_t8"),
            ("9. La boue sur la lentille rend l'image ......... et inutilisable.", ["Choisir...", "floue", "nette"], "floue", "ltr_t9"),
            ("10. Le calcul de position image applique la formule de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "ltr_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qltr2_1", "q": "Quel capteur optique situé derrière le pare-brise utilise deux petites lentilles convergentes pour détecter les gouttes d'eau ?", "options": ["Le capteur de pluie et de luminosité automatique", "Le capteur de pression des pneus", "Le débitmètre d'air moteur"], "rep": "Le capteur de pluie et de luminosité automatique"},
            {"id": "qltr2_2", "q": "Quel rôle joue la première lentille convergente placée devant la LED infrarouge du capteur de pluie ?", "options": ["Elle rend parallèles les rayons divergents émis par la LED (collimation)", "Elle refroidit le pare-brise", "Elle colore la pluie en bleu"], "rep": "Elle rend parallèles les rayons divergents émis par la LED (collimation)"},
            {"id": "qltr2_3", "q": "Où doit être située la puce LED émettrice par rapport à la lentille de collimation pour obtenir un faisceau parallèle ?", "options": ["Au foyer objet F de la lentille convergente", "À l'infini", "Sur le foyer image F'"], "rep": "Au foyer objet F de la lentille convergente"},
            {"id": "qltr2_4", "q": "Quel rôle joue la seconde lentille convergente placée devant la photodiode réceptrice ?", "options": ["Elle fait converger le faisceau réfléchi en son foyer image F' sur la photodiode", "Elle bloque les rayons infrarouges", "Elle disperse la lumière dans l'habitacle"], "rep": "Elle fait converger le faisceau réfléchi en son foyer image F' sur la photodiode"},
            {"id": "qltr2_5", "q": "Pourquoi concentre-t-on la lumière sur la minuscule surface de la photodiode grâce à une lentille convergente ?", "options": ["Pour maximiser le signal électrique reçu et éviter les déclenchements intempestifs", "Pour économiser le liquide lave-glace", "Pour chauffer la vitre"], "rep": "Pour maximiser le signal électrique reçu et éviter les déclenchements intempestifs"},
            {"id": "qltr2_6", "q": "Que se passe-t-il sur le signal concentré par la lentille réceptrice lorsque des gouttes de pluie tombent sur le pare-brise ?", "options": ["Une partie de la lumière s'échappe dans les gouttes d'eau : l'intensité focalisée chute et active les essuie-glaces", "L'intensité augmente de 200 %", "La lentille devient opaque"], "rep": "Une partie de la lumière s'échappe dans les gouttes d'eau : l'intensité focalisée chute et active les essuie-glaces"},
            {"id": "qltr2_7", "q": "Quel autre capteur situé dans le même boîtier utilise une lentille convergente pour allumer automatiquement les feux dans un tunnel ?", "options": ["Le capteur de luminosité ambiante", "Le capteur ABS de roue", "La sonde lambda"], "rep": "Le capteur de luminosité ambiante"},
            {"id": "qltr2_8", "q": "Si le gel optique en silicone entre le bloc de lentilles et le pare-brise est mal recollé (bulles d'air), que se passe-t-il ?", "options": ["Les rayons sont déviés hors du foyer de la photodiode et les essuie-glaces fonctionnent par intermittence anarchique", "Les feux de route restent allumés en plein jour", "Le pare-brise se fissure"], "rep": "Les rayons sont déviés hors du foyer de la photodiode et les essuie-glaces fonctionnent par intermittence anarchique"},
            {"id": "qltr2_9", "q": "Quelle longueur d'onde utilise la LED du capteur de pluie pour ne pas gêner le conducteur la nuit ?", "options": ["L'infrarouge (invisible à l'œil humain)", "Le vert fluo", "Le blanc haute puissance"], "rep": "L'infrarouge (invisible à l'œil humain)"},
            {"id": "qltr2_10", "q": "Quelle est la vergence d'une micro-lentille convergente de capteur de focale f' = 10 mm (0,010 m) ?", "options": ["+ 100 dioptries (δ)", "+ 10 dioptries (δ)", "+ 1 dioptrie (δ)"], "rep": "+ 100 dioptries (δ)"},
        ],
        "trous": [
            ("1. Le capteur de pluie utilise deux micro-lentilles .........", ["Choisir...", "convergentes", "divergentes"], "convergentes", "ltr_t1"),
            ("2. La LED infrarouge est placée au foyer ......... F de la première lentille.", ["Choisir...", "objet", "image"], "objet", "ltr_t2"),
            ("3. Le faisceau émis devient alors ......... avant d'entrer dans le pare-brise.", ["Choisir...", "parallèle", "divergent"], "parallèle", "ltr_t3"),
            ("4. La seconde lentille concentre la lumière au foyer ......... F' sur le capteur.", ["Choisir...", "image", "objet"], "image", "ltr_t4"),
            ("5. Le récepteur optique est une ......... sensible à l'infrarouge.", ["Choisir...", "photodiode", "résistance"], "photodiode", "ltr_t5"),
            ("6. En cas de pluie, l'intensité lumineuse focalisée .........", ["Choisir...", "diminue", "double"], "diminue", "ltr_t6"),
            ("7. La baisse de signal déclenche automatiquement les .........-glaces.", ["Choisir...", "essuie", "lave"], "essuie", "ltr_t7"),
            ("8. Un ......... en silicone assure le couplage optique avec le verre.", ["Choisir...", "gel", "aimant"], "gel", "ltr_t8"),
            ("9. Une lentille de focale f' = 10 mm a une vergence de ......... dioptries.", ["Choisir...", "100", "10"], "100", "ltr_t9"),
            ("10. Le capteur de ......... commande aussi l'allumage des phares dans les tunnels.", ["Choisir...", "luminosité", "pression"], "luminosité", "ltr_t10"),
        ]
    }
}


def mettre_a_jour_len_trans_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles convergentes adapté au Transport Routier."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        pos_led = st.session_state.get("slider_ltr_s0", 40.0)
        mode_feux = st.session_state.get("radio_ltr_feux_s0", "Feux de croisement (Volet actif)")
        f_phare = 40.0
        x0, y0 = 230.0, 125.0

        ax.plot(list((x0, x0)), list((45, 205)), color="#38bdf8", lw=4)
        ax.text(x0, 34, "Lentille Phare (f' = 40 mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        x_src = x0 - pos_led * 2.5
        ax.add_patch(patches.Circle((x_src, y0), 7, facecolor="#fde047", edgecolor="#f59e0b", zorder=5))
        ax.text(x_src, y0 + 18, f"Source ({pos_led:.0f} mm)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        est_code = "croisement" in mode_feux
        if est_code:
            ax.add_patch(patches.Rectangle((x_src + 15, y0), 6, 45, facecolor="#ef4444", edgecolor="white", zorder=5))
            ax.text(x_src + 18, y0 + 56, "Volet coupure", color="#fca5a5", fontsize=7, fontweight="bold", ha="center")

        ecart = pos_led - f_phare
        pente_div = -ecart * 0.008
        for dy in [-55, -25, 25, 55]:
            if est_code and dy > 0:
                ax.plot(list((x_src, x_src + 15)), list((y0, y0 + dy * 0.3)), color="#ef4444", lw=1.2, ls=":")
                continue
            ax.plot(list((x_src, x0)), list((y0, y0 + dy)), color="#fde047", lw=1.3, ls=":")
            pente_out = (0.04 if est_code else 0.0) + pente_div * (dy / 55.0)
            y_end = (y0 + dy) + pente_out * 320.0
            c_ray = "#22c55e" if abs(ecart) <= 1.5 else "#f59e0b"
            ax.annotate("", xy=(560, y_end), xytext=(x0, y0 + dy), arrowprops=dict(arrowstyle="->", color=c_ray, lw=2))

        statut = "FAISCEAU CALIBRÉ : Coupure nette anti-éblouissement !" if abs(ecart) <= 1.5 else f"DÉRÉGLÉ (Écart {ecart:+.0f} mm) : Placez la source à 40 mm."
        c_stat = "#22c55e" if abs(ecart) <= 1.5 else "#ef4444"
        ax.text(25, 18, "ÉCLAIRAGE TRANSPORT : PHARE LENTICULAIRE À LENTILLE CONVERGENTE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.ltr_mesure_courante = (f"Pos = {pos_led:.0f} mm", mode_feux[:17], f"Écart = {ecart:+.0f} mm", "CONFORME" if abs(ecart) <= 1.5 else "DÉRÉGLÉ")

    elif sujet_idx == 1:
        dist_veh_m = st.session_state.get("slider_ltr_s1", 35.0)
        f_adas_mm = 12.0
        largeur_camion_m = 2.50
        taille_capteur_mm = (largeur_camion_m * (f_adas_mm / 1000.0) / dist_veh_m) * 1000.0

        ax.add_patch(patches.Rectangle((40, 185), 520, 40, facecolor="#334155", edgecolor="#64748b"))
        ax.add_patch(patches.Rectangle((40, 115), 55, 70, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(67, 150, "Caméra\nADAS", color="white", fontsize=7.5, fontweight="bold", ha="center", va="center")

        xc = 140.0 + (dist_veh_m / 80.0) * 380.0
        ax.add_patch(patches.Rectangle((xc, 110), 65, 75, facecolor="#f97316", edgecolor="white", lw=1.5))
        ax.text(xc + 32, 148, f"Véhicule\n({dist_veh_m:.0f} m)", color="white", fontsize=7.5, fontweight="bold", ha="center", va="center")

        ax.plot(list((95, xc)), list((135, 110)), color="#22c55e", lw=1.4, ls="--")
        ax.plot(list((95, xc)), list((135, 185)), color="#22c55e", lw=1.4, ls="--")

        alerte = dist_veh_m <= 18.0
        statut = f"ALERTE COLLISION (D = {dist_veh_m:.0f} m) : Image capteur A'B' = {taille_capteur_mm:.2f} mm -> Freinage !" if alerte else f"DISTANCE SÉCURITÉ OK (D = {dist_veh_m:.0f} m) : Image capteur A'B' = {taille_capteur_mm:.2f} mm."
        c_stat = "#ef4444" if alerte else "#22c55e"
        ax.text(25, 18, "AIDE À LA CONDUITE (ADAS) : MESURE DE DISTANCE PAR OBJECTIF CONVERGENT", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.ltr_mesure_courante = (f"D = {dist_veh_m:.0f} m", "f' = 12 mm", f"A'B' = {taille_capteur_mm:.2f} mm", "FREINAGE" if alerte else "SÉCURITÉ OK")

    else:
        intensite_pluie = st.session_state.get("slider_ltr_s2", 20)
        signal_mv = max(120, 1000 - intensite_pluie * 8)
        x0, y0 = 280.0, 130.0

        ax.plot(list((x0, x0)), list((55, 205)), color="#38bdf8", lw=3.5)
        ax.text(x0, 44, "Lentille Réceptrice (f' = 10 mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        xfp = x0 + 140.0
        ax.add_patch(patches.Rectangle((xfp, 118), 14, 24, facecolor="#22c55e", edgecolor="white"))
        ax.text(xfp + 7, 108, "Photodiode (F')", color="#86efac", fontsize=7.5, fontweight="bold", ha="center")

        alpha_ray = max(0.25, 1.0 - intensite_pluie / 110.0)
        for dy in [-50, -25, 0, 25, 50]:
            ax.plot(list((60, x0)), list((y0 + dy, y0 + dy)), color="#ef4444", lw=2, alpha=alpha_ray)
            ax.plot(list((x0, xfp)), list((y0 + dy, y0)), color="#ef4444", lw=2, alpha=alpha_ray)

        actif = signal_mv < 650
        statut = f"PLUIE DÉTECTÉE ({intensite_pluie} %) : Signal focalisé = {signal_mv} mV -> Essuie-glaces ACTIFS" if actif else f"PARE-BRISE SEC ({intensite_pluie} %) : Signal focalisé = {signal_mv} mV -> Veille"
        c_stat = "#38bdf8" if actif else "#22c55e"
        ax.text(25, 18, "CAPTEUR OPTIQUE : FOCALISATION INFRAROUGE SUR PHOTODIODE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.ltr_mesure_courante = (f"Pluie = {intensite_pluie} %", f"Signal = {signal_mv} mV", "Foyer F' = 10 mm", "ESSUYAGE ON" if actif else "VEILLE")

    return fig


def afficher_atelier_len_trans(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet Transport Routier ci-dessus.")
        return
    banque = BANQUES_LEN_TRANS[sujet_idx]
    cle_ordre = f"ordre_quiz_ltr_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Transport Routier (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"ltr_at6_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Transport Routier (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")


BANQUES_LEN_GEO = {
    0: {
        "questions": [
            {"id": "qlg0_1", "q": "Quel système de lentilles convergentes équipe la lunette de visée d'un théodolite ou d'une station totale ?", "options": ["Un objectif convergent à longue focale et un oculaire convergent", "Deux miroirs sphériques divergents", "Un filtre polarisant rouge"], "rep": "Un objectif convergent à longue focale et un oculaire convergent"},
            {"id": "qlg0_2", "q": "Pourquoi l'objectif d'une station totale a-t-il une grande distance focale f' et un large diamètre ?", "options": ["Pour obtenir un fort grossissement (30×) et collecter un maximum de lumière à longue distance", "Pour rendre l'appareil plus lourd", "Pour dévier le laser vers le bas"], "rep": "Pour obtenir un fort grossissement (30×) et collecter un maximum de lumière à longue distance"},
            {"id": "qlg0_3", "q": "Quel composant optique situé dans la lunette redresse l'image renversée formée par l'objectif convergent ?", "options": ["Un prisme redresseur (prisme de Porro ou en toit)", "Une pile alcaline", "Un niveau à bulle"], "rep": "Un prisme redresseur (prisme de Porro ou en toit)"},
            {"id": "qlg0_4", "q": "Sur quel plan interne de la lunette se forme l'image nette du prisme visé sur le terrain ?", "options": ["Sur le plan du réticule gravé d'une croix de visée", "Sur le trépied en bois", "Sur le clavier numérique"], "rep": "Sur le plan du réticule gravé d'une croix de visée"},
            {"id": "qlg0_5", "q": "Pourquoi le géomètre doit-il d'abord régler la netteté de la croix du réticule en tournant la bague de l'oculaire ?", "options": ["Pour adapter l'oculaire (loupe) à sa propre vue et supprimer toute erreur de parallaxe", "Pour allumer le faisceau infrarouge", "Pour mesurer la pression atmosphérique"], "rep": "Pour adapter l'oculaire (loupe) à sa propre vue et supprimer toute erreur de parallaxe"},
            {"id": "qlg0_6", "q": "Que se passe-t-il sur le trajet de la lentille interne de mise au point lorsque le géomètre vise un prisme à 20 m puis à 300 m ?", "options": ["La lentille interne se déplace pour ramener l'image exactement sur le réticule", "L'oculaire change de couleur", "La station tourne automatiquement de 180°"], "rep": "La lentille interne se déplace pour ramener l'image exactement sur le réticule"},
            {"id": "qlg0_7", "q": "Quel rôle joue la lentille de collimation placée devant l'émetteur infrarouge (IMEL) de la station totale ?", "options": ["Elle rend le faisceau de mesure parfaitement parallèle pour atteindre le prisme à plusieurs kilomètres", "Elle disperse le faisceau dans tout le champ", "Elle refroidit la diode"], "rep": "Elle rend le faisceau de mesure parfaitement parallèle pour atteindre le prisme à plusieurs kilomètres"},
            {"id": "qlg0_8", "q": "Quelle est la précision angulaire courante d'une lunette de station totale bien réglée ?", "options": ["1 à 2 secondes d'arc (soit moins de 1 mm à 100 m)", "1 degré d'arc", "5 degrés d'arc"], "rep": "1 à 2 secondes d'arc (soit moins de 1 mm à 100 m)"},
            {"id": "qlg0_9", "q": "Comment appelle-t-on le défaut optique qui provoque des liserés colorés autour des jalons visés en plein soleil ?", "options": ["L'aberration chromatique (corrigée par des doublets achromatiques)", "La réflexion totale", "La convection thermique"], "rep": "L'aberration chromatique (corrigée par des doublets achromatiques)"},
            {"id": "qlg0_10", "q": "Quelle relation mathématique gouverne la position de la lentille de mise au point en fonction de la distance D visée ?", "options": ["La relation de conjugaison de Descartes (1/x' - 1/x = 1/f')", "La loi de Joule", "La loi de Hooke"], "rep": "La relation de conjugaison de Descartes (1/x' - 1/x = 1/f')"},
        ],
        "trous": [
            ("1. La lunette d'une station totale associe un ......... convergent et un oculaire.", ["Choisir...", "objectif", "miroir"], "objectif", "lgeo_t1"),
            ("2. L'image du point visé se forme sur la croix du .........", ["Choisir...", "réticule", "trépied"], "réticule", "lgeo_t2"),
            ("3. L'......... agit comme une loupe réglable à la vue de l'opérateur.", ["Choisir...", "oculaire", "écran"], "oculaire", "lgeo_t3"),
            ("4. Une lentille interne assure la ......... au point selon la distance.", ["Choisir...", "mise", "vitesse"], "mise", "lgeo_t4"),
            ("5. Une lentille de ......... rend parallèle le faisceau infrarouge de mesure.", ["Choisir...", "collimation", "dispersion"], "collimation", "lgeo_t5"),
            ("6. Le grossissement d'une station totale est d'environ ......... fois.", ["Choisir...", "30", "3"], "30", "lgeo_t6"),
            ("7. Un doublet ......... corrige les défauts de couleur (aberrations).", ["Choisir...", "achromatique", "divergent"], "achromatique", "lgeo_t7"),
            ("8. Un mauvais réglage de netteté entraîne une erreur de .........", ["Choisir...", "parallaxe", "pesanteur"], "parallaxe", "lgeo_t8"),
            ("9. La portée avec prisme atteint plusieurs ......... grâce au faisceau parallèle.", ["Choisir...", "kilomètres", "centimètres"], "kilomètres", "lgeo_t9"),
            ("10. Le calcul de focalisation repose sur la loi de .........", ["Choisir...", "Descartes", "Ohm"], "Descartes", "lgeo_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qlg1_1", "q": "Quel instrument optique composé de deux lentilles convergentes permet au géomètre d'observer des détails fins sur un plan ou un repère proche ?", "options": ["Un microscope de lecture (ou loupe micrométrique de vernier)", "Un télescope spatial", "Un périscope naval"], "rep": "Un microscope de lecture (ou loupe micrométrique de vernier)"},
            {"id": "qlg1_2", "q": "Dans un microscope optique de laboratoire ou de métrologie, comment appelle-t-on les deux lentilles convergentes ?", "options": ["L'objectif (très courte focale) et l'oculaire", "Le prisme et le miroir", "Le diaphragme et le filtre"], "rep": "L'objectif (très courte focale) et l'oculaire"},
            {"id": "qlg1_3", "q": "De quelle nature est l'image intermédiaire A1B1 formée par l'objectif d'un microscope ?", "options": ["Réelle, renversée et agrandie", "Virtuelle et droite", "À l'infini"], "rep": "Réelle, renversée et agrandie"},
            {"id": "qlg1_4", "q": "Comment agit ensuite l'oculaire du microscope sur l'image intermédiaire A1B1 ?", "options": ["Il agit comme une loupe et forme une image finale virtuelle, agrandie et renversée par rapport à l'objet", "Il projette l'image sur le plafond", "Il rétrécit l'image de moitié"], "rep": "Il agit comme une loupe et forme une image finale virtuelle, agrandie et renversée par rapport à l'objet"},
            {"id": "qlg1_5", "q": "Comment calcule-t-on le grossissement total G d'un microscope composé d'un objectif de grandissement |γ1| et d'un oculaire de grossissement G2 ?", "options": ["G = |γ1| × G2 (produit des deux)", "G = |γ1| + G2", "G = |γ1| / G2"], "rep": "G = |γ1| × G2 (produit des deux)"},
            {"id": "qlg1_6", "q": "Si l'objectif d'un microscope de lecture a un grandissement de 10× et l'oculaire un grossissement de 5×, quel est le grossissement total ?", "options": ["50×", "15×", "2×"], "rep": "50×"},
            {"id": "qlg1_7", "q": "Dans les anciens théodolites optico-mécaniques, à quoi servait le microscope de lecture intégré à côté de l'oculaire principal ?", "options": ["À lire les graduations micrométriques des cercles horizontal et vertical gravés sur verre", "À observer les nuages", "À mesurer la température"], "rep": "À lire les graduations micrométriques des cercles horizontal et vertical gravés sur verre"},
            {"id": "qlg1_8", "q": "Pourquoi l'objectif d'un microscope possède-t-il une distance focale f'1 très courte (quelques millimètres) ?", "options": ["Pour obtenir un très fort grandissement |γ1| à courte distance de l'objet", "Pour voir à 10 kilomètres", "Pour réduire le prix du verre"], "rep": "Pour obtenir un très fort grandissement |γ1| à courte distance de l'objet"},
            {"id": "qlg1_9", "q": "De quel sens est l'image finale vue dans un microscope simple sans prisme redresseur par rapport à l'objet réel ?", "options": ["Renversée (inversée)", "Droite (dans le même sens)", "Toujours floue"], "rep": "Renversée (inversée)"},
            {"id": "qlg1_10", "q": "Quelle distance sépare le foyer image F'1 de l'objectif et le foyer objet F2 de l'oculaire dans un microscope standard ?", "options": ["L'intervalle optique Δ (environ 160 mm)", "0 mm (ils sont toujours confondus)", "10 mètres"], "rep": "L'intervalle optique Δ (environ 160 mm)"},
        ],
        "trous": [
            ("1. Un microscope associe deux lentilles convergentes : l'......... et l'oculaire.", ["Choisir...", "objectif", "prisme"], "objectif", "lgeo_t1"),
            ("2. L'objectif possède une distance focale f'1 très .........", ["Choisir...", "courte", "longue"], "courte", "lgeo_t2"),
            ("3. L'image intermédiaire A1B1 formée par l'objectif est ......... et agrandie.", ["Choisir...", "réelle", "virtuelle"], "réelle", "lgeo_t3"),
            ("4. L'......... observe cette image intermédiaire comme une loupe.", ["Choisir...", "oculaire", "écran"], "oculaire", "lgeo_t4"),
            ("5. L'image finale observée à l'œil est ......... et très agrandie.", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "lgeo_t5"),
            ("6. Le grossissement total est le ......... du grandissement objectif et du grossissement oculaire.", ["Choisir...", "produit", "quotient"], "produit", "lgeo_t6"),
            ("7. Sans prisme redresseur, l'image finale est ......... par rapport à l'objet.", ["Choisir...", "renversée", "droite"], "renversée", "lgeo_t7"),
            ("8. En topographie, le microscope permettait de lire les graduations du .........", ["Choisir...", "cercle", "trépied"], "cercle", "lgeo_t8"),
            ("9. La distance entre F'1 et F2 s'appelle l'......... optique Δ.", ["Choisir...", "intervalle", "angle"], "intervalle", "lgeo_t9"),
            ("10. Chaque lentille obéit à la relation de conjugaison de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "lgeo_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qlg2_1", "q": "Quel appareil optique composé de lentilles convergentes permet de dresser la carte topographique d'un territoire depuis un avion ?", "options": ["Une chambre métrique aérienne (appareil photo photogrammétrique calibré)", "Un microscope électronique", "Un phare maritime"], "rep": "Une chambre métrique aérienne (appareil photo photogrammétrique calibré)"},
            {"id": "qlg2_2", "q": "Lors d'un levé aérien à altitude H = 1 500 m avec une focale f' = 150 mm (0,15 m), quelle est l'échelle des clichés ?", "options": ["1 / 10 000 (soit |γ| = f' / H = 0,15 / 1500)", "1 / 150", "1 / 1 500"], "rep": "1 / 10 000 (soit |γ| = f' / H = 0,15 / 1500)"},
            {"id": "qlg2_3", "q": "Comment appelle-t-on l'observation en relief (3D) d'un couple de photos aériennes prises avec recouvrement à l'aide de deux lentilles convergentes ?", "options": ["La stéréoscopie (stéréorestitution)", "La calorimétrie", "La spectroscopie"], "rep": "La stéréoscopie (stéréorestitution)"},
            {"id": "qlg2_4", "q": "Pourquoi un stéréoscope de bureau utilise-t-il deux lentilles convergentes placées au-dessus des deux photos aériennes ?", "options": ["Pour permettre à chaque œil d'observer une photo différente sans fatigue et reconstituer le relief", "Pour colorier les courbes de niveau", "Pour inverser le nord et le sud"], "rep": "Pour permettre à chaque œil d'observer une photo différente sans fatigue et reconstituer le relief"},
            {"id": "qlg2_5", "q": "Quel défaut géométrique d'un objectif grand-angle doit être mathématiquement corrigé par le logiciel du géomètre ?", "options": ["La distorsion radiale (effet coussinet ou barillet) sur les bords de l'image", "La couleur bleue du ciel", "La vitesse de l'avion"], "rep": "La distorsion radiale (effet coussinet ou barillet) sur les bords de l'image"},
            {"id": "qlg2_6", "q": "Si un terrain de 200 m de côté est photographié à l'échelle 1 / 10 000, quelle est la taille de son image sur le capteur ?", "options": ["20 mm (2,0 cm)", "200 mm", "2 mètres"], "rep": "20 mm (2,0 cm)"},
            {"id": "qlg2_7", "q": "Où se forme l'image du sol terrestre dans l'objectif de la chambre aérienne (H très grand devant f') ?", "options": ["Dans le plan focal image (x' = f')", "À 2 × f'", "Sur le hublot de l'avion"], "rep": "Dans le plan focal image (x' = f')"},
            {"id": "qlg2_8", "q": "Quel document cartographique précis le géomètre produit-il à partir de l'assemblage redressé des clichés aériens ?", "options": ["Une orthophotoplan géoréférencée", "Une carte routière dessinée à main levée", "Un relevé bancaire"], "rep": "Une orthophotoplan géoréférencée"},
            {"id": "qlg2_9", "q": "Quel est l'avantage d'utiliser un objectif à focale fixe plutôt qu'un zoom variable en cartographie aérienne ?", "options": ["La distance focale f' reste parfaitement stable et connue au micromètre près", "Il est plus léger de 10 kg", "Il fonctionne de nuit sans lumière"], "rep": "La distance focale f' reste parfaitement stable et connue au micromètre près"},
            {"id": "qlg2_10", "q": "Quelle formule donne la taille réelle AB d'un bâtiment à partir de sa mesure A'B' sur l'orthophoto d'échelle 1/E ?", "options": ["AB = A'B' × E", "AB = A'B' / E", "AB = A'B' + E"], "rep": "AB = A'B' × E"},
        ],
        "trous": [
            ("1. L'observation en relief de deux photos aériennes s'appelle la .........", ["Choisir...", "stéréoscopie", "thermographie"], "stéréoscopie", "lgeo_t1"),
            ("2. L'objectif aérien est un système optique ......... de haute précision.", ["Choisir...", "convergent", "divergent"], "convergent", "lgeo_t2"),
            ("3. L'échelle du cliché est donnée par le rapport |γ| = f' / .........", ["Choisir...", "H", "2"], "H", "lgeo_t3"),
            ("4. Le sol étant très éloigné, le capteur est placé au foyer ......... F'.", ["Choisir...", "image", "objet"], "image", "lgeo_t4"),
            ("5. Le logiciel corrige la ......... géométrique sur les bords de l'objectif.", ["Choisir...", "distorsion", "température"], "distorsion", "lgeo_t5"),
            ("6. L'image redressée et mise à l'échelle s'appelle un .........", ["Choisir...", "orthophotoplan", "hologramme"], "orthophotoplan", "lgeo_t6"),
            ("7. Un ......... à deux lentilles permet de voir le relief sur table.", ["Choisir...", "stéréoscope", "périscope"], "stéréoscope", "lgeo_t7"),
            ("8. On utilise une focale ......... pour garantir la stabilité géométrique.", ["Choisir...", "fixe", "aléatoire"], "fixe", "lgeo_t8"),
            ("9. Si l'altitude H augmente, l'échelle du cliché devient plus .........", ["Choisir...", "petite", "grande"], "petite", "lgeo_t9"),
            ("10. Le calcul des distances terrain repose sur la loi de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "lgeo_t10"),
        ]
    }
}


def mettre_a_jour_len_geo_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles convergentes adapté au Géomètre Topographe."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        dist_visee_m = st.session_state.get("slider_lgeo_s0", 150.0)
        f_obj_mm = 200.0
        x_img_mm = (f_obj_mm * (-dist_visee_m * 1000.0)) / (-dist_visee_m * 1000.0 + f_obj_mm)

        x0, y0 = 220.0, 125.0
        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x0, x0)), list((45, 205)), color="#38bdf8", lw=4)
        ax.text(x0, 34, "Objectif Station Totale (f' = 200 mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        x_ret = 440.0
        ax.plot(list((x_ret, x_ret)), list((70, 180)), color="#22c55e", lw=3)
        ax.text(x_ret, 60, "Plan du Réticule", color="#86efac", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((495, 495)), list((85, 165)), color="#eab308", lw=3)
        ax.text(495, 76, "Oculaire (30×)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((40, x0)), list((85, 85)), color="#ef4444", lw=1.8)
        ax.plot(list((40, x0)), list((165, 165)), color="#ef4444", lw=1.8)
        ax.plot(list((x0, x_ret)), list((85, y0)), color="#ef4444", lw=1.8)
        ax.plot(list((x0, x_ret)), list((165, y0)), color="#ef4444", lw=1.8)

        ax.text(25, 18, "STATION TOTALE : FORMATION DE L'IMAGE DU PRISME SUR LE RÉTICULE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Distance prisme : D = {dist_visee_m:.0f} m | Position image objectif : x' = {x_img_mm:.3f} mm | Grossissement : 30×", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.lgeo_mesure_courante = (f"D = {dist_visee_m:.0f} m", f"x' = {x_img_mm:.3f} mm", "Grossissement 30×", "VISÉE NETTE")

    elif sujet_idx == 1:
        g1_obj = st.session_state.get("slider_lgeo_g1_s1", 10)
        g2_oc = st.session_state.get("slider_lgeo_g2_s1", 5)
        g_total = g1_obj * g2_oc

        x1, x2, y0 = 190.0, 410.0, 130.0
        ax.plot(list((30, 570)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x1, x1)), list((65, 195)), color="#38bdf8", lw=3.5)
        ax.text(x1, 54, f"Objectif (|γ1| = {g1_obj}×)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        ax.plot(list((x2, x2)), list((50, 210)), color="#eab308", lw=3.5)
        ax.text(x2, 40, f"Oculaire (G2 = {g2_oc}×)", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        ax.annotate("", xy=(110, y0 - 15), xytext=(110, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
        ax.text(110, y0 + 16, "Graduation", color="#fca5a5", fontsize=7.5, fontweight="bold", ha="center")

        ax.annotate("", xy=(330, y0 + 38), xytext=(330, y0), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2.5))
        ax.text(330, y0 - 10, "Image A1B1", color="#86efac", fontsize=7.5, fontweight="bold", ha="center")

        ax.text(25, 18, "MÉTROLOGIE OPTIQUE : GROSSISSEMENT D'UN MICROSCOPE DE LECTURE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Grossissement total : G = |γ1| × G2 = {g1_obj} × {g2_oc} = {g_total}× (Lecture micrométrique)", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.lgeo_mesure_courante = (f"|γ1| = {g1_obj}×", f"G2 = {g2_oc}×", f"Total = {g_total}×", "LECTURE OK")

    else:
        alt_avion_m = st.session_state.get("slider_lgeo_s2", 1500.0)
        f_chambre_mm = st.session_state.get("slider_lgeo_f_s2", 150.0)
        echelle_e = int(round(alt_avion_m / (f_chambre_mm / 1000.0)))
        parcelle_m = 200.0
        img_capteur_mm = (parcelle_m / echelle_e) * 1000.0

        ax.add_patch(patches.Rectangle((40, 195), 520, 35, facecolor="#365314", edgecolor="#4d7c0f"))
        ax.add_patch(patches.Rectangle((220, 185), 160, 10, facecolor="#eab308", edgecolor="white"))
        ax.text(300, 214, "Parcelle cadastrale au sol (AB = 200 m)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        y_av = 180.0 - (alt_avion_m / 3000.0) * 115.0
        ax.add_patch(patches.Rectangle((265, y_av - 12), 70, 12, facecolor="#38bdf8", edgecolor="white"))
        ax.text(300, y_av - 18, f"Avion IGN (H = {alt_avion_m:.0f} m | f' = {f_chambre_mm:.0f} mm)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        ax.plot(list((220, 300)), list((185, y_av)), color="#22c55e", lw=1.4, ls="--")
        ax.plot(list((380, 300)), list((185, y_av)), color="#22c55e", lw=1.4, ls="--")

        ax.text(25, 18, "CARTOGRAPHIE AÉRIENNE : ÉCHELLE DE CLICHÉ ET ORTHOPHOTOPLAN", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Échelle du cliché : 1 / {echelle_e}  |  Taille de la parcelle sur le capteur : A'B' = {img_capteur_mm:.2f} mm", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.lgeo_mesure_courante = (f"H = {alt_avion_m:.0f} m", f"f' = {f_chambre_mm:.0f} mm", f"Échelle 1/{echelle_e}", f"A'B' = {img_capteur_mm:.2f} mm")

    return fig


def afficher_atelier_len_geo(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort une mission Géomètre ci-dessus.")
        return
    banque = BANQUES_LEN_GEO[sujet_idx]
    cle_ordre = f"ordre_quiz_lgeo_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Géomètre Topographe (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"lgeo_at7_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Géomètre Topographe (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")



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
    st.header("Atelier 1 : L'histoire des lentilles convergentes")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Objectif de l'atelier :</p>
        <p style="margin-bottom: 0;">Découvrir l'invention des lentilles convergentes, depuis les cristaux de l'Antiquité jusqu'aux lunettes astronomiques et aux lentilles à échelons de Fresnel.</p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    with col_l1:
        try:
            st.image("nimrud.jpg", caption="Lentille de Nimrud (750 av. J.-C.)", use_container_width=True)
        except Exception:
            st.warning("L'image 'nimrud.jpg' est introuvable.")
        st.info("**L'Antiquité : Les verres ardents**\n* Taillée dans du cristal de roche poli.\n* Utilisée pour concentrer les rayons solaires en un foyer et allumer un feu ou grossir de fins détails.")

    with col_l2:
        try:
            st.image("alhazen.jpg", caption="Ibn al-Haytham / Alhazen (965 - 1040)", use_container_width=True)
        except Exception:
            st.warning("L'image 'alhazen.jpg' est introuvable.")
        st.info("**Alhazen (*Traité d'optique*, 1021)**\n* Étudie géométriquement le grossissement produit par des segments de sphère en verre.\n* Inspire l'invention des premières lunettes de vue en Italie vers 1285.")

    with col_l3:
        try:
            st.image("kepler.jpg", caption="Johannes Kepler (1571 - 1630)", use_container_width=True)
        except Exception:
            st.warning("L'image 'kepler.jpg' est introuvable.")
        st.info("**Johannes Kepler (*Dioptrice*, 1611)**\n* Perfectionne la lunette astronomique à deux lentilles convergentes.\n* Formalise la marche des rayons lumineux et la notion de foyer image.")

    with col_l4:
        try:
            st.image("fresnel.jpg", caption="Augustin Fresnel (1788 - 1827)", use_container_width=True)
        except Exception:
            st.warning("L'image 'fresnel.jpg' est introuvable.")
        st.info("**Augustin Fresnel (1822)**\n* Invente la lentille convergente à échelons pour réduire le poids et l'épaisseur du verre.\n* Équipe tous les phares maritimes et aujourd'hui les projecteurs et capteurs.")

    st.markdown("---")
    if "hl_verrouille_tab1" not in st.session_state:
        st.session_state.hl_verrouille_tab1 = False
    verrou_hl = st.session_state.hl_verrouille_tab1

    afficher_atelier_hist_lentilles(verrouille=verrou_hl)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_hl = st.checkbox("Je certifie avoir complété les questions de l'Atelier 1 (Histoire des lentilles).", key="check_certif_hl", disabled=verrou_hl)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_hl1", use_container_width=True, disabled=verrou_hl):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_hl:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            sc_q1 = sum(1.0 for q in st.session_state.get("ordre_quiz_hl_aleatoire", []) if st.session_state.get(f"hl_at1_g_{q['id']}") == q["rep"])
            rep_t1 = {"hl_t1": "lens", "hl_t2": "Nimrud", "hl_t3": "Alhazen", "hl_t4": "lunettes", "hl_t5": "Galilée", "hl_t6": "Kepler", "hl_t7": "Fresnel", "hl_t8": "foyer", "hl_t9": "presbytie", "hl_t10": "Descartes"}
            sc_t1 = sum(1.0 for k, v in rep_t1.items() if st.session_state.get(k) == v)
            st.session_state.score_hl1_p1 = sc_q1
            st.session_state.score_hl1_p2 = sc_t1
            st.session_state.score_final_hl1 = sc_q1 + sc_t1
            st.session_state.hl_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("hl_verrouille_tab1", False):
        scr1 = st.session_state.get("score_hl1_p1", 0.0)
        scr2 = st.session_state.get("score_hl1_p2", 0.0)
        tot_s = st.session_state.get("score_final_hl1", 0.0)
        ts_hl = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 1 SCELLÉ | Note : {tot_s:.1f} / 20")

        html_hl = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 1 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;text-align:center;border:2px solid white}}.sub-title{{font-weight:bold;color:#475569;margin-top:25px;text-transform:uppercase;font-size:13px;border-bottom:2px solid #cbd5e1;padding-bottom:5px;margin-bottom:10px}}table{{width:100%;border-collapse:collapse;margin-top:10px;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:12px;font-size:14px;text-align:left}}td{{padding:12px;font-size:13px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 1 : Histoire des Lentilles Convergentes</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve}</p><p style="font-size:12px;">Scellé le : {ts_hl}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <div class="sub-title">Récapitulatif des Notes</div><p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div><table><thead><tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""

        for num, q_item in enumerate(st.session_state.get("ordre_quiz_hl_aleatoire", []), 1):
            saisie = st.session_state.get(f"hl_at1_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_hl += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_cls}'>{v_lbl}</td></tr>"

        html_hl += """</tbody></table><div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (10 TROUS)</div><table><thead><tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""

        verif_t1 = [
            ("1. Le mot lentille vient du latin ......... en raison de sa forme bombée.", "lens", "hl_t1"),
            ("2. La lentille de ......... (750 av. J.-C.) est taillée dans du cristal de roche.", "Nimrud", "hl_t2"),
            ("3. Au XIe siècle, ......... étudie le grossissement des surfaces convexes.", "Alhazen", "hl_t3"),
            ("4. Les premières ......... de vue convergentes apparaissent en Italie vers 1285.", "lunettes", "hl_t4"),
            ("5. En 1609, ......... utilise une lunette pour observer les astres.", "Galilée", "hl_t5"),
            ("6. En 1611, Johannes ......... publie le traité Dioptrice.", "Kepler", "hl_t6"),
            ("7. En 1822, Augustin ......... invente la lentille à échelons pour les phares.", "Fresnel", "hl_t7"),
            ("8. Une lentille convergente concentre les rayons solaires en son .........", "foyer", "hl_t8"),
            ("9. Au Moyen Âge, les verres convergents corrigeaient la .........", "presbytie", "hl_t9"),
            ("10. La formule de conjugaison porte le nom de René .........", "Descartes", "hl_t10"),
        ]
        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(verif_t1, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_hl += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"

        html_hl += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 1 (.html)", data=html_hl, file_name=preparer_nom_fichier("Rapport_Atelier_1_Histoire_Lentilles").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab2:
    st.header("Atelier 2 : Définition et règles de tracé des rayons")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les 3 rayons particuliers d'une lentille mince convergente :</p>
        <ul style="margin-bottom: 0; line-height: 1.7;">
            <li><strong>Rayon 1 (Jaune - Parallèle à l'axe) :</strong> Tout rayon incident parallèle à l'axe optique ressort en passant par le <strong>foyer image F'</strong>.</li>
            <li><strong>Rayon 2 (Bleu - Centre optique O) :</strong> Tout rayon incident passant par le centre optique <strong>O</strong> n'est <strong>pas dévié</strong>.</li>
            <li><strong>Rayon 3 (Rose - Foyer objet F) :</strong> Tout rayon incident passant par le foyer objet <strong>F</strong> ressort <strong>parallèlement à l'axe optique</strong>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns([0.55, 0.45])
    with col_r1:
        st.radio(
            "Sélectionnez le rayon à observer :",
            ["Tous les 3 rayons particuliers", "Rayon 1 : Parallèle à l'axe → F'", "Rayon 2 : Passe par O → Non dévié", "Rayon 3 : Passe par F → Parallèle"],
            key="radio_regles_rayon"
        )
    with col_r2:
        st.slider("Distance focale f' de démonstration (px) :", min_value=60.0, max_value=140.0, value=100.0, step=5.0, key="slider_regles_f")

    fig_regles = dessiner_regles_trace_lentille_matplotlib()
    st.pyplot(fig_regles, use_container_width=True)

    st.markdown("---")
    if "rl_verrouille_tab2" not in st.session_state:
        st.session_state.rl_verrouille_tab2 = False
    verrou_rl = st.session_state.rl_verrouille_tab2

    afficher_atelier_regles_lentilles(verrouille=verrou_rl)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_rl = st.checkbox("Je certifie avoir complété les questions de l'Atelier 2 (Règles de tracé).", key="check_certif_rl", disabled=verrou_rl)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_rl2", use_container_width=True, disabled=verrou_rl):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_rl:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            sc_q2 = sum(1.0 for q in st.session_state.get("ordre_quiz_rl_aleatoire", []) if st.session_state.get(f"rl_at2_g_{q['id']}") == q["rep"])
            rep_t2 = {"rl_t1": "minces", "rl_t2": "optique", "rl_t3": "optique", "rl_t4": "dévié", "rl_t5": "image", "rl_t6": "parallèle", "rl_t7": "symétriques", "rl_t8": "focale", "rl_t9": "vergence", "rl_t10": "dioptrie"}
            sc_t2 = sum(1.0 for k, v in rep_t2.items() if st.session_state.get(k) == v)
            st.session_state.score_rl2_p1 = sc_q2
            st.session_state.score_rl2_p2 = sc_t2
            st.session_state.score_final_rl2 = sc_q2 + sc_t2
            st.session_state.rl_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("rl_verrouille_tab2", False):
        scr1 = st.session_state.get("score_rl2_p1", 0.0)
        scr2 = st.session_state.get("score_rl2_p2", 0.0)
        tot_s = st.session_state.get("score_final_rl2", 0.0)
        ts_rl = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 2 SCELLÉ | Note : {tot_s:.1f} / 20")

        html_rl = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 2 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;text-align:center;border:2px solid white}}.sub-title{{font-weight:bold;color:#475569;margin-top:25px;text-transform:uppercase;font-size:13px;border-bottom:2px solid #cbd5e1;padding-bottom:5px;margin-bottom:10px}}table{{width:100%;border-collapse:collapse;margin-top:10px;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:12px;font-size:14px;text-align:left}}td{{padding:12px;font-size:13px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 2 : Définition et Règles de Tracé des Lentilles Convergentes</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve}</p><p style="font-size:12px;">Scellé le : {ts_rl}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <div class="sub-title">Récapitulatif des Notes</div><p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div><table><thead><tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""

        for num, q_item in enumerate(st.session_state.get("ordre_quiz_rl_aleatoire", []), 1):
            saisie = st.session_state.get(f"rl_at2_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_rl += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_cls}'>{v_lbl}</td></tr>"

        html_rl += """</tbody></table><div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (10 TROUS)</div><table><thead><tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""

        verif_t2 = [
            ("1. Une lentille convergente a des bords plus ......... que son centre.", "minces", "rl_t1"),
            ("2. L'axe de symétrie perpendiculaire à la lentille est l'axe .........", "optique", "rl_t2"),
            ("3. Le point central de la lentille noté O est le centre .........", "optique", "rl_t3"),
            ("4. Tout rayon passant par le centre O n'est pas .........", "dévié", "rl_t4"),
            ("5. Tout rayon parallèle à l'axe émerge en passant par le foyer ......... F'.", "image", "rl_t5"),
            ("6. Tout rayon passant par le foyer objet F ressort ......... à l'axe.", "parallèle", "rl_t6"),
            ("7. Les foyers F et F' sont ......... par rapport au centre O.", "symétriques", "rl_t7"),
            ("8. La distance OF' s'appelle la distance ......... f'.", "focale", "rl_t8"),
            ("9. L'inverse de la distance focale en mètres est la ......... C.", "vergence", "rl_t9"),
            ("10. L'unité de la vergence d'une lentille est la ......... (δ).", "dioptrie", "rl_t10"),
        ]
        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(verif_t2, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_rl += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"

        html_rl += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 2 (.html)", data=html_rl, file_name=preparer_nom_fichier("Rapport_Atelier_2_Regles_Trace").replace(".txt", ".html"), mime="text/html", use_container_width=True)



with tab3:
    st.header("Lentilles Minces Convergentes & Relation de Conjugaison")
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel des Formules de la Dioptrique (Lentilles Convergentes) :</p>
        <ul style="margin-bottom: 0; line-height: 1.8;">
            <li><strong>Relation de conjugaison de Descartes :</strong> <b>1 / <i>x'</i> &minus; 1 / <i>x</i> = 1 / <i>f'</i></b> &nbsp;(avec <i>x</i> = <span style="text-decoration: overline;">OA</span> et <i>x'</i> = <span style="text-decoration: overline;">OA'</span>)</li>
            <li><strong>Vergence d'une lentille :</strong> <b><i>C</i> = 1 / <i>f'</i></b> &nbsp;(exprimée en Dioptries <b>&delta;</b> avec <i>f'</i> en mètres)</li>
            <li><strong>Grandissement transversal :</strong> <b>&gamma; = <span style="text-decoration: overline;">A'B'</span> / <span style="text-decoration: overline;">AB</span> = <i>x'</i> / <i>x</i></b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt5_verrouille" not in st.session_state: st.session_state.opt5_verrouille = False
    if "mesures_inv_x" not in st.session_state: st.session_state.mesures_inv_x = []
    if "mesures_inv_xprime" not in st.session_state: st.session_state.mesures_inv_xprime = []


    # =========================================================================
    # ARCHITECTURE DOUBLE COLONNE : COMMANDES GRAPH_LAB / VISUALISATIONS
    # =========================================================================
    col_g_widgets, col_d_rendu = st.columns([1.2, 2.2])

    # --- PANNEAU DE GAUCHE : TOUS VOS CURSEURS ET CASES À COCHER TKINTER ---
    with col_g_widgets:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>CONTRÔLES DE LA LENTILLE</p>", unsafe_allow_html=True)
            
            # Curseurs physiques d'origines calqués sur vos DoubleVar
            height_ab = st.slider("Hauteur de l'objet AB (cm) :", min_value=1.0, max_value=100.0, value=40.0, step=1.0, key="slide_len_ab", disabled=st.session_state.opt5_verrouille)
            pos_x = st.slider("Position de l'objet x (cm) :", min_value=-600.0, max_value=-1.0, value=-80.0, step=1.0, key="slide_len_x", disabled=st.session_state.opt5_verrouille)
            f_prime = st.slider("Distance focale f' (cm) :", min_value=20.0, max_value=500.0, value=50.0, step=1.0, key="slide_len_f", disabled=st.session_state.opt5_verrouille)

            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            st.markdown("##### Affichage des rayons :")
            
            # Cases à cocher réactives d'origines (BooleanVar)
            chk_bleu = st.checkbox("Rayon central (O)", value=True, key="chk_rayon_bleu", disabled=st.session_state.opt5_verrouille)
            chk_jaune = st.checkbox("Rayon parallele (F')", value=True, key="chk_rayon_jaune", disabled=st.session_state.opt5_verrouille)
            chk_rose = st.checkbox("Rayon focal (F)", value=True, key="chk_rayon_rose", disabled=st.session_state.opt5_verrouille)
            chk_image = st.checkbox("Afficher l'image A'B'", value=True, key="chk_afficher_image_verte", disabled=st.session_state.opt5_verrouille)

            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("CAPTURER LA MESURE", key="btn_capt_mesure_len", use_container_width=True, disabled=st.session_state.opt5_verrouille):
                    ajouter_mesure_lentille_convergente_streamlit()
                    st.rerun()
            with col_b2:
                if st.button("EFFACER", key="btn_clear_len", use_container_width=True, disabled=st.session_state.opt5_verrouille):
                    reinitialiser_mesures_lentille_streamlit()
                    st.rerun()

        # BLOC RENDU DU PANNEAU RÉSULTAT TECHNIQUE (CANVAS_RESULTAT BAS GAUCHE)
        with st.container(border=True):
            # Moteur de calcul physique en direct pour l'affichage de la console
            try:
                inv_x_c = 1.0 / pos_x
                inv_f_c = 1.0 / f_prime
                inv_xp_c = inv_f_c + inv_x_c
                pos_xprime = 1.0 / inv_xp_c if inv_xp_c != 0 else 9999.0
                vergence = 100.0 / f_prime
                grandissement = pos_xprime / pos_x
                taille_image = height_ab * grandissement
            except:
                pos_xprime = vergence = grandissement = taille_image = 0.0

            st.markdown("**Console de calculs de la lentille :**")
            txt_console = (
                f"• Objet x = {pos_x:.1f} cm\n"
                f"• Taille AB = {height_ab:.1f} cm\n"
                f"• Focale f' = {f_prime:.1f} cm\n"
                f"• Image x' = {pos_xprime:.1f} cm\n"
                f"• Taille A'B' = {taille_image:.1f} cm\n"
                f"• Vergence C = {vergence:.2f} δ\n"
                f"• Grandissement γ = {grandissement:.2f}"
            )
            st.text(txt_console)

    # --- PANNEAU DE DROITE : LES DEUX FIGURES ET LE TABLEAU CHIFCRÉ PANDAS ---
    with col_d_rendu:
        # 1. LE GRAND DESSIN DU BANC D'OPTIQUE (TOUTE LA LARGEUR EN PREMIER)
        st.subheader("Banc d'optique virtuel")
        fig_banc_optique = mettre_a_jour_lentille_matplotlib()
        st.pyplot(fig_banc_optique, use_container_width=True)
        
        # 2. LE TABLEAU DES VALEURS NUMÉRIQUES (JUSTE EN DESSOUS)
        st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Tableau des points enregistres (Espace de Descartes)")
        
        import pandas as pd
        if st.session_state.get("mesures_inv_x"):
            df_lentille = pd.DataFrame({
                "Essai": [f"Essai {idx}" for idx in range(1, len(st.session_state.mesures_inv_x) + 1)],
                "1/x (cm^-1)": st.session_state.mesures_inv_x,
                "1/x' (cm^-1)": st.session_state.mesures_inv_xprime,
                "1/x' - 1/x (cm^-1)": [round(xp - x, 5) for x, xp in zip(st.session_state.mesures_inv_x, st.session_state.mesures_inv_xprime)]
            })
            st.dataframe(df_lentille, use_container_width=True, hide_index=True)
        else:
            st.caption("Tableau vide. Deplacez les curseurs de la lentille et cliquez sur Capturer la mesure.")

        # 3. LE GRAPHISQUE CARTÉSIEN DE LA DROITE DE DESCARTES (TOUT EN BAS)
        st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        st.subheader("Relation de Descartes")
        fig_courbe_descartes = mettre_a_jour_graphique_lentille_matplotlib()
        st.pyplot(fig_courbe_descartes, use_container_width=True)
        
    st.write("---")
    dict_q5, dict_t5 = afficher_questions_optique5(verrouille=st.session_state.get("opt5_verrouille", False))

    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION AUTOMATIQUE SUR 20 POINTS
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - ")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt5 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier.", 
        key="check_certif_opt5_officiel_20pts", 
        disabled=st.session_state.get("opt5_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER ", key="btn_export_opt5_official_20pts", use_container_width=True, disabled=st.session_state.get("opt5_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt5: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Moteur de correction automatique du Quiz (10 questions = 10 pts)
            attendus_qo5_v = {
                "q1": "1/x' - 1/x = 1/f'", "q2": "Continue en ligne droite sans subir de deviation", 
                "q3": "Le foyer image F'", "q4": "La dioptrie (delta)", "q5": "Reelle et renversee", 
                "q6": "Renversee par rapport a l'objet", "q7": "A l'infini", 
                "q8": "Plus minces que son centre", "q9": "+2.0", "q10": "1 (droite inclinee a 45 degres)"
            }
            score_quiz_opt5 = sum([1.0 for qk, qv in attendus_qo5_v.items() if st.session_state.get(f"col_g_quiz_opt5_{qk}") == qv])

            # Moteur de correction automatique du Texte a trous (10 trous = 10 pts)
            attendus_to5_v = {
                "t1": "Convergente", "t2": "Image F'", "t3": "Dioptries", "t4": "Grandissement", "t5": "Deviation",
                "t6": "Optique", "t7": "Focale", "t8": "Reelle", "t9": "Renversee", "t10": "Infini"
            }
            score_trous_opt5 = sum([1.0 for tk, tv in attendus_to5_v.items() if st.session_state.get(f"opt5_{tk}") == tv])

            st.session_state.score_opt5_p1 = round(score_quiz_opt5, 1)
            st.session_state.score_opt5_p2 = round(score_trous_opt5, 1)
            st.session_state.score_final_opt5 = round(score_quiz_opt5 + score_trous_opt5, 1)
            st.session_state.opt5_verrouille = True
            st.rerun()

    # LE BLOC D'EXPORT PERMANENT LIÉ AU VERROU
    if st.session_state.get("opt5_verrouille", False):
        scr1 = st.session_state.get("score_opt5_p1", 0.0)
        scr2 = st.session_state.get("score_opt5_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt5", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt5 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE  SCELLE | Note de session : {tot_s} / 20")

        attendus_qo5_v = {
            "q1": "1/x' - 1/x = 1/f'", "q2": "Continue en ligne droite sans subir de deviation", 
            "q3": "Le foyer image F'", "q4": "La dioptrie (delta)", "q5": "Reelle et renversee", 
            "q6": "Renversee par rapport a l'objet", "q7": "A l'infini", 
            "q8": "Plus minces que son centre", "q9": "+2.0", "q10": "1 (droite inclinee a 45 degres)"
        }
        enonces_qo5_v = {
            "q1": "D'apres la relation de conjugaison de Descartes, la formule exacte est :",
            "q2": "Un rayon lumineux passant par le centre optique O d'une lentille mince :",
            "q3": "Un rayon incident parallele a l'axe optique ressort de la lentille en passant par :",
            "q4": "La vergence C d'une lentille est l'inverse de sa distance focale f'. Son unite est :",
            "q5": "Si l'objet AB est situe a une distance superieure a la distance focale (x > f'), l'image obtenue est :",
            "q6": "Si le grandissement gamma est negatif (gamma < 0), cela signifie geometriquement que l'image est :",
            "q7": "Lorsque l'objet AB est deplace et positionne pile sur le foyer objet F, l'image se forme :",
            "q8": "Une lentille mince est qualifiee de convergente si ses bords sont :",
            "q9": "Si la taille de l'image est deux fois plus grande que l'objet et de meme sens, gamma vaut :",
            "q10": "Lorsqu'on trace le graphique de 1/x' en fonction de 1/x, la courbe obtenue est une droite de pente :"
        }

        attendus_to5_v = {
            "t1": "Convergente", "t2": "Image F'", "t3": "Dioptries", "t4": "Grandissement", "t5": "Deviation",
            "t6": "Optique", "t7": "Focale", "t8": "Reelle", "t9": "Renversee", "t10": "Infini"
        }
        enonces_to5_v = {
            "t1": "1. Une lentille mince possede des bords plus minces que son centre. Elle est qualifiee de .........",
            "t2": "2. Tout rayon incident parallele a l'axe optique ressort en convergeant vers le foyer .........",
            "t3": "3. La relation de conjugaison permet de calculer la position x' de l'image. Sa vergence s'exprime en .........",
            "t4": "4. Enfin, le rapport des dimensions entre l'image et l'objet definit le .........",
            "t5": "5. Tout rayon passant par le centre optique O traverse la lentille sans aucune .........",
            "t6": "6. Tout rayon passant par le foyer objet F ressort de la lentille parallelement a l'axe .........",
            "t7": "7. La distance entre le centre optique O et le foyer image F' s'appelle la distance .........",
            "t8": "8. Lorsque l'image se projette sur un ecran derriere la lentille, elle est qualifiee de .........",
            "t9": "9. Si le grandissement gamma est negatif, l'image obtenue sur l'ecran est .........",
            "t10": "10. Lorsque l'objet est place exactement sur le foyer objet F, l'image se forme a l'........."
        }

        # Generation du document HTML propre pour le professeur Gallet
        html_export_opt5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique  - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Atelier : Lentilles Minces Convergentes | Scelle le : {timestamp_opt5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 5</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE CONJUGAISON (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Question posée</th>
                        <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_q, (q_id, attendu) in enumerate(attendus_qo5_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt5_{q_id}", "Choisir...")
            enonce_q = enonces_qo5_v.get(q_id, f"Question {idx_q}")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt5 += f"<tr><td>{idx_q}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt5 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS (TEXTE A TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 55%; text-align: left;">Phrase explicative à trous</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for t_key, attendu_t in attendus_to5_v.items():
            saisie_t = st.session_state.get(f"opt5_{t_key}", "Choisir...")
            phrase_t = enonces_to5_v.get(t_key, t_key)
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt5 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align: center;'>{v_lbl_t}</td></tr>"

        html_export_opt5 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">
                Laboratoire d'Optique Physique Appliquee &copy; 2026
            </div>
        </body>
        </html>
        """

        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt5,
            file_name=f"Bilan_Optique_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("Atelier 4 : Applications dans le domaine de la Maintenance Industrielle")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles convergentes au service du diagnostic et de l'usinage :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">En maintenance industrielle, les lentilles minces convergentes permettent de grossir les défauts de surface (loupe), de former des images nettes sur des caméras de contrôle qualité ou de concentrer l'énergie d'un laser de découpe au foyer image <b><i>F'</i></b>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_len_maint = [
        {"titre": "Cas N°1 : Loupe d'inspection éclairante (Contrôle de micro-fissures)", "img": "len_maint_loupe.jpg", "leg": "Contrôle visuel de soudures à la loupe convergente", "exp": "**Principe :** En plaçant l'objet entre le centre optique **O** et le foyer objet **F** (<i>x</i> &lt; <i>f'</i>), la loupe forme une image **virtuelle, droite et agrandie** (grandissement &gamma; &gt; +1)."},
        {"titre": "Cas N°2 : Caméra de vision industrielle (Mise au point sur capteur CMOS)", "img": "len_maint_camera.jpg", "leg": "Caméra de contrôle qualité sur ligne automatisée", "exp": "**Principe :** L'objectif convergent projette une image **réelle et renversée** sur la matrice électronique. La distance capteur <i>x'</i> doit vérifier <b>1/<i>x'</i> &minus; 1/<i>x</i> = 1/<i>f'</i></b>."},
        {"titre": "Cas N°3 : Tête de découpe laser (Focalisation au foyer image F')", "img": "len_maint_laser.jpg", "leg": "Lentille ZnSe concentrant un faisceau laser sur tôle acier", "exp": "**Principe :** Un faisceau laser parallèle converge exactement au **foyer image F'** (<i>f'</i> = 127 mm), multipliant la densité de puissance pour découper le métal net."}
    ]

    if "sujet_lm_tire" not in st.session_state:
        st.session_state.sujet_lm_tire = None

    if st.button("TIRER AU SORT UN SUJET MAINTENANCE (LENTILLES)", key="btn_tirage_lm", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_lm_tire]
        st.session_state.sujet_lm_tire = random.choice(choix)
        st.session_state.mesures_lm_log = []
        st.rerun()

    if st.session_state.sujet_lm_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique de maintenance.")
    else:
        idx_lm = st.session_state.sujet_lm_tire
        data_lm = sujets_len_maint[idx_lm]
        st.success(f"Sujet attribué : **{data_lm['titre']}**")
        st.markdown(data_lm["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_lm["img"], caption=data_lm["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_lm['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_len_maint.jpg", caption="La pause BD : Attention à ne pas oublier le capuchon de l'objectif !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_len_maint.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_lm_log" not in st.session_state: st.session_state.mesures_lm_log = []
        if idx_lm == 0:
            st.slider("Distance pièce - loupe (cm) [f' = 5,0 cm] :", 1.0, 7.0, 3.5, 0.1, key="slider_lm_s0")
        elif idx_lm == 1:
            st.slider("Position du capteur CMOS x' (mm) [Cible nette = 55,6 mm] :", 48.0, 64.0, 55.0, 0.2, key="slider_lm_s1")
        else:
            st.slider("Distance lentille - tôle (mm) [Focale f' = 127 mm] :", 110.0, 145.0, 120.0, 1.0, key="slider_lm_s2")

        if st.button("ENREGISTRER CE RELEVÉ MAINTENANCE", key="btn_rel_lm", use_container_width=True):
            if "lm_mesure_courante" in st.session_state:
                st.session_state.mesures_lm_log.append(st.session_state.lm_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_len_maint_matplotlib(idx_lm), use_container_width=True)
        if st.session_state.mesures_lm_log:
            df_lm = pd.DataFrame(st.session_state.mesures_lm_log, columns=["Réglage", "Référence", "Résultat", "Diagnostic"])
            st.dataframe(df_lm, use_container_width=True, hide_index=True)

    st.write("---")
    if "lm_verrouille_tab4" not in st.session_state: st.session_state.lm_verrouille_tab4 = False
    verrou_lm = st.session_state.lm_verrouille_tab4
    sujet_actif_lm = st.session_state.get("sujet_lm_tire", None)
    afficher_atelier_len_maint(sujet_actif_lm, verrouille=verrou_lm)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_lm = st.checkbox("Je certifie avoir complété l'Atelier 4 (Maintenance - Lentilles).", key="certif_lm4", disabled=verrou_lm)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_exp_lm4", use_container_width=True, disabled=verrou_lm):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_lm is None or not case_certif_lm:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_LEN_MAINT[sujet_actif_lm]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_lm_{sujet_actif_lm}", []) if st.session_state.get(f"lm_at4_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_lm}") == rep)
            st.session_state.score_lm4_p1, st.session_state.score_lm4_p2, st.session_state.score_final_lm4 = sc_q, sc_t, sc_q + sc_t
            st.session_state.lm_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("lm_verrouille_tab4", False) and sujet_actif_lm is not None:
        scr1, scr2, tot_s = st.session_state.score_lm4_p1, st.session_state.score_lm4_p2, st.session_state.score_final_lm4
        ts_lm = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 4 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LEN_MAINT[sujet_actif_lm]
        html_lm = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 4 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 4 : Maintenance (Lentilles Convergentes) - {sujets_len_maint[sujet_actif_lm]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_lm}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_lm_{sujet_actif_lm}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"lm_at4_g_{qid_curr}", "Choisir...")
            html_lm += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td></tr>"
        html_lm += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_lm}", "Choisir...")
            html_lm += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td></tr>"
        html_lm += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 4 (.html)", data=html_lm, file_name=preparer_nom_fichier("Rapport_Atelier_4_Maintenance_Lentilles").replace(".txt", ".html"), mime="text/html", use_container_width=True)





with tab5:
    st.header("Atelier 5 : Applications dans le domaine des Travaux Publics")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles convergentes sur les chantiers de génie civil et de voirie :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Sur les chantiers TP, les lentilles convergentes équipent les <strong>lunettes de nivellement</strong>, les <strong>lentilles à échelons de Fresnel</strong> des feux de signalisation et les <strong>objectifs de drones photogrammétriques</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_len_tp = [
        {"titre": "Chantier N°1 : Niveau optique de chantier & Lecture stadimétrique", "img": "len_tp_niveau.jpg", "leg": "Niveau optique sur trépied visant une mire graduée", "exp": "**Principe :** L'objectif convergent forme une image réelle de la mire sur le réticule, grossie par l'oculaire. L'écart entre les fils stadimétriques haut et bas donne la distance : <b><i>D</i> = 100 &times; (<i>H</i> &minus; <i>B</i>)</b>."},
        {"titre": "Chantier N°2 : Feu de balisage à lentille de Fresnel convergente", "img": "len_tp_fresnel.jpg", "leg": "Lentille convergente à échelons concentriques sur feu de chantier", "exp": "**Principe :** La lentille de Fresnel réduit le poids et l'épaisseur du verre grâce à ses anneaux concentriques. Placée au **foyer objet F**, la LED émet un faisceau parallèle visible à longue distance."},
        {"titre": "Chantier N°3 : Photogrammétrie par drone TP (Calcul des cubatures)", "img": "len_tp_drone.jpg", "leg": "Drone de topographie TP équipé d'un objectif calibré", "exp": "**Principe :** L'objectif convergent forme une image réelle rétrécie du terrassement sur le capteur CMOS selon l'échelle <b>|&gamma;| = <i>f'</i> / <i>H</i></b>, permettant de calculer les volumes de terre en 3D."}
    ]

    if "sujet_ltp_tire" not in st.session_state:
        st.session_state.sujet_ltp_tire = None

    if st.button("TIRER AU SORT UN CHANTIER TP (LENTILLES)", key="btn_tirage_ltp", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_ltp_tire]
        st.session_state.sujet_ltp_tire = random.choice(choix)
        st.session_state.mesures_ltp_log = []
        st.rerun()

    if st.session_state.sujet_ltp_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un chantier de Travaux Publics.")
    else:
        idx_ltp = st.session_state.sujet_ltp_tire
        data_ltp = sujets_len_tp[idx_ltp]
        st.success(f"Chantier attribué : **{data_ltp['titre']}**")
        st.markdown(data_ltp["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_ltp["img"], caption=data_ltp["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_ltp['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_len_tp.jpg", caption="La pause BD : Quand la mire est tenue à l'envers sur le chantier !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_len_tp.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_ltp_log" not in st.session_state: st.session_state.mesures_ltp_log = []
        if idx_ltp == 0:
            st.slider("Distance niveau optique - mire (mètres) :", 10.0, 80.0, 40.0, 2.0, key="slider_ltp_s0")
        elif idx_ltp == 1:
            st.slider("Distance LED - Lentille de Fresnel (mm) [Foyer F = 80 mm] :", 60.0, 100.0, 80.0, 1.0, key="slider_ltp_s1")
        else:
            c1_d, c2_d = st.columns(2)
            with c1_d: st.slider("Altitude de vol du drone H (mètres) :", 30.0, 150.0, 80.0, 5.0, key="slider_ltp_s2")
            with c2_d: st.slider("Distance focale de l'objectif f' (mm) :", 16.0, 50.0, 24.0, 2.0, key="slider_ltp_f_s2")

        if st.button("ENREGISTRER CE RELEVÉ TP", key="btn_rel_ltp", use_container_width=True):
            if "ltp_mesure_courante" in st.session_state:
                st.session_state.mesures_ltp_log.append(st.session_state.ltp_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_len_tp_matplotlib(idx_ltp), use_container_width=True)
        if st.session_state.mesures_ltp_log:
            df_ltp = pd.DataFrame(st.session_state.mesures_ltp_log, columns=["Paramètre 1", "Paramètre 2", "Calcul", "Résultat"])
            st.dataframe(df_ltp, use_container_width=True, hide_index=True)

    st.write("---")
    if "ltp_verrouille_tab5" not in st.session_state: st.session_state.ltp_verrouille_tab5 = False
    verrou_ltp = st.session_state.ltp_verrouille_tab5
    sujet_actif_ltp = st.session_state.get("sujet_ltp_tire", None)
    afficher_atelier_len_tp(sujet_actif_ltp, verrouille=verrou_ltp)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ltp = st.checkbox("Je certifie avoir complété l'Atelier 5 (Travaux Publics - Lentilles).", key="certif_ltp5", disabled=verrou_ltp)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_exp_ltp5", use_container_width=True, disabled=verrou_ltp):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_ltp is None or not case_certif_ltp:
            st.error("Action refusée : Tirez au sort un chantier et cochez la case de certification.")
        else:
            bq = BANQUES_LEN_TP[sujet_actif_ltp]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_ltp_{sujet_actif_ltp}", []) if st.session_state.get(f"ltp_at5_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_ltp}") == rep)
            st.session_state.score_ltp5_p1, st.session_state.score_lm5_p2, st.session_state.score_final_ltp5 = sc_q, sc_t, sc_q + sc_t
            st.session_state.ltp_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("ltp_verrouille_tab5", False) and sujet_actif_ltp is not None:
        scr1, scr2, tot_s = st.session_state.score_ltp5_p1, st.session_state.score_lm5_p2, st.session_state.score_final_ltp5
        ts_ltp = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 5 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LEN_TP[sujet_actif_ltp]
        html_ltp = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 5 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 5 : Travaux Publics (Lentilles Convergentes) - {sujets_len_tp[sujet_actif_ltp]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_ltp}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_ltp_{sujet_actif_ltp}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"ltp_at5_g_{qid_curr}", "Choisir...")
            html_ltp += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td></tr>"
        html_ltp += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_ltp}", "Choisir...")
            html_ltp += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td></tr>"
        html_ltp += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 5 (.html)", data=html_ltp, file_name=preparer_nom_fichier("Rapport_Atelier_5_TP_Lentilles").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab6:
    st.header("Atelier 6 : Applications dans le domaine du Transport Routier")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles convergentes au cœur de l'éclairage et des aides à la conduite :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans les véhicules modernes, les lentilles convergentes assurent la collimation des <strong>phares projecteurs</strong>, la formation d'images sur les <strong>caméras ADAS</strong> de freinage d'urgence et la focalisation des <strong>capteurs de pluie</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_len_trans = [
        {"titre": "Cas Transport N°1 : Phare lenticulaire convergent & Volet de coupure", "img": "len_trans_phare.jpg", "leg": "Optique lenticulaire convergente sur projecteur poids lourd", "exp": "**Principe :** La source lumineuse est placée au **foyer objet F** d'une lentille plan-convexe pour émettre un faisceau parallèle. En feux de croisement, un **volet de coupure** bloque les rayons vers le haut."},
        {"titre": "Cas Transport N°2 : Caméra ADAS frontale & Freinage d'urgence", "img": "len_trans_adas.jpg", "leg": "Caméra d'aide à la conduite derrière le pare-brise", "exp": "**Principe :** L'objectif convergent projette une image réelle du trafic sur le capteur CMOS. Le calculateur déduit la distance d'obstacle via le grandissement : <b><i>D</i> &approx; (<i>AB</i> &times; <i>f'</i>) / <i>A'B'</i></b>."},
        {"titre": "Cas Transport N°3 : Capteur de pluie à lentilles de collimation et focalisation", "img": "len_trans_pluie.jpg", "leg": "Bloc optique du capteur de pluie automatique", "exp": "**Principe :** Une première lentille convergente rend parallèle le faisceau d'une LED infrarouge placée en **F**, tandis qu'une seconde lentille focalise le faisceau réfléchi en **F'** sur une photodiode."}
    ]

    if "sujet_ltr_tire" not in st.session_state:
        st.session_state.sujet_ltr_tire = None

    if st.button("TIRER AU SORT UN SUJET TRANSPORT (LENTILLES)", key="btn_tirage_ltr", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_ltr_tire]
        st.session_state.sujet_ltr_tire = random.choice(choix)
        st.session_state.mesures_ltr_log = []
        st.rerun()

    if st.session_state.sujet_ltr_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique du Transport Routier.")
    else:
        idx_ltr = st.session_state.sujet_ltr_tire
        data_ltr = sujets_len_trans[idx_ltr]
        st.success(f"Étude attribuée : **{data_ltr['titre']}**")
        st.markdown(data_ltr["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_ltr["img"], caption=data_ltr["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_ltr['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_len_trans.jpg", caption="La pause BD : Quand la caméra ADAS confond un panneau avec un camion !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_len_trans.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_ltr_log" not in st.session_state: st.session_state.mesures_ltr_log = []
        if idx_ltr == 0:
            c1_t, c2_t = st.columns(2)
            with c1_t: st.slider("Position de la source LED (mm) [Foyer F = 40 mm] :", 25.0, 55.0, 40.0, 1.0, key="slider_ltr_s0")
            with c2_t: st.radio("Mode d'éclairage :", ["Feux de croisement (Volet actif)", "Feux de route (Plein phare)"], key="radio_ltr_feux_s0")
        elif idx_ltr == 1:
            st.slider("Distance du véhicule précédent D (mètres) :", 5.0, 80.0, 35.0, 1.0, key="slider_ltr_s1")
        else:
            st.slider("Intensité de la pluie sur le pare-brise (%) :", 0, 100, 20, 5, key="slider_ltr_s2")

        if st.button("ENREGISTRER CE CONTRÔLE TRANSPORT", key="btn_rel_ltr", use_container_width=True):
            if "ltr_mesure_courante" in st.session_state:
                st.session_state.mesures_ltr_log.append(st.session_state.ltr_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_len_trans_matplotlib(idx_ltr), use_container_width=True)
        if st.session_state.mesures_ltr_log:
            df_ltr = pd.DataFrame(st.session_state.mesures_ltr_log, columns=["Paramètre", "Configuration", "Mesure optique", "Diagnostic"])
            st.dataframe(df_ltr, use_container_width=True, hide_index=True)

    st.write("---")
    if "ltr_verrouille_tab6" not in st.session_state: st.session_state.ltr_verrouille_tab6 = False
    verrou_ltr = st.session_state.ltr_verrouille_tab6
    sujet_actif_ltr = st.session_state.get("sujet_ltr_tire", None)
    afficher_atelier_len_trans(sujet_actif_ltr, verrouille=verrou_ltr)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ltr = st.checkbox("Je certifie avoir complété l'Atelier 6 (Transport Routier - Lentilles).", key="certif_ltr6", disabled=verrou_ltr)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_exp_ltr6", use_container_width=True, disabled=verrou_ltr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_ltr is None or not case_certif_ltr:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_LEN_TRANS[sujet_actif_ltr]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_ltr_{sujet_actif_ltr}", []) if st.session_state.get(f"ltr_at6_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_ltr}") == rep)
            st.session_state.score_ltr6_p1, st.session_state.score_ltr6_p2, st.session_state.score_final_ltr6 = sc_q, sc_t, sc_q + sc_t
            st.session_state.ltr_verrouille_tab6 = True
            st.rerun()

    if st.session_state.get("ltr_verrouille_tab6", False) and sujet_actif_ltr is not None:
        scr1, scr2, tot_s = st.session_state.score_ltr6_p1, st.session_state.score_ltr6_p2, st.session_state.score_final_ltr6
        ts_ltr = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 6 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LEN_TRANS[sujet_actif_ltr]
        html_ltr = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 6 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 6 : Transport Routier (Lentilles Convergentes) - {sujets_len_trans[sujet_actif_ltr]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_ltr}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_ltr_{sujet_actif_ltr}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"ltr_at6_g_{qid_curr}", "Choisir...")
            html_ltr += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td></tr>"
        html_ltr += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_ltr}", "Choisir...")
            html_ltr += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td></tr>"
        html_ltr += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 6 (.html)", data=html_ltr, file_name=preparer_nom_fichier("Rapport_Atelier_6_Transport_Lentilles").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab7:
    st.header("Atelier 7 : Applications dans le domaine du Géomètre Topographe")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles convergentes dans les instruments de topographie et de cartographie :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Pour viser des prismes à plusieurs kilomètres, lire des graduations micrométriques ou cartographier un territoire depuis un avion, le géomètre utilise des <strong>lunettes astronomiques/terrestres</strong>, des <strong>microscopes de lecture</strong> et des <strong>chambres photogrammétriques</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_len_geo = [
        {"titre": "Mission N°1 : Lunette de Station Totale & Collimation infrarouge", "img": "len_geo_station.jpg", "leg": "Lunette optique haute précision d'une station totale", "exp": "**Principe :** L'objectif convergent (<i>f'</i> = 200 mm) forme une image nette du prisme sur le réticule, grossie 30× par l'oculaire, tandis qu'une lentille de collimation rend le faisceau infrarouge parallèle."},
        {"titre": "Mission N°2 : Microscope de lecture optique & Vernier micrométrique", "img": "len_geo_microscope.jpg", "leg": "Microscope de lecture des cercles gradués d'un théodolite", "exp": "**Principe :** L'association d'un objectif à courte focale (|&gamma;<sub>1</sub>|) et d'un oculaire (<i>G</i><sub>2</sub>) donne un grossissement total <b><i>G</i> = |&gamma;<sub>1</sub>| &times; <i>G</i><sub>2</sub></b> permettant de lire la seconde d'arc."},
        {"titre": "Mission N°3 : Photogrammétrie aérienne & Stéréorestitution 3D", "img": "len_geo_avion.jpg", "leg": "Chambre métrique aérienne à objectif convergent calibré", "exp": "**Principe :** L'objectif aérien projette l'image du terrain dans son plan focal image <b><i>F'</i></b> à l'échelle <b>1 / <i>E</i> = <i>f'</i> / <i>H</i></b> pour produire des orthophotoplans et des modèles numériques de terrain."}
    ]

    if "sujet_lgeo_tire" not in st.session_state:
        st.session_state.sujet_lgeo_tire = None

    if st.button("TIRER AU SORT UNE MISSION GÉOMÈTRE (LENTILLES)", key="btn_tirage_lgeo", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_lgeo_tire]
        st.session_state.sujet_lgeo_tire = random.choice(choix)
        st.session_state.mesures_lgeo_log = []
        st.rerun()

    if st.session_state.sujet_lgeo_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort une mission de Géomètre Topographe.")
    else:
        idx_lgeo = st.session_state.sujet_lgeo_tire
        data_lgeo = sujets_len_geo[idx_lgeo]
        st.success(f"Mission attribuée : **{data_lgeo['titre']}**")
        st.markdown(data_lgeo["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_lgeo["img"], caption=data_lgeo["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_lgeo['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_len_geo.jpg", caption="La pause BD : Quand un oiseau se pose juste devant l'objectif de la station !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_len_geo.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_lgeo_log" not in st.session_state: st.session_state.mesures_lgeo_log = []
        if idx_lgeo == 0:
            st.slider("Distance de visée du prisme D (mètres) :", 20.0, 500.0, 150.0, 10.0, key="slider_lgeo_s0")
        elif idx_lgeo == 1:
            c1_g, c2_g = st.columns(2)
            with c1_g: st.slider("Grandissement objectif |γ1| :", 5, 20, 10, 1, key="slider_lgeo_g1_s1")
            with c2_g: st.slider("Grossissement oculaire G2 :", 2, 15, 5, 1, key="slider_lgeo_g2_s1")
        else:
            c1_a, c2_a = st.columns(2)
            with c1_a: st.slider("Altitude de vol de l'avion H (mètres) :", 500.0, 3000.0, 1500.0, 100.0, key="slider_lgeo_s2")
            with c2_a: st.slider("Focale de la chambre aérienne f' (mm) :", 80.0, 300.0, 150.0, 10.0, key="slider_lgeo_f_s2")

        if st.button("ENREGISTRER CE POINT TOPOGRAPHIQUE", key="btn_rel_lgeo", use_container_width=True):
            if "lgeo_mesure_courante" in st.session_state:
                st.session_state.mesures_lgeo_log.append(st.session_state.lgeo_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_len_geo_matplotlib(idx_lgeo), use_container_width=True)
        if st.session_state.mesures_lgeo_log:
            df_lgeo = pd.DataFrame(st.session_state.mesures_lgeo_log, columns=["Paramètre 1", "Paramètre 2", "Calcul optique", "Validation"])
            st.dataframe(df_lgeo, use_container_width=True, hide_index=True)

    st.write("---")
    if "lgeo_verrouille_tab7" not in st.session_state: st.session_state.lgeo_verrouille_tab7 = False
    verrou_lgeo = st.session_state.lgeo_verrouille_tab7
    sujet_actif_lgeo = st.session_state.get("sujet_lgeo_tire", None)
    afficher_atelier_len_geo(sujet_actif_lgeo, verrouille=verrou_lgeo)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_lgeo = st.checkbox("Je certifie avoir complété l'Atelier 7 (Géomètre Topographe - Lentilles).", key="certif_lgeo7", disabled=verrou_lgeo)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_exp_lgeo7", use_container_width=True, disabled=verrou_lgeo):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_lgeo is None or not case_certif_lgeo:
            st.error("Action refusée : Tirez au sort une mission et cochez la case de certification.")
        else:
            bq = BANQUES_LEN_GEO[sujet_actif_lgeo]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_lgeo_{sujet_actif_lgeo}", []) if st.session_state.get(f"lgeo_at7_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_lgeo}") == rep)
            st.session_state.score_lgeo7_p1, st.session_state.score_lgeo7_p2, st.session_state.score_final_lgeo7 = sc_q, sc_t, sc_q + sc_t
            st.session_state.lgeo_verrouille_tab7 = True
            st.rerun()

    if st.session_state.get("lgeo_verrouille_tab7", False) and sujet_actif_lgeo is not None:
        scr1, scr2, tot_s = st.session_state.score_lgeo7_p1, st.session_state.score_lgeo7_p2, st.session_state.score_final_lgeo7
        ts_lgeo = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 7 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LEN_GEO[sujet_actif_lgeo]
        html_lgeo = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 7 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 7 : Géomètre Topographe (Lentilles Convergentes) - {sujets_len_geo[sujet_actif_lgeo]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_lgeo}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_lgeo_{sujet_actif_lgeo}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"lgeo_at7_g_{qid_curr}", "Choisir...")
            html_lgeo += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td></tr>"
        html_lgeo += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_lgeo}", "Choisir...")
            html_lgeo += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td></tr>"
        html_lgeo += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 7 (.html)", data=html_lgeo, file_name=preparer_nom_fichier("Rapport_Atelier_7_Geometre_Lentilles").replace(".txt", ".html"), mime="text/html", use_container_width=True)






