# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application géométrie dans le plan",
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
st.title("Application géométrie dans le plan")
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
    "Les triangles",
    "Les quadrilatères",
    "Les cercles",
    "Les surfaces complexes",
    "Utilisation dans la vie",
    "Décomposition en surfaces classiques",
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]


def afficher_questions_complexes_dynamiques(verrouille=False):
    import streamlit as st

    ordre_fixe_tab4 = [
        {
            "id": "q4_1",
            "q": "La méthode consistant à diviser une surface irrégulière en formes simples s'appelle :",
            "options": ["La décomposition", "La translation", "L'extrapolating"],
            "rep": "La décomposition",
        },
        {
            "id": "q4_2",
            "q": "Si on combine deux surfaces disjointes d'aires A1 et A2, l'aire totale est :",
            "options": ["La somme A1 + A2", "Le produit A1 * A2", "La moyenne des deux"],
            "rep": "La somme A1 + A2",
        },
        {
            "id": "q4_3",
            "q": "Dans la méthode des rectangles, comment évolue la précision quand leur nombre augmente ?",
            "options": [
                "La précision augmente",
                "La précision diminue",
                "La précision reste identique",
            ],
            "rep": "La précision augmente",
        },
        {
            "id": "q4_4",
            "q": "Quelle unité agraire équivaut exactement à une surface de 10 000 mètres carrés ?",
            "options": ["L'hectare", "L'are", "Le centiare"],
            "rep": "L'hectare",
        },
        {
            "id": "q4_5",
            "q": "Pour calculer l'aire d'une couronne circulaire (un anneau), on effectue une :",
            "options": ["Soustraction d'aires", "Somme d'aires", "Division d'aires"],
            "rep": "Soustraction d'aires",
        },
        {
            "id": "q4_6",
            "q": "L'estimation d'une aire par des rectangles situés entièrement sous la courbe est une borne :",
            "options": ["Inférieure", "Supérieure", "Exacte"],
            "rep": "Inférieure",
        },
        {
            "id": "q4_7",
            "q": "Une surface délimitée par des segments de droites est obligatoirement un :",
            "options": ["Polygone", "Disque", "Secteur"],
            "rep": "Polygone",
        },
        {
            "id": "q4_8",
            "q": "L'unité standard de mesure de surface dans le système international est le :",
            "options": [
                "Mètre carré",
                "Mètre cube",
                "Mètre linéaire",
            ],
            "rep": "Mètre carré",
        },
        {
            "id": "q4_9",
            "q": "Une figure composite est une figure géométrique :",
            "options": [
                "Formée par l'assemblage de plusieurs figures simples",
                "Qui possède un nombre infini de côtés",
                "Qui ne peut pas être mesurée",
            ],
            "rep": "Formée par l'assemblage de plusieurs figures simples",
        },
        {
            "id": "q4_10",
            "q": "Un are correspond exactement à un carré de combien de mètres de côté ?",
            "options": ["10 mètres", "100 mètres", "1 mètre"],
            "rep": "10 mètres",
        },
    ]

    st.session_state.ordre_quiz_tab4 = ordre_fixe_tab4

    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz sur les surfaces complexes (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab4_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox(
                "",
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse sur les surfaces complexes (Texte à trous - 10 cases - 10 pts)"
        )

        champs_cx = [
            ("1. Découper une forme en entités élémentaires est la décomposition", ["Choisir...", "décomposition", "symétrie", "rotation"], "tab4_t1_final"),
            ("2. L'aire d'une forme évidée s'obtient par une soustraction géométrique", ["Choisir...", "soustraction", "multiplication", "addition"], "tab4_t2_final"),
            ("3. Un terrain de cent mètres sur cent mètres a une aire d'un hectare", ["Choisir...", "hectare", "are", "centiare"], "tab4_t3_final"),
            ("4. L'additivité indique que l'aire totale est la somme des aires partielles", ["Choisir...", "somme", "différence", "proportion"], "tab4_t4_final"),
            ("5. Augmenter le nombre de rectangles réduit l'erreur d'estimation", ["Choisir...", "erreur", "hauteur", "largeur"], "tab4_t5_final"),
            ("6. Un polygone régulier peut se découper en triangles isocèles identiques", ["Choisir...", "triangles", "cercles", "trapèzes"], "tab4_t6_final"),
            ("7. La surface délimitée par une courbe nécessite une méthode d'approximation", ["Choisir...", "approximation", "exacte", "directe"], "tab4_t7_final"),
            ("8. L'are est une unité de mesure adaptée aux surfaces agraires", ["Choisir...", "agraires", "volumiques", "linéaires"], "tab4_t8_final"),
            ("9. Les rectangles qui dépassent la courbe forment une borne supérieure", ["Choisir...", "supérieure", "inférieure", "nulle"], "tab4_t9_final"),
            ("10. Mesurer une surface complexe revient à évaluer son extension plane", ["Choisir...", "plane", "inclinée", "sphérique"], "tab4_t10_final"),
        ]

        for enonce, choix, cle in champs_cx:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=cle,
                    disabled=verrouille,
                    label_visibility="collapsed",
                )

def afficher_questions_cercles_dynamiques(verrouille=False):
    import streamlit as st

    ordre_fixe_tab3 = [
        {
            "id": "q3_1",
            "q": "Le diametre d'un cercle correspond exactement a :",
            "options": [
                "Deux fois le rayon",
                "La moitie du rayon",
                "Le carre du rayon",
            ],
            "rep": "Deux fois le rayon",
        },
        {
            "id": "q3_2",
            "q": "Quelle est la valeur approchee courante de la constante Pi (pi) ?",
            "options": ["3.1416", "2.718", "1.618"],
            "rep": "3.1416",
        },
        {
            "id": "q3_3",
            "q": "Un segment joignant deux points du cercle en passant par son centre est :",
            "options": ["Un diametre", "Une corde", "Une tangente"],
            "rep": "Un diametre",
        },
        {
            "id": "q3_4",
            "q": "La formule exacte pour calculer la circonference (perimetre) d'un cercle est :",
            "options": ["2 * pi * R", "pi * R^2", "2 * pi * D"],
            "rep": "2 * pi * R",
        },
        {
            "id": "q3_5",
            "q": "Une droite qui possède un unique point commun avec un cercle est appelee :",
            "options": ["Une tangente", "Une secante", "Une corde"],
            "rep": "Une tangente",
        },
        {
            "id": "q3_6",
            "q": "Quelle est la formule exacte pour calculer l'aire d'un disque ?",
            "options": ["pi * R^2", "2 * pi * R", "pi * D"],
            "rep": "pi * R^2",
        },
        {
            "id": "q3_7",
            "q": "Une portion de plan delimitee par deux rayons et un arc de cercle s'appelle :",
            "options": ["Un secteur circulaire", "Un segment de cercle", "Une corde"],
            "rep": "Un secteur circulaire",
        },
        {
            "id": "q3_8",
            "q": "La droite tangente a un cercle en un point est toujours :",
            "options": [
                "Perpendiculaire au rayon passant par ce point",
                "Parallele au diametre du cercle",
                "Secante au centre du cercle",
            ],
            "rep": "Perpendiculaire au rayon passant par ce point",
        },
        {
            "id": "q3_9",
            "q": "Comment qualifie-t-on deux cercles qui possèdent le meme centre ?",
            "options": ["Concentriques", "Secants", "Tangents"],
            "rep": "Concentriques",
        },
        {
            "id": "q3_10",
            "q": "Le perimetre du cercle s'appelle egalement :",
            "options": ["La circonference", "La surface", "L'amplitude"],
            "rep": "La circonference",
        },
    ]

    st.session_state.ordre_quiz_tab3 = ordre_fixe_tab3

    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz sur les cercles (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab3_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox(
                "",
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse sur les cercles (Texte à trous - 10 cases - 10 pts)"
        )

        champs_c = [
            ("1. La distance constante reliant le centre au contour est le rayon", ["Choisir...", "rayon", "diametre", "corde"], "tab3_t1_final"),
            ("2. Un segment reliant deux points distincts sans passer par le centre est une corde", ["Choisir...", "corde", "rayon", "tangente"], "tab3_t2_final"),
            ("3. La longueur totale de la bordure exterieure est la circonference", ["Choisir...", "circonference", "aire", "diagonale"], "tab3_t3_final"),
            ("4. Pour trouver le diametre, on multiplie la valeur du rayon par 2", ["Choisir...", "2", "3", "4"], "tab3_t4_final"),
            ("5. La portion courbe du cercle comprise entre deux points s'appelle un arc", ["Choisir...", "arc", "secteur", "fleche"], "tab3_t5_final"),
            ("6. L'aire mesure l'espace occupe par la surface du disque", ["Choisir...", "disque", "cercle", "segment"], "tab3_t6_final"),
            ("7. La tangente ne croise la ligne du cercle qu'en un point", ["Choisir...", "point", "segment", "sommet"], "tab3_t7_final"),
            ("8. L'angle entre un rayon et la tangente a son extremite vaut 90 degres", ["Choisir...", "90", "180", "45"], "tab3_t8_final"),
            ("9. Deux cercles ayant des centres distincts mais se croisant sont secants", ["Choisir...", "secants", "concentriques", "isoles"], "tab3_t9_final"),
            ("10. La constante mathematique notee par la lettre grecque est pi", ["Choisir...", "pi", "alpha", "delta"], "tab3_t10_final"),
        ]

        for enonce, choix, cle in champs_c:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=cle,
                    disabled=verrouille,
                    label_visibility="collapsed",
                )


