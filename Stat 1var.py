# -*- coding: utf-8 -*-

import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application de statistiques à une variable",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application statistiques à une variable")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

# =============================================================================
# INITIALISATION SECURISEE DU SESSION STATE (A l'ouverture de l'application)
# =============================================================================
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
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")


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
    "1. Le diagramme bâton",
    "2. le diagramme circulaire",
    "3. le graphique",
    "4. le diagramme à moustache",
    "5. l'histogramme",
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]

def afficher_questions_statistiques5_dynamiques(df_donnees=None, verrouille=False):
    import numpy as np
    
    if "df_session_tab5" not in st.session_state or st.session_state.df_session_tab5 is None:
        return {}, {}
        
    v_total_n = st.session_state.get("hist_vrai_total_n", 0.0)
    v_nbr_c = st.session_state.get("hist_vrai_nbr_classes", 0.0)
    v_max_ni = st.session_state.get("hist_vrai_max_ni", 0.0)

    # Protection : si le tableau est vide au chargement global, on simule des donnees
    if v_total_n == 0.0:
        v_total_n, v_nbr_c, v_max_ni = 60.0, 4.0, 22.0

    col_double_quiz_dyn5, col_double_trous_dyn5 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ INTERACTIF DE 10 QUESTIONS DYNAMIQUES (10 PTS) ---
    with col_double_quiz_dyn5:
        st.markdown("##### Quiz numerique sur VOTRE histogramme (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{v_total_n:.0f}", f"{v_total_n + 10:.0f}", "100"]
        st.write("**1.** D'apres votre groupement en classes, quelle est la valeur de l'effectif global N ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_dyn_s5_q1", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_nbr_c:.0f}", f"{v_nbr_c + 2:.0f}", "10"]
        st.write("**2.** Quel est le nombre exact de rectangles (classes) dessines sur votre graphique ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_dyn_s5_q2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_max_ni:.0f}", f"{v_max_ni - 4:.0f}", "50"]
        st.write("**3.** Quelle est la valeur de l'effectif ni maximal declare dans votre distribution ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_dyn_s5_q3", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** L'amplitude d'une classe d'intervalle [a ; b[ se calcule en effectuant :")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "La soustraction : b - a", "La somme : a + b", "Le rapport : b / a"], key="col_g_quiz_dyn_s5_q4", disabled=verrouille, label_visibility="collapsed")

        st.write("**5.** Le centre d'une classe d'intervalle [a ; b[ se calcule en effectuant :")
        dict_reponses_quiz["q5"] = st.selectbox("", ["Choisir...", "La demi-somme : (a + b) / 2", "La difference : b - a", "Le produit : a * b"], key="col_g_quiz_dyn_s5_q5", disabled=verrouille, label_visibility="collapsed")

        st.write("**6.** Un histogramme est une representation graphique exclusivement reservee aux variables :")
        dict_reponses_quiz["q6"] = st.selectbox("", ["Choisir...", "Quantitatives continues regroupees en intervalles", "Qualitatives nominales"], key="col_g_quiz_dyn_s5_q6", disabled=verrouille, label_visibility="collapsed")

        st.write("**7.** Si les amplitudes des classes de la serie sont inegales, la hauteur de chaque rectangle est proportionnelle a :")
        dict_reponses_quiz["q7"] = st.selectbox("", ["Choisir...", "La densite d'effectif (ni / amplitude)", "L'effectif brut ni", "La borne superieure"], key="col_g_quiz_dyn_s5_q7", disabled=verrouille, label_visibility="collapsed")

        st.write("**8.** Si les amplitudes de toutes les classes sont rigoureusement egales, la hauteur du rectangle represente :")
        dict_reponses_quiz["q8"] = st.selectbox("", ["Choisir...", "L'effectif ni de la classe (ou sa frequence)", "Le centre de la classe"], key="col_g_quiz_dyn_s5_q8", disabled=verrouille, label_visibility="collapsed")

        st.write("**9.** Dans un histogramme, c'est la surface (l'aire) de chaque rectangle qui est proportionnelle a :")
        dict_reponses_quiz["q9"] = st.selectbox("", ["Choisir...", "L'effectif ni de la classe", "L'etendue globale", "La borne de depart"], key="col_g_quiz_dyn_s5_q9", disabled=verrouille, label_visibility="collapsed")

        st.write("**10.** La classe qui possede le plus grand effectif (ou la plus forte densite) est qualifiee de :")
        dict_reponses_quiz["q10"] = st.selectbox("", ["Choisir...", "Classe modale", "Mediane de classe", "Intervalle quartile"], key="col_g_quiz_dyn_s5_q10", disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS 100% MATHÉMATIQUE EN SÉLECTEURS (10 PTS) ---
    with col_double_trous_dyn5:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. L'histogramme represente graphiquement des variables")
        with c2: t1 = st.selectbox("", ["Choisir...", "Continues", "Discretes", "Qualitatives"], key="stat5_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Les donnees numeriques brutes sont regroupees par")
        with c4: t2 = st.selectbox("", ["Choisir...", "Classes", "Batons", "Secteurs"], key="stat5_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La largeur de la base de chaque rectangle correspond a l'")
        with c6: t3 = st.selectbox("", ["Choisir...", "Amplitude", "Mediane", "Moyenne"], key="stat5_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La demi-somme des bornes d'un intervalle donne son")
        with c8: t4 = st.selectbox("", ["Choisir...", "Centre", "Amplitude", "Ecart-type"], key="stat5_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le rapport de l'effectif sur la largeur est la")
        with c10: t5 = st.selectbox("", ["Choisir...", "Densite", "Frequence", "Variance"], key="stat5_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'intervalle qui regroupe la plus forte densite est dit")
        with c12: t6 = st.selectbox("", ["Choisir...", "Modal", "Median", "Quartile"], key="stat5_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Dans ce graphique, l'effectif ni est represente par l'")
        with c14: t7 = st.selectbox("", ["Choisir...", "Aire du rectangle", "Hauteur seule", "Base"], key="stat5_t7_dyn", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le crochet ferme au depart de [a ; b[ signifie que a est")
        with c16: t8 = st.selectbox("", ["Choisir...", "Inclus", "Exclu", "Nul"], key="stat5_t8_dyn", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le crochet ouvert a la fin de [a ; b[ signifie que b est")
        with c18: t9 = st.selectbox("", ["Choisir...", "Exclu", "Inclus", "Maximal"], key="stat5_t9_dyn", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. La somme de toutes les aires de l'histogramme vaut")
        with c20: t10 = st.selectbox("", ["Choisir...", "L'effectif total N", "La moyenne", "100%"], key="stat5_t10_dyn", disabled=verrouille, label_visibility="collapsed")

        dict_trous = {
            "t1": st.session_state.get("stat5_t1_dyn", "Choisir..."), "t2": st.session_state.get("stat5_t2_dyn", "Choisir..."),
            "t3": st.session_state.get("stat5_t3_dyn", "Choisir..."), "t4": st.session_state.get("stat5_t4_dyn", "Choisir..."),
            "t5": st.session_state.get("stat5_t5_dyn", "Choisir..."), "t6": t6, "t7": t7, "t8": t8, "t9": t9, "t10": t10
        }

    return dict_reponses_quiz, dict_trous


def afficher_questions_statistiques4_dynamiques(df_donnees=None, verrouille=False):
    import numpy as np
    
    # GARDE-FOU ANTI-CRASH INTÉGRAL : Si l'onglet n'est pas chargé ou si la fonction est lue hors contexte, on coupe court
    if df_donnees is None or "df_session_tab4" not in st.session_state or st.session_state.df_session_tab4 is None:
        return {}, {}
        
    # Sécurité métrique : si aucune boîte n'a commencé à être calculée, on n'affiche aucun widget visuel
    if st.session_state.get("mous_vrai_total_n", 0.0) == 0.0 and st.session_state.get("mous_vrai_min", 0.0) == 0.0:
        return {}, {}
        
    v_min = st.session_state.get("mous_vrai_min", 4.0)
    v_q1 = st.session_state.get("mous_vrai_q1", 0.0)
    v_med = st.session_state.get("mous_vrai_med", 0.0)
    v_q3 = st.session_state.get("mous_vrai_q3", 0.0)
    v_max = st.session_state.get("mous_vrai_max", 0.0)
    v_iqr = st.session_state.get("mous_vrai_iqr", 0.0)

    if v_min == 0.0 and v_max == 0.0:
        v_min, v_q1, v_med, v_q3, v_max, v_iqr = 4.0, 8.0, 11.0, 14.0, 19.0, 6.0

    col_double_quiz_dyn4, col_double_trous_dyn4 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ INTERACTIF DE 10 QUESTIONS DYNAMIQUES ---
    with col_double_quiz_dyn4:
        st.markdown("##### Quiz numerique sur VOTRE diagramme a moustache (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{v_min:.2f}", f"{v_min - 1:.2f}", "0.00"]
        st.write("**1.** Quelle est la valeur minimale qui delimite l'extremite de la moustache gauche ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_dyn_s4_q1", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_q1:.2f}", f"{v_q1 + 2:.2f}", "10.00"]
        st.write("**2.** Quelle est la valeur du premier quartile Q1 formant le bord gauche de la boite ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_dyn_s4_q2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_med:.2f}", f"{v_med + 1:.2f}", "12.00"]
        st.write("**3.** Quelle est la valeur centrale de la mediane marquant le trait interieur de la boite ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_dyn_s4_q3", disabled=verrouille, label_visibility="collapsed")

        opts_q4 = ["Choisir...", f"{v_q3:.2f}", f"{v_q3 - 3:.2f}", "15.00"]
        st.write("**4.** Quelle est la valeur du troisieme quartile Q3 formant le bord droit de la boite ?")
        dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, key="col_g_quiz_dyn_s4_q4", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{v_max:.2f}", f"{v_max + 4:.2f}", "20.00"]
        st.write("**5.** Quelle est la valeur maximale qui delimite l'extremite de la moustache droite ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_dyn_s4_q5", disabled=verrouille, label_visibility="collapsed")

        st.write("**6.** La boîte centrale du diagramme (entre Q1 et Q3) englobe obligatoirement :")
        dict_reponses_quiz["q6"] = st.selectbox("", ["Choisir...", "50% de la population", "25% de la population", "75% de la population"], key="col_g_quiz_dyn_s4_q6", disabled=verrouille, label_visibility="collapsed")

        st.write("**7.** Quel pourcentage maximal de la population se situe en dessous de la mediane ?")
        dict_reponses_quiz["q7"] = st.selectbox("", ["Choisir...", "50% de la population", "25% de la population", "100%"], key="col_g_quiz_dyn_s4_q7", disabled=verrouille, label_visibility="collapsed")

        st.write("**8.** La longueur totale separant le debut de la boite de sa fin s'appelle :")
        dict_reponses_quiz["q8"] = st.selectbox("", ["Choisir...", "L'ecart interquartile", "L'etendue totale", "La variance"], key="col_g_quiz_dyn_s4_q8", disabled=verrouille, label_visibility="collapsed")

        st.write("**9.** Si une valeur se trouve isolee tres loin au-dela des moustaches, elle est qualifiee de :")
        dict_reponses_quiz["q9"] = st.selectbox("", ["Choisir...", "Valeur atypique ou aberrante", "Valeur centrale", "Valeur nulle"], key="col_g_quiz_dyn_s4_q9", disabled=verrouille, label_visibility="collapsed")

        st.write("**10.** Le diagramme a moustache est l'outil visuel de reference pour analyser :")
        dict_reponses_quiz["q10"] = st.selectbox("", ["Choisir...", "La dispersion et la symetrie d'une serie", "Le calcul exact de la moyenne"], key="col_g_quiz_dyn_s4_q10", disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS 100% INTERACTIF EN SÉLECTEURS ---
    with col_double_trous_dyn4:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le diagramme a moustache porte aussi le nom anglais de")
        with c2: t1 = st.selectbox("", ["Choisir...", "Boxplot", "Scatter", "Piechart"], key="stat4_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le rectangle central porte le nom traditionnel de")
        with c4: t2 = st.selectbox("", ["Choisir...", "Boite", "Moustache", "Segment"], key="stat4_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Les traits qui prolongent la boite s'appellent les")
        with c6: t3 = st.selectbox("", ["Choisir...", "Moustaches", "Vecteurs", "Axes"], key="stat4_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La boite contient la moitie des effectifs centraux soit")
        with c8: t4 = st.selectbox("", ["Choisir...", "50%", "25%", "75%"], key="stat4_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le premier quartile Q1 correspond a au moins")
        with c10: t5 = st.selectbox("", ["Choisir...", "25%", "50%", "75%"], key="stat4_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le troisieme quartile Q3 correspond a au moins")
        with c12: t6 = st.selectbox("", ["Choisir...", "75%", "25%", "50%"], key="stat4_t6_dyn", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La ligne coloree a l'interieur du rectangle est la")
        with c14: t7 = st.selectbox("", ["Choisir...", "Mediane", "Moyenne", "Etendue"], key="stat4_t7_dyn", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La largeur du rectangle central mesure la longueur de l'")
        with c16: t8 = st.selectbox("", ["Choisir...", "Ecart interquartile", "Etendue globale"], key="stat4_t8_dyn", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La longueur totale entre les deux extremites mesure l'")
        with c18: t9 = st.selectbox("", ["Choisir...", "Etendue", "Mediane", "Moyenne"], key="stat4_t9_dyn", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Ce trace se prete a l'etude de variables de type")
        with c20: t10 = st.selectbox("", ["Choisir...", "Quantitatifs", "Qualitatifs"], key="stat4_t10_dyn", disabled=verrouille, label_visibility="collapsed")

        dict_trous = {
            "t1": st.session_state.get("stat4_t1_dyn", "Choisir..."), "t2": st.session_state.get("stat4_t2_dyn", "Choisir..."),
            "t3": st.session_state.get("stat4_t3_dyn", "Choisir..."), "t4": st.session_state.get("stat4_t4_dyn", "Choisir..."),
            "t5": t5, "t6": t6, "t7": t7, "t8": t8, "t9": t9, "t10": t10
        }

    return dict_reponses_quiz, dict_trous



def afficher_questions_statistiques3_dynamiques(df_donnees=None, verrouille=False):
    import numpy as np
    
    if df_donnees is None or "df_session_tab3" not in st.session_state or st.session_state.df_session_tab3 is None:
        return {}, {}
        
    v_total_n = st.session_state.get("graph_vrai_total_n", 10.0)
    v_max_y = st.session_state.get("graph_vrai_max_y", 10.0)
    v_min_y = st.session_state.get("graph_vrai_min_y", 0.0)
    v_amplitude = round(float(v_max_y - v_min_y), 1)

    col_double_quiz_dyn3, col_double_trous_dyn3 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ INTERACTIF DE 10 QUESTIONS ---
    with col_double_quiz_dyn3:
        st.markdown("##### Quiz sur VOTRE repere cartesien (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{v_total_n:.0f}", f"{v_total_n + 5:.0f}", "100"]
        st.write("**1.** L'effectif global cumule (somme des ordonnees ni) vaut :")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_dyn_s3_q1", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_max_y:.1f}", f"{v_max_y + 10:.1f}", "0.0"]
        st.write("**2.** Quelle est la valeur de l'ordonnee maximale (Y max) lue ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_dyn_s3_q2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_min_y:.1f}", f"{v_min_y - 2:.1f}", "10.0"]
        st.write("**3.** Quelle est la valeur de l'ordonnee minimale (Y min) lue ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_dyn_s3_q3", disabled=verrouille, label_visibility="collapsed")

        opts_q4 = ["Choisir...", f"{v_amplitude:.1f}", f"{v_amplitude + 5:.1f}", "5.0"]
        st.write("**4.** L'amplitude verticale (Y max - Y min) de votre courbe s'eleve a :")
        dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, key="col_g_quiz_dyn_s3_q4", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{v_amplitude/2:.1f}", f"{(v_amplitude/2)+2:.1f}", "1.0"]
        st.write("**5.** La demi-amplitude ou ecart moyen vertical de la distribution vaut :")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_dyn_s3_q5", disabled=verrouille, label_visibility="collapsed")

        st.write("**6.** Relier des coordonnees par des segments rectilignes definit une :")
        dict_reponses_quiz["q6"] = st.selectbox("", ["Choisir...", "Interpolation lineaire", "Regression polynomiale"], key="col_g_quiz_dyn_s3_q6", disabled=verrouille, label_visibility="collapsed")

        st.write("**7.** Sur l'axe vertical (ordonnees) d'une courbe d'evolution, on place :")
        dict_reponses_quiz["q7"] = st.selectbox("", ["Choisir...", "L'effectif ni / la grandeur mesuree", "Le caractere xi"], key="col_g_quiz_dyn_s3_q7", disabled=verrouille, label_visibility="collapsed")

        st.write("**8.** La hauteur d'un point geometrique sur ce graphique depend directement de :")
        dict_reponses_quiz["q8"] = st.selectbox("", ["Choisir...", "Son ordonnee ni", "Son abscisse xi"], key="col_g_quiz_dyn_s3_q8", disabled=verrouille, label_visibility="collapsed")

        st.write("**9.** Si un graphique suit l'evolution d'une grandeur temporelle, la serie est :")
        dict_reponses_quiz["q9"] = st.selectbox("", ["Choisir...", "Chronologique", "Qualitative textuelle"], key="col_g_quiz_dyn_s3_q9", disabled=verrouille, label_visibility="collapsed")

        st.write("**10.** Le rapport de l'effectif d'un point sur l'effectif global N definit sa :")
        dict_reponses_quiz["q10"] = st.selectbox("", ["Choisir...", "Frequence relative", "Amplitude de classe"], key="col_g_quiz_dyn_s3_q10", disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS UNIFORMISÉ EN SÉLECTEURS ---
    with col_double_trous_dyn3:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Un repere a deux axes orthogonaux est dit repere")
        with c2: t1 = st.selectbox("", ["Choisir...", "Cartesien", "Polaire"], key="stat3_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'axe horizontal porte traditionnellement le nom d'")
        with c4: t2 = st.selectbox("", ["Choisir...", "Abscisses", "Ordonnees"], key="stat3_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'axe vertical porte traditionnellement le nom d'")
        with c4: t3 = st.selectbox("", ["Choisir...", "Ordonnees", "Abscisses"], key="stat3_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Le croisement perpendiculaire des deux axes definit l'")
        with c8: t4 = st.selectbox("", ["Choisir...", "Origine", "Mediane"], key="stat3_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La totalite des points isoles du repere forme un")
        with c10: t5 = st.selectbox("", ["Choisir...", "Nuage de points", "Histogramme"], key="stat3_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Un trace compose de segments successifs est une ligne")
        with c12: t6 = st.selectbox("", ["Choisir...", "Brisee", "Continue"], key="stat3_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Si la courbe monte, la tendance de la distribution est")
        with c14: t7 = st.selectbox("", ["Choisir...", "Croissante", "Constante"], key="stat3_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le point d'intersection initial a pour coordonnees")
        with c16: t8 = st.selectbox("", ["Choisir...", "(0,0)", "(1,1)"], key="stat3_t8", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La premiere coordonnee lue pour placer un point est l'")
        with c18: t9 = st.selectbox("", ["Choisir...", "Abscisse", "Ordonnee"], key="stat3_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. La courbe cartesienne est ideale pour des caracteres")
        with c20: t10 = st.selectbox("", ["Choisir...", "Quantitatifs", "Qualitatifs"], key="stat3_t10", disabled=verrouille, label_visibility="collapsed")

        dict_trous = {
            "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5, "t6": t6, "t7": t7, "t8": t8, "t9": t9, "t10": t10
        }

    return dict_reponses_quiz, dict_trous

def afficher_questions_statistiques2_dynamiques(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st
        
    # Recupération des variables calculées par votre moteur de graphe
    v_total_n = st.session_state.get("circ_vrai_total_n", 0.0)
    v_max_fr = st.session_state.get("circ_max_freq", 0.0)
    v_min_fr = st.session_state.get("circ_min_freq", 0.0)
    v_labels = st.session_state.get("circ_labels_presents", [])
    
    # VALEURS DE SECOURS : Si l'etudiant n'a rien saisi, on force des valeurs types
    # Cela evite le blocage ou les coupures blanches a l'ecran
    if v_total_n == 0.0:
        v_total_n = 20.0
        v_max_fr = 45.0
        v_min_fr = 15.0
        v_labels = [" Categorie A", " Categorie B"]
    
    v_label_premier = v_labels if len(v_labels) > 0 else "Aucun"
    v_label_dernier = v_labels[-1] if len(v_labels) > 1 else "Aucun"

    # Activation immediate de la structure bicolonne
    col_double_quiz_dyn2, col_double_trous_dyn2 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ INTERACTIF ---
    with col_double_quiz_dyn2:
        st.markdown("##### Quiz numerique sur VOS parts de repartition (10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{v_total_n:.0f}", f"{v_total_n + 5:.0f}", f"{v_total_n * 2:.0f}"]
        st.write("**1.** D'apres votre grille de saisie, quelle est la valeur exacte de l'effectif total N ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_dyn_s2_q1", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_max_fr:.1f}%", f"{v_max_fr + 12.5:.1f}%", "100.0%"]
        st.write("**2.** Quelle est la valeur de la frequence maximale (%) obtenue dans votre gâteau ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_dyn_s2_q2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_min_fr:.1f}%", f"{v_min_fr - 3.2:.1f}%", "0.0%"]
        st.write("**3.** Quelle est la valeur de la frequence minimale (%) calculee par la console ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_dyn_s2_q3", disabled=verrouille, label_visibility="collapsed")

        opts_q4 = ["Choisir...", f"{v_label_premier}", "Effectif Global", "Somme des Secteurs"]
        st.write("**4.** Quel est l'intitule exact du tout premier caractere (xi) de votre tableau ?")
        dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, key="col_g_quiz_dyn_s2_q4", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{v_label_dernier}", "Moyenne", "Ecart-type"]
        st.write("**5.** Quel est l'intitule exact de la derniere categorie ajoutee a la ligne ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_dyn_s2_q5", disabled=verrouille, label_visibility="collapsed")

        st.write("**6.** Pour calculer un angle de secteur en degres a partir d'un effectif ni, on applique la formule :")
        dict_reponses_quiz["q6"] = st.selectbox("", ["Choisir...", "Angle = (ni / N) * 360", "Angle = ni * 100", "Angle = N / ni"], key="col_g_quiz_dyn_s2_q6", disabled=verrouille, label_visibility="collapsed")

        st.write("**7.** Si une categorie de donnees represente une frequence de pile 25%, son angle vaut :")
        dict_reponses_quiz["q7"] = st.selectbox("", ["Choisir...", "90 degres (un quart de cercle)", "45 degres", "180 degres"], key="col_g_quiz_dyn_s2_q7", disabled=verrouille, label_visibility="collapsed")

        st.write("**8.** La somme de toutes les frequences relatives calculees au sein d'une serie vaut :")
        dict_reponses_quiz["q8"] = st.selectbox("", ["Choisir...", "100% (ou 1)", "360%", "L'effectif total N"], key="col_g_quiz_dyn_s2_q8", disabled=verrouille, label_visibility="collapsed")

        st.write("**9.** Le diagramme circulaire est l'outil parfait pour representer graphiquement :")
        dict_reponses_quiz["q9"] = st.selectbox("", ["Choisir...", "Une structure de repartition globale", "Une evolution temporelle lineaire", "Une dispersion d'ecart-type"], key="col_g_quiz_dyn_s2_q9", disabled=verrouille, label_visibility="collapsed")

        st.write("**10.** Le rapport de l'effectif d'une ligne ni sur l'effectif global N definit sa :")
        dict_reponses_quiz["q10"] = st.selectbox("", ["Choisir...", "Frequence", "Vergence", "Amplitude de classe"], key="col_g_quiz_dyn_s2_q10", disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS ---
    with col_double_trous_dyn2:
        st.markdown("##### Synthese de cours (Texte a trous numerique - 10 pts)")
        
        ct1, ct2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct1: st.write("1. Le nombre global de donnees collectees dans N vaut :")
        with ct2: t1_saisie = st.text_input("", key="stat2_t1_dyn", disabled=verrouille, label_visibility="collapsed")
        
        ct3, ct4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct3: st.write("2. Saisissez la frequence maximale lue sans le symbole % :")
        with ct4: t2_saisie = st.text_input("", key="stat2_t2_dyn", disabled=verrouille, label_visibility="collapsed")

        ct5, ct6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct5: st.write("3. Saisissez la frequence minimale lue sans le symbole % :")
        with ct6: t3_saisie = st.text_input("", key="stat2_t3_dyn", disabled=verrouille, label_visibility="collapsed")

        ct7, ct8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct7: st.write("4. L'ecart entre votre frequence max et min s'eleve a :")
        with ct8: t4_saisie = st.text_input("", key="stat2_t4_dyn", disabled=verrouille, label_visibility="collapsed")

        ct9, ct10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct9: st.write("5. L'angle associe a un secteur de 50% de la population vaut :")
        with ct10: t5_saisie = st.selectbox("", ["Choisir...", "180°", "90°", "360°"], key="stat2_t5_dyn", disabled=verrouille, label_visibility="collapsed")

        ct11, ct12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct11: st.write("6. Un gâteau statistique complet verifie un angle total de :")
        with ct12: t6_saisie = st.selectbox("", ["Choisir...", "360°", "100°", "180°"], key="stat2_t6_dyn", disabled=verrouille, label_visibility="collapsed")

        ct13, ct14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct13: st.write("7. La somme de toutes les frequences relatives en % vaut :")
        with ct14: t7_saisie = st.selectbox("", ["Choisir...", "100%", "360%", "50%"], key="stat2_t7_dyn", disabled=verrouille, label_visibility="collapsed")

        ct15, ct16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct15: st.write("8. Le diagramme circulaire reflete la structure de :")
        with ct16: t8_saisie = st.selectbox("", ["Choisir...", "Repartition", "Dispersion"], key="stat2_t8_dyn", disabled=verrouille, label_visibility="collapsed")

        ct17, ct18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct17: st.write("9. Pour l'angle en degres, le coefficient multiplicateur vaut :")
        with ct18: t9_saisie = st.selectbox("", ["Choisir...", "3.6", "360", "100"], key="stat2_t9_dyn", disabled=verrouille, label_visibility="collapsed")

        ct19, ct20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with ct19: st.write("10. Cet outil traite aussi les variables qualitatives ou :")
        with ct20: t10_saisie = st.selectbox("", ["Choisir...", "Textuelles", "Continues"], key="stat2_t10_dyn", disabled=verrouille, label_visibility="collapsed")

        dict_trous = {
            "t1": t1_saisie, "t2": t2_saisie, "t3": t3_saisie, "t4": t4_saisie, "t5": t5_saisie,
            "t6": t6_saisie, "t7": t7_saisie, "t8": t8_saisie, "t9": t9_saisie, "t10": t10_saisie
        }

    # --- PUSH DE SYNCHRONISATION DANS LA SESSION GLOBALE ---
    # Sauvegarde des choix du quiz
    for qk, qv in dict_reponses_quiz.items():
        st.session_state[f"col_g_quiz_dyn_s2_state_{qk}"] = qv
        
    # Sauvegarde des choix du texte a trous
    for tk, tv in dict_trous.items():
        st.session_state[f"col_g_trous_dyn_s2_state_{tk}"] = tv

    return dict_reponses_quiz, dict_trous       
        
def afficher_questions_statistiques_dynamiques(df_donnees, verrouille=False):
    import numpy as np
    import pandas as pd
    import streamlit as st

    # 1. MOTEUR DE PRE-CALCULS DES VALEURS DU TABLEAU POUR LES QUESTIONS
    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    # Valeurs de secours par defaut si le tableau est vide
    v_eff_total = 10
    v_moyenne = 10.0
    v_mediane = 10.0
    v_etendue = 5.0
    v_max_xi = 12.0
    v_min_xi = 7.0

    if not df_filtre.empty:
        try:
            nums = df_filtre["Caractere (xi)"].astype(float).to_numpy()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            weighted = np.repeat(nums, effs.astype(int))
            
            if len(weighted) > 0:
                v_eff_total = int(np.sum(effs))
                v_moyenne = round(float(np.average(nums, weights=effs)), 2)
                v_mediane = round(float(np.median(weighted)), 2)
                v_min_xi = round(float(np.min(nums)), 2)
                v_max_xi = round(float(np.max(nums)), 2)
                v_etendue = round(float(v_max_xi - v_min_xi), 2)
        except:
            pass

    col_double_quiz_dyn, col_double_trous_dyn = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DYNAMIQUE DE 10 QUESTIONS ---
    with col_double_quiz_dyn:
        st.markdown(f"##### Quiz sur VOTRE serie de donnees (10 questions - 10 pts)")
        
        # Initialisation fixe de l'ordre pour eviter le melange au clic
        if "ordre_quiz_dyn_s1" not in st.session_state:
            st.session_state.ordre_quiz_dyn_s1 = [f"q{i}" for i in range(1, 11)]

        dict_reponses_quiz = {}
        
        for num_idx, q_id in enumerate(st.session_state.ordre_quiz_dyn_s1, 1):
            cle_select = f"col_g_quiz_dyn_s1_{q_id}"
            
            # Generation des questions et des options selon les donnees reelles du tableau
            if q_id == "q1":
                q_txt = f"Quelle est la valeur exacte de l'effectif total (N) de votre serie ?"
                opts = [f"{v_eff_total}", f"{v_eff_total + 2}", f"{v_eff_total * 2}"]
            elif q_id == "q2":
                q_txt = f"La valeur calculee de la moyenne ponderee de votre serie vaut :"
                opts = [f"{v_moyenne}", f"{v_moyenne + 1.50:.2f}", f"{v_moyenne - 0.75:.2f}"]
            elif q_id == "q3":
                q_txt = f"La valeur centrale de la mediane de votre distribution est :"
                opts = [f"{v_mediane}", f"{v_mediane + 2.00:.2f}", f"{v_mediane / 2.00:.2f}"]
            elif q_id == "q4":
                q_txt = f"L'etendue totale de votre serie (Valeur max - Valeur min) vaut :"
                opts = [f"{v_etendue}", f"{v_etendue + 4.00:.2f}", "10.00"]
            elif q_id == "q5":
                q_txt = f"Quelle est la plus petite valeur du caractere (xi min) saisie ?"
                opts = [f"{v_min_xi}", f"{v_min_xi - 1.00:.2f}", "0.00"]
            elif q_id == "q6":
                q_txt = f"Quelle est la plus grande valeur du caractere (xi max) saisie ?"
                opts = [f"{v_max_xi}", f"{v_max_xi + 3.50:.2f}", f"{v_max_xi * 1.5:.2f}"]
            elif q_id == "q7":
                q_txt = f"Dans un diagramme en batons, l'axe vertical (ordonnees) represente :"
                opts = ["Les effectifs (ni)", "Les caracteres (xi)", "Les angles en degres"]
            elif q_id == "q8":
                q_txt = f"Dans un diagramme en batons, l'axe horizontal (abscisses) represente :"
                opts = ["Les caracteres (xi)", "Les effectifs (ni)", "Les frequences en %"]
            elif q_id == "q9":
                q_txt = f"La somme de toutes les frequences calculees d'une serie doit toujours valoir :"
                opts = ["100% (ou 1)", "50%", "L'effectif total N"]
            elif q_id == "q10":
                q_txt = f"Si l'on multiplie tous les effectifs par 2, la moyenne de la serie :"
                opts = ["Reste strictement inchangee", "Est multipliee par 2", "Est divisee par 2"]

            cle_opts_shuffle = f"opts_shuffled_dyn_s1_{q_id}"
            if cle_opts_shuffle not in st.session_state:
                v_correcte = opts
                import random
                copie_opts = list(opts)
                random.shuffle(copie_opts)
                st.session_state[cle_opts_shuffle] = ["Choisir..."] + copie_opts
                st.session_state[f"correct_ans_dyn_s1_{q_id}"] = v_correcte

            # Affichage du texte de la question a l'ecran
            st.write(f"**{num_idx}.** {q_txt}")

            val_p = st.session_state.get(cle_select, "Choisir...")
            liste_opts = st.session_state.get(cle_opts_shuffle, ["Choisir..."])
            idx_securise = liste_opts.index(val_p) if val_p in liste_opts else 0
            
            dict_reponses_quiz[f"{q_id}_stat1"] = st.selectbox(
                "", 
                liste_opts, 
                index=idx_securise, 
                key=cle_select, 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

        # =========================================================================
        # C'EST EXACTEMENT ICI QU'IL FAUT COLLER LA SUITE (HORS DE LA BOUCLE FOR)
        # =========================================================================
        with col_double_trous_dyn:
            st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
            
            # SÉCURITÉ : Initialisation par defaut pour eviter les NameError/UnboundLocalError
            t1 = t2 = t3 = t4 = t5 = t6 = t7 = t8 = t9 = t10 = "Choisir..."

                
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write("1. Le diagramme en batons modelise une variable")
            with c2: t1 = st.selectbox("", ["Choisir...", "Discrete", "Continue"], key="st1_t1", disabled=verrouille, label_visibility="collapsed")

            c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c5: st.write("3. La valeur partageant la serie en deux blocs de 50% est la")
            with c6: t3 = st.selectbox("", ["Choisir...", "Mediane", "Moyenne"], key="st1_t3", disabled=verrouille, label_visibility="collapsed")

            c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c7: st.write("4. L'indicateur de dispersion associe a la moyenne est l'")
            with c8: t4 = st.selectbox("", ["Choisir...", "Ecart-type", "Etendue"], key="st1_t4", disabled=verrouille, label_visibility="collapsed")

            c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c9: st.write("5. Le premier quartile Q1 correspond a au moins")
            with c10: t5 = st.selectbox("", ["Choisir...", "25%", "50%", "75%"], key="st1_t5", disabled=verrouille, label_visibility="collapsed")

            c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c11: st.write("6. Le troisieme quartile Q3 correspond a au moins")
            with c12: t6 = st.selectbox("", ["Choisir...", "75%", "25%", "100%"], key="st1_t6", disabled=verrouille, label_visibility="collapsed")

            c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c13: st.write("7. La difference entre la valeur max et min est l'")
            with c14: t7 = st.selectbox("", ["Choisir...", "Etendue", "Variance"], key="st1_t7", disabled=verrouille, label_visibility="collapsed")

            c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c15: st.write("8. L'effectif d'une valeur note ni represente sa")
            with c16: t8 = st.selectbox("", ["Choisir...", "Frequence", "Frequence absolue"], key="st1_t8", disabled=verrouille, label_visibility="collapsed")

            c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c17: st.write("9. Le rapport de ni sur l'effectif global N est la")
            with c18: t9 = st.selectbox("", ["Choisir...", "Frequence", "Moyenne"], key="st1_t9", disabled=verrouille, label_visibility="collapsed")

            c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c19: st.write("10. L'effectif total N est le denominateur du calcul de la")
            with c20: t10 = st.selectbox("", ["Choisir...", "Frequence", "Mediane"], key="st1_t10", disabled=verrouille, label_visibility="collapsed")

        # 3. SAUVEGARDE ET ENREGISTREMENT DES REPONSES DANS LA SESSION GLOBALE
        dict_reponses_quiz["t1_stat1"] = t1
        dict_reponses_quiz["t2_stat1"] = t2
        dict_reponses_quiz["t3_stat1"] = t3
        dict_reponses_quiz["t4_stat1"] = t4
        dict_reponses_quiz["t5_stat1"] = t5
        dict_reponses_quiz["t6_stat1"] = t6
        dict_reponses_quiz["t7_stat1"] = t7
        dict_reponses_quiz["t8_stat1"] = t8
        dict_reponses_quiz["t9_stat1"] = t9
        dict_reponses_quiz["t10_stat1"] = t10

        # Pousser toutes les saisies dans la session globale pour le moteur d'evaluation HTML
        for k_key, v_val in dict_reponses_quiz.items():
            st.session_state[f"col_g_quiz_dyn_s1_state_{k_key}"] = v_val

        # RETOUR MULTIPLE POUR CORRESPONDRE EXACTEMENT A LA LIGNE 1233
        return dict_reponses_quiz, dict_reponses_quiz

def calculer_et_tracer_histogramme_matplotlib(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez les bornes des classes [Inf ; Sup[ et les effectifs ni."
    
    st.session_state.hist_vrai_total_n = 0.0
    st.session_state.hist_vrai_nbr_classes = 0.0
    st.session_state.hist_vrai_max_ni = 0.0

    df_filtre = df_donnees.dropna(subset=["Borne Inf", "Borne Sup", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Borne Inf"].astype(str).str.strip() != "") & 
                          (df_filtre["Borne Sup"].astype(str).str.strip() != "") & 
                          (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            b_inf = pd.to_numeric(df_filtre["Borne Inf"], errors='coerce').to_numpy()
            b_sup = pd.to_numeric(df_filtre["Borne Sup"], errors='coerce').to_numpy()
            effs = pd.to_numeric(df_filtre["Effectif (ni)"], errors='coerce').to_numpy()
            
            mask = ~np.isnan(b_inf) & ~np.isnan(b_sup) & ~np.isnan(effs)
            b_inf, b_sup, effs = b_inf[mask], b_sup[mask], effs[mask]

            if len(effs) > 0:
                amplitudes = b_sup - b_inf
                centres = (b_inf + b_sup) / 2.0
                
                # Verification de l'egalite des amplitudes pour adapter la hauteur (densite)
                amplitudes_egales = np.allclose(amplitudes, amplitudes[0])
                
                if amplitudes_egales:
                    hauteurs = effs
                    ylabel_txt = "Effectifs (ni)"
                else:
                    hauteurs = effs / amplitudes
                    ylabel_txt = "Densite d'effectif"

                total_n = np.sum(effs)
                st.session_state.hist_vrai_total_n = float(total_n)
                st.session_state.hist_vrai_nbr_classes = float(len(effs))
                st.session_state.hist_vrai_max_ni = float(np.max(effs))

                lignes_stats = [f"• Effectif Total N = {total_n:.0f}", f"• Nombre de classes = {len(effs):.0f}"]
                for i in range(len(effs)):
                    lignes_stats.append(f"  [{b_inf[i]:.1f};{b_sup[i]:.1f}[ : Centre={centres[i]:.1f}, Amp={amplitudes[i]:.1f}")
                stats_text = "\n".join(lignes_stats)

                # Trace manuel de l'histogramme pour gerer les amplitudes egales ou inegales
                ax.bar(centres, hauteurs, width=amplitudes, color="#38bdf8", edgecolor="#0f172a", lw=1.5, zorder=3)
                ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
                ax.set_ylabel(ylabel_txt, color="#cbd5e1", fontsize=9, fontweight="bold")
        except Exception:
            stats_text = "Erreur de calcul. Verifiez que toutes les saisies sont strictement numeriques."

    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Classes du caractere continuous", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Histogramme des frequences / effectifs", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats5_affichage_texte = stats_text
    return fig



def calculer_et_tracer_moustache_matplotlib(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(4, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs numeriques pour generer la boite a moustaches."
    
    st.session_state.mous_vrai_min = 0.0
    st.session_state.mous_vrai_q1 = 0.0
    st.session_state.mous_vrai_med = 0.0
    st.session_state.mous_vrai_q3 = 0.0
    st.session_state.mous_vrai_max = 0.0
    st.session_state.mous_vrai_iqr = 0.0

    if df_donnees is None or "df_session_tab4" not in st.session_state or st.session_state.df_session_tab4 is None:
        ax.spines['bottom'].set_color('#94a3b8')
        ax.spines['left'].set_color('#94a3b8')
        ax.tick_params(colors='#94a3b8', labelsize=8)
        st.session_state.stats4_affichage_texte = stats_text
        return fig

    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            df_numerique = df_filtre.copy()
            df_numerique["xi_num"] = pd.to_numeric(df_numerique["Caractere (xi)"], errors='coerce')
            df_numerique["ni_num"] = pd.to_numeric(df_numerique["Effectif (ni)"], errors='coerce')
            df_numerique = df_numerique.dropna(subset=["xi_num", "ni_num"])

            if not df_numerique.empty:
                nums = df_numerique["xi_num"].to_numpy()
                effs = df_numerique["ni_num"].to_numpy()
                weighted = np.repeat(nums, effs.astype(int))

                if len(weighted) > 0:
                    v_min = float(np.min(nums))
                    v_max = float(np.max(nums))
                    v_q1 = float(np.percentile(weighted, 25))
                    v_med = float(np.median(weighted))
                    v_q3 = float(np.percentile(weighted, 75))
                    v_iqr = float(v_q3 - v_q1)

                    st.session_state.mous_vrai_min = round(v_min, 1)
                    st.session_state.mous_vrai_q1 = round(v_q1, 1)
                    st.session_state.mous_vrai_med = round(v_med, 1)
                    st.session_state.mous_vrai_q3 = round(v_q3, 1)
                    st.session_state.mous_vrai_max = round(v_max, 1)
                    st.session_state.mous_vrai_iqr = round(v_iqr, 1)

                    stats_text = (
                        f"Moyenne : {np.average(nums, weights=effs):.2f}\n"
                        f"Ecart-type : {np.sqrt(np.average((nums - np.average(nums, weights=effs))**2, weights=effs)):.2f}\n"
                        f"Mediane : {v_med:.1f}\n"
                        f"Q1 : {v_q1:.1f} | Q3 : {v_q3:.1f}"
                    )

                    # Tracé VERTICAL exact de la boite (Equivalence avec self.ax4.boxplot(..., vert=True))
                    ax.boxplot(
                        weighted, vert=True, patch_artist=True, widths=0.3,
                        boxprops=dict(facecolor="#1e3a8a", color="#38bdf8", lw=1.5),
                        whiskerprops=dict(color="#38bdf8", lw=1.5),
                        capprops=dict(color="#38bdf8", lw=1.5),
                        medianprops=dict(color="#eab308", lw=2),
                        flierprops=dict(marker="o", markerfacecolor="#ef4444", markeredgecolor="none")
                    )
                    ax.grid(True, axis="y", color="#334155", linestyle=":", lw=0.8)
            else:
                ax.text(0.5, 0.5, "Donnees non numeriques", color="#ef4444", ha='center', va='center')
                stats_text = "Statistiques (Moyenne, Mediane, Q1/Q3) indisponibles pour caracteres textuels."
        except Exception:
            ax.text(0.5, 0.5, "Donnees non numeriques", color="#ef4444", ha='center', va='center')
            stats_text = "Statistiques (Moyenne, Mediane, Q1/Q3) indisponibles pour caracteres textuels."

    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_title("Diagramme a moustache vertical", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats4_affichage_texte = stats_text
    return fig

def mettre_a_jour_graphique3(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs numeriques ordonnees pour tracer la courbe."
    
    st.session_state.graph_vrai_total_n = 0.0
    st.session_state.graph_vrai_max_y = 0.0
    st.session_state.graph_vrai_min_y = 0.0

    if df_donnees is None:
        st.session_state.stats3_affichage_texte = stats_text
        return fig

    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            df_numerique = df_filtre.copy()
            df_numerique["xi_num"] = pd.to_numeric(df_numerique["Caractere (xi)"], errors='coerce')
            df_numerique["ni_num"] = pd.to_numeric(df_numerique["Effectif (ni)"], errors='coerce')
            df_numerique = df_numerique.dropna(subset=["xi_num", "ni_num"])

            if not df_numerique.empty:
                df_triee = df_numerique.sort_values(by="xi_num")
                nums_x = df_triee["xi_num"].to_numpy()
                effs_y = df_triee["ni_num"].to_numpy()
                labels_x = df_triee["xi_num"].astype(str).tolist()

                weighted = np.repeat(nums_x, effs_y.astype(int))

                moy = np.average(nums_x, weights=effs_y)
                std = np.sqrt(np.average((nums_x - moy)**2, weights=effs_y))
                med = np.median(weighted)
                q1, q3 = np.percentile(weighted, [25, 75])

                st.session_state.graph_vrai_total_n = float(np.sum(effs_y))
                st.session_state.graph_vrai_max_y = float(np.max(effs_y))
                st.session_state.graph_vrai_min_y = float(np.min(effs_y))

                stats_text = (
                    f"Moyenne : {moy:.2f}\n"
                    f"Ecart-type : {std:.2f}\n"
                    f"Mediane : {med:.2f}\n"
                    f"Q1 : {q1:.2f} | Q3 : {q3:.2f}"
                )

                ax.plot(labels_x, effs_y, color="#38bdf8", marker="o", linestyle="-", lw=2, markersize=6, zorder=3)
            else:
                labels_x = df_filtre["Caractere (xi)"].astype(str).tolist()
                effs_y = pd.to_numeric(df_filtre["Effectif (ni)"], errors='coerce').fillna(0).to_numpy()
                ax.plot(labels_x, effs_y, color="#38bdf8", marker="o", linestyle="-", lw=2, zorder=3)
                stats_text = "Statistiques indisponibles pour caracteres qualitatifs."

            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
        except Exception:
            pass

    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Caractere (xi)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("Effectif (ni)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Courbe d'evolution de la serie", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats3_affichage_texte = stats_text
    return fig

def calculer_et_tracer_graphique_lineaire_matplotlib(df_donnees=None):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs numeriques ordonnees pour tracer la courbe d'evolution."
    
    st.session_state.graph_vrai_total_n = 0.0
    st.session_state.graph_vrai_max_y = 0.0
    st.session_state.graph_vrai_min_y = 0.0

    # BOUCLIER DE SÉCURITÉ ABSOLUE : Si les donnees sont absentes ou non initialisees par la session, on quitte proprement sans crash global
    if df_donnees is None or "df_session_tab3" not in st.session_state or st.session_state.df_session_tab3 is None:
        ax.spines['bottom'].set_color('#94a3b8')
        ax.spines['left'].set_color('#94a3b8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#94a3b8', labelsize=8)
        st.session_state.stats3_affichage_texte = stats_text
        return fig

def calculer_et_tracer_circulaire_matplotlib(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs dans le tableau pour generer le diagramme circulaire."
    
    st.session_state.circ_vrai_total_n = 0.0
    st.session_state.circ_max_freq = 0.0
    st.session_state.circ_min_freq = 0.0
    st.session_state.circ_labels_presents = []

    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()
            total_n = np.sum(effs)

            if total_n > 0:
                freqs = (effs / total_n) * 100.0
                angles = (effs / total_n) * 360.0

                st.session_state.circ_vrai_total_n = float(total_n)
                st.session_state.circ_max_freq = round(float(np.max(freqs)), 1)
                st.session_state.circ_min_freq = round(float(np.min(freqs)), 1)
                st.session_state.circ_labels_presents = labels

                # Generation textuelle pour le panneau de resultats
                lignes_stats = [f"Effectif Total N = {total_n:.0f}"]
                for lbl, fr, ang in zip(labels, freqs, angles):
                    lignes_stats.append(f"• {lbl} : {fr:.1f}% ({ang:.1f}°)")
                stats_text = "\n".join(lignes_stats)

                # Trace du diagramme circulaire Matplotlib
                theme_sombre_colors = plt.cm.Dark2(np.linspace(0, 1, len(labels)))
                wedges, texts, autotexts = ax.pie(
                    freqs, labels=labels, autopct='%1.1f%%', 
                    startangle=90, colors=theme_sombre_colors,
                    textprops=dict(color="#cbd5e1", fontsize=8)
                )
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(8)
                    autotext.set_weight('bold')
        except Exception:
            stats_text = "Erreur de calcul. Verifiez que les effectifs saisis sont numeriques."

    st.session_state.stats2_affichage_texte = stats_text
    return fig

def calculer_et_tracer_batons_matplotlib(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs numeriques dans le tableau pour lancer les calculs."
    
    # Réinitialisation des variables de calcul dynamique de session
    st.session_state.vrai_total_n = 0.0
    st.session_state.vraie_moyenne = 0.0
    st.session_state.vraie_mediane = 0.0
    st.session_state.vrai_q1 = 0.0
    st.session_state.vrai_q3 = 0.0
    st.session_state.vrai_etendue = 0.0
    
    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            nums = df_filtre["Caractere (xi)"].astype(float).to_numpy()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()

            weighted = np.repeat(nums, effs.astype(int))

            if len(weighted) == 0:
                stats_text = "Saisissez des effectifs superieurs ou egaux a 1 pour lancer l'analyse."
            else:
                moy = np.average(nums, weights=effs)
                std = np.sqrt(np.average((nums - moy)**2, weights=effs))
                med = np.median(weighted)
                q1, q3 = np.percentile(weighted, [25, 75])
                etendue = np.max(nums) - np.min(nums)
                total_n = np.sum(effs)

                # Stockage des vraies valeurs physiques calculées
                st.session_state.vrai_total_n = float(total_n)
                st.session_state.vraie_moyenne = round(float(moy), 2)
                st.session_state.vraie_mediane = round(float(med), 2)
                st.session_state.vrai_q1 = round(float(q1), 2)
                st.session_state.vrai_q3 = round(float(q3), 2)
                st.session_state.vrai_etendue = round(float(etendue), 2)

                stats_text = (
                    f"Moyenne : {moy:.2f}\n"
                    f"Ecart-type : {std:.2f}\n"
                    f"Mediane : {med:.2f}\n"
                    f"Premier Quartile Q1 : {q1:.2f} | Troisieme Quartile Q3 : {q3:.2f}"
                )

            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            
        except Exception:
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            stats_text = "Statistiques indisponibles pour caracteres qualitatifs."

    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Caractere (xi)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("Effectif (ni)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Diagramme en batons de la serie", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats1_affichage_texte = stats_text
    return fig

with tab0:
    st.subheader("Identification de l'élève")
    st.write("Veuillez renseigner vos informations pour déverrouiller l'accès aux ateliers pratiques.")
    
    col_ident_1, col_ident_2 = st.columns(2)
    
    with col_ident_1:
        # Les champs lisent la configuration et bloquent la saisie si validé
        nom_brut = st.text_input(
            "Nom de famille :",
            value=st.session_state.get("nom_var", ""),
            disabled=st.session_state.verrouille,
            key="widget_saisie_nom_maitre"
        )
        
        prenom_brut = st.text_input(
            "Prénom :",
            value=st.session_state.get("prenom_var", ""),
            disabled=st.session_state.verrouille,
            key="widget_saisie_prenom_maitre"
        )
        
        classe_brut = st.text_input(
            "Groupe / Classe :",
            value=st.session_state.get("classe_var", ""),
            disabled=st.session_state.verrouille,
            key="widget_saisie_classe_maitre"
        )
        
        st.write("")
        
        # Bouton maître de validation d'accès
        if st.button(
            "Valider mes informations (OK)", 
            key="btn_validation_identite_maitre",
            disabled=st.session_state.verrouille
        ):
            # Normalisation et injection dans la session au moment du clic
            st.session_state.nom_var = nom_brut.strip().upper()
            st.session_state.prenom_var = prenom_brut.strip().capitalize()
            st.session_state.classe_var = classe_brut.strip().upper()
            
            # Appel de la fonction globale de validation
            valider_saisie()
            
            # Rechargement propre de la page avec la parenthèse fermée
            if st.session_state.verrouille:
                st.rerun()



with tab1:
    st.header("Atelier 1 : Analyse Statistique & Diagramme en Batons")
    
    # 1. Initialisation securisee du nombre de lignes
    if "nbr_lignes_tab1" not in st.session_state: 
        st.session_state.nbr_lignes_tab1 = 5

    # =========================================================================
    # ARCHITECTURE EN COLONNES : GRILLE DE SAISIE / GRAPHIQUE SYNCHRONE
    # =========================================================================
    col_g_tableau, col_d_graphique = st.columns([1.2, 1.8])

    # --- PANNEAU DE GAUCHE : TABLEAU DE SAISIE ET BOUTONS ---
    with col_g_tableau:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DES DONNÉES STATISTIQUES</p>", unsafe_allow_html=True)
            
            # Saisie securisee du nombre de lignes
            n_lignes = st.number_input(
                "Nombre de valeurs differentes (lignes) :", 
                min_value=1, 
                max_value=50, 
                value=int(st.session_state.nbr_lignes_tab1), 
                step=1, 
                key="input_nbr_lignes_tab1"
            )
            
            # Mise a jour de la taille si elle change
            if n_lignes != st.session_state.nbr_lignes_tab1:
                st.session_state.nbr_lignes_tab1 = n_lignes
                # Creation d'un nouveau dataframe adapte
                st.session_state.df_session_tab1 = pd.DataFrame({
                    "Caractere (xi)": [""] * n_lignes,
                    "Effectif (ni)": [""] * n_lignes
                })
            
            # Construction ou recuperation du DataFrame initial
            if "df_session_tab1" not in st.session_state:
                st.session_state.df_session_tab1 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab1,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab1
                })

            # Editeur de donnees interactif
            df_edite = st.data_editor(
                st.session_state.df_session_tab1, 
                use_container_width=True, 
                hide_index=True,
                key="editeur_grille_tab1"
            )
            st.session_state.df_session_tab1 = df_edite

            # Bouton de reinitialisation complet
            if st.button("Reinitialiser la grille", key="btn_reset_tab1", use_container_width=True):
                st.session_state.df_session_tab1 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab1,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab1
                })
                st.rerun()

        # CONSOLE DES STATISTIQUES DESCRIPTIVES
        with st.container(border=True):
            st.markdown("**Console d'analyse descriptive :**")
            st.text(st.session_state.get("stats1_affichage_texte", "En attente de saisies..."))

    # --- PANNEAU DE DROITE : LE DIAGRAMME EN BÂTONS EN DIRECT ---
    with col_d_graphique:
        st.subheader("Rendu graphique de la distribution")
        try:
            fig_batons = calculer_et_tracer_batons_matplotlib(st.session_state.df_session_tab1)
            st.pyplot(fig_batons, use_container_width=True)
        except Exception as e:
            st.info("Veuillez remplir correctement les valeurs numeriques dans le tableau pour afficher le graphique.")

    # =========================================================================
    # BLOC DE VALIDATION FINALE SUR 20 POINTS SANS EMOJI
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    if "stat1_verrouille" not in st.session_state:
        st.session_state.stat1_verrouille = False

    # Affichage des questions dynamiques
    dict_reponses_complet = afficher_questions_statistiques_dynamiques(
        st.session_state.df_session_tab1, 
        verrouille=st.session_state.stat1_verrouille
    )

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complete l'integralite des 20 questions de l'Atelier 1.", 
        key="check_certif_stat1_officiel_20pts", 
        disabled=st.session_state.stat1_verrouille
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_stat1_official_20pts", use_container_width=True, disabled=st.session_state.stat1_verrouille):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz
            score_quiz = 0.0
            for i in range(1, 11):
                q_key = f"q{i}"
                saisie_e = st.session_state.get(f"col_g_quiz_dyn_s1_{q_key}", "Choisir...")
                attendu_e = st.session_state.get(f"correct_ans_dyn_s1_{q_key}")
                if str(saisie_e) == str(attendu_e):
                    score_quiz += 1.0

            # 2. Correction automatique du Texte a trous
            score_trous = 0.0
            attendus_trous = {
                "t1": "Discrete", "t2": "Moyenne", "t3": "Mediane", "t4": "Ecart-type",
                "t5": "25%", "t6": "75%", "t7": "Etendue", "t8": "Frequence absolue",
                "t9": "Frequence", "t10": "Frequence"
            }
            for tk, tv in attendus_trous.items():
                if st.session_state.get(f"st1_{tk}") == tv:
                    score_trous += 1.0

            st.session_state.score_stat1_p1 = round(score_quiz, 1)
            st.session_state.score_stat1_p2 = round(score_trous, 1)
            st.session_state.score_final_stat1 = round(score_quiz + score_trous, 1)
            st.session_state.stat1_verrouille = True
            st.rerun()

    # LE GENERATEUR DU DOCUMENT HTML OFFICIEL APRÈS VERROUILLAGE
    if st.session_state.stat1_verrouille:
        scr1 = st.session_state.get("score_stat1_p1", 0.0)
        scr2 = st.session_state.get("score_stat1_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat1", 0.0)
        timestamp_stat1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 1 SCELLE | Note globale de l'eleve : {tot_s} / 20")

        # =========================================================================
        # MOTEUR D'INJECTION DU GRAPHIQUE BASE64 DANS LE HTML
        # =========================================================================
        img_base64_stat1 = ""
        try:
            df_source = st.session_state.df_session_tab1.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
            df_source = df_source[(df_source["Caractere (xi)"].astype(str).str.strip() != "") & (df_source["Effectif (ni)"].astype(str).str.strip() != "")]
            
            fig_export, ax_export = plt.subplots(figsize=(6, 3.5))
            xi_vals = df_source["Caractere (xi)"].astype(float).to_numpy()
            ni_vals = df_source["Effectif (ni)"].astype(float).to_numpy()
            
            ax_export.bar(xi_vals, ni_vals, color='#1e3a8a', width=0.4, edgecolor='black', zorder=3)
            ax_export.set_xlabel("Caracteres (xi)", fontsize=10, fontweight='bold')
            ax_export.set_ylabel("Effectifs (ni)", fontsize=10, fontweight='bold')
            ax_export.set_title("Diagramme en batons de la distribution", fontsize=11, fontweight='bold')
            ax_export.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
            plt.tight_layout()
            
            import io, base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150)
            buf.seek(0)
            img_base64_stat1 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close(fig_export)
        except Exception as e:
            img_base64_stat1 = ""

        # =========================================================================
        # CONTRUCTION EN DOCK TEXTE DU RAPPORT HTML (SANS RUPTURE DE CONTEXTE)
        # =========================================================================
        # Generation des lignes dynamiques du tableau HTML liees aux saisies
        lignes_tableau_html = ""
        try:
            for idx, row in st.session_state.df_session_tab1.iterrows():
                xi = str(row["Caractere (xi)"]).strip()
                ni = str(row["Effectif (ni)"]).strip()
                if xi or ni:
                    lignes_tableau_html += f"<tr><td style='text-align:center;'>{xi}</td><td style='text-align:center;'>{ni}</td></tr>"
        except Exception:
            lignes_tableau_html = "<tr><td colspan='2' style='text-align:center;'>Aucune donnee valide</td></tr>"

        lignes_tableau_html = ""
        try:
            for idx, row in st.session_state.df_session_tab1.iterrows():
                xi = str(row["Caractere (xi)"]).strip()
                ni = str(row["Effectif (ni)"]).strip()
                if xi or ni:
                    lignes_tableau_html += f"<tr><td style='text-align:center;'>{xi}</td><td style='text-align:center;'>{ni}</td></tr>"
        except Exception:
            lignes_tableau_html = "<tr><td colspan='2' style='text-align:center;'>Aucune donnee valide</td></tr>"

        # En-tête globale du rapport autonome
        html_export_stat1 = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rapport Statistiques 1 - {n_eleve}</title>
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
        .flex-container {{ display: flex; gap: 20px; margin-bottom: 25px; }}
        .flex-child {{ flex: 1; background: white; padding: 15px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    </style>
</head>
<body>
    <div class="header-box">
        <h1>Professeur Laurent GALLET</h1>
        <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
        <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat1}</p>
        <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
    </div>

    <div class="sub-title">Recapitulatif de session - Diagramme en Batons</div>
    <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
        &bull; Partie 1 : Quiz de validation adaptatif : <strong>{scr1} / 10</strong><br>
        &bull; Partie 2 : Synthese de cours (10 trous) : <strong>{scr2} / 10</strong>
    </p>

    <div class="sub-title">Donnees de Base de l'Atelier 1</div>
    <div class="flex-container">
        <div class="flex-child">
            <p style="font-weight: bold; margin-top: 0; color: #1e3a8a;">Grille des donnees saisies</p>
            <table style="margin-bottom: 0; box-shadow: none; border: 1px solid #e2e8f0;">
                <thead>
                    <tr><th style="text-align:center;">Caractere (xi)</th><th style="text-align:center;">Effectif (ni)</th></tr>
                </thead>
                <tbody>
                    {lignes_tableau_html}
                </tbody>
            </table>
        </div>
        <div class="flex-child" style="text-align: center;">
            <p style="font-weight: bold; margin-top: 0; color: #1e3a8a;">Distribution graphique</p>
"""
        
        if img_base64_stat1:
            html_export_stat1 += f'<img src="data:image/png;base64,{img_base64_stat1}" alt="Diagramme en batons" style="max-width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 4px;" />'
        else:
            html_export_stat1 += '<p style="color: #64748b; font-size: 13px; padding-top: 40px;">Aucun graphique disponible</p>'

        html_export_stat1 += """
        </div>
    </div>

    <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ DYNAMIQUE (10 PTS)</div>
    <table>
        <thead>
            <tr>
                <th style="width: 50%;">Question posee</th>
                <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                <th style="width: 15%; text-align: center;">Attendu Technique</th>
                <th style="width: 15%; text-align: center;">Verdict</th>
            </tr>
        </thead>
        <tbody>
"""

        enonces_quiz_html = {
            "q1": "Quelle est la valeur exacte de l'effectif total (N) de votre serie ?",
            "q2": "La valeur calculee de la moyenne ponderee de votre serie vaut :",
            "q3": "La valeur centrale de la mediane de votre distribution est :",
            "q4": "L'etendue totale de votre serie (Valeur max - Valeur min) vaut :",
            "q5": "Quelle est la plus petite valeur du caractere (xi min) saisie ?",
            "q6": "Quelle est la plus grande valeur du caractere (xi max) saisie ?",
            "q7": "Dans un diagramme en batons, l'axe vertical (ordonnees) represente :",
            "q8": "Dans un diagramme en batons, l'axe horizontal (abscisses) represente :",
            "q9": "La somme de toutes les frequences calculees d'une serie doit toujours valoir :",
            "q10": "Si l'on multiplie tous les effectifs par 2, la moyenne de la serie :"
        }

        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s1_{qk}", "Choisir...")
            attendu = st.session_state.get(f"correct_ans_dyn_s1_{qk}")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            
            html_export_stat1 += f"""
            <tr>
                <td><strong>Q{i}.</strong> {enonces_quiz_html[qk]}</td>
                <td style='text-align:center;'>{saisie}</td>
                <td style='text-align:center;'>{attendu}</td>
                <td class='{v_class}' style='text-align: center;'>{v_lbl}</td>
            </tr>"""

        html_export_stat1 += """
        </tbody>
    </table>

    <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS (10 PTS)</div>
    <table>
        <thead>
            <tr>
                <th style="width: 50%;">Phrase a trous complete</th>
                <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                <th style="width: 15%; text-align: center;">Attendu theorique</th>
                <th style="width: 15%; text-align: center;">Verdict</th>
            </tr>
        </thead>
        <tbody>
"""

        phrases_trous_html = {
            "t1": "1. Le diagramme en batons modelise une variable [...]",
            "t2": "2. La somme des produits xi*ni divisee par N donne la [...]",
            "t3": "3. La valeur partageant la serie en deux blocs de 50% est la [...]",
            "t4": "4. L'indicateur de dispersion associe a la moyenne est l' [...]",
            "t5": "5. Le premier quartile Q1 correspond a au moins [...]",
            "t6": "6. Le troisieme quartile Q3 correspond a au moins [...]",
            "t7": "7. La difference entre la valeur max et min est l' [...]",
            "t8": "8. L'effectif d'une valeur note ni represente sa [...]",
            "t9": "9. Le rapport de ni sur l'effectif global N est la [...]",
            "t10": "10. L'effectif total N est le denominateur du calcul de la [...]"
        }

        for tk, tv in attendus_trous.items():
            saisie = st.session_state.get(f"st1_{tk}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            
            html_export_stat1 += f"""
            <tr>
                <td>{phrases_trous_html[tk]}</td>
                <td style='text-align:center;'>{saisie}</td>
                <td style='text-align:center;'>{tv}</td>
                <td class='{v_class}' style='text-align: center;'>{v_lbl}</td>
            </tr>"""

        html_export_stat1 += """
        </tbody>
    </table>
</body>
</html>"""

        # Option de telechargement direct du rapport officiel en HTML pour l'eleve
        st.download_button(
            label="TELECHARGER LE RAPPORT HTML OFFICIEL DE L'ATELIER 1",
            data=html_export_stat1,
            file_name=preparer_nom_fichier("Atelier1_Batons"),
            mime="text/html",
            use_container_width=True
        )


        
with tab2:
    st.header("Atelier 2 : Analyse Statistique & Diagramme Circulaire")
    
    # 1. Initialisation permanente du nombre de lignes de saisie en memoire
    if "nbr_lignes_tab2" not in st.session_state: 
        st.session_state.nbr_lignes_tab2 = 5
    if "stat2_verrouille" not in st.session_state: 
        st.session_state.stat2_verrouille = False

    # =========================================================================
    # ARCHITECTURE EN COLONNES : GRILLE DE SAISIE / RENDU DU GÂTEAU
    # =========================================================================
    col_g_tableau2, col_d_graphique2 = st.columns([1.2, 1.8])

    with col_g_tableau2:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DES DONNÉES STATISTIQUES (CIRCULAIRE)</p>", unsafe_allow_html=True)
            
            # Saisie securisee du nombre de lignes
            n_lignes2 = st.number_input(
                "Nombre de lignes necessaires (categories) :", 
                min_value=1, 
                max_value=50, 
                value=int(st.session_state.nbr_lignes_tab2), 
                step=1, 
                key="input_nbr_lignes_tab2"
            )
            
            # Reconstruction du dataframe si la taille change
            if n_lignes2 != st.session_state.nbr_lignes_tab2:
                st.session_state.nbr_lignes_tab2 = n_lignes2
                st.session_state.df_session_tab2 = pd.DataFrame({
                    "Caractere (xi)": [""] * n_lignes2,
                    "Effectif (ni)": [""] * n_lignes2
                })
            
            # Initialisation par defaut du dataframe d'onglet 2
            if "df_session_tab2" not in st.session_state:
                st.session_state.df_session_tab2 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab2,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab2
                })

            df_edite2 = st.data_editor(
                st.session_state.df_session_tab2, 
                use_container_width=True, 
                hide_index=True, 
                key="editeur_grille_tab2"
            )
            st.session_state.df_session_tab2 = df_edite2

            if st.button("Reinitialiser la grille ", key="btn_reset_tab2", use_container_width=True):
                st.session_state.df_session_tab2 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab2,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab2
                })
                st.rerun()

        with st.container(border=True):
            st.markdown("**Frequences relatives & Secteurs angulaires :**")
            st.text(st.session_state.get("stats2_affichage_texte", "En attente de saisies..."))

    with col_d_graphique2:
        st.subheader("Distribution en secteurs")
        try:
            fig_circulaire = calculer_et_tracer_circulaire_matplotlib(st.session_state.df_session_tab2)
            st.pyplot(fig_circulaire, use_container_width=True)
        except Exception:
            st.info("Veuillez remplir les donnees numeriques du tableau pour generer le diagramme circulaire.")

    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 2")
    
    # Appel de la fonction maitresse de generation dynamique
    res_q2, res_t2 = afficher_questions_statistiques2_dynamiques(
        st.session_state.df_session_tab2, 
        verrouille=st.session_state.stat2_verrouille
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires dynamiques de l'Atelier 2.", 
        key="check_certif_stat2_officiel_20pts_dyn", 
        disabled=st.session_state.stat2_verrouille
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_stat2_official_20pts_dyn", use_container_width=True, disabled=st.session_state.stat2_verrouille):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            v_total_n = st.session_state.get("circ_vrai_total_n", 0.0)
            v_max_fr = st.session_state.get("circ_max_freq", 0.0)
            v_min_fr = st.session_state.get("circ_min_freq", 0.0)
            v_labels = st.session_state.get("circ_labels_presents", [])
            v_label_premier = v_labels[0] if len(v_labels) > 0 else "Aucun"
            v_label_dernier = v_labels[-1] if len(v_labels) > 1 else "Aucun"

            # 1. Correction automatique du Quiz de gauche (10 questions x 1.0 pt)
            score_q2 = 0.0
            if st.session_state.get("col_g_quiz_dyn_s2_q1") == f"{v_total_n:.0f}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q2") == f"{v_max_fr:.1f}%": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q3") == f"{v_min_fr:.1f}%": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q4") == f"{v_label_premier}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q5") == f"{v_label_dernier}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q6") == "Angle = (ni / N) * 360": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q7") == "90 degres (un quart de cercle)": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q8") == "100% (ou 1)": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q9") == "Une structure de repartition globale": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s2_q10") == "Frequence": score_q2 += 1.0

            # 2. Correction automatique du Texte a trous de droite (10 cases x 1.0 pt)
            score_t2 = 0.0
            try:
                if float(str(st.session_state.get("stat2_t1_dyn", "")).strip()) == float(v_total_n): score_t2 += 1.0
            except: pass
            try:
                if float(str(st.session_state.get("stat2_t2_dyn", "")).strip()) == float(v_max_fr): score_t2 += 1.0
            except: pass
            try:
                if float(str(st.session_state.get("stat2_t3_dyn", "")).strip()) == float(v_min_fr): score_t2 += 1.0
            except: pass
            try:
                if float(str(st.session_state.get("stat2_t4_dyn", "")).strip()) == round(float(v_max_fr - v_min_fr), 1): score_t2 += 1.0
            except: pass

            if st.session_state.get("stat2_t5_dyn") == "180°": score_t2 += 1.0
            if st.session_state.get("stat2_t6_dyn") == "360°": score_t2 += 1.0
            if st.session_state.get("stat2_t7_dyn") == "100%": score_t2 += 1.0
            if st.session_state.get("stat2_t8_dyn") == "Repartition": score_t2 += 1.0
            if st.session_state.get("stat2_t9_dyn") == "3.6": score_t2 += 1.0
            if st.session_state.get("stat2_t10_dyn") == "Textuelles": score_t2 += 1.0

            st.session_state.score_stat2_p1 = round(score_q2, 1)
            st.session_state.score_stat2_p2 = round(score_t2, 1)
            st.session_state.score_final_stat2 = round(score_q2 + score_t2, 1)
            st.session_state.stat2_verrouille = True
            st.rerun()

    # GENERATION ET AFFICHAGE DU RAPPORT HTML OFFICIEL DE L'ATELIER 2
    if st.session_state.stat2_verrouille:
        scr1 = st.session_state.get("score_stat2_p1", 0.0)
        scr2 = st.session_state.get("score_stat2_p2", 0.0)
        tot_s2 = st.session_state.get("score_final_stat2", 0.0)
        
        from datetime import datetime
        timestamp_stat2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 2 SCELLE | Note globale de l'eleve : {tot_s2} / 20")

        # Recuperation des donnees dynamiques calculees
        v_total_n = st.session_state.get("circ_vrai_total_n", 0.0)
        v_max_fr = st.session_state.get("circ_max_freq", 0.0)
        v_min_fr = st.session_state.get("circ_min_freq", 0.0)
        v_labels = st.session_state.get("circ_labels_presents", [])
        v_label_premier = v_labels[0] if len(v_labels) > 0 else "Aucun"
        v_label_dernier = v_labels[-1] if len(v_labels) > 1 else "Aucun"

        # Genere le graphique base64 autonome pour l'extraction
        img_base64_stat2 = ""
        # Generation des lignes dynamiques du tableau HTML
        lignes_tableau_html = ""
        try:
            df_source2 = st.session_state.df_session_tab2.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
            df_source2 = df_source2[(df_source2["Caractere (xi)"].astype(str).str.strip() != "") & (df_source2["Effectif (ni)"].astype(str).str.strip() != "")]
            
            fig_ex2, ax_ex2 = plt.subplots(figsize=(4, 4))
            labels_circ = df_source2["Caractere (xi)"].astype(str).to_numpy()
            sizes_circ = df_source2["Effectif (ni)"].astype(float).to_numpy()
            
            ax_ex2.pie(sizes_circ, labels=labels_circ, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
            ax_ex2.axis('equal')
            plt.tight_layout()
            
            import io, base64
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', dpi=150)
            buf2.seek(0)
            img_base64_stat2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
            plt.close(fig_ex2)
        except Exception:
            img_base64_stat2 = ""

        # Generation des lignes dynamiques du tableau HTML
        lignes_tableau_html = ""
        try:
            for idx, row in st.session_state.df_session_tab2.iterrows():
                xi = str(row["Caractere (xi)"]).strip()
                ni = str(row["Effectif (ni)"]).strip()
                if xi or ni:
                    lignes_tableau_html += f"<tr><td style='text-align:center;'>{xi}</td><td style='text-align:center;'>{ni}</td></tr>"
        except Exception:
            lignes_tableau_html = "<tr><td colspan='2' style='text-align:center;'>Aucune donnee valide</td></tr>"

        # Reconstruction de la structure HTML complete avec variables integrees
        html_export_stat2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 2 - {n_eleve}</title>
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
                .flex-container {{ display: flex; gap: 20px; margin-bottom: 25px; }}
                .flex-child {{ flex: 1; background: white; padding: 15px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p>Filiere numerique securisee &bull; Serie unique et dynamique</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s2}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Diagramme Circulaire</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de validation adaptatif (10 items) : <strong>

                &bull; Partie 1 : Quiz de validation adaptatif (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours numerique (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">Donnees Generales de la Machine a 5 symboles</div>
            <div class="flex-container">
                <div class="flex-child">
                    <p style="font-weight: bold; margin-top: 0; color: #1e3a8a;">Grille des donnees de repartition saisies</p>
                    <table style="margin-bottom: 0; box-shadow: none; border: 1px solid #e2e8f0;">
                        <thead>
                            <tr><th style='text-align:center;'>Caractere (xi)</th><th style='text-align:center;'>Effectif (ni)</th></tr>
                        </thead>
                        <tbody>
                            {lignes_tableau_html}
                        </tbody>
                    </table>
                </div>
                <div class="flex-child" style="text-align: center;">
                    <p style="font-weight: bold; margin-top: 0; color: #1e3a8a;">Diagramme Circulaire de repartition</p>
        """

            # Injection propre conditionnelle de la balise image
        if img_base64_stat2:
            html_export_stat2 += f'<img src="data:image/png;base64,{img_base64_stat2}" alt="Diagramme circulaire" style="max-width: 80%; height: auto; border: 1px solid #e2e8f0; border-radius: 4px;" />'
        else:
            html_export_stat2 += '<p style="color: #64748b; font-size: 13px; padding-top: 40px;">Aucun graphique disponible (tableau vide)</p>'

            # Section métrique dynamique construite séparément
            html_export_stat2 += f"""
                </div>
            </div>

            <div class="sub-title">PARTIE METRIQUE : VALEURS ATTENDUES DE VOTRE REPARTITION</div>
            <table>
                <thead>
                    <tr><th>Indicateur Dynamique</th><th>Valeur Attendue Calculee</th></tr>
                </thead>
                <tbody>
                    <tr><td>Effectif global calcule (N)</td><td>{v_total_n:.0f}</td></tr>
                    <tr><td>Frequence relative maximum (%)</td><td>{v_max_fr:.1f}%</td></tr>
                    <tr><td>Frequence relative minimum (%)</td><td>{v_min_fr:.1f}%</td></tr>
                    <tr><td>Premier caractere de controle (xi)</td><td>{v_label_premier}</td></tr>
                    <tr><td>Dernier caractere de controle (xi)</td><td>{v_label_dernier}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ CIRCULAIRE DYNAMIQUE GENERÉ POUR L'ELEVE</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 50%;">Question posee</th>
                        <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

                enonces_quiz2_html = {
                    "q1": "D'apres votre grille de saisie, quelle est la valeur exacte de l'effectif total N ?",
                    "q2": "Quelle est la valeur de la frequence maximale (%) obtenue dans votre gâteau ?",
                    "q3": "Quelle est la valeur de la frequence minimale (%) calculee par la console ?",
                    "q4": "Quel est l'intitule exact du tout premier caractere (xi) de votre tableau ?",
                    "q5": "Quel est l'intitule exact de la derniere categorie ajoutee a la ligne ?",
                    "q6": "Pour calculer un angle de secteur en degres a partir d'un effectif ni, on applique la formule :",
                    "q7": "Si une categorie de donnees represente une frequence de pile 25%, son angle vaut :",
                    "q8": "La somme de toutes les frequences relatives calculees au sein d'une serie vaut :",
                    "q9": "Le diagramme circulaire est l'outil parfait pour representer graphiquement :",
                    "q10": "Le rapport de l'effectif d'une ligne ni sur l'effectif global N definit sa :"
                }

                attendus_quiz2_txt = {
                    "q1": f"{v_total_n:.0f}",
                    "q2": f"{v_max_fr:.1f}%",
                    "q3": f"{v_min_fr:.1f}%",
                    "q4": f"{v_label_premier}",
                    "q5": f"{v_label_dernier}",
                    "q6": "Angle = (ni / N) * 360",
                    "q7": "90 degres (un quart de cercle)",
                    "q8": "100% (ou 1)",
                    "q9": "Une structure de repartition globale",
                    "q10": "Frequence"
                }

            # Boucle de generation des lignes de la Partie 1 (Quiz)
        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s2_{qk}", "Choisir...")
            attendu = attendus_quiz2_txt[qk]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                    
                    html_export_stat2 += f"""
                    <tr>
                        <td><strong>Q{i}.</strong> {enonces_quiz2_html[qk]}</td>
                        <td style='text-align:center;'>{saisie}</td>
                        <td style='text-align:center;'>{attendu}</td>
                        <td class='{v_class}' style='text-align: center;'>{v_lbl}</td>
                    </tr>"""

                html_export_stat2 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS NUMÉRIQUE</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 50%;">Phrase a trous posee</th>
                        <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu theorique</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

                phrases_trous2_html = {
                    "t1": "1. Le nombre global de donnees collectees dans N vaut :",
                    "t2": "2. Saisissez la frequence maximale lue sans le symbole % :",
                    "t3": "3. Saisissez la frequence minimale lue sans le symbole % :",
                    "t4": "4. L'ecart entre votre frequence max et min s'eleve a :",
                    "t5": "5. L'angle associe a une demi-repartition (50% de N) mesure :",
                    "t6": "6. La totalite des secteurs angulaires d'un disque complet mesure :",
                    "t7": "7. La somme cumulative des frequences calculees doit faire :",
                    "t8": "8. Le diagramme en secteurs represente l'indicateur de la :",
                    "t9": "9. Le coefficient multiplicateur pour obtenir un angle depuis un pourcentage vaut :",
                    "t10": "10. Ce type de graphique est optimal pour des variables qualitatives ou :"
                }

                attendus_trous2_txt = {
                    "t1": f"{v_total_n}",
                    "t2": f"{v_max_fr}",
                    "t3": f"{v_min_fr}",
                    "t4": f"{round(float(v_max_fr - v_min_fr), 1)}",
                    "t5": "180°",
                    "t6": "360°",
                    "t7": "100%",
                    "t8": "Repartition",
                    "t9": "3.6",
                    "t10": "Textuelles"
                }

                # Boucle de generation des lignes de la Partie 2 (Texte a trous)
        for tk, tv in attendus_trous2_txt.items():
            saisie = st.session_state.get(f"stat2_t6_dyn" if tk == "t6" else f"stat2_{tk}_dyn", "Choisir...")
            v_lbl = "CORRECT" if str(saisie).strip() == str(tv).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                
                    html_export_stat2 += f"""
                    <tr>
                        <td>{phrases_trous2_html[tk]}</td>
                        <td style='text-align:center;'>{saisie}</td>
                        <td style='text-align:center;'>{tv}</td>
                        <td class='{v_class}' style='text-align: center;'>{v_lbl}</td>
                    </tr>"""

                html_export_stat2 += """
                </tbody>
            </table>
        </body>
        </html>"""

        # Composant officiel de telechargement Streamlit
        st.download_button(
            label="TELECHARGER LE RAPPORT COMPLET HTML DE L'ATELIER 2",
            data=html_export_stat2,
            file_name=f"Rapport_Atelier2_Complet_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )            

with tab3:
    st.header("Atelier 3 : Analyse Graphique & Courbe d'Evolution")
    
    if "nbr_lignes_tab3" not in st.session_state: st.session_state.nbr_lignes_tab3 = 5
    if "stat3_verrouille" not in st.session_state: st.session_state.stat3_verrouille = False

    col_g3, col_d3 = st.columns([1.2, 1.8])
    with col_g3:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DE COORDONNÉES CARTÉSIENNES</p>", unsafe_allow_html=True)
            st.number_input("Nombre de points de mesure (lignes) :", min_value=1, max_value=30, value=5, key="nbr_lignes_tab3")
            
            if "df_session_tab3" not in st.session_state or len(st.session_state.df_session_tab3) != st.session_state.nbr_lignes_tab3:
                st.session_state.df_session_tab3 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab3, 
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab3
                })
            
            df_edite3 = st.data_editor(st.session_state.df_session_tab3, use_container_width=True, hide_index=True, key="editeur_tab3_unique_key")
            st.session_state.df_session_tab3 = df_edite3
            
            # REPARATION : Le bouton force le recalcul et le rafraichissement immediat de l'ecran
            if st.button("Calculer et tracer le graphique", key="btn_calculer_graph_tab3", use_container_width=True):
                st.rerun()
            
        with st.container(border=True):
            st.markdown("**Console d'analyse geometrique :**")
            st.text(st.session_state.get("stats3_affichage_texte", "Saisissez vos couples de points ordonnes pour tracer la courbe."))
            
    with col_d3:
        st.subheader("Rendu graphique cartésien")
        
        # APPEL SYNCHRONE DE LA NOUVELLE FONCTION MAÎTRESSE
        fig_courbe_evolution = mettre_a_jour_graphique3(st.session_state.df_session_tab3)
        st.pyplot(fig_courbe_evolution, use_container_width=True)
        
    # LE BLOC D'ÉVALUATION SUR 20 POINTS DE L'ATELIER 3
    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 3")

    # APPEL UNIQUE DU QUESTIONNAIRE NETTOYÉ À 10 QUIZ ET 10 TROUS
    res_q3, res_t3 = afficher_questions_statistiques3_dynamiques(
        st.session_state.df_session_tab3, 
        verrouille=st.session_state.get("stat3_verrouille", False)
    )

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires numeriques de l'Atelier 3.", 
        key="check_certif_stat3_officiel_20pts_dyn", 
        disabled=st.session_state.get("stat3_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_stat3_official_20pts_dyn", use_container_width=True, disabled=st.session_state.get("stat3_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            v_total_n = st.session_state.get("graph_vrai_total_n", 0.0)
            v_max_y = st.session_state.get("graph_vrai_max_y", 0.0)
            v_min_y = st.session_state.get("graph_vrai_min_y", 0.0)
            v_amplitude = round(float(v_max_y - v_min_y), 1)

            if v_total_n == 0.0:
                v_total_n, v_max_y, v_min_y, v_amplitude = 45.0, 18.0, 2.0, 16.0

            # 1. Correction automatique du Quiz adaptatif (10 questions x 1.0 pt)
            score_q3 = 0.0
            if st.session_state.get("col_g_quiz_dyn_s3_q1") == f"{v_total_n:.0f}": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q2") == f"{v_max_y:.1f}": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q3") == f"{v_min_y:.1f}": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q4") == f"{v_amplitude:.1f}": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q5") == f"{v_amplitude/2:.1f}": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q6") == "Interpolation lineaire": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q7") == "L'effectif ni / la grandeur mesuree": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q8") == "Son ordonnee ni": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q9") == "Chronologique": score_q3 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s3_q10") == "Frequence relative": score_q3 += 1.0

            # 2. Correction automatique des 10 Selecteurs (10 trous x 1.0 pt)
            score_t3 = 0.0
            if st.session_state.get("stat3_t1") == "Cartesien": score_t3 += 1.0
            if st.session_state.get("stat3_t2") == "Abscisses": score_t3 += 1.0
            if st.session_state.get("stat3_t3") == "Ordonnees": score_t3 += 1.0
            if st.session_state.get("stat3_t4") == "Origine": score_t3 += 1.0
            if st.session_state.get("stat3_t5") == "Nuage de points": score_t3 += 1.0
            if st.session_state.get("stat3_t6") == "Brisee": score_t3 += 1.0
            if st.session_state.get("stat3_t7") == "Croissante": score_t3 += 1.0
            if st.session_state.get("stat3_t8") == "(0,0)": score_t3 += 1.0
            if st.session_state.get("stat3_t9") == "Abscisse": score_t3 += 1.0
            if st.session_state.get("stat3_t10") == "Quantitatifs": score_t3 += 1.0

            st.session_state.score_stat3_p1 = round(score_q3, 1)
            st.session_state.score_stat3_p2 = round(score_t3, 1)
            st.session_state.score_final_stat3 = round(score_q3 + score_t3, 1)
            st.session_state.stat3_verrouille = True
            st.rerun()

    # LE GENERATEUR DU DOCUMENT HTML OFFICIEL APRES LE SCELLE
    if st.session_state.get("stat3_verrouille", False):
        scr1 = st.session_state.get("score_stat3_p1", 0.0)
        scr2 = st.session_state.get("score_stat3_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat3", 0.0)

        v_total_n = st.session_state.get("graph_vrai_total_n", 45.0)
        v_max_y = st.session_state.get("graph_vrai_max_y", 18.0)
        v_min_y = st.session_state.get("graph_vrai_min_y", 2.0)
        v_amplitude = round(float(v_max_y - v_min_y), 1)

        from datetime import datetime, timedelta
        timestamp_stat3 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 3 SCELLE | Note de session : {tot_s} / 20")

        attendus_trous3 = {
            "t1": "Cartesien", "t2": "Abscisses", "t3": "Ordonnees", "t4": "Origine",
            "t5": "Nuage de points", "t6": "Brisee", "t7": "Croissante", "t8": "(0,0)",
            "t9": "Abscisse", "t10": "Quantitatifs"
        }

        html_export_stat3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 3 - {n_eleve}</title>
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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Courbe d'Evolution</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308;">
                &bull; Partie 1 : Quiz de validation cartesiene (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours geometrique (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">VERIFICATION DES GRANDEURS CALCULÉES DE VOTRE COURBE :</div>
            <table>
                <thead>
                    <tr><th>Parametre Cartesien</th><th>Valeur Attendue Exacte</th></tr>
                </thead>
                <tbody>
                    <tr><td>Somme totale des effectifs Y</td><td>{v_total_n:.1f}</td></tr>
                    <tr><td>Ordonnee maximale relevée (Y max)</td><td>{v_max_y:.1f}</td></tr>
                    <tr><td>Ordonnee minimale relevée (Y min)</td><td>{v_min_y:.1f}</td></tr>
                    <tr><td>Amplitude verticale relevee</td><td>{v_amplitude:.1f}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ CARTÉSIEN DYNAMIQUE</div>
            <table>
                <thead>
                    <tr><th>Item</th><th>Saisie Eleve</th><th>Attendu Technique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Injection dynamique des lignes du Quiz 3 dans le HTML
        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s3_{qk}", "Choisir...")
            
            # Generation dynamique de l'attendu unique selon la question associee
            if qk == "q1": attendu = f"{v_total_n:.0f}"
            elif qk == "q2": attendu = f"{v_max_y:.1f}"
            elif qk == "q3": attendu = f"{v_min_y:.1f}"
            elif qk == "q4": attendu = f"{v_amplitude:.1f}"
            elif qk == "q5": attendu = f"{v_amplitude/2:.1f}"
            elif qk == "q6": attendu = "Interpolation lineaire"
            elif qk == "q7": attendu = "L'effectif ni / la grandeur mesuree"
            elif qk == "q8": attendu = "Son ordonnee ni"
            elif qk == "q9": attendu = "Chronologique"
            elif qk == "q10": attendu = "Frequence relative"
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat3 += f"<tr><td>Question {i}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_stat3 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS (10 TROUS)</div>
            <table>
                <thead>
                    <tr><th>Case</th><th>Saisie Eleve</th><th>Attendu theorique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Injection dynamique des 10 trous du cours 3 dans le HTML
        for tk, tv in attendus_trous3.items():
            saisie = st.session_state.get(f"stat3_{tk}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat3 += f"<tr><td>Trou {tk.replace('t','')}</td><td>{saisie}</td><td>{tv}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_stat3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f3 = f"Rapport_Evaluation_Statistiques3_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: nom_f3 = nom_f3.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_stat3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )








with tab4:
    st.header("Atelier 4 : Analyse Statistique & Diagramme a Moustache")
    
    if "nbr_lignes_tab4" not in st.session_state: st.session_state.nbr_lignes_tab4 = 5
    if "stat4_verrouille" not in st.session_state: st.session_state.stat4_verrouille = False

    col_g4, col_d4 = st.columns([1.2, 1.8])
    with col_g4:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DES DONNÉES STATISTIQUES (BOXPLOT)</p>", unsafe_allow_html=True)
            st.number_input("Nombre de lignes de valeurs :", min_value=1, max_value=30, value=5, key="nbr_lignes_tab4")
            
            if "df_session_tab4" not in st.session_state or len(st.session_state.df_session_tab4) != st.session_state.nbr_lignes_tab4:
                st.session_state.df_session_tab4 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab4, 
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab4
                })
            
            df_edite4 = st.data_editor(st.session_state.df_session_tab4, use_container_width=True, hide_index=True, key="editeur_tab4_unique_key")
            st.session_state.df_session_tab4 = df_edite4
            
            if st.button("Calculer et tracer la boite", key="btn_calculer_mous_tab4", use_container_width=True):
                st.rerun()
            
        with st.container(border=True):
            st.markdown("**Indicateurs de position & dispersion :**")
            st.text(st.session_state.get("stats4_affichage_texte", "Saisissez vos valeurs pour lancer l'analyse de dispersion."))
            
    with col_d4:
        st.subheader("Rendu vertical de la boite")
        fig4 = calculer_et_tracer_moustache_matplotlib(st.session_state.df_session_tab4)
        st.pyplot(fig4, use_container_width=True)

    # RACCORDEMENT DU DOUBLE FORMULAIRE ET DU VERROU SUR 20 POINTS DE L'ATELIER 4
    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 4")
    dict_q4, dict_t4 = afficher_questions_statistiques4_dynamiques(st.session_state.df_session_tab4, st.session_state.stat4_verrouille)

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires numeriques de l'Atelier 4.", 
        key="check_certif_stat4_officiel_20pts_dyn", 
        disabled=st.session_state.get("stat4_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_stat4_official_20pts_dyn", use_container_width=True, disabled=st.session_state.get("stat4_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            v_min = st.session_state.get("mous_vrai_min", 4.0)
            v_q1 = st.session_state.get("mous_vrai_q1", 8.0)
            v_med = st.session_state.get("mous_vrai_med", 11.0)
            v_q3 = st.session_state.get("mous_vrai_q3", 14.0)
            v_max = st.session_state.get("mous_vrai_max", 19.0)
            v_iqr = st.session_state.get("mous_vrai_iqr", 6.0)

            # 1. Correction automatique du Quiz adaptatif (10 questions x 1.0 pt)
            score_q4 = 0.0
            if st.session_state.get("col_g_quiz_dyn_s4_q1") == f"{v_min:.2f}": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q2") == f"{v_q1:.2f}": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q3") == f"{v_med:.2f}": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q4") == f"{v_q3:.2f}": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q5") == f"{v_max:.2f}": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q6") == "50% de la population": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q7") == "50% de la population": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q8") == "L'ecart interquartile": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q9") == "Valeur atypique ou aberrante": score_q4 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s4_q10") == "La dispersion et la symetrie d'une serie": score_q4 += 1.0

            # 2. Correction automatique des 10 Selecteurs du cours 4 (10 trous x 1.0 pt)
            score_t4 = 0.0
            if st.session_state.get("stat4_t1") == "Boxplot": score_t4 += 1.0
            if st.session_state.get("stat4_t2") == "Boite": score_t4 += 1.0
            if st.session_state.get("stat4_t3") == "Moustaches": score_t4 += 1.0
            if st.session_state.get("stat4_t4") == "50%": score_t4 += 1.0
            if st.session_state.get("stat4_t5") == "25%": score_t4 += 1.0
            if st.session_state.get("stat4_t6") == "75%": score_t4 += 1.0
            if st.session_state.get("stat4_t7") == "Mediane": score_t4 += 1.0
            if st.session_state.get("stat4_t8") == "Ecart interquartile": score_t4 += 1.0
            if st.session_state.get("stat4_t9") == "Etendue": score_t4 += 1.0
            if st.session_state.get("stat4_t10") == "Quantitatifs": score_t4 += 1.0

            st.session_state.score_stat4_p1 = round(score_q4, 1)
            st.session_state.score_stat4_p2 = round(score_t4, 1)
            st.session_state.score_final_stat4 = round(score_q4 + score_t4, 1)
            st.session_state.stat4_verrouille = True
            st.rerun()

    # GENERATEUR DU DOCUMENT HTML OFFICIEL APRÈS LE SCELLE
    if st.session_state.get("stat4_verrouille", False):
        scr1 = st.session_state.get("score_stat4_p1", 0.0)
        scr2 = st.session_state.get("score_stat4_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat4", 0.0)

        v_min = st.session_state.get("mous_vrai_min", 4.0)
        v_q1 = st.session_state.get("mous_vrai_q1", 8.0)
        v_med = st.session_state.get("mous_vrai_med", 11.0)
        v_q3 = st.session_state.get("mous_vrai_q3", 14.0)
        v_max = st.session_state.get("mous_vrai_max", 19.0)

        from datetime import datetime, timedelta
        timestamp_stat4 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 4 SCELLE | Note de session : {tot_s} / 20")

        attendus_trous4 = {
            "t1": "Boxplot", "t2": "Boite", "t3": "Moustaches", "t4": "50%", "t5": "25%",
            "t6": "75%", "t7": "Mediane", "t8": "Ecart interquartile", "t9": "Etendue", "t10": "Quantitatifs"
        }

        html_export_stat4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 4 - {n_eleve}</title>
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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Diagramme a Moustache</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308;">
                &bull; Partie 1 : Quiz de validation adaptatif (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours numerique (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE METRIQUE : VALEURS ATTENDUES DE VOTRE DISPERSION</div>
            <table>
                <thead>
                    <tr><th>Repere Geometrique</th><th>Valeur Unique Calculee</th></tr>
                </thead>
                <tbody>
                    <tr><td>Minimum (Moustache gauche)</td><td>{v_min:.2f}</td></tr>
                    <tr><td>Premier Quartile (Q1)</td><td>{v_q1:.2f}</td></tr>
                    <tr><td>Mediane (Trait central)</td><td>{v_med:.2f}</td></tr>
                    <tr><td>Troisieme Quartile (Q3)</td><td>{v_q3:.2f}</td></tr>
                    <tr><td>Maximum (Moustache droite)</td><td>{v_max:.2f}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ DYNAMIQUE</div>
            <table>
                <thead>
                    <tr><th>Item</th><th>Saisie Eleve</th><th>Attendu Technique Unique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s4_{qk}", "Choisir...")
            
            if qk == "q1": attendu = f"{v_min:.2f}"
            elif qk == "q2": attendu = f"{v_q1:.2f}"
            elif qk == "q3": attendu = f"{v_med:.2f}"
            elif qk == "q4": attendu = f"{v_q3:.2f}"
            elif qk == "q5": attendu = f"{v_max:.2f}"
            elif qk == "q6": attendu = "50% de la population"
            elif qk == "q7": attendu = "50% de la population"
            elif qk == "q8": attendu = "L'ecart interquartile"
            elif qk == "q9": attendu = "Valeur atypique ou aberrante"
            elif qk == "q10": attendu = "La dispersion et la symetrie d'une serie"
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat4 += f"<tr><td>Question {i}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_stat4 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS DYNAMIQUE (10 TROUS)</div>
            <table>
                <thead>
                    <tr><th>Case</th><th>Saisie Eleve</th><th>Attendu theorique Unique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for tk, tv in attendus_trous4.items():

            saisie = st.session_state.get(f"stat4_{tk}_dyn", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat4 += f"<tr><td>Trou {tk.replace('t','')}</td><td>{saisie}</td><td>{tv}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_stat4 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse statistique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f4 = f"Rapport_Evaluation_Statistiques4_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f4 = nom_f4.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 4 SUR VOTRE ORDINATEUR",
            data=html_export_stat4,
            file_name=f"{nom_f4}.html",
            mime="text/html",
            use_container_width=True
        )






with tab5:
    st.header("Atelier 5 : Analyse Statistique & Histogramme de Classes")
    
    if "nbr_lignes_tab5" not in st.session_state: st.session_state.nbr_lignes_tab5 = 4
    if "stat5_verrouille" not in st.session_state: st.session_state.stat5_verrouille = False

    col_g5, col_d5 = st.columns([1.3, 1.7])

    with col_g5:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DES CLASSES CONTINUES [Borne Inf ; Borne Sup[</p>", unsafe_allow_html=True)
            st.number_input("Nombre de classes necessaires (lignes) :", min_value=1, max_value=20, value=4, key="nbr_lignes_tab5")
            
            if "df_session_tab5" not in st.session_state or len(st.session_state.df_session_tab5) != st.session_state.nbr_lignes_tab5:
                st.session_state.df_session_tab5 = pd.DataFrame({
                    "Borne Inf": [""] * st.session_state.nbr_lignes_tab5,
                    "Borne Sup": [""] * st.session_state.nbr_lignes_tab5,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab5
                })
            
            df_edite5 = st.data_editor(st.session_state.df_session_tab5, use_container_width=True, hide_index=True, key="editeur_tab5_unique_key")
            st.session_state.df_session_tab5 = df_edite5
            
            if st.button("Calculer et tracer l'histogramme", key="btn_calculer_hist_tab5", use_container_width=True):
                st.rerun()

            if st.button("Reinitialiser la grille   ", key="btn_reset_tab5", use_container_width=True):
                st.session_state.df_session_tab5 = pd.DataFrame({
                    "Borne Inf": [""] * st.session_state.nbr_lignes_tab5,
                    "Borne Sup": [""] * st.session_state.nbr_lignes_tab5,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab5
                })
                st.rerun()
            
        with st.container(border=True):
            st.markdown("**Console d'analyse des variables continues :**")
            st.text(st.session_state.get("stats5_affichage_texte", "Saisissez vos bornes et effectifs pour analyser les amplitudes."))
            
    with col_d5:
        st.subheader("Rendu graphique de l'histogramme")
        fig5 = calculer_et_tracer_histogramme_matplotlib(st.session_state.df_session_tab5)
        st.pyplot(fig5, use_container_width=True)

    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 5")

    dict_q5, dict_t5 = afficher_questions_statistiques5_dynamiques(
        st.session_state.df_session_tab5, 
        verrouille=st.session_state.stat5_verrouille
    )

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires numeriques de l'Atelier 5.", 
        key="check_certif_stat5_officiel_20pts_dyn", 
        disabled=st.session_state.stat5_verrouille
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_stat5_official_20pts_dyn", use_container_width=True, disabled=st.session_state.stat5_verrouille):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            v_total_n = st.session_state.get("hist_vrai_total_n", 60.0)
            v_nbr_c = st.session_state.get("hist_vrai_nbr_classes", 4.0)
            v_max_ni = st.session_state.get("hist_vrai_max_ni", 22.0)

            score_q5 = 0.0
            if st.session_state.get("col_g_quiz_dyn_s5_q1") == f"{v_total_n:.0f}": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q2") == f"{v_nbr_c:.0f}": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q3") == f"{v_max_ni:.0f}": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q4") == "La soustraction : b - a": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q5") == "La demi-somme : (a + b) / 2": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q6") == "Quantitatives continues regroupees en intervalles": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q7") == "La densite d'effectif (ni / amplitude)": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q8") == "L'effectif ni de la classe (ou sa frequence)": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q9") == "L'effectif ni de la classe": score_q5 += 1.0
            if st.session_state.get("col_g_quiz_dyn_s5_q10") == "Classe modale": score_q5 += 1.0

            score_t5 = 0.0
            if st.session_state.get("stat5_t1") == "Continues": score_t5 += 1.0
            if st.session_state.get("stat5_t2") == "Classes": score_t5 += 1.0
            if st.session_state.get("stat5_t3") == "Amplitude": score_t5 += 1.0
            if st.session_state.get("stat5_t4") == "Centre": score_t5 += 1.0
            if st.session_state.get("stat5_t5") == "Densite": score_t5 += 1.0
            if st.session_state.get("stat5_t6") == "Modal": score_t5 += 1.0
            if st.session_state.get("stat5_t7") == "Aire du rectangle": score_t5 += 1.0
            if st.session_state.get("stat5_t8") == "Inclus": score_t5 += 1.0
            if st.session_state.get("stat5_t9") == "Exclu": score_t5 += 1.0
            if st.session_state.get("stat5_t10") == "L'effectif total N": score_t5 += 1.0

            st.session_state.score_stat5_p1 = round(score_q5, 1)
            st.session_state.score_stat5_p2 = round(score_t5, 1)
            st.session_state.score_final_stat5 = round(score_q5 + score_t5, 1)
            st.session_state.stat5_verrouille = True
            st.rerun()

    if st.session_state.get("stat5_verrouille", False):
        scr1 = st.session_state.get("score_stat5_p1", 0.0)
        scr2 = st.session_state.get("score_stat5_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat5", 0.0)

        v_total_n = st.session_state.get("hist_vrai_total_n", 60.0)
        v_nbr_c = st.session_state.get("hist_vrai_nbr_classes", 4.0)
        v_max_ni = st.session_state.get("hist_vrai_max_ni", 22.0)

        from datetime import datetime, timedelta
        timestamp_stat5 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 5 SCELLE | Note de session unique : {tot_s} / 20")

        attendus_trous5 = {
            "t1": "Continues", "t2": "Classes", "t3": "Amplitude", "t4": "Centre", "t5": "Densite",
            "t6": "Modal", "t7": "Aire du rectangle", "t8": "Inclus", "t9": "Exclu", "t10": "L'effectif total N"
        }

        html_export_stat5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 5 - {n_eleve}</title>
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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Histogramme Continu</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308;">
                &bull; Partie 1 : Quiz de validation (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">VERIFICATION DES GRANDEURS CALCULÉES DE VOTRE APPRENTISSAGE :</div>
            <table>
                <thead>
                    <tr><th>Indicateur Continu</th><th>Valeur Attendue Exacte</th></tr>
                </thead>
                <tbody>
                    <tr><td>Effectif global total (N)</td><td>{v_total_n:.0f}</td></tr>
                    <tr><td>Nombre d'intervalles (rectangles)</td><td>{v_nbr_c:.0f}</td></tr>
                    <tr><td>Effectif brut maximum saisi (ni max)</td><td>{v_max_ni:.0f}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ CONTINU</div>
            <table>
                <thead>
                    <tr><th>Item</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu Technique Unique</th><th style="text-align:center;">Verdict</th></tr>
                </thead>
                <tbody>
        """

        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s5_{qk}", "Choisir...")
            
            if qk == "q1": attendu = f"{v_total_n:.0f}"
            elif qk == "q2": attendu = f"{v_nbr_c:.0f}"
            elif qk == "q3": attendu = f"{v_max_ni:.0f}"
            elif qk == "q4": attendu = "La soustraction : b - a"
            elif qk == "q5": attendu = "La demi-somme : (a + b) / 2"
            elif qk == "q6": attendu = "Quantitatives continues regroupees en intervalles"
            elif qk == "q7": attendu = "La densite d'effectif (ni / amplitude)"
            elif qk == "q8": attendu = "L'effectif ni de la classe (ou sa frequence)"
            elif qk == "q9": attendu = "L'effectif ni de la classe"
            elif qk == "q10": attendu = "Classe modale"
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat5 += f"<tr><td>Question {i}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_stat5 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS DYNAMIQUE (10 TROUS)</div>
            <table>
                <thead>
                    <tr><th>Case</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu theorique Unique</th><th style="text-align:center;">Verdict</th></tr>
                </thead>
                <tbody>
        """

        for tk, tv in attendus_trous5.items():
            saisie = st.session_state.get(f"stat5_{tk}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat5 += f"<tr><td>Trou {tk.replace('t','')}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{tv}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_stat5 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse statistique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f5 = f"Rapport_Evaluation_Statistiques5_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: nom_f5 = nom_f5.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 5 SUR VOTRE ORDINATEUR",
            data=html_export_stat5,
            file_name=f"{nom_f5}.html",
            mime="text/html",
            use_container_width=True
        )







