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
    "1. Définition de la force centrifuge",
    "2. Véhicule B",
    "3. Véhicule B + remorque",
    "4. Porteur",
    "5. Porteur + remorque",
    "6. Poids lourd ",
    "7.Bus ",   
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]
tab7 = onglets[7]


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
    
    st.header("Simulateur de Dynamique Automobile (Véhicule Permis B - Vue Arrière)")
    st.write("Ce simulateur permet d'analyser le comportement de l'essieu arrière d'une voiture soumis à la force centrifuge en fonction de son poids à vide, de ses passagers/bagages et de la route.")

    # --- BARRE LATÉRALE : PARAMÈTRES INTERACTIFS (VALEURS PERMIS B) ---
    st.sidebar.header("Propriétés de la Voiture")
    masse_a_vide = st.sidebar.slider("Masse à vide du véhicule (kg)", 900, 2500, 1300, step=50, help="Citadine (~1000kg) à gros SUV/Électrique (~2200kg)")
    chargement = st.sidebar.slider("Passagers & Bagages (kg)", 0, 1000, 150, step=10, help="Poids cumulé des occupants et des bagages (max charge utile permis B)")
    h_g = st.sidebar.slider("Hauteur du Centre de Gravité - CG (m)", 0.4, 0.9, 0.55, step=0.05, help="Une berline basse est à ~0.5m, un SUV ou utilitaire est plus haut")
    voie = st.sidebar.slider("Largeur de voie de l'essieu arrière (m)", 1.4, 1.8, 1.55, step=0.05)

    st.sidebar.header("Géométrie & État de la Route")
    rayon = st.sidebar.slider("Rayon de courbure du virage R (m)", 10, 300, 80, step=5)
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 15.0, 2.5, step=0.5, help="Inclinaison de la chaussée vers l'intérieur du virage")
    vitesse_kmh = st.sidebar.slider("Vitesse de la voiture (km/h)", 10, 150, 70, step=5)

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    masse_totale = masse_a_vide + chargement
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg) # Angle de dévers en radians

    # 1. Calcul des forces fondamentales au Centre de Gravité (CG)
    Poids = masse_totale * g
    F_centrifuge = (masse_totale * (vitesse_ms ** 2)) / rayon

    # 2. Projection des forces dans le repère de la route inclinée
    # Axe normal au sol (Fn) et tangentiel au sol (Ft)
    P_normal = Poids * np.cos(alpha)
    P_tangent = Poids * np.sin(alpha)

    F_normal = F_centrifuge * np.sin(alpha)
    F_tangent = F_centrifuge * np.cos(alpha)

    # Forces résultantes appliquées au sol
    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent # Pousse la voiture vers l'extérieur

    # 3. Répartition des charges sur les roues arrière (Virage à gauche -> Appui à droite)
    # Roue gauche = Intérieure du virage | Roue droite = Extérieure du virage
    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g) / voie
    N_droite = Force_Normale_Totale - N_gauche

    # --- ANALYSE DE LA STABILITÉ ---
    statut = "VEHICULE STABLE"
    couleur_statut = "#2ecc71"

    # Seuil de glissement (coefficient d'adhérence moyen pneu/route sec ~ 0.8)
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (Roue intérieure décollée)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > 0.8 * Force_Normale_Totale:
        statut = "PERTE D'ADHÉRENCE / DÉRAPAGE (Crissement des pneus - Décrochage)"
        couleur_statut = "#f39c12"

    # --- AFFICHAGE DES MÉTRIQUES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Masse totale", f"{masse_totale:,} kg".replace(",", " "))
    col2.metric("Force Centrifuge", f"{int(F_centrifuge):,} N")
    col3.metric("Poids (G)", f"{int(Poids):,} N")
    col4.metric("Vitesse", f"{vitesse_ms:.1f} m/s")

    st.markdown(f"### Diagnostic comportement routier : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    # --- RENDU GRAPHIQUE (MATPLOTLIB) ---
    fig, ax = plt.subplots(figsize=(9, 6))

    # Surface de la route (Ligne inclinée selon le dévers)
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#95a5a6", lw=4, label="Chaussée (Dévers)")

    # Positions de contact des pneus au sol
    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    # Dessin de l'essieu arrière et des pneus de voiture (Vue arrière)
    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#34495e", lw=6, label="Essieu arrière")
    # Pneus proportionnels à une voiture
    ax.plot([x_rg, x_rg + 0.2 * sin_a], [y_rg, y_rg - 0.2 * cos_a], color="#111111", lw=14, solid_capstyle="round")
    ax.plot([x_rd, x_rd + 0.2 * sin_a], [y_rd, y_rd - 0.2 * cos_a], color="#111111", lw=14, solid_capstyle="round")

    # Position du Centre de Gravité (plus bas que sur un camion)
    x_cg = 0 - h_g * sin_a
    y_cg = 0 + h_g * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=12, label="Centre de Gravité (CG)")

    # Échelle dynamique pour les flèches de forces
    max_force = max(Poids, F_centrifuge, Force_Normale_Totale)
    facteur_echelle = max_force / 1.2

    # Vecteurs forces au CG
    # Poids (vertical)
    ax.quiver(x_cg, y_cg, 0, -Poids / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2.5, label='Poids (G)')
    # Force Centrifuge (horizontale)
    ax.quiver(x_cg, y_cg, F_centrifuge / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2.5, label='Force Centrifuge (Fc)')

    # Vecteurs réactions d'appui au sol (perpendiculaires à la route)
    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2.5, label='Appui Roue Intérieure (Ng)')
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2.5, label='Appui Roue Extérieure (Nd)')

    # Paramétrage de la zone d'affichage
    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g + 0.8)
    ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Forces sur l'essieu arrière d'une voiture (Vue Arrière - Virage à Gauche)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Largeur (m)")
    ax.set_ylabel("Hauteur (m)")
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.0))

    # Affichage dans Streamlit
    st.pyplot(fig)

    st.info("""
    Informations physiques (Permis B) :
    * Résistance au tonneau : Contrairement à un camion, une voiture possède un centre de gravité très bas (h_g) par rapport à sa largeur de voie (voie). C'est pourquoi une voiture sur route sèche va presque toujours déraper (glisser latéralement) bien avant de risquer un retournement.
    * Effet du chargement arrière : Ajouter des bagages lourds dans le coffre augmente la masse totale mais peut aussi modifier la hauteur du CG et la répartition de la force d'adhérence entre l'essieu avant et l'essieu arrière.
    """)

