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
            st.rerun()

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


def afficher_questions_gnr_tab4(verrouille=False):
    import streamlit as st

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LA FIOLE ET LE RÉSERVOIR ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation de l'analyse quantitative (Fiole de 500 mL)</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("1. Quelle est la concentration en colorant observee dans l'extrait concentre (mg/L) :")
    with c2: st.text_input("", value="0.0", key="at3_c_extrait_gnr", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("2. Quel est le facteur multiplicateur applique lors de l'extraction liquide-liquide :")
    with c4: st.text_input("", value="0.0", key="at3_facteur_ext_gnr", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("3. En deduire la concentration en colorant calculee dans le reservoir du vehicule (mg/L) :")
    with c6: st.text_input("", value="0.0", key="at3_c_reservoir_gnr", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("4. Rappeler la masse molaire precise du Solvent Red 24 (g/mol) :")
    with c8: st.text_input("", value="0.0", key="at3_masse_molaire_red24", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("5. Convertir la concentration du reservoir en concentration molaire (mol/L) :")
    with c10: st.text_input("", value="0.0", key="at3_c_molaire_reservoir_gnr", disabled=verrouille, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : SYNTHÈSE DE COURS ET VERDICT DOUANIER ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Synthese de l'enquete fiscale et verdict douanier</p>", unsafe_allow_html=True)

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("6. Le Solvent Red 24 est une molecule chimiquement acide, basique ou neutre :")
    with c12: st.text_input("", value="", key="gnr_t1_tab4", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("7. Quel type de solvant a permis de decrocher et separer le colorant (polaire ou apolaire) :")
    with c14: st.text_input("", value="", key="gnr_t2_tab4", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("8. Rappeler le dosage legal minimum de ce colorant requis dans le GNR pur (mg/L) :")
    with c16: st.text_input("", value="0.0", key="at3_dosage_legal_gnr", disabled=verrouille, label_visibility="collapsed")

    # Choix dynamique basé sur l'état aléatoire stocké en session
    is_fraudeur = st.session_state.get("fraudeur", False)
    if is_fraudeur:
        choix_conclusion = [
            "Choisir...", 
            "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)", 
            "Le vehicule est en regle : Aucun residu de colorant fiscal detecte"
        ]
    else:
        choix_conclusion = [
            "Choisir...", 
            "Le vehicule est en regle : Aucun residu de colorant fiscal detecte",
            "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)"
        ]

    c17, c18 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c17: st.write("9. Conclusion finale sur la conformite du carburant inspecte :")
    with c18: st.selectbox(
        "", 
        choix_conclusion, 
        key="at3_conclusion_verdict_gnr", 
        disabled=verrouille, 
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)


def afficher_questions_persistance_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable mis à jour pour le comportement et le contrôle du GNR (tab3)
    ordre_fixe_tab3 = [
        {"id": "q3_1", "q": "Lors du fonctionnement du moteur, le colorant subit une :", "options": ["combustion conjointe", "évaporation isolée", "filtration totale"], "rep": "combustion conjointe"},
        {"id": "q3_2", "q": "La température au sein de la chambre de combustion dépasse :", "options": ["600 °C", "200 °C", "100 °C"], "rep": "600 °C"},
        {"id": "q3_3", "q": "Le solvant Red 24 possède une température d'ébullition qualifiée de :", "options": ["très élevée", "très basse", "ambiante"], "rep": "très élevée"},
        {"id": "q3_4", "q": "Quel organe retient massivement les pigments sous forme liquide ?", "options": ["Le filtre à gazole", "Le pot d'échappement", "Le radiateur"], "rep": "Le filtre à gazole"},
        {"id": "q3_5", "q": "La couleur persistante sur les parois du réservoir est due à une :", "options": ["imprégnation des polymères", "évaporation instantanée", "réaction à l'eau"], "rep": "imprégnation des polymères"},
        {"id": "q3_6", "q": "Quelle méthode utilise une sonde fine par l'orifice du réservoir ?", "options": ["L'aspiration par dépression", "La purge sous le capot", "Le frottis externe"], "rep": "L'aspiration par dépression"},
        {"id": "q3_7", "q": "Où se fait la purge alternative si le réservoir possède un anti-siphonnage ?", "options": ["Au filtre à gazole", "À la pompe de direction", "Au bloc moteur"], "rep": "Au filtre à gazole"},
        {"id": "q3_8", "q": "Les bandelettes réactives insérées par les douaniers réagissent au :", "options": ["traceur fiscal", "plomb de l'essence", "niveau d'eau"], "rep": "traceur fiscal"},
        {"id": "q3_9", "q": "Quelle méthode de laboratoire quantifie le colorant en cas de litige ?", "options": ["La chromatographie HPLC", "La pesée sur balance", "La centrifugation simple"], "rep": "La chromatographie HPLC"},
        {"id": "q3_10", "q": "Combien de flacons officiels scellés sont préparés lors du contrôle ?", "options": ["2 flacons", "1 seul flacon", "4 flacons"], "rep": "2 flacons"}
    ]

    st.session_state.ordre_quiz_tab3 = ordre_fixe_tab3

    col_double_quiz_tab3, col_double_trous_tab3 = st.columns(2)

    with col_double_quiz_tab3:
        st.markdown("##### Quiz sur le comportement et le contrôle (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_tab3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab3_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_tab3:
        st.markdown("##### Synthèse sur la persistance et les douanes (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Dans le cylindre, le colorant brûle avec le carburant lors de la")
        with c2: st.selectbox("", ["Choisir...", "combustion", "distillation", "filtration"], key="tab3_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le Solvent Red 24 ne peut pas se séparer du gazole par simple")
        with c4: st.selectbox("", ["Choisir...", "évaporation", "imprégnation", "décantation"], key="tab3_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Le média en papier qui vire instantanément au rouge vif est le")
        with c6: st.selectbox("", ["Choisir...", "filtre à gazole", "filtre à air", "filtre à huile"], key="tab3_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Les parois en plastique du réservoir subissent une forte")
        with c8: st.selectbox("", ["Choisir...", "imprégnation", "combustion", "évaporation"], key="tab3_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le prélèvement standard dans le réservoir s'effectue par")
        with c10: st.selectbox("", ["Choisir...", "aspiration", "frottis extérieur", "démontage"], key="tab3_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. En cas de clapet anti-siphonnage, les agents purgent le")
        with c12: st.selectbox("", ["Choisir...", "circuit du filtre", "pot d'échappement", "carburateur"], key="tab3_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Pour une détection instantanée dans le conduit, on utilise une")
        with c14: st.selectbox("", ["Choisir...", "bandelette", "pompe manuelle", "balance"], key="tab3_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le test de terrain cherche la présence du colorant et du")
        with c16: st.selectbox("", ["Choisir...", "traceur fiscal", "plomb lourd", "pigment bleu"], key="tab3_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'analyse officielle de laboratoire pour mesurer la masse utilise la")
        with c18: st.selectbox("", ["Choisir...", "chromatographie", "distillation", "décantation"], key="tab3_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour garantir la validité juridique, les échantillons sont mis sous")
        with c20: st.selectbox("", ["Choisir...", "scellés", "abri", "pression"], key="tab3_t10_final", disabled=verrouille, label_visibility="collapsed")
        
    return


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
    
    st.write(
        "Le titre massique (ou concentration massique $C_m$) représente la masse de colorant "
        "présente par unité de volume de gazole. Pour le GNR, la réglementation impose un "
        "marquage strict pour le contrôle fiscal."
    )
    
    # Rappel des normes officielles
    st.subheader("Normes réglementaires")
    st.markdown("- **Solvent Red 24 (Colorant visuel) :** Environ 5 à 10 mg/L (soit 5 à 10 g/m³)")
    st.markdown("- **Solvent Yellow 124 (Traceur fiscal) :** Strictement 6 mg/L (soit 6 g/m³)")
    
    # Outil de simulation et de calcul
    st.subheader("Simulateur de dosage")
    
    # Entrées utilisateur
    volume_gnr = st.number_input(
        "Volume de GNR à analyser ou préparer (en Litres) :", 
        min_value=1.0, 
        value=1000.0, 
        step=10.0
    )
    
    titre_massique = st.slider(
        "Titre massique ciblé pour le Solvent Red 24 (en mg/L) :", 
        min_value=0.0, 
        max_value=20.0, 
        value=7.0, 
        step=0.5
    )
    
    # Calcul de la masse requise (m = Cm * V)
    masse_colorant_mg = titre_massique * volume_gnr
    masse_colorant_g = masse_colorant_mg / 1000
    
    # Affichage du résultat
    st.metric(
        label="Masse totale de colorant nécessaire", 
        value=f"{masse_colorant_g:.3f} g", 
        delta=f"{masse_colorant_mg:.0f} mg"
    )
    
    # Note de conformité dynamique
    if 5.0 <= titre_massique <= 10.0:
        st.success("Ce titre massique est conforme aux standards de coloration du GNR.")
    elif titre_massique < 5.0:
        st.warning("Titre massique trop faible : le gazole risque de ne pas être assez coloré (risque de non-conformité fiscale).")
    else:
        st.info("Titre massique élevé : la coloration sera très intense.")


            

with tab3:
    st.header("Destinée du colorant et méthodes de contrôle")
    st.caption("Analyse du comportement thermique, de la contamination mécanique et des protocoles douaniers")
    
    # Division en deux colonnes principales pour le traitement chimique vs terrain
    col_g, col_d = st.columns([1, 1])
    
    with col_g:
        st.subheader("Où se retrouve le colorant ?")
        st.write(
            "Lors du fonctionnement d'un moteur, le colorant subit une combustion "
            "conjointe avec le gazole au sein du cylindre. Il ne se sépare pas du "
            "carburant par simple évaporation."
        )
        
        st.markdown("**Combustion intégrale dans le moteur**")
        st.write(
            "Le Solvent Red 24 est une molécule organique lourde possédant une "
            "température d'ébullition très élevée. Elle reste intimement liée au "
            "gazole liquide dans le réservoir et ne s'évapore pas de manière isolée. "
            "Lorsque le mélange est injecté dans la chambre de combustion à haute "
            "température (plus de 600 °C), le colorant brûle intégralement avec les "
            "hydrocarbures pour se transformer en gaz d'échappement et en suies."
        )
        
        st.markdown("**Phénomène d'imprégnation**")
        st.write(
            "Bien que le colorant soit détruit par le feu dans les cylindres, le "
            "carburant circule sous forme liquide dans tout le système d'alimentation "
            "avant d'être brûlé. Les molécules de colorant et de traceur possèdent "
            "une forte affinité avec les polymères et les métaux porosés, ce qui "
            "entraîne une coloration rose ou rouge persistante sur les parois du "
            "réservoir, les durites et surtout le média filtrant du filtre à gazole."
        )
        
        st.info(
            "Conséquence sur la détection des fraudes : Il est techniquement impossible "
            "d'éliminer le colorant par chauffage ou évaporation domestique. Les contrôles "
            "douaniers ciblent le carburant liquide non encore consommé. La persistance des "
            "molécules chimiques dans le filtre à gazole permet de caractériser l'utilisation "
            "du GNR longtemps après la vidange ou la dilution du réservoir."
        )

    with col_d:
        st.subheader("Protocole de prélèvement douanier")
        st.write(
            "Lors d'un contrôle routier ou sur site, les agents des douanes suivent un "
            "protocole strict et standardisé pour récupérer un échantillon de carburant "
            "sans endommager le véhicule."
        )
        
        st.markdown("**Aspiration par le puits de jauge**")
        st.write(
            "La méthode la plus courante consiste à introduire une sonde flexible fine "
            "(un tube en plastique à usage unique) directement par l'orifice de remplissage "
            "du réservoir. À l'aide d'une pompe manuelle à dépression, les douaniers aspirent "
            "quelques dizaines de millilitres de carburant vers un flacon stérile."
        )
        
        st.markdown("**Prélèvement sur le circuit d'alimentation**")
        st.write(
            "Si l'accès au réservoir est obstrué par un clapet anti-siphonnage, les agents "
            "peuvent effectuer le prélèvement sous le capot. Ils déconnectent brièvement une "
            "durite ou ouvrent la vis de purge du filtre à gazole pour recueillir le liquide. "
            "Cette méthode est redoutable car le filtre concentre les pigments."
        )
        
        st.markdown("**Détection par frottis et bandelettes**")
        st.write(
            "Dans certains cas, les douaniers insèrent des bandelettes chimiques spécifiques "
            "dans le conduit de remplissage pour les frotter contre les parois internes. Si du "
            "GNR a transité par ce conduit, la bandelette change immédiatement de couleur, "
            "révélant la fraude même si le réservoir a été entièrement vidé entre-temps."
        )

    # Séparation visuelle pour la section basse sur la contamination physique
    st.divider()
    
    st.subheader("Contamination visuelle des organes du véhicule")
    st.write(
        "L'utilisation de gazole non routier laisse des traces physiques indélébiles "
        "sur plusieurs composants clés du système d'alimentation et du moteur. Faute d'images "
        "publiques disponibles (ces constats techniques relevant du secret judiciaire), "
        "voici la cartographie des pièces mécaniques qui restent durablement marquées :"
    )

    # Utilisation de colonnes secondaires pour présenter proprement les organes touchés
    col_organes_1, col_organes_2 = st.columns(2)
    
    with col_organes_1:
        st.warning(
            "Le filtre à gazole : C'est l'organe le plus massivement contaminé. Le média filtrant "
            "en papier ou en feutre retient les impuretés et se colore instantanément en rouge vif. "
            "C'est le premier composant vérifié lors d'une inspection mécanique approfondie."
        )
        st.error(
            "Le réservoir et les durites : Les parois en plastique ou en composite absorbent les "
            "pigments en surface, créant un voile rosé persistant même après plusieurs pleins successifs "
            "de gazole blanc routier."
        )
        
    with col_organes_2:
        st.error(
            "La pompe à injection et les injecteurs : Le passage continu du carburant sous haute "
            "pression thermique provoque une imprégnation microscopique des composants métalliques "
            "internes et des joints d'étanchéité."
        )
        st.warning(
            "La chambre de combustion : Bien que le colorant brûle, les dépôts de suie et de "
            "calamine fine qui se forment naturellement sur la tête des pistons et autour des soupapes "
            "conservent une teinte sombre teintée par les résidus du marqueur."
        )

    # Bloc de procédure légale de fin de page
    st.info(
        "Procédure légale et mise sous scellés : Pour que le contrôle soit juridiquement valable, "
        "l'échantillon prélevé est réparti dans des flacons officiels scellés en présence du conducteur. "
        "Un flacon sert au test rapide de terrain, tandis qu'un second flacon témoin est conservé pour les "
        "analyses de laboratoire (chromatographie HPLC) en cas de litige ou de contestation des résultats."
    )


    st.write("---")
    st.subheader("Généralités sur la persistance et le contrôle du GNR")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # Déclaration du verrou pour éviter le NameError
    verrou_gnr = st.session_state.get("vin_verrouille_tab3", False)

    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 3.", 
        key="check_certif_tab3_final_net", 
        disabled=verrou_gnr
    )
    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_vin3_official_net", use_container_width=True, disabled=verrou_gnr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q3 = 0.0
            if "ordre_quiz_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3:
                    reponse_eleve = st.session_state.get(f"tab3_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q3 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t3 = sum([
                st.session_state.get("tab3_t1_final") == "combustion",
                st.session_state.get("tab3_t2_final") == "évaporation",
                st.session_state.get("tab3_t3_final") == "filtre à gazole",
                st.session_state.get("tab3_t4_final") == "imprégnation",
                st.session_state.get("tab3_t5_final") == "aspiration",
                st.session_state.get("tab3_t6_final") == "circuit du filtre",
                st.session_state.get("tab3_t7_final") == "bandelette",
                st.session_state.get("tab3_t8_final") == "traceur fiscal",
                st.session_state.get("tab3_t9_final") == "chromatographie",
                st.session_state.get("tab3_t10_final") == "scellés"
            ])

            st.session_state.score_vin3_p1 = round(float(score_q3), 1)
            st.session_state.score_vin3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_vin3 = round(float(score_q3 + score_t3), 1)
            st.session_state.vin_verrouille_tab3 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 3 ---
    if st.session_state.get("vin_verrouille_tab3", False):
        scr1 = st.session_state.get("score_vin3_p1", 0.0)
        scr2 = st.session_state.get("score_vin3_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin3", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER PERSISTANCE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_tab3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Persistance GNR - {n_eleve}</title>
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
                <p>Atelier 3 : Comportement thermique, persistance et protocoles douaniers (GNR)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Technique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse des propriétés : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3, 1):
                saisie = st.session_state.get(f"tab3_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tab3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab3 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        phrases_trous3 = [
            "1. Dans le cylindre, le colorant brûle avec le carburant lors de la",
            "2. Le Solvent Red 24 ne peut pas se séparer du gazole par simple",
            "3. Le média en papier qui vire instantanément au rouge vif est le",
            "4. Les parois en plastique du réservoir subissent une forte",
            "5. Le prélèvement standard dans le réservoir s'effectue par",
            "6. En cas de clapet anti-siphonnage, les agents purgent le",
            "7. Pour une détection instantanée dans le conduit, on utilise une",
            "8. Le test de terrain cherche la présence du colorant et du",
            "9. L'analyse officielle de laboratoire pour mesurer la masse utilise la",
            "10. Pour garantir la validité juridique, les échantillons sont mis sous"
        ]
        
        attendus_trous3 = ["combustion", "évaporation", "filtre à gazole", "imprégnation", "aspiration", "circuit du filtre", "bandelette", "traceur fiscal", "chromatographie", "scellés"]
        cles_trous3 = [f"tab3_t{i}_final" for i in range(1, 11)]

        for num, (phrase, attendu, cle) in enumerate(zip(phrases_trous3, attendus_trous3, cles_trous3), 1):
            saisie = st.session_state.get(cle, "Non complété")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_tab3 += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu ou bouton de téléchargement du fichier HTML généré
        st.download_button(
            label="Télécharger le Rapport Officiel HTML (Atelier 3)",
            data=html_export_tab3,
            file_name=f"Rapport_Atelier3_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )

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
            verdict = "FRAUDE CONFIRMEE : Traces nettes de GNR détectées dans l'extrait."
            statut_type = "error"
        elif concentration_extrait >= 1:
            couleur_alcool = "#F1948A"  # Rose clair
            verdict = "FRAUDE CONFIRMEE : Résidus de colorant fiscal mis en evidence. Utilisation passee avérée."
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
        # --- SECTION 3 : REVELATION DES VALEURS POUR LE CORRIGE ---
        st.markdown("---")
        st.subheader("Rapport technique (Pour verification des resultats)")
        st.write(f"Statut reel du vehicule : {'Fraudeur' if st.session_state.fraudeur else 'En regle'}")
        if st.session_state.fraudeur:
            st.write(f"Nombre de dilutions (pleins successifs) : {st.session_state.nb_pleins}")
        st.write(f"Concentration exacte en colorant dans le reservoir : {concentration_actuelle:.4f} mg/L")

    # --- INSEREZ CE BLOC EXACTEMENT ICI POUR FAIRE APPARAITRE LES QUESTIONS ---
    st.write("---")
    st.subheader("Generalites sur le Solvent Red 24 et le GNR")

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # --- BLOC BLEU : EXPLOITATION QUANTITATIVE ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #0369a1; margin-bottom: 10px;'>Exploitation de l'analyse quantitative (Fiole de 500 mL)</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("1. Quelle est la concentration en colorant observee dans l'extrait concentre (mg/L) :")
    with c2: st.text_input("", value="0.0", key="at3_c_extrait_gnr", disabled=verrou_gnr, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("2. Quel est le facteur multiplicateur applique lors de l'extraction liquide-liquide :")
    with c4: st.text_input("", value="0.0", key="at3_facteur_ext_gnr", disabled=verrou_gnr, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("3. En deduire la concentration en colorant calculee dans le reservoir du vehicule (mg/L) :")
    with c6: st.text_input("", value="0.0", key="at3_c_reservoir_gnr", disabled=verrou_gnr, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("4. Rappeler la masse molaire precise du Solvent Red 24 (g/mol) :")
    with c8: st.text_input("", value="0.0", key="at3_masse_molaire_red24", disabled=verrou_gnr, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("5. Convertir la concentration du reservoir en concentration molaire (mol/L) :")
    with c10: st.text_input("", value="0.0", key="at3_c_molaire_reservoir_gnr", disabled=verrou_gnr, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : SYNTHÈSE ET VERDICT ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='font-weight: bold; color: #854d0e; margin-bottom: 10px;'>Synthese de l'enquete fiscale et verdict douanier</p>", unsafe_allow_html=True)

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("6. Le Solvent Red 24 est une molecule chimiquement acide, basique ou neutre :")
    with c12: st.text_input("", value="", key="gnr_t1_tab4", disabled=verrou_gnr, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("7. Quel type de solvant a permis de decrocher et separer le colorant (polaire ou apolaire) :")
    with c14: st.text_input("", value="", key="gnr_t2_tab4", disabled=verrou_gnr, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("8. Rappeler le dosage legal minimum de ce colorant requis dans le GNR pur (mg/L) :")
    with c16: st.text_input("", value="0.0", key="at3_dosage_legal_gnr", disabled=verrou_gnr, label_visibility="collapsed")

    if st.session_state.fraudeur:
        choix_conclusion = [
            "Choisir...", 
            "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)", 
            "Le vehicule est en regle : Aucun residu de colorant fiscal detecte"
        ]
    else:
        choix_conclusion = [
            "Choisir...", 
            "Le vehicule est en regle : Aucun residu de colorant fiscal detecte",
            "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)"
        ]

    c17, c18 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c17: st.write("9. Conclusion finale sur la conformite du carburant inspecte :")
    with c18: st.selectbox("", choix_conclusion, key="at3_conclusion_verdict_gnr", disabled=verrou_gnr, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- LA SUITE DE VOTRE CODE EXISTANT REPREND ICI ---
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    
    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_gnr = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier GNR.", 
        key="check_certif_gnr_final_net", 
        disabled=verrou_gnr
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_gnr_official_net", use_container_width=True, disabled=verrou_gnr):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_gnr:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Recuperation des donnees masquees generees pour cet etudiant
            is_fraudeur = st.session_state.get("fraudeur", False)
            nb_pleins_simules = st.session_state.get("nb_pleins", 0)
            
            # Attendus theoriques exacts
            c_initiale = 10.0  # mg/L
            c_reservoir_attendue = c_initiale / (2 ** nb_pleins_simules) if is_fraudeur else 0.0
            c_extrait_attendue = c_reservoir_attendue * 10.0
            c_molaire_attendue = (c_reservoir_attendue / 1000.0) / 380.44
            if is_fraudeur:
                verdict_attendu = "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)"
            else:
                verdict_attendu = "Le vehicule est en regle : Aucun residu de colorant fiscal detecte"

            # Fonctions de nettoyage des saisies etudiants
            def clean_val(k): return str(st.session_state.get(k, "0.0")).replace(",", ".").strip()
            def clean_txt(k): return str(st.session_state.get(k, "")).strip().lower()

            # 1. Correction de la Partie 1 : Analyse quantitative (10 points)
            try:
                score_q1 = sum([
                    abs(float(clean_val("at3_c_extrait_gnr")) - c_extrait_attendue) < 0.1,
                    abs(float(clean_val("at3_facteur_ext_gnr")) - 10.0) < 0.01,
                    abs(float(clean_val("at3_c_reservoir_gnr")) - c_reservoir_attendue) < 0.1,
                    abs(float(clean_val("at3_masse_molaire_red24")) - 380.44) < 0.01,
                    abs(float(clean_val("at3_c_molaire_reservoir_gnr")) - c_molaire_attendue) < 1e-6
                ]) * (10.0 / 5.0)
            except ValueError:
                score_q1 = 0.0

            # 2. Correction de la Partie 2 : Synthese de cours et Verdict (10 points)
            try:
                score_t1 = sum([
                    clean_txt("gnr_t1_tab4") == "neutre",
                    clean_txt("gnr_t2_tab4") == "polaire",
                    abs(float(clean_val("at3_dosage_legal_gnr")) - 10.0) < 0.01,
                    st.session_state.get("at3_conclusion_verdict_gnr") == verdict_attendu
                ]) * (10.0 / 4.0)
            except ValueError:
                score_t1 = 0.0

            st.session_state.score_gnr_p1 = round(float(score_q1), 1)
            st.session_state.score_gnr_p2 = round(float(score_t1), 1)
            st.session_state.score_final_gnr = round(float(score_q1 + score_t1), 1)
            st.session_state.gnr_verrouille_final = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 4 ---
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
        
        verdict_attendu = (
            "Fraude averee : Du GNR a ete utilise (Presence de colorant detectee)" 
            if is_fraudeur else 
            "Le vehicule est en regle : Aucun residu de colorant fiscal detecte"
        )

        from datetime import datetime, timedelta
        timestamp_gnr = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER GNR SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_gnr = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport GNR - {n_eleve}</title>
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
                <p>Atelier 4 : Controle de la fraude fiscale sur les carburants (GNR)</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_gnr}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue sur les calculs d'extraction (Partie 1) : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue sur la synthese et verdict (Partie 2) : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DES CALCULS QUANTITATIFS D'EXTRACTION</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Parametre cible</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        keys_p1 = ["at3_c_extrait_gnr", "at3_facteur_ext_gnr", "at3_c_reservoir_gnr", "at3_masse_molaire_red24", "at3_c_molaire_reservoir_gnr"]
        labels_p1 = [
            "1. Concentration estimee dans l'extrait concentre (mg/L)",
            "2. Facteur multiplicateur lie a l'extraction liquide-liquide",
            "3. Concentration calculee dans le reservoir du vehicule (mg/L)",
            "4. Masse molaire precise du Solvent Red 24 (g/mol)",
            "5. Concentration molaire dans le reservoir (mol/L)"
        ]
        attendus_p1 = [c_extrait_attendue, 10.0, c_reservoir_attendue, 380.44, c_molaire_attendue]
        tolerances_p1 = [0.1, 0.01, 0.1, 0.01, 1e-6]

        for i in range(5):
            saisie = str(st.session_state.get(keys_p1[i], "0.0")).replace(",", ".").strip()
            attendu = attendus_p1[i]
            try:
                is_ok = abs(float(saisie) - attendu) < tolerances_p1[i]
            except ValueError:
                is_ok = False
            v_lbl = "CORRECT" if is_ok else "INCORRECT"
            v_class = "status-correct" if is_ok else "status-incorrect"
            
            fmt_attendu = f"{attendu:.6e}" if i == 4 else f"{attendu:.2f}"
            html_export_gnr += f"<tr><td>{i+1}</td><td>{labels_p1[i]}</td><td>{saisie}</td><td>{fmt_attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_gnr += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE ET DU VERDICT</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Critere pedagogique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Ligne 6 : Nature chimique
        s_t1 = str(st.session_state.get("gnr_t1_tab4", "")).strip()
        v_ok6 = s_t1.lower() == "neutre"
        html_export_gnr += f"<tr><td>6</td><td>Caractere acido-basique de la molecule</td><td>{s_t1}</td><td>neutre</td><td class='{'status-correct' if v_ok6 else 'status-incorrect'}'>{'CORRECT' if v_ok6 else 'INCORRECT'}</td></tr>"

        # Ligne 7 : Type de solvant
        s_t2 = str(st.session_state.get("gnr_t2_tab4", "")).strip()
        v_ok7 = s_t2.lower() == "polaire"
        html_export_gnr += f"<tr><td>7</td><td>Type de solvant utilise pour extraire</td><td>{s_t2}</td><td>polaire</td><td class='{'status-correct' if v_ok7 else 'status-incorrect'}'>{'CORRECT' if v_ok7 else 'INCORRECT'}</td></tr>"

        # Ligne 8 : Dosage légal
        s_legal = str(st.session_state.get("at3_dosage_legal_gnr", "0.0")).replace(",", ".").strip()
        try: v_ok8 = abs(float(s_legal) - 10.0) < 0.01
        except ValueError: v_ok8 = False
        html_export_gnr += f"<tr><td>8</td><td>Dosage legal minimum requis dans le GNR pur</td><td>{s_legal} mg/L</td><td>10.0 mg/L</td><td class='{'status-correct' if v_ok8 else 'status-incorrect'}'>{'CORRECT' if v_ok8 else 'INCORRECT'}</td></tr>"

        # Ligne 9 : Verdict de conformité
        s_verdict = st.session_state.get("at3_conclusion_verdict_gnr", "Choisir...")
        v_ok9 = s_verdict == verdict_attendu
        html_export_gnr += f"<tr><td>9</td><td>Verdict rendu sur la conformite du véhicule</td><td>{s_verdict}</td><td>{verdict_attendu}</td><td class='{'status-correct' if v_ok9 else 'status-incorrect'}'>{'CORRECT' if v_ok9 else 'INCORRECT'}</td></tr>"

        html_export_gnr += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE BILAN ACADEMIQUE OFFICIEL (HTML)",
            data=html_export_gnr,
            file_name=f"Bilan_GNR_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )








        
