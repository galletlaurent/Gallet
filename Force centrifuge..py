# -*- coding: utf-8 -*-

import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application force centrifuge",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application force centrifuge")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

# =============================================================================
# INITIALISATION SECURISEE DU SESSION STATE (A l'ouverture de l'application)
# =============================================================================
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
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")
if "roulette_dernier_numero" not in st.session_state:
    st.session_state.roulette_dernier_numero = 0


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
    "Simulateur Dynamique de Véhicules",])


tab0 = onglets[0]
tab1 = onglets[1]



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
            key="btn_validation_identite_maitre",
            disabled=st.session_state.get("verrouille", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("verrouille", False):
                st.rerun()


with tab1:
    

    st.set_page_config(page_title="Simulateur Dynamique", layout="wide")

    st.title("Simulateur de Dynamique de Virage et Trajectoire")
    st.write("Ajustez les curseurs ci-dessous pour modifier en direct les graphiques de vue arriere et de vue de dessus.")

    # --- TOUS LES CURSEURS AFFICHES DIRECTEMENT SUR LA PAGE ---
    st.subheader("Configuration des parametres")

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        type_vehicule = st.selectbox(
            "Type de vehicule :",
            ["Voiture seule", "Voiture avec remorque", "Camion porteur lourd", "Camion avec remorque", "Semi-remorque articulot"]
        )
        vitesse_kmh = st.slider("Vitesse du vehicule (km/h)", 10, 150, 60, step=5)

    with col_c2:
        rayon = st.slider("Rayon de courbure R (m)", 15, 400, 90, step=5)
        angle_virage_deg = st.slider("Angle total du virage (degres)", 15, 180, 90, step=5)

    with col_c3:
        devers_deg = st.slider("Angle de devers de la route (degres)", -5.0, 15.0, 2.5, step=0.5)
        vitesse_animation = st.slider("Vitesse de l'animation", 1, 5, 3)

    # Deuxieme ligne de curseurs pour les masses et dimensions
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        masse_a_vide = st.slider("Masse a vide du vehicule principal (kg)", 900, 15000, 1500, step=100)
    with col_m2:
        chargement_principal = st.slider("Charge du vehicule principal (kg)", 0, 25000, 200, step=100)
    with col_m3:
        h_g = st.slider("Hauteur du centre de gravite principal (m)", 0.4, 3.0, 0.6, step=0.05)
    with col_m4:
        voie = st.slider("Largeur de voie de l'essieu (m)", 1.4, 2.5, 1.6, step=0.05)

    # Variables optionnelles pour les cas avec remorque
    masse_remorque = 500.0
    charge_remorque = 0.0
    h_g_remorque = 0.7
    poids_attelage_statique = 50.0

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    masse_totale_principale = masse_a_vide + chargement_principal
    Poids_sur_essieu = masse_totale_principale * g
    F_centrifuge_sur_essieu = (masse_totale_principale * (vitesse_ms ** 2)) / rayon
    h_g_combine = h_g
    seuil_adherence = 0.75
    has_attelage = False
    h_attelage = 0.5
    description = "Configuration standard."

    # Adaptation legere des variables de calcul selon le texte selectionne
    if "remorque" in type_vehicule.lower() or "articulot" in type_vehicule.lower():
        has_attelage = True
        seuil_adherence = 0.60
        if "voiture" in type_vehicule.lower():
            masse_remorque = 400.0
            h_attelage = 0.45
        else:
            masse_remorque = 8000.0
            h_attelage = 1.20
        Poids_sur_essieu += (masse_remorque * 0.5 * g)
        F_centrifuge_sur_essieu += ((masse_remorque * (vitesse_ms ** 2)) / rayon * 0.5)
        h_g_combine = (h_g + h_attelage) / 2

    # Projections des forces
    P_normal = Poids_sur_essieu * np.cos(alpha)
    P_tangent = Poids_sur_essieu * np.sin(alpha)
    F_normal = F_centrifuge_sur_essieu * np.sin(alpha)
    F_tangent = F_centrifuge_sur_essieu * np.cos(alpha)

    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent

    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g_combine) / voie
    N_droite = Force_Normale_Totale - N_gauche

    statut = "VEHICULE STABLE"
    couleur_statut = "#2ecc71"
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > seuil_adherence * Force_Normale_Totale:
        statut = "RISQUE DE PERTE D'ADHERENCE / DERAPAGE"
        couleur_statut = "#f39c12"

    # --- RENDER GRAPHICS ---
    st.write("---")
    st.subheader("1. Repartion des forces (Vue Arriere)")

    st.markdown(f"Statut : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#7f8c8d", lw=4)

    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=4)
    ax.plot([x_rg, x_rg + 0.2 * sin_a], [y_rg, y_rg - 0.2 * cos_a], color="#111111", lw=12, solid_capstyle="round")
    ax.plot([x_rd, x_rd + 0.2 * sin_a], [y_rd, y_rd - 0.2 * cos_a], color="#111111", lw=12, solid_capstyle="round")

    x_cg, y_cg = 0 - h_g_combine * sin_a, 0 + h_g_combine * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=10)

    facteur_echelle = max(Poids_sur_essieu, F_centrifuge_sur_essieu, Force_Normale_Totale) / 1.2
    ax.quiver(x_cg, y_cg, 0, -Poids_sur_essieu / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2, label='Poids')
    ax.quiver(x_cg, y_cg, F_centrifuge_sur_essieu / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2, label='Centrifuge')

    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g_combine + 1.0)
    st.pyplot(fig)
    plt.close(fig)

    # --- PARTIE 2 : VUE DE DESSUS ---
    st.write("---")
    st.subheader("2. Geometrie du traco de la route (Vue de dessus)")

    bouton_rouler = st.button("Lancer la simulation (Rouler)")

    largeur_voie = 3.5
    longueur_entree, longueur_sortie = 40.0, 40.0

    y_entree = np.linspace(0, longueur_entree, 25)
    x_entree = np.zeros_like(y_entree)
    theta = np.linspace(np.pi, np.pi - alpha, 60) if alpha != 0 else np.linspace(np.pi, np.pi - 0.5, 60)
    x_virage = rayon + rayon * np.cos(theta)
    y_virage = longueur_entree + rayon * np.sin(theta)

    x_fin, y_fin = x_virage[-1], y_virage[-1]
    angle_sortie = -0.5
    distances_s = np.linspace(0, longueur_sortie, 25)
    x_sortie = x_fin + distances_s * np.cos(angle_sortie + np.pi/2)
    y_sortie = y_fin + distances_s * np.sin(angle_sortie + np.pi/2)

    x_axe = np.concatenate([x_entree, x_virage, x_sortie])
    y_axe = np.concatenate([y_entree, y_virage, y_sortie])

    espace_graphique = st.empty()

    def dessiner_dessus(index_v):
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        ax2.plot(x_axe, y_axe, color="#34495e", lw=2, linestyle="--")
        ax2.plot(x_axe[index_v], y_axe[index_v], marker='o', color='red', markersize=10)
        ax2.set_aspect('equal')
        espace_graphique.pyplot(fig2)
        plt.close(fig2)

    if bouton_rouler:
        for i in range(len(x_axe)):
            dessiner_dessus(i)
            time.sleep(0.06 / vitesse_animation)
    else:
        dessiner_dessus(len(x_entree) + 10)









