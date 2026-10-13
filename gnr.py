# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application colorant GNR",
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
st.title("Application colorant GNR")
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
    "Généralités sur GNR",
    "Le titre massique du colorant GNR",
    "Pourqoui le colorant reste-t-il?",
    "Fraude ou non",
    ""
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]


def afficher_questions_fraude_gnr(fraudeur=False, verrouille=False):
    import streamlit as st

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE ET DU COEFFICIENT DE DILUTION ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation de l'analyse et de la concentration du colorant</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Estimer la concentration en Solvent Red 24 dans l'extrait concentre (mg/L) :")
    with c2: st.text_input("", value="0.0", key="at3_c_extrait_gnr", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Rappeler le facteur de concentration lie a l'extraction liquide-liquide :")
    with c4: st.text_input("", value="10.0", key="at3_facteur_ext_gnr", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("Calculer la concentration reelle en colorant dans le reservoir suspect (mg/L) :")
    with c6: st.text_input("", value="0.0", key="at3_c_reservoir_gnr", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Rappeler la masse molaire du Solvent Red 24 (g/mol) :")
    with c8: st.text_input("", value="380.44", key="at3_masse_molaire_red24", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("En deduire la concentration molaire en colorant dans le reservoir (mol/L) :")
    with c10: st.text_input("", value="0.0", key="at3_c_molaire_reservoir_gnr", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : DIAGNOSTIC ET CONFORMITÉ ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Diagnostic de conformite et rapport d'enquete</p>", unsafe_allow_html=True)

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("Rappeler le dosage legal en colorant rouge exigé pour le GNR pur (mg/L) :")
    with c12: st.text_input("", value="10.0", key="at3_dosage_legal_gnr", disabled=verrouille, label_visibility="collapsed")

    # Adaptation dynamique des choix de conclusion selon le statut du vehicule genéré
    if fraudeur:
        choix_conclusion = [
            "Choisir...",
            "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)",
            "Erreur de diagnostic : Le carburant est pourtant en regle"
        ]
    else:
        choix_conclusion = [
            "Choisir...",
            "Le vehicule est en regle : Aucun residu de colorant fiscal detecte",
            "Erreur de diagnostic : Une fraude est pourtant suspectee"
        ]

    c13, c14 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c13: st.write("Rendre votre verdict final sur la conformite du carburant inspecte :")
    with c14: st.selectbox(
        "", 
        choix_conclusion, 
        key="at3_conclusion_verdict_gnr", 
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


def afficher_questions_red24_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable mis à jour pour le Solvent Red 24
    ordre_fixe_red24 = [
        {"id": "q1_1", "q": "Le Solvent Red 24 est un colorant principalement qualifié de :", "options": ["liposoluble", "hydrosoluble", "gazeux"], "rep": "liposoluble"},
        {"id": "q1_2", "q": "Calculer la masse molaire du Solvent Red 24 pur (C24H20N4O) en g/mol :", "options": ["380,44", "180,15", "254,32"], "rep": "380,44"},
        {"id": "q1_3", "q": "Quel est l'autre nom ou synonyme courant de laboratoire de cette molécule ?", "options": ["Sudan IV", "Bleu de méthylène", "Phénolphtaléine"], "rep": "Sudan IV"},
        {"id": "q1_4", "q": "Quel est le nombre d'atomes de carbone (C) dans le Solvent Red 24 ?", "options": ["24", "9", "12"], "rep": "24"},
        {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogène (H) dans le Solvent Red 24 ?", "options": ["20", "8", "10"], "rep": "20"},
        {"id": "q1_6", "q": "Quel est le nombre d'atomes d'azote (N) formant les ponts azoïques ?", "options": ["4", "2", "0"], "rep": "4"},
        {"id": "q1_7", "q": "Quelle est la formule brute exacte du Solvent Red 24 ?", "options": ["C24H20N4O", "C9H8O4", "C6H6"], "rep": "C24H20N4O"},
        {"id": "q1_8", "q": "La masse molaire de l'élément Azote (N) vaut environ :", "options": ["14 g/mol", "12 g/mol", "1 g/mol"], "rep": "14 g/mol"},
        {"id": "q1_9", "q": "Quelle couleur conventionnelle représente les atomes d'azote (N) dans le modèle ?", "options": ["Bleu", "Noir", "Blanc"], "rep": "Bleu"},
        {"id": "q1_10", "q": "Dans quelle industrie pétrolière est-il utilisé comme marqueur fiscal ?", "options": ["Gazole Non Routier (GNR)", "Essence Sans Plomb 98", "Kérosène Aviation"], "rep": "Gazole Non Routier (GNR)"}
    ]

    st.session_state.ordre_quiz1_red24 = ordre_fixe_red24

    col_double_quiz_red24, col_double_trous_red24 = st.columns(2)

    with col_double_quiz_red24:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_red24, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"red24_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_red24:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le nom scientifique commun ou synonyme de laboratoire du Solvent Red 24 est")
        with c2: st.selectbox("", ["Choisir...", "Sudan IV", "Sudan I", "Eosine"], key="red24_t1_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale s'écrit")
        with c4: st.selectbox("", ["Choisir...", "C24H20N4O", "C9H8O4", "C12H22O11"], key="red24_t2_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculée à partir de ses éléments constitutifs vaut")
        with c6: st.selectbox("", ["Choisir...", "380,44 g/mol", "180,15 g/mol", "45,00 g/mol"], key="red24_t3_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au sein de son squelette, on compte un nombre total d'atomes de Carbone de")
        with c8: st.selectbox("", ["Choisir...", "24 atomes", "9 atomes", "6 atomes"], key="red24_t4_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre d'atomes d'Hydrogène présents dans la structure vaut")
        with c10: st.selectbox("", ["Choisir...", "20 atomes", "8 atomes", "4 atomes"], key="red24_t5_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le nombre d'atomes d'Azote constituant les ponts azoïques vaut")
        with c12: st.selectbox("", ["Choisir...", "4 atomes", "2 atomes", "0 atome"], key="red24_t6_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Le nombre d'atomes d'Oxygène présents sur sa fonction alcool vaut")
        with c14: st.selectbox("", ["Choisir...", "1 atome", "2 atomes", "4 atomes"], key="red24_t7_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La constante de masse molaire de l'élément atomique Azote (N) vaut")
        with c16: st.selectbox("", ["Choisir...", "14 g/mol", "12 g/mol", "1 g/mol"], key="red24_t8_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. En France, le dosage officiel de ce colorant pour la dénaturation douanière vaut")
        with c18: st.selectbox("", ["Choisir...", "10 mg / L", "5 mg / L", "100 mg / L"], key="red24_t9_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour obtenir l'appellation GNR, il faut obligatoirement lui adjoindre le traceur")
        with c20: st.selectbox("", ["Choisir...", "Accutrace", "Fluorescéine", "Héliantine"], key="red24_t10_tab1_final", disabled=verrouille, label_visibility="collapsed")
        
    return

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
    st.header("Atelier 1 : Généralités sur le GNR")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Document d'étude")

        st.markdown("""
            <style>
            .title-red {
                color: #FF0000;
                font-weight: bold;
                font-size: 20px;
                margin-top: 20px;
                margin-bottom: 10px;
                text-decoration: underline;
            }
            .custom-p {
                text-align: justify;
                margin-bottom: 12px;
                line-height: 1.5;
            }
            .custom-bullet {
                margin-left: 20px;
                text-align: justify;
                margin-bottom: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

        # --- CONTENU DE LA COLONNE GAUCHE MISO EN FORME ---
        
        # Section 1
        st.markdown("<div class='title-red'>1. Coloration des carburants et lubrifiants</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='custom-p'>
            <b>Marquage fiscal et douanier :</b> Il est historiquement utilisé par les gouvernements pour colorer les carburants à taxation réduite (comme le fioul domestique ou le Gazole Non Routier - GNR) afin de les distinguer facilement du carburant routier standard et de détecter les fraudes.
        </div>
        <div class='custom-p'>
            <b>Lubrifiants et huiles moteur :</b> Il sert d'indicateur visuel pour identifier les fuites de fluides hydrauliques, de graisses industrielles ou d'huiles de transmission.
        </div>
        """, unsafe_allow_html=True)

        # Section 2
        st.markdown("<div class='title-red'>2. Industrie des plastiques et polymères</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='custom-p'>
            <b>Coloration de masse :</b> Il est incorporé directement dans la matrice des plastiques rigides ou transparents avant moulage. Il est particulièrement performant avec le polystyrène (PS), les résines acryliques (PMMA), le polycarbonate (PC) et l'ABS.
        </div>
        <div class='custom-p'>
            <b>Stabilité thermique :</b> Il résiste aux hautes températures requises lors des processus d'extrusion et d'injection du plastique.
        </div>
        """, unsafe_allow_html=True)

        # Section 3
        st.markdown("<div class='title-red'>3. Produits d'entretien et cires</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='custom-p'>
            <b>Cires et bougies :</b> Il permet d'obtenir des teintes rouges intenses dans la paraffine, les cires d'abeilles ou végétales, sans perturber la combustion.
        </div>
        <div class='custom-p'>
            <b>Cirages et encres :</b> Il entre dans la formulation de cirages pour chaussures, de teintures pour le cuir et de certaines encres d'imprimerie non aqueuses.
        </div>
        """, unsafe_allow_html=True)

        # Section 4
        st.markdown("<div class='title-red'>4. Biologie et histologie (Application scientifique)</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='custom-p'>
            <b>Coloration des lipides :</b> Connu sous le nom de Sudan IV, il est largement utilisé en laboratoire pour colorer les graisses, les triglycérides et les sections de tissus adipeux dans les analyses microscopiques.
        </div>
        """, unsafe_allow_html=True)

        # Paragraphes Réglementation finaux
        st.markdown("""
        <br>
        <div class='custom-p'>
            En France, selon la réglementation douanière et fiscale pour la dénaturation des carburants (comme le Gazole Non Routier – Farez Fiouls), le dosage officiel du Solvent Red 24 (Rouge écarlate) est fixé à : <b>10 mg / L</b> (ce qui équivaut exactement à 1 gramme par hectolitre ou 10 g pour 1 000 litres).
        </div>
        <div class='custom-p'>
            Pour qu'un carburant soit considéré comme du GNR, l'ajout de ce colorant rouge seul ne suffit pas face aux douanes. La loi impose d'y adjoindre le traceur fiscal européen. Depuis les récentes mises à jour réglementaires, le traceur requis en France est l'<b>Accutrace™</b>, dosé quant à lui entre <b>12,5 et 18,75 mg / L</b>.
        </div>
        """, unsafe_allow_html=True)
        
        st.info("Le document d'étude ci-dessus présente les spécifications officielles du Solvent Red 24 et du traceur Accutrace™.")


    with col_droite:
        st.subheader("Données et Légendes Atomiques (Solvent Red 24)")
        
        col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphère noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Azote (N)**\n\nSphère bleue\nM(N) = 14 g/mol")
        with col_leg4: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(11, 5), facecolor="white")
        ax_mol.set_facecolor("white")

        # --- POSITIONNEMENT DES ATOMES ---
        # 1. Double cycle Naphtol (Gauche)
        n1 = np.array([1.2, 1.5])
        n2 = np.array([1.7, 0.7])
        n3 = np.array([2.7, 0.7])
        n4 = np.array([3.2, 1.5])
        n5 = np.array([2.7, 2.3])
        n6 = np.array([1.7, 2.3])
        n7 = np.array([3.2, 3.1])
        n8 = np.array([2.7, 3.9])
        n9 = np.array([1.7, 3.9])
        n10 = np.array([1.2, 3.1])

        # Oxygène et hydrogène du groupement alcool (-OH)
        o_oh = np.array([3.2, 4.7])
        h_oh = np.array([3.9, 4.5])

        # Hydrogènes périphériques du Naphtol (6 hydrogènes)
        h_n1 = np.array([0.5, 1.5])
        h_n2 = np.array([1.4, 0.0])
        h_n3 = np.array([3.0, 0.0])
        h_n4 = np.array([3.9, 1.5])
        h_n9 = np.array([1.4, 4.6])
        h_n10 = np.array([0.5, 3.1])

        # 2. Premier pont Azoïque
        n_azo1_1 = np.array([4.1, 2.7])
        n_azo1_2 = np.array([4.7, 3.2])

        # 3. Cycle benzénique central
        c_c1 = np.array([5.6, 3.0])
        c_c2 = np.array([6.2, 3.8])
        c_c3 = np.array([7.2, 3.6])
        c_c4 = np.array([7.6, 2.7])
        c_c5 = np.array([7.0, 1.9])
        c_c6 = np.array([6.0, 2.1])
        
        # Méthyle central et ses 3 hydrogènes
        c_me1 = np.array([5.7, 4.8])
        h1_me1 = np.array([5.0, 5.2])
        h2_me1 = np.array([6.3, 5.3])
        h3_me1 = np.array([5.8, 4.2])
        
        # Hydrogènes du cycle central (3 hydrogènes restants)
        h_cc3 = np.array([7.6, 4.3])
        h_cc5 = np.array([7.3, 1.2])
        h_cc6 = np.array([5.6, 1.4])

        # 4. Deuxième pont Azoïque
        n_azo2_1 = np.array([8.5, 2.5])
        n_azo2_2 = np.array([9.1, 3.0])

        # 5. Cycle benzénique droit (Terminal)
        t_c1 = np.array([10.0, 2.8])
        t_c2 = np.array([10.6, 3.6])
        t_c3 = np.array([11.6, 3.4])
        t_c4 = np.array([12.0, 2.5])
        t_c5 = np.array([11.4, 1.7])
        t_c6 = np.array([10.4, 1.9])
        
        # Méthyle droit et ses 3 hydrogènes
        c_me2 = np.array([10.2, 4.6])
        h1_me2 = np.array([9.5, 5.0])
        h2_me2 = np.array([10.8, 5.1])
        h3_me2 = np.array([10.4, 4.0])

        # Hydrogènes du cycle droit (4 hydrogènes restants)
        h_tc3 = np.array([12.0, 4.1])
        h_tc4 = np.array([12.7, 2.4])
        h_tc5 = np.array([11.7, 1.0])
        h_tc6 = np.array([10.0, 1.2])

        liste_hydrogenes = [
            h_oh, h_n1, h_n2, h_n3, h_n4, h_n9, h_n10,
            h1_me1, h2_me1, h3_me1, h_cc3, h_cc5, h_cc6,
            h1_me2, h2_me2, h3_me2, h_tc3, h_tc4, h_tc5, h_tc6
        ]

        # --- FONCTION DE TRACÉ DES LIAISONS CORRIGÉE ---
        def tracer_liaison(p1, p2, double=False):
            # Vérifie si p2 fait partie des hydrogènes pour lui donner une couleur grise plus claire
            est_h = any(np.array_equal(p2, h) for h in liste_hydrogenes)
            couleur_liaison = "#666666" if est_h else "#333333"
            
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.05
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=2.5, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=2.5, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color=couleur_liaison, linewidth=2, zorder=1)

        # --- DESSIN DES LIAISONS SQUELETTE ---
        # Naphtol & OH
        tracer_liaison(n1, n2, double=True); tracer_liaison(n2, n3); tracer_liaison(n3, n4, double=True)
        tracer_liaison(n4, n5); tracer_liaison(n5, n6); tracer_liaison(n6, n1)
        tracer_liaison(n5, n7, double=True); tracer_liaison(n7, n8); tracer_liaison(n8, n9, double=True)
        tracer_liaison(n9, n10); tracer_liaison(n10, n6); tracer_liaison(n8, o_oh); tracer_liaison(o_oh, h_oh)
        
        # Ponts azo
        tracer_liaison(n7, n_azo1_1); tracer_liaison(n_azo1_1, n_azo1_2, double=True); tracer_liaison(n_azo1_2, c_c1)
        tracer_liaison(c_c4, n_azo2_1); tracer_liaison(n_azo2_1, n_azo2_2, double=True); tracer_liaison(n_azo2_2, t_c1)
        
        # Cycles centraux et terminaux
        tracer_liaison(c_c1, c_c2); tracer_liaison(c_c2, c_c3, double=True); tracer_liaison(c_c3, c_c4)
        tracer_liaison(c_c4, c_c5, double=True); tracer_liaison(c_c5, c_c6); tracer_liaison(c_c6, c_c1, double=True); tracer_liaison(c_c2, c_me1)
        tracer_liaison(t_c1, t_c2, double=True); tracer_liaison(t_c2, t_c3); tracer_liaison(t_c3, t_c4, double=True)
        tracer_liaison(t_c4, t_c5); tracer_liaison(t_c5, t_c6, double=True); tracer_liaison(t_c6, t_c1); tracer_liaison(t_c2, c_me2)

        # --- DESSIN DES LIAISONS HYDROGÈNES ---
        for p, h in [(n1, h_n1), (n2, h_n2), (n3, h_n3), (n4, h_n4), (n9, h_n9), (n10, h_n10)]: tracer_liaison(p, h)
        for h in [h1_me1, h2_me1, h3_me1]: tracer_liaison(c_me1, h)
        for p, h in [(c_c3, h_cc3), (c_c5, h_cc5), (c_c6, h_cc6)]: tracer_liaison(p, h)
        for h in [h1_me2, h2_me2, h3_me2]: tracer_liaison(c_me2, h)
        for p, h in [(t_c3, h_tc3), (t_c4, h_tc4), (t_c5, h_tc5), (t_c6, h_tc6)]: tracer_liaison(p, h)

        # --- FONCTION DE TRACÉ DES ATOMES CORRIGÉE ---
        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, texte_couleur, r = "#2b3e50", "white", 0.18
            elif symbole == 'O': couleur, texte_couleur, r = "#e74c3c", "white", 0.18
            elif symbole == 'N': couleur, texte_couleur, r = "#4a90e2", "white", 0.18
            elif symbole == 'H': couleur, texte_couleur, r = "#ecf0f1", "black", 0.12
            
            ax_mol.add_patch(patches.Circle((p[0], p[1]), r, facecolor=couleur, edgecolor="#1a252f", linewidth=1.2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=7 if symbole=='H' else 8, ha="center", va="center", zorder=3)
            
        # --- DESSIN DES ATOMES ---
        # Carbones, Azotes, Oxygène
        for pt in [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, c_c1, c_c2, c_c3, c_c4, c_c5, c_c6, c_me1, t_c1, t_c2, t_c3, t_c4, t_c5, t_c6, c_me2]: tracer_atome(pt, 'C')
        for pt in [n_azo1_1, n_azo1_2, n_azo2_1, n_azo2_2]: tracer_atome(pt, 'N')
        tracer_atome(o_oh, 'O')
        
        # Les 20 Hydrogènes (H)
        tracer_atome(h_oh, 'H')
        for h in [h_n1, h_n2, h_n3, h_n4, h_n9, h_n10, h1_me1, h2_me1, h3_me1, h_cc3, h_cc5, h_cc6, h1_me2, h2_me2, h3_me2, h_tc3, h_tc4, h_tc5, h_tc6]:
            tracer_atome(h, 'H')

        ax_mol.set_xlim(0.0, 13.2)
        ax_mol.set_ylim(-0.2, 5.8)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    if "vin_verrouille_tab1" not in st.session_state:
        st.session_state.vin_verrouille_tab1 = False

    verrou_at1 = st.session_state.vin_verrouille_tab1

    # Appel direct et propre de la fonction sans affectation binaire
    try:
        # Adaptation de la fonction pour le Red 24
        afficher_questions_red24_dynamiques(verrouille=verrou_at1)
    except NameError:
        pass

    st.write("---")
    st.subheader("Généralités sur le Solvent Red 24")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_red24_final_net", 
        disabled=verrou_at1
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_vin1_official_net", use_container_width=True, disabled=verrou_at1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz1_red24" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_red24:
                    reponse_eleve = st.session_state.get(f"red24_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction des Textes à trous mis à jour pour le Solvent Red 24 (10 points)
            score_t1 = sum([
                st.session_state.get("red24_t1_tab1_final") == "Sudan IV",
                st.session_state.get("red24_t2_tab1_final") == "C24H20N4O",
                st.session_state.get("red24_t3_tab1_final") == "380,44 g/mol",
                st.session_state.get("red24_t4_tab1_final") == "24 atomes",
                st.session_state.get("red24_t5_tab1_final") == "20 atomes",
                st.session_state.get("red24_t6_tab1_final") == "4 atomes",
                st.session_state.get("red24_t7_tab1_final") == "1 atome",
                st.session_state.get("red24_t8_tab1_final") == "14 g/mol",
                st.session_state.get("red24_t9_tab1_final") == "10 mg / L",
                st.session_state.get("red24_t10_tab1_final") == "Accutrace"
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
        timestamp_vin1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER RED 24 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_red24 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Solvent Red 24 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #991b1b; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 1 : Étude moléculaire du Solvent Red 24</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Nomenclature Moléculaire : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse des propriétés : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_red24" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_red24, 1):
                saisie = st.session_state.get(f"red24_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_red24 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_red24 += """
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
            "1. Le nom scientifique commun ou synonyme de laboratoire du Solvent Red 24 est",
            "2. Sa formule de structure brute globale s'écrit",
            "3. La masse molaire calculée à partir de ses éléments constitutifs vaut",
            "4. Au sein de son squelette, on compte un nombre total d'atomes de Carbone de",
            "5. Le nombre d'atomes d'Hydrogène présents dans la structure vaut",
            "6. Le nombre d'atomes d'Azote constituant les ponts azoïques vaut",
            "7. Le nombre d'atomes d'Oxygène présents sur sa fonction alcool vaut",
            "8. La constante de masse molaire de l'élément atomique Azote (N) vaut",
            "9. En France, le dosage officiel de ce colorant pour la dénaturation douanière vaut",
            "10. Pour obtenir l'appellation GNR, il faut obligatoirement lui adjoindre le traceur"
        ]
        
        attendus_trous1 = ["Sudan IV", "C24H20N4O", "380,44 g/mol", "24 atomes", "20 atomes", "4 atomes", "1 atome", "14 g/mol", "10 mg / L", "Accutrace"]
        cles_trous1 = [f"red24_t{i}_tab1_final" for i in range(1, 11)]

        for num, (phrase, attendu, cle) in enumerate(zip(phrases_trous1, attendus_trous1, cles_trous1), 1):
            saisie = st.session_state.get(cle, "Non complété")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_red24 += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_red24 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu ou bouton de téléchargement du fichier HTML généré
        st.download_button(
            label="Télécharger le Rapport Officiel HTML (Atelier 1)",
            data=html_export_red24,
            file_name=f"Rapport_Atelier1_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Le titre massique du colorant du GNR")
    st.caption("Concentration massique du colorant du GNR")


            

with tab3:
    st.header("Pourquoi le colorant reste-t-il dans le réservoir?")
    st.caption("Persistance du colorant")




with tab4:
    st.header("Fraude ou non")
    st.subheader("Simulateur de dilution et d'extraction en laboratoire")


    st.markdown("""
    Cette application simule un controle routier des douanes. L'historique du vehicule inspecte est **genere de maniere aleatoire** 
    pour chaque etudiant. Vous devez mener l'enquete visuelle et chimique pour rendre votre verdict.
    """)

    # Initialisation des variables aleatoires dans la session Streamlit (pour eviter qu'elles ne changent a chaque clic)
    if 'fraudeur' not in st.session_state:
        st.session_state.fraudeur = random.choice([True, False])
        if st.session_state.fraudeur:
            st.session_state.nb_pleins = random.randint(0, 5)
        else:
            st.session_state.nb_pleins = 0

    # AJOUTEZ CETTE LIGNE ICI POUR CORRIGER L'ERREUR
    verrou_gnr = st.session_state.get("gnr_verrouille_final", False)

    # --- SECTION 1 : CONFIGURATION DE LA FRAUDE ---
    st.header("1. Echantillon suspect de la cuve ou du reservoir")

    concentration_initiale = 10.0  # mg/L

    # Calcul de la concentration reelle cachee selon le tirage aleatoire
    if st.session_state.fraudeur:
        concentration_actuelle = concentration_initiale / (2 ** st.session_state.nb_pleins)
    else:
        concentration_actuelle = 0.0  # Vehicule parfaitement en regle

    # Determination de la couleur visuelle en fonction de la concentration
    if concentration_actuelle >= 10:
        couleur_gazole = "#E60000"  # Rouge vif
        etat_visuel = "Rouge vif - Coloration marquee"
    elif concentration_actuelle >= 5:
        couleur_gazole = "#FF4D4D"  # Rouge/Rose
        etat_visuel = "Rose bien visible"
    elif concentration_actuelle >= 2:
        couleur_gazole = "#FFA6A6"  # Rose clair
        etat_visuel = "Teinte rosee suspecte"
    elif concentration_actuelle >= 1:
        couleur_gazole = "#FFD1A9"  # Orange/Jaune legerement teinte
        etat_visuel = "Teinte douteuse legerement orangee"
    else:
        couleur_gazole = "#F4D03F"  # Jaune normal du gazole routier
        etat_visuel = "Jaune normal"

    # Affichage de l'aspect visuel (la concentration reste cachee pour l'etudiant au debut)
    st.metric(label="Aspect visuel du carburant preleve", value=etat_visuel)

    # Rendu visuel de l'eprouvette de gazole
    st.markdown(
        f"""
        <div style="background-color: {couleur_gazole}; width: 100%; height: 120px; 
        border: 3px solid #566573; border-radius: 10px; display: flex; 
        align-items: center; justify-content: center; color: black; font-weight: bold; font-size: 18px;">
            Gazole du reservoir ({concentration_actuelle:.2f} mg/L)
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- SECTION 2 : LE TEST D'EXTRACTION CHIMIQUE ---
    st.header("2. Analyse chimique (Test d'extraction)")
    st.write("Si le carburant semble visuellement jaune ou douteux, lancez l'extraction liquide-liquide a l'ethanol pour separer et concentrer le colorant.")

    activer_test = st.button("Lancer l'extraction")

    if activer_test:
        st.markdown("### Resultat apres decantation en ampoule :")
        
        # Facteur de concentration : on concentre les traces dans un petit volume d'alcool (x10)
        facteur_concentration = 10 
        concentration_extrait = concentration_actuelle * facteur_concentration
        
        # Couleur de la phase alcoolique superieure apres extraction
        if concentration_extrait >= 20:
            couleur_alcool = "#C0392B"  # Rouge fonce
            verdict = "FRAUDE CONFIRMEE : Forte presence de Solvent Red 24 extraite !"
            statut_type = "error"
        elif concentration_extrait >= 5:
            couleur_alcool = "#E74C3C"  # Rouge/Rose net
            verdict = "FRAUDE CONFIRMEE : Traces nettes de GNR detectees dans l'extrait."
            statut_type = "error"
        elif concentration_extrait >= 1:
            couleur_alcool = "#F1948A"  # Rose clair
            verdict = "FRAUDE CONFIRMEE : Résidus de colorant fiscal mis en evidence. Utilisation passee averee."
            statut_type = "warning"
        else:
            couleur_alcool = "#F8F9F9"  # Incolore/Transparent
            verdict = "RAS : Aucune trace de colorant extraite. Le carburant est conforme."
            statut_type = "success"
            
        # Affichage graphique des deux phases
        st.markdown(
            f"""
            <div style="border: 3px solid #34495E; border-radius: 10px; overflow: hidden;">
                <!-- Phase superieure : Alcool -->
                <div style="background-color: {couleur_alcool}; height: 80px; display: flex; 
                align-items: center; justify-content: center; color: black; font-weight: bold;">
                    PHASE ALCOOLIQUE (Extrait concentre)
                </div>
                <!-- Phase inferieure : Gazole -->
                <div style="background-color: #F4D03F; height: 120px; display: flex; 
                align-items: center; justify-content: center; color: black; font-weight: bold; border-top: 2px dashed #34495E;">
                    PHASE HYDROCARBURE (Gazole lave)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
            
        # Affichage du verdict
        if statut_type == "error":
            st.error(verdict)
        elif statut_type == "warning":
            st.warning(verdict)
        else:
            st.success(verdict)

        # --- SECTION 3 : REVELATION DES VALEURS POUR LE CORRIGE ---
        st.markdown("---")
        st.subheader("Rapport technique (Pour verification des resultats)")
        st.write(f"Statut reel du vehicule : {'Fraudeur' if st.session_state.fraudeur else 'En regle'}")
        if st.session_state.fraudeur:
            st.write(f"Nombre de dilutions (pleins successifs) : {st.session_state.nb_pleins}")
        st.write(f"Concentration exacte en colorant dans le reservoir : {concentration_actuelle:.4f} mg/L")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    
    
    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_gnr = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier GNR.", 
        key="check_certif_gnr_final_net", 
        disabled=verrou_gnr
    )

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER GNR", key="btn_export_gnr_official_net", use_container_width=True, disabled=verrou_gnr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_gnr:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Récupération des données masquées de la session
            is_fraudeur = st.session_state.get("fraudeur", False)
            nb_pleins_simules = st.session_state.get("nb_pleins", 0)
            
            # Calculs théoriques attendus
            c_initiale = 10.0  # mg/L legal
            c_reservoir_attendue = c_initiale / (2 ** nb_pleins_simules) if is_fraudeur else 0.0
            c_extrait_attendue = c_reservoir_attendue * 10.0
            
            # Masse molaire du Solvent Red 24 = 380.44 g/mol
            # Concentration molaire = (C_massique en mg/L / 1000) / 380.44
            c_molaire_attendue = (c_reservoir_attendue / 1000.0) / 380.44

            # Verdict attendu textuel
            verdict_attendu = (
                "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)" 
                if is_fraudeur else 
                "Le vehicule est en regle : Aucun residu de colorant fiscal detecte"
            )

            # 1. Correction de la Partie Analyse & Concentration (sur 10 points)
            # Saisie nettoyée pour tolérer les espaces et virgules des étudiants
            def clean_val(k): return st.session_state.get(k, "0.0").replace(",", ".").strip()

            score_p1 = sum([
                abs(float(clean_val("at3_c_extrait_gnr")) - c_extrait_attendue) < 0.1,
                abs(float(clean_val("at3_facteur_ext_gnr")) - 10.0) < 0.01,
                abs(float(clean_val("at3_c_reservoir_gnr")) - c_reservoir_attendue) < 0.1,
                abs(float(clean_val("at3_masse_molaire_red24")) - 380.44) < 0.01,
                abs(float(clean_val("at3_c_molaire_reservoir_gnr")) - c_molaire_attendue) < 1e-6
            ]) * (10.0 / 5.0)

            # 2. Correction de la Partie Diagnostic (sur 10 points)
            score_p2 = sum([
                abs(float(clean_val("at3_dosage_legal_gnr")) - 10.0) < 0.01,
                st.session_state.get("at3_conclusion_verdict_gnr") == verdict_attendu
            ]) * (10.0 / 2.0)

            st.session_state.score_gnr_p1 = round(float(score_p1), 1)
            st.session_state.score_gnr_p2 = round(float(score_p2), 1)
            st.session_state.score_final_gnr = round(float(score_p1 + score_p2), 1)
            st.session_state.gnr_verrouille_final = True
            st.rerun()

    # --- COMPILATION DU RAPPORT HTML POUR LE GNR ---
    if st.session_state.get("gnr_verrouille_final", False):
        scr1 = st.session_state.get("score_gnr_p1", 0.0)
        scr2 = st.session_state.get("score_gnr_p2", 0.0)
        tot_s = st.session_state.get("score_final_gnr", 0.0)
        
        is_fraudeur = st.session_state.get("fraudeur", False)
        nb_pleins_simules = st.session_state.get("nb_pleins", 0)
        c_initiale = 10.0
        c_reservoir_attendue = c_initiale / (2 ** nb_pleins_simules) if is_fraudeur else 0.0
        c_extrait_attendue = c_reservoir_attendue * 10.0
        c_molaire_attendue = (c_reservoir_attendue / 1000.0) / 380.44
        verdict_attendu = "Fraude averee" if is_fraudeur else "Vehicule en regle"

        from datetime import datetime, timedelta
        timestamp_gnr = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        html_export_gnr = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Controle GNR - {n_eleve}</title>
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
                <p>Atelier GNR : Controle de la fraude fiscale sur les carburants</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_gnr}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue sur les calculs d'extraction : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue sur le diagnostic de conformite : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Finale de l'Atelier GNR : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">Compose recherche : Solvent Red 24 (C24H20N4O)</div>
            
            <div class="sub-title">PARTIE 1 : DETAILS DES CALCULS QUANTITATIFS D'EXTRACTION</div>
            <table>
                <thead><tr><th>N°</th><th>Parametre a determiner</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """

        attendus_p1 = [
            f"{c_extrait_attendue:.2f} mg/L",
            "10.0",
            f"{c_reservoir_attendue:.2f} mg/L",
            "380.44 g/mol",
            f"{c_molaire_attendue:.6e} mol/L"
        ]
        
        labels_p1 = [
            "1. Concentration estimee dans l'extrait concentre",
            "2. Rappel du facteur de concentration de l'extraction",
            "3. Concentration calculee dans le reservoir suspect",
            "4. Rappel de la masse molaire du Solvent Red 24",
            "5. Concentration molaire en colorant dans le reservoir"
        ]
        
        keys_p1 = ["at3_c_extrait_gnr", "at3_facteur_ext_gnr", "at3_c_reservoir_gnr", "at3_masse_molaire_red24", "at3_c_molaire_reservoir_gnr"]
        
        for i in range(5):
            saisie = st.session_state.get(keys_p1[i], "0.0")
            attendu = attendus_p1[i]
            # Logique de validation simplifiee pour l'affichage textuel
            v_lbl = "CORRECT" if abs(float(saisie.replace(",", ".").strip()) - float(attendu.split()[0])) < 0.1 else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_gnr += f"<tr><td>{i+1}</td><td>{labels_p1[i]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_gnr += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DIAGNOSTIC DE CONFORMITÉ</div>
            <table>
                <thead><tr><th>N°</th><th>Critere pedagogique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr></thead>
                <tbody>
        """
        
        # Ligne pour le dosage légal
        saisie_legal = st.session_state.get("at3_dosage_legal_gnr", "0.0")
        v_lbl_legal = "CORRECT" if abs(float(saisie_legal.replace(",", ".").strip()) - 10.0) < 0.01 else "INCORRECT"
        v_class_legal = "status-correct" if v_lbl_legal == "CORRECT" else "status-incorrect"
        html_export_gnr += f"<tr><td>1</td><td>Dosage legal exige pour le GNR pur</td><td>{saisie_legal} mg/L</td><td>10.0 mg/L</td><td class='{v_class_legal}'>{v_lbl_legal}</td></tr>"
        
        # Ligne pour le verdict final
        saisie_verdict = st.session_state.get("at3_conclusion_verdict_gnr", "Choisir...")
        v_lbl_verdict = "CORRECT" if ("Fraude" in saisie_verdict and is_fraudeur) or ("regle" in saisie_verdict and not is_fraudeur) else "INCORRECT"
        v_class_verdict = "status-correct" if v_lbl_verdict == "CORRECT" else "status-incorrect"
        html_export_gnr += f"<tr><td>2</td><td>Verdict rendu sur la conformite du carburant</td><td>{saisie_verdict}</td><td>{verdict_attendu}</td><td class='{v_class_verdict}'>{v_lbl_verdict}</td></tr>"




