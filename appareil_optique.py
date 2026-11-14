# -*- coding: utf-8 -*-

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Application appareils optique ",
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

st.title("Application appareils optique")
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

BANQUES_APP_GEO = {
    0: {
        "questions": [
            {"id": "qag0_1", "q": "Quel appareil optique et électronique de référence utilise le géomètre topographe pour mesurer simultanément les angles horizontaux, les angles verticaux et les distances ?", "options": ["Une station totale (tachéomètre électronique)", "Une loupe binoculaire", "Un microscope métallographique"], "rep": "Une station totale (tachéomètre électronique)"},
            {"id": "qag0_2", "q": "Quel est le grossissement nominal standard de la lunette astronomique intégrée à une station totale de précision ?", "options": ["30× (permettant de viser un prisme à plus de 1 km)", "2×", "500×"], "rep": "30× (permettant de viser un prisme à plus de 1 km)"},
            {"id": "qag0_3", "q": "Comment s'appelle le dispositif optique placé à l'intérieur de la lunette permettant d'effectuer la mise au point sans modifier la longueur extérieure du tube ?", "options": ["Une lentille divergente interne mobile de focalisation", "Un miroir concave externe", "Un filtre polarisant"], "rep": "Une lentille divergente interne mobile de focalisation"},
            {"id": "qag0_4", "q": "Pourquoi l'image observée dans la lunette d'une station totale moderne est-elle droite (à l'endroit) ?", "options": ["Grâce à un prisme redresseur de Porro ou en toit intégré dans le chemin optique", "Parce que l'oculaire est divergent", "Parce que le trépied est inversé"], "rep": "Grâce à un prisme redresseur de Porro ou en toit intégré dans le chemin optique"},
            {"id": "qag0_5", "q": "Comment appelle-t-on le croisillon très fin gravé sur une lame de verre interne permettant au géomètre de centrer exactement la cible ?", "options": ["Le réticule (dont l'éclairage est réglable pour les visées de nuit ou en tunnel)", "Le diaphragme iris", "La pupille de sortie"], "rep": "Le réticule (dont l'éclairage est réglable pour les visées de nuit ou en tunnel)"},
            {"id": "qag0_6", "q": "Quel petit système optique vertical situé sur l'embase de la station totale permet de centrer l'instrument exactement au-dessus du clou d'arpentage au sol ?", "options": ["Le plomb optique (ou plomb laser)", "Le régloscope", "L'endoscope"], "rep": "Le plomb optique (ou plomb laser)"},
            {"id": "qag0_7", "q": "Quelle est la première opération de réglage optique que doit faire le géomètre avant de viser la cible ?", "options": ["Régler la netteté des fils du réticule grâce à la bague dioptrique de l'oculaire", "Changer l'objectif", "Démonter le trépied"], "rep": "Régler la netteté des fils du réticule grâce à la bague dioptrique de l'oculaire"},
            {"id": "qag0_8", "q": "Comment appelle-t-on le défaut optique qui se produit lorsque l'image de la cible ne se forme pas exactement dans le plan du réticule (le croisillon bouge sur la cible si on déplace l'œil) ?", "options": ["L'erreur de parallaxe", "La dispersion chromatique", "La fluorescence"], "rep": "L'erreur de parallaxe"},
            {"id": "qag0_9", "q": "Sur quel principe optique fonctionne la lunette d'un théodolite ou d'une station totale lors d'une visée à l'infini ?", "options": ["Un système afocal (objectif convergent + prisme redresseur + oculaire convergent)", "Un miroir plan incliné", "Une lentille divergente seule"], "rep": "Un système afocal (objectif convergent + prisme redresseur + oculaire convergent)"},
            {"id": "qag0_10", "q": "Quel composant motorisé équipe les stations totales robotisées modernes pour suivre automatiquement le prisme porté par l'opérateur ?", "options": ["Une caméra de reconnaissance optique (ATR - Automatic Target Recognition) captant le reflet infrarouge du prisme", "Un microphone directionnel", "Une boussole magnétique"], "rep": "Une caméra de reconnaissance optique (ATR - Automatic Target Recognition) captant le reflet infrarouge du prisme"},
        ],
        "trous": [
            ("1. La lunette d'une station totale possède un grossissement standard de .........×.", ["Choisir...", "30", "3"], "30", "ag_t1"),
            ("2. Un ......... redresseur interne permet d'observer le terrain à l'endroit.", ["Choisir...", "prisme", "filtre"], "prisme", "ag_t2"),
            ("3. La mise au point se fait par déplacement d'une lentille interne de .........", ["Choisir...", "focalisation", "dispersion"], "focalisation", "ag_t3"),
            ("4. La croix de visée gravée dans l'oculaire s'appelle le .........", ["Choisir...", "réticule", "verre dépoli"], "réticule", "ag_t4"),
            ("5. Le centrage vertical au-dessus du repère au sol utilise le ......... optique.", ["Choisir...", "plomb", "niveau"], "plomb", "ag_t5"),
            ("6. La bague ......... de l'oculaire permet de voir les fils du réticule parfaitement nets.", ["Choisir...", "dioptrique", "magnétique"], "dioptrique", "ag_t6"),
            ("7. Si le réticule semble bouger sur la cible quand l'œil se déplace, il y a une erreur de .........", ["Choisir...", "parallaxe", "réfraction"], "parallaxe", "ag_t7"),
            ("8. Pour une visée lointaine sans fatigue, la lunette fonctionne en système .........", ["Choisir...", "afocal", "divergent"], "afocal", "ag_t8"),
            ("9. Le suivi automatique du prisme (ATR) utilise un faisceau ......... réfléchi.", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "ag_t9"),
            ("10. Le tachéomètre électronique mesure à la fois les ......... et les distances.", ["Choisir...", "angles", "masses"], "angles", "ag_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qag1_1", "q": "Quelle technique topographique permet de reconstituer un terrain ou un bâtiment en 3D à partir de photographies aériennes prises par drone ou avion ?", "options": ["La photogrammétrie numérique", "La thermographie infrarouge", "L'endoscopie industrielle"], "rep": "La photogrammétrie numérique"},
            {"id": "qag1_2", "q": "Pourquoi les caméras embarquées sur les drones topographiques sont-elles équipées d'un obturateur mécanique global (« Global Shutter ») plutôt que déroulant ?", "options": ["Pour figer instantanément toute l'image sans déformation géométrique liée à la vitesse de vol du drone", "Pour prendre des photos en noir et blanc", "Pour consommer plus de batterie"], "rep": "Pour figer instantanément toute l'image sans déformation géométrique liée à la vitesse de vol du drone"},
            {"id": "qag1_3", "q": "Comment appelle-t-on la taille réelle au sol (en cm/pixel) représentée par un pixel du capteur CMOS lors d'un levé photogrammétrique par drone ?", "options": ["La résolution spatiale au sol ou GSD (Ground Sampling Distance)", "L'indice NDVI", "La pupille de sortie"], "rep": "La résolution spatiale au sol ou GSD (Ground Sampling Distance)"},
            {"id": "qag1_4", "q": "Quelle relation géométrique (théorème de Thalès) relie la hauteur de vol H, la distance focale f', la taille d'un pixel p et la résolution au sol GSD ?", "options": ["GSD = (H × p) / f'", "GSD = (f' × p) / H", "GSD = H + f'"], "rep": "GSD = (H × p) / f'"},
            {"id": "qag1_5", "q": "Si un drone vole à H = 100 m d'altitude avec un objectif de focale f' = 20 mm et un capteur dont les pixels mesurent p = 4 µm, quel est le GSD au sol ?", "options": ["2,0 cm/pixel", "20 cm/pixel", "0,2 mm/pixel"], "rep": "2,0 cm/pixel"},
            {"id": "qag1_6", "q": "Quel taux de recouvrement (superposition) entre deux photographies successives le géomètre programme-t-il lors d'un plan de vol photogrammétrique ?", "options": ["75 % à 80 % de recouvrement longitudinal pour voir chaque point sous plusieurs angles (stéréoscopie)", "5 % seulement", "0 % (aucun recouvrement)"], "rep": "75 % à 80 % de recouvrement longitudinal pour voir chaque point sous plusieurs angles (stéréoscopie)"},
            {"id": "qag1_7", "q": "Pourquoi un objectif photogrammétrique métrique doit-il être calibré en laboratoire avant le levé ?", "options": ["Pour connaître exactement sa distance focale principale et corriger la distorsion radiale des lentilles", "Pour nettoyer la batterie", "Pour changer la couleur du boîtier"], "rep": "Pour connaître exactement sa distance focale principale et corriger la distorsion radiale des lentilles"},
            {"id": "qag1_8", "q": "Quelle est la nature de l'image projetée par l'objectif du drone sur son capteur CMOS ?", "options": ["Réelle, renversée et fortement réduite", "Virtuelle et droite", "Agrandie 10 fois"], "rep": "Réelle, renversée et fortement réduite"},
            {"id": "qag1_9", "q": "Comment appelle-t-on les cibles au sol (damiers noir et blanc) mesurées au GPS RTK par le géomètre pour caler précisément le modèle 3D photogrammétrique ?", "options": ["Des points de calage au sol (GCP - Ground Control Points)", "Des fils stadimétriques", "Des prismes de Porro"], "rep": "Des points de calage au sol (GCP - Ground Control Points)"},
            {"id": "qag1_10", "q": "Si le géomètre double l'altitude de vol H du drone (de 50 m à 100 m) avec le même appareil photo, comment évolue la taille du pixel au sol (GSD) ?", "options": ["Le GSD est multiplié par 2 (la précision diminue d'un facteur 2)", "Le GSD est divisé par 4", "Le GSD reste identique"], "rep": "Le GSD est multiplié par 2 (la précision diminue d'un facteur 2)"},
        ],
        "trous": [
            ("1. La reconstitution 3D à partir de photos aériennes s'appelle la .........", ["Choisir...", "photogrammétrie", "thermographie"], "photogrammétrie", "ag_t1"),
            ("2. La taille réelle d'un pixel au sol se note ......... (Ground Sampling Distance).", ["Choisir...", "GSD", "NDVI"], "GSD", "ag_t2"),
            ("3. Par proportionnalité optique, on a la relation GSD = (H × p) / .........", ["Choisir...", "f'", "c"], "f'", "ag_t3"),
            ("4. Un drone topographique utilise un obturateur ......... pour éviter toute déformation.", ["Choisir...", "global", "manuel"], "global", "ag_t4"),
            ("5. Le recouvrement entre deux clichés successifs est d'environ ......... %.", ["Choisir...", "80", "10"], "80", "ag_t5"),
            ("6. L'objectif doit être ......... pour corriger la distorsion optique des lentilles.", ["Choisir...", "calibré", "teinté"], "calibré", "ag_t6"),
            ("7. Les cibles au sol mesurées au GPS pour géoréférencer le modèle sont des .........", ["Choisir...", "GCP", "LED"], "GCP", "ag_t7"),
            ("8. Si l'altitude de vol H augmente, la valeur du GSD .........", ["Choisir...", "augmente", "diminue"], "augmente", "ag_t8"),
            ("9. Sur le capteur CMOS du drone, l'image du terrain est réelle et .........", ["Choisir...", "renversée", "droite"], "renversée", "ag_t9"),
            ("10. Le calcul des altitudes (Z) par drone repose sur la vision ......... multi-angles.", ["Choisir...", "stéréoscopique", "monochromatique"], "stéréoscopique", "ag_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qag2_1", "q": "Quel appareil optique et laser de haute technologie permet au géomètre de numériser intégralement un bâtiment, un tunnel ou un monument en quelques minutes ?", "options": ["Un scanner laser 3D terrestre (LiDAR statique ou mobile)", "Une loupe simple", "Un niveau à bulle"], "rep": "Un scanner laser 3D terrestre (LiDAR statique ou mobile)"},
            {"id": "qag2_2", "q": "Quel élément optique tournant à très haute vitesse (jusqu'à 100 tours/seconde) dévie verticalement le faisceau laser dans un scanner 3D ?", "options": ["Un miroir polygonal (ou miroir oscillant) à réflexion totale", "Une lentille divergente", "Un filtre rouge"], "rep": "Un miroir polygonal (ou miroir oscillant) à réflexion totale"},
            {"id": "qag2_3", "q": "Combien de points par seconde un scanner laser 3D topographique moderne peut-il mesurer ?", "options": ["Jusqu'à 1 000 000 à 2 000 000 de points par seconde", "10 points par minute", "50 points par heure"], "rep": "Jusqu'à 1 000 000 à 2 000 000 de points par seconde"},
            {"id": "qag2_4", "q": "Quel système optique reçoit le faible signal laser renvoyé par les façades jusqu'à 100 ou 300 mètres de distance ?", "options": ["Une lentille collectrice de grand diamètre focalisant le faisceau retour sur une photodiode avalanche (APD)", "Un oculaire de microscope", "Un prisme dispersif"], "rep": "Une lentille collectrice de grand diamètre focalisant le faisceau retour sur une photodiode avalanche (APD)"},
            {"id": "qag2_5", "q": "Pourquoi l'axe optique d'émission du laser et l'axe optique de réception du scanner 3D sont-ils coaxiaux (alignés sur le même miroir) ?", "options": ["Pour garantir que le faisceau réfléchi revienne toujours exactement au centre du capteur quelle que soit la distance", "Pour économiser du verre", "Pour rendre le laser visible"], "rep": "Pour garantir que le faisceau réfléchi revienne toujours exactement au centre du capteur quelle que soit la distance"},
            {"id": "qag2_6", "q": "Comment s'appelle l'angle d'ouverture d'un faisceau laser qui s'élargit légèrement avec la distance (environ 0,2 à 0,3 mrad) ?", "options": ["La divergence du faisceau laser", "La convergence oculaire", "La réfraction totale"], "rep": "La divergence du faisceau laser"},
            {"id": "qag2_7", "q": "Quel impact a une forte divergence du faisceau laser à 100 mètres de distance sur la précision topographique ?", "options": ["La tache laser (spot) devient plus large sur la façade, réduisant la finesse de détection des arêtes", "Le laser change de couleur", "La distance devient nulle"], "rep": "La tache laser (spot) devient plus large sur la façade, réduisant la finesse de détection des arêtes"},
            {"id": "qag2_8", "q": "Quel accessoire sphérique blanc mat placé sur trépieds dans la scène sert de repère optique pour assembler plusieurs stations de scan 3D ?", "options": ["Des sphères de calibrage / référence (dont le scanner calcule automatiquement le centre géométrique)", "Des miroirs plans", "Des prismes de Newton"], "rep": "Des sphères de calibrage / référence (dont le scanner calcule automatiquement le centre géométrique)"},
            {"id": "qag2_9", "q": "Quelle difficulté optique rencontre un scanner laser 3D face à une grande baie vitrée transparente ou un miroir ?", "options": ["Le faisceau traverse la vitre ou rebondit vers un autre mur, créant des points fantômes erronés", "La vitre fait exploser le capteur", "Le scanner s'arrête automatiquement"], "rep": "Le faisceau traverse la vitre ou rebondit vers un autre mur, créant des points fantômes erronés"},
            {"id": "qag2_10", "q": "Quel logiciel exploite le nuage de points 3D issu du scanner laser pour produire la maquette numérique du bâtiment ?", "options": ["Un logiciel de modélisation BIM / CAO 3D", "Un tableur simple uniquement", "Un traitement de texte"], "rep": "Un logiciel de modélisation BIM / CAO 3D"},
        ],
        "trous": [
            ("1. Le scanner laser 3D dévie le faisceau grâce à un ......... tournant à haute vitesse.", ["Choisir...", "miroir", "prisme dispersif"], "miroir", "ag_t1"),
            ("2. L'optique de réception focalise le signal retour sur une ......... très sensible.", ["Choisir...", "photodiode", "pellicule"], "photodiode", "ag_t2"),
            ("3. Les faisceaux d'émission et de réception sont ......... (alignés sur le même axe).", ["Choisir...", "coaxiaux", "perpendiculaires"], "coaxiaux", "ag_t3"),
            ("4. L'élargissement progressif du faisceau laser avec la distance s'appelle la .........", ["Choisir...", "divergence", "convergence"], "divergence", "ag_t4"),
            ("5. Des ......... blanches mates servent de cibles de référence pour assembler les scans.", ["Choisir...", "sphères", "lentilles"], "sphères", "ag_t5"),
            ("6. Les surfaces vitrées créent des points ......... par réflexion spéculaire.", ["Choisir...", "fantômes", "fixes"], "fantômes", "ag_t6"),
            ("7. Un scanner moderne acquiert jusqu'à un ......... de points par seconde.", ["Choisir...", "million", "millier"], "million", "ag_t7"),
            ("8. Le nuage de points sert de base à la maquette numérique ......... du bâtiment.", ["Choisir...", "BIM", "PDF"], "BIM", "ag_t8"),
            ("9. Le miroir du scanner fonctionne par ......... optique sans déformation.", ["Choisir...", "réflexion", "réfraction"], "réflexion", "ag_t9"),
            ("10. Le diamètre du faisceau laser sur la cible s'appelle la taille du .........", ["Choisir...", "spot", "réticule"], "spot", "ag_t10"),
        ]
    }
}


