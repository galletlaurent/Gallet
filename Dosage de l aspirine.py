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
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.1
if "animation_active" not in st.session_state: st.session_state.animation_active = False
if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine": { "ph_min": 8.2, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F8BBD0", "nom_zone": "Rose pâle",  "couleur_base": "#E91E63", "nom_base": "Rose fuchsia" },
        "Bleu de Thymol": { "ph_min": 1.2, "ph_max": 2.8,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FFEB3B", "nom_zone": "Jaune", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Hélianthine / Orange de méthyle": {"ph_min": 3.2, "ph_max": 4.4,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Vert de Bromocrésol": { "ph_min": 3.8, "ph_max": 5.4, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#8BC34A", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Rouge de Méthyle": { "ph_min": 4.2, "ph_max": 6.2, "couleur_acide": "#F44336", "nom_acide": "Rouge","couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Bleu de Bromophténol": { "ph_min": 3.0, "ph_max": 4.6, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#00BCD4", "nom_zone": "Vert-Bleu", "couleur_base": "#3F51B5", "nom_base": "Bleu violet" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },
        "Jaune d'Alizarin R": {"ph_min": 10.1, "ph_max": 12.0, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#F44336", "nom_base": "Rouge" }
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
    import random
    
    if "ordre_quiz1_asp" not in st.session_state:
        base_quiz1_asp = [
            {"id": "q1_1", "q": "L'aspirine est une molecule possedant des proprietes :", "type": "menu", "options": ["acides", "neutres", "basiques"], "rep": "acides"},
            {"id": "q1_2", "q": "Calculer la masse molaire moleculaire de l'aspirine pure (C9H8O4) en g/mol :", "type": "menu", "options": ["180,15", "60,05", "150,10"], "rep": "180,15"},
            {"id": "q1_3", "q": "Quel est le nom scientifique officiel de la molecule d'aspirine ?", "type": "menu", "options": ["acide acetylsalicylique", "acide salicylique", "paracetamol"], "rep": "acide acetylsalicylique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes de carbone (C) dans un motif d'aspirine ?", "type": "menu", "options": ["9", "7", "6"], "rep": "9"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogene (H) dans un motif d'aspirine ?", "type": "menu", "options": ["8", "6", "4"], "rep": "8"},
            {"id": "q1_6", "q": "Quel est le nombre d'atomes d'oxygene (O) dans un motif d'aspirine ?", "type": "menu", "options": ["4", "2", "3"], "rep": "4"},
            {"id": "q1_7", "q": "Quelle est la formule brute exacte de l'aspirine commerciale ?", "type": "menu", "options": ["C9H8O4", "C7H6O3", "C6H8O6"], "rep": "C9H8O4"},
            {"id": "q1_8", "q": "D'apres la classification atomique, le nombre de masse de l'element C vaut :", "type": "menu", "options": ["12 g/mol", "14 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "Quelle couleur conventionnelle represente l'atome d'oxygene sur les maquettes ?", "type": "menu", "options": ["Rouge", "Noir", "Blanc"], "rep": "Rouge"},
            {"id": "q1_10", "q": "L'aspirine est utilisee en medecine humaine comme un puissant :", "type": "menu", "options": ["Analgésique (anti-douleur)", "Antibiotique", "Vitamines"], "rep": "Analgésique (anti-douleur)"}
        ]
        copie_base = list(base_quiz1_asp)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_asp = copie_base

    col_double_quiz_asp1, col_double_trous_asp1 = st.columns(2)

    with col_double_quiz_asp1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_asp, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"asp_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_asp_{q_data['id']}"
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

    with col_double_trous_asp1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le principe actif contenu dans un comprime d'aspirine est l'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "acetylsalicylique", "salicylique", "citrique"], key="asp_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale est")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "C9H8O4", "C7H6O3", "C2H4O2"], key="asp_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculee a partir de ses elements constitutifs vaut")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "180,15 g/mol", "60,05 g/mol", "150,00 g/mol"], key="asp_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au sein de son squelette carbone, on compte un total de")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "9 atomes", "7 atomes", "6 atomes"], key="asp_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre d'atomes d'Hydrogene presents dans la structure vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "8 atomes", "6 atomes", "4 atomes"], key="asp_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le nombre d'atomes d'Oxygene fixees sur les fonctions ester/acide est de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "4 atomes", "2 atomes", "3 atomes"], key="asp_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La constante de masse molaire de l'element atomique C est")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "12 g/mol", "1 g/mol", "16 g/mol"], key="asp_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La constante de masse molaire de l'element oxygene O vaut")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "16 g/mol", "12 g/mol", "1 g/mol"], key="asp_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Lors de la manipulation de réactifs corrosifs comme la soude, le port de gants est")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Obligatoire", "Facultatif", "Interdit"], key="asp_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide concentree permet de rapprocher sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7 (neutre)", "0 (acide)", "14 (basique)"], key="asp_t10_tab1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous




def appliquer_couleur_teinte_tableau(valeur_cellule):
    val_str = str(valeur_cellule).lower()
    if "incolore" in val_str:
        return "background-color: #f1f5f9; color: #64748b; font-weight: bold;"
    elif "rose" in val_str or "fuchsia" in val_str:
        return "background-color: #fbcfe8; color: #9d174d; font-weight: bold;"
    elif "jaune" in val_str:
        return "background-color: #fef08a; color: #854d0e; font-weight: bold;"
    elif "bleu" in val_str:
        return "background-color: #bfdbfe; color: #1e40af; font-weight: bold;"
    elif "vert" in val_str:
        return "background-color: #bbf7d0; color: #166534; font-weight: bold;"
    elif "orange" in val_str:
        return "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
    elif "zone" in val_str or "virage" in val_str or "intermediaire" in val_str:
        return "background-color: #fef08a; color: #854d0e; font-weight: bold; font-style: italic;"
    return ""


def appliquer_analyse_geometrique_courbe(ax_cr, volumes_np, phs_np, idx_actuel, v_eq, ph_eq, v_max_ml, chk_tangentes=False):
    import numpy as np
    
    if chk_tangentes and idx_actuel > 5:
        lim_inf = max(0.0, v_eq - 3.5)
        lim_sup = min(v_max_ml, v_eq + 3.5)
        
        idx_inf = np.where(volumes_np <= lim_inf)[0]
        idx_sup = np.where((volumes_np >= lim_sup) & (volumes_np <= v_max_ml))[0]
        
        if len(idx_inf) > 0 and len(idx_sup) > 0:
            v_i = volumes_np[idx_inf[-1]]
            ph_i = phs_np[idx_inf[-1]]
            pente_regulee = 0.08  
            b1 = ph_i - pente_regulee * v_i
            
            v_s = volumes_np[idx_sup[0]]
            ph_s = phs_np[idx_sup[0]]
            b2 = ph_s - pente_regulee * v_s
            
            b_med = (b1 + b2) / 2.0
            v_axe_x = np.linspace(0, v_max_ml, 200)
            
            ax_cr.plot(v_axe_x, pente_regulee * v_axe_x + b1, color="blue", linestyle="-", lw=1.0, alpha=0.6, label="Tangente inf")
            ax_cr.plot(v_axe_x, pente_regulee * v_axe_x + b2, color="blue", linestyle="-", lw=1.0, alpha=0.6, label="Tangente sup")
            ax_cr.plot(v_axe_x, pente_regulee * v_axe_x + b_med, color="blue", linestyle="-", lw=1.2, label="Mediane")
            
            ax_cr.axvline(x=v_eq, color="red", linestyle=":", lw=1.0)
            ax_cr.axhline(y=ph_eq, color="red", linestyle=":", lw=1.0)
            
            ax_cr.scatter([v_eq], [ph_eq], color="red", marker="+", s=150, linewidths=2.5, zorder=6)

    elif not chk_tangentes and idx_actuel > 5:
        derivee_ph = np.diff(phs_np) / np.diff(volumes_np)
        idx_pic = np.argmax(derivee_ph)
        
        v_pic = volumes_np[idx_pic]
        ph_pic = phs_np[idx_pic]
        
        ax_cr.axvline(x=v_pic, color="purple", linestyle="--", lw=1.0, label="Volume Eq (Derivee)")
        ax_cr.scatter([v_pic], [ph_pic], color="purple", marker="x", s=100, linewidths=2.0, zorder=6)

def simuler_et_ajouter_goutte_dosage_aspirine():
    import streamlit as st
    import numpy as np
    import math

    # Paramètres physico-chimiques de la paillasse d'aspirine commerciale
    v_max_ml = 25.0
    V_ini = 20.0  # Volume de prise d'essai mis dans le becher (20 mL)
    pKa = 3.5     # pKa de l'acide acetylsalicylique a 25 degres
    M_aspirine = 180.15
    
    C_base = st.session_state.get("c_base_asp", 0.020)
    masse_g = st.session_state.get("masse_reelle_g_asp", 0.500) # Ex: Comprime standard de 500mg dissous
    v_actuel = st.session_state.get("v_verse_asp", 0.0)
    choix_ind = st.session_state.get("choix_ind_cle_asp", "Phenolphtaleine")

    v_nouveau = round(min(v_max_ml, v_actuel + 0.1), 1)
    st.session_state.v_verse_asp = v_nouveau

    # Calcul des fractions molaires instantanees pour la fiole de 250mL et la prise de 20mL
    # Prise d'essai = 20 mL sur une fiole totale de 250 mL -> facteur 20/250
    n_acide_ini = (masse_g / M_aspirine) * (20.0 / 250.0)
    n_b = (v_nouveau / 1000.0) * C_base
    v_tot = (V_ini / 1000.0) + (v_nouveau / 1000.0)

    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    if v_tot <= 0 or n_acide_ini <= 0:
        ph_point = 1.0
    elif n_b < n_acide_ini:
        if n_b == 0:
            ph_point = max(1.0, 0.5 * (pKa - math.log10(n_acide_ini / (V_ini / 1000.0))))
        else:
            ratio = n_b / n_acide_ini
            ph_point = max(1.5, min(13.0, pKa + math.log10(ratio / (1.0 - ratio))))
    else:
        ratio = n_b / n_acide_ini
        if ratio == 1.0:
            ph_point = ph_eq_theorique
        else:
            ph_point = min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1.0))

    st.session_state.asp_vrai_ph_final = float(ph_point)
    
    if "suivi_gouttes_session_asp" not in st.session_state:
        st.session_state.suivi_gouttes_session_asp = {}

    ind_d = st.session_state.indicateurs[choix_ind]
    if ph_point < ind_d["ph_min"]: 
        obs = ind_d["nom_acide"]
    elif ph_point > ind_d["ph_max"]: 
        obs = ind_d["nom_base"]
    else: 
        obs = ind_d["nom_zone"]

    st.session_state.suivi_gouttes_session_asp[f"Goutte {int(v_nouveau * 10)}"] = {
        "Soude versee V_B (mL)": f"{v_nouveau:.1f}",
        "pH mesure": f"{ph_point:.2f}",
        "Observations / Teinte": obs
    }


