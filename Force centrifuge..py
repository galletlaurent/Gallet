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
    
    st.set_page_config(page_title="Simulateur Dynamique de Véhicules", layout="wide")

    st.title("Simulateur de Dynamique de Véhicules en Virage (Vue Arrière)")
    st.write("Sélectionnez le type de véhicule pour analyser le comportement de l'essieu arrière soumis à la force centrifuge.")

    # --- NAVIGATION UNIFIÉE ---
    type_vehicule = st.selectbox(
        "Choisissez la configuration du véhicule :",
        [
            "Voiture seule (Permis B)",
            "Voiture avec remorque (Permis B)",
            "Porteur seul (Poids Lourd)",
            "Porteur avec remorque (Train Routier)",
            "Ensemble articulé (Tracteur + Semi-remorque)"
        ],
        key="select_vehicule_unique"
    )

    st.sidebar.header("Paramètres de la Route")
    rayon = st.sidebar.slider("Rayon de courbure du virage R (m)", 15, 400, 90, step=5, key="route_rayon_unique")
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 15.0, 2.5, step=0.5, key="route_devers_unique")

    # --- CONFIGURATION DYNAMIQUE DES VARIABLES SELON LE CHOIX ---
    g = 9.81
    voie = 1.55
    h_g_combine = 0.55
    Poids_sur_essieu = 10000.0
    F_centrifuge_sur_essieu = 5000.0
    label_cg = "Centre de Gravité"
    seuil_adherence = 0.8
    description_physique = ""
    has_attelage = False
    h_attelage = 0.5

    if type_vehicule == "Voiture seule (Permis B)":
        st.sidebar.header("Propriétés de la Voiture")
        vitesse_kmh = st.sidebar.slider("Vitesse (km/h)", 10, 150, 70, step=5, key="v_voiture_seule")
        masse_a_vide = st.sidebar.slider("Masse à vide (kg)", 900, 2500, 1300, step=50, key="m_voiture_seule")
        chargement = st.sidebar.slider("Passagers & Bagages (kg)", 0, 1000, 150, step=10, key="c_voiture_seule")
        h_g = st.sidebar.slider("Hauteur du CG (m)", 0.4, 0.9, 0.55, step=0.05, key="h_voiture_seule")
        voie = st.sidebar.slider("Largeur de voie (m)", 1.4, 1.8, 1.55, step=0.05, key="w_voiture_seule")
        
        masse_totale = masse_a_vide + chargement
        vitesse_ms = vitesse_kmh / 3.6
        Poids_sur_essieu = masse_totale * g
        F_centrifuge_sur_essieu = (masse_totale * (vitesse_ms ** 2)) / rayon
        h_g_combine = h_g
        seuil_adherence = 0.8
        label_cg = "CG Voiture"
        description_physique = "Une voiture possède un centre de gravité bas par rapport à sa largeur. Elle dérapera presque toujours avant de se retourner."

    elif type_vehicule == "Voiture avec remorque (Permis B)":
        st.sidebar.header("Propriétés de l'Attelage")
        vitesse_kmh = st.sidebar.slider("Vitesse (km/h)", 10, 130, 65, step=5, key="v_voiture_remorque")
        masse_v = st.sidebar.slider("Masse à vide voiture (kg)", 900, 2500, 1300, step=50, key="m_voiture_remorque")
        chargement_v = st.sidebar.slider("Charge voiture (kg)", 0, 800, 150, step=10, key="c_voiture_remorque")
        h_g_v = st.sidebar.slider("Hauteur CG voiture (m)", 0.4, 0.9, 0.55, step=0.05, key="h_voiture_remorque")
        voie = st.sidebar.slider("Largeur de voie (m)", 1.4, 1.8, 1.55, step=0.05, key="w_voiture_remorque")
        masse_r = st.sidebar.slider("Masse à vide remorque (kg)", 150, 1000, 300, step=50, key="m_remorque_b")
        chargement_r = st.sidebar.slider("Charge remorque (kg)", 0, 2500, 400, step=50, key="c_remorque_b")
        poids_fleche = st.sidebar.slider("Poids sur la flèche (kg)", 30, 100, 65, step=5, key="f_remorque_b")
        
        vitesse_ms = vitesse_kmh / 3.6
        m_voiture = masse_v + chargement_v
        m_remorque = masse_r + chargement_r
        Poids_sur_essieu = (m_voiture * g * 0.5) + (poids_fleche * g)
        F_centrifuge_sur_essieu = ((m_voiture * (vitesse_ms ** 2)) / rayon * 0.5) + (((m_remorque * (vitesse_ms ** 2)) / rayon) * 0.5)
        h_g_combine = ((m_voiture * g * 0.5 * h_g_v) + (((m_remorque * (vitesse_ms ** 2)) / rayon) * 0.5 * 0.45)) / F_centrifuge_sur_essieu
        seuil_adherence = 0.65
        has_attelage = True
        h_attelage = 0.45
        label_cg = "CG Combiné"
        description_physique = "La remorque pousse l'attelage vers l'extérieur du virage, augmentant les risques de dérapage du train arrière de la voiture."

    elif type_vehicule == "Porteur seul (Poids Lourd)":
        st.sidebar.header("Propriétés du Porteur")
        vitesse_kmh = st.sidebar.slider("Vitesse (km/h)", 10, 110, 55, step=5, key="v_porteur_seul")
        masse_a_vide = st.sidebar.slider("Masse à vide (kg)", 6000, 14000, 9000, step=500, key="m_porteur_seul")
        charge_utile = st.sidebar.slider("Charge utile (kg)", 0, 22000, 12000, step=500, key="c_porteur_seul")
        h_g = st.sidebar.slider("Hauteur du CG (m)", 0.8, 2.8, 1.70, step=0.05, key="h_porteur_seul")
        voie = st.sidebar.slider("Largeur de voie (m)", 1.8, 2.5, 2.20, step=0.05, key="w_porteur_seul")
        
        masse_totale = masse_a_vide + charge_utile
        vitesse_ms = vitesse_kmh / 3.6
        Poids_sur_essieu = masse_totale * g
        F_centrifuge_sur_essieu = (masse_totale * (vitesse_ms ** 2)) / rayon
        h_g_combine = h_g
        seuil_adherence = 0.6
        label_cg = "CG Porteur"
        description_physique = "Le porteur lourd possède un centre de gravité très haut. Le moment de renversement est fort : il peut basculer avant de glisser."

    elif type_vehicule == "Porteur avec remorque (Train Routier)":
        st.sidebar.header("Propriétés du Train Routier")
        vitesse_kmh = st.sidebar.slider("Vitesse (km/h)", 10, 90, 50, step=5, key="v_train_routier")
        masse_p = st.sidebar.slider("Masse à vide porteur (kg)", 6000, 14000, 9000, step=500, key="m_porteur_train")
        charge_p = st.sidebar.slider("Charge porteur (kg)", 0, 22000, 12000, step=500, key="c_porteur_train")
        h_g_p = st.sidebar.slider("Hauteur CG porteur (m)", 0.8, 2.8, 1.70, step=0.05, key="h_porteur_train")
        voie = st.sidebar.slider("Largeur de voie (m)", 1.8, 2.5, 2.20, step=0.05, key="w_porteur_train")
        masse_r = st.sidebar.slider("Masse à vide remorque (kg)", 3000, 8000, 5000, step=500, key="m_remorque_train")
        charge_r = st.sidebar.slider("Charge remorque (kg)", 0, 24000, 14000, step=500, key="c_remorque_train")
        h_g_r = st.sidebar.slider("Hauteur CG remorque (m)", 0.8, 2.8, 1.80, step=0.05, key="h_remorque_train")
        poids_timon = st.sidebar.slider("Charge verticale attelage (kg)", 0, 1000, 200, step=50, key="f_train_routier")
        
        vitesse_ms = vitesse_kmh / 3.6
        m_porteur = masse_p + charge_p
        m_remorque = masse_r + charge_r
        Poids_sur_essieu = (m_porteur * g * 0.55) + (poids_timon * g)
        F_centrifuge_sur_essieu = (m_porteur * (vitesse_ms ** 2) / rayon * 0.55) + ((m_remorque * (vitesse_ms ** 2) / rayon) * 0.45)
        h_g_combine = ((m_porteur * (vitesse_ms ** 2) / rayon * 0.55 * h_g_p) + ((m_remorque * (vitesse_ms ** 2) / rayon * 0.45) * h_g_r)) / F_centrifuge_sur_essieu
        seuil_adherence = 0.55
        has_attelage = True
        h_attelage = 0.60
        label_cg = "CG Combiné"
        description_physique = "L'effet bras de levier de la remorque attelée en porte-à-faux arrière applique une force latérale critique sur le train arrière."

    elif type_vehicule == "Ensemble articulé (Tracteur + Semi-remorque)":
        st.sidebar.header("Propriétés de la Semi")
        vitesse_kmh = st.sidebar.slider("Vitesse (km/h)", 10, 90, 50, step=5, key="v_semi_articule")
        masse_t = st.sidebar.slider("Masse à vide tracteur (kg)", 6000, 10000, 7500, step=500, key="m_tracteur_semi")
        h_g_t = st.sidebar.slider("Hauteur CG tracteur (m)", 0.6, 1.2, 0.85, step=0.05, key="h_tracteur_semi")
        voie = st.sidebar.slider("Largeur de voie (m)", 1.8, 2.5, 2.20, step=0.05, key="w_tracteur_semi")
        masse_s = st.sidebar.slider("Masse à vide semi (kg)", 5000, 9000, 6500, step=500, key="m_semi_pure")
        charge_s = st.sidebar.slider("Charge semi (kg)", 0, 28000, 18000, step=500, key="c_semi_pure")
        h_g_s = st.sidebar.slider("Hauteur CG semi (m)", 1.2, 3.2, 2.10, step=0.05, key="h_semi_pure")
        report_sellette = st.sidebar.slider("Report sur sellette (%)", 35, 55, 45, step=5, key="r_sellette_semi")
        
        vitesse_ms = vitesse_kmh / 3.6
        m_semi = masse_s + charge_s
        ratio = report_sellette / 100.0
        Poids_sur_essieu = (masse_t * g * 0.60) + (m_semi * g * ratio)
        F_centrifuge_sur_essieu = (masse_t * (vitesse_ms ** 2) / rayon * 0.60) + ((m_semi * (vitesse_ms ** 2) / rayon) * ratio)
        h_g_combine = ((masse_t * (vitesse_ms ** 2) / rayon * 0.60 * h_g_t) + (((m_semi * (vitesse_ms ** 2) / rayon) * ratio) * h_g_s)) / F_centrifuge_sur_essieu
        seuil_adherence = 0.58
        has_attelage = True
        h_attelage = 1.25
        label_cg = "CG Équivalent"
        description_physique = "La semi-remorque repose sur la sellette en hauteur. La force centrifuge applique un fort couple de torsion, risquant la mise en portefeuille."

    # --- PROJECTIONS RÉFÉRENTIEL ROUTE ---
    alpha = np.radians(devers_deg)
    P_normal = Poids_sur_essieu * np.cos(alpha)
    P_tangent = Poids_sur_essieu * np.sin(alpha)
    F_normal = F_centrifuge_sur_essieu * np.sin(alpha)
    F_tangent = F_centrifuge_sur_essieu * np.cos(alpha)

    Force_Normale_Totale = P_normal + F_normal
    Force_Tangente_Totale = F_tangent - P_tangent

    N_gauche = (Force_Normale_Totale * (voie / 2) - Force_Tangente_Totale * h_g_combine) / voie
    N_droite = Force_Normale_Totale - N_gauche

    # --- TRAITEMENT STABILITÉ ---
    statut = "VEHICULE STABLE"
    couleur_statut = "#2ecc71"
    if N_gauche <= 0:
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (Roue intérieure décollée)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > seuil_adherence * Force_Normale_Totale:
        statut = "RISQUE DE PERTE D'ADHÉRENCE / DÉRAPAGE LATÉRAL"
        couleur_statut = "#f39c12"

    # --- INTERFACE GRAPHIQUE STREAMLIT ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Force Centrifuge subie", f"{int(F_centrifuge_sur_essieu):,} N")
    col2.metric("Poids vertical subi", f"{int(Poids_sur_essieu):,} N")
    col3.metric("Force latérale nette", f"{int(Force_Tangente_Totale):,} N")

    st.markdown(f"### Diagnostic de sécurité : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    # --- RENDU VECTORIEL MATPLOTLIB ---
    fig, ax = plt.subplots(figsize=(9, 5.5))

    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#7f8c8d", lw=4, label="Chaussée (Dévers)")

    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=6, label="Axe d'essieu")

    pneu_lw = 14 if "Voiture" in type_vehicule else 18
    pneu_h = 0.2 if "Voiture" in type_vehicule else 0.35
    ax.plot([x_rg, x_rg + pneu_h * sin_a], [y_rg, y_rg - pneu_h * cos_a], color="#111111", lw=pneu_lw, solid_capstyle="round")
    ax.plot([x_rd, x_rd + pneu_h * sin_a], [y_rd, y_rd - pneu_h * cos_a], color="#111111", lw=pneu_lw, solid_capstyle="round")

    if has_attelage:
        x_att = 0 - h_attelage * sin_a
        y_att = 0 + h_attelage * cos_a
        ax.plot(x_att, y_att, 'go', markersize=10, label="Point d'attelage")

    x_cg = 0 - h_g_combine * sin_a
    y_cg = 0 + h_g_combine * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=12, label=label_cg)

    max_f = max(Poids_sur_essieu, F_centrifuge_sur_essieu, Force_Normale_Totale)
    facteur_echelle = max_f / 1.3

    ax.quiver(x_cg, y_cg, 0, -Poids_sur_essieu / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2.5, label='Poids (G)')
    ax.quiver(x_cg, y_cg, F_centrifuge_sur_essieu / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2.5, label='Force Centrifuge (Fc)')

    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2.5, label='Appui Roue Intérieure')
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2.5, label='Appui Roue Extérieure')

    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g_combine + 1.2)
    ax.axhline(0, color='black', linewidth=0.5, linestyle=':')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title(f"Répartition vectorielle : {type_vehicule}", fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.0))

    st.pyplot(fig)

    st.info(f"""
    Informations physiques :
    * {description_physique}
    * Le rôle du dévers : L'inclinaison de la route permet d'utiliser une composante du poids propre du véhicule pour contrer l'effet de la force centrifuge. Un dévers bien calculé stabilise l'empreinte au sol et réduit le transfert de charge vers la roue extérieure.
    """)




    st.write("---")
    st.subheader("Tracé géométrique de la route et trajectoire (Vue de dessus)")

    # --- PARAMÈTRES SUPPLÉMENTAIRES DANS LA BARRE LATÉRALE ---
    st.sidebar.header("Géométrie du Virage (Vue de dessus)")
    # Permet de régler l'angle total de changement de direction du virage (ex: un virage en équerre fait 90°)
    angle_virage_deg = st.sidebar.slider(
        "Angle de déviation du virage (°)", 
        15, 180, 90, step=5, 
        key="route_angle_deviation"
    )

    # Largeur d'une route nationale / départementale standard (2 x 3.5m)
    largeur_route = 7.0  
    largeur_voie = largeur_route / 2

    # --- CALCULS GÉOMÉTRIQUES DU TRACÉ VUE DE DESSUS ---
    angle_rad = np.radians(angle_virage_deg)
    longueur_entree = 40.0  # Longueur de la ligne droite avant le virage (m)
    longueur_sortie = 40.0  # Longueur de la ligne droite après le virage (m)

    # 1. Génération de la ligne droite d'entrée (axe vertical Y allant vers le haut)
    y_entree = np.linspace(0, longueur_entree, 20)
    x_entree = np.zeros_like(y_entree)

    # Centre de courbure du virage (situé à droite de la ligne droite d'entrée)
    cx = rayon
    cy = longueur_entree

    # 2. Génération du virage en arc de cercle
    # Les angles vont de 180° (à gauche du centre) à (180 - angle_virage) en tournant à droite
    theta = np.linspace(np.pi, np.pi - angle_rad, 50)
    x_virage = cx + rayon * np.cos(theta)
    y_virage = cy + rayon * np.sin(theta)

    # Point de fin du virage (tangente de sortie)
    x_fin_virage = x_virage[-1]
    y_fin_virage = y_virage[-1]

    # Angle de la direction de sortie
    angle_sortie = - angle_rad

    # 3. Génération de la ligne droite de sortie (dans le prolongement de la tangente)
    distances_sortie = np.linspace(0, longueur_sortie, 20)
    x_sortie = x_fin_virage + distances_sortie * np.cos(angle_sortie + np.pi/2)
    y_sortie = y_fin_virage + distances_sortie * np.sin(angle_sortie + np.pi/2)

    # --- FUSION DES AXES (LIGNE DE CENTRE / LIGNE DE FOI) ---
    x_centre = np.concatenate([x_entree, x_virage, x_sortie])
    y_centre = np.concatenate([y_entree, y_virage, y_sortie])

    # --- CRÉATION DE LA FIGURE VUE DE DESSUS ---
    fig2, ax2 = plt.subplots(figsize=(10, 8))

    # Calcul des vecteurs normaux pour tracer les bords de la route et la ligne médiane
    def tracer_bord_route(x, y, decalage, style='-', couleur='#cbd5e1', epaisseur=1.5):
        # Approximation des normales locales pour élargir la route uniformément
        nx = np.zeros_like(x)
        ny = np.zeros_like(y)
        
        # Calcul des tangentes
        dx = np.gradient(x)
        dy = np.gradient(y)
        
        # Normalisation pour obtenir les vecteurs normaux perpendiculaires à la route
        norme = np.sqrt(dx**2 + dy**2)
        # Évite la division par zéro
        norme[norme == 0] = 1.0 
        
        nx = -dy / norme
        ny = dx / norme
        
        ax2.plot(x + decalage * nx, y + decalage * ny, linestyle=style, color=couleur, linewidth=epaisseur)

    # Remplissage de la chaussée (Gris asphalte)
    ax2.fill_between(x_centre, y_centre - largeur_voie*2, y_centre + largeur_voie*2, color="#334155", alpha=0.1)

    # Dessin des composants de la route
    tracer_bord_route(x_centre, y_centre, 0, style='--', couleur='#fef08a', epaisseur=1.5) # Ligne médiane jaune discontinue
    tracer_bord_route(x_centre, y_centre, -largeur_voie, style='-', couleur='#ffffff', epaisseur=2) # Bord extérieur droit (ligne blanche)
    tracer_bord_route(x_centre, y_centre, largeur_voie, style='-', couleur='#ffffff', epaisseur=2)  # Bord extérieur gauche (ligne blanche)

    # Affichage de la position de la voiture (Placée arbitrairement au milieu du virage pour illustration)
    index_virage_milieu = len(x_entree) + int(len(x_virage) / 2)

    # Dessin de la position du véhicule
    ax2.plot(x_centre[index_virage_milieu], y_centre[index_virage_milieu], 'ro', markersize=10, label="Position du véhicule")

    # Paramétrages géométriques du graphique
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.set_title(f"Plan de la route double voies (Largeur: {largeur_route}m, Rayon: {rayon}m)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Distance X (m)")
    ax2.set_ylabel("Distance Y (m)")
    ax2.legend(loc='lower left')

    # Rendu dans Streamlit
    st.pyplot(fig2)

    st.info("""
    Informations géométriques (Vue de dessus) :
    * L'axe de la route est composé d'une ligne droite initiale d'approche (tangente), suivie d'une transition circulaire parfaite basée sur votre rayon de courbure (R), et se termine par une ligne droite de sortie.
    * La force centrifuge calculée dans le premier graphique s'applique exclusivement lorsque le véhicule se situe dans la section courbe (arc de cercle). En ligne droite (entrée et sortie), la force centrifuge est rigoureusement nulle ($F_c = 0$).
    """)

