def afficher_questions_quadrilateres_dynamiques(verrouille=False):
    import streamlit as st

    ordre_fixe_tab2 = [
        {
            "id": "q2_1",
            "q": "Quelle est la somme des angles interieurs d'un quadrilatere convexe ?",
            "options": ["360 degres", "180 degres", "540 degres"],
            "rep": "360 degres",
        },
        {
            "id": "q2_2",
            "q": "Un parallelogramme possédant un angle droit est obligatoirement un :",
            "options": ["Rectangle", "Losange", "Trapeze"],
            "rep": "Rectangle",
        },
        {
            "id": "q2_3",
            "q": "Quelle est la caracteristique principale des diagonales d'un losange ?",
            "options": [
                "Elles sont perpendiculaires",
                "Elles sont de meme longueur",
                "Elles sont paralleles",
            ],
            "rep": "Elles sont perpendiculaires",
        },
        {
            "id": "q2_4",
            "q": "Le carre reunit simultanement les proprietes du :",
            "options": [
                "Rectangle et du losange",
                "Trapeze et du cerf-volant",
                "Rectangle et du trapeze",
            ],
            "rep": "Rectangle et du losange",
        },
        {
            "id": "q2_5",
            "q": "Comment appelle-t-on un quadrilatere qui a seulement deux cotes opposes paralleles ?",
            "options": ["Un trapeze", "Un parallelogramme", "Un losange"],
            "rep": "Un trapeze",
        },
        {
            "id": "q2_6",
            "q": "Si un quadrilatere a ses diagonales qui se coupent en leur milieu, c'est un :",
            "options": ["Parallelogramme", "Trapeze", "Quadrilatere quelconque"],
            "rep": "Parallelogramme",
        },
        {
            "id": "q2_7",
            "q": "Combien d'axes de symetrie un rectangle non carre possede-t-il ?",
            "options": ["2 axes", "4 axes", "0 axe"],
            "rep": "2 axes",
        },
        {
            "id": "q2_8",
            "q": "La formule de l'aire d'un parallelogramme est :",
            "options": [
                "Base multipliee par la hauteur",
                "Longueur multipliee par la largeur",
                "Base multipliee par cote",
            ],
            "rep": "Base multipliee par la hauteur",
        },
        {
            "id": "q2_9",
            "q": "Les diagonales d'un rectangle sont toujours :",
            "options": [
                "De meme longueur",
                "Perpendiculaires",
                "Bissectrices des angles",
            ],
            "rep": "De meme longueur",
        },
        {
            "id": "q2_10",
            "q": "Un quadrilatere dont les quatre cotes sont de meme longueur est un :",
            "options": ["Losange", "Rectangle", "Trapeze isoceles"],
            "rep": "Losange",
        },
    ]

    st.session_state.ordre_quiz_tab2 = ordre_fixe_tab2

    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz sur les quadrilatères (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tab2_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox(
                "",
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown(
            "##### Synthèse sur les quadrilatères (Texte à trous - 10 cases - 10 pts)"
        )

        champs = [
            ("1. Le rectangle possede quatre angles droits", ["Choisir...", "droits", "aigus", "plats"], "tab2_t1_final"),
            ("2. Les cotes opposes d'un parallelogramme sont paralleles", ["Choisir...", "paralleles", "perpendiculaires", "secants"], "tab2_t2_final"),
            ("3. Un carre possede des diagonales de meme longueur et perpendiculaires", ["Choisir...", "perpendiculaires", "paralleles", "obliques"], "tab2_t3_final"),
            ("4. Le losange a ses quatre cotes de longueurs egales", ["Choisir...", "egales", "differentes", "variables"], "tab2_t4_final"),
            ("5. Le point d'intersection des diagonales d'un parallelogramme est leur milieu", ["Choisir...", "milieu", "sommet", "foyer"], "tab2_t5_final"),
            ("6. Un trapeze possede deux cotes paralleles appele la grande et la petite base", ["Choisir...", "base", "hauteur", "diagonale"], "tab2_t6_final"),
            ("7. L'aire d'un rectangle se calcule en multipliant la longueur par la largeur", ["Choisir...", "largeur", "diagonale", "hauteur"], "tab2_t7_final"),
            ("8. Les diagonales d'un losange sont les axes de symetrie de la figure", ["Choisir...", "axes", "cotes", "hauteurs"], "tab2_t8_final"),
            ("9. Un quadrilatere non croise possede toujours deux diagonales", ["Choisir...", "diagonales", "mediatrices", "hauteurs"], "tab2_t9_final"),
            ("10. La somme complete des angles interieurs d'un quadrilatere vaut 360 degres", ["Choisir...", "360", "180", "90"], "tab2_t10_final"),
        ]

        for enonce, choix, cle in champs:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=cle,
                    disabled=verrouille,
                    label_visibility="collapsed",
                )



def afficher_questions_triangles_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le comportement et le controle des triangles (tab1)
    ordre_fixe_tab1 = [
        {
            "id": "q1_1",
            "q": "La somme des trois angles interieurs d'un triangle est toujours egale a :",
            "options": ["180 degres", "90 degres", "360 degres"],
            "rep": "180 degres",
        },
        {
            "id": "q1_2",
            "q": "Selon l'inegalite triangulaire, la longueur d'un cote doit etre strictement :",
            "options": [
                "Inferieure a la somme des deux autres",
                "Superieure a la somme des deux autres",
                "Egale a la difference des deux autres",
            ],
            "rep": "Inferieure a la somme des deux autres",
        },
        {
            "id": "q1_3",
            "q": "Comment appelle-t-on le cote oppose a l'angle droit dans un triangle rectangle ?",
            "options": ["L'hypotenuse", "La base", "La mediatrice"],
            "rep": "L'hypotenuse",
        },
        {
            "id": "q1_4",
            "q": "Un triangle possedant trois cotes de longueurs identiques est qualifie d' :",
            "options": ["Equilateral", "Isoceles", "Scalene"],
            "rep": "Equilateral",
        },
        {
            "id": "q1_5",
            "q": "Quelle droite passe par un sommet et coupe le cote oppose perpendiculairement ?",
            "options": ["La hauteur", "La mediane", "La bissectrice"],
            "rep": "La hauteur",
        },
        {
            "id": "q1_6",
            "q": "Le point d'intersection des trois medianes d'un triangle s'appelle le :",
            "options": [
                "Centre de gravite",
                "Orthocentre",
                "Centre du cercle inscrit",
            ],
            "rep": "Centre de gravite",
        },
        {
            "id": "q1_7",
            "q": "Les mediatrices des cotes d'un triangle se coupent au centre du cercle :",
            "options": ["Circonscrit", "Inscrit", "Exinscrit"],
            "rep": "Circonscrit",
        },
        {
            "id": "q1_8",
            "q": "La droite qui partage un angle de triangle en deux angles egaux est la :",
            "options": ["Bissectrice", "Mediatrice", "Mediane"],
            "rep": "Bissectrice",
        },
        {
            "id": "q1_9",
            "q": "Pour tracer un triangle de maniere unique avec le critere SAS, il faut connaitre :",
            "options": [
                "Deux cotes et l'angle entre eux",
                "Trois longueurs de cotes",
                "Un cote et deux angles adjacents",
            ],
            "rep": "Deux cotes et l'angle entre eux",
        },
        {
            "id": "q1_10",
            "q": "Dans un triangle isoceles, les deux angles a la base sont toujours :",
            "options": ["Egaux", "Complementaires", "Obtus"],
            "rep": "Egaux",
        },
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
                label_visibility="collapsed",
            )

    with col_double_trous_tab1:
        st.markdown(
            "##### Synthese sur les proprietes des triangles (Texte a trous - 10 cases - 10 pts)"
        )

        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1:
            st.write(
                "1. Le calcul de la surface interieure du triangle correspond a son aire"
            )
        with c2:
            st.selectbox(
                "",
                ["Choisir...", "aire", "perimetre", "volume"],
                key="tab1_t1_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3:
            st.write(
                "2. La droite passant par le milieu d'un cote et un sommet est une mediane"
            )
        with c4:
            st.selectbox(
                "",
                ["Choisir...", "mediane", "hauteur", "mediatrice"],
                key="tab1_t2_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5:
            st.write(
                "3. Les trois hauteurs d'un triangle se coupent en un point nomme orthocentre"
            )
        with c6:
            st.selectbox(
                "",
                ["Choisir...", "orthocentre", "gravite", "centre"],
                key="tab1_t3_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7:
            st.write(
                "4. La mediatrice coupe perpendiculairement un cote en son milieu"
            )
        with c8:
            st.selectbox(
                "",
                ["Choisir...", "milieu", "sommet", "tiers"],
                key="tab1_t4_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9:
            st.write(
                "5. Les bissectrices se croisent au centre du cercle inscrit interieurement"
            )
        with c10:
            st.selectbox(
                "",
                ["Choisir...", "inscrit", "circonscrit", "orthogonal"],
                key="tab1_t5_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11:
            st.write(
                "6. Le theoreme de Pythagore s'applique uniquement dans un triangle rectangle"
            )
        with c12:
            st.selectbox(
                "",
                ["Choisir...", "rectangle", "isoceles", "equilateral"],
                key="tab1_t6_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13:
            st.write(
                "7. Un triangle possedant deux cotes egaux est un triangle isoceles"
            )
        with c14:
            st.selectbox(
                "",
                ["Choisir...", "isoceles", "equilateral", "scalene"],
                key="tab1_t7_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15:
            st.write(
                "8. La formule classique de l'aire necessite de multiplier la base par la hauteur"
            )
        with c16:
            st.selectbox(
                "",
                ["Choisir...", "hauteur", "mediane", "diagonale"],
                key="tab1_t8_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17:
            st.write(
                "9. Pour la construction avec le critere SSS, il faut connaitre les 3 cotes"
            )
        with c18:
            st.selectbox(
                "",
                ["Choisir...", "cotes", "angles", "sommets"],
                key="tab1_t9_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19:
            st.write(
                "10. Chaque angle interieur d'un triangle equilateral mesure toujours 60 degres"
            )
        with c20:
            st.selectbox(
                "",
                ["Choisir...", "60", "90", "180"],
                key="tab1_t10_final",
                disabled=verrouille,
                label_visibility="collapsed",
            )

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
    st.header("Exploration du Triangle")

    # SECTION 1 : THÉORIE ET CONFIGURATION DES DROITES REMARQUABLES
    st.subheader("1. Propriétés et Droites Remarquables")
    col_th1, col_th2 = st.columns(2)

    with col_th1:
        st.markdown(
            """
        **Propriétés Fondamentales :**
        *   **Somme des angles :** La somme des angles intérieurs est toujours égale à **180°**.
        *   **Inégalité triangulaire :** La longueur d'un côté est toujours strictement inférieure à la somme des deux autres.
        *   **Aire :** $\\text{Aire} = \\frac{\\text{Base} \\times \\text{Hauteur}}{2}$
        *   **Périmètre :** $\\text{Périmètre} = a + b + c$
        
        **Triangles Spéciaux :**
        *   **Isocèle :** Deux côtés égaux et deux angles à la base égaux.
        *   **Équilatéral :** Trois côtés égaux et trois angles égaux à 60°.
        *   **Rectangle :** Un angle droit (90°), le côté opposé est l'hypoténuse ($a^2 + b^2 = c^2$).
        """
        )

    with col_th2:
        st.write("**Tracé des droites remarquables (Cochez pour voir sur le graphique ci-dessous) :**")
        voir_hauteur = st.checkbox("Afficher les Hauteurs (Rouge)", key="tri_voir_hauteur")
        voir_mediane = st.checkbox("Afficher les Médianes (Vert)", key="tri_voir_mediane")
        # Ajout des deux droites manquantes
        voir_mediatrice = st.checkbox("Afficher les Médiatrices (Cyan)", key="tri_voir_mediatrice")
        voir_bissectrice = st.checkbox("Afficher les Bissectrices (Magenta)", key="tri_voir_bissectrice")
      
    # ==========================================
    # SECTION 2 : CONSTRUCTION ET TRACÉ D'UN TRIANGLE
    # ==========================================
    st.markdown("---")
    st.subheader("2. Construction et Tracé Dynamique")

    choix_construction = st.selectbox(
        "Choisissez votre méthode de construction :",
        [
            "3 longueurs de côtés (SSS)",
            "2 côtés et l'angle entre eux (SAS)",
            "1 côté et les 2 angles adjacents (ASA)",
        ],
    )

    # Initialisation des variables géométriques pour le calcul
    a, b, c = 0.0, 0.0, 0.0
    possible = False

    if choix_construction == "3 longueurs de côtés (SSS)":
        c = st.number_input(
            "Longueur du côté c (Base [AB])",
            min_value=0.1,
            value=5.0,
            step=0.1,
        )
        b = st.number_input(
            "Longueur du côté b (Côté [AC])",
            min_value=0.1,
            value=4.0,
            step=0.1,
        )
        a = st.number_input(
            "Longueur du côté a (Côté [BC])",
            min_value=0.1,
            value=3.0,
            step=0.1,
        )

        # Vérification de l'inégalité triangulaire
        if (a + b > c) and (a + c > b) and (b + c > a):
            possible = True
            angle_A_rad = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
        else:
            st.error(
                "Construction impossible : la somme de deux côtés doit être strictement supérieure au troisième côté."
            )

    elif choix_construction == "2 côtés et l'angle entre eux (SAS)":
        c = st.number_input(
            "Longueur du côté c (Base [AB])",
            min_value=0.1,
            value=6.0,
            step=0.1,
        )
        angle_A_deg = st.number_input(
            "Angle A en degrés (entre [AB] et [AC])",
            min_value=1.0,
            max_value=179.0,
            value=60.0,
            step=1.0,
        )
        b = st.number_input(
            "Longueur du côté b (Côté [AC])",
            min_value=0.1,
            value=5.0,
            step=0.1,
        )

        possible = True
        angle_A_rad = math.radians(angle_A_deg)
        a = math.sqrt(b**2 + c**2 - 2 * b * c * math.cos(angle_A_rad))

    elif choix_construction == "1 côté et les 2 angles adjacents (ASA)":
        c = st.number_input(
            "Longueur du côté c (Base [AB])",
            min_value=0.1,
            value=6.0,
            step=0.1,
        )
        angle_A_deg = st.number_input(
            "Angle A en degrés (adjacent à A)",
            min_value=1.0,
            max_value=179.0,
            value=45.0,
            step=1.0,
        )
        angle_B_deg = st.number_input(
            "Angle B en degrés (adjacent à B)",
            min_value=1.0,
            max_value=179.0,
            value=60.0,
            step=1.0,
        )

        if angle_A_deg + angle_B_deg < 180:
            possible = True
            angle_A_rad = math.radians(angle_A_deg)
            angle_B_rad = math.radians(angle_B_deg)
            angle_C_rad = math.pi - (angle_A_rad + angle_B_rad)

            a = c * math.sin(angle_A_rad) / math.sin(angle_C_rad)
            b = c * math.sin(angle_B_rad) / math.sin(angle_C_rad)
        else:
            st.error(
                "La somme des deux angles doit être strictement inférieure à 180°."
            )

    # Si le triangle est valide, calcul des coordonnées et tracé
    if possible:
        Ax, Ay = 0.0, 0.0
        Bx, By = c, 0.0
        Cx = b * math.cos(angle_A_rad)
        Cy = b * math.sin(angle_A_rad)

        perimetre = a + b + c
        s = perimetre / 2
        aire = math.sqrt(s * (s - a) * (s - b) * (s - c))

        st.success("Triangle valide.")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(label="Périmètre du triangle", value=f"{perimetre:.2f} cm")
        res_col2.metric(label="Aire du triangle", value=f"{aire:.2f} cm²")

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot([Ax, Bx, Cx, Ax], [Ay, By, Cy, Ay], marker="o", color="#1f77b4", linewidth=2, label="Triangle")
        
        # 1. OPTION : MÉDIANES (Vert pointillé)
        if voir_mediane:
            ax.plot([Cx, c/2.0], [Cy, 0.0], color="green", linestyle=":", linewidth=1.5, label="Médiane")
            ax.plot([Ax, (Bx+Cx)/2.0], [Ay, (By+Cy)/2.0], color="green", linestyle=":", linewidth=1.5)
            ax.plot([Bx, Cx/2.0], [By, Cy/2.0], color="green", linestyle=":", linewidth=1.5)

        # 2. OPTION : HAUTEURS (Rouge tirets)
        if voir_hauteur:
            ax.plot([Cx, Cx], [Cy, 0.0], color="red", linestyle="--", linewidth=1.5, label="Hauteur")
            
            # Pied de hauteur issue de A
            v_BC_x, v_BC_y = Bx - Cx, By - Cy
            mag_BC = v_BC_x**2 + v_BC_y**2
            t_A = ((Ax - Cx) * v_BC_x + (Ay - Cy) * v_BC_y) / mag_BC if mag_BC > 0 else 0.0
            ax.plot([Ax, Cx + t_A * v_BC_x], [Ay, Cy + t_A * v_BC_y], color="red", linestyle="--", linewidth=1.5)
            
            # Pied de hauteur issue de B
            v_CA_x, v_CA_y = Ax - Cx, Ay - Cy
            mag_CA = v_CA_x**2 + v_CA_y**2
            t_B = ((Bx - Cx) * v_CA_x + (By - Cy) * v_CA_y) / mag_CA if mag_CA > 0 else 0.0
            ax.plot([Bx, Cx + t_B * v_CA_x], [By, Cy + t_B * v_CA_y], color="red", linestyle="--", linewidth=1.5)

        # 3. OPTION : MÉDIATRICES & CERCLE CIRCONSCRIT (Cyan)
        if voir_mediatrice:
            D = 2 * (Ax*(By - Cy) + Bx*(Cy - Ay) + Cx*(Ay - By))
            if abs(D) > 1e-5:
                Ux = ((Ax**2 + Ay**2)*(By - Cy) + (Bx**2 + By**2)*(Cy - Ay) + (Cx**2 + Cy**2)*(Ay - By)) / D
                Uy = ((Ax**2 + Ay**2)*(Cx - Bx) + (Bx**2 + By**2)*(Ax - Cx) + (Cx**2 + Cy**2)*(Bx - Ax)) / D
                
                # Tracé des segments des médiatrices
                ax.plot([c/2.0, Ux], [0.0, Uy], color="cyan", linestyle="-.", linewidth=1.5, label="Médiatrice")
                ax.plot([Cx/2.0, Ux], [Cy/2.0, Uy], color="cyan", linestyle="-.", linewidth=1.5)
                ax.plot([(Bx+Cx)/2.0, Ux], [(By+Cy)/2.0, Uy], color="cyan", linestyle="-.", linewidth=1.5)
                
                # Tracé du cercle circonscrit (Rayon R_c = distance entre le centre U et un sommet)
                rayon_circonscrit = math.sqrt((Ux - Ax)**2 + (Uy - Ay)**2)
                cercle_circonscrit = plt.Circle((Ux, Uy), rayon_circonscrit, color="#17becf", fill=False, linestyle="-.", linewidth=1.2, label="Cercle circonscrit")
                ax.add_patch(cercle_circonscrit)

        # 4. OPTION : BISSECTRICES & CERCLE INSCRIT (Magenta / Orange)
        if voir_bissectrice:
            # Centre du cercle inscrit (Incentre I)
            Ix = (a * Ax + b * Bx + c * Cx) / perimetre
            Iy = (a * Ay + b * By + c * Cy) / perimetre
            
            # Tracé des droites bissectrices
            ax.plot([Ax, Ix], [Ay, Iy], color="magenta", linestyle="-", linewidth=1.2, label="Bissectrice")
            ax.plot([Bx, Ix], [By, Iy], color="magenta", linestyle="-", linewidth=1.2)
            ax.plot([Cx, Ix], [Cy, Iy], color="magenta", linestyle="-", linewidth=1.2)
            
            # Tracé du cercle inscrit (Rayon r_i = Aire / demi-périmètre)
            rayon_inscrit = aire / s
            cercle_inscrit = plt.Circle((Ix, Iy), rayon_inscrit, color="#ff7f0e", fill=False, linestyle="-", linewidth=1.2, label="Cercle inscrit")
            ax.add_patch(cercle_inscrit)

        ax.text(Ax - 0.2, Ay - 0.2, "A", fontsize=12, fontweight="bold")
        ax.text(Bx + 0.1, By - 0.2, "B", fontsize=12, fontweight="bold")
        ax.text(Cx, Cy + 0.2, "C", fontsize=12, fontweight="bold")
        ax.set_aspect("equal")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)
        

    st.write("---")
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    afficher_questions_triangles_dynamiques(verrouille=verrou_at1)

    st.write("---")
    st.subheader("Synthese et validation sur les triangles")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_suite1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.",
        key="check_certif_generalites_final_net",
        disabled=verrou_at1,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1",
        key="btn_export_suite1_official_net",
        use_container_width=True,
        disabled=verrou_at1,
    ):
        if (
            st.session_state.get("nom_var", "Nom") == "Nom"
            or st.session_state.get("prenom_var", "Prenom") == "Prenom"
        ):
            st.error(
                "Action refusee : Saisissez votre identite dans l'onglet 'Identification'."
            )
        elif not case_certif_suite1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_tab1" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1:
                    reponse_eleve = st.session_state.get(
                        f"tab1_at1_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction des Textes a trous (10 points)
            score_t1 = sum(
                [
                    st.session_state.get("tab1_t1_final") == "aire",
                    st.session_state.get("tab1_t2_final") == "mediane",
                    st.session_state.get("tab1_t3_final") == "orthocentre",
                    st.session_state.get("tab1_t4_final") == "milieu",
                    st.session_state.get("tab1_t5_final") == "inscrit",
                    st.session_state.get("tab1_t6_final") == "rectangle",
                    st.session_state.get("tab1_t7_final") == "isoceles",
                    st.session_state.get("tab1_t8_final") == "hauteur",
                    st.session_state.get("tab1_t9_final") == "cotes",
                    st.session_state.get("tab1_t10_final") == "60",
                ]
            )

            st.session_state.score_suite1_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1 = round(
                float(score_q1 + score_t1), 1
            )
            st.session_state.suite_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 1 ---
    if st.session_state.get("suite_verrouille_tab1", False):
        scr1 = st.session_state.get("score_suite1_p1", 0.0)
        scr2 = st.session_state.get("score_suite1_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite1", 0.0)

        from datetime import datetime, timedelta

        timestamp_suite1 = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d a %H:%M:%S"
        )

        st.success(
            f"ATELIER TRIANGLES SCELLE | Note de session : {tot_s:.1f} / 20"
        )

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Proprietes Triangles - {n_eleve}</title>
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
                <p>Atelier 1 : Proprietes et geometrie des triangles</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz de Notions de Base : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese des proprietes : <strong>{scr2:.1f} / 10</strong><br>
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
            for num, q_item in enumerate(
                st.session_state.ordre_quiz_tab1, 1
            ):
                saisie = st.session_state.get(
                    f"tab1_at1_final_g_{q_item['id']}", "Choisir..."
                )
                attendu = q_item["rep"]
                v_lbl = (
                    "CORRECT"
                    if str(saisie).strip() == str(attendu).strip()
                    else "INCORRECT"
                )
                v_class = (
                    "status-correct"
                    if v_lbl == "CORRECT"
                    else "status-incorrect"
                )
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
            (
                "1. Le calcul de la surface interieure du triangle correspond a son aire",
                "tab1_t1_final",
                "aire",
            ),
            (
                "2. La droite passant par le milieu d'un cote et un sommet est une mediane",
                "tab1_t2_final",
                "mediane",
            ),
            (
                "3. Les trois hauteurs d'un triangle se coupent en un point nomme orthocentre",
                "tab1_t3_final",
                "orthocentre",
            ),
            (
                "4. La mediatrice coupe perpendiculairement un cote en son milieu",
                "tab1_t4_final",
                "milieu",
            ),
            (
                "5. Les bissectrices se croisent au centre du cercle inscrit interieurement",
                "tab1_t5_final",
                "inscrit",
            ),
            (
                "6. Le theoreme de Pythagore s'applique uniquement dans un triangle rectangle",
                "tab1_t6_final",
                "rectangle",
            ),
            (
                "7. Un triangle possedant deux cotes egaux est un triangle isoceles",
                "tab1_t7_final",
                "isoceles",
            ),
            (
                "8. La formule classique de l'aire necessite de multiplier la base par la hauteur",
                "tab1_t8_final",
                "hauteur",
            ),
            (
                "9. Pour la construction avec le critere SSS, il faut connaitre les 3 cotes",
                "tab1_t9_final",
                "cotes",
            ),
            (
                "10. Chaque angle interieur d'un triangle equilateral mesure toujours 60 degres",
                "tab1_t10_final",
                "60",
            ),
        ]

        for num, (enonce, cle, attendu) in enumerate(phrases_trous1, 1):
            saisie = self.combos_trous[num - 1][0].get()
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            
            # Cette ligne est désormais parfaitement alignée avec le reste du bloc
            html_export_suites += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_suites += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Enregistrement du fichier HTML généré dans le session_state
        st.session_state.html_export_tab1 = html_export_suites

        # Génération du nom de fichier standardisé et unique via votre fonction dédiée
        nom_complet_fichier = preparer_nom_fichier("Les_triangles")

        # Bouton de téléchargement officiel pour l'élève
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_suites,
            file_name=nom_complet_fichier,
            mime="text/html",
            use_container_width=True,
        )

with tab2:
    st.header("Exploration des Quadrilatères")

    # ==========================================
    # SECTION 1 : PROPRIÉTÉS DES QUADRILATÈRES
    # ==========================================
    st.subheader("1. Propriétés Fondamentales")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **Propriétés Communes :**
        *   **Somme des angles :** La somme des angles intérieurs d'un quadrilatère convexe est toujours de **360°**.
        *   **Périmètre :** Somme des longueurs des quatre côtés ($a + b + c + d$).
        
        **Quadrilatères Particuliers :**
        *   **Parallélogramme :** Côtés opposés parallèles et de même longueur. Les diagonales se coupent en leur milieu.
        *   **Rectangle :** Parallélogramme avec quatre angles droits (90°). Diagonales de même longueur. $\\text{Aire} = \\text{Longueur} \\times \\text{Largeur}$.
        *   **Losange :** Parallélogramme avec quatre côtés égaux. Diagonales perpendiculaires.
        *   **Carré :** À la fois un rectangle et un losange (quatre côtés égaux et quatre angles droits). Diagonales égales et perpendiculaires.
        """
        )

    with col2:
        st.write(
            "**Éléments caractéristiques (Cochez pour voir les définitions) :**"
        )

        voir_diagonales = st.checkbox("Les Diagonales")
        if voir_diagonales:
            st.info(
                "**Diagonales :** Segments reliant deux sommets non consécutifs. Elles se coupent en leur milieu pour tous les parallélogrammes."
            )

        voir_axes = st.checkbox("Les Axes de symétrie")
        if voir_axes:
            st.info(
                "**Axes de symétrie :** Le rectangle en possède 2 (ses médiatrices), le losange en possède 2 (ses diagonales), et le carré en possède 4."
            )

        voir_hauteur_q = st.checkbox("La Hauteur d'un parallélogramme")
        if voir_hauteur_q:
            st.info(
                "**Hauteur :** Distance perpendiculaire entre deux côtés opposés parallèles. $\\text{Aire} = \\text{Base} \\times \\text{Hauteur}$."
            )

    # ==========================================
    # SECTION 2 : CONSTRUCTION ET TRACÉ DYNAMIQUE
    # ==========================================
    st.markdown("---")
    st.subheader("2. Construction graphique")

    type_quadri = st.selectbox(
        "Sélectionnez le quadrilatère à tracer :",
        ["Carré", "Rectangle", "Parallélogramme"],
    )

    fig, ax = plt.subplots(figsize=(5, 4))
    trace_possible = False
    perimetre_q, aire_q = 0.0, 0.0

    if type_quadri == "Carré":
        cote_c = st.number_input(
            "Longueur du côté (cm) :", min_value=0.1, value=4.0, step=0.1
        )
        perimetre_q = cote_c * 4
        aire_q = cote_c**2
        # Dessin du carré
        rect = patches.Rectangle(
            (0, 0), cote_c, cote_c, linewidth=2, edgecolor="#2ca02c", facecolor="none"
        )
        ax.add_patch(rect)
        ax.set_xlim(-0.5, cote_c + 0.5)
        ax.set_ylim(-0.5, cote_c + 0.5)
        trace_possible = True

    elif type_quadri == "Rectangle":
        largeur_r = st.number_input(
            "Largeur (cm) :", min_value=0.1, value=3.0, step=0.1
        )
        longueur_r = st.number_input(
            "Longueur (cm) :", min_value=0.1, value=5.0, step=0.1
        )
        perimetre_q = (largeur_r + longueur_r) * 2
        aire_q = largeur_r * longueur_r
        # Dessin du rectangle
        rect = patches.Rectangle(
            (0, 0), longueur_r, largeur_r, linewidth=2, edgecolor="#2ca02c", facecolor="none"
        )
        ax.add_patch(rect)
        ax.set_xlim(-0.5, longueur_r + 0.5)
        ax.set_ylim(-0.5, largeur_r + 0.5)
        trace_possible = True

    elif type_quadri == "Parallélogramme":
        base_p = st.number_input(
            "Longueur de la base AB (cm) :", min_value=0.1, value=5.0, step=0.1
        )
        cote_p = st.number_input(
            "Longueur du côté AD (cm) :", min_value=0.1, value=3.0, step=0.1
        )
        angle_deg = st.number_input(
            "Angle A (degrés) :", min_value=1.0, max_value=179.0, value=60.0, step=1.0
        )

        angle_rad = math.radians(angle_deg)
        perimetre_q = (base_p + cote_p) * 2
        aire_q = base_p * (cote_p * math.sin(angle_rad))

        # Coordonnées des sommets
        Ax, Ay = 0.0, 0.0
        Bx, By = base_p, 0.0
        Dx = cote_p * math.cos(angle_rad)
        Dy = cote_p * math.sin(angle_rad)
        Cx = Bx + Dx
        Cy = By + Dy

        ax.plot(
            [Ax, Bx, Cx, Dx, Ax], [Ay, By, Cy, Dy, Ay], color="#2ca02c", linewidth=2, marker="o"
        )
        ax.set_xlim(-0.5, max(Bx, Cx, Dx) + 0.5)
        ax.set_ylim(-0.5, max(Dy, Cy) + 0.5)
        trace_possible = True

    if trace_possible:
        st.success("Structure valide.")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(label="Périmètre calculé", value=f"{perimetre_q:.2f} cm")
        res_col2.metric(label="Aire calculée", value=f"{aire_q:.2f} cm²")

        ax.set_aspect("equal")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_title(f"Représentation graphique : {type_quadri}")
        st.pyplot(fig)

    # ==========================================
    # SECTION 3 : ÉVALUATION ET EXPORTATION
    # ==========================================
    st.write("---")
    if "quadri_verrouille_tab2" not in st.session_state:
        st.session_state.quadri_verrouille_tab2 = False
    verrou_at2 = st.session_state.quadri_verrouille_tab2

    afficher_questions_quadrilateres_dynamiques(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation des quadrilatères")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_quadri = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 2.",
        key="check_certif_quadri_final_net",
        disabled=verrou_at2,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2",
        key="btn_export_quadri_official_net",
        use_container_width=True,
        disabled=verrou_at2,
    ):
        if (
            st.session_state.get("nom_var", "Nom") == "Nom"
            or st.session_state.get("prenom_var", "Prenom") == "Prenom"
        ):
            st.error(
                "Action refusee : Saisissez votre identite dans l'onglet 'Identification'."
            )
        elif not case_certif_quadri:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Correction du Quiz
            score_q2 = 0.0
            if "ordre_quiz_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2:
                    reponse = st.session_state.get(
                        f"tab2_at2_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(reponse) == str(q_item["rep"]):
                        score_q2 += 1.0

            # Correction des Trous
            score_t2 = sum(
                [
                    st.session_state.get("tab2_t1_final") == "droits",
                    st.session_state.get("tab2_t2_final") == "paralleles",
                    st.session_state.get("tab2_t3_final") == "perpendiculaires",
                    st.session_state.get("tab2_t4_final") == "egales",
                    st.session_state.get("tab2_t5_final") == "milieu",
                    st.session_state.get("tab2_t6_final") == "base",
                    st.session_state.get("tab2_t7_final") == "largeur",
                    st.session_state.get("tab2_t8_final") == "axes",
                    st.session_state.get("tab2_t9_final") == "diagonales",
                    st.session_state.get("tab2_t10_final") == "360",
                ]
            )

            st.session_state.score_quadri_p1 = round(float(score_q2), 1)
            st.session_state.score_quadri_p2 = round(float(score_t2), 1)
            st.session_state.score_final_quadri = round(
                float(score_q2 + score_t2), 1
            )
            st.session_state.quadri_verrouille_tab2 = True
            st.rerun()

    # Génération du Document HTML Scellé
    if st.session_state.get("quadri_verrouille_tab2", False):
        scr1 = st.session_state.get("score_quadri_p1", 0.0)
        scr2 = st.session_state.get("score_quadri_p2", 0.0)
        tot_s = st.session_state.get("score_final_quadri", 0.0)

        from datetime import datetime, timedelta

        timestamp_quadri = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d a %H:%M:%S"
        )

        st.success(
            f"ATELIER QUADRILATERES SCELLE | Note de session : {tot_s:.1f} / 20"
        )

        html_export_quadri = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Proprietes Quadrilateres - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #16a34a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Evaluation de Geometrie</h1>
                <p>Atelier 2 : Proprietes des Quadrilateres</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_quadri}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #16a34a;">
                Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2" in st.session_state:
            for num, q_item in enumerate(
                st.session_state.ordre_quiz_tab2, 1
            ):
                saisie = st.session_state.get(
                    f"tab2_at2_final_g_{q_item['id']}", "Choisir..."
                )
                attendu = q_item["rep"]
                v_lbl = (
                    "CORRECT"
                    if str(saisie).strip() == str(attendu).strip()
                    else "INCORRECT"
                )
                v_class = (
                    "status-correct"
                    if v_lbl == "CORRECT"
                    else "status-incorrect"
                )
                html_export_quadri += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_quadri += """
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
            ("1. Le rectangle possede quatre angles droits", "tab2_t1_final", "droits"),
            ("2. Les cotes opposes d'un parallelogramme sont paralleles", "tab2_t2_final", "paralleles"),
            ("3. Un carre possede des diagonales de meme longueur et perpendiculaires", "tab2_t3_final", "perpendiculaires"),
            ("4. Le losange a ses quatre cotes de longueurs egales", "tab2_t4_final", "egales"),
            ("5. Le point d'intersection des diagonales d'un parallelogramme est leur milieu", "tab2_t5_final", "milieu"),
            ("6. Un trapeze possede deux cotes paralleles appele la grande et la petite base", "tab2_t6_final", "base"),
            ("7. L'aire d'un rectangle se calcule en multipliant la longueur par la largeur", "tab2_t7_final", "largeur"),
            ("8. Les diagonales d'un losange sont les axes de symetrie de la figure", "tab2_t8_final", "axes"),
            ("9. Un quadrilatere non croise possede toujours deux diagonales", "tab2_t9_final", "diagonales"),
            ("10. La somme complete des angles interieurs d'un quadrilatere vaut 360 degres", "tab2_t10_final", "360"),
        ]

        for num, (enonce, cle, attendu) in enumerate(phrases_trous2, 1):
            saisie = st.session_state.get(cle, "Choisir...")
            v_lbl = (
                "CORRECT"
                if str(saisie).strip() == str(attendu).strip()
                else "INCORRECT"
            )
            v_class = (
                "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            )
            html_export_quadri += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_quadri += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.session_state.html_export_tab2 = html_export_quadri

        # Bouton de téléchargement finalisé
        nom_complet_fichier_q = preparer_nom_fichier("Les_quadrilateres")
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_quadri,
            file_name=nom_complet_fichier_q.replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
            key="btn_dl_html_tab2",
            )


with tab3:
    st.header("Exploration du Cercle")

    # ==========================================
    # SECTION 1 : PROPRIÉTÉS DU CERCLE
    # ==========================================
    st.subheader("1. Propriétés Fondamentales")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **Définitions de Base :**
        *   **Cercle :** Ensemble de tous les points du plan situés à égale distance d'un point fixe appelé le centre.
        *   **Rayon ($R$) :** Segment reliant le centre à un point quelconque du cercle.
        *   **Diamètre ($D$) :** Segment passant par le centre et reliant deux points opposés du cercle ($D = 2 \\times R$).
        *   **Corde :** Segment reliant deux points quelconques du cercle sans obligatoirement passer par le centre.
        
        **Formules Clés :**
        *   **Périmètre (Circonférence) :** $P = 2 \\times \\pi \\times R = \\pi \\times D$
        *   **Aire du disque :** $A = \\pi \\times R^2$
        """
        )

    with col2:
        st.write(
            "**Éléments géométriques (Cochez pour voir les définitions) :**"
        )

        voir_arc = st.checkbox("L'Arc de cercle")
        if voir_arc:
            st.info(
                "**Arc de cercle :** Portion de la circonférence comprise entre deux points distincts du cercle."
            )

        voir_tangente = st.checkbox("La Tangente")
        if voir_tangente:
            st.info(
                "**Tangente :** Droite qui touche le cercle en un seul point unique. Elle est toujours perpendiculaire au rayon passant par ce point."
            )

        voir_secteur = st.checkbox("Le Secteur circulaire")
        if voir_secteur:
            st.info(
                "**Secteur circulaire :** Portion de la surface du disque délimitée par deux rayons et un arc de cercle (comme une part de gâteau)."
            )

    # ==========================================
    # SECTION 2 : TRACÉ DYNAMIQUE ET CALCULS
    # ==========================================
    st.markdown("---")
    st.subheader("2. Visualisation dynamique")

    rayon = st.number_input(
        "Saisissez la longueur du rayon R (cm) :",
        min_value=0.1,
        value=3.0,
        step=0.1,
    )

    if rayon > 0:
        # Calculs géométriques
        perimetre_c = 2 * math.pi * rayon
        aire_c = math.pi * (rayon**2)

        st.success("Calculs effectues.")
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(
            label="Périmètre (Circonférence)", value=f"{perimetre_c:.2f} cm"
        )
        res_col2.metric(label="Aire du disque", value=f"{aire_c:.2f} cm²")

        # Tracé avec Matplotlib
        fig, ax = plt.subplots(figsize=(5, 4))
        cercle_dessin = plt.Circle(
            (0, 0), rayon, color="#e377c2", fill=False, linewidth=2
        )
        ax.add_patch(cercle_dessin)

        # Dessin du centre et du rayon pour illustration
        ax.plot(0, 0, marker="o", color="black")
        ax.text(-0.2, -0.2, "O", fontsize=10, fontweight="bold")
        ax.plot([0, rayon], [0, 0], color="red", linestyle="--", linewidth=1.5)
        ax.text(rayon / 2, 0.1, f"R = {rayon} cm", color="red", fontsize=10)

        # Ajustement des axes
        limite = rayon + 1
        ax.set_xlim(-limite, limite)
        ax.set_ylim(-limite, limite)
        ax.set_aspect("equal")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_title("Représentation graphique du cercle")

        st.pyplot(fig)

    # ==========================================
    # SECTION 3 : ÉVALUATION ET EXPORTATION
    # ==========================================
    st.write("---")
    if "cercle_verrouille_tab3" not in st.session_state:
        st.session_state.cercle_verrouille_tab3 = False
    verrou_at3 = st.session_state.cercle_verrouille_tab3

    afficher_questions_cercles_dynamiques(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthèse et validation sur les cercles")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_cercle = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 3.",
        key="check_certif_cercle_final_net",
        disabled=verrou_at3,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3",
        key="btn_export_cercle_official_net",
        use_container_width=True,
        disabled=verrou_at3,
    ):
        if (
            st.session_state.get("nom_var", "Nom") == "Nom"
            or st.session_state.get("prenom_var", "Prenom") == "Prenom"
        ):
            st.error(
                "Action refusee : Saisissez votre identite dans l'onglet 'Identification'."
            )
        elif not case_certif_cercle:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Correction du Quiz
            score_q3 = 0.0
            if "ordre_quiz_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3:
                    reponse = st.session_state.get(
                        f"tab3_at3_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(reponse) == str(q_item["rep"]):
                        score_q3 += 1.0

            # Correction des Trous
            score_t3 = sum(
                [
                    st.session_state.get("tab3_t1_final") == "rayon",
                    st.session_state.get("tab3_t2_final") == "corde",
                    st.session_state.get("tab3_t3_final") == "circonference",
                    st.session_state.get("tab3_t4_final") == "2",
                    st.session_state.get("tab3_t5_final") == "arc",
                    st.session_state.get("tab3_t6_final") == "disque",
                    st.session_state.get("tab3_t7_final") == "point",
                    st.session_state.get("tab3_t8_final") == "90",
                    st.session_state.get("tab3_t9_final") == "secants",
                    st.session_state.get("tab3_t10_final") == "pi",
                ]
            )

            st.session_state.score_cercle_p1 = round(float(score_q3), 1)
            st.session_state.score_cercle_p2 = round(float(score_t3), 1)
            st.session_state.score_final_cercle = round(
                float(score_q3 + score_t3), 1
            )
            st.session_state.cercle_verrouille_tab3 = True
            st.rerun()

    # Génération du Document HTML Scellé
    if st.session_state.get("cercle_verrouille_tab3", False):
        scr1 = st.session_state.get("score_cercle_p1", 0.0)
        scr2 = st.session_state.get("score_cercle_p2", 0.0)
        tot_s = st.session_state.get("score_final_cercle", 0.0)

        from datetime import datetime, timedelta

        timestamp_cercle = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d a %H:%M:%S"
        )

        st.success(
            f"ATELIER CERCLES SCELLE | Note de session : {tot_s:.1f} / 20"
        )

        html_export_cercle = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Proprietes Cercles - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #e377c2; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Evaluation de Geometrie</h1>
                <p>Atelier 3 : Proprietes du Cercle et du Disque</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_cercle}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #e377c2;">
                Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3" in st.session_state:
            for num, q_item in enumerate(
                st.session_state.ordre_quiz_tab3, 1
            ):
                saisie = st.session_state.get(
                    f"tab3_at3_final_g_{q_item['id']}", "Choisir..."
                )
                attendu = q_item["rep"]
                v_lbl = (
                    "CORRECT"
                    if str(saisie).strip() == str(attendu).strip()
                    else "INCORRECT"
                )
                v_class = (
                    "status-correct"
                    if v_lbl == "CORRECT"
                    else "status-incorrect"
                )
                html_export_cercle += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cercle += """
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
            ("1. La distance constante reliant le centre au contour est le rayon", "tab3_t1_final", "rayon"),
            ("2. Un segment reliant deux points distincts sans passer par le centre est une corde", "tab3_t2_final", "corde"),
            ("3. La longueur totale de la bordure exterieure est la circonference", "tab3_t3_final", "circonference"),
            ("4. Pour trouver le diametre, on multiplie la valeur du rayon par 2", "tab3_t4_final", "2"),
            ("5. La portion courbe du cercle comprise entre deux points s'appelle un arc", "tab3_t5_final", "arc"),
            ("6. L'aire mesure l'espace occupe par la surface du disque", "tab3_t6_final", "disque"),
            ("7. La tangente ne croise la ligne du cercle qu'en un point", "tab3_t7_final", "point"),
            ("8. L'angle entre un rayon et la tangente a son extremite vaut 90 degres", "tab3_t8_final", "90"),
            ("9. Deux cercles ayant des centres distincts mais se croisant sont secants", "tab3_t9_final", "secants"),
            ("10. La constante mathematique notee par la lettre grecque est pi", "tab3_t10_final", "pi"),
        ]

        for num, (enonce, cle, attendu) in enumerate(phrases_trous3, 1):
            saisie = st.session_state.get(cle, "Choisir...")
            v_lbl = (
                "CORRECT"
                if str(saisie).strip() == str(attendu).strip()
                else "INCORRECT"
            )
            v_class = (
                "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            )
            html_export_cercle += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cercle += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.session_state.html_export_tab3 = html_export_cercle

        # Bouton de téléchargement finalisé
        nom_complet_fichier_c = preparer_nom_fichier("Les_cercles")
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_cercle,
            file_name=nom_complet_fichier_c.replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
            key="btn_dl_html_tab3",
        )


with tab4:
    st.header("Exploration des Surfaces Complexes")

    # ==========================================
    # SECTION 1 : THÉORIE DES SURFACES COMPLEXES
    # ==========================================
    st.subheader("1. Approches Méthodologiques")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **Principes de Calcul :**
        *   **Décomposition :** Découpage d'une surface irrégulière en plusieurs figures géométriques simples (triangles, rectangles, disques) dont les formules d'aire sont connues.
        *   **Soustraction :** Calcul d'une grande surface englobante à laquelle on soustrait les surfaces vides ou manquantes.
        *   **Approximation (Méthode des rectangles) :** Division d'une zone courbe en une multitude de petits rectangles pour estimer l'aire totale par sommation. Plus le nombre de rectangles est grand, plus la précision est élevée.
        """
        )

    with col2:
        st.write(
            "**Concepts clés (Cochez pour voir les définitions) :**"
        )

        voir_additivite = st.checkbox("Principe d'additivité")
        if voir_additivite:
            st.info(
                "**Additivité :** Si une surface est partagée en plusieurs morceaux disjoints, son aire totale est strictement égale à la somme des aires de chaque morceau."
            )

        voir_unites = st.checkbox("Unités de surface")
        if voir_unites:
            st.info(
                "**Unités :** L'unité légale est le mètre carré ($m^2$). Pour les terrains, on utilise le système agraire : l'are ($1 \\text{ a} = 100 \\text{ m}^2$) et l'hectare ($1 \\text{ ha} = 10\\,000 \\text{ m}^2$)."
            )

        voir_integration = st.checkbox("Approximation par encadrement")
        if voir_integration:
            st.info(
                "**Encadrement :** Consiste à définir une borne inférieure (rectangles sous la courbe) et une borne supérieure (rectangles dépassant la courbe) pour situer la valeur exacte de l'aire."
            )

    # ==========================================
    # SECTION 2 : SIMULATION D'APPROXIMATION D'AIRE
    # ==========================================
    st.markdown("---")
    st.subheader("2. Simulation d'approximation d'une surface courbe")
    st.write("Visualisez comment le découpage en rectangles permet d'estimer l'aire sous une courbe parabolique entre x = 0 et x = 4.")

    nb_rectangles = st.slider(
        "Nombre de rectangles de découpage :",
        min_value=4,
        max_value=50,
        value=10,
        step=1
    )

    # Paramètres de la fonction f(x) = -x^2 + 4x + 2
    x_debut, x_fin = 0.0, 4.0
    largeur_interv = (x_fin - x_debut) / nb_rectangles

    # Calcul de l'aire par la méthode des rectangles (somme à gauche)
    points_x = np.linspace(x_debut, x_fin - largeur_interv, nb_rectangles)
    valeurs_y = -(points_x**2) + 4 * points_x + 2
    aire_estimee = np.sum(valeurs_y * largeur_interv)

    # Valeur exacte par intégration mathématique : [-(x^3)/3 + 2x^2 + 2x] de 0 à 4 = 18.666...
    aire_exacte = 18.6667
    erreur_relative = abs(aire_estimee - aire_exacte) / aire_exacte * 100

    st.success("Calculs de simulation finalisés.")
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric(label="Aire estimée (rectangles)", value=f"{aire_estimee:.3f} u²")
    res_col2.metric(label="Aire exacte théorique", value=f"{aire_exacte:.3f} u²")
    res_col3.metric(label="Erreur d'approximation", value=f"{erreur_relative:.2f} %")

    # Génération graphique
    fig, ax = plt.subplots(figsize=(6, 4))
    x_courbe = np.linspace(x_debut, x_fin, 200)
    y_courbe = -(x_courbe**2) + 4 * x_courbe + 2
    ax.plot(x_courbe, y_courbe, color="#ff7f0e", linewidth=2.5, label="Frontière de la surface")

    # Tracé des rectangles
    for px, py in zip(points_x, valeurs_y):
        rect = plt.Rectangle((px, 0), largeur_interv, py, facecolor="#1f77b4", alpha=0.4, edgecolor="#1f77b4")
        ax.add_patch(rect)

    ax.set_xlim(-0.2, 4.2)
    ax.set_ylim(0, 7)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_title("Approximation d'une surface par discrétisation")
    st.pyplot(fig)

    # ==========================================
    # SECTION 3 : ÉVALUATION ET EXPORTATION
    # ==========================================
    st.write("---")
    if "complex_verrouille_tab4" not in st.session_state:
        st.session_state.complex_verrouille_tab4 = False
    verrou_at4 = st.session_state.complex_verrouille_tab4

    afficher_questions_complexes_dynamiques(verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation sur les surfaces complexes")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_complex = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 4.",
        key="check_certif_complex_final_net",
        disabled=verrou_at4,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4",
        key="btn_export_complex_official_net",
        use_container_width=True,
        disabled=verrou_at4,
    ):
        if (
            st.session_state.get("nom_var", "Nom") == "Nom"
            or st.session_state.get("prenom_var", "Prenom") == "Prenom"
        ):
            st.error(
                "Action refusee : Saisissez votre identite dans l'onglet 'Identification'."
            )
        elif not case_certif_complex:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Correction du Quiz
            score_q4 = 0.0
            if "ordre_quiz_tab4" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4:
                    reponse = st.session_state.get(
                        f"tab4_at4_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(reponse) == str(q_item["rep"]):
                        score_q4 += 1.0

            # Correction des Trous
            score_t4 = sum(
                [
                    st.session_state.get("tab4_t1_final") == "décomposition",
                    st.session_state.get("tab4_t2_final") == "soustraction",
                    st.session_state.get("tab4_t3_final") == "hectare",
                    st.session_state.get("tab4_t4_final") == "somme",
                    st.session_state.get("tab4_t5_final") == "erreur",
                    st.session_state.get("tab4_t6_final") == "triangles",
                    st.session_state.get("tab4_t7_final") == "approximation",
                    st.session_state.get("tab4_t8_final") == "agraires",
                    st.session_state.get("tab4_t9_final") == "supérieure",
                    st.session_state.get("tab4_t10_final") == "plane",
                ]
            )

            st.session_state.score_complex_p1 = round(float(score_q4), 1)
            st.session_state.score_complex_p2 = round(float(score_t4), 1)
            st.session_state.score_final_complex = round(
                float(score_q4 + score_t4), 1
            )
            st.session_state.complex_verrouille_tab4 = True
            st.rerun()

    # Génération du Document HTML Scellé
    if st.session_state.get("complex_verrouille_tab4", False):
        scr1 = st.session_state.get("score_complex_p1", 0.0)
        scr2 = st.session_state.get("score_complex_p2", 0.0)
        tot_s = st.session_state.get("score_final_complex", 0.0)

        from datetime import datetime, timedelta

        timestamp_complex = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d a %H:%M:%S"
        )

        st.success(
            f"ATELIER SURFACES COMPLEXES SCELLE | Note de session : {tot_s:.1f} / 20"
        )

        html_export_complex = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Surfaces Complexes - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #ff7f0e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Evaluation de Geometrie</h1>
                <p>Atelier 4 : Calcul et Evaluation de Surfaces Complexes</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_complex}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #ff7f0e;">
                Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4" in st.session_state:
            for num, q_item in enumerate(
                st.session_state.ordre_quiz_tab4, 1
            ):
                saisie = st.session_state.get(
                    f"tab4_at4_final_g_{q_item['id']}", "Choisir..."
                )
                attendu = q_item["rep"]
                v_lbl = (
                    "CORRECT"
                    if str(saisie).strip() == str(attendu).strip()
                    else "INCORRECT"
                )
                v_class = (
                    "status-correct"
                    if v_lbl == "CORRECT"
                    else "status-incorrect"
                )
                html_export_complex += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_complex += """
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
            ("1. Découper une forme en entités élémentaires est la décomposition", "tab4_t1_final", "décomposition"),
            ("2. L'aire d'une forme évidée s'obtient par une soustraction géométrique", "tab4_t2_final", "soustraction"),
            ("3. Un terrain de cent mètres sur cent mètres a une aire d'un hectare", "tab4_t3_final", "hectare"),
            ("4. L'additivité indique que l'aire totale est la somme des aires partielles", "tab4_t4_final", "somme"),
            ("5. Augmenter le nombre de rectangles réduit l'erreur d'estimation", "tab4_t5_final", "erreur"),
            ("6. Un polygone régulier peut se découper en triangles isocèles identiques", "tab4_t6_final", "triangles"),
            ("7. La surface délimitée par une courbe nécessite une méthode d'approximation", "tab4_t7_final", "approximation"),
            ("8. L'are est une unité de mesure adaptée aux surfaces agraires", "tab4_t8_final", "agraires"),
            ("9. Les rectangles qui dépassent la courbe forment une borne supérieure", "tab4_t9_final", "supérieure"),
            ("10. Mesurer une surface complexe revient à évaluer son extension plane", "tab4_t10_final", "plane"),
        ]

        for num, (enonce, cle, attendu) in enumerate(phrases_trous4, 1):
            saisie = st.session_state.get(cle, "Choisir...")
            v_lbl = (
                "CORRECT"
                if str(saisie).strip() == str(attendu).strip()
                else "INCORRECT"
            )
            v_class = (
                "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            )
            html_export_complex += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_complex += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.session_state.html_export_tab4 = html_export_complex

        # Bouton de téléchargement finalisé
        nom_complet_fichier_cx = preparer_nom_fichier("Surfaces_complexes")
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_complex,
            file_name=nom_complet_fichier_cx.replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
            key="btn_dl_html_tab4",
            )























