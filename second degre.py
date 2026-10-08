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
st.sidebar.header("Coefficients de la fonction")
a = st.sidebar.number_input("Coefficient a (different de 0)", value=1.0, step=0.5, format="%.2f")
if a == 0:
    st.sidebar.error("Le coefficient a ne peut pas etre egal a 0 pour une fonction du second degre.")
    st.stop()

b = st.sidebar.number_input("Coefficient b", value=-2.0, step=0.5, format="%.2f")
c = st.sidebar.number_input("Coefficient c", value=-3.0, step=0.5, format="%.2f")

# Calculs de base preliminaires (Alpha et Beta de la forme canonique)
alpha = -b / (2 * a)
beta = a * (alpha ** 2) + b * alpha + c

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
    st.header("Generalites, definition et interactivite")
    
    # Section 1 : Influence des coefficients
    st.subheader("Influence géométrique des coefficients a et c")
    col_a, col_c = st.columns(2)
    
    with col_a:
        st.write("**Influence de a (Forme et orientation) :**")
        st.write(f"Actuellement, a = {a}.")
        if a > 0:
            st.write("- Puisque a > 0, la parabole est orientee 'vers le haut' (en U). Le sommet est un minimum.")
        else:
            st.write("- Puisque a < 0, la parabole est orientee 'vers le bas' (en cloche). Le sommet est un maximum.")
        st.write("- Plus la valeur absolue de a est grande, plus la parabole est etroite et resserree.")
        st.write("- Plus la valeur absolue de a est proche de zero, plus la parabole est large et evasee.")

    with col_c:
        st.write("**Influence de c (Intersection avec l'axe vertical) :**")
        st.write(f"Actuellement, c = {c}.")
        st.write(f"- Le coefficient c represente l'ordonnee a l'origine. La courbe coupe l'axe des ordonnees au point de coordonnees (0 ; {c}).")
        st.write("- Modifier c deplace verticalement toute la parabole vers le haut ou vers le bas sans changer sa forme.")
        st.write(f"- L'axe de symetrie reste fixe a la droite verticale d'equation x = alpha = {alpha:.2f}.")

    st.divider()

    # Section 2 : Tableaux de valeurs (Statique et Interactif)
    col_tab_fixe, col_tab_interactif = st.columns(2)
    
    with col_tab_fixe:
        st.subheader("Tableau de valeurs automatique")
        st.write("Tableau standard centre autour de l'axe de symetrie :")
        x_values = np.linspace(alpha - 4, alpha + 4, 9)
        y_values = a * (x_values ** 2) + b * x_values + c
        df_valeurs = pd.DataFrame({"x": x_values, "f(x)": y_values})
        st.dataframe(df_valeurs.style.format({"x": "{:.2f}", "f(x)": "{:.2f}"}), use_container_width=True)
        
    with col_tab_interactif:
        st.subheader("Outil de calcul interactif (Recherche libre)")
        mode_calcul = st.radio(
            "Choisissez votre mode de calcul :",
            ["Calculer f(x) a partir de x (Image)", "Calculer x a partir de f(x) (Antecédents)"],
            key="mode_calcul"
        )
        
        if mode_calcul == "Calculer f(x) a partir de x (Image)":
            input_x = st.number_input("Entrez une valeur pour x :", value=float(round(alpha, 2)), step=0.5, format="%.2f")
            output_fx = a * (input_x ** 2) + b * input_x + c
            st.success(f"Pour x = {input_x:.2f}, l'image est f(x) = {output_fx:.2f}")
            
        else:
            input_fx = st.number_input("Entrez une valeur cible pour f(x) :", value=float(round(beta, 2)), step=0.5, format="%.2f")
            # Resolution de a(x-alpha)^2 + beta = fx_cible -> (x-alpha)^2 = (fx_cible - beta) / a
            rapport_cible = (input_fx - beta) / a
            
            if rapport_cible < 0:
                st.error(f"Il n'existe aucun nombre reel x tel que f(x) = {input_fx:.2f} avec la configuration actuelle.")
            elif rapport_cible == 0:
                st.success(f"Il existe une seule valeur unique : x = {alpha:.2f}")
            else:
                x_sol1 = alpha - np.sqrt(rapport_cible)
                x_sol2 = alpha + np.sqrt(rapport_cible)
                st.success(f"Il existe deux valeurs de x qui donnent f(x) = {input_fx:.2f} :")
                st.write(f"- x1 = {x_sol1:.2f}")
                st.write(f"- x2 = {x_sol2:.2f}")


























