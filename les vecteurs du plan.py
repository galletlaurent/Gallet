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
st.title("TP les vecteur du plan ")
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
    "Définition d'un vecteur du plan", 
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

with tab1:
    st.header("Définition d'un vecteur du plan")
    st.write("Un vecteur représente un déplacement d'un point de départ $A$ vers un point d'arrivée $B$. Il est caractérisé par une **direction**, un **sens** et une **norme** (longueur).")

    # 1. Curseurs interactifs pour manipuler les points A et B
    st.subheader("Manipulation des points de départ et d'arrivée")
    col_xa, col_ya, col_xb, col_yb = st.columns(4)
    with col_xa:
        xA = st.slider("x de A", min_value=-10.0, max_value=10.0, value=-2.0, step=0.5, format="%.1f", key="tab1_xA")
    with col_ya:
        yA = st.slider("y de A", min_value=-10.0, max_value=10.0, value=1.0, step=0.5, format="%.1f", key="tab1_yA")
    with col_xb:
        xB = st.slider("x de B", min_value=-10.0, max_value=10.0, value=4.0, step=0.5, format="%.1f", key="tab1_xB")
    with col_yb:
        yB = st.slider("y de B", min_value=-10.0, max_value=10.0, value=5.0, step=0.5, format="%.1f", key="tab1_yB")

    # 2. Calculs géométriques fondamentaux
    vec_x = xB - xA
    vec_y = yB - yA
    norme_AB = np.sqrt(vec_x**2 + vec_y**2)

    # 3. Affichage des résultats analytiques
    st.subheader("Composantes et caractéristiques du vecteur")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.write("Le vecteur $\\overrightarrow{{AB}}$ a pour coordonnées :")
        st.latex(f"\\overrightarrow{{AB}} \\begin{{pmatrix}} x_B - x_A \\\\ y_B - y_A \\end{{pmatrix}} = \\begin{{pmatrix}} {xB:.1f} - ({xA:.1f}) \\\\ {yB:.1f} - ({yA:.1f}) \\end{{pmatrix}} = \\begin{{pmatrix}} {vec_x:.1f} \\\\ {vec_y:.1f} \\end{{pmatrix}}")
    with col_res2:
        st.metric(label="Norme de AB (Distance)", value=f"{norme_AB:.2f}")
        st.write("La norme correspond à la longueur du segment $[AB]$.")

    # 4. Tracé graphique dynamique du vecteur
    st.subheader("Visualisation géométrique")
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    
    # Dessin des points A et B
    ax1.scatter([xA, xB], [yA, yB], color=["red", "blue"], s=80, zorder=5)
    ax1.text(xA, yA, f" A({xA:.1f}; {yA:.1f})", verticalalignment="bottom", horizontalalignment="right", color="red", fontweight="bold")
    ax1.text(xB, yB, f" B({xB:.1f}; {yB:.1f})", verticalalignment="bottom", horizontalalignment="left", color="blue", fontweight="bold")
    
    # Tracé de la flèche représentant le vecteur AB
    if norme_AB > 0:
        ax1.quiver(xA, yA, vec_x, vec_y, angles='xy', scale_units='xy', scale=1, color="purple", width=0.006, zorder=4, label=f"v_AB ({vec_x:.1f} ; {vec_y:.1f})")
    
    # Habillage du graphique (repère orthonormé)
    ax1.axhline(0, color="black", linewidth=0.8)
    ax1.axvline(0, color="black", linewidth=0.8)
    ax1.set_xlim(-11, 11)
    ax1.set_ylim(-11, 11)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.set_aspect('equal', 'box')
    ax1.legend(loc="upper left")
    st.pyplot(fig1)

    verrou_v1 = st.session_state.get("v_verrouille_tab1", False)

    # Appel de la fonction de questionnaire pour la fonction du second degre
    res_q1, res_t1 = afficher_questions_definition_vecteur(
        xA=xA, 
        yA=yA, 
        xB=xB, 
        yB=yB, 
        vec_x=vec_x, 
        vec_y=vec_y, 
        norme_AB=norme_AB, 
        verrouille=verrou_v1
    )

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_v1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_vec1_official", 
        disabled=verrou_v1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_vec1_official", use_container_width=True, disabled=verrou_v1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_v1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_vec1" in st.session_state:
                for q_item in st.session_state.ordre_quiz_vec1:
                    reponse_eleve = st.session_state.get(f"vec_t1_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction de la Synthèse à trous (10 points)
            score_t1 = sum([
                st.session_state.get("vec_t1_t1") == "Vecteur",
                st.session_state.get("vec_t1_t2") == "x_A",
                st.session_state.get("vec_t1_t3") == "Norme",
                st.session_state.get("vec_t1_t4") == "Direction",
                st.session_state.get("vec_t1_t5") == "Sens",
                st.session_state.get("vec_t1_t6") == "y_A",
                st.session_state.get("vec_t1_t7") == "Pythagore",
                st.session_state.get("vec_t1_t8") == "Nul",
                st.session_state.get("vec_t1_t9") == "Coordonnees",
                st.session_state.get("vec_t1_t10") == "Opposes"
            ])

            st.session_state.score_v1_p1 = round(float(score_q1), 1)
            st.session_state.score_v1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_v1 = round(float(score_q1 + score_t1), 1)
            st.session_state.v_verrouille_tab1 = True
            st.rerun()
            
    if st.session_state.get("v_verrouille_tab1", False):
        scr1 = st.session_state.get("score_v1_p1", 0.0)
        scr2 = st.session_state.get("score_v1_v2", 0.0) if st.session_state.get("score_v1_v2") else st.session_state.get("score_v1_p2", 0.0)
        tot_s = st.session_state.get("score_final_v1", 0.0)

        from datetime import datetime
        timestamp_v1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DÉFINITION VECTEUR SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # Initialisation correcte de l'export HTML autonome (Style Bleu)
        html_export_v1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Definition Vecteurs - {n_eleve}</title>
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
                <p>Atelier 1 : Définition, composantes analytiques et direction du vecteur dans le plan</p>
                <p>Configuration manipulee : A({xA:.1f}; {yA:.1f}) vers B({xB:.1f}; {yB:.1f}) &rarr; AB({vec_x:.1f}; {vec_y:.1f})</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_v1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                - Note obtenue au Quiz des Vecteurs : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_vec1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_vec1, 1):
                saisie = st.session_state.get(f"vec_t1_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_v1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_v1 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_v1 = [
            ("1. Le deplacement rectiligne reliant l'origine A a l'extremite B s'appelle un", st.session_state.get("vec_t1_t1"), "Vecteur"),
            ("2. Pour calculer la composante x, on effectue la soustraction x_B -", st.session_state.get("vec_t1_t2"), "x_A"),
            ("3. La longueur mathématique d'un vecteur se désigne sous le terme de", st.session_state.get("vec_t1_t3"), "Norme"),
            ("4. La droite contenant le deplacement determine ce que l'on appelle sa", st.session_state.get("vec_t1_t4"), "Direction"),
            ("5. La fleche qui indique vers quel point on se dirige definit le", st.session_state.get("vec_t1_t5"), "Sens"),
            ("6. Pour calculer la composante verticale d'un vecteur, on effectue la différence y_B -", st.session_state.get("vec_t1_t6"), "y_A"),
            ("7. La formule de calcul de la norme d'un vecteur s'appuie sur le théorème géométrique de", st.session_state.get("vec_t1_t7"), "Pythagore"),
            ("8. Un vecteur dont la norme est égale à zéro est appelé un vecteur", st.session_state.get("vec_t1_t8"), "Nul"),
            ("9. Les deux valeurs numériques ordonnées décrivant le déplacement forment les", st.session_state.get("vec_t1_t9"), "Coordonnees"),
            ("10. Deux vecteurs ayant la même direction, la même norme mais un sens opposé sont dits", st.session_state.get("vec_t1_t10"), "Opposes")
        ]

        for num_t, (texte_t, saisie_t, attendu_t) in enumerate(phrases_trous_v1, 1):
            saisie_t = saisie_t if saisie_t else "Choisir..."
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_v1 += f"<tr><td>{num_t}</td><td>{texte_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_v1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL DE L'ATELIER 1 (HTML)",
            data=html_export_v1,
            file_name=f"Rapport_Atelier1_Vecteurs_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )





with tab2:
    st.header("Coordonnées et norme d'un vecteur")
    st.write("Dans un repère orthonormé, la norme d'un vecteur correspond à sa longueur. Elle se calcule en additionnant les carrés de ses composantes puis en extrayant la racine carrée du résultat.")

    # 1. Curseurs interactifs pour piloter le vecteur de la Tab 2
    st.subheader("Configuration du vecteur d'étude")
    col_sc2_x, col_sc2_y = st.columns(2)
    with col_sc2_x:
        x_u = st.slider("Composante horizontale (x)", min_value=-10.0, max_value=10.0, value=3.0, step=0.5, format="%.1f", key="tab2_x_u")
    with col_sc2_y:
        y_u = st.slider("Composante verticale (y)", min_value=-10.0, max_value=10.0, value=4.0, step=0.5, format="%.1f", key="tab2_y_u")

    # 2. Calculs géométriques locaux
    somme_carres = x_u**2 + y_u**2
    norme_u = np.sqrt(somme_carres)

    # 3. Démonstration de calcul pas à pas en LaTeX
    st.subheader("Démonstration analytique de la longueur")
    st.latex(f"\\|\\vec{{u}}\\| = \\sqrt{{x^2 + y^2}} = \\sqrt{{{x_u:.1f}^2 + ({y_u:.1f})^2}} = \\sqrt{{{somme_carres:.2f}}} = {norme_u:.2f}")

    # 4. Tracé graphique du vecteur depuis l'origine (0,0)
    st.subheader("Visualisation du vecteur")
    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    
    # Tracé de la flèche vectorielle
    if norme_u > 0:
        ax2.quiver(0, 0, x_u, y_u, angles='xy', scale_units='xy', scale=1, color="green", width=0.006, zorder=4, label=f"vec_u ({x_u:.1f} ; {y_u:.1f})")
    
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.axvline(0, color="black", linewidth=0.8)
    ax2.set_xlim(-11, 11)
    ax2.set_ylim(-11, 11)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.set_aspect('equal', 'box')
    ax2.legend(loc="upper left")
    st.pyplot(fig2)

    # --- ZONE QUESTIONNAIRE ET VALIDATION ATELIER 2 ---
    verrou_v2 = st.session_state.get("v_verrouille_tab2", False)

    res_q2, res_t2 = afficher_questions_coordonnees_norme(
        x_u=x_u, 
        y_u=y_u, 
        norme_u=norme_u, 
        verrouille=verrou_v2
    )

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_v2 = st.checkbox(
        "Je certifie avoir complète les questions de l'Atelier 2.", 
        key="check_certif_vec2_official", 
        disabled=verrou_v2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vec2_official", use_container_width=True, disabled=verrou_v2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_v2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Correction du Quiz 2 (10 points)
            score_q2 = 0.0
            if "ordre_quiz_vec2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_vec2:
                    reponse_eleve = st.session_state.get(f"vec_t2_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # Correction de la Synthèse 2 (10 points)
            score_t2 = sum([
                st.session_state.get("vec_t2_t1") == "Abscisse",
                st.session_state.get("vec_t2_t2") == "Ordonnee",
                st.session_state.get("vec_t2_t3") == "Orthonorme",
                st.session_state.get("vec_t2_t4") == "Barre",
                st.session_state.get("vec_t2_t5") == "Longueur",
                st.session_state.get("vec_t2_t6") == "Carre",
                st.session_state.get("vec_t2_t7") == "Carree",
                st.session_state.get("vec_t2_t8") == "Nul",
                st.session_state.get("vec_t2_t9") == "||u||",
                st.session_state.get("vec_t2_t10") == "2"
            ])

            st.session_state.score_v2_p1 = round(float(score_q2), 1)
            st.session_state.score_v2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_v2 = round(float(score_q2 + score_t2), 1)
            st.session_state.v_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab2", False):
        scr1 = st.session_state.get("score_v2_p1", 0.0)
        scr2 = st.session_state.get("score_v2_p2", 0.0)
        tot_s = st.session_state.get("score_final_v2", 0.0)

        from datetime import datetime
        timestamp_v2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER COORDONNÉES ET NORME SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # Initialisation de l'export HTML (Style Vert)
        html_export_v2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Norme Vecteurs - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #047857; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 2 : Coordonnées analytiques et calcul de la norme d'un vecteur dans un plan orthonormé</p>
                <p>Vecteur étudié : u({x_u:.1f}; {y_u:.1f}) &rarr; Norme ||u|| = {norme_u:.2f}</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_v2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #047857;">
                - Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_vec2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_vec2, 1):
                saisie = st.session_state.get(f"vec_t2_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_v2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_v2 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_v2 = [
            ("1. Dans un repère, le premier nombre d'un couple de coordonnées s'appelle l'", st.session_state.get("vec_t2_t1"), "Abscisse"),
            ("2. Le second nombre d'un couple de coordonnées d'un vecteur s'appelle l'", st.session_state.get("vec_t2_t2"), "Ordonnee"),
            ("3. Pour pouvoir utiliser la formule sqrt(x²+y²), le repère doit impérativement être", st.session_state.get("vec_t2_t3"), "Orthonorme"),
            ("4. La notation mathématique de la norme utilise une double", st.session_state.get("vec_t2_t4"), "Barre"),
            ("5. La valeur d'une norme géométrique correspond physiquement à une", st.session_state.get("vec_t2_t5"), "Longueur"),
            ("6. Dans la formule, les coordonnées x et y sont élevées au", st.session_state.get("vec_t2_t6"), "Carre"),
            ("7. La somme des carrés est placée sous une racine", st.session_state.get("vec_t2_t7"), "Carree"),
            ("8. Le seul vecteur dont la norme est mathématiquement égale à 0 est le vecteur", st.session_state.get("vec_t2_t8"), "Nul"),
            ("9. La norme d'un vecteur u est notée algébriquement", st.session_state.get("vec_t2_t9"), "||u||"),
            ("10. Si les composantes x et y doublent, la norme du vecteur sera multipliée par", st.session_state.get("vec_t2_t10"), "2")
        ]

        for num_t, (texte_t, saisie_t, attendu_t) in enumerate(phrases_trous_v2, 1):
            saisie_t = saisie_t if saisie_t else "Choisir..."
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_v2 += f"<tr><td>{num_t}</td><td>{texte_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_v2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL DE L'ATELIER 2 (HTML)",
            data=html_export_v2,
            file_name=f"Rapport_Atelier2_Normes_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("Propriétés géométriques des vecteurs")
    st.write("Modifiez les coordonnées des deux vecteurs $\\vec{u}$ et $\\vec{v}$ pour observer l'évolution de leurs relations de parallélisme (colinéarité) ou de perpendicularité (orthogonalité).")

    # 1. Curseurs pour manipuler les deux vecteurs distincts
    st.subheader("Coordonnées de u et v")
    col_u, col_v = st.columns(2)
    with col_u:
        x_u3 = st.slider("x de u", min_value=-10.0, max_value=10.0, value=2.0, step=1.0, format="%.1f", key="tab3_xu")
        y_u3 = st.slider("y de u", min_value=-10.0, max_value=10.0, value=3.0, step=1.0, format="%.1f", key="tab3_yu")
    with col_v:
        x_v3 = st.slider("x de v", min_value=-10.0, max_value=10.0, value=-3.0, step=1.0, format="%.1f", key="tab3_xv")
        y_v3 = st.slider("y de v", min_value=-10.0, max_value=10.0, value=2.0, step=1.0, format="%.1f", key="tab3_yv")

    # 2. Calculs géométriques
    det = x_u3 * y_v3 - y_u3 * x_v3
    p_scalaire = x_u3 * x_v3 + y_u3 * y_v3

    # 3. Affichage des blocs d'analyse analytique
    st.subheader("Analyses algébriques simultanées")
    c_det, c_ps = st.columns(2)
    with c_det:
        st.write("**Calcul du Déterminant :**")
        st.latex(f"\\text{{det}}(\\vec{{u}}, \\vec{{v}}) = x y' - y x' = {x_u3:.0f}({y_v3:.0f}) - {y_u3:.0f}({x_v3:.0f}) = {det:.0f}")
        if det == 0:
            st.success("Le déterminant est NUL : les vecteurs sont COLINÉAIRES (parallèles).")
        else:
            st.info("Déterminant non nul : les vecteurs ne sont pas colinéaires.")
            
    with c_ps:
        st.write("**Calcul du Produit Scalaire :**")
        st.latex(f"\\vec{{u}} \\cdot \\vec{{v}} = x x' + y y' = {x_u3:.0f}({x_v3:.0f}) + {y_u3:.0f}({y_v3:.0f}) = {p_scalaire:.0f}")
        if p_scalaire == 0:
            st.success("Le produit scalaire est NUL : les vecteurs sont PERPENDICULAIRES.")
        else:
            st.info("Produit scalaire non nul : les vecteurs ne sont pas orthogonaux.")

    # 4. Tracé graphique conjoint de u et v depuis l'origine
    st.subheader("Visualisation géométrique")
    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    
    if (x_u3 != 0 or y_u3 != 0):
        ax3.quiver(0, 0, x_u3, y_u3, angles='xy', scale_units='xy', scale=1, color="purple", width=0.006, zorder=4, label=f"u ({x_u3:.0f};{y_u3:.0f})")
    if (x_v3 != 0 or y_v3 != 0):
        ax3.quiver(0, 0, x_v3, y_v3, angles='xy', scale_units='xy', scale=1, color="orange", width=0.006, zorder=4, label=f"v ({x_v3:.0f};{y_v3:.0f})")

    ax3.axhline(0, color="black", linewidth=0.8)
    ax3.axvline(0, color="black", linewidth=0.8)
    ax3.set_xlim(-11, 11)
    ax3.set_ylim(-11, 11)
    ax3.grid(True, linestyle=":", alpha=0.6)
    ax3.set_aspect('equal', 'box')
    ax3.legend(loc="upper left")
    st.pyplot(fig3)

    # --- ZONE ÉVALUATION ATELIER 3 ---
    verrou_v3 = st.session_state.get("v_verrouille_tab3", False)

    res_q3, res_t3 = afficher_questions_proprietes_vectorielles(
        x_u=x_u3, y_u=y_u3, x_v=x_v3, y_v=y_v3, det=det, p_scalaire=p_scalaire, verrouille=verrou_v3
    )

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_v3 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 3.", key="check_certif_vec3_official", disabled=verrou_v3)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_vec3_official", use_container_width=True, disabled=verrou_v3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_v3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction Quiz 3 (10 points)
            score_q3 = 0.0
            if "ordre_quiz_vec3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_vec3:
                    reponse_eleve = st.session_state.get(f"vec_t3_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # Correction Synthèse 3 (10 points)
            score_t3 = sum([
                st.session_state.get("vec_t3_t1") == "Egaux",
                st.session_state.get("vec_t3_t2") == "Opposes",
                st.session_state.get("vec_t3_t3") == "Determinant",
                st.session_state.get("vec_t3_t4") == "Scalaire",
                st.session_state.get("vec_t3_t5") == "y*x'",
                st.session_state.get("vec_t3_t6") == "y*y'",
                st.session_state.get("vec_t3_t7") == "90_degres",
                st.session_state.get("vec_t3_t8") == "Paralleles",
                st.session_state.get("vec_t3_t9") == "Perpendicularite",
                st.session_state.get("vec_t3_t10") == "0"
            ])

            st.session_state.score_v3_p1 = round(float(score_q3), 1)
            st.session_state.score_v3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_v3 = round(float(score_q3 + score_t3), 1)
            st.session_state.v_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab3", False):
        scr1 = st.session_state.get("score_v3_p1", 0.0)
        scr2 = st.session_state.get("score_v3_p2", 0.0)
        tot_s = st.session_state.get("score_final_v3", 0.0)

        from datetime import datetime
        timestamp_v3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER PROPRIÉTÉS VECTORIELLES SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # Initialisation du rapport HTML (Style Ambre/Bordeaux)
        html_export_v3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Proprietes Vecteurs - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b45309; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 3 : Alignement, orthogonalité, parallélisme et décomposition de repère géométrique</p>
                <p>Configurations testées : u({x_u3:.0f};{y_u3:.0f}) et v({x_v3:.0f};{y_v3:.0f}) &rarr; Det = {det:.0f} | P.Scalaire = {p_scalaire:.0f}</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_v3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b45309;">
                - Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_vec3" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_vec3, 1):
                saisie = st.session_state.get(f"vec_t3_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_v3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_v3 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_v3 = [
            ("1. Deux vecteurs ayant les mêmes composantes x=x' et y=y' sont dits", st.session_state.get("vec_t3_t1"), "Egaux"),
            ("2. Si x = -x' et y = -y', les deux vecteurs sont qualifiés d'", st.session_state.get("vec_t3_t2"), "Opposes"),
            ("3. La colinéarité analytique de deux directions se vérifie par le calcul du", st.session_state.get("vec_t3_t3"), "Determinant"),
            ("4. L'orthogonalité (perpendicularité) de deux vecteurs se vérifie par le produit", st.session_state.get("vec_t3_t4"), "Scalaire"),
            ("5. Le calcul du déterminant croisé répond à l'opération de soustraction x*y' -", st.session_state.get("vec_t3_t5"), "y*x'"),
            ("6. Le produit scalaire s'établit par l'addition x*x' +", st.session_state.get("vec_t3_t6"), "y*y'"),
            ("7. Si le produit scalaire est nul, l'angle géométrique formé entre eux vaut", st.session_state.get("vec_t3_t7"), "90_degres"),
            ("8. Des vecteurs colinéaires modélisent géométriquement des lignes de fuite", st.session_state.get("vec_t3_t8"), "Paralleles"),
            ("9. Le mot orthogonalité est un synonyme mathématique rigoureux de", st.session_state.get("vec_t3_t9"), "Perpendicularite"),
            ("10. Le déterminant de deux vecteurs colinéaires est mathématiquement égal à", st.session_state.get("vec_t3_t10"), "0")
        ]

        for num_t, (texte_t, saisie_t, attendu_t) in enumerate(phrases_trous_v3, 1):
            saisie_t = saisie_t if saisie_t else "Choisir..."
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_v3 += f"<tr><td>{num_t}</td><td>{texte_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_v3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL DE L'ATELIER 3 (HTML)",
            data=html_export_v3,
            file_name=f"Rapport_Atelier3_Proprietes_Vectorielles_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )









with tab4:
    st.header("Application professionnelle et exercice d'évaluation")
    st.write("Sélectionnez votre domaine d'activité pour générer un énoncé technique unique avec des valeurs aléatoires.")

    # 1. Sélecteur de métier pour l'exercice
    metier_ex = st.selectbox(
        "Choisissez votre spécialité :",
        [
            "Topographe-Géomètre (Implantation de parcelles)",
            "Travaux Publics (Vérification d'alignement de bordures)",
            "Transport Routier (Force de traction combinée)"
        ],
        key="select_metier_vectoriel"
    )

    # Gestion de la génération aléatoire des coordonnées pour la session
    import random
    if "vec_ex_xu" not in st.session_state:
        st.session_state["vec_ex_xu"] = float(random.randint(2, 5))
        st.session_state["vec_ex_yu"] = float(random.randint(1, 4))
        # Génération d'un vecteur v perpendiculaire ou colinéaire selon le besoin pédagogique
        # Ici, un vecteur quelconque pour tester le calcul brut de l'élève
        st.session_state["vec_ex_xv"] = float(random.randint(-5, -2))
        st.session_state["vec_ex_yv"] = float(random.randint(2, 6))

    xu_ex = st.session_state["vec_ex_xu"]
    yu_ex = st.session_state["vec_ex_yu"]
    xv_ex = st.session_state["vec_ex_xv"]
    yv_ex = st.session_state["vec_ex_yv"]

    # Calculs académiques de contrôle en arrière-plan
    det_attendu = xu_ex * yv_ex - yu_ex * xv_ex
    ps_attendu = xu_ex * xv_ex + yu_ex * yv_ex
    norme_u_attendue = np.sqrt(xu_ex**2 + yu_ex**2)

    # 2. Affichage des énoncés selon le métier choisi
    st.write("---")
    if "Topographe" in metier_ex:
        st.subheader("Atelier 4 : Calcul d'implantation de repères topographiques")
        st.write(f"Un géomètre implante deux vecteurs de déplacement sur un chantier. Le vecteur de visée principal est $\\vec{{u}}\\begin{{pmatrix}} {xu_ex:.0f} \\\\ {yu_ex:.0f} \\end{{pmatrix}}$ et le vecteur secondaire est $\\vec{{v}}\\begin{{pmatrix}} {xv_ex:.0f} \\\\ {yv_ex:.0f} \\end{{pmatrix}}$.")
    elif "Travaux Publics" in metier_ex:
        st.subheader("Atelier 4 : Alignement de bordures de chaussée")
        st.write(f"Lors de la pose de bordures, un technicien utilise deux alignements lasers matérialisés par les vecteurs de direction $\\vec{{u}}\\begin{{pmatrix}} {xu_ex:.0f} \\\\ {yu_ex:.0f} \\end{{pmatrix}}$ et $\\vec{{v}}\\begin{{pmatrix}} {xv_ex:.0f} \\\\ {yv_ex:.0f} \\end{{pmatrix}}$.")
    else:
        st.subheader("Atelier 4 : Analyse des forces de traction d'un convoi")
        st.write(f"Deux remorqueurs exercent des forces de traction sur un châssis lourd. Les composantes des forces sont modélisées par les vecteurs $\\vec{{u}}\\begin{{pmatrix}} {xu_ex:.0f} \\\\ {yu_ex:.0f} \\end{{pmatrix}}$ et $\\vec{{v}}\\begin{{pmatrix}} {xv_ex:.0f} \\\\ {yv_ex:.0f} \\end{{pmatrix}}$.")

    # 3. Formulaire d'évaluation de l'élève
    st.markdown("##### Effectuez vos calculs analytiques et complétez les champs :")
    
    verrou_v4 = st.session_state.get("v_verrouille_tab4", False)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        ans_det = st.number_input("Calculez le Déterminant det(u, v) :", value=0.0, step=1.0, disabled=verrou_v4, key="ex_v4_det")
        ans_ps = st.number_input("Calculez le Produit Scalaire u · v :", value=0.0, step=1.0, disabled=verrou_v4, key="ex_v4_ps")
    with col_f2:
        ans_norme = st.number_input("Calculez la norme ||u|| (arrondie à 2 décimales) :", value=0.0, step=0.01, disabled=verrou_v4, key="ex_v4_norme")
        ans_colin = st.selectbox("Les deux vecteurs sont-ils colinéaires ?", ["Choisir...", "Oui", "Non"], disabled=verrou_v4, key="ex_v4_colin")

    # --- ZONE DE SCELLÉ ET TRAITEMENT DES NOTES DE L'ATELIER 4 ---
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_v4 = st.checkbox("Je certifie avoir résolu ce cas concret par le calcul.", key="check_certif_vec4_official", disabled=verrou_v4)

    if st.button("VALIDER ET ENREGISTRER L'EVALUATION DE L'ATELIER 4", key="btn_export_vec4_official", use_container_width=True, disabled=verrou_v4):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_v4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Grille de notation sur 20 points
            v_colin_attendu = "Oui" if det_attendu == 0 else "Non"
            
            score_v4 = sum([
                round(ans_det, 1) == round(det_attendu, 1),
                round(ans_ps, 1) == round(ps_attendu, 1),
                round(ans_norme, 2) == round(norme_u_attendue, 2),
                ans_colin == v_colin_attendu
            ]) * 5.0 # 4 critères valant 5 points chacun

            st.session_state.score_final_v4 = round(float(score_v4), 1)
            st.session_state.v_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab4", False):
        tot_s4 = st.session_state.get("score_final_v4", 0.0)
        st.success(f"ATELIER 4 EXERCICE METIER SCELLÉ | Note finale : {tot_s4:.1f} / 20")
















