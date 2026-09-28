# -*- coding: utf-8 -*-

import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application dosage du vinaigre",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage du vinaigre")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

# Variables d'état expérimentales et modes examen
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 7.0
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.1

if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine": { "ph_min": 8.2, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F8BBD0", "nom_zone": "Rose pâle",  "couleur_base": "#E91E63", "nom_base": "Rose fuchsia" },
        "Bleu de Thymol": { "ph_min": 1.2, "ph_max": 2.8,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FFEB3B", "nom_zone": "Jaune", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Hélianthine / Orange de méthyle": {"ph_min": 3.2, "ph_max": 4.4,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Vert de Bromocrésol": { "ph_min": 3.8, "ph_max": 5.4, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#8BC34A", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Rouge de Méthyle": { "ph_min": 4.2, "ph_max": 6.2, "couleur_acide": "#F44336", "nom_acide": "Rouge","couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Bleu de Bromophténol": { "ph_min": 3.0, "ph_max": 4.6, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#00BCD4", "nom_zone": "Vert-Bleu", "couleur_base": "#3F51B5", "nom_base": "Bleu violet" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },
        "Jaune d'Alizarin R": {"ph_min": 10.1, "ph_max": 12.0, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#F44336", "nom_base": "Rouge" }
    }

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


# Déclaration officielle de la barre de navigation
# Les variables d'onglets sont liées à leurs index de liste respectifs
onglets = st.tabs([
    "Identification",
    "Généralités sur le vinaigre",
    "Dosage colorimétrique du vinaigre",
    "Calcul théorique sur le vinaigre et vérification de l'inscription sur la bouteille"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

