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
        elif "opt1_scenario" not in st.session_state: 
            st.error("Action refusee : Generez d'abord un exercice.")
        else:
            sol = st.session_state.opt1_scenario
            sol_m = sol
            d_r_f = f"{sol_m.get('D_r', 0.0):.1f}"
            d_v_f = f"{sol_m.get('D_v', 0.0):.1f}"
            d_vi_f = f"{sol_m.get('D_vi', 0.0):.1f}"

            # Partie 1 : Quiz (10 Pts)
            attendus_qo1_v = {"q1": d_r_f, "q2": d_vi_f, "q3": "Dispersion", "q4": "Angles", "q5": "Violet", "q6": "Newton", "q7": "A = r1 + r2", "q8": "Blanche", "q9": "Augmente", "q10": "Monochromatique"}
            score_quiz_opt1 = sum([1 for qk, qv in attendus_qo1_v.items() if st.session_state.get(f"col_g_quiz_opt1_{qk}_opt1") == qv])

            # Partie 2 : Texte a Trous (10 Pts)
            attendus_to1_v = {"t1": "Dispersion", "t2": "Devie", "t3": d_r_f, "t4": d_vi_f, "t5": "Blanche"}
            score_trous_opt1 = round(sum([1 for tk, tv in attendus_to1_v.items() if st.session_state.get(f"opt1_{tk}") == tv]) * 2, 1)

            st.session_state.score_opt1_p1 = score_quiz_opt1
            st.session_state.score_opt1_p2 = score_trous_opt1
            st.session_state.score_final_opt1 = round(score_quiz_opt1 + score_trous_opt1, 1)
            st.session_state.opt1_verrouille = True
            st.rerun()

    if st.session_state.get("opt1_verrouille", False):
        sol = st.session_state.opt1_scenario
        sol_m = sol
        d_r_f = f"{sol_m.get('D_r', 0.0):.1f}"
        d_v_f = f"{sol_m.get('D_v', 0.0):.1f}"
        d_vi_f = f"{sol_m.get('D_vi', 0.0):.1f}"
        
        scr1 = st.session_state.get("score_opt1_p1", 0)
        scr2 = st.session_state.get("score_opt1_p2", 0)
        tot_s = st.session_state.get("score_final_opt1", 0)

        from datetime import timedelta
        timestamp_opt1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 1 SCELLE ET VALIDE | Note : {tot_s} / 20")

        attendus_qo1_v = {"q1": d_r_f, "q2": d_vi_f, "q3": "Dispersion", "q4": "Angles", "q5": "Violet", "q6": "Newton", "q7": "A = r1 + r2", "q8": "Blanche", "q9": "Augmente", "q10": "Monochromatique"}
        attendus_to1_v = {"t1": "Dispersion", "t2": "Devie", "t3": d_r_f, "t4": d_vi_f, "t5": "Blanche"}

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
                &bull; Partie 1 : Questionnaire Numerique (Quiz 10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous 5 items) : <strong>{scr2} / 10</strong>
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

        ordre_reel_opt1 = st.session_state.get("ordre_questions_opt1", [])
        for idx_q, (q_id, q_txt) in enumerate(ordre_reel_opt1, 1):
            saisie = st.session_state.get(f"col_g_quiz_opt1_{q_id}", "Choisir...")
            attendu = attendus_qo1_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

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

        for idx_t, t_key in enumerate(["t1", "t2", "t3", "t4", "t5"], 1):
            saisie = st.session_state.get(f"opt1_{t_key}", "Choisir...")
            attendu = attendus_to1_v[t_key]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt1 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'optique geometrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """
        
        nom_f = f"Rapport_Evaluation_Optique1_{n_eleve}_{c_eleve}"
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

    # =====================================================================
    # ZONE BASSE : GRILLE D'EVALUATION ET CONTROLE DE L'EXAMEN
    # =====================================================================
    st.markdown("---")
    col_quiz2, col_controle2 = st.columns(2)

    # Generation des menus déroulants pour le questionnaire

    with col_quiz2:
        st.markdown("##### Évaluation : Les différentes lumières")

        # Grille officielle des 10 questions d'optique pour l'Atelier 2
        base_questions_2 = [
            {"q": "Quel type de spectre obtient-on en analysant la lumiere emise par un gaz d'atomes isoles excites ?", "options": ["Un spectre de raies d'emission", "Un spectre continu d'absorption", "Un spectre de bandes"], "rep": "Un spectre de raies d'emission"},
            {"q": "Quelle source lumineuse classique produit un spectre continu contenant toutes les radiations colorees ?", "options": ["Une lampe a incandescence", "Un laser de laboratoire", "Une lampe a vapeur de sodium"], "rep": "Une lampe a incandescence"},
            {"q": "Lors du test de flamme, quelle couleur caracteristique prend la combustion du chlorure de Sodium (Na) ?", "options": ["Jaune intense", "Vert brillant", "Violet pale"], "rep": "Jaune intense"},
            {"q": "Quelle couleur de flamme specifique permet d'identifyer la presence d'ions Cuivre (Cu) ?", "options": ["Vert-bleu", "Rouge carmin", "Jaune orange"], "rep": "Vert-bleu"},
            {"q": "Pourquoi les raies d'emission d'un element chimique constituent-elles sa signature ou carte d'identite ?", "options": ["Chaque element possede un ensemble unique de longueurs d'onde", "Elles changent de couleur avec la distance", "Elles dependent de l'age du prisme"], "rep": "Chaque element possede un ensemble unique de longueurs d'onde"},
            {"q": "Comment qualifie-t-on le spectre d'une etoile qui traverse une atmosphere gazeuse plus froide ?", "options": ["Un spectre de raies d'absorption", "Un spectre continu pur", "Un spectre polychromatique opaque"], "rep": "Un spectre de raies d'absorption"},
            {"q": "Quel instrument d'optique muni d'un element dispersif permet d'observer ces raies colorees ?", "options": ["Le spectroscope", "Le sonometre", "La lunette afocale"], "rep": "Le spectroscope"},
            {"q": "Quelle est l'unite de mesure utilisee pour reperer la position exacte d'une raie sur l'ecran ?", "options": ["Le nanometre (nm)", "Le Watt (W)", "Le Pascal (Pa)"], "rep": "Le nanometre (nm)"},
            {"q": "Si une source emet une raie unique a 589 nm, dans quel domaine de couleur se situe-t-elle ?", "options": ["Le Jaune", "Le Rouge", "Le Violet"], "rep": "Le Jaune"},
            {"q": "Le spectre de la lumiere émise par le Soleil reçu sur Terre est un spectre :", "options": ["Continu avec des raies d'absorption (Fraunhofer)", "De raies d'emission pur", "Monochromatique strict"], "rep": "Continu avec des raies d'absorption (Fraunhofer)"}
        ]

        # Structure d'enregistrement des réponses de l'Atelier 2
        if "reponses_quiz2" not in st.session_state:
            st.session_state.reponses_quiz2 = {i: "" for i in range(len(base_questions_2))}

        # Rendu des menus déroulants interactifs
        for idx, item in enumerate(base_questions_2):
            options_affichage = list(item["options"])
            
            st.session_state.reponses_quiz2[idx] = st.selectbox(
                f"{idx + 1}. {item['q']}",
                options=[""] + options_affichage,
                index=0 if st.session_state.reponses_quiz2[idx] == "" else options_affichage.index(st.session_state.reponses_quiz2[idx]) + 1,
                key=f"q2_real_{idx}",
                disabled=st.session_state.quiz2_valide
            )
    # Separation de la page en deux colonnes principales
    col_gauche2, col_droite2 = st.columns(2)

    # Cadran de validation et activation de la protection examen
    with col_controle2:
        with st.container(border=True):
            st.markdown(
                "<p style='color:darkblue; font-weight:bold; margin-bottom:0;'>CONTROLE EXAMEN</p>",
                unsafe_allow_html=True,
            )
    with col_controle2:
        with st.container(border=True):
            st.markdown(
                "<p style='color:darkblue; font-weight:bold; margin-bottom:0;'>CONTROLE EXAMEN</p>",
                unsafe_allow_html=True,
            )

            mode_examen2_avant = st.session_state.mode_examen_tab2
            st.session_state.mode_examen_tab2 = st.checkbox(
                "Mode Examen",
                value=st.session_state.mode_examen_tab2,
                key="check_examen_tab2_final",
                disabled=st.session_state.quiz2_valide or mode_examen2_avant,
            )

            if st.session_state.mode_examen_tab2 and not mode_examen2_avant:
                basculer_mode_examen_protection2()
                st.rerun()

            if st.session_state.quiz2_valide:
                st.info(st.session_state.quiz2_score_txt)

            if not st.session_state.quiz2_valide:
                confirmer2 = st.checkbox(
                    "Je confirme vouloir valider définitivement l'évaluation de l'Atelier 2.",
                    key="conf_quiz2_final_propre",
                )
                if st.button(
                    "Valider",
                    key="btn_valider_tab2_final",
                    use_container_width=True,
                    disabled=not confirmer2,
                ):
                    valider_tout2(base_questions_2)
                    st.rerun()
            else:
                st.button(
                    "Validation effectuée",
                    key="btn_valider_tab2_dis_final",
                    use_container_width=True,
                    disabled=True,
                )




                
with tab3:
    st.header("3. La loi de la réflexion")

with tab4:
    st.header("4. La loi de la réfraction")

with tab5:
    st.header("5. Les lentilles convergentes")

with tab6:
    st.header("6. Les lentilles divergentes")

with tab7:
    st.header("7. La lunette astronomique")

with tab8:
    st.header("8. La lunette de Galilée")

with tab9:
    st.header("9. Le microscope")
