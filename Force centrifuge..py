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
    
    st.set_page_config(page_title="Simulateur Bi-Essieu Trace", layout="wide")

    st.title("Simulateur de Deport d'Essieu Arriere et Tracé des Trajectoires")
    st.write("Tous les curseurs de reglage sont positionnes directement ci-dessous. Ajustez-les pour voir les traces des essieux.")

    # --- ZONE DES CURSEURS FORCEE EN CONFIGURATION PRINCIPALE ---
    st.subheader("Reglages de la simulation")

    col_reglage1, col_reglage2, col_reglage3 = st.columns(3)

    with col_reglage1:
        vitesse_kmh = st.slider("Vitesse du vehicule (km/h)", 10, 130, 50, step=5, key="slider_vitesse_unique_v3")
        empattement = st.slider("Empattement - Distance entre essieux (m)", 2.0, 4.5, 2.8, step=0.1, key="slider_empattement_unique_v3")

    with col_reglage2:
        rayon = st.slider("Rayon du virage R (m)", 15, 200, 50, step=5, key="slider_rayon_unique_v3")
        angle_virage_deg = st.slider("Angle total du virage (degres)", 30, 180, 90, step=5, key="slider_angle_unique_v3")

    with col_reglage3:
        adherence_pneus = st.slider("Coefficient d'adherence des pneus arriere", 0.1, 1.0, 0.6, step=0.05, key="slider_adherence_unique_v3")
        vitesse_animation = st.slider("Vitesse de defilement", 1, 5, 2, key="slider_animation_unique_v3")

    # --- CALCULS PHYSIQUES ET GEOMETRIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    angle_rad = np.radians(angle_virage_deg)
    largeur_voie = 1.6
    largeur_route = 7.0

    angle_braquage_theorique = np.arctan(empattement / rayon)
    acceleration_laterale = (vitesse_ms ** 2) / rayon
    angle_derive_arriere = (acceleration_laterale / (adherence_pneus * g)) * 0.04
    angle_derive_arriere = min(angle_derive_arriere, 0.35)

    # --- GENERATION DE LA TRAJECTOIRE PRE-CALCULEE ---
    longueur_entree, longueur_sortie = 35.0, 35.0

    # 1. Trajectoire de l'essieu avant (axe de reference)
    y_entree = np.linspace(0, longueur_entree, 30)
    x_entree = np.zeros_like(y_entree)

    theta = np.linspace(np.pi, np.pi - angle_rad, 60)
    x_virage = rayon + rayon * np.cos(theta)
    y_virage = longueur_entree + rayon * np.sin(theta)

    x_fin, y_fin = x_virage[-1], y_virage[-1]
    angle_sortie = - angle_rad
    distances_s = np.linspace(0, longueur_sortie, 30)
    x_sortie = x_fin + distances_s * np.cos(angle_sortie + np.pi/2)
    y_sortie = y_fin + distances_s * np.sin(angle_sortie + np.pi/2)

    x_axe_av = np.concatenate([x_entree, x_virage, x_sortie])
    y_axe_av = np.concatenate([y_entree, y_virage, y_sortie])

    # 2. Pre-calcul complet de la trajectoire de l'essieu arriere pour le tracé en pointilles
    x_axe_ar = []
    y_axe_ar = []

    for i in range(len(x_axe_av)):
        x_av = x_axe_av[i]
        y_av = y_axe_av[i]
        
        idx_suiv = min(i + 1, len(x_axe_av) - 1)
        idx_prec = max(i - 1, 0)
        psi_route = np.arctan2(y_axe_av[idx_suiv] - y_axe_av[idx_prec], x_axe_av[idx_suiv] - x_axe_av[idx_prec])
        
        en_virage = len(x_entree) <= i < (len(x_entree) + len(x_virage))
        psi_vehicule = psi_route - angle_braquage_theorique + angle_derive_arriere if en_virage else psi_route
        
        x_axe_ar.append(x_av - empattement * np.cos(psi_vehicule))
        y_axe_ar.append(y_av - empattement * np.sin(psi_vehicule))

    x_axe_ar = np.array(x_axe_ar)
    y_axe_ar = np.array(y_axe_ar)

    # --- CALCUL DES BORDURES DE ROUTE ---
    dx = np.gradient(x_axe_av)
    dy = np.gradient(y_axe_av)
    norme = np.sqrt(dx**2 + dy**2)
    norme[norme == 0] = 1.0
    nx, ny = -dy / norme, dx / norme

    x_bord_g = x_axe_av + (largeur_route / 2) * nx
    y_bord_g = y_axe_av + (largeur_route / 2) * ny
    x_bord_d = x_axe_av - (largeur_route / 2) * nx
    y_bord_d = y_axe_av - (largeur_route / 2) * ny

    # --- INTERFACE DE SIMULATION ANIME ---
    st.write("---")
    bouton_rouler = st.button("Lancer la simulation (Rouler)", key="btn_rouler_v3")
    espace_graphique = st.empty()

    def dessiner_scene_complete(index_v):
        fig, ax = plt.subplots(figsize=(9, 7))
        
        # Dessin des limites de la chaussée
        ax.plot(x_bord_g, y_bord_g, color="#94a3b8", lw=2, label="Bords de route")
        ax.plot(x_bord_d, y_bord_d, color="#94a3b8", lw=2)
        
        # 1. Tracé permanent en pointilles des traces d'essieux au sol
        ax.plot(x_axe_av, y_axe_av, color="#0284c7", lw=1.5, linestyle=":", label="Trace au sol essieu avant")
        ax.plot(x_axe_ar, y_axe_ar, color="#ef4444", lw=1.5, linestyle="--", label="Trace au sol essieu arriere")
        
        # 2. Recuperation des positions instantanees
        x_av_pos = x_axe_av[index_v]
        y_av_pos = y_axe_av[index_v]
        x_ar_pos = x_axe_ar[index_v]
        y_ar_pos = y_axe_ar[index_v]
        
        # Re-calcul de l'orientation pour positionner les barres d'essieux transversales
        idx_suiv = min(index_v + 1, len(x_axe_av) - 1)
        idx_prec = max(index_v - 1, 0)
        psi_route = np.arctan2(y_axe_av[idx_suiv] - y_axe_av[idx_prec], x_axe_av[idx_suiv] - x_axe_av[idx_prec])
        en_virage = len(x_entree) <= index_v < (len(x_entree) + len(x_virage))
        psi_vehicule = psi_route - angle_braquage_theorique + angle_derive_arriere if en_virage else psi_route
        
        # Dessin du châssis physique reliant l'avant et l'arriere
        ax.plot([x_ar_pos, x_av_pos], [y_ar_pos, y_av_pos], color="#334155", lw=4, label="Chassis de la voiture")
        
        # Dessin transversal Essieu Avant
        cos_av, sin_av = np.cos(psi_route + angle_braquage_theorique), np.sin(psi_route + angle_braquage_theorique)
        ax.plot([x_av_pos - (largeur_voie/2)*sin_av, x_av_pos + (largeur_voie/2)*sin_av], 
                [y_av_pos + (largeur_voie/2)*cos_av, y_av_pos - (largeur_voie/2)*cos_av], color="#0284c7", lw=4)
        
        # Dessin transversal Essieu Arriere
        cos_ar, sin_ar = np.cos(psi_vehicule), np.sin(psi_vehicule)
        ax.plot([x_ar_pos - (largeur_voie/2)*sin_ar, x_ar_pos + (largeur_voie/2)*sin_ar], 
                [y_ar_pos + (largeur_voie/2)*cos_ar, y_ar_pos - (largeur_voie/2)*cos_ar], color="#ef4444", lw=4)
        
        # Pastilles de roues de couleur
        ax.plot(x_av_pos, y_av_pos, 'bo', markersize=8)
        ax.plot(x_ar_pos, y_ar_pos, 'ro', markersize=8)
        
        # Fleche indicative du vecteur force de derive
        if en_virage and angle_derive_arriere > 0.04:
            ax.quiver(x_ar_pos, y_ar_pos, np.sin(psi_vehicule)*2.5, -np.cos(psi_vehicule)*2.5, color="#e11d48", scale=12, label="Force de derive")

        # Ajustements graphiques de la fenetre Matplotlib
        ax.set_aspect('equal')
        ax.set_xlim(min(x_axe_av) - 10, max(x_axe_av) + 10)
        ax.set_ylim(min(y_axe_av) - 5, max(y_axe_av) + 10)
        ax.grid(True, linestyle=':', alpha=0.4)
        ax.set_title("Ecartement geometrique et traces des essieux au sol", fontsize=11, fontweight="bold")
        ax.legend(loc="lower right")
        
        espace_graphique.pyplot(fig)
        plt.close(fig)

    # --- LOGIQUE D'ANIMATION ---
    if bouton_rouler:
        for i in range(len(x_axe_av)):
            dessiner_scene_complete(i)
            time.sleep(0.07 / vitesse_animation)
    else:
        # Position par defaut stable au milieu du virage si non cliqué
        dessiner_scene_complete(len(x_entree) + int(len(x_virage) / 2))

    st.info("""
    Analyse visuelle des traces au sol :
    * Trace en pointilles bleus (Essieu avant) : Elle correspond parfaitement a l'axe central de la route car c'est l'essieu directeur qui dicte la trajectoire d'entree.
    * Trace en pointilles rouges (Essieu arriere) : Elle illustre de maniere permanente le deport du train arriere. A basse vitesse, la ligne rouge passe a l'interieur de la ligne bleue. Si vous augmentez la vitesse ou reduisez le coefficient d'adherence, la force centrifuge prend le dessus et pousse la ligne rouge a l'exterieur de la ligne bleue, materialisant graphiquement la derive ou le derapage de l'arriere.
    """)





