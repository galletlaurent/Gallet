# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage du dioxyde de soufre dans le vin blanc",
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
import pandas as pd
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage du dioxyde de soufre dans le vin blanc")
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
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 7.0
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 7.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.005
if "animation_active" not in st.session_state: st.session_state.animation_active = False

if "eau" not in st.session_state:
    st.session_state["eau"] = {
        "Vin blanc : Sec standard": {"SO2": 140.0},
        "Vin blanc : Moelleux / Douceur": {"SO2": 190.0},
        "Vin blanc : Liquoreux d'exception": {"SO2": 240.0},
        "Général : Vin blanc déshydrogéné (Témoin)": {"SO2": 10.0}
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
    "Généralités sur le dioxyde de soufre",
    "Dosage colorimétrique des sulfites d'un vin",
    "Calcul théorique analytique et vérification de la conformité de l'étiquette"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

def afficher_questions_so2_vin_commercial(verrouille=False):
    import streamlit as st

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    dict_reponses_bouteille = {}

    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation du dosage d'oxydoréduction de Ripper (Volume vin Va = 20 mL)</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("1. Convertir le volume équivalent relevé $V_E$ en Litre (L) :")
    with c2: dict_reponses_bouteille["v_eq_l"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_v_eq_l_cl", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("2. Calculer la quantité de matière de molécules de diode apportée à l'équivalence $n_{\\text{I}_2}$ (mol) pour $C_0 = 0,01\\text{ mol/L}$ :")
    with c4: dict_reponses_bouteille["n_argent"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.6f", key="at3_n_argent_cl", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("3. En déduire la quantité de matière de dioxyde de soufre présente dans l'échantillon $n_{\\text{SO}_2}$ (mol) :")
    with c6: dict_reponses_bouteille["n_chlorure"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.6f", key="at3_n_chlorure_becher", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("4. Déterminer la concentration molaire $C_a$ en dioxyde de soufre du vin analysé (mol/L) :")
    with c8: dict_reponses_bouteille["c_molaire"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_c_molaire_cl", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Remontée au titre massique et conclusion analytique</p>", unsafe_allow_html=True)

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("5. En déduire la concentration massique ou titre massique $t$ en dioxyde de soufre (g/L) [$M(SO_2) = 64\\text{ g/mol}$] :")
    with c10: dict_reponses_bouteille["t_g"] = st.number_input("", min_value=0.000, max_value=10.000, format="%.3f", key="at3_t_massique_g", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("6. Exprimer cette concentration massique finale en milligramme par Litre (mg/L) :")
    with c12: dict_reponses_bouteille["t_mg"] = st.number_input("", min_value=0.0, max_value=5000.0, format="%.1f", key="at3_t_massique_mg", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    return dict_reponses_bouteille

def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    v_eq_attendu = st.session_state.get("th_vrai_veq_calc", 12.0)
    c_base_session = 0.01 
    v_eau_dosee = 20.0 

    n_diode_equiv = (c_base_session * v_eq_attendu) / 1000.0
    c_so2_dose_attendu = (c_base_session * v_eq_attendu) / v_eau_dosee

    col_double_quiz_so2, col_double_trous_so2 = st.columns(2)

    with col_double_quiz_so2:
        st.markdown("##### Quiz numérique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        # --- QUESTION 1 ---
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de diode ($C_0$) utilisée ?")
        val_q1 = st.session_state.get("col_g_quiz_ox_q1_tab2", "Choisir...")
        try:
            idx_q1 = opts_q1.index(val_q1)
        except ValueError:
            idx_q1 = 0
            st.session_state["col_g_quiz_ox_q1_tab2"] = "Choisir..."
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, index=idx_q1, key="col_g_quiz_ox_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 2 ---
        opts_q2 = ["Choisir...", f"{v_eau_dosee:.1f} mL", "10.0 mL", "40.0 mL"]
        st.write("**2.** Quel volume d'échantillon de vin blanc analysé ($V_a$) a été introduit dans le bécher ?")
        val_q2 = st.session_state.get("col_g_quiz_ox_q2_tab2", "Choisir...")
        try:
            idx_q2 = opts_q2.index(val_q2)
        except ValueError:
            idx_q2 = 0
            st.session_state["col_g_quiz_ox_q2_tab2"] = "Choisir..."
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, index=idx_q2, key="col_g_quiz_ox_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 3 ---
        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume équivalent exact ($V_E$) de solution de diode versé relevé au changement de teinte ?")
        val_q3 = st.session_state.get("col_g_quiz_ox_q3_tab2", "Choisir...")
        try:
            idx_q3 = opts_q3.index(val_q3)
        except ValueError:
            idx_q3 = 0
            st.session_state["col_g_quiz_ox_q3_tab2"] = "Choisir..."
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, index=idx_q3, key="col_g_quiz_ox_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 4 ---
        opts_q4 = ["Choisir...", "n(I2) = n(SO2)", "n(I2) = 2 * n(SO2)", "2 * n(I2) = n(SO2)"]
        st.write("**4.** Quelle est la relation stœchiométrique à l'équivalence pour ce titrage d'oxydoréduction ?")
        val_q4 = st.session_state.get("col_g_quiz_ox_q4_tab2", "Choisir...")
        try:
            idx_q4 = opts_q4.index(val_q4)
        except ValueError:
            idx_q4 = 0
            st.session_state["col_g_quiz_ox_q4_tab2"] = "Choisir..."
        dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, index=idx_q4, key="col_g_quiz_ox_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 5 ---
        opts_q5 = ["Choisir...", f"{n_diode_equiv:.5f} mol", f"{n_diode_equiv * 10:.5f} mol", "0.00100 mol"]
        st.write("**5.** Quelle quantité de matière de molécules de diode $I_2$ a été apportée à l'équivalence ?")
        val_q5 = st.session_state.get("col_g_quiz_ox_q5_tab2", "Choisir...")
        try:
            idx_q5 = opts_q5.index(val_q5)
        except ValueError:
            idx_q5 = 0
            st.session_state["col_g_quiz_ox_q5_tab2"] = "Choisir..."
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, index=idx_q5, key="col_g_quiz_ox_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 6 ---
        opts_q6 = ["Choisir...", f"{c_so2_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Déduisez-en la concentration molaire en dioxyde de soufre ($C_a$) dans le bécher :")
        val_q6 = st.session_state.get("col_g_quiz_ox_q6_tab2", "Choisir...")
        try:
            idx_q6 = opts_q6.index(val_q6)
        except ValueError:
            idx_q6 = 0
            st.session_state["col_g_quiz_ox_q6_tab2"] = "Choisir..."
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, index=idx_q6, key="col_g_quiz_ox_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_so2:
        st.markdown("##### Synthèse de cours (Texte à trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        # --- TROU 1 ---
        opts_t1 = ["Choisir...", "Burette", "Éprouvette graduée", "Pipette jaugée"]
        st.write("1. La verrerie graduée permettant l'ajout de la solution titrante de diode est la")
        val_t1 = st.session_state.get("ox_t1_tab2", "Choisir...")
        try:
            idx_t1 = opts_t1.index(val_t1)
        except ValueError:
            idx_t1 = 0
            st.session_state["ox_t1_tab2"] = "Choisir..."
        dict_trous["t1"] = st.selectbox("", opts_t1, index=idx_t1, key="ox_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- TROU 2 ---
        opts_t2 = ["Choisir...", "Pipette jaugée", "Éprouvette graduée", "Fiole jaugée"]
        st.write("2. Pour prélever les 20 mL de vin blanc de manière précise, on utilise une")
        val_t2 = st.session_state.get("ox_t2_tab2", "Choisir...")
        try:
            idx_t2 = opts_t2.index(val_t2)
        except ValueError:
            idx_t2 = 0
            st.session_state["ox_t2_tab2"] = "Choisir..."
        dict_trous["t2"] = st.selectbox("", opts_t2, index=idx_t2, key="ox_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- TROU 3 ---
        opts_t3 = ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"]
        st.write("3. Pour convertir le volume équivalent expérimental de mL en Litres, on doit le")
        val_t3 = st.session_state.get("ox_t3_tab2", "Choisir...")
        try:
            idx_t3 = opts_t3.index(val_t3)
        except ValueError:
            idx_t3 = 0
            st.session_state["ox_t3_tab2"] = "Choisir..."
        dict_trous["t3"] = st.selectbox("", opts_t3, index=idx_t3, key="ox_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- TROU 4 ---
        opts_t4 = ["Choisir...", "stoechiometriques", "inverses", "maximales"]
        st.write("4. Au point équivalent, les molécules de SO2 et de diode ont réagi dans des proportions")
        val_t4 = st.session_state.get("ox_t4_tab2", "Choisir...")
        try:
            idx_t4 = opts_t4.index(val_t4)
        except ValueError:
            idx_t4 = 0
            st.session_state["ox_t4_tab2"] = "Choisir..."
        dict_trous["t4"] = st.selectbox("", opts_t4, index=idx_t4, key="ox_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- TROU 5 ---
        opts_t5 = ["Choisir...", "bleu-violet foncé", "rouge brique", "rose violacé"]
        st.write("5. Lors d'un suivi par la méthode de Ripper, l'équivalence correspond au virage persistant vers le")
        val_t5 = st.session_state.get("ox_t5_tab2", "Choisir...")
        try:
            idx_t5 = opts_t5.index(val_t5)
        except ValueError:
            idx_t5 = 0
            st.session_state["ox_t5_tab2"] = "Choisir..."
        dict_trous["t5"] = st.selectbox("", opts_t5, index=idx_t5, key="ox_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous


def afficher_questions_so2_eau1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_so2" not in st.session_state:
        base_quiz1_so2 = [
            {"id": "q1_1", "q": "Le dosage colorimétrique du dioxyde de soufre (SO2) par le diode (I2) est un titrage par :", "type": "menu", "options": ["oxydoréduction", "complexation", "précipitation"], "rep": "oxydoréduction"},
            {"id": "q1_2", "q": "Quelle est la formule chimique du dioxyde de soufre analysé dans le vin blanc ?", "type": "menu", "options": ["SO2", "H2SO4", "SO42-"], "rep": "SO2"},
            {"id": "q1_3", "q": "Quel indicateur de fin de réaction utilise-t-on pour repérer l'équivalence (méthode Ripper) ?", "type": "menu", "options": ["empois d'amidon", "NET", "chromate de potassium"], "rep": "empois d'amidon"},
            {"id": "q1_4", "q": "D'après la classification, quelle est la masse molaire de la molécule de dioxyde de soufre (SO2) en g/mol ?", "type": "menu", "options": ["64,1", "32,1", "48,0"], "rep": "64,1"},
            {"id": "q1_5", "q": "Quelle est la couleur initiale du mélange vin + indicateur avant le premier ajout de diode ?", "type": "menu", "options": ["jaune pâle", "bleu-violet", "rose"], "rep": "jaune pâle"},
            {"id": "q1_6", "q": "Au point équivalent, l'excès de quelle espèce chimique provoque la coloration de la solution ?", "type": "menu", "options": ["diode (I2)", "ions iodure (I-)", "ions sulfate (SO42-)"], "rep": "diode (I2)"},
            {"id": "q1_7", "q": "Quelle teinte persistante et intense caractérise la fin du dosage de la méthode Ripper ?", "type": "menu", "options": ["bleu-violet foncé", "rouge brique", "rose pâle"], "rep": "bleu-violet foncé"},
            {"id": "q1_8", "q": "Quelle est la formule brute de la molécule titrante colorant la burette graduée ?", "type": "menu", "options": ["I2", "KI", "AgNO3"], "rep": "I2"},
            {"id": "q1_9", "q": "Le rapport stœchiométrique de la réaction d'oxydoréduction entre I2 et SO2 est de :", "type": "menu", "options": ["1 pour 1", "1 pour 2", "2 pour 1"], "rep": "1 pour 1"},
            {"id": "q1_10", "q": "Quelle est la concentration molaire standard C0 de la solution titrante de diode employée ?", "type": "menu", "options": ["0,005 mol/L", "0,010 mol/L", "0,100 mol/L"], "rep": "0,005 mol/L"}
        ]
        copie_base = list(base_quiz1_so2)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_so2 = copie_base

    col_double_quiz_so2, col_double_trous_so2 = st.columns(2)

    with col_double_quiz_so2:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_so2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"th_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_so2_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = opts_copie
            
            opts_affichees = ["Choisir..."] + st.session_state[cle_shuff_opts]
            val_p = st.session_state.get(cle_select, "Choisir...")
            
            try:
                sel_idx = opts_affichees.index(val_p)
            except ValueError:
                sel_idx = 0
            
            dict_reponses_quiz[q_data["id"]] = st.selectbox(
                "", opts_affichees, index=sel_idx, key=cle_select,
                disabled=verrouille, label_visibility="collapsed"
            )

    with col_double_trous_so2:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. L'additif dosé dans cet atelier pour ses effets antioxydants dans le vin est le dioxyde de")
        val_t1 = st.session_state.get("th_t1_tab1", "Choisir...")
        opts_t1 = ["Choisir...", "soufre", "carbone", "chlore"]
        idx_t1 = opts_t1.index(val_t1) if val_t1 in opts_t1 else 0
        with c2: dict_trous["t1"] = st.selectbox("", opts_t1, index=idx_t1, key="th_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La solution titrante placée dans la burette apporte des molécules de formule brute")
        val_t2 = st.session_state.get("th_t2_tab1", "Choisir...")
        opts_t2 = ["Choisir...", "I2", "SO2", "Ag+"]
        idx_t2 = opts_t2.index(val_t2) if val_t2 in opts_t2 else 0
        with c4: dict_trous["t2"] = st.selectbox("", opts_t2, index=idx_t2, key="th_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La réaction d'échange d'électrons mise en jeu lors de ce titrage Ripper est une")
        val_t3 = st.session_state.get("th_t3_tab1", "Choisir...")
        opts_t3 = ["Choisir...", "oxydoréduction", "précipitation", "complexation"]
        idx_t3 = opts_t3.index(val_t3) if val_t3 in opts_t3 else 0
        with c6: dict_trous["t3"] = st.selectbox("", opts_t3, index=idx_t3, key="th_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La masse molaire moléculaire du dioxyde de soufre (SO2) calculée vaut environ")
        val_t4 = st.session_state.get("th_t4_tab1", "Choisir...")
        opts_t4 = ["Choisir...", "64,1 g/mol", "32,1 g/mol", "44,0 g/mol"]
        idx_t4 = opts_t4.index(val_t4) if val_t4 in opts_t4 else 0
        with c8: dict_trous["t4"] = st.selectbox("", opts_t4, index=idx_t4, key="th_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. L'indicateur spécifique ajouté dans le bécher pour déceler le point d'équivalence est l'")
        val_t5 = st.session_state.get("th_t5_tab1", "Choisir...")
        opts_t5 = ["Choisir...", "empois d'amidon", "NET", "phénolphtaléine"]
        idx_t5 = opts_t5.index(val_t5) if val_t5 in opts_t5 else 0
        with c10: dict_trous["t5"] = st.selectbox("", opts_t5, index=idx_t5, key="th_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Tant que le dioxyde de soufre est en excès, les molécules de diode versées se transforment en ions")
        val_t6 = st.session_state.get("th_t6_tab1", "Choisir...")
        opts_t6 = ["Choisir...", "iodure", "sulfate", "argent"]
        idx_t6 = opts_t6.index(val_t6) if val_t6 in opts_t6 else 0
        with c12: dict_trous["t6"] = st.selectbox("", opts_t6, index=idx_t6, key="th_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Au point d'équivalence stœchiométrique, la couleur de la solution vire brutalement vers le")
        val_t7 = st.session_state.get("th_t7_tab1", "Choisir...")
        opts_t7 = ["Choisir...", "bleu-violet foncé", "rouge brique", "rose pâle"]
        idx_t7 = opts_t7.index(val_t7) if val_t7 in opts_t7 else 0
        with c14: dict_trous["t7"] = st.selectbox("", opts_t7, index=idx_t7, key="th_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le virage s'explique par la formation d'un complexe coloré dès que l'espèce titrante est en")
        val_t8 = st.session_state.get("th_t8_tab1", "Choisir...")
        opts_t8 = ["Choisir...", "excès", "défaut", "équilibre"]
        idx_t8 = opts_t8.index(val_t8) if val_t8 in opts_t8 else 0
        with c16: dict_trous["t8"] = st.selectbox("", opts_t8, index=idx_t8, key="th_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La concentration molaire C0 de la solution de diode de la burette est fixée à")
        val_t9 = st.session_state.get("th_t9_tab1", "Choisir...")
        opts_t9 = ["Choisir...", "0,005 mol/L", "0,010 mol/L", "0,100 mol/L"]
        idx_t9 = opts_t9.index(val_t9) if val_t9 in opts_t9 else 0
        with c18: dict_trous["t9"] = st.selectbox("", opts_t9, index=idx_t9, key="th_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Les limites réglementaires européennes expriment généralement la teneur en SO2 en")
        val_t10 = st.session_state.get("th_t10_tab1", "Choisir...")
        opts_t10 = ["Choisir...", "mg/L", "g/L", "mol/L"]
        idx_t10 = opts_t10.index(val_t10) if val_t10 in opts_t10 else 0
        with c20: dict_trous["t10"] = st.selectbox("", opts_t10, index=idx_t10, key="th_t10_tab1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous




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
    st.header("Atelier 1 : Généralités sur le dioxyde de soufre dans le vin")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    col_gauche, col_droite = st.columns([1, 1])
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    
    with col_gauche:
        st.subheader("Données et Principe de la méthode Ripper")
        st.info(
            "Le dioxyde de soufre (SO2) est un additif utilisé en œnologie pour ses propriétés antioxydantes "
            "et antiseptiques. La méthode de Ripper permet son dosage direct par oxydoréduction. "
            "La solution titrante employée est une solution de diode (I2) de concentration C0 = 0,005 mol/L. "
            "Le diode réagit mole à mole avec le dioxyde de soufre pour former des ions iodure incolores et des ions sulfate. "
            "L'indicateur coloré introduit est l'empois d'amidon (ou thiodène). "
            "Tant que le dioxyde de soufre est présent, le diode versé est instantanément consommé et la solution "
            "reste initialement incolore (ou garde la teinte jaune pâle du vin). "
            "À l'équivalence, la première goutte de diode en excès réagit avec l'empois d'amidon pour former "
            "un complexe d'une coloration bleu-violet foncé intense et persistante."
        )


        fig_ox, ax_ox = plt.subplots(figsize=(6, 5.5), facecolor="white")
        ax_ox.set_facecolor("white")

        ax_ox.set_ylim(550, 0)
        ax_ox.set_xlim(0, 700)

        # 1. Le bouchon de liège et col de la bouteille de vin blanc
        ax_ox.add_patch(patches.Rectangle((220, 10), 80, 50, facecolor="#78350f", edgecolor="#451a03", linewidth=1.5, zorder=3))
        ax_ox.plot([220, 300], [35, 35], color="#451a03", linewidth=1.5, zorder=4)

        # 2. Le col de la bouteille
        ax_ox.add_patch(patches.Rectangle((225, 60), 70, 70, facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.5, zorder=2))

        # 3. Les épaules de la bouteille de vin
        ax_ox.plot([225, 160], [130, 160], color="#cbd5e1", linewidth=1.5, zorder=3)
        ax_ox.plot([295, 360], [130, 160], color="#cbd5e1", linewidth=1.5, zorder=3)

        # 4. Le corps de la bouteille en verre blanc
        ax_ox.add_patch(patches.Rectangle((160, 160), 200, 280, facecolor="#ffffff", edgecolor="none", zorder=2))
        ax_ox.add_patch(patches.Wedge((260, 440), 100, 0, 180, facecolor="#ffffff", edgecolor="none", zorder=2))

        ax_ox.plot([160, 160], [160, 440], color="#cbd5e1", linewidth=1.5, zorder=2)
        ax_ox.plot([360, 360], [160, 440], color="#cbd5e1", linewidth=1.5, zorder=2)

        # 5. L'étiquette de style château œnologique (Bordeaux / Lie de vin)
        ax_ox.add_patch(patches.Rectangle((161, 230), 198, 230, facecolor="#7f1d1d", edgecolor="none", zorder=3))

        vague_x = np.linspace(161, 359, 50)
        vague_y = 230 + 12 * np.sin((vague_x - 161) / 25)
        coords_vague = [[161, 230], [359, 230]] + [[x, y] for x, y in zip(vague_x, vague_y)]
        ax_ox.add_patch(patches.Polygon(coords_vague, facecolor="#ffffff", edgecolor="none", zorder=3))

        # 6. TEXTES DE L'ÉTIQUETTE DU VIN BLANC ACCORDÉS AU TP RIPPER
        ax_ox.text(260, 165, "Analyse Vinicole", fontname="Arial", fontsize=9, weight="bold", color="#7f1d1d", ha="center", va="center", zorder=4)
        ax_ox.text(260, 195, "Dioxyde de soufre", fontname="Arial", fontsize=8, weight="bold", color="#0f172a", ha="center", va="center", zorder=4)
        ax_ox.text(260, 222, "ŒNOLOGIE", fontname="Arial", fontsize=10, weight="bold", color="#7f1d1d", ha="center", va="center", zorder=4)

        ax_ox.text(165, 285, "• Contient des sulfites", fontname="Arial", fontsize=7, weight="bold", color="#ffffff", ha="left", va="center", zorder=4)
        ax_ox.text(165, 310, "• Conservateur du vin", fontname="Arial", fontsize=7, weight="bold", color="#ffffff", ha="left", va="center", zorder=4)
        ax_ox.text(165, 425, "750 mL", fontname="Arial", fontsize=11, weight="bold", color="#ffffff", ha="left", va="center", zorder=4)

        # 7. Sceau officiel du laboratoire

        ax_ox.add_patch(patches.Ellipse((320, 390), 20, 20, facecolor="#b45309", edgecolor="none", zorder=4))
        coords_logo_int = np.array([[315, 395], [325, 395], [320, 385]])
        ax_ox.add_patch(patches.Polygon(coords_logo_int, facecolor="#ffffff", edgecolor="none", zorder=5))
        
        ax_ox.text(315, 412, "CONTROLE", fontname="Arial", fontsize=5, color="#ffffff", ha="center", va="center", zorder=4)
        ax_ox.text(320, 425, "QUALITE", fontname="Arial", fontsize=6, weight="bold", color="#0f172a", ha="center", va="center", zorder=4)

        ax_ox.axis("off")
        st.pyplot(fig_ox)
        st.divider()



    with col_droite:

        st.subheader("Données et Légendes Atomiques du Titrage")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Iode (I)**\n\nSphère violette\nM(I) = 127 g/mol")
        with col_leg2: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16,0 g/mol")
        with col_leg3: st.caption("**Soufre (S)**\n\nSphère jaune\nM(S) = 32 g/mol")
            
        st.divider()


        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # --- 1. Représentation de la molécule de diode I2 ---
        i1_pos = np.array([2.0, 3.5])
        i2_pos = np.array([3.4, 3.5])

        # --- 2. Représentation de la molécule de dioxyde de soufre SO2 ---
        s_pos = np.array([2.7, 1.5])
        o1_pos = np.array([1.7, 0.9])
        o2_pos = np.array([3.7, 0.9])

        def tracer_liaison_ox(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.05
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Tracé des liaisons de session
        tracer_liaison_ox(i1_pos, i2_pos, double=False)
        tracer_liaison_ox(s_pos, o1_pos, double=True)
        tracer_liaison_ox(s_pos, o2_pos, double=True)

        def tracer_atome_ox(p, symbole):
            if symbole == 'I': couleur, text_color = "#9333ea", "white"
            elif symbole == 'S': couleur, text_color = "#facc15", "black"
            elif symbole == 'O': couleur, text_color = "#ef4444", "white"
            else: couleur, text_color = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.24, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=text_color, weight="bold", fontsize=9, ha="center", va="center", zorder=3)

        # Rendu des structures moléculaires
        tracer_atome_ox(i1_pos, 'I')
        tracer_atome_ox(i2_pos, 'I')
        ax_mol.text(2.7, 4.1, "Molécule d'Iode Titrante I₂", fontsize=9, style="italic", ha="center")

        tracer_atome_ox(s_pos, 'S')
        tracer_atome_ox(o1_pos, 'O')
        tracer_atome_ox(o2_pos, 'O')
        ax_mol.text(2.7, 0.3, "Dioxyde de Soufre Dosé SO₂", fontsize=9, style="italic", ha="center")

        ax_mol.set_xlim(0.8, 4.6)
        ax_mol.set_ylim(0.0, 4.5)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        
        st.subheader("Réglementation et Étiquetage Œnologique")

        fig_box, ax_box = plt.subplots(figsize=(7, 5.5), facecolor="white")
        ax_box.set_facecolor("white")
        ax_box.set_ylim(500, 0)
        ax_box.set_xlim(0, 700)

        ax_box.add_patch(patches.Rectangle((150, 20), 400, 460, facecolor="white", edgecolor="#7f1d1d", linewidth=4, zorder=1))
        ax_box.add_patch(patches.Rectangle((152, 22), 396, 45, facecolor="#7f1d1d", edgecolor="none", zorder=2))
        ax_box.text(170, 45, "RAPPORT D'ANALYSE ŒNOLOGIQUE", fontname="Arial", fontsize=10, weight="bold", color="white", ha="left", va="center", zorder=3)
        ax_box.text(525, 45, "mg/L", fontname="Arial", fontsize=10, style="italic", color="white", ha="right", va="center", zorder=3)

        elements_analyse = [
            ("DIOXYDE DE SOUFRE (SO2)", "140", 120),
            ("ACIDITÉ TOTALE", "3.8", 170),
            ("ALCOOL ACQUIS", "12.5 %", 220),
            ("SUCRES RÉSIDUELS", "2.0", 270),
            ("PH DU VIN", "3.3", 320)
        ]

        for nom, val, y_pos in elements_analyse:
            ax_box.text(170, y_pos, nom, fontname="Arial", fontsize=11, weight="bold", color="#7f1d1d", ha="left", va="center", zorder=3)
            ax_box.text(530, y_pos, val, fontname="Arial", fontsize=12, weight="bold", color="#7f1d1d", ha="right", va="center", zorder=3)
            points_x = np.linspace(340, 480, 15)
            points_y = np.full_like(points_x, y_pos + 2)
            ax_box.scatter(points_x, points_y, s=2, color="#94a3b8", zorder=3)

        ax_box.add_patch(patches.Rectangle((152, 440), 396, 38, facecolor="#7f1d1d", edgecolor="none", zorder=2))
        ax_box.text(350, 458, "Conforme aux limites de l'Union Européenne", fontname="Arial", fontsize=9, style="italic", color="white", ha="center", va="center", zorder=3)
        ax_box.axis("off")
        st.pyplot(fig_box)
        st.divider()

    verrou_so2_1_officiel = st.session_state.get("vin_verrouille_tab1", False)

    # Appel direct de la fonction pour afficher le questionnaire complet sur le SO2
    res_quiz, res_trous = afficher_questions_so2_eau1_dynamiques(verrouille=verrou_so2_1_officiel)

    st.write("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
    case_certif_cl1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_th1_final_net", 
        disabled=verrou_so2_1_officiel
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_th1_official_net", use_container_width=True, disabled=verrou_so2_1_officiel):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_cl1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz de gauche mélangé (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_so2" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_so2:
                    reponse_eleve = st.session_state.get(f"th_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 cases)
            score_t1 = sum([
                st.session_state.get("th_t1_tab1") == "soufre",
                st.session_state.get("th_t2_tab1") == "I2",
                st.session_state.get("th_t3_tab1") == "oxydoréduction",
                st.session_state.get("th_t4_tab1") == "64,1 g/mol",
                st.session_state.get("th_t5_tab1") == "empois d'amidon",
                st.session_state.get("th_t6_tab1") == "iodure",
                st.session_state.get("th_t7_tab1") == "bleu-violet foncé",
                st.session_state.get("th_t8_tab1") == "excès",
                st.session_state.get("th_t9_tab1") == "0,005 mol/L",
                st.session_state.get("th_t10_tab1") == "mg/L"
            ])

            # Sauvegarde centrale des notes et enregistrement du verrou de l'Atelier 1
            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- SCELLÉ ET COMPILATION DU RAPPORT HTML POUR LE DIOXYDE DE SOUFRE ---
    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
        timestamp_cl1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        html_export_cl1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dioxyde de soufre 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Généralités sur le dioxyde de soufre (Méthode de Ripper)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_cl1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de Nomenclature Redox : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse de cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_so2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_so2, 1):
                saisie = st.session_state.get(f"th_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_cl1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cl1 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous1 = [
            "1. L'additif dosé dans cet atelier pour ses effets antioxydants dans le vin est le dioxyde de",
            "2. La solution titrante placée dans la burette apporte des molécules de formule brute",
            "3. La réaction d'échange d'électrons mise en jeu lors de ce titrage Ripper est une",
            "4. La masse molaire moléculaire du dioxyde de soufre (SO2) calculée vaut environ",
            "5. L'indicateur spécifique ajouté dans le bécher pour déceler le point d'équivalence est l'",
            "6. Tant que le dioxyde de soufre est en excès, les molécules de diode versées se transforment en ions",
            "7. Au point d'équivalence stœchiométrique, la couleur de la solution vire brutalement vers le",
            "8. Le virage s'explique par la formation d'un complexe coloré dès que l'espèce titrante est en",
            "9. La concentration molaire C0 de la solution de diode de la burette est fixée à",
            "10. Les limites réglementaires européennes expriment généralement la teneur en SO2 en"
        ]
        attendus_trous1 = ["soufre", "I2", "oxydoréduction", "64 g/mol", "empois d'amidon", "iodure", "bleu-violet foncé", "excès", "0,005 mol/L", "mg/L"]

        for i in range(1, 11):
            saisie = st.session_state.get(f"th_t{i}_tab1", "Choisir...")
            attendu = attendus_trous1[i-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_cl1 += f"<tr><td>{i}</td><td>{phrases_trous1[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cl1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse de l'Atelier 1 généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Rapport_Atelier1_SO2_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.success(f"ATELIER SO2 1 SCELLÉ | Note de session : {tot_s:.1f} / 20")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_cl1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )
        

with tab2:
    st.header("Atelier 2 : Dosage colorimétrique des sulfites dans le vin")
    st.caption("Simulation interactive de la méthode Ripper avec virage au bleu-violet foncé")

    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "v_verse_ox" not in st.session_state: st.session_state.v_verse_ox = 0.0
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    
    if "facteur_titrage_ox" not in st.session_state:
        import random
        st.session_state.facteur_titrage_ox = random.uniform(0.95, 1.05)
        
    coeff_alea = st.session_state.facteur_titrage_ox

    liste_bouteilles = list(st.session_state["eau"].keys())
    bouteille_selectionnee = st.selectbox("Sélectionnez le vin blanc à analyser :", options=liste_bouteilles, disabled=st.session_state.vin_verrouille_tab2)

    v_max_ml = 25.0
    V_ini = 20.0  # Prise d'essai standard de vin blanc (20.0 mL)
    M_so2 = 64  # Masse molaire du dioxyde de soufre (g/mol)


    with st.container(border=True):
        st.subheader("Contrôle de la burette graduée")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            # FIXATION STRICTE : Force la concentration réglementaire de la méthode Ripper
            C_base = st.number_input("Concentration de la solution de diode C0 (mol/L) :", min_value=0.001, max_value=0.100, value=0.005, format="%.3f", disabled=True, key="c_titrant_diode_officielle_net")
        with col_p2:
            st.session_state.pas_ml = st.slider("Pas de versement de la molette (mL) :", min_value=0.1, max_value=2.0, value=0.5, step=0.1, disabled=st.session_state.get("vin_verrouille_tab2", False))

        # --- CALCUL TECHNIQUE RIGOUREUX DE L'ÉQUIVALENCE RIPPER ---
        info_bouteille = st.session_state["eau"][bouteille_selectionnee]
        teneur_so2_nominale = info_bouteille["SO2"]
        
        if "facteur_titrage_ox" not in st.session_state:
            import random
            st.session_state.facteur_titrage_ox = random.uniform(0.95, 1.05)
            
        coeff_alea = st.session_state.facteur_titrage_ox

        # Déduction de la concentration réelle simulée en mol/L
        c_so2_simulee = ((teneur_so2_nominale / 1000.0) / M_so2) * coeff_alea
        st.session_state.masse_reelle_g = c_so2_simulee * (V_ini / 1000.0) * M_so2
        masse_affichee_mg = st.session_state.masse_reelle_g * 1000.0

        # Formule de Ripper : n(I2) = n(SO2) => C0 * VE = C_so2 * Va => VE = (C_so2 * Va) / C0
        v_eq_theorique_calcul = (c_so2_simulee * V_ini / C_base) 

        st.session_state["th_vrai_veq_calc"] = round(float(v_eq_theorique_calcul), 2)
        st.session_state["input_at2_ve_lu_eleve"] = round(float(v_eq_theorique_calcul), 2)

        st.info(
            f"Composé dosé : Dioxyde de soufre (SO2) | Prise d'essai: {V_ini:.1f} mL | "
            f"Masse : {masse_affichee_mg:.2f} mg | "
            f"Indicateur : Empois d'amidon"
        )
        st.divider()

    v_eq_visuel = st.session_state.th_vrai_veq_calc
    
    # --- CANVAS HTML ANIMATION METHODE RIPPER (VIRAGE BLEU-VIOLET) ---
    html_paillasse = f"""
    <div style="text-align: center; font-family: sans-serif;">
        <div style="margin-bottom: 12px;">
            <button id="btn-start" style="padding: 6px 16px; background: #22c55e; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px;">Démarrer</button>
            <button id="btn-pause" style="padding: 6px 16px; background: #eab308; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px;">Pause</button>
            <button id="btn-clear" style="padding: 6px 16px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Effacer</button>
        </div>
        <canvas id="paillasse_canvas" width="260" height="360" style="background: white; border: 1px solid #cbd5e1; border-radius: 8px;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('paillasse_canvas');
        const ctx = canvas.getContext('2d');
        let vVerse = {st.session_state.v_verse_ox};
        const vMax = {v_max_ml};
        const vEq = {v_eq_visuel};
        const pas = {st.session_state.pas_ml};
        let isRunning = false;
        let tick = 0;

        document.getElementById('btn-start').addEventListener('click', () => {{ isRunning = true; }});
        document.getElementById('btn-pause').addEventListener('click', () => {{ isRunning = false; }});
        document.getElementById('btn-clear').addEventListener('click', () => {{ isRunning = false; vVerse = 0; tick = 0; }});

        function drawScene() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            tick++;

            if (isRunning && vVerse < vMax) {{ vVerse = Math.min(vMax, vVerse + pas); }}
            else if (vVerse >= vMax) {{ isRunning = false; }}

            ctx.fillStyle = '#7f8c8d'; ctx.fillRect(40, 30, 10, 300);
            ctx.strokeStyle = '#34495e'; ctx.lineWidth = 1.5; ctx.strokeRect(140, 40, 20, 160);
            
            let hauteurBurette = 156 * (1 - (vVerse / vMax));
            ctx.fillStyle = 'rgba(180, 83, 9, 0.4)'; ctx.fillRect(141.5, 41.5 + (156 - hauteurBurette), 17, hauteurBurette);

            ctx.fillStyle = '#b45309'; ctx.font = 'bold 11px sans-serif';
            ctx.fillText(vVerse.toFixed(1) + ' mL', 165, 45 + (156 - hauteurBurette));

            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 215 : 235;
                ctx.fillStyle = '#b45309'; ctx.beginPath(); ctx.arc(150, yGoutte, 2, 0, 2 * Math.PI); ctx.fill();
            }}

            ctx.strokeStyle = '#34495e'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(105, 220); ctx.lineTo(105, 290); ctx.lineTo(205, 290); ctx.lineTo(205, 220); ctx.stroke();

            // Teinte initiale jaune pâle du vin blanc -> Virage bleu-violet persistant
            let couleurSol = "#fef08a"; 
            let nomTeinte = "Jaune pâle translucide (Vin + Amidon)";
            
            if (vVerse > 0 && vVerse < vEq) {{
                couleurSol = "#fef08a"; 
                nomTeinte = "Jaune pâle (I2 consommé instantanément)";
            }} else if (Math.abs(vVerse - vEq) <= 0.4) {{
                couleurSol = "#c084fc"; 
                nomTeinte = "Teinte sensible violette (Équivalence)";
            }} else if (vVerse > vEq) {{
                couleurSol = "#1e1b4b"; // Complexe diode-amidon bleu-violet très sombre
                nomTeinte = "Bleu-Violet foncé persistant (Diode en excès)";
            }}

            let hauteurLiq = 15 + (40 * (vVerse / vMax));
            ctx.fillStyle = couleurSol; ctx.fillRect(106, 289 - hauteurLiq, 98, hauteurLiq);

            ctx.fillStyle = '#34495e'; ctx.font = 'bold 11px sans-serif';
            ctx.fillText('Aspect : ' + nomTeinte, 40, 335);

            setTimeout(() => {{ requestAnimationFrame(drawScene); }}, 500);
        }}
        drawScene();
    </script>
    """
    components.html(html_paillasse, height=365)

    if st.button("ENREGISTRER LE VOLUME ÉQUIVALENT RELEVÉ", key="btn_sync_diode_2"):
        st.session_state.v_verse_ox = float(v_eq_visuel)
        st.success(f"Volume équivalent synchronisé avec succès : VE = {v_eq_visuel:.2f} mL")
        st.session_state.vin_verrouille_tab2 = True

    verrou_so2_2_officiel = st.session_state.get("vin_verrouille_tab2", False)
    res_q2, res_t12 = generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_so2_2_officiel)
    st.write("---")
    st.subheader("Validation et scellé de l'Atelier 2")
        
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_cl2 = st.checkbox(
        "Je certifie avoir complété l'intégralité des questionnaires de l'Atelier 2.", 
        key="check_certif_cl2_officiel", 
        disabled=verrou_so2_2_officiel
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_cl2_unifie_final_secure_813", use_container_width=True, disabled=verrou_so2_2_officiel):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_cl2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            v_acide_dose = 20.0
            v_eq_theorique = st.session_state.get("th_vrai_veq_calc", 12.0)
            C_base = 0.005
            
            moles_diode_equiv = (C_base * v_eq_theorique) / 1000.0
            concentration_so2_attendue = (C_base * v_eq_theorique) / v_acide_dose

            # Correction automatique du Quiz Iodométrique (sur 10 points)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_ox_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_ox_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_ox_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_ox_q4_tab2") == "n(I2) = n(SO2)",
                st.session_state.get("col_g_quiz_ox_q5_tab2") == f"{moles_diode_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_ox_q6_tab2") == f"{concentration_so2_attendue:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # Correction automatique de la Synthèse de cours Méthode Ripper (sur 10 points)
            score_t2 = sum([
                st.session_state.get("ox_t1_tab2") == "Burette",
                st.session_state.get("ox_t2_tab2") == "Pipette jaugée",
                st.session_state.get("ox_t3_tab2") == "diviser par 1000",
                st.session_state.get("ox_t4_tab2") == "stoechiometriques",
                st.session_state.get("ox_t5_tab2") == "bleu-violet foncé"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()
            
    # --- COMPILATION DU RAPPORT HTML PROPRE ET SYNCHRONISÉ POUR LE S02 ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        v_acide_dose = 20.0
        v_eq_theorique = st.session_state.get("th_vrai_veq_calc", 12.0)
        C_base = 0.01
        moles_diode_equiv = (C_base * v_eq_theorique) / 1000.0

        from datetime import datetime, timedelta
        timestamp_th2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_th2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dioxyde de soufre 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 2 : Exploitation du dosage du dioxyde de soufre dans un vin blanc</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_th2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de suivi de titrage : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Finale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">Solution titrante : Diode (I2) | Concentration : 0.005 mol/L | 
            Composé dosé : Dioxyde de soufre (SO2) | Prise d'essai Va : {v_acide_dose:.1f} mL | 
            Indicateur : Empois d'amidon</div>          
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question de paillasse demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Concentration molaire de la solution titrante de I2 (C0)</td><td>{st.session_state.get("col_g_quiz_ox_q1_tab2", "Choisir...")}</td><td>{C_base:.3f} mol/L</td></tr>
                    <tr><td>2</td><td>Volume de vin blanc introduit dans le bécher (Va)</td><td>{st.session_state.get("col_g_quiz_ox_q2_tab2", "Choisir...")}</td><td>{v_acide_dose:.1f} mL</td></tr>
                    <tr><td>3</td><td>Volume equivalent exact (VE) de solution de diode verse</td><td>{st.session_state.get("col_g_quiz_ox_q3_tab2", "Choisir...")}</td><td>{v_eq_theorique:.1f} mL</td></tr>
                    <tr><td>4</td><td>Relation stoechiometrique a l'equivalence</td><td>{st.session_state.get("col_g_quiz_ox_q4_tab2", "Choisir...")}</td><td>n(I2) = n(SO2)</td></tr>
                    <tr><td>5</td><td>Quantite de matiere de I2 apportee a l'equivalence</td><td>{st.session_state.get("col_g_quiz_ox_q5_tab2", "Choisir...")}</td><td>{moles_diode_equiv:.5f} mol</td></tr>
                    <tr><td>6</td><td>Concentration molaire en SO2 deduite (Ca)</td><td>{st.session_state.get("col_g_quiz_ox_q6_tab2", "Choisir...")}</td><td>{((C_base * v_eq_theorique) / v_acide_dose):.4f} mol/L</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Concept du texte a trous</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Verrerie graduee pour la solution titrante</td><td>{st.session_state.get("ox_t1_tab2", "Choisir...")}</td><td>Burette</td></tr>
                    <tr><td>2</td><td>Verrerie de precision pour prelever le vin</td><td>{st.session_state.get("ox_t2_tab2", "Choisir...")}</td><td>Pipette jaugée</td></tr>
                    <tr><td>3</td><td>Conversion du volume equivalent en Litres</td><td>{st.session_state.get("ox_t3_tab2", "Choisir...")}</td><td>diviser par 1000</td></tr>
                    <tr><td>4</td><td>Proportions des reactifs a l'equivalence</td><td>{st.session_state.get("ox_t4_tab2", "Choisir...")}</td><td>stoechiometriques</td></tr>
                    <tr><td>5</td><td>Teinte persistante de la fin du dosage de Ripper</td><td>{st.session_state.get("ox_t5_tab2", "Choisir...")}</td><td>bleu-violet foncé</td></tr>
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de dosage de Ripper de l'Atelier 2 généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Atelier2_SO2_Vin_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_th2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )        
            

with tab3:
    st.header("Calcul théorique et vérification de l'étiquette")
    st.caption("Détermination de la concentration en dioxyde de soufre d'un vin")

    if "vin_verrouille_tab3" not in st.session_state: 
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.get("vin_verrouille_tab3", False)

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = 0.005
    v_eq_session = st.session_state.get("th_vrai_veq_calc", 12.0)
    v_titre_session = 20.0 
    M_so2 = 64

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les résultats de votre dosage iodométrique
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On prélève un volume Va = 20,0 mL de vin blanc à l'aide d'une pipette jaugée que l'on titre par la solution de diode.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq relevé = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Concentration I2 C_0 = {c_base_session:.3f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Volume vin dosé V_a = {v_titre_session:.1f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M(SO2) = {M_so2:.2f} g/mol</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # --- APPEL SÉCURISÉ DU QUESTIONNAIRE DE SAISIE DU SO2 ---
    try:
        dict_saisies_eleve = afficher_questions_so2_vin_commercial(verrouille=verrou_at3)
    except NameError:
        dict_saisies_eleve = {}

    # --- CALCULS EXPÉRIMENTAUX DE RÉFÉRENCE DE LA SESSION ALÉATOIRE ---
    att_v_eq_l = v_eq_session / 1000.0
    att_n_argent = c_base_session * att_v_eq_l
    att_n_chlorure = att_n_argent
    att_c_molaire = att_n_chlorure / (v_titre_session / 1000.0)
    att_t_g = att_c_molaire * M_so2
    att_t_mg = att_t_g * 1000.0

    # --- CASE À COCHER DE CERTIFICATION ---
    case_certif_th3 = st.checkbox("Je certifie avoir complété l'intégralité des calculs d'exploitation de l'Atelier 3.", key="check_certif_cl3_final", disabled=verrou_at3)
    
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_cl3_final_secure", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_th3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_at3_total = 0.0
            import numpy as np
            
            if np.isclose(st.session_state.get("at3_v_eq_l_cl", 0.0), att_v_eq_l, rtol=0.02): score_at3_total += 3.5
            if np.isclose(st.session_state.get("at3_n_argent_cl", 0.0), att_n_argent, rtol=0.02): score_at3_total += 3.5
            if np.isclose(st.session_state.get("at3_n_chlorure_becher", 0.0), att_n_chlorure, rtol=0.02): score_at3_total += 3.5
            if np.isclose(st.session_state.get("at3_c_molaire_cl", 0.0), att_c_molaire, rtol=0.02): score_at3_total += 3.5
            if np.isclose(st.session_state.get("at3_t_massique_g", 0.0), att_t_g, rtol=0.02): score_at3_total += 3.0
            if np.isclose(st.session_state.get("at3_t_massique_mg", 0.0), att_t_mg, rtol=0.02): score_at3_total += 3.0

            st.session_state["score_final_vin3"] = round(min(20.0, score_at3_total), 1)
            st.session_state["vin_verrouille_tab3"] = True
            st.rerun()

    # --- CONTEXTE DU BILAN SCELLÉ ET RAPPORT HTML IODOMÉTRIQUE RIPPER ---
    if st.session_state.get("vin_verrouille_tab3", False):
        tot_s3 = st.session_state.get("score_final_vin3", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import datetime, timedelta
        timestamp_cl3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")
        
        html_export_cl3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dioxyde de Soufre 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Exploitation quantitative et teneur en dioxyde de soufre (Méthode de Ripper)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_cl3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue aux calculs sur les moles : <strong>{min(10.0, tot_s3):.1f} / 10</strong><br>
                &bull; Note obtenue à la détermination massique : <strong>{max(0.0, tot_s3 - 10.0):.1f} / 10</strong><br>
                &bull; Note Finale de l'Atelier 3 : <strong>{tot_s3:.1f} / 20</strong>
            </p>
            <div class="sub-title">Solution titrante : Diode (I2) | Concentration : 0.005 mol/L | 
            Composé dosé : Dioxyde de soufre (SO2) | Prise d'essai Va : {v_titre_session:.1f} mL | 
            Indicateur : Empois d'amidon</div>
            <div class="sub-title">DETAILS DE VOS CALCULS DE LABORATOIRE</div>
            <table>
                <thead>
                    <tr><th>Grandeur Mathematique / Etape</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        lignes_rapport3 = [
            ("Volume équivalent de diode en litre (L)", "at3_v_eq_l_cl", f"{att_v_eq_l:.5f} L", att_v_eq_l, 0.02),
            ("Quantité de matière d'I2 versée (mol)", "at3_n_argent_cl", f"{att_n_argent:.6f} mol", att_n_argent, 0.02),
            ("Quantité de matière de SO2 du bécher (mol)", "at3_n_chlorure_becher", f"{att_n_chlorure:.6f} mol", att_n_chlorure, 0.02),
            ("Concentration molaire en SO2 Ca (mol/L)", "at3_c_molaire_cl", f"{att_c_molaire:.4f} mol/L", att_c_molaire, 0.02),
            ("Concentration massique ou titre massique t (g/L)", "at3_t_massique_g", f"{att_t_g:.3f} g/L", att_t_g, 0.02),
            ("Concentration massique ou titre massique t (mg/L)", "at3_t_massique_mg", f"{att_t_mg:.1f} mg/L", att_t_mg, 0.02),
        ]

        import numpy as np
        for desc, key, txt_att, val_att, tol in lignes_rapport3:
            saisie_raw = str(st.session_state.get(key, "0.0")).replace(",", ".")
            try: saisie_val = float(saisie_raw)
            except: saisie_val = -999.0
            v_lbl = "CORRECT" if np.isclose(saisie_val, val_att, rtol=tol) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_cl3 += f"<tr><td>{desc}</td><td>{saisie_raw}</td><td>{txt_att}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cl3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'exploitation de Ripper généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"Rapport_Atelier3_SO2_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_cl3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )














