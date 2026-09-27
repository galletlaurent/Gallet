# -*- coding: utf-8 -*-

import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application optique",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from datetime import datetime
from itertools import combinations, product
import math
import random
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import time 

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

if "milieu_refraction_1" not in st.session_state:
    st.session_state.milieu_refraction_1 = "Air (n = 1.00)"
if "milieu_refraction_2" not in st.session_state:
    st.session_state.milieu_refraction_2 = "Eau (n = 1.33)"
if "var_angle_refraction_i1" not in st.session_state:
    st.session_state.var_angle_refraction_i1 = 30.0
if "var_texte_resultats_refraction" not in st.session_state:
    st.session_state.var_texte_resultats_refraction = ""

# Variables pour le controle d'examen de l'Atelier 4
if "mode_examen_tab4" not in st.session_state:
    st.session_state.mode_examen_tab4 = False
if "quiz4_valide" not in st.session_state:
    st.session_state.quiz4_valide = False
if "quiz4_score_txt" not in st.session_state:
    st.session_state.quiz4_score_txt = ""
# 3. INITIALISATION DES INTERRUPTEURS ET ETATS DE MANIPULATION
if "var_sel_metal" not in st.session_state:
    st.session_state.var_sel_metal = "Sodium (Na)"
if "source_lumineuse_choisie" not in st.session_state:
    st.session_state.source_lumineuse_choisie = "Lumière du Soleil"
if "var_combustion_active" not in st.session_state:
    st.session_state.var_combustion_active = False
if "var_versement_poudre" not in st.session_state:
    st.session_state.var_versement_poudre = False

# Variables de controle d'examen pour le volet 2
if "mode_examen_tab2" not in st.session_state:
    st.session_state.mode_examen_tab2 = False
if "quiz2_valide" not in st.session_state:
    st.session_state.quiz2_valide = False
if "quiz2_score_txt" not in st.session_state:
    st.session_state.quiz2_score_txt = ""


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
if "roulette_dernier_numero" not in st.session_state:
    st.session_state.roulette_dernier_numero = 0


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
    "1. Décomposition de la lumière",
    "2. Les différentes lumières",
    "3. La loi de la réflexion",
    "4. La loi de la réfraction",
    "5. Les lentilles convergentes",
    "6. Les lentilles divergentes",
    "7. La lunette astronomique",
    "8. La lunette de Galilée",
    "9. Le microscope"
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


