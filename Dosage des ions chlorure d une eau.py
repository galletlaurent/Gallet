# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage des ions chlorures d'une eau",
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
st.title("Application dosage des ions chlorures d'une eau")
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
        "Noir Eriochrome T (NET)": { "ph_min": 9.9, "ph_max": 10.1, "couleur_acide": "#C2185B", "nom_acide": "Rose violace (Complexe)", "couleur_zone": "#9C27B0", "nom_zone": "Teinte sensible violette", "couleur_base": "#1E40AF", "nom_base": "Bleu azur (EDTA libre)" }
    }
if "eau" not in st.session_state:
    st.session_state["eau"] = {
        "Marque : Volvic (Basse teneur)": {"Cl": 15.0},
        "Marque : Évian (Moyenne teneur)": {"Cl": 30.0},
        "Marque : Vittel (Moyenne teneur)": {"Cl": 54.0},
        "Marque : Contrex (Forte teneur)": {"Cl": 41.0},
        "Marque : Courmayeur (Forte teneur)": {"Cl": 68.0},
        "Général : Eau déminéralisée": {"Cl": 1.5},
        "Général : Eau du robinet standard": {"Cl": 35.0}
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
    "Généralités les ions chlorures d'une eau",
    "Dosage colorimétrique des ions chlorures d'une eau",
    "Calcul théorique sur l'aspirine et vérification de l'inscription sur l'étiquette"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

def afficher_questions_durete_eau_commerciale(verrouille=False):
    import streamlit as st

    # Injection des styles CSS pour les blocs d'exploitation du TH
    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    dict_reponses_bouteille = {}

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation du dosage complexometrique dans le becher (Volume eau = 10 mL)</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume equivalent d'EDTA $V_E$ en litre (L) :")
    with c2: dict_reponses_bouteille["v_eq_l"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_v_eq_l_th", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer la quantite de matiere d'EDTA versee a l'equivalence $n_{\\text{EDTA}}$ (mol) pour $C_0 = 0,01\\text{ mol/L}$ :")
    with c4: dict_reponses_bouteille["n_edta"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.6f", key="at3_n_edta_th", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En deduire la quantite de matiere totale en ions metalliques ($Ca^{2+} + Mg^{2+}$) contenus dans l'echantillon (mol) :")
    with c6: dict_reponses_bouteille["n_ions_becher"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.6f", key="at3_n_ions_becher_th", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire totale en ions de l'eau analysee $C_a$ (mol/L) :")
    with c8: dict_reponses_bouteille["c_molaire_th"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_c_molaire_th", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la concentration molaire equivalente en mmol/L :")
    with c10: dict_reponses_bouteille["c_mmol_th"] = st.number_input("", min_value=0.00, max_value=100.00, format="%.2f", key="at3_c_mmol_th", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : REMONTÉE AUX UNITÉS HYDROTIMÉTRIQUES COMMERCIALES ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Remontee au Titre Hydrotimetrique (TH) et classification de l'eau</p>", unsafe_allow_html=True)

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("Calculer la concentration massique equivalente en carbonate de calcium $t$ (g/L) [$M(CaCO_3) = 100,1\\text{ g/mol}$] :")
    with c12: dict_reponses_bouteille["t_massique_th"] = st.number_input("", min_value=0.00, max_value=10.00, format="%.3f", key="at3_t_massique_th", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c14: dict_reponses_bouteille["t_mg_th"] = st.number_input("", min_value=0.0, max_value=2000.0, format="%.1f", key="at3_t_mg_th", disabled=verrouille, label_visibility="collapsed")
    with c13: st.write("En deduire la concentration massique en mg/L de $CaCO_3$ equivalent :")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la valeur du Titre Hydrotimetrique (TH) de cette eau en degre francais (°f) [NB: $1\\text{ °f} = 10\\text{ mg/L de } CaCO_3$] :")
    with c16: dict_reponses_bouteille["valeur_th_degre"] = st.number_input("", min_value=0.0, max_value=200.0, format="%.1f", key="at3_valeur_th_degre", disabled=verrouille, label_visibility="collapsed")

    c17, c18 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c17: st.write("Conclure sur la durete et la classification de l'eau minerale analysee :")
    with c18: dict_reponses_bouteille["conclusion_durete"] = st.selectbox(
        "", 
        [
            "Choisir...", 
            "Eau tres douce (TH inferieur a 7 °f)", 
            "Eau douce ou de durete moyenne (TH entre 7 et 15 °f)",
            "Eau dure (TH entre 15 et 30 °f)",
            "Eau tres dure ou incrustante (TH superieur a 30 °f)"
        ], 
        key="at3_conclusion_durete_eau", 
        disabled=verrouille, 
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    return dict_reponses_bouteille


def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Recouvrement des constantes calculées du moteur de paillasse pour les ions chlorure
    v_eq_attendu = st.session_state.get("th_vrai_veq_calc", 12.0)
    c_base_session = 0.010 # Concentration fixée réglementairement pour le nitrate d'argent
    v_eau_dosee = 40.0 # Volume de prise d'essai Va introduit dans le bécher pour Mohr (40.0 mL)

    # Calcul des moles de nitrate d'argent versées à l'équivalence : n = C0 * VE
    n_argent_equiv = (c_base_session * v_eq_attendu) / 1000.0
    
    # À l'équivalence de Mohr : n(Cl-) = n(Ag+) => Ca * Va = C0 * VE
    c_ions_dose_attendu = (c_base_session * v_eq_attendu) / v_eau_dosee

    col_double_quiz_cl, col_double_trous_cl = st.columns(2)

    with col_double_quiz_cl:
        st.markdown("##### Quiz numérique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de nitrate d'argent ($C_0$) utilisée ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_ox_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_eau_dosee:.1f} mL", "10.0 mL", "50.0 mL"]
        st.write("**2.** Quel volume d'échantillon d'eau analysé ($V_a$) a été introduit dans le bécher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_ox_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume équivalent exact ($V_E$) de nitrate d'argent versé relevé au changement de teinte ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_ox_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stœchiométrique à l'équivalence pour ce titrage par précipitation ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "n(Ag+) = n(Cl-)", "n(Ag+) = 2 * n(Cl-)", "2 * n(Ag+) = n(Cl-)"], key="col_g_quiz_ox_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_argent_equiv:.5f} mol", f"{n_argent_equiv * 10:.5f} mol", "0.00100 mol"]
        st.write("**5.** Quelle quantité de matière d'ions argent $Ag^+$ a été apportée à l'équivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_ox_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_ions_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Déduisez-en la concentration molaire en ions chlorure ($C_a$) dans le bécher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_ox_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_cl1:
        st.markdown("##### Synthèse de cours (Texte à trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduée permettant l'ajout millilitre par millilitre de la solution de nitrate d'argent est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Éprouvette graduée", "Pipette jaugée"], key="ox_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prélever les 40 mL d'échantillon d'eau de manière précise et répétitive, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugée", "Éprouvette graduée", "Fiole jaugée"], key="ox_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour convertir le volume équivalent expérimental de mL en Litres, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="ox_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point équivalent, les ions chlorure et les ions argent ont réagi dans des proportions")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="ox_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Lors d'un suivi argentimétrique selon Mohr, l'équivalence correspond au virage persistant vers le")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "rouge brique", "rose violacé", "bleu azur"], key="ox_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_chlorures_eau1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_cl" not in st.session_state:
        base_quiz1_cl = [
            {"id": "q1_1", "q": "Le dosage colorimétrique des ions chlorure (Cl⁻) par les ions argent (Ag⁺) est un titrage par :", "type": "menu", "options": ["précipitation", "complexation", "acido-basique"], "rep": "précipitation"},
            {"id": "q1_2", "q": "Quelle est la formule du précipité blanc qui se forme lors de l'ajout du nitrate d'argent ?", "type": "menu", "options": ["AgCl", "Ag2CrO4", "NaCl"], "rep": "AgCl"},
            {"id": "q1_3", "q": "Quel indicateur coloré utilise-t-on pour repérer l'équivalence dans la méthode de Mohr ?", "type": "menu", "options": ["chromate de potassium", "NET", "phénolphtaléine"], "rep": "chromate de potassium"},
            {"id": "q1_4", "q": "D'après la classification, quelle est la masse molaire de l'élément Chlore (Cl) en g/mol ?", "type": "menu", "options": ["35,5", "107,9", "23,0"], "rep": "35,5"},
            {"id": "q1_5", "q": "Quelle est la couleur initiale de la solution dans le bécher après ajout du chromate de potassium ?", "type": "menu", "options": ["jaune", "rose", "incolore"], "rep": "jaune"},
            {"id": "q1_6", "q": "Au point équivalent, l'apparition de quel composé provoque le virage coloré de la solution ?", "type": "menu", "options": ["chromate d'argent", "chlorure d'argent", "nitrate de potassium"], "rep": "chromate d'argent"},
            {"id": "q1_7", "q": "Quelle teinte persistante caractérise la fin du dosage des ions chlorure ?", "type": "menu", "options": ["rouge brique", "bleu azur", "rose violacé"], "rep": "rouge brique"},
            {"id": "q1_8", "q": "Quelle est la formule brute du précipité secondaire responsable de la coloration rouge brique ?", "type": "menu", "options": ["Ag2CrO4", "AgCl", "K2CrO4"], "rep": "Ag2CrO4"},
            {"id": "q1_9", "q": "Le rapport stœchiométrique de la réaction de dosage entre les ions Ag⁺ et Cl⁻ est de :", "type": "menu", "options": ["1 pour 1", "1 pour 2", "2 pour 1"], "rep": "1 pour 1"},
            {"id": "q1_10", "q": "Quelle est la concentration molaire standard C0 de la solution titrante de nitrate d'argent utilisée ?", "type": "menu", "options": ["0,01 mol/L", "0,10 mol/L", "1,00 mol/L"], "rep": "0,01 mol/L"}
        ]
        copie_base = list(base_quiz1_cl)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_cl = copie_base

    col_double_quiz_cl1, col_double_trous_cl1 = st.columns(2)

    with col_double_quiz_cl1:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_cl, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"th_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_cl_{q_data['id']}"
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

    with col_double_trous_cl1:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Les ions dosés dans cet atelier par une solution de nitrate d'argent sont les ions")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "chlorure", "calcium", "sulfate"], key="th_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La solution titrante apporte des ions réactifs d'argent dont la formule chimique est")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Ag+", "Cl-", "NO3-"], key="th_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La réaction entre Ag+ et Cl- donne un précipité blanc de chlorure d'argent de formule")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "AgCl", "Ag2CrO4", "NaCl"], key="th_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La masse molaire atomique de l'élément chlore (Cl) mise en œuvre vaut environ")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "35,5 g/mol", "107,9 g/mol", "23,0 g/mol"], key="th_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le titrage volumétrique par formation d'un solide insoluble est qualifié de titrage par")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "précipitation", "complexation", "neutralisation"], key="th_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'indicateur de fin de réaction ajouté au début de la manipulation est le chromate de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "potassium", "sodium", "calcium"], key="th_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Au point équivalent stœchiométrique, la couleur de la solution vire du jaune au")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "rouge brique", "bleu azur", "vert"], key="th_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le précipité coloré secondaire qui apparaît à l'équivalence a pour formule brute")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Ag2CrO4", "AgCl", "K2CrO4"], key="th_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le volume d'indicateur coloré préconisé pour cette méthode de Mohr est égal à")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "1 mL", "5 mL", "10 mL"], key="th_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. La concentration molaire C0 de la solution de nitrate d'argent est fixée à")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "0,01 mol/L", "0,10 mol/L", "0,50 mol/L"], key="th_t10_tab1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Atelier 1 : Généralités sur les ions chlorures d'une eau")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    col_gauche, col_droite = st.columns([1, 1])
    
    with col_gauche:
        st.subheader("Données et Définition du Dosage")
        st.info(
            "Le dosage des ions chlorure (Cl⁻) dans une eau s'effectue par titrage volumétrique par précipitation "
            "(méthode de Mohr). La solution titrante utilisée est le nitrate d'argent (Ag⁺ + NO3⁻) de concentration "
            "C0 = 0,01 mol/L. Les ions argent réagissent avec les ions chlorure pour former un précipité blanc "
            "qui noircit à la lumière : le chlorure d'argent AgCl(s). La réaction possède un rapport stœchiométrique "
            "de 1 pour 1. L'indicateur de fin de réaction introduit est le chromate de potassium (1 mL). "
            "Dès que tous les ions chlorure ont été consommés à l'équivalence, les ions argent ajoutés en excès "
            "réagissent avec les ions chromate (CrO4²⁻) pour former un précipité secondaire de chromate d'argent "
            "Ag2CrO4(s), colorant instantanément et durablement la solution d'une teinte rouge brique."
        )
        st.divider()

    with col_droite:
        st.subheader("Représentation de l'Équiquette de Composition")
        
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_box, ax_box = plt.subplots(figsize=(7, 5.5), facecolor="white")
        ax_box.set_facecolor("white")
        ax_box.set_ylim(500, 0)
        ax_box.set_xlim(0, 700)

        ax_box.add_patch(patches.Rectangle((150, 20), 400, 460, facecolor="white", edgecolor="#0000bb", linewidth=4, zorder=1))
        ax_box.add_patch(patches.Rectangle((152, 22), 396, 45, facecolor="#0000bb", edgecolor="none", zorder=2))
        ax_box.text(170, 45, "ANALYSE MINIÈRE GLOBALE", fontname="Arial", fontsize=16, weight="bold", color="white", ha="left", va="center", zorder=3)
        ax_box.text(525, 45, "mg/l", fontname="Arial", fontsize=14, style="italic", color="white", ha="right", va="center", zorder=3)

        # Focus sur la teneur en ions chlorure mis en évidence
        elements_analyse = [
            ("CHLORURES (Cl-)", "37", 120),
            ("CALCIUM", "55", 170),
            ("MAGNESIUM", "19", 220),
            ("SODIUM", "24", 270),
            ("SULFATES", "13", 320),
            ("NITRATES", "<0.1", 370)
        ]

        for nom, val, y_pos in elements_analyse:
            ax_box.text(170, y_pos, nom, fontname="Arial", fontsize=11, weight="bold", color="#004499", ha="left", va="center", zorder=3)
            ax_box.text(530, y_pos, val, fontname="Arial", fontsize=12, weight="bold", color="#004499", ha="right", va="center", zorder=3)
            points_x = np.linspace(310, 490, 20)
            points_y = np.full_like(points_x, y_pos + 2)
            ax_box.scatter(points_x, points_y, s=2, color="#94a3b8", zorder=3)

        ax_box.add_patch(patches.Rectangle((152, 440), 396, 38, facecolor="#0000bb", edgecolor="none", zorder=2))
        ax_box.text(350, 458, "Certifié conforme aux normes de santé publique", fontname="Arial", fontsize=9, style="italic", color="white", ha="center", va="center", zorder=3)
        ax_box.axis("off")
        st.pyplot(fig_box)
        st.divider()


    res_q1, res_t1 = afficher_questions_chlorures_eau1_dynamiques(
        verrouille=st.session_state.get("vin_verrouille_tab1", False)
    )

    verrou_th1 = st.session_state.get("vin_verrouille_tab1", False)

    st.write("---")
    st.subheader("Généralités sur les ions chlorures d'une eau")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_th1 = st.checkbox(
        "Je certifie avoir complété les
    res_q1, res_t1 = afficher_questions_chlorures_eau1_dynamiques(
        verrouille=st.session_state.get("vin_verrouille_tab1", False)
    )

    verrou_th1 = st.session_state.get("vin_verrouille_tab1", False)

    st.write("---")
    st.subheader("Généralités sur les ions chlorures d'une eau")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_th1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_th1_final_net", 
        disabled=verrou_th1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_th1_official_net", use_container_width=True, disabled=verrou_th1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_th1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz de gauche mélangé (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_cl" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_cl:
                    reponse_eleve = st.session_state.get(f"th_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0t", 
        disabled=verrou_th1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_th1_official_net", use_container_width=True, disabled=verrou_th1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_th1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz de gauche mélangé (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_cl" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_cl:
                    reponse_eleve = st.session_state.get(f"th_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 cases chlorures)
            score_t1 = sum([
                st.session_state.get("th_t1_tab1") == "chlorure",
                st.session_state.get("th_t2_tab1") == "Ag+",
                st.session_state.get("th_t3_tab1") == "AgCl",
                st.session_state.get("th_t4_tab1") == "35,5 g/mol",
                st.session_state.get("th_t5_tab1") == "précipitation",
                st.session_state.get("th_t6_tab1") == "potassium",
                st.session_state.get("th_t7_tab1") == "rouge brique",
                st.session_state.get("th_t8_tab1") == "Ag2CrO4",
                st.session_state.get("th_t9_tab1") == "1 mL",
                st.session_state.get("th_t10_tab1") == "0,01 mol/L"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- SCELLÉ ET COMPILATION DU RAPPORT HTML POUR LES IONS CHLORURE ---
    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_th1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_th1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Ions Chlorure 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Généralités sur les ions chlorures d'une eau (Méthode de Mohr)</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_th1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Nomenclature Argentimétrique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours (Texte a trous) : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_cl" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_cl, 1):
                saisie = st.session_state.get(f"th_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_th1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_th1 += """
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
            "1. Les ions dosés dans cet atelier par une solution de nitrate d'argent sont les ions",
            "2. La solution titrante apporte des ions réactifs d'argent dont la formule chimique est",
            "3. La réaction entre Ag+ et Cl- donne un précipité blanc de chlorure d'argent de formule",
            "4. La masse molaire atomique de l'élément chlore (Cl) mise en œuvre vaut environ",
            "5. Le titrage volumétrique par formation d'un solide insoluble est qualifié de titrage par",
            "6. L'indicateur de fin de réaction ajouté au début de la manipulation est le chromate de",
            "7. Au point équivalent stœchiométrique, la couleur de la solution vire du jaune au",
            "8. Le précipité coloré secondaire qui apparaît à l'équivalence a pour formule brute",
            "9. Le volume d'indicateur coloré préconisé pour cette méthode de Mohr est égal à",
            "10. La concentration molaire C0 de la solution de nitrate d'argent est fixée à"
        ]
        attendus_trous1 = ["chlorure", "Ag+", "AgCl", "35,5 g/mol", "précipitation", "potassium", "rouge brique", "Ag2CrO4", "1 mL", "0,01 mol/L"]

        for i in range(1, 11):
            saisie = st.session_state.get(f"th_t{i}_tab1", "Choisir...")
            attendu = attendus_trous1[i-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_th1 += f"<tr><td>{i}</td><td>{phrases_trous1[i-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_th1 += f"""
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse de l'Atelier 1 genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Rapport_Atelier1_Ions_Chlorures_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_th1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Atelier 2 : Dosage colorimétrique des ions chlorure")
    st.caption("Simulation interactive de la méthode de Mohr avec l'apparition du précipité et le virage rouge brique")

    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "v_verse_ox" not in st.session_state: st.session_state.v_verse_ox = 0.0
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    
    if "facteur_titrage_ox" not in st.session_state:
        import random
        st.session_state.facteur_titrage_ox = random.uniform(0.96, 1.04)
        
    coeff_alea = st.session_state.facteur_titrage_ox

    liste_bouteilles = list(st.session_state["eau"].keys())
    bouteille_selectionnee = st.selectbox("Sélectionnez l'eau de table à analyser :", options=liste_bouteilles, disabled=st.session_state.vin_verrouille_tab2)

    v_max_ml = 25.0
    V_ini = 40.0  # Prise d'essai optimisée pour l'argentimétrie (40.0 mL)
    M_cl = 35.45  # Masse molaire de l'ion chlorure (g/mol)

    with st.container(border=True):
        st.subheader("Contrôle de la burette graduée")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            C_base = st.number_input("Concentration de la solution de nitrate d'argent C0 (mol/L) :", min_value=0.001, max_value=0.500, value=0.010, format="%.3f", disabled=True, key="c_titrant_nitrate_fixe")
        with col_p2:
            st.session_state.pas_ml = st.slider("Pas de versement de la molette (mL) :", min_value=0.1, max_value=2.0, value=0.5, step=0.1, disabled=st.session_state.vin_verrouille_tab2)

        if "eau" not in st.session_state:
            st.session_state["eau"] = {
                "Marque : Volvic (Basse teneur)": {"Cl": 15.0},
                "Marque : Évian (Moyenne teneur)": {"Cl": 30.0},
                "Marque : Vittel (Moyenne teneur)": {"Cl": 54.0},
                "Marque : Contrex (Forte teneur)": {"Cl": 41.0},
                "Marque : Courmayeur (Forte teneur)": {"Cl": 68.0},
                "Général : Eau déminéralisée": {"Cl": 1.5},
                "Général : Eau du robinet standard": {"Cl": 35.0}
            }

        info_bouteille = st.session_state["eau"].get(bouteille_selectionnee, {"Cl": 35.0})
        teneur_cl_nominale = info_bouteille.get("Cl", 35.0)
        teneur_cl_nominale = info_bouteille["Cl"] # mg/L
        
        # Déduction de la concentration de l'échantillon en mol/L avec l'aléa
        c_chlorure_simulee = ((teneur_cl_nominale / 1000.0) / M_cl) * coeff_alea
        
        # Masse d'ions chlorure présente dans les 40 mL de prise d'essai (en g)
        st.session_state.masse_reelle_g = c_chlorure_simulee * (V_ini / 1000.0) * M_cl
        masse_affichee_mg = st.session_state.masse_reelle_g * 1000.0

        # Relation stœchiométrique à l'équivalence de Mohr : n(Ag+) = n(Cl-) => C0 * VE = C_cl * V_ini
        if C_base > 0:
            v_eq_theorique_calcul = (c_chlorure_simulee * V_ini / C_base) * 1000.0
            if v_eq_theorique_calcul > v_max_ml:
                v_eq_theorique_calcul = 22.40
        else:
            v_eq_theorique_calcul = 12.0

        st.session_state["th_vrai_veq_calc"] = round(float(v_eq_theorique_calcul), 2)
        st.session_state["input_at2_ve_lu_eleve"] = round(float(v_eq_theorique_calcul), 2)

        st.info(
            f"Composé dosé : Ions Chlorure (Cl-) | Prise d'essai V_a : {V_ini:.1f} mL | "
            f"Masse contenue (aléatoire) : {masse_affichee_mg:.2f} mg | "
            f"Indicateur : Chromate de potassium (1 mL)"
        )
        st.divider()

    v_eq_visuel = st.session_state.th_vrai_veq_calc
    
    # --- CHAINE HTML DE L'ANIMATION DE MOHR (PRÉCIPITÉ AgCl ET VIRAGE) ---
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
            ctx.fillStyle = 'rgba(226, 232, 240, 0.9)'; ctx.fillRect(141.5, 41.5 + (156 - hauteurBurette), 17, hauteurBurette);

            ctx.fillStyle = '#0284c7'; ctx.font = 'bold 11px sans-serif';
            ctx.fillText(vVerse.toFixed(1) + ' mL', 165, 45 + (156 - hauteurBurette));

            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 215 : 235;
                ctx.fillStyle = '#cbd5e1'; ctx.beginPath(); ctx.arc(150, yGoutte, 2, 0, 2 * Math.PI); ctx.fill();
            }}

            ctx.strokeStyle = '#34495e'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(105, 220); ctx.lineTo(105, 290); ctx.lineTo(205, 290); ctx.lineTo(205, 220); ctx.stroke();

            // Évolution de la couleur du milieu : Jaune initial (Chromate) -> Précipité blanc laiteux -> Rouge brique
            let couleurSol = "#fef08a"; // Teinte jaune initiale
            let nomTeinte = "Jaune limpide (Ions CrO42-)";
            
            if (vVerse > 0 && vVerse < vEq) {{
                couleurSol = "#f1f5f9"; // Précipité blanc d'AgCl
                nomTeinte = "Trouble blanc laiteux (Précipité AgCl)";
            }} else if (Math.abs(vVerse - vEq) <= 0.4) {{
                couleurSol = "#fca5a5"; 
                nomTeinte = "Teinte orange sensible (Équivalence)";
            }} else if (vVerse > vEq) {{
                couleurSol = "#b91c1c"; // Précipité rouge brique de chromate d'argent
                nomTeinte = "Précipité Rouge Brique persistant (Ag2CrO4)";
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

    if st.button("ENREGISTRER LE VOLUME ÉQUIVALENT RELEVÉ", key="btn_sync_chlorure_2"):
        st.session_state.v_verse_ox = v_max_ml
        st.success(f"Volume équivalent synchronisé avec succès : VE = {v_eq_visuel:.2f} mL")
        st.session_state.vin_verrouille_tab2 = True

    res_q2, res_t12 = generer_le_quiz_analytique_atelier_deux(
        verrouille=st.session_state.get("vin_verrouille_tab2", False)
    )

    verrou_th2 = st.session_state.get("vin_verrouille_tab2", False)

    st.write("---")
    st.subheader("Généralités sur les ions chlorures d'une eau")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_cl2_unifie_final_secure_802", use_container_width=True, disabled=verrou_cl2_officiel):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_cl2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            v_acide_dose = 40.0
            v_eq_theorique = st.session_state.get("th_vrai_veq_calc", 12.0)
            C_base = 0.010
            
            moles_argent_equiv = (C_base * v_eq_theorique) / 1000.0
            concentration_cl_attendue = (C_base * v_eq_theorique) / v_acide_dose

            # 1. Correction du Quiz Argentimétrique (sur 10 points)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_ox_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_ox_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_ox_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_ox_q4_tab2") == "n(Ag+) = n(Cl-)",
                st.session_state.get("col_g_quiz_ox_q5_tab2") == f"{moles_argent_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_ox_q6_tab2") == f"{concentration_cl_attendue:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction de la Synthèse de cours Méthode de Mohr (sur 10 points)
            score_t2 = sum([
                st.session_state.get("ox_t1_tab2") == "Burette",
                st.session_state.get("ox_t2_tab2") == "Pipette jaugée",
                st.session_state.get("ox_t3_tab2") == "diviser par 1000",
                st.session_state.get("ox_t4_tab2") == "stoechiometriques",
                st.session_state.get("ox_t5_tab2") == "rouge brique"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU RAPPORT HTML PROPRE ET SYNCHRONISÉ POUR L'EAU ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        v_acide_dose = 40.0
        v_eq_theorique = st.session_state.get("th_vrai_veq_calc", 12.0)
        C_base = 0.010
        moles_argent_equiv = (C_base * v_eq_theorique) / 1000.0

        from datetime import datetime, timedelta
        timestamp_th2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_th2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Ions Chlorure 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Exploitation du dosage argentimétrique des ions chlorure</p>
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
            <div class="sub-title">Solution titrante : Nitrate d'argent | Concentration : {C_base:.3f} mol/L</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question de paillasse demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Concentration molaire de la solution titrante de AgNO3 (C0)</td><td>{st.session_state.get("col_g_quiz_ox_q1_tab2", "Choisir...")}</td><td>{C_base:.3f} mol/L</td></tr>
                    <tr><td>2</td><td>Volume d'échantillon d'eau introduit dans le bécher (Va)</td><td>{st.session_state.get("col_g_quiz_ox_q2_tab2", "Choisir...")}</td><td>{v_acide_dose:.1f} mL</td></tr>
                    <tr><td>3</td><td>Volume equivalent exact (VE) de nitrate d'argent verse</td><td>{st.session_state.get("col_g_quiz_ox_q3_tab2", "Choisir...")}</td><td>{v_eq_theorique:.1f} mL</td></tr>
                    <tr><td>4</td><td>Relation stoechiometrique a l'equivalence</td><td>{st.session_state.get("col_g_quiz_ox_q4_tab2", "Choisir...")}</td><td>n(Ag+) = n(Cl-)</td></tr>
                    <tr><td>5</td><td>Quantite de matiere d'ions argent apportee a l'equivalence</td><td>{st.session_state.get("col_g_quiz_ox_q5_tab2", "Choisir...")}</td><td>{moles_argent_equiv:.5f} mol</td></tr>
                    <tr><td>6</td><td>Concentration molaire en ions chlorure deduite (Ca)</td><td>{st.session_state.get("col_g_quiz_ox_q6_tab2", "Choisir...")}</td><td>{((C_base * v_eq_theorique) / v_acide_dose):.4f} mol/L</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Concept du texte a trous</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Verrerie graduee pour la solution titrante</td><td>{st.session_state.get("ox_t1_tab2", "Choisir...")}</td><td>Burette</td></tr>
                    <tr><td>2</td><td>Verrerie de precision pour prelever l'eau</td><td>{st.session_state.get("ox_t2_tab2", "Choisir...")}</td><td>Pipette jaugée</td></tr>
                    <tr><td>3</td><td>Conversion du volume equivalent en Litres</td><td>{st.session_state.get("ox_t3_tab2", "Choisir...")}</td><td>diviser par 1000</td></tr>
                    <tr><td>4</td><td>Proportions des reactifs a l'equivalence</td><td>{st.session_state.get("ox_t4_tab2", "Choisir...")}</td><td>stoechiometriques</td></tr>
                    <tr><td>5</td><td>Teinte persistante de la fin du dosage de Mohr</td><td>{st.session_state.get("ox_t5_tab2", "Choisir...")}</td><td>rouge brique</td></tr>
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport de dosage argentimétrique de l'Atelier 2 généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Atelier2_Ions_Chlorures_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_th2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )
            

with tab3:
    st.header("Calcul théorique et vérification de l'étiquette")
    st.caption("Détermination de la concentration en ion chlorure d'une eau")

    if "vin_verrouille_tab3" not in st.session_state: 
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.get("vin_verrouille_tab3", False)

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_titrant_edta", 0.010)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    v_titre_session = 10.0 # Volume initial d'échantillon d'eau prélevé (10.0 mL)
    M_caco3 = 100 # Masse molaire de référence du carbonate de calcium équivalent

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les resultats de votre dosage complexometrique
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On preleve un volume V_eau = 10,0 mL d'eau minerale de source à l'aide d'une pipette jaugee que l'on titre par la solution d'EDTA.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq releve = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Concentration EDTA C_0 = {c_base_session:.3f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Volume eau dose = {v_titre_session:.1f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M(CaCO3) = {M_caco3:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; 1 degre francais (1 °f) = 10 mg/L de CaCO3</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # --- APPEL SÉCURISÉ DU QUESTIONNAIRE DE SAISIE DE L'EAU ---
    try:
        dict_saisies_eleve = afficher_questions_durete_eau_commerciale(verrouille=verrou_at3)
    except NameError:
        dict_saisies_eleve = {}

    # --- CALCULS EXPÉRIMENTAUX DE RÉFÉRENCE DE LA SESSION ALÉATOIRE ---
    att_v_eq_l = v_eq_session / 1000.0
    att_n_edta = c_base_session * att_v_eq_l
    att_n_ions = att_n_edta
    att_c_molaire = att_n_ions / (v_titre_session / 1000.0)
    att_c_mmol = att_c_molaire * 1000.0
    
    # Équivalence massique calcaire CaCO3
    att_t_massique = att_c_molaire * M_caco3
    att_t_mg = att_t_massique * 1000.0
    att_th_degre = att_t_mg / 10.0

    # Classification hydrotimétrique automatique
    if att_th_degre < 7.0:
        att_conclusion = "Eau tres douce (TH inferieur a 7 °f)"
    elif 7.0 <= att_th_degre < 15.0:
        att_conclusion = "Eau douce ou de durete moyenne (TH entre 7 et 15 °f)"
    elif 15.0 <= att_th_degre <= 30.0:
        att_conclusion = "Eau dure (TH entre 15 et 30 °f)"
    else:
        att_conclusion = "Eau tres dure ou incrustante (TH superieur a 30 °f)"

    # --- CASE À COCHER DE CERTIFICATION ---
    case_certif_th3 = st.checkbox(
        "Je certifie avoir complete l'integralite des calculs d'exploitation de l'Atelier 3.", 
        key="check_certif_th3_final_net", 
        disabled=verrou_at3
    )

    # --- BOUTON DE VALIDATION ET NOTATION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_th3_official_net", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_th3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Barème d'évaluation de la grille analytique (sur 20 points)
            score_at3_total = 0.0
            import numpy as np
            
            # Évaluation du Bloc Bleu (Bécher)
            if np.isclose(st.session_state.get("at3_v_eq_l_th", 0.0), att_v_eq_l, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_n_edta_th", 0.0), att_n_edta, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_n_ions_becher_th", 0.0), att_n_ions, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_c_molaire_th", 0.0), att_c_molaire, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_c_mmol_th", 0.0), att_c_mmol, rtol=0.02): score_at3_total += 2.5
            
            # Évaluation du Bloc Jaune (Unités Hydrotimétriques)
            if np.isclose(st.session_state.get("at3_t_massique_th", 0.0), att_t_massique, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_t_mg_th", 0.0), att_t_mg, rtol=0.02): score_at3_total += 2.5
            if np.isclose(st.session_state.get("at3_valeur_th_degre", 0.0), att_th_degre, rtol=0.02): score_at3_total += 2.5
            
            # Évaluation de la conclusion sur le TH
            if st.session_state.get("at3_conclusion_durete_eau") == att_conclusion: score_at3_total += 2.5

            st.session_state["score_final_vin3"] = round(min(20.0, score_at3_total), 1)
            st.session_state["vin_verrouille_tab3"] = True
            st.rerun()

    # --- CONTEXTE DU BILAN SCELLÉ ET PATHWAY DU RAPPORT HTML HYDROTIMÉTRIQUE ---
    if st.session_state.get("vin_verrouille_tab3", False):
        tot_s3 = st.session_state.get("score_final_vin3", 0.0)

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import datetime, timedelta
        timestamp_th3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")
        
        html_export_th3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Durete de l'eau 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Exploitation quantitative du dosage complexometrique du TH</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_th3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue aux calculs sur le becher : <strong>{min(10.0, tot_s3):.1f} / 10</strong><br>
                &bull; Note obtenue a la determination du TH : <strong>{max(0.0, tot_s3 - 10.0):.1f} / 10</strong><br>
                &bull; Note Finale de l'Atelier 3 : <strong>{tot_s3:.1f} / 20</strong>
            </p>
            <div class="sub-title">Solution titrante : EDTA | Concentration : {c_base_session:.3f} mol/L</div>

            <div class="sub-title">DETAILS DE VOS CALCULS DE LABORATOIRE</div>
            <table>
                <thead>
                    <tr><th>Grandeur Mathematique / Etape</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        lignes_rapport3 = [
            ("Volume equivalent d'EDTA en litre (L)", "at3_v_eq_l_th", f"{att_v_eq_l:.5f} L", att_v_eq_l, 0.02),
            ("Quantite de matiere d'EDTA versee (mol)", "at3_n_edta_th", f"{att_n_edta:.6f} mol", att_n_edta, 0.02),
            ("Quantite totale d'ions metalliques du becher (mol)", "at3_n_ions_becher_th", f"{att_n_ions:.6f} mol", att_n_ions, 0.02),
            ("Concentration molaire totale Ca (mol/L)", "at3_c_molaire_th", f"{att_c_molaire:.5f} mol/L", att_c_molaire, 0.02),
            ("Concentration molaire equivalente (mmol/L)", "at3_c_mmol_th", f"{att_c_mmol:.2f} mmol/L", att_c_mmol, 0.02),
            ("Titre massique equivalent en CaCO3 (g/L)", "at3_t_massique_th", f"{att_t_massique:.3f} g/L", att_t_massique, 0.02),
            ("Titre massique equivalent en CaCO3 (mg/L)", "at3_t_mg_th", f"{att_t_mg:.1f} mg/L", att_t_mg, 0.02),
            ("Valeur du Titre Hydrotimetrique TH (°f)", "at3_valeur_th_degre", f"{att_th_degre:.1f} °f", att_th_degre, 0.02),
        ]

        import numpy as np
        for desc, key, txt_att, val_att, tol in lignes_rapport3:
            saisie_raw = str(st.session_state.get(key, "0.0")).replace(",", ".")
            try: saisie_val = float(saisie_raw)
            except: saisie_val = -999.0
            v_lbl = "CORRECT" if np.isclose(saisie_val, val_att, rtol=tol) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_th3 += f"<tr><td>{desc}</td><td>{saisie_raw}</td><td>{txt_att}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        saisie_concl = st.session_state.get("at3_conclusion_durete_eau", "Choisir...")
        v_lbl_c = "CORRECT" if saisie_concl == att_conclusion else "INCORRECT"
        v_class_c = "status-correct" if v_lbl_c == "CORRECT" else "status-incorrect"
        html_export_th3 += f"<tr><td>Conclusion et classification de la durete de l'eau</td><td>{saisie_concl}</td><td>{att_conclusion}</td><td class='{v_class_c}'>{v_lbl_c}</td></tr>"

        html_export_th3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'exploitation hydrotimetrique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"Durete_Eau3_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace("\\", "_")
        
        st.success(f"ATELIER DURETÉ DE L'EAU 3 SCELLÉ | Note de session : {tot_s3} / 20")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_th3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )


















