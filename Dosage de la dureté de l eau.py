# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dureté de l eau",
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
st.title("Application dureté de l'eau")
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
    st.session_state.eau = {
            "Marque : Volvic ": {"Ca": 11.5, "Mg": 8.0},
            "Marque : Evian ": {"Ca": 80.0, "Mg": 26.0},
            "Marque : Vittel ": {"Ca": 240.0, "Mg": 42.0},
            "Marque : Contrex ": {"Ca": 468.0, "Mg": 74.8},
            "Marque : Hépar ": {"Ca": 549.0, "Mg": 119.0},
            "Général : Eau déminéralisée ": {"Ca": 2.0, "Mg": 1.0},
            "Général : Eau douce standard": {"Ca": 60.0, "Mg": 15.0},
            "Général : Eau du robinet standard": {"Ca": 120.0, "Mg": 30.0},
            "Général : Eau dure ": {"Ca": 200.0, "Mg": 50.0},
            "Général : Eau très dure ": {"Ca": 300.0, "Mg": 80.0},
            " Aléatoire ": "RANDOM"
        }  #  en mg / L

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
    "Généralités sur la dureté de l'eau",
    "Dosage colorimétrique de la dureté de l'eau",
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

    # Recouvrement des constantes calculees du moteur de paillasse pour la durete de l'eau
    v_eq_attendu = st.session_state.get("th_vrai_veq_calc", 12.0)
    c_base_session = st.session_state.get("c_titrant", 0.010) # Concentration standard de l'EDTA (mol/L)
    v_eau_dosee = 50.0 # Volume initial d'echantillon d'eau Va mis dans le becher (50 mL standard)

    # Calcul des moles d'EDTA versees a l'equivalence : n = C_EDTA * Ve
    n_edta_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # A l'equivalence n_ions = n_EDTA (complexation mole a mole)
    c_ions_dose_attendu = (c_base_session * v_eq_attendu) / v_eau_dosee

    col_double_quiz_th, col_double_trous_th = st.columns(2)

    with col_double_quiz_th:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante d'EDTA ($C_b$) utilisee ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_th_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_eau_dosee:.1f} mL", "10.0 mL", "20.0 mL"]
        st.write("**2.** Quel volume d'echantillon d'eau analyse ($V_a$) a ete introduit dans le becher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_th_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume equivalent exact ($V_E$) d'EDTA verse releve a la rupture ou changement de teinte ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_th_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stoechiometrique a l'equivalence pour ce titrage complexometrique ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Ca * Va = Cb * Ve", "Ca * Cb = Va * Ve", "Ca / Va = Cb / Ve"], key="col_g_quiz_th_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_edta_equiv:.5f} mol", f"{n_edta_equiv * 10:.5f} mol", "0.00100 mol"]
        st.write("**5.** Quelle quantite de matiere de l'agent complexant EDTA a ete apportee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_th_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_ions_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Deduisez-en la concentration molaire totale en ions alcalino-terreux ($C_a$) dans le becher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_th_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_th:
        st.markdown("##### Synthese de cours (Texte a trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee verifiant l'ajout millilitre par millilitre de la solution d'EDTA est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Eprouvette graduee", "Pipette jaugee"], key="th_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prelever les 50 mL d'echantillon d'eau de maniere precise et repetitive, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugée", "Eprouvette graduee", "Fioles"], key="th_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour convertir le volume equivalent experimental de mL en Litres, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="th_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point equivalent, les ions metalliques et le chelateur ont reagis dans des proportions")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="th_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Lors d'un suivi colorimetrique avec le NET, l'equivalence correspond au virage net vers le")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "bleu azur", "rose violace", "jaune vif"], key="th_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous


def afficher_questions_durete_eau1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_th" not in st.session_state:
        base_quiz1_th = [
            {"id": "q1_1", "q": "La durete d'une eau (titre hydrotimetrique TH) evalue la concentration en ions :", "type": "menu", "options": ["calcium et magnesium", "sodium et chlorure", "nitrate et sulfate"], "rep": "calcium et magnesium"},
            {"id": "q1_2", "q": "D'apres la classification, quelle est la masse molaire de l'element Calcium (Ca) en g/mol ?", "type": "menu", "options": ["40,1", "24,3", "16,0"], "rep": "40,1"},
            {"id": "q1_3", "q": "Quel est le nom de la molecule complexante utilisee pour doser la durete de l'eau ?", "type": "menu", "options": ["EDTA", "Soude", "Acide chlorhydrique"], "rep": "EDTA"},
            {"id": "q1_4", "q": "D'apres la classification, quelle est la masse molaire de l'element Magnesium (Mg) en g/mol ?", "type": "menu", "options": ["24,3", "40,1", "1,0"], "rep": "24,3"},
            {"id": "q1_5", "q": "Une eau calcaire contenant beaucoup d'ions Ca2+ et Mg2+ est qualifiee d'eau :", "type": "menu", "options": ["dure", "douce", "demineralisee"], "rep": "dure"},
            {"id": "q1_6", "q": "En France, l'unite usuelle pour exprimer la durete de l'eau est le :", "type": "menu", "options": ["degre francais (°f)", "degre Dornic (°D)", "degre Celsius (°C)"], "rep": "degre francais (°f)"},
            {"id": "q1_7", "q": "A quoi correspond la valeur de 1 degre francais (1 °f) en concentration d'ions ?", "type": "menu", "options": ["10 mg/L de CaCO3", "1 mg/L de CaCO3", "100 mg/L de CaCO3"], "rep": "10 mg/L de CaCO3"},
            {"id": "q1_8", "q": "Quelle est la formule chimique du calcaire (tartre) qui se depose dans les canalisations ?", "type": "menu", "options": ["CaCO3", "NaCl", "H2O"], "rep": "CaCO3"},
            {"id": "q1_9", "q": "Quelle couleur prend l'indicateur NET lorsqu'il est lie aux ions metalliques Ca2+/Mg2+ ?", "type": "menu", "options": ["Rose violace", "Bleu azur", "Jaune"], "rep": "Rose violace"},
            {"id": "q1_10", "q": "Pour realiser ce titrage complexometrique, le pH de la solution doit etre tamponne a :", "type": "menu", "options": ["10", "4", "7"], "rep": "10"}
        ]
        copie_base = list(base_quiz1_th)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_th = copie_base

    col_double_quiz_th1, col_double_trous_th1 = st.columns(2)

    with col_double_quiz_th1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_th, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"th_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_th_{q_data['id']}"
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

    with col_double_trous_th1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Les ions responsables de la durete et de l'entartrage sont le magnesium et le")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "calcium", "sodium", "potassium"], key="th_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La solution titrante utilisee pour pieger ces ions metalliques est l'")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "EDTA", "soude", "acide"], key="th_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire atomique de l'element Calcium (Ca) vaut environ")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "40 g/mol", "24 g/mol", "16,0 g/mol"], key="th_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La masse molaire atomique de l'element Magnesium (Mg) est egale a")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "24 g/mol", "40 g/mol", "12,0 g/mol"], key="th_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Une eau de faible mineralite qui mousse facilement avec le savon est une eau")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "douce", "dure", "calcaire"], key="th_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'indicateur colore de fin de titrage utilise s'appelle le")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "NET", "BBT", "hélianthine"], key="th_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Au point equivalent, la couleur de la solution vire du rose violace au")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "bleu azur", "jaune", "vert"], key="th_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Pour maintenir l'indicateur dans sa zone de virage, on ajoute une solution")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "tampon (pH=10)", "acide", "neutre"], key="th_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Un degre francais (1 °f) represente une concentration equivalente de")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "10 mg/L", "1 mg/L", "100 mg/L"], key="th_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Les eaux dont le TH est superieur a 30 °f sont qualifiees de tres")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "dures", "douces", "pures"], key="th_t10_tab1", disabled=verrouille, label_visibility="collapsed")

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
            "La dureté d'une eau (titre hydrotimétrique TH) évalue la concentration en ions calcium et magnesium contenus dans cette eau. "
            "D'après la classification, la masse molaire de l'élément Calcium (Ca) en g/mol vaut environ 40 g/mol et la masse molaire atomique de l'élément Magnésium (Mg) est égale a 24 g/mol. "
            "On definit le degré de dureté hydrotimétrique comme une grandeur ou un degré francais (1 °f) représente une concentration équivalente de 10 mg/L de CaCO3, ce qui correspond à une concentration en ions de 0,0001 mol/L. "
            "En France, le degré francais (°f) est l'unité usuelle utilisée pour exprimer la dureté, et la formule chimique du calcaire (tartre) qui se depose dans les canalisations s'ecrit CaCO3. "
            "Une eau de faible mineralité qui mousse facilement avec le savon est qualifiée d'eau douce, tandis qu'une eau calcaire contenant beaucoup d'ions Ca2+ et Mg2+ est appelée une eau dure. "
            "Les eaux dont le TH est supérieur a 30 °f sont qualifiées de très dures. "
            "La solution titrante utilisée pour piéger ces ions métalliques est l'EDTA. "
            "Pour réaliser ce titrage complexométrique, le pH de la solution doit être tamponné à 10 en ajoutant une solution tampon (pH=10). "
            "L'indicateur coloré de fin de titrage utilisé s'appelle le NET. "
            "L'indicateur NET prend une couleur rose violacé lorsqu'il est lié aux ions metalliques Ca2+/Mg2+, et au point équivalent, la couleur de la solution vire du rose violacé au bleu azur."
        )
        st.divider()



    with col_droite:
        st.subheader("Modèles Atomiques de Bohr et de Lewis")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Modèle de Bohr**\n\nRépartition des électrons sur les couches K, L, M, N")
        with col_leg2: st.caption("**Modèle de Lewis**\n\nReprésentation des électrons de la couche externe")
        with col_leg3: st.caption("**Données de Valence**\n\nCalcium et Magnésium : 2 électrons de valence")
            
        st.divider()

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # --- 1. REPRÉSENTATION DU MAGNÉSIUM (Z=12 : K2, L8, M2) ---
        cx_mg, cy_mg = 2.2, 2.5
        
        # Noyau du Magnésium
        ax_mol.add_patch(patches.Circle((cx_mg, cy_mg), 0.25, facecolor="#10b981", edgecolor="#1e293b", linewidth=2, zorder=3))
        ax_mol.text(cx_mg, cy_mg, "Mg", color="white", weight="bold", fontsize=12, ha="center", va="center", zorder=4)
        
        # Orbites de Bohr (Couches K, L, M)
        ax_mol.add_patch(patches.Circle((cx_mg, cy_mg), 0.5, facecolor="none", edgecolor="#cbd5e1", linestyle="--", linewidth=1, zorder=2))
        ax_mol.add_patch(patches.Circle((cx_mg, cy_mg), 0.9, facecolor="none", edgecolor="#cbd5e1", linestyle="--", linewidth=1, zorder=2))
        ax_mol.add_patch(patches.Circle((cx_mg, cy_mg), 1.3, facecolor="none", edgecolor="#64748b", linestyle="-", linewidth=1.5, zorder=2))
        
        # Électrons sur la couche externe M (2 électrons de valence)
        ax_mol.add_patch(patches.Circle((cx_mg, cy_mg + 1.3), 0.05, facecolor="#1e293b", edgecolor="none", zorder=5))
        ax_mol.add_patch(patches.Circle((cx_mg, cy_mg - 1.3), 0.05, facecolor="#1e293b", edgecolor="none", zorder=5))
        
        # Représentation de Lewis du Magnésium juste en dessous
        ax_mol.text(cx_mg, cy_mg - 1.8, "• Mg •", fontname="Arial", fontsize=14, weight="bold", color="#10b981", ha="center")

        # --- 2. REPRÉSENTATION DU CALCIUM (Z=20 : K2, L8, M8, N2) ---
        cx_ca, cy_ca = 6.2, 2.5
        
        # Noyau du Calcium
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca), 0.25, facecolor="#f59e0b", edgecolor="#1e293b", linewidth=2, zorder=3))
        ax_mol.text(cx_ca, cy_ca, "Ca", color="white", weight="bold", fontsize=12, ha="center", va="center", zorder=4)
        
        # Orbites de Bohr (Couches K, L, M, N)
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca), 0.4, facecolor="none", edgecolor="#cbd5e1", linestyle="--", linewidth=1, zorder=2))
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca), 0.7, facecolor="none", edgecolor="#cbd5e1", linestyle="--", linewidth=1, zorder=2))
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca), 1.0, facecolor="none", edgecolor="#cbd5e1", linestyle="--", linewidth=1, zorder=2))
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca), 1.3, facecolor="none", edgecolor="#64748b", linestyle="-", linewidth=1.5, zorder=2))
        
        # Électrons sur la couche externe N (2 électrons de valence)
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca + 1.3), 0.05, facecolor="#1e293b", edgecolor="none", zorder=5))
        ax_mol.add_patch(patches.Circle((cx_ca, cy_ca - 1.3), 0.05, facecolor="#1e293b", edgecolor="none", zorder=5))
        
        # Représentation de Lewis du Calcium juste en dessous
        ax_mol.text(cx_ca, cy_ca - 1.8, "• Ca •", fontname="Arial", fontsize=14, weight="bold", color="#f59e0b", ha="center")

        ax_mol.set_xlim(0.5, 8.0)
        ax_mol.set_ylim(0.2, 4.8)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import random

        fig_box, ax_box = plt.subplots(figsize=(7, 5.5), facecolor="white")
        ax_box.set_facecolor("white")
        
        # Alignement strict sur le repère d'origine (0 en haut)
        ax_box.set_ylim(500, 0)
        ax_box.set_xlim(0, 700)

        # 1. Le corps principal de la fiche d'analyse (Bords arrondis simulés par rectangle)
        ax_box.add_patch(patches.Rectangle((150, 20), 400, 460, facecolor="white", edgecolor="#0000bb", linewidth=4, zorder=1))
        
        # 2. Le bandeau de titre supérieur (Bleu foncé)
        ax_box.add_patch(patches.Rectangle((152, 22), 396, 45, facecolor="#0000bb", edgecolor="none", zorder=2))
        ax_box.text(170, 45, "COMPOSITION MOYENNE", fontname="Arial", fontsize=16, weight="bold", color="white", ha="left", va="center", zorder=3)
        ax_box.text(525, 45, "mg/l", fontname="Arial", fontsize=14, style="italic", color="white", ha="right", va="center", zorder=3)

        # 3. Tableau détaillé des teneurs minérales de l'étiquette (Lignes de texte et pointillés)
        elements_analyse = [
            ("CALCIUM", "55", 100),
            ("MAGNESIUM", "19", 135),
            ("POTASSIUM", "1", 170),
            ("SODIUM", "24", 205),
            ("BICARBONATE", "248", 240),
            ("CHLORURE", "37", 275),
            ("SULFATE", "13", 310),
            ("NITRATE", "<0.1", 345),
            ("FLUOR", "0", 380),
            ("SILICE", "0", 415)
        ]

        for nom, val, y_pos in elements_analyse:
            # Libellé du minéral à gauche
            ax_box.text(170, y_pos, nom, fontname="Arial", fontsize=11, weight="bold", color="#004499", ha="left", va="center", zorder=3)
            # Valeur numérique à droite
            ax_box.text(530, y_pos, val, fontname="Arial", fontsize=12, weight="bold", color="#004499", ha="right", va="center", zorder=3)
            
            # Génération des pointillés de liaison
            points_x = np.linspace(290, 490, 25)
            points_y = np.full_like(points_x, y_pos + 2)
            ax_box.scatter(points_x, points_y, color="#94a3b8", s=1.5, zorder=2)

        # 4. Bloc des mentions de résidu sec et caractéristiques physico-chimiques
        ax_box.text(170, 445, "RESIDU A 180°C ... 280", fontname="Arial", fontsize=11, weight="bold", color="#0000bb", ha="left", va="center", zorder=3)
        ax_box.text(170, 470, "pH  .................... 7.4", fontname="Arial", fontsize=12, weight="bold", color="#0000bb", ha="left", va="center", zorder=3)

        ax_box.axis("off")
        st.pyplot(fig_box)
        st.divider()




    res_q1, res_t1 = afficher_questions_durete_eau1_dynamiques(
        verrouille=st.session_state.get("vin_verrouille_tab1", False)
    )

    verrou_th1 = st.session_state.get("vin_verrouille_tab1", False)

    st.write("---")
    st.subheader("Généralité sur la dureté de l'eau (TH)")

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
            # 1. Correction automatique du Quiz de gauche (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_th" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_th:
                    reponse_eleve = st.session_state.get(f"th_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 cases)
            score_t1 = sum([
                st.session_state.get("th_t1_tab1") == "calcium",
                st.session_state.get("th_t2_tab1") == "EDTA",
                st.session_state.get("th_t3_tab1") == "40 g/mol",
                st.session_state.get("th_t4_tab1") == "24 g/mol",
                st.session_state.get("th_t5_tab1") == "douce",
                st.session_state.get("th_t6_tab1") == "NET",
                st.session_state.get("th_t7_tab1") == "bleu azur",
                st.session_state.get("th_t8_tab1") == "tampon (pH=10)",
                st.session_state.get("th_t9_tab1") == "10 mg/L",
                st.session_state.get("th_t10_tab1") == "dures"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- SCELLÉ ET COMPILATION DU RAPPORT HTML POUR LA DURETÉ DE L'EAU ---
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
            <title>Rapport Durete de l'eau 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Analyse hydrotimetrique - Titre Hydrotimetrique (TH)</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_th1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Nomenclature Hydrotimetrique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue a la Synthese des proprietes des eaux : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_th" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_th, 1):
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
            "1. Les ions responsables de la durete et de l'entartrage sont le magnesium et le",
            "2. La solution titrante utilisee pour pieger ces ions metalliques est l'",
            "3. La masse molaire atomique de l'element Calcium (Ca) vaut environ",
            "4. La masse molaire atomique de l'element Magnesium (Mg) est egale a",
            "5. Une eau de faible mineralite qui mousse facilement avec le savon est une eau",
            "6. L'indicateur colore de fin de titrage utilise s'appelle le",
            "7. Au point equivalent, la couleur de la solution vire du rose violace au",
            "8. Pour maintenir l'indicateur dans sa zone de virage, on ajoute une solution",
            "9. Un degre francais (1 °f) represente une concentration equivalente de",
            "10. Les eaux dont le TH est superieur a 30 °f sont qualifiees de tres"
        ]
        attendus_trous1 = ["calcium", "EDTA", "40 g/mol", "24 g/mol", "douce", "NET", "bleu azur", "tampon (pH=10)", "10 mg/L", "dures"]

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

        nom_f1 = f"Rapport_Atelier1_Durete_Eau_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_th1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Dosage complexométrique de la dureté de l'eau")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage des ions calcium et magnésium par l'EDTA")

    # Initialisation des etats de session specifiques a la durete de l'eau
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse_th" not in st.session_state: st.session_state.v_verse_th = 0.0
    if "c_titrant_edta" not in st.session_state: st.session_state.c_titrant_edta = 0.010
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    
    liste_marques_disponibles = list(st.session_state.eau.keys())
    
    eau_selectionnee = st.selectbox(
        "Sélectionnez l'échantillon d'eau minérale à analyser :",
        options=liste_marques_disponibles,
        index=0,
        disabled=st.session_state.vin_verrouille_tab2,
        key="choix_marque_eau_utilisateur"
    )

    # Initialisation unique du coefficient de variation aléatoire anti-triche de session
    if "facteur_anti_triche" not in st.session_state:
        import random
        st.session_state.facteur_anti_triche = random.uniform(0.97, 1.03)

    coeff_alea = st.session_state.facteur_anti_triche

    # Récupération ou génération des données minérales (mg/L) d'après le choix utilisateur
    if "Aléatoire" in eau_selectionnee:
        # Génération déterministe d'un échantillon inconnu si choix aléatoire
        ca_mg_l = 150.0
        mg_mg_l = 40.0
    else:
        donnees_minerales = st.session_state.eau[eau_selectionnee]
        ca_mg_l = donnees_minerales["Ca"]
        mg_mg_l = donnees_minerales["Mg"]

    # Application du facteur d'aléa individuel secret sur les concentrations lues
    ca_mg_l_aleamise = ca_mg_l * coeff_alea
    mg_mg_l_aleamise = mg_mg_l * coeff_alea

    # --- CALCULS ANALYTIQUES DES ATTENDUS DU DOSAGE ---
    M_ca = 40
    M_mg = 24
    M_caco3 = 100
    v_max_ml = 25.0
    V_ini = 10.0  # Volume de la prise d'essai d'eau (10.0 mL)

    # Conversion des masses (mg/L) en concentrations molaires (mol/L)
    c_ca_mol = (ca_mg_l_aleamise / 1000.0) / M_ca
    c_mg_mol = (mg_mg_l_aleamise / 1000.0) / M_mg
    C_total_ions_reel = c_ca_mol + c_mg_mol

    # Lecture de la concentration de l'EDTA titrant
    C_base = st.session_state.get("c_titrant_edta", 0.010)

    # Détermination du véritable volume d'équivalence V_E (mL) de cette séance
    if C_base > 0:
        v_eq_theorique = (C_total_ions_reel * V_ini) / C_base
        if v_eq_theorique > v_max_ml:
            v_eq_theorique = 22.4
            C_total_ions_reel = (C_base * v_eq_theorique) / V_ini
    else:
        v_eq_theorique = 0.0

    # Enregistrement des valeurs de référence pour la correction automatique de l'Atelier 3
    st.session_state.th_vrai_veq_calc = round(float(v_eq_theorique), 2)
    st.session_state.th_vrai_c_total = float(C_total_ions_reel)
    st.session_state.session_eau_tiree = eau_selectionnee
    
    v_eq_visuel = v_eq_theorique

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-à-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            C_base = st.number_input(
                "Concentration de l'EDTA C_0 (mol/L) :",
                min_value=0.001, max_value=2.0, value=float(st.session_state.c_titrant_edta), step=0.001,
                format="%.3f",
                disabled=st.session_state.vin_verrouille_tab2, key="c_titrant_edta"
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

    # Affichage des informations de la session hydrotimétrique
    st.info(f"Échantillon : {st.session_state.get('session_eau_tiree', 'Non selectionne')} | Volume d'eau dosé : {V_ini:.1f} mL | Solution titrante d'EDTA : {C_base:.3f} mol/L")
    st.divider()

    v_eq_affiche = v_eq_theorique
    ph_eq_affiche = 10.0

    # --- TRANSMISSION DES COULEURS DE L'INDICATEUR NET ---
    ind_data = st.session_state.indicateurs[choix_ind]
    c_acide = ind_data["couleur_acide"]
    c_zone = ind_data["couleur_zone"]
    c_base = ind_data["couleur_base"]

    
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
        
        let vVerse = {st.session_state.get("v_verse_th", 0.0)};
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

            // 2. Burette Graduée (EDTA)
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

            // 4. Bécher d'Eau minérale
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(105, 230); ctx.lineTo(105, 310); ctx.lineTo(205, 310); ctx.lineTo(205, 230);
            ctx.stroke();

            let couleurSol = colorAcide; 
            let nomTeinte = 'Initiale';
            if (Math.abs(vVerse - vEq) <= 0.4) {{
                couleurSol = colorZone; 
                nomTeinte = 'Équivalence (NET)';
            }} else if (vVerse > vEq) {{
                couleurSol = colorBase; 
                nomTeinte = 'EDTA Libre';
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

            // 5. Capteur de conductivité
            ctx.fillStyle = '#34495e';
            ctx.fillRect(182, 210, 12, 85); 
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(188, 210); ctx.lineTo(188, 170); ctx.lineTo(215, 170); ctx.stroke(); 

            // 6. Boîtier conductimètre (Suivi σ)
            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(215, 140, 42, 45);
            
            ctx.fillStyle = '#2ecc71';
            ctx.font = 'bold 9px monospace';
            let txtCond = (vVerse === 0) ? '0.45' : (0.45 + (vVerse * 0.015)).toFixed(2);
            ctx.fillText('mS: ' + txtCond, 217, 166);

            ctx.fillStyle = '#334155';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText('NET : ' + nomTeinte, 150, 365);

            setTimeout(() => {{
                requestAnimationFrame(drawScene);
            }}, 500);
        }}

        drawScene();
    </script>
    """
    
    # Rendu du canvas HTML5 dans votre onglet 2
    components.html(html_animation_paillasse, height=430)

    if st.button("AFFICHER LES RÉSULTATS DU TITRAGE", key="btn_sync_paillasse_final", use_container_width=True):
        st.session_state.v_verse_th = v_max_ml
        st.rerun()

    v_eq_affiche = st.session_state.get("th_vrai_veq_calc", 12.0)
    
    texte_resultats = (
        f"Reperes d'equivalence de la session : "
        f"Volume equivalent Veq = {v_eq_affiche:.2f} mL"
    )
    
    if st.session_state.get("v_verse_th", 0.0) >= v_max_ml or st.session_state.get("vin_verrouille_tab2", False):
        st.success(texte_resultats)
        st.session_state["input_at2_ve_lu_eleve"] = v_eq_affiche

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # Configuration des variables compatibles avec le quiz de la durete de l'eau (V_eau = 10.0 mL)
    v_eq_theorique = st.session_state.get("th_vrai_veq_calc", 12.0)
    C_base = st.session_state.get("c_titrant_edta", 0.010)
    v_acide_dose = 10.0 # CORRECTION : Volume initial d'eau dans le becher passe a 10.0 mL

    verrou_th2 = st.session_state.get("vin_verrouille_tab2", False)

    if not st.session_state.get("animation_active", False):
        try:
            generer_le_quiz_analytique_atelier_deux(verrouille=verrou_th2)
        except NameError:
            pass
    else:
        st.info("Le versement de l'EDTA est en cours... Le formulaire d'évaluation s'affichera dès que l'animation sera terminée.")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_th2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.", 
        key="check_certif_th2_final_net", 
        disabled=verrou_th2
    )

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_th2_official_net", use_container_width=True, disabled=verrou_th2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_th2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Attendus théoriques exacts pour le barème hydrotimétrique recalcules sur 10 mL
            n_edta_equiv = (C_base * v_eq_theorique) / 1000.0
            c_ions_dose_attendu = (C_base * v_eq_theorique) / v_acide_dose

            # 1. Correction du Quiz (sur 10 points)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_th_q1_tab2") == f"{C_base:.3f} mol/L",
                st.session_state.get("col_g_quiz_th_q2_tab2") == f"{v_acide_dose:.1f} mL",
                st.session_state.get("col_g_quiz_th_q3_tab2") == f"{v_eq_theorique:.1f} mL",
                st.session_state.get("col_g_quiz_th_q4_tab2") == "Ca * Va = Cb * Ve",
                st.session_state.get("col_g_quiz_th_q5_tab2") == f"{n_edta_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_th_q6_tab2") == f"{c_ions_dose_attendu:.4f} mol/L"
            ]) * (10.0 / 6.0)

            # 2. Correction de la Synthèse de cours (sur 10 points)
            score_t2 = sum([
                st.session_state.get("th_t1_tab2") == "Burette",
                st.session_state.get("th_t2_tab2") == "Pipette jaugée",
                st.session_state.get("th_t3_tab2") == "diviser par 1000",
                st.session_state.get("th_t4_tab2") == "stoechiometriques",
                st.session_state.get("th_t5_tab2") == "bleu azur"
            ]) * (10.0 / 5.0)

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.verrouille_tab2_asp = True
            st.rerun()

    # --- COMPILATION DU RAPPORT HTML PROPRE ET SYNCHRONISÉ POUR L'EAU ---
    if st.session_state.get("verrouille_tab2_asp", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_th2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_th2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Durete de l'eau 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Exploitation du dosage complexometrique de l'eau</p>
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
            <div class="sub-title">Solution titrante : EDTA | Concentration : {C_base:.3f} mol/L</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question de paillasse demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Concentration molaire de la solution titrante d'EDTA (Cb)</td><td>{st.session_state.get("col_g_quiz_th_q1_tab2", "Choisir...")}</td><td>{C_base:.3f} mol/L</td></tr>
                    <tr><td>2</td><td>Volume d'echantillon d'eau de source introduit (Va)</td><td>{st.session_state.get("col_g_quiz_th_q2_tab2", "Choisir...")}</td><td>{v_acide_dose:.1f} mL</td></tr>
                    <tr><td>3</td><td>Volume equivalent exact (VE) d'EDTA verse</td><td>{st.session_state.get("col_g_quiz_th_q3_tab2", "Choisir...")}</td><td>{v_eq_theorique:.1f} mL</td></tr>
                    <tr><td>4</td><td>Relation stoechiometrique a l'equivalence</td><td>{st.session_state.get("col_g_quiz_th_q4_tab2", "Choisir...")}</td><td>Ca * Va = Cb * Ve</td></tr>
                    <tr><td>5</td><td>Quantite de matiere d'EDTA apportee a l'equivalence</td><td>{st.session_state.get("col_g_quiz_th_q5_tab2", "Choisir...")}</td><td>{(C_base * v_eq_theorique / 1000.0):.5f} mol</td></tr>
                    <tr><td>6</td><td>Concentration molaire totale en ions deduite (Ca)</td><td>{st.session_state.get("col_g_quiz_th_q6_tab2", "Choisir...")}</td><td>{((C_base * v_eq_theorique) / v_acide_dose):.4f} mol/L</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Concept du texte a trous</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Verrerie graduee pour la solution titrante</td><td>{st.session_state.get("th_t1_tab2", "Choisir...")}</td><td>Burette</td></tr>
                    <tr><td>2</td><td>Verrerie de precision pour prelever l'eau</td><td>{st.session_state.get("th_t2_tab2", "Choisir...")}</td><td>Pipette jaugée</td></tr>
                    <tr><td>3</td><td>Conversion du volume equivalent en Litres</td><td>{st.session_state.get("th_t3_tab2", "Choisir...")}</td><td>diviser par 1000</td></tr>
                    <tr><td>4</td><td>Proportions des reactifs a l'equivalence</td><td>{st.session_state.get("th_t4_tab2", "Choisir...")}</td><td>stoechiometriques</td></tr>
                    <tr><td>5</td><td>Reperage du point equivalent avec le NET</td><td>{st.session_state.get("th_t5_tab2", "Choisir...")}</td><td>bleu azur</td></tr>
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse complexometrique de l'Atelier 2 genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Atelier2_Durete_Eau_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_th2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )                    
            

with tab3:
    st.header("Calcul théorique et Bilan Hydrotimétrique")
    st.caption("Détermination du Titre Hydrotimétrique (TH) de l'échantillon d'eau minérale")

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


















