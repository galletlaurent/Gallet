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
    st.write("Ajustez l'ensemble des parametres ci-dessous puis lancez l'animation pour observer le comportement de l'essieu arriere.")

    # --- SECTION 1 : CHOIX DU VEHICULE ---
    st.subheader("1. Choix du vehicule de simulation")
    type_vehicule = st.selectbox(
        "Configuration du vehicule a tester :",
        [
            "Voiture seule (Permis B)", 
            "Voiture avec remorque (Permis B)", 
            "Porteur seul (Camion Poids Lourd)", 
            "Porteur avec remorque (Camion Train Routier)", 
            "Ensemble articulé (Tracteur + Semi-remorque)"
        ],
        key="choix_vehicule_v7"
    )

    # --- SECTION 2 : REGLAGES GEOMETRIQUES DU VEHICULE SELECTIONNE ---
    st.subheader("2. Caracteristiques geometriques et masses du vehicule")
    col_m1, col_m2, col_m3 = st.columns(3)

    # Initialisation par defaut des variables pour eviter les erreurs d'execution
    has_attelage = False
    h_attelage = 0.0
    report_sellette = 0.0
    masse_remorque_totale = 0.0
    h_g_remorque = 0.0

    if type_vehicule == "Voiture seule (Permis B)":
        with col_m1:
            masse_a_vide = st.slider("Masse a vide de la voiture (kg)", 900, 2500, 1300, step=50, key="m_v_v7")
            chargement = st.slider("Passagers et bagages de la voiture (kg)", 0, 1000, 150, step=10, key="c_v_v7")
        with col_m2:
            h_g = st.slider("Hauteur du centre de gravite (m)", 0.40, 0.90, 0.55, step=0.05, key="h_v_v7")
            voie = st.slider("Largeur de voie de l'essieu (m)", 1.40, 1.80, 1.55, step=0.05, key="w_v_v7")
        with col_m3:
            empattement = st.slider("Empattement - Distance entre essieux (m)", 2.20, 3.50, 2.70, step=0.10, key="e_v_v7")
        
        masse_totale_calcul = masse_a_vide + chargement
        Poids_sur_essieu = masse_totale_calcul * 9.81 * 0.5 # Essieu arriere supporte environ 50%
        h_g_combine = h_g
        seuil_adherence_type = 0.80
        facteur_derive = 0.12

    elif type_vehicule == "Voiture avec remorque (Permis B)":
        has_attelage = True
        h_attelage = 0.45
        with col_m1:
            masse_a_vide = st.slider("Masse a vide de la voiture (kg)", 900, 2500, 1300, step=50, key="m_vr_v7")
            chargement = st.slider("Passagers et bagages de la voiture (kg)", 0, 800, 150, step=10, key="c_vr_v7")
            h_g = st.slider("Hauteur CG de la voiture (m)", 0.40, 0.90, 0.55, step=0.05, key="h_vr_v7")
        with col_m2:
            masse_remorque = st.slider("Masse a vide de la remorque (kg)", 150, 1000, 300, step=50, key="m_r_v7")
            chargement_r = st.slider("Chargement dans la remorque (kg)", 0, 2500, 500, step=50, key="c_r_v7")
            h_g_remorque = st.slider("Hauteur CG de la remorque (m)", 0.40, 1.30, 0.70, step=0.05, key="h_r_v7")
        with col_m3:
            voie = st.slider("Largeur de voie de l'essieu (m)", 1.40, 1.80, 1.55, step=0.05, key="w_vr_v7")
            empattement = st.slider("Empattement - Distance entre essieux (m)", 2.20, 3.50, 2.70, step=0.10, key="e_vr_v7")
            poids_fleche = st.slider("Transfert de poids vertical sur la fleche (kg)", 30, 100, 65, step=5, key="f_r_v7")
            
        masse_totale_calcul = masse_a_vide + chargement
        masse_remorque_totale = masse_remorque + chargement_r
        Poids_sur_essieu = (masse_totale_calcul * 9.81 * 0.5) + (poids_fleche * 9.81)
        h_g_combine = ((masse_totale_calcul * 0.5 * h_g) + (poids_fleche * h_attelage)) / (masse_totale_calcul * 0.5 + poids_fleche)
        seuil_adherence_type = 0.65
        facteur_derive = 0.15

    elif type_vehicule == "Porteur seul (Camion Poids Lourd)":
        with col_m1:
            masse_a_vide = st.slider("Masse a vide du porteur (kg)", 6000, 14000, 9000, step=500, key="m_p_v7")
            charge_utile = st.slider("Masse de la cargaison (kg)", 0, 22000, 12000, step=500, key="c_p_v7")
        with col_m2:
            h_g = st.slider("Hauteur du centre de gravite charge (m)", 0.80, 2.80, 1.70, step=0.05, key="h_p_v7")
            voie = st.slider("Largeur de voie de l'essieu (m)", 1.80, 2.50, 2.20, step=0.05, key="w_p_v7")
        with col_m3:
            empattement = st.slider("Empattement du camion (m)", 3.50, 6.50, 4.80, step=0.10, key="e_p_v7")
            
        masse_totale_calcul = masse_a_vide + charge_utile
        Poids_sur_essieu = masse_totale_calcul * 9.81 * 0.60 # Essieu arriere moteur charge
        h_g_combine = h_g
        seuil_adherence_type = 0.60
        facteur_derive = 0.06

    elif type_vehicule == "Porteur avec remorque (Camion Train Routier)":
        has_attelage = True
        h_attelage = 0.60
        with col_m1:
            masse_a_vide = st.slider("Masse a vide du porteur (kg)", 6000, 14000, 9000, step=500, key="m_pt_v7")
            charge_utile = st.slider("Charge du porteur (kg)", 0, 22000, 12000, step=500, key="c_pt_v7")
            h_g = st.slider("Hauteur CG du porteur (m)", 0.80, 2.80, 1.70, step=0.05, key="h_pt_v7")
        with col_m2:
            masse_remorque = st.slider("Masse a vide de la remorque lourde (kg)", 3000, 8000, 5000, step=500, key="m_tr_v7")
            chargement_r = st.slider("Charge de la remorque lourde (kg)", 0, 24000, 14000, step=500, key="c_tr_v7")
            h_g_remorque = st.slider("Hauteur CG de la remorque lourde (m)", 0.80, 2.80, 1.80, step=0.05, key="h_tr_v7")
        with col_m3:
            voie = st.slider("Largeur de voie de l'essieu (m)", 1.80, 2.50, 2.20, step=0.05, key="w_pt_v7")
            empattement = st.slider("Empattement du camion (m)", 3.50, 6.50, 4.80, step=0.10, key="e_pt_v7")
            poids_timon = st.slider("Charge verticale statique du timon (kg)", 0, 1000, 200, step=50, key="f_tr_v7")
            
        masse_totale_calcul = masse_a_vide + charge_utile
        masse_remorque_totale = masse_remorque + chargement_r
        Poids_sur_essieu = (masse_totale_calcul * 9.81 * 0.55) + (poids_timon * 9.81)
        h_g_combine = ((masse_totale_calcul * 0.55 * h_g) + (poids_timon * h_attelage)) / (masse_totale_calcul * 0.55 + poids_timon)
        seuil_adherence_type = 0.55
        facteur_derive = 0.08

    else:  # Ensemble articule (Tracteur + Semi-remorque)
        has_attelage = True
        h_attelage = 1.25
        with col_m1:
            masse_a_vide = st.slider("Masse a vide du tracteur (kg)", 6000, 10000, 7500, step=500, key="m_t_v7")
            h_g = st.slider("Hauteur CG du tracteur (m)", 0.60, 1.20, 0.85, step=0.05, key="h_t_v7")
            voie = st.slider("Largeur de voie de l'essieu (m)", 1.80, 2.50, 2.20, step=0.05, key="w_t_v7")
        with col_m2:
            masse_remorque = st.slider("Masse a vide de la semi-remorque (kg)", 5000, 9000, 6500, step=500, key="m_s_v7")
            charge_utile = st.slider("Charge utile dans la semi (kg)", 0, 28000, 18000, step=500, key="c_s_v7")
            h_g_remorque = st.slider("Hauteur CG de la semi (m)", 1.20, 3.20, 2.10, step=0.05, key="h_s_v7")
        with col_m3:
            empattement = st.slider("Empattement du tracteur (m)", 3.00, 5.00, 4.00, step=0.10, key="e_t_v7")
            report_sellette = st.slider("Report de charge sur la sellette (%)", 35, 55, 45, step=5, key="r_s_v7")
            
        masse_totale_calcul = masse_a_vide
        masse_remorque_totale = masse_remorque + charge_utile
        ratio = report_sellette / 100.0
        Poids_sur_essieu = (masse_a_vide * 9.81 * 0.60) + (masse_remorque_totale * 9.81 * ratio)
        h_g_combine = ((masse_a_vide * 0.60 * h_g) + (masse_remorque_totale * ratio * h_g_remorque)) / (masse_a_vide * 0.60 + masse_remorque_totale * ratio)
        seuil_adherence_type = 0.58
        facteur_derive = 0.09

    # --- SECTION 3 : REGLAGE DE LA VITESSE ET DE LA ROUTE ---
    st.subheader("3. Reglage de la vitesse et de la route")
    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        vitesse_kmh = st.slider("Vitesse du vehicule (km/h)", 10, 130, 75, step=5, key="vitesse_route_v7")
    with col_r2:
        rayon = st.slider("Rayon du virage R (m)", 15, 150, 45, step=5, key="rayon_route_v7")
        angle_virage_deg = st.slider("Angle total du virage (degres)", 30, 180, 90, step=5, key="angle_route_v7")
    with col_r3:
        devers_deg = st.slider("Angle de devers de la route (degres)", -5.0, 15.0, 2.5, step=0.5, key="devers_route_v7")
        adherence_pneus = st.slider("Coefficient d'adherence de la route", 0.1, 1.0, 0.4, step=0.05, key="adherence_route_v7")

    # --- CONVERSIONS ET CALCULS DYNAMIQUES DE FORCE ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    # Calcul dynamique de la force centrifuge appliquee sur l'essieu considere
    if type_vehicule == "Voiture seule (Permis B)" or type_vehicule == "Porteur seul (Camion Poids Lourd)":
        F_centrifuge_max = (masse_totale_calcul * (vitesse_ms ** 2)) / rayon
    elif type_vehicule == "Voiture avec remorque (Permis B)" or type_vehicule == "Porteur avec remorque (Camion Train Routier)":
        F_centrifuge_max = ((masse_totale_calcul * (vitesse_ms ** 2)) / rayon * 0.55) + (((masse_remorque_totale * (vitesse_ms ** 2)) / rayon) * 0.45)
    else: # Semi-remorque
        ratio_fc = report_sellette / 100.0
        F_centrifuge_max = (masse_a_vide * (vitesse_ms ** 2) / rayon * 0.60) + ((masse_remorque_totale * (vitesse_ms ** 2) / rayon) * ratio_fc)

    # --- PRE-CALCUL DE LA TRAJECTOIRE GEOMETRIQUE VUE DE DESSUS ---
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

    # --- SECTION 4 : VISUALISATION ET ACTIONS ANIMEES ---
    st.write("---")
    st.subheader("4. Visualisation de la simulation en direct")
    bouton_rouler = st.button("Lancer la simulation (Rouler)", key="bouton_global_v7")

    zone_gauche, zone_droite = st.columns(2)
    with zone_gauche:
        st.write("Repartition des forces (Vue Arriere)")
        espace_arriere = st.empty()
    with zone_droite:
        st.write("Trace progressif des traces d'essieux (Vue de dessus)")
        espace_dessus = st.empty()

    pneu_lw = 12 if "Voiture" in type_vehicule else 16
    pneu_h = 0.2 if "Voiture" in type_vehicule else 0.35
    label_cg = "CG Combine" if has_attelage else "CG"



    def executer_rendu_scene(index_v, crash_sauvegarde=None):
        en_virage = len(x_entree) <= index_v < (len(x_entree) + len(x_virage))
        
        # Gestion des forces stabilisees
        F_centrifuge_instant = F_centrifuge_max if en_virage else 0.0
        if crash_sauvegarde is not None:
            F_centrifuge_instant = crash_sauvegarde["Fc"]
            
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
            statut = "ACCIDENT : TONNEAU !"
            color_st = "#e74c3c"
            N_gauche = 0
            N_droite = Force_Normale_Totale
        elif Force_Tangente_Totale > seuil_adherence_type * Force_Normale_Totale:
            statut = "ACCIDENT : DERAPAGE !"
            color_st = "#f39c12"
            
        # Rendu Graphique 1 : Vue Arriere
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
        ax_arr.quiver(x_cg_a, y_cg_a, 0, -Poids_sur_essieu / f_scale, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2)
        if F_centrifuge_instant > 0:
            ax_arr.quiver(x_cg_a, y_cg_a, F_centrifuge_instant / f_scale, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2)
            
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































