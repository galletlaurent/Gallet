# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de l'indice d'acide d'une huile ",
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
st.title("Application dosage de l'indice d'acide d'une huile")
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
if "th_vrai_veq_calc" not in st.session_state:
    st.session_state.th_vrai_veq_calc = 12.0
if "input_at2_ve_lu_eleve" not in st.session_state:
    st.session_state.input_at2_ve_lu_eleve = 12.0
if "v_verse_ox" not in st.session_state:
    st.session_state.v_verse_ox = 0.0
if "pas_ml" not in st.session_state:
    st.session_state.pas_ml = 0.5
if "masse_reelle_g" not in st.session_state:
    st.session_state.masse_reelle_g = 0.0

if "facteur_titrage_ox" not in st.session_state:
    import random
    st.session_state.facteur_titrage_ox = random.uniform(0.95, 1.05)

# Fixation stricte de la solution titrante d'hydroxyde de potassium (Potasse KOH)
if "c_titrant_thiosulfate" not in st.session_state:
    st.session_state.c_titrant_thiosulfate = 0.100

# Cartographie officielle des teintes de l'huile de lubrification (Indicateur : Phénolphtaléine)
if "teintes_iodometrie" not in st.session_state:
    st.session_state.teintes_iodometrie = {
        "Avant equivalence": {
            "couleur_hex": "#b45309",
            "nom_aspect": "Ambree sombre (Huile de vidange en solvant)"
        },
        "Zone sensible": {
            "couleur_hex": "#cb5a43",
            "nom_aspect": "Teinte sensible brune-rosee (Proche equivalence)"
        },
        "Apres equivalence": {
            "couleur_hex": "#be123c",
            "nom_aspect": "Rose-orange opaque fonce (Hydroxyde de potassium en exces)"
        }
    }