with tab2:
    
    st.header("Simulateur de Dynamique Automobile avec Remorque (Permis B - Vue Arrière)")
    st.write("Ce simulateur permet d'analyser l'impact d'une remorque chargée sur la stabilité et la répartition des forces de l'essieu arrière de la voiture en virage.")

    # --- BARRE LATÉRALE : PARAMÈTRES INTERACTIFS (VOITURE + REMORQUE) ---
    st.sidebar.header("Propriétés de la Voiture")
    masse_a_vide_v = st.sidebar.slider("Masse à vide voiture (kg)", 900, 2500, 1300, step=50)
    chargement_v = st.sidebar.slider("Passagers & Bagages voiture (kg)", 0, 800, 150, step=10)
    h_g_v = st.sidebar.slider("Hauteur CG voiture (m)", 0.4, 0.9, 0.55, step=0.05)
    voie = st.sidebar.slider("Largeur de voie essieu arrière (m)", 1.4, 1.8, 1.55, step=0.05)

    st.sidebar.header("Propriétés de la Remorque")
    masse_a_vide_r = st.sidebar.slider("Masse à vide remorque (kg)", 150, 1000, 300, step=50, help="Petite remorque (~150kg) à van/caravane (~1000kg)")
    chargement_r = st.sidebar.slider("Chargement dans la remorque (kg)", 0, 2500, 400, step=50, help="Attention aux limites du permis B (Somme des PTAC inférieur à 3500kg ou 4250kg avec formation B96)")
    h_g_r = st.sidebar.slider("Hauteur CG remorque (m)", 0.4, 1.5, 0.70, step=0.05)
    poids_fleche = st.sidebar.slider("Poids sur la flèche d'attelage (kg)", 30, 100, 65, step=5, help="Force verticale statique exercée par la remorque sur la boule d'attelage de la voiture")

    st.sidebar.header("Géométrie & État de la Route")
    rayon = st.sidebar.slider("Rayon du virage R (m)", 15, 300, 80, step=5)
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 15.0, 2.5, step=0.5)
    vitesse_kmh = st.sidebar.slider("Vitesse de l'ensemble (km/h)", 10, 130, 65, step=5)

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    # Masses globales
    masse_voiture = masse_a_vide_v + chargement_v
    masse_remorque = masse_a_vide_r + chargement_r
    masse_totale_ensemble = masse_voiture + masse_remorque

    # 1. Forces de la voiture seule
    Poids_v = masse_voiture * g
    F_centrifuge_v = (masse_voiture * (vitesse_ms ** 2)) / rayon

    # 2. Forces de la remorque (transmises en partie à l'attelage)
    Poids_r = masse_remorque * g
    F_centrifuge_r = (masse_remorque * (vitesse_ms ** 2)) / rayon

    # Force centrifuge de la remorque reportée sur l'attelage (approximation ~50% selon la géométrie du timon)
    F_centrifuge_remorque_sur_attelage = F_centrifuge_r * 0.5

    # 3. Forces cumulées agissant sur l'essieu arrière de la voiture
    # L'essieu arrière supporte le poids statique sur la flèche + une partie de la voiture
    Poids_sur_essieu_arriere = (Poids_v * 0.5) + (poids_fleche * g)
    F_centrifuge_sur_essieu_arriere = F_centrifuge_v * 0.5 + F_centrifuge_remorque_sur_attelage

    # Hauteur équivalente du Centre de Gravité combiné pour l'essieu arrière
    h_g_combine = ((F_centrifuge_v * 0.5 * h_g_v) + (F_centrifuge_remorque_sur_attelage * 0.45)) / F_centrifuge_sur_essieu_arriere

    # 4. Projection dans le repère incliné de la route
    P_normal = Poids_sur_essieu_arriere * np.cos(alpha)
    P_tangent = Poids_sur_essieu_arriere * np.sin(alpha)

    F_normal = F_centrifuge_sur_essieu_arriere * np.sin(alpha)
    F_tangent = F_centrifuge_sur_essieu_arriere * np.cos(alpha)

    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent

    # 5. Répartition des charges sur les roues arrière (Virage à gauche -> Appui à droite)
    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g_combine) / voie
    N_droite = Force_Normale_Totale - N_gauche

    # --- ANALYSE DE LA STABILITÉ ---
    statut = "ENSEMBLE STABLE"
    couleur_statut = "#2ecc71"

    # Seuil d'adhérence réduit à 0.65 car l'effet de l'attelage perturbe la trajectoire (risque de mise en lacet / mise en portefeuille)
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (La roue intérieure décolle)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > 0.65 * Force_Normale_Totale:
        statut = "RISQUE DE DERAPAGE / MISE EN PORTEFEUILLE (L'arrière de la voiture décroche)"
        couleur_statut = "#f39c12"

    # --- AFFICHAGE DES MÉTRIQUES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Masse de l'ensemble", f"{masse_totale_ensemble:,} kg".replace(",", " "))
    col2.metric("Masse de la remorque", f"{masse_remorque:,} kg".replace(",", " "))
    col3.metric("Force Centrifuge Essieu Ar", f"{int(F_centrifuge_sur_essieu_arriere):,} N")
    col4.metric("Poids sur Essieu Ar", f"{int(Poids_sur_essieu_arriere):,} N")

    st.markdown(f"### Diagnostic comportement routier : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    # --- RENDU GRAPHIQUE (MATPLOTLIB) ---
    fig, ax = plt.subplots(figsize=(9, 6))

    # Surface de la route
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#95a5a6", lw=4, label="Chaussée (Dévers)")

    # Contact des pneus
    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    # Dessin de l'essieu arrière de la voiture
    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#34495e", lw=6, label="Essieu arrière voiture")
    ax.plot([x_rg, x_rg + 0.2 * sin_a], [y_rg, y_rg - 0.2 * cos_a], color="#111111", lw=14, solid_capstyle="round")
    ax.plot([x_rd, x_rd + 0.2 * sin_a], [y_rd, y_rd - 0.2 * cos_a], color="#111111", lw=14, solid_capstyle="round")

    # Représentation de la boule d'attelage (centrée derrière l'essieu)
    x_att = 0 - 0.45 * sin_a
    y_att = 0 + 0.45 * cos_a
    ax.plot(x_att, y_att, 'go', markersize=10, label="Point d'attelage")

    # Position du CG virtuel combiné appliqué à l'essieu
    x_cg = 0 - h_g_combine * sin_a
    y_cg = 0 + h_g_combine * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=12, label="CG combiné (Voiture + Remorque)")

    # Échelle dynamique pour les flèches de forces
    max_force = max(Poids_sur_essieu_arriere, F_centrifuge_sur_essieu_arriere, Force_Normale_Totale)
    facteur_echelle = max_force / 1.2

    # Vecteurs forces au CG combiné
    ax.quiver(x_cg, y_cg, 0, -Poids_sur_essieu_arriere / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2.5, label='Poids total subit (G)')
    ax.quiver(x_cg, y_cg, F_centrifuge_sur_essieu_arriere / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2.5, label='Force Centrifuge subie (Fc)')

    # Vecteurs réactions d'appui au sol
    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2.5, label='Appui Roue Intérieure (Ng)')
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2.5, label='Appui Roue Extérieure (Nd)')

    # Paramétrage de la zone d'affichage
    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g_combine + 0.8)
    ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Forces sur l'essieu arrière - Configuration avec Remorque (Virage à Gauche)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Largeur (m)")
    ax.set_ylabel("Hauteur (m)")
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.0))

    st.pyplot(fig)

    st.info("""
    Informations physiques avec remorque :
    * Augmentation de la force latérale : La remorque génère sa propre force centrifuge en virage. Cette force pousse l'attelage vers l'extérieur et crée un moment de rotation qui cherche à faire chasser (déraper) le train arrière de la voiture.
    * Importance du poids sur la flèche : Un poids trop faible sur la flèche déleste l'arrière de la voiture et favorise le dérapage. Un poids trop lourd surcharge l'essieu arrière et écrase les suspensions, modifiant la géométrie de direction de la voiture.
    """)

