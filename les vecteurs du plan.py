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


def afficher_questions_variations_signes(a3, b3, c3, alpha3, beta3, rapport3, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_tab3" not in st.session_state:
        base_quiz_tab3 = [
            {"id": "t3_1", "q": "Dans le tableau de variation, quelle valeur de x marque le changement de direction de la courbe ?", "type": "menu", "options": [f"alpha = {alpha3:.2f}", f"beta = {beta3:.2f}", "x = 0"], "rep": f"alpha = {alpha3:.2f}"},
            {"id": "t3_2", "q": "Quelle est la valeur de l'extremum (maximum ou minimum) atteinte par la fonction ?", "type": "menu", "options": [f"{beta3:.2f}", f"{alpha3:.2f}", "0"], "rep": f"{beta3:.2f}"},
            {"id": "t3_3", "q": "À l'exterieur de ses racines reelles, quel est le signe d'un polynome du second degre ?", "type": "menu", "options": ["Toujours le signe du coefficient a", "Toujours le signe du coefficient c", "Toujours strictement negatif"], "rep": "Toujours le signe du coefficient a"},
            {"id": "t3_4", "q": "Si un polynome n'a aucune racine reelle, change-t-il de signe sur la droite des reels ?", "type": "menu", "options": ["Non, il conserve un signe constant", "Oui, il change au niveau de alpha", "Oui, il change au niveau de f(0)"], "rep": "Non, il conserve un signe constant"},
            {"id": "t3_5", "q": "Dans l'intervalle strict situe entre deux racines reelles distinctes, le signe de f(x) est :", "type": "menu", "options": ["Le signe oppose de a", "Le signe de a", "Le signe de c"], "rep": "Le signe oppose de a"}
        ]
        copie_base = list(base_quiz_tab3)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_tab3 = copie_base

    col_q3, col_t3 = st.columns(2)

    with col_q3:
        st.markdown("##### Quiz sur les variations et les signes (5 questions - 10 pts)")
        dict_rep_q3 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"sd_t3_q_{q_data['id']}"
            cle_opts = f"opts_t3_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q3[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t3:
        st.markdown("##### Synthese de cours (5 trous - 10 pts)")
        dict_trous_3 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le sens de variation change precisement au niveau du point d'abscisse")
        with c2: dict_trous_3["t1"] = st.selectbox("", ["Choisir...", "alpha", "beta", "c"], key="sd_t3_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Si le parametre dominant 'a' est positif, la fonction commence par etre")
        with c4: dict_trous_3["t2"] = st.selectbox("", ["Choisir...", "Decroissante", "Croissante"], key="sd_t3_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Graphiquement, la parabole traverse ou effleure l'axe des abscisses au niveau de ses")
        with c6: dict_trous_3["t3"] = st.selectbox("", ["Choisir...", "Racines", "Sommets", "Asymptotes"], key="sd_t3_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Entre les deux racines, le signe algebrique obtenu est le signe oppose de")
        with c8: dict_trous_3["t4"] = st.selectbox("", ["Choisir...", "a", "b", "c"], key="sd_t3_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. L'ordonnee maximale ou minimale atteinte par l'extremum correspond a la valeur")
        with c10: dict_trous_3["t5"] = st.selectbox("", ["Choisir...", "beta", "alpha", "c"], key="sd_t3_t5", disabled=verrouille, label_visibility="collapsed")

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

    # --- ZONE QUESTIONNAIRE ET VALIDATION ATELIER 1 ---
    verrou_v1 = st.session_state.get("v_verrouille_tab1", False)
    
    # Section 2 : Tableaux de valeurs
    col_tab_fixe, col_tab_interactif = st.columns(2)
    
    with col_tab_fixe:
        st.subheader("Tableau de valeurs automatique (Base globale)")
        st.write("Tableau standard calcule a partir des coefficients de la barre laterale :")

        x_values = np.linspace(-10, 10, 9)
        y_values = np.linspace(-10, 10, 9)
        df_valeurs = pd.DataFrame({"x": x_values, "f(x)": y_values})
        st.dataframe(df_valeurs.style.format({"x": "{:.2f}", "f(x)": "{:.2f}"}), use_container_width=True)
        
    with col_tab_interactif:
        st.subheader("Outil de calcul interactif (Base globale)")
        mode_calcul = st.radio(
            "Choisissez votre mode de calcul :",
            ["Calculer f(x) a partir de x (Image)", "Calculer x a partir de f(x) (Antecédents)"],
            key="mode_calcul"
        )
        
        if mode_calcul == "Calculer f(x) a partir de x (Image)":
            input_x = st.number_input("Entrez une valeur pour x :", value=0.0, step=0.5, format="%.2f")
            output_fx = a_global * (input_x ** 2) + b_global * input_x + c_global
            st.info(f"Pour x = {input_x:.2f}, l'image est f(x) = {output_fx:.2f}")
            
        else:
            input_fx = st.number_input("Entrez une valeur cible pour f(x) :", value=float(round(beta_global, 2)), step=0.5, format="%.2f")
            rapport_cible = (input_fx - beta_global) / a_global
            
            if rapport_cible < 0:
                st.warning(f"Il n'existe aucun nombre reel x tel que f(x) = {input_fx:.2f} avec la configuration globale.")
            elif rapport_cible == 0:
                st.info(f"Il existe une seule valeur unique : x = {alpha_global:.2f}")
            else:
                x_sol1 = alpha_global - np.sqrt(rapport_cible)
                x_sol2 = alpha_global + np.sqrt(rapport_cible)
                st.info(f"Il existe deux antécédents pour f(x) = {input_fx:.2f} :\n- x1 = {x_sol1:.2f}\n- x2 = {x_sol2:.2f}")

    verrou_sd_1 = st.session_state.get("sd_verrouille_tab1", False)

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
    st.header("Analyses completes de la fonction")
    st.write("Utilisez les curseurs locaux pour observer l'impact des coefficients sur les variations et le signe de la fonction.")

    # Curseurs specifiques pour l'onglet 3
    col_c3_1, col_c3_2, col_c3_3 = st.columns(3)
    with col_c3_1:
        a3 = st.slider("Coefficient a", min_value=-5.0, max_value=5.0, value=1.0, step=0.1, format="%.1f", key="tab3_slider_a")
        if a3 == 0.0:
            st.error("Le coefficient a ne peut pas etre nul pour une fonction du second degre.")
            st.stop()
    with col_c3_2:
        b3 = st.slider("Coefficient b", min_value=-10.0, max_value=10.0, value=-2.0, step=0.1, format="%.1f", key="tab3_slider_b")
    with col_c3_3:
        c3 = st.slider("Coefficient c", min_value=-10.0, max_value=10.0, value=-3.0, step=0.1, format="%.1f", key="tab3_slider_c")

    # Calculs locaux lies aux curseurs de l'onglet 3
    alpha3 = -b3 / (2 * a3)
    beta3 = a3 * (alpha3 ** 2) + b3 * alpha3 + c3
    
    # Repérage des racines locales pour le tableau de signe
    rapport3 = -beta3 / a3
    racines3 = []
    if rapport3 > 0:
        racines3 = [alpha3 - np.sqrt(rapport3), alpha3 + np.sqrt(rapport3)]

    # Affichage des tableaux de variations et de signes
    st.write("---")
    col_var, col_signe = st.columns(2)
    
    with col_var:
        st.subheader("Tableau de variation")
        
        if a3 > 0:
            html_variation = f"""
            <table style="width:100%; border-collapse: collapse; border: 2px solid #1e293b; font-family: 'Times New Roman', serif; background: white; color: black;">
                <tr style="border-bottom: 2px solid #1e293b; height: 40px; text-align: center;">
                    <td style="width: 20%; font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">x</td>
                    <td style="width: 26.6%;">-&infin;</td>
                    <td style="width: 26.6%; font-weight: bold;">{alpha3:.2f}</td>
                    <td style="width: 26.6%;">+&infin;</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc; text-align: center; height: 130px;">f(x)</td>
                    <td colspan="3" style="padding: 0; height: 130px; vertical-align: top;">
                        <svg width="100%" height="130" style="display: block;">
                            <defs>
                                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>
                                </marker>
                            </defs>
                            <text x="15%" y="25" font-family="Times New Roman" font-size="16" text-anchor="middle" fill="black">+&infin;</text>
                            <text x="50%" y="115" font-family="Times New Roman" font-size="16" font-weight="bold" text-anchor="middle" fill="black">{beta3:.2f}</text>
                            <text x="85%" y="25" font-family="Times New Roman" font-size="16" text-anchor="middle" fill="black">+&infin;</text>
                            <line x1="20%" y1="35" x2="45%" y2="105" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
                            <line x1="55%" y1="105" x2="80%" y2="35" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
                        </svg>
                    </td>
                </tr>
            </table>
            """
        else:
            html_variation = f"""
            <table style="width:100%; border-collapse: collapse; border: 2px solid #1e293b; font-family: 'Times New Roman', serif; background: white; color: black;">
                <tr style="border-bottom: 2px solid #1e293b; height: 40px; text-align: center;">
                    <td style="width: 20%; font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">x</td>
                    <td style="width: 26.6%;">-&infin;</td>
                    <td style="width: 26.6%; font-weight: bold;">{alpha3:.2f}</td>
                    <td style="width: 26.6%;">+&infin;</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc; text-align: center; height: 130px;">f(x)</td>
                    <td colspan="3" style="padding: 0; height: 130px; vertical-align: top;">
                        <svg width="100%" height="130" style="display: block;">
                            <defs>
                                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/>
                                </marker>
                            </defs>
                            <text x="15%" y="115" font-family="Times New Roman" font-size="16" text-anchor="middle" fill="black">-&infin;</text>
                            <text x="50%" y="25" font-family="Times New Roman" font-size="16" font-weight="bold" text-anchor="middle" fill="black">{beta3:.2f}</text>
                            <text x="85%" y="115" font-family="Times New Roman" font-size="16" text-anchor="middle" fill="black">-&infin;</text>
                            <line x1="20%" y1="105" x2="45%" y2="35" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
                            <line x1="55%" y1="35" x2="80%" y2="105" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
                        </svg>
                    </td>
                </tr>
            </table>
            """
            
        st.markdown(html_variation, unsafe_allow_html=True)

    with col_signe:
        st.subheader("Tableau de signe")
        
        signe_a = "+" if a3 > 0 else "-"
        signe_oppose = "-" if a3 > 0 else "+"
        
        # Traitement selon le nombre de racines trouvees
        if len(racines3) == 2:
            r1, r2 = sorted(racines3)
            html_signe = f"""
            <table style="width:100%; border-collapse: collapse; border: 2px solid #1e293b; font-family: 'Times New Roman', serif; text-align: center; background: white; color: black;">
                <tr style="border-bottom: 2px solid #1e293b; height: 40px;">
                    <td style="width: 15%; font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">x</td>
                    <td style="width: 15%;">-&infin;</td>
                    <td style="width: 15%; font-weight: bold;">{r1:.2f}</td>
                    <td style="width: 25%;"></td>
                    <td style="width: 15%; font-weight: bold;">{r2:.2f}</td>
                    <td style="width: 15%;">+&infin;</td>
                </tr>
                <tr style="height: 50px;">
                    <td style="font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">f(x)</td>
                    <td style="color: #ef4444; font-size: 16px;">signe de a ({signe_a})</td>
                    <td style="border-left: 1px solid #000; border-right: 1px solid #000; font-weight: bold; font-size: 16px;">0</td>
                    <td style="color: #0284c7; font-size: 16px;">signe de -a ({signe_oppose})</td>
                    <td style="border-left: 1px solid #000; border-right: 1px solid #000; font-weight: bold; font-size: 16px;">0</td>
                    <td style="color: #ef4444; font-size: 16px;">signe de a ({signe_a})</td>
                </tr>
            </table>
            """
        elif rapport3 == 0:
            html_signe = f"""
            <table style="width:100%; border-collapse: collapse; border: 2px solid #1e293b; font-family: 'Times New Roman', serif; text-align: center; background: white; color: black;">
                <tr style="border-bottom: 2px solid #1e293b; height: 40px;">
                    <td style="width: 20%; font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">x</td>
                    <td style="width: 25%;">-&infin;</td>
                    <td style="width: 30%; font-weight: bold;">{alpha3:.2f}</td>
                    <td style="width: 25%;">+&infin;</td>
                </tr>
                <tr style="height: 50px;">
                    <td style="font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">f(x)</td>
                    <td style="color: #ef4444; font-size: 16px;">signe de a ({signe_a})</td>
                    <td style="border-left: 1px solid #000; border-right: 1px solid #000; font-weight: bold; font-size: 16px;">0</td>
                    <td style="color: #ef4444; font-size: 16px;">signe de a ({signe_a})</td>
                </tr>
            </table>
            """
        else:
            html_signe = f"""
            <table style="width:100%; border-collapse: collapse; border: 2px solid #1e293b; font-family: 'Times New Roman', serif; text-align: center; background: white; color: black;">
                <tr style="border-bottom: 2px solid #1e293b; height: 40px;">
                    <td style="width: 20%; font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">x</td>
                    <td style="width: 40%;">-&infin;</td>
                    <td style="width: 40%;">+&infin;</td>
                </tr>
                <tr style="height: 50px;">
                    <td style="font-weight: bold; border-right: 2px solid #1e293b; background: #f8fafc;">f(x)</td>
                    <td colspan="2" style="color: #ef4444; font-size: 16px;">Le polynome ne s'annule pas<br>Chaque point est du signe de a ({signe_a})</td>
                </tr>
            </table>
            """
            
        st.markdown(html_signe, unsafe_allow_html=True)

    # --- ZONE QUESTIONNAIRE ET VALIDATION ATELIER 3 ---
    verrou_sd_3 = st.session_state.get("sd_verrouille_tab3", False)

    st.write("---")
    st.subheader("Validation des connaissances de l'Atelier 3")

    # Appel direct de la fonction externe definie plus haut
    res_q3, res_t3 = afficher_questions_variations_signes(
        a3=a3,
        b3=b3,
        c3=c3,
        alpha3=alpha3,
        beta3=beta3,
        rapport3=rapport3,
        verrouille=verrou_sd_3
    )

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_sd3 = st.checkbox("Je certifie avoir complete les questions de l'Atelier 3.", key="check_certif_sd3", disabled=verrou_sd_3)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_sd3", use_container_width=True, disabled=verrou_sd_3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_sd3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Quiz : 5 questions comptant pour 2 points chacune (Total 10 pts)
            score_q3 = 0.0
            if "ordre_quiz_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3:
                    rep_e = st.session_state.get(f"sd_t3_q_{q_item['id']}", "Choisir...")
                    if str(rep_e).strip() == str(q_item["rep"]).strip():
                        score_q3 += 2.0

            # Trous : 5 trous comptant pour 2 points chacun (Total 10 pts)
            score_t3 = sum([
                st.session_state.get("sd_t3_t1") == "alpha",
                st.session_state.get("sd_t3_t2") == "Decroissante",
                st.session_state.get("sd_t3_t3") == "Racines",
                st.session_state.get("sd_t3_t4") == "a",
                st.session_state.get("sd_t3_t5") == "beta"
            ]) * 2.0

            st.session_state.score_sd3_p1 = round(float(score_q3), 1)
            st.session_state.score_sd3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_sd3 = round(float(score_q3 + score_t3), 1)
            st.session_state.sd_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("sd_verrouille_tab3", False):
        scr1 = st.session_state.get("score_sd3_p1", 0.0)
        scr2 = st.session_state.get("score_sd3_p2", 0.0)
        tot_s = st.session_state.get("score_final_sd3", 0.0)
        
        from datetime import datetime
        timestamp_sd3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER 3 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # Initialisation HTML de l'Atelier 3 avec une couleur bordeaux / ambre distinctive
        html_export_sd3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Signes et Variations - {n_eleve}</title>
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
                <p>Atelier 3 : Tableaux de signes, extremums locaux et variations de la parabole</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_sd3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b45309;">
                - Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3, 1):
                saisie = st.session_state.get(f"sd_t3_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_sd3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_sd3 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce</th><th>Saisie</th><th>Attendu</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_3 = [
            ("1. Le sens de variation change precisement au point d'abscisse", st.session_state.get("sd_t3_t1"), "alpha"),
            ("2. Si a est positif, la fonction commence par etre", st.session_state.get("sd_t3_t2"), "Decroissante"),
            ("3. La fonction s'annule graphiquement au niveau de ses", st.session_state.get("sd_t3_t3"), "Racines"),
            ("4. Entre les racines, le signe obtenu est le signe oppose de", st.session_state.get("sd_t3_t4"), "a"),
            ("5. L'ordonnee maximale ou minimale de la courbe correspond a", st.session_state.get("sd_t3_t5"), "beta")
        ]

        for num_t, (texte_t, saisie_t, attendu_t) in enumerate(phrases_trous_3, 1):
            saisie_t = saisie_t if saisie_t else "Choisir..."
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_sd3 += f"<tr><td>{num_t}</td><td>{texte_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_sd3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL DE L'ATELIER 3 (HTML)",
            data=html_export_sd3,
            file_name=f"Rapport_Atelier3_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



