# -*- coding: utf-8 -*-

import streamlit as st

# --- 1. CONFIGURATION DE LA PAGE WEB STREAMLIT ---
st.set_page_config(
    page_title="Application modèle moléculaire",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 2. IMPORTATIONS SCIENTIFIQUES ET SYSTEME STANDARDS ---
from datetime import datetime
import math
import os
import random
import time

# --- 3. BIBLIOTHÈQUES DE CALCULS ET TABLEAUX DE DONNÉES ---
import numpy as np
import pandas as pd

# --- 4. TRAITEMENT ET RENDU DES GRAPHES CHIMIQUES (Matplotlib / Plotly) ---
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go

# --- 5. COMPOSANTS ET INTEGRATION HTML/SVG POUR LE WEB ---
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application modèle moléculaire")
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

# Variables d'état expérimentales et modes examen
if "animation_active" not in st.session_state: 
    st.session_state.animation_active = False

if "evaluation_deja_faite" not in st.session_state:
    st.session_state.evaluation_deja_faite = False
if "liste_evaluation_courante" not in st.session_state:
    st.session_state.liste_evaluation_courante = []
if "index_evaluation_courant" not in st.session_state:
    st.session_state.index_evaluation_courant = 0
if "notes_par_question" not in st.session_state:
    st.session_state.notes_par_question = []
if "tableau_etudiant_lignes" not in st.session_state:
    st.session_state.tableau_etudiant_lignes = []
if "molecules_deja_faites" not in st.session_state:
    st.session_state.molecules_deja_faites = set()
CATALOGUE_MOLECULES = {
    "Huiles Moteur & Lubrifiants": {
        "Sébaçate de dibutyle (Lubrifiant fluide)": {
            "atomes": ['C','C','C','C','O','C','O','C','C','C','C','C','C','C','C','O','C','O','C','C','C','C'],
            "liaisons": [(0,1,False), (1,2,False), (2,3,False), (3,4,False), (4,5,True), (4,6,False), (6,7,False), (7,8,False), (8,9,False), (9,10,False), (10,11,False), (11,12,False), (12,13,False), (13,14,False), (14,15,True), (14,16,False), (16,17,False), (17,18,False), (18,19,False), (19,20,False), (20,21,False)]
        },
        "Phosphate de tricrésyle (Additif anti-usure)": {
            "atomes": ['P','O','O','O','O','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C'],
            "liaisons": [(0,1,True), (0,2,False), (0,3,False), (0,4,False), (2,5,False), (3,11,False), (4,17,False), (5,6,True), (6,7,False), (7,8,True), (8,9,False), (9,10,True), (10,5,False), (5,24,False), (11,12,True), (12,13,False), (13,14,True), (14,15,False), (15,16,True), (16,11,False), (17,18,True), (18,19,False), (19,20,True), (20,21,False), (21,22,True), (22,17,False)]
        },
        "Squalane (Lubrifiant de synthèse premium)": {
            "atomes": ['C'] * 30,
            "liaisons": [(i, i+1, False) for i in range(29)]
        },
        "Polydiméthylsiloxane (Huile de silicone de base)": {
            "atomes": ['C','O','C','O','C','O','C','O','C','O','C'],
            "liaisons": [(i, i+1, False) for i in range(10)]
        }
    },
    "Esters (Arômes & Solvants)": {
        "Acétate d'éthyle (Solvant peintures)": {
            "atomes": ['C', 'C', 'O', 'O', 'C', 'C'],
            "liaisons": [(0,1,False), (1,2,True), (1,3,False), (3,4,False), (4,5,False)]
        },
        "Acétate d'isoamyle (Arôme Banane)": {
            "atomes": ['C', 'C', 'O', 'O', 'C', 'C', 'C', 'C'],
            "liaisons": [(0,1,False), (1,2,True), (1,3,False), (3,4,False), (4,5,False), (5,6,False), (5,7,False)]
        },
        "Butanoate de méthyle (Arôme Pomme)": {
            "atomes": ['C', 'C', 'C', 'C', 'O', 'O', 'C'],
            "liaisons": [(0,1,False), (1,2,False), (2,3,False), (3,4,True), (3,5,False), (5,6,False)]
        },
        "Salicylate de méthyle (Wintergreen)": {
            "atomes": ['C','C','C','C','C','C','C','O','O','C','O'],
            "liaisons": [(0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False), (0,6,False), (6,7,True), (6,8,False), (8,9,False), (1,10,False)]
        },
        "Butanoate d'éthyle (Arôme Ananas)": {
            "atomes": ['C','C','C','C','O','O','C','C'],
            "liaisons": [(0,1,False), (1,2,False), (2,3,False), (3,4,True), (3,5,False), (5,6,False), (6,7,False)]
        },
        "Formiate d'éthyle (Arôme Rhum)": {
            "atomes": ['C','O','O','C','C'],
            "liaisons": [(0,1,True), (0,2,False), (2,3,False), (3,4,False)]
        }
    },
    "Colorants & Indicateurs": {
        "Azobenzène (Base jaune azoïque)": {
            "atomes": ['C','C','C','C','C','C','N','N','C','C','C','C','C','C'],
            "liaisons": [(0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False), (0,6,False), (6,7,True), (7,8,False), (8,9,True), (9,10,False), (10,11,True), (11,12,False), (12,13,True), (13,8,False)]
        },
        "Indigo (Teinture bleue textile)": {
            "atomes": ['C','C','C','C','C','C', 'C', 'O', 'N', 'C', 'C', 'O', 'N', 'C','C','C','C','C','C'],
            "liaisons": [(0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False), (0,6,False), (6,7,True), (6,8,False), (8,9,False), (9,10,True), (9,11,True), (10,12,False), (12,13,False), (13,14,True), (14,15,False), (15,16,True), (16,17,False), (17,18,True), (18,13,False)]
        },
        "Aniline (Base colorants industriels)": {
            "atomes": ['C','C','C','C','C','C','N'],
            "liaisons": [(0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False), (0,6,False)]
        }
    },
    "Solvants & Chimie Organique": {
        "Acétone": {
            "atomes": ['C','C','C','O'],
            "liaisons": [(0,1,False), (1,2,False), (1,3,True)]
        },
        "Éthylène Glycol (Antigel moteur)": {
            "atomes": ['O','C','C','O'],
            "liaisons": [(0,1,False), (1,2,False), (2,3,False)]
        },
        "Acide Lactique": {
            "atomes": ['C','C','C','O', 'O', 'O'],
            "liaisons": [(0,1,False), (1,2,False), (1,3,False), (2,4,True), (2,5,False)]
        },
        "Benzène": {
            "atomes": ['C','C','C','C','C','C'],
            "liaisons": [(0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False)]
        }
    },
    "Alcènes (C1 à C12)": {
        "C2 : Éthène (Éthylène - Synthèse des plastiques)": {
            "atomes": ['C', 'C'],
            "liaisons": [(0, 1, True)]
        },
        "C3 : Propène (Propylène)": {
            "atomes": ['C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False)]
        },
        "C4 : But-1-ène": {
            "atomes": ['C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False)]
        },
        "C5 : Pent-1-ène": {
            "atomes": ['C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False)]
        },
        "C6 : Hex-1-ène": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False)]
        },
        "C7 : Hept-1-ène": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False)]
        },
        "C8 : Oct-1-ène": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False)]
        },
        "C9 : Non-1-ène": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False)]
        },
        "C10 : Déc-1-ène (Composant majeur des huiles PAO)": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False), (8, 9, False)]
        },
        "C11 : Undéc-1-ène": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False), (8, 9, False), (9, 10, False)]
        },
        "C12 : Dodéc-1-ène (Tensioactifs et détergents)": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, True), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False), (8, 9, False), (9, 10, False), (10, 11, False)]
        }
    },
    "Alcanes (C1 à C12)": {
        "C1 : Méthane (Gaz naturel / Biogaz)": {
            "atomes": ['C'],
            "liaisons": []
        },
        "C2 : Éthane": {
            "atomes": ['C', 'C'],
            "liaisons": [(0, 1, False)]
        },
        "C3 : Propane (Gaz de chauffage en bouteille)": {
            "atomes": ['C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False)]
        },
        "C4 : Butane": {
            "atomes": ['C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False)]
        },
        "C5 : Pentane (Solvant de laboratoire)": {
            "atomes": ['C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False)]
        },
        "C6 : Hexane": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False)]
        },
        "C7 : Heptane (Référence indice d'octane 0)": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False)]
        },
        "C8 : Octane (Composant de l'essence)": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False)]
        },
        "C9 : Nonane": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False)]
        },
        "C10 : Décane (Carburant Kérosène Aviation)": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False), (8, 9, False)]
        },
        "C11 : Undécane": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False), (8, 9, False), (9, 10, False)]
        },
        "C12 : Dodécane (Solvant et composant Diesel)": {
            "atomes": ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'],
            "liaisons": [(0, 1, False), (1, 2, False), (2, 3, False), (3, 4, False), (4, 5, False), (5, 6, False), (6, 7, False), (7, 8, False), (8, 9, False), (9, 10, False), (10, 11, False)]
        }
    },
    "Vitamines (Les 13 Essentielles)": {
        "Vitamine A (Rétinol - Vision & Peau)": {
            "atomes": ['C','C','C','C','C','C', 'C','C','C', 'C','C','C','C','C','C','C','C','C','C','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,False), (3,4,False), (4,5,False), (5,0,False),
                (5,6,False), (5,7,False), (1,8,False),
                (0,9,False), (9,10,True), (10,11,False), (11,12,True), (12,13,False), 
                (13,14,True), (14,15,False), (15,16,True), (16,17,False), (17,18,False), (18,19,False)
            ]
        },
        "Vitamine B1 (Thiamine - Métabolisme)": {
            "atomes": ['C','N','C','N','C','C', 'C', 'N', 'C','S','C','C','C','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,0,False), (2,7,False),
                (4,5,False), (5,6,False),
                (6,8,True), (8,9,False), (9,10,False), (10,6,False), (8,11,False),
                (10,12,False), (12,13,False)
            ]
        },
        "Vitamine B2 (Riboflavine - Croissance)": {
            "atomes": ['C','C','C','C','C','C','N','C','N','C','C','N','C','N','O','O','C','C','C','C','O','O','O','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (1,16,False), (2,17,False),
                (4,6,False), (6,7,True), (7,8,False), (8,9,True), (9,10,False), (10,5,False),
                (7,14,True), (9,11,False), (11,12,True), (12,13,False), (13,10,False), (12,15,True),
                (6,18,False), (18,19,False), (19,20,False), (20,21,False), (21,22,False), (19,23,False)
            ]
        },
        "Vitamine B3 (Niacine - Énergie)": {
            "atomes": ['N', 'C', 'C', 'C', 'C', 'C', 'C', 'O', 'O'],
            "liaisons": [
                (0, 1, True), (1, 2, False), (2, 3, True), (3, 4, False), (4, 5, True), (5, 0, False),
                (2, 6, False), (6, 7, True), (6, 8, False)
            ]
        },
        "Vitamine B5 (Acide pantothénique)": {
            "atomes": ['O','C','C','C','C','O','C','O','N','C','C','C','O','O'],
            "liaisons": [
                (0,1,False), (1,2,False), (2,3,False), (2,4,False), (2,5,False),
                (1,6,False), (6,7,True), (6,8,False),
                (8,9,False), (9,10,False), (10,11,False), (11,12,True), (11,13,False)
            ]
        },
        "Vitamine B6 (Pyridoxine - Nerfs)": {
            "atomes": ['N', 'C', 'C', 'C', 'C', 'C', 'C', 'O', 'C', 'O', 'C', 'O'],
            "liaisons": [
                (0, 1, True), (1, 2, False), (2, 3, True), (3, 4, False), (4, 5, True), (5, 0, False),
                (1, 6, False), (2, 7, False), (3, 8, False), (8, 9, False), (4, 10, False), (10, 11, False)
            ]
        },
        "Vitamine B8 (Biotine - Cheveux & Ongles)": {
            "atomes": ['C','C','N','C','N','O','S','C','C','C','C','C','O','O'],
            "liaisons": [
                (0,1,False), (1,2,False), (2,3,False), (3,4,False), (4,0,False), (3,5,True),
                (0,6,False), (6,1,False),
                (1,7,False), (7,8,False), (8,9,False), (9,10,False), (10,11,False), (11,12,True), (11,13,False)
            ]
        },
        "Vitamine B9 (Acide folique - Grossesse)": {
            "atomes": ['N','C','N','C','C','N','C','N','C','O','C', 'N','C','C','C','C','C','C','C','O','N','C','C', 'C','O','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (3,6,False), (6,7,True), (7,8,False), (8,4,False), (6,9,True),
                (1,10,False), (10,11,False),
                (11,12,False), (12,13,True), (13,14,False), (14,15,True), (15,16,False), (16,17,True), (17,12,False),
                (15,18,False), (18,19,True), (18,20,False),
                (20,21,False), (21,22,False), (22,23,False), (23,24,True), (23,25,False)
            ]
        },
        "Vitamine B12 (Cobalamine - Noyau Corrine)": {
            "atomes": ['N','C','C','N','C','C','N','C','C','N','C','C','C'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,False), (3,4,True), (4,5,False),
                (5,6,False), (6,7,True), (7,8,False), (8,9,False), (9,10,True),
                (10,11,False), (11,0,False), (2,12,False), (5,12,False)
            ]
        },
        "Vitamine C (Acide ascorbique)": {
            "atomes": ['C', 'O', 'C', 'C', 'C', 'O', 'O', 'O', 'C', 'C', 'O', 'O'],
            "liaisons": [
                (0, 1, False), (1, 2, False), (2, 3, True), (3, 4, False), (4, 0, False),
                (0, 5, True), (2, 6, False), (3, 7, False), (4, 8, False), (8, 9, False), (8, 10, False), (9, 11, False)
            ]
        },
        "Vitamine D3 (Cholécalciférol - Os)": {
            "atomes": ['C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','O'],
            "liaisons": [
                (0,1,False), (1,2,False), (2,3,False), (3,4,False), (4,5,False), (5,0,False), (2,27,False),
                (5,6,True), (6,7,False), (7,8,True),
                (8,9,False), (9,10,False), (10,11,False), (11,12,False), (12,13,False), (13,8,False),
                (13,14,False), (14,15,False), (15,16,False), (16,11,False),
                (16,17,False), (17,18,False), (18,19,False), (19,20,False), (20,21,False), (21,22,False), (22,23,False), (22,24,False)
            ]
        },
        "Vitamine E (Tocophérol - Antioxydant)": {
            "atomes": ['O','C','C','C','C','C','C','C','C','O','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C'],
            "liaisons": [
                (0,1,False), (1,2,True), (2,3,False), (3,4,True), (4,5,False), (5,0,False),
                (1,10,False), (2,11,False), (4,12,False),
                (5,6,False), (6,7,False), (7,8,False), (8,9,False), (9,6,False),
                (8,13,False), (13,14,False), (14,15,False), (15,16,False), (16,17,False), (17,18,False),
                (14,19,False), (17,20,False), (18,21,False), (21,22,False), (22,23,False), (23,24,False)
            ]
        },
        "Vitamine K1 (Phylloquinone - Coagulation)": {
            "atomes": ['C','C','C','C','C','C','C','C','C','C','O','O','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C','C'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (0,6,False), (1,7,True), (2,8,False), (3,9,True), (4,10,False), (5,11,False),
                (6,12,False), (12,13,True), (13,14,False), (14,15,False), (15,16,False), (16,17,False),
                (13,18,False), (17,19,False), (19,20,False), (20,21,False), (21,22,False), (22,23,False)
            ]
        },
    "Colorants Alimentaires (E100 - E150)": {
        "E100 : Curcumine (Jaune naturel du Safran/Curcuma)": {
            "atomes": ['C','C','C','C','C','C','O','O','C','C','C','O','C','C','C','C','C','C','C','O','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (2,6,False), (3,7,False),
                (4,8,False), (8,9,True), (9,10,False), (10,11,True), (10,12,False),
                (12,13,False), (13,14,True), (14,15,False),
                (15,16,False), (16,17,True), (17,18,False), (18,19,True), (19,20,False), (20,15,False)
            ]
        },
        "E102 : Tartrazine (Jaune de synthèse pour confiseries)": {
            "atomes": ['C','C','C','C','C','C','N','N','C','C','N','N','C','O','C','C','C','C','C','C','S','O','O','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (2,6,False), (6,7,True), (7,8,False),
                (8,9,True), (9,10,False), (10,11,False), (11,8,False), (9,13,True),
                (10,12,False), (12,14,False), (14,15,True), (15,16,False), (16,17,True), (17,18,False), (18,19,True), (19,14,False),
                (17,20,False), (20,21,True), (20,22,True), (20,23,False)
            ]
        },
        "E110 : Jaune Soleil FCF (Boissons et sirops)": {
            "atomes": ['C','C','C','C','C','C','C','C','C','C','O','N','N','C','C','C','C','C','C','S','O','O','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (0,6,False), (6,7,True), (7,8,False), (8,9,True), (9,5,False), (1,10,False),
                (7,11,False), (11,12,True), (12,13,False),
                (13,14,True), (14,15,False), (15,16,True), (16,17,False), (17,18,True), (18,13,False),
                (16,19,False), (19,20,True), (19,21,True), (19,22,False)
            ]
        },
        "E124 : Rouge Ponceau 4R (Sirop de grenadine)": {
            "atomes": ['C','C','C','C','C','C','C','C','C','C','N','N','C','C','C','C','C','C','C','C','C','C','O'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,True), (3,4,False), (4,5,True), (5,0,False),
                (0,6,False), (6,7,True), (7,8,False), (8,9,True), (9,5,False),
                (7,10,False), (10,11,True), (11,12,False),
                (12,13,True), (13,14,False), (14,15,True), (15,16,False), (16,17,True), (17,12,False),
                (13,18,False), (18,19,True), (19,20,False), (20,21,True), (21,17,False), (14,22,False)
            ]
        },
        "E131 : Bleu Patenté V (Colorant bleu des bonbons schtroumpf)": {
            "atomes": ['C', 'C','C','C','C','C','C', 'C','C','C','C','C','C', 'C','C','C','C','C','C', 'N', 'N', 'O'],
            "liaisons": [
                (0,1,False), (0,7,False), (0,13,False),
                (1,2,True), (2,3,False), (3,4,True), (4,5,False), (5,6,True), (6,1,False), (4,19,False),
                (7,8,True), (8,9,False), (9,10,True), (10,11,False), (11,12,True), (12,7,False), (10,20,False),
                (13,14,True), (14,15,False), (15,16,True), (16,17,False), (17,18,True), (18,13,False), (16,21,False)
            ]
        },
        "E140 : Chlorophylle (Vert naturel des feuilles et légumes)": {
            "atomes": ['N','C','C','N','C','C','N','C','C','N','C','C','C','C','C','C'],
            "liaisons": [
                (0,1,True), (1,2,False), (2,3,False), (3,4,True), (4,5,False),
                (5,6,False), (6,7,True), (7,8,False), (8,9,False), (9,10,True),
                (10,11,False), (11,0,False),
                (1,12,False), (4,13,False), (7,14,False), (10,15,False)
            ]
        }
    },
    "Petites Molécules du Quotidien (Le Top 50)": {
        "01. Eau (H2O - Base de la vie)": {"atomes": ['O'], "liaisons": []},
        "02. Dioxyde de Carbone (CO2 - Gaz carbonique)": {"atomes": ['C', 'O', 'O'], "liaisons": [(0, 1, True), (0, 2, True)]},
        "03. Dioxygène (O2 - Respiration)": {"atomes": ['O', 'O'], "liaisons": [(0, 1, True)]},
        "04. Diazote (N2 - 78% de l'atmosphère)": {"atomes": ['N', 'N'], "liaisons": [(0, 1, True)]},
        "05. Ozone (O3 - Couche protectrice)": {"atomes": ['O', 'O', 'O'], "liaisons": [(0, 1, False), (1, 2, True)]},
        "06. Hydrogène (H2 - Diatome pure)": {"atomes": ['H', 'H'], "liaisons": [(0, 1, False)]},
        "07. Ammoniac (NH3 - Nettoyant / Engrais)": {"atomes": ['N'], "liaisons": []},
        "08. Monoxyde de Carbone (CO - Gaz toxique)": {"atomes": ['C', 'O'], "liaisons": [(0, 1, True)]},
        "09. Dioxyde de Soufre (SO2 - Conservateur E220)": {"atomes": ['S', 'O', 'O'], "liaisons": [(0, 1, True), (0, 2, True)]},
        "10. Trioxyde de Soufre (SO3 - Pluies acides)": {"atomes": ['S', 'O', 'O', 'O'], "liaisons": [(0, 1, True), (0, 2, True), (0, 3, True)]},
        "11. Sulfure d'Hydrogène (H2S - Œuf pourri)": {"atomes": ['S'], "liaisons": []},
        "12. Monoxyde d'Azote (NO - Polluant auto)": {"atomes": ['N', 'O'], "liaisons": [(0, 1, True)]},
        "13. Peroxyde d'Azote (NO2 - Gaz brun polluant)": {"atomes": ['N', 'O', 'O'], "liaisons": [(0, 1, True), (0, 2, False)]},
        "14. Protoxyde d'Azote (N2O - Gaz hilarant)": {"atomes": ['N', 'N', 'O'], "liaisons": [(0, 1, True), (1, 2, False)]},
        "15. Phosphine (PH3 - Gaz de dératisation)": {"atomes": ['P'], "liaisons": []},
        "16. Trioxyde de Phosphore (P2O3)": {"atomes": ['P', 'P', 'O', 'O', 'O'], "liaisons": [(0, 2, False), (0, 3, False), (1, 3, False), (1, 4, False)]},
        "17. Pentoxyde de Phosphore (P2O5)": {"atomes": ['P', 'P', 'O', 'O', 'O', 'O', 'O'], "liaisons": [(0, 2, True), (1, 3, True), (0, 4, False), (0, 5, False), (1, 5, False), (1, 6, False)]},
        "18. Acide Chlorhydrique (HCl - Detartrant)": {"atomes": ['Cl'], "liaisons": []}
    }
}}

    
def basculer_mode_exercice_streamlit():
    """Gère l'activation du mode examen et procède au tirage au sort des 10 molécules"""
    # 1. Sécurité absolue : blocage si l'évaluation a déjà été validée au cours de la session
    if st.session_state.get("evaluation_deja_faite", False):
        st.error("Accès refusé : Vous avez déjà réalisé votre évaluation pour cette session. Il est impossible de recommencer le contrôle.")
        st.session_state.mode_evaluation = False
        return

    # 2. Initialisation du pool d'examen lors du passage en mode Évaluation
    if st.session_state.get("mode_evaluation", False) and not st.session_state.liste_evaluation_courante:
        pool_moyennes = []
        
        for cat in CATALOGUE_MOLECULES:
            for nom_m, data_m in CATALOGUE_MOLECULES[cat].items():
                nb_lourds = len(data_m.get("atomes", []))
                # Filtrage académique : molécules contenant entre 4 et 12 atomes
                if 4 <= nb_lourds <= 12 and nom_m not in st.session_state.molecules_deja_faites:
                    pool_moyennes.append((cat, nom_m))
        
        if len(pool_moyennes) < 10:
            st.warning("Catalogue insuffisant : Il n'y a plus assez de molécules disponibles pour générer un test complet.")
            st.session_state.mode_evaluation = False
            return
            
        # Tirage au sort de 10 molécules uniques et initialisation du suivi
        st.session_state.liste_evaluation_courante = random.sample(pool_moyennes, 10)
        st.session_state.index_evaluation_courant = 0
        st.session_state.notes_par_question = []
        st.session_state.tableau_etudiant_lignes = [] # Nettoyage initial du tableau
        
        st.info("CONTRÔLE OFFICIEL ACTIF : Le mode Évaluation officielle est lancé. Tous les contrôles de sélection et les onglets sont restreints jusqu'à la fin de l'épreuve.")
        charger_molecule_evaluation_courante_streamlit()