def mettre_a_jour_app_geo_matplotlib(sujet_idx):
    """Banc d'essai Appareils Optiques adapté au Géomètre Topographe."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        parallaxe = st.session_state.get("check_ag_s0", False)
        ax.add_patch(patches.Rectangle((55, 95), 110, 60, facecolor="#eab308", edgecolor="white", lw=1.5))
        ax.text(110, 125, "Lunette 30×\nStation Totale", color="#0f172a", fontsize=8.5, fontweight="bold", ha="center", va="center")


        # Cercle de visée agrandi à droite
        ax.add_patch(patches.Circle((410, 125), 72, facecolor="#1e293b", edgecolor="#38bdf8", lw=2.5))
        ax.plot([345, 475], [125, 125], color="#ef4444", lw=1.5)
        ax.plot([410, 410], [60, 190], color="#ef4444", lw=1.5)


        decal = 18 if parallaxe else 0
        ax.add_patch(patches.Polygon([[410 + decal, 125], [398 + decal, 102], [422 + decal, 102]], facecolor="#22c55e", edgecolor="white"))
        ax.text(410 + decal, 92, "Cible", color="#22c55e", fontsize=8, fontweight="bold", ha="center")

        if parallaxe:
            msg_st = "ERREUR DE PARALLAXE : L'image de la cible n'est pas dans le plan du réticule (décalage visuel) !"
            c_st = "#ef4444"
        else:
            msg_st = "VISÉE PARFAITE (Parallaxe nulle) : Image de la cible exactement superposée au réticule !"
            c_st = "#22c55e"

        ax.text(25, 18, "LUNETTE DE STATION TOTALE (30×) : RÉGLAGE DU RÉTICULE ET PARALLAXE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg_st, color=c_st, fontsize=8, fontweight="bold")
        st.session_state.ag_mesure_courante = ("Grossissement 30×", "Prisme redresseur", "Parallaxe active" if parallaxe else "Parallaxe nulle", "ERREUR VISÉE" if parallaxe else "POINTÉ PRÉCIS")

    elif sujet_idx == 1:
        h_vol = st.session_state.get("slider_ag_s1", 80.0)
        foc_mm = st.session_state.get("radio_ag_s1", 20.0)
        pixel_um = 4.0
        gsd_cm = round((h_vol * pixel_um * 100.0) / (foc_mm * 1000.0), 2)

        ax.add_patch(patches.Rectangle((230, 42), 140, 36, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(300, 60, f"Drone H = {h_vol:.0f} m\nf' = {foc_mm:.0f} mm", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        demi_larg = min(230.0, (h_vol / foc_mm) * 35.0)
        ax.fill([300, 300 - demi_larg, 300 + demi_larg], [78, 192, 192], color="#38bdf8", alpha=0.22)
        ax.plot([300 - demi_larg, 300 + demi_larg], [192, 192], color="#22c55e", lw=4)

        ax.text(300, 215, f"Emprise au sol  |  Résolution GSD = {gsd_cm:.2f} cm/pixel", color="#fde047", fontsize=8.5, fontweight="bold", ha="center")

        ax.text(25, 18, "PHOTOGRAMMÉTRIE DRONE : CALCUL DE LA RÉSOLUTION AU SOL GSD = (H × p) / f'", color="#38bdf8", fontsize=9, fontweight="bold")
        st.session_state.ag_mesure_courante = (f"H = {h_vol:.0f} m", f"f' = {foc_mm:.0f} mm", f"GSD = {gsd_cm:.2f} cm/px", "HAUTE PRÉCISION" if gsd_cm <= 2.5 else "LEVÉ STANDARD")

    else:
        dist_scan = st.session_state.get("slider_ag_s2", 50.0)
        spot_mm = round(3.0 + dist_scan * 0.25, 1)

        ax.add_patch(patches.Rectangle((55, 95), 95, 60, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(102, 125, "Scanner 3D\nMiroir rotatif", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        x_mur = 190.0 + (dist_scan / 150.0) * 310.0
        ax.fill([150, x_mur, x_mur], [125, 125 - spot_mm * 0.6, 125 + spot_mm * 0.6], color="#22c55e", alpha=0.35)
        ax.plot([x_mur, x_mur], [65, 185], color="#cbd5e1", lw=5)

        ax.text(x_mur, 202, f"Façade à {dist_scan:.0f} m\nSpot = {spot_mm:.1f} mm", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "SCANNER LASER 3D TERRESTRE : DIVERGENCE DU FAISCEAU ET TAILLE DU SPOT", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Distance façade = {dist_scan:.0f} m  =>  Diamètre de la tache laser (spot) = {spot_mm:.1f} mm", color="#22c55e" if spot_mm <= 18.0 else "#f59e0b", fontsize=8, fontweight="bold")
        st.session_state.ag_mesure_courante = (f"D = {dist_scan:.0f} m", "Div = 0,25 mrad", f"Spot = {spot_mm:.1f} mm", "DÉTAIL FIN" if spot_mm <= 18.0 else "SPOT LARGE")

    return fig


def afficher_atelier_app_geo(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort une mission Géomètre ci-dessus.")
        return
    banque = BANQUES_APP_GEO[sujet_idx]
    cle_ordre = f"ordre_quiz_ag_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Géomètre Topographe (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"ag_at10_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Géomètre Topographe (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")



BANQUES_APP_TRANS = {
    0: {
        "questions": [
            {"id": "qatr0_1", "q": "Quel type de miroir équipe les rétroviseurs grand-angle et antéviseur d'un poids lourd pour élargir le champ de vision et supprimer les angles morts ?", "options": ["Un miroir convexe (bombé vers l'extérieur)", "Un miroir concave", "Un prisme dispersif"], "rep": "Un miroir convexe (bombé vers l'extérieur)"},
            {"id": "qatr0_2", "q": "Quelle est la nature de l'image observée dans un rétroviseur convexe de véhicule ?", "options": ["Virtuelle, droite et plus petite que l'objet réel", "Réelle et renversée", "Agrandie 10 fois"], "rep": "Virtuelle, droite et plus petite que l'objet réel"},
            {"id": "qatr0_3", "q": "Pourquoi les objets observés dans un rétroviseur grand-angle convexe paraissent-ils plus éloignés qu'ils ne le sont en réalité ?", "options": ["Parce que le miroir convexe réduit la taille apparente des véhicules suiveurs", "Parce que la lumière ralentit", "Parce que le verre est teinté en bleu"], "rep": "Parce que le miroir convexe réduit la taille apparente des véhicules suiveurs"},
            {"id": "qatr0_4", "q": "Par quel dispositif optique et électronique les caméras de rétrovision (CMS / MirrorCam) remplacent-elles les rétroviseurs extérieurs sur les poids lourds récents ?", "options": ["Des caméras à objectif grand-angle reliées à des écrans intérieurs montés sur les montants de pare-brise", "Des lunettes astronomiques", "Des périscopes à eau"], "rep": "Des caméras à objectif grand-angle reliées à des écrans intérieurs montés sur les montants de pare-brise"},
            {"id": "qatr0_5", "q": "Quel avantage aérodynamique et énergétique apporte le remplacement des gros blocs rétroviseurs par des bras caméras profilés (CMS) ?", "options": ["Une réduction de la traînée aérodynamique permettant d'économiser 1 à 2 % de carburant", "Une augmentation du poids de 500 kg", "Une suppression des phares"], "rep": "Une réduction de la traînée aérodynamique permettant d'économiser 1 à 2 % de carburant"},
            {"id": "qatr0_6", "q": "Comment s'appelle le rétroviseur orienté vers le sol juste devant la cabine d'un camion pour voir les piétons ou cyclistes à l'arrêt ?", "options": ["Le rétroviseur antéviseur (classe VI)", "Le télescope de Newton", "La loupe binoculaire"], "rep": "Le rétroviseur antéviseur (classe VI)"},
            {"id": "qatr0_7", "q": "Quelle loi optique régit la réflexion d'un rayon lumineux sur le miroir d'un rétroviseur ?", "options": ["La loi de Snell-Descartes : l'angle de réflexion est égal à l'angle d'incidence (i' = i)", "La loi d'Ohm", "La loi de Boyle-Mariotte"], "rep": "La loi de Snell-Descartes : l'angle de réflexion est égal à l'angle d'incidence (i' = i)"},
            {"id": "qatr0_8", "q": "Comment les rétroviseurs intérieurs électrochromes évitent-ils l'éblouissement nocturne par les phares d'un véhicule suiveur ?", "options": ["Un gel électrochrome s'assombrit automatiquement sous l'effet d'un capteur de lumière pour absorber l'excès de flux réfléchi", "Ils basculent vers le plafond", "Ils émettent un flash rouge"], "rep": "Un gel électrochrome s'assombrit automatiquement sous l'effet d'un capteur de lumière pour absorber l'excès de flux réfléchi"},
            {"id": "qatr0_9", "q": "Quel capteur équipe les caméras de recul et caméras latérales d'angle mort pour voir de nuit lors des manœuvres à quai ?", "options": ["Un capteur CMOS haute sensibilité assisté de LED infrarouges invisibles", "Un microscope optique", "Une lampe au sodium"], "rep": "Un capteur CMOS haute sensibilité assisté de LED infrarouges invisibles"},
            {"id": "qatr0_10", "q": "Quel avantage procure l'affichage par caméra CMS par rapport à un miroir classique par temps de pluie battante ou de nuit ?", "options": ["Le capteur numérique amplifie la luminosité de nuit et les lentilles chauffantes évitent les gouttes d'eau", "Il coupe la pluie", "Il augmente la vitesse du camion"], "rep": "Le capteur numérique amplifie la luminosité de nuit et les lentilles chauffantes évitent les gouttes d'eau"},
        ],
        "trous": [
            ("1. Les rétroviseurs grand-angle utilisent un miroir ......... pour élargir le champ de vision.", ["Choisir...", "convexe", "concave"], "convexe", "atr_t1"),
            ("2. L'image formée par un miroir convexe est virtuelle, ......... et plus petite que l'objet.", ["Choisir...", "droite", "renversée"], "droite", "atr_t2"),
            ("3. Lors de la réflexion sur un miroir, l'angle de réflexion est ......... à l'angle d'incidence.", ["Choisir...", "égal", "supérieur"], "égal", "atr_t3"),
            ("4. Le miroir orienté vers l'avant bas de la cabine s'appelle l'.........", ["Choisir...", "antéviseur", "oculaire"], "antéviseur", "atr_t4"),
            ("5. Les systèmes CMS remplacent les miroirs par des caméras à objectif .........-angle.", ["Choisir...", "grand", "télé"], "grand", "atr_t5"),
            ("6. L'image est projetée sur un capteur ......... puis affichée sur un écran en cabine.", ["Choisir...", "CMOS", "argentique"], "CMOS", "atr_t6"),
            ("7. Les bras caméras réduisent la résistance ......... et la consommation de gazole.", ["Choisir...", "aérodynamique", "thermique"], "aérodynamique", "atr_t7"),
            ("8. Un rétroviseur ......... s'assombrit automatiquement la nuit pour éviter l'éblouissement.", ["Choisir...", "électrochrome", "parabolique"], "électrochrome", "atr_t8"),
            ("9. Les caméras de recul utilisent des LED ......... pour éclairer la zone sans éblouir.", ["Choisir...", "infrarouges", "ultraviolettes"], "infrarouges", "atr_t9"),
            ("10. Les miroirs grand-angle permettent de réduire les ......... morts autour du véhicule.", ["Choisir...", "angles", "points"], "angles", "atr_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qatr1_1", "q": "Où est placée la caméra optique des systèmes d'aide à la conduite ADAS (maintien dans la voie, freinage d'urgence AEBS) sur un véhicule ?", "options": ["En haut du pare-brise, dans la zone balayée par les essuie-glaces", "Sous le châssis arrière", "Dans le réservoir de carburant"], "rep": "En haut du pare-brise, dans la zone balayée par les essuie-glaces"},
            {"id": "qatr1_2", "q": "Quel composant optique de la caméra ADAS projette l'image de la route devant le camion sur le capteur CMOS ?", "options": ["Un objectif convergent multi-lentilles à focale fixe calibrée", "Un prisme de Newton", "Une lentille divergente seule"], "rep": "Un objectif convergent multi-lentilles à focale fixe calibrée"},
            {"id": "qatr1_3", "q": "Comment une caméra stéréoscopique (double objectif espacé de 20 à 30 cm) mesure-t-elle la distance d'un piéton ou d'un véhicule devant le camion ?", "options": ["Par triangulation (parallaxe) en comparant le décalage entre l'image gauche et l'image droite", "En envoyant un faisceau laser", "En pesant la route"], "rep": "Par triangulation (parallaxe) en comparant le décalage entre l'image gauche et l'image droite"},
            {"id": "qatr1_4", "q": "Pourquoi faut-il obligatoirement recalibrer la caméra ADAS après le remplacement d'un pare-brise fissuré en atelier ?", "options": ["Car un décalage d'un seul degré de l'axe optique entraîne une erreur de plusieurs mètres à 100 m de distance", "Pour recharger la batterie", "Pour nettoyer les lentilles"], "rep": "Car un décalage d'un seul degré de l'axe optique entraîne une erreur de plusieurs mètres à 100 m de distance"},
            {"id": "qatr1_5", "q": "Quel panneau géométrique noir et blanc place le technicien devant le véhicule lors du calibrage statique de la caméra ADAS ?", "options": ["Une cible de calibrage étalonnée positionnée à une distance et hauteur précises", "Un miroir concave", "Une mire de nivellement"], "rep": "Une cible de calibrage étalonnée positionnée à une distance et hauteur précises"},
            {"id": "qatr1_6", "q": "Quel rôle joue le capteur optique de pluie et de luminosité collé contre le pare-brise ?", "options": ["Il détecte la perte de réflexion totale interne causée par les gouttes d'eau pour déclencher les essuie-glaces", "Il mesure la pression des pneus", "Il refroidit le pare-brise"], "rep": "Il détecte la perte de réflexion totale interne causée par les gouttes d'eau pour déclencher les essuie-glaces"},
            {"id": "qatr1_7", "q": "Quelle est la nature de l'image formée par l'objectif de la caméra ADAS sur son capteur électronique ?", "options": ["Réelle, renversée et réduite", "Virtuelle et droite", "Infinie"], "rep": "Réelle, renversée et réduite"},
            {"id": "qatr1_8", "q": "Pourquoi l'objectif d'une caméra ADAS possède-t-il une focale fixe sans zoom mécanique ?", "options": ["Pour conserver un étalonnage géométrique invariable permettant le calcul précis des distances", "Par manque de place", "Pour économiser le plastique"], "rep": "Pour conserver un étalonnage géométrique invariable permettant le calcul précis des distances"},
            {"id": "qatr1_9", "q": "Quel phénomène optique produit par un soleil rasant bas sur l'horizon peut temporairement aveugler la caméra frontale ADAS ?", "options": ["L'éblouissement direct (saturation du capteur CMOS et reflets internes « flare »)", "La diffraction nocturne", "L'absorption infrarouge"], "rep": "L'éblouissement direct (saturation du capteur CMOS et reflets internes « flare »)"},
            {"id": "qatr1_10", "q": "Quelle fonction de sécurité déclenche le freinage automatique d'urgence lorsqu'la caméra et le radar détectent un obstacle immobile ?", "options": ["L'AEBS (Advanced Emergency Braking System)", "L'ABS seul", "Le régulateur de vitesse"], "rep": "L'AEBS (Advanced Emergency Braking System)"},
        ],
        "trous": [
            ("1. La caméra frontale ADAS est fixée en haut du .........-brise.", ["Choisir...", "pare", "coupe"], "pare", "atr_t1"),
            ("2. Son objectif convergent forme une image ......... et renversée sur le capteur CMOS.", ["Choisir...", "réelle", "virtuelle"], "réelle", "atr_t2"),
            ("3. Une caméra stéréoscopique mesure les distances par ......... entre deux objectifs.", ["Choisir...", "triangulation", "diffraction"], "triangulation", "atr_t3"),
            ("4. Après un changement de pare-brise, il faut effectuer le ......... de la caméra.", ["Choisir...", "calibrage", "polissage"], "calibrage", "atr_t4"),
            ("5. Le calibrage statique utilise une ......... géométrique placée devant le véhicule.", ["Choisir...", "cible", "loupe"], "cible", "atr_t5"),
            ("6. Le capteur de pluie utilise la perte de ......... totale interne sur le verre mouillé.", ["Choisir...", "réflexion", "absorption"], "réflexion", "atr_t6"),
            ("7. L'objectif ADAS possède une focale ......... pour garantir la précision des mesures.", ["Choisir...", "fixe", "variable"], "fixe", "atr_t7"),
            ("8. Un soleil rasant peut provoquer la ......... du capteur électronique.", ["Choisir...", "saturation", "congélation"], "saturation", "atr_t8"),
            ("9. Le système de freinage d'urgence assisté par caméra s'appelle l'.........", ["Choisir...", "AEBS", "ESP"], "AEBS", "atr_t9"),
            ("10. Le système LKA détecte le franchissement involontaire des ......... blanches.", ["Choisir...", "lignes", "glissières"], "lignes", "atr_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qatr2_1", "q": "Quel composant optique équipe les projecteurs lenticulaires (ellipsoïdaux) modernes des poids lourds et automobiles ?", "options": ["Une épaisse lentille convergente plan-convexe en verre projetant le faisceau sur la route", "Un prisme triangulaire", "Une lentille divergente"], "rep": "Une épaisse lentille convergente plan-convexe en verre projetant le faisceau sur la route"},
            {"id": "qatr2_2", "q": "Quel élément mécanique placé au foyer de la lentille d'un projecteur lenticulaire crée la coupure horizontale nette des feux de croisement ?", "options": ["Un cache métallique (volet de coupure) qui bloque la moitié supérieure du faisceau", "Un filtre rouge", "Un miroir plan"], "rep": "Un cache métallique (volet de coupure) qui bloque la moitié supérieure du faisceau"},
            {"id": "qatr2_3", "q": "Pourquoi le faisceau d'un projecteur lenticulaire est-il renversé par la lentille convergente ?", "options": ["Parce que la lentille convergente projette une image réelle et renversée du cache de coupure sur la route", "Parce que l'ampoule est montée à l'envers", "Parce que le verre est teinté"], "rep": "Parce que la lentille convergente projette une image réelle et renversée du cache de coupure sur la route"},
            {"id": "qatr2_4", "q": "Comment un projecteur Bi-Xénon ou Bi-LED passe-t-il instantanément des feux de croisement aux feux de route avec une seule lentille ?", "options": ["Un électroaimant abaisse le volet métallique de coupure pour libérer tout le faisceau lumineux", "La lentille tourne à 180°", "On change d'ampoule en roulant"], "rep": "Un électroaimant abaisse le volet métallique de coupure pour libérer tout le faisceau lumineux"},
            {"id": "qatr2_5", "q": "Quelle est la forme géométrique du réflecteur placé derrière la source lumineuse dans un phare classique pour renvoyer les rayons vers l'avant ?", "options": ["Un miroir concave parabolique (source placée au foyer F)", "Un miroir plan", "Un miroir convexe"], "rep": "Un miroir concave parabolique (source placée au foyer F)"},
            {"id": "qatr2_6", "q": "Lorsque la source LED ou halogène est placée exactement au foyer F d'un miroir parabolique, comment ressortent les rayons réfléchis ?", "options": ["Parallèles à l'axe optique pour éclairer loin devant le véhicule", "Convergents à 10 cm du phare", "Vers l'arrière du véhicule"], "rep": "Parallèles à l'axe optique pour éclairer loin devant le véhicule"},
            {"id": "qatr2_7", "q": "Quel défaut d'optique apparaît sur un phare en polycarbonate vieilli par les UV du soleil et les gravillons ?", "options": ["L'opacification (jaunissement) qui diffuse la lumière, réduit la portée et entraîne un refus au contrôle technique", "Une augmentation de la puissance", "Un changement de couleur en vert"], "rep": "L'opacification (jaunissement) qui diffuse la lumière, réduit la portée et entraîne un refus au contrôle technique"},
            {"id": "qatr2_8", "q": "Quel appareil optique d'atelier utilise le mécanicien pour contrôler le faisceau et la ligne de coupure d'un phare ?", "options": ["Un régloscope (composé d'une lentille convergente et d'un écran gradué interne)", "Un microscope", "Une loupe binoculaire"], "rep": "Un régloscope (composé d'une lentille convergente et d'un écran gradué interne)"},
            {"id": "qatr2_9", "q": "Comment fonctionne l'écran interne d'un régloscope placé à 30 cm devant le phare d'un camion ?", "options": ["Sa lentille convergente forme dans son plan focal image l'image réduite du faisceau projeté à 25 mètres", "Il mesure la température du pneu", "Il recharge le phare"], "rep": "Sa lentille convergente forme dans son plan focal image l'image réduite du faisceau projeté à 25 mètres"},
            {"id": "qatr2_10", "q": "Pourquoi les projecteurs Matrix LED comportent-ils plusieurs dizaines de micro-lentilles indépendantes ?", "options": ["Pour éteindre uniquement le faisceau dirigé vers un véhicule croisé tout en gardant les pleins phares ailleurs", "Pour faire clignoter les phares", "Pour éclairer l'intérieur de la cabine"], "rep": "Pour éteindre uniquement le faisceau dirigé vers un véhicule croisé tout en gardant les pleins phares ailleurs"},
        ],
        "trous": [
            ("1. Un projecteur lenticulaire utilise une lentille ......... pour projeter le faisceau.", ["Choisir...", "convergente", "divergente"], "convergente", "atr_t1"),
            ("2. Un ......... métallique interne crée la coupure nette des feux de croisement.", ["Choisir...", "volet", "prisme"], "volet", "atr_t2"),
            ("3. Dans un phare parabolique, l'ampoule est placée au ......... du miroir concave.", ["Choisir...", "foyer", "sommet"], "foyer", "atr_t3"),
            ("4. Les rayons issus du foyer d'une parabole ressortent ......... à l'axe optique.", ["Choisir...", "parallèles", "perpendiculaires"], "parallèles", "atr_t4"),
            ("5. Le vieillissement du polycarbonate entraîne une ......... qui diffuse la lumière.", ["Choisir...", "opacification", "focalisation"], "opacification", "atr_t5"),
            ("6. Le contrôle de l'orientation des phares s'effectue avec un .........", ["Choisir...", "régloscope", "endoscope"], "régloscope", "atr_t6"),
            ("7. L'écran du régloscope est placé dans le plan ......... image de sa lentille.", ["Choisir...", "focal", "central"], "focal", "atr_t7"),
            ("8. La lentille convergente projette une image ......... et renversée du faisceau.", ["Choisir...", "réelle", "virtuelle"], "réelle", "atr_t8"),
            ("9. Les phares ......... LED pilotent individuellement chaque faisceau lumineux.", ["Choisir...", "Matrix", "Halogène"], "Matrix", "atr_t9"),
            ("10. Le faisceau de croisement est asymétrique pour éclairer le bas-côté .........", ["Choisir...", "droit", "gauche"], "droit", "atr_t10"),
        ]
    }
}


def mettre_a_jour_app_trans_matplotlib(sujet_idx):
    """Banc d'essai Appareils Optiques adapté au Transport Routier."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        type_retro = st.session_state.get("radio_atr_s0", "Miroir Convexe Grand-Angle (Champ 45°)")
        if "Plan" in type_retro:
            angle_c, dy, c_r, msg_r = 18, 35, "#f59e0b", "MIROIR PLAN (Champ 18°) : Taille réelle mais angle mort latéral important !"
        else:
            angle_c, dy, c_r, msg_r = 45, 95, "#22c55e", "MIROIR CONVEXE GRAND-ANGLE (Champ 45°) : Angle mort éliminé, image virtuelle réduite."

        ax.add_patch(patches.Rectangle((60, 95), 95, 60, facecolor="#1e3a8a", edgecolor="white", lw=1.5))
        ax.text(107, 125, "Cabine PL\nRétroviseur", color="white", fontsize=8, fontweight="bold", ha="center", va="center")


        ax.fill([155, 520, 520], [125, 125 - dy, 125 + dy], color=c_r, alpha=0.25)
        ax.plot([155, 520], [125, 125 - dy], color=c_r, lw=2)
        ax.plot([155, 520], [125, 125 + dy], color=c_r, lw=2)

        ax.text(25, 18, "RÉTROVISION POIDS LOURDS : MIROIR PLAN VS MIROIR CONVEXE GRAND-ANGLE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg_r, color=c_r, fontsize=8, fontweight="bold")
        st.session_state.atr_mesure_courante = (type_retro.split("(").strip(), f"Champ = {angle_c}°", "Image virtuelle", "ANGLE MORT OK" if angle_c >= 40 else "ANGLE MORT")

    elif sujet_idx == 1:
        ecart_deg = st.session_state.get("slider_atr_s1", 0.0)
        dist_cible = 80.0
        err_lat = round(dist_cible * math.tan(math.radians(abs(ecart_deg))), 2)

        ax.add_patch(patches.Rectangle((55, 100), 90, 50, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(100, 125, "Caméra ADAS\nPare-brise", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot([145, 505], [125, 125], color="#94a3b8", lw=1.5, ls="--")
        y_dev = 125 - ecart_deg * 18.0
        c_adas = "#22c55e" if abs(ecart_deg) <= 0.3 else "#ef4444"
        ax.plot([145, 505], [125, y_dev], color=c_adas, lw=3)


        ax.add_patch(patches.Rectangle((505, 85), 25, 80, facecolor="#f8fafc", edgecolor="#eab308", lw=1.5))
        ax.text(517, 180, "Cible\n80 m", color="#fde047", fontsize=8, fontweight="bold", ha="center")
        ax.text(517, 180, "Cible\n80 m", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "CALIBRAGE CAMÉRA ADAS : IMPACT D'UN DÉFAUT D'ALIGNEMENT ANGULAIRE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Écart angulaire = {ecart_deg:+.1f}°  =>  Décalage latéral à 80 m = {err_lat:.2f} mètres", color=c_adas, fontsize=8, fontweight="bold")
        st.session_state.atr_mesure_courante = (f"Angle = {ecart_deg:+.1f}°", "Distance = 80 m", f"Erreur = {err_lat:.2f} m", "CALIBRÉ" if abs(ecart_deg) <= 0.3 else "RECALIBRER")

    else:
        mode_phare = st.session_state.get("radio_atr_s2", "Feux de croisement (Volet de coupure abaissé)")
        ax.add_patch(patches.Circle((85, 125), 14, facecolor="#fde047", edgecolor="white"))
        ax.text(85, 155, "LED", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        ax.plot([210, 210], [65, 185], color="#3b82f6", lw=4)
        ax.text(210, 52, "Lentille convergente", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        if "croisement" in mode_phare:
            ax.add_patch(patches.Rectangle((145, 65), 10, 60, facecolor="#ef4444", edgecolor="white"))
            ax.text(150, 55, "Volet", color="#ef4444", fontsize=7.5, fontweight="bold", ha="center")
            ax.fill([210, 530, 530], [125, 125, 195], color="#fde047", alpha=0.35)
            msg_p = "FEUX DE CROISEMENT : Le volet bloque le haut ; la lentille projette le faisceau sous l'horizon."
        else:
            ax.fill([210, 530, 530], [125, 65, 185], color="#fde047", alpha=0.45)
            msg_p = "FEUX DE ROUTE (BI-LED) : Volet escamoté ; plein faisceau longue portée activé."


        ax.text(25, 18, "PROJECTEUR LENTICULAIRE : LENTILLE CONVERGENTE ET VOLET DE COUPURE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg_p, color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.atr_mesure_courante = (mode_phare.split("(")[0].strip(), "Lentille conv.", "Coupure nette", "CONFORME")

    return fig


def afficher_atelier_app_trans(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet Transport Routier ci-dessus.")
        return
    banque = BANQUES_APP_TRANS[sujet_idx]
    cle_ordre = f"ordre_quiz_atr_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Transport Routier (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"atr_at9_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Transport Routier (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")






BANQUES_APP_TP = {
    0: {
        "questions": [
            {"id": "qatp0_1", "q": "Quel appareil optique utilise le chef de chantier Travaux Publics pour mesurer des différences d'altitude (nivellement direct) sur un terrassement ?", "options": ["Un niveau optique de chantier (lunette de nivellement)", "Un microscope composé", "Une loupe binoculaire"], "rep": "Un niveau optique de chantier (lunette de nivellement)"},
            {"id": "qatp0_2", "q": "Sur quel accessoire gradué en centimètres et millimètres le technicien effectue-t-il ses lectures à travers la lunette du niveau optique ?", "options": ["Une mire parlante verticale", "Un prisme de Newton", "Une règle en bois non graduée"], "rep": "Une mire parlante verticale"},
            {"id": "qatp0_3", "q": "Quelle est la nature de l'image de la mire observée à travers un niveau optique de chantier moderne ?", "options": ["Droite (redressée grâce à un prisme redresseur interne)", "Renversée à l'envers", "Floue sur les bords"], "rep": "Droite (redressée grâce à un prisme redresseur interne)"},
            {"id": "qatp0_4", "q": "Comment appelle-t-on la croix gravée sur une lentille interne de la lunette permettant de viser précisément une graduation de la mire ?", "options": ["Le réticule (avec fil niveleur horizontal et fils stadimétriques)", "Le diaphragme iris", "Le capteur CMOS"], "rep": "Le réticule (avec fil niveleur horizontal et fils stadimétriques)"},
            {"id": "qatp0_5", "q": "Comment calcule-t-on rapidement la distance horizontale D (en mètres) entre le niveau optique et la mire à partir de l'écart ΔH (en mètres) lu entre les deux fils stadimétriques ?", "options": ["D = 100 × ΔH (constante stadimétrique K = 100)", "D = ΔH / 100", "D = 10 + ΔH"], "rep": "D = 100 × ΔH (constante stadimétrique K = 100)"},
            {"id": "qatp0_6", "q": "Si le fil stadimétrique supérieur indique 1,650 m et le fil inférieur indique 1,250 m sur la mire, quelle est la distance D du niveau à la mire ?", "options": ["40 mètres (100 × 0,400 m)", "0,40 mètre", "290 mètres"], "rep": "40 mètres (100 × 0,400 m)"},
            {"id": "qatp0_7", "q": "Quel mécanisme interne suspendu par des fils fins maintient automatiquement la ligne de visée parfaitement horizontale après calage de la nivelle sphérique ?", "options": ["Le compensateur automatique à prisme pendulaire", "Un moteur thermique", "Une batterie 24 V"], "rep": "Le compensateur automatique à prisme pendulaire"},
            {"id": "qatp0_8", "q": "Quelle molette latérale du niveau optique permet de rendre l'image de la mire parfaitement nette quelle que soit sa distance (de 1 m à 100 m) ?", "options": ["La molette de mise au point interne (qui déplace une lentille divergente interne)", "La vis de blocage du trépied", "Le bouton d'allumage"], "rep": "La molette de mise au point interne (qui déplace une lentille divergente interne)"},
            {"id": "qatp0_9", "q": "Que signifie un grossissement de 24× ou 32× inscrit sur le corps d'un niveau optique de chantier ?", "options": ["L'objet visé est vu sous un angle 24 ou 32 fois plus grand qu'à l'œil nu", "L'appareil pèse 24 kg", "La portée est limitée à 24 mètres"], "rep": "L'objet visé est vu sous un angle 24 ou 32 fois plus grand qu'à l'œil nu"},
            {"id": "qatp0_10", "q": "Pourquoi faut-il toujours équilibrer les portées (distance arrière ≈ distance avant) lors d'un cheminement au niveau optique ?", "options": ["Pour éliminer toute erreur résiduelle de collimation (défaut d'horizontalité de l'axe optique)", "Pour économiser la batterie", "Pour aller plus vite"], "rep": "Pour éliminer toute erreur résiduelle de collimation (défaut d'horizontalité de l'axe optique)"},
        ],
        "trous": [
            ("1. Le nivellement optique utilise une lunette de visée et une ......... parlante graduée.", ["Choisir...", "mire", "sonde"], "mire", "atp_t1"),
            ("2. Un ......... redresseur interne permet d'observer la mire à l'endroit.", ["Choisir...", "prisme", "filtre"], "prisme", "atp_t2"),
            ("3. Le repère de visée gravé dans la lunette s'appelle le .........", ["Choisir...", "réticule", "verre dépoli"], "réticule", "atp_t3"),
            ("4. L'écart entre les deux fils stadimétriques permet de calculer la ......... D = 100 × ΔH.", ["Choisir...", "distance", "température"], "distance", "atp_t4"),
            ("5. Le ......... automatique maintient l'axe optique horizontal.", ["Choisir...", "compensateur", "diaphragme"], "compensateur", "atp_t5"),
            ("6. La molette latérale assure la ......... au point selon l'éloignement de la mire.", ["Choisir...", "mise", "remise"], "mise", "atp_t6"),
            ("7. Un grossissement de 32× multiplie par ......... l'angle apparent de la mire.", ["Choisir...", "32", "3,2"], "32", "atp_t7"),
            ("8. Avant la mesure, on cale la bulle de la ......... sphérique grâce aux trois vis calantes.", ["Choisir...", "nivelle", "lentille"], "nivelle", "atp_t8"),
            ("9. Si ΔH = 0,250 m entre les fils stadimétriques, la distance vaut ......... mètres.", ["Choisir...", "25", "2,5"], "25", "atp_t9"),
            ("10. L'égalité des portées arrière et avant annule l'erreur de ......... de l'axe optique.", ["Choisir...", "collimation", "réfraction"], "collimation", "atp_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qatp1_1", "q": "Quel appareil optique robotisé utilise-t-on en Travaux Publics pour inspecter l'état intérieur des réseaux d'assainissement enterrés ?", "options": ["Un chariot caméra d'inspection télévisée (ITV)", "Une lunette astronomique", "Un microscope métallographique"], "rep": "Un chariot caméra d'inspection télévisée (ITV)"},
            {"id": "qatp1_2", "q": "Quel type d'objectif équipe la tête rotative d'une caméra d'inspection de canalisations (ITV) ?", "options": ["Un objectif grand-angle (focale très courte) permettant de voir toute la circonférence du tuyau", "Un téléobjectif à champ étroit", "Un oculaire divergent"], "rep": "Un objectif grand-angle (focale très courte) permettant de voir toute la circonférence du tuyau"},
            {"id": "qatp1_3", "q": "Pourquoi l'objectif d'une caméra ITV est-il protégé par un hublot en verre saphir ou polycarbonate épais ?", "options": ["Pour assurer l'étanchéité sous pression d'eau et résister aux rayures des graviers", "Pour grossir l'image 100 fois", "Pour filtrer la lumière rouge"], "rep": "Pour assurer l'étanchéité sous pression d'eau et résister aux rayures des graviers"},
            {"id": "qatp1_4", "q": "Comment mesure-t-on la largeur exacte d'une fissure dans une canalisation à l'aide d'une caméra ITV moderne ?", "options": ["Par projection de deux points laser parallèles d'écartement connu servant d'échelle optique sur l'image", "En envoyant un mètre ruban", "À l'œil nu sans repère"], "rep": "Par projection de deux points laser parallèles d'écartement connu servant d'échelle optique sur l'image"},
            {"id": "qatp1_5", "q": "Quel problème optique survient lorsque le hublot de la caméra ITV est couvert de buée à cause de l'humidité de l'égout ?", "options": ["Les microgouttelettes diffusent la lumière des LED et rendent l'image floue et laiteuse", "L'image devient inversée", "Le capteur CMOS s'éteint"], "rep": "Les microgouttelettes diffusent la lumière des LED et rendent l'image floue et laiteuse"},
            {"id": "qatp1_6", "q": "Quelle couronne entoure l'objectif de la caméra ITV pour éclairer l'intérieur du collecteur enterré ?", "options": ["Une couronne de LED blanches haute puissance à intensité réglable", "Un miroir concave", "Une lampe au sodium"], "rep": "Une couronne de LED blanches haute puissance à intensité réglable"},
            {"id": "qatp1_7", "q": "Dans quel cas l'inspection vidéo des réseaux (ITV) est-elle obligatoire en Travaux Publics ?", "options": ["Avant la réception des travaux de pose de canalisations neuves et pour le diagnostic de réhabilitation", "Uniquement pour les lignes électriques aériennes", "Uniquement pour les autoroutes"], "rep": "Avant la réception des travaux de pose de canalisations neuves et pour le diagnostic de réhabilitation"},
            {"id": "qatp1_8", "q": "Sur quel composant électronique se forme l'image réelle projetée par l'objectif de la caméra ITV ?", "options": ["Un capteur numérique CMOS haute sensibilité", "Un prisme de Newton", "Une lentille divergente"], "rep": "Un capteur numérique CMOS haute sensibilité"},
            {"id": "qatp1_9", "q": "Pourquoi utilise-t-on une tête de caméra rotative (panoramique 360° / inclinaison 180°) dans les collecteurs ?", "options": ["Pour orienter l'axe optique perpendiculairement aux branchements latéraux et aux joints", "Pour refroidir le moteur du chariot", "Pour mesurer la pente"], "rep": "Pour orienter l'axe optique perpendiculairement aux branchements latéraux et aux joints"},
            {"id": "qatp1_10", "q": "Quel défaut optique est typique des objectifs très grand-angle (« fisheye ») utilisés en inspection de tuyaux ?", "options": ["Une distorsion en barillet (courbure des lignes droites sur les bords de l'image)", "Une image en noir et blanc", "Une perte totale du centre"], "rep": "Une distorsion en barillet (courbure des lignes droites sur les bords de l'image)"},
        ],
        "trous": [
            ("1. L'état des canalisations enterrées est contrôlé par caméra d'inspection ......... (ITV).", ["Choisir...", "télévisée", "thermique"], "télévisée", "atp_t1"),
            ("2. La caméra utilise un objectif .........-angle pour visualiser toute la paroi du tuyau.", ["Choisir...", "grand", "télé"], "grand", "atp_t2"),
            ("3. L'image réelle se forme sur un capteur électronique ......... haute sensibilité.", ["Choisir...", "CMOS", "argentique"], "CMOS", "atp_t3"),
            ("4. Deux faisceaux ......... parallèles permettent de mesurer la largeur des fissures sur l'écran.", ["Choisir...", "laser", "ultrasons"], "laser", "atp_t4"),
            ("5. Le hublot frontal en verre ......... protège l'optique de l'eau et des rayures.", ["Choisir...", "saphir", "ordinaire"], "saphir", "atp_t5"),
            ("6. La buée sur le hublot provoque une ......... de la lumière rendant l'image floue.", ["Choisir...", "diffusion", "réfraction"], "diffusion", "atp_t6"),
            ("7. L'éclairage du collecteur est assuré par une couronne de ......... blanches.", ["Choisir...", "LED", "halogènes"], "LED", "atp_t7"),
            ("8. Un objectif très grand-angle introduit une ......... géométrique sur les bords.", ["Choisir...", "distorsion", "dispersion"], "distorsion", "atp_t8"),
            ("9. La tête optique est ......... à 360° pour inspecter les branchements latéraux.", ["Choisir...", "rotative", "fixe"], "rotative", "atp_t9"),
            ("10. Le contrôle ITV est obligatoire avant la ......... d'un réseau d'assainissement neuf.", ["Choisir...", "réception", "démolition"], "réception", "atp_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qatp2_1", "q": "Quel instrument optique portable utilise le conducteur de travaux pour inspecter à distance l'état des piles d'un pont ou d'une falaise rocheuse ?", "options": ["Des jumelles à prismes de Porro ou en toit", "Une loupe de bijoutier", "Un microscope"], "rep": "Des jumelles à prismes de Porro ou en toit"},
            {"id": "qatp2_2", "q": "Pourquoi les jumelles modernes de chantier sont-elles beaucoup plus courtes qu'une lunette astronomique de même grossissement ?", "options": ["Elles utilisent des prismes à réflexion totale qui replient le trajet lumineux et redressent l'image", "Elles n'ont pas d'objectif", "Elles utilisent des miroirs paraboliques"], "rep": "Elles utilisent des prismes à réflexion totale qui replient le trajet lumineux et redressent l'image"},
            {"id": "qatp2_3", "q": "Que signifient les deux nombres « 10 × 42 » gravés sur une paire de jumelles de chantier ?", "options": ["Grossissement de 10× et diamètre des objectifs de 42 mm", "Portée de 10 km et poids de 420 g", "10 lentilles et 42 prismes"], "rep": "Grossissement de 10× et diamètre des objectifs de 42 mm"},
            {"id": "qatp2_4", "q": "Quel avantage apporte un grand diamètre d'objectif (ex : 50 mm au lieu de 25 mm) sur des jumelles ?", "options": ["Il collecte davantage de lumière, offrant une image plus lumineuse par temps couvert ou au crépuscule", "Il augmente le grossissement", "Il rend les jumelles plus légères"], "rep": "Il collecte davantage de lumière, offrant une image plus lumineuse par temps couvert ou au crépuscule"},
            {"id": "qatp2_5", "q": "À quoi servent les traitements antireflets multicouches (teinte verte ou bleutée) déposés sur les lentilles des jumelles et niveaux optiques ?", "options": ["À augmenter la transmission de la lumière (jusqu'à 95 %) et supprimer les reflets parasites", "À teinter le paysage en vert", "À rendre le verre incassable"], "rep": "À augmenter la transmission de la lumière (jusqu'à 95 %) et supprimer les reflets parasites"},
            {"id": "qatp2_6", "q": "Quelle est la nature de l'image finale observée à travers des jumelles à prismes ?", "options": ["Droite, virtuelle, rejetée à l'infini et agrandie", "Renversée et réelle", "Plus petite que l'objet"], "rep": "Droite, virtuelle, rejetée à l'infini et agrandie"},
            {"id": "qatp2_7", "q": "Comment s'appelle le diamètre du faisceau lumineux sortant de l'oculaire des jumelles (calculé par D_objectif / Grossissement) ?", "options": ["La pupille de sortie (ou cercle oculaire)", "La distance focale", "Le réticule"], "rep": "La pupille de sortie (ou cercle oculaire)"},
            {"id": "qatp2_8", "q": "Quelle est la taille de la pupille de sortie d'une paire de jumelles 8 × 40 ?", "options": ["5 mm (40 mm / 8)", "320 mm", "0,2 mm"], "rep": "5 mm (40 mm / 8)"},
            {"id": "qatp2_9", "q": "Pourquoi remplit-on l'intérieur des jumelles et niveaux optiques de chantier avec de l'azote sec ?", "options": ["Pour empêcher la formation de buée interne sur les lentilles lors des variations de température", "Pour alléger l'appareil", "Pour refroidir les prismes"], "rep": "Pour empêcher la formation de buée interne sur les lentilles lors des variations de température"},
            {"id": "qatp2_10", "q": "Quelle précaution de sécurité est impérative lors de l'utilisation de jumelles ou d'une lunette de chantier ?", "options": ["Ne jamais viser le Soleil sous peine de brûlure irréversible de la rétine", "Toujours garder les bouchons fermés", "Ne les utiliser que la nuit"], "rep": "Ne jamais viser le Soleil sous peine de brûlure irréversible de la rétine"},
        ],
        "trous": [
            ("1. Les jumelles utilisent des ......... internes pour redresser l'image et raccourcir le tube.", ["Choisir...", "prismes", "miroirs plans"], "prismes", "atp_t1"),
            ("2. Les prismes renvoient la lumière sans perte par ......... totale interne.", ["Choisir...", "réflexion", "absorption"], "réflexion", "atp_t2"),
            ("3. Sur des jumelles 10 × 42, le grossissement vaut .........", ["Choisir...", "10×", "42×"], "10×", "atp_t3"),
            ("4. Le nombre 42 désigne le ......... de l'objectif en millimètres.", ["Choisir...", "diamètre", "poids"], "diamètre", "atp_t4"),
            ("5. Le traitement ......... sur les lentilles augmente la luminosité de l'image.", ["Choisir...", "antireflet", "opaque"], "antireflet", "atp_t5"),
            ("6. Le diamètre du faisceau sortant de l'oculaire s'appelle la ......... de sortie.", ["Choisir...", "pupille", "rétine"], "pupille", "atp_t6"),
            ("7. Pour des jumelles 8 × 40, la pupille de sortie mesure ......... mm.", ["Choisir...", "5", "32"], "5", "atp_t7"),
            ("8. Le remplissage à l'......... sec évite la buée interne sur les optiques de chantier.", ["Choisir...", "azote", "oxygène"], "azote", "atp_t8"),
            ("9. L'image finale vue dans des jumelles est agrandie et .........", ["Choisir...", "droite", "renversée"], "droite", "atp_t9"),
            ("10. Il est strictement interdit de viser le ......... avec une lunette ou des jumelles.", ["Choisir...", "Soleil", "ciel nocturne"], "Soleil", "atp_t10"),
        ]
    }
}


def mettre_a_jour_app_tp_matplotlib(sujet_idx):
    """Banc d'essai Appareils Optiques adapté aux Travaux Publics."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        dist_m = st.session_state.get("slider_atp_s0", 35.0)
        lec_niv = 1.450
        delta_h = round(dist_m / 100.0, 3)
        fil_sup = round(lec_niv + delta_h / 2.0, 3)
        fil_inf = round(lec_niv - delta_h / 2.0, 3)

        ax.add_patch(patches.Rectangle((55, 100), 90, 45, facecolor="#eab308", edgecolor="white", lw=1.5))
        ax.text(100, 122, "Niveau Optique\n(K = 100)", color="#0f172a", fontsize=8, fontweight="bold", ha="center", va="center")

        x_mire = 180.0 + (dist_m / 80.0) * 330.0
        ax.plot([145, x_mire], [122, 122], color="#22c55e", lw=2)
        ax.plot([145, x_mire], [122, 122 - dist_m * 0.45], color="#38bdf8", lw=1.2, ls="--")
        ax.plot([145, x_mire], [122, 122 + dist_m * 0.45], color="#38bdf8", lw=1.2, ls="--")


        ax.add_patch(patches.Rectangle((x_mire, 65), 24, 130, facecolor="#f8fafc", edgecolor="#ef4444", lw=1.5))
        ax.text(x_mire + 12, 208, f"Mire parlante\nD = {dist_m:.0f} m", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "NIVELLEMENT OPTIQUE DE CHANTIER : LECTURE STADIMÉTRIQUE SUR MIRE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Fil sup = {fil_sup:.3f} m  |  Fil niv = {lec_niv:.3f} m  |  Fil inf = {fil_inf:.3f} m  =>  D = 100 × {delta_h:.3f} = {dist_m:.1f} m", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.atp_mesure_courante = (f"Sup={fil_sup:.3f}m", f"Inf={fil_inf:.3f}m", f"ΔH={delta_h:.3f}m", f"D = {dist_m:.1f} m")

    elif sujet_idx == 1:
        foc_itv = st.session_state.get("radio_atp_s1", "Grand-angle 3,6 mm (Vision 360° paroi)")
        if "Grand-angle" in foc_itv:
            angle_v, msg_itv, c_itv = 120, "CHAMP LARGE (120°) : Visualisation complète des parois et joints du collecteur.", "#22c55e"
        else:
            angle_v, msg_itv, c_itv = 35, "CHAMP ÉTROIT (35°) : Zoom sur le fond du tuyau mais parois latérales invisibles !", "#f59e0b"

        ax.add_patch(patches.Rectangle((65, 100), 85, 50, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(107, 125, "Chariot ITV\nCapteur CMOS", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        dy = 85 if angle_v == 120 else 28
        ax.fill([150, 520, 520], [125, 125 - dy, 125 + dy], color=c_itv, alpha=0.25)
        ax.plot([150, 520], [40, 40], color="#94a3b8", lw=4)
        ax.plot([150, 520], [210, 210], color="#94a3b8", lw=4)

        ax.text(300, 224, "Canalisation d'assainissement enterrée", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

        ax.text(25, 18, "ASSAINISSEMENT TP : CAMÉRA D'INSPECTION TÉLÉVISÉE (ITV) GRAND-ANGLE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg_itv, color=c_itv, fontsize=8, fontweight="bold")
        st.session_state.atp_mesure_courante = (foc_itv.split("(")[0].strip(), f"Champ = {angle_v}°", "Capteur CMOS", "OPTIMAL" if angle_v == 120 else "CHAMP RÉDUIT")

    else:
        jum = st.session_state.get("radio_atp_s2", "Jumelles 10 × 42 (Chantier jour)")
        g_j = 8 if "8" in jum else (10 if "10" in jum else 12)
        d_obj = 32 if "32" in jum else (42 if "42" in jum else 50)
        pupille = round(d_obj / g_j, 1)

        ax.add_patch(patches.Rectangle((70, 85), 160, 80, facecolor="#1e293b", edgecolor="#38bdf8", lw=2))
        ax.text(150, 125, f"Jumelles à prismes\n{g_j} × {d_obj}", color="white", fontsize=9, fontweight="bold", ha="center", va="center")

        ax.add_patch(patches.Circle((370, 125), pupille * 6.0, facecolor="#38bdf8", edgecolor="white", lw=2))
        ax.text(370, 185, f"Pupille de sortie = {pupille:.1f} mm\n(D_obj / G)", color="#fde047", fontsize=8.5, fontweight="bold", ha="center")

        ax.text(25, 18, "INSPECTION D'OUVRAGES D'ART : JUMELLES À PRISMES ET PUPILLE DE SORTIE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Grossissement = {g_j}×  |  Diamètre objectif = {d_obj} mm  =>  Pupille de sortie = {pupille:.1f} mm", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.atp_mesure_courante = (f"{g_j} × {d_obj}", f"G = {g_j}×", f"Pupille = {pupille:.1f} mm", "LUMINEUX" if pupille >= 4.0 else "JOUR UNIQUEMENT")

    return fig


def afficher_atelier_app_tp(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un chantier TP ci-dessus.")
        return
    banque = BANQUES_APP_TP[sujet_idx]
    cle_ordre = f"ordre_quiz_atp_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Travaux Publics (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"atp_at8_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Travaux Publics (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")



BANQUES_APP_MAINT = {
    0: {
        "questions": [
            {"id": "qam0_1", "q": "Quel instrument optique souple ou rigide permet d'inspecter l'intérieur d'un moteur, d'une turbine ou d'une canalisation sans démontage ?", "options": ["Un endoscope industriel (fibroscope ou vidéoscope)", "Un télescope de Newton", "Un théodolite"], "rep": "Un endoscope industriel (fibroscope ou vidéoscope)"},
            {"id": "qam0_2", "q": "Quel phénomène optique permet de guider la lumière d'éclairage et l'image le long du tube souple d'un fibroscope ?", "options": ["La réflexion totale interne à l'intérieur des fibres optiques en verre", "La dispersion prismatique", "La diffraction"], "rep": "La réflexion totale interne à l'intérieur des fibres optiques en verre"},
            {"id": "qam0_3", "q": "Dans un vidéoscope industriel moderne, où se situe le capteur miniature CMOS qui filme les défauts internes ?", "options": ["Directement à l'extrémité distale de la sonde, juste derrière un objectif grand-angle", "Dans la poignée uniquement", "Sur l'écran de contrôle"], "rep": "Directement à l'extrémité distale de la sonde, juste derrière un objectif grand-angle"},
            {"id": "qam0_4", "q": "Quel type d'objectif équipe l'extrémité d'un endoscope pour observer une large zone à très courte distance (quelques millimètres) ?", "options": ["Un objectif grand-angle à très courte distance focale", "Un téléobjectif de 300 mm", "Une lentille divergente seule"], "rep": "Un objectif grand-angle à très courte distance focale"},
            {"id": "qam0_5", "q": "Quelle est la nature de l'image formée par l'objectif miniature sur le micro-capteur d'un vidéoscope ?", "options": ["Réelle et renversée (redressée électroniquement sur l'écran)", "Virtuelle et droite", "Infinie"], "rep": "Réelle et renversée (redressée électroniquement sur l'écran)"},
            {"id": "qam0_6", "q": "Pourquoi l'indice de réfraction du cœur d'une fibre optique doit-il être supérieur à celui de sa gaine optique ?", "options": ["Pour garantir la réflexion totale interne sans perte de lumière dans les courbes", "Pour accélérer la lumière au-delà de c", "Pour colorer l'image en bleu"], "rep": "Pour garantir la réflexion totale interne sans perte de lumière dans les courbes"},
            {"id": "qam0_7", "q": "Quel avantage majeur procure l'endoscopie en maintenance préventive aéronautique ou automobile ?", "options": ["Éviter un démontage long et coûteux tout en détectant fissures, corrosion ou corps étrangers", "Augmenter la puissance du moteur", "Remplacer l'huile moteur"], "rep": "Éviter un démontage long et coûteux tout en détectant fissures, corrosion ou corps étrangers"},
            {"id": "qam0_8", "q": "Comment éclaire-t-on l'intérieur sombre d'un cylindre ou d'une boîte de vitesses lors d'un contrôle endoscopique ?", "options": ["Par des LED miniatures intégrées en bout de sonde ou un faisceau de fibres d'éclairage", "Avec la lumière du soleil uniquement", "Avec un laser infrarouge"], "rep": "Par des LED miniatures intégrées en bout de sonde ou un faisceau de fibres d'éclairage"},
            {"id": "qam0_9", "q": "Dans un endoscope rigide (boroscope), quel système optique transporte l'image jusqu'à l'oculaire ?", "options": ["Une série de lentilles relais convergentes", "Un seul miroir plan", "Un prisme de Newton"], "rep": "Une série de lentilles relais convergentes"},
            {"id": "qam0_10", "q": "Que signifie une profondeur de champ étendue sur un endoscope industriel ?", "options": ["La capacité à voir net simultanément des pièces proches et plus éloignées sans refaire la mise au point", "La longueur maximale du câble", "Le poids de la mallette"], "rep": "La capacité à voir net simultanément des pièces proches et plus éloignées sans refaire la mise au point"},
        ],
        "trous": [
            ("1. L'inspection visuelle interne sans démontage s'effectue à l'aide d'un .........", ["Choisir...", "endoscope", "télescope"], "endoscope", "am_t1"),
            ("2. La lumière est guidée dans les fibres optiques par ......... totale interne.", ["Choisir...", "réflexion", "absorption"], "réflexion", "am_t2"),
            ("3. Le cœur de la fibre possède un ......... de réfraction supérieur à celui de la gaine.", ["Choisir...", "indice", "diamètre"], "indice", "am_t3"),
            ("4. L'extrémité de la sonde comporte un objectif ......... à très courte focale.", ["Choisir...", "grand-angle", "téléobjectif"], "grand-angle", "am_t4"),
            ("5. Sur le micro-capteur CMOS, l'objectif forme une image ......... et renversée.", ["Choisir...", "réelle", "virtuelle"], "réelle", "am_t5"),
            ("6. L'éclairage interne est assuré par des ......... miniatures en bout de sonde.", ["Choisir...", "LED", "bougies"], "LED", "am_t6"),
            ("7. Un endoscope rigide utilise une suite de lentilles ......... convergentes.", ["Choisir...", "relais", "divergentes"], "relais", "am_t7"),
            ("8. Une grande ......... de champ permet de voir net sur plusieurs centimètres.", ["Choisir...", "profondeur", "largeur"], "profondeur", "am_t8"),
            ("9. Ce contrôle non destructif relève de la maintenance .........", ["Choisir...", "préventive", "corrective"], "préventive", "am_t9"),
            ("10. L'endoscopie permet de détecter les fissures et la ......... interne.", ["Choisir...", "corrosion", "pression"], "corrosion", "am_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qam1_1", "q": "Quel appareil optique de précision utilise-t-on en atelier électronique pour souder des composants CMS et inspecter les circuits imprimés en relief ?", "options": ["Une loupe binoculaire (stéréomicroscope)", "Une lunette astronomique", "Un niveau optique"], "rep": "Une loupe binoculaire (stéréomicroscope)"},
            {"id": "qam1_2", "q": "Pourquoi une loupe binoculaire offre-t-elle une vision en relief (stéréoscopique) indispensable pour manipuler des outils sous l'objectif ?", "options": ["Elle possède deux chemins optiques distincts formant un léger angle entre l'œil gauche et l'œil droit", "Elle utilise un laser rouge", "Elle inverse le haut et le bas"], "rep": "Elle possède deux chemins optiques distincts formant un léger angle entre l'œil gauche et l'œil droit"},
            {"id": "qam1_3", "q": "Quelle est la différence majeure entre l'image observée dans un microscope biologique classique et dans une loupe binoculaire d'atelier ?", "options": ["La loupe binoculaire intègre des prismes redresseurs donnant une image droite (non inversée)", "La loupe binoculaire grossit 10 000 fois", "La loupe binoculaire n'a pas d'oculaires"], "rep": "La loupe binoculaire intègre des prismes redresseurs donnant une image droite (non inversée)"},
            {"id": "qam1_4", "q": "Comment appelle-t-on la distance entre l'objectif de la loupe binoculaire et la carte électronique observée ?", "options": ["La distance de travail (souvent 80 à 120 mm pour passer le fer à souder)", "L'intervalle optique Delta", "La distance focale image"], "rep": "La distance de travail (souvent 80 à 120 mm pour passer le fer à souder)"},
            {"id": "qam1_5", "q": "Si une loupe binoculaire est réglée sur un objectif 2x et équipée d'oculaires 10x, quel est le grossissement total ?", "options": ["20x (2 × 10)", "12x (2 + 10)", "5x (10 / 2)"], "rep": "20x (2 × 10)"},
            {"id": "qam1_6", "q": "Quel appareil optique utilise le laboratoire de maintenance pour analyser la structure cristalline d'un acier ou l'origine d'une rupture mécanique ?", "options": ["Un microscope métallographique (à éclairage épiscopique par réflexion)", "Une lunette de Galilée", "Un appareil photo jetable"], "rep": "Un microscope métallographique (à éclairage épiscopique par réflexion)"},
            {"id": "qam1_7", "q": "Pourquoi un microscope métallographique éclaire-t-il l'échantillon métallique par le dessus (à travers l'objectif) plutôt que par dessous ?", "options": ["Parce que le métal est opaque et ne laisse pas passer la lumière par transmission", "Parce que la lampe est trop grosse", "Pour chauffer le métal"], "rep": "Parce que le métal est opaque et ne laisse pas passer la lumière par transmission"},
            {"id": "qam1_8", "q": "À quoi servent les bonnettes en caoutchouc et le réglage de l'écartement interpupillaire sur les oculaires ?", "options": ["À aligner parfaitement les deux faisceaux avec les yeux du technicien pour éviter la fatigue visuelle", "À augmenter le grossissement", "À protéger la carte électronique"], "rep": "À aligner parfaitement les deux faisceaux avec les yeux du technicien pour éviter la fatigue visuelle"},
            {"id": "qam1_9", "q": "Que permet la bague de correction dioptrique située sur l'un des oculaires de la loupe binoculaire ?", "options": ["De compenser une différence de vue entre l'œil gauche et l'œil droit de l'opérateur", "De changer la couleur de l'éclairage", "De bloquer le zoom"], "rep": "De compenser une différence de vue entre l'œil gauche et l'œil droit de l'opérateur"},
            {"id": "qam1_10", "q": "Quelle est l'unité du grossissement d'une loupe binoculaire ou d'un microscope ?", "options": ["Sans unité (noté par un nombre suivi de ×, ex : 20×)", "En mètres", "En kelvins"], "rep": "Sans unité (noté par un nombre suivi de ×, ex : 20×)"},
        ],
        "trous": [
            ("1. En atelier électronique, on utilise une loupe ......... pour voir les soudures en relief.", ["Choisir...", "binoculaire", "monoculaire"], "binoculaire", "am_t1"),
            ("2. Des ......... redresseurs permettent d'obtenir une image droite facilitant le geste.", ["Choisir...", "prismes", "miroirs plans"], "prismes", "am_t2"),
            ("3. L'espace libre sous l'objectif pour passer les outils s'appelle la distance de .........", ["Choisir...", "travail", "freinage"], "travail", "am_t3"),
            ("4. Avec un objectif 3x et des oculaires 10x, le grossissement total vaut .........x.", ["Choisir...", "30", "13"], "30", "am_t4"),
            ("5. Pour analyser un métal opaque, on utilise un microscope .........", ["Choisir...", "métallographique", "astronomique"], "métallographique", "am_t5"),
            ("6. Le métal étant opaque, l'éclairage se fait par ......... sur la surface polie.", ["Choisir...", "réflexion", "transparence"], "réflexion", "am_t6"),
            ("7. Le réglage de l'écartement ......... adapte l'instrument aux yeux de l'opérateur.", ["Choisir...", "interpupillaire", "focal"], "interpupillaire", "am_t7"),
            ("8. La bague ......... compense la différence de vue entre les deux yeux.", ["Choisir...", "dioptrique", "magnétique"], "dioptrique", "am_t8"),
            ("9. Les lentilles situées près des yeux de l'observateur sont les .........", ["Choisir...", "oculaires", "objectifs"], "oculaires", "am_t9"),
            ("10. Le grossissement optique est une grandeur ......... unité.", ["Choisir...", "sans", "en"], "sans", "am_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qam2_1", "q": "Quel appareil optique de diagnostic détecte à distance les points chauds sur une armoire électrique ou un roulement en rotation ?", "options": ["Une caméra thermique infrarouge", "Une loupe simple", "Un microscope optique"], "rep": "Une caméra thermique infrarouge"},
            {"id": "qam2_2", "q": "Dans quel domaine du spectre électromagnétique fonctionne le capteur microbolomètre d'une caméra thermique ?", "options": ["L'infrarouge thermique (longueurs d'onde de 8 à 14 µm)", "L'ultraviolet (200 nm)", "Le visible bleu (450 nm)"], "rep": "L'infrarouge thermique (longueurs d'onde de 8 à 14 µm)"},
            {"id": "qam2_3", "q": "Pourquoi l'objectif d'une caméra thermique est-il fabriqué en germanium (cristal opaque à la lumière visible) plutôt qu'en verre ordinaire ?", "options": ["Parce que le verre ordinaire bloque les rayons infrarouges thermiques alors que le germanium est transparent aux IR", "Parce que le germanium est moins cher que le verre", "Pour colorer l'image en vert"], "rep": "Parce que le verre ordinaire bloque les rayons infrarouges thermiques alors que le germanium est transparent aux IR"},
            {"id": "qam2_4", "q": "Comment appelle-t-on le paramètre compris entre 0 et 1 qui caractérise la capacité d'une surface à émettre un rayonnement thermique ?", "options": ["L'émissivité (ε)", "L'albédo", "La vergence"], "rep": "L'émissivité (ε)"},
            {"id": "qam2_5", "q": "Pourquoi une barre de cuivre ou d'inox poli et brillant (faible émissivité ε ≈ 0,10) fausse-t-elle la mesure d'une caméra thermique ?", "options": ["Elle agit comme un miroir infrarouge et réfléchit la chaleur des objets environnants au lieu d'émettre la sienne", "Elle absorbe tous les rayons X", "Elle refroidit la caméra"], "rep": "Elle agit comme un miroir infrarouge et réfléchit la chaleur des objets environnants au lieu d'émettre la sienne"},
            {"id": "qam2_6", "q": "Quelle astuce utilise le technicien de maintenance pour mesurer avec précision la température d'un tube en métal brillant à la caméra thermique ?", "options": ["Coller un morceau de ruban adhésif isolant noir mat (émissivité connue ε ≈ 0,95) sur le tube", "Arroser le tube d'eau froide", "Éteindre l'éclairage de l'atelier"], "rep": "Coller un morceau de ruban adhésif isolant noir mat (émissivité connue ε ≈ 0,95) sur le tube"},
            {"id": "qam2_7", "q": "Quelle loi physique établit que tout corps dont la température est supérieure au zéro absolu (-273,15 °C) émet un rayonnement électromagnétique ?", "options": ["La loi du rayonnement du corps noir (Planck / Stefan-Boltzmann)", "La loi d'Archimède", "La loi de Hooke"], "rep": "La loi du rayonnement du corps noir (Planck / Stefan-Boltzmann)"},
            {"id": "qam2_8", "q": "Que révèle un échauffement anormal localisé sur une borne de disjoncteur dans un tableau électrique ?", "options": ["Un mauvais serrage de la connexion entraînant une résistance de contact élevée (effet Joule)", "Une baisse de tension normale", "Un défaut de peinture"], "rep": "Un mauvais serrage de la connexion entraînant une résistance de contact élevée (effet Joule)"},
            {"id": "qam2_9", "q": "Comment l'écran de la caméra thermique représente-t-il les écarts de température invisibles à l'œil nu ?", "options": ["En fausses couleurs (palette arc-en-ciel ou fer : du bleu/noir froid au jaune/blanc chaud)", "En texte uniquement", "En ultrasons"], "rep": "En fausses couleurs (palette arc-en-ciel ou fer : du bleu/noir froid au jaune/blanc chaud)"},
            {"id": "qam2_10", "q": "Quel avantage essentiel offre la thermographie infrarouge lors de l'inspection d'une installation électrique haute tension ?", "options": ["Mesurer la température à distance, sans contact et sans couper la production", "Remplacer les fusibles à distance", "Augmenter le courant"], "rep": "Mesurer la température à distance, sans contact et sans couper la production"},
        ],
        "trous": [
            ("1. La caméra thermique capte le rayonnement ......... émis par les machines.", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "am_t1"),
            ("2. Son objectif convergent est taillé dans un cristal de ......... transparent aux IR.", ["Choisir...", "germanium", "verre ordinaire"], "germanium", "am_t2"),
            ("3. Le verre ordinaire est ......... aux rayons infrarouges lointains.", ["Choisir...", "opaque", "transparent"], "opaque", "am_t3"),
            ("4. La capacité d'un matériau à rayonner sa chaleur s'appelle l'......... (ε).", ["Choisir...", "émissivité", "absorbance"], "émissivité", "am_t4"),
            ("5. Un métal poli et brillant possède une émissivité très ......... (≈ 0,10).", ["Choisir...", "faible", "élevée"], "faible", "am_t5"),
            ("6. Pour mesurer sur du métal brillant, on colle un ruban adhésif noir .........", ["Choisir...", "mat", "transparent"], "mat", "am_t6"),
            ("7. Un mauvais serrage électrique provoque un échauffement par effet .........", ["Choisir...", "Joule", "Doppler"], "Joule", "am_t7"),
            ("8. L'image thermique est affichée sur l'écran en ......... couleurs.", ["Choisir...", "fausses", "vraies"], "fausses", "am_t8"),
            ("9. La thermographie s'effectue à distance et sans ......... avec les pièces sous tension.", ["Choisir...", "contact", "objectif"], "contact", "am_t9"),
            ("10. Le contrôle thermique permet d'anticiper les pannes en maintenance .........", ["Choisir...", "prédictive", "destructive"], "prédictive", "am_t10"),
        ]
    }
}


def mettre_a_jour_app_maint_matplotlib(sujet_idx):
    """Banc d'essai Appareils Optiques adapté à la Maintenance Industrielle."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        angle_inc = st.session_state.get("slider_am_s0", 18.0)
        angle_limite = 24.0
        ax.add_patch(patches.Rectangle((60, 75), 480, 100, facecolor="#1e293b", edgecolor="#64748b", lw=1.5))
        ax.add_patch(patches.Rectangle((60, 95), 480, 60, facecolor="#0f172a", edgecolor="#38bdf8", lw=1.5))
        ax.text(300, 64, "Gaine optique (n2 = 1,45)  /  Cœur de la fibre (n1 = 1,48)", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

        if angle_inc <= angle_limite:
            ax.plot([60, 180, 300, 420, 540], [125, 95, 155, 95, 125], color="#22c55e", lw=3)
            msg = f"RÉFLEXION TOTALE INTERNE (Angle = {angle_inc:.0f}° ≤ 24°) : Image transmise sans perte !"
            c_m = "#22c55e"
            diag = "TRANSMISSION OK"
        else:
            ax.plot([60, 220], [125, 95], color="#ef4444", lw=3)
            ax.plot([220, 310], [95, 62], color="#ef4444", lw=2, ls="--")
            msg = f"PERTE DE SIGNAL (Rayon de courbure trop serré : {angle_inc:.0f}° > 24°) : La lumière sort de la fibre !"
            c_m = "#ef4444"
            diag = "COURBURE EXCESSIVE"


        ax.text(25, 18, "ENDOSCOPIE INDUSTRIELLE : GUIDAGE DE LA LUMIÈRE PAR FIBRE OPTIQUE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg, color=c_m, fontsize=8, fontweight="bold")
        st.session_state.am_mesure_courante = (f"Angle = {angle_inc:.0f}°", "n1=1,48 / n2=1,45", "Limite = 24°", diag)

    elif sujet_idx == 1:
        obj_bino = st.session_state.get("radio_am_s1", "Objectif 2x (Grossissement total 20x)")
        g_obj = 1 if "1x" in obj_bino else (2 if "2x" in obj_bino else 4)
        g_tot = g_obj * 10
        dist_trav = 115 if g_obj == 1 else (95 if g_obj == 2 else 65)

        ax.add_patch(patches.Rectangle((210, 45), 180, 40, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(300, 65, f"Loupe Binoculaire\n(Oculaires 10x + Obj {g_obj}x)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        y_carte = 85 + dist_trav
        ax.plot([255, 295], [85, y_carte], color="#eab308", lw=2)
        ax.plot([345, 305], [85, y_carte], color="#eab308", lw=2)
        ax.add_patch(patches.Rectangle((180, y_carte), 240, 18, facecolor="#15803d", edgecolor="white"))

        ax.text(300, y_carte + 9, "Carte électronique CMS", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.text(25, 18, "CONTRÔLE ÉLECTRONIQUE : LOUPE BINOCULAIRE STÉRÉOSCOPIQUE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 18, "CONTRÔLE ÉLECTRONIQUE : LOUPE BINOCULAIRE STÉRÉOSCOPIQUE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Grossissement total = {g_tot}x  |  Distance de travail libre = {dist_trav} mm  |  Image : Droite & Relief 3D", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.am_mesure_courante = (f"Obj {g_obj}x / Ocu 10x", f"G = {g_tot}x", f"D_trav = {dist_trav} mm", "VISION 3D OK")

    else:
        surface_ir = st.session_state.get("radio_am_s2", "Borne électrique + Ruban noir mat (ε = 0,95)")
        if "poli" in surface_ir:
            eps, temp_lue = 0.12, 26.5
            msg_ir = "ERREUR DE MESURE : Le cuivre poli réfléchit la pièce (26,5 °C lus au lieu de 85 °C réels) !"
            c_ir = "#ef4444"
        else:
            eps, temp_lue = 0.95, 84.2
            msg_ir = "MESURE FIABLE (ε = 0,95) : Détection d'un point chaud critique à 84,2 °C ! Resserrer la borne."
            c_ir = "#22c55e"

        ax.add_patch(patches.Rectangle((65, 95), 110, 65, facecolor="#334155", edgecolor="#38bdf8", lw=1.5))
        ax.text(120, 127, f"Caméra IR\nObjectif Germanium\nT lue = {temp_lue:.1f} °C", color="#fde047", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.annotate("", xy=(175, 127), xytext=(410, 127), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=3, ls="--"))
        ax.add_patch(patches.Rectangle((410, 85), 120, 85, facecolor="#b45309" if "poli" in surface_ir else "#1e293b", edgecolor="white", lw=1.5))
        ax.text(470, 127, f"Borne 85 °C\nε = {eps:.2f}", color="white", fontsize=8.5, fontweight="bold", ha="center", va="center")

        ax.text(25, 18, "THERMOGRAPHIE INFRAROUGE : OBJECTIF EN GERMANIUM ET ÉMISSIVITÉ", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, msg_ir, color=c_ir, fontsize=8, fontweight="bold")
        st.session_state.am_mesure_courante = (surface_ir.split("(").strip(), f"ε = {eps:.2f}", f"T lue = {temp_lue:.1f} °C", "ALERTE CHAUD" if eps > 0.5 else "REFLET FAUX")

    return fig


def afficher_atelier_app_maint(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet de maintenance ci-dessus.")
        return
    banque = BANQUES_APP_MAINT[sujet_idx]
    cle_ordre = f"ordre_quiz_am_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Maintenance (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"am_at7_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Maintenance (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")







def afficher_atelier_hist_optique(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Histoire des appareils optiques."""
    questions_ho = [
        {"id": "qho1", "q": "Quel savant arabe du XIe siècle a décrit le principe de la chambre noire (camera obscura) projetant une image renversée ?", "options": ["Ibn al-Haytham (Alhazen)", "Aristote", "Archimède"], "rep": "Ibn al-Haytham (Alhazen)"},
        {"id": "qho2", "q": "Quel artisan opticien hollandais a déposé le premier brevet de lunette d'approche en 1608 ?", "options": ["Hans Lippershey", "Johannes Kepler", "Isaac Newton"], "rep": "Hans Lippershey"},
        {"id": "qho3", "q": "En quelle année Galilée a-t-il perfectionné la lunette astronomique pour découvrir les cratères de la Lune et les satellites de Jupiter ?", "options": ["1609", "1492", "1889"], "rep": "1609"},
        {"id": "qho4", "q": "Quelle est la particularité de l'oculaire de la lunette inventée par Galilée ?", "options": ["C'est une lentille divergente qui donne une image droite", "C'est un miroir sphérique", "C'est un prisme triangulaire"], "rep": "C'est une lentille divergente qui donne une image droite"},
        {"id": "qho5", "q": "Quel astronome allemand a remplacé en 1611 l'oculaire divergent de Galilée par un oculaire convergent pour élargir le champ de vision ?", "options": ["Johannes Kepler", "Nicolas Copernic", "Tycho Brahe"], "rep": "Johannes Kepler"},
        {"id": "qho6", "q": "Quel savant anglais a inventé en 1668 le premier télescope réflecteur utilisant un miroir concave à la place d'une lentille objectif ?", "options": ["Isaac Newton", "Thomas Young", "Robert Hooke"], "rep": "Isaac Newton"},
        {"id": "qho7", "q": "Quel naturaliste néerlandais du XVIIe siècle a observé les premiers micro-organismes (bactéries, globules) avec un microscope simple à une lentille ?", "options": ["Antoni van Leeuwenhoek", "Louis Pasteur", "Blaise Pascal"], "rep": "Antoni van Leeuwenhoek"},
        {"id": "qho8", "q": "Quel scientifique anglais a publié en 1665 l'ouvrage Micrographia décrivant les cellules observées au microscope composé ?", "options": ["Robert Hooke", "Michael Faraday", "James Watt"], "rep": "Robert Hooke"},
        {"id": "qho9", "q": "Quel inventeur français a réalisé en 1826-1827 la première photographie permanente de l'histoire à l'aide d'une chambre noire ?", "options": ["Nicéphore Niépce", "Louis Daguerre", "Gustave Eiffel"], "rep": "Nicéphore Niépce"},
        {"id": "qho10", "q": "Quel composant électronique a remplacé la pellicule argentique dans les appareils photographiques modernes ?", "options": ["Le capteur numérique CMOS / CCD", "Le tube cathodique", "La bobine de Tesla"], "rep": "Le capteur numérique CMOS / CCD"},
    ]

    if "ordre_quiz_ho_aleatoire" not in st.session_state:
        random.shuffle(questions_ho)
        st.session_state.ordre_quiz_ho_aleatoire = questions_ho

    champs_ho = [
        ("1. Au XIe siècle, Alhazen décrit la chambre ......... qui projette une image renversée.", ["Choisir...", "noire", "claire"], "noire", "ho_t1"),
        ("2. En 1609, ......... observe les astres avec une lunette munie d'un oculaire divergent.", ["Choisir...", "Galilée", "Newton"], "Galilée", "ho_t2"),
        ("3. En 1611, Johannes ......... utilise deux lentilles convergentes pour élargir le champ.", ["Choisir...", "Kepler", "Euclide"], "Kepler", "ho_t3"),
        ("4. En 1668, Isaac ......... remplace la lentille objectif par un miroir concave.", ["Choisir...", "Newton", "Descartes"], "Newton", "ho_t4"),
        ("5. Un télescope utilise un ......... alors qu'une lunette utilise uniquement des lentilles.", ["Choisir...", "miroir", "prisme"], "miroir", "ho_t5"),
        ("6. Au XVIIe siècle, Van Leeuwenhoek observe les bactéries grâce à une ......... puissante.", ["Choisir...", "loupe", "jumelle"], "loupe", "ho_t6"),
        ("7. Robert Hooke utilise un ......... composé pour découvrir les cellules végétales.", ["Choisir...", "microscope", "périscope"], "microscope", "ho_t7"),
        ("8. En 1827, Nicéphore ......... fixe la première image photographique de l'histoire.", ["Choisir...", "Niépce", "Lumière"], "Niépce", "ho_t8"),
        ("9. Dans un appareil photo, l'objectif forme une image ......... sur le capteur.", ["Choisir...", "réelle", "virtuelle"], "réelle", "ho_t9"),
        ("10. Les appareils photo numériques utilisent un capteur électronique .........", ["Choisir...", "CMOS", "thermique"], "CMOS", "ho_t10"),
    ]

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Historique : Les appareils optiques (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_ho_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"ho_at1_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Historique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_ho:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")



def afficher_questions_optique9(verrouille=False):
    col_double_quiz_opt9, col_double_trous_opt9 = st.columns(2)

    with col_double_quiz_opt9:
        st.markdown("##### Quiz sur le microscope (10 questions - 10 pts)")
        if "ordre_questions_opt9" not in st.session_state:
            questions_opt9_base = [
                ("q1", "Dans un microscope, la première lentille convergente très puissante près de l'objet s'appelle l' :"),
                ("q2", "La distance fixe séparant le foyer image de l'objectif F'1 et le foyer objet de l'oculaire F2 est appelée l' :"),
                ("q3", "L'image intermédiaire A1B1 créée par l'objectif du microscope est une image :"),
                ("q4", "La seconde lentille (l'oculaire) joue le rôle d'une loupe. Elle observe l'image intermédiaire placée :"),
                ("q5", "Pour un confort visuel maximal de l'observateur (œil au repos sans accommoder), l'image finale doit se former :"),
                ("q6", "Le grandissement transversal de l'objectif d'un microscope est une grandeur physique de signe :"),
                ("q7", "Le grossissement total G du microscope est égal au produit du grossissement de l'oculaire par :"),
                ("q8", "Si le grandissement de l'objectif vaut -10 et le grossissement de l'oculaire vaut 4, le grossissement total vaut :"),
                ("q9", "Par rapport à l'objet micro-optique réel placé sur la platine, l'image finale observée est :"),
                ("q10", "La puissance d'un microscope s'exprime couramment en dioptries ou par son grossissement commercial noté :")
            ]
            random.shuffle(questions_opt9_base)
            st.session_state.ordre_questions_opt9 = questions_opt9_base

        dict_quiz_opt9 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt9, 1):
            cle_qo9 = f"col_g_quiz_opt9_{q_id}"
            cle_opts_unique = f"opts_opt9_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Objectif (de très courte distance focale)", "Oculaire", "Condenseur de champ"]
                elif q_id == "q2": copie_opts = ["Intervalle optique Delta", "Distance focale totale", "Longueur mécanique du tube"]
                elif q_id == "q3": copie_opts = ["Réelle, renversée et très agrandie", "Virtuelle, droite et plus petite", "Virtuelle et renversée"]
                elif q_id == "q4": copie_opts = ["Pile dans son plan focal objet (foyer F2)", "Sur son centre optique O2", "À l'infini en aval"]
                elif q_id == "q5": copie_opts = ["À l'infini", "Sur la lentille objectif", "Au niveau du cercle oculaire"]
                elif q_id == "q6": copie_opts = ["Négatif (car l'image intermédiaire est renversée)", "Positif", "Nul"]
                elif q_id == "q7": copie_opts = ["Le grandissement de l'objectif", "La vergence de l'objectif", "La distance focale de l'oculaire"]
                elif q_id == "q8": copie_opts = ["-40", "40", "-2.5"]
                elif q_id == "q9": copie_opts = ["Renversée et fortement agrandie", "Droite et agrandie", "Renversée et plus petite"]
                elif q_id == "q10": copie_opts = ["Un nombre suivi de la lettre X (ex: x40)", "Un angle en radians", "Une valeur en mètres"]
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo9, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt9[f"{q_id}_opt9"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo9, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt9:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 items) - Optique 9 (10 pts)")
        
        items_trous_o9 = [
            ("1. Le microscope composé utilise deux systèmes convergents. Le premier est l'", ["Choisir...", "Objectif", "Oculaire", "Miroir"], "opt9_t1"),
            ("2. De très courte focale, il génère une image intermédiaire réelle. Le second est l'", ["Choisir...", "Oculaire", "Objectif", "Prisme"], "opt9_t2"),
            ("3. Il fait office de loupe pour observer cette dernière. La distance fixe F'1F2 s'appelle l'", ["Choisir...", "Intervalle optique", "Axe de visée", "Diamètre utile"], "opt9_t3"),
            ("4. L'image intermédiaire A1B1 formée par l'objectif est réelle et", ["Choisir...", "Renversée", "Droite", "Virtuelle"], "opt9_t4"),
            ("5. Pour que l'œil observe sans fatigue, l'image finale est rejetée à l'", ["Choisir...", "Infini", "Objectif", "Foyer F1"], "opt9_t5"),
            ("6. Le grandissement transversal de l'objectif d'un microscope est toujours", ["Choisir...", "Négatif", "Positif", "Nul"], "opt9_t6"),
            ("7. La distance minimale de vision distincte standard est fixée à", ["Choisir...", "25 cm", "100 cm", "1 mm"], "opt9_t7"),
            ("8. Le grossissement total G est le produit du grandissement de l'objectif par celui de l'", ["Choisir...", "Oculaire", "Écran", "Condenseur"], "opt9_t8"),
            ("9. Par rapport à l'objet placé sur la platine, l'image finale perçue est", ["Choisir...", "Renversée", "Droite", "Réduite"], "opt9_t9"),
            ("10. Le grossissement commercial d'un microscope s'écrit avec la lettre", ["Choisir...", "X", "V", "D"], "opt9_t10"),
        ]

        dict_trous_opt9 = {}
        for enonce, options, cle in items_trous_o9:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2:
                val = st.selectbox("", options, key=cle, disabled=verrouille, label_visibility="collapsed")
                dict_trous_opt9[f"{cle.replace('opt9_', '')}_opt9"] = val

    return dict_quiz_opt9, dict_trous_opt9


def afficher_questions_optique8(verrouille=False):
    col_double_quiz_opt8, col_double_trous_opt8 = st.columns(2)

    with col_double_quiz_opt8:
        st.markdown("##### Quiz sur la lunette de Galilée (10 questions - 10 pts)")
        if "ordre_questions_opt8" not in st.session_state:
            questions_opt8_base = [
                ("q1", "Quelle est la principale différence de constitution entre la lunette de Galilée et celle de Kepler :"),
                ("q2", "L'oculaire utilisé dans une lunette de Galilée possède une distance focale f'2 :"),
                ("q3", "Pour qu'une lunette de Galilée soit afocale, le foyer image F'1 de l'objectif doit être confondu avec :"),
                ("q4", "Par rapport à la lunette de Kepler, l'image finale observée à travers la lunette de Galilée est :"),
                ("q5", "L'encombrement de l'instrument (distance O1O2) d'une lunette de Galilée afocale est égal à :"),
                ("q6", "La distance séparant les deux lentilles O1O2 d'une lunette de Galilée est nécessairement :"),
                ("q7", "Le grossissement nominal G d'une lunette afocale est calculé par G = - f'1 / f'2. Pour Galilée, G est :"),
                ("q8", "Si l'objectif fait f'1 = 60 cm et l'oculaire f'2 = -15 cm, le grossissement G vaut :"),
                ("q9", "Quel est l'inconvénient principal d'une lunette de Galilée par rapport à une lunette de Kepler :"),
                ("q10", "Dans quel instrument grand public retrouve-t-on couramment le système optique de Galilée :")
            ]
            random.shuffle(questions_opt8_base)
            st.session_state.ordre_questions_opt8 = questions_opt8_base

        dict_quiz_opt8 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt8, 1):
            cle_qo8 = f"col_g_quiz_opt8_{q_id}"
            cle_opts_unique = f"opts_opt8_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["L'oculaire de Galilée est une lentille divergente", "L'objectif de Galilée est une lentille divergente", "Galilée comporte trois miroirs prismatiques"]
                elif q_id == "q2": copie_opts = ["Strictement négative (f'2 < 0)", "Strictement positive (f'2 > 0)", "Rigoureusement nulle"]
                elif q_id == "q3": copie_opts = ["Le foyer objet F2 de l'oculaire divergent", "Le foyer image F'2 de l'oculaire divergent", "Le centre optique O2"]
                elif q_id == "q4": copie_opts = ["Droite (dans le même sens que l'astre)", "Renversée (haut-bas)", "Inclinée à 90 degrés"]
                elif q_id == "q5": copie_opts = ["f'1 + f'2 (ce qui donne une soustraction car f'2 est négatif)", "f'1 - f'2 (ce qui donne une addition)", "f'1 * f'2"]
                elif q_id == "q6": copie_opts = ["Plus courte que celle de Kepler", "Plus longue que celle de Kepler", "Rigoureusement identique"]
                elif q_id == "q7": copie_opts = ["Positif (l'image finale est droite)", "Négatif (l'image finale est inversée)", "Nul"]
                elif q_id == "q8": copie_opts = ["4.0 (car f'2 est négatif)", "-4.0", "0.25"]
                elif q_id == "q9": copie_opts = ["Un champ visuel très étroit", "Une image totalement floue au centre", "Une perte totale de luminosité"]
                elif q_id == "q10": copie_opts = ["Les jumelles de théâtre (ou de spectacle)", "Les microscopes biologiques", "Les télémètres de topographie"]
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo8, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt8[f"{q_id}_opt8"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo8, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt8:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 items) - Optique 8 (10 pts)")
        
        items_trous_o8 = [
            ("1. La lunette de Galilée se distingue par l'utilisation d'un oculaire de nature", ["Choisir...", "Divergente", "Convergente", "Prismatique"], "opt8_t1"),
            ("2. Pour obtenir la configuration afocale, le foyer image de l'objectif coïncide avec le foyer", ["Choisir...", "Objet F2", "Image F'2", "Central O2"], "opt8_t2"),
            ("3. L'avantage majeur de ce montage est de générer une image finale", ["Choisir...", "Droite", "Inversée", "Virtuelle pure"], "opt8_t3"),
            ("4. Son objectif est une lentille convergente dont la distance focale f'1 est", ["Choisir...", "Positive", "Négative", "Nulle"], "opt8_t4"),
            ("5. La longueur de la lunette de Galilée (d = f'1 - |f'2|) est plus", ["Choisir...", "Courte", "Longue", "Lourde"], "opt8_t5"),
            ("6. Le grossissement nominal G de la lunette de Galilée est de signe", ["Choisir...", "Positif", "Négatif", "Nul"], "opt8_t6"),
            ("7. Pour observer l'astre sans fatigue oculaire, l'image finale est rejetée à l'", ["Choisir...", "Infini", "Objectif", "Foyer F1"], "opt8_t7"),
            ("8. Le principal défaut optique de la lunette de Galilée est un champ visuel très", ["Choisir...", "Étroit", "Large", "Sombre"], "opt8_t8"),
            ("9. On utilise encore ce principe optique dans les jumelles de", ["Choisir...", "Théâtre", "Chasse longue portée", "Astronomie"], "opt8_t9"),
            ("10. Un système optique qui transforme un faisceau parallèle en faisceau parallèle est dit", ["Choisir...", "Afocal", "Divergent", "Dispersif"], "opt8_t10"),
        ]

        dict_trous_opt8 = {}
        for enonce, options, cle in items_trous_o8:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2:
                val = st.selectbox("", options, key=cle, disabled=verrouille, label_visibility="collapsed")
                dict_trous_opt8[f"{cle.replace('opt8_', '')}_opt8"] = val

    return dict_quiz_opt8, dict_trous_opt8



def afficher_questions_optique7(verrouille=False):
    col_double_quiz_opt7, col_double_trous_opt7 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES SUR LA LUNETTE ---
    with col_double_quiz_opt7:
        st.markdown("##### Quiz sur la lunette astronomique (10 questions - 10 pts)")
        if "ordre_questions_opt7" not in st.session_state:
            questions_opt7_base = [
                ("q1", "Dans une lunette astronomique, la première lentille qui reçoit les rayons de l'astre est l' :"),
                ("q2", "La seconde lentille devant laquelle l'observateur place son œil s'appelle l' :"),
                ("q3", "Une lunette astronomique est dite « afocale » si l'image d'un objet situé à l'infini se forme :"),
                ("q4", "Pour qu'une lunette soit parfaitement afocale, il faut que le foyer image F'1 de l'objectif soit confondu avec :"),
                ("q5", "Quelle est la nature de l'image intermédiaire A1B1 créée entre l'objectif et l'oculaire :"),
                ("q6", "L'image finale de l'astre observée par l'étudiant à travers la lunette afocale est située :"),
                ("q7", "Le grossissement G d'une lunette afocale est donné par le rapport des distances focales :"),
                ("q8", "Si l'objectif a une focale f'1 = 100 cm et l'oculaire f'2 = 5 cm, le grossissement G de la lunette vaut :"),
                ("q9", "Par rapport à l'astre réel pointé dans le ciel, l'image finale observée à travers la lunette est :"),
                ("q10", "Le cercle oculaire correspond à la zone où la luminosité est maximale. Il est l'image de :")
            ]
            random.shuffle(questions_opt7_base)
            st.session_state.ordre_questions_opt7 = questions_opt7_base

        dict_quiz_opt7 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt7, 1):
            cle_qo7 = f"col_g_quiz_opt7_{q_id}"
            cle_opts_unique = f"opts_opt7_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Objectif (de grande distance focale)", "Oculaire (de courte distance focale)", "Miroir parabolique"]
                elif q_id == "q2": copie_opts = ["Oculaire", "Objectif", "Diaphragme de champ"]
                elif q_id == "q3": copie_opts = ["À l'infini (confort de vision sans fatigue pour l'œil)", "Sur le centre optique O1", "Entre les deux lentilles"]
                elif q_id == "q4": copie_opts = ["Le foyer objet F2 de l'oculaire", "Le foyer image F'2 de l'oculaire", "Le centre optique O2"]
                elif q_id == "q5": copie_opts = ["Réelle et renversée (située dans le plan focal commun)", "Virtuelle et droite", "Réelle et droite"]
                elif q_id == "q6": copie_opts = ["À l'infini (pas besoin d'accommoder)", "À la distance minimale de vision distincte", "Pile sur la lentille oculaire"]
                elif q_id == "q7": copie_opts = ["G = f'1 / f'2", "G = f'2 / f'1", "G = f'1 * f'2"]
                elif q_id == "q8": copie_opts = ["20", "200", "0.05"]
                elif q_id == "q9": copie_opts = ["Renversée (haut-bas et droite-gauche)", "Droite (dans le même sens)", "Inclinée à 45 degrés"]
                elif q_id == "q10": copie_opts = ["L'objectif par l'oculaire", "L'oculaire par l'objectif", "L'astre par l'oculaire"]
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo7, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt7[f"{q_id}_opt7"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo7, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS COMPLET (10 ITEMS = 10 PTS) ---
    with col_double_trous_opt7:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 items) - Optique 7 (10 pts)")
        
        items_trous_o7 = [
            ("1. La lunette astronomique est composée de deux lentilles convergentes. La première est l'", ["Choisir...", "Objectif", "Oculaire", "Inverseur"], "opt7_t1"),
            ("2. de grande distance focale, et la seconde, proche de l'œil, est l'", ["Choisir...", "Oculaire", "Objectif", "Prisme"], "opt7_t2"),
            ("3. Lorsque le foyer image de la première coïncide avec le foyer objet de la seconde, le système est", ["Choisir...", "Afocal", "Convergent", "Divergent"], "opt7_t3"),
            ("4. L'image d'un astre lointain sort alors à l'infini, permettant d'observer sans fatigue. Le", ["Choisir...", "Grossissement", "Grandissement", "Champ"], "opt7_t4"),
            ("5. de l'appareil correspond au rapport de la focale de l'objectif sur celle de l'", ["Choisir...", "Oculaire", "Écran", "Prisme"], "opt7_t5"),
            ("6. L'image intermédiaire A1B1 formée dans le plan focal commun est réelle et", ["Choisir...", "Renversée", "Droite", "Virtuelle"], "opt7_t6"),
            ("7. La longueur totale d'une lunette afocale est égale à la somme d = f'1 +", ["Choisir...", "f'2", "25 cm", "0"], "opt7_t7"),
            ("8. Pour observer sans accommoder, l'image finale de l'astre est rejetée à l'", ["Choisir...", "Infini", "Foyer F1", "Centre O1"], "opt7_t8"),
            ("9. La zone la plus lumineuse où placer la pupille de l'œil s'appelle le cercle", ["Choisir...", "Oculaire", "Polychromatique", "Nodal"], "opt7_t9"),
            ("10. Par rapport à l'objet céleste observé, l'image finale vue dans cette lunette est", ["Choisir...", "Renversée", "Droite", "Réduite"], "opt7_t10"),
        ]

        dict_trous_opt7 = {}
        for enonce, options, cle in items_trous_o7:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2:
                val = st.selectbox("", options, key=cle, disabled=verrouille, label_visibility="collapsed")
                dict_trous_opt7[f"{cle.replace('opt7_', '')}_opt7"] = val

    return dict_quiz_opt7, dict_trous_opt7

def dessiner_loupe_matplotlib():
    w, h = 680, 275
    y0 = h / 2.0 + 8.0

    fig, ax = plt.subplots(figsize=(10, 4.0), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()
    ax.axis("off")

    f_cm = st.session_state.get("slide_loupe_f", 10.0)
    d_obj_cm = st.session_state.get("slide_loupe_d", 6.0)
    h_obj_cm = st.session_state.get("slide_loupe_ab", 2.0)

    # Sécurité pour rester en mode loupe (objet strictement avant F)
    if d_obj_cm >= f_cm - 0.8:
        d_obj_cm = f_cm - 0.8

    # Formule de conjugaison exacte : 1/OA' - 1/OA = 1/f' avec OA = -d_obj_cm
    oa_prime_cm = (f_cm * (-d_obj_cm)) / (f_cm + (-d_obj_cm))
    gamma = oa_prime_cm / (-d_obj_cm)
    h_img_cm = h_obj_cm * gamma

    # Adaptation automatique de l'échelle pour que A'B' reste toujours dans le cadre sans déformation
    x_lentille = 430.0
    echelle_x = min(14.0, (x_lentille - 45.0) / abs(oa_prime_cm))
    echelle_y = min(22.0, (y0 - 42.0) / h_img_cm)

    f_px = f_cm * echelle_x
    xf = x_lentille - f_px
    xf_prime = x_lentille + f_px

    xa = x_lentille - d_obj_cm * echelle_x
    h_obj = h_obj_cm * echelle_y

    xa_prime = x_lentille + oa_prime_cm * echelle_x
    h_img = h_img_cm * echelle_y

    # Axe optique et foyers F et F'
    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5, zorder=1)
    ax.plot([xf, xf], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5)
    ax.text(xf, y0 + 17, "F", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")
    ax.plot([xf_prime, xf_prime], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5)
    ax.text(xf_prime, y0 + 17, "F'", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")

    # Lentille convergente (raccourcie en haut pour ne pas toucher le titre)
    y_top_l, y_bot_l = 36, h - 18
    ax.plot([x_lentille, x_lentille], [y_top_l, y_bot_l], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_lentille - 6, x_lentille, x_lentille + 6], [y_top_l + 8, y_top_l, y_top_l + 8], color="#3b82f6", lw=2)
    ax.plot([x_lentille - 6, x_lentille, x_lentille + 6], [y_bot_l - 8, y_bot_l, y_bot_l - 8], color="#3b82f6", lw=2)
    ax.text(x_lentille + 10, y0 + 15, "O", color="#cbd5e1", fontsize=8, fontweight="bold")

    # Objet réel AB (Violet)
    ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2.5), zorder=5)
    ax.text(xa, y0 + 15, "A", color="#a855f7", fontsize=8, fontweight="bold", ha="center")
    ax.text(xa, y0 - h_obj - 6, "B", color="#a855f7", fontsize=8, fontweight="bold", ha="center")

    # Image virtuelle A'B' (Vert pointillé) — position et hauteur exactes
    ax.annotate("", xy=(xa_prime, y0 - h_img), xytext=(xa_prime, y0), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2.2, ls="--"), zorder=5)
    ax.text(xa_prime, y0 + 15, "A'", color="#10b981", fontsize=8, fontweight="bold", ha="center")
    ax.text(xa_prime, y0 - h_img - 6, "B'", color="#10b981", fontsize=8, fontweight="bold", ha="center")

    x_fin = x_lentille + 145.0

    # 1. RAYON BLEU : passe par le centre optique O sans être dévié
    pente_bleu = h_obj / (x_lentille - xa)
    ax.plot([xa, x_fin], [y0 - h_obj, y0 + (x_fin - x_lentille) * pente_bleu], color="#2563eb", lw=1.6, zorder=4)
    ax.plot([xa_prime, xa], [y0 - h_img, y0 - h_obj], color="#2563eb", lw=1.3, ls=":", zorder=4)

    # 2. RAYON JAUNE : arrive parallèle à l'axe, ressort en passant par F'
    ax.plot([xa, x_lentille], [y0 - h_obj, y0 - h_obj], color="#eab308", lw=1.6, zorder=4)
    pente_jaune = h_obj / f_px
    ax.plot([x_lentille, x_fin], [y0 - h_obj, y0 - h_obj + (x_fin - x_lentille) * pente_jaune], color="#eab308", lw=1.6, zorder=4)
    ax.plot([xa_prime, x_lentille], [y0 - h_img, y0 - h_obj], color="#eab308", lw=1.3, ls=":", zorder=4)

    # 3. RAYON ROSE : aligné avec F et B, ressort parallèle à l'axe optique
    y_impact_rose = y0 - h_img
    ax.plot([xa, x_lentille], [y0 - h_obj, y_impact_rose], color="#ec4899", lw=1.6, zorder=4)
    ax.plot([x_lentille, x_fin], [y_impact_rose, y_impact_rose], color="#ec4899", lw=1.6, zorder=4)
    ax.plot([xa_prime, x_lentille], [y0 - h_img, y_impact_rose], color="#ec4899", lw=1.3, ls=":", zorder=4)

    # Œil observateur
    x_oeil = x_fin + 15.0
    y_oeil = y0 + 18.0
    ax.add_patch(patches.Arc((x_oeil, y_oeil), 20, 28, angle=90, theta1=0, theta2=180, edgecolor="#cbd5e1", lw=2, zorder=5))
    ax.add_patch(patches.Ellipse((x_oeil - 1.5, y_oeil), 7, 10, facecolor="#3b82f6", edgecolor="#1e3a8a", zorder=5))
    ax.add_patch(patches.Ellipse((x_oeil - 1.5, y_oeil), 3, 6, facecolor="black", zorder=5))

    gc = 25.0 / f_cm
    st.session_state.loupe_txt_panneau_bas = (
        f"• Distance focale f' = {f_cm:.1f} cm  |  Position objet OA = -{d_obj_cm:.1f} cm\n"
        f"• Grandissement γ = +{gamma:.2f} (Image Virtuelle et Droite)\n"
        f"• Grossissement commercial Gc = 25 / f' = {gc:.2f}x"
    )
    ax.text(20, 20, "INSTRUMENTATION : LOUPE SIMPLE (OBJET AVANT LE FOYER F)", color="#38bdf8", fontsize=9, fontweight="bold")
    return fig


def afficher_questions_loupe(verrouille=False):
    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz sur la loupe (10 questions - 10 pts)")
        if "ordre_questions_loupe" not in st.session_state:
            q_base = [
                ("q1", "Quelle est la nature de la lentille constituant une loupe simple :"),
                ("q2", "Pour qu'une lentille fonctionne en loupe, l'objet AB doit être placé :"),
                ("q3", "Quelle est la nature de l'image A'B' observée à travers une loupe :"),
                ("q4", "Par rapport à l'objet réel, l'image formée par une loupe est toujours :"),
                ("q5", "Où doit-on placer l'objet pour observer l'image à l'infini sans aucune fatigue oculaire :"),
                ("q6", "Quelle est la formule du grossissement commercial Gc d'une loupe de focale f' (en mètres) :"),
                ("q7", "Quelle est la distance minimale de vision distincte standard dm retenue pour l'œil humain :"),
                ("q8", "Si une loupe possède une distance focale f' = 5 cm (0,05 m), son grossissement commercial vaut :"),
                ("q9", "Comment s'exprime la vergence C d'une loupe de distance focale f' = 10 cm (0,10 m) :"),
                ("q10", "Si l'on éloigne l'objet au-delà du foyer objet F de la loupe, l'image devient :"),
            ]
            random.shuffle(q_base)
            st.session_state.ordre_questions_loupe = q_base

        for idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_loupe, 1):
            cle_q = f"col_g_quiz_loupe_{q_id}"
            cle_opts = f"opts_loupe_shuf_{q_id}"
            if cle_opts not in st.session_state:
                opts_map = {
                    "q1": ["Une lentille convergente de courte distance focale", "Une lentille divergente", "Un miroir plan"],
                    "q2": ["Entre le foyer objet F et le centre optique O", "Au-delà de 2 fois la distance focale", "À l'infini"],
                    "q3": ["Virtuelle (non projetable sur un écran)", "Réelle (projetable sur un écran)", "Inversée et réduite"],
                    "q4": ["Droite et agrandie", "Renversée et agrandie", "Droite et plus petite"],
                    "q5": ["Pile dans le plan focal objet (sur le foyer F)", "Contre le verre de la loupe", "À 2 mètres de la loupe"],
                    "q6": ["Gc = 0,25 / f'", "Gc = f' / 0,25", "Gc = 25 * f'"],
                    "q7": ["25 cm (0,25 m)", "100 cm (1 m)", "2,5 cm"],
                    "q8": ["5 (soit x5)", "20", "0,2"],
                    "q9": ["+10 dioptries (δ)", "-10 dioptries", "+0,1 dioptrie"],
                    "q10": ["Réelle et renversée (la lentille agit alors comme un projecteur)", "Toujours virtuelle", "Invisible"],
                }
                copie = list(opts_map[q_id])
                random.shuffle(copie)
                st.session_state[cle_opts] = ["Choisir..."] + copie
            cq1, cq2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq1: st.write(f"**{idx}.** {q_txt}")
            with cq2: st.selectbox("", st.session_state[cle_opts], key=cle_q, disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse de cours : La loupe (Texte à trous - 10 items - 10 pts)")
        items_loupe = [
            ("1. Une loupe est constituée d'une lentille mince ......... de courte distance focale.", ["Choisir...", "convergente", "divergente"], "loupe_t1"),
            ("2. L'objet observé doit être placé entre le centre optique O et le foyer objet .........", ["Choisir...", "F", "F'"], "loupe_t2"),
            ("3. L'image obtenue à travers la loupe est droite, agrandie et .........", ["Choisir...", "virtuelle", "réelle"], "loupe_t3"),
            ("4. Une image virtuelle ne peut pas être recueillie sur un .........", ["Choisir...", "écran", "capteur"], "loupe_t4"),
            ("5. Le grandissement transversal γ d'une loupe est toujours positif et supérieur à .........", ["Choisir...", "1", "0"], "loupe_t5"),
            ("6. Pour observer sans accommoder, l'objet est placé exactement au foyer .........", ["Choisir...", "objet F", "image F'"], "loupe_t6"),
            ("7. L'image finale se forme alors à l'.........", ["Choisir...", "infini", "centre O"], "loupe_t7"),
            ("8. La distance minimale de vision distincte standard vaut ......... cm.", ["Choisir...", "25", "50"], "loupe_t8"),
            ("9. Plus la distance focale f' est courte, plus le grossissement commercial est .........", ["Choisir...", "grand", "faible"], "loupe_t9"),
            ("10. L'unité de la vergence C = 1 / f' d'une loupe est la ......... (δ).", ["Choisir...", "dioptrie", "candela"], "loupe_t10"),
        ]
        for enonce, opts, cle in items_loupe:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", opts, key=cle, disabled=verrouille, label_visibility="collapsed")


def dessiner_appareil_photo_matplotlib():
    w, h = 680, 260
    y0 = h / 2.0

    fig, ax = plt.subplots(figsize=(10, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()
    ax.axis("off")

    f_mm = st.session_state.get("slide_apn_f", 50.0)
    dist_obj_m = st.session_state.get("slide_apn_d", 2.0)
    h_obj_m = st.session_state.get("slide_apn_ab", 1.6)

    x_lentille = 430.0
    f_px = f_mm * 1.4
    xf = x_lentille - f_px
    xf_prime = x_lentille + f_px

    xa = max(40.0, x_lentille - dist_obj_m * 110.0)
    h_obj = h_obj_m * 45.0

    # Conjugaison exacte en millimètres : 1/OA' = 1/f' + 1/OA
    oa_mm = -dist_obj_m * 1000.0
    oa_prime_mm = (f_mm * oa_mm) / (f_mm + oa_mm)
    gamma = oa_prime_mm / oa_mm
    x_capteur = x_lentille + f_px + (oa_prime_mm - f_mm) * 2.5
    h_img = abs(h_obj * gamma)

    # Boîtier noir de l'appareil photo
    ax.add_patch(patches.Rectangle((x_lentille, 25), (x_capteur - x_lentille) + 12, h - 50, facecolor="#1e293b", edgecolor="#64748b", lw=1.5))

    # Axe optique et foyers
    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=1.5, zorder=1)
    ax.plot([xf, xf], [y0 - 5, y0 + 5], color="#cbd5e1", lw=1.5)
    ax.text(xf, y0 + 16, "F", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center")
    ax.plot([xf_prime, xf_prime], [y0 - 5, y0 + 5], color="#38bdf8", lw=1.5)
    ax.text(xf_prime, y0 - 10, "F'", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

    # Objectif convergent
    # Objectif convergent
    ax.plot([x_lentille, x_lentille], [25, h - 25], color="#3b82f6", lw=3, zorder=3)
    ax.plot([x_lentille - 6, x_lentille, x_lentille + 6], [33, 25, 33], color="#3b82f6", lw=2)
    ax.plot([x_lentille - 6, x_lentille, x_lentille + 6], [h - 33, h - 25, h - 33], color="#3b82f6", lw=2)
    ax.text(x_lentille - 12, y0 + 14, "O", color="#cbd5e1", fontsize=8, fontweight="bold")

    # Capteur CMOS
    ax.plot([x_capteur, x_capteur], [35, h - 35], color="#f59e0b", lw=4, zorder=4)
    ax.text(x_capteur + 8, 45, "Capteur\nCMOS", color="#fde047", fontsize=8, fontweight="bold")

    # Objet réel AB
    ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2.5), zorder=4)
    ax.text(xa, y0 + 14, "A", color="#a855f7", fontsize=8, fontweight="bold", ha="center")
    ax.text(xa, y0 - h_obj - 6, "B", color="#a855f7", fontsize=8, fontweight="bold", ha="center")

    # Image réelle renversée A'B' sur le capteur
    ax.annotate("", xy=(x_capteur, y0 + h_img), xytext=(x_capteur, y0), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2.5), zorder=5)
    ax.text(x_capteur + 8, y0 - 6, "A'", color="#10b981", fontsize=8, fontweight="bold")
    ax.text(x_capteur + 8, y0 + h_img + 10, "B'", color="#10b981", fontsize=8, fontweight="bold")

    # Rayons lumineux
    ax.plot([xa, x_lentille, x_capteur], [y0 - h_obj, y0, y0 + h_img], color="#2563eb", lw=1.5)
    ax.plot([xa, x_lentille, x_capteur], [y0 - h_obj, y0 - h_obj, y0 + h_img], color="#eab308", lw=1.5)

    taille_img_mm = h_obj_m * 1000.0 * abs(gamma)
    st.session_state.apn_txt_panneau_bas = (
        f"• Focale Objectif f' = {f_mm:.0f} mm  |  Tirage optique OA' = {oa_prime_mm:.2f} mm\n"
        f"• Grandissement γ = {gamma:.4f} (Image Réelle et Renversée)\n"
        f"• Taille image sur capteur CMOS = {taille_img_mm:.1f} mm"
    )
    ax.text(20, 20, "INSTRUMENTATION : APPAREIL PHOTOGRAPHIQUE ET CAPTEUR CMOS", color="#38bdf8", fontsize=9, fontweight="bold")
    return fig


def afficher_questions_apn(verrouille=False):
    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz sur l'appareil photographique (10 questions - 10 pts)")
        if "ordre_questions_apn" not in st.session_state:
            q_base = [
                ("q1", "Quel élément optique d'un appareil photo joue le rôle de lentille convergente pour former l'image :"),
                ("q2", "Sur quel composant électronique sensible à la lumière se forme l'image nette dans un appareil numérique :"),
                ("q3", "Quelle est la nature de l'image A'B' formée sur le capteur d'un appareil photographique :"),
                ("q4", "Comment s'appelle le mécanisme à lamelles qui règle la quantité de lumière entrant dans l'objectif :"),
                ("q5", "Quelle opération consiste à déplacer légèrement l'objectif par rapport au capteur pour obtenir une image nette selon la distance du sujet :"),
                ("q6", "Lorsque l'objet photographié est situé très loin (à l'infini), où se forme son image nette :"),
                ("q7", "Comment appelle-t-on un objectif de courte focale (ex : 18 mm ou 24 mm) offrant un très large champ de vision :"),
                ("q8", "Comment appelle-t-on un objectif de longue focale (ex : 200 mm ou 300 mm) permettant de rapprocher les sujets lointains :"),
                ("q9", "Quelle grandeur règle la durée pendant laquelle la lumière frappe le capteur CMOS :"),
                ("q10", "Quelle partie de l'œil humain joue le même rôle que le capteur CMOS d'un appareil photo :"),
            ]
            random.shuffle(q_base)
            st.session_state.ordre_questions_apn = q_base

        for idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_apn, 1):
            cle_q = f"col_g_quiz_apn_{q_id}"
            cle_opts = f"opts_apn_shuf_{q_id}"
            if cle_opts not in st.session_state:
                opts_map = {
                    "q1": ["L'objectif photographique", "Le viseur optique", "Le flash"],
                    "q2": ["Le capteur CMOS (ou CCD)", "La batterie lithium", "Le diaphragme"],
                    "q3": ["Réelle, renversée et généralement plus petite que l'objet", "Virtuelle et droite", "Réelle et droite"],
                    "q4": ["Le diaphragme", "L'obturateur", "Le prisme"],
                    "q5": ["La mise au point (autofocus)", "Le zoom numérique", "La balance des blancs"],
                    "q6": ["Dans le plan focal image (sur le foyer F')", "Sur le centre optique O", "Devant l'objectif"],
                    "q7": ["Un objectif grand-angle", "Un téléobjectif", "Un microscope"],
                    "q8": ["Un téléobjectif", "Un objectif macro", "Un oculaire"],
                    "q9": ["Le temps de pose (vitesse d'obturation)", "La sensibilité ISO", "La distance focale"],
                    "q10": ["La rétine", "La cornée", "L'iris"],
                }
                copie = list(opts_map[q_id])
                random.shuffle(copie)
                st.session_state[cle_opts] = ["Choisir..."] + copie
            cq1, cq2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq1: st.write(f"**{idx}.** {q_txt}")
            with cq2: st.selectbox("", st.session_state[cle_opts], key=cle_q, disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse de cours : Appareil photo (Texte à trous - 10 items - 10 pts)")
        items_apn = [
            ("1. L'objectif d'un appareil photographique est équivalent à une lentille .........", ["Choisir...", "convergente", "divergente"], "apn_t1"),
            ("2. L'image formée sur le capteur numérique est réelle et .........", ["Choisir...", "renversée", "droite"], "apn_t2"),
            ("3. Le composant qui convertit la lumière en signal électrique est le capteur .........", ["Choisir...", "CMOS", "thermique"], "apn_t3"),
            ("4. Le réglage de la netteté selon la distance du sujet s'appelle la ......... au point.", ["Choisir...", "mise", "prise"], "apn_t4"),
            ("5. Pour un paysage à l'infini, le capteur se situe dans le plan ......... image F'.", ["Choisir...", "focal", "central"], "apn_t5"),
            ("6. Le ......... régule le flux lumineux entrant grâce à une ouverture variable.", ["Choisir...", "diaphragme", "flash"], "apn_t6"),
            ("7. Dans l'œil humain, le diaphragme correspond à l'.........", ["Choisir...", "iris", "cristallin"], "apn_t7"),
            ("8. Dans l'œil humain, le capteur correspond à la .........", ["Choisir...", "rétine", "cornée"], "apn_t8"),
            ("9. Un objectif de longue focale permettant de grossir les objets lointains est un .........", ["Choisir...", "téléobjectif", "grand-angle"], "apn_t9"),
            ("10. Le grandissement γ d'un appareil photo est de signe .........", ["Choisir...", "négatif", "positif"], "apn_t10"),
        ]
        for enonce, opts, cle in items_apn:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", opts, key=cle, disabled=verrouille, label_visibility="collapsed")





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
    st.subheader("L'histoire des appareils optiques")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Objectif de l'atelier :</p>
        <p style="margin-bottom: 0;">Découvrir comment l'homme a assemblé lentilles et miroirs pour explorer l'infiniment grand (lunettes et télescopes), l'infiniment petit (loupes et microscopes) et fixer les images (chambre noire et photographie).</p>
    </div>
    """, unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        try: st.image("camera_obscura.jpg", caption="Chambre noire d'Alhazen (XIe siècle)", use_container_width=True)
        except Exception: st.warning("Image 'camera_obscura.jpg' introuvable.")
        st.info("**La Chambre Noire (XIe siècle)**\n* Décrite par **Ibn al-Haytham (Alhazen)**.\n* Ancêtre de l'appareil photo : projette une image réelle et renversée sur un écran.")

    with col_h2:
        try: st.image("lunette_galilee.jpg", caption="Lunette de Galilée (1609) & Kepler (1611)", use_container_width=True)
        except Exception: st.warning("Image 'lunette_galilee.jpg' introuvable.")
        st.info("**Lunettes Astronomiques (1609 - 1611)**\n* **Galilée** utilise un oculaire divergent (image droite).\n* **Kepler** utilise deux lentilles convergentes pour un champ plus large.")

    with col_h3:
        try: st.image("telescope_newton.jpg", caption="Télescope de Newton (1668)", use_container_width=True)
        except Exception: st.warning("Image 'telescope_newton.jpg' introuvable.")
        st.info("**Le Télescope à Miroir (1668)**\n* **Isaac Newton** remplace la lentille objectif par un **miroir concave**.\n* Supprime les défauts de couleurs (aberrations chromatiques).")

    with col_h4:
        try: st.image("microscope_ancien.jpg", caption="Microscopes de Hooke et Leeuwenhoek", use_container_width=True)
        except Exception: st.warning("Image 'microscope_ancien.jpg' introuvable.")
        st.info("**Microscope & Photographie**\n* **Hooke** et **Leeuwenhoek** révèlent le monde cellulaire.\n* **Niépce (1827)** réalise la première photographie permanente.")

    st.markdown("---")
    if "ho_verrouille_tab1" not in st.session_state:
        st.session_state.ho_verrouille_tab1 = False
    verrou_ho = st.session_state.ho_verrouille_tab1
    afficher_atelier_hist_optique(verrouille=verrou_ho)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ho = st.checkbox("Je certifie avoir complété l'Atelier Historique des appareils optiques.", key="certif_ho1", disabled=verrou_ho)
    if st.button("VALIDER ET EXPORTER LE BILAN HISTORIQUE", key="btn_exp_ho1", use_container_width=True, disabled=verrou_ho):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_ho:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            sc_q = sum(1.0 for q in st.session_state.get("ordre_quiz_ho_aleatoire", []) if st.session_state.get(f"ho_at1_g_{q['id']}") == q["rep"])
            rep_t = {"ho_t1": "noire", "ho_t2": "Galilée", "ho_t3": "Kepler", "ho_t4": "Newton", "ho_t5": "miroir", "ho_t6": "loupe", "ho_t7": "microscope", "ho_t8": "Niépce", "ho_t9": "réelle", "ho_t10": "CMOS"}
            sc_t = sum(1.0 for k, v in rep_t.items() if st.session_state.get(k) == v)
            st.session_state.score_ho1_p1, st.session_state.score_ho1_p2, st.session_state.score_final_ho1 = sc_q, sc_t, sc_q + sc_t
            st.session_state.ho_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("ho_verrouille_tab1", False):
        scr1, scr2, tot_s = st.session_state.score_ho1_p1, st.session_state.score_ho1_p2, st.session_state.score_final_ho1
        ts_ho = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note : {tot_s:.1f} / 20")

        html_ho = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Histoire Appareils Optiques - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 1 : Histoire des Appareils Optiques</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_ho}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get("ordre_quiz_ho_aleatoire", []), 1):
            qid_c = q["id"]
            saisie_q = st.session_state.get(f"ho_at1_g_{qid_c}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_q) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_ho += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_q}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_ho += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        verif_ho = [
            ("1. Au XIe siècle, Alhazen décrit la chambre ......... qui projette une image renversée.", "noire", "ho_t1"),
            ("2. En 1609, ......... observe les astres avec une lunette munie d'un oculaire divergent.", "Galilée", "ho_t2"),
            ("3. En 1611, Johannes ......... utilise deux lentilles convergentes pour élargir le champ.", "Kepler", "ho_t3"),
            ("4. En 1668, Isaac ......... remplace la lentille objectif par un miroir concave.", "Newton", "ho_t4"),
            ("5. Un télescope utilise un ......... alors qu'une lunette utilise uniquement des lentilles.", "miroir", "ho_t5"),
            ("6. Au XVIIe siècle, Van Leeuwenhoek observe les bactéries grâce à une ......... puissante.", "loupe", "ho_t6"),
            ("7. Robert Hooke utilise un ......... composé pour découvrir les cellules végétales.", "microscope", "ho_t7"),
            ("8. En 1827, Nicéphore ......... fixe la première image photographique de l'histoire.", "Niépce", "ho_t8"),
            ("9. Dans un appareil photo, l'objectif forme une image ......... sur le capteur.", "réelle", "ho_t9"),
            ("10. Les appareils photo numériques utilisent un capteur électronique .........", "CMOS", "ho_t10"),
        ]
        for idx_t, (en, rep, cle) in enumerate(verif_ho, 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_ho += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_ho += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier Historique (.html)", data=html_ho, file_name=preparer_nom_fichier("Rapport_Histoire_Appareils_Optiques").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab2:
    st.subheader("La loupe")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 15px;">Rappel du Modèle Optique de la Loupe :</p>
        <ul style="margin-bottom: 0; line-height: 1.9;">
            <li><strong>Principe :</strong> Une loupe est une <strong>lentille convergente</strong> de courte distance focale (<i>f'</i> &gt; 0).</li>
            <li><strong>Condition d'observation :</strong> L'objet AB doit être placé entre le foyer objet <strong>F</strong> et le centre optique <strong>O</strong> (|OA| &lt; <i>f'</i>). L'image A'B' obtenue est <strong>virtuelle, droite et agrandie</strong>.</li>
            <li><strong>Grossissement commercial :</strong> Avec une distance minimale de vision distincte <i>d</i><sub>m</sub> = 25 cm = 0,25 m, il vaut <strong><i>G</i><sub>c</sub> = <span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1.1; margin: 0 3px;"><span style="display: block; border-bottom: 1px solid #1e293b; padding: 0 3px;">0,25</span><span style="display: block; padding: 0 3px;"><i>f'</i></span></span></strong> (avec <i>f'</i> en mètres).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "loupe_verrouille" not in st.session_state:
        st.session_state.loupe_verrouille = False

    col_g_loupe, col_d_loupe = st.columns([1.2, 2.2])
    with col_g_loupe:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>PARAMÈTRES DE LA LOUPE</p>", unsafe_allow_html=True)
            f_loupe = st.slider("Distance focale f' (cm) :", 4.0, 20.0, 10.0, 0.5, key="slide_loupe_f", disabled=st.session_state.loupe_verrouille)
            d_loupe = st.slider("Distance objet |OA| (cm) :", 1.0, 19.0, 6.0, 0.5, key="slide_loupe_d", disabled=st.session_state.loupe_verrouille)
            ab_loupe = st.slider("Hauteur objet AB (cm) :", 1.0, 5.0, 3.0, 0.5, key="slide_loupe_ab", disabled=st.session_state.loupe_verrouille)

        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>RAPPORT D'ANALYSE OPTIQUE</p>", unsafe_allow_html=True)
            d_eff = min(d_loupe, f_loupe - 0.5)
            oa_p = (f_loupe * (-d_eff)) / (f_loupe - d_eff)
            gam_l = oa_p / (-d_eff)
            gc_l = 25.0 / f_loupe
            st.text(f"Loupe Simple :\n• Focale f' = {f_loupe:.1f} cm\n• Vergence C = {100.0/f_loupe:.1f} δ\n• Grandissement γ = +{gam_l:.2f}\n• Grossissement Gc = {gc_l:.2f}x\n• Image : Virtuelle & Droite")

    with col_d_loupe:
        st.subheader("Banc d'optique virtuel : Formation de l'image virtuelle")
        st.pyplot(dessiner_loupe_matplotlib(), use_container_width=True)
        st.info(st.session_state.get("loupe_txt_panneau_bas", "Ajustez les curseurs pour observer l'image virtuelle."))

    st.write("---")
    afficher_questions_loupe(verrouille=st.session_state.get("loupe_verrouille", False))

    st.write("---")
    st.subheader("Validation et Génération du Bilan Officiel - La Loupe")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_loupe = st.checkbox("Je certifie avoir complété l'intégralité de l'atelier La Loupe.", key="certif_loupe_tab2", disabled=st.session_state.loupe_verrouille)
    if st.button("VALIDER ET EXPORTER LE BILAN DE LA LOUPE", key="btn_exp_loupe_tab2", use_container_width=True, disabled=st.session_state.loupe_verrouille):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_loupe:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            att_ql = {
                "q1": "Une lentille convergente de courte distance focale", "q2": "Entre le foyer objet F et le centre optique O",
                "q3": "Virtuelle (non projetable sur un écran)", "q4": "Droite et agrandie",
                "q5": "Pile dans le plan focal objet (sur le foyer F)", "q6": "Gc = 0,25 / f'",
                "q7": "25 cm (0,25 m)", "q8": "5 (soit x5)",
                "q9": "+10 dioptries (δ)", "q10": "Réelle et renversée (la lentille agit alors comme un projecteur)"
            }
            att_tl = {"loupe_t1": "convergente", "loupe_t2": "F", "loupe_t3": "virtuelle", "loupe_t4": "écran", "loupe_t5": "1", "loupe_t6": "objet F", "loupe_t7": "infini", "loupe_t8": "25", "loupe_t9": "grand", "loupe_t10": "dioptrie"}
            sc_q = sum(1.0 for k, v in att_ql.items() if st.session_state.get(f"col_g_quiz_loupe_{k}") == v)
            sc_t = sum(1.0 for k, v in att_tl.items() if st.session_state.get(k) == v)
            st.session_state.score_loupe_p1, st.session_state.score_loupe_p2, st.session_state.score_final_loupe = sc_q, sc_t, sc_q + sc_t
            st.session_state.loupe_verrouille = True
            st.rerun()

    if st.session_state.get("loupe_verrouille", False):
        scr1, scr2, tot_s = st.session_state.score_loupe_p1, st.session_state.score_loupe_p2, st.session_state.score_final_loupe
        ts_l = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER LA LOUPE SCELLÉ | Note : {tot_s:.1f} / 20")
        att_ql = {
            "q1": "Une lentille convergente de courte distance focale", "q2": "Entre le foyer objet F et le centre optique O",
            "q3": "Virtuelle (non projetable sur un écran)", "q4": "Droite et agrandie",
            "q5": "Pile dans le plan focal objet (sur le foyer F)", "q6": "Gc = 0,25 / f'",
            "q7": "25 cm (0,25 m)", "q8": "5 (soit x5)",
            "q9": "+10 dioptries (δ)", "q10": "Réelle et renversée (la lentille agit alors comme un projecteur)"
        }
        html_loupe = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport La Loupe - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier : La Loupe Simple</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_l}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, (qid, qtxt) in enumerate(st.session_state.get("ordre_questions_loupe", []), 1):
            saisie = st.session_state.get(f"col_g_quiz_loupe_{qid}", "Choisir...")
            att = att_ql[qid]
            v_lbl = "CORRECT" if str(saisie) == str(att) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_loupe += f"<tr><td>{num}</td><td>{qtxt}</td><td>{saisie}</td><td>{att}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_loupe += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        verif_tl = [
            ("1. Une loupe est constituée d'une lentille mince ......... de courte distance focale.", "convergente", "loupe_t1"),
            ("2. L'objet observé doit être placé entre le centre optique O et le foyer objet .........", "F", "loupe_t2"),
            ("3. L'image obtenue à travers la loupe est droite, agrandie et .........", "virtuelle", "loupe_t3"),
            ("4. Une image virtuelle ne peut pas être recueillie sur un .........", "écran", "loupe_t4"),
            ("5. Le grandissement transversal γ d'une loupe est toujours positif et supérieur à .........", "1", "loupe_t5"),
            ("6. Pour observer sans accommoder, l'objet est placé exactement au foyer .........", "objet F", "loupe_t6"),
            ("7. L'image finale se forme alors à l'.........", "infini", "loupe_t7"),
            ("8. La distance minimale de vision distincte standard vaut ......... cm.", "25", "loupe_t8"),
            ("9. Plus la distance focale f' est courte, plus le grossissement commercial est .........", "grand", "loupe_t9"),
            ("10. L'unité de la vergence C = 1 / f' d'une loupe est la ......... (δ).", "dioptrie", "loupe_t10"),
        ]
        for idx_t, (en, rep, cle) in enumerate(verif_tl, 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_loupe += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_loupe += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de La Loupe (.html)", data=html_loupe, file_name=preparer_nom_fichier("Rapport_La_Loupe").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab3:
    st.subheader("La lunette astronomique")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 15px;">Rappel du Modèle de la Lunette Afocale :</p>
        <ul style="margin-bottom: 0; line-height: 1.8;">
            <li><strong>Configuration afocale :</strong> La distance entre les deux lentilles est égale à la somme de leurs distances focales (<strong><i>d</i> = O<sub>1</sub>O<sub>2</sub> = <i>f'</i><sub>1</sub> + <i>f'</i><sub>2</sub></strong>).</li>
            <li><strong>Grossissement de l'instrument :</strong> Le grossissement nominal se calcule par la relation <strong><i>G</i> = <i>f'</i><sub>1</sub> / <i>f'</i><sub>2</sub></strong> (soit <span style="display: inline-block; vertical-align: middle; text-align: center; font-weight: bold; line-height: 1.1; margin-left: 4px;"><span style="display: block; border-bottom: 1px solid #1e293b; padding: 0 3px;"><i>f'</i><sub>1</sub></span><span style="display: block; padding: 0 3px;"><i>f'</i><sub>2</sub></span></span>).</li>
            <li><strong>Confort visuel :</strong> L'image finale sortant de l'oculaire est rejetée à l'infini, permettant à l'œil du marin ou de l'astronome d'observer l'astre sans aucune fatigue (pas d'accommodation).</li>
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
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_opt7: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Moteur de correction automatique du Quiz (Partie 1 : 10 Pts)
            attendus_qo7_v = {
                "q1": "Objectif (de grande distance focale)", "q2": "Oculaire", 
                "q3": "À l'infini (confort de vision sans fatigue pour l'œil)", 
                "q4": "Le foyer objet F2 de l'oculaire", "q5": "Réelle et renversée (située dans le plan focal commun)", 
                "q6": "À l'infini (pas besoin d'accommoder)", "q7": "G = f'1 / f'2", 
                "q8": "20", "q9": "Renversée (haut-bas et droite-gauche)", "q10": "L'objectif par l'oculaire"
            }
            score_quiz_opt7 = sum([1.0 for qk, qv in attendus_qo7_v.items() if st.session_state.get(f"col_g_quiz_opt7_{qk}") == qv])

            # Moteur de correction automatique du Texte à trous (Partie 2 : 10 items x 1 pt = 10 Pts)
            attendus_to7_v = {
                "t1": "Objectif", "t2": "Oculaire", "t3": "Afocal", "t4": "Grossissement", "t5": "Oculaire",
                "t6": "Renversée", "t7": "f'2", "t8": "Infini", "t9": "Oculaire", "t10": "Renversée"
            }
            score_trous_opt7 = sum([1.0 for tk, tv in attendus_to7_v.items() if st.session_state.get(f"opt7_{tk}") == tv])

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

        from datetime import timedelta, datetime
        timestamp_opt7 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 7 SCELLÉ | Note de session : {tot_s} / 20")

        attendus_qo7_v = {
            "q1": "Objectif (de grande distance focale)", "q2": "Oculaire", 
            "q3": "À l'infini (confort de vision sans fatigue pour l'œil)", 
            "q4": "Le foyer objet F2 de l'oculaire", "q5": "Réelle et renversée (située dans le plan focal commun)", 
            "q6": "À l'infini (pas besoin d'accommoder)", "q7": "G = f'1 / f'2", 
            "q8": "20", "q9": "Renversée (haut-bas et droite-gauche)", "q10": "L'objectif par l'oculaire"
        }
        attendus_to7_v = {
            "t1": "Objectif", "t2": "Oculaire", "t3": "Afocal", "t4": "Grossissement", "t5": "Oculaire",
            "t6": "Renversée", "t7": "f'2", "t8": "Infini", "t9": "Oculaire", "t10": "Renversée"
        }
        enonces_to7_v = {
            "t1": "1. La lunette astronomique est composée de deux lentilles convergentes. La première est l'.........",
            "t2": "2. de grande distance focale, et la seconde, proche de l'œil, est l'.........",
            "t3": "3. Lorsque le foyer image de la première coïncide avec le foyer objet de la seconde, le système est .........",
            "t4": "4. L'image d'un astre lointain sort alors à l'infini, permettant d'observer sans fatigue. Le .........",
            "t5": "5. de l'appareil correspond au rapport de la focale de l'objectif sur celle de l'.........",
            "t6": "6. L'image intermédiaire A1B1 formée dans le plan focal commun est réelle et .........",
            "t7": "7. La longueur totale d'une lunette afocale est égale à la somme d = f'1 + .........",
            "t8": "8. Pour observer sans accommoder, l'image finale de l'astre est rejetée à l'.........",
            "t9": "9. La zone la plus lumineuse où placer la pupille de l'œil s'appelle le cercle .........",
            "t10": "10. Par rapport à l'objet céleste observé, l'image finale vue dans cette lunette est ........."
        }

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
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_opt7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Récapitulatif des scores de compétences - Optique 7</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthèse de Cours (Texte à trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LA LUNETTE KÉPLÉRIENNE (10 PTS)</div>
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

        ordre_reel_opt7 = st.session_state.get("ordre_questions_opt7", [])
        for idx_q, (q_id, q_txt) in enumerate(ordre_reel_opt7, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt7_{q_id}", "Choisir...")
            attendu = attendus_qo7_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_q}</td><td>{q_txt}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
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

        for t_key, t_val in attendus_to7_v.items():
            saisie = st.session_state.get(f"opt7_{t_key}", "Choisir...")
            phrase_t = enonces_to7_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique géométrique généré automatiquement &bull; Professeur Laurent GALLET</div>
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

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 15px;">Rappel du Modèle de la Lunette de Galilée :</p>
        <ul style="margin-bottom: 0; line-height: 1.8;">
            <li><strong>Association Optique :</strong> Elle associe un <strong>objectif convergent</strong> (<strong><i>f'</i><sub>1</sub> &gt; 0</strong>) et un <strong>oculaire divergent</strong> (<strong><i>f'</i><sub>2</sub> &lt; 0</strong>).</li>
            <li><strong>Condition Afocale :</strong> Le foyer image de l'objectif et le foyer objet de l'oculaire sont confondus (<strong>F'<sub>1</sub> = F<sub>2</sub></strong>). La distance séparant les verres est réduite : <strong><i>d</i> = <i>f'</i><sub>1</sub> &minus; |<i>f'</i><sub>2</sub>|</strong>.</li>
            <li><strong>Propriété d'image :</strong> Contrairement au système de Kepler, la lunette de Galilée fournit une <strong>image finale droite</strong> (redressée, dans le même sens que l'objet).</li>
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
    st.subheader("Validation et Génération du Bilan Officiel - Atelier 8")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt8 = st.checkbox(
        "Je certifie avoir complété l'intégralité des questionnaires de l'Atelier 8.", 
        key="check_certif_opt8_officiel_20pts", 
        disabled=st.session_state.get("opt8_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8", key="btn_export_opt8_official_20pts", use_container_width=True, disabled=st.session_state.get("opt8_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_opt8: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction Automatique de la Partie 1 (10 Pts)
            attendus_qo8_v = {
                "q1": "L'oculaire de Galilée est une lentille divergente", "q2": "Strictement négative (f'2 < 0)", 
                "q3": "Le foyer objet F2 de l'oculaire divergent", "q4": "Droite (dans le même sens que l'astre)", 
                "q5": "f'1 + f'2 (ce qui donne une soustraction car f'2 est négatif)", "q6": "Plus courte que celle de Kepler", 
                "q7": "Positif (l'image finale est droite)", "q8": "4.0 (car f'2 est négatif)", 
                "q9": "Un champ visuel très étroit", "q10": "Les jumelles de théâtre (ou de spectacle)"
            }
            score_quiz_opt8 = sum([1.0 for qk, qv in attendus_qo8_v.items() if st.session_state.get(f"col_g_quiz_opt8_{qk}") == qv])

            # Correction Automatique de la Partie 2 (10 Pts : 10 items x 1 pt)
            attendus_to8_v = {
                "t1": "Divergente", "t2": "Objet F2", "t3": "Droite", "t4": "Positive", "t5": "Courte",
                "t6": "Positif", "t7": "Infini", "t8": "Étroit", "t9": "Théâtre", "t10": "Afocal"
            }
            score_trous_opt8 = sum([1.0 for tk, tv in attendus_to8_v.items() if st.session_state.get(f"opt8_{tk}") == tv])

            st.session_state.score_opt8_p1 = round(score_quiz_opt8, 1)
            st.session_state.score_opt8_p2 = round(score_trous_opt8, 1)
            st.session_state.score_final_opt8 = round(score_quiz_opt8 + score_trous_opt8, 1)
            st.session_state.opt8_verrouille = True
            st.rerun()

    if st.session_state.get("opt8_verrouille", False):
        scr1 = st.session_state.get("score_opt8_p1", 0.0)
        scr2 = st.session_state.get("score_opt8_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt8", 0.0)

        from datetime import timedelta, datetime
        timestamp_opt8 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 8 SCELLÉ | Note de session : {tot_s} / 20")

        attendus_qo8_v = {
            "q1": "L'oculaire de Galilée est une lentille divergente", "q2": "Strictement négative (f'2 < 0)", 
            "q3": "Le foyer objet F2 de l'oculaire divergent", "q4": "Droite (dans le même sens que l'astre)", 
            "q5": "f'1 + f'2 (ce qui donne une soustraction car f'2 est négatif)", "q6": "Plus courte que celle de Kepler", 
            "q7": "Positif (l'image finale est droite)", "q8": "4.0 (car f'2 est négatif)", 
            "q9": "Un champ visuel très étroit", "q10": "Les jumelles de théâtre (ou de spectacle)"
        }
        attendus_to8_v = {
            "t1": "Divergente", "t2": "Objet F2", "t3": "Droite", "t4": "Positive", "t5": "Courte",
            "t6": "Positif", "t7": "Infini", "t8": "Étroit", "t9": "Théâtre", "t10": "Afocal"
        }
        enonces_to8_v = {
            "t1": "1. La lunette de Galilée se distingue par l'utilisation d'un oculaire de nature .........",
            "t2": "2. Pour obtenir la configuration afocale, le foyer image de l'objectif coïncide avec le foyer .........",
            "t3": "3. L'avantage majeur de ce montage est de générer une image finale .........",
            "t4": "4. Son objectif est une lentille convergente dont la distance focale f'1 est .........",
            "t5": "5. La longueur de la lunette de Galilée (d = f'1 - |f'2|) est plus .........",
            "t6": "6. Le grossissement nominal G de la lunette de Galilée est de signe .........",
            "t7": "7. Pour observer l'astre sans fatigue oculaire, l'image finale est rejetée à l'.........",
            "t8": "8. Le principal défaut optique de la lunette de Galilée est un champ visuel très .........",
            "t9": "9. On utilise encore ce principe optique dans les jumelles de .........",
            "t10": "10. Un système optique qui transforme un faisceau parallèle en faisceau parallèle est dit ........."
        }

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
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_opt8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Récapitulatif des scores de compétences - Optique 8</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthèse de Cours (Texte à trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ LUNETTE GALILÉENNE (10 PTS)</div>
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

        ordre_reel_opt8 = st.session_state.get("ordre_questions_opt8", [])
        for idx_q, (q_id, q_txt) in enumerate(ordre_reel_opt8, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt8_{q_id}", "Choisir...")
            attendu = attendus_qo8_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>{idx_q}</td><td>{q_txt}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
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

        for t_key, t_val in attendus_to8_v.items():
            saisie = st.session_state.get(f"opt8_{t_key}", "Choisir...")
            phrase_t = enonces_to8_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
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

        for t_key, t_val in attendus_to8_v.items():
            saisie = st.session_state.get(f"opt8_{t_key}", "Choisir...")
            phrase_t = enonces_to8_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel généré automatiquement &bull; Professeur Laurent GALLET</div>
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
    st.subheader("Le microscope")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 15px;">Rappel du Modèle Optique du Microscope :</p>
        <ul style="margin-bottom: 0; line-height: 2.0;">
            <li><strong>Grandissement de l'objectif (L<sub>1</sub>) :</strong> <strong><i>&gamma;</i><sub>1</sub> = &minus; <span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1.1; margin: 0 3px;"><span style="display: block; border-bottom: 1px solid #1e293b; padding: 0 3px;">&Delta;</span><span style="display: block; padding: 0 3px;"><i>f'</i><sub>1</sub></span></span></strong> (avec <strong>&Delta;</strong> l'intervalle optique entre <strong>F'<sub>1</sub></strong> et <strong>F<sub>2</sub></strong>).</li>
            <li><strong>Grossissement de l'oculaire (L<sub>2</sub>) :</strong> <strong><i>G</i><sub>c2</sub> = <span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1.1; margin: 0 3px;"><span style="display: block; border-bottom: 1px solid #1e293b; padding: 0 3px;">0,25</span><span style="display: block; padding: 0 3px;"><i>f'</i><sub>2</sub></span></span></strong> (avec distance minimale de visée standard à <strong>25 cm</strong>).</li>
            <li><strong>Grossissement total de l'instrument :</strong> <strong><i>G</i> = <i>&gamma;</i><sub>1</sub> &middot; <i>G</i><sub>c2</sub> = &minus; <span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1.1; margin: 0 3px;"><span style="display: block; border-bottom: 1px solid #1e293b; padding: 0 3px;">&Delta; &middot; 0,25</span><span style="display: block; padding: 0 3px;"><i>f'</i><sub>1</sub> &middot; <i>f'</i><sub>2</sub></span></span></strong>.</li>
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
    st.subheader("Validation et Génération du Bilan Officiel - Atelier 9")

    case_certif_opt9 = st.checkbox(
        "Je certifie avoir complété l'intégralité des questionnaires de l'Atelier 9.", 
        key="check_certif_opt9_officiel_20pts", 
        disabled=st.session_state.get("opt9_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9", key="btn_export_opt9_official_20pts", use_container_width=True, disabled=st.session_state.get("opt9_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_opt9: 
            st.error("Cochez la case de certification.")
        else:
            # Partie 1 : Quiz (10 Pts)
            attendus_qo9_v = {
                "q1": "Objectif (de très courte distance focale)", "q2": "Intervalle optique Delta",
                "q3": "Réelle, renversée et très agrandie", "q4": "Pile dans son plan focal objet (foyer F2)",
                "q5": "À l'infini", "q6": "Négatif (car l'image intermédiaire est renversée)",
                "q7": "Le grandissement de l'objectif", "q8": "-40",
                "q9": "Renversée et fortement agrandie", "q10": "Un nombre suivi de la lettre X (ex: x40)"
            }
            score_quiz_opt9 = sum([1.0 for qk, qv in attendus_qo9_v.items() if st.session_state.get(f"col_g_quiz_opt9_{qk}") == qv])

            # Partie 2 : Texte à trous (10 Pts : 10 items x 1 pt)
            attendus_to9_v = {
                "t1": "Objectif", "t2": "Oculaire", "t3": "Intervalle optique", "t4": "Renversée", "t5": "Infini",
                "t6": "Négatif", "t7": "25 cm", "t8": "Oculaire", "t9": "Renversée", "t10": "X"
            }
            score_trous_opt9 = sum([1.0 for tk, tv in attendus_to9_v.items() if st.session_state.get(f"opt9_{tk}") == tv])

            st.session_state.score_opt9_p1 = round(score_quiz_opt9, 1)
            st.session_state.score_opt9_p2 = round(score_trous_opt9, 1)
            st.session_state.score_final_opt9 = round(score_quiz_opt9 + score_trous_opt9, 1)
            st.session_state.opt9_verrouille = True
            st.rerun()
    if st.session_state.get("opt9_verrouille", False):
        scr1 = st.session_state.get("score_opt9_p1", 0.0)
        scr2 = st.session_state.get("score_opt9_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt9", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import timedelta, datetime
        timestamp_opt9 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 9 SCELLÉ | Note de session : {tot_s} / 20")

        attendus_qo9_v = {
            "q1": "Objectif (de très courte distance focale)", "q2": "Intervalle optique Delta",
            "q3": "Réelle, renversée et très agrandie", "q4": "Pile dans son plan focal objet (foyer F2)",
            "q5": "À l'infini", "q6": "Négatif (car l'image intermédiaire est renversée)",
            "q7": "Le grandissement de l'objectif", "q8": "-40",
            "q9": "Renversée et fortement agrandie", "q10": "Un nombre suivi de la lettre X (ex: x40)"
        }
        attendus_to9_v = {
            "t1": "Objectif", "t2": "Oculaire", "t3": "Intervalle optique", "t4": "Renversée", "t5": "Infini",
            "t6": "Négatif", "t7": "25 cm", "t8": "Oculaire", "t9": "Renversée", "t10": "X"
        }
        enonces_to9_v = {
            "t1": "1. Le microscope composé utilise deux systèmes convergents. Le premier est l'.........",
            "t2": "2. De très courte focale, il génère une image intermédiaire réelle. Le second est l'.........",
            "t3": "3. Il fait office de loupe pour observer cette dernière. La distance fixe F'1F2 s'appelle l'.........",
            "t4": "4. L'image intermédiaire A1B1 formée par l'objectif est réelle et .........",
            "t5": "5. Pour que l'œil observe sans fatigue, l'image finale est rejetée à l'.........",
            "t6": "6. Le grandissement transversal de l'objectif d'un microscope est toujours .........",
            "t7": "7. La distance minimale de vision distincte standard est fixée à .........",
            "t8": "8. Le grossissement total G est le produit du grandissement de l'objectif par celui de l'.........",
            "t9": "9. Par rapport à l'objet placé sur la platine, l'image finale perçue est .........",
            "t10": "10. Le grossissement commercial d'un microscope s'écrit avec la lettre ........."
        }

        html_export_opt9 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 9 - {n_eleve}</title>
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
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_opt9}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Récapitulatif des scores de compétences - Optique 9 (Microscope)</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthèse de Cours (Texte à trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LE MICROSCOPE (10 PTS)</div>
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

        ordre_reel_opt9 = st.session_state.get("ordre_questions_opt9", [])
        for idx_q, (q_id, q_txt) in enumerate(ordre_reel_opt9, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt9_{q_id}", "Choisir...")
            attendu = attendus_qo9_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt9 += f"<tr><td>{idx_q}</td><td>{q_txt}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt9 += """
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

        for t_key, t_val in attendus_to9_v.items():
            saisie = st.session_state.get(f"opt9_{t_key}", "Choisir...")
            phrase_t = enonces_to9_v.get(t_key, t_key)
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt9 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt9 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique géométrique généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique9_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]:
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DU MICROSCOPE SUR VOTRE ORDINATEUR",
            data=html_export_opt9,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )


with tab6:
    st.subheader("L'appareil photographique")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 15px;">Rappel du Modèle Optique de l'Appareil Photographique :</p>
        <ul style="margin-bottom: 0; line-height: 1.9;">
            <li><strong>Objectif :</strong> Équivalent à une <strong>lentille mince convergente</strong> (<i>f'</i> &gt; 0).</li>
            <li><strong>Formation de l'image :</strong> L'objectif projette sur le <strong>capteur CMOS</strong> (ou la pellicule) une image <strong>réelle, renversée et réduite</strong> (grandissement <i>&gamma;</i> &lt; 0).</li>
            <li><strong>Mise au point :</strong> Lorsque l'objet se rapproche, on éloigne légèrement l'objectif du capteur (tirage <strong>OA' &gt; <i>f'</i></strong>) selon la relation de conjugaison.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "apn_verrouille" not in st.session_state:
        st.session_state.apn_verrouille = False

    col_g_apn, col_d_apn = st.columns([1.2, 2.2])
    with col_g_apn:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>PARAMÈTRES DE PRISE DE VUE</p>", unsafe_allow_html=True)
            f_apn = st.slider("Focale Objectif f' (mm) :", 24.0, 100.0, 50.0, 2.0, key="slide_apn_f", disabled=st.session_state.apn_verrouille)
            d_apn = st.slider("Distance du sujet |OA| (m) :", 0.5, 5.0, 2.0, 0.1, key="slide_apn_d", disabled=st.session_state.apn_verrouille)
            ab_apn = st.slider("Taille du sujet AB (m) :", 0.5, 2.5, 1.6, 0.1, key="slide_apn_ab", disabled=st.session_state.apn_verrouille)

        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>RAPPORT D'ANALYSE OPTIQUE</p>", unsafe_allow_html=True)
            oa_m = -d_apn * 1000.0
            oa_p_m = (f_apn * oa_m) / (f_apn + oa_m)
            gam_a = oa_p_m / oa_m
            st.text(f"Appareil Photo Numérique :\n• Focale f' = {f_apn:.0f} mm\n• Tirage OA' = {oa_p_m:.2f} mm\n• Grandissement γ = {gam_a:.4f}\n• Image : Réelle & Renversée")

    with col_d_apn:
        st.subheader("Banc d'optique virtuel : Formation de l'image sur capteur CMOS")
        st.pyplot(dessiner_appareil_photo_matplotlib(), use_container_width=True)
        st.info(st.session_state.get("apn_txt_panneau_bas", "Ajustez la focale et la distance pour observer la mise au point."))

    st.write("---")
    afficher_questions_apn(verrouille=st.session_state.get("apn_verrouille", False))

    st.write("---")
    st.subheader("Validation et Génération du Bilan Officiel - Appareil Photographique")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_apn = st.checkbox("Je certifie avoir complété l'intégralité de l'atelier Appareil Photographique.", key="certif_apn_tab6", disabled=st.session_state.apn_verrouille)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'APPAREIL PHOTO", key="btn_exp_apn_tab6", use_container_width=True, disabled=st.session_state.apn_verrouille):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_apn:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            att_qa = {
                "q1": "L'objectif photographique", "q2": "Le capteur CMOS (ou CCD)",
                "q3": "Réelle, renversée et généralement plus petite que l'objet", "q4": "Le diaphragme",
                "q5": "La mise au point (autofocus)", "q6": "Dans le plan focal image (sur le foyer F')",
                "q7": "Un objectif grand-angle", "q8": "Un téléobjectif",
                "q9": "Le temps de pose (vitesse d'obturation)", "q10": "La rétine"
            }
            att_ta = {"apn_t1": "convergente", "apn_t2": "renversée", "apn_t3": "CMOS", "apn_t4": "mise", "apn_t5": "focal", "apn_t6": "diaphragme", "apn_t7": "iris", "apn_t8": "rétine", "apn_t9": "téléobjectif", "apn_t10": "négatif"}
            sc_q = sum(1.0 for k, v in att_qa.items() if st.session_state.get(f"col_g_quiz_apn_{k}") == v)
            sc_t = sum(1.0 for k, v in att_ta.items() if st.session_state.get(k) == v)
            st.session_state.score_apn_p1, st.session_state.score_apn_p2, st.session_state.score_final_apn = sc_q, sc_t, sc_q + sc_t
            st.session_state.apn_verrouille = True
            st.rerun()

    if st.session_state.get("apn_verrouille", False):
        scr1, scr2, tot_s = st.session_state.score_apn_p1, st.session_state.score_apn_p2, st.session_state.score_final_apn
        ts_a = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER APPAREIL PHOTO SCELLÉ | Note : {tot_s:.1f} / 20")
        att_qa = {
            "q1": "L'objectif photographique", "q2": "Le capteur CMOS (ou CCD)",
            "q3": "Réelle, renversée et généralement plus petite que l'objet", "q4": "Le diaphragme",
            "q5": "La mise au point (autofocus)", "q6": "Dans le plan focal image (sur le foyer F')",
            "q7": "Un objectif grand-angle", "q8": "Un téléobjectif",
            "q9": "Le temps de pose (vitesse d'obturation)", "q10": "La rétine"
        }
        html_apn = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Appareil Photo - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier : L'Appareil Photographique</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_a}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, (qid, qtxt) in enumerate(st.session_state.get("ordre_questions_apn", []), 1):
            saisie = st.session_state.get(f"col_g_quiz_apn_{qid}", "Choisir...")
            att = att_qa[qid]
            v_lbl = "CORRECT" if str(saisie) == str(att) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_apn += f"<tr><td>{num}</td><td>{qtxt}</td><td>{saisie}</td><td>{att}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_apn += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        verif_ta = [
            ("1. L'objectif d'un appareil photographique est équivalent à une lentille .........", "convergente", "apn_t1"),
            ("2. L'image formée sur le capteur numérique est réelle et .........", "renversée", "apn_t2"),
            ("3. Le composant qui convertit la lumière en signal électrique est le capteur .........", "CMOS", "apn_t3"),
            ("4. Le réglage de la netteté selon la distance du sujet s'appelle la ......... au point.", "mise", "apn_t4"),
            ("5. Pour un paysage à l'infini, le capteur se situe dans le plan ......... image F'.", "focal", "apn_t5"),
            ("6. Le ......... régule le flux lumineux entrant grâce à une ouverture variable.", "diaphragme", "apn_t6"),
            ("7. Dans l'œil humain, le diaphragme correspond à l'.........", "iris", "apn_t7"),
            ("8. Dans l'œil humain, le capteur correspond à la .........", "rétine", "apn_t8"),
            ("9. Un objectif de longue focale permettant de grossir les objets lointains est un .........", "téléobjectif", "apn_t9"),
            ("10. Le grandissement γ d'un appareil photo est de signe .........", "négatif", "apn_t10"),
        ]
        for idx_t, (en, rep, cle) in enumerate(verif_ta, 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_apn += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_apn += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Appareil Photo (.html)", data=html_apn, file_name=preparer_nom_fichier("Rapport_Appareil_Photo").replace(".txt", ".html"), mime="text/html", use_container_width=True)
    
with tab7:
    st.subheader("Application dans le domaine de la Maintenance Industrielle")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les appareils optiques au service du diagnostic et du contrôle sans démontage :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">En maintenance industrielle, les techniciens utilisent l'<strong>endoscope à fibres optiques</strong> pour explorer l'intérieur des machines, la <strong>loupe binoculaire</strong> pour le contrôle électronique et la <strong>caméra thermique infrarouge</strong> pour détecter les échauffements électriques.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_app_maint = [
        {"titre": "Cas Maintenance N°1 : Endoscope industriel et fibres optiques", "img": "app_maint_endo.jpg", "leg": "Inspection endoscopique d'une turbine sans démontage", "exp": "**Principe :** La lumière est guidée par **réflexion totale interne** dans la fibre optique (<i>n</i><sub>1</sub> &gt; <i>n</i><sub>2</sub>), tandis qu'un objectif grand-angle forme l'image sur le micro-capteur."},
        {"titre": "Cas Maintenance N°2 : Loupe binoculaire stéréoscopique en atelier électronique", "img": "app_maint_bino.jpg", "leg": "Contrôle de soudures CMS sous loupe binoculaire", "exp": "**Principe :** Deux trajets optiques inclinés et des **prismes redresseurs** fournissent une **image droite en relief 3D** avec une grande distance de travail."},
        {"titre": "Cas Maintenance N°3 : Caméra thermique infrarouge et objectif en germanium", "img": "app_maint_thermo.jpg", "leg": "Diagnostic thermographique d'une armoire électrique", "exp": "**Principe :** L'objectif en **germanium** focalise les rayons infrarouges (8 - 14 µm) sur le capteur ; un ruban noir mat (**&epsilon; = 0,95**) est requis sur les métaux brillants."}
    ]

    if "sujet_am_tire" not in st.session_state:
        st.session_state.sujet_am_tire = None

    if st.button("TIRER AU SORT UN SUJET MAINTENANCE (APPAREILS OPTIQUES)", key="btn_tirage_am", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_am_tire]
        st.session_state.sujet_am_tire = random.choice(choix)
        st.session_state.mesures_am_log = []
        st.rerun()

    if st.session_state.sujet_am_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique de maintenance.")
    else:
        idx_am = st.session_state.sujet_am_tire
        data_am = sujets_app_maint[idx_am]
        st.success(f"Sujet attribué : **{data_am['titre']}**")
        st.markdown(data_am["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_am["img"], caption=data_am["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_am['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_app_maint.jpg", caption="La pause BD : Toujours vérifier l'émissivité sur le cuivre poli !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_app_maint.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_am_log" not in st.session_state: st.session_state.mesures_am_log = []
        if idx_am == 0:
            st.slider("Angle d'incidence dans la fibre optique (°) [Angle limite = 24°] :", 5.0, 40.0, 18.0, 1.0, key="slider_am_s0")
        elif idx_am == 1:
            st.radio("Tourelle d'objectif de la loupe binoculaire (Oculaires 10x) :", ["Objectif 1x (Grossissement total 10x)", "Objectif 2x (Grossissement total 20x)", "Objectif 4x (Grossissement total 40x)"], index=1, key="radio_am_s1", horizontal=True)
        else:
            st.radio("Cible visée par la caméra thermique :", ["Barre de cuivre poli brillant (ε = 0,12)", "Borne électrique + Ruban noir mat (ε = 0,95)"], index=1, key="radio_am_s2", horizontal=True)

        if st.button("ENREGISTRER CE CONTRÔLE MAINTENANCE", key="btn_rel_am", use_container_width=True):
            if "am_mesure_courante" in st.session_state:
                st.session_state.mesures_am_log.append(st.session_state.am_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_app_maint_matplotlib(idx_am), use_container_width=True)
        if st.session_state.mesures_am_log:
            df_am = pd.DataFrame(st.session_state.mesures_am_log, columns=["Paramètre", "Caractéristique", "Valeur", "Diagnostic"])
            st.dataframe(df_am, use_container_width=True, hide_index=True)

    st.write("---")
    if "am_verrouille_tab7" not in st.session_state: st.session_state.am_verrouille_tab7 = False
    verrou_am = st.session_state.am_verrouille_tab7
    sujet_actif_am = st.session_state.get("sujet_am_tire", None)
    afficher_atelier_app_maint(sujet_actif_am, verrouille=verrou_am)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_am = st.checkbox("Je certifie avoir complété l'atelier Maintenance (Appareils Optiques).", key="certif_am7", disabled=verrou_am)
    if st.button("VALIDER ET EXPORTER LE BILAN MAINTENANCE", key="btn_exp_am7", use_container_width=True, disabled=verrou_am):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_am is None or not case_certif_am:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_APP_MAINT[sujet_actif_am]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_am_{sujet_actif_am}", []) if st.session_state.get(f"am_at7_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_am}") == rep)
            st.session_state.score_am7_p1, st.session_state.score_am7_p2, st.session_state.score_final_am7 = sc_q, sc_t, sc_q + sc_t
            st.session_state.am_verrouille_tab7 = True
            st.rerun()

    if st.session_state.get("am_verrouille_tab7", False) and sujet_actif_am is not None:
        scr1, scr2, tot_s = st.session_state.score_am7_p1, st.session_state.score_am7_p2, st.session_state.score_final_am7
        ts_am = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER MAINTENANCE SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_APP_MAINT[sujet_actif_am]
        html_am = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Maintenance Optique - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Application Maintenance (Appareils Optiques) - {sujets_app_maint[sujet_actif_am]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_am}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_am_{sujet_actif_am}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"am_at7_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_am += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_am += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_am}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_am += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_am += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel Maintenance (.html)", data=html_am, file_name=preparer_nom_fichier("Rapport_Maintenance_Appareils_Optiques").replace(".txt", ".html"), mime="text/html", use_container_width=True)



with tab8:
    st.subheader("Application dans le domaine des Travaux Publics")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les appareils optiques sur les chantiers de génie civil et d'assainissement :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans les Travaux Publics, le <strong>niveau optique à prisme redresseur</strong> contrôle les altitudes de terrassement, la <strong>caméra robotisée ITV grand-angle</strong> inspecte les collecteurs enterrés et les <strong>jumelles à prismes</strong> permettent l'observation des ouvrages d'art.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_app_tp = [
        {"titre": "Chantier N°1 : Niveau optique de chantier et lecture stadimétrique sur mire", "img": "app_tp_niveau.jpg", "leg": "Lunette de nivellement à compensateur automatique et mire parlante", "exp": "**Principe :** Un **prisme redresseur** donne une image droite de la mire, tandis que les fils stadimétriques donnent la distance par **D = 100 &times; &Delta;H**."},
        {"titre": "Chantier N°2 : Caméra robotisée d'inspection télévisée des canalisations (ITV)", "img": "app_tp_itv.jpg", "leg": "Chariot caméra grand-angle à éclairage LED dans un collecteur", "exp": "**Principe :** Un objectif **grand-angle** étanche projette l'image de la paroi sur un **capteur CMOS**, avec deux points laser calibrés pour mesurer les fissures."},
        {"titre": "Chantier N°3 : Jumelles à prismes et pupille de sortie sur ouvrages d'art", "img": "app_tp_jumelles.jpg", "leg": "Contrôle visuel à distance d'un tablier de pont aux jumelles 10×42", "exp": "**Principe :** Des **prismes à réflexion totale** replient le faisceau lumineux et redressent l'image ; la **pupille de sortie** vaut **D<sub>objectif</sub> / Grossissement**."}
    ]

    if "sujet_atp_tire" not in st.session_state:
        st.session_state.sujet_atp_tire = None

    if st.button("TIRER AU SORT UN CHANTIER TP (APPAREILS OPTIQUES)", key="btn_tirage_atp", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_atp_tire]
        st.session_state.sujet_atp_tire = random.choice(choix)
        st.session_state.mesures_atp_log = []
        st.rerun()

    if st.session_state.sujet_atp_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un chantier de Travaux Publics.")
    else:
        idx_atp = st.session_state.sujet_atp_tire
        data_atp = sujets_app_tp[idx_atp]
        st.success(f"Chantier attribué : **{data_atp['titre']}**")
        st.markdown(data_atp["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_atp["img"], caption=data_atp["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_atp['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_app_tp.jpg", caption="La pause BD : D = 100 × ΔH, le calcul mental du chef de chantier !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_app_tp.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_atp_log" not in st.session_state: st.session_state.mesures_atp_log = []
        if idx_atp == 0:
            st.slider("Distance entre le niveau optique et la mire parlante (m) :", 10.0, 80.0, 35.0, 5.0, key="slider_atp_s0")
        elif idx_atp == 1:
            st.radio("Choix de l'objectif sur le chariot caméra ITV :", ["Grand-angle 3,6 mm (Vision 360° paroi)", "Focale standard 16 mm (Vision frontale étroite)"], key="radio_atp_s1", horizontal=True)
        else:
            st.radio("Modèle de jumelles utilisé sur le chantier :", ["Jumelles 8 × 32 (Compactes)", "Jumelles 10 × 42 (Chantier jour)", "Jumelles 12 × 50 (Crépuscule / Ouvrages)"], index=1, key="radio_atp_s2", horizontal=True)

        if st.button("ENREGISTRER CE RELEVÉ TP", key="btn_rel_atp", use_container_width=True):
            if "atp_mesure_courante" in st.session_state:
                st.session_state.mesures_atp_log.append(st.session_state.atp_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_app_tp_matplotlib(idx_atp), use_container_width=True)
        if st.session_state.mesures_atp_log:
            df_atp = pd.DataFrame(st.session_state.mesures_atp_log, columns=["Lecture 1", "Lecture 2", "Paramètre optique", "Résultat"])
            st.dataframe(df_atp, use_container_width=True, hide_index=True)

    st.write("---")
    if "atp_verrouille_tab8" not in st.session_state: st.session_state.atp_verrouille_tab8 = False
    verrou_atp = st.session_state.atp_verrouille_tab8
    sujet_actif_atp = st.session_state.get("sujet_atp_tire", None)
    afficher_atelier_app_tp(sujet_actif_atp, verrouille=verrou_atp)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_atp = st.checkbox("Je certifie avoir complété l'atelier Travaux Publics (Appareils Optiques).", key="certif_atp8", disabled=verrou_atp)
    if st.button("VALIDER ET EXPORTER LE BILAN TRAVAUX PUBLICS", key="btn_exp_atp8", use_container_width=True, disabled=verrou_atp):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_atp is None or not case_certif_atp:
            st.error("Action refusée : Tirez au sort un chantier et cochez la case de certification.")
        else:
            bq = BANQUES_APP_TP[sujet_actif_atp]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_atp_{sujet_actif_atp}", []) if st.session_state.get(f"atp_at8_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_atp}") == rep)
            st.session_state.score_atp8_p1, st.session_state.score_atp8_p2, st.session_state.score_final_atp8 = sc_q, sc_t, sc_q + sc_t
            st.session_state.atp_verrouille_tab8 = True
            st.rerun()

    if st.session_state.get("atp_verrouille_tab8", False) and sujet_actif_atp is not None:
        scr1, scr2, tot_s = st.session_state.score_atp8_p1, st.session_state.score_atp8_p2, st.session_state.score_final_atp8
        ts_atp = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER TRAVAUX PUBLICS SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_APP_TP[sujet_actif_atp]
        html_atp = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport TP Appareils Optiques - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Application Travaux Publics (Appareils Optiques) - {sujets_app_tp[sujet_actif_atp]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_atp}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_atp_{sujet_actif_atp}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"atp_at8_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_atp += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_atp += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_atp}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_atp += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_atp += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel Travaux Publics (.html)", data=html_atp, file_name=preparer_nom_fichier("Rapport_TP_Appareils_Optiques").replace(".txt", ".html"), mime="text/html", use_container_width=True)

with tab9:
    st.subheader("Application dans le domaine du Transport Routier")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les appareils optiques embarqués sur les véhicules industriels et routiers :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans le transport routier, les <strong>miroirs convexes et caméras CMS</strong> suppriment les angles morts, la <strong>caméra pare-brise ADAS calibrée</strong> pilote le freinage d'urgence et les <strong>projecteurs lenticulaires</strong> assurent un éclairage sans éblouissement.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_app_trans = [
        {"titre": "Cas Transport N°1 : Miroirs convexes grand-angle et caméras de rétrovision CMS", "img": "app_trans_retro.jpg", "leg": "Caméra de rétrovision CMS et rétroviseur grand-angle sur poids lourd", "exp": "**Principe :** Un **miroir convexe** donne une image **virtuelle, droite et réduite** qui élargit le champ de vision et élimine les angles morts."},
        {"titre": "Cas Transport N°2 : Caméra pare-brise ADAS et calibrage géométrique", "img": "app_trans_adas.jpg", "leg": "Cible de calibrage statique devant la caméra pare-brise d'un camion", "exp": "**Principe :** L'objectif à focale fixe projette la route sur un **capteur CMOS** ; un **calibrage précis** est indispensable après tout remplacement de pare-brise."},
        {"titre": "Cas Transport N°3 : Projecteurs lenticulaires Bi-LED et contrôle au régloscope", "img": "app_trans_phare.jpg", "leg": "Optique lenticulaire convergente avec volet de coupure", "exp": "**Principe :** Une **lentille convergente** projette une image réelle et renversée du volet métallique pour créer une **coupure nette** anti-éblouissement."}
    ]

    if "sujet_atr_tire" not in st.session_state:
        st.session_state.sujet_atr_tire = None

    if st.button("TIRER AU SORT UN SUJET TRANSPORT (APPAREILS OPTIQUES)", key="btn_tirage_atr", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_atr_tire]
        st.session_state.sujet_atr_tire = random.choice(choix)
        st.session_state.mesures_atr_log = []
        st.rerun()

    if st.session_state.sujet_atr_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique du Transport Routier.")
    else:
        idx_atr = st.session_state.sujet_atr_tire
        data_atr = sujets_app_trans[idx_atr]
        st.success(f"Étude attribuée : **{data_atr['titre']}**")
        st.markdown(data_atr["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_atr["img"], caption=data_atr["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_atr['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_app_trans.jpg", caption="La pause BD : Grâce au miroir convexe, plus aucun cycliste dans l'angle mort !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_app_trans.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_atr_log" not in st.session_state: st.session_state.mesures_atr_log = []
        if idx_atr == 0:
            st.radio("Type d'équipement optique de rétrovision :", ["Miroir Plan Classique (Champ 18°)", "Miroir Convexe Grand-Angle (Champ 45°)"], index=1, key="radio_atr_s0", horizontal=True)
        elif idx_atr == 1:
            st.slider("Défaut d'alignement angulaire de la caméra ADAS après pose pare-brise (°) :", -2.0, 2.0, 0.0, 0.1, key="slider_atr_s1")
        else:
            st.radio("Position du volet interne dans le projecteur lenticulaire :", ["Feux de croisement (Volet de coupure abaissé)", "Feux de route (Volet escamoté)"], key="radio_atr_s2", horizontal=True)

        if st.button("ENREGISTRER CE CONTRÔLE TRANSPORT", key="btn_rel_atr", use_container_width=True):
            if "atr_mesure_courante" in st.session_state:
                st.session_state.mesures_atr_log.append(st.session_state.atr_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_app_trans_matplotlib(idx_atr), use_container_width=True)
        if st.session_state.mesures_atr_log:
            df_atr = pd.DataFrame(st.session_state.mesures_atr_log, columns=["Équipement", "Paramètre", "Mesure", "Diagnostic"])
            st.dataframe(df_atr, use_container_width=True, hide_index=True)

    st.write("---")
    if "atr_verrouille_tab9" not in st.session_state: st.session_state.atr_verrouille_tab9 = False
    verrou_atr = st.session_state.atr_verrouille_tab9
    sujet_actif_atr = st.session_state.get("sujet_atr_tire", None)
    afficher_atelier_app_trans(sujet_actif_atr, verrouille=verrou_atr)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_atr = st.checkbox("Je certifie avoir complété l'atelier Transport Routier (Appareils Optiques).", key="certif_atr9", disabled=verrou_atr)
    if st.button("VALIDER ET EXPORTER LE BILAN TRANSPORT ROUTIER", key="btn_exp_atr9", use_container_width=True, disabled=verrou_atr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_atr is None or not case_certif_atr:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_APP_TRANS[sujet_actif_atr]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_atr_{sujet_actif_atr}", []) if st.session_state.get(f"atr_at9_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_atr}") == rep)
            st.session_state.score_atr9_p1, st.session_state.score_atr9_p2, st.session_state.score_final_atr9 = sc_q, sc_t, sc_q + sc_t
            st.session_state.atr_verrouille_tab9 = True
            st.rerun()

    if st.session_state.get("atr_verrouille_tab9", False) and sujet_actif_atr is not None:
        scr1, scr2, tot_s = st.session_state.score_atr9_p1, st.session_state.score_atr9_p2, st.session_state.score_final_atr9
        ts_atr = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER TRANSPORT ROUTIER SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_APP_TRANS[sujet_actif_atr]
        html_atr = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Transport Appareils Optiques - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Application Transport Routier (Appareils Optiques) - {sujets_app_trans[sujet_actif_atr]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_atr}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_atr_{sujet_actif_atr}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"atr_at9_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_atr += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_atr += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_atr}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_atr += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_atr += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel Transport Routier (.html)", data=html_atr, file_name=preparer_nom_fichier("Rapport_Transport_Appareils_Optiques").replace(".txt", ".html"), mime="text/html", use_container_width=True)



with tab10:
    st.subheader("Application dans le domaine du Géomètre Topographe")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les instruments optiques de haute précision du géomètre topographe :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Au cœur du métier de géomètre se trouvent la <strong>lunette 30× de station totale à prisme redresseur</strong>, l'<strong>objectif métrique calibré des drones de photogrammétrie</strong> et le <strong>miroir rotatif coaxial des scanners laser 3D</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_app_geo = [
        {"titre": "Mission N°1 : Lunette de station totale (30×), réticule et erreur de parallaxe", "img": "app_geo_station.jpg", "leg": "Visée de précision à la station totale avec réticule éclairé", "exp": "**Principe :** La lunette afocale **30×** intègre un **prisme redresseur** et une lentille interne de mise au point supprimant toute **erreur de parallaxe**."},
        {"titre": "Mission N°2 : Photogrammétrie par drone et résolution au sol (GSD)", "img": "app_geo_drone.jpg", "leg": "Levé photogrammétrique aérien et calcul de la résolution GSD", "exp": "**Principe :** L'objectif calibré projette le terrain sur le capteur CMOS ; la taille d'un pixel au sol vaut **GSD = (H &times; p) / <i>f'</i>**."},
        {"titre": "Mission N°3 : Scanner laser 3D terrestre, miroir rotatif et divergence du spot", "img": "app_geo_scanner.jpg", "leg": "Numérisation laser 3D d'une façade par miroir polygonal tournant", "exp": "**Principe :** Un **miroir tournant** dévie le faisceau laser coaxialement à la lentille de réception ; plus la cible est loin, plus le **spot laser** s'élargit."}
    ]

    if "sujet_ag_tire" not in st.session_state:
        st.session_state.sujet_ag_tire = None

    if st.button("TIRER AU SORT UNE MISSION GÉOMÈTRE (APPAREILS OPTIQUES)", key="btn_tirage_ag", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_ag_tire]
        st.session_state.sujet_ag_tire = random.choice(choix)
        st.session_state.mesures_ag_log = []
        st.rerun()

    if st.session_state.sujet_ag_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort une mission de Géomètre Topographe.")
    else:
        idx_ag = st.session_state.sujet_ag_tire
        data_ag = sujets_app_geo[idx_ag]
        st.success(f"Mission attribuée : **{data_ag['titre']}**")
        st.markdown(data_ag["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_ag["img"], caption=data_ag["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_ag['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_app_geo.jpg", caption="La pause BD : Toujours éliminer la parallaxe avant d'enregistrer l'angle !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_app_geo.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_ag_log" not in st.session_state: st.session_state.mesures_ag_log = []
        if idx_ag == 0:
            st.checkbox("Simuler un défaut de mise au point (présence d'erreur de parallaxe)", key="check_ag_s0")
        elif idx_ag == 1:
            c_d1, c_d2 = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_d1: st.slider("Altitude de vol du drone H (m) :", 30.0, 150.0, 80.0, 5.0, key="slider_ag_s1")
            with c_d2: st.radio("Focale objectif f' (mm) :", [16.0, 20.0, 35.0], index=1, key="radio_ag_s1", horizontal=True)
        else:
            st.slider("Distance entre le scanner 3D et la façade (m) :", 10.0, 150.0, 50.0, 5.0, key="slider_ag_s2")

        if st.button("ENREGISTRER CE POINT TOPOGRAPHIQUE", key="btn_rel_ag", use_container_width=True):
            if "ag_mesure_courante" in st.session_state:
                st.session_state.mesures_ag_log.append(st.session_state.ag_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_app_geo_matplotlib(idx_ag), use_container_width=True)
        if st.session_state.mesures_ag_log:
            df_ag = pd.DataFrame(st.session_state.mesures_ag_log, columns=["Paramètre", "Configuration", "Calcul optique", "Diagnostic"])
            st.dataframe(df_ag, use_container_width=True, hide_index=True)

    st.write("---")
    if "ag_verrouille_tab10" not in st.session_state: st.session_state.ag_verrouille_tab10 = False
    verrou_ag = st.session_state.ag_verrouille_tab10
    sujet_actif_ag = st.session_state.get("sujet_ag_tire", None)
    afficher_atelier_app_geo(sujet_actif_ag, verrouille=verrou_ag)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ag = st.checkbox("Je certifie avoir complété l'atelier Géomètre Topographe (Appareils Optiques).", key="certif_ag10", disabled=verrou_ag)
    if st.button("VALIDER ET EXPORTER LE BILAN GÉOMÈTRE TOPOGRAPHE", key="btn_exp_ag10", use_container_width=True, disabled=verrou_ag):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_ag is None or not case_certif_ag:
            st.error("Action refusée : Tirez au sort une mission et cochez la case de certification.")
        else:
            bq = BANQUES_APP_GEO[sujet_actif_ag]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_ag_{sujet_actif_ag}", []) if st.session_state.get(f"ag_at10_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_ag}") == rep)
            st.session_state.score_ag10_p1, st.session_state.score_ag10_p2, st.session_state.score_final_ag10 = sc_q, sc_t, sc_q + sc_t
            st.session_state.ag_verrouille_tab10 = True
            st.rerun()

    if st.session_state.get("ag_verrouille_tab10", False) and sujet_actif_ag is not None:
        scr1, scr2, tot_s = st.session_state.score_ag10_p1, st.session_state.score_ag10_p2, st.session_state.score_final_ag10
        ts_ag = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER GÉOMÈTRE TOPOGRAPHE SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_APP_GEO[sujet_actif_ag]
        html_ag = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Géomètre Appareils Optiques - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Application Géomètre Topographe (Appareils Optiques) - {sujets_app_geo[sujet_actif_ag]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_ag}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_ag_{sujet_actif_ag}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"ag_at10_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_ag += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_ag += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_ag}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_ag += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_ag += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel Géomètre Topographe (.html)", data=html_ag, file_name=preparer_nom_fichier("Rapport_Geometre_Appareils_Optiques").replace(".txt", ".html"), mime="text/html", use_container_width=True)






