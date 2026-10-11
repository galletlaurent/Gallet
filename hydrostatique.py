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



def afficher_questions_plomberie(p_compteur, h_nourrice, n_reynolds, q_total_maison, taux_remplissage, verrouille=False):
    import random
    import streamlit as st
    
    if "ordre_quiz_hydro5" not in st.session_state:
        val_p_statique = f"{max(0.01, p_compteur - (1000.0 * 9.81 * h_nourrice / 100000.0)):.2f}"
        val_rey_str = f"{n_reynolds:.0f}"
        val_q_pvc = f"{q_total_maison:.2f}"
        val_remp_pvc = f"{taux_remplissage:.0f}"
        
        base_cat_qcm_t5 = [
            {"id": "h5_1", "q": "Quelle loi de perte de charge hydrostatique quantifie la baisse de pression liee a l'altitude de la nourrice ?", "options": ["Loi de Pascal", "Principe d'Archimede", "Theoreme de Venturi"], "rep": "Loi de Pascal"},
            {"id": "h5_2", "q": "D'apres vos reglages d'eau potable, calculez la pression statique disponible a la nourrice (bar) :", "options": [val_p_statique, f"{float(val_p_statique)+1.5:.2f}", "0.00"], "rep": val_p_statique},
            {"id": "h5_3", "q": "Le pic de surpression destructeur genere par la fermeture brutale d'une vanne s'appelle le coup de :", "options": ["Belier", "Venturi", "Pascal"], "rep": "Belier"},
            {"id": "h5_4", "q": "D'apres vos reglages au robinet, quel est le nombre de Reynolds Re exact calcule en session :", "options": [val_rey_str, "1500", "5000"], "rep": val_rey_str},
            {"id": "h5_5", "q": "Sous quel nombre de Reynolds le regime d'un fluide est-il considere comme strictly laminaire ?", "options": ["Moins de 2000", "De 2000 a 4000", "Plus de 4000"], "rep": "Moins de 2000"},
            {"id": "h5_6", "q": "Au-dela de Re = 4000, comment qualifie-t-on le regime fluide du jet (debit desordonne) :", "options": ["Turbulent", "Laminaire", "Transitoire"], "rep": "Turbulent"},
            {"id": "h5_7", "q": "Quelle formule normalisee regit la capacite de transport gravitaire a surface libre des tubes PVC ?", "options": ["Manning-Strickler", "Bernoulli", "Loi de Mariotte"], "rep": "Manning-Strickler"},
            {"id": "h5_8", "q": "D'apres vos reglages PVC, quel est le debit total d'evacuation rejete par le batiment (L/s) :", "options": [val_q_pvc, "1.50", "20.00"], "rep": val_q_pvc},
            {"id": "h5_9", "q": "D'apres vos reglages PVC, quel est le taux de remplissage effectif du collecteur d'egout (%) :", "options": [val_remp_pvc, "50", "100"], "rep": val_remp_pvc},
            {"id": "h5_10", "q": "A partir de quel taux de remplissage lineaire le collecteur PVC entre-t-it en charge (glouglou) ?", "options": ["Plus de 70%", "Moins de 30%", "Exactement 50%"], "rep": "Plus de 70%"}
        ]
        
        base_cat_trous_t5 = [
            {"id": "h5t_1", "q": "1. Le deplacement lineaire d'une particule en regime laminaire suit des trajectoires", "options": ["Paralleles", "Tourbillonnantes", "Hachures"], "rep": "Paralleles"},
            {"id": "h5t_2", "q": "2. La resistance d'un fluide face au glissement de ses couches internes definit la", "options": ["Viscosite", "Pression", "Densite"], "rep": "Viscosite"},
            {"id": "h5t_3", "q": "3. Les canalisations gravitaires en PVC evacuent les eaux usees sans contrainte de", "options": ["Pression", "Pente", "Debit"], "rep": "Pression"},
            {"id": "h5t_4", "q": "4. Le raccord de distribution bivalent distribuant l'eau vers les terminaux est la", "options": ["Nourrice", "Vanne", "Cuve"], "rep": "Nourrice"},
            {"id": "h5t_5", "q": "5. L'essor de la rugosite interne des parois de flexibles accroit les pertes de", "options": ["Charge", "Vitesse", "Masse"], "rep": "Charge"},
            {"id": "h5t_6", "q": "6. La celerite de l'onde acoustique lors d'un choc de belier est liee a l'elasticite du", "options": ["Conduit", "Fluide", "Reservoir"], "rep": "Conduit"},
            {"id": "h5t_7", "q": "7. Une decharge fluide depassant la capacite maximale d'un PVC provoque un", "options": ["Engorgement", "Siphonage", "Bypass"], "rep": "Engorgement"},
            {"id": "h5t_8", "q": "8. Le nombre de Reynolds met en rapport les forces d'inertia et les forces de", "options": ["Viscosite", "Pesanteur", "Tension"], "rep": "Viscosite"},
            {"id": "h5t_9", "q": "9. Pour preserver l'arret des odeurs d'egout, chaque appareil est muni d'un", "options": ["Siphon", "Clapet", "Compteur"], "rep": "Siphon"},
            {"id": "h5t_10", "q": "10. En regime turbulent desordonne, les billes de fluide subissent de fortes", "options": ["Oscillations", "Stagnations", "Compressions"], "rep": "Oscillations"}
        ]
        
        st.session_state.ordre_qcm_hydro5 = list(base_cat_qcm_t5)
        st.session_state.ordre_trous_hydro5 = list(base_cat_trous_t5)
        random.shuffle(st.session_state.ordre_qcm_hydro5)
        random.shuffle(st.session_state.ordre_trous_hydro5)

    col_form1, col_form2 = st.columns(2)

    with col_form1:
        st.markdown("##### Quiz technique de plomberie (10 questions - 10 pts)")
        dict_rep_q5 = {}
        for idx, q_data in enumerate(st.session_state.ordre_qcm_hydro5, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_t5_q_{q_data['id']}"
            cle_opts = f"opts_hydro5_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q5[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_form2:
        st.markdown("##### Synthese de cours a trous (10 trous - 10 pts)")
        dict_trous_5 = {}
        for idx, q_data in enumerate(st.session_state.ordre_trous_hydro5, 1):
            c_text, col_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_text:
                st.write(f"{idx}. {q_data['q']}")
            cle_select_t = f"hydro_t5_t_{q_data['id']}"
            cle_opts_t = f"opts_trous5_{q_data['id']}"
            if cle_opts_t not in st.session_state:
                opts_t = list(q_data["options"])
                random.shuffle(opts_t)
                st.session_state[cle_opts_t] = ["Choisir..."] + opts_t
            val_p_t = st.session_state.get(cle_select_t, "Choisir...")
            sel_idx_t = st.session_state[cle_opts_t].index(val_p_t) if val_p_t in st.session_state[cle_opts_t] else 0
            with col_sel:
                dict_trous_5[q_data["id"]] = st.selectbox("", st.session_state[cle_opts_t], index=sel_idx_t, key=cle_select_t, disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q5, dict_trous_5

def afficher_questions_carburateur(delta_p_pa, obs_air, fissure, col_gicleur, rpm, vitesse_air_col_reelle, depression_bar, etat_combustion, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_hydro4" not in st.session_state:
        val_dp_str = f"{abs(delta_p_pa):.1f}"
        val_dep_str = f"{-depression_bar:.3f}"
        val_vit_str = f"{vitesse_air_col_reelle:.1f}"
        
        base_cat_qcm_t4 = [
            {"id": "h4_1", "q": "Au niveau du col d'un tube Venturi, la vitesse du fluide subit une :", "options": ["Augmentation", "Diminution", "Stagnation"], "rep": "Augmentation"},
            {"id": "h4_2", "q": "D'apres le theoreme de Bernoulli, l'essor de la vitesse au col provoque une baisse de :", "options": ["Pression", "Debit", "Masse"], "rep": "Pression"},
            {"id": "h4_3", "q": "Calculez la valeur absolue de la pression differentielle Delta P de session (Pa) :", "options": [val_dp_str, f"{float(val_dp_str)*2:.1f}", f"{float(val_dp_str)/2:.1f}"], "rep": val_dp_str},
            {"id": "h4_4", "q": "Quelle anomalie d'admission provoque un vide artificiel et la noyade de la bougie ?", "options": ["Filtre obstrue", "Fissure collecteur", "Gicleur colmate"], "rep": "Filtre obstrue"},
            {"id": "h4_5", "q": "Quel composant calibre le passage de l'essence pour former le melange gazeux ?", "options": ["Gicleur", "Papillon", "Soupape"], "rep": "Gicleur"},
            {"id": "h4_6", "q": "D'apres vos reglages, quelle est la depression exacte calculee au col du Venturi (bar) :", "options": [val_dep_str, "-0.010", "-0.150"], "rep": val_dep_str},
            {"id": "h4_7", "q": "D'apres vos reglages, quelle est la vitesse de l'air reelle circulant au col (m/s) :", "options": [val_vit_str, f"{float(val_vit_str)*1.5:.1f}", f"{float(val_vit_str)/2:.1f}"], "rep": val_vit_str},
            {"id": "h4_8", "q": "Quel est l'etat thermique dynamique deduite par l'automate pour le moteur actuel ?", "options": [etat_combustion, "NORMAL", "ETEINT"], "rep": etat_combustion},
            {"id": "h4_9", "q": "Quel type d'organe mecanique mobile regle le debit d'air total admis (ex: accelerateur) :", "options": ["Papillon", "Gicleur", "Flotteur"], "rep": "Papillon"},
            {"id": "h4_10", "q": "Si le regime moteur double sans obstruction, la depression au col du Venturi est :", "options": ["Quadruplee", "Doublee", "Divisee_par_deux"], "rep": "Quadruplee"}
        ]
        
        base_cat_trous_t4 = [
            {"id": "h4t_1", "q": "1. Le fluide le plus lourd reference dans votre liste de Bernoulli est le", "options": ["Mercure", "Eau pure", "Glycerine"], "rep": "Mercure"},
            {"id": "h4t_2", "q": "2. Une prise d'air parasite sur le collecteur engendre un melange trop", "options": ["Pauvre", "Riche", "Homogene"], "rep": "Pauvre"},
            {"id": "h4t_3", "q": "3. Les gaz de combustion sont consideres comme des fluides hautement", "options": ["Compressibles", "Incompressibles", "Visqueux"], "rep": "Compressibles"},
            {"id": "h4t_4", "q": "4. Le tube de Venturi exploite directement le principe de conservation du", "options": ["Debit", "Poids", "Volume"], "rep": "Debit"},
            {"id": "h4t_5", "q": "5. En cas de colmatage integral du gicleur, le moteur thermique se retrouve", "options": ["Eteint", "Noye", "Surchauffe"], "rep": "Eteint"},
            {"id": "h4t_6", "q": "6. L'aspiration du carburant est creee par la difference de pression dite", "options": ["Differentielle", "Atmospherique", "Statique"], "rep": "Differentielle"},
            {"id": "h4t_7", "q": "7. L'obstruction severe du filtre a air enrichit le melange par manque d'", "options": ["Oxygene", "Carburant", "Viscosite"], "rep": "Oxygene"},
            {"id": "h4t_8", "q": "8. Le rapport geometrique entre section large et etroite conditionne le taux d'", "options": ["Acceleration", "Frottement", "Compression"], "rep": "Acceleration"},
            {"id": "h4t_9", "q": "9. Une vitesse de fluide excessive engendre une deperdition nommee perte de", "options": ["Charge", "Masse", "Vitesse"], "rep": "Charge"},
            {"id": "h4t_10", "q": "10. La reserve de carburant a niveau constant est maintenue stable par la", "options": ["Cuve", "Buse", "Pipe"], "rep": "Cuve"}
        ]
        
        st.session_state.ordre_qcm_hydro4 = list(base_cat_qcm_t4)
        st.session_state.ordre_trous_hydro4 = list(base_cat_trous_t4)
        random.shuffle(st.session_state.ordre_qcm_hydro4)
        random.shuffle(st.session_state.ordre_trous_hydro4)

    col_q4, col_t4 = st.columns(2)

    with col_q4:
        st.markdown("##### Quiz aerodynamique et pannes (10 questions - 10 pts)")
        dict_rep_q4 = {}
        for idx, q_data in enumerate(st.session_state.ordre_qcm_hydro4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_t4_q_{q_data['id']}"
            cle_opts = f"opts_hydro4_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q4[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t4:
        st.markdown("##### Synthese aerothermique a trous (10 trous - 10 pts)")
        dict_trous_4 = {}
        for idx, q_data in enumerate(st.session_state.ordre_trous_hydro4, 1):
            c_text, col_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_text:
                st.write(f"{idx}. {q_data['q']}")
            cle_select_t = f"hydro_t4_t_{q_data['id']}"
            cle_opts_t = f"opts_trous4_{q_data['id']}"
            if cle_opts_t not in st.session_state:
                opts_t = list(q_data["options"])
                random.shuffle(opts_t)
                st.session_state[cle_opts_t] = ["Choisir..."] + opts_t
            val_p_t = st.session_state.get(cle_select_t, "Choisir...")
            sel_idx_t = st.session_state[cle_opts_t].index(val_p_t) if val_p_t in st.session_state[cle_opts_t] else 0
            with col_sel:
                dict_trous_4[q_data["id"]] = st.selectbox("", st.session_state[cle_opts_t], index=sel_idx_t, key=cle_select_t, disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q4, dict_trous_4





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


def initialiser_billes_reynolds_autonome():
    """Genere et securise la liste initiale des 20 particules pour le canal Reynolds en session state."""
    import random
    
    if "billes_reynolds_libre" not in st.session_state:
        st.session_state.billes_reynolds_libre = []
        
        # On repartit les 20 billes de maniere homogene sur la longueur du petit repere (300px)
        for i in range(20):
            st.session_state.billes_reynolds_libre.append({
                "x": float(random.randint(10, 290)),
                "y_base": 20.0,              # Centre vertical du petit canal (hauteur 40)
                "y_oscillation": 0.0,        
                "phase": float(random.uniform(0, 6.28))
            })


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

        # RECTIFICATION : Facteur d'échelle fluide pour adapter la vitesse excessive à l'écran fixe
        v_b_ajustee = v_b_pomp * 0.05
        portee_reelle_m = (v_b_ajustee ** 1.4) * 0.22
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
                    <strong>Donnees d'etude :</strong> Q1 = {var_debit_pompier:.1f} L/s &rarr; VA = {v_a:.2f} m/s | VB = {v_b:.2f} m/s | Portee lance = {portee_reelle_m:.1f} m<br>
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
        st.subheader("Schéma Technologique : Circuit Hydraulique de l'Engin")
        plt.close('all')
            
        # === INITIALISATION ET SÉCURISATION DES VARIABLES LOCALES ===
        direction_actuelle = st.session_state.get("etat_distributeur", "STOP")
        p_bar = float(var_pression_engin)
        q_engin = float(var_debit_engin)
        
        # Récupération des dimensions constructeur depuis la machine active
        specs_actives = catalogue_machines[st.session_state.machine_choisie]
        d_piston_m = specs_actives["diametre_piston"] / 1000.0
        d_tige_m = specs_actives["diametre_tige"] / 1000.0
        
        s_piston_m2 = np.pi * (d_piston_m / 2.0)**2
        s_tige_m2 = np.pi * ((d_piston_m / 2.0)**2 - (d_tige_m / 2.0)**2)

        # Initialisation sécurisée du chronomètre dans Streamlit
        if "temps_simulation" not in st.session_state:
            st.session_state.temps_simulation = 0.0

        pression_pa = p_bar * 100000.0
        q_m3s_calcul = q_engin / 60000.0
        s_active_m2 = s_tige_m2 if direction_actuelle == "RENTRER" else s_piston_m2
        
        # Vitesse théorique de la tige (en m/s puis mm/s)
        vitesse_tige_ms = q_m3s_calcul / s_active_m2 if s_active_m2 > 0 else 0
        vitesse_theorique_mm_s = vitesse_tige_ms * 1000.0

        if direction_actuelle == "RENTRER":
            force_kn = (pression_pa * s_tige_m2) / 1000.0
            texte_force = f"Force Traction : {force_kn:.1f} kN"
            couleur_force = "#2563eb"
            # Déplacement basé sur le débit de l'engin
            st.session_state.course_verin_mm = max(0.0, st.session_state.course_verin_mm - (q_engin * 0.4))
            
        elif direction_actuelle == "SORTIR":
            force_kn = (pression_pa * s_piston_m2) / 1000.0
            texte_force = f"Force Poussee : {force_kn:.1f} kN"
            couleur_force = "#b91c1c"
            # Déplacement basé sur le débit de l'engin
            st.session_state.course_verin_mm = min(70.0, st.session_state.course_verin_mm + (q_engin * 0.4))
            
        else:
            force_kn = (pression_pa * s_piston_m2) / 1000.0
            texte_force = f"Force Poussee (Fige) : {force_kn:.1f} kN"
            couleur_force = "#475569"


            
        # --- ENGINE GRAPHIQUE MATPLOTLIB : NORME ISO 1219 RECALCULÉE ---
        fig_hyd, ax_hyd = plt.subplots(figsize=(6, 5), dpi=100)
        ax_hyd.set_xlim(-10, 200)
        ax_hyd.set_ylim(-100, 100)
        ax_hyd.axis('off')

        # Configuration dynamique des couleurs (Rouge = Haute Pression, Bleu = Basse Pression)
        c_p = "#ef4444" 
        c_t = "#2563eb" 
        c_ch_a = "#ef4444" if direction_actuelle == "SORTIR" else "#2563eb"
        c_ch_b = "#ef4444" if direction_actuelle == "RENTRER" else "#2563eb"

        # === 1. DESSIN DE LA RÉGLETTE DE MESURE DE LA COURSE ===
        y_reglette = 60.0
        x_verin_origine = 100.0
        ax_hyd.plot([x_verin_origine, x_verin_origine + 70.0], [y_reglette, y_reglette], color="#475569", linewidth=2)
        
        for mm in range(0, 71, 10):
            x_grad = x_verin_origine + mm
            ax_hyd.plot([x_grad, x_grad], [y_reglette, y_reglette + 4.0], color="#475569", linewidth=1.5)
            if mm == 0:
                ax_hyd.text(x_grad, y_reglette + 8.0, "0mm", fontsize=7, fontweight="bold", color="#64748b", ha="center")
            elif mm == 70:
                ax_hyd.text(x_grad, y_reglette + 8.0, "70mm", fontsize=7, fontweight="bold", color="#64748b", ha="center")

        # Index mobile rouge lié au piston principal
        course_piston_mm = st.session_state.course_verin_mm
        x_piston_actuel = x_verin_origine + course_piston_mm
        ax_hyd.arrow(x_piston_actuel, y_reglette + 6.0, 0.0, -5.0, head_width=2.5, head_length=2.0, fc="#dc2626", ec="#dc2626", zorder=5)

        # === 2. DESSIN DU CORPS DU VÉRIN DOUBLE EFFET ===
        ax_hyd.add_patch(plt.Rectangle((x_verin_origine-5, 20.0), 85.0, 30.0, facecolor="white", edgecolor="black", linewidth=2, zorder=3))
        # Piston interne mobile
        ax_hyd.add_patch(plt.Rectangle((x_piston_actuel , 21.0), 6.0, 28.0, facecolor="#94a3b8", edgecolor="none", zorder=4))
        # Tige du vérin
        ax_hyd.add_patch(plt.Rectangle((x_piston_actuel, 31.0), 95.0, 8.0, facecolor="#94a3b8", edgecolor="none", zorder=4))
        
        # Affichage dynamique de la force sous le vérin
        ax_hyd.text(x_verin_origine + 35.0, -2.0, texte_force, fontsize=9, fontweight="bold", color=couleur_force, ha="center")

        # === 3. DISTRIBUTEUR 4/2 NORMALISÉ ISO 1219 (DEUX CASES ADJACENTES) ===
        # Positionnement des boîtes (Chaque case fait 30x30)
        # Case Gauche (x de 10 à 40, y de -30 à 0) | Case Droite (x de 40 à 70, y de -30 à 0)
        y_dist_top = 0.0
        y_dist_bot = -30.0
        ax_hyd.add_patch(plt.Rectangle((10, y_dist_bot), 30, 30, fill=False, edgecolor="black", linewidth=2, zorder=3))
        ax_hyd.add_patch(plt.Rectangle((40, y_dist_bot), 30, 30, fill=False, edgecolor="black", linewidth=2, zorder=3))
        ax_hyd.plot([40, 40], [y_dist_bot, y_dist_top], color="black", linestyle="--", linewidth=1.5, zorder=4)
        ax_hyd.text(40, y_dist_top +20.0, "Distributeur 4/2", fontsize=9, fontweight="bold", color="#475569", ha="center")

        # --- Flèches de flux internes de la Case Droite (Repos / Sortir) ---
        ax_hyd.annotate('', xy=(47.5, y_dist_top - 2), xytext=(47.5, y_dist_bot + 2), arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
        ax_hyd.annotate('', xy=(62.5, y_dist_bot + 2), xytext=(62.5, y_dist_top - 2), arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))

        # --- Flèches de flux internes de la Case Gauche (Travail / Rentrer) ---
        ax_hyd.annotate('', xy=(32.5, y_dist_top - 2), xytext=(17.5, y_dist_bot + 2), arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))
        ax_hyd.annotate('', xy=(17.5, y_dist_bot + 2), xytext=(32.5, y_dist_top - 2), arrowprops=dict(arrowstyle="->", lw=1.5, color='black'))

        # Organes de commande (Levier à gauche, ressort à droite)
        # Levier mécanique réactif
        if direction_actuelle == "RENTRER":
            ax_hyd.plot([10, 2], [-15, -2], color="#475569", linewidth=3)
            ax_hyd.plot([2], [-2], marker="o", color="#dc2626", markersize=8)
        else:
            ax_hyd.plot([10, 5], [-15, -5], color="#475569", linewidth=3)
            ax_hyd.plot([5], [-5], marker="o", color="#dc2626", markersize=8)
            
        # Ressort de rappel (à droite de la case droite)
        rx = [70, 72, 71, 73, 72, 74, 73, 75]
        ry = [-15, -13, -17, -13, -17, -13, -17, -15]
        ax_hyd.plot(rx, ry, color="black", linewidth=1.2)

        # === 4. DESSIN DE LA POMPE HYDRAULIQUE ET DU RÉSERVOIR (ISO 1219) ===
        # Pompe (Cercle parfait avec triangle vers le haut) centré en (47.5, -65)
        x_pompe, y_pompe = 47.5, -65.0
        ax_hyd.add_patch(plt.Circle((x_pompe, y_pompe), 8.0, fill=False, edgecolor="black", linewidth=2, zorder=4))
        ax_hyd.fill([x_pompe, x_pompe - 4.0, x_pompe + 4.0], [y_pompe + 8.0, y_pompe + 1.0, y_pompe + 1.0], color="black", zorder=5)
        ax_hyd.text(x_pompe - 12.0, y_pompe - 3.0, "Pompe", fontsize=8, fontweight="bold", color="#475569", ha="right")

        # Conduite d'aspiration et bac de réserve d'aspiration sous la pompe
        ax_hyd.plot([x_pompe, x_pompe], [y_pompe - 8.0, -85.0], color="black", linewidth=1.5)
        ax_hyd.plot([x_pompe - 6.0, x_pompe - 6.0, x_pompe + 6.0, x_pompe + 6.0], [-80.0, -86.0, -86.0, -80.0], color="black", linewidth=2)

        # Réservoir principal de retour (T) distant, ouvert vers le haut
        x_res, y_res = 62.5, -70.0
        ax_hyd.plot([x_res - 6.0, x_res - 6.0, x_res + 6.0, x_res + 6.0], [y_res + 5.0, y_res - 5.0, y_res - 5.0, y_res + 5.0], color="black", linewidth=2)
        ax_hyd.text(x_res + 10.0, y_res - 3.0, "Réservoir\n(Tank)", fontsize=8, color="#475569", ha="left")

        # === 5. COULEURS DES CANALISATIONS COHÉRENTES ET ADAPTATIVES ===
        # Orifices fixes du distributeur référencés sur la case active (Droite par défaut ou Gauche si actionné)
        x_offset = 0.0 if direction_actuelle == "RENTRER" else 30.0
        
        x_P = 17.5 + x_offset
        x_T = 32.5 + x_offset
        x_A = 17.5 + x_offset
        x_B = 32.5 + x_offset

        # Lignes d'alimentation (Du bas vers le distributeur)
        ax_hyd.plot([x_pompe, x_pompe, x_P, x_P], [y_pompe + 8.0, -45.0, -45.0, y_dist_bot], color=c_p, linewidth=3, zorder=2)
        ax_hyd.plot([x_T, x_T, x_res, x_res], [y_dist_bot, -40.0, -40.0, y_res - 2.0], color=c_t, linewidth=3, zorder=2)

        # Lignes d'utilisation (Du distributeur vers le vérin)
        # Orifice A va à la chambre arrière (fond du vérin x = 103)
        ax_hyd.plot([x_A, x_A, 98.0, 98.0], [y_dist_top, 10.0, 10.0, 20.0], color=c_ch_a, linewidth=3, zorder=2)
        # Orifice B va à la chambre avant (côté tige du vérin x = 167)
        ax_hyd.plot([x_B, x_B, 177.0, 177.0], [y_dist_top, 5.0, 5.0, 20.0], color=c_ch_b, linewidth=3, zorder=2)

        # Repères textuels normalisés des ports
        ax_hyd.text(x_P, y_dist_bot - 6.0, "P", fontsize=8, fontweight="bold", ha="center")
        ax_hyd.text(x_T, y_dist_bot - 6.0, "T", fontsize=8, fontweight="bold", ha="center")
        ax_hyd.text(x_A, y_dist_top + 2.0, "A", fontsize=8, fontweight="bold", ha="center")
        ax_hyd.text(x_B, y_dist_top + 2.0, "B", fontsize=8, fontweight="bold", ha="center")

        # Flèche de flux dynamique interne sur le piston
        if q_engin > 1.0 and direction_actuelle == "SORTIR":
            ax_hyd.arrow(x_piston_actuel + 8.0, 35.0, 5.0, 0.0, head_width=2.0, head_length=2.0, fc="white", ec="white", zorder=5)


        # === 6. CALCULS PHYSIQUES ET INCRIÉMENTATION DU CHRONOMÈTRE ===
        if vitesse_theorique_mm_s > 0:
            if direction_actuelle == "SORTIR" and st.session_state.course_verin_mm >= 70.0:
                # Verrouillage du temps au maximum exact pour 70mm
                st.session_state.temps_simulation = 70.0 / vitesse_theorique_mm_s
            elif direction_actuelle == "RENTRER" and st.session_state.course_verin_mm <= 0.0:
                # Verrouillage du temps à 0 en position initiale
                st.session_state.temps_simulation = 0.0
            else:
                # En mouvement : calcul dynamique standard
                st.session_state.temps_simulation = st.session_state.course_verin_mm / vitesse_theorique_mm_s
        else:
            # Si le débit est mis à 0, on garde la dernière valeur de temps enregistrée
            pass

        # Gestion de la vitesse effective lors des butées mécaniques
        if direction_actuelle == "SORTIR" and st.session_state.course_verin_mm >= 70.0:
            vitesse_effective_mm_s = 0.0
            texte_vitesse = "Vitesse : 0.0 mm/s (Butée Max)"
            couleur_vit = "#475569"
        elif direction_actuelle == "RENTRER" and st.session_state.course_verin_mm <= 0.0:
            vitesse_effective_mm_s = 0.0
            texte_vitesse = "Vitesse : 0.0 mm/s (Butée Min)"
            couleur_vit = "#475569"
        elif direction_actuelle == "STOP":
            vitesse_effective_mm_s = 0.0
            texte_vitesse = "Vitesse : 0.0 mm/s (Immobile)"
            couleur_vit = "#475569"
        else:
            vitesse_effective_mm_s = vitesse_theorique_mm_s
            signe = "+" if direction_actuelle == "SORTIR" else "-"
            texte_vitesse = f"Vitesse : {signe}{vitesse_effective_mm_s:.1f} mm/s"
            couleur_vit = "#b91c1c" if direction_actuelle == "SORTIR" else "#2563eb"


        # === 7. RE-DESSIN ET AFFICHAGE DÉFINITIF SUR LE GRAPHIC ===

        if vitesse_theorique_mm_s > 0:
            if direction_actuelle == "SORTIR" and st.session_state.course_verin_mm >= 70.0:
                # Verrouillage du temps au maximum exact pour 70mm
                st.session_state.temps_simulation = 70.0 / vitesse_theorique_mm_s
            elif direction_actuelle == "RENTRER" and st.session_state.course_verin_mm <= 0.0:
                # Verrouillage du temps à 0 en position initiale
                st.session_state.temps_simulation = 0.0
            else:
                # En mouvement : calcul dynamique standard
                st.session_state.temps_simulation = st.session_state.course_verin_mm / vitesse_theorique_mm_s
        else:
            # Si le débit est mis à 0, on garde la dernière valeur de temps enregistrée
            pass

        # Gestion de la vitesse effective lors des butées mécaniques
        if direction_actuelle == "SORTIR" and st.session_state.course_verin_mm >= 70.0:
            vitesse_effective_mm_s = 0.0
            texte_vitesse = "Vitesse : 0.0 mm/s (Butée Max)"
            couleur_vit = "#475569"
        elif direction_actuelle == "RENTRER" and st.session_state.course_verin_mm <= 0.0:
            vitesse_effective_mm_s = 0.0
            texte_vitesse = "Vitesse : 0.0 mm/s (Butée Min)"
            couleur_vit = "#475569"
        elif direction_actuelle == "STOP":
            vitesse_effective_mm_s = 0.0
            texte_vitesse = "Vitesse : 0.0 mm/s (Immobile)"
            couleur_vit = "#475569"
        else:
            vitesse_effective_mm_s = vitesse_theorique_mm_s
            signe = "+" if direction_actuelle == "SORTIR" else "-"
            texte_vitesse = f"Vitesse : {signe}{vitesse_effective_mm_s:.1f} mm/s"
            couleur_vit = "#b91c1c" if direction_actuelle == "SORTIR" else "#2563eb"

        # === 7. RE-DESSIN ET AFFICHAGE DÉFINITIF SUR LE GRAPHIC ===
        ax_hyd.text(x_verin_origine + 35.0, -2.0, texte_force, fontsize=9, fontweight="bold", color=couleur_force, ha="center")

        # Affichage des textes en haut à gauche
        ax_hyd.text(-5, 85, f"T = {st.session_state.temps_simulation:.3f} s", fontsize=10, fontweight="bold", color="#1e293b", ha="left")
        ax_hyd.text(-5, 73, texte_vitesse, fontsize=9.5, fontweight="bold", color=couleur_vit, ha="left")
        ax_hyd.text(-5, 61, f"Débit Pompe : {q_engin:.1f} L/min", fontsize=8.5, color="#64748b", ha="left")

        # Rendu final sur l'interface Streamlit
        st.pyplot(fig_hyd)
           
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
            st.rerun()

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





with tab4:
    st.header("Carburateur moteur et simulation a effet Venturi")
    st.write("Analyse thermodynamique des lois de Bernoulli appliquees a l'admission moteur et a la carburation thermique.")

    # =====================================================================
    # --- 1. BANQUE DE DONNÉES DES FLUIDES DE BERNOULLI ---
    # =====================================================================
    if "fluides_bernoulli" not in st.session_state:
        st.session_state.fluides_bernoulli = {
            "Eau pure (Liquide)": {"rho": 1000.0, "color": "#0284c7", "bg": "#e0f2fe", "nu": 1.0e-6},
            "Huile moteur (Liquide)": {"rho": 850.0, "color": "#b45309", "bg": "#fef3c7", "nu": 6.0e-5},
            "Mercure (Liquide lourd)": {"rho": 13600.0, "color": "#475569", "bg": "#e2e8f0", "nu": 1.1e-7},
            "Essence (Liquide leger)": {"rho": 750.0, "color": "#16a34a", "bg": "#dcfce7", "nu": 6.0e-7},
            "Glycerine (Liquide visqueux)": {"rho": 1260.0, "color": "#7c3aed", "bg": "#f3e8ff", "nu": 1.18e-3},
            "Air sec (Gaz standard)": {"rho": 1.2, "color": "#38bdf8", "bg": "#fafafa", "nu": 1.5e-5},
            "Dioxyde de carbone CO2 (Gaz)": {"rho": 1.98, "color": "#94a3b8", "bg": "#f1f5f9", "nu": 8.0e-6},
            "Helium (Gaz ultra-leger)": {"rho": 0.178, "color": "#f43f5e", "bg": "#fff1f2", "nu": 1.2e-4},
            "Neon (Gaz rare)": {"rho": 0.90, "color": "#ea580c", "bg": "#fff7ed", "nu": 3.5e-5},
            "Propane (Gaz lourd)": {"rho": 1.88, "color": "#0d9488", "bg": "#f0fdfa", "nu": 4.5e-6}
        }
        st.session_state.nom_fluide_actif = "Eau pure (Liquide)"

    fluides_dict = st.session_state.fluides_bernoulli

    # Choice du mode d'evaluation pour l'Atelier 4
    mode_selectionne_tab4 = st.radio(
        "Mode de fonctionnement de l'Atelier 4 :",
        ["Mode Normal (Libre)", "Mode Evaluation (Aleatoire)"],
        key="radio_mode_tab4"
    )
    
    st.markdown("---")

    # =====================================================================
    # --- 2. CONFIGURATION DOUBLE COLONNE DE L'ONGLET DE CARBURATION ---
    # =====================================================================
    col_gauche_t4, col_droite_t4 = st.columns(2)

    with col_gauche_t4:
        st.subheader("1. Reglages Hydrodynamiques et Bernoulli")
        
        # --- BLOC HORLOGE D'ANIMATION EN CONTINU ---
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=200, limit=1000, key="horloge_animation_billes_t4")
        except ImportError:
            pass

        st.button("ACTUALISER L'ANIMATION (FAIRE COULER LE FLUIDE)", key="btn_marche_forcee_billes_t4", use_container_width=True)

        # Lecture de vos curseurs de configuration
        var_debit_b3 = st.slider("Debit volumique (L/s) :", min_value=0.1, max_value=15.0, value=5.0, step=0.1, key="slide_q_t4")
        var_z2_b3 = st.slider("Denivele Sortie Z2 (m) :", min_value=-5.0, max_value=5.0, value=0.0, step=0.01, key="slide_z2_t4")
        var_d1_b3 = st.slider("Diametre Entree D1 (mm) :", min_value=1.0, max_value=500.0, value=80.0, step=1.0, key="slide_d1_t4")
        var_d2_b3 = st.slider("Diametre Etranglement D2 (mm) :", min_value=1.0, max_value=500.0, value=40.0, step=1.0, key="slide_d2_t4")
        
        liste_noms_fluides = list(fluides_dict.keys())
        nom_selectionne = st.selectbox("CHOISIR LE FLUIDE...", liste_noms_fluides, index=liste_noms_fluides.index(st.session_state.nom_fluide_actif))
        st.session_state.nom_fluide_actif = nom_selectionne

        f_actif = fluides_dict[st.session_state.nom_fluide_actif]

        # --- MOTEUR ANALYTIQUE EN DIRECT DES CURSEURS ---
        q_m3s = float(var_debit_b3) / 1000.0
        s1_m2 = np.pi * ((float(var_d1_b3) / 1000.0) / 2.0)**2
        s2_m2 = np.pi * ((float(var_d2_b3) / 1000.0) / 2.0)**2
        
        v1_vitesse = q_m3s / s1_m2 if s1_m2 > 0 else 0.0
        v2_vitesse = q_m3s / s2_m2 if s2_m2 > 0 else 0.0
        
        # Loi de Bernoulli complete entre l'entree (1) et la sortie decalee (3)
        g_gravite = 9.81
        delta_p_pa = 0.5 * f_actif["rho"] * (v2_vitesse**2 - v1_vitesse**2) + (f_actif["rho"] * g_gravite * float(var_z2_b3))

        st.markdown("**2. Profil de l'Ecoulement : Tube Venturi**")
        
        # Gestion de la memoire de translation des billes
        if "billes_bernoulli_t4" not in st.session_state:
            st.session_state.billes_bernoulli_t4 = [i * (440.0 / 30.0) for i in range(30)]
            
        vitesse_billes = max(0.5, float(var_debit_b3) * 0.8)
        st.session_state.billes_bernoulli_t4 = [(x + vitesse_billes) % 440.0 for x in st.session_state.billes_bernoulli_t4]

        # Figure de duplication Matplotlib calee sur vos dimensions exactes
        fig_vent, ax_vent = plt.subplots(figsize=(6.5, 3.8), dpi=100)
        ax_vent.clear()

        # Titre en grand bleu majuscule conforme a l'image cible
        titre_majuscule = str(st.session_state.nom_fluide_actif).upper()
        ax_vent.text(220.0, 215.0, titre_majuscule, fontsize=12, fontname="Arial", color="#1e3a8a", fontweight="bold", ha="center")

        # Proportions geometriques des diametres indexes sur D1, D2 et la denivellation Z2
        h_entree_px = max(15.0, min(55.0, float(var_d1_b3) * 0.5))
        h_col_px = max(2.0, min(45.0, float(var_d2_b3) * 0.5))
        dy_denivele = max(-40.0, min(40.0, float(var_z2_b3) * 10.0))
        
        y_milieu_tube = 80.0
        
        # Geometrie exacte du sablier/diabolo de votre capture d'ecran
        px_v = [0.0, 140.0, 200.0, 260.0, 320.0, 440.0, 440.0, 320.0, 260.0, 200.0, 140.0, 0.0]
        py_v = [
            y_milieu_tube - h_entree_px, y_milieu_tube - h_entree_px, y_milieu_tube - h_col_px, y_milieu_tube - h_col_px, y_milieu_tube - h_entree_px + dy_denivele, y_milieu_tube - h_entree_px + dy_denivele,
            y_milieu_tube + h_entree_px + dy_denivele, y_milieu_tube + h_entree_px + dy_denivele, y_milieu_tube + h_col_px, y_milieu_tube + h_col_px, y_milieu_tube + h_entree_px, y_milieu_tube + h_entree_px
        ]
        ax_vent.fill(px_v, py_v, color=f_actif["bg"], edgecolor="#1e293b", linewidth=2.5, zorder=1)

        # DUPLICATION DES TUBES : Le deuxieme tube est replace a DROITE (x = 340 a 360) sur la section inclinee
        # Tube de gauche (Entree - x: 45 a 65)
        y_raccord_1 = y_milieu_tube + h_entree_px
        ax_vent.plot([45.0, 45.0], [y_raccord_1, 195.0], color="#475569", linewidth=1.5, zorder=2)
        ax_vent.plot([65.0, 65.0], [y_raccord_1, 195.0], color="#475569", linewidth=1.5, zorder=2)
        
        # Tube de droite (Sortie decalee - x: 340 a 360) qui suit le denivele dy_denivele
        y_raccord_3 = y_milieu_tube + h_entree_px + dy_denivele
        ax_vent.plot([340.0, 340.0], [y_raccord_3, 195.0], color="#475569", linewidth=1.5, zorder=2)
        ax_vent.plot([360.0, 360.0], [y_raccord_3, 195.0], color="#475569", linewidth=1.5, zorder=2)

        # Niveaux hydrostatiques des deux colonnes cales sur votre repere visuel
        h_base_piezo = 145.0
        h_liquide_1 = h_base_piezo + max(0.0, float(var_debit_b3) * 1.8)
        
        # Calcul de la hauteur de sortie affectee par la section et le denivele
        facteur_perte = min(55.0, abs(delta_p_pa) * 0.00015)
        h_liquide_2 = max(y_raccord_3 + 5.0, h_liquide_1 - facteur_perte)

        # Remplissage des fluides
        ax_vent.fill_between([45.5, 64.5], y_raccord_1 - 1, h_liquide_1, color=f_actif["bg"], zorder=1)
        ax_vent.fill_between([340.5, 359.5], y_raccord_3 - 1, h_liquide_2, color=f_actif["bg"], zorder=1)
        ax_vent.plot([45.5, 64.5], [h_liquide_1, h_liquide_1], color=f_actif["color"], linewidth=2.5, zorder=3)
        ax_vent.plot([340.5, 359.5], [h_liquide_2, h_liquide_2], color=f_actif["color"], linewidth=2.5, zorder=3)

        # Graduations de 0.0 a 4.0 alignees comme sur votre capture
        for h_rep in np.linspace(h_base_piezo, 185.0, 5):
            val_grad = (h_rep - h_base_piezo) / 10.0
            ax_vent.plot([41.0, 45.0], [h_rep, h_rep], color="#475569", linewidth=1)
            ax_vent.plot([336.0, 340.0], [h_rep, h_rep], color="#475569", linewidth=1)
            ax_vent.text(39.0, h_rep, f"{val_grad:.1f}", fontname="Arial", fontsize=7, ha="right", va="center", color="#475569")
            ax_vent.text(334.0, h_rep, f"{val_grad:.1f}", fontname="Arial", fontsize=7, ha="right", va="center", color="#475569")

        # 3. Repartition et deplacement des billes bleues a l'interieur du goulet
        for x_bille in st.session_state.billes_bernoulli_t4:
            if x_bille < 140.0:
                y_base_bas = y_milieu_tube - h_entree_px
                y_base_haut = y_milieu_tube + h_entree_px
            elif 140.0 <= x_bille < 200.0:
                f_c = (x_bille - 140.0) / 60.0
                h_dyn = h_entree_px - (f_c * (h_entree_px - h_col_px))
                y_base_bas = y_milieu_tube - h_dyn
                y_base_haut = y_milieu_tube + h_dyn
            elif 200.0 <= x_bille < 260.0:
                y_base_bas = y_milieu_tube - h_col_px
                y_base_haut = y_milieu_tube + h_col_px
            elif 260.0 <= x_bille < 320.0:
                f_c = (x_bille - 260.0) / 60.0
                h_dyn = h_col_px + (f_c * (h_entree_px - h_col_px))
                y_base_bas = y_milieu_tube - h_dyn + (dy_denivele * 0.5 * f_c)
                y_base_haut = y_milieu_tube + h_dyn + (dy_denivele * 0.5 * f_c)
            else:
                y_base_bas = y_milieu_tube - h_entree_px + dy_denivele
                y_base_haut = y_milieu_tube + h_entree_px + dy_denivele

            for ecart in [0.25, 0.5, 0.75]:
                y_bille = y_base_bas + (y_base_haut - y_base_bas) * ecart
                ax_vent.plot([x_bille], [y_bille], marker="o", color=f_actif["color"], markersize=3.5, zorder=4)

        # Affichage des textes de vitesse et pression basse
        ax_vent.text(20.0, 15.0, f"v1 = {v1_vitesse:.2f} m/s", fontname="Arial", fontsize=9, color="black", fontweight="bold", ha="center")
        ax_vent.text(220.0, 15.0, f"v2 = {v2_vitesse:.2f} m/s", fontname="Arial", fontsize=9, color="black", fontweight="bold", ha="center")
        ax_vent.text(440.0, 15.0 + dy_denivele, f"v3 = {v1_vitesse:.2f} m/s", fontname="Arial", fontsize=9, color="black", fontweight="bold", ha="center")
        ax_vent.text(220.0, -15.0, f"Pression differentielle (Delta P) : {abs(delta_p_pa):.1f} Pa", fontname="Arial", color="#b45309", fontsize=9, fontweight="bold", ha="center")

        # Fleche d'entree de flux indicatrice gauche
        ax_vent.arrow(-25.0, y_milieu_tube, 12.0, 0.0, head_width=6.0, head_length=6.0, fc="#0284c7", ec="#0284c7", zorder=5)

        ax_vent.set_xlim(-30.0, 460.0)
        ax_vent.set_ylim(-25.0, 230.0)
        ax_vent.axis("off")
        st.pyplot(fig_vent)
        plt.close(fig_vent)

    with col_droite_t4:
        st.subheader("2. Carburateur Moteur et Simulation")
       
        if "Normal" in mode_selectionne_tab4:
            var_regime_moteur = st.slider("Regime du moteur (Tr/min) :", min_value=800, max_value=6000, value=1000, step=100, key="slide_regime_t4")
            var_obstruction_air = st.slider("Encrassement  du filtre a air (%) :", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key="slide_obst_t4")
            var_fissure_pipe = st.slider("Defaut d'etancheite collecteur (mm) :", min_value=0.0, max_value=3.0, value=0.0, step=0.2, key="slide_fissure_t4")
            var_colmatage_gicleur = st.slider("Encrassement du gicleur (%) :", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key="slide_colmatage_t4")
        else:
            var_regime_moteur = 3000
            var_obstruction_air = 0.0
            var_fissure_pipe = 0.0
            var_colmatage_gicleur = 0.0
            
            st.markdown(f"* **Regime force de rotation :** {var_regime_moteur} Tr/min")
            st.markdown(f"* **Obstruction nominale du filtre :** {var_obstruction_air:.0f} %")
            st.markdown(f"* **Fissure du collecteur d'admission :** {var_fissure_pipe:.2f} mm")
            st.markdown(f"* **Colmatage du gicleur d'essence :** {var_colmatage_gicleur:.0f} %")

        # --- MOTEUR PHYSIQUE ET DIAGNOSTIC DE CARBURATION MOTEUR ---
        rpm = float(var_regime_moteur)
        obs_air = float(var_obstruction_air)
        fissure = float(var_fissure_pipe)
        col_gicleur = float(var_colmatage_gicleur)

        vitesse_air_amont = 4.0 + (rpm / 6000.0) * 16.0
        vitesse_air_col = vitesse_air_amont * 2.5
        coeff_air = max(0.1, 1.0 - (obs_air / 100.0))
        coeff_essence = max(0.0, 1.0 - (col_gicleur / 100.0))

        vitesse_air_col_reelle = vitesse_air_col * coeff_air
        pression_col = 1.013e5 - 0.5 * 1.2 * (vitesse_air_col_reelle**2 - (vitesse_air_amont * coeff_air)**2)

        if obs_air > 50.0:
            pression_col -= (obs_air / 100.0) * 40000.0 * (rpm / 6000.0)

        depression_bar = max(0.0, (1.013e5 - pression_col) / 100000.0)
        if fissure > 0.0:
            depression_bar = depression_bar * max(0.05, 1.0 - (fissure / 1.5))

        nombre_gouttes = int(depression_bar * 140.0 * coeff_essence)

        # Arbitrage de panne automatique
        if col_gicleur >= 75.0 or (depression_bar < 0.005 and fissure > 0.0):
            etat_combustion = "ETEINT"
        elif obs_air >= 80.0:
            etat_combustion = "NOYE"
        elif fissure >= 1.0 or (nombre_gouttes < 20 and rpm > 1500):
            etat_combustion = "PAUVRE"
        else:
            etat_combustion = "NORMAL"

        # --- RENDER DES TEXTES ET ANALYSES DES PHASES ---
        st.write("---")
        st.markdown("**Donnees d'admission du Col du Venturi :**")

        st.info(f"Depression col : -{depression_bar:.3f} bar | Vitesse air col : {vitesse_air_col_reelle:.1f} m/s")

        st.markdown(f"**Etat de fonctionnement du moteur :**")
        if etat_combustion == "NORMAL":
            st.success(
                f"FONCTIONNEMENT NORMAL : Modele nominal de carburation.\n\n"
                f"Le melange air/essence est optimal pour assurer une combustion complete. "
                f"Rendement thermique ideal de l'engin a {rpm:.0f} Tr/min."
            )
        elif etat_combustion == "NOYE":
            txt_p = f"PHASE 3 (Noyade) : Filtre obstrue a {obs_air:.1f}%. Le manque d'air genere un vide artificiel de -{depression_bar:.3f} bar. L'essence sature le conduit et noie la bougie : fumee noire."
            st.error(f"SITUATION MATÉRIEL : {etat_combustion}\n\n{txt_p}")
        elif etat_combustion == "PAUVRE":
            txt_p = f"PHASE 3 (Prise d'air) : La fissure de {fissure:.1f} mm detruit la depression Venturi (-{depression_bar:.3f} bar). L'essence s'effondre a {nombre_gouttes} billes, le melange est trop pauvre."
            st.warning(f"SITUATION MATÉRIEL : {etat_combustion}\n\n{txt_p}")
        elif etat_combustion == "ETEINT":
            txt_p = f"PHASE 3 (Obstruction) : Le gicleur est colmate a {col_gicleur:.1f}%. Plus aucune particule de carburant ne peut monter. Faute de carburant, le cycle s'interrompt et le moteur cale."
            st.error(f"SITUATION MATÉRIEL : {etat_combustion}\n\n{txt_p}")


        fig_carb, ax_carb = plt.subplots(figsize=(6.5, 3.2), dpi=100)
        ax_carb.clear()

        # 1. Dessin des conduits principaux du carburateur (Forme Venturi)
        px_c = [40.0, 140.0, 180.0, 240.0, 340.0, 340.0, 240.0, 180.0, 140.0, 40.0]
        py_c = [35.0, 35.0, 48.0, 48.0, 35.0, 115.0, 102.0, 102.0, 115.0, 115.0]
        ax_carb.fill(px_c, py_c, color="#f8fafc", edgecolor="#1e293b", linewidth=2, zorder=1)

        # Tracé des prolongements droits vers le collecteur d'admission
        ax_carb.plot([340.0, 440.0], [35.0, 20.0 + (dy_denivele * 0.3)], color="#1e293b", linewidth=2, zorder=1)
        ax_carb.plot([340.0, 440.0], [115.0, 130.0 + (dy_denivele * 0.3)], color="#1e293b", linewidth=2, zorder=1)

        # 2. Rendu du Filtre a Air (A gauche - x: 5 a 40)
        ax_carb.add_patch(plt.Rectangle((5.0, 25.0), 35.0, 100.0, facecolor="#e2e8f0", edgecolor="black", linewidth=1.5, zorder=3))
        ax_carb.text(22.5, 130.0, "Filtre Air", fontname="Arial", fontsize=7, fontweight="bold", ha="center")
        # Stries noires du filtre
        for s_y in np.linspace(30.0, 120.0, 12):
            ax_carb.plot([8.0, 37.0], [s_y, s_y], color="black", linewidth=2, zorder=4)

        # Fleches bleues indicatrices d'entree d'air amont
        for f_y in [60.0, 75.0, 90.0]:
            ax_carb.arrow(-15.0, f_y, 10.0, 0.0, head_width=4.0, head_length=4.0, fc="#0284c7", ec="#0284c7", zorder=5)

        x_centre_col = 210.0  # Centrage exact au col du Venturi (entre 180 et 240)

        # La cuve inferieure verte recentree au col
        ax_carb.add_patch(plt.Rectangle((x_centre_col - 21.0, -25.0), 42.0, 40.0, facecolor="#10b981", edgecolor="#047857", linewidth=1.5, zorder=2))
        
        # Le flotteur orange dans la cuve
        ax_carb.add_patch(plt.Rectangle((x_centre_col - 16.0, -10.0), 32.0, 15.0, facecolor="#f97316", edgecolor="#c2410c", linewidth=1, zorder=3))
        
        # Le tube de gicleur vertical en cuivre (zorder=6 pour masquer les traits du tube d'air)
        ax_carb.plot([x_centre_col, x_centre_col], [-15.0, 71.0], color="#b45309", linewidth=3.5, solid_capstyle="butt", zorder=6)
        
        # La buse d'injection rouge : calee au sommet exact du tube (y=71, zorder=7)
        ax_carb.plot([x_centre_col - 3.0, x_centre_col + 3.0], [71.0, 71.0], color="#dc2626", linewidth=2.5, zorder=7) 
        
        # Le diffuseur vert clair : emboite au-dessus (zorder=8)
        ax_carb.plot([x_centre_col - 1.5, x_centre_col + 1.5], [73.5, 73.5], color="#22c55e", linewidth=4.0, solid_capstyle="round", zorder=8)

        # Note pour la suite du script : Le papillon des gaz rotatif doit etre decale legerement a droite du col (ex: x = 275.0) pour ne pas croiser le gicleur
        angle_papillon = np.radians(20.0 + (rpm / 6000.0) * 50.0)
        x_p1 = 275.0 - 15.0 * np.cos(angle_papillon)
        y_p1 = 75.0 - 15.0 * np.sin(angle_papillon)
        x_p2 = 275.0 + 15.0 * np.cos(angle_papillon)
        y_p2 = 75.0 + 15.0 * np.sin(angle_papillon)
        ax_carb.plot([x_p1, x_p2], [y_p1, y_p2], color="#334155", linewidth=3.5, solid_capstyle="round", zorder=4)

        # 5. ANIMATION DES LIGNES DE FLUX ET AS-PIRATION DES GOUTTES D'ESSENCE
        if "billes_essence_t4" not in st.session_state:
            st.session_state.billes_essence_t4 = []

        # Generation dynamique des billes vertes de carburant basee sur la depression reelle
        if nombre_gouttes > 0 and rpm > 800:
            if len(st.session_state.billes_essence_t4) < nombre_gouttes:
                for _ in range(3):
                    st.session_state.billes_essence_t4.append({
                        "x": 156.0, "y": 68.0, 
                        "vx": np.random.uniform(2.5, 5.0) * coeff_air, 
                        "vy": np.random.uniform(-1.0, 1.0)
                    })

        # Avancement et deplacement des particules dans le flux gazeux
        billes_actives = []
        for b in st.session_state.billes_essence_t4:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            # Confinement visuel des billes dans la pipe d'admission convergente
            if b["x"] < 440.0 and 30.0 < b["y"] < 120.0:
                ax_carb.plot([b["x"]], [b["y"]], marker="o", color="#22c55e", markersize=3, zorder=4)
                billes_actives.append(b)
        st.session_state.billes_essence_t4 = billes_actives

        # Lignes de courant d'air bleues traversant le carburateur
        for l_y in [50.0, 65.0, 85.0, 100.0]:
            t_steps = np.linspace(40, 430, 20)
            px_l = []
            py_l = []
            for xl in t_steps:
                if xl < 140.0: yl = l_y
                elif 140.0 <= xl < 180.0:
                    f = (xl - 140.0) / 40.0
                    h_r = h_entree_px - (f * (h_entree_px - h_col_px))
                    yl = y_milieu_tube + ((l_y - y_milieu_tube) * (h_r / h_entree_px))
                elif 180.0 <= xl < 240.0:
                    yl = y_milieu_tube + ((l_y - y_milieu_tube) * (h_col_px / h_entree_px))
                else:
                    f = min(1.0, (xl - 240.0) / 100.0)
                    yl = y_milieu_tube + ((l_y - y_milieu_tube) * (1.0 + f * 0.2)) + (dy_denivele * 0.3 * f)
                px_l.append(xl)
                py_l.append(yl)
            ax_carb.plot(px_l, py_l, color="#38bdf8", linewidth=1, alpha=0.6, zorder=2)

        x_moteur_ancrage = 440.0
        y_moteur_bas = 15.0 + (dy_denivele * 0.3)
        
        # 6. Rendu du Boitier Cylindre de Combustion de droite parfaitement emboite
        ax_carb.add_patch(plt.Rectangle((x_moteur_ancrage, y_moteur_bas), 110.0, 115.0, facecolor="#f1f5f9", edgecolor="black", linewidth=2, zorder=3))
        
        # Dessin des deux disques pistons de combustion noirs
        piston_color = "#ef4444" if etat_combustion == "NOYE" else ("#22c55e" if etat_combustion == "NORMAL" else "#64748b")
        
        # Coordonnees centrees reajustees a l'interieur du rectangle recale
        ax_carb.plot([x_moteur_ancrage + 35.0], [y_moteur_bas + 60.0], marker="o", color="#475569", markersize=26, zorder=4)
        ax_carb.plot([x_moteur_ancrage + 75.0], [y_moteur_bas + 70.0], marker="o", color="#475569", markersize=26, zorder=4)
        
        # Etiquette de rapport d'etat texte rouge ou verte interne centree
        ax_carb.text(x_moteur_ancrage + 55.0, y_moteur_bas + 62.0, f"MOTEUR\n{etat_combustion}", fontname="Arial", fontsize=7, color=piston_color, fontweight="bold", ha="center", va="center", zorder=5)

        # Ajustement final de la fenetre de tirage
        ax_carb.set_xlim(-20.0, 555.0)
        ax_carb.set_ylim(-30.0, 150.0)
        ax_carb.axis("off")
        
        st.pyplot(fig_carb)
        plt.close(fig_carb)
    # =====================================================================
    # --- 5. INTERFACE TECHNIQUE DU QUESTIONNAIRE DE L'ATELIER 4 ---
    # =====================================================================
    st.write("---")
    st.subheader("Feuille de Route et Questionnaire de Synthese - Atelier 4")

    verrou_h4 = st.session_state.get("v_verrouille_tab4", False)
    
    # Appel dynamique de la fonction 20 questions (10 QCM + 10 Trous)
    res_q4, res_t4 = afficher_questions_carburateur(
        delta_p_pa, obs_air, fissure, col_gicleur, 
        rpm, vitesse_air_col_reelle, depression_bar, 
        etat_combustion, verrouille=verrou_h4
    )

    # =====================================================================
    # --- 6. VALIDATION ET EXPORTATION DU RAPPORT SCELLÉ DE L'ATELIER 4 ---
    # =====================================================================
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_h4 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 4.", 
        key="check_certif_hydro4_official_scelle_final_action", 
        disabled=verrou_h4
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_hydro4_final_click_action", use_container_width=True, disabled=verrou_h4):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_h4:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction analytique du premier bloc (Quiz QCM - 10 points)
            score_q4_brut = 0.0
            lignes_qcm_html = ""
            map_reponses_qcm = {q["id"]: q["rep"] for q in st.session_state.ordre_qcm_hydro4}
            map_enonces_qcm = {q["id"]: q["q"] for q in st.session_state.ordre_qcm_hydro4}

            for idx, (q_id, saisie) in enumerate(res_q4.items(), 1):
                attendu = map_reponses_qcm[q_id]
                enonce = map_enonces_qcm[q_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_q4_brut += 1.0
                    verdict, lbl_style = "CORRECT", "status-pass"
                else:
                    verdict, lbl_style = "INCORRECT", "status-fail"
                lignes_qcm_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            # 2. Correction analytique du second bloc (Textes a trous - 10 points)
            score_t4_brut = 0.0
            lignes_trous_html = ""
            map_reponses_trous = {t["id"]: t["rep"] for t in st.session_state.ordre_trous_hydro4}
            map_enonces_trous = {t["id"]: t["q"] for t in st.session_state.ordre_trous_hydro4}

            for idx, (t_id, saisie) in enumerate(res_t4.items(), 1):
                attendu = map_reponses_trous[t_id]
                enonce = map_enonces_trous[t_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_t4_brut += 1.0
                    verdict, lbl_style = "CORRECT", "status-pass"
                else:
                    verdict, lbl_style = "INCORRECT", "status-fail"
                lignes_trous_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            # Enregistrement des scores coefficients et verrouillage
            st.session_state.score_v4_p1 = round(float(score_q4_brut), 1)
            st.session_state.score_v4_p2 = round(float(score_t4_brut), 1)
            st.session_state.score_final_v4 = round(float(score_q4_brut + score_t4_brut), 1)
            st.session_state.lignes_qcm_html_t4 = lignes_qcm_html
            st.session_state.lignes_trous_html_t4 = lignes_trous_html
            st.session_state.v_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab4", False):
        scr1 = st.session_state.get("score_v4_p1", 0.0)
        scr2 = st.session_state.get("score_v4_p2", 0.0)
        tot_s = st.session_state.get("score_final_v4", 0.0)
        lignes_qcm_html = st.session_state.get("lignes_qcm_html_t4", "")
        lignes_trous_html = st.session_state.get("lignes_trous_html_t4", "")
        
        from datetime import datetime
        timestamp_v4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER CARBURATEUR ET VENTURI SCELLÉ | Note de session : {tot_s:.1f} / 20.0")

        # Elaboration de la page de correction academique HTML (Style Bleu)
        html_content_t4 = f"""<!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Rapport d'Evaluation Carburateur - Atelier 4</title>
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
                    <strong>Module d'Evaluation :</strong> Carburation moteur, theoreme de Bernoulli et effet Venturi (Atelier 4)<br>
                    <strong>Eleve :</strong> {p_eleve} {n_eleve} | <strong>Classe :</strong> {c_eleve}<br>
                    <strong>Fluide d'etude :</strong> {st.session_state.nom_fluide_actif} | <strong>Regime teste :</strong> {rpm:.0f} Tr/min<br>
                    <span style="font-size:11px; opacity:0.8;">Fige et scelle le : {timestamp_v4}</span>
                </div>
            </div>
            
            <div class="section-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 0 0 25px 0;">
                - Note Questionnaire Technologique : <strong>{scr1:.1f} / 10.0</strong><br>
                - Note Synthese de cours a trous : <strong>{scr2:.1f} / 10.0</strong><br>
                - Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20.0</strong>
            </p>

            <div class="section-title">1. Correction detaillee du Questionnaire QCM (Note sur 10)</div>
            <table>
                <thead>
                    <tr><th style="width: 5%; text-align: center;">N°</th><th style="width: 45%;">Enonce de la question posee au sort</th><th style="width: 19%;">Saisie de l'eleve</th><th style="width: 19%;">Attendu academique</th><th style="width: 12%; text-align: center;">Statut</th></tr>
                </thead>
                <tbody>{lignes_qcm_html}</tbody>
            </table>
            <div class="section-title">2. Correction detaillee de la Synthese a trous (Note sur 10)</div>
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
        chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Carburateur_Atelier4_{n_eleve}.html")
        try:
            with open(chemin_sauvegarde, "w", encoding="utf-8") as f: 
                f.write(html_content_t4)
        except Exception: 
            pass

        st.download_button(
            label="Telecharger mon rapport d'evaluation HTML",
            data=html_content_t4,
            file_name=f"Carburateur_Atelier4_{n_eleve}_Copie.html",
            mime="text/html",
            key="btn_download_hydro_t4_final_action",
            use_container_width=True
        )



with tab5:
    st.header("Applications concretes du batiment : Reseaux fluides")
    st.write("Etude comparative entre la distribution sous pression (Eau Potable) et l'evacuation gravitaire a surface libre (PVC), suivie de l'analyse du regime de Reynolds.")

    # =====================================================================
    # --- 1. CONFIGURATION DES QUESTIONS TECHNIQUE (10 QCM + 10 TROUS) ---
    # =====================================================================
    def afficher_questions_plomberie(p_compteur, h_nourrice, n_reynolds, q_total_maison, taux_remplissage, verrouille=False):
        import random
        
        if "ordre_quiz_hydro5" not in st.session_state:
            val_p_statique = f"{max(0.01, p_compteur - (1000.0 * 9.81 * h_nourrice / 100000.0)):.2f}"
            val_rey_str = f"{n_reynolds:.0f}"
            val_q_pvc = f"{q_total_maison:.2f}"
            val_remp_pvc = f"{taux_remplissage:.0f}"
            
            base_cat_qcm_t5 = [
                {"id": "h5_1", "q": "Quelle loi de perte de charge hydrostatique quantifie la baisse de pression liee a l'altitude de la nourrice ?", "options": ["Loi de Pascal", "Principe d'Archimede", "Theoreme de Venturi"], "rep": "Loi de Pascal"},
                {"id": "h5_2", "q": "D'apres vos reglages d'eau potable, calculez la pression statique disponible a la nourrice (bar) :", "options": [val_p_statique, f"{float(val_p_statique)+1.5:.2f}", "0.00"], "rep": val_p_statique},
                {"id": "h5_3", "q": "Le pic de surpression destructeur genere par la fermeture brutale d'une vanne s'appelle le coup de :", "options": ["Belier", "Venturi", "Pascal"], "rep": "Belier"},
                {"id": "h5_4", "q": "D'apres vos reglages au robinet, quel est le nombre de Reynolds Re exact calcule en session :", "options": [val_rey_str, "1500", "5000"], "rep": val_rey_str},
                {"id": "h5_5", "q": "Sous quel nombre de Reynolds le regime d'un fluide est-il considere comme strictement laminaire ?", "options": ["Moins de 2000", "De 2000 a 4000", "Plus de 4000"], "rep": "Moins de 2000"},
                {"id": "h5_6", "q": "Au-dela de Re = 4000, comment qualifie-t-on le regime fluide du jet (debit desordonne) :", "options": ["Turbulent", "Laminaire", "Transitoire"], "rep": "Turbulent"},
                {"id": "h5_7", "q": "Quelle formule normalisee regit la capacite de transport gravitaire a surface libre des tubes PVC ?", "options": ["Manning-Strickler", "Bernoulli", "Loi de Mariotte"], "rep": "Manning-Strickler"},
                {"id": "h5_8", "q": "D'apres vos reglages PVC, quel est le debit total d'evacuation rejete par le batiment (L/s) :", "options": [val_q_pvc, "1.50", "20.00"], "rep": val_q_pvc},
                {"id": "h5_9", "q": "D'apres vos reglages PVC, quel est le taux de remplissage effectif du collecteur d'egout (%) :", "options": [val_remp_pvc, "50", "100"], "rep": val_remp_pvc},
                {"id": "h5_10", "q": "A partir de quel taux de remplissage lineaire le collecteur PVC entre-t-il en charge (glouglou) ?", "options": ["Plus de 70%", "Moins de 30%", "Exactement 50%"], "rep": "Plus de 70%"}
            ]
            
            base_cat_trous_t5 = [
                {"id": "h5t_1", "q": "1. Le deplacement lineaire d'une particule en regime laminaire suit des trajectoires", "options": ["Paralleles", "Tourbillonnantes", "Hachures"], "rep": "Paralleles"},
                {"id": "h5t_2", "q": "2. La resistance d'un fluide face au glissement de ses couches internes definit la", "options": ["Viscosite", "Pression", "Densite"], "rep": "Viscosite"},
                {"id": "h5t_3", "q": "3. Les canalisations gravitaires en PVC evacuent les eaux usees sans contrainte de", "options": ["Pression", "Pente", "Debit"], "rep": "Pression"},
                {"id": "h5t_4", "q": "4. Le raccord de distribution bivalent distribuant l'eau vers les terminaux est la", "options": ["Nourrice", "Vanne", "Cuve"], "rep": "Nourrice"},
                {"id": "h5t_5", "q": "5. L'essor de la rugosite interne des parois de flexibles accroit les pertes de", "options": ["Charge", "Vitesse", "Masse"], "rep": "Charge"},
                {"id": "h5t_6", "q": "6. La celerite de l'onde acoustique lors d'un choc de bélier est liee a l'elasticite du", "options": ["Conduit", "Fluide", " Reservoir"], "rep": "Conduit"},
                {"id": "h5t_7", "q": "7. Une decharge fluide depassant la capacite maximale d'un PVC provoque un", "options": ["Engorgement", "Siphonage", "Bypass"], "rep": "Engorgement"},
                {"id": "h5t_8", "q": "8. Le nombre de Reynolds met en rapport les forces d'inertie et les forces de", "options": ["Viscosite", "Pesanteur", "Tension"], "rep": "Viscosite"},
                {"id": "h5t_9", "q": "9. Pour preserver l'arret des odeurs d'egout, chaque appareil est muni d'un", "options": ["Siphon", "Clapet", "Compteur"], "rep": "Siphon"},
                {"id": "h5t_10", "q": "10. En regime turbulent desordonne, les billes de fluide subissent de fortes", "options": ["Oscillations", "Stagnations", "Compressions"], "rep": "Oscillations"}
            ]
            
            st.session_state.ordre_qcm_hydro5 = list(base_cat_qcm_t5)
            st.session_state.ordre_trous_hydro5 = list(base_cat_trous_t5)
            random.shuffle(st.session_state.ordre_qcm_hydro5)
            random.shuffle(st.session_state.ordre_trous_hydro5)

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            st.markdown("##### Quiz technique de plomberie (10 questions - 10 pts)")
            dict_rep_q5 = {}
            for idx, q_data in enumerate(st.session_state.ordre_qcm_hydro5, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"hydro_t5_q_{q_data['id']}"
                cle_opts = f"opts_hydro5_{q_data['id']}"
                if cle_opts not in st.session_state:
                    opts = list(q_data["options"])
                    random.shuffle(opts)
                    st.session_state[cle_opts] = ["Choisir..."] + opts
                val_p = st.session_state.get(cle_select, "Choisir...")
                sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
                dict_rep_q5[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

        with col_form2:
            st.markdown("##### Synthese de cours a trous (10 trous - 10 pts)")
            dict_trous_5 = {}
            for idx, q_data in enumerate(st.session_state.ordre_trous_hydro5, 1):
                c_text, col_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
                with c_text:
                    st.write(f"{idx}. {q_data['q']}")
                cle_select_t = f"hydro_t5_t_{q_data['id']}"
                cle_opts_t = f"opts_trous5_{q_data['id']}"
                if cle_opts_t not in st.session_state:
                    opts_t = list(q_data["options"])
                    random.shuffle(opts_t)
                    st.session_state[cle_opts_t] = ["Choisir..."] + opts_t
                val_p_t = st.session_state.get(cle_select_t, "Choisir...")
                sel_idx_t = st.session_state[cle_opts_t].index(val_p_t) if val_p_t in st.session_state[cle_opts_t] else 0
                with col_sel:
                    dict_trous_5[q_data["id"]] = st.selectbox("", st.session_state[cle_opts_t], index=sel_idx_t, key=cle_select_t, disabled=verrouille, label_visibility="collapsed")

        return dict_rep_q5, dict_trous_5

    # =====================================================================
    # --- 2. GESTION DE LA MEMOIRE DE SESSION ET MODE D'EXAMEN ---
    # =====================================================================
    if "domaine_actif_b3" not in st.session_state:
        st.session_state.domaine_actif_b3 = "Canalisation Eau Potable (PER / Cuivre)"
        st.session_state.var_pression_compteur = 3.0
        st.session_state.var_h_nourrice = 1.5
        st.session_state.v_ouvert_wc = True
        st.session_state.v_ouvert_sdb = True
        st.session_state.v_ouvert_ce = True

    mode_selectionne_tab5 = st.radio(
        "Mode de fonctionnement de l'Atelier 5 :",
        ["Mode Normal (Libre)", "Mode Evaluation (Aleatoire)"],
        key="radio_mode_tab5"
    )

    # Commande d'aiguillage des deux grands réseaux du bâtiment
    choix_reseau = st.radio(
        "Selectionner la nature de la canalisation du batiment :",
        ["Canalisation Eau Potable (PER / Cuivre)", "Evacuation des Eaux ou Ventilation (PVC)"],
        key="radio_aiguillage_plomberie_tab5"
    )

    if choix_reseau != st.session_state.domaine_actif_b3:
        st.session_state.domaine_actif_b3 = choix_reseau
        if choix_reseau == "Canalisation Eau Potable (PER / Cuivre)":
            st.session_state.var_pression_compteur = 4.0
            st.session_state.var_h_nourrice = 3.0
        else:
            st.session_state.var_pression_compteur = 6.0
            st.session_state.var_h_nourrice = 100.0
        st.rerun()

    st.write("---")

    # =====================================================================
    # --- 3. CONFIGURATION DOUBLE COLONNE DU LIVRET DE PLOMBERIE ---
    # =====================================================================
    col_gauche_plomb, col_droite_plomb = st.columns(2)

    with col_gauche_plomb:
        st.markdown("##### Configuration des infrastructures de l'habitation")
        
        if "Normal" in mode_selectionne_tab5:
            if st.session_state.domaine_actif_b3 == "Canalisation Eau Potable (PER / Cuivre)":
                p_compteur = st.slider("Pression au Compteur (bars) :", min_value=0.5, max_value=5.0, value=float(st.session_state.var_pression_compteur), step=0.1, key="slide_p_compteur")
                h_nourrice = st.slider("Hauteur de la Nourrice (m) :", min_value=0.0, max_value=3.0, value=float(st.session_state.var_h_nourrice), step=0.1, key="slide_h_nourrice")
                st.session_state.var_pression_compteur = p_compteur
                st.session_state.var_h_nourrice = h_nourrice
                
                st.markdown("##### Commande des robinets de puisage")
                ch_wc = st.checkbox("Ouvrir le robinet (Toilettes / WC)", value=st.session_state.v_ouvert_wc, key="chk_pot_wc")
                ch_sdb = st.checkbox("Ouvrir le robinet (Salle de Bain)", value=st.session_state.v_ouvert_sdb, key="chk_pot_sdb")
                ch_ce = st.checkbox("Ouvrir le robinet (Chauffe-Eau)", value=st.session_state.v_ouvert_ce, key="chk_pot_ce")
            else:
                q_decharge = st.slider("Debit de decharge global (L/s) :", min_value=0.5, max_value=15.0, value=float(st.session_state.var_pression_compteur), step=0.5, key="slide_q_pvc")
                d_collecteur = st.slider("Diametre du Collecteur Egout (mm) :", min_value=50.0, max_value=160.0, value=float(st.session_state.var_h_nourrice), step=10.0, key="slide_d_pvc")
                st.session_state.var_pression_compteur = q_decharge
                st.session_state.var_h_nourrice = d_collecteur
                
                st.markdown("##### Commande des organes d'evacuation")
                ch_wc = st.checkbox("Tirer la chasse d'eau", value=st.session_state.v_ouvert_wc, key="chk_pvc_wc")
                ch_sdb = st.checkbox("Vider la douche / lavabo", value=st.session_state.v_ouvert_sdb, key="chk_pvc_sdb")
                ch_ce = st.checkbox("Purger la vidange", value=st.session_state.v_ouvert_ce, key="chk_pvc_ce")
        else:
            st.info("Parametres imposes par l'examen de session technique.")
            if st.session_state.domaine_actif_b3 == "Canalisation Eau Potable (PER / Cuivre)":
                p_compteur, h_nourrice = 4.0, 3.0
                ch_wc, ch_sdb, ch_ce = True, True, True
                st.markdown(f"* **Pression compteur fige :** {p_compteur:.1f} bars")
                st.markdown(f"* **Altitude nourrice fige :** {h_nourrice:.1f} m")
            else:
                q_decharge, d_collecteur = 6.0, 100.0
                ch_wc, ch_sdb, ch_ce = True, True, True
                st.markdown(f"* **Debit de decharge impose :** {q_decharge:.1f} L/s")
                st.markdown(f"* **Diametre collecteur impose :** {d_collecteur:.0f} mm")

        st.session_state.v_ouvert_wc = ch_wc
        st.session_state.v_ouvert_sdb = ch_sdb
        st.session_state.v_ouvert_ce = ch_ce

    # =====================================================================
    # --- 4. EXÉCUTION DES CALCULS D'INGÉNIERIE ET TRACÉ GRAPHIQUE ---
    # =====================================================================
    with col_droite_plomb:
        st.markdown("##### 4. Rendus Physiques et Verifications")
        plt.close('all')

        fig_plomb, ax_plomb = plt.subplots(figsize=(6, 3.2), dpi=100)
        ax_plomb.clear()

        w_canvas = 600.0
        h_canvas = 220.0
        q_total_maison = 0.0
        taux_remplissage = 0.0

        if st.session_state.domaine_actif_b3 == "Canalisation Eau Potable (PER / Cuivre)":
            p_nourrice_statique = p_compteur - (1000.0 * 9.81 * h_nourrice / 100000.0)
            inv_wc = 1 if ch_wc else 0
            inv_sdb = 1 if ch_sdb else 0
            inv_ce = 1 if ch_ce else 0
            nombre_vannes_ouvertes = inv_wc + inv_sdb + inv_ce

            chute_frottement = 0.15 if nombre_vannes_ouvertes == 1 else (0.55 if nombre_vannes_ouvertes == 2 else (1.10 if nombre_vannes_ouvertes == 3 else 0.0))
            p_dynamique_nourrice = max(0.01, p_nourrice_statique - chute_frottement)

            if p_nourrice_statique < 0.5:
                msg_alert = f"DANGER - PRESSION INSUFFISANTE A LA NOURRICE : {p_nourrice_statique:.2f} bar. L'eau ne montera pas !"
                c_msg = "#dc2626"
            elif p_nourrice_statique > 4.0:
                msg_alert = f"ATTENTION - PRESSION TROP ELEVEE : {p_nourrice_statique:.2f} bar. Risque de fatigue du PER."
                c_msg = "#b45309"
            else:
                msg_alert = f"RESEAU EAU POTABLE BIEN EQUILIBRE : Pression disponible a la nourrice = {p_nourrice_statique:.2f} bar."
                c_msg = "#16a34a"

            st.markdown(f"<span style='color:{c_msg}; font-weight:bold; font-size:11px;'>{msg_alert}</span>", unsafe_allow_html=True)

            y_sol_line = 170.0
            y_nourrice_plt = y_sol_line - (h_nourrice * 22.0)
            
            ax_plomb.plot([10.0, 150.0, 150.0, 200.0], [h_canvas - y_sol_line, h_canvas - y_sol_line, h_canvas - y_nourrice_plt, h_canvas - y_nourrice_plt], color="#2563eb", linewidth=2)
            ax_plomb.plot([10.0], [h_canvas - y_sol_line], marker="o", color="#1d4ed8", markersize=5)
            ax_plomb.text(12.0, h_canvas - y_sol_line + 12.0, "Compteur", fontsize=7, color="#1e3a8a", fontweight="bold")
            ax_plomb.add_patch(plt.Rectangle((185.0, h_canvas - (y_nourrice_plt + 5.0)), 30.0, 10.0, facecolor="#ef4444", edgecolor="black"))
            ax_plomb.text(200.0, h_canvas - (y_nourrice_plt - 10.0), "Nourrice", fontsize=7, color="#b91c1c", ha="center")

            q_maison_total = max(0.2, p_compteur * 1.4)
            
            q_wc = (q_maison_total * 0.20) if ch_wc else 0.0
            v_wc = (q_wc / 1000.0) / (np.pi * ((0.012) / 2.0)**2) if q_wc > 0 else 0.0
            p_wc_dispo = max(0.0, p_dynamique_nourrice - (1000.0 * v_wc**2 / 2.0) / 100000.0)
            p_belier_wc = (1000.0 * 300.0 * v_wc) / 100000.0

            q_sdb = (q_maison_total * 0.30) if ch_sdb else 0.0
            v_sdb = (q_sdb / 1000.0) / (np.pi * ((0.016) / 2.0)**2) if q_sdb > 0 else 0.0
            p_sdb_dispo = max(0.0, p_dynamique_nourrice - (1000.0 * v_sdb**2 / 2.0) / 100000.0)
            p_belier_sdb = (1000.0 * 300.0 * v_sdb) / 100000.0

            q_ce = (q_maison_total * 0.50) if ch_ce else 0.0
            v_ce = (q_ce / 1000.0) / (np.pi * ((0.016) / 2.0)**2) if q_ce > 0 else 0.0
            p_ce_dispo = max(0.0, p_dynamique_nourrice - (1000.0 * v_ce**2 / 2.0) / 100000.0)
            p_belier_ce = (1000.0 * 300.0 * v_ce) / 100000.0

            ax_plomb.add_patch(plt.Rectangle((200.0, 20.0), 390.0, 150.0, facecolor="white", edgecolor="#cbd5e1"))
            ax_plomb.plot([330.0, 330.0], [20.0, 170.0], color="#e2e8f0", linewidth=1)
            ax_plomb.plot([470.0, 470.0], [20.0, 170.0], color="#e2e8f0", linewidth=1)

            ax_plomb.text(210.0, 150.0, "TOILETTES / WC\nTube: PER O12", fontsize=7, color="#0369a1", fontweight="bold")
            ax_plomb.text(210.0, 100.0, f"Debit: {q_wc:.2f} L/s\nVitesse: {v_wc:.2f} m/s\nPression: {p_wc_dispo:.2f} bar\nChoc Belier: +{p_belier_wc:.1f} bar", fontsize=7)

            ax_plomb.text(345.0, 150.0, "SALLE DE BAIN\nTube: PER O16", fontsize=7, color="#0f766e", fontweight="bold")
            ax_plomb.text(345.0, 100.0, f"Debit: {q_sdb:.2f} L/s\nVitesse: {v_sdb:.2f} m/s\nPression: {p_sdb_dispo:.2f} bar\nChoc Belier: +{p_belier_sdb:.1f} bar", fontsize=7)

            ax_plomb.text(485.0, 150.0, "CHAUFFE-EAU\nTube: PER O20", fontsize=7, color="#047857", fontweight="bold")
            ax_plomb.text(485.0, 100.0, f"Debit: {q_ce:.2f} L/s\nVitesse: {v_ce:.2f} m/s\nPression: {p_ce_dispo:.2f} bar\nChoc Belier: +{p_belier_ce:.1f} bar", fontsize=7)
        else:
            inv_wc = 1 if ch_wc else 0
            inv_sdb = 1 if ch_sdb else 0
            q_reel_wc = q_decharge * 0.7 * inv_wc
            q_reel_sdb = q_decharge * 0.3 * inv_sdb
            q_total_maison = q_reel_wc + q_reel_sdb

            capacite_max_egout = 0.1 if d_collecteur <= 0 else ((d_collecteur / 100.0) ** 2.5) * 5.0
            taux_remplissage = min(100, int((q_total_maison / capacite_max_egout) * 100.0)) if capacite_max_egout > 0 else 0

            if taux_remplissage >= 90:
                msg_alert = f"DANGER - ENGORGEMENT DU COLLECTEUR : Diametre trop petit, reflux vers l'egout !"
                c_msg = "#b91c1c"
            elif taux_remplissage > 70:
                msg_alert = f"ATTENTION - ECOULEMENT EN CHARGE : Conduite pleine a plus de 70%, bruits de glouglou."
                c_msg = "#b45309"
            else:
                msg_alert = f"RESEAU GRADUE CONFORME : Ecoulement libre a surface superieure ventilee."
                c_msg = "#16a34a"

            st.markdown(f"<span style='color:{c_msg}; font-weight:bold; font-size:11px;'>{msg_alert}</span>", unsafe_allow_html=True)

            ax_plomb.plot([15.0, 140.0, 140.0, 440.0], [h_canvas - 110.0, h_canvas - 110.0, h_canvas - 150.0, h_canvas - 150.0], color="#64748b", linewidth=6)
            epaisseur_px = max(3, min(12, int(d_collecteur / 12.0)))
            ax_plomb.plot([140.0, 440.0], [h_canvas - 180.0, h_canvas - 185.0], color="#1e293b", linewidth=epaisseur_px)
            ax_plomb.text(440.0, h_canvas - 200.0, f"Egout (Ø {d_collecteur:.0f}mm)", fontsize=7, color="#1e293b", fontweight="bold")

            if taux_remplissage > 5:
                h_eau_px = (epaisseur_px * (taux_remplissage / 100.0))
                ax_plomb.fill_between([140.0, 440.0], h_canvas - 180.0, h_canvas - 180.0 - h_eau_px, color="#38bdf8", alpha=0.8)

            ax_plomb.add_patch(plt.Rectangle((200.0, 20.0), 390.0, 150.0, facecolor="white", edgecolor="#cbd5e1"))
            ax_plomb.plot([340.0, 340.0], [20.0, 170.0], color="#e2e8f0", linewidth=1)
            ax_plomb.plot([480.0, 480.0], [20.0, 170.0], color="#e2e8f0", linewidth=1)

            v_wc_pvc = q_reel_wc / (np.pi * (0.100/2.0)**2) if q_reel_wc > 0 else 0.0
            ax_plomb.text(210.0, 150.0, "EVACUATION WC\nTube: PVC Ø100", fontsize=7, color="#334155", fontweight="bold")
            ax_plomb.text(210.0, 100.0, f"Debit: {q_reel_wc:.2f} L/s\nVitesse: {v_wc_pvc:.2f} m/s\nPression: 0.0 bar\n(Gravitaire)", fontsize=7)
            v_sdb_pvc = q_reel_sdb / (np.pi * (0.040/2.0)**2) if q_reel_sdb > 0 else 0.0
            ax_plomb.text(345.0, 150.0, "EVACUATION SDB\nTube: PVC Ø40", fontsize=7, color="#475569", fontweight="bold")
            ax_plomb.text(345.0, 100.0, f"Debit: {q_reel_sdb:.2f} L/s\nVitesse: {v_sdb_pvc:.2f} m/s\nSiphon: Normal", fontsize=7)

            ax_plomb.text(485.0, 150.0, "COLLECTEUR EGOUT\nTube: Principal", fontsize=7, color="#1e293b", fontweight="bold")
            ax_plomb.text(485.0, 100.0, f"Q Total: {q_total_maison:.2f} L/s\nRempliss.: {taux_remplissage} %\nCapacite: {capacite_max_egout:.1f} L/s", fontsize=7)

        ax_plomb.set_xlim(0.0, w_canvas)
        ax_plomb.set_ylim(0.0, h_canvas)
        ax_plomb.axis("off")
        st.pyplot(fig_plomb)
        plt.close(fig_plomb)

    # =====================================================================
    # --- 5. ETUDE DU REGIME DE REYNOLDS AU ROBINET ---
    # =====================================================================
    st.write("---")
    st.subheader("Analyse du Regime Fluide de Reynolds au Bec du Robinet")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("##### 3. Robinet et Panneau de Controle")
        st.info("LIQUIDE ROBINET : EAU DOMESTIQUE")
        
        if "Normal" in mode_selectionne_tab5:
            var_pression_robinet = st.slider("Pression du reseau amont (bar) :", min_value=0.1, max_value=7.0, value=1.5, step=0.1, key="slide_p_rob_t5")
            var_diam_robinet = st.slider("Diametre du bec (mm) :", min_value=5, max_value=200, value=40, step=1, key="slide_d_rob_t5")
            var_reglage_reducteur = st.slider("Ouverture du reducteur de pression (%) :", min_value=10, max_value=100, value=100, step=5, key="slide_red_rob_t5")
        else:
            var_pression_robinet = 1.5
            var_diam_robinet = 40
            var_reglage_reducteur = 100
            st.markdown(f"* **Pression amont forcee :** {var_pression_robinet:.1f} bar")
            st.markdown(f"* **Diametre du bec force :** {var_diam_robinet} mm")
            st.markdown(f"* **Ouverture du reducteur forcee :** {var_reglage_reducteur} %")

        # --- REPRODUCTION STRICTE DE VOTRE MOTEUR DE CALCULS SOURCE ---
        p_amont_bar = float(var_pression_robinet)
        diam_mm = float(var_diam_robinet)
        pourcentage_ouverture = float(var_reglage_reducteur)

        p_robinet_bar = p_amont_bar * (pourcentage_ouverture / 100.0)
        pression_pascal = p_robinet_bar * 100000.0
        vitesse_reelle = np.sqrt(max(0.0, (2.0 * pression_pascal) / 1000.0))
        vitesse = vitesse_reelle / 50.0

        # Viscosite et couleur de base issues de votre dictionnaire
        nu = 1.0e-6
        couleur_fluide_base = "#38bdf8"
        
        # Nombre de Reynolds calcule STRICTEMENT avec votre formule de mise a l'echelle graphique
        re_local = (vitesse_reelle * (diam_mm / 10.0)) / (nu * 100000.0)

        # Extraction fidele des variables physiques et visuelles d'origine
        w, h = 450.0, 250.0
        largeur_haut = max(6.0, min(35.0, diam_mm * 0.4))
        y_depart_jet = 95.0

        if re_local < 2000.0:
            mode = "laminaire"
            vitesse_chute = max(1.5, vitesse * h * 0.015)
            couleur_goutte = couleur_fluide_base
            texte_regime = "Jet Laminaire : Continu et lisse"
            force_eclaboussure = 0.0
            couleur_fond_cone = "#e0f2fe"
            largeur_bas = 22.0
        elif re_local < 4000.0:
            mode = "transitoire"
            vitesse_chute = max(2.5, vitesse * h * 0.025)
            couleur_goutte = "#f59e0b"
            texte_regime = "Jet Transitoire : Premieres ondulations"
            force_eclaboussure = 2.0
            couleur_fond_cone = "#fef3c7"
            largeur_bas = 45.0
        else:
            mode = "turbulent"
            vitesse_chute = max(4.0, vitesse * h * 0.04)
            couleur_goutte = "#ef4444"
            texte_regime = "Jet Turbulent : Forte dispersion et eclaboussures"
            force_eclaboussure = min(8.0, 2.0 + vitesse * 0.6)
            couleur_fond_cone = "#fee2e2"
            largeur_bas = 75.0

    with col_r2:
        # Horloge d'avance cinetique basee sur votre variable de vitesse_chute
        if "billes_robinet_exact_t5" not in st.session_state:
            st.session_state.billes_robinet_exact_t5 = [{"y": np.random.uniform(y_depart_jet, h - 40.0), "x_offset": np.random.uniform(-1.0, 1.0)} for _ in range(25)]

        for b in st.session_state.billes_robinet_exact_t5:
            b["y"] += vitesse_chute
            if b["y"] > h - 40.0:
                b["y"] = y_depart_jet
                b["x_offset"] = np.random.uniform(-1.0, 1.0)

        fig_rey, ax_rey = plt.subplots(figsize=(6, 4.2), dpi=100)
        ax_rey.clear()

        # Axe vertical decale de -150px pour reproduire votre centrage d'ecran
        x_bec_decor = (w / 2.0) - 150.0

        # 1. RENDU DU CADRAN DE JAUGE TRICOLORE REYNOLDS SUPERIEUR (x: 240 a 420)
        ax_rey.add_patch(plt.Rectangle((240.0, 140.0), 40.0, 15.0, facecolor="#16a34a", zorder=2))  
        ax_rey.add_patch(plt.Rectangle((280.0, 140.0), 40.0, 15.0, facecolor="#eab308", zorder=2))  
        ax_rey.add_patch(plt.Rectangle((320.0, 140.0), 100.0, 15.0, facecolor="#dc2626", zorder=2)) 
        
        ax_rey.plot([240.0, 420.0], [140.0, 140.0], color="black", linewidth=1.5, zorder=3)
        ax_rey.text(240.0, 160.0, "0", fontsize=7, color="#475569", ha="center")
        ax_rey.text(280.0, 160.0, "2000", fontsize=7, color="#475569", ha="center")
        ax_rey.text(320.0, 160.0, "4000", fontsize=7, color="#475569", ha="center")
        ax_rey.text(420.0, 160.0, "10000", fontsize=7, color="#475569", ha="center")

        # Fleche indicatrice mobile liee a la vraie valeur de votre re_local
        pos_x_fleche = 240.0 + min(180.0, (re_local / 10000.0) * 180.0)
        ax_rey.arrow(pos_x_fleche, 175.0, 0.0, -12.0, head_width=6.0, head_length=5.0, fc="black", ec="black", zorder=4)
        ax_rey.text(420.0, 115.0, f"Re = {re_local:.0f}", fontsize=9, fontweight="bold", ha="right")

        y_sol_plt = h - (h - 40.0)
        y_depart_plt = h - y_depart_jet

        # Re-creation immediate des listes de points lues par le zorder
        t_y = np.linspace(0.0, y_depart_plt - y_sol_plt, 20)
        px_gauche_jet = [x_bec_decor + 15.0 - (largeur_haut / 2.0) - (y_p * ((largeur_bas - largeur_haut) / 2.0) / (y_depart_plt - y_sol_plt)) for y_p in t_y]
        px_droite_jet = [x_bec_decor + 15.0 + (largeur_haut / 2.0) + (y_p * ((largeur_bas - largeur_haut) / 2.0) / (y_depart_plt - y_sol_plt)) for y_p in t_y]
        py_jet_lignes = [y_depart_plt - y_p for y_p in t_y]

        # =========================================================================
        # --- ORDONNANCEMENT PARFAIT DE L'ÉCOULEMENT (SANS DÉCALAGE VISUEL) ---
        # =========================================================================
        # 1. Rendu du cone de fond fluide et de ses limites pointillees
        ax_rey.plot(px_gauche_jet, py_jet_lignes, color="#0284c7", linestyle=":", linewidth=1.5, zorder=1)
        ax_rey.plot(px_droite_jet, py_jet_lignes, color="#0284c7", linestyle=":", linewidth=1.5, zorder=1)
        ax_rey.fill_betweenx(py_jet_lignes, px_gauche_jet, px_droite_jet, color=couleur_fond_cone, alpha=0.5, zorder=1)

        # 2. Rendu des billes fluides (zorder=2 pour couler sous le bec metal)
        for b in st.session_state.billes_robinet_exact_t5:
            y_visuelle = h - b["y"]
            if y_sol_plt < y_visuelle < y_depart_plt:
                f_progression = (y_depart_plt - y_visuelle) / (y_depart_plt - y_sol_plt)
                largeur_courante = largeur_haut + f_progression * (largeur_bas - largeur_haut)
                
                if mode == "laminaire":
                    x_bille = x_bec_decor + 15.0 + (b["x_offset"] * (largeur_courante * 0.3))
                    ax_rey.plot([x_bille], [y_visuelle], marker="d", color=couleur_goutte, markersize=3.5, zorder=2)
                elif mode == "transitoire":
                    x_bille = x_bec_decor + 15.0 + (b["x_offset"] * (largeur_courante * 0.4)) + np.sin(y_visuelle * 0.1) * 3.0
                    ax_rey.plot([x_bille], [y_visuelle], marker="o", color=couleur_goutte, markersize=3, zorder=2)
                else:
                    x_bille = x_bec_decor + 15.0 + (b["x_offset"] * (largeur_courante * 0.5)) + np.random.uniform(-force_eclaboussure, force_eclaboussure)
                    ax_rey.plot([x_bille], [y_visuelle], marker="x", color=couleur_goutte, markersize=3.5, zorder=2)

        # 3. Rendu du tuyau de cuivre et du reducteur orange (zorder=3)
        ax_rey.plot(px_gauche_jet, py_jet_lignes, color="#0284c7", linestyle=":", linewidth=1.5, zorder=1)
        ax_rey.plot(px_droite_jet, py_jet_lignes, color="#0284c7", linestyle=":", linewidth=1.5, zorder=1)
        ax_rey.fill_betweenx(py_jet_lignes, px_gauche_jet, px_droite_jet, color=couleur_fond_cone, alpha=0.5, zorder=1)

        # 2. Rendu des billes fluides animées (zorder=2)
        for b in st.session_state.billes_robinet_exact_t5:
            y_visuelle = h - b["y"]
            if y_sol_plt < y_visuelle < y_depart_plt:
                f_progression = (y_depart_plt - y_visuelle) / (y_depart_plt - y_sol_plt)
                largeur_courante = largeur_haut + f_progression * (largeur_bas - largeur_haut)
                
                if mode == "laminaire":
                    x_bille = x_bec_decor + 15.0 + (b["x_offset"] * (largeur_courante * 0.3))
                    ax_rey.plot([x_bille], [y_visuelle], marker="d", color=couleur_goutte, markersize=3.5, zorder=2)
                elif mode == "transitoire":
                    x_bille = x_bec_decor + 15.0 + (b["x_offset"] * (largeur_courante * 0.4)) + np.sin(y_visuelle * 0.1) * 3.0
                    ax_rey.plot([x_bille], [y_visuelle], marker="o", color=couleur_goutte, markersize=3, zorder=2)
                else:
                    x_bille = x_bec_decor + 15.0 + (b["x_offset"] * (largeur_courante * 0.5)) + np.random.uniform(-force_eclaboussure, force_eclaboussure)
                    ax_rey.plot([x_bille], [y_visuelle], marker="x", color=couleur_goutte, markersize=3.5, zorder=2)

        # 3. Rendu de la conduite de cuivre horizontale et du chapeau supérieur (zorder=3)
        ax_rey.plot([0.0, x_bec_decor], [h - 110.0, h - 110.0], color="#b45309", linewidth=4, zorder=3)
        ax_rey.add_patch(plt.Rectangle((x_bec_decor + 10.0, h - 90.0), 10.0, 15.0, facecolor="#ea580c", edgecolor="black", linewidth=1.5, zorder=3))
        
        # Le gros bloc carré orange du milieu (Hauteur augmentée pour correspondre à l'image)
        ax_rey.add_patch(plt.Rectangle((x_bec_decor - 5.0, h - 135.0), 40.0, 45.0, facecolor="#ea580c", edgecolor="black", linewidth=2, zorder=3))

        # 4. Rendu du bec métallique gris épais et de son orifice (Premier plan : zorder=4)
        # Bloc principal carré gris
        x_gauche_col = x_bec_decor + 48.0
        x_droite_col = x_bec_decor + 72.0

        # 4. Rendu du bec metallique gris epais et de son orifice (Premier plan : zorder=4)
        ax_ray_corp = plt.Rectangle((x_bec_decor + 35.0, h - 110.0), 55.0, 25.0, facecolor="#64748b", edgecolor="black", linewidth=2)
        ax_rey.add_patch(ax_ray_corp)
        
        # Le petit manchon d'orifice noir emboite en dessous dessine sans aucun bug
        ax_rey.add_patch(plt.Rectangle((x_gauche_col, h - 125.0), x_droite_col - x_gauche_col, 15.0, facecolor="#475569", edgecolor="black", linewidth=1.5, zorder=4))
        
        # Ligne de separation interne sombre du bec
        ax_rey.plot([x_bec_decor + 40.0, x_bec_decor + 85.0], [h - 98.0, h - 98.0], color="#1e293b", linewidth=3.5, zorder=5)

        # 5. Rendu du manomètre de pression circulaire à gauche
        cercle_mano = plt.Circle((x_bec_decor - 25.0, h - 90.0), 12.0, facecolor="white", edgecolor="black", linewidth=1.5, zorder=5)
        ax_rey.add_patch(cercle_mano)
        ax_rey.plot([x_bec_decor - 25.0, x_bec_decor - 25.0 + 9.0 * np.cos(angle_aiguille)], [h - 90.0, h - 90.0 + 9.0 * np.sin(angle_aiguille)], color="black", linewidth=1.5, zorder=6)

        # Impression de l'analyse nominale basse
        ax_rey.text(x_bec_decor + 15.0, y_sol_plt - 15.0, texte_regime, fontsize=9, fontname="Arial", fontweight="bold", ha="center", color=couleur_goutte)

        ax_rey.set_xlim(-10.0, 440.0)
        ax_rey.set_ylim(0.0, h)
        ax_rey.axis("off")
        st.pyplot(fig_rey)
        plt.close(fig_rey)
    # =====================================================================
    # --- 6. APPEL DE L'INTERFACE INTERACTIVE DU FORMULAIRE ---
    # =====================================================================
        p_compteur_val = float(st.session_state.get("slide_p_compteur", 3.0)) if st.session_state.domaine_actif_b3 == "Canalisation Eau Potable (PER / Cuivre)" else 3.0
        h_nourrice_val = float(st.session_state.get("slide_h_nourrice", 1.5)) if st.session_state.domaine_actif_b3 == "Canalisation Eau Potable (PER / Cuivre)" else 1.5
        n_reynolds_val = float(locals().get("re_local", 0.0))
        q_pvc_val = float(locals().get("q_total_maison", 0.0))
        remp_pvc_val = float(locals().get("taux_remplissage", 0.0))

    st.write("---")
    st.subheader("Feuille de Route et Questionnaire de Synthese - Atelier 5")
    
    verrou_h5 = st.session_state.get("v_verrouille_tab5", False)

# =====================================================================
# --- 7. MOTEUR DE CORRECTION ANALYTIQUE ET RAPPORT HTML SCELLÉ ---
# =====================================================================
    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_h5 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 5.", 
        key="check_certif_hydro5_official_scelle_final_action", 
        disabled=verrou_h5
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_hydro5_final_click_action", use_container_width=True, disabled=verrou_h5):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_h5:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q5_brut = 0.0
            lignes_qcm_html = ""
            map_reponses_qcm = {q["id"]: q["rep"] for q in st.session_state.ordre_qcm_hydro5}
            map_enonces_qcm = {q["id"]: q["q"] for q in st.session_state.ordre_qcm_hydro5}

            for idx, (q_id, saisie) in enumerate(res_q5.items(), 1):
                attendu = map_reponses_qcm[q_id]
                enonce = map_enonces_qcm[q_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_q5_brut += 1.0
                    verdict, lbl_style = "CORRECT", "status-pass"
                else:
                    verdict, lbl_style = "INCORRECT", "status-fail"
                lignes_qcm_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            score_t5_brut = 0.0
            lignes_trous_html = ""
            map_reponses_trous = {t["id"]: t["rep"] for t in st.session_state.ordre_trous_hydro5}
            map_enonces_trous = {t["id"]: t["q"] for t in st.session_state.ordre_trous_hydro5}

            for idx, (t_id, saisie) in enumerate(res_t5.items(), 1):
                attendu = map_reponses_trous[t_id]
                enonce = map_enonces_trous[t_id]
                if str(saisie).strip() == str(attendu).strip():
                    score_t5_brut += 1.0
                    verdict, lbl_style = "CORRECT", "status-pass"
                else:
                    verdict, lbl_style = "INCORRECT", "status-fail"
                lignes_trous_html += f"<tr><td style='text-align: center;'>{idx}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td style='text-align: center;'><span class='{lbl_style}'>{verdict}</span></td></tr>"

            st.session_state.score_v5_p1 = round(float(score_q5_brut), 1)
            st.session_state.score_v5_p2 = round(float(score_t5_brut), 1)
            st.session_state.score_final_v5 = round(float(score_q5_brut + score_t5_brut), 1)
            st.session_state.lignes_qcm_html_t5 = lignes_qcm_html
            st.session_state.lignes_trous_html_t5 = lignes_trous_html
            st.session_state.v_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab5", False):
        scr1 = st.session_state.get("score_v5_p1", 0.0)
        scr2 = st.session_state.get("score_v5_p2", 0.0)
        tot_s = st.session_state.get("score_final_v5", 0.0)
        lignes_qcm_html = st.session_state.get("lignes_qcm_html_t5", "")
        lignes_trous_html = st.session_state.get("lignes_trous_html_t5", "")
        
        from datetime import datetime
        timestamp_v5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER BATIMENT ET REYNOLDS SCELLÉ | Note de session : {tot_s:.1f} / 20.0")

        html_content_t5 = f"""<!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Rapport d'Evaluation Plomberie - Atelier 5</title>
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
                    <strong>Module d'Evaluation :</strong> Applications concretes du batiment et etude de Reynolds (Atelier 5)<br>
                    <strong>Eleve :</strong> {p_eleve} {n_eleve} | <strong>Classe :</strong> {c_eleve}<br>
                    <strong>Analyse :</strong> {st.session_state.domaine_actif_b3} | Nombre de Reynolds teste: Re = {re_local:.0f}<br>
                <span style="font-size:11px; opacity:0.8;">Fige et scelle le : {timestamp_v5}</span>
                </div>
            </div>
            <div class="section-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 0 0 25px 0;">
                - Note obtenue au Questionnaire Technologique : <strong>{scr1:.1f} / 10.0</strong><br>
                - Note obtenue a la Synthese de cours a trous : <strong>{scr2:.1f} / 10.0</strong><br>
                - Note Totale de l'Atelier 5 : <strong>{tot_s:.1f} / 20.0</strong>
            </p>
            <div class="section-title">1. Correction detaillee du Questionnaire QCM (Note sur 10)</div>
            <table>
                <thead>
                    <tr><th style='width: 5%; text-align: center;'>N°</th><th style='width: 45%;'>Enonce de la question posee au sort</th><th style='width: 19%;'>Saisie de l'eleve</th><th style='width: 19%;'>Attendu academique</th><th style='width: 12%; text-align: center;'>Statut</th></tr>
                </thead>
                <tbody>{lignes_qcm_html}</tbody>
            </table>
            <div class="section-title">2. Correction detaillee de la Synthese a trous (Note sur 10)</div>
            <table>
                <thead>
                    <tr><th style='width: 5%; text-align: center;'>N°</th><th style='width: 45%;'>Phrase de cours completee au sort</th><th style='width: 19%;'>Saisie de l'eleve</th><th style='width: 19%;'>Attendu academique</th><th style='width: 12%; text-align: center;'>Statut</th></tr>
                </thead>
                <tbody>{lignes_trous_html}</tbody>
            </table>
        </body>
        </html>"""

        import os
        chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Plomberie_Atelier5_{n_eleve}.html")
        try:
            with open(chemin_sauvegarde, "w", encoding="utf-8") as f: f.write(html_content_t5)
        except Exception: pass

        st.download_button(
            label="Telecharger mon rapport d'evaluation HTML",
            data=html_content_t5,
            file_name=f"Plomberie_Atelier5_{n_eleve}_Copie.html",
            mime="text/html",
            key="btn_download_hydro_v5_pv_export_final",
            use_container_width=True
        )





