def charger_molecule_evaluation_courante_streamlit():
    """Charge la molécule d'examen courante et vide le tableau d'analyse de l'élève"""
    idx = st.session_state.index_evaluation_courant
    cat, nom_mol = st.session_state.liste_evaluation_courante[idx]
    
    # Stockage de la molécule courante d'examen pour le moteur physique
    st.session_state.molecule_exercice_active = nom_mol
    st.session_state.categorie_exercice_active = cat
    
    # Nettoyage complet des saisies et du tableau d'analyse de la question précédente
    st.session_state.tableau_etudiant_lignes = []
    
    # Réinitialisation forcée des entrées numériques et textuelles de l'élève
    if "entry_masse_totale_etudiant" in st.session_state:
        st.session_state.entry_masse_totale_etudiant = 0.0
        
    # Appel de votre constructeur géométrique tridimensionnel (Liaison moteur physique)
    data = CATALOGUE_MOLECULES[cat][nom_mol]
    # self.configurer_et_lancer(nom_mol, data["atomes"], data["liaisons"])


def inserer_ligne_etudiant_streamlit(symb, qty, masse):
    """Prend les saisies du formulaire web, vérifie l'élément et l'insère dans le tableau de session"""
    symb_clean = symb.strip().upper()
    
    if not symb_clean or qty <= 0 or masse <= 0.0:
        st.warning("Saisie incomplète : Veuillez remplir le symbole, une quantité supérieure à 0 et votre masse calculée.")
        return

    # Vérification de l'existence de l'élément dans votre dictionnaire global ELEMENTS_PAR_SYMBOLE
    if symb_clean not in ELEMENTS_PAR_SYMBOLE:
        st.error(f"Élément inconnu : Le symbole '{symb_clean}' n'a pas été trouvé dans votre dictionnaire de référence ELEMENTS_DB.")
        return

    nom_element, _ = ELEMENTS_PAR_SYMBOLE[symb_clean]
    
    # Insertion de la ligne dans le tableau stocké en session (Ancien Treeview.insert)
    st.session_state.tableau_etudiant_lignes.append({
        "Symb.": symb_clean,
        "Nom Élément": nom_element.capitalize(),
        "Quantité": int(qty),
        "Masse Calc.": float(masse)
    })
    st.success(f"Ligne de l'élément {symb_clean} insérée avec succès dans votre tableau d'analyse.")