with tab3:
    
    st.header("Simulateur de Dynamique de Véhicule Porteur (Poids Lourd - Vue Arrière)")
    st.write("Ce simulateur permet d'analyser le comportement d'un camion rigide (porteur) soumis à la force centrifuge en fonction de son chargement lourd et de la hauteur de son centre de gravité.")

    # --- BARRE LATÉRALE : PARAMÈTRES INTERACTIFS (VALEURS POIDS LOURD PORTEUR) ---
    st.sidebar.header("Propriétés du Porteur")
    masse_a_vide = st.sidebar.slider("Masse à vide du porteur (kg)", 6000, 14000, 9000, step=500, help="Poids du camion sans marchandise selon sa configuration (2, 3 ou 4 essieux)")
    charge_utile = st.sidebar.slider("Masse du chargement (kg)", 0, 22000, 12000, step=500, help="Poids de la marchandise transportée (Limite technique du PTAC)")
    h_g = st.sidebar.slider("Hauteur du Centre de Gravité - CG (m)", 0.8, 2.8, 1.70, step=0.05, help="Un chargement haut (ex: citerne, palettes empilées) élève drastiquement le CG")
    voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.8, 2.5, 2.20, step=0.05, help="Largeur standard d'un train arrière de poids lourd")

    st.sidebar.header("Géométrie & État de la Route")
    rayon = st.sidebar.slider("Rayon de courbure du virage R (m)", 20, 400, 100, step=10)
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 12.0, 3.0, step=0.5)
    vitesse_kmh = st.sidebar.slider("Vitesse du camion (km/h)", 10, 110, 50, step=5)

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    masse_totale = masse_a_vide + charge_utile
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    # 1. Calcul des forces fondamentales au Centre de Gravité (CG)
    Poids = masse_totale * g
    F_centrifuge = (masse_totale * (vitesse_ms ** 2)) / rayon

    # 2. Projection des forces dans le repère de la route inclinée
    P_normal = Poids * np.cos(alpha)
    P_tangent = Poids * np.sin(alpha)

    F_normal = F_centrifuge * np.sin(alpha)
    F_tangent = F_centrifuge * np.cos(alpha)

    # Forces résultantes appliquées à l'essieu
    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent 

    # 3. Répartition des charges sur les roues (Virage à gauche -> Appui à droite)
    # Roue gauche = Intérieure du virage | Roue droite = Extérieure du virage
    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g) / voie
    N_droite = Force_Normale_Totale - N_gauche

    # --- ANALYSE DE LA STABILITÉ COMPORTEMENTALE ---
    statut = "VEHICULE STABLE"
    couleur_statut = "#2ecc71"

    # Les poids lourds basculent souvent avant de glisser à cause de leur CG élevé (coefficient d'adhérence fixé à 0.6)
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (La roue intérieure décolle)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > 0.6 * Force_Normale_Totale:
        statut = "RISQUE DE GLISSEMENT LATÉRAL (Perte d'adhérence des pneumatiques)"
        couleur_statut = "#f39c12"

    # --- AFFICHAGE DES MÉTRIQUES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Masse totale (PTAC)", f"{masse_totale:,} kg".replace(",", " "))
    col2.metric("Force Centrifuge", f"{int(F_centrifuge):,} N")
    col3.metric("Poids total (G)", f"{int(Poids):,} N")
    col4.metric("Vitesse du porteur", f"{vitesse_kmh} km/h")

    st.markdown(f"### Diagnostic comportement routier : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    # --- RENDU GRAPHIQUE (MATPLOTLIB) ---
    fig, ax = plt.subplots(figsize=(9, 6))

    # Surface de la route (Inclinée selon le dévers)
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#7f8c8d", lw=5, label="Chaussée (Dévers)")

    # Positions de contact des pneus au sol
    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    # Dessin de l'essieu lourd et des pneus de camion (Vue arrière)
    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=8, label="Essieu rigide porteur")
    # Pneus larges type Poids Lourd
    ax.plot([x_rg, x_rg + 0.35 * sin_a], [y_rg, y_rg - 0.35 * cos_a], color="#111111", lw=18, solid_capstyle="round")
    ax.plot([x_rd, x_rd + 0.35 * sin_a], [y_rd, y_rd - 0.35 * cos_a], color="#111111", lw=18, solid_capstyle="round")

    # Position du Centre de Gravité du porteur (Haut placé)
    x_cg = 0 - h_g * sin_a
    y_cg = 0 + h_g * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=14, label="CG Porteur")

    # Échelle dynamique pour les flèches de forces
    max_force = max(Poids, F_centrifuge, Force_Normale_Totale)
    facteur_echelle = max_force / 1.5

    # Vecteurs forces au CG
    # Poids (vertical)
    ax.quiver(x_cg, y_cg, 0, -Poids / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2.5, label='Poids (G)')
    # Force Centrifuge (horizontale)
    ax.quiver(x_cg, y_cg, F_centrifuge / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2.5, label='Force Centrifuge (Fc)')

    # Vecteurs réactions d'appui au sol (perpendiculaires à la route)
    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2.5, label='Appui Roue Intérieure (Ng)')
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2.5, label='Appui Roue Extérieure (Nd)')

    # Paramétrage de la zone d'affichage
    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g + 1.2)
    ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Forces sur l'essieu arrière d'un Porteur Lourd (Vue Arrière - Virage à Gauche)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Largeur (m)")
    ax.set_ylabel("Hauteur (m)")
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.0))

    # Affichage dans Streamlit
    st.pyplot(fig)

    st.info("""
    Informations physiques (Porteur Poids Lourd) :
    * Le risque majeur de renversement : Contrairement à une voiture, le porteur lourd possède un centre de gravité très haut (h_g) par rapport à sa largeur de voie. En virage serré, le moment de renversement (Force centrifuge multipliée par la hauteur h_g) peut facilement annuler la force d'appui de la roue intérieure (Ng). Le camion bascule alors instantanément (tonneau) avant même d'avoir glissé.
    * Effet du devers : L'inclinaison de la route est essentielle pour un poids lourd car elle utilise une partie du poids pour contrer la force centrifuge et maintenir la charge plaquée au sol.
    """)



