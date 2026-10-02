# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de la fraîcheur du lait",
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
st.title("Application dosage de la fraîcheur du lait")
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
    "Généralités sur le lait",
    "Dosage colorimétrique de la lait",
    "Calcul théorique sur l'aspirine et vérification de l'inscription sur la boîte"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]


def afficher_questions_bouteille_commerciale(verrouille=False):
    import streamlit as st

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("##### Exploitation du dosage de l'acide lactique dans le becher")
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume equivalent en litre (L) :")
    with c2: st.text_input("", value="0.0", key="at3_v_eq_l", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer le nombre de mole de soude versee a l'equivalence (mol) :")
    with c4: st.text_input("", value="0.0", key="at3_n_soude", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En deduire le nombre de mole d'acide lactique dosee dans le becher (mol) :")
    with c6: st.text_input("", value="0.0", key="at3_n_acide_becher", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en acide lactique du lait (mol/L) :")
    with c8: st.text_input("", value="0.0", key="at3_c_molaire_fille", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse d'acide lactique dosee dans le becher (g) :")
    with c10: st.text_input("", value="0.0", key="at3_m_acide_gramme", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En deduire la masse d'acide lactique dosee (mg) :")
    with c12: st.text_input("", value="0.0", key="at3_m_acide_mg", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique en acide lactique du lait (g/L) :")
    with c14: st.text_input("", value="0.0", key="at3_c_massique_fille", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique en acide lactique du lait (mg/L) :")
    with c16: st.text_input("", value="0.0", key="at3_c_massique_fille_mg", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : DÉTERMINATION DE L'ACIDITÉ DORNIC ET CONCLUSION SANITAIRE ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("##### Remontee au degre Dornic et diagnostic de fraicheur du lait")

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Rappel de la masse molaire de l'acide lactique (g/mol) :")
    with c18: st.text_input("", value="0.0", key="at3_masse_molaire_lait", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("Calculer la masse d'acide lactique contenue dans 1 L de ce lait (g) :")
    with c20: st.text_input("", value="0.0", key="at3_masse_par_litre", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En deduire la valeur de l'acidité Dornic de votre echantillon (°D) :")
    with c22: st.text_input("", value="0.0", key="at3_valeur_degre_dornic", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c23: st.write("Conclure sur la fraicheur et la conformite commerciale de ce lait :")
    with c24: st.selectbox(
        "", 
        [
            "Choisir...", 
            "Le lait est frais et conforme (Acidite entre 15 et 18 °D)", 
            "Le lait n'est pas frais / impropre a la consommation (Acidite superieure a 18 °D)"
        ], 
        key="at3_conclusion_bouteille", 
        disabled=verrouille, 
        label_visibility="collapsed"
    )

    st.markdown('</div>', unsafe_allow_html=True)

def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Recouvrement des constantes calculees du moteur de paillasse pour l'acide lactique
    v_eq_attendu = st.session_state.get("lact_vrai_veq_calc", 12.5)
    c_base_session = st.session_state.get("c_base_lact", 0.10)
    v_acide_dose = 20.0 # Volume initial de solution d'acide lactique Va mis dans le becher

    # Calcul des moles de soude versees a l'equivalence : n = Cb * Ve
    n_soude_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # A l'equivalence n_acide_lactique = n_base (reaction mole a mole)
    c_lact_dose_attendu = (c_base_session * v_eq_attendu) / v_acide_dose

    col_double_quiz_lact, col_double_trous_lact = st.columns(2)

    with col_double_quiz_lact:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de soude ($C_b$) utilisee ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_lact_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_acide_dose:.1f} mL", "10.0 mL", "25.0 mL"]
        st.write("**2.** Quel volume de solution d'acide lactique titree ($V_a$) a ete introduit dans le becher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_lact_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume equivalent exact ($V_E$) de soude verse releve sur la courbe ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_lact_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Ca * Va = Cb * Ve", "Ca * Cb = Va * Ve", "Ca / Va = Cb / Ve"], key="col_g_quiz_lact_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_soude_equiv:.5f} mol", f"{n_soude_equiv * 10:.5f} mol", "0.01000 mol"]
        st.write("**5.** Quelle quantite de matiere d'ions hydroxyle $HO^-$ a ete apportee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_lact_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_lact_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Deduisez-en la concentration molaire ($C_a$) de l'acide lactique dans le becher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_lact_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_lact:
        st.markdown("##### Synthese de cours (Texte a trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee verifiant l'ajout millilitre par millilitre de soude est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Eprouvette graduee", "Pipette jaugee"], key="lact_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prelever de maniere precise le volume d'acide lactique a doser, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugee", "Eprouvette graduee", "Fioles"], key="lact_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="lact_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point equivalent, les reactifs acide et basique ont ete introduits dans les proportions")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="lact_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Sur un suivi pH-metrique d'acide faible, l'equivalence correspond a la rupture du")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Saut de pH", "Palier initial", "Debut du dosage"], key="lact_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_acidelactique1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_lact" not in st.session_state:
        base_quiz1_lact = [
            {"id": "q1_1", "q": "L'acide lactique est une molecule possedant des proprietes :", "type": "menu", "options": ["acides", "neutres", "basiques"], "rep": "acides"},
            {"id": "q1_2", "q": "Calculer la masse molaire moleculaire de l'acide lactique pure (C3H6O3) en g/mol :", "type": "menu", "options": ["90,08", "180,15", "60,05"], "rep": "90,08"},
            {"id": "q1_3", "q": "Quel est le nom chimique officiel de la molecule d'acide lactique ?", "type": "menu", "options": ["acide 2-hydroxypropanoique", "acide acetylsalicylique", "acide ethanoique"], "rep": "acide 2-hydroxypropanoique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes de carbone (C) dans un motif d'acide lactique ?", "type": "menu", "options": ["3", "6", "9"], "rep": "3"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogene (H) dans un motif d'acide lactique ?", "type": "menu", "options": ["6", "8", "4"], "rep": "6"},
            {"id": "q1_6", "q": "Quel est le nombre d'atomes d'oxygene (O) dans un motif d'acide lactique ?", "type": "menu", "options": ["3", "6", "4"], "rep": "3"},
            {"id": "q1_7", "q": "Quelle est la formule brute exacte de l'acide lactique du lait ?", "type": "menu", "options": ["C3H6O3", "C6H8O6", "C2H4O2"], "rep": "C3H6O3"},
            {"id": "q1_8", "q": "D'apres la classification atomique, le nombre de masse de l'element C vaut :", "type": "menu", "options": ["12 g/mol", "14 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "Quelle couleur conventionnelle represente l'atome d'oxygene sur les maquettes ?", "type": "menu", "options": ["Rouge", "Noir", "Blanc"], "rep": "Rouge"},
            {"id": "q1_10", "q": "Dans le lait, l'acide lactique provient principalement de la fermentation du :", "type": "menu", "options": ["Lactose (sucre du lait)", "Lipide (gras du lait)", "Caseine (proteine)"], "rep": "Lactose (sucre du lait)"}
        ]
        copie_base = list(base_quiz1_lact)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_lact = copie_base

    col_double_quiz_lact1, col_double_trous_lact1 = st.columns(2)

    with col_double_quiz_lact1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_lact, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"lact_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_lact_{q_data['id']}"
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

    with col_double_trous_lact1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le principe actif responsable de l'acidite du lait est l'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "lactique", "ascorbique", "citrique"], key="lact_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale s'ecrit")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "C3H6O3", "C6H8O6", "C2H4O2"], key="lact_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculee a partir de ses elements constitutifs vaut")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "90,08 g/mol", "176,12 g/mol", "60,05 g/mol"], key="lact_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au sein de son squelette carbone, on compte un total de")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "3 atomes", "6 atomes", "9 atomes"], key="lact_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre d'atomes d'Hydrogene presents dans la structure vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "6 atomes", "8 atomes", "4 atomes"], key="lact_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le nombre d'atomes d'Oxygene repartis sur ses fonctions hydroxyles et carboxyle est de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "3 atomes", "6 atomes", "4 atomes"], key="lact_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La constante de masse molaire de l'element atomique C est")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "12 g/mol", "1 g/mol", "16 g/mol"], key="lact_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La constante de masse molaire de l'element oxygene O vaut")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "16 g/mol", "12 g/mol", "1 g/mol"], key="lact_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Lors de la manipulation de réactifs corrosifs comme la soude, le port de gants est")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Obligatoire", "Facultatif", "Interdit"], key="lact_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide concentree permet de rapprocher sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7 (neutre)", "0 (acide)", "14 (basique)"], key="lact_t10_tab1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Atelier 1 : Généralités la fraîcheur du lait ")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])

    with col_gauche:
        st.subheader("Document d'étude")
        texte_document = (  "Pour connaître la fraîcheur du lait, on mesure son degré Dornic (°D) qui correspond à la quantité "
            "d'acide lactique, sachant que 1°D correspond à 0,1 g d'acide lactique par litre de lait. Le lait cru est fragile, "
            "mais plus onctueux et aromatisé que les autres laits. Il est embouteillé directement à la ferme puis déposé en magasin "
            "au rayon frais. On le reconnaît à son bouchon jaune. Le lait cru se conserve au maximum 72 heures au frais après mise en bouteille. "
            "En magasin, on reconnaît les laits entier, demi-écrémé et écrémé (pasteurisé c'est-à-dire chauffé à 72 °C pendant 20 secondes, "
            "il peut être conservé pendant 7 jours à 4°C) grâce à la couleur de leur bouchon (respectivement rouge, bleu, vert). Ces trois "
            "catégories correspondent à la teneur en crème présente dans le lait ; en effet, à la laiterie, le lait est pasteurisé, "
            "puis séparé de la crème grâce à une écrémeuse centrifugeuse."
        )
            
        st.info(texte_document)
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        # Création de la figure Matplotlib pour remplacer le Canvas Tkinter
        fig_lait, ax_lait = plt.subplots(figsize=(6, 5.5), facecolor="white")
        ax_lait.set_facecolor("white")
        
        # Alignement strict sur le repère Tkinter de votre script (0 en haut)
        ax_lait.set_ylim(550, 0)
        ax_lait.set_xlim(0, 700)

        # 1. Le bouchon bleu vissé en haut et son effet relief
        ax_lait.add_patch(patches.Rectangle((230, 5), 80, 35, facecolor="#0066cc", edgecolor="none"))
        for i in range(240, 300, 10):
            ax_lait.plot([i, i], [5, 40], color="#004499", linewidth=1)

        # 2. Le col de la bouteille
        coords_col = np.array([[235, 40], [305, 40], [315, 75], [225, 75]])
        ax_lait.add_patch(patches.Polygon(coords_col, facecolor="white", edgecolor="#cccccc", linewidth=1))

        # 3. Le corps de la bouteille (Épaules, rectangle central et fond arrondi)
        ax_lait.add_patch(patches.Ellipse((270, 105), 180, 80, facecolor="white", edgecolor="none"))
        ax_lait.add_patch(patches.Rectangle((180, 105), 180, 390, facecolor="white", edgecolor="none"))
        ax_lait.add_patch(patches.Wedge((270, 490), 90, 0, 180, facecolor="white", edgecolor="none"))
        # Tracé des lignes de contour extérieures globales pour la cohérence
        ax_lait.plot([180, 180], [105, 490], color="#cccccc", linewidth=1)
        ax_lait.plot([360, 360], [105, 490], color="#cccccc", linewidth=1)

        # 4. La poignée creuse (Simulation du trou par couleur de fond lightblue)
        ax_lait.add_patch(patches.Rectangle((325, 110), 20, 180, facecolor="lightblue", edgecolor="#cccccc", linewidth=1))

        # 5. L'étiquette bleue et blanche centrale
        ax_lait.add_patch(patches.Rectangle((181, 280), 178, 180, facecolor="#0099ff", edgecolor="#0099ff"))

        # 6. Décoration de l'étiquette (Partie verte prairie et courbe blanche de laitage)
        coords_prairie = np.array([[181, 390], [359, 390], [359, 460], [181, 460]])
        ax_lait.add_patch(patches.Polygon(coords_prairie, facecolor="#00b050", edgecolor="none"))
        
        coords_chemin = np.array([[260, 390], [300, 390], [240, 460], [200, 460]])
        ax_lait.add_patch(patches.Polygon(coords_chemin, facecolor="#ffffff", edgecolor="none"))

        # 7. Logo "candia"
        ax_lait.add_patch(patches.Ellipse((270, 307.5), 60, 35, facecolor="white", edgecolor="#004499", linewidth=1))
        ax_lait.text(270, 306, "candia", fontname="Arial", fontsize=11, weight="bold", color="#004499", ha="center", va="center")

        # 8. Texte "Grandlait" principal en gras et italique
        ax_lait.text(275, 360, "Grandlait", fontname="Impact", fontsize=15, style="italic", color="#003366", ha="center", va="center")

        # 9. Mention "Demi-écrémé" orientée verticalement à gauche
        ax_lait.text(195, 370, "Demi-écrémé", fontname="Arial", fontsize=9, weight="bold", color="white", rotation=90, ha="center", va="center")

        # 10. Petite vache géométrique sur la prairie
        ax_lait.add_patch(patches.Ellipse((322.5, 430), 25, 20, facecolor="white", edgecolor="black", linewidth=1))
        ax_lait.add_patch(patches.Rectangle((315, 435), 5, 10, facecolor="black", edgecolor="none"))
        ax_lait.add_patch(patches.Rectangle((325, 435), 5, 10, facecolor="black", edgecolor="none"))
        
        ax_lait.axis("off")
        st.pyplot(fig_lait)   
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Données et Légendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphère noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.divider()

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # --- 1. Coordonnées géométriques des atomes de la chaîne carbonée principale ---
        c_methyl = np.array([2.4, 3.0])
        c_cent = np.array([3.6, 2.5])
        c_carboxy = np.array([4.8, 3.0])

        # --- 2. Coordonnées des substituants du carbone central ---
        oh_cent = np.array([3.4, 1.4])
        h_oh_cent = np.array([3.3, 0.8])
        h_cent = np.array([4.2, 1.9])

        # --- 3. Coordonnées des substituants du groupe carboxyle ---
        double_o = np.array([5.6, 2.4])
        oh_carb = np.array([5.0, 4.1])
        h_carb = np.array([5.7, 4.5])

        # --- 4. Coordonnées des hydrogènes du groupement méthyle (-CH3) ---
        h1_m = np.array([1.8, 2.2])
        h2_m = np.array([1.7, 3.4])
        h3_m = np.array([2.5, 4.0])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # --- TRACÉ DES LIAISONS DE LA CHAÎNE PRINCIPALE ---
        tracer_liaison(c_methyl, c_cent)
        tracer_liaison(c_cent, c_carboxy)
        
        # --- TRACÉ DES LIAISONS DES HYDROGÈNES DU MÉTHYLE ---
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)
        
        # --- TRACÉ DES LIAISONS DU -OH CENTRAL ET DE SON HYDROGÈNE ---
        tracer_liaison(c_cent, oh_cent)
        tracer_liaison(oh_cent, h_oh_cent)
        
        # --- TRACÉ DE LA LIAISON DE L'HYDROGÈNE DU CARBONE CENTRAL ---
        tracer_liaison(c_cent, h_cent)
        
        # --- TRACÉ DES LIAISONS DU GROUPEMENT CARBOXYLE ---
        tracer_liaison(c_carboxy, double_o, double=True)
        tracer_liaison(c_carboxy, oh_carb)
        tracer_liaison(oh_carb, h_carb)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, text_color = "#2b3e50", "white"
            elif symbole == 'O': couleur, text_color = "#e74c3c", "white"
            elif symbole == 'H': couleur, text_color = "#ecf0f1", "black"
            else: couleur, text_color = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=text_color, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # --- RENDU DE TOUS LES ATOMES (PAR-DESSUS) ---
        # Atomes de Carbone
        tracer_atome(c_methyl, 'C')
        tracer_atome(c_cent, 'C')
        tracer_atome(c_carboxy, 'C')
        
        # Atomes d'Oxygène
        tracer_atome(oh_cent, 'O')
        tracer_atome(double_o, 'O')
        tracer_atome(oh_carb, 'O')
        
        # Atomes d'Hydrogène
        tracer_atome(h_oh_cent, 'H')
        tracer_atome(h_cent, 'H')
        tracer_atome(h_carb, 'H')
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')

        ax_mol.set_xlim(1.2, 6.2)
        ax_mol.set_ylim(0.5, 4.8)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    res_q1, res_t1 = afficher_questions_acidelactique1_dynamiques(
        verrouille=st.session_state.vin_verrouille_tab1
    )

    st.write("---")
    st.subheader("Généralité sur le lait")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir completé les questions.", 
        key="check_certif_vin1", 
        disabled=st.session_state.vin_verrouille_tab1
    )

    verrou_vin1 = st.session_state.get("vin_verrouille_tab1", False)



