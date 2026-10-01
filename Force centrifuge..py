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
    
    st.set_page_config(page_title="Simulateur Bi-Essieu Dynamique", layout="wide")

    st.title("Simulateur de Deport d'Essieu Arriere et Derive de Trajectoire (Vue de dessus)")
    st.write("Ce modele utilise l'empattement du vehicule pour simuler la difference de trajectoire entre le train avant et le train arriere.")

    # --- COMPOSANTS DE REGLAGE ---
    st.subheader("Parametres de simulation")
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        vitesse_kmh = st.sidebar.slider("Vitesse du vehicule (km/h)", 10, 130, 60, step=5, key="vitesse_b")
        empattement = st.sidebar.slider("Empattement - Longueur entre essieux (m)", 2.0, 4.5, 2.8, step=0.1, key="empattement_b")

    with col_c2:
        rayon = st.sidebar.slider("Rayon du virage R (m)", 15, 200, 50, step=5, key="rayon_b")
        angle_virage_deg = st.sidebar.slider("Angle total du virage (degres)", 30, 180, 90, step=5, key="angle_b")

    with col_c3:
        adherence_pneus = st.sidebar.slider("Coefficient d'adherence des pneus arriere", 0.1, 1.0, 0.6, step=0.05, key="adherence_b")
        vitesse_animation = st.sidebar.slider("Vitesse de l'animation", 1, 5, 2, key="anim_v_b")

    # --- CALCULS PHYSIQUES ET GEOMETRIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    angle_rad = np.radians(angle_virage_deg)
    largeur_voie = 1.6
    largeur_route = 7.0

    # Angle de braquage cinematique geometrique (epure de Ackermann)
    angle_braquage_theorique = np.arctan(empattement / rayon)

    # Calcul dynamique de la derive induite par la force centrifuge sur l'essieu arriere
    acceleration_laterale = (vitesse_ms ** 2) / rayon
    angle_derive_arriere = (acceleration_laterale / (adherence_pneus * g)) * 0.04
    angle_derive_arriere = min(angle_derive_arriere, 0.35) # Saturation physique du pneumatique

    # --- GENERATION DE LA ROUTE STANDARD ---
    longueur_entree, longueur_sortie = 35.0, 35.0

    # Ligne droite d'entree
    y_entree = np.linspace(0, longueur_entree, 25)
    x_entree = np.zeros_like(y_entree)

    # Courbe circulaire
    theta = np.linspace(np.pi, np.pi - angle_rad, 55)
    x_virage = rayon + rayon * np.cos(theta)
    y_virage = longueur_entree + rayon * np.sin(theta)

    # Ligne droite de sortie dans l'axe de la tangente
    x_fin, y_fin = x_virage[-1], y_virage[-1]
    angle_sortie = - angle_rad
    distances_s = np.linspace(0, longueur_sortie, 25)
    x_sortie = x_fin + distances_s * np.cos(angle_sortie + np.pi/2)
    y_sortie = y_fin + distances_s * np.sin(angle_sortie + np.pi/2)

    # Assemblage des coordonnees de l'axe central
    x_axe = np.concatenate([x_entree, x_virage, x_sortie])
    y_axe = np.concatenate([y_entree, y_virage, y_sortie])

    # --- CONDUITE ET GRAPHISME ---
    st.write("---")
    bouton_rouler = st.button("Lancer la simulation (Rouler)")
    espace_graphique = st.empty()

    def dessiner_vehicule_deux_essieux(index_v):
        fig, ax = plt.subplots(figsize=(9, 7))
        
        # Trace de la ligne de centre jaune
        ax.plot(x_axe, y_axe, color="#fef08a", lw=1.5, linestyle="--", label="Axe central route")
        
        # Calcul des bordures paralleles de la route par vecteurs normaux
        dx = np.gradient(x_axe)
        dy = np.gradient(y_axe)
        norme = np.sqrt(dx**2 + dy**2)
        norme[norme == 0] = 1.0
        nx, ny = -dy / norme, dx / norme
        
        ax.plot(x_axe + (largeur_route/2) * nx, y_axe + (largeur_route/2) * ny, color="#94a3b8", lw=2, label="Limites de voie")
        ax.plot(x_axe - (largeur_route/2) * nx, y_axe - (largeur_route/2) * ny, color="#94a3b8", lw=2)
        
        # Position de l'essieu avant (guide sur l'axe central de la route)
        x_av = x_axe[index_v]
        y_av = y_axe[index_v]
        
        # Orientation instantanee de la route
        idx_suiv = min(index_v + 1, len(x_axe) - 1)
        idx_prec = max(index_v - 1, 0)
        psi_route = np.arctan2(y_axe[idx_suiv] - y_axe[idx_prec], x_axe[idx_suiv] - x_axe[idx_prec])
        
        en_virage = len(x_entree) <= index_v < (len(x_entree) + len(x_virage))
        
        if en_virage:
            # En virage, l'arriere tend a serrer a l'interieur (cinematique)
            # mais la force centrifuge le pousse et le deporte vers l'exterieur (derive)
            psi_vehicule = psi_route - angle_braquage_theorique + angle_derive_arriere
        else:
            psi_vehicule = psi_route
            
        # Calcul de la coordonnee exacte de l'essieu arriere lie par l'empattement
        x_ar = x_av - empattement * np.cos(psi_vehicule)
        y_ar = y_av - empattement * np.sin(psi_vehicule)
        
        # Trace du châssis reliant les deux trains d'essieux
        ax.plot([x_ar, x_av], [y_ar, y_av], color="#334155", lw=4, label="Chassis de la voiture")
        
        # Rendu graphique Essieu Avant (Directeur)
        cos_av, sin_av = np.cos(psi_route + angle_braquage_theorique), np.sin(psi_route + angle_braquage_theorique)
        ax.plot([x_av - (largeur_voie/2)*sin_av, x_av + (largeur_voie/2)*sin_av], 
                [y_av + (largeur_voie/2)*cos_av, y_av - (largeur_voie/2)*cos_av], color="#0284c7", lw=4, label="Essieu Avant Directeur")
        
        # Rendu graphique Essieu Arriere (Suiveur sujet au deport)
        cos_ar, sin_ar = np.cos(psi_vehicule), np.sin(psi_vehicule)
        ax.plot([x_ar - (largeur_voie/2)*sin_ar, x_ar + (largeur_voie/2)*sin_ar], 
                [y_ar + (largeur_voie/2)*cos_ar, y_ar - (largeur_voie/2)*cos_ar], color="#ef4444", lw=5, label="Essieu Arriere Suiveur")
        
        # Marqueurs des centres géométriques
        ax.plot(x_av, y_av, 'bo', markersize=7)
        ax.plot(x_ar, y_ar, 'ro', markersize=7)
        
        # Affichage du vecteur de force latérale si l'essieu arriere glisse ou se deporte sensiblement
        if en_virage and angle_derive_arriere > 0.04:
            ax.quiver(x_ar, y_ar, np.sin(psi_vehicule)*2.5, -np.cos(psi_vehicule)*2.5, color="#e11d48", scale=12, label="Force de dérive latérale")

        ax.set_aspect('equal')
        ax.set_xlim(min(x_axe) - 10, max(x_axe) + 10)
        ax.set_ylim(min(y_axe) - 5, max(y_axe) + 10)
        ax.grid(True, linestyle=':', alpha=0.4)
        ax.set_title("Deport et alignement geometrique des essieux", fontsize=12, fontweight="bold")
        ax.legend(loc="lower right")
        
        espace_graphique.pyplot(fig)
        plt.close(fig)

    # --- AUTOMATISATION DU MOUVEMENT ---
    if bouton_rouler:
        for i in range(len(x_axe)):
            dessiner_vehicule_deux_essieux(i)
            time.sleep(0.07 / vitesse_animation)
    else:
        # Position initiale par defaut (entree de courbe)
        dessiner_vehicule_deux_essieux(len(x_entree) + 12)

    st.info("""
    Comportement mecanique observé :
    * Basse vitesse : L'essieu arriere (point rouge) coupe la trajectoire vers l'interieur du virage par rapport a l'essieu avant (point bleu). C'est le comportement cinematique naturel (la remorque ou l'arriere suit un rayon plus court).
    * Haute vitesse / Glissement : La force centrifuge s'oppose a ce mouvement et deporte le train arriere vers l'exterieur. Si la vitesse augmente ou si l'adherence diminue, vous observerez l'essieu rouge s'écarter brutalement de la trajectoire idéale, simulant un dérapage du train arrière.
    """)