with tab4:
    
    st.header("Simulateur de Dynamique de Train Routier (Porteur + Remorque - Vue Arrière)")
    st.write("Ce simulateur permet d'analyser l'impact d'une remorque lourde sur la stabilité et la répartition des forces de l'essieu arrière du porteur en virage.")

    # --- BARRE LATÉRALE : PARAMÈTRES INTERACTIFS (PORTEUR + REMORQUE) ---
    st.sidebar.header("Propriétés du Porteur")
    masse_a_vide_p = st.sidebar.slider("Masse à vide porteur (kg)", 6000, 14000, 9000, step=500)
    charge_utile_p = st.sidebar.slider("Chargement dans le porteur (kg)", 0, 22000, 12000, step=500)
    h_g_p = st.sidebar.slider("Hauteur CG porteur (m)", 0.8, 2.8, 1.70, step=0.05)
    voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.8, 2.5, 2.20, step=0.05)

    st.sidebar.header("Propriétés de la Remorque")
    masse_a_vide_r = st.sidebar.slider("Masse à vide remorque (kg)", 3000, 8000, 5000, step=500)
    charge_utile_r = st.sidebar.slider("Chargement dans la remorque (kg)", 0, 24000, 14000, step=500)
    h_g_r = st.sidebar.slider("Hauteur CG remorque (m)", 0.8, 2.8, 1.80, step=0.05)
    poids_timon = st.sidebar.slider("Charge verticale sur l'attelage (kg)", 0, 1000, 200, step=50, help="Force verticale exercée par le timon de la remorque sur le crochet d'attelage du porteur")

    st.sidebar.header("Géométrie & État de la Route")
    rayon = st.sidebar.slider("Rayon du virage R (m)", 20, 400, 100, step=10)
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 12.0, 3.0, step=0.5)
    vitesse_kmh = st.sidebar.slider("Vitesse du train routier (km/h)", 10, 90, 45, step=5)

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    # Masses globales
    masse_porteur = masse_a_vide_p + charge_utile_p
    masse_remorque = masse_a_vide_r + charge_utile_r
    masse_totale_train = masse_porteur + masse_remorque

    # 1. Forces du porteur seul
    Poids_p = masse_porteur * g
    F_centrifuge_p = (masse_porteur * (vitesse_ms ** 2)) / rayon

    # 2. Forces de la remorque translatées sur l'attelage arrière
    Poids_r = masse_remorque * g
    F_centrifuge_r = (masse_remorque * (vitesse_ms ** 2)) / rayon

    # La force centrifuge de la remorque se répercute sur l'attelage arrière du porteur (approximation empirique ~45%)
    F_centrifuge_remorque_sur_attelage = F_centrifuge_r * 0.45

    # 3. Forces cumulées appliquées au niveau du train arrière du porteur
    # L'essieu arrière supporte une fraction de la charge du porteur + la charge verticale de l'attelage
    Poids_sur_essieu_arriere = (Poids_p * 0.55) + (poids_timon * g)
    F_centrifuge_sur_essieu_arriere = (F_centrifuge_p * 0.55) + F_centrifuge_remorque_sur_attelage

    # Hauteur du Centre de Gravité combiné équivalent pour l'essieu arrière du porteur
    h_g_combine = ((F_centrifuge_p * 0.55 * h_g_p) + (F_centrifuge_remorque_sur_attelage * h_g_r)) / F_centrifuge_sur_essieu_arriere

    # 4. Projection dans le repère incliné de la route
    P_normal = Poids_sur_essieu_arriere * np.cos(alpha)
    P_tangent = Poids_sur_essieu_arriere * np.sin(alpha)

    F_normal = F_centrifuge_sur_essieu_arriere * np.sin(alpha)
    F_tangent = F_centrifuge_sur_essieu_arriere * np.cos(alpha)

    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent

    # 5. Répartition des charges sur les roues arrière (Virage à gauche -> Appui à droite)
    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g_combine) / voie
    N_droite = Force_Normale_Totale - N_gauche

    # --- ANALYSE DE LA STABILITÉ ---
    statut = "TRAIN ROUTIER STABLE"
    couleur_statut = "#2ecc71"

    # Seuil de stabilité réduit à 0.55 en raison de l'effet d'amplification dynamique arrière (coup de raquette)
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (La roue intérieure décolle)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > 0.55 * Force_Normale_Totale:
        statut = "RISQUE DE CHASSSE LATÉRALE / MISE EN PORTEFEUILLE DU TRAIN ROUTIER"
        couleur_statut = "#f39c12"

    # --- AFFICHAGE DES MÉTRIQUES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Masse totale ensemble", f"{masse_totale_train:,} kg".replace(",", " "))
    col2.metric("Masse remorque", f"{masse_remorque:,} kg".replace(",", " "))
    col3.metric("Fc subie Essieu Ar", f"{int(F_centrifuge_sur_essieu_arriere):,} N")
    col4.metric("Poids subi Essieu Ar", f"{int(Poids_sur_essieu_arriere):,} N")

    st.markdown(f"### Diagnostic comportement routier : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    # --- RENDU GRAPHIQUE (MATPLOTLIB) ---
    fig, ax = plt.subplots(figsize=(9, 6))

    # Surface de la route
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#7f8c8d", lw=5, label="Chaussée (Dévers)")

    # Contact des pneus
    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    # Dessin de l'essieu lourd du porteur
    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=8, label="Essieu arrière porteur")
    ax.plot([x_rg, x_rg + 0.35 * sin_a], [y_rg, y_rg - 0.35 * cos_a], color="#111111", lw=18, solid_capstyle="round")
    ax.plot([x_rd, x_rd + 0.35 * sin_a], [y_rd, y_rd - 0.35 * cos_a], color="#111111", lw=18, solid_capstyle="round")

    # Crochet d'attelage arrière du porteur
    x_att = 0 - 0.60 * sin_a
    y_att = 0 + 0.60 * cos_a
    ax.plot(x_att, y_att, 'go', markersize=12, label="Crochet d'attelage")

    # Position du CG virtuel combiné appliqué à cet essieu arrière
    x_cg = 0 - h_g_combine * sin_a
    y_cg = 0 + h_g_combine * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=14, label="CG combiné (Porteur + Remorque)")

    # Échelle dynamique pour les flèches de forces
    max_force = max(Poids_sur_essieu_arriere, F_centrifuge_sur_essieu_arriere, Force_Normale_Totale)
    facteur_echelle = max_force / 1.5

    # Vecteurs forces au CG combiné
    ax.quiver(x_cg, y_cg, 0, -Poids_sur_essieu_arriere / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2.5, label='Poids total subi (G)')
    ax.quiver(x_cg, y_cg, F_centrifuge_sur_essieu_arriere / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2.5, label='Force Centrifuge subie (Fc)')

    # Vecteurs réactions d'appui au sol
    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2.5, label='Appui Roue Intérieure (Ng)')
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2.5, label='Appui Roue Extérieure (Nd)')

    # Paramétrage de la zone d'affichage
    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g_combine + 1.2)
    ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Forces sur l'essieu arrière du Porteur - Configuration Train Routier", fontsize=11, fontweight='bold')
    ax.set_xlabel("Largeur (m)")
    ax.set_ylabel("Hauteur (m)")
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.0))

    st.pyplot(fig)

    st.info("""
    Informations physiques (Porteur + Remorque) :
    * Amplification géométrique : La remorque est reliée à un point d'attelage situé en porte-à-faux derrière l'essieu arrière du porteur. Lorsque la remorque subit la force centrifuge, elle exerce un effort latéral important sur ce crochet, agissant comme un bras de levier qui tend à déstabiliser l'arrière du camion.
    * Hauteur critique cumulée : Si le porteur et la remorque sont tous deux chargés en hauteur, le centre de gravité équivalent s'élève. Cela accroît drastiquement le risque de basculement de l'ensemble du train routier lors de virages négociés à vitesse excessive.
    """)





with tab:
    
    st.header("Simulateur de Dynamique d'Ensemble Articulé (Tracteur + Semi-remorque - Vue Arrière)")
    st.write("Ce simulateur permet d'analyser la répartition des forces sur le train arrière d'un tracteur routier soumis aux contraintes d'une semi-remorque chargée en virage.")

    # --- BARRE LATÉRALE : PARAMÈTRES INTERACTIFS (TRACTEUR + SEMI) ---
    st.sidebar.header("Propriétés du Tracteur")
    masse_a_vide_t = st.sidebar.slider("Masse à vide tracteur (kg)", 6000, 10000, 7500, step=500, help="Poids du tracteur seul à vide sans la semi-remorque")
    h_g_t = st.sidebar.slider("Hauteur CG tracteur (m)", 0.6, 1.2, 0.85, step=0.05)
    voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.8, 2.5, 2.20, step=0.05)

    st.sidebar.header("Propriétés de la Semi-remorque")
    masse_a_vide_s = st.sidebar.slider("Masse à vide semi-remorque (kg)", 5000, 9000, 6500, step=500)
    charge_utile_s = st.sidebar.slider("Chargement dans la semi (kg)", 0, 28000, 18000, step=500, help="Charge utile de marchandises transportée dans le fourgon ou la bâchée")
    h_g_s = st.sidebar.slider("Hauteur CG de la semi chargée (m)", 1.2, 3.2, 2.10, step=0.05, help="La marchandise stockée en hauteur élève considérablement le CG global de la semi")
    report_sellette_pct = st.sidebar.slider("Report de charge sur la sellette (%)", 35, 55, 45, step=5, help="Pourcentage du poids de la semi-remorque transféré sur la selle du tracteur (le reste va aux essieux de la semi)")

    st.sidebar.header("Géométrie & État de la Route")
    rayon = st.sidebar.slider("Rayon du virage R (m)", 20, 400, 100, step=10)
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 12.0, 3.0, step=0.5)
    vitesse_kmh = st.sidebar.slider("Vitesse de l'ensemble (km/h)", 10, 90, 45, step=5)

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    # Masses globales
    masse_semi_totale = masse_a_vide_s + charge_utile_s
    masse_totale_articule = masse_a_vide_t + masse_semi_totale

    # 1. Forces du tracteur seul
    Poids_t = masse_a_vide_t * g
    F_centrifuge_t = (masse_a_vide_t * (vitesse_ms ** 2)) / rayon

    # 2. Forces de la semi-remorque
    Poids_s = masse_semi_totale * g
    F_centrifuge_s = (masse_semi_totale * (vitesse_ms ** 2)) / rayon

    # Transfert des forces de la semi sur la sellette (située juste au-dessus/légèrement en avant de l'essieu arrière)
    ratio_sellette = report_sellette_pct / 100.0
    Poids_semi_sur_sellette = Poids_s * ratio_sellette
    F_centrifuge_semi_sur_sellette = F_centrifuge_s * ratio_sellette

    # 3. Forces cumulées sur le train arrière du tracteur
    # L'essieu arrière du tracteur porte une fraction de son propre poids (ex: 60%) + la charge de la sellette
    Poids_sur_essieu_arriere = (Poids_t * 0.60) + Poids_semi_sur_sellette
    F_centrifuge_sur_essieu_arriere = (F_centrifuge_t * 0.60) + F_centrifuge_semi_sur_sellette

    # Hauteur de la sellette (généralement située à ~1.25m du sol)
    h_sellette = 1.25

    # Hauteur équivalente du Centre de Gravité combiné subie par l'essieu arrière
    # Elle intègre l'effet de levier de la semi-remorque qui pivote et s'incline au-dessus de la sellette
    h_g_combine = ((F_centrifuge_t * 0.60 * h_g_t) + (F_centrifuge_semi_sur_sellette * h_g_s)) / F_centrifuge_sur_essieu_arriere

    # 4. Projection dans le repère incliné de la route
    P_normal = Poids_sur_essieu_arriere * np.cos(alpha)
    P_tangent = Poids_sur_essieu_arriere * np.sin(alpha)

    F_normal = F_centrifuge_sur_essieu_arriere * np.sin(alpha)
    F_tangent = F_centrifuge_sur_essieu_arriere * np.cos(alpha)

    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent

    # 5. Répartition des charges sur les roues arrière (Virage à gauche -> Appui à droite)
    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g_combine) / voie
    N_droite = Force_Normale_Totale - N_gauche

    # --- ANALYSE DE LA STABILITÉ ---
    statut = "ENSEMBLE ARTICULE STABLE"
    couleur_statut = "#2ecc71"

    # Les ensembles articulés subissent un risque élevé de mise en portefeuille ou de basculement direct de la semi
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (La roue intérieure du tracteur décolle)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > 0.58 * Force_Normale_Totale:
        statut = "RISQUE DE MISE EN PORTEFEUILLE (Perte d'adhérence latérale du train arrière tracteur)"
        couleur_statut = "#f39c12"

    # --- AFFICHAGE DES MÉTRIQUES ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Masse totale (PMA)", f"{masse_totale_articule:,} kg".replace(",", " "))
    col2.metric("Charge sur sellette", f"{int(Poids_semi_sur_sellette / g):,} kg".replace(",", " "))
    col3.metric("Fc subie Essieu Ar", f"{int(F_centrifuge_sur_essieu_arriere):,} N")
    col4.metric("Poids subi Essieu Ar", f"{int(Poids_sur_essieu_arriere):,} N")

    st.markdown(f"### Diagnostic comportement routier : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    # --- RENDU GRAPHIQUE (MATPLOTLIB) ---
    fig, ax = plt.subplots(figsize=(9, 6))

    # Surface de la route
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#7f8c8d", lw=5, label="Chaussée (Dévers)")

    # Contact des pneus
    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    # Dessin de l'essieu moteur du tracteur
    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=8, label="Essieu moteur tracteur")
    ax.plot([x_rg, x_rg + 0.35 * sin_a], [y_rg, y_rg - 0.35 * cos_a], color="#111111", lw=18, solid_capstyle="round")
    ax.plot([x_rd, x_rd + 0.35 * sin_a], [y_rd, y_rd - 0.35 * cos_a], color="#111111", lw=18, solid_capstyle="round")

    # Représentation de la sellette d'accouplement
    x_selle = 0 - h_sellette * sin_a
    y_selle = 0 + h_sellette * cos_a
    ax.plot(x_selle, y_selle, 'ks', markersize=12, label="Sellette d'accouplement")

    # Position du CG virtuel combiné appliqué à cet essieu
    x_cg = 0 - h_g_combine * sin_a
    y_cg = 0 + h_g_combine * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=14, label="CG équivalent subit")

    # Échelle dynamique pour les flèches de forces
    max_force = max(Poids_sur_essieu_arriere, F_centrifuge_sur_essieu_arriere, Force_Normale_Totale)
    facteur_echelle = max_force / 1.5

    # Vecteurs forces au CG combiné
    ax.quiver(x_cg, y_cg, 0, -Poids_sur_essieu_arriere / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2.5, label='Poids total subi (G)')
    ax.quiver(x_cg, y_cg, F_centrifuge_sur_essieu_arriere / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2.5, label='Force Centrifuge subie (Fc)')

    # Vecteurs réactions d'appui au sol
    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2.5, label='Appui Roue Intérieure (Ng)')
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2.5, label='Appui Roue Extérieure (Nd)')

    # Paramétrage de la zone d'affichage
    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g_combine + 1.2)
    ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Forces sur l'essieu tracteur - Configuration Semi-remorque Articulée", fontsize=11, fontweight='bold')
    ax.set_xlabel("Largeur (m)")
    ax.set_ylabel("Hauteur (m)")
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.0))

    st.pyplot(fig)

    st.info("""
    Informations physiques (Ensemble Articulé) :
    * Liaison par sellette : La semi-remorque repose directement sur le tracteur. En virage, la force centrifuge latérale de la cargaison s'applique très haut, créant un fort moment de torsion sur la sellette. Cela déleste la roue intérieure du tracteur bien plus vite que sur un porteur rigide.
    * Risque de mise en portefeuille : Si l'essieu arrière du tracteur perd son adhérence sous l'effet d'une force tangente excessive, l'ensemble pivote violemment autour de la sellette (l'arrière du tracteur est poussé en dehors du virage par la semi), provoquant un accident majeur appelé mise en portefeuille.
    """)


























