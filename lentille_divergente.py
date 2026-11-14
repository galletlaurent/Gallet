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

BANQUES_DIV_TRANS = {
    0: {
        "questions": [
            {"id": "qdtr0_1", "q": "Quel type de lentille divergente équipe les rétroviseurs grand-angle ou les optiques d'extension de champ sur les poids lourds ?", "options": ["Une lentille divergente à grand champ (ou un ensemble divergent-convexe rétrofocus)", "Un prisme dispersif en plastique", "Une loupe convergente à fort grossissement"], "rep": "Une lentille divergente à grand champ (ou un ensemble divergent-convexe rétrofocus)"},
            {"id": "qdtr0_2", "q": "Quel effet optique produit une lentille divergente sur la taille apparente des véhicules observés derrière un camion ?", "options": ["Elle forme une image virtuelle, droite et rétrécie permettant d'élargir le champ de vision", "Elle grossit les véhicules 20 fois", "Elle retourne l'image la tête en bas"], "rep": "Elle forme une image virtuelle, droite et rétrécie permettant d'élargir le champ de vision"},
            {"id": "qdtr0_3", "q": "Quelle précaution de conduite impose l'utilisation d'une optique divergente grand-angle pour surveiller l'angle mort ?", "options": ["Les véhicules paraissent plus éloignés sur l'image qu'ils ne le sont réellement", "Les véhicules paraissent collés au pare-chocs", "La vitesse affichée est divisée par deux"], "rep": "Les véhicules paraissent plus éloignés sur l'image qu'ils ne le sont réellement"},
            {"id": "qdtr0_4", "q": "Comment ressortent les rayons lumineux issus d'un obstacle latéral après traversée de la lentille divergente frontale d'une caméra d'angle mort ?", "options": ["Ils s'écartent moins de l'axe vers le capteur, permettant de capter un angle jusqu'à 170°", "Ils sont arrêtés par la lentille", "Ils ressortent strictement parallèles"], "rep": "Ils s'écartent moins de l'axe vers le capteur, permettant de capter un angle jusqu'à 170°"},
            {"id": "qdtr0_5", "q": "Quel est le signe de la distance focale f' et de la vergence C de cette lentille frontale divergente ?", "options": ["Négatif (f' < 0 et C < 0)", "Positif (f' > 0 et C > 0)", "Nul"], "rep": "Négatif (f' < 0 et C < 0)"},
            {"id": "qdtr0_6", "q": "Quelle réglementation impose désormais des systèmes de vision indirecte grand-angle (caméras/rétroviseurs) sur les poids lourds en ville ?", "options": ["La détection des usagers vulnérables (cyclistes et piétons) dans les angles morts", "La mesure de la pression des pneus", "Le contrôle de la température d'échappement"], "rep": "La détection des usagers vulnérables (cyclistes et piétons) dans les angles morts"},
            {"id": "qdtr0_7", "q": "Que vaut le grandissement γ de l'image virtuelle formée par la lentille divergente ?", "options": ["Positif et compris entre 0 et 1 (0 < γ < 1)", "Négatif (-3)", "Supérieur à +5"], "rep": "Positif et compris entre 0 et 1 (0 < γ < 1)"},
            {"id": "qdtr0_8", "q": "Quel défaut géométrique apparaît sur les bords de l'écran lorsque la vergence C est très négative (ex : -22 δ) ?", "options": ["Une distorsion en barillet (courbure des lignes verticales)", "Une image en noir et blanc", "Un dédoublement de l'image"], "rep": "Une distorsion en barillet (courbure des lignes verticales)"},
            {"id": "qdtr0_9", "q": "Comment le calculateur vidéo du camion corrige-t-il la courbure due à la lentille divergente ?", "options": ["Par un traitement numérique de redressement d'image (déwarping) avant affichage", "En chauffant la lentille", "En coupant la moitié de l'écran"], "rep": "Par un traitement numérique de redressement d'image (déwarping) avant affichage"},
            {"id": "qdtr0_10", "q": "Si la lentille divergente frontale a une distance focale f' = -5,0 cm (-0,050 m), quelle est sa vergence C ?", "options": ["- 20 dioptries (δ)", "+ 20 dioptries (δ)", "- 0,5 dioptrie (δ)"], "rep": "- 20 dioptries (δ)"},
        ],
        "trous": [
            ("1. Les caméras d'angle mort utilisent une lentille ......... à l'avant.", ["Choisir...", "divergente", "plane"], "divergente", "dtr_t1"),
            ("2. Cette lentille permet d'élargir le ......... de vision jusqu'à 170°.", ["Choisir...", "champ", "rayon"], "champ", "dtr_t2"),
            ("3. Elle protège les usagers vulnérables (cyclistes) dans les angles .........", ["Choisir...", "morts", "droits"], "morts", "dtr_t3"),
            ("4. L'image virtuelle formée par la lentille divergente est droite et .........", ["Choisir...", "rétrécie", "agrandie"], "rétrécie", "dtr_t4"),
            ("5. Sur l'écran, les véhicules paraissent plus ......... qu'en réalité.", ["Choisir...", "éloignés", "proches"], "éloignés", "dtr_t5"),
            ("6. La déformation courbe des bords s'appelle la distorsion en .........", ["Choisir...", "barillet", "coussinet"], "barillet", "dtr_t6"),
            ("7. Une focale f' = -5,0 cm correspond à une vergence de ......... dioptries.", ["Choisir...", "-20", "+20"], "-20", "dtr_t7"),
            ("8. La distance focale f' d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dtr_t8"),
            ("9. Le grandissement vérifie toujours 0 < γ < .........", ["Choisir...", "1", "10"], "1", "dtr_t9"),
            ("10. Le calcul optique applique la loi de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "dtr_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qdtr1_1", "q": "Quel équipement optique de sécurité routière utilise des lentilles divergentes pour étaler le faisceau d'une LED rouge sur toute la largeur du véhicule ?", "options": ["Les feux de position arrière et feux antibrouillard à diffuseur divergent", "Les phares longue portée laser", "Le rétroviseur intérieur électrochrome"], "rep": "Les feux de position arrière et feux antibrouillard à diffuseur divergent"},
            {"id": "qdtr1_2", "q": "Pourquoi cherche-t-on à faire diverger le faisceau d'un feu de position arrière plutôt que de le concentrer en un point ?", "options": ["Pour être vu par les véhicules arrivant aussi bien de face que sur les côtés", "Pour chauffer le pare-chocs arrière", "Pour économiser le câblage"], "rep": "Pour être vu par les véhicules arrivant aussi bien de face que sur les côtés"},
            {"id": "qdtr1_3", "q": "Quel est le comportement d'un faisceau lumineux parallèle traversant une lentille plan-concave divergente ?", "options": ["Il s'écarte de l'axe optique en semblant provenir du foyer image virtuel F'", "Il converge au foyer image F'", "Il est réfléchi vers la batterie"], "rep": "Il s'écarte de l'axe optique en semblant provenir du foyer image virtuel F'"},
            {"id": "qdtr1_4", "q": "Quel type de lentille divergente est moulé directement sur la face interne des optiques de feux arrière de semi-remorques ?", "options": ["Des micro-lentilles divergentes (optiques cylindriques ou biconcaves)", "Des miroirs sphériques", "Des filtres polarisants"], "rep": "Des micro-lentilles divergentes (optiques cylindriques ou biconcaves)"},
            {"id": "qdtr1_5", "q": "Comment évolue l'angle de diffusion lumineuse si l'on remplace une lentille de vergence -5 δ par une lentille de vergence -18 δ ?", "options": ["L'angle de diffusion s'élargit considérablement", "L'angle se rétrécit", "La lumière devient bleue"], "rep": "L'angle de diffusion s'élargit considérablement"},
            {"id": "qdtr1_6", "q": "Quel défaut de sécurité apparaît si un choc casse la lentille divergente d'un feu arrière et laisse la LED nue ?", "options": ["Le faisceau devient trop directif et n'est plus visible sous les angles latéraux réglementaires", "La LED grille instantanément", "Les clignotants s'inversent"], "rep": "Le faisceau devient trop directif et n'est plus visible sous les angles latéraux réglementaires"},
            {"id": "qdtr1_7", "q": "Quel matériau plastique résistant aux intempéries et aux chocs est utilisé pour les optiques divergentes de feux arrière ?", "options": ["Le PMMA (Plexiglas) ou le polycarbonate teinté dans la masse", "Le verre ordinaire non trempé", "La céramique"], "rep": "Le PMMA (Plexiglas) ou le polycarbonate teinté dans la masse"},
            {"id": "qdtr1_8", "q": "Dans les feux antibrouillard arrière, pourquoi combine-t-on une lentille convergente et des stries divergentes horizontales ?", "options": ["Pour étaler la lumière horizontalement sur toute la largeur de la chaussée sans éclairer le ciel", "Pour éclairer uniquement les panneaux d'autoroute", "Pour réduire la consommation électrique"], "rep": "Pour étaler la lumière horizontalement sur toute la largeur de la chaussée sans éclairer le ciel"},
            {"id": "qdtr1_9", "q": "Quelle est la caractéristique géométrique d'une lentille divergente ?", "options": ["Ses bords sont plus épais que son centre", "Ses bords sont plus minces que son centre", "Elle est parfaitement plate"], "rep": "Ses bords sont plus épais que son centre"},
            {"id": "qdtr1_10", "q": "Quelle loi de l'optique explique l'écartement des rayons vers l'extérieur lors du passage verre-air ?", "options": ["La loi de réfraction de Snell-Descartes", "La loi d'Ohm", "Le principe d'inertie"], "rep": "La loi de réfraction de Snell-Descartes"},
        ],
        "trous": [
            ("1. Les feux arrière de poids lourds intègrent des lentilles .........", ["Choisir...", "divergentes", "planes"], "divergentes", "dtr_t1"),
            ("2. Elles permettent d'......... le faisceau lumineux sur les côtés.", ["Choisir...", "étaler", "concentrer"], "étaler", "dtr_t2"),
            ("3. Le véhicule reste ainsi ......... sous des angles latéraux importants.", ["Choisir...", "visible", "invisible"], "visible", "dtr_t3"),
            ("4. Une lentille divergente possède des bords plus ......... que son centre.", ["Choisir...", "épais", "minces"], "épais", "dtr_t4"),
            ("5. Les rayons émergents semblent provenir du foyer image virtuel .........", ["Choisir...", "F'", "F"], "F'", "dtr_t5"),
            ("6. Plus la vergence C est négative, plus l'angle de diffusion est .........", ["Choisir...", "large", "étroit"], "large", "dtr_t6"),
            ("7. Les optiques de feux sont moulées en ......... résistant aux chocs.", ["Choisir...", "PMMA", "carton"], "PMMA", "dtr_t7"),
            ("8. La vergence C d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dtr_t8"),
            ("9. Les feux antibrouillard étalent la lumière sur le plan .........", ["Choisir...", "horizontal", "vertical"], "horizontal", "dtr_t9"),
            ("10. La déviation des rayons obéit à la loi de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "dtr_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qdtr2_1", "q": "Quel dispositif d'affichage moderne projeté sur le pare-brise utilise un ensemble de lentilles divergentes et convergentes pour afficher la vitesse au loin ?", "options": ["L'affichage tête haute (HUD - Head-Up Display)", "Le chronotachygraphe mécanique", "L'autoradio Bluetooth"], "rep": "L'affichage tête haute (HUD - Head-Up Display)"},
            {"id": "qdtr2_2", "q": "Quel est le rôle du groupe optique comportant une lentille divergente dans un afficheur tête haute (HUD) de camion ou voiture ?", "options": ["Former une image virtuelle droite de la vitesse semblant flotter à 2 ou 3 mètres devant le pare-brise", "Projeter l'image sur le volant", "Éblouir le conducteur la nuit"], "rep": "Former une image virtuelle droite de la vitesse semblant flotter à 2 ou 3 mètres devant le pare-brise"},
            {"id": "qdtr2_3", "q": "Pourquoi projette-t-on une image virtuelle éloignée (à 2,5 m) plutôt que de regarder le tableau de bord à 60 cm ?", "options": ["Pour éviter à l'œil du conducteur d'avoir à refaire la mise au point (accommodation) entre la route et le compteur", "Pour économiser du carburant", "Pour agrandir le pare-brise"], "rep": "Pour éviter à l'œil du conducteur d'avoir à refaire la mise au point (accommodation) entre la route et le compteur"},
            {"id": "qdtr2_4", "q": "De quelle nature est l'image des chiffres de vitesse observée par le conducteur dans un système HUD ?", "options": ["Virtuelle et droite (à l'endroit)", "Réelle et renversée", "Floue sur les bords"], "rep": "Virtuelle et droite (à l'endroit)"},
            {"id": "qdtr2_5", "q": "Quel défaut visuel d'un conducteur nécessite le port de verres correcteurs divergents pour lire nettement les panneaux routiers au loin ?", "options": ["La myopie", "L'hypermétropie", "La presbytie"], "rep": "La myopie"},
            {"id": "qdtr2_6", "q": "Que risque un conducteur myope qui conduit de nuit sans ses lunettes à verres divergents ?", "options": ["Une perception tardive et floue des panneaux, des piétons et des distances de freinage", "Une vision trop perçante", "Un éblouissement par les feux rouges uniquement"], "rep": "Une perception tardive et floue des panneaux, des piétons et des distances de freinage"},
            {"id": "qdtr2_7", "q": "Comment agit le verre divergent devant l'œil myope du conducteur ?", "options": ["Il fait diverger légèrement les rayons entrants pour repousser l'image nette sur la rétine", "Il rapproche l'image devant le cristallin", "Il filtre les rayons infrarouges"], "rep": "Il fait diverger légèrement les rayons entrants pour repousser l'image nette sur la rétine"},
            {"id": "qdtr2_8", "q": "Si l'ordonnance optique d'un chauffeur indique une correction de -2,50 δ, quelle est la distance focale f' de ses verres divergents ?", "options": ["- 40 cm (-0,40 m)", "+ 40 cm (+0,40 m)", "- 2,50 m"], "rep": "- 40 cm (-0,40 m)"},
            {"id": "qdtr2_9", "q": "Pourquoi les lentilles divergentes modernes pour la conduite de nuit reçoivent-elles un traitement antireflet ?", "options": ["Pour supprimer les halos lumineux autour des phares arrivant en face et améliorer le contraste", "Pour teinter les verres en noir", "Pour augmenter le poids des lunettes"], "rep": "Pour supprimer les halos lumineux autour des phares arrivant en face et améliorer le contraste"},
            {"id": "qdtr2_10", "q": "Quelle relation relie la vergence C (en δ) et la distance focale f' (en m) du verre correcteur ?", "options": ["C = 1 / f'", "C = f' × 100", "C = 1 + f'"], "rep": "C = 1 / f'"},
        ],
        "trous": [
            ("1. L'affichage tête haute (HUD) projette une image ......... devant le véhicule.", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "dtr_t1"),
            ("2. L'œil du conducteur n'a pas besoin de modifier son ......... entre route et vitesse.", ["Choisir...", "accommodation", "diamètre"], "accommodation", "dtr_t2"),
            ("3. La ......... est le défaut visuel empêchant de voir nettement les panneaux au loin.", ["Choisir...", "myopie", "presbytie"], "myopie", "dtr_t3"),
            ("4. On corrige la myopie avec des verres de lentilles .........", ["Choisir...", "divergentes", "convergentes"], "divergentes", "dtr_t4"),
            ("5. Le verre divergent repousse l'image exactement sur la .........", ["Choisir...", "rétine", "cornée"], "rétine", "dtr_t5"),
            ("6. Une correction de -2,50 δ correspond à une focale f' = ......... cm.", ["Choisir...", "-40", "+40"], "-40", "dtr_t6"),
            ("7. Un traitement ......... élimine les halos des phares la nuit.", ["Choisir...", "antireflet", "polarisant"], "antireflet", "dtr_t7"),
            ("8. La vergence d'un verre correcteur de myope est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dtr_t8"),
            ("9. La formule liant vergence et focale est C = 1 / .........", ["Choisir...", "f'", "2"], "f'", "dtr_t9"),
            ("10. Le calcul des positions images repose sur la loi de .........", ["Choisir...", "Descartes", "Ohm"], "Descartes", "dtr_t10"),
        ]
    }
}


def mettre_a_jour_div_trans_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles divergentes adapté au Transport Routier."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        vergence_am = st.session_state.get("slider_dtr_s0", -18.0)
        angle_am = int(min(175, 65 + abs(vergence_am) * 4.5))
        x0, y0 = 210.0, 130.0

        ax.add_patch(patches.Rectangle((55, 85), 140, 90, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(125, 130, "POIDS LOURD\n(Angle mort latéral)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((x0, x0)), list((95, 165)), color="#38bdf8", lw=4)
        ax.text(x0, 82, f"Optique Divergente (C = {vergence_am:.0f} δ)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        dy_c = min(105.0, abs(vergence_am) * 4.4)
        ax.fill(list((x0, 560, 560)), list((y0, y0 - dy_c, y0 + dy_c)), color="#22c55e", alpha=0.22)
        ax.plot(list((x0, 560)), list((y0, y0 - dy_c)), color="#22c55e", lw=1.5, ls="--")
        ax.plot(list((x0, 560)), list((y0, y0 + dy_c)), color="#22c55e", lw=1.5, ls="--")
        ax.text(470, 130, "Zone cycliste\nsurveillée", color="#86efac", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.text(25, 18, "SÉCURITÉ POIDS LOURDS : DÉTECTION D'ANGLE MORT PAR OPTIQUE DIVERGENTE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence frontale : C = {vergence_am:.0f} δ  |  Champ latéral surveillé : {angle_am}° (Cyclistes visibles)", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dtr_mesure_courante = (f"C = {vergence_am:.0f} δ", f"Champ = {angle_am}°", "Image rétrécie", "ANGLE MORT OK")

    elif sujet_idx == 1:
        vergence_feu = st.session_state.get("slider_dtr_s1", -14.0)
        angle_diff = int(min(170, 55 + abs(vergence_feu) * 4.8))
        x0, y0 = 180.0, 130.0

        ax.add_patch(patches.Rectangle((65, 112), 45, 36, facecolor="#ef4444", edgecolor="white"))
        ax.text(87, 130, "LED AR", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((x0, x0)), list((55, 205)), color="#38bdf8", lw=4)
        ax.text(x0, 44, f"Diffuseur Divergent (C = {vergence_feu:.0f} δ)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        dy_end = min(105.0, abs(vergence_feu) * 4.5)
        ax.fill(list((x0, 560, 560)), list((y0 - 25, y0 - dy_end, y0 + dy_end)), color="#ef4444", alpha=0.25)
        for dy in [-25, -12, 12, 25]:
            ax.plot(list((110, x0)), list((y0 + dy, y0 + dy)), color="#fca5a5", lw=1.8)
            pente = (dy / 25.0) * (dy_end / 380.0)
            ax.annotate("", xy=(560, y0 + dy + pente * 380.0), xytext=(x0, y0 + dy), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))

        ax.text(25, 18, "SIGNALISATION ARRIÈRE : DIFFUSION GRAND-ANGLE PAR LENTILLE DIVERGENTE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence diffuseur : C = {vergence_feu:.0f} δ  |  Angle de visibilité latérale : {angle_diff}°", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dtr_mesure_courante = (f"C = {vergence_feu:.0f} δ", f"Angle = {angle_diff}°", "Diffusion large", "HOMOLOGUÉ")

    else:
        vergence_oeil = st.session_state.get("slider_dtr_s2", -2.5)
        focale_cm = 100.0 / vergence_oeil
        x0, y0 = 260.0, 130.0

        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x0, x0)), list((65, 195)), color="#38bdf8", lw=3.5)
        ax.text(x0, 52, f"Verre Correcteur Myope (C = {vergence_oeil:.2f} δ)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        ax.add_patch(patches.Circle((410, y0), 55, facecolor="#1e293b", edgecolor="#eab308", lw=2))
        ax.text(410, 62, "Œil du conducteur (Rétine à droite)", color="#fde047", fontsize=8, fontweight="bold", ha="center")

        for dy in [-32, 32]:
            ax.plot(list((40, x0)), list((y0 + dy, y0 + dy)), color="#22c55e", lw=1.8)
            dy_corn = dy * (1.0 + abs(vergence_oeil) * 0.08)
            ax.plot(list((x0, 360)), list((y0 + dy, y0 + dy_corn)), color="#22c55e", lw=1.8)
            ax.plot(list((360, 465)), list((y0 + dy_corn, y0)), color="#22c55e", lw=1.8)

        ax.text(25, 18, "VISION DU CONDUCTEUR : CORRECTION DE LA MYOPIE PAR VERRE DIVERGENT", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Correction : C = {vergence_oeil:.2f} δ  |  Focale f' = {focale_cm:.1f} cm  =>  Image des panneaux nette sur la rétine", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dtr_mesure_courante = (f"C = {vergence_oeil:.2f} δ", f"f' = {focale_cm:.1f} cm", "Foyer sur rétine", "VISION NETTE")

    return fig


def afficher_atelier_div_trans(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet Transport Routier ci-dessus.")
        return
    banque = BANQUES_DIV_TRANS[sujet_idx]
    cle_ordre = f"ordre_quiz_dtr_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Transport Routier (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"dtr_at6_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Transport Routier (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")


BANQUES_DIV_GEO = {
    0: {
        "questions": [
            {"id": "qdg0_1", "q": "Quel rôle joue la lentille divergente interne placée dans le tube optique d'une station totale ou d'un théodolite ?", "options": ["Assurer la mise au point interne (focalisation sur le réticule) et augmenter le grossissement", "Bloquer le faisceau infrarouge", "Inverser la gauche et la droite"], "rep": "Assurer la mise au point interne (focalisation sur le réticule) et augmenter le grossissement"},
            {"id": "qdg0_2", "q": "Comment appelle-t-on l'association optique composée d'un objectif convergent à l'avant et d'une lentille divergente à l'arrière (téléobjectif) ?", "options": ["Un système optique compact à longue distance focale équivalente", "Un microscope simple", "Un prisme de Porro"], "rep": "Un système optique compact à longue distance focale équivalente"},
            {"id": "qdg0_3", "q": "Quel avantage essentiel procure la mise au point interne par lentille divergente mobile pour un géomètre sur le terrain ?", "options": ["Le tube de la lunette reste court, parfaitement équilibré et étanche à l'eau et aux poussières", "La station fonctionne sans batterie", "Le trépied devient inutile"], "rep": "Le tube de la lunette reste court, parfaitement équilibré et étanche à l'eau et aux poussières"},
            {"id": "qdg0_4", "q": "Comment la lentille divergente interne modifie-t-elle le trajet des rayons convergents issus de l'objectif ?", "options": ["Elle réduit leur convergence et repousse le point focal exactement sur le plan du réticule", "Elle les fait diverger hors du tube", "Elle les colore en vert"], "rep": "Elle réduit leur convergence et repousse le point focal exactement sur le plan du réticule"},
            {"id": "qdg0_5", "q": "Lorsque le géomètre passe d'un prisme proche (15 m) à un prisme lointain (400 m), que fait la lentille divergente interne ?", "options": ["Elle se translate le long de l'axe optique grâce à la molette de mise au point", "Elle tourne de 90°", "Elle sort du tube optique"], "rep": "Elle se translate le long de l'axe optique grâce à la molette de mise au point"},
            {"id": "qdg0_6", "q": "Quel défaut optique des lentilles convergentes est corrigé par les lentilles divergentes en verre flint dans les doublets d'objectifs topographiques ?", "options": ["L'aberration chromatique (liserés colorés autour des mires et prismes)", "La pesanteur terrestre", "La réfraction atmosphérique"], "rep": "L'aberration chromatique (liserés colorés autour des mires et prismes)"},
            {"id": "qdg0_7", "q": "Quel est le signe de la vergence C et de la distance focale f' de la lentille divergente interne ?", "options": ["Négatif (C < 0 et f' < 0)", "Positif (C > 0 et f' > 0)", "Nul"], "rep": "Négatif (C < 0 et f' < 0)"},
            {"id": "qdg0_8", "q": "Quel instrument historique de topographie ou de reconnaissance utilise un objectif convergent et un oculaire divergent ?", "options": ["La lunette de Galilée (donnant directement une image droite)", "Le niveau à eau", "Le sextant à miroir"], "rep": "La lunette de Galilée (donnant directement une image droite)"},
            {"id": "qdg0_9", "q": "Pourquoi un choc violent faisant dévier l'axe de la lentille divergente mobile fausse-t-il les mesures angulaires de la station totale ?", "options": ["Il introduit une erreur de collimation horizontale (décalage entre l'axe optique et l'axe mécanique)", "Il vide la mémoire interne", "Il change la fréquence du GPS"], "rep": "Il introduit une erreur de collimation horizontale (décalage entre l'axe optique et l'axe mécanique)"},
            {"id": "qdg0_10", "q": "Comment corrige-t-on l'erreur de collimation d'une station totale sur le terrain ?", "options": ["Par une double visée (cercle gauche et cercle droit) ou une procédure de calibrage", "En nettoyant le trépied", "En changeant les piles"], "rep": "Par une double visée (cercle gauche et cercle droit) ou une procédure de calibrage"},
        ],
        "trous": [
            ("1. Les stations totales modernes utilisent une lentille ......... interne mobile.", ["Choisir...", "divergente", "plane"], "divergente", "dgeo_t1"),
            ("2. Ce dispositif assure la mise au point ......... en gardant un tube étanche.", ["Choisir...", "interne", "externe"], "interne", "dgeo_t2"),
            ("3. L'association convergent + divergent permet d'allonger la focale dans un tube .........", ["Choisir...", "court", "souple"], "court", "dgeo_t3"),
            ("4. La lentille divergente amène l'image nette exactement sur le .........", ["Choisir...", "réticule", "trépied"], "réticule", "dgeo_t4"),
            ("5. Les verres divergents en flint corrigent les aberrations .........", ["Choisir...", "chromatiques", "thermiques"], "chromatiques", "dgeo_t5"),
            ("6. La distance focale f' de la lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dgeo_t6"),
            ("7. La lunette de ......... utilise un oculaire divergent pour donner une image droite.", ["Choisir...", "Galilée", "Kepler"], "Galilée", "dgeo_t7"),
            ("8. Un décentrement optique crée une erreur de ......... horizontale.", ["Choisir...", "collimation", "pesanteur"], "collimation", "dgeo_t8"),
            ("9. On élimine cette erreur par une ......... visée (cercle gauche / cercle droit).", ["Choisir...", "double", "simple"], "double", "dgeo_t9"),
            ("10. Le calcul optique repose sur la loi de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "dgeo_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qdg1_1", "q": "Quel composant optique équipe l'émetteur d'un niveau laser rotatif de chantier ou d'un scanner 3D terrestre ?", "options": ["Une lentille divergente cylindrique (lentille de Powell) ou conique étalant le point laser en ligne ou en plan", "Un prisme opaque", "Une loupe convergente simple"], "rep": "Une lentille divergente cylindrique (lentille de Powell) ou conique étalant le point laser en ligne ou en plan"},
            {"id": "qdg1_2", "q": "Comment une lentille divergente cylindrique (ou lentille de Powell) transforme-t-elle un faisceau laser ponctuel ?", "options": ["Elle fait diverger le faisceau dans un seul plan pour projeter un trait laser rectiligne sur les murs et le sol", "Elle concentre le laser en un point microscopique", "Elle bloque le faisceau rouge"], "rep": "Elle fait diverger le faisceau dans un seul plan pour projeter un trait laser rectiligne sur les murs et le sol"},
            {"id": "qdg1_3", "q": "Quel avantage apporte une lentille de Powell divergente par rapport à une simple baguette cylindrique en verre ?", "options": ["Elle répartit l'intensité lumineuse de manière uniforme sur toute la longueur de la ligne laser", "Elle consomme deux fois moins de piles", "Elle transforme le laser rouge en vert"], "rep": "Elle répartit l'intensité lumineuse de manière uniforme sur toute la longueur de la ligne laser"},
            {"id": "qdg1_4", "q": "Dans un scanner laser 3D (LiDAR terrestre), pourquoi place-t-on un élargisseur de faisceau de Galilée (divergente + convergente) en sortie ?", "options": ["Pour réduire la divergence angulaire à longue distance et conserver un spot laser très fin à 100 mètres", "Pour colorer les façades des bâtiments", "Pour alourdir le scanner"], "rep": "Pour réduire la divergence angulaire à longue distance et conserver un spot laser très fin à 100 mètres"},
            {"id": "qdg1_5", "q": "Comment évolue la largeur du trait laser projeté sur un mur à 10 m si l'on utilise une lentille divergente de vergence plus négative ?", "options": ["La longueur de la ligne laser projetée s'agrandit (angle d'ouverture plus large)", "La ligne se rétrécit en un point", "Le laser s'éteint"], "rep": "La longueur de la ligne laser projetée s'agrandit (angle d'ouverture plus large)"},
            {"id": "qdg1_6", "q": "Quelle précaution de sécurité laser doit respecter le géomètre lors de l'utilisation d'un laser de nivellement à ligne divergente ?", "options": ["Ne jamais diriger le faisceau vers les yeux (classe 2 ou 3R) et placer le plan laser hors hauteur des yeux", "Regarder directement dans la lentille pour vérifier la diode", "Retirer la lentille divergente pour augmenter la puissance"], "rep": "Ne jamais diriger le faisceau vers les yeux (classe 2 ou 3R) et placer le plan laser hors hauteur des yeux"},
            {"id": "qdg1_7", "q": "Pourquoi un faisceau laser étalé en ligne par une lentille divergente est-il moins dangereux pour l'œil qu'un faisceau ponctuel de même puissance ?", "options": ["Parce que la puissance totale est répartie sur toute la longueur du trait (densité d'énergie plus faible)", "Parce que la lentille absorbe tout le laser", "Parce que le laser devient infrarouge"], "rep": "Parce que la puissance totale est répartie sur toute la longueur du trait (densité d'énergie plus faible)"},
            {"id": "qdg1_8", "q": "Si un faisceau laser traverse une lentille divergente de focale f' = -20 mm (-0,020 m), quelle est sa vergence C ?", "options": ["- 50 dioptries (δ)", "+ 50 dioptries (δ)", "- 20 dioptries (δ)"], "rep": "- 50 dioptries (δ)"},
            {"id": "qdg1_9", "q": "Quelle surface de référence matérialise un laser lignes muni d'une lentille divergente horizontale et d'une verticale ?", "options": ["Deux plans orthogonaux (un plan horizontal de nivellement et un plan vertical d'alignement)", "Une sphère en 3D", "Un cercle au plafond"], "rep": "Deux plans orthogonaux (un plan horizontal de nivellement et un plan vertical d'alignement)"},
            {"id": "qdg1_10", "q": "Quelle loi de l'optique gouverne l'étalement angulaire du faisceau à travers la lentille divergente ?", "options": ["La loi de réfraction de Snell-Descartes", "La loi d'Ohm", "Le principe d'Archimède"], "rep": "La loi de réfraction de Snell-Descartes"},
        ],
        "trous": [
            ("1. Un laser de chantier utilise une lentille ......... cylindrique pour tracer une ligne.", ["Choisir...", "divergente", "plane"], "divergente", "dgeo_t1"),
            ("2. La lentille de ......... assure une luminosité uniforme sur tout le trait laser.", ["Choisir...", "Powell", "Newton"], "Powell", "dgeo_t2"),
            ("3. Le faisceau ponctuel s'......... dans un plan pour former une ligne droite.", ["Choisir...", "étale", "concentre"], "étale", "dgeo_t3"),
            ("4. Plus la vergence C est négative, plus l'angle d'ouverture est .........", ["Choisir...", "large", "étroit"], "large", "dgeo_t4"),
            ("5. Une focale f' = -20 mm correspond à une vergence de ......... dioptries.", ["Choisir...", "-50", "+50"], "-50", "dgeo_t5"),
            ("6. L'étalement réduit la ......... de puissance par rapport à un point fixe.", ["Choisir...", "densité", "couleur"], "densité", "dgeo_t6"),
            ("7. Un scanner 3D utilise un élargisseur de ......... (divergente + convergente).", ["Choisir...", "Galilée", "Kepler"], "Galilée", "dgeo_t7"),
            ("8. Il ne faut jamais diriger le faisceau vers les .........", ["Choisir...", "yeux", "murs"], "yeux", "dgeo_t8"),
            ("9. La distance focale f' d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dgeo_t9"),
            ("10. La déviation des rayons obéit à la loi de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "dgeo_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qdg2_1", "q": "Dans les objectifs grand-angle utilisés en photogrammétrie terrestre ou par drone pour relever des façades dans des rues étroites, quel est le rôle de la lentille divergente frontale ?", "options": ["Augmenter l'angle de champ (architecture rétrofocus) pour photographier toute la façade avec peu de recul", "Zoomer sur le toit uniquement", "Transformer la photo en noir et blanc"], "rep": "Augmenter l'angle de champ (architecture rétrofocus) pour photographier toute la façade avec peu de recul"},
            {"id": "qdg2_2", "q": "Comment appelle-t-on un objectif photogrammétrique doté d'une lentille divergente à l'avant permettant de conserver un espace suffisant devant le capteur ?", "options": ["Un objectif rétrofocus (grand-angle)", "Un télescope de Newton", "Un microscope optique"], "rep": "Un objectif rétrofocus (grand-angle)"},
            {"id": "qdg2_3", "q": "Quel défaut géométrique induit par la lentille divergente frontale le géomètre doit-il impérativement calibrer avant un levé 3D ?", "options": ["La distorsion radiale en barillet sur les bords du capteur", "La température du capteur", "La vitesse du vent"], "rep": "La distorsion radiale en barillet sur les bords du capteur"},
            {"id": "qdg2_4", "q": "Quelle image virtuelle la lentille divergente frontale forme-t-elle avant les lentilles convergentes de focalisation ?", "options": ["Une image virtuelle, droite et rétrécie de la scène", "Une image réelle et agrandie", "Une image inversée"], "rep": "Une image virtuelle, droite et rétrécie de la scène"},
            {"id": "qdg2_5", "q": "Pourquoi le calibrage de la distorsion d'une lentille divergente grand-angle est-il crucial en topographie ?", "options": ["Pour que les arêtes droites d'un bâtiment n'apparaissent pas courbées sur le plan côté", "Pour augmenter le nombre de pixels", "Pour économiser la batterie du drone"], "rep": "Pour que les arêtes droites d'un bâtiment n'apparaissent pas courbées sur le plan côté"},
            {"id": "qdg2_6", "q": "Quelle est la caractéristique géométrique d'une lentille ménisque divergente utilisée en photogrammétrie ?", "options": ["Ses bords sont plus épais que son centre (vergence C < 0)", "Son centre est plus épais que ses bords", "Ses deux faces sont planes"], "rep": "Ses bords sont plus épais que son centre (vergence C < 0)"},
            {"id": "qdg2_7", "q": "Dans un objectif grand-angle, comment évolue le champ angulaire couvert lorsque la distance focale équivalente diminue (ex : 14 mm au lieu de 35 mm) ?", "options": ["Le champ angulaire couvert augmente fortement", "Le champ angulaire diminue", "Le champ reste identique"], "rep": "Le champ angulaire couvert augmente fortement"},
            {"id": "qdg2_8", "q": "Quel paramètre interne le logiciel de photogrammétrie détermine-t-il lors du calibrage de l'objectif ?", "options": ["La distance principale (focale calibrée), le point principal d'autocollimation et les coefficients de distorsion", "La marque du trépied", "L'altitude du soleil"], "rep": "La distance principale (focale calibrée), le point principal d'autocollimation et les coefficients de distorsion"},
            {"id": "qdg2_9", "q": "Quel est le signe du grandissement γ de l'image virtuelle donnée par la lentille divergente frontale ?", "options": ["Positif et compris entre 0 et 1 (0 < γ < 1)", "Négatif (-2)", "Supérieur à +10"], "rep": "Positif et compris entre 0 et 1 (0 < γ < 1)"},
            {"id": "qdg2_10", "q": "Quelle loi optique régit le tracé des rayons à travers l'ensemble des lentilles divergentes et convergentes de l'objectif ?", "options": ["La loi de réfraction de Snell-Descartes", "La loi d'Ohm", "Le théorème de Bernoulli"], "rep": "La loi de réfraction de Snell-Descartes"},
        ],
        "trous": [
            ("1. Un objectif grand-angle photogrammétrique place une lentille ......... à l'avant.", ["Choisir...", "divergente", "plane"], "divergente", "dgeo_t1"),
            ("2. Cette architecture optique s'appelle un montage .........", ["Choisir...", "rétrofocus", "afocal"], "rétrofocus", "dgeo_t2"),
            ("3. Elle permet de photographier une façade entière avec peu de .........", ["Choisir...", "recul", "lumière"], "recul", "dgeo_t3"),
            ("4. Le logiciel doit corriger la ......... radiale en barillet.", ["Choisir...", "distorsion", "réflexion"], "distorsion", "dgeo_t4"),
            ("5. L'image virtuelle formée par la lentille divergente est droite et .........", ["Choisir...", "rétrécie", "agrandie"], "rétrécie", "dgeo_t5"),
            ("6. Les bords d'une lentille divergente sont plus ......... que son centre.", ["Choisir...", "épais", "minces"], "épais", "dgeo_t6"),
            ("7. La vergence C d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dgeo_t7"),
            ("8. Le grandissement vérifie toujours 0 < γ < .........", ["Choisir...", "1", "10"], "1", "dgeo_t8"),
            ("9. Le calibrage garantit que les murs droits restent ......... sur le plan.", ["Choisir...", "droits", "courbes"], "droits", "dgeo_t9"),
            ("10. Le calcul des rayons repose sur la loi de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "dgeo_t10"),
        ]
    }
}


def mettre_a_jour_div_geo_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles divergentes adapté au Géomètre Topographe."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        pos_int_mm = st.session_state.get("slider_dgeo_s0", 60.0)
        cible_mm = 60.0
        x0, y0 = 150.0, 125.0
        x_div = x0 + pos_int_mm * 2.8
        x_ret = 480.0

        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x0, x0)), list((45, 205)), color="#22c55e", lw=4)
        ax.text(x0, 34, "Objectif Station Totale", color="#86efac", fontsize=8, fontweight="bold", ha="center")

        ax.plot(list((x_div, x_div)), list((70, 180)), color="#38bdf8", lw=3)
        ax.text(x_div, 58, f"Lentille Divergente\n({pos_int_mm:.0f} mm)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((x_ret, x_ret)), list((80, 170)), color="#eab308", lw=3)
        ax.text(x_ret, 68, "Réticule", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        ecart = abs(pos_int_mm - cible_mm)
        for dy in [-45, 45]:
            ax.plot(list((35, x0)), list((y0 + dy, y0 + dy)), color="#ef4444", lw=1.8)
            dy_mid = dy * 0.52
            ax.plot(list((x0, x_div)), list((y0 + dy, y0 + dy_mid)), color="#ef4444", lw=1.8)
            y_end = y0 if ecart <= 1.0 else (y0 + (dy / 45.0) * (pos_int_mm - cible_mm) * 1.4)
            ax.plot(list((x_div, x_ret)), list((y0 + dy_mid, y_end)), color="#ef4444", lw=1.8)

        statut = "FOCALISATION STATION TOTALE OK : Image nette sur la croix du réticule !" if ecart <= 1.0 else f"DÉFOCALISÉ (Écart {ecart:.0f} mm) : Réglez la lentille interne à 60 mm."
        c_stat = "#22c55e" if ecart <= 1.0 else "#ef4444"
        ax.text(25, 18, "STATION TOTALE : MISE AU POINT INTERNE PAR LENTILLE DIVERGENTE MOBILE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.dgeo_mesure_courante = (f"Pos = {pos_int_mm:.0f} mm", "Cible = 60 mm", f"Écart = {ecart:.0f} mm", "VISÉE OK" if ecart <= 1.0 else "PARALLAXE")

    elif sujet_idx == 1:
        vergence_pow = st.session_state.get("slider_dgeo_s1", -35.0)
        dist_mur_m = st.session_state.get("slider_dgeo_d_s1", 10.0)
        angle_rad = math.radians(min(120, 30 + abs(vergence_pow) * 1.6))
        longueur_ligne_m = 2.0 * dist_mur_m * math.tan(angle_rad / 2.0)

        x0, y0 = 150.0, 130.0
        ax.add_patch(patches.Rectangle((55, 115), 40, 30, facecolor="#ef4444", edgecolor="white"))
        ax.text(75, 130, "Laser", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((x0, x0)), list((65, 195)), color="#38bdf8", lw=3.5)
        ax.text(x0, 52, f"Lentille Powell (C = {vergence_pow:.0f} δ)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        xm = 250.0 + (dist_mur_m / 25.0) * 280.0
        dy_m = min(95.0, (longueur_ligne_m / 40.0) * 95.0)
        ax.plot(list((95, x0)), list((y0, y0)), color="#ef4444", lw=2.5)
        ax.fill(list((x0, xm, xm)), list((y0, y0 - dy_m, y0 + dy_m)), color="#ef4444", alpha=0.25)
        ax.plot(list((xm, xm)), list((y0 - dy_m, y0 + dy_m)), color="#22c55e", lw=4)
        ax.text(xm + 8, y0, f"Mur ({dist_mur_m:.0f} m)\nLigne = {longueur_ligne_m:.1f} m", color="#86efac", fontsize=7.5, fontweight="bold", va="center")

        ax.text(25, 18, "NIVELLEMENT LASER : ÉTALEMENT EN LIGNE PAR LENTILLE DIVERGENTE DE POWELL", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence : C = {vergence_pow:.0f} δ | Distance mur : D = {dist_mur_m:.0f} m  =>  Longueur du trait laser : L = {longueur_ligne_m:.1f} m", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dgeo_mesure_courante = (f"C = {vergence_pow:.0f} δ", f"Mur = {dist_mur_m:.0f} m", f"Ligne = {longueur_ligne_m:.1f} m", "TRAIT UNIFORME")

    else:
        vergence_rf = st.session_state.get("slider_dgeo_s2", -20.0)
        champ_rf = int(min(140, 60 + abs(vergence_rf) * 2.8))
        x0, y0 = 180.0, 130.0

        ax.add_patch(patches.Rectangle((75, 100), 90, 60, facecolor="#1e3a8a", edgecolor="#38bdf8", lw=1.5))
        ax.text(120, 130, "Chambre\nRétrofocus", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((x0, x0)), list((85, 175)), color="#38bdf8", lw=4)
        ax.text(x0, 74, f"Divergente Avant (C = {vergence_rf:.0f} δ)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        dy_f = min(100.0, abs(vergence_rf) * 3.5)
        ax.fill(list((x0, 520, 520)), list((y0, y0 - dy_f, y0 + dy_f)), color="#22c55e", alpha=0.22)
        ax.plot(list((520, 520)), list((30, 230)), color="#eab308", lw=4)
        ax.text(532, 130, "Façade\nrelevée", color="#fde047", fontsize=8, fontweight="bold", va="center")

        ax.text(25, 18, "PHOTOGRAMMÉTRIE ARCHITECTURALE : OBJECTIF GRAND-ANGLE RÉTROFOCUS", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence frontale : C = {vergence_rf:.0f} δ  |  Angle de champ couvert : {champ_rf}° (Relevé sans recul)", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dgeo_mesure_courante = (f"C = {vergence_rf:.0f} δ", f"Champ = {champ_rf}°", "Rétrofocus", "FAÇADE COMPLÈTE")

    return fig


def afficher_atelier_div_geo(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort une mission Géomètre ci-dessus.")
        return
    banque = BANQUES_DIV_GEO[sujet_idx]
    cle_ordre = f"ordre_quiz_dgeo_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Géomètre Topographe (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"dgeo_at7_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Géomètre Topographe (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")






BANQUES_DIV_TP = {
    0: {
        "questions": [
            {"id": "qdtp0_1", "q": "Quel rôle joue la lentille divergente intégrée au dôme d'une balise lumineuse de chantier (gyrophare LED) ?", "options": ["Élargir et répartir le faisceau de la LED sur 360° autour de la zone de travaux", "Concentrer toute la lumière en un seul point au sol", "Bloquer la lumière infrarouge"], "rep": "Élargir et répartir le faisceau de la LED sur 360° autour de la zone de travaux"},
            {"id": "qdtp0_2", "q": "Comment ressortent les rayons lumineux d'une LED après avoir traversé une lentille mince divergente ?", "options": ["Ils s'écartent de l'axe optique (faisceau divergent large)", "Ils deviennent strictement parallèles sur 10 km", "Ils convergent en un point brûlant"], "rep": "Ils s'écartent de l'axe optique (faisceau divergent large)"},
            {"id": "qdtp0_3", "q": "Quel est le signe de la distance focale f' et de la vergence C d'une lentille divergente de balise TP ?", "options": ["Négatif (f' < 0 et C < 0)", "Positif (f' > 0 et C > 0)", "Nul"], "rep": "Négatif (f' < 0 et C < 0)"},
            {"id": "qdtp0_4", "q": "Pourquoi cherche-t-on à faire diverger la lumière sur un cône ou une barrière de chantier plutôt que de créer un rayon laser étroit ?", "options": ["Pour que le signal lumineux soit visible sous tous les angles par les automobilistes et les engins", "Pour économiser le plastique du cône", "Pour chauffer l'enrobé bitumineux"], "rep": "Pour que le signal lumineux soit visible sous tous les angles par les automobilistes et les engins"},
            {"id": "qdtp0_5", "q": "Comment évolue l'angle d'ouverture du faisceau lumineux lorsque la vergence C devient plus négative (ex : -20 δ au lieu de -5 δ) ?", "options": ["L'angle de divergence augmente : le faisceau éclaire une zone encore plus large", "Le faisceau devient plus étroit", "La lumière change de couleur"], "rep": "L'angle de divergence augmente : le faisceau éclaire une zone encore plus large"},
            {"id": "qdtp0_6", "q": "Où semble provenir le faisceau émergent d'une lentille divergente éclairée par des rayons parallèles ?", "options": ["De son foyer image virtuel F' situé en amont", "De son foyer objet F", "Du sol de la tranchée"], "rep": "De son foyer image virtuel F' situé en amont"},
            {"id": "qdtp0_7", "q": "Quel matériau polymère transparent et résistant aux chocs utilise-t-on pour mouler les lentilles divergentes de balisage TP ?", "options": ["Le polycarbonate (PC) ou le PMMA", "Le verre cristal fragile", "La fonte grise"], "rep": "Le polycarbonate (PC) ou le PMMA"},
            {"id": "qdtp0_8", "q": "Quel inconvénient optique accompagne un très fort élargissement du faisceau par une lentille divergente ?", "options": ["L'intensité lumineuse par unité de surface diminue avec la distance (il faut une LED puissante)", "La batterie se recharge toute seule", "La lentille devient opaque"], "rep": "L'intensité lumineuse par unité de surface diminue avec la distance (il faut une LED puissante)"},
            {"id": "qdtp0_9", "q": "Si la lentille divergente d'un feu de chantier a une distance focale f' = -10 cm (-0,10 m), quelle est sa vergence C ?", "options": ["- 10 dioptries (δ)", "+ 10 dioptries (δ)", "- 0,10 dioptrie (δ)"], "rep": "- 10 dioptries (δ)"},
            {"id": "qdtp0_10", "q": "Quelle loi fondamentale de l'optique régit la déviation des rayons vers l'extérieur à la traversée de la lentille divergente ?", "options": ["La loi de réfraction de Snell-Descartes", "La loi d'Ohm", "Le théorème de Pythagore"], "rep": "La loi de réfraction de Snell-Descartes"},
        ],
        "trous": [
            ("1. Les balises de chantier utilisent une lentille ......... pour diffuser la lumière.", ["Choisir...", "divergente", "convergente"], "divergente", "dtp_t1"),
            ("2. Les rayons lumineux ......... en s'écartant de l'axe optique.", ["Choisir...", "divergent", "convergent"], "divergent", "dtp_t2"),
            ("3. Le faisceau large assure une visibilité sous tous les .........", ["Choisir...", "angles", "mètres"], "angles", "dtp_t3"),
            ("4. La distance focale f' d'une lentille divergente est toujours .........", ["Choisir...", "négative", "positive"], "négative", "dtp_t4"),
            ("5. Plus la vergence C est négative, plus l'angle d'ouverture est .........", ["Choisir...", "large", "étroit"], "large", "dtp_t5"),
            ("6. Les rayons émergents semblent provenir du foyer image virtuel .........", ["Choisir...", "F'", "F"], "F'", "dtp_t6"),
            ("7. Les dômes de chantier sont moulés en ......... résistant aux chocs.", ["Choisir...", "polycarbonate", "céramique"], "polycarbonate", "dtp_t7"),
            ("8. Une focale f' = -10 cm correspond à une vergence de ......... dioptries.", ["Choisir...", "-10", "+10"], "-10", "dtp_t8"),
            ("9. Les bords d'une lentille divergente sont plus ......... que son centre.", ["Choisir...", "épais", "minces"], "épais", "dtp_t9"),
            ("10. La déviation des rayons obéit à la loi de réfraction de .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "dtp_t10"),
        ]
    },
    1: {
        "questions": [
            {"id": "qdtp1_1", "q": "Quel type d'objectif optique équipe les caméras de recul et de sécurité d'angle mort sur les pelles hydrauliques et tombereaux TP ?", "options": ["Un objectif grand-angle rétrofocus comportant une lentille divergente frontale", "Un téléobjectif astronomique", "Une vitre plane opaque"], "rep": "Un objectif grand-angle rétrofocus comportant une lentille divergente frontale"},
            {"id": "qdtp1_2", "q": "Quel est le rôle de la lentille divergente placée à l'avant d'un objectif grand-angle d'engin de chantier ?", "options": ["Capturer un champ de vision très large (130° à 170°) autour de l'engin pour supprimer les angles morts", "Zoomer sur un écrou à 500 mètres", "Filtrer les rayons ultraviolets"], "rep": "Capturer un champ de vision très large (130° à 170°) autour de l'engin pour supprimer les angles morts"},
            {"id": "qdtp1_3", "q": "Quelle image intermédiaire la lentille divergente frontale forme-t-elle avant le groupe convergent de l'objectif ?", "options": ["Une image virtuelle, droite et rétrécie", "Une image réelle et agrandie", "Une ombre portée"], "rep": "Une image virtuelle, droite et rétrécie"},
            {"id": "qdtp1_4", "q": "Quel effet visuel caractéristique (distorsion) produit un objectif grand-angle très divergent sur les lignes droites proches des bords de l'écran ?", "options": ["Une courbure des lignes droites (distorsion en barillet / effet fisheye)", "Une inversion des couleurs rouge et bleu", "Un flou total au centre"], "rep": "Une courbure des lignes droites (distorsion en barillet / effet fisheye)"},
            {"id": "qdtp1_5", "q": "Pourquoi le conducteur d'un tombereau TP doit-il être vigilant lorsqu'il évalue une distance sur l'écran de sa caméra grand-angle ?", "options": ["La lentille divergente rétrécit les objets : les obstacles paraissent plus éloignés qu'ils ne le sont en réalité", "Les obstacles paraissent 10 fois plus proches", "L'image est décalée de 5 secondes"], "rep": "La lentille divergente rétrécit les objets : les obstacles paraissent plus éloignés qu'ils ne le sont en réalité"},
            {"id": "qdtp1_6", "q": "Comment appelle-t-on l'architecture optique associant une lentille divergente à l'avant et un groupe convergent à l'arrière ?", "options": ["Un objectif rétrofocus (grand-angle)", "Un télescope de Newton", "Un microscope simple"], "rep": "Un objectif rétrofocus (grand-angle)"},
            {"id": "qdtp1_7", "q": "Dans la simulation de caméra d'engin TP, comment évolue la largeur de la zone surveillée derrière la pelle si la vergence frontale passe de -8 δ à -22 δ ?", "options": ["La zone surveillée s'élargit fortement et élimine l'angle mort arrière", "La zone surveillée se réduit à un point", "La caméra s'éteint"], "rep": "La zone surveillée s'élargit fortement et élimine l'angle mort arrière"},
            {"id": "qdtp1_8", "q": "Quel dispositif d'entretien équipe les caméras grand-angle des engins de terrassement travaillant dans la boue ?", "options": ["Une buse de lavage haute pression ou un volet motorisé protégeant la lentille frontale", "Un essuie-glace en métal", "Un chauffage à 500 °C"], "rep": "Une buse de lavage haute pression ou un volet motorisé protégeant la lentille frontale"},
            {"id": "qdtp1_9", "q": "Quel est le signe du grandissement produit par la lentille divergente frontale sur l'image virtuelle intermédiaire ?", "options": ["Positif et inférieur à 1 (0 < γ < 1)", "Négatif (-2)", "Supérieur à +5"], "rep": "Positif et inférieur à 1 (0 < γ < 1)"},
            {"id": "qdtp1_10", "q": "Quel système moderne assemble les images de 4 caméras grand-angle divergentes autour d'un engin TP ?", "options": ["La vision panoramique 360° (Bird View / vue aérienne reconstituée)", "Le radar Doppler météo", "Le niveau laser rotatif"], "rep": "La vision panoramique 360° (Bird View / vue aérienne reconstituée)"},
        ],
        "trous": [
            ("1. Les caméras grand-angle d'engins TP intègrent une lentille ......... à l'avant.", ["Choisir...", "divergente", "plane"], "divergente", "dtp_t1"),
            ("2. Cette lentille permet d'élargir le ......... de vision jusqu'à 170°.", ["Choisir...", "champ", "rayon"], "champ", "dtp_t2"),
            ("3. Elle supprime les angles ......... autour des pelles et tombereaux.", ["Choisir...", "morts", "droits"], "morts", "dtp_t3"),
            ("4. L'image virtuelle formée par la lentille divergente est droite et .........", ["Choisir...", "rétrécie", "agrandie"], "rétrécie", "dtp_t4"),
            ("5. Le conducteur doit savoir que les objets paraissent plus ......... sur l'écran.", ["Choisir...", "éloignés", "proches"], "éloignés", "dtp_t5"),
            ("6. La déformation courbe des bords de l'image s'appelle la distorsion en .........", ["Choisir...", "barillet", "coussinet"], "barillet", "dtp_t6"),
            ("7. Un objectif combinant divergent avant et convergent arrière est dit .........", ["Choisir...", "rétrofocus", "afocal"], "rétrofocus", "dtp_t7"),
            ("8. Quatre caméras grand-angle permettent une vision panoramique à .........°.", ["Choisir...", "360", "90"], "360", "dtp_t8"),
            ("9. La lentille divergente possède une vergence C toujours .........", ["Choisir...", "négative", "positive"], "négative", "dtp_t9"),
            ("10. Le grandissement de la lentille divergente vérifie 0 < γ < .........", ["Choisir...", "1", "10"], "1", "dtp_t10"),
        ]
    },
    2: {
        "questions": [
            {"id": "qdtp2_1", "q": "Dans un niveau optique ou un théodolite de chantier, quel est le rôle de la lentille divergente interne placée entre l'objectif et le réticule ?", "options": ["Assurer la mise au point interne (focalisation) et allonger la distance focale sans rallonger le tube", "Bloquer la lumière du soleil", "Inverser les graduations de la mire"], "rep": "Assurer la mise au point interne (focalisation) et allonger la distance focale sans rallonger le tube"},
            {"id": "qdtp2_2", "q": "Comment appelle-t-on une lunette de chantier dont la longueur du tube reste fixe lors de la mise au point grâce au déplacement d'une lentille divergente interne ?", "options": ["Une lunette à mise au point interne (étanche aux poussières et à la pluie)", "Un télescope à miroir liquide", "Une loupe binoculaire"], "rep": "Une lunette à mise au point interne (étanche aux poussières et à la pluie)"},
            {"id": "qdtp2_3", "q": "Quel avantage majeur procure la mise au point interne par lentille divergente mobile sur un chantier TP poussiéreux ou pluvieux ?", "options": ["Le tube optique reste totalement hermétique : aucune poussière ni humidité ne pénètre dans l'instrument", "L'instrument pèse 20 kg de plus", "Il fonctionne sans trépied"], "rep": "Le tube optique reste totalement hermétique : aucune poussière ni humidité ne pénètre dans l'instrument"},
            {"id": "qdtp2_4", "q": "Quel est l'effet optique de la lentille divergente interne sur le faisceau convergent issu de l'objectif ?", "options": ["Elle diminue la convergence du faisceau pour l'amener exactement sur le plan du réticule", "Elle dévie le faisceau à 90° vers le sol", "Elle bloque les rayons rouges"], "rep": "Elle diminue la convergence du faisceau pour l'amener exactement sur le plan du réticule"},
            {"id": "qdtp2_5", "q": "Que se passe-t-il lorsque le chef de chantier tourne la molette de mise au point pour viser une mire plus proche ?", "options": ["La lentille divergente interne se déplace le long de l'axe optique pour maintenir l'image nette sur le réticule", "L'objectif avant tombe", "La distance focale de l'objectif devient négative"], "rep": "La lentille divergente interne se déplace le long de l'axe optique pour maintenir l'image nette sur le réticule"},
            {"id": "qdtp2_6", "q": "Quel type de combinaison optique (téléobjectif) associe une lentille convergente à l'avant et une lentille divergente à l'arrière ?", "options": ["Un système optique compact à longue distance focale équivalente", "Un prisme de Porro", "Un miroir plan"], "rep": "Un système optique compact à longue distance focale équivalente"},
            {"id": "qdtp2_7", "q": "Si la molette de mise au point est grippée et bloque la lentille divergente interne, quel défaut apparaît dans la lunette ?", "options": ["L'image de la mire est floue et présente une erreur de parallaxe", "L'image devient 100 fois plus lumineuse", "Le niveau à bulle se vide"], "rep": "L'image de la mire est floue et présente une erreur de parallaxe"},
            {"id": "qdtp2_8", "q": "Quel traitement de surface applique-t-on sur les faces de la lentille divergente interne pour éviter les pertes de lumière ?", "options": ["Un traitement antireflet multicouche", "Une couche de peinture noire", "Un vernis opaque"], "rep": "Un traitement antireflet multicouche"},
            {"id": "qdtp2_9", "q": "Quel est le signe de la distance focale f' de cette lentille interne de mise au point ?", "options": ["Négatif (f' < 0)", "Positif (f' > 0)", "Nul"], "rep": "Négatif (f' < 0)"},
            {"id": "qdtp2_10", "q": "Quelle loi optique régit le trajet des rayons à travers l'objectif convergent puis la lentille divergente mobile ?", "options": ["La relation de conjugaison de Descartes appliquée successivement aux deux lentilles", "La loi d'Ohm", "Le principe de Pascal"], "rep": "La relation de conjugaison de Descartes appliquée successivement aux deux lentilles"},
        ],
        "trous": [
            ("1. Les niveaux optiques modernes utilisent une lentille ......... interne mobile.", ["Choisir...", "divergente", "plane"], "divergente", "dtp_t1"),
            ("2. Ce système permet une mise au point ......... sans allonger le tube.", ["Choisir...", "interne", "externe"], "interne", "dtp_t2"),
            ("3. Le tube fermé protège l'optique contre la ......... et la pluie du chantier.", ["Choisir...", "poussière", "lumière"], "poussière", "dtp_t3"),
            ("4. La lentille divergente repousse le foyer pour amener l'image sur le .........", ["Choisir...", "réticule", "trépied"], "réticule", "dtp_t4"),
            ("5. En tournant la ......... latérale, on déplace la lentille divergente.", ["Choisir...", "molette", "nivelle"], "molette", "dtp_t5"),
            ("6. L'association convergent + divergent permet un tube court et .........", ["Choisir...", "compact", "souple"], "compact", "dtp_t6"),
            ("7. Si la lentille interne est mal réglée, il apparaît une erreur de .........", ["Choisir...", "parallaxe", "pesanteur"], "parallaxe", "dtp_t7"),
            ("8. Un traitement ......... évite les reflets parasites à l'intérieur du tube.", ["Choisir...", "antireflet", "opaque"], "antireflet", "dtp_t8"),
            ("9. La lentille divergente interne possède une vergence C .........", ["Choisir...", "négative", "positive"], "négative", "dtp_t9"),
            ("10. Le calcul des positions images repose sur la loi de .........", ["Choisir...", "Descartes", "Joule"], "Descartes", "dtp_t10"),
        ]
    }
}


def mettre_a_jour_div_tp_matplotlib(sujet_idx):
    """Banc d'essai optique lentilles divergentes adapté aux Travaux Publics."""
    fig, ax = plt.subplots(figsize=(12, 6.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 250)
    ax.invert_yaxis()
    ax.axis("off")

    if sujet_idx == 0:
        vergence_bal = st.session_state.get("slider_dtp_s0", -12.0)
        angle_ouv = int(min(170, 50 + abs(vergence_bal) * 5.0))
        x0, y0 = 180.0, 130.0

        ax.add_patch(patches.Rectangle((60, 112), 45, 36, facecolor="#eab308", edgecolor="white"))
        ax.text(82, 130, "LED TP", color="#0f172a", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((x0, x0)), list((55, 205)), color="#38bdf8", lw=4)
        ax.text(x0, 44, f"Lentille Divergente (C = {vergence_bal:.0f} δ)", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        dy_end = min(105.0, abs(vergence_bal) * 4.5)
        ax.fill(list((x0, 560, 560)), list((y0 - 25, y0 - dy_end, y0 + dy_end)), color="#f59e0b", alpha=0.25)
        for dy in [-25, -12, 12, 25]:
            ax.plot(list((105, x0)), list((y0 + dy, y0 + dy)), color="#fde047", lw=1.8)
            pente = (dy / 25.0) * (dy_end / 380.0)
            ax.annotate("", xy=(560, y0 + dy + pente * 380.0), xytext=(x0, y0 + dy), arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2))

        ax.text(25, 18, "SIGNALISATION DE CHANTIER : ÉLARGISSEMENT DU FAISCEAU PAR LENTILLE DIVERGENTE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence C = {vergence_bal:.0f} δ  |  Ouverture du faisceau de signalisation : {angle_ouv}°", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dtp_mesure_courante = (f"C = {vergence_bal:.0f} δ", f"Ouverture = {angle_ouv}°", "Faisceau large", "VISIBILITÉ 360°")

    elif sujet_idx == 1:
        vergence_cam = st.session_state.get("slider_dtp_s1", -16.0)
        champ_ar = int(min(175, 65 + abs(vergence_cam) * 4.5))
        x0, y0 = 220.0, 130.0

        ax.add_patch(patches.Rectangle((60, 85), 145, 90, facecolor="#eab308", edgecolor="white", lw=1.5))
        ax.text(132, 130, "TOMBEREAU TP\n(Marche arrière)", color="#0f172a", fontsize=8, fontweight="bold", ha="center", va="center")

        ax.plot(list((x0, x0)), list((95, 165)), color="#38bdf8", lw=4)
        ax.text(x0, 82, f"Caméra Grand-Angle (C = {vergence_cam:.0f} δ)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        dy_c = min(105.0, abs(vergence_cam) * 4.5)
        ax.fill(list((x0, 560, 560)), list((y0, y0 - dy_c, y0 + dy_c)), color="#22c55e", alpha=0.22)
        ax.plot(list((x0, 560)), list((y0, y0 - dy_c)), color="#22c55e", lw=1.5, ls="--")
        ax.plot(list((x0, 560)), list((y0, y0 + dy_c)), color="#22c55e", lw=1.5, ls="--")

        ax.text(25, 18, "SÉCURITÉ ENGINS TP : CAMÉRA DE RECUL GRAND-ANGLE DIVERGENTE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, f"Vergence frontale : C = {vergence_cam:.0f} δ  |  Champ arrière couvert : {champ_ar}° (Angles morts éliminés)", color="#22c55e", fontsize=8, fontweight="bold")
        st.session_state.dtp_mesure_courante = (f"C = {vergence_cam:.0f} δ", f"Champ = {champ_ar}°", "Rétrofocus", "SÉCURITÉ OK")

    else:
        pos_interne_mm = st.session_state.get("slider_dtp_s2", 45.0)
        cible_mm = 45.0
        x0, y0 = 160.0, 130.0
        x_div = x0 + pos_interne_mm * 3.0
        x_ret = 470.0

        ax.plot(list((20, 580)), list((y0, y0)), color="#64748b", lw=1.2, ls="-.")
        ax.plot(list((x0, x0)), list((50, 210)), color="#22c55e", lw=3.5)
        ax.text(x0, 40, "Objectif Convergent", color="#86efac", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((x_div, x_div)), list((75, 185)), color="#38bdf8", lw=3)
        ax.text(x_div, 64, f"Lentille Divergente\n({pos_interne_mm:.0f} mm)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((x_ret, x_ret)), list((85, 175)), color="#eab308", lw=3)
        ax.text(x_ret, 75, "Réticule", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        ecart_r = abs(pos_interne_mm - cible_mm)
        for dy in [-40, 40]:
            ax.plot(list((40, x0)), list((y0 + dy, y0 + dy)), color="#ef4444", lw=1.8)
            dy_mid = dy * 0.55
            ax.plot(list((x0, x_div)), list((y0 + dy, y0 + dy_mid)), color="#ef4444", lw=1.8)
            y_end = y0 if ecart_r <= 1.0 else (y0 + (dy / 40.0) * (pos_interne_mm - cible_mm) * 1.5)
            ax.plot(list((x_div, x_ret)), list((y0 + dy_mid, y_end)), color="#ef4444", lw=1.8)

        statut = "MISE AU POINT INTERNE PARFAITE : Image nette sur le réticule, zéro parallaxe !" if ecart_r <= 1.0 else f"PARALLAXE DÉTECTÉE (Écart {ecart_r:.0f} mm) : Réglez la lentille interne à 45 mm."
        c_stat = "#22c55e" if ecart_r <= 1.0 else "#ef4444"
        ax.text(25, 18, "NIVELLEMENT TP : MISE AU POINT INTERNE PAR LENTILLE DIVERGENTE MOBILE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 34, statut, color=c_stat, fontsize=8, fontweight="bold")
        st.session_state.dtp_mesure_courante = (f"Pos = {pos_interne_mm:.0f} mm", "Cible = 45 mm", f"Écart = {ecart_r:.0f} mm", "NETTE (OK)" if ecart_r <= 1.0 else "PARALLAXE")

    return fig


def afficher_atelier_div_tp(sujet_idx, verrouille=False):
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un chantier TP ci-dessus.")
        return
    banque = BANQUES_DIV_TP[sujet_idx]
    cle_ordre = f"ordre_quiz_dtp_{sujet_idx}"
    if cle_ordre not in st.session_state:
        lq = list(banque["questions"])
        random.shuffle(lq)
        st.session_state[cle_ordre] = lq

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique Travaux Publics (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", ["Choisir..."] + q_data["options"], key=f"dtp_at5_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse Travaux Publics (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")




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

def dessiner_regles_trace_divergente_matplotlib():
    """Schéma pédagogique interactif des 3 rayons particuliers d'une lentille divergente."""
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 240)
    ax.invert_yaxis()
    ax.axis("off")

    x0, y0 = 300.0, 120.0
    f_px = st.session_state.get("slider_regles_div_f", 100.0)
    choix_rayon = st.session_state.get("radio_regles_div_rayon", "Tous les 3 rayons particuliers")

    ax.plot(list((20, 580)), list((y0, y0)), color="#cbd5e1", lw=1.3, ls="-.")
    ax.text(575, y0 + 14, "Axe optique", color="#94a3b8", fontsize=8, ha="right")

    # Lentille divergente (flèches inversées vers l'intérieur)
    ax.plot(list((x0, x0)), list((25, 215)), color="#38bdf8", lw=3)
    ax.plot(list((x0 - 9, x0, x0 + 9)), list((15, 28, 15)), color="#38bdf8", lw=3)
    ax.plot(list((x0 - 9, x0, x0 + 9)), list((225, 212, 225)), color="#38bdf8", lw=3)
    ax.text(x0 + 12, 30, "Lentille Divergente (L)", color="#38bdf8", fontsize=8.5, fontweight="bold")
    ax.text(x0 - 10, y0 + 14, "O", color="#cbd5e1", fontsize=8.5, fontweight="bold", ha="right")

    # Foyers inversés : F' (image virtuel) à GAUCHE, F (objet virtuel) à DROITE
    xfp = x0 - f_px
    xf = x0 + f_px
    ax.scatter(list((xfp, xf)), list((y0, y0)), color="#fde047", s=45, zorder=5)
    ax.text(xfp, y0 + 16, "F' (Foyer image)", color="#fde047", fontsize=8, fontweight="bold", ha="center")
    ax.text(xf, y0 + 16, "F (Foyer objet)", color="#fde047", fontsize=8, fontweight="bold", ha="center")

    # Point objet B à gauche
    xb, yb = 110.0, 55.0
    ax.annotate("", xy=(xb, yb), xytext=(xb, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
    ax.text(xb - 6, y0 + 14, "A", color="#ef4444", fontsize=8.5, fontweight="bold", ha="right")
    ax.text(xb - 6, yb, "B", color="#ef4444", fontsize=8.5, fontweight="bold", ha="right")

    x_obj = xb - x0
    f_neg = -f_px
    x_img = (f_neg * x_obj) / (x_obj + f_neg)
    h_obj = y0 - yb
    h_img = h_obj * (x_img / x_obj)
    xbp = x0 + x_img
    ybp = y0 - h_img

    # Rayon 1 : Parallèle -> diverge en semblant venir de F'
    if "1" in choix_rayon or "Tous" in choix_rayon:
        ax.annotate("", xy=(x0, yb), xytext=(xb, yb), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))
        pente1 = (yb - y0) / (x0 - xfp)
        ax.annotate("", xy=(560, yb + pente1 * (560 - x0)), xytext=(x0, yb), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))
        ax.plot(list((xfp, x0)), list((y0, yb)), color="#eab308", lw=1.3, ls="--")

    # Rayon 2 : Passe par O -> non dévié
    if "2" in choix_rayon or "Tous" in choix_rayon:
        pente2 = (y0 - yb) / (x0 - xb)
        ax.annotate("", xy=(560, yb + pente2 * (560 - xb)), xytext=(xb, yb), arrowprops=dict(arrowstyle="->", color="#3b82f6", lw=2))

    # Rayon 3 : Vise F -> ressort parallèle à l'axe
    if "3" in choix_rayon or "Tous" in choix_rayon:
        pente3 = (y0 - yb) / (xf - xb)
        y_hit3 = yb + pente3 * (x0 - xb)
        ax.annotate("", xy=(x0, y_hit3), xytext=(xb, yb), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=2))
        ax.plot(list((x0, xf)), list((y_hit3, y0)), color="#ec4899", lw=1.3, ls="--")
        ax.annotate("", xy=(560, y_hit3), xytext=(x0, y_hit3), arrowprops=dict(arrowstyle="->", color="#ec4899", lw=2))
        ax.plot(list((xbp, x0)), list((y_hit3, y_hit3)), color="#ec4899", lw=1.3, ls="--")

    # Image virtuelle A'B'
    ax.annotate("", xy=(xbp, ybp), xytext=(xbp, y0), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2.5))
    ax.text(xbp - 6, y0 + 14, "A'", color="#c084fc", fontsize=8.5, fontweight="bold", ha="right")
    ax.text(xbp - 6, ybp - 4, "B'", color="#c084fc", fontsize=8.5, fontweight="bold", ha="right")

    ax.text(20, 18, "RÈGLES DE CONSTRUCTION GÉOMÉTRIQUE D'UNE LENTILLE DIVERGENTE", color="#38bdf8", fontsize=9, fontweight="bold")
    return fig
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

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    if "hd_verrouille_tab1" not in st.session_state:
        st.session_state.hd_verrouille_tab1 = False
    verrou_hd = st.session_state.hd_verrouille_tab1

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
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 1 : Histoire des Lentilles Divergentes</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_hd}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get("ordre_quiz_hd_aleatoire", []), 1):
            qid_c = q["id"]
            saisie_q = st.session_state.get(f"hd_at1_g_{qid_c}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_q) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_hd += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_q}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_hd += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        verif_hd = [
            ("1. Une lentille divergente possède des bords plus ......... que son centre.", "épais", "hd_t1"),
            ("2. L'empereur romain ......... utilisait une émeraude concave pour voir de loin.", "Néron", "hd_t2"),
            ("3. Les verres divergents corrigent le défaut visuel appelé la .........", "myopie", "hd_t3"),
            ("4. En 1604, Johannes ......... explique le fonctionnement des verres concaves.", "Kepler", "hd_t4"),
            ("5. En 1609, ......... utilise une lentille divergente comme oculaire de sa lunette.", "Galilée", "hd_t5"),
            ("6. La lunette de Galilée donne directement une image ......... (à l'endroit).", "droite", "hd_t6"),
            ("7. Dans un œil myope, l'image se forme en ......... de la rétine.", "avant", "hd_t7"),
            ("8. Le verre divergent repousse l'image sur la ......... pour la rendre nette.", "rétine", "hd_t8"),
            ("9. En 1758, John ......... associe lentille convergente et divergente.", "Dollond", "hd_t9"),
            ("10. Ce doublet supprime les aberrations ......... dans les objectifs photo.", "chromatiques", "hd_t10"),
        ]
        for idx_t, (en, rep, cle) in enumerate(verif_hd, 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_hd += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
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
        html_rd = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 2 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 2 : Règles de Tracé des Lentilles Divergentes</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_rd}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get("ordre_quiz_rd_aleatoire", []), 1):
            qid_c = q["id"]
            saisie_q = st.session_state.get(f"rd_at2_g_{qid_c}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_q) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_rd += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_q}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_rd += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
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
        html_rd += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 2 (.html)", data=html_rd, file_name=preparer_nom_fichier("Rapport_Atelier_2_Regles_Divergente").replace(".txt", ".html"), mime="text/html", use_container_width=True)



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
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    if "dm_verrouille_tab4" not in st.session_state:
        st.session_state.dm_verrouille_tab4 = False
    verrou_dm = st.session_state.dm_verrouille_tab4
    sujet_actif_dm = st.session_state.get("sujet_dm_tire", None)
    afficher_atelier_div_maint(sujet_actif_dm, verrouille=verrou_dm)

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
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 4 : Maintenance (Lentilles Divergentes) - {sujets_div_maint[sujet_actif_dm]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_dm}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_dm_{sujet_actif_dm}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"dm_at4_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_dm += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_dm += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_dm}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_dm += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_dm += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 4 (.html)", data=html_dm, file_name=preparer_nom_fichier("Rapport_Atelier_4_Maintenance_Divergentes").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab5:
    st.header("Atelier 5 : Applications dans le domaine des Travaux Publics")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles divergentes sur les chantiers de génie civil et de voirie :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Sur les chantiers TP, les lentilles divergentes équipent les <strong>balises lumineuses grand-angle</strong>, les <strong>caméras de sécurité d'engins à 170°</strong> et les <strong>lunettes de nivellement à mise au point interne étanche</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_div_tp = [
        {"titre": "Chantier N°1 : Balise lumineuse de signalisation à lentille divergente", "img": "div_tp_balise.jpg", "leg": "Feu de balisage de chantier diffusant la lumière sur 360°", "exp": "**Principe :** La lentille divergente (<i>C</i> &lt; 0) écarte les rayons lumineux de l'axe optique pour assurer une signalisation visible sous tous les angles."},
        {"titre": "Chantier N°2 : Caméra de recul grand-angle rétrofocus sur tombereau TP", "img": "div_tp_camera.jpg", "leg": "Caméra grand-angle arrière éliminant les angles morts sur chantier", "exp": "**Principe :** La lentille divergente frontale forme une image **virtuelle, droite et rétrécie** couvrant jusqu'à **175°** derrière l'engin."},
        {"titre": "Chantier N°3 : Niveau optique étanche à mise au point interne divergente", "img": "div_tp_niveau.jpg", "leg": "Lunette de chantier à lentille divergente interne mobile", "exp": "**Principe :** Le déplacement interne d'une lentille divergente ajuste la focalisation sur le réticule tout en gardant le tube hermétique à la poussière et à la pluie."}
    ]

    if "sujet_dtp_tire" not in st.session_state:
        st.session_state.sujet_dtp_tire = None

    if st.button("TIRER AU SORT UN CHANTIER TP (DIVERGENTES)", key="btn_tirage_dtp", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_dtp_tire]
        st.session_state.sujet_dtp_tire = random.choice(choix)
        st.session_state.mesures_dtp_log = []
        st.rerun()

    if st.session_state.sujet_dtp_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un chantier de Travaux Publics.")
    else:
        idx_dtp = st.session_state.sujet_dtp_tire
        data_dtp = sujets_div_tp[idx_dtp]
        st.success(f"Chantier attribué : **{data_dtp['titre']}**")
        st.markdown(data_dtp["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_dtp["img"], caption=data_dtp["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_dtp['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_div_tp.jpg", caption="La pause BD : Avec la caméra grand-angle, le camion paraît encore loin !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_div_tp.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_dtp_log" not in st.session_state: st.session_state.mesures_dtp_log = []
        if idx_dtp == 0:
            st.slider("Vergence C de la lentille divergente de balise (δ) :", -20.0, -4.0, -12.0, 1.0, key="slider_dtp_s0")
        elif idx_dtp == 1:
            st.slider("Vergence C de la caméra grand-angle (δ) :", -24.0, -6.0, -16.0, 1.0, key="slider_dtp_s1")
        else:
            st.slider("Position de la lentille divergente interne (mm) [Cible = 45 mm] :", 30.0, 60.0, 45.0, 1.0, key="slider_dtp_s2")

        if st.button("ENREGISTRER CE RELEVÉ TP", key="btn_rel_dtp", use_container_width=True):
            if "dtp_mesure_courante" in st.session_state:
                st.session_state.mesures_dtp_log.append(st.session_state.dtp_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_div_tp_matplotlib(idx_dtp), use_container_width=True)
        if st.session_state.mesures_dtp_log:
            df_dtp = pd.DataFrame(st.session_state.mesures_dtp_log, columns=["Paramètre 1", "Paramètre 2", "Calcul", "Diagnostic"])
            st.dataframe(df_dtp, use_container_width=True, hide_index=True)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_dtp = st.checkbox("Je certifie avoir complété l'Atelier 5 (Travaux Publics - Divergentes).", key="certif_dtp5", disabled=verrou_dtp)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_exp_dtp5", use_container_width=True, disabled=verrou_dtp):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_dtp is None or not case_certif_dtp:
            st.error("Action refusée : Tirez au sort un chantier et cochez la case de certification.")
        else:
            bq = BANQUES_DIV_TP[sujet_actif_dtp]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_dtp_{sujet_actif_dtp}", []) if st.session_state.get(f"dtp_at5_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_dtp}") == rep)
            st.session_state.score_dtp5_p1, st.session_state.score_dtp5_p2, st.session_state.score_final_dtp5 = sc_q, sc_t, sc_q + sc_t
            st.session_state.dtp_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("dtp_verrouille_tab5", False) and sujet_actif_dtp is not None:
        scr1, scr2, tot_s = st.session_state.score_dtp5_p1, st.session_state.score_dtp5_p2, st.session_state.score_final_dtp5
        ts_dtp = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 5 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_DIV_TP[sujet_actif_dtp]
        html_dtp = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 5 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 5 : Travaux Publics (Lentilles Divergentes) - {sujets_div_tp[sujet_actif_dtp]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_dtp}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_dtp_{sujet_actif_dtp}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"dtp_at5_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_dtp += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_dtp += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_dtp}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_dtp += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_dtp += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 5 (.html)", data=html_dtp, file_name=preparer_nom_fichier("Rapport_Atelier_5_TP_Divergentes").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab6:
    st.header("Atelier 6 : Applications dans le domaine du Transport Routier")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles divergentes au service de la visibilité et de la sécurité routière :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans le transport routier, les lentilles divergentes (<b><i>f'</i> &lt; 0</b>) équipent les <strong>caméras d'angle mort à 170°</strong>, les <strong>diffuseurs de feux arrière</strong> et les <strong>verres correcteurs de myopie</strong>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_div_trans = [
        {"titre": "Cas Transport N°1 : Caméra d'angle mort grand-angle sur poids lourd", "img": "div_trans_anglemort.jpg", "leg": "Caméra latérale grand-angle détectant les cyclistes et piétons", "exp": "**Principe :** La lentille divergente frontale forme une image **virtuelle, droite et rétrécie** élargissant le champ de vision jusqu'à **175°** autour du véhicule."},
        {"titre": "Cas Transport N°2 : Diffuseur divergent de feux de position arrière", "img": "div_trans_feu.jpg", "leg": "Optique arrière à lentilles divergentes étalant le faisceau LED", "exp": "**Principe :** La lentille divergente écarte les rayons lumineux de l'axe optique pour garantir une visibilité latérale homologuée."},
        {"titre": "Cas Transport N°3 : Correction de la myopie du conducteur (Verre divergent)", "img": "div_trans_myopie.jpg", "leg": "Action d'un verre divergent devant un œil myope", "exp": "**Principe :** Le verre divergent (<i>C</i> = 1 / <i>f'</i> &lt; 0) fait diverger légèrement les rayons incidents pour repousser l'image nette des panneaux sur la **rétine**."}
    ]

    if "sujet_dtr_tire" not in st.session_state:
        st.session_state.sujet_dtr_tire = None

    if st.button("TIRER AU SORT UN SUJET TRANSPORT (DIVERGENTES)", key="btn_tirage_dtr", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_dtr_tire]
        st.session_state.sujet_dtr_tire = random.choice(choix)
        st.session_state.mesures_dtr_log = []
        st.rerun()

    if st.session_state.sujet_dtr_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique du Transport Routier.")
    else:
        idx_dtr = st.session_state.sujet_dtr_tire
        data_dtr = sujets_div_trans[idx_dtr]
        st.success(f"Étude attribuée : **{data_dtr['titre']}**")
        st.markdown(data_dtr["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_dtr["img"], caption=data_dtr["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_dtr['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_div_trans.jpg", caption="La pause BD : Avec les optiques grand-angle, rien n'échappe au conducteur !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_div_trans.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_dtr_log" not in st.session_state: st.session_state.mesures_dtr_log = []
        if idx_dtr == 0:
            st.slider("Vergence C de la caméra d'angle mort (δ) :", -24.0, -6.0, -18.0, 1.0, key="slider_dtr_s0")
        elif idx_dtr == 1:
            st.slider("Vergence C du diffuseur de feu arrière (δ) :", -20.0, -4.0, -14.0, 1.0, key="slider_dtr_s1")
        else:
            st.slider("Correction optique du conducteur myope C (δ) :", -6.0, -0.5, -2.5, 0.25, key="slider_dtr_s2")

        if st.button("ENREGISTRER CE CONTRÔLE TRANSPORT", key="btn_rel_dtr", use_container_width=True):
            if "dtr_mesure_courante" in st.session_state:
                st.session_state.mesures_dtr_log.append(st.session_state.dtr_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_div_trans_matplotlib(idx_dtr), use_container_width=True)
        if st.session_state.mesures_dtr_log:
            df_dtr = pd.DataFrame(st.session_state.mesures_dtr_log, columns=["Paramètre", "Configuration", "Mesure optique", "Diagnostic"])
            st.dataframe(df_dtr, use_container_width=True, hide_index=True)

    st.write("---")
    if "dtr_verrouille_tab6" not in st.session_state: st.session_state.dtr_verrouille_tab6 = False
    verrou_dtr = st.session_state.dtr_verrouille_tab6
    sujet_actif_dtr = st.session_state.get("sujet_dtr_tire", None)
    afficher_atelier_div_trans(sujet_actif_dtr, verrouille=verrou_dtr)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_dtr = st.checkbox("Je certifie avoir complété l'Atelier 6 (Transport Routier - Divergentes).", key="certif_dtr6", disabled=verrou_dtr)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_exp_dtr6", use_container_width=True, disabled=verrou_dtr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_dtr is None or not case_certif_dtr:
            st.error("Action refusée : Tirez au sort un sujet et cochez la case de certification.")
        else:
            bq = BANQUES_DIV_TRANS[sujet_actif_dtr]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_dtr_{sujet_actif_dtr}", []) if st.session_state.get(f"dtr_at6_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_dtr}") == rep)
            st.session_state.score_dtr6_p1, st.session_state.score_dtr6_p2, st.session_state.score_final_dtr6 = sc_q, sc_t, sc_q + sc_t
            st.session_state.dtr_verrouille_tab6 = True
            st.rerun()

    if st.session_state.get("dtr_verrouille_tab6", False) and sujet_actif_dtr is not None:
        scr1, scr2, tot_s = st.session_state.score_dtr6_p1, st.session_state.score_dtr6_p2, st.session_state.score_final_dtr6
        ts_dtr = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 6 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_DIV_TRANS[sujet_actif_dtr]
        html_dtr = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 6 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 6 : Transport Routier (Lentilles Divergentes) - {sujets_div_trans[sujet_actif_dtr]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_dtr}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_dtr_{sujet_actif_dtr}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"dtr_at6_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_dtr += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_dtr += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_dtr}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_dtr += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_dtr += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 6 (.html)", data=html_dtr, file_name=preparer_nom_fichier("Rapport_Atelier_6_Transport_Divergentes").replace(".txt", ".html"), mime="text/html", use_container_width=True)


with tab7:
    st.header("Atelier 7 : Applications dans le domaine du Géomètre Topographe")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Les lentilles divergentes dans les instruments de topographie et de relevé 3D :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Chez le géomètre topographe, les lentilles divergentes assurent la <strong>mise au point interne étanche</strong> des stations totales, l'<strong>étalement en ligne</strong> des lasers de chantier (lentille de Powell) et le <strong>grand champ</strong> des chambres photogrammétriques rétrofocus.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_div_geo = [
        {"titre": "Mission N°1 : Station Totale à lentille divergente interne mobile", "img": "div_geo_station.jpg", "leg": "Schéma optique interne d'une lunette de station totale", "exp": "**Principe :** La translation interne d'une lentille divergente (<i>f'</i> &lt; 0) ajuste la netteté sur le réticule tout en maintenant un tube court et hermétique."},
        {"titre": "Mission N°2 : Laser lignes à lentille divergente de Powell", "img": "div_geo_laser.jpg", "leg": "Lentille divergente cylindrique étalant un point laser en ligne", "exp": "**Principe :** La lentille divergente de Powell étale le faisceau laser dans un seul plan pour projeter un trait lumineux rectiligne uniforme sur le bâtiment."},
        {"titre": "Mission N°3 : Chambre photogrammétrique grand-angle rétrofocus", "img": "div_geo_retrofocus.jpg", "leg": "Objectif grand-angle rétrofocus pour relevé de façades", "exp": "**Principe :** Une lentille divergente frontale élargit l'angle de vue jusqu'à **130°** pour relever des façades dans des rues étroites."}
    ]

    if "sujet_dgeo_tire" not in st.session_state:
        st.session_state.sujet_dgeo_tire = None

    if st.button("TIRER AU SORT UNE MISSION GÉOMÈTRE (DIVERGENTES)", key="btn_tirage_dgeo", use_container_width=True):
        choix = [i for i in range(3) if i != st.session_state.sujet_dgeo_tire]
        st.session_state.sujet_dgeo_tire = random.choice(choix)
        st.session_state.mesures_dgeo_log = []
        st.rerun()

    if st.session_state.sujet_dgeo_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort une mission de Géomètre Topographe.")
    else:
        idx_dgeo = st.session_state.sujet_dgeo_tire
        data_dgeo = sujets_div_geo[idx_dgeo]
        st.success(f"Mission attribuée : **{data_dgeo['titre']}**")
        st.markdown(data_dgeo["exp"], unsafe_allow_html=True)

        c_img, c_bd = st.columns(2)
        with c_img:
            try: st.image(data_dgeo["img"], caption=data_dgeo["leg"], use_container_width=True)
            except Exception: st.warning(f"L'image '{data_dgeo['img']}' est introuvable.")
        with c_bd:
            try: st.image("bd_div_geo.jpg", caption="La pause BD : Quand la ligne laser traverse tout le bureau d'études !", use_container_width=True)
            except Exception: st.warning("L'image 'bd_div_geo.jpg' est introuvable.")

        st.markdown("---")
        if "mesures_dgeo_log" not in st.session_state: st.session_state.mesures_dgeo_log = []
        if idx_dgeo == 0:
            st.slider("Position de la lentille divergente interne (mm) [Cible = 60 mm] :", 40.0, 80.0, 60.0, 1.0, key="slider_dgeo_s0")
        elif idx_dgeo == 1:
            c1_p, c2_p = st.columns(2)
            with c1_p: st.slider("Vergence lentille de Powell C (δ) :", -50.0, -15.0, -35.0, 1.0, key="slider_dgeo_s1")
            with c2_p: st.slider("Distance au mur D (mètres) :", 2.0, 25.0, 10.0, 1.0, key="slider_dgeo_d_s1")
        else:
            st.slider("Vergence de la lentille divergente frontale C (δ) :", -28.0, -8.0, -20.0, 1.0, key="slider_dgeo_s2")

        if st.button("ENREGISTRER CE POINT TOPOGRAPHIQUE", key="btn_rel_dgeo", use_container_width=True):
            if "dgeo_mesure_courante" in st.session_state:
                st.session_state.mesures_dgeo_log.append(st.session_state.dgeo_mesure_courante)
                st.rerun()

        st.pyplot(mettre_a_jour_div_geo_matplotlib(idx_dgeo), use_container_width=True)
        if st.session_state.mesures_dgeo_log:
            df_dgeo = pd.DataFrame(st.session_state.mesures_dgeo_log, columns=["Paramètre 1", "Paramètre 2", "Calcul optique", "Validation"])
            st.dataframe(df_dgeo, use_container_width=True, hide_index=True)

    st.write("---")
    if "dgeo_verrouille_tab7" not in st.session_state: st.session_state.dgeo_verrouille_tab7 = False
    verrou_dgeo = st.session_state.dgeo_verrouille_tab7
    sujet_actif_dgeo = st.session_state.get("sujet_dgeo_tire", None)
    afficher_atelier_div_geo(sujet_actif_dgeo, verrouille=verrou_dgeo)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_dgeo = st.checkbox("Je certifie avoir complété l'Atelier 7 (Géomètre Topographe - Divergentes).", key="certif_dgeo7", disabled=verrou_dgeo)
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_exp_dgeo7", use_container_width=True, disabled=verrou_dgeo):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_dgeo is None or not case_certif_dgeo:
            st.error("Action refusée : Tirez au sort une mission et cochez la case de certification.")
        else:
            bq = BANQUES_DIV_GEO[sujet_actif_dgeo]
            sc_q = sum(1.0 for q in st.session_state.get(f"ordre_quiz_dgeo_{sujet_actif_dgeo}", []) if st.session_state.get(f"dgeo_at7_g_{q['id']}") == q["rep"])
            sc_t = sum(1.0 for _, _, rep, cle in bq["trous"] if st.session_state.get(f"{cle}_s{sujet_actif_dgeo}") == rep)
            st.session_state.score_dgeo7_p1, st.session_state.score_dgeo7_p2, st.session_state.score_final_dgeo7 = sc_q, sc_t, sc_q + sc_t
            st.session_state.dgeo_verrouille_tab7 = True
            st.rerun()

    if st.session_state.get("dgeo_verrouille_tab7", False) and sujet_actif_dgeo is not None:
        scr1, scr2, tot_s = st.session_state.score_dgeo7_p1, st.session_state.score_dgeo7_p2, st.session_state.score_final_dgeo7
        ts_dgeo = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER 7 SCELLÉ | Note : {tot_s:.1f} / 20")
        bq = BANQUES_DIV_GEO[sujet_actif_dgeo]
        html_dgeo = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Rapport Atelier 7 - {n_eleve}</title>
        <style>body{{font-family:Arial,sans-serif;margin:30px;background:#f8fafc;color:#1e293b}}.header-box{{background:#1e3a8a;color:white;padding:20px;border-radius:8px;margin-bottom:25px;position:relative}}.score-badge{{position:absolute;top:20px;right:20px;background:#eab308;color:#1e293b;padding:15px 25px;border-radius:8px;font-size:24px;font-weight:bold;border:2px solid white}}table{{width:100%;border-collapse:collapse;margin-bottom:25px;background:white}}th{{background:#0f172a;color:white;padding:10px;text-align:left}}td{{padding:10px;border-bottom:1px solid #e2e8f0}}.status-correct{{color:#10b981;font-weight:bold}}.status-incorrect{{color:#ef4444;font-weight:bold}}</style></head>
        <body><div class="header-box"><h1>Professeur Laurent GALLET</h1><p>Atelier 7 : Géomètre Topographe (Lentilles Divergentes) - {sujets_div_geo[sujet_actif_dgeo]['titre']}</p><p>Élève : {p_eleve} {n_eleve} | Classe : {c_eleve} | Scellé le : {ts_dgeo}</p><div class="score-badge">SCORE<br>{tot_s:.1f} / 20</div></div>
        <p style="background:white;padding:15px;border-left:4px solid #1e3a8a;">Quiz : <strong>{scr1:.1f}/10</strong> | Synthèse : <strong>{scr2:.1f}/10</strong> | Total : <strong>{tot_s:.1f}/20</strong></p>
        <table><thead><tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"""
        for num, q in enumerate(st.session_state.get(f"ordre_quiz_dgeo_{sujet_actif_dgeo}", []), 1):
            qid_curr = q["id"]
            saisie_curr = st.session_state.get(f"dgeo_at7_g_{qid_curr}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie_curr) == str(q["rep"]) else "INCORRECT"
            v_cls = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_dgeo += f"<tr><td>{num}</td><td>{q['q']}</td><td>{saisie_curr}</td><td>{q['rep']}</td><td class='{v_cls}'>{v_lbl}</td></tr>"
        html_dgeo += "</tbody></table><table><thead><tr><th>N°</th><th>Phrase à trous</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr></thead><tbody>"
        for idx_t, (en, _, rep, cle) in enumerate(bq["trous"], 1):
            saisie_t_curr = st.session_state.get(f"{cle}_s{sujet_actif_dgeo}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t_curr) == str(rep) else "INCORRECT"
            v_cls_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_dgeo += f"<tr><td>{idx_t}</td><td>{en}</td><td>{saisie_t_curr}</td><td>{rep}</td><td class='{v_cls_t}'>{v_lbl_t}</td></tr>"
        html_dgeo += "</tbody></table></body></html>"
        st.download_button("Télécharger le rapport officiel de l'Atelier 7 (.html)", data=html_dgeo, file_name=preparer_nom_fichier("Rapport_Atelier_7_Geometre_Divergentes").replace(".txt", ".html"), mime="text/html", use_container_width=True)



