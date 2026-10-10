# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="TP les vecteur du plan ",
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
st.title("TP hydrostatique ")
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
    "La presse", 
    "Coordonnées et norme d'un vecteur", 
    "Vecteurs égaux, vecteur perpendiculaires, vecteur opposés et vecteur colinéaires",
    "Exemple  "
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]


def afficher_questions_proprietes_vectorielles(x_u, y_u, x_v, y_v, det, p_scalaire, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_vec3" not in st.session_state:
        # Diagnostics textuels
        colin = "Oui, ils sont colinéaires" if det == 0 else "Non, ils ne sont pas colinéaires"
        perp = "Oui, ils sont perpendiculaires" if p_scalaire == 0 else "Non, ils ne sont pas perpendiculaires"
        egaux = "Oui, ils sont égaux" if (x_u == x_v and y_u == y_v) else "Non, ils ne sont pas égaux"
        opp = "Oui, ils sont opposés" if (x_u == -x_v and y_u == -y_v) else "Non, ils ne sont pas opposés"

        base_quiz_vec3 = [
            {"id": "v3_1", "q": "Quelle formule analytique permet de calculer le déterminant de deux vecteurs u(x;y) et v(x';y') ?", "options": ["x*y' - y*x'", "x*x' + y*y'", "x*y' + y*x'"], "rep": "x*y' - y*x'"},
            {"id": "v3_2", "q": "Quelle formule analytique definit le produit scalaire de deux vecteurs u(x;y) et v(x';y') ?", "options": ["x*x' + y*y'", "x*y' - y*x'", "x*x' - y*y'"], "rep": "x*x' + y*y'"},
            {"id": "v3_3", "q": "Lorsque le déterminant de deux vecteurs est strictement égal à 0, on en déduit qu'ils sont :", "options": ["Colinéaires", "Perpendiculaires", "Égaux"], "rep": "Colinéaires"},
            {"id": "v3_4", "q": "Lorsque le produit scalaire de deux vecteurs est strictement égal à 0, on en déduit qu'ils sont :", "options": ["Perpendiculaires (orthogonaux)", "Colinéaires", "Opposés"], "rep": "Perpendiculaires (orthogonaux)"},
            {"id": "v3_5", "q": "D'après vos curseurs actuels, le déterminant calculé vaut-il 0 (colinéarité) ?", "options": ["Oui, ils sont colinéaires", "Non, ils ne sont pas colinéaires"], "rep": colin},
            {"id": "v3_6", "q": "D'après vos curseurs actuels, le produit scalaire calculé vaut-il 0 (orthogonalité) ?", "options": ["Oui, ils sont perpendiculaires", "Non, ils ne sont pas perpendiculaires"], "rep": perp},
            {"id": "v3_7", "q": "D'après vos réglages de session, les vecteurs u et v sont-ils strictement égaux ?", "options": ["Oui, ils sont égaux", "Non, ils ne sont pas égaux"], "rep": egaux},
            {"id": "v3_8", "q": "D'après vos réglages de session, les vecteurs u et v sont-ils strictement opposés ?", "options": ["Oui, ils sont opposés", "Non, ils ne sont pas opposés"], "rep": opp},
            {"id": "v3_9", "q": "Si deux vecteurs non nuls sont colinéaires, géométriquement leurs droites supports sont :", "options": ["Parallèles ou confondues", "Sécantes et perpendiculaires", "Obliques sans lien"], "rep": "Parallèles ou confondues"},
            {"id": "v3_10", "q": "Si le vecteur v est égal à -u, alors la somme vectorielle u + v donne :", "options": ["Le vecteur nul", "Le double du vecteur u", "Un vecteur unitaire"], "rep": "Le vecteur nul"}
        ]
        copie_base = list(base_quiz_vec3)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_vec3 = copie_base

    col_q3, col_t3 = st.columns(2)

    with col_q3:
        st.markdown("##### Quiz sur les relations vectorielles (10 questions - 10 pts)")
        dict_rep_q3 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_vec3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vec_t3_q_{q_data['id']}"
            cle_opts = f"opts_vec3_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q3[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t3:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_3 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Deux vecteurs ayant les mêmes composantes x=x' et y=y' sont dits")
        with c2: dict_trous_3["t1"] = st.selectbox("", ["Choisir...", "Egaux", "Opposes", "Colineaires"], key="vec_t3_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Si x = -x' et y = -y', les deux vecteurs sont qualifiés d'")
        with c4: dict_trous_3["t2"] = st.selectbox("", ["Choisir...", "Opposes", "Egaux", "Orthogonaux"], key="vec_t3_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La colinéarité analytique de deux directions se vérifie par le calcul du")
        with c6: dict_trous_3["t3"] = st.selectbox("", ["Choisir...", "Determinant", "Produit_scalaire", "Somme"], key="vec_t3_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. L'orthogonalité (perpendicularité) de deux vecteurs se vérifie par le produit")
        with c8: dict_trous_3["t4"] = st.selectbox("", ["Choisir...", "Scalaire", "Vectoriel", "Nul"], key="vec_t3_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le calcul du déterminant croisé répond à l'opération de soustraction x*y' -")
        with c10: dict_trous_3["t5"] = st.selectbox("", ["Choisir...", "y*x'", "x*x'", "y*y'"], key="vec_t3_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le produit scalaire s'établit par l'addition x*x' +")
        with c12: dict_trous_3["t6"] = st.selectbox("", ["Choisir...", "y*y'", "y*x'", "x*y'"], key="vec_t3_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Si le produit scalaire est nul, l'angle géométrique formé entre eux vaut")
        with c14: dict_trous_3["t7"] = st.selectbox("", ["Choisir...", "90_degres", "0_degre", "180_degres"], key="vec_t3_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Des vecteurs colinéaires modélisent géométriquement des lignes de fuite")
        with c16: dict_trous_3["t8"] = st.selectbox("", ["Choisir...", "Paralleles", "Secantes", "Confondues"], key="vec_t3_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le mot orthogonalité est un synonyme mathématique rigoureux de")
        with r18: dict_trous_3["t9"] = st.selectbox("", ["Choisir...", "Perpendicularite", "Egalite", "Alignement"], key="vec_t3_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Le déterminant de deux vecteurs colinéaires est mathématiquement égal à")
        with c20: dict_trous_3["t10"] = st.selectbox("", ["Choisir...", "0", "1", "-1"], key="vec_t3_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q3, dict_trous_3

def afficher_questions_coordonnees_norme(x_u, y_u, norme_u, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_vec2" not in st.session_state:
        base_quiz_vec2 = [
            {"id": "v2_1", "q": "Quelle est la formule générale de la norme d'un vecteur u(x;y) dans un repère orthonormé ?", "options": ["sqrt(x² + y²)", "x² + y²", "sqrt(x² - y²)"], "rep": "sqrt(x² + y²)"},
            {"id": "v2_2", "q": "Quelle est la valeur exacte de la composante horizontale x de votre vecteur actuel ?", "options": [f"{x_u:.1f}", f"{-x_u:.1f}", f"{y_u:.1f}"], "rep": f"{x_u:.1f}"},
            {"id": "v2_3", "q": "Quelle est la valeur exacte de la composante verticale y de votre vecteur actuel ?", "options": [f"{y_u:.1f}", f"{-y_u:.1f}", f"{x_u:.1f}"], "rep": f"{y_u:.1f}"},
            {"id": "v2_4", "q": "Quelle est la valeur numérique arrondie de la norme ||u|| calculée pour vos curseurs ?", "options": [f"{norme_u:.2f}", f"{norme_u+1:.2f}", f"{abs(x_u):.2f}"], "rep": f"{norme_u:.2f}"},
            {"id": "v2_5", "q": "Si un vecteur possède des coordonnées u(-3;4), quelle est la valeur exacte de sa norme ?", "options": ["5", "25", "7"], "rep": "5"},
            {"id": "v2_6", "q": "Que se passe-t-il pour la norme d'un vecteur si on multiplie toutes ses composantes par -1 ?", "options": ["La norme reste inchangée", "La norme devient négative", "La norme est doublée"], "rep": "La norme reste inchangée"},
            {"id": "v2_7", "q": "Si la norme d'un vecteur est égale à 1, on dit que ce vecteur est :", "options": ["Unitaire", "Nul", "Orthogonal"], "rep": "Unitaire"},
            {"id": "v2_8", "q": "Le calcul de la distance entre deux points s'appuie sur quel théorème de géométrie ?", "options": ["Théorème de Pythagore", "Théorème de Thalès", "Théorème de Al-Kashi"], "rep": "Théorème de Pythagore"},
            {"id": "v2_9", "q": "Une norme vectorielle peut-elle être une valeur numérique strictement négative ?", "options": ["Non, une norme est toujours positive ou nulle", "Oui, si les composantes sont négatives", "Oui, dans un repère non orthonormé"], "rep": "Non, une norme est toujours positive ou nulle"},
            {"id": "v2_10", "q": "Si le vecteur u a pour coordonnées (0; -6), quelle est la valeur numérique de sa norme ||u|| ?", "options": ["6", "-6", "36"], "rep": "6"}
        ]
        copie_base = list(base_quiz_vec2)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_vec2 = copie_base

    col_q2, col_t2 = st.columns(2)

    with col_q2:
        st.markdown("##### Quiz sur les coordonnées et la norme (10 questions - 10 pts)")
        dict_rep_q2 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_vec2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vec_t2_q_{q_data['id']}"
            cle_opts = f"opts_vec2_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q2[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t2:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_2 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Dans un repère, le premier nombre d'un couple de coordonnées s'appelle l'")
        with c2: dict_trous_2["t1"] = st.selectbox("", ["Choisir...", "Abscisse", "Ordonnee", "Norme"], key="vec_t2_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le second nombre d'un couple de coordonnées d'un vecteur s'appelle l'")
        with c4: dict_trous_2["t2"] = st.selectbox("", ["Choisir...", "Ordonnee", "Abscisse", "Direction"], key="vec_t2_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour pouvoir utiliser la formule sqrt(x²+y²), le repère doit impérativement être")
        with c6: dict_trous_2["t3"] = st.selectbox("", ["Choisir...", "Orthonorme", "Quelconque", "Oblique"], key="vec_t2_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La notation mathématique de la norme utilise une double")
        with c8: dict_trous_2["t4"] = st.selectbox("", ["Choisir...", "Barre", "Parenthese", "Fleche"], key="vec_t2_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La valeur d'une norme géométrique correspond physiquement à une")
        with c10: dict_trous_2["t5"] = st.selectbox("", ["Choisir...", "Longueur", "Pente", "Orientation"], key="vec_t2_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Dans la formule, les coordonnées x et y sont élevées au")
        with c12: dict_trous_2["t6"] = st.selectbox("", ["Choisir...", "Carre", "Cube", "Double"], key="vec_t2_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La somme des carrés est placée sous une racine")
        with c14: dict_trous_2["t7"] = st.selectbox("", ["Choisir...", "Carree", "Cubique", "Absolue"], key="vec_t2_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le seul vecteur dont la norme est mathématiquement égale à 0 est le vecteur")
        with c16: dict_trous_2["t8"] = st.selectbox("", ["Choisir...", "Nul", "Unitaire", "Egal"], key="vec_t2_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La norme d'un vecteur u est notée algébriquement")
        with r18: dict_trous_2["t9"] = st.selectbox("", ["Choisir...", "||u||", "[u]", "f(u)"], key="vec_t2_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Si les composantes x et y doublent, la norme du vecteur sera multipliée par")
        with c20: dict_trous_2["t10"] = st.selectbox("", ["Choisir...", "2", "4", "1"], key="vec_t2_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q2, dict_trous_2


def afficher_questions_definition_vecteur(xA, yA, xB, yB, vec_x, vec_y, norme_AB, verrouille=False):
    import streamlit as st
    import random
    import numpy as np
    
    if "ordre_quiz_vec1" not in st.session_state:
        base_quiz_vec1 = [
            {"id": "v1_1", "q": "Quels sont les trois éléments qui définissent caractérisquement un vecteur du plan ?", "options": ["Direction, sens et norme", "Longueur, inclinaison et origine", "Coordonnées, droite et milieu"], "rep": "Direction, sens et norme"},
            {"id": "v1_2", "q": "Quelle est la valeur exacte actuelle de la composante horizontale (x_B - x_A) de votre vecteur ?", "options": [f"{vec_x:.1f}", f"{-vec_x:.1f}", f"{vec_y:.1f}"], "rep": f"{vec_x:.1f}"},
            {"id": "v1_3", "q": "Quelle est la valeur exacte actuelle de la composante verticale (y_B - y_A) de votre vecteur ?", "options": [f"{vec_y:.1f}", f"{-vec_y:.1f}", f"{vec_x:.1f}"], "rep": f"{vec_y:.1f}"},
            {"id": "v1_4", "q": "Si le point de départ A et le point d'arrivée B sont confondus (xA=xB et yA=yB), on obtient :", "options": ["Le vecteur nul", "Un vecteur de norme 1", "Une droite infinie"], "rep": "Le vecteur nul"},
            {"id": "v1_5", "q": "Géométriquement, que représente précisément la norme d'un vecteur AB ?", "options": ["La distance entre le point A et le point B", "L'inclinaison de la droite par rapport à l'axe X", "Le coefficient multiplicateur du déplacement"], "rep": "La distance entre le point A et le point B"},
            {"id": "v1_6", "q": "Quelle est la valeur arrondie à deux décimales de la norme actuelle de votre vecteur ?", "options": [f"{norme_AB:.2f}", f"{norme_AB+2:.2f}", f"{abs(vec_x):.2f}"], "rep": f"{norme_AB:.2f}"},
            {"id": "v1_7", "q": "Si on change les deux points pour obtenir un vecteur opposé, quelle sera sa composante horizontale ?", "options": [f"{-vec_x:.1f}", f"{vec_x:.1f}", f"{vec_y:.1f}"], "rep": f"{-vec_x:.1f}"},
            {"id": "v1_8", "q": "Dans la notation du vecteur AB, quel point désigne l'origine du déplacement ?", "options": ["Le point A", "Le point B", "L'origine du repère O"], "rep": "Le point A"},
            {"id": "v1_9", "q": "Dans la notation du vecteur AB, quel point désigne l'extrémité du déplacement ?", "options": ["Le point B", "Le point A", "Le point de coordonnées (0,0)"], "rep": "Le point B"},
            {"id": "v1_10", "q": "Si le vecteur possède une composante x positive et une composante y positive, le déplacement se fait :", "options": ["Vers la droite et vers le haut", "Vers la gauche et vers le bas", "Vers la droite et vers le bas"], "rep": "Vers la droite et vers le haut"}
        ]
        copie_base = list(base_quiz_vec1)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_vec1 = copie_base

    col_q1, col_t1 = st.columns(2)

    with col_q1:
        st.markdown("##### Quiz sur les définitions vectorielles (10 questions - 10 pts)")
        dict_rep_q1 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_vec1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vec_t1_q_{q_data['id']}"
            cle_opts = f"opts_vec1_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q1[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t1:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_1 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le déplacement rectiligne reliant l'origine A à l'extrémité B s'appelle un")
        with c2: dict_trous_1["t1"] = st.selectbox("", ["Choisir...", "Vecteur", "Segment", "Axe"], key="vec_t1_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour calculer la composante x, on effectue la soustraction x_B -")
        with c4: dict_trous_1["t2"] = st.selectbox("", ["Choisir...", "x_A", "y_A", "y_B"], key="vec_t1_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La longueur mathématique d'un vecteur se désigne sous le terme de")
        with c6: dict_trous_1["t3"] = st.selectbox("", ["Choisir...", "Norme", "Direction", "Sens"], key="vec_t1_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La droite contenant le déplacement détermine ce que l'on appelle sa")
        with c8: dict_trous_1["t4"] = st.selectbox("", ["Choisir...", "Direction", "Norme", "Extremite"], key="vec_t1_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La flèche qui indique vers quel point on se dirige définit le")
        with c10: dict_trous_1["t5"] = st.selectbox("", ["Choisir...", "Sens", "Origine", "Rapport"], key="vec_t1_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Pour calculer la composante verticale d'un vecteur, on effectue la différence y_B -")
        with c12: dict_trous_1["t6"] = st.selectbox("", ["Choisir...", "y_A", "x_A", "x_B"], key="vec_t1_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La formule de calcul de la norme d'un vecteur s'appuie sur le théorème géométrique de")
        with c14: dict_trous_1["t7"] = st.selectbox("", ["Choisir...", "Pythagore", "Thales", "Chasles"], key="vec_t1_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Un vecteur dont la norme est égale à zéro est appelé un vecteur")
        with c16: dict_trous_1["t8"] = st.selectbox("", ["Choisir...", "Nul", "Unitaire", "Fixe"], key="vec_t1_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Les deux valeurs numériques ordonnées décrivant le déplacement forment les")
        with r18: dict_trous_1["t9"] = st.selectbox("", ["Choisir...", "Coordonnees", "Longueurs", "Equations"], key="vec_t1_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Deux vecteurs ayant la même direction, la même norme mais un sens opposé sont dits")
        with c20: dict_trous_1["t10"] = st.selectbox("", ["Choisir...", "Opposes", "Egaux", "Colineaires"], key="vec_t1_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q1, dict_trous_1


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



def afficher_questions_hydrostatique(section_d1, section_d2, f2_reelle_presse, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_hydro1" not in st.session_state:
        # 1. Catalogue general contenant 15 QCM et 15 textes a trous dynamiques
        catalogue_qcm = [
            {"id": "h1", "q": "Quelle loi enonce qu'une variation de pression subie par un liquide se transmet integralement :", "options": ["Pascal", "Bernoulli", "Archimede"], "rep": "Pascal"},
            {"id": "h2", "q": "Calculez la surface du petit piston D1 en centimetres carres (arrondie au dixieme) :", "options": [f"{section_d1 * 10000.0:.1f}", f"{section_d1 * 100.0:.1f}", f"{section_d1 * 1000.0:.1f}"], "rep": f"{section_d1 * 10000.0:.1f}"},
            {"id": "h3", "q": "Calculez la surface du gros piston D2 en centimetres carres (arrondie au dixieme) :", "options": [f"{section_d2 * 10000.0:.1f}", f"{section_d2 * 100.0:.1f}", f"{section_d2 * 1000.0:.1f}"], "rep": f"{section_d2 * 10000.0:.1f}"},
            {"id": "h4", "q": "Indiquez la valeur numerique du rapport multiplicateur de force (D2/D1 au carre) :", "options": [f"{section_d2 / section_d1:.1f}", f"{section_d2 / section_d1:.0f}", f"{section_d1 / section_d2:.1f}"], "rep": f"{section_d2 / section_d1:.1f}"},
            {"id": "h5", "q": "Une presse hydraulique permet-elle d'accroitre l'effort mecanique developpe en sortie ? :", "options": ["Oui", "Non"], "rep": "Oui"},
            {"id": "h6", "q": "Comment se nomme la science qui etudie les fluides incompressibles au repos :", "options": ["Hydrostatique", "Hydrodynamique", "Aerodynamique"], "rep": "Hydrostatique"},
            {"id": "h7", "q": "Quel est l'effet de l'augmentation du diametre D2 sur le rapport de force :", "options": ["Augmenter", "Diminuer", "Stagner"], "rep": "Augmenter"},
            {"id": "h8", "q": "Calculez la force reelle theorique developpee en sortie F2 (Newtons, a l'unite) :", "options": [f"{f2_reelle_presse:.0f}", f"{f2_reelle_presse * 10:.0f}", f"{f2_reelle_presse / 10:.0f}"], "rep": f"{f2_reelle_presse:.0f}"},
            {"id": "h9", "q": "Quel element central d'une installation hydraulique genere le debit du fluide :", "options": ["Pompe", "Verin", "Distributeur"], "rep": "Pompe"},
            {"id": "h10", "q": "La relation fondamentale des forces et surfaces s'ecrit F1/S1 = F2/ (nom de variable) :", "options": ["S2", "S1", "P1"], "rep": "S2"},
            {"id": "h11", "q": "Si D1 double sans modifier D2, le rapport multiplicateur est-il divise par quatre ? :", "options": ["Oui", "Non"], "rep": "Oui"},
            {"id": "h12", "q": "Les frottements du liquide visqueux sont-ils pris en compte en hydrostatique brute ? :", "options": ["Non", "Oui"], "rep": "Non"},
            {"id": "h13", "q": "Quelle force developpe l'action de la gravite terrestre sur une masse active :", "options": ["Poids", "Masse", "Pression"], "rep": "Poids"},
            {"id": "h14", "q": "Quelle valeur de la pesanteur g a ete utilisee pour le calcul du poids (a deux decimales) :", "options": ["9.81", "9.80", "10.0"], "rep": "9.81"},
            {"id": "h15", "q": "La pression transmise depend-elle de la geometrie ou de la courbure du tube en U ? :", "options": ["Non", "Oui"], "rep": "Non"}
        ]
        
        catalogue_trous = [
            {"id": "t1", "q": "1. La pression au sein d'un fluide au repos est partout la meme dans toutes les", "options": ["Directions", "Surfaces", "Hauteurs"], "rep": "Directions"},
            {"id": "t2", "q": "2. L'unite de mesure internationale de la pression est le", "options": ["Pascal", "Bar", "Newton"], "rep": "Pascal"},
            {"id": "t3", "q": "3. Les liquides de transmission industrielle sont consideres en hydrostatique comme", "options": ["Incompressibles", "Compressibles", "Visqueux"], "rep": "Incompressibles"},
            {"id": "t4", "q": "4. Une pression nominale equivalente a 1 bar correspond exactement a cent-mille", "options": ["Pascals", "Bars", "Newtons"], "rep": "Pascals"},
            {"id": "t5", "q": "5. Le rapport de deplacement des pistons est inversement proportionnel au rapport de leurs", "options": ["Surfaces", "Diametres", "Rayons"], "rep": "Surfaces"},
            {"id": "t6", "q": "6. Selon le principe de Pascal, la pression se transmet avec la meme", "options": ["Intensite", "Vitesse", "Force"], "rep": "Intensite"},
            {"id": "t7", "q": "7. La force exercee par un fluide sur une paroi est toujours perpendiculaire a cette", "options": ["Surface", "Ligne", "Direction"], "rep": "Surface"},
            {"id": "t8", "q": "8. Un fluide incompressible maintient un volume rigoureusement", "options": ["Constant", "Variable", "Nul"], "rep": "Constant"},
            {"id": "t9", "q": "9. L'appareil technique de metrologie utilise pour relever la pression se nomme un", "options": ["Manometre", "Thermomitre", "Multimetre"], "rep": "Manometre"},
            {"id": "t10", "q": "10. L'huile hydraulique est utilisee pour sa lubrification et sa faible", "options": ["Compressibilite", "Viscosite", "Densite"], "rep": "Compressibilite"},
            {"id": "t11", "q": "11. L'energie fluide convertit la pression en un travail", "options": ["Mecanique", "Thermique", "Electrique"], "rep": "Mecanique"},
            {"id": "t12", "q": "12. La difference de niveau de fluide entre deux colonnes engendre une pression dite", "options": ["Hydrostatique", "Hydrodynamique", "Atmospherique"], "rep": "Hydrostatique"},
            {"id": "t13", "q": "13. Un liquide change de forme facilement mais oppose une grande resistance au changement de", "options": ["Volume", "Masse", "Surface"], "rep": "Volume"},
            {"id": "t14", "q": "14. Dans les systemes industriels fermes, le fluide retourne directement vers le", "options": ["Reservoir", "Verin", "Moteur"], "rep": "Reservoir"},
            {"id": "t15", "q": "15. Le piston recevant l'effort initial mecanique de consigne est appele piston d'", "options": ["Entree", "Sortie", "Plateau"], "rep": "Entree"}
        ]
        
        copie_qcm = list(catalogue_qcm)
        copie_trous = list(catalogue_trous)
        random.shuffle(copie_qcm)
        random.shuffle(copie_trous)
        
        st.session_state.ordre_qcm_hydro1 = copie_qcm[:5]
        st.session_state.ordre_trous_hydro1 = copie_trous[:5]

    col_q1, col_t1 = st.columns(2)

    with col_q1:
        st.markdown("##### Quiz sur l'analyse technologique (5 questions - 10 pts)")
        dict_rep_q1 = {}
        for idx, q_data in enumerate(st.session_state.ordre_qcm_hydro1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_t1_q_{q_data['id']}"
            cle_opts = f"opts_hydro1_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q1[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t1:
        st.markdown("##### Synthese de cours a trous (5 trous - 10 pts)")
        dict_trous_1 = {}
        for idx, q_data in enumerate(st.session_state.ordre_trous_hydro1, 1):
            c_text, col_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_text: 
                st.write(f"{idx}. {q_data['q'].split('...', 1)[0].strip()}")
            cle_select_t = f"hydro_t1_t_{q_data['id']}"
            cle_opts_t = f"opts_trous1_{q_data['id']}"
            if cle_opts_t not in st.session_state:
                opts_t = list(q_data["options"])
                random.shuffle(opts_t)
                st.session_state[cle_opts_t] = ["Choisir..."] + opts_t
            val_p_t = st.session_state.get(cle_select_t, "Choisir...")
            sel_idx_t = st.session_state[cle_opts_t].index(val_p_t) if val_p_t in st.session_state[cle_opts_t] else 0
            with col_sel:
                dict_trous_1[q_data["id"]] = st.selectbox("", st.session_state[cle_opts_t], index=sel_idx_t, key=cle_select_t, disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q1, dict_trous_1


with tab1:
    st.header("Etude de la presse hydraulique et du pont elevateur")
    st.write("Modelisation mecanique et exploitation hydrostatique d'apres le principe de Pascal.")

    # =====================================================================
    # --- INITIALISATION STABLE DE LA SESSION DE TRAVAIL ---
    # =====================================================================
    if "session_initialisee_tab1" not in st.session_state:
        st.session_state.session_initialisee_tab1 = True
        st.session_state.eval_f1 = float(random.randint(90, 150)) if 'random' in locals() else 120.0
        st.session_state.eval_p_pompe = float(random.randint(35, 65)) if 'random' in locals() else 45.0
        
        # Tirage au sort initial et fixe des indices pour les 10 questions (5 QCM et 5 Trous parmi 15)
        st.session_state.indices_qcm_choisis = random.sample(range(15), 5) if 'random' in locals() else list(range(5))
        st.session_state.indices_trous_choisis = random.sample(range(15), 5) if 'random' in locals() else list(range(5))

    catalogue_charges_tab1 = {
        "Citadine compacte (1200 kg)": 1200.0,
        "Berline familiale (1800 kg)": 1800.0,
        "SUV / Utilitaire (2500 kg)": 2500.0,
        "Minipelle de chantier (3500 kg)": 3500.0,
        "Tractopelle agricole (8000 kg)": 8000.0,
        "Camion toupie à béton (15000 kg)": 15000.0
    }

    # =====================================================================
    # --- LAYOUT DOUBLE COLONNE PRINCIPALE ---
    # =====================================================================
    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.subheader("Parametres de la presse")
        
        mode_selectionne = st.radio(
            "Mode de fonctionnement :",
            ["Mode Normal (Libre)", "Mode Evaluation (Aleatoire)"],
            key="radio_mode_tab1"
        )
        
        st.markdown("---")
        
        if "Normal" in mode_selectionne:
            var_f1 = st.slider("Force d'entree F1 (N) :", min_value=0, max_value=5000, value=100, step=10, key="slide_f1_tab1")
            engin_selectionne = st.selectbox("Choisir l'engin a soulever :", list(catalogue_charges_tab1.keys()), key="select_engin_tab1")
            
            masse_engin = catalogue_charges_tab1[engin_selectionne]
            var_f2_theorique = masse_engin * 9.81
            st.metric(label="Force de sortie requise F2 (N)", value=f"{var_f2_theorique:.1f}")
            
            scale_d1 = st.slider("Diametre petit piston D1 (cm) :", min_value=2.0, max_value=10.0, value=4.0, step=0.5, key="slide_d1_tab1")
            scale_d2 = st.slider("Diametre gros piston D2 (cm) :", min_value=10.0, max_value=50.0, value=20.0, step=1.0, key="slide_d2_tab1")
            
            st.markdown("---")
            st.subheader("Parametres pont elevateur")
            scale_p_pompe = st.slider("Pression de la pompe en bar :", min_value=5, max_value=150, value=40, step=5, key="slide_p_tab1")
            scale_d_verin = st.slider("Diametre du piston du plateau (cm) :", min_value=10, max_value=50, value=25, step=1, key="slide_dv_tab1")
            
            section_d1 = np.pi * (scale_d1 / 100.0 / 2.0)**2
            section_d2 = np.pi * (scale_d2 / 100.0 / 2.0)**2
            rapport_sections = section_d2 / section_d1
            f2_reelle_presse = var_f1 * rapport_sections
            
            section_verin_plateau = np.pi * (scale_d_verin / 100.0 / 2.0)**2
            pression_pompe_pa = scale_p_pompe * 100000.0
            force_max_verin = pression_pompe_pa * section_verin_plateau
            pression_suffisante = force_max_verin >= var_f2_theorique
            
        else:
            st.info("Champs de mesures imposes pour l'examen. Calculez analytiquement les indicateurs fluides manquants.")
            scale_d1 = 4.0
            scale_d2 = 20.0
            scale_d_verin = 25.0
            var_f1 = st.session_state.eval_f1
            scale_p_pompe = st.session_state.eval_p_pompe
            
            section_d1 = np.pi * (scale_d1 / 100.0 / 2.0)**2
            section_d2 = np.pi * (scale_d2 / 100.0 / 2.0)**2
            f2_reelle_presse = var_f1 * (section_d2 / section_d1)
            
            st.markdown(f"* **Diametre du petit piston D1 :** {scale_d1} cm")
            st.markdown(f"* **Diametre du gros piston D2 :** {scale_d2} cm")
            st.markdown(f"* **Force de consigne appliquee en entree F1 :** {var_f1:.0f} N")
            st.markdown(f"* **Pression cible de la pompe d'alimentation :** {scale_p_pompe:.0f} bar")
            st.markdown(f"* **Diametre nominal du piston du plateau :** {scale_d_verin} cm")

    with col_droite:
        st.subheader("Visualisation Graphique et Metrologie")
        
        # RECTIFICATION CRITIQUE : Nettoyage absolu de la memoire cache Matplotlib pour forcer le rafraichissement
        plt.close('all')
        
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            st.markdown("**1. Modele Physique Theorique**")
            fig1, ax1 = plt.subplots(figsize=(4, 4), dpi=100)
            ax1.clear()
            
            # Trait fixe de la structure en U
            ax1.plot([-2, -2, 2, 2], [5, -2, -2, 5], color="black", linewidth=2)
            ax1.plot([-1, -1, 1, 1], [5, -1, -1, 5], color="black", linewidth=2)
            
            # Calcul dynamique de la hauteur du fluide liee a l'effort F1 applique
            hauteur_fluide_gauche = 1.5 - (var_f1 / 2500.0)
            hauteur_fluide_droite = 1.5 + (f2_reelle_presse / 40000.0)
            
            # Remplissage dynamique du fluide hydraulique
            ax1.fill_between([-2, 2], [-2, -2], [-1, -1], color="#38bdf8", alpha=0.6)
            ax1.fill_between([-2, -1], [-1, -1], [hauteur_fluide_gauche, hauteur_fluide_gauche], color="#38bdf8", alpha=0.6)
            ax1.fill_between([1, 2], [-1, -1], [hauteur_fluide_droite, hauteur_fluide_droite], color="#38bdf8", alpha=0.6)
            
            # Fleches vectorielles dynamiques
            ax1.arrow(-1.5, hauteur_fluide_gauche + 1.5, 0, -1.0, head_width=0.2, head_length=0.3, fc="red", ec="red", linewidth=1.5)
            ax1.text(-1.5, hauteur_fluide_gauche + 1.8, f"F1: {var_f1:.0f}N", color="red", ha="center", fontsize=8, fontweight="bold")
            
            ax1.arrow(1.5, hauteur_fluide_droite, 0, 1.0, head_width=0.2, head_length=0.3, fc="green", ec="green", linewidth=1.5)
            ax1.text(1.5, hauteur_fluide_droite + 1.3, f"F2: {f2_reelle_presse:.0f}N", color="green", ha="center", fontsize=8, fontweight="bold")
            
            ax1.set_xlim(-3, 3)
            ax1.set_ylim(-3, 6)
            ax1.axis("off")
            st.pyplot(fig1)
            plt.close(fig1)
            
    with sub_col2:
        st.markdown("**2. Application Industrielle : Pont Elevateur**")
        if "Normal" in mode_selectionne:
            if pression_suffisante: 
                st.success("Pression suffisante : Pret pour le levage")
            else: 
                st.error("Pression insuffisante : Levage impossible")
        
        fig2, ax2 = plt.subplots(figsize=(4, 4), dpi=100)
        ax2.clear()
        
        # Base et colonnes de guidage
        ax2.plot([-3, 3], [0, 0], color="black", linewidth=3)
        ax2.plot([-1.5, -1.5], [0, 4], color="#64748b", linewidth=4)
        ax2.plot([1.5, 1.5], [0, 4], color="#64748b", linewidth=4)
        
        # Calcul de la hauteur de montee du plateau selon l'intensite de la force de sortie realisable
        hauteur_plateau = 0.4
        if "Normal" in mode_selectionne and pression_suffisante:
            hauteur_plateau = 0.4 + (f2_reelle_presse / var_f2_theorique) * 2.0
            if hauteur_plateau > 3.2: 
                hauteur_plateau = 3.2
        
        # Rendu dynamique du plateau mobile et de la charge
        ax2.plot([-2, 2], [hauteur_plateau, hauteur_plateau], color="#1e293b", linewidth=5)
        ax2.fill_between([-1.2, 1.2], [hauteur_plateau, hauteur_plateau], [hauteur_plateau + 0.8, hauteur_plateau + 0.8], color="#ef4444", alpha=0.8)
        ax2.text(0, hauteur_plateau + 0.3, "VEHICULE", color="white", ha="center", fontsize=8, fontweight="bold")
        
        ax2.set_xlim(-4, 4)
        ax2.set_ylim(-1, 5)
        ax2.axis("off")
        st.pyplot(fig2)
        plt.close(fig2)


    st.markdown("---")
    res_q1, res_t1 = afficher_questions_hydrostatique(section_d1, section_d2, f2_reelle_presse)

    # =====================================================================
    # --- EVALUATION SECURISEE ET EXPORTATION HTML ---
    # =====================================================================
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # Gestion locale du verrou technique de l'Atelier 1
    verrou_h1 = st.session_state.get("v_verrouille_tab1", False)

    case_certif_h1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_hydro1_official", 
        disabled=verrou_h1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_hydro1_official", use_container_width=True, disabled=verrou_h1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_h1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz QCM (10 points)
            score_q1 = 0.0
            if "ordre_qcm_hydro1" in st.session_state:
                for q_item in st.session_state.ordre_qcm_hydro1:
                    reponse_eleve = st.session_state.get(f"hydro_t1_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction de la Synthèse à trous (10 points)
            score_t1 = 0.0
            if "ordre_trous_hydro1" in st.session_state:
                for t_item in st.session_state.ordre_trous_hydro1:
                    reponse_trous = st.session_state.get(f"hydro_t1_t_{t_item['id']}", "Choisir...")
                    if str(reponse_trous).strip() == str(t_item["rep"]).strip():
                        score_trous += 1.0

            st.session_state.score_v1_p1 = round(float(score_q1 * 2.0), 1)
            st.session_state.score_v1_p2 = round(float(score_t1 * 2.0), 1)
            st.session_state.score_final_v1 = round(float((score_q1 + score_t1) * 2.0), 1)
            st.session_state.v_verrouille_tab1 = True
            st.rerun()
            
    if st.session_state.get("v_verrouille_tab1", False):
        scr1 = st.session_state.get("score_v1_p1", 0.0)
        scr2 = st.session_state.get("score_v1_p2", 0.0)
        tot_s = st.session_state.get("score_final_v1", 0.0)

        from datetime import datetime
        timestamp_v1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER HYDROSTATIQUE SCELLED | Note de session : {tot_s:.1f} / 20")

        # Confection de l'export HTML autonome (Style Bleu Académique)
        html_export_v1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Hydrostatique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #ffffff; color: #1e293b; }}
                .header-blue {{ background-color: #2563eb; color: white; padding: 24px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-box {{ position: absolute; top: 24px; right: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; font-size: 24px; font-weight: bold; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; }}
                th {{ background-color: #475569; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                tr:nth-child(even) td {{ background-color: #f8fafc; }}
                .status-pass {{ background-color: #dcfce7; color: #16a34a; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
                .status-fail {{ background-color: #fee2e2; color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header-blue">
                <h2 style="margin: 0; padding-bottom: 8px;">Professeur Laurent GALLET</h2>
                <p style="margin: 0; padding-bottom: 4px;">Atelier 1 : Etude de la presse hydraulique, loi de Pascal et levage mécanique</p>
                <p style="margin: 0; padding-bottom: 4px;">Configuration de session : S1 = {section_d1*10000.0:.1f} cm² | S2 = {section_d2*10000.0:.1f} cm² &rarr; F1 = {var_f1:.0f} N | F2 theorique = {f2_reelle_presse:.0f} N</p>
                <p style="margin: 0;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 11px; opacity: 0.8; margin-top: 8px;">Scelle le : {timestamp_v1}</p>
                <div class="score-box">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="section-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 0 0 25px 0;">
                - Note obtenue au Questionnaire Technologique : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours a trous : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="section-title">1. Correction detaillee du Questionnaire QCM (Ordre d'affichage de session)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th style="text-align: center;">Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_qcm_hydro1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_qcm_hydro1, 1):
                saisie = st.session_state.get(f"hydro_t1_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-pass" if v_lbl == "CORRECT" else "status-fail"
                html_export_v1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{v_class}'>{v_lbl}</span></td></tr>"

        html_export_v1 += """
                </tbody>
            </table>

            <div class="section-title">2. Correction detaillee des Trous de Synthese (Ordre d'affichage de session)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours a Completer</th><th>Saisie Eleve</th><th>Attendu Academique</th><th style="text-align: center;">Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_trous_hydro1" in st.session_state:
            for num, t_item in enumerate(st.session_state.ordre_trous_hydro1, 1):
                saisie = st.session_state.get(f"hydro_t1_t_{t_item['id']}", "Choisir...")
                attendu = t_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-pass" if v_lbl == "CORRECT" else "status-fail"
                html_export_v1 += f"<tr><td>{num}</td><td>{t_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{v_class}'>{v_lbl}</span></td></tr>"

        html_export_v1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        import os
        chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Hydrostatique_Atelier1_{n_eleve}.html")
        try:
            with open(chemin_sauvegarde, "w", encoding="utf-8") as f:
                f.write(html_export_v1)
        except Exception:
            pass

        st.download_button(
            label="Telecharger mon rapport d'evaluation HTML",
            data=html_export_v1,
            file_name=f"Hydrostatique_Atelier1_{n_eleve}_Copie.html",
            mime="text/html",
            key="btn_download_hydro_final_t1",
            use_container_width=True
        )











