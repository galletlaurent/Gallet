# -*- coding: utf-8 -*-

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Application Réfraction ",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application Réfraction")
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
    "Loi de la Réfraction",
    "Double réfraction",
    "Fibre optique et réflexion totale",
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
tab8 = onglets[8] 






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

def dessiner_fibre_optique_avancee_matplotlib():
    """Genere le schema complet d'une fibre optique à sauts d'indice.
    Incorpore l'ouverture numerique (ON), l'angle maximal d'injection dans l'air,
    la normale d'entree horizontale avec son angle i1, et les rebonds internes.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions du canevas
    w = 600
    h = 280
    
    # Structure de la fibre (interfaces horizontales)
    y_gaine_haut = 60.0
    y_gaine_bas = 220.0
    hauteur_coeur = y_gaine_bas - y_gaine_haut
    y_centre = h / 2.0

    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Alignement repere informatique inversé
    ax.axis("off")

    # 1. Récupération des variables de session Streamlit
    n_coeur = st.session_state.get("var_n_coeur", 1.50)
    n_gaine = st.session_state.get("var_n_gaine", 1.40)
    n_air = 1.00  # Milieu extérieur d'injection
    
    nb_rebonds_max = st.session_state.get("var_nb_rebonds", 3)
    
    nom_lampe = st.session_state.get("var_choix_lampe_fibre", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[nom_lampe]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    # Fond visuel : Gaines et Coeur
    ax.add_patch(patches.Rectangle((0, 10), w, y_gaine_haut - 10, facecolor="#38bdf8", alpha=0.05, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, y_gaine_haut), w, hauteur_coeur, facecolor="#e0f2fe", alpha=0.12, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, y_gaine_bas), w, h - 10 - y_gaine_bas, facecolor="#38bdf8", alpha=0.05, edgecolor="none"))
    
    # Lignes d'interfaces horizontales
    ax.plot([0, w], [y_gaine_haut, y_gaine_haut], color="#475569", lw=1.5, zorder=3)
    ax.plot([0, w], [y_gaine_bas, y_gaine_bas], color="#475569", lw=1.5, zorder=3)

    # Face d'entrée de la fibre (Dioptre d'entrée vertical à x = 60)
    x_entree = 60.0
    ax.plot([x_entree, x_entree], [y_gaine_haut, y_gaine_bas], color="#94a3b8", lw=2, zorder=3)

    if n_coeur <= n_gaine:
        msg, color = "ERREUR : L'indice du cœur doit être strictement supérieur à celui de la gaine.", "#ef4444"
        txt_math = "Guidage impossible (n_coeur <= n_gaine)"
        ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
        st.session_state.opt4_txt_box_fibre = txt_math
        return fig

    # 2. CALCULS THÉORIQUES
    on = math.sqrt(n_coeur**2 - n_gaine**2)
    
    if on <= 1.0:
        i_max_rad = math.asin(on / n_air)
        i_max_deg = math.degrees(i_max_rad)
        txt_i_max = f"{i_max_deg:.1f}°"
    else:
        i_max_rad = math.radians(90.0)
        i_max_deg = 90.0
        txt_i_max = "90° (Total)"

    theta_c_rad = math.asin(n_gaine / n_coeur)
    theta_c_deg = math.degrees(theta_c_rad)

    # Angle d'injection choisi à l'entrée de la fibre (par rapport à l'HORIZONTALE)
    i1_deg = st.session_state.get("var_angle_injection_externe", 25.0)
    i1_rad = math.radians(i1_deg)

    # Réfraction au dioptre d'entrée (Air -> Cœur)
    sin_r1 = (n_air * math.sin(i1_rad)) / n_coeur
    r1_rad = math.asin(sin_r1)
    
    alpha_interne_rad = r1_rad
    theta_interne_rad = (math.pi / 2.0) - alpha_interne_rad
    theta_interne_deg = math.degrees(theta_interne_rad)

    # --- AJOUT : NORMALE HORIZONTALE D'ENTRÉE ET SON ANGLE ---
    # Ligne pointillée horizontale représentant l'axe central (normale de la face d'entrée)
    ax.plot([15, x_entree + 40], [y_centre, y_centre], color="#64748b", linestyle=":", lw=1.2, zorder=2)
    
    # Rayon incident extérieur (de l'air jusqu'à la face d'entrée)
    x_source = x_entree - 55.0
    y_source = y_centre - 55.0 * math.tan(i1_rad)
    ax.annotate("", xy=(x_entree, y_centre), xytext=(x_source, y_source),
                arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

    # Arc pour l'angle d'incidence i1 à l'entrée (mesuré entre l'horizontale et le rayon incident)
    # Compte tenu du repère inversé, l'arc s'oriente de 180° à 180° + i1_deg
    arc_i1 = patches.Arc((x_entree, y_centre), 35, 35, angle=0, 
                        theta1=180, theta2=180 + i1_deg, 
                        edgecolor="#cbd5e1", lw=1.2, zorder=5)
    ax.add_patch(arc_i1)
    
    # Positionnement du texte i1 au-dessus de l'axe pointillé
    x_text_i1 = x_entree - 25 * math.cos(math.radians(i1_deg / 2))
    y_text_i1 = y_centre - 25 * math.sin(math.radians(i1_deg / 2))
    ax.text(x_text_i1, y_text_i1, "i1", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center", va="bottom")
    # Initialisation du parcours
    x_actuel = x_entree
    y_actuel = y_centre
    signe_y = 1  # Commence en montant vers la gaine du haut

    # 3. PROPAGATION ET REBONDS MULTIPLES
    if theta_interne_deg >= theta_c_deg:
        msg, color = "GUIDAGE VALIDÉ : Réflexions totales internes parfaites.", "#10b981"
        
        for rebond in range(nb_rebonds_max):
            if signe_y == -1:
                y_suivant = y_gaine_haut
                dy = y_actuel - y_gaine_haut
            else:
                y_suivant = y_gaine_bas
                dy = y_gaine_bas - y_actuel

            dx = dy / math.tan(alpha_interne_rad)
            x_suivant = x_actuel + dx

            if x_suivant > w - 10:
                x_suivant = w - 10
                y_suivant = y_actuel + (signe_y * (x_suivant - x_actuel) * math.tan(alpha_interne_rad))
                ax.annotate("", xy=(x_suivant, y_suivant), xytext=(x_actuel, y_actuel),
                            arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
                break

            # Tracé du segment de rebond
            ax.annotate("", xy=(x_suivant, y_suivant), xytext=(x_actuel, y_actuel),
                        arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

            # --- CORRECTION DE L'ARC INTERNE (i > ic) ---
            if rebond == 0:
                # --- CORRECTION DE LA NORMALE (MONTE VERS LE CŒUR) ---
                # Dans le repère inversé, soustraire 40 fait monter la ligne vers le haut de l'écran
                ax.plot([x_suivant, x_suivant], [y_suivant - 40, y_suivant], color="#64748b", linestyle=":", lw=1.2)
                
                # --- CORRECTION DE L'ARC (QUADRANT HAUT-GAUCHE INTERNE) ---
                # L'angle 270° pointe vers le haut. On dessine l'arc entre (270 - theta) et 270°
                arc_r = patches.Arc((x_suivant, y_suivant), 35, 35, angle=0, 
                                    theta1=270 - theta_interne_deg, theta2=270, 
                                    edgecolor="#cbd5e1", lw=1, zorder=5)
                ax.add_patch(arc_r)
                
                # --- CORRECTION DU TEXTE (AU-DESSUS DE LA PAROI INFÉRIEURE) ---
                x_text_refl = x_suivant - 22 * math.sin(theta_interne_rad / 2)
                y_text_refl = y_suivant - 22 * math.cos(theta_interne_rad / 2)  # Moins pour monter le texte dans le cœur
                ax.text(x_text_refl, y_text_refl, "i > ic", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right", va="bottom")

            x_actuel = x_suivant
            y_actuel = y_suivant
            signe_y *= -1
            
        if x_actuel < w - 10:
            x_fin = w - 10
            y_fin = y_actuel + (signe_y * (x_fin - x_actuel) * math.tan(alpha_interne_rad))
            ax.plot([x_actuel, x_fin], [y_actuel, y_fin], color=couleur_laser, lw=2.5, zorder=4)
            
    else:
        msg, color = "RÉFRACTION DANS LA GAINE : Rayon perdu (Angle trop grand).", "#ef4444"
        dy = y_actuel - y_gaine_haut
        dx = dy / math.tan(alpha_interne_rad)
        x_perte = x_actuel + dx
        ax.annotate("", xy=(x_perte, y_gaine_haut), xytext=(x_actuel, y_actuel), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        sin_gaine = (n_coeur * math.sin(theta_interne_rad)) / n_gaine
        angle_gaine_rad = math.asin(sin_gaine)
        dx_fuite = 40 * math.sin(angle_gaine_rad)
        dy_fuite = 40 * math.cos(angle_gaine_rad)
        ax.annotate("", xy=(x_perte + dx_fuite, y_gaine_haut - dy_fuite), xytext=(x_perte, y_gaine_haut), 
                    arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=1.5, linestyle="--"), zorder=4)

    # 4. Textes d'affichage et habillage
    txt_math = (
        f"Données de la Fibre :\n"
        f"• Ouverture Numérique (ON) = {on:.3f}\n"
        f"• Cône d'Acceptance (i_max) = {txt_i_max}\n"
        f"• Incidence choisie i1 = {i1_deg:.1f}°\n"
        f"• Angle critique interne (ic) = {theta_c_deg:.1f}°\n"
        f"• Angle d'impact interne = {theta_interne_deg:.1f}°\n"
        f"• Nombre de rebonds tracés = {nb_rebonds_max}"
    )

    ax.text(25, 20, "OPTIQUE GÉOMÉTRIQUE : LA FIBRE OPTIQUE PRO", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    
    ax.text(w - 60, y_gaine_haut - 12, "Gaine (n2)", color="#64748b", fontsize=7, fontweight="bold")
    ax.text(w - 60, y_centre, "Cœur (n1)", color="#94a3b8", fontsize=8, fontweight="bold")
    ax.text(w - 60, y_gaine_bas + 15, "Gaine (n2)", color="#64748b", fontsize=7, fontweight="bold")
    ax.text(x_entree - 10, y_gaine_bas - 15, "Face\nd'entrée", color="#94a3b8", fontsize=6, ha="right", style="italic")

    st.session_state.opt4_txt_box_fibre = txt_math
    return fig

def dessiner_reflexion_totale_directe_matplotlib():
    """Genere le schema d'une reflexion totale interne pure (Source en bas, Dioptre horizontal).
    Version vectorielle haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    w = 600
    h = 280
    x0 = 300.0  
    y_dioptre = 110.0  # Position horizontale de la surface

    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(15, w - 15)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Alignement sur le repere informatique inversé
    ax.axis("off")

    # Lecture des paramètres de la session active
    m1_nom = st.session_state.get("var_choix_milieu_bas", "Verre Couronne (n = 1.52)")
    m2_nom = st.session_state.get("var_choix_milieu_haut", "Air (n = 1.00)")
    
    n1 = st.session_state.produits_indices[m1_nom] if "produits_indices" in st.session_state else 1.52
    n2 = st.session_state.produits_indices[m2_nom] if "produits_indices" in st.session_state else 1.00

    nom_lampe = st.session_state.get("var_choix_lampe_refl", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[nom_lampe]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    theta1_deg = st.session_state.get("var_angle_incidence_bas", 50.0)
    theta1_rad = math.radians(theta1_deg)

    # Tracé des milieux (Milieu léger en haut, Milieu dense transparent en bas)
    ax.add_patch(patches.Rectangle((15, 10), w - 30, y_dioptre - 10, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    ax.add_patch(patches.Rectangle((15, y_dioptre), w - 30, h - 10 - y_dioptre, facecolor="#e0f2fe", alpha=0.2, edgecolor="none"))
    ax.plot([15, w - 15], [y_dioptre, y_dioptre], color="#475569", lw=2, zorder=3)

    # Axe de la Normale verticale (S'arrête là où il faut selon le cas pour la clarté)
    ax.plot([x0, x0], [20, h - 20], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2, zorder=2)
    ax.text(x0 + 6, 25, "Normale", color="#64748b", fontsize=7, fontweight="bold", ha="left")

    # Rayon incident provenant DU BAS et allant vers le centre (x0, y_dioptre)
    longueur_rayon = 100
    x_inc = x0 - longueur_rayon * math.sin(theta1_rad)
    y_inc = y_dioptre + longueur_rayon * math.cos(theta1_rad) # Plus grand car l'axe Y descend
    ax.annotate("", xy=(x0, y_dioptre), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

    # Arc et étiquette pour l'angle d'incidence i (en bas à gauche du point d'impact)
    # L'angle 90° pointe vers le bas. L'arc va de 90° à 90° + theta1
    arc_i = patches.Arc((x0, y_dioptre), 40, 40, angle=0, theta1=90, theta2=90 + theta1_deg, edgecolor="#cbd5e1", lw=1.2, zorder=5)
    ax.add_patch(arc_i)
    ax.text(x0 - 15 * math.sin(theta1_rad/2) - 8, y_dioptre + 25 * math.cos(theta1_rad/2), "i", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right")

    # Calcul de la condition limite
    if n1 > n2:
        sin_lim = n2 / n1
        angle_critique_deg = math.degrees(math.asin(sin_lim))
    else:
        sin_lim = 2.0  # Impossible d'avoir de réflexion totale si n1 <= n2
        angle_critique_deg = 0.0

    sin_theta2 = (n1 * math.sin(theta1_rad)) / n2

    if sin_theta2 > 1.0:
        # --- CAS DE LA RÉFLEXION TOTALE INTERNE PURE ---
        # Le rayon rebondit vers le bas à droite
        x_refl = x0 + longueur_rayon * math.sin(theta1_rad)
        y_refl = y_dioptre + longueur_rayon * math.cos(theta1_rad)
        ax.annotate("", xy=(x_refl, y_refl), xytext=(x0, y_dioptre), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        # Arc pour l'angle réfléchi r (en bas à droite du point d'impact)
        # Il va de 90 - theta1 jusqu'à 90° pour épouser la normale du bas
        arc_r_refl = patches.Arc((x0, y_dioptre), 40, 40, angle=0, theta1=90 - theta1_deg, theta2=90, edgecolor=couleur_laser, lw=1.2, zorder=5)
        ax.add_patch(arc_r_refl)
        ax.text(x0 + 15 * math.sin(theta1_rad/2) + 8, y_dioptre + 25 * math.cos(theta1_rad/2), "r", color=couleur_laser, fontsize=8, fontweight="bold", ha="left")

        msg, color = "RÉFLEXION TOTALE INTERNE : Le rayon reste piégé.", "#ef4444"
        txt_math = f"Indices : n1={n1:.2f} > n2={n2:.2f}\nAngle critique = {angle_critique_deg:.1f}°\ni = {theta1_deg:.1f}° > Angle critique\n-> 100% Réfléchi !"
    else:
        # --- CAS DE LA RÉFRACTION CLASSIQUE ---
        # Le rayon s'échappe vers le haut à droite
        theta2_rad = math.asin(sin_theta2)
        theta2_deg = math.degrees(theta2_rad)
        
        x_ref = x0 + longueur_rayon * math.sin(theta2_rad)
        y_ref = y_dioptre - longueur_rayon * math.cos(theta2_rad) # Moins car il monte dans le repère inversé
        ax.annotate("", xy=(x_ref, y_ref), xytext=(x0, y_dioptre), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        # Arc pour l'angle réfracté r (en haut à droite de la normale)
        # L'angle 270° pointe vers le haut. On tourne de 270° à 270° + theta2
        arc_r = patches.Arc((x0, y_dioptre), 40, 40, angle=0, theta1=270, theta2=270 + theta2_deg, edgecolor="#cbd5e1", lw=1.2, zorder=5)
        ax.add_patch(arc_r)
        ax.text(x0 + 15 * math.sin(theta2_rad/2) + 8, y_dioptre - 25 * math.cos(theta2_rad/2), "r", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left")

        msg, color = "RÉFRACTION CLASSIQUE : Le rayon traverse l'interface.", "#10b981"
        txt_math = f"Indices : n1={n1:.2f}, n2={n2:.2f}\nAngle critique = {angle_critique_deg:.1f}°\ni = {theta1_deg:.1f}°\nr = {theta2_deg:.1f}°"

    # Habillage textuel
    ax.text(25, 20, "ATELIER DE SPÉCIALITÉ - RÉFLEXION TOTALE INTERNE", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    ax.text(25, y_dioptre - 15, f"Milieu supérieur : {m2_nom}", color="#64748b", fontsize=7, ha="left")
    ax.text(25, y_dioptre + 20, f"Milieu inférieur : {m1_nom}", color="#94a3b8", fontsize=7, ha="left")

    st.session_state.opt4_txt_box_refl_totale = txt_math
    return fig

def dessiner_double_refraction_lame_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    w = 600
    h = 280
    x0 = 300.0  
    y_dioptre1, y_dioptre2 = 90.0, 180.0
    epaisseur_lame_px = y_dioptre2 - y_dioptre1

    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(15, w - 15)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    m1_nom = st.session_state.get("var_choix_milieu1_double", "Air (n = 1.00)")
    m2_nom = st.session_state.get("var_choix_milieu2_double", "Verre Couronne (n = 1.52)")
    m3_nom = st.session_state.get("var_choix_milieu3_double", "Air (n = 1.00)")
    
    n1 = st.session_state.produits_indices[m1_nom] if "produits_indices" in st.session_state else 1.00
    n2 = st.session_state.produits_indices[m2_nom] if "produits_indices" in st.session_state else 1.52
    n3 = st.session_state.produits_indices[m3_nom] if "produits_indices" in st.session_state else 1.00

    nom_lampe2 = st.session_state.get("var_choix_lampe_double2", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[nom_lampe2]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    theta1_deg = st.session_state.get("var_angle_double", 45.0)
    theta1_rad = math.radians(theta1_deg)

    ax.add_patch(patches.Rectangle((15, 10), w - 30, y_dioptre1 - 10, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    ax.add_patch(patches.Rectangle((15, y_dioptre1), w - 30, epaisseur_lame_px, facecolor="#e0f2fe", alpha=0.2, edgecolor="none"))
    ax.add_patch(patches.Rectangle((15, y_dioptre2), w - 30, h - 10 - y_dioptre2, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    
    ax.plot([15, w - 15], [y_dioptre1, y_dioptre1], color="#475569", lw=2, zorder=3)
    ax.plot([15, w - 15], [y_dioptre2, y_dioptre2], color="#475569", lw=2, zorder=3)

    # Axe de la Normale 1 (S'arrête au premier dioptre pour la clarté)
    ax.plot([x0, x0], [20, y_dioptre1 + 40], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2, zorder=2)
    ax.text(x0 + 6, 25, "Normale 1", color="#64748b", fontsize=7, fontweight="bold", ha="left")

    x_inc = x0 - 70 * math.sin(theta1_rad)
    y_inc = y_dioptre1 - 70 * math.cos(theta1_rad)
    ax.annotate("", xy=(x0, y_dioptre1), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

    sin_theta2 = (n1 * math.sin(theta1_rad)) / n2

    if sin_theta2 > 1.0:
        x_total = x0 + 80 * math.sin(theta1_rad)
        y_total = y_dioptre1 - 80 * math.cos(theta1_rad)
        ax.annotate("", xy=(x_total, y_total), xytext=(x0, y_dioptre1), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        msg, color = "REFLEXION TOTALE INTERNE amont.", "#ef4444"
        txt_math = "Reflexion totale amont !\nSin(r1) impossible > 1"
        ax.text(x0 + 40, y_dioptre1 - 30, "Rayon reflechi", color="#ef4444", fontsize=7, style="italic", ha="left")
    else:
        theta2_rad = math.asin(sin_theta2)
        theta2_deg = math.degrees(theta2_rad)

        dx_px = epaisseur_lame_px * math.tan(theta2_rad)
        x_sortie = x0 + dx_px
        ax.annotate("", xy=(x_sortie, y_dioptre2), xytext=(x0, y_dioptre1), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        # Positionnement optimisé du texte de r1 près de son arc
        ax.text(x0 + 15 * math.sin(theta2_rad/2) + 5, y_dioptre1 + 25 * math.cos(theta2_rad/2), "r1", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left", va="center")

        # Axe de la Normale 2 (Dépasse un peu à l'intérieur de la lame)
        ax.plot([x_sortie, x_sortie], [y_dioptre2 - 40, h - 15], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2, zorder=2)
        ax.text(x_sortie + 6, y_dioptre2 + 15, "Normale 2", color="#64748b", fontsize=7, fontweight="bold", ha="left")

        sin_theta3 = (n2 * math.sin(theta2_rad)) / n3

        if sin_theta3 > 1.0:
            x_total2 = x_sortie - 70 * math.sin(theta2_rad)
            y_total2 = y_dioptre2 - 70 * math.cos(theta2_rad)
            ax.annotate("", xy=(x_total2, y_total2), xytext=(x_sortie, y_dioptre2), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
            msg, color = "REFLEXION TOTALE INTERNE basse.", "#ef4444"
            txt_math = f"Incidence i1 = {theta1_deg:.1f}°\nRefraction r1 = {theta2_deg:.1f}°\nSortie : Miroir bas !"
        else:
            theta3_rad = math.asin(sin_theta3)
            theta3_deg = math.degrees(theta3_rad)
            
            x_emerg = x_sortie + 70 * math.sin(theta3_rad)
            y_emerg = y_dioptre2 + 70 * math.cos(theta3_rad)
            ax.annotate("", xy=(x_emerg, y_emerg), xytext=(x_sortie, y_dioptre2), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
            
            # Positionnement de l'étiquette s (angle d'émergence) près de son arc
            ax.text(x_sortie + 20 * math.sin(theta3_rad/2) + 6, y_dioptre2 + 25 * math.cos(theta3_rad/2), "s", color="#ef4444", fontsize=8, fontweight="bold", ha="left", va="center")

            dx_mm = (epaisseur_lame_px * 0.20) * math.sin(theta1_rad - theta2_rad) / math.cos(theta2_rad)
            msg, color = "DOUBLE DIOPTRE : Trajectoires de sorties calculees librement.", "#10b981"
            txt_math = f"Lame :\n• i1 = {theta1_deg:.1f}°\n• r1 = {theta2_deg:.1f}°\n• s = {theta3_deg:.1f}°\n• dx = {abs(dx_mm):.2f} mm"

            # Arc pour l'angle d'émergence s (en bas à droite du point de sortie)
            arc_s = patches.Arc((x_sortie, y_dioptre2), 40, 40, angle=0, theta1=90 - theta3_deg, theta2=90, edgecolor="#ef4444", lw=1.2, zorder=5)
            ax.add_patch(arc_s)

        # Arc pour l'angle de réfraction r1 (en bas à droite du point d'incidence dans la lame)
        arc_r1 = patches.Arc((x0, y_dioptre1), 40, 40, angle=0, theta1=90 - theta2_deg, theta2=90, edgecolor="#cbd5e1", lw=1.2, zorder=5)
        ax.add_patch(arc_r1)

    ax.text(25, 20, "DOUBLE DIOPTRE ET TRAJECTOIRES", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    ax.text(x_inc - 8, y_inc + 12, "Rayon incident (i1)", color="#cbd5e1", fontsize=7, style="italic", ha="right")

    # Arc corrigé pour l'angle incident i1 (en haut à gauche, du rayon jusqu'à la normale à 270°)
    arc_i1 = patches.Arc((x0, y_dioptre1), 40, 40, angle=0, theta1=270 - theta1_deg, theta2=270, edgecolor="#cbd5e1", lw=1.2, zorder=5)
    ax.add_patch(arc_i1)

    st.session_state.opt4_txt_box_double = txt_math
    return fig

def ajouter_point_mesure_optique_streamlit():
    import math
    theta1_deg = st.session_state.get("var_angle_inc", 30.0)
    theta1_rad = math.radians(theta1_deg)
    
    milieu1 = st.session_state.get("var_choix_milieu1", "Air (n = 1.00)")
    milieu2 = st.session_state.get("var_choix_milieu2", "Eau (n = 1.33)")
    n1 = st.session_state.produits_indices[milieu1] if "produits_indices" in st.session_state else 1.00
    n2 = st.session_state.produits_indices[milieu2] if "produits_indices" in st.session_state else 1.33
    
    sin_i = math.sin(theta1_rad)
    sin_r = (n1 * sin_i) / n2
    
    if sin_r <= 1.0:
        if "mesures_sin_i" not in st.session_state: st.session_state.mesures_sin_i = []
        if "mesures_sin_r" not in st.session_state: st.session_state.mesures_sin_r = []
        if "mesures_i_deg" not in st.session_state: st.session_state.mesures_i_deg = []
        if "mesures_r_deg" not in st.session_state: st.session_state.mesures_r_deg = []
        
        st.session_state.mesures_sin_i.append(round(sin_i, 3))
        st.session_state.mesures_sin_r.append(round(sin_r, 3))
        st.session_state.mesures_i_deg.append(theta1_deg)
        st.session_state.mesures_r_deg.append(round(math.degrees(math.asin(sin_r)), 1))

def reinitialiser_graphique_optique_streamlit():
    st.session_state.mesures_sin_i = []
    st.session_state.mesures_sin_r = []
    st.session_state.mesures_i_deg = []
    st.session_state.mesures_r_deg = []


def dessiner_schema_refraction_simple():
    """Genere le schema de la cuve optique avec le rayon laser incident et refracte/reflechi.
    Version vectorielle haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions fixes constantes du repere d'origine
    wg = 400
    hg = 260
    x0_s = (wg / 2.0) + 100.0  
    y0_s = 170.0        

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(x0_s - 250, x0_s + 150)
    ax.set_ylim(y0_s - 150, y0_s + 110)
    ax.invert_yaxis()  # Alignement sur le repere informatique inversé
    ax.axis("off")

    # Lecture des curseurs de l'Atelier 4 de la session active
    theta1_deg = st.session_state.get("var_angle_inc", 30.0)
    theta1_rad = math.radians(theta1_deg)
    
    milieu1 = st.session_state.get("var_choix_milieu1", "Air (n = 1.00)")
    milieu2 = st.session_state.get("var_choix_milieu2", "Eau (n = 1.33)")
    n1 = st.session_state.produits_indices[milieu1] if "produits_indices" in st.session_state else 1.00
    n2 = st.session_state.produits_indices[milieu2] if "produits_indices" in st.session_state else 1.33
    
    choix_lampe = st.session_state.get("slider_lampe_simple", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[choix_lampe]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    # Tracé des milieux (Rectangle superieur Air / Inferieur Liquide)
    y_fond_liquide = y0_s + 160.0
    ax.add_patch(patches.Rectangle((x0_s - 300, y0_s - 160), 600, 160, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    ax.add_patch(patches.Rectangle((x0_s - 300, y0_s), 600, 160, facecolor="#e0f2fe", alpha=0.2, edgecolor="none"))
    ax.plot([x0_s - 300, x0_s + 300], [y0_s, y0_s], color="#475569", lw=2, zorder=3)
    
    # Axe vertical : La Normale pointillee
    ax.plot([x0_s, x0_s], [y0_s - 150, y_fond_liquide - 10], color="#94a3b8", linestyle="--", lw=1.5, zorder=2)
    
    # Textes pour la normale
    ax.text(x0_s + 8, y0_s - 120, "Normale", color="#94a3b8", fontsize=9, va="center")

    # Longueur totale des rayons
    longueur_rayon = 130

    # --- 1. RAYON INCIDENT ET SON ANGLE ---
    x_inc = x0_s - longueur_rayon * math.sin(theta1_rad)
    y_inc = y0_s - longueur_rayon * math.cos(theta1_rad)
    
    # Tracé du rayon de base
    ax.plot([x_inc, x0_s], [y_inc, y0_s], color=couleur_laser, lw=3, zorder=4)
    
    # Flèche au milieu du rayon incident
    ax.annotate("", xy=(x0_s - (longueur_rayon/2) * math.sin(theta1_rad), y0_s - (longueur_rayon/2) * math.cos(theta1_rad)), 
                xytext=(x_inc, y_inc),
                arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=3, mutation_scale=15), zorder=5)

    # Arc de cercle pour l'angle incident 'i'
    # Compte tenu de l'inversion Y, l'angle vers le haut-gauche est défini géométriquement
    arc_i = patches.Arc((x0_s, y0_s), width=50, height=50, angle=0, theta1=270 - theta1_deg, theta2=270, 
                        color="#f1f5f9", lw=1.5, zorder=5)
    ax.add_patch(arc_i)
    
    # Positionnement du texte 'i'
    x_text_i = x0_s - 35 * math.sin(theta1_rad / 2)
    y_text_i = y0_s - 35 * math.cos(theta1_rad / 2)
    ax.text(x_text_i, y_text_i, "i", color="#f1f5f9", fontsize=11, fontweight="bold", ha="center", va="center")


    # --- 2. RAYON RÉFRACTÉ ET SON ANGLE ---
    sin_theta2 = (n1 * math.sin(theta1_rad)) / n2

    if abs(sin_theta2) <= 1.0:
        theta2_rad = math.asin(sin_theta2)
        theta2_deg = math.degrees(theta2_rad)
        
        x_ref = x0_s + longueur_rayon * math.sin(theta2_rad)
        y_ref = y0_s + longueur_rayon * math.cos(theta2_rad)
        
        # Tracé du rayon de base
        ax.plot([x0_s, x_ref], [y0_s, y_ref], color=couleur_laser, lw=3, zorder=4)
        
        # Flèche au milieu du rayon réfracté
        ax.annotate("", xy=(x0_s + (longueur_rayon/2) * math.sin(theta2_rad), y0_s + (longueur_rayon/2) * math.cos(theta2_rad)), 
                    xytext=(x0_s, y0_s),
                    arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=3, mutation_scale=15), zorder=5)

        # Arc de cercle pour l'angle réfracté 'r' (en bas à droite dans le repère inversé)
        arc_r = patches.Arc((x0_s, y0_s), width=50, height=50, angle=0, theta1=90 - theta2_deg, theta2=90, 
                            color="#f1f5f9", lw=1.5, zorder=5)
        ax.add_patch(arc_r)
        
        # Positionnement du texte 'r' (déjà correct, conservé tel quel)
        x_text_r = x0_s + 35 * math.sin(theta2_rad / 2)
        y_text_r = y0_s + 35 * math.cos(theta2_rad / 2)
        ax.text(x_text_r, y_text_r, "r", color="#f1f5f9", fontsize=11, fontweight="bold", ha="center", va="center")
    else:
        # En cas de Réflexion totale interne
        x_refl = x0_s + longueur_rayon * math.sin(theta1_rad)
        y_refl = y0_s - longueur_rayon * math.cos(theta1_rad)
        ax.plot([x0_s, x_refl], [y0_s, y_refl], color=couleur_laser, lw=2, linestyle=":", zorder=4)

    return fig

def dessiner_graphique_sinus_matplotlib():
    """Genere le graphique cartesien sin(r) = f(sin(i)) avec mise a jour de l'historique.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1.1)

    # Affichage de la grille de cours millimetree stable
    ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)

    # Titres et axes
    ax.set_xlabel("sin(i)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_ylabel("sin(r)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_title(" Releves sin(r) = f(sin(i))", color="#38bdf8", fontsize=8, style="italic")

    # Superposition permanente des points memorises (Croix vertes d'origine)
    m_sin_i = st.session_state.get("mesures_sin_i", [])
    m_sin_r = st.session_state.get("mesures_sin_r", [])
    
    if m_sin_i:
        ax.scatter(m_sin_i, m_sin_r, color="#10b981", marker="x", s=50, lw=2, label="Points mesures", zorder=5)
        ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="white", fontsize=7, loc="upper left")

    return fig

def afficher_questions_refraction_hist(verrouille=False):
    col_g, col_d = st.columns(2)

    questions_hist_ref = [
        ("qh1", "Quel savant grec de l'Antiquité a dressé les premières tables d'angles de réfraction entre l'air, l'eau et le verre ?", ["Claude Ptolémée", "Galilée", "Isaac Newton", "Albert Einstein"], "Claude Ptolémée"),
        ("qh2", "Quelle erreur mathématique Claude Ptolémée a-t-il commise dans son traité d'optique ?", ["Il pensait que l'angle réfracté était proportionnel à l'angle incident", "Il pensait que la lumière ne traversait pas l'eau", "Il croyait que le verre avait un indice négatif", "Il confondait réfraction et magnétisme"], "Il pensait que l'angle réfracté était proportionnel à l'angle incident"),
        ("qh3", "Quel savant de Bagdad a découvert dès l'an 984 la loi exacte des sinus de la réfraction ?", ["Ibn Sahl", "Archimède", "Pythagore", "Léonard de Vinci"], "Ibn Sahl"),
        ("qh4", "Pour quelle application pratique Ibn Sahl a-t-il utilisé sa découverte de la loi de la réfraction ?", ["La taille de lentilles convergentes (instruments ardents)", "La fabrication de fibres optiques", "Le réglage des phares automobiles", "La photographie numérique"], "La taille de lentilles convergentes (instruments ardents)"),
        ("qh5", "Dans quel ouvrage publié en 1637 René Descartes expose-t-il la loi moderne de la réfraction ?", ["La Dioptrique", "Les Principia", "L'Origine des espèces", "Le Dialogue sur les deux grands systèmes"], "La Dioptrique"),
        ("qh6", "Pourquoi la loi de la réfraction porte-t-elle le double nom de « Snell-Descartes » ?", ["Snell l'a découverte en 1621 sans la publier et Descartes l'a publiée en 1637", "Ils étaient frères jumeaux", "Ils ont écrit un livre ensemble à Paris", "Snell a inventé le laser et Descartes le prisme"], "Snell l'a découverte en 1621 sans la publier et Descartes l'a publiée en 1637"),
        ("qh7", "Quelle fonction mathématique relie l'angle d'incidence i1 et l'angle de réfraction i2 dans la loi exacte ?", ["Le sinus (sin)", "La tangente (tan)", "Le logarithme (ln)", "La racine carrée"], "Le sinus (sin)"),
        ("qh8", "Quelle grandeur physique notée n caractérise chaque milieu transparent traversé par la lumière ?", ["L'indice de réfraction", "La résistance thermique", "La masse volumique", "La fréquence sonore"], "L'indice de réfraction"),
        ("qh9", "Quel phénomène se produit lorsque la lumière passe d'un milieu plus réfringent à un milieu moins réfringent au-delà de l'angle critique ?", ["La réflexion totale interne", "La diffraction circulaire", "L'absorption complète", "La polarisation linéaire"], "La réflexion totale interne"),
        ("qh10", "En quelle année René Descartes a-t-il publié sa formulation de la loi de la réfraction ?", ["1637", "1492", "1789", "1905"], "1637"),
    ]

    if "ordre_hist_ref" not in st.session_state:
        liste_qh = list(questions_hist_ref)
        random.shuffle(liste_qh)
        st.session_state.ordre_hist_ref = liste_qh

    trous_hist_ref = [
        ("1. La réfraction correspond à la ......... de la lumière au passage d'un dioptre.", ["Choisir...", "déviation", "disparition", "coloration", "accélération"], "déviation", "href_t1"),
        ("2. Dans l'Antiquité, Claude ......... a mesuré les premiers tableaux d'angles.", ["Choisir...", "Ptolémée", "Platon", "Socrate", "Homère"], "Ptolémée", "href_t2"),
        ("3. En 984, le savant ......... découvre la loi géométrique des sinus.", ["Choisir...", "Ibn Sahl", "Newton", "Kepler", "Copernic"], "Ibn Sahl", "href_t3"),
        ("4. En 1621, l'astronome néerlandais Willebrord ......... établit le rapport constant.", ["Choisir...", "Snell", "Huygens", "Foucault", "Fresnel"], "Snell", "href_t4"),
        ("5. En 1637, René ......... publie la formule moderne dans La Dioptrique.", ["Choisir...", "Descartes", "Pascal", "Fermat", "Lavoisier"], "Descartes", "href_t5"),
        ("6. La loi relie les ......... des angles d'incidence et de réfraction.", ["Choisir...", "sinus", "cosinus", "tangentes", "carrés"], "sinus", "href_t6"),
        ("7. Chaque milieu transparent est défini par son ......... de réfraction n.", ["Choisir...", "indice", "poids", "volume", "rayon"], "indice", "href_t7"),
        ("8. La formule s'écrit n1 × sin(i1) = n2 × .........(i2).", ["Choisir...", "sin", "cos", "tan", "log"], "sin", "href_t8"),
        ("9. Dans le vide et l'air, l'indice de réfraction vaut environ .........", ["Choisir...", "1.00", "1.50", "2.42", "0.50"], "1.00", "href_t9"),
        ("10. Lorsque la lumière entre dans l'eau (n=1,33), elle se ......... de la normale.", ["Choisir...", "rapproche", "éloigne", "détache", "retourne"], "rapproche", "href_t10"),
    ]

    with col_g:
        st.markdown("##### Quiz Historique Refraction - Optique 1 (10 pts)")
        for idx, (qid, qtxt, opts, _) in enumerate(st.session_state.ordre_hist_ref, 1):
            cq1, cq2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq1: st.write(f"{idx}. {qtxt}")
            with cq2: st.selectbox("", ["Choisir..."] + opts, key=f"col_g_quiz_opt1_{qid}", disabled=verrouille, label_visibility="collapsed")

    with col_d:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 1 (10 pts)")
        for enonce, choix, _, cle in trous_hist_ref:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce)
            with ct2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

    return st.session_state.ordre_hist_ref, trous_hist_ref

def afficher_questions_optique2(verrouille=False):
    col_g, col_d = st.columns(2)

    questions_opt2 = [
        ("qs1", "Quelle est l'expression mathématique exacte de la deuxième loi de Snell-Descartes ?", ["n1 · sin(i1) = n2 · sin(i2)", "n1 + i1 = n2 + i2", "sin(i1) / n1 = sin(i2) / n2", "n1 · cos(i1) = n2 · cos(i2)"], "n1 · sin(i1) = n2 · sin(i2)"),
        ("qs2", "Dans quel plan se situent le rayon incident, la normale au dioptre et le rayon réfracté ?", ["Dans un même plan (plan d'incidence)", "Dans deux plans perpendiculaires", "Dans un plan parallèle à la surface", "Dans trois plans distincts"], "Dans un même plan (plan d'incidence)"),
        ("qs3", "Lorsque la lumière passe de l'air (n1 = 1,00) vers l'eau (n2 = 1,33), comment se comporte le rayon réfracté ?", ["Il se rapproche de la normale (i2 < i1)", "Il s'éloigne de la normale (i2 > i1)", "Il repart en arrière à 180°", "Il longe la surface à 90°"], "Il se rapproche de la normale (i2 < i1)"),
        ("qs4", "Si un rayon lumineux arrive perpendiculairement au dioptre (incidence normale i1 = 0°), que vaut l'angle de réfraction i2 ?", ["0° (le rayon n'est pas dévié)", "90°", "45°", "30°"], "0° (le rayon n'est pas dévié)"),
        ("qs5", "Que représente le coefficient directeur (la pente) de la droite obtenue en traçant sin(i1) en fonction de sin(i2) ?", ["Le rapport des indices n2 / n1", "La somme des indices n1 + n2", "La vitesse de la lumière c", "La longueur d'onde en nanomètres"], "Le rapport des indices n2 / n1"),
        ("qs6", "Que vaut l'indice de réfraction n de l'air ou du vide par convention ?", ["1,00", "1,33", "1,52", "2,42"], "1,00"),
        ("qs7", "Lorsque la lumière passe d'un milieu plus réfringent (verre n1 = 1,52) vers un milieu moins réfringent (air n2 = 1,00), le rayon :", ["S'éloigne de la normale (i2 > i1)", "Se rapproche de la normale (i2 < i1)", "Ne subit aucune déviation", "Devient ultraviolet"], "S'éloigne de la normale (i2 > i1)"),
        ("qs8", "Comment s'appelle la droite perpendiculaire à la surface de séparation au point d'incidence ?", ["La normale", "La tangente", "L'axe focal", "La diagonale"], "La normale"),
        ("qs9", "Quel nom donne-t-on à la surface séparant deux milieux transparents d'indices différents ?", ["Un dioptre", "Un prisme", "Un foyer", "Un réseau"], "Un dioptre"),
        ("qs10", "Si n1 = 1,00 et i1 = 30° dans l'air, et que i2 = 22° dans un liquide, l'indice n2 du liquide est environ égal à :", ["1,33 (Eau)", "1,00 (Air)", "2,42 (Diamant)", "0,75"], "1,33 (Eau)"),
    ]

    if "ordre_quiz_opt2" not in st.session_state:
        liste_q2 = list(questions_opt2)
        random.shuffle(liste_q2)
        st.session_state.ordre_quiz_opt2 = liste_q2

    trous_opt2 = [
        ("1. La surface qui sépare deux milieux transparents s'appelle un .........", ["Choisir...", "dioptre", "miroir", "foyer", "écran"], "dioptre", "opt2_t1"),
        ("2. Les angles i1 et i2 sont toujours mesurés par rapport à la .........", ["Choisir...", "normale", "surface", "horizontale", "source"], "normale", "opt2_t2"),
        ("3. La deuxième loi s'écrit n1 × sin(i1) = n2 × .........(i2).", ["Choisir...", "sin", "cos", "tan", "log"], "sin", "opt2_t3"),
        ("4. En incidence normale (i1 = 0°), le rayon n'est pas .........", ["Choisir...", "dévié", "visible", "transmis", "absorbé"], "dévié", "opt2_t4"),
        ("5. En passant de l'air dans l'eau, le rayon se ......... de la normale.", ["Choisir...", "rapproche", "éloigne", "détache", "retourne"], "rapproche", "opt2_t5"),
        ("6. En passant du verre dans l'air, le rayon s'......... de la normale.", ["Choisir...", "éloigne", "rapproche", "arrête", "inverse"], "éloigne", "opt2_t6"),
        ("7. L'indice de réfraction d'un milieu est toujours supérieur ou égal à .........", ["Choisir...", "1", "0", "2", "10"], "1", "opt2_t7"),
        ("8. Le graphique sin(i1) = f(sin(i2)) est une ......... passant par l'origine.", ["Choisir...", "droite", "parabole", "hyperbole", "sinusoïde"], "droite", "opt2_t8"),
        ("9. Le coefficient directeur de cette droite est égal à n2 / .........", ["Choisir...", "n1", "i1", "i2", "90"], "n1", "opt2_t9"),
        ("10. Le rayon incident, la normale et le rayon réfracté sont dans le même .........", ["Choisir...", "plan", "cercle", "cube", "angle"], "plan", "opt2_t10"),
    ]

    with col_g:
        st.markdown("##### Quiz Lois de Snell-Descartes - Optique 2 (10 pts)")
        for idx, (qid, qtxt, opts, _) in enumerate(st.session_state.ordre_quiz_opt2, 1):
            cq1, cq2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq1: st.write(f"{idx}. {qtxt}")
            with cq2: st.selectbox("", ["Choisir..."] + opts, key=f"col_g_quiz_opt2_{qid}", disabled=verrouille, label_visibility="collapsed")

    with col_d:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 2 (10 pts)")
        for enonce, choix, _, cle in trous_opt2:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce)
            with ct2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

    return st.session_state.ordre_quiz_opt2, trous_opt2



def afficher_questions_optique3(verrouille=False):
    col_g, col_d = st.columns(2)

    questions_opt3 = [
        ("qd1", "Combien de dioptres (surfaces de séparation) un rayon lumineux traverse-t-il au total dans une lame à faces parallèles ?", ["2 dioptres (entrée et sortie)", "1 seul dioptre", "4 dioptres", "Aucun dioptre"], "2 dioptres (entrée et sortie)"),
        ("qd2", "Lorsque le milieu d'entrée et le milieu de sortie sont identiques (ex : Air → Verre → Air), comment ressort le rayon émergent ?", ["Parallèle au rayon incident (s = i1)", "Perpendiculaire au rayon incident", "Réfléchi vers le haut à 180°", "Convergent vers un point unique"], "Parallèle au rayon incident (s = i1)"),
        ("qd3", "Comment appelle-t-on la distance perpendiculaire séparant le prolongement du rayon incident et le rayon émergent ?", ["Le décalage latéral (dx)", "La distance focale", "L'ouverture numérique", "La longueur d'onde"], "Le décalage latéral (dx)"),
        ("qd4", "Que se passe-t-il sur le décalage latéral dx si l'on augmente l'épaisseur de la lame en verre ?", ["Le décalage latéral dx augmente proportionnellement", "Le décalage latéral dx devient nul", "Le décalage latéral dx diminue", "Le rayon est bloqué dans le verre"], "Le décalage latéral dx augmente proportionnellement"),
        ("qd5", "Si l'angle d'incidence d'entrée i1 vaut 0° (incidence normale perpendiculaire à la lame), que vaut le décalage latéral dx ?", ["0 mm (aucune déviation ni décalage)", "45 mm", "100 mm", "Infini"], "0 mm (aucune déviation ni décalage)"),
        ("qd6", "Lors du passage de l'air (n1 = 1,00) vers le verre (n2 = 1,52), comment évolue l'angle de réfraction r1 par rapport à i1 ?", ["r1 est inférieur à i1 (le rayon se rapproche de la normale)", "r1 est supérieur à i1", "r1 est toujours égal à 90°", "r1 est négatif"], "r1 est inférieur à i1 (le rayon se rapproche de la normale)"),
        ("qd7", "Quelle relation lie l'angle de réfraction au premier dioptre (r1) et l'angle d'incidence sur le second dioptre (i2) dans une lame à faces parallèles ?", ["Ils sont égaux (r1 = i2) car les deux normales sont parallèles", "Leur somme vaut 180°", "i2 vaut le double de r1", "i2 est toujours nul"], "Ils sont égaux (r1 = i2) car les deux normales sont parallèles"),
        ("qd8", "Si le milieu de sortie n3 est différent du milieu d'entrée n1 (ex : Air → Verre → Eau), l'angle de sortie s est-il égal à i1 ?", ["Non, car n3 est différent de n1 (s ≠ i1)", "Oui, toujours", "Oui, si le verre est épais", "Non, le rayon s'arrête dans l'eau"], "Non, car n3 est différent de n1 (s ≠ i1)"),
        ("qd9", "Dans la simulation de la double réfraction, que se produit-il au second dioptre si n2 > n3 et que l'angle r1 dépasse l'angle critique ?", ["Une réflexion totale interne sur la face inférieure de la lame", "Une accélération du laser", "Une extinction complète du faisceau", "Une dispersion en arc-en-ciel uniquement"], "Une réflexion totale interne sur la face inférieure de la lame"),
        ("qd10", "Quelle loi physique permet de calculer successivement r1 puis l'angle d'émergence s ?", ["La deuxième loi de Snell-Descartes appliquée deux fois", "La loi d'Ohm", "Le principe d'Archimède", "La loi de Boyle-Mariotte"], "La deuxième loi de Snell-Descartes appliquée deux fois"),
    ]

    if "ordre_quiz_opt3" not in st.session_state:
        liste_q3 = list(questions_opt3)
        random.shuffle(liste_q3)
        st.session_state.ordre_quiz_opt3 = liste_q3

    trous_opt3 = [
        ("1. Une lame à faces parallèles comporte ......... dioptres successifs.", ["Choisir...", "deux", "trois", "quatre", "un"], "deux", "opt3_t1"),
        ("2. À l'entrée dans le verre (n2 > n1), le rayon se ......... de la normale.", ["Choisir...", "rapproche", "éloigne", "détache", "retourne"], "rapproche", "opt3_t2"),
        ("3. Les deux normales aux faces parallèles sont ......... entre elles.", ["Choisir...", "parallèles", "perpendiculaires", "sécantes", "confondues"], "parallèles", "opt3_t3"),
        ("4. Si n3 = n1, l'angle d'émergence s est ......... à l'angle d'incidence i1.", ["Choisir...", "égal", "supérieur", "inférieur", "opposé"], "égal", "opt3_t4"),
        ("5. Le rayon émergent sort donc ......... au rayon incident d'entrée.", ["Choisir...", "parallèle", "perpendiculaire", "inversé", "vertical"], "parallèle", "opt3_t5"),
        ("6. La translation subie par le faisceau s'appelle le ......... latéral dx.", ["Choisir...", "décalage", "foyer", "prisme", "sinus"], "décalage", "opt3_t6"),
        ("7. Plus la lame est épaisse, plus le décalage dx est .........", ["Choisir...", "grand", "petit", "nul", "négatif"], "grand", "opt3_t7"),
        ("8. En incidence normale (i1 = 0°), le décalage latéral vaut ......... mm.", ["Choisir...", "0", "45", "90", "100"], "0", "opt3_t8"),
        ("9. Si n3 ≠ n1, le rayon émergent n'est plus ......... au rayon incident.", ["Choisir...", "parallèle", "visible", "réfracté", "monochromatique"], "parallèle", "opt3_t9"),
        ("10. Chaque traversée obéit à la loi de .........-Descartes.", ["Choisir...", "Snell", "Newton", "Joule", "Pascal"], "Snell", "opt3_t10"),
    ]

    with col_g:
        st.markdown("##### Quiz Double Réfraction - Optique 3 (10 pts)")
        for idx, (qid, qtxt, opts, _) in enumerate(st.session_state.ordre_quiz_opt3, 1):
            cq1, cq2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq1: st.write(f"{idx}. {qtxt}")
            with cq2: st.selectbox("", ["Choisir..."] + opts, key=f"col_g_quiz_opt3_{qid}", disabled=verrouille, label_visibility="collapsed")

    with col_d:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 3 (10 pts)")
        for enonce, choix, _, cle in trous_opt3:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce)
            with ct2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

    return st.session_state.ordre_quiz_opt3, trous_opt3


def afficher_questions_optique4(verrouille=False):
    col_g, col_d = st.columns(2)

    questions_opt4 = [
        ("qf1", "Quelle condition stricte sur les indices permet d'observer une réflexion totale interne ?", ["n1 > n2 (milieu incident plus réfringent)", "n1 < n2", "n1 = n2", "n2 > 2,50"], "n1 > n2 (milieu incident plus réfringent)"),
        ("qf2", "Quelle formule permet de calculer le sinus de l'angle critique (angle limite ic) ?", ["sin(ic) = n2 / n1", "sin(ic) = n1 / n2", "sin(ic) = n1 · n2", "sin(ic) = n1 - n2"], "sin(ic) = n2 / n1"),
        ("qf3", "Que vaut l'angle de réfraction théorique lorsque l'angle d'incidence est exactement égal à l'angle critique ic ?", ["90° (rayon réfracté rasant le dioptre)", "0°", "45°", "180°"], "90° (rayon réfracté rasant le dioptre)"),
        ("qf4", "Que se passe-t-il lorsque l'angle d'incidence i dépasse l'angle critique ic (i > ic) ?", ["100 % de la lumière est réfléchie dans le milieu 1 (réflexion totale)", "La lumière est absorbée par le verre", "La lumière traverse en ligne droite", "La fréquence du laser double"], "100 % de la lumière est réfléchie dans le milieu 1 (réflexion totale)"),
        ("qf5", "Dans une fibre optique à saut d'indice, quelle partie possède l'indice de réfraction le plus élevé ?", ["Le cœur (n1)", "La gaine optique (n2)", "L'air ambiant (n = 1,00)", "La gaine plastique de protection"], "Le cœur (n1)"),
        ("qf6", "Que vaut l'angle critique à l'interface verre (n1 = 1,50) / air (n2 = 1,00) ?", ["Environ 41,8°", "Environ 90,0°", "Environ 12,5°", "Environ 75,0°"], "Environ 41,8°"),
        ("qf7", "Comment appelle-t-on le cône d'entrée maximal permettant à un rayon extérieur d'être guidé dans la fibre ?", ["Le cône d'acceptance (lié à l'ouverture numérique ON)", "Le cône de dispersion", "L'angle de Brewster", "L'angle mort"], "Le cône d'acceptance (lié à l'ouverture numérique ON)"),
        ("qf8", "Quelle est la formule de l'Ouverture Numérique (ON) d'une fibre optique ?", ["ON = √(n1² - n2²)", "ON = n1 + n2", "ON = n1 / n2", "ON = 2 · n1"], "ON = √(n1² - n2²)"),
        ("qf9", "Si l'angle d'injection externe i1 dans la fibre est trop grand (supérieur à i_max), que devient le rayon dans la fibre ?", ["Il se réfracte dans la gaine et est perdu", "Il rebondit deux fois plus vite", "Il fait demi-tour vers le laser", "Il devient invisible"], "Il se réfracte dans la gaine et est perdu"),
        ("qf10", "Pourquoi les fibres optiques sont-elles privilégiées pour les télécommunications très haut débit ?", ["Elles transmettent la lumière sur de très longues distances sans perte ni interférence électromagnétique", "Elles fonctionnent sans aucune source lumineuse", "Elles coûtent moins cher que le fil de fer", "Elles transportent du courant haute tension"], "Elles transmettent la lumière sur de très longues distances sans perte ni interférence électromagnétique"),
    ]

    if "ordre_quiz_opt4" not in st.session_state:
        liste_q4 = list(questions_opt4)
        random.shuffle(liste_q4)
        st.session_state.ordre_quiz_opt4 = liste_q4

    trous_opt4 = [
        ("1. La réflexion totale exige que l'indice n1 soit ......... à l'indice n2.", ["Choisir...", "supérieur", "inférieur", "égal", "nul"], "supérieur", "opt4_t1"),
        ("2. L'angle limite ic vérifie la relation sin(ic) = n2 / .........", ["Choisir...", "n1", "90", "1", "c"], "n1", "opt4_t2"),
        ("3. Lorsque i > ic, le rayon lumineux est intégralement .........", ["Choisir...", "réfléchi", "réfracté", "absorbé", "diffracté"], "réfléchi", "opt4_t3"),
        ("4. Une fibre optique est composée d'un ......... entouré d'une gaine.", ["Choisir...", "cœur", "prisme", "miroir", "écran"], "cœur", "opt4_t4"),
        ("5. L'indice du cœur n1 est toujours supérieur à celui de la ......... n2.", ["Choisir...", "gaine", "lentille", "source", "table"], "gaine", "opt4_t5"),
        ("6. Le signal lumineux progresse dans la fibre par ......... totales successives.", ["Choisir...", "réflexions", "réfractions", "dispersions", "absorptions"], "réflexions", "opt4_t6"),
        ("7. L'angle maximal d'injection à l'entrée définit le cône d'.........", ["Choisir...", "acceptance", "incidence nulle", "ombre", "réfraction"], "acceptance", "opt4_t7"),
        ("8. L'ouverture ......... ON mesure la capacité de collecte lumineuse de la fibre.", ["Choisir...", "numérique", "thermique", "magnétique", "acoustique"], "numérique", "opt4_t8"),
        ("9. Si on courbe trop la fibre, le rayon s'échappe par ......... dans la gaine.", ["Choisir...", "réfraction", "combustion", "polarisation", "convection"], "réfraction", "opt4_t9"),
        ("10. Au dioptre verre/air (n=1,50), l'angle critique vaut environ ......... degrés.", ["Choisir...", "41.8", "90.0", "15.0", "75.0"], "41.8", "opt4_t10"),
    ]

    with col_g:
        st.markdown("##### Quiz Réflexion Totale & Fibre Optique - Optique 4 (10 pts)")
        for idx, (qid, qtxt, opts, _) in enumerate(st.session_state.ordre_quiz_opt4, 1):
            cq1, cq2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq1: st.write(f"{idx}. {qtxt}")
            with cq2: st.selectbox("", ["Choisir..."] + opts, key=f"col_g_quiz_opt4_{qid}", disabled=verrouille, label_visibility="collapsed")

    with col_d:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 4 (10 pts)")
        for enonce, choix, _, cle in trous_opt4:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce)
            with ct2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

    return st.session_state.ordre_quiz_opt4, trous_opt4






def afficher_questions_optique5(verrouille=False):
    col_double_quiz_opt5, col_double_trous_opt5 = st.columns(2)

    cas_actif = st.session_state.get("app_maint_choisie", "refractometre")

    with col_double_quiz_opt5:
        st.markdown("##### Quiz d'application maintenance (10 questions) - Optique 5 (10 pts)")

        cle_session_ordre = f"ordre_questions_opt5_{cas_actif}"
        if cle_session_ordre not in st.session_state:
            if cas_actif == "refractometre":
                base_questions = [
                    ("m1", "Quelle grandeur optique le réfractomètre d'atelier mesure-t-il pour connaître la concentration d'un fluide ?"),
                    ("m2", "Lorsque la concentration en huile soluble augmente dans l'eau, l'indice n devient plus :"),
                    ("m3", "Quelle est l'unité affichée sur l'échelle interne d'un réfractomètre de maintenance ?"),
                    ("m4", "Avec quel liquide étalonne-t-on le zéro (n = 1,333) d'un réfractomètre avant une mesure ?"),
                    ("m5", "Un fluide d'usinage trop pauvre en huile (indice proche de 1,33) entraîne sur les pièces une :"),
                    ("m6", "Le volet translucide rabattu sur le prisme permet d'étaler le liquide en film :"),
                    ("m7", "La ligne de séparation claire/sombre dans l'oculaire correspond au phénomène de :"),
                    ("m8", "Quel paramètre physique doit être compensé (fonction ATC) pour éviter une erreur de lecture ?"),
                    ("m9", "Dans un circuit de refroidissement, le réfractomètre permet de contrôler la protection contre le :"),
                    ("m10", "Pour que l'appareil fonctionne, l'indice du prisme doit être par rapport au liquide :")
                ]
            elif cas_actif == "voyant_niveau":
                base_questions = [
                    ("v1", "Lorsque le réservoir hydraulique est plein d'huile, le voyant optique conique apparaît :"),
                    ("v2", "Lorsque le niveau d'huile est trop bas (contact avec l'air), le voyant apparaît :"),
                    ("v3", "L'aspect brillant à sec est dû au phénomène optique de :"),
                    ("v4", "L'angle au sommet du prisme conique d'un voyant de niveau vaut généralement :"),
                    ("v5", "Lorsque l'huile (n = 1,46) recouvre le cône en verre (n = 1,50), la lumière traverse par :"),
                    ("v6", "L'angle critique à l'interface verre/air (41,8°) est par rapport aux 45° du cône :"),
                    ("v7", "L'angle critique à l'interface verre/huile (76,7°) est par rapport aux 45° du cône :"),
                    ("v8", "L'avantage majeur du voyant optique par rapport à un flotteur est l'absence de pièce :"),
                    ("v9", "Si le voyant passe au brillant argenté en production, le technicien doit faire l' :"),
                    ("v10", "Le fonctionnement de ce capteur de niveau repose sur la loi de :")
                ]
            else: # endoscope_fibre
                base_questions = [
                    ("e1", "Quel phénomène permet de guider la lumière dans un endoscope à fibres optiques courbé ?"),
                    ("e2", "Pour confiner la lumière, l'indice du cœur (n1) doit être par rapport à la gaine (n2) :"),
                    ("e3", "Si le technicien plie trop fortement la sonde, l'angle d'incidence devient inférieur à l'angle :"),
                    ("e4", "Lorsque l'angle limite n'est plus respecté, la lumière s'échappe dans la :"),
                    ("e5", "L'angle maximal d'entrée dans la fibre optique définit le cône d' :"),
                    ("e6", "L'inspection interne d'une turbine sans démontage est un contrôle non :"),
                    ("e7", "Un endoscope industriel comporte un faisceau pour l'image et un faisceau pour l' :"),
                    ("e8", "Sur l'écran de contrôle, une microfibre brisée apparaît sous la forme d'un point :"),
                    ("e9", "La capacité d'une fibre à capter la lumière se mesure par son Ouverture :"),
                    ("e10", "L'endoscopie optique est systématique en maintenance aéronautique pour contrôler les :")
                ]
            random.shuffle(base_questions)
            st.session_state[cle_session_ordre] = base_questions

        dict_quiz_opt5 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state[cle_session_ordre], 1):
            cle_qo5 = f"col_g_quiz_opt5_{cas_actif}_{q_id}"
            cle_opts_unique = f"opts_opt5_shuffled_{cas_actif}_{q_id}"

            if cle_opts_unique not in st.session_state:
                if cas_actif == "refractometre":
                    if q_id == "m1": copie_opts = ["L'indice de réfraction n", "La résistance électrique", "La pression hydraulique", "La viscosité dynamique"]
                    elif q_id == "m2": copie_opts = ["Élevé", "Faible", "Nul", "Négatif"]
                    elif q_id == "m3": copie_opts = ["Degré Brix (%)", "Décibel (dB)", "Newton (N)", "Hertz (Hz)"]
                    elif q_id == "m4": copie_opts = ["Eau distillée", "Huile moteur", "Acétone pur", "Solvant chloré"]
                    elif q_id == "m5": copie_opts = ["Corrosion", "Surpression", "Surtension", "Aimantation"]
                    elif q_id == "m6": copie_opts = ["Mince uniforme", "Épais et trouble", "Solide", "Gazeux"]
                    elif q_id == "m7": copie_opts = ["Réfraction limite", "Diffraction", "Polarisation", "Absorption totale"]
                    elif q_id == "m8": copie_opts = ["La température", "L'altitude", "La pression atmosphérique", "La couleur des murs"]
                    elif q_id == "m9": copie_opts = ["Gel", "Feu", "Bruit", "Calcaire"]
                    elif q_id == "m10": copie_opts = ["Supérieur", "Inférieur", "Égal à 1", "Nul"]
                elif cas_actif == "voyant_niveau":
                    if q_id == "v1": copie_opts = ["Noir / sombre", "Brillant / argenté", "Rouge clignotant", "Bleu fluo"]
                    elif q_id == "v2": copie_opts = ["Brillant / argenté", "Totalement noir", "Vert opaque", "Invisible"]
                    elif q_id == "v3": copie_opts = ["Réflexion totale interne", "Réfraction diffuse", "Dispersion", "Absorption calorifique"]
                    elif q_id == "v4": copie_opts = ["90°", "180°", "20°", "150°"]
                    elif q_id == "v5": copie_opts = ["Réfraction dans l'huile", "Réflexion métallique", "Diffraction", "Convection"]
                    elif q_id == "v6": copie_opts = ["Inférieur", "Supérieur", "Égal", "Nul"]
                    elif q_id == "v7": copie_opts = ["Supérieur", "Inférieur", "Égal", "Nul"]
                    elif q_id == "v8": copie_opts = ["Mobile mécanique", "Transparente", "Filetée", "Étanche"]
                    elif q_id == "v9": copie_opts = ["Appoint d'huile", "Arrêt définitif", "Équilibrage", "Usinage"]
                    elif q_id == "v10": copie_opts = ["Snell-Descartes", "Ohm", "Hooke", "Joule"]
                else: # endoscope_fibre
                    if q_id == "e1": copie_opts = ["Réflexion totale interne", "Réfraction externe", "Conduction électrique", "Convection"]
                    elif q_id == "e2": copie_opts = ["Supérieur", "Inférieur", "Égal", "Nul"]
                    elif q_id == "e3": copie_opts = ["Critique (limite)", "Droit", "Plat", "Nul"]
                    elif q_id == "e4": copie_opts = ["Gaine", "Batterie", "Poignée", "Lentille"]
                    elif q_id == "e5": copie_opts = ["Acceptance", "Observation", "Incidences nulles", "Dispersion"]
                    elif q_id == "e6": copie_opts = ["Destructif", "Visuel", "Électrique", "Thermique"]
                    elif q_id == "e7": copie_opts = ["Éclairage", "Refroidissement", "Graissage", "Freinage"]
                    elif q_id == "e8": copie_opts = ["Noir fixe", "Vert", "Clignotant", "Jaune"]
                    elif q_id == "e9": copie_opts = ["Numérique", "Thermique", "Magnétique", "Acoustique"]
                    elif q_id == "e10": copie_opts = ["Aubes de turbines", "Pneus", "Batteries", "Carrosseries"]

                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts

            val_p = st.session_state.get(cle_qo5, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0

            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt5[f"{q_id}_opt5"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo5, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt5:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 5 (10 pts)")

        if cas_actif == "refractometre":
            phrases = [
                ("1. Le réfractomètre mesure l'indice de ......... d'un fluide industriel.", ["Choisir...", "réfraction", "viscosité", "pression", "densité"], "t1_opt5"),
                ("2. L'étalonnage à zéro s'effectue avec de l'eau ......... (n = 1,333).", ["Choisir...", "distillée", "salée", "savonneuse", "glacée"], "t2_opt5"),
                ("3. La concentration se lit directement en degrés ......... sur l'échelle.", ["Choisir...", "Brix", "Celsius", "Kelvin", "Radian"], "t3_opt5"),
                ("4. Plus le liquide est concentré, plus son indice n est .........", ["Choisir...", "élevé", "faible", "nul", "négatif"], "t4_opt5"),
                ("5. Le prisme doit posséder un indice ......... à celui du liquide.", ["Choisir...", "supérieur", "inférieur", "égal", "nul"], "t5_opt5"),
                ("6. La frontière claire/sombre correspond à l'angle .........", ["Choisir...", "limite", "droit", "plat", "nul"], "t6_opt5"),
                ("7. La fonction ATC compense les variations de .........", ["Choisir...", "température", "lumière", "pression", "vitesse"], "t7_opt5"),
                ("8. Dans un moteur, on vérifie la concentration en .........", ["Choisir...", "glycol", "sable", "mercure", "soufre"], "t8_opt5"),
                ("9. Un fluide d'usinage trop dilué provoque la ......... des pièces.", ["Choisir...", "corrosion", "lubrification", "peinture", "soudure"], "t9_opt5"),
                ("10. Le volet étale la goutte en un film ......... uniforme.", ["Choisir...", "mince", "épais", "solide", "opaque"], "t10_opt5"),
            ]
        elif cas_actif == "voyant_niveau":
            phrases = [
                ("1. Le voyant optique utilise un prisme de forme ......... à 90°.", ["Choisir...", "conique", "sphérique", "cubique", "cylindrique"], "t1_opt5"),
                ("2. Au contact de l'air (n=1,00), la lumière subit une ......... totale.", ["Choisir...", "réflexion", "réfraction", "absorption", "diffusion"], "t2_opt5"),
                ("3. Lorsque le niveau est bas, le voyant apparaît ......... à l'opérateur.", ["Choisir...", "brillant", "noir", "rouge", "opaque"], "t3_opt5"),
                ("4. Lorsque l'huile (n=1,46) recouvre le cône, la lumière est ......... dans le fluide.", ["Choisir...", "réfractée", "réfléchie", "bloquée", "polarisée"], "t4_opt5"),
                ("5. Un voyant immergé dans l'huile apparaît ......... (niveau conforme).", ["Choisir...", "noir", "argenté", "jaune", "lumineux"], "t5_opt5"),
                ("6. L'angle d'incidence sur les faces du cône vaut ......... degrés.", ["Choisir...", "45", "10", "85", "0"], "t6_opt5"),
                ("7. L'indice de l'huile est très ......... de celui du verre (1,50).", ["Choisir...", "proche", "éloigné", "inférieur à 1", "nul"], "t7_opt5"),
                ("8. Ce capteur optique ne possède aucune pièce ......... mécanique.", ["Choisir...", "mobile", "transparente", "filetée", "étanche"], "t8_opt5"),
                ("9. Si le voyant devient brillant, il faut faire l'......... d'huile.", ["Choisir...", "appoint", "arrêt définitif", "équilibrage", "usinage"], "t9_opt5"),
                ("10. Le phénomène obéit à la loi de .........-Descartes.", ["Choisir...", "Snell", "Newton", "Joule", "Pascal"], "t10_opt5"),
            ]
        else: # endoscope_fibre
            phrases = [
                ("1. L'endoscope guide la lumière grâce à des ......... optiques souples.", ["Choisir...", "fibres", "tiges", "barres", "câbles"], "t1_opt5"),
                ("2. L'indice du cœur n1 est strictement ......... à celui de la gaine n2.", ["Choisir...", "supérieur", "inférieur", "égal", "nul"], "t2_opt5"),
                ("3. Le guidage repose sur la ......... totale interne.", ["Choisir...", "réflexion", "réfraction", "dispersion", "absorption"], "t3_opt5"),
                ("4. Inspecter l'intérieur d'une turbine sans démonter est un contrôle non .........", ["Choisir...", "destructif", "visuel", "électrique", "thermique"], "t4_opt5"),
                ("5. Si on plie trop la sonde, l'angle devient inférieur à l'angle .........", ["Choisir...", "critique", "plat", "droit", "nul"], "t5_opt5"),
                ("6. La lumière s'échappe alors dans la ......... et est perdue.", ["Choisir...", "gaine", "lentille", "batterie", "poignée"], "t6_opt5"),
                ("7. L'ouverture ......... caractérise la capacité de collecte lumineuse.", ["Choisir...", "numérique", "thermique", "magnétique", "acoustique"], "t7_opt5"),
                ("8. Une fibre cassée apparaît comme un point ......... sur l'écran.", ["Choisir...", "noir", "vert", "clignotant", "jaune"], "t8_opt5"),
                ("9. L'endoscope est très utilisé pour contrôler les aubes de .........", ["Choisir...", "turbines", "pneus", "batteries", "freins"], "t9_opt5"),
                ("10. Le faisceau d'éclairage transmet une lumière ......... sans chauffer la zone.", ["Choisir...", "froide", "ultraviolette", "laser", "infrarouge"], "t10_opt5"),
            ]

        dict_trous_opt5 = {}
        for enonce_t, opts_t, cle_t in phrases:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce_t)
            with ct2: dict_trous_opt5[cle_t] = st.selectbox("", opts_t, key=f"opt5_{cle_t}", disabled=verrouille, label_visibility="collapsed")

    return dict_quiz_opt5, dict_trous_opt5

def afficher_questions_optique6(verrouille=False):
    col_double_quiz_opt6, col_double_trous_opt6 = st.columns(2)

    cas_actif = st.session_state.get("app_tp_choisie", "nivellement_atm")

    with col_double_quiz_opt6:
        st.markdown("##### Quiz d'application Travaux Publics (10 questions) - Optique 6 (10 pts)")

        cle_session_ordre = f"ordre_questions_opt6_{cas_actif}"
        if cle_session_ordre not in st.session_state:
            if cas_actif == "nivellement_atm":
                base_questions = [
                    ("tp1", "Lors d'un nivellement optique longue portée sur un chantier routier, la chaleur du sol provoque une :"),
                    ("tp2", "L'air surchauffé juste au-dessus du bitume ou de la terre possède un indice de réfraction plus :"),
                    ("tp3", "En traversant des couches d'air de températures différentes, le rayon lumineux de visée devient :"),
                    ("tp4", "Si le rayon lumineux se courbe vers le haut près du sol chaud, la lecture sur la mire graduée est :"),
                    ("tp5", "Pour limiter l'erreur due à la réfraction atmosphérique, le chef de chantier place le niveau optique à :"),
                    ("tp6", "À quelle période de la journée la réfraction atmosphérique perturbe-t-elle le plus les visées laser TP ?"),
                    ("tp7", "Pourquoi conseille-t-on d'éviter de viser à moins de 50 cm du sol lors d'un terrassement de précision ?"),
                    ("tp8", "L'indice de réfraction de l'air dépend directement de sa température et de sa :"),
                    ("tp9", "Dans un milieu parfaitement homogène (température uniforme), la lumière se propage en ligne :"),
                    ("tp10", "Quelle formule fondamentale régit la déviation progressive du faisceau entre deux couches d'air ?")
                ]
            elif cas_actif == "adjuvant_beton":
                base_questions = [
                    ("ad1", "Sur un chantier en hiver, quel appareil optique permet de contrôler la concentration d'antigel du béton ?"),
                    ("ad2", "Le réfractomètre de chantier mesure la concentration d'un adjuvant liquide grâce à son :"),
                    ("ad3", "Lorsque l'on ajoute davantage d'adjuvant dans l'eau de gâchage, l'indice de réfraction n :"),
                    ("ad4", "La séparation entre la zone bleue et la zone blanche dans l'oculaire correspond à l'angle :"),
                    ("ad5", "Quel liquide utilise-t-on sur le chantier pour vérifier le zéro du réfractomètre avant essai ?"),
                    ("ad6", "Quelle unité graduée lit-on directement sur l'échelle optique d'un réfractomètre TP ?"),
                    ("ad7", "Pour mesurer l'indice d'une émulsion de bitume ou d'un antigel, il suffit de déposer sur le prisme :"),
                    ("ad8", "L'indice du prisme en verre de l'appareil doit être par rapport à celui de l'adjuvant :"),
                    ("ad9", "Un mauvais dosage en antigel béton (indice n trop bas) expose l'ouvrage frais au risque de :"),
                    ("ad10", "La compensation automatique de température (ATC) corrige l'influence de la chaleur sur l' :")
                ]
            else: # camera_reseau
                base_questions = [
                    ("ca1", "Pour inspecter une canalisation d'assainissement enterrée avant réception, on utilise une caméra à :"),
                    ("ca2", "La lumière d'éclairage est transportée jusqu'à la tête de caméra grâce au phénomène de :"),
                    ("ca3", "Dans une fibre optique de chantier, l'indice du cœur (n1) doit être par rapport à la gaine (n2) :"),
                    ("ca4", "Si la gaine de poussée est pliée dans un coude à angle droit trop serré, la lumière va :"),
                    ("ca5", "L'objectif grand angle de la caméra d'inspection dévie les rayons lumineux par :"),
                    ("ca6", "Lorsque la tête de caméra plonge dans une flaque d'eau au fond du tuyau, l'angle de vue :"),
                    ("ca7", "Pourquoi le champ de vision sous l'eau (n = 1,33) est-il plus étroit que dans l'air (n = 1,00) ?"),
                    ("ca8", "La loi qui permet de calculer la déviation des rayons à l'entrée de la lentille est la loi de :"),
                    ("ca9", "Quel défaut d'étanchéité sur un collecteur TP est immédiatement repéré par l'inspection optique ?"),
                    ("ca10", "La condition limite de guidage dans la fibre impose que l'angle d'incidence soit supérieur à l'angle :")
                ]
            random.shuffle(base_questions)
            st.session_state[cle_session_ordre] = base_questions

        dict_quiz_opt6 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state[cle_session_ordre], 1):
            cle_qo6 = f"col_g_quiz_opt6_{cas_actif}_{q_id}"
            cle_opts_unique = f"opts_opt6_shuffled_{cas_actif}_{q_id}"

            if cle_opts_unique not in st.session_state:
                if cas_actif == "nivellement_atm":
                    if q_id == "tp1": copie_opts = ["Réfraction atmosphérique", "Diffraction magnétique", "Polarisation circulaire", "Absorption totale"]
                    elif q_id == "tp2": copie_opts = ["Faible", "Élevé", "Supérieur à celui du verre", "Négatif"]
                    elif q_id == "tp3": copie_opts = ["Curviligne (courbe)", "Strictement verticale", "Brisée à 90°", "Invisible"]
                    elif q_id == "tp4": copie_opts = ["Faussée (trop basse sur la mire)", "Parfaitement exacte", "Multipliée par deux", "Toujours nulle"]
                    elif q_id == "tp5": copie_opts = ["Égale distance des deux mires", "Collé contre le sol chaud", "À 500 mètres d'un seul côté", "Dans une tranchée fermée"]
                    elif q_id == "tp6": copie_opts = ["En plein après-midi sous fort soleil", "À minuit par temps couvert", "Sous une pluie fine uniforme", "À l'aube sans vent"]
                    elif q_id == "tp7": copie_opts = ["Le gradient thermique y est maximal", "Le laser ne fonctionne pas près du sol", "La gravité dévie le laser", "La mire n'est pas graduée en bas"]
                    elif q_id == "tp8": copie_opts = ["Pression (densité)", "Couleur", "Vitesse du vent uniquement", "Humidité électrique"]
                    elif q_id == "tp9": copie_opts = ["Droite", "Courbe", "Hélicoïdale", "Brisée"]
                    elif q_id == "tp10": copie_opts = ["Snell-Descartes", "Archimède", "Coulomb", "Bernoulli"]
                elif cas_actif == "adjuvant_beton":
                    if q_id == "ad1": copie_opts = ["Un réfractomètre optique", "Un théodolite", "Un mètre ruban", "Un sonomètre"]
                    elif q_id == "ad2": copie_opts = ["Indice de réfraction n", "Poids volumique en tonnes", "Potentiel électrique", "Point d'ébullition"]
                    elif q_id == "ad3": copie_opts = ["Augmente", "Diminue sous 1,00", "Reste bloqué à 0", "Devient négatif"]
                    elif q_id == "ad4": copie_opts = ["Critique (limite)", "Droit (90°)", "Plat (180°)", "Nul (0°)"]
                    elif q_id == "ad5": copie_opts = ["De l'eau propre (distillée)", "Du gasoil", "De l'huile de coffrage", "Du ciment liquide"]
                    elif q_id == "ad6": copie_opts = ["Degré Brix (%)", "Pascal (Pa)", "Watt (W)", "Ampère (A)"]
                    elif q_id == "ad7": copie_opts = ["Une ou deux gouttes", "Un seau de 10 litres", "Une carotte de béton sec", "Un échantillon de gravier"]
                    elif q_id == "ad8": copie_opts = ["Supérieur", "Inférieur", "Égal", "Nul"]
                    elif q_id == "ad9": copie_opts = ["Gel du béton frais", "Surchauffe à 200°C", "Corrosion des pneus", "Court-circuit"]
                    elif q_id == "ad10": copie_opts = ["Indice de réfraction", "Pression des pneus", "Vitesse du malaxeur", "Hauteur de la grue"]
                else: # camera_reseau
                    if q_id == "ca1": copie_opts = ["Fibres optiques", "Ultrasons magnétiques", "Rayons gamma", "Câbles de cuivre nu"]
                    elif q_id == "ca2": copie_opts = ["Réflexion totale interne", "Réfraction externe", "Conduction thermique", "Électrolyse"]
                    elif q_id == "ca3": copie_opts = ["Supérieur", "Inférieur", "Égal", "Nul"]
                    elif q_id == "ca4": copie_opts = ["S'échapper dans la gaine", "Accélérer", "Devenir infrarouge", "Se réfléchir vers l'arrière"]
                    elif q_id == "ca5": copie_opts = ["Réfraction à travers des lentilles", "Réflexion sur un miroir plan", "Diffraction", "Aimantation"]
                    elif q_id == "ca6": copie_opts = ["Se rétrécit (angle réfracté plus petit)", "S'élargit à 360°", "S'inverse haut/bas", "Ne change pas"]
                    elif q_id == "ca7": copie_opts = ["L'écart d'indice verre/eau est plus faible que verre/air", "L'eau est totalement opaque", "La lentille gonfle dans l'eau", "La lumière va plus vite dans l'eau"]
                    elif q_id == "ca8": copie_opts = ["Snell-Descartes", "Ohm", "Pascal", "Newton"]
                    elif q_id == "ca9": copie_opts = ["Une fissure ou un joint déboîté", "La profondeur de la nappe phréatique à 100 m", "La résistance du béton en MPa", "Le débit électrique"]
                    elif q_id == "ca10": copie_opts = ["Critique (limite)", "Droit", "Plat", "Nul"]

                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts

            val_p = st.session_state.get(cle_qo6, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0

            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt6[f"{q_id}_opt6"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo6, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt6:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 6 (10 pts)")

        if cas_actif == "nivellement_atm":
            phrases = [
                ("1. Sur un chantier chaud, l'air près du sol a un indice plus .........", ["Choisir...", "faible", "élevé", "infini", "négatif"], "t1_opt6"),
                ("2. Le faisceau optique de visée subit une ......... atmosphérique.", ["Choisir...", "réfraction", "absorption", "aimantation", "combustion"], "t2_opt6"),
                ("3. Au lieu d'être droite, la trajectoire du rayon devient .........", ["Choisir...", "curviligne", "verticale", "brisée", "carrée"], "t3_opt6"),
                ("4. Cette courbure fausse la lecture de hauteur sur la ......... graduée.", ["Choisir...", "mire", "pelle", "grue", "benne"], "t4_opt6"),
                ("5. On réduit l'erreur en plaçant le niveau à égale ......... des deux mires.", ["Choisir...", "distance", "hauteur", "vitesse", "pression"], "t5_opt6"),
                ("6. Il faut éviter de viser à moins de 50 cm du ......... surchauffé.", ["Choisir...", "sol", "camion", "casque", "plan"], "t6_opt6"),
                ("7. L'indice de l'air diminue lorsque sa ......... augmente.", ["Choisir...", "température", "couleur", "masse", "vitesse"], "t7_opt6"),
                ("8. Dans un air homogène, la lumière se propage en ligne .........", ["Choisir...", "droite", "courbe", "brisée", "spirale"], "t8_opt6"),
                ("9. Le phénomène est maximal en plein ......... d'été.", ["Choisir...", "après-midi", "hiver", "brouillard", "tunnel"], "t9_opt6"),
                ("10. Chaque déviation suit la loi de .........-Descartes.", ["Choisir...", "Snell", "Joule", "Ohm", "Hooke"], "t10_opt6"),
            ]
        elif cas_actif == "adjuvant_beton":
            phrases = [
                ("1. On contrôle le dosage d'antigel béton avec un ......... de chantier.", ["Choisir...", "réfractomètre", "sonomètre", "manomètre", "voltmètre"], "t1_opt6"),
                ("2. L'appareil mesure l'indice de ......... d'une goutte d'adjuvant.", ["Choisir...", "réfraction", "viscosité", "dureté", "porosité"], "t2_opt6"),
                ("3. Plus la concentration en adjuvant est forte, plus l'indice n .........", ["Choisir...", "augmente", "diminue", "s'annule", "stagne"], "t3_opt6"),
                ("4. La lecture s'effectue sur une échelle graduée en degrés .........", ["Choisir...", "Brix", "Kelvin", "Radian", "Newton"], "t4_opt6"),
                ("5. L'étalonnage du zéro se fait avec de l'......... propre (n = 1,333).", ["Choisir...", "eau", "huile", "essence", "acide"], "t5_opt6"),
                ("6. La ligne claire/sombre correspond à l'angle ......... de réfraction.", ["Choisir...", "limite", "droit", "plat", "nul"], "t6_opt6"),
                ("7. L'indice du prisme en verre est ......... à celui du liquide.", ["Choisir...", "supérieur", "inférieur", "égal", "nul"], "t7_opt6"),
                ("8. Un dosage insuffisant expose le béton frais au risque de .........", ["Choisir...", "gel", "fusion", "rouille", "surchauffe"], "t8_opt6"),
                ("9. La fonction ATC compense l'effet de la ......... ambiante.", ["Choisir...", "température", "lumière", "poussière", "vibration"], "t9_opt6"),
                ("10. Ce contrôle optique rapide évite de couler un béton non .........", ["Choisir...", "conforme", "liquide", "lourd", "gris"], "t10_opt6"),
            ]
        else: # camera_reseau
            phrases = [
                ("1. Les réseaux enterrés sont inspectés grâce à une caméra à ......... optiques.", ["Choisir...", "fibres", "barres", "plaques", "tiges"], "t1_opt6"),
                ("2. La lumière est guidée dans la fibre par ......... totale interne.", ["Choisir...", "réflexion", "réfraction", "diffusion", "absorption"], "t2_opt6"),
                ("3. L'indice du cœur n1 est strictement ......... à celui de la gaine n2.", ["Choisir...", "supérieur", "inférieur", "égal", "nul"], "t3_opt6"),
                ("4. L'objectif grand angle dévie les rayons par ......... à travers les lentilles.", ["Choisir...", "réfraction", "aimantation", "convection", "électrolyse"], "t4_opt6"),
                ("5. Si la caméra plonge dans l'eau (n = 1,33), l'angle de vue se .........", ["Choisir...", "rétrécit", "double", "renverse", "bloque"], "t5_opt6"),
                ("6. L'eau possède un indice de réfraction ......... à celui de l'air (1,00).", ["Choisir...", "supérieur", "inférieur", "égal", "nul"], "t6_opt6"),
                ("7. Un coude trop serré fait passer l'angle sous l'angle .........", ["Choisir...", "critique", "droit", "plat", "nul"], "t7_opt6"),
                ("8. La lumière s'échappe alors dans la ......... et l'éclairage chute.", ["Choisir...", "gaine", "lentille", "batterie", "roue"], "t8_opt6"),
                ("9. Ce contrôle permet de détecter une ......... avant le remblaiement.", ["Choisir...", "fissure", "tempête", "surcharge", "panne moteur"], "t9_opt6"),
                ("10. Le calcul des lentilles repose sur la loi de .........-Descartes.", ["Choisir...", "Snell", "Pascal", "Ohm", "Newton"], "t10_opt6"),
            ]

        dict_trous_opt6 = {}
        for enonce_t, opts_t, cle_t in phrases:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce_t)
            with ct2: dict_trous_opt6[cle_t] = st.selectbox("", opts_t, key=f"opt6_{cle_t}", disabled=verrouille, label_visibility="collapsed")

    return dict_quiz_opt6, dict_trous_opt6
def afficher_questions_optique7(verrouille=False):
    col_double_quiz_opt7, col_double_trous_opt7 = st.columns(2)

    # Récupération du cas routier actif généré dans l'onglet tab7
    cas_actif = st.session_state.get("app_routiere_choisie", "catadioptre")

    # =========================================================================
    # COLONNE GAUCHE : QUIZ SÉLECTIONNÉ SELON LE CAS (10 QUESTIONS)
    # =========================================================================
    with col_double_quiz_opt7:
        st.markdown("##### Quiz d'application routiere (10 questions) - Optique 7 (10 pts)")
        
        # Initialisation unique de l'ordre des questions pour le cas actif
        cle_session_ordre = f"ordre_questions_opt7_{cas_actif}"
        if cle_session_ordre not in st.session_state:
            if cas_actif == "catadioptre":
                base_questions = [
                    ("c1", "Un catadioptre sert a renvoyer les rayons lumineux de facon :"),
                    ("c2", "La forme geometrique interne utilisee dans un catadioptre est un :"),
                    ("c3", "Les facettes arriere du catadioptre forment entre elles un angle de :"),
                    ("c4", "Le retour de la lumiere s'effectue sans miroir grace au phenomene de :"),
                    ("c5", "Apres deux reflexions successives a 90 degres, la deviation totale vaut :"),
                    ("c6", "Pour que le dispositif fonctionne, l'angle d'impact sur la facette doit etre :"),
                    ("c7", "Le grand avantage du catadioptre par rapport a une lampe classique est qu'il est :"),
                    ("c8", "Dans le repere d'un prisme droit, les rayons incidents et emergents sont :"),
                    ("c9", "Si le materiau du catadioptre possede un indice trop faible, la lumiere va :"),
                    ("c10", "Sur la route, les catadioptres équipent obligatoirement l'arriere des véhicules en :")
                ]
            elif cas_actif == "mirage":
                base_questions = [
                    ("m1", "Le mirage routier donne l'illusion visuelle de la présence d'une :"),
                    ("m2", "En ete, la forte chaleur emise par le bitume rend l'air en surface tres :"),
                    ("m3", "Cet air fortement chauffe possede une densite plus :"),
                    ("m4", "L'indice de refraction de la couche d'air au ras du sol devient donc plus :"),
                    ("m5", "Le gradient d'indice genere des couches d'air qui font courber la trajectoire en :"),
                    ("m6", "La reflexion totale progressive se produit car l'angle d'incidence finit par dépasser l' :"),
                    ("m7", "Les rayons lumineux qui subissent cette courbe proviennent initialement du :"),
                    ("m8", "Puisque l'indice varie continuellement avec l'altitude, la trajectoire finale est :"),
                    ("m9", "L'oeil du conducteur prolonge la trajectoire rectilignement et voit une image :"),
                    ("m10", "Ce phenomene montre que la lumiere ne se propage en ligne droite que si le milieu est :")
                ]
            elif cas_actif == "capteur_pluie":
                base_questions = [
                    ("p1", "Le capteur de pluie automatique d'une automobile est generalement place derriere le :"),
                    ("p2", "La source lumineuse utilisee par l'emetteur est une LED fonctionnant en :"),
                    ("p3", "Lorsque le pare-brise est sec, le faisceau lumineux subit sur la face externe une :"),
                    ("p4", "L'angle d'injection initial de la LED dans le verre est calcule pour etre :"),
                    ("p5", "Dans des conditions seches, la quantite de lumiere renvoyee au recepteur vaut environ :"),
                    ("p6", "L'indice de refraction de l'eau (n = 1.33) est superieur a celui de l' :"),
                    ("p7", "L'arrivee d'eau sur le pare-brise modifie la valeur de l'angle :"),
                    ("p8", "Lorsque la condition aux limites change a cause de la pluie, la reflexion totale est :"),
                    ("p9", "Une fraction importante de l'intensite lumineuse infrarouge va alors :"),
                    ("p10", "La baisse de signal electrique mesuree par la photodiode declenche l'action des :")
                ]
            else: # panneau_signalisation
                base_questions = [
                    ("s1", "Le revetement brillant des panneaux de signalisation routiere modernes est un :"),
                    ("s2", "Ce film plastique technique renferme une multitude de structures nommees :"),
                    ("s3", "Contrairement a un miroir classique, le panneau de signalisation renvoie le flux vers :"),
                    ("s4", "Cette capacite particuliere a renvoyer la lumiere vers sa source s'appelle la :"),
                    ("s5", "A l'interieur d'un microprisme, les rayons subissent une serie de reflexions :"),
                    ("s6", "La surface du panneau semble s'illuminer fortement des que la voiture allume ses :"),
                    ("s7", "La directivite du faisceau evite de disperser inutilement l'energie vers le :"),
                    ("s8", "La condition de guidage impose que l'indice du plastique soit superieur a celui de l' :"),
                    ("s9", "Les facettes microscopiques arriere agissent comme des miroirs parfaits grace a l' :"),
                    ("s10", "Pour l'automobiliste de nuit, ce systeme passif apporte un gain majeur en termes de :")
                ]
            import random
            random.shuffle(base_questions)
            st.session_state[cle_session_ordre] = base_questions

        dict_quiz_opt7 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state[cle_session_ordre], 1):
            cle_qo7 = f"col_g_quiz_opt7_{cas_actif}_{q_id}"
            cle_opts_unique = f"opts_opt7_shuffled_{cas_actif}_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if cas_actif == "catadioptre":
                    if q_id == "c1": copie_opts = ["Parallèle à l'axe incident", "Perpendiculaire à la route", "Diffuse dans toutes les directions", "Divergente vers le fossé"]
                    elif q_id == "c2": copie_opts = ["Coin de cube (angle droit)", "Cylindre concave", "Disque convexe plan", "Prisme dispersif triangulaire"]
                    elif q_id == "c3": copie_opts = ["90°", "45°", "60°", "180°"]
                    elif q_id == "c4": copie_opts = ["Réflexion totale interne", "Réfraction limite", "Dispersion chromatique", "Interférence destructive"]
                    elif q_id == "c5": copie_opts = ["180° (demi-tour complet)", "90° (quart de tour)", "0° (aucune déviation)", "360° (tour complet)"]
                    elif q_id == "c6": copie_opts = ["Supérieur à l'angle critique", "Inférieur à l'angle critique", "Parfaitement nul", "Égal à 30°"]
                    elif q_id == "c7": copie_opts = ["Passif (sans consommation électrique)", "Actif à batterie", "Fluorescent à rayons UV", "Alimenté par l'alternateur"]
                    elif q_id == "c8": copie_opts = ["Parallèles", "Perpendiculaires", "Sécants à 45°", "Inclinés à 60°"]
                    elif q_id == "c9": copie_opts = ["S'échapper par réfraction", "Être absorbée à 100%", "Accélérer sa course", "Changer de longueur d'onde"]
                    elif q_id == "c10": copie_opts = ["Rouge", "Blanc", "Jaune", "Bleu"]
                elif cas_actif == "mirage":
                    if q_id == "m1": copie_opts = ["Flaque d'eau", "Plaque de verglas", "Ombre géante", "Brumisation dense"]
                    elif q_id == "m2": copie_opts = ["Chaud", "Froid", "Humide", "Saturé en ozone"]
                    elif q_id == "m3": copie_opts = ["Faible", "Élevée", "Infinie", "Stable"]
                    elif q_id == "m4": copie_opts = ["Faible", "Élevé", "Nul", "Égal à celui du verre"]
                    elif q_id == "m5": copie_opts = ["U inversé (courbe montante)", "Ligne droite oblique", "Z (zig-zag brisé)", "Spirale descendante"]
                    elif q_id == "m6": copie_opts = ["Angle critique (limite)", "Angle droit", "Angle nul", "Angle d'incidence normal"]
                    elif q_id == "m7": copie_opts = ["Ciel", "Sol", "Tableau de bord", "Phares de la voiture"]
                    elif q_id == "m8": copie_opts = ["Curviligne (courbe)", "Rectiligne (droite)", "Brisée en facettes", "Ondulatoire sinusoïdale"]
                    elif q_id == "m9": copie_opts = ["Inversée (reflétée)", "Droite et rétrécie", "Floue et décolorée", "Totalement invisible"]
                    elif q_id == "m10": copie_opts = ["Homogène", "Hétérogène", "Opaque", "Conducteur"]
                elif cas_actif == "capteur_pluie":
                    if q_id == "p1": copie_opts = ["Rétroviseur central", "Pare-chocs avant", "Compteur de vitesse", "Gicleur de lave-glace"]
                    elif q_id == "p2": copie_opts = ["Infrarouge (invisible)", "Ultraviolet", "Laser vert puissant", "Lumière blanche pulsée"]
                    elif q_id == "p3": copie_opts = ["Réflexion totale interne", "Réfraction vers l'extérieur", "Absorption calorifique", "Dispersion spectrale"]
                    elif q_id == "p4": copie_opts = ["Supérieur à l'angle critique", "Inférieur à l'angle critique", "Nul (incidence normale)", "Égal à 90°"]
                    elif q_id == "p5": copie_opts = ["100% (intensité maximale)", "50% (intensité moitié)", "0% (signal nul)", "25% seulement"]
                    elif q_id == "p6": copie_opts = ["Air (n = 1.00)", "Verre (n = 1.50)", "Plexiglas (n = 1.49)", "Diamant (n = 2.42)"]
                    elif q_id == "p7": copie_opts = ["Critique (limite)", "De Brewster", "D'injection", "De émergence"]
                    elif q_id == "p8": copie_opts = ["Brisée (rompue)", "Amplifiée", "Stabilisée", "Inversée"]
                    elif q_id == "p9": copie_opts = ["S'échapper dans la goutte", "Retourner vers la LED", "Se transformer en chaleur", "Accélérer dans le verre"]
                    elif q_id == "p10": copie_opts = ["Essuie-glaces", "Phares directionnels", "Freins d'urgence", "Feux de détresse"]
                else: # panneau_signalisation
                    if q_id == "s1": copie_opts = ["Film plastique technique", "Miroir d'argent classique", "Vernis fluorescent", "Plaque métallique polie"]
                    elif q_id == "s2": copie_opts = ["Microprismes transparents", "Lentilles concaves", "Fibres optiques parallèles", "Fils de carbone"]
                    elif q_id == "s3": copie_opts = ["La voiture d'origine (la source)", "Le ciel uniquement", "Le bas-côté de la chaussée", "Les nuages en hauteur"]
                    elif q_id == "s4": copie_opts = ["Rétroréflexion", "Réfraction totale", "Dispersion diffuse", "Focalisation optique"]
                    elif q_id == "s5": copie_opts = ["Totales internes", "Partielles externes", "Réfractées rasantes", "Absorbantes sélectives"]
                    elif q_id == "s6": copie_opts = ["Phares", "Clignotants", "Feux de stop", "Plafonniers"]
                    elif q_id == "s7": copie_opts = ["Ciel ou environnement", "Sol immédiat", "Moteur", "Rétroviseur"]
                    elif q_id == "s8": copie_opts = ["Air", "Verre", "Métal", "Silicone lourd"]
                    elif q_id == "s9": copie_opts = ["Angle limite dépassé", "Dépôt d'argenture", "Peinture blanche", "Effet laser de champ"]
                    elif q_id == "s10": copie_opts = ["Sécurité routière", "Vitesse de conduite", "Consommation de carburant", "Confort des sièges"]
                
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts

            val_p = st.session_state.get(cle_qo7, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0

            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt7[f"{q_id}_opt7"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo7, disabled=verrouille, label_visibility="collapsed")

    # =========================================================================
    # COLONNE DROITE : SYNTHÈSE DE COURS À TROUS VARIANT SELON LE CAS (4 OPTIONS)
    # =========================================================================
    with col_double_trous_opt7:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 7 (10 pts)")

        if cas_actif == "catadioptre":
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. Le catadioptre routier utilise un bloc plastique constitue de petits")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Prismes", "Miroirs", "Fils", "Lentilles"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. tailles en angle droit. Le faisceau lumineux des phares y subit une")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Réflexion", "Réfraction", "Dispersion", "Absorption"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. qui est qualifiée de totale car toute l'intensité est renvoyée dans le milieu")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Initial", "Extérieur", "Métallique", "Opaque"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. sans aucune perte. Les rebonds successifs dévient le rayon d'un angle de")
            with ct8: t4 = st.selectbox("", ["Choisir...", "90°", "45°", "180°", "0°"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. sur chaque face interne. Le faisceau émergeant repart de facon")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Parallèle", "Inclinée", "Perpendiculaire", "Diffuse"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. par rapport à l'axe d'entrée. Ce retour rectiligne cible directement le")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Conducteur", "Piéton", "Nuage", "Soleil"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. de l'automobile. Ce système fonctionne la nuit de manière entièrement")
            with ct14: t7 = st.selectbox("", ["Choisir...", "Passive", "Active", "Électrique", "Thermique"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. sans consommer de batterie. Pour être visible, l'indice du plastique doit être")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Supérieur", "Inférieur", "Égal", "Nul"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. à l'indice extérieur de l'")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Air", "Verre", "Eau", "Goudron"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. afin que la condition limite de Snell-Descartes soit toujours vérifiée pour la sécurité")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Routière", "Aérienne", "Maritime", "Ferroviaire"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        elif cas_actif == "mirage":
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. Le mirage routier apparaît en été lorsque la forte chaleur surchauffe le")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Bitume", "Ciel", "Pneu", "Pare-brise"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. de la chaussée. Cela diminue localement la densité et l'indice de l'")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Air", "Sol", "Goudron", "Verre"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. au ras du sol. L'indice de réfraction de cette zone devient très")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Faible", "Élevé", "Infini", "Stable"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. par rapport à l'air frais plus haut. Les rayons lumineux descendants du")
            with ct8: t4 = st.selectbox("", ["Choisir...", "Ciel", "Moteur", "Phares", "Tableau"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. traversent un milieu d'indice continuellement décroissant. La trajectoire est")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Curviligne", "Rectiligne", "Brisée", "Ondulée"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. car l'angle d'incidence augmente à chaque couche d'air jusqu'à dépasser l'angle")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Critique", "Droit", "Nul", "Plat"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. On observe alors une réflexion totale progressive qui fait remonter le rayon vers l'")
            with ct14: t7 = st.selectbox("", ["Choisir...", "Oeil", "Bitume", "Feu", "Brouillard"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. de l'automobiliste. Le cerveau prolonge la direction finale et interprète une image")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Inversée", "Droite", "Rétrécie", "Invisible"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. de l'azur lointain sur l'asphalte, provoquant la spectaculaire")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Illusion", "Ombre", "Teinte", "Vapeur"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. d'une fausse flaque d'eau miroitante sur une route totalement")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Sèche", "Mouillée", "Inondée", "Glacée"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        elif cas_actif == "capteur_pluie":
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. Le capteur automatique d'essuyage est fixé directement contre le")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Pare-brise", "Moteur", "Pneu", "Phare"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. Une source émettrice produit un rayon invisible de nature")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Infrarouge", "Ultraviolete", "Laser", "Visible"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. Ce faisceau est injecté à l'intérieur de l'épaisseur du")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Verre", "Plastique", "Silicone", "Quartz"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. Tant que la surface extérieure reste parfaitement sèche, le contact avec l'")
            with ct8: t4 = st.selectbox("", ["Choisir...", "Air", "Eau", "Métal", "Givre"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. d'indice n = 1.00 provoque au niveau du dioptre une réflexion")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Totale", "Partielle", "Diffuse", "Nulle"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. interne. L'intégralité de l'énergie lumineuse est guidée vers le")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Récepteur", "Générateur", "Prisme", "Miroir"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. Mais lorsque des gouttes d'eau se déposent, l'indice externe passe à")
            with ct14: t7 = st.selectbox("", ["Choisir...", "1.33", "1.00", "1.50", "2.42"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. Cette élévation d'indice à l'interface modifie l'angle limite : la condition est")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Brisée", "Rendue stable", "Inversée", "Amplifiée"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. Une partie de la lumière s'échappe à l'extérieur. La photodiode mesure une forte")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Baisse", "Hausse", "Stabilité", "Dispersion"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. d'intensité, ce qui commande l'enclenchement instantané des")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Essuie-glaces", "Freins", "Phares", "Clignotants"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        else: # panneau_signalisation
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. La rétroréflexion nocturne des panneaux utilise un film plastique à")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Microprismes", "Miroirs", "Lentilles", "Fils"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. Le faisceau lumineux provient directement des projecteurs de")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Phares", "Clignotants", "Feux de stop", "Plafonniers"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. de la voiture. La lumière pénètre dans le polymère rigide de nature")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Transparente", "Opaque", "Réfléchissante", "Métallique"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. Elle rencontre les facettes microscopiques arrières de chaque prisme droit")
            with ct8: t4 = st.selectbox("", ["Choisir...", "D'angle droit", "Arrondies", "Concaves", "Polies"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. Le guidage interne parfait de l'intensité s'effectue par réflexion")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Totale", "Partielle", "Diffuse", "Réfractée"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. car la valeur d'incidence dépasse l'angle critique de l'interface avec l'")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Air", "Verre", "Métal", "Eau"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. Mais lorsque des gouttes d'eau se déposent, l'indice externe passe à")
            with ct14: t7 = st.selectbox("", ["Choisir...", "1.33", "1.00", "1.50", "2.42"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. Les rayons concentrés retournent vers le conducteur au lieu d'être")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Dispersés", "Absorbés", "Accélérés", "Filtrés"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. dans l'espace ou vers le ciel. La surface du panneau semble posséder une forte")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Luminosité", "Chaleur", "Transparence", "Opacité"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. apportant une aide à la visibilité indispensable pour assurer la sécurité")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Routière", "Aérienne", "Maritime", "Industrielle"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        # Ligne de conclusion invariable commune aux 4 structures conditionnelles
        ct_fin1, ct_fin2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with ct_fin1: st.write("Ces diverses applications routieres mettent en evidence la maitrise des phenomenes optiques pour la securite.")

        dict_trous_opt7 = {
            "t1_opt7": t1, "t2_opt7": t2, "t3_opt7": t3, "t4_opt7": t4, "t5_opt7": t5,
            "t6_opt7": t6, "t7_opt7": t7, "t8_opt7": t8, "t9_opt7": t9, "t10_opt7": t10
        }

    return dict_quiz_opt7, dict_trous_opt7

def afficher_questions_optique8(verrouille=False):
    col_double_quiz_opt8, col_double_trous_opt8 = st.columns(2)

    cas_actif = st.session_state.get("app_geo_choisie", "refraction_terrestre")

    with col_double_quiz_opt8:
        st.markdown("##### Quiz d'application Géomètre Topographe (10 questions) - Optique 8 (10 pts)")

        cle_session_ordre = f"ordre_questions_opt8_{cas_actif}"
        if cle_session_ordre not in st.session_state:
            if cas_actif == "refraction_terrestre":
                base_questions = [
                    ("g1", "Dans l'atmosphère terrestre, l'indice de réfraction de l'air diminue lorsque l'altitude :"),
                    ("g2", "À cause de ce gradient d'indice vertical, la ligne de visée d'un théodolite s'incurve vers :"),
                    ("g3", "Quelle est la valeur moyenne standard du coefficient de réfraction atmosphérique k en géodésie ?"),
                    ("g4", "Sur une visée longue (ex : 1 km), ne pas corriger la réfraction atmosphérique fausse la mesure d' :"),
                    ("g5", "Pour éliminer naturellement la réfraction atmosphérique, le géomètre pratique le nivellement par :"),
                    ("g6", "Dans le vide absolu, l'indice de réfraction vaut 1,00000 ; au niveau de la mer, il vaut environ :"),
                    ("g7", "Quelle grandeur météorologique mesurée sur le terrain permet d'affiner la correction d'indice ?"),
                    ("g8", "En traversant des couches d'air de plus en plus denses vers le sol, le rayon lumineux se rapproche de la :"),
                    ("g9", "L'erreur altimétrique due à la réfraction augmente proportionnellement au carré de la :"),
                    ("g10", "La déviation continue d'un rayon dans l'atmosphère obéit à la loi de :")
                ]
            elif cas_actif == "constante_prisme":
                base_questions = [
                    ("p1", "Lorsqu'un faisceau infrarouge entre dans un prisme topographique en verre (n = 1,52), sa vitesse :"),
                    ("p2", "Le ralentissement de la lumière dans le verre du prisme allonge le temps de trajet optique, ce qui impose une :"),
                    ("p3", "Quelle est la valeur courante de la constante de prisme sur un réflecteur topographique standard ?"),
                    ("p4", "Si le géomètre oublie de saisir la constante de prisme dans sa station totale, toutes les distances sont faussées de :"),
                    ("p5", "À l'entrée dans le prisme en verre (n = 1,52) depuis l'air (n = 1,00), le rayon subit une :"),
                    ("p6", "À l'intérieur du prisme coin de cube, le faisceau est renvoyé vers la station par :"),
                    ("p7", "Quel est l'indice de réfraction typique du verre borosilicate utilisé dans les prismes de précision ?"),
                    ("p8", "La vitesse de la lumière dans un verre d'indice n se calcule par la relation :"),
                    ("p9", "La face avant d'un prisme topographique reçoit un traitement antireflet pour limiter les pertes par :"),
                    ("p10", "Pour mesurer une distance en mode « sans prisme » directement sur un mur, la constante vaut :")
                ]
            else: # bathymetrie_lidar
                base_questions = [
                    ("b1", "Pour relever le relief des fonds marins ou fluviaux par avion, le géomètre utilise un LiDAR à laser :"),
                    ("b2", "Pourquoi utilise-t-on une longueur d'onde verte (532 nm) plutôt qu'infrarouge en bathymétrie ?"),
                    ("b3", "En pénétrant de l'air (n = 1,00) dans l'eau (n = 1,33), le faisceau laser est dévié par :"),
                    ("b4", "Lorsqu'il entre obliquement dans l'eau, le rayon laser se rapproche de la :"),
                    ("b5", "Dans l'eau (n = 1,33), la vitesse de propagation du laser diminue d'environ :"),
                    ("b6", "Si le logiciel ne corrigeait pas l'indice de l'eau (n = 1,33), la profondeur mesurée serait :"),
                    ("b7", "Le capteur aéroporté reçoit deux échos : un premier sur la surface de l'eau et un second sur le :"),
                    ("b8", "La différence de temps entre l'écho de surface et l'écho du fond permet de calculer la :"),
                    ("b9", "Quel angle de visée du scanner utilise-t-on pour limiter la réflexion spéculaire à la surface de l'eau ?"),
                    ("b10", "Le calcul exact de la trajectoire sous-marine du laser applique la loi de :")
                ]
            random.shuffle(base_questions)
            st.session_state[cle_session_ordre] = base_questions

        dict_quiz_opt8 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state[cle_session_ordre], 1):
            cle_qo8 = f"col_g_quiz_opt8_{cas_actif}_{q_id}"
            cle_opts_unique = f"opts_opt8_shuffled_{cas_actif}_{q_id}"

            if cle_opts_unique not in st.session_state:
                if cas_actif == "refraction_terrestre":
                    if q_id == "g1": copie_opts = ["Augmente", "Diminue", "Reste nulle", "Devient négative"]
                    elif q_id == "g2": copie_opts = ["Le bas (la surface terrestre)", "L'espace verticalement", "La gauche uniquement", "L'arrière de l'appareil"]
                    elif q_id == "g3": copie_opts = ["0,13", "1,52", "9,81", "0,00"]
                    elif q_id == "g4": copie_opts = ["Altitude (denivelée)", "Couleur du sol", "Température du trépied", "Charge de batterie"]
                    elif q_id == "g5": copie_opts = ["Rayonnement égal (portées égales)", "Visée unique à 5 km", "Lecture nocturne sans mire", "Calcul magnétique"]
                    elif q_id == "g6": copie_opts = ["1,00029", "1,33300", "1,52000", "2,42000"]
                    elif q_id == "g7": copie_opts = ["Température et pression atmosphérique", "Vitesse du son", "Humidité du bois", "Taux de CO2"]
                    elif q_id == "g8": copie_opts = ["Normale (verticale)", "Tangente horizontale", "Mire arrière", "Boussole"]
                    elif q_id == "g9": copie_opts = ["Distance", "Hauteur du trépied", "Largeur de la mire", "Masse de l'opérateur"]
                    elif q_id == "g10": copie_opts = ["Snell-Descartes", "Coulomb", "Joule", "Archimède"]
                elif cas_actif == "constante_prisme":
                    if q_id == "p1": copie_opts = ["Diminue (v = c / n)", "Augmente de 50 %", "Devient infinie", "S'annule"]
                    elif q_id == "p2": copie_opts = ["Constante de prisme", "Tare magnétique", "Correction solaire", "Balance des blancs"]
                    elif q_id == "p3": copie_opts = ["-34,4 mm (ou 0 mm)", "+15,0 mètres", "-2,5 kilomètres", "+500 cm"]
                    elif q_id == "p4": copie_opts = ["Plusieurs centimètres systématiquement", "0,000 mm", "10 mètres", "50 %"]
                    elif q_id == "p5": copie_opts = ["Réfraction", "Diffraction", "Combustion", "Polarisation circulaire"]
                    elif q_id == "p6": copie_opts = ["Réflexion totale interne", "Absorption thermique", "Réfraction diffuse", "Interférence"]
                    elif q_id == "p7": copie_opts = ["1,52", "1,00", "1,33", "0,85"]
                    elif q_id == "p8": copie_opts = ["v = c / n", "v = c × n", "v = c + n", "v = n / c"]
                    elif q_id == "p9": copie_opts = ["Réflexion vitreuse parasite", "Condensation", "Dilatation", "Rayures"]
                    elif q_id == "p10": copie_opts = ["0 mm", "-34,4 mm", "+100 mm", "-10 cm"]
                else: # bathymetrie_lidar
                    if q_id == "b1": copie_opts = ["Vert (532 nm)", "Infrarouge lointain", "Ultraviolet", "Micro-ondes"]
                    elif q_id == "b2": copie_opts = ["La lumière verte pénètre profondément dans l'eau claire", "L'infrarouge traverse 500 m d'eau", "Le vert est invisible", "L'eau amplifie le vert"]
                    elif q_id == "b3": copie_opts = ["Réfraction", "Réflexion totale", "Diffraction", "Aimantation"]
                    elif q_id == "b4": copie_opts = ["Normale", "Surface de l'eau", "Horizontalité", "Queue de l'avion"]
                    elif q_id == "b5": copie_opts = ["25 % (v ≈ 225 000 km/s)", "90 %", "0 %", "50 %"]
                    elif q_id == "b6": copie_opts = ["Surestimée (trop profonde de 33 %)", "Sous-estimée de moitié", "Parfaitement exacte", "Négative"]
                    elif q_id == "b7": copie_opts = ["Fond marin (lit de la rivière)", "Nuage", "Soleil", "Capot de l'avion"]
                    elif q_id == "b8": copie_opts = ["Profondeur d'eau", "Salinité en g/L", "Température de l'eau", "Vitesse du courant"]
                    elif q_id == "b9": copie_opts = ["Inclinaison oblique constante (15° à 20°)", "0° strictement vertical", "85° rasant", "90° horizontal"]
                    elif q_id == "b10": copie_opts = ["Snell-Descartes", "Ohm", "Bernoulli", "Hooke"]

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

        if cas_actif == "refraction_terrestre":
            phrases = [
                ("1. L'indice de réfraction de l'air diminue avec l'.........", ["Choisir...", "altitude", "couleur", "vitesse", "masse"], "t1_opt8"),
                ("2. La ligne de visée d'un théodolite s'incurve vers le .........", ["Choisir...", "sol", "ciel", "nord", "sud"], "t2_opt8"),
                ("3. Le coefficient moyen de réfraction terrestre vaut k = .........", ["Choisir...", "0.13", "1.52", "9.81", "0.00"], "t3_opt8"),
                ("4. Cette courbure introduit une erreur sur les mesures d'.........", ["Choisir...", "altitude", "surface", "temps", "tension"], "t4_opt8"),
                ("5. On annule cet effet en plaçant la station à égale ......... des mires.", ["Choisir...", "distance", "hauteur", "température", "pente"], "t5_opt8"),
                ("6. Au niveau de la mer, l'indice de l'air vaut environ .........", ["Choisir...", "1.00029", "1.33300", "1.52000", "2.42000"], "t6_opt8"),
                ("7. L'appareil corrige l'indice grâce à la température et la .........", ["Choisir...", "pression", "lumière", "batterie", "boussole"], "t7_opt8"),
                ("8. L'erreur altimétrique varie comme le ......... de la distance.", ["Choisir...", "carré", "double", "tiers", "logarithme"], "t8_opt8"),
                ("9. En entrant dans un air plus dense, le rayon se rapproche de la .........", ["Choisir...", "normale", "mire", "lunette", "terre"], "t9_opt8"),
                ("10. Ce phénomène applique la loi de .........-Descartes.", ["Choisir...", "Snell", "Pascal", "Joule", "Ohm"], "t10_opt8"),
            ]
        elif cas_actif == "constante_prisme":
            phrases = [
                ("1. Dans le verre du prisme (n = 1,52), la vitesse de la lumière .........", ["Choisir...", "diminue", "augmente", "double", "s'annule"], "t1_opt8"),
                ("2. La vitesse dans un milieu d'indice n vaut v = c / .........", ["Choisir...", "n", "2", "t", "d"], "t2_opt8"),
                ("3. Ce ralentissement optique impose de régler la ......... de prisme.", ["Choisir...", "constante", "masse", "couleur", "hauteur"], "t3_opt8"),
                ("4. Une valeur courante de constante de prisme est ......... mm.", ["Choisir...", "-34.4", "+500", "-1200", "+85.0"], "t4_opt8"),
                ("5. À l'entrée du prisme, le rayon infrarouge subit une .........", ["Choisir...", "réfraction", "diffraction", "combustion", "dispersion"], "t5_opt8"),
                ("6. Le retour vers la station totale s'effectue par ......... totale interne.", ["Choisir...", "réflexion", "absorption", "convection", "diffusion"], "t6_opt8"),
                ("7. L'indice du verre optique vaut environ .........", ["Choisir...", "1.52", "1.00", "1.33", "0.50"], "t7_opt8"),
                ("8. Un traitement antireflet réduit les pertes sur la face .........", ["Choisir...", "avant", "inférieure", "métallique", "latérale"], "t8_opt8"),
                ("9. En mode sans prisme sur un mur, la constante vaut ......... mm.", ["Choisir...", "0", "-34.4", "+50", "-100"], "t9_opt8"),
                ("10. Le calcul de déviation utilise la loi de .........-Descartes.", ["Choisir...", "Snell", "Newton", "Ohm", "Hooke"], "t10_opt8"),
            ]
        else: # bathymetrie_lidar
            phrases = [
                ("1. La bathymétrie aéroportée utilise un laser de couleur ......... (532 nm).", ["Choisir...", "verte", "rouge", "infrarouge", "ultraviolette"], "t1_opt8"),
                ("2. En pénétrant dans l'eau (n = 1,33), le faisceau subit une .........", ["Choisir...", "réfraction", "aimantation", "extinction", "diffraction"], "t2_opt8"),
                ("3. Dans l'eau, le rayon laser se rapproche de la .........", ["Choisir...", "normale", "surface", "plage", "rive"], "t3_opt8"),
                ("4. La vitesse du laser dans l'eau est plus ......... que dans l'air.", ["Choisir...", "faible", "grande", "instantanée", "chaude"], "t4_opt8"),
                ("5. L'indice de réfraction de l'eau vaut environ .........", ["Choisir...", "1.33", "1.00", "1.52", "2.42"], "t5_opt8"),
                ("6. Le capteur enregistre l'écho de surface et l'écho du .........", ["Choisir...", "fond", "nuage", "soleil", "bateau"], "t6_opt8"),
                ("7. Sans correction d'indice, la profondeur serait ......... de 33 %.", ["Choisir...", "surestimée", "annulée", "inversée", "divisée par 10"], "t7_opt8"),
                ("8. On vise avec un angle ......... pour éviter l'éblouissement de surface.", ["Choisir...", "oblique", "nul", "rasant", "vertical"], "t8_opt8"),
                ("9. Cette technique permet de cartographier le relief des fonds .........", ["Choisir...", "marins", "rocheux secs", "nuageux", "urbains"], "t9_opt8"),
                ("10. Le logiciel corrige l'angle grâce à la loi de .........-Descartes.", ["Choisir...", "Snell", "Joule", "Pascal", "Ohm"], "t10_opt8"),
            ]

        dict_trous_opt8 = {}
        for enonce_t, opts_t, cle_t in phrases:
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write(enonce_t)
            with ct2: dict_trous_opt8[cle_t] = st.selectbox("", opts_t, key=f"opt8_{cle_t}", disabled=verrouille, label_visibility="collapsed")

    return dict_quiz_opt8, dict_trous_opt8



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
    st.header("Atelier 1 : Historique sur la réfraction")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Objectif de l'atelier :</p>
        <p style="color: #334155; margin-bottom: 0;">Découvrir l'évolution historique des connaissances sur la déviation de la lumière à travers les milieux transparents, de l'Antiquité jusqu'à la formulation mathématique de Snell-Descartes.</p>
    </div>
    """, unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)

    with col_h1:
        try:
            st.image("ptolemee.jpg", caption="Claude Ptolémée (IIe siècle)", use_container_width=True)
        except Exception:
            st.warning("Fichier image ptolemee.jpg introuvable dans le dossier.")
        st.info("**Claude Ptolémée (vers 150 ap. J.-C.)**\n* Astronome grec vivant à Alexandrie.\n* Il mesure les premiers tableaux d'angles entre l'air, l'eau et le verre, mais pense à tort que l'angle réfracté est proportionnel à l'angle incident.")

    with col_h2:
        try:
            st.image("ibn_sahl.jpg", caption="Ibn Sahl (940 - 1000)", use_container_width=True)
        except Exception:
            st.warning("Fichier image ibn_sahl.jpg introuvable dans le dossier.")
        st.info("**Ibn Sahl (*Sur les instruments ardents*, 984)**\n* Mathématicien de Bagdad.\n* Il découvre le premier la loi exacte des sinus et l'utilise pour concevoir des lentilles convergentes sans aberration.")

    with col_h3:
        try:
            st.image("snell.jpg", caption="Willebrord Snellius (1580 - 1626)", use_container_width=True)
        except Exception:
            st.warning("Fichier image snell.jpg introuvable dans le dossier.")
        st.info("**Willebrord Snell (1621)**\n* Astronome et mathématicien néerlandais.\n* Il redécouvre expérimentalement le rapport constant entre sin(i1) et sin(i2), resté non publié de son vivant.")

    with col_h4:
        try:
            st.image("descartes_refraction.jpg", caption="René Descartes (1596 - 1650)", use_container_width=True)
        except Exception:
            st.warning("Fichier image descartes_refraction.jpg introuvable dans le dossier.")
        st.info("**René Descartes (*La Dioptrique*, 1637)**\n* Mathématicien, physicien et philosophe français.\n* Il publie la formulation moderne universelle : n1.sin(i1) = n2.sin(i2) et définit l'indice de réfraction.")

    st.markdown("---")

    liste_q_opt1, liste_t_opt1 = afficher_questions_refraction_hist(
        verrouille=st.session_state.get("opt1_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt1 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 1.",
        key="check_certif_opt1_officiel_20pts",
        disabled=st.session_state.get("opt1_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_opt1_official_20pts", use_container_width=True, disabled=st.session_state.get("opt1_verrouille", False)):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_quiz_opt1 = sum(1.0 for qid, _, _, rep in liste_q_opt1 if st.session_state.get(f"col_g_quiz_opt1_{qid}") == rep)
            score_trous_opt1 = sum(1.0 for _, _, rep, cle in liste_t_opt1 if st.session_state.get(cle) == rep)

            st.session_state.score_opt1_p1 = round(score_quiz_opt1, 1)
            st.session_state.score_opt1_p2 = round(score_trous_opt1, 1)
            st.session_state.score_final_opt1 = round(score_quiz_opt1 + score_trous_opt1, 1)
            st.session_state.opt1_verrouille = True
            st.rerun()

    if st.session_state.get("opt1_verrouille", False):
        scr1 = st.session_state.get("score_opt1_p1", 0.0)
        scr2 = st.session_state.get("score_opt1_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt1", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 1 SCELLE ET VALIDE | Note : {tot_s} / 20")

        html_export_opt1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 1 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Atelier 1 : Historique Refraction | Scelle le : {timestamp_opt1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores - Optique 1</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire historique : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ HISTORIQUE (10 PTS)</div>
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

        for idx_t, (qid, enonce_q, _, attendu) in enumerate(liste_q_opt1, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt1_{qid}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div>
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

        for enonce_t, _, attendu_t, cle_t in liste_t_opt1:
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td style='text-align: left;'>{enonce_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align: center;'>{v_lbl_t}</td></tr>"

        html_export_opt1 += """
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
            data=html_export_opt1,
            file_name=f"Bilan_Optique1_{n_eleve}.html",
            mime="text/html",
            use_container_width=True)

with tab2:
    
    st.header("Atelier  : Lois de Snell-Descartes ")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel des Formules Fondamentales de la Réfraction :</p>
        <ul>
            <li><strong>Deuxième loi de Snell-Descartes :</strong> <i>n</i><sub>1</sub> &middot; sin(<i>i</i><sub>1</sub>) = <i>n</i><sub>2</sub> &middot; sin(<i>i</i><sub>2</sub>)</li>
            <li><strong>Loi du double dioptre (Lame à faces parallèles) :</strong> Le rayon émergent sort de la lame avec un angle de déviation nul (<i>i</i><sub>3</sub> = <i>i</i><sub>1</sub>) mais subit un <strong>décalage latéral <i>dx</i></strong>.</li>
            <li><strong>Calcul de la pente :</strong> En traçant sin(<i>i</i><sub>1</sub>) en fonction de sin(<i>i</i><sub>2</sub>), la droite linéaire possède un coefficient directeur égal au rapport des indices <i>n</i><sub>2</sub> / <i>n</i><sub>1</sub>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt4_verrouille" not in st.session_state: 
        st.session_state.opt4_verrouille = False

    # Initialisation permanente des listes de mesures d'origine (Reconversion Tkinter)
    if "mesures_sin_i" not in st.session_state: st.session_state.mesures_sin_i = []
    if "mesures_sin_r" not in st.session_state: st.session_state.mesures_sin_r = []
    if "mesures_i_deg" not in st.session_state: st.session_state.mesures_i_deg = []
    if "mesures_r_deg" not in st.session_state: st.session_state.mesures_r_deg = []

    # Récupération des catalogues présents en mémoire de session
    liste_lampes = list(st.session_state.lampes_data.keys()) if "lampes_data" in st.session_state else ["Lumiere du Soleil"]
    liste_milieux = list(st.session_state.produits_indices.keys()) if "produits_indices" in st.session_state else ["Air (n = 1.00)", "Eau (n = 1.33)", "Verre Couronne (n = 1.52)"]

    # =========================================================================
    # INTERFACE EN COLONNES PROPRE ET AERÉE
    # =========================================================================

    st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:2px;'>1. REFRACTION SIMPLE</p>", unsafe_allow_html=True)
    
    choix_lampe1 = st.selectbox("Source lumineuse :", liste_lampes, key="slider_lampe_simple", disabled=st.session_state.opt4_verrouille)
    angle_i1 = st.slider("Angle d'incidence i1 (°) :", min_value=0.0, max_value=90.0, value=30.0, step=1.0, key="var_angle_inc", disabled=st.session_state.opt4_verrouille)
    
    milieu1 = st.selectbox("Milieu superieur (n1) :", liste_milieux, index=0, key="var_choix_milieu1", disabled=st.session_state.opt4_verrouille)
    milieu2 = st.selectbox("Milieu inferieur (n2) :", liste_milieux, index=1, key="var_choix_milieu2", disabled=st.session_state.opt4_verrouille)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("PRENDRE UNE MESURE", key="btn_mesure_simple_officiel", use_container_width=True, disabled=st.session_state.opt4_verrouille):
            ajouter_point_mesure_optique_streamlit()
            st.rerun()

    with col_btn2:
        if st.button("Effacer le graphique", key="btn_raz_simple_officiel", use_container_width=True, disabled=st.session_state.opt4_verrouille):
            reinitialiser_graphique_optique_streamlit()
            st.rerun()


    # APPEL DE VOTRE DESSIN DU DIOPTRE SIMPLE DE REFRACTION
    fig_cuve_simple = dessiner_schema_refraction_simple()
    st.pyplot(fig_cuve_simple, use_container_width=True)
    
    # Boite blanche de resultats sous le graphique de la cuve
    st.info(st.session_state.get("opt4_txt_box_simple", "Ajustez le curseur pour initialiser."))
        
    st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    st.markdown("##### Tableau des points de mesures memorises (Loi de Snell-Descartes)")
        
    import pandas as pd
    if st.session_state.mesures_i_deg:
        df_treeview = pd.DataFrame({
            "N° Essai": [f"Essai {idx}" for idx in range(1, len(st.session_state.mesures_i_deg) + 1)],
            "Angle i1 (°)": [f"{val:.1f}°" for val in st.session_state.mesures_i_deg],
            "Angle r2 (°)": [f"{val:.1f}°" for val in st.session_state.mesures_r_deg],
            "sin(i1)": st.session_state.mesures_sin_i,
            "sin(r2)": st.session_state.mesures_sin_r
        })
        st.dataframe(df_treeview, use_container_width=True, hide_index=True)
    else:
        st.caption("Tableau de mesures vide. Modifiez l'angle d'incidence et cliquez sur Prendre une mesure pour enregistrer des donnees.")            

                # APPEL DE VOTRE GRAPHIQUE LINÉAIRE EXPERIMENTAL SIN(R) = F(SIN(I))
        fig_loi_sinus = dessiner_graphique_sinus_matplotlib()
        st.pyplot(fig_loi_sinus, use_container_width=True)
    st.markdown("---")

    liste_q_opt2, liste_t_opt2 = afficher_questions_optique2(
        verrouille=st.session_state.get("opt2_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.",
        key="check_certif_opt2_officiel_20pts",
        disabled=st.session_state.get("opt2_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_opt2_official_20pts", use_container_width=True, disabled=st.session_state.get("opt2_verrouille", False)):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_quiz_opt2 = sum(1.0 for qid, _, _, rep in liste_q_opt2 if st.session_state.get(f"col_g_quiz_opt2_{qid}") == rep)
            score_trous_opt2 = sum(1.0 for _, _, rep, cle in liste_t_opt2 if st.session_state.get(cle) == rep)

            st.session_state.score_opt2_p1 = round(score_quiz_opt2, 1)
            st.session_state.score_opt2_p2 = round(score_trous_opt2, 1)
            st.session_state.score_final_opt2 = round(score_quiz_opt2 + score_trous_opt2, 1)
            st.session_state.opt2_verrouille = True
            st.rerun()

    if st.session_state.get("opt2_verrouille", False):
        scr1 = st.session_state.get("score_opt2_p1", 0.0)
        scr2 = st.session_state.get("score_opt2_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt2", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER OPTIQUE 2 SCELLE ET VALIDE | Note : {tot_s} / 20")

        html_export_opt2 = f"""<!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Rapport Optique 2 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Atelier 2 : Lois de Snell-Descartes | Scelle le : {timestamp_opt2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif des scores - Optique 2</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8;">
                &bull; Partie 1 : Questionnaire Snell-Descartes : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>
            <div class="sub-title">PARTIE 1 : QUIZ SNELL-DESCARTES (10 PTS)</div>
            <table><thead><tr><th>N°</th><th>Question posée</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>
        """

        for idx_t, (qid, enonce_q, _, attendu) in enumerate(liste_q_opt2, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt2_{qid}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt2 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_opt2 += """</tbody></table><div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div><table><thead><tr><th>Phrase explicative à trous</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>"""

        for enonce_t, _, attendu_t, cle_t in liste_t_opt2:
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt2 += f"<tr><td>{enonce_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align:center;'>{v_lbl_t}</td></tr>"

        html_export_opt2 += """</tbody></table><div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">Laboratoire d'Optique Physique Appliquee &copy; 2026</div></body></html>"""

        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt2,
            file_name=f"Bilan_Optique2_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("**La double réfraction**")
            
    st.markdown("<p style='color:#991b1b; font-weight:bold; margin-bottom:2px;'> DOUBLE REFRACTION</p>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #991b1b; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #991b1b; margin-top: 0; font-size: 16px;">Principe de la double réfraction (Lame à faces parallèles) :</p>
        <ul style="margin-bottom: 0; line-height: 1.6;">
            <li><strong>Premier dioptre (Entrée Air → Verre) :</strong> Lorsque le rayon lumineux passe d'un milieu moins réfringent (<i>n</i><sub>1</sub> = 1,00) à un milieu plus réfringent (<i>n</i><sub>2</sub> = 1,52), il se rapproche de la normale (<i>r</i><sub>1</sub> &lt; <i>i</i><sub>1</sub>).</li>
            <li><strong>Second dioptre (Sortie Verre → Air) :</strong> En ressortant dans le même milieu initial (<i>n</i><sub>3</sub> = <i>n</i><sub>1</sub>), le rayon s'écarte de la normale d'un angle identique à l'angle d'entrée (<b><i>s</i> = <i>i</i><sub>1</sub></b>).</li>
            <li><strong>Décalage latéral (<i>dx</i>) :</strong> Le rayon émergent reste strictement <b>parallèle</b> au rayon incident mais subit une translation latérale <i>dx</i> qui augmente avec l'épaisseur et l'indice de la lame.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    choix_lampe2 = st.selectbox("Source lumineuse  :", liste_lampes, key="var_choix_lampe_double2", disabled=st.session_state.opt4_verrouille)
    angle_double = st.slider("Angle d'incidence double (°) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="var_angle_double", disabled=st.session_state.opt4_verrouille)
    
    milieu1_d = st.selectbox("Milieu 1 (n1) :", liste_milieux, index=0, key="var_choix_milieu1_double", disabled=st.session_state.opt4_verrouille)
    milieu2_d = st.selectbox("Milieu 2 - Lame (n2) :", liste_milieux, index=2, key="var_choix_milieu2_double", disabled=st.session_state.opt4_verrouille)
    milieu3_d = st.selectbox("Milieu 3 (n3) :", liste_milieux, index=0, key="var_choix_milieu3_double", disabled=st.session_state.opt4_verrouille)    
  

    # Rendu du second schema de la double refraction en dessous
    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    fig_double_dioptre = dessiner_double_refraction_lame_matplotlib()
    st.pyplot(fig_double_dioptre, use_container_width=True)
    
    # Boîte blanche flottante mémorisée dans la session
    st.info(st.session_state.get("opt4_txt_box_double", "Ajustez les curseurs pour initialiser la lame."))
    st.markdown("---")

    liste_q_opt3, liste_t_opt3 = afficher_questions_optique3(
        verrouille=st.session_state.get("opt3_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt3 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 3.",
        key="check_certif_opt3_officiel_20pts",
        disabled=st.session_state.get("opt3_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_opt3_official_20pts", use_container_width=True, disabled=st.session_state.get("opt3_verrouille", False)):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_quiz_opt3 = sum(1.0 for qid, _, _, rep in liste_q_opt3 if st.session_state.get(f"col_g_quiz_opt3_{qid}") == rep)
            score_trous_opt3 = sum(1.0 for _, _, rep, cle in liste_t_opt3 if st.session_state.get(cle) == rep)

            st.session_state.score_opt3_p1 = round(score_quiz_opt3, 1)
            st.session_state.score_opt3_p2 = round(score_trous_opt3, 1)
            st.session_state.score_final_opt3 = round(score_quiz_opt3 + score_trous_opt3, 1)
            st.session_state.opt3_verrouille = True
            st.rerun()

    if st.session_state.get("opt3_verrouille", False):
        scr1 = st.session_state.get("score_opt3_p1", 0.0)
        scr2 = st.session_state.get("score_opt3_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt3", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 3 SCELLE ET VALIDE | Note : {tot_s} / 20")

        html_export_opt3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 3 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Atelier 3 : Double refraction | Scelle le : {timestamp_opt3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores - Optique 3</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire Double Refraction : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DOUBLE REFRACTION (10 PTS)</div>
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

        for idx_t, (qid, enonce_q, _, attendu) in enumerate(liste_q_opt3, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt3_{qid}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt3 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt3 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div>
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

        for enonce_t, _, attendu_t, cle_t in liste_t_opt3:
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt3 += f"<tr><td style='text-align: left;'>{enonce_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align: center;'>{v_lbl_t}</td></tr>"

        html_export_opt3 += """
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
            data=html_export_opt3,
            file_name=f"Bilan_Optique3_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("**Réflexion totale : application à la fibre optique**")

    st.markdown("<p style='color:#38bdf8; font-weight:bold; margin-bottom:2px;'>- PHÉNOMÈNE DE RÉFLEXION TOTALE INTERNE</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #0284c7; margin-top: 0; font-size: 16px;">Conditions de la réflexion totale interne et guidage dans une fibre optique :</p>
        <ul style="margin-bottom: 0; line-height: 1.6;">
            <li><strong>Condition d'indices :</strong> La réflexion totale ne peut se produire que lorsque la lumière passe d'un milieu plus réfringent vers un milieu moins réfringent (<b><i>n</i><sub>1</sub> &gt; <i>n</i><sub>2</sub></b>, par exemple du verre vers l'air ou du cœur vers la gaine).</li>
            <li><strong>Angle critique (<i>i</i><sub>c</sub>) :</strong> Lorsque l'angle de réfraction atteint 90° (rayon rasant), l'angle d'incidence vaut <b>sin(<i>i</i><sub>c</sub>) = <i>n</i><sub>2</sub> / <i>n</i><sub>1</sub></b>.</li>
            <li><strong>Réflexion totale (<i>i</i> &gt; <i>i</i><sub>c</sub>) :</strong> Dès que l'angle d'incidence dépasse l'angle critique, plus aucun rayon ne traverse l'interface. <b>100 % de la lumière est réfléchie</b> à l'intérieur du cœur de la fibre sans perte d'énergie.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélecteurs pour la réflexion totale directe (Source en bas)
    choix_lampe_refl = st.selectbox("Source lumineuse (Réflexion totale) :", liste_lampes, key="var_choix_lampe_refl", index=0)
    
    col_refl1, col_refl2 = st.columns(2)
    with col_refl1:
        milieu_bas = st.selectbox("Milieu inférieur (dense, n1) :", liste_milieux, index=2, key="var_choix_milieu_bas") # Ex: Verre Couronne
    with col_refl2:
        milieu_haut = st.selectbox("Milieu supérieur (léger, n2) :", liste_milieux, index=0, key="var_choix_milieu_haut") # Ex: Air
        
    angle_incidence_bas = st.slider("Angle d'incidence depuis le bas (i) (°) :", min_value=0.0, max_value=90.0, value=50.0, step=0.5, key="var_angle_incidence_bas")

    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # Rendu du schéma de la Réflexion Totale
    fig_refl_totale = dessiner_reflexion_totale_directe_matplotlib()
    st.pyplot(fig_refl_totale, use_container_width=True)

    # Boîte blanche d'information pour la réflexion totale
    st.info(st.session_state.get("opt4_txt_box_refl_totale", "Ajustez les curseurs pour initialiser la simulation de réflexion totale."))

    st.markdown("---") # Ligne de séparation visuelle entre les deux ateliers


    st.markdown("<p style='color:#38bdf8; font-weight:bold; margin-bottom:2px;'> LA FIBRE OPTIQUE PRO</p>", unsafe_allow_html=True)
    
    # 1. Sélection des composants et de la lampe
    choix_lampe_fibre = st.selectbox("Source lumineuse (Fibre) :", liste_lampes, key="var_choix_lampe_fibre", index=0)
    
    col_fibre1, col_fibre2 = st.columns(2)
    with col_fibre1:
        # Configuration des indices du cœur et de la gaine
        n_coeur = st.slider("Indice de réfraction du Cœur (n1) :", min_value=1.40, max_value=1.80, value=1.52, step=0.01, key="var_n_coeur")
    with col_fibre2:
        n_gaine = st.slider("Indice de réfraction de la Gaine (n2) :", min_value=1.30, max_value=1.45, value=1.40, step=0.01, key="var_n_gaine")

    # 2. Réglages des propriétés du rayon lumineux
    angle_injection = st.slider("Angle d'incidence externe (i1) (°) :", min_value=0.0, max_value=85.0, value=25.0, step=0.5, key="var_angle_injection_externe")
    nb_rebonds = st.slider("Nombre maximum de rebonds :", min_value=1, max_value=8, value=4, step=1, key="var_nb_rebonds")

    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # 3. Rendu du schéma Matplotlib de la fibre optique avancée
    fig_fibre = dessiner_fibre_optique_avancee_matplotlib()
    st.pyplot(fig_fibre, use_container_width=True)

    # 4. Boîte d'information mémorisée dans la session
    st.info(st.session_state.get("opt4_txt_box_fibre", "Ajustez les curseurs pour initialiser la simulation de la fibre optique."))     
    st.markdown("---")

    liste_q_opt4, liste_t_opt4 = afficher_questions_optique4(
        verrouille=st.session_state.get("opt4_fibre_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 4")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt4 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 4.",
        key="check_certif_opt4_officiel_20pts",
        disabled=st.session_state.get("opt4_fibre_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_opt4_official_20pts", use_container_width=True, disabled=st.session_state.get("opt4_fibre_verrouille", False)):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt4:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_quiz_opt4 = sum(1.0 for qid, _, _, rep in liste_q_opt4 if st.session_state.get(f"col_g_quiz_opt4_{qid}") == rep)
            score_trous_opt4 = sum(1.0 for _, _, rep, cle in liste_t_opt4 if st.session_state.get(cle) == rep)

            st.session_state.score_opt4_p1 = round(score_quiz_opt4, 1)
            st.session_state.score_opt4_p2 = round(score_trous_opt4, 1)
            st.session_state.score_final_opt4 = round(score_quiz_opt4 + score_trous_opt4, 1)
            st.session_state.opt4_fibre_verrouille = True
            st.rerun()

    if st.session_state.get("opt4_fibre_verrouille", False):
        scr1 = st.session_state.get("score_opt4_p1", 0.0)
        scr2 = st.session_state.get("score_opt4_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt4", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt4 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER OPTIQUE 4 SCELLE ET VALIDE | Note : {tot_s} / 20")

        html_export_opt4 = f"""<!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Rapport Optique 4 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Atelier 4 : Reflexion totale & Fibre optique | Scelle le : {timestamp_opt4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif des scores - Optique 4</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8;">
                &bull; Partie 1 : Questionnaire Fibre Optique : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>
            <div class="sub-title">PARTIE 1 : QUIZ FIBRE OPTIQUE (10 PTS)</div>
            <table><thead><tr><th>N°</th><th>Question posée</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>
        """

        for idx_t, (qid, enonce_q, _, attendu) in enumerate(liste_q_opt4, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt4_{qid}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt4 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_opt4 += """</tbody></table><div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div><table><thead><tr><th>Phrase explicative à trous</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>"""

        for enonce_t, _, attendu_t, cle_t in liste_t_opt4:
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt4 += f"<tr><td>{enonce_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align:center;'>{v_lbl_t}</td></tr>"

        html_export_opt4 += """</tbody></table><div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">Laboratoire d'Optique Physique Appliquee &copy; 2026</div></body></html>"""

        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt4,
            file_name=f"Bilan_Optique4_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



with tab5:
    st.header("Applications de la réfraction dans le domaine de la maintenance")

    def dessiner_schema_explicatif_maint(type_app, couleur_faisceau="#ef4444"):
        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.invert_yaxis()
        ax.axis("off")

        if type_app == "refractometre":
            ax.add_patch(patches.Polygon([(20, 45), (80, 45), (70, 75), (30, 75)], facecolor="#38bdf8", alpha=0.25, edgecolor="#38bdf8", lw=1.5))
            ax.add_patch(patches.Rectangle((25, 35), 50, 10, facecolor="#eab308", alpha=0.5, edgecolor="#fde047"))
            ax.text(50, 30, "Film fluide industriel (n2)", color="#fde047", fontsize=8, ha="center")
            ax.text(50, 62, "Prisme verre (n1 > n2)", color="#38bdf8", fontsize=8, ha="center")
            ax.annotate("", xy=(50, 45), xytext=(25, 85), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.annotate("", xy=(75, 85), xytext=(50, 45), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.text(50, 93, "Réflexion totale à partir de l'angle limite ic", color="#cbd5e1", fontsize=7.5, ha="center")

        elif type_app == "voyant_niveau":
            ax.add_patch(patches.Polygon([(30, 20), (30, 80), (65, 50)], facecolor="#e0f2fe", alpha=0.2, edgecolor="#94a3b8", lw=1.5))
            ax.add_patch(patches.Rectangle((65, 15), 25, 70, facecolor="#f59e0b", alpha=0.25, edgecolor="none"))
            ax.text(77, 50, "Huile\n(n=1,46)\nou Air\n(n=1,00)", color="#fbbf24", fontsize=7.5, ha="center", va="center")
            ax.annotate("", xy=(50, 37), xytext=(10, 37), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.annotate("", xy=(50, 63), xytext=(50, 37), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2, ls="--"))
            ax.annotate("", xy=(10, 63), xytext=(50, 63), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2, ls="--"))
            ax.annotate("", xy=(85, 25), xytext=(50, 37), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
            ax.text(45, 92, "Air = Réflexion (brillant) | Huile = Réfraction (noir)", color="#cbd5e1", fontsize=7.5, ha="center")

        else: # endoscope_fibre
            ax.add_patch(patches.Rectangle((10, 25), 80, 50, facecolor="#38bdf8", alpha=0.08, edgecolor="#475569"))
            ax.add_patch(patches.Rectangle((10, 35), 80, 30, facecolor="#e0f2fe", alpha=0.2, edgecolor="#38bdf8"))
            ax.text(50, 20, "Gaine optique (n2 = 1,40)", color="#94a3b8", fontsize=7.5, ha="center")
            ax.text(50, 50, "Cœur (n1 = 1,52)", color="#38bdf8", fontsize=8, ha="center", va="center")
            ax.annotate("", xy=(30, 35), xytext=(10, 50), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.annotate("", xy=(55, 65), xytext=(30, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.annotate("", xy=(80, 35), xytext=(55, 65), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.text(50, 88, "Guidage par réflexions totales (i > ic)", color="#10b981", fontsize=8, ha="center")

        return fig

    APPLICATIONS_MAINTENANCE = {
        "refractometre": {
            "titre": "Le Réfractomètre d'Atelier (Contrôle des fluides de coupe et glycol)",
            "description": """
            **Principe :** Un réfractomètre portatif mesure l'angle limite de réfraction d'une goutte de fluide d'usinage ou de liquide de refroidissement posée sur un prisme en verre.
            Plus la concentration en huile soluble ou en glycol augmente, plus l'indice de réfraction $n$ s'élève (de $1,33$ à $1,42$), déplaçant la limite claire/sombre sur l'échelle graduée en **degrés Brix**.
            """,
            "image_filename": "maint_refractometre.jpg"
        },
        "voyant_niveau": {
            "titre": "Le Voyant de Niveau Optique Conique sur Centrale Hydraulique",
            "description": """
            **Principe :** Un cône transparent à 90° ($n = 1,50$) est monté sur la paroi d'un réservoir. Quand le niveau est bas, le cône est au contact de l'**air** ($n = 1,00$) : la lumière subit une **réflexion totale interne** et le voyant brille.
            Lorsque l'**huile** ($n = 1,46$) immerge le cône, les indices sont proches : la lumière est **réfractée dans l'huile** et le voyant devient noir.
            """,
            "image_filename": "maint_voyant_niveau.jpg"
        },
        "endoscope_fibre": {
            "titre": "L'Endoscope Industriel à Fibres Optiques (Contrôle Non Destructif)",
            "description": """
            **Principe :** Pour inspecter l'intérieur d'une turbine, d'un moteur ou d'une canalisation sans démontage, l'endoscope guide la lumière dans des **fibres optiques** souples.
            Grâce à un cœur d'indice $n_1 = 1,52$ entouré d'une gaine d'indice $n_2 = 1,40$, la lumière reste piégée par **réflexion totale interne** même dans les coudes.
            """,
            "image_filename": "maint_endoscope_fibre.jpg"
        }
    }

    if "app_maint_choisie" not in st.session_state:
        st.session_state.app_maint_choisie = "refractometre"

    if st.button("Générer une application maintenance au hasard", key="btn_rand_maint_ref"):
        choix_possibles = [c for c in APPLICATIONS_MAINTENANCE.keys() if c != st.session_state.app_maint_choisie]
        st.session_state.app_maint_choisie = random.choice(choix_possibles)
        st.rerun()

    app_m_active = APPLICATIONS_MAINTENANCE[st.session_state.app_maint_choisie]
    st.subheader(app_m_active["titre"])

    col_m_txt, col_m_vis = st.columns(2)
    with col_m_txt:
        st.markdown(app_m_active["description"])
        st.markdown("**Schéma optique de principe :**")
        fig_maint_ref = dessiner_schema_explicatif_maint(st.session_state.app_maint_choisie)
        st.pyplot(fig_maint_ref, use_container_width=True)

    with col_m_vis:
        try:
            st.image(app_m_active["image_filename"], caption="Illustration en situation réelle", use_container_width=True)
        except Exception:
            st.warning(f"Fichier image {app_m_active['image_filename']} introuvable dans le dossier.")

    st.markdown("---")

    dict_quiz_opt5, dict_trous_opt5 = afficher_questions_optique5(
        verrouille=st.session_state.get("opt5_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 5")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    cas_m_actif = st.session_state.get("app_maint_choisie", "refractometre")

    case_certif_opt5 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 5.",
        key="check_certif_opt5_officiel_20pts",
        disabled=st.session_state.get("opt5_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_opt5_official_20pts", use_container_width=True, disabled=st.session_state.get("opt5_verrouille", False)):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt5:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            rep_quiz_m = {
                "refractometre": {"m1": "L'indice de réfraction n", "m2": "Élevé", "m3": "Degré Brix (%)", "m4": "Eau distillée", "m5": "Corrosion", "m6": "Mince uniforme", "m7": "Réfraction limite", "m8": "La température", "m9": "Gel", "m10": "Supérieur"},
                "voyant_niveau": {"v1": "Noir / sombre", "v2": "Brillant / argenté", "v3": "Réflexion totale interne", "v4": "90°", "v5": "Réfraction dans l'huile", "v6": "Inférieur", "v7": "Supérieur", "v8": "Mobile mécanique", "v9": "Appoint d'huile", "v10": "Snell-Descartes"},
                "endoscope_fibre": {"e1": "Réflexion totale interne", "e2": "Supérieur", "e3": "Critique (limite)", "e4": "Gaine", "e5": "Acceptance", "e6": "Destructif", "e7": "Éclairage", "e8": "Noir fixe", "e9": "Numérique", "e10": "Aubes de turbines"}
            }
            rep_trous_m = {
                "refractometre": {"t1_opt5": "réfraction", "t2_opt5": "distillée", "t3_opt5": "Brix", "t4_opt5": "élevé", "t5_opt5": "supérieur", "t6_opt5": "limite", "t7_opt5": "température", "t8_opt5": "glycol", "t9_opt5": "corrosion", "t10_opt5": "mince"},
                "voyant_niveau": {"t1_opt5": "conique", "t2_opt5": "réflexion", "t3_opt5": "brillant", "t4_opt5": "réfractée", "t5_opt5": "noir", "t6_opt5": "45", "t7_opt5": "proche", "t8_opt5": "mobile", "t9_opt5": "appoint", "t10_opt5": "Snell"},
                "endoscope_fibre": {"t1_opt5": "fibres", "t2_opt5": "supérieur", "t3_opt5": "réflexion", "t4_opt5": "destructif", "t5_opt5": "critique", "t6_opt5": "gaine", "t7_opt5": "numérique", "t8_opt5": "noir", "t9_opt5": "turbines", "t10_opt5": "froide"}
            }

            sc_q5 = sum(1.0 for k, v in rep_quiz_m[cas_m_actif].items() if st.session_state.get(f"col_g_quiz_opt5_{cas_m_actif}_{k}") == v)
            sc_t5 = sum(1.0 for k, v in rep_trous_m[cas_m_actif].items() if st.session_state.get(f"opt5_{k}") == v)

            st.session_state.score_opt5_p1 = round(sc_q5, 1)
            st.session_state.score_opt5_p2 = round(sc_t5, 1)
            st.session_state.score_final_opt5 = round(sc_q5 + sc_t5, 1)
            st.session_state.opt5_verrouille = True
            st.rerun()

    if st.session_state.get("opt5_verrouille", False):
        scr1 = st.session_state.get("score_opt5_p1", 0.0)
        scr2 = st.session_state.get("score_opt5_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt5", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt5 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 5 SCELLE ET VALIDE | Note : {tot_s} / 20")

        rep_quiz_m = {
            "refractometre": {"m1": "L'indice de réfraction n", "m2": "Élevé", "m3": "Degré Brix (%)", "m4": "Eau distillée", "m5": "Corrosion", "m6": "Mince uniforme", "m7": "Réfraction limite", "m8": "La température", "m9": "Gel", "m10": "Supérieur"},
            "voyant_niveau": {"v1": "Noir / sombre", "v2": "Brillant / argenté", "v3": "Réflexion totale interne", "v4": "90°", "v5": "Réfraction dans l'huile", "v6": "Inférieur", "v7": "Supérieur", "v8": "Mobile mécanique", "v9": "Appoint d'huile", "v10": "Snell-Descartes"},
            "endoscope_fibre": {"e1": "Réflexion totale interne", "e2": "Supérieur", "e3": "Critique (limite)", "e4": "Gaine", "e5": "Acceptance", "e6": "Destructif", "e7": "Éclairage", "e8": "Noir fixe", "e9": "Numérique", "e10": "Aubes de turbines"}
        }

        rep_trous_m = {
            "refractometre": {"t1_opt5": "réfraction", "t2_opt5": "distillée", "t3_opt5": "Brix", "t4_opt5": "élevé", "t5_opt5": "supérieur", "t6_opt5": "limite", "t7_opt5": "température", "t8_opt5": "glycol", "t9_opt5": "corrosion", "t10_opt5": "mince"},
            "voyant_niveau": {"t1_opt5": "conique", "t2_opt5": "réflexion", "t3_opt5": "brillant", "t4_opt5": "réfractée", "t5_opt5": "noir", "t6_opt5": "45", "t7_opt5": "proche", "t8_opt5": "mobile", "t9_opt5": "appoint", "t10_opt5": "Snell"},
            "endoscope_fibre": {"t1_opt5": "fibres", "t2_opt5": "supérieur", "t3_opt5": "réflexion", "t4_opt5": "destructif", "t5_opt5": "critique", "t6_opt5": "gaine", "t7_opt5": "numérique", "t8_opt5": "noir", "t9_opt5": "turbines", "t10_opt5": "froide"}
        }

        dict_q_m_actif = rep_quiz_m[cas_m_actif]
        dict_t_m_actif = rep_trous_m[cas_m_actif]

        html_export_opt5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 5 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Cas maintenance etudie : {cas_m_actif.upper()} | Scelle le : {timestamp_opt5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores - Optique 5 (Maintenance)</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire d'application maintenance : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ MAINTENANCE INDUSTRIELLE (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Question</th>
                        <th style="width: 35%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 35%; text-align: center;">Attendu</th>
                        <th style="width: 20%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_q, (q_id, attendu) in enumerate(dict_q_m_actif.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt5_{cas_m_actif}_{q_id}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt5 += f"<tr><td>Question {idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_opt5 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 15%;">Trou</th>
                        <th style="width: 35%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 35%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_t in range(1, 11):
            t_key = f"t{idx_t}_opt5"
            saisie_t = st.session_state.get(f"opt5_{t_key}", "Choisir...")
            attendu_t = dict_t_m_actif.get(t_key, "Inconnu")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt5 += f"<tr><td>Trou {idx_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align:center;'>{v_lbl_t}</td></tr>"

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
            file_name=f"Bilan_Optique5_{n_eleve}_{cas_m_actif}.html",
            mime="text/html",
            use_container_width=True
        )


            



with tab6:
    st.header("Applications de la réfraction dans le domaine des TP")

    def dessiner_schema_explicatif_tp(type_app, couleur_faisceau="#ef4444"):
        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.invert_yaxis()
        ax.axis("off")

        if type_app == "nivellement_atm":
            ax.add_patch(patches.Rectangle((0, 82), 100, 18, facecolor="#f59e0b", alpha=0.25, edgecolor="none"))
            ax.plot(list((0, 100)), list((82, 82)), color="#f59e0b", lw=1.5)
            ax.text(50, 93, "Sol / Enrobé surchauffé (air chaud, n plus faible)", color="#fbbf24", fontsize=7.5, ha="center")
            ax.plot(list((12, 88)), list((45, 45)), color="#64748b", lw=1.2, ls="--")
            ax.text(50, 39, "Visée théorique rectiligne", color="#94a3b8", fontsize=7, ha="center")
            xs = [float(x) for x in range(12, 89)]
            ys = [45 + 0.012 * ((x - 12) ** 1.65) / 10.0 for x in xs]
            ax.plot(xs, ys, color=couleur_faisceau, lw=2.5)
            ax.text(50, 68, "Rayon réel courbé par réfraction atmosphérique", color=couleur_faisceau, fontsize=7.5, ha="center")

        elif type_app == "adjuvant_beton":
            ax.add_patch(patches.Polygon([(20, 45), (80, 45), (70, 75), (30, 75)], facecolor="#38bdf8", alpha=0.25, edgecolor="#38bdf8", lw=1.5))
            ax.add_patch(patches.Rectangle((25, 35), 50, 10, facecolor="#22c55e", alpha=0.45, edgecolor="#86efac"))
            ax.text(50, 29, "Adjuvant antigel béton (n2)", color="#86efac", fontsize=8, ha="center")
            ax.text(50, 62, "Prisme optique (n1 > n2)", color="#38bdf8", fontsize=8, ha="center")
            ax.annotate("", xy=(50, 45), xytext=(25, 85), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.annotate("", xy=(75, 85), xytext=(50, 45), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.text(50, 93, "Mesure du dosage en degrés Brix via l'angle limite", color="#cbd5e1", fontsize=7.5, ha="center")

        else: # camera_reseau
            ax.add_patch(patches.Rectangle((8, 22), 84, 56, facecolor="#475569", alpha=0.25, edgecolor="#94a3b8", lw=1.5))
            ax.text(50, 15, "Canalisation d'assainissement enterrée", color="#cbd5e1", fontsize=8, ha="center")
            ax.add_patch(patches.Rectangle((12, 46), 30, 8, facecolor="#38bdf8", alpha=0.4, edgecolor="#38bdf8"))
            ax.text(27, 40, "Fibre optique", color="#38bdf8", fontsize=7.5, ha="center")
            ax.annotate("", xy=(82, 30), xytext=(42, 50), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2))
            ax.annotate("", xy=(82, 70), xytext=(42, 50), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2))
            ax.text(65, 88, "Éclairage fibré + Objectif réfractif grand angle", color="#fde047", fontsize=7.5, ha="center")

        return fig

    APPLICATIONS_TP = {
        "nivellement_atm": {
            "titre": "La Réfraction Atmosphérique en Nivellement Longue Portée",
            "description": """
            **Principe :** Sur les grands chantiers de voirie ou de terrassement, le soleil chauffe fortement l'enrobé ou le sol, créant des couches d'air d'indice $n$ variable avec la hauteur.
            Le faisceau optique du niveau ou du laser s'incurve progressivement par **réfraction**, ce qui fausse les lectures de cote sur la mire si l'on ne se place pas à égale distance des points visés.
            """,
            "image_filename": "tp_nivellement_refraction.jpg"
        },
        "adjuvant_beton": {
            "titre": "Le Contrôle des Adjuvants Béton et Émulsions au Réfractomètre",
            "description": """
            **Principe :** Avant de couler un ouvrage d'art par temps froid, le chef de chantier contrôle la concentration de l'antigel béton ou de l'émulsion routière grâce à un **réfractomètre de chantier**.
            La mesure de l'angle limite de réfraction indique immédiatement le pourcentage en **degrés Brix** et garantit la résistance au gel.
            """,
            "image_filename": "tp_refractometre_chantier.jpg"
        },
        "camera_reseau": {
            "titre": "L'Inspection Télévisée des Réseaux Enterrés par Fibres Optiques",
            "description": """
            **Principe :** Avant le remblaiement d'une tranchée d'assainissement, une caméra poussée par jonc fibré inspecte l'intérieur des collecteurs.
            Les **fibres optiques** transportent la lumière par **réflexion totale interne**, tandis que les lentilles réfractives de l'objectif adaptent le champ de vision dans l'air et sous l'eau.
            """,
            "image_filename": "tp_camera_canalisation.jpg"
        }
    }

    if "app_tp_choisie" not in st.session_state:
        st.session_state.app_tp_choisie = "nivellement_atm"

    if st.button("Générer une application Travaux Publics au hasard", key="btn_rand_tp_ref"):
        choix_possibles = [c for c in APPLICATIONS_TP.keys() if c != st.session_state.app_tp_choisie]
        st.session_state.app_tp_choisie = random.choice(choix_possibles)
        st.rerun()

    app_tp_active = APPLICATIONS_TP[st.session_state.app_tp_choisie]
    st.subheader(app_tp_active["titre"])

    col_tp_txt, col_tp_vis = st.columns(2)
    with col_tp_txt:
        st.markdown(app_tp_active["description"])
        st.markdown("**Schéma optique de principe :**")
        fig_tp_ref = dessiner_schema_explicatif_tp(st.session_state.app_tp_choisie)
        st.pyplot(fig_tp_ref, use_container_width=True)

    with col_tp_vis:
        try:
            st.image(app_tp_active["image_filename"], caption="Illustration en situation réelle", use_container_width=True)
        except Exception:
            st.warning(f"Fichier image {app_tp_active['image_filename']} introuvable dans le dossier.")

    st.markdown("---")

    dict_quiz_opt6, dict_trous_opt6 = afficher_questions_optique6(
        verrouille=st.session_state.get("opt6_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 6")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    cas_tp_actif = st.session_state.get("app_tp_choisie", "nivellement_atm")

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
            rep_quiz_tp = {
                "nivellement_atm": {"tp1": "Réfraction atmosphérique", "tp2": "Faible", "tp3": "Curviligne (courbe)", "tp4": "Faussée (trop basse sur la mire)", "tp5": "Égale distance des deux mires", "tp6": "En plein après-midi sous fort soleil", "tp7": "Le gradient thermique y est maximal", "tp8": "Pression (densité)", "tp9": "Droite", "tp10": "Snell-Descartes"},
                "adjuvant_beton": {"ad1": "Un réfractomètre optique", "ad2": "Indice de réfraction n", "ad3": "Augmente", "ad4": "Critique (limite)", "ad5": "De l'eau propre (distillée)", "ad6": "Degré Brix (%)", "ad7": "Une ou deux gouttes", "ad8": "Supérieur", "ad9": "Gel du béton frais", "ad10": "Indice de réfraction"},
                "camera_reseau": {"ca1": "Fibres optiques", "ca2": "Réflexion totale interne", "ca3": "Supérieur", "ca4": "S'échapper dans la gaine", "ca5": "Réfraction à travers des lentilles", "ca6": "Se rétrécit (angle réfracté plus petit)", "ca7": "L'écart d'indice verre/eau est plus faible que verre/air", "ca8": "Snell-Descartes", "ca9": "Une fissure ou un joint déboîté", "ca10": "Critique (limite)"}
            }
            rep_trous_tp = {
                "nivellement_atm": {"t1_opt6": "faible", "t2_opt6": "réfraction", "t3_opt6": "curviligne", "t4_opt6": "mire", "t5_opt6": "distance", "t6_opt6": "sol", "t7_opt6": "température", "t8_opt6": "droite", "t9_opt6": "après-midi", "t10_opt6": "Snell"},
                "adjuvant_beton": {"t1_opt6": "réfractomètre", "t2_opt6": "réfraction", "t3_opt6": "augmente", "t4_opt6": "Brix", "t5_opt6": "eau", "t6_opt6": "limite", "t7_opt6": "supérieur", "t8_opt6": "gel", "t9_opt6": "température", "t10_opt6": "conforme"},
                "camera_reseau": {"t1_opt6": "fibres", "t2_opt6": "réflexion", "t3_opt6": "supérieur", "t4_opt6": "réfraction", "t5_opt6": "rétrécit", "t6_opt6": "supérieur", "t7_opt6": "critique", "t8_opt6": "gaine", "t9_opt6": "fissure", "t10_opt6": "Snell"}
            }

            sc_q6 = sum(1.0 for k, v in rep_quiz_tp[cas_tp_actif].items() if st.session_state.get(f"col_g_quiz_opt6_{cas_tp_actif}_{k}") == v)
            sc_t6 = sum(1.0 for k, v in rep_trous_tp[cas_tp_actif].items() if st.session_state.get(f"opt6_{k}") == v)

            st.session_state.score_opt6_p1 = round(sc_q6, 1)
            st.session_state.score_opt6_p2 = round(sc_t6, 1)
            st.session_state.score_final_opt6 = round(sc_q6 + sc_t6, 1)
            st.session_state.opt6_verrouille = True
            st.rerun()

    if st.session_state.get("opt6_verrouille", False):
        scr1 = st.session_state.get("score_opt6_p1", 0.0)
        scr2 = st.session_state.get("score_opt6_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt6", 0.0)
        from datetime import datetime, timedelta
        from datetime import datetime, timedelta
        timestamp_opt6 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER OPTIQUE 6 SCELLE ET VALIDE | Note : {tot_s} / 20")

        rep_quiz_tp = {
            "nivellement_atm": {"tp1": "Réfraction atmosphérique", "tp2": "Faible", "tp3": "Curviligne (courbe)", "tp4": "Faussée (trop basse sur la mire)", "tp5": "Égale distance des deux mires", "tp6": "En plein après-midi sous fort soleil", "tp7": "Le gradient thermique y est maximal", "tp8": "Pression (densité)", "tp9": "Droite", "tp10": "Snell-Descartes"},
            "adjuvant_beton": {"ad1": "Un réfractomètre optique", "ad2": "Indice de réfraction n", "ad3": "Augmente", "ad4": "Critique (limite)", "ad5": "De l'eau propre (distillée)", "ad6": "Degré Brix (%)", "ad7": "Une ou deux gouttes", "ad8": "Supérieur", "ad9": "Gel du béton frais", "ad10": "Indice de réfraction"},
            "camera_reseau": {"ca1": "Fibres optiques", "ca2": "Réflexion totale interne", "ca3": "Supérieur", "ca4": "S'échapper dans la gaine", "ca5": "Réfraction à travers des lentilles", "ca6": "Se rétrécit (angle réfracté plus petit)", "ca7": "L'écart d'indice verre/eau est plus faible que verre/air", "ca8": "Snell-Descartes", "ca9": "Une fissure ou un joint déboîté", "ca10": "Critique (limite)"}
        }
        rep_trous_tp = {
            "nivellement_atm": {"t1_opt6": "faible", "t2_opt6": "réfraction", "t3_opt6": "curviligne", "t4_opt6": "mire", "t5_opt6": "distance", "t6_opt6": "sol", "t7_opt6": "température", "t8_opt6": "droite", "t9_opt6": "après-midi", "t10_opt6": "Snell"},
            "adjuvant_beton": {"t1_opt6": "réfractomètre", "t2_opt6": "réfraction", "t3_opt6": "augmente", "t4_opt6": "Brix", "t5_opt6": "eau", "t6_opt6": "limite", "t7_opt6": "supérieur", "t8_opt6": "gel", "t9_opt6": "température", "t10_opt6": "conforme"},
            "camera_reseau": {"t1_opt6": "fibres", "t2_opt6": "réflexion", "t3_opt6": "supérieur", "t4_opt6": "réfraction", "t5_opt6": "rétrécit", "t6_opt6": "supérieur", "t7_opt6": "critique", "t8_opt6": "gaine", "t9_opt6": "fissure", "t10_opt6": "Snell"}
        }

        html_export_opt6 = f"""<!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Rapport Optique 6 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Cas Travaux Publics etudie : {cas_tp_actif.upper()} | Scelle le : {timestamp_opt6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif des scores - Optique 6 (Travaux Publics)</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8;">
                &bull; Partie 1 : Questionnaire Travaux Publics : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>
            <div class="sub-title">PARTIE 1 : QUIZ TRAVAUX PUBLICS (10 PTS)</div>
            <table><thead><tr><th>Question</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>
        """

        for idx_q, (q_id, attendu) in enumerate(rep_quiz_tp[cas_tp_actif].items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt6_{cas_tp_actif}_{q_id}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt6 += f"<tr><td>Question {idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_opt6 += """</tbody></table><div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div><table><thead><tr><th>Trou</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>"""

        for idx_t in range(1, 11):
            t_key = f"t{idx_t}_opt6"
            saisie_t = st.session_state.get(f"opt6_{t_key}", "Choisir...")
            attendu_t = rep_trous_tp[cas_tp_actif].get(t_key, "Inconnu")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt6 += f"<tr><td>Trou {idx_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align:center;'>{v_lbl_t}</td></tr>"

        html_export_opt6 += """</tbody></table><div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">Laboratoire d'Optique Physique Appliquee &copy; 2026</div></body></html>"""

        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt6,
            file_name=f"Bilan_Optique6_{n_eleve}_{cas_tp_actif}.html",
            mime="text/html",
            use_container_width=True
        )


with tab7:
    st.header("**Applications de la réfraction dans le domaine routier")
    
    import random
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    def dessiner_schema_explicatif_routier(type_application, couleur_faisceau="#ef4444"):
        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.invert_yaxis()
        ax.axis("off")
        
        if type_application == "catadioptre":
            # Structure du prisme
            x_prisme = [45, 85, 45]
            y_prisme = [15, 45, 75]
            ax.fill(x_prisme, y_prisme, facecolor="#38bdf8", alpha=0.15, edgecolor="#475569", lw=1.5)
            
            x_entree = [45, 45]
            y_entree = [15, 75]
            ax.plot(x_entree, y_entree, color="#94a3b8", lw=2)
            
            # Trajectoire du rayon lumineux
            ax.annotate("", xy=(65, 35), xytext=(5, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(65, 55), xytext=(65, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(5, 55), xytext=(65, 55), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            
            ax.text(35, 28, "Entrée", color="#94a3b8", fontsize=8)
            ax.text(70, 45, "Réflexions\ntotales (2x)", color="#cbd5e1", fontsize=8, ha="left", va="center")
            
        elif type_application == "mirage":
            ax.add_patch(patches.Rectangle((0, 85), 100, 15, facecolor="#f59e0b", alpha=0.25, edgecolor="none"))
            
            x_sol = [0, 100]
            y_sol = [85, 85]
            ax.plot(x_sol, y_sol, color="#f59e0b", lw=1.5)
            ax.text(50, 95, "Bitume chaud (n plus faible)", color="#f59e0b", fontsize=8, ha="center")
            
            x_vals = [float(x) for x in range(5, 95)]
            y_vals = [25 + 0.0075 * (x - 50)**2 for x in x_vals]
            ax.plot(x_vals, y_vals, color=couleur_faisceau, lw=2.5)
            
            ax.annotate("", xy=(30, 28), xytext=(10, 37), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=0, mutation_scale=12))
            ax.annotate("", xy=(90, 37), xytext=(70, 28), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=0, mutation_scale=12))
            
            x_norm = [50, 50]
            y_norm = [60, 85]
            ax.plot(x_norm, y_norm, color="#64748b", linestyle=":", lw=1)
            ax.text(50, 55, "Réflexion totale\nprogressive", color="#cbd5e1", fontsize=8, ha="center")
            
        elif type_application == "capteur_pluie":
            ax.add_patch(patches.Rectangle((5, 35), 90, 25, facecolor="#e0f2fe", alpha=0.15, edgecolor="#475569", lw=1.5))
            ax.text(10, 48, "Verre du pare-brise", color="#94a3b8", fontsize=8)
            
            goutte = patches.Wedge((50, 35), 14, 180, 360, facecolor="#38bdf8", alpha=0.5, edgecolor="#0284c7")
            ax.add_patch(goutte)
            ax.text(50, 25, "Goutte de pluie", color="#38bdf8", fontsize=8, ha="center")
            
            ax.annotate("", xy=(50, 35), xytext=(20, 75), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(60, 10), xytext=(50, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=1.5, linestyle="--"))
            ax.annotate("", xy=(80, 75), xytext=(50, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=1.5, alpha=0.4))
            
            ax.text(32, 60, "Faisceau LED", color=couleur_faisceau, fontsize=7, rotation=35)
            ax.text(54, 52, "Réflexion brisée", color="#cbd5e1", fontsize=8)
            
        elif type_application == "panneau_signalisation":
            # Reconstruction géométrique propre à base de listes indépendantes
            y_h = [45, 25, 45]
            for i in range(4):
                offset = 15 + i * 20
                x_h = [offset, offset + 10, offset + 20]
                ax.fill(x_h, y_h, facecolor="#10b981", alpha=0.1, edgecolor="#10b981", lw=1)
            
            ax.annotate("", xy=(40, 30), xytext=(15, 85), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(25, 85), xytext=(45, 30), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            
            ax.text(50, 70, "Retour du faisceau\nvers le conducteur", color="#cbd5e1", fontsize=8, ha="center")
            ax.text(50, 15, "Revêtement microprismatique", color="#10b981", fontsize=8, ha="center")
            
        return fig

    # --- BASE DE DONNÉES DES APPLICATIONS ROUTIÈRES ---
    APPLICATIONS_ROUTIERES = {
        "catadioptre": {
            "titre": "Le Catadioptre (Rétroréflecteur)",
            "description": """
            **Principe :** Les catadioptres situés à l'arrière des véhicules ou sur les balises de virage utilisent des prismes d'angle droit (coins de cube). 
            La lumière des phares d'une voiture entre par la face avant, subit **deux réflexions totales internes successives à 90°** sur les parois intérieures, et repart *exactement* dans la même direction vers les yeux du conducteur. 
            Cela permet de rendre les obstacles extrêmement visibles la nuit sans consommer d'électricité.
            """,
            "image_filename": "catadioptre_routier.jpg"
        },
        "mirage": {
            "titre": "Le Mirage Routier (Effet de flaque d'eau)",
            "description": """
            **Principe :** En été, le soleil chauffe intensément le bitume, ce qui crée une couche d'air très chaud (et donc moins dense, avec un indice de réfraction plus faible) juste au-dessus de la route. L'air plus haut reste plus frais (indice plus élevé).
            Les rayons lumineux du ciel descendent vers le sol et passent d'un milieu plus réfringent à un milieu moins réfringent. L'angle critique est dépassé : le rayon subit une **réflexion totale interne curviligne** juste avant de toucher le sol et remonte vers l'œil du conducteur. Celui-ci croit voir le ciel se refléter sur la route, donnant l'illusion d'une flaque d'eau.
            """,
            "image_filename": "mirage_routier.jpg"
        },
        "capteur_pluie": {
            "titre": "Le Capteur de Pluie automatique",
            "description": """
            **Principe :** Placé derrière le rétroviseur central, un émetteur LED envoie de la lumière dans le pare-brise avec un angle calculé pour qu'il y ait **réflexion totale interne** sur la face externe du verre sec. La lumière est normalement réfléchie à 100 % vers un récepteur.
            Dès que des gouttes de pluie tombent sur le pare-brise, l'eau (indice n = 1,33) modifie les conditions optiques par rapport à l'air (n = 1,00). L'angle critique change, la réflexion totale est brisée : une partie de la lumière s'échappe dans la goutte d'eau. Le récepteur reçoit moins de lumière et déclenche automatiquement les essuie-glaces !
            """,
            "image_filename": "capteur_pluie_routier.jpg"
        },
        "panneau_signalisation": {
            "titre": "Les Panneaux de Signalisation Rétroréflecteurs",
            "description": """
            **Principe :** Le revêtement des panneaux de signalisation routière modernes n'est pas un simple miroir, mais un film plastique composé de millions de **microprismes transparents**.
            La lumière des phares pénètre dans chaque microprisme et subit une série de **réflexions totales internes** sur les facettes arrières. Grâce à la géométrie rigoureuse des prismes, les rayons lumineux sont renvoyés de manière concentrée vers leur source (la voiture) plutôt que d'être dispersés dans la nature. Le panneau semble alors s'illuminer sous l'effet des phares.
            """,
            "image_filename": "panneau_signalisation_routier.jpg"
        }
    }

    if "app_routiere_choisie" not in st.session_state:
        st.session_state.app_routiere_choisie = "catadioptre"

    # Bouton pour générer une application au hasard
    if st.button("Générer une application routière au hasard"):
        choix_possibles = list(APPLICATIONS_ROUTIERES.keys())
        choix_filtrés = [c for c in choix_possibles if c != st.session_state.app_routiere_choisie]
        st.session_state.app_routiere_choisie = random.choice(choix_filtrés)
        st.rerun()

    app_active = APPLICATIONS_ROUTIERES[st.session_state.app_routiere_choisie]

    st.subheader(app_active["titre"])
    
    # Utilisation stricte de st.columns(2) pour éviter le bug safe_columns
    col_texte, col_visualisation = st.columns(2)
    
    with col_texte:
        st.markdown(app_active["description"])
        st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        # Récupération dynamique de la couleur globale de la source lumineuse
        couleur_faisceau_bouton = "#ef4444"
        if "var_choix_lampe_simple" in st.session_state and "lampes_data" in st.session_state:
            lampe_sel = st.session_state.var_choix_lampe_simple
            if lampe_sel in st.session_state.lampes_data:
                couleur_faisceau_bouton = st.session_state.lampes_data[lampe_sel]["couleur_source"]

        # Affichage du schéma vectoriel Matplotlib
        st.markdown("**Schéma optique de principe :**")
        fig_routier = dessiner_schema_explicatif_routier(st.session_state.app_routiere_choisie, couleur_faisceau=couleur_faisceau_bouton)
        st.pyplot(fig_routier, use_container_width=True)

    with col_visualisation:
        try:
            st.image(app_active["image_filename"], caption="Illustration en situation réelle", use_container_width=True)
        except Exception:
            st.warning(f"Fichier image {app_active['image_filename']} introuvable dans le dossier.")  

    st.markdown("---")
    
    # Appel de la fonction pour générer et afficher les questions à l'écran
    dict_quiz_opt7, dict_trous_opt7 = afficher_questions_optique7(
        verrouille=st.session_state.get("opt7_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 7")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    cas_actif = st.session_state.get("app_routiere_choisie", "catadioptre")

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
            # 1. BASE DE CORRECTION DYNAMIQUE DU QUIZ (PARTIE 1 : 10 POINTS)
            reponses_attendues_quiz = {
                "catadioptre": {
                    "c1": "Parallèle à l'axe incident", "c2": "Coin de cube (angle droit)", "c3": "90°", 
                    "c4": "Réflexion totale interne", "c5": "180° (demi-tour complet)", "c6": "Supérieur à l'angle critique", 
                    "c7": "Passif (sans consommation électrique)", "c8": "Parallèles", "c9": "S'échapper par réfraction", "c10": "Rouge"
                },
                "mirage": {
                    "m1": "Flaque d'eau", "m2": "Chaud", "m3": "Faible", "m4": "Faible", 
                    "m5": "U inversé (courbe montante)", "m6": "Angle critique (limite)", "m7": "Ciel", 
                    "m8": "Curviligne (courbe)", "m9": "Inversée (reflétée)", "m10": "Homogène"
                },
                "capteur_pluie": {
                    "p1": "Rétroviseur central", "p2": "Infrarouge (invisible)", "p3": "Réflexion totale interne", 
                    "p4": "Supérieur à l'angle critique", "p5": "100% (intensité maximale)", "p6": "Air (n = 1.00)", 
                    "p7": "Critique (limite)", "p8": "Brisée (rompue)", "p9": "S'échapper dans la goutte", "p10": "Essuie-glaces"
                },
                "panneau_signalisation": {
                    "s1": "Film plastique technique", "s2": "Microprismes transparents", "s3": "La voiture d'origine (la source)", 
                    "s4": "Rétroréflexion", "s5": "Totales internes", "s6": "Phares", "s7": "Ciel ou environnement", 
                    "s8": "Air", "s9": "Angle limite dépassé", "s10": "Sécurité routière"
                }
            }

            dictionnaire_quiz_actif = reponses_attendues_quiz[cas_actif]
            score_quiz_opt7 = 0.0
            for qk, qv in dictionnaire_quiz_actif.items():
                cle_saisie = f"col_g_quiz_opt7_{cas_actif}_{qk}"
                if st.session_state.get(cle_saisie) == qv:
                    score_quiz_opt7 += 1.0
            
            score_quiz_opt7 = min(10.0, round(score_quiz_opt7, 1))

            # 2. BASE DE CORRECTION DYNAMIQUE DES TROUS (PARTIE 2 : 10 POINTS)
            reponses_attendues_trous = {
                "catadioptre": {
                    "t1_opt7": "Phares", "t2_opt7": "Avant", "t3_opt7": "Prismes", "t4_opt7": "Droit", "t5_opt7": "Incident",
                    "t6_opt7": "Réflexions", "t7_opt7": "Totales", "t8_opt7": "Internes", "t9_opt7": "Parallèle", "t10_opt7": "Conducteur"
                },
                "mirage": {
                    "t1_opt7": "Soleil", "t2_opt7": "Bitume", "t3_opt7": "Chaud", "t4_opt7": "Faible", "t5_opt7": "Supérieures",
                    "t6_opt7": "Réfringent", "t7_opt7": "Critique", "t8_opt7": "Totale", "t9_opt7": "Ciel", "t10_opt7": "Illusion"
                },
                "capteur_pluie": {
                    "t1_opt7": "Diode", "t2_opt7": "Verre", "t3_opt7": "Supérieur", "t4_opt7": "Air", "t5_opt7": "Totale",
                    "t6_opt7": "Récepteur", "t7_opt7": "Gouttes", "t8_opt7": "Eau", "t9_opt7": "Brisée", "t10_opt7": "Essuie-glaces"
                },
                "panneau_signalisation": {
                    "t1_opt7": "Film", "t2_opt7": "Microprismes", "t3_opt7": "Phares", "t4_opt7": "Transparents", "t5_opt7": "Facettes",
                    "t6_opt7": "Interne", "t7_opt7": "Supérieur", "t8_opt7": "Source", "t9_opt7": "Luminosité", "t10_opt7": "Sécurité routière"
                }
            }

            dict_t_actif = reponses_attendues_trous[cas_actif]
            score_trous_opt7 = 0.0
            for tk, tv in dict_t_actif.items():
                if st.session_state.get(f"opt7_{tk}") == tv:
                    score_trous_opt7 += 1.0

            st.session_state.score_opt7_p1 = round(score_quiz_opt7, 1)
            st.session_state.score_opt7_p2 = round(score_trous_opt7, 1)
            st.session_state.score_final_opt7 = round(score_quiz_opt7 + score_trous_opt7, 1)
            st.session_state.opt7_verrouille = True
            st.rerun()

    # BLOC PERMANENT D'AFFICHAGE DU RAPPORT HTML APRÈS VERROUILLAGE
    if st.session_state.get("opt7_verrouille", False):
        scr1 = st.session_state.get("score_opt7_p1", 0.0)
        scr2 = st.session_state.get("score_opt7_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt7", 0.0)

        from datetime import datetime, timedelta
        timestamp_opt7 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 7 SCELLE ET VALIDE | Note : {tot_s} / 20")

        # --- CORRECTION : RE-DÉCLARATION LOCALE DES DICTIONNAIRES POUR LA BOUCLE HTML ---
        reponses_attendues_quiz = {
            "catadioptre": {
                "c1": "Parallèle à l'axe incident", "c2": "Coin de cube (angle droit)", "c3": "90°", 
                "c4": "Réflexion totale interne", "c5": "180° (demi-tour complet)", "c6": "Supérieur à l'angle critique", 
                "c7": "Passif (sans consommation électrique)", "c8": "Parallèles", "c9": "S'échapper par réfraction", "c10": "Rouge"
            },
            "mirage": {
                "m1": "Flaque d'eau", "m2": "Chaud", "m3": "Faible", "m4": "Faible", 
                "m5": "U inversé (courbe montante)", "m6": "Angle critique (limite)", "m7": "Ciel", 
                "m8": "Curviligne (courbe)", "m9": "Inversée (reflétée)", "m10": "Homogène"
            },
            "capteur_pluie": {
                "p1": "Rétroviseur central", "p2": "Infrarouge (invisible)", "p3": "Réflexion totale interne", 
                "p4": "Supérieur à l'angle critique", "p5": "100% (intensité maximale)", "p6": "Air (n = 1.00)", 
                "p7": "Critique (limite)", "p8": "Brisée (rompue)", "p9": "S'échapper dans la goutte", "p10": "Essuie-glaces"
            },
            "panneau_signalisation": {
                "s1": "Film plastique technique", "s2": "Microprismes transparents", "s3": "La voiture d'origine (la source)", 
                "s4": "Rétroréflexion", "s5": "Totales internes", "s6": "Phares", "s7": "Ciel ou environnement", 
                "s8": "Air", "s9": "Angle limite dépassé", "s10": "Sécurité routière"
            }
        }
        

        
        reponses_attendues_trous = {
            "catadioptre": {
                "t1_opt7": "Phares", "t2_opt7": "Avant", "t3_opt7": "Prismes", "t4_opt7": "Droit", "t5_opt7": "Incident",
                "t6_opt7": "Réflexions", "t7_opt7": "Totales", "t8_opt7": "Internes", "t9_opt7": "Parallèle", "t10_opt7": "Conducteur"
            },
            "mirage": {
                "t1_opt7": "Soleil", "t2_opt7": "Bitume", "t3_opt7": "Chaud", "t4_opt7": "Faible", "t5_opt7": "Supérieures",
                "t6_opt7": "Réfringent", "t7_opt7": "Critique", "t8_opt7": "Totale", "t9_opt7": "Ciel", "t10_opt7": "Illusion"
            },
            "capteur_pluie": {
                "t1_opt7": "Diode", "t2_opt7": "Verre", "t3_opt7": "Supérieur", "t4_opt7": "Air", "t5_opt7": "Totale",
                "t6_opt7": "Récepteur", "t7_opt7": "Gouttes", "t8_opt7": "Eau", "t9_opt7": "Brisée", "t10_opt7": "Essuie-glaces"
            },
            "panneau_signalisation": {
                "t1_opt7": "Film", "t2_opt7": "Microprismes", "t3_opt7": "Phares", "t4_opt7": "Transparents", "t5_opt7": "Facettes",
                "t6_opt7": "Interne", "t7_opt7": "Supérieur", "t8_opt7": "Source", "t9_opt7": "Luminosité", "t10_opt7": "Sécurité routière"
            }
        }

        
        dict_textes_questions_quiz = {
            "catadioptre": {
                "c1": "Un catadioptre sert a renvoyer les rayons lumineux de facon :",
                "c2": "La forme geometrique interne utilisee dans un catadioptre est un :",
                "c3": "Les facettes arriere du catadioptre forment entre elles un angle de :",
                "c4": "Le retour de la lumiere s'effectue sans miroir grace au phenomene de :",
                "c5": "Apres deux reflexions successives a 90 degres, la deviation totale vaut :",
                "c6": "Pour que le dispositif fonctionne, l'angle d'impact sur la facette doit etre :",
                "c7": "Le grand avantage du catadioptre par rapport a une lampe classique est qu'il est :",
                "c8": "Dans le repere d'un prisme droit, les rayons incidents et emergents sont :",
                "c9": "Si le materiau du catadioptre possede un indice trop faible, la lumiere va :",
                "c10": "Sur la route, les catadioptres équipent obligatoirement l'arriere des véhicules en :"
            },
            "mirage": {
                "m1": "Le mirage routier donne l'illusion visuelle de la présence d'une :",
                "m2": "En ete, la forte chaleur emise par le bitume rend l'air en surface tres :",
                "m3": "Cet air fortement chauffe possede une densite plus :",
                "m4": "L'indice de refraction de la couche d'air au ras du sol devient donc plus :",
                "m5": "Le gradient d'indice genere des couches d'air qui font courber la trajectoire en :",
                "m6": "La reflexion totale progressive se produit car l'angle d'incidence finit par dépasser l' :",
                "m7": "Les rayons lumineux qui subissent cette courbe proviennent initialement du :",
                "m8": "Puisque l'indice varie continuellement avec l'altitude, la trajectoire finale est :",
                "m9": "L'oeil du conducteur prolonge la trajectoire rectilignement et voit une image :",
                "m10": "Ce phenomene montre que la lumiere ne se propage en ligne droite que si le milieu est :"
            },
            "capteur_pluie": {
                "p1": "Le capteur de pluie automatique d'une automobile est generalement place derriere le :",
                "p2": "La source lumineuse utilisee par l'emetteur is une LED fonctionnant en :",
                "p3": "Lorsque le pare-brise est sec, le faisceau lumineux subit sur la face externe une :",
                "p4": "L'angle d'injection initial de la LED dans le verre est calcule pour etre :",
                "p5": "Dans des conditions seches, la quantite de lumiere renvoyee au recepteur vaut environ :",
                "p6": "L'indice de refraction de l'eau (n = 1.33) est superieur a celui de l' :",
                "p7": "L'arrivee d'eau sur le pare-brise modifie la valeur de l'angle :",
                "p8": "Lorsque la condition aux limites change a cause de la pluie, la reflexion totale est :",
                "p9": "Une fraction importante de l'intensite lumineuse infrarouge va alors :",
                "p10": "La baisse de signal electrique mesuree par la photodiode declenche l'action des :"
            },
            "panneau_signalisation": {
                "s1": "Le revetement brillant des panneaux de signalisation routiere modernes est un :",
                "s2": "Ce film plastique technique renferme une multitude de structures nommees :",
                "s3": "Contrairement a un miroir classique, le panneau de signalisation renvoie le flux vers :",
                "s4": "Cette capacite particuliere a renvoyer la lumiere vers sa source s'appelle la :",
                "s5": "A l'interieur d'un microprisme, les rayons subissent une serie de reflexions :",
                "s6": "La surface du panneau semble s'illuminer fortement des que la voiture allume ses :",
                "s7": "La directivite du faisceau evite de disperser inutilement l'energie vers le :",
                "s8": "La condition de guidage impose que l'indice du plastique soit superieur a celui de l' :",
                "s9": "Les facettes microscopiques arriere agissent comme des miroirs parfaits grace a l' :",
                "s10": "Pour l'automobiliste de nuit, ce systeme passif apporte un gain majeur en termes de :"
            }
        }



        dict_textes_trous_synthese = {
            "catadioptre": {
                "t1_opt7": "1. Le catadioptre routier utilise un bloc plastique constitue de petits [Trou 1]...",
                "t2_opt7": "2. ...tailles en angle droit. Le faisceau lumineux des phares y subit une [Trou 2]...",
                "t3_opt7": "3. ...qui est qualifiée de totale car toute l'intensité est renvoyée dans le milieu [Trou 3]...",
                "t4_opt7": "4. ...sans aucune perte. Les rebonds successifs dévient le rayon d'un angle de [Trou 4]...",
                "t5_opt7": "5. ...sur chaque face interne. Le faisceau émergeant repart de facon [Trou 5]...",
                "t6_opt7": "6. ...par rapport à l'axe d'entrée. Ce retour rectiligne cible directement le [Trou 6]...",
                "t7_opt7": "7. ...de l'automobile. Ce système fonctionne la nuit de manière entièrement [Trou 7]...",
                "t8_opt7": "8. ...sans consommer de batterie. Pour être visible, l'indice du plastique doit être [Trou 8]...",
                "t9_opt7": "9. ...à l'indice extérieur de l' [Trou 9]...",
                "t10_opt7": "10. ...afin que la condition limite soit vérifiée pour la sécurité [Trou 10]"
            },
            "mirage": {
                "t1_opt7": "1. Le mirage routier apparaît en été lorsque la forte chaleur surchauffe le [Trou 1]...",
                "t2_opt7": "2. ...de la chaussée. Cela diminue localement la densité et l'indice de l' [Trou 2]...",
                "t3_opt7": "3. ...au ras du sol. L'indice de réfraction de cette zone devient très [Trou 3]...",
                "t4_opt7": "4. ...par rapport à l'air frais plus haut. Les rayons lumineux descendants du [Trou 4]...",
                "t5_opt7": "5. ...traversent un milieu d'indice continuellement décroissant. La trajectoire est [Trou 5]...",
                "t6_opt7": "6. ...car l'angle d'incidence augmente à chaque couche d'air jusqu'à dépasser l'angle [Trou 6]...",
                "t7_opt7": "7. ...On observe alors une réflexion totale progressive qui fait remonter le rayon vers l' [Trou 7]...",
                "t8_opt7": "8. ...de l'automobiliste. Le cerveau prolonge la direction finale et interprète une image [Trou 8]...",
                "t9_opt7": "9. ...de l'azur lointain sur l'asphalte, provoquant la spectaculaire [Trou 9]...",
                "t10_opt7": "10. ...d'une fausse flaque d'eau miroitante sur une route totalement [Trou 10]"
            },
            "capteur_pluie": {
                "t1_opt7": "1. Le capteur automatique d'essuyage est fixé directement contre le [Trou 1]...",
                "t2_opt7": "2. Une source émettrice produit un rayon invisible de nature [Trou 2]...",
                "t3_opt7": "3. Ce faisceau est injecté à l'intérieur de l'épaisseur du [Trou 3]...",
                "t4_opt7": "4. Tant que la surface extérieure reste parfaitement sèche, le contact avec l' [Trou 4]...",
                "t5_opt7": "5. ...d'indice n = 1.00 provoque au niveau du dioptre une réflexion [Trou 5]...",
                "t6_opt7": "6. ...interne. L'intégralité de l'énergie lumineuse est guidée vers le [Trou 6]...",
                "t7_opt7": "7. Mais lorsque des gouttes d'eau se déposent, l'indice externe passe à [Trou 7]...",
                "t8_opt7": "8. Cette élévation d'indice à l'interface modifie l'angle limite : la condition est [Trou 8]...",
                "t9_opt7": "9. Une partie de la lumière s'échappe. La photodiode mesure une forte [Trou 9]...",
                "t10_opt7": "10. ...d'intensité, ce qui commande l'enclenchement instantané des [Trou 10]"
            },
            "panneau_signalisation": {
                "t1_opt7": "1. La rétroréflexion nocturne des panneaux utilise un film plastique à [Trou 1]...",
                "t2_opt7": "2. Le faisceau lumineux provient directement des projecteurs de [Trou 2]...",
                "t3_opt7": "3. ...de la voiture. La lumière pénètre dans le polymère rigide de nature [Trou 3]...",
                "t4_opt7": "4. Elle rencontre les facettes microscopiques arrières de chaque prisme droit [Trou 4]...",
                "t5_opt7": "5. Le guidage interne parfait de l'intensité s'effectue par réflexion [Trou 5]...",
                "t6_opt7": "6. ...car la valeur d'incidence dépasse l'angle critique de l'interface avec l' [Trou 6]...",
                "t7_opt7": "7. Grâce à la structure géométrique, la lumière effectue un demi-tour [Trou 7]...",
                "t8_opt7": "8. Les rayons concentrés retournent vers le conducteur au lieu d'être [Trou 8]...",
                "t9_opt7": "9. ...dans l'espace ou vers le ciel. La surface du panneau semble posséder une forte [Trou 9]...",
                "t10_opt7": "10. ...apportant une aide indispensable pour assurer la sécurité [Trou 10]"
            }
        }

        dict_q_actif = reponses_attendues_quiz[cas_actif]
        dict_enonces_actif = dict_textes_questions_quiz[cas_actif]
        dict_phrases_actif = dict_textes_trous_synthese[cas_actif]

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
                <p style="font-size: 12px; opacity: 0.7;">Cas routier etudie : {cas_actif.upper()} | Scelle le : {timestamp_opt7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores - Optique 7</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire d'application routiere : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous thématique) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LES CONNAISSANCES ROUTIÈRES (10 PTS)</div>
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

        # Remplissage du tableau de la Partie 1 avec l'énoncé de la question
        for idx_t, (q_id, attendu) in enumerate(dict_q_actif.items(), 1):
            cle_saisie = f"col_g_quiz_opt7_{cas_actif}_{q_id}"
            saisie = st.session_state.get(cle_saisie, "Choisir...")
            enonce_q = dict_enonces_actif.get(q_id, "Question d'optique routière")
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"
            
        html_export_opt7 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div>
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

        reponses_trous_officiel = reponses_attendues_trous[cas_actif]
        for idx_t in range(1, 11):
            t_key = f"t{idx_t}_opt7"
            saisie = st.session_state.get(f"opt7_{t_key}", "Choisir...")
            attendu = reponses_trous_officiel.get(t_key, "Inconnu")
            phrase_q = dict_phrases_actif.get(t_key, f"Phrase {idx_t}")
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            
            # Injection de la variable phrase_q contenant l'énoncé de la question dans la première cellule
            html_export_opt7 += f"<tr><td style='text-align: left;'>{phrase_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">
                Laboratoire d'Optique Physique Appliquee &copy; 2026
            </div>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement pour l'élève
        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt7,
            file_name=f"Bilan_Optique7_{n_eleve}_{cas_actif}.html",
            mime="text/html",
            use_container_width=True
        )


with tab8:
    st.header("Applications de la réfraction dans le domaine géomètre topographe")

    def dessiner_schema_explicatif_geo(type_app, couleur_faisceau="#ef4444"):
        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.invert_yaxis()
        ax.axis("off")

        if type_app == "refraction_terrestre":
            ax.add_patch(patches.Rectangle((0, 80), 100, 20, facecolor="#365314", alpha=0.45, edgecolor="#4d7c0f"))
            ax.text(50, 92, "Surface terrestre (air dense, n ≈ 1,00029)", color="#a3e635", fontsize=7.5, ha="center")
            ax.text(50, 16, "Haute atmosphère (air moins dense, n → 1,00000)", color="#94a3b8", fontsize=7.5, ha="center")
            ax.plot(list((10, 90)), list((45, 45)), color="#64748b", lw=1.2, ls="--")
            xs = [float(x) for x in range(10, 91)]
            ys = [45 + 0.008 * ((x - 10) ** 1.7) / 10.0 for x in xs]
            ax.plot(xs, ys, color=couleur_faisceau, lw=2.5)
            ax.text(50, 68, "Courbure vers le bas (coefficient k ≈ 0,13)", color=couleur_faisceau, fontsize=7.5, ha="center")

        elif type_app == "constante_prisme":
            ax.add_patch(patches.Polygon([(45, 20), (85, 50), (45, 80)], facecolor="#38bdf8", alpha=0.25, edgecolor="#38bdf8", lw=1.5))
            ax.text(60, 50, "Verre\nn = 1,52", color="#38bdf8", fontsize=8, ha="center", va="center")
            ax.text(22, 25, "Air (n = 1,00)", color="#94a3b8", fontsize=7.5, ha="center")
            ax.annotate("", xy=(45, 38), xytext=(10, 38), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.annotate("", xy=(68, 38), xytext=(45, 38), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2))
            ax.annotate("", xy=(68, 62), xytext=(68, 38), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2))
            ax.annotate("", xy=(45, 62), xytext=(68, 62), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2))
            ax.annotate("", xy=(10, 62), xytext=(45, 62), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.2))
            ax.text(50, 92, "Ralentissement v = c / n → Constante de prisme", color="#fde047", fontsize=7.5, ha="center")

        else: # bathymetrie_lidar
            ax.add_patch(patches.Rectangle((0, 45), 100, 55, facecolor="#0284c7", alpha=0.25, edgecolor="#38bdf8"))
            ax.text(20, 38, "Air (n1 = 1,00)", color="#94a3b8", fontsize=7.5)
            ax.text(20, 56, "Eau (n2 = 1,33)", color="#38bdf8", fontsize=7.5)
            ax.plot(list((45, 45)), list((20, 88)), color="#64748b", lw=1, ls=":")
            ax.annotate("", xy=(45, 45), xytext=(22, 15), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2.5))
            ax.annotate("", xy=(60, 88), xytext=(45, 45), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2.5))
            ax.text(50, 95, "Laser vert 532 nm : réfraction air/eau (i2 < i1)", color="#86efac", fontsize=7.5, ha="center")

        return fig

    APPLICATIONS_GEOMETRE = {
        "refraction_terrestre": {
            "titre": "La Réfraction Atmosphérique Terrestre en Géodésie (k ≈ 0,13)",
            "description": """
            **Principe :** L'atmosphère terrestre est formée de couches d'air dont la densité et l'indice de réfraction diminuent avec l'altitude ($n \\approx 1,00029$ au sol vers $1,00000$ en altitude).
            La ligne de visée d'un théodolite ou d'une station totale s'incurve vers la Terre, obligeant le géomètre à appliquer une correction altimétrique sur les longues portées.
            """,
            "image_filename": "geo_refraction_atm.jpg"
        },
        "constante_prisme": {
            "titre": "La Réfraction dans le Prisme Topographique et la Constante de Prisme",
            "description": """
            **Principe :** Lorsque l'onde infrarouge de la station totale pénètre dans le prisme en verre ($n = 1,52$), sa vitesse ralentit ($v = c / n$).
            Ce trajet optique plus long dans le verre impose de paramétrer la **constante de prisme** (souvent $-34,4\\text{ mm}$) dans l'appareil pour garantir une mesure millimétrique.
            """,
            "image_filename": "geo_constante_prisme.jpg"
        },
        "bathymetrie_lidar": {
            "titre": "La Bathymétrie Laser Aéroportée (LiDAR Vert Air / Eau)",
            "description": """
            **Principe :** Pour cartographier le fond des rivières et des zones côtières, un scanner aéroporté émet un **laser vert (532 nm)** qui traverse la surface de l'eau ($n_2 = 1,33$).
            Le logiciel du géomètre applique la **loi de Snell-Descartes** pour corriger l'angle de réfraction et la vitesse du faisceau dans l'eau.
            """,
            "image_filename": "geo_bathymetrie_lidar.jpg"
        }
    }

    if "app_geo_choisie" not in st.session_state:
        st.session_state.app_geo_choisie = "refraction_terrestre"

    if st.button("Générer une application Géomètre Topographe au hasard", key="btn_rand_geo_ref"):
        choix_possibles = [c for c in APPLICATIONS_GEOMETRE.keys() if c != st.session_state.app_geo_choisie]
        st.session_state.app_geo_choisie = random.choice(choix_possibles)
        st.rerun()

    app_g_active = APPLICATIONS_GEOMETRE[st.session_state.app_geo_choisie]
    st.subheader(app_g_active["titre"])

    col_g_txt, col_g_vis = st.columns(2)
    with col_g_txt:
        st.markdown(app_g_active["description"])
        st.markdown("**Schéma optique de principe :**")
        fig_geo_ref = dessiner_schema_explicatif_geo(st.session_state.app_geo_choisie)
        st.pyplot(fig_geo_ref, use_container_width=True)

    with col_g_vis:
        try:
            st.image(app_g_active["image_filename"], caption="Illustration en situation réelle", use_container_width=True)
        except Exception:
            st.warning(f"Fichier image {app_g_active['image_filename']} introuvable dans le dossier.")

    st.markdown("---")

    dict_quiz_opt8, dict_trous_opt8 = afficher_questions_optique8(
        verrouille=st.session_state.get("opt8_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 8")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    cas_g_actif = st.session_state.get("app_geo_choisie", "refraction_terrestre")

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
            rep_quiz_g = {
                "refraction_terrestre": {"g1": "Augmente", "g2": "Le bas (la surface terrestre)", "g3": "0,13", "g4": "Altitude (denivelée)", "g5": "Rayonnement égal (portées égales)", "g6": "1,00029", "g7": "Température et pression atmosphérique", "g8": "Normale (verticale)", "g9": "Distance", "g10": "Snell-Descartes"},
                "constante_prisme": {"p1": "Diminue (v = c / n)", "p2": "Constante de prisme", "p3": "-34,4 mm (ou 0 mm)", "p4": "Plusieurs centimètres systématiquement", "p5": "Réfraction", "p6": "Réflexion totale interne", "p7": "1,52", "p8": "v = c / n", "p9": "Réflexion vitreuse parasite", "p10": "0 mm"},
                "bathymetrie_lidar": {"b1": "Vert (532 nm)", "b2": "La lumière verte pénètre profondément dans l'eau claire", "b3": "Réfraction", "b4": "Normale", "b5": "25 % (v ≈ 225 000 km/s)", "b6": "Surestimée (trop profonde de 33 %)", "b7": "Fond marin (lit de la rivière)", "b8": "Profondeur d'eau", "b9": "Inclinaison oblique constante (15° à 20°)", "b10": "Snell-Descartes"}
            }
            rep_trous_g = {
                "refraction_terrestre": {"t1_opt8": "altitude", "t2_opt8": "sol", "t3_opt8": "0.13", "t4_opt8": "altitude", "t5_opt8": "distance", "t6_opt8": "1.00029", "t7_opt8": "pression", "t8_opt8": "carré", "t9_opt8": "normale", "t10_opt8": "Snell"},
                "constante_prisme": {"t1_opt8": "diminue", "t2_opt8": "n", "t3_opt8": "constante", "t4_opt8": "-34.4", "t5_opt8": "réfraction", "t6_opt8": "réflexion", "t7_opt8": "1.52", "t8_opt8": "avant", "t9_opt8": "0", "t10_opt8": "Snell"},
                "bathymetrie_lidar": {"t1_opt8": "verte", "t2_opt8": "réfraction", "t3_opt8": "normale", "t4_opt8": "faible", "t5_opt8": "1.33", "t6_opt8": "fond", "t7_opt8": "surestimée", "t8_opt8": "oblique", "t9_opt8": "marins", "t10_opt8": "Snell"}
            }

            sc_q8 = sum(1.0 for k, v in rep_quiz_g[cas_g_actif].items() if st.session_state.get(f"col_g_quiz_opt8_{cas_g_actif}_{k}") == v)
            sc_t8 = sum(1.0 for k, v in rep_trous_g[cas_g_actif].items() if st.session_state.get(f"opt8_{k}") == v)

            st.session_state.score_opt8_p1 = round(sc_q8, 1)
            st.session_state.score_opt8_p2 = round(sc_t8, 1)
            st.session_state.score_final_opt8 = round(sc_q8 + sc_t8, 1)
            st.session_state.opt8_verrouille = True
            st.rerun()

    if st.session_state.get("opt8_verrouille", False):
        scr1 = st.session_state.get("score_opt8_p1", 0.0)
        scr2 = st.session_state.get("score_opt8_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt8", 0.0)
        from datetime import datetime, timedelta
        timestamp_opt8 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER OPTIQUE 8 SCELLE ET VALIDE | Note : {tot_s} / 20")

        rep_quiz_g = {
            "refraction_terrestre": {"g1": "Augmente", "g2": "Le bas (la surface terrestre)", "g3": "0,13", "g4": "Altitude (denivelée)", "g5": "Rayonnement égal (portées égales)", "g6": "1,00029", "g7": "Température et pression atmosphérique", "g8": "Normale (verticale)", "g9": "Distance", "g10": "Snell-Descartes"},
            "constante_prisme": {"p1": "Diminue (v = c / n)", "p2": "Constante de prisme", "p3": "-34,4 mm (ou 0 mm)", "p4": "Plusieurs centimètres systématiquement", "p5": "Réfraction", "p6": "Réflexion totale interne", "p7": "1,52", "p8": "v = c / n", "p9": "Réflexion vitreuse parasite", "p10": "0 mm"},
            "bathymetrie_lidar": {"b1": "Vert (532 nm)", "b2": "La lumière verte pénètre profondément dans l'eau claire", "b3": "Réfraction", "b4": "Normale", "b5": "25 % (v ≈ 225 000 km/s)", "b6": "Surestimée (trop profonde de 33 %)", "b7": "Fond marin (lit de la rivière)", "b8": "Profondeur d'eau", "b9": "Inclinaison oblique constante (15° à 20°)", "b10": "Snell-Descartes"}
        }
        rep_trous_g = {
            "refraction_terrestre": {"t1_opt8": "altitude", "t2_opt8": "sol", "t3_opt8": "0.13", "t4_opt8": "altitude", "t5_opt8": "distance", "t6_opt8": "1.00029", "t7_opt8": "pression", "t8_opt8": "carré", "t9_opt8": "normale", "t10_opt8": "Snell"},
            "constante_prisme": {"t1_opt8": "diminue", "t2_opt8": "n", "t3_opt8": "constante", "t4_opt8": "-34.4", "t5_opt8": "réfraction", "t6_opt8": "réflexion", "t7_opt8": "1.52", "t8_opt8": "avant", "t9_opt8": "0", "t10_opt8": "Snell"},
            "bathymetrie_lidar": {"t1_opt8": "verte", "t2_opt8": "réfraction", "t3_opt8": "normale", "t4_opt8": "faible", "t5_opt8": "1.33", "t6_opt8": "fond", "t7_opt8": "surestimée", "t8_opt8": "oblique", "t9_opt8": "marins", "t10_opt8": "Snell"}
        }

        html_export_opt8 = f"""<!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Rapport Optique 8 - {n_eleve}</title>
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
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Cas Geometre Topographe etudie : {cas_g_actif.upper()} | Scelle le : {timestamp_opt8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif des scores - Optique 8 (Geometre Topographe)</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8;">
                &bull; Partie 1 : Questionnaire Geometre Topographe : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>
            <div class="sub-title">PARTIE 1 : QUIZ GEOMETRE TOPOGRAPHE (10 PTS)</div>
            <table><thead><tr><th>Question</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>
        """

        for idx_q, (q_id, attendu) in enumerate(rep_quiz_g[cas_g_actif].items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt8_{cas_g_actif}_{q_id}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>Question {idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """</tbody></table><div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div><table><thead><tr><th>Trou</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr></thead><tbody>"""

        for idx_t in range(1, 11):
            t_key = f"t{idx_t}_opt8"
            saisie_t = st.session_state.get(f"opt8_{t_key}", "Choisir...")
            attendu_t = rep_trous_g[cas_g_actif].get(t_key, "Inconnu")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>Trou {idx_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align:center;'>{v_lbl_t}</td></tr>"

        html_export_opt8 += """</tbody></table><div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">Laboratoire d'Optique Physique Appliquee &copy; 2026</div></body></html>"""

        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt8,
            file_name=f"Bilan_Optique8_{n_eleve}_{cas_g_actif}.html",
            mime="text/html",
            use_container_width=True
        )