def verifier_exercice_streamlit():
    """Analyse les reponses de l etudiant par rapport a la solution scientifique cible"""
    # 1. Recuperation de la molecule courante selon le mode actif
    if st.session_state.get("mode_evaluation", False):
        if not st.session_state.get("liste_evaluation_courante"):
            return
        idx = st.session_state.index_evaluation_courant
        cat, nom_reel = st.session_state.liste_evaluation_courante[idx]
    else:
        cat = st.session_state.get("combo_cat_tab2")
        nom_reel = st.session_state.get("combo_mol_tab2")

    if not nom_reel:
        return

    if nom_reel in st.session_state.get("molecules_deja_faites", set()) and not st.session_state.mode_evaluation:
        st.warning("Exercice deja resolu ! Passez a la suite.")
        return

    # 2. Solution scientifique de reference (Realite du modele)
    data_mol = CATALOGUE_MOLECULES[cat][nom_reel]
    atomes_totaux = list(data_mol["atomes"])
    
    valences = [0] * len(data_mol["atomes"])
    for idx1, idx2, dbl in data_mol["liaisons"]:
        p = 2 if dbl else 1
        valences[idx1] += p
        valences[idx2] += p
        
    for idx, symb in enumerate(data_mol["atomes"]):
        h_manquants = {'C': 4, 'N': 3, 'O': 2, 'H': 1, 'S': 2, 'P': 5, 'Cl': 1, 'Fe': 2, 'I': 1}.get(symb, 0) - valences[idx]
        for _ in range(h_manquants): 
            atomes_totaux.append('H')

    solution_cible = {}
    masse_totale_reelle = 0.0
    for s in atomes_totaux:
        s_up = s.upper()
        solution_cible[s_up] = solution_cible.get(s_up, 0) + 1
        
        for nom_e, donnees_e in ELEMENTS_DB.items():
            if isinstance(donnees_e, tuple) and len(donnees_e) == 3:
                symb_db = donnees_e[0].upper()
                m_db = float(donnees_e[2])
                if symb_db == s_up:
                    masse_totale_reelle += m_db
                    break

    # 3. Lecture du tableau de session de l etudiant
    analyse_etudiant = {}
    for ligne in st.session_state.get("tableau_etudiant_lignes", []):
        s_etudiant = str(ligne.get("Symb.", "")).upper()
        q_etudiant = int(ligne.get("Quantite", 0))
        if s_etudiant:
            analyse_etudiant[s_etudiant] = {'qty': q_etudiant}

    masse_etudiant = float(st.session_state.get("entry_masse_totale_etudiant", 0.0))

    # 4. Decompte des fautes academiques
    fautes = 0
    for symb_th, qty_th in solution_cible.items():
        if symb_th not in analyse_etudiant: 
            fautes += 2  # Element oublie
        elif analyse_etudiant[symb_th]['qty'] != qty_th: 
            fautes += 1  # Mauvaise quantite
            
    for symb_et in analyse_etudiant:
        if symb_et not in solution_cible: 
            fautes += 1  # Element invente
            
    if abs(masse_etudiant - masse_totale_reelle) > 1.2: 
        fautes += 2  # Masse fausse ou vide

    # 5. Enregistrement des notes et affichage des bandeaux de verdict
    if st.session_state.get("mode_evaluation", False):
        note_question = max(0.0, 2.0 - (fautes * 0.5))
        st.session_state.notes_par_question.append(note_question)
        
        st.session_state.etape_validation_valide = True # Verrouille le verificateur
        if fautes == 0:
            st.success("Molecule reussie parfaitement ! +2.00 points.")
        else:
            st.warning(f"Question enregistree. Note attribuee : {note_question:.2f} / 2.00 points.")
    else:
        st.session_state.tentatives += 1
        if fautes == 0:
            st.session_state.reussites += 1
            st.session_state.molecules_deja_faites.add(nom_reel)
            st.success("Tout est juste !")
            st.session_state.etape_validation_valide = True
        else:
            st.error("Des erreurs sont presentes dans votre tableau d'analyse.")


