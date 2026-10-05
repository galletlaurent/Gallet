# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de l'Hydrazine",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage de l'Hydrazine")
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
if "points_ve_ph" not in st.session_state: 
    st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: 
    st.session_state.ph_actuel = 10.5  # L'hydrazine pure est basique
if "ph_eq_reel" not in st.session_state: 
    st.session_state.ph_eq_reel = 5.2  # pH théorique à l'équivalence (acide faible)
if "c_titrant" not in st.session_state: 
    st.session_state.c_titrant = 0.30
if "c_titre" not in st.session_state: 
    st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: 
    st.session_state.v_eq = 102.0
if "ph_eq" not in st.session_state: 
    st.session_state.ph_eq = 5.2
if "animation_active" not in st.session_state: 
    st.session_state.animation_active = False

if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Rouge de Méthyle": { "ph_min": 4.2, "ph_max": 6.2, "couleur_acide": "#F44336", "nom_acide": "Rouge","couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine": { "ph_min": 8.2, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F8BBD0", "nom_zone": "Rose pâle",  "couleur_base": "#E91E63", "nom_base": "Rose fuchsia" },
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
    "Généralités sur l'hydrazine",
    "Dosage colorimétrique de l'hydrazine",
    "Calcul théorique sur l'hydrazine et vérification pour le lancement"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]



