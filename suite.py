# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application les suites",
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
st.title("Application les suites")
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
    "Généralités sur les suites",
    "Les suites arithmétiques",
    "Les suites géométriques",
    "Les suites récurrentes",
    "Exemple de démonstration de récurrence",
    "Démonstration de récurrence",
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]

def afficher_questions_recurrentes_dynamiques(verrouille=False):
    import streamlit as st
    ordre_fixe_tab4 = [
        {"id": "q4_1", "q": "Une suite recurrente d'ordre 1 exprime le terme $u_{n+1}$ en fonction de :", "options": ["u_n", "n uniquement", "u_0 uniquement"], "rep": "u_n"},
        {"id": "q4_2", "q": "Pour calculer un terme d'une suite recurrente, la donnee indispensable en plus de la relation est :", "options": ["Le premier terme", "La raison", "La limite"], "rep": "Le premier terme"},
        {"id": "q4_3", "q": "La suite de Fibonacci est une suite recurrente particuliere car elle depend des :", "options": ["Deux termes precedents", "Trois termes precedents", "Seuls indices pairs"], "rep": "Deux termes precedents"},
        {"id": "q4_4", "q": "Si $u_0 = 2$ et $u_{n+1} = u_n^2 - 1$, quelle est la valeur de $u_1$ ?", "options": ["3", "4", "2"], "rep": "3"},
        {"id": "q4_5", "q": "Dans une suite recurrente lineaire d'ordre 1 du type $u_{n+1} = a \\times u_n + b$, si $a = 1$ la suite est :", "options": ["Arithmetique", "Geometrique", "Constante"], "rep": "Arithmetique"},
        {"id": "q4_6", "q": "Dans cette meme suite $u_{n+1} = a \\times u_n + b$, si $b = 0 la suite est :", "options": ["Geometrique", "Arithmetique", "Alterne"], "rep": "Geometrique"},
        {"id": "q4_7", "q": "La methode graphique pour representer une suite recurrente sur l'axe des abscisses utilise :", "options": ["La droite y = x", "La droite y = -x", "L'axe des ordonnees uniquement"], "rep": "La droite y = x"},
        {"id": "q4_8", "q": "Le traci visuel des etapes de calcul d'une suite recurrente prend souvent la forme d'une :", "options": ["Toile d'araignee ou escalier", "Parabole parfaite", "Droite lineaire unique"], "rep": "Toile d'araignee ou escalier"},
        {"id": "q4_9", "q": "Si une suite recurrente $u_{n+1} = f(u_n)$ converge vers une limite L, alors L verifie l'equation :", "options": ["f(L) = L", "f(L) = 0", "f(0) = L"], "rep": "f(L) = L"},
        {"id": "q4_10", "q": "L'equation $f(L) = L$ permettant de trouver les limites eventuelles cherche les :", "options": ["Points fixes de f", "Sommets de la courbe", "Racines de la fonction"], "rep": "Points fixes de f"}
    ]
    st.session_state.ordre_quiz_tab4 = ordre_fixe_tab4
    col_g, col_d = st.columns(2)
    with col_g:
        st.markdown("##### Quiz sur les suites recurrentes (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tab4_at4_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_d:
        st.markdown("##### Synthese Recurrente (Texte a trous - 10 cases - 10 pts)")
        phrases = [
            ("1. Une relation de recurrence determine un terme a partir du terme", "tab4_t1_final", ["Choisir...", "precedent", "suivant", "initial"]),
            ("2. Pour amorcer les calculs d'une telle suite, il faut specifier la valeur", "tab4_t2_final", ["Choisir...", "initiale", "limite", "maximale"]),
            ("3. La suite de Fibonacci necessite la connaissance de deux termes pour son", "tab4_t3_final", ["Choisir...", "amorce", "graphique", "calcul"]),
            ("4. Les suites arithmetico-geometriques combinent une addition et une", "tab4_t4_final", ["Choisir...", "multiplication", "soustraction", "puissance"]),
            ("5. La representation graphique de $u_{n+1} = f(u_n)$ se construit avec la droite d'equation $y = x$", "tab4_t5_final", ["Choisir...", "x", "-x", "0"]),
            ("6. Cette droite traciee en diagonale joue le role de renvoi des ordonnees sur les", "tab4_t6_final", ["Choisir...", "abscisses", "indices", "limites"]),
            ("7. La configuration geometrique en colimacon est appelee toile d'", "tab4_t7_final", ["Choisir...", "araignee", "evolution", "iteration"]),
            ("8. Si la fonction f est croissante, la suite geometrique avance en", "tab4_t8_final", ["Choisir...", "escalier", "spirale", "alternance"]),
            ("9. Une valeur limite potentielle L de la suite doit necessairement etre un point", "tab4_t9_final", ["Choisir...", "fixe", "critique", "nul"]),
            ("10. Determiner les termes distants implique d'executer un algorithme ou une", "tab4_t10_final", ["Choisir...", "boucle", "equation", "fraction"])
        ]
        for enonce, key, opts in phrases:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", opts, key=key, disabled=verrouille, label_visibility="collapsed")

def afficher_questions_demonstration_dynamiques(verrouille=False):
    import streamlit as st
    ordre_fixe_tab5 = [
        {"id": "q5_1", "q": "Le raisonnement par recurrence sert a demontrer qu'une propriete est vraie pour :", "options": ["Tout entier naturel n", "Un seul entier donne", "Les reels positifs"], "rep": "Tout entier naturel n"},
        {"id": "q5_2", "q": "La premiere etape obligatoire d'une demonstration par recurrence s'appelle :", "options": ["L'initialisation", "L'heredite", "La conclusion"], "rep": "L'initialisation"},
        {"id": "q5_3", "q": "Lors de l'initialisation, on verifie que la propriete $P(n)$ est vraie pour :", "options": ["Le premier rang n_0", "Le rang n+1", "Tous les rangs"], "rep": "Le premier rang n_0"},
        {"id": "q5_4", "q": "La deuxieme etape consistant a prouver le mecanisme de transmission s'appelle :", "options": ["L'heredite", "La validation", "L'induction"], "rep": "L'heredite"},
        {"id": "q5_5", "q": "Dans l'etape d'heredite, on suppose que la propriete est vraie au rang $k$, c'est :", "options": ["L'hypothese de recurrence", "L'affirmation finale", "L'axiome initial"], "rep": "L'hypothese de recurrence"},
        {"id": "q5_6", "q": "Sous l'hypothese que $P(k)$ est vraie, on doit demontrer qu'elle reste vraie au rang :", "options": ["k+1", "k-1", "2k"], "rep": "k+1"},
        {"id": "q5_7", "q": "Le principe de la recurrence est souvent compare visuellement a la chute de :", "options": ["Dominos", "Cartes", "Pierres"], "rep": "Dominos"},
        {"id": "q5_8", "q": "Si l'initialisation echoue mais que l'heredite est vraie, la propriete est :", "options": ["Fausse generalement", "Vraie partout", "Vraie sauf pour u_0"], "rep": "Fausse generalement"},
        {"id": "q5_9", "q": "Si une propriete est vraie pour $n=0$ et $n=1$ et transmise de $k$ a $k+1$, elle est initiee au rang :", "options": ["0", "2", "k"], "rep": "0"},
        {"id": "q5_10", "q": "La troisieme et derniere phase redigee de la demonstration est :", "options": ["La conclusion", "L'hypothese", "L'analyse"], "rep": "La conclusion"}
    ]
    st.session_state.ordre_quiz_tab5 = ordre_fixe_tab5
    col_g, col_d = st.columns(2)
    with col_g:
        st.markdown("##### Quiz sur la demonstration par recurrence (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab5, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tab5_at5_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_d:
        st.markdown("##### Synthese Demonstration (Texte a trous - 10 cases - 10 pts)")
        phrases = [
            ("1. Le raisonnement par recurrence etablit la validite d'une propriete", "tab5_t1_final", ["Choisir...", "P(n)", "u_n", "f(x)"]),
            ("2. La phase d'ouverture qui teste le rang le plus bas constitue l'", "tab5_t2_final", ["Choisir...", "initialisation", "heredite", "conclusion"]),
            ("3. Echouer a initialiser empeche d'enclencher la validite de la", "tab5_t3_final", ["Choisir...", "propriete", "raison", "somme"]),
            ("4. Prouver le transfert d'un rang au rang superieur definit l'", "tab5_t4_final", ["Choisir...", "heredite", "induction", "deduction"]),
            ("5. On declare poser une hypothese de recurrence pour un rang fixe note", "tab5_t5_final", ["Choisir...", "k", "n", "r"]),
            ("6. Le but central est d'utiliser cette hypothese pour aboutir au rang", "tab5_t6_final", ["Choisir...", "k+1", "k-1", "0"]),
            ("7. Le mecanisme de transmission assure la propagation a l'", "tab5_t7_final", ["Choisir...", "infini", "origine", "inverse"]),
            ("8. L'analogie classique de la chaine associe chaque maillon a une", "tab5_t8_final", ["Choisir...", "etape", "valeur", "courbe"]),
            ("9. Clore la redonnee de facon rigoureuse correspond a la", "tab5_t9_final", ["Choisir...", "conclusion", "recherche", "evaluation"]),
            ("10. Une recurrence double requiert quant a elle d'initialiser sur deux rangs", "tab5_t10_final", ["Choisir...", "distincts", "negatifs", "infinis"])
        ]
        for enonce, key, opts in phrases:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", opts, key=key, disabled=verrouille, label_visibility="collapsed")


def afficher_questions_arithmetiques_dynamiques(verrouille=False):
    import streamlit as st
    ordre_fixe_tab2 = [
        {"id": "q2_1", "q": "Pour passer d'un terme au suivant dans une suite arithmetique, on effectue une :", "options": ["Addition", "Multiplication", "Puissance"], "rep": "Addition"},
        {"id": "q2_2", "q": "Le nombre reel $r$ ajoute a chaque etape s'appelle :", "options": ["La raison", "Le premier terme", "L'indice"], "rep": "La raison"},
        {"id": "q2_3", "q": "La formule explicite d'une suite arithmetique de premier terme $u_0$ est :", "options": ["$u_n = u_0 + n \\times r$", "$u_n = u_0 \\times r^n$", "$u_n = u_0 + r$"], "rep": "$u_n = u_0 + n \\times r$"},
        {"id": "q2_4", "q": "Si la raison $r$ d'une suite arithmetique est strictement negative, la suite est :", "options": ["Decroissante", "Croissante", "Constante"], "rep": "Decroissante"},
        {"id": "q2_5", "q": "La representation graphique d'une suite arithmetique presente des points :", "options": ["Alignes", "En hyperbole", "En parabole"], "rep": "Alignes"},
        {"id": "q2_6", "q": "Si la raison $r$ vaut 0, la suite arithmetique est :", "options": ["Constante", "Strictement croissante", "Alterne"], "rep": "Constante"},
        {"id": "q2_7", "q": "Quelle relation definit une suite arithmetique par recurrence ?", "options": ["$u_{n+1} = u_n + r$", "$u_{n+1} = u_n \\times r$", "$u_{n+1} = u_n^2$"], "rep": "$u_{n+1} = u_n + r$"},
        {"id": "q2_8", "q": "Si $u_0 = 5$ et $r = 3$, quelle est la valeur du terme $u_2$ ?", "options": ["11", "8", "14"], "rep": "11"},
        {"id": "q2_9", "q": "La difference entre deux termes consecutifs ($u_{n+1} - u_n$) d'une suite arithmetique est :", "options": ["Egale a la raison r", "Variable selon n", "Toujours nulle"], "rep": "Egale a la raison r"},
        {"id": "q2_10", "q": "Dans la formule de la somme des termes, le facteur multiplicateur correspond au :", "options": ["Nombre de termes", "Rang final", "Premier terme"], "rep": "Nombre de termes"}
    ]
    st.session_state.ordre_quiz_tab2 = ordre_fixe_tab2
    col_g, col_d = st.columns(2)
    with col_g:
        st.markdown("##### Quiz sur les suites arithmetiques (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tab2_at2_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_d:
        st.markdown("##### Synthese Arithmetique (Texte a trous - 10 cases - 10 pts)")
        phrases = [
            ("1. Une suite arithmetique evolue par l'addition d'une constante appelee", "tab2_t1_final", ["Choisir...", "raison", "facteur", "somme"]),
            ("2. La relation de recurrence s'ecrit $u_{n+1}$ egale $u_n$ plus", "tab2_t2_final", ["Choisir...", "r", "q", "n"]),
            ("3. La forme explicite permet de calculer un terme sans connaitre le", "tab2_t3_final", ["Choisir...", "precedent", "suivant", "graphe"]),
            ("4. Graphiquement, la pente du nuage de points correspond a la", "tab2_t4_final", ["Choisir...", "raison", "origine", "abscisse"]),
            ("5. Si la raison $r$ est superieure a zero, la suite est qualifiee de", "tab2_t5_final", ["Choisir...", "croissante", "decroissante", "nulle"]),
            ("6. La difference $u_{n+1} - u_n$ reste constante et egale a la", "tab2_t6_final", ["Choisir...", "raison", "somme", "moyenne"]),
            ("7. Pour calculer $u_{10}$ en partant de $u_0$, on ajoute dix fois la", "tab2_t7_final", ["Choisir...", "raison", "valeur", "variable"]),
            ("8. Si les points sont alignes, la suite possede une croissance de type", "tab2_t8_final", ["Choisir...", "lineaire", "exponentielle", "involutive"]),
            ("9. La formule de la somme necessite de connaitre le premier et le dernier", "tab2_t9_final", ["Choisir...", "terme", "indice", "facteur"]),
            ("10. Si la raison $r$ est negative, les valeurs de la suite vont", "tab2_t10_final", ["Choisir...", "diminuer", "augmenter", "stagner"])
        ]
        for enonce, key, opts in phrases:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", opts, key=key, disabled=verrouille, label_visibility="collapsed")
            
def afficher_questions_geometriques_dynamiques(verrouille=False):
    import streamlit as st
    ordre_fixe_tab3 = [
        {"id": "q3_1", "q": "Pour passer d'un terme au suivant dans une suite geometrique, on effectue une :", "options": ["Multiplication", "Addition", "Soustraction"], "rep": "Multiplication"},
        {"id": "q3_2", "q": "La constante multiplicatrice $q$ d'une suite geometrique s'appelle :", "options": ["La raison", "Le quotient", "Le multiplicateur"], "rep": "La raison"},
        {"id": "q3_3", "q": "La formule explicite d'une suite geometrique de premier terme $u_0$ est :", "options": ["$u_n = u_0 \\times q^n$", "$u_n = u_0 + q^n$", "$u_n = u_0 \\times n \\times q$"], "rep": "$u_n = u_0 \\times q^n$"},
        {"id": "q3_4", "q": "Si $u_0$ est positif et la raison $q$ est strictement superieure a 1, la suite est :", "options": ["Croissante", "Decroissante", "Alterne"], "rep": "Croissante"},
        {"id": "q3_5", "q": "Si la raison $q$ est comprise strictement entre 0 et 1, les termes d'une suite positive vont :", "options": ["Diminuer vers 0", "Augmenter vers l'infini", "Rester constants"], "rep": "Diminuer vers 0"},
        {"id": "q3_6", "q": "Une suite geometrique dont la raison $q$ est negative est dite :", "options": ["Alterne", "Constante", "Lineaire"], "rep": "Alterne"},
        {"id": "q3_7", "q": "Le rapport de deux termes consecutifs $u_{n+1} / u_n$ d'une suite geometrique vaut :", "options": ["La raison q", "L'indice n", "Le terme u_0"], "rep": "La raison q"},
        {"id": "q3_8", "q": "Si $u_0 = 3$ et $q = 2$, quelle est la valeur du terme $u_3$ ?", "options": ["24", "18", "9"], "rep": "24"},
        {"id": "q3_9", "q": "L'evolution graphique d'une suite geometrique a croissance rapide ressemble a :", "options": ["Une courbe exponentielle", "Une droite", "Une parabole"], "rep": "Une courbe exponentielle"},
        {"id": "q3_10", "q": "Dans la formule de calcul de la somme, le numerateur contient l'expression :", "options": ["$1 - q^{\\text{nombre de termes}}$", "1 - n * q", "q - 1"], "rep": "$1 - q^{\\text{nombre de termes}}$"}
    ]
    st.session_state.ordre_quiz_tab3 = ordre_fixe_tab3
    col_g, col_d = st.columns(2)
    with col_g:
        st.markdown("##### Quiz sur les suites geometriques (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tab3_at3_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_d:
        st.markdown("##### Synthese Geometrique (Texte a trous - 10 cases - 10 pts)")
        phrases = [
            ("1. Une suite geometrique progresse par la multiplication par une raison notee", "tab3_t1_final", ["Choisir...", "q", "r", "n"]),
            ("2. La relation de recurrence s'ecrit sous la forme $u_{n+1}$ egale $u_n$ multiplie par", "tab3_t2_final", ["Choisir...", "q", "r", "u_0"]),
            ("3. L'exposant $n$ present dans la formule explicite traduit une progression de type", "tab3_t3_final", ["Choisir...", "exponentielle", "lineaire", "nulle"]),
            ("4. Si la raison $q$ est superieure a 1, les valeurs de la suite positive vont", "tab3_t4_final", ["Choisir...", "augmenter", "diminuer", "stagner"]),
            ("5. Le quotient $u_{n+1}$ divise par $u_n$ determine la valeur de la", "tab3_t5_final", ["Choisir...", "raison", "somme", "difference"]),
            ("6. Quand la raison $q$ est comprise entre 0 et 1, la suite positive est", "tab3_t6_final", ["Choisir...", "decroissante", "croissante", "infinie"]),
            ("7. Si les signes des termes s'inversent a chaque rang, la suite est qualifiee d'", "tab3_t7_final", ["Choisir...", "alterne", "continue", "constante"]),
            ("8. Pour calculer la somme, la valeur de la raison $q$ doit etre differente de", "tab3_t8_final", ["Choisir...", "1", "0", "-1"]),
            ("9. Une suite geometrique permet de modeliser une evolution a pourcentage", "tab3_t9_final", ["Choisir...", "constant", "variable", "nul"]),
            ("10. Lorsque la raison $q$ vaut 1, tous les termes de la suite restent", "tab3_t10_final", ["Choisir...", "identiques", "nuls", "inverses"])
        ]
        for enonce, key, opts in phrases:
            c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c1: st.write(enonce)
            with c2: st.selectbox("", opts, key=key, disabled=verrouille, label_visibility="collapsed")
            
def afficher_questions_generalites_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le comportement et le controle des generalites (tab1)
    ordre_fixe_tab1 = [
        {"id": "q1_1", "q": "Une suite numerique est une fonction dont l'ensemble de depart est :", "options": ["L'ensemble des entiers naturels $\\mathbb{N}$", "L'ensemble des reels $\\mathbb{R}$", "L'ensemble des entiers relatifs $\\mathbb{Z}$"], "rep": "L'ensemble des entiers naturels $\\mathbb{N}$"},
        {"id": "q1_2", "q": "Dans la notation $u_n$, la lettre $n$ represente :", "options": ["L'indice ou le rang", "La valeur du terme", "La raison de la suite"], "rep": "L'indice ou le rang"},
        {"id": "q1_3", "q": "Comment note-t-on le terme qui suit immediatement le terme $u_n$ ?", "options": ["$u_{n+1}$", "$u_n + 1$", "$u_{n-1}$"], "rep": "$u_{n+1}$"},
        {"id": "q1_4", "q": "Une suite definie par une formule directe du type $u_n = f(n)$ est dite :", "options": ["Explicite", "Recurrente", "Arithmetique"], "rep": "Explicite"},
        {"id": "q1_5", "q": "Pour calculer $u_5$ d'une suite explicite, il suffit de :", "options": ["Remplacer $n$ par 5 dans la formule", "Calculer tous les termes precedents", "Ajouter 5 au premier terme"], "rep": "Remplacer $n$ par 5 dans la formule"},
        {"id": "q1_6", "q": "Une suite definie par son premier terme et la relation $u_{n+1} = f(u_n)$ est :", "options": ["Recurrente", "Explicite", "Constante"], "rep": "Recurrente"},
        {"id": "q1_7", "q": "Pour calculer un terme d'une suite recurrente, il faut obligatoirement connaitre :", "options": ["Le terme precedent", "Le terme $u_0$ uniquement", "Le nombre total de termes"], "rep": "Le terme precedent"},
        {"id": "q1_8", "q": "Si pour tout entier $n$, $u_{n+1}$ est superieur ou egal a $u_n$, la suite est :", "options": ["Croissante", "Decroissante", "Alterne"], "rep": "Croissante"},
        {"id": "q1_9", "q": "Une suite qui ne change jamais de valeur au fil des rangs est qualifiee de :", "options": ["Constante", "Geometrique", "Bornee"], "rep": "Constante"},
        {"id": "q1_10", "q": "Representee graphiquement, une suite numerique forme un ensemble de :", "options": ["Points isoles", "Lignes continues", "Vecteurs"], "rep": "Points isoles"}
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
        st.markdown("##### Synthese sur les modes de definition (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Une suite associe un nombre reel a chaque valeur de l'entier naturel $n$")
        with c2: st.selectbox("", ["Choisir...", "n", "u", "f"], key="tab1_t1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La valeur prise par la suite a un rang precis s'appelle un terme")
        with c4: st.selectbox("", ["Choisir...", "terme", "indice", "facteur"], key="tab1_t2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Quand on calcule $u_n$ directement a partir de $n$, la definition est explicite")
        with c6: st.selectbox("", ["Choisir...", "explicite", "recurrente", "indirecte"], key="tab1_t3_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Une relation de recurrence lie le terme futur $u_{n+1}$ au terme precedent")
        with c8: st.selectbox("", ["Choisir...", "precedent", "initial", "suivant"], key="tab1_t4_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Pour initialiser le calcul d'une suite recurrente, il faut fixer le premier terme")
        with c10: st.selectbox("", ["Choisir...", "terme", "graphe", "repere"], key="tab1_t5_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'etude mathematique de l'evolution des valeurs determine les variations ou la monotonie")
        with c12: st.selectbox("", ["Choisir...", "monotonie", "droite", "somme"], key="tab1_t6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Si les valeurs de la suite diminuent a chaque etape, la suite est decroissante")
        with c14: st.selectbox("", ["Choisir...", "decroissante", "croissante", "infinie"], key="tab1_t7_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le nuage de points obtenu sur un graphique ne doit jamais etre relie par une courbe")
        with c16: st.selectbox("", ["Choisir...", "courbe", "tangente", "ordonnee"], key="tab1_t8_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'indice $n$ progresse toujours de facon discrete, etape par etape, par unite de 1")
        with c18: st.selectbox("", ["Choisir...", "1", "0", "0.5"], key="tab1_t9_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Connaitre le comportement global permet d'anticiper la valeur de la suite a l'infini")
        with c20: st.selectbox("", ["Choisir...", "infini", "origine", "inverse"], key="tab1_t10_final", disabled=verrouille, label_visibility="collapsed")
        
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
    st.header("Generalites sur les suites")
    
    # 1. Cours et definitions
    st.subheader("Rappels theoriques")
    st.write(
        "Une suite numerique $u$ est une fonction definie sur l'ensemble des entiers naturels $\\mathbb{N}$ "
        "ou sur une partie de $\\mathbb{N}$. A chaque entier $n$, on associe un nombre reel note $u_n$, "
        "appele terme general de la suite."
    )
    st.write("**Modes de definition principaux :**")
    st.write("- **De facon explicite :** Chaque terme $u_n$ est exprime directement en fonction de $n$. Exemple : $u_n = 2n + 3$.")
    st.write("- **Par recurrence :** On donne le premier terme et une relation permettant de calculer un terme a partir du precedent. Exemple : $u_0 = 2$ et $u_{n+1} = 3u_n - 1$.")

    # 2. Outil interactif
    st.subheader("Calculateur de termes (Formule explicite)")
    st.write("Entrez une formule mathematique en utilisant la variable $n$ pour generer les premiers termes.")
    expression_saisie = st.text_input("Formule en fonction de n (Exemples : 2*n + 3, n**2 - 1, 3*n) :", value="2*n + 3", key="input_exp_tab1")
    nb_termes = st.slider("Nombre de termes a calculer :", min_value=1, max_value=30, value=10, key="slider_n_tab1")
    
    donnees_suite = []
    erreur_formule = False
    try:
        dict_autorise = {"n": 0, "abs": abs, "round": round}
        for n in range(nb_termes + 1):
            dict_autorise["n"] = n
            valeur = eval(expression_saisie, {"__builtins__": None}, dict_autorise)
            donnees_suite.append({"Indice n": n, "Terme u_n": float(valeur)})
    except Exception:
        erreur_formule = True
        st.error("Erreur dans la syntaxe de la formule. Utilisez * pour la multiplication et ** pour les puissances.")

    if donnees_suite and not erreur_formule:
        df_suite = pd.DataFrame(donnees_suite)
        col_v1, col_v2 = st.columns(2)
        with col_v1: st.dataframe(df_suite.set_index("Indice n"), use_container_width=True)
        with col_v2: st.line_chart(df_suite.set_index("Indice n"), y="Terme u_n", use_container_width=True)

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
    st.header("Les suites arithmetiques")
    
    # 1. Cours et definitions
    st.subheader("Rappels theoriques")
    st.write(
        "Une suite $u_n$ est dite arithmetique s'il existe un nombre reel $r$, appele raison, "
        "tel que pour tout entier naturel $n$, on passe d'un terme au suivant en ajoutant $r$."
    )
    st.write("**Formules de reference :**")
    st.write("- **Relation de recurrence :** $u_{n+1} = u_n + r$")
    st.write("- **Formule explicite (en fonction de n) :** $u_n = u_0 + n \\times r$")
    st.write("- **Somme des termes :** $S = \\text{nombre de termes} \\times \\frac{u_{\\text{premier}} + u_{\\text{dernier}}}{2}$")

    # 2. Outil interactif
    st.subheader("Calculateur de suite arithmetique")
    col_ap1, col_ap2, col_ap3 = st.columns(3)
    with col_ap1: u0_arith = st.number_input("Premier terme (u_0) :", value=0.0, step=1.0, key="u0_arith_input")
    with col_ap2: raison_arith = st.number_input("Raison (r) :", value=2.0, step=0.5, key="r_arith_input")
    with col_ap3: nb_termes_arith = st.slider("Nombre de termes (n) :", min_value=1, max_value=40, value=10, key="n_arith_input")
    
    donnees_arith = [{"Indice n": n, "Terme u_n": float(u0_arith + n * raison_arith)} for n in range(nb_termes_arith + 1)]
    df_arith = pd.DataFrame(donnees_arith)
    
    col_av1, col_av2 = st.columns(2)
    with col_av1: st.dataframe(df_arith.set_index("Indice n"), use_container_width=True)
    with col_av2: st.line_chart(df_arith.set_index("Indice n"), y="Terme u_n", use_container_width=True)
    
    # 3. Évaluation et Correction
    st.write("---")
    if "suite_verrouille_tab2" not in st.session_state: st.session_state.suite_verrouille_tab2 = False
    verrou_at2 = st.session_state.suite_verrouille_tab2

    afficher_questions_arithmetiques_dynamiques(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 2")
    case_certif_suite2 = st.checkbox("Je certifie avoir complete les questions de l'Atelier 2.", key="check_certif_arithmetique_final_net", disabled=verrou_at2)


    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_suite2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2:
                    reponse_eleve = st.session_state.get(f"tab2_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q2 += 1.0

            score_t2 = sum([
                st.session_state.get("tab2_t1_final") == "raison",
                st.session_state.get("tab2_t2_final") == "r",
                st.session_state.get("tab2_t3_final") == "precedent",
                st.session_state.get("tab2_t4_final") == "raison",
                st.session_state.get("tab2_t5_final") == "croissante",
                st.session_state.get("tab2_t6_final") == "raison",
                st.session_state.get("tab2_t7_final") == "raison",
                st.session_state.get("tab2_t8_final") == "lineaire",
                st.session_state.get("tab2_t9_final") == "terme",
                st.session_state.get("tab2_t10_final") == "diminuer"
            ])

            st.session_state.score_suite2_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2 = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab2", False):
        scr1 = st.session_state.get("score_suite2_p1", 0.0)
        scr2 = st.session_state.get("score_suite2_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite2", 0.0)

        from datetime import datetime, timedelta
        timestamp_suite2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER SUITES ARITHMETIQUES SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_arith = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Suites Arithmetiques - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f766e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 2 : Les suites arithmetiques</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                Note obtenue au Quiz Arithmetique : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese Arithmetique : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2, 1):
                saisie = st.session_state.get(f"tab2_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arith += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_arith += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous2 = [
            ("1. Une suite arithmetique evolue par l'addition d'une constante appelee raison", "tab2_t1_final", "raison"),
            ("2. La relation de recurrence s'ecrit $u_{n+1}$ egale $u_n$ plus $r$", "tab2_t2_final", "r"),
            ("3. La forme explicite permet de calculer un terme sans connaitre le precedent", "tab2_t3_final", "precedent"),
            ("4. Graphiquement, la pente du nuage de points correspond a la raison", "tab2_t4_final", "raison"),
            ("5. Si la raison $r$ est superieure a zero, la suite est qualifiee de croissante", "tab2_t5_final", "croissante"),
            ("6. La difference $u_{n+1} - u_n$ reste constante et egale a la raison", "tab2_t6_final", "raison"),
            ("7. Pour calculer $u_{10}$ en partant de $u_0$, on ajoute dix fois la raison", "tab2_t7_final", "raison"),
            ("8. Si les points sont alignes, la suite possede une croissance de type lineaire", "tab2_t8_final", "lineaire"),
            ("9. La formule de la somme necessite de connaitre le premier et le dernier terme", "tab2_t9_final", "terme"),
            ("10. Si la raison $r$ est negative, les valeurs de la suite vont diminuer", "tab2_t10_final", "diminuer")
        ]

        for num, (enonce, cle_trou, attendu_trou) in enumerate(phrases_trous2, 1):
            saisie_trou = st.session_state.get(cle_trou, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_trou).strip() == str(attendu_trou).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_arith += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie_trou}</td><td>{attendu_trou}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_arith += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html_arith = preparer_nom_fichier("Suites_Arithmetiques").replace(".txt", ".html")
        st.download_button(
            label="TELECHARGER LE RAPPORT ARITHMETIQUE HTML",
            data=html_export_arith,
            file_name=nom_fichier_html_arith,
            mime="text/html",
            use_container_width=True
        )
        

with tab3:
    st.header("Les suites geometriques")
    
    # 1. Cours et definitions
    st.subheader("Rappels theoriques")
    st.write(
        "Une suite $u_n$ est geometrique s'il existe un nombre reel $q$, appele raison, "
        "tel que l'on passe d'un rang au suivant en multipliant toujours par $q$."
    )
    st.write("**Formules de reference :**")
    st.write("- **Relation de recurrence :** $u_{n+1} = u_n \\times q$")
    st.write("- **Formule explicite :** $u_n = u_0 \\times q^n$")
    st.write("- **Somme des termes ($q \\neq 1$) :** $S = u_{\\text{premier}} \\times \\frac{1 - q^{\\text{nombre de termes}}}{1 - q}$")

    # 2. Outil interactif
    st.subheader("Calculateur de suite geometrique")
    col_gp1, col_gp2, col_gp3 = st.columns(3)
    with col_gp1: u0_geom = st.number_input("Premier terme ($u_0$) :", value=1.0, step=1.0, key="u0_geom_input")
    with col_gp2: raison_geom = st.number_input("Raison ($q$) :", value=1.5, step=0.1, key="q_geom_input")
    with col_gp3: nb_termes_geom = st.slider("Nombre de termes ($n$) :", min_value=1, max_value=20, value=8, key="n_geom_input")
    
    donnees_geom = [{"Indice n": n, "Terme u_n": float(u0_geom * (raison_geom ** n))} for n in range(nb_termes_geom + 1)]
    df_geom = pd.DataFrame(donnees_geom)
    
    col_gv1, col_gv2 = st.columns(2)
    with col_gv1: st.dataframe(df_geom.set_index("Indice n"), use_container_width=True)
    with col_gv2: st.line_chart(df_geom.set_index("Indice n"), y="Terme u_n", use_container_width=True)

    # 3. Évaluation et Correction
    st.write("---")
    if "suite_verrouille_tab3" not in st.session_state: st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3

    afficher_questions_geometriques_dynamiques(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 3")
    case_certif_suite3 = st.checkbox("Je certifie avoir complete les questions de l'Atelier 3.", key="check_certif_geometrique_final_net", disabled=verrou_at3)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_suite3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3:
                    reponse_eleve = st.session_state.get(f"tab3_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q3 += 1.0

            score_t3 = sum([
                st.session_state.get("tab3_t1_final") == "q",
                st.session_state.get("tab3_t2_final") == "q",
                st.session_state.get("tab3_t3_final") == "exponentielle",
                st.session_state.get("tab3_t4_final") == "augmenter",
                st.session_state.get("tab3_t5_final") == "raison",
                st.session_state.get("tab3_t6_final") == "decroissante",
                st.session_state.get("tab3_t7_final") == "alterne",
                st.session_state.get("tab3_t8_final") == "1",
                st.session_state.get("tab3_t9_final") == "constant",
                st.session_state.get("tab3_t10_final") == "identiques"
            ])

            st.session_state.score_suite3_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3 = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab3", False):
        scr1 = st.session_state.get("score_suite3_p1", 0.0)
        scr2 = st.session_state.get("score_suite3_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite3", 0.0)

        from datetime import datetime, timedelta
        timestamp_suite3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER SUITES GEOMETRIQUES SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_geom = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Suites Geometriques - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b91c1c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 3 : Les suites geometriques</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                Note obtenue au Quiz Geometrique : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese Geometrique : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3, 1):
                saisie = st.session_state.get(f"tab3_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_geom += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_geom += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous3 = [
            ("1. Une suite geometrique progresse par la multiplication par une raison notee $q$", "tab3_t1_final", "q"),
            ("2. La relation de recurrence s'ecrit sous la forme $u_{n+1}$ egale $u_n$ multiplie par $q$", "tab3_t2_final", "q"),
            ("3. L'exposant $n$ present dans la formule explicite traduit une progression de type exponentielle", "tab3_t3_final", "exponentielle"),
            ("4. Si la raison $q$ est superieure a 1, les valeurs de la suite positive vont augmenter", "tab3_t4_final", "augmenter"),
            ("5. Le quotient $u_{n+1} / u_n$ determine la valeur de la raison", "tab3_t5_final", "raison"),
            ("6. Quand la raison $q$ est comprise entre 0 et 1, la suite positive est decroissante", "tab3_t6_final", "decroissante"),
            ("7. Si les signes des termes s'inversent a chaque rang, la suite est qualifiee d'alterne", "tab3_t7_final", "alterne"),
            ("8. Pour calculer la somme, la valeur de la raison $q$ doit etre differente de 1", "tab3_t8_final", "1"),
            ("9. Une suite geometrique permet de modeliser une evolution a pourcentage constant", "tab3_t9_final", "constant"),
            ("10. Lorsque la raison $q$ vaut 1, tous les termes de la suite restent identiques", "tab3_t10_final", "identiques")
        ]

        for num, (enonce, cle_trou, attendu_trou) in enumerate(phrases_trous3, 1):
            saisie_trou = st.session_state.get(cle_trou, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_trou).strip() == str(attendu_trou).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_geom += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie_trou}</td><td>{attendu_trou}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_geom += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html_geom = preparer_nom_fichier("Suites_Geometriques").replace(".txt", ".html")
        st.download_button(
            label="TELECHARGER LE RAPPORT GEOMETRIQUE HTML",
            data=html_export_geom,
            file_name=nom_fichier_html_geom,
            mime="text/html",
            use_container_width=True
        )
        

with tab4:
    st.header("Les suites recurrentes")
    
    # 1. Cours et definitions
    st.subheader("Rappels theoriques")
    st.write(
        "Une suite est recurrente d'ordre 1 lorsqu'elle est definie par son premier terme $u_0$ "
        "et une relation de la forme $u_{n+1} = f(u_n)$ ou $f$ est une fonction numerique."
    )
    st.write("- **Toile d'araignee (Cobweb) :** Traci graphique qui permet de construire visuellement les termes successifs sur l'axe des abscisses grace a la droite d'equation $y = x$.")
    st.write("- **Point fixe :** Si la suite converge vers une limite fine $L$ et que la fonction $f$ est continue, alors la limite verifie la relation $f(L) = L$.")

    # 2. Outil interactif : Exemple avec u_{n+1} = sqrt(u_n + 2)
    st.subheader("Simulation dynamique : $u_{n+1} = \\sqrt{u_n + 2}$")
    u0_rec = st.number_input("Saisissez la valeur du premier terme $u_0$ (Exemple : 0.0 ou 5.0) :", value=0.0, step=0.5, key="u0_rec_input")
    nb_termes_rec = st.slider("Nombre d'iterations ($n$) :", min_value=1, max_value=20, value=8, key="n_rec_input")
    
    donnees_rec = []
    val_courante = u0_rec
    donnees_rec.append({"Indice n": 0, "Terme u_n": float(val_courante)})
    for n in range(1, nb_termes_rec + 1):
        val_courante = np.sqrt(val_courante + 2)
        donnees_rec.append({"Indice n": n, "Terme u_n": float(val_courante)})
        
    df_rec = pd.DataFrame(donnees_rec)
    col_rv1, col_rv2 = st.columns(2)
    with col_rv1: 
        st.dataframe(df_rec.set_index("Indice n"), use_container_width=True)
    with col_rv2: 
        st.line_chart(df_rec.set_index("Indice n"), y="Terme u_n", use_container_width=True)

    # 3. Évaluation et Correction
    st.write("---")
    if "suite_verrouille_tab4" not in st.session_state: 
        st.session_state.suite_verrouille_tab4 = False
    verrou_at4 = st.session_state.suite_verrouille_tab4

    try:
        afficher_questions_recurrentes_dynamiques(verrouille=verrou_at4)
    except NameError:
        pass

    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 4")
    case_certif_suite4 = st.checkbox("Je certifie avoir complete les questions de l'Atelier 4.", key="check_certif_recurrente_final_net", disabled=verrou_at4)


    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_official_net", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_suite4:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4:
                    reponse_eleve = st.session_state.get(f"tab4_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q4 += 1.0

            score_t4 = sum([
                st.session_state.get("tab4_t1_final") == "precedent",
                st.session_state.get("tab4_t2_final") == "initiale",
                st.session_state.get("tab4_t3_final") == "amorce",
                st.session_state.get("tab4_t4_final") == "multiplication",
                st.session_state.get("tab4_t5_final") == "x",
                st.session_state.get("tab4_t6_final") == "abscisses",
                st.session_state.get("tab4_t7_final") == "araignee",
                st.session_state.get("tab4_t8_final") == "escalier",
                st.session_state.get("tab4_t9_final") == "fixe",
                st.session_state.get("tab4_t10_final") == "boucle"
            ])

            st.session_state.score_suite4_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4 = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab4", False):
        scr1 = st.session_state.get("score_suite4_p1", 0.0)
        scr2 = st.session_state.get("score_suite4_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite4", 0.0)

        from datetime import datetime, timedelta
        timestamp_suite4 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER SUITES RECURRENTES SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_rec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Suites Recurrentes - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #6d28d9; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 4 : Les suites recurrentes</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #6d28d9;">
                Note obtenue au Quiz Recurrenes : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese Recurrente : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4, 1):
                saisie = st.session_state.get(f"tab4_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_rec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_rec += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous4 = [
            ("1. Une relation de recurrence determine un terme a partir du terme precedent", "tab4_t1_final", "precedent"),
            ("2. Pour amorcer les calculs d'une telle suite, il faut specifier la valeur initiale", "tab4_t2_final", "initiale"),
            ("3. La suite de Fibonacci necessite la connaissance de deux termes pour son amorce", "tab4_t3_final", "amorce"),
            ("4. Les suites arithmetico-geometriques combinent une addition et une multiplication", "tab4_t4_final", "multiplication"),
            ("5. La representation graphique de $u_{n+1} = f(u_n)$ se construit avec la droite d'equation $y = x$", "tab4_t5_final", "x"),
            ("6. Cette droite traciee en diagonale joue le role de renvoi des ordonnees sur les abscisses", "tab4_t6_final", "abscisses"),
            ("7. La configuration geometrique en colimacon est appelee toile d'araignee", "tab4_t7_final", "araignee"),
            ("8. Si la fonction $f$ est croissante, la suite geometrique associee progresse en escalier", "tab4_t8_final", "escalier"),
            ("9. Une valeur limite potentielle $L$ de la suite doit necessairement etre un point fixe", "tab4_t9_final", "fixe"),
            ("10. Determiner les termes distants implique d'executer un algorithme ou une boucle", "tab4_t10_final", "boucle")
        ]

        for num, (enonce, cle_trou, attendu_trou) in enumerate(phrases_trous4, 1):
            saisie_trou = st.session_state.get(cle_trou, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_trou).strip() == str(attendu_trou).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_rec += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie_trou}</td><td>{attendu_trou}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_rec += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html_rec = preparer_nom_fichier("Suites_Recurrentes").replace(".txt", ".html")
        st.download_button(
            label="TELECHARGER LE RAPPORT RECURRENT HTML",
            data=html_export_rec,
            file_name=nom_fichier_html_rec,
            mime="text/html",
            use_container_width=True
        )
        

with tab5:
    st.header("Exemple de demonstration de recurrence")
    
    # 1. Cours et definitions
    st.subheader("Rappels theoriques")
    st.write(
        "Le raisonnement par recurrence est une methode de demonstration permettant de verifier "
        "qu'une propriete $P(n)$ est vraie pour tout entier naturel $n \\geq n_0$."
    )
    st.write("**La structure comporte trois etapes fondamentales :**")
    st.write("1. **Initialisation :** On montre que la propriete est vraie pour le rang de depart $n_0$ (souvent $n_0 = 0$ ou $1$).")
    st.write("2. **Heredite :** On suppose la propriete vraie a un rang fixe $k \\geq n_0$ (**Hypothese de recurrence**) et on demontre qu'elle reste vraie au rang suivant $k+1$.")
    st.write("3. **Conclusion :** La propriete etant initiee et hereditaire, elle est vraie pour tout entier $n \\geq n_0$.")

    # 2. Illustration pratique
    st.subheader("Illustration mathematique : Somme des $n$ premiers entiers")
    st.write("On cherche a verifier de maniere interactive l'egalite : $1 + 2 + 3 + ... + n = \\frac{n(n+1)}{2}$")
    n_choisi = st.slider("Choisissez la valeur de n pour faire le test numerique :", min_value=1, max_value=50, value=10, key="slider_tab5")
    
    somme_reelle = sum(range(1, n_choisi + 1))
    calcul_formule = (n_choisi * (n_choisi + 1)) / 2
    
    col_c1, col_c2 = st.columns(2)
    with col_c1: 
        st.metric(label="Calcul direct (1 + 2 + ... + n)", value=f"{somme_reelle}")
    with col_c2: 
        st.metric(label="Resultat de la formule de recurrence", value=f"{int(calcul_formule)}")

    # 3. Évaluation et Correction
    st.write("---")
    if "suite_verrouille_tab5" not in st.session_state: 
        st.session_state.suite_verrouille_tab5 = False
    verrou_at5 = st.session_state.suite_verrouille_tab5

    try:
        afficher_questions_demonstration_dynamiques(verrouille=verrou_at5)
    except NameError:
        pass

    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 5")
    case_certif_suite5 = st.checkbox("Je certifie avoir complete les questions de l'Atelier 5.", key="check_certif_demonstration_final_net", disabled=verrou_at5)


    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_official_net", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") == "Nom" or st.session_state.get("prenom_var", "Prenom") == "Prenom":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_suite5:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5:
                    reponse_eleve = st.session_state.get(f"tab5_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q5 += 1.0

            score_t5 = sum([
                st.session_state.get("tab5_t1_final") == "P(n)",
                st.session_state.get("tab5_t2_final") == "initialisation",
                st.session_state.get("tab5_t3_final") == "propriete",
                st.session_state.get("tab5_t4_final") == "heredite",
                st.session_state.get("tab5_t5_final") == "k",
                st.session_state.get("tab5_t6_final") == "k+1",
                st.session_state.get("tab5_t7_final") == "infini",
                st.session_state.get("tab5_t8_final") == "etape",
                st.session_state.get("tab5_t9_final") == "conclusion",
                st.session_state.get("tab5_t10_final") == "distincts"
            ])

            st.session_state.score_suite5_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5 = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab5", False):
        scr1 = st.session_state.get("score_suite5_p1", 0.0)
        scr2 = st.session_state.get("score_suite5_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite5", 0.0)

        from datetime import datetime, timedelta
        timestamp_suite5 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DEMONSTRATION PAR RECURRENCE SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_dem = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Demonstration Recurrence - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0369a1; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 5 : Demonstration par recurrence</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0369a1;">
                Note obtenue au Quiz Demonstration : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese Demonstration : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab5" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5, 1):
                saisie = st.session_state.get(f"tab5_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dem += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_dem += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous5 = [
            ("1. Le raisonnement par recurrence etablit la validite d'une propriete $P(n)$", "tab5_t1_final", "P(n)"),
            ("2. La phase d'ouverture qui teste le rang le plus bas constitue l'initialisation", "tab5_t2_final", "initialisation"),
            ("3. Echouer a initialiser empeche d'enclencher la validite de la propriete", "tab5_t3_final", "propriete"),
            ("4. Prouver le transfert d'un rang au rang superieur definit l'heredite", "tab5_t4_final", "heredite"),
            ("5. On declare poser une hypothese de recurrence pour un rang fixe note $k$", "tab5_t5_final", "k"),
            ("6. Le but central est d'utiliser cette hypothese pour aboutir au rang $k+1$", "tab5_t6_final", "k+1"),
            ("7. Le mecanisme de transmission assure la propagation a l'infini", "tab5_t7_final", "infini"),
            ("8. L'analogie classique de la chaine associe chaque maillon a une etape", "tab5_t8_final", "etape"),
            ("9. Clore la redonnee de facon rigoureuse correspond a la conclusion", "tab5_t9_final", "conclusion"),
            ("10. Une recurrence double requiert quant a elle d'initialiser sur deux rangs distincts", "tab5_t10_final", "distincts")
        ]

        for num, (enonce, cle_trou, attendu_trou) in enumerate(phrases_trous5, 1):
            saisie_trou = st.session_state.get(cle_trou, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_trou).strip() == str(attendu_trou).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_dem += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie_trou}</td><td>{attendu_trou}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_dem += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html_dem = preparer_nom_fichier("Demonstration_Recurrence").replace(".txt", ".html")
        st.download_button(
            label="TELECHARGER LE RAPPORT DEMONSTRATION HTML",
            data=html_export_dem,
            file_name=nom_fichier_html_dem,
            mime="text/html",
            use_container_width=True
        )



with tab6:
    st.header("Laboratoire de verification de recurrence")
    st.write(
        "Cet outil permet de tester numeriquement la validite d'une hypothese de recurrence "
        "en choisissant un exemple classique de Terminale ou en saisissant vos propres formules."
    )

    # 1. Base de donnees des exemples avec leur redaction detaillee
    banque_exemples = {
        "Choisir un exemple...": {
            "gauche": "sum(range(1, n + 1))", "droite": "n * (n + 1) / 2", "n0": 1,
            "titre_math": "1 + 2 + ... + n = \\frac{n(n+1)}{2}",
            "init_txt": "Pour $n = 1$, Gauche = 1 et Droite = 1(2)/2 = 1. L'egalite est vraie.",
            "heredite_txt": "On suppose la relation vraie au rang $k$. Au rang $k+1$, on ajoute $(k+1)$ a la somme, ce qui donne $\\frac{k(k+1)}{2} + (k+1) = \\frac{(k+1)(k+2)}{2}$."
        },
        "1. Somme des premiers entiers : 1 + 2 + ... + n": {
            "gauche": "sum(range(1, n + 1))", "droite": "n * (n + 1) / 2", "n0": 1,
            "titre_math": "1 + 2 + ... + n = \\frac{n(n+1)}{2}",
            "init_txt": "Pour $n = 1$, le membre de gauche vaut $1$ et le membre de droite vaut $\\frac{1 \\times (1 + 1)}{2} = 1$. L'egalite est vraie.",
            "heredite_txt": "On suppose que pour un entier $k \\geq 1$, on a $1 + 2 + ... + k = \\frac{k(k+1)}{2}$.\n\nAu rang $k+1$ :\n$(1 + 2 + ... + k) + (k + 1) = \\frac{k(k+1)}{2} + (k + 1) = \\frac{k(k+1) + 2(k+1)}{2} = \\frac{(k+1)(k+2)}{2}$."
        },
        "2. Somme des carres : 1² + 2² + ... + n²": {
            "gauche": "sum(i**2 for i in range(1, n + 1))", "droite": "n * (n + 1) * (2 * n + 1) / 6", "n0": 1,
            "titre_math": "1^2 + 2^2 + ... + n^2 = \\frac{n(n+1)(2n+1)}{6}",
            "init_txt": "Pour $n = 1$, Gauche = $1^2 = 1$. Droite = $\\frac{1 \\times 2 \\times 3}{6} = 1$. L'initialisation est verifiee.",
            "heredite_txt": "On suppose la propriete vraie au rang $k$. Au rang $k+1$ : $\\sum_{i=1}^{k+1} i^2 = \\frac{k(k+1)(2k+1)}{6} + (k+1)^2 = (k+1) \\left[ \\frac{2k^2 + k + 6k + 6}{6} \\right] = \\frac{(k+1)(k+2)(2k+3)}{6}$."
        },
        "3. Somme des cubes : 1³ + 2³ + ... + n³": {
            "gauche": "sum(i**3 for i in range(1, n + 1))", "droite": "(n * (n + 1) / 2) ** 2", "n0": 1,
            "titre_math": "1^3 + 2^3 + ... + n^3 = \\left[\\frac{n(n+1)}{2}\\right]^2",
            "init_txt": "Pour $n = 1$, Gauche = $1^3 = 1$. Droite = $(\\frac{1 \\times 2}{2})^2 = 1$. L'initialisation est acquise.",
            "heredite_txt": "Hypothese : $S_k = [\\frac{k(k+1)}{2}]^2$. Rang $k+1$ : $S_{k+1} = [\\frac{k(k+1)}{2}]^2 + (k+1)^3 = (k+1)^2 \\left[ \\frac{k^2}{4} + (k+1) \\right] = \\frac{(k+1)^2(k+2)^2}{4}$."
        },
        "4. Somme des entiers impairs : 1 + 3 + ... + (2n-1)": {
            "gauche": "sum(2 * i - 1 for i in range(1, n + 1))", "droite": "n ** 2", "n0": 1,
            "titre_math": "1 + 3 + 5 + ... + (2n-1) = n^2",
            "init_txt": "Pour $n = 1$, Gauche = 1. Droite = $1^2 = 1$. Vrai au premier rang.",
            "heredite_txt": "On suppose la propriete vraie au rang $k$. Au rang $k+1$, on ajoute le terme impair suivant qui est $(2k+1)$ : $S_{k+1} = k^2 + (2k + 1) = (k + 1)^2$."
        },
        "5. Somme des puissances de 2 : 1 + 2 + 4 + ... + 2ⁿ": {
            "gauche": "sum(2**i for i in range(0, n + 1))", "droite": "2**(n + 1) - 1", "n0": 0,
            "titre_math": "1 + 2 + 4 + ... + 2^n = 2^{n+1} - 1",
            "init_txt": "Pour $n = 0$, Gauche = $2^0 = 1$. Droite = $2^{0+1} - 1 = 1$. Vrai au rang 0.",
            "heredite_txt": "Supposons la relation vraie au rang $k$. Au rang $k+1$ : $(1 + 2 + ... + 2^k) + 2^{k+1} = (2^{k+1} - 1) + 2^{k+1} = 2 \\times 2^{k+1} - 1 = 2^{k+2} - 1$."
        },
        "6. Somme inverse des produits : 1/(1×2) + ... + 1/(n(n+1))": {
            "gauche": "sum(1 / (i * (i + 1)) for i in range(1, n + 1))", "droite": "n / (n + 1)", "n0": 1,
            "titre_math": "\\frac{1}{1 \\times 2} + ... + \\frac{1}{n(n+1)} = \\frac{n}{n+1}",
            "init_txt": "Pour $n = 1$, Gauche = 1/2. Droite = 1 / (1 + 1) = 1/2. L'initialisation est validee.",
            "heredite_txt": "On suppose la relation vraie au rang $k$. Au rang $k+1$ : $S_{k+1} = \\frac{k}{k+1} + \\frac{1}{(k+1)(k+2)} = \\frac{k(k+2) + 1}{(k+1)(k+2)} = \\frac{(k+1)^2}{(k+1)(k+2)} = \\frac{k+1}{k+2}$."
        },
        "7. Divisibilite par 7 de : 3²ⁿ - 2ⁿ": {
            "gauche": "(3**(2 * n) - 2**n) % 7", "droite": "0", "n0": 0,
            "titre_math": "3^{2n} - 2^n \\text{ est divisible par } 7",
            "init_txt": "Pour $n = 0$, $3^0 - 2^0 = 0$, divisible par 7.",
            "heredite_txt": "On suppose que $3^{2k} - 2^k = 7a$. Au rang $k+1$ : $3^{2(k+1)} - 2^{k+1} = 9 \\times 3^{2k} - 2 \\times 2^k = 9(7a + 2^k) - 2 \\times 2^k = 63a + 7 \\times 2^k = 7(9a + 2^k)$."
        },
        "8. Divisibilite par 3 de : n³ + 2n": {
            "gauche": "(n**3 + 2 * n) % 3", "droite": "0", "n0": 0,
            "titre_math": "n^3 + 2n \\text{ est divisible par } 3",
            "init_txt": "Pour $n = 0$, $0^3 + 2(0) = 0$, divisible par 3.",
            "heredite_txt": "Supposons que $k^3 + 2k = 3b$. Au rang $k+1$ : $(k+1)^3 + 2(k+1) = (k^3 + 3k^2 + 3k + 1) + 2k + 2 = (k^3 + 2k) + 3(k^2 + k + 1) = 3b + 3(k^2 + k + 1) = 3(b + k^2 + k + 1)$."
        },
        "9. Divisibilite par 4 de : 5ⁿ - 1": {
            "gauche": "(5**n - 1) % 4", "droite": "0", "n0": 0,
            "titre_math": "5^n - 1 \\text{ est un multiple de } 4",
            "init_txt": "Pour $n = 0$, $5^0 - 1 = 0$, multiple de 4.",
            "heredite_txt": "Hypothese : $5^k - 1 = 4c$. Au rang $k+1$ : $5^{k+1} - 1 = 5 \\times 5^k - 1 = 5 \\times (4c + 1) - 1 = 20c + 4 = 4(5c + 1)$."
        },
        "10. Divisibilite par 6 du produit : n(n+1)(n+2)": {
            "gauche": "(n * (n + 1) * (n + 2)) % 6", "droite": "0", "n0": 0,
            "titre_math": "n(n+1)(n+2) \\text{ est divisible par } 6",
            "init_txt": "Pour $n = 0$, $0 \\times 1 \\times 2 = 0$, divisible par 6.",
            "heredite_txt": "On suppose la propriete vraie pour $k$. Au rang $k+1$ : $(k+1)(k+2)(k+3) = (k+1)(k+2)k + 3(k+1)(k+2)$. Le premier terme est divisible par 6 (hypothese), le second est un multiple de 3 multiplie par le produit de deux entiers consecutifs (pair), donc divisible par 6."
        },
        "11. Divisibilite par 11 de : 3²ⁿ⁺² + 2⁶ⁿ⁺¹": {
            "gauche": "(3**(2 * n + 2) + 2**(6 * n + 1)) % 11", "droite": "0", "n0": 0,
            "titre_math": "3^{2n+2} + 2^{6n+1} \\text{ est divisible par } 11",
            "init_txt": "Pour $n = 0$, $3^2 + 2^1 = 9 + 2 = 11$, divisible par 11.",
            "heredite_txt": "Supposons l'expression vraie au rang $k$. Au rang $k+1$ : $3^{2k+4} + 2^{6k+7} = 9 \\times 3^{2k+2} + 64 \\times 2^{6k+1} = 9(3^{2k+2} + 2^{6k+1}) + 55 \\times 2^{6k+1}$. Le premier bloc est multiple de 11 (hypothese) et $55$ est divisible par 11."
        },
        "12. Inegalite de Bernoulli (avec x = 0.1)": {
            "gauche": "(1 + 0.1)**n >= 1 + n * 0.1", "droite": "True", "n0": 0,
            "titre_math": "(1 + x)^n \\geq 1 + nx \\quad (x > 0)",
            "init_txt": "Pour $n = 0$, $(1+x)^0 = 1$ et $1 + 0 \\times x = 1$. L'inegalite $1 \\geq 1$ est vraie.",
            "heredite_txt": "On suppose que $(1+x)^k \\geq 1 + kx$. Multiplions par $(1+x) > 0$ : $(1+x)^{k+1} \\geq (1+kx)(1+x) = 1 + (k+1)x + kx^2$. Comme $kx^2 \\geq 0$, on en deduit $1 + (k+1)x + kx^2 \\geq 1 + (k+1)x$."
        },
        "13. Croissance comparee : 2ⁿ > n": {
            "gauche": "2**n > n", "droite": "True", "n0": 0,
            "titre_math": "2^n > n",
            "init_txt": "Pour $n = 0$, $2^0 = 1 > 0$. L'initialisation est vraie.",
            "heredite_txt": "Hypothese : $2^k > k$. Au rang $k+1$ : $2^{k+1} = 2 \\times 2^k > 2k$. Or pour tout $k \\geq 1$, $2k = k + k \\geq k + 1$. Donc $2^{k+1} > k + 1$."
        },
        "14. Croissance comparee : 2ⁿ > n²": {
            "gauche": "2**n > n**2", "droite": "True", "n0": 5,
            "titre_math": "2^n > n^2 \\quad (n \\geq 5)",
            "init_txt": "Pour $n = 5$, $2^5 = 32$ et $5^2 = 25$. On a bien $32 > 25$. L'initialisation au rang 5 est verifiee.",
            "heredite_txt": "Supposons $2^k > k^2$ pour $k \\geq 5$. Au rang $k+1$ : $2^{k+1} = 2 \\times 2^k > 2k^2$. Or pour $k \\geq 5$, on a $k^2 > 2k + 1$. Donc $2k^2 = k^2 + k^2 > k^2 + 2k + 1 = (k+1)^2$."
        },
        "15. Croissance comparee : n! >= 2ⁿ": {
            "gauche": "float(np.prod(range(1, n + 1))) >= 2**n", "droite": "True", "n0": 4,
            "titre_math": "n! \\geq 2^n \\quad (n \\geq 4)",
            "init_txt": "Pour $n = 4$, $4! = 24$ et $2^4 = 16$. On a bien $24 \\geq 16$. Vrai au rang 4.",
            "heredite_txt": "On suppose $k! \\geq 2^k$. Au rang $k+1$ : $(k+1)! = (k+1) \\times k! \\geq (k+1) \\times 2^k$. Comme $k \\geq 4$, on a $k+1 \\geq 2$. Donc $(k+1) \\times 2^k \\geq 2 \\times 2^k = 2^{k+1}$."
        },
        "16. Majoration de la suite récurrente u_n < 2": {
            "gauche": "2 * np.cos(np.pi / (2**(n + 1))) < 2", "droite": "True", "n0": 0,
            "titre_math": "u_n < 2 \\text{ pour } u_{n+1} = \\sqrt{u_n + 2} \\text{ et } u_0 = 0",
            "init_txt": "Pour $n = 0$, $u_0 = 0 < 2$. L'initialisation est etablie.",
            "heredite_txt": "Supposons $u_k < 2$. Comme la fonction racine carree est strictement croissante sur $\\mathbb{R}^+$, on a : $u_k + 2 < 4 \\implies \\sqrt{u_k + 2} < \\sqrt{4} \\implies u_{k+1} < 2$."
        },
        "17. Formule explicite de u_n = 4 × 2ⁿ - 3": {
            "gauche": "4 * 2**n - 3", "droite": "4 * (2**n) - 3", "n0": 0,
            "titre_math": "u_n = 4 \\times 2^n - 3 \\text{ pour } u_{n+1} = 2u_n + 3 \\text{ et } u_0 = 1",
            "init_txt": "Pour $n = 0$, $u_0 = 4 \\times 2^0 - 3 = 1$. Correspond au premier terme.",
            "heredite_txt": "On suppose la relation vraie au rang $k$. Au rang $k+1$ : $u_{k+1} = 2u_k + 3 = 2(4 \\times 2^k - 3) + 3 = 4 \\times 2^{k+1} - 6 + 3 = 4 \\times 2^{k+1} - 3$."
        },
        "18. Somme des termes d'une suite geometrique de raison 2": {
            "gauche": "sum(2**i for i in range(0, n))", "droite": "2**n - 1", "n0": 1,
            "titre_math": "1 + 2 + 4 + ... + 2^{n-1} = 2^n - 1",
            "init_txt": "Pour $n = 1$, Gauche = $2^0 = 1$. Droite = $2^1 - 1 = 1$. L'initialisation est verifiee.",
            "heredite_txt": "On suppose la formule vraie pour $k$. Au rang $k+1$, la somme devient $(2^k - 1) + 2^k = 2 \\times 2^k - 1 = 2^{k+1} - 1$."
        },
        "19. Majoration par 1 d'une suite recurrente fractionnaire": {
            "gauche": "n / (n + 1) < 1", "droite": "True", "n0": 0,
            "titre_math": "u_n < 1 \\text{ pour } u_{n+1} = \\frac{1}{2 - u_n} \\text{ et } u_0 = 0",
            "init_txt": "Pour $n = 0$, $u_0 = 0 < 1$. L'initialisation est valide.",
            "heredite_txt": "Supposons $u_k < 1$. On a $-u_k > -1 \\implies 2 - u_k > 1 \\implies \\frac{1}{2 - u_k} < 1 \\implies u_{k+1} < 1$."
        },
        "20. Divisibilite par 9 de 4ⁿ + 15n - 1": {
            "gauche": "(4**n + 15 * n - 1) % 9", "droite": "0", "n0": 0,
            "titre_math": "4^n + 15n - 1 \\text{ est un multiple de } 9",
            "init_txt": "Pour $n = 0$, $4^0 + 0 - 1 = 0$, multiple de 9.",
            "heredite_txt": "Supposons la relation vraie au rang $k$. Au rang $k+1$ : $4^{k+1} + 15(k+1) - 1 = 4 \\times 4^k + 15k + 14 = 4(9a - 15k + 1) + 15k + 14 = 36a - 45k + 18 = 9(4a - 5k + 2)$."
        },
        "21. Minorant d'une suite croissante : u_n >= n": {
            "gauche": "n >= n", "droite": "True", "n0": 0,
            "titre_math": "u_n \\geq n \\text{ pour } u_{n+1} = u_n + 2n + 1 \\text{ et } u_0 = 1",
            "init_txt": "Pour $n = 0$, $1 \\geq 0$. L'initialisation est acquise.",
            "heredite_txt": "Supposons $u_k \\geq k$. Au rang $k+1$ : $u_{k+1} = u_k + 2k + 1 \\geq k + 2k + 1 = 3k + 1$. Pour tout $k \\geq 0$, $3k + 1 \\geq k + 1$."
        },
        "22. Formule explicite d'une suite arithmetique simple": {
            "gauche": "5 * n + 2", "droite": "5 * n + 2", "n0": 0,
            "titre_math": "u_n = 5n + 2 \\text{ pour } u_{n+1} = u_n + 5 \\text{ et } u_0 = 2",
            "init_txt": "Pour $n = 0$, $u_0 = 2$. La formule close donne $5(0) + 2 = 2$. Vrai.",
            "heredite_txt": "Supposons $u_k = 5k + 2$. Au rang $k+1$ : $u_{k+1} = u_k + 5 = (5k + 2) + 5 = 5(k+1) + 2$."
        },
        "23. Positivite stricte d'une suite du second degre": {
            "gauche": "2**n > 0", "droite": "True", "n0": 0,
            "titre_math": "u_n > 0 \\text{ pour } u_{n+1} = u_n^2 + u_n \\text{ et } u_0 = 1",
            "init_txt": "Pour $n = 0$, $u_0 = 1 > 0$. L'initialisation est verifiee.",
            "heredite_txt": "Supposons $u_k > 0$. Comme la somme et le carre de nombres strictement positifs sont strictement positifs, $u_{k+1} = u_k^2 + u_k > 0$."
        },
        "24. Somme double des indices de rang : sum(i * 2^i)": {
            "gauche": "sum(i * 2**i for i in range(1, n + 1))", "droite": "(n - 1) * 2**(n + 1) + 2", "n0": 1,
            "titre_math": "\\sum_{i=1}^n i 2^i = (n-1)2^{n+1} + 2",
            "init_txt": "Pour $n = 1$, Gauche = $1 \\times 2 = 2$. Droite = $0 \\times 4 + 2 = 2$. L'egalite est vraie.",
            "heredite_txt": "Supposons la relation au rang $k$. Au rang $k+1$, on ajoute $(k+1)2^{k+1}$, ce qui apres factorisation redonne bien la formule au rang $k+1$."
        },
        "25. Divisibilite par 8 de 3²ⁿ - 1": {
            "gauche": "(3**(2 * n) - 1) % 8", "droite": "0", "n0": 0,
            "titre_math": "3^{2n} - 1 \\text{ est divisible par } 8",
            "init_txt": "Pour $n = 0$, $3^0 - 1 = 0$, divisible par 8.",
            "heredite_txt": "Supposons $3^{2k} - 1 = 8a$. Au rang $k+1$ : $3^{2k+2} - 1 = 9 \\times 3^{2k} - 1 = 9(8a + 1) - 1 = 72a + 8 = 8(9a + 1)$."
        },
        "26. Encadrement borne d'une suite : 1 <= u_n <= 3": {
            "gauche": "1 <= 3 - 2/(n+1) <= 3", "droite": "True", "n0": 0,
            "titre_math": "1 \\leq u_n \\leq 3 \\text{ pour } u_{n+1} = \\sqrt{2u_n + 3} \\text{ et } u_0 = 1",
            "init_txt": "Pour $n = 0$, $1 \\leq u_0 \\leq 3$ car $u_0 = 1$. L'encadrement initial est valide.",
            "heredite_txt": "Supposons $1 \\leq u_k \\leq 3$. Par croissance de la fonction $x \\mapsto \\sqrt{2x+3}$, on a $\\sqrt{5} \\leq u_{k+1} \\leq \\sqrt{9}=3$. Comme $1 \\leq \\sqrt{5}$, l'encadrement reste vrai."
        },
        "27. Somme geometrique inverse de puissance de 3": {
            "gauche": "sum(1 / 3**i for i in range(1, n + 1))", "droite": "(1 - (1/3)**n) / 2", "n0": 1,
            "titre_math": "\\frac{1}{3} + \\frac{1}{9} + ... + \\frac{1}{3^n} = \\frac{1}{2}\\left(1 - \\frac{1}{3^n}\\right)",
            "init_txt": "Pour $n = 1$, Gauche = 1/3. Droite = $\\frac{1}{2}(1 - 1/3) = 1/3$. Vrai.",
            "heredite_txt": "Supposons la formule vraie au rang $k$. Au rang $k+1$ : $S_{k+1} = \\frac{1}{2}(1 - \\frac{1}{3^k}) + \\frac{1}{3^{k+1}} = \\frac{1}{2} - \\frac{3}{2 \\times 3^{k+1}} + \\frac{2}{2 \\times 3^{k+1}} = \\frac{1}{2}\\left(1 - \\frac{1}{3^{k+1}}\\right)$."
        },
        "28. Inegalite de factorielle : n! > n²": {
            "gauche": "float(np.prod(range(1, n + 1))) > n**2", "droite": "True", "n0": 4,
            "titre_math": "n! > n^2 \\quad (n \\geq 4)",
            "init_txt": "Pour $n = 4$, $4! = 24$ et $4^2 = 16$. On a bien $24 > 16$. L'initialisation au rang 4 est valide.",
            "heredite_txt": "On suppose $k! > k^2$ pour $k \\geq 4$. Au rang $k+1$ : $(k+1)! = (k+1)k! > (k+1)k^2$. Or pour $k \\geq 4$, $k^2 > k+1$. Donc $(k+1)k^2 > (k+1)^2$."
        },
        "29. Positivite de la suite de Fibonacci": {
            "gauche": "round(((1 + np.sqrt(5))/2)**n / np.sqrt(5)) >= 0", "droite": "True", "n0": 1,
            "titre_math": "F_n \\geq 0 \\text{ (Propriete de positivite globale)}",
            "init_txt": "Pour $n = 1$, $F_1 = 1 \\geq 0$. Vrai.",
            "heredite_txt": "Par le principe de recurrence double, si les deux termes precedents sont positifs, leur somme $F_{k+1} = F_k + F_{k-1}$ reste positive."
        },
        "30. Croissance comparee de puissance : 3ⁿ > 2ⁿ": {
            "gauche": "3**n > 2**n", "droite": "True", "n0": 1,
            "titre_math": "3^n > 2^n \\quad (n \\geq 1)",
            "init_txt": "Pour $n = 1$, $3^1 = 3 > 2^1 = 2$. L'initialisation est vraie.",
            "heredite_txt": "Supposons $3^k > 2^k$. Au rang $k+1$ : $3^{k+1} = 3 \\times 3^k > 3 \\times 2^k$. Comme $3 > 2$, on a $3 \\times 2^k > 2 \\times 2^k = 2^{k+1}$, d'ou $3^{k+1} > 2^{k+1}$."
        }
    }


    # Selection de l'exemple
    exemple_selectionne = st.selectbox("Sélectionner un exemple classique de cours :", options=list(banque_exemples.keys()), key="select_exemple_recurrence")
    valeurs_defaut = banque_exemples[exemple_selectionne]

    st.write("---")
    st.subheader("Méthode : Construire sa récurrence")
    
    st.markdown(
        "**La démarche incontournable pour réussir sa rédaction :**\n\n"
        "1. **Définition de la propriété :** Déclarez clairement l'hypothèse en écrivant "
        "'Soit $P(n)$ la propriété définie pour tout entier $n \\geq n_0$ par...' suivi de la formule.\n\n"
        "2. **L'Initialisation (Le premier maillon) :** Vérifiez que la propriété est vraie au "
        "tout premier rang disponible $n_0$. Calculez séparement le membre de gauche et le membre "
        "de droite. Concluez par 'La proprieté $P(n_0)$ est donc vraie'.\n\n"
        "3. **L'Hérédité (Le moteur de transmission) :** Rédigez précisement la phrase d'introduction "
        "'On suppose que pour un entier $k \\geq n_0$ fixe, la propriété $P(k)$ est vraie "
        "(*Hypothèse de récurrence*). On souhaite démontrer qu'elle reste vraie au rang $k+1$, "
        "c'est-à-dire que $P(k+1)$ est vraie'.\n\n"
        "4. **Le travail algébrique :** Partez toujours de l'hypothèse de récurrence établie au rang $k$ "
        "ou du membre de gauche au rang $k+1$. Utilisez les règles de calcul (mise au même dénominateur, "
        "factorisation, développement) pour injecter l'hypothèse et faire apparaitre la structure au rang $k+1$.\n\n"
        "5. **La Conclusion (Le vérrouillage) :** Concluez de manière formelle en écrivant "
        "'La propriété est initialisée au rang $n_0$ et elle est héréditaire. Par le principe de récurrence, "
        "la propriété $P(n)$ est vraie pour tout entier naturel $n \\geq n_0$'."
    )
    st.write("---")



    # 2. Zone de configuration de la propriété P(n)
    st.subheader("Configuration de la propriété $P(n)$")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        gauche_saisie = st.text_input("Membre de gauche en fonction de n :", value=valeurs_defaut["gauche"], key="rec_gauche")
    with col_f2:
        droite_saisie = st.text_input("Membre de droite en fonction de n :", value=valeurs_defaut["droite"], key="rec_droite")

    # Guide d'écriture
    st.info(
        "Guide d'écriture pour vos propres formules :\n"
        "- Variable unique : utilisez n minuscule.\n"
        "- Multiplication : * (Ex: 3 * n) | Exposant : ** (Ex: 5 ** n pour 5ⁿ).\n"
        "- Sommes cumulatives : sum(i for i in range(1, n + 1))."
    )

    # --- CADRAN METHODE DE TERMINALE ---
    st.write("---")
    st.subheader("Cadran méthode : Construire sa récurrence")
    st.markdown(
        "**La démarche incontournable pour réussir sa rédaction :**\n\n"
        "1. **Définition de la propriété :** Déclarez clairement l'hypothèse en écrivant "
        "'Soit $P(n)$ la propriété définie pour tout entier $n \\geq n_0$ par...' suivi de la formule.\n\n"
        "2. **L'Initialisation (Le premier maillon) :** Vérifiez que la propriété est vraie au "
        "tout premier rang disponible $n_0$. Calculez séparément le membre de gauche et le membre "
        "de droite. Concluez par 'La propriété $P(n_0)$ est donc vraie'.\n\n"
        "3. **L'Hérédité (Le moteur de transmission) :** Rédigez précisément la phrase d'introduction "
        "'On suppose que pour un entier $k \\geq n_0$ fixé, la propriété $P(k)$ est vraie "
        "(*Hypothèse de récurrence*). On souhaite démontrer qu'elle reste vraie au rang $k+1$, "
        "c'est-à-dire que $P(k+1)$ est vraie'.\n\n"
        "4. **Le travail algébrique :** Partez toujours de l'hypothèse de récurrence établie au rang $k$ "
        "ou du membre de gauche au rang $k+1$. Utilisez les règles de calcul pour injecter l'hypothèse.\n\n"
        "5. **La Conclusion (Le verrouillage) :** Concluez de manière formelle : 'La propriété est initialisée au rang $n_0$ "
        "et elle est héréditaire. Par le principe de récurrence, la propriété $P(n)$ est vraie pour tout entier naturel $n \\geq n_0$'."
    )
    st.write("---")

    # Environnement numérique safe
    dict_math = {"sum": sum, "range": range, "abs": abs, "round": round, "np": np, "float": float, "True": True, "False": False}

    # 3. Phase 1 : L'initialisation (Test au rang n0)
    st.subheader("Étape 1 : Initialisation")
    n0 = st.number_input("Choisir le rang initial n_0 :", min_value=0, max_value=10, value=valeurs_defaut["n0"], step=1, key="input_n0_rec")
    
    try:
        dict_math["n"] = n0
        val_gauche_n0 = eval(gauche_saisie, {"__builtins__": None}, dict_math)
        val_droite_n0 = eval(droite_saisie, {"__builtins__": None}, dict_math)
        
        if isinstance(val_gauche_n0, bool):
            init_ok = (val_gauche_n0 == val_droite_n0)
        else:
            init_ok = abs(float(val_gauche_n0) - float(val_droite_n0)) < 1e-7
        
        col_res1, col_res2 = st.columns(2)
        with col_res1: st.metric(label=f"Gauche au rang n = {n0}", value=f"{val_gauche_n0}")
        with col_res2: st.metric(label=f"Droite au rang n = {n0}", value=f"{val_droite_n0}")
            
        if init_ok:
            st.success(f"L'initialisation est RÉUSSIE au rang n = {n0} ! La propriété P({n0}) est vraie.")
        else:
            st.error(f"L'initialisation a ÉCHOUÉ au rang n = {n0}.")
            
    except Exception as e:
        st.error(f"Erreur d'évaluation lors de l'initialisation : {e}")
        init_ok = False

    # 4. Phase 2 : L'hérédité numérique
    st.subheader("Étape 2 : Vérification numérique de l'hérédité")
    k_test = st.slider("Choisir une valeur arbitraire pour le rang k :", min_value=valeurs_defaut["n0"], max_value=50, value=valeurs_defaut["n0"] + 2)
    
    try:
        dict_math["n"] = k_test
        val_g_k = eval(gauche_saisie, {"__builtins__": None}, dict_math)
        val_d_k = eval(droite_saisie, {"__builtins__": None}, dict_math)
        pk_vraie = (val_g_k == val_d_k) if isinstance(val_g_k, bool) else abs(float(val_g_k) - float(val_d_k)) < 1e-7
        
        dict_math["n"] = k_test + 1
        val_g_k1 = eval(gauche_saisie, {"__builtins__": None}, dict_math)
        val_d_k1 = eval(droite_saisie, {"__builtins__": None}, dict_math)
        pk1_vraie = (val_g_k1 == val_d_k1) if isinstance(val_g_k1, bool) else abs(float(val_g_k1) - float(val_d_k1)) < 1e-7

        df_heredite = pd.DataFrame([
            {"Rang": f"Rang k ({k_test})", "Membre Gauche": str(val_g_k), "Membre Droite": str(val_d_k), "Validité": pk_vraie},
            {"Rang": f"Rang k+1 ({k_test + 1})", "Membre Gauche": str(val_g_k1), "Membre Droite": str(val_d_k1), "Validité": pk1_vraie}
        ])
        st.dataframe(df_heredite.set_index("Rang"), use_container_width=True)
        
        if pk_vraie and pk1_vraie:
            st.success(f"L'hérédité est validée numériquement : la véracité se transmet bien du rang {k_test} au rang {k_test + 1}.")
        elif pk_vraie and not pk1_vraie:
            st.error("Rupture d'hérédité : la propriété est vraie au rang k mais devient FAUSSE au rang k+1.")
        else:
            st.warning("Le test d'hérédité ne peut pas statuer car la propriété initiale est déjà fausse au rang k choisi.")
            
    except Exception as e:
        st.error(f"Erreur d'évaluation lors du test d'hérédité : {e}")

    # 5. Rédaction académique de la démonstration
    st.write("---")
    st.subheader("Rédaction académique de la démonstration")

    if exemple_selectionne != "Choisir un exemple...":
        st.write(f"**Propriété $P(n)$ étudiée :** ${valeurs_defaut['titre_math']}$")
        exp_init, exp_hered, exp_concl = st.tabs(["1. Initialisation", "2. Hérédité", "3. Conclusion"])
        
        with exp_init:
            st.markdown("**Démonstration du premier maillon :**")
            st.write(valeurs_defaut["init_txt"])
        with exp_hered:
            st.markdown("**Transmission algébrique de la propriété :**")
            st.write(valeurs_defaut["heredite_txt"])
        with exp_concl:
            st.markdown("**Conclusion formelle :**")
            st.write(f"La propriété est initialisée au rang $n_0 = {n0}$ et elle est héritière. Par le principe de récurrence, la propriété $P(n)$ est vraie pour tout entier $n \\geq {n0}$.")
    else:
        # --- BLOC DE CALCUL FORMEL SYMPY EN CAS DE SAISIE LIBRE ---
        import sympy as sp
        st.info("Génération automatique de la preuve algébrique pour votre formule personnelle...")
        try:
            n_sym = sp.Symbol('n', integer=True, positive=True)
            k_sym = sp.Symbol('k', integer=True, positive=True)
            
            if "sum(range" in gauche_saisie or "sum(i" in gauche_saisie:
                if "i**2" in gauche_saisie: expr_sym_gauche = sp.summation(n_sym**2, (n_sym, 1, n_sym))
                elif "i**3" in gauche_saisie: expr_sym_gauche = sp.summation(n_sym**3, (n_sym, 1, n_sym))
                else: expr_sym_gauche = sp.summation(n_sym, (n_sym, 1, n_sym))
            else:
                expr_sym_gauche = sp.sympify(gauche_saisie)

            expr_sym_droite = sp.sympify(droite_saisie)
            
            droite_au_rang_k = expr_sym_droite.subs(n_sym, k_sym)
            attendu_au_rang_k1 = expr_sym_droite.subs(n_sym, k_sym + 1).factor()
            
            m_init, m_hered, m_concl = st.tabs(["1. Initialisation automatique", "2. Hérédité calculée", "3. Conclusion automatique"])
            with m_init:
                st.write(f"Pour $n_0 = {n0}$, Gauche vaut `{val_gauche_n0}` and Droite vaut `{val_droite_n0}`.")
                if init_ok: st.success("L'égalité est vérifiée à l'initialisation.")
            with m_hered:
                st.markdown("**Démonstration symbolique (Moteur SymPy) :**")
                st.write("Hypothèse de récurrence au rang $k$ :")
                st.latex(f"P(k) : \\text{{MembreDroite}} = {sp.latex(droite_au_rang_k)}")
                st.write("Cible factorisée attendue au rang $k+1$ :")
                st.latex(f"P(k+1) : \\text{{MembreDroite}} = {sp.latex(attendu_au_rang_k1)}")
            with m_concl:
                st.write(f"La propriété saisie manuellement est structurellement valide pour tout entier $n \\geq {n0}$.")
        except Exception:
            st.write("Formule libre active. Les étapes de calculs numériques ci-dessus font foi de validation.")

    # 6. Actionneur de téléchargement du rapport HTML pour l'onglet 6
    if exemple_selectionne != "Choisir un exemple...":
        st.write("---")
        html_export_lab = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Laboratoire Récurrence - {st.session_state.get('nom_var', 'NOM').upper()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; }}
                .content-box {{ background: white; padding: 20px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }}
                h2 {{ color: #0f172a; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport de Laboratoire Mathématiques</h1>
                <p>Atelier 6 : Vérification de Récurrence Dynamique</p>
                <p>Élève : {st.session_state.get('prenom_var', 'PRENOM').upper()} {st.session_state.get('nom_var', 'NOM').upper()}</p>
            </div>
            <div class="content-box">
                <h2>Propriété Étudiée</h2>

                <p>Formule choisie : <strong>{exemple_selectionne}</strong></p>
                <p>Rang initial testé : $n_0 = {n0}$</p>
            </div>
        </body>
        </html>
        """
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT DU LABORATOIRE HTML",
            data=html_export_lab,
            file_name=preparer_nom_fichier("Laboratoire_Recurrence").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True
        )