if "eau" not in st.session_state:
    st.session_state["eau"] = {
        "Huile moteur usagée : Vidange véhicule essence (Indice élevé)": {"tan": 3.8},
        "Huile de boîte de vitesses : Transmission intensive (Indice critique)": {"tan": 5.4},
        "Huile moteur neuve : Synthèse 5W30 de référence (Témoin conforme)": {"tan": 0.5},
        "Huile hydraulique : Circuit haute pression échauffé (Indice modéré)": {"tan": 2.2}
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
    "Généralités sur l'huile",
    "Dosage de l'indice d'acide",
    "Calcul théorique et vérification du lubrifiant"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

def afficher_questions_bouteille_commerciale(verrouille=False):
    import numpy as np
    import streamlit as st

    # Récupération des données de session calculées au préalable pour la potasse et l'huile
    C_base = st.session_state.get("c_titrant_thiosulfate", 0.100)
    v_eq_theorique = st.session_state.get("vin_vrai_veq_calc", 12.0)
    masse_huile_dosee = 5.00  
    M_koh = 56.11  

    st.markdown("""
        <style>
        .bloc-bleu-at3 { background-color: #e0f2fe; padding: 15px; border-radius: 4px; border-left: 5px solid #0284c7; margin-bottom: 20px; }
        .bloc-jaune-at3 { background-color: #fefce8; padding: 15px; border-radius: 4px; border-left: 5px solid #ca8a04; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    dict_reponses_bouteille = {}

    # --- BLOC BLEU : EXPLOITATION DU DOSAGE DANS LE BÉCHER ---
    st.markdown('<div class="bloc-bleu-at3">', unsafe_allow_html=True)
    st.markdown("<p style='margin-top:0; font-weight:bold; color:#0284c7;'>EXPLOITATION DE LA NEUTRALISATION DANS LE BECHER</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c1: st.write("1. Convertir le volume équivalent de potasse relevé $V_E$ en litre (L) :")
    with c2: dict_reponses_bouteille["v_eq_l"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_v_eq_l", disabled=verrouille, label_visibility="collapsed")

    c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c3: st.write("2. Calculer la quantité de matière d'ions hydroxyde $HO^-$ versée à l'équivalence (mol) :")
    with c4: dict_reponses_bouteille["n_soude"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_soude", disabled=verrouille, label_visibility="collapsed")

    c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c5: st.write("3. En déduire la quantité de matière d'acibles organiques libres neutralisés dans le bécher (mol) :")
    with c6: dict_reponses_bouteille["n_acide_becher"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide_becher", disabled=verrouille, label_visibility="collapsed")

    c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c7: st.write("4. En déduire la quantité d'acides organiques libres par gramme d'huile analysé (mol/g) :")
    with c8: dict_reponses_bouteille["c_molaire_fille"] = st.number_input("", min_value=0.000000, max_value=10.000000, format="%.6f", key="at3_c_molaire_fille", disabled=verrouille, label_visibility="collapsed")

    c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c9: st.write("5. Calculer la masse équivalente d'hydroxyde de potassium (KOH) consommée en gramme (g) :")
    with c10: dict_reponses_bouteille["m_acide_gramme"] = st.number_input("", min_value=0.0000, max_value=100.0000, format="%.4f", key="at3_m_acide_gramme", disabled=verrouille, label_visibility="collapsed")

    c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c11: st.write("6. En déduire la masse équivalente de KOH consommée pour l'essai en milligramme (mg) :")
    with c12: dict_reponses_bouteille["m_acide_mg"] = st.number_input("", min_value=0.0, max_value=10000.0, format="%.1f", key="at3_m_acide_mg", disabled=verrouille, label_visibility="collapsed")

    c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c13: st.write("7. Calculer le titre massique en KOH par rapport à la masse totale de potasse (g/L équivalent) :")
    with c14: dict_reponses_bouteille["c_massique_fille"] = st.number_input("", min_value=0.00, max_value=500.00, format="%.5f", key="at3_c_massique_fille", disabled=verrouille, label_visibility="collapsed")

    c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c15: st.write("8. Convertir ce titre massique équivalent du fluide en mg/L :")
    with c16: dict_reponses_bouteille["c_massique_fille_mg"] = st.number_input("", min_value=0.0, max_value=500000.0, format="%.1f", key="at3_c_massique_fille_mg", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOC JAUNE : DETERMINATION DE L'INDICE D'ACIDE ET DIAGNOSTIC ---
    st.markdown('<div class="bloc-jaune-at3">', unsafe_allow_html=True)
    st.markdown("<p style='margin-top:0; font-weight:bold; color:#ca8a04;'>DETERMINATION DE L'INDICE D'ACIDE TOTAL (TAN) ET DIAGNOSTIC MOTEUR</p>", unsafe_allow_html=True)

    c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c17: st.write("9. Donner la masse de la prise d'essai d'huile de vidange introduite (g) :")
    with c18: dict_reponses_bouteille["rapport_dilution"] = st.number_input("", min_value=0.0, max_value=1000.0, format="%.2f", key="at3_rapport_dilution", disabled=verrouille, label_visibility="collapsed")

    c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c19: st.write("10. Rappeler la quantité de matière totale d'acides organiques présents dans l'essai (mol) :")
    with c20: dict_reponses_bouteille["n_acide_fiole"] = st.number_input("", min_value=0.00000, max_value=1.00000, format="%.5f", key="at3_n_acide_fiole", disabled=verrouille, label_visibility="collapsed")

    c21, c22 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c21: st.write("11. Confirmer la masse totale de KOH nécessaire à la neutralisation de cet essai (mg) :")
    with c22: dict_reponses_bouteille["n_acide_bouteille"] = st.number_input("", min_value=0.0, max_value=5000.0, format="%.2f", key="at3_n_acide_bouteille", disabled=verrouille, label_visibility="collapsed")

    c23, c24 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c23: st.write("12. Calculer le nombre de milligrammes de KOH requis pour neutraliser un seul gramme d'huile :")
    with c24: dict_reponses_bouteille["c_molaire_mere"] = st.number_input("", min_value=0.00, max_value=20.00, format="%.2f", key="at3_c_molaire_mere", disabled=verrouille, label_visibility="collapsed")

    c25, c26 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c25: st.write("13. En déduire la valeur numérique finale de l'indice d'acide TAN expérimental (mg/g) :")
    with c26: dict_reponses_bouteille["m_mere_gramme"] = st.number_input("", min_value=0.0, max_value=1000.0, format="%.2f", key="at3_m_mere_gramme", disabled=verrouille, label_visibility="collapsed")

    c27, c28 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c27: st.write("14. Calculer la masse totale de potasse nécessaire pour traiter un kilogramme de ce lubrifiant (g) :")
    with c28: dict_reponses_bouteille["m_mere_mg"] = st.number_input("", min_value=0.0, max_value=1000000.0, format="%.2f", key="at3_m_mere_mg", disabled=verrouille, label_visibility="collapsed")

    c29, c30 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c29: st.write("15. Indiquer la valeur limite critique du TAN pour ce type de fluide avant usure sévère (mg/g) :")
    with c30: dict_reponses_bouteille["c_massique_mere"] = st.number_input("", min_value=0.0, max_value=1000.0, format="%.2f", key="at3_c_massique_mere", disabled=verrouille, label_visibility="collapsed")

    c31, c32 = st.columns([0.70, 0.30], vertical_alignment="bottom")
    with c31: st.write("16. En déduire la masse équivalente de KOH de référence calculée par gramme d'huile liquide :")
    with c32: dict_reponses_bouteille["c_massique_mere_mg"] = st.number_input("", min_value=0.0, max_value=1000000.0, format="%.2f", key="at3_c_massique_mere_mg", disabled=verrouille, label_visibility="collapsed")

    c33, c34 = st.columns([0.55, 0.45], vertical_alignment="bottom")
    with c33: st.write("17. Établir le diagnostic de maintenance pour l'échantillon choisi :")
    with c34: dict_reponses_bouteille["conclusion_bouteille"] = st.selectbox("", ["Choisir...", "L'huile est conforme à l'étiquette", "L'huile n'est pas conforme"], key="at3_conclusion_bouteille", disabled=verrouille, label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)
    return dict_reponses_bouteille

def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    v_eq_attendu = st.session_state.get("th_vrai_veq_calc", 12.0)
    c_base_session = 0.10
    masse_huile_dosee = 5.00 

    # Récupération dynamique liée à la masse aléatoire de session
    n_potasse_equiv = (c_base_session * v_eq_attendu) / 1000.0
    moles_acide_par_g_huile = n_potasse_equiv / masse_huile_dosee

    col_double_quiz_huile, col_double_trous_huile = st.columns(2)

    with col_double_quiz_huile:
        st.markdown("##### Quiz numérique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        # --- QUESTION 1 ---
        opts_q1 = ["Choisir...", f"{c_base_session:.2f} mol/L", "1.00 mol/L", "0.50 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante d'hydroxyde de potassium ($C_0$) utilisée ?")
        val_q1 = st.session_state.get("col_g_quiz_vin_q1_tab2", "Choisir...")
        try: idx_q1 = opts_q1.index(val_q1)
        except ValueError: idx_q1 = 0
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, index=idx_q1, key="col_g_quiz_vin_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 2 ---
        opts_q2 = ["Choisir...", f"{masse_huile_dosee:.2f} g", "1.00 g", "10.00 g"]
        st.write("**2.** Quelle masse d'échantillon d'huile de vidange ($m$) a été introduite dans le bécher ?")
        val_q2 = st.session_state.get("col_g_quiz_vin_q2_tab2", "Choisir...")
        try: idx_q2 = opts_q2.index(val_q2)
        except ValueError: idx_q2 = 0
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, index=idx_q2, key="col_g_quiz_vin_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 3 ---
        opts_q3 = ["Choisir...", f"{v_eq_attendu:.2f} mL", "10.00 mL", "15.00 mL"]
        st.write("**3.** Quel est le volume équivalent exact ($V_E$) de solution de potasse versé relevé au virage de teinte ?")
        val_q3 = st.session_state.get("col_g_quiz_vin_q3_tab2", "Choisir...")
        try: idx_q3 = opts_q3.index(val_q3)
        except ValueError: idx_q3 = 0
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, index=idx_q3, key="col_g_quiz_vin_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 4 ---
        opts_q4 = ["Choisir...", "n(KOH) = n(Acide)", "n(KOH) = 2 * n(Acide)", "2 * n(KOH) = n(Acide)"]
        st.write("**4.** Quelle est la relation stœchiométrique établie à l'équivalence pour ce titrage direct ?")
        val_q4 = st.session_state.get("col_g_quiz_vin_q4_tab2", "Choisir...")
        try: idx_q4 = opts_q4.index(val_q4)
        except ValueError: idx_q4 = 0
        dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, index=idx_q4, key="col_g_quiz_vin_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 5 ---
        opts_q5 = ["Choisir...", f"{n_potasse_equiv:.5f} mol", f"{n_potasse_equiv * 10:.5f} mol", "0.00100 mol"]
        st.write("**5.** Quelle quantité de matière d'ions hydroxyde $HO^-$ a été apportée à l'équivalence ?")
        val_q5 = st.session_state.get("col_g_quiz_vin_q5_tab2", "Choisir...")
        try: idx_q5 = opts_q5.index(val_q5)
        except ValueError: idx_q5 = 0
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, index=idx_q5, key="col_g_quiz_vin_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        # --- QUESTION 6 ---
        opts_q6 = ["Choisir...", f"{moles_acide_par_g_huile:.6f} mol/g", "0.010000 mol/g", "0.100000 mol/g"]
        st.write("**6.** Déduisez-en la quantité d'acide libre par gramme d'huile dosé dans le bécher :")
        val_q6 = st.session_state.get("col_g_quiz_vin_q6_tab2", "Choisir...")
        try: idx_q6 = opts_q6.index(val_q6)
        except ValueError: idx_q6 = 0
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, index=idx_q6, key="col_g_quiz_vin_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_huile:
        st.markdown("##### Synthèse de cours (Texte à trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        opts_t1 = ["Choisir...", "Burette", "Eprouvette graduée", "Pipette graduee"]
        st.write("1. La verrerie graduée utilisée pour verser la solution titrante de potasse est la")
        val_t1 = st.session_state.get("vin_t1_tab2", "Choisir...")
        try: idx_t1 = opts_t1.index(val_t1)
        except ValueError: idx_t1 = 0
        dict_trous["t1"] = st.selectbox("", opts_t1, index=idx_t1, key="vin_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_t2 = ["Choisir...", "Balance analytique", "Eprouvette graduée", "Pipette jaugée"]
        st.write("2. Pour introduire précisément les 5,00 g de fluide mécanique glissant, on utilise une")
        val_t2 = st.session_state.get("vin_t2_tab2", "Choisir...")
        try: idx_t2 = opts_t2.index(val_t2)
        except ValueError: idx_t2 = 0
        dict_trous["t2"] = st.selectbox("", opts_t2, index=idx_t2, key="vin_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_t3 = ["Choisir...", "diviser par 1000", "multiplier par 1000", "diviser par 10", "multiplier par 10"]
        st.write("3. Pour convertir le volume équivalent expérimental de mL en Litres, on doit le")
        val_t3 = st.session_state.get("vin_t3_tab2", "Choisir...")
        try: idx_t3 = opts_t3.index(val_t3)
        except ValueError: idx_t3 = 0
        dict_trous["t3"] = st.selectbox("", opts_t3, index=idx_t3, key="vin_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_t4 = ["Choisir...", "stoechiometriques", "doubles", "inverses"]
        st.write("4. Au point équivalent, les ions hydroxyde et les molécules d'acides libres ont réagi dans des proportions")
        val_t4 = st.session_state.get("vin_t4_tab2", "Choisir...")
        try: idx_t4 = opts_t4.index(val_t4)
        except ValueError: idx_t4 = 0
        dict_trous["t4"] = st.selectbox("", opts_t4, index=idx_t4, key="vin_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_t5 = ["Choisir...", "Au changement de couleur persistant", "Au saut de pH", "Au changement de couleur de la burette"]
        st.write("5. Lors d'un titrage de fluide mécanique en présence de phénolphtaléine, l'équivalence est obtenue")
        val_t5 = st.session_state.get("vin_t5_tab2", "Choisir...")
        try: idx_t5 = opts_t5.index(val_t5)
        except ValueError: idx_t5 = 0
        dict_trous["t5"] = st.selectbox("", opts_t5, index=idx_t5, key="vin_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_huile1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_huile" not in st.session_state:
        base_quiz1_huile = [
            {"id": "q1_1", "q": "L'oxydation d'une huile moteur en service génère des composés aux propriétés :", "type": "menu", "options": ["acides", "neutres", "basiques"], "rep": "acides"},
            {"id": "q1_2", "q": "Calculez la masse molaire moléculaire de l'hydroxyde de potassium KOH en g/mol :", "type": "menu", "options": ["56,1", "39,1", "74,6"], "rep": "56,1"},
            {"id": "q1_3", "q": "Que signifie le sigle TAN utilisé pour qualifier l'usure chimique d'un lubrifiant ?", "type": "menu", "options": ["Total Acid Number", "Total Alkali Number", "Thermal Acid Neutralizer"], "rep": "Total Acid Number"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes de potassium (K) dans une formule unitaire de potasse KOH ?", "type": "menu", "options": ["1", "2", "3"], "rep": "1"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'oxygène (O) dans une fonction carboxylique libre R-COOH ?", "type": "menu", "options": ["2", "1", "3"], "rep": "2"},
            {"id": "q1_6", "q": "L'indice d'acide TAN exprime la masse de KOH nécessaire pour neutraliser quel échantillon d'huile ?", "type": "menu", "options": ["1 gramme d'huile", "1 litre d'huile", "100 grammes d'huile"], "rep": "1 gramme d'huile"},
            {"id": "q1_7", "q": "Quelle est la formule chimique brute de la potasse utilisée comme solution titrante ?", "type": "menu", "options": ["KOH", "NaOH", "HCl"], "rep": "KOH"},
            {"id": "q1_8", "q": "D'après la légende atomique, quelle est la masse molaire de l'élément Potassium (K) ?", "type": "menu", "options": ["39,1 g/mol", "12,0 g/mol", "16,0 g/mol"], "rep": "39,1 g/mol"},
            {"id": "q1_9", "q": "D'après la légende atomique, quelle est la masse molaire de l'élément Oxygène (O) ?", "type": "menu", "options": ["16,0 g/mol", "1,0 g/mol", "39,1 g/mol"], "rep": "16,0 g/mol"},
            {"id": "q1_10", "q": "D'après la légende atomique, la sphère blanche représente l'atome d' :", "type": "menu", "options": ["Hydrogène (H)", "Potassium (K)", "Oxygène (O)"], "rep": "Hydrogène (H)"}
        ]
        copie_base = list(base_quiz1_huile)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_huile = copie_base

    col_double_quiz_h1, col_double_trous_h1 = st.columns(2)

    with col_double_quiz_h1:
        st.markdown("##### Quiz de nomenclature moléculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_huile, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vin_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_huile_{q_data['id']}"
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

    with col_double_trous_h1:
        st.markdown("##### Synthèse des propriétés des lubrifiants (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le vieillissement thermique d'un lubrifiant en service provoque une réaction d'")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Oxydation", "Hydrolyse"], key="vin_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'indice d'acide TAN quantifie la masse en milligrammes requise de")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Potasse", "Soude", "Acide"], key="vin_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La réaction de neutralisation mise en jeu entre HO- et les acides libres est une réaction")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Acido-basique", "D'oxydoréduction"], key="vin_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c47, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c47: st.write("4. La fin de la réaction sur l'huile ambrée est caractérisée par une coloration")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Brune-rosée", "Bleu-violet", "Jaune vif"], key="vin_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La masse de l'échantillon de fluide mécanique pesée pour le dosage vaut m =")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "5,00 g", "1,00 g", "10,0 g"], key="vin_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'espèce chimique titrante employée dans la burette graduée est l'hydroxyde de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Potassium", "Sodium", "Calcium"], key="vin_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La solution de potasse introduite apporte des ions basiques réactifs de formule")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "HO-", "K+", "Cl-"], key="vin_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. L'indicateur coloré acido-basique ajouté au départ dans le solvant est la")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Phénolphtaléine", "Murexide", "Hélianthine"], key="vin_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le changement de couleur persistant de l'indicateur signale le point d'")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Equivalence", "Saturabilité"], key="vin_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Un indice TAN qui augmente fortement indique un lubrifiant devenu")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Corrosif", "Lubrifiant", "Inerte"], key="vin_t10_s1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Atelier 1 : Généralités sur l'acidité des lubrifiants")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    col_gauche, col_droite = st.columns([1, 1])
    
    # =========================================================================
    # COLONNE GAUCHE : LE DOCUMENT ET LE BIDON D'HUILE GRAPHISME MECANIQUE
    # =========================================================================
    with col_gauche:
        st.subheader("Document d'étude")
        
        texte_document = (
            "Au cours du cycle de vie d'un moteur thermique, l'huile de lubrification subit d'extrêmes contraintes "
            "thermiques, mécaniques et des pollutions par les gaz de combustion. Ce vieillissement induit un phénomène "
            "d'oxydation de sa matrice d'hydrocarbures, générant des acides organiques libres corrosifs. "
            "L'indice d'acide, ou TAN (Total Acid Number), quantifie cet état d'usure en représentant la masse d'hydroxyde "
            "de potassium (KOH), exprimée en milligrammes (mg), nécessaire pour neutraliser les composés acides libres "
            "présents dans un gramme de fluide. Un indice qui s'élève de manière excessive indique une dégradation sévère "
            "du lubrifiant, risquant d'endommager les pièces mécaniques (coussinets de bielle) par corrosion. "
            "Le dosage s'effectue en dissolvant une prise d'essai d'huile de vidange dans un solvant approprié, suivi "
            "d'un titrage acido-basique direct par une solution d'hydroxyde de potassium (potasse)."
        )
        st.info(texte_document)
        
        # Rendu graphique du bidon d'huile moteur en 2D via Matplotlib
        fig_bouteille, ax = plt.subplots(figsize=(4, 5.2), facecolor="#bae6fd")
        ax.set_facecolor("#bae6fd")
        
        bouchon = patches.Rectangle((4, 8.5), 2, 0.8, color="#ef4444", ec="#94a3b8")
        col = patches.Polygon([[4.2, 8.5], [5.8, 8.5], [6.5, 7], [3.5, 7]], color="#1e293b", ec="#334155")
        corps = patches.Rectangle((2.5, 1), 5, 6, color="#1e293b", ec="#334155")
        etiquette = patches.Rectangle((2.7, 1.5), 4.6, 4, color="#0f172a")
        logo_fond = patches.Rectangle((4.2, 2.2), 1.6, 1.2, color="#b45309")
        
        ax.add_patch(patches.Circle((5, 1), 2.5, color="#1e293b", ec="#1e293b"))
        ax.add_patch(corps)
        ax.add_patch(col)
        ax.add_patch(bouchon)
        ax.add_patch(etiquette)
        ax.add_patch(logo_fond)
        
        for y in np.linspace(1.2, 6.8, 8):
            ax.plot([2.55, 7.45], [y, y], color="#334155", linewidth=1)
            
        ax.text(5, 5.0, "HUILE MOTEUR", color="white", weight="bold", fontsize=14, ha="center")
        ax.text(5, 4.5, "SYNTHESE 5W30", color="#94a3b8", weight="bold", fontsize=10, ha="center")
        ax.text(5, 4.1, "LUBRIFIANT PRO", color="#94a3b8", weight="bold", fontsize=10, ha="center")
        ax.text(5, 3.0, "PERFORMANCE", color="white", weight="bold", fontsize=11, ha="center")
        ax.text(5, 2.5, "TAN TEST", color="#facc15", weight="bold", fontsize=11, ha="center")
        ax.text(3.3, 2.0, "15W40", color="white", weight="bold", fontsize=9, ha="center")
        ax.text(6.7, 2.0, "5 L", color="white", weight="bold", fontsize=11, ha="center")
        
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
        with col_leg1: st.caption("**Potassium (K)**\n\nSphère violette\nM(K) = 39,1 g/mol")
        with col_leg2: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16,0 g/mol")
        with col_leg3: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1,0 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # Coordonnées pour le motif d'acide carboxylique libre R-COOH (issu de l'oxydation de l'huile)
        c_acide = np.array([2.0, 3.2])
        o1_double = np.array([1.6, 4.2])
        o2_simple = np.array([3.2, 3.2])
        h_acide = np.array([4.0, 3.2])
        
        # Coordonnées pour l'ion hydroxyde HO- réactif (solution titrante de potasse)
        o_hydroxyde = np.array([2.2, 1.6])
        h_hydroxyde = np.array([3.6, 1.6])

        def tracer_liaison_huile(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Tracé des liaisons de la neutralisation acido-basique
        tracer_liaison_huile(c_acide, o1_double, double=True)
        tracer_liaison_huile(c_acide, o2_simple, double=False)
        tracer_liaison_huile(o2_simple, h_acide, double=False)
        tracer_liaison_huile(o_hydroxyde, h_hydroxyde, double=False)

        def tracer_atome_huile(p, symbole):
            if symbole == 'K': couleur, texte_couleur = "#a855f7", "white"
            elif symbole == 'O': couleur, texte_couleur = "#ef4444", "white"
            elif symbole == 'H': couleur, texte_couleur = "#f1f5f9", "black"
            elif symbole == 'C': couleur, texte_couleur = "#334155", "white"
            else: couleur, texte_couleur = "#94a3b8", "black"
            
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.24, facecolor=couleur, edgecolor="#0f172a", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # Rendu des motifs moléculaires
        tracer_atome_huile(c_acide, 'C')
        tracer_atome_huile(o1_double, 'O')
        tracer_atome_huile(o2_simple, 'O')
        tracer_atome_huile(h_acide, 'H')
        ax_mol.text(4.6, 3.2, "Acide libre R-COOH (Flui. usagé)", fontsize=9, style="italic", ha="left", va="center")

        tracer_atome_huile(o_hydroxyde, 'O')
        tracer_atome_huile(h_hydroxyde, 'H')
        ax_mol.text(4.6, 1.6, "Ion Hydroxyde HO⁻ (Titrante KOH)", fontsize=9, style="italic", ha="left", va="center")

        ax_mol.set_xlim(1.0, 6.8)
        ax_mol.set_ylim(0.8, 4.6)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()
        
    # =========================================================================
    # LOGIQUE DE COUPLAGE DES CONFIGURATIONS DE NOTATION DYNAMIQUES
    # =========================================================================
    verrou_huile_1 = st.session_state.get("vin_verrouille_tab1", False)

    # Appel de la fonction de questionnaire pour l'huile de vidange
    res_q1, res_t1 = afficher_questions_huile1_dynamiques(verrouille=verrou_huile_1)

    st.write("---")
    st.subheader("Généralités sur l'indice d'acide de l'huile")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_huile1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_huile1_official", 
        disabled=verrou_huile_1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_huile1_official_net", use_container_width=True, disabled=verrou_huile_1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_huile1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz de gauche mélangé (10 questions)
            score_q1 = 0.0
            if "ordre_quiz1_huile" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_huile:
                    reponse_eleve = st.session_state.get(f"vin_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 points)
            score_t1 = sum([
                st.session_state.get("vin_t1_s1") == "Oxydation",
                st.session_state.get("vin_t2_s1") == "Potasse",
                st.session_state.get("vin_t3_s1") == "Acido-basique",
                st.session_state.get("vin_t4_s1") == "Brune-rosée",
                st.session_state.get("vin_t5_s1") == "5,00 g",
                st.session_state.get("vin_t6_s1") == "Potassium",
                st.session_state.get("vin_t7_s1") == "HO-",
                st.session_state.get("vin_t8_s1") == "Phénolphtaléine",
                st.session_state.get("vin_t9_s1") == "Equivalence",
                st.session_state.get("vin_t10_s1") == "Corrosif"
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

        from datetime import datetime
        timestamp_huile1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER INDICE ACIDE 1 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_huile1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Acidité Huile 1 - {n_eleve}</title>
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
                <p>Atelier 1 : Généralités sur l'usure chimique et l'indice d'acide des huiles</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_huile1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de Nomenclature : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse des lubrifiants : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_huile" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_huile, 1):
                saisie = st.session_state.get(f"vin_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_huile1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_huile1 += """
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
            "1. Le vieillissement thermique d'un lubrifiant en service provoque une réaction d'",
            "2. L'indice d'acide TAN quantifie la masse en milligrammes requise de",
            "3. La réaction de neutralisation mise en jeu entre HO- et les acides libres ést une réaction",
            "4. La fin de la réaction sur l'huile ambrée est caractérisée par une coloration",
            "5. La masse de l'échantillon de fluide mécanique pesée pour le dosage vaut m =",
            "6. L'espèce chimique titrante employée dans la burette graduée est l'hydroxyde de",
            "7. La solution de potasse introduite apporte des ions basiques réactifs de formule",
            "8. L'indicateur coloré acido-basique ajouté au départ dans le solvant est la",
            "9. Le changement de couleur persistant de l'indicateur signale le point d'",
            "10. Un indice TAN qui augmente fortement indique un lubrifiant devenu"
        ]
        attendus_trous1 = ["Oxydoration", "Potasse", "Acido-basique", "Brune-rosée", "5,00 g", "Potassium", "HO-", "Phénolphtaléine", "Equivalence", "Corrosif"]
        
        for num in range(1, 11):
            saisie = st.session_state.get(f"vin_t{num}_s1", "Choisir...")
            attendu = attendus_trous1[num-1]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_huile1 += f"<tr><td>{num}</td><td>{phrases_trous1[num-1]}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_huile1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse de l'Atelier 1 généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Rapport_Atelier1_Huile_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_huile1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )







with tab2:
    st.header("Dosage colorimétrique de l'huile de vidange")
    st.caption("Simulation interactive et animée du titrage des acides libres par l'hydroxyde de potassium")

    if "vin_verrouille_tab2" not in st.session_state: 
        st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: 
        st.session_state.animation_active = False
    if "v_verse_ox" not in st.session_state: 
        st.session_state.v_verse_ox = 0.0
    if "pas_ml" not in st.session_state: 
        st.session_state.pas_ml = 0.5

    # Constantes physico-chimiques fixes du modèle mécanique (TAN)
    masse_huile_g = 5.00  
    v_max_ml = 25.0  
    M_koh = 56.11  

    # Récupération de la concentration officielle fixée dans l'initialisation de session (0,100 mol/L)
    C_base = st.session_state.get("c_titrant_thiosulfate", 0.100)

    # Récupération adaptative du TAN nominal de la bouteille d'huile sélectionnée
    liste_bouteilles = list(st.session_state["eau"].keys())
    bouteille_selectionnee = st.selectbox(
        "Sélectionnez l'huile moteur à analyser :", 
        options=liste_bouteilles, 
        disabled=st.session_state.vin_verrouille_tab2,
        key="select_bouteille_huile_tab2"
    )

    info_bouteille = st.session_state["eau"][bouteille_selectionnee]
    tan_nominal = info_bouteille["tan"]

    coeff_alea = st.session_state.get("facteur_titrage_ox", 1.0)

    # RECALCUL ALÉATOIRE SÉCURISÉ POUR DÉTERMINER LA PROPRIÉTÉ DE L'HUILE
    V_molaire_gaz = 22.4  
    
    # Votre formule de simulation qui s'exécute maintenant parfaitement
    c_clo_simulee = (tan_nominal / V_molaire_gaz / 10.0) * coeff_alea
    
    # Fixation de la masse réelle d'acides organiques en grammes
    st.session_state.masse_reelle_g = c_clo_simulee * (masse_huile_g / 1000.0) * M_koh
    masse_affichee_mg = st.session_state.masse_reelle_g * 1000.0

    # Liaison mathématique directe pour que le volume équivalent s'adapte à cette masse unique
    moles_acide_becher = st.session_state.masse_reelle_g / M_koh
    
    if C_base > 0:
        v_eq_theorique = (moles_acide_becher / C_base) * 1000.0
    else:
        v_eq_theorique = 12.0

    st.session_state["th_vrai_veq_calc"] = round(float(v_eq_theorique), 2)
    st.session_state["input_at2_ve_lu_eleve"] = round(float(v_eq_theorique), 2)
    v_eq_visuel = st.session_state.th_vrai_veq_calc

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-à-goutte")
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            C_base = st.number_input(
                "Concentration de la potasse KOH C_0 (mol/L) :",
                min_value=0.001, max_value=1.0, value=float(C_base), step=0.001,
                format="%.3f",
                disabled=True, key="c_base_vitc"
            )
            
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :",
                min_value=0.1, max_value=2.0, value=float(st.session_state.pas_ml), step=0.1,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_slider_pas_ml"
            )

    import random
    if "masse_reelle_acide_mg" not in st.session_state:
        st.session_state.masse_reelle_acide_mg = random.uniform(15.0, 30.0)

    # Affectation pour les calculs de référence de l'Atelier 2 et de l'Atelier 3
    masse_affichee_mg = st.session_state.masse_reelle_acide_mg
    st.session_state.masse_reelle_g = masse_affichee_mg / 1000.0

    if "masse_reelle_g" not in st.session_state:
        st.session_state.masse_reelle_g = 0.0

    moles_acide_becher = st.session_state.masse_reelle_g / M_koh
    v_eq_theorique_calcul = (st.session_state.masse_reelle_g / (C_base * M_koh)) * 1000.0

    st.session_state["th_vrai_veq_calc"] = round(float(v_eq_theorique_calcul), 2)
    st.session_state["input_at2_ve_lu_eleve"] = round(float(v_eq_theorique_calcul), 2)
    v_eq_visuel = st.session_state.th_vrai_veq_calc

    st.info(
        f"Paramètre mesuré : TAN (Total Acid Number) | Prise d'essai d'huile m : {masse_huile_g:.2f} g | "
        f"Masse de KOH équivalente simulée : {masse_affichee_mg:.2f} mg | "
        f"Indicateur : Phénolphtaléine"
    )
    st.divider()

    v_eq_affiche = v_eq_visuel

    # Lecture des couleurs de l'indicateur acido-basique configurées en session pour l'huile
    t_data = st.session_state.teintes_iodometrie
    c_acide = t_data["Avant equivalence"]["couleur_hex"]
    c_zone = t_data["Zone sensible"]["couleur_hex"]
    c_base = t_data["Apres equivalence"]["couleur_hex"]
    
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
        
        let vVerse = 0;
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
            
            ctx.fillStyle = 'rgba(241, 245, 249, 0.9)';
            ctx.fillRect(141.5, yLiquideHaut, 17, hauteurBurette);

            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 0.8;
            for (let y = 60; y < 200; y += 15) {{
                ctx.beginPath(); ctx.moveTo(140, y); ctx.lineTo(145, y); ctx.stroke();
            }}

            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(146, 210, 8, 15);

            // Volume en direct
            ctx.fillStyle = '#b45309';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText(vVerse.toFixed(1) + ' mL', 165, yLiquideHaut + 4);

            // Goutte en chute
            if (isRunning && vVerse < vMax) {{
                let yGoutte = (tick % 2 === 0) ? 232 : 258;
                ctx.fillStyle = 'rgba(241, 245, 249, 0.9)';
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
            let nomTeinte = 'Ambrée sombre';
            if (Math.abs(vVerse - vEq) <= 0.4) {{
                couleurSol = colorZone; 
                nomTeinte = 'Teinte sensible';
            }} else if (vVerse > vEq) {{
                couleurSol = colorBase; 
                nomTeinte = 'Rose-orangé opaque foncé';
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

            ctx.fillStyle = '#334155';
            ctx.font = 'bold 11px sans-serif';
            ctx.fillText('Aspect : ' + nomTeinte, 40, 365);

            setTimeout(() => {{
                requestAnimationFrame(drawScene);
            }}, 500);
        }}

        drawScene();
    </script>
    """
    components.html(html_animation_paillasse, height=460)
    
    if st.button("AFFICHER LES RÉSULTATS DU TITRAGE", key="btn_sync_paillasse_final", use_container_width=True):
        st.session_state.v_verse_ox = float(v_eq_visuel)
        st.session_state.vin_verrouille_tab2 = True
        st.rerun()

    # --- BANDEAU DE RÉSULTATS DE SÉANCE SYNCHRONISÉ ---
    v_eq_affiche = v_eq_visuel

    texte_resultats = (
        f"Repères d'équivalence de la session : "
        f"Volume équivalent de potasse Veq = {v_eq_affiche:.2f} mL"
    )
    
    if st.session_state.get("vin_verrouille_tab2", False):
        st.success(texte_resultats)
        st.session_state["input_at2_ve_lu_eleve"] = v_eq_affiche

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    masse_huile_dosee = 5.00
    C_base_correction = 0.10
    n_potasse_equiv = (C_base_correction * v_eq_theorique) / 1000.0
    moles_acide_par_g_huile = n_potasse_equiv / masse_huile_dosee

    verrou_huile2 = st.session_state.get("vin_verrouille_tab2", False)

    if not st.session_state.get("animation_active", False):
        try:
            generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_huile2)
        except NameError:
            pass
    else:
        st.info("Le versement de la solution titrante est en cours... Le formulaire d'évaluation s'affichera dès que l'animation sera terminée.")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_vin2 = st.checkbox(
        "Je certifie avoir complété l'intégralité des questionnaires de l'Atelier 2.", 
        key="check_certif_javel2_final_net", 
        disabled=verrou_huile2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official_net", use_container_width=True, disabled=verrou_huile2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz Numérique de Paillasse (6 questions)
            score_q2 = sum([
                st.session_state.get("col_g_quiz_vin_q1_tab2") == f"{C_base_correction:.2f} mol/L",
                st.session_state.get("col_g_quiz_vin_q2_tab2") == f"{masse_huile_dosee:.2f} g",
                st.session_state.get("col_g_quiz_vin_q3_tab2") == f"{v_eq_theorique:.2f} mL",
                st.session_state.get("col_g_quiz_vin_q4_tab2") == "n(KOH) = n(Acide)",
                st.session_state.get("col_g_quiz_vin_q5_tab2") == f"{n_potasse_equiv:.5f} mol",
                st.session_state.get("col_g_quiz_vin_q6_tab2") == f"{moles_acide_par_g_huile:.6f} mol/g"
            ]) * (10.0 / 6.0)

            # 2. Correction automatique du Texte à trous (5 cases)
            score_t2 = sum([
                st.session_state.get("vin_t1_tab2") == "Burette",
                st.session_state.get("vin_t2_tab2") == "Balance analytique",
                st.session_state.get("vin_t3_tab2") == "diviser par 1000",
                st.session_state.get("vin_t4_tab2") == "stoechiometriques",
                st.session_state.get("vin_t5_tab2") == "Au changement de couleur persistant"
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
      
        from datetime import datetime
        timestamp_javel2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER INDICE ACIDE 2 SCELLÉ | Note de session : {tot_s} / 20")

        html_export_javel2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Indice Acide 2 - {n_eleve}</title>
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
                <p>Atelier 2 : Dosage de l'acidité libre d'une huile de lubrification</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_javel2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes d'Evaluation</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de suivi de titrage : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue a la Synthese de cours : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Finale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">Solution titrante : Hydroxyde de potassium (KOH) | Concentration : {C_base_correction:.2f} mol/L | Prise d'essai d'huile m : {masse_huile_dosee:.2f} g | Masse d'acides : {masse_affichee_mg:.2f} mg</div>          
            
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ NUMÉRIQUE DE TITRAGE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question de paillasse demandee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Concentration molaire de la solution titrante de KOH</td><td>{st.session_state.get("col_g_quiz_vin_q1_tab2", "Choisir...")}</td><td>{C_base_correction:.2f} mol/L</td><td class='{"status-correct" if st.session_state.get("col_g_quiz_vin_q1_tab2") == f"{C_base_correction:.2f} mol/L" else "status-incorrect"}'>{"CORRECT" if st.session_state.get("col_g_quiz_vin_q1_tab2") == f"{C_base_correction:.2f} mol/L" else "INCORRECT"}</td></tr>
                    <tr><td>2</td><td>Masse d'échantillon d'huile de vidange introduite (m)</td><td>{st.session_state.get("col_g_quiz_vin_q2_tab2", "Choisir...")}</td><td>{masse_huile_dosee:.2f} g</td><td class='{"status-correct" if st.session_state.get("col_g_quiz_vin_q2_tab2") == f"{masse_huile_dosee:.2f} g" else "status-incorrect"}'>{"CORRECT" if st.session_state.get("col_g_quiz_vin_q2_tab2") == f"{masse_huile_dosee:.2f} g" else "INCORRECT"}</td></tr>
                    <tr><td>3</td><td>Volume équivalent exact VE de solution de potasse versé</td><td>{st.session_state.get("col_g_quiz_vin_q3_tab2", "Choisir...")}</td><td>{v_eq_theorique:.2f} mL</td><td class='{"status-correct" if st.session_state.get("col_g_quiz_vin_q3_tab2") == f"{v_eq_theorique:.2f} mL" else "status-incorrect"}'>{"CORRECT" if st.session_state.get("col_g_quiz_vin_q3_tab2") == f"{v_eq_theorique:.2f} mL" else "INCORRECT"}</td></tr>
                    <tr><td>4</td><td>Relation stoechiométrique à l'équivalence</td><td>{st.session_state.get("col_g_quiz_vin_q4_tab2", "Choisir...")}</td><td>n(KOH) = n(Acide)</td><td class='{"status-correct" if st.session_state.get("col_g_quiz_vin_q4_tab2") == "n(KOH) = n(Acide)" else "status-incorrect"}'>{"CORRECT" if st.session_state.get("col_g_quiz_vin_q4_tab2") == "n(KOH) = n(Acide)" else "INCORRECT"}</td></tr>
                    <tr><td>5</td><td>Quantité de matière d'ions hydroxyde HO- apportée (mol)</td><td>{st.session_state.get("col_g_quiz_vin_q5_tab2", "Choisir...")}</td><td>{n_potasse_equiv:.5f} mol</td><td class='{"status-correct" if st.session_state.get("col_g_quiz_vin_q5_tab2") == f"{n_potasse_equiv:.5f} mol" else "status-incorrect"}'>{"CORRECT" if st.session_state.get("col_g_quiz_vin_q5_tab2") == f"{n_potasse_equiv:.5f} mol" else "INCORRECT"}</td></tr>
                    <tr><td>6</td><td>Quantité d'acide par gramme d'huile déduite (mol/g)</td><td>{st.session_state.get("col_g_quiz_vin_q6_tab2", "Choisir...")}</td><td>{moles_acide_par_g_huile:.6f} mol/g</td><td class='{"status-correct" if st.session_state.get("col_g_quiz_vin_q6_tab2") == f"{moles_acide_par_g_huile:.6f} mol/g" else "status-incorrect"}'>{"CORRECT" if st.session_state.get("col_g_quiz_vin_q6_tab2") == f"{moles_acide_par_g_huile:.6f} mol/g" else "INCORRECT"}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHÈSE DE COURS (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Concept du texte a trous</th><th>Saisie Eleve</th><th>Attendu Academique</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Verrerie graduée pour la solution titrante</td><td>{st.session_state.get("vin_t1_tab2", "Choisir...")}</td><td>Burette</td></tr>
                    <tr><td>2</td><td>Verrerie de précision pour prélever l'échantillon</td><td>{st.session_state.get("vin_t2_tab2", "Choisir...")}</td><td>Balance analytique</td></tr>
                    <tr><td>3</td><td>Conversion du volume équivalent en Litres</td><td>{st.session_state.get("vin_t3_tab2", "Choisir...")}</td><td>diviser par 1000</td></tr>
                    <tr><td>4</td><td>Proportions des réactifs à l'équivalence</td><td>{st.session_state.get("vin_t4_tab2", "Choisir...")}</td><td>stoechiometriques</td></tr>
                    <tr><td>5</td><td>Repérage du point d'équivalence expérimental</td><td>{st.session_state.get("vin_t5_tab2", "Choisir...")}</td><td>Au changement de couleur persistant</td></tr>
                </tbody>
            </table>
            
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Rapport d'analyse de l'indice d'acide généré automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Atelier2_Huile_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_javel2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )

with tab3:
    st.header("Calcul théorique & Vérification du lubrifiant")
    st.caption("Vérification de la conformité et de l'état d'usure de l'huile moteur analysée")

    if "vin_verrouille_tab3" not in st.session_state: 
        st.session_state.vin_verrouille_tab3 = False

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_titrant_thiosulfate", 0.10)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    masse_huile_dosee = 5.00
    M_koh = 56.11

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les résultats de votre dosage
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On a pesé exactement 5,00 g d'huile moteur usagée dans un bécher, dissous dans un mélange de solvants. La solution titrante est une solution d'hydroxyde de potassium (KOH).
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq relevé = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Concentration potasse KOH = {c_base_session:.2f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Prise d'essai d'huile m = {masse_huile_dosee:.2f} g</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M(KOH) = {M_koh:.2f} g/mol</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 3")

    # --- CALCULS EXPÉRIMENTAUX DE RÉFÉRENCE DE L'INDICE D'ACIDE (TAN) ---
    v_eq_litre_ref = v_eq_session / 1000.0
    
    # n(KOH) versé à l'équivalence = C0 * VE
    n_soude_equiv_ref = c_base_session * v_eq_litre_ref
    
    # Neutralisation directe mole à mole : n(Acide) dans le bécher = n(KOH)
    n_acide_becher_ref = n_soude_equiv_ref
    
    # Récupération de la masse réelle d'acides générée à l'Atelier 2
    m_acide_becher_ref_fausse = st.session_state.get("masse_reelle_g", 0.0)
    m_acide_becher_mg_ref_fausse = m_acide_becher_ref_fausse * 1000.0
    
    # Quantité d'acide libre par gramme d'huile (mol/g)
    c_acide_fille_ref_fausse = n_acide_becher_ref / masse_huile_dosee
    
    # Titre massique équivalent en KOH
    c_massique_fille_ref = c_acide_fille_ref_fausse * M_koh
    c_massique_fille_mg_ref = c_massique_fille_ref * 1000.0

    n_acide_fiole_ref = n_acide_becher_ref
    c_acide_mere_ref = c_acide_fille_ref_fausse * masse_huile_dosee
    n_acide_bouteille_ref = n_acide_becher_ref
    m_acide_bouteille_ref = m_acide_becher_ref_fausse
    m_acide_bouteille_mg_ref = m_acide_becher_mg_ref_fausse
    c_massique_mere_ref = c_acide_mere_ref * M_koh
    
    # Indice d'acide expérimental TAN calculé = mg de KOH / g d'huile
    degre_bouteille_ref = m_acide_becher_mg_ref_fausse / masse_huile_dosee

    # Sélection de la bouteille active pour adapter la chaîne de conclusion de l'huile
    bouteille_active = st.session_state.get("select_bouteille_huile_tab2", list(st.session_state["eau"].keys())[0])
    tan_nominal_bouteille = st.session_state["eau"][bouteille_active]["tan"]

    if abs(degre_bouteille_ref - tan_nominal_bouteille) / tan_nominal_bouteille <= 0.05:
        att_conclusion_huile = "L'huile est conforme à l'étiquette"
    else:
        att_conclusion_huile = "L'huile n'est pas conforme"

    # Appel du formulaire de saisie des calculs pour l'élève

    verrou_huile3 = st.session_state.get("vin_verrouille_tab3", False)
    
    dict_reponses_bouteille = afficher_questions_bouteille_commerciale(verrouille=verrou_huile3)
    
    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complété l'intégralité des calculs de l'Atelier 3.", 
        key="check_certif_vin3_net", 
        disabled=verrou_huile3
    )
   
    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", 
        key="btn_export_vin3_official_net", 
        use_container_width=True, 
        disabled=verrou_huile3
    ):
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()

        if p_eleve == "INCONNU" or n_eleve == "INCONNU":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not st.session_state.get("check_certif_vin3_net", False):
            st.error("Action refusée : Cochez la case de certification.")
        else:  
            st.success("Validation en cours...")

            # 1. Correction automatique du Bloc Bleu (8 questions d'exploitation du bécher)
            score_b1 = sum([
                abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.0001,
                abs(st.session_state.get("at3_n_soude", 0.0) - n_soude_equiv_ref) < 0.00001,
                abs(st.session_state.get("at3_n_acide_becher", 0.0) - n_acide_becher_ref) < 0.00001,
                abs(st.session_state.get("at3_c_molaire_fille", 0.0) - (n_acide_becher_ref / 5.00)) < 0.000001,
                abs(st.session_state.get("at3_m_acide_gramme", 0.0) - (n_acide_becher_ref * 56.11)) < 0.001,
                abs(st.session_state.get("at3_m_acide_mg", 0.0) - (n_acide_becher_ref * 56.11 * 1000.0)) < 0.1,
                abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1,
                abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 10.0
            ]) * (10.0 / 8.0)

            # 2. Correction automatique du Bloc Jaune (9 questions de calcul de l'indice TAN)
            # Les tolérances ont été resserrées (< 0.1) pour rejeter les saisies à 0.00
            score_b2 = sum([
                st.session_state.get("at3_rapport_dilution", 0.0) == 5.00,
                abs(st.session_state.get("at3_n_acide_fiole", 0.0) - n_acide_becher_ref) < 0.00001,
                abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - (n_acide_becher_ref * 56.11 * 1000.0)) < 0.1,                
                abs(st.session_state.get("at3_c_molaire_mere", 0.0) - (n_acide_becher_ref / 5.00)) < 0.00001,
                abs(st.session_state.get("at3_m_mere_gramme", 0.0) - (n_acide_becher_ref * 56.11)) < 0.001,
                abs(st.session_state.get("at3_m_mere_mg", 0.0) - (n_acide_becher_ref * 56.11 * 1000.0)) < 0.1,
                abs(st.session_state.get("at3_c_massique_mere", 0.0) - st.session_state.get("tan_nominal_bouteille", 3.0)) < 0.1,
                abs(st.session_state.get("at3_c_massique_mere_mg", 0.0) - ((n_acide_becher_ref * 56.11 * 1000.0) / 5.00)) < 0.1,
                st.session_state.get("at3_conclusion_bouteille") == st.session_state.get("att_conclusion_huile", "L'huile est conforme à l'étiquette")
            ]) * (10.0 / 9.0)

            # Sauvegarde des scores de session unifiés pour l'huile
            st.session_state.score_vin3_p1 = round(float(score_b1), 1)
            st.session_state.score_vin3_p2 = round(float(score_b2), 1)
            st.session_state.score_final_vin3 = round(float(score_b1 + score_b2), 1)
            st.session_state.vin_verrouille_tab3 = True
            st.rerun()

    # --- BANDEAU PERSISTANT D'AFFICHAGE ET EXPORT HTML DE CORRECTION ---
    if st.session_state.get("vin_verrouille_tab3", False): 
        scr1 = st.session_state.get("score_vin3_p1", 0.0)
        scr2 = st.session_state.get("score_vin3_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin3", 0.0)
        
        c_base_session = st.session_state.get("c_titrant_potasse", 0.10)
        v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 0.0)
        masse_huile_dosee = 5.00

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        from datetime import datetime
        timestamp_huile3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER 3 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # RE-CALCULS STRICTEMENT IDENTIQUES AU MOTEUR DE DROITE POUR L'AFFICHAGE
        v_eq_litre_ref = v_eq_session / 1000.0
        n_soude_equiv_ref = c_base_session * v_eq_litre_ref
        n_acide_becher_ref = n_soude_equiv_ref
        
        # Alignement des titres massiques dynamiques (g/L et mg/L)
        c_massique_fille_ref = (n_acide_becher_ref * 56.11) / v_eq_litre_ref if v_eq_litre_ref > 0 else 0.0
        c_massique_fille_mg_ref = c_massique_fille_ref * 1000.0

        html_export_vin3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Indice d'Acide 3 - {n_eleve}</title>
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
                <p>Atelier 3 : Évaluation quantitative de l'indice d'acide TAN du lubrifiant</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_huile3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées (V_eq relevé = {v_eq_session:.2f} mL)</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Bloc Exploitation (Bécher) : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue au Bloc Diagnostic d'Indice d'Acide : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">Composé dosé : Acides libres d'oxydation | Prise d'essai d'huile m : {masse_huile_dosee:.2f} g | Solution titrante : Potasse KOH {c_base_session:.3f} mol/L</div> 
            <div class="sub-title">CORRECTION DÉTAILLÉE DU BLOC BLEU (EXPLOITATION EXPÉRIMENTALE DANS LE BÉCHER)</div>
            <table>
                <thead>
                    <tr><th>Grandeur demandée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Volume équivalent en Litres (L)</td>
                        <td>{st.session_state.get("at3_v_eq_l", 0.0):.5f}</td>
                        <td>{v_eq_litre_ref:.5f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_v_eq_l", 0.0) - v_eq_litre_ref) < 0.001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Quantité de potasse KOH versée (mol)</td>
                        <td>{st.session_state.get("at3_n_soude", 0.0):.5f}</td>
                        <td>{n_soude_equiv_ref:.5f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_n_soude", 0.0) - n_soude_equiv_ref) < 0.00001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_n_soude", 0.0) - n_soude_equiv_ref) < 0.00001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Quantité d'acides neutralisés (mol)</td>
                        <td>{st.session_state.get("at3_n_acide_becher", 0.0):.5f}</td>
                        <td>{n_acide_becher_ref:.5f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_becher", 0.0) - n_acide_becher_ref) < 0.00001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_n_acide_becher", 0.0) - n_acide_becher_ref) < 0.00001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Moles d'acide par gramme de fluide (mol/g)</td>
                        <td>{st.session_state.get("at3_c_molaire_fille", 0.0):.6f}</td>
                        <td>{(n_acide_becher_ref / 5.00):.6f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_c_molaire_fille", 0.0) - (n_acide_becher_ref / 5.00)) < 0.000001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_c_molaire_fille", 0.0) - (n_acide_becher_ref / 5.00)) < 0.000001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Masse de KOH requise pour l'essai (g)</td>
                        <td>{st.session_state.get("at3_m_acide_gramme", 0.0):.4f}</td>
                        <td>{(n_acide_becher_ref * 56.11):.4f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_m_acide_gramme", 0.0) - (n_acide_becher_ref * 56.11)) < 0.001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_m_acide_gramme", 0.0) - (n_acide_becher_ref * 56.11)) < 0.001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Masse de KOH requise pour l'essai (mg)</td>
                        <td>{st.session_state.get("at3_m_acide_mg", 0.0):.1f}</td>
                        <td>{(n_acide_becher_ref * 56.11 * 1000.0):.1f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_m_acide_mg", 0.0) - (n_acide_becher_ref * 56.11 * 1000.0)) < 0.1 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_m_acide_mg", 0.0) - (n_acide_becher_ref * 56.11 * 1000.0)) < 0.1 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Titre de masse équivalent fluide (g/L)</td>
                        <td>{st.session_state.get("at3_c_massique_fille", 0.0):.2f}</td>
                        <td>{c_massique_fille_ref:.2f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_c_massique_fille", 0.0) - c_massique_fille_ref) < 0.1 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Titre de masse équivalent fluide (mg/L)</td>
                        <td>{st.session_state.get("at3_c_massique_fille_mg", 0.0):.1f}</td>
                        <td>{c_massique_fille_mg_ref:.1f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 0.5 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_c_massique_fille_mg", 0.0) - c_massique_fille_mg_ref) < 0.5 else "INCORRECT"}
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU BLOC JAUNE (REMONTÉE A L'INDICE TAN DE LA BOUTEILLE D'HUILE)</div>
            <table>
                <thead>
                    <tr><th>Grandeur demandée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Masse de la prise d'essai de fluide (g)</td>
                        <td>{st.session_state.get("at3_rapport_dilution", 0.0):.2f}</td>
                        <td>5.00</td>
                        <td class="{"status-correct" if st.session_state.get("at3_rapport_dilution", 0.0) == 5.00 else "status-incorrect"}">
                            {"CORRECT" if st.session_state.get("at3_rapport_dilution", 0.0) == 5.00 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Quantité d'acide totale de l'essai (mol)</td>
                        <td>{st.session_state.get("at3_n_acide_fiole", 0.0):.5f}</td>
                        <td>{n_acide_becher_ref:.5f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_fiole", 0.0) - n_acide_becher_ref) < 0.00001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_n_acide_fiole", 0.0) - n_acide_becher_ref) < 0.00001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Masse totale de KOH pour l'essai (mg)</td>
                        <td>{st.session_state.get("at3_n_acide_bouteille", 0.0):.1f}</td>
                        <td>{m_acide_becher_mg_ref_fausse:.1f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - m_acide_becher_mg_ref_fausse) < 0.1 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_n_acide_bouteille", 0.0) - m_acide_becher_mg_ref_fausse) < 0.1 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Indice d'acide par gramme (mol/g)</td>
                        <td>{st.session_state.get("at3_c_molaire_mere", 0.0):.5f}</td>
                        <td>{c_acide_fille_ref_fausse:.5f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_c_molaire_mere", 0.0) - c_acide_fille_ref_fausse) < 0.00001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_c_molaire_mere", 0.0) - c_acide_fille_ref_fausse) < 0.00001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Masse pure de KOH par gramme (g)</td>
                        <td>{st.session_state.get("at3_m_mere_gramme", 0.0):.4f}</td>
                        <td>{m_acide_becher_ref_fausse:.4f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_m_mere_gramme", 0.0) - m_acide_becher_ref_fausse) < 0.001 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_m_mere_gramme", 0.0) - m_acide_becher_ref_fausse) < 0.001 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Masse pure de KOH par gramme (mg)</td>
                        <td>{st.session_state.get("at3_m_mere_mg", 0.0):.1f}</td>
                        <td>{m_acide_becher_mg_ref_fausse:.1f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_m_mere_mg", 0.0) - m_acide_becher_mg_ref_fausse) < 0.1 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_m_mere_mg", 0.0) - m_acide_becher_mg_ref_fausse) < 0.1 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Indice d'acide global critique (g/L)</td>
                        <td>{st.session_state.get("at3_c_massique_mere", 0.0):.2f}</td>
                        <td>{st.session_state.get("tan_nominal_bouteille", 3.0):.2f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_mere", 0.0) - st.session_state.get("tan_nominal_bouteille", 3.0)) < 0.1 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_c_massique_mere", 0.0) - st.session_state.get("tan_nominal_bouteille", 3.0)) < 0.1 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Masse KOH de reference calculée (mg/g)</td>
                        <td>{st.session_state.get("at3_c_massique_mere_mg", 0.0):.2f}</td>
                        <td>{(m_acide_becher_mg_ref_fausse / 5.00):.2f}</td>
                        <td class="{"status-correct" if abs(st.session_state.get("at3_c_massique_mere_mg", 0.0) - (m_acide_becher_mg_ref_fausse / 5.00)) < 0.1 else "status-incorrect"}">
                            {"CORRECT" if abs(st.session_state.get("at3_c_massique_mere_mg", 0.0) - (m_acide_becher_mg_ref_fausse / 5.00)) < 0.1 else "INCORRECT"}
                        </td>
                    </tr>
                    <tr>
                        <td>Diagnostic de maintenance lubrifiant</td>
                        <td>{str(st.session_state.get("at3_conclusion_bouteille"))}</td>
                        <td>{str(st.session_state.get("att_conclusion_huile", "L'huile est conforme à l'étiquette"))}</td>
                        <td class="{"status-correct" if st.session_state.get("at3_conclusion_bouteille") == st.session_state.get("att_conclusion_huile", "L'huile est conforme à l'étiquette") else "status-incorrect"}">
                            {"CORRECT" if st.session_state.get("at3_conclusion_bouteille") == st.session_state.get("att_conclusion_huile", "L'huile est conforme à l'étiquette") else "INCORRECT"}
                        </td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
            st.session_state["html_export_vin3"] = html_export_vin3
            st.session_state.vin_verrouille_tab3 = True


        nom_f3 = f"Rapport_Atelier3_Huile_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":", " "]:
            nom_f3 = nom_f3.replace(c, "_")
            
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=st.session_state.get("html_export_vin3", "<h3>Erreur critique : Flux de donnees introuvable</h3>"),
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )





















