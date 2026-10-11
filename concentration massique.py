# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="TP la concentration massique",
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
st.title("TP la concentration massique ")
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
    "La masse et le volume", 
    "La concentration massique Cm", 
    "Préparation d'une solution de concentration précise",
    "Dilution et concentration massique",
    "Exemple"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]

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


def afficher_questions_masse_volume(masse_actuelle, volume_actuel, cm_actuelle, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_mv" not in st.session_state:
        base_quiz_mv = [
            {
                "id": "mv_1", 
                "q": "Quelle est la définition physique de la masse d'un échantillon ?", 
                "options": ["La quantité de matière contenue dans l'échantillon", "L'espace à trois dimensions occupé par l'échantillon", "La force d'attraction exercée par la Terre"], 
                "rep": "La quantité de matière contenue dans l'échantillon"
            },
            {
                "id": "mv_2", 
                "q": "Quelle est la valeur de votre masse actuelle convertie en milligrammes (mg) ?", 
                "options": [f"{masse_actuelle * 1000:.1f}", f"{masse_actuelle / 1000:.4f}", f"{masse_actuelle * 100:.1f}"], 
                "rep": f"{masse_actuelle * 1000:.1f}"
            },
            {
                "id": "mv_3", 
                "q": "Quelle est la valeur de votre volume actuel exprimé en Litres (L) ?", 
                "options": [f"{volume_actuel / 1000:.4f}", f"{volume_actuel * 1000:.1f}", f"{volume_actuel / 100:.2f}"], 
                "rep": f"{volume_actuel / 1000:.4f}"
            },
            {
                "id": "mv_4", 
                "q": "Quel appareil de laboratoire permet de mesurer un volume liquide avec la plus haute précision ?", 
                "options": ["La fiole jaugée", "L'éprouvette graduée", "Le bécher"], 
                "rep": "La fiole jaugée"
            },
            {
                "id": "mv_5", 
                "q": "Pour effectuer correctement la lecture d'un volume sur une éprouvette graduée, l'oeil doit être aligné avec :", 
                "options": ["La base du ménisque", "Le haut des bords incurvés du liquide", "Le milieu exact de la verrerie"], 
                "rep": "La base du ménisque"
            },
            {
                "id": "mv_6", 
                "q": "Quelle est la valeur exacte calculée de la concentration massique actuelle de votre solution ?", 
                "options": [f"{cm_actuelle:.2f}", f"{cm_actuelle * 1000:.1f}", f"{cm_actuelle / 10:.2f}"], 
                "rep": f"{cm_actuelle:.2f}"
            },
            {
                "id": "mv_7", 
                "q": "Avant de peser un solide dans un récipient sur la balance, sur quel bouton faut-il appuyer ?", 
                "options": ["Le bouton TARE", "Le bouton ON/OFF", "Le bouton CALIBRATE"], 
                "rep": "Le bouton TARE"
            },
            {
                "id": "mv_8", 
                "q": "L'unité officielle de la masse dans le Système International est le :", 
                "options": ["Kilogramme", "Gramme", "Milligramme"], 
                "rep": "Kilogramme"
            },
            {
                "id": "mv_9", 
                "q": "L'unité de volume équivalente à 1 décimètre cube (1 dm³) est :", 
                "options": ["Le litre", "Le millilitre", "Le mètre cube"], 
                "rep": "Le litre"
            },
            {
                "id": "mv_10", 
                "q": "Si on multiplie la concentration massique par le volume de la solution, on retrouve :", 
                "options": ["La masse du soluté", "La masse totale de l'eau", "Le facteur de dilution"], 
                "rep": "La masse du soluté"
            }
        ]
        copie_base = list(base_quiz_mv)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_mv = copie_base

    col_q1, col_t1 = st.columns(2)

    with col_q1:
        st.markdown("##### Quiz sur la masse, le volume et les mesures (10 questions - 10 pts)")
        dict_rep_q1 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_mv, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"mv_quiz_q_{q_data['id']}"
            cle_opts = f"opts_mv_{q_data['id']}"
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
        with c1: st.write("1. La grandeur qui caractérise l'espace tridimensionnel occupé par un corps est le")
        with c2: dict_trous_1["t1"] = st.selectbox("", ["Choisir...", "Volume", "Masse", "Surface"], key="mv_t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour éliminer la masse du récipient vide posé sur la balance, on réalise la")
        with c4: dict_trous_1["t2"] = st.selectbox("", ["Choisir...", "Tare", "Mesure", "Pesee"], key="mv_t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Au laboratoire de chimie, la masse d'un soluté solide s'exprime couramment en")
        with c6: dict_trous_1["t3"] = st.selectbox("", ["Choisir...", "Gramme", "Litre", "Kilogramme"], key="mv_t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La verrerie graduée de forme allongée servant à mesurer grossièrement un liquide est l'")
        with c8: dict_trous_1["t4"] = st.selectbox("", ["Choisir...", "Eprouvette", "Fiole", "Becher"], key="mv_t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La surface incurvée d'un liquide observée dans un tube étroit s'appelle un")
        with c10: dict_trous_1["t5"] = st.selectbox("", ["Choisir...", "Menisque", "Niveau", "Disque"], key="mv_t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Un litre équivaut précisément à un volume de un décimètre")
        with c12: dict_trous_1["t6"] = st.selectbox("", ["Choisir...", "Cube", "Carre", "Lineaire"], key="mv_t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. L'erreur de lecture liée à une mauvaise position de l'oeil face aux graduations est l'erreur de")
        with c14: dict_trous_1["t7"] = st.selectbox("", ["Choisir...", "Parallaxe", "Calibrage", "Pesee"], key="mv_t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Le rapport de la masse du soluté par le volume total définit la concentration")
        with c16: dict_trous_1["t8"] = st.selectbox("", ["Choisir...", "Massique", "Molaire", "Volumique"], key="mv_t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'unité usuelle de la concentration massique utilisée par le chimiste est le g par")
        with r18: dict_trous_1["t9"] = st.selectbox("", ["Choisir...", "Litre", "Gramme", "Millilitre"], key="mv_t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour préparer un volume rigoureux de solution par dissolution, on utilise une fiole")
        with c20: dict_trous_1["t10"] = st.selectbox("", ["Choisir...", "Jaugee", "Graduee", "Erlenmeyer"], key="mv_t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q1, dict_trous_1


def generer_simulateur_pesee(cle_suffixe):
    import streamlit as st
    
    st.markdown("### Module de manipulation interactive")
    st.markdown("""
    Choisissez votre appareil de pesée pour mesurer un échantillon solide (morceaux de sucre) 
    ou un échantillon liquide (eau). Trouvez l'équilibre mécanique ou lisez la valeur digitale de masse nette.
    """)

    # Option d'appareil de mesure
    choix_balance = st.radio(
        "Sélectionnez l'appareil de pesée :",
        ["Balance de Roberval (Mécanique à aiguille)", "Balance électronique (Affichage digital moderne)"],
        key=f"choix_balance_{cle_suffixe}"
    )

    # Choix du type de soluté à peser
    type_echantillon = st.radio(
        "Quel type d'échantillon souhaitez-vous peser ?",
        ["Échantillon solide (Sucre)", "Échantillon liquide (Eau)"],
        key=f"type_echantillon_{cle_suffixe}"
    )

    col_sim1, col_sim2 = st.columns(2)

    with col_sim1:
        st.markdown("**Plateau Gauche : Échantillon à peser**")
        
        if type_echantillon == "Échantillon solide (Sucre)":
            nb_sucres = st.slider("Nombre de morceaux de sucre (5,0 g chacun) :", min_value=0, max_value=40, value=20, step=1, key=f"pesee_solide_sucres_{cle_suffixe}")
            poids_boite = st.checkbox("Ajouter le récipient de pesée vide (20,0 g)", value=False, key=f"pesee_solide_boite_{cle_suffixe}")
            
            masse_solute_g = nb_sucres * 5.0
            masse_totale_gauche = masse_solute_g
            if poids_boite:
                masse_totale_gauche += 20.0
                
        else:  # Cas du liquide
            st.markdown("*Note : Pour un liquide, l'utilisation d'un récipient (bécher de 30,0 g) est obligatoire.*")
            volume_liquide_ml = st.slider("Volume de liquide à introduire (mL) :", min_value=0, max_value=200, value=50, step=5, key=f"pesee_liquide_vol_{cle_suffixe}")
            
            masse_solute_g = float(volume_liquide_ml)
            masse_totale_gauche = masse_solute_g + 30.0
            
        st.info(f"Masse totale de l'échantillon brut avec récipient : {masse_totale_gauche:.1f} g")

    # Affichage adapté selon le type de balance sélectionné
    if choix_balance == "Balance de Roberval (Mécanique à aiguille)":
        with col_sim2:
            st.markdown("**Plateau Droite : Boîte de masses marquées**")
            
            m_100 = st.number_input("Masses de 100 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m100_{cle_suffixe}")
            m_50 = st.number_input("Masses de 50 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m50_{cle_suffixe}")
            m_20 = st.number_input("Masses de 20 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m20_{cle_suffixe}")
            m_10 = st.number_input("Masses de 10 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m10_{cle_suffixe}")
            m_5 = st.number_input("Masses de 5 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m5_{cle_suffixe}")
            
            masse_totale_droite = (m_100 * 100.0) + (m_50 * 50.0) + (m_20 * 20.0) + (m_10 * 10.0) + (m_5 * 5.0)
            st.info(f"Masse totale posée sur le plateau droit : {masse_totale_droite:.1f} g")

        st.markdown("---")
        st.markdown("**État visuel du fléau de la balance de Roberval**")

        if masse_totale_gauche > masse_totale_droite:
            st.warning(f"La balance penche vers la gauche (Excès de : {masse_totale_gauche - masse_totale_droite:.1f} g)")
            st.image("balance_gauche.jpg", caption="Le plateau gauche descend. Ajoutez des contrepoids à droite.", use_container_width=True)
            return 0.0, False
        elif masse_totale_droite > masse_totale_gauche:
            st.warning(f"La balance penche vers la droite (Excès de : {masse_totale_droite - masse_totale_gauche:.1f} g)")
            st.image("balance_droite.jpg", caption="Le plateau droit descend. Retirez des masses marquées.", use_container_width=True)
            return 0.0, False
        else:
            st.success("L'équilibre de la balance est parfait.")
            st.image("balance_equilibre.jpg", caption="Aiguille centrale au zéro. L'équilibre mécanique est atteint.", use_container_width=True)
            st.metric(label="Masse nette de l'échantillon validée (m)", value=f"{masse_solute_g:.1f} g")
            return masse_solute_g, True

    else:
        # Mode balance électronique digitale moderne
        with col_sim2:
            st.markdown("**Écran d'affichage digital et commandes**")
            bouton_tare = st.checkbox("Activer la fonction TARE électronique (Remise à zéro avec récipient)", value=False, key=f"tare_digitale_{cle_suffixe}")
            
            if bouton_tare:
                masse_affichee = masse_solute_g
                st.info("La masse du récipient vide a été soustraite par le logiciel de la balance.")
                pesee_ok = True if masse_solute_g > 0 else False
            else:
                masse_affichee = masse_totale_gauche
                st.warning("Attention : L'affichage inclut la masse du récipient. Pensez à tarer pour obtenir la masse nette du soluté.")
                pesee_ok = False
                
        st.markdown("---")
        st.markdown("**Visuel de la balance électronique**")
        st.image("balance_electronique.jpg", caption="Balance électronique de précision numérique", use_container_width=True)
        
        st.metric(label="Valeur affichée sur l'écran numérique", value=f"{masse_affichee:.1f} g")
        return masse_solute_g if pesee_ok else 0.0, pesee_ok




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
    st.header("Rappels et mesures : Masse et Volume")
    
    # ------------------------------------------
    # SECTION MASSE
    # ------------------------------------------
    st.subheader("1. La Masse (m)")
    st.markdown("""
    La masse correspond à la quantité de matière contenue dans un échantillon.
    L'unité officielle du Système International est le kilogramme (kg), mais en chimie, l'unité usuelle est le gramme (g) ou le milligramme (mg).
     On la mesure à l'aide d'une balance électronique de précision. """)
    
    col_img_masse = st.columns(1)[0]
    with col_img_masse:
        st.caption("Appareil de mesure de la masse :")
        st.image(
            "balance.jpg", 
            caption="Balance électronique de précision du laboratoire", 
            use_container_width=True
        )
    st.subheader("Différences de mesure de la masse selon l'état physique")

    col_texte_phys, col_img_phys = st.columns(2)

    with col_texte_phys:
        st.markdown("""
        * **Pour un solide :** La mesure est directe. On place une coupelle de pesée vide sur la balance, on appuie sur le bouton TARE pour remettre l'affichage à zéro, puis on introduit le solide à la spatule.
        * **Pour un liquide :** Un liquide n'a pas de forme propre. On pose obligatoirement le récipient de stockage (bécher, fiole) vide sur la balance, on réalise la TARE, puis on verse le liquide. La valeur affichée correspond exclusivement à la masse du liquide transféré.
        * **Pour un gaz :** Un gaz occupe tout l'espace disponible et sa masse est très faible. On réalise une pesée différentielle. On pèse le récipient plein de gaz (masse m1), on laisse s'échapper un volume précis de gaz, puis on repèse le contenant (masse m2). La masse du gaz extrait vaut m = m1 - m2.
        """)

    with col_img_phys:
        st.image(
            "etats_physiques_masse.jpg", 
            caption="Techniques de pesée pour les solides, liquides et gaz au laboratoire", 
            use_container_width=True
        )
    # Tableau interactif de conversion pour la Masse
    st.markdown("---")
    st.markdown("**Tableau de conversion interactif des masses**")
    st.markdown("Saisissez une valeur pour voir sa conversion automatique dans les autres unités :")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        valeur_m = st.number_input("Valeur à convertir (masse) :", min_value=0.0, value=1.0, step=0.1, key="input_masse_val")
    with col_m2:
        unite_m = st.selectbox("Unité de saisie :", ["kg", "g", "mg"], index=1, key="input_masse_unit")
    
    if unite_m == "kg":
        masse_en_g = valeur_m * 1000.0
    elif unite_m == "mg":
        masse_en_g = valeur_m / 1000.0
    else:
        masse_en_g = valeur_m
        
    st.markdown("Correspondances obtenues :")
    st.markdown(f"* Kilogramme (kg) : **{masse_en_g / 1000.0:.6f}** kg")
    st.markdown(f"* Gramme (g) : **{masse_en_g:.3f}** g")
    st.markdown(f"* Milligramme (mg) : **{masse_en_g * 1000.0:.1f}** mg")

    st.divider()

    # ------------------------------------------
    # SECTION VOLUME
    # ------------------------------------------
    st.subheader("2. Le Volume (V)")
    st.markdown("""
    Le volume représente l'espace à trois dimensions occupé par un corps ou une solution.
    L'unité officielle est le mètre cube (m³), mais en chimie, on utilise presque exclusivement le litre (L) et le millilitre (mL).
    
    **Différences de mesure selon l'état physique :**
    *   **Pour un liquide :** On utilise de la verrerie graduée (éprouvette graduée) pour une mesure courante, ou jaugée (fiole jaugée, pipette jaugée) pour une haute précision. L'oeil doit être au niveau du liquide pour éviter l'erreur de parallaxe, et la mesure se lit à la **base du ménisque**.
    *   **Pour un solide :** 
        *   *S'il est géométrique et régulier :* On mesure ses dimensions linéaires (longueur, rayon, etc.) et on applique une formule mathématique de volume.
        *   *S'il est irrégulier :* On utilise la méthode de **déplacement de liquide**. On verse un volume d'eau V1 dans une éprouvette, on y plonge le solide, on lit le nouveau volume V2. Le volume du solide vaut V = V2 - V1.
    *   **Pour un gaz :** Un gaz n'a pas de volume propre, il est compressible et expansible. On mesure son volume à l'aide d'une **seringue à gaz** étanche ou par la méthode du **déplacement d'eau** (on piège le gaz dans une éprouvette initialement remplie d'eau et retournée sur une cuve à eau).
    """)
    
    col_img_vol = st.columns(1)[0]
    with col_img_vol:
        st.caption("Appareil de mesure du volume :")
        st.image(
            "verrerie_precision.jpg", 
            caption="Verrerie graduée et jaugée pour les mesures de volumes", 
            use_container_width=True
        )

    # Tableau interactif de conversion pour le Volume
    st.markdown("---")
    st.markdown("**Tableau de conversion interactif des volumes**")
    st.markdown("Saisissez une valeur pour voir sa conversion automatique dans les autres unités :")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        valeur_v = st.number_input("Valeur à convertir (volume) :", min_value=0.0, value=100.0, step=1.0, key="input_vol_val")
    with col_v2:
        unite_v = st.selectbox("Unité de saisie :", ["L", "dL", "cL", "mL"], index=3, key="input_vol_unit")
        
    if unite_v == "dL":
        vol_en_l = valeur_v / 10.0
    elif unite_v == "cL":
        vol_en_l = valeur_v / 100.0
    elif unite_v == "mL":
        vol_en_l = valeur_v / 1000.0
    else:
        vol_en_l = valeur_v
        
    st.markdown("Correspondances obtenues :")
    st.markdown(f"* Litre (L) : **{vol_en_l:.4f}** L")
    st.markdown(f"* Décilitre (dL) : **{vol_en_l * 10.0:.2f}** dL")
    st.markdown(f"* Centilitre (cL) : **{vol_en_l * 100.0:.1f}** cL")
    st.markdown(f"* Millilitre (mL) : **{vol_en_l * 1000.0:.0f}** mL")

    masse_dynamique, pesee_reussie = generer_simulateur_pesee(cle_suffixe="cours")
    
    st.divider()
    
    # Variables pour votre bloc de questionnaire
    masse_actuelle = float(masse_dynamique) if pesee_reussie else 10.0
    volume_actuel = 100.0  
    cm_actuelle = masse_actuelle / (volume_actuel / 1000.0)
    verrou_v1 = st.session_state.get("v_verrouille_tab1", False)
    verrou_v1 = st.session_state.get("v_verrouille_tab1", False)

    res_q1, res_t1 = afficher_questions_masse_volume(
        masse_actuelle=masse_actuelle,
        volume_actuel=volume_actuel,
        cm_actuelle=cm_actuelle,
        verrouille=verrou_v1
    )

    st.write("---")
    p_eleve = st.session_state.get("id_prenom", "INCONNU").upper()
    n_eleve = st.session_state.get("id_nom", "INCONNU").upper()
    c_eleve = st.session_state.get("id_classe", "INCONNU").upper()

    case_certif_mv = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_mv_official", 
        disabled=verrou_v1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_mv_official", use_container_width=True, disabled=verrou_v1):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_mv:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_mv" in st.session_state:
                for q_item in st.session_state.ordre_quiz_mv:
                    reponse_eleve = st.session_state.get(f"mv_quiz_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction de la Synthese a trous (10 points)
            score_t1 = sum([
                st.session_state.get("mv_t_t1") == "Volume",
                st.session_state.get("mv_t_t2") == "Tare",
                st.session_state.get("mv_t_t3") == "Gramme",
                st.session_state.get("mv_t_t4") == "Eprouvette",
                st.session_state.get("mv_t_t5") == "Menisque",
                st.session_state.get("mv_t_t6") == "Cube",
                st.session_state.get("mv_t_t7") == "Parallaxe",
                st.session_state.get("mv_t_t8") == "Massique",
                st.session_state.get("mv_t_t9") == "Litre",
                st.session_state.get("mv_t_t10") == "Jaugee"
            ])

            st.session_state.score_mv_p1 = round(float(score_q1), 1)
            st.session_state.score_mv_p2 = round(float(score_t1), 1)
            st.session_state.score_final_mv = round(float(score_q1 + score_t1), 1)
            st.session_state.v_verrouille_tab1 = True
            st.rerun()
            
    if st.session_state.get("v_verrouille_tab1", False):
        scr1 = st.session_state.get("score_mv_p1", 0.0)
        scr2 = st.session_state.get("score_mv_p2", 0.0)
        tot_s = st.session_state.get("score_final_mv", 0.0)

        from datetime import datetime
        timestamp_mv = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER MASSE ET VOLUME SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # Initialisation de l'export HTML autonome (Style Bleu)
        html_export_mv = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Masse et Volume - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Chimie</h1>
                <p>Atelier 1 : Definition, mesures et unites de la masse et du volume</p>
                <p>Configuration simulee : m = {masse_actuelle:.3f} g | V = {volume_actuel:.1f} mL &rarr; Cm = {cm_actuelle:.2f} g/L</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_mv}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                - Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_mv" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_mv, 1):
                saisie = st.session_state.get(f"mv_quiz_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mv += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mv += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_mv = [
            ("1. La grandeur qui caracterise l'espace tridimensionnel occupe par un corps est le", st.session_state.get("mv_t_t1"), "Volume"),
            ("2. Pour eliminer la masse du recipient vide pose sur la balance, on realise la", st.session_state.get("mv_t_t2"), "Tare"),
            ("3. Au laboratoire de chimie, la masse d'un solute solide s'exprime couramment en", st.session_state.get("mv_t_t3"), "Gramme"),
            ("4. La verrerie graduee de forme allongee servant a mesurer grossierement un liquide est l'", st.session_state.get("mv_t_t4"), "Eprouvette"),
            ("5. La surface incurvee d'un liquide observee dans un tube etroit s'appelle un", st.session_state.get("mv_t_t5"), "Menisque"),
            ("6. Un litre equivaut precisement a un volume de un decimetre", st.session_state.get("mv_t_t6"), "Cube"),
            ("7. L'erreur de lecture liee a une mauvaise position de l'oeil face aux graduations est l'erreur de", st.session_state.get("mv_t_t7"), "Parallaxe"),
            ("8. Le rapport de la masse du solute par le volume total definit la concentration", st.session_state.get("mv_t_t8"), "Massique"),
            ("9. L'unite usuelle de la concentration massique utilisee par le chimiste est le g par", st.session_state.get("mv_t_t9"), "Litre"),
            ("10. Pour preparer un volume rigoureux de solution par dissolution, on utilise une fiole", st.session_state.get("mv_t_t10"), "Jaugee")
        ]

        for num, (phrase, saisie, attendu) in enumerate(phrases_trous_mv, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_mv += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mv += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE SESSION EN HTML",
            data=html_export_mv,
            file_name=f"Rapport_Masse_Volume_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Calcul de la Concentration Massique (Cm)")
    st.markdown("La formule fondamentale est :  \n\\[C_m = \\frac{m}{V}\\]")
    
    col1, col2 = st.columns(2)
    with col1:
        m_solute = st.number_input("Masse du soluté m (en g) :", min_value=0.0, value=5.0, key="cm_m")
        v_solution_ml = st.number_input("Volume de la solution V (en mL) :", min_value=0.1, value=250.0, key="cm_v")
    
    with col2:
        v_solution_l = v_solution_ml / 1000
        if st.button("Calculer la concentration Cm", type="primary", key="btn_cm"):
            cm_result = m_solute / v_solution_l
            st.metric(label="Concentration Massique (Cm)", value=f"{cm_result:.2f} g/L")
            st.code(f"Cm = {m_solute} g / {v_solution_l} L = {cm_result:.2f} g/L", language="python")

    st.header("Laboratoire interactif : De la pesée à la concentration")

    st.markdown("""
    Utilisez la simulation de la balance de Roberval pour peser vos morceaux de sucre solides, 
    puis observez comment cette masse influence directement la concentration massique de votre solution aqueuse.
    """)

    # =========================================================================
    # PARTIE 1 : SIMULATION GRAPHIQUE DE LA PESÉE (BALANCE DE ROBERVAL)
    # =========================================================================
    st.subheader("Etape 1 : Pesée du soluté (Sucre)")

    col_sim1, col_sim2 = st.columns(2)

    with col_sim1:
        st.markdown("**Plateau Gauche : Échantillon solide**")
        nb_sucres = st.slider("Nombre de morceaux de sucre (5,0 g chacun) :", min_value=0, max_value=40, value=20, step=1, key="lab_nb_sucres")
        poids_boite = st.checkbox("Ajouter le récipient de pesée vide (20,0 g)", value=False, key="lab_poids_boite")
        
        # Calcul de la masse réelle du soluté et de la masse totale du plateau gauche
        masse_solute_g = nb_sucres * 5.0
        masse_totale_gauche = masse_solute_g
        if poids_boite:
            masse_totale_gauche += 20.0
            
        st.info(f"Masse totale posée sur le plateau gauche : {masse_totale_gauche:.1f} g")

    with col_sim2:
        st.markdown("**Plateau Droite : Boîte de masses marquées**")
        
        # Saisie des masses par l'expérimentateur
        m_100 = st.number_input("Masses de 100 g :", min_value=0, max_value=5, value=0, step=1, key="lab_m100")
        m_50 = st.number_input("Masses de 50 g :", min_value=0, max_value=5, value=0, step=1, key="lab_m50")
        m_20 = st.number_input("Masses de 20 g :", min_value=0, max_value=5, value=0, step=1, key="lab_m20")
        m_10 = st.number_input("Masses de 10 g :", min_value=0, max_value=5, value=0, step=1, key="lab_m10")
        m_5 = st.number_input("Masses de 5 g :", min_value=0, max_value=5, value=0, step=1, key="lab_m5")
        
        masse_totale_droite = (m_100 * 100.0) + (m_50 * 50.0) + (m_20 * 20.0) + (m_10 * 10.0) + (m_5 * 5.0)
        st.info(f"Masse totale posée sur le plateau droit : {masse_totale_droite:.1f} g")

        st.markdown("**État visuel du fléau de la balance**")

        # Logique d'affichage dynamique des images d'état proposé
        pesee_valide = False

        if masse_totale_gauche > masse_totale_droite:
            st.warning(f"La balance penche vers la gauche (Excès de : {masse_totale_gauche - masse_totale_droite:.1f} g)")
            st.image(
                "balance_gauche.jpg", 
                caption="Le plateau gauche descend. Ajoutez des contrepoids à droite.", 
                use_container_width=True
            )

        elif masse_totale_droite > masse_totale_gauche:
            st.warning(f"La balance penche vers la droite (Excès de : {masse_totale_droite - masse_totale_gauche:.1f} g)")
            st.image(
                "balance_droite.jpg", 
                caption="Le plateau droit descend. Retirez des masses marquées.", 
                use_container_width=True
            )

        else:
            pesee_valide = True
            st.success("L'équilibre de la balance de Roberval est parfait.")
            st.image(
                "balance_equilibre.jpg", 
                caption="Aiguille centrale au zéro. La pesée est rigoureusement exacte.", 
                use_container_width=True
            )

        st.divider()

    # =========================================================================
    # PARTIE 2 : CONNECTION DIRECTE AVEC LE CALCUL DE LA CONCENTRATION MASSIQUE
    # =========================================================================
        st.subheader("Etape 2 : Dissolution et calcul de la concentration massique")

        if not pesee_valide:
            st.error("Le calcul de la solution est bloqué : Ajustez vos masses marquées à droite pour équilibrer la balance.")
        else:
            st.markdown(f"La masse de soluté validée par la pesée est de : **m = {masse_solute_g:.1f} g**")
            
            # Choix du volume de dissolution par l'élève
            volume_fiole_ml = st.selectbox(
                "Sélectionnez le volume de la fiole jaugée pour la dissolution :",
                [50.0, 100.0, 200.0, 250.0, 500.0, 1000.0],
                index=3,
                key="lab_volume_fiole"
            )
            
            # Calcul de la concentration massique
            volume_l = volume_fiole_ml / 1000.0
            concentration_massique_g_l = masse_solute_g / volume_l
            
            st.subheader("Résultat de la manipulation")
            st.metric(label="Concentration massique obtenue (Cm)", value=f"{concentration_massique_g_l:.2f} g/L")
            
            st.markdown(f"""
            **Détail de la relation physique :**
            * Formule appliquée : Cm = m / V
            * Masse de soluté (sucre) : {masse_solute_g:.1f} g
            * Volume de solution (eau distillée) : {volume_l:.3f} L (soit {volume_fiole_ml:.0f} mL)
            * Équation : {masse_solute_g:.1f} g / {volume_l:.3f} L = **{concentration_massique_g_l:.2f} g/L**
            """)


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
    st.header("Dissolution : Préparer une solution par pesée")
    st.markdown("""
    Pour préparer un volume précis V d'une solution à une concentration Cm donnée, 
    on cherche la **masse exacte** à peser à l'aide de la formule inversée :  
    \\[m = C_m \\times V\\]
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        target_cm = st.number_input("Concentration Cm ciblée (g/L) :", min_value=0.0, value=10.0, key="prep_cm")
        target_v_ml = st.number_input("Volume de fiole jaugée disponible V (mL) :", min_value=1.0, value=100.0, key="prep_v")
        
    with col2:
        target_v_l = target_v_ml / 1000
        required_m = target_cm * target_v_l
        
        st.subheader("Protocole expérimental :")
        st.success(f"Il faut peser exactement {required_m:.3f} g de soluté solide.")
        st.markdown(f"""
        1. Peser {required_m:.3f} g de solide dans une coupelle de pesée.
        2. Introduire le solide dans une fiole jaugée de {target_v_ml} mL à l'aide d'un entonnoir.
        3. Rincer la coupelle et l'entonnoir avec de l'eau distillée vers la fiole.
        4. Remplir la fiole aux 2/3, agiter pour dissoudre complètement.
        5. Ajuster jusqu'au trait de jauge avec de l'eau distillée, puis homogénéiser.
        """)

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
    st.header("Dilution : Préparation à partir d'une solution mère")
    st.markdown("""
    Lors d'une dilution, la masse de soluté se conserve (\\(m_{\\text{{mère}}}} = m_{\\text{{fille}}}\\)). On applique la formule :
    \\[C_{\\text{{mère}}} \\times V_{\\text{{mère}}} = C_{\\text{{fille}}} \\times V_{\\text{{fille}}}\\]
    Le **facteur de dilution** F est donné par : \\[F = \\frac{{C_{\\text{{mère}}}}}{{C_{\\text{{fille}}}}} = \\frac{{V_{\\text{{fille}}}}}{{V_{\\text{{mère}}}}}\\]
    """)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        c_mere = st.number_input("Concentration de la solution mère C_mère (g/L) :", min_value=0.1, value=20.0, key="dil_cmere")
    with c2:
        c_fille = st.number_input("Concentration voulue pour la solution fille C_fille (g/L) :", min_value=0.01, value=2.0, key="dil_cfille")
    with c3:
        v_fille_ml = st.number_input("Volume de solution fille souhaité V_fille (mL) :", min_value=1.0, value=100.0, key="dil_vfille")
        
    if c_fille > c_mere:
        st.error("La concentration de la solution fille ne peut pas être supérieure à celle de la solution mère !")
    else:
        facteur_f = c_mere / c_fille
        v_mere_ml = v_fille_ml / facteur_f
        
        st.subheader("Résultats théoriques et matériels :")
        st.metric(label="Facteur de dilution (F)", value=f"{facteur_f:.1f} x")
        st.info(f"Volume de solution mère à prélever (V_mère) : {v_mere_ml:.2f} mL")
        
        st.markdown(f"""
        **Verrerie recommandée :**
        *   Prélever {v_mere_ml:.2f} mL de solution mère avec une pipette jaugée ou graduée adaptée.
        *   Introduire le prélèvement dans une fiole jaugée de {v_fille_ml:.0f} mL.
        *   Compléter avec de l'eau distillée jusqu'au trait de jauge, puis mélanger.
        """)










        
    # --- 4. EVALUATION ET EXPORTATION HTML COMPLÈTE ---
    st.markdown("---")
    if st.button("Valider et corriger ma copie d'examen", type="primary", key="btn_correction_tab4"):
        if not ident_verrouille:
            st.error("Action refusee : Veuillez d'abord completer vos informations d'identification dans le premier onglet.")
        else:
            score = 0
            lignes_html = ""
            
            for item in saisies_eleve:
                saisie = item["saisie"].strip().lower().replace("é", "e").replace("à", "a").replace(",", ".")
                attendu = item["attendu"].strip().lower().replace(",", ".")
                
                is_juste = False
                if attendu in ["oui", "non", "chasles", "pythagore", "vecteurs", "carre", "rectangle", "trapeze"]:
                    is_juste = (saisie == attendu)
                else:
                    try:
                        is_juste = (abs(float(saisie) - float(attendu)) <= 1.1)
                    except ValueError:
                        is_juste = False
                        
                if is_juste:
                    score += 1
                    verdict = "CORRECT"
                    lbl_style = "status-pass"
                else:
                    verdict = "INCORRECT"
                    lbl_style = "status-fail"
                    
                lignes_html += f"""<tr>
                    <td>{item['index']}</td>
                    <td>Question technique d'examen n°{item['index']}</td>
                    <td>{item['saisie']}</td>
                    <td>{item['attendu']}</td>
                    <td><span class="{lbl_style}">{verdict}</span></td>
                </tr>"""
                
            note_finale = float(score)
            
            if note_finale >= 10.0:
                st.success(f"Examen valide. Note obtenue : {note_finale:.1f} / 20.0")
            else:
                st.error(f"Examen non valide. Note obtenue : {note_finale:.1f} / 20.0")
                
            date_jour = datetime.now().strftime("%d/%m/%Y à %H:%M")
            html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Evaluation Complete - Atelier 4</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; margin-bottom: 30px; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px; font-size: 13px; text-align: left; }}
        td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ background-color: #dcfce7; color: #16a34a; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
        .status-fail {{ background-color: #fee2e2; color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">{note_finale:.1f} / 20</div>
        <h2 style="margin: 0; padding-bottom: 8px;">Professeur Laurent GALLET</h2>
        <div class="meta-info" style="font-size: 13px; line-height: 1.5;">
            <strong>Atelier 4 :</strong> Evaluation de Synthese Vectorielle Multicriteres<br>
            <strong>Eleve :</strong> {prenom_eleve} {nom_eleve} | <strong>Classe :</strong> {classe_eleve}<br>
            <strong>Domaine Metier :</strong> {choix_metier}<br>
            <span style="font-size:11px; opacity:0.8;">Fige et scelle le : {date_jour}</span>
        </div>
    </div>
    
    <div class="section-title">DETAIL DES COMPTES RENDUS LOGISTIQUES ET GEOMETRIQUES</div>
    <table>
        <thead>
            <tr>
                <th style="width: 8%; text-align: center;">N°</th>
                <th style="width: 42%;">Indicateur de session verifie</th>
                <th style="width: 19%;">Saisie de l'eleve</th>
                <th style="width: 19%;">Correction Academique</th>
                <th style="width: 12%; text-align: center;">Verdict</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html}
        </tbody>
    </table>
</body>
</html>"""

            chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Vecteurs_Atelier4_{nom_eleve}_Streamlit.html")
            try:
                with open(chemin_sauvegarde, "w", encoding="utf-8") as f:
                    f.write(html_content)
                st.success(f"Copie scellee sauvegardee localement : `{chemin_sauvegarde}`")
            except Exception as e:
                st.error(f"Erreur d'ecriture : {str(e)}")

            st.download_button(
                label="Telecharger mon rapport d'evaluation HTML",
                data=html_content,
                file_name=f"Vecteurs_Atelier4_{nom_eleve}_Copie.html",
                mime="text/html",
                key="btn_download_tab4"
            )



with tab5:
    st.header("Exemple d'application concret")
    st.markdown("""
    ### Énoncé type :
    Un technicien de laboratoire souhaite préparer **200 mL** d'une solution aqueuse de sulfate de cuivre à une concentration de **5,0 g/L**.
    
    ### Résolution pas à pas :
    1. **Identification des données :**
       * Concentration visée : Cm = 5,0 g/L
       * Volume de la solution : V = 200 mL = 0,200 L
    
    2. **Calcul de la masse nécessaire :**
       \\[m = C_m \\times V\\]
       \\[m = 5,0 \\text{{ g/L}} \\times 0,200 \\text{{ L}} = 1,0 \\text{{ g}}\\]
       
    3. **Conclusion :**
       Le technicien devra peser précisément **1,0 gramme** de cristaux de sulfate de cuivre pour fabriquer sa solution.
    """)
    st.info("Vous pouvez tester ces valeurs exactes dans l'onglet 'Préparation d'une solution...' pour vérifier la cohérence du simulateur.")


    st.write("---")
    st.subheader("Espace d'expérimentation autonome")
    
    # Second appel indépendant exploitant les mêmes fichiers .jpg
    masse_libre, etat_libre = generer_simulateur_pesee(cle_suffixe="exemple")