with tab2:
    st.header("Dosage de la fraîcheur du lait")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage de l'acidité du lait par la soude")

    # Initialisation des etats de session specifiques a l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "c_base" not in st.session_state: st.session_state.c_base = 0.1
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(3, 7) 

    # Données physico-chimiques réglementaires de l'acide lactique
    v_max_ml = 25.0
    V_ini = 20.0  
    pKa = 3.9     
    M_lait = 90
    C_base = st.session_state.c_base
    n_acide_ini = st.session_state.masse_reelle_g / (M_lait*50)

    # --- CALCULS CHIMIQUES ET THÉORIQUES DE SÉCURITÉ ---
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        import math
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    # Définition sécurisée du volume d'équivalence visuel
    v_eq_visuel = v_eq_theorique if v_eq_theorique < v_max_ml else 12.0

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-a-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.session_state.c_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :", 
                min_value=0.001, max_value=2.0, value=st.session_state.c_base, step=0.001,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_input_cb_base"
            )
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :", 
                min_value=0.1, max_value=2.0, value=st.session_state.pas_ml, step=0.1,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_slider_pas_ml"
            )
        with col_p3:
            liste_indicateurs = list(st.session_state.indicateurs.keys())
            choix_ind = st.selectbox(
                "Sélectionner un indicateur coloré :", 
                options=liste_indicateurs, index=0,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_select_ind_colore"
            )

        st.info(f"Compose : Acide lactique | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000 :.1f} mg | Soude titrante : {C_base} mol/L")
        st.divider()


    v_eq_affiche = locals().get('v_eq_theorique', globals().get('v_eq_theorique', 12.5))
    ph_eq_affiche = locals().get('ph_eq_theorique', globals().get('ph_eq_theorique', 8.2))

    # Utilisation d'une structure de chaîne simple et propre, sans échappement complexe
    texte_resultats = (
        f"Reperes d'equivalence de la session : "
        f"Volume equivalent Veq = {v_eq_affiche:.2f} mL | "
        f"pH a l'equivalence pHeq = {ph_eq_affiche:.2f}"
    )
    
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
    
    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # Calculs automatiques des veritables attendus pour la correction automatique du bouton
    v_acide_dose = 20.0
    moles_soude_equiv = (C_base * v_eq_theorique) / 1000.0
    concentration_lactique_attendue = (C_base * v_eq_theorique) / v_acide_dose

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)

    # Variables locales pour stocker le retour des fonctions
    dict_reponses_quiz, dict_trous = {}, {}

    # Execution propre de l'affichage bicolonne defini dans votre fonction prof
    if not st.session_state.get("animation_active", False):
        try:
            # Appel dynamique de votre def prof existante
            dict_reponses_quiz, dict_trous = generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_vin2)
        except NameError:
            try:
                # Securite si votre def porte encore l'ancien nom dans votre fichier
                dict_reponses_quiz, dict_trous = afficher_questions_titrage_dynamiques(df_donnees=None, verrouille=verrou_vin2)
            except:
                pass
    else:
        st.info("Le versement de la soude est en cours... Le formulaire d'evaluation s'affichera des que l'animation sera terminee.")

    # Profil de l'eleve connecte
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.", 
        key="check_certif_vin2_final_net", 
        disabled=verrou_vin2
    )

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    # Le bouton est actif pour permettre la premiere soumission de l'exercice
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_vin2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz Numérique de gauche (6 questions pour le Lait)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_lact_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_lact_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_lact_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_lact_q4_tab2") == "Ca * Va = Cb * Ve",
                st.session_state.get("col_g_quiz_lact_q5_tab2") == f"{moles_soude_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_lact_q6_tab2") == f"{concentration_lactique_attendue:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction automatique du Texte à trous de droite (5 cases pour le Lait)
            score_t2 = sum([
                st.session_state.get("lact_t1_tab2") == "Burette",
                st.session_state.get("lact_t2_tab2") == "Pipette jaugée",
                st.session_state.get("lact_t3_tab2") == "diviser par 1000",
                st.session_state.get("lact_t4_tab2") == "stoechiometriques",
                st.session_state.get("lact_t5_tab2") == "Saut de pH"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU RAPPORT HTML SANS GRAPHIQUE ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_lait2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Lait 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Dosage de la fraicheur du lait</p>
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
            <div class="sub-title">Compose : Acide lactique | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead><tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        attendus_quiz2 = [f"{C_base:.3f} mol/L", f"{v_acide_dose:.1f} mL", f"{v_eq_theorique:.1f} mL", "Ca * Va = Cb * Ve", f"{moles_soude_equiv:.5f} mol", f"{concentration_lactique_attendue:.4f} mol/L"]
        questions_text2 = [
            "1. Quelle est la concentration molaire de la solution titrante de soude (Cb) utilisee ?",
            "2. Quel volume de solution d'acide lactique titree (Va) a ete introduit dans le becher ?",
            "3. Quel est le volume equivalent exact (VE) de soude verse releve sur la courbe ?",
            "4. Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?",
            "5. Quelle quantite de matiere d'ions hydroxyle HO- a ete apportee a l'equivalence ?",
            "6. Deduisez-en la concentration molaire (Ca) de l'acide lactique dans le becher :"
        ]
        for i in range(1, 7):
            saisie = st.session_state.get(f"col_g_quiz_lact_q{i}_tab2", "Choisir...")
            attendu = attendus_quiz2[i-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_lait2 += f"<tr><td>{i}</td><td>{questions_text2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_lait2 += """
                </tbody>
            </table>
            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead><tr><th>N°</th><th>Phrase complétée</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """
        phrases_trous2 = [
            "1. La verrerie graduee verifiant l'ajout millilitre par millilitre de soude est la",
            "2. Pour prelever de maniere precise le volume d'acide lactique a doser, on utilise une",
            "3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le",
            "4. Au point equivalent, les reactifs acide et basique ont ete introduits dans les proportions",
            "5. Sur un suivi pH-metrique d'acide faible, l'equivalence correspond a la rupture du"
        ]
        attendus_trous2 = ["Burette", "Pipette jaugée", "diviser par 1000", "stoechiometriques", "Saut de pH"]
        
        # CORRECTION DES CLÉS : Changement de "vin_t" par "lact_t" pour lire vos vraies boîtes de l'Atelier Lait 2
        for i in range(1, 6):
            saisie = st.session_state.get(f"lact_t{i}_tab2", "Choisir...")
            attendu = attendus_trous2[i-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_lait2 += f"<tr><td>{i}</td><td>{phrases_trous2[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_lait2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de paillasse colorimetrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Lait2_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f2 = nom_f2.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_lait2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )

            

with tab3:
    st.header("Calcul théorique & Vérification de la boîte")
    st.caption("Verification de la conformite de la fraicheur du lait")

    # Récupération sécurisée du verrou de l'Atelier 3
    verrou_vin3 = st.session_state.get("vin_verrouille_tab3", False)

    # --- APPEL SÉCURISÉ DU FORMULAIRE DE CALCULS ---
    try:
        # Appel de la fonction globale (déplacée en haut du fichier)
        afficher_questions_bouteille_commerciale(verrouille=verrou_vin3)
    except NameError:
        try:
            afficher_questions_titrage_dynamiques(verrouille=verrou_vin3)
        except:
            pass

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_base", 0.1)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    ph_eq_session = st.session_state.get("input_at2_phe_lu_eleve", 8.7)
    v_titre_session = 20.0
    M_lait = 90
    facteur_dilution = 1
    V_fiole = 1

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les resultats de votre dosage
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On dose 20 mL de lait d'une bouteille d'un litre avec que l'on prélève à l'aide aide d'une pipette jaugée.
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
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M = {M_lait:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; n = C x V </p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; m = n x M</p>", unsafe_allow_html=True)


    st.write("")

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # Calculs automatiques des veritables attendus pour la correction automatique du bouton
    v_acide_dose = 20.0
    moles_soude_equiv = (C_base * v_eq_theorique) / 1000.0
    concentration_lactique_attendue = (C_base * v_eq_theorique) / v_acide_dose

    verrou_vin3 = st.session_state.get("vin_verrouille_tab3", False)

    # Variables locales pour stocker le retour des fonctions
    dict_reponses_quiz, dict_trous = {}, {}

    # Execution propre de l'affichage bicolonne defini dans votre fonction prof
    try:
        afficher_questions_bouteille_commerciale(verrouille=verrou_vin3)
    except NameError:
        try:
            afficher_questions_titrage_dynamiques(verrouille=verrou_vin3)
        except:
            pass

    else:
        st.info("Le versement de la soude est en cours... Le formulaire d'evaluation s'affichera des que l'animation sera terminee.")

    # Profil de l'eleve connecte
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 3.", 
        key="check_certif_vin3_final_net", 
        disabled=verrou_vin3
    )
    
    # Initialisation de l'état de verrouillage spécifique à l'Atelier 3 si absent
    if "vin_verrouille_tab3" not in st.session_state:
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.get("vin_verrouille_tab3", False)

    # Récupération de la case à cocher de l'Atelier 2 pour sécuriser la progression
    case_certif_at2_cliquee = st.session_state.get("check_certif_asp2_final_net", False)

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complete l'integralite des calculs d'exploitation de l'Atelier 3.", 
        key="check_certif_asp3_final_net", 
        disabled=verrou_at3
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_vin3_official_net", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at2_cliquee:
            st.error("Action refusee : Vous devez d'abord valider et sceller l'Atelier 2 avant de pouvoir soumettre l'Atelier 3.")
        elif not case_certif_vin3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # --- CALCULS ANALYTIQUES DES ATTENDUS DU LAIT ---
            V_ini_lait = 20.0
            M_lactique = 90.0
            
            att_v_eq_l = v_eq_session / 1000.0
            att_n_soude = C_base * att_v_eq_l
            att_n_acide = att_n_soude
            att_c_molaire = att_n_acide / (V_ini_lait / 1000.0)
            att_m_g = att_n_acide * M_lactique
            att_m_mg = att_m_g * 1000.0
            att_c_massique = att_c_molaire * M_lactique
            att_c_massique_mg = att_c_massique * 1000.0
            
            att_m_litre = att_c_massique
            att_dornic = round(v_eq_session, 1)
            
            att_conclusion = "Le lait est frais et conforme (Acidite entre 15 et 18 °D)" if (15.0 <= att_dornic <= 18.0) else "Le lait n'est pas frais / impropre a la consommation (Acidite superieure a 18 °D)"

            # --- CORRECTION DE TOUTES LES SAISIES ÉLÈVES (Tolérance serrée de 2%) ---
            score_at3_total = 0.0
            
            if np.isclose(st.session_state.get("at3_v_eq_l", 0.0), att_v_eq_l, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_n_soude", 0.0), att_n_soude, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_n_acide_becher", 0.0), att_n_acide, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_c_molaire_fille", 0.0), att_c_molaire, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_m_acide_gramme", 0.0), att_m_g, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_m_acide_mg", 0.0), att_m_mg, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_c_massique_fille", 0.0), att_c_massique, rtol=0.02): score_at3_total += 0.75
            if np.isclose(st.session_state.get("at3_c_massique_fille_mg", 0.0), att_c_massique_mg, rtol=0.02): score_at3_total += 0.75
            
            if np.isclose(st.session_state.get("at3_masse_molaire_lait", 0.0), M_lactique, rtol=0.02): score_at3_total += 1.0
            if np.isclose(st.session_state.get("at3_masse_par_litre", 0.0), att_m_litre, rtol=0.02): score_at3_total += 1.0
            if np.isclose(st.session_state.get("at3_valeur_degre_dornic", 0.0), att_dornic, rtol=0.02): score_at3_total += 1.0
            if st.session_state.get("at3_conclusion_bouteille") == att_conclusion: score_at3_total += 1.0

            st.session_state["score_final_vin3"] = round(min(10.0, score_at3_total), 1)
            st.session_state["vin_verrouille_tab3"] = True
            st.rerun()

    # --- COMPILATION DU RAPPORT CHIMIQUE HTML DE L'ATELIER 3 ---
    if st.session_state.get("vin_verrouille_tab3", False):
        tot_s3 = st.session_state.get("score_final_vin3", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_lait3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Lait 3 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #10b981; color: white; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
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
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 3 : Exploitation quantitative et diagnostic Dornic du lait</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3}</span> / 10</div>
            </div>
            
            <div class="sub-title">Recapitulatif de la Note d'exploitation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                &bull; Note Finale de l'Atelier 3 : <strong>{tot_s3} / 10</strong>
            </p>

            <div class="sub-title">DETAILS DE VOS CALCULS DE LABORATOIRE</div>
            <table>
                <thead>
                    <tr><th>Grandeur Mathematique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Recalcul local pour l'écriture des lignes HTML
        V_ini_lait = 20.0
        M_lactique = 90.0
        ref_v_eq_l = v_eq_session / 1000.0
        ref_n_soude = C_base * ref_v_eq_l
        ref_c_molaire = ref_n_soude / (V_ini_lait / 1000.0)
        ref_m_g = ref_n_soude * M_lactique
        ref_c_massique = ref_c_molaire * M_lactique
        ref_dornic = round(v_eq_session, 1)
        ref_conclusion = "Le lait est frais et conforme (Acidite entre 15 et 18 °D)" if (15.0 <= ref_dornic <= 18.0) else "Le lait n'est pas frais / impropre a la consommation (Acidite superieure a 18 °D)"

        lignes_rapport3 = [
            ("Volume equivalent en litre (L)", "at3_v_eq_l", f"{ref_v_eq_l:.5f} L", ref_v_eq_l, 0.02),
            ("Quantite de soude versee (mol)", "at3_n_soude", f"{ref_n_soude:.5f} mol", ref_n_soude, 0.02),
            ("Quantite d'acide du becher (mol)", "at3_n_acide_becher", f"{ref_n_soude:.5f} mol", ref_n_soude, 0.02),
            ("Concentration molaire Ca (mol/L)", "at3_c_molaire_fille", f"{ref_c_molaire:.3f} mol/L", ref_c_molaire, 0.02),
            ("Masse d'acide du becher (g)", "at3_m_acide_gramme", f"{ref_m_g:.4f} g", ref_m_g, 0.02),
            ("Masse d'acide du becher (mg)", "at3_m_acide_mg", f"{ref_m_g*1000.0:.1f} mg", ref_m_g*1000.0, 0.02),
            ("Concentration massique t (g/L)", "at3_c_massique_fille", f"{ref_c_massique:.2f} g/L", ref_c_massique, 0.02),
            ("Concentration massique t (mg/L)", "at3_c_massique_fille_mg", f"{ref_c_massique*1000.0:.1f} mg/L", ref_c_massique*1000.0, 0.02),
            ("Masse molaire acide lactique (g/mol)", "at3_masse_molaire_lait", f"{M_lactique:.1f} g/mol", M_lactique, 0.02),
            ("Masse d'acide par litre de lait (g)", "at3_masse_par_litre", f"{ref_c_massique:.2f} g", ref_c_massique, 0.02),
            ("Acidite Dornic du lait (°D)", "at3_valeur_degre_dornic", f"{ref_dornic:.1f} °D", ref_dornic, 0.02),
        ]

        for desc, key, txt_att, val_att, tol in lignes_rapport3:
            saisie = st.session_state.get(key, 0.0)
            v_lbl = "CORRECT" if np.isclose(float(saisie), val_att, rtol=tol) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_lait3 += f"<tr><td>{desc}</td><td>{saisie}</td><td>{txt_att}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Ajout de la ligne finale de conclusion
        saisie_concl = st.session_state.get("at3_conclusion_bouteille", "Choisir...")
        v_lbl_c = "CORRECT" if saisie_concl == ref_conclusion else "INCORRECT"
        v_class_c = "status-correct" if v_lbl_c == "CORRECT" else "status-incorrect"

        # Ajout de la ligne finale de conclusion dans le tableau HTML
        html_export_lait3 += f"<tr><td>Conclusion sur la conformite du lait</td><td>{saisie_concl}</td><td>{ref_conclusion}</td><td class='{v_class_c}'>{v_lbl_c}</td></tr>"

        # Fermeture propre des balises de la structure du rapport HTML
        html_export_lait3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'exploitation massique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        # Nettoyage et sécurisation du nom de fichier d'export
        nom_f3 = f"Lait3_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f3 = nom_f3.replace(c, "_")

        # Affichage du bandeau de réussite de fin d'Atelier 3
        st.success(f"ATELIER LAIT 3 SCELLÉ | Note de session : {tot_s3} / 10")
        
        # Bouton de téléchargement final de la note de calcul
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_lait3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )


























