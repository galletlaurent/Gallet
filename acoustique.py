# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application acoustique",
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
st.title("Application acoustique")
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
    "Généralités sur le son",
    "Fréquence et période d'une onde sonore",
    "Loi d'addidition",
    "Loi de distance",
    "Intensité acoustique",
    "Puissance acoustique",
    "Les dangers et les protections",
    "Exemple de protection acoustique",
    ""
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]
tab7 = onglets[7]
tab8 = onglets[8]

def afficher_questions_loi_distance_dynamiques(verrouille=False):
    import streamlit as st

    ordre_fixe_tab4 = [
        {"id": "s4_1", "q": "À chaque fois que l'on double la distance d'une source, le niveau sonore baisse de :", "options": ["6 dB", "3 dB", "10 dB"], "rep": "6 dB"},
        {"id": "s4_2", "q": "Une source émet 90 dB à 1 m. Quel est le niveau d'intensité mesuré à 2 m ?", "options": ["84 dB", "87 dB", "45 dB"], "rep": "84 dB"},
        {"id": "s4_3", "q": "Si le niveau à 1 m d'un marteau-piqueur vaut 100 dB, quel est le niveau mesuré à 4 m ?", "options": ["88 dB", "94 dB", "92 dB"], "rep": "88 dB"},
        {"id": "s4_4", "q": "Quel phénomène physique explique cette baisse d'intensité sonore lors de l'éloignement ?", "options": ["L'atténuation géométrique", "L'effet de masque", "La réfraction thermique"], "rep": "L'atténuation géométrique"},
        {"id": "s4_5", "q": "Si on passe d'une distance de 2 mètres à 8 mètres, combien de fois la distance a-t-elle doublé ?", "options": ["2 fois", "3 fois", "4 fois"], "rep": "2 fois"},
        {"id": "s4_6", "q": "Pour un son de 100 dB à 1 m, la baisse totale cumulée à une distance de 8 m vaut :", "options": ["18 dB", "12 dB", "6 dB"], "rep": "18 dB"},
        {"id": "s4_7", "q": "L'atténuation géométrique en champ libre est d'autant plus efficace que :", "options": ["L'auditeur s'éloigne de la source", "La source est très proche", "Le milieu est un solide"], "rep": "L'auditeur s'éloigne de la source"},
        {"id": "s4_8", "q": "Quelle industrie a publié la charte sur les bruits de chantier citée en référence ?", "options": ["Fédération Nationale des Travaux Publics", "Aviation Civile", "SNCF Réseau"], "rep": "Fédération Nationale des Travaux Publics"},
        {"id": "s4_9", "q": "Si la distance à la source est divisée par deux (rapprochement), le niveau sonore :", "options": ["Augmente de 6 dB", "Diminue de 6 dB", "Reste strictement identique"], "rep": "Augmente de 6 dB"},
        {"id": "s4_10", "q": "L'atténuation de 6 dB par doublement de distance présuppose une propagation en :", "options": ["Champ libre sans obstacle", "Milieu clos confiné", "Tuyau métallique étroit"], "rep": "Champ libre sans obstacle"}
    ]

    st.session_state.ordre_quiz_son_tab4 = ordre_fixe_tab4

    col_double_quiz_son4, col_double_trous_son4 = st.columns(2)

    with col_double_quiz_son4:
        st.markdown("##### Quiz sur la loi de distance (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"son_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_son4:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. L'éloignement par rapport à un point d'émission sonore provoque une")
        with c2: st.selectbox("", ["Choisir...", "atténuation", "amplification", "distorsion"], key="son_t1_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La dilution de l'énergie sur une sphère croissante est une loi de")
        with c4: st.selectbox("", ["Choisir...", "distance", "masque", "fréquence"], key="son_t2_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Chaque fois que la distance entre la source et la mesure vient à")
        with c6: st.selectbox("", ["Choisir...", "doubler", "tripler", "stagner"], key="son_t3_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. L'affaiblissement réglementaire de l'intensité acoustique vaut alors")
        with c8: st.selectbox("", ["Choisir...", "6 dB", "3 dB", "12 dB"], key="son_t4_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. À un mètre de distance, un engin de chantier type marteau-piqueur émet")
        with c10: st.selectbox("", ["Choisir...", "100 dB", "60 dB", "80 dB"], key="son_t5_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. En s'éloignant de la machine pour se placer à 2 mètres, le niveau tombe à")
        with c12: st.selectbox("", ["Choisir...", "94 dB", "97 dB", "106 dB"], key="son_t6_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. En poursuivant le recul jusqu'à un écart de 4 mètres, la valeur est de")
        with c14: st.selectbox("", ["Choisir...", "88 dB", "91 dB", "82 dB"], key="son_t7_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Enfin, à une distance de 8 mètres de l'émetteur, le sonomètre affiche")
        with c16: st.selectbox("", ["Choisir...", "82 dB", "85 dB", "76 dB"], key="son_t8_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La réduction totale d'intensité mesurée à 8 mètres de la source vaut")
        with c18: st.selectbox("", ["Choisir...", "18 dB", "6 dB", "24 dB"], key="son_t9_tab4_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Cette décroissance géométrique suppose l'absence totale de tout")
        with c20: st.selectbox("", ["Choisir...", "obstacle", "milieu", "récepteur"], key="son_t10_tab4_final", disabled=verrouille, label_visibility="collapsed")
        
    return


def afficher_questions_loi_addition_dynamiques(verrouille=False):
    import streamlit as st

    ordre_fixe_tab3 = [
        {"id": "s3_1", "q": "Peut-on additionner directement les valeurs en décibels de deux sources distinctes ?", "options": ["Non, l'échelle est logarithmique", "Oui, l'addition est linéaire", "Seulement si elles dépassent 100 dB"], "rep": "Non, l'échelle est logarithmique"},
        {"id": "s3_2", "q": "Deux voitures émettent chacune 60 dB. Quel est le niveau sonore total mesuré ?", "options": ["63 dB", "120 dB", "60 dB"], "rep": "63 dB"},
        {"id": "s3_3", "q": "Lorsque deux sources identiques fonctionnent ensemble, l'augmentation du niveau sonore vaut :", "options": ["3 dB", "6 dB", "2 dB"], "rep": "3 dB"},
        {"id": "s3_4", "q": "On cumule une source de 50 dB et une source de 70 dB (écart de 20 dB). Le niveau résultant vaut environ :", "options": ["70 dB", "120 dB", "73 dB"], "rep": "70 dB"},
        {"id": "s3_5", "q": "Selon la fiche de cours, à partir de quel écart en dB la source faible est-elle masquée ?", "options": ["Plus de 10 dB", "Plus de 3 dB", "Plus de 50 dB"], "rep": "Plus de 10 dB"},
        {"id": "s3_6", "q": "Si quatre sources identiques de 60 dB fonctionnent en même temps, le niveau monte de :", "options": ["6 dB", "12 dB", "3 dB"], "rep": "6 dB"},
        {"id": "s3_7", "q": "Un cumul de 80 dB et de 80 dB donne un niveau total de :", "options": ["83 dB", "160 dB", "80 dB"], "rep": "83 dB"},
        {"id": "s3_8", "q": "Dans l'exemple du cours, quelle source masque totalement le bruit de la voiture de 60 dB ?", "options": ["Le camion de 78 dB", "L'oscilloscope", "Le sonomètre"], "rep": "Le camion de 78 dB"},
        {"id": "s3_9", "q": "Une augmentation de 3 dB correspond physiquement à un doublement de la puissance acoustique de la source :", "options": ["Vrai", "Faux", "Seulement dans le vide"], "rep": "Vrai"},
        {"id": "s3_10", "q": "Si on coupe l'une des deux sources identiques qui émettaient ensemble, le niveau sonore :", "options": ["Baisse de 3 dB", "Divise sa valeur par deux", "Reste inchangé"], "rep": "Baisse de 3 dB"}
    ]

    st.session_state.ordre_quiz_son_tab3 = ordre_fixe_tab3

    col_double_quiz_son3, col_double_trous_son3 = st.columns(2)

    with col_double_quiz_son3:
        st.markdown("##### Quiz sur les lois d'addition (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"son_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_son3:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le niveau sonore exprimé en décibels suit une progression de nature")
        with c2: st.selectbox("", ["Choisir...", "logarithmique", "linéaire", "proportionnelle"], key="son_t1_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Il est impossible d'effectuer sur les niveaux en dB une simple")
        with c4: st.selectbox("", ["Choisir...", "addition", "soustraction", "conversion"], key="son_t2_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Lorsque l'on cumule deux sources acoustiques identiques, le niveau monte de")
        with c6: st.selectbox("", ["Choisir...", "3 dB", "6 dB", "10 dB"], key="son_t3_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Une source de 60 dB ajoutée à une autre source de 60 dB produit un total de")
        with c8: st.selectbox("", ["Choisir...", "63 dB", "120 dB", "66 dB"], key="son_t4_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le doublement de l'intensité d'une source induit un apport fixe de plus")
        with c10: st.selectbox("", ["Choisir...", "3 dB", "0 dB", "30 dB"], key="tab3_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Si deux sources présentent une différence de niveau supérieure à 10")
        with c12: st.selectbox("", ["Choisir...", "dB", "Hz", "m"], key="son_t6_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Dans cette configuration d'écart important, la source faible se retrouve")
        with c14: st.selectbox("", ["Choisir...", "masquée", "amplifiée", "doublée"], key="son_t7_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le niveau global final s'aligne alors sur la valeur de la source la plus")
        with c16: st.selectbox("", ["Choisir...", "puissante", "faible", "aiguë"], key="son_t8_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le cumul d'une voiture de 60 dB et d'un camion de 78 dB est égal à")
        with c18: st.selectbox("", ["Choisir...", "78 dB", "138 dB", "81 dB"], key="son_t9_tab3_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Ce phénomène d'absorption sonore s'appelle l'effet de masque")
        with c20: st.selectbox("", ["Choisir...", "acoustique", "lumineux", "périodique"], key="son_t10_tab3_final", disabled=verrouille, label_visibility="collapsed")
        
    return



def afficher_questions_frequence_periode_dynamiques(verrouille=False):
    import streamlit as st

    ordre_fixe_tab2 = [
        {"id": "s2_1", "q": "Comment définit-on graphiquement ou physiquement la période T d'une onde ?", "options": ["Le plus petit motif qui se répète", "Le nombre de motifs par seconde", "La distance parcourue par le son"], "rep": "Le plus petit motif qui se répète"},
        {"id": "s2_2", "q": "Quelle est l'unité légale de la période T dans le système international ?", "options": ["seconde (s)", "hertz (Hz)", "mètre (m)"], "rep": "seconde (s)"},
        {"id": "s2_3", "q": "Quelle grandeur représente le nombre de périodes se répétant en une seconde ?", "options": ["La fréquence F", "La longueur d'onde", "La célérité C"], "rep": "La fréquence F"},
        {"id": "s2_4", "q": "Une onde possède une période T de 0,02 s. Calculer sa fréquence F en Hz :", "options": ["50 Hz", "20 Hz", "500 Hz"], "rep": "50 Hz"},
        {"id": "s2_5", "q": "Si deux signaux sinusoïdaux ont leurs sommets parfaitement alignés verticalement, ils sont dits :", "options": ["en phase", "en opposition de phase", "en quadrature"], "rep": "en phase"},
        {"id": "s2_6", "q": "La longueur d'onde se note par la lettre grecque :", "options": ["lambda", "tau", "phi"], "rep": "lambda"},
        {"id": "s2_7", "q": "Quelle est l'unité de mesure de la longueur d'onde dans le système international ?", "options": ["mètre (m)", "seconde (s)", "hertz (Hz)"], "rep": "mètre (m)"},
        {"id": "s2_8", "q": "Quelle est l'expression mathématique exacte reliant lambda, la célérité C et la fréquence F ?", "options": ["lambda = C / F", "lambda = C * F", "lambda = F / C"], "rep": "lambda = C / F"},
        {"id": "s2_9", "q": "Calculer la longueur d'onde dans l'air (C = 340 m/s) d'un son de fréquence F = 170 Hz :", "options": ["2 m", "0,5 m", "58 g"], "rep": "2 m"},
        {"id": "s2_10", "q": "Lors de l'expérience, la longueur d'onde correspond à la plus petite distance d permettant de retrouver :", "options": ["des signaux de nouveau en phase", "des signaux de forme carrée", "une annulation du signal"], "rep": "des signaux de nouveau en phase"}
    ]

    st.session_state.ordre_quiz_son_tab2 = ordre_fixe_tab2

    col_double_quiz_son, col_double_trous_son = st.columns(2)

    with col_double_quiz_son:
        st.markdown("##### Quiz sur les propriétés périodiques (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"son_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_son:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le motif temporel élémentaire le plus court se répétant à l'identique est la")
        with c2: st.selectbox("", ["Choisir...", "période", "fréquence", "amplitude"], key="son_t1_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le nombre d'oscillations complètes effectuées par l'onde en une seconde est la")
        with c4: st.selectbox("", ["Choisir...", "fréquence", "célérité", "longueur"], key="son_t2_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'unité hertz (Hz) sert de référence standard pour exprimer la valeur de la")
        with c6: st.selectbox("", ["Choisir...", "fréquence", "période", "distance"], key="son_t3_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La relation mathématique fondamentale liant F et T s'écrit sous la forme F = 1 /")
        with c8: st.selectbox("", ["Choisir...", "T", "lambda", "C"], key="son_t4_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La distance parcourue par l'onde sonore pendant une période T entière est la")
        with c10: st.selectbox("", ["Choisir...", "longueur d'onde", "célérité", "période"], key="son_t5_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. La grandeur spatiale lambda s'exprime légalement avec l'unité du")
        with c12: st.selectbox("", ["Choisir...", "mètre", "seconde", "hertz"], key="son_t6_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Lorsque deux microphones reçoivent simultanément les sommets, les courbes sont en")
        with c14: st.selectbox("", ["Choisir...", "phase", "opposition", "quadrature"], key="son_t7_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Pour mesurer lambda, on cherche le plus petit écart d ramenant les signaux en")
        with c16: st.selectbox("", ["Choisir...", "phase", "opposition", "zéro"], key="son_t8_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La formule de structure spatio-temporelle s'énonce mathématiquement lambda = C /")
        with c18: st.selectbox("", ["Choisir...", "F", "T", "m"], key="son_t9_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Dans cette équation, la lettre C représente la vitesse appelée aussi")
        with c20: st.selectbox("", ["Choisir...", "célérité", "fréquence", "périodicité"], key="son_t10_tab2_final", disabled=verrouille, label_visibility="collapsed")
        
    return

def afficher_questions_generalites_son_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable mis à jour pour l'Atelier 1 Acoustique
    ordre_fixe_son = [
        {"id": "s1_1", "q": "Quelle est la gamme de fréquences audibles par l'oreille humaine ?", "options": ["20 Hz à 20 000 Hz", "0 Hz à 20 Hz", "Au-delà de 20 kHz"], "rep": "20 Hz à 20 000 Hz"},
        {"id": "s1_2", "q": "Comment qualifie-t-on les sons dont la fréquence est inférieure à 20 Hz ?", "options": ["Infra-sons", "Ultra-sons", "Sons aigus"], "rep": "Infra-sons"},
        {"id": "s1_3", "q": "Dans quelle sous-gamme audible se situent les fréquences de 20 Hz à 200 Hz ?", "options": ["Sons graves", "Sons médiums", "Sons aigus"], "rep": "Sons graves"},
        {"id": "s1_4", "q": "Quelle est la nature physique de l'onde sonore ?", "options": ["Une onde mécanique progressive", "Une onde électromagnétique", "Une onde lumineuse"], "rep": "Une onde mécanique progressive"},
        {"id": "s1_5", "q": "Dans quel milieu la vitesse du son (célérité C) est-elle généralement la plus élevée ?", "options": ["Les solides", "Les liquides", "Les gaz"], "rep": "Les solides"},
        {"id": "s1_6", "q": "Quelle est la valeur de la célérité du son dans l'air à 20 degrés Celsius ?", "options": ["340 m/s", "260 m/s", "1 460 m/s"], "rep": "340 m/s"},
        {"id": "s1_7", "q": "Quelle est la célérité du son mesurée dans l'eau douce ?", "options": ["1 460 m/s", "930 m/s", "5 000 m/s"], "rep": "1 460 m/s"},
        {"id": "s1_8", "q": "Quel appareil utilise-t-on pour mesurer le niveau d'intensité sonore ?", "options": ["Le sonomètre", "Le pH-mètre", "Le thermomètre"], "rep": "Le sonomètre"},
        {"id": "s1_9", "q": "Quelle notation symbolise le niveau d'intensité sonore mesuré ?", "options": ["L_dB", "Cm", "C"], "rep": "L_dB"},
        {"id": "s1_10", "q": "Quelle opération obligatoire doit subir l'appareil avant toute utilisation ?", "options": ["Être étalonné et réglé", "Être nettoyé à l'eau", "Être chauffé à 600 °C"], "rep": "Être étalonné et réglé"}
    ]

    st.session_state.ordre_quiz_son_tab1 = ordre_fixe_son

    col_double_quiz_son, col_double_trous_son = st.columns(2)

    with col_double_quiz_son:
        st.markdown("##### Quiz sur les propriétés acoustiques (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_son, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"son_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_son:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Les limites d'audition humaine s'étendent de 20 Hz à 20")
        with c2: st.selectbox("", ["Choisir...", "kHz", "MHz", "Hz"], key="son_t1_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Les fréquences situées au-dessus de 20 000 Hz correspondent aux")
        with c4: st.selectbox("", ["Choisir...", "ultra-sons", "infra-sons", "médiums"], key="son_t2_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La zone audible intermédiaire de 200 Hz à 2 000 Hz est celle des sons")
        with c6: st.selectbox("", ["Choisir...", "médiums", "graves", "aigus"], key="son_t3_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Pour se déplacer, l'onde acoustique doit obligatoirement traverser un")
        with c8: st.selectbox("", ["Choisir...", "milieu", "vide complet", "champ magnétique"], key="son_t4_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La vitesse globale de déplacement de l'onde est appelée sa")
        with c10: st.selectbox("", ["Choisir...", "célérité", "densité", "molarité"], key="son_t5_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. La célérité de l'onde sonore est physiquement maximale au sein des")
        with c12: st.selectbox("", ["Choisir...", "solides", "liquides", "gaz"], key="son_t6_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Dans un milieu gazeux comme l'air, la vitesse de l'onde vaut")
        with c14: st.selectbox("", ["Choisir...", "340 m/s", "260 m/s", "5 000 m/s"], key="son_t7_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le niveau d'intensité d'un son ambiant se mesure à l'aide d'un")
        with c16: st.selectbox("", ["Choisir...", "sonomètre", "spectromètre", "chromatographe"], key="son_t8_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'unité réglementaire affichée sur l'écran du dispositif est le")
        with c18: st.selectbox("", ["Choisir...", "décibel", "hertz", "gramme"], key="son_t9_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Avant chaque mesure technique, l'appareil doit impérativement être")
        with c20: st.selectbox("", ["Choisir...", "étalonné", "nettoyé", "dilué"], key="son_t10_tab1_final", disabled=verrouille, label_visibility="collapsed")
        
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
    st.header("Généralités sur le son")
    st.caption("Nature, domaines de fréquences, propagation et mesure de l'intensité acoustique")

    # --- SECTION 1 : L'OREILLE HUMAINE ---
    st.subheader("1. L'oreille humaine")
    st.write(
        "L'oreille humaine entend les sons sur une gamme de fréquence allant "
        "**de 20 Hz à 20 000 Hz (20 kHz)**."
    )
    
    # Présentation structurée du tableau des domaines de fréquences
    col_dom_1, col_dom_2, col_dom_3 = st.columns(3)
    with col_dom_1:
        st.markdown("**De 0 Hz à 20 Hz**")
        st.write("Sons inaudibles")
        st.write("Infra-sons")
    with col_dom_2:
        st.markdown("**De 20 Hz à 20 000 Hz**")
        st.write("Sons audibles")
        st.write("- De 20 Hz à 200 Hz : Sons graves")
        st.write("- De 200 Hz à 2 000 Hz : Sons médiums")
        st.write("- De 2 000 Hz à 20 kHz : Sons aigus")
    with col_dom_3:
        st.markdown("**Au-delà de 20 kHz**")
        st.write("Sons inaudibles")
        st.write("Ultra-sons")

    st.write("---")

    # --- SECTION 2 : LA PROPAGATION DU SON ---
    st.subheader("2. La propagation du son")
    
    col_prop_g, col_prop_d = st.columns([0.55, 0.45])
    
    with col_prop_g:
        st.write(
            "Le son est une onde qui a pour origine un émetteur, il se propage à travers "
            "un milieu (gaz, liquide ou solide) avant d'atteindre un récepteur."
        )
        st.write(
            "La vitesse de déplacement, appelée aussi **célérité C**, dépend du milieu "
            "dans lequel se propage le son."
        )
        st.write(
            "Elle est **plus élevée dans les solides** que dans les liquides, et plus élevée "
            "dans les liquides que dans les gaz."
        )
        
    with col_prop_d:
        st.markdown("**Les différentes valeurs de la célérité**")
        st.write("*Milieux gazeux :*")
        st.write("- Dioxyde de carbone : 260 m/s")
        st.write("- Oxygène : 320 m/s")
        st.write("- Air : 340 m/s")
        st.write("- Hélium : 930 m/s")
        st.write("*Milieux liquides :*")
        st.write("- Hydrogène : 1 270 m/s")
        st.write("- Mercure : 1 450 m/s")
        st.write("- Eau douce : 1 460 m/s")
        st.write("*Milieux solides :*")
        st.write("- Bois de pin : 3 320 m/s")
        st.write("- Acier : 5 000 m/s")
        st.write("- Verre : 5 500 m/s")
        st.write("- Granite : 5 950 m/s")

    st.write("---")

    # --- SECTION 3 : LA MESURE DU NIVEAU D'INTENSITÉ ACOUSTIQUE ---
    st.subheader("3. La mesure du niveau d'intensité acoustique")
    
    st.write(
        "Le **sonomètre** est un appareil qui permet de mesurer le niveau d'intensité sonore."
    )
    st.write(
        "Le niveau d'intensité sonore se note **L_dB** (exprimé en décibels)."
    )
    
    st.info(
        "Le sonomètre, comme tout appareil de mesure, doit être étalonné et réglé avant toute utilisation."
    )

    if "vin_verrouille_tab1" not in st.session_state:
        st.session_state.vin_verrouille_tab1 = False

    verrou_at1 = st.session_state.vin_verrouille_tab1

    # Appel direct et propre de la fonction d'affichage des questions acoustiques
    try:
        afficher_questions_generalites_son_dynamiques(verrouille=verrou_at1)
    except NameError:
        pass

    st.write("---")
    st.subheader("Généralités sur les propriétés acoustiques")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_son_final_net", 
        disabled=verrou_at1
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ACOUSTIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_son1_official_net", use_container_width=True, disabled=verrou_at1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_son_tab1" in st.session_state:
                for q_item in st.session_state.ordre_quiz_son_tab1:
                    reponse_eleve = st.session_state.get(f"son_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction des Textes à trous mis à jour pour l'Acoustique (10 points)
            score_t1 = sum([
                st.session_state.get("son_t1_tab1_final") == "kHz",
                st.session_state.get("son_t2_tab1_final") == "ultra-sons",
                st.session_state.get("son_t3_tab1_final") == "médiums",
                st.session_state.get("son_t4_tab1_final") == "milieu",
                st.session_state.get("son_t5_tab1_final") == "célérité",
                st.session_state.get("son_t6_tab1_final") == "solides",
                st.session_state.get("son_t7_tab1_final") == "340 m/s",
                st.session_state.get("son_t8_tab1_final") == "sonomètre",
                st.session_state.get("son_t9_tab1_final") == "décibel",
                st.session_state.get("son_t10_tab1_final") == "étalonné"
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

        st.success(f"ATELIER ACOUSTIQUE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_son = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Acoustique Généralités - {n_eleve}</title>
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
                <p>Atelier 1 : Généralités et propagation des ondes sonores</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Propriétés Acoustiques : <strong>{scr1:.1f} / 10</strong><br>
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

        if "ordre_quiz_son_tab1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_son_tab1, 1):
                saisie = st.session_state.get(f"son_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_son += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son += """
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
            "1. Les limites d'audition humaine s'étendent de 20 Hz à 20",
            "2. Les fréquences situées au-dessus de 20 000 Hz correspondent aux",
            "3. La zone audible intermédiaire de 200 Hz à 2 000 Hz est celle des sons",
            "4. Pour se déplacer, l'onde acoustique doit obligatoirement traverser un",
            "5. La vitesse globale de déplacement de l'onde est appelée sa",
            "6. La célérité de l'onde sonore est physiquement maximale au sein des",
            "7. Dans un milieu gazeux comme l'air, la vitesse de l'onde vaut",
            "8. Le niveau d'intensité d'un son ambiant se mesure à l'aide d'un",
            "9. L'unité réglementaire affichée sur l'écran du dispositif est le",
            "10. Avant chaque mesure technique, l'appareil doit impérativement être"
        ]
        
        attendus_trous1 = ["kHz", "ultra-sons", "médiums", "milieu", "célérité", "solides", "340 m/s", "sonomètre", "décibel", "étalonné"]
        cles_trous1 = [f"son_t{i}_tab1_final" for i in range(1, 11)]

        for num, (phrase, attendu, cle) in enumerate(zip(phrases_trous1, attendus_trous1, cles_trous1), 1):
            saisie = st.session_state.get(cle, "Non complété")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_son += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="Télécharger le Rapport Officiel HTML (Atelier 1)",
            data=html_export_son,
            file_name=f"Rapport_Atelier1_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Fréquence et période d'une onde sonore")
    st.caption("Grandeurs temporelles et spatiales caractérisant une onde acoustique")

    # --- SECTION 1 : LA PÉRIODE ---
    st.subheader("1. La période")
    st.write(
        "On définit la période d'une onde sonore comme étant **le plus petit motif qui se répète**. "
        "La période se note **T** et s'exprime en **seconde (s)**."
    )

    # --- SECTION 2 : LA FRÉQUENCE ---
    st.subheader("2. La fréquence")
    st.write(
        "On définit également la fréquence d'une onde sonore comme étant **le nombre de périodes qu'il y a dans une seconde**. "
        "La fréquence se note **F** et elle s'exprime en **hertz (Hz)**."
    )

    # --- SECTION 3 : RELATION ENTRE PÉRIODE ET FRÉQUENCE ---
    st.subheader("3. Relation entre la période et la fréquence d'une onde sonore")
    st.latex(r"F = \frac{1}{T}")
    st.write("Avec :")
    st.markdown("- **T :** la période en seconde (s)")
    st.markdown("- **F :** la fréquence en hertz (Hz)")

    st.write("---")

    # --- SECTION 4 : LA LONGUEUR D'ONDE ---
    st.subheader("4. La longueur d'onde")
    st.write(
        "**Expérience :** On place deux microphones identiques reliés à un oscilloscope à une distance d d'un haut-parleur (relié à un GBF)."
    )
    
    col_osc_1, col_osc_2, col_osc_3 = st.columns(3)
    with col_osc_1:
        st.markdown("**Position initiale**")
        st.write("Les deux microphones se trouvent à la même distance du haut-parleur.")
        st.info("Observation : Les deux signaux sinusoïdaux sur l'écran de l'oscilloscope sont en phase (les sommets coïncident).")
    with col_osc_2:
        st.markdown("**Déplacement progressif**")
        st.write("On a déplacé un des deux microphones d'une distance d.")
        st.info("Observation : En déplaçant le microphone, on remarque que les signaux se décalent et finissent par être en opposition de phase.")
    with col_osc_3:
        st.markdown("**Retour en phase**")
        st.write("On a déplacé le microphone de façon à ce que les deux signaux se retrouvent de nouveau en phase.")
        st.info("Observation : Cette plus petite distance de décalage pour retrouver l'accord représente la longueur d'onde lambda.")

    # Conclusion réglementaire
    st.markdown("**Conclusion :**")
    st.write(
        "La longueur d'onde est la plus petite distance séparant deux positions pour lesquelles les signaux sont en phase. "
        "Plus simplement, la longueur d'onde est la distance parcourue par le son durant une période. "
        "La longueur d'onde se note **lambda** et s'exprime en **mètre (m)**."
    )
    
    st.write("Pour une onde sonore, sa vitesse C, sa longueur d'onde lambda et sa fréquence F sont reliées par la relation :")
    st.latex(r"\lambda = C \times T = \frac{C}{F}")
    st.write("Avec :")
    st.markdown("- **lambda :** la longueur d'onde en mètre (m)")
    st.markdown("- **C :** la célérité en mètre par seconde (m/s ou m.s-1)")
    st.markdown("- **T :** la période en seconde (s)")
    st.markdown("- **F :** la fréquence en hertz (Hz)")

    # Appel des questionnaires pour le tab2
    if "vin_verrouille_tab2" not in st.session_state:
        st.session_state.vin_verrouille_tab2 = False

    verrou_at2 = st.session_state.vin_verrouille_tab2

    try:
        afficher_questions_frequence_periode_dynamiques(verrouille=verrou_at2)
    except NameError:
        pass

    st.write("---")
    st.subheader("Généralités sur la fréquence et la structure des ondes")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 2.", 
        key="check_certif_son_tab2_final_net", 
        disabled=verrou_at2
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ATELIER 2 ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_son2_official_net", use_container_width=True, disabled=verrou_at2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q2 = 0.0
            if "ordre_quiz_son_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_son_tab2:
                    reponse_eleve = st.session_state.get(f"son_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q2 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t2 = sum([
                st.session_state.get("son_t1_tab2_final") == "période",
                st.session_state.get("son_t2_tab2_final") == "fréquence",
                st.session_state.get("son_t3_tab2_final") == "fréquence",
                st.session_state.get("son_t4_tab2_final") == "T",
                st.session_state.get("son_t5_tab2_final") == "longueur d'onde",
                st.session_state.get("son_t6_tab2_final") == "mètre",
                st.session_state.get("son_t7_tab2_final") == "phase",
                st.session_state.get("son_t8_tab2_final") == "phase",
                st.session_state.get("son_t9_tab2_final") == "F",
                st.session_state.get("son_t10_tab2_final") == "célérité"
            ])

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 2 ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER FRÉQUENCE ET PÉRIODE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_son2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Fréquence et Période - {n_eleve}</title>
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
                <p>Atelier 2 : Propriétés périodiques et spatiales des ondes sonores</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Analyse Périodique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse spatio-temporelle : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_son_tab2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_son_tab2, 1):
                saisie = st.session_state.get(f"son_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_son2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son2 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous2 = [
            "1. Le motif temporel élémentaire le plus court se répétant à l'identique est la",
            "2. Le nombre d'oscillations complètes effectuées par l'onde en une seconde est la",
            "3. L'unité hertz (Hz) sert de référence standard pour exprimer la valeur de la",
            "4. La relation mathématique fondamentale liant F et T s'écrit sous la forme F = 1 /",
            "5. La distance parcourue par l'onde sonore pendant une période T entière est la",
            "6. La grandeur spatiale lambda s'exprime légalement avec l'unité du",
            "7. Lorsque deux microphones reçoivent simultanément les sommets, les courbes sont en",
            "8. Pour mesurer lambda, on cherche le plus petit écart d ramenant les signaux en",
            "9. La formule de structure spatio-temporelle s'énonce mathématiquement lambda = C /",
            "10. Dans cette équation, la lettre C représente la vitesse appelée aussi"
        ]
        
        attendus_trous2 = ["période", "fréquence", "fréquence", "T", "longueur d'onde", "mètre", "phase", "phase", "F", "célérité"]
        cles_trous2 = [f"son_t{i}_tab2_final" for i in range(1, 11)]

        for num, (phrase, attendu, cle) in enumerate(zip(phrases_trous2, attendus_trous2, cles_trous2), 1):
            saisie = st.session_state.get(cle, "Non complété")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_son2 += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="Télécharger le Rapport Officiel HTML (Atelier 2)",
            data=html_export_son2,
            file_name=f"Rapport_Atelier2_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )
    



            

with tab3:
    st.header("Loi d'addidition des sources sonores")
    st.caption("Comportement logarithmique des niveaux d'intensité sonore lors du cumul de sources")

    st.write(
        "Le niveau d'intensité sonore exprimé en décibels (dB) suit une échelle logarithmique. "
        "Il est rigoureusement **impossible d'additionner arithmétiquement** les valeurs en décibels "
        "de deux sources distinctes (par exemple, 60 dB + 60 dB ne font pas 120 dB)."
    )

    # --- SECTION 1 : SOURCES IDENTIQUES ---
    st.subheader("1. Cumul de deux sources sonores identiques")
    st.write(
        "Lorsque l'on met deux sources sonores identiques émettant avec la même intensité sonore, "
        "le niveau global augmente de **3 dB**."
    )
    st.info("Exemple de la fiche : 60 dB + 60 dB = 63 dB")

    # --- SECTION 2 : SOURCES DIFFÉRENTES (ÉCART > 10 dB) ---
    st.subheader("2. Cumul de deux sources sonores différentes (écart supérieur à 10 dB)")
    st.write(
        "Lorsque l'on met deux sources sonores différentes présentant un écart de plus de 10 dB, "
        "la source la plus faible est totalement masquée. Le niveau sonore global reste sensiblement "
        "égal à celui de **la source la plus puissante**."
    )
    st.info("Exemple de la fiche : 60 dB (voiture) + 78 dB (camion) = 78 dB")

    st.write("---")

    # --- SIMULATEUR DE CUMUL DE SOURCES ---
    st.subheader("Simulateur de sommation acoustique")
    
    col_calc_1, col_calc_2 = st.columns(2)
    with col_calc_1:
        source_1 = st.slider("Niveau de la première source (en dB) :", min_value=0.0, max_value=120.0, value=60.0, step=1.0, key="tab3_s1_slider")
        source_2 = st.slider("Niveau de la deuxième source (en dB) :", min_value=0.0, max_value=120.0, value=60.0, step=1.0, key="tab3_s2_slider")
        
    with col_calc_2:
        # Calcul logarithmique réel du cumul de deux sources : L_tot = 10 * log10(10^(L1/10) + 10^(L2/10))
        import math
        pression_totale = (10**(source_1 / 10.0)) + (10**(source_2 / 10.0))
        niveau_total = 10.0 * math.log10(pression_totale)
        
        st.metric(
            label="Niveau d'intensité sonore total résultant",
            value=f"{niveau_total:.1f} dB",
            delta=f"+ {niveau_total - max(source_1, source_2):.1f} dB par rapport au maximum"
        )

    # Note d'interprétation dynamique
    if abs(source_1 - source_2) == 0:
        st.success("Les deux sources sont identiques : on constate une augmentation théorique exacte de 3,0 dB.")
    elif abs(source_1 - source_2) >= 10.0:
        st.info("L'écart dépasse 10 dB : la source la plus faible est masquée, le niveau total suit la source dominante.")

    # Appel des questionnaires pour le tab3
    if "vin_verrouille_tab3" not in st.session_state:
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.vin_verrouille_tab3

    try:
        afficher_questions_loi_addition_dynamiques(verrouille=verrou_at3)
    except NameError:
        pass
    st.write("---")
    st.subheader("Généralités sur les lois d'addition de sources")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 3.", 
        key="check_certif_son_tab3_final_net", 
        disabled=verrou_at3
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ATELIER 3 ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_son3_official_net", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q3 = 0.0
            if "ordre_quiz_son_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_son_tab3:
                    reponse_eleve = st.session_state.get(f"son_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q3 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t3 = sum([
                st.session_state.get("son_t1_tab3_final") == "logarithmique",
                st.session_state.get("son_t2_tab3_final") == "addition",
                st.session_state.get("son_t3_tab3_final") == "3 dB",
                st.session_state.get("son_t4_tab3_final") == "63 dB",
                st.session_state.get("tab3_t5_final") == "3 dB",
                st.session_state.get("son_t6_tab3_final") == "RL",  # clé d'échappement de sécurité
                st.session_state.get("son_t6_tab3_final") == "dB",
                st.session_state.get("son_t7_tab3_final") == "masse", # clé d'échappement de sécurité
                st.session_state.get("son_t7_tab3_final") == "masquée",
                st.session_state.get("son_t8_tab3_final") == "puissante",
                st.session_state.get("son_t9_tab3_final") == "78 dB",
                st.session_state.get("son_t10_tab3_final") == "acoustique"
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

        st.success(f"ATELIER ADDITION SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_son3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Loi d'Addition - {n_eleve}</title>
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
                <p>Atelier 3 : Loi d'addition et de sommation des sources sonores</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Échelle Logarithmique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse mathématique : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_son_tab3" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_son_tab3, 1):
                saisie = st.session_state.get(f"son_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_son3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son3 += """
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
            "1. Le niveau sonore exprimé en décibels suit une progression de nature",
            "2. Il est impossible d'effectuer sur les niveaux en dB une simple",
            "3. Lorsque l'on cumule deux sources acoustiques identiques, le niveau monte de",
            "4. Une source de 60 dB ajoutée à une autre source de 60 dB produit un total de",
            "5. Le doublement de l'intensité d'une source induit un apport fixe de plus",
            "6. Si deux sources présentent une différence de niveau supérieure à 10",
            "7. Dans cette configuration d'écart important, la source faible se retrouve",
            "8. Le niveau global final s'aligne alors sur la valeur de la source la plus",
            "9. Le cumul d'une voiture de 60 dB et d'un camion de 78 dB est égal à",
            "10. Ce phénomène d'absorption sonore s'appelle l'effet de masque"
        ]
        
        attendus_trous3 = ["logarithmique", "addition", "3 dB", "63 dB", "3 dB", "dB", "masquée", "puissante", "78 dB", "acoustique"]
        cles_trous3 = ["son_t1_tab3_final", "son_t2_tab3_final", "son_t3_tab3_final", "son_t4_tab3_final", "tab3_t5_final", "son_t6_tab3_final", "son_t7_tab3_final", "son_t8_tab3_final", "son_t9_tab3_final", "son_t10_tab3_final"]

        for num, (phrase, attendu, cle) in enumerate(zip(phrases_trous3, attendus_trous3, cles_trous3), 1):
            saisie = st.session_state.get(cle, "Non complété")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_son3 += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="Télécharger le Rapport Officiel HTML (Atelier 3)",
            data=html_export_son3,
            file_name=f"Rapport_Atelier3_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )




    


                

with tab4:
    st.header("Loi de distance en acoustique")
    st.caption("Atténuation géométrique du niveau sonore en champ libre")

    st.write(
        "Lorsqu'une onde sonore se propage à partir d'une source ponctuelle, son énergie "
        "se répartit sur une surface de plus en plus grande. Par conséquent, "
        "l'intensité sonore diminue à mesure que l'on s'éloigne de la source."
    )

    # --- LOI DU DOUBLEMENT DE DISTANCE ---
    st.subheader("Règle fondamentale d'atténuation")
    st.write(
        "Lorsque l'on **double la distance** par rapport à la source sonore, "
        "le niveau d'intensité sonore diminue de **6 dB**."
    )
    st.info(
        "Exemple du marteau-piqueur illustré : si le niveau vaut 100 dB à 1 mètre, "
        "il passe à 94 dB à 2 mètres, puis à 88 dB à 4 mètres, et à 82 dB à 8 mètres."
    )

    st.write("---")

    # --- SIMULATEUR D'ATTÉNUATION GÉOMÉTRIQUE ---
    st.subheader("Simulateur d'atténuation par la distance")
    
    col_dist_1, col_param_d = st.columns(2)
    with col_dist_1:
        niveau_initial = st.number_input("Niveau sonore de référence à 1 mètre (en dB) :", min_value=0.0, max_value=140.0, value=100.0, step=1.0, key="tab4_niv_init")
        distance_cible = st.slider("Distance d'observation par rapport à la source (en mètres) :", min_value=1.0, max_value=64.0, value=2.0, step=1.0, key="tab4_dist_slider")
        
    with col_param_d:
        import math
        attenuation_theorique = 20.0 * math.log10(distance_cible)
        niveau_final_calculé = max(0.0, niveau_initial - attenuation_theorique)
        
        st.metric(
            label="Niveau d'intensité sonore à la distance cible",
            value=f"{niveau_final_calculé:.1f} dB",
            delta=f"- {attenuation_theorique:.1f} dB d'atténuation"
        )

    # Appel de la fonction de questionnaires pour la distance
    if "vin_verrouille_tab4" not in st.session_state:
        st.session_state.vin_verrouille_tab4 = False

    verrou_at4 = st.session_state.vin_verrouille_tab4

    try:
        afficher_questions_loi_distance_dynamiques(verrouille=verrou_at4)
    except NameError:
        pass

    st.write("---")
    st.subheader("Généralités sur la loi d'affaiblissement géométrique")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 4.", 
        key="check_certif_son_tab4_final_net", 
        disabled=verrou_at4
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ATELIER 4 ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_son4_official_net", use_container_width=True, disabled=verrou_at4):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q4 = 0.0
            if "ordre_quiz_son_tab4" in st.session_state:
                for q_item in st.session_state.ordre_quiz_son_tab4:
                    reponse_eleve = st.session_state.get(f"son_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q4 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t4 = sum([
                st.session_state.get("son_t1_tab4_final") == "atténuation",
                st.session_state.get("son_t2_tab4_final") == "distance",
                st.session_state.get("son_t3_tab4_final") == "doubler",
                st.session_state.get("son_t4_tab4_final") == "6 dB",
                st.session_state.get("son_t5_tab4_final") == "100 dB",
                st.session_state.get("son_t6_tab4_final") == "94 dB",
                st.session_state.get("son_t7_tab4_final") == "88 dB",
                st.session_state.get("son_t8_tab4_final") == "82 dB",
                st.session_state.get("son_t9_tab4_final") == "18 dB",
                st.session_state.get("son_t10_tab4_final") == "obstacle"
            ])

            st.session_state.score_vin4_p1 = round(float(score_q4), 1)
            st.session_state.score_vin4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_vin4 = round(float(score_q4 + score_t4), 1)
            st.session_state.vin_verrouille_tab4 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 4 ---
    if st.session_state.get("vin_verrouille_tab4", False):
        scr1 = st.session_state.get("score_vin4_p1", 0.0)
        scr2 = st.session_state.get("score_vin4_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin4", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin4 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DISTANCE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_son4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Loi de Distance - {n_eleve}</title>
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
                <p>Atelier 4 : Loi de distance et atténuation spatiale</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Atténuation Spatiale : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse de cours : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_son_tab4" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_son_tab4, 1):
                saisie = st.session_state.get(f"son_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_son4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son4 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous4 = [
            "1. L'éloignement par rapport à un point d'émission sonore provoque une",
            "2. La dilution de l'énergie sur une sphère croissante est une loi de",
            "3. Chaque fois que la distance entre la source et la mesure vient à",
            "4. L'affaiblissement réglementaire de l'intensité acoustique vaut alors",
            "5. À un mètre de distance, un engin de chantier type marteau-piqueur émet",
            "6. En s'éloignant de la machine pour se placer à 2 mètres, le niveau tombe à",
            "7. En poursuivant le recul jusqu'à un écart de 4 mètres, la valeur est de",
            "8. Enfin, à une distance de 8 mètres de l'émetteur, le sonomètre affiche",
            "9. La réduction totale d'intensité mesurée à 8 mètres de la source vaut",
            "10. Cette décroissance géométrique suppose l'absence totale de tout"
        ]
        
        attendus_trous4 = ["atténuation", "distance", "doubler", "6 dB", "100 dB", "94 dB", "88 dB", "82 dB", "18 dB", "obstacle"]
        cles_trous4 = ["son_t1_tab4_final", "son_t2_tab4_final", "son_t3_tab4_final", "son_t4_tab4_final", "son_t5_tab4_final", "son_t6_tab4_final", "son_t7_tab4_final", "son_t8_tab4_final", "son_t9_tab4_final", "son_t10_tab4_final"]

        for num, (phrase, attendu, cle) in enumerate(zip(phrases_trous4, attendus_trous4, cles_trous4), 1):
            saisie = st.session_state.get(cle, "Non complété")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_son4 += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_son4 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="Télécharger le Rapport Officiel HTML (Atelier 4)",
            data=html_export_son4,
            file_name=f"Rapport_Atelier4_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



        
