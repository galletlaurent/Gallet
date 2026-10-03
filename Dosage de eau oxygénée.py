# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de l'eau oxygénée",
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
st.title("Application dosage de l'eau oxygénée")
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
    
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 680.0  # Potentiel Rédox initial E (mV)
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 950.0  # Potentiel Rédox attendu à l'équivalence (mV)
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 950.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.020  # Concentration KMnO4 standard (mol/L)
if "animation_active" not in st.session_state: st.session_state.animation_active = False


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
    "Généralités surl'eau oxygénée",
    "Dosage colorimétrique de l'eau oxygénée",
    "Calcul théorique sur l'eau oxygénée et vérification de l'inscription"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]



def generer_atelier_trois_eau_oxygenee(verrouille=False):
    import numpy as np
    import streamlit as st

    C_base = st.session_state.get("c_titrant_kmno4", 0.020)
    v_eq_theorique = st.session_state.get("th_vrai_veq_calc", 12.0)
    V_ini = 10.0  
    M_ox = 34  

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    dict_reponses_bouteille = {}

    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation du dosage de l'eau oxygénée dans le bécher</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume équivalent $V_E$ en litre (L) :")
    with c2: dict_reponses_bouteille["v_eq_l"] = st.number_input("", min_value=0.00000, max_value=1.00000, value=0.00000, step=0.00001, format="%.5f", key="at3_v_eq_l_ox", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer la quantité de matière de permanganate versée à l'équivalence $n(\\text{MnO}_4^-)$ (mol) :")
    with c4: dict_reponses_bouteille["n_permanganate"] = st.number_input("", min_value=0.00000, max_value=1.00000, value=0.00000, step=0.00001, format="%.5f", key="at3_n_permanganate", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En déduire la quantité de matière de peroxyde d'hydrogène dosée dans le bécher $n(\\text{H}_2\\text{O}_2)$ (mol) :")
    with c6: dict_reponses_bouteille["n_acide_becher"] = st.number_input("", min_value=0.00000, max_value=1.00000, value=0.00000, step=0.00001, format="%.5f", key="at3_n_acide_becher_ox", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en peroxyde d'hydrogène de la solution dosée (mol/L) :")
    with c8: dict_reponses_bouteille["c_molaire_fille"] = st.number_input("", min_value=0.000, max_value=10.000, value=0.000, step=0.001, format="%.3f", key="at3_c_molaire_fille_ox", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse de peroxyde d'hydrogène dosée dans le bécher (g) :")
    with c10: dict_reponses_bouteille["m_acide_gramme"] = st.number_input("", min_value=0.0000, max_value=100.0000, value=0.0000, step=0.0001, format="%.4f", key="at3_m_acide_gramme_ox", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En déduire la masse de peroxyde d'hydrogène dosée en milligramme (mg) :")
    with c12: dict_reponses_bouteille["m_acide_mg"] = st.number_input("", min_value=0.0, max_value=10000.0, value=0.0, step=0.1, format="%.1f", key="at3_m_acide_mg_ox", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique en peroxyde d'hydrogène de la solution (g/L) :")
    with c14: dict_reponses_bouteille["c_massique_fille"] = st.number_input("", min_value=0.00, max_value=500.00, value=0.00, step=0.01, format="%.2f", key="at3_c_massique_fille_ox", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique en peroxyde d'hydrogène de la solution (mg/L) :")
    with c16: dict_reponses_bouteille["c_massique_fille_mg"] = st.number_input("", min_value=0.0, max_value=500000.0, value=0.0, step=0.1, format="%.1f", key="at3_c_massique_fille_mg_ox", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Remontée au titre en volumes et diagnostic de conformité commerciale</p>", unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Rappel de la masse molaire de l'eau oxygénée (g/mol) :")
    with c18: dict_reponses_bouteille["masse_molaire"] = st.number_input("", min_value=0.0, max_value=500.0, value=0.0, step=0.1, format="%.1f", key="at3_masse_molaire_ox", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("Calculer la concentration molaire de la solution mère commerciale (mol/L) :")
    with c20: dict_reponses_bouteille["c_molaire_mere"] = st.number_input("", min_value=0.00, max_value=10.00, value=0.00, step=0.01, format="%.2f", key="at3_c_molaire_mere_ox", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En déduire la valeur du titre en volumes de votre échantillon (Volumes) :")
    with c22: dict_reponses_bouteille["valeur_titre_vol"] = st.number_input("", min_value=0.0, max_value=200.0, value=0.0, step=0.1, format="%.1f", key="at3_valeur_titre_vol", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c23: st.write("Conclure sur la conformité de la solution par rapport à l'étiquette commerciale :")
    with c24: dict_reponses_bouteille["conclusion_bouteille"] = st.selectbox(
        "", 
        [
            "Choisir...", 
            "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)", 
            "La solution n'est pas conforme à l'étiquette (Écart trop important / Solution dégradée)"
        ], 
        key="at3_conclusion_bouteille_ox", 
        disabled=verrouille, 
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    return dict_reponses_bouteille


def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Recouvrement des constantes calculees du moteur de paillasse pour l'eau oxygenee
    v_eq_attendu = st.session_state.get("th_vrai_veq_calc", 12.0)
    c_base_session = st.session_state.get("c_titrant_kmno4", 0.020) # Solution de permanganate de potassium
    v_acide_dose = 10.0 # Volume initial d'eau oxygenee Va mis dans le becher (10.0 mL)

    # Calcul des moles de permanganate versees a l'equivalence : n = Cb * Ve
    n_permanganate_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # A l'equivalence n(H2O2)/5 = n(MnO4-)/2 -> n(H2O2) = 2.5 * n(MnO4-)
    c_ox_dose_attendu = (2.5 * c_base_session * v_eq_attendu) / v_acide_dose

    col_double_quiz_ox, col_double_trous_ox = st.columns(2)

    with col_double_quiz_ox:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de permanganate ($C_b$) utilisee ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_ox_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_acide_dose:.1f} mL", "20.0 mL", "25.0 mL"]
        st.write("**2.** Quel volume de solution diluee d'eau oxygenee ($V_a$) a ete introduit dans le becher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_ox_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume equivalent exact ($V_E$) de permanganate verse releve au changement de teinte ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_ox_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stoechiometrique a l'equivalence pour ce titrage redox ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "n(H2O2)/5 = n(MnO4-)/2", "Ca * Va = Cb * Ve", "n(H2O2)/2 = n(MnO4-)/5"], key="col_g_quiz_ox_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_permanganate_equiv:.5f} mol", f"{n_permanganate_equiv * 2.5:.5f} mol", "0.01000 mol"]
        st.write("**5.** Quelle quantite de matiere d'ions permanganate $MnO_4^-$ a ete apportee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_ox_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_ox_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Deduisez-en la concentration molaire ($C_a$) de l'eau oxygenee dans le becher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_ox_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_ox:
        st.markdown("##### Synthese de cours (Texte a trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee verifiant l'ajout millilitre par millilitre de permanganate est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Eprouvette graduee", "Pipette jaugee"], key="ox_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prelever de maniere precise les 10 mL de solution d'eau oxygenee, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugee", "Eprouvette graduee", "Fioles"], key="ox_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="ox_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point equivalent, les reactifs ont ete introduits dans les proportions de l'equation, dites")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="ox_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Ce dosage etant auto-indicateur, la fin de la reaction est marquee par la persistance d'une teinte")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "rose pale", "violet fonce", "incolore"], key="ox_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous


def afficher_questions_eauoxygenee1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_ox" not in st.session_state:
        base_quiz1_ox = [
            {"id": "q1_1", "q": "L'eau oxygénée (peroxyde d'hydrogène) est une molécule possédant des propriétés :", "type": "menu", "options": ["oxydantes", "neutres", "basiques"], "rep": "oxydantes"},
            {"id": "q1_2", "q": "Calculez la masse molaire moléculaire de l'eau oxygénée pure (H2O2) en g/mol :", "type": "menu", "options": ["34,01", "176,12", "54,94"], "rep": "34,01"},
            {"id": "q1_3", "q": "Quel est le nom chimique officiel de la molécule d'eau oxygénée ?", "type": "menu", "options": ["peroxyde d'hydrogène", "acide ascorbique", "permanganate de potassium"], "rep": "peroxyde d'hydrogène"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes d'hydrogène (H) dans un motif de peroxyde d'hydrogène ?", "type": "menu", "options": ["2", "4", "1"], "rep": "2"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'oxygène (O) dans un motif de peroxyde d'hydrogène ?", "type": "menu", "options": ["2", "4", "3"], "rep": "2"},
            {"id": "q1_6", "q": "Quelle spécification technique correspond à une eau oxygénée commerciale à 30 volumes ?", "type": "menu", "options": ["2,68 mol/L", "0,89 mol/L", "1,00 mol/L"], "rep": "2,68 mol/L"},
            {"id": "q1_7", "q": "Quelle est la formule brute exacte du peroxyde d'hydrogène ?", "type": "menu", "options": ["H2O2", "MnO4-", "O2"], "rep": "H2O2"},
            {"id": "q1_8", "q": "D'après l'équation-bilan, combien de moles de H2O2 réagissent avec 2 moles de MnO4- ?", "type": "menu", "options": ["5", "2", "6"], "rep": "5"},
            {"id": "q1_9", "q": "Quelle couleur prend la solution dans le bécher juste après le point d'équivalence ?", "type": "menu", "options": ["Rose pâle", "Incolore", "Violet intense"], "rep": "Rose pâle"},
            {"id": "q1_10", "q": "Par définition, un litre d'eau oxygénée à 30 volumes peut libérer quel volume de gaz dioxygène ?", "type": "menu", "options": ["30 litres", "10 litres", "2,68 litres"], "rep": "30 litres"}
        ]
        copie_base = list(base_quiz1_ox)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_ox = copie_base

    col_double_quiz_ox1, col_double_trous_ox1 = st.columns(2)

    with col_double_quiz_ox1:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_ox, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ox_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_ox_{q_data['id']}"
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

    with col_double_trous_ox1:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le principe actif contenu dans le flacon Gilbert est le peroxyde d'")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "hydrogène", "manganèse", "potassium"], key="ox_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale s'écrit")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "H2O2", "MnO4-", "O2"], key="ox_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculée à partir de ses éléments constitutifs vaut")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "34,01 g/mol", "176,12 g/mol", "54,94 g/mol"], key="ox_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Une solution commerciale à 30 volumes possède une concentration de")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "2,68 mol/L", "0,89 mol/L", "1,00 mol/L"], key="ox_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le volume de gaz dioxygène libéré par un litre de cette solution est de")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "30 litres", "10 litres", "2,68 litres"], key="ox_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le titrage d'oxydoréduction s'effectue à l'aide d'ions permanganate de couleur")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "violette", "incolore", "rose"], key="ox_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Le rapport stœchiométrique de cette réaction entre MnO4- et H2O2 est de 2 pour")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "5", "2", "6"], key="ox_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Au cours du dosage, les ions MnO4- versés deviennent des ions Mn2+")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "incolores", "violets", "roses"], key="ox_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le point d'équivalence est repéré par l'apparition d'une teinte durable")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "rose pâle", "violet foncé", "jaune pâle"], key="ox_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Ce type de dosage n'utilisant pas d'indicateur externe est qualifié d'")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "auto-indicateur", "pH-métrique", "conductimétrique"], key="ox_t10_tab1", disabled=verrouille, label_visibility="collapsed")

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
            disabled=st.session_state.get("verrouille", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # On force la clé principale "verrouille" à True pour bloquer les widgets
            st.session_state["verrouille"] = True
            
            # Rechargement instantané au premier clic
            st.rerun()

with tab1:
    st.header("Atelier 1 : Généralités la fraîcheur du lait ")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])

    with col_gauche:
        st.subheader("Document d'étude")
        texte_document = ("L'eau oxygénée, ou solution aqueuse de peroxyde d'hydrogène (H2O2), est un liquide incolore utilisé en médecine comme antiseptique et dans l'industrie comme agent de blanchiment. "
        "Le titre d'une eau oxygénée commerciale s'exprime couramment en 'Volumes'. Par définition, une eau oxygénée à 30 volumes signifie qu'un litre de cette solution est capable de libérer un volume de 30 litres de gaz dioxygène (O2) dans les conditions normales de température et de pression lors de sa décomposition totale. "
        "Cette spécification technique de 30 volumes correspond précisément à une concentration molaire mère très élevée de 2,68 mol/L en peroxyde d'hydrogène. "
        "Pour réaliser son suivi quantitatif en laboratoire, on effectue un titrage d'oxydoréduction auto-indicateur en milieu acide à l'aide d'une solution titrante de permanganate de potassium (K+ + MnO4-) de couleur violette intense. "
        "L'équation-bilan de cette réaction montre que deux moles d'ions permanganate réagissent avec cinq moles de peroxyde d'hydrogène, établissant un rapport stœchiométrique de 2 pour 5. "
        "Au cours du versement, les ions MnO4- violets sont immédiatement consommés et transformés en ions manganèse Mn2+ qui sont totalement incolores dans le bécher. "
        "Tant que l'eau oxygénée est présente, le milieu reste donc limpide. Au point équivalence exact, l'eau oxygénée est entièrement épuisée : la moindre goutte de permanganate ajoutée en excès ne peut plus réagir et colore la solution d'une teinte rose pâle persistante, marquant la fin du dosage."
    )
            
        st.info(texte_document)

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_ox, ax_ox = plt.subplots(figsize=(6, 5.5), facecolor="white")
        ax_ox.set_facecolor("white")
        
        # Réglage strict du repère cartésien inversé (0 en haut)
        ax_ox.set_ylim(550, 0)
        ax_ox.set_xlim(0, 700)

        # 1. Le bouchon blanc à clapet supérieur et sa fente de relief
        ax_ox.add_patch(patches.Rectangle((220, 10), 80, 50, facecolor="#ffffff", edgecolor="#cccccc", linewidth=1.5, zorder=3))
        ax_ox.plot([220, 300], [35, 35], color="#cccccc", linewidth=1.5, zorder=4)

        # 2. Le col court du flacon (Vertical et rectiligne au centre)
        ax_ox.add_patch(patches.Rectangle((225, 60), 70, 70, facecolor="#ffffff", edgecolor="#e2e8f0", linewidth=1.5, zorder=2))

        # --- RECTIFICATION GÉOMÉTRIQUE : LES DEUX TRAITS OBLIQUES DE FERMETURE DU FLACON ---
        # Trait oblique gauche : scelle l'épaule gauche du bas du col (225, 130) jusqu'au bord du flacon (160, 160)
        ax_ox.plot([225, 160], [130, 160], color="#e2e8f0", linewidth=1.5, zorder=3)
        # Trait oblique droit : scelle l'épaule droite du bas du col (295, 130) jusqu'au bord du flacon (360, 160)
        ax_ox.plot([295, 360], [130, 160], color="#e2e8f0", linewidth=1.5, zorder=3)

        # 3. Le corps du flacon blanc ( Rectangle central et fond arrondi Wedge adapté aux lignes obliques à Y=160 )
        ax_ox.add_patch(patches.Rectangle((160, 160), 200, 280, facecolor="#ffffff", edgecolor="none", zorder=2))
        ax_ox.add_patch(patches.Wedge((260, 440), 100, 0, 180, facecolor="#ffffff", edgecolor="none", zorder=2))
        
        # Alignement des lignes de contour latérales gauches et droites verticales (débutant au bas des obliques à Y=160)
        ax_ox.plot([160, 160], [160, 440], color="#e2e8f0", linewidth=1.5, zorder=2)
        ax_ox.plot([360, 360], [160, 440], color="#e2e8f0", linewidth=1.5, zorder=2)
        
        # 4. Le grand fond orange de l'étiquette centrale
        ax_ox.add_patch(patches.Rectangle((161, 230), 198, 230, facecolor="#f97316", edgecolor="none", zorder=3))

        # 5. La grande vague blanche supérieure de l'étiquette Gilbert
        vague_x = np.linspace(161, 359, 50)
        vague_y = 230 + 15 * np.sin((vague_x - 161) / 30)
        coords_vague = [[161, 230], [359, 230]] + [[x, y] for x, y in zip(vague_x, vague_y)]
        ax_ox.add_patch(patches.Polygon(coords_vague, facecolor="#ffffff", edgecolor="none", zorder=3))

        # 6. TEXTES PRINCIPAUX DE L'ÉTIQUETTE
        ax_ox.text(260, 165, "Eau oxygénée", fontname="Arial", fontsize=9, weight="bold", color="#0369a1", ha="center", va="center", zorder=4)
        ax_ox.text(260, 195, "30 volumes", fontname="Arial", fontsize=10, weight="bold", color="#0f172a", ha="center", va="center", zorder=4)
        ax_ox.text(260, 222, "GILBERT", fontname="Arial", fontsize=10, weight="bold", color="#0369a1", ha="center", va="center", zorder=4)
        
        ax_ox.text(160, 285, "• Décolore les cheveux", fontname="Arial", fontsize=7, weight="bold", color="#ffffff", ha="left", va="center", zorder=4)
        ax_ox.text(160, 310, "• Blanchit le linge", fontname="Arial", fontsize=7, weight="bold", color="#ffffff", ha="left", va="center", zorder=4)
        ax_ox.text(165, 425, "250 mL", fontname="Arial", fontsize=11, weight="bold", color="#ffffff", ha="left", va="center", zorder=4)

        # 7. Logo bleu des Laboratoires Gilbert (Bas droit)
        ax_ox.add_patch(patches.Ellipse((320, 390), 20, 20, facecolor="#0284c7", edgecolor="none", zorder=4))
        coords_logo_int = np.array([[315, 395], [325, 395], [320, 385]])
        ax_ox.add_patch(patches.Polygon(coords_logo_int, facecolor="#ffffff", edgecolor="none", zorder=5))
        
        ax_ox.text(315, 412, "LABORATOIRES", fontname="Arial", fontsize=5, color="#0f172a", ha="center", va="center", zorder=4)
        ax_ox.text(320, 425, "GILBERT", fontname="Arial", fontsize=6, weight="bold", color="#0f172a", ha="center", va="center", zorder=4)
        
        ax_ox.axis("off")
        st.pyplot(fig_ox)
        st.divider()
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Données et Légendes Atomiques du Titrage")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1,0 g/mol")
        with col_leg2: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16,0 g/mol")
        with col_leg3: st.caption("**Manganèse (Mn)**\n\nSphère violette\nM(Mn) = 54,9 g/mol")
            
        st.divider()

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # --- 1. Représentation du Peroxyde d'Hydrogène H2O2 (Incolore) ---
        # Coordonnées des atomes de H-O-O-H
        h1_ox = np.array([1.5, 3.8])
        o1_ox = np.array([2.3, 3.2])
        o2_ox = np.array([3.5, 3.2])
        h2_ox = np.array([4.3, 3.8])

        # --- 2. Représentation de l'Ion Permanganate MnO4- (Violet) ---
        # Coordonnées de l'ion tétraédrique projeté à plat (Mn au centre)
        mn_perm = np.array([3.0, 1.4])
        o1_perm = np.array([3.0, 2.3]) # Liaison double du haut
        o2_perm = np.array([2.1, 0.9]) # Liaison double bas gauche
        o3_perm = np.array([3.9, 0.9]) # Liaison double bas droite
        o4_perm = np.array([1.8, 1.8]) # Liaison simple chargée

        def tracer_liaison_ox(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.05
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # --- TRACÉ DES LIAISONS POUR H2O2 ---
        tracer_liaison_ox(h1_ox, o1_ox)
        tracer_liaison_ox(o1_ox, o2_ox)
        tracer_liaison_ox(o2_ox, h2_ox)

        # --- TRACÉ DES LIAISONS POUR MnO4- ---
        tracer_liaison_ox(mn_perm, o1_perm, double=True)
        tracer_liaison_ox(mn_perm, o2_perm, double=True)
        tracer_liaison_ox(mn_perm, o3_perm, double=True)
        tracer_liaison_ox(mn_perm, o4_perm, double=False)

        def tracer_atome_ox(p, symbole):
            if symbole == 'Mn': couleur, text_color = "#701a75", "white"
            elif symbole == 'O': couleur, text_color = "#e74c3c", "white"
            elif symbole == 'H': couleur, text_color = "#ecf0f1", "black"
            else: couleur, text_color = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=text_color, weight="bold", fontsize=9, ha="center", va="center", zorder=3)

        # --- RENDU DE TOUS LES ATOMES DE LA SÉANCE D'OXYDORÉDUCTION ---
        # Molécule H2O2
        tracer_atome_ox(h1_ox, 'H')
        tracer_atome_ox(o1_ox, 'O')
        tracer_atome_ox(o2_ox, 'O')
        tracer_atome_ox(h2_ox, 'H')
        ax_mol.text(2.9, 4.2, "Peroxyde d'hydrogène H₂O₂", fontsize=9, style="italic", ha="center")

        # Ion MnO4-
        tracer_atome_ox(mn_perm, 'Mn')
        tracer_atome_ox(o1_perm, 'O')
        tracer_atome_ox(o2_perm, 'O')
        tracer_atome_ox(o3_perm, 'O')
        tracer_atome_ox(o4_perm, 'O')
        ax_mol.text(3.0, 0.2, "Ion Permanganate MnO₄⁻", fontsize=9, style="italic", ha="center")

        ax_mol.set_xlim(0.8, 5.2)
        ax_mol.set_ylim(0.0, 4.6)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    verrou_at1 = st.session_state.get("vin_verrouille_tab1", False)
    
    # Appel de la fonction graphique et des questions de nomenclature
    try:
        afficher_questions_eauoxygenee1_dynamiques(verrouille=verrou_at1)
    except NameError:
        pass

    st.write("---")
    st.subheader("Généralité sur l'eau oxygénée")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ox1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_ox1_final_net", 
        disabled=verrou_at1
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE (ATELIER OXYDORÉDUCTION 1) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_ox1_official_net", use_container_width=True, disabled=verrou_at1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_ox1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction dynamique du Quiz de gauche (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_ox" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_ox:
                    reponse_eleve = st.session_state.get(f"ox_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 cases)
            score_t1 = sum([
                st.session_state.get("ox_t1_tab1") == "hydrogène",
                st.session_state.get("ox_t2_tab1") == "H2O2",
                st.session_state.get("ox_t3_tab1") == "34,01 g/mol",
                st.session_state.get("ox_t4_tab1") == "2,68 mol/L",
                st.session_state.get("ox_t5_tab1") == "30 litres",
                st.session_state.get("ox_t6_tab1") == "violette",
                st.session_state.get("ox_t7_tab1") == "5",
                st.session_state.get("ox_t8_tab1") == "incolores",
                st.session_state.get("ox_t9_tab1") == "rose pâle",
                st.session_state.get("ox_t10_tab1") == "auto-indicateur"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- SCELLÉ ET COMPILATION DU RAPPORT HTML POUR L'EAU OXYGÉNÉE ---
    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_ox1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER EAU OXYGÉNÉE 1 SCELLÉ | Note de session : {tot_s} / 20")

        html_export_ox1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Eau Oxygenee 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Etude moleculaire et titre de l'eau oxygenee</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ox1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de Nomenclature : <strong>{scr1:.1f} / 10</strong><br>
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

        if "ordre_quiz1_ox" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_ox, 1):
                saisie = st.session_state.get(f"ox_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ox1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ox1 += """
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
            "1. Le principe actif contenu dans le flacon Gilbert est le peroxyde d'",
            "2. Sa formule de structure brute globale s'écrit",
            "3. La masse molaire calculée à partir de ses éléments constitutifs vaut",
            "4. Une solution commerciale à 30 volumes possède une concentration de",
            "5. Le volume de gaz dioxygène libéré par un litre de cette solution est de",
            "6. Le titrage d'oxydoréduction s'effectue à l'aide d'ions permanganate de couleur",
            "7. Le rapport stœchiométrique de cette réaction entre MnO4- et H2O2 est de 2 pour",
            "8. Au cours du dosage, les ions MnO4- versés deviennent des ions Mn2+",
            "9. Le point d'équivalence est repéré par l'apparition d'une teinte durable",
            "10. Ce type de dosage n'utilisant pas d'indicateur externe est qualifié d'"
        ]
        for num in range(1, 11):
            saisie = st.session_state.get(f"ox_t{num}_tab1", "Choisir...")
            attendu = attendus_trous1[num-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_ox1 += f"<tr><td>{num}</td><td>{phrases_trous1[num-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ox1 += f"""
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse d'oxydoreduction de l'Atelier 1 genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Rapport_Atelier1_Eau_Oxygenee_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_ox1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Dosage d'oxydoréduction de l'eau oxygénée")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage du peroxyde d'hydrogène par le permanganate de potassium")

    # Initialisation des états de session spécifiques à l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse_ox" not in st.session_state: st.session_state.v_verse_ox = 0.0
    if "c_titrant_kmno4" not in st.session_state: st.session_state.c_titrant_kmno4 = 0.020
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    
    # FACTEUR ANTI-TRICHE ÉQUIVALENT AU VINAIGRE (Génération de la masse dosée en mg entre 48 mg et 55 mg)
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(48.0, 55.0) / 1000.0

    # Sélection manuelle du flacon commercial par l'utilisateur
    if "eau" not in st.session_state:
        st.session_state.eau = {
            "Eau oxygénée : Officinale 10 Volumes": {"concentration_mere": 0.892, "titre_vol": 10.0},
            "Eau oxygénée : Officinale 20 Volumes": {"concentration_mere": 1.784, "titre_vol": 20.0},
            "Eau oxygénée : Officinale 30 Volumes": {"concentration_mere": 2.676, "titre_vol": 30.0}
        }
        
    liste_bouteilles = list(st.session_state.eau.keys())
    bouteille_selectionnee = st.selectbox(
        "Sélectionnez le flacon commercial d'eau oxygénée à analyser :",
        options=liste_bouteilles,
        index=0,
        disabled=st.session_state.vin_verrouille_tab2,
        key="choix_bouteille_ox_utilisateur"
    )

    # Données physico-chimiques réglementaires de l'eau oxygénée
    v_max_ml = 25.0
    V_ini = 10.0  # Volume de la prise d'essai introduit dans le bécher (10.0 mL)
    M_ox = 34.01  # Masse molaire précise de H2O2
    C_base = st.session_state.c_titrant_kmno4
    
    # Calcul des moles de peroxyde d'hydrogène réellement présentes dans le bécher
    n_acide_ini = st.session_state.masse_reelle_g / M_ox

    # --- CALCULS CHIMIQUES ET THÉORIQUES DE SÉCURITÉ (Rapport stœchiométrique 2 MnO4- pour 5 H2O2) ---
    if C_base > 0:
        # Relation à l'équivalence : n(H2O2)/5 = n(MnO4-)/2 -> V_E = (2 * n(H2O2)) / (5 * C_b)
        v_eq_theorique = ((2.0 * n_acide_ini) / (5.0 * C_base)) * 1000.0
        if v_eq_theorique > v_max_ml:
            v_eq_theorique = 21.5
            n_acide_ini = (5.0 * C_base * (v_eq_theorique / 1000.0)) / 2.0
            st.session_state.masse_reelle_g = n_acide_ini * M_ox
    else:
        v_eq_theorique = 0.0

    # Sauvegarde des repères au centième pour l'Atelier 3
    st.session_state.th_vrai_veq_calc = round(float(v_eq_theorique), 2)
    st.session_state.session_eau_tiree = bouteille_selectionnee
    v_eq_visuel = v_eq_theorique

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-à-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            C_base = st.number_input(
                "Concentration du permanganate C_b (mol/L) :", 
                min_value=0.001, max_value=2.0, value=float(st.session_state.c_titrant_kmno4), step=0.001,
                format="%.3f",
                disabled=st.session_state.vin_verrouille_tab2, key="c_titrant_kmno4"
            )
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :", 
                min_value=0.1, max_value=2.0, value=float(st.session_state.pas_ml), step=0.1,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_slider_pas_ml"
            )
        with col_p3:
            if "indicateurs" not in st.session_state:
                st.session_state.indicateurs = {
                    "Ions Permanganate (Auto-indicateur)": { "couleur_acide": "#f8fafc", "couleur_zone": "#f472b6", "couleur_base": "#701a75" }
                }
                
            liste_indicateurs = list(st.session_state.indicateurs.keys())

        st.info(f"Composé : Peroxyde d'hydrogène | Échantillon : {bouteille_selectionnee} | Permanganate titrant : {C_base:.3f} mol/L")
        st.divider()

    v_eq_affiche = v_eq_theorique

    # Affichage du bandeau de réussite après complétion de la burette
    texte_resultats = (
        f"Reperes d'equivalence de la session : "
        f"Volume equivalent Veq = {v_eq_affiche:.2f} mL"
    )
    
    if st.session_state.get("v_verse_ox", 0.0) >= v_max_ml or st.session_state.get("vin_verrouille_tab2", False):
        st.success(texte_resultats)
        st.session_state["input_at2_ve_lu_eleve"] = v_eq_affiche

    # --- TRANSMISSION DES TEINTES EXPÉRIMENTALES DE L'AUTO-INDICATEUR ---
    if "indicateurs" not in st.session_state:
        st.session_state.indicateurs = {
            "Ions Permanganate (Auto-indicateur)": { "couleur_acide": "#f8fafc", "couleur_zone": "#f472b6", "couleur_base": "#701a75" }
        }

    try:
        ind_data = st.session_state.indicateurs[choix_ind]
    except (KeyError, NameError):
        ind_data = st.session_state.indicateurs["Ions Permanganate (Auto-indicateur)"]

    # =========================================================================
    # CONSOLE DE SUPERVISION PROFESSEUR (LOGIQUE EXACTE COMPATIBLE VINAIGRE)
    # =========================================================================

    c_acide = ind_data.get("couleur_acide", "#f8fafc")
    c_zone = ind_data.get("couleur_zone", "#f472b6")
    c_base = ind_data.get("couleur_base", "#701a75")        

    html_animation_paillasse = f"""
    <div style="text-align: center; font-family: sans-serif;">
        <div style="margin-bottom: 12px;">
            <button id="btn-start" style="padding: 6px 16px; background: #22c55e; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 6px; font-size: 12px;">Démarrer</button>
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
        
        let vVerse = {st.session_state.get("v_verse_ox", 0.0)};
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

            // 2. Burette Graduée (Solution de KMnO4 violette)
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(140, 50, 20, 160); 
            
            let hauteurBurette = 156 * (1 - (vVerse / vMax));
            let yLiquideHaut = 51.5 + (156 - hauteurBurette);
            
            ctx.fillStyle = 'rgba(112, 26, 117, 0.85)';
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

            // Goutte de permanganate en chute (Violette)
            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 232 : 258;
                ctx.fillStyle = '#701a75';
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
            let nomTeinte = 'Incolore (H2O2)';
            if (Math.abs(vVerse - vEq) <= 0.3) {{
                couleurSol = colorZone; 
                nomTeinte = 'Rose pâle (Équivalence)';
            }} else if (vVerse > vEq) {{
                couleurSol = colorBase; 
                nomTeinte = 'Violet (MnO4- en excès)';
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

            // 5. Électrode de mesure rédox
            ctx.fillStyle = '#34495e';
            ctx.fillRect(182, 210, 12, 85); 
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(188, 210); ctx.lineTo(188, 170); ctx.lineTo(215, 170); ctx.stroke(); 

            // 6. Boîtier Millivoltmètre (Potentiel E en mV)
            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(215, 140, 44, 45);
            
            ctx.fillStyle = '#2ecc71';
            ctx.font = 'bold 9px monospace';
            let txtMv = (vVerse === 0) ? '680' : (680 + (vVerse * 18.5)).toFixed(0);
            ctx.fillText('E: ' + txtMv + ' mV', 217, 166);

            ctx.fillStyle = '#334155';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText('Teinte : ' + nomTeinte, 120, 365);

            setTimeout(() => {{
                requestAnimationFrame(drawScene);
            }}, 500);
        }}

        drawScene();
    </script>
    """
    components.html(html_animation_paillasse, height=430)

    components.html(html_animation_paillasse, height=460)
    if st.button("AFFICHER LES RÉSULTATS DU TITRAGE", key="btn_sync_paillasse_final", use_container_width=True):
        st.session_state.v_verse_ox = v_max_ml
        st.rerun()

    v_eq_affiche = st.session_state.get("th_vrai_veq_calc", 12.0)

    texte_resultats = (
        f"Reperes d'equivalence de la session : "
        f"Volume equivalent Veq = {v_eq_affiche:.2f} mL"
    )
    
    if st.session_state.get("v_verse_ox", 0.0) >= v_max_ml or st.session_state.get("vin_verrouille_tab2", False):
        st.success(texte_resultats)
        st.session_state["input_at2_ve_lu_eleve"] = v_eq_affiche

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # Calculs automatiques des veritables attendus pour le titrage d'oxydoredouction (Va = 10.0 mL)
    v_acide_dose = 10.0
    moles_soude_equiv = (C_base * v_eq_theorique) / 1000.0
    concentration_lactique_attendue = (2.5 * C_base * v_eq_theorique) / v_acide_dose

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)
    dict_reponses_quiz, dict_trous = {}, {}

    if not st.session_state.get("animation_active", False):
        try:
            dict_reponses_quiz, dict_trous = generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_vin2)
        except NameError:
            pass
    else:
        st.info("Le versement du permanganate est en cours... Le formulaire d'evaluation s'affichera des que l'animation sera terminee.")

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
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_vin2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz Numerique (sur 10 points)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_ox_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_ox_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_ox_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_ox_q4_tab2") == "n(H2O2)/5 = n(MnO4-)/2",
                st.session_state.get("col_g_quiz_ox_q5_tab2") == f"{moles_soude_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_ox_q6_tab2") == f"{concentration_lactique_attendue:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction automatique du Texte a trous (sur 10 points)
            score_t2 = sum([
                st.session_state.get("ox_t1_tab2") == "Burette",
                st.session_state.get("ox_t2_tab2") == "Pipette jaugee",
                st.session_state.get("ox_t3_tab2") == "diviser par 1000",
                st.session_state.get("ox_t4_tab2") == "stoechiometriques",
                st.session_state.get("ox_t5_tab2") == "rose pale"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION ET FERMETURE DU DOCUMENT EXPORT HTML POUR L'EAU OXYGÉNÉE ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_ox2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Eau Oxygenee 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Dosage d'oxydoredouction de l'eau oxygenee</p>
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
            <div class="sub-title">Solution titrante : KMnO4 | Concentration : {C_base:.3f} mol/L</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question de paillasse demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Concentration molaire de la solution titrante de KMnO4 (Cb)</td><td>{st.session_state.get("col_g_quiz_ox_q1_tab2", "Choisir...")}</td><td>{C_base:.3f} mol/L</td></tr>
                    <tr><td>2</td><td>Volume d'eau oxygenee introduit dans le becher (Va)</td><td>{st.session_state.get("col_g_quiz_ox_q2_tab2", "Choisir...")}</td><td>{v_acide_dose:.1f} mL</td></tr>
                    <tr><td>3</td><td>Volume equivalent exact (VE) de KMnO4 verse</td><td>{st.session_state.get("col_g_quiz_ox_q3_tab2", "Choisir...")}</td><td>{v_eq_theorique:.1f} mL</td></tr>
                    <tr><td>4</td><td>Relation stoechiometrique d'oxydoredouction</td><td>{st.session_state.get("col_g_quiz_ox_q4_tab2", "Choisir...")}</td><td>n(H2O2)/5 = n(MnO4-)/2</td></tr>
                    <tr><td>5</td><td>Quantite de matiere de KMnO4 apportee a l'equivalence</td><td>{st.session_state.get("col_g_quiz_ox_q5_tab2", "Choisir...")}</td><td>{moles_soude_equiv:.5f} mol</td></tr>
                    <tr><td>6</td><td>Concentration molaire fille calculee dans le becher (Ca)</td><td>{st.session_state.get("col_g_quiz_ox_q6_tab2", "Choisir...")}</td><td>{concentration_lactique_attendue:.4f} mol/L</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Concept du texte a trous</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Verrerie graduee pour la solution de KMnO4</td><td>{st.session_state.get("ox_t1_tab2", "Choisir...")}</td><td>Burette</td></tr>
                    <tr><td>2</td><td>Verrerie de precision pour prelever la solution fille</td><td>{st.session_state.get("ox_t2_tab2", "Choisir...")}</td><td>Pipette jaugee</td></tr>
                    <tr><td>3</td><td>Conversion du volume equivalent en Litres</td><td>{st.session_state.get("ox_t3_tab2", "Choisir...")}</td><td>diviser par 1000</td></tr>
                    <tr><td>4</td><td>Proportions des reactifs definies a l'equivalence</td><td>{st.session_state.get("ox_t4_tab2", "Choisir...")}</td><td>stoechiometriques</td></tr>
                    <tr><td>5</td><td>Teinte persistante caracteristique de la fin du dosage</td><td>{st.session_state.get("ox_t5_tab2", "Choisir...")}</td><td>rose pale</td></tr>
                </tbody>
            </table>
           <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse d'oxydoreduction de l'Atelier 2 genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Atelier2_Eau_Oxygenee_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_ox2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )

            
with tab3:
    st.header("Calcul théorique et Bilan Commercial")
    st.caption("Vérification de la conformité du titre en volumes de l'eau oxygénée")

    # Récupération dynamique des repères expérimentaux calculés par l'Atelier 2
    c_base_session = st.session_state.get("c_titrant_kmno4", 0.020)
    
    # On va chercher le volume théorique calculé d'après le flacon d'eau oxygénée
    v_eq_session = st.session_state.get("th_vrai_veq_calc", 12.0)
    
    # Sécurité : Si l'élève a utilisé le curseur manuel ou la burette, on prend la vraie valeur scellée
    if "input_at2_ve_lu_eleve" in st.session_state and st.session_state["input_at2_ve_lu_eleve"] > 0:
        v_eq_session = st.session_state["input_at2_ve_lu_eleve"]

    v_titre_session = 10.0  # Volume fixe d'essai d'eau oxygénée introduit dans le bécher (10.0 mL)
    M_ox = 34.01 # Masse molaire du peroxyde d'hydrogène (g/mol)

    # Bandeau de rappel graphique en couleurs (Bleu)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="background-color: #ef4444; color: white; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les résultats de votre dosage d'oxydoréduction
            </div>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px;">
                On dose 10,0 mL d'une solution diluée d'eau oxygénée que l'on prélève à l'aide d'une pipette jaugée.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq relevé = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Concentration KMnO4 C_b = {c_base_session:.3f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Volume titré V_a = {v_titre_session:.1f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M(H2O2) = {M_ox:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown("<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Relation redox : n(H2O2) = 2.5 x n(MnO4-)</p>", unsafe_allow_html=True)
        st.markdown("<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Titre en Volumes = C_mère x 11.2</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # Gestion de l'état de verrouillage de l'Atelier 3
    if "vin_verrouille_tab3" not in st.session_state:
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.get("vin_verrouille_tab3", False)

    # Appel de la sous-fonction d'affichage analytique de l'eau oxygénée
    generer_atelier_trois_eau_oxygenee(verrouille=verrou_at3)

    # --- SÉCURITÉ DE CERTIFICATION AND NOTATION AUTOMATIQUE ---
    case_certif_at2_cliquee = st.session_state.get("check_certif_ox1_final_net", False)
    
    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complété l'intégralité des calculs d'exploitation de l'Atelier 3.", 
        key="check_certif_ox3_final_net", 
        disabled=verrou_at3
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_ox3_official_net_final_fixed", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Calcul des attendus physico-chimiques de référence (Prise d'essai Va = 10.0 mL)
            att_v_eq_l = v_eq_session / 1000.0
            att_n_permanganate = c_base_session * att_v_eq_l
            att_n_acide = att_n_permanganate * 2.5
            att_c_molaire = att_n_acide / (v_titre_session / 1000.0)
            att_m_g = att_n_acide * M_ox
            att_m_mg = att_m_g * 1000.0
            att_c_massique = att_c_molaire * M_ox
            att_c_massique_mg = att_c_massique * 1000.0
            
            # Remontée à la solution mère du flacon Gilbert (Facteur de dilution 10)
            att_c_molaire_mere = att_c_molaire * 10.0
            att_titre_vol = att_c_molaire_mere * 11.2
            
            bouteille_active = st.session_state.get("session_eau_tiree", "10 Volumes")
            if "10" in bouteille_active:
                att_conclusion = "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)"
            elif "20" in bouteille_active:
                att_conclusion = "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)"
            else:
                att_conclusion = "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)"

            # Barème d'évaluation mis à jour sur les clés de saisie réelles
            score_at3_total = 0.0
            import numpy as np
            
            if np.isclose(st.session_state.get("at3_v_eq_l_ox", 0.0), att_v_eq_l, rtol=0.02): score_at3_total += 2.0
            if np.isclose(st.session_state.get("at3_n_permanganate", 0.0), att_n_permanganate, rtol=0.02): score_at3_total += 2.0
            if np.isclose(st.session_state.get("at3_n_acide_becher_ox", 0.0), att_n_acide, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_c_molaire_fille_ox", 0.0), att_c_molaire, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_m_acide_gramme_ox", 0.0), att_m_g, rtol=0.02): score_at3_total += 1.5
            if np.isclose(st.session_state.get("at3_m_acide_mg_ox", 0.0), att_m_mg, rtol=0.02): score_at3_total += 1.5
            if np.isclose(st.session_state.get("at3_c_massique_fille_ox", 0.0), att_c_massique, rtol=0.02): score_at3_total += 1.5
            if np.isclose(st.session_state.get("at3_c_massique_fille_mg_ox", 0.0), att_c_massique_mg, rtol=0.02): score_at3_total += 1.5
            
            if np.isclose(st.session_state.get("at3_masse_molaire_ox", 0.0), M_ox, rtol=0.02): score_at3_total += 1.0
            if np.isclose(st.session_state.get("at3_c_molaire_mere_ox", 0.0), att_c_molaire_mere, rtol=0.02): score_at3_total += 1.5
            if np.isclose(st.session_state.get("at3_valeur_titre_vol", 0.0), att_titre_vol, rtol=0.02): score_at3_total += 1.5
            if st.session_state.get("at3_conclusion_bouteille_ox") == att_conclusion: score_at3_total += 1.0

            st.session_state["score_final_vin3"] = round(min(20.0, score_at3_total), 1)
            st.session_state["vin_verrouille_tab3"] = True
            st.rerun()

            
    if st.session_state.get("vin_verrouille_tab3", False):
        tot_s3 = st.session_state.get("score_final_vin3", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import datetime, timedelta
        timestamp_ox3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_ox3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Eau Oxygenee 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Exploitation quantitative et titre en volumes de l'eau oxygenee</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ox3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue aux calculs sur le becher : <strong>{min(14.0, tot_s3):.1f} / 14</strong><br>
                &bull; Note obtenue au controle du flacon commercial : <strong>{max(0.0, tot_s3 - 14.0):.1f} / 6</strong><br>
                &bull; Note Finale de l'Atelier 3 : <strong>{tot_s3:.1f} / 20</strong>
            </p>
            <div class="sub-title">Solution titrante : KMnO4 | Concentration : {c_base_session:.3f} mol/L</div>

            <div class="sub-title">DETAILS DE VOS CALCULS DE LABORATOIRE</div>
            <table>
                <thead>
                    <tr><th>Grandeur Mathematique / Etape</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Recalcul strict des valeurs attendues pour le tableau HTML
        att_v_eq_l = v_eq_session / 1000.0
        att_n_permanganate = c_base_session * att_v_eq_l
        att_n_acide = att_n_permanganate * 2.5
        att_c_molaire = att_n_acide / (v_titre_session / 1000.0)
        att_m_g = att_n_acide * M_ox
        att_m_mg = att_m_g * 1000.0
        att_c_massique = att_c_molaire * M_ox
        att_c_massique_mg = att_c_massique * 1000.0
        att_c_molaire_mere = att_c_molaire * 10.0
        att_titre_vol = att_c_molaire_mere * 11.2

        bouteille_active = st.session_state.get("session_eau_tiree", "10 Volumes")
        if "10" in bouteille_active:
            att_conclusion = "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)" if (8.5 <= att_titre_vol <= 11.5) else "La solution n'est pas conforme à l'étiquette (Écart trop important / Solution dégradée)"
        elif "20" in bouteille_active:
            att_conclusion = "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)" if (17.5 <= att_titre_vol <= 22.5) else "La solution n'est pas conforme à l'étiquette (Écart trop important / Solution dégradée)"
        else:
            att_conclusion = "La solution est conforme à l'étiquette (Titre proche de la valeur nominale)" if (26.5 <= att_titre_vol <= 33.5) else "La solution n'est pas conforme à l'étiquette (Écart trop important / Solution dégradée)"

        lignes_rapport3 = [
            ("Volume equivalent en litre (L)", "at3_v_eq_l_ox", f"{att_v_eq_l:.5f} L", att_v_eq_l, 0.02),
            ("Quantite de permanganate versee (mol)", "at3_n_permanganate", f"{att_n_permanganate:.5f} mol", att_n_permanganate, 0.02),
            ("Quantite de peroxyde d'hydrogene du becher (mol)", "at3_n_acide_becher_ox", f"{att_n_acide:.5f} mol", att_n_acide, 0.02),
            ("Concentration molaire Ca (mol/L)", "at3_c_molaire_fille_ox", f"{att_c_molaire:.3f} mol/L", att_c_molaire, 0.02),
            ("Masse de peroxyde d'hydrogene du becher (g)", "at3_m_acide_gramme_ox", f"{att_m_g:.4f} g", att_m_g, 0.02),
            ("Masse de peroxyde d'hydrogene du becher (mg)", "at3_m_acide_mg_ox", f"{att_m_mg:.1f} mg", att_m_mg, 0.02),
            ("Concentration massique t (g/L)", "at3_c_massique_fille_ox", f"{att_c_massique:.2f} g/L", att_c_massique, 0.02),
            ("Concentration massique t (mg/L)", "at3_c_massique_fille_mg_ox", f"{att_c_massique_mg:.1f} mg/L", att_c_massique_mg, 0.02),
            ("Masse molaire eau oxygenee (g/mol)", "at3_masse_molaire_ox", f"{M_ox:.1f} g/mol", M_ox, 0.02),
            ("Concentration molaire de la solution mere (mol/L)", "at3_c_molaire_mere_ox", f"{att_c_molaire_mere:.2f} mol/L", att_c_molaire_mere, 0.02),
            ("Titre en volumes de la solution commerciale (Volumes)", "at3_valeur_titre_vol", f"{att_titre_vol:.1f} Volumes", att_titre_vol, 0.02),
        ]

        import numpy as np
        for desc, key, txt_att, val_att, tol in lignes_rapport3:
            saisie_raw = str(st.session_state.get(key, "0.0")).replace(",", ".")
            try: saisie_val = float(saisie_raw)
            except: saisie_val = -999.0
            v_lbl = "CORRECT" if np.isclose(saisie_val, val_att, rtol=tol) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_ox3 += f"<tr><td>{desc}</td><td>{saisie_raw}</td><td>{txt_att}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        saisie_concl = st.session_state.get("at3_conclusion_bouteille_ox", "Choisir...")
        v_lbl_c = "CORRECT" if saisie_concl == att_conclusion else "INCORRECT"
        v_class_c = "status-correct" if v_lbl_c == "CORRECT" else "status-incorrect"
        html_export_ox3 += f"<tr><td>Conclusion sur la conformite de la solution</td><td>{saisie_concl}</td><td>{att_conclusion}</td><td class='{v_class_c}'>{v_lbl_c}</td></tr>"

        html_export_ox3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'exploitation d'oxydoreduction genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"EauOxygenee3_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        st.success(f"ATELIER EAU OXYGÉNÉE 3 SCELLÉ | Note de session : {tot_s3} / 20")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_ox3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )




