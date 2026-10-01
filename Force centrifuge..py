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
    

    st.title("Simulateur de Dynamique de Véhicules en Virage (Vue Arrière & Vue de Dessus)")
    st.write("Modifiez les paramètres dans la barre latérale pour analyser le comportement et la trajectoire du véhicule en temps réel.")

    # --- BARRE LATÉRALE : SÉLECTION DU VÉHICULE ---
    st.sidebar.header("Type de Véhicule")
    type_vehicule = st.sidebar.selectbox(
        "Configuration :",
        [
            "Voiture seule (Permis B)",
            "Voiture avec remorque (Permis B)",
            "Porteur seul (Poids Lourd)",
            "Porteur avec remorque (Train Routier)",
            "Ensemble articulé (Tracteur + Semi-remorque)"
        ],
        key="select_vehicule_global"
    )

    # --- BARRE LATÉRALE : CONTROLE DE LA VITESSE ET DE LA ROUTE ---
    st.sidebar.header("Vitesse & Route")
    vitesse_kmh = st.sidebar.slider("Vitesse du véhicule (km/h)", 10, 150, 60, step=5, key="vitesse_vehicule_kmh")
    rayon = st.sidebar.slider("Rayon de courbure R (m)", 15, 400, 90, step=5, key="rayon_courbure_m")
    angle_virage_deg = st.sidebar.slider("Angle total du virage (°)", 15, 180, 90, step=5, key="angle_virage_deg")
    devers_deg = st.sidebar.slider("Angle de dévers de la route (°)", -5.0, 15.0, 2.5, step=0.5, key="devers_route_deg")
    vitesse_animation = st.sidebar.slider("Vitesse de l'animation", 1, 5, 3, key="vitesse_animation_sim")

    # --- BARRE LATÉRALE : CURSEURS DE MASSE ET DIMENSIONS SELON LE VÉHICULE ---
    st.sidebar.header("Masse & Dimensions")

    if type_vehicule == "Voiture seule (Permis B)":
        masse_a_vide = st.sidebar.slider("Masse à vide (kg)", 900, 2500, 1300, step=50)
        chargement = st.sidebar.slider("Passagers & Bagages (kg)", 0, 1000, 150, step=10)
        h_g = st.sidebar.slider("Hauteur du Centre de Gravité (m)", 0.4, 0.9, 0.55, step=0.05)
        voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.4, 1.8, 1.55, step=0.05)

    elif type_vehicule == "Voiture avec remorque (Permis B)":
        masse_a_vide = st.sidebar.slider("Masse à vide voiture (kg)", 900, 2500, 1300, step=50)
        chargement = st.sidebar.slider("Passagers & Bagages voiture (kg)", 0, 800, 150, step=10)
        h_g = st.sidebar.slider("Hauteur CG voiture (m)", 0.4, 0.9, 0.55, step=0.05)
        voie = st.sidebar.slider("Largeur de voie (m)", 1.4, 1.8, 1.55, step=0.05)
        masse_r = st.sidebar.slider("Masse à vide remorque (kg)", 150, 1000, 300, step=50)
        chargement_r = st.sidebar.slider("Chargement dans la remorque (kg)", 0, 2500, 400, step=50)
        poids_fleche = st.sidebar.slider("Poids sur la flèche (kg)", 30, 100, 65, step=5)

    elif type_vehicule == "Porteur seul (Poids Lourd)":
        masse_a_vide = st.sidebar.slider("Masse à vide du porteur (kg)", 6000, 14000, 9000, step=500)
        charge_utile = st.sidebar.slider("Masse du chargement (kg)", 0, 22000, 12000, step=500)
        h_g = st.sidebar.slider("Hauteur du Centre de Gravité (m)", 0.8, 2.8, 1.70, step=0.05)
        voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.8, 2.5, 2.20, step=0.05)

    elif type_vehicule == "Porteur avec remorque (Train Routier)":
        masse_a_vide = st.sidebar.slider("Masse à vide porteur (kg)", 6000, 14000, 9000, step=500)
        charge_utile = st.sidebar.slider("Chargement dans le porteur (kg)", 0, 22000, 12000, step=500)
        h_g = st.sidebar.slider("Hauteur CG porteur (m)", 0.8, 2.8, 1.70, step=0.05)
        voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.8, 2.5, 2.20, step=0.05)
        masse_r = st.sidebar.slider("Masse à vide remorque (kg)", 3000, 8000, 5000, step=500)
        charge_utile_r = st.sidebar.slider("Chargement dans la remorque (kg)", 0, 24000, 14000, step=500)
        h_g_r = st.sidebar.slider("Hauteur CG remorque (m)", 0.8, 2.8, 1.80, step=0.05)
        poids_timon = st.sidebar.slider("Charge verticale sur l'attelage (kg)", 0, 1000, 200, step=50)

    elif type_vehicule == "Ensemble articulé (Tracteur + Semi-remorque)":
        masse_a_vide = st.sidebar.slider("Masse à vide tracteur (kg)", 6000, 10000, 7500, step=500)
        h_g_t = st.sidebar.slider("Hauteur CG tracteur (m)", 0.6, 1.2, 0.85, step=0.05)
        voie = st.sidebar.slider("Largeur de voie de l'essieu (m)", 1.8, 2.5, 2.20, step=0.05)
        masse_s = st.sidebar.slider("Masse à vide semi (kg)", 5000, 9000, 6500, step=500)
        charge_s = st.sidebar.slider("Charge semi (kg)", 0, 28000, 18000, step=500)
        h_g_s = st.sidebar.slider("Hauteur CG semi (m)", 1.2, 3.2, 2.10, step=0.05)
        report_sellette = st.sidebar.slider("Report sur sellette (%)", 35, 55, 45, step=5)

    # --- CALCULS PHYSIQUES ---
    g = 9.81
    vitesse_ms = vitesse_kmh / 3.6
    alpha = np.radians(devers_deg)

    Poids_sur_essieu = 1000.0 * g
    F_centrifuge_sur_essieu = 500.0
    h_g_combine = 0.5
    seuil_adherence = 0.8
    label_cg = "CG"
    description_physique = ""
    has_attelage = False
    h_attelage = 0.5

    if type_vehicule == "Voiture seule (Permis B)":
        masse_totale = masse_a_vide + chargement
        Poids_sur_essieu = masse_totale * g
        F_centrifuge_sur_essieu = (masse_totale * (vitesse_ms ** 2)) / rayon
        h_g_combine = h_g
        seuil_adherence = 0.8
        label_cg = "CG Voiture"
        description_physique = "Centre de gravité bas. La voiture aura tendance à glisser plutôt qu'à se retourner."

    elif type_vehicule == "Voiture avec remorque (Permis B)":
        m_voiture = masse_a_vide + chargement
        m_remorque = masse_r + chargement_r
        Poids_sur_essieu = (m_voiture * g * 0.5) + (poids_fleche * g)
        F_centrifuge_sur_essieu = ((m_voiture * (vitesse_ms ** 2)) / rayon * 0.5) + (((m_remorque * (vitesse_ms ** 2)) / rayon) * 0.5)
        h_g_combine = ((m_voiture * g * 0.5 * h_g) + (((m_remorque * (vitesse_ms ** 2)) / rayon) * 0.5 * 0.45)) / F_centrifuge_sur_essieu
        seuil_adherence = 0.65
        has_attelage = True
        h_attelage = 0.45
        label_cg = "CG Combiné"
        description_physique = "La remorque pousse l'attelage latéralement et déstabilise l'arrière de la voiture."

    elif type_vehicule == "Porteur seul (Poids Lourd)":
        masse_totale = masse_a_vide + charge_utile
        Poids_sur_essieu = masse_totale * g
        F_centrifuge_sur_essieu = (masse_totale * (vitesse_ms ** 2)) / rayon
        h_g_combine = h_g
        seuil_adherence = 0.6
        label_cg = "CG Porteur"
        description_physique = "Centre de gravité haut. Risque majeur de tonneau avant même le début du dérapage."

    elif type_vehicule == "Porteur avec remorque (Train Routier)":
        m_porteur = masse_a_vide + charge_utile
        m_remorque = masse_r + charge_utile_r
        Poids_sur_essieu = (m_porteur * g * 0.55) + (poids_timon * g)
        F_centrifuge_sur_essieu = (m_porteur * (vitesse_ms ** 2) / rayon * 0.55) + ((m_remorque * (vitesse_ms ** 2) / rayon) * 0.45)
        h_g_combine = ((m_porteur * (vitesse_ms ** 2) / rayon * 0.55 * h_g) + ((m_remorque * (vitesse_ms ** 2) / rayon * 0.45) * h_g_r)) / F_centrifuge_sur_essieu
        seuil_adherence = 0.55
        has_attelage = True
        h_attelage = 0.60
        label_cg = "CG Combiné"
        description_physique = "L'effet bras de levier du timon sur le crochet arrière perturbe l'essieu moteur."

    elif type_vehicule == "Ensemble articulé (Tracteur + Semi-remorque)":
        m_semi = masse_s + charge_s
        ratio = report_sellette / 100.0
        Poids_sur_essieu = (masse_a_vide * g * 0.60) + (m_semi * g * ratio)
        F_centrifuge_sur_essieu = (masse_a_vide * (vitesse_ms ** 2) / rayon * 0.60) + ((m_semi * (vitesse_ms ** 2) / rayon) * ratio)
        h_g_combine = ((masse_a_vide * (vitesse_ms ** 2) / rayon * 0.60 * h_g_t) + (((m_semi * (vitesse_ms ** 2) / rayon) * ratio) * h_g_s)) / F_centrifuge_sur_essieu
        seuil_adherence = 0.58
        has_attelage = True
        h_attelage = 1.25
        label_cg = "CG Équivalent"
        description_physique = "La charge de la semi pèse sur la sellette en hauteur. Risque fort de mise en portefeuille."

    # Équations de projection
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
        statut = "RISQUE CRITIQUE DE RETOURNEMENT ! (Roue intérieure décollée)"
        couleur_statut = "#e74c3c"
        N_gauche = 0
        N_droite = Force_Normale_Totale
    elif Force_Tangente_Totale > seuil_adherence * Force_Normale_Totale:
        statut = "RISQUE DE PERTE D'ADHÉRENCE / DÉRAPAGE LATÉRAL"
        couleur_statut = "#f39c12"

    # --- PARTIE 1 : VUE ARRIÈRE ---
    st.subheader("1. Analyse de répartition des forces (Vue Arrière)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Force Centrifuge subie", f"{int(F_centrifuge_sur_essieu):,} N")
    col2.metric("Poids sur cet essieu", f"{int(Poids_sur_essieu):,} N")
    col3.metric("Force latérale nette (Ft)", f"{int(Force_Tangente_Totale):,} N")

    st.markdown(f"#### Diagnostic de sécurité : <span style='color:{couleur_statut}; font-weight:bold;'>{statut}</span>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x_route = np.array([-voie * 1.5, voie * 1.5])
    y_route = x_route * np.sin(alpha)
    ax.plot(x_route, y_route, color="#7f8c8d", lw=4, label="Chaussée")

    cos_a, sin_a = np.cos(alpha), np.sin(alpha)
    x_rg, y_rg = -voie / 2 * cos_a, -voie / 2 * sin_a
    x_rd, y_rd = voie / 2 * cos_a, voie / 2 * sin_a

    ax.plot([x_rg, x_rd], [y_rg, y_rd], color="#2c3e50", lw=5)
    pneu_lw = 12 if "Voiture" in type_vehicule else 16
    pneu_h = 0.2 if "Voiture" in type_vehicule else 0.35
    ax.plot([x_rg, x_rg + pneu_h * sin_a], [y_rg, y_rg - pneu_h * cos_a], color="#111111", lw=pneu_lw, solid_capstyle="round")
    ax.plot([x_rd, x_rd + pneu_h * sin_a], [y_rd, y_rd - pneu_h * cos_a], color="#111111", lw=pneu_lw, solid_capstyle="round")

    if has_attelage:
        ax.plot(0 - h_attelage * sin_a, 0 + h_attelage * cos_a, 'go', markersize=9, label="Attelage/Sellette")

    x_cg, y_cg = 0 - h_g_combine * sin_a, 0 + h_g_combine * cos_a
    ax.plot(x_cg, y_cg, 'ro', markersize=11, label=label_cg)

    facteur_echelle = max(Poids_sur_essieu, F_centrifuge_sur_essieu, Force_Normale_Totale) / 1.3
    ax.quiver(x_cg, y_cg, 0, -Poids_sur_essieu / facteur_echelle, angles='xy', scale_units='xy', scale=1, color='#2980b9', lw=2, label='Poids')
    ax.quiver(x_cg, y_cg, F_centrifuge_sur_essieu / facteur_echelle, 0, angles='xy', scale_units='xy', scale=1, color='#e67e22', lw=2, label='Force Cent.')

    if N_gauche > 0:
        ax.quiver(x_rg, y_rg, -N_gauche / facteur_echelle * sin_a, N_gauche / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#27ae60', lw=2)
    ax.quiver(x_rd, y_rd, -N_droite / facteur_echelle * sin_a, N_droite / facteur_echelle * cos_a, angles='xy', scale_units='xy', scale=1, color='#8e44ad', lw=2)

    ax.set_aspect('equal')
    ax.set_xlim(-voie * 1.8, voie * 1.8)
    ax.set_ylim(-0.5, h_g_combine + 1.0)
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    st.pyplot(fig)
    plt.close(fig)

    # --- PARTIE 2 : VUE DE DESSUS ---
    st.write("---")
    st.subheader("2. Tracé géométrique et simulation de trajectoire (Vue de dessus)")

    bouton_rouler = st.button("Lancer l'animation (Rouler)")

    largeur_voie = 3.5
    angle_rad = np.radians(angle_virage_deg)
    longueur_entree, longueur_sortie = 40.0, 40.0

    y_entree = np.linspace(0, longueur_entree, 25)
    x_entree = np.zeros_like(y_entree)
    theta = np.linspace(np.pi, np.pi - angle_rad, 60)
    x_virage = rayon + rayon * np.cos(theta)
    y_virage = longueur_entree + rayon * np.sin(theta)

    x_fin, y_fin = x_virage[-1], y_virage[-1]
    angle_sortie = - angle_rad
    distances_s = np.linspace(0, longueur_sortie, 25)
    x_sortie = x_fin + distances_s * np.cos(angle_sortie + np.pi/2)
    y_sortie = y_fin + distances_s * np.sin(angle_sortie + np.pi/2)

    x_axe = np.concatenate([x_entree, x_virage, x_sortie])
    y_axe = np.concatenate([y_entree, y_virage, y_sortie])

    x_bord_g = np.concatenate([x_entree - largeur_voie, rayon + (rayon + largeur_voie) * np.cos(theta), x_sortie + largeur_voie * (-np.sin(angle_sortie))])
    y_bord_g = np.concatenate([y_entree, longueur_entree + (rayon + largeur_voie) * np.sin(theta), y_sortie + largeur_voie * (np.cos(angle_sortie))])
    x_bord_d = np.concatenate([x_entree + largeur_voie, rayon + (rayon - largeur_voie) * np.cos(theta), x_sortie - largeur_voie * (-np.sin(angle_sortie))])
    y_bord_d = np.concatenate([y_entree, longueur_entree + (rayon - largeur_voie) * np.sin(theta), y_sortie - largeur_voie * (np.cos(angle_sortie))])

    espace_graphique = st.empty()

    def dessiner_dessus(index_v):
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.fill(np.concatenate([x_bord_g, x_bord_d[::-1]]), np.concatenate([y_bord_g, y_bord_d[::-1]]), color="#e2e8f0", alpha=0.9)
        ax2.plot(x_bord_g, y_bord_g, color="#ffffff", lw=2)
        ax2.plot(x_bord_d, y_bord_d, color="#ffffff", lw=2)
        ax2.plot(x_axe, y_axe, color="#fef08a", lw=1.5, linestyle="--")
        
        en_virage = len(x_entree) <= index_v < (len(x_entree) + len(x_virage))
        couleur_p = "red" if en_virage else "blue"
        ax2.plot(x_axe[index_v], y_axe[index_v], marker='o', color=couleur_p, markersize=11, label="Véhicule")
        
        ax2.set_aspect('equal')
        ax2.grid(True, linestyle=':', alpha=0.4)
        ax2.set_xlim(min(x_bord_g)-5, max(x_bord_g)+5)
        ax2.set_ylim(min(y_bord_d)-5, max(y_bord_g)+5)
        ax2.legend(loc='lower right')
        espace_graphique.pyplot(fig2)
        plt.close(fig2)

    if bouton_rouler:
        for i in range(len(x_axe)):
            dessiner_dessus(i)
            time.sleep(0.06 / vitesse_animation)
    else:
        dessiner_dessus(len(x_entree) + int(len(x_virage) / 2))

    st.info(f"""
    Mémo dynamique :
    * {description_physique}
    * Les forces physiques du premier graphique s'appliquent pleinement lorsque le point est rouge (dans la courbe). En ligne droite (point bleu), la force centrifuge tombe instantanément à zéro.
    """)










