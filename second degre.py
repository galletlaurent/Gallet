# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="TP le second degré ",
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
st.title("TP le second degré")
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
    
st.sidebar.header("Coefficients globaux de la fonction")
a_global = st.sidebar.number_input("Coefficient a (different de 0)", value=1.0, step=0.5, format="%.2f")
if a_global == 0:
    st.sidebar.error("Le coefficient a ne peut pas etre egal a 0 pour une fonction du second degre.")
    st.stop()

b_global = st.sidebar.number_input("Coefficient b", value=-2.0, step=0.5, format="%.2f")
c_global = st.sidebar.number_input("Coefficient c", value=-3.0, step=0.5, format="%.2f")

# Calculs globaux preliminaires
alpha_global = -b_global / (2 * a_global)
beta_global = a_global * (alpha_global ** 2) + b_global * alpha_global + c_global


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
    "Généralités et définition", 
    "Les racines et leur utilisations", 
    "Tableau de signe et tableau de variation",
    "Exemple "
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]

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
    st.header("Generalites, definition et analyse des curseurs")
    
    st.write("Utilisez les curseurs ci-dessous pour observer en temps reel l'influence de chaque coefficient sur la courbe decorative.")
    
    # Creation des curseurs specifiques au graphique de l'onglet 1
    col_slide1, col_slide2, col_slide3 = st.columns(3)
    with col_slide1:
        a = st.slider("Ajuster le coefficient a", min_value=-5.0, max_value=5.0, value=float(a_global), step=0.1, format="%.1f", key="slide_a")
        if a == 0.0:
            st.warning("Le coefficient a est nul : la courbe devient une droite (fonction affine).")
    with col_slide2:
        b = st.slider("Ajuster le coefficient b", min_value=-10.0, max_value=10.0, value=float(b_global), step=0.1, format="%.1f", key="slide_b")
    with col_slide3:
        c = st.slider("Ajuster le coefficient c", min_value=-10.0, max_value=10.0, value=float(c_global), step=0.1, format="%.1f", key="slide_c")

    # Calculs locaux lies aux curseurs
    alpha_local = -b / (2 * a) if a != 0 else 0
    beta_local = a * (alpha_local ** 2) + b * alpha_local + c if a != 0 else c

    # Zone d'affichage : Texte explicatif a gauche, Graphique interactif a droite
    col_texte, col_graph = st.columns([1, 1])
    
    with col_texte:
        st.subheader("Influence géométrique")
        if a > 0:
            st.write(f"- **a = {a:.1f} (> 0)** : Les branches de la parabole sont tournees **vers le haut**. Plus |a| augmente, plus la parabole se resserre.")
        elif a < 0:
            st.write(f"- **a = {a:.1f} (< 0)** : Les branches de la parabole sont tournees **vers le bas**. Plus |a| augmente, plus la parabole se resserre.")
        else:
            st.write("- **a = 0** : Ce n'est plus une parabole mais une droite d'equation f(x) = bx + c.")
            
        st.write(f"- **b = {b:.1f}** : Modifie la position de l'axe de symetrie et deplace horizontalement et verticalement le sommet.")
        st.write(f"- **c = {c:.1f}** : L'ordonnee a l'origine. La courbe coupe l'axe vertical au point (0 ; {c:.1f}). Augmenter c leve la courbe, diminuer c la descend.")
        
        if a != 0:
            st.write(f"Position actuelle du sommet lie aux curseurs : S({alpha_local:.2f} ; {beta_local:.2f})")

    with col_graph:
        # Generation du graphique local
        x_local = np.linspace(alpha_local - 5 if a != 0 else -5, alpha_local + 5 if a != 0 else 5, 400)
        y_local = a * (x_local ** 2) + b * x_local + c
        
        fig_local, ax_local = plt.subplots(figsize=(6, 4))
        ax_local.plot(x_local, y_local, color="purple", linewidth=2, label="Courbe des curseurs")
        
        if a != 0:
            ax_local.scatter(alpha_local, beta_local, color="red", s=80, zorder=5, label=f"Sommet S({alpha_local:.1f}, {beta_local:.1f})")
            ax_local.axvline(alpha_local, color='grey', linestyle=':', label=f"Axe x={alpha_local:.1f}")
            
        ax_local.scatter(0, c, color="blue", s=60, zorder=5, label=f"Intersection (0, {c:.1f})")
        ax_local.axhline(0, color='black', linewidth=0.6, linestyle='--')
        ax_local.axvline(0, color='black', linewidth=0.6, linestyle='--')
        ax_local.grid(True, linestyle=':', alpha=0.6)
        ax_local.legend(loc="upper right")
        st.pyplot(fig_local)

    st.divider()

    # Section 2 : Tableaux de valeurs
    col_tab_fixe, col_tab_interactif = st.columns(2)
    
    with col_tab_fixe:
        st.subheader("Tableau de valeurs automatique (Base globale)")
        st.write("Tableau standard calcule a partir des coefficients de la barre laterale :")
        x_values = np.linspace(alpha_global - 4, alpha_global + 4, 9)
        y_values = a_global * (x_values ** 2) + b_global * x_values + c_global
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
            input_x = st.number_input("Entrez une valeur pour x :", value=float(round(alpha_global, 2)), step=0.5, format="%.2f")
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



