with tab4:
    st.header("Application professionnelle et exercice d'evaluation")
    st.write("Selectionnez votre domaine d'activite. Un enonce unique avec des valeurs aleatoires sera genere.")

    # Selecteur de metier pour l'exercice
    metier_ex = st.selectbox(
        "Choisissez votre specialite :",
        [
            "Travaux Publics (Profil de la chaussee)",
            "Maintenance Industrielle (Cout d'exploitation)",
            "Transport Routier (Courbe de puissance)",
            "Topographe-Geometre (Implantation altimetrique)"
        ],
        key="select_metier_exercice"
    )

    # Bouton optionnel pour changer les chiffres de l'exercice libre
    if st.button("GENERER DE NOUVELLES VALEURS ALEATOIRES", key="btn_generer_aleatoire"):
        if "ex_a4" in st.session_state: del st.session_state["ex_a4"]
        if "ex_b4" in st.session_state: del st.session_state["ex_b4"]
        if "ex_c4" in st.session_state: del st.session_state["ex_c4"]
        st.rerun()

    # --- GENERATION ALEATOIRE CONTROLEE (Viete inverse pour racines propres) ---
    import random
    if "ex_a4" not in st.session_state:
        # On choisit le type d'ouverture selon le metier selectionne
        if "Travaux Publics" in metier_ex or "Maintenance" in metier_ex:
            a_gen = 0.5  # Parabole vers le haut (Minimum)
        else:
            a_gen = -0.5 # Parabole vers le bas (Maximum)
            
        # Generation de deux racines entieres distinctes cachees (ex: entre 1 et 5)
        r1_sec = float(random.randint(1, 3))
        r2_sec = float(random.randint(5, 7))
        
        # Calcul des coefficients theoriques de f(x)=0 : a(x - r1)(x - r2) = ax^2 - a(r1+r2)x + a*r1*r2
        b_gen = -a_gen * (r1_sec + r2_sec)
        c_gen = a_gen * r1_sec * r2_sec
        
        st.session_state["ex_a4"] = a_gen
        st.session_state["ex_b4"] = b_gen
        st.session_state["ex_c4"] = c_gen

    # Recuperation des valeurs de la session
    a4 = st.session_state["ex_a4"]
    b4 = st.session_state["ex_b4"]
    c4 = st.session_state["ex_c4"]

    # Attribution des labels contextuels
    if "Travaux Publics" in metier_ex:
        st.subheader("Atelier 4 : Conception d'un raccordement routier en cuvette")
        st.write("Un raccordement routier entre deux pentes est modélise par la fonction suivante, definissant l'altitude f(x) en mètres selon la distance horizontale x en mètres :")
        label_x, label_fx = "Distance x (m)", "Altitude f(x) (m)"
        type_extremum = "Minimum"
    elif "Maintenance" in metier_ex:
        st.subheader("Atelier 4 : Optimisation des couts de maintenance preventive")
        st.write("Le cout total de maintenance d'une ligne de production (en milliers d'euros) depend du temps t (en mois) ecoule entre deux révisions selon la fonction suivante :")
        label_x, label_fx = "Temps t (mois)", "Cout C(t) (k euros)"
        type_extremum = "Minimum"
    elif "Transport" in metier_ex:
        st.subheader("Atelier 4 : Rendement energetique d'un moteur de poids lourd")
        st.write("La puissance exploitable d'un moteur en fonction de son regime (divise par 1000 pour simplifier les calculs) est modélisee par la fonction suivante :")
        label_x, label_fx = "Regime N (tr/min / 1000)", "Puissance P(N) (ch)"
        type_extremum = "Maximum"
    else:
        st.subheader("Atelier 4 : Implantation topographique d'une voie ferree")
        st.write("L'altimetrie d'une voie ferree en zone valonnee est calculee par un geometre sur une portion de route selon la fonction suivante :")
        label_x, label_fx = "Distance x (m)", "Altitude Alt(x) (m)"
        type_extremum = "Maximum"

    # Affichage de l'equation genere de l'exercice
    signe_b4 = "+" if b4 >= 0 else ""
    signe_c4 = "+" if c4 >= 0 else ""
    st.latex(f"f(x) = {a4}x^2 {signe_b4} {b4}x {signe_c4} {c4}")

    # Proprietes theoriques auto-ajustees dynamiquement pour la correction automatique
    alpha4 = -b4 / (2 * a4)
    beta4 = a4 * (alpha4 ** 2) + b4 * alpha4 + c4
    somme_theorique4 = -b4 / a4
    produit_theorique4 = c4 / a4
    
    rapport4 = -beta4 / a4
    r1_theorique = alpha4 - np.sqrt(rapport4)
    r2_theorique = alpha4 + np.sqrt(rapport4)

    
    # État du verrou de l'Atelier 4
    verrou_sd_4 = st.session_state.get("sd_verrouille_tab4", False)

    # --- CREATION DE L'ARCHITECTURE EN DEUX COLONNES ---
    col_questions, col_graphique_interactif = st.columns([0.55, 0.45])

    with col_questions:
        # --- 1. TABLEAU DE VALEURS A COMPLETER ---
        st.subheader("1. Tableau de valeurs de l'exercice")
        st.write("Calculez les images de la fonction pour chaque valeur de x :")
        
        col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
        with col_v1: val_x0 = st.number_input("x = 0 :", value=0.0, step=1.0, disabled=verrou_sd_4, key="ex_v0")
        with col_v2: val_x2 = st.number_input("x = 2 :", value=0.0, step=1.0, disabled=verrou_sd_4, key="ex_v2")
        with col_v3: val_x4 = st.number_input("x = 4 :", value=0.0, step=1.0, disabled=verrou_sd_4, key="ex_v4")
        with col_v4: val_x6 = st.number_input("x = 6 :", value=0.0, step=1.0, disabled=verrou_sd_4, key="ex_v6")
        with col_v5: val_x8 = st.number_input("x = 8 :", value=0.0, step=1.0, disabled=verrou_sd_4, key="ex_v8")

        # --- 2. TABLEAU DE VARIATION A COMPLETER ---
        st.subheader("2. Tableau de variation de l'exercice")
        st.write("Renseignez la valeur de l'abscisse du changement de direction et de son extremum :")
        
        col_var1, col_var2, col_var3 = st.columns(3)
        with col_var1:
            choix_extremum = st.selectbox("Cette courbe admet un :", ["Choisir...", "Minimum", "Maximum"], disabled=verrou_sd_4, key="ex_type_ext")
        with col_var2:
            ans_alpha = st.number_input("Abscisse du sommet :", value=0.0, step=0.1, disabled=verrou_sd_4, key="ex_alpha")
        with col_var3:
            ans_beta = st.number_input("Valeur de l'extremum :", value=0.0, step=0.1, disabled=verrou_sd_4, key="ex_beta")

        # --- 3. LES RACINES ET LE TABLEAU DE SIGNE ---
        st.subheader("3. Recherche des racines et tableau de signe")
        st.write("Trouvez les valeurs ou la courbe coupe l'axe horizontal f(x) = 0 sans utiliser le discriminant :")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            ans_r1 = st.number_input("Premiere racine trouvee (la plus petite) :", value=0.0, step=0.1, disabled=verrou_sd_4, key="ex_r1")
        with col_r2:
            ans_r2 = st.number_input("Seconde racine trouvee (la plus grande) :", value=0.0, step=0.1, disabled=verrou_sd_4, key="ex_r2")

        st.write("Completez le tableau de signe du cours correspondant :")
        col_sig1, col_sig2, col_sig3 = st.columns(3)
        with col_sig1:
            ans_sig_ext = st.selectbox("Signe a l'exterieur des racines :", ["Choisir...", "+", "-"], disabled=verrou_sd_4, key="ex_sig_ext")
        with col_sig2:
            ans_sig_int = st.selectbox("Signe a l'interieur des racines :", ["Choisir...", "+", "-"], disabled=verrou_sd_4, key="ex_sig_int")
        with col_sig3:
            ans_annulation = st.selectbox("La fonction s'annule aux racines :", ["Choisir...", "Oui, f(x)=0", "Non"], disabled=verrou_sd_4, key="ex_annule")

        # --- 4. OPERATIONS SUR LES RACINES DE L'EXERCICE ---
        st.subheader("4. Verifications algebriques sur les racines de l'exercice")
        st.write("Effectuez les calculs operatoires demandes a partir de vos resultats :")
        
        col_op1, col_op2 = st.columns(2)
        with col_op1:
            ans_somme = st.number_input("Calculez la somme de vos deux racines (x1 + x2) :", value=0.0, step=0.1, disabled=verrou_sd_4, key="ex_somme")
        with col_op2:
            ans_produit = st.number_input("Calculez le produit de vos deux racines (x1 * x2) :", value=0.0, step=0.1, disabled=verrou_sd_4, key="ex_produit")

    with col_graphique_interactif:
        st.subheader("Graphique interactif d'analyse")
        st.write("Survolez ou cliquez sur la courbe avec votre souris pour reveler precisement les coordonnees (x, y) de chaque point.")
        
        # Generation des points de la parabole pour Plotly (sans marquer les reponses)
        import plotly.graph_objects as go
        
        x_plotly = np.linspace(alpha4 - 5, alpha4 + 5, 200)
        y_plotly = a4 * (x_plotly ** 2) + b4 * x_plotly + c4
        
        fig_plotly = go.Figure()
        
        # Ajout de la courbe brute
        fig_plotly.add_trace(go.Scatter(
            x=x_plotly, 
            y=y_plotly, 
            mode='lines',
            name='Courbe f(x)',
            line=dict(color='#5b21b6', width=3),
            hovertemplate='Coordonnees :<br>x = %{x:.2f}<br>y = %{y:.2f}<extra></textextra>'
        ))
        
        # Ajustement esthétique de la grille et des axes
        fig_plotly.update_layout(
            xaxis=dict(title=label_x, showgrid=True, gridcolor='lightgrey', zeroline=True, zerolinecolor='black'),
            yaxis=dict(title=label_fx, showgrid=True, gridcolor='lightgrey', zeroline=True, zerolinecolor='black'),
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            hovermode='x unified',
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_plotly, use_container_width=True)

    # --- VALIDATION ET EXPORTATION HTML ---
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_sd4 = st.checkbox("Je certifie avoir resolu l'integralite de ce cas concret.", key="check_certif_sd4", disabled=verrou_sd_4)


    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_sd4", use_container_width=True, disabled=verrou_sd_4):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_sd4:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction dynamique du tableau de valeurs (5 points, 1 pt par reponse)
            correct_v = sum([
                round(val_x0, 2) == round(c4, 2),
                round(val_x2, 2) == round(a4*(2**2) + b4*2 + c4, 2),
                round(val_x4, 2) == round(a4*(4**2) + b4*4 + c4, 2),
                round(val_x6, 2) == round(a4*(6**2) + b4*6 + c4, 2),
                round(val_x8, 2) == round(a4*(8**2) + b4*8 + c4, 2)
            ])

            # 2. Correction dynamique du tableau de variation et de l'extremum (5 points)
            correct_var = sum([
                choix_extremum == type_extremum,
                round(ans_alpha, 2) == round(alpha4, 2),
                round(ans_beta, 2) == round(beta4, 2)
            ]) * (5.0 / 3.0)

            # 3. Correction dynamique des racines et du tableau de signe (5 points, 1 pt par reponse)
            signe_ext_attendu = "+" if a4 > 0 else "-"
            signe_int_attendu = "-" if a4 > 0 else "+"
            correct_signe = sum([
                round(ans_r1, 2) == round(r1_theorique, 2),
                round(ans_r2, 2) == round(r2_theorique, 2),
                ans_sig_ext == signe_ext_attendu,
                ans_sig_int == signe_int_attendu,
                ans_annulation == "Oui, f(x)=0"
            ])

            # 4. Correction dynamique des operations sur les racines de Viete (5 points, 2.5 pts par reponse)
            correct_op = sum([
                round(ans_somme, 2) == round(somme_theorique4, 2),
                round(ans_produit, 2) == round(produit_theorique4, 2)
            ]) * 2.5

            # Enregistrement des notes recalculees dans la session de l'eleve
            st.session_state.score_sd4_p1 = round(float(correct_v), 1)
            st.session_state.score_sd4_p2 = round(float(correct_var), 1)
            st.session_state.score_sd4_p3 = round(float(correct_signe), 1)
            st.session_state.score_sd4_p4 = round(float(correct_op), 1)
            st.session_state.score_final_sd4 = round(float(correct_v + correct_var + correct_signe + correct_op), 1)
            st.session_state.sd_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("sd_verrouille_tab4", False):
        s1 = st.session_state.get("score_sd4_p1", 0.0)
        s2 = st.session_state.get("score_sd4_p2", 0.0)
        s3 = st.session_state.get("score_sd4_p3", 0.0)
        s4 = st.session_state.get("score_sd4_p4", 0.0)
        tot_s4 = st.session_state.get("score_final_sd4", 0.0)
        
        from datetime import datetime
        timestamp_sd4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER 4 EVALUATION SCELLÉ | Note finale de session : {tot_s4:.1f} / 20")

        # --- CALCUL DES COMPOSANTS ATTENDUS POUR LA TABLE DE CORRECTION ---
        img_x0 = c4
        img_x4 = a4*(4**2) + b4*4 + c4
        
        import io
        import base64
        
        x_img = np.linspace(alpha4 - 5, alpha4 + 5, 400)
        y_img = a4 * (x_img ** 2) + b4 * x_img + c4
        
        fig_img, ax_img = plt.subplots(figsize=(6, 3.5))
        ax_img.plot(x_img, y_img, color="#5b21b6", linewidth=2, label="Courbe metier f(x)")
        ax_img.scatter(alpha4, beta4, color="red", s=80, zorder=5, label=f"Sommet S ({alpha4:.1f};{beta4:.1f})")
        ax_img.scatter([r1_theorique, r2_theorique], [0, 0], color="green", marker="x", s=80, zorder=5, label="Racines")
        ax_img.axhline(0, color='black', linewidth=0.6, linestyle='--')
        ax_img.axvline(0, color='black', linewidth=0.6, linestyle='--')
        ax_img.grid(True, linestyle=':', alpha=0.5)
        ax_img.legend(loc="upper right", fontsize='small')
        
        buf = io.BytesIO()
        fig_img.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        base64_graph = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig_img)

        # --- DEFINITION DES VALEURS ATTENDUES MANQUANTES ---
        img_x0 = float(c4)
        img_x2 = float(a4 * (2 ** 2) + b4 * 2 + c4)
        img_x4 = float(beta4)
        img_x6 = float(a4 * (6 ** 2) + b4 * 6 + c4)
        img_x8 = float(a4 * (8 ** 2) + b4 * 8 + c4)
        
        signe_ext_attendu = "+" if a4 > 0 else "-"
        signe_int_attendu = "-" if a4 > 0 else "+"

        # --- DÉFINITION DES VERDICTS POUR TOUTES LES QUESTIONS ---
        v_v0 = "CORRECT" if round(val_x0, 2) == round(img_x0, 2) else "INCORRECT"
        v_v2 = "CORRECT" if round(val_x2, 2) == round(img_x2, 2) else "INCORRECT"
        v_v4 = "CORRECT" if round(val_x4, 2) == round(img_x4, 2) else "INCORRECT"
        v_v6 = "CORRECT" if round(val_x6, 2) == round(img_x6, 2) else "INCORRECT"
        v_v8 = "CORRECT" if round(val_x8, 2) == round(img_x8, 2) else "INCORRECT"
        
        v_type = "CORRECT" if choix_extremum == type_extremum else "INCORRECT"
        v_alpha = "CORRECT" if round(ans_alpha, 2) == round(alpha4, 2) else "INCORRECT"
        v_beta = "CORRECT" if round(ans_beta, 2) == round(beta4, 2) else "INCORRECT"
        
        v_r1 = "CORRECT" if round(ans_r1, 2) == round(r1_theorique, 2) else "INCORRECT"
        v_r2 = "CORRECT" if round(ans_r2, 2) == round(r2_theorique, 2) else "INCORRECT"
        v_sext = "CORRECT" if ans_sig_ext == signe_ext_attendu else "INCORRECT"
        v_sint = "CORRECT" if ans_sig_int == signe_int_attendu else "INCORRECT"
        v_annul = "CORRECT" if ans_annulation == "Oui, f(x)=0" else "INCORRECT"
        
        v_somme = "CORRECT" if round(ans_somme, 2) == round(somme_theorique4, 2) else "INCORRECT"
        v_produit = "CORRECT" if round(ans_produit, 2) == round(produit_theorique4, 2) else "INCORRECT"
        # --- INITIALISATION DU RAPPORT HTML DETAILLÉ ---

        from datetime import datetime
        timestamp_sd4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        s1 = st.session_state.get("score_sd4_p1", 0.0)
        s2 = st.session_state.get("score_sd4_p2", 0.0)
        s3 = st.session_state.get("score_sd4_p3", 0.0)
        s4 = st.session_state.get("score_sd4_p4", 0.0)
        tot_s4 = st.session_state.get("score_final_sd4", 0.0)
        # --- INITIALISATION DU RAPPORT HTML DETAILLÉ ---
        html_export_sd4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier Concret - {n_eleve}</title>
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
                <p>Atelier 4 : Evaluation finale et application contextuelle sur dossier metier</p>
                <p>Metier evalue : {metier_ex}</p>
                <p>Equation attribuee : f(x) = {a4}x&sup2; + ({b4})x + ({c4})</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_sd4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Detail des competences verifiees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #5b21b6;">
                - Resolution du tableau de valeurs : <strong>{s1:.1f} / 5</strong><br>
                - Analyse du tableau de variation et extremums : <strong>{s2:.1f} / 5</strong><br>
                - Calcul des racines et du tableau de signe : <strong>{s3:.1f} / 5</strong><br>
                - Operations sur la somme et le produit de Viete : <strong>{s4:.1f} / 5</strong>
            </p>

            <div class="sub-title">Synthese complete, questions posees et corrections academiques</div>
            <table>
                <thead>
                    <tr><th>Question / Champ Posé</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <!-- 1. TABLEAU DE VALEURS -->
                    <tr><td><b>1.1</b> Image pour x = 0</td><td>{val_x0:.2f}</td><td>{c4:.2f}</td><td class="{'status-correct' if v_v0 == 'CORRECT' else 'status-incorrect'}">{v_v0}</td></tr>
                    <tr><td><b>1.2</b> Image pour x = 2</td><td>{val_x2:.2f}</td><td>{img_x2:.2f}</td><td class="{'status-correct' if v_v2 == 'CORRECT' else 'status-incorrect'}">{v_v2}</td></tr>
                    <tr><td><b>1.3</b> Image pour x = 4 (Sommet)</td><td>{val_x4:.2f}</td><td>{img_x4:.2f}</td><td class="{'status-correct' if v_v4 == 'CORRECT' else 'status-incorrect'}">{v_v4}</td></tr>
                    <tr><td><b>1.4</b> Image pour x = 6</td><td>{val_x6:.2f}</td><td>{img_x6:.2f}</td><td class="{'status-correct' if v_v6 == 'CORRECT' else 'status-incorrect'}">{v_v6}</td></tr>
                    <tr><td><b>1.5</b> Image pour x = 8</td><td>{val_x8:.2f}</td><td>{img_x8:.2f}</td><td class="{'status-correct' if v_v8 == 'CORRECT' else 'status-incorrect'}">{v_v8}</td></tr>
                    
                    <!-- 2. TABLEAU DE VARIATION -->
                    <tr><td><b>2.1</b> Nature de l'extremum (Max ou Min)</td><td>{choix_extremum}</td><td>{type_extremum}</td><td class="{'status-correct' if v_type == 'CORRECT' else 'status-incorrect'}">{v_type}</td></tr>
                    <tr><td><b>2.2</b> Abscisse du sommet (&alpha; = -b/2a)</td><td>{ans_alpha:.2f}</td><td>{alpha4:.2f}</td><td class="{'status-correct' if v_alpha == 'CORRECT' else 'status-incorrect'}">{v_alpha}</td></tr>
                    <tr><td><b>2.3</b> Ordonnee du sommet / extremum (&beta;)</td><td>{ans_beta:.2f}</td><td>{beta4:.2f}</td><td class="{'status-correct' if v_beta == 'CORRECT' else 'status-incorrect'}">{v_beta}</td></tr>
                    
                    <!-- 3. RACINES ET TABLEAU DE SIGNE -->
                    <tr><td><b>3.1</b> Premiere racine reelle trouvee (x1)</td><td>{ans_r1:.2f}</td><td>{r1_theorique:.2f}</td><td class="{'status-correct' if v_r1 == 'CORRECT' else 'status-incorrect'}">{v_r1}</td></tr>
                    <tr><td><b>3.2</b> Seconde racine reelle trouvee (x2)</td><td>{ans_r2:.2f}</td><td>{r2_theorique:.2f}</td><td class="{'status-correct' if v_r2 == 'CORRECT' else 'status-incorrect'}">{v_r2}</td></tr>
                    <tr><td><b>3.3</b> Signe a l'exterieur des racines (signe de a)</td><td>{ans_sig_ext}</td><td>{signe_ext_attendu}</td><td class="{'status-correct' if v_sext == 'CORRECT' else 'status-incorrect'}">{v_sext}</td></tr>
                    <tr><td><b>3.4</b> Signe a l'interieur des racines (signe de -a)</td><td>{ans_sig_int}</td><td>{signe_int_attendu}</td><td class="{'status-correct' if v_sint == 'CORRECT' else 'status-incorrect'}">{v_sint}</td></tr>
                    <tr><td><b>3.5</b> Est-ce que f(x) s'annule aux racines ?</td><td>{ans_annulation}</td><td>Oui, f(x)=0</td><td class="{'status-correct' if v_annul == 'CORRECT' else 'status-incorrect'}">{v_annul}</td></tr>
                    
                    <!-- 4. OPERATIONS SUR LES RACINES -->
                    <tr><td><b>4.1</b> Calcul de la somme operatoire (x1 + x2)</td><td>{ans_somme:.2f}</td><td>{somme_theorique4:.2f}</td><td class="{'status-correct' if v_somme == 'CORRECT' else 'status-incorrect'}">{v_somme}</td></tr>
                    <tr><td><b>4.2</b> Calcul du produit operatoire (x1 &times; x2)</td><td>{ans_produit:.2f}</td><td>{produit_theorique4:.2f}</td><td class="{'status-correct' if v_produit == 'CORRECT' else 'status-incorrect'}">{v_produit}</td></tr>
                </tbody>
            </table>

            <div class="sub-title">Visualisation Graphique de Correction</div>
            <div class="graph-container">
                <img src="data:image/png;base64,{base64_graph}" alt="Graphique de Correction" style="max-width: 100%; height: auto; border: 1px solid #cbd5e1; border-radius: 4px;"/>
            </div>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL D'EVALUATION METIER (HTML)",
            data=html_export_sd4,
            file_name=f"Rapport_Atelier4_Evaluation_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


