def afficher_questions_conteneur_hydrazine(verrouille=False):
    import numpy as np
    import streamlit as st

    # Récupération des données de session calculées au préalable
    C_acide = st.session_state.get("c_titrant", 0.30)  # Ca (Acide chlorhydrique)
    v_eq_theorique = st.session_state.get("hyd_vrai_veq_calc", 102.0)  # Ve en mL
    V_ini = 10.0  # Vb (Volume d'hydrazine dans le bécher)
    M_hydrazine = 32.05  # g/mol
    facteur_dilution = 10.0
    V_fiole = 100.0  

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume équivalent en litre ($V_E$) :")
    with c2: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_v_eq_l", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer le nombre de moles d'acide chlorhydrique versé à l'équivalence :")
    with c4: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En déduire le nombre de moles d'hydrazine dosée dans le bécher :")
    with c6: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_base_becher", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en hydrazine fille dosée en mol/L :")
    with c8: st.number_input("", min_value=0.000, max_value=10.000, format="%.3f", key="at3_c_molaire_fille", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse d'hydrazine dosée dans le bécher en grammes :")
    with c10: st.number_input("", min_value=0.0000, max_value=100.0000, format="%.4f", key="at3_m_base_gramme", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En déduire la masse d'hydrazine dosée en milligrammes :")
    with c12: st.number_input("", min_value=0.0, max_value=10000.0, format="%.1f", key="at3_m_base_mg", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique d'hydrazine fille dosée en g/L :")
    with c14: st.number_input("", min_value=0.00, max_value=500.00, format="%.2f", key="at3_c_massique_fille", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique d'hydrazine fille dosée en mg/L :")
    with c16: st.number_input("", min_value=0.0, max_value=500000.0, format="%.1f", key="at3_c_massique_fille_mg", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : REMONTÉE AU CONTENEUR COMMERCIAL D'ERGO ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Donner le facteur de dilution appliqué :")
    with c18: st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_rapport_dilution", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("En déduire le nombre de moles d'hydrazine dans la fiole jaugée :")
    with c20: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_base_fiole", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En déduire le nombre de moles d'hydrazine estimé dans le réservoir mère :")
    with c22: st.number_input("", min_value=0.00000, max_value=5.00000, format="%.5f", key="at3_n_base_bouteille", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c23: st.write("Calculer la concentration molaire en hydrazine du conteneur mère en mol/L :")
    with c24: st.number_input("", min_value=0.00, max_value=20.00, format="%.2f", key="at3_c_molaire_mere", disabled=verrouille, label_visibility="collapsed")

    c25, c26 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c25: st.write("Calculer la masse de pureté d'hydrazine par litre de solution mère en grammes :")
    with c26: st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_m_mere_gramme", disabled=verrouille, label_visibility="collapsed")

    c27, c28 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c27: st.write("En déduire la masse d'hydrazine par litre de solution mère en milligrammes :")
    with c28: st.number_input("", min_value=0.0, max_value=1000000.0, format="%.1f", key="at3_m_mere_mg", disabled=verrouille, label_visibility="collapsed")

    c29, c30 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c29: st.write("Calculer la concentration massique globale de la solution mère en g/L :")
    with c30: st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_c_massique_mere", disabled=verrouille, label_visibility="collapsed")

    c31, c32 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c31: st.write("En déduire le pourcentage de pureté massique (%) obtenu :")
    with c32: st.number_input("", min_value=0.0, max_value=100.0, format="%.1f", key="at3_purete_massique_pourcent", disabled=verrouille, label_visibility="collapsed")

    c33, c34 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c33: st.write("Conclure sur l'autorisation d'avitaillement de l'étage de la fusée :")
    with c34: st.selectbox("", ["Choisir...", "L'hydrazine est conforme (≥ 98%): FEU VERT", "L'hydrazine n'est pas conforme: PROTOCOLE DE REJET"], key="at3_conclusion_bouteille", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

def generer_le_quiz_analytique_atelier_deux_hydrazine(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Récupération sécurisée des constantes calculées par le moteur de paillasse spatial
    v_eq_attendu = st.session_state.get("hyd_vrai_veq_calc", 102.0)
    c_acide_session = st.session_state.get("c_titrant", 0.30) # Concentration de l'acide titrant (Ca)
    v_base_dosée = 10.0 # Volume initial d'hydrazine Vb introduit dans le bécher

    # Calcul des moles d'ions oxonium versés à l'équivalence : n = Ca * Ve
    n_acide_equiv = (c_acide_session * v_eq_attendu) / 1000.0
    # À l'équivalence n_hydrazine = n_acide (coefficients stœchiométriques de 1:1)
    c_hydrazine_dose_attendue = (c_acide_session * v_eq_attendu) / v_base_dosée

    col_double_quiz_hyd, col_double_trous_hyd = st.columns(2)

    # Utilisation du suffixe d'état
    sfx = f"_h{int(st.session_state.get('v_verse', 0.0) * 10)}"

    with col_double_quiz_hyd:
        st.markdown("##### Quiz numérique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_acide_session:.2f} mol/L", "1.00 mol/L", "0.10 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante d'acide chlorhydrique ($C_a$) utilisée ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_hyd_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_base_dosée:.1f} mL", "20.0 mL", "50.0 mL"]
        st.write("**2.** Quel volume de solution titrée d'hydrazine ($V_b$) a été introduit dans le bécher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_hyd_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.2f} mL", "50.00 mL", "10.00 mL"]
        st.write("**3.** Quel est le volume équivalent exact ($V_E$) d'acide versé lu à la burette ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_hyd_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation entre Ca, Cb, Va, Vb à l'équivalence stœchiométrique ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Cb * Vb = Ca * Ve", "Ca * Cb = Va * Ve", "Cb / Vb = Ca / Ve"], key="col_g_quiz_hyd_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_acide_equiv:.5f} mol", f"{n_acide_equiv * 10:.5f} mol", "0.00100 mol"]
        st.write("**5.** Quelle quantité de matière d'ions oxonium $H_3O^+$ a été versée à l'équivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_hyd_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_hydrazine_dose_attendue:.3f} mol/L", "0.050 mol/L", "0.200 mol/L"]
        st.write("**6.** Déduisez-en la concentration molaire ($C_b$) de l'hydrazine dosée dans le bécher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_hyd_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_hyd:
        st.markdown("##### Synthèse de cours (Texte à trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduée utilisée pour verser la solution titrante d'acide est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette","Eprouvette graduée", "Pipette graduée"], key="hyd_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prélever les 10 mL d'hydrazine de manière ultra-précise, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugée", "Eprouvette graduée", "Burette graduée"], key="hyd_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour convertir le volume équivalent de mL en Litres, on doit l'")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "diviser par 10"], key="hyd_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. À l'équivalence, le nombre de moles de base et le nombre de moles d'acide réagis sont")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Egaux", "Doubles", "Inverses"], key="hyd_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. L'équivalence d'un titrage acido-basique se manifeste graphiquement")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Au saut de pH", "Au début du dosage", "À la fin du dégazage"], key="hyd_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_hydrazine1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "hyd_verrouille_tab1" not in st.session_state:
        return {}, {}

    # Initialisation et mélange unique obligatoire des 10 questions adaptées à l'hydrazine
    if "ordre_quiz1_hyd" not in st.session_state:
        base_quiz1_hyd = [
            {"id": "q1_1", "q": "La molécule d'hydrazine en solution aqueuse est une :", "type": "menu", "options": ["acide", "neutre", "basique"], "rep": "basique"},
            {"id": "q1_2", "q": "Calculer la masse molaire moléculaire de l'hydrazine en g/mol :", "type": "menu", "options": ["32", "17", "46"], "rep": "32"},
            {"id": "q1_3", "q": "Quel est le nom systématique (IUPAC) de la molécule d'hydrazine ?", "type": "menu", "options": ["diazane", "ammoniac", "azoture d'hydrogène"], "rep": "diazane"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes d'azote (N) que possède la molécule d'hydrazine ?", "type": "menu", "options": ["2", "1", "4"], "rep": "2"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogène (H) que possède la molécule d'hydrazine ?", "type": "menu", "options": ["4", "2", "6"], "rep": "4"},
            {"id": "q1_6", "q": "Quel est le nombre d'atomes d'oxygène (O) présents dans la structure moléculaire de l'hydrazine pure ?", "type": "menu", "options": ["0", "2", "1"], "rep": "0"},
            {"id": "q1_7", "q": "Quelle est la formule brute de l'hydrazine ?", "type": "menu", "options": ["N2H4", "NH3", "N2H2", "N4H2"], "rep": "N2H4"},
            {"id": "q1_8", "q": "D'après la légende atomique, quelle est la masse molaire de l'élément Azote (N) ?", "type": "menu", "options": ["14 g/mol", "1 g/mol", "16 g/mol"], "rep": "14 g/mol"},
            {"id": "q1_9", "q": "D'après la légende atomique, quelle est la masse molaire de l'élément Hydrogène (H) ?", "type": "menu", "options": ["1 g/mol", "14 g/mol", "7 g/mol"], "rep": "1 g/mol"},
            {"id": "q1_10", "q": "D'après la légende atomique du modèle moléculaire, la sphère bleue représente l'atome d' :", "type": "menu", "options": ["Azote (N)", "Hydrogène (H)", "Oxygène (O)"], "rep": "Azote (N)"}
        ]
        # Sauvegarde du mélange obligatoire en session
        copie_base = list(base_quiz1_hyd)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_hyd = copie_base

    col_double_quiz_h1, col_double_trous_h1 = st.columns(2)

    # --- COLONNE DE GAUCHE : L'ORDRE DES 10 QUESTIONS MÉLANGÉES ---
    with col_double_quiz_h1:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_hyd, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hyd_cl_g_{q_data['id']}"
            
            # Mélange local des options pour éviter l'ordre fixe des propositions
            cle_shuff_opts = f"opts_shuff_hyd_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = ["Choisir..."] + opts_copie
                
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_shuff_opts].index(val_p) if val_p in st.session_state[cle_shuff_opts] else 0
            
            dict_reponses_quiz[q_data["id"]] = st.selectbox(
                "", st.session_state[cle_shuff_opts], 
                index=sel_idx, key=cle_select, 
                disabled=verrouille, label_visibility="collapsed"
            )

    # --- COLONNE DE DROITE : LES 10 TROUS DE SYNTHÈSE ASSOCIFS ---
    with col_double_trous_h1:
        st.markdown("##### Synthèse des propriétés acido-basiques (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le carburant d'avitaillement étudié est une solution aqueuse de diazane ou")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Hydrazine", "Ammoniac"], key="hyd_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La présence d'un pKa de couple indique que ")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "La base est faible", "La base est forte", "L'acide est fort"], key="hyd_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'hydrazine appartient à la catégorie chimique des bases")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Faibles", "Fortes"], key="hyd_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Dans le bécher, la fin de la réaction se repère visuellement par ")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Le changement de couleur dans le bécher", "Le changement de couleur dans la burette"], key="hyd_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le pKa du couple de l'hydrazine à 25°C est de l'ordre de")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "8.1", "4.8", "1.2"], key="hyd_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'espèce chimique titrante acide employée dans la burette est l'")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Acide chlorhydrique", "Soude"], key="hyd_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. L'acide chlorhydrique ($H_3O^+ + Cl^-$) apporte en solution")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Un acide fort", "Une base faible"], key="hyd_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. L'unité internationale de la concentration molaire est le")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "mol/L", "g/mol", "g/L"], key="hyd_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le saut de pH et le changement de teinte de l'indicateur signalent l'")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Equivalence", "Liquéfaction"], key="hyd_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution basique d'ergol fait tendre sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7.0", "14.0", "0.0"], key="hyd_t10_s1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Atelier 1 : Généralités sur l'Hydrazine")
    
    # Adaptation de votre variable de verrouillage à l'hydrazine
    if "hyd_verrouille_tab1" not in st.session_state: 
        st.session_state.hyd_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme à votre structure
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LE RÉSERVOIR GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Document d'étude")
        
        # Adaptation du texte documentaire au domaine spatial de l'hydrazine
        texte_document = (
            "L'hydrazine est une solution liquide composée majoritairement d'hydrazine pure (N₂H₄) appelée également "
            "diazane, qui est une base faible caractérisée par le pKa de son couple acide/base (N₂H₅⁺/N₂H₄) égal à 8,1. "
            "C'est un composé chimique de synthèse instable utilisé comme monopergol ou ergol réducteur pour la propulsion "
            "et le contrôle d'attitude des satellites et des étages supérieurs de fusées (Norme spatiale ECSS-E-ST-35C). "
            "Le degré de pureté d’une solution d’hydrazine, indiqué sur le conteneur d'avitaillement, représente le pourcentage "
            "de pureté massique, c'est-à-dire la masse d'hydrazine pure exprimée en grammes pour 100 grammes de solution d'ergol. "
            "Pour autoriser le transfert, ce taux doit réglementairement être supérieur ou égal à 98,0 %."
        )
        st.info(texte_document)
        
        # Rendu graphique du conteneur/bouteille de transport d'ergol spatial via Matplotlib
        # Changement du fond de facecolor pour un ton industriel gris-bleu spatial (#e2e8f0)
        fig_bouteille, ax = plt.subplots(figsize=(4, 5.2), facecolor="#e2e8f0")
        ax.set_facecolor("#e2e8f0")
        
        # Dessin géométrique du conteneur renforcé d'hydrazine
        bouchon = patches.Rectangle((4, 8.5), 2, 0.8, color="#374151", ec="#1f2937") # Valve étanche grise
        col = patches.Polygon([[4.2, 8.5], [5.8, 8.5], [6.5, 7.2], [3.5, 7.2]], color="#9ca3af", ec="#4b5563")
        corps = patches.Rectangle((2.5, 1), 5, 6.2, color="#d1d5db", ec="#4b5563") # Corps en acier inox
        etiquette = patches.Rectangle((2.7, 1.8), 4.6, 4, color="#1e3a8a") # Étiquette bleue aérospatiale
        logo_fond = patches.Rectangle((4.2, 2.2), 1.6, 1.2, color="#b91c1c") # Picto danger rouge
        
        ax.add_patch(patches.Circle((5, 1), 2.5, color="#d1d5db", ec="#d1d5db"))
        ax.add_patch(corps)
        ax.add_patch(col)
        ax.add_patch(bouchon)
        ax.add_patch(etiquette)
        ax.add_patch(logo_fond)
        
        # Lignes de niveau / stries de renforcement du conteneur
        for y in np.linspace(1.2, 6.8, 8):
            ax.plot([2.55, 7.45], [y, y], color="#9ca3af", linewidth=1)
            
        # Textes de l'étiquette adaptés à l'hydrazine
        ax.text(5, 5.2, "HYDRAZINE", color="white", weight="bold", fontsize=14, ha="center")
        ax.text(5, 4.6, "N₂H₄ PUR", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 4.1, "ERGOL UNIQUE", color="white", weight="bold", fontsize=9, ha="center")
        ax.text(5, 3.0, "SPACE", color="white", weight="bold", fontsize=12, ha="center")
        ax.text(5, 2.5, "☣", color="#ffcc00", weight="bold", fontsize=16, ha="center") # Symbole danger chimique
        ax.text(3.4, 2.1, "98%", color="white", weight="bold", fontsize=11, ha="center") # Pureté visée
        ax.text(6.6, 2.1, "25 L", color="white", weight="bold", fontsize=11, ha="center") # Volume échantillonné
        
        ax.set_xlim(1, 9)
        ax.set_ylim(0, 10)
        ax.axis("off")
        st.pyplot(fig_bouteille)

    # --------------------------------------------------------
    # COLONNE DROITE : LES DONNÉES ATOMIQUES ET LA MOLÉCULE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Données et Légendes Atomiques")
        
        # Adaptation des légendes atomiques pour l'hydrazine
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Azote (N)**\n\nSphère bleue\nM(N) = 14 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # Nouvelles coordonnées géométriques pour la structure de l'hydrazine (H2N-NH2)
        n1 = np.array([3.3, 2.5])  # Premier atome d'azote
        n2 = np.array([4.7, 2.5])  # Second atome d'azote
        
        # Hydrogènes fixés sur le premier azote (n1)
        h1_n1 = np.array([2.7, 3.4])
        h2_n1 = np.array([2.7, 1.6])
        
        # Hydrogènes fixés sur le second azote (n2)
        h3_n2 = np.array([5.3, 3.4])
        h4_n2 = np.array([5.3, 1.6])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Tracé des liaisons covalentes de l'hydrazine
        tracer_liaison(n1, n2)      # Liaison simple centrale N-N
        tracer_liaison(n1, h1_n1)   # Liaisons N-H
        tracer_liaison(n1, h2_n1)
        tracer_liaison(n2, h3_n2)
        tracer_liaison(n2, h4_n2)

        def tracer_atome(p, symbole):
            if symbole == 'N': couleur, texte_couleur = "#2196F3", "white" # Bleu pour l'azote
            elif symbole == 'H': couleur, texte_couleur = "#ecf0f1", "black" # Blanc/gris pour l'hydrogène
            else: couleur, texte_couleur = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.24, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # Rendu des sphères atomiques
        tracer_atome(n1, 'N')
        tracer_atome(n2, 'N')
        tracer_atome(h1_n1, 'H')
        tracer_atome(h2_n1, 'H')
        tracer_atome(h3_n2, 'H')
        tracer_atome(h4_n2, 'H')

        # Ajustement des limites pour centrer la molécule N2H4
        ax_mol.set_xlim(1.5, 6.5)
        ax_mol.set_ylim(1.0, 4.2)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    # =========================================================================
    # LOGIQUE DE COUPLAGE DES CONFIGURATIONS DE NOTATION DYNAMIQUES
    # =========================================================================
    res_q1, res_t1 = afficher_questions_hydrazine1_dynamiques(
        verrouille=st.session_state.hyd_verrouille_tab1
    )

    st.write("---")
    st.subheader("Généralité sur l'hydrazine")

    # Récupération des identifiants (Assurez-vous que ces clés existent dans l'onglet Identification)
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_hyd1 = st.checkbox(
        "Je certifie avoir complété les questions relatives à l'hydrazine.", 
        key="check_certif_hyd1", 
        disabled=st.session_state.hyd_verrouille_tab1
    )

    verrou_hyd1 = st.session_state.get("hyd_verrouille_tab1", False)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_hyd1_official_net", use_container_width=True, disabled=verrou_hyd1):
        # Vérification des prérequis de validation
        if p_eleve == "INCONNU" or n_eleve == "INCONNU":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification Mission'.")
        elif not case_certif_hyd1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique adaptative liée au Quiz mélangé de l'hydrazine
            score_q1 = 0.0
            if "ordre_quiz1_hyd" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_hyd:
                    reponse_eleve = st.session_state.get(f"hyd_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (Spécifique Hydrazine)
            score_t1 = sum([
                st.session_state.get("hyd_t1_s1") == "Hydrazine",
                st.session_state.get("hyd_t2_s1") == "La base est faible",
                st.session_state.get("hyd_t3_s1") == "Faibles",
                st.session_state.get("hyd_t4_s1") == "Le changement de couleur dans le bécher",
                st.session_state.get("hyd_t5_s1") == "8.1",
                st.session_state.get("hyd_t6_s1") == "Acide chlorhydrique",
                st.session_state.get("hyd_t7_s1") == "Un acide fort",
                st.session_state.get("hyd_t8_s1") == "mol/L",
                st.session_state.get("hyd_t9_s1") == "Equivalence",
                st.session_state.get("hyd_t10_s1") == "7.0"
            ])

            # Sauvegarde des scores en mémoire session
            st.session_state.score_hyd1_p1 = round(float(score_q1), 1)
            st.session_state.score_hyd1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_hyd1 = round(float(score_q1 + score_t1), 1)
            st.session_state.hyd_verrouille_tab1 = True
            st.rerun()

    # --- AFFICHAGE ET COMPILATION DU RAPPORT APRÈS VERROUILLAGE ---
    if st.session_state.get("hyd_verrouille_tab1", False):
        scr1 = st.session_state.get("score_hyd1_p1", 0.0)
        scr2 = st.session_state.get("score_hyd1_p2", 0.0)
        tot_s = st.session_state.get("score_final_hyd1", 0.0)

        from datetime import datetime, timedelta
        timestamp_hyd1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HYDRAZINE 1 SCELLÉ | Note de session : {tot_s} / 20")

        # --- COMPILATION DU RAPPORT CHIMIQUE HTML ADAPTÉ ---
        html_export_hyd1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Hydrazine 1 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #3b82f6; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e3a8a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport de Laboratoire Spatial</h1>
                <p>Atelier 1 : Caractérisation de la solution mère d'ergol (Hydrazine)</p>
                <p>Opérateur : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Mission : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_hyd1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Nomenclature Moléculaire : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue à la Synthèse des propriétés : <strong>{scr2} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_hyd" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_hyd, 1):
                saisie = st.session_state.get(f"hyd_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hyd1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hyd1 += """
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
            "1. Le carburant d'avitaillement étudié est une solution aqueuse de diazane ou",
            "2. La présence d'un pKa de couple indique que",
            "3. L'hydrazine appartient à la catégorie chimique des bases",
            "4. Dans le bécher, la fin de la réaction se repère visuellement par",
            "5. Le pKa du couple de l'hydrazine à 25°C est de l'ordre de",
            "6. L'espèce chimique titrante acide employée dans la burette est l'",
            "7. L'acide chlorhydrique apporte en solution",
            "8. L'unité internationale de la concentration molaire est le",
            "9. Le saut de pH et le changement de teinte de l'indicateur signalent l'",
            "10. Diluer une solution basique d'ergol fait tendre sa valeur de pH vers"
        ]
        attendus_trous1 = ["Hydrazine", "La base est faible", "Faibles", "Le changement de couleur dans le bécher", "8.1", "Acide chlorhydrique", "Un acide fort", "mol/L", "Equivalence", "7.0"]
        
        for num in range(1, 11):
            saisie = st.session_state.get(f"hyd_t{num}_s1", "Choisir...")
            attendu = attendus_trous1[num-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_hyd1 += f"<tr><td>{num}</td><td>{phrases_trous1[num-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hyd1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Ajout d'un bouton de téléchargement pour le fichier HTML ainsi généré
        st.download_button(
            label=" TÉLÉCHARGER LE COMPTE-RENDU OFFICIEL (HTML)",
            data=html_export_hyd1,
            file_name=f"Rapport_Hydrazine_Atelier1_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



with tab2:
    st.header("Dosage colorimétrique de l'hydrazine")
    st.caption("Simulation interactive et animée du titrage de l'hydrazine par l'acide chlorhydrique")

    # Éviter les crashs si les dictionnaires parents ne sont pas encore initialisés
    if "solutions_hydrazine" not in st.session_state:
        st.session_state["solutions_hydrazine"] = {
            "Échantillon A (Eau de chaudière haute pression)": {"concentration_nominale_gL": 1.5},
            "Échantillon B (Stockage technique étalon)": {"concentration_nominale_gL": 3.2},
            "Échantillon C (Rejet industriel dilué)": {"concentration_nominale_gL": 0.6}
        }

    # Initialisation propre des états de session pour l'animation et le verrouillage
    if "hydrazine_verrouille_tab2" not in st.session_state: 
        st.session_state.hydrazine_verrouille_tab2 = False
    if "animation_active" not in st.session_state: 
        st.session_state.animation_active = False
    if "v_verse_acide" not in st.session_state: 
        st.session_state.v_verse_acide = 0.0
    if "pas_ml" not in st.session_state: 
        st.session_state.pas_ml = 0.5

    # Constantes physico-chimiques réelles de l'hydrazine (N2H4)
    V_echantillon_ml = 20.0     # Volume de solution d'hydrazine pipeté dans le bécher
    v_max_ml = 25.0             # Capacité maximale de la burette graduée
    M_hydrazine = 32.05         # Masse molaire de l'hydrazine (g/mol)

    # Récupération de la concentration de l'acide titrant (HCl) depuis la session (ou 0.100 mol/L par défaut)
    C_acide = st.session_state.get("c_titrant_acide", 0.100)

    # Récupération adaptative de la solution sélectionnée par l'étudiant
    liste_echantillons = list(st.session_state["solutions_hydrazine"].keys())
    solution_selectionnee = st.selectbox(
        "Sélectionnez la solution d'hydrazine à analyser :", 
        options=liste_echantillons, 
        disabled=st.session_state.hydrazine_verrouille_tab2,
        key="select_hydrazine_tab2"
    )

    info_solution = st.session_state["solutions_hydrazine"][solution_selectionnee]
    concentration_nominale_gL = info_solution["concentration_nominale_gL"]

    # Coefficient aléatoire pour individualiser les résultats des élèves
    coeff_alea = st.session_state.get("facteur_titrage_hydrazine", 1.0)

    # CALCUL CHIMIQUE RIGOUREUX
    # 1. Concentration molaire réelle de l'hydrazine simulée (mol/L)
    c_hydrazine_simulee = (concentration_nominale_gL / M_hydrazine) * coeff_alea
    
    # 2. Fixation de la masse réelle d'hydrazine présente dans le bécher (en g puis mg)
    st.session_state.masse_reelle_g = c_hydrazine_simulee * (V_echantillon_ml / 1000.0) * M_hydrazine
    masse_affichee_mg = st.session_state.masse_reelle_g * 1000.0

    # 3. Quantité de matière (moles) d'hydrazine dans le bécher
    moles_hydrazine_becher = st.session_state.masse_reelle_g / M_hydrazine
    
    # 4. Liaison mathématique : l'équivalence respecte la stœchiométrie 1:1 (N2H4 + H3O+ -> N2H5+ + H2O)
    if C_acide > 0:
        v_eq_theorique = (moles_hydrazine_becher / C_acide) * 1000.0
    else:
        v_eq_theorique = 12.0

    # Sauvegarde des variables calculées pour l'interface de l'étudiant et la correction
    st.session_state["th_vrai_veq_calc"] = round(float(v_eq_theorique), 2)
    st.session_state["input_at2_ve_lu_eleve"] = round(float(v_eq_theorique), 2)
    v_eq_visuel = st.session_state.th_vrai_veq_calc

    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-à-goutte")
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            # L'hydrazine est une base : on la titre par un acide fort (HCl)
            C_acide = st.number_input(
                "Concentration de l'acide chlorhydrique HCl C_0 (mol/L) :",
                min_value=0.001, max_value=1.0, value=float(C_acide), step=0.001,
                format="%.3f",
                disabled=True, key="c_acide_hydrazine_tab2"
            )
            
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :",
                min_value=0.1, max_value=2.0, value=float(st.session_state.pas_ml), step=0.1,
                disabled=st.session_state.hydrazine_verrouille_tab2, key="cfg_slider_pas_ml"
            )

    # Génération aléatoire d'une masse d'hydrazine dans le bécher pour individualiser le TP
    if "masse_reelle_hydrazine_mg" not in st.session_state:
        st.session_state.masse_reelle_hydrazine_mg = random.uniform(15.0, 30.0)

    # Affectation pour les calculs de référence des Ateliers 2 et 3
    masse_affichee_mg = st.session_state.masse_reelle_hydrazine_mg
    st.session_state.masse_reelle_g = masse_affichee_mg / 1000.0

    if "masse_reelle_g" not in st.session_state:
        st.session_state.masse_reelle_g = 0.0

    # CALCULS CHIMIQUES CORRIGÉS (Rapport stœchiométrique 1:1 entre HCl et N2H4)
    moles_hydrazine_becher = st.session_state.masse_reelle_g / M_hydrazine
    v_eq_theorique_calcul = (st.session_state.masse_reelle_g / (C_acide * M_hydrazine)) * 1000.0

    # Stockage et arrondi du volume équivalent pour l'interface étudiant
    st.session_state["th_vrai_veq_calc"] = round(float(v_eq_theorique_calcul), 2)
    st.session_state["input_at2_ve_lu_eleve"] = round(float(v_eq_theorique_calcul), 2)
    v_eq_visuel = st.session_state.th_vrai_veq_calc

    st.info(
        f"Paramètre mesuré : Concentration en Hydrazine | Volume de prise d'essai V : {V_echantillon_ml:.1f} mL | "
        f"Masse de N₂H₄ simulée dans le bécher : {masse_affichee_mg:.2f} mg | "
        f"Indicateur : Phénolphtaléine (ou Rouge de méthyle)"
    )
    st.divider()

    v_eq_affiche = v_eq_visuel

    # Lecture dynamique des teintes de l'indicateur configurées dans la session
    # Note : Remplacer 'teintes_acido_basique' si le dictionnaire global utilise un autre nom
    t_data = st.session_state.get("teintes_acido_basique", {
        "Avant equivalence": {"couleur_hex": "#FF69B4"},   # Rose (Phénolphtaléine en milieu basique)
        "Zone sensible": {"couleur_hex": "#FFC0CB"},       # Rose pâle
        "Apres equivalence": {"couleur_hex": "#FFFFFF"}     # Incolore (milieu acide)
    })

    c_base_initiale = t_data["Avant equivalence"]["couleur_hex"]
    c_zone = t_data["Zone sensible"]["couleur_hex"]
    c_acide_final = t_data["Apres equivalence"]["couleur_hex"]

    html_animation_paillasse = f"""
    <div style="text-align: center; font-family: sans-serif;">
        <div style="margin-bottom: 12px;">
            <button id="btn-start" style="padding: 6px 16px; background: #22c55e; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Démarrer</button>
            <button id="btn-pause" style="padding: 6px 16px; background: #eab308; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Pause</button>
            <button id="btn-clear" style="padding: 6px 16px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">Effacer</button>
        </div>
        <canvas id="paillasse_canvas" width="260" height="380" style="background: white; border: 1px solid #cbd5e1; border-radius: 8px;"></canvas>
        <div id="zone-bilan" style="margin-top: 10px; padding: 8px; border-radius: 6px; background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; font-size: 11px; font-weight: bold; display: none;">
            Titrage terminé : Le volume maximal de la burette a été versé.
        </div>
    </div>

    <script>
        const canvas = document.getElementById('paillasse_canvas');
        const ctx = canvas.getContext('2d');
        
        let vVerse = 0;
        const vMax = {v_max_ml};
        const vEq = {v_eq_visuel};
        const pas = {st.session_state.pas_ml};
        let isRunning = false;
        let tick = 0;

        // Récupération des teintes adaptées au virage acido-basique de la session
        const colorInitialeBase = "{c_base_initiale}";  // Rose (ex: Phénolphtaléine en milieu basique)
        const colorZoneSensible = "{c_zone}";           // Rose pâle (Zone de virage)
        const colorFinaleAcide = "{c_acide_final}";     // Incolore / Neutre (Milieu acide)

        document.getElementById('btn-start').addEventListener('click', () => {{ isRunning = true; }});
        document.getElementById('btn-pause').addEventListener('click', () => {{ isRunning = false; }});
        document.getElementById('btn-clear').addEventListener('click', () => {{
            isRunning = false;
            vVerse = 0;
            tick = 0;
            document.getElementById('zone-bilan').style.display = 'none';
        }});

        function drawScene() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            tick++;

            if (isRunning && vVerse < vMax) {{
                vVerse = Math.min(vMax, vVerse + pas);
            }} else if (vVerse >= vMax) {{
                isRunning = false;
                document.getElementById('zone-bilan').style.display = 'block';
            }}

            // 1. Potence métallique
            ctx.fillStyle = '#7f8c8d';
            ctx.fillRect(40, 40, 10, 310); 
            ctx.fillStyle = '#95a5a6';
            ctx.fillRect(45, 60, 105, 5);  

            // 2. Burette Graduée (contient l'acide HCl)
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(140, 50, 20, 160); 
            
            let hauteurBurette = 156 * (1 - (vVerse / vMax));
            let yLiquideHaut = 51.5 + (156 - hauteurBurette);
            
            ctx.fillStyle = 'rgba(224, 242, 254, 0.8)'; // Teinte bleutée translucide pour l'acide HCl aqueux
            ctx.fillRect(141.5, yLiquideHaut, 17, hauteurBurette);

            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 0.8;
            for (let y = 60; y < 200; y += 15) {{
                ctx.beginPath(); ctx.moveTo(140, y); ctx.lineTo(145, y); ctx.stroke();
            }}

            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(146, 210, 8, 15);

            // Volume en direct
            ctx.fillStyle = '#b45309';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText(vVerse.toFixed(1) + ' mL', 165, yLiquideHaut + 4);

            // Goutte en chute
            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 232 : 258;
                ctx.fillStyle = 'rgba(224, 242, 254, 0.8)';
                ctx.beginPath(); ctx.arc(150, yGoutte, 2.5, 0, 2 * Math.PI); ctx.fill();
            }}

            // 3. Agitateur Magnétique
            ctx.fillStyle = '#bdc3c7';
            ctx.strokeStyle = '#7f8c8d';
            ctx.lineWidth = 1.5;
            ctx.fillRect(90, 310, 120, 30);
            ctx.strokeRect(90, 310, 120, 30);
            
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath(); ctx.ellipse(150, 325, 12, 5, 0, 0, 2 * Math.PI); ctx.fill();

            // 4. Bécher Gradué (Contient la solution d'hydrazine)
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(105, 230); ctx.lineTo(105, 310); ctx.lineTo(205, 310); ctx.lineTo(205, 230);
            ctx.stroke();

            // Gestion chimique dynamique des couleurs dans le bécher (Milieu Basique -> Neutre -> Acide)
            let couleurSol = colorInitialeBase; 
            let nomTeinte = 'Teinte basique (Initiale)';
            
            if (Math.abs(vVerse - vEq) <= 0.3) {{
                couleurSol = colorZoneSensible; 
                nomTeinte = 'Zone de virage (Équivalence proche)';
            }} else if (vVerse > vEq) {{
                couleurSol = colorFinaleAcide; 
                nomTeinte = 'Teinte acide (Post-équivalence)';
            }}

            let hauteurLiq = 15 + (45 * (vVerse / vMax));
            ctx.fillStyle = couleurSol;
            ctx.fillRect(106, 309 - hauteurLiq, 98, hauteurLiq);

            // Barreau aimanté (effet de rotation accéléré)
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 0.8;
            ctx.save();
            ctx.translate(150, 302);
            ctx.rotate((tick % 2 === 0 ? 20 : -20) * Math.PI / 180);
            ctx.fillRect(-14, -2.5, 28, 5);
            ctx.strokeRect(-14, -2.5, 28, 5);
            ctx.restore();

            ctx.fillStyle = '#334155';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText('Indicateur : ' + nomTeinte, 40, 365);

            setTimeout(() => {{
                requestAnimationFrame(drawScene);
            }}, 60); // Vitesse d'animation accrue (60ms) pour un rendu fluide du compte-goutte
        }}

        drawScene();
    </script>
    """
    components.html(html_animation_paillasse, height=460)

    if st.button("AFFICHER LES RÉSULTATS DU TITRAGE", key="btn_sync_paillasse_final", use_container_width=True):
        # Utilisation des variables d'état unifiées pour l'hydrazine
        st.session_state.v_verse_acide = float(v_eq_visuel)
        st.session_state.hydrazine_verrouille_tab2 = True
        st.rerun()

    # --- BANDEAU DE RÉSULTATS DE SÉANCE SYNCHRONISÉ ---
    v_eq_affiche = v_eq_visuel

    texte_resultats = (
        f"Repères d'équivalence de la session : "
        f"Volume équivalent d'acide chlorhydrique Veq = {v_eq_affiche:.2f} mL"
    )

    # Affichage du bandeau de succès si l'atelier est verrouillé (résultats validés)
    if st.session_state.get("hydrazine_verrouille_tab2", False):
        st.success(texte_resultats)
        st.session_state["input_at2_ve_lu_eleve"] = v_eq_affiche

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # --- CALCULS CHIMIQUES DE CORRECTION (Pour le Quiz/Vérification) ---
    # Paramètres du prélèvement de la solution d'hydrazine
    V_echantillon_ml_correction = 20.0
    C_acide_correction = 0.10  # En mol/L, aligné avec votre configuration

    # Quantité de matière d'acide HCl versée à l'équivalence (en moles)
    n_acide_equiv = (C_acide_correction * v_eq_theorique) / 1000.0

    # Relation stœchiométrique 1:1 -> n(hydrazine) dans le bécher = n(acide) versé
    moles_hydrazine_becher_simule = n_acide_equiv

    # Détermination de l'état de verrouillage global pour l'étudiant
    verrou_hydrazine2 = st.session_state.get("hydrazine_verrouille_tab2", False)

    # Affichage adaptatif du questionnaire selon l'avancement de l'animation
    if not st.session_state.get("animation_active", False):
        try:
            # Appel de votre fonction de quiz dédiée à l'hydrazine
            generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_hydrazine2)
        except NameError:
            st.warning("La fonction de génération du quiz analytique n'est pas définie dans ce scope.")
    else:
        st.info("Le versement de la solution titrante est en cours... Le formulaire d'évaluation s'affichera dès que l'animation sera terminée.")

    # Récupération des informations d'identification de l'étudiant
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # Case à cocher de certification finale unique pour l'Atelier 2
    case_certif_hyd2 = st.checkbox(
        "Je certifie avoir complété l'intégralité des questionnaires de l'Atelier 2 relatifs au dosage de l'hydrazine.", 
        key="check_certif_hyd2_final_net", 
        disabled=verrou_hydrazine2
    )
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_hyd2_official_net", use_container_width=True, disabled=verrou_hyd2):
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
        
        if p_eleve == "INCONNU" or n_eleve == "INCONNU":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification Mission'.")
        elif not case_certif_hyd2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Récupération des constantes de référence pour l'hydrazine
            C_acide = st.session_state.get("c_titrant", 0.30)
            v_eq_theorique = st.session_state.get("hyd_vrai_veq_calc", 102.0)
            V_ini = 10.0 # Volume initial d'hydrazine Vb mis dans le bécher

            # 1. Correction automatique du Quiz Numérique de gauche (6 questions)
            moles_acide_equiv = (C_acide * v_eq_theorique) / 1000.0
            concentration_hydrazine_attendue = (C_acide * v_eq_theorique) / V_ini

            score_q2 = sum([
                st.session_state.get("col_g_quiz_hyd_q1_tab2") == f"{C_acide:.2f} mol/L",
                st.session_state.get("col_g_quiz_hyd_q2_tab2") == f"{V_ini:.1f} mL",
                st.session_state.get("col_g_quiz_hyd_q3_tab2") == f"{v_eq_theorique:.2f} mL",
                st.session_state.get("col_g_quiz_hyd_q4_tab2") == "Cb * Vb = Ca * Ve",
                st.session_state.get("col_g_quiz_hyd_q5_tab2") == f"{moles_acide_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_hyd_q6_tab2") == f"{concentration_hydrazine_attendue:.3f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction automatique du Texte à trous de droite (5 cases)
            score_t2 = sum([
                st.session_state.get("hyd_t1_tab2") == "Burette",
                st.session_state.get("hyd_t2_tab2") == "Pipette jaugée",
                st.session_state.get("hyd_t3_tab2") == "diviser par 1000",
                st.session_state.get("hyd_t4_tab2") == "Egaux",
                st.session_state.get("hyd_t5_tab2") == "Au saut de pH"
            ]) * (10.0 / 5.0)

            st.session_state.score_hyd2_p1 = round(float(score_q2), 1)
            st.session_state.score_hyd2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_hyd2 = round(float(score_q2 + score_t2), 1)
            st.session_state.hyd_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("hyd_verrouille_tab2", False):
        scr1 = st.session_state.get("score_hyd2_p1", 0.0)
        scr2 = st.session_state.get("score_hyd2_p2", 0.0)
        tot_s = st.session_state.get("score_final_hyd2", 0.0)

        # Récupération des données d'affichage et de l'indicateur actif
        C_acide = st.session_state.get("c_titrant", 0.30)
        v_eq_theorique = st.session_state.get("hyd_vrai_veq_calc", 102.0)
        ph_eq_theorique = st.session_state.get("ph_eq", 5.2)
        
        # Récupération de l'indicateur actif (sélection par défaut ou stockée)
        ind_data = st.session_state.indicateurs["Rouge de Méthyle"]

        # Tracé complet de la courbe expérimentale de suivi pH-métrique pour le rapport
        import io
        import base64
        
        volumes_simules = np.linspace(0.0, 150.0, 300)
        phs_simules = []
        for v in volumes_simules:
            if v < v_eq_theorique:
                ph = 8.5 + 1.5 * np.log10(max(0.001, (v_eq_theorique - v) / v_eq_theorique))
            else:
                ph = 2.5 - 1.0 * np.log10(max(0.001, (v - v_eq_theorique) / v_eq_theorique))
            phs_simules.append(ph)

        fig_rep, ax_rp = plt.subplots(figsize=(5, 3.8))
        ax_rp.axhspan(0, ind_data["ph_min"], facecolor=ind_data["couleur_acide"], alpha=0.15, zorder=0)
        ax_rp.axhspan(ind_data["ph_min"], ind_data["ph_max"], facecolor=ind_data["couleur_zone"], alpha=0.20, zorder=0)
        ax_rp.axhspan(ind_data["ph_max"], 14, facecolor=ind_data["couleur_base"], alpha=0.15, zorder=0)
        
        # Courbe continue
        ax_rp.plot(volumes_simules, phs_simules, color="black", linewidth=2.0)
        
        # Point de contrôle de l'équivalence d'une base faible
        ax_rp.scatter([v_eq_theorique], [ph_eq_theorique], color="blue", marker="+", s=150, linewidths=2.5, zorder=6)
        ax_rp.plot([v_eq_theorique, v_eq_theorique], [0, ph_eq_theorique], color="blue", linestyle=":", lw=1.2)
        ax_rp.plot([0, v_eq_theorique], [ph_eq_theorique, ph_eq_theorique], color="blue", linestyle=":", lw=1.2)

        ax_rp.set_xlim(0, 155)
        ax_rp.set_ylim(0, 14)
        ax_rp.set_xlabel("Volume d'acide verse V_A (mL)", fontsize=9)
        ax_rp.set_ylabel("pH", fontsize=9)
        ax_rp.grid(True, linestyle=":")
        
        tampon_memoire = io.BytesIO()
        fig_rep.savefig(tampon_memoire, format="png", bbox_inches="tight")
        tampon_memoire.seek(0)
        base64_image_courbe = base64.b64encode(tampon_memoire.read()).decode("utf-8")
        plt.close(fig_rep)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        timestamp_hyd2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER HYDRAZINE 2 SCELLÉ | Note de session : {tot_s} / 20")

        # --- COMPILATION DU RAPPORT TECHNIQUE HTML ---
        html_export_hyd2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Hydrazine 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #3b82f6; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                .img-container {{ text-align: center; margin: 25px 0; background: white; padding: 15px; border-radius: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                .img-container img {{ max-width: 100%; height: auto; border: 1px solid #cbd5e1; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e3a8a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport de Qualification des Ergols</h1>
                <p>Atelier 2 : Dosage colorimetrique et suivi pH-metrique de la solution fille</p>
                <p>Ingenieur : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Mission : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_hyd2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #3b82f6;">
                &bull; Note obtenue au Quiz de suivi de titrage : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours : <strong>{scr2} / 10</strong><br>
                &bull; Note Finale de l'Atelier 2 : <strong>{tot_s} / 20</strong>
            </p>
            <div class="sub-title">Compose : Hydrazine ($N_2H_4$) | Titrant : Acide chlorhydrique ($HCl$) : {C_acide:.2f} mol/L</div>

            <div class="sub-title">SAUVEGARDE GEOMETRIQUE DE VOTRE COURBE EXPERIMENTALE</div>
            <div class="img-container">
                <img src="data:image/png;base64,{base64_image_courbe}" alt="Courbe de suivi de titrage hydrazine">
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="TELECHARGER LE RAPPORT COMPLET DE L'ATELIER 2 (HTML)",
            data=html_export_hyd2,
            file_name=f"Rapport_Hydrazine_Atelier2_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("Calcul théorique & Vérification du conteneur")
    st.caption("Vérification de la conformité du pourcentage de pureté massique indiqué sur le lot d'ergols")

    if "hyd_verrouille_tab3" not in st.session_state: 
        st.session_state.hyd_verrouille_tab3 = False

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2 (Hydrazine)
    c_acide_session = st.session_state.get("c_titrant", 0.30)  # Ca
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 102.0)  # Ve en mL
    ph_eq_session = st.session_state.get("input_at2_phe_lu_eleve", 5.2)  # pHe
    v_titre_session = 10.0  # Vb (Volume de solution d'hydrazine diluée dans le bécher)
    M_hydrazine = 32.05  # g/mol
    facteur_dilution = 10.0
    V_fiole = 100.0
    MASSE_VOLUMIQUE_MERE = 1010.0  # g/L de solution mère d'ergol

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #3b82f6; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les résultats de votre dosage d'ergol
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On a dilué 10 mL d'hydrazine pure dans une fiole de 100 mL à l'aide d'une pipette jaugée. Pour le dosage, on a prélevé 10 mL de cette solution fille diluée.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; pH_eq = {ph_eq_session:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; concentration titrante (HCl) = {c_acide_session:.2f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Volume titré (Hydrazine) = {v_titre_session:.1f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M = {M_hydrazine:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; n = C x V </p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; m = n x M</p>", unsafe_allow_html=True)

    st.write("---")

    # Moteur de calcul théorique de référence pour la correction automatique sur 20 points
    v_eq_litre_ref = v_eq_session / 1000.0
    n_acide_equiv_ref = c_acide_session * v_eq_litre_ref
    n_base_becher_ref = n_acide_equiv_ref
    c_hydrazine_fille_ref = n_base_becher_ref / (v_titre_session / 1000.0)
    m_hydrazine_becher_ref = n_base_becher_ref * M_hydrazine
    m_hydrazine_becher_mg_ref = m_hydrazine_becher_ref * 1000.0
    c_massique_fille_ref = c_hydrazine_fille_ref * M_hydrazine
    c_massique_fille_mg_ref = c_massique_fille_ref * 1000.0

    n_hydrazine_fiole_ref = c_hydrazine_fille_ref * (V_fiole / 1000.0)
    n_hydrazine_bouteille_ref = n_hydrazine_fiole_ref * facteur_dilution * 10 # Remontée par litre de solution mère
    c_hydrazine_mere_ref = c_hydrazine_fille_ref * facteur_dilution
    m_hydrazine_bouteille_ref = n_hydrazine_bouteille_ref * M_hydrazine
    m_hydrazine_bouteille_mg_ref = m_hydrazine_bouteille_ref * 1000.0
    c_massique_mere_ref = c_hydrazine_mere_ref * M_hydrazine
    c_massique_mere_mg_ref = c_massique_mere_ref * 1000.0
    
    # Pureté massique (%) = (Concentration massique mère / Masse volumique de la solution mère) * 100
    purete_calcule_ref = (c_massique_mere_ref / MASSE_VOLUMIQUE_MERE) * 100.0

    verrou_hyd3 = st.session_state.hyd_verrouille_tab3

    # Appel de la fonction contenant l'affichage des deux blocs colorés adaptés à l'hydrazine
    try:
        afficher_questions_conteneur_hydrazine(verrouille=verrou_hyd3)
    except NameError:
        st.error("La fonction 'afficher_questions_conteneur_hydrazine' n'a pas été trouvée au sommet de votre script.")

    verrou_hyd3 = st.session_state.get("hyd_verrouille_tab3", False)
    case_certif_hyd3 = st.checkbox(
        "Je certifie avoir complété l'intégralité des calculs de l'Atelier 3.", 
        key="check_certif_hyd3_net", 
        disabled=verrou_hyd3
    )
    
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_vin3_official_net", use_container_width=True, disabled=verrou_vin3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Bloc Bleu (8 questions)
            score_b1 = sum([
                abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001,
                abs(st.session_state.get("at3_n_soude", 0.0) - n_soude_equiv_ref) < 0.0001,
                abs(st.session_state.get("at3_n_acide_becher", 0.0) - n_acide_becher_ref) < 0.0001,
                abs(st.session_state.get("at3_c_molaire_fille", 0.0) - c_acide_fille_ref) < 0.01,
                abs(st.session_state.get("at3_m_acide_gramme", 0.0) - m_acide_becher_ref) < 0.01,
                abs(st.session_state.get("at3_m_acide_mg", 0.0) - m_acide_becher_mg_ref) < 1.0,
                abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1,
                abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 10.0
            ]) * (10.0 / 8.0)

            # 2. Correction du Bloc Jaune (9 questions)
            score_b2 = sum([
                st.session_state.get("at3_rapport_dilution", 0.0) == 10.0,
                abs(st.session_state.get("at3_n_acide_fiole", 0.0) - n_acide_fiole_ref) < 0.0001,
                abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - n_acide_bouteille_ref) < 0.001,
                abs(st.session_state.get("at3_c_molaire_mere", 0.0) - c_acide_mere_ref) < 0.1,
                abs(st.session_state.get("at3_m_mere_gramme", 0.0) - m_acide_bouteille_ref) < 1.0,
                abs(st.session_state.get("at3_m_mere_mg", 0.0) - m_acide_bouteille_mg_ref) < 100.0,
                abs(st.session_state.get("at3_c_massique_mere", 0.0) - c_massique_mere_ref) < 1.0,
                abs(st.session_state.get("at3_c_massique_mere_mg", 0.0) - degre_bouteille_ref) < 0.2,
                "conforme" in str(st.session_state.get("at3_conclusion_bouteille")).lower()
            ]) * (10.0 / 9.0)

            st.session_state.score_vin3_p1 = round(float(score_b1), 1)
            st.session_state.score_vin3_p2 = round(float(score_b2), 1)
            st.session_state.score_final_vin3 = round(float(score_b1 + score_b2), 1)
            st.session_state.vin_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("vin_verrouille_tab3", False):
        scr1 = st.session_state.get("score_vin3_p1", 0.0)
        scr2 = st.session_state.get("score_vin3_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin3", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import datetime, timedelta
        timestamp_vin3 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"VINAIGRE 3 SCELLE | Note de session : {tot_s} / 20")

        # --- COMPILATION DU RAPPORT CHIMIQUE HTML ---
        html_export_vin3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vinaigre 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Calcul theorique & Verification de la bouteille</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Compose : Vinaigre | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L</div>
            <div class="sub-title">Recapitulatif des Notes Generees (V_eq releve = {v_eq_session:.2f} mL)</div>

            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Bloc Exploitation (Becher) : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue au Bloc Bouteille Commerciale : <strong>{scr2} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU BLOC BLEU (EXPLOITATION DANS LE BECHER)</div>
            <table>
                <thead>
                    <tr><th>Grandeur demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr><td>Volume equivalent en Litres (L)</td><td>{st.session_state.get("at3_v_eq_l", 0.0):.5f}</td><td>{v_eq_litre_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001 else "INCORRECT"}</td></tr>
                    <tr><td>Quantite de soude versee (mol)</td><td>{st.session_state.get("at3_n_soude", 0.0):.5f}</td><td>{n_soude_equiv_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_soude", 0.0) - n_soude_equiv_ref) < 0.0001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_soude", 0.0) - n_soude_equiv_ref) < 0.0001 else "INCORRECT"}</td></tr>
                    <tr><td>Quantite d'acide dosee (mol)</td><td>{st.session_state.get("at3_n_acide_becher", 0.0):.5f}</td><td>{n_acide_becher_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_becher", 0.0) - n_acide_becher_ref) < 0.0001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_acide_becher", 0.0) - n_acide_becher_ref) < 0.0001 else "INCORRECT"}</td></tr>
                    <tr><td>Concentration molaire fille (mol/L)</td><td>{st.session_state.get("at3_c_molaire_fille", 0.0):.3f}</td><td>{c_acide_fille_ref:.3f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_molaire_fille", 0.0) - c_acide_fille_ref) < 0.01 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_molaire_fille", 0.0) - c_acide_fille_ref) < 0.01 else "INCORRECT"}</td></tr>
                    <tr><td>Masse d'acide dosee (g)</td><td>{st.session_state.get("at3_m_acide_gramme", 0.0):.4f}</td><td>{m_acide_becher_ref:.4f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_m_acide_gramme", 0.0) - m_acide_becher_ref) < 0.01 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_m_acide_gramme", 0.0) - m_acide_becher_ref) < 0.01 else "INCORRECT"}</td></tr>

                    <tr><td>Masse d'acide dosé (mg)</td><td>{st.session_state.get("at3_m_acide_mg", 0.0):.1f}</td><td>{m_acide_becher_mg_ref:.1f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_m_acide_mg", 0.0) - m_acide_becher_mg_ref) < 1.0 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_m_acide_mg", 0.0) - m_acide_becher_mg_ref) < 1.0 else "INCORRECT"}</td></tr>
                    <tr><td>Concentration massique fille (g/L)</td><td>{st.session_state.get("at3_c_massique_fille", 0.0):.2f}</td><td>{c_massique_fille_ref:.2f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1 else "INCORRECT"}</td></tr>
                    <tr><td>Concentration massique fille (mg/L)</td><td>{st.session_state.get("at3_c_massique_fille_mg", 0.0):.1f}</td><td>{c_massique_fille_mg_ref:.1f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 10.0 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 10.0 else "INCORRECT"}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DU BLOC JAUNE (REMONTEE COMMERCIALE)</div>
            <table>
                <thead>
                    <tr><th>Grandeur demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr><td>Rapport de dilution</td><td>{st.session_state.get("at3_rapport_dilution", 0.0):.1f}</td><td>10.0</td><td class="{"status-correct" if st.session_state.get("at3_rapport_dilution", 0.0) == 10.0 else "status-incorrect"}">{"CORRECT" if st.session_state.get("at3_rapport_dilution", 0.0) == 10.0 else "INCORRECT"}</td></tr>
                    <tr><td>Quantite de matiere dans la fiole (mol)</td><td>{st.session_state.get("at3_n_acide_fiole", 0.0):.5f}</td><td>{n_acide_fiole_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_fiole", 0.0) - n_acide_fiole_ref) < 0.0001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_acide_fiole", 0.0) - n_acide_fiole_ref) < 0.0001 else "INCORRECT"}</td></tr>
                    <tr><td>Quantite de matiere dans la bouteille (mol)</td><td>{st.session_state.get("at3_n_acide_bouteille", 0.0):.5f}</td><td>{n_acide_bouteille_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - n_acide_bouteille_ref) < 0.01 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - n_acide_bouteille_ref) < 0.01 else "INCORRECT"}</td></tr>
                    <tr><td>Concentration molaire mere (mol/L)</td><td>{st.session_state.get("at3_c_molaire_mere", 0.0):.2f}</td><td>{c_acide_mere_ref:.2f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_molaire_mere", 0.0) - c_acide_mere_ref) < 0.1 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_molaire_mere", 0.0) - c_acide_mere_ref) < 0.1 else "INCORRECT"}</td></tr>
                    <tr><td>Masse d'acide mere par Litre (g)</td><td>{st.session_state.get("at3_m_mere_gramme", 0.0):.1f}</td><td>{m_acide_bouteille_ref:.1f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_m_mere_gramme", 0.0) - m_acide_bouteille_ref) < 1.0 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_m_mere_gramme", 0.0) - m_acide_bouteille_ref) < 1.0 else "INCORRECT"}</td></tr>
                    <tr><td>Masse d'acide mere par Litre (mg)</td><td>{st.session_state.get("at3_m_mere_mg", 0.0):.1f}</td><td>{m_acide_bouteille_mg_ref:.1f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_m_mere_mg", 0.0) - m_acide_bouteille_mg_ref) < 100.0 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_m_mere_mg", 0.0) - m_acide_bouteille_mg_ref) < 100.0 else "INCORRECT"}</td></tr>
                    <tr><td>Concentration massique mere (g/L)</td><td>{st.session_state.get("at3_c_massique_mere", 0.0):.1f}</td><td>{c_massique_mere_ref:.1f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_mere", 0.0) - c_massique_mere_ref) < 1.0 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_massique_mere", 0.0) - c_massique_mere_ref) < 1.0 else "INCORRECT"}</td></tr>
                    <tr><td>Degré massique d'acidite du vinaigre (°)</td><td>{st.session_state.get("at3_c_massique_mere_mg", 0.0):.1f}°</td><td>{degre_bouteille_ref:.1f}°</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_mere_mg", 0.0) - degre_bouteille_ref) < 0.2 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_massique_mere_mg", 0.0) - degre_bouteille_ref) < 0.2 else "INCORRECT"}</td></tr>
                    <tr><td>Conclusion reglementaire officielle</td><td>{st.session_state.get("at3_conclusion_bouteille", "Choisir...")}</td><td>Le vinaigre est conforme a l'étiquette (8°)</td><td class="{"status-correct" if "conforme" in str(st.session_state.get("at3_conclusion_bouteille")).lower() else "status-incorrect"}">{"CORRECT" if "conforme" in str(st.session_state.get("at3_conclusion_bouteille")).lower() else "INCORRECT"}</td></tr>
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de synthese analytique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"Vinaigre3_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: nom_f3 = nom_f3.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_vin3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )
    verrou_hyd3 = st.session_state.get("hyd_verrouille_tab3", False)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_hyd3_official_net", use_container_width=True, disabled=verrou_hyd3):
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        
        if p_eleve == "INCONNU" or n_eleve == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification Mission'.")
        elif not case_certif_hyd3_net:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Bloc Bleu (8 questions) - Hydrazine dans le becher
            score_b1 = sum([
                abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001,
                abs(st.session_state.get("at3_n_acide", 0.0) - n_acide_equiv_ref) < 0.0001,
                abs(st.session_state.get("at3_n_base_becher", 0.0) - n_base_becher_ref) < 0.0001,
                abs(st.session_state.get("at3_c_molaire_fille", 0.0) - c_hydrazine_fille_ref) < 0.01,
                abs(st.session_state.get("at3_m_base_gramme", 0.0) - m_hydrazine_becher_ref) < 0.01,
                abs(st.session_state.get("at3_m_base_mg", 0.0) - m_hydrazine_becher_mg_ref) < 1.0,
                abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1,
                abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 10.0
            ]) * (10.0 / 8.0)

            # 2. Correction du Bloc Jaune (9 questions) - Remontee au conteneur d'ergol
            score_b2 = sum([
                st.session_state.get("at3_rapport_dilution", 0.0) == 10.0,
                abs(st.session_state.get("at3_n_base_fiole", 0.0) - n_hydrazine_fiole_ref) < 0.0001,
                abs(st.session_state.get("at3_n_base_bouteille", 0.0) - n_hydrazine_bouteille_ref) < 0.001,
                abs(st.session_state.get("at3_c_molaire_mere", 0.0) - c_hydrazine_mere_ref) < 0.1,
                abs(st.session_state.get("at3_m_mere_gramme", 0.0) - m_hydrazine_mere_litre_ref) < 1.0,
                abs(st.session_state.get("at3_m_mere_mg", 0.0) - m_hydrazine_mere_litre_mg_ref) < 100.0,
                abs(st.session_state.get("at3_c_massique_mere", 0.0) - c_massique_mere_ref) < 1.0,
                abs(st.session_state.get("at3_purete_massique_pourcent", 0.0) - purete_massique_ref) < 0.2,
                "vert" in str(st.session_state.get("at3_conclusion_bouteille")).lower() or "conforme" in str(st.session_state.get("at3_conclusion_bouteille")).lower()
            ]) * (10.0 / 9.0)

            # Enregistrement des scores de session
            st.session_state.score_hyd3_p1 = round(float(score_b1), 1)
            st.session_state.score_hyd3_p2 = round(float(score_b2), 1)
            st.session_state.score_final_hyd3 = round(float(score_b1 + score_b2), 1)
            st.session_state.hyd_verrouille_tab3 = True
            st.rerun()

    # --- ENCAPSULATION DU COMPTE-RENDU APRES VERROUILLAGE SECURISE ---
    if st.session_state.get("hyd_verrouille_tab3", False):
        scr1 = st.session_state.get("score_hyd3_p1", 0.0)
        scr2 = st.session_state.get("score_hyd3_p2", 0.0)
        tot_s = st.session_state.get("score_final_hyd3", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        timestamp_hyd3 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER HYDRAZINE 3 SCELLE | Note de session : {tot_s} / 20")

        # --- RECONSTITUTION COMPLETE ET EXPORTATION HTML DU RAPPORT ---
        html_export_hyd3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Mission Hydrazine 3 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #3b82f6; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e3a8a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport de Qualification Ergols</h1>
                <p>Atelier 3 : Validation Metrologique et Calcul Theorique de Purete</p>
                <p>Ingenieur : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Mission : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_hyd3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Compose : Hydrazine ($N_2H_4$) | Titrant : Acide Chlorhydrique ($HCl$) : {c_acide_session:.2f} mol/L</div>
            <div class="sub-title">Recapitulatif des Notes Generees (V_eq releve = {v_eq_session:.2f} mL)</div>

            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #3b82f6;">
                &bull; Note obtenue au Bloc Exploitation (Becher) : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue au Bloc Conteneur d'Ergols : <strong>{scr2} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU BLOC BLEU (EXPLOITATION DANS LE BECHER)</div>
            <table>
                <thead>
                    <tr><th>Grandeur demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr><td>Volume equivalent en Litres (L)</td><td>{st.session_state.get("at3_v_eq_l", 0.0):.5f}</td><td>{v_eq_litre_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001 else "INCORRECT"}</td></tr>
                    <tr><td>Quantite d'acide versee (mol)</td><td>{st.session_state.get("at3_n_acide", 0.0):.5f}</td><td>{n_acide_equiv_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_acide", 0.0) - n_acide_equiv_ref) < 0.0001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_acide", 0.0) - n_acide_equiv_ref) < 0.0001 else "INCORRECT"}</td></tr>
                    <tr><td>Quantite d'hydrazine dosee (mol)</td><td>{st.session_state.get("at3_n_base_becher", 0.0):.5f}</td><td>{n_base_becher_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_base_becher", 0.0) - n_base_becher_ref) < 0.0001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_base_becher", 0.0) - n_base_becher_ref) < 0.0001 else "INCORRECT"}</td></tr>
                    <tr><td>Concentration molaire fille (mol/L)</td><td>{st.session_state.get("at3_c_molaire_fille", 0.0):.3f}</td><td>{c_hydrazine_fille_ref:.3f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_c_molaire_fille", 0.0) - c_hydrazine_fille_ref) < 0.01 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_c_molaire_fille", 0.0) - c_hydrazine_fille_ref) < 0.01 else "INCORRECT"}</td></tr>
                    <tr><td>Masse d'hydrazine dosee (g)</td><td>{st.session_state.get("at3_m_base_gramme", 0.0):.4f}</td><td>{m_hydrazine_becher_ref:.4f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_m_base_gramme", 0.0) - m_hydrazine_becher_ref) < 0.01 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_m_base_gramme", 0.0) - m_hydrazine_becher_ref) < 0.01 else "INCORRECT"}</td></tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement du compte-rendu scellé
        st.download_button(
            label="TELECHARGER LE COMPTE-RENDU TECHNIQUE COMPLET (HTML)",
            data=html_export_hyd3,
            file_name=f"Rapport_Aerospatial_Hydrazine_Atelier3_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )








