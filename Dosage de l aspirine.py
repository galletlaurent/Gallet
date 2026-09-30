# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de l'aspirine",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage de l'aspirine")
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

# Variables d'état expérimentales et modes examen
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 7.0
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.1
if "animation_active" not in st.session_state: st.session_state.animation_active = False
if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine": { "ph_min": 8.2, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F8BBD0", "nom_zone": "Rose pâle",  "couleur_base": "#E91E63", "nom_base": "Rose fuchsia" },
        "Bleu de Thymol": { "ph_min": 1.2, "ph_max": 2.8,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FFEB3B", "nom_zone": "Jaune", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Hélianthine / Orange de méthyle": {"ph_min": 3.2, "ph_max": 4.4,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Vert de Bromocrésol": { "ph_min": 3.8, "ph_max": 5.4, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#8BC34A", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Rouge de Méthyle": { "ph_min": 4.2, "ph_max": 6.2, "couleur_acide": "#F44336", "nom_acide": "Rouge","couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Bleu de Bromophténol": { "ph_min": 3.0, "ph_max": 4.6, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#00BCD4", "nom_zone": "Vert-Bleu", "couleur_base": "#3F51B5", "nom_base": "Bleu violet" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },
        "Jaune d'Alizarin R": {"ph_min": 10.1, "ph_max": 12.0, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#F44336", "nom_base": "Rouge" }
    }

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
    "Généralités sur l'aspirine",
    "Dosage colorimétrique de l'aspirine",
    "Calcul théorique sur l'aspirine et vérification de l'inscription sur la boîte"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]


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









with tab2:
    st.header("Atelier 2 : Courbe de titrage et reperage de l'equivalence")
    st.caption("Visualisation interactive des courbes d'evolution pH-metriques et conductimatriques")

    if "verrouille_tab2_asp" not in st.session_state:
        st.session_state.verrouille_tab2_asp = False

    verrou_tab2 = st.session_state.verrouille_tab2_asp
    
    # 1. SIMULATION SCIENTIFIQUE DES DONNÉES DE TITRAGE DE L'ASPIRINE
    import numpy as np
    import pandas as pd

    # Generation de 0 a 25 mL de soude versee
    V_sud_verse = np.linspace(0.0, 25.0, 100)
    V_eq_theorique = 13.9

    # Modelisation mathematique d'un saut de pH pour un acide faible (pKa = 3,5)
    pH_calcule = []
    conductivite_calculee = []
    
    for v in V_sud_verse:
        # Courbe pH-metrique (Saut de pH centre autour de V_eq)
        if v < V_eq_theorique:
            ph_val = 3.5 + np.log10(max(0.001, v) / max(0.001, V_eq_theorique - v))
            ph_val = max(2.8, min(6.5, ph_val))
        else:
            if v == V_eq_theorique:
                ph_val = 8.3
            else:
                ph_val = 11.5 + np.log10(max(0.001, v - V_eq_theorique) / 25.0)
                ph_val = max(10.0, min(12.5, ph_val))
        pH_calcule.append(round(ph_val, 2))

        # Courbe conductimetrique (Evolution des pentes avant/apres equivalence)
        if v < V_eq_theorique:
            sigma_val = 1.2 - (0.02 * v) # Decroissance lente (remplacement des ions)
        else:
            sigma_val = 0.92 + (0.15 * (v - V_eq_theorique)) # Croissance rapide (exces de HO- et Na+)
        conductivite_calculee.append(round(sigma_val, 2))

    # Assemblage dans un DataFrame unique pour Streamlit
    donnees_courbe_df = pd.DataFrame({
        "Volume de soude verse (mL)": V_sud_verse,
        "pH de la solution": pH_calcule,
        "Conductivite sigma (mS/cm)": conductivite_calculee
    })

    # --- RENDU DES GRAPHICHES INTERACTIFS ---
    st.write("Visualisez les donnees de paillasse collectees par vos capteurs :")
    
    choix_suivi = st.radio(
        "Selectionnez le mode d'affichage de la courbe :",
        ["Suivi pH-metrique : pH = f(V_B)", "Suivi conductimetrique : sigma = f(V_B)"],
        horizontal=True,
        disabled=verrou_tab2
    )

    if "pH" in choix_suivi:
        st.line_chart(
            donnees_courbe_df,
            x="Volume de soude verse (mL)",
            y="pH de la solution",
            use_container_width=True
        )
    else:
        st.line_chart(
            donnees_courbe_df,
            x="Volume de soude verse (mL)",
            y="Conductivite sigma (mS/cm)",
            use_container_width=True
        )

    # --- ZONE D'EXPLOITATION PAR L'ÉLÈVE ---
    st.subheader("Exploitation graphique des points equivalents")
    st.write("Analysez le saut ou la rupture de pente pour determiner graphiquement les coordonnees experimentales :")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        veq_tab2 = st.number_input(
            "Volume equivalent releve V_E (mL) :",
            min_value=0.0,
            max_value=25.0,
            value=st.session_state.get("asp_tab2_veq", 0.0),
            step=0.1,
            format="%.1f",
            key="asp_tab2_veq",
            disabled=verrou_tab2
        )
    with col_e2:
        pheq_tab2 = st.number_input(
            "pH equivalent associe pH_E :",
            min_value=0.0,
            max_value=14.0,
            value=st.session_state.get("asp_tab2_pheq", 0.0),
            step=0.1,
            format="%.1f",
            key="asp_tab2_pheq",
            disabled=verrou_tab2
        )

    # --- SYSTEME DE VERROUILLAGE ET COMPILATION DU BILAN LOCAL ---
    st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    case_certif_tab2 = st.checkbox("Je certifie avoir extrait les coordonnees de l'equivalence avec precision.", key="check_certif_tab2_asp", disabled=verrou_tab2)

    if st.button("VALIDER ET SCELLER L'ATELIER 2", key="btn_valider_tab2_asp", use_container_width=True, disabled=verrou_tab2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Remplissez d'abord votre fiche d'identification.")
        elif not case_certif_tab2:
            st.error("Action refusee : Vous devez cocher la case de certification.")
        else:
            # Bareme academique de proximite (Volume a 0.2 mL pres, pH a 0.3 pres)
            score_veq = 10.0 if abs(veq_tab2 - V_eq_theorique) <= 0.2 else 0.0
            score_pheq = 10.0 if abs(pheq_tab2 - 8.3) <= 0.3 else 0.0
            
            st.session_state.score_asp_tab2 = round(float(score_veq + score_pheq), 1)
            st.session_state.verrouille_tab2_asp = True
            st.rerun()

    if st.session_state.get("verrouille_tab2_asp", False):
        note_t2 = st.session_state.get("score_asp_tab2", 0.0)
        st.success(f"ATELIER 2 CONGELÉ | Note d'exploitation graphique : {note_t2} / 20")






with tab3:
    st.header("Atelier 3 : Dosage de l'aspirine - Validation analytique")

    # Menu deroulant de filiere adapte au contexte pharmaceutique et industriel
    liste_filieres_asp = ["Pharmacie d'officine", "Maintenance industrielle pharmaceutique", "Controle Qualite"]
    filiere_actuelle_asp = st.session_state.get("var_filiere_asp", "Pharmacie d'officine")
    
    if filiere_actuelle_asp in liste_filieres_asp:
        idx_filiere_asp = liste_filieres_asp.index(filiere_actuelle_asp)
    else:
        idx_filiere_asp = 0

    filiere_active = st.selectbox(
        "Selectionnez votre filiere d'application :",
        liste_filieres_asp,
        index=idx_filiere_asp,
        key="var_filiere_asp"
    )
    st.caption(f"Contexte applicatif : {filiere_active}")

    if "verrouille_tab3_asp" not in st.session_state: 
        st.session_state.verrouille_tab3_asp = False

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    verrouille = st.session_state.get("verrouille_tab3_asp", False)

    # Constantes physico-chimiques officielles de l'acide acetylsalicylique
    M_aspirine = 180.15 
    V_fiole_ref = 0.250  
    C_soude_titrante = 0.020 
    V_prise_essai = 0.020  
    V_equivalence_theorique = 0.0139 

    # Calculs chimiques de reference pour le barème academique
    n_acide_dose_ref = C_soude_titrante * V_equivalence_theorique 
    n_acide_fiole_ref = n_acide_dose_ref * (V_fiole_ref / V_prise_essai) 
    m_aspirine_calculee_g = n_acide_fiole_ref * M_aspirine 

    # Configuration predictive des variables memoires pour forcer le tableau vide (0.00)
    for cle_asp in ["asp_m11", "asp_m12", "asp_tot1", "asp_m21", "asp_m22", "asp_tot2", "asp_m31", "asp_m32"]:
        if cle_asp not in st.session_state or isinstance(st.session_state[cle_asp], str):
            st.session_state[cle_asp] = 0.00

    # Definition de la phrase d'introduction selon la filiere metier selectionnee
    if "officine" in filiere_active.lower():
        txt_contexte = "Un preparateur en pharmacie controle la masse en principe actif d'un comprime d'aspirine standard."
    else:
        txt_contexte = "Un technicien de laboratoire realise le suivi analytique par titrage acido-basique d'un lot d'aspirine."

    # --- RENDU DE L'ÉNONCÉ FORMEL DE PAILLASSE ---
    with st.container(border=True):
        st.markdown("<p style='color: #1e3a8a; font-weight: bold; margin-bottom: 5px; font-size: 15px;'>PROTOCOLE EXPERIMENTAL ET DONNEES</p>", unsafe_allow_html=True)
        st.write(txt_contexte)
        st.write("Le comprime est dissous dans une fiole jaugee de $V_0 = 250\\text{ mL}$. On titre une prise d'essai de $V_A = 20\\text{ mL}$ par une solution de soude de concentration $C_B = 0,020\\text{ mol/L}$.")
        st.latex("V_{\\text{equivalence}} = 13,9\\text{ mL}")
        st.latex("M_{\\text{aspirine}} = 180,15\\text{ g/mol}")

    # --- GRILLE DE COMPLÉTION DU TABLEAU (SAISIE NUMÉRIQUE DIRECTE EN BLANC) ---
    st.subheader("Grille des resultats du titrage a completer")
    st.caption("Remplissez l'integralite des cellules du tableau au clavier")

    hdr_c1, hdr_c2, hdr_c3, hdr_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with hdr_c2: st.markdown("<p style='text-align:center; font-weight:bold; color:#1e3a8a; margin-bottom:2px;'>Prise d'essai (20 mL)</p>", unsafe_allow_html=True)
    with hdr_c3: st.markdown("<p style='text-align:center; font-weight:bold; color:#1e3a8a; margin-bottom:2px;'>Fiole Jaugee (250 mL)</p>", unsafe_allow_html=True)
    with hdr_c4: st.markdown("<p style='text-align:center; font-weight:bold; color:#0f172a; margin-bottom:2px;'>TOTAL COMPRIME</p>", unsafe_allow_html=True)

    # Ligne 1 : Quantite de matiere n (mol)
    l1_c1, l1_c2, l1_c3, l1_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with l1_c1: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold;'>Matiere n (mol)</div>", unsafe_allow_html=True)
    with l1_c2: v11 = st.number_input("", min_value=0.0000, max_value=1.0000, value=st.session_state.asp_m11, step=0.0001, format="%.4f", key="inp_asp_m11", disabled=verrouille, label_visibility="collapsed")
    with l1_c3: v12 = st.number_input("", min_value=0.0000, max_value=1.0000, value=st.session_state.asp_m12, step=0.0001, format="%.4f", key="inp_asp_m12", disabled=verrouille, label_visibility="collapsed")
    with l1_c4: v_t1 = st.number_input("", min_value=0.0000, max_value=1.0000, value=st.session_state.asp_tot1, step=0.0001, format="%.4f", key="inp_asp_tot1", disabled=verrouille, label_visibility="collapsed")

    # Ligne 2 : Masse m (g)
    l2_c1, l2_c2, l2_c3, l2_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with l2_c1: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold;'>Masse m (g)</div>", unsafe_allow_html=True)
    with l2_c2: v21 = st.number_input("", min_value=0.00, max_value=10.00, value=st.session_state.asp_m21, step=0.01, format="%.2f", key="inp_asp_m21", disabled=verrouille, label_visibility="collapsed")
    with l2_c3: v22 = st.number_input("", min_value=0.00, max_value=10.00, value=st.session_state.asp_m22, step=0.01, format="%.2f", key="inp_asp_m22", disabled=verrouille, label_visibility="collapsed")
    with l2_c4: v_t2 = st.number_input("", min_value=0.00, max_value=10.00, value=st.session_state.asp_tot2, step=0.01, format="%.2f", key="inp_asp_tot2", disabled=verrouille, label_visibility="collapsed")

    # Ligne 3 : Concentration C (mol/L)
    l3_c1, l3_c2, l3_c3, l3_c4 = st.columns([1.5, 1.0, 1.0, 1.0])
    with l3_c1: st.markdown("<div style='background-color:#cbd5e1; padding:8px; border-radius:4px; font-weight:bold;'>Concentration (mol/L)</div>", unsafe_allow_html=True)
    with l3_c2: v31 = st.number_input("", min_value=0.000, max_value=5.000, value=st.session_state.asp_m31, step=0.001, format="%.3f", key="inp_asp_m31", disabled=verrouille, label_visibility="collapsed")
    with l3_c3: v32 = st.number_input("", min_value=0.000, max_value=5.000, value=st.session_state.asp_m32, step=0.001, format="%.3f", key="inp_asp_m32", disabled=verrouille, label_visibility="collapsed")
    with l3_c4: st.markdown("<div style='background-color:#cbd5e1; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>Idem</div>", unsafe_allow_html=True)

    # Sauvegarde immediate en session pour l'analyse
    st.session_state.asp_m11 = float(v11)
    st.session_state.asp_m12 = float(v12)
    st.session_state.asp_tot1 = float(v_t1)
    st.session_state.asp_m21 = float(v21)
    st.session_state.asp_m22 = float(v22)
    st.session_state.asp_tot2 = float(v_t2)
    st.session_state.asp_m31 = float(v31)
    st.session_state.asp_m32 = float(v32)

    st.write("---")
    col_g_asp, col_d_asp = st.columns(2)

    with col_g_asp:
        st.markdown("##### 1. Suivi Colorimetrique (Indicateurs Colores)")
        st.write("L'aspirine (acide acetylsalicylique) est un acide faible dont le pH a l'equivalence se situe aux alentours de **8,3** lors d'un titrage par la soude.")
        
        opt_indicateurs = ["Choisir...", "Heliantine (zone de virage : 3,1 - 4,4)", "Bleu de bromothymol (zone de virage : 6,0 - 7,6)", "Phenolphtaleine (zone de virage : 8,2 - 10,0)"]
        asp_ind_saisie = st.selectbox(
            "Selectionnez l'indicateur colore le plus adapte pour ce titrage :",
            opt_indicateurs,
            key="asp_indicateur_colore",
            disabled=verrouille
        )
        
        st.write("Quel changement de couleur observez-vous a l'equivalence avec cet indicateur ?")
        asp_col_saisie = st.selectbox(
            "Changement de teinte de la solution dans l'erlenmeyer :",
            ["Choisir...", "De l'incolore au rose persistant", "Du jaune au bleu", "Du rouge au jaune"],
            key="asp_couleur_virage",
            disabled=verrouille
        )

    with col_d_asp:
        st.markdown("##### 2. Suivi pH-metrique (Saut de pH)")
        st.write("A l'aide de la courbe de titrage $pH = f(V_B)$ obtenue sur votre terminal de paillasse, determinez les coordonnées du point d'equivalence.")
        
        # Saisie directe au clavier du volume et du pH equivalent
        asp_veq_saisie = st.number_input(
            "Volume de soude verse a l'equivalence $V_{E}$ (mL) :",
            min_value=0.0,
            max_value=25.0,
            value=st.session_state.get("asp_veq_saisie_val", 0.0),
            step=0.1,
            format="%.1f",
            key="asp_veq_saisie_val",
            disabled=verrouille
        )
        
        asp_pheq_saisie = st.number_input(
            "pH de la solution a l'equivalence $pH_{E}$ :",
            min_value=0.0,
            max_value=14.0,
            value=st.session_state.get("asp_pheq_saisie_val", 0.0),
            step=0.1,
            format="%.1f",
            key="asp_pheq_saisie_val",
            disabled=verrouille
        )

    # --- BLOC DE VERROUILLAGE ET CORRECTION AUTOMATIQUE SUR 28 POINTS ---
    st.subheader("Validation et Generation du Bilan Officiel - Aspirine")
    case_certif_asp = st.checkbox("Je certifie avoir complete l'integralite des calculs et observations.", key="check_certif_asp", disabled=verrouille)

    if st.button("VALIDER ET EXPORTER LE BILAN DE DOSAGE ASPIRINE", key="btn_export_asp_final", use_container_width=True, disabled=verrouille):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_asp:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Notation de la grille numerique (8 cases = 8 points)
            scr_grille = sum([
                abs(st.session_state.asp_m11 - n_acide_dose_ref) < 0.001,
                abs(st.session_state.asp_m12 - n_acide_fiole_ref) < 0.001,
                abs(st.session_state.asp_tot1 - n_acide_fiole_ref) < 0.001,
                abs(st.session_state.asp_m21 - (n_acide_dose_ref * M_aspirine)) < 0.05,
                abs(st.session_state.asp_m22 - m_aspirine_calculee_g) < 0.05,
                abs(st.session_state.asp_tot2 - m_aspirine_calculee_g) < 0.05,
                abs(st.session_state.asp_m31 - (n_acide_fiole_ref / V_fiole_ref)) < 0.005,
                abs(st.session_state.asp_m32 - (n_acide_fiole_ref / V_fiole_ref)) < 0.005
            ])

            # 2. Notation de la partie colorimetrique (2 questions = 10 points)
            scr_colorimetrie = sum([
                st.session_state.asp_indicateur_colore == "Phenolphtaleine (zone de virage : 8,2 - 10,0)",
                st.session_state.asp_couleur_virage == "De l'incolore au rose persistant"
            ]) * 5.0

            # 3. Notation de la partie pH-metrique (2 coordonnees = 10 points)
            scr_phmetrie = sum([
                abs(st.session_state.asp_veq_saisie_val - 13.9) < 0.2,
                abs(st.session_state.asp_pheq_saisie_val - 8.3) < 0.3
            ]) * 5.0

            st.session_state.score_asp_grille = float(scr_grille)
            st.session_state.score_asp_col = float(scr_colorimetrie)
            st.session_state.score_asp_ph = float(scr_phmetrie)
            st.session_state.score_final_asp = round(float(scr_grille + scr_colorimetrie + scr_phmetrie), 1)
            st.session_state.verrouille_tab3_asp = True
            st.rerun()

    if st.session_state.get("verrouille_tab3_asp", False):
        s_g = st.session_state.get("score_asp_grille", 0.0)
        s_c = st.session_state.get("score_asp_col", 0.0)
        s_p = st.session_state.get("score_asp_ph", 0.0)
        tot_asp = st.session_state.get("score_final_asp", 0.0)

        st.success(f"DOSAGE ASPIRINE SCELLE | Note globale de session : {tot_asp} / 28")

        # --- ARBORESCENCE HTML MIS À JOUR AVEC LES DEUX RAPPORTS DE METHODES ---
        html_aspirine = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Titrage Aspirine - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0284c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; }}
                .score-badge {{ float: right; background-color: #eab308; color: #1e293b; padding: 15px; border-radius: 8px; font-size: 22px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; margin-bottom: 25px; }}
                th {{ background-color: #0f172a; color: white; padding: 12px; }}
                td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <div class="score-badge">SCORE : {tot_asp} / 28</div>
                <h1>Professeur Laurent GALLET</h1>
                <p>Bilan complet : Dosage colorimetrique et pH-metrique de l'aspirine</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
            </div>
            
            <h2>1. Grille des Resultats Numeriques (Score : {s_g} / 8)</h2>
            <table>
                <thead>
                    <tr><th>Grandeur chimique</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr><td>Matiere Prise d'essai (mol)</td><td>{st.session_state.get("asp_m11", 0.00):.5f}</td><td>{n_acide_dose_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("asp_m11", 0.00) - n_acide_dose_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("asp_m11", 0.00) - n_acide_dose_ref) < 0.001 else "INCORRECT"}</td></tr>
                    <tr><td>Matiere Fiole jaugee (mol)</td><td>{st.session_state.get("asp_m12", 0.00):.5f}</td><td>{n_acide_fiole_ref:.5f}</td><td class="{"status-correct" if abs(st.session_state.get("asp_m12", 0.00) - n_acide_fiole_ref) < 0.001 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("asp_m12", 0.00) - n_acide_fiole_ref) < 0.001 else "INCORRECT"}</td></tr>
                    <tr><td>Total Masse Comprime (g)</td><td>{st.session_state.get("asp_tot2", 0.00):.3f}</td><td>{m_aspirine_calculee_g:.3f}</td><td class="{"status-correct" if abs(st.session_state.get("asp_tot2", 0.00) - m_aspirine_calculee_g) < 0.05 else "status-incorrect"}">{"CORRECT" if abs(st.session_state.get("asp_tot2", 0.00) - m_aspirine_calculee_g) < 0.05 else "INCORRECT"}</td></tr>
                </tbody>
            </table>

            <h2>2. Validation du Suivi Colorimetrique (Score : {s_c} / 10)</h2>
            <table>
                <thead>
                    <tr><th>Parametre observe</th><th>Reponse de l'eleve</th><th>Attendu Professeur</th></tr>
                </thead>
                <tbody>
                    <tr><td>Choix de l'indicateur colore</td><td>{st.session_state.get("asp_indicateur_colore", "Choisir...")}</td><td>Phenolphtaleine (zone de virage : 8,2 - 10,0)</td></tr>
                    <tr><td>Teinte au virage a l'equivalence</td><td>{st.session_state.get("asp_couleur_virage", "Choisir...")}</td><td>De l'incolore au rose persistant</td></tr>
                </tbody>
            </table>

            <h2>3. Validation du Suivi pH-metrique (Score : {s_p} / 10)</h2>
            <table>
                <thead>
                    <tr><th>Coordonnee de l'equivalence</th><th>Saisie Eleve</th><th>Attendu Professeur</th></tr>
                </thead>
                <tbody>
                    <tr><td>Volume equivalent V_E (mL)</td><td>{st.session_state.get("asp_veq_saisie_val", 0.0):.1f} mL</td><td>13.9 mL</td></tr>
                    <tr><td>pH a l'equivalence pH_E</td><td>{st.session_state.get("asp_pheq_saisie_val", 0.0):.1f}</td><td>8.3</td></tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_f_asp = f"Rapport_Dosage_Aspirine_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_")
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ASPIRINE SUR VOTRE ORDINATEUR", 
            data=html_aspirine, 
            file_name=f"{nom_f_asp}.html", 
            mime="text/html", 
            use_container_width=True
        )







































