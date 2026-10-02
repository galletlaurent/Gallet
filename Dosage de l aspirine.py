# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de l'aspirine",
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
st.title("Application dosage de l'aspirine")
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
    "Généralités sur l'aspirine",
    "Dosage colorimétrique de l'aspirine",
    "Calcul théorique sur l'aspirine et vérification de l'inscription sur la boîte"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]



def afficher_questions_aspirine_commerciale(verrouille=False):
    import streamlit as st

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation du dosage de l'aspirine dans le becher</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume equivalent en litre (L) :")
    with c2: st.text_input("", value="0.0", key="at3_v_eq_l_aspirine", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer le nombre de mole de soude versee a l'equivalence (mol) :")
    with c4: st.text_input("", value="0.0", key="at3_n_soude_aspirine", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En deduire le nombre de mole d'aspirine dosee dans le becher (mol) :")
    with c6: st.text_input("", value="0.0", key="at3_n_acide_becher_aspirine", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en aspirine de la solution dosee (mol/L) :")
    with c8: st.text_input("", value="0.0", key="at3_c_molaire_fille_aspirine", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse d'aspirine dosee dans le becher (g) :")
    with c10: st.text_input("", value="0.0", key="at3_m_acide_gramme_aspirine", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En deduire la masse d'aspirine dosee (mg) :")
    with c12: st.text_input("", value="0.0", key="at3_m_acide_mg_aspirine", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique en aspirine de la solution (g/L) :")
    with c14: st.text_input("", value="0.0", key="at3_c_massique_fille_aspirine", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique en aspirine de la solution (mg/L) :")
    with c16: st.text_input("", value="0.0", key="at3_c_massique_fille_mg_aspirine", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : REMONTÉE AU COMPRIMÉ COMMERCIAL ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Remontee a la masse du comprime et conformite de l'etiquette</p>", unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Rappel de la masse molaire de l'aspirine pure (g/mol) :")
    with c18: st.text_input("", value="0.0", key="at3_masse_molaire_aspirine_aspirine", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("Calculer la masse totale d'aspirine contenue dans le comprime entier (g) :")
    with c20: st.text_input("", value="0.0", key="at3_masse_par_comprime_aspirine", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En deduire la masse d'aspirine contenue dans le comprime (mg) :")
    with c22: st.text_input("", value="0.0", key="at3_valeur_mg_comprime_aspirine", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c23: st.write("Conclure sur la conformite de la masse par rapport a l'etiquette (500 mg) :")
    with c24: st.selectbox(
        "", 
        [
            "Choisir...", 
            "Le comprime est conforme a l'etiquette (Masse d'aspirine proche de 500 mg)", 
            "Le comprime n'est pas conforme a l'etiquette (Ecart trop important)"
        ], 
        key="at3_conclusion_bouteille_aspirine", 
        disabled=verrouille, 
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)


def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Recouvrement des constantes calcules du moteur de paillasse pour l'aspirine
    v_eq_attendu = st.session_state.get("asp_vrai_veq_calc", 13.9)
    c_base_session = st.session_state.get("c_base_asp", 0.020)
    v_acide_dose = 20.0 # Volume initial d'aspirine Va mis dans le becher pour le titrage

    # Calcul des moles de soude versees a l'equivalence : n = Cb * Ve
    n_soude_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # A l'equivalence n_aspirine = n_base (reaction mole a mole)
    c_aspirine_dose_attendu = (c_base_session * v_eq_attendu) / v_acide_dose

    col_double_quiz_asp, col_double_trous_asp = st.columns(2)

    with col_double_quiz_asp:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de soude ($C_b$) utilisee ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_asp_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_acide_dose:.1f} mL", "10.0 mL", "25.0 mL"]
        st.write("**2.** Quel volume de solution d'aspirine dissoute ($V_a$) a ete introduit dans le becher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_asp_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume equivalent exact ($V_E$) de soude verse releve sur la courbe ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_asp_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Ca * Va = Cb * Ve", "Ca * Cb = Va * Ve", "Ca / Va = Cb / Ve"], key="col_g_quiz_asp_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_soude_equiv:.5f} mol", f"{n_soude_equiv * 10:.5f} mol", "0.01000 mol"]
        st.write("**5.** Quelle quantite de matiere d'ions hydroxyle $HO^-$ a ete apportee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_asp_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_aspirine_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Deduisez-en la concentration molaire ($C_a$) de l'aspirine dans le becher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_asp_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_asp:
        st.markdown("##### Synthese de cours (Texte a trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee verifiant l'ajout millilitre par millilitre de soude est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Eprouvette graduee", "Pipette jaugee"], key="asp_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prelever les 20 mL de solution d'acide de maniere homogene, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugee", "Eprouvette graduee", "Fioles"], key="asp_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="asp_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point equivalent, les reactifs acide et basique ont ete introduits dans les proportions")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="asp_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Sur un suivi pH-metrique d'acide faible, l'equivalence correspond a la rupture du")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Saut de pH", "Palier initial", "Debut du dosage"], key="asp_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous


def afficher_questions_aspirine1_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour empêcher les plantages d'identifiants Streamlit
    ordre_fixe_asp = [
        {"id": "q1_1", "q": "L'acide acetylsalicylique est une molecule possedant des proprietes :", "options": ["acides", "neutres", "basiques"], "rep": "acides"},
        {"id": "q1_2", "q": "Calculer la masse molaire de l'aspirine pure (C9H8O4) en g/mol :", "options": ["180,15", "90,08", "60,05"], "rep": "180,15"},
        {"id": "q1_3", "q": "Quel est le nom chimique de la molecule d'aspirine ?", "options": ["acide acetylsalicylique", "acide ethanoique", "acide lactique"], "rep": "acide acetylsalicylique"},
        {"id": "q1_4", "q": "Quel est le nombre d'atomes de carbone (C) dans l'aspirine ?", "options": ["9", "6", "3"], "rep": "9"},
        {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogene (H) dans l'aspirine ?", "options": ["8", "6", "4"], "rep": "8"},
        {"id": "q1_6", "q": "Quel est le nombre d'atomes d'oxygene (O) dans l'aspirine ?", "options": ["4", "3", "6"], "rep": "4"},
        {"id": "q1_7", "q": "Quelle est la formule brute exacte de l'aspirine ?", "options": ["C9H8O4", "C3H6O3", "C2H4O2"], "rep": "C9H8O4"},
        {"id": "q1_8", "q": "Le nombre de masse de l'element Carbone (C) vaut :", "options": ["12 g/mol", "1 g/mol", "16 g/mol"], "rep": "12 g/mol"},
        {"id": "q1_9", "q": "Quelle couleur conventionnelle represente l'atome d'hydrogene ?", "options": ["Blanc", "Noir", "Rouge"], "rep": "Blanc"},
        {"id": "q1_10", "q": "Le role principal de l'aspirine dans l'organisme est d'agir comme :", "options": ["Antalgique", "Vitamine", "Sucre"], "rep": "Antalgique"}
    ]

    st.session_state.ordre_quiz1_asp = ordre_fixe_asp

    col_double_quiz_asp1, col_double_trous_asp1 = st.columns(2)

    with col_double_quiz_asp1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_asp, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"asp_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_asp1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le principe actif de l'aspirine commerciale est l'acide")
        with c2: st.selectbox("", ["Choisir...", "acetylsalicylique", "lactique", "ethanoique"], key="asp_t1_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale s'ecrit")
        with c4: st.selectbox("", ["Choisir...", "C9H8O4", "C3H6O3", "C2H4O2"], key="asp_t2_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculee a partir de ses elements constitutifs vaut")
        with c6: st.selectbox("", ["Choisir...", "180,15 g/mol", "90,08 g/mol", "60,05 g/mol"], key="asp_t3_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au sein de son squelette carbone, on compte un total de")
        with c8: st.selectbox("", ["Choisir...", "9 atomes", "6 atomes", "3 atomes"], key="asp_t4_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre d'atomes d'Hydrogene presents dans la structure vaut")
        with c10: st.selectbox("", ["Choisir...", "8 atomes", "6 atomes", "4 atomes"], key="asp_t5_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le nombre d'atomes d'Oxygene repartis sur ses fonctions vaut")
        with c12: st.selectbox("", ["Choisir...", "4 atomes", "3 atomes", "6 atomes"], key="asp_t6_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La constante de masse molaire de l'element atomique C est")
        with c14: st.selectbox("", ["Choisir...", "12 g/mol", "1 g/mol", "16 g/mol"], key="asp_t7_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La constante de masse molaire de l'element oxygene O vaut")
        with c16: st.selectbox("", ["Choisir...", "16 g/mol", "12 g/mol", "1 g/mol"], key="asp_t8_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Lors de la manipulation de réactifs corrosifs comme la soude, le port de gants est")
        with c18: st.selectbox("", ["Choisir...", "Obligatoire", "Facultatif", "Interdit"], key="asp_t9_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide concentree permet de rapprocher sa valeur de pH vers")
        with c20: st.selectbox("", ["Choisir...", "7 (neutre)", "0 (acide)", "14 (basique)"], key="asp_t10_tab1_final", disabled=verrouille, label_visibility="collapsed")
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
    st.header("Atelier 1 : Généralités sur l'aspirine")
    
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
            "L'acide acétylsalicylique, plus connu sous le nom d'aspirine, est la substance active de nombreux "
            "médicaments aux propriétés antalgiques, antipyrétiques et anti-inflammatoires. Il est aussi utilisé comme "
            "antiagrégant plaquettaire. Il s'agit d'un anti-inflammatoire non stéroïdien. C'est un acide faible, dont "
            "la base conjuguée est l'anion acétylsalicylate. L'acide acétylsalicylique est obtenu par acétylation de "
            "l'acide salicylique. Son nom vient du latin salix 'saule'. En 1859 Adolph Wilhelm Hermann Kolbe, "
            "chimiste allemand, réussit la synthèse chimique de l'acide salicylique, utilisé alors pour ses propriétés "
            "antiseptiques, mais c'est Felix Hoffmann (chimiste allemand), entré au service des laboratoires Bayer en 1894, "
            "qui, en octobre 1897, reprenant les travaux antérieurs de Gerhardt, trouve le moyen d'obtenir de l'acide "
            "acétylsalicylique pur. (source : Wikipedia.org)"
        )
        st.info(texte_document)
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        # Création de la figure Matplotlib pour remplacer le Frame et les Canvas Tkinter
        fig_asp_box, ax_asp = plt.subplots(figsize=(6, 4.5), facecolor="#008040")
        ax_asp.set_facecolor("#008040")
        
        # Inversion de l'axe Y pour correspondre au repère Tkinter (0 en haut)
        ax_asp.set_ylim(400, 0)
        ax_asp.set_xlim(0, 600)

        # --- ZONE SUPÉRIEURE (LOGO + TEXTE PRINCIPAL) ---
        # Logo Bayer (Cercle blanc)
        ax_asp.add_patch(patches.Circle((50, 50), 20, facecolor="white", edgecolor="white", zorder=2))
        
        # Texte ASPIRINE ®500
        ax_asp.text(90, 62, "ASPIRINE", fontname="Helvetica", fontsize=24, weight="bold", color="white", ha="left", va="bottom", zorder=2)
        ax_asp.text(235, 35, "®500", fontname="Helvetica", fontsize=10, color="white", ha="left", va="top", zorder=2)

        # --- ZONE MÉDIANE (SUBSTANCE ACTIVE) ---
        ax_asp.text(300, 110, "Acide acétylsalicylique 500 mg", fontname="Helvetica", fontsize=14, color="white", ha="center", va="center", zorder=2)

        # --- LIGNE DE SÉPARATION ROUGE ---
        ax_asp.add_patch(patches.Rectangle((10, 140), 580, 5, facecolor="red", edgecolor="none", zorder=2))

        # --- ZONE INFÉRIEURE (COMPRIMÉS + CORPS TEXTUEL) ---
        # Comprimé 1 (arrière)
        ax_asp.add_patch(patches.Ellipse((120, 240), 70, 70, facecolor="white", edgecolor="white", zorder=2))
        
        # Comprimé 2 (avant - décalé et superposé)
        ax_asp.add_patch(patches.Ellipse((160, 280), 70, 70, facecolor="white", edgecolor="white", zorder=3))

        # Textes indicatifs et de description à droite des comprimés
        ax_asp.text(420, 230, "Contre les céphalées aiguës", fontname="Helvetica", fontsize=10, color="white", ha="center", va="center", zorder=2)
        ax_asp.text(420, 270, "6x2 comprimés effervescents", fontname="Helvetica", fontsize=10, color="white", ha="center", va="center", zorder=2)

        ax_asp.axis("off")
        st.pyplot(fig_asp_box)      

    with col_droite:
        st.subheader("Données et Légendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphère noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # 1. Coordonnées géométriques des 6 carbones du cycle benzénique (Hexagone)
        c1 = np.array([4.0, 3.2])
        c2 = np.array([4.8, 2.7])
        c3 = np.array([4.8, 1.8])
        c4 = np.array([4.0, 1.3])
        c5 = np.array([3.2, 1.8])
        c6 = np.array([3.2, 2.7])

        # 2. Coordonnées du groupement Carboxyle (-COOH) lié à C1
        c_carb = np.array([4.0, 4.3])
        double_o_carb = np.array([4.8, 4.9])
        oh_o_carb = np.array([3.2, 4.8])
        oh_h_carb = np.array([3.2, 5.5])

        # 3. Coordonnées du groupement Ester (-O-CO-CH3) lié à C6
        ester_o1 = np.array([2.3, 3.2])
        ester_c = np.array([1.5, 3.8])
        ester_o2 = np.array([1.5, 4.7])
        c_methyl = np.array([0.7, 3.2])

        # 4. Hydrogènes du groupement méthyle terminal
        h1_m = np.array([0.1, 3.8])
        h2_m = np.array([0.2, 2.4])
        h3_m = np.array([1.1, 2.6])

        # 5. Hydrogènes périphériques du cycle benzénique (liés à C2, C3, C4, C5)
        h_c2 = np.array([5.5, 3.1])
        h_c3 = np.array([5.5, 1.4])
        h_c4 = np.array([4.0, 0.6])
        h_c5 = np.array([2.5, 1.4])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Tracé des liaisons alternées du cycle benzénique
        tracer_liaison(c1, c2, double=True)
        tracer_liaison(c2, c3)
        tracer_liaison(c3, c4, double=True)
        tracer_liaison(c4, c5)
        tracer_liaison(c5, c6, double=True)
        tracer_liaison(c6, c1)

        # Tracé des liaisons du groupement Carboxyle
        tracer_liaison(c1, c_carb)
        tracer_liaison(c_carb, double_o_carb, double=True)
        tracer_liaison(c_carb, oh_o_carb)
        tracer_liaison(oh_o_carb, oh_h_carb)

        # Tracé des liaisons du groupement Ester
        tracer_liaison(c6, ester_o1)
        tracer_liaison(ester_o1, ester_c)
        tracer_liaison(ester_c, ester_o2, double=True)
        tracer_liaison(ester_c, c_methyl)

        # Tracé des liaisons des hydrogènes du méthyle
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)

        # Tracé des liaisons des hydrogènes du cycle
        tracer_liaison(c2, h_c2)
        tracer_liaison(c3, h_c3)
        tracer_liaison(c4, h_c4)
        tracer_liaison(c5, h_c5)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, texte_couleur = "#2b3e50", "white"
            elif symbole == 'O': couleur, texte_couleur = "#e74c3c", "white"
            elif symbole == 'H': couleur, texte_couleur = "#ecf0f1", "black"
            else: couleur, texte_couleur = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # Affichage des atomes du cycle benzénique
        tracer_atome(c1, 'C')
        tracer_atome(c2, 'C')
        tracer_atome(c3, 'C')
        tracer_atome(c4, 'C')
        tracer_atome(c5, 'C')
        tracer_atome(c6, 'C')

        # Affichage des atomes du groupement Carboxyle
        tracer_atome(c_carb, 'C')
        tracer_atome(double_o_carb, 'O')
        tracer_atome(oh_o_carb, 'O')
        tracer_atome(oh_h_carb, 'H')

        # Affichage des atomes du groupement Ester et Méthyle
        tracer_atome(ester_o1, 'O')
        tracer_atome(ester_c, 'C')
        tracer_atome(ester_o2, 'O')
        tracer_atome(c_methyl, 'C')

        # Affichage de tous les atomes d'hydrogène périphériques
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')
        tracer_atome(h_c2, 'H')
        tracer_atome(h_c3, 'H')
        tracer_atome(h_c4, 'H')
        tracer_atome(h_c5, 'H')

        ax_mol.set_xlim(-0.2, 6.2)
        ax_mol.set_ylim(0.2, 6.0)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()


    if "vin_verrouille_tab1" not in st.session_state:
        st.session_state.vin_verrouille_tab1 = False

    verrou_at1 = st.session_state.vin_verrouille_tab1

    # Appel direct et propre de la fonction sans affectation binaire
    try:
        afficher_questions_aspirine1_dynamiques(verrouille=verrou_at1)
    except NameError:
        pass

    st.write("---")
    st.subheader("Généralité sur l'aspirine")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_asp1_final_net", 
        disabled=verrou_at1
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_vin1_official_net", use_container_width=True, disabled=verrou_at1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz1_asp" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_asp:
                    reponse_eleve = st.session_state.get(f"asp_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t1 = sum([
                st.session_state.get("asp_t1_tab1_final") == "acetylsalicylique",
                st.session_state.get("asp_t2_tab1_final") == "C9H8O4",
                st.session_state.get("asp_t3_tab1_final") == "180,15 g/mol",
                st.session_state.get("asp_t4_tab1_final") == "9 atomes",
                st.session_state.get("asp_t5_tab1_final") == "8 atomes",
                st.session_state.get("asp_t6_tab1_final") == "4 atomes",
                st.session_state.get("asp_t7_tab1_final") == "12 g/mol",
                st.session_state.get("asp_t8_tab1_final") == "16 g/mol",
                st.session_state.get("asp_t9_tab1_final") == "Obligatoire",
                st.session_state.get("asp_t10_tab1_final") == "7 (neutre)"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 1 ---
    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ASPIRINE 1 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_asp1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Aspirine 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Etude moleculaire de l'aspirine</p>
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

        if "ordre_quiz1_asp" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_asp, 1):
                saisie = st.session_state.get(f"asp_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_asp1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_asp1 += """
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
            "1. Le principe actif de l'aspirine commerciale est l'acide",
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
        attendus_trous1 = ["acetylsalicylique", "C9H8O4", "180,15 g/mol", "9 atomes", "8 atomes", "4 atomes", "12 g/mol", "16 g/mol", "Obligatoire", "7 (neutre)"]
        
        for num in range(1, 11):
            saisie = st.session_state.get(f"asp_t{num}_tab1_final", "Choisir...")
            attendu = attendus_trous1[num-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_asp1 += f"<tr><td>{num}</td><td>{phrases_trous1[num-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_asp1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de synthese genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Aspirine1_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_asp1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Dosage colorimétrique de l'aspirine")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage de l'acide acétylsalicylique par la soude")

    # # Initialisation des etats de session specifiques a l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "c_base_asp" not in st.session_state: st.session_state.c_base_asp = 0.020
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(490, 510) / 1000.0

    # Données physico-chimiques réglementaires de l'acide acétylsalicylique
    v_max_ml = 25.0
    V_ini = 20.0
    pKa = 3.8
    M_aspirine = 180.15
    C_base = st.session_state.c_base_asp
    n_acide_ini = st.session_state.masse_reelle_g / (M_aspirine * 25)

    # Calcul exact des reperes d'equivalence de la session
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        import math
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    # --- ZONE DES REGLAGES SUPERIEURS (DOUBLON SUPPRIMÉ ET SÉCURISÉ) ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-à-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            C_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :",
                min_value=0.001, max_value=2.0, value=float(st.session_state.c_base_asp), step=0.001,
                format="%.3f",
                disabled=st.session_state.vin_verrouille_tab2, key="c_base_asp"
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

    st.info(f"Compose : Aspirine | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L")
    st.divider()

     # Définition sécurisée du volume d'équivalence visuel
    v_eq_visuel = v_eq_theorique if v_eq_theorique < v_max_ml else 12.0




    v_eq_affiche = locals().get('v_eq_theorique', globals().get('v_eq_theorique', 12.5))
    ph_eq_affiche = locals().get('ph_eq_theorique', globals().get('ph_eq_theorique', 8.2))

    # Utilisation d'une structure de chaîne simple et propre, sans échappement complexe
    texte_resultats = (
        f"Reperes d'equivalence de la session : "
        f"Volume equivalent Veq = {v_eq_affiche:.2f} mL | "
        f"pH a l'equivalence pHeq = {ph_eq_affiche:.2f}"
    )
    
    if st.session_state.get("v_verse", 0.0) >= v_max_ml or st.session_state.get("vin_verrouille_tab2", False):
        st.success(texte_resultats)

    # --- GRANDE CHAÎNE HTML/JS DE LA PAILLASSE ---
    ind_data = st.session_state.indicateurs[choix_ind]
    c_acide = ind_data["couleur_acide"]
    c_zone = ind_data["couleur_zone"]
    c_base = ind_data["couleur_base"]

    html_animation_paillasse = f"""
    <div style="text-align: center; font-family: sans-serif;">
        <div style="margin-bottom: 12px;">
            <button id="btn-start" style="padding: 6px 16px; background: #22c55e; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Demarrer</button>
            <button id="btn-pause" style="padding: 6px 16px; background: #eab308; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Pause</button>
            <button id="btn-clear" style="padding: 6px 16px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">Effacer</button>
        </div>
        <canvas id="paillasse_canvas" width="260" height="380" style="background: white; border: 1px solid #cbd5e1; border-radius: 8px;"></canvas>
        
        <div id="zone-bilan" style="margin-top: 10px; padding: 8px; border-radius: 6px; background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; font-size: 11px; font-weight: bold; display: none;">
            Fin du versement ! Veq = {v_eq_theorique:.2f} mL | pHeq = {ph_eq_theorique:.2f}
        </div>
    </div>

    <script>
        const canvas = document.getElementById('paillasse_canvas');
        const ctx = canvas.getContext('2d');
        
        let vVerse = 0.0;
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

            // 1. Potence metallique
            ctx.fillStyle = '#7f8c8d';
            ctx.fillRect(40, 40, 10, 310); 
            ctx.fillStyle = '#95a5a6';
            ctx.fillRect(45, 60, 105, 5);  

            // 2. Burette Graduee
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

            // Volume en direct a cote du menisque
            ctx.fillStyle = '#0284c7';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText(vVerse.toFixed(1) + ' mL', 165, yLiquideHaut + 4);

            // Goutte en chute
            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 232 : 258;
                ctx.fillStyle = '#38bdf8';
                ctx.beginPath(); ctx.arc(150, yGoutte, 2.5, 0, 2 * Math.PI); ctx.fill();
            }}

            // 3. Agitateur Magnetique
            ctx.fillStyle = '#bdc3c7';
            ctx.strokeStyle = '#7f8c8d';
            ctx.lineWidth = 1.5;
            ctx.fillRect(90, 310, 120, 30);
            ctx.strokeRect(90, 310, 120, 30);
            
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath(); ctx.ellipse(150, 325, 12, 5, 0, 0, 2 * Math.PI); ctx.fill();

            // 4. Becher Gradue
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(105, 230); ctx.lineTo(105, 310); ctx.lineTo(205, 310); ctx.lineTo(205, 230);
            ctx.stroke();

            // Remplissage de couleur
            let couleurSol = colorAcide; 
            let nomTeinte = 'Acide';
            if (Math.abs(vVerse - vEq) <= 0.4) {{
                couleurSol = colorZone; 
                nomTeinte = 'Equivalence';
            }} else if (vVerse > vEq) {{
                couleurSol = colorBase; 
                nomTeinte = 'Basique';
            }}

            let hauteurLiq = 15 + (45 * (vVerse / vMax));
            ctx.fillStyle = couleurSol;
            ctx.fillRect(106, 309 - hauteurLiq, 98, hauteurLiq);

            // Barreau aimante
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 0.8;
            ctx.save();
            ctx.translate(150, 302);
            ctx.rotate((tick % 2 === 0 ? 15 : -15) * Math.PI / 180);
            ctx.fillRect(-14, -2.5, 28, 5);
            ctx.strokeRect(-14, -2.5, 28, 5);
            ctx.restore();

            // 5. Sonde pH-metrique
            ctx.fillStyle = '#34495e';
            ctx.fillRect(182, 210, 12, 85); 
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(188, 210); ctx.lineTo(188, 170); ctx.lineTo(215, 170); ctx.stroke(); 

            // 6. Boitier pH-metre
            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(215, 140, 42, 45);
            
            ctx.fillStyle = '#2ecc71';
            ctx.font = 'bold 9px monospace';
            let txtPh = (vVerse === 0) ? '--' : (2.8 + (vVerse * 0.32)).toFixed(2);
            ctx.fillText('pH: ' + txtPh, 217, 166);

            ctx.fillStyle = '#334155';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText('Teinte : ' + nomTeinte, 95, 365);

            setTimeout(() => {{
                requestAnimationFrame(drawScene);
            }}, 150);
        }}

        drawScene();
    </script>
    """

    # --- RENDU FINAL DU COMPOSANT DANS STREAMLIT ---
    components.html(html_animation_paillasse, height=460)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # Récupération sécurisée des repères expérimentaux réels de la session
    v_eq_theorique = st.session_state.get("asp_vrai_veq_calc", 13.9)
    C_base = st.session_state.get("c_base_asp", 0.020)
    v_acide_dose = 20.0

    # Injection dynamique pour que votre fonction prof lise les bonnes valeurs
    st.session_state["asp_vrai_veq_calc"] = float(v_eq_theorique)
    st.session_state["c_base_asp"] = float(C_base)

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)

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

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_vin2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Attendus théoriques pour l'Aspirine
            n_soude_equiv = (C_base * v_eq_theorique) / 1000.0
            c_aspirine_dose_attendu = (C_base * v_eq_theorique) / v_acide_dose

            # 1. Correction du Quiz (sur 10 points)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_asp_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_asp_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_asp_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_asp_q4_tab2") == "Ca * Va = Cb * Ve",
                st.session_state.get("col_g_quiz_asp_q5_tab2") == f"{n_soude_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_asp_q6_tab2") == f"{c_aspirine_dose_attendu:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction de la Synthèse de cours (sur 10 points)
            score_t2 = sum([
                st.session_state.get("asp_t1_tab2") == "Burette",
                st.session_state.get("asp_t2_tab2") == "Pipette jaugée",
                st.session_state.get("asp_t3_tab2") == "diviser par 1000",
                st.session_state.get("asp_t4_tab2") == "stoechiometriques",
                st.session_state.get("asp_t5_tab2") == "Saut de pH"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU RAPPORT HTML PROPRE ET SYNCHRONISÉ POUR L'ASPIRINE ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_asp2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Aspirine 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Dosage du comprimé d'aspirine</p>
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
            <div class="sub-title">Compose : Acide acetylsalicylique | Soude titrante : {C_base:.3f} mol/L</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead><tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        # Alignement strict des attendus du tableau HTML avec le barème
        n_soude_ref = (C_base * v_eq_theorique) / 1000.0
        c_asp_ref = (C_base * v_eq_theorique) / v_acide_dose

        attendus_quiz2 = [
            f"{C_base:.3f} mol/L", 
            f"{v_acide_dose:.1f} mL", 
            f"{v_eq_theorique:.1f} mL", 
            "Ca * Va = Cb * Ve", 
            f"{n_soude_ref:.5f} mol", 
            f"{c_asp_ref:.4f} mol/L"
        ]
        
        questions_text2 = [
            "1. Quelle est la concentration molaire de la solution titrante de soude (Cb) utilisee ?",
            "2. Quel volume de solution d'aspirine dissoute (Va) a ete introduit dans le becher ?",
            "3. Quel est le volume equivalent exact (VE) de soude verse releve sur la courbe ?",
            "4. Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?",
            "5. Quelle quantite de matiere d'ions hydroxyle HO- a ete apportee a l'equivalence ?",
            "6. Deduisez-en la concentration molaire (Ca) de l'aspirine dans le becher :"
        ]
        
        for i in range(1, 7):
            saisie = st.session_state.get(f"col_g_quiz_asp_q{i}_tab2", "Choisir...")
            attendu = attendus_quiz2[i-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_asp2 += f"<tr><td>{i}</td><td>{questions_text2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_asp2 += """
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
            saisie = st.session_state.get(f"asp_t{i}_tab2", "Choisir...")
            attendu = attendus_trous2[i-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_asp2 += f"<tr><td>{i}</td><td>{phrases_trous2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Fermeture des balises de structure du rapport HTML
        html_export_asp2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de paillasse quantitatif genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        # Sécurisation du nom de fichier d'exportation
        nom_f2 = f"Aspirine2_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        # Affichage du bandeau de validation et du bouton sur Streamlit
        st.success(f"ATELIER ASPIRINE 2 SCELLÉ | Note de session : {tot_s:.1f} / 20")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_asp2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )
            

with tab3:
    st.header("Calcul theorique & Verification de la boîte")
    st.caption("Verification de la conformite de la masse d'acide acétylsalicylique")

    if "vin_verrouille_tab3" not in st.session_state: 
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.get("vin_verrouille_tab3", False)

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_base", 0.1)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    ph_eq_session = st.session_state.get("input_at2_phe_lu_eleve", 8.7)
    v_titre_session = 20.0
    M_aspirine = 180.15
    facteur_dilution = 25.0
    V_fiole = 500.0

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les resultats de votre dosage
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On a dissous un cachet d'aspirine dans une fiole de 500mL and on prélève 20 mL de cette solution à l'aide d'une pipette jaugée.
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
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M = {M_aspirine:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; n = C x V </p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; m = n x M</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # --- APPEL SÉCURISÉ DU QUESTIONNAIRE DE SAISIE ---
    try:
        afficher_questions_aspirine_commerciale(verrouille=verrou_at3)
    except NameError:
        pass

    # --- CALCULS EXPÉRIMENTAUX DE RÉFÉRENCE ---
    att_v_eq_l = v_eq_session / 1000.0
    att_n_soude = c_base_session * att_v_eq_l
    att_n_acide = att_n_soude
    att_c_molaire = att_n_acide / (v_titre_session / 1000.0)
    att_m_g = att_n_acide * M_aspirine
    att_m_mg = att_m_g * 1000.0
    att_c_massique = att_c_molaire * M_aspirine
    att_c_massique_mg = att_c_massique * 1000.0
    
    # Remontée de la fiole de 500 mL (Facteur 25)
    att_m_comprime_g = att_m_g * facteur_dilution
    att_m_comprime_mg = att_m_comprime_g * 1000.0
    
    att_conclusion = "Le comprime est conforme a l'etiquette (Masse d'aspirine proche de 500 mg)" if (450.0 <= att_m_comprime_mg <= 550.0) else "Le comprime n'est pas conforme a l'etiquette (Ecart trop important)"

    # --- CASE À COCHER DE CERTIFICATION ---
    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complete l'integralite des calculs d'exploitation de l'Atelier 3.", 
        key="check_certif_asp3_final_net", 
        disabled=verrou_at3
    )

    # --- BOTTON DE VALIDATION ET NOTATION AUTOMATIQUE ---
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
            
            if np.isclose(safe_float("at3_v_eq_l_aspirine"), att_v_eq_l, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_n_soude_aspirine"), att_n_soude, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_n_acide_becher_aspirine"), att_n_acide, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_c_molaire_fille_aspirine"), att_c_molaire, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_m_acide_gramme_aspirine"), att_m_g, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_m_acide_mg_aspirine"), att_m_mg, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_c_massique_fille_aspirine"), att_c_massique, rtol=0.02): score_at3_total += 0.75
            if np.isclose(safe_float("at3_c_massique_fille_mg_aspirine"), att_c_massique_mg, rtol=0.02): score_at3_total += 0.75
            
            if np.isclose(safe_float("at3_masse_molaire_aspirine_aspirine"), M_aspirine, rtol=0.02): score_at3_total += 1.0
            if np.isclose(safe_float("at3_masse_par_comprime_aspirine"), att_m_comprime_g, rtol=0.02): score_at3_total += 1.0
            if np.isclose(safe_float("at3_valeur_mg_comprime_aspirine"), att_m_comprime_mg, rtol=0.02): score_at3_total += 1.0
            if st.session_state.get("at3_conclusion_bouteille_aspirine") == att_conclusion: score_at3_total += 1.0

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

        html_export_aspirine3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Aspirine 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Exploitation quantitative du dosage de l'aspirine</p>
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
            <div class="sub-title">Compose : Acide acetylsalicylique | Soude titrante : {c_base_session} mol/L</div>

            <div class="sub-title">DETAILS DE VOS CALCULS DE LABORATOIRE</div>
            <table>
                <thead>
                    <tr><th>Grandeur Mathematique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        lignes_rapport3 = [
            ("Volume equivalent en litre (L)", "at3_v_eq_l_aspirine", f"{att_v_eq_l:.5f} L", att_v_eq_l, 0.02),
            ("Quantite de soude versee (mol)", "at3_n_soude_aspirine", f"{att_n_soude:.5f} mol", att_n_soude, 0.02),
            ("Quantite d'aspirine du becher (mol)", "at3_n_acide_becher_aspirine", f"{att_n_acide:.5f} mol", att_n_acide, 0.02),
            ("Concentration molaire Ca (mol/L)", "at3_c_molaire_fille_aspirine", f"{att_c_molaire:.3f} mol/L", att_c_molaire, 0.02),
            ("Masse d'aspirine du becher (g)", "at3_m_acide_gramme_aspirine", f"{att_m_g:.4f} g", att_m_g, 0.02),
            ("Masse d'aspirine du becher (mg)", "at3_m_acide_mg_aspirine", f"{att_m_mg:.1f} mg", att_m_mg, 0.02),
            ("Concentration massique t (g/L)", "at3_c_massique_fille_aspirine", f"{att_c_massique:.2f} g/L", att_c_massique, 0.02),
            ("Concentration massique t (mg/L)", "at3_c_massique_fille_mg_aspirine", f"{att_c_massique_mg:.1f} mg/L", att_c_massique_mg, 0.02),
            ("Masse molaire de l'aspirine (g/mol)", "at3_masse_molaire_aspirine_aspirine", f"{M_aspirine:.1f} g/mol", M_aspirine, 0.02),
            ("Masse d'aspirine dans le comprime (g)", "at3_masse_par_comprime_aspirine", f"{att_m_comprime_g:.2f} g", att_m_comprime_g, 0.02),
            ("Masse d'aspirine dans le comprime (mg)", "at3_valeur_mg_comprime_aspirine", f"{att_m_comprime_mg:.1f} mg", att_m_comprime_mg, 0.02),
        ]

        import numpy as np
        for desc, key, txt_att, val_att, tol in lignes_rapport3:
            saisie_raw = st.session_state.get(key, "0.0").replace(",", ".")
            try: saisie_val = float(saisie_raw)
            except: saisie_val = -999.0
            v_lbl = "CORRECT" if np.isclose(saisie_val, val_att, rtol=tol) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_aspirine3 += f"<tr><td>{desc}</td><td>{saisie_raw}</td><td>{txt_att}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        saisie_concl = st.session_state.get("at3_conclusion_bouteille_aspirine", "Choisir...")
        v_lbl_c = "CORRECT" if saisie_concl == att_conclusion else "INCORRECT"
        v_class_c = "status-correct" if v_lbl_c == "CORRECT" else "status-incorrect"
        html_export_aspirine3 += f"<tr><td>Conclusion sur l'affichage du comprime</td><td>{saisie_concl}</td><td>{att_conclusion}</td><td class='{v_class_c}'>{v_lbl_c}</td></tr>"

        html_export_aspirine3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'exploitation d'aspirine genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"Aspirine3_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        st.success(f"ATELIER ASPIRINE 3 SCELLÉ | Note de session : {tot_s3} / 10")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_aspirine3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )













