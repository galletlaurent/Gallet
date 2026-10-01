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
        
    st.set_page_config(page_title="Simulateur Dynamique Complet", layout="wide")

    st.title("Simulateur de Dynamique Automobile : Vue Arriere et Vue de Dessus")
    st.write("Selectionnez d'abord votre vehicule, ajustez les parametres puis cliquez sur Rouler pour observer les forces et le trace progressif des essieux.")

    # --- POSITIONNEMENT DU MENU DEROULANT TOUT EN HAUT DE LA PAGE ---
    st.subheader("1. Choix du vehicule de simulation")
    type_vehicule = st.selectbox(
        "Configuration du vehicule à tester :",
        [
            "Voiture seule (Permis B)", 
            "Voiture avec remorque (Permis B)", 
            "Porteur seul (Camion Poids Lourd)", 
            "Porteur avec remorque (Camion Train Routier)", 
            "Ensemble articule (Tracteur + Semi-remorque)"
        ],
        key="widget_choix_vehicule_principal_v6"
    )

    # --- ZONE DES PARAMETRES SECONDAIRES DANS DES COLONNES ---
    st.subheader("2. Reglage de la vitesse et de la route")
    col_reglage1, col_reglage2, col_reglage3 = st.columns(3)

    with col_reglage1:
        vitesse_kmh = st.slider("Vitesse du vehicule (km/h)", 10, 130, 75, step=5, key="widget_slider_vitesse_v6")

    with col_reglage2:
        rayon = st.slider("Rayon du virage R (m)", 15, 150, 45, step=5, key="widget_slider_rayon_v6")
        angle_virage_deg = st.slider("Angle total du virage (degres)", 30, 180, 90, step=5, key="widget_slider_angle_v6")

    with col_reglage3:
        devers_deg = st.slider("Angle de devers de la route (degres)", -5.0, 15.0, 2.5, step=0.5, key="widget_slider_devers_v6")
        adherence_pneus = st.slider("Coefficient d'adherence de la route", 0.1, 1.0, 0.4, step=0.05, key="widget_slider_adherence_v6")

    # --- CONTEXTE ET CONSTANTES PHYSIQUES DYNAMIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)
    largeur_route = 7.0

    # Adaptation precise des masses, dimensions et comportements selon le menu selectionne
    if "Voiture seule" in type_vehicule:
        masse_totale = 1500.0
        h_g_combine = 0.55
        voie = 1.55
        empattement = 2.8
        pneu_lw, pneu_h = 12, 0.2
        label_cg = "CG Voiture"
        seuil_adherence_type = 0.8
        facteur_derive = 0.12
        has_attelage = False
        h_attelage = 0.0

    elif "Voiture avec remorque" in type_vehicule:
        masse_totale = 2200.0  # Voiture + remorque legere
        h_g_combine = 0.60
        voie = 1.55
        empattement = 2.8
        pneu_lw, pneu_h = 12, 0.2
        label_cg = "CG Combine"
        seuil_adherence_type = 0.65
        facteur_derive = 0.15
        has_attelage = True
        h_attelage = 0.45

    elif "Porteur seul" in type_vehicule:
        masse_totale = 19000.0
        h_g_combine = 1.70
        voie = 2.20
        empattement = 4.8
        pneu_lw, pneu_h = 16, 0.35
        label_cg = "CG Porteur"
        seuil_adherence_type = 0.60
        facteur_derive = 0.06
        has_attelage = False
        h_attelage = 0.0

    elif "Camion Train Routier" in type_vehicule:
        masse_totale = 38000.0
        h_g_combine = 1.75
        voie = 2.20
        empattement = 4.8
        pneu_lw, pneu_h = 16, 0.35
        label_cg = "CG Combine PL"
        seuil_adherence_type = 0.55
        facteur_derive = 0.08
        has_attelage = True
        h_attelage = 0.60

    else:  # Ensemble articule Semi-remorque
        masse_totale = 32000.0
        h_g_combine = 1.95
        voie = 2.20
        empattement = 4.0
        pneu_lw, pneu_h = 16, 0.35
        label_cg = "CG Equivalent"
        seuil_adherence_type = 0.58
        facteur_derive = 0.09
        has_attelage = True
        h_attelage = 1.25

    # Calculs des forces fondamentales
    Poids_sur_essieu = (masse_totale * 0.5) if has_attelage else (masse_totale * g)
    if not has_attelage:
        Poids_sur_essieu = masse_totale * g

    F_centrifuge_max = (masse_totale * (vitesse_ms ** 2)) / rayon

    # --- PRE-CALCUL DE LA TRAJECTOIRE GEOMETRIQUE (VUE DE DESSUS) ---
    longueur_entree, longueur_sortie = 35.0, 35.0
    angle_rad = np.radians(angle_virage_deg)

    y_entree = np.linspace(0, longueur_entree, 35)
    x_entree = np.zeros_like(y_entree)

    theta = np.linspace(np.pi, np.pi - angle_rad, 70)
    x_virage = rayon + rayon * np.cos(theta)
    y_virage = longueur_entree + rayon * np.sin(theta)

    distances_s = np.linspace(0, longueur_sortie, 35)
    x_sortie = x_virage[-1] + distances_s * np.cos(-angle_rad + np.pi/2)
    y_sortie = y_virage[-1] + distances_s * np.sin(-angle_rad + np.pi/2)

    x_axe_av = np.concatenate([x_entree, x_virage, x_sortie])
    y_axe_av = np.concatenate([y_entree, y_virage, y_sortie])

    angle_braquage_theorique = np.arctan(empattement / rayon)
    acceleration_laterale = (vitesse_ms ** 2) / rayon
    angle_derive_arriere = (acceleration_laterale / (adherence_pneus * g)) * facteur_derive
    angle_derive_arriere = min(angle_derive_arriere, 0.60)

    x_axe_ar, y_axe_ar = [], []
    for i in range(len(x_axe_av)):
        idx_suiv = min(i + 1, len(x_axe_av) - 1)
        idx_prec = max(i - 1, 0)
        psi_route = np.arctan2(y_axe_av[idx_suiv] - y_axe_av[idx_prec], x_axe_av[idx_suiv] - x_axe_av[idx_prec])
        en_virage = len(x_entree) <= i < (len(x_entree) + len(x_virage))
        psi_vehicule = psi_route - angle_braquage_theorique + angle_derive_arriere if en_virage else psi_route
        x_axe_ar.append(x_axe_av[i] - empattement * np.cos(psi_vehicule))
        y_axe_ar.append(y_axe_av[i] - empattement * np.sin(psi_vehicule))

    x_axe_ar = np.array(x_axe_ar)
    y_axe_ar = np.array(y_axe_ar)

    dx, dy = np.gradient(x_axe_av), np.gradient(y_axe_av)
    norme = np.sqrt(dx**2 + dy**2)
    norme[norme == 0] = 1.0
    nx, ny = -dy / norme, dx / norme
    x_bord_g, y_bord_g = x_axe_av + (largeur_route / 2) * nx, y_axe_av + (largeur_route / 2) * ny
    x_bord_d, y_bord_d = x_axe_av - (largeur_route / 2) * nx, y_axe_av - (largeur_route / 2) * ny

    # --- GESTION DES DEUX COLONNES DE RENDU ---
    st.write("---")
    st.subheader("3. Visualisation de la simulation en direct")
    bouton_rouler = st.button("Lancer la simulation (Rouler)", key="widget_bouton_rouler_global_v6")

    zone_gauche, zone_droite = st.columns(2)
    with zone_gauche:
        st.write("Reparition des forces (Vue Arriere)")
        espace_arriere = st.empty()
    with zone_droite:
        st.write("Tracé progressif des traces d'essieux (Vue de dessus)")
        espace_dessus = st.empty()

    def executer_rendu_scene(index_v):
        en_virage = len(x_entree) <= index_v < (len(x_entree) + len(x_virage))
        
        # Rendu Vue Arriere
        F_centrifuge_instant = F_centrifuge_max if en_virage else 0.0
        P_normal = Poids_sur_essieu * np.cos(alpha)
        P_tangent = Poids_sur_essieu * np.sin(alpha)
        F_normal = F_centrifuge_instant * np.sin(alpha)
        F_tangent = F_centrifuge_instant * np.cos(alpha)
        
        Force_Normale_Totale = P_normal + F_normal
        Force_Tangente_Totale = F_tangent - P_tangent
        
        N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g_combine) / voie
        N_droite = Force_Normale_Totale - N_gauche
        
        statut = "STABLE"
        color_st = "#2ecc71"
        if N_gauche <= 0:
            statut = "RETOURNEMENT !"
            color_st = "#e74c3c"
            N_gauche = 0
            N_droite = Force_Normale_Totale
        elif Force_Tangente_Totale > seuil_adherence_type * Force_Normale_Totale:
            statut = "DERAPAGE LATERAL"
            color_st = "#f39c12"
            
        fig_arr, ax_arr = plt.subplots(figsize=(5.5, 4.8))
        x_r_line = np.array([-voie * 1.5, voie * 1.5])
        y_r_line = x_r_line * np.sin(alpha)
        ax_arr.plot(x_r_line, y_r_line, color="#7f8c8d", lw=4)
        
        cos_a, sin_a = np.cos(alpha), np.sin(alpha)
        x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
        x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a
        
        ax_arr.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=5)
        ax_arr.plot([x_rg, x_rg + pneu_h * sin_a], [y_rg, y_rg - pneu_h * cos_a], color="#111111", lw=pneu_lw, solid_capstyle="round")
        ax_arr.plot([x_rd, x_rd + pneu_h * sin_a], [y_rd, y_rd - pneu_h * cos_a], color="#111111", lw=pneu_lw, solid_capstyle="round")
        
        x_cg_a, y_cg_a = 0 - h_g_combine * sin_a, 0 + h_g_combine * cos_a
        ax_arr.plot(x_cg_a, y_cg_a, 'ro', markersize=10)
        
        f_scale = max(Poids_sur_essieu, F_centrifuge_max, Force_Normale_Totale) / 1.2
        ax_arr.quiver(x_cg_a, y_cg_a, 0, -Poids_sur_essieu / f_scale, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2, label='Poids')
        if F_centrifuge_instant > 0:
            ax_arr.quiver(x_cg_a, y_cg_a, F_centrifuge_instant / f_scale, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2, label='Force Cent.')
            
        if N_gauche > 0:
            ax_arr.quiver(x_rg, y_rg, -N_gauche / f_scale * sin_a, N_gauche / f_scale * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2)
        ax_arr.quiver(x_rd, y_rd, -N_droite / f_scale * sin_a, N_droite / f_scale * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2)
        
        ax_arr.set_aspect('equal')
        ax_arr.set_xlim(-voie * 1.8, voie * 1.8)
        ax_arr.set_ylim(-0.5, h_g_combine + 1.0)
        ax_arr.set_title(f"Statut : {statut}", color=color_st, fontweight="bold")
        ax_arr.grid(True, linestyle=':', alpha=0.4)
        espace_arriere.pyplot(fig_arr)
        plt.close(fig_arr)
        
        # Rendu Vue de dessus (Trace progressif)
        fig_top, ax_top = plt.subplots(figsize=(5.5, 4.8))
        ax_top.fill(np.concatenate([x_bord_g, x_bord_d[::-1]]), np.concatenate([y_bord_g, y_bord_d[::-1]]), color="#1e293b", alpha=0.95)
        ax_top.plot(x_bord_g, y_bord_g, color="#ffffff", lw=1)
        ax_top.plot(x_bord_d, y_bord_d, color="#ffffff", lw=1)
        
        if index_v > 0:
            ax_top.plot(x_axe_av[0:index_v+1], y_axe_av[0:index_v+1], color="#38bdf8", lw=2.5, linestyle=":", label="Trace Avant")
            ax_top.plot(x_axe_ar[0:index_v+1], y_axe_ar[0:index_v+1], color="#f43f5e", lw=2.5, linestyle="--", label="Trace Arriere")
            
        x_av_pos, y_av_pos = x_axe_av[index_v], y_axe_av[index_v]
        x_ar_pos, y_ar_pos = x_axe_ar[index_v], y_axe_ar[index_v]
        
        idx_s = min(index_v + 1, len(x_axe_av) - 1)
        idx_p = max(index_v - 1, 0)

        psi_r = np.arctan2(y_axe_av[idx_s] - y_axe_av[idx_p], x_axe_av[idx_s] - x_axe_av[idx_p])
        psi_v = psi_r - angle_braquage_theorique + angle_derive_arriere if en_virage else psi_r
        
        ax_top.plot([x_ar_pos, x_av_pos], [y_ar_pos, y_av_pos], color="#ffffff", lw=3)
        
        cos_av, sin_av = np.cos(psi_r + angle_braquage_theorique), np.sin(psi_r + angle_braquage_theorique)
        ax_top.plot([x_av_pos - (voie/2)*sin_av, x_av_pos + (voie/2)*sin_av], 
                    [y_av_pos + (voie/2)*cos_av, y_av_pos - (voie/2)*cos_av], color="#0ea5e9", lw=3)
        
        cos_ar, sin_ar = np.cos(psi_v), np.sin(psi_v)
        ax_top.plot([x_ar_pos - (voie/2)*sin_ar, x_ar_pos + (voie/2)*sin_ar], 
                    [y_ar_pos + (voie/2)*cos_ar, y_ar_pos - (voie/2)*cos_ar], color="#e11d48", lw=3)
        
        ax_top.set_aspect('equal')
        ax_top.set_xlim(min(x_axe_av) - 10, max(x_axe_av) + 10)
        ax_top.set_ylim(min(y_axe_av) - 5, max(y_axe_av) + 10)
        ax_top.grid(True, linestyle=':', color="#334155", alpha=0.3)
        
        espace_dessus.pyplot(fig_top)
        plt.close(fig_top)

    # --- BOUCLE DE LE L'ANIMATION ---
    if bouton_rouler:
        for i in range(len(x_axe_av)):
            executer_rendu_scene(i)
            time.sleep(0.05)
    else:
        # Position par defaut figee au milieu de la courbe avant lancement
        executer_rendu_scene(len(x_entree) + int(len(x_virage) / 2))