def passer_exercice_suivant_streamlit():
    """Enchaine sur la question suivante ou calcule la note finale de l examen"""
    if st.session_state.get("mode_evaluation", False):
        st.session_state.index_evaluation_courant += 1
        st.session_state.etape_validation_valide = False # Relache le verrou pour la question suivante
        
        if st.session_state.index_evaluation_courant < 10:
            # Reinitialisation du formulaire pour la molecule suivante
            st.session_state.tableau_etudiant_lignes = []
            if "entry_masse_totale_etudiant" in st.session_state:
                st.session_state.entry_masse_totale_etudiant = 0.0
            st.rerun()
        else:
            # Fin des 10 questions : calcul de la note globale sur 20 points
            note_finale = sum(st.session_state.notes_par_question)
            if note_finale > 19.8: note_finale = 20.0
            if note_finale < 0.0: note_finale = 0.0
            
            st.session_state.note_officielle_scellee = note_finale
            st.session_state.evaluation_deja_faite = True
            st.session_state.mode_evaluation = False
            
            # Remise a zero des structures d examen
            st.session_state.liste_evaluation_courante = []
            st.session_state.tableau_etudiant_lignes = []
            st.rerun()
    else:
        # Reinitialisation simple en entraînement libre
        st.session_state.tableau_etudiant_lignes = []
        st.session_state.etape_validation_valide = False
        st.rerun()

