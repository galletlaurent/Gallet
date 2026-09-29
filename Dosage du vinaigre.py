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
    "Généralités sur le vinaigre",
    "Dosage colorimétrique du vinaigre",
    "Calcul théorique sur le vinaigre et vérification de l'inscription sur la bouteille"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

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
    
    # 1. TRACÉ EXCLUSIF ET FIABLE DE LA MÉTHODE DES TANGENTES PARALLÈLES
    if chk_tangentes and idx_actuel > 5:
        lim_inf = max(0.0, v_eq - 3.5)
        lim_sup = min(v_max_ml, v_eq + 3.5)
        
        idx_inf = np.where(volumes_np <= lim_inf)[0]
        idx_sup = np.where((volumes_np >= lim_sup) & (volumes_np <= v_max_ml))[0]
        
        if len(idx_inf) > 0 and len(idx_sup) > 0:
            v_i = volumes_np[idx_inf[-1]]
            ph_i = phs_np[idx_inf[-1]]
            pente_regulee = 0.12  # Inclinaison standardisee pour le vinaigre commercial
            b1 = ph_i - pente_regulee * v_i
            
            v_s = volumes_np[idx_sup[0]]
            ph_s = phs_np[idx_sup[0]]
            b2 = ph_s - pente_regulee * v_s
            
            b_med = (b1 + b2) / 2.0
            v_axe_x = np.linspace(0, v_max_ml, 200)
            
            # Dessin des deux tangentes paralleles et de la droite equidistante
            ax_cr.plot(v_axe_x, pente_regulee * v_axe_x + b1, color="blue", linestyle="-", lw=1.0, alpha=0.6, label="Tangente inf")
            ax_cr.plot(v_axe_x, pente_regulee * v_axe_x + b2, color="blue", linestyle="-", lw=1.0, alpha=0.6, label="Tangente sup")
            ax_cr.plot(v_axe_x, pente_regulee * v_axe_x + b_med, color="blue", linestyle="-", lw=1.2, label="Mediane")
            
            # Point equivalent geometrique central
            ax_cr.axvline(x=v_eq, color="red", linestyle=":", lw=1.0)
            ax_cr.axhline(y=ph_eq, color="red", linestyle=":", lw=1.0)
            
            # Marquage du point central de l'equivalence
            ax_cr.scatter([v_eq], [ph_eq], color="red", marker="+", s=150, linewidths=2.5, zorder=6)


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

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("Convertir le volume équivalent en litre")
    with c2: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_v_eq_l", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("Calculer le nombre de mole de soude versee :")
    with c4: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_soude", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("En déduire le nombre de mole de vinaigre dosée")
    with c6: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide_becher", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("Calculer la concentration molaire en vinaigre dosée en mol/L")
    with c8: st.number_input("", min_value=0.000, max_value=10.000, format="%.3f", key="at3_c_molaire_fille", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("Calculer la masse de vinaigre dosée en gramme")
    with c10: st.number_input("", min_value=0.0000, max_value=100.0000, format="%.4f", key="at3_m_acide_gramme", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("En déduire la masse de vinaigre dosée en milligramme")
    with c12: st.number_input("", min_value=0.0, max_value=10000.0, format="%.1f", key="at3_m_acide_mg", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("Calculer la concentration massique de vinaigre dosee en g/L")
    with c14: st.number_input("", min_value=0.00, max_value=500.00, format="%.2f", key="at3_c_massique_fille", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("Calculer la concentration massique de vinaigre dosée en mg/L")
    with c16: st.number_input("", min_value=0.0, max_value=500000.0, format="%.1f", key="at3_c_massique_fille_mg", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : REMONTÉE À LA BOUTEILLE COMMERCIALE ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("Donner le rapport de dilution ?")
    with c18: st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_rapport_dilution", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("En déduire le nombre de mole de vinaigre dans la fiole")
    with c20: st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide_fiole", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("En déduire le nombre de mole de vinaigre dans la bouteille")
    with c22: st.number_input("", min_value=0.00000, max_value=5.00000, format="%.5f", key="at3_n_acide_bouteille", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c23: st.write("Calculer la concentration molaire en vinaigre de la bouteille en mol/L")
    with c24: st.number_input("", min_value=0.00, max_value=20.00, format="%.2f", key="at3_c_molaire_mere", disabled=verrouille, label_visibility="collapsed")

    c25, c26 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c25: st.write("Calculer la masse de vinaigre dans la bouteille en gramme")
    with c26: st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_m_mere_gramme", disabled=verrouille, label_visibility="collapsed")

    c27, c28 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c27: st.write("En déduire la masse de vinaigre dans la bouteille en milligramme")
    with c28: st.number_input("", min_value=0.0, max_value=1000000.0, format="%.1f", key="at3_m_mere_mg", disabled=verrouille, label_visibility="collapsed")

    c29, c30 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c29: st.write("Calculer la concentration massique de vinaigre de la bouteille en g/L")
    with c30: st.number_input("", min_value=0.0, max_value=1000.0, format="%.1f", key="at3_c_massique_mere", disabled=verrouille, label_visibility="collapsed")

    c31, c32 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c31: st.write("en déduire le degré de votre vinaigre")
    with c32: st.number_input("", min_value=0.0, max_value=1000000.0, format="%.1f", key="at3_c_massique_mere_mg", disabled=verrouille, label_visibility="collapsed")


    c33, c34 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c33: st.write("Conclure sur l'affichage de la bouteille")
    with c34: st.selectbox("", ["Choisir...", "Le vinaigre est conforme a l'étiquette (8°)", "Le vinaigre n'est pas conforme"], key="at3_conclusion_bouteille", disabled=verrouille, label_visibility="collapsed")



    st.markdown('</div>', unsafe_allow_html=True)

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

        opts_q6 = ["Choisir...", f"{c_vinaigre_dosée_attendu:.3f} mol/L", "0.010 mol/L", "0.100 mol/L"]
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





def simuler_et_ajouter_goutte_dosage():
    import streamlit as st
    import numpy as np
    import math

    # Recupération securisee des parametres du flacon de la session
    v_max_ml = 25.0
    V_ini = 10.0
    pKa = 4.8
    M_vinaigre = 60.0
    
    C_base = st.session_state.get("c_base", 0.1)
    masse_g = st.session_state.get("masse_reelle_g", 0.085)
    v_actuel = st.session_state.get("v_verse", 0.0)
    choix_ind = st.session_state.get("choix_ind_cle", "Phenolphtaleine")

    # Increment d'une goutte unique de 0.1 mL
    v_nouveau = round(min(v_max_ml, v_actuel + 0.1), 1)
    st.session_state.v_verse = v_nouveau

    # Calcul physico-chimique instantane du pH pour ce point précis
    n_acide_ini = masse_g / M_vinaigre
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
            ph_point = max(1.0, min(13.0, pKa + math.log10(ratio / (1.0 - ratio))))
    else:
        ratio = n_b / n_acide_ini
        if ratio == 1.0:
            ph_point = ph_eq_theorique
        else:
            ph_point = min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1.0))

    # Synchronisation instantanee des etats de la paillasse numerique
    st.session_state.vin_vrai_ph_final = float(ph_point)
    
    # Historisation immediate de la goutte dans la matrice de suivi
    if "suivi_gouttes_session" not in st.session_state:
        st.session_state.suivi_gouttes_session = {}

    ind_d = st.session_state.indicateurs[choix_ind]
    if ph_point < ind_d["ph_min"]: 
        obs = ind_d["nom_acide"]
    elif ph_point > ind_d["ph_max"]: 
        obs = ind_d["nom_base"]
    else: 
        obs = ind_d["nom_zone"]

    st.session_state.suivi_gouttes_session[f"Goutte {int(v_nouveau * 10)}"] = {
        "Soude versee V_B (mL)": f"{v_nouveau:.1f}",
        "pH mesure": f"{ph_point:.2f}",
        "Observations / Teinte": obs
    }

def calculer_et_tracer_titrage_vinaigre(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez les couples (Volume de soude en mL ; pH mesure) pour tracer la courbe de titrage."
    
    st.session_state.vin_vrai_total_points = 0.0
    st.session_state.vin_vrai_ph_max = 0.0
    st.session_state.vin_vrai_ph_min = 0.0

    if df_donnees is None or "df_session_vin2" not in st.session_state or st.session_state.df_session_vin2 is None:
        ax.spines['bottom'].set_color('#94a3b8')
        ax.spines['left'].set_color('#94a3b8')
        ax.tick_params(colors='#94a3b8', labelsize=8)
        st.session_state.stats_vin_affichage_texte = stats_text
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
                labels_x = df_triee["v_num"].astype(str).tolist()

                st.session_state.vin_vrai_total_points = float(len(ph_y))
                st.session_state.vin_vrai_ph_max = float(np.max(ph_y))
                st.session_state.vin_vrai_ph_min = float(np.min(ph_y))

                stats_text = (
                    f"Moyenne : {np.mean(ph_y):.2f}\n"
                    f"pH maximal : {st.session_state.vin_vrai_ph_max:.2f}\n"
                    f"pH minimal : {st.session_state.vin_vrai_ph_min:.2f}"
                )

                ax.plot(labels_x, ph_y, color="#38bdf8", marker="o", linestyle="-", lw=2, markersize=6, zorder=3)
                ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            else:
                stats_text = "Statistiques indisponibles pour caracteres textuels."
        except Exception:
            stats_text = "Statistiques indisponibles pour caracteres textuels."

    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Volume de base HO- verse V (mL)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("pH de la solution", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Courbe de titrage pH-metrique", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats_vin_affichage_texte = stats_text
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

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_vin1_official_net", use_container_width=True, disabled=verrou_vin1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusee : Cochez la case de certification.")
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
    pKa = 4.17
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
        st.subheader("Paramètres de la solution titrante et du goutte-a-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.session_state.c_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :", 
                min_value=0.01, max_value=2.0, value=st.session_state.c_base, step=0.01,
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

    st.info(f"Compose : Vinaigre | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L")
    st.divider()

    # Algorithme mathematique pour generer la courbe complete
    def extraire_ph_calcul_tp(v_b_ml):
        v_b = v_b_ml / 1000.0
        v_a_total = V_ini / 1000.0
        n_b = v_b * C_base
        v_tot = v_a_total + v_b
        if v_tot <= 0 or n_acide_ini <= 0: return 1.0
        if n_b < n_acide_ini:
            if n_b == 0:
                c_acide_ini = n_acide_ini / v_a_total
                return max(1.0, 0.5 * (pKa - math.log10(c_acide_ini)))
            ratio = n_b / n_acide_ini
            return max(1.0, min(13.0, pKa + math.log10(ratio / (1.0 - ratio))))
        else:
            ratio = n_b / n_acide_ini
            if ratio == 1.0: return ph_eq_theorique
            return min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1.0))

    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    volumes_simules = np.arange(0, v_max_ml + 0.1, 0.1)
    phs_simules = [extraire_ph_calcul_tp(v) for v in volumes_simules]

    # --- BARRE DE COMMANDE DE L'ANIMATION DU TP ---
    st.subheader("Ajout progressif de la solution titrante")
    col_b1, col_b2, col_sl = st.columns([1.1, 0.9, 2.0], vertical_alignment="bottom")
    
    with col_b1:
        activer_flux = st.button("Demarrer le versement automatique", key="btn_run_auto_soude", use_container_width=True, disabled=st.session_state.vin_verrouille_tab2)
    with col_b2:
        if st.button("Effacer tout", key="btn_clear_auto_soude", use_container_width=True, disabled=st.session_state.vin_verrouille_tab2):
            st.session_state.v_verse = 0.0
            st.session_state.animation_active = False
            st.rerun()
    with col_sl:
        v_manuel = st.slider("Volume de soude total verse V_B (mL) :", min_value=0.0, max_value=v_max_ml, value=float(st.session_state.v_verse), step=0.1, disabled=st.session_state.vin_verrouille_tab2, key="slider_vol_principal_at2")
        if not activer_flux and not st.session_state.get("animation_active", False): 
            st.session_state.v_verse = float(v_manuel)

    # --- EXÉCUTION DE LA BOUCLE WHILE DANS LE CONTENEUR DYNAMIQUE ---
    if activer_flux: 
        st.session_state.animation_active = True

    conteneur_paillasse_animee = st.empty()

    while st.session_state.get("animation_active", False) and st.session_state.v_verse < v_max_ml:
        import time
        st.session_state.v_verse = round(min(v_max_ml, st.session_state.v_verse + 0.1), 1)
        
        idx_b = min(int(round(st.session_state.v_verse * 10)), len(volumes_simules) - 1)
        ph_b = phs_simules[idx_b]

        ind_data = st.session_state.indicateurs[choix_ind]
        if ph_b < ind_data["ph_min"]:
            couleur_sol = ind_data["couleur_acide"]; nom_teinte = ind_data["nom_acide"]
        elif ph_b > ind_data["ph_max"]:
            couleur_sol = ind_data["couleur_base"]; nom_teinte = ind_data["nom_base"]
        else:
            couleur_sol = ind_data["couleur_zone"]; nom_teinte = ind_data["nom_zone"]

        fig_m, ax_mo = plt.subplots(figsize=(4, 4.2), facecolor="white")
        ax_mo.set_facecolor("white")
        ax_mo.add_patch(patches.Rectangle((1.0, 0.5), 0.3, 9.0, color="#7f8c8d"))
        ax_mo.add_patch(patches.Rectangle((1.3, 8.0), 3.2, 0.15, color="#95a5a6"))
        hauteur_b = 3.5 * (1.0 - (st.session_state.v_verse / v_max_ml))
        ax_mo.add_patch(patches.Rectangle((3.6, 4.5), 0.6, 4.0, facecolor="none", edgecolor="#34495e", linewidth=2))
        ax_mo.add_patch(patches.Rectangle((3.62, 4.52), 0.56, hauteur_b, facecolor="#aed6f1", alpha=0.8))
        ax_mo.add_patch(patches.Rectangle((3.8, 4.1), 0.2, 0.4, color="#2c3e50"))
        ax_mo.add_patch(patches.Circle((3.9, 3.7), 0.08, color="#aed6f1"))
        hauteur_liq = 1.0 + 1.2 * (st.session_state.v_verse / v_max_ml)
        ax_mo.add_patch(patches.Polygon([[2.6, 1.0], [2.6, 3.2], [4.8, 3.2], [4.8, 1.0]], facecolor="none", edgecolor="#34495e", linewidth=3))
        ax_mo.add_patch(patches.Rectangle((2.65, 1.05), 2.1, hauteur_liq, facecolor=couleur_sol, alpha=0.75))
        ax_mo.add_patch(patches.Rectangle((2.2, 0.3), 3.0, 0.7, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=2))
        angle_barreau = 8 if idx_b % 2 == 0 else -8
        ax_mo.add_patch(patches.Rectangle((3.1, 1.1), 1.2, 0.15, facecolor="#ffffff", edgecolor="#7f8c8d", angle=angle_barreau))
        ax_mo.add_patch(patches.Rectangle((4.3, 1.6), 0.3, 3.0, color="#34495e"))
        ax_mo.plot([4.45, 4.45, 5.5], [4.6, 7.5, 7.5], color="#34495e", linewidth=2)
        ax_mo.add_patch(patches.Rectangle((5.5, 6.5), 2.2, 1.5, facecolor="#2c3e50", edgecolor="#1a252f", linewidth=2))
        ax_mo.text(6.6, 7.2, f"pH: {ph_b:.2f}", color="#2ecc71", fontfamily="monospace", weight="bold", fontsize=11, ha="center")
        ax_mo.text(3.7, 0.05, f"Teinte : {nom_teinte}", color="#1e293b", fontsize=9, ha="center")
        ax_mo.set_xlim(0.5, 8.0)
        ax_mo.set_ylim(0.0, 9.5)
        ax_mo.axis("off")

        with conteneur_paillasse_animee.container():
            c_v, c_g = st.columns([1, 1.2])
            with c_v: st.pyplot(fig_m)
            with c_g:
                fig_c, ax_cr = plt.subplots(figsize=(4.5, 3.8))
                ax_cr.axhspan(0, ind_data["ph_min"], facecolor=ind_data["couleur_acide"], alpha=0.15, zorder=0)
                ax_cr.axhspan(ind_data["ph_min"], ind_data["ph_max"], facecolor=ind_data["couleur_zone"], alpha=0.20, zorder=0)
                ax_cr.axhspan(ind_data["ph_max"], 14, facecolor=ind_data["couleur_base"], alpha=0.15, zorder=0)
                ax_cr.plot(volumes_simules[:idx_b+1], phs_simules[:idx_b+1], color="black", linewidth=2.0)
                ax_cr.scatter([st.session_state.v_verse], [ph_b], color="red", s=60, zorder=5)
                ax_cr.set_xlim(0, v_max_ml + 1)
                ax_cr.set_ylim(0, 14)
                ax_cr.grid(True, linestyle=":")
                st.pyplot(fig_c)
                plt.close(fig_c)
            
            st.write("---")
            st.subheader("Tableau de suivi (3 lignes - Colonnes multiples)")
            matrice_b = {}
            for i_b in range(idx_b + 1):
                v_p = volumes_simules[i_b]
                ph_p = phs_simules[i_b]
                obs_p = ind_data["nom_acide"] if ph_p < ind_data["ph_min"] else (ind_data["nom_base"] if ph_p > ind_data["ph_max"] else ind_data["nom_zone"])
                matrice_b[f"Goutte {i_b}"] = {"Soude versee V_B (mL)": f"{v_p:.1f}", "pH mesure": f"{ph_p:.2f}", "Observations / Teinte": obs_p}
            import pandas as pd
            df_gouttes_b = pd.DataFrame.from_dict(matrice_b, orient="index").T
            # Application de la coloration en direct dixieme par dixieme
            st.dataframe(df_gouttes_b.style.map(appliquer_couleur_teinte_tableau), use_container_width=True)

        plt.close(fig_m)
        time.sleep(0.01)

    if st.session_state.v_verse >= v_max_ml:
        st.session_state.animation_active = False

    # Synchronisation finale statique a l'arret
    idx_actuel = min(int(round(st.session_state.v_verse * 10)), len(volumes_simules) - 1)
    ph_actuel = phs_simules[idx_actuel]

    st.session_state.vin_vrai_ph_final = float(ph_actuel)
    st.session_state.vin_vrai_veq_calc = float(v_eq_theorique)
    st.session_state.vin_vrai_total_points = float(idx_actuel + 1)
    st.session_state.vin_vrai_ph_max = float(np.max(phs_simules))
    st.session_state.vin_vrai_ph_min = float(np.min(phs_simules))

    # Synchronisation immediate des valeurs pour l'Atelier 3
    st.session_state.input_at2_ve_lu_eleve = float(v_eq_theorique)
    st.session_state.input_at2_phe_lu_eleve = float(ph_eq_theorique)




    # --- RENDU DE REPOS FIXE INTERACTIF ---
    if not st.session_state.get("animation_active", False):
        ind_data = st.session_state.indicateurs[choix_ind]
        if ph_actuel < ind_data["ph_min"]:
            couleur_sol = ind_data["couleur_acide"]; nom_teinte = ind_data["nom_acide"]
        elif ph_actuel > ind_data["ph_max"]:
            couleur_sol = ind_data["couleur_base"]; nom_teinte = ind_data["nom_base"]
        else:
            couleur_sol = ind_data["couleur_zone"]; nom_teinte = ind_data["nom_zone"]

        fig_m, ax_mo = plt.subplots(figsize=(4, 4.2), facecolor="white")
        ax_mo.set_facecolor("white")
        ax_mo.add_patch(patches.Rectangle((1.0, 0.5), 0.3, 9.0, color="#7f8c8d"))
        ax_mo.add_patch(patches.Rectangle((1.3, 8.0), 3.2, 0.15, color="#95a5a6"))
        hauteur_b = 3.5 * (1.0 - (st.session_state.v_verse / v_max_ml))
        ax_mo.add_patch(patches.Rectangle((3.6, 4.5), 0.6, 4.0, facecolor="none", edgecolor="#34495e", linewidth=2))
        ax_mo.add_patch(patches.Rectangle((3.62, 4.52), 0.56, hauteur_b, facecolor="#aed6f1", alpha=0.8))
        ax_mo.add_patch(patches.Rectangle((3.8, 4.1), 0.2, 0.4, color="#2c3e50"))
        hauteur_liq = 1.0 + 1.2 * (st.session_state.v_verse / v_max_ml)
        ax_mo.add_patch(patches.Polygon([[2.6, 1.0], [2.6, 3.2], [4.8, 3.2], [4.8, 1.0]], facecolor="none", edgecolor="#34495e", linewidth=3))
        ax_mo.add_patch(patches.Rectangle((2.65, 1.05), 2.1, hauteur_liq, facecolor=couleur_sol, alpha=0.75))
        ax_mo.add_patch(patches.Rectangle((2.2, 0.3), 3.0, 0.7, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=2))
        ax_mo.add_patch(patches.Rectangle((3.1, 1.1), 1.2, 0.15, facecolor="#ffffff", edgecolor="#7f8c8d"))
        ax_mo.add_patch(patches.Rectangle((4.3, 1.6), 0.3, 3.0, color="#34495e"))
        ax_mo.plot([4.45, 4.45, 5.5], [4.6, 7.5, 7.5], color="#34495e", linewidth=2)
        ax_mo.add_patch(patches.Rectangle((5.5, 6.5), 2.2, 1.5, facecolor="#2c3e50", edgecolor="#1a252f", linewidth=2))
        ax_mo.text(6.6, 7.2, f"pH: {ph_actuel:.2f}", color="#2ecc71", fontfamily="monospace", weight="bold", fontsize=11, ha="center")
        ax_mo.text(3.7, 0.05, f"Teinte : {nom_teinte}", color="#1e293b", fontsize=9, ha="center")
        ax_mo.set_xlim(0.5, 8.0)
        ax_mo.set_ylim(0.0, 9.5)
        ax_mo.axis("off")

        with conteneur_paillasse_animee.container():
            c_v, c_g = st.columns([1, 1.2])
            with c_v: 
                st.pyplot(fig_m)
                plt.close(fig_m)
            with c_g:
                with st.container(border=True):
                    st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>VALEURS RELEVEES DU DOSAGE</p>", unsafe_allow_html=True)
                    st.text(f"• Volume equivalent V_eq = {v_eq_theorique:.2f} mL\n• pH a l'equivalence pH_eq = {ph_eq_theorique:.2f}")

                # --- 1. GRAPHIQUE PRINCIPAL : COURBE DE pH ET TANGENTES ---
                fig_c, ax_cr = plt.subplots(figsize=(4.5, 3.5))
                ax_cr.axhspan(0, ind_data["ph_min"], facecolor=ind_data["couleur_acide"], alpha=0.15, zorder=0)
                ax_cr.axhspan(ind_data["ph_min"], ind_data["ph_max"], facecolor=ind_data["couleur_zone"], alpha=0.20, zorder=0)
                ax_cr.axhspan(ind_data["ph_max"], 14, facecolor=ind_data["couleur_base"], alpha=0.15, zorder=0)
                
                ax_cr.plot(volumes_simules[:idx_actuel+1], phs_simules[:idx_actuel+1], color="black", linewidth=2.0)
                ax_cr.scatter([st.session_state.v_verse], [ph_actuel], color="red", s=60, zorder=5)
                
                v_sim_np = np.array(volumes_simules)
                ph_sim_np = np.array(phs_simules)
                
                # Appel de votre def pour les tangentes uniquement
                appliquer_analyse_geometrique_courbe(
                    ax_cr, v_sim_np, ph_sim_np, idx_actuel,
                    v_eq_theorique, ph_eq_theorique, v_max_ml,
                    chk_tangentes=st.session_state.chk_tangentes_at2_stable
                )

                ax_cr.set_xlim(0, v_max_ml + 1)
                ax_cr.set_ylim(0, 14)
                ax_cr.set_xlabel("Volume de soude verse V_B (mL)", fontsize=9)
                ax_cr.set_ylabel("pH", fontsize=9)
                ax_cr.grid(True, linestyle=":")
                st.pyplot(fig_c)
                plt.close(fig_c)

            st.write("---")
            st.subheader("Tableau de suivi (3 lignes - Colonnes multiples)")
            matrice_f = {}
            for i_f in range(idx_actuel + 1):
                v_p = volumes_simules[i_f]
                ph_p = phs_simules[i_f]
                obs_p = ind_data["nom_acide"] if ph_p < ind_data["ph_min"] else (ind_data["nom_base"] if ph_p > ind_data["ph_max"] else ind_data["nom_zone"])
                matrice_f[f"Goutte {i_f}"] = {"Soude versee V_B (mL)": f"{v_p:.1f}", "pH mesure": f"{ph_p:.2f}", "Observations / Teinte": obs_p}
            import pandas as pd
            st.dataframe(pd.DataFrame.from_dict(matrice_f, orient="index").T, use_container_width=True)
        plt.close(fig_m)
    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 2")

    # Calculs automatiques des veritables attendus pour la correction automatique du bouton
    v_acide_dose = 10.0
    n_soude_equiv = (C_base * v_eq_theorique) / 1000.0
    c_vinaigre_dose_attendu = (C_base * v_eq_theorique) / v_acide_dose

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)

    # Execution propre de l'affichage bicolonne defini dans votre fonction prof
    if not st.session_state.get("animation_active", False):
        try:
            # Appel dynamique de votre def prof existante
            generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_vin2)
        except NameError:
            # Securite si votre def porte encore l'ancien nom dans votre fichier
            afficher_questions_titrage_dynamiques(df_donnees=None, verrouille=verrou_vin2)
    else:
        st.info("Le versement de la soude est en cours... Le formulaire d'evaluation s'affichera des que l'animation sera terminee.")

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    
    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin2 = st.checkbox("Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.", key="check_certif_vin2_net", disabled=verrou_vin2)


    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        # CAPTURE ET ENCODAGE DE LA COURBE AVEC SES LOGICIELS ET POINT MOBILE
        import io
        import base64
        fig_rep, ax_rp = plt.subplots(figsize=(5, 3.8))
        ax_rp.axhspan(0, ind_data["ph_min"], facecolor=ind_data["couleur_acide"], alpha=0.15, zorder=0)
        ax_rp.axhspan(ind_data["ph_min"], ind_data["ph_max"], facecolor=ind_data["couleur_zone"], alpha=0.20, zorder=0)
        ax_rp.axhspan(ind_data["ph_max"], 14, facecolor=ind_data["couleur_base"], alpha=0.15, zorder=0)
        ax_rp.plot(volumes_simules[:idx_actuel+1], phs_simules[:idx_actuel+1], color="black", linewidth=2.0)
        ax_rp.scatter([st.session_state.v_verse], [ph_actuel], color="red", s=60, zorder=5)
        
        v_l_el = st.session_state.get("vin_ve_lu_at2", 0.0)
        ph_l_el = st.session_state.get("vin_phe_lu_at2", 0.0)
        if v_l_el > 0.0:
            ax_rp.scatter([v_l_el], [ph_l_el], color="#1e3a8a", s=120, edgecolor="white", linewidths=1.5, zorder=7)
            ax_rp.plot([v_l_el, v_l_el], [0, ph_l_el], color="#1e3a8a", linestyle=":", lw=1.2)
            ax_rp.plot([0, v_l_el], [ph_l_el, ph_l_el], color="#1e3a8a", linestyle=":", lw=1.2)

        if st.session_state.get("chk_tangentes_at2_net", False):
            v_np = np.array(volumes_simules)
            ph_np = np.array(phs_simules)
            idx_av = np.where(v_np <= max(0.5, v_eq_theorique - 4.0))
            idx_ap = np.where((v_np >= min(v_max_ml, v_eq_theorique + 4.0)) & (v_np <= v_max_ml - 1.0))
            if len(idx_av) > 1 and len(idx_ap) > 1:
                pente_av = (ph_np[idx_av[-1]] - ph_np[idx_av]) / (v_np[idx_av[-1]] - v_np[idx_av]) if (v_np[idx_av[-1]] - v_np[idx_av]) != 0 else 0.1
                pente_ap = (ph_np[idx_ap[-1]] - ph_np[idx_ap]) / (v_np[idx_ap[-1]] - v_np[idx_ap]) if (v_np[idx_ap[-1]] - v_np[idx_ap]) != 0 else 0.1
                pente_c = (pente_av + pente_ap) / 2.0
                b1 = ph_np[idx_av[-1]] - pente_c * v_np[idx_av[-1]]
                b2 = ph_np[idx_ap] - pente_c * v_np[idx_ap]
                b_med = (b1 + b2) / 2.0
                v_tr = np.linspace(0, v_max_ml, 200)
                ax_rp.plot(v_tr, pente_c * v_tr + b1, color="black", linestyle="-", lw=1.0, alpha=0.6)
                ax_rp.plot(v_tr, pente_c * v_tr + b2, color="black", linestyle="-", lw=1.0, alpha=0.6)
                ax_rp.plot(v_tr, pente_c * v_tr + b_med, color="black", linestyle="-", lw=1.2)
            ax_rp.axvline(x=v_eq_theorique, color="blue", linestyle="--", lw=1.2)
            ax_rp.scatter([v_eq_theorique], [ph_eq_theorique], color="blue", marker="+", s=150, linewidths=2.5, zorder=6)

        ax_rp.set_xlim(0, v_max_ml + 1)
        ax_rp.set_ylim(0, 14)
        ax_rp.grid(True, linestyle=":")
        
        tampon_memoire = io.BytesIO()
        fig_rep.savefig(tampon_memoire, format="png", bbox_inches="tight")
        tampon_memoire.seek(0)
        base64_image_courbe = base64.b64encode(tampon_memoire.read()).decode("utf-8")
        plt.close(fig_rep)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin2 = st.checkbox("Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.", key="check_certif_vin2_final_net", disabled=verrou_vin2)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_vin2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz Numérique de gauche (6 questions)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_vin_q1_tab2") == f"{c_base_session:.2f} mol/L",
                st.session_state.get("col_g_quiz_vin_q2_tab2") == f"{v_acide_dosé:.1f} mL",
                st.session_state.get("col_g_quiz_vin_q3_tab2") == f"{v_eq_attendu:.2f} mL",
                st.session_state.get("col_g_quiz_vin_q4_tab2") == "Ca * Va = Cb * Ve",
                st.session_state.get("col_g_quiz_vin_q5_tab2") == f"{n_soude_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_vin_q6_tab2") == f"{c_vinaigre_dose_attendu:.3f} mol/L"
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

        # GENERATION DE LA COURBE EN ARRIÈRE-PLAN POUR L'INJECTION HTML (BASE64)
        import io
        import base64
        buf = io.BytesIO()
        fig_c.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        base64_courbe_at2 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

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

            <div class="sub-title">SAUVEGARDE GÉOMÉTRIQUE DE VOTRE COURBE EXPERIMENTALE</div>
            <div class="img-container">
                <img src="data:image/png;base64,{base64_courbe_at2}" alt="Courbe de suivi eleve">
            </div>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        attendus_quiz2 = [f"{c_base_session:.2f} mol/L", f"{v_acide_dosé:.1f} mL", f"{v_eq_attendu:.2f} mL", "Ca * Va = Cb * Ve", f"{n_soude_equiv:.5f} mol", f"{c_vinaigre_dose_attendu:.3f} mol/L"]
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

    st.write("---")

    # Moteur de calcul théorique de référence pour la correction sur 20 points
    v_eq_litre_ref = v_eq_session / 1000.0
    n_soude_equiv_ref = c_base_session * v_eq_litre_ref
    n_acide_becher_ref = n_soude_equiv_ref
    c_acide_fille_ref = n_acide_becher_ref / (v_titre_session / 1000.0)
    m_acide_becher_ref = n_acide_becher_ref * M_vinaigre
    m_acide_becher_mg_ref = m_acide_becher_ref * 1000.0
    c_massique_fille_ref = c_acide_fille_ref * M_vinaigre
    c_massique_fille_mg_ref = c_massique_fille_ref * 1000.0

    n_acide_fiole_ref = c_acide_fille_ref * (V_fiole / 1000.0)
    n_acide_bouteille_ref = n_acide_fiole_ref * facteur_dilution
    c_acide_mere_ref = c_acide_fille_ref * facteur_dilution
    m_acide_bouteille_ref = n_acide_bouteille_ref * M_vinaigre
    m_acide_bouteille_mg_ref = m_acide_bouteille_ref * 1000.0
    c_massique_mere_ref = c_acide_mere_ref * M_vinaigre
    c_massique_mere_mg_ref = c_massique_mere_ref * 1000.0
    degre_calcule_ref = c_massique_mere_ref / 10.0

    verrou_vin3 = st.session_state.vin_verrouille_tab3

    # Appel de votre fonction professeur existante contenant l'affichage des deux blocs colorés
    try:
        afficher_questions_bouteille_commerciale(verrouille=verrou_vin3)
    except NameError:
        st.error("La fonction 'afficher_questions_bouteille_commerciale' n'a pas ete trouvee au sommet de votre script.")

    # --- SÉCURITÉ DE NOTATION DE L'ATELIER 3 ---
    case_certif_vin3 = st.checkbox("Je certifie avoir complete l'integralite des calculs de l'Atelier 3.", key="check_certif_vin3_net", disabled=verrou_vin3)

    v_eq_litre_ref = v_eq_session / 1000.0
    n_soude_equiv_ref = c_base_session * v_eq_litre_ref
    n_acide_becher_ref = n_soude_equiv_ref
    c_acide_fille_ref = n_acide_becher_ref / (v_titre_session / 1000.0)
    m_acide_becher_ref = n_acide_becher_ref * M_vinaigre
    m_acide_becher_mg_ref = m_acide_becher_ref * 1000.0
    c_massique_fille_ref = c_acide_fille_ref * M_vinaigre
    c_massique_fille_mg_ref = c_massique_fille_ref * 1000.0

    n_acide_fiole_ref = c_acide_fille_ref * (V_fiole / 1000.0)
    n_acide_bouteille_ref = n_acide_fiole_ref * facteur_dilution
    c_acide_mere_ref = c_acide_fille_ref * facteur_dilution
    m_acide_bouteille_ref = n_acide_bouteille_ref * M_vinaigre
    m_acide_bouteille_mg_ref = m_acide_bouteille_ref * 1000.0
    c_massique_mere_ref = c_acide_mere_ref * M_vinaigre
    degre_bouteille_ref = c_massique_mere_ref / 10.0

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin3 = st.checkbox("Je certifie avoir complete l'integralite des calculs de l'Atelier 3.", key="check_certif_vin3_net", disabled=verrou_vin3)

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
                    <tr><td>Quantite de matiere dans la bouteille (mol)</td><td>{st.session_state.get("at3_n_acide_bouteille", 0.0):.5f}</td><td>{n_acide_bouteille_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - n_acide_bouteille_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - n_acide_bouteille_ref) < 0.001 else "INCORRECT"}</td></tr>
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









