
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application tableau électrique",
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
st.title("Application tableau électrique")
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
        st.rerun()

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
    "Tableau maison 130m²",
])

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
            key="btn_validation_identité_maitre",
            disabled=st.session_state.get("vérrouillé", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("vérrouillé", False):
                st.rerun()

with tab1:
    st.title("Simulateur Professionnel de Tableau Electrique - Maison 130m²")
    st.write("Configuration complete conforme a la norme NF C 15-100 avec repartition par rangees differentielles et schema tricolore.")

    TENSION_VOLT = 230

    # --- STRUCTURE TECHNIQUE DE LA MAISON ---
    limite_cable_ampere = {
        "0.0 mm²": 0,
        "1.5 mm²": 16,
        "2.5 mm²": 20,
        "4.0 mm²": 25,
        "6.0 mm²": 32
    }
    options_calibre_global = [0, 2, 10, 16, 20, 25, 32]

    # --- STRUCTURE REELLE DE LA MAISON (INITIALISEE INTEGRALEMENT A ZERO) ---
    structure_maison = {
        "Rangee 1 - Type A (Circuits Specifiques)": {
            "Plaques de cuisson": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 100},
            "Machine a laver": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 180},
            "Prise Vehicule": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 260},
            "VMC permanente": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 340}
        },
        "Rangee 2 - Type AC (Zone Jour)": {
            "Four encastrable": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 100},
            "Lave-vaisselle": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 180},
            "Prises Salon": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 260},
            "Prises Cuisine": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 340},
            "Eclairage Jour": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 420}
        },
        "Rangee 3 - Type AC (Zone Nuit)": {
            "Chauffage Sejour": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 100},
            "Chauffage Chambres": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 180},
            "Chauffe-eau": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 260},
            "Prises Chambres": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 340},
            "Eclairage Nuit": {"puissance": 0, "cable": "0.0 mm²", "calibre": 0, "x_pos": 420}
        }
    }

    # --- INITIALISATION DU SESSION STATE ---
    if "etat_disjoncteurs" not in st.session_state:
        st.session_state.etat_disjoncteurs = {}
        st.session_state.compteur_tentatives = {}
        st.session_state.sinistre = {}
        for rangee, appareils in structure_maison.items():
            st.session_state.etat_disjoncteurs[rangee] = {app: True for app in appareils}
            st.session_state.compteur_tentatives[rangee] = {app: 0 for app in appareils}
            st.session_state.sinistre[rangee] = {app: "Aucun" for app in appareils}

    if "etat_differentiels" not in st.session_state:
        st.session_state.etat_differentiels = {rangee: True for rangee in structure_maison}

    if "general_claque" not in st.session_state:
        st.session_state.general_claque = False

    if "parafoudre_operationnel" not in st.session_state:
        st.session_state.parafoudre_operationnel = True

    if "temps_secondes" not in st.session_state:
        st.session_state.temps_secondes = 0.0

    if "dernier_clic" not in st.session_state:
        st.session_state.dernier_clic = time.time()

    if "historique_pannes" not in st.session_state:
        st.session_state.historique_pannes = []

    # --- BARRE LATERALE DE CONTROLE ---
    st.sidebar.header("Parametres et Controle")

    calibre_general_max = st.sidebar.selectbox("Calibre du Disjoncteur General (A)", options=[10, 15, 30, 45, 60, 90], index=4)
    puissance_max_abonnement = calibre_general_max * TENSION_VOLT

    prix_kwh = st.sidebar.number_input("Prix du kWh (en €) :", min_value=0.01, max_value=2.00, value=0.25, step=0.01, format="%.2f")

    frequence_pannes = st.sidebar.slider("Frequence des pannes au hasard (%)", min_value=0, max_value=20, value=2, step=1)

    simulation_active = st.sidebar.checkbox("Activer l'horloge en temps reel", value=False)

    st.sidebar.markdown("---")
    if st.sidebar.button("Rearmer Disjoncteur General"):
        st.session_state.general_claque = False
        st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Normal", "Rearmement manuel du disjoncteur general principal de la maison."))
        st.rerun()

    if st.sidebar.button("Simuler Impact de Foudre"):
        st.session_state.general_claque = True
        for rangee in st.session_state.etat_differentiels:
            st.session_state.etat_differentiels[rangee] = False
        if st.session_state.parafoudre_operationnel:
            st.session_state.parafoudre_operationnel = False
            st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Alerte", "IMPACT DE FOUDRE ! Le module Parafoudre s'est sacrifie. Maison protegee."))
        else:
            for rangee in structure_maison:
                for app in structure_maison[rangee]:
                    puissance_cle = f"p_{rangee}_{app}"
                    if st.session_state.get(puissance_cle, 0) > 0:
                        if random.random() < 0.6:
                            st.session_state.sinistre[rangee][app] = "CARTE ELECTRONIQUE DETRUITE"
                            st.session_state.etat_disjoncteurs[rangee][app] = False
            st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Sinistre", "IMPACT DE FOUDRE ! Sans protection active, les composants branches ont grille."))
        st.rerun()

    if st.sidebar.button("Reparation par un electricien"):
        st.session_state.general_claque = False
        st.session_state.parafoudre_operationnel = True
        for rangee, appareils in structure_maison.items():
            st.session_state.etat_differentiels[rangee] = True
            for app in appareils:
                st.session_state.etat_disjoncteurs[rangee][app] = True
                st.session_state.compteur_tentatives[rangee][app] = 0
                st.session_state.sinistre[rangee][app] = "Aucun"
        st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Normal", "Passage de l'electricien professionnel. Remise aux normes complete et changement du parafoudre."))
        st.rerun()

    if st.sidebar.button("Vider memoire temporelle"):
        st.session_state.temps_secondes = 0.0
        st.session_state.historique_pannes = []
        st.rerun()

    # --- DEF : SIMULATION CENTRALISEE DES INCIDENTS ET BÊTISES ---
    def generer_incident_aleatoire():
        betises_possibles = [
            "multiprises_en_cascade",
            "ciseaux_dans_prise",
            "doigt_dans_prise",
            "objet_dans_prise",
            "defaut_carcasse_machine"
        ]
        accident = random.choice(betises_possibles)
        horodatage = round(st.session_state.temps_secondes, 1)
        
        if accident == "multiprises_en_cascade":
            r_target, a_target = "Rangee 2 - Type AC (Zone Jour)", "Prises Salon"
            if st.session_state.etat_disjoncteurs[r_target][a_target] and st.session_state.sinistre[r_target][a_target] == "Aucun":
                st.session_state.historique_pannes.append((horodatage, "Alerte", "BETISE : Branchement dangereux de plusieurs multiprises en cascade dans le salon ! Surcharge severe."))
                st.session_state[f"p_{r_target}_{a_target}"] = 4500
                
        elif accident == "ciseaux_dans_prise":
            r_target = random.choice(["Rangee 2 - Type AC (Zone Jour)", "Rangee 3 - Type AC (Zone Nuit)"])
            a_target = "Prises Salon" if "Zone Jour" in r_target else "Prises Chambres"
            if st.session_state.etat_disjoncteurs[r_target][a_target]:
                st.session_state.etat_disjoncteurs[r_target][a_target] = False
                st.session_state.historique_pannes.append((horodatage, "Alerte", f"BETISE : Des ciseaux metalliques ont ete enfonces dans les prises. Court-circuit franc, le disjoncteur divisionnaire de {a_target} a saute."))
                
        elif accident == "doigt_dans_prise":
            r_target = "Rangee 3 - Type AC (Zone Nuit)"
            if st.session_state.etat_differentiels[r_target]:
                st.session_state.etat_differentiels[r_target] = False
                st.session_state.historique_pannes.append((horodatage, "Sinistre", "ACCIDENT GRAVE : Contact direct avec un conducteur sous tension ! L'interrupteur differentiel 30mA a immediatement coupe la rangee."))
                
        elif accident == "objet_dans_prise":
            r_target, a_target = "Rangee 2 - Type AC (Zone Jour)", "Prises Cuisine"
            if st.session_state.etat_disjoncteurs[r_target][a_target]:
                st.session_state.etat_disjoncteurs[r_target][a_target] = False
                st.session_state.historique_pannes.append((horodatage, "Alerte", "ACCIDENT : Un objet humide est tombe dans une prise de la cuisine. Coupure automatique de la ligne."))
                
        elif accident == "defaut_carcasse_machine":
            r_target, a_target = "Rangee 1 - Type A (Circuits Specifiques)", "Machine a laver"
            if st.session_state.etat_differentiels[r_target]:
                st.session_state.etat_differentiels[r_target] = False
                st.session_state.historique_pannes.append((horodatage, "Alerte", "DEFAUT INTERNE : Defaut d'isolement sur la machine a laver, la phase touche la carcasse en metal. Le differentiel de Type A s'est declenche."))

    # --- DECLENCHEMENT MANUEL DES INCIDENTS (SIDEBAR) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Declenchement Manuel d'un Incident")

    dictionnaire_choix_betises = {
        "Multiprises en cascade (Surcharge)": "multiprises_en_cascade",
        "Ciseaux dans une prise (Court-circuit)": "ciseaux_dans_prise",
        "Doigt dans une prise (Electrocution)": "doigt_dans_prise",
        "Objet humide dans une prise (Alerte Cuisine)": "objet_dans_prise",
    "Defaut carcasse metallique (Machine a laver)": "defaut_carcasse_machine"
    }

    betise_selectionnee = st.sidebar.selectbox(
        "Choisir l'accident a provoquer :",
        options=list(dictionnaire_choix_betises.keys()),
        key="select_betise_manuelle"
    )

    if st.sidebar.button("Provoquer l'incident selectionne"):
        incident_technique = dictionnaire_choix_betises[betise_selectionnee]
        horodatage = round(st.session_state.temps_secondes, 1)
        
        if incident_technique == "multiprises_en_cascade":
            r_target, a_target = "Rangee 2 - Type AC (Zone Jour)", "Prises Salon"
            if st.session_state.etat_disjoncteurs[r_target][a_target] and st.session_state.sinistre[r_target][a_target] == "Aucun":
                st.session_state.historique_pannes.append((horodatage, "Alerte", "MANUEL - BETISE : Branchement volontaire de plusieurs multiprises en cascade. Surcharge severe."))
                st.session_state[f"p_{r_target}_{a_target}"] = 4500
                
        elif incident_technique == "ciseaux_dans_prise":
            r_target = random.choice(["Rangee 2 - Type AC (Zone Jour)", "Rangee 3 - Type AC (Zone Nuit)"])
            a_target = "Prises Salon" if "Zone Jour" in r_target else "Prises Chambres"
            
            if st.session_state.etat_disjoncteurs[r_target][a_target]:
                # Choix au hasard entre les deux scenarios (50% de chance chacun)
                scenario_violent = random.choice([True, False])
                
                if not scenario_violent:
                    # SCENARIO 1 : Coupure normale du disjoncteur divisionnaire seul (Selectivite parfaite)
                    st.session_state.etat_disjoncteurs[r_target][a_target] = False
                    st.session_state.historique_pannes.append(
                        (horodatage, "Alerte", f"BETISE : Des ciseaux metalliques ont provoque un court-circuit sur {a_target}. Le disjoncteur divisionnaire a saute normalement pour isoler la ligne.")
                    )
                else:
                    # SCENARIO 2 : Court-circuit ultra-violent avec destruction et declenchement du general
                    st.session_state.etat_disjoncteurs[r_target][a_target] = False
                    st.session_state.sinistre[r_target][a_target] = "DISJONCTEUR RESTE SOUDE PAR LE FLASH"
                    st.session_state.general_claque = True
                    st.session_state.historique_pannes.append(
                        (horodatage, "Sinistre", f"BETISE : Des ciseaux metalliques ont provoque un court-circuit ultra-violent sur {a_target}. Le disjoncteur de ligne a fondu, le DISJONCTEUR GENERAL a du sauter en secours !")
                    ) 
        elif incident_technique == "doigt_dans_prise":
            r_target = "Rangee 3 - Type AC (Zone Nuit)"
            if st.session_state.etat_differentiels[r_target]:
                st.session_state.etat_differentiels[r_target] = False
                st.session_state.historique_pannes.append((horodatage, "Sinistre", "MANUEL - ACCIDENT : Contact direct provoque sur un conducteur sous tension. Coupure differentielle 30mA immediate."))
                
        elif incident_technique == "objet_dans_prise":
            r_target, a_target = "Rangee 2 - Type AC (Zone Jour)", "Prises Cuisine"
            if st.session_state.etat_disjoncteurs[r_target][a_target]:
                st.session_state.etat_disjoncteurs[r_target][a_target] = False
                st.session_state.historique_pannes.append((horodatage, "Alerte", "MANUEL - ACCIDENT : Introduction d'un objet humide dans une prise de la cuisine."))
                
        elif incident_technique == "defaut_carcasse_machine":
            r_target, a_target = "Rangee 1 - Type A (Circuits Specifiques)", "Machine a laver"
            if st.session_state.etat_differentiels[r_target]:
                st.session_state.etat_differentiels[r_target] = False
                st.session_state.historique_pannes.append((horodatage, "Alerte", "MANUEL - DEFAUT : Simulation d'un defaut d'isolement de phase sur la carcasse de la machine a laver. Declenchement du Type A."))
        st.rerun()

    # --- GESTION DU TEMPS ELECTRIQUE ---
    if simulation_active:
        temps_actuel = time.time()
        pas_de_temps = temps_actuel - st.session_state.dernier_clic
        st.session_state.temps_secondes += pas_de_temps
        st.session_state.dernier_clic = temps_actuel
    else:
        st.session_state.dernier_clic = time.time()

    if simulation_active and not st.session_state.general_claque and frequence_pannes > 0:
        if random.random() < (frequence_pannes / 100.0):
            generer_incident_aleatoire()
            st.rerun()

    # --- PANNEAU DE CONTROLE CENTRAL ---
    st.header("1. Panneau de Controle des Lignes du Logement")

    puissance_totale_maison = 0.0
    intensite_totale_maison = 0.0

    titres_onglets = [rangee.split(" - ")[0] for rangee in structure_maison.keys()]
    tabs = st.tabs(titres_onglets)
    for idx, (rangee, appareils) in enumerate(structure_maison.items()):
        with tabs[idx]:
            diff_actif = st.session_state.etat_differentiels[rangee] and not st.session_state.general_claque
            
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                if st.session_state.general_claque:
                    st.error("Interrupteur Differentiel : Coupe par le general")
                elif st.session_state.etat_differentiels[rangee]:
                    st.success("Interrupteur Differentiel : Protection Active (Enclenche)")
                else:
                    st.warning("Interrupteur Differentiel : DECLENCHE")
            with col_d2:
                if st.button("Enclencher Differentiel", key=f"btn_diff_{rangee}"):
                    st.session_state.etat_differentiels[rangee] = True
                    st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Normal", f"Enclenchement de l'interrupteur differentiel pour {rangee.split(' - ')}."))
                    st.rerun()
            with col_d3:
                if st.button("Test 30mA", key=f"btn_test_{rangee}"):
                    if diff_actif:
                        st.session_state.etat_differentiels[rangee] = False
                        st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Alerte", f"Bouton TEST enclenche sur le differentiel 30mA de la {rangee.split(' - ')}."))
                        st.rerun()

            st.markdown("---")

            for app, specs in appareils.items():
                st.markdown(f"**Ligne : {app}**")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    p_val = st.number_input("Puissance (W)", min_value=0, max_value=12000, value=specs["puissance"], step=100, key=f"p_{rangee}_{app}")
                with col2:
                    options_cable = ["0.0 mm²", "1.5 mm²", "2.5 mm²", "4.0 mm²", "6.0 mm²"]
                    c_val = st.selectbox("Cable", options=options_cable, index=options_cable.index(specs["cable"]), key=f"c_{rangee}_{app}")
                with col3:
                    c_val_int = st.selectbox("Disjoncteur (A)", options=options_calibre_global, index=options_calibre_global.index(specs["calibre"]), key=f"cal_{rangee}_{app}")
                
                intensite_ligne = p_val / TENSION_VOLT if c_val_int != 0 else 0
                max_cable = limite_cable_ampere[c_val]
                sec_conseillee = "1.5 mm²" if intensite_ligne <= 16 else ("2.5 mm²" if intensite_ligne <= 20 else "6.0 mm²")
                
                # Surveillance normative et logique physique active
                if diff_actif and st.session_state.etat_disjoncteurs[rangee][app] and st.session_state.sinistre[rangee][app] == "Aucun" and p_val > 0:
                    if c_val_int == 0 or max_cable == 0:
                        st.session_state.etat_disjoncteurs[rangee][app] = False
                        st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Alerte", f"Coupure immediate sur {app} : Diametre de cable ou calibre regle a 0."))
                        st.rerun()
                    elif intensite_ligne > c_val_int:
                        st.session_state.etat_disjoncteurs[rangee][app] = False
                        st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Alerte", f"Calibre depasse sur {app} ({intensite_ligne:.1f}A > {c_val_int}A)."))
                        if st.session_state.compteur_tentatives[rangee][app] >= 2:
                            st.session_state.sinistre[rangee][app] = "RISQUE ELECTROCUTION MORTEL"
                            st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Sinistre", f"Contact direct non isole detecte sur la ligne {app}."))
                        st.rerun()
                    elif intensite_ligne > max_cable:
                        st.session_state.etat_differentiels[rangee] = False
                        st.session_state.etat_disjoncteurs[rangee][app] = False
                        st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Alerte", f"Surchauffe severe du cable sur {app} ({intensite_ligne:.1f}A > {max_cable}A)."))
                        if st.session_state.compteur_tentatives[rangee][app] >= 2:
                            st.session_state.sinistre[rangee][app] = "INCENDIE DANS LES CLOISONS"
                            st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Sinistre", f"Feu electrique declare lie au sous-dimensionnement sur {app}."))
                        st.rerun()
                    else:
                        puissance_totale_maison += p_val
                        intensite_totale_maison += intensite_ligne

                with col4:
                    if st.session_state.sinistre[rangee][app] != "Aucun":
                        st.error(f"CRITIQUE : {st.session_state.sinistre[rangee][app]}")
                    elif c_val_int == 0 or max_cable == 0:
                        st.error("Ligne non raccordee (Valeur à 0)")
                    elif st.session_state.general_claque or not st.session_state.etat_differentiels[rangee] or not st.session_state.etat_disjoncteurs[rangee][app]:
                        st.warning(f"Statut : Ligne Coupée | Conseille : {sec_conseillee}")
                    else:
                        index_actuel = list(limite_cable_ampere.keys()).index(c_val)
                        index_rec = list(limite_cable_ampere.keys()).index(sec_conseillee)
                        if index_actuel < index_rec:
                            st.markdown(f"<span style='color:magenta;'>Section {c_val} faible, {sec_conseillee} requise !</span>", unsafe_allow_html=True)
                        else:
                            st.success(f"En Service | {intensite_ligne:.1f} A")
                
                with col5:
                    if not st.session_state.etat_disjoncteurs[rangee][app] and st.session_state.sinistre[rangee][app] == "Aucun":
                        if st.button("Rearmer Ligne", key=f"rearm_{rangee}_{app}"):
                            st.session_state.compteur_tentatives[rangee][app] += 1
                            st.session_state.etat_disjoncteurs[rangee][app] = True
                            st.session_state.historique_pannes.append((round(st.session_state.temps_secondes, 1), "Normal", f"Tentative de rearmement du disjoncteur de {app} (Essai {st.session_state.compteur_tentatives[rangee][app]})."))
                            st.rerun()
                st.markdown("---")

    if puissance_totale_maison > puissance_max_abonnement or intensite_totale_maison > calibre_general_max:
        if not st.session_state.general_claque:
            st.session_state.general_claque = True
            st.session_state.historique_pannes.append(
                (round(st.session_state.temps_secondes, 1), "Alerte", "Disjoncteur general de branchement coupe (Limite Linky depassee).")
            )
            st.rerun()

    # --- MESURES FINANCIERES ET GLOBALES ---
    st.header("2. Mesures de Consommation Energétique et Cout Generaux")

    puissance_totale_kw = puissance_totale_maison / 1000
    temps_heures = st.session_state.temps_secondes / 3600
    energie_kwh = puissance_totale_kw * temps_heures
    cout_total = energie_kwh * prix_kwh

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Puissance Globale", f"{puissance_totale_maison:.0f} W / {puissance_max_abonnement:.0f} W")
    m2.metric("Temps de fonctionnement", f"{st.session_state.temps_secondes:.1f} sec")
    m3.metric("Energie accumulee", f"{energie_kwh:.6f} kWh")
    m4.metric("Montant de la facture", f"{cout_total:.4f} €")

    # --- RAPPORT GRAPHIQUE VECTORIEL TRICOLORE (SVG DYNAMIQUE) ---
    st.header("3. Schema Vectoriel Technique du Tableau General")

    svg_lines = []
    svg_lines.append('<svg width="100%" height="300" style="background-color:#121212; font-family:Arial, sans-serif;">')

    # Bornier de Terre centralise hache vert/jaune en bas
    svg_lines.append('<rect x="30" y="240" width="650" height="10" fill="#228b22" />')
    for hx in range(40, 680, 20):
        svg_lines.append(f'<line x1="{hx}" y1="240" x2="{hx+10}" y2="250" stroke="#ffff00" stroke-width="3" />')
    svg_lines.append('<text x="350" y="265" fill="#00ff00" font-size="9" text-anchor="middle">BORNIER PRINCIPAL DE TERRE (PROTECTION EQUIPOTENTIELLE)</text>')

    # Disjoncteur General EDF
    c_gen = "#ff4d4d" if st.session_state.general_claque else "#4caf50"
    svg_lines.append(f'<rect x="15" y="15" width="120" height="30" fill="{c_gen}" stroke="white" />')
    svg_lines.append(f'<text x="75" y="34" fill="white" font-size="10" font-weight="bold" text-anchor="middle">GENERAL : {"OFF" if st.session_state.general_claque else "ON"}</text>')

    # Colonne montante principale (Phase rouge et Neutre bleu)
    svg_lines.append('<line x1="135" y1="25" x2="150" y2="25" stroke="#ff3333" stroke-width="2" />')
    svg_lines.append('<line x1="135" y1="35" x2="155" y2="35" stroke="#3333ff" stroke-width="2" />')
    svg_lines.append('<line x1="150" y1="25" x2="150" y2="200" stroke="#ff3333" stroke-width="2" />')
    svg_lines.append('<line x1="155" y1="35" x2="155" y2="200" stroke="#3333ff" stroke-width="2" />')

    # Parafoudre SPD
    c_spd = "#4caf50" if st.session_state.parafoudre_operationnel else "#ff4d4d"
    svg_lines.append(f'<rect x="20" y="75" width="110" height="25" fill="{c_spd}" stroke="white" />')
    svg_lines.append(f'<text x="75" y="91" fill="white" font-size="8" font-weight="bold" text-anchor="middle">PARAFOUDRE : {"OK" if st.session_state.parafoudre_operationnel else "HS"}</text>')
    svg_lines.append('<line x1="150" y1="85" x2="130" y2="85" stroke="#ff3333" stroke-width="1.5" />')
    svg_lines.append('<line x1="155" y1="95" x2="130" y2="95" stroke="#3333ff" stroke-width="1.5" />')
    svg_lines.append('<line x1="75" y1="100" x2="75" y2="240" stroke="#228b22" stroke-width="1.5" />')

    y_offset = 60
    for rangee, appareils in structure_maison.items():
        diff_actif = st.session_state.etat_differentiels[rangee] and not st.session_state.general_claque
        c_diff = "#4caf50" if (st.session_state.etat_differentiels[rangee] and not st.session_state.general_claque) else "#ff9800"
        if st.session_state.general_claque: c_diff = "#444444"
        
        svg_lines.append(f'<line x1="150" y1="{y_offset + 8}" x2="165" y2="{y_offset + 8}" stroke="#ff3333" stroke-width="2" />')
        svg_lines.append(f'<line x1="155" y1="{y_offset + 16}" x2="165" y2="{y_offset + 16}" stroke="#3333ff" stroke-width="2" />')
        
        svg_lines.append(f'<rect x="165" y="{y_offset}" width="70" height="24" fill="{c_diff}" stroke="white" />')
        svg_lines.append(f'<text x="200" y="{y_offset + 15}" fill="white" font-size="8" font-weight="bold" text-anchor="middle">30mA DIFF</text>')
        
        c_peigne_p = "#ff3333" if diff_actif else "#555555"
        c_peigne_n = "#3333ff" if diff_actif else "#555555"
        svg_lines.append(f'<line x1="235" y1="{y_offset + 6}" x2="680" y2="{y_offset + 6}" stroke="{c_peigne_p}" stroke-width="2" />')
        svg_lines.append(f'<line x1="235" y1="{y_offset + 18}" x2="680" y2="{y_offset + 18}" stroke="{c_peigne_n}" stroke-width="2" />')
        
        for app, specs in appareils.items():
            x = 235 + specs["x_pos"]
            
            if st.session_state.sinistre[rangee][app] != "Aucun":
                c_div = "#7b1fa2"
                c_fils = "#ff00ff"
            elif not diff_actif or not st.session_state.etat_disjoncteurs[rangee][app]:
                c_div = "#ff9800"
                c_fils = "#555555"
            else:
                c_div = "#00b8d4"
                c_fils = "active"
                
            svg_lines.append(f'<rect x="{x}" y="{y_offset - 8}" width="40" height="40" fill="{c_div}" stroke="white" />')
            svg_lines.append(f'<text x="{x + 20}" y="{y_offset + 5}" fill="white" font-size="8" font-weight="bold" text-anchor="middle">{st.session_state.get(f"cal_{rangee}_{app}", 0)}A</text>')
            svg_lines.append(f'<text x="{x + 20}" y="{y_offset + 22}" fill="#eeeeee" font-size="7" text-anchor="middle">{app[:7]}</text>')
            
            f_p = "#ff3333" if c_fils == "active" else c_fils
            f_n = "#3333ff" if c_fils == "active" else c_fils
            
            svg_lines.append(f'<line x1="{x + 10}" y1="{y_offset + 32}" x2="{x + 10}" y2="{y_offset + 48}" stroke="{f_p}" stroke-width="1.5" />')
            svg_lines.append(f'<line x1="{x + 30}" y1="{y_offset + 32}" x2="{x + 30}" y2="{y_offset + 48}" stroke="{f_n}" stroke-width="1.5" />')
            svg_lines.append(f'<line x1="{x + 20}" y1="{y_offset + 32}" x2="{x + 20}" y2="240" stroke="#228b22" stroke-width="1.5" />')
            
        y_offset += 58

    svg_lines.append('</svg>')
    st.components.v1.html("\n".join(svg_lines), height=300)


    st.header("4 Le mur de la honte : Vos exploits en bande dessinee")

    # Verification du statut du tableau pour cibler l'accident en cours
    sinistre_actif = "Aucun"
    type_sinistre_detecte = ""

    for rangee, appareils in structure_maison.items():
        for app in appareils:
            if st.session_state.sinistre[rangee][app] != "Aucun":
                sinistre_actif = st.session_state.sinistre[rangee][app]
                type_sinistre_detecte = app
                break

    # --- 1. CASE BD : LES CISEAUX DANS LA PRISE (COURT-CIRCUIT SEVERE OU VIOLENT) ---
    if (sinistre_actif != "Aucun" and "SOUDE" in sinistre_actif) or (not st.session_state.general_claque and any(not st.session_state.etat_disjoncteurs[r][a] for r in structure_maison for a in structure_maison[r] if "Prises" in a and "ciseaux" in str(st.session_state.historique_pannes))):
        st.markdown("### Case active : Le Jeu Interdit")
        bd_ciseaux = """
        <svg width="100%" height="240" style="background-color:#FFFdf0; border: 3px solid #0f172a; border-radius: 8px; font-family:Arial, sans-serif;">
            <!-- Entete de case -->
            <rect x="10" y="10" width="180" height="25" fill="#fef08a" stroke="#0f172a" stroke-width="2"/>
            <text x="20" y="27" fill="#0f172a" font-size="11" font-weight="bold">PANEL 2: LE JEU INTERDIT</text>
            
            <!-- Dessin de la prise murale -->
            <rect x="300" y="80" width="60" height="60" fill="#f1f5f9" stroke="#0f172a" stroke-width="2" rx="5"/>
            <circle cx="330" cy="110" r="18" fill="#cbd5e1" stroke="#0f172a"/>
            <circle cx="320" cy="110" r="4" fill="#0f172a"/>
            <circle cx="340" cy="110" r="4" fill="#0f172a"/>
            
            <!-- Paire de ciseaux plantes dans les trous -->
            <path d="M 220,150 L 320,110 L 220,80" stroke="#475569" stroke-width="6" fill="none" stroke-linecap="round"/>
            <circle cx="210" cy="150" r="12" stroke="#0f172a" stroke-width="3" fill="none"/>
            <circle cx="210" cy="80" r="12" stroke="#0f172a" stroke-width="3" fill="none"/>
            
            <!-- Onomatopee de court-circuit -->
            <text x="110" y="120" fill="#dc2626" font-size="28" font-weight="bold" transform="rotate(-5, 110, 120)">KABOOM !</text>
            
            <!-- Nuage de fumee de cartoon -->
            <ellipse cx="330" cy="110" rx="45" ry="20" fill="rgba(0, 0, 0, 0.4)" filter="blur(4px)"/>
            <path d="M 330,90 Q 290,50 320,30" stroke="gray" stroke-width="2" fill="none" opacity="0.6"/>
            
            <!-- Triangles d'avertissement de danger electrique -->
            <polygon points="500,140 530,90 560,140" fill="#f59e0b" stroke="#0f172a" stroke-width="2"/>
            <text x="530" y="130" font-size="20" font-weight="bold" text-anchor="middle">!</text>
            
            <polygon points="580,140 610,90 640,140" fill="#f59e0b" stroke="#0f172a" stroke-width="2"/>
            <path d="M 610,98 L 600,118 L 620,118 L 610,135" stroke="#0f172a" stroke-width="2" fill="none"/>
        </svg>
        """
        st.components.v1.html(bd_ciseaux, height=250)
        st.error("Felicitations ! Vous venez de transformer une paire de ciseaux en appareil a souder de l'extreme. Le disjoncteur divisionnaire a fondu ou saute pour isoler la ligne.")

    # --- 2. CASE BD : DOIGT DANS LA PRISE (RISQUES SANITAIRES ET CORPORELS) ---
    elif not st.session_state.etat_differentiels["Rangee 3 - Type AC (Zone Nuit)"] and not st.session_state.general_claque:
        st.markdown("### Case active : Les Risques Sanitaires")
        bd_corps = """
        <svg width="100%" height="240" style="background-color:#FFFdf0; border: 3px solid #0f172a; border-radius: 8px; font-family:Arial, sans-serif;">
            <!-- Entete de case -->
            <rect x="10" y="10" width="190" height="25" fill="#fef08a" stroke="#0f172a" stroke-width="2"/>
            <text x="20" y="27" fill="#0f172a" font-size="11" font-weight="bold">PANEL 3: LES RISQUES SANITAIRES</text>
            
            <!-- Silhouette anatomique -->
            <rect x="100" y="70" width="40" height="100" fill="#fbcfe8" stroke="#0f172a" stroke-width="2" rx="10"/>
            <circle cx="120" cy="55" r="15" fill="#fbcfe8" stroke="#0f172a" stroke-width="2"/>
            
            <!-- Effets physiologiques de l'electrocution -->
            <circle cx="300" cy="65" r="18" fill="#fecdd3" stroke="#0f172a" stroke-width="2"/>
            <path d="M 290,65 L 295,55 L 300,75 L 305,60 L 310,65" stroke="#ef4444" stroke-width="2" fill="none"/>
            <text x="330" y="70" font-size="11" font-weight="bold">Arrêt Cardiaque (Fibrillation)</text>
            
            <!-- Dessin de la main / peau brûlee -->
            <rect x="280" y="115" width="40" height="35" fill="#f87171" stroke="#0f172a" stroke-width="2" rx="5"/>
            <path d="M 290,115 L 295,95 L 300,115" stroke="#dc2626" stroke-width="2" fill="none"/>
            <text x="330" y="135" font-size="11" font-weight="bold">Brûlures thermiques externes</text>
            
            <!-- Systematique de tetanie nerveuse -->
            <circle cx="300" cy="180" r="15" fill="#cbd5e1" stroke="#0f172a" stroke-width="2"/>
            <path d="M 290,180 Q 300,165 310,180" stroke="#0f172a" stroke-width="2" fill="none"/>
            <text x="330" y="185" font-size="11" font-weight="bold">Asphyxie par tetanie musculaire</text>
            
            <!-- Fleches indicatrices rouges -->
            <path d="M 140,100 L 270,65" stroke="#ef4444" stroke-width="2" fill="none"/>
            <path d="M 140,115 L 270,130" stroke="#ef4444" stroke-width="2" fill="none"/>
            <path d="M 140,130 L 270,180" stroke="#ef4444" stroke-width="2" fill="none"/>
        </svg>
        """
        st.components.v1.html(bd_corps, height=250)
        st.warning("Bravo Einstein ! Mettre les doigts dans la prise pour verifier s'il y a du courant, c'est audacieux. Heureusement que le differentiel 30mA a coupe en moins de 30ms pour vous sauver d'une fibrillation cardiaque.")

    # --- 3. CASE BD : LES MULTIPRISES EN CASCADE (LA SURCHARGE DE PRISE) ---
    elif st.session_state.get("p_Rangee 2 - Type AC (Zone Jour)_Prises Salon", 0) >= 4500:
        st.markdown("### Case active : La Surcharge de Prise")
        bd_surcharge = """
        <svg width="100%" height="240" style="background-color:#FFFdf0; border: 3px solid #0f172a; border-radius: 8px; font-family:Arial, sans-serif;">
            <rect x="10" y="10" width="220" height="25" fill="#fef08a" stroke="#0f172a" stroke-width="2"/>
            <text x="20" y="27" fill="#0f172a" font-size="11" font-weight="bold">PANEL 1: LA SURCHARGE DE PRISE</text>
            
            <!-- Blocs de multiprises empiles -->
            <rect x="260" y="60" width="45" height="110" fill="#e2e8f0" stroke="#0f172a" stroke-width="2" rx="4"/>
            <circle cx="282" cy="80" r="5" fill="#475569"/>
            <circle cx="282" cy="110" r="5" fill="#475569"/>
            <circle cx="282" cy="140" r="5" fill="#475569"/>
            
            <!-- Deuxieme bloc repique par dessus -->
            <rect x="330" y="40" width="45" height="90" fill="#cbd5e1" stroke="#0f172a" stroke-width="2" rx="4"/>
            <circle cx="352" cy="60" r="5" fill="#475569"/>
            <circle cx="352" cy="90" r="5" fill="#475569"/>
            
            <!-- Liaison filaire de cascade -->
            <path d="M 330,85 Q 300,100 282,110" stroke="#0f172a" stroke-width="3" fill="none"/>
            
            <!-- Ondes thermiques de surchauffe (Effet Joule) -->
            <path d="M 240,80 Q 230,90 240,100 Q 230,110 240,120" stroke="#dc2626" stroke-width="2" fill="none"/>
            <text x="120" y="110" fill="#dc2626" font-size="24" font-weight="bold">BZZZTT !</text>
            
            <!-- Le Rat inspecteur du batiment inquiet -->
            <circle cx="560" cy="120" r="25" fill="#94a3b8" stroke="#0f172a" stroke-width="2"/>
            <rect x="545" y="90" width="30" height="15" fill="#f59e0b" rx="2"/>
            <text x="510" y="75" fill="#dc2626" font-size="11" font-weight="bold">ALERTE !</text>
        </svg>
        """
        st.components.v1.html(bd_surcharge, height=250)
        st.warning("Regardez-moi cette magnifique cascade de multiprises. Le cable subit un effet Joule tellement violent qu'il pourrait faire fondre sa gaine isolante et declencher un incendie.")

    # --- 4. CASE BD : L'IMPACT DE FOUDRE (LES RISQUES POUR LE BÂTIMENT) ---
    elif not st.session_state.parafoudre_operationnel or (st.session_state.general_claque and sinistre_actif != "Aucun" and "INCENDIE" in sinistre_actif):
        st.markdown("### Case active : Les Risques pour le Batiment")
        bd_incendie = """
        <svg width="100%" height="240" style="background-color:#FFFdf0; border: 3px solid #0f172a; border-radius: 8px; font-family:Arial, sans-serif;">
            <rect x="10" y="10" width="230" height="25" fill="#fef08a" stroke="#0f172a" stroke-width="2"/>
            <text x="20" y="27" fill="#0f172a" font-size="11" font-weight="bold">PANEL 4: LES RISQUES POUR LE BÂTIMENT</text>
            
            <!-- Dessin structurel de la maison -->
            <polygon points="120,95 170,45 220,95" fill="#f97316" stroke="#0f172a" stroke-width="2"/>
            <rect x="130" y="95" width="80" height="80" fill="#ffedd5" stroke="#0f172a" stroke-width="2"/>
            
            <!-- Flammes de toiture -->
            <path d="M 160,45 Q 170,15 180,45 Q 190,25 200,55" fill="#ef4444" stroke="#0f172a" stroke-width="1.5"/>
            
            <!-- Gaine de cable fondu en gros plan -->
            <circle cx="410" cy="90" r="22" fill="#4b5563" stroke="#0f172a" stroke-width="2"/>
            <path d="M 395,85 C 405,105 405,75 420,95" stroke="#111827" stroke-width="4" fill="none"/>
            <text x="450" y="95" font-size="11" font-weight="bold">Gaine PVC carbonisee</text>
            
            <!-- Symbole de coupure totale en blackout -->
            <circle cx="410" cy="160" r="18" fill="none" stroke="#ef4444" stroke-width="2"/>
            <line x1="398" y1="148" x2="422" y2="172" stroke="#ef4444" stroke-width="2"/>
            <text x="450" y="165" font-size="11" font-weight="bold">Destruction thermique totale</text>
        </svg>
        """
        st.components.v1.html(bd_incendie, height=250)

    # --- 5. CASE BD : L'ETAT DE SIMULATION NORMAL (SANS ACCIDENT) ---
    else:
        st.markdown("### Case active : Situation Sous Controle")
        bd_sain = """
        <svg width="100%" height="240" style="background-color:#FFFdf0; border: 3px solid #0f172a; border-radius: 8px; font-family:Arial, sans-serif;">
            <rect x="10" y="10" width="200" height="25" fill="#bbf7d0" stroke="#0f172a" stroke-width="2"/>
            <text x="20" y="27" fill="#0f172a" font-size="11" font-weight="bold">SITUATION DU LOGEMENT : SÉCURISÉE</text>
            
            <circle cx="160" cy="120" r="35" fill="#475569" stroke="#0f172a" stroke-width="2"/>
            <rect x="145" y="70" width="30" height="15" fill="#cbd5e1" rx="2" stroke="#0f172a"/>
            
            <line x1="350" y1="120" x2="550" y2="120" stroke="#16a34a" stroke-width="3"/>
            <circle cx="450" cy="120" r="8" fill="#16a34a"/>
            
            <text x="230" y="115" fill="#0f172a" font-size="13" font-weight="bold">L'installation electrique est saine.</text>
            <text x="230" y="135" fill="#475569" font-size="11">Les protections veillent, la classe peut etudier en toute securite.</text>
        </svg>
        """
        st.components.v1.html(bd_sain, height=250)
        st.info("Miracle ! Aucun appareil n'a explose, aucun cable ne fume et aucun utilisateur n'a essaye de chatouiller les fils conducteurs. Pourvu que ca dure.")

    st.header("5. Historique Professionnel des Incidents et Rapport Technique")

    if st.session_state.historique_pannes:
        # 1. Declaration du contenu HTML
        html_content = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Rapport d'Incidents Electriques</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 40px; }
            h1 { color: #1e293b; border-bottom: 2px solid #cbd5e1; padding-bottom: 10px; }
            .info { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }
            th { background-color: #0f172a; color: #ffffff; font-weight: 600; }
            tr:hover { background-color: #f8fafc; }
            .badge { padding: 5px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold; text-transform: uppercase; }
            .badge-normal { background-color: #dcfce7; color: #15803d; }
            .badge-alerte { background-color: #fef3c7; color: #b45309; }
            .badge-sinistre { background-color: #fee2e2; color: #b91c1c; }
        </style>
    </head>
    <body>
        <h1>Rapport Technique d'Incidents de l'Installation Electrique</h1>
        <div class="info">
            <p><strong>Logement :</strong> Maison Individuelle 130m² (Conformite NF C 15-100)</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Horodatage (s)</th>
                    <th>Gravite / Type</th>
                    <th>Description de l'evenement</th>
                </tr>
            </thead>
            <tbody>
    """
        for temps, gravite, desc in reversed(st.session_state.historique_pannes):
            b_class = "badge-normal" if gravite == "Normal" else ("badge-alerte" if gravite == "Alerte" else "badge-sinistre")
            html_content += f"""            <tr>
                    <td><strong>{temps} s</strong></td>
                    <td><span class="badge {b_class}">{gravite}</span></td>
                    <td>{desc}</td>
                </tr>\n"""
                
        html_content += """        </tbody>
        </table>
    </body>
    </html>"""

        # 2. Bouton de téléchargement (IMPORTANT : aligné à l'intérieur du bloc IF avec 4 espaces)
        st.download_button(
            label="Telecharger le rapport complet (.html)",
            data=html_content,
            file_name="rapport_incidents_maison_130m2.html",
            mime="text/html"
        )
        
        # 3. Journal d'affichage dans la page web
        for temps, gravite, desc in reversed(st.session_state.historique_pannes):
            st.text(f"[{temps}s] - {gravite.upper()} - {desc}")
    else:
        st.write("L'installation electrique globale de la maison est saine. Aucun defaut sur le reseau.")

    # Boucle de rafraichissement automatique globale
    if simulation_active:
        time.sleep(0.4)
        st.rerun()
