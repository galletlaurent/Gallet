# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dérivées",
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
import sympy as sp

# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dérivées")
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
    "A quoi sert la notion de dérivée",
    "Le nombre dérivée en un point d'une courbe",
    "La tangente en un point à une courbe",
    "Les dérivées des fonctions ploynômes de degré n",
    "Les dérivées des fonctions rationnelles ",
    "Les dérivées des autres fonctions",
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]



def afficher_questions_autres_fonctions(verrouille=False):
    import streamlit as st

    # Questions de quiz sur les autres fonctions et composées
    ordre_fixe_tab6 = [
        {"id": "q6_1", "q": "Quelle est la fonction dérivée de la fonction f(x) = sin(x) sur l'ensemble des réels ?", "options": ["f'(x) = cos(x)", "f'(x) = -cos(x)", "f'(x) = -sin(x)"], "rep": "f'(x) = cos(x)"},
        {"id": "q6_2", "q": "Quelle est la fonction dérivée de la fonction f(x) = cos(x) sur l'ensemble des réels ?", "options": ["f'(x) = -sin(x)", "f'(x) = sin(x)", "f'(x) = -cos(x)"], "rep": "f'(x) = -sin(x)"},
        {"id": "q6_3", "q": "Sur quel ensemble la fonction de référence f(x) = \u221ax est-elle rigoureusement dérivable ?", "options": ["Sur ]0 ; +inf[ (strictement positif)", "Sur [0 ; +inf[ (positif ou nul)", "Sur l'ensemble de tous les réels"], "rep": "Sur ]0 ; +inf[ (strictement positif)"},
        {"id": "q6_4", "q": "Quelle est l'expression de la fonction dérivée de f(x) = \u221ax pour x strictement positif ?", "options": ["f'(x) = 1 / (2\u221ax)", "f'(x) = 2\u221ax", "f'(x) = -1 / (2\u221ax)"], "rep": "1 / (2\u221ax)"},
        {"id": "q6_5", "q": "Quelle formule applique-t-on pour dériver une fonction composée de la forme f(x) = u(ax + b) ?", "options": ["f'(x) = a * u'(ax + b)", "f'(x) = u'(ax + b)", "f'(x) = a * u'(x)"], "rep": "f'(x) = a * u'(ax + b)"},
        {"id": "q6_6", "q": "Calculez la fonction dérivée de f(x) = sin(3x + 2) en appliquant la formule des composées :", "options": ["f'(x) = 3 * cos(3x + 2)", "f'(x) = cos(3x + 2)", "f'(x) = -3 * cos(3x + 2)"], "rep": "f'(x) = 3 * cos(3x + 2)"},
        {"id": "q6_7", "q": "Calculez la fonction dérivée de f(x) = cos(2x - 5) :", "options": ["f'(x) = -2 * sin(2x - 5)", "f'(x) = 2 * sin(2x - 5)", "f'(x) = -sin(2x - 5)"], "rep": "f'(x) = -2 * sin(2x - 5)"},
        {"id": "q6_8", "q": "Quelle est la valeur de la dérivée de f(x) = \u221ax au point d'abscisse x = 1/4 ?", "options": ["1", "2", "4"], "rep": "1"},
        {"id": "q6_9", "q": "Graphiquement, la courbe représentative de la fonction racine carrée admet en l'origine (0;0) :", "options": ["Une demi-tangente verticale", "Une tangente horizontale", "Aucune tangente"], "rep": "Une demi-tangente verticale"},
        {"id": "q6_10", "q": "La dérivée de la fonction f(x) = sin(x) + cos(x) est égale à l'expression :", "options": ["cos(x) - sin(x)", "cos(x) + sin(x)", "sin(x) - cos(x)"], "rep": "cos(x) - sin(x)"}
    ]

    st.session_state.ordre_quiz_tab6 = ordre_fixe_tab6

    col_double_quiz_tab6, col_double_trous_tab6 = st.columns(2)

    with col_double_quiz_tab6:
        st.markdown("##### Quiz sur les autres fonctions (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_tab6, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab6_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_tab6:
        st.markdown("##### Synthèse sur les trigonométriques et composées (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La fonction sinus associe à chaque valeur réelle une dérivée égale à")
        with c2: st.selectbox("", ["Choisir...", "cos(x)", "-cos(x)", "sin(x)"], key="tab6_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La fonction cosinus voit ses variations dictées par sa dérivée égale à")
        with c4: st.selectbox("", ["Choisir...", "-sin(x)", "sin(x)", "cos(x)"], key="tab6_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La fonction racine carrée est continue en zéro mais n'y est pas")
        with c6: st.selectbox("", ["Choisir...", "dérivable", "définie", "positive"], key="tab6_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La présence de la racine au dénominateur de sa dérivée crée une pente")
        with c8: st.selectbox("", ["Choisir...", "infinie", "nulle", "négative"], key="tab6_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, col10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Dériver la forme u(ax+b) demande d'extraire le coefficient a en tant que")
        with col10: st.selectbox("", ["Choisir...", "facteur", "exposant", "quotient"], key="tab6_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Dans l'expression finale d'une composée, l'argument intérieur ax+b reste")
        with c12: st.selectbox("", ["Choisir...", "inchangé", "dérivé", "annulé"], key="tab6_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La courbe représentative de la fonction racine carrée est strictement")
        with c14: st.selectbox("", ["Choisir...", "croissante", "décroissante", "périodique"], key="tab6_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Les fonctions sinus et cosinus alternent leurs variations de manière")
        with c16: st.selectbox("", ["Choisir...", "périodique", "linéaire", "infinie"], key="tab6_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La dérivée de la fonction f(x) = \u221ax possède la valeur constante 2 au")
        with c18: st.selectbox("", ["Choisir...", "dénominateur", "numérateur", "facteur"], key="tab6_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Valider ce dernier bloc achève l'étude formelle des fonctions usuelles de ce")
        with c20: st.selectbox("", ["Choisir...", "chapitre", "trimestre", "repère"], key="tab6_t10_final", disabled=verrouille, label_visibility="collapsed")


def afficher_questions_rationnelles(verrouille=False):
    import streamlit as st

    # Questions de quiz sur les règles de dérivation des fonctions rationnelles
    ordre_fixe_tab5 = [
        {"id": "q5_1", "q": "Quelle est la fonction dérivée de la fonction inverse f(x) = 1/x sur son domaine de définition ?", "options": ["f'(x) = -1/x²", "f'(x) = 1/x²", "f'(x) = -1/x"], "rep": "f'(x) = -1/x²"},
        {"id": "q5_2", "q": "Pour dériver une fonction de la forme 1/v(x), quelle formule doit-on utiliser ?", "options": ["-v'(x) / [v(x)]²", "1 / v'(x)", "v'(x) / [v(x)]²"], "rep": "-v'(x) / [v(x)]²"},
        {"id": "q5_3", "q": "Quelle est la formule correcte pour la dérivée d'un quotient de fonctions (u/v)' ?", "options": ["(u'v - uv') / v²", "(u'v + uv') / v²", "(u'v' - uv) / v²"], "rep": "(u'v - uv') / v²"},
        {"id": "q5_4", "q": "Dans la formule de dérivation d'un quotient, quel élément figure au dénominateur ?", "options": ["Le carré du dénominateur initial v²", "La dérivée du dénominateur v'", "Le produit des dénominateurs u*v"], "rep": "Le carré du dénominateur initial v²"},
        {"id": "q5_5", "q": "Trouvez la fonction dérivée de f(x) = 1 / (x + 3) :", "options": ["f'(x) = -1 / (x + 3)¹", "f'(x) = -1 / (x + 3)²", "f'(x) = 1 / (x + 3)²"], "rep": f"'(x) = -1 / (x + 3)²"},
        {"id": "q5_6", "q": "Si u(x) = x et v(x) = x + 1, quel est le numérateur de la dérivée de u/v après calcul de u'v - uv' ?", "options": ["1", "-1", "2x + 1"], "rep": "1"},
        {"id": "q5_7", "q": "Une fonction rationnelle n'est pas dérivable aux points où son dénominateur :", "options": ["S'annule", "Est positif", "Est maximal"], "rep": "S'annule"},
        {"id": "q5_8", "q": "Pour étudier le signe de la dérivée d'un quotient (u'v - uv')/v², il suffit souvent d'étudier le signe :", "options": ["Du numérateur uniquement", "Du dénominateur uniquement", "De la fonction initiale"], "rep": "Du numérateur uniquement"},
        {"id": "q5_9", "q": "Quelle est la dérivée de la fonction f(x) = 3/x (qui s'écrit aussi 3 * (1/x)) ?", "options": ["f'(x) = -3/x²", "f'(x) = -1/3x²", "f'(x) = 3/x²"], "rep": "f'(x) = -3/x²"},
        {"id": "q5_10", "q": "La dérivée de la fonction f(x) = (2x + 1) / x se simplifie sous la forme :", "options": ["f'(x) = -1/x²", "f'(x) = 2 - 1/x²", "f'(x) = 1/x²"], "rep": "f'(x) = -1/x²"}
    ]

    st.session_state.ordre_quiz_tab5 = ordre_fixe_tab5

    col_double_quiz_tab5, col_double_trous_tab5 = st.columns(2)

    with col_double_quiz_tab5:
        st.markdown("##### Quiz sur les fonctions rationnelles (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_tab5, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab5_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_tab5:
        st.markdown("##### Synthèse algébrique des quotients (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Une fonction rationnelle est définie comme le quotient de deux fonctions")
        with c2: st.selectbox("", ["Choisir...", "polynômes", "affines", "constantes"], key="tab5_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La dérivée de la fonction de référence 1/x est égale à -1 divisé par")
        with c4: st.selectbox("", ["Choisir...", "x²", "x", "2x"], key="tab5_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La formule du quotient (u/v)' possède un numérateur contenant le signe opératoire")
        with c6: st.selectbox("", ["Choisir...", "moins", "plus", "multiplier"], key="tab5_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Le dénominateur de la dérivée d'un quotient est toujours strictement")
        with c8: st.selectbox("", ["Choisir...", "positif", "négatif", "nul"], key="tab5_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, col10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le domaine de dérivabilité d'un quotient exclut les valeurs qui annulent le")
        with col10: st.selectbox("", ["Choisir...", "dénominateur", "numérateur", "facteur"], key="tab5_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Dans la formule du quotient, le premier terme développé au numérateur est u' multiplié par")
        with c12: st.selectbox("", ["Choisir...", "v", "v'", "u"], key="tab5_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Le second terme retranché au numérateur du quotient correspond au produit de u par")
        with c14: st.selectbox("", ["Choisir...", "v'", "v", "u'"], key="tab5_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le carré présent au dénominateur ne doit en aucun cas être développé lors des")
        with c16: st.selectbox("", ["Choisir...", "calculs", "tracés", "graphiques"], key="tab5_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La fonction inverse est strictement décroissante sur chaque intervalle de son domaine car sa dérivée est")
        with c18: st.selectbox("", ["Choisir...", "négative", "positive", "nulle"], key="tab5_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Maîtriser le numérateur permet de localiser les changements de sens de la fonction")
        with c20: st.selectbox("", ["Choisir...", "rationnelle", "constante", "linéaire"], key="tab5_t10_final", disabled=verrouille, label_visibility="collapsed")



def afficher_questions_polynomes(verrouille=False):
    import streamlit as st

    # Questions de quiz sur les règles de dérivation des polynômes
    ordre_fixe_tab4 = [
        {"id": "q4_1", "q": "Quelle est la fonction dérivée de la fonction constante f(x) = k ?", "options": ["f'(x) = 0", "f'(x) = 1", "f'(x) = k"], "rep": "f'(x) = 0"},
        {"id": "q4_2", "q": "Si f(x) = x, quelle est l'expression correcte de sa dérivée f'(x) ?", "options": ["f'(x) = 1", "f'(x) = 0", "f'(x) = x"], "rep": "f'(x) = 1"},
        {"id": "q4_3", "q": "Quelle formule applique-t-on pour dériver f(x) = x^n (avec n entier naturel non nul) ?", "options": ["f'(x) = n * x^(n-1)", "f'(x) = x^(n-1)", "f'(x) = n * x^n"], "rep": "f'(x) = n * x^(n-1)"},
        {"id": "q4_4", "q": "Trouvez la fonction dérivée de f(x) = x³ :", "options": ["f'(x) = 3x²", "f'(x) = 2x³", "f'(x) = 3x"], "rep": "f'(x) = 3x²"},
        {"id": "q4_5", "q": "Si f(x) = k * u(x) où k est une constante, quelle est sa dérivée f'(x) ?", "options": ["f'(x) = k * u'(x)", "f'(x) = u'(x)", "f'(x) = 0"], "rep": "f'(x) = k * u'(x)"},
        {"id": "q4_6", "q": "Déterminez la dérivée de la fonction f(x) = 5x⁴ :", "options": ["f'(x) = 20x³", "f'(x) = 5x³", "f'(x) = 20x⁴"], "rep": "f'(x) = 20x³"},
        {"id": "q4_7", "q": "La règle de dérivation d'une somme de fonctions (u + v)' s'énonce ainsi :", "options": ["u' + v'", "u' * v + u * v'", "u' * v'"], "rep": "u' + v'"},
        {"id": "q4_8", "q": "Quelle est la fonction dérivée du polynôme f(x) = x² - 4x + 7 ?", "options": ["f'(x) = 2x - 4", "f'(x) = 2x - 4 + 7", "f'(x) = x - 4"], "rep": "f'(x) = 2x - 4"},
        {"id": "q4_9", "q": "Si le coefficient dominant d'un polynôme de degré 2 est positif, sa dérivée s'annule en :", "options": ["Un minimum local", "Un maximum local", "Un point d'inflexion"], "rep": "Un minimum local"},
        {"id": "q4_10", "q": "Le degré de la fonction dérivée d'un polynôme de degré n non nul est égal à :", "options": ["n - 1", "n", "n + 1"], "rep": "n - 1"}
    ]

    st.session_state.ordre_quiz_tab4 = ordre_fixe_tab4

    col_double_quiz_tab4, col_double_trous_tab4 = st.columns(2)

    with col_double_quiz_tab4:
        st.markdown("##### Quiz sur les polynômes (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_tab4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab4_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_tab4:
        st.markdown("##### Synthèse algébrique des polynômes (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La dérivée d'une fonction constante est toujours égale à")
        with c2: st.selectbox("", ["Choisir...", "0", "1", "k"], key="tab4_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La fonction affine f(x) = ax + b possède une dérivée constante égale à")
        with c4: st.selectbox("", ["Choisir...", "a", "b", "x"], key="tab4_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour dériver une puissance, l'exposant n descend en tant que")
        with c6: st.selectbox("", ["Choisir...", "facteur", "exposant", "dénominateur"], key="tab4_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Après dérivation de x^n, la nouvelle puissance résiduelle devient de degré n moins")
        with c8: st.selectbox("", ["Choisir...", "1", "2", "0"], key="tab4_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, col10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La dérivation est une opération linéaire qui conserve les coefficients multiplicatifs")
        with col10: st.selectbox("", ["Choisir...", "réels", "nuls", "inverses"], key="tab4_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Dériver un polynôme se réalise terme à terme en appliquant la formule de la")
        with c12: st.selectbox("", ["Choisir...", "somme", "produit", "quotient"], key="tab4_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La dérivée de la fonction f(x) = x² est l'expression linéaire")
        with c14: st.selectbox("", ["Choisir...", "2x", "x", "2"], key="tab4_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La dérivée de x³ est égale à 3 multiplié par")
        with c16: st.selectbox("", ["Choisir...", "x²", "x", "1"], key="tab4_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Un monôme de degré 1 se transforme après dérivation en une valeur")
        with c18: st.selectbox("", ["Choisir...", "constante", "nulle", "quadratique"], key="tab4_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. L'opération de dérivation réduit le degré du polynôme initial de")
        with c20: st.selectbox("", ["Choisir...", "1", "2", "0"], key="tab4_t10_final", disabled=verrouille, label_visibility="collapsed")

def afficher_questions_tangente(verrouille=False):
    import streamlit as st

    # Questions de quiz sur la tangente et son équation
    ordre_fixe_tab3 = [
        {"id": "q3_1", "q": "L'équation réduite de la droite tangente à la courbe de f au point d'abscisse a est :", "options": ["y = f'(a)(x - a) + f(a)", "y = f(a)(x - a) + f'(a)", "y = f'(a)x + f(a)"], "rep": "y = f'(a)(x - a) + f(a)"},
        {"id": "q3_2", "q": "Dans l'équation y = f'(a)(x - a) + f(a), que représente concrètement la valeur f'(a) ?", "options": ["Le coefficient directeur de la droite tangente", "L'ordonnée à l'origine de la droite", "L'abscisse du point d'intersection avec l'axe x"], "rep": "Le coefficient directeur de la droite tangente"},
        {"id": "q3_3", "q": "Si le nombre dérivé f'(a) est égal à 0, la droite tangente au point d'abscisse a est :", "options": ["Horizontale", "Verticale", "Parallèle à la droite y = x"], "rep": "Horizontale"},
        {"id": "q3_4", "q": "Quelle est l'équation d'une tangente horizontale au point d'abscisse a ?", "options": ["y = f(a)", "x = a", "y = 0"], "rep": "y = f(a)"},
        {"id": "q3_5", "q": "Si une tangente a pour équation y = 4x - 2, quel est le nombre dérivé en ce point ?", "options": ["4", "-2", "2"], "rep": "4"},
        {"id": "q3_6", "q": "Pour tracer précisément une droite tangente à partir de son équation, on a besoin :", "options": ["Du point de contact et du coefficient directeur", "Uniquement de la fonction dérivée f'", "De deux points situés en dehors de la courbe"], "rep": "Du point de contact et du coefficient directeur"},
        {"id": "q3_7", "q": "Lorsque la droite tangente se situe entièrement en dessous de la courbe sur un intervalle, la fonction est dite :", "options": ["Convexe", "Concave", "Linéaire"], "rep": "Convexe"},
        {"id": "q3_8", "q": "Si la droite tangente traverse la courbe en changeant de côté au point de contact, ce point s'appelle :", "options": ["Un point d'inflexion", "Un point critique", "Un point anguleux"], "rep": "Un point d'inflexion"},
        {"id": "q3_9", "q": "Au point d'inflexion d'une courbe, la fonction dérivée seconde f'' s'annule en :", "options": ["Changeant de signe", "Restant positive", "Devenant infinie"], "rep": "Changeant de signe"},
        {"id": "q3_10", "q": "La droite sécante (AB) s'approche de la droite tangente lorsque la distance séparant A et B :", "options": ["Tend vers zéro", "Devient infiniment grande", "Reste strictement constante"], "rep": "Tend vers zéro"}
    ]

    st.session_state.ordre_quiz_tab3 = ordre_fixe_tab3

    col_double_quiz_tab3, col_double_trous_tab3 = st.columns(2)

    with col_double_quiz_tab3:
        st.markdown("##### Quiz sur la tangente (10 questions - 10 pts)")
        
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
        st.markdown("##### Synthèse géométrique de la tangente (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La droite qui effleure au plus près une courbe en un point unique est la")
        with c2: st.selectbox("", ["Choisir...", "tangente", "sécante", "directrice"], key="tab3_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le coefficient directeur de cette droite est égal au nombre")
        with c4: st.selectbox("", ["Choisir...", "dérivé", "entier", "nominal"], key="tab3_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La formule générale de l'équation de la tangente fait intervenir la valeur de f(a) et de")
        with c6: st.selectbox("", ["Choisir...", "f'(a)", "f''(a)", "h"], key="tab3_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Une pente positive pour la tangente indique que la fonction est localement")
        with c8: st.selectbox("", ["Choisir...", "croissante", "décroissante", "nulle"], key="tab3_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Une pente négative pour la tangente indique que la fonction est localement")
        with c10: st.selectbox("", ["Choisir...", "décroissante", "croissante", "stationnaire"], key="tab3_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Un extremum local d'une fonction dérivable est caractérisé par une tangente")
        with c12: st.selectbox("", ["Choisir...", "horizontale", "verticale", "oblique"], key="tab3_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Si la courbe se situe entièrement au-dessus de ses tangentes, elle est")
        with c14: st.selectbox("", ["Choisir...", "convexe", "concave", "asymptotique"], key="tab3_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Si la courbe se situe entièrement en dessous de ses tangentes, elle est")
        with c16: st.selectbox("", ["Choisir...", "concave", "convexe", "symétrique"], key="tab3_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le point de la courbe où la tangente traverse cette dernière s'appelle un point d'")
        with c18: st.selectbox("", ["Choisir...", "inflexion", "rupture", "contact"], key="tab3_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. À l'échelle microscopique, zoomer sur le point de contact assimile la courbe à sa")
        with c20: st.selectbox("", ["Choisir...", "tangente", "sécante", "origine"], key="tab3_t10_final", disabled=verrouille, label_visibility="collapsed")


def afficher_questions_nombre_derive(verrouille=False):
    import streamlit as st

    # Questions de quiz sur le nombre dérivé et le taux d'accroissement
    ordre_fixe_tab2 = [
        {"id": "q2_1", "q": "Le taux d'accroissement d'une fonction f entre deux points d'abscisses a et a+h est donné par :", "options": ["(f(a+h) - f(a)) / h", "(f(a+h) + f(a)) / h", "f(a+h) - f(a)"], "rep": "(f(a+h) - f(a)) / h"},
        {"id": "q2_2", "q": "Géométriquement, le taux d'accroissement entre le point A(a; f(a)) et le point B(a+h; f(a+h)) représente :", "options": ["Le coefficient directeur de la sécante (AB)", "Le coefficient directeur de la tangente", "La distance minimale entre A et B"], "rep": "Le coefficient directeur de la sécante (AB)"},
        {"id": "q2_3", "q": "Le nombre dérivé f'(a) est obtenu en calculant la limite du taux d'accroissement quand h tend vers :", "options": ["0", "1", "L'infini"], "rep": "0"},
        {"id": "q2_4", "q": "Si la limite du taux d'accroissement en un point a existe et est finie, on dit que la fonction f est :", "options": ["Dérivable en a", "Continue uniquement en a", "Périodique de période a"], "rep": "Dérivable en a"},
        {"id": "q2_5", "q": "Pour la fonction f(x) = x², le taux d'accroissement en un point a après simplification par h est égal à :", "options": ["2a + h", "a² + h", "2a"], "rep": "2a + h"},
        {"id": "q2_6", "q": "Lorsque h s'approche de 0, la droite sécante (AB) pivote et se confond avec :", "options": ["La droite tangente au point A", "L'axe des abscisses", "La droite sécante à l'origine"], "rep": "La droite tangente au point A"},
        {"id": "q2_7", "q": "Si f'(2) = -3, cela signifie que la courbe au point d'abscisse 2 est localement :", "options": ["Décroissante avec une pente de -3", "Croissante avec une pente de 3", "Horizontale"], "rep": "Décroissante avec une pente de -3"},
        {"id": "q2_8", "q": "Quelle condition doit remplir la limite du taux d'accroissement pour définir un nombre dérivé ?", "options": ["Être une valeur réelle finie", "Être toujours positive", "Être égale à l'infini"], "rep": "Être une valeur réelle finie"},
        {"id": "q2_9", "q": "Graphiquement, si une fonction admet une tangente verticale au point d'abscisse a, alors :", "options": ["La fonction n'est pas dérivable en a", "Le nombre dérivé f'(a) vaut 0", "Le nombre dérivé f'(a) est infini"], "rep": "La fonction n'est pas dérivable en a"},
        {"id": "q2_10", "q": "La notation différentielle équivalente à f'(a) inventée par Leibniz s'écrit sous la forme :", "options": ["df/dx évalué en a", "delta f / delta x", "f point en a"], "rep": "df/dx évalué en a"}
    ]

    st.session_state.ordre_quiz_tab2 = ordre_fixe_tab2

    col_double_quiz_tab2, col_double_trous_tab2 = st.columns(2)

    with col_double_quiz_tab2:
        st.markdown("##### Quiz sur le nombre dérivé (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_tab2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab2_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_tab2:
        st.markdown("##### Synthèse sur le taux d'accroissement (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le rapport f(a+h)-f(a) divisé par h s'appelle le taux d'")
        with c2: st.selectbox("", ["Choisir...", "accroissement", "ajustement", "évolution"], key="tab2_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Ce taux correspond géométriquement à la pente de la droite")
        with c4: st.selectbox("", ["Choisir...", "sécante", "tangente", "asymptote"], key="tab2_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour trouver le nombre dérivé, on étudie la position limite lorsque h tend vers")
        with c6: st.selectbox("", ["Choisir...", "0", "1", "infini"], key="tab2_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La valeur de cette limite finie est appelée le nombre")
        with c8: st.selectbox("", ["Choisir...", "dérivé", "entier", "réel"], key="tab2_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre dérivé f'(a) correspond précisément à la pente de la")
        with c10: st.selectbox("", ["Choisir...", "tangente", "courbe", "ordonnée"], key="tab2_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Si la courbe présente un point anguleux, la limite à gauche est différente de la limite à")
        with c12: st.selectbox("", ["Choisir...", "droite", "l'origine", "l'infini"], key="tab2_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Dans ce cas particulier de point anguleux, la fonction n'est pas")
        with c14: st.selectbox("", ["Choisir...", "dérivable", "continue", "définie"], key="tab2_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le calcul algébrique nécessite souvent de simplifier l'expression pour éliminer h du")
        with c16: st.selectbox("", ["Choisir...", "dénominateur", "numérateur", "facteur"], key="tab2_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Si la valeur f'(a) obtenue est nulle, la tangente associée est alors")
        with c18: st.selectbox("", ["Choisir...", "horizontale", "verticale", "oblique"], key="tab2_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Ce point à tangente horizontale correspond généralement à un maximum ou un minimum")
        with c20: st.selectbox("", ["Choisir...", "local", "absolu", "nul"], key="tab2_t10_final", disabled=verrouille, label_visibility="collapsed")


def afficher_questions_generalites_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le comportement et le contrôle de l'introduction à la dérivation (tab1)
    ordre_fixe_tab1 = [
        {"id": "q1_1", "q": "Au XVIIe siècle, le calcul différentiel est né de manière indépendante entre Newton et :", "options": ["Gottfried Wilhelm Leibniz", "René Descartes", "Blaise Pascal"], "rep": "Gottfried Wilhelm Leibniz"},
        {"id": "q1_2", "q": "Isaac Newton a principalement développé la dérivation pour résoudre des problèmes liés à :", "options": ["La physique et le mouvement", "La géométrie pure et les tangentes", "Les probabilités et les jeux de hasard"], "rep": "La physique et le mouvement"},
        {"id": "q1_3", "q": "Quelle notation moderne majeure doit-on au mathématicien allemand Leibniz ?", "options": ["Le symbole différentiel dx", "La notation f'(x)", "La notation avec un point supérieur pour la vitesse"], "rep": "Le symbole différentiel dx"},
        {"id": "q1_4", "q": "Globalement, effectuer la dérivation d'une fonction revient à étudier son comportement :", "options": ["Local et sa sensibilité aux variations", "Asymptotique aux bornes de l'infini", "Uniquement au point d'origine zéro"], "rep": "Local et sa sensibilité aux variations"},
        {"id": "q1_5", "q": "La fonction dérivée f' associe à chaque nombre x un nombre qui correspond au :", "options": ["Coefficient directeur de la droite tangente", "Rayon de courbure de la fonction", "Milieu du segment sécant"], "rep": "Coefficient directeur de la droite tangente"},
        {"id": "q1_6", "q": "En connaissant le signe de la dérivée sur un intervalle, on peut construire le tableau de :", "options": ["Variation de la fonction", "Signes de la fonction initiale", "Valeurs discrètes par pas de un"], "rep": "Variation de la fonction"},
        {"id": "q1_7", "q": "En physique, la vitesse instantanée d'un mobile est modélisée mathématiquement comme la dérivée de :", "options": ["La position par rapport au temps", "La vitesse par rapport au temps", "L'accélération par rapport à la distance"], "rep": "La position par rapport au temps"},
        {"id": "q1_8", "q": "L'accélération d'un objet en mouvement correspond à la dérivée première de :", "options": ["La vitesse par rapport au temps", "La position par rapport au temps", "La force par rapport à la masse"], "rep": "La vitesse par rapport au temps"},
        {"id": "q1_9", "q": "En économie, la dérivée du coût total par rapport à la quantité produite donne le coût :", "options": ["Marginal", "Moyen", "Fixe"], "rep": "Marginal"},
        {"id": "q1_10", "q": "Dans les algorithmes d'apprentissage automatique, les dérivées servent à optimiser le système via la descente de :", "options": ["Gradient", "Courbe", "Tangente"], "rep": "Gradient"}
    ]

    st.session_state.ordre_quiz_tab1 = ordre_fixe_tab1

    col_double_quiz_tab1, col_double_trous_tab1 = st.columns(2)

    with col_double_quiz_tab1:
        st.markdown("##### Quiz sur les notions de base (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_tab1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab1_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_tab1:
        st.markdown("##### Synthèse sur l'histoire, la définition et l'utilité (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Newton a abordé la dérivation sous l'angle du mouvement à travers la théorie des")
        with c2: st.selectbox("", ["Choisir...", "fluxions", "fractions", "fonctions"], key="tab1_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Leibniz s'est quant à lui concentré sur une approche géométrique liée aux recherches de")
        with c4: st.selectbox("", ["Choisir...", "tangentes", "polynômes", "rationnelles"], key="tab1_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La notion de dérivée mesure précisément la sensibilité d'une courbe face aux")
        with c6: st.selectbox("", ["Choisir...", "variations", "constantes", "limites"], key="tab1_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Géométriquement, la valeur f'(x) représente la valeur du coefficient")
        with c8: st.selectbox("", ["Choisir...", "directeur", "marginal", "ordonné"], key="tab1_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La droite qui effleure la courbe au point d'étude est appelée la droite")
        with c10: st.selectbox("", ["Choisir...", "tangente", "sécante", "verticale"], key="tab1_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'analyse mathématique locale du signe de la dérivée fournit le sens de")
        with c12: st.selectbox("", ["Choisir...", "variation", "continuité", "définition"], key="tab1_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. En cinématique, la dérivée temporelle de la position fournit la vitesse")
        with c14: st.selectbox("", ["Choisir...", "instantanée", "moyenne", "constante"], key="tab1_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le coût de fabrication d'une unité additionnelle en économie est modélisé par le coût")
        with c16: st.selectbox("", ["Choisir...", "marginal", "global", "unitaire"], key="tab1_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Trouver la valeur maximale ou minimale d'un système est une procédure d'")
        with c18: st.selectbox("", ["Choisir...", "optimisation", "dérivation", "itération"], key="tab1_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. En intelligence artificielle, le calcul différentiel permet de minimiser les")
        with c20: st.selectbox("", ["Choisir...", "erreurs", "matrices", "variables"], key="tab1_t10_final", disabled=verrouille, label_visibility="collapsed")
        
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
    st.header("Introduction aux concepts de la dérivation")
    
    # Section Historique
    st.subheader("Historique de la notion")
    st.write(
        "Le calcul différentiel est né au XVIIe siècle pour résoudre des problèmes de géométrie "
        "(tracer des tangentes) et de physique (calculer des vitesses instantanées). "
        "Deux savants ont développé cette méthode de manière indépendante :"
    )
    st.markdown(
        "- **Isaac Newton** : Scientifique anglais qui a abordé la dérivation sous l'angle de la physique "
        "et du mouvement (les fluxions) pour décrire la gravitation universelle.\n"
        "- **Gottfried Wilhelm Leibniz** : Mathématicien allemand qui a adopté une approche plus géométrique "
        "et philosophique. C'est à lui que l'on doit les notations modernes comme le symbole dx."
    )
    
    # Section Définition
    st.subheader("Définition mathématique globale")
    st.write(
        "Dériver une fonction consiste à étudier son comportement local et à mesurer sa sensibilité aux variations. "
        "Si on observe l'évolution d'une courbe, la dérivée représente l'outil mathématique qui indique "
        "si la courbe monte ou descend, et avec quelle intensité."
    )
    st.write(
        "La fonction dérivée, notée f', associe ainsi à chaque nombre x le coefficient directeur "
        "de la droite tangente à la courbe en ce point. Elle permet de dresser précisément le tableau de variation "
        "d'une fonction complexe."
    )
    
    # Section Utilité
    st.subheader("Utilité concrète dans le monde réel")
    st.write(
        "La dérivation intervient dès qu'il s'agit d'analyser un changement ou d'optimiser un système :"
    )
    st.markdown(
        "- **En physique et ingénierie** : Elle permet de définir la vitesse instantanée comme la dérivée de la position "
        "par rapport au temps, ou l'accélération comme la dérivée de la vitesse.\n"
        "- **En économie** : Elle sert à calculer le coût marginal, c'est-à-dire le coût engendré par la production "
        "d'une unité supplémentaire de marchandise.\n"
        "- **En optimisation numérique** : Les algorithmes d'intelligence artificielle utilisent les dérivées (descente de gradient) "
        "pour minimiser les erreurs et ajuster les prédictions."
    )


    # 3. Évaluation et Correction
    st.write("---")
    if "suite_verrouille_tab1" not in st.session_state: st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    afficher_questions_generalites_dynamiques(verrouille=verrou_at1)

    st.write("---")
    st.subheader("Synthese et validation des generalites")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_suite1 = st.checkbox("Je certifie avoir complete les questions de l'Atelier 1.", key="check_certif_generalites_final_net", disabled=verrou_at1)


    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_suite1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_tab1" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1:
                    reponse_eleve = st.session_state.get(f"tab1_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction des Textes a trous (10 points)
            score_t1 = sum([
                st.session_state.get("tab1_t1_final") == "n",
                st.session_state.get("tab1_t2_final") == "terme",
                st.session_state.get("tab1_t3_final") == "explicite",
                st.session_state.get("tab1_t4_final") == "precedent",
                st.session_state.get("tab1_t5_final") == "terme",
                st.session_state.get("tab1_t6_final") == "monotonie",
                st.session_state.get("tab1_t7_final") == "decroissante",
                st.session_state.get("tab1_t8_final") == "courbe",
                st.session_state.get("tab1_t9_final") == "1",
                st.session_state.get("tab1_t10_final") == "infini"
            ])

            st.session_state.score_suite1_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1 = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 1 ---
    if st.session_state.get("suite_verrouille_tab1", False):
        scr1 = st.session_state.get("score_suite1_p1", 0.0)
        scr2 = st.session_state.get("score_suite1_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite1", 0.0)

        from datetime import datetime, timedelta
        timestamp_suite1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER SUITES SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Generalites Suites - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Mathematiques</h1>
                <p>Atelier 1 : Generalites sur les suites numeriques</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz de Notions de Base : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese des modes de definition : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1, 1):
                saisie = st.session_state.get(f"tab1_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_suites += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_suites += """
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
            ("1. Une suite associe un nombre reel a chaque valeur de l'entier naturel $n$", "tab1_t1_final", "n"),
            ("2. La valeur prise par la suite a un rang precis s'appelle un terme", "tab1_t2_final", "terme"),
            ("3. Quand on calcule $u_n$ directement a partir de $n$, la definition est explicite", "tab1_t3_final", "explicite"),
            ("4. Une relation de recurrence lie le terme futur $u_{n+1}$ au terme precedent", "tab1_t4_final", "precedent"),
            ("5. Pour initialiser le calcul d'une suite recurrente, il faut fixer le premier terme", "tab1_t5_final", "terme"),
            ("6. L'etude mathematique de l'evolution des valeurs determine les variations ou la monotonie", "tab1_t6_final", "monotonie"),
            ("7. Si les valeurs de la suite diminuent a chaque etape, la suite est decroissante", "tab1_t7_final", "decroissante"),
            ("8. Le nuage de points obtenu sur un graphique ne doit jamais etre relie par une courbe", "tab1_t8_final", "courbe"),
            ("9. L'indice $n$ progresse toujours de facon discrete, etape par etape, par unite de 1", "tab1_t9_final", "1"),
            ("10. Connaitre le comportement global permet d'anticiper la valeur de la suite a l'infini", "tab1_t10_final", "infini")
        ]

        for num, (enonce, cle_trou, attendu_trou) in enumerate(phrases_trous1, 1):
            saisie_trou = st.session_state.get(cle_trou, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_trou).strip() == str(attendu_trou).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_suites += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie_trou}</td><td>{attendu_trou}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_suites += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html = preparer_nom_fichier("Generalites_Suites").replace(".txt", ".html")
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL HTML",
            data=html_export_suites,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )
        



with tab2:
    st.header("Le nombre dérivé en un point d'une courbe")
    
    st.subheader("Approche théorique par les limites")
    st.write(
        "Soit f une fonction définie sur un intervalle I, et un point A d'abscisse a appartenant à I. "
        "Pour mesurer l'évolution de la fonction juste après le point a, on ajoute une petite variation positive ou négative notée h."
    )
    st.write(
        "On construit un second point B sur la courbe, situé à l'abscisse a + h. "
        "Le coefficient directeur de la droite sécante qui passe par les points A et B se calcule par le rapport suivant :"
    )
    st.latex(r"\text{Taux d'accroissement} = \frac{f(a+h) - f(a)}{h}")
    
    st.write(
        "Le nombre dérivé f'(a) correspond à la valeur vers laquelle se rapproche ce taux d'accroissement "
        "lorsque l'écart h devient infiniment petit, c'est-à-dire lorsqu'il tend vers 0 :"
    )
    st.latex(r"f'(a) = \lim_{h \to 0} \frac{f(a+h) - f(a)}{h}")

    # Section Évaluation et Correction de l'Atelier 2
    st.write("---")
    if "derivation_verrouille_tab2" not in st.session_state: 
        st.session_state.derivation_verrouille_tab2 = False
    verrou_at2 = st.session_state.derivation_verrouille_tab2

    afficher_questions_nombre_derive(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation du nombre dérivé")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_derivation2 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 2.", key="check_certif_derivation_final_net_tab2", disabled=verrou_at2)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_derivation2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_derivation2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q2 = 0.0
            if "ordre_quiz_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2:
                    reponse_eleve = st.session_state.get(f"tab2_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q2 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t2 = sum([
                st.session_state.get("tab2_t1_final") == "accroissement",
                st.session_state.get("tab2_t2_final") == "sécante",
                st.session_state.get("tab2_t3_final") == "0",
                st.session_state.get("tab2_t4_final") == "dérivé",
                st.session_state.get("tab2_t5_final") == "tangente",
                st.session_state.get("tab2_t6_final") == "droite",
                st.session_state.get("tab2_t7_final") == "dérivable",
                st.session_state.get("tab2_t8_final") == "dénominateur",
                st.session_state.get("tab2_t9_final") == "horizontale",
                st.session_state.get("tab2_t10_final") == "local"
            ])

            st.session_state.score_derivation2_p1 = round(float(score_q2), 1)
            st.session_state.score_derivation2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_derivation2 = round(float(score_q2 + score_t2), 1)
            st.session_state.derivation_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 2 ---
    if st.session_state.get("derivation_verrouille_tab2", False):
        scr1_t2 = st.session_state.get("score_derivation2_p1", 0.0)
        scr2_t2 = st.session_state.get("score_derivation2_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_derivation2", 0.0)

        from datetime import datetime, timedelta
        timestamp_derivation2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER NOMBRE DÉRIVÉ SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_derivation2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Nombre Dérivé - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f766e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #111827; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Mathématiques</h1>
                <p>Atelier 2 : Définition et calcul algébrique du nombre dérivé</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_derivation2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                Note obtenue au Quiz du Nombre Dérivé : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du Taux d'Accroissement : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2, 1):
                saisie = st.session_state.get(f"tab2_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_derivation2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_derivation2 += """
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
            ("1. Le rapport f(a+h)-f(a) divisé par h s'appelle le taux d'accroissement", "tab2_t1_final", "accroissement"),
            ("2. Ce taux correspond géométriquement à la pente de la droite sécante", "tab2_t2_final", "sécante"),
            ("3. Pour trouver le nombre dérivé, on étudie la position limite lorsque h tend vers 0", "tab2_t3_final", "0"),
            ("4. La valeur de cette limite finie est appelée le nombre dérivé", "tab2_t4_final", "dérivé"),
            ("5. Le nombre dérivé f'(a) correspond précisément à la pente de la tangente", "tab2_t5_final", "tangente"),
            ("6. Si la courbe présente un point anguleux, la limite à gauche est différente de la limite à droite", "tab2_t6_final", "droite"),
            ("7. Dans ce cas particulier de point anguleux, la fonction n'est pas dérivable", "tab2_t7_final", "dérivable"),
            ("8. Le calcul algébrique nécessite souvent de simplifier l'expression pour éliminer h du dénominateur", "tab2_t8_final", "dénominateur"),
            ("9. Si la valeur f'(a) obtenue est nulle, la tangente associée est alors horizontale", "tab2_t9_final", "horizontale"),
            ("10. Ce point à tangente horizontale correspond généralement à un maximum ou un minimum local", "tab2_t10_final", "local")
        ]

        for num_t, (texte_t, cle_t, attendu_t) in enumerate(phrases_trous2, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"

        v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
        html_export_derivation2 += f"{num_t}{texte_t}{saisie_t}{attendu_t}{v_lbl_t}"
        html_export_derivation2 += """

        """
        st.download_button(
        label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE L'ATELIER 2 (HTML)",
        data=html_export_derivation2,
        file_name=f"Rapport_Nombre_Derive_{n_eleve}_{p_eleve}.html",
        mime="text/html",
        use_container_width=True
        )
            
# --- Onglet 3 : La tangente en un point ---
with tab3:
    st.header("La tangente en un point à une courbe")
    
    st.subheader("Visualisation graphique et dynamique")
    st.write(
        "Utilisez les sélecteurs et curseurs ci-dessous pour analyser le comportement géométrique d'une droite sécante "
        "lorsqu'elle pivote autour du point de contact A pour devenir la droite tangente définitive lorsque l'écart h s'annule."
    )

    # Configuration des fonctions mathématiques pour le tracé Plotly
    choix_f = st.selectbox("Sélectionnez la fonction f(x) :", ["x² (Parabole)", "x³ (Cubique)", "sin(x) (Sinusoïde)"], key="choix_f_tab3")
    
    if choix_f == "x² (Parabole)":
        def f(x): return x**2
        def df(x): return 2*x
    elif choix_f == "x³ (Cubique)":
        def f(x): return x**3
        def df(x): return 3*x**2
    else:
        def f(x): return np.sin(x)
        def df(x): return np.cos(x)

    # Curseurs pour piloter l'affichage géométrique
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        a = st.slider("Abscisse du point de contact (a) :", -3.0, 3.0, 1.0, 0.1, key="slider_a_tab3")
    with col_c2:
        h = st.slider("Écart horizontal (h) pour la sécante (AB) :", 0.01, 2.0, 1.0, 0.05, key="slider_h_tab3")

    # Calcul des coordonnées et des coefficients directeurs
    xA, yA = a, f(a)
    xB, yB = a + h, f(a + h)
    pente_secante = (yB - yA) / h
    pente_tangente = df(a)

    # Construction du domaine de tracé graphique
    x_vals = np.linspace(-4, 4, 200)
    y_vals = f(x_vals)
    y_secante = pente_secante * (x_vals - xA) + yA
    y_tangente = pente_tangente * (x_vals - xA) + yA

    # Tracé interactif avec Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, name="Courbe f(x)", line=dict(color="blue", width=3)))
    fig.add_trace(go.Scatter(x=x_vals, y=y_secante, name="Sécante (AB)", line=dict(color="red", dash="dash")))
    fig.add_trace(go.Scatter(x=x_vals, y=y_tangente, name="Tangente finale", line=dict(color="green", width=2)))
    fig.add_trace(go.Scatter(x=[xA, xB], y=[yA, yB], mode="markers+text", text=["A", "B"], textposition="top left", name="Points de contrôle", marker=dict(color="black", size=10)))
    
    fig.update_layout(xaxis_range=[-4, 4], yaxis_range=[min(y_vals)-2, max(y_vals)+2], title="Analyse géométrique locale")
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"**Équation de la tangente affichée au point A :** y = {pente_tangente:.2f}(x - {a:.2f}) + {yA:.2f}")

    # Section Évaluation et Correction de l'Atelier 3
    st.write("---")
    if "derivation_verrouille_tab3" not in st.session_state: 
        st.session_state.derivation_verrouille_tab3 = False
    verrou_at3 = st.session_state.derivation_verrouille_tab3

    afficher_questions_tangente(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthèse et validation de la tangente géométrique")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_derivation3 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 3.", key="check_certif_derivation_final_net_tab3", disabled=verrou_at3)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_derivation3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_derivation3:
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
                st.session_state.get("tab3_t1_final") == "tangente",
                st.session_state.get("tab3_t2_final") == "dérivé",
                st.session_state.get("tab3_t3_final") == "f'(a)",
                st.session_state.get("tab3_t4_final") == "croissante",
                st.session_state.get("tab3_t5_final") == "décroissante",
                st.session_state.get("tab3_t6_final") == "horizontale",
                st.session_state.get("tab3_t7_final") == "convexe",
                st.session_state.get("tab3_t8_final") == "concave",
                st.session_state.get("tab3_t9_final") == "inflexion",
                st.session_state.get("tab3_t10_final") == "tangente"
            ])

            st.session_state.score_derivation3_p1 = round(float(score_q3), 1)
            st.session_state.score_derivation3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_derivation3 = round(float(score_q3 + score_t3), 1)
            st.session_state.derivation_verrouille_tab3 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 3 ---
    if st.session_state.get("derivation_verrouille_tab3", False):
        scr1_t3 = st.session_state.get("score_derivation3_p1", 0.0)
        scr2_t3 = st.session_state.get("score_derivation3_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_derivation3", 0.0)

        from datetime import datetime, timedelta
        timestamp_derivation3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TANGENTE GÉOMÉTRIQUE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_derivation3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Droite Tangente - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0369a1; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #111827; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Mathématiques</h1>
                <p>Atelier 3 : Propriétés géométriques et équation de la droite tangente</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_derivation3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0369a1;">
                Note obtenue au Quiz de la Tangente : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse Géométrique : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
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
                html_export_derivation3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_derivation3 += """
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

        ("1. La droite qui effleure au plus près une courbe en un point unique est la tangente", "tab3_t1_final", "tangente"),
        ("2. Le coefficient directeur de cette droite est égal au nombre dérivé", "tab3_t2_final", "dérivé"),
        ("3. La formule générale de l'équation de la tangente fait intervenir la valeur de f(a) et de f'(a)", "tab3_t3_final", "f'(a)"),
        ("4. Une pente positive pour la tangente indique que la fonction est localement croissante", "tab3_t4_final", "croissante"),
        ("5. Une pente négative pour la tangente indique que la fonction est localement décroissante", "tab3_t5_final", "décroissante"),
        ("6. Un extremum local d'une fonction dérivable est caractérisé par une tangente horizontale", "tab3_t6_final", "horizontale"),
        ("7. Si la courbe se situe entièrement au-dessus de ses tangentes, elle est convexe", "tab3_t7_final", "convexe"),
        ("8. Si la courbe se situe entièrement en dessous de ses tangentes, elle est concave", "tab3_t8_final", "concave"),
        ("9. Le point de la courbe où la tangente traverse cette dernière s'appelle un point d'inflexion", "tab3_t9_final", "inflexion"),
        ("10. À l'échelle microscopique, zoomer sur le point de contact assimile la courbe à sa tangente", "tab3_t10_final", "tangente")
        ]
        for num_t, (texte_t, cle_t, attendu_t) in enumerate(phrases_trous3, 1):
        saisie_t = st.session_state.get(cle_t, "Choisir...")
        v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
        v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
        html_export_derivation3 += f"{num_t}{texte_t}{saisie_t}{attendu_t}{v_lbl_t}"
        html_export_derivation3 += """




        """
        st.download_button(
        label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE L'ATELIER 3 (HTML)",
        data=html_export_derivation3,
        file_name=f"Rapport_Droite_Tangente_{n_eleve}_{p_eleve}.html",
        mime="text/html",
        use_container_width=True
        )

            
with tab4:
    st.header("Les dérivées des fonctions polynômes de degré n")
    
    st.subheader("Formulaire des règles fondamentales")
    st.write(
        "L'étude des fonctions polynômes repose sur la combinaison linéaire de puissances entières de x. "
        "Le tableau de dérivation usuel se résume par les propriétés indispensables suivantes :"
    )
    st.latex(r"f(x) = k \Longrightarrow f'(x) = 0")
    st.latex(r"f(x) = x^n \Longrightarrow f'(x) = n \cdot x^{n-1}")
    st.latex(r"(u(x) + v(x))' = u'(x) + v'(x)")

    # Section Évaluation et Correction de l'Atelier 4
    st.write("---")
    if "derivation_verrouille_tab4" not in st.session_state: 
        st.session_state.derivation_verrouille_tab4 = False
    verrou_at4 = st.session_state.derivation_verrouille_tab4

    afficher_questions_polynomes(verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation des fonctions polynômes")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_derivation4 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 4.", key="check_certif_derivation_final_net_tab4", disabled=verrou_at4)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_derivation4_official_net", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_derivation4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q4 = 0.0
            if "ordre_quiz_tab4" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4:
                    reponse_eleve = st.session_state.get(f"tab4_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q4 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t4 = sum([
                st.session_state.get("tab4_t1_final") == "0",
                st.session_state.get("tab4_t2_final") == "a",
                st.session_state.get("tab4_t3_final") == "facteur",
                st.session_state.get("tab4_t4_final") == "1",
                st.session_state.get("tab4_t5_final") == "réels",
                st.session_state.get("tab4_t6_final") == "somme",
                st.session_state.get("tab4_t7_final") == "2x",
                st.session_state.get("tab4_t8_final") == "x²",
                st.session_state.get("tab4_t9_final") == "constante",
                st.session_state.get("tab4_t10_final") == "1"
            ])

            st.session_state.score_derivation4_p1 = round(float(score_q4), 1)
            st.session_state.score_derivation4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_derivation4 = round(float(score_q4 + score_t4), 1)
            st.session_state.derivation_verrouille_tab4 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 4 ---
    if st.session_state.get("derivation_verrouille_tab4", False):
        scr1_t4 = st.session_state.get("score_derivation4_p1", 0.0)
        scr2_t4 = st.session_state.get("score_derivation4_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_derivation4", 0.0)

        from datetime import datetime, timedelta
        timestamp_derivation4 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER FONCTIONS POLYNÔMES SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_derivation4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Fonctions Polynômes - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4338ca; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #111827; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Mathématiques</h1>
                <p>Atelier 4 : Dérivation algébrique des fonctions polynômes de degré n</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_derivation4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4338ca;">
                Note obtenue au Quiz des Polynômes : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse Algébrique : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4, 1):
                saisie = st.session_state.get(f"tab4_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_derivation4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_derivation4 += """
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
            ("1. La dérivée d'une fonction constante est toujours égale à 0", "tab4_t1_final", "0"),
            ("2. La fonction affine f(x) = ax + b possède une dérivée constante égale à a", "tab4_t2_final", "a"),
            ("3. Pour dériver une puissance, l'exposant n descend en tant que facteur", "tab4_t3_final", "facteur"),
            ("4. Après dérivation de x^n, la nouvelle puissance résiduelle devient de degré n moins 1", "tab4_t4_final", "1"),
            ("5. La dérivation est une opération linéaire qui conserve les coefficients multiplicatifs réels", "tab4_t5_final", "réels"),
            ("6. Dériver un polynôme se réalise terme à terme en appliquant la formule de la somme", "tab4_t6_final", "somme"),
            ("7. La dérivée de la fonction f(x) = x² est l'expression linéaire 2x", "tab4_t7_final", "2x"),
            ("8. La dérivée de x³ est égale à 3 multiplié par x²", "tab4_t8_final", "x²"),
            ("9. Un monôme de degré 1 se transforme après dérivation en une valeur constante", "tab4_t9_final", "constante"),
            ("10. L'opération de dérivation réduit le degré du polynôme initial de 1", "tab4_t10_final", "1")
        ]

        for num_t, (texte_t, cle_t, attendu_t) in enumerate(phrases_trous4, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_derivation4 += f"<tr><td>{num_t}</td><td>{texte_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_derivation4 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE L'ATELIER 4 (HTML)",
            data=html_export_derivation4,
            file_name=f"Rapport_Fonctions_Polynomes_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
            )

            