def afficher_questions_optique9(verrouille=False):
    col_double_quiz_opt9, col_double_trous_opt9 = st.columns(2)

    with col_double_quiz_opt9:
        st.markdown("##### Quiz sur le microscope (10 questions) - Optique 9 (10 pts)")
        if "ordre_questions_opt9" not in st.session_state:
            questions_opt9_base = [
                ("q1", "Dans un microscope, la premiere lentille convergente tres puissante pres de l'objet s'appelle l' :"),
                ("q2", "La distance fixe separent le foyer image de l'objectif F'1 et le foyer objet de l'oculaire F2 est appelee l' :"),
                ("q3", "L'image intermediaire A1B1 creee par l'objectif du microscope est une image :"),
                ("q4", "La seconde lentille (l'oculaire) joue le role d'une loupe. Elle observe l'image intermédiaire placee :"),
                ("q5", "Pour un confort visuel maximal de l'observateur (oeil au repos sans accommoder), l'image finale doit se former :"),
                ("q6", "Le grandissement transversal de l'objectif d'un microscope est une grandeur physique de signe :"),
                ("q7", "Le grossissement total G du microscope est egal au produit du grossissement de l'oculaire par :"),
                ("q8", "Si le grandissement de l'objectif vaut -10 et le grossissement de l'oculaire vaut 4, le grossissement total vaut :"),
                ("q9", "Par rapport a l'objet micro-optique reel place sur la platine, l'image finale observee est :"),
                ("q10", "La puissance d'un microscope s'exprime couramment en dioptries ou par son grossissement commercial note :")
            ]
            import random
            random.shuffle(questions_opt9_base)
            st.session_state.ordre_questions_opt9 = questions_opt9_base

        dict_quiz_opt9 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt9, 1):
            cle_qo9 = f"col_g_quiz_opt9_{q_id}"
            cle_opts_unique = f"opts_opt9_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Objectif (de tres courte distance focale)", "Oculaire", "Condenseur de champ"]
                elif q_id == "q2": copie_opts = ["Intervalle optique Delta", "Distance focale totale", "Longueur mecanique du tube"]
                elif q_id == "q3": copie_opts = ["Reelle, renversee et tres agrandie", "Virtuelle, droite et plus petite", "Virtuelle et renversee"]
                elif q_id == "q4": copie_opts = ["Pile dans son plan focal objet (foyer F2)", "Sur son centre optique O2", "A l'infini en aval"]
                elif q_id == "q5": copie_opts = ["A l'infini", "Sur la lentille objectif", "Au niveau du cercle oculaire"]
                elif q_id == "q6": copie_opts = ["Negatif (car l'image intermediaire est renversee)", "Positif", "Nul"]
                elif q_id == "q7": copie_opts = ["Le grandissement de l'objectif", "La vergence de l'objectif", "La distance focale de l'oculaire"]
                elif q_id == "q8": copie_opts = ["-40", "40", "-2.5"]
                elif q_id == "q9": copie_opts = ["Renversee et fortement agrandie", "Droite et agrandie", "Renversee et plus petite"]
                elif q_id == "q10": copie_opts = ["Un nombre suivi de la lettre X (ex: x40)", "Un angle en radians", "Une valeur en metres"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo9, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt9[f"{q_id}_opt9"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo9, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_opt9:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 9 (10 pts)")
        
        co9_1, co9_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_1: st.write("Le microscope compose utilise deux systemes convergents. Le premier est l'")
        with co9_2: t1 = st.selectbox("", ["Choisir...", "Objectif", "Oculaire", "Miroir"], key="opt9_t1", disabled=verrouille, label_visibility="collapsed")
        
        co9_3, co9_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_3: st.write("de tres courte focale, qui genere une image intermediaire reelle. Le second est l'")
        with co9_4: t2 = st.selectbox("", ["Choisir...", "Oculaire", "Objectif", "Prisme"], key="opt9_t2", disabled=verrouille, label_visibility="collapsed")

        co9_5, co9_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_5: st.write("qui fait office de loupe pour observer cette derniere. La distance fixe F'1F2 s'appelle l'")
        with co9_6: t3 = st.selectbox("", ["Choisir...", "Intervalle optique", "Axe de visée", "Diametre utile"], key="opt9_t3", disabled=verrouille, label_visibility="collapsed")

        co9_7, co9_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co9_7: st.write("L'image finale de la structure cellulaire ou micro-mecanique est ainsi rejetee a l'infini.")

        dict_trous_opt9 = {
            "t1_opt9": t1, "t2_opt9": t2, "t3_opt9": t3
        }

    return dict_quiz_opt9, dict_trous_opt9

def afficher_questions_optique8(verrouille=False):
    col_double_quiz_opt8, col_double_trous_opt8 = st.columns(2)

    with col_double_quiz_opt8:
        st.markdown("##### Quiz sur la lunette de Galilee (10 questions) - Optique 8 (10 pts)")
        if "ordre_questions_opt8" not in st.session_state:
            questions_opt8_base = [
                ("q1", "Quelle est la principale difference de constitution entre la lunette de Galilee et celle de Kepler :"),
                ("q2", "L'oculaire utilise dans une lunette de Galilee possede une distance focale f'2 :"),
                ("q3", "Pour qu'une lunette de Galilee soit afocale, le foyer image F'1 de l'objectif doit etre confondu avec :"),
                ("q4", "Par rapport a la lunette de Kepler, l'image finale observee a travers la lunette de Galilee est :"),
                ("q5", "L'encombrement de l'instrument (distance O1O2) d'une lunette de Galilee afocale est egal a :"),
                ("q6", "La distance separent les deux lentilles O1O2 d'une lunette de Galilee est necessairement :"),
                ("q7", "Le grossissement nominal G d'une lunette afocale est calculé par G = - f'1 / f'2. Pour Galilee, G est :"),
                ("q8", "Si l'objectif fait f'1 = 60 cm et l'oculaire f'2 = -15 cm, le grossissement G vaut :"),
                ("q9", "Quel est l'inconvenient principal d'une lunette de Galilee par rapport a une lunette de Kepler :"),
                ("q10", "Dans quel instrument grand public retrouve-t-on couramment le systeme optique de Galilee :")
            ]
            import random
            random.shuffle(questions_opt8_base)
            st.session_state.ordre_questions_opt8 = questions_opt8_base

        dict_quiz_opt8 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt8, 1):
            cle_qo8 = f"col_g_quiz_opt8_{q_id}"
            cle_opts_unique = f"opts_opt8_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["L'oculaire de Galilee est une lentille divergente", "L'objectif de Galilee est une lentille divergente", "Galilee comporte trois miroirs prismatiques"]
                elif q_id == "q2": copie_opts = ["Strictement negative (f'2 < 0)", "Strictement positive (f'2 > 0)", "Rigoureusement nulle"]
                elif q_id == "q3": copie_opts = ["Le foyer objet F2 de l'oculaire divergent", "Le foyer image F'2 de l'oculaire divergent", "Le centre optique O2"]
                elif q_id == "q4": copie_opts = ["Droite (dans le meme sens que l'astre)", "Renversee (haut-bas)", "Inclinee a 90 degres"]
                elif q_id == "q5": copie_opts = ["f'1 + f'2 (ce qui donne une soustraction car f'2 est negatif)", "f'1 - f'2 (ce qui donne une addition)", "f'1 * f'2"]
                elif q_id == "q6": copie_opts = ["Plus courte que celle de Kepler", "Plus longue que celle de Kepler", "Rigoureusement identique"]
                elif q_id == "q7": copie_opts = ["Positif (l'image finale est droite)", "Negatif (l'image finale est inversee)", "Nul"]
                elif q_id == "q8": copie_opts = ["4.0 (car f'2 est negatif)", "-4.0", "0.25"]
                elif q_id == "q9": copie_opts = ["Un champ visuel tres etroit", "Une image totalement floue au centre", "Une perte totale de luminosite"]
                elif q_id == "q10": copie_opts = ["Les jumelles de theatre (ou de spectacle)", "Les microscopes biologiques", "Les telemetres de topographie"]
                import random
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
        
        co8_1, co8_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_1: st.write("La lunette de Galilee se distingue par l'utilisation d'un oculaire de nature")
        with co8_2: t1 = st.selectbox("", ["Choisir...", "Divergente", "Convergente", "Prismatique"], key="opt8_t1", disabled=verrouille, label_visibility="collapsed")
        
        co8_3, co8_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_3: st.write("Pour obtenir la configuration afocale, le foyer image de l'objectif coincide avec le foyer")
        with co8_4: t2 = st.selectbox("", ["Choisir...", "Objet F2", "Image F'2", "Central O2"], key="opt8_t2", disabled=verrouille, label_visibility="collapsed")

        co8_5, co8_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_5: st.write("de l'oculaire. L'avantage majeur de ce montage est de generer une image finale")
        with co8_6: t3 = st.selectbox("", ["Choisir...", "Droite", "Inversee", "Virtuelle pure"], key="opt8_t3", disabled=verrouille, label_visibility="collapsed")

        co8_7, co8_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co8_7: st.write("ce qui dispense de l'utilisation d'un vehicule de redressement. Son grossissement est")
        with col_double_trous_opt8: st.write("calcule positivement par le rapport des focales.")

        dict_trous_opt8 = {
            "t1_opt8": t1, "t2_opt8": t2, "t3_opt8": t3
        }

    return dict_quiz_opt8, dict_trous_opt8



def afficher_questions_optique7(verrouille=False):
    col_double_quiz_opt7, col_double_trous_opt7 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES SUR LA LUNETTE ---
    with col_double_quiz_opt7:
        st.markdown("##### Quiz sur la lunette astronomique (10 questions) - Optique 7 (10 pts)")
        if "ordre_questions_opt7" not in st.session_state:
            questions_opt7_base = [
                ("q1", "Dans une lunette astronomique, la premiere lentille qui reçoit les rayons de l'astre est l' :"),
                ("q2", "La seconde lentille devant laquelle l'observateur place son oeil s'appelle l' :"),
                ("q3", "Une lunette astronomique est dite 'afocale' si l'image d'un objet situe a l'infini se forme :"),
                ("q4", "Pour qu'une lunette soit parfaitement afocale, il faut que le foyer image F'1 de l'objectif soit confondu avec :"),
                ("q5", "Quelle est la nature de l'image intermediaire A1B1 creee entre l'objectif et l'oculaire :"),
                ("q6", "L'image finale de l'astre observee par l'etudiant a travers la lunette afocale est situee :"),
                ("q7", "Le grossissement G d'une lunette afocale est donne par le rapport des distances focales :"),
                ("q8", "Si l'objectif a une focale f'1 = 100 cm et l'oculaire f'2 = 5 cm, le grossissement G de la lunette vaut :"),
                ("q9", "Par rapport a l'astre reel pointe dans le ciel, l'image finale observee a travers la lunette est :"),
                ("q10", "Le cercle oculaire correspond a la zone ou la luminosite est maximale. Il est l'image de :")
            ]
            import random
            random.shuffle(questions_opt7_base)
            st.session_state.ordre_questions_opt7 = questions_opt7_base

        dict_quiz_opt7 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt7, 1):
            cle_qo7 = f"col_g_quiz_opt7_{q_id}"
            cle_opts_unique = f"opts_opt7_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Objectif (de grande distance focale)", "Oculaire (de courte distance focale)", "Miroir parabolique"]
                elif q_id == "q2": copie_opts = ["Oculaire", "Objectif", "Diaphragme de champ"]
                elif q_id == "q3": copie_opts = ["A l'infini (confort de vision sans fatigue pour l'oeil)", "Sur le centre optique O1", "Entre les deux lentilles"]
                elif q_id == "q4": copie_opts = ["Le foyer objet F2 de l'oculaire", "Le foyer image F'2 de l'oculaire", "Le centre optique O2"]
                elif q_id == "q5": copie_opts = ["Reelle et renversee (situee dans le plan focal commun)", "Virtuelle et droite", "Reelle et droite"]
                elif q_id == "q6": copie_opts = ["A l'infini (pas besoin d'accommoder)", "A la distance minimale de vision distincte", "Pile sur la lentille oculaire"]
                elif q_id == "q7": copie_opts = ["G = f'1 / f'2", "G = f'2 / f'1", "G = f'1 * f'2"]
                elif q_id == "q8": copie_opts = ["20", "200", "0.05"]
                elif q_id == "q9": copie_opts = ["Renversee (haut-bas et droite-gauche)", "Droite (dans le meme sens)", "Inclinee a 45 degres"]
                elif q_id == "q10": copie_opts = ["L'objectif par l'oculaire", "L'oculaire par l'objectif", "L'astre par l'oculaire"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo7, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt7[f"{q_id}_opt7"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo7, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE DU DOUBLE SYSTÈME AFOCAL ---
    with col_double_trous_opt7:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 7 (10 pts)")
        
        co7_1, co7_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_1: st.write("La lunette astronomique est composee de deux lentilles convergentes. La premiere est l'")
        with co7_2: t1 = st.selectbox("", ["Choisir...", "Objectif", "Oculaire", "Inverseur"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")
        
        co7_3, co7_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_3: st.write("de grande distance focale, et la seconde, proche de l'oeil, est l'")
        with co7_4: t2 = st.selectbox("", ["Choisir...", "Oculaire", "Objectif", "Prisme"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

        co7_5, co7_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_5: st.write("Lorsque le foyer image de la premiere coincide avec le foyer objet de la seconde, le systeme est")
        with co7_6: t3 = st.selectbox("", ["Choisir...", "Afocal", "Convergent", "Divergent"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

        co7_7, co7_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co7_7: st.write("L'image d'un astre lointain sort alors a l'infini, permettant d'observer sans fatigue. Le")
        with co7_8: t4 = st.selectbox("", ["Choisir...", "Grossissement", "Grandissement", "Champ"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")
        
        st.write("de l'appareil correspond au rapport de la focale de l'objectif sur celle de l'oculaire.")

        dict_trous_opt7 = {
            "t1_opt7": t1, "t2_opt7": t2, "t3_opt7": t3, "t4_opt7": t4
        }

    return dict_quiz_opt7, dict_trous_opt7

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



def afficher_questions_optique5(verrouille=False):
    col_double_quiz_opt5, col_double_trous_opt5 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES SUR LES LENTILLES ---
    with col_double_quiz_opt5:
        st.markdown("##### Quiz sur les lentilles convergentes (10 questions) - Optique 5 (10 pts)")
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

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE DES LENTILLES ---
    with col_double_trous_opt5:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 5 (10 pts)")
        
        co5_1, co5_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_1: st.write("Une lentille mince possede des bords plus minces que son centre. Elle est qualifiee de")
        with co5_2: t1 = st.selectbox("", ["Choisir...", "Convergente", "Divergente", "Cylindrique"], key="opt5_t1", disabled=verrouille, label_visibility="collapsed")
        
        co5_3, co5_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_3: st.write("Tout rayon incident parallele a l'axe optique ressort en convergeant vers le foyer")
        with co5_4: t2 = st.selectbox("", ["Choisir...", "Image F'", "Objet F", "Central O"], key="opt5_t2", disabled=verrouille, label_visibility="collapsed")

        co5_5, co5_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_5: st.write("La relation de conjugaison permet de calculer la position x' de l'image. Sa vergence s'exprime en")
        with co5_6: t3 = st.selectbox("", ["Choisir...", "Dioptries", "Metres", "Degres"], key="opt5_t3", disabled=verrouille, label_visibility="collapsed")

        co5_7, co5_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co5_7: st.write("Enfin, le rapport des dimensions entre l'image et l'objet definit le")
        with co5_8: t4 = st.selectbox("", ["Choisir...", "Grandissement", "Pouvoir separateur", "Facteur de forme"], key="opt5_t4", disabled=verrouille, label_visibility="collapsed")

        dict_trous_opt5 = {
            "t1_opt5": t1, "t2_opt5": t2, "t3_opt5": t3, "t4_opt5": t4
        }

    return dict_quiz_opt5, dict_trous_opt5



def afficher_questions_optique4(verrouille=False):
    col_double_quiz_opt4, col_double_trous_opt4 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DE CONNAISSANCES DE LA RÉFRACTION ---
    with col_double_quiz_opt4:
        st.markdown("##### Quiz sur la refraction (10 questions) - Optique 4 (10 pts)")
        if "ordre_questions_opt4" not in st.session_state:
            questions_opt4_base = [
                ("q1", "D'apres la deuxieme loi de Snell-Descartes pour la refraction, la relation exacte est :"),
                ("q2", "Lorsqu'un rayon lumineux passe d'un milieu moins refringent (Air) a un milieu plus refringent (Eau) :"),
                ("q3", "Si le rayon incident arrive perpendiculairement a la surface de separation (sur la normale), l'angle i2 vaut :"),
                ("q4", "Quel est l'indice de refraction theorique de l'air ou du vide servant de reference :"),
                ("q5", "L'indice de refraction n d'un milieu transparent est calcule par le rapport c/v. Il est donc toujours :"),
                ("q6", "Dans une lame a faces paralleles (double refraction), comment ressort le rayon emergent par rapport au rayon incident :"),
                ("q7", "Le phenomene de mirage optique observe sur une route surchauffee est une consequence directe de la :"),
                ("q8", "Comment appelle-t-on la surface plane qui separe les deux milieux transparents differents (ex: Air/Eau) :"),
                ("q9", "Si l'angle d'incidence augmente dans le milieu 1, l'angle de refraction dans le milieu 2 va necessairement :"),
                ("q10", "Lorsqu'on trace le graphique de sin(i1) en fonction de sin(i2), on obtient une droite dont la pente vaut :")
            ]
            import random
            random.shuffle(questions_opt4_base)
            st.session_state.ordre_questions_opt4 = questions_opt4_base

        dict_quiz_opt4 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt4, 1):
            cle_qo4 = f"col_g_quiz_opt4_{q_id}"
            cle_opts_unique = f"opts_opt4_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["n1 * sin(i1) = n2 * sin(i2)", "n1 * sin(i2) = n2 * sin(i1)", "n1 * cos(i1) = n2 * cos(i2)"]
                elif q_id == "q2": copie_opts = ["Le rayon se rapproche de la normale", "Le rayon s'eloigne de la normale", "Le rayon continue en ligne droite sans devier"]
                elif q_id == "q3": copie_opts = ["0 degres", "90 degres", "45 degres"]
                elif q_id == "q4": copie_opts = ["1.00", "1.33", "1.50"]
                elif q_id == "q5": copie_opts = ["Superieur ou egal a 1", "Inferieur a 1", "Egal a zero"]
                elif q_id == "q6": copie_opts = ["Parallele (avec un decalage lateral dx)", "Perpendiculaire", "Incline a 45 degres"]
                elif q_id == "q7": copie_opts = ["Refraction (courbure des rayons)", "Reflexion pure", "Dispersion prismatique"]
                elif q_id == "q8": copie_opts = ["Le dioptre", "La normale", "L'axe optique"]
                elif q_id == "q9": copie_opts = ["Augmenter", "Diminuer", "Rester rigoureusement fixe"]
                elif q_id == "q10": copie_opts = ["Le rapport des indices n2 / n1", "L'indice n1 uniquement", "La valeur de l'angle limite"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo4, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt4[f"{q_id}_opt4"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo4, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE DES LOIS DE DESCARTES ---
    with col_double_trous_opt4:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 4 (10 pts)")
        
        co4_1, co4_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co4_1: st.write("Lorsqu'un rayon lumineux traverse la surface de separation appelee")
        with co4_2: t1 = st.selectbox("", ["Choisir...", "Dioptre", "Normale", "Miroir"], key="opt4_t1", disabled=verrouille, label_visibility="collapsed")
        
        co4_3, co4_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co4_3: st.write("il change de direction. Ce phenomene de deviation s'appelle la")
        with co4_4: t2 = st.selectbox("", ["Choisir...", "Refraction", "Reflexion", "Dispersion"], key="opt4_t2", disabled=verrouille, label_visibility="collapsed")

        co4_5, co4_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co4_5: st.write("La loi associee lie le produit de l'indice de refraction par le")
        with co4_6: t3 = st.selectbox("", ["Choisir...", "Sinus", "Cosinus", "Tangente"], key="opt4_t3", disabled=verrouille, label_visibility="collapsed")

        co4_7, co4_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co4_7: st.write("de l'angle de rayonnement. Dans le cas d'une lame a faces paralleles, le rayon")
        with co4_8: t4 = st.selectbox("", ["Choisir...", "Emergent", "Incident", "Reflechi"], key="opt4_t4", disabled=verrouille, label_visibility="collapsed")

        co4_9, co4_10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co4_9: st.write("qui sort de la structure reste rigoureusement parallele au rayon d'entree.")
        with co4_10: st.write("")

        dict_trous_opt4 = {
            "t1_opt4": t1, "t2_opt4": t2, "t3_opt4": t3, "t4_opt4": t4
        }

    return dict_quiz_opt4, dict_trous_opt4




def afficher_questions_optique3(verrouille=False):
    col_double_quiz_opt3, col_double_trous_opt3 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ INTERACTIF ---
    with col_double_quiz_opt3:
        st.markdown("##### Quiz sur la reflexion (10 questions) - Optique 3 (10 pts)")
        if "ordre_questions_opt3" not in st.session_state:
            questions_opt3_base = [
                ("q1", "D'apres la premiere loi de Snell-Descartes pour la reflexion, l'angle i' vaut :"),
                ("q2", "Par rapport a quelle ligne imaginaire mesure-t-on les angles d'incidence et de reflexion :"),
                ("q3", "Si un rayon incident arrive avec un angle de 35° par rapport a la normale, l'angle de reflexion vaut :"),
                ("q4", "Pour obtenir l'illusion parfaite du Spectre de Pepper, l'angle du miroir doit valoir :"),
                ("q5", "Si un rayon est perpendiculaire a la surface du miroir (incident sur la normale), l'angle i vaut :"),
                ("q6", "Le phenomene ou la lumiere rebondit sur une surface lisse sans changer de milieu s'appelle la :"),
                ("q7", "L'image d'un objet formee par un miroir plan est une image qualifiee de :"),
                ("q8", "Si le conducteur modifie sa position dans le siege, les angles de visibilite des retroviseurs :"),
                ("q9", "Un miroir plan inverse-t-il la droite et la gauche de l'objet observe :"),
                ("q10", "La somme de l'angle d'incidence et de l'angle entre le rayon et le miroir vaut toujours :")
            ]
            import random
            random.shuffle(questions_opt3_base)
            st.session_state.ordre_questions_opt3 = questions_opt3_base

        dict_quiz_opt3 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt3, 1):
            cle_qo3 = f"col_g_quiz_opt3_{q_id}"
            cle_opts_unique = f"opts_opt3_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Strictement l'angle i", "Le double de l'angle i", "90° - i"]
                elif q_id == "q2": copie_opts = ["La normale au miroir", "La surface du miroir", "L'axe horizontal du repere"]
                elif q_id == "q3": copie_opts = ["35°", "55°", "70°"]
                elif q_id == "q4": copie_opts = ["45°", "90°", "0°"]
                elif q_id == "q5": copie_opts = ["0°", "90°", "45°"]
                elif q_id == "q6": copie_opts = ["Reflexion", "Refraction", "Dispersion"]
                elif q_id == "q7": copie_opts = ["Virtuelle", "Reelle", "Inversee haut-bas"]
                elif q_id == "q8": copie_opts = ["Changent (il faut reregler)", "Restent identiques", "S'annulent"]
                elif q_id == "q9": copie_opts = ["Oui", "Non", "Seulement si le miroir est courbe"]
                elif q_id == "q10": copie_opts = ["90°", "180°", "45°"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo3, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt3[f"{q_id}_opt3"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo3, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS ---
    with col_double_trous_opt3:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 3 (10 pts)")
        
        co3_1, co3_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co3_1: st.write("La premiere loi de Snell-Descartes demontre que l'angle de reflexion est toujours")
        with co3_2: t1 = st.selectbox("", ["Choisir...", "Egal", "Superieur", "Inferieur"], key="opt3_t1", disabled=verrouille, label_visibility="collapsed")
        
        co3_3, co3_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co3_3: st.write("a l'angle d'incidence. Les angles de rayonnements se mesurent obligatoirement par rapport a la")
        with co3_4: t2 = st.selectbox("", ["Choisir...", "Normale", "Surface", "Tangente"], key="opt3_t2", disabled=verrouille, label_visibility="collapsed")

        co3_5, co3_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co3_5: st.write("au miroir. L'illusion spectrale utilise une inclinaison precise du miroir a un angle de")
        with co3_6: t3 = st.selectbox("", ["Choisir...", "45", "90", "60"], key="opt3_t3", disabled=verrouille, label_visibility="collapsed")
        with co3_6: st.write("degres.")

        dict_trous_opt3 = {
            "t1_opt3": t1, "t2_opt3": t2, "t3_opt3": t3
        }

    return dict_quiz_opt3, dict_trous_opt3

def afficher_questions_optique2(verrouille=False):
    col_double_quiz_opt2, col_double_trous_opt2 = st.columns(2)

    # --- COLONNE DE GAUCHE : VOTRE QUIZ DE 10 QUESTIONS D'ORIGINE ---
    with col_double_quiz_opt2:
        st.markdown("##### Evaluation : Les differentes lumieres (10 pts)")
        if "ordre_questions_opt2" not in st.session_state:
            questions_opt2_base = [
                ("q1", "Quel type de spectre obtient-on en analysant la lumiere emise par un gaz d'atomes isoles excites ?"),
                ("q2", "Quelle source lumineuse classique produit un spectre continu contenant toutes les radiations colorees ?"),
                ("q3", "Lors du test de flamme, quelle couleur caracteristique prend la combustion du chlorure de Sodium (Na) ?"),
                ("q4", "Quelle couleur de flamme specifique permet d'identifier la presence d'ions Cuivre (Cu) ?"),
                ("q5", "Pourquoi les raies d'emission d'un element chimique constituent-elles sa signature ou carte d'identite ?"),
                ("q6", "Comment qualifie-t-on le spectre d'une etoile qui traverse une atmosphere gazeuse plus froide ?"),
                ("q7", "Quel instrument d'optique muni d'un element dispersif permet d'observer ces raies colorees ?"),
                ("q8", "Quelle est l'unite de mesure utilisee pour reperer la position exacte d'une raie sur l'ecran ?"),
                ("q9", "Si une source emet une raie unique a 589 nm, dans quel domaine de couleur se situe-t-elle ?"),
                ("q10", "Le spectre de la lumiere emise par le Soleil recu sur Terre est un spectre :")
            ]
            import random
            random.shuffle(questions_opt2_base)
            st.session_state.ordre_questions_opt2 = questions_opt2_base

        dict_quiz_opt2 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt2, 1):
            cle_qo2 = f"col_g_quiz_opt2_{q_id}"
            cle_opts_unique = f"opts_opt2_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["Spectre d'emission de raies", "Spectre continu", "Spectre d'absorption"]
                elif q_id == "q2": copie_opts = ["Corps dense incandescent (Lampe a filament)", "Lampe a vapeur de gaz", "Laser monochromatique"]
                elif q_id == "q3": copie_opts = ["Jaune orange intense", "Vert pre", "Bleu azur"]
                elif q_id == "q4": copie_opts = ["Vert pre / turquoise", "Jaune orange", "Violet pourpre"]
                elif q_id == "q5": copie_opts = ["Chaque element a des raies uniques", "Elles dependent de la temperature", "Elles sont toutes blanches"]
                elif q_id == "q6": copie_opts = ["Spectre d'absorption de raies", "Spectre d'emission continu", "Spectre de diffraction"]
                elif q_id == "q7": copie_opts = ["Spectroscope / Spectrometre", "Microscope", "Lentille convergente simple"]
                elif q_id == "q8": copie_opts = ["Nanometre (nm)", "Millimetre (mm)", "Hertz (Hz)"]
                elif q_id == "q9": copie_opts = ["Jaune", "Rouge", "Violet"]
                elif q_id == "q10": copie_opts = ["D'absorption de raies (Fraunhofer)", "D'emission pur", "Continu sans aucune raie"]
                
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo2, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt2[f"{q_id}_opt2"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo2, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE SYNTHÈSE HARMONISÉ ---
    with col_double_trous_opt2:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 2 (10 pts)")
        
        co2_1, co2_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co2_1: st.write("L'excitation thermique de sels metalliques par une flamme produit un spectre d'")
        with co2_2: t1 = st.selectbox("", ["Choisir...", "Emission", "Absorption", "Reflexion"], key="opt2_t1", disabled=verrouille, label_visibility="collapsed")
        
        co2_3, co2_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co2_3: st.write("La combustion du Sodium se caracterise par une couleur intense dans le")
        with co2_4: t2 = st.selectbox("", ["Choisir...", "Jaune", "Vert", "Bleu"], key="opt2_t2", disabled=verrouille, label_visibility="collapsed")

        co2_5, co2_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co2_5: st.write("A l'inverse, un solide porte a haute temperature emet une lumiere au spectre")
        with co2_6: t3 = st.selectbox("", ["Choisir...", "Continu", "Discontinu", "Monochrome"], key="opt2_t3", disabled=verrouille, label_visibility="collapsed")

        co2_7, co2_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co2_7: st.write("Le rayonnement solaire recu sur Terre comporte de fines raies sombres d'")
        with co2_8: t4 = st.selectbox("", ["Choisir...", "Absorption", "Emission", "Diffraction"], key="opt2_t4", disabled=verrouille, label_visibility="collapsed")

        co2_9, co2_10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co2_9: st.write("La position precise de ces signatures se mesure sur l'ecran en")
        with co2_10: t5 = st.selectbox("", ["Choisir...", "Nanometres", "Millimetres", "Degres"], key="opt2_t5", disabled=verrouille, label_visibility="collapsed")

        dict_trous_opt2 = {
            "t1_opt2": t1, "t2_opt2": t2, "t3_opt2": t3, "t4_opt2": t4, "t5_opt2": t5
        }

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
                ("q1", "L'angle de deviation minimale calcule pour le rayonnement rouge vaut :"),
                ("q2", "L'angle de deviation maximale obtenu pour le rayonnement violet vaut :"),
                ("q3", "Le phenomene de separation des couleurs par le prisme s'appelle la :"),
                ("q4", "La loi de Snell-Descartes relie les indices des milieux aux sinus des :"),
                ("q5", "Quelle couleur possede l'indice de refraction le plus eleve dans le verre :"),
                ("q6", "La recomposition de la lumiere blanche peut etre observee grace au disque de :"),
                ("q7", "La relation geometrique liee a l'angle au sommet A du prisme est :"),
                ("q8", "Lorsque la vitesse du disque de Newton est maximale, l'oeil percoit la couleur :"),
                ("q9", "Si l'indice de base du prisme augmente, la deviation globale de tous les rayons :"),
                ("q10", "Un rayonnement compose d'une seule radiation chromatique est qualifie de :")
            ]
            import random
            random.shuffle(questions_opt1_base)
            st.session_state.ordre_questions_opt1 = questions_opt1_base

        dict_quiz_opt1 = {}
        opts_num = ["Choisir...", d_r_f, d_v_f, d_vi_f, "Blanche", "Noir"]
        opts_num = list(dict.fromkeys(opts_num))

        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_opt1, 1):
            cle_qo1 = f"col_g_quiz_opt1_{q_id}_opt1"
            cle_opts_unique = f"opts_opt1_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q3": copie_opts = ["Dispersion", "Reflexion", "Absorption"]
                elif q_id == "q4": copie_opts = ["Angles", "Longueurs", "Indices"]
                elif q_id == "q5": copie_opts = ["Violet", "Rouge", "Vert"]
                elif q_id == "q6": copie_opts = ["Newton", "Descartes", "Snell"]
                elif q_id == "q7": copie_opts = ["A = r1 + r2", "A = i1 + i2", "A = r1 - r2"]
                elif q_id == "q8": copie_opts = ["Blanche", "Grise", "Noire"]
                elif q_id == "q9": copie_opts = ["Augmente", "Diminue", "Reste fixe"]
                elif q_id == "q10": copie_opts = ["Monochromatique", "Polychromatique", "Laser"]
                else: copie_opts = list(set(opts_num[1:]))
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qo1, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt1[f"{q_id}_opt1"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo1, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS ---
    with col_double_trous_opt1:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 1")
        co1_1, co1_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_1: st.write("Le prisme permet de separer les radiations de la lumiere blanche par")
        with co1_2: t1 = st.selectbox("", ["Choisir...", "Dispersion", "Reflexion", "Diffraction"], key="opt1_t1", disabled=verrouille, label_visibility="collapsed")
        
        co1_3, co1_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_3: st.write("Chaque couleur possede son propre indice de refraction. Le rouge est le moins")
        with co1_4: t2 = st.selectbox("", ["Choisir...", "Devie", "Ralenti", "Absorbe"], key="opt1_t2", disabled=verrouille, label_visibility="collapsed")

        co1_5, co1_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_5: st.write("La deviation minimale calculee pour le rayonnement rouge correspond a")
        with co1_6: t3 = st.selectbox("", opts_num, key="opt1_t3", disabled=verrouille, label_visibility="collapsed")

        co1_7, co1_8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_7: st.write("Tandis que la deviation maximale du rayonnement violet atteint la valeur de")
        with co1_8: t4 = st.selectbox("", opts_num, key="opt1_t4", disabled=verrouille, label_visibility="collapsed")

        co1_9, co1_10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_9: st.write("A l'inverse, la rotation rapide du disque colore montre la recomposition")
        with co1_10: t5 = st.selectbox("", ["Choisir...", "Blanche", "Monochrome", "Spectrale"], key="opt1_t5", disabled=verrouille, label_visibility="collapsed")

        dict_trous_opt1 = {
            "t1_opt1": t1, "t2_opt1": t2, "t3_opt1": t3, "t4_opt1": t4, "t5_opt1": t5
        }

    return dict_quiz_opt1, dict_trous_opt1





















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
    h_image_interm = h_obj * grandissement_obj

    xf1 = x_obj - f1
    xf_prime1 = x_obj + f1
    
    # REPARATION DES FOYERS DE L'OCULAIRE (F2 est en amont, F'2 en aval)
    xf2 = x_ocu - f2
    xf_prime2 = x_ocu + f2
    x_fin_rayons = x_ocu + 110.0

    pente_sortie_vrais_rayons = h_image_interm / f2 if f2 != 0 else 0

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

    # L2 : Oculaire loupe avec coordonnées de flèches complètes (RÉPARÉ)
    ax.plot([x_ocu, x_ocu], [15, h - 15], color="#3b82f6", lw=2.5, zorder=3)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [23, 15, 23], color="#3b82f6", lw=2)
    ax.plot([x_ocu - 6, x_ocu, x_ocu + 6], [h - 23, h - 15, h - 23], color="#3b82f6", lw=2)
    ax.text(x_ocu + 12, y0 + 14, "O2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="left")

    ax.annotate("", xy=(xa, y0 - h_obj), xytext=(xa, y0), arrowprops=dict(arrowstyle="->", color="#a855f7", lw=2.5), zorder=4)
    ax.text(xa, y0 + 14, "A", color="#a855f7", fontsize=7, fontweight="bold", ha="center")

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

    # REPARATION : L'image intermédiaire pointe desormais bien vers le bas (h_image_interm est negatif)
    ax.annotate("", xy=(xa1, y0 + h_image_interm), xytext=(xa1, y0), arrowprops=dict(arrowstyle="->", color="#10b981", lw=2.5), zorder=5)
    ax.text(xa1 - 10, y0 + (h_image_interm / 2.0), "A1B1", color="#10b981", fontsize=7, fontweight="bold", ha="right", va="center")

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

    ax.plot([x0, x0], [20, y_dioptre2 - 20], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2)
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
        ax.text(x0 + (dx_px/2) + 8, y_dioptre1 + (epaisseur_lame_px/2), "r1", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left", va="center")

        ax.plot([x_sortie, x_sortie], [y_dioptre1 + 15, h - 15], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2)
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
            ax.text(x_emerg + 8, y_emerg - 5, "s", color="#ef4444", fontsize=8, fontweight="bold", ha="left", va="center")

            dx_mm = (epaisseur_lame_px * 0.20) * math.sin(theta1_rad - theta2_rad) / math.cos(theta2_rad)
            msg, color = "DOUBLE DIOPTRE : Trajectoires de sorties calculees librement.", "#10b981"
            txt_math = f"Lame :\n• i1 = {theta1_deg:.1f}°\n• r1 = {theta2_deg:.1f}°\n• s = {theta3_deg:.1f}°\n• dx = {abs(dx_mm):.2f} mm"

    ax.text(25, 20, "ATELIER 2 - DOUBLE DIOPTRE ET TRAJECTOIRES", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    ax.text(x_inc - 8, y_inc + 12, "Rayon incident (i1)", color="#cbd5e1", fontsize=7, style="italic", ha="right")

    arc_i1 = patches.Arc((x0, y_dioptre1), 40, 40, angle=270, theta1=-theta1_deg, theta2=0, edgecolor=couleur_laser, lw=1.2)
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
    ax.plot([x0_s, x0_s], [y0_s - 150, y_fond_liquide - 10], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.5) 
    ax.text(x0_s + 8, y0_s - 120, "Normale", color="#64748b", fontsize=8, fontweight="bold", ha="left")
    
    # Rayon incident (Longueur 140 pixels)
    x_inc = x0_s - 130 * math.sin(theta1_rad)
    y_inc = y0_s - 130 * math.cos(theta1_rad)
    ax.annotate("", xy=(x0_s, y0_s), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
    ax.text(x_inc - 10, y_inc, "Rayon incident", color=couleur_laser, fontsize=8, fontweight="bold", style="italic", ha="right", va="center")

    # Arc geometrique pour l'incidence i
    arc_i = patches.Arc((x0_s, y0_s), 60, 60, angle=270, theta1=-theta1_deg, theta2=0, edgecolor=couleur_laser, lw=1.5)
    ax.add_patch(arc_i)
    ax.text(x0_s - 18, y0_s - 38, "i", color=couleur_laser, fontsize=9, fontweight="bold", ha="center")

    # Application de la loi physique de Snell-Descartes et gestion de la R.T.I.
    sin_r = (n1 * math.sin(theta1_rad)) / n2
    if sin_r > 1.0:
        # Reflexion totale interne
        x_tot = x0_s + 130 * math.sin(theta1_rad)
        y_tot = y0_s - 130 * math.cos(theta1_rad)
        ax.annotate("", xy=(x_tot, y_tot), xytext=(x0_s, y0_s), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        ax.text(x_tot + 10, y_tot, "Reflechi", color="#ef4444", fontsize=8, fontweight="bold", style="italic", ha="left", va="center")
        txt_box_simple = f"Simple :\n- i = {theta1_deg:.1f}°\n- r = Reflexion totale\n- Rapport n1/n2 = {n1/n2:.2f}"
    else:
        theta2_rad = math.asin(sin_r)
        theta2_deg = math.degrees(theta2_rad)
        
        x_frac = x0_s + 130 * math.sin(theta2_rad)
        y_frac = y0_s + 130 * math.cos(theta2_rad)
        ax.annotate("", xy=(x_frac, y_frac), xytext=(x0_s, y0_s), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        ax.text(x_frac + 10, y_frac, "Rayon refracte", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left", va="center")

        # Arc geometrique pour la refraction r sous le dioptre
        arc_r = patches.Arc((x0_s, y0_s), 60, 60, angle=90, theta1=-theta2_deg, theta2=0, edgecolor="#cbd5e1", lw=1.5)
        ax.add_patch(arc_r)
        ax.text(x0_s + 18, y0_s + 38, "r", color="#cbd5e1", fontsize=9, fontweight="bold", ha="center")
        txt_box_simple = f"Simple :\n- i = {theta1_deg:.1f}°\n- r = {theta2_deg:.1f}°\n- Rapport n1/n2 = {n1/n2:.2f}"

    # Sauvegarde locale pour l'affichage de la boite de donnees
    st.session_state.opt4_txt_box_simple = txt_box_simple
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

def mettre_a_jour_illusion_matplotlib():
    """Moteur d'illusion HUD : simulation automobile reelle avec projecteur vertical.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions fixes constantes du laboratoire d'origine
    w = 400
    h = 240
    x0, y0 = 200.0, 115.0  # Point d'impact fixe au centre du pare-brise

    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12,8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # Lecture du curseur d'angle depuis le session_state de Streamlit
    angle_deg = st.session_state.get("slider_angle_ill", 45.0)
    angle_rad = math.radians(angle_deg)

    # =========================================================================
    # 1. LE PROJECTEUR AUTOMOBILE (Placé verticalement sous le pare-brise)
    # =========================================================================
    x_ecran, y_ecran = x0, 205.0
    # Boîtier du projecteur HUD encastre
    proj_box = patches.Rectangle((x_ecran - 25, y_ecran), 50, 12, facecolor="#334155", edgecolor="#1e293b", zorder=3)
    proj_lens = patches.Rectangle((x_ecran - 18, y_ecran - 4), 36, 4, facecolor="#0284c7", edgecolor="none", zorder=3)
    ax.add_patch(proj_box)
    ax.add_patch(proj_lens)
    ax.text(x_ecran, y_ecran - 2, "50", color="white", fontsize=6, fontweight="bold", ha="center", va="bottom", zorder=4)
    ax.text(x_ecran, y_ecran + 22, "Projecteur HUD", color="#475569", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 2. LA ROUTE RÉELLE D'HORIZON (Centrée au milieu à droite)
    # =========================================================================
    x_route, y_route = 330.0, 90.0  
    route_rect = patches.Rectangle((x_route - 40, y_route), 80, 50, facecolor="#64748b", edgecolor="none", zorder=1)
    ax.add_patch(route_rect)
    ax.plot([x_route, x_route], [y_route, y_route + 50], color="white", lw=1.5, linestyle=(0, (4, 4)), zorder=2)
    ax.text(x_route, y_route + 56, "Axe de la route", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 3. LA PLANCHE DE BORD HORIZONTALE ET LE PARE-BRISE MOBILE
    # =========================================================================
    # Table de bord gauche qui cache la vue directe
    bord_rect = patches.Rectangle((20, y_ecran - 4), x_ecran - 45, 16, facecolor="#1e293b", edgecolor="none", zorder=2)
    ax.add_patch(bord_rect)
    
    # Pare-brise mobile turquoise incline
    dx_m = 70 * math.cos(angle_rad)
    dy_m = 70 * math.sin(angle_rad)
    ax.plot([x0 - dx_m, x0 + dx_m], [y0 - dy_m, y0 + dy_m], color="#0d9488", lw=3, zorder=3)
    ax.text(x0 + dx_m + 5, y0 + dy_m + 5, "miroir", color="#0d9488", fontsize=7, fontweight="bold", ha="left", va="center")

    # =========================================================================
    # 4. MOTEUR PHYSIQUE VECTORIEL (PROJECTEUR VERTICAL)
    # =========================================================================
    # Le rayon émis monte verticalement
    uix, uiy = 0.0, -1.0
    ax.annotate("", xy=(x0, y0), xytext=(x_ecran, y_ecran - 4), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_ecran + 10, (y_ecran + y0)/2, "Rayon incident", color="#ef4444", fontsize=7, style="italic", ha="left", va="center")

    # La Normale pivotante a 90° face au rayon vertical
    unx = -math.sin(angle_rad)
    uny = math.cos(angle_rad)
    ax.plot([x0 - 50 * unx, x0 + 50 * unx], [y0 - 50 * uny, y0 + 50 * uny], color="#94a3b8", lw=1.2, linestyle=(0, (3, 3)))
    ax.text(x0 + 55 * unx, y0 + 55 * uny, "Normale", color="#64748b", fontsize=7, fontweight="bold", ha="center", va="center")

    # Lois de réflexion de Descartes (Vecteur réfléchi)
    dot_product = uix * unx + uiy * uny
    urx = uix - 2.0 * dot_product * unx
    ury = uiy - 2.0 * dot_product * uny

    # Tracé du Rayon Réfléchi vers le conducteur a gauche
    x_conducteur = x0 + urx * 130.0
    y_conducteur = y0 + ury * 130.0
    ax.annotate("", xy=(x_conducteur, y_conducteur), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_conducteur - 5, y_conducteur, "Conducteur ", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right", va="center")
    ax.text(x0 - 40, y0 - 30, "Rayon reflechi", color="#b91c1c", fontsize=7, style="italic", ha="left", va="bottom")

    # Prolongement virtuel en ligne droite vers la route
    x_illusion = x0 - urx * 130.0
    y_illusion = y0 - ury * 130.0
    ax.plot([x0, x_illusion], [y0, y_illusion], color="#94a3b8", lw=1, linestyle=(0, (2, 2)))

    # =========================================================================
    # 5. PROJECTION DE L'HOLOGRAMME HUD (PILE SUR LA ROUTE À 45°)
    # =========================================================================
    hud_box = patches.Rectangle((x_illusion - 18, y_illusion - 12), 36, 16, fill=False, edgecolor="#22c55e", lw=1.5, linestyle=(0, (2, 2)), zorder=4)
    ax.add_patch(hud_box)
    ax.text(x_illusion, y_illusion - 4, "50", color="#22c55e", fontsize=10, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(x_illusion, y_illusion - 18, "HUD", color="#22c55e", fontsize=7, style="italic", ha="center", va="bottom")

    # Condition de validation mecanique de l'illusion d'optique
    if 44.0 <= angle_deg <= 46.0:
        msg_ill = "ALIGNEMENT HUD OK : La vitesse est projetee pile sur la route !"
        couleur_ill = "#16a34a"
    else:
        msg_ill = "DEREGLE : L'hologramme sort de la zone de vision."
        couleur_ill = "#ef4444"

    # Affichage des en-têtes de statut textuels de Matplotlib
    ax.text(20, h - 220, "AFFICHAGE TETE HAUTE (HUD)", color="#38bdf8", fontsize=9, fontweight="bold", ha="left", va="top")
    ax.text(20, h - 205, msg_ill, color=couleur_ill, fontsize=7, fontweight="bold", ha="left", va="top")

    # Sauvegarde des donnees numeriques de simulation dans le bloc de l'Atelier 3
    st.session_state.opt3_txt_box_ill = (
        f"Mesures du HUD :\n"
        f"• Miroir i = {angle_deg:.1f}°\n"
        f"• Reflexion i' = {angle_deg:.1f}°\n"
        f"• Loi optique : i = i'\n"
        f"• Point X={x_illusion:.1f} / Y={y_illusion:.1f}"
    )

    return fig


def mettre_a_jour_reflexion_pure_matplotlib():
    """Moteur physique de reflexion pure : entierement verrouille sur le curseur d'incidence.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions de securite fixes constantes
    w, h = 400, 240
    x0, y0 = 200.0, 180.0  

    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # Lecture du vrai curseur d'incidence synchronise
    theta_i_deg = st.session_state.get("slider_angle_ref_i", 45.0)
    theta_i_rad = math.radians(theta_i_deg)

    # Support hachure du miroir plan horizontal
    miroir_fond = patches.Rectangle((0, y0), w, h - y0, facecolor="#1e293b", edgecolor="none", alpha=0.5)
    ax.add_patch(miroir_fond)
    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=3, zorder=3) 
    
    # Hachures mecaniques
    for x_hach in range(20, int(w - 15), 12):
        ax.plot([x_hach, x_hach - 6], [y0, y0 + 8], color="#64748b", lw=1)

    # Tracé de la ligne de repère : La Normale verticale
    ax.plot([x0, x0], [15, y0], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.5)
    ax.text(x0 + 8, 25, "Normale", color="#64748b", fontsize=8, fontweight="bold", ha="left", va="top")

    # Tracé du Rayon Incident (i)
    x_inc = x0 - 130 * math.sin(theta_i_rad)
    y_inc = y0 - 130 * math.cos(theta_i_rad)
    couleur_laser = "#ef4444" 
    ax.annotate("", xy=(x0, y0), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
    ax.text(x_inc - 8, y_inc, "Rayon incident", color=couleur_laser, fontsize=8, fontweight="bold", style="italic", ha="right", va="center")

    # Tracé du Rayon Réfléchi (i')
    x_ref = x0 + 130 * math.sin(theta_i_rad)
    y_ref = y0 - 130 * math.cos(theta_i_rad)
    ax.annotate("", xy=(x_ref, y_ref), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
    ax.text(x_ref + 8, y_ref, "Rayon reflechi", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left", va="center")

    # Arcs geometriques des angles i et i' via des patches Arc de Matplotlib
    arc_i = patches.Arc((x0, y0), 70, 70, angle=270, theta1=0, theta2=theta_i_deg, edgecolor=couleur_laser, lw=1.5)
    arc_iprime = patches.Arc((x0, y0), 70, 70, angle=270, theta1=-theta_i_deg, theta2=0, edgecolor="#cbd5e1", lw=1.5)
    ax.add_patch(arc_i)
    ax.add_patch(arc_iprime)
    
    ax.text(x0 - 18, y0 - 42, "i", color=couleur_laser, fontsize=9, fontweight="bold", ha="center")
    ax.text(x0 + 18, y0 - 42, "i'", color="#cbd5e1", fontsize=9, fontweight="bold", ha="center")

    # Titres généraux de l'Atelier 3
    ax.text(20, 20, "LOI DE LA REFLEXION (i = i')", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    
    # Generation de la boite de resultats synchrone
    st.session_state.opt3_txt_box_ref = (
        f"Mesures Miroir Plan :\n"
        f"• Angle d'incidence i = {theta_i_deg:.1f}°\n"
        f"• Angle de reflexion i' = {theta_i_deg:.1f}°\n"
        f"• Statut : i = i' verifie"
    )

    return fig

def ajouter_mesure_reflexion_pure_streamlit():
    """Capte la valeur de la reglette i et l'ajoute de maniere permanente dans les listes de session."""
    theta_i = st.session_state.get("slider_angle_ref_i", 45.0)
    
    # Memorisation etanche dans vos tableaux de stockage de reflexion
    if "mesures_reflexion_i" in st.session_state:
        st.session_state.mesures_reflexion_i.append(theta_i)
        st.session_state.mesures_reflexion_iprime.append(theta_i)



def mettre_a_jour_illusion_matplotlib():
    """Moteur d'illusion HUD : simulation automobile reelle avec projecteur vertical.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # VERROUILLÉ : Dimensions fixes constantes du laboratoire
    w = 400
    h = 240
    x0, y0 = 200.0, 115.0  # Point d'impact fixe au centre du pare-brise

    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # RECONNEXION DIRECTE SUR LE CURSEUR DU LABORATOIRE VISUEL DE GAUCHE
    angle_deg = st.session_state.get("slider_angle_ill_quiz", 45.0)
    angle_rad = math.radians(angle_deg)

    
    # =========================================================================
    # 1. LE PROJECTEUR AUTOMOBILE (Placé verticalement sous le pare-brise)
    # =========================================================================
    x_ecran, y_ecran = x0, 205.0
    # Boîtier du projecteur HUD encastre
    proj_box = patches.Rectangle((x_ecran - 25, y_ecran), 50, 12, facecolor="#334155", edgecolor="#1e293b", zorder=3)
    proj_lens = patches.Rectangle((x_ecran - 18, y_ecran - 4), 36, 4, facecolor="#0284c7", edgecolor="none", zorder=3)
    ax.add_patch(proj_box)
    ax.add_patch(proj_lens)
    ax.text(x_ecran, y_ecran - 2, "50", color="white", fontsize=6, fontweight="bold", ha="center", va="bottom", zorder=4)
    ax.text(x_ecran, y_ecran + 22, "Projecteur HUD", color="#475569", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 2. LA ROUTE RÉELLE D'HORIZON (Centrée au milieu à droite)
    # =========================================================================
    x_route, y_route = 330.0, 90.0  
    route_rect = patches.Rectangle((x_route - 40, y_route), 80, 50, facecolor="#64748b", edgecolor="none", zorder=1)
    ax.add_patch(route_rect)
    ax.plot([x_route, x_route], [y_route, y_route + 50], color="white", lw=1.5, linestyle=(0, (4, 4)), zorder=2)
    ax.text(x_route, y_route + 56, "Axe de la route", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 3. LA PLANCHE DE BORD HORIZONTALE ET LE PARE-BRISE MOBILE
    # =========================================================================
    bord_rect = patches.Rectangle((20, y_ecran - 4), x_ecran - 45, 16, facecolor="#1e293b", edgecolor="none", zorder=2)
    ax.add_patch(bord_rect)
    
    # Pare-brise mobile turquoise incline
    dx_m = 70 * math.cos(angle_rad)
    dy_m = 70 * math.sin(angle_rad)
    ax.plot([x0 - dx_m, x0 + dx_m], [y0 - dy_m, y0 + dy_m], color="#0d9488", lw=3, zorder=3)
    ax.text(x0 + dx_m + 5, y0 + dy_m + 5, "Pare-brise", color="#0d9488", fontsize=7, fontweight="bold", ha="left", va="center")

    # =========================================================================
    # 4. MOTEUR PHYSIQUE VECTORIEL (PROJECTEUR VERTICAL)
    # =========================================================================
    uix, uiy = 0.0, -1.0
    ax.annotate("", xy=(x0, y0), xytext=(x_ecran, y_ecran - 4), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_ecran + 10, (y_ecran + y0)/2, "Rayon incident", color="#ef4444", fontsize=7, style="italic", ha="left", va="center")

    unx = -math.sin(angle_rad)
    uny = math.cos(angle_rad)
    ax.plot([x0 - 50 * unx, x0 + 50 * unx], [y0 - 50 * uny, y0 + 50 * uny], color="#94a3b8", lw=1.2, linestyle=(0, (3, 3)))
    ax.text(x0 + 55 * unx, y0 + 55 * uny, "Normale", color="#64748b", fontsize=7, fontweight="bold", ha="center", va="center")

    dot_product = uix * unx + uiy * uny
    urx = uix - 2.0 * dot_product * unx
    ury = uiy - 2.0 * dot_product * uny

    x_conducteur = x0 + urx * 130.0
    y_conducteur = y0 + ury * 130.0
    ax.annotate("", xy=(x_conducteur, y_conducteur), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_conducteur - 5, y_conducteur, "Conducteur ", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right", va="center")
    ax.text(x0 - 40, y0 - 30, "Rayon reflechi", color="#b91c1c", fontsize=7, style="italic", ha="left", va="bottom")

    x_illusion = x0 - urx * 130.0
    y_illusion = y0 - ury * 130.0
    ax.plot([x0, x_illusion], [y0, y_illusion], color="#94a3b8", lw=1, linestyle=(0, (2, 2)))

    # =========================================================================
    # 5. PROJECTION DE L'HOLOGRAMME HUD (PILE SUR LA ROUTE À 45°)
    # =========================================================================
    hud_box = patches.Rectangle((x_illusion - 18, y_illusion - 12), 36, 16, fill=False, edgecolor="#22c55e", lw=1.5, linestyle=(0, (2, 2)), zorder=4)
    ax.add_patch(hud_box)
    ax.text(x_illusion, y_illusion - 4, "50", color="#22c55e", fontsize=10, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(x_illusion, y_illusion - 18, "HUD", color="#22c55e", fontsize=7, style="italic", ha="center", va="bottom")

    if 44.0 <= angle_deg <= 46.0:
        msg_ill = "ALIGNEMENT HUD OK : La vitesse est projetee pile sur la route !"
        couleur_ill = "#16a34a"
    else:
        msg_ill = "DEREGLE : L'hologramme sort de la zone de vision."
        couleur_ill = "#ef4444"

    ax.text(20, h - 220, "AFFICHAGE TETE HAUTE (HUD)", color="#38bdf8", fontsize=9, fontweight="bold", ha="left", va="top")
    ax.text(20, h - 205, msg_ill, color=couleur_ill, fontsize=7, fontweight="bold", ha="left", va="top")

    st.session_state.opt3_txt_box_ill = (
        f"Mesures du HUD :\n"
        f"• Miroir i = {angle_deg:.1f}°\n"
        f"• Reflexion i' = {angle_deg:.1f}°\n"
        f"• Loi optique : i = i'\n"
        f"• Point X={x_illusion:.1f} / Y={y_illusion:.1f}"
    )

    return fig

def mettre_a_jour_periscope_matplotlib():
    """Moteur physique de reflexion : calcule et dessine le periscope du sous-marin.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions fixes constantes du laboratoire
    w = 600
    h = 280
    x0 = 300.0  # Axe central vertical exact du tube du periscope (600 / 2)

    # Creation de la figure Matplotlib sombre ajustee en taille
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # Lecture du curseur d'angle depuis le session_state de Streamlit
    angle_miroir_deg = st.session_state.get("slider_angle_periscope", 45.0)
    angle_miroir_rad = math.radians(angle_miroir_deg)

    # Hauteurs fixes des deux miroirs pour s'aligner sur la double reflexion
    y_miroir1 = 90.0
    y_miroir2 = 180.0
    epaisseur_tube_px = y_miroir2 - y_miroir1

    # =========================================================================
    # 1. DESSIN DU DECOR : LA MER ET LE TUBE DU PÉRISCOPE
    # =========================================================================
    # La mer bleue en fond bas (S'aligne sur la strate basse du dioptre)
    mer_rect = patches.Rectangle((15, y_miroir2), w - 30, h - 10 - y_miroir2, facecolor="#0284c7", edgecolor="none", zorder=1)
    ax.add_patch(mer_rect)
    
    # Tube vertical metallique du periscope (Centre sur x0)
    tube_vert = patches.Rectangle((x0 - 25, 10), 50, y_miroir2 + 13, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5, zorder=2)
    # Coude amont d'entree (a gauche)
    coude_amont = patches.Rectangle((x0 - 120, y_miroir1 - 25), 95, 50, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5, zorder=2)
    # Coude aval de sortie vers l'oeil (a droite)
    coude_aval = patches.Rectangle((x0 + 25, y_miroir2 - 25), 95, 50, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5, zorder=2)
    
    ax.add_patch(tube_vert)
    ax.add_patch(coude_amont)
    ax.add_patch(coude_aval)

    # Masquage des jointures internes pour un rendu de canalisation propre et fluide
    ax.add_patch(patches.Rectangle((x0 - 23, 12), 46, y_miroir2 - 12, facecolor="#cbd5e1", edgecolor="none", zorder=2))
    ax.add_patch(patches.Rectangle((x0 - 118, y_miroir1 - 23), 95, 46, facecolor="#cbd5e1", edgecolor="none", zorder=2))
    ax.add_patch(patches.Rectangle((x0 + 23, y_miroir2 - 23), 95, 46, facecolor="#cbd5e1", edgecolor="none", zorder=2))

    # =========================================================================
    # 2. POSITIONNEMENT DES DEUX MIROIRS PLANS
    # =========================================================================
    # Miroir 1 superieur (Incline a l'impact vertical de l'entree)
    ax.plot([x0 - 25, x0 + 25], [y_miroir1 - 25, y_miroir1 + 25], color="#475569", lw=4, zorder=3)
    ax.text(x0 + 32, y_miroir1 - 15, "Miroir 1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="left", va="center", zorder=4)
    
    # Miroir 2 inferieur (Incline a l'impact vertical de la sortie)
    ax.plot([x0 - 25, x0 + 25], [y_miroir2 - 25, y_miroir2 + 25], color="#475569", lw=4, zorder=3)
    ax.text(x0 - 32, y_miroir2 + 15, "Miroir 2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right", va="center", zorder=4)

    # =========================================================================
    # 3. TRACE GEOMETRIQUE DES RAYONS LASER (i = r)
    # =========================================================================
    angle_deviation_deg = angle_miroir_deg * 2.0
    angle_deviation_rad = math.radians(angle_deviation_deg)

    # Rayon 1 : Faisceau incident horizontal exterieur arrivant de gauche
    ax.annotate("", xy=(x0, y_miroir1), xytext=(15, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
    ax.text(25, y_miroir1 - 10, "Rayon incident", color="#ef4444", fontsize=8, fontweight="bold", style="italic", ha="left", va="bottom")

    # Calcul de la trajectoire descendante dans le tube vertical
    dx_faisceau = epaisseur_tube_px * math.tan(math.radians(90.0 - angle_deviation_deg)) if angle_deviation_deg != 90.0 else 0
    x_impact2 = x0 + dx_faisceau
    y_impact2 = y_miroir2

    # Rayon 2 : Faisceau reflechi intermediaire circulant dans le tube vertical
    ax.annotate("", xy=(x_impact2, y_impact2), xytext=(x0, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)

    # Rayon 3 : Faisceau emergent final vers l'oeil de l'etudiant
    angle_deviation_deg = angle_miroir_deg * 2.0
    
    # Rayon 1 : Faisceau incident horizontal exterieur arrivant de gauche
    ax.annotate("", xy=(x0, y_miroir1), xytext=(15, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
    ax.text(25, y_miroir1 - 10, "Rayon incident", color="#ef4444", fontsize=8, fontweight="bold", style="italic", ha="left", va="bottom")

    # Calcul de la trajectoire descendante dans le tube vertical
    dx_faisceau = epaisseur_tube_px * math.tan(math.radians(90.0 - angle_deviation_deg)) if angle_deviation_deg != 90.0 else 0
    x_impact2 = x0 + dx_faisceau
    y_impact2 = y_miroir2

    # Rayon 2 : Faisceau genie intermediaire circulant dans le tube vertical
    ax.annotate("", xy=(x_impact2, y_impact2), xytext=(x0, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)

    # Rayon 3 : Faisceau emergent final recalcule selon l'inclinaison reelle
    if 44.0 <= angle_miroir_deg <= 46.0:
        # Alignement geometrique parfait (90 degres de cassure vers l'oeil)
        ax.annotate("", xy=(w - 15, y_impact2), xytext=(x_impact2, y_impact2), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
        ax.text(w - 25, y_impact2 - 10, "Oeil du Marin (Vision OK)", color="#15803d", fontsize=8, fontweight="bold", ha="right", va="bottom")
        msg_status = "PERISCOPE ALIGNE : Les faisceaux de sortie sont paralleles."
        couleur_status = "#0d9488"
    else:
        # DEVIATION RECOUPÉE EN DIRECT : L'angle de sortie depend directement de la loi des miroirs
        # L'angle de sortie par rapport a l'horizontale vaut (90 - 2 * delta_angle)
        angle_sortie_rad = math.radians(90.0 - (angle_miroir_deg - 45.0) * 2.0)
        
        x_perdu = x_impact2 + 120.0 * math.sin(angle_sortie_rad)
        y_perdu = y_impact2 + 120.0 * math.cos(angle_sortie_rad)
        
        # Securite pour confiner le tracé dans la structure basse si le faisceau plonge
        if y_perdu > h - 15:
            y_perdu = h - 15
            
        ax.annotate("", xy=(x_perdu, y_perdu), xytext=(x_impact2, y_impact2), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
        ax.text(w - 25, y_miroir2 - 10, "Faisceau obstrue", color="#ef4444", fontsize=8, fontweight="bold", ha="right", va="bottom")
        msg_status = "ERREUR D'ALIGNEMENT : Le rayon percute la structure."
        couleur_status = "#ef4444"

    # CORRECTION : Titre singulier propre sans lettre parasite
    ax.text(25, 20, "LE PÉRISCOPE", color="#38bdf8", fontsize=9, fontweight="bold", ha="left", va="top")
    ax.text(25, 35, msg_status, color=couleur_status, fontsize=7, fontweight="bold", ha="left", va="top")

    # Legendes des milieux ancrees fixement a l'extreme droite (X=575)
    ax.text(w - 25, 20, "Milieu 1 : Air (n=1.00)", color="#94a3b8", fontsize=7, fontweight="bold", ha="right")
    ax.text(w - 25, y_miroir1 + 15, "Structure : Metal opaque", color="#475569", fontsize=7, fontweight="bold", ha="right")
    ax.text(w - 25, h - 20, "Milieu 3 : Eau de mer (n=1.33)", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right")

    # Sauvegarde du bloc de texte technique pour la boite d'information
    st.session_state.opt3_txt_box_periscope = (
        f"Periscope :\n"
        f"• Miroir 1 = {angle_miroir_deg:.1f}°\n"
        f"• Miroir 2 = {angle_miroir_deg:.1f}°\n"
        f"• Reflexion i=r = {angle_miroir_deg:.1f}°\n"
        f"• Deviation = {angle_deviation_deg:.1f}°"
    )

    return fig

def mettre_a_jour_retroviseurs_matplotlib():
    """Moteur physique : Calcule les lois de reflexion de Descartes avec conversion en radians.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions stables calquees sur le Canvas Tkinter d'origine
    w = 740
    h = 260
    
    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien du repere inversé indispensable de Tkinter
    ax.axis("off")

    # Positionnement de la voiture (Recentré bas pour laisser de la place au champ arriere)
    cx, cy = w / 2.0, h / 2.0 + 35.0
    w_voiture, h_voiture = 110.0, 150.0
    
    # Tracé des lignes de delimitation de la route
    ax.plot([130, 130], [0, h], color="#475569", lw=1.5, linestyle=(0, (6, 6)))
    ax.plot([w - 130, w - 130], [0, h], color="#475569", lw=1.5, linestyle=(0, (6, 6)))

    # Carrosserie grise de la voiture
    voiture_rect = patches.Rectangle(
        (cx - w_voiture/2, cy - h_voiture/2), w_voiture, h_voiture,
        facecolor="#334155", edgecolor="#cbd5e1", lw=2, zorder=3
    )
    ax.add_patch(voiture_rect)
    
    # Vitrages (Pare-brise en bas / Lunette arriere en haut)
    ax.plot([cx - w_voiture/2 + 6, cx + w_voiture/2 - 6], [cy + h_voiture/4, cy + h_voiture/4], color="#94a3b8", lw=3, zorder=4)
    ax.plot([cx - w_voiture/2 + 6, cx + w_voiture/2 - 6], [cy - h_voiture/3, cy - h_voiture/3], color="#94a3b8", lw=3, zorder=4)

    # =========================================================================
    # RECOVERY DES COMPOSANTS DE SESSIONS DE L'ATELIER 3
    # =========================================================================
    obs = st.session_state.get("combo_obs_retro_final", "Conducteur")
    decalage_cond = st.session_state.get("slide_siege_cond_eval", 0.0)
    decalage_pass = st.session_state.get("slide_siege_pass_eval", 0.0)

    # Récupération dynamique des curseurs d'angles de rétroviseurs révisés
    dev_g = st.session_state.get("slide_retro_g_eval", 0.0)
    dev_i = st.session_state.get("slide_retro_i_eval", 0.0)
    dev_d = st.session_state.get("slide_retro_d_eval", 0.0)

    y_cond_dynamique = (cy + 25.0) - decalage_cond
    y_pass_dynamique = (cy + 25.0) - decalage_pass

    if obs == "Conducteur":
        x_oeil, y_oeil = cx - 22.0, y_cond_dynamique
        ax.plot(x_oeil, y_oeil, marker="o", color="#2563eb", markeredgecolor="white", markersize=7, zorder=5)
        ax.text(x_oeil, y_oeil + 14, "Conducteur", color="#38bdf8", fontsize=7, fontweight="bold", ha="center", zorder=5)
        ax.plot(cx + 22, y_pass_dynamique, marker="o", color="#64748b", markersize=4, zorder=5)
    else:
        x_oeil, y_oeil = cx + 22.0, y_pass_dynamique
        ax.plot(x_oeil, y_oeil, marker="o", color="#ec4899", markeredgecolor="white", markersize=7, zorder=5)
        ax.text(x_oeil, y_oeil + 14, "Passager", color="#f472b6", fontsize=7, fontweight="bold", ha="center", zorder=5)
        ax.plot(cx - 22, y_cond_dynamique, marker="o", color="#64748b", markersize=4, zorder=5)

    # Configuration geometrique des 3 miroirs
    positions_miroirs = {
        "gauche": {"x": cx - w_voiture/2 - 10, "y": cy - h_voiture/4, "long": 16.0, "ang_base": 90.0, "dev": dev_g},
        "interne": {"x": cx, "y": cy - h_voiture/3 - 10, "long": 22.0, "ang_base": 0.0, "dev": dev_i},
        "droit": {"x": cx + w_voiture/2 + 10, "y": cy - h_voiture/4, "long": 16.0, "ang_base": -90.0, "dev": dev_d}
    }

    for nom, m in positions_miroirs.items():
        angle_miroir_rad = math.radians(m["ang_base"] + m["dev"])
        
        xa = m["x"] - (m["long"] / 2.0) * math.cos(angle_miroir_rad)
        ya = m["y"] - (m["long"] / 2.0) * math.sin(angle_miroir_rad)
        xb = m["x"] + (m["long"] / 2.0) * math.cos(angle_miroir_rad)
        yb = m["y"] + (m["long"] / 2.0) * math.sin(angle_miroir_rad)
        
        # Bras de fixation physiques de la carrosserie
        if nom == "gauche":
            ax.plot([cx - w_voiture/2, xa], [m["y"], ya], color="#cbd5e1", lw=2, zorder=3)
        elif nom == "droit":
            ax.plot([cx + w_voiture/2, xb], [m["y"], yb], color="#cbd5e1", lw=2, zorder=3)

        # Dessin de la face réfléchissante cyan
        ax.plot([xa, xb], [ya, yb], color="#06b6d4", lw=3.5, zorder=4)

        # Tracé des rayons incidents de visée (Jaune)
        ax.plot([x_oeil, xa], [y_oeil, ya], color="#f59e0b", lw=1.0, alpha=0.8, zorder=2)
        ax.plot([x_oeil, xb], [y_oeil, yb], color="#f59e0b", lw=1.0, alpha=0.8, zorder=2)

        # CALCUL TRIGONOMÉTRIQUE DES DEUX RAYONS RÉFLÉCHIS (i = r)
        ang_inc_a = math.atan2(ya - y_oeil, xa - x_oeil)
        ang_norm_a = angle_miroir_rad + math.pi / 2.0
        ang_ref_a = 2.0 * ang_norm_a - ang_inc_a - math.pi
        x_fond_a = xa + 600.0 * math.cos(ang_ref_a)
        y_fond_a = ya + 600.0 * math.sin(ang_ref_a)

        ang_inc_b = math.atan2(yb - y_oeil, xb - x_oeil)
        ang_norm_b = angle_miroir_rad + math.pi / 2.0
        ang_ref_b = 2.0 * ang_norm_b - ang_inc_b - math.pi
        x_fond_b = xb + 600.0 * math.cos(ang_ref_b)
        y_fond_b = yb + 600.0 * math.sin(ang_ref_b)

        # Test d'obstacle de la vitre arriere pour le rétroviseur interne
        passe_par_vitre = True
        if nom == "interne":
            y_vitre_arriere = cy - h_voiture / 2.0
            largeur_vitre_arriere = w_voiture - 30.0
            x_vitre_gauche = cx - largeur_vitre_arriere / 2.0
            x_vitre_droite = cx + largeur_vitre_arriere / 2.0
            
            x_int_a = xa + ((y_vitre_arriere - ya) / math.sin(ang_ref_a)) * math.cos(ang_ref_a) if math.sin(ang_ref_a) != 0 else 9999
            x_int_b = xb + ((y_vitre_arriere - yb) / math.sin(ang_ref_b)) * math.cos(ang_ref_b) if math.sin(ang_ref_b) != 0 else -9999
            
            if not (x_vitre_gauche <= x_int_a <= x_vitre_droite) or not (x_vitre_gauche <= x_int_b <= x_vitre_droite):
                passe_par_vitre = False

        # Rendu du champ visuel refléchi ou de l'angle mort obstrué
        if nom == "interne" and not passe_par_vitre:
            ax.plot([xa, x_fond_a], [ya, y_fond_a], color="#475569", lw=1.0, linestyle=":", alpha=0.6)
            ax.plot([xb, x_fond_b], [yb, y_fond_b], color="#475569", lw=1.0, linestyle=":", alpha=0.6)
        else:
            # Remplacement de create_polygon par un polygone Matplotlib bleu translucide
            poly_points = np.array([[xa, ya], [xb, yb], [x_fond_b, y_fond_b], [x_fond_a, y_fond_a]])
            champ_poly = patches.Polygon(poly_points, facecolor="#1d4ed8", alpha=0.25, edgecolor="none", zorder=1)
            ax.add_patch(champ_poly)
            
            # Tracé net des deux bordures du cône de visibilité en rouge vif
            ax.plot([xa, x_fond_a], [ya, y_fond_a], color="#ef4444", lw=1.5, zorder=2)
            ax.plot([xb, x_fond_b], [yb, y_fond_b], color="#ef4444", lw=1.5, zorder=2)

    # Affichage de la legende technique informative au bas du repere
    ax.text(15, h - 15, "Jaune : Visee | Voile Bleu : Champ de vision | Zones sombres : Angles morts", color="#94a3b8", fontsize=8, style="italic", va="center", ha="left")

    return fig

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
    """Génère la figure Matplotlib du disque de Newton avec blanchiment physique

    calculé de manière linéaire selon la vitesse (0 à 25 tr/s).
    """
    # 1. Récupération des paramètres depuis le session_state
    vitesse = st.session_state.var_vitesse_disque
    anim_en_cours = st.session_state.anim_en_cours
    angle_rotation = getattr(st.session_state, "angle_rotation_disque", 0.0)

    # Configuration de la figure Matplotlib
    fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(-110, 110)
    ax.set_ylim(-110, 110)
    ax.axis("off")

    rayon_disque = 100.0
    ouverture_secteur = 360.0 / 7.0

    # Calcul mathématique du blanchiment (Maximum à 25 tours/seconde)
    if anim_en_cours:
        facteur_blanchiment = vitesse / 25.0
        if facteur_blanchiment > 1.0:
            facteur_blanchiment = 1.0
    else:
        facteur_blanchiment = 0.0

    # Base des 7 couleurs de Newton
    couleurs = recuperer_couleurs_newton()

    # Dictionnaire de conversion RVB d'origine
    rgb_base = {
        "#ef4444": (239, 68, 68),  # Rouge
        "#f97316": (249, 115, 22),  # Orange
        "#eab308": (234, 179, 8),  # Jaune
        "#22c55e": (34, 197, 94),  # Vert
        "#2563eb": (37, 99, 235),  # Bleu
        "#4f46e5": (79, 70, 229),  # Indigo
        "#7c3aed": (124, 58, 237),  # Violet
    }

    # Tracé des 7 secteurs avec transition continue vers le blanc pur
    for i, couleur in enumerate(couleurs):
        angle_depart = (angle_rotation + (i * ouverture_secteur)) % 360.0
        hex_code = couleur["code"]

        if hex_code in rgb_base:
            r, g, b = rgb_base[hex_code]
            # Interpolation linéaire vers le blanc (255, 255, 255)
            new_r = int(r + (255 - r) * facteur_blanchiment)
            new_g = int(g + (255 - g) * facteur_blanchiment)
            new_b = int(b + (255 - b) * facteur_blanchiment)
            # Conversion en format normalisé pour Matplotlib (0.0 à 1.0)
            color_plt = (new_r / 255.0, new_g / 255.0, new_b / 255.0)
        else:
            color_plt = hex_code

        # Création de la portion de cercle (Wedge) pour Matplotlib
        wedge = patches.Wedge(
            (0, 0),
            rayon_disque,
            angle_depart,
            angle_depart + ouverture_secteur,
            facecolor=color_plt,
            edgecolor=color_plt,
        )
        ax.add_patch(wedge)

    # Axe central fixe
    axe_central = plt.Circle(
        (0, 0), 5, facecolor="#1e293b", edgecolor="white", lw=1
    )
    ax.add_patch(axe_central)

    # Texte indicatif de l'état de la vitesse en haut à gauche
    txt_vitesse = f"{vitesse:.1f} tr/s" if anim_en_cours else "Statique"
    ax.text(
        -105,
        95,
        f"Vitesse : {txt_vitesse}",
        color="white",
        fontsize=9,
        fontweight="bold",
    )

    return fig

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

# --- SIGNATURE DE L'AUTEUR (Placée en bas de la barre latérale) ---
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)


# Initialisation d'un flag de verrouillage dans le session_state s'il n'existe pas
if "verrouille" not in st.session_state:
    st.session_state.verrouille = False

# 2. Initialisation des variables de session
if "nom_var" not in st.session_state:
    st.session_state.nom_var = ""
if "prenom_var" not in st.session_state:
    st.session_state.prenom_var = ""
if "classe_var" not in st.session_state:
    st.session_state.classe_var = ""
if "heure_var" not in st.session_state:
    st.session_state.heure_var = datetime.now().strftime("%d/%m/%Y %H:%M")
if "mesures_sin_i" not in st.session_state:
    st.session_state.mesures_sin_i = []
if "mesures_sin_r" not in st.session_state:
    st.session_state.mesures_sin_r = []
if "mesures_deg_i" not in st.session_state:
    st.session_state.mesures_deg_i = []
if "mesures_deg_r" not in st.session_state:
    st.session_state.mesures_deg_r = []
if "var_angle_incidence" not in st.session_state:
    st.session_state.var_angle_incidence = 45.0
if "var_indice_n" not in st.session_state:
    st.session_state.var_indice_n = 1.515
if "var_texte_resultats_decomposition" not in st.session_state:
    st.session_state.var_texte_resultats_decomposition = ""
if "var_vitesse_disque" not in st.session_state:
    st.session_state.var_vitesse_disque = 5.0
if "var_mode_synthese" not in st.session_state:
    st.session_state.var_mode_synthese = "Additive"
if "var_opacite_synthese" not in st.session_state:
    st.session_state.var_opacite_synthese = 1.0
if "anim_en_cours" not in st.session_state:
    st.session_state.anim_en_cours = False
if "quiz1_valide" not in st.session_state:
    st.session_state.quiz1_valide = False
if "quiz1_score_txt" not in st.session_state:
    st.session_state.quiz1_score_txt = ""

    
# Couleurs et codes hexadécimaux
if "var_rouge" not in st.session_state: st.session_state.var_rouge = 0
if "var_vert" not in st.session_state: st.session_state.var_vert = 0
if "var_bleu" not in st.session_state: st.session_state.var_bleu = 0
if "var_cyan" not in st.session_state: st.session_state.var_cyan = 0
if "var_magenta" not in st.session_state: st.session_state.var_magenta = 0
if "var_jaune" not in st.session_state: st.session_state.var_jaune = 0    
# Initialisation des modes examen pour les onglets (tab1 à tab9)
for i in range(1, 10):
    key = f"mode_examen_tab{i}"
    if key not in st.session_state:
        st.session_state[key] = False



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
            
            # 1. ON ENREGISTRE D'ABORD LES CURSEURS
            st.session_state.var_angle_incidence = st.slider(
                "Angle d'incidence i (°):",
                min_value=10.0, max_value=80.0,
                value=st.session_state.var_angle_incidence,
                step=0.5, key="slider_angle",
                disabled=st.session_state.mode_examen_tab1
            )

            st.session_state.var_indice_n = st.slider(
                "Indice de base n :",
                min_value=1.30, max_value=1.80,
                value=st.session_state.var_indice_n,
                step=0.005, key="slider_indice",
                disabled=st.session_state.mode_examen_tab1
            )
            
            # 2. ON CORRIGE : ON FORCE LE CALCUL TECHNIQUE IMMÉDIATEMENT APRÈS LA LECTURE DES SLIDERS
            fig_decomposition = mettre_a_jour_decomposition()

            # 3. ON AFFICHE LE TEXTE CALCULÉ ET RAFRAÎCHI
            if st.session_state.var_texte_resultats_decomposition:
                st.code(st.session_state.var_texte_resultats_decomposition)
            else:
                st.info("Résultats de la décomposition")

        # --- CADRAN 2 : Recomposition ---
        with st.container(border=True):
            st.markdown("**Recomposition de la lumière du soleil**")
            
            label_bouton = "Arrêter le Disque" if st.session_state.anim_en_cours else "Lancer le Disque"
            if st.button(label_bouton, key="btn_disque_action", disabled=st.session_state.mode_examen_tab1):
                st.session_state.anim_en_cours = not st.session_state.anim_en_cours
                gerer_action_disque()
                st.rerun()

            st.session_state.var_vitesse_disque = st.slider(
                "Vitesse du disque (tr/s) :",
                min_value=1.0,
                max_value=40.0,
                value=st.session_state.var_vitesse_disque,
                step=1.0,
                key="slider_vitesse_disque"
            )


    with col_droite:
        # 4. AFFICHAGE DIRECT DES FIGURES DE DIFFRACTION DE L'ATELIER
        st.pyplot(fig_decomposition)
        st.markdown("---")
        fig_disque = dessiner_disque_newton()
        st.pyplot(fig_disque)

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
            # ÉVALUATION DIRECTE LIÉE AUX VALEURS COURANTES DU LABORATOIRE
            # Pas besoin de scénario fixe, on note les questions textuelles stables
            
            # Partie 1 : Quiz (10 Pts)
            attendus_qo1_v = {
                "q3": "Dispersion", "q4": "Angles", "q5": "Violet", 
                "q6": "Newton", "q7": "A = r1 + r2", "q8": "Blanche", 
                "q9": "Augmente", "q10": "Monochromatique"
            }
            # Calcul de la note du Quiz (ramene sur 10 points pour les questions de cours stables)
            score_quiz_opt1 = sum([1.25 for qk, qv in attendus_qo1_v.items() if st.session_state.get(f"col_g_quiz_opt1_{qk}_opt1") == qv])
            score_quiz_opt1 = min(10.0, round(score_quiz_opt1, 1))

            # Partie 2 : Texte a Trous (10 Pts)
            attendus_to1_v = {"t1": "Dispersion", "t2": "Devie", "t5": "Blanche"}
            score_trous_opt1 = sum([3.33 for tk, tv in attendus_to1_v.items() if st.session_state.get(f"opt1_{tk}") == tv])
            score_trous_opt1 = min(10.0, round(score_trous_opt1, 1))

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

        # Heure locale francaise native stable (UTC+2)
        from datetime import timedelta
        timestamp_opt1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 1 SCELLE ET VALIDE | Note : {tot_s} / 20")

        attendus_qo1_v = {
            "q3": "Dispersion", "q4": "Angles", "q5": "Violet", 
            "q6": "Newton", "q7": "A = r1 + r2", "q8": "Blanche", 
            "q9": "Augmente", "q10": "Monochromatique"
        }
        attendus_to1_v = {"t1": "Dispersion", "t2": "Devie", "t5": "Blanche"}

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
                &bull; Partie 2 : Synthese de Cours (Texte a trous items de cours) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE CONNAISSANCES OPTIQUES (10 PTS)</div>
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

        for idx_t, (q_id, q_txt) in enumerate(attendus_qo1_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt1_{q_id}_opt1", "Choisir...")
            attendu = attendus_qo1_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"
        html_export_opt1 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to1_v.items(), 1):
            saisie = st.session_state.get(f"opt1_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

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

with tab2:
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
            st.session_state.var_sel_metal = st.selectbox(
                "Choisir un flacon de sel :",
                options=liste_metaux,
                index=liste_metaux.index(st.session_state.var_sel_metal),
                key="select_metal_tab2_final",
                disabled=st.session_state.mode_examen_tab2,
            )

            # Recuperation des donnees du metal et mise a jour de la description
            info_metal = gerer_changement_metal()
            st.info(f"**Analyse :** {info_metal['descr']}")

            # Bouton d'action pour declencher la combustion sequentielle
            label_bouton = (
                "Eteindre le bruleur"
                if st.session_state.var_combustion_active
                else "Bruler l'echantillon (Test de flamme)"
            )
            if st.button(
                label_bouton, key="btn_flamme_tab2_final", use_container_width=True
            ):
                declencher_test_flamme_web()
                st.rerun()

            # Rendu visuel de la simulation de la flamme du bec bunsen
            st.markdown("**Visualisation du brûleur Bec Bunsen :**")
            if st.session_state.var_versement_poudre:
                st.markdown(
                    '<div style="background-color: #475569; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 2px dashed #94a3b8;"><span style="color: #ffffff; font-weight: bold;">Versement de la poudre en cours...</span></div>',
                    unsafe_allow_html=True,
                )
            elif st.session_state.var_combustion_active:
                st.markdown(
                    f'<div style="background-color: {info_metal["couleur"]}; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 1px solid #ffffff;"><span style="color: #0d1117; font-weight: bold;">Combustion active : {st.session_state.var_sel_metal}</span></div>',
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
            st.session_state.source_lumineuse_choisie = st.selectbox(
                "Source lumineuse :",
                options=liste_lampes,
                index=liste_lampes.index(
                    st.session_state.source_lumineuse_choisie
                ),
                key="select_lampe_tab2_final",
                disabled=st.session_state.mode_examen_tab2,
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

        # Horodatage local francais natif synchrone
        from datetime import timedelta
        timestamp_opt2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 2 SCELLE ET VALIDE | Note : {tot_s} / 20")

        attendus_qo2_v = {
            "q1": "Spectre d'emission de raies", "q2": "Corps dense incandescent (Lampe a filament)", 
            "q3": "Jaune orange intense", "q4": "Vert pre / turquoise", 
            "q5": "Chaque element a des raies uniques", "q6": "Spectre d'absorption de raies", 
            "q7": "Spectroscope / Spectrometre", "q8": "Nanometre (nm)", 
            "q9": "Jaune", "q10": "D'absorption de raies (Fraunhofer)"
        }
        attendus_to2_v = {"t1": "Emission", "t2": "Jaune", "t3": "Continu", "t4": "Absorption", "t5": "Nanometres"}

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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 2</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire de Connaissances (Quiz 10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 5 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LES DIFFÉRENTES LUMIÈRES (10 PTS)</div>
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


                
with tab3:
    st.header("Atelier 3 : Lois de la Reflexion & Applications Metiers")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel de la Premiere Loi de Snell-Descartes pour la Reflexion :</p>
        <ul>
            <li><strong>Loi fondamentale :</strong> $i = i'$ (L'angle de reflexion $i'$ est rigoureusement egal a l'angle d'incidence $i$).</li>
            <li><strong>Mesure des angles :</strong> Les deux angles sont mesures par rapport a la <strong>normale</strong> (la droite perpendiculaire a la surface du miroir au point d'impact).</li>
            <li><strong>Application du Spectre de Pepper :</strong> Permet de creer une image virtuelle superposee a un objet reel par une inclinaison precise a $45.0^\circ$.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt3_verrouille" not in st.session_state: st.session_state.opt3_verrouille = False

    # Initialisation permanente du tableau de mesures pour l'exercice de l'eleve
    if "mesures_reflexion_i" not in st.session_state: st.session_state.mesures_reflexion_i = []
    if "mesures_reflexion_iprime" not in st.session_state: st.session_state.mesures_reflexion_iprime = []

    # =========================================================================
    # ARCHITECTURE DOUBLE COLONNE : SIMULATEURS PHYSIQUES / EXAMEN FORMEL
    # =========================================================================
    col_g_laboratoire, col_d_questionnaires = st.columns([1.5, 1.5])

    # --- PANNEAU DE GAUCHE : LABORATOIRES VISUELS INTERACTIFS ---
    with col_g_laboratoire:
        st.subheader("Laboratoire Virtuel de Reflexion")
        
        # MODULE A : REFLÉXION PURE ET TABLEAU DE BORD TREEVIEW RECONVERTI
        with st.container(border=True):
            st.markdown("**Manipulation A : Verification experimentale (Miroir plan)**")
            
            # Le curseur d'angle d'incidence exclusif
            st.slider("Angle d'incidence i (degrés) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="slider_angle_ref_i")
            
            # Bouton d'action connecte au systeme de memorisation
            if st.button("PRENDRE UNE MESURE (MIROIR)", key="btn_ajouter_mesure_ref", use_container_width=True):
                ajouter_mesure_reflexion_pure_streamlit()
                st.rerun()
            
            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            # Affichage synchrone du rayon laser et du miroir horizontal
            fig_miroir_laser = mettre_a_jour_reflexion_pure_matplotlib()
            st.pyplot(fig_miroir_laser, use_container_width=True)

            # Boîte de resultats technique locale sous le graphique
            st.info(st.session_state.get("opt3_txt_box_ref", "Ajustez le curseur pour initialiser."))

            # Affichage de l'historique des mesures (Treeview) sous forme de tableau Pandas propre
            import pandas as pd
            st.markdown("##### Historique des points de mesures enregistres")
            if st.session_state.get("mesures_reflexion_i"):
                df_mesures = pd.DataFrame({
                    "N° Essai": [f"Essai {idx}" for idx in range(1, len(st.session_state.mesures_reflexion_i) + 1)],
                    "Incidence i (°)": [f"{val:.1f}°" for val in st.session_state.mesures_reflexion_i],
                    "Réflexion i' (°)": [f"{val:.1f}°" for val in st.session_state.mesures_reflexion_iprime],
                    "Loi : i = i' ?": ["Oui (100%)" for _ in st.session_state.mesures_reflexion_i]
                })
                st.dataframe(df_mesures, use_container_width=True, hide_index=True)
            else:
                st.caption("Tableau vide. Cliquez sur le bouton bleu ci-dessus pour memoriser l'angle courant.")

        # MODULE B : ILLUSION D'OPTIQUE (SPECTRE DE PEPPER)
        with st.container(border=True):
            st.markdown("**Manipulation B : Illusion d'optique (Affichage Tete Haute - HUD)**")
            
            # Curseur interactif d'angle connecté au moteur physique
            st.slider("Angle d'inclinaison du pare-brise i (degrés) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="slider_angle_ill")
            
            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            # APPEL ET RENDU DE LA GRAPHISQUE VECTORIELLE DU PAR-BRISE HUD
            fig_hud_illusion = mettre_a_jour_illusion_matplotlib()
            st.pyplot(fig_hud_illusion, use_container_width=True)

            # Affichage de la boîte de résultats technique en couleur
            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            st.info(st.session_state.get("opt3_txt_box_ill", "Ajustez le curseur pour initialiser la matrice."))
            
            angle_illusion = st.slider("Angle du miroir plan i (°) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="slider_angle_ill_quiz")
            


        # MODULE C : SIMULATION DES RÉTROVISEURS MÉTIERS
        with st.container(border=True):
            st.markdown("**Manipulation C : Conduite & Topographie (Simulation Retroviseurs)**")
            
            st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            st.markdown("##### Carte interactive du champ de vision arriere")
            
            # APPEL ET AFFICHAGE SYNCHRONE DE LA MAP DE LA ROUTE MATPLOTLIB
            fig_retro_route = mettre_a_jour_retroviseurs_matplotlib()
            st.pyplot(fig_retro_route, use_container_width=True)
            observateur = st.selectbox("Qui regarde dans les miroirs ?", ["Conducteur", "Passager Avant"], key="combo_obs_retro_final")
            retro_gauche = st.slider("Orientation Retroviseur Gauche (°)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0, key="slide_retro_g_eval")
            retro_interne = st.slider("Orientation Retroviseur Interne Central (°)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0, key="slide_retro_i_eval")
            retro_droit = st.slider("Orientation Retroviseur Droit (°)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0, key="slide_retro_d_eval")
            
            st.slider("Position Avancement Siege Conducteur (cm)", min_value=-15.0, max_value=15.0, value=0.0, step=1.0, key="slide_siege_cond_eval")
            st.slider("Position Avancement Siege Passager (cm)", min_value=-15.0, max_value=15.0, value=0.0, step=1.0, key="slide_siege_pass_eval")
            st.caption(f"Position active calculee pour le profil : {observateur}")


        # INTERCONNEXION DU CURSEUR PHYSIQUE DU PÉRISCOPE (MANQUANT SUR L'ÉCRAN)
        with st.container(border=True):
            st.markdown("**Manipulation D : Application Navale (Le Periscope du sous-marin)**")
            
            # Curseur d'angle unique connecté au moteur du périscope Matplotlib
            st.slider(
                "Angle d'inclinaison des miroirs internes (degrés) :", 
                min_value=0.0, 
                max_value=90.0, 
                value=45.0, 
                step=1.0, 
                key="slider_angle_periscope"
            )
            
            st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            # Rendu graphique dynamique de la canalisation du laser périscopique
            fig_periscope = mettre_a_jour_periscope_matplotlib()
            st.pyplot(fig_periscope, use_container_width=True)

            # Boîte de résultats technique locale
            st.info(st.session_state.get("opt3_txt_box_periscope", "Ajustez la reglette pour deplacer le laser."))



       # =========================================================================
        # RECONSTRUCTION DE LA MISE EN PAGE GLOBALE (SORTIE DES COLONNES)
        # =========================================================================
        
    # 1. On ferme d'abord proprement l'espace du laboratoire du haut
    st.write("---")

    # 2. ON EXÉCUTE LES QUESTIONNAIRES SUR TOUTE LA LARGEUR DE L'ÉCRAN
    if "opt3_verrouille" not in st.session_state: 
        st.session_state.opt3_verrouille = False

    # L'appel genere automatiquement ses propres sous-colonnes internes de gauche et droite
    dict_q3, dict_t3 = afficher_questions_optique3(verrouille=st.session_state.get("opt3_verrouille", False))

    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION AUTOMATIQUE SUR 20 POINTS
    # =========================================================================
    st.markdown("---")
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
            # Correction de la Partie 1 (Quiz)
            attendus_qo3_v = {
                "q1": "Strictement l'angle i", "q2": "La normale au miroir", "q3": "35°", 
                "q4": "45°", "q5": "0°", "q6": "Reflexion", "q7": "Virtuelle", 
                "q8": "Changent (il faut reregler)", "q9": "Oui", "q10": "90°"
            }
            score_quiz_opt3 = sum([1.0 for qk, qv in attendus_qo3_v.items() if st.session_state.get(f"col_g_quiz_opt3_{qk}") == qv])

            # Correction de la Partie 2 (Texte a trous)
            score_trous_opt3 = 0.0
            if st.session_state.get("opt3_t1") == "Egal": score_trous_opt3 += 3.33
            if st.session_state.get("opt3_t2") == "Normale": score_trous_opt3 += 3.33
            if st.session_state.get("opt3_t3") == "45": score_trous_opt3 += 3.34

            st.session_state.score_opt3_p1 = round(score_quiz_opt3, 1)
            st.session_state.score_opt3_p2 = round(min(10.0, score_trous_opt3), 1)
            st.session_state.score_final_opt3 = round(score_quiz_opt3 + min(10.0, score_trous_opt3), 1)
            st.session_state.opt3_verrouille = True
            st.rerun()

    if st.session_state.get("opt3_verrouille", False):
        scr1 = st.session_state.get("score_opt3_p1", 0.0)
        scr2 = st.session_state.get("score_opt3_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt3", 0.0)

        from datetime import timedelta
        timestamp_opt3 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 3 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo3_v = {
            "q1": "Strictement l'angle i", "q2": "La normale au miroir", "q3": "35°", 
            "q4": "45°", "q5": "0°", "q6": "Reflexion", "q7": "Virtuelle", 
            "q8": "Changent (il faut reregler)", "q9": "Oui", "q10": "90°"
        }
        attendus_to3_v = {"t1": "Egal", "t2": "Normale", "t3": "45"}

        html_export_opt3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 3 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; position: relative; }}
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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 3</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE CALCULS ET FORMULES (10 PTS)</div>
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

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo3_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt3_{q_id}", "Choisir...")
            attendu = attendus_qo3_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt3 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt3 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to3_v.items(), 1):
            saisie = st.session_state.get(f"opt3_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt3 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique3_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_opt3,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True)



with tab4:
    st.header("Atelier 4 : Lois de Snell-Descartes & Applications Industrielles")
    
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
    col_g_commandes, col_d_graphiques = st.columns([1.2, 2.2])

    # --- PANNEAU DE GAUCHE : LES PANNEAUX DE COMMANDES 1 & 2 RECONVERTIS ---
    with col_g_commandes:
        
        # BLOC 1 : PANNEAU DE COMMANDE DE LA RÉFRACTION SIMPLE
        with st.container(border=True):
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

        # BLOC 2 : PANNEAU DE COMMANDE DE LA DOUBLE RÉFRACTION
        with st.container(border=True):
            st.markdown("<p style='color:#991b1b; font-weight:bold; margin-bottom:2px;'>2. DOUBLE REFRACTION</p>", unsafe_allow_html=True)
            
            choix_lampe2 = st.selectbox("Source lumineuse  :", liste_lampes, key="var_choix_lampe_double2", disabled=st.session_state.opt4_verrouille)
            angle_double = st.slider("Angle d'incidence double (°) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="var_angle_double", disabled=st.session_state.opt4_verrouille)
            
            milieu1_d = st.selectbox("Milieu 1 (n1) :", liste_milieux, index=0, key="var_choix_milieu1_double", disabled=st.session_state.opt4_verrouille)
            milieu2_d = st.selectbox("Milieu 2 - Lame (n2) :", liste_milieux, index=2, key="var_choix_milieu2_double", disabled=st.session_state.opt4_verrouille)
            milieu3_d = st.selectbox("Milieu 3 (n3) :", liste_milieux, index=0, key="var_choix_milieu3_double", disabled=st.session_state.opt4_verrouille)

    # --- PANNEAU DE DROITE : TRACÉS GRAPHIQUES ET ET TABLES DE MESURES ---
    with col_d_graphiques:
        st.subheader("Visualisations des trajectoires optiques")
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
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
        with col_img2:
            # APPEL DE VOTRE GRAPHIQUE LINÉAIRE EXPERIMENTAL SIN(R) = F(SIN(I))
            fig_loi_sinus = dessiner_graphique_sinus_matplotlib()
            st.pyplot(fig_loi_sinus, use_container_width=True)

        # Rendu du second schema de la double refraction en dessous
        st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        
        fig_double_dioptre = dessiner_double_refraction_lame_matplotlib()
        st.pyplot(fig_double_dioptre, use_container_width=True)
        
        # Boîte blanche flottante mémorisée dans la session
        st.info(st.session_state.get("opt4_txt_box_double", "Ajustez les curseurs pour initialiser la lame."))
        



    # =========================================================================
    # DEPLOYEMENT DES QUESTIONNAIRES GENERAUX SUR TOUTE LA LARGEUR DE LA PAGE
    # =========================================================================
    st.write("---")
    dict_q4, dict_t4 = afficher_questions_optique4(verrouille=st.session_state.get("opt4_verrouille", False))

    # =========================================================================
    # ZONE DE NOTATION ET BOUTON D'EXPORTATION DU BILAN HTML SUR 20 POINTS
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 4")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_opt4 = st.checkbox(

        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 4.", 
        key="check_certif_opt4_officiel_20pts", 
        disabled=st.session_state.get("opt4_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_opt4_official_20pts", use_container_width=True, disabled=st.session_state.get("opt4_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt4: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            attendus_qo4_v = {
                "q1": "n1 * sin(i1) = n2 * sin(i2)", "q2": "Le rayon se rapproche de la normale", 
                "q3": "0 degres", "q4": "1.00", "q5": "Superieur ou egal a 1", 
                "q6": "Parallele (avec un decalage lateral dx)", "q7": "Refraction (courbure des rayons)", 
                "q8": "Le dioptre", "q9": "Augmenter", "q10": "Le rapport des indices n2 / n1"
            }
            score_quiz_opt4 = sum([1.0 for qk, qv in attendus_qo4_v.items() if st.session_state.get(f"col_g_quiz_opt4_{qk}") == qv])

            score_trous_opt4 = 0.0
            if st.session_state.get("opt4_t1") == "Dioptre": score_trous_opt4 += 2.5
            if st.session_state.get("opt4_t2") == "Refraction": score_trous_opt4 += 2.5
            if st.session_state.get("opt4_t3") == "Sinus": score_trous_opt4 += 2.5
            if st.session_state.get("opt4_t4") == "Emergent": score_trous_opt4 += 2.5

            st.session_state.score_opt4_p1 = round(score_quiz_opt4, 1)
            st.session_state.score_opt4_p2 = round(score_trous_opt4, 1)
            st.session_state.score_final_opt4 = round(score_quiz_opt4 + score_trous_opt4, 1)
            st.session_state.opt4_verrouille = True
            st.rerun()

    if st.session_state.get("opt4_verrouille", False):
        scr1 = st.session_state.get("score_opt4_p1", 0.0)
        scr2 = st.session_state.get("score_opt4_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt4", 0.0)

        from datetime import timedelta
        timestamp_opt4 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 4 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo4_v = {
            "q1": "n1 * sin(i1) = n2 * sin(i2)", "q2": "Le rayon se rapproche de la normale", 
            "q3": "0 degres", "q4": "1.00", "q5": "Superieur ou egal a 1", 
            "q6": "Parallele (avec un decalage lateral dx)", "q7": "Refraction (courbure des rayons)", 
            "q8": "Le dioptre", "q9": "Augmenter", "q10": "Le rapport des indices n2 / n1"
        }
        attendus_to4_v = {"t1": "Dioptre", "t2": "Refraction", "t3": "Sinus", "t4": "Emergent"}

        html_export_opt4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 4 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; position: relative; }}
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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 4</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 4 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE SNELL-DESCARTES (10 PTS)</div>
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

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo4_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt4_{q_id}", "Choisir...")
            attendu = attendus_qo4_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt4 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt4 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to4_v.items(), 1):
            saisie = st.session_state.get(f"opt4_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt4 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt4 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique4_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 4 SUR VOTRE ORDINATEUR",
            data=html_export_opt4,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )

with tab5:
    st.header("Atelier 5 : Lentilles Minces Convergentes & Relation de Conjugaison")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel des Formules de la Dioptrique (Lentilles Convergentes) :</p>
        <ul>
            <li><strong>Relation de conjugaison de Descartes :</strong> $\\frac{1}{x'} - \\frac{1}{x} = \\frac{1}{f'}$ &nbsp;(avec $x = \\overline{OA}$ et $x' = \\overline{OA'}$)</li>
            <li><strong>Vergence d'une lentille :</strong> $C = \\frac{1}{f'}$ &nbsp;(exprimee en Dioptries $\\delta$ avec $f'$ en metres)</li>
            <li><strong>Grandissement transversal :</strong> $\\gamma = \\frac{\\overline{A'B'}}{\\overline{AB}} = \\frac{x'}{x}$</li>
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
    st.subheader("Validation et Generation du Bilan Officiel - Optique 5")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

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
            # Moteur de correction automatique du Quiz
            attendus_qo5_v = {
                "q1": "1/x' - 1/x = 1/f'", "q2": "Continue en ligne droite sans subir de deviation", 
                "q3": "Le foyer image F'", "q4": "La dioptrie (delta)", "q5": "Reelle et renversee", 
                "q6": "Renversee par rapport a l'objet", "q7": "A l'infini", 
                "q8": "Plus minces que son centre", "q9": "+2.0", "q10": "-1"
            }
            score_quiz_opt5 = sum([1.0 for qk, qv in attendus_qo5_v.items() if st.session_state.get(f"col_g_quiz_opt5_{qk}") == qv])

            # Moteur de correction automatique du Texte a trous
            score_trous_opt5 = 0.0
            if st.session_state.get("opt5_t1") == "Convergente": score_trous_opt5 += 2.5
            if st.session_state.get("opt5_t2") == "Image F'": score_trous_opt5 += 2.5
            if st.session_state.get("opt5_t3") == "Dioptries": score_trous_opt5 += 2.5
            if st.session_state.get("opt5_t4") == "Grandissement": score_trous_opt5 += 2.5

            st.session_state.score_opt5_p1 = round(score_quiz_opt5, 1)
            st.session_state.score_opt5_p2 = round(score_trous_opt5, 1)
            st.session_state.score_final_opt5 = round(score_quiz_opt5 + score_trous_opt5, 1)
            st.session_state.opt5_verrouille = True
            st.rerun()

    # LE BLOC D'EXPORT PERMANENT LIÉ AU VERROU (RESTAURÉ)
    if st.session_state.get("opt5_verrouille", False):
        scr1 = st.session_state.get("score_opt5_p1", 0.0)
        scr2 = st.session_state.get("score_opt5_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt5", 0.0)

        from datetime import timedelta
        timestamp_opt5 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 5 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo5_v = {
            "q1": "1/x' - 1/x = 1/f'", "q2": "Continue en ligne droite sans subir de deviation", 
            "q3": "Le foyer image F'", "q4": "La dioptrie (delta)", "q5": "Reelle et renversee", 
            "q6": "Renversee par rapport a l'objet", "q7": "A l'infini", 
            "q8": "Plus minces que son centre", "q9": "+2.0", "q10": "-1"
        }
        attendus_to5_v = {"t1": "Convergente", "t2": "Image F'", "t3": "Dioptries", "t4": "Grandissement"}

        # Generation du document HTML propre pour le professeur Gallet
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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 5</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 4 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE CONJUGAISON (10 PTS)</div>
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

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo5_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt5_{q_id}", "Choisir...")
            attendu = attendus_qo5_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt5 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt5 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to5_v.items(), 1):
            saisie = st.session_state.get(f"opt5_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt5 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt5 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique5_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 5 SUR VOTRE ORDINATEUR",
            data=html_export_opt5,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )



with tab6:
    st.header("Atelier 6 : Lentilles Minces Divergentes & Applications Visuelles")
    
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

        nom_f = f"Rapport_Evaluation_Optique6_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 6 SUR VOTRE ORDINATEUR",
            data=html_export_opt6,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )

with tab7:
    st.header("Atelier 7 : La Lunette Astronomique de Kepler")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel du Modele de la Lunette Afocale :</p>
        <ul>
            <li><strong>Configuration afocale :</strong> La distance entre les deux lentilles est egale a la somme de leurs distances focales ($d = O_1O_2 = f'_1 + f'_2$).</li>
            <li><strong>Grossissement de l'instrument :</strong> Le grossissement nominal se calcule par la relation $G = \\frac{f'_1}{f'_2}$.</li>
            <li><strong>Confort visuel :</strong> L'image finale sortant de l'oculaire est rejetee a l'infini, permettant a l'oeil du marin ou de l'astronome d'observer l'astre sans aucune fatigue (pas d'accommodation).</li>
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
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt7: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Moteur de correction automatique du Quiz (Partie 1)
            attendus_qo7_v = {
                "q1": "Objectif (de grande distance focale)", "q2": "Oculaire", 
                "q3": "A l'infini (confort de vision sans fatigue pour l'oeil)", 
                "q4": "Le foyer objet F2 de l'oculaire", "q5": "Reelle et renversee (situee dans le plan focal commun)", 
                "q6": "A l'infini (pas besoin d'accommoder)", "q7": "G = f'1 / f'2", 
                "q8": "20", "q9": "Renversee (haut-bas et droite-gauche)", "q10": "L'objectif par l'oculaire"
            }
            score_quiz_opt7 = sum([1.0 for qk, qv in attendus_qo7_v.items() if st.session_state.get(f"col_g_quiz_opt7_{qk}") == qv])

            # Moteur de correction automatique du Texte a trous (Partie 2)
            score_trous_opt7 = 0.0
            if st.session_state.get("opt7_t1") == "Objectif": score_trous_opt7 += 2.5
            if st.session_state.get("opt7_t2") == "Oculaire": score_trous_opt7 += 2.5
            if st.session_state.get("opt7_t3") == "Afocal": score_trous_opt7 += 2.5
            if st.session_state.get("opt7_t4") == "Grossissement": score_trous_opt7 += 2.5

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

        from datetime import timedelta
        from datetime import datetime
        timestamp_opt7 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 7 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo7_v = {
            "q1": "Objectif (de grande distance focale)", "q2": "Oculaire", 
            "q3": "A l'infini (confort de vision sans fatigue pour l'oeil)", 
            "q4": "Le foyer objet F2 de l'oculaire", "q5": "Reelle et renversee (situee dans le plan focal commun)", 
            "q6": "A l'infini (pas besoin d'accommoder)", "q7": "G = f'1 / f'2", 
            "q8": "20", "q9": "Renversee (haut-bas et droite-gauche)", "q10": "L'objectif par l'oculaire"
        }
        attendus_to7_v = {"t1": "Objectif", "t2": "Oculaire", "t3": "Afocal", "t4": "Grossissement"}

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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 7</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 4 items) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LA LUNETTE KEPLERIENNE (10 PTS)</div>
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

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo7_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt7_{q_id}", "Choisir...")
            attendu = attendus_qo7_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to7_v.items(), 1):
            saisie = st.session_state.get(f"opt7_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique7_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 7 SUR VOTRE ORDINATEUR",
            data=html_export_opt7,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )

with tab8:
    st.header("Atelier 8 : La Lunette Astronomique de Galilee")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel du Modele de la Lunette de Galilee :</p>
        <ul>
            <li><strong>Association Optique :</strong> Elle associe un <strong>objectif convergent</strong> ($f'_1 > 0$) et un <strong>oculaire divergent</strong> ($f'_2 < 0$).</li>
            <li><strong>Condition Afocale :</strong> Le foyer image de l'objectif et le foyer objet de l'oculaire sont confondus ($F'_1 = F_2$). La distance separent les verres est reduite : $d = f'_1 - |f'_2|$.</li>
            <li><strong>Propriete d'image :</strong> Contrairement au systeme de Kepler, la lunette de Galilee fournit une <strong>image finale droite</strong> (redressee, dans le meme sens que l'objet).</li>
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
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 8")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

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
            # Correction Automatique de la Partie 1
            attendus_qo8_v = {
                "q1": "L'oculaire de Galilee est une lentille divergente", "q2": "Strictement negative (f'2 < 0)", 
                "q3": "Le foyer objet F2 de l'oculaire divergent", "q4": "Droite (dans le meme sens que l'astre)", 
                "q5": "f'1 + f'2 (ce qui donne une soustraction car f'2 est negatif)", "q6": "Plus courte que celle de Kepler", 
                "q7": "Positif (l'image finale est droite)", "q8": "4.0 (car f'2 est negatif)", 
                "q9": "Un champ visuel tres etroit", "q10": "Les jumelles de theatre (ou de spectacle)"
            }
            score_quiz_opt8 = sum([1.0 for qk, qv in attendus_qo8_v.items() if st.session_state.get(f"col_g_quiz_opt8_{qk}") == qv])

            # Correction Automatique de la Partie 2
            score_trous_opt8 = 0.0
            if st.session_state.get("opt8_t1") == "Divergente": score_trous_opt8 += 3.33
            if st.session_state.get("opt8_t2") == "Objet F2": score_trous_opt8 += 3.33
            if st.session_state.get("opt8_t3") == "Droite": score_trous_opt8 += 3.34

            st.session_state.score_opt8_p1 = round(score_quiz_opt8, 1)
            st.session_state.score_opt8_p2 = round(min(10.0, score_trous_opt8), 1)
            st.session_state.score_final_opt8 = round(score_quiz_opt8 + min(10.0, score_trous_opt8), 1)
            st.session_state.opt8_verrouille = True
            st.rerun()

    if st.session_state.get("opt8_verrouille", False):
        scr1 = st.session_state.get("score_opt8_p1", 0.0)
        scr2 = st.session_state.get("score_opt8_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt8", 0.0)

        from datetime import timedelta
        from datetime import datetime
        timestamp_opt8 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 8 SCELLE | Note de session : {tot_s} / 20")

        attendus_qo8_v = {
            "q1": "L'oculaire de Galilee est une lentille divergente", "q2": "Strictement negative (f'2 < 0)", 
            "q3": "Le foyer objet F2 de l'oculaire divergent", "q4": "Droite (dans le meme sens que l'astre)", 
            "q5": "f'1 + f'2 (ce qui donne une soustraction car f'2 est negatif)", "q6": "Plus courte que celle de Kepler", 
            "q7": "Positif (l'image finale est droite)", "q8": "4.0 (car f'2 est negatif)", 
            "q9": "Un champ visuel tres etroit", "q10": "Les jumelles de theatre (ou de spectacle)"
        }
        attendus_to8_v = {"t1": "Divergente", "t2": "Objet F2", "t3": "Droite"}

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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_opt8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Optique 8</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ LUNETTE GALILÉENNE (10 PTS)</div>
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

        for idx_q, (q_id, q_txt) in enumerate(attendus_qo8_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_opt8_{q_id}", "Choisir...")
            attendu = attendus_qo8_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
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

        for idx_t, (t_key, t_val) in enumerate(attendus_to8_v.items(), 1):
            saisie = st.session_state.get(f"opt8_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt8 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt8 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Optique8_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 8 SUR VOTRE ORDINATEUR",
            data=html_export_opt8,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )


with tab9:
    st.header("Atelier 9 : Le Microscope Compose & Double Grossissement")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel du Modele Optique du Microscope :</p>
        <ul>
            <li><strong>Grandissement de l'objectif (L1) :</strong> $\\gamma_1 = - \\frac{\\Delta}{f'_1}$ &nbsp;(avec $\\Delta$ l'intervalle optique entre $F'_1$ et $F_2$).</li>
            <li><strong>Grossissement de l'oculaire (L2) :</strong> $G_{c2} = \\frac{0.25}{f'_2}$ &nbsp;(avec distance minimale de visee standard a $25\\text{ cm}$).</li>
            <li><strong>Grossissement total de l'instrument :</strong> $G = \\gamma_1 \\cdot G_{c2} = - \\frac{\\Delta \\cdot 0.25}{f'_1 \\cdot f'_2}$.</li>
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
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 9")

    case_certif_opt9 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 9.", 
        key="check_certif_opt9_officiel_20pts", 
        disabled=st.session_state.get("opt9_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9", key="btn_export_opt9_official_20pts", use_container_width=True, disabled=st.session_state.get("opt9_verrouille", False)):
        if not st.session_state.get("verrouille", False): st.error("Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt9: st.error("Cochez la case de certification.")
        else:
            attendus_qo9_v = {
                "q1": "Objectif (de tres courte distance focale)", "q2": "Oculaire", "q3": "Reelle, renversee et tres agrandie",
                "q4": "Pile sur le foyer objet F2 de l'oculaire", "q5": "Le foyer image F'1 de l'objectif et le foyer objet F2 de l'oculaire",
                "q6": "gamma1 = - delta / f'1", "q7": "Gc2 = 0.25 / f'2", "q8": "Du grandissement de l'objectif par le grossissement de l'oculaire",
                "q9": "-40 (l'image est inversee et 40 fois plus grande)", "q10": "Inversee et virtuelle"
            }
            score_quiz_opt9 = sum([1.0 for qk, qv in attendus_qo9_v.items() if st.session_state.get(f"col_g_quiz_opt9_{qk}") == qv])

            score_trous_opt9 = 0.0
            if st.session_state.get("opt9_t1") == "Objectif": score_trous_opt9 += 3.33
            if st.session_state.get("opt9_t2") == "Oculaire": score_trous_opt9 += 3.33
            if st.session_state.get("opt9_t3") == "Optique": score_trous_opt9 += 3.34

            st.session_state.score_opt9_p1 = round(score_quiz_opt9, 1)
            st.session_state.score_opt9_p2 = round(min(10.0, score_trous_opt9), 1)
            st.session_state.score_final_opt9 = round(score_quiz_opt9 + min(10.0, score_trous_opt9), 1)
            st.session_state.opt9_verrouille = True
            st.rerun()