def configurer_et_lancer_streamlit(nom_mol, atomes_bruts, liaisons_bruts, cle_onglet="tab1"):
    """
    Moteur physique tridimensionnel : place a plat les atomes et injecte les forces.
    cle_onglet prend la valeur 'tab1' ou 'tab2' pour cibler le bon curseur de zoom.
    """
    # Stockage des listes d atomes et liaisons calcules dans la session globale
    st.session_state.atomes_physique = []
    
    for i, info in enumerate(atomes_bruts):
        hauteur_initiale = 250.0 + (20.0 if i % 2 == 0 else -20.0)
        st.session_state.atomes_physique.append({
            'symbole': info, 
            'x': 200.0 + i * 55.0, 
            'y': hauteur_initiale, 
            'z': 0.0, 
            'vx': 0.0, 
            'vy': 0.0
        })
        
    st.session_state.liaisons_physique = list(liaisons_bruts)
    valences = [0] * len(atomes_bruts)
    
    for idx1, idx2, dbl in liasons_bruts:
        p = 2 if dbl else 1
        valences[idx1] += p
        valences[idx2] += p
        
    nb_init = len(atomes_bruts)
    for parent in range(nb_init):
        symb = st.session_state.atomes_physique[parent]['symbole']
        
        # Prise en compte de tous les elements avec leurs valences respectives
        h_req = {'C': 4, 'N': 3, 'O': 2, 'H': 1, 'S': 2, 'P': 5, 'Cl': 1, 'Fe': 2, 'I': 1}.get(symb, 0) - valences[parent]
        
        px = st.session_state.atomes_physique[parent]['x']
        py = st.session_state.atomes_physique[parent]['y']
        
        for h_idx in range(h_req):
            angle_h = h_idx * (2 * math.pi / 3)
            z_fictif = 25.0 if h_idx % 2 == 0 else -25.0
            
            decourage_y = -35.0 if h_idx == 0 else 20.0
            angle_x = math.sin(angle_h) * 35.0 if h_idx > 0 else 0.0
            
            h_x = px + angle_x
            h_y = py + decourage_y
            
            st.session_state.atomes_physique.append({
                'symbole': 'H', 
                'x': h_x, 
                'y': h_y, 
                'z': z_fictif, 
                'vx': 0.0, 
                'vy': 0.0
            })
            st.session_state.liaisons_physique.append((parent, len(st.session_state.atomes_physique) - 1, False))

    # Declenchement du moteur de relaxation de forces
    calculer_moteur_forces_streamlit(cle_onglet)


def calculer_moteur_forces_streamlit(cle_onglet="tab1"):
    """Moteur de relaxation physique 3D : deploie les molecules de facon realiste dans l espace"""
    # 1. Recuperation de la longueur de liaison via les sliders natifs du session_state de l onglet actif
    if cle_onglet == "tab2" and "slider_zoom_tab2" in st.session_state:
        longueur_ideal = float(st.session_state.slider_zoom_tab2)
    elif "slider_zoom" in st.session_state:
        longueur_ideal = float(st.session_state.slider_zoom)
    else:
        longueur_ideal = 45.0
        
    k_attraction = 0.15      # Force de rappel elastique des liaisons
    repulsion_base = 1200.0   # Force de repulsion entre les atomes pour eviter la superposition
    
    iterations = 80 if len(st.session_state.atomes_physique) > 12 else 55
    
    # 2. Boucle de relaxation physique tridimensionnelle
    for _ in range(iterations):
        for a in st.session_state.atomes_physique:
            a['vx'] = 0.0
            a['vy'] = 0.0
            a.setdefault('z', 0.0)
        
        # Etape A : Force de repulsion globale entre tous les atomes
        for i in range(len(st.session_state.atomes_physique)):
            for j in range(i + 1, len(st.session_state.atomes_physique)):
                a1 = st.session_state.atomes_physique[i]
                a2 = st.session_state.atomes_physique[j]
                
                dx = a2['x'] - a1['x']
                dy = a2['y'] - a1['y']
                dz = a2['z'] - a1['z']
                
                dist = math.sqrt(dx*dx + dy*dy + dz*dz) or 0.1
                force_rep = repulsion_base / (dist * dist)
                
                fx = (dx / dist) * force_rep
                fy = (dy / dist) * force_rep
                fz = (dz / dist) * force_rep
                
                a1['vx'] -= fx
                a1['vy'] -= fy
                a1['z'] -= fz
                
                a2['vx'] += fx
                a2['vy'] += fy
                a2['z'] += fz
        
        # Etape B : Force d attraction elastique des liaisons chimiques
        for idx1, idx2, type_liaison in st.session_state.liaisons_physique:
            a1 = st.session_state.atomes_physique[idx1]
            a2 = st.session_state.atomes_physique[idx2]
            
            dx = a2['x'] - a1['x']
            dy = a2['y'] - a1['y']
            dz = a2['z'] - a1['z']
            
            dist = math.sqrt(dx*dx + dy*dy + dz*dz) or 0.1
            delta = dist - longueur_ideal
            force_att = delta * k_attraction
            
            fx = (dx / dist) * force_att
            fy = (dy / dist) * force_att
            fz = (dz / dist) * force_att
            
            a1['vx'] += fx
            a1['vy'] += fy
            a1['z'] += fz
            
            a2['vx'] -= fx
            a2['vy'] -= fy
            a2['z'] -= fz
        
        # Etape C : Deplacement physique applique avec limitation de vitesse de securite
        for a in st.session_state.atomes_physique:
            vitesse = math.sqrt(a['vx']**2 + a['vy']**2)
            if vitesse > 12.0:
                a['vx'] = (a['vx'] / vitesse) * 12.0
                a['vy'] = (a['vy'] / vitesse) * 12.0
            
            a['x'] += a['vx']
            a['y'] += a['vy']


