# -*- coding: utf-8 -*-

import streamlit as st

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
import pandas as pd
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage du vinaigre")
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
import streamlit.components.v1 as components

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


def afficher_questions_bouteille_commerciale(verrouille=False):
    import numpy as np
    import streamlit as st

    # Récupération des données de session calculées au préalable
    C_base = st.session_state.get("c_base", 0.1)
    v_eq_theorique = st.session_state.get("vin_vrai_veq_calc", 12.0)
    V_ini = 10.0  
    M_vinaigre = 60.0  
    facteur_dilution = 10.0
    V_fiole = 100.0  

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    dict_reponses_bouteille = {}

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='margin-top:0; font-weight:bold; color:#0284c7;'>EXPLOITATION DU DOSAGE DANS LE BÉCHER</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume équivalent en litre :")
    with c2: dict_reponses_bouteille["v_eq_l"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_v_eq_l", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer le nombre de mole de soude versée :")
    with c4: dict_reponses_bouteille["n_soude"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_soude", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En déduire le nombre de mole de vinaigre dosée :")
    with c6: dict_reponses_bouteille["n_acide_becher"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide_becher", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en vinaigre dosée en mol/L :")
    with c8: dict_reponses_bouteille["c_molaire_fille"] = st.number_input("", min_value=0.000, max_value=10.000, format="%.3f", key="at3_c_molaire_fille", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse de vinaigre dosée en gramme :")
    with c10: dict_reponses_bouteille["m_acide_gramme"] = st.number_input("", min_value=0.0000, max_value=100.0000, format="%.4f", key="at3_m_acide_gramme", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En déduire la masse de vinaigre dosée en milligramme :")
    with c12: dict_reponses_bouteille["m_acide_mg"] = st.number_input("", min_value=0.0, max_value=10000.0, format="%.1f", key="at3_m_acide_mg", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique de vinaigre dosée en g/L :")
    with c14: dict_reponses_bouteille["c_massique_fille"] = st.number_input("", min_value=0.00, max_value=500.00, format="%.2f", key="at3_c_massique_fille", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique de vinaigre dosée en mg/L :")
    with c16: dict_reponses_bouteille["c_massique_fille_mg"] = st.number_input("", min_value=0.0, max_value=500000.0, format="%.1f", key="at3_c_massique_fille_mg", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : REMONTÉE À LA BOUTEILLE COMMERCIALE ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='margin-top:0; font-weight:bold; color:#ca8a04;'>REMONTÉE À LA BOUTEILLE COMMERCIALE</p>", unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Donner le rapport de dilution :")
    with c18: dict_reponses_bouteille["rapport_dilution"] = st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_rapport_dilution", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("En déduire le nombre de mole de vinaigre dans la fiole :")
    with c20: dict_reponses_bouteille["n_acide_fiole"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide_fiole", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En déduire le nombre de mole de vinaigre dans la bouteille :")
    with c22: dict_reponses_bouteille["n_acide_bouteille"] = st.number_input("", min_value=0.00000, max_value=5.00000, format="%.5f", key="at3_n_acide_bouteille", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c23: st.write("Calculer la concentration molaire en vinaigre de la bouteille en mol/L :")
    with c24: dict_reponses_bouteille["c_molaire_mere"] = st.number_input("", min_value=0.00, max_value=20.00, format="%.2f", key="at3_c_molaire_mere", disabled=verrouille, label_visibility="collapsed")

    c25, c26 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c25: st.write("Calculer la masse de vinaigre dans la bouteille en gramme :")
    with c26: dict_reponses_bouteille["m_mere_gramme"] = st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_m_mere_gramme", disabled=verrouille, label_visibility="collapsed")

    c27, c28 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c27: st.write("En déduire la masse de vinaigre dans la bouteille en milligramme :")
    with c28: dict_reponses_bouteille["m_mere_mg"] = st.number_input("", min_value=0.0, max_value=1000000.0, format="%.1f", key="at3_m_mere_mg", disabled=verrouille, label_visibility="collapsed")

    c29, c30 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c29: st.write("Calculer la concentration massique de vinaigre de la bouteille en g/L :")
    with c30: dict_reponses_bouteille["c_massique_mere"] = st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_c_massique_mere", disabled=verrouille, label_visibility="collapsed")

    c31, c32 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c31: st.write("En déduire le degré de votre vinaigre :")
    with c32: dict_reponses_bouteille["c_massique_mere_mg"] = st.number_input("", min_value=0.0, max_value=1000000.0, format="%.1f", key="at3_c_massique_mere_mg", disabled=verrouille, label_visibility="collapsed")

    c33, c34 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c33: st.write("Conclure sur l'affichage de la bouteille :")
    with c34: dict_reponses_bouteille["conclusion_bouteille"] = st.selectbox("", ["Choisir...", "Le vinaigre est conforme a l'étiquette (8°)", "Le vinaigre n'est pas conforme"], key="at3_conclusion_bouteille", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    return dict_reponses_bouteille

def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Récupération sécurisée des constantes calculées par le moteur de paillasse
    v_eq_attendu = st.session_state.get("vin_vrai_veq_calc", 12.0)
    c_base_session = st.session_state.get("c_base", 0.1)
    v_acide_dosé = 10.0 # Volume initial d'acide Va mis dans le bécher

    # Calcul des moles de soude versées à l'équivalence pour le corrigé automatique : n = Cb * Ve
    n_soude_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # À l'équivalence n_acide = n_base car les coefficients stœchiométriques valent 1
    c_vinaigre_dose_attendu = (c_base_session * v_eq_attendu) / v_acide_dosé

    col_double_quiz_vin, col_double_trous_vin = st.columns(2)

    sfx = f"_v{int(st.session_state.get('v_verse', 0.0) * 10)}"

    with col_double_quiz_vin:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.2f} mol/L", "1.00 mol/L", "0.50 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de soude ($C_b$) utilisee ?")
        # RÉPARATION : Ajout du suffixe _tab2 unique
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_vin_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_acide_dosé:.1f} mL", "20.0 mL", "25.0 mL"]
        st.write("**2.** Quel volume de solution titrée de vinaigre dilué ($V_a$) a été introduit dans le bécher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_vin_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.2f} mL", "10.00 mL", "15.00 mL"]
        st.write("**3.** Quel est le volume équivalent exact ($V_E$) de soude versé ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_vin_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation entre Ca , Cb , Va , Vb à l'équivalence ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Ca * Va = Cb * Ve", "Ca * Cb = Va * Ve", "Ca / Va = Cb / Ve"], key="col_g_quiz_vin_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_soude_equiv:.5f} mol", f"{n_soude_equiv * 10:.5f} mol", "0.00100 mol"]
        st.write("**5.** Quelle quantite de matiere d'ions hydroxyle $HO^-$ a ete versee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_vin_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_vinaigre_dose_attendu:.3f} mol/L", "0.010 mol/L", "0.100 mol/L"]
        st.write("**6.** Déduisez-en la concentration molaire molaire ($C_a$) du vinaigre dosé dans le bécher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_vin_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_vin:
        st.markdown("##### Synthèse de cours (Texte à trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduée utilisée pour verser la solution titrante est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette","Eprouvette graduée", "Pipette graduee"], key="vin_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prélever les 10 mL de vinaigre de manière précise, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugée", "Eprouvette graduée", "Burette graduée"], key="vin_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour convertir le volume équivalent de mL en Litres, on doit l")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "diviser par 10", "multiplier par 10"], key="vin_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. A l'équivalence, le nombre de moles d'acide et le nombre de moles de base sont")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Egaux", "Doubles", "Inverses"], key="vin_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. L'équivalence est obtenue au ")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...","Au début du dosage", "Au saut de pH", "A la fin du dosage"], key="vin_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_vinaigre1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "vin_verrouille_tab1" not in st.session_state:
        return {}, {}

    # Initialisation et melange unique obligatoire de vos 7 questions d'origine + 3 completes
    if "ordre_quiz1" not in st.session_state:
        base_quiz1 = [
            {"id": "q1_1", "q": "La molécule du vinaigre est :", "type": "menu", "options": ["acide", "neutre", "basique"], "rep": "acide"},
            {"id": "q1_2", "q": "Calculer la masse molaire moléculaire du vinaigre en g/mol: ", "type": "menu", "options": ["60", "46", "29"], "rep": "60"},
            {"id": "q1_3", "q": "Quel est le nom chimique de la molécule du vinaigre ?", "type": "menu", "options": ["acide acétique", "acide méthanoïque", "acide chlorhydrique"], "rep": "acide acétique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atome de carbone que possède la molecule de vinaigre ?", "type": "menu", "options": ["2", "1", "4"], "rep": "2"},
            {"id": "q1_5", "q": "Quel est le nombre d'atome d'hydrogène que possede la molécule de vinaigre ?", "type": "menu", "options": ["4", "2", "6"], "rep": "4"},
            {"id": "q1_6", "q": "Quel est le nombre d'atome d''oxygène que possède la molécule de vinaigre ?", "type": "menu", "options": ["2", "1", "3"], "rep": "2"},
            {"id": "q1_7", "q": "Quelle est la formule brute de vinaigre ?", "type": "menu", "options": ["C4H2O2", "C2H4O2", "C2H2O4", "C2H2O2"], "rep": "C2H4O2"},
            {"id": "q1_8", "q": "D'après la légende atomique, quelle est la masse molaire de l'élément Carbone (C) ?", "type": "menu", "options": ["12 g/mol", "1 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "D'après la légende atomique, quelle est la masse molaire de l'élément Oxygène (O) ?", "type": "menu", "options": ["16 g/mol", "12 g/mol", "1 g/mol"], "rep": "16 g/mol"},
            {"id": "q1_10", "q": "D'après la légende atomique, la sphere blanche représente l'atome d' :", "type": "menu", "options": ["Hydrogène (H)", "Carbone (C)", "Oxygène (O)"], "rep": "Hydrogène (H)"}
        ]
        # Sauvegarde du melange obligatoire en session
        copie_base = list(base_quiz1)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1 = copie_base

    col_double_quiz_v1, col_double_trous_v1 = st.columns(2)

    # --- COLONNE DE GAUCHE : L'ORDRE DES 10 QUESTIONS ME LANGÉES ---
    with col_double_quiz_v1:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vin_cl_g_{q_data['id']}"
            
            # Melange local des options pour eviter l'ordre fixe des propositions
            cle_shuff_opts = f"opts_shuff_{q_data['id']}"
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

    # --- COLONNE DE DROITE : LES 10 TROUS DE SYNTHÈSE ASSOCIES ---
    with col_double_trous_v1:
        st.markdown("##### Synthèse des propriétés acido-basiques (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le vinaigre commercial est une solution aqueuse d'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Ethanoique", "Méthanoique"], key="vin_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le pKa signifie que  ")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...",  "L 'acide est fort", "L'acide est faible","La base est forte", "La base est faible"], key="vin_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'acide acetique appartient à la categorie des acides")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Faibles", "Forts"], key="vin_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La fin de la réaction est caractérisé par ")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Le changement de couleur dans le bécher", "Le changement de couleur dans la burette"], key="vin_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le pKa du couple de l'acide acetique a 25°C vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "4.8", "7.0", "9.2"], key="vin_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'espèce chimique titrante employée dans la burette est la")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Soude", "Acide"], key="vin_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La soude est ")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Une base", "Un acide"], key="vin_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. L'unite internationale de la concentration molaire est")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "mol/L", "g/mol", "g/L"], key="vin_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le virage de couleur de l'indicateur signale l'")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Equivalence", "Dissociation"], key="vin_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide fait tendre sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7.0", "0.0", "14.0"], key="vin_t10_s1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Atelier 1 : Généralités sur le vinaigre")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Document d'étude")
        
        texte_document = (
            "Le vinaigre est une solution aqueuse composée majoritairement d'acide acétique appelé également acide éthanoïque qui est un acide faible caractérisé par son pKa de 4,8. "
            "C'est un produit naturel et biodégradable issu de la biotransformation de l'alcool éthylique "
            "present dans les vins ou les cidres. La dénomination vinaigre est réservée au produit obtenu "
            "exclusivement par le procedé biologique de la double fermentation, alcoolique et acétique, "
            "de denrées et boissons d'origine agricole ou de leurs dilutions aqueuses (Décret n°88-1207 du 30 décembre 1988). "
            "Le degré d’acidité d’un vinaigre, indique sur la bouteille, represente l’acidité totale rapportée "
            "à la masse d’acide acétique exprimée en grammes pour 100 grammes de vinaigre."
        )
        st.info(texte_document)
        
        # Rendu graphique de la bouteille 2D via Matplotlib
        fig_bouteille, ax = plt.subplots(figsize=(4, 5.2), facecolor="#bae6fd")
        ax.set_facecolor("#bae6fd")
        
        bouchon = patches.Rectangle((4, 8.5), 2, 0.8, color="#d0d8dc", ec="#b0bec5")
        col = patches.Polygon([[4.2, 8.5], [5.8, 8.5], [6.5, 7], [3.5, 7]], color="white", ec="#b0bec5")
        corps = patches.Rectangle((2.5, 1), 5, 6, color="white", ec="#b0bec5")
        etiquette = patches.Rectangle((2.7, 1.5), 4.6, 4, color="#008040")
        logo_fond = patches.Rectangle((4.2, 2.2), 1.6, 1.2, color="#0033cc")
        
        ax.add_patch(patches.Circle((5, 1), 2.5, color="white", ec="white"))
        ax.add_patch(corps)
        ax.add_patch(col)
        ax.add_patch(bouchon)
        ax.add_patch(etiquette)
        ax.add_patch(logo_fond)
        
        for y in np.linspace(1.2, 6.8, 8):
            ax.plot([2.55, 7.45], [y, y], color="#e2e8f0", linewidth=1)
            
        ax.text(5, 5.0, "VINAIGRE", color="white", weight="bold", fontsize=14, ha="center")
        ax.text(5, 4.5, "D'ALCOOL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 4.1, "CRISTAL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 3.0, "Eco", color="white", weight="bold", fontsize=12, ha="center")
        ax.text(5, 2.5, "+", color="#ffcc00", weight="bold", fontsize=14, ha="center")
        ax.text(3.3, 2.0, "8°", color="white", weight="bold", fontsize=11, ha="center")
        ax.text(6.7, 2.0, "1 L", color="white", weight="bold", fontsize=11, ha="center")
        
        ax.set_xlim(1, 9)
        ax.set_ylim(0, 10)
        ax.axis("off")
        st.pyplot(fig_bouteille)

    # --------------------------------------------------------
    # COLONNE DROITE : LES DONNÉES ATOMIQUES ET LA MOLÉCULE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Données et Légendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphère noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        c_methyl = np.array([2.8, 2.5])
        c_carboxy = np.array([4.2, 2.5])
        double_o = np.array([4.6, 3.4])
        oh_o = np.array([5.1, 1.9])
        oh_h = np.array([5.9, 1.7])
        h1_m = np.array([2.3, 3.5])
        h2_m = np.array([2.3, 1.5])
        h3_m = np.array([3.2, 3.6])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        tracer_liaison(c_methyl, c_carboxy)
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)
        tracer_liaison(c_carboxy, double_o, double=True)
        tracer_liaison(c_carboxy, oh_o)
        tracer_liaison(oh_o, oh_h)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, texte_couleur = "#2b3e50", "white"
            elif symbole == 'O': couleur, texte_couleur = "#e74c3c", "white"
            elif symbole == 'H': couleur, texte_couleur = "#ecf0f1", "black"
            else: couleur, texte_couleur = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        tracer_atome(c_methyl, 'C')
        tracer_atome(c_carboxy, 'C')
        tracer_atome(double_o, 'O')
        tracer_atome(oh_o, 'O')
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')
        tracer_atome(oh_h, 'H')

        ax_mol.set_xlim(1.5, 6.5)
        ax_mol.set_ylim(1.0, 4.2)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    # =========================================================================
    # LOGIQUE DE COUPLAGE DES CONFIGURATIONS DE NOTATION DYNAMIQUES
    # =========================================================================
    res_q1, res_t1 = afficher_questions_vinaigre1_dynamiques(
        verrouille=st.session_state.vin_verrouille_tab1
    )

    st.write("---")
    st.subheader("Généralité sur le vinaigre")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir completé les questions.", 
        key="check_certif_vin1", 
        disabled=st.session_state.vin_verrouille_tab1
    )

    verrou_vin1 = st.session_state.get("vin_verrouille_tab1", False)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_vin1_official_net", use_container_width=True, disabled=verrou_vin1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique adaptative liée à l'ordre mélangé du Quiz 1
            score_q1 = 0.0
            if "ordre_quiz1" in st.session_state:
                for q_item in st.session_state.ordre_quiz1:
                    reponse_eleve = st.session_state.get(f"vin_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite
            score_t1 = sum([
                st.session_state.get("vin_t1_s1") == "Ethanoique",
                st.session_state.get("vin_t2_s1") == "L'acide est faible",
                st.session_state.get("vin_t3_s1") == "Faibles",
                st.session_state.get("vin_t4_s1") == "Le changement de couleur dans le bécher",
                st.session_state.get("vin_t5_s1") == "4.8",
                st.session_state.get("vin_t6_s1") == "Soude",
                st.session_state.get("vin_t7_s1") == "Une base",
                st.session_state.get("vin_t8_s1") == "mol/L",
                st.session_state.get("vin_t9_s1") == "Equivalence",
                st.session_state.get("vin_t10_s1") == "7.0"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER VINAIGRE 1 SCELLE | Note de session : {tot_s} / 20")

        # --- COMPILATION DU RAPPORT CHIMIQUE HTML DE L'ATELIER 1 ---
        html_export_vin1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vinaigre 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Preparation de la solution fille de vinaigre</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Nomenclature Moléculaire : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue a la Synthese des proprietes : <strong>{scr2} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1, 1):
                saisie = st.session_state.get(f"vin_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_vin1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vin1 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enoncé de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous1 = [
            "1. Le vinaigre commercial est une solution aqueuse d'acide",
            "2. Le pKa signifie que",
            "3. L'acide acétique appartient à la catégorie des acides",
            "4. La fin de la réaction est caractérisé par",
            "5. Le pKa du couple de l'acide acétique a 25°C vaut",
            "6. L'espèce chimique titrante employée dans la burette est la",
            "7. La soude est",
            "8. L'unité internationale de la concentration molaire est",
            "9. Le virage de couleur de l'indicateur signale l'",
            "10. Diluer une solution acide fait tendre sa valeur de pH vers"
        ]
        attendus_trous1 = ["Ethanoique", "L'acide est faible", "Faibles", "Le changement de couleur dans le bécher", "4.8", "Soude", "Une base", "mol/L", "Equivalence", "7.0"]
        
        for num in range(1, 11):
            saisie = st.session_state.get(f"vin_t{num}_s1", "Choisir...")
            attendu = attendus_trous1[num-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin1 += f"<tr><td>{num}</td><td>{phrases_trous1[num-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vin1 += f"""
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de synthese nomenclature genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Vinaigre1_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: nom_f1 = nom_f1.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_vin1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )










with tab2:
    st.header("Dosage colorimétrique du vinaigre")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage de l'acide acétique par la soude")

    # Initialisation des etats de session specifiques a l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "c_base" not in st.session_state: st.session_state.c_base = 0.1
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(80.0, 90.0) / 1000.0

    # Constantes physico-chimiques fixes du modele
    pKa = 4.75
    M_vinaigre = 60.0
    V_ini = 10.0
    v_max_ml = 25.0
    C_base = st.session_state.c_base
    n_acide_ini = st.session_state.masse_reelle_g / M_vinaigre

    # Calcul exact des reperes d'equivalence de la session
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        import math
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-à-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            # Correction : Utilisation exclusive de c_base_vitc pour détruire le KeyError
            C_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :",
                min_value=0.001, max_value=2.0, value=float(st.session_state.c_base_vitc), step=0.001,
                format="%.3f",
                disabled=st.session_state.vin_verrouille_tab2, key="c_base_vitc"
            )
            
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :",
                min_value=0.1, max_value=2.0, value=float(st.session_state.pas_ml), step=0.1,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_slider_pas_ml"
            )
            
        with col_p3:
            liste_indicateurs = list(st.session_state.indicateurs.keys())
            choix_ind = st.selectbox(
                "Sélectionner un indicateur coloré :",
                options=liste_indicateurs, index=0,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_select_ind_colore"
            )



    st.info(f"Compose : Vinaigre | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L")
    st.divider()

    v_eq_affiche = locals().get('v_eq_theorique', globals().get('v_eq_theorique', 12.5))
    ph_eq_affiche = locals().get('ph_eq_theorique', globals().get('ph_eq_theorique', 8.2))

    # 2. LECTURE DES COULEURS DE L'INDICATEUR
    nom_indicateur_choisi = st.session_state.get("c_base_asp", list(st.session_state.indicateurs.keys())[0])
    ind_data = st.session_state.indicateurs.get(nom_indicateur_choisi, list(st.session_state.indicateurs.values())[0])
    c_acide = ind_data["couleur_acide"]
    c_zone = ind_data["couleur_zone"]
    c_base = ind_data["couleur_base"]

    # 3. CRÉATION DU COMPOSANT GRAPHIQUE
    html_animation_paillasse = f"""
    <div style="text-align: center; font-family: sans-serif;">
        <div style="margin-bottom: 12px;">
            <button id="btn-start" style="padding: 6px 16px; background: #22c55e; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Demarrer</button>
            <button id="btn-pause" style="padding: 6px 16px; background: #eab308; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Pause</button>
            <button id="btn-clear" style="padding: 6px 16px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">Effacer</button>
        </div>
        <canvas id="paillasse_canvas" width="260" height="380" style="background: white; border: 1px solid #cbd5e1; border-radius: 8px;"></canvas>
        <div id="zone-bilan" style="margin-top: 10px; padding: 8px; border-radius: 6px; background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; font-size: 11px; font-weight: bold; display: none;">
        </div>
    </div>

    <script>
        const canvas = document.getElementById('paillasse_canvas');
        const ctx = canvas.getContext('2d');
        
        let vVerse = {st.session_state.v_verse};
        const vMax = {v_max_ml};
        v_eq = st.session_state.get("vin_vrai_veq_calc", 12.0)
        const pas = {st.session_state.pas_ml};
        let isRunning = false;
        let tick = 0;

        const colorAcide = "{c_acide}";
        const colorZone = "{c_zone}";
        const colorBase = "{c_base}";

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

            // 2. Burette Graduée
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(140, 50, 20, 160); 
            
            let hauteurBurette = 156 * (1 - (vVerse / vMax));
            let yLiquideHaut = 51.5 + (156 - hauteurBurette);
            
            ctx.fillStyle = 'rgba(186, 230, 253, 0.85)';
            ctx.fillRect(141.5, yLiquideHaut, 17, hauteurBurette);

            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 0.8;
            for (let y = 60; y < 200; y += 15) {{
                ctx.beginPath(); ctx.moveTo(140, y); ctx.lineTo(145, y); ctx.stroke();
            }}

            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(146, 210, 8, 15);

            // Volume en direct
            ctx.fillStyle = '#0284c7';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText(vVerse.toFixed(1) + ' mL', 165, yLiquideHaut + 4);

            // Goutte en chute
            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 232 : 258;
                ctx.fillStyle = '#38bdf8';
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

            // 4. Bécher Gradué
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(105, 230); ctx.lineTo(105, 310); ctx.lineTo(205, 310); ctx.lineTo(205, 230);
            ctx.stroke();

            let couleurSol = colorAcide; 
            let nomTeinte = 'Acide';
            if (Math.abs(vVerse - vEq) <= 0.4) {{
                couleurSol = colorZone; 
                nomTeinte = 'Équivalence';
            }} else if (vVerse > vEq) {{
                couleurSol = colorBase; 
                nomTeinte = 'Basique';
            }}

            let hauteurLiq = 15 + (45 * (vVerse / vMax));
            ctx.fillStyle = couleurSol;
            ctx.fillRect(106, 309 - hauteurLiq, 98, hauteurLiq);

            // Barreau aimanté
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 0.8;
            ctx.save();
            ctx.translate(150, 302);
            ctx.rotate((tick % 2 === 0 ? 15 : -15) * Math.PI / 180);
            ctx.fillRect(-14, -2.5, 28, 5);
            ctx.strokeRect(-14, -2.5, 28, 5);
            ctx.restore();

            // 5. Sonde pH-métrique
            ctx.fillStyle = '#34495e';
            ctx.fillRect(182, 210, 12, 85); 
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(188, 210); ctx.lineTo(188, 170); ctx.lineTo(215, 170); ctx.stroke(); 

            // 6. Boîtier pH-mètre
            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(215, 140, 42, 45);
            
            ctx.fillStyle = '#2ecc71';
            ctx.font = 'bold 9px monospace';
            let txtPh = (vVerse === 0) ? '--' : (3.2 + (vVerse * 0.35)).toFixed(2);
            ctx.fillText('pH: ' + txtPh, 217, 166);

            ctx.fillStyle = '#334155';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText('Teinte : ' + nomTeinte, 150, 365);

            setTimeout(() => {{
                requestAnimationFrame(drawScene);
            }}, 500);
        }}

        drawScene();
    </script>
    """
    # --- 3. RENDU FINAL DU COMPOSANT DANS STREAMLIT ---
    components.html(html_animation_paillasse, height=460)
    if st.button("AFFICHER LES RÉSULTATS DU TITRAGE", key="btn_sync_paillasse_final", use_container_width=True):
        # On force Streamlit à enregistrer que la burette a terminé sa course
        st.session_state.v_verse = v_max_ml
        st.rerun()

    # --- BANDEAU DE RÉSULTATS PYTHON (Celui validé tout à l'heure) ---
    v_eq_affiche = locals().get('v_eq_theorique', globals().get('v_eq_theorique', 14.20))
    ph_eq_affiche = locals().get('ph_eq_theorique', globals().get('ph_eq_theorique', 8.20))

    texte_resultats = (
        f"Reperes d'equivalence de la session : "
        f"Volume equivalent Veq = {v_eq_affiche:.2f} mL | "
        f"pH a l'equivalence pHeq = {ph_eq_affiche:.2f}"
    )
    
    # S'affiche si l'élève a cliqué sur le bouton ou si le questionnaire est validé
    if st.session_state.get("v_verse", 0.0) >= v_max_ml or st.session_state.get("vin_verrouille_tab2", False):
        st.success(texte_resultats)
        
        # Sauvegarde des repères en mémoire pour que l'Atelier 3 puisse les récupérer
        st.session_state["input_at2_ve_lu_eleve"] = v_eq_affiche
        st.session_state["input_at2_phe_lu_eleve"] = ph_eq_affiche
        
    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # Calculs automatiques des veritables attendus pour la correction automatique du bouton
    v_acide_dose = 20.0
    moles_soude_equiv = (C_base * v_eq_theorique) / 1000.0
    concentration_lactique_attendue = (C_base * v_eq_theorique) / v_acide_dose

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)

    # Variables locales pour stocker le retour des fonctions
    dict_reponses_quiz, dict_trous = {}, {}

    # Appel direct et propre sans affectation pour éviter le TypeError
    if not st.session_state.get("animation_active", False):
        try:
            # Correction : Nettoyage de l'argument df_donnees pour eviter le crash
            generer_le_quiz_analytique_atelier_deux(verrouille=verrou_vin2)
        except NameError:
            try:
                afficher_questions_titrage_dynamiques(verrouille=verrou_vin2)
            except:
                pass
    else:
        st.info("Le versement de la soude est en cours... Le formulaire d'evaluation s'affichera des que l'animation sera terminee.")

    # Profil étudiant et certification
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.", 
        key="check_certif_asp2_final_net", 
        disabled=verrou_vin2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_vin2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz Numérique de gauche (6 questions)
            moles_soude_equiv = (C_base * v_eq_theorique) / 1000.0
            concentration_vinaigre_attendue = (C_base * v_eq_theorique) / V_ini

            score_q2 = sum([
                st.session_state.get("col_g_quiz_vin_q1_tab2") == f"{C_base:.5f} mol/L",
                st.session_state.get("col_g_quiz_vin_q2_tab2") == f"{V_ini:.5f} mL",
                st.session_state.get("col_g_quiz_vin_q3_tab2") == f"{v_eq_theorique:.5f} mL",
                st.session_state.get("col_g_quiz_vin_q4_tab2") == "Ca * Va = Cb * Ve",
                st.session_state.get("col_g_quiz_vin_q5_tab2") == f"{moles_soude_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_vin_q6_tab2") == f"{concentration_vinaigre_attendue:.5f} mol/L"
            ]) * (10.0 / 6.0)
            # 2. Correction automatique du Texte à trous de droite (5 cases)
            score_t2 = sum([
                st.session_state.get("vin_t1_tab2") == "Burette",
                st.session_state.get("vin_t2_tab2") == "Pipette jaugée",
                st.session_state.get("vin_t3_tab2") == "diviser par 1000",
                st.session_state.get("vin_t4_tab2") == "Egaux",
                st.session_state.get("vin_t5_tab2") == "Au saut de pH"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)
      
        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER VINAIGRE 2 SCELLE | Note de session : {tot_s} / 20")

        # --- COMPILATION DU RAPPORT CHIMIQUE HTML DE L'ATELIER 2 ---
        html_export_vin2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vinaigre 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                .img-container {{ text-align: center; margin: 25px 0; background: white; padding: 15px; border-radius: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                .img-container img {{ max-width: 100%; height: auto; border: 1px solid #cbd5e1; }}
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
                <p>Atelier 2 : Dosage colorimetrique du vinaigre</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de suivi de titrage : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours : <strong>{scr2} / 10</strong><br>
                &bull; Note Finale de l'Atelier 2 : <strong>{tot_s} / 20</strong>
            </p>
            <div class="sub-title">Compose : Vinaigre | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L</div>

            <div class="sub-title">SAUVEGARDE GÉOMÉTRIQUE DE VOTRE COURBE EXPERIMENTALE</div>
            <div class="img-container">
                <img src="data:image/png;base64,{base64_image_courbe}" alt="Courbe de suivi eleve">
            </div>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        moles_soude_ref = (C_base * v_eq_theorique) / 1000.0
        concentration_vinaigre_ref = (C_base * v_eq_theorique) / V_ini

        attendus_quiz2 = [
            f"{C_base:.2f} mol/L", 
            f"{V_ini:.1f} mL", 
            f"{v_eq_theorique:.2f} mL", 
            "Ca * Va = Cb * Ve", 
            f"{moles_soude_ref:.5f} mol", 
            f"{concentration_vinaigre_ref:.3f} mol/L"
        ]
        questions_text2 = [
            "1. Quelle est la concentration molaire de la solution titrante de soude (Cb) utilisee ?",
            "2. Quel volume de solution titrée de vinaigre dilué (Va) a été introduit dans le bécher ?",
            "3. Quel est le volume équivalent exact (VE) de soude versé ?",
            "4. Quelle est la relation entre Ca , Cb , Va , Vb à l'équivalence ?",
            "5. Quelle quantite de matiere d'ions hydroxyle HO- a ete versee a l'equivalence ?",
            "6. Déduisez-en la concentration molaire molaire (Ca) du vinaigre dosé dans le bécher :"
        ]
        for i in range(1, 7):
            saisie = st.session_state.get(f"col_g_quiz_vin_q{i}_tab2", "Choisir...")
            attendu = attendus_quiz2[i-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin2 += f"<tr><td>{i}</td><td>{questions_text2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vin2 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase complétée</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous2 = [
            "1. La verrerie graduée utilisée pour verser la solution titrante est la",
            "2. Pour prélever les 10 mL de vinaigre de manière précise, on utilise une",
            "3. Pour convertir le volume équivalent de mL en Litres, on doit l",
            "4. A l'équivalence, le nombre de moles d'acide et le nombre de moles de base sont",
            "5. L'équivalence est obtenue au"
        ]
        attendus_trous2 = ["Burette", "Pipette jaugée", "diviser par 1000", "Egaux", "Au saut de pH"]
        for i in range(1, 6):
            saisie = st.session_state.get(f"vin_t{i}_tab2", "Choisir...")
            attendu = attendus_trous2[i-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin2 += f"<tr><td>{i}</td><td>{phrases_trous2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vin2 += f"""
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de paillasse colorimetrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Vinaigre2_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: nom_f2 = nom_f2.replace(c, "_")

        st.download_button(label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_vin2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )





with tab3:
    st.header("Calcul theorique & Verification de la bouteille")
    st.caption("Verification de la conformite du degre d'acidite indique sur l'etiquette reglementaire")

    if "vin_verrouille_tab3" not in st.session_state: st.session_state.vin_verrouille_tab3 = False

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_base", 0.1)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    ph_eq_session = st.session_state.get("input_at2_phe_lu_eleve", 8.7)
    v_titre_session = 10.0
    M_vinaigre = 60.0
    facteur_dilution = 10.0
    V_fiole = 100.0

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les resultats de votre dosage
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On a dilue 10 mL de vinaigre pur dans une fiole de 100 mL a l'aide d'une pipette jaugee. Pour le dosage on a preleve 10 mL de cette solution diluee.
            </div>

        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; pH_eq = {ph_eq_session:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; concentration titrante = {c_base_session:.2f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Volume titre = {v_titre_session:.1f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M = {M_vinaigre:.0f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; n = C x V </p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; m = n x M</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # --- SÉCURITÉ DE NOTATION DE L'ATELIER 3 ---

    v_eq_litre_ref = v_eq_session / 1000.0
    n_soude_equiv_ref = c_base_session * v_eq_litre_ref
    n_acide_becher_ref = n_soude_equiv_ref
    c_acide_fille_ref = n_acide_becher_ref / (v_titre_session / 1000.0)
    m_acide_becher_ref = n_acide_becher_ref * M_vinaigre
    m_acide_becher_mg_ref = m_acide_becher_ref * 1000.0
    c_massique_fille_ref = c_acide_fille_ref * M_vinaigre
    c_massique_fille_mg_ref = c_massique_fille_ref * 1000.0

    n_acide_fiole_ref = c_acide_fille_ref * (V_fiole / 1000.0)
    n_acide_bouteille_ref = n_acide_fiole_ref * facteur_dilution *10
    c_acide_mere_ref = c_acide_fille_ref * facteur_dilution
    m_acide_bouteille_ref = n_acide_bouteille_ref * M_vinaigre
    m_acide_bouteille_mg_ref = m_acide_bouteille_ref * 1000.0
    c_massique_mere_ref = c_acide_mere_ref * M_vinaigre
    degre_bouteille_ref = c_massique_mere_ref / 10.0


    verrou_vin3 = st.session_state.get("vin_verrouille_tab3", False)
    
    dict_reponses_bouteille = afficher_questions_bouteille_commerciale(verrouille=verrou_vin3)

    case_certif_vin3 = st.checkbox("Je certifie avoir complete l'integralite des calculs de l'Atelier 3.", key="check_certif_vin3_net", disabled=st.session_state.get("vin_verrouille_tab3", False))
    
    
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









