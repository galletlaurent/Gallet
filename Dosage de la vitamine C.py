# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de la vitamine C",
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
st.title("Application dosage de la vitamine C")
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
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.05
if "animation_active" not in st.session_state: st.session_state.animation_active = False
if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },

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
    "Généralités sur la vitamine C",
    "Dosage colorimétrique de la vitamine C",
    "Calcul théorique sur l'aspirine et vérification de l'inscription sur la boîte"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

def afficher_questions_vitaminec_commerciale(verrouille=False):
    import streamlit as st

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation du dosage de la vitamine C dans le becher</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume equivalent en litre (L) :")
    with c2: st.text_input("", value="0.0", key="at3_v_eq_l_vitc", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer le nombre de mole de soude versee a l'equivalence (mol) :")
    with c4: st.text_input("", value="0.0", key="at3_n_soude_vitc", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En deduire le nombre de mole de vitamine C dosee dans le becher (mol) :")
    with c6: st.text_input("", value="0.0", key="at3_n_acide_becher_vitc", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en vitamine C de la solution dosee (mol/L) :")
    with c8: st.text_input("", value="0.0", key="at3_c_molaire_fille_vitc", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse de vitamine C dosee dans le becher (g) :")
    with c10: st.text_input("", value="0.0", key="at3_m_acide_gramme_vitc", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En deduire la masse de vitamine C dosee (mg) :")
    with c12: st.text_input("", value="0.0", key="at3_m_acide_mg_vitc", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique en vitamine C de la solution (g/L) :")
    with c14: st.text_input("", value="0.0", key="at3_c_massique_fille_vitc", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique en vitamine C de la solution (mg/L) :")
    with c16: st.text_input("", value="0.0", key="at3_c_massique_fille_mg_vitc", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : REMONTÉE AU COMPRIMÉ COMMERCIAL ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Remontee a la masse du comprime and conformite de l'etiquette</p>", unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Rappel de la masse molaire de la vitamine C pure (g/mol) :")
    with c18: st.text_input("", value="0.0", key="at3_masse_molaire_vitc_vitc", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("Calculer la masse totale de vitamine C contenue dans le comprime entier (g) :")
    with c20: st.text_input("", value="0.0", key="at3_masse_par_comprime_vitc", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En deduire la masse de vitamine C contenue dans le comprime (mg) :")
    with c22: st.text_input("", value="0.0", key="at3_valeur_mg_comprime_vitc", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c23: st.write("Conclure sur la conformite de la masse par rapport a l'etiquette (500 mg) :")
    with c24: st.selectbox(
        "", 
        [
            "Choisir...", 
            "Le comprime est conforme a l'etiquette (Masse de vitamine C proche de 500 mg)", 
            "Le comprime n'est pas conforme a l'etiquette (Ecart trop important)"
        ], 
        key="at3_conclusion_bouteille_vitc", 
        disabled=verrouille, 
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)


def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Recouvrement des constantes calculees du moteur de paillasse pour la vitamine C
    v_eq_attendu = st.session_state.get("vitc_vrai_veq_calc", 14.2)
    c_base_session = st.session_state.get("c_base_vitc", 0.010)
    v_acide_dose = 20.0 # Volume initial de solution de vitamine C Va mis dans le becher

    # Calcul des moles de soude versees a l'equivalence : n = Cb * Ve
    n_soude_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # A l'equivalence n_vitamineC = n_base (reaction mole a mole)
    c_vitc_dose_attendu = (c_base_session * v_eq_attendu) / v_acide_dose

    col_double_quiz_vitc, col_double_trous_vitc = st.columns(2)

    with col_double_quiz_vitc:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de soude ($C_b$) utilisee ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_vitc_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_acide_dose:.1f} mL", "20.0 mL", "25.0 mL"]
        st.write("**2.** Quel volume de solution de vitamine C ($V_a$) a ete introduit dans le becher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_vitc_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume equivalent exact ($V_E$) de soude verse releve sur la courbe ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_vitc_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Ca * Va = Cb * Ve", "Ca * Cb = Va * Ve", "Ca / Va = Cb / Ve"], key="col_g_quiz_vitc_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_soude_equiv:.5f} mol", f"{n_soude_equiv * 10:.5f} mol", "0.01000 mol"]
        st.write("**5.** Quelle quantite de matiere d'ions hydroxyle $HO^-$ a ete apportee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_vitc_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_vitc_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Deduisez-en la concentration molaire ($C_a$) de la vitamine C dans le becher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_vitc_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_vitc:
        st.markdown("##### Synthese de cours (Texte a trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee verifiant l'ajout millilitre par millilitre de soude est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Eprouvette graduee", "Pipette jaugee"], key="vitc_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prelever les 10 mL de solution d'acide de maniere homogene, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugee", "Eprouvette graduee", "Fioles"], key="vitc_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="vitc_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point equivalent, les reactifs acide et basique ont ete introduits dans les proportions")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="vitc_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Sur un suivi pH-metrique d'acide faible, l'equivalence correspond a la rupture du")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Saut de pH", "Palier initial", "Debut du dosage"], key="vitc_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous


def afficher_questions_vitaminec1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_vitc" not in st.session_state:
        base_quiz1_vitc = [
            {"id": "q1_1", "q": "La vitamine C (acide ascorbique) est une molecule possedant des proprietes :", "type": "menu", "options": ["acides", "neutres", "basiques"], "rep": "acides"},
            {"id": "q1_2", "q": "Calculer la masse molaire moleculaire de la vitamine C pure (C6H8O6) en g/mol :", "type": "menu", "options": ["176,12", "180,15", "150,10"], "rep": "176,12"},
            {"id": "q1_3", "q": "Quel est le nom chimique officiel de la molecule de vitamine C ?", "type": "menu", "options": ["acide ascorbique", "acide acetylsalicylique", "acide citrique"], "rep": "acide ascorbique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes de carbone (C) dans un motif de vitamine C ?", "type": "menu", "options": ["6", "9", "4"], "rep": "6"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogene (H) dans un motif de vitamine C ?", "type": "menu", "options": ["8", "6", "4"], "rep": "8"},
            {"id": "q1_6", "q": "Quel est le nombre d'atomes d'oxygene (O) dans un motif de vitamine C ?", "type": "menu", "options": ["6", "4", "3"], "rep": "6"},
            {"id": "q1_7", "q": "Quelle est la formule brute exacte de la vitamine C commerciale ?", "type": "menu", "options": ["C6H8O6", "C9H8O4", "C2H4O2"], "rep": "C6H8O6"},
            {"id": "q1_8", "q": "D'apres la classification atomique, le nombre de masse de l'element C vaut :", "type": "menu", "options": ["12 g/mol", "14 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "Quelle couleur conventionnelle represente l'atome d'oxygene sur les maquettes ?", "type": "menu", "options": ["Rouge", "Noir", "Blanc"], "rep": "Rouge"},
            {"id": "q1_10", "q": "La vitamine C est essentielle au corps humain et agit principalement comme :", "type": "menu", "options": ["Antioxydant et tonique", "Antibiotique", "Analgésique"], "rep": "Antioxydant et tonique"}
        ]
        copie_base = list(base_quiz1_vitc)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_vitc = copie_base

    col_double_quiz_vitc1, col_double_trous_vitc1 = st.columns(2)

    with col_double_quiz_vitc1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_vitc, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vitc_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_vitc_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = opts_copie
            
            opts_affichees = ["Choisir..."] + st.session_state[cle_shuff_opts]
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = opts_affichees.index(val_p) if val_p in opts_affichees else 0
            
            dict_reponses_quiz[q_data["id"]] = st.selectbox(
                "", opts_affichees, index=sel_idx, key=cle_select,
                disabled=verrouille, label_visibility="collapsed"
            )

    with col_double_trous_vitc1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le principe actif contenu dans un comprime de vitamine C est l'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "ascorbique", "acetylsalicylique", "citrique"], key="vitc_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale est")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "C6H8O6", "C9H8O4", "C2H4O2"], key="vitc_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculee a partir de ses elements constitutifs vaut")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "176,12 g/mol", "180,15 g/mol", "60,05 g/mol"], key="vitc_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au sein de son squelette carbone, on compte un total de")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "6 atomes", "9 atomes", "4 atomes"], key="vitc_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre d'atomes d'Hydrogene presents dans la structure vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "8 atomes", "6 atomes", "4 atomes"], key="vitc_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le nombre d'atomes d'Oxygene fixees sur les fonctions de la molecule est de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "6 atomes", "4 atomes", "3 atomes"], key="vitc_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La constante de masse molaire de l'element atomique C est")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "12 g/mol", "1 g/mol", "16 g/mol"], key="vitc_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La constante de masse molaire de l'element oxygene O vaut")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "16 g/mol", "12 g/mol", "1 g/mol"], key="vitc_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Lors de la manipulation de réactifs corrosifs comme la soude, le port de gants est")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Obligatoire", "Facultatif", "Interdit"], key="vitc_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide concentree permet de rapprocher sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7 (neutre)", "0 (acide)", "14 (basique)"], key="vitc_t10_tab1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Atelier 1 : Généralités sur la vitamine C ")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Données et Légendes Atomiques")
        
        # Affichage du bloc textuel descriptif issu de Wikipédia
        st.info(
            "La vitamine C est une vitamine hydrosoluble sensible à la chaleur et à la lumière "
            "jouant un rôle important dans le métabolisme de l'être humain et de nombreux autres mammifères. "
            "Chimiquement parlant, il s'agit de l'acide ascorbique, un des stéréoisomères de l'acide "
            "ascorbique, et de ses sels, les ascorbates. Les plus courants sont l'ascorbate de sodium "
            "et l'ascorbate de calcium. (source : Wikipedia.org)"
        )
            
        st.divider()

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import random

        # Création de la figure Matplotlib pour remplacer le Canvas Tkinter
        fig_box, ax_box = plt.subplots(figsize=(7, 5), facecolor="white")
        ax_box.set_facecolor("white")
        
        # Inversement de l'axe Y pour correspondre au repère Tkinter (0 en haut)
        ax_box.set_ylim(500, 0)
        ax_box.set_xlim(0, 700)

        # 1. Le corps de la boîte (Jaune et Côté Orange)
        ax_box.add_patch(patches.Rectangle((50, 80), 600, 380, facecolor="#ffbf00", edgecolor="#ff8c00", linewidth=2))
        ax_box.add_patch(patches.Rectangle((350, 80), 300, 380, facecolor="#ff8c00", edgecolor="none"))

        # 2. Zone supérieure blanche avec le logo
        ax_box.add_patch(patches.Rectangle((50, 20), 600, 60, facecolor="white", edgecolor="white"))
        
        # Bandes colorées du logo
        y_bandes = 35
        largeur_bande = 25
        espace_bande = 5
        x_start = 180
        couleurs_bandes = ["#00aaff", "#77dd77", "#ff66cc", "#ff9933", "#ff0066"]
        for i, couleur in enumerate(couleurs_bandes):
            x_b = x_start + i * (largeur_bande + espace_bande)
            ax_box.add_patch(patches.Rectangle((x_b, y_bandes), largeur_bande, 5, facecolor=couleur, edgecolor="none"))

        # Texte du logo Juvamine
        ax_box.text(350, 55, "JUVAMINE", fontname="Arial", fontsize=20, weight="bold", color="#000066", ha="center", va="center")
        ax_box.text(335, 32, "LABORATOIRES", fontname="Arial", fontsize=8, color="#000066", ha="center", va="center")

        # 3. Texte Principal "Vitamine C"
        ax_box.text(90, 120, "Vitamine C", fontname="Helvetica", fontsize=40, weight="bold", color="#111111", ha="left", va="center")

        # 4. Cercle "500 mg" bordeaux
        ax_box.add_patch(patches.Ellipse((190, 252.5), 220, 155, facecolor="#cc3333", edgecolor="#cc3333"))
        ax_box.text(190, 250, "500", fontname="Helvetica", fontsize=70, weight="bold", color="white", ha="center", va="center")
        ax_box.text(270, 300, "mg", fontname="Helvetica", fontsize=14, weight="bold", color="white", ha="center", va="center")

        # 5. Zone du bas (Mentions textuelles)
        ax_box.text(90, 400, "Arôme naturel orange", fontname="Arial", fontsize=14, weight="bold", color="#ffffff", ha="left", va="center")
        ax_box.text(90, 425, "Sans Sucres", fontname="Arial", fontsize=14, weight="bold", color="#ffffff", ha="left", va="center")

        # 6. Représentation de l'effervescence
        ax_box.add_patch(patches.Ellipse((515, 310), 170, 120, facecolor="#99ccff", edgecolor="#99ccff"))
        
        # Génération déterministe des bulles pour éviter les clignotements intempestifs sous Streamlit
        random.seed(42)
        for _ in range(30):
            x_b = random.randint(440, 590)
            y_b = random.randint(310, 410)
            rayon_b = random.randint(2, 5)
            ax_box.add_patch(patches.Circle((x_b, y_b), rayon_b, facecolor="white", edgecolor="white"))

        # 7. Petit carton d'information (bas à droite)
        ax_box.add_patch(patches.Rectangle((430, 420), 190, 40, facecolor="#e0e0e0", edgecolor="#e0e0e0"))
        ax_box.text(450, 435, "x30", fontname="Arial", fontsize=18, weight="bold", color="#cc3333", ha="left", va="center")
        ax_box.text(545, 430, "COMPRIMÉS", fontname="Arial", fontsize=8, color="#cc3333", ha="center", va="center")
        ax_box.text(545, 445, "EFFERVESCENTS", fontname="Arial", fontsize=8, weight="bold", color="#cc3333", ha="center", va="center")
        ax_box.text(520, 465, "FABRIQUÉ EN FRANCE", fontname="Arial", fontsize=6, color="#000066", ha="center", va="center")
        
        # Drapeau français simplifié
        ax_box.add_patch(patches.Rectangle((485, 470), 20, 15, facecolor="#0055cc", edgecolor="none"))
        ax_box.add_patch(patches.Rectangle((505, 470), 20, 15, facecolor="white", edgecolor="none"))
        ax_box.add_patch(patches.Rectangle((525, 470), 20, 15, facecolor="#ee3344", edgecolor="none"))

        # 8. Côté droit de la boîte (pli)
        ax_box.add_patch(patches.Rectangle((640, 80), 20, 380, facecolor="#e08000", edgecolor="none"))
        ax_box.plot([650, 650], [90, 450], color="#ffffff", linestyle="--", linewidth=1)
        
        ax_box.axis("off")
        st.pyplot(fig_box)
        st.divider()

    with col_droite:
        st.subheader("Données et Légendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphère noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # --- 1. Coordonnées géométriques des atomes du cycle à 5 sommets ---
        o_cycle = np.array([3.3, 1.9])
        c1 = np.array([4.4, 1.7])
        c2 = np.array([4.5, 2.6])
        c3 = np.array([3.6, 3.0])
        c4 = np.array([3.0, 2.7])

        # --- 2. Coordonnées de la chaîne latérale attachée à C4 ---
        c5 = np.array([2.1, 3.2])
        c6 = np.array([1.3, 2.7])

        # --- 3. Coordonnées des groupements hydroxyles, carbonyle et hydrogènes ---
        o_exo = np.array([5.2, 1.3])
        
        oh_c2 = np.array([5.4, 3.1])
        h_c2 = np.array([6.1, 3.3])

        oh_c3 = np.array([3.6, 4.0])
        h_c3 = np.array([3.6, 4.6])

        h_c4 = np.array([2.7, 3.5])

        oh_c5 = np.array([1.9, 4.1])
        h_oh5 = np.array([1.4, 4.6])
        h_c5 = np.array([2.3, 2.4])

        oh_c6 = np.array([0.7, 3.3])
        h_oh6 = np.array([0.3, 3.7])
        h1_c6 = np.array([1.0, 2.0])
        h2_c6 = np.array([1.6, 2.1])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # --- TRACÉ DES LIAISONS DU CYCLE ---
        tracer_liaison(o_cycle, c1)
        tracer_liaison(c1, c2)
        tracer_liaison(c2, c3, double=True)  # Double liaison caractéristique
        tracer_liaison(c3, c4)
        tracer_liaison(c4, o_cycle)

        # --- TRACÉ DES LIAISONS DES SUBSTITUANTS ---
        tracer_liaison(c1, o_exo, double=True)
        
        tracer_liaison(c2, oh_c2)
        tracer_liaison(oh_c2, h_c2)

        tracer_liaison(c3, oh_c3)
        tracer_liaison(oh_c3, h_c3)

        tracer_liaison(c4, h_c4)

        tracer_liaison(c4, c5)
        tracer_liaison(c5, c6)

        tracer_liaison(c5, oh_c5)
        tracer_liaison(oh_c5, h_oh5)
        tracer_liaison(c5, h_c5)

        tracer_liaison(c6, oh_c6)
        tracer_liaison(oh_c6, h_oh6)
        tracer_liaison(c6, h1_c6)
        tracer_liaison(c6, h2_c6)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, texte_couleur = "#2b3e50", "white"
            elif symbole == 'O': couleur, texte_couleur = "#e74c3c", "white"
            elif symbole == 'H': couleur, texte_couleur = "#ecf0f1", "black"
            else: couleur, texte_couleur = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # --- RENDU DE TOUS LES ATOMES (PAR-DESSUS) ---
        # Atomes de Carbone
        tracer_atome(c1, 'C')
        tracer_atome(c2, 'C')
        tracer_atome(c3, 'C')
        tracer_atome(c4, 'C')
        tracer_atome(c5, 'C')
        tracer_atome(c6, 'C')

        # Atomes d'Oxygène
        tracer_atome(o_cycle, 'O')
        tracer_atome(o_exo, 'O')
        tracer_atome(oh_c2, 'O')
        tracer_atome(oh_c3, 'O')
        tracer_atome(oh_c5, 'O')
        tracer_atome(oh_c6, 'O')

        # Atomes d'Hydrogène
        tracer_atome(h_c2, 'H')
        tracer_atome(h_c3, 'H')
        tracer_atome(h_c4, 'H')
        tracer_atome(h_c5, 'H')
        tracer_atome(h_oh5, 'H')
        tracer_atome(h_oh6, 'H')
        tracer_atome(h1_c6, 'H')
        tracer_atome(h2_c6, 'H')

        ax_mol.set_xlim(-0.2, 6.8)
        ax_mol.set_ylim(0.8, 5.2)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    res_q1, res_t1 = afficher_questions_vitaminec1_dynamiques(
        verrouille=st.session_state.vin_verrouille_tab1
    )

    verrou_vin1 = st.session_state.get("vin_verrouille_tab1", False)

    st.write("---")
    st.subheader("Généralité sur la vitamine C")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_asp1_final_net", 
        disabled=st.session_state.get("vin_verrouille_tab1", False)
    )

    verrou_vin1 = st.session_state.get("vin_verrouille_tab1", False)

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE (ATELIER VITAMINE C 1) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_vin1_official_net", use_container_width=True, disabled=verrou_vin1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz de gauche (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_vitc" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_vitc:
                    reponse_eleve = st.session_state.get(f"vitc_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 cases)
            score_t1 = sum([
                st.session_state.get("vitc_t1_tab1") == "ascorbique",
                st.session_state.get("vitc_t2_tab1") == "C6H8O6",
                st.session_state.get("vitc_t3_tab1") == "176,12 g/mol",
                st.session_state.get("vitc_t4_tab1") == "6 atomes",
                st.session_state.get("vitc_t5_tab1") == "8 atomes",
                st.session_state.get("vitc_t6_tab1") == "6 atomes",
                st.session_state.get("vitc_t7_tab1") == "12 g/mol",
                st.session_state.get("vitc_t8_tab1") == "16 g/mol",
                st.session_state.get("vitc_t9_tab1") == "Obligatoire",
                st.session_state.get("vitc_t10_tab1") == "7 (neutre)"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- SCELLÉ ET COMPILATION DU RAPPORT HTML POUR LA VITAMINE C ---
    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_vitc1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vitamine C 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Etude moleculaire de la vitamine C</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Nomenclature Moleculaire : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue a la Synthese des proprietes : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_vitc" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_vitc, 1):
                saisie = st.session_state.get(f"vitc_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_vitc1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vitc1 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enoncé de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous1 = [
            "1. Le principe actif contenu dans un comprime de vitamine C est l'acide",
            "2. Sa formule de structure brute globale s'ecrit",
            "3. La masse molaire calculee a partir de ses elements constitutifs vaut",
            "4. Au sein de son squelette carbone, on compte un total de",
            "5. Le nombre d'atomes d'Hydrogene presents dans la structure vaut",
            "6. Le nombre d'atomes d'Oxygene repartis sur ses fonctions vaut",
            "7. La constante de masse molaire de l'element atomique C est",
            "8. La constante de masse molaire de l'element oxygene O vaut",
            "9. Lors de la manipulation de réactifs corrosifs comme la soude, le port de gants est",
            "10. Diluer une solution acide concentree permet de rapprocher sa valeur de pH vers"
        ]
        attendus_trous1 = ["ascorbique", "C6H8O6", "176,12 g/mol", "6 atomes", "8 atomes", "6 atomes", "12 g/mol", "16 g/mol", "Obligatoire", "7 (neutre)"]
        
        for num in range(1, 11):
            saisie = st.session_state.get(f"vitc_t{num}_tab1", "Choisir...")
            attendu = attendus_trous1[num-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vitc1 += f"<tr><td>{num}</td><td>{phrases_trous1[num-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vitc1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de synthese genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"VitamineC1_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_vitc1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Dosage colorimétrique de la vitamine C")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage de la vitamine C par la soude")

    # Initialisation des etats de session specifiques a l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "c_base_vitc" not in st.session_state: st.session_state.c_base_vitc = 0.050
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    
    # REPARATION CRITIQUE : Force la creation d'une masse aleatoire differente a chaque session
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(490.0, 510.0) / 1000.0

    # Données physico-chimiques réglementaires de la VITAMINE C (Acide ascorbique)
    v_max_ml = 25.0
    V_ini = 20.0
    pKa = 4.2
    M_vitC = 176  # Masse molaire precise de la vitamine C
    C_base = st.session_state.c_base_vitc
    
    # Calcul exact des moles presentes dans le becher (Fiole de 500mL prélevée à 20mL = Facteur 25)
    n_acide_ini = st.session_state.masse_reelle_g / (M_vitC * 25)



    # --- ZONE DES REGLAGES SUPERIEURS ---
    # Calcul exact des reperes d'equivalence de la session
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        import math
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    v_eq_visuel = v_eq_theorique if v_eq_theorique < v_max_ml else 12.0
    
    # --- ZONE DES REGLAGES SUPERIEURS (DOUBLON SUPPRIMÉ ET SÉCURISÉ) ---
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

    # Mise à jour du texte de description pour afficher Vitamine C au lieu d'Aspirine
    st.info(f"Compose : Vitamine C | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L")
    st.divider()


    v_eq_affiche = locals().get('v_eq_theorique', globals().get('v_eq_theorique', 12.5))
    ph_eq_affiche = locals().get('ph_eq_theorique', globals().get('ph_eq_theorique', 8.2))

    # --- GRANDE CHAÎNE HTML/JS DE LA PAILLASSE ---
    ind_data = st.session_state.indicateurs[choix_ind]
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
        const vEq = {v_eq_visuel};
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

    # --- 1. SÉCURISATION DES VARIABLES COMPATIBLES AVEC LE QUIZ ---
    v_eq_theorique = st.session_state.get("vitc_vrai_veq_calc", 14.2)
    C_base = st.session_state.get("c_base_vitc", 0.00)
    v_acide_dose = 20.0

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)

    # --- 2. APPEL DIRECT ET PROPRE SANS DOUBLONS DE CLÉS (Ligne 1092 nettoyée) ---
    if not st.session_state.get("animation_active", False):
        try:
            # Nettoyage complet : On retire 'df_donnees=None' pour éviter le TypeError
            generer_le_quiz_analytique_atelier_deux(verrouille=verrou_vin2)
        except NameError:
            try:
                afficher_questions_titrage_dynamiques(verrouille=verrou_vin2)
            except:
                pass
    else:
        st.info("Le versement de la soude est en cours... Le formulaire d'évaluation s'affichera dès que l'animation sera terminée.")
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

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_vin2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Attendus théoriques pour la Vitamine C
            n_soude_equiv = (C_base * v_eq_theorique) / 1000.0
            c_vitc_dose_attendu = (C_base * v_eq_theorique) / v_acide_dose

            # 1. Correction du Quiz (sur 10 points)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_vitc_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_vitc_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_vitc_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_vitc_q4_tab2") == "Ca * Va = Cb * Ve",
                st.session_state.get("col_g_quiz_vitc_q5_tab2") == f"{n_soude_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_vitc_q6_tab2") == f"{c_vitc_dose_attendu:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction de la Synthèse de cours (sur 10 points)
            score_t2 = sum([
                st.session_state.get("vitc_t1_tab2") == "Burette",
                st.session_state.get("vitc_t2_tab2") == "Pipette jaugée",
                st.session_state.get("vitc_t3_tab2") == "diviser par 1000",
                st.session_state.get("vitc_t4_tab2") == "stoechiometriques",
                st.session_state.get("vitc_t5_tab2") == "Saut de pH"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU RAPPORT HTML PROPRE ET SYNCHRONISÉ ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_vitc2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vitamine C 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Dosage de la solution de vitamine C</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de suivi de titrage : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Finale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">Compose : Acide ascorbique | Soude titrante : {C_base:.3f} mol/L</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead><tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        n_soude_ref = (C_base * v_eq_theorique) / 1000.0
        c_vitc_ref = (C_base * v_eq_theorique) / v_acide_dose

        attendus_quiz2 = [
            f"{C_base:.3f} mol/L", 
            f"{v_acide_dose:.1f} mL", 
            f"{v_eq_theorique:.1f} mL", 
            "Ca * Va = Cb * Ve", 
            f"{n_soude_ref:.5f} mol", 
            f"{c_vitc_ref:.4f} mol/L"
        ]
        
        questions_text2 = [
            "1. Quelle est la concentration molaire de la solution titrante de soude (Cb) utilisee ?",
            "2. Quel volume de solution de vitamine C (Va) a ete introduit dans le becher ?",
            "3. Quel est le volume equivalent exact (VE) de soude verse releve sur la courbe ?",
            "4. Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?",
            "5. Quelle quantite de matiere d'ions hydroxyle HO- a ete apportee a l'equivalence ?",
            "6. Deduisez-en la concentration molaire (Ca) de la vitamine C dans le becher :"
        ]
        
        for i in range(1, 7):
            saisie = st.session_state.get(f"col_g_quiz_vitc_q{i}_tab2", "Choisir...")
            attendu = attendus_quiz2[i-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vitc2 += f"<tr><td>{i}</td><td>{questions_text2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_vitc2 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead><tr><th>N°</th><th>Phrase complétée</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """
        
        phrases_trous2 = [
            "1. La verrerie graduee verifiant l'ajout millilitre par millilitre de soude est la",
            "2. Pour prelever les 20 mL de solution d'acide de maniere homogene, on utilise une",
            "3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le",
            "4. Au point equivalent, les reactifs acide et basique ont ete introduits dans les proportions",
            "5. Sur un suivi pH-metrique d'acide faible, l'equivalence correspond a la rupture du"
        ]

        attendus_trous2 = ["Burette", "Pipette jaugée", "diviser par 1000", "stoechiometriques", "Saut de pH"]
        
        # Génération dynamique des lignes de la Partie 2 (Texte à trous)
        for i in range(1, 6):
            saisie = st.session_state.get(f"vitc_t{i}_tab2", "Choisir...")
            attendu = attendus_trous2[i-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vitc2 += f"<tr><td>{i}</td><td>{phrases_trous2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Fermeture des balises de structure du rapport HTML
        html_export_vitc2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de paillasse quantitatif genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        # Sécurisation du nom de fichier d'exportation
        nom_f2 = f"VitamineC2_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        # Affichage du bandeau de validation et du bouton sur Streamlit
        st.success(f"ATELIER VITAMINE C 2 SCELLÉ | Note de session : {tot_s:.1f} / 20")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_vitc2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )
            

with tab3:
    st.header("Calcul theorique & Verification de la boîte")
    st.caption("Verification de la conformite de la masse de vitamine C")

    if "vin_verrouille_tab3" not in st.session_state: 
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.get("vin_verrouille_tab3", False)

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_base", 0.05)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    ph_eq_session = st.session_state.get("input_at2_phe_lu_eleve", 8.7)
    v_titre_session = 20.0
    M_vitC = 176
    facteur_dilution = 25.0
    V_fiole = 500.0

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les resultats de votre dosage
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On a dissous un cachet de vitamine C dans une fiole de 200mL et on prélève 20 mL de cette solution à l'aide d'une pipette jaugée.
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
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M = {M_vitC:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; n = C x V </p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; m = n x M</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # --- APPEL SÉCURISÉ DU QUESTIONNAIRE DE SAISIE ---
    try:
        afficher_questions_vitaminec_commerciale(verrouille=verrou_at3)
    except NameError:
        pass

    # --- CALCULS EXPÉRIMENTAUX DE RÉFÉRENCE ---
    att_v_eq_l = v_eq_session / 1000.0
    att_n_soude = c_base_session * att_v_eq_l
    att_n_acide = att_n_soude
    att_c_molaire = att_n_acide / (v_titre_session / 1000.0)
    att_m_g = att_n_acide * M_vitC
    att_m_mg = att_m_g * 1000.0
    att_c_massique = att_c_molaire * M_vitC
    att_c_massique_mg = att_c_massique * 1000.0
    
    # Remontée du cachet de la fiole de 500 mL (Facteur 25.0)
    att_m_comprime_g = att_m_g * facteur_dilution
    att_m_comprime_mg = att_m_comprime_g * 1000.0
    
    att_conclusion = "Le comprime est conforme a l'etiquette (Masse de vitamine C proche de 500 mg)" if (450.0 <= att_m_comprime_mg <= 550.0) else "Le comprime n'est pas conforme a l'etiquette (Ecart trop important)"

    # --- CASE À COCHER DE CERTIFICATION ---
    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complete l'integralite des calculs d'exploitation de l'Atelier 3.", 
        key="check_certif_asp3_final_net", 
        disabled=verrou_at3
    )

    # --- BOUTON DE VALIDATION ET NOTATION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_vin3_official_net", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Conversion sécurisée du texte tapé par l'élève en float
            def safe_float(key_name):
                try: return float(st.session_state.get(key_name, "0.0").replace(",", "."))
                except: return -999.0

            # Calcul du barème d'évaluation (sur 10 points)
            score_at3_total = 0.0
            import numpy as np
            
            if np.isclose(safe_float("at3_v_eq_l_vitc"), att_v_eq_l, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_n_soude_vitc"), att_n_soude, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_n_acide_becher_vitc"), att_n_acide, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_c_molaire_fille_vitc"), att_c_molaire, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_m_acide_gramme_vitc"), att_m_g, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_m_acide_mg_vitc"), att_m_mg, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_c_massique_fille_vitc"), att_c_massique, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_c_massique_fille_mg_vitc"), att_c_massique_mg, rtol=0.02): score_at3_total += 0.75
            
            if np.isclose(safe_float("at3_masse_molaire_vitc_vitc"), M_vitC, rtol=0.02): score_at3_total += 1.0
            if np.isclose(safe_float("at3_masse_par_comprime_vitc"), att_m_comprime_g, rtol=0.02): score_at3_total += 1.0
            if np.isclose(safe_float("at3_valeur_mg_comprime_vitc"), att_m_comprime_mg, rtol=0.02): score_at3_total += 1.0
            if st.session_state.get("at3_conclusion_bouteille_vitc") == att_conclusion: score_at3_total += 1.0

            st.session_state["score_final_vin3"] = round(min(10.0, score_at3_total), 1)
            st.session_state["vin_verrouille_tab3"] = True
            st.rerun()

    # --- CONSTRUCTION DU DOCUMENT RAPPORT HTML CHIC ---
    if st.session_state.get("vin_verrouille_tab3", False):
        tot_s3 = st.session_state.get("score_final_vin3", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import datetime, timedelta
        timestamp_vin3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_vitc3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vitamine C 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Exploitation quantitative du dosage de la vitamine C</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 10</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue aux calculs sur le becher : <strong>{min(6.0, tot_s3):.1f} / 6</strong><br>
                &bull; Note obtenue au controle du comprime : <strong>{max(0.0, tot_s3 - 6.0):.1f} / 4</strong><br>
                &bull; Note Finale de l'Atelier 3 : <strong>{tot_s3:.1f} / 10</strong>
            </p>
            <div class="sub-title">Compose : Acide ascorbique | Soude titrante : {c_base_session} mol/L</div>

            <div class="sub-title">DETAILS DE VOS CALCULS DE LABORATOIRE</div>
            <table>
                <thead>
                    <tr><th>Grandeur Mathematique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        lignes_rapport3 = [
            ("Volume equivalent en litre (L)", "at3_v_eq_l_vitc", f"{att_v_eq_l:.5f} L", att_v_eq_l, 0.02),
            ("Quantite de soude versee (mol)", "at3_n_soude_vitc", f"{att_n_soude:.5f} mol", att_n_soude, 0.02),
            ("Quantite d'acide ascorbique du becher (mol)", "at3_n_acide_becher_vitc", f"{att_n_acide:.5f} mol", att_n_acide, 0.02),
            ("Concentration molaire Ca (mol/L)", "at3_c_molaire_fille_vitc", f"{att_c_molaire:.3f} mol/L", att_c_molaire, 0.02),
            ("Masse d'acide ascorbique du becher (g)", "at3_m_acide_gramme_vitc", f"{att_m_g:.4f} g", att_m_g, 0.02),
            ("Masse d'acide ascorbique du becher (mg)", "at3_m_acide_mg_vitc", f"{att_m_mg:.1f} mg", att_m_mg, 0.02),
            ("Concentration massique t (g/L)", "at3_c_massique_fille_vitc", f"{att_c_massique:.2f} g/L", att_c_massique, 0.02),
            ("Concentration massique t (mg/L)", "at3_c_massique_fille_mg_vitc", f"{att_c_massique_mg:.1f} mg/L", att_c_massique_mg, 0.02),
            ("Masse molaire de la vitamine C (g/mol)", "at3_masse_molaire_vitc_vitc", f"{M_vitC:.1f} g/mol", M_vitC, 0.02),
            ("Masse de vitamine C dans le comprime (g)", "at3_masse_par_comprime_vitc", f"{att_m_comprime_g:.2f} g", att_m_comprime_g, 0.02),
            ("Masse de vitamine C dans le comprime (mg)", "at3_valeur_mg_comprime_vitc", f"{att_m_comprime_mg:.1f} mg", att_m_comprime_mg, 0.02),
        ]

        import numpy as np
        for desc, key, txt_att, val_att, tol in lignes_rapport3:
            saisie_raw = st.session_state.get(key, "0.0").replace(",", ".")
            try: saisie_val = float(saisie_raw)
            except: saisie_val = -999.0
            v_lbl = "CORRECT" if np.isclose(saisie_val, val_att, rtol=tol) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vitc3 += f"<tr><td>{desc}</td><td>{saisie_raw}</td><td>{txt_att}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        saisie_concl = st.session_state.get("at3_conclusion_bouteille_vitc", "Choisir...")
        v_lbl_c = "CORRECT" if saisie_concl == att_conclusion else "INCORRECT"
        v_class_c = "status-correct" if v_lbl_c == "CORRECT" else "status-incorrect"
        html_export_vitc3 += f"<tr><td>Conclusion sur l'affichage du comprime</td><td>{saisie_concl}</td><td>{att_conclusion}</td><td class='{v_class_c}'>{v_lbl_c}</td></tr>"

        html_export_vitc3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'exploitation de vitamine C genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"VitamineC3_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        st.success(f"ATELIER VITAMINE C 3 SCELLÉ | Note de session : {tot_s3} / 10")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_vitc3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )



















