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

BANQUES_DIV_MAINT = {
    0: {
        "questions": [
            {"id": "qdm0_1", "q": "Quel dispositif optique associe une lentille divergente et une lentille convergente pour augmenter le diamètre d'un faisceau laser de découpe ou de mesure ?", "options": ["Un élargisseur de faisceau (beam expander de Galilée)", "Un prisme dispersif", "Un miroir plan"], "rep": "Un élargisseur de faisceau (beam expander de Galilée)"},
            {"id": "qdm0_2", "q": "Pourquoi place-t-on une lentille divergente en entrée d'un élargisseur de faisceau laser industriel ?", "options": ["Pour faire diverger le faisceau fin avant qu'il ne soit rendu parallèle par la lentille convergente de sortie", "Pour bloquer 90 % de la puissance du laser", "Pour changer la couleur du laser"], "rep": "Pour faire diverger le faisceau fin avant qu'il ne soit rendu parallèle par la lentille convergente de sortie"},
            {"id": "qdm0_3", "q": "Comment sont disposés les foyers de la lentille divergente (f'1 < 0) et de la lentille convergente (f'2 > 0) dans un élargisseur afocal ?", "options": ["Leurs foyers images F'1 et objet F2 sont confondus (distance d = f'1 + f'2)", "Les deux lentilles sont collées l'une contre l'autre", "Elles sont séparées de 10 mètres"], "rep": "Leurs foyers images F'1 et objet F2 sont confondus (distance d = f'1 + f'2)"},
            {"id": "qdm0_4", "q": "Comment calcule-t-on le facteur d'élargissement G du diamètre du faisceau laser ?", "options": ["G = |f'2 / f'1|", "G = f'1 + f'2", "G = f'1 × f'2"], "rep": "G = |f'2 / f'1|"},
            {"id": "qdm0_5", "q": "Quel est l'intérêt en maintenance laser d'élargir un faisceau avant de l'envoyer sur une longue distance dans la machine ?", "options": ["Réduire la divergence naturelle du faisceau et diminuer la densité de puissance sur les miroirs de renvoi", "Rendre le laser visible dans le noir", "Refroidir le tube laser"], "rep": "Réduire la divergence naturelle du faisceau et diminuer la densité de puissance sur les miroirs de renvoi"},
            {"id": "qdm0_6", "q": "Si la lentille divergente a une focale f'1 = -25 mm et la convergente f'2 = +100 mm, quelle distance d sépare les deux lentilles ?", "options": ["75 mm (car d = -25 + 100 = 75 mm)", "125 mm", "25 mm"], "rep": "75 mm (car d = -25 + 100 = 75 mm)"},
            {"id": "qdm0_7", "q": "Avec f'1 = -25 mm et f'2 = +100 mm, par combien le diamètre du faisceau laser est-il multiplié ?", "options": ["Par 4 (G = 100 / 25 = 4×)", "Par 25", "Par 125"], "rep": "Par 4 (G = 100 / 25 = 4×)"},
            {"id": "qdm0_8", "q": "Pourquoi préfère-t-on un montage de Galilée (divergente + convergente) à un montage de Kepler (deux convergentes) pour les lasers haute puissance ?", "options": ["Parce qu'il n'y a pas de point de focalisation interne où l'air pourrait s'ioniser (claquage plasma)", "Parce que les lentilles divergentes sont incassables", "Parce qu'il ne nécessite aucun réglage"], "rep": "Parce qu'il n'y a pas de point de focalisation interne où l'air pourrait s'ioniser (claquage plasma)"},
            {"id": "qdm0_9", "q": "Que se passe-t-il en sortie si le technicien dérègle la distance d entre les deux lentilles de l'élargisseur ?", "options": ["Le faisceau de sortie n'est plus parallèle (il converge ou diverge)", "La longueur d'onde du laser change", "Le laser s'éteint"], "rep": "Le faisceau de sortie n'est plus parallèle (il converge ou diverge)"},
            {"id": "qdm0_10", "q": "Quelle précaution d'entretien prolonge la durée de vie de la lentille divergente d'entrée soumise à une forte densité d'énergie ?", "options": ["Maintenir sa surface parfaitement propre sans poussière ni trace de doigt avant chaque remise en service", "Appliquer de la graisse silicone sur la lentille", "La nettoyer avec un solvant abrasif"], "rep": "Maintenir sa surface parfaitement propre sans poussière ni trace de doigt avant chaque remise en service"},
        ],
        "trous": [
            ("1. Un élargisseur de Galilée associe une lentille ......... en entrée et une convergente en sortie.", ["Choisir...", "divergente", "plane"], "divergente", "dm_t1"),
            ("2. La lentille divergente possède une distance focale f'1 .........", ["Choisir...", "négative", "positive"], "négative", "dm_t2"),
            ("3. Dans un système afocal, un faisceau entrant parallèle ressort .........", ["Choisir...", "parallèle", "focalisé"], "parallèle", "dm_t3"),
            ("4. Le facteur d'élargissement du diamètre vaut G = |f'2 / .........|.", ["Choisir...", "f'1", "2"], "f'1", "dm_t4"),
            ("5. Élargir le faisceau réduit la ......... thermique sur les miroirs de renvoi.", ["Choisir...", "charge", "vitesse"], "charge", "dm_t5"),
            ("6. La distance entre les deux lentilles vérifie d = f'1 + .........", ["Choisir...", "f'2", "100"], "f'2", "dm_t6"),
            ("7. Ce montage évite tout point de ......... interne dans l'air.", ["Choisir...", "focalisation", "réflexion"], "focalisation", "dm_t7"),
            ("8. Si f'1 = -25 mm et f'2 = +100 mm, le diamètre est multiplié par .........", ["Choisir...", "4", "100"], "4", "dm_t8"),
            ("9. Si l'écartement d est déréglé, le faisceau de sortie n'est plus .........", ["Choisir...", "parallèle", "visible"], "parallèle", "dm_t9"),
            ("10. Une poussière sur la lentille d'entrée risque de la faire ......... sous l'effet du laser.", ["Choisir...", "fissurer", "fondre doucement"], "fissurer", "dm_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qdm1_1", "q": "Quel dispositif optique équipé d'une lentille divergente permet d'observer l'intérieur d'une enceinte machine fermée avec un très large champ de vision ?", "options": ["Un judas optique grand-angle (œilleton de porte de sécurité)", "Un microscope électronique", "Une loupe d'horloger"], "rep": "Un judas optique grand-angle (œilleton de porte de sécurité)"},
            {"id": "qdm1_2", "q": "Quel est le rôle de la lentille divergente placée du côté extérieur (côté zone dangereuse/machine) du judas optique ?", "options": ["Capturer un angle de vue très large (jusqu'à 160°-180°) et former une image virtuelle réduite", "Grossir 100 fois un boulon", "Bloquer la lumière blanche"], "rep": "Capturer un angle de vue très large (jusqu'à 160°-180°) et former une image virtuelle réduite"},
            {"id": "qdm1_3", "q": "De quelle nature est l'image observée par le technicien de maintenance à travers un judas grand-angle ?", "options": ["Virtuelle, droite (à l'endroit) et fortement rétrécie", "Réelle et renversée", "Plus grande que la machine"], "rep": "Virtuelle, droite (à l'endroit) et fortement rétrécie"},
            {"id": "qdm1_4", "q": "Pourquoi ne peut-on pas voir depuis l'intérieur de la machine ce qui se passe à l'extérieur à travers un judas optique ?", "options": ["La combinaison optique asymétrique (divergente en entrée, convergente en oculaire) rend l'image minuscule et floue en sens inverse", "Le verre est un miroir sans tain", "Un clapet ferme le trou"], "rep": "La combinaison optique asymétrique (divergente en entrée, convergente en oculaire) rend l'image minuscule et floue en sens inverse"},
            {"id": "qdm1_5", "q": "Quel avantage sécuritaire apporte un judas optique grand-angle sur le carter d'un centre d'usinage CNC ?", "options": ["Vérifier visuellement la présence d'un opérateur ou d'un outil sans ouvrir la porte ni couper le cycle", "Mesurer la vitesse de rotation de la broche", "Éclairer l'atelier"], "rep": "Vérifier visuellement la présence d'un opérateur ou d'un outil sans ouvrir la porte ni couper le cycle"},
            {"id": "qdm1_6", "q": "Quel est le signe du grandissement γ d'un judas grand-angle composé d'une lentille divergente ?", "options": ["Positif et très inférieur à 1 (0 < γ << 1)", "Négatif (-5)", "Supérieur à +10"], "rep": "Positif et très inférieur à 1 (0 < γ << 1)"},
            {"id": "qdm1_7", "q": "Dans la simulation du judas optique, comment évolue l'angle du champ de vision lorsque la vergence C devient plus négative (ex : -20 δ au lieu de -5 δ) ?", "options": ["L'angle du champ de vision s'élargit considérablement", "L'angle se rétrécit", "L'image se retourne à l'envers"], "rep": "L'angle du champ de vision s'élargit considérablement"},
            {"id": "qdm1_8", "q": "Quel matériau transparent résistant aux impacts de copeaux protège la lentille divergente d'un judas industriel ?", "options": ["Un hublot en polycarbonate haute résistance", "Une feuille de papier calque", "Du verre fin non trempé"], "rep": "Un hublot en polycarbonate haute résistance"},
            {"id": "qdm1_9", "q": "Quel symptôme indique qu'un judas optique de cellule robotisée doit être remplacé lors d'une visite préventive ?", "options": ["Des micro-rayures ou un voile opaque dû aux projections de liquide de coupe réduisant la visibilité", "Un changement de distance focale", "Une consommation électrique excessive"], "rep": "Des micro-rayures ou un voile opaque dû aux projections de liquide de coupe réduisant la visibilité"},
            {"id": "qdm1_10", "q": "Quelle loi optique permet de tracer la déviation vers l'extérieur des rayons incidents à travers la lentille divergente du judas ?", "options": ["La loi de réfraction de Snell-Descartes", "La loi d'Ohm", "La loi de Joule"], "rep": "La loi de réfraction de Snell-Descartes"},
        ],
        "trous": [
            ("1. Un judas de sécurité machine utilise une lentille ......... grand-angle.", ["Choisir...", "divergente", "convergente"], "divergente", "dm_t1"),
            ("2. Cette lentille permet d'obtenir un très large ......... de vision (jusqu'à 180°).", ["Choisir...", "champ", "rayon"], "champ", "dm_t2"),
            ("3. L'image observée par le technicien est droite, rétrécie et .........", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "dm_t3"),
            ("3. L'image observée par le technicien est droite, rétrécie et .........", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "dm_t3"),
            ("4. Comme l'image est plus petite que la zone observée, 0 < γ < .........", ["Choisir...", "1", "10"], "1", "dm_t4"),
            ("5. Plus la vergence C est ........., plus l'angle de vue est large.", ["Choisir...", "négative", "positive"], "négative", "dm_t5"),
            ("6. Le judas permet d'inspecter l'enceinte sans ouvrir la ......... de sécurité.", ["Choisir...", "porte", "vanne"], "porte", "dm_t6"),
            ("7. Un écran en ......... protège l'optique contre les projections de copeaux.", ["Choisir...", "polycarbonate", "carton"], "polycarbonate", "dm_t7"),
            ("8. Les rayons lumineux s'écartent de l'axe ......... en traversant la lentille.", ["Choisir...", "optique", "vertical"], "optique", "dm_t8"),
            ("9. Les projections d'huile de coupe rendent la vision .........", ["Choisir...", "floue", "zoomée"], "floue", "dm_t9"),
            ("10. Le calcul de position image applique la formule de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "dm_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qdm2_1", "q": "Dans un appareil photo d'inspection de maintenance ou un viseur optique, comment augmente-t-on la distance focale f' d'un téléobjectif sans rallonger le boîtier ?", "options": ["En plaçant un groupe de lentilles divergentes (téléconvertisseur) derrière l'objectif convergent", "En retirant toutes les lentilles", "En ajoutant un miroir plan"], "rep": "En plaçant un groupe de lentilles divergentes (téléconvertisseur) derrière l'objectif convergent"},
            {"id": "qdm2_2", "q": "Quel est l'effet d'une lentille divergente placée sur le trajet d'un faisceau convergent ?", "options": ["Elle réduit l'angle de convergence et repousse le point de focalisation plus loin en arrière", "Elle rapproche le foyer image F' de la lentille", "Elle bloque totalement la lumière"], "rep": "Elle réduit l'angle de convergence et repousse le point de focalisation plus loin en arrière"},
            {"id": "qdm2_3", "q": "En augmentant la distance focale équivalente du système optique, comment évolue le grandissement des détails d'une pièce éloignée ?", "options": ["Le grandissement augmente (effet zoom / téléobjectif)", "Le grandissement diminue", "L'image devient inversée gauche-droite"], "rep": "Le grandissement augmente (effet zoom / téléobjectif)"},
            {"id": "qdm2_4", "q": "Dans un objectif grand-angle de caméra d'inspection de cuves (montage rétrofocus), où est placée la lentille divergente ?", "options": ["À l'avant de l'objectif, face à la zone à inspecter", "Derrière le capteur CMOS", "Sur le trépied"], "rep": "À l'avant de l'objectif, face à la zone à inspecter"},
            {"id": "qdm2_5", "q": "Pourquoi les lentilles divergentes en verre flint sont-elles indispensables dans tous les objectifs d'inspection de précision ?", "options": ["Pour corriger les aberrations chromatiques et la courbure de champ des lentilles convergentes", "Pour alourdir la caméra", "Pour filtrer les ondes radio"], "rep": "Pour corriger les aberrations chromatiques et la courbure de champ des lentilles convergentes"},
            {"id": "qdm2_6", "q": "Si l'on accole une lentille convergente de vergence C1 = +10 δ et une lentille divergente de vergence C2 = -4 δ, quelle est la vergence totale C ?", "options": ["+ 6 dioptries (car C = C1 + C2 = 10 - 4)", "+ 14 dioptries", "- 40 dioptries"], "rep": "+ 6 dioptries (car C = C1 + C2 = 10 - 4)"},
            {"id": "qdm2_7", "q": "Que se passe-t-il si l'on accole deux lentilles de vergences opposées exactes (C1 = +8 δ et C2 = -8 δ) ?", "options": ["La vergence totale est nulle (C = 0 δ) : l'ensemble se comporte comme une lame à faces parallèles", "La distance focale vaut 16 cm", "Le faisceau est réfléchi"], "rep": "La vergence totale est nulle (C = 0 δ) : l'ensemble se comporte comme une lame à faces parallèles"},
            {"id": "qdm2_8", "q": "Quel contrôle optique réalise-t-on en maintenance sur un banc de collimation pour vérifier la vergence d'une lentille divergente ?", "options": ["La focométrie par association avec une lentille convergente connue (méthode de Badal)", "La pesée sur balance de précision", "La mesure au pied à coulisse uniquement"], "rep": "La focométrie par association avec une lentille convergente connue (méthode de Badal)"},
            {"id": "qdm2_9", "q": "Quelle est la conséquence d'un choc mécanique qui décentre la lentille divergente interne d'un objectif de contrôle ?", "options": ["Une perte de netteté asymétrique sur un côté de l'image (décentrement optique)", "Une hausse de la luminosité", "Une augmentation de la batterie"], "rep": "Une perte de netteté asymétrique sur un côté de l'image (décentrement optique)"},
            {"id": "qdm2_10", "q": "Quelle relation mathématique donne la vergence équivalente de deux lentilles minces accolées ?", "options": ["C = C1 + C2", "C = C1 × C2", "C = C1 / C2"], "rep": "C = C1 + C2"},
        ],
        "trous": [
            ("1. Un téléconvertisseur utilise une lentille ......... pour allonger la focale.", ["Choisir...", "divergente", "plane"], "divergente", "dm_t1"),
            ("2. La lentille divergente repousse le foyer image plus ......... en arrière.", ["Choisir...", "loin", "près"], "loin", "dm_t2"),
            ("3. La vergence de deux lentilles accolées vaut C = C1 + .........", ["Choisir...", "C2", "10"], "C2", "dm_t3"),
            ("4. Si C1 = +10 δ et C2 = -4 δ, la vergence résultante vaut +......... δ.", ["Choisir...", "6", "14"], "6", "dm_t4"),
            ("5. Si C1 + C2 = 0, le système est équivalent à une lame à faces .........", ["Choisir...", "parallèles", "courbes"], "parallèles", "dm_t5"),
            ("6. L'association convergent + divergent corrige les aberrations .........", ["Choisir...", "chromatiques", "thermiques"], "chromatiques", "dm_t6"),
            ("7. La mesure expérimentale de la focale d'une lentille s'appelle la .........", ["Choisir...", "focométrie", "calorimétrie"], "focométrie", "dm_t7"),
            ("8. Un choc déplaçant la lentille interne provoque un ......... optique.", ["Choisir...", "décentrement", "court-circuit"], "décentrement", "dm_t8"),
            ("9. L'allongement de la focale augmente le ......... des détails éloignés.", ["Choisir...", "grandissement", "poids"], "grandissement", "dm_t9"),
            ("10. La vergence d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dm_t10"),
        ]
    }
}


def mettre_a_jour_div_maint_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles divergentes adapté à la maintenance industrielle."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        dist_lentilles = st.session_state.get("slider_dm_s0", 75.0)
        f1_div = -25.0
        f2_conv = 100.0
        d_optimal = f1_div + f2_conv

        x1, y0 = 180.0, 125.0
        x2 = x1 + dist_lentilles * 2.2

        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x1, x1)), list((65, 185)), color="#38bdf8", lw=3)
        ax.text(x1, 55, "L1 Divergente\n(f'1 = -25 mm)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((x2, x2)), list((40, 210)), color="#22c55e", lw=3.5)
        ax.text(x2, 32, "L2 Convergente\n(f'2 = +100 mm)", color="#86efac", fontsize=7.5, fontweight="bold", ha="center")

        ecart_d = dist_lentilles - d_optimal
        pente_out = -ecart_d * 0.008
        for dy in [-14, 14]:
            ax.plot(list((40, x1)), list((y0 + dy, y0 + dy)), color="#ef4444", lw=2)
            dy2 = dy * (dist_lentilles / 25.0)
            ax.plot(list((x1, x2)), list((y0 + dy, y0 + dy2)), color="#ef4444", lw=2)
            y_fin = (y0 + dy2) + pente_out * (dy / 14.0) * (560 - x2)
            c_out = "#22c55e" if abs(ecart_d) <= 1.5 else "#f59e0b"
            ax.annotate("", xy=(560, y_fin), xytext=(x2, y0 + dy2), arrowprops=dict(arrowstyle="->", color=c_out, lw=2))

        statut = "FAISCEAU ÉLARGI (×4) ET PARALLÈLE : Écartement d = 75 mm optimal !" if abs(ecart_d) <= 1.5 else f"DÉRÉGLÉ (Écart {ecart_d:+.0f} mm) : Réglez la distance L1-L2 à 75 mm."
        c_stat = "#22c55e" if abs(ecart_d) <= 1.5 else "#ef4444"
        ax.text(25, 18, "MAINTENANCE LASER : ÉLARGISSEUR DE FAISCEAU AFOCAL DE GALILÉE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.dm_mesure_courante = (f"d = {dist_lentilles:.0f} mm", "Cible = 75 mm", "Facteur G = 4×", "PARALLÈLE" if abs(ecart_d) <= 1.5 else "DÉRÉGLÉ")

    elif sujet_idx == 1:
        vergence_judas = st.session_state.get("slider_dm_s1", -15.0)
        champ_deg = int(min(175, 60 + abs(vergence_judas) * 4.5))
        x0, y0 = 260.0, 130.0

        ax.add_patch(patches.Rectangle((x0 - 8, 30), 16, 200, facecolor="#475569", edgecolor="#94a3b8"))
        ax.plot(list((x0, x0)), list((95, 165)), color="#38bdf8", lw=4)
        ax.text(x0, 22, f"Porte Machine + Judas (C = {vergence_judas:.0f} δ)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        rad_c = math.radians(champ_deg / 2.0)
        dy_champ = min(105.0, 220.0 * math.tan(rad_c) * 0.45)
        ax.fill(list((x0, 40, 40)), list((y0, y0 - dy_champ, y0 + dy_champ)), color="#22c55e", alpha=0.22)
        ax.plot(list((40, x0)), list((y0 - dy_champ, y0 - 15)), color="#fde047", lw=1.8)
        ax.plot(list((40, x0)), list((y0 + dy_champ, y0 + 15)), color="#fde047", lw=1.8)
        ax.annotate("", xy=(470, y0 - 15), xytext=(x0, y0 - 15), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
        ax.annotate("", xy=(470, y0 + 15), xytext=(x0, y0 + 15), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
        ax.text(485, y0, "Œil Opérateur", color="#86efac", fontsize=8, fontweight="bold", va="center")

        ax.text(25, 18, "SÉCURITÉ MACHINE : JUDAS OPTIQUE GRAND-ANGLE DIVERGENT", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence C = {vergence_judas:.0f} δ  |  Champ de vision couvert : {champ_deg}° (Image virtuelle droite et rétrécie)", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dm_mesure_courante = (f"C = {vergence_judas:.0f} δ", f"Champ = {champ_deg}°", "0 < γ < 1", "VISIBILITÉ OK")

    else:
        c1_conv = st.session_state.get("slider_dm_c1_s2", 10.0)
        c2_div = st.session_state.get("slider_dm_c2_s2", -4.0)
        c_tot = c1_conv + c2_div
        x0, y0 = 240.0, 130.0

        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x0 - 4, x0 - 4)), list((50, 210)), color="#22c55e", lw=3)
        ax.plot(list((x0 + 4, x0 + 4)), list((50, 210)), color="#38bdf8", lw=3)
        ax.text(x0, 38, f"Doublet (C1={c1_conv:+.0f}δ | C2={c2_div:+.0f}δ)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        for dy in [-45, -22, 22, 45]:
            ax.plot(list((40, x0 - 4)), list((y0 + dy, y0 + dy)), color="#ef4444", lw=1.8)
            if abs(c_tot) < 0.1:
                ax.annotate("", xy=(560, y0 + dy), xytext=(x0 + 4, y0 + dy), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))
            elif c_tot > 0:
                f_px = min(300.0, 1200.0 / c_tot)
                ax.annotate("", xy=(x0 + f_px, y0), xytext=(x0 + 4, y0 + dy), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
            else:
                pente_d = (dy / 45.0) * 0.25 * (abs(c_tot) / 5.0)
                ax.annotate("", xy=(560, y0 + dy + pente_d * 300.0), xytext=(x0 + 4, y0 + dy), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2))

        nature = "LAME PARALLÈLE (C = 0 δ)" if abs(c_tot) < 0.1 else ("CONVERGENT (C > 0)" if c_tot > 0 else "DIVERGENT (C < 0)")
        ax.text(25, 18, "FOCOMÉTRIE : VERGENCE ÉQUIVALENTE DE DEUX LENTILLES ACCOLÉES (C = C1 + C2)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence totale : C = ({c1_conv:+.0f}) + ({c2_div:+.0f}) = {c_tot:+.1f} δ  =>  Système {nature}", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dm_mesure_courante = (f"C1 = {c1_conv:+.0f} δ", f"C2 = {c2_div:+.0f} δ", f"C_tot = {c_tot:+.1f} δ", nature)

    return fig


def afficher_atelier_div_maint(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet de maintenance ci-dessus.")
        return
    banque = BANQUES_DIV_MAINT[sujet_idx]
    cle_ordre = f"ordre_quiz_dm_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Maintenance (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"dm_at4_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Maintenance (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")





def afficher_questions_optique6(verrouille=False):
    col_double_quiz_opt6, col_double_trous_opt6 = st.columns(2)

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
        
        trous_div = [
            ("1. Une lentille mince possede des bords plus epais que son centre. Elle est qualifiee de", ["Choisir...", "Divergente", "Convergente", "Plane"], "opt6_t1"),
            ("2. Sa distance focale f' et sa vergence C ont la particularite d'etre de signe", ["Choisir...", "Negatif", "Positif", "Neutre"], "opt6_t2"),
            ("3. Un rayon incident parallele a l'axe ressort en s'eloignant : son prolongement passe par le foyer", ["Choisir...", "Image F'", "Objet F", "Central O"], "opt6_t3"),
            ("4. Pour un objet reel, la fleche de l'image obtenue est toujours droite, plus petite et de nature", ["Choisir...", "Virtuelle", "Reelle", "Infinie"], "opt6_t4"),
            ("5. Tout rayon lumineux passant par le centre optique O traverse la lentille sans", ["Choisir...", "Deviation", "Reflexion", "Absorption"], "opt6_t5"),
            ("6. Le foyer image F' d'une lentille divergente est situe en amont : il est donc", ["Choisir...", "Virtuel", "Reel", "Inexistant"], "opt6_t6"),
            ("7. Un rayon incident dont le prolongement vise le foyer objet F ressort", ["Choisir...", "Parallele", "Perpendiculaire", "Inverse"], "opt6_t7"),
            ("8. Une lentille divergente corrige le defaut visuel de l'oeil appele la", ["Choisir...", "Myopie", "Presbytie", "Cataracte"], "opt6_t8"),
            ("9. Pour une focale f' = -50 cm (-0,50 m), la vergence C vaut -2,00", ["Choisir...", "Dioptries", "Metres", "Degres"], "opt6_t9"),
            ("10. Le grandissement gamma d'une lentille divergente est toujours compris entre 0 et", ["Choisir...", "1", "10", "100"], "opt6_t10"),
        ]

        dict_trous_opt6 = {}
        for enonce_t, opts_t, cle_t in trous_div:
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c1: st.write(enonce_t)
            with c2: dict_trous_opt6[cle_t] = st.selectbox("", opts_t, key=cle_t, disabled=verrouille, label_visibility="collapsed")

    return dict_quiz_opt6, dict_trous_opt6

def afficher_atelier_regles_div(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 2 (Règles de tracé divergentes)."""
    questions_rd = [
        {"id": "qrd1", "q": "Quelle est la caractéristique géométrique d'une lentille mince divergente ?", "options": ["Ses bords sont plus épais que son centre", "Ses bords sont plus minces que son centre", "Elle est parfaitement cylindrique"], "rep": "Ses bords sont plus épais que son centre"},
        {"id": "qrd2", "q": "Où est situé le foyer image F' d'une lentille divergente ?", "options": ["En amont (du côté de la lumière incidente, donc f' < 0)", "En aval (après la lentille, f' > 0)", "Sur le centre optique O"], "rep": "En amont (du côté de la lumière incidente, donc f' < 0)"},
        {"id": "qrd3", "q": "Comment ressort un rayon incident parallèle à l'axe optique après avoir traversé une lentille divergente ?", "options": ["Il s'écarte de l'axe optique en semblant provenir du foyer image F'", "Il converge vers le foyer image F'", "Il traverse tout droit sans déviation"], "rep": "Il s'écarte de l'axe optique en semblant provenir du foyer image F'"},
        {"id": "qrd4", "q": "Que fait un rayon incident passant par le centre optique O d'une lentille divergente ?", "options": ["Il traverse la lentille en ligne droite sans être dévié", "Il est réfléchi à 180°", "Il ressort parallèlement à l'axe optique"], "rep": "Il traverse la lentille en ligne droite sans être dévié"},
        {"id": "qrd5", "q": "Comment ressort un rayon incident dont le prolongement vise le foyer objet F (situé après la lentille) ?", "options": ["Il ressort parallèlement à l'axe optique", "Il passe par le centre optique O", "Il diverge vers le bas"], "rep": "Il ressort parallèlement à l'axe optique"},
        {"id": "qrd6", "q": "Quelles sont toujours les 3 propriétés de l'image A'B' d'un objet réel donnée par une lentille divergente ?", "options": ["Virtuelle, droite et plus petite que l'objet", "Réelle, renversée et plus grande", "Virtuelle, renversée et plus petite"], "rep": "Virtuelle, droite et plus petite que l'objet"},
        {"id": "qrd7", "q": "Quel est le signe de la distance focale f' et de la vergence C d'une lentille divergente ?", "options": ["Négatif (f' < 0 et C < 0)", "Positif (f' > 0 et C > 0)", "Nul"], "rep": "Négatif (f' < 0 et C < 0)"},
        {"id": "qrd8", "q": "Une lentille divergente de distance focale f' = -25 cm (-0,25 m) possède une vergence C égale à :", "options": ["- 4,0 dioptries (δ)", "+ 4,0 dioptries (δ)", "- 0,25 dioptrie (δ)"], "rep": "- 4,0 dioptries (δ)"},
        {"id": "qrd9", "q": "Peut-on projeter directement sur un écran l'image d'un objet réel formée par une lentille divergente seule ?", "options": ["Non, car l'image est toujours virtuelle (située avant la lentille)", "Oui, à n'importe quelle distance", "Oui, si l'objet est très grand"], "rep": "Non, car l'image est toujours virtuelle (située avant la lentille)"},
        {"id": "qrd10", "q": "Pourquoi représente-t-on certains rayons en pointillés avant une lentille divergente ?", "options": ["Ce sont les prolongements virtuels des rayons qui permettent de localiser l'image virtuelle A'B'", "Ce sont des rayons infrarouges invisibles", "Ce sont des rayons arrêtés par la lentille"], "rep": "Ce sont les prolongements virtuels des rayons qui permettent de localiser l'image virtuelle A'B'"},
    ]

    if "ordre_quiz_rd_aleatoire" not in st.session_state:
        random.shuffle(questions_rd)
        st.session_state.ordre_quiz_rd_aleatoire = questions_rd

    champs_rd = [
        ("1. Le symbole d'une lentille divergente porte des flèches pointant vers l'.........", ["Choisir...", "intérieur", "extérieur"], "intérieur", "rd_t1"),
        ("2. Les foyers F et F' sont ......... par rapport à une lentille convergente.", ["Choisir...", "inversés", "identiques"], "inversés", "rd_t2"),
        ("3. Le foyer image F' est situé en ......... de la lentille (f' < 0).", ["Choisir...", "amont", "aval"], "amont", "rd_t3"),
        ("4. Tout rayon passant par le centre optique O n'est pas .........", ["Choisir...", "dévié", "transmis"], "dévié", "rd_t4"),
        ("5. Tout rayon parallèle à l'axe diverge en semblant venir de .........", ["Choisir...", "F'", "F"], "F'", "rd_t5"),
        ("6. Tout rayon visant le foyer objet F ressort ......... à l'axe.", ["Choisir...", "parallèle", "perpendiculaire"], "parallèle", "rd_t6"),
        ("7. L'image d'un objet réel est toujours située ......... la lentille.", ["Choisir...", "avant", "après"], "avant", "rd_t7"),
        ("8. L'image formée est toujours droite, plus petite et .........", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "rd_t8"),
        ("9. La vergence C d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "rd_t9"),
        ("10. Le grandissement γ vérifie toujours 0 < γ < .........", ["Choisir...", "1", "10"], "1", "rd_t10"),
    ]

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Règles de Tracé Divergente (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_rd_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"rd_at2_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Règles de Tracé (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_rd:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


        
def afficher_atelier_hist_div(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 1 (Histoire des lentilles divergentes)."""
    questions_hd = [
        {"id": "qhd1", "q": "Quel défaut de vision (difficulté à voir nettement de loin) est corrigé par des lentilles divergentes ?", "options": ["La myopie", "La presbytie", "Le daltonisme"], "rep": "La myopie"},
        {"id": "qhd2", "q": "Qui est représenté sur le plus ancien portrait connu portant des lunettes à verres divergents (peint en 1517 par Raphaël) ?", "options": ["Le pape Léon X", "Galilée", "Napoléon Bonaparte"], "rep": "Le pape Léon X"},
        {"id": "qhd3", "q": "Quel astronome allemand a expliqué dès 1604 (Paralipomènes à Vitellion) comment les verres concaves corrigent la myopie ?", "options": ["Johannes Kepler", "Isaac Newton", "Archimède"], "rep": "Johannes Kepler"},
        {"id": "qhd4", "q": "Quel type de lentille Galilée a-t-il utilisé comme oculaire dans sa lunette astronomique de 1609 pour obtenir une image droite ?", "options": ["Une lentille divergente (plan-concave)", "Un prisme en coin de cube", "Un miroir parabolique"], "rep": "Une lentille divergente (plan-concave)"},
        {"id": "qhd5", "q": "Comment appelle-t-on la combinaison d'un objectif convergent et d'un oculaire divergent inventée en 1608-1609 ?", "options": ["La lunette de Galilée (utilisée aujourd'hui dans les jumelles de théâtre)", "Le microscope électronique", "Le périscope naval"], "rep": "La lunette de Galilée (utilisée aujourd'hui dans les jumelles de théâtre)"},
        {"id": "qhd6", "q": "Quel savant a inventé le doublet achromatique en 1758 en associant une lentille convergente (crown) et une lentille divergente (flint) ?", "options": ["John Dollond", "René Descartes", "Euclide"], "rep": "John Dollond"},
        {"id": "qhd7", "q": "Quel défaut optique des lentilles simples est supprimé en accolant une lentille divergente en verre flint à une convergente en verre crown ?", "options": ["L'aberration chromatique (les irisations colorées sur les bords)", "La réflexion totale", "La gravité"], "rep": "L'aberration chromatique (les irisations colorées sur les bords)"},
        {"id": "qhd8", "q": "Où se forme l'image d'un objet lointain dans un œil myope non corrigé ?", "options": ["En avant de la rétine (œil trop long ou trop convergent)", "Derrière la rétine", "Sur le cristallin"], "rep": "En avant de la rétine (œil trop long ou trop convergent)"},
        {"id": "qhd9", "q": "Pourquoi place-t-on un verre divergent devant un œil myope ?", "options": ["Pour faire diverger légèrement les rayons et repousser l'image exactement sur la rétine", "Pour grossir l'image 50 fois", "Pour bloquer la lumière bleue"], "rep": "Pour faire diverger légèrement les rayons et repousser l'image exactement sur la rétine"},
        {"id": "qhd10", "q": "Quel empereur romain myope utilisait déjà une émeraude taillée concave (divergente) pour regarder les combats de gladiateurs ?", "options": ["L'empereur Néron", "Jules César", "Charlemagne"], "rep": "L'empereur Néron"},
    ]

    if "ordre_quiz_hd_aleatoire" not in st.session_state:
        random.shuffle(questions_hd)
        st.session_state.ordre_quiz_hd_aleatoire = questions_hd

    champs_hd = [
        ("1. Une lentille divergente possède des bords plus ......... que son centre.", ["Choisir...", "épais", "minces"], "épais", "hd_t1"),
        ("2. L'empereur romain ......... utilisait une émeraude concave pour voir de loin.", ["Choisir...", "Néron", "Auguste"], "Néron", "hd_t2"),
        ("3. Les verres divergents corrigent le défaut visuel appelé la .........", ["Choisir...", "myopie", "presbytie"], "myopie", "hd_t3"),
        ("4. En 1604, Johannes ......... explique le fonctionnement des verres concaves.", ["Choisir...", "Kepler", "Pascal"], "Kepler", "hd_t4"),
        ("5. En 1609, ......... utilise une lentille divergente comme oculaire de sa lunette.", ["Choisir...", "Galilée", "Newton"], "Galilée", "hd_t5"),
        ("6. La lunette de Galilée donne directement une image ......... (à l'endroit).", ["Choisir...", "droite", "renversée"], "droite", "hd_t6"),
        ("7. Dans un œil myope, l'image se forme en ......... de la rétine.", ["Choisir...", "avant", "arrière"], "avant", "hd_t7"),
        ("8. Le verre divergent repousse l'image sur la ......... pour la rendre nette.", ["Choisir...", "rétine", "cornée"], "rétine", "hd_t8"),
        ("9. En 1758, John ......... associe lentille convergente et divergente.", ["Choisir...", "Dollond", "Fresnel"], "Dollond", "hd_t9"),
        ("10. Ce doublet supprime les aberrations ......... dans les objectifs photo.", ["Choisir...", "chromatiques", "thermiques"], "chromatiques", "hd_t10"),
    ]

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Historique Lentilles Divergentes (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_hd_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"hd_at1_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Historique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_hd:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


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


with tab1:
    st.header("Atelier 1 : Histoire des lentilles divergentes et de la correction de la myopie")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Objectif de l'atelier :</p>
        <p style="margin-bottom: 0;">Découvrir l'histoire des lentilles divergentes (biconcaves et plan-concaves), depuis l'émeraude de Néron jusqu'à la lunette de Galilée et aux doublets achromatiques.</p>
    </div>
    """, unsafe_allow_html=True)

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        try: st.image("neron_emeraude.jpg", caption="L'Antiquité : L'émeraude de Néron", use_container_width=True)
        except Exception: st.warning("L'image 'neron_emeraude.jpg' est introuvable.")
        st.info("**L'Antiquité : Les pierres concaves**\n* L'historien Pline l'Ancien rapporte que l'empereur Néron regardait les jeux du cirque à travers une émeraude taillée en creux (divergente) pour corriger sa myopie.")

    with col_d2:
        try: st.image("kepler.jpg", caption="Johannes Kepler (1571 - 1630)", use_container_width=True)
        except Exception: st.warning("L'image 'kepler.jpg' est introuvable.")
        st.info("**Johannes Kepler (1604)**\n* Démontre que dans un œil myope, les rayons convergent trop tôt devant la rétine.\n* Prouve qu'un verre divergent repousse le foyer sur la rétine.")

    with col_d3:
        try: st.image("galilee_lunette.jpg", caption="Galilée et sa lunette (1609)", use_container_width=True)
        except Exception: st.warning("L'image 'galilee_lunette.jpg' est introuvable.")
        st.info("**Galilée (1609)**\n* Associe un objectif convergent et un oculaire divergent.\n* Obtient une image droite (à l'endroit), principe toujours utilisé dans les jumelles de théâtre.")

    with col_d4:
        try: st.image("dollond_doublet.jpg", caption="John Dollond (1758)", use_container_width=True)
        except Exception: st.warning("L'image 'dollond_doublet.jpg' est introuvable.")
        st.info("**John Dollond (1758)**\n* Invente le doublet achromatique en accolant une lentille convergente (crown) et une divergente (flint) pour supprimer les défauts de couleur.")

    st.markdown("---")
    if "hd_verrouille_tab1" not in st.session_state: st.session_state.hd_verrouille_tab1 = False
    verrou_hd = st.session_state.hd_verrouille_tab1
    afficher_atelier_hist_div(verrouille=verrou_hd)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_hd = st.checkbox("Je certifie avoir complété l'Atelier 1 (Histoire des lentilles divergentes).", key="certif_hd1", disabled=verrou_hd)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_exp_hd1", use_container_width=True, disabled=verrou_hd):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_hd:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            sc_q = sum(1.0 for q in st.session_state.get("ordre_quiz_hd_aleatoire", []) if st.session_state.get(f"hd_at1_g_{q['id']}") == q["rep"])
            rep_t = {"hd_t1": "épais", "hd_t2": "Néron", "hd_t3": "myopie", "hd_t4": "Kepler", "hd_t5": "Galilée", "hd_t6": "droite", "hd_t7": "avant", "hd_t8": "rétine", "hd_t9": "Dollond", "hd_t10": "chromatiques"}
            sc_t = sum(1.0 for k, v in rep_t.items() if st.session_state.get(k) == v)
            st.session_state.score_hd1_p1, st.session_state.score_hd1_p2, st.session_state.score_final_hd1 = sc_q, sc_t, sc_q + sc_t
            st.session_state.hd_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("hd_verrouille_tab1", False):
        scr1, scr2, tot_s = st.session_state.score_hd1_p1, st.session_state.score_hd1_p2, st.session_state.score_final_hd1
        ts_hd = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 1 SCELLÉ | Note : {tot_s:.1f} / 20")
        html_hd = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 1 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 1 : Histoire des Lentilles Divergentes</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_hd}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get("ordre_quiz_hd_aleatoire", []), 1):
            qid_c = q["id"]
            html_hd += f"<tr><td>{num}</td><td>{q['q']}</td><td>{st.session_state.get(f'hd_at1_g_{qid_c}', 'Choisir...')}</td><td>{q['rep']}</td></tr>"
        html_hd += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"
        verif_hd = [("1. Bords plus ......... que le centre.", "épais", "hd_t1"), ("2. Empereur romain .........", "Néron", "hd_t2"), ("3. Défaut visuel : .........", "myopie", "hd_t3"), ("4. Savant de 1604 : .........", "Kepler", "hd_t4"), ("5. Savant de 1609 : .........", "Galilée", "hd_t5"), ("6. Image .........", "droite", "hd_t6"), ("7. En ......... de la rétine.", "avant", "hd_t7"), ("8. Sur la .........", "rétine", "hd_t8"), ("9. Doublet de .........", "Dollond", "hd_t9"), ("10. Aberrations .........", "chromatiques", "hd_t10")]
        for idx_t, (en, rep, cle) in enumerate(verif_hd, 1):
            html_hd += f"<tr><td>{idx_t}</td><td>{en}</td><td>{st.session_state.get(cle, 'Choisir...')}</td><td>{rep}</td></tr>"
        html_hd += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 1 (.html)", data=html_hd, file_name=preparer_nom_fichier("Rapport_Atelier_1_Histoire_Divergentes").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab2:
    st.header("Atelier 2 : Définition et règles de tracé des rayons (Lentille divergente)")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les 3 rayons particuliers d'une lentille mince divergente :</p>
        <ul style="margin-bottom: 0; line-height: 1.7;">
            <li><strong>Rayon 1 (Jaune - Parallèle à l'axe) :</strong> Tout rayon incident parallèle à l'axe optique diverge en semblant provenir du <strong>foyer image virtuel F'</strong> (situé en amont).</li>
            <li><strong>Rayon 2 (Bleu - Centre optique O) :</strong> Tout rayon incident passant par le centre optique <strong>O</strong> n'est <strong>pas dévié</strong>.</li>
            <li><strong>Rayon 3 (Rose - Vise le foyer objet F) :</strong> Tout rayon incident dont le prolongement passe par le foyer objet <strong>F</strong> ressort <strong>parallèlement à l'axe optique</strong>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_rd1, col_rd2 = st.columns([0.55, 0.45])
    with col_rd1:
        st.radio(
            "Sélectionnez le rayon à observer :",
            ["Tous les 3 rayons particuliers", "Rayon 1 : Parallèle → Semble venir de F'", "Rayon 2 : Passe par O → Non dévié", "Rayon 3 : Vise F → Ressort parallèle"],
            key="radio_regles_div_rayon"
        )
    with col_rd2:
        st.slider("Distance focale |f'| de démonstration (px) :", min_value=60.0, max_value=140.0, value=100.0, step=5.0, key="slider_regles_div_f")

    st.pyplot(dessiner_regles_trace_divergente_matplotlib(), use_container_width=True)

    st.markdown("---")
    if "rd_verrouille_tab2" not in st.session_state: st.session_state.rd_verrouille_tab2 = False
    verrou_rd = st.session_state.rd_verrouille_tab2
    afficher_atelier_regles_div(verrouille=verrou_rd)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_rd = st.checkbox("Je certifie avoir complété l'Atelier 2 (Règles de tracé - Divergente).", key="certif_rd2", disabled=verrou_rd)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_exp_rd2", use_container_width=True, disabled=verrou_rd):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_rd:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            sc_q = sum(1.0 for q in st.session_state.get("ordre_quiz_rd_aleatoire", []) if st.session_state.get(f"rd_at2_g_{q['id']}") == q["rep"])
            rep_t = {"rd_t1": "intérieur", "rd_t2": "inversés", "rd_t3": "amont", "rd_t4": "dévié", "rd_t5": "F'", "rd_t6": "parallèle", "rd_t7": "avant", "rd_t8": "virtuelle", "rd_t9": "négative", "rd_t10": "1"}
            sc_t = sum(1.0 for k, v in rep_t.items() if st.session_state.get(k) == v)
            st.session_state.score_rd2_p1, st.session_state.score_rd2_p2, st.session_state.score_final_rd2 = sc_q, sc_t, sc_q + sc_t
            st.session_state.rd_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("rd_verrouille_tab2", False):
        scr1, scr2, tot_s = st.session_state.score_rd2_p1, st.session_state.score_rd2_p2, st.session_state.score_final_rd2
        ts_rd = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 2 SCELLÉ | Note : {tot_s:.1f} / 20")

        html_rd = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Règles de Tracé des Lentilles Divergentes</p>
                <p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_rd}</p>
                <div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div>
            </div>
            <p style="background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong>
            </p>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q in enumerate(st.session_state.get("ordre_quiz_rd_aleatoire", []), 1):
            qid_c = q["id"]
            saisie_q = st.session_state.get(f"rd_at2_g_{qid_c}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_q) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_rd += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_q}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"

        html_rd += """
                </tbody>
            </table>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        verif_rd = [
            ("1. Le symbole d'une lentille divergente porte des flèches pointant vers l'.........", "intérieur", "rd_t1"),
            ("2. Les foyers F et F' sont ......... par rapport à une lentille convergente.", "inversés", "rd_t2"),
            ("3. Le foyer image F' est situé en ......... de la lentille (f' < 0).", "amont", "rd_t3"),
            ("4. Tout rayon passant par le centre optique O n'est pas .........", "dévié", "rd_t4"),
            ("5. Tout rayon parallèle à l'axe diverge en semblant venir de .........", "F'", "rd_t5"),
            ("6. Tout rayon visant le foyer objet F ressort ......... à l'axe.", "parallèle", "rd_t6"),
            ("7. L'image d'un objet réel est toujours située ......... la lentille.", "avant", "rd_t7"),
            ("8. L'image formée est toujours droite, plus petite et .........", "virtuelle", "rd_t8"),
            ("9. La vergence C d'une lentille divergente est toujours .........", "négative", "rd_t9"),
            ("10. Le grandissement γ vérifie toujours 0 < γ < .........", "1", "rd_t10"),
        ]

        for idx_t, (en, rep, cle) in enumerate(verif_rd, 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_rd += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"

        html_rd += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            "Télécharger le rapport officiel de l'Atelier 2 (.html)",
            data=html_rd,
            file_name=preparer_nom_fichier("Rapport_Atelier_2_Regles_Divergente").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True
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

            # Moteur de correction automatique du Texte a trous (10 Pts : 10 items x 1 pt)
            attendus_to6_v = {
                "t1": "Divergente", "t2": "Negatif", "t3": "Image F'", "t4": "Virtuelle", "t5": "Deviation",
                "t6": "Virtuel", "t7": "Parallele", "t8": "Myopie", "t9": "Dioptries", "t10": "1"
            }
            score_trous_opt6 = sum([1.0 for tk, tv in attendus_to6_v.items() if st.session_state.get(f"opt6_{tk}") == tv])

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
        timestamp_opt6 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 6 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo6_v = {
            "q1": "Plus epais que son centre", "q2": "Une fleche double retournee (pointes vers le centre)", 
            "q3": "Toujours negative (f' < 0)", "q4": "Negative (en dioptries)", 
            "q5": "Le foyer image virtuel F' situe en amont", "q6": "Parallele a l'axe optique", 
            "q7": "Virtuelle, droite et plus petite", "q8": "Positif et inferieur a 1 (0 < g < 1)", 
            "q9": "-2.00 δ", "q10": "Oui, ce sont les valeurs numeriques de f' et x qui changent de signe"
        }
        enonces_qo6_v = {
            "q1": "D'un point de vue geometrique, une lentille mince est qualifiee de divergente si ses bords sont :",
            "q2": "Le symbole d'une lentille divergente sur un schema optique est represente par :",
            "q3": "La distance focale f' d'une lentille divergente est une grandeur physique :",
            "q4": "Par consequent, la vergence C d'une lentille divergente s'exprime par une valeur :",
            "q5": "Un rayon incident parallele a l'axe optique ressort de la lentille divergente en semblant provenir de :",
            "q6": "Un rayon incident dont le prolongement passe par le foyer objet F ressort de la lentille :",
            "q7": "Pour un objet reel AB place avant la lentille divergente, l'image A'B' obtenue est toujours :",
            "q8": "Le grandissement gamma pour une lentille divergente avec un objet reel est toujours :",
            "q9": "Si une lentille divergente a une distance focale f' = -50 cm, sa vergence C vaut :",
            "q10": "Dans la relation de conjugaison de Descartes, la formule reste-t-elle identique a celle des convergentes :"
        }

        attendus_to6_v = {
            "t1": "Divergente", "t2": "Negatif", "t3": "Image F'", "t4": "Virtuelle", "t5": "Deviation",
            "t6": "Virtuel", "t7": "Parallele", "t8": "Myopie", "t9": "Dioptries", "t10": "1"
        }
        enonces_to6_v = {
            "t1": "1. Une lentille mince possede des bords plus epais que son centre. Elle est qualifiee de .........",
            "t2": "2. Sa distance focale f' et sa vergence C ont la particularite d'etre de signe .........",
            "t3": "3. Un rayon incident parallele a l'axe ressort en s'eloignant : son prolongement passe par le foyer .........",
            "t4": "4. Pour un objet reel, la fleche de l'image obtenue est toujours droite, plus petite et de nature .........",
            "t5": "5. Tout rayon lumineux passant par le centre optique O traverse la lentille sans .........",
            "t6": "6. Le foyer image F' d'une lentille divergente est situe en amont : il est donc .........",
            "t7": "7. Un rayon incident dont le prolongement vise le foyer objet F ressort .........",
            "t8": "8. Une lentille divergente corrige le defaut visuel de l'oeil appele la .........",
            "t9": "9. Pour une focale f' = -50 cm (-0,50 m), la vergence C vaut -2,00 .........",
            "t10": "10. Le grandissement gamma d'une lentille divergente est toujours compris entre 0 et ........."
        }

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
                <p style="font-size: 12px; opacity: 0.7;">Atelier : Lentilles Minces Divergentes | Scelle le : {timestamp_opt6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 6</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 10 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LA DIVERGENCE (10 PTS)</div>
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

        for idx_q, (q_id, attendu) in enumerate(attendus_qo6_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt6_{q_id}", "Choisir...")
            enonce_q = enonces_qo6_v.get(q_id, f"Question {idx_q}")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"

            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt6 += f"<tr><td>{idx_q}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt6 += """
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

        for t_key, attendu_t in attendus_to6_v.items():
            saisie_t = st.session_state.get(f"opt6_{t_key}", "Choisir...")
            phrase_t = enonces_to6_v.get(t_key, t_key)
            v_lbl_t = "CORRECT" if str(saisie_t) == str(attendu_t) else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_opt6 += f"<tr><td style='text-align: left;'>{phrase_t}</td><td style='text-align:center;'>{saisie_t}</td><td style='text-align:center;'>{attendu_t}</td><td class='{v_class_t}' style='text-align: center;'>{v_lbl_t}</td></tr>"

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


with tab4:
    st.header("Atelier 4 : Applications dans le domaine de la Maintenance Industrielle")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles divergentes au service de la sécurité et de la métrologie laser :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">En maintenance industrielle, les lentilles minces divergentes (<b><i>f'</i> &lt; 0</b>) permettent d'élargir les faisceaux laser haute puissance, d'inspecter les enceintes machines à 180° via des judas grand-angle et de contrôler les doublets optiques.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_div_maint = [
        {"titre": "Cas N°1 : Élargisseur de faisceau laser de Galilée (Divergente + Convergente)", "img": "div_maint_laser.jpg", "leg": "Expander de faisceau laser monté sur tête de découpe", "exp": "**Principe :** L'association d'une lentille divergente (<i>f'</i><sub>1</sub> = &minus;25 mm) et d'une lentille convergente (<i>f'</i><sub>2</sub> = +100 mm) séparées de <i>d</i> = 75 mm multiplie le diamètre du faisceau par <b><i>G</i> = |<i>f'</i><sub>2</sub> / <i>f'</i><sub>1</sub>| = 4&times;</b>."},
        {"titre": "Cas N°2 : Judas optique grand-angle sur porte de sécurité machine", "img": "div_maint_judas.jpg", "leg": "Œilleton grand-angle installé sur carter de centre d'usinage CNC", "exp": "**Principe :** La lentille divergente d'entrée donne une image **virtuelle, droite et rétrécie** couvrant jusqu'à **175°** de champ de vision."},
        {"titre": "Cas N°3 : Contrôle focométrique de lentilles accolées (C = C1 + C2)", "img": "div_maint_banc.jpg", "leg": "Banc de contrôle optique de doublets achromatiques", "exp": "**Principe :** En associant une lentille convergente (<i>C</i><sub>1</sub> &gt; 0) et une divergente (<i>C</i><sub>2</sub> &lt; 0), la vergence totale vaut <b><i>C</i> = <i>C</i><sub>1</sub> + <i>C</i><sub>2</sub></b>."}
    ]

    if "sujet_dm_tire" not in st.session_state:
        st.session_state.sujet_dm_tire = None

    if st.button("TIRER AU SORT UN SUJET MAINTENANCE (DIVERGENTES)", key="btn_tirage_dm", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_dm_tire]
        st.session_state.sujet_dm_tire = random.choice(choix)
        st.session_state.mesures_dm_log = []
        st.rerun()

    if st.session_state.sujet_dm_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique de maintenance.")
    else:
        idx_dm = st.session_state.sujet_dm_tire
        data_dm = sujets_div_maint[idx_dm]
        st.success(f"Sujet attribué : **{data_dm['titre']}**")
        st.markdown(data_dm["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_dm["img"], caption=data_dm["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_dm['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_div_maint.jpg", caption="La pause BD : Attention à ne pas inverser la lentille divergente au remontage !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_div_maint.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_dm_log" not in st.session_state: st.session_state.mesures_dm_log = []
        if idx_dm == 0:
            st.slider("Distance d entre L1 et L2 (mm) [Optimal = 75 mm] :", 55.0, 95.0, 75.0, 1.0, key="slider_dm_s0")
        elif idx_dm == 1:
            st.slider("Vergence C de la lentille divergente du judas (δ) :", -25.0, -5.0, -15.0, 1.0, key="slider_dm_s1")
        else:
            c1_m, c2_m = st.columns(2)
            with c1_m: st.slider("Vergence lentille convergente C1 (δ) :", 2.0, 15.0, 10.0, 1.0, key="slider_dm_c1_s2")
            with c2_m: st.slider("Vergence lentille divergente C2 (δ) :", -15.0, -2.0, -4.0, 1.0, key="slider_dm_c2_s2")

        if st.button("ENREGISTRER CE RELEVÉ MAINTENANCE", key="btn_rel_dm", use_container_width=True):
            if "dm_mesure_courante" in st.session_state:
                st.session_state.mesures_dm_log.append(st.session_state.dm_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_div_maint_matplotlib(idx_dm), use_container_width=True)
        if st.session_state.mesures_dm_log:
            df_dm = pd.DataFrame(st.session_state.mesures_dm_log, columns=["Paramètre 1", "Paramètre 2", "Calcul", "Diagnostic"])
            st.dataframe(df_dm, use_container_width=True, hide_index=True)

    st.write("---")
    if "dm_verrouille_tab4" not in st.session_state: st.session_state.dm_verrouille_tab4 = False
    verrou_dm = st.session_state.dm_verrouille_tab4
    sujet_actif_dm = st.session_state.get("sujet_dm_tire", None)
    afficher_atelier_div_maint(sujet_actif_dm, verrouille=verrou_dm)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_dm = st.checkbox("Je certifie avoir complété l'Atelier 4 (Maintenance - Divergentes).", key="certif_dm4", disabled=verrou_dm)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_exp_dm4", use_container_width=True, disabled=verrou_dm):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_dm is None or not case_certif_dm:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_DIV_MAINT[sujet_actif_dm]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_dm_{sujet_actif_dm}", []) if st.session_state.get(f"dm_at4_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_dm}") == rep)
            st.session_state.score_dm4_p1, st.session_state.score_dm4_p2, st.session_state.score_final_dm4 = sc_q, sc_t, sc_q + sc_t
            st.session_state.dm_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("dm_verrouille_tab4", False) and sujet_actif_dm is not None:
        scr1, scr2, tot_s = st.session_state.score_dm4_p1, st.session_state.score_dm4_p2, st.session_state.score_final_dm4
        ts_dm = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 4 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_DIV_MAINT[sujet_actif_dm]
        html_dm = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 4 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 4 : Maintenance (Lentilles Divergentes) - {sujets_div_maint[sujet_actif_dm]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_dm}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_dm_{sujet_actif_dm}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"dm_at4_g_{qid_curr}", "Choisir...")
            html_dm += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td></tr>"
        html_dm += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_dm}", "Choisir...")
            html_dm += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td></tr>"
        html_dm += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 4 (.html)", data=html_dm, file_name=preparer_nom_fichier("Rapport_Atelier_4_Maintenance_Divergentes").replace(".txt", ".html"), mime="text/html", use_container_width=True)










