# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="TP hydrostatique et hydrodynamique",
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
st.title("TP hydrostatique et hydrodynamique ")
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
    "Conservation du débit 1", 
    "Conservation du débit 2",
    "Bernouilli 1 ",
    "Bernouilli 2",
    "Bernouilli 3 (perte de charge)",
    "Torricelli (vidange)",
    "Circuit hydraulique ",
    "Barrage hydraulique"
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
tab9 = onglets[9]


def afficher_questions_engin_tp(force_verin_kn, s_piston_m2, s_tige_m2, var_pression_engin, limite_sol_kn, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_hydro3" not in st.session_state:
        # Configuration des diagnostics textuels pour les réponses dynamiques
        val_f_poussee = f"{(var_pression_engin * 100000.0 * s_piston_m2) / 1000.0:.0f}"
        val_sol_res = f"{limite_sol_kn:.0f}"
        val_reussite = "Oui" if (var_pression_engin * 100000.0 * s_piston_m2 / 1000.0) >= limite_sol_kn else "Non"

        base_quiz_hydro3 = [
            {"id": "h3_1", "q": "Quel element mecanique recepteur convertit la puissance hydraulique en force rectiligne ?", "options": ["Verin", "Pompe", "Moteur"], "rep": "Verin"},
            {"id": "h3_2", "q": "D'apres vos curseurs actuels, calculez la surface complete du piston S1 en cm² (arrondie au dixieme) :", "options": [f"{s_piston_m2 * 10000.0:.1f}", f"{s_piston_m2 * 100.0:.1f}", f"{s_piston_m2 * 1000.0:.1f}"], "rep": f"{s_piston_m2 * 10000.0:.1f}"},
            {"id": "h3_3", "q": "D'apres vos curseurs actuels, calculez la surface reduite cote tige S2 en cm² (arrondie au dixieme) :", "options": [f"{s_tige_m2 * 10000.0:.1f}", f"{s_tige_m2 * 100.0:.1f}", f"{s_tige_m2 * 1000.0:.1f}"], "rep": f"{s_tige_m2 * 10000.0:.1f}"},
            {"id": "h3_4", "q": "Lequel developpe la plus grande force mecanique a pression strictement identique ?", "options": ["Poussee", "Traction", "Egalite"], "rep": "Poussee"},
            {"id": "h3_5", "q": "Quel appareil de distribution a tiroir pilote l'inversion du fluide vers le verin de la fleche ?", "options": ["4/2", "3/2", "2/2"], "rep": "4/2"},
            {"id": "h3_6", "q": "Indiquez la valeur numerique du rapport multiplicateur des surfaces de session (S1/S2) :", "options": [f"{s_piston_m2 / s_tige_m2:.1f}", f"{s_tige_m2 / s_piston_m2:.1f}", "1.0"], "rep": f"{s_piston_m2 / s_tige_m2:.1f}"},
            {"id": "h3_7", "q": "Quel organe hydraulique de securite s'ouvre si la pression depasse le seuil maximum ?", "options": ["Limiteur", "Clapet", "Filtre"], "rep": "Limiteur"},
            {"id": "h3_8", "q": "Quelle est la valeur de la force theorique de pousse du verin calculee sous vos reglages actuel (kN) ?", "options": [val_f_poussee, f"{float(val_f_poussee)*1.5:.0f}", f"{float(val_f_poussee)/2:.0f}"], "rep": val_f_poussee},
            {"id": "h3_9", "q": "Quel est le seuil nominal de resistance a l'avancement oppose par le type de terrain selectionne (kN) ?", "options": [val_sol_res, "10", "100"], "rep": val_sol_res},
            {"id": "h3_10", "q": "La force reelle developpee par le verin de l'engin est-elle suffisante pour vaincre l'obstacle du sol ?", "options": ["Oui", "Non"], "rep": val_reussite}
        ]
        copie_base = list(base_quiz_hydro3)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_hydro3 = copie_base

    col_q3, col_t3 = st.columns(2)

    with col_q3:
        st.markdown("##### Quiz sur les circuits de puissance (10 questions - 10 pts)")
        dict_rep_q3 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_hydro3, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_t3_q_{q_data['id']}"
            cle_opts = f"opts_hydro3_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q3[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t3:
        st.markdown("##### Synthese de cours a trous (10 trous - 10 pts)")
        dict_trous_3 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le deplacement de la tige de verin est directement proportionnel au")
        with c2: dict_trous_3["t1"] = st.selectbox("", ["Choisir...", "Debit", "Pression", "Volume"], key="hydro_t3_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La force developpee mecaniquement par un verin depend de sa")
        with c4: dict_trous_3["t2"] = st.selectbox("", ["Choisir...", "Surface", "Vitesse", "Longueur"], key="hydro_t3_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Les fuites internes qui traversent le piston d'un verin decrivent un")
        with c6: dict_trous_3["t3"] = st.selectbox("", ["Choisir...", "Bypass", "Circuit", "Blocage"], key="hydro_t3_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Si le verin depasse la charge max, le fluide s'echappe par le limiteur de")
        with c8: dict_trous_3["t4"] = st.selectbox("", ["Choisir...", "Pression", "Debit", "Vitesse"], key="hydro_t3_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La puissance utile de sortie de la tige associe sa force active et sa")
        with c10: dict_trous_3["t5"] = st.selectbox("", ["Choisir...", "Vitesse", "Course", "Masse"], key="hydro_t3_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Un fluide sous contrainte de charge cherche la zone de plus faible")
        with c12: dict_trous_3["t6"] = st.selectbox("", ["Choisir...", "Resistance", "Pression", "Hauteur"], key="hydro_t3_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La deperdition energetique par frottements visqueux est une perte de")
        with c14: dict_trous_3["t7"] = st.selectbox("", ["Choisir...", "Charge", "Debit", "Vitesse"], key="hydro_t3_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. En hydrostatique, les huiles minerales sont considerees comme")
        with c16: dict_trous_3["t8"] = st.selectbox("", ["Choisir...", "Incompressibles", "Compressibles", "Gazeuses"], key="hydro_t3_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La reduction de section au sein d'une conduite entraine l'essor de la")
        with r18: dict_trous_3["t9"] = st.selectbox("", ["Choisir...", "Vitesse", "Masse", "Charge"], key="hydro_t3_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. L'evacuation finale de l'huile usagee non contrainte s'effectue vers le")
        with c20: dict_trous_3["t10"] = st.selectbox("", ["Choisir...", "Reservoir", "Verin", "Distributeur"], key="hydro_t3_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q3, dict_trous_3



def afficher_questions_hydrodynamiques(v_a, v_b, v_ej, p_r, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_hydro2" not in st.session_state:
        base_cat_qcm = [
            {"id": "hd1", "q": "Lorsque la section d'un tube fluide diminue, la vitesse de l'eau :", "options": ["Augmenter", "Diminuer", "Stagner"], "rep": "Augmenter"},
            {"id": "hd2", "q": "D'apres l'enonce de votre session, calculez la vitesse d'entree VA (m/s) :", "options": [f"{v_a:.2f}", f"{v_a*10:.2f}", f"{v_a/10:.2f}"], "rep": f"{v_a:.2f}"},
            {"id": "hd3", "q": "D'apres l'enonce de votre session, calculez la vitesse de sortie VB (m/s) :", "options": [f"{v_b:.2f}", f"{v_b*10:.2f}", f"{v_b/10:.2f}"], "rep": f"{v_b:.2f}"},
            {"id": "hd4", "q": "Le phenomene d'acceleration d'un fluide associe a une baisse de pression s'appelle l'effet :", "options": ["Venturi", "Bernoulli", "Pascal"], "rep": "Venturi"},
            {"id": "hd5", "q": "Indiquez la valeur numerique exacte de la vitesse d'ejection de la lance de pompier (m/s) :", "options": [f"{v_ej:.2f}", f"{v_ej*2:.2f}", f"{v_ej/2:.2f}"], "rep": f"{v_ej:.2f}"},
            {"id": "hd6", "q": "Comment evolue la pression statique dans le goulet d'etranglement du Venturi ?", "options": ["Diminuer", "Augmenter", "Stagner"], "rep": "Diminuer"},
            {"id": "hd7", "q": "Quel theoreme energetique fonde la relation entre vitesse et pression dans un ecoulement ?", "options": ["Bernoulli", "Pascal", "Torricelli"], "rep": "Bernoulli"},
            {"id": "hd8", "q": "Calculez la portee horizontale maximum du jet de la lance de pompier (metres) :", "options": [f"{p_r:.1f}", f"{p_r+10:.1f}", f"{p_r-10:.1f}"], "rep": f"{p_r:.1f}"},
            {"id": "hd9", "q": "Quel type de regime fluide considere que les lignes de courant sont stables et paralleles ?", "options": ["Laminaire", "Turbulent", "Transitoire"], "rep": "Laminaire"},
            {"id": "hd10", "q": "Le produit algebrique de la section S par la vitesse moyenne V definit le :", "options": ["Debit", "Volume", "Flux_massique"], "rep": "Debit"},
            {"id": "hd11", "q": "Si la section droite d'une canalisation est divisee par deux, la vitesse du fluide est :", "options": ["Doublee", "Divisee_par_deux", "Quadruplee"], "rep": "Doublee"},
            {"id": "hd12", "q": "Les pertes d'energie d'un fluide liees aux frottements visqueux sont les pertes de :", "options": ["Charge", "Debit", "Pression"], "rep": "Charge"},
            {"id": "hd13", "q": "Quelle est l'unite de mesure standard du debit volumique dans le systeme international ?", "options": ["m3/s", "L/s", "L/min"], "rep": "m3/s"},
            {"id": "hd14", "q": "La trajectoire geometrique decrite par l'eau s'echappant de la lance est une :", "options": ["Parabole", "Droite", "Hyperbole"], "rep": "Parabole"},
            {"id": "hd15", "q": "Le fluide etudie ici est suppose ideal, sa viscosite est consideree comme :", "options": ["Nulle", "Infinie", "Constante"], "rep": "Nulle"}
        ]
        
        base_cat_trous = [
            {"id": "hdt1", "q": "1. L'equation de continuite technique exprime que le debit volumique d'un fluide incompressible reste", "options": ["Constant", "Variable", "Nul"], "rep": "Constant"},
            {"id": "hdt2", "q": "2. Pour un fluide parfait, la somme des pressions statique, dynamique et de pesanteur est une grandeur", "options": ["Conservatrice", "Evolutive", "Nulle"], "rep": "Conservatrice"},
            {"id": "hdt3", "q": "3. L'acceleration du fluide au passage d'un etranglement convergent resulte de la conservation de la", "options": ["Masse", "Vitesse", "Force"], "rep": "Masse"},
            {"id": "hdt4", "q": "4. Lorsque la vitesse d'ejection augmente, la portee horizontale ballistique du jet se trouve", "options": ["Allongee", "Raccourcie", "Inchangee"], "rep": "Allongee"},
            {"id": "hdt5", "q": "5. Les tourbillons desordonnes au sein d'un ecoulement caracterisent le regime dit", "options": ["Turbulent", "Laminaire", "Stable"], "rep": "Turbulent"},
            {"id": "hdt6", "q": "6. La loi de Bernoulli constitue l'expression de la conservation de l'energie appliquee aux", "options": ["Fluides", "Solides", "Gaz"], "rep": "Fluides"},
            {"id": "hdt7", "q": "7. Un tube convergent possede une section d'entree superieure a sa section de", "options": ["Sortie", "Col", "Pente"], "rep": "Sortie"},
            {"id": "hdt8", "q": "8. Le nombre adimensionnel utilise pour determiner le type de regime est le nombre de", "options": ["Reynolds", "Froude", "Nusselt"], "rep": "Reynolds"},
            {"id": "hdt9", "q": "9. Une buse de lance de pompier convertit la pression en energie", "options": ["Cinetique", "Potentielle", "Thermique"], "rep": "Cinetique"},
            {"id": "hdt10", "q": "10. En l'absence de frottement, l'eau s'ejecte de la buse selon un mouvement rectiligne", "options": ["Uniforme", "Accelere", "Decelere"], "rep": "Uniforme"},
            {"id": "hdt11", "q": "11. L'etranglement minimal situe au centre d'un tube Venturi se nomme le", "options": ["Col", "Goulet", "Sifflet"], "rep": "Col"},
            {"id": "hdt12", "q": "12. La vitesse d'ecoulement d'un liquide est inversement proportionnelle a l'aire de sa", "options": ["Section", "Longueur", "Hauteur"], "rep": "Section"},
            {"id": "hdt13", "q": "13. L'action de la gravite incurve la trajectoire de l'eau vers le", "options": ["Sol", "Ciel", "Camion"], "rep": "Sol"},
            {"id": "hdt14", "q": "14. La viscosite dynamique traduit la resistance interne d'un fluide a l'", "options": ["Ecoulement", "Compression", "Surchauffe"], "rep": "Ecoulement"},
            {"id": "hdt15", "q": "15. Le debit massique s'obtient en multipliant le debit volumique par la masse", "options": ["Volumique", "Molaire", "Totale"], "rep": "Volumique"}
        ]
        
        # Tirage aleatoire stable de 10 questions parmi les 15 de chaque catalogue
        st.session_state.ordre_qcm_hydro2 = random.sample(base_cat_qcm, 10)
        st.session_state.ordre_trous_hydro2 = random.sample(base_cat_trous, 10)

    col_q2, col_t2 = st.columns(2)

    with col_q2:
        st.markdown("##### Quiz d'analyse technologique (10 questions - 10 pts)")
        dict_rep_q2 = {}
        for idx, q_data in enumerate(st.session_state.ordre_qcm_hydro2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_t2_q_{q_data['id']}"
            cle_opts = f"opts_hydro2_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q2[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t2:
        st.markdown("##### Synthese de cours a trous (10 trous - 10 pts)")
        dict_trous_2 = {}
        for idx, q_data in enumerate(st.session_state.ordre_trous_hydro2, 1):
            c_text, col_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_text:
                st.write(f"{idx}. {q_data['q']}")
            cle_select_t = f"hydro_t2_t_{q_data['id']}"
            cle_opts_t = f"opts_trous2_{q_data['id']}"
            if cle_opts_t not in st.session_state:
                opts_t = list(q_data["options"])
                random.shuffle(opts_t)
                st.session_state[cle_opts_t] = ["Choisir..."] + opts_t
            val_p_t = st.session_state.get(cle_select_t, "Choisir...")
            sel_idx_t = st.session_state[cle_opts_t].index(val_p_t) if val_p_t in st.session_state[cle_opts_t] else 0
            with col_sel:
                dict_trous_2[q_data["id"]] = st.selectbox("", st.session_state[cle_opts_t], index=sel_idx_t, key=cle_select_t, disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q2, dict_trous_2


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
    

        st.markdown("**1. Modele Physique Theorique**")
        fig1, ax1 = plt.subplots(figsize=(3, 3), dpi=100)
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
            

        st.markdown("**2. Application Industrielle : Pont Elevateur**")
        if "Normal" in mode_selectionne:
            if pression_suffisante: 
                st.success("Pression suffisante : Pret pour le levage")
            else: 
                st.error("Pression insuffisante : Levage impossible")
        
        fig2, ax2 = plt.subplots(figsize=(3, 3), dpi=100)
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


with tab2:
    st.header("Hydrodynamique et conservation du debit")
    st.write("Analyse de l'effet Venturi dans un tube convergent et application industrielle au defi d'extinction de la lance de pompier.")

    # =====================================================================
    # --- INITIALISATION STABLE DE LA SESSION DE TRAVAIL ---
    # =====================================================================
    if "session_initialisee_tab2" not in st.session_state:
        st.session_state.session_initialisee_tab2 = True
        st.session_state.eval_q1 = float(random.randint(10, 30)) if 'random' in locals() else 15.0
        st.session_state.eval_qlance = float(random.randint(400, 800)) if 'random' in locals() else 500.0

    # Choix du mode de fonctionnement pour l'Atelier 2
    mode_selectionne_tab2 = st.radio(
        "Mode de fonctionnement de l'Atelier 2 :",
        ["Mode Normal (Libre)", "Mode Evaluation (Aleatoire)"],
        key="radio_mode_tab2"
    )
    
    st.markdown("---")

    # =====================================================================
    # --- DESTRUCTURATION ET DISTRIBUTION DES DEUX COLONNES WEB ---
    # =====================================================================
    st.subheader("Configuration de session")
    col_gauche_t2, col_droite_t2 = st.columns(2)

    # =====================================================================
    # --- COLONNE GAUCHE : MODULE TUBE CONVERGENT ---
    # =====================================================================
    with col_gauche_t2:
        if "Normal" in mode_selectionne_tab2:
            st.markdown("##### 1. Tube Convergent ")
            var_debit_theorie = st.slider("Débit de l'eau Q1 (L/s) :", min_value=1, max_value=50, value=5, step=1, key="slide_q1_t2")
            scale_da = st.slider("Diametre Entree DA (cm) :", min_value=1.0, max_value=50.0, value=15.0, step=0.1, key="slide_da_t2")
            scale_db = st.slider("Diametre Sortie DB (cm) :", min_value=1.0, max_value=50.0, value=6.0, step=0.1, key="slide_db_t2")
        else:
            st.info("Parametres d'examen imposes de l'Atelier 2")
            var_debit_theorie = st.session_state.eval_q1
            scale_da = 15.0
            scale_db = 6.0
            st.markdown(f"* **Débit theorique du tube Q1 :** {var_debit_theorie:.0f} L/s")
            st.markdown(f"* **Diametre nominal d'entree DA :** {scale_da:.1f} cm")
            st.markdown(f"* **Diametre nominal de sortie DB :** {scale_db:.1f} cm")

        # Calculs et équations hydrodynamiques du tube
        q_m3s = var_debit_theorie / 1000.0
        s_a_m2 = np.pi * ((scale_da / 100.0) / 2.0)**2
        s_b_m2 = np.pi * ((scale_db / 100.0) / 2.0)**2
        v_a = q_m3s / s_a_m2 if s_a_m2 > 0 else 0
        v_b = q_m3s / s_b_m2 if s_b_m2 > 0 else 0

        st.markdown("**1. Conservation du Debit (Tube convergent)**")
        if "billes_hydro_tab2" not in st.session_state:
            st.session_state.billes_hydro_tab2 = [i * (100.0 / 25.0) for i in range(25)]
            
        vitesse_globale = max(0.2, var_debit_theorie * 0.15)
        st.session_state.billes_hydro_tab2 = [(t + vitesse_globale) % 100.0 for t in st.session_state.billes_hydro_tab2]
        
        fig_tube, ax_tube = plt.subplots(figsize=(4.5, 3.5), dpi=100)
        ax_tube.clear()
        
        w_c1 = 450.0
        h_c1 = 200.0
        y_milieu = h_c1 / 2.0
        h_a_px = max(10.0, scale_da * 1.8)
        h_b_px = max(10.0, scale_db * 1.8)
        x_debut_pente = 200.0  
        x_fin_pente = 260.0    

        px_tube = [0.0, x_debut_pente, x_fin_pente, w_c1, w_c1, x_fin_pente, x_debut_pente, 0.0]
        py_tube = [
            y_milieu - h_a_px, y_milieu - h_a_px, y_milieu - h_b_px, y_milieu - h_b_px,
            y_milieu + h_b_px, y_milieu + h_b_px, y_milieu + h_a_px, y_milieu + h_a_px
        ]
        ax_tube.fill(px_tube, py_tube, color="#bae6fd", edgecolor="#0284c7", linewidth=2, zorder=1)

        x_fin_va = 50.0 + max(10.0, min(130.0, v_a * 30.0))
        ax_tube.arrow(50.0, y_milieu, x_fin_va - 50.0, 0.0, head_width=6.0, head_length=10.0, fc="#ef4444", ec="#ef4444", linewidth=2, zorder=4)
        ax_tube.text(70.0, y_milieu - h_a_px - 10.0, f"VA = {v_a:.2f} m/s", color="#ef4444", fontname="Arial", fontsize=8, fontweight="bold", zorder=5)

        x_fin_vb = (x_fin_pente + 20.0) + max(15.0, min(140.0, v_b * 30.0))
        ax_tube.arrow(x_fin_pente + 20.0, y_milieu, x_fin_vb - (x_fin_pente + 20.0), 0.0, head_width=6.0, head_length=10.0, fc="#ef4444", ec="#ef4444", linewidth=2, zorder=4)
        ax_tube.text(x_fin_pente + 30.0, y_milieu - h_b_px - 10.0, f"VB = {v_b:.2f} m/s", color="#ef4444", fontname="Arial", fontsize=8, fontweight="bold", zorder=5)

        for t_bille in st.session_state.billes_hydro_tab2:
            if t_bille < 60.0:
                fraction = t_bille / 60.0
                x_goutte = fraction * x_debut_pente
            elif 60.0 <= t_bille < 70.0:
                fraction = (t_bille - 60.0) / 10.0
                x_goutte = x_debut_pente + (fraction * (x_fin_pente - x_debut_pente))
            else:
                fraction = (t_bille - 70.0) / 30.0
                x_goutte = x_fin_pente + (fraction * (w_c1 - x_fin_pente))

            for ligne in [-12.0, 0.0, 12.0]:
                if x_goutte < x_debut_pente:
                    y_goutte = y_milieu + (ligne * (h_a_px / 40.0))
                    r_goutte = 3.5
                elif x_debut_pente <= x_goutte < x_fin_pente:
                    fraction_h = (x_goutte - x_debut_pente) / (x_fin_pente - x_debut_pente)
                    h_intermediaire = h_a_px - (fraction_h * (h_a_px - h_b_px))
                    y_goutte = y_milieu + (ligne * (h_intermediaire / 40.0))
                    r_goutte = 3.5 - (fraction_h * 1.5)
                else:
                    y_goutte = y_milieu + (ligne * (h_b_px / 40.0))
                    r_goutte = 2.0

                if x_goutte < w_c1:
                    ax_tube.plot([x_goutte], [y_goutte], marker="o", color="#0284c7", markersize=r_goutte*1.5, markeredgecolor="#0369a1", markeredgewidth=0.5, zorder=3)

        ax_tube.set_xlim(-5.0, w_c1 + 5.0)
        ax_tube.set_ylim(-10.0, h_c1 + 10.0)
        ax_tube.axis("off")
        st.pyplot(fig_tube)
        plt.close(fig_tube)
        
        st.info(
            f"Equation de Continuite :\n\n"
            f" * Debit impose Q : {var_debit_theorie:.1f} L/s\n"
            f" * Section A : {s_a_m2*10000.0:.1f} cm²\n"
            f" * Section B : {s_b_m2*10000.0:.1f} cm²\n"
            f" * Rapport des aires : x{s_a_m2/s_b_m2:.1f}\n\n"
            f"Constat : L'eau est acceleree d'un facteur x{v_b/v_a:.1f}."
        )

    # =====================================================================
    # --- COLONNE DROITE : MODULE LANCE DE POMPIER ---
    # =====================================================================
    with col_droite_t2:    
        if "Normal" in mode_selectionne_tab2:
            st.markdown("##### 2. Defi Lance de Pompier ")
            var_debit_pompier = st.slider("Débit de la lance Q_lance (L/s) :", min_value=1, max_value=2000, value=800, step=10, key="slide_qlance_t2")
            scale_db_pompier = st.slider("Diametre de la buse D_buse (cm) :", min_value=0.1, max_value=50.0, value=4.5, step=0.1, key="slide_dbuse_t2")
            scale_distance_feu = st.slider("Distance de l'incendie d (m) :", min_value=5, max_value=100, value=25, step=1, key="slide_dist_t2")
        else:
            var_debit_pompier = st.session_state.eval_qlance
            scale_db_pompier = 4.5
            scale_distance_feu = 25
            st.markdown(f"* **Débit force de la lance Q_lance :** {var_debit_pompier:.0f} L/s")
            st.markdown(f"* **Diametre de la buse d'ejection D_buse :** {scale_db_pompier:.1f} cm")
            st.markdown(f"* **Distance d'intervention cible d :** {scale_distance_feu} m")

        st.markdown("**2. Application : Lance de Pompier (Defi d'extinction)**")
        
        # Moteur de calcul balistique isolé avec suffixe unique _pomp
        q_m3s_pomp = (float(var_debit_pompier) / 1000.0)
        s_b_m2_pomp = np.pi * ((float(scale_db_pompier) / 100.0) / 2.0)**2
        v_b_pomp = q_m3s_pomp / s_b_m2_pomp if s_b_m2_pomp > 0 else 0

        # Application stricte de votre formule de portee reelle d'origine
        portee_reelle_m = (v_b_pomp ** 1.4) * 0.22
        pixel_par_metre = 7.0
        
        w_c2 = 450.0
        h_c2 = 205.0
        y_sol = 165.0
        x_lance = 120.0 
        y_lance = y_sol - 45.0
        
        x_feu = x_lance + (scale_distance_feu * pixel_par_metre)
        x_impact_jet = x_lance + (portee_reelle_m * pixel_par_metre)

        fig_pomp, ax_pomp = plt.subplots(figsize=(6, 2.73), dpi=100)
        ax_pomp.clear()
        
        y_sol_plt = h_c2 - y_sol
        y_lance_plt = h_c2 - y_lance

        # 1. Ciel et Pelouse (Sans double virgule)
        ax_pomp.fill_between([0, w_c2], [y_sol_plt, y_sol_plt], [h_c2, h_c2], color="#f0fdfa", zorder=1)
        ax_pomp.fill_between([0, w_c2], 0, [y_sol_plt, y_sol_plt], color="#15803d", zorder=2)
        
        # 2. Camion de Pompier Rouge
        ax_pomp.fill_between([20.0, 110.0], [h_c2 - (y_sol - 5.0), h_c2 - (y_sol - 5.0)], [h_c2 - (y_sol - 40.0), h_c2 - (y_sol - 40.0)], color="#dc2626", edgecolor="#991b1b", linewidth=1.5, zorder=3)
        ax_pomp.fill_between([85.0, 110.0], [h_c2 - (y_sol - 15.0), h_c2 - (y_sol - 15.0)], [h_c2 - (y_sol - 40.0), h_c2 - (y_sol - 40.0)], color="#eff6ff", edgecolor="#dc2626", linewidth=1, zorder=4)
        ax_pomp.fill_between([40.0, 48.0], [h_c2 - (y_sol - 40.0), h_c2 - (y_sol - 40.0)], [h_c2 - (y_sol - 45.0), h_c2 - (y_sol - 45.0)], color="#3b82f6", zorder=4)
        
        ax_pomp.plot([45.0], [h_c2 - (y_sol - 0.0)], marker="o", color="black", markersize=14, linewidth=0, zorder=5)
        ax_pomp.plot([90.0], [h_c2 - (y_sol - 0.0)], marker="o", color="black", markersize=14, linewidth=0, zorder=5)
        
        epaisseur_buse = max(1.5, min(6.0, scale_db_pompier * 0.7))
        ax_pomp.plot([100.0, x_lance], [h_c2 - (y_sol - 40.0), y_lance_plt], color="#94a3b8", linewidth=epaisseur_buse, zorder=4)

        # 3. Foyer Incendie
        if x_feu < w_c2 - 10.0:
            fx = [x_feu - 15.0, x_feu, x_feu + 15.0, x_feu + 5.0]
            fy = [y_sol_plt, h_c2 - (y_sol - 40.0), y_sol_plt, h_c2 - (y_sol - 15.0)]
            ax_pomp.fill(fx, fy, color="#ea580c", zorder=3)
            cjx = [x_feu - 8.0, x_feu, x_feu + 8.0]
            cjy = [y_sol_plt, h_c2 - (y_sol - 25.0), y_sol_plt]
            ax_pomp.fill(cjx, cjy, color="#facc15", zorder=4)
            ax_pomp.text(x_feu, y_sol_plt - 12.0, f"d = {scale_distance_feu:.0f} m", color="white", fontsize=8, ha="center", fontweight="bold", zorder=5)

        # 4. Trajectoire de l'eau
        x_controle = (x_lance + x_impact_jet) / 2.0
        
        # RECTIFICATION : On utilise un + pour que le sommet de la parabole monte dans le ciel
        y_ctrl_plt = y_lance_plt + max(10.0, portee_reelle_m * 0.75)
        
        t_steps = np.linspace(0, 1, 40)
        px_eau = (1 - t_steps)**2 * x_lance + 2 * (1 - t_steps) * t_steps * x_controle + t_steps**2 * x_impact_jet
        py_eau = (1 - t_steps)**2 * y_lance_plt + 2 * (1 - t_steps) * t_steps * y_ctrl_plt + t_steps**2 * y_sol_plt
        
        ax_pomp.plot(px_eau, py_eau, color="#38bdf8", linewidth=3.0, zorder=4)
        ax_pomp.text(x_impact_jet, y_sol_plt + 12.0, f"{portee_reelle_m:.1f} m", color="#0284c7", fontsize=8, ha="center", fontweight="bold", zorder=5)
        # 5. Diagnostic d'extinction
        erreur_metres = scale_distance_feu - portee_reelle_m
        if abs(erreur_metres) <= 1.5:
            statut_tir = "SUCCÈS : L'incendie est maîtrise !"
            couleur_statut = "#16a34a"
        elif erreur_metres > 0:
            statut_tir = f"TROP COURT ! (Il manque {abs(erreur_metres):.1f} m)"
            couleur_statut = "#dc2626"
        else:
            statut_tir = f"TROP LOINTAIN ! (Le jet depasse de {abs(erreur_metres):.1f} m)"
            couleur_statut = "#eab308"

        ax_pomp.text(10.0, h_c2 - 15.0, "2. Application : Lance de Pompier (Defi d'extinction)", fontsize=8, color="#475569", fontweight="bold", ha="left", zorder=5)
        ax_pomp.text(10.0, h_c2 - 35.0, statut_tir, fontsize=9, color=couleur_statut, fontweight="bold", ha="left", zorder=5)

        ax_pomp.set_xlim(0.0, w_c2)
        ax_pomp.set_ylim(0.0, h_c2)
        ax_pomp.axis("off")
        st.pyplot(fig_pomp)
        plt.close(fig_pomp)

        
    st.write("---")
    
    res_q2, res_t2 = afficher_questions_hydrodynamiques(v_a, v_b, v_b_pomp, portee_reelle_m)

    # =====================================================================
    # --- EVALUATION SECURISEE ET EXPORTATION HTML ---
    # =====================================================================
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # Gestion locale du verrou technique de l'Atelier 2
    verrou_h2 = st.session_state.get("v_verrouille_tab2", False)

    case_certif_h2 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 2.", 
        key="check_certif_hydro2_official", 
        disabled=verrou_h2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_hydro2_official_final_action", use_container_width=True, disabled=verrou_h2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_h2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du premier bloc (Quiz QCM - 10 points)
            score_q2_brut = 0.0
            lignes_qcm_html = ""
            map_reponses_qcm = {q["id"]: q["rep"] for q in st.session_state.ordre_qcm_hydro2}
            map_enonces_qcm = {q["id"]: q["q"] for q in st.session_state.ordre_qcm_hydro2}

            for idx, (q_id, saisie) in enumerate(res_q2.items(), 1):
                attendu = map_reponses_qcm[q_id]
                enonce = map_enonces_qcm[q_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_q2_brut += 1.0
                    verdict = "CORRECT"
                    lbl_style = "status-pass"
                else:
                    verdict = "INCORRECT"
                    lbl_style = "status-fail"
                lignes_qcm_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            # 2. Correction du second bloc (Textes a trous - 10 points)
            score_t2_brut = 0.0
            lignes_trous_html = ""
            map_reponses_trous = {t["id"]: t["rep"] for t in st.session_state.ordre_trous_hydro2}
            map_enonces_trous = {t["id"]: t["q"] for t in st.session_state.ordre_trous_hydro2}

            for idx, (t_id, saisie) in enumerate(res_t2.items(), 1):
                attendu = map_reponses_trous[t_id]
                enonce = map_enonces_trous[t_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_t2_brut += 1.0
                    verdict = "CORRECT"
                    lbl_style = "status-pass"
                else:
                    verdict = "INCORRECT"
                    lbl_style = "status-fail"
                lignes_trous_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            # Sauvegarde des notes et verrouillage de session
            st.session_state.score_v2_p1 = round(float(score_q2_brut), 1)
            st.session_state.score_v2_p2 = round(float(score_t2_brut), 1)
            st.session_state.score_final_v2 = round(float(score_q2_brut + score_t2_brut), 1)
            st.session_state.lignes_qcm_html_t2 = lignes_qcm_html
            st.session_state.lignes_trous_html_t2 = lignes_trous_html
            st.session_state.v_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab2", False):
        scr1 = st.session_state.get("score_v2_p1", 0.0)
        scr2 = st.session_state.get("score_v2_p2", 0.0)
        tot_s = st.session_state.get("score_final_v2", 0.0)
        lignes_qcm_html = st.session_state.get("lignes_qcm_html_t2", "")
        lignes_trous_html = st.session_state.get("lignes_trous_html_t2", "")
        
        from datetime import datetime
        timestamp_v2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER HYDRODYNAMIQUE SCELLÉ | Note globale obtenue : {tot_s:.1f} / 20.0")

        # Confection de la page web du rapport d'evaluation autonome (Style Bleu Académique)
        html_content_t2 = f"""<!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Rapport d'Evaluation Hydrodynamique - Atelier 2</title>
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
                <div class="score-box">{tot_s:.1f} / 20</div>
                <h2 style="margin: 0; padding-bottom: 8px;">Professeur Laurent GALLET</h2>
                <div class="meta-info" style="font-size: 13px; line-height: 1.5;">
                    <strong>Module d'Evaluation :</strong> Hydrodynamique, Conservation du Debit et Effet Venturi (Atelier 2)<br>
                    <strong>Eleve :</strong> {p_eleve} {n_eleve} | <strong>Classe :</strong> {c_eleve}<br>
                    <strong>Donnees d'etude :</strong> Q1 = {var_debit_theorie:.1f} L/s &rarr; VA = {vitesse_a:.2f} m/s | VB = {vitesse_b:.2f} m/s | Portee lance = {portee_reelle_m:.1f} m<br>
                    <span style="font-size:11px; opacity:0.8;">Fige et scelle le : {timestamp_v2}</span>
                </div>
            </div>
            
            <div class="section-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 0 0 25px 0;">
                - Note obtenue au Questionnaire Technologique : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours a trous : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="section-title">1. Correction detaillee du Questionnaire QCM (Note sur 10 points)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%; text-align: center;">N°</th>
                        <th style="width: 45%;">Enonce de la question tiree au sort</th>
                        <th style="width: 19%;">Saisie de l'eleve</th>
                        <th style="width: 19%;">Attendu academique</th>
                        <th style="width: 12%; text-align: center;">Statut</th>
                    </tr>
                </thead>
                <tbody>{lignes_qcm_html}</tbody>
            </table>

            <div class="section-title">2. Correction detaillee de la Synthese a trous (Note sur 10 points)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%; text-align: center;">N°</th>
                        <th style="width: 45%;">Phrase de cours completee au sort</th>
                        <th style="width: 19%;">Saisie de l'eleve</th>
                        <th style="width: 19%;">Attendu academique</th>
                        <th style="width: 12%; text-align: center;">Statut</th>
                    </tr>
                </thead>
                <tbody>{lignes_trous_html}</tbody>
            </table>
        </body>
        </html>"""

        import os
        chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Hydrodynamique_Atelier2_{n_eleve}.html")
        try:
            with open(chemin_sauvegarde, "w", encoding="utf-8") as f: 
                f.write(html_content_t2)
        except Exception: 
            pass

        st.download_button(
            label="Telecharger mon rapport d'evaluation HTML",
            data=html_content_t2,
            file_name=f"Hydrodynamique_Atelier2_{n_eleve}_Copie.html",
            mime="text/html",
            key="btn_download_hydro_t2_final_action",
            use_container_width=True
        )





with tab3:
    st.header("Analyse hydro-mecanique de l'engin de chantier")
    st.write("Etude du circuit hydraulique de puissance, force de verin et sequence d'excavation de la pelleteuse d'apres la loi des pressions fluides.")

    # =====================================================================
    # --- 1. MOTEUR DE GÉNÉRATION ALGORITHMIQUE DU CATALOGUE CONSTRUCTEUR ---
    # =====================================================================
    if "catalogue_machines_tab3" not in st.session_state:
        st.session_state.catalogue_machines_tab3 = {}
        
        # Gamme 1 : Generation algorithmique des 15 Mini-pelles (Modeles Urbains de 1T a 6T)
        for i in range(1, 16):
            tonnes = 0.8 + (i * 0.35)
            piston = 40 + (i * 2)
            st.session_state.catalogue_machines_tab3[f"Modele Urbain - Mini-pelle {tonnes:.1f}T (N{i})"] = {
                "diametre_piston": piston, 
                "diametre_tige": int(piston * 0.5),
                "debit_recommande": 15 + (i * 2), 
                "pression_max": 140 + (i * 4)
            }
            
        # Gamme 2 : Generation algorithmique des 20 Pelleteuses Standards (7T a 35T)
        for i in range(1, 21):
            tonnes = 6.5 + (i * 1.5)
            piston = 70 + (i * 2)
            st.session_state.catalogue_machines_tab3[f"Modele Standard - Pelleteuse {tonnes:.1f}T (M{i})"] = {
                "diametre_piston": piston, 
                "diametre_tige": int(piston * 0.5),
                "debit_recommande": 50 + (i * 5), 
                "pression_max": 200 + (i * 5)
            }
            
        # Gamme 3 : Generation algorithmique des 15 Excavatrices de Carriere (36T a 110T)
        for i in range(1, 16):
            tonnes = 35.0 + (i * 5.0)
            piston = 110 + (i * 4)
            st.session_state.catalogue_machines_tab3[f"Modele Carriere - Excavatrice {tonnes:.1f}T (X{i})"] = {
                "diametre_piston": piston, 
                "diametre_tige": int(piston * 0.55),
                "debit_recommande": 150 + (i * 10), 
                "pression_max": 300 + (i * 8)
            }

    # =====================================================================
    # --- INITIALISATION STABLE DE LA SESSION DE L'ATELIER 3 ---
    # =====================================================================
    if "session_initialisee_tab3" not in st.session_state:
        st.session_state.session_initialisee_tab3 = True
        st.session_state.machine_choisie = "Modele Standard - Pelleteuse 12.5T (M4)"
        st.session_state.etat_distributeur = "STOP"
        st.session_state.course_verin_mm = 35.0
        st.session_state.eval_p_circuit = float(random.randint(90, 160)) if 'random' in locals() else 120.0

    # Raccourci d'acces local aux 50 machines generees
    catalogue_machines = st.session_state.catalogue_machines_tab3

    # Choix du mode d'evaluation pour l'Atelier 3
    mode_selectionne_tab3 = st.radio(
        "Mode de fonctionnement de l'Atelier 2 :",
        ["Mode Normal (Libre)", "Mode Evaluation (Aleatoire)"],
        key="radio_mode_tab3"
    )
    
    st.markdown("---")

    # =====================================================================
    # --- DISTRIBUTION DOUBLE COLONNE : ENTRÉES ET CONFIGURATIONS ---
    # =====================================================================
    col_gauche_t3, col_droite_t3 = st.columns(2)

    with col_gauche_t3:
        st.subheader("3. Circuit Engin de TP (Bas)")
        
        if "Normal" in mode_selectionne_tab3:
            var_debit_engin = st.slider("Débit de la pompe Q (L/min) :", min_value=1, max_value=150, value=10, step=1, key="slide_q_t3")
            var_pression_engin = st.slider("Pression du circuit P (bar) :", min_value=1, max_value=200, value=120, step=1, key="slide_p_t3")
            
            machine_selectionnee = st.selectbox(
                "Configuration du materiel (Catalogue Constructeur) :",
                list(catalogue_machines.keys()),
                index=list(catalogue_machines.keys()).index(st.session_state.machine_choisie)
            )
            st.session_state.machine_choisie = machine_selectionnee
            
            terrain_choisi = st.selectbox(
                "Type de terrain / Résistance :",
                ["Sable (Facile - 15 kN)", "Terre compacte (Moyen - 45 kN)", "Roche (Difficile - 65 kN)"]
            )
        else:
            st.info("Parametres d'examen imposes de l'Atelier 3.")
            var_debit_engin = 10
            var_pression_engin = st.session_state.eval_p_circuit
            st.session_state.machine_choisie = "Modele Standard - Pelleteuse 12.5T (M4)"
            terrain_choisi = "Terre compacte (Moyen - 45 kN)"
            
            st.markdown(f"* **Débit force de la pompe Q :** {var_debit_engin} L/min")
            st.markdown(f"* **Pression de consigne du circuit P :** {var_pression_engin:.0f} bar")
            st.markdown(f"* **Engin d'etude impose :** {st.session_state.machine_choisie}")
            st.markdown(f"* **Foyer de resistance du sol :** {terrain_choisi}")

        # Extraction des fiches constructeur
        specs = catalogue_machines[st.session_state.machine_choisie]
        st.markdown(f"""
        **Fiche Technique Constructeur Recuperee :**
        * Alesage Piston : {specs['diametre_piston']} mm | Diametre Tige : {specs['diametre_tige']} mm
        * Debit Recommande : {specs['debit_recommande']} L/min | Pression Max : {specs['pression_max']} bar
        """)

        # --- MOTEUR DE CALCUL DE FORCE DYNAMIQUE DU VÉRIN ---
        d_piston_m = specs["diametre_piston"] / 1000.0
        d_tige_m = specs["diametre_tige"] / 1000.0
        
        s_piston_m2 = np.pi * (d_piston_m / 2.0)**2
        s_tige_m2 = np.pi * ((d_piston_m / 2.0)**2 - (d_tige_m / 2.0)**2)

        # Commande interactive du distributeur 4/2
        c_b1, c_b2, c_b3 = st.columns(3)
        with c_b1:
            if st.button("SORTIR", use_container_width=True, key="btn_sortir_t3"):
                st.session_state.etat_distributeur = "SORTIR"
        with c_b2:
            if st.button("STOP", use_container_width=True, key="btn_stop_t3"):
                st.session_state.etat_distributeur = "STOP"
        with c_b3:
            if st.button("RENTRE", use_container_width=True, key="btn_rentrer_t3"):
                st.session_state.etat_distributeur = "RENTRER"

        pression_pa = var_pression_engin * 100000.0
        if st.session_state.etat_distributeur == "SORTIR":
            force_verin_kn = (pression_pa * s_piston_m2) / 1000.0
            texte_force = f"Force Pousseee : {force_verin_kn:.1f} kN"
            st.session_state.course_verin_mm = min(70.0, st.session_state.course_verin_mm + (var_debit_engin * 0.4))
        elif st.session_state.etat_distributeur == "RENTRER":
            force_verin_kn = (pression_pa * s_tige_m2) / 1000.0
            texte_force = f"Force Traction : {force_verin_kn:.1f} kN"
            st.session_state.course_verin_mm = max(0.0, st.session_state.course_verin_mm - (var_debit_engin * 0.4))
        else:
            force_verin_kn = (pression_pa * s_piston_m2) / 1000.0
            texte_force = f"Force Pousseee (Fige) : {force_verin_kn:.1f} kN"

        # Diagnostic de validation face au sol
        limite_sol_kn = 15.0 if "Sable" in terrain_choisi else (65.0 if "Roche" in terrain_choisi else 45.0)
        machine_prete = force_verin_kn >= limite_sol_kn
        
        st.markdown("---")
        st.markdown(f"**Statut Actuel :** {texte_force}")
        if machine_prete:
            st.success(f"Machine prete - Puissance suffisante pour le terrain ({force_verin_kn:.1f} kN >= {limite_sol_kn:.0f} kN)")
        else:
            st.error(f"SECURITE : Force insuffisante ! Le verin cale face a la resistance ({force_verin_kn:.1f} kN < {limite_sol_kn:.0f} kN)")

        # Automatisation des butees constructeur
        if "Normal" in mode_selectionne_tab3:
            st.write("---")
            st.markdown("##### Seuils limites constructeur")
            st.info(f"Pour cette machine, ne depassez pas {specs['debit_recommande']} L/min et {specs['pression_max']} bar.")

        if st.button("PAUSE MANUELLE (ARRET D'URGENCE)", key="btn_pause_manuel_t3", type="primary", use_container_width=True):
            st.session_state.etat_distributeur = "STOP"
            st.warning("Système hydraulique fige en arret d'urgence.")
            st.rerun()

    # =====================================================================
    # --- COLONNE DROITE : RENDUS GRAPHIQUE MATPLOTLIB RECALÉS ---
    # =====================================================================
    with col_droite_t3:
        st.subheader("4. Rendus Graphiques et Modele d'Excavation")
        plt.close('all')

        sub_col1_t3, sub_col2_t3 = st.columns(2)

        # --- SCHEMA 1 : COMPOSANTS DU CIRCUIT HYDRAULIQUE VÉRIN ---

        with sub_col1_t3:
            st.markdown("**3. Schema Technologique : Circuit Hydraulique**")
            fig_hyd, ax_hyd = plt.subplots(figsize=(4.5, 4.5), dpi=100)
            ax_hyd.clear()

            # 1. Dessin normalise de la Pompe et de son Reservoir (A gauche)
            # Le bac/reservoir sous la pompe
            ax_hyd.plot([0.5, 0.5, 2.0, 2.0], [1.5, 0.8, 1.5], color="#1e293b", linewidth=2)
            ax_hyd.text(1.25, 0.5, "Pompe", fontsize=8, ha="center", fontweight="bold", color="#1e293b")
            
            # Le cercle de la pompe
            cercle_pompe = plt.Circle((1.25, 1.8), 0.4, facecolor="white", edgecolor="black", linewidth=2, zorder=4)
            ax_hyd.add_patch(cercle_pompe)
            # Le triangle noir interne pointant vers le haut
            triangle_pompe = plt.Polygon([[1.25, 2.2], [1.05, 1.7], [1.45, 1.7]], facecolor="black", edgecolor="black", zorder=5)
            ax_hyd.add_patch(triangle_pompe)

            # 2. Dessin du Bloc Distributeur 4/2 (Au milieu)
            ax_hyd.add_patch(plt.Rectangle((3.0, 1.3), 2.2, 1.8, facecolor="#e2e8f0", edgecolor="black", linewidth=2, zorder=3))
            ax_hyd.text(4.1, 3.2, "Distributeur 4/2", fontsize=8, ha="center", fontweight="bold")
            # Ligne de separation pointillee au milieu du tiroir
            ax_hyd.plot([4.1, 4.1], [1.3, 3.1], color="black", linestyle=":", linewidth=1.5, zorder=4)
            
            # Levier de commande avec sa boule rouge indexe sur la position
            x_boule = 2.4 if st.session_state.etat_distributeur == "SORTIR" else (2.0 if st.session_state.etat_distributeur == "RENTRER" else 2.2)
            y_boule = 2.8 if st.session_state.etat_distributeur == "SORTIR" else (2.2 if st.session_state.etat_distributeur == "RENTRER" else 2.5)
            ax_hyd.plot([3.0, x_boule], [2.2, y_boule], color="black", linewidth=2.5, zorder=4)
            ax_hyd.plot([x_boule], [y_boule], marker="o", color="red", markersize=8, zorder=5)

            # 3. Dessin du Corps Cylindrique du Vérin (A droite)
            ax_hyd.add_patch(plt.Rectangle((5.8, 1.5), 2.2, 0.8, facecolor="white", edgecolor="black", linewidth=2, zorder=3))
            
            # Deplacement du piston et de la tige grise d'apres la course reelle
            x_piston_plt = 5.8 + (st.session_state.course_verin_mm / 70.0) * 1.3
            ax_hyd.fill_between([5.8, x_piston_plt], [1.55, 1.55], [2.25, 2.25], color="#cbd5e1", alpha=0.5, zorder=2) # Fluide interne
            ax_hyd.plot([x_piston_plt, x_piston_plt], [1.5, 2.3], color="black", linewidth=4, zorder=4) # Tête complet
            ax_hyd.plot([x_piston_plt, 7.9], [1.9, 1.9], color="#94a3b8", linewidth=6, solid_capstyle="butt", zorder=4) # Tige
            ax_hyd.plot([x_piston_plt], [1.9], marker=">", color="white", markersize=6, zorder=5)

            # Reglette graduée supérieure de metrologie (0mm a 70mm)
            ax_hyd.plot([5.8, 7.8], [2.5, 2.5], color="black", linewidth=1.5)
            for grad in np.linspace(5.8, 7.8, 5):
                ax_hyd.plot([grad, grad], [2.5, 2.6], color="black", linewidth=1)
            ax_hyd.text(5.8, 2.7, "0mm", fontsize=7, ha="center")
            ax_hyd.text(7.8, 2.7, "70mm", fontsize=7, ha="center")
            # Index mobile rouge sur la reglette
            ax_hyd.arrow(x_piston_plt, 2.4, 0, -0.15, head_width=0.08, head_length=0.08, fc="red", ec="red", zorder=5)

            # 4. Connexions des Tuyauteries Fluides Bicolores Croisées
            c_gauche = "red" if st.session_state.etat_distributeur == "SORTIR" else "blue"
            c_droite = "blue" if st.session_state.etat_distributeur == "SORTIR" else "red"
            if st.session_state.etat_distributeur == "STOP": 
                c_gauche = "blue"
                c_droite = "blue"

            # Tuyau A (Alimentation gauche du verin)
            ax_hyd.plot([1.25, 1.25, 3.5], [2.2, 2.4, 2.4], color=c_gauche, linewidth=2, zorder=2) # Pompe vers distrib
            ax_hyd.plot([3.5, 3.5, 6.0, 6.0], [3.1, 2.6, 2.6, 1.5], color=c_gauche, linewidth=2, zorder=2) # Distrib vers verin gauche
            
            # Tuyau B (Retour reservoir droite du verin)
            ax_hyd.plot([4.7, 4.7, 7.4, 7.4], [3.1, 1.1, 1.1, 1.5], color=c_droite, linewidth=2, zorder=2) # Distrib vers verin droite
            ax_hyd.plot([4.7, 4.7, 1.6], [1.3, 1.0, 1.1], color=c_droite, linewidth=2, zorder=2) # Distrib vers reservoir

            # 5. Valeurs et Etiquettes de métrologie basse
            ax_hyd.text(6.8, 1.0, f"Force Pousseee : {force_verin_kn:.1f} kN", color="red", fontsize=8, fontweight="bold", ha="center")
            ax_hyd.text(4.1, 0.4, f"T = {st.session_state.course_verin_mm * 0.1:.3f} s", bbox=dict(facecolor='#f8fafc', edgecolor='#cbd5e1', boxstyle='square,pad=0.3'), fontsize=8, ha="center")

            # Cadrage de l'espace de rendu
            ax_hyd.set_xlim(0.0, 8.5)
            ax_hyd.set_ylim(0.0, 3.6)
            ax_hyd.axis("off")
            
            st.pyplot(fig_hyd)
            plt.close(fig_hyd)

    # --- SCHEMA 2 : RENDU ARTICULÉ DE LA SÉQUENCE DE CHANTIER (DROITE) ---
    with sub_col2_t3:
        st.markdown("**4. Application Chantier : Sequence d'Excavation**")
        fig_pel, ax_pel = plt.subplots(figsize=(4, 4), dpi=100)
        ax_pel.clear()

        c_sol_bloc = "#78350f" if "Terre" in terrain_choisi else ("#94a3b8" if "Roche" in terrain_choisi else "#fef08a")

        # Fond de ciel et sol
        ax_pel.fill_between([0, 10], [0, 0], [8, 8], color="#f1f5f9", zorder=1)
        ax_pel.fill_between([0, 10], [-2, -2], [0, 0], color=c_sol_bloc, zorder=2)
        ax_pel.plot([0, 10], [0, 0], color="#16a34a", linewidth=3, zorder=3)

        # Cinematique du bras articule
        facteur_angulaire = (st.session_state.course_verin_mm / 70.0)
        angle_bras = np.radians(35.0 + (facteur_angulaire * 25.0))
        angle_balancier = np.radians(45.0 - (facteur_angulaire * 30.0))

        x_pivot, y_pivot = 3.0, 1.5
        x_artic1 = x_pivot + 3.0 * np.cos(angle_bras)
        y_artic1 = y_pivot + 3.0 * np.sin(angle_bras)
        x_godet = x_artic1 + 2.2 * np.cos(angle_bras - angle_balancier)
        y_godet = y_artic1 - 2.2 * np.sin(angle_bras - angle_balancier)

        # Chassis jaune de la machine et cabine
        ax_pel.add_patch(plt.Rectangle((1.5, 0.2), 2.0, 1.2, facecolor="#eab308", edgecolor="black", linewidth=1.5, zorder=4))
        ax_pel.add_patch(plt.Rectangle((1.8, 1.4), 1.2, 0.8, facecolor="#cbd5e1", edgecolor="black", linewidth=1, zorder=4))
        ax_pel.plot([1.2, 3.8], [0.1, 0.1], color="black", linewidth=5, solid_capstyle="round", zorder=5)

        # Tracé des éléments articulés
        ax_pel.plot([x_pivot, x_artic1], [y_pivot, y_artic1], color="#eab308", linewidth=6, solid_capstyle="round", zorder=4)
        ax_pel.plot([x_artic1, x_godet], [y_artic1, y_godet], color="#94a3b8", linewidth=4, solid_capstyle="round", zorder=4)
        ax_pel.plot([x_godet, x_godet + 0.6, x_godet + 0.3], [y_godet, y_godet - 0.4, y_godet - 0.6], color="#475569", linewidth=3, zorder=5)

        ax_pel.set_xlim(0, 10)
        ax_pel.set_ylim(-2, 8)
        ax_pel.axis("off")
        st.pyplot(fig_pel)
        plt.close(fig_pel)            
    st.write("---")
    verrou_h3 = st.session_state.get("v_verrouille_tab3", False)
    
    res_q3, res_t3 = afficher_questions_engin_tp(
        force_verin_kn, 
        s_piston_m2, 
        s_tige_m2, 
        var_pression_engin, 
        limite_sol_kn, 
        verrouille=verrou_h3
    )

    # =====================================================================
    # --- MOTEUR DE CORRECTION ET EXPORTATION DU RAPPORT SCELLÉ ---
    # =====================================================================
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_h3 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 3.", 
        key="check_certif_hydro3_official_scelle_final_action", 
        disabled=verrou_h3
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_hydro3_official_final_action_click", use_container_width=True, disabled=verrou_h3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_h3:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du premier bloc (Quiz QCM - 10 points)
            score_q3_brut = 0.0
            lignes_qcm_html = ""
            map_reponses_qcm = {q["id"]: q["rep"] for q in st.session_state.ordre_quiz_hydro3}
            map_enonces_qcm = {q["id"]: q["q"] for q in st.session_state.ordre_quiz_hydro3}

            for idx, (q_id, saisie) in enumerate(res_q3.items(), 1):
                attendu = map_reponses_qcm[q_id]
                enonce = map_enonces_qcm[q_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_q3_brut += 1.0
                    verdict = "CORRECT"
                    lbl_style = "status-pass"
                else:
                    verdict = "INCORRECT"
                    lbl_style = "status-fail"
                lignes_qcm_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            # 2. Correction du second bloc (Textes a trous - 10 points)
            score_t3_brut = 0.0
            lignes_trous_html = ""
            
            # Reponses attendues pour les textes a trous fixes de l'Atelier 3
            map_reponses_trous = {
                "t1": "Debit", "t2": "Surface", "t3": "Bypass", "t4": "Pression", "t5": "Vitesse",
                "t6": "Resistance", "t7": "Charge", "t8": "Incompressibles", "t9": "Vitesse", "t10": "Reservoir"
            }
            map_enonces_trous = {
                "t1": "Le deplacement de la tige de verin est directement proportionnel au",
                "t2": "La force developpee mecaniquement par un verin depend de sa",
                "t3": "Les joints d'etancheite composites d'un piston bloquent les fuites de fluide internes dites en",
                "t4": "Si le verin depasse la charge max, le fluide s'echappe par le limiteur de",
                "t5": "La puissance utile de sortie de la tige associe sa force active et sa",
                "t6": "Un fluide sous contrainte de charge cherche la zone de plus faible",
                "t7": "La deperdition energetique par frottements visqueux est une perte de",
                "t8": "En hydrostatique, les huiles minerales sont considerees comme",
                "t9": "La reduction de section au sein d'une conduite entraine l'essor de la",
                "t10": "L'evacuation finale de l'huile usagee non contrainte s'effectue vers le"
            }

            for idx, (t_id, saisie) in enumerate(res_t3.items(), 1):
                attendu = map_reponses_trous[t_id]
                enonce = map_enonces_trous[t_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_t3_brut += 1.0
                    verdict = "CORRECT"
                    lbl_style = "status-pass"
                else:
                    verdict = "INCORRECT"
                    lbl_style = "status-fail"
                lignes_trous_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            # Sauvegarde des notes et verrouillage de session
            st.session_state.score_v3_p1 = round(float(score_q3_brut), 1)
            st.session_state.score_v3_p2 = round(float(score_t3_brut), 1)
            st.session_state.score_final_v3 = round(float(score_q3_brut + score_t3_brut), 1)
            st.session_state.lignes_qcm_html_t3 = lignes_qcm_html
            st.session_state.lignes_trous_html_t3 = lignes_trous_html
            st.session_state.v_verrouille_tab3 = True
            st.st.rerun()

    if st.session_state.get("v_verrouille_tab3", False):
        scr1 = st.session_state.get("score_v3_p1", 0.0)
        scr2 = st.session_state.get("score_v3_p2", 0.0)
        tot_s = st.session_state.get("score_final_v3", 0.0)
        lignes_qcm_html = st.session_state.get("lignes_qcm_html_t3", "")
        lignes_trous_html = st.session_state.get("lignes_trous_html_t3", "")
        
        from datetime import datetime
        timestamp_v3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ENGIN DE CHANTIER SCELLÉ | Note globale obtenue : {tot_s:.1f} / 20.0")

        # Confection du rapport d'evaluation autonome (Style Bleu Académique)
        html_content_t3 = f"""<!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Rapport d'Evaluation Engin TP - Atelier 3</title>
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
                <div class="score-box">{tot_s:.1f} / 20</div>
                <h2 style="margin: 0; padding-bottom: 8px;">Professeur Laurent GALLET</h2>
                <div class="meta-info" style="font-size: 13px; line-height: 1.5;">
                    <strong>Module d'Evaluation :</strong> Circuit hydraulique de puissance et engins de TP (Atelier 3)<br>
                    <strong>Eleve :</strong> {p_eleve} {n_eleve} | <strong>Classe :</strong> {c_eleve}<br>
                    <strong>Machine configuree :</strong> {st.session_state.machine_choisie} | Force de consigne developpee : {force_verin_kn:.1f} kN<br>
                    <span style="font-size:11px; opacity:0.8;">Fige et scelle le : {timestamp_v3}</span>
                </div>
            </div>
            
            <div class="section-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 0 0 25px 0;">
                - Note obtenue au Questionnaire Technologique : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours a trous : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="section-title">1. Correction detaillee du Questionnaire QCM (Note sur 10 points)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%; text-align: center;">N°</th>
                        <th style="width: 45%;">Enonce de la question tiree au sort</th>
                        <th style="width: 19%;">Saisie de l'eleve</th>
                        <th style="width: 19%;">Attendu academique</th>
                        <th style="width: 12%; text-align: center;">Statut</th>
                    </tr>
                </thead>
                <tbody>{lignes_qcm_html}</tbody>
            </table>

            <div class="section-title">2. Correction detaillee de la Synthese a trous (Note sur 10 points)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%; text-align: center;">N°</th>
                        <th style="width: 45%;">Phrase de cours completee au sort</th>
                        <th style="width: 19%;">Saisie de l'eleve</th>
                        <th style="width: 19%;">Attendu academique</th>
                        <th style="width: 12%; text-align: center;">Statut</th>
                    </tr>
                </thead>
                <tbody>{lignes_trous_html}</tbody>
            </table>
        </body>
        </html>"""

        import os
        chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Circuit_TP_Atelier3_{n_eleve}.html")
        try:
            with open(chemin_sauvegarde, "w", encoding="utf-8") as f: 
                f.write(html_content_t3)
        except Exception: 
            pass

        st.download_button(
            label="Telecharger mon rapport d'evaluation HTML",
            data=html_content_t3,
            file_name=f"Circuit_TP_Atelier3_{n_eleve}_Copie.html",
            mime="text/html",
            key="btn_download_hydro_t3_final_action_click",
            use_container_width=True
        )





