def generer_scene_svg_streamlit(cle_onglet="tab1"):
    """
    Projette les coordonnees 3D calculees en memoire de session et retourne un bloc SVG.
    cle_onglet prend la valeur 'tab1' ou 'tab2' pour appliquer le bon jeu de curseurs.
    """
    # 1. Recuperation securisee des donnees calculees par le moteur physique
    atomes_physique = st.session_state.get("atomes_physique", [])
    liaisons_physique = st.session_state.get("liaisons_physique", [])
    
    if not atomes_physique:
        return '<div style="text-align:center; color:#64748b; font-style:italic; padding:20px;">Aucun modele charge.</div>'
        
    # Dimensions fixes de la zone de dessin web (Ancien canvas_cible)
    w_c = 600
    h_c = 340
    
    xs_bruts = [a['x'] for a in atomes_physique]
    ys_bruts = [a['y'] for a in atomes_physique]
    
    centre_x = (min(xs_bruts) + max(xs_bruts)) / 2
    centre_y = (min(ys_bruts) + max(ys_bruts)) / 2
    
    # 2. Recuperation des angles depuis le session_state de Streamlit
    angle_rot = 0.0
    angle_inc = 20.0
    longueur_courante = 45.0
    
    if cle_onglet == "tab2":
        angle_rot = float(st.session_state.get("slider_rotation_tab2", 0.0))
        angle_inc = float(st.session_state.get("slider_inclinaison_tab2", 20.0))
        longueur_courante = float(st.session_state.get("slider_zoom_tab2", 45.0))
    else:
        angle_rot = float(st.session_state.get("slider_rotation", 0.0))
        angle_inc = float(st.session_state.get("slider_inclinaison", 20.0))
        longueur_courante = float(st.session_state.get("slider_zoom", 45.0))
        
    rad_rot = math.radians(angle_rot)
    rad_inc = math.radians(angle_inc)
    
    cos_r = math.cos(rad_rot)
    sin_r = math.sin(rad_rot)
    cos_i = math.cos(rad_inc)
    sin_inc = math.sin(rad_inc)
    
    facteur_echelle = longueur_courante / 45.0

    # 3. Projection tridimensionnelle des atomes (Algorithme d orientation matriciel)
    atomes_projetes = []
    for a in atomes_physique:
        dx = a['x'] - centre_x
        dy = a['y'] - centre_y
        dz = a.get('z', 0.0)
        
        # Rotation Horizontale
        x1 = dx * cos_r - dz * sin_r
        z1 = dx * sin_r + dz * cos_r
        
        # Rotation Verticale
        y2 = dy * cos_i - z1 * sin_inc
        z2 = dy * sin_inc + z1 * cos_i
        
        x_zoome = x1 * facteur_echelle
        y_zoome = y2 * facteur_echelle
        
        atomes_projetes.append({
            'symbole': a['symbole'], 
            'x': x_zoome, 
            'y': y_zoome, 
            'z_profondeur': z2
        })
        
    # Recentrage dynamique automatique sur le canvas de paillasse
    xs_p = [a['x'] for a in atomes_projetes]
    ys_p = [a['y'] for a in atomes_projetes]
    ox = (w_c / 2) - ((min(xs_p) + max(xs_p)) / 2)
    oy = (h_c / 2) - ((min(ys_p) + max(ys_p)) / 2)
    
    # 4. Debut de generation du flux vectoriel SVG
    svg_lignes = []
    svg_lignes.append(f'<svg width="{w_c}" height="{h_c}" xmlns="http://w3.org" style="background-color: white;">')
    
    # Étape A : Dessin des liaisons chimiques (Simples, doubles et triples)
    for idx1, idx2, type_liaison in liaisons_physique:
        x1 = atomes_projetes[idx1]['x'] + ox
        y1 = atomes_projetes[idx1]['y'] + oy
        x2 = atomes_projetes[idx2]['x'] + ox
        y2 = atomes_projetes[idx2]['y'] + oy
        
        dt = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) or 1
        nx = -(y2 - y1) / dt
        ny = (x2 - x1) / dt
        
        # CAS 1 : LIAISON TRIPLE
        if type_liaison == 3 or type_liaison == "triple":
            svg_lignes.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#475569" stroke-width="3" />')
            svg_lignes.append(f'<line x1="{x1 + nx*5}" y1="{y1 + ny*5}" x2="{x2 + nx*5}" y2="{y2 + ny*5}" stroke="#475569" stroke-width="3" />')
            svg_lignes.append(f'<line x1="{x1 - nx*5}" y1="{y1 - ny*5}" x2="{x2 - nx*5}" y2="{y2 - ny*5}" stroke="#475569" stroke-width="3" />')
            
        # CAS 2 : LIAISON DOUBLE
        elif type_liaison == 2 or type_liaison is True:
            svg_lignes.append(f'<line x1="{x1 + nx*3.5}" y1="{y1 + ny*3.5}" x2="{x2 + nx*3.5}" y2="{y2 + ny*3.5}" stroke="#475569" stroke-width="4" />')
            svg_lignes.append(f'<line x1="{x1 - nx*3.5}" y1="{y1 - ny*3.5}" x2="{x2 - nx*3.5}" y2="{y2 - ny*3.5}" stroke="#475569" stroke-width="4" />')
            
        # CAS 3 : LIAISON SIMPLE
        else:
            svg_lignes.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#64748b" stroke-width="4" />')
            
    # Étape B : Dessin des atomes avec tri de profondeur Z (Algorithme du peintre)
    indices_tries = sorted(range(len(atomes_projetes)), key=lambda k: atomes_projetes[k]['z_profondeur'])
    r = max(5, int(longueur_courante * 0.3))
    
    for idx in indices_tries:
        a = atomes_projetes[idx]
        x = a['x'] + ox
        y = a['y'] + oy
        
        # Chargement de la charte de couleur securisee depuis votre STYLE_ATOMES
        cfg = STYLE_ATOMES.get(a['symbole'], {'couleur': "#94a3b8", 'texte': "black"})
        
        # Ajout du cercle de l atome en SVG
        svg_lignes.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{cfg["couleur"]}" stroke="#0f172a" stroke-width="1.5" />')
        
    svg_lignes.append('</svg>')
    return "".join(svg_lignes)

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
    "Modèle moleculaire",
    "Exercice évaluation",

])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]


if "initialise" not in st.session_state:
    # Variables de suivi de l'exercice (Ancien Tab 2)
    st.session_state.molecules_deja_faites = set()
    st.session_state.tentatives = 0
    st.session_state.reussites = 0

    # Variables de calcul du moteur physique
    st.session_state.atomes_physique = []
    st.session_state.liaisons_physique = []
    st.session_state.formule_brute_courante = ""
    st.session_state.masse_molaire_courante = 0.0
    
    # Variables spécifiques au Mode Évaluation (Ancien Tab 2)
    st.session_state.mode_evaluation = False  # False = Entraînement, True = Évaluation
    st.session_state.liste_evaluation_courante = []
    st.session_state.index_evaluation_courant = 0
    st.session_state.notes_par_question = []
    st.session_state.evaluation_deja_faite = False

    # Variables d'identité par défaut
    st.session_state.prenom_var = "INCONNU"
    st.session_state.nom_var = "INCONNU"
    st.session_state.classe_var = "INCONNU"
    
    # Marquage de fin d'initialisation
    st.session_state.initialise = True