def calculer_et_tracer_titrage_aspirine(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez les couples (Volume de soude en mL ; pH mesure) pour tracer la courbe de titrage de l'aspirine."
    
    st.session_state.asp_vrai_total_points = 0.0
    st.session_state.asp_vrai_ph_max = 0.0
    st.session_state.asp_vrai_ph_min = 0.0

    if df_donnees is None or "df_session_asp2" not in st.session_state or st.session_state.df_session_asp2 is None:
        ax.spines['bottom'].set_color('#94a3b8')
        ax.spines['left'].set_color('#94a3b8')
        ax.tick_params(colors='#94a3b8', labelsize=8)
        st.session_state.stats_asp_affichage_texte = stats_text
        return fig

    df_filtre = df_donnees.dropna(subset=["Volume NaOH (mL)", "pH mesure"])
    df_filtre = df_filtre[(df_filtre["Volume NaOH (mL)"].astype(str).str.strip() != "") & (df_filtre["pH mesure"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            df_numerique = df_filtre.copy()
            df_numerique["v_num"] = pd.to_numeric(df_numerique["Volume NaOH (mL)"], errors='coerce')
            df_numerique["ph_num"] = pd.to_numeric(df_numerique["pH mesure"], errors='coerce')
            df_numerique = df_numerique.dropna(subset=["v_num", "ph_num"])

            if not df_numerique.empty:
                df_triee = df_numerique.sort_values(by="v_num")
                vol_x = df_triee["v_num"].to_numpy()
                ph_y = df_triee["ph_num"].to_numpy()

                st.session_state.asp_vrai_total_points = float(len(ph_y))
                st.session_state.asp_vrai_ph_max = float(np.max(ph_y))
                st.session_state.asp_vrai_ph_min = float(np.min(ph_y))

                stats_text = (
                    f"Points collectes : {int(st.session_state.asp_vrai_total_points)}\n"
                    f"pH maximal mesure : {st.session_state.asp_vrai_ph_max:.2f}\n"
                    f"pH minimal mesure : {st.session_state.asp_vrai_ph_min:.2f}"
                )

                # REPARATION AXE CONTINU : vol_x numerique remplace les chaines pour eviter l'espacement lineaire errone
                ax.plot(vol_x, ph_y, color="#38bdf8", marker="o", linestyle="-", lw=2, markersize=6, zorder=3)
                ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
                ax.set_xlim(0.0, 25.0)
                ax.set_ylim(0.0, 14.0)
            else:
                stats_text = "Statistiques indisponibles pour caracteres textuels."
        except Exception:
            stats_text = "Statistiques indisponibles pour caracteres textuels."

    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Volume de soude verse V_B (mL)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("pH de la solution", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Courbe de titrage pH-metrique de l'aspirine", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats_asp_affichage_texte = stats_text
    return fig



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









with tab2:
    st.header("Atelier 2 : Suivi expérimental et tracé de la courbe de titrage")
    st.caption("Ajoutez la soude goutte à goutte et complétez votre tableau de mesures")

    if "verrouille_tab2_asp" not in st.session_state: st.session_state.verrouille_tab2_asp = False
    verrou_tab2 = st.session_state.verrouille_tab2_asp

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # 1. INITIALISATION DE LA PAILLASSE INTERACTIVE DE CHIMIE
    if "v_verse_asp" not in st.session_state: st.session_state.v_verse_asp = 0.0
    if "suivi_gouttes_session_asp" not in st.session_state: st.session_state.suivi_gouttes_session_asp = {}
    if "choix_ind_cle_asp" not in st.session_state: st.session_state.choix_ind_cle_asp = "Phénolphtaléine"

    # Constantes physico-chimiques de référence de l'exercice Aspirine
    v_max_ml = 25.0
    V_ini = 20.0  
    pKa = 3.5     
    M_aspirine = 180.15
    C_base_session = st.session_state.get("c_base_asp", 0.020)
    masse_g = st.session_state.get("masse_reelle_g_asp", 0.500)

    # Dictionnaire des indicateurs colorés réels (Copie conforme du Vinaigre)
    if "indicateurs" not in st.session_state:
        st.session_state.indicateurs = {
            "Héliantine": {"ph_min": 3.1, "ph_max": 4.4, "nom_acide": "Rouge", "nom_zone": "Orange", "nom_base": "Jaune"},
            "Bleu de bromothymol": {"ph_min": 6.0, "ph_max": 7.6, "nom_acide": "Jaune", "nom_zone": "Vert", "nom_base": "Bleu"},
            "Phénolphtaléine": {"ph_min": 8.2, "ph_max": 10.0, "nom_acide": "Incolore", "nom_zone": "Rose pâle", "nom_base": "Rose fuchsia"}
        }

    # --- ZONE DE SÉLECTION DE L'INDICATEUR COLORÉ DE SÉANCE ---
    st.session_state.choix_ind_cle_asp = st.selectbox(
        "Sélectionnez l'indicateur coloré introduit dans l'erlenmeyer :",
        list(st.session_state.indicateurs.keys()),
        index=2, # Phénolphtaléine par défaut
        disabled=verrou_tab2
    )

    # --- INTERFACE DES BOUTONS DE LA BURETTE GRADUÉE ---
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("AJOUTER UNE GOUTTE DE SOUDE (0.1 mL)", key="btn_add_goutte_asp", use_container_width=True, disabled=verrou_tab2):
            simuler_et_ajouter_goutte_dosage_aspirine()
            st.rerun()
            
    with col_btn2:
        if st.button("VIDER ET REINITIALISER LA BURETTE", key="btn_reset_burette_asp", use_container_width=True, disabled=verrou_tab2):
            st.session_state.v_verse_asp = 0.0
            st.session_state.suivi_gouttes_session_asp = {}
            st.rerun()

    # --- RENDU DE LA SOUDE VERSÉE ET DE LA COULEUR DE LA SOLUTION ---
    v_actuel = st.session_state.v_verse_asp
    ph_actuel = st.session_state.get("asp_vrai_ph_final", 2.8)

    # Récupération de la teinte actuelle de l'erlenmeyer
    ind_actif = st.session_state.indicateurs[st.session_state.choix_ind_cle_asp]
    if ph_actuel < ind_actif["ph_min"]: teinte_actuelle = ind_actif["nom_acide"]
    elif ph_actuel > ind_actif["ph_max"]: teinte_actuelle = ind_actif["nom_base"]
    else: teinte_actuelle = ind_actif["nom_zone"]

    style_couleur = appliquer_couleur_teinte_tableau(teinte_actuelle)

    st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px; margin-top: 10px; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 14px;">Volume de soude versé à la burette : <strong style="color: #0284c7; font-size: 18px;">{v_actuel:.1f} mL</strong></p>
            <p style="margin: 5px 0 0 0; font-size: 14px;">Aspect visuel de la solution dans le bécher : 
                <span style="{style_couleur} padding: 4px 10px; border-radius: 4px; text-transform: uppercase;">{teinte_actuelle}</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. TABLEAU DE MESURES INTERACTIF (SOUDE ; pH SÉLECTIONNÉ) ---
    st.subheader("Tableau de mesures pH-métriques expérimentales")
    st.caption("Saisissez les couples de valeurs lues pour chaque volume remarquable afin de tracer votre courbe")

    if "df_session_asp2" not in st.session_state or st.button("GÉNÉRER UN TABLEAU DE MESURES VIERGE (12 LIGNES)", key="btn_clear_df_asp", use_container_width=True, disabled=verrou_tab2):
        st.session_state.df_session_asp2 = pd.DataFrame(
            [["", ""]] * 12,
            columns=["Volume NaOH (mL)", "pH mesure"]
        )

    # Édition en direct de la grille par les élèves
    df_edite = st.data_editor(
        st.session_state.df_session_asp2,
        num_rows="dynamic",
        use_container_width=True,
        disabled=verrou_tab2,
        key="editor_asp_tab2"
    )
    st.session_state.df_session_asp2 = df_edite

    # --- 3. RENDU GRAPHIQUE DYNAMIQUE DE LA COURBE DE L'ÉLÈVE ---
    st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    fig_titrage = calculer_et_tracer_titrage_aspirine(df_edite)
    st.pyplot(fig_titrage)

    if "stats_asp_affichage_texte" in st.session_state:
        st.text(st.session_state.stats_asp_affichage_texte)

    # --- 4. FORMULAIRE DE QUESTIONS SYNCHRONISÉ (QUIZ + TEXTE À TROUS) ---
    st.write("---")
    dict_reponses_quiz, dict_trous = generer_le_quiz_analytique_atelier_deux(df_donnees=df_edite, verrouille=verrou_tab2)

    # --- 5. ENREGISTREMENT ET EXPORTATION DE LA PAILLASSE ---
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 2")

    # Constantes mathématiques de vérification pour le corrigé automatique
    n_acide_dose_ref = C_base_session * 0.0139 
    n_acide_fiole_ref = n_acide_dose_ref * (0.250 / 0.020)
    m_aspirine_calculee_g = n_acide_fiole_ref * M_aspirine
    c_aspirine_dose_attendu = (C_base_session * 13.9) / 20.0

    case_certif_asp2 = st.checkbox("Je certifie avoir complété l'intégralité du questionnaire de l'Atelier 2.", key="check_certif_asp2_final_net", disabled=verrou_tab2)
    
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_asp2_official_net", use_container_width=True, disabled=verrou_tab2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_asp2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if st.session_state.get("col_g_quiz_asp_q1_tab2") == f"{C_base_session:.3f} mol/L": score_q2 += 1.66
            if st.session_state.get("col_g_quiz_asp_q2_tab2") == "20.0 mL": score_q2 += 1.66
            if st.session_state.get("col_g_quiz_asp_q3_tab2") == "13.9 mL": score_q2 += 1.66
            if st.session_state.get("col_g_quiz_asp_q4_tab2") == "Ca * Va = Cb * Ve": score_q2 += 1.66
            if st.session_state.get("col_g_quiz_asp_q5_tab2") == f"{n_acide_dose_ref:.5f} mol": score_q2 += 1.66
            if st.session_state.get("col_g_quiz_asp_q6_tab2") == f"{c_aspirine_dose_attendu:.4f} mol/L": score_q2 += 1.70

            score_t2 = sum([
                st.session_state.get("asp_t1_tab2") == "Burette",
                st.session_state.get("asp_t2_tab2") == "Pipette jaugée",
                st.session_state.get("asp_t3_tab2") == "diviser par 1000",
                st.session_state.get("asp_t4_tab2") == "stoechiométriques",
                st.session_state.get("asp_t5_tab2") == "Saut de pH"
            ]) * 2.0

            st.session_state.score_asp2_p1 = round(float(score_q2), 1)
            st.session_state.score_asp2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_asp2 = round(float(score_q2 + score_t2), 1)
            st.session_state.verrouille_tab2_asp = True
            st.rerun()

    if st.session_state.get("verrouille_tab2_asp", False):
        scr1 = st.session_state.get("score_asp2_p1", 0.0)
        scr2 = st.session_state.get("score_asp2_p2", 0.0)
        tot_s = st.session_state.get("score_final_asp2", 0.0)

        from datetime import datetime, timedelta
        timestamp_asp2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER 2 SCELLÉ | Note globale d'exploitation : {tot_s} / 20")

        html_export_asp2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0284c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #0284c7; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 2 : Exploitation physique de la courbe de titrage de l'aspirine</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_asp2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
                &bull; Note obtenue au Quiz de suivi : <strong>{scr1} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours : <strong>{scr2} / 10</strong><br>
                &bull; Note Finale de l'Atelier 2 : <strong>{tot_s} / 20</strong>
            </p>

            <div class="sub-title">PARTIE 1 : VERDICT DES QUESTIONS DE SUIVI NUMERIQUE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question de paillasse demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Concentration molaire de la solution titrante de soude (Cb)</td><td>{st.session_state.get("col_g_quiz_asp_q1_tab2", "Choisir...")}</td><td>{C_base_session:.3f} mol/L</td></tr>
                    <tr><td>2</td><td>Volume de solution titree d'aspirine introduit (Va)</td><td>{st.session_state.get("col_g_quiz_asp_q2_tab2", "Choisir...")}</td><td>20.0 mL</td></tr>
                    <tr><td>3</td><td>Volume equivalent exact (VE) de soude verse</td><td>{st.session_state.get("col_g_quiz_asp_q3_tab2", "Choisir...")}</td><td>13.9 mL</td></tr>
                    <tr><td>4</td><td>Relation stoechiometrique a l'equivalence</td><td>{st.session_state.get("col_g_quiz_asp_q4_tab2", "Choisir...")}</td><td>Ca * Va = Cb * Ve</td></tr>
                    <tr><td>5</td><td>Quantite de matiere d'ions HO- versee a l'equivalence</td><td>{st.session_state.get("col_g_quiz_asp_q5_tab2", "Choisir...")}</td><td>{n_acide_dose_ref:.5f} mol</td></tr>
                    <tr><td>6</td><td>Concentration molaire (Ca) de l'aspirine deduite</td><td>{st.session_state.get("col_g_quiz_asp_q6_tab2", "Choisir...")}</td><td>{c_aspirine_dose_attendu:.4f} mol/L</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : VERDICT DE LA SYNTHESE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Texte a trous - Concept instrumente</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Verrerie graduee pour la solution titrante</td><td>{st.session_state.get("asp_t1_tab2", "Choisir...")}</td><td>Burette</td></tr>
                    <tr><td>2</td><td>Verrerie de precision pour prelever l'acide</td><td>{st.session_state.get("asp_t2_tab2", "Choisir...")}</td><td>Pipette jaugee</td></tr>
                    <tr><td>3</td><td>Conversion du volume equivalent en Litres</td><td>{st.session_state.get("asp_t3_tab2", "Choisir...")}</td><td>diviser par 1000</td></tr>
                    <tr><td>4</td><td>Proportions des reactifs introduits a l'equivalence</td><td>{st.session_state.get("asp_t4_tab2", "Choisir...")}</td><td>stoechiometriques</td></tr>
                    <tr><td>5</td><td>Reperage de l'equivalence sur courbe d'acide faible</td><td>{st.session_state.get("asp_t5_tab2", "Choisir...")}</td><td>Saut de pH</td></tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Exploitation_Atelier2_Aspirine_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: nom_f2 = nom_f2.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_asp2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )

with tab3:
    st.header("Atelier 3 : Dosage de l'aspirine - Validation analytique")

    # Menu deroulant de filiere adapte au contexte pharmaceutique et industriel
    liste_filieres_asp = ["Pharmacie d'officine", "Maintenance industrielle pharmaceutique", "Controle Qualite"]
    filiere_actuelle_asp = st.session_state.get("var_filiere_asp", "Pharmacie d'officine")
    
    if filiere_actuelle_asp in liste_filieres_asp:
        idx_filiere_asp = liste_filieres_asp.index(filiere_actuelle_asp)
    else:
        idx_filiere_asp = 0

    filiere_active = st.selectbox(
        "Selectionnez votre filiere d'application :",
        liste_filieres_asp,
        index=idx_filiere_asp,
        key="var_filiere_asp"
    )
    st.caption(f"Contexte applicatif : {filiere_active}")

    if "verrouille_tab3_asp" not in st.session_state: 
        st.session_state.verrouille_tab3_asp = False

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    verrouille = st.session_state.get("verrouille_tab3_asp", False)

    # Constantes physico-chimiques officielles de l'acide acetylsalicylique
    M_aspirine = 180.15 
    V_fiole_ref = 0.250  
    C_soude_titrante = 0.020 
    V_prise_essai = 0.020  
    V_equivalence_theorique = 0.0139 

    # Calculs chimiques de reference pour le barème academique
    n_acide_dose_ref = C_soude_titrante * V_equivalence_theorique 
    n_acide_fiole_ref = n_acide_dose_ref * (V_fiole_ref / V_prise_essai) 
    m_aspirine_calculee_g = n_acide_fiole_ref * M_aspirine 

    # Configuration predictive des variables memoires pour forcer le tableau vide (0.00)
    for cle_asp in ["asp_m11", "asp_m12", "asp_tot1", "asp_m21", "asp_m22", "asp_tot2", "asp_m31", "asp_m32"]:
        if cle_asp not in st.session_state or isinstance(st.session_state[cle_asp], str):
            st.session_state[cle_asp] = 0.00

    # Definition de la phrase d'introduction selon la filiere metier selectionnee
    if "officine" in filiere_active.lower():
        txt_contexte = "Un preparateur en pharmacie controle la masse en principe actif d'un comprime d'aspirine standard."
    else:
        txt_contexte = "Un technicien de laboratoire realise le suivi analytique par titrage acido-basique d'un lot d'aspirine."

    # --- RENDU DE L'ÉNONCÉ FORMEL DE PAILLASSE ---
    with st.container(border=True):
        st.markdown("<p style='color: #1e3a8a; font-weight: bold; margin-bottom: 5px; font-size: 15px;'>PROTOCOLE EXPERIMENTAL ET DONNEES</p>", unsafe_allow_html=True)
        st.write(txt_contexte)
        st.write("Le comprime est dissous dans une fiole jaugee de $V_0 = 250\\text{ mL}$. On titre une prise d'essai de $V_A = 20\\text{ mL}$ par une solution de soude de concentration $C_B = 0,020\\text{ mol/L}$.")
        st.latex("V_{\\text{equivalence}} = 13,9\\text{ mL}")
        st.latex("M_{\\text{aspirine}} = 180,15\\text{ g/mol}")

    # --- GRILLE DE COMPLÉTION DU TABLEAU (SAISIE NUMÉRIQUE DIRECTE EN BLANC) ---
    st.subheader("Grille des resultats du titrage a completer")
    st.caption("Remplissez l'integralite des cellules du tableau au clavier")

    hdr_c1, hdr_c2, hdr_c3, hdr_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with hdr_c2: st.markdown("<p style='text-align:center; font-weight:bold; color:#1e3a8a; margin-bottom:2px;'>Prise d'essai (20 mL)</p>", unsafe_allow_html=True)
    with hdr_c3: st.markdown("<p style='text-align:center; font-weight:bold; color:#1e3a8a; margin-bottom:2px;'>Fiole Jaugee (250 mL)</p>", unsafe_allow_html=True)
    with hdr_c4: st.markdown("<p style='text-align:center; font-weight:bold; color:#0f172a; margin-bottom:2px;'>TOTAL COMPRIME</p>", unsafe_allow_html=True)

    # Ligne 1 : Quantite de matiere n (mol)
    l1_c1, l1_c2, l1_c3, l1_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with l1_c1: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold;'>Matiere n (mol)</div>", unsafe_allow_html=True)
    with l1_c2: v11 = st.number_input("", min_value=0.0000, max_value=1.0000, value=st.session_state.asp_m11, step=0.0001, format="%.4f", key="inp_asp_m11", disabled=verrouille, label_visibility="collapsed")
    with l1_c3: v12 = st.number_input("", min_value=0.0000, max_value=1.0000, value=st.session_state.asp_m12, step=0.0001, format="%.4f", key="inp_asp_m12", disabled=verrouille, label_visibility="collapsed")
    with l1_c4: v_t1 = st.number_input("", min_value=0.0000, max_value=1.0000, value=st.session_state.asp_tot1, step=0.0001, format="%.4f", key="inp_asp_tot1", disabled=verrouille, label_visibility="collapsed")

    # Ligne 2 : Masse m (g)
    l2_c1, l2_c2, l2_c3, l2_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with l2_c1: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold;'>Masse m (g)</div>", unsafe_allow_html=True)
    with l2_c2: v21 = st.number_input("", min_value=0.00, max_value=10.00, value=st.session_state.asp_m21, step=0.01, format="%.2f", key="inp_asp_m21", disabled=verrouille, label_visibility="collapsed")
    with l2_c3: v22 = st.number_input("", min_value=0.00, max_value=10.00, value=st.session_state.asp_m22, step=0.01, format="%.2f", key="inp_asp_m22", disabled=verrouille, label_visibility="collapsed")
    with l2_c4: v_t2 = st.number_input("", min_value=0.00, max_value=10.00, value=st.session_state.asp_tot2, step=0.01, format="%.2f", key="inp_asp_tot2", disabled=verrouille, label_visibility="collapsed")

    # Ligne 3 : Concentration C (mol/L)
    l3_c1, l3_c2, l3_c3, l3_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with l3_c1: st.markdown("<div style='background-color:#cbd5e1; padding:8px; border-radius:4px; font-weight:bold;'>Concentration (mol/L)</div>", unsafe_allow_html=True)
    with l3_c2: v31 = st.number_input("", min_value=0.000, max_value=5.000, value=st.session_state.asp_m31, step=0.001, format="%.3f", key="inp_asp_m31", disabled=verrouille, label_visibility="collapsed")
    with l3_c3: v32 = st.number_input("", min_value=0.000, max_value=5.000, value=st.session_state.asp_m32, step=0.001, format="%.3f", key="inp_asp_m32", disabled=verrouille, label_visibility="collapsed")
    with l3_c4: st.markdown("<div style='background-color:#cbd5e1; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>Idem</div>", unsafe_allow_html=True)

    # Sauvegarde immediate en session pour l'analyse
    st.session_state.asp_m11 = float(v11)
    st.session_state.asp_m12 = float(v12)
    st.session_state.asp_tot1 = float(v_t1)
    st.session_state.asp_m21 = float(v21)
    st.session_state.asp_m22 = float(v22)
    st.session_state.asp_tot2 = float(v_t2)
    st.session_state.asp_m31 = float(v31)
    st.session_state.asp_m32 = float(v32)

    st.write("---")
    col_g_asp, col_d_asp = st.columns(2)

    with col_g_asp:
        st.markdown("##### 1. Suivi Colorimetrique (Indicateurs Colores)")
        st.write("L'aspirine (acide acetylsalicylique) est un acide faible dont le pH a l'equivalence se situe aux alentours de **8,3** lors d'un titrage par la soude.")
        
        opt_indicateurs = ["Choisir...", "Heliantine (zone de virage : 3,1 - 4,4)", "Bleu de bromothymol (zone de virage : 6,0 - 7,6)", "Phenolphtaleine (zone de virage : 8,2 - 10,0)"]
        asp_ind_saisie = st.selectbox(
            "Selectionnez l'indicateur colore le plus adapte pour ce titrage :",
            opt_indicateurs,
            key="asp_indicateur_colore",
            disabled=verrouille
        )
        
        st.write("Quel changement de couleur observez-vous a l'equivalence avec cet indicateur ?")
        asp_col_saisie = st.selectbox(
            "Changement de teinte de la solution dans l'erlenmeyer :",
            ["Choisir...", "De l'incolore au rose persistant", "Du jaune au bleu", "Du rouge au jaune"],
            key="asp_couleur_virage",
            disabled=verrouille
        )

    with col_d_asp:
        st.markdown("##### 2. Suivi pH-metrique (Saut de pH)")
        st.write("A l'aide de la courbe de titrage $pH = f(V_B)$ obtenue sur votre terminal de paillasse, determinez les coordonnées du point d'equivalence.")
        
        # Saisie directe au clavier du volume et du pH equivalent
        asp_veq_saisie = st.number_input(
            "Volume de soude verse a l'equivalence $V_{E}$ (mL) :",
            min_value=0.0,
            max_value=25.0,
            value=st.session_state.get("asp_veq_saisie_val", 0.0),
            step=0.1,
            format="%.1f",
            key="asp_veq_saisie_val",
            disabled=verrouille
        )
        
        asp_pheq_saisie = st.number_input(
            "pH de la solution a l'equivalence $pH_{E}$ :",
            min_value=0.0,
            max_value=14.0,
            value=st.session_state.get("asp_pheq_saisie_val", 0.0),
            step=0.1,
            format="%.1f",
            key="asp_pheq_saisie_val",
            disabled=verrouille
        )

    # --- BLOC DE VERROUILLAGE ET CORRECTION AUTOMATIQUE SUR 28 POINTS ---
    st.subheader("Validation et Generation du Bilan Officiel - Aspirine")
    case_certif_asp = st.checkbox("Je certifie avoir complete l'integralite des calculs et observations.", key="check_certif_asp", disabled=verrouille)

    if st.button("VALIDER ET EXPORTER LE BILAN DE DOSAGE ASPIRINE", key="btn_export_asp_final", use_container_width=True, disabled=verrouille):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_asp:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Notation de la grille numerique (8 cases = 8 points)
            scr_grille = sum([
                abs(st.session_state.asp_m11 - n_acide_dose_ref) < 0.001,
                abs(st.session_state.asp_m12 - n_acide_fiole_ref) < 0.001,
                abs(st.session_state.asp_tot1 - n_acide_fiole_ref) < 0.001,
                abs(st.session_state.asp_m21 - (n_acide_dose_ref * M_aspirine)) < 0.05,
                abs(st.session_state.asp_m22 - m_aspirine_calculee_g) < 0.05,
                abs(st.session_state.asp_tot2 - m_aspirine_calculee_g) < 0.05,
                abs(st.session_state.asp_m31 - (n_acide_fiole_ref / V_fiole_ref)) < 0.005,
                abs(st.session_state.asp_m32 - (n_acide_fiole_ref / V_fiole_ref)) < 0.005
            ])

            # 2. Notation de la partie colorimetrique (2 questions = 10 points)
            scr_colorimetrie = sum([
                st.session_state.asp_indicateur_colore == "Phenolphtaleine (zone de virage : 8,2 - 10,0)",
                st.session_state.asp_couleur_virage == "De l'incolore au rose persistant"
            ]) * 5.0

            # 3. Notation de la partie pH-metrique (2 coordonnees = 10 points)
            scr_phmetrie = sum([
                abs(st.session_state.asp_veq_saisie_val - 13.9) < 0.2,
                abs(st.session_state.asp_pheq_saisie_val - 8.3) < 0.3
            ]) * 5.0

            st.session_state.score_asp_grille = float(scr_grille)
            st.session_state.score_asp_col = float(scr_colorimetrie)
            st.session_state.score_asp_ph = float(scr_phmetrie)
            st.session_state.score_final_asp = round(float(scr_grille + scr_colorimetrie + scr_phmetrie), 1)
            st.session_state.verrouille_tab3_asp = True
            st.rerun()

    if st.session_state.get("verrouille_tab3_asp", False):
        s_g = st.session_state.get("score_asp_grille", 0.0)
        s_c = st.session_state.get("score_asp_col", 0.0)
        s_p = st.session_state.get("score_asp_ph", 0.0)
        tot_asp = st.session_state.get("score_final_asp", 0.0)

        st.success(f"DOSAGE ASPIRINE SCELLE | Note globale de session : {tot_asp} / 28")

        # --- ARBORESCENCE HTML MIS À JOUR AVEC LES DEUX RAPPORTS DE METHODES ---
        html_aspirine = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Titrage Aspirine - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0284c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; }}
                .score-badge {{ float: right; background-color: #eab308; color: #1e293b; padding: 15px; border-radius: 8px; font-size: 22px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; margin-bottom: 25px; }}
                th {{ background-color: #0f172a; color: white; padding: 12px; }}
                td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <div class="score-badge">SCORE : {tot_asp} / 28</div>
                <h1>Professeur Laurent GALLET</h1>
                <p>Bilan complet : Dosage colorimetrique et pH-metrique de l'aspirine</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
            </div>
            
            <h2>1. Grille des Resultats Numeriques (Score : {s_g} / 8)</h2>
            <table>
                <thead>
                    <tr><th>Grandeur chimique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr><td>Matiere Prise d'essai (mol)</td><td>{st.session_state.get("asp_m11", 0.00):.5f}</td><td>{n_acide_dose_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("asp_m11", 0.00) - n_acide_dose_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("asp_m11", 0.00) - n_acide_dose_ref) < 0.001 else "INCORRECT"}</td></tr>
                    <tr><td>Matiere Fiole jaugee (mol)</td><td>{st.session_state.get("asp_m12", 0.00):.5f}</td><td>{n_acide_fiole_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("asp_m12", 0.00) - n_acide_fiole_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("asp_m12", 0.00) - n_acide_fiole_ref) < 0.001 else "INCORRECT"}</td></tr>
                    <tr><td>Total Masse Comprime (g)</td><td>{st.session_state.get("asp_tot2", 0.00):.3f}</td><td>{m_aspirine_calculee_g:.3f}</td><td class="{"status-correct" if abs(st.session_state.get("asp_tot2", 0.00) - m_aspirine_calculee_g) < 0.05 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("asp_tot2", 0.00) - m_aspirine_calculee_g) < 0.05 else "INCORRECT"}</td></tr>
                </tbody>
            </table>

            <h2>2. Validation du Suivi Colorimetrique (Score : {s_c} / 10)</h2>
            <table>
                <thead>
                    <tr><th>Parametre observe</th><th>Reponse de l'eleve</th><th>Attendu Professeur</th></tr>
                </thead>
                <tbody>
                    <tr><td>Choix de l'indicateur colore</td><td>{st.session_state.get("asp_indicateur_colore", "Choisir...")}</td><td>Phenolphtaleine (zone de virage : 8,2 - 10,0)</td></tr>
                    <tr><td>Teinte au virage a l'equivalence</td><td>{st.session_state.get("asp_couleur_virage", "Choisir...")}</td><td>De l'incolore au rose persistant</td></tr>
                </tbody>
            </table>

            <h2>3. Validation du Suivi pH-metrique (Score : {s_p} / 10)</h2>
            <table>
                <thead>
                    <tr><th>Coordonnee de l'equivalence</th><th>Saisie Eleve</th><th>Attendu Professeur</th></tr>
                </thead>
                <tbody>
                    <tr><td>Volume equivalent V_E (mL)</td><td>{st.session_state.get("asp_veq_saisie_val", 0.0):.1f} mL</td><td>13.9 mL</td></tr>
                    <tr><td>pH a l'equivalence pH_E</td><td>{st.session_state.get("asp_pheq_saisie_val", 0.0):.1f}</td><td>8.3</td></tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_f_asp = f"Rapport_Dosage_Aspirine_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ASPIRINE SUR VOTRE ORDINATEUR", 
            data=html_aspirine, 
            file_name=f"{nom_f_asp}.html", 
            mime="text/html", 
            use_container_width=True
        )







