with tab5:
    st.header("Les dérivées des fonctions rationnelles")
    
    st.subheader("Formules des quotients et inverses")
    st.write(
        "Une fonction rationnelle se présente sous la forme d'un quotient de deux fonctions polynômes. "
        "Leur dérivation nécessite l'application de règles spécifiques afin de gérer la présence du dénominateur :"
    )
    st.latex(r"f(x) = \frac{1}{x} \Longrightarrow f'(x) = -\frac{1}{x^2}")
    st.latex(r"\left(\frac{1}{v}\right)' = -\frac{v'}{v^2}")
    st.latex(r"\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}")

    # Section Évaluation et Correction de l'Atelier 5
    st.write("---")
    if "derivation_verrouille_tab5" not in st.session_state: 
        st.session_state.derivation_verrouille_tab5 = False
    verrou_at5 = st.session_state.derivation_verrouille_tab5

    afficher_questions_rationnelles(verrouille=verrou_at5)

    st.write("---")
    st.subheader("Synthèse et validation des fonctions rationnelles")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_derivation5 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 5.", key="check_certif_derivation_final_net_tab5", disabled=verrou_at5)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_derivation5_official_net", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_derivation5:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q5 = 0.0
            if "ordre_quiz_tab5" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5:
                    reponse_eleve = st.session_state.get(f"tab5_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q5 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t5 = sum([
                st.session_state.get("tab5_t1_final") == "polynômes",
                st.session_state.get("tab5_t2_final") == "x²",
                st.session_state.get("tab5_t3_final") == "moins",
                st.session_state.get("tab5_t4_final") == "positif",
                st.session_state.get("tab5_t5_final") == "dénominateur",
                st.session_state.get("tab5_t6_final") == "v",
                st.session_state.get("tab5_t7_final") == "v'",
                st.session_state.get("tab5_t8_final") == "calculs",
                st.session_state.get("tab5_t9_final") == "négative",
                st.session_state.get("tab5_t10_final") == "rationnelle"
            ])

            st.session_state.score_derivation5_p1 = round(float(score_q5), 1)
            st.session_state.score_derivation5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_derivation5 = round(float(score_q5 + score_t5), 1)
            st.session_state.derivation_verrouille_tab5 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 5 ---
    if st.session_state.get("derivation_verrouille_tab5", False):
        scr1_t5 = st.session_state.get("score_derivation5_p1", 0.0)
        scr2_t5 = st.session_state.get("score_derivation5_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_derivation5", 0.0)

        from datetime import datetime, timedelta
        timestamp_derivation5 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER FONCTIONS RATIONNELLES SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_derivation5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Fonctions Rationnelles - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b91c1c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #111827; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Mathématiques</h1>
                <p>Atelier 5 : Dérivation des fonctions rationnelles et étude des quotients</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_derivation5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                Note obtenue au Quiz des Quotients : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse Algébrique : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab5" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5, 1):
                saisie = st.session_state.get(f"tab5_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_derivation5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_derivation5 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous5 = [
            ("1. Une fonction rationnelle est définie comme le quotient de deux fonctions polynômes", "tab5_t1_final", "polynômes"),
            ("2. La dérivée de la fonction de référence 1/x est égale à -1 divisé par x²", "tab5_t2_final", "x²"),
            ("3. La formule du quotient (u/v)' possède un numérateur contenant le signe opératoire moins", "tab5_t3_final", "moins"),
            ("4. Le dénominateur de la dérivée d'un quotient est toujours strictement positif", "tab5_t4_final", "positif"),
            ("5. Le domaine de dérivabilité d'un quotient exclut les valeurs qui annulent le dénominateur", "tab5_t5_final", "dénominateur"),
            ("6. Dans la formule du quotient, le premier terme développé au numérateur est u' multiplié par v", "tab5_t6_final", "v"),
            ("7. Le second terme retranché au numérateur du quotient correspond au produit de u par v'", "tab5_t7_final", "v'"),
            ("8. Le carré présent au dénominateur ne doit en aucun cas être développé lors des calculs", "tab5_t8_final", "calculs"),
            ("9. La fonction inverse est strictement décroissante car sa dérivée est négative", "tab5_t9_final", "négative"),
            ("10. Maîtriser le numérateur permet de localiser les changements de sens de la fonction rationnelle", "tab5_t10_final", "rationnelle")
        ]

        for num_t, (texte_t, cle_t, attendu_t) in enumerate(phrases_trous5, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_derivation5 += f"<tr><td>{num_t}</td><td>{texte_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_derivation5 += """
                </tbody>
            </table>
        </body>

        """
        st.download_button(
        label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE L'ATELIER 5 (HTML)",
        data=html_export_derivation5,
        file_name=f"Rapport_Fonctions_Rationnelles_{n_eleve}_{p_eleve}.html",
        mime="text/html",
        use_container_width=True
        )


        
with tab6:
    st.header("Les dérivées des autres fonctions")
    
    st.subheader("Formulaire des fonctions trigonométriques et composées")
    st.write(
        "Ce dernier module regroupe les fonctions circulaires (sinus et cosinus), la fonction racine carrée, "
        "ainsi que la formule d'introduction à la dérivation des fonctions composées de type affine :"
    )
    st.latex(r"f(x) = \sin(x) \Longrightarrow f'(x) = \cos(x)")
    st.latex(r"f(x) = \cos(x) \Longrightarrow f'(x) = -\sin(x)")
    st.latex(r"f(x) = \sqrt{x} \Longrightarrow f'(x) = \frac{1}{2\sqrt{x}} \quad (\text{pour } x > 0)")
    st.latex(r"f(x) = u(ax + b) \Longrightarrow f'(x) = a \cdot u'(ax + b)")

    # Section Évaluation et Correction de l'Atelier 6
    st.write("---")
    if "derivation_verrouille_tab6" not in st.session_state: 
        st.session_state.derivation_verrouille_tab6 = False
    verrou_at6 = st.session_state.derivation_verrouille_tab6

    afficher_questions_autres_fonctions(verrouille=verrou_at6)

    st.write("---")
    st.subheader("Synthèse et validation des fonctions circulaires et composées")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_derivation6 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 6.", key="check_certif_derivation_final_net_tab6", disabled=verrou_at6)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_derivation6_official_net", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_derivation6:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q6 = 0.0
            if "ordre_quiz_tab6" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6:
                    reponse_eleve = st.session_state.get(f"tab6_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q6 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t6 = sum([
                st.session_state.get("tab6_t1_final") == "cos(x)",
                st.session_state.get("tab6_t2_final") == "-sin(x)",
                st.session_state.get("tab6_t3_final") == "dérivable",
                st.session_state.get("tab6_t4_final") == "infinie",
                st.session_state.get("tab6_t5_final") == "facteur",
                st.session_state.get("tab6_t6_final") == "inchangé",
                st.session_state.get("tab6_t7_final") == "croissante",
                st.session_state.get("tab6_t8_final") == "périodique",
                st.session_state.get("tab6_t9_final") == "dénominateur",
                st.session_state.get("tab6_t10_final") == "chapitre"
            ])

            st.session_state.score_derivation6_p1 = round(float(score_q6), 1)
            st.session_state.score_derivation6_p2 = round(float(score_t6), 1)
            st.session_state.score_final_derivation6 = round(float(score_q6 + score_t6), 1)
            st.session_state.derivation_verrouille_tab6 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 6 ---
    if st.session_state.get("derivation_verrouille_tab6", False):
        scr1_t6 = st.session_state.get("score_derivation6_p1", 0.0)
        scr2_t6 = st.session_state.get("score_derivation6_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_derivation6", 0.0)

        from datetime import datetime, timedelta
        timestamp_derivation6 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER AUTRES FONCTIONS SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_derivation6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Autres Fonctions - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0d9488; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #111827; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Mathématiques</h1>
                <p>Atelier 6 : Dérivation des fonctions trigonométriques, racines et composées affines</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_derivation6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
                Note obtenue au Quiz des Fonctions Spécifiques : <strong>{scr1_t6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse Circulaire : <strong>{scr2_t6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s_t6:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab6" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6, 1):
                saisie = st.session_state.get(f"tab6_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_derivation6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_derivation6 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous6 = [
            ("1. La fonction sinus associe à chaque valeur réelle une dérivée égale à cos(x)", "tab6_t1_final", "cos(x)"),
            ("2. La fonction cosinus voit ses variations dictées par sa dérivée égale à -sin(x)", "tab6_t2_final", "-sin(x)"),
            ("3. La fonction racine carrée est continue en zéro mais n'y est pas dérivable", "tab6_t3_final", "dérivable"),
            ("4. La présence de la racine au dénominateur de sa dérivée crée une pente infinie", "tab6_t4_final", "infinie"),
            ("5. Dériver la forme u(ax+b) demande d'extraire le coefficient a en tant que facteur", "tab6_t5_final", "facteur"),
            ("6. Dans l'expression finale d'une composée, l'argument intérieur ax+b reste inchangé", "tab6_t6_final", "inchangé"),
            ("7. La courbe représentative de la fonction racine carrée est strictement croissante", "tab6_t7_final", "croissante"),
            ("8. Les fonctions sinus et cosinus alternent leurs variations de manière périodique", "tab6_t8_final", "périodique"),
            ("9. La dérivée de la fonction f(x) = \u221ax possède la valeur constante 2 au dénominateur", "tab6_t9_final", "dénominateur"),
            ("10. Valider ce dernier bloc achève l'étude formelle des fonctions usuelles de ce chapitre", "tab6_t10_final", "chapitre")
        ]

        for num_t, (texte_t, cle_t, attendu_t) in enumerate(phrases_trous6, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"

        html_export_derivation6 += f"{num_t}{texte_t}{saisie_t}{attendu_t}{v_lbl_t}"
        html_export_derivation6 += """




        """
        st.download_button(
        label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE L'ATELIER 6 (HTML)",
        data=html_export_derivation6,
        file_name=f"Rapport_Autres_Fonctions_{n_eleve}_{p_eleve}.html",
        mime="text/html",
        use_container_width=True
        )


            
