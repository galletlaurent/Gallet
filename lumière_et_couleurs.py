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
    "Décomposition de la lumière",
    "Les différentes lumières",
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

BANQUES_LUM_GEO = {
    0: {
        "questions": [
            {"id": "qlg0_1", "q": "Pourquoi les niveaux laser rotatifs et lasers d'intérieur modernes de chantier utilisent-ils une diode laser verte (532 nm) plutôt que rouge (635 nm) ?", "options": ["L'œil humain est environ 4 fois plus sensible au vert (532 nm) qu'au rouge en plein jour", "Le laser vert traverse les murs en béton", "Le laser vert consomme 10 fois moins d'énergie"], "rep": "L'œil humain est environ 4 fois plus sensible au vert (532 nm) qu'au rouge en plein jour"},
            {"id": "qlg0_2", "q": "À quelle longueur d'onde précise se situe le maximum de sensibilité diurne (vision photopique) de l'œil humain ?", "options": ["555 nm (jaune-vert)", "410 nm (violet)", "680 nm (rouge profond)"], "rep": "555 nm (jaune-vert)"},
            {"id": "qlg0_3", "q": "Comment qualifie-t-on la lumière émise par un laser topographique (une seule longueur d'onde très pure) ?", "options": ["Monochromatique et cohérente", "Polychromatique blanche", "Incohérente thermique"], "rep": "Monochromatique et cohérente"},
            {"id": "qlg0_4", "q": "Quel accessoire utilise le géomètre topographe sur le terrain pour repérer plus facilement le trait laser rouge ou vert en plein soleil ?", "options": ["Des lunettes filtrantes de la même couleur que le laser (qui bloquent les autres couleurs du soleil) ou une cellule de réception", "Des lunettes de soudure noires", "Un prisme de Newton"], "rep": "Des lunettes filtrantes de la même couleur que le laser (qui bloquent les autres couleurs du soleil) ou une cellule de réception"},
            {"id": "qlg0_5", "q": "Comment agissent les lunettes rouges portées par un géomètre travaillant avec un laser rouge 635 nm ?", "options": ["Par synthèse soustractive : elles absorbent le bleu et le vert du soleil et augmentent le contraste du trait rouge", "Elles amplifient la puissance du laser", "Elles transforment le rouge en vert"], "rep": "Par synthèse soustractive : elles absorbent le bleu et le vert du soleil et augmentent le contraste du trait rouge"},
            {"id": "qlg0_6", "q": "Quelle surface de chantier renvoie le mieux le faisceau d'un télémètre laser sans prisme ?", "options": ["Une façade claire mate à albédo élevé (enduit blanc ou béton clair)", "Une vitre inclinée ou un revêtement bitumineux noir", "Une flaque d'eau"], "rep": "Une façade claire mate à albédo élevé (enduit blanc ou béton clair)"},
            {"id": "qlg0_7", "q": "Pourquoi un télémètre laser sans prisme peine-t-il à mesurer la distance d'un bardage métallique noir mat ?", "options": ["Le noir mat absorbe la majorité de l'énergie lumineuse (faible albédo) et renvoie un signal très faible", "Le métal noir dévie la lumière à 90°", "La vitesse de la lumière diminue devant le noir"], "rep": "Le noir mat absorbe la majorité de l'énergie lumineuse (faible albédo) et renvoie un signal très faible"},
            {"id": "qlg0_8", "q": "Dans quel domaine spectral fonctionne le distancemètre électronique (EDM) d'une station totale mesurant sur un prisme à 2 kilomètres ?", "options": ["L'infrarouge proche (environ 850 nm, invisible à l'œil nu)", "L'ultraviolet lointain", "Le bleu à 450 nm"], "rep": "L'infrarouge proche (environ 850 nm, invisible à l'œil nu)"},
            {"id": "qlg0_9", "q": "Quelle classe de sécurité laser équipe la quasi-totalité des niveaux laser et stations totales de chantier ?", "options": ["Classe 2 (puissance < 1 mW, réflexe palpébral protecteur) ou Classe 3R", "Classe 4 (découpe industrielle)", "Classe 0"], "rep": "Classe 2 (puissance < 1 mW, réflexe palpébral protecteur) ou Classe 3R"},
            {"id": "qlg0_10", "q": "Quelle est la vitesse de propagation du faisceau laser dans l'atmosphère utilisée pour calculer les distances topographiques ?", "options": ["Environ 299 700 km/s (corrigée de l'indice de réfraction de l'air)", "340 m/s", "1 000 km/h"], "rep": "Environ 299 700 km/s (corrigée de l'indice de réfraction de l'air)"},
        ],
        "trous": [
            ("1. Un laser vert (532 nm) est environ ......... fois plus visible qu'un laser rouge de jour.", ["Choisir...", "4", "100"], "4", "lgeo_t1"),
            ("2. L'œil humain atteint son pic de sensibilité diurne autour de ......... nm.", ["Choisir...", "555", "700"], "555", "lgeo_t2"),
            ("3. La lumière d'un laser ne contient qu'une seule longueur d'onde : elle est .........", ["Choisir...", "monochromatique", "blanche"], "monochromatique", "lgeo_t3"),
            ("4. Les lunettes filtrantes rouges améliorent le contraste par synthèse .........", ["Choisir...", "soustractive", "additive"], "soustractive", "lgeo_t4"),
            ("5. Le distancemètre longue portée d'une station totale émet dans l'.........", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "lgeo_t5"),
            ("6. Une surface blanche mate possède un ......... élevé et renvoie bien le laser.", ["Choisir...", "albédo", "poids"], "albédo", "lgeo_t6"),
            ("7. Un revêtement noir mat ......... la majorité du faisceau laser incident.", ["Choisir...", "absorbe", "réfléchit"], "absorbe", "lgeo_t7"),
            ("8. Les lasers de chantier appartiennent généralement à la Classe ......... (< 1 mW).", ["Choisir...", "2", "4"], "2", "lgeo_t8"),
            ("9. La lumière se propage dans l'air à environ 300 000 ......... par seconde.", ["Choisir...", "kilomètres", "mètres"], "kilomètres", "lgeo_t9"),
            ("10. Sur un chantier très ensoleillé, on utilise une ......... de réception pour capter le laser.", ["Choisir...", "cellule", "loupe"], "cellule", "lgeo_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qlg1_1", "q": "Quel capteur embarqué sur un drone topographique permet d'analyser la santé des cultures, des forêts ou l'humidité des sols grâce aux couleurs invisibles ?", "options": ["Une caméra multispectrale (captant le Rouge, le Vert, le Bleu, le Red-Edge et le Proche Infrarouge)", "Un appareil photo noir et blanc", "Un simple microphone"], "rep": "Une caméra multispectrale (captant le Rouge, le Vert, le Bleu, le Red-Edge et le Proche Infrarouge)"},
            {"id": "qlg1_2", "q": "Pourquoi une végétation saine et bien irriguée apparaît-elle verte à l'œil nu ?", "options": ["La chlorophylle absorbe le bleu et le rouge pour la photosynthèse et réfléchit le vert", "La plante émet de la lumière verte la nuit", "La terre est bleue"], "rep": "La chlorophylle absorbe le bleu et le rouge pour la photosynthèse et réfléchit le vert"},
            {"id": "qlg1_3", "q": "Comment se comporte une feuille végétale en bonne santé dans le Proche Infrarouge (PIR, 750 - 900 nm) ?", "options": ["Elle réfléchit très fortement le proche infrarouge (réflectance > 50 %)", "Elle absorbe 100 % de l'infrarouge", "Elle devient transparente"], "rep": "Elle réfléchit très fortement le proche infrarouge (réflectance > 50 %)"},
            {"id": "qlg1_4", "q": "Comment appelle-t-on l'indice normalisé calculé par les géomètres à partir de la bande Rouge (R) et du Proche Infrarouge (PIR) : (PIR - R) / (PIR + R) ?", "options": ["L'indice NDVI (Normalized Difference Vegetation Index)", "L'indice IRC", "L'indice de réfraction n"], "rep": "L'indice NDVI (Normalized Difference Vegetation Index)"},
            {"id": "qlg1_5", "q": "Quelle valeur prend l'indice NDVI pour une végétation très dense et vigoureuse ?", "options": ["Proche de + 0,70 à + 0,90", "Négative (- 0,80)", "Égale à 0"], "rep": "Proche de + 0,70 à + 0,90"},
            {"id": "qlg1_6", "q": "Quelle valeur prend l'indice NDVI pour une surface d'eau libre (lac, rivière) qui absorbe fortement le proche infrarouge ?", "options": ["Une valeur négative (comprise entre - 1 et 0)", "Une valeur égale à + 1", "Une valeur de + 0,85"], "rep": "Une valeur négative (comprise entre - 1 et 0)"},
            {"id": "qlg1_7", "q": "Quelle valeur prend l'indice NDVI pour un sol nu, un parking en enrobé ou du béton ?", "options": ["Proche de 0 (entre 0,05 et 0,15)", "Égale à + 0,95", "Égale à - 0,90"], "rep": "Proche de 0 (entre 0,05 et 0,15)"},
            {"id": "qlg1_8", "q": "Quel panneau de référence le géomètre photographie-t-il au sol avant le décollage du drone multispectral ?", "options": ["Une mire de calibrage radiométrique (gris neutre étalonné) pour corriger l'ensoleillement du jour", "Un panneau stop", "Une mire de nivellement optique"], "rep": "Une mire de calibrage radiométrique (gris neutre étalonné) pour corriger l'ensoleillement du jour"},
            {"id": "qlg1_9", "q": "Comment appelle-t-on l'image aérienne assemblée et géoréférencée où chaque pixel possède ses vraies coordonnées (X, Y) ?", "options": ["Une orthophotographie (ou orthomosaïque)", "Un croquis à main levée", "Un profil en long"], "rep": "Une orthophotographie (ou orthomosaïque)"},
            {"id": "qlg1_10", "q": "En télédétection satellite ou drone, que signifie le sigle RVB (ou RGB) ?", "options": ["Rouge, Vert, Bleu (les trois canaux de la synthèse additive)", "Réseau, Voirie, Bâtiment", "Rayon, Vergence, Base"], "rep": "Rouge, Vert, Bleu (les trois canaux de la synthèse additive)"},
        ],
        "trous": [
            ("1. Une caméra ......... capte des bandes visibles et proches infrarouges par drone.", ["Choisir...", "multispectrale", "thermique seule"], "multispectrale", "lgeo_t1"),
            ("2. La chlorophylle des plantes ......... fortement la lumière rouge.", ["Choisir...", "absorbe", "réfléchit"], "absorbe", "lgeo_t2"),
            ("3. À l'inverse, une végétation saine réfléchit massivement le proche .........", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "lgeo_t3"),
            ("4. L'indice de végétation calculé par (PIR - R) / (PIR + R) s'appelle le .........", ["Choisir...", "NDVI", "IRC"], "NDVI", "lgeo_t4"),
            ("5. Pour une forêt dense, l'indice NDVI est élevé, proche de .........", ["Choisir...", "+ 0,80", "- 0,80"], "+ 0,80", "lgeo_t5"),
            ("6. Pour une étendue d'eau, l'indice NDVI est .........", ["Choisir...", "négatif", "égal à +1"], "négatif", "lgeo_t6"),
            ("7. Pour une route en béton ou enrobé, le NDVI est proche de .........", ["Choisir...", "0", "+ 0,90"], "0", "lgeo_t7"),
            ("8. Avant le vol, on calibre le capteur sur une mire ......... étalonnée.", ["Choisir...", "radiométrique", "acoustique"], "radiométrique", "lgeo_t8"),
            ("9. La carte aérienne assemblée et géoréférencée est une .........", ["Choisir...", "orthophotographie", "radiographie"], "orthophotographie", "lgeo_t9"),
            ("10. Les images couleurs classiques utilisent les trois canaux Rouge, Vert et .........", ["Choisir...", "Bleu", "Jaune"], "Bleu", "lgeo_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qlg2_1", "q": "Comment un scanner laser 3D terrestre (LiDAR topographique) génère-t-il un nuage de points colorisé réaliste d'un monument historique ?", "options": ["Il associe chaque mesure de distance laser (X, Y, Z) aux couleurs (R, V, B) capturées par un appareil photo calibré intégré", "Il peint le monument avec des lasers", "Il devine les couleurs au hasard"], "rep": "Il associe chaque mesure de distance laser (X, Y, Z) aux couleurs (R, V, B) capturées par un appareil photo calibré intégré"},
            {"id": "qlg2_2", "q": "Quelle propriété physique de la lumière utilise-t-on dans un distancemètre électro-optique de haute précision (précision millimétrique) ?", "options": ["La mesure du déphasage entre l'onde lumineuse modulée émise et l'onde réfléchie par le prisme", "La couleur de la batterie", "La température de la lentille"], "rep": "La mesure du déphasage entre l'onde lumineuse modulée émise et l'onde réfléchie par le prisme"},
            {"id": "qlg2_3", "q": "Pourquoi un prisme topographique (rétroréflecteur à coin de cube) renvoie-t-il toujours le faisceau lumineux exactement vers la station totale ?", "options": ["Grâce à trois réflexions totales internes successives sur ses trois faces perpendiculaires à 90°", "Parce qu'il contient un moteur électrique", "Par absorption sélective"], "rep": "Grâce à trois réflexions totales internes successives sur ses trois faces perpendiculaires à 90°"},
            {"id": "qlg2_4", "q": "Pourquoi la vitesse de la lumière dans l'air varie-t-elle légèrement selon la température, la pression atmosphérique et l'humidité (correction PPM) ?", "options": ["Parce que ces paramètres modifient l'indice de réfraction n de l'air (v = c / n)", "Parce que le laser s'use", "Parce que la Terre tourne"], "rep": "Parce que ces paramètres modifient l'indice de réfraction n de l'air (v = c / n)"},
            {"id": "qlg2_5", "q": "Que signifie l'acronyme PPM affiché dans les paramètres atmosphériques d'une station totale ?", "options": ["Parties Par Million (correction de distance en millimètres par kilomètre)", "Points Par Minute", "Prisme Pour Mire"], "rep": "Parties Par Million (correction de distance en millimètres par kilomètre)"},
            {"id": "qlg2_6", "q": "Lors de la colorisation RVB d'un nuage de points 3D par scanner, pourquoi faut-il éviter les forts contrastes ombre / plein soleil sur la façade ?", "options": ["Les écarts de luminosité créent des raccords de couleurs disgracieux sur le modèle 3D texturé", "Le laser ne fonctionne pas à l'ombre", "Le trépied glisse au soleil"], "rep": "Les écarts de luminosité créent des raccords de couleurs disgracieux sur le modèle 3D texturé"},
            {"id": "qlg2_7", "q": "Quelle grandeur appelée « intensité de réflectance » enregistre le scanner laser en plus des coordonnées (X, Y, Z) ?", "options": ["La puissance du signal laser renvoyé par chaque matériau (permettant de distinguer les marquages blancs de l'enrobé noir même de nuit)", "La masse de la façade", "L'âge du bâtiment"], "rep": "La puissance du signal laser renvoyé par chaque matériau (permettant de distinguer les marquages blancs de l'enrobé noir même de nuit)"},
            {"id": "qlg2_8", "q": "Quelle loi optique régit les trois réflexions totales à l'intérieur d'un prisme topographique à coin de cube ?", "options": ["Les lois de la réflexion et de la réfraction de Snell-Descartes", "La loi de Coulomb", "Le théorème de Pythagore"], "rep": "Les lois de la réflexion et de la réfraction de Snell-Descartes"},
            {"id": "qlg2_9", "q": "Si l'indice de réfraction n de l'air augmente (air froid et haute pression), comment évolue la vitesse de propagation v = c / n de l'onde lumineuse ?", "options": ["Elle diminue légèrement", "Elle augmente", "Elle devient infinie"], "rep": "Elle diminue légèrement"},
            {"id": "qlg2_10", "q": "Dans un scanner laser 3D, comment appelle-t-on l'ensemble des millions de points mesurés dans l'espace ?", "options": ["Un nuage de points 3D colorisé (Point Cloud)", "Un spectre de raies", "Un nivellement direct"], "rep": "Un nuage de points 3D colorisé (Point Cloud)"},
        ],
        "trous": [
            ("1. Un prisme topographique à coin de cube renvoie la lumière par ......... totale interne.", ["Choisir...", "réflexion", "absorption"], "réflexion", "lgeo_t1"),
            ("2. Ses trois faces réfléchissantes forment entre elles des angles de ......... degrés.", ["Choisir...", "90", "45"], "90", "lgeo_t2"),
            ("3. Le scanner 3D associe chaque point (X, Y, Z) aux trois couleurs Rouge, Vert et .........", ["Choisir...", "Bleu", "Jaune"], "Bleu", "lgeo_t3"),
            ("4. L'ensemble des mesures forme un ......... de points 3D colorisé.", ["Choisir...", "nuage", "spectre"], "nuage", "lgeo_t4"),
            ("5. La vitesse de la lumière dans l'air vaut v = c / .........", ["Choisir...", "n", "f"], "n", "lgeo_t5"),
            ("6. La température et la pression modifient l'......... de réfraction de l'air.", ["Choisir...", "indice", "albédo"], "indice", "lgeo_t6"),
            ("7. La correction atmosphérique des distances s'exprime en ......... (Parties Par Million).", ["Choisir...", "PPM", "LUX"], "PPM", "lgeo_t7"),
            ("8. Le distancemètre mesure le ......... entre l'onde émise et l'onde reçue.", ["Choisir...", "déphasage", "poids"], "déphasage", "lgeo_t8"),
            ("9. Même dans le noir, l'......... de réflectance permet de voir les bandes blanches au sol.", ["Choisir...", "intensité", "épaisseur"], "intensité", "lgeo_t9"),
            ("10. Les réflexions dans le prisme obéissent aux lois de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "lgeo_t10"),
        ]
    }
}


def mettre_a_jour_lum_geo_matplotlib(sujet_idx):
    """Banc d'essai optique Lumière & Couleurs adapté au Géomètre Topographe."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        coul_laser = st.session_state.get("radio_lgeo_s0", "Laser Vert Chantier (532 nm)")
        if "Rouge" in coul_laser:
            c_ray, sens_rel, portee_vis = "#ef4444", "25 % (Faible en plein soleil)", "35 m"
        else:
            c_ray, sens_rel, portee_vis = "#22c55e", "92 % (Proche du pic 555 nm)", "120 m"

        ax.add_patch(patches.Rectangle((55, 105), 80, 45, facecolor="#334155", edgecolor="white"))
        ax.text(95, 127, "Niveau\nLaser", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((135, 510)), list((127, 127)), color=c_ray, lw=4.5)
        ax.add_patch(patches.Rectangle((510, 65), 25, 125, facecolor="#cbd5e1", edgecolor="white"))
        ax.text(522, 205, "Mire / Mur", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "TOPOGRAPHIE DE CHANTIER : VISIBILITÉ DES LASERS ROUGE (635 NM) VS VERT (532 NM)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"{coul_laser}  |  Sensibilité œil humain : {sens_rel}  |  Portée visuelle : {portee_vis}", color=c_ray, fontsize=8, fontweight="bold")
        st.session_state.lgeo_mesure_courante = (coul_laser, sens_rel, f"Portée = {portee_vis}", "VISIBILITÉ MAX" if "Vert" in coul_laser else "LUNETTE ROUGE")

    elif sujet_idx == 1:
        surface = st.session_state.get("radio_lgeo_s1", "Végétation dense irriguée (Forêt / Culture)")
        if "Végétation" in surface:
            r_val, pir_val, c_zone = 0.08, 0.72, "#22c55e"
        elif "Sol" in surface:
            r_val, pir_val, c_zone = 0.28, 0.32, "#94a3b8"
        else:
            r_val, pir_val, c_zone = 0.12, 0.03, "#3b82f6"

        ndvi = round((pir_val - r_val) / (pir_val + r_val), 2)
        ax.add_patch(patches.Rectangle((220, 35), 160, 40, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(300, 55, "Drone Multispectral\n(Capteurs R + PIR)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.add_patch(patches.Rectangle((60, 175), 480, 45, facecolor=c_zone, edgecolor="white", lw=1.5))
        ax.text(300, 197, f"{surface}  =>  NDVI = {ndvi:+.2f}", color="white", fontsize=9, fontweight="bold", ha="center", va="center")

        ax.annotate("", xy=(250, 75), xytext=(220, 175), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
        ax.text(175, 125, f"Rouge réfléchi\nR = {r_val:.2f}", color="#fca5a5", fontsize=8, fontweight="bold", ha="center")

        ax.annotate("", xy=(350, 75), xytext=(380, 175), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=3))
        ax.text(435, 125, f"Proche IR réfléchi\nPIR = {pir_val:.2f}", color="#d8b4fe", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "TÉLÉDÉTECTION DRONE : CALCUL DE L'INDICE SPECTRAL NDVI = (PIR - R) / (PIR + R)", color="#38bdf8", fontsize=9, fontweight="bold")
        st.session_state.lgeo_mesure_courante = (surface.split("(")[0].strip(), f"R = {r_val:.2f}", f"PIR = {pir_val:.2f}", f"NDVI = {ndvi:+.2f}")

    else:
        temp_air = st.session_state.get("slider_lgeo_s2", 15.0)
        ppm = round((temp_air - 15.0) * 1.0, 1)
        dist_base = 1000.0
        dist_corr = round(dist_base + (ppm / 1000.0), 4)

        ax.add_patch(patches.Rectangle((55, 100), 90, 60, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(100, 130, "Station Totale\n(IR 850 nm)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((145, 495)), list((122, 122)), color="#ef4444", lw=2.5)
        ax.plot(list((495, 145)), list((138, 138)), color="#22c55e", lw=2.5, ls="--")

        ax.add_patch(patches.Polygon(list(((495, 130), (535, 100), (535, 160))), facecolor="#e0f2fe", edgecolor="#38bdf8", lw=2))
        ax.text(515, 178, "Prisme\nCoin de cube", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "DISTANCEMÈTRE LASER : RÉFLEXION TOTALE SUR PRISME ET CORRECTION ATMOSPHÉRIQUE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Température air = {temp_air:.0f} °C  |  Correction = {ppm:+.1f} ppm  =>  Distance corrigée = {dist_corr:.4f} m", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.lgeo_mesure_courante = (f"T = {temp_air:.0f} °C", f"Corr = {ppm:+.1f} ppm", f"D = {dist_corr:.4f} m", "PRISME LOCK")

    return fig


def afficher_atelier_lum_geo(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort une mission Géomètre ci-dessus.")
        return
    banque = BANQUES_LUM_GEO[sujet_idx]
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






BANQUES_LUM_TRANS = {
    0: {
        "questions": [
            {"id": "qltr0_1", "q": "Quelle couleur réglementaire doivent émettre les feux de position arrière et les feux stop d'un véhicule routier ?", "options": ["Rouge (longueur d'onde autour de 630 à 660 nm)", "Bleu azur", "Vert émeraude"], "rep": "Rouge (longueur d'onde autour de 630 à 660 nm)"},
            {"id": "qltr0_2", "q": "Pourquoi le rouge est-il universellement choisi pour les feux stop et les signaux d'arrêt ?", "options": ["C'est la radiation visible la moins diffusée par le brouillard et associée immédiatement au danger", "C'est la couleur la plus froide", "C'est la seule couleur produite par les LED"], "rep": "C'est la radiation visible la moins diffusée par le brouillard et associée immédiatement au danger"},
            {"id": "qltr0_3", "q": "Quelle couleur réglementaire est imposée pour les indicateurs de direction (clignotants) et feux de détresse ?", "options": ["Jaune-orangé (ambre, autour de 590 nm)", "Blanc pur", "Bleu"], "rep": "Jaune-orangé (ambre, autour de 590 nm)"},
            {"id": "qltr0_4", "q": "Dans un phare équipé d'une ampoule halogène à spectre continu, comment obtient-on la lumière rouge d'un feu stop ?", "options": ["Par synthèse soustractive : le cabochon rouge absorbe le bleu et le vert et ne transmet que le rouge", "Par synthèse additive", "Par diffraction"], "rep": "Par synthèse soustractive : le cabochon rouge absorbe le bleu et le vert et ne transmet que le rouge"},
            {"id": "qltr0_5", "q": "Quel avantage énergétique apportent les LED monochromatiques rouges ou ambrées par rapport à une ampoule halogène derrière un filtre ?", "options": ["Elles émettent directement la bonne couleur sans gaspiller d'énergie absorbée par un filtre coloré", "Elles chauffent davantage le plastique", "Elles consomment dix fois plus"], "rep": "Elles émettent directement la bonne couleur sans gaspiller d'énergie absorbée par un filtre coloré"},
            {"id": "qltr0_6", "q": "Quelle couleur émettent obligatoirement les feux de recul à l'arrière d'un poids lourd ou d'une voiture ?", "options": ["Blanc", "Rouge", "Vert"], "rep": "Blanc"},
            {"id": "qltr0_7", "q": "Quelle est la couleur réservée aux feux de gabarit latéraux d'un ensemble routier de plus de 6 mètres ?", "options": ["Jaune-orangé (ambre)", "Bleu", "Violet"], "rep": "Jaune-orangé (ambre)"},
            {"id": "qltr0_8", "q": "Si l'on éclaire un panneau stop rouge avec la lumière bleue pure d'un gyrophare de police la nuit, de quelle couleur apparaît le fond du panneau ?", "options": ["Noir sombre (car le rouge absorbe le bleu)", "Blanc pur", "Vert vif"], "rep": "Noir sombre (car le rouge absorbe le bleu)"},
            {"id": "qltr0_9", "q": "Quel est le rôle des microprismes moulés à l'intérieur des catadioptres rouges arrière d'une semi-remorque ?", "options": ["Renvoyer la lumière des phares des véhicules suiveurs par rétroréflexion même moteur éteint", "Éclairer l'intérieur de la remorque", "Mesurer la vitesse"], "rep": "Renvoyer la lumière des phares des véhicules suiveurs par rétroréflexion même moteur éteint"},
            {"id": "qltr0_10", "q": "À quels véhicules sont strictement réservés les feux spéciaux bleus à éclats ?", "options": ["Aux véhicules d'intérêt général prioritaires (police, gendarmerie, pompiers, SAMU)", "Aux convois exceptionnels", "Aux dépanneuses"], "rep": "Aux véhicules d'intérêt général prioritaires (police, gendarmerie, pompiers, SAMU)"},
        ],
        "trous": [
            ("1. Les feux stop et de position arrière émettent une lumière de couleur .........", ["Choisir...", "rouge", "bleue"], "rouge", "ltr_t1"),
            ("2. Les clignotants et feux de gabarit latéraux sont de couleur jaune-.........", ["Choisir...", "orangé", "vert"], "orangé", "ltr_t2"),
            ("3. Un filtre rouge placé devant une lampe blanche agit par synthèse .........", ["Choisir...", "soustractive", "additive"], "soustractive", "ltr_t3"),
            ("4. Le filtre rouge ......... les radiations bleues et vertes de la lumière blanche.", ["Choisir...", "absorbe", "amplifie"], "absorbe", "ltr_t4"),
            ("5. Les LED colorées émettent directement une lumière quasi ......... sans perte.", ["Choisir...", "monochromatique", "blanche"], "monochromatique", "ltr_t5"),
            ("6. Les feux de recul émettent obligatoirement une lumière .........", ["Choisir...", "blanche", "rouge"], "blanche", "ltr_t6"),
            ("7. Les catadioptres arrière fonctionnent la nuit par .........", ["Choisir...", "rétroréflexion", "dispersion"], "rétroréflexion", "ltr_t7"),
            ("8. La lumière rouge est moins ......... par les gouttelettes de brouillard.", ["Choisir...", "diffusée", "rapide"], "diffusée", "ltr_t8"),
            ("9. Les gyrophares des convois exceptionnels sont de couleur .........", ["Choisir...", "orange", "bleue"], "orange", "ltr_t9"),
            ("10. Un objet rouge éclairé uniquement en lumière bleue paraît .........", ["Choisir...", "noir", "blanc"], "noir", "ltr_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qltr1_1", "q": "Quelle température de couleur (en kelvins) caractérise les phares LED modernes des poids lourds et voitures ?", "options": ["5000 K à 6000 K (blanc froid proche de la lumière du jour)", "2000 K (jaune bougie)", "12000 K (violet)"], "rep": "5000 K à 6000 K (blanc froid proche de la lumière du jour)"},
            {"id": "qltr1_2", "q": "Pourquoi les anciens phares automobiles français étaient-ils équipés d'ampoules jaunes (3000 K) jusqu'en 1993 ?", "options": ["Pour réduire l'éblouissement nocturne des conducteurs arrivant en face en filtrant le bleu", "Parce que le verre blanc n'existait pas", "Pour éclairer plus loin que le blanc"], "rep": "Pour réduire l'éblouissement nocturne des conducteurs arrivant en face en filtrant le bleu"},
            {"id": "qltr1_3", "q": "Quel avantage procure un éclairage LED blanc neutre (5500 K) par rapport aux anciennes ampoules halogènes jaunâtres (3200 K) sur autoroute ?", "options": ["Un meilleur contraste des panneaux, des marquages au sol et une détection plus rapide des obstacles", "Une consommation électrique doublée", "Une portée limitée à 10 mètres"], "rep": "Un meilleur contraste des panneaux, des marquages au sol et une détection plus rapide des obstacles"},
            {"id": "qltr1_4", "q": "Quel inconvénient présente une lumière trop riche en bleu (température > 6500 K) par temps de brouillard dense ou de neige ?", "options": ["Les courtes longueurs d'onde bleues sont fortement diffusées par les gouttelettes, créant un mur blanc éblouissant", "La lumière traverse le brouillard sans aucune diffusion", "Les panneaux deviennent invisibles"], "rep": "Les courtes longueurs d'onde bleues sont fortement diffusées par les gouttelettes, créant un mur blanc éblouissant"},
            {"id": "qltr1_5", "q": "Comment s'appelle le phénomène physique par lequel les fines gouttelettes de brouillard renvoient la lumière bleue vers le conducteur ?", "options": ["La diffusion de la lumière", "La réfraction totale", "L'absorption atomique"], "rep": "La diffusion de la lumière"},
            {"id": "qltr1_6", "q": "Quel défaut de réglage d'un phare de poids lourd provoque l'éblouissement dangereux des automobilistes arrivant en sens inverse ?", "options": ["Un faisceau de croisement réglé trop haut (rabattement insuffisant)", "Une ampoule trop propre", "Une batterie trop chargée"], "rep": "Un faisceau de croisement réglé trop haut (rabattement insuffisant)"},
            {"id": "qltr1_7", "q": "Quel appareil utilise le contrôleur technique pour vérifier l'inclinaison et l'intensité lumineuse des feux d'un véhicule ?", "options": ["Un régloscope (ou contrôloscope de phares)", "Un sonomètre", "Un opacimètre"], "rep": "Un régloscope (ou contrôloscope de phares)"},
            {"id": "qltr1_8", "q": "Comment agissent les lunettes de conduite de nuit à verres jaunes légèrement teintés ?", "options": ["Elles filtrent une partie du pic bleu des phares LED adverses pour diminuer l'éblouissement", "Elles amplifient les rayons X", "Elles rendent la route bleue"], "rep": "Elles filtrent une partie du pic bleu des phares LED adverses pour diminuer l'éblouissement"},
            {"id": "qltr1_9", "q": "Comment fonctionnent les feux de route adaptatifs matriciels (Matrix LED) sur les véhicules récents ?", "options": ["Une caméra détecte les phares et feux arrière des autres usagers et éteint sélectivement les segments LED correspondants", "Ils éteignent tous les phares dès qu'il fait nuit", "Ils clignotent en permanence"], "rep": "Une caméra détecte les phares et feux arrière des autres usagers et éteint sélectivement les segments LED correspondants"},
            {"id": "qltr1_10", "q": "Quelle est l'unité de mesure de la température de couleur d'un projecteur LED ?", "options": ["Le kelvin (K)", "Le lux (lx)", "Le watt (W)"], "rep": "Le kelvin (K)"},
        ],
        "trous": [
            ("1. Les phares LED modernes émettent une lumière blanche autour de ......... K.", ["Choisir...", "5500", "2000"], "5500", "ltr_t1"),
            ("2. Les anciennes ampoules halogènes ont une teinte plus chaude autour de ......... K.", ["Choisir...", "3200", "8000"], "3200", "ltr_t2"),
            ("3. Dans le brouillard, les radiations ......... sont les plus diffusées par les gouttelettes.", ["Choisir...", "bleues", "rouges"], "bleues", "ltr_t3"),
            ("4. Le réglage de la hauteur des phares se contrôle au garage avec un .........", ["Choisir...", "régloscope", "luxmètre"], "régloscope", "ltr_t4"),
            ("5. Des verres de conduite teintés en ......... filtrent l'excès de lumière bleue la nuit.", ["Choisir...", "jaune", "bleu"], "jaune", "ltr_t5"),
            ("6. Les phares ......... LED découpent le faisceau pour ne pas éblouir les autres usagers.", ["Choisir...", "Matrix", "Sodium"], "Matrix", "ltr_t6"),
            ("7. La température de couleur s'exprime en .........", ["Choisir...", "kelvins", "nanomètres"], "kelvins", "ltr_t7"),
            ("8. Une lumière à 5500 K améliore le ......... des panneaux et marquages au sol.", ["Choisir...", "contraste", "poids"], "contraste", "ltr_t8"),
            ("9. Les feux de croisement sont inclinés vers le ......... pour éviter l'éblouissement.", ["Choisir...", "bas", "haut"], "bas", "ltr_t9"),
            ("10. Le spectre d'une LED blanche présente un pic important dans le .........", ["Choisir...", "bleu", "vert"], "bleu", "ltr_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qltr2_1", "q": "Comment un capteur LiDAR (télédétection par laser) embarqué sur un poids lourd ou véhicule autonome mesure-t-il la distance des obstacles ?", "options": ["En mesurant le temps de vol (aller-retour) d'une impulsion lumineuse laser infrarouge réfléchie par l'obstacle", "En pesant l'obstacle", "En émettant des ultrasons audibles"], "rep": "En mesurant le temps de vol (aller-retour) d'une impulsion lumineuse laser infrarouge réfléchie par l'obstacle"},
            {"id": "qltr2_2", "q": "Dans quel domaine spectral invisible fonctionnent la majorité des capteurs LiDAR automobiles (905 nm ou 1550 nm) ?", "options": ["L'infrarouge proche (IR)", "L'ultraviolet (UV)", "Les rayons gamma"], "rep": "L'infrarouge proche (IR)"},
            {"id": "qltr2_3", "q": "Pourquoi utilise-t-on un faisceau infrarouge invisible plutôt qu'un laser rouge ou vert visible pour le LiDAR d'un camion ?", "options": ["Pour ne pas éblouir ni distraire les autres conducteurs sur la route", "Parce que la lumière visible ne se réfléchit pas", "Parce que l'infrarouge est plus lent"], "rep": "Pour ne pas éblouir ni distraire les autres conducteurs sur la route"},
            {"id": "qltr2_4", "q": "Quelle surface de véhicule renvoie le moins bien le faisceau infrarouge d'un capteur LiDAR ?", "options": ["Une carrosserie noire mate (faible albédo) qui absorbe la majorité du rayonnement", "Une plaque d'immatriculation blanche rétroréfléchissante", "Un panneau routier neuf"], "rep": "Une carrosserie noire mate (faible albédo) qui absorbe la majorité du rayonnement"},
            {"id": "qltr2_5", "q": "Quel système d'aide à la conduite utilise une caméra couleur RVB derrière le pare-brise pour lire les panneaux de limitation de vitesse ?", "options": ["La reconnaissance optique de panneaux (TSR) basée sur la détection des formes et des couleurs (cercles rouges)", "L'ABS", "Le régulateur de pression de pneus"], "rep": "La reconnaissance optique de panneaux (TSR) basée sur la détection des formes et des couleurs (cercles rouges)"},
            {"id": "qltr2_6", "q": "Comment la caméra de maintien dans la voie (LKA) repère-t-elle les lignes blanches ou jaunes sur la chaussée ?", "options": ["Par le fort contraste lumineux (différence d'albédo) entre la bande claire et l'enrobé sombre", "Par détection magnétique", "Par mesure thermique"], "rep": "Par le fort contraste lumineux (différence d'albédo) entre la bande claire et l'enrobé sombre"},
            {"id": "qltr2_7", "q": "Quelle anomalie visuelle appelée daltonisme touche environ 8 % des hommes et affecte la distinction entre le rouge et le vert ?", "options": ["Une déficience des cônes rétiniens sensibles au rouge ou au vert", "Une myopie sévère", "Une cataracte"], "rep": "Une déficience des cônes rétiniens sensibles au rouge ou au vert"},
            {"id": "qltr2_8", "q": "Comment les feux tricolores routiers sont-ils normalisés pour qu'un conducteur daltonien puisse les interpréter sans erreur ?", "options": ["Par la position fixe des feux (rouge toujours en haut, orange au milieu, vert toujours en bas)", "Par la taille des poteaux", "Par un signal sonore permanent"], "rep": "Par la position fixe des feux (rouge toujours en haut, orange au milieu, vert toujours en bas)"},
            {"id": "qltr2_9", "q": "Quelle est la vitesse de propagation de l'impulsion laser infrarouge utilisée dans le calcul de distance d'un LiDAR ?", "options": ["c ≈ 300 000 km/s (3 × 10⁸ m/s)", "340 m/s", "100 km/h"], "rep": "c ≈ 300 000 km/s (3 × 10⁸ m/s)"},
            {"id": "qltr2_10", "q": "Pourquoi le pare-brise devant la caméra ADAS doit-il être parfaitement propre et exempt d'impact ?", "options": ["Les salissures diffusent la lumière et empêchent l'analyse fidèle des couleurs et des lignes", "Pour réduire la consommation de carburant", "Pour refroidir le moteur"], "rep": "Les salissures diffusent la lumière et empêchent l'analyse fidèle des couleurs et des lignes"},
        ],
        "trous": [
            ("1. Les capteurs LiDAR utilisent des impulsions laser dans le domaine ......... (905 nm).", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "ltr_t1"),
            ("2. Le faisceau est invisible afin de ne pas ......... les autres conducteurs.", ["Choisir...", "éblouir", "ralentir"], "éblouir", "ltr_t2"),
            ("3. Une carrosserie ......... mate absorbe le rayonnement et réduit la portée du LiDAR.", ["Choisir...", "noire", "blanche"], "noire", "ltr_t3"),
            ("4. Les caméras ADAS repèrent les lignes au sol grâce au ......... clair/sombre.", ["Choisir...", "contraste", "bruit"], "contraste", "ltr_t4"),
            ("5. Les panneaux d'interdiction sont détectés par leur bordure de couleur .........", ["Choisir...", "rouge", "bleue"], "rouge", "ltr_t5"),
            ("6. Le ......... est une anomalie de perception entre le rouge et le vert.", ["Choisir...", "daltonisme", "astigmatisme"], "daltonisme", "ltr_t6"),
            ("7. Sur un feu tricolore, le feu ......... est toujours placé en haut.", ["Choisir...", "rouge", "vert"], "rouge", "ltr_t7"),
            ("8. La vitesse des impulsions laser dans l'air vaut environ 300 000 ........./s.", ["Choisir...", "km", "m"], "km", "ltr_t8"),
            ("9. Les trois capteurs d'une caméra couleur sont sensibles au Rouge, Vert et .........", ["Choisir...", "Bleu", "Jaune"], "Bleu", "ltr_t9"),
            ("10. Le calcul de distance LiDAR mesure le ......... de vol aller-retour de la lumière.", ["Choisir...", "temps", "poids"], "temps", "ltr_t10"),
        ]
    }
}


def mettre_a_jour_lum_trans_matplotlib(sujet_idx):
    """Banc d'essai optique Lumière & Couleurs adapté au Transport Routier."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        filtre = st.session_state.get("radio_ltr_s0", "Cabochon Rouge (Feu Stop)")
        ax.add_patch(patches.Rectangle((45, 105), 75, 50, facecolor="#fef08a", edgecolor="white"))
        ax.text(82, 130, "Ampoule\nBlanche", color="#0f172a", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((120, 240)), list((115, 115)), color="#ef4444", lw=4)
        ax.plot(list((120, 240)), list((130, 130)), color="#22c55e", lw=4)
        ax.plot(list((120, 240)), list((145, 145)), color="#3b82f6", lw=4)

        if "Rouge" in filtre:
            c_f, c_out, txt_out = "#ef4444", "#ef4444", "TRANSMISSION ROUGE : Vert et Bleu absorbés (Synthèse soustractive)"
        elif "Ambre" in filtre:
            c_f, c_out, txt_out = "#f59e0b", "#f59e0b", "TRANSMISSION AMBRE (Rouge + Vert) : Bleu absorbé (Clignotant)"
        else:
            c_f, c_out, txt_out = "#ffffff", "#ffffff", "TRANSMISSION BLANCHE : Toutes radiations transmises (Feu de recul)"

        ax.add_patch(patches.Rectangle((240, 75), 35, 110, facecolor=c_f, edgecolor="white", lw=2))
        ax.text(257, 62, filtre, color=c_f, fontsize=8, fontweight="bold", ha="center")

        ax.plot(list((275, 480)), list((130, 130)), color=c_out, lw=8)
        ax.text(380, 112, "Faisceau émergent", color=c_out, fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "SIGNALISATION VÉHICULE : SYNTHÈSE SOUSTRACTIVE DES FEUX ARRIÈRE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, txt_out, color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.ltr_mesure_courante = (filtre, "Source RVB", "Filtrage sélectif", "CONFORME CODE ROUTE")

    elif sujet_idx == 1:
        temp_k = st.session_state.get("slider_ltr_s1", 5500)
        brouillard = st.session_state.get("check_ltr_s1", False)
        if temp_k < 3800:
            c_phare, teinte = "#fde047", "Blanc Chaud / Jaune (Halogène)"
        elif temp_k <= 6000:
            c_phare, teinte = "#ffffff", "Blanc Neutre Jour (LED Homologuée)"
        else:
            c_phare, teinte = "#93c5fd", "Blanc Bleuté Froid (> 6000 K)"

        ax.add_patch(patches.Rectangle((55, 100), 85, 60, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(97, 130, f"Phare LED\n{temp_k} K", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        alpha_f = 0.18 if (brouillard and temp_k > 5500) else 0.35
        ax.fill(list((140, 520, 520)), list((130, 75, 185)), color=c_phare, alpha=alpha_f)

        if brouillard and temp_k > 5500:
            ax.text(330, 130, "BROUILLARD : Forte diffusion du bleu !\nÉblouissement retour conducteur", color="#ef4444", fontsize=8.5, fontweight="bold", ha="center", va="center")
            diag_p = "DANGER BROUILLARD : Trop de bleu diffusé ! Utiliser les feux antibrouillard bas."
            c_dp = "#ef4444"
        else:
            ax.text(340, 130, f"Éclairage optimal : {teinte}", color=c_phare, fontsize=8.5, fontweight="bold", ha="center", va="center")
            diag_p = f"VISIBILITÉ OPTIMALE : Température {temp_k} K adaptée aux conditions."
            c_dp = "#22c55e"

        ax.text(25, 18, "ÉCLAIRAGE ROUTIER : TEMPÉRATURE DE COULEUR ET DIFFUSION ATMOSPHÉRIQUE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, diag_p, color=c_dp, fontsize=8, fontweight="bold")
        st.session_state.ltr_mesure_courante = (f"{temp_k} K", "Brouillard" if brouillard else "Temps clair", teinte, "ATTENTION" if (brouillard and temp_k > 5500) else "OPTIMAL")

    else:
        cible_coul = st.session_state.get("radio_ltr_s2", "Plaque rétroréfléchissante blanche (Albédo 0,85)")
        if "noire" in cible_coul:
            c_cib, portee_m, alb = "#1e293b", 65, 0.08
        elif "grise" in cible_coul:
            c_cib, portee_m, alb = "#94a3b8", 140, 0.45
        else:
            c_cib, portee_m, alb = "#f8fafc", 220, 0.85

        ax.add_patch(patches.Rectangle((55, 100), 90, 60, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(100, 130, "Capteur LiDAR\n(IR 905 nm)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        xc = 200.0 + (portee_m / 240.0) * 310.0
        ax.plot(list((145, xc)), list((122, 122)), color="#ef4444", lw=2.5, ls="--")
        ax.plot(list((xc, 145)), list((138, 138)), color="#22c55e", lw=2.5, ls=":")

        ax.add_patch(patches.Rectangle((xc, 95), 40, 70, facecolor=c_cib, edgecolor="#eab308", lw=2))
        ax.text(xc + 20, 180, f"Obstacle\nPortée = {portee_m} m", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        ax.text(25, 18, "AIDES À LA CONDUITE (ADAS) : PORTÉE LIDAR SELON L'ALBÉDO DE L'OBSTACLE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Albédo cible = {alb:.2f}  =>  Portée de détection LiDAR = {portee_m} mètres", color="#22c55e" if portee_m >= 140 else "#f59e0b", fontsize=8, fontweight="bold")
        st.session_state.ltr_mesure_courante = (f"Albédo = {alb:.2f}", "IR 905 nm", f"Portée = {portee_m} m", "DÉTECTION OK")

    return fig


def afficher_atelier_lum_trans(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet Transport Routier ci-dessus.")
        return
    banque = BANQUES_LUM_TRANS[sujet_idx]
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


BANQUES_LUM_TP = {
    0: {
        "questions": [
            {"id": "qltp0_1", "q": "Quel phénomène optique permet aux gilets haute visibilité et panneaux de chantier jaune-vert d'être très lumineux à l'aube et au crépuscule ?", "options": ["La fluorescence : les pigments convertissent les UV invisibles en lumière visible", "La réflexion totale interne", "L'incandescence thermique"], "rep": "La fluorescence : les pigments convertissent les UV invisibles en lumière visible"},
            {"id": "qltp0_2", "q": "Comment agit la bande rétroréfléchissante grise d'un gilet ou d'un cône de chantier éclairée la nuit par les phares ?", "options": ["Elle renvoie la lumière directement vers les phares grâce à des microbilles de verre ou microprismes", "Elle absorbe toute la lumière", "Elle disperse la lumière vers le ciel"], "rep": "Elle renvoie la lumière directement vers les phares grâce à des microbilles de verre ou microprismes"},
            {"id": "qltp0_3", "q": "Pourquoi associe-t-on couleur fluorescente et bandes rétroréfléchissantes sur les EPI des Travaux Publics ?", "options": ["La fluorescence agit de jour et au crépuscule, la rétroréflexion agit de nuit sous les phares", "Pour réduire le poids du gilet", "Pour imperméabiliser le tissu"], "rep": "La fluorescence agit de jour et au crépuscule, la rétroréflexion agit de nuit sous les phares"},
            {"id": "qltp0_4", "q": "À quelle longueur d'onde l'œil humain présente-t-il sa sensibilité maximale de jour (vision photopique) ?", "options": ["Autour de 555 nm (jaune-vert)", "Autour de 400 nm (violet)", "Autour de 750 nm (infrarouge)"], "rep": "Autour de 555 nm (jaune-vert)"},
            {"id": "qltp0_5", "q": "Quelle norme européenne régit les vêtements de signalisation à haute visibilité sur les chantiers ?", "options": ["La norme EN ISO 20471", "La norme Euro 6", "La norme NF C 15-100"], "rep": "La norme EN ISO 20471"},
            {"id": "qltp0_6", "q": "Que se passe-t-il si un gilet fluorescent reste exposé plusieurs mois en plein soleil ?", "options": ["Les rayons UV dégradent les pigments fluorescents : le gilet pâlit et perd sa visibilité", "Le gilet devient rétroréfléchissant", "La couleur devient plus foncée"], "rep": "Les rayons UV dégradent les pigments fluorescents : le gilet pâlit et perd sa visibilité"},
            {"id": "qltp0_7", "q": "Pourquoi la boue sur les bandes rétroréfléchissantes d'un panneau annule-t-elle leur efficacité la nuit ?", "options": ["La couche opaque bloque les rayons avant qu'ils n'atteignent les microbilles de verre", "La boue change l'indice de réfraction de l'air", "Les phares s'éteignent"], "rep": "La couche opaque bloque les rayons avant qu'ils n'atteignent les microbilles de verre"},
            {"id": "qltp0_8", "q": "Quelle classe de film rétroréfléchissant offre la distance de visibilité maximale sur autoroute ?", "options": ["La Classe 3 (microprismes haute intensité)", "La Classe 1", "Aucune différence"], "rep": "La Classe 3 (microprismes haute intensité)"},
            {"id": "qltp0_9", "q": "Quel rayonnement solaire invisible active les pigments fluorescents par temps couvert ?", "options": ["Les rayons ultraviolets (UV)", "Les ondes radio", "Les rayons X"], "rep": "Les rayons ultraviolets (UV)"},
            {"id": "qltp0_10", "q": "Quelle couleur est réservée en France à la signalisation temporaire de chantier ?", "options": ["Le fond jaune", "Le fond bleu", "Le fond vert"], "rep": "Le fond jaune"},
        ],
        "trous": [
            ("1. Les gilets de chantier utilisent des pigments ......... pour transformer les UV en lumière visible.", ["Choisir...", "fluorescents", "opaques"], "fluorescents", "ltp_t1"),
            ("2. La nuit, les bandes grises renvoient la lumière vers les phares par .........", ["Choisir...", "rétroréflexion", "absorption"], "rétroréflexion", "ltp_t2"),
            ("3. Ces bandes contiennent des microbilles de verre ou des .........", ["Choisir...", "microprismes", "miroirs plans"], "microprismes", "ltp_t3"),
            ("4. L'œil humain est le plus sensible autour de 555 nm, dans le .........", ["Choisir...", "jaune-vert", "violet"], "jaune-vert", "ltp_t4"),
            ("5. La fluorescence est particulièrement efficace de jour et au .........", ["Choisir...", "crépuscule", "sous-sol"], "crépuscule", "ltp_t5"),
            ("6. Les vêtements haute visibilité sont classés selon la norme EN ISO .........", ["Choisir...", "20471", "9001"], "20471", "ltp_t6"),
            ("7. En France, les panneaux temporaires de chantier ont un fond .........", ["Choisir...", "jaune", "bleu"], "jaune", "ltp_t7"),
            ("8. Une exposition prolongée au soleil dégrade les pigments sous l'effet des .........", ["Choisir...", "UV", "infrarouges"], "UV", "ltp_t8"),
            ("9. Les films de Classe ......... offrent la visibilité maximale sur autoroute.", ["Choisir...", "3", "1"], "3", "ltp_t9"),
            ("10. Le nettoyage régulier des panneaux évite l'......... de la lumière par la boue.", ["Choisir...", "absorption", "dispersion"], "absorption", "ltp_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qltp1_1", "q": "Dans les tranchées TP, pourquoi utilise-t-on des grillages avertisseurs de couleurs normalisées ?", "options": ["Pour identifier visuellement la nature du réseau enterré avant tout coup de godet", "Pour décorer la tranchée", "Pour mesurer la profondeur de fouille"], "rep": "Pour identifier visuellement la nature du réseau enterré avant tout coup de godet"},
            {"id": "qltp1_2", "q": "Quelle couleur normalisée identifie un réseau électrique enterré ?", "options": ["Rouge", "Bleu", "Jaune"], "rep": "Rouge"},
            {"id": "qltp1_3", "q": "Quelle couleur identifie un réseau de gaz combustible enterré sur un chantier TP ?", "options": ["Jaune", "Vert", "Marron"], "rep": "Jaune"},
            {"id": "qltp1_4", "q": "Quelle couleur identifie une canalisation d'eau potable enterrée ?", "options": ["Bleu", "Rouge", "Orange"], "rep": "Bleu"},
            {"id": "qltp1_5", "q": "Pourquoi un éclairage de chantier nocturne à vapeur de sodium (lumière jaune) est-il dangereux près des réseaux ?", "options": ["Son faible IRC empêche de distinguer les grillages rouges, bleus, verts et jaunes", "Il éclaire trop fort", "Il fait fondre les gaines plastiques"], "rep": "Son faible IRC empêche de distinguer les grillages rouges, bleus, verts et jaunes"},
            {"id": "qltp1_6", "q": "Quel type de projecteur de chantier privilégier la nuit pour respecter le code couleur des réseaux ?", "options": ["Un mât d'éclairage LED blanc neutre (4500 K) avec IRC ≥ 80", "Une lampe au sodium jaune (IRC 22)", "Un projecteur rouge pur"], "rep": "Un mât d'éclairage LED blanc neutre (4500 K) avec IRC ≥ 80"},
            {"id": "qltp1_7", "q": "Quelle couleur de grillage avertisseur correspond aux réseaux de fibre optique et télécoms ?", "options": ["Vert", "Bleu", "Jaune"], "rep": "Vert"},
            {"id": "qltp1_8", "q": "À quelle hauteur au-dessus d'une canalisation pose-t-on le grillage avertisseur coloré ?", "options": ["Entre 20 cm et 30 cm au-dessus de la canalisation", "Directement sous le tuyau", "À 2 mètres au-dessus du trottoir"], "rep": "Entre 20 cm et 30 cm au-dessus de la canalisation"},
            {"id": "qltp1_9", "q": "Quelle couleur identifie les réseaux d'assainissement et eaux usées ?", "options": ["Marron", "Blanc", "Rose"], "rep": "Marron"},
            {"id": "qltp1_10", "q": "Quelle grandeur photométrique vérifie-t-on sur un chantier nocturne ?", "options": ["L'éclairement lumineux en lux (lx)", "La vergence en dioptries", "La masse volumique en kg/m³"], "rep": "L'éclairement lumineux en lux (lx)"},
        ],
        "trous": [
            ("1. En tranchée, un grillage avertisseur ......... signale un câble électrique.", ["Choisir...", "rouge", "bleu"], "rouge", "ltp_t1"),
            ("2. Le grillage avertisseur de couleur ......... signale une canalisation de gaz.", ["Choisir...", "jaune", "vert"], "jaune", "ltp_t2"),
            ("3. Le réseau d'eau potable est repéré par la couleur .........", ["Choisir...", "bleue", "rouge"], "bleue", "ltp_t3"),
            ("4. Les réseaux de fibre optique et télécoms utilisent la couleur .........", ["Choisir...", "verte", "jaune"], "verte", "ltp_t4"),
            ("5. Le grillage se pose environ ......... cm au-dessus de la canalisation.", ["Choisir...", "20 à 30", "200"], "20 à 30", "ltp_t5"),
            ("6. De nuit, il faut éclairer la tranchée avec des LED ayant un ......... supérieur à 80.", ["Choisir...", "IRC", "poids"], "IRC", "ltp_t6"),
            ("7. Une lampe au sodium jaune altère la perception des ......... des réseaux.", ["Choisir...", "couleurs", "profondeurs"], "couleurs", "ltp_t7"),
            ("8. La température de couleur recommandée sur un mât LED est autour de ......... K.", ["Choisir...", "4500", "1800"], "4500", "ltp_t8"),
            ("9. Les réseaux d'assainissement sont repérés par la couleur .........", ["Choisir...", "marron", "bleue"], "marron", "ltp_t9"),
            ("10. L'éclairement sur le chantier se mesure en .........", ["Choisir...", "lux", "watts"], "lux", "ltp_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qltp2_1", "q": "Comment appelle-t-on le pouvoir réfléchissant d'une surface routière (rapport énergie réfléchie / reçue) ?", "options": ["L'albédo (compris entre 0 et 1)", "La vergence", "La réfraction"], "rep": "L'albédo (compris entre 0 et 1)"},
            {"id": "qltp2_2", "q": "Pourquoi un enrobé bitumineux noir neuf (albédo ≈ 0,05) chauffe-t-il énormément en été en ville ?", "options": ["Parce qu'il absorbe environ 95 % du rayonnement solaire et le transforme en chaleur", "Parce qu'il réfléchit 95 % de la lumière", "Parce qu'il est composé de verre"], "rep": "Parce qu'il absorbe environ 95 % du rayonnement solaire et le transforme en chaleur"},
            {"id": "qltp2_3", "q": "Quel phénomène climatique urbain est aggravé par les revêtements routiers sombres à faible albédo ?", "options": ["L'îlot de chaleur urbain (ICU)", "L'effet de serre marin", "Les pluies acides"], "rep": "L'îlot de chaleur urbain (ICU)"},
            {"id": "qltp2_4", "q": "Quelle solution technique mettent en œuvre les entreprises de Travaux Publics pour réduire la température des chaussées en été ?", "options": ["Des revêtements clairs ou enrobés végétaux / réflectifs à albédo élevé (0,35 à 0,55)", "Des enrobés encore plus noirs", "Des plaques d'acier"], "rep": "Des revêtements clairs ou enrobés végétaux / réflectifs à albédo élevé (0,35 à 0,55)"},
            {"id": "qltp2_5", "q": "Quel avantage secondaire procure une chaussée claire à albédo élevé lors de l'éclairage public nocturne ?", "options": ["Elle réfléchit mieux la lumière des lampadaires, permettant de réduire la puissance électrique", "Elle émet sa propre lumière sans lampadaire", "Elle absorbe les phares des voitures"], "rep": "Elle réfléchit mieux la lumière des lampadaires, permettant de réduire la puissance électrique"},
            {"id": "qltp2_6", "q": "Quel instrument optique utilise-t-on sur chantier pour mesurer l'albédo d'un revêtement routier ?", "options": ["Un albédomètre (double pyranomètre)", "Un théodolite", "Un scléromètre"], "rep": "Un albédomètre (double pyranomètre)"},
            {"id": "qltp2_7", "q": "Quelle est la valeur de l'albédo d'une surface parfaitement noire absorbant toute la lumière ?", "options": ["0", "1", "0,5"], "rep": "0"},
            {"id": "qltp2_8", "q": "Quelle est la valeur de l'albédo de la neige fraîche ou d'un marquage routier blanc très réfléchissant ?", "options": ["Proche de 0,80 à 0,90", "Proche de 0,05", "Négative"], "rep": "Proche de 0,80 à 0,90"},
            {"id": "qltp2_9", "q": "De combien de degrés peut baisser la température de surface d'une voirie en passant d'un enrobé noir (0,05) à un revêtement clair (0,45) en été ?", "options": ["De 8 °C à 15 °C en surface", "De 0,1 °C", "De 100 °C"], "rep": "De 8 °C à 15 °C en surface"},
            {"id": "qltp2_10", "q": "Pourquoi ajoute-t-on des microbilles de verre à la surface de la peinture blanche des bandes de signalisation routière ?", "options": ["Pour rendre le marquage rétroréfléchissant la nuit sous les phares", "Pour rendre la route glissante", "Pour colorer la peinture en bleu"], "rep": "Pour rendre le marquage rétroréfléchissant la nuit sous les phares"},
        ],
        "trous": [
            ("1. Le rapport entre la lumière réfléchie et la lumière reçue s'appelle l'.........", ["Choisir...", "albédo", "indice"], "albédo", "ltp_t1"),
            ("2. Un enrobé bitumineux noir neuf possède un albédo très faible, proche de .........", ["Choisir...", "0,05", "0,85"], "0,05", "ltp_t2"),
            ("3. Le noir ......... la quasi-totalité du rayonnement solaire et le transforme en chaleur.", ["Choisir...", "absorbe", "réfléchit"], "absorbe", "ltp_t3"),
            ("4. Les surfaces sombres en ville créent des ......... de chaleur urbains.", ["Choisir...", "îlots", "puits"], "îlots", "ltp_t4"),
            ("5. Les revêtements routiers ......... réfléchissent davantage la lumière solaire.", ["Choisir...", "clairs", "noirs"], "clairs", "ltp_t5"),
            ("6. L'albédo d'une surface est toujours compris entre 0 et .........", ["Choisir...", "1", "100"], "1", "ltp_t6"),
            ("7. L'instrument qui mesure le rayonnement réfléchi par un sol est un .........", ["Choisir...", "albédomètre", "luxmètre"], "albédomètre", "ltp_t7"),
            ("8. Une chaussée claire permet d'économiser l'énergie de l'......... public la nuit.", ["Choisir...", "éclairage", "arrosage"], "éclairage", "ltp_t8"),
            ("9. On incorpore des ......... de verre dans la peinture routière pour la visibilité nocturne.", ["Choisir...", "microbilles", "graviers noirs"], "microbilles", "ltp_t9"),
            ("10. Le passage à un enrobé clair peut abaisser la température de surface de ......... °C.", ["Choisir...", "10", "0"], "10", "ltp_t10"),
        ]
    }
}


def mettre_a_jour_lum_tp_matplotlib(sujet_idx):
    """Banc d'essai optique Lumière & Couleurs adapté aux Travaux Publics."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        moment = st.session_state.get("radio_ltp_s0", "Crépuscule (UV dominants)")
        ax.add_patch(patches.Rectangle((60, 85), 95, 95, facecolor="#eab308", edgecolor="white", lw=2))
        ax.add_patch(patches.Rectangle((60, 122), 95, 22, facecolor="#cbd5e1"))
        ax.text(107, 195, "Gilet EPI TP\n(Fluo + Rétro)", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        if "Crépuscule" in moment:
            ax.annotate("", xy=(155, 105), xytext=(480, 50), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2.5, ls="--"))
            ax.annotate("", xy=(480, 80), xytext=(155, 105), arrowprops=dict(arrowstyle="->", color="#bef264", lw=3))
            msg = "FLUORESCENCE ACTIVE : Les UV du ciel sont convertis en lumière jaune-vert très visible !"
            c_msg = "#22c55e"
        else:
            ax.annotate("", xy=(155, 133), xytext=(480, 133), arrowprops=dict(arrowstyle="->", color="#ffffff", lw=2.5))
            ax.annotate("", xy=(480, 145), xytext=(155, 133), arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=3))
            msg = "RÉTRORÉFLEXION NOCTURNE : Les microbilles renvoient 100% du faisceau vers les phares !"
            c_msg = "#38bdf8"

        ax.add_patch(patches.Rectangle((480, 45), 75, 125, facecolor="#1e3a8a", edgecolor="white"))
        ax.text(517, 107, "Observateur\n(Conducteur)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")
        ax.text(25, 18, "SIGNALISATION DE CHANTIER : FLUORESCENCE ET RÉTRORÉFLEXION", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg, color=c_msg, fontsize=8, fontweight="bold")
        st.session_state.ltp_mesure_courante = (moment, "Gilet Classe 3", "Visibilité maximale", "CONFORME EPI")

    elif sujet_idx == 1:
        eclairage_tr = st.session_state.get("radio_ltp_s1", "Mât LED Blanc Neutre (4500 K - IRC 90)")
        if "Sodium" in eclairage_tr:
            c_fond, c_r, c_b, c_v, irc_t = "#d97706", "#78350f", "#451a03", "#713f12", 22
            diag_t = "DANGER RÉSEAUX : IRC = 22 ! Les grillages Rouge (Élec) et Bleu (Eau) sont confondus !"
        else:
            c_fond, c_r, c_b, c_v, irc_t = "#334155", "#ef4444", "#3b82f6", "#22c55e", 90
            diag_t = "CHANTIER SÉCURISÉ : IRC = 90 ! Identification parfaite des réseaux Rouge, Bleu, Jaune et Vert."

        ax.add_patch(patches.Rectangle((55, 52), 490, 170, facecolor=c_fond, edgecolor="#38bdf8", lw=2))
        reseaux = [("Grillage ROUGE (Électricité)", c_r, 85), ("Grillage BLEU (Eau potable)", c_b, 122), ("Grillage JAUNE (Gaz)", "#eab308", 159), ("Grillage VERT (Fibre / Télécom)", c_v, 196)]
        for lbl, col, yy in reseaux:
            ax.add_patch(patches.Rectangle((110, yy - 12), 380, 22, facecolor=col, edgecolor="white"))
            ax.text(300, yy - 1, lbl, color="white" if col != "#eab308" else "#0f172a", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.text(25, 18, "TERRASSEMENT NOCTURNE : IDENTIFICATION DES RÉSEAUX ENTERRÉS PAR COULEUR", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, diag_t, color="#22c55e" if irc_t >= 80 else "#ef4444", fontsize=8, fontweight="bold")
        st.session_state.ltp_mesure_courante = (eclairage_tr.split("(").strip(), f"IRC = {irc_t}", "4 réseaux", "SÉCURITÉ OK" if irc_t >= 80 else "RISQUE ACCROCHAGE")

    else:
        albedo = st.session_state.get("slider_ltp_s2", 0.35)
        flux_recu = 900.0
        flux_ref = round(flux_recu * albedo, 0)
        flux_abs = round(flux_recu * (1.0 - albedo), 0)
        temp_surf = round(64.0 - albedo * 35.0, 1)

        gris = int(35 + albedo * 200)
        c_sol = f"#{gris:02x}{gris:02x}{gris:02x}"
        ax.add_patch(patches.Rectangle((60, 165), 480, 45, facecolor=c_sol, edgecolor="white", lw=1.5))
        ax.text(300, 187, f"Revêtement routier (Albédo = {albedo:.2f})", color="white" if albedo < 0.4 else "#0f172a", fontsize=8.5, fontweight="bold", ha="center", va="center")

        ax.annotate("", xy=(240, 165), xytext=(150, 55), arrowprops=dict(arrowstyle="->", color="#fde047", lw=4))
        ax.text(145, 75, f"Soleil : {flux_recu:.0f} W/m²", color="#fde047", fontsize=8, fontweight="bold")

        ax.annotate("", xy=(420, 55), xytext=(310, 165), arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=max(1.0, albedo * 6.0)))
        ax.text(390, 75, f"Réfléchi : {flux_ref:.0f} W/m²", color="#38bdf8", fontsize=8, fontweight="bold")

        ax.text(25, 18, "VOIRIE DURABLE : ALBÉDO DES REVÊTEMENTS ET ÎLOTS DE CHALEUR URBAINS", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Albédo = {albedo:.2f} | Énergie absorbée = {flux_abs:.0f} W/m² | Température chaussée en été = {temp_surf:.1f} °C", color="#22c55e" if albedo >= 0.35 else "#f59e0b", fontsize=8, fontweight="bold")
        st.session_state.ltp_mesure_courante = (f"Albédo = {albedo:.2f}", f"Abs = {flux_abs:.0f} W/m²", f"T = {temp_surf:.1f} °C", "FRAÎCHEUR" if albedo >= 0.35 else "ÎLOT CHALEUR")

    return fig


def afficher_atelier_lum_tp(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un chantier TP ci-dessus.")
        return
    banque = BANQUES_LUM_TP[sujet_idx]
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






BANQUES_LUM_MAINT = {
    0: {
        "questions": [
            {"id": "qlm0_1", "q": "Quel principe de la synthèse soustractive utilise-t-on en vision industrielle pour faire ressortir en noir un défaut rouge sur une pièce métallique ?", "options": ["Éclairer la pièce avec une lumière complémentaire (cyan ou verte) qui est absorbée par le rouge", "Éclairer la pièce avec une lumière rouge", "Éteindre toutes les lumières de l'atelier"], "rep": "Éclairer la pièce avec une lumière complémentaire (cyan ou verte) qui est absorbée par le rouge"},
            {"id": "qlm0_2", "q": "Quelle couleur perçoit une caméra monochrome si on éclaire une étiquette bleue avec une lumière rouge pure ?", "options": ["Du noir (car le pigment bleu absorbe la lumière rouge et ne renvoie rien)", "Du blanc éclatant", "Du jaune vif"], "rep": "Du noir (car le pigment bleu absorbe la lumière rouge et ne renvoie rien)"},
            {"id": "qlm0_3", "q": "Pourquoi utilise-t-on des projecteurs LED monochromatiques (rouges, verts ou bleus) sur les lignes de contrôle automatisé ?", "options": ["Pour augmenter fortement le contraste entre les défauts et la surface saine de la pièce", "Pour chauffer les pièces avant soudage", "Pour économiser la peinture"], "rep": "Pour augmenter fortement le contraste entre les défauts et la surface saine de la pièce"},
            {"id": "qlm0_4", "q": "Quelle est la couleur complémentaire du rouge en synthèse additive ?", "options": ["Le cyan (vert + bleu)", "Le jaune", "Le magenta"], "rep": "Le cyan (vert + bleu)"},
            {"id": "qlm0_5", "q": "Si l'on veut faire disparaître un marquage jaune sur un emballage lors d'un contrôle optique, quelle lumière d'éclairage faut-il choisir ?", "options": ["Une lumière jaune (ou rouge + vert) qui sera réfléchie aussi bien par le fond blanc que par le marquage jaune", "Une lumière bleue", "Une lumière ultraviolette"], "rep": "Une lumière jaune (ou rouge + vert) qui sera réfléchie aussi bien par le fond blanc que par le marquage jaune"},
            {"id": "qlm0_6", "q": "Quel rayonnement invisible (longueur d'onde < 400 nm) utilise-t-on en contrôle non destructif par ressuage fluorescent pour détecter les microfissures ?", "options": ["Les rayons ultraviolets (UV-A / lumière noire)", "Les rayons infrarouges lointains", "Les ondes radio"], "rep": "Les rayons ultraviolets (UV-A / lumière noire)"},
            {"id": "qlm0_7", "q": "Lors d'un contrôle par ressuage UV, pourquoi le pénétrant piégé dans une fissure émet-il une lumière jaune-verte visible ?", "options": ["Par phénomène de fluorescence : il absorbe l'énergie UV invisible et réémet de la lumière visible", "Par combustion chimique", "Par réflexion totale sur le métal"], "rep": "Par phénomène de fluorescence : il absorbe l'énergie UV invisible et réémet de la lumière visible"},
            {"id": "qlm0_8", "q": "Quelle précaution de sécurité est obligatoire lors de l'utilisation d'une lampe UV de contrôle en maintenance ?", "options": ["Porter des lunettes de protection filtrant les UV (anti-UV)", "Regarder directement la lampe pour vérifier son intensité", "Travailler sans gants"], "rep": "Porter des lunettes de protection filtrant les UV (anti-UV)"},
            {"id": "qlm0_9", "q": "Quelle couleur d'éclairage LED est privilégiée pour inspecter des soudures en cuivre ou laiton afin d'éviter les reflets éblouissants ?", "options": ["La lumière bleue (450 nm) qui est fortement absorbée par le cuivre", "La lumière infrarouge", "La lumière jaune"], "rep": "La lumière bleue (450 nm) qui est fortement absorbée par le cuivre"},
            {"id": "qlm0_10", "q": "La couleur apparente d'un objet dépend à la fois de ses pigments et de :", "options": ["La composition spectrale de la lumière qui l'éclaire", "La pression atmosphérique", "La masse de l'objet"], "rep": "La composition spectrale de la lumière qui l'éclaire"},
        ],
        "trous": [
            ("1. La couleur d'un objet dépend de la lumière qui l'éclaire et de l'......... sélective de sa surface.", ["Choisir...", "absorption", "réflexion totale"], "absorption", "lm_t1"),
            ("2. Un objet bleu éclairé uniquement en lumière rouge apparaît .........", ["Choisir...", "noir", "blanc"], "noir", "lm_t2"),
            ("3. En vision industrielle, on utilise une lumière ......... pour maximiser le contraste d'un défaut.", ["Choisir...", "complémentaire", "infrarouge"], "complémentaire", "lm_t3"),
            ("4. La couleur complémentaire du rouge est le .........", ["Choisir...", "cyan", "jaune"], "cyan", "lm_t4"),
            ("5. Le contrôle non destructif par ressuage utilise une lampe à rayons .........", ["Choisir...", "ultraviolets", "X"], "ultraviolets", "lm_t5"),
            ("6. Les UV ont une longueur d'onde inférieure à ......... nm.", ["Choisir...", "400", "700"], "400", "lm_t6"),
            ("7. Le produit pénétrant révèle les fissures par phénomène de .........", ["Choisir...", "fluorescence", "dispersion"], "fluorescence", "lm_t7"),
            ("8. Le technicien doit porter des lunettes de protection .........", ["Choisir...", "anti-UV", "grossissantes"], "anti-UV", "lm_t8"),
            ("9. Une surface blanche ......... toutes les radiations du spectre visible.", ["Choisir...", "diffuse", "absorbe"], "diffuse", "lm_t9"),
            ("10. Les trois couleurs primaires de la synthèse additive sont Rouge, Vert et .........", ["Choisir...", "Bleu", "Jaune"], "Bleu", "lm_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qlm1_1", "q": "Quel instrument optique utilise-t-on en maintenance prédictive pour mesurer le vieillissement et l'oxydation d'une huile hydraulique par sa couleur ?", "options": ["Un spectrophotomètre (ou colorimètre optique)", "Un pied à coulisse", "Un tachymètre"], "rep": "Un spectrophotomètre (ou colorimètre optique)"},
            {"id": "qlm1_2", "q": "Comment évolue le spectre de transmission lumineuse d'une huile industrielle lorsqu'elle s'oxyde ou se charge en particules d'usure ?", "options": ["Elle absorbe davantage la lumière (surtout dans le bleu et le vert) et devient plus sombre", "Elle devient totalement transparente comme de l'eau pure", "Elle émet de la lumière bleue"], "rep": "Elle absorbe davantage la lumière (surtout dans le bleu et le vert) et devient plus sombre"},
            {"id": "qlm1_3", "q": "Quelle grandeur physique mesure le spectrophotomètre en comparant l'intensité lumineuse avant et après la cuve d'huile ?", "options": ["L'absorbance (ou la transmittance) en fonction de la longueur d'onde", "La viscosité cinématique", "La température d'éclair"], "rep": "L'absorbance (ou la transmittance) en fonction de la longueur d'onde"},
            {"id": "qlm1_4", "q": "Quelle loi optique relie l'absorbance A d'un fluide à la concentration c des impuretés dissoutes et à l'épaisseur l de la cuve ?", "options": ["La loi de Beer-Lambert (A = ε × l × c)", "La loi d'Ohm", "La loi de Kepler"], "rep": "La loi de Beer-Lambert (A = ε × l × c)"},
            {"id": "qlm1_5", "q": "Pourquoi une huile neuve de couleur jaune clair absorbe-t-elle principalement les radiations bleues ?", "options": ["Parce que le jaune est la couleur complémentaire du bleu", "Parce que le bleu est plus lourd", "Parce que la cuve est en verre rouge"], "rep": "Parce que le jaune est la couleur complémentaire du bleu"},
            {"id": "qlm1_6", "q": "Quel composant optique décompose la lumière blanche en longueurs d'onde précises à l'intérieur d'un spectrophotomètre d'atelier ?", "options": ["Un réseau de diffraction ou un prisme dispersif", "Un miroir plan", "Une vitre teintée"], "rep": "Un réseau de diffraction ou un prisme dispersif"},
            {"id": "qlm1_7", "q": "Dans la norme colorimétrique ASTM D1500 des huiles industrielles, que signifie le passage de l'indice couleur de 1,5 à 6,5 ?", "options": ["Une forte dégradation thermique ou oxydation nécessitant une vidange préventive", "Une amélioration de la lubrification", "Une baisse de niveau dans le réservoir"], "rep": "Une forte dégradation thermique ou oxydation nécessitant une vidange préventive"},
            {"id": "qlm1_8", "q": "Quelle opération d'étalonnage doit effectuer le technicien avant chaque analyse spectrophotométrique d'échantillon ?", "options": ["Faire le zéro (blanc optique) avec une cuve remplie d'huile neuve de référence ou de solvant pur", "Chauffer la lampe à 1000 °C", "Secouer le spectromètre"], "rep": "Faire le zéro (blanc optique) avec une cuve remplie d'huile neuve de référence ou de solvant pur"},
            {"id": "qlm1_9", "q": "Si la transmittance T d'un échantillon d'huile chute à 10 % (0,10), que peut-on en déduire ?", "options": ["90 % de la lumière incidente a été absorbée par les impuretés ou produits d'oxydation", "90 % de la lumière traverse l'huile", "L'ampoule du capteur est neuve"], "rep": "90 % de la lumière incidente a été absorbée par les impuretés ou produits d'oxydation"},
            {"id": "qlm1_10", "q": "Quelle maintenance permet l'analyse optique régulière des huiles sans démonter les machines ?", "options": ["La maintenance prédictive (ou conditionnelle)", "La maintenance corrective d'urgence", "La maintenance destructive"], "rep": "La maintenance prédictive (ou conditionnelle)"},
        ],
        "trous": [
            ("1. L'analyse optique de la couleur des huiles relève de la maintenance .........", ["Choisir...", "prédictive", "corrective"], "prédictive", "lm_t1"),
            ("2. L'appareil mesurant l'absorption de la lumière selon la longueur d'onde est un .........", ["Choisir...", "spectrophotomètre", "manomètre"], "spectrophotomètre", "lm_t2"),
            ("3. L'absorbance d'un liquide est proportionnelle à sa concentration selon la loi de .........", ["Choisir...", "Beer-Lambert", "Newton"], "Beer-Lambert", "lm_t3"),
            ("4. Une huile jaune absorbe principalement les radiations de couleur .........", ["Choisir...", "bleue", "rouge"], "bleue", "lm_t4"),
            ("5. Plus une huile est oxydée, plus son ......... augmente.", ["Choisir...", "absorbance", "transmittance"], "absorbance", "lm_t5"),
            ("6. Le composant dispersif du spectrophotomètre peut être un prisme ou un .........", ["Choisir...", "réseau", "condensateur"], "réseau", "lm_t6"),
            ("7. Avant la mesure, il faut effectuer le réglage du ......... optique de référence.", ["Choisir...", "blanc", "noir"], "blanc", "lm_t7"),
            ("8. Une forte augmentation de l'indice couleur ASTM signale une ......... de l'huile.", ["Choisir...", "oxydation", "dilution"], "oxydation", "lm_t8"),
            ("9. La lumière visible s'étend de 400 nm à ......... nm.", ["Choisir...", "700", "200"], "700", "lm_t9"),
            ("10. Le contrôle d'huile évite une panne mécanique en déclenchant une ......... ciblée.", ["Choisir...", "vidange", "peinture"], "vidange", "lm_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qlm2_1", "q": "Quelle grandeur exprimée en kelvins (K) caractérise la teinte (chaude ou froide) d'un éclairage LED d'atelier de maintenance ?", "options": ["La température de couleur", "L'indice de réfraction", "La fréquence secteur"], "rep": "La température de couleur"},
            {"id": "qlm2_2", "q": "Quelle température de couleur (blanc neutre lumière du jour) est recommandée par la norme NF EN 12464-1 pour les postes de contrôle qualité et câblage électrique ?", "options": ["4000 K à 5000 K (blanc neutre à froid)", "1800 K (lumière de bougie)", "10000 K (bleu intense)"], "rep": "4000 K à 5000 K (blanc neutre à froid)"},
            {"id": "qlm2_3", "q": "Que mesure l'Indice de Rendu des Couleurs (IRC ou Ra, noté sur 100) d'une lampe d'atelier ?", "options": ["Sa capacité à restituer fidèlement les vraies couleurs des objets par rapport à la lumière du soleil", "Sa consommation électrique en watts", "Sa durée de vie en heures"], "rep": "Sa capacité à restituer fidèlement les vraies couleurs des objets par rapport à la lumière du soleil"},
            {"id": "qlm2_4", "q": "Quel risque encourt un technicien de maintenance qui câble une armoire électrique sous une lampe à vapeur de sodium basse pression (IRC très faible < 25) ?", "options": ["Confondre les couleurs des fils (ex : fil bleu neutre, fil rouge phase, fil vert/jaune terre)", "Avoir trop de lumière blanche", "Surchauffer les câbles"], "rep": "Confondre les couleurs des fils (ex : fil bleu neutre, fil rouge phase, fil vert/jaune terre)"},
            {"id": "qlm2_5", "q": "Pourquoi une lampe à vapeur de sodium basse pression ne permet-elle pas de distinguer les couleurs des fils électriques ?", "options": ["Parce qu'elle émet un spectre de raies quasi monochromatique jaune (589 nm) dépourvu de bleu et de rouge", "Parce qu'elle clignote trop vite", "Parce qu'elle n'émet que des ultraviolets"], "rep": "Parce qu'elle émet un spectre de raies quasi monochromatique jaune (589 nm) dépourvu de bleu et de rouge"},
            {"id": "qlm2_6", "q": "Quel IRC minimal est exigé dans un atelier de contrôle couleur ou de câblage de précision ?", "options": ["IRC ≥ 80 (voire IRC ≥ 90 pour le contrôle chromatique fin)", "IRC = 20", "IRC = 0"], "rep": "IRC ≥ 80 (voire IRC ≥ 90 pour le contrôle chromatique fin)"},
            {"id": "qlm2_7", "q": "Comment se caractérise le spectre d'une LED blanche utilisée dans les projecteurs modernes d'atelier ?", "options": ["Un spectre continu enrichi par un pic bleu (450 nm) et une bande jaune-verte", "Une raie unique à 650 nm", "Un spectre exclusivement infrarouge"], "rep": "Un spectre continu enrichi par un pic bleu (450 nm) et une bande jaune-verte"},
            {"id": "qlm2_8", "q": "Quel appareil utilise le responsable maintenance pour vérifier le niveau d'éclairement (en lux) sur un établi ?", "options": ["Un luxmètre", "Un sonomètre", "Un ohmmètre"], "rep": "Un luxmètre"},
            {"id": "qlm2_9", "q": "Que se passe-t-il si une ampoule LED d'atelier vieillit et que sa couche de phosphore jaune se dégrade ?", "options": ["La lumière devient excessivement bleutée (hausse de la température de couleur) et fatigue les yeux", "La lumière devient rouge vif", "L'ampoule produit un spectre d'absorption"], "rep": "La lumière devient excessivement bleutée (hausse de la température de couleur) et fatigue les yeux"},
            {"id": "qlm2_10", "q": "Quelle est l'unité de mesure de l'éclairement lumineux reçu par un plan de travail ?", "options": ["Le lux (lx)", "Le kelvin (K)", "Le nanomètre (nm)"], "rep": "Le lux (lx)"},
        ],
        "trous": [
            ("1. La teinte chaude ou froide d'une lampe est donnée par sa ......... de couleur en kelvins.", ["Choisir...", "température", "puissance"], "température", "lm_t1"),
            ("2. Pour un atelier de maintenance, on choisit un blanc neutre autour de ......... K.", ["Choisir...", "4500", "2000"], "4500", "lm_t2"),
            ("3. La fidélité des couleurs sous une lampe est mesurée par l'indice ......... (sur 100).", ["Choisir...", "IRC", "ISO"], "IRC", "lm_t3"),
            ("4. Une lampe au sodium émet une lumière jaune ......... à 589 nm.", ["Choisir...", "monochromatique", "blanche"], "monochromatique", "lm_t4"),
            ("5. Sous une lampe au sodium, il est impossible de distinguer la ......... des fils électriques.", ["Choisir...", "couleur", "longueur"], "couleur", "lm_t5"),
            ("6. La lumière du Soleil possède un IRC égal à .........", ["Choisir...", "100", "50"], "100", "lm_t6"),
            ("7. L'éclairement d'un établi se mesure en lux à l'aide d'un .........", ["Choisir...", "luxmètre", "voltmètre"], "luxmètre", "lm_t7"),
            ("8. Pour le câblage de précision, l'IRC doit être supérieur à .........", ["Choisir...", "80", "20"], "80", "lm_t8"),
            ("9. Une lumière à 2700 K est qualifiée de blanc .........", ["Choisir...", "chaud", "froid"], "chaud", "lm_t9"),
            ("10. Le spectre d'une LED blanche combine un pic ......... et une émission jaune.", ["Choisir...", "bleu", "vert"], "bleu", "lm_t10"),
        ]
    }
}


def mettre_a_jour_lum_maint_matplotlib(sujet_idx):
    """Banc d'essai optique Lumière & Couleurs adapté à la Maintenance Industrielle."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        couleur_eclairage = st.session_state.get("radio_lm_s0", "Lumière Verte (530 nm)")
        coul_map = {
            "Lumière Blanche (RVB)": ("#ffffff", "#ef4444", "FAIBLE CONTRASTE : Le défaut rouge ressort sur fond clair."),
            "Lumière Rouge (650 nm)": ("#ef4444", "#ef4444", "DÉFAUT INVISIBLE : Le défaut rouge et le fond renvoient le rouge !"),
            "Lumière Verte (530 nm)": ("#22c55e", "#0f172a", "CONTRASTE MAXIMAL : Le défaut rouge absorbe le vert et apparaît NOIR !")
        }
        c_faisceau, c_defaut_vu, msg = coul_map[couleur_eclairage]

        ax.add_patch(patches.Rectangle((80, 35), 90, 35, facecolor="#334155", edgecolor="white"))
        ax.text(125, 52, "Projecteur LED", color="white", fontsize=8, fontweight="bold", ha="center", va="center")
        ax.fill(list((110, 140, 320, 220)), list((70, 70, 185, 185)), color=c_faisceau, alpha=0.25)

        ax.add_patch(patches.Rectangle((190, 185), 160, 28, facecolor="#94a3b8", edgecolor="white"))
        ax.add_patch(patches.Rectangle((255, 185), 30, 10, facecolor="#ef4444"))
        ax.text(270, 225, "Pièce usinée + Défaut rouge", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

        ax.add_patch(patches.Rectangle((410, 45), 95, 45, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(457, 67, "Caméra Vision\n(Capteur)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.add_patch(patches.Rectangle((410, 115), 95, 75, facecolor=c_faisceau, edgecolor="white", lw=1.5))
        ax.add_patch(patches.Rectangle((442, 138), 30, 28, facecolor=c_defaut_vu, edgecolor="#64748b"))
        ax.text(457, 202, "Image perçue caméra", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        ax.text(25, 18, "VISION INDUSTRIELLE : DÉTECTION DE DÉFAUTS PAR ÉCLAIRAGE COLORÉ", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 32, msg, color="#22c55e" if "MAXIMAL" in msg else "#f59e0b", fontsize=8, fontweight="bold")
        st.session_state.lm_mesure_courante = (couleur_eclairage, "Défaut Rouge", "Noir pur" if "MAXIMAL" in msg else "Peu contrasté", "OPTIMAL" if "MAXIMAL" in msg else "À CORRIGER")

    elif sujet_idx == 1:
        usure_pct = st.session_state.get("slider_lm_s1", 35.0)
        absorbance = round(0.15 + (usure_pct / 100.0) * 1.85, 2)
        transmittance = round(100.0 * (10 ** (-absorbance)), 1)

        ax.add_patch(patches.Rectangle((45, 105), 75, 50, facecolor="#eab308", edgecolor="white"))
        ax.text(82, 130, "Source\nBlanche", color="#0f172a", fontsize=8, fontweight="bold", ha="center", va="center")
        ax.plot(list((120, 240)), list((130, 130)), color="#ffffff", lw=6)

        r_h = max(60, int(245 - usure_pct * 1.8))
        g_h = max(30, int(200 - usure_pct * 1.7))
        b_h = max(10, int(40 - usure_pct * 0.3))
        c_huile = f"#{r_h:02x}{g_h:02x}{b_h:02x}"
        ax.add_patch(patches.Rectangle((240, 80), 65, 100, facecolor=c_huile, edgecolor="#38bdf8", lw=2))
        ax.text(272, 68, f"Cuve Huile\n(Usure {usure_pct:.0f}%)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        alpha_out = max(0.15, transmittance / 100.0)
        ax.plot(list((305, 440)), list((130, 130)), color="#f97316", lw=6, alpha=alpha_out)

        ax.add_patch(patches.Rectangle((440, 100), 105, 60, facecolor="#1e293b", edgecolor="#22c55e", lw=1.5))
        ax.text(492, 130, f"Capteur Spectro\nT = {transmittance:.1f}%\nA = {absorbance:.2f}", color="#86efac", fontsize=8, fontweight="bold", ha="center", va="center")

        diag = "HUILE CONFORME : Transmittance élevée." if usure_pct < 50 else ("ALERTE OXYDATION : Prévoir vidange !" if usure_pct < 80 else "CRITIQUE : Huile saturée, vidange immédiate !")
        c_diag = "#22c55e" if usure_pct < 50 else ("#f59e0b" if usure_pct < 80 else "#ef4444")
        ax.text(25, 18, "MAINTENANCE PRÉDICTIVE : SPECTROPHOTOMÉTRIE DES HUILES (BEER-LAMBERT)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Absorbance A = {absorbance:.2f}  |  Transmittance T = {transmittance:.1f}%  =>  {diag}", color=c_diag, fontsize=8, fontweight="bold")
        st.session_state.lm_mesure_courante = (f"Usure = {usure_pct:.0f}%", f"A = {absorbance:.2f}", f"T = {transmittance:.1f}%", "OK" if usure_pct < 50 else "VIDANGE")

    else:
        type_lampe = st.session_state.get("radio_lm_s2", "LED Atelier Blanc Neutre (4500 K - IRC 92)")
        if "Sodium" in type_lampe:
            c_amb, c_fil_bleu, c_fil_vert, irc_val = "#f59e0b", "#78350f", "#92400e", 22
            statut = "DANGER CÂBLAGE : IRC = 22 ! Impossible de distinguer le bleu, le vert et le rouge !"
        elif "Chaud" in type_lampe:
            c_amb, c_fil_bleu, c_fil_vert, irc_val = "#fed7aa", "#1e40af", "#15803d", 82
            statut = "ACCEPTABLE : IRC = 82 (2700 K). Couleurs visibles mais légère dominante orangée."
        else:
            c_amb, c_fil_bleu, c_fil_vert, irc_val = "#f8fafc", "#2563eb", "#22c55e", 92
            statut = "CONFORME NORME ATELIER : IRC = 92 (4500 K). Distinction parfaite des conducteurs !"

        ax.add_patch(patches.Rectangle((60, 50), 480, 175, facecolor=c_amb, edgecolor="#38bdf8", lw=2))
        ax.text(300, 72, f"Établi de câblage sous : {type_lampe}", color="#0f172a", fontsize=9, fontweight="bold", ha="center")

        ax.add_patch(patches.Rectangle((120, 105), 360, 18, facecolor=c_fil_bleu, edgecolor="#0f172a"))
        ax.text(300, 114, "Conducteur Neutre (Bleu)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.add_patch(patches.Rectangle((120, 140), 360, 18, facecolor=c_fil_vert, edgecolor="#0f172a"))
        ax.text(300, 149, "Conducteur Protection PE (Vert/Jaune)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.add_patch(patches.Rectangle((120, 175), 360, 18, facecolor="#dc2626", edgecolor="#0f172a"))
        ax.text(300, 184, "Conducteur Phase (Rouge)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.text(25, 18, "ERGONOMIE & SÉCURITÉ : TEMPÉRATURE DE COULEUR ET INDICE IRC EN ATELIER", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color="#22c55e" if irc_val >= 90 else ("#f59e0b" if irc_val >= 80 else "#ef4444"), fontsize=8, fontweight="bold")
        st.session_state.lm_mesure_courante = (type_lampe.split("(")[0].strip(), f"IRC = {irc_val}", "Rendu fidèle" if irc_val >= 80 else "Altéré", "CONFORME" if irc_val >= 80 else "NON CONFORME")

    return fig


def afficher_atelier_lum_maint(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet de maintenance ci-dessus.")
        return
    banque = BANQUES_LUM_MAINT[sujet_idx]
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





def afficher_questions_optique2(verrouille=False):
    col_double_quiz_opt2, col_double_trous_opt2 = st.columns(2)

    # --- COLONNE DE GAUCHE : VOTRE QUIZ DE 10 QUESTIONS ---
    with col_double_quiz_opt2:
        st.markdown("##### Évaluation : Les différentes lumières (10 pts)")
        if "ordre_questions_opt2" not in st.session_state:
            questions_opt2_base = [
                ("q1", "Quel type de spectre obtient-on en analysant la lumière émise par un gaz d'atomes isolés excités ?"),
                ("q2", "Quelle source lumineuse classique produit un spectre continu contenant toutes les radiations colorées ?"),
                ("q3", "Lors du test de flamme, quelle couleur caractéristique prend la combustion du chlorure de Sodium (Na) ?"),
                ("q4", "Quelle couleur de flamme spécifique permet d'identifier la présence d'ions Cuivre (Cu) ?"),
                ("q5", "Pourquoi les raies d'émission d'un élément chimique constituent-elles sa signature ou carte d'identité ?"),
                ("q6", "Comment qualifie-t-on le spectre d'une étoile qui traverse une atmosphère gazeuse plus froide ?"),
                ("q7", "Quel instrument d'optique muni d'un élément dispersif permet d'observer ces raies colorées ?"),
                ("q8", "Quelle est l'unité de mesure utilisée pour repérer la position exacte d'une raie sur l'écran ?"),
                ("q9", "Si une source émet une raie unique à 589 nm, dans quel domaine de couleur se situe-t-elle ?"),
                ("q10", "Le spectre de la lumière émise par le Soleil reçu sur Terre est un spectre :")
            ]
            random.shuffle(questions_opt2_base)
            st.session_state.ordre_questions_opt2 = questions_opt2_base

        dict_quiz_opt2 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt2, 1):
            cle_qo2 = f"col_g_quiz_opt2_{q_id}"
            cle_opts_unique = f"opts_opt2_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Spectre d'émission de raies", "Spectre continu", "Spectre d'absorption"]
                elif q_id == "q2": copie_opts = ["Corps dense incandescent (Lampe à filament)", "Lampe à vapeur de gaz", "Laser monochromatique"]
                elif q_id == "q3": copie_opts = ["Jaune orangé intense", "Vert pré", "Bleu azur"]
                elif q_id == "q4": copie_opts = ["Vert pré / turquoise", "Jaune orangé", "Violet pourpre"]
                elif q_id == "q5": copie_opts = ["Chaque élément a des raies uniques", "Elles dépendent de la température", "Elles sont toutes blanches"]
                elif q_id == "q6": copie_opts = ["Spectre d'absorption de raies", "Spectre d'émission continu", "Spectre de diffraction"]
                elif q_id == "q7": copie_opts = ["Spectroscope / Spectromètre", "Microscope", "Lentille convergente simple"]
                elif q_id == "q8": copie_opts = ["Nanomètre (nm)", "Millimètre (mm)", "Hertz (Hz)"]
                elif q_id == "q9": copie_opts = ["Jaune", "Rouge", "Violet"]
                elif q_id == "q10": copie_opts = ["D'absorption de raies (Fraunhofer)", "D'émission pur", "Continu sans aucune raie"]
                
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo2, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt2[f"{q_id}_opt2"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo2, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS COMPLET (10 ITEMS = 10 PTS) ---
    with col_double_trous_opt2:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 items) - Optique 2 (10 pts)")
        
        items_trous_o2 = [
            ("1. L'excitation thermique de sels métalliques par une flamme produit un spectre d'", ["Choisir...", "Émission", "Absorption", "Réflexion"], "opt2_t1"),
            ("2. La combustion du Sodium se caractérise par une couleur intense dans le", ["Choisir...", "Jaune", "Vert", "Bleu"], "opt2_t2"),
            ("3. À l'inverse, un solide porté à haute température émet une lumière au spectre", ["Choisir...", "Continu", "Discontinu", "Monochrome"], "opt2_t3"),
            ("4. Le rayonnement solaire reçu sur Terre comporte de fines raies sombres d'", ["Choisir...", "Absorption", "Émission", "Diffraction"], "opt2_t4"),
            ("5. La position précise de ces signatures se mesure sur l'écran en", ["Choisir...", "Nanomètres", "Millimètres", "Degrés"], "opt2_t5"),
            ("6. La combustion du chlorure de Cuivre donne à la flamme une teinte", ["Choisir...", "Verte", "Rouge", "Violette"], "opt2_t6"),
            ("7. Chaque atome possède des raies spectrales qui constituent sa carte d'", ["Choisir...", "Identité", "Énergie", "Absorption"], "opt2_t7"),
            ("8. Une lampe à vapeur de Mercure ou de Sodium émet un spectre de", ["Choisir...", "Raies", "Bandes", "Continu"], "opt2_t8"),
            ("9. Les raies noires du spectre solaire portent le nom de raies de", ["Choisir...", "Fraunhofer", "Newton", "Descartes"], "opt2_t9"),
            ("10. L'appareil qui décompose la lumière pour analyser ses raies est un", ["Choisir...", "Spectroscope", "Microscope", "Télescope"], "opt2_t10"),
        ]

        dict_trous_opt2 = {}
        for enonce, options, cle in items_trous_o2:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2:
                val = st.selectbox("", options, key=cle, disabled=verrouille, label_visibility="collapsed")
                dict_trous_opt2[f"{cle.replace('opt2_', '')}_opt2"] = val

    return dict_quiz_opt2, dict_trous_opt2


def afficher_questions_optique1(verrouille=False):
    col_double_quiz_opt1, col_double_trous_opt1 = st.columns(2)

    sol_m = st.session_state.get("opt1_scenario", {})
    d_r_f = f"{sol_m.get('D_r', 0.0):.1f}"
    d_v_f = f"{sol_m.get('D_v', 0.0):.1f}"
    d_vi_f = f"{sol_m.get('D_vi', 0.0):.1f}"

    # --- COLONNE DE GAUCHE : LE QUIZ INTERACTIF ---
    with col_double_quiz_opt1:
        st.markdown("##### Quiz sur la dispersion (10 questions) - Optique 1")
        if "ordre_questions_opt1" not in st.session_state:
            questions_opt1_base = [
                ("q1", "L'angle de déviation minimale calculé pour le rayonnement rouge vaut :"),
                ("q2", "L'angle de déviation maximale obtenu pour le rayonnement violet vaut :"),
                ("q3", "Le phénomène de séparation des couleurs par le prisme s'appelle la :"),
                ("q4", "La loi de Snell-Descartes relie les indices des milieux aux sinus des :"),
                ("q5", "Quelle couleur possède l'indice de réfraction le plus élevé dans le verre :"),
                ("q6", "La recomposition de la lumière blanche peut être observée grâce au disque de :"),
                ("q7", "La relation géométrique liée à l'angle au sommet A du prisme est :"),
                ("q8", "Lorsque la vitesse du disque de Newton est maximale, l'œil perçoit la couleur :"),
                ("q9", "Si l'indice de base du prisme augmente, la déviation globale de tous les rayons :"),
                ("q10", "Un rayonnement composé d'une seule radiation chromatique est qualifié de :")
            ]
            random.shuffle(questions_opt1_base)
            st.session_state.ordre_questions_opt1 = questions_opt1_base

        dict_quiz_opt1 = {}
        opts_num = ["Choisir...", d_r_f, d_v_f, d_vi_f, "Blanche", "Noir"]
        opts_num = list(dict.fromkeys(opts_num))

        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt1, 1):
            cle_qo1 = f"col_g_quiz_opt1_{q_id}_opt1"
            cle_opts_unique = f"opts_opt1_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q3": copie_opts = ["Dispersion", "Réflexion", "Absorption"]
                elif q_id == "q4": copie_opts = ["Angles", "Longueurs", "Indices"]
                elif q_id == "q5": copie_opts = ["Violet", "Rouge", "Vert"]
                elif q_id == "q6": copie_opts = ["Newton", "Descartes", "Snell"]
                elif q_id == "q7": copie_opts = ["A = r1 + r2", "A = i1 + i2", "A = r1 - r2"]
                elif q_id == "q8": copie_opts = ["Blanche", "Grise", "Noire"]
                elif q_id == "q9": copie_opts = ["Augmente", "Diminue", "Reste fixe"]
                elif q_id == "q10": copie_opts = ["Monochromatique", "Polychromatique", "Laser"]
                else: copie_opts = list(set(opts_num[1:]))
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo1, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt1[f"{q_id}_opt1"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo1, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS COMPLET (10 ITEMS = 10 PTS) ---
    with col_double_trous_opt1:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 items) - Optique 1")
        
        items_trous_o1 = [
            ("1. Le prisme permet de séparer les radiations de la lumière blanche par", ["Choisir...", "Dispersion", "Réflexion", "Diffraction"], "opt1_t1"),
            ("2. Chaque couleur possède son propre indice de réfraction. Le rouge est le moins", ["Choisir...", "Dévié", "Ralenti", "Absorbé"], "opt1_t2"),
            ("3. À l'inverse, la radiation visible la plus déviée par le prisme est le", ["Choisir...", "Violet", "Jaune", "Vert"], "opt1_t3"),
            ("4. Une lumière composée d'une seule radiation colorée est qualifiée de", ["Choisir...", "Monochromatique", "Polychromatique", "Blanche"], "opt1_t4"),
            ("5. La rotation rapide du disque coloré montre la recomposition", ["Choisir...", "Blanche", "Monochrome", "Spectrale"], "opt1_t5"),
            ("6. Les trois couleurs primaires de la synthèse additive sont Rouge, Vert et", ["Choisir...", "Bleu", "Jaune", "Cyan"], "opt1_t6"),
            ("7. En synthèse additive, l'addition du Rouge et du Vert produit du", ["Choisir...", "Jaune", "Magenta", "Cyan"], "opt1_t7"),
            ("8. En synthèse soustractive, les trois couleurs primaires sont Cyan, Magenta et", ["Choisir...", "Jaune", "Bleu", "Rouge"], "opt1_t8"),
            ("9. La superposition des trois filtres Cyan, Magenta et Jaune donne du", ["Choisir...", "Noir", "Blanc", "Gris"], "opt1_t9"),
            ("10. L'unité utilisée pour exprimer la longueur d'onde d'une couleur est le", ["Choisir...", "Nanomètre", "Millimètre", "Degré"], "opt1_t10"),
        ]

        dict_trous_opt1 = {}
        for enonce, options, cle in items_trous_o1:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2:
                val = st.selectbox("", options, key=cle, disabled=verrouille, label_visibility="collapsed")
                dict_trous_opt1[f"{cle.replace('opt1_', '')}_opt1"] = val

    return dict_quiz_opt1, dict_trous_opt1



def afficher_atelier_hist_lumiere(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 1 (Histoire de la lumière)."""
    questions_hl = [
        {"id": "qhl1", "q": "Quel savant grec antique a énoncé les premières lois de la réflexion sur les miroirs dans son traité Catoptrique ?", "options": ["Euclide", "Galilée", "Isaac Newton"], "rep": "Euclide"},
        {"id": "qhl2", "q": "Quel savant arabe du XIe siècle (Livre de l'Optique) a prouvé que la lumière entre dans l'œil depuis les objets éclairés ?", "options": ["Ibn al-Haytham (Alhazen)", "Aristote", "Pythagore"], "rep": "Ibn al-Haytham (Alhazen)"},
        {"id": "qhl3", "q": "En quelle année Isaac Newton a-t-il démontré avec un prisme que la lumière blanche est composée de 7 couleurs ?", "options": ["1666", "1492", "1889"], "rep": "1666"},
        {"id": "qhl4", "q": "Quel astronome danois a mesuré pour la première fois que la vitesse de la lumière est finie en observant les satellites de Jupiter en 1676 ?", "options": ["Ole Rømer", "Nicolas Copernic", "Johannes Kepler"], "rep": "Ole Rømer"},
        {"id": "qhl5", "q": "Quelle est la valeur exacte de la vitesse de propagation de la lumière dans le vide ?", "options": ["299 792 458 m/s (environ 300 000 km/s)", "340 m/s", "1 500 m/s"], "rep": "299 792 458 m/s (environ 300 000 km/s)"},
        {"id": "qhl6", "q": "Quel physicien britannique a prouvé en 1801 la nature ondulatoire de la lumière grâce à son expérience des fentes d'interférence ?", "options": ["Thomas Young", "Blaise Pascal", "André-Marie Ampère"], "rep": "Thomas Young"},
        {"id": "qhl7", "q": "Quel physicien écossais a unifié l'électricité, le magnétisme et la lumière en démontrant que la lumière est une onde électromagnétique ?", "options": ["James Clerk Maxwell", "Michael Faraday", "James Watt"], "rep": "James Clerk Maxwell"},
        {"id": "qhl8", "q": "Quel physicien allemand a découvert en 1814 les fines raies noires d'absorption dans le spectre du Soleil ?", "options": ["Joseph von Fraunhofer", "Wilhelm Röntgen", "Heinrich Hertz"], "rep": "Joseph von Fraunhofer"},
        {"id": "qhl9", "q": "Comment appelle-t-on les grains d'énergie lumineuse introduits par Max Planck et Albert Einstein en 1905 ?", "options": ["Les photons", "Les électrons", "Les neutrons"], "rep": "Les photons"},
        {"id": "qhl10", "q": "Quelle expérience inventée par Isaac Newton permet de recomposer la lumière blanche en faisant tourner rapidement un disque coloré ?", "options": ["Le disque de Newton", "Le pendule de Foucault", "La pile de Volta"], "rep": "Le disque de Newton"},
    ]

    if "ordre_quiz_hl_aleatoire" not in st.session_state:
        random.shuffle(questions_hl)
        st.session_state.ordre_quiz_hl_aleatoire = questions_hl

    champs_hl = [
        ("1. Au XIe siècle, ......... démontre que l'œil reçoit la lumière des objets.", ["Choisir...", "Alhazen", "Aristote"], "Alhazen", "hl_t1"),
        ("2. En 1666, Isaac ......... décompose la lumière blanche avec un prisme.", ["Choisir...", "Newton", "Galilée"], "Newton", "hl_t2"),
        ("3. La lumière blanche est composée d'une infinité de radiations .........", ["Choisir...", "colorées", "sonores"], "colorées", "hl_t3"),
        ("4. En 1676, Ole ......... prouve que la lumière a une vitesse finie.", ["Choisir...", "Rømer", "Descartes"], "Rømer", "hl_t4"),
        ("5. Dans le vide, la lumière se propage à environ 300 000 ......... par seconde.", ["Choisir...", "kilomètres", "mètres"], "kilomètres", "hl_t5"),
        ("6. En 1801, Thomas ......... met en évidence les interférences lumineuses.", ["Choisir...", "Young", "Euler"], "Young", "hl_t6"),
        ("7. En 1814, Joseph von ......... observe les raies sombres du spectre solaire.", ["Choisir...", "Fraunhofer", "Kepler"], "Fraunhofer", "hl_t7"),
        ("8. James Clerk ......... démontre que la lumière est une onde électromagnétique.", ["Choisir...", "Maxwell", "Joule"], "Maxwell", "hl_t8"),
        ("9. En 1905, Albert ......... explique que la lumière est transportée par des photons.", ["Choisir...", "Einstein", "Curie"], "Einstein", "hl_t9"),
        ("10. La rotation rapide du disque de Newton montre la synthèse .........", ["Choisir...", "additive", "soustractive"], "additive", "hl_t10"),
    ]

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Historique : La lumière et les couleurs (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_hl_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"hl_at1_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Historique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_hl:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")



def gerer_changement_metal():
    """Moteur exclusif Atelier 2 : Interroge le catalogue de flammes."""
    nom_selectionne = st.session_state.var_sel_metal
    catalogue = st.session_state.catalogue_metaux
    if nom_selectionne in catalogue:
        return catalogue[nom_selectionne]
    return {"couleur": "#0d1117", "descr": "Aucune propriete enregistree."}


def declencher_test_flamme_web():
    """Moteur séquentiel de l'Atelier 2 : simule le versement de la poudre."""
    if st.session_state.var_combustion_active:
        st.session_state.var_combustion_active = False
        st.session_state.var_versement_poudre = False
        return

    st.session_state.var_versement_poudre = True
    st.session_state.var_combustion_active = False

    # Message d'attente textuel pur pendant le versement
    with st.spinner(
        "Action : Versement de l'echantillon de sel dans la coupelle en cours..."
    ):
        time.sleep(2.0)

    st.session_state.var_versement_poudre = False
    st.session_state.var_combustion_active = True

def get_rgb_continu(ratio, type_spectre="continu"):
    """Moteur chromatique : calcule les composantes spectrales RGB selon la position."""
    r, g, b = 0, 0, 0
    if ratio < 0.25:
        r = 255
        g = int(ratio * 4 * 255)
    elif ratio < 0.5:
        g = 255
        r = int((0.5 - ratio) * 4 * 255)
    elif ratio < 0.75:
        g = 255
        b = int((ratio - 0.5) * 4 * 255)
    else:
        b = 255
        g = int((1.0 - ratio) * 4 * 255)
        r = int((ratio - 0.75) * 4 * 150)

    # Modulateurs d'intensite selon la technologie de la lampe
    if type_spectre == "continu_chaude":
        b = int(b * 0.25)
        g = int(g * 0.7)
    elif type_spectre == "led_froide":
        if 0.65 < ratio < 0.85:
            b = min(255, int(b * 1.5))
        elif 0.45 < ratio <= 0.65:
            b = int(b * 0.3)
            g = int(g * 0.5)
    elif type_spectre == "mixte":
        r, g, b = int(r * 0.2), int(g * 0.2), int(b * 0.2)

    return f"#{r:02x}{g:02x}{b:02x}"

def dessiner_spectre_flamme_combustion():
    """Génère la figure du spectre d'émission atomique réel du métal (400 à 900 nm)."""
    metal_choisi = st.session_state.var_sel_metal
    info = st.session_state.catalogue_metaux[metal_choisi]

    fig, ax = plt.subplots(figsize=(10, 1.8), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(400, 900)
    ax.set_ylim(-0.2, 1.2)
    ax.axis("off")

    # Fond noir de la chambre d'analyse
    ax.add_patch(
        plt.Rectangle((400, 0), 500, 1.0, fill=True, facecolor="black", lw=0)
    )

    if st.session_state.var_combustion_active:
        for wl, couleur, intensite in info.get("raies", []):
            if 400 <= wl <= 900:
                ax.axvline(x=wl, color=couleur, lw=4, alpha=intensite)
                ax.text(
                    wl,
                    -0.25,
                    f"{wl}nm",
                    color="#94a3b8",
                    fontsize=7,
                    fontname="Courier",
                    ha="center",
                )
    else:
        ax.text(
            650,
            0.5,
            "[ Allumez le bruleur pour observer le spectre d'emission ]",
            color="#475569",
            fontsize=9,
            style="italic",
            ha="center",
            va="center",
        )

    # Règle graduée de référence (400 à 900 nm)
    for g in range(400, 901, 50):
        ax.plot([g, g], [1.0, 1.06], color="white", lw=1)
        ax.text(g, 1.15, str(g), color="#64748b", fontsize=7, ha="center")

    rect_cadre = plt.Rectangle(
        (400, 0), 500, 1.0, fill=False, edgecolor="#334155", lw=1.5
    )
    ax.add_patch(rect_cadre)

    return fig

def dessiner_montage_complet_atelier2():
    """Moteur graphique unifie de l'Atelier 2 : Dessine le banc d'optique complet

    et projette les faisceaux colores reels vers l'ecran.
    """
    nom_selectionne = st.session_state.source_lumineuse_choisie
    info = st.session_state.lampes_data[nom_selectionne]

    # Coordonnees fixes du banc d'optique calquees sur Tkinter
    x_lampe, y_lampe = 60, 120
    x_fente, x_lentille, x_prisme, y_axe = 190, 330, 520, 120
    x_ecran, y_ecran_haut, y_ecran_bas = 960, 30, 290
    h_spectre = y_ecran_bas - y_ecran_haut - 30

    fig, ax = plt.subplots(figsize=(11.6, 4.5), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, 1050)
    ax.set_ylim(0, 320)
    ax.invert_yaxis()  # Maintient le repere Y identique a Tkinter
    ax.axis("off")

    # 1. Trace des faisceaux lumineux geometriques avant le prisme
    ax.fill(
        [x_lampe + 25, x_fente, x_fente],
        [y_axe, y_axe - 12, y_axe + 12],
        color=info["couleur_source"],
        alpha=0.25,
    )
    ax.fill(
        [x_fente, x_fente, x_lentille, x_lentille],
        [y_axe - 12, y_axe + 12, y_axe + 45, y_axe - 45],
        color=info["couleur_source"],
        alpha=0.25,
    )
    ax.fill(
        [x_lentille, x_lentille, x_prisme - 20, x_prisme - 25],
        [y_axe - 45, y_axe + 45, y_axe + 35, y_axe - 20],
        color=info["couleur_source"],
        alpha=0.25,
    )

    # 2. Projection des rayons colores disperses apres le prisme
    x_sortie_prisme, y_sortie_prisme = x_prisme + 20, y_axe + 15

    if info["type"] in [
        "continu",
        "continu_chaude",
        "led_froide",
        "led_chaude",
        "mixte",
    ]:
        for i in range(int(h_spectre)):
            ratio = i / h_spectre
            c_hex = get_rgb_continu(
                ratio, info["type"]
            )  # Utilise le moteur chromatique de l'Atelier 1
            y_pixel_ecran = y_ecran_haut + 15 + i
            ax.plot(
                [x_sortie_prisme, x_ecran],
                [y_sortie_prisme, y_pixel_ecran],
                color=c_hex,
                lw=1.5,
                alpha=0.7,
            )

    if "raies" in info:
        for wl, couleur, pos_relative in info["raies"]:
            y_pixel_ecran = y_ecran_bas - 15 - int(pos_relative * h_spectre)
            ax.plot(
                [x_sortie_prisme, x_ecran],
                [y_sortie_prisme, y_pixel_ecran],
                color=couleur,
                lw=2.5,
                alpha=0.9,
            )

    # 3. Dessin des composants materiels du banc
    # Source
    ax.add_patch(
        plt.Circle(
            (x_lampe, y_lampe),
            25,
            facecolor=info["couleur_source"],
            edgecolor="white",
            lw=2,
        )
    )
    ax.add_patch(
        plt.Rectangle(
            (x_lampe - 10, y_lampe + 25), 20, 25, facecolor="#455A64"
        )
    )
    ax.text(
        x_lampe,
        y_lampe - 35,
        "Source",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Fente
    ax.plot([x_fente, x_fente], [y_axe - 50, y_axe - 12], color="#90A4AE", lw=5)
    ax.plot([x_fente, x_fente], [y_axe + 12, y_axe + 50], color="#90A4AE", lw=5)
    ax.text(
        x_fente,
        y_axe - 60,
        "Fente",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Lentille L
    ax.plot(
        [x_lentille, x_lentille], [y_axe - 65, y_axe + 65], color="#4FC3F7", lw=2.5
    )
    ax.text(
        x_lentille,
        y_axe - 75,
        "Lentille L",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Prisme
    ax.add_patch(
        plt.Polygon(
            [[x_prisme, y_axe - 50], [x_prisme - 40, y_axe + 40], [x_prisme + 50, y_axe + 40]],
            facecolor="#E0F7FA",
            edgecolor="#80DEEA",
            lw=2,
        )
    )
    ax.text(
        x_prisme + 5,
        y_axe - 62,
        "Prisme",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Ecran
    ax.add_patch(
        plt.Rectangle(
            (x_ecran, y_ecran_haut),
            20,
            y_ecran_bas - y_ecran_haut,
            facecolor="#FFFFFF",
            edgecolor="#B0BEC5",
            lw=2,
        )
    )
    ax.text(
        x_ecran + 40,
        (y_ecran_haut + y_ecran_bas) / 2,
        "Ecran",
        color="white",
        fontsize=10,
        fontweight="bold",
        va="center",
        rotation=-90,
    )

    return fig


def dessiner_zoom_spectre_atelier2():
    """Génère la règle nanométrique horizontale zoomée du spectre de l'Atelier 2."""
    nom_selectionne = st.session_state.source_lumineuse_choisie
    info = st.session_state.lampes_data[nom_selectionne]
    largeur_s = 700

    fig, ax = plt.subplots(figsize=(10, 2.0), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, largeur_s)
    ax.set_ylim(-0.4, 1.4)
    ax.axis("off")

    if info["type"] in [
        "continu",
        "continu_chaude",
        "led_froide",
        "led_chaude",
        "mixte",
    ]:
        for i in range(largeur_s):
            ratio = i / largeur_s
            c_hex = get_rgb_continu(1.0 - ratio, info["type"])
            ax.plot([i, i], [0.02, 0.98], color=c_hex, lw=1.5, alpha=1.0)

    ax.add_patch(
        plt.Rectangle(
            (0, 0), largeur_s, 1.0, fill=False, edgecolor="white", lw=1.5
        )
    )

    if "raies" in info:
        for wl, couleur, pos_relative in info["raies"]:
            x_raie = int(pos_relative * largeur_s)
            ax.plot([x_raie, x_raie], [0.02, 0.98], color=couleur, lw=3.5)
            ax.text(
                x_raie,
                -0.25,
                f"{wl} nm",
                color="#ECEFF1",
                fontsize=8,
                fontname="Courier",
                fontweight="bold",
                ha="center",
            )

    for wl_test in range(400, 701, 50):
        x_grad = int(((wl_test - 400) / 300) * largeur_s)
        ax.plot([x_grad, x_grad], [1.0, 1.08], color="white", lw=1)
        if info["type"] not in ["raies"]:
            ax.text(
                x_grad,
                -0.25,
                f"{wl_test}",
                color="#90A4AE",
                fontsize=8,
                ha="center",
            )

    return fig


   
def reset_sous():
    """Remet à zéro la synthèse soustractive (Retour au Blanc)."""
    st.session_state.var_cyan = 0
    st.session_state.var_magenta = 0
    st.session_state.var_jaune = 0


def reset_rvb():
    """Remet à zéro la synthèse additive (Retour au Noir)."""
    st.session_state.var_rouge = 0
    st.session_state.var_vert = 0
    st.session_state.var_bleu = 0

def dessiner_synthese_couleurs():
    """Moteur de calcul physique : Mélange les couleurs CMJ et RVB

    d'après les curseurs présents dans le session_state.
    """
    # 1. Traitement de la Synthèse Soustractive (CMJ)
    # Formule physique : Le Cyan absorbe le Rouge, le Magenta absorbe le Vert, le Jaune absorbe le Bleu
    c = st.session_state.var_cyan
    m = st.session_state.var_magenta
    j = st.session_state.var_jaune

    r_sous = max(0, 255 - c)
    g_sous = max(0, 255 - m)
    b_sous = max(0, 255 - j)
    hex_sous = f"#{r_sous:02x}{g_sous:02x}{b_sous:02x}"
    st.session_state.var_txt_hex_sous = f"Simulation SOUS (RGB): {hex_sous.upper()}"

    # 2. Traitement de la Synthèse Additive (RVB)
    # Formule physique : Addition directe des intensités lumineuses reçues
    r_add = st.session_state.var_rouge
    g_add = st.session_state.var_vert
    b_add = st.session_state.var_bleu
    hex_rvb = f"#{r_add:02x}{g_add:02x}{b_add:02x}"
    st.session_state.var_txt_hex_rvb = f"Code Hex: {hex_rvb.upper()}"

    return hex_rvb, hex_sous


        
def mettre_a_jour_decomposition():
    """Moteur geometrique stable converti de Tkinter vers Matplotlib.
    Connecte en direct aux curseurs de la session de l'eleve.
    """
    angle_i_deg = st.session_state.get("slider_angle", 45.0)
    n_base = st.session_state.get("slider_indice", 1.51)

    # 1. DEFINITION DES DIMENSIONS EN PREMIER
    w, h = 680, 260
    y0 = (h - 60) / 2.0

    # 2. INITIALISATION DE SECURITE DU SPECTRE JUSTE APRES
    dev_rouge = dev_orange = dev_jaune = dev_vert = dev_bleu = dev_indigo = dev_violet = "R.T.I."

    fig, ax = plt.subplots(figsize=(8, 3.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()
    ax.axis("off")

    angle_i = math.radians(angle_i_deg)
    angle_prisme = math.radians(60.0)

    x_sommet = 120.0
    y_sommet = y0 - 50.0
    x_gauche = x_sommet - 45.0
    y_gauche = y0 + 50.0
    x_droite = x_sommet + 45.0
    y_droite = y0 + 50.0

    prisme = plt.Polygon(
        [[x_sommet, y_sommet], [x_gauche, y_gauche], [x_droite, y_droite]],
        facecolor="#e0f2fe", edgecolor="#38bdf8", linewidth=1.5, alpha=0.7
    )
    ax.add_patch(prisme)
    ax.text(x_sommet, y_sommet - 15, "Prisme", color="white", fontsize=8, fontweight="bold", ha="center")

    x_entree = x_gauche + 15.0
    y_entree = y0 + 12.0
    x_src = 15.0
    y_src = y_entree - (x_entree - x_src) * math.tan(angle_i - math.radians(30))

    ax.plot([x_src, x_entree], [y_src, y_entree], color="#ffffff", lw=2)
    ax.annotate("", xy=(x_entree, y_entree), xytext=(x_src, y_src), arrowprops=dict(arrowstyle="->", color="#ffffff", lw=1.5))

    def wl_to_rgb(wl):
        if 380 <= wl < 440: R, G, B = -(wl - 440) / (440 - 380), 0.0, 1.0
        elif 440 <= wl < 490: R, G, B = 0.0, (wl - 440) / (490 - 440), 1.0
        elif 490 <= wl < 510: R, G, B = 0.0, 1.0, -(wl - 510) / (510 - 490)
        elif 510 <= wl < 580: R, G, B = (wl - 510) / (580 - 510), 1.0, 0.0
        elif 580 <= wl < 645: R, G, B = 1.0, -(wl - 645) / (645 - 580), 0.0
        elif 645 <= wl <= 780: R, G, B = 1.0, 0.0, 0.0
        else: R, G, B = 0.0, 0.0, 0.0
        f = 1.0 if 420 <= wl <= 700 else (0.3 + 0.7 * (wl - 380) / (420 - 380) if wl < 420 else 0.3 + 0.7 * (780 - wl) / (780 - 700))
        return f"#{int(R*f*255):02x}{int(G*f*255):02x}{int(B*f*255):02x}"

    dev_rouge = dev_vert = dev_violet = 0.0
    y_impact_ecran_vert = -999.0
    x_ecran = w - 60.0

    bx_debut = 160.0
    bx_fin = w - 60.0
    by_haut = h - 55.0
    by_bas = h - 25.0
    largeur_bande = bx_fin - bx_debut

    # Balayage par pas de 1 nm pour construire le faisceau disperse
    for wl in range(400, 701, 1):
        dn = 0.02 * ((550 / wl) ** 2 - 0.5)
        n_reel = n_base + dn

        try:
            sin_r1 = math.sin(angle_i) / n_reel
            if abs(sin_r1) <= 1.0:
                r1 = math.asin(sin_r1)
                r2 = angle_prisme - r1
                sin_i2 = n_reel * math.sin(r2)

                if abs(sin_i2) <= 1.0:
                    i2 = math.asin(sin_i2)
                    D_deg = math.degrees(angle_i + i2 - angle_prisme)

                    # Sauvegarde des deviations calculees pour les 7 couleurs fondamentales
                    if wl == 700: dev_rouge = D_deg
                    if wl == 620: dev_orange = D_deg
                    if wl == 580: dev_jaune = D_deg
                    if wl == 530: dev_vert = D_deg
                    if wl == 475: dev_bleu = D_deg
                    if wl == 435: dev_indigo = D_deg
                    if wl == 400: dev_violet = D_deg

                    if wl == 550:
                        y_impact_ecran_vert = (
                            y0 + 10.0 + (dn * 10) + (w - 60.0 - (x_sommet + 15.0 + (dn * 40)))
                            * math.tan(angle_i + i2 - angle_prisme - math.radians(30))
                        )

                    x_sortie = x_sommet + 15.0 + (dn * 40)
                    y_sortie = y0 + 10.0 + (dn * 10)
                    y_ecran = y_sortie + (x_ecran - x_sortie) * math.tan(
                        angle_i + i2 - angle_prisme - math.radians(30)
                    )

                    # REPARATION ABSOLUE : Si le rayon lumineu descend trop bas, on le stoppe au ras de la bande
                    if y_ecran > by_haut:
                        x_ecran_limite = x_sortie + (by_haut - y_sortie) / math.tan(angle_i + i2 - angle_prisme - math.radians(30))
                        y_ecran_limite = by_haut
                    else:
                        x_ecran_limite = x_ecran
                        y_ecran_limite = y_ecran

                    color_hex = wl_to_rgb(wl)
                    ax.plot([x_entree, x_sortie], [y_entree, y_sortie], color=color_hex, lw=1.5)
                    ax.plot([x_sortie, x_ecran_limite], [y_sortie, y_ecran_limite], color=color_hex, lw=2)
        except:
            pass

    # Dessin de l'Ecran d'observation blanc
    x_ecran_pos = w - 60.0
    y_ecran_haut = y0 - 30
    y_ecran_bas = y0 + 110
    ecran_rect = plt.Rectangle((x_ecran_pos, y_ecran_haut), 12, y_ecran_bas - y_ecran_haut, facecolor="#ffffff", edgecolor="#94a3b8", lw=1.5)
    ax.add_patch(ecran_rect)
    ax.text(x_ecran_pos + 6, y0 + 40, "Ecran", color="black", fontsize=8, fontweight="bold", va="center", ha="center", rotation=-90)

    ax.text(bx_debut - 15, (by_haut + by_bas) / 2.0, "Spectre observe\nsur l'ecran :", color="white", fontsize=8, fontweight="bold", ha="right", va="center")

    # NETTOYAGE VISUEL DE LA ZONE DU SPECTRE POUR EVITER LES DOUBLONS
    ax.add_patch(plt.Rectangle((bx_debut, by_haut), largeur_bande, by_bas - by_haut, facecolor="#0f172a", edgecolor="none"))

    faisceau_touche_l_ecran = False
    if y_impact_ecran_vert != -999.0 and (y_ecran_haut <= y_impact_ecran_vert <= y_ecran_bas):
        faisceau_touche_l_ecran = True

    # Nettoyage preventif de la zone de dessin
    ax.add_patch(plt.Rectangle((bx_debut, by_haut), largeur_bande, by_bas - by_haut, facecolor="#0f172a", edgecolor="none"))

    if faisceau_touche_l_ecran:
        if largeur_bande > 50:
            for px in range(int(largeur_bande)):
                wl_courante = 400 + (px / largeur_bande) * (700 - 400)
                couleur_px = wl_to_rgb(wl_courante)
                ax.vlines(bx_debut + px, by_haut, by_bas, colors=couleur_px, linewidth=1.5)
            
            spectre_cadre = plt.Rectangle((bx_debut, by_haut), largeur_bande, by_bas - by_haut, fill=False, edgecolor="white", lw=1.5)
            ax.add_patch(spectre_cadre)
    else:
        # SI LE RAYON PASSE À CÔTÉ DE L'ÉCRAN : LA BANDE RESTE NOIRE
        spectre_vide = plt.Rectangle((bx_debut, by_haut), largeur_bande, by_bas - by_haut, facecolor="black", edgecolor="#334155", lw=1.5)
        ax.add_patch(spectre_vide)
        ax.text((bx_debut + bx_fin) / 2.0, (by_haut + by_bas) / 2.0, "[ Aucun faisceau sur l'ecran ]", color="#64748b", fontsize=8, style="italic", ha="center", va="center")
    if largeur_bande > 50:
        for wl_repere in range(400, 701, 50):
            ratio = (wl_repere - 400) / (700 - 400)
            x_repere = bx_debut + ratio * largeur_bande
            ax.plot([x_repere, x_repere], [by_bas, by_bas + 4], color="#475569", lw=1)
            ax.text(x_repere, by_bas + 14, str(wl_repere), color="#64748b", fontsize=7, ha="center", va="top")

    # CONFIGURATION DES CHAÎNES DE CARACTÈRES POUR L'ÉLÈVE
    d_r = f"{dev_rouge:.1f}°" if isinstance(dev_rouge, float) else "R.T.I."
    d_o = f"{dev_orange:.1f}°" if isinstance(dev_orange, float) else "R.T.I."
    d_j = f"{dev_jaune:.1f}°" if isinstance(dev_jaune, float) else "R.T.I."
    d_v = f"{dev_vert:.1f}°" if isinstance(dev_vert, float) else "R.T.I."
    d_b = f"{dev_bleu:.1f}°" if isinstance(dev_bleu, float) else "R.T.I."
    d_i = f"{dev_indigo:.1f}°" if isinstance(dev_indigo, float) else "R.T.I."
    d_vi = f"{dev_violet:.1f}°" if isinstance(dev_violet, float) else "R.T.I."

    st.session_state.var_texte_resultats_decomposition = (
        f"Analyse de dispersion :\n"
        f"• Incidence i = {angle_i_deg:.1f}° | Indice n = {n_base:.3f}\n"
        f"-----------------------------------------\n"
        f"• D_Rouge   = {d_r}  | • D_Bleu   = {d_b}\n"
        f"• D_Orange  = {d_o}  | • D_Indigo = {d_i}\n"
        f"• D_Jaune   = {d_j}  | • D_Violet = {d_vi}\n"
        f"• D_Vert    = {d_v}"
    )

    return fig

def recuperer_couleurs_newton():
    """Renvoie le catalogue des 7 couleurs fondamentales d'Isaac Newton."""
    return [
        {"nom": "Rouge", "code": "#ef4444"},
        {"nom": "Orange", "code": "#f97316"},
        {"nom": "Jaune", "code": "#eab308"},
        {"nom": "Vert", "code": "#22c55e"},
        {"nom": "Bleu", "code": "#2563eb"},
        {"nom": "Indigo", "code": "#4f46e5"},
        {"nom": "Violet", "code": "#7c3aed"},
    ]


def dessiner_disque_newton():
    """Animation Canvas HTML5 sans crochets pour éviter toute altération au copier-coller."""
    vitesse = float(st.session_state.get("var_vitesse_disque", 10.0))
    anim_en_cours = bool(st.session_state.get("anim_en_cours", False))
    vitesse_eff = vitesse if anim_en_cours else 0.0

    html_canvas = f"""
    <div style="background-color:#0f172a; border-radius:8px; padding:12px; border:1px solid #1e293b; text-align:center; font-family:Arial,sans-serif;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#38bdf8; font-weight:bold; font-size:13px;">DISQUE DE NEWTON</span>
            <span style="color:#eab308; font-weight:bold; font-size:13px;">Vitesse : {vitesse_eff:.1f} tr/s</span>
        </div>
        <canvas id="disqueCanvas" width="290" height="290"></canvas>
    </div>

    <script>
        (function() {{
            const canvas = document.getElementById("disqueCanvas");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const cx = 145;
            const cy = 145;
            const rayon = 125;

            const vitesse = {vitesse_eff};
            const rTab = new Array(239, 249, 234, 34, 37, 79, 124);
            const gTab = new Array(68, 115, 179, 197, 99, 70, 58);
            const bTab = new Array(68, 22, 8, 94, 235, 229, 237);

            const fusion = Math.min(1.0, vitesse / 25.0);
            let angle = 0;
            let tPrev = performance.now();

            function dessiner(tNow) {{
                const dt = (tNow - tPrev) / 1000.0;
                tPrev = tNow;

                const omega = Math.min(vitesse, 14.0) * 2.0 * Math.PI;
                angle = (angle + omega * dt) % (2.0 * Math.PI);

                ctx.clearRect(0, 0, 290, 290);

                ctx.beginPath();
                ctx.arc(cx, cy, rayon + 4, 0, 2 * Math.PI);
                ctx.fillStyle = "#1e293b";
                ctx.fill();

                const pas = (2.0 * Math.PI) / 7.0;
                const traines = vitesse > 0 ? 5 : 1;

                for (let k = 0; k < traines; k++) {{
                    const aOffset = angle - k * 0.09 * Math.min(vitesse / 4.0, 2.5);
                    ctx.globalAlpha = 1.0 / (k + 1);

                    for (let i = 0; i < 7; i++) {{
                        const a1 = aOffset + i * pas;
                        const a2 = a1 + pas + 0.02;
                        const r = Math.round(rTab.at(i) + (255 - rTab.at(i)) * fusion);
                        const g = Math.round(gTab.at(i) + (255 - gTab.at(i)) * fusion);
                        const b = Math.round(bTab.at(i) + (255 - bTab.at(i)) * fusion);

                        ctx.beginPath();
                        ctx.moveTo(cx, cy);
                        ctx.arc(cx, cy, rayon, a1, a2);
                        ctx.closePath();
                        ctx.fillStyle = "rgb(" + r + "," + g + "," + b + ")";
                        ctx.fill();
                    }}
                }}

                ctx.globalAlpha = 1.0;

                if (fusion < 0.85) {{
                    const mx = cx + (rayon - 14) * Math.cos(angle);
                    const my = cy + (rayon - 14) * Math.sin(angle);
                    ctx.beginPath();
                    ctx.arc(mx, my, 5, 0, 2 * Math.PI);
                    ctx.fillStyle = "#0f172a";
                    ctx.fill();
                }}

                ctx.beginPath();
                ctx.arc(cx, cy, 9, 0, 2 * Math.PI);
                ctx.fillStyle = "#334155";
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = "#ffffff";
                ctx.stroke();

                if (vitesse > 0) {{
                    requestAnimationFrame(dessiner);
                }}
            }}

            requestAnimationFrame(dessiner);
        }})();
    </script>
    """
    return html_canvas



def gerer_action_disque():
    """Gère l'état d'activation et le calcul d'angle statique du disque de Newton."""
    if "angle_rotation_disque" not in st.session_state:
        st.session_state.angle_rotation_disque = 0.0

    vitesse = st.session_state.var_vitesse_disque

    if st.session_state.anim_en_cours:
        st.session_state.angle_rotation_disque = (
            st.session_state.angle_rotation_disque + (vitesse * 2.5)
        ) % 360.0

# 1. Configuration de la page principale
st.set_page_config(
    page_title="TP Physique : optique",
    layout="wide",  # Permet d'occuper tout l'écran de manière fluide
)


for i in range(1, 10):
    key = f"mode_examen_tab{i}"
    if key not in st.session_state:
        st.session_state[key] = False

if "var_angle_incidence" not in st.session_state:
    st.session_state.var_angle_incidence = 30.0
if "var_rouge" not in st.session_state: st.session_state.var_rouge = 0
if "var_vert" not in st.session_state: st.session_state.var_vert = 0
if "var_bleu" not in st.session_state: st.session_state.var_bleu = 0
if "var_cyan" not in st.session_state: st.session_state.var_cyan = 0
if "var_magenta" not in st.session_state: st.session_state.var_magenta = 0
if "var_jaune" not in st.session_state: st.session_state.var_jaune = 0  

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
    st.header("Atelier 1 : L'histoire de la lumière et des couleurs")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Objectif de l'atelier :</p>
        <p style="margin-bottom: 0;">Retracer les grandes étapes scientifiques qui ont permis de comprendre la nature de la lumière, sa vitesse de propagation et l'origine des couleurs.</p>
    </div>
    """, unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        try: st.image("alhazen_optique.jpg", caption="Ibn al-Haytham (965 - 1040)", use_container_width=True)
        except Exception: st.warning("L'image 'alhazen_optique.jpg' est introuvable.")
        st.info("**Ibn al-Haytham (XIe siècle)**\n* Père de l'optique moderne (*Kitab al-Manazir*).\n* Démontre par la chambre noire (*camera obscura*) que la lumière voyage en ligne droite jusqu'à l'œil.")

    with col_h2:
        try: st.image("newton_prisme.jpg", caption="Isaac Newton et son prisme (1666)", use_container_width=True)
        except Exception: st.warning("L'image 'newton_prisme.jpg' est introuvable.")
        st.info("**Isaac Newton (1666)**\n* Décompose la lumière blanche du Soleil grâce à un prisme en verre.\n* Prouve que le blanc est un mélange de radiations colorées.")

    with col_h3:
        try: st.image("fraunhofer_spectre.jpg", caption="Joseph von Fraunhofer (1814)", use_container_width=True)
        except Exception: st.warning("L'image 'fraunhofer_spectre.jpg' est introuvable.")
        st.info("**Joseph von Fraunhofer (1814)**\n* Découvre plus de 570 raies noires d'absorption dans le spectre solaire.\n* Fonde ainsi la spectroscopie moderne.")

    with col_h4:
        try: st.image("maxwell_einstein.jpg", caption="Maxwell (1865) & Einstein (1905)", use_container_width=True)
        except Exception: st.warning("L'image 'maxwell_einstein.jpg' est introuvable.")
        st.info("**Onde et Photon (1865 - 1905)**\n* Maxwell montre que la lumière est une onde électromagnétique.\n* Einstein introduit les **photons**, grains d'énergie lumineuse.")

    st.markdown("---")
    if "hl_verrouille_tab1" not in st.session_state:
        st.session_state.hl_verrouille_tab1 = False
    verrou_hl = st.session_state.hl_verrouille_tab1
    afficher_atelier_hist_lumiere(verrouille=verrou_hl)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_hl = st.checkbox("Je certifie avoir complété l'Atelier 1 (Histoire de la lumière et des couleurs).", key="certif_hl1", disabled=verrou_hl)
    if st.button("VALIDER ET EXPORTER LE BILAN HISTORIQUE", key="btn_exp_hl1", use_container_width=True, disabled=verrou_hl):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_hl:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            sc_q = sum(1.0 for q in st.session_state.get("ordre_quiz_hl_aleatoire", []) if st.session_state.get(f"hl_at1_g_{q['id']}") == q["rep"])
            rep_t = {"hl_t1": "Alhazen", "hl_t2": "Newton", "hl_t3": "colorées", "hl_t4": "Rømer", "hl_t5": "kilomètres", "hl_t6": "Young", "hl_t7": "Fraunhofer", "hl_t8": "Maxwell", "hl_t9": "Einstein", "hl_t10": "additive"}
            sc_t = sum(1.0 for k, v in rep_t.items() if st.session_state.get(k) == v)
            st.session_state.score_hl1_p1 = sc_q
            st.session_state.score_hl1_p2 = sc_t
            st.session_state.score_final_hl1 = sc_q + sc_t
            st.session_state.hl_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("hl_verrouille_tab1", False):
        scr1 = st.session_state.score_hl1_p1
        scr2 = st.session_state.score_hl1_p2
        tot_s = st.session_state.score_final_hl1
        ts_hl = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note : {tot_s:.1f} / 20")

        html_hl = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Histoire de la Lumière - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background: #f8fafc; color: #1e293b; }}
                .header-box {{ background: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; border: 2px solid white; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; background: white; }}
                th {{ background: #0f172a; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 1 : L'Histoire de la Lumière et des Couleurs</p>
                <p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_hl}</p>
                <div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div>
            </div>
            <p style="background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong>
            </p>
            <table>
                <thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead>
                <tbody>
        """
        for num, q in enumerate(st.session_state.get("ordre_quiz_hl_aleatoire", []), 1):
            qid_c = q["id"]
            saisie_q = st.session_state.get(f"hl_at1_g_{qid_c}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_q) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_hl += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_q}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"

        html_hl += """
                </tbody>
            </table>
            <table>
                <thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead>
                <tbody>
        """
        verif_hl = [
            ("1. Au XIe siècle, ......... démontre que l'œil reçoit la lumière des objets.", "Alhazen", "hl_t1"),
            ("2. En 1666, Isaac ......... décompose la lumière blanche avec un prisme.", "Newton", "hl_t2"),
            ("3. La lumière blanche est composée d'une infinité de radiations .........", "colorées", "hl_t3"),
            ("4. En 1676, Ole ......... prouve que la lumière a une vitesse finie.", "Rømer", "hl_t4"),
            ("5. Dans le vide, la lumière se propage à environ 300 000 ......... par seconde.", "kilomètres", "hl_t5"),
            ("6. En 1801, Thomas ......... met en évidence les interférences lumineuses.", "Young", "hl_t6"),
            ("7. En 1814, Joseph von ......... observe les raies sombres du spectre solaire.", "Fraunhofer", "hl_t7"),
            ("8. James Clerk ......... démontre que la lumière est une onde électromagnétique.", "Maxwell", "hl_t8"),
            ("9. En 1905, Albert ......... explique que la lumière est transportée par des photons.", "Einstein", "hl_t9"),
            ("10. La rotation rapide du disque de Newton montre la synthèse .........", "additive", "hl_t10"),
        ]
        for idx_t, (en, rep, cle) in enumerate(verif_hl, 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_hl += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"

        html_hl += """
                </tbody>
            </table>
        </body>
        </html>
        """
        st.download_button(
            "Télécharger le rapport officiel de l'Atelier Historique (.html)",
            data=html_hl,
            file_name=preparer_nom_fichier("Rapport_Atelier_1_Histoire_Lumiere").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True
        )




with tab2:
    st.subheader("Décomposition de la lumière")

    # Déclaration du catalogue de questions pour éviter les erreurs de lecture
    base_questions = [
        {"q": "Quel physicien célèbre a démontré le premier la décomposition de la lumière blanche à l'aide d'un prisme ?", "options": ["Isaac Newton", "Albert Einstein", "René Descartes"], "rep": "Isaac Newton"},
        {"q": "Comment qualifie-t-on une lumière composée d'une seule radiation colorée (une seule longueur d'onde) ?", "options": ["Monochromatique", "Polychromatique", "Isotrope"], "rep": "Monochromatique"},
        {"q": "Quel phénomène physique explique la séparation des longueurs d'onde lors de la traversée du prisme ?", "options": ["La dispersion", "La diffraction", "La réflexion totale"], "rep": "La dispersion"},
        {"q": "Comment varie l'indice de réfraction 'n' du verre en fonction de la fréquence de la lumière incidente ?", "options": ["L'indice n augmente quand la fréquence augmente", "L'indice n diminue quand la fréquence augmente", "L'indice n reste constant"], "rep": "L'indice n augmente quand la fréquence augmente"},
        {"q": "Quelle radiation lumineuse visible subit la déviation la plus forte (l'angle de déviation le plus grand) ?", "options": ["Le Violet", "Le Rouge", "Le Vert"], "rep": "Le Violet"},
        {"q": "Quelle radiation lumineuse visible subit la déviation la moins forte à la sortie du bloc de verre ?", "options": ["Le Rouge", "Le Bleu", "Le Jaune"], "rep": "Le Rouge"},
        {"q": "Quelle est la grandeur physique qui s'exprime en nanomètres (nm) pour caractériser une couleur du spectre ?", "options": ["La longueur d'onde lambda", "L'indice de réfraction n", "La célérité c"], "rep": "La longueur d'onde lambda"},
        {"q": "Quelle experience interactive présente à l'écran permet de reconstituer la lumière blanche par persistance rétinienne ?", "options": ["Le disque de Newton tournant", "La synthèse soustractive", "L'analyse dispersive"], "rep": "Le disque de Newton tournant"},
        {"q": "Comment appelle-t-on la superposition de lumières colorées pour créer une nouvelle teinte (Rouge + Vert = Jaune) ?", "options": ["La synthèse additive", "La synthèse soustractive", "La dispersion prismatique"], "rep": "La synthèse additive"},
        {"q": "Si on mélange les trois filtres Cyan, Magenta et Jaune en synthèse soustractive pure, quelle couleur obtient-on ?", "options": ["Du Noir", "Du Blanc", "Du Vert"], "rep": "Du Noir"}
    ]

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        with st.container(border=True):
            st.markdown("**Décomposition de la lumière du soleil**")
            
            # 0. INITIALISATION SÉCURISÉE DES VARIABLES DE SESSION
            if "var_angle_incidence" not in st.session_state:
                st.session_state.var_angle_incidence = 45.0
            if "var_indice_n" not in st.session_state:
                st.session_state.var_indice_n = 1.50
            verrou_tab1 = st.session_state.get("mode_examen_tab1", False)

            # 1. ON ENREGISTRE D'ABORD LES CURSEURS
            st.session_state.var_angle_incidence = st.slider(
                "Angle d'incidence i (°):",
                min_value=10.0,
                max_value=80.0,
                value=float(st.session_state.get("var_angle_incidence", 45.0)),
                step=0.5,
                key="slider_angle",
                disabled=verrou_tab1
            )

            st.session_state.var_indice_n = st.slider(
                "Indice de base n :",
                min_value=1.30,
                max_value=1.80,
                value=float(st.session_state.get("var_indice_n", 1.50)),
                step=0.005,
                key="slider_indice",
                disabled=verrou_tab1
            )
            
            # 2. ON CORRIGE : ON FORCE LE CALCUL TECHNIQUE IMMÉDIATEMENT APRÈS LA LECTURE DES SLIDERS
            fig_decomposition = mettre_a_jour_decomposition()


            # 3. ON AFFICHE LE TEXTE CALCULÉ ET RAFRAÎCHI
            if st.session_state.var_texte_resultats_decomposition:
                st.code(st.session_state.var_texte_resultats_decomposition)
            else:
                st.info("Résultats de la décomposition")

        # --- CADRAN 2 : Recomposition ---
        # --- CADRAN 2 : Recomposition ---
        with st.container(border=True):
            st.markdown("**Recomposition de la lumière du soleil**")
            
            # Initialisation sécurisée des variables du disque de Newton
            if "anim_en_cours" not in st.session_state:
                st.session_state.anim_en_cours = False
            if "var_vitesse_disque" not in st.session_state:
                st.session_state.var_vitesse_disque = 10.0
            verrou_tab1 = st.session_state.get("mode_examen_tab1", False)

            label_bouton = "Arrêter le Disque" if st.session_state.get("anim_en_cours", False) else "Lancer le Disque"
            if st.button(label_bouton, key="btn_disque_action", disabled=verrou_tab1):
                st.session_state.anim_en_cours = not st.session_state.get("anim_en_cours", False)
                gerer_action_disque()
                st.rerun()

            st.session_state.var_vitesse_disque = st.slider(
                "Vitesse du disque (tr/s) :",
                min_value=1.0,
                max_value=40.0,
                value=float(st.session_state.get("var_vitesse_disque", 10.0)),
                step=1.0,
                key="slider_vitesse_disque",
                disabled=verrou_tab1
            )


    with col_droite:
        st.pyplot(fig_decomposition)
        st.markdown("---")
        html_disque = dessiner_disque_newton()
        components.html(html_disque, height=345)
    # =========================================================================
    # LABO DE SIMULATION : SYNTHÈSE ADDITIVE ET SOUSTRACTIVE
    # =========================================================================
    with st.container(border=True):
        st.markdown("**Synthese additive et soustractive**")

        col_add, col_sous = st.columns(2)
      
        # --- BLOC SYNTHÈSE ADDITIVE (CORRIGÉ POUR RECHARGEMENT EN DIRECT) ---
        with col_add:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; font-weight:bold;'>Synthese Additive</p>", unsafe_allow_html=True)
                
                # ÉTAPE 1 : PLACEMENT DES SLIDERS EN PREMIER POUR CAPTURER LA TOUCHE EN DIRECT
                r = st.slider("Rouge", 0, 255, value=st.session_state.get("var_rouge", 0), key="slide_rouge_tab1")
                v = st.slider("Vert", 0, 255, value=st.session_state.get("var_vert", 0), key="slide_vert_tab1")
                b = st.slider("Bleu", 0, 255, value=st.session_state.get("var_bleu", 0), key="slide_bleu_tab1")
                
                # Écriture immédiate en mémoire pour écraser le blocage sur le noir
                st.session_state.var_rouge = r
                st.session_state.var_vert = v
                st.session_state.var_bleu = b
                
                # ÉTAPE 2 : CALCUL DU CODE HEX ET RENDU IMMÉDIAT
                hex_rvb = f"#{r:02x}{v:02x}{b:02x}"
                st.markdown(
                    f'<div style="background-color: {hex_rvb}; height: 45px; border: 1px solid #cbd5e1; border-radius: 4px; margin-bottom: 10px;"></div>', 
                    unsafe_allow_html=True
                )
                
                st.caption(f"Code Hex: {hex_rvb.upper()}")
                
                if st.button("Reinitialiser RVB", key="btn_reset_rvb"):
                    st.session_state.var_rouge = 0
                    st.session_state.var_vert = 0
                    st.session_state.var_bleu = 0
                    st.rerun()

        # --- BLOC SYNTHÈSE SOUSTRACTIVE ---
        with col_sous:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; font-weight:bold;'>Synthese Soustractive</p>", unsafe_allow_html=True)
                
                c = st.slider("Cyan", 0, 255, value=st.session_state.get("var_cyan", 0), key="slide_cyan_tab1")
                m = st.slider("Magenta", 0, 255, value=st.session_state.get("var_magenta", 0), key="slide_magenta_tab1")
                j = st.slider("Jaune", 0, 255, value=st.session_state.get("var_jaune", 0), key="slide_jaune_tab1")
                
                st.session_state.var_cyan = c
                st.session_state.var_magenta = m
                st.session_state.var_jaune = j
                
                # Simulation soustractive convertie en RVB pour le rendu de l'écran
                r_s = max(0, min(255, int(255 - c)))
                v_s = max(0, min(255, int(255 - m)))
                b_s = max(0, min(255, int(255 - j)))
                hex_sous = f"#{r_s:02x}{v_s:02x}{b_s:02x}"
                
                st.markdown(
                    f'<div style="background-color: {hex_sous}; height: 45px; border: 1px solid #cbd5e1; border-radius: 4px; margin-bottom: 10px;"></div>', 
                    unsafe_allow_html=True
                )
                
                st.caption(f"Simulation RGB: {hex_sous.upper()}")
                
                if st.button("Reinitialiser CMJ", key="btn_reset_cmj"):
                    st.session_state.var_cyan = 0
                    st.session_state.var_magenta = 0
                    st.session_state.var_jaune = 0
                    st.rerun()

    st.write("---")
    dict_q1, dict_t1 = afficher_questions_optique1(verrouille=st.session_state.get("opt1_verrouille", False))

    # =========================================================================
    # VALIDATION DÉFINITIVE ET NOTATION DE L'ATELIER OPTIQUE 1 (Déjà présent au bas)
    # =========================================================================
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
            # Partie 1 : Quiz (10 Pts)
            attendus_qo1_v = {
                "q3": "Dispersion", "q4": "Angles", "q5": "Violet", 
                "q6": "Newton", "q7": "A = r1 + r2", "q8": "Blanche", 
                "q9": "Augmente", "q10": "Monochromatique"
            }
            score_quiz_opt1 = sum([1.25 for qk, qv in attendus_qo1_v.items() if st.session_state.get(f"col_g_quiz_opt1_{qk}_opt1") == qv])
            score_quiz_opt1 = min(10.0, round(score_quiz_opt1, 1))

            # Partie 2 : Texte a Trous (10 Pts : 10 items x 1 pt)
            attendus_to1_v = {
                "t1": "Dispersion", "t2": "Devie", "t3": "Violet", "t4": "Monochromatique", "t5": "Blanche",
                "t6": "Bleu", "t7": "Jaune", "t8": "Jaune", "t9": "Noir", "t10": "Nanometre"
            }
            score_trous_opt1 = round(sum([1.0 for tk, tv in attendus_to1_v.items() if st.session_state.get(f"opt1_{tk}") == tv]), 1)

            st.session_state.score_opt1_p1 = score_quiz_opt1
            st.session_state.score_opt1_p2 = score_trous_opt1
            st.session_state.score_final_opt1 = round(score_quiz_opt1 + score_trous_opt1, 1)
            st.session_state.opt1_verrouille = True
            st.rerun()

    # BLOC PERMANENT D'AFFICHAGE DU RAPPORT HTML APRÈS VERROUILLAGE
    if st.session_state.get("opt1_verrouille", False):
        scr1 = st.session_state.get("score_opt1_p1", 0)
        scr2 = st.session_state.get("score_opt1_p2", 0)
        tot_s = st.session_state.get("score_final_opt1", 0)

        from datetime import timedelta
        timestamp_opt1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 1 SCELLÉ ET VALIDÉ | Note : {tot_s} / 20")

        attendus_qo1_v = {
            "q3": "Dispersion", "q4": "Angles", "q5": "Violet", 
            "q6": "Newton", "q7": "A = r1 + r2", "q8": "Blanche", 
            "q9": "Augmente", "q10": "Monochromatique"
        }
        enonces_qo1_v = {
            "q3": "Le phénomène de séparation des couleurs par le prisme s'appelle la :",
            "q4": "La loi de Snell-Descartes relie les indices des milieux aux sinus des :",
            "q5": "Quelle couleur possède l'indice de réfraction le plus élevé dans le verre :",
            "q6": "La recomposition de la lumière blanche peut être observée grâce au disque de :",
            "q7": "La relation géométrique liée à l'angle au sommet A du prisme est :",
            "q8": "Lorsque la vitesse du disque de Newton est maximale, l'œil perçoit la couleur :",
            "q9": "Si l'indice de base du prisme augmente, la déviation globale de tous les rayons :",
            "q10": "Un rayonnement composé d'une seule radiation chromatique est qualifié de :"
        }

        attendus_to1_v = {
            "t1": "Dispersion", "t2": "Dévié", "t3": "Violet", "t4": "Monochromatique", "t5": "Blanche",
            "t6": "Bleu", "t7": "Jaune", "t8": "Jaune", "t9": "Noir", "t10": "Nanomètre"
        }
        enonces_to1_v = {
            "t1": "1. Le prisme permet de séparer les radiations de la lumière blanche par .........",
            "t2": "2. Chaque couleur possède son propre indice de réfraction. Le rouge est le moins .........",
            "t3": "3. À l'inverse, la radiation visible la plus déviée par le prisme est le .........",
            "t4": "4. Une lumière composée d'une seule radiation colorée est qualifiée de .........",
            "t5": "5. La rotation rapide du disque coloré montre la recomposition .........",
            "t6": "6. Les trois couleurs primaires de la synthèse additive sont Rouge, Vert et .........",
            "t7": "7. En synthèse additive, l'addition du Rouge et du Vert produit du .........",
            "t8": "8. En synthèse soustractive, les trois couleurs primaires sont Cyan, Magenta et .........",
            "t9": "9. La superposition des trois filtres Cyan, Magenta et Jaune donne du .........",
            "t10": "10. L'unité utilisée pour exprimer la longueur d'onde d'une couleur est le ........."
        }

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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 1</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire Numerique (Quiz items de cours) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE CONNAISSANCES OPTIQUES (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Question posee</th>
                        <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_t, (q_id, attendu) in enumerate(attendus_qo1_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt1_{q_id}_opt1", "Choisir...")
            enonce_q = enonces_qo1_v.get(q_id, "")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS (TEXTE A TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 55%; text-align: left;">Phrase a trous</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for t_key, t_val in attendus_to1_v.items():
            saisie = st.session_state.get(f"opt1_{t_key}", "Choisir...")
            phrase_t = enonces_to1_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS (TEXTE A TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 55%; text-align: left;">Phrase a trous</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for t_key, t_val in attendus_to1_v.items():
            saisie = st.session_state.get(f"opt1_{t_key}", "Choisir...")
            phrase_t = enonces_to1_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """
        
        nom_f = f"Rapport_Evaluation_Optique1_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_opt1,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.subheader("2. Les différentes lumières")

    # AJOUT INDISPENSABLE : Déclaration des deux colonnes pour l'Atelier 2
    col_gauche2, col_droite2 = st.columns(2)

    # Ligne 1897 : Maintenant col_gauche2 est parfaitement reconnue par Python
    with col_gauche2:
        with st.container(border=True):
            st.markdown("##### Manipulation A : Test de flamme")
            st.caption(
                "Analyse des spectres d'emission par excitation thermique de sels metalliques."
            )

            # Menu deroulant pour le choix du flacon de sel
            liste_metaux = list(st.session_state.catalogue_metaux.keys())
            
            # Initialisation securisee des variables de session
            if "var_sel_metal" not in st.session_state or st.session_state.var_sel_metal not in liste_metaux:
                st.session_state.var_sel_metal = liste_metaux[0]
            verrou_tab2 = st.session_state.get("mode_examen_tab2", False)

            st.session_state.var_sel_metal = st.selectbox(
                "Choisir un flacon de sel :",
                options=liste_metaux,
                index=liste_metaux.index(st.session_state.var_sel_metal),
                key="select_metal_tab2_final",
                disabled=verrou_tab2,
            )


            # Initialisation securisee des etats du bruleur Bunsen
            if "var_combustion_active" not in st.session_state:
                st.session_state.var_combustion_active = False
            if "var_versement_poudre" not in st.session_state:
                st.session_state.var_versement_poudre = False

            # Recuperation des donnees du metal et mise a jour de la description
            info_metal = gerer_changement_metal()
            st.info(f"**Analyse :** {info_metal['descr']}")

            # Bouton d'action pour declencher la combustion sequentielle
            label_bouton = (
                "Eteindre le bruleur"
                if st.session_state.get("var_combustion_active", False)
                else "Bruler l'echantillon (Test de flamme)"
            )
            if st.button(
                label_bouton,
                key="btn_flamme_tab2_final",
                use_container_width=True,
                disabled=st.session_state.get("mode_examen_tab2", False),
            ):
                declencher_test_flamme_web()
                st.rerun()

            # Rendu visuel de la simulation de la flamme du bec bunsen
            st.markdown("**Visualisation du brûleur Bec Bunsen :**")
            if st.session_state.get("var_versement_poudre", False):
                st.markdown(
                    '<div style="background-color: #475569; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 2px dashed #94a3b8;"><span style="color: #ffffff; font-weight: bold;">Versement de la poudre en cours...</span></div>',
                    unsafe_allow_html=True,
                )
            elif st.session_state.get("var_combustion_active", False):
                metal_courant = st.session_state.get("var_sel_metal", "Lithium (Li)")
                st.markdown(
                    f'<div style="background-color: {info_metal["couleur"]}; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 1px solid #ffffff;"><span style="color: #0d1117; font-weight: bold;">Combustion active : {metal_courant}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="background-color: #0d1117; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 1px solid #334155;"><span style="color: #64748b; font-style: italic;">[ Bruleur eteint - Cliquez sur Bruler ]</span></div>',
                    unsafe_allow_html=True,
                )


        # Affichage du profil du spectre de raies de la flamme en dessous
        st.markdown("---")
        fig_flamme = dessiner_spectre_flamme_combustion()
        st.pyplot(fig_flamme)

    # =====================================================================
    # COLONNE DROITE : MANIPULATION B - BANC DE SPECTROSCOPIE (Lampes)
    # =====================================================================
    with col_droite2:
        with st.container(border=True):
            st.markdown("##### Manipulation B : Banc de spectroscopie")

            # Menu deroulant pour le choix de l'ampoule / source lumineuse
            liste_lampes = list(st.session_state.lampes_data.keys())

            # Initialisation securisee des variables de session
            if "source_lumineuse_choisie" not in st.session_state or st.session_state.source_lumineuse_choisie not in liste_lampes:
                st.session_state.source_lumineuse_choisie = liste_lampes[0]
            verrou_tab2 = st.session_state.get("mode_examen_tab2", False)

            st.session_state.source_lumineuse_choisie = st.selectbox(
                "Source lumineuse :",
                options=liste_lampes,
                index=liste_lampes.index(
                    st.session_state.source_lumineuse_choisie
                ),
                key="select_lampe_tab2_final",
                disabled=verrou_tab2,
            )

            # Identification et coloration de la boite du type de spectre de l'ampoule
            nom_selectionne = st.session_state.source_lumineuse_choisie
            info_lampe = st.session_state.lampes_data[nom_selectionne]

            descr_spectre = info_lampe["descr"]
            if "CONTINU" in descr_spectre.upper():
                st.info(f"**Type de spectre :** {descr_spectre}")
            elif "RAIES" in descr_spectre.upper():
                st.warning(f"**Type de spectre :** {descr_spectre}")
            else:
                st.success(f"**Type de spectre :** {descr_spectre}")

            # Rendu visuel geometrique complet du banc d'optique
            fig_banc_optique = dessiner_montage_complet_atelier2()
            st.pyplot(fig_banc_optique)

            # Rendu du zoom lineaire nanometrique inverse de l'ecran
            st.markdown("---")
            fig_spectre_zoom = dessiner_zoom_spectre_atelier2()
            st.pyplot(fig_spectre_zoom)

        if "opt2_verrouille" not in st.session_state:
            st.session_state.opt2_verrouille = False
        if "opt2_afficher_correction" not in st.session_state:
            st.session_state.opt2_afficher_correction = False


    # Raccordement officiel a la fonction globale des questionnaires
    st.write("---")
    dict_q2, dict_t2 = afficher_questions_optique2(verrouille=st.session_state.get("opt2_verrouille", False))

    # =========================================================================
    # VALIDATION DÉFINITIVE ET CODE D'ASSEMBLAGE DU RAPPORT HTML ATELIER 2
    # =========================================================================
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
            # Partie 1 : Quiz (10 Pts)
            attendus_qo2_v = {
                "q1": "Spectre d'emission de raies", "q2": "Corps dense incandescent (Lampe a filament)", 
                "q3": "Jaune orange intense", "q4": "Vert pre / turquoise", 
                "q5": "Chaque element a des raies uniques", "q6": "Spectre d'absorption de raies", 
                "q7": "Spectroscope / Spectrometre", "q8": "Nanometre (nm)", 
                "q9": "Jaune", "q10": "D'absorption de raies (Fraunhofer)"
            }
            score_quiz_opt2 = sum([1 for qk, qv in attendus_qo2_v.items() if st.session_state.get(f"col_g_quiz_opt2_{qk}") == qv])

            # Partie 2 : Texte a trous (10 Pts)
            attendus_to2_v = {"t1": "Emission", "t2": "Jaune", "t3": "Continu", "t4": "Absorption", "t5": "Nanometres"}
            score_trous_opt2 = round(sum([1 for tk, tv in attendus_to2_v.items() if st.session_state.get(f"opt2_{tk}") == tv]) * 2, 1)

            st.session_state.score_opt2_p1 = score_quiz_opt2
            st.session_state.score_opt2_p2 = score_trous_opt2
            st.session_state.score_final_opt2 = round(score_quiz_opt2 + score_trous_opt2, 1)
            st.session_state.opt2_verrouille = True
            st.rerun()

    # BLOC DE DESSIN DU RAPPORT DE REUSSITE APRES VERROUILLAGE
    if st.session_state.get("opt2_verrouille", False):
        scr1 = st.session_state.get("score_opt2_p1", 0)
        scr2 = st.session_state.get("score_opt2_p2", 0)
        tot_s = st.session_state.get("score_final_opt2", 0)

        from datetime import timedelta
        timestamp_opt2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 2 SCELLÉ ET VALIDÉ | Note : {tot_s} / 20")

        attendus_qo2_v = {
            "q1": "Spectre d'émission de raies", "q2": "Corps dense incandescent (Lampe à filament)", 
            "q3": "Jaune orangé intense", "q4": "Vert pré / turquoise", 
            "q5": "Chaque élément a des raies uniques", "q6": "Spectre d'absorption de raies", 
            "q7": "Spectroscope / Spectromètre", "q8": "Nanomètre (nm)", 
            "q9": "Jaune", "q10": "D'absorption de raies (Fraunhofer)"
        }
        attendus_to2_v = {
            "t1": "Émission", "t2": "Jaune", "t3": "Continu", "t4": "Absorption", "t5": "Nanomètres",
            "t6": "Verte", "t7": "Identité", "t8": "Raies", "t9": "Fraunhofer", "t10": "Spectroscope"
        }
        enonces_to2_v = {
            "t1": "1. L'excitation thermique de sels métalliques par une flamme produit un spectre d'.........",
            "t2": "2. La combustion du Sodium se caractérise par une couleur intense dans le .........",
            "t3": "3. À l'inverse, un solide porté à haute température émet une lumière au spectre .........",
            "t4": "4. Le rayonnement solaire reçu sur Terre comporte de fines raies sombres d'.........",
            "t5": "5. La position précise de ces signatures se mesure sur l'écran en .........",
            "t6": "6. La combustion du chlorure de Cuivre donne à la flamme une teinte .........",
            "t7": "7. Chaque atome possède des raies spectrales qui constituent sa carte d'.........",
            "t8": "8. Une lampe à vapeur de Mercure ou de Sodium émet un spectre de .........",
            "t9": "9. Les raies noires du spectre solaire portent le nom de raies de .........",
            "t10": "10. L'appareil qui décompose la lumière pour analyser ses raies est un ........."
        }

        html_export_opt2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 2 - {n_eleve}</title>
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
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_opt2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Récapitulatif des scores de compétences - Optique 2</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire de Connaissances (Quiz 10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthèse de Cours (Texte à trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LES DIFFÉRENTES LUMIÈRES (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Question posée</th>
                        <th style="width: 20%; text-align: center;">Saisie Élève</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        ordre_reel_opt2 = st.session_state.get("ordre_questions_opt2", [])
        for idx_q, (q_id, q_txt) in enumerate(ordre_reel_opt2, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt2_{q_id}", "Choisir...")
            attendu = attendus_qo2_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt2 += f"<tr><td>{idx_q}</td><td>{q_txt}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt2 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHÈSE DE COURS (TEXTE À TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 55%; text-align: left;">Phrase à trous</th>
                        <th style="width: 15%; text-align: center;">Saisie Élève</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for t_key, attendu in attendus_to2_v.items():
            saisie = st.session_state.get(f"opt2_{t_key}", "Choisir...")
            phrase_t = enonces_to2_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt2 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel de spectroscopie généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """
        
        nom_f = f"Rapport_Evaluation_Optique2_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_opt2,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )


        ordre_reel_opt2 = st.session_state.get("ordre_questions_opt2", [])
        for idx_q, (q_id, q_txt) in enumerate(ordre_reel_opt2, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt2_{q_id}", "Choisir...")
            attendu = attendus_qo2_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt2 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt2 += """
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

        for idx_t, t_key in enumerate(["t1", "t2", "t3", "t4", "t5"], 1):
            saisie = st.session_state.get(f"opt2_{t_key}", "Choisir...")
            attendu = attendus_to2_v[t_key]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt2 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel de spectroscopie genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """
        
        nom_f = f"Rapport_Evaluation_Optique2_{n_eleve}_{p_eleve}_{c_eleve}"

        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_opt2,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )



with tab4:
    st.header("Atelier 4 : Applications dans le domaine de la Maintenance Industrielle")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">La lumière et les couleurs au service du contrôle qualité et de la maintenance prédictive :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">En maintenance industrielle, la maîtrise des spectres lumineux permet de <strong>détecter des défauts de surface</strong> par éclairage complémentaire, d'<strong>analyser l'oxydation des huiles</strong> par spectrophotométrie et de <strong>sécuriser le câblage électrique</strong> grâce à un Indice de Rendu des Couleurs (IRC) élevé.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_lum_maint = [
        {"titre": "Cas Maintenance N°1 : Vision industrielle et contrôle par éclairage coloré", "img": "lum_maint_vision.jpg", "leg": "Caméra de contrôle qualité sous éclairage LED monochromatique", "exp": "**Principe :** Éclairer un défaut rouge avec sa couleur complémentaire (**vert / cyan**) provoque une absorption totale : le défaut apparaît **noir** sur fond clair."},
        {"titre": "Cas Maintenance N°2 : Analyse spectrophotométrique des huiles hydrauliques", "img": "lum_maint_huile.jpg", "leg": "Contrôle d'absorbance et d'oxydation d'un échantillon d'huile", "exp": "**Principe :** Selon la loi de **Beer-Lambert**, l'absorbance lumineuse augmente avec la concentration des particules d'usure et de l'oxydation."},
        {"titre": "Cas Maintenance N°3 : Température de couleur et IRC sur poste de câblage", "img": "lum_maint_irc.jpg", "leg": "Comparaison du rendu des couleurs sous différentes lampes d'atelier", "exp": "**Principe :** Un éclairement blanc neutre (**4000 K – 5000 K**) avec un **IRC ≥ 80** est indispensable pour identifier sans erreur les conducteurs électriques."}
    ]

    if "sujet_lm_tire" not in st.session_state:
        st.session_state.sujet_lm_tire = None

    if st.button("TIRER AU SORT UN SUJET MAINTENANCE (LUMIÈRE & COULEURS)", key="btn_tirage_lm", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_lm_tire]
        st.session_state.sujet_lm_tire = random.choice(choix)
        st.session_state.mesures_lm_log = []
        st.rerun()

    if st.session_state.sujet_lm_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique de maintenance.")
    else:
        idx_lm = st.session_state.sujet_lm_tire
        data_lm = sujets_lum_maint[idx_lm]
        st.success(f"Sujet attribué : **{data_lm['titre']}**")
        st.markdown(data_lm["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_lm["img"], caption=data_lm["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_lm['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_lum_maint.jpg", caption="La pause BD : Câbler sous une lampe au sodium jaune, mauvaise idée !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_lum_maint.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_lm_log" not in st.session_state: st.session_state.mesures_lm_log = []
        if idx_lm == 0:
            st.radio("Choisissez la couleur du projecteur LED :", ["Lumière Blanche (RVB)", "Lumière Rouge (650 nm)", "Lumière Verte (530 nm)"], index=2, key="radio_lm_s0", horizontal=True)
        elif idx_lm == 1:
            st.slider("Taux de dégradation / oxydation de l'huile (%) :", 0.0, 100.0, 35.0, 5.0, key="slider_lm_s1")
        else:
            st.radio("Sélectionnez l'éclairage de l'atelier :", ["Lampe Sodium Basse Pression (IRC 22)", "LED Blanc Chaud (2700 K - IRC 82)", "LED Atelier Blanc Neutre (4500 K - IRC 92)"], index=2, key="radio_lm_s2", horizontal=True)

        if st.button("ENREGISTRER CE CONTRÔLE MAINTENANCE", key="btn_rel_lm", use_container_width=True):
            if "lm_mesure_courante" in st.session_state:
                st.session_state.mesures_lm_log.append(st.session_state.lm_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_lum_maint_matplotlib(idx_lm), use_container_width=True)
        if st.session_state.mesures_lm_log:
            df_lm = pd.DataFrame(st.session_state.mesures_lm_log, columns=["Paramètre", "Mesure 1", "Mesure 2", "Diagnostic"])
            st.dataframe(df_lm, use_container_width=True, hide_index=True)

    st.write("---")
    if "lm_verrouille_tab4" not in st.session_state: st.session_state.lm_verrouille_tab4 = False
    verrou_lm = st.session_state.lm_verrouille_tab4
    sujet_actif_lm = st.session_state.get("sujet_lm_tire", None)
    afficher_atelier_lum_maint(sujet_actif_lm, verrouille=verrou_lm)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_lm = st.checkbox("Je certifie avoir complété l'Atelier 4 (Maintenance - Lumière et Couleurs).", key="certif_lm4", disabled=verrou_lm)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_exp_lm4", use_container_width=True, disabled=verrou_lm):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_lm is None or not case_certif_lm:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_LUM_MAINT[sujet_actif_lm]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_lm_{sujet_actif_lm}", []) if st.session_state.get(f"lm_at4_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_lm}") == rep)
            st.session_state.score_lm4_p1, st.session_state.score_lm4_p2, st.session_state.score_final_lm4 = sc_q, sc_t, sc_q + sc_t
            st.session_state.lm_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("lm_verrouille_tab4", False) and sujet_actif_lm is not None:
        scr1, scr2, tot_s = st.session_state.score_lm4_p1, st.session_state.score_lm4_p2, st.session_state.score_final_lm4
        ts_lm = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 4 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LUM_MAINT[sujet_actif_lm]
        html_lm = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 4 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 4 : Maintenance (Lumière et Couleurs) - {sujets_lum_maint[sujet_actif_lm]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_lm}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_lm_{sujet_actif_lm}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"lm_at4_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_lm += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_lm += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_lm}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_lm += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_lm += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 4 (.html)", data=html_lm, file_name=preparer_nom_fichier("Rapport_Atelier_4_Maintenance_Lumiere").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab5:
    st.header("Atelier 5 : Applications dans le domaine des Travaux Publics")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">La lumière et les couleurs sur les chantiers de génie civil et de voirie :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans les Travaux Publics, les propriétés optiques des matériaux assurent la <strong>visibilité des équipements (fluorescence et rétroréflexion)</strong>, le <strong>repérage par code couleur des réseaux enterrés</strong> et la <strong>limitation des îlots de chaleur urbains grâce à l'albédo</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_lum_tp = [
        {"titre": "Chantier N°1 : Signalisation fluorescente et rétroréfléchissante de chantier", "img": "lum_tp_epi.jpg", "leg": "Gilet haute visibilité et panneaux temporaires Classe 3", "exp": "**Principe :** La **fluorescence** convertit les UV solaires en lumière visible au crépuscule, tandis que les **microbilles de verre** assurent la rétroréflexion la nuit."},
        {"titre": "Chantier N°2 : Éclairage LED de chantier et code couleur des réseaux enterrés", "img": "lum_tp_reseaux.jpg", "leg": "Grillages avertisseurs colorés en tranchée sous éclairage LED", "exp": "**Principe :** Un mât d'éclairage **IRC ≥ 80** permet de distinguer sans erreur les réseaux enterrés (**Rouge** = Élec, **Bleu** = Eau, **Jaune** = Gaz, **Vert** = Télécom)."},
        {"titre": "Chantier N°3 : Albédo des revêtements routiers et îlots de chaleur urbains", "img": "lum_tp_albedo.jpg", "leg": "Comparaison thermique entre enrobé noir et revêtement clair", "exp": "**Principe :** Un revêtement clair à **albédo élevé (0,40 à 0,55)** réfléchit l'énergie solaire et abaisse la température de surface de plus de **10 °C** en été."}
    ]

    if "sujet_ltp_tire" not in st.session_state:
        st.session_state.sujet_ltp_tire = None

    if st.button("TIRER AU SORT UN CHANTIER TP (LUMIÈRE & COULEURS)", key="btn_tirage_ltp", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_ltp_tire]
        st.session_state.sujet_ltp_tire = random.choice(choix)
        st.session_state.mesures_ltp_log = []
        st.rerun()

    if st.session_state.sujet_ltp_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un chantier de Travaux Publics.")
    else:
        idx_ltp = st.session_state.sujet_ltp_tire
        data_ltp = sujets_lum_tp[idx_ltp]
        st.success(f"Chantier attribué : **{data_ltp['titre']}**")
        st.markdown(data_ltp["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_ltp["img"], caption=data_ltp["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_ltp['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_lum_tp.jpg", caption="La pause BD : Rouge ou jaune ? Toujours vérifier le code couleur !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_lum_tp.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_ltp_log" not in st.session_state: st.session_state.mesures_ltp_log = []
        if idx_ltp == 0:
            st.radio("Condition d'observation :", ["Crépuscule (UV dominants)", "Nuit noire sous phares"], key="radio_ltp_s0", horizontal=True)
        elif idx_ltp == 1:
            st.radio("Éclairage nocturne de la tranchée :", ["Lampe Sodium Jaune (IRC 22)", "Mât LED Blanc Neutre (4500 K - IRC 90)"], index=1, key="radio_ltp_s1", horizontal=True)
        else:
            st.slider("Albédo du revêtement routier (0,05 = Enrobé noir | 0,55 = Enrobé clair) :", 0.05, 0.60, 0.35, 0.05, key="slider_ltp_s2")

        if st.button("ENREGISTRER CE RELEVÉ TP", key="btn_rel_ltp", use_container_width=True):
            if "ltp_mesure_courante" in st.session_state:
                st.session_state.mesures_ltp_log.append(st.session_state.ltp_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_lum_tp_matplotlib(idx_ltp), use_container_width=True)
        if st.session_state.mesures_ltp_log:
            df_ltp = pd.DataFrame(st.session_state.mesures_ltp_log, columns=["Paramètre", "Configuration", "Calcul", "Diagnostic"])
            st.dataframe(df_ltp, use_container_width=True, hide_index=True)

    st.write("---")
    if "ltp_verrouille_tab5" not in st.session_state: st.session_state.ltp_verrouille_tab5 = False
    verrou_ltp = st.session_state.ltp_verrouille_tab5
    sujet_actif_ltp = st.session_state.get("sujet_ltp_tire", None)
    afficher_atelier_lum_tp(sujet_actif_ltp, verrouille=verrou_ltp)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ltp = st.checkbox("Je certifie avoir complété l'Atelier 5 (Travaux Publics - Lumière et Couleurs).", key="certif_ltp5", disabled=verrou_ltp)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_exp_ltp5", use_container_width=True, disabled=verrou_ltp):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_ltp is None or not case_certif_ltp:
            st.error("Action refusée : Tirez au sort un chantier et cochez la case de certification.")
        else:
            bq = BANQUES_LUM_TP[sujet_actif_ltp]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_ltp_{sujet_actif_ltp}", []) if st.session_state.get(f"ltp_at5_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_ltp}") == rep)
            st.session_state.score_ltp5_p1, st.session_state.score_ltp5_p2, st.session_state.score_final_ltp5 = sc_q, sc_t, sc_q + sc_t
            st.session_state.ltp_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("ltp_verrouille_tab5", False) and sujet_actif_ltp is not None:
        scr1, scr2, tot_s = st.session_state.score_ltp5_p1, st.session_state.score_ltp5_p2, st.session_state.score_final_ltp5
        ts_ltp = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 5 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LUM_TP[sujet_actif_ltp]
        html_ltp = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 5 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 5 : Travaux Publics (Lumière et Couleurs) - {sujets_lum_tp[sujet_actif_ltp]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_ltp}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_ltp_{sujet_actif_ltp}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"ltp_at5_g_{qid_curr}", "Choisir...")
            saisie_curr = st.session_state.get(f"ltp_at5_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_ltp += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_ltp += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_ltp}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_ltp += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_ltp += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 5 (.html)", data=html_ltp, file_name=preparer_nom_fichier("Rapport_Atelier_5_TP_Lumiere").replace(".txt", ".html"), mime="text/html", use_container_width=True)



with tab6:
    st.header("Atelier 6 : Applications dans le domaine du Transport Routier")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">La lumière et les couleurs au service de la signalisation et de la sécurité routière :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans le transport routier, le filtrage optique (<strong>synthèse soustractive des feux</strong>), la <strong>température de couleur des projecteurs LED</strong> et la <strong>télédétection infrarouge LiDAR</strong> garantissent la sécurité de conduite de jour comme de nuit.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_lum_trans = [
        {"titre": "Cas Transport N°1 : Synthèse soustractive et couleurs réglementaires des feux", "img": "lum_trans_feux.jpg", "leg": "Feux arrière LED et catadioptres rétroréfléchissants", "exp": "**Principe :** Un cabochon rouge agit par **synthèse soustractive** en absorbant le vert et le bleu, tandis que les LED colorées émettent directement la radiation réglementaire."},
        {"titre": "Cas Transport N°2 : Température de couleur des phares et visibilité par brouillard", "img": "lum_trans_phares.jpg", "leg": "Projecteurs LED 5500 K et diffusion atmosphérique", "exp": "**Principe :** Une lumière blanche à **5500 K** maximise le contraste de nuit, mais son pic bleu est fortement **diffusé** par les gouttelettes d'eau dans le brouillard."},
        {"titre": "Cas Transport N°3 : Capteurs LiDAR infrarouge et reconnaissance des couleurs ADAS", "img": "lum_trans_lidar.jpg", "leg": "Faisceau laser infrarouge 905 nm et caméra de lecture des panneaux", "exp": "**Principe :** Le LiDAR mesure le **temps de vol** d'impulsions infrarouges invisibles, dont la portée dépend de l'**albédo** de l'obstacle."}
    ]

    if "sujet_ltr_tire" not in st.session_state:
        st.session_state.sujet_ltr_tire = None

    if st.button("TIRER AU SORT UN SUJET TRANSPORT (LUMIÈRE & COULEURS)", key="btn_tirage_ltr", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_ltr_tire]
        st.session_state.sujet_ltr_tire = random.choice(choix)
        st.session_state.mesures_ltr_log = []
        st.rerun()

    if st.session_state.sujet_ltr_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique du Transport Routier.")
    else:
        idx_ltr = st.session_state.sujet_ltr_tire
        data_ltr = sujets_lum_trans[idx_ltr]
        st.success(f"Étude attribuée : **{data_ltr['titre']}**")
        st.markdown(data_ltr["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_ltr["img"], caption=data_ltr["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_ltr['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_lum_trans.jpg", caption="La pause BD : Pleins phares dans le brouillard, un mur tout blanc !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_lum_trans.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_ltr_log" not in st.session_state: st.session_state.mesures_ltr_log = []
        if idx_ltr == 0:
            st.radio("Sélectionnez le filtre / cabochon du feu :", ["Cabochon Rouge (Feu Stop)", "Cabochon Ambre (Clignotant)", "Cabochon Transparent (Feu de recul)"], key="radio_ltr_s0", horizontal=True)
        elif idx_ltr == 1:
            c_t1, c_t2 = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_t1: st.slider("Température de couleur des projecteurs (K) :", 2800, 7500, 5500, 100, key="slider_ltr_s1")
            with c_t2: st.checkbox("Présence de brouillard dense", key="check_ltr_s1")
        else:
            st.radio("Choisissez la surface de l'obstacle devant le camion :", ["Carrosserie noire mate (Albédo 0,08)", "Carrosserie grise métallisée (Albédo 0,45)", "Plaque rétroréfléchissante blanche (Albédo 0,85)"], index=2, key="radio_ltr_s2", horizontal=True)

        if st.button("ENREGISTRER CE CONTRÔLE TRANSPORT", key="btn_rel_ltr", use_container_width=True):
            if "ltr_mesure_courante" in st.session_state:
                st.session_state.mesures_ltr_log.append(st.session_state.ltr_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_lum_trans_matplotlib(idx_ltr), use_container_width=True)
        if st.session_state.mesures_ltr_log:
            df_ltr = pd.DataFrame(st.session_state.mesures_ltr_log, columns=["Paramètre", "Condition", "Propriété optique", "Diagnostic"])
            st.dataframe(df_ltr, use_container_width=True, hide_index=True)

    st.write("---")
    if "ltr_verrouille_tab6" not in st.session_state: st.session_state.ltr_verrouille_tab6 = False
    verrou_ltr = st.session_state.ltr_verrouille_tab6
    sujet_actif_ltr = st.session_state.get("sujet_ltr_tire", None)
    afficher_atelier_lum_trans(sujet_actif_ltr, verrouille=verrou_ltr)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ltr = st.checkbox("Je certifie avoir complété l'Atelier 6 (Transport Routier - Lumière et Couleurs).", key="certif_ltr6", disabled=verrou_ltr)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_exp_ltr6", use_container_width=True, disabled=verrou_ltr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_ltr is None or not case_certif_ltr:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_LUM_TRANS[sujet_actif_ltr]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_ltr_{sujet_actif_ltr}", []) if st.session_state.get(f"ltr_at6_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_ltr}") == rep)
            st.session_state.score_ltr6_p1, st.session_state.score_ltr6_p2, st.session_state.score_final_ltr6 = sc_q, sc_t, sc_q + sc_t
            st.session_state.ltr_verrouille_tab6 = True
            st.rerun()

    if st.session_state.get("ltr_verrouille_tab6", False) and sujet_actif_ltr is not None:
        scr1, scr2, tot_s = st.session_state.score_ltr6_p1, st.session_state.score_ltr6_p2, st.session_state.score_final_ltr6
        ts_ltr = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 6 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LUM_TRANS[sujet_actif_ltr]
        html_ltr = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 6 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 6 : Transport Routier (Lumière et Couleurs) - {sujets_lum_trans[sujet_actif_ltr]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_ltr}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_ltr_{sujet_actif_ltr}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"ltr_at6_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_ltr += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_ltr += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_ltr}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_ltr += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_ltr += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 6 (.html)", data=html_ltr, file_name=preparer_nom_fichier("Rapport_Atelier_6_Transport_Lumiere").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab7:
    st.header("Atelier 7 : Applications dans le domaine du Géomètre Topographe")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">La lumière et les couleurs dans les levés topographiques et la télédétection :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Chez le géomètre topographe, la physique des rayonnements explique la <strong>haute visibilité des lasers verts (532 nm)</strong>, l'<strong>analyse multispectrale NDVI par drone</strong> et la <strong>mesure millimétrique de distance par réflexion sur prisme</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_lum_geo = [
        {"titre": "Mission N°1 : Visibilité des lasers de chantier Rouge (635 nm) vs Vert (532 nm)", "img": "lum_geo_laser.jpg", "leg": "Comparaison de visibilité entre laser rouge et laser vert sur chantier", "exp": "**Principe :** L'œil humain est **4 fois plus sensible** à la longueur d'onde verte (**532 nm**) qu'au rouge (**635 nm**) en vision diurne."},
        {"titre": "Mission N°2 : Télédétection multispectrale par drone et indice NDVI", "img": "lum_geo_ndvi.jpg", "leg": "Carte NDVI issue d'un levé drone multispectral (Rouge + Proche Infrarouge)", "exp": "**Principe :** La végétation saine absorbe le **Rouge** et réfléchit le **Proche Infrarouge (PIR)**, donnant un indice **NDVI = (PIR - R) / (PIR + R)** élevé."},
        {"titre": "Mission N°3 : Distancemètre laser sur prisme et nuage de points 3D colorisé", "img": "lum_geo_prisme.jpg", "leg": "Prisme topographique rétroréflecteur et scanner 3D", "exp": "**Principe :** Le prisme renvoie le faisceau infrarouge par **réflexion totale interne**, tandis que l'indice de l'air corrige la vitesse de la lumière (**PPM**)."}
    ]

    if "sujet_lgeo_tire" not in st.session_state:
        st.session_state.sujet_lgeo_tire = None

    if st.button("TIRER AU SORT UNE MISSION GÉOMÈTRE (LUMIÈRE & COULEURS)", key="btn_tirage_lgeo", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_lgeo_tire]
        st.session_state.sujet_lgeo_tire = random.choice(choix)
        st.session_state.mesures_lgeo_log = []
        st.rerun()

    if st.session_state.sujet_lgeo_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort une mission de Géomètre Topographe.")
    else:
        idx_lgeo = st.session_state.sujet_lgeo_tire
        data_lgeo = sujets_lum_geo[idx_lgeo]
        st.success(f"Mission attribuée : **{data_lgeo['titre']}**")
        st.markdown(data_lgeo["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_lgeo["img"], caption=data_lgeo["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_lgeo['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_lum_geo.jpg", caption="La pause BD : Avec le laser vert, même en plein soleil on voit le trait !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_lum_geo.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_lgeo_log" not in st.session_state: st.session_state.mesures_lgeo_log = []
        if idx_lgeo == 0:
            st.radio("Sélectionnez le type de niveau laser :", ["Laser Rouge Standard (635 nm)", "Laser Vert Chantier (532 nm)"], index=1, key="radio_lgeo_s0", horizontal=True)
        elif idx_lgeo == 1:
            st.radio("Zone survolée par le drone multispectral :", ["Végétation dense irriguée (Forêt / Culture)", "Sol nu / Parking en enrobé", "Plan d'eau / Rivière"], key="radio_lgeo_s1", horizontal=True)
        else:
            st.slider("Température de l'air sur le chantier (°C) [Référence = 15 °C] :", -5.0, 40.0, 15.0, 1.0, key="slider_lgeo_s2")

        if st.button("ENREGISTRER CE POINT TOPOGRAPHIQUE", key="btn_rel_lgeo", use_container_width=True):
            if "lgeo_mesure_courante" in st.session_state:
                st.session_state.mesures_lgeo_log.append(st.session_state.lgeo_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_lum_geo_matplotlib(idx_lgeo), use_container_width=True)
        if st.session_state.mesures_lgeo_log:
            df_lgeo = pd.DataFrame(st.session_state.mesures_lgeo_log, columns=["Paramètre", "Mesure 1", "Mesure 2", "Résultat"])
            st.dataframe(df_lgeo, use_container_width=True, hide_index=True)

    st.write("---")
    if "lgeo_verrouille_tab7" not in st.session_state: st.session_state.lgeo_verrouille_tab7 = False
    verrou_lgeo = st.session_state.lgeo_verrouille_tab7
    sujet_actif_lgeo = st.session_state.get("sujet_lgeo_tire", None)
    afficher_atelier_lum_geo(sujet_actif_lgeo, verrouille=verrou_lgeo)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_lgeo = st.checkbox("Je certifie avoir complété l'Atelier 7 (Géomètre Topographe - Lumière et Couleurs).", key="certif_lgeo7", disabled=verrou_lgeo)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_exp_lgeo7", use_container_width=True, disabled=verrou_lgeo):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_lgeo is None or not case_certif_lgeo:
            st.error("Action refusée : Tirez au sort une mission et cochez la case de certification.")
        else:
            bq = BANQUES_LUM_GEO[sujet_actif_lgeo]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_lgeo_{sujet_actif_lgeo}", []) if st.session_state.get(f"lgeo_at7_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_lgeo}") == rep)
            st.session_state.score_lgeo7_p1, st.session_state.score_lgeo7_p2, st.session_state.score_final_lgeo7 = sc_q, sc_t, sc_q + sc_t
            st.session_state.lgeo_verrouille_tab7 = True
            st.rerun()

    if st.session_state.get("lgeo_verrouille_tab7", False) and sujet_actif_lgeo is not None:
        scr1, scr2, tot_s = st.session_state.score_lgeo7_p1, st.session_state.score_lgeo7_p2, st.session_state.score_final_lgeo7
        ts_lgeo = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 7 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_LUM_GEO[sujet_actif_lgeo]
        html_lgeo = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 7 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 7 : Géomètre Topographe (Lumière et Couleurs) - {sujets_lum_geo[sujet_actif_lgeo]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_lgeo}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_lgeo_{sujet_actif_lgeo}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"lgeo_at7_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_lgeo += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_lgeo += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_lgeo}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_lgeo += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_lgeo += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 7 (.html)", data=html_lgeo, file_name=preparer_nom_fichier("Rapport_Atelier_7_Geometre_Lumiere").replace(".txt", ".html"), mime="text/html", use_container_width=True)





