with tab1:
    st.markdown("### STRUCTURE ET MODELE MOLECULAIRE")
    
    # --- CHARTE GRAPHIQUE TECHNIQUE DES ATOMES (Ancien configuration_elements) ---
    configuration_elements = [
        {"nom": "hydrogène", "symb": "H", "bg": "#ffffff", "fg": "black", "masse": 1.0},
        {"nom": "carbone", "symb": "C", "bg": "#000000", "fg": "white", "masse": 12.0},
        {"nom": "oxygène", "symb": "O", "bg": "#e74c3c", "fg": "white", "masse": 16.0},
        {"nom": "azote", "symb": "N", "bg": "#3498db", "fg": "white", "masse": 14.0},
        {"nom": "soufre", "symb": "S", "bg": "#ffff00", "fg": "black", "masse": 32.0},
        {"nom": "phosphore", "symb": "P", "bg": "#e67e22", "fg": "white", "masse": 31.0},
        {"nom": "chlore", "symb": "Cl", "bg": "#2ecc71", "fg": "white", "masse": 35.5},
        {"nom": "fer", "symb": "Fe", "bg": "#e67e22", "fg": "white", "masse": 56.0},
        {"nom": "iode", "symb": "I", "bg": "#9400d3", "fg": "white", "masse": 127.0}
    ]

    adjectifs_couleurs = {
        "hydrogène": "blanche", "carbone": "noire", "oxygène": "rouge", 
        "azote": "bleue", "soufre": "jaune", "phosphore": "orange", "chlore": "verte",
        "fer": "marron", "iode": "violette"
    }

    # --- 1. CONFIGURATION DE LA BARRE DE SÉLECTION D'ERGOLS / MOLÉCULES ---
    st.markdown("#### Configuration Technique de la Molécule")
    c_menu1, c_menu2 = st.columns(2)

    if "CATALOGUE_MOLECULES" in globals() or "CATALOGUE_MOLECULES" in locals():
        liste_categories = list(CATALOGUE_MOLECULES.keys())
    else:
        liste_categories = ["Hydrocarbures", "Alcools", "Ergols Spatiaux"]

    with c_menu1:
        cat_choisie = st.selectbox(
            "Catégorie :", 
            options=liste_categories, 
            key="combo_cat_tab1"
        )

    # Récupération automatique des molécules de la sous-catégorie sélectionnée
    if "CATALOGUE_MOLECULES" in globals() and cat_choisie in CATALOGUE_MOLECULES:
        liste_molecules = list(CATALOGUE_MOLECULES[cat_choisie].keys())
    else:
        liste_molecules = ["Molécule Démo A", "Molécule Démo B"]

    with c_menu2:
        mol_choisie = st.selectbox(
            "Molécule :", 
            options=liste_molecules, 
            key="combo_mol_tab1"
        )

    # --- 2. ZONE CONFIGURATION : CHARTE DES SPHÈRES ATOMIQUES (Ancien LabelFrame/Grid) ---
    st.markdown("---")
    st.markdown("<p style='font-weight:bold; color:#2E7D32; font-size:16px;'>LEGENDE ET PROPRIETES DES SPHERES ATOMIQUES</p>", unsafe_allow_html=True)

    # Affichage sous forme de fiches horizontales réparties en colonnes web
    colonnes_atomes = st.columns(len(configuration_elements))

    for idx, atome in enumerate(configuration_elements):
        with colonnes_atomes[idx]:
            adj = adjectifs_couleurs[atome["nom"]]
            st.markdown(
                f"""
                <div style="background-color: #E8F5E9; padding: 8px; border: 1px solid #2E7D32; border-radius: 4px; text-align: center; min-height: 140px;">
                    <span style="font-size: 11px; font-weight: bold; color: #2E7D32;">{atome['nom'].upper()}</span><br>
                    <div style="width: 20px; height: 20px; background-color: {atome['bg']}; border: 1.5px solid #0f172a; border-radius: 50%; margin: 6px auto;"></div>
                    <span style="font-size: 14px; font-weight: bold; color: #0f172a;">{atome['symb']}</span><br>
                    <span style="font-size: 10px; color: #475569;">M = {atome['masse']} g/mol</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    st.markdown("---")

    # --- 3. CALCULS DYNAMIQUES DE MASSE MOLÉCULAIRE (Ancien charger_molecule_tab1) ---
    if mol_choisie:
        # Récupération sécurisée du catalogue local ou global
        if "CATALOGUE_MOLECULES" in globals() and cat_choisie in CATALOGUE_MOLECULES and mol_choisie in CATALOGUE_MOLECULES[cat_choisie]:
            data = CATALOGUE_MOLECULES[cat_choisie][mol_choisie]
            atomes_a_calculer = data.get("atomes", [])
        else:
            atomes_a_calculer = []

        compte = {}
        st.session_state.masse_molaire_courante = 0.0
        
        for a in atomes_a_calculer:
            symb = a.get('symbole', '').upper() if isinstance(a, dict) else a.upper()
            if not River:
                continue
            compte[symb] = compte.get(symb, 0) + 1
            
            for nom_e, donnees_e in ELEMENTS_DB.items():
                symb_db = donnees_e[0].upper()
                m_db = float(donnees_e[2])
                if symb_db == symb:
                    st.session_state.masse_molaire_courante += m_db
                    break

        ordre = sorted(compte.keys(), key=lambda x: (x != 'C', x != 'H', x))
        
        # Reconstruction des données du Treeview sous forme de tableau Pandas
        lignes_tableau = []
        for s in ordre:
            nom_complet = "Inconnu"
            masse_atome_individuel = 0.0
            
            for nom_e, donnees_e in ELEMENTS_DB.items():
                if isinstance(donnees_e, tuple) and len(donnees_e) == 3:
                    symb_db = donnees_e[0].upper()
                    m_db = float(donnees_e[2])
                    if symb_db == s:
                        nom_complet = nom_e.capitalize()
                        masse_atome_individuel = m_db
                        break
            
            quantite = compte[s]
            masse_totale_element = quantite * masse_atome_individuel
            chaine_calcul_detail = f"{quantite} × {masse_atome_individuel:.1f} = {masse_totale_element:.1f} g/mol"
            
            lignes_tableau.append({
                "Symb.": s,
                "Nom Élément": nom_complet,
                "Quantité": int(quantite),
                "Calcul Détaillé": chaine_calcul_detail
            })
            
        st.session_state.formule_brute_courante = "".join([f"{k}{compte[k]}" if compte[k] > 1 else k for k in ordre])
        df_analytique = pd.DataFrame(lignes_tableau)

        # --- 4. AFFICHAGE DES CURSEURS 3D ET DU TABLEAU ANALYTIQUE ---
        col_gauche, col_droite = st.columns([0.55, 0.45])
        
        with col_gauche:
            st.markdown("#### Visualisation Tridimensionnelle")
            slider_zoom = st.slider("Échelle (Zoom) :", min_value=5, max_value=100, value=45, key="slider_zoom")
            slider_inclinaison = st.slider("Inclinaison (Axe X) :", min_value=-90, max_value=90, value=20, key="slider_inclinaison")
            slider_rotation = st.slider("Rotation (Axe Y) :", min_value=0, max_value=360, value=0, key="slider_rotation")
            
            # Rendu dynamique de la molécule en SVG 3D
            html_svg_tab1 = generer_scene_svg_streamlit(cle_onglet="tab1")
            st.components.v1.html(html_svg_tab1, height=350)
            
            # Affichage des informations textuelles
            st.markdown(f"**Nom choisi :** <span style='font-size:16px; color:#0f172a;'>{mol_choisie}</span>", unsafe_allow_html=True)
            
            st.markdown(
                f"""
                <p style="font-size: 14px; margin-top: 10px; background-color: #f1f5f9; padding: 10px; border-radius: 4px; border-left: 4px solid #2563eb;">
                    <strong>Formule brute :</strong> <span style="color:#2563eb; font-weight:bold;">{st.session_state.formule_brute_courante}</span>
                    &nbsp;&nbsp;|&nbsp;&nbsp; 
                    <strong>Masse Molaire :</strong> <strong>{st.session_state.masse_molaire_courante:.1f} g/mol</strong>
                </p>
                """,
                unsafe_allow_html=True
            )
            
        with col_droite:
            st.markdown("#### Tableau Analytique")
            if not df_analytique.empty:
                st.dataframe(df_analytique, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune donnée analytique disponible pour cette molécule.")
                
            quantite_totale_atomes = sum(compte.values()) if compte else 0
            st.markdown(
                f"""
                <table style="width:100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 13px; border-top: 2px solid #cbd5e1; margin-top: 5px;">
                    <tr style="background-color: #f8fafc; font-weight: bold; color: #0f172a;">
                        <td style="padding: 10px; text-align: left;">Bilan Global</td>
                        <td style="padding: 10px; text-align: left;">Atomes au total : <span style="color:#2563eb;">{quantite_totale_atomes}</span></td>
                        <td style="padding: 10px; text-align: right; color: #2e7d32;">M = {st.session_state.masse_molaire_courante:.1f} g/mol</td>
                    </tr>
                </table>
                """,
                unsafe_allow_html=True
            )



with tab2:
    st.markdown("### MODE EXERCICE ET EVALUATION")

    # --- INITIALISATION DES VARIABLES DE SESSION SPECIFIQUES A LA TAB 2 ---
    if "tableau_etudiant_lignes" not in st.session_state:
        st.session_state.tableau_etudiant_lignes = []
    if "score_exercice" not in st.session_state:
        st.session_state.score_exercice = 0
    if "total_exercice" not in st.session_state:
        st.session_state.total_exercice = 0

    # --- BARRE D'OUTILS ET SELECTION DU MODE DE JEU ---
    st.markdown("#### Configuration de la session")
    c_mode1, c_mode2 = st.columns([0.4, 0.6])
    
    with c_mode1:
        # Remplacement des Radiobuttons Tkinter
        mode_selectionne = st.radio(
            "Choix du mode :",
            options=["Entrainement Libre", "Evaluation (Note sur 20)"],
            key="radio_mode_exercice"
        )
        st.session_state.mode_evaluation = (mode_selectionne == "Evaluation (Note sur 20)")

    # Chargement dynamique des categories et molecules pour l'exercice
    if "CATALOGUE_MOLECULES" in globals() or "CATALOGUE_MOLECULES" in locals():
        liste_categories_t2 = list(CATALOGUE_MOLECULES.keys())
    else:
        liste_categories_t2 = ["Hydrocarbures", "Alcools"]

    with c_mode2:
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            cat_choisie_t2 = st.selectbox("Categorie :", options=liste_categories_t2, key="combo_cat_tab2")
        with c_sub2:
            if "CATALOGUE_MOLECULES" in globals() and cat_choisie_t2 in CATALOGUE_MOLECULES:
                liste_molecules_t2 = list(CATALOGUE_MOLECULES[cat_choisie_t2].keys())
            else:
                liste_molecules_t2 = ["Molecule Demo A"]
            mol_choisie_t2 = st.selectbox("Molecule :", options=liste_molecules_t2, key="combo_mol_tab2")

    # Configuration des curseurs de manipulation visuelle de la Tab 2
    c_sl1, c_sub_scale, c_sl2 = st.columns(3)
    with c_sl1:
        slider_rotation_t2 = st.slider("Rotation :", min_value=0, max_value=360, value=0, key="slider_rotation_tab2")
    with c_sub_scale:
        slider_zoom_t2 = st.slider("Echelle :", min_value=30, max_value=80, value=45, key="slider_zoom_tab2")
    with c_sl2:
        slider_inclinaison_t2 = st.slider("Inclinaison :", min_value=-90, max_value=90, value=20, key="slider_inclinaison_tab2")

    # Affichage du score textuel global (Ancien lbl_score_tab2 / lbl_note_permanente)
    st.markdown(
        f"""
        <div style="background-color: #cbd5e1; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 15px;">
            <span style="font-size: 18px; font-weight: bold; color: #0f172a;">
                Score de session actuel : {st.session_state.score_exercice} / {st.session_state.total_exercice}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- REPRODUCTION DES SPHERES ATOMIQUES DONNEES (Ancien LabelFrame) ---
    st.markdown("<p style='font-weight:bold; color:#2E7D32; font-size:14px; margin-top:10px;'>DONNEES COMPLEMENTAIRES DISPONIBLES</p>", unsafe_allow_html=True)
    configuration_elements_t2 = [
        {"nom": "hydrogène", "symb": "H", "bg": "#ffffff", "masse": "1"},
        {"nom": "carbone", "symb": "C", "bg": "#000000", "masse": "12"},
        {"nom": "oxygène", "symb": "O", "bg": "#e74c3c", "masse": "16"},
        {"nom": "azote", "symb": "N", "bg": "#3498db", "masse": "14"},
        {"nom": "soufre", "symb": "S", "bg": "#ffff00", "masse": "32"}
    ]
    
    cols_atomes_t2 = st.columns(len(configuration_elements_t2))
    for idx, at in enumerate(configuration_elements_t2):
        with cols_atomes_t2[idx]:
            st.markdown(
                f"""
                <div style="background-color: #E8F5E9; padding: 5px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px;">
                    <strong>{at['symb']}</strong> ({at['nom']})<br>
                    M = {at['masse']} g/mol
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # --- ZONE CENTRALE : AFFICHAGE DU MODELE ET DU FORMULAIRE ETUDIANT ---
    col_visuel, col_formulaire = st.columns([0.50, 0.50])

    with col_visuel:
        st.markdown(f"##### Visualisation de l'exercice : {mol_choisie_t2}")
        
        # Rendu dynamique SVG de la molécule mystère
        html_svg_tab2 = generer_scene_svg_streamlit(cle_onglet="tab2")
        st.components.v1.html(html_svg_tab2, height=350)

    with col_formulaire:
        st.markdown("##### VOTRE TABLEAU D'ANALYSE")

        # Affichage dynamique du tableau de l'etudiant (Ancien Treeview_exercice)
        if st.session_state.tableau_etudiant_lignes:
            df_exercice = pd.DataFrame(st.session_state.tableau_etudiant_lignes)
            st.dataframe(df_exercice, use_container_width=True, hide_index=True)
            
            if st.button("Reinitialiser le tableau", key="btn_clear_table"):
                st.session_state.tableau_etudiant_lignes = []
                st.rerun()
        else:
            st.info("Votre tableau d'analyse est vide. Utilisez le module ci-dessous pour ajouter vos lignes.")

        # --- MODULE D'AJOUT RAPIDE D'UNE LIGNE AU TABLEAU (Ancien cadre_saisie_ligne) ---
        st.markdown("<p style='font-weight:bold; font-size:13px; color:#475569; margin-top:10px;'>Ajouter un constituant au tableau</p>", unsafe_allow_html=True)
        
        c_add1, c_add2, c_add3 = st.columns(3)
        with c_add1:
            symb_input = st.text_input("Symbole (C, H, O...) :", key="entry_ajout_symb", max_chars=2)
        with c_add2:
            qty_input = st.number_input("Quantite comptee :", key="entry_ajout_qty", min_value=0, step=1)
        with c_add3:
            masse_input = st.number_input("Masse calculee :", key="entry_ajout_masse", min_value=0.0, step=0.1)

        if st.button("Inserer cette ligne", key="btn_insert_line", use_container_width=True):
            if symb_input.strip() == "":
                st.error("Saisie invalide : Indiquez le symbole de l'atome.")
            else:
                # Ajout de la ligne dans la memoire de session (Equivalent a self.inserer_ligne_etudiant)
                st.session_state.tableau_etudiant_lignes.append({
                    "Symb.": symb_input.strip().upper(),
                    "Nom Element": "A valider",
                    "Quantite": int(qty_input),
                    "Masse Calc.": float(masse_input)
                })
                st.success(f"Ligne {symb_input.upper()} ajoutee avec succes.")
                st.rerun()

        st.markdown("---")

        # Case finale pour l'estimation de la masse molaire moleculaire totale
        masse_totale_etudiant = st.number_input(
            "Masse Molaire Totale de la Molecule (g/mol) :", 
            key="entry_masse_totale_etudiant",
            min_value=0.0,
            step=0.1
        )

        # --- POSITIONNEMENT DES BOUTONS DE FIN SACCADES ---
        # 1. Le bouton de verification (Bleu)
        if st.button("Verifier mon tableau d'analyse", key="btn_verifier_t2", use_container_width=True):
            # Liaison immediate vers votre ancienne logique de correction
            # Exemple : self.verifier_exercice()
            st.success("Analyse soumise au moteur academique.")

        # 2. Le bouton molecule suivante (Gris, debloque uniquement apres validation ou en entrainement)
        verrou_bouton_suivant = st.session_state.get("mode_evaluation", False)
        if st.button("Molecule suivante", key="btn_suivant_t2", use_container_width=True, disabled=verrou_bouton_suivant):
            # Liaison immediate vers votre logique d'avancement
            # Exemple : self.passer_exercice_suivant()
            st.session_state.tableau_etudiant_lignes = []
            st.rerun()















