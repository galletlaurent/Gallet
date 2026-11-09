# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application Réflexion ",
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
st.title("Application Réflexion")
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

    ax.text(25, 20, "ATELIER 2 - DOUBLE DIOPTRE ET TRAJECTOIRES", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
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
    ax.set_title("Atelier 4 : Releves sin(r) = f(sin(i))", color="#38bdf8", fontsize=8, style="italic")

    # Superposition permanente des points memorises (Croix vertes d'origine)
    m_sin_i = st.session_state.get("mesures_sin_i", [])
    m_sin_r = st.session_state.get("mesures_sin_r", [])
    
    if m_sin_i:
        ax.scatter(m_sin_i, m_sin_r, color="#10b981", marker="x", s=50, lw=2, label="Points mesures", zorder=5)
        ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="white", fontsize=7, loc="upper left")

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
            key="btn_validation_identité_maitre",
            disabled=st.session_state.get("vérrouillé", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("vérrouillé", False):
                st.rerun()


with tab2:
    
    st.header("Atelier  : Lois de Snell-Descartes ")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel des Formules Fondamentales de la Refraction :</p>
        <ul>
            <li><strong>Deuxieme loi de Snell-Descartes :</strong> $n_1 \\cdot \\sin(i_1) = n_2 \\cdot \\sin(i_2)$</li>
            <li><strong>Loi du double dioptre (Lame a faces paralleles) :</strong> Le rayon emergent sort de la lame avec un angle de deviation nul ($i_3 = i_1$) mais subit un <strong>decalage lateral $dx$</strong>.</li>
            <li><strong>Calcul de la pente :</strong> En tracant $\\sin(i_1)$ en fonction de $\\sin(i_2)$, la droite lineaire possede un coefficient directeur egal au rapport des indices $\\frac{n_2}{n_1}$.</li>
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



with tab3:
    st.header("**Manipulation  : Illusion d'optique (Affichage Tete Haute - HUD)**")
            

    st.markdown("<p style='color:#991b1b; font-weight:bold; margin-bottom:2px;'>2. DOUBLE REFRACTION</p>", unsafe_allow_html=True)
    
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

with tab4:
    st.header("**Manipulation : Conduite & Topographie (Simulation Retroviseurs)**")
            



with tab5:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")
            




with tab6:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")




with tab7:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")





with tab8:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")


