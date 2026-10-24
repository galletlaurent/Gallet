
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application transmission d'informations ",
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
st.title("Application transmission d'informations")
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
    "Historique",
    "Les ondes radio",
    "Le téléphone à la maison",
    "Les téléphones portables: smartphone",
    "La fibre optique",
    "Le réseau satellite",
    "Le WIFI",
    "Le bluetooth",
    "L'infra rouge",    
    "Les brouilleurs d'onde",
    "Du Téléphone au Téléphone"    
])

tab0 = onglets[0]
tab1 = onglets[1] 
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4] 
tab5 = onglets[5] 
tab6 = onglets[6] 
tab7 = onglets[7] 
tab8 = onglets[8]
tab9 = onglets[9]
tab10 = onglets[10]
tab11 = onglets[11]

def afficher_atelier_synthese_reseau(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 11 (Synthèse Réseau) sur deux colonnes étanches."""
    import random

    questions_sources_syn = [
        {"id": "t_syn_1", "q": "Par quel composant matériel la voix humaine est-elle convertie en données binaires (0 et 1) ?", "options": ["Le Convertisseur Analogique-Numérique (CAN)", "L'antenne fouet", "La carte SIM"], "rep": "Le Convertisseur Analogique-Numérique (CAN)"},
        {"id": "t_syn_2", "q": "Quelle affirmation est vraie concernant la communication entre deux smartphones proches ?", "options": ["Ils ne communiquent jamais en direct et transitent obligatoirement par des antennes et de la fibre", "Ils s'envoient les données directement par liaison infrarouge", "Ils passent par un fil de cuivre invisible"], "rep": "Ils ne communiquent jamais en direct et transitent obligatoirement par des antennes et de la fibre"},
        {"id": "t_syn_3", "q": "Quel type d'ondes physiques assure le transport du signal dans l'air entre le téléphone et le pylône ?", "options": ["Les ondes radio hyperfréquences (micro-ondes)", "Les ondes sonores acoustiques", "Les faisceaux laser ultraviolets"], "rep": "Les ondes radio hyperfréquences (micro-ondes)"},
        {"id": "t_syn_4", "q": "Quel milieu physique transporte le signal sous terre entre les antennes-relais à l'échelle nationale ?", "options": ["Les câbles de fibre optique", "Les lignes électriques de haute tension", "Les tuyaux d'air comprimé"], "rep": "Les câbles de fibre optique"},
        {"id": "t_syn_5", "q": "Quel est l'organe central de l'opérateur chargé de localiser le récepteur sur la planète et d'aiguiller l'appel ?", "options": ["Le Cœur de Réseau", "La boussole magnétique", "Le transpondeur satellite"], "rep": "Le Cœur de Réseau"},
        {"id": "t_syn_6", "q": "Comment appelle-t-on le saut hertzien reliant l'antenne-relais locale vers le smartphone de l'utilisateur ?", "options": ["La liaison descendante (Downlink)", "La liaison montante (Uplink)", "Le saut de fréquence"], "rep": "La liaison descendante (Downlink)"},
        {"id": "t_syn_7", "q": "Quelle pièce du smartphone récepteur reconvertit les données numériques en signal électrique pour le haut-parleur ?", "options": ["Le Convertisseur Numérique-Analogique (CNA)", "La carte SD d'extension", "La batterie Li-ion"], "rep": "Le Convertisseur Numérique-Analogique (CNA)"},
        {"id": "t_syn_8", "q": "Quel est le principal point fort de la technologie 5G par rapport à la 4G pour l'industrie ?", "options": ["Une latence ultra-basse atteignant 1 milliseconde", "Une portée augmentée à 100 kilomètres", "L'utilisation de fils de cuivre plus épais"], "rep": "Une latence ultra-basse atteignant 1 milliseconde"},
        {"id": "t_syn_9", "q": "Dans la fibre optique souterraine, sous quelle forme physique l'information se déplace-t-elle ?", "options": ["Sous forme d'impulsions lumineuses (photons)", "Sous forme d'électrons libres", "Sous forme de vibrations sonores"], "rep": "Sous forme d'impulsions lumineuses (photons)"},
        {"id": "t_syn_10", "q": "Quelle unité standard exprime le retard ou temps de réponse d'un paquet sur le réseau ?", "options": ["La latence en millisecondes (ms)", "Le débit en Mbps", "La fréquence en Gigahertz"], "rep": "La latence en millisecondes (ms)"}
    ]

    if "ordre_quiz_tab11_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_syn)
        st.session_state.ordre_quiz_tab11_telecom_aleatoire = questions_sources_syn

    st.session_state.champs_telecom11_clean = [
        ("1. Capturer la voix exige d'abord de la convertir en données .......... numériques.", ["Choisir...", "binaires", "analogiques"], "binaires", "telecom11_t1"),
        ("2. Les données sont injectées dans l'air via des ondes radio ..........", ["Choisir...", "hyperfréquences", "sonores"], "hyperfréquences", "telecom11_t2"),
        ("3. Le trajet aérien ascendant du smartphone au pylône est la liaison ..........", ["Choisir...", "montante", "descendante"], "montante", "telecom11_t3"),
        ("4. Sous le sol, le signal transite à la vitesse de la lumière dans la ..........", ["Choisir...", "fibre", "brique"], "fibre", "telecom11_t4"),
        ("5. Identifier l'antenne où se trouve le destinataire est le rôle du .......... de réseau.", ["Choisir...", "Cœur", "Répéteur"], "Cœur", "telecom11_t5"),
        ("6. Le signal repart du pylône d'arrivée vers le destinataire en liaison ..........", ["Choisir...", "descendante", "montante"], "descendante", "telecom11_t6"),
        ("7. Les bits reçus sont reconvertis en électricité par le convertisseur ..........", ["Choisir...", "CNA", "CAN"], "CNA", "telecom11_t7"),
        ("8. Le courant fait vibrer le haut-parleur pour recréer l'onde .......... audible.", ["Choisir...", "sonore", "hertzienne"], "sonore", "telecom11_t8"),
        ("9. Par rapport à la 4G, la 5G divise par trente le temps de ..........", ["Choisir...", "latence", "calcul"], "latence", "telecom11_t9"),
        ("10. Ce grand réseau maillé planétaire assure l'interconnexion en quelques ..........", ["Choisir...", "millisecondes", "heures"], "millisecondes", "telecom11_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique Final (10 questions - 10 pts)")
        if "ordre_quiz_tab11_telecom_aleatoire" in st.session_state:
            if "inc_local_tel11" not in st.session_state: st.session_state.inc_local_tel11 = 0
            st.session_state.inc_local_tel11 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab11_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel11_{q_data['id']}_inst_{st.session_state.inc_local_tel11}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Finale (Texte à trous - 10 pts)")
        if "champs_telecom11_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel11", 1)
            for idx, ligne in enumerate(st.session_state.champs_telecom11_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel11_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_brouilleurs(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 10 sur deux colonnes étanches."""
    import random

    questions_sources_br = [
        {"id": "t_br_1", "q": "Quel est le principe physique fondamental utilisé par un brouilleur d'onde ?", "options": ["Saturer une bande de fréquence avec un bruit radio plus puissant que le signal légitime", "Couper physiquement les câbles de cuivre", "Créer un vide d'air absolu autour de l'appareil"], "rep": "Saturer une bande de fréquence avec un bruit radio plus puissant que le signal légitime"},
        {"id": "t_br_2", "q": "Comment appelle-t-on le rapport entre la puissance du signal utile et celle du bruit parasite ?", "options": ["Le rapport Signal sur Bruit (SNR)", "L'indicateur SSID", "L'indice de réfraction totale"], "rep": "Le rapport Signal sur Bruit (SNR)"},
        {"id": "t_br_3", "q": "Quel est l'effet d'un brouillage sur le récepteur (smartphone ou box) ?", "options": ["Le récepteur ne parvient plus à décoder les données utiles au milieu du bruit", "Le récepteur double sa vitesse de téléchargement", "Le récepteur change de couleur de coque"], "rep": "Le récepteur ne parvient plus à décoder les données utiles au milieu du bruit"},
        {"id": "t_br_4", "q": "En France, quelle est la règle juridique générale concernant la détention et l'usage de brouilleurs par des particuliers ?", "options": ["Ils sont strictement interdits par la loi", "Ils sont autorisés uniquement dans les chambres", "Ils sont obligatoires dans les écoles"], "rep": "Ils sont strictement interdits par la loi"},
        {"id": "t_br_5", "q": "Quel type d'organisme public ou étatique est légalement autorisé à utiliser des brouilleurs (ex: en prison ou lors d'opérations) ?", "options": ["Les forces de sécurité, l'administration pénitentiaire ou l'armée", "Les cinémas de quartier", "Les syndics de copropriété"], "rep": "Les forces de sécurité, l'administration pénitentiaire ou l'armée"},
        {"id": "t_br_6", "q": "Comment réagit un signal Wi-Fi ou Bluetooth face à un brouilleur opérant sur la fréquence de 2,4 GHz ?", "options": ["La liaison se dégrade immédiatement jusqu'à la déconnexion", "La liaison passe sur un câble invisible", "La portée augmente de dix mètres"], "rep": "La liaison se dégrade immédiatement jusqu'à la déconnexion"},
        {"id": "t_br_7", "q": "Quelle technique de brouillage consiste à saturer spécifiquement un seul canal précis ?", "options": ["Le brouillage ciblé (ou sélectif)", "Le brouillage de barrage large", "Le saut de fréquence"], "rep": "Le brouillage ciblé (ou sélectif)"},
        {"id": "t_br_8", "q": "Quelle technique consiste à émettre un bruit blanc sur un très large spectre de fréquences simultanément ?", "options": ["Le brouillage de barrage", "Le chiffrement WPA3", "L'appairage BLE"], "rep": "Le brouillage de barrage"},
        {"id": "t_br_9", "q": "Outre les communications, quel système de positionnement par satellites peut être neutralisé par un brouilleur ?", "options": ["Le GPS", "La fibre optique", "Le télégraphe de Chappe"], "rep": "Le GPS"},
        {"id": "t_br_10", "q": "Quel phénomène naturel similaire à un brouillage peut perturber les satellites lors de fortes activités solaires ?", "options": ["Les tempêtes magnétiques solaires", "La foudre de plaine", "Les courants de Foucault"], "rep": "Les tempêtes magnétiques solaires"}
    ]

    if "ordre_quiz_tab10_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_br)
        st.session_state.ordre_quiz_tab10_telecom_aleatoire = questions_sources_br

    st.session_state.champs_telecom10_clean = [
        ("1. Un brouilleur neutralise les récepteurs en émettant un .......... radio parasite.", ["Choisir...", "bruit", "courant"], "bruit", "telecom10_t1"),
        ("2. Cette agression hertzienne vise à saturer une .......... de fréquence précise.", ["Choisir...", "bande", "antenne"], "bande", "telecom10_t2"),
        ("3. La qualité de liaison s'effondre lorsque le rapport signal sur .......... (SNR) devient trop bas.", ["Choisir...", "bruit", "vide"], "bruit", "telecom10_t3"),
        ("4. Incapable d'isoler les bits utiles au milieu des parasites, l'appareil subit une ..........", ["Choisir...", "déconnexion", "accélération"], "déconnexion", "telecom10_t4"),
        ("5. Bloquer simultanément le GSM, le Wi-Fi et le GPS nécessite un brouillage de ..........", ["Choisir...", "barrage", "canal"], "barrage", "telecom10_t5"),
        ("6. Pour un particulier, l'usage de ces équipements est strictement .......... par la loi.", ["Choisir...", "interdit", "recommandé"], "interdit", "telecom10_t6"),
        ("7. L'administration .......... utilise légalement ces systèmes pour bloquer les téléphones clandestins.", ["Choisir...", "pénitentiaire", "scolaire"], "pénitentiaire", "telecom10_t7"),
        ("8. Le saut de fréquence (FHSS) historique permettait justement de .......... le brouillage.", ["Choisir...", "contourner", "amplifier"], "contourner", "telecom10_t8"),
        ("9. Une perturbation hertzienne naturelle peut être provoquée par un orage ..........", ["Choisir...", "magnétique", "acoustique"], "magnétique", "telecom10_t9"),
        ("10. Ce type d'équipement réalise une application de contre-mesure ..........", ["Choisir...", "électronique", "optique"], "électronique", "telecom10_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab10_telecom_aleatoire" in st.session_state:
            if "inc_local_tel10" not in st.session_state: st.session_state.inc_local_tel10 = 0
            st.session_state.inc_local_tel10 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab10_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel10_{q_data['id']}_inst_{st.session_state.inc_local_tel10}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 10 (Texte à trous - 10 pts)")
        if "champs_telecom10_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel10", 1)
            for idx, ligne in enumerate(st.session_state.champs_telecom10_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel10_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_infrarouge(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 9 sur deux colonnes étanches."""
    import random

    questions_sources_ir = [
        {"id": "t_ir_1", "q": "Quel astronome et physicien a découvert les rayons infrarouges en l'an 1800 ?", "options": ["William Herschel", "Heinrich Hertz", "Guglielmo Marconi"], "rep": "William Herschel"},
        {"id": "t_ir_2", "q": "Quelle est la nature physique du rayonnement infrarouge utilisé dans les télécommunications ?", "options": ["Une onde lumineuse invisible dont la longueur d'onde est plus longue que le rouge", "Une onde radio hyperfréquence", "Un flux d'électrons circulant dans un fil"], "rep": "Une onde lumineuse invisible dont la longueur d'onde est plus longue que le rouge"},
        {"id": "t_ir_3", "q": "Quelle est la contrainte la plus sévère d'une liaison infrarouge domestique (ex: télécommande) ?", "options": ["Elle exige une ligne de visée directe et ne traverse aucun obstacle opaque", "Elle provoque des interférences avec les box Wi-Fi", "Elle ne fonctionne qu'à plus de 50 mètres"], "rep": "Elle exige une ligne de visée directe et ne traverse aucun obstacle opaque"},
        {"id": "t_ir_4", "q": "Quel composant d'émission standard équipe l'extrémité d'une télécommande de télévision ?", "options": ["Une diode LED infrarouge", "Une antenne-relais miniature", "Un microphone à pastille de carbone"], "rep": "Une diode LED infrarouge"},
        {"id": "t_ir_5", "q": "Quel composant de réception capte et décode les flashs lumineux de la télécommande sur le téléviseur ?", "options": ["Une photodiode (ou phototranscepteur)", "Un haut-parleur électromagnétique", "Un miroir parabolique"], "rep": "Une photodiode (ou phototranscepteur)"},
        {"id": "t_ir_6", "q": "Comment la télécommande transmet-elle un ordre spécifique (ex: changer de chaîne) ?", "options": ["En émettant une série rapide de flashs lumineux codés en binaire (0 et 1)", "En faisant varier la couleur de la lumière", "En augmentant la chaleur du faisceau"], "rep": "En émettant une série rapide de flashs lumineux codés en binaire (0 et 1)"},
        {"id": "t_ir_7", "q": "Quel type d'ondes du spectre électromagnétique se situe juste en dessous de l'infrarouge en termes de fréquence ?", "options": ["Les micro-ondes / ondes radio", "Les rayons X", "Les ultraviolets"], "rep": "Les micro-ondes / ondes radio"},
        {"id": "t_ir_8", "q": "Quel capteur du quotidien utilise le rayonnement infrarouge passif pour détecter la chaleur des corps ?", "options": ["Le détecteur de mouvement des systèmes d'alarme", "Le manomètre de pression", "La carte SIM"], "rep": "Le détecteur de mouvement des systèmes d'alarme"},
        {"id": "t_ir_9", "q": "Pourquoi l'infrarouge a-t-il été abandonné pour le transfert de fichiers entre téléphones portables ?", "options": ["Parce que le Bluetooth offre des débits plus élevés et n'impose pas de coller les téléphones face à face", "Parce que l'infrarouge est devenu payant", "Parce que le fil de cuivre est plus rapide"], "rep": "Parce que le Bluetooth offre des débits plus élevés et n'impose pas de coller les téléphones face à face"},
        {"id": "t_ir_10", "q": "Quel phénomène thermique est intrinsèquement lié au rayonnement infrarouge ?", "options": ["L'émission de chaleur (rayonnement thermique)", "La condensation de l'eau", "La création d'un champ magnétique"], "rep": "L'émission de chaleur (rayonnement thermique)"}
    ]

    if "ordre_quiz_tab9_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_ir)
        st.session_state.ordre_quiz_tab9_telecom_aleatoire = questions_sources_ir

    st.session_state.champs_telecom9_clean = [
        ("1. Les rayons infrarouges furent mis en évidence par le scientifique William ..........", ["Choisir...", "Herschel", "Tyndall"], "Herschel", "telecom9_t1"),
        ("2. Ce signal n'est pas une onde radio mais un rayonnement .......... invisible.", ["Choisir...", "lumineux", "acoustique"], "lumineux", "telecom9_t2"),
        ("3. Les ondes infrarouges transportent naturellement l'énergie sous forme de ..........", ["Choisir...", "chaleur", "courant"], "chaleur", "telecom9_t3"),
        ("4. Une télécommande transmet ses ordres via une diode de type ..........", ["Choisir...", "LED", "triode"], "LED", "telecom9_t4"),
        ("5. À l'arrivée, le signal optique est intercepté par une .......... réceptrice.", ["Choisir...", "photodiode", "antenne"], "photodiode", "telecom9_t5"),
        ("6. Coder l'information s'appuie sur la succession de .......... lumineux rapides.", ["Choisir...", "flashs", "sauts"], "flashs", "telecom9_t6"),
        ("7. Ce mode de couplage exige une ligne de visée .......... entre les boîtiers.", ["Choisir...", "directe", "ondulée"], "directe", "telecom9_t7"),
        ("8. Le faisceau photonique est instantanément .......... par le moindre corps opaque.", ["Choisir...", "bloqué", "amplifié"], "bloqué", "telecom9_t8"),
        ("9. L'infrarouge équipe l'immense majorité des .......... de nos salons.", ["Choisir...", "télécommandes", "routeurs"], "télécommandes", "telecom9_t9"),
        ("10. Pour l'échange de fichiers mobiles, cette liaison fut supplantée par le ..........", ["Choisir...", "Bluetooth", "Télégraphe"], "Bluetooth", "telecom9_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab9_telecom_aleatoire" in st.session_state:
            if "inc_local_tel9" not in st.session_state: st.session_state.inc_local_tel9 = 0
            st.session_state.inc_local_tel9 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab9_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel9_{q_data['id']}_inst_{st.session_state.inc_local_tel9}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 9 (Texte à trous - 10 pts)")
        if "champs_telecom9_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel9", 1)
            for idx, ligne in enumerate(st.session_state.champs_telecom9_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel9_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_bluetooth(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 8 sur deux colonnes étanches."""
    import random

    questions_sources_bt = [
        {"id": "t_blue_1", "q": "D'où provient historiquement le nom commercial et le logo du Bluetooth ?", "options": ["D'un roi viking nommé Harald à la dent bleue", "D'une marque de chewing-gum", "Du nom du chien de l'inventeur"], "rep": "D'un roi viking nommé Harald à la dent bleue"},
        {"id": "t_blue_2", "q": "Quel consortium industriel gère et valide le développement des normes Bluetooth ?", "options": ["Le Bluetooth SIG (Special Interest Group)", "L'IEEE international", "L'alliance GSM"], "rep": "Le Bluetooth SIG (Special Interest Group)"},
        {"id": "t_blue_3", "q": "Quelle est la bande de fréquence industrielle mondiale utilisée par la technologie Bluetooth ?", "options": ["2,4 GHz (bande ISM)", "5 GHz", "88 MHz"], "rep": "2,4 GHz (bande ISM)"},
        {"id": "t_blue_4", "q": "Quelle est la portée théorique maximale d'une connexion Bluetooth de Classe 2 standard ?", "options": ["Environ 10 mètres", "Plus de 5 kilomètres", "Moins de 30 centimètres"], "rep": "Environ 10 mètres"},
        {"id": "t_blue_5", "q": "Comment appelle-t-on la phase initiale obligatoire de liaison et d'authentification entre deux appareils ?", "options": ["L'appairage (ou pairing)", "Le handover cellulaire", "La réfraction totale"], "rep": "L'appairage (ou pairing)"},
        {"id": "t_blue_6", "q": "Quelle évolution du Bluetooth (à partir de la v4.0) permet de connecter des capteurs médicaux ou des montres en consommant très peu d'énergie ?", "options": ["Le Bluetooth Low Energy (BLE)", "Le Bluetooth AM", "Le mode Multiplexé synchrone"], "rep": "Le Bluetooth Low Energy (BLE)"},
        {"id": "t_blue_7", "q": "Quel indicateur de puissance en dBm permet de mesurer la qualité de réception du signal reçu ?", "options": ["Le RSSI", "Le SSID", "L'adresse IP"], "rep": "Le RSSI"},
        {"id": "t_blue_8", "q": "Comment appelle-t-on le mini-réseau sans fil formé instantanément par un maître et ses esclaves ?", "options": ["Un piconet", "Une constellation", "Une cellule hexagonale"], "rep": "Un piconet"},
        {"id": "t_blue_9", "q": "Quelle technique de sécurité permet d'éviter les interférences en changeant de fréquence 1600 fois par seconde ?", "options": ["L'étalement de spectre par saut de fréquence (FHSS)", "La modulation d'amplitude fixe", "Le codage binaire direct"], "rep": "L'étalement de spectre par saut de fréquence (FHSS)"},
        {"id": "t_blue_10", "q": "Quel profil Bluetooth standardisé assure le transfert des flux audio de haute qualité vers un casque ?", "options": ["Le profil A2DP", "Le profil FTP", "Le profil RJ45"], "rep": "Le profil A2DP"}
    ]

    if "ordre_quiz_tab8_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_bt)
        st.session_state.ordre_quiz_tab8_telecom_aleatoire = questions_sources_bt

    st.session_state.champs_telecom8_clean = [
        ("1. Le nom Bluetooth rend hommage au roi viking Harald aux dents ..........", ["Choisir...", "bleues", "vertes"], "bleues", "telecom8_t1"),
        ("2. La normalisation et l'évolution de la technologie dépendent du groupement ..........", ["Choisir...", "SIG", "MIMO"], "SIG", "telecom8_t2"),
        ("3. Le signal s'appuie sur des micro-ondes libres d'usage sur la bande des .......... GHz.", ["Choisir...", "2,4", "5"], "2,4", "telecom8_t3"),
        ("4. Relier deux équipements nécessite d'abord de réaliser leur ..........", ["Choisir...", "appairage", "handover"], "appairage", "telecom8_t4"),
        ("5. La puissance instantanée du lien radio se mesure à l'aide de l'indicateur ..........", ["Choisir...", "RSSI", "SSID"], "RSSI", "telecom8_t5"),
        ("6. Pour les montres connectées, le protocole basse consommation se nomme le ..........", ["Choisir...", "BLE", "WPA3"], "BLE", "telecom8_t6"),
        ("7. Le réseau local restreint créé entre un maître et ses périphériques est un ..........", ["Choisir...", "piconet", "cœur"], "piconet", "telecom8_t7"),
        ("8. Le saut de fréquence permanent s'appelle la technique de transmission ..........", ["Choisir...", "FHSS", "CAN"], "FHSS", "telecom8_t8"),
        ("9. Transmettre la musique en stéréo vers des écouteurs s'appuie sur le profil ..........", ["Choisir...", "A2DP", "SIM"], "A2DP", "telecom8_t9"),
        ("10. Cette technologie sans fil cible des applications de très courte ..........", ["Choisir...", "portée", "vitesse"], "portée", "telecom8_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab8_telecom_aleatoire" in st.session_state:
            if "inc_local_tel8" not in st.session_state: st.session_state.inc_local_tel8 = 0
            st.session_state.inc_local_tel8 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab8_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel8_{q_data['id']}_inst_{st.session_state.inc_local_tel8}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 8 (Texte à trous - 10 pts)")
        if "champs_telecom8_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel8", 1)
            for idx, ligne in enumerate(st.session_state.champs_telecom8_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel8_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_wifi(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 7 sur deux colonnes étanches."""
    import random

    questions_sources_wf = [
        {"id": "t_wifi_1", "q": "Quelle célèbre actrice et inventrice a co-breveté le principe du saut de fréquence, base du Wi-Fi moderne ?", "options": ["Hedy Lamarr", "Marie Curie", "Ada Lovelace"], "rep": "Hedy Lamarr"},
        {"id": "t_wifi_2", "q": "Que signifie littéralement l'acronyme commercial Wi-Fi ?", "options": ["Wireless Fidelity", "Wave Frequency Interconnection", "Wired Filter Induction"], "rep": "Wireless Fidelity"},
        {"id": "t_wifi_3", "q": "Quelles sont les deux bandes de fréquences principales utilisées par les normes Wi-Fi standards (ex: 802.11) ?", "options": ["2,4 GHz et 5 GHz", "87 MHz et 108 MHz", "900 MHz et 1800 MHz"], "rep": "2,4 GHz et 5 GHz"},
        {"id": "t_wifi_4", "q": "Quel est l'impact physique d'un mur en béton armé sur le signal Wi-Fi d'une habitation ?", "options": ["Il atténue fortement le signal en absorbant l'énergie des ondes", "Il amplifie la portée du signal", "Il transforme les ondes en lumière visible"], "rep": "Il atténue fortement le signal en absorbant l'énergie des ondes"},
        {"id": "t_wifi_5", "q": "Quelle est l'unité normalisée utilisée pour exprimer le débit binaire brut d'une connexion Wi-Fi ?", "options": ["Le Mégabit par seconde (Mbps)", "Le Hertz (Hz)", "Le Mètre (m)"], "rep": "Le Mégabit par seconde (Mbps)"},
        {"id": "t_wifi_6", "q": "Comment appelle-t-on l'identifiant textuel public unique (nom du réseau) diffusé par une borne Wi-Fi ?", "options": ["Le SSID", "L'adresse IP", "Le code PIN"], "rep": "Le SSID"},
        {"id": "t_wifi_7", "q": "Quel protocole de chiffrement actuel assure la sécurité de la clé de sécurité Wi-Fi (génération 3) ?", "options": ["WPA3", "WEP historique", "GSM"],"rep": "WPA3"},
        {"id": "t_skip_8", "q": "Quelle technologie multi-antennes (MIMO) permet à une box Wi-Fi de communiquer avec plusieurs appareils en même temps ?", "options": ["Multiple-Input Multiple-Output", "Modulation Inter-Modulaire Optimisée", "Monocanal Indépendant Multi-Ondes"], "rep": "Multiple-Input Multiple-Output"},
        {"id": "t_wifi_9", "q": "Par rapport à une bande de 2,4 GHz, quel est le comportement de la bande de 5 GHz ?", "options": ["Elle offre un débit plus élevé mais possède une portée plus faible et traverse moins bien les murs", "Elle traverse mieux les murs épais", "Elle consomme dix fois moins d'énergie"], "rep": "Elle offre un débit plus élevé mais possède une portée plus faible et traverse moins bien les murs"},
        {"id": "t_wifi_10", "q": "Quel appareil réseau central gère la diffusion du Wi-Fi et l'aiguillage des paquets de la maison vers la fibre ?", "options": ["Le routeur (ou Box Internet)", "Le commutateur Strowger", "Le transpondeur"], "rep": "Le routeur (ou Box Internet)"}
    ]

    if "ordre_quiz_tab7_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_wf)
        st.session_state.ordre_quiz_tab7_telecom_aleatoire = questions_sources_wf

    st.session_state.champs_telecom7_clean = [
        ("1. Le principe du saut de fréquence fut co-inventé par la star hollywoodienne Hedy ..........", ["Choisir...", "Lamarr", "Kao"], "Lamarr", "telecom7_t1"),
        ("2. L'acronyme grand public Wi-Fi désigne la fidélité sans ..........", ["Choisir...", "fil", "limite"], "fil", "telecom7_t2"),
        ("3. Les normes de transmission associées dépendent du comité international ..........", ["Choisir...", "802.11", "GSM"], "802.11", "telecom7_t3"),
        ("4. Une borne Wi-Fi émet des ondes de hautes fréquences mesurées en ..........", ["Choisir...", "Gigahertz", "Mégahertz"], "Gigahertz", "telecom7_t4"),
        ("5. Le nom textuel du réseau visible affiché sur l'écran est le ..........", ["Choisir...", "SSID", "IP"], "SSID", "telecom7_t5"),
        ("6. Traverser des cloisons lourdes en briques provoque une .......... du signal hertzien.", ["Choisir...", "atténuation", "amplification"], "atténuation", "telecom7_t6"),
        ("7. La bande de 5 GHz offre un meilleur .......... de données que la bande 2,4 GHz.", ["Choisir...", "débit", "filtrage"], "débit", "telecom7_t7"),
        ("8. Protéger la clé d'accès domestique contre le piratage s'appuie sur le protocole ..........", ["Choisir...", "WPA3", "WEP"], "WPA3", "telecom7_t8"),
        ("9. Exploiter plusieurs antennes simultanément pour doper le signal réalise le ..........", ["Choisir...", "MIMO", "CAN"], "MIMO", "telecom7_t9"),
        ("10. La vitesse de transfert brute instantanée s'exprime en .......... par seconde (Mbps).", ["Choisir...", "Mégabits", "Mètres"], "Mégabits", "telecom7_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab7_telecom_aleatoire" in st.session_state:
            if "inc_local_tel7" not in st.session_state: st.session_state.inc_local_tel7 = 0
            st.session_state.inc_local_tel7 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel7_{q_data['id']}_inst_{st.session_state.inc_local_tel7}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 pts)")
        if "champs_telecom7_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel7", 1)
            
            for idx, ligne in enumerate(st.session_state.champs_telecom7_clean, 1):
                # Correction de l'indexation pour nettoyer l'affichage des phrases
                enonce = ligne[0]  # Extrait uniquement la phrase de cours épurée
                choix = ligne[1]   # Extrait uniquement la liste des mots sélectionnables
                cle = ligne[-1]    # Extrait la clé technique de session
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel:
                    # Clé dynamique unique pour éviter les collisions de selectbox
                    cle_dynamique_trou = f"trous_tel7_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_satellite(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 6 sur deux colonnes étanches."""
    import random

    questions_sources_sat = [
        {"id": "t_sat_1", "q": "Quel fut le tout premier satellite artificiel de télécommunication envoyé en orbite par l'Homme en 1957 ?", "options": ["Spoutnik 1", "Telstar 1", "Hubble"], "rep": "Spoutnik 1"},
        {"id": "t_sat_2", "q": "À quelle altitude approximative se situent les satellites de télécommunication géostationnaires (orbite GEO) ?", "options": ["36 000 km", "400 km", "2 000 km"], "rep": "36 000 km"},
        {"id": "t_sat_3", "q": "Quelle est la particularité d'un satellite placé sur une orbite géostationnaire ?", "options": ["Il reste immobile par rapport à un point fixe de la surface terrestre", "Il tourne deux fois plus vite que la Terre", "Il change d'orbite toutes les heures"], "rep": "Il reste immobile par rapport à un point fixe de la surface terrestre"},
        {"id": "t_sat_4", "q": "Quel type d'ondes physiques permet de traverser l'atmosphère terrestre pour atteindre l'espace ?", "options": ["Les micro-ondes hyperfréquences", "Les ondes sonores ultrasoniques", "Les signaux infrarouges de courte portée"], "rep": "Les micro-ondes hyperfréquences"},
        {"id": "t_sat_5", "q": "Comment appelle-t-on le composant interne du satellite qui capte le signal de la Terre, l'amplifie et change sa fréquence avant de le renvoyer ?", "options": ["Le répéteur (ou transpondeur)", "L'accumulateur", "L'antenne fouet"], "rep": "Le répéteur (ou transpondeur)"},
        {"id": "t_sat_6", "q": "Quelle forme géométrique parabolique possède l'antenne au sol pour focaliser le signal vers le satellite ?", "options": ["Une parabole (assiette)", "Une tige rectiligne", "Une boucle carrée"], "rep": "Une parabole (assiette)"},
        {"id": "t_sat_7", "q": "Quel est l'inconvénient d'une liaison par satellite géostationnaire par rapport à la fibre optique pour les jeux en ligne ?", "options": ["Un temps de latence (ping) plus élevé dû à l'immense distance à parcourir", "Un débit strictement limité à 10 kbit/s", "Une coupure automatique dès qu'il pleut"], "rep": "Un temps de latence (ping) plus élevé dû à l'immense distance à parcourir"},
        {"id": "t_sat_8", "q": "Quelle constellation de satellites en orbite basse (LEO) offre aujourd'hui un accès Internet mondial à faible latence ?", "options": ["Starlink", "GPS", "Galileo"], "rep": "Starlink"},
        {"id": "t_sat_9", "q": "Comment les satellites reçoivent-ils leur énergie électrique de façon autonome dans le vide spatial ?", "options": ["Grâce à de grands panneaux solaires photovoltaïques", "Par un câble relié au sol", "En brûlant du charbon interne"], "rep": "Grâce à de grands panneaux solaires photovoltaïques"},
        {"id": "t_sat_10", "q": "Quelle est la fonction principale des propulseurs de maintien à poste sur un satellite ?", "options": ["Corriger les dérives de trajectoire causées par les attractions de la Lune et du Soleil", "Augmenter la vitesse pour atteindre Mars", "Faire tourner les panneaux solaires"], "rep": "Corriger les dérives de trajectoire causées par les attractions de la Lune et du Soleil"}
    ]

    if "ordre_quiz_tab6_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_sat)
        st.session_state.ordre_quiz_tab6_telecom_aleatoire = questions_sources_sat

    st.session_state.champs_telecom6_clean = [
        ("1. Le lancement du premier satellite artificiel Spoutnik marqua le début de l'ère ..........", ["Choisir...", "spatiale", "filaire"], "spatiale", "telecom6_t1"),
        ("2. Les télécommunications mondiales utilisent l'orbite fixe appelée ..........", ["Choisir...", "géostationnaire", "polaire"], "géostationnaire", "telecom6_t2"),
        ("3. Pour tourner à la même vitesse que la Terre, l'altitude requise est de 36 000 ..........", ["Choisir...", "kilomètres", "mètres"], "kilomètres", "telecom6_t3"),
        ("4. Vu du sol, un appareil géostationnaire semble parfaitement .......... en l'air.", ["Choisir...", "immobile", "filant"], "immobile", "telecom6_t4"),
        ("5. Le composant spatial qui amplifie et réémet le signal reçu est le ..........", ["Choisir...", "répéteur", "modulateur"], "répéteur", "telecom6_t5"),
        ("6. La liaison montante et la liaison descendante exploitent des ondes ..........", ["Choisir...", "hyperfréquences", "sonores"], "hyperfréquences", "telecom6_t6"),
        ("7. Capter ces signaux faibles depuis la Terre nécessite une antenne ..........", ["Choisir...", "parabolique", "télescopique"], "parabolique", "telecom6_t7"),
        ("8. L'aller-retour du signal vers l'espace crée un temps de .......... mesurable.", ["Choisir...", "latence", "stockage"], "latence", "telecom6_t8"),
        ("9. Déployer des milliers de satellites à basse altitude forme une .......... de communication.", ["Choisir...", "constellation", "cellule"], "constellation", "telecom6_t9"),
        ("10. L'alimentation électrique des circuits embarqués dépend de grands panneaux ..........", ["Choisir...", "solaires", "thermiques"], "solaires", "telecom6_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab6_telecom_aleatoire" in st.session_state:
            if "inc_local_tel6" not in st.session_state: st.session_state.inc_local_tel6 = 0
            st.session_state.inc_local_tel6 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel6_{q_data['id']}_inst_{st.session_state.inc_local_tel6}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 pts)")
        if "champs_telecom6_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel6", 1)
            for idx, ligne in enumerate(st.session_state.champs_telecom6_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel6_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_fibre_optique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 5 sur deux colonnes étanches."""
    import random

    questions_sources_f = [
        {"id": "t_fib_1", "q": "Quel physicien a démontré le guidage de la lumière dans un jet d'eau en 1870, posant les bases de la fibre ?", "options": ["John Tyndall", "Claude Chappe", "Heinrich Hertz"], "rep": "John Tyndall"},
        {"id": "t_fib_2", "q": "Quel physicien sino-américain a reçu le prix Nobel pour avoir purifié le verre et permis des transmissions kilométriques ?", "options": ["Charles Kao", "Samuel Morse", "Martin Cooper"], "rep": "Charles Kao"},
        {"id": "t_fib_3", "q": "Quel phénomène physique fondamental emprisonne la lumière au cœur de la fibre optique ?", "options": ["La réflexion totale interne", "La diffraction de phase", "L'induction électromagnétique"], "rep": "La réflexion totale interne"},
        {"id": "t_fib_4", "q": "Comment appelle-t-on le cylindre central en verre très pur où circule le signal lumineux ?", "options": ["Le cœur", "La gaine", "Le tampon"], "rep": "Le cœur"},
        {"id": "t_fib_5", "q": "Comment appelle-t-on la couche de verre entourant le cœur et possédant un indice de réfraction plus faible ?", "options": ["La gaine optique", "L'armature métallique", "L'isolant en bakélite"], "rep": "La gaine optique"},
        {"id": "t_fib_6", "q": "Quelle est la nature physique du signal qui transporte l'information dans une fibre optique ?", "options": ["Un faisceau lumineux (photons)", "Un courant électrique (électrons)", "Une onde sonore acoustique"], "rep": "Un faisceau lumineux (photons)"},
        {"id": "t_fib_7", "q": "À quelle vitesse approximative la lumière se déplace-t-elle au cœur du verre d'une fibre ?", "options": ["Environ 200 000 km/s", "300 000 km/s", "1 500 m/s"], "rep": "Environ 200 000 km/s"},
        {"id": "t_fib_8", "q": "Quel type de composant d'émission convertit les données binaires électriques en impulsions de lumière ?", "options": ["Une diode laser (ou LED)", "Un microphone à carbone", "Un électroaimant récepteur"], "rep": "Une diode laser (ou LED)"},
        {"id": "t_fib_9", "q": "Quel avantage majeur possède la fibre optique par rapport au câble en cuivre ?", "options": ["Une bande passante immense et une insensibilité totale aux parasites électriques", "Une flexibilité mécanique extensible", "Un coût de fabrication nul"], "rep": "Une bande passante immense et une insensibilité totale aux parasites électriques"},
        {"id": "t_fib_10", "q": "Quel type de fibre optique n'autorise qu'un seul mode de propagation rectiligne pour les longues distances ?", "options": ["La fibre monomode", "La fibre multimode", "La fibre en plastique"], "rep": "La fibre monomode"}
    ]

    if "ordre_quiz_tab5_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_f)
        st.session_state.ordre_quiz_tab5_telecom_aleatoire = questions_sources_f

    st.session_state.champs_telecom5_clean = [
        ("1. Le guidage de la lumière par réflexion fut expérimenté par John ..........", ["Choisir...", "Tyndall", "Bell"], "Tyndall", "telecom5_t1"),
        ("2. Purifier le verre pour réduire l'atténuation fut la découverte de Charles ..........", ["Choisir...", "Kao", "Morse"], "Kao", "telecom5_t2"),
        ("3. Le signal ne s'échappe pas de la fibre grâce à la réflexion totale ..........", ["Choisir...", "interne", "externe"], "interne", "telecom5_t3"),
        ("4. Le composant central conducteur de lumière se nomme le .......... de la fibre.", ["Choisir...", "cœur", "nez"], "cœur", "telecom5_t4"),
        ("5. La couche périphérique protectrice à faible indice est la .......... optique.", ["Choisir...", "gaine", "pastille"], "gaine", "telecom5_t5"),
        ("6. La transmission n'exploite plus les électrons mais les .......... de la lumière.", ["Choisir...", "photons", "ondes"], "photons", "telecom5_t6"),
        ("7. Dans le verre pur, la vitesse de la lumière chute à .......... kilomètres par seconde.", ["Choisir...", "200000", "300000"], "200000", "telecom5_t7"),
        ("8. L'émission du signal lumineux est générée par une diode de type ..........", ["Choisir...", "laser", "triode"], "laser", "telecom5_t8"),
        ("9. Le réseau optique offre l'avantage d'une immunité absolue aux .......... électromagnétiques.", ["Choisir...", "parasites", "vides"], "parasites", "telecom5_t9"),
        ("10. Les liaisons intercontinentales transocéaniques utilisent des câbles ..........", ["Choisir...", "monomodes", "analogiques"], "monomodes", "telecom5_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab5_telecom_aleatoire" in st.session_state:
            if "inc_local_tel5" not in st.session_state: st.session_state.inc_local_tel5 = 0
            st.session_state.inc_local_tel5 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel5_{q_data['id']}_inst_{st.session_state.inc_local_tel5}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 pts)")
        if "champs_telecom5_clean" in st.session_state:
            # Récupération sécurisée du jeton d'instance
            instance_id = st.session_state.get("inc_local_tel5", 1)
            
            for idx, ligne in enumerate(st.session_state.champs_telecom5_clean, 1):
                # Correction de l'indexation pour isoler proprement les chaînes textuelles
                enonce = ligne[0]  # Extrait uniquement la phrase de cours épurée
                choix = ligne[1]   # Extrait uniquement la liste des mots sélectionnables
                cle = ligne[-1]    # Extrait la clé technique de session
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel:
                    # Clé dynamique unique pour éviter les collisions de selectbox
                    cle_dynamique_trou = f"trous_tel5_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_smartphone(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 4 sur deux colonnes étanches."""
    import random

    questions_sources_s = [
        {"id": "t_smart_1", "q": "Qui a passé le tout premier appel depuis un téléphone portable combiné en 1973 ?", "options": ["Martin Cooper", "Alexander Bell", "Steve Jobs"], "rep": "Martin Cooper"},
        {"id": "t_smart_2", "q": "Pourquoi le réseau de téléphonie mobile est-il qualifié de réseau 'cellulaire' ?", "options": ["Car le territoire est découpé en zones géographiques hexagonales appelées cellules", "Parce qu'il fonctionne avec des piles biologiques", "Car les téléphones ressemblent à des cellules de prison"], "rep": "Car le territoire est découpé en zones géographiques hexagonales appelées cellules"},
        {"id": "t_smart_3", "q": "Quelle pièce métallique surélevée assure la liaison radio constante avec les téléphones portables de sa cellule ?", "options": ["L'antenne-relais (station de base)", "Le répartiteur en cuivre", "Le commutateur Strowger"], "rep": "L'antenne-relais (station de base)"},
        {"id": "t_smart_4", "q": "Quel type d'ondes physiques transporte la voix et les données entre un smartphone et l'antenne ?", "options": ["Les ondes radio hyperfréquences (micro-ondes)", "Les ondes sonores ultrasoniques", "Les faisceaux laser infrarouges"], "rep": "Les ondes radio hyperfréquences (micro-ondes)"},
        {"id": "t_smart_5", "q": "Quel petit circuit à puce amovible inséré dans le téléphone stocke l'identité de l'abonné au réseau ?", "options": ["La carte SIM", "La carte SD", "Le microprocesseur principal"], "rep": "La carte SIM"},
        {"id": "t_smart_6", "q": "Comment appelle-t-on le transfert transparent d'une communication d'une antenne à une autre quand l'utilisateur se déplace ?", "options": ["Le handover (ou transfert intercellulaire)", "Le multiplexage optique", "La cavitation de fréquence"], "rep": "Le handover (ou transfert intercellulaire)"},
        {"id": "t_smart_7", "q": "Quelle génération de réseau mobile a introduit pour la toute première fois l'accès à Internet haut débit sur smartphone ?", "options": ["La 3G", "La 1G (analogique)", "La 2G (GSM)"], "rep": "La 3G"},
        {"id": "t_smart_8", "q": "Quel composant interne d'un smartphone convertit le signal analogique de la voix en données binaires ?", "options": ["Le convertisseur analogique-numérique (CAN)", "Le haut-parleur", "La dalle tactile"], "rep": "Le convertisseur analogique-numérique (CAN)"},
        {"id": "t_smart_9", "q": "Que signifie l'acronyme GSM, norme numérique historique de la 2G ?", "options": ["Global System for Mobile communications", "Générateur de Signaux Modulés", "Grille de Sécurité Multi-antennes"], "rep": "Global System for Mobile communications"},
        {"id": "t_smart_10", "q": "Quelle est la fonction principale du processeur d'applications dans un smartphone moderne ?", "options": ["Exécuter le système d'exploitation et les applications logicielles", "Capter directement le signal radio aérien", "Stocker l'énergie électrique"], "rep": "Exécuter le système d'exploitation et les applications logicielles"}
    ]

    if "ordre_quiz_tab4_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_s)
        st.session_state.ordre_quiz_tab4_telecom_aleatoire = questions_sources_s

    st.session_state.champs_telecom4_clean = [
        ("1. Le pionnier de la téléphonie mobile à New York fut l'ingénieur Martin ..........", ["Choisir...", "Cooper", "Marconi"], "Cooper", "telecom4_t1"),
        ("2. Pour optimiser les fréquences, le territoire est découpé en .......... hexagonales.", ["Choisir...", "cellules", "bandes"], "cellules", "telecom4_t2"),
        ("3. Chaque zone est couverte par une station de base équipée d'une ..........", ["Choisir...", "antenne-relais", "magnéto"], "antenne-relais", "telecom4_t3"),
        ("4. Les liaisons aériennes exploitent des ondes radio de type ..........", ["Choisir...", "hyperfréquences", "sonores"], "hyperfréquences", "hyperfréquences"),
        ("5. L'accès sécurisé et le numéro de l'abonné dépendent de sa carte ..........", ["Choisir...", "SIM", "SD"], "SIM", "telecom4_t5"),
        ("6. Changer d'antenne en roulant sans couper l'appel s'appelle le ..........", ["Choisir...", "handover", "clapet"], "handover", "telecom4_t6"),
        ("7. La transition historique de la 1G à la 2G a marqué le passage à la technologie ..........", ["Choisir...", "numérique", "analogique"], "numérique", "telecom4_t7"),
        ("8. Envoyer une photo ou une vidéo s'appuie sur le transfert de données ..........", ["Choisir...", "binaires", "mécaniques"], "binaires", "telecom4_t8"),
        ("9. Le smartphone moderne réunit un téléphone et un véritable .......... de poche.", ["Choisir...", "ordinateur", "oscillateur"], "ordinateur", "telecom4_t9"),
        ("10. Ce réseau sans fil offre une liberté totale s'affranchissant des liaisons ..........", ["Choisir...", "filaires", "satellitaires"], "filaires", "telecom4_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab4_telecom_aleatoire" in st.session_state:
            if "inc_local_tel4" not in st.session_state: st.session_state.inc_local_tel4 = 0
            st.session_state.inc_local_tel4 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel4_{q_data['id']}_inst_{st.session_state.inc_local_tel4}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 pts)")
        if "champs_telecom4_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel4", 1)
            for idx, ligne in enumerate(st.session_state.champs_telecom4_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel4_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_telephone_maison(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 3 sur deux colonnes étanches."""
    import random

    questions_sources_t = [
        {"id": "t_tel_1", "q": "Qui a déposé le brevet officiel du téléphone électrique en 1876 ?", "options": ["Alexander Graham Bell", "Thomas Edison", "Nikola Tesla"], "rep": "Alexander Graham Bell"},
        {"id": "t_tel_2", "q": "Quel composant du combiné transforme les vibrations de la voix en signal électrique ?", "options": ["Le microphone (pastille de carbone)", "L'écouteur", "La magnéto"], "rep": "Le microphone (pastille de carbone)"},
        {"id": "t_tel_3", "q": "Comment appelait-on les opératrices chargées de relier manuellement les lignes au début du téléphone ?", "options": ["Les demoiselles du téléphone", "Les télégraphistes", "Les standardistes hertziennes"], "rep": "Les demoiselles du téléphone"},
        {"id": "t_tel_4", "q": "Quel type de signal physique circule à l'intérieur des fils de cuivre d'un téléphone fixe ?", "options": ["Un courant électrique analogique", "Une onde radio libre", "Un faisceau lumineux"], "rep": "Un courant électrique analogique"},
        {"id": "t_tel_5", "q": "Quelle pièce historique du téléphone permettait de composer manuellement le numéro de son correspondant ?", "options": ["Le cadran rotatif", "Le clavier à touches tactiles", "Le manipulateur à levier"], "rep": "Le cadran rotatif"},
        {"id": "t_tel_6", "q": "Quel système automatique a remplacé les opératrices manuelles grâce à Almon Strowger ?", "options": ["Le commutateur automatique", "Le multiplexeur optique", "Le relais hertzien"], "rep": "Le commutateur automatique"},
        {"id": "t_tel_7", "q": "Quelle pièce du combiné reconvertit le courant électrique analogique en ondes sonores audibles ?", "options": ["L'écouteur (haut-parleur)", "Le microphone", "Le condensateur"], "rep": "L'écouteur (haut-parleur)"},
        {"id": "t_tel_8", "q": "Comment le téléphone de type Marty générait-il le courant d'appel électrique ?", "options": ["En tournant une manivelle (magnéto)", "Grâce à une batterie interne rechargeable", "Par liaison solaire"], "rep": "En tournant une manivelle (magnéto)"},
        {"id": "t_tel_9", "q": "Quel matériau composait la coque noire des célèbres téléphones rétro des années 1930 à 1950 (ex: Socotel) ?", "options": ["La bakélite", "Le plastique PVC", "L'aluminium anodisé"], "rep": "La bakélite"},
        {"id": "t_tel_10", "q": "Quel composant électrique a permis d'amplifier les signaux longue distance au début du XXe siècle ?", "options": ["La lampe triode (tube à vide)", "Le microprocesseur", "Le connecteur RJ11"], "rep": "La lampe triode (tube à vide)"}
    ]

    if "ordre_quiz_tab3_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_t)
        st.session_state.ordre_quiz_tab3_telecom_aleatoire = questions_sources_t

    st.session_state.champs_telecom3_clean = [
        ("1. Le brevet historique du téléphone électrique fut déposé par Alexander Graham ..........", ["Choisir...", "Bell", "Edison"], "Bell", "telecom3_t1"),
        ("2. Parler dans le microphone fait varier la résistance d'une pastille de ..........", ["Choisir...", "carbone", "cuivre"], "carbone", "telecom3_t2"),
        ("3. La voix humaine est ainsi convertie en un courant électrique ..........", ["Choisir...", "analogique", "numérique"], "analogique", "telecom3_t3"),
        ("4. Les liaisons du réseau d'époque reposaient sur des paires de fils de ..........", ["Choisir...", "cuivre", "fer"], "cuivre", "telecom3_t4"),
        ("5. Établir la connexion nécessitait d'abord l'action manuelle des ..........", ["Choisir...", "demoiselles", "machines"], "demoiselles", "telecom3_t5"),
        ("6. Pour appeler le standard, le modèle Marty utilisait une manivelle appelée ..........", ["Choisir...", "magnéto", "manipulateur"], "magnéto", "telecom3_t6"),
        ("7. L'automatisation du réseau s'est faite grâce à l'invention du ..........", ["Choisir...", "commutateur", "filtre"], "commutateur", "telecom3_t7"),
        ("8. Composer le numéro d'un abonné à la maison utilisait un cadran ..........", ["Choisir...", "rotatif", "tactile"], "rotatif", "telecom3_t8"),
        ("9. L'écouteur du combiné s'appuie sur une membrane et un .......... pour recréer le son.", ["Choisir...", "électroaimant", "ressort"], "électroaimant", "telecom3_t9"),
        ("10. Les boîtiers des téléphones vintage étaient moulés en .......... noire rigide.", ["Choisir...", "bakélite", "plexiglas"], "bakélite", "telecom3_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab3_telecom_aleatoire" in st.session_state:
            if "inc_local_tel3" not in st.session_state: st.session_state.inc_local_tel3 = 0
            st.session_state.inc_local_tel3 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel3_{q_data['id']}_inst_{st.session_state.inc_local_tel3}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 pts)")
        if "champs_telecom3_clean" in st.session_state:
            instance_id = st.session_state.get("inc_local_tel3", 1)
            
            for idx, ligne in enumerate(st.session_state.champs_telecom3_clean, 1):
                # Correction de l'indexation pour isoler le texte propre
                enonce = ligne[0]  # Extrait uniquement la phrase de cours
                choix = ligne[1]   # Extrait uniquement les options du menu déroulant
                cle = ligne[-1]    # Extrait la clé technique
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel:
                    cle_dynamique_trou = f"trous_tel3_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_ondes_radio(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 2 sur deux colonnes étanches."""
    import random

    questions_sources_r = [
        {"id": "t_rad_1", "q": "Quel physicien a prouvé expérimentalement l'existence des ondes électromagnétiques en 1887 ?", "options": ["Heinrich Hertz", "James Watt", "Thomas Edison"], "rep": "Heinrich Hertz"},
        {"id": "t_rad_2", "q": "Qui a réalisé les premières transmissions radio à grande distance au tournant du XXe siècle ?", "options": ["Guglielmo Marconi", "Claude Chappe", "Alexander Bell"], "rep": "Guglielmo Marconi"},
        {"id": "t_rad_3", "q": "Quelle est l'unité normalisée internationale utilisée pour mesurer la fréquence d'une onde ?", "options": ["Le Hertz (Hz)", "Le Décibel (dB)", "Le Mètre (m)"], "rep": "Le Hertz (Hz)"},
        {"id": "t_rad_4", "q": "Comment appelle-t-on le sommet maximal d'une oscillation sinusoïdale radio ?", "options": ["L'amplitude", "La période", "La phase"], "rep": "L'amplitude"},
        {"id": "t_rad_5", "q": "Quelle est la vitesse approximative de propagation d'une onde radio dans l'air ?", "options": ["300 000 km/s (vitesse de la lumière)", "340 m/s (vitesse du son)", "1 500 m/s"], "rep": "300 000 km/s (vitesse de la lumière)"},
        {"id": "t_rad_6", "q": "Si on augmente la fréquence d'une onde électromagnétique, qu'advient-il de sa longueur d'onde ?", "options": ["Elle diminue", "Elle augmente", "Elle reste strictement identique"], "rep": "Elle diminue"},
        {"id": "t_rad_7", "q": "Quel organe physique capte les variations du champ électromagnétique pour les transformer en courant électrique ?", "options": ["L'antenne réceptrice", "Le haut-parleur", "Le condensateur"], "rep": "L'antenne réceptrice"},
        {"id": "t_rad_8", "q": "Quel type de modulation fait varier la hauteur du signal pour y injecter de l'information ?", "options": ["La modulation d'amplitude (AM)", "La modulation de fréquence (FM)", "La modulation de phase"], "rep": "La modulation d'amplitude (AM)"},
        {"id": "t_rad_9", "q": "Dans quel milieu une onde radio peut-elle se propager, contrairement à une onde sonore ?", "options": ["Le vide absolu (espace)", "L'eau pure", "Le plomb massif"], "rep": "Le vide absolu (espace)"},
        {"id": "t_rad_10", "q": "Quel composant d'émission génère l'oscillation électrique de haute fréquence ?", "options": ["L'oscillateur", "Le microphone", "La boussole"], "rep": "L'oscillateur"}
    ]

    if "ordre_quiz_tab2_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_r)
        st.session_state.ordre_quiz_tab2_telecom_aleatoire = questions_sources_r

    st.session_state.champs_telecom2_clean = [
        ("1. L'existence théorique des ondes fut démontrée en labo par Heinrich ..........", ["Choisir...", "Hertz", "Marconi"], "Hertz", "telecom2_t1"),
        ("2. Guglielmo Marconi utilisa ces ondes pour créer la télégraphie sans ..........", ["Choisir...", "fil", "courant"], "fil", "telecom2_t2"),
        ("3. Le nombre d'oscillations émises par seconde définit la .......... du signal.", ["Choisir...", "fréquence", "vitesse"], "fréquence", "telecom2_t3"),
        ("4. Cette valeur de répétition temporelle se mesure en ..........", ["Choisir...", "Hertz", "Mètres"], "Hertz", "telecom2_t4"),
        ("5. La hauteur maximale de la crête sinusoïdale représente l'..........", ["Choisir...", "amplitude", "période"], "amplitude", "telecom2_t5"),
        ("6. La distance parcourue par l'onde durant une période est sa .......... d'onde.", ["Choisir...", "longueur", "vitesse"], "longueur", "telecom2_t6"),
        ("7. Les ondes hertziennes se déplacent à la vitesse de la .......... dans le vide.", ["Choisir...", "lumière", "foudre"], "lumière", "telecom2_t7"),
        ("8. Capter l'onde libre nécessite obligatoirement l'usage d'une .......... métallique.", ["Choisir...", "antenne", "bobine"], "antenne", "telecom2_t8"),
        ("9. Faire varier la fréquence pour coder un son correspond à la modulation ..........", ["Choisir...", "FM", "AM"], "FM", "telecom2_t9"),
        ("10. Contrairement au son, le signal hertzien traverse le .......... spatial.", ["Choisir...", "vide", "noyau"], "vide", "telecom2_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab2_telecom_aleatoire" in st.session_state:
            if "inc_local_tel2" not in st.session_state: st.session_state.inc_local_tel2 = 0
            st.session_state.inc_local_tel2 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel2_{q_data['id']}_inst_{st.session_state.inc_local_tel2}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 pts)")
        if "champs_telecom2_clean" in st.session_state:
            # Sécurisation : Utilisation du jeton d'instance pour la colonne de droite
            instance_id = st.session_state.get("inc_local_tel2", 1)
            
            for idx, ligne in enumerate(st.session_state.champs_telecom2_clean, 1):
                # Correction de l'indexation pour nettoyer l'affichage des phrases
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    cle_dynamique_trou = f"trous_tel2_{cle}_inst_{instance_id}_{idx}"
                    st.selectbox("", choix, key=cle_dynamique_trou, disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_historique_telecom(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 1 sur deux colonnes étanches."""
    import random

    questions_sources_h = [
        {"id": "t_hist_1", "q": "Qui est l'inventeur français du télégraphe optique déployé pendant la Révolution française ?", "options": ["Claude Chappe", "Samuel Morse", "Alexander Graham Bell"], "rep": "Claude Chappe"},
        {"id": "t_hist_2", "q": "Quelle était la contrainte majeure du système de sémaphore optique de Chappe ?", "options": ["Il était inutilisable la nuit, par temps de brouillard ou de forte pluie", "Il nécessitait des câbles en cuivre sous terre", "Il propageait des ondes radio nocives"], "rep": "Il était inutilisable la nuit, par temps de brouillard ou de forte pluie"},
        {"id": "t_hist_3", "q": "En quelle année Samuel Morse a-t-il réalisé la première démonstration publique de son télégraphe électrique ?", "options": ["1837", "1792", "1914"], "rep": "1837"},
        {"id": "t_hist_4", "q": "Quel composant physique a permis de s'affranchir de la visibilité directe entre les stations ?", "options": ["Le fil conducteur électrique en cuivre (puis de fer)", "La lentille de télescope à fort grossissement", "La bobine d'induction Tesla"], "rep": "Le fil conducteur électrique en cuivre (puis de fer)"},
        {"id": "t_hist_5", "q": "Comment le télégraphe de Morse transcrit-il les messages à distance ?", "options": ["Par l'émission d'impulsions électriques courtes et longues (points et traits)", "Par la projection d'ombres chinoises sur un écran blanc", "Par la voix convertie en vibrations magnétiques"], "rep": "Par l'émission d'impulsions électriques courtes et longues (points et traits)"},
        {"id": "t_hist_6", "q": "Quelle pièce mécanique le télégraphiste manipule-t-it manuellement pour envoyer le signal ?", "options": ["Le manipulateur (ou clé télégraphique)", "Le sémaphore de toiture", "Le cadran rotatif"], "rep": "Le manipulateur (ou clé télégraphique)"},
        {"id": "t_hist_7", "q": "Quel élément à l'arrivée traduit l'impulsion électrique en un clic mécanique audible ou un tracé d'encre ?", "options": ["L'électroaimant (récepteur)", "La pile Volta", "Le miroir parabolique"], "rep": "L'électroaimant (récepteur)"},
        {"id": "t_hist_8", "q": "Quelle célèbre ligne de télégraphe optique Chappe fut la première inaugurée en 1794 ?", "options": ["Paris - Lille", "Paris - Marseille", "Lyon - Strasbourg"], "rep": "Paris - Lille"},
        {"id": "t_hist_9", "q": "Quelle était approximativement la vitesse de transmission d'un signal d'une tour à l'autre chez Chappe ?", "options": ["Quelques secondes", "Plusieurs heures", "Une journée entière"], "rep": "Quelques secondes"},
        {"id": "t_hist_10", "q": "Quelle invention majeure succèdera directement au télégraphe électrique à la fin du XIXe siècle ?", "options": ["Le téléphone de Bell", "La fibre optique", "Le réseau satellite"], "rep": "Le téléphone de Bell"}
    ]

    if "ordre_quiz_tab1_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_h)
        st.session_state.ordre_quiz_tab1_telecom_aleatoire = questions_sources_h

    st.session_state.champs_telecom1_clean = [
        ("1. Le télégraphe optique a été conçu par l'ingénieur français Claude ..........", ["Choisir...", "Chappe", "Morse"], "Chappe", "telecom1_t1"),
        ("2. Ce mécanisme transmettait des données par la position de bras ..........", ["Choisir...", "articulés", "électriques"], "articulés", "telecom1_t2"),
        ("3. Le système Chappe nécessitait une ligne de visée .......... entre les tours.", ["Choisir...", "directe", "enterrée"], "directe", "telecom1_t3"),
        ("4. Samuel Morse a remplacé les signaux visuels par des impulsions ..........", ["Choisir...", "électriques", "lumineuses"], "électriques", "telecom1_t4"),
        ("5. Le code Morse repose sur l'association de points et de ..........", ["Choisir...", "traits", "lettres"], "traits", "telecom1_t5"),
        ("6. L'opérateur utilise un .......... pour ouvrir et fermer le circuit.", ["Choisir...", "manipulateur", "clapet"], "manipulateur", "telecom1_t6"),
        ("7. À la réception, un .......... attire une armature pour créer le clic audible.", ["Choisir...", "électroaimant", "ressort"], "électroaimant", "telecom1_t7"),
        ("8. La toute première ligne du télégraphe optique reliait Paris à la ville de ..........", ["Choisir...", "Lille", "Lyon"], "Lille", "telecom1_t8"),
        ("9. Le temps de passage du signal visuel entre deux stations Chappe prenait quelques ..........", ["Choisir...", "secondes", "minutes"], "secondes", "telecom1_t9"),
        ("10. À la fin du XIXe siècle, les signaux codés laisseront la place à la voix avec le ..........", ["Choisir...", "téléphone", "satellite"], "téléphone", "telecom1_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab1_telecom_aleatoire" in st.session_state:
            if "inc_local_tel1" not in st.session_state: st.session_state.inc_local_tel1 = 0
            st.session_state.inc_local_tel1 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel1_{q_data['id']}_inst_{st.session_state.inc_local_tel1}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 pts)")
        if "champs_telecom1_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_telecom1_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel: st.selectbox("", choix, key=f"trous_tel1_{cle}_inst_{idx}", disabled=verrouille, label_visibility="collapsed")

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
    st.header("L'Origine des Télécommunications : Les Télégraphes")
    
    # --- DÉCLARATION DES VERROUS ET SÉCURITÉS ---
    if "suite_verrouille_tab1_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab1_telecom = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_telecom

    
    col_t11, col_t12 = st.columns(2)
    with col_t11:
        col_graph11, im_t11 = st.columns(2)
        with col_graph11:
            # --- PERSONNAGE CLÉ 1 : CLAUDE CHAPPE ---
            st.header("Claude Chappe et le Télégraphe Optique (1792)")
            st.write(
                "**Le Personnage :** En pleine Révolution française, l'ingénieur **Claude Chappe** réalise un coup de génie "
                "en créant le tout premier réseau de télécommunication d'envergure nationale [I1]. Face à la menace des invasions étrangères, "
                "la France avait un besoin vital de transmettre les ordres militaires plus vite que les chevaux des messagers.\n\n"
                "**Fonctionnement extrêmement détaillé :** Le système repose sur des **tours de sémaphores** distantes de 10 à 15 km [I1]. "
                "Au sommet de chaque tour est dressé un mât en bois équipé d'un grand bras pivotant horizontal appelé **Régulateur**, "
                "portant à ses extrémités deux petits bras articulés mobiles appelés **Indicateurs**. "
                "En manipulant un ingénieux système de poulies et de cordages depuis l'intérieur de la tour, l'opérateur pouvait configurer "
                "**92 positions géométriques distinctes**. Chaque configuration correspondait à un numéro de page et de ligne d'un dictionnaire secret, "
                "permettant de traduire les formes en mots complets. Les stationnaires des tours voisines observaient les signaux à l'aide de lunettes "
                "astronomiques et recopiaient immédiatement la position pour la transmettre à la tour suivante. C'est le premier réseau à transfert de paquets physiques !"
            )

            # --- SIMULATEUR INTERACTIF DU SÉMAPHORE DE CHAPPE ---
            st.write("**Laboratoire interactif : Positionnement des bras mécaniques Chappe**")
            angle_reg = st.slider("Orienter le bras Régulateur central (degrés) :", min_value=-90, max_value=90, value=0, step=45, key="slide_reg_chappe")
            angle_ind = st.slider("Orienter les Indicateurs d'extrémités (degrés) :", min_value=-90, max_value=90, value=45, step=45, key="slide_ind_chappe")

            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            import numpy as np
            import time

            fig_ch, ax_ch = plt.subplots(figsize=(6, 2.8), facecolor="white")
            ax_ch.set_facecolor("white")
            # Dessin de la tour en pierre
            ax_ch.add_patch(patches.Rectangle((2.2, 0.0), 0.6, 1.0, facecolor="#94a3b8", edgecolor="#475569", linewidth=2))
            ax_ch.plot([2.5, 2.5], [1.0, 1.8], color="black", linewidth=3) # Mât fixe
            
            # Calcul cinématique du bras régulateur central (longueur 1.2)
            rad_reg = np.radians(angle_reg)
            x1 = 2.5 - 0.6 * np.cos(rad_reg)
            y1 = 1.8 - 0.6 * np.sin(rad_reg)
            x2 = 2.5 + 0.6 * np.cos(rad_reg)
            y2 = 1.8 + 0.6 * np.sin(rad_reg)
            ax_ch.plot([x1, x2], [y1, y2], color="#b91c1c", linewidth=5, solid_capstyle="round", zorder=3) # Régulateur
            
            # Petits bras indicateurs aux extrémités (longueur 0.3)
            rad_ind = np.radians(angle_ind + angle_reg)
            ax_ch.plot([x1, x1 - 0.3 * np.sin(rad_ind)], [y1, y1 + 0.3 * np.cos(rad_ind)], color="#1e293b", linewidth=3, zorder=4)
            ax_ch.plot([x2, x2 + 0.3 * np.sin(rad_ind)], [y2, y2 - 0.3 * np.cos(rad_ind)], color="#1e293b", linewidth=3, zorder=4)
            
            ax_ch.set_xlim(1.0, 4.0)
            ax_ch.set_ylim(0.0, 2.6)
            ax_ch.axis("off")
            st.pyplot(fig_ch)
            plt.close(fig_ch)

        with im_t11:

            try:
                st.image("telegraphe_optique.jpg", caption=f"Le Télégraphe Optique (1792)  Claude Chappe", use_container_width=True)
            except Exception:
                st.error("Image d'illustration manquante : telegraphe_optique.jpg")
            try:
                st.image("alphabet_telegraphe_optique.jpg", caption=f"Le Télégraphe Optique (1792)  Claude Chappe", use_container_width=True)
            except Exception:
                st.error("Image d'illustration manquante : alphabet_telegraphe_optique.jpg")

        
    st.divider()

    with col_t12:
        col_graph12, im_t12 = st.columns(2)
        with col_graph12:
            # --- PERSONNAGE CLÉ 2 : SAMUEL MORSE ---
            st.header("Samuel Morse et le Télégraphe Électrique (1837)")
            st.write(
                "**Le Personnage :** L'artiste et inventeur américain **Samuel Morse**, frappé par le drame d'avoir appris la mort de sa femme "
                "plusieurs jours après son enterrement à cause de la lenteur du courrier, consacre sa vie à dompter l'électricité pour créer "
                "une communication instantanée [I2]. En s'associant avec Alfred Vail, il développe le code universel qui porte son nom.\n\n"
                "**Fonctionnement extrêmement détaillé :** Le télégraphe filaire révolutionne l'histoire en s'affranchissant totalement de la météo "
                "et de la visibilité directe. Le circuit comprend trois blocs indissociables :\n"
                "1. **La source d'énergie :** Une pile chimique (type Daniell) fournissant un courant électrique continu de basse tension.\n"
                "2. **L'émetteur (Le Manipulateur) :** Un interrupteur mécanique à levier inversé maintenu ouvert par un ressort. L'opérateur appuie "
                "sur le bouton en bois pour fermer le circuit et laisser passer le courant. Un appui bref génère un **point** (impulsion électrique de 0,1s), "
                "un appui long génère un **trait** (impulsion électrique de 0,3s).\n"
                "3. **Le récepteur (L'Électroaimant) :** À des centaines de kilomètres, le courant traverse une bobine de fil de cuivre enroulée autour "
                "d'un noyau de fer doux. Ce bobinage se transforme instantanément en aimant puissant (effet d'induction électromagnétique) et attire "
                "une palette métallique articulée. Cette palette vient frapper une butée dans un 'clic' sec audible, ou presse une pointe encrée contre "
                "une bande de papier déroulante, transcrivant physiquement l'alphabet Morse."
            )

            # --- SIMULATEUR DU SIGNAL ÉLECTRIQUE MORSE ---
            st.write("**Banc d'essai cinématique : Codage et impulsions de l'alphabet Morse complet (A-Z)**")
            
            # 1. Dictionnaire d'indexation académique officiel du code Morse
            dict_morse_complet = {
                "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", 
                "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..", 
                "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", 
                "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", 
                "Y": "-.--", "Z": "--.."
            }
            
            # Génération de la liste des options pour le menu déroulant
            options_alphabet = [f"Lettre {lettre} (Code : {code})" for lettre, code in dict_morse_complet.items()]
            
            lettre_choisie = st.selectbox(
                "Sélectionner la lettre de l'alphabet à transmettre sur la ligne :",
                options=options_alphabet,
                key="select_lettre_morse_alphabet_complet"
            )
            
            # Extraction de la lettre pure (la 8ème position de la chaîne)
            lettre_pure = lettre_choisie[7]
            code_morse_actif = dict_morse_complet[lettre_pure]

            # Moteur de rendu graphique vectoriel
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches

            fig_mo, ax_mo = plt.subplots(figsize=(7, 2.0), facecolor="white")
            ax_mo.set_facecolor("white")
            
            # Fil conducteur de ligne de cuivre passif (fond gris)
            ax_mo.plot([0.5, 6.5], [1.0, 1.0], color="#cbd5e1", linewidth=2, linestyle="--", zorder=1)
            
            # Composants du réseau (Émetteur Pile / Récepteur Électroaimant)
            ax_mo.add_patch(patches.Rectangle((0.1, 0.8), 0.4, 0.4, facecolor="#334155", edgecolor="black", zorder=2))
            ax_mo.text(0.3, 1.3, "Pile", ha="center", fontsize=8, weight="bold")
            
            ax_mo.add_patch(patches.Rectangle((6.0, 0.7), 0.5, 0.6, facecolor="#475569", edgecolor="black", zorder=2))
            ax_mo.text(6.25, 1.4, "Récepteur", ha="center", fontsize=8, weight="bold")

            # 2. ALGORITHME DE PLACEMENT ET D'ESPACEMENT DES PAQUETS D'ÉLECTRONS
            x_depart_paquet = 1.0
            
            for caractere in code_morse_actif:
                if caractere == ".":
                    # Impulsion électrique courte (Point) : largeur 0.25
                    ax_mo.plot([x_depart_paquet, x_depart_paquet + 0.25], [1.0, 1.0], color="#b91c1c", linewidth=5, solid_capstyle="round", zorder=3)
                    ax_mo.text(x_depart_paquet + 0.125, 0.7, ".", color="#b91c1c", weight="bold", fontsize=15, ha="center")
                    x_depart_paquet += 0.55  # Espace constant après un point
                elif caractere == "-":
                    # Impulsion électrique longue (Trait) : largeur 0.65
                    ax_mo.plot([x_depart_paquet, x_depart_paquet + 0.65], [1.0, 1.0], color="#b91c1c", linewidth=5, solid_capstyle="round", zorder=3)
                    ax_mo.text(x_depart_paquet + 0.325, 0.7, "-", color="#b91c1c", weight="bold", fontsize=15, ha="center")
                    x_depart_paquet += 0.95  # Espace constant après un trait

            # Configuration des axes Matplotlib
            ax_mo.set_xlim(0, 6.6)
            ax_mo.set_ylim(0.2, 1.6)
            ax_mo.axis("off")
            st.pyplot(fig_mo)
            plt.close(fig_mo)
            
            # Message de confirmation dynamique sous l'écran
            st.success(f"Signal physique en ligne : Transmission de la lettre {lettre_pure} encodée en '{code_morse_actif}'.")

        with im_t12:

            try:
                st.image("telegraphe_morse.jpg", caption=f"Le Télégraphe morse (1837)  Samuel Morse", use_container_width=True)
            except Exception:
                st.error("Image d'illustration manquante : telegraphe_morse.jpg")
            try:
                st.image("alphabet_telegraphe_morse.jpg", caption=f"Le Télégraphe morse (1837)  Samuel Morse", use_container_width=True)
            except Exception:
                st.error("Image d'illustration manquante : alphabet_telegraphe_morse.jpg")

        

    # --- CARICATURE / BD HUMORISTIQUE TEXTUELLE ---

    col_graph13, im_t13 = st.columns(2)
    with col_graph13:
        st.write("**La BD humoristique textuelle : Le jour où la météo s'en est mêlée**")
        st.info(
            "**Case 1 (Caricature de Claude Chappe) :** Claude Chappe est debout au sommet de sa tour, sa longue vue "
            "coincée sous le bras, agitant ses cordages avec ferveur : 'Vite ! Envoyons le message secret à Napoléon !'. "
            "Les bras en bois tournent joyeusement : 'Schliiiit !'.\n\n"
            "**Case 2 (Le Drame) :** Un énorme nuage noir et farceur crève juste au-dessus de la colline. "
            "Une pluie torrentielle et un brouillard à couper au couteau enveloppent la station suivante. "
            "Le stationnaire voisin, les yeux collés à sa longue vue pleine d'eau, râle : 'Je ne vois même pas le mât ! "
            "Le message est noyé !'.\n\n"
            "**Case 3 (Caricature de Samuel Morse) :** Samuel Morse arrive avec un grand sourire en coin, un rouleau de fil de cuivre "
            "sous le bras et sa pile chimique à la main : 'Laissez tomber vos télescopes les gars ! Mon fluide magique passe "
            "à travers la tempête sans mouiller son chapeau !'.\n\n"
            "**Case 4 (La Victoire) :** L'opérateur Morse tape frénétiquement sur son manipulateur : 'Clic-clac-clic !'. "
            "À 500 kilomètres de là, sous un orage terrible, l'électroaimant récepteur tape joyeusement sur sa bande de papier "
            "au sec : 'Message reçu instantanément ! Fin de la préhistoire des télécoms !'."
        )

    with im_t13:
        try:
            # Correction : Retrait des espaces parasites au début de la chaîne
            st.image("bd_telegraphe.jpg", caption="Caricature historique des télégraphes", use_container_width=True)
        except Exception:
            # Remplacement par un avertissement d'absence de média plus propre pour l'élève
            st.warning("Illustration en cours de chargement ou fichier 'bd_telegraphe.jpg' absent du serveur.")

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 1 ---
    afficher_atelier_historique_telecom(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    case_certif_tel1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_tel1_final", 
        disabled=verrou_at1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_tel1_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q1 = 0.0
            if "ordre_quiz_tab1_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel1_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q1 += 1.0

            # B. Correction de la Synthèse par texte à trous (10 trous -> 10 pts)
            score_t1 = 0.0
            if "champs_telecom1_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom1_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"trous_tel1_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t1 += 1.0

            # Sauvegarde des résultats en session
            st.session_state.score_suite1_tel_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_tel_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_telecom = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 1 ---
    if st.session_state.get("suite_verrouille_tab1_telecom", False):
        scr1_tel = st.session_state.get("score_suite1_tel_p1", 0.0)
        scr2_tel = st.session_state.get("score_suite1_tel_p2", 0.0)
        tot_s_tel = st.session_state.get("score_final_suite1_telecom", 0.0)
        timestamp_tel1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 1 HISTORIQUE SCELLÉ | Note de session : {tot_s_tel:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Telecom - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 1 : Origine historique, télégraphes Chappe et impulsion filaire Morse</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_tel:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab1_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel1_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel1_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel1 = preparer_nom_fichier("Rapport_Historique_Telecom").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_tel1,
            file_name=nom_fichier_html_tel1,
            mime="text/html",
            use_container_width=True
        )




with tab2:
    st.header("Les Ondes Électromagnétiques : La Radio")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab2_telecom = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_telecom

    if "inc_local_tel2" not in st.session_state:
        st.session_state.inc_local_tel2 = 0

    col_graph21, col_im_21 = st.columns(2)
   
    with col_graph21:
    # --- PERSONNAGES CLÉS : HERTZ ET MARCONI ---
        st.subheader("La découverte invisible : Heinrich Hertz et Guglielmo Marconi")
        st.write(
            "**Les Personnages :** En 1887, le physicien allemand **Heinrich Hertz** réussit l'impossible dans son laboratoire : "
            "générer et capter une étincelle électrique à distance, sans aucun fil conducteur. Il vient de prouver l'existence des ondes de Maxwell. "
            "Quelques années plus tard, l'Italien **Guglielmo Marconi** reprend ces travaux pour en faire un outil industriel : "
            "il invente la Télégraphie Sans Fil (TSF), transmettant des messages au-dessus de l'océan Atlantique et sauvant, "
            "plus tard, les survivants du Titanic [INDEX].\n\n"
            "**Fonctionnement extrêmement détaillé :** Une onde radio est une oscillation invisible du champ électromagnétique. "
            "Contrairement à une onde sonore qui a besoin d'air pour vibrer, l'onde radio est autonome et peut se déplacer dans le **vide absolu** "
            "à la vitesse de la lumière ($300~000$ km/s). Elle est définie par trois paramètres physiques stricts :\n"
            "* **L'Amplitude :** La puissance ou hauteur de la crête du signal (liée à l'intensité de l'onde).\n"
            "* **La Fréquence :** Le nombre d'oscillations complètes par seconde, mesuré en **Hertz (Hz)**.\n"
            "* **La Longueur d'onde ($\lambda$) :** La distance physique séparant deux sommets successifs. Elle est inversement proportionnelle "
            "à la fréquence ($\lambda = c / f$) : plus la fréquence est haute, plus les sommets sont serrés et plus la longueur d'onde est petite."
        )

        col_graph211, col_im_211 = st.columns(2)

        with col_graph211:
            try:
                # Réduction de la taille en fixant la largeur à 180 pixels maximum
                st.image("hertz.jpg", caption="Heinrich Hertz", width=300)
            except Exception:
                st.warning("Illustration en cours de chargement ou fichier 'hertz.jpg' absent du serveur.")
        with col_im_211:     
            try:
                st.image("Guglielmo_Marconi.jpg", caption="Guglielmo Marconi", width=300)
            except Exception:
                st.warning("Illustration en cours de chargement ou fichier 'Guglielmo_Marconi.jpg' absent du serveur.")


        # --- LABORATOIRE INTERACTIF : OSCILLATION ET LONGUEUR D'ONDE ---
        st.subheader("Laboratoire de métrologie hertzienne : Visualisation de la sinusoïde")
        st.write(
            "Modifiez les curseurs de fréquence et d'amplitude pour analyser en direct la modification géométrique de l'onde. "
            "Observez comment les sommets se resserrent (la longueur d'onde diminue) lorsque la fréquence augmente."
        )

        # Curseurs d'action cinématique
        f_slider = st.slider("Ajuster la fréquence du signal (Hz) :", min_value=1.0, max_value=5.0, value=2.0, step=0.5, key="slide_freq_radio")
        a_slider = st.slider("Ajuster l'amplitude de la tension (V) :", min_value=0.5, max_value=2.0, value=1.0, step=0.25, key="slide_amp_radio")

        # Calcul et tracé vectoriel synchrone de la sinusoïde
        import matplotlib.pyplot as plt
        import numpy as np

        fig_rd, ax_rd = plt.subplots(figsize=(6.5, 2.4), facecolor="white")
        ax_rd.set_facecolor("white")
        
        x_points = np.linspace(0, 10, 500)
        # L'équation du signal temporel : y = A * sin(2 * pi * f * t)
        y_points = a_slider * np.sin(f_slider * x_points)
        
        # Tracé de la courbe de tension
        ax_rd.plot(x_points, y_points, color="#10b981", linewidth=2.5, zorder=2)
        # Ligne d'axe zéro neutre
        ax_rd.plot([0, 10], [0, 0], color="#94a3b8", linewidth=1, linestyle="--", zorder=1)
        
        # MATÉRIALISATION PHYSIQUE DE LA PÉRIODE (Distance temporelle entre deux crêtes)
        if f_slider > 0:
            x_crete1 = 0.25 * (2 * np.pi) / f_slider
            x_crete2 = x_crete1 + (2 * np.pi) / f_slider
            if x_crete2 <= 10.0:
                # Flèche de cotation supérieure de la période temporelle T
                ax_rd.annotate(
                    "", xy=(x_crete1, a_slider + 0.15), xytext=(x_crete2, a_slider + 0.15),
                    arrowprops=dict(arrowstyle="<->", color="#ef4444", linewidth=1.5)
                )
                ax_rd.text((x_crete1 + x_crete2)/2, a_slider + 0.25, r"Période $T$", color="#ef4444", weight="bold", fontsize=9, ha="center")

        ax_rd.set_xlim(0, 10)
        ax_rd.set_ylim(-2.5, 2.5)
        ax_rd.axis("off")
        st.pyplot(fig_rd)
        plt.close(fig_rd)
        
        # Calcul rigoureux de la période réelle affichée (T = 1 / f)
        periode_calculee = 1.0 / f_slider
        st.info(f"Analyse temporelle : Pour une fréquence de {f_slider:.1f} Hz, la période physique mesurée entre deux crêtes est de T = {periode_calculee:.3f} seconde.")

    with col_im_21:
        try:
            # Réduction de la taille en fixant la largeur à 180 pixels maximum
            st.image("histoire_premiere_radio.jpg", caption="Découverte des ondes radio", width=500)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'histoire_premiere_radio.jpg' absent du serveur.")
            
        try:
            st.image("premiere_radio.jpg", caption="Première radio", width=400)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'premiere_radio.jpg' absent du serveur.")
            
        try:
            st.image("titanic_telegraphe.jpg", caption="Le Titanic", width=400)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'titanic_telegraphe.jpg' absent du serveur.")
    
    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ET ILLUSTRATION ---
    col_graph_r, im_t_r = st.columns(2)
    
    with col_graph_r:
        st.write("**La BD humoristique textuelle : Le mystère de l'étincelle fantôme**")
        st.info(
            "**Case 1 (Caricature de Heinrich Hertz) :** Heinrich Hertz fait claquer une énorme étincelle bleue sur sa table de labo : 'Bzzzt !'. "
            "À l'autre bout de la pièce, un simple anneau de cuivre émet un micro-éclair synchrone. "
            "Hertz sursaute, ses lunettes de travers : 'Incroyable ! Le signal a sauté à travers le vide de la pièce !'.\n\n"
            "**Case 2 (Le scepticisme) :** Des savants en costume rigide observent l'expérience en secouant la tête : "
            "'Une force invisible qui traverse les murs sans fil ? Mon cher Heinrich, c'est de la sorcellerie ou un courant d'air !'.\n\n"
            "**Case 3 (Caricature de Guglielmo Marconi) :** Le jeune Marconi arrive en courant sur la falaise, une immense perche de fer "
            "à la main en guise d'antenne : 'Laissez parler les sceptiques ! On va envoyer ce signal de l'autre côté de la Manche !'.\n\n"
            "**Case 4 (Le triomphe de la TSF) :** Marconi presse son interrupteur. Les ondes invisibles traversent l'océan "
            "dans la tempête. À Douvres, le récepteur tinte : 'Drelin !'. Les marins exultent : 'Les fils ont disparu, "
            "la radio est née !'."
        )

    with im_t_r:
        try:
            st.image("bd_radio.jpg", caption="Caricature historique de la transmission hertzienne", use_container_width=True)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'bd_radio.jpg' absent du serveur.")

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 2 ---
    afficher_atelier_ondes_radio(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    case_certif_tel2 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 2.", key="check_certif_tel2_final", disabled=verrou_at2)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_tel2_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q2 = 0.0
            if "ordre_quiz_tab2_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel2_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q2 += 1.0

            # B. Correction de la Synthèse par texte à trous (10 trous -> 10 pts)
            score_t2 = 0.0
            if "champs_telecom2_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom2_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = st.session_state.get(f"trous_tel2_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t2 += 1.0

            # Sauvegarde des résultats en session
            st.session_state.score_suite2_tel_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_tel_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_telecom = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 2 ---
    if st.session_state.get("suite_verrouille_tab2_telecom", False):
        scr1_tel2 = st.session_state.get("score_suite2_tel_p1", 0.0)
        scr2_tel2 = st.session_state.get("score_suite2_tel_p2", 0.0)
        tot_s_tel2 = st.session_state.get("score_final_suite2_telecom", 0.0)
        timestamp_tel2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 2 ONDES RADIO SCELLÉ | Note de session : {tot_s_tel2:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Ondes Radio - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 2 : Physique spectrale, oscillation sinusoïdale et ondes hertziennes</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #10b981;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_tel2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab2_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel2_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel2_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel2 = preparer_nom_fichier("Rapport_Ondes_Radio").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_tel2,
            file_name=nom_fichier_html_tel2,
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("Le Téléphone à la Maison : L'Ère Filaire")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 3 ---
    if "suite_verrouille_tab3_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab3_telecom = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_telecom

    if "inc_local_tel3" not in st.session_state:
        st.session_state.inc_local_tel3 = 0

    # --- PERSONNAGE CLÉ : ALEXANDER GRAHAM BELL ---
    st.subheader("La transmission de la voix : Alexander Graham Bell (1876)")
    st.write(
        "**Le Personnage :** En 1876, l'éducateur d'enfants sourds et inventeur écossais **Alexander Graham Bell** réalise "
        "une percée monumentale en déposant le brevet du premier téléphone électrique fonctionnel. "
        "Alors qu'il tente d'améliorer le télégraphe, il découvre qu'un courant électrique continu peut transporter "
        "la forme exacte des vibrations sonores de la voix humaine.\n\n"
        "**Fonctionnement extrêmement détaillé :** Contrairement au télégraphe qui utilise des signaux saccadés (tout ou rien), "
        "le téléphone fixe repose sur un système **analogique continu** interconnecté par des câbles physiques en cuivre. "
        "L'appareil s'appuie sur deux composants physiques réversibles contenus dans le combiné :\n"
        "* **L'émetteur (Le Microphone) :** La voix frappe une fine membrane métallique. En vibrant, cette membrane presse "
        "plus ou moins fortement des grains de carbone logés dans une capsule (pastille). Cette compression mécanique modifie "
        "en temps réel la résistance électrique de la capsule, transformant l'onde sonore en une ondulation correspondante du courant.\n"
        "* **Le récepteur (L'Écouteur) :** À l'autre bout de la ligne de cuivre, ce courant variable pénètre dans un petit électroaimant. "
        "Le champ magnétique généré attire et relâche une membrane métallique au rythme exact du signal reçu, recréant fidèlement "
        "la vibration de l'air et donc la voix originale."
    )

    try:
        st.image("telephone_maison.jpg", caption=f"Le télephone à la maison", use_container_width=True)
    except Exception:
        st.error("Image d'illustration manquante : telephone_maison.jpg")


    st.divider()

    # --- LABORATOIRE INTERACTIF : ÉTAT DU COMBINÉ ET NUMÉROTATION ---
    st.subheader("Laboratoire de commutation domestique : Le combiné et le cadran")
    st.write(
        "Modifiez l'interrupteur pour simuler l'état du décroché téléphonique. "
        "Faites ensuite tourner le bouton rotatif pour simuler la numérotation par impulsions d'époque."
    )

    # Commandes cinématiques
    etat_telephone = st.radio("État du combiné fixe de la maison :", options=["Posé sur la base (Raccroché - Ligne ouverte)", "Soulevé de la base (Décroché - Ligne fermée)"], index=0, horizontal=True)
    chiffre_cadran = st.slider("Sélectionner un chiffre à composer sur le cadran rotatif :", min_value=1, max_value=9, value=5, step=1)

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_tl, ax_tl = plt.subplots(figsize=(7, 3.8), facecolor="white")
    ax_tl.set_facecolor("white")
    
    # 1. Base fixe du boîtier de téléphone (Bakélite noire pyramidale centrée à x=1.5)
    ax_tl.add_patch(patches.Rectangle((1.5, 0.2), 2.0, 1.1, facecolor="#1e293b", edgecolor="black", linewidth=2.5, zorder=2))
    
    # Crochets de support fixes au sommet du boîtier (y=1.3)
    ax_tl.plot([1.8, 1.8], [1.3, 1.45], color="#0f172a", linewidth=4, zorder=3)
    ax_tl.plot([3.2, 3.2], [1.3, 1.45], color="#0f172a", linewidth=4, zorder=3)
    
    # Cadran Rotatif central en verre (Axe à x=2.5, y=0.75)
    ax_tl.add_patch(patches.Circle((2.5, 0.75), 0.4, facecolor="#e2e8f0", edgecolor="#475569", linewidth=2, zorder=3))
    ax_tl.add_patch(patches.Circle((2.5, 0.75), 0.15, facecolor="#cbd5e1", edgecolor="#475569", zorder=4))
    
    # Les 9 trous de numérotation circulaires
    for ch in range(1, 10):
        angle_trou = np.radians(ch * 32 + 40)
        ax_tl.add_patch(patches.Circle((2.5 + 0.26 * np.cos(angle_trou), 0.75 + 0.26 * np.sin(angle_trou)), 0.05, facecolor="white", edgecolor="black", zorder=5))
        
    # 2. GESTION DES COORDONNÉES DYNAMIQUES DU COMBINÉ MOBILE
    if "Posé" in etat_telephone:
        # Le combiné repose parfaitement à l'horizontale sur ses deux crochets fixes
        x_comb = [1.4, 3.6]
        y_comb = [1.48, 1.48]
        ax_tl.plot(x_comb, y_comb, color="#0f172a", linewidth=12, solid_capstyle="round", zorder=6) # Poignée
        ax_tl.add_patch(patches.Circle((1.4, 1.48), 0.16, facecolor="#0f172a", zorder=5)) # Écouteur gauche
        ax_tl.add_patch(patches.Circle((3.6, 1.48), 0.16, facecolor="#0f172a", zorder=5)) # Micro droit
        
        # Fil de raccordement pendant sous forme d'arc propre
        x_fil = np.linspace(0.8, 1.5, 50)
        y_fil = 0.85 - 0.4 * (1.0 - ((x_fil - 1.15) / 0.35) ** 2)
        ax_tl.plot(x_fil, y_fil, color="#334155", linewidth=2, linestyle="-", zorder=1)
        
        lbl_stat = "Ligne téléphonique au repos. Tension continue stable de 48V présente. Aucune impulsion."
    else:
        # Le combiné est soulevé dans les airs, incliné et prêt pour la conversation
        x_comb = [0.8, 2.2]
        y_comb = [2.2, 2.6]
        ax_tl.plot(x_comb, y_comb, color="#0f172a", linewidth=12, solid_capstyle="round", zorder=6) # Poignée
        ax_tl.add_patch(patches.Circle((0.8, 2.2), 0.16, facecolor="#0f172a", zorder=5)) # Écouteur gauche
        ax_tl.add_patch(patches.Circle((2.2, 2.6), 0.16, facecolor="#0f172a", zorder=5)) # Micro droit
        
        # Cordon extensible torsadé stabilisé
        t_fil = np.linspace(0, 1, 100)
        x_fil = 0.8 + (1.5 - 0.8) * t_fil + 0.1 * np.sin(t_fil * 8 * np.pi)
        y_fil = 2.1 - (2.1 - 0.4) * t_fil
        ax_tl.plot(x_fil, y_fil, color="#334155", linewidth=2, zorder=1)
        
        # 3. DESSIN DU TRAIN D'IMPULSIONS ÉLECTRIQUES NUMÉRIQUES (À droite du téléphone)
        # Ligne de cuivre sortant de l'appareil (de x=3.5 à x=6.8, hauteur y=0.75)
        ax_tl.plot([3.5, 6.8], [0.75, 0.75], color="#94a3b8", linewidth=1.5, linestyle="--", zorder=1)
        ax_tl.text(5.2, 1.3, "Ligne vers le Central", color="#475569", fontsize=8, ha="center", weight="bold")
        
        # Algorithme de génération des créneaux de coupure (Impulsions décimales)
        # Chaque chiffre génère N impulsions carrées de coupure de boucle
        x_depart_impulsion = 3.8
        for imp in range(chiffre_cadran):
            # Dessin du créneau carré : rupture de tension (y monte à 1.1) puis retour à 0.75
            ax_tl.plot([x_depart_impulsion, x_depart_impulsion], [0.75, 1.1], color="#ef4444", linewidth=2.5, zorder=3)
            ax_tl.plot([x_depart_impulsion, x_depart_impulsion + 0.15], [1.1, 1.1], color="#ef4444", linewidth=2.5, zorder=3)
            ax_tl.plot([x_depart_impulsion + 0.15, x_depart_impulsion + 0.15], [1.1, 0.75], color="#ef4444", linewidth=2.5, zorder=3)
            
            # Petit point indicateur sous l'impulsion
            ax_tl.text(x_depart_impulsion + 0.075, 0.5, "I", color="#ef4444", weight="bold", fontsize=8, ha="center")
            
            # Espacement régulier pour le créneau suivant
            x_depart_impulsion += 0.30
            
        lbl_stat = f"Ligne active. Le cadran rotatif libère son ressort : envoi de {chiffre_cadran} créneaux d'impulsion de coupure de boucle."

    # Cadrage final étanche
    ax_tl.set_xlim(0, 7.0)
    ax_tl.set_ylim(0, 3.2)
    ax_tl.axis("off")
    st.pyplot(fig_tl)
    plt.close(fig_tl)
    
    st.info(lbl_stat)

    st.divider()

    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ET ILLUSTRATION ---
    col_graph_t, im_t_t = st.columns(2)
    
    with col_graph_t:
        st.write("**La BD humoristique textuelle : 'Allo, mademoiselle ? Ne coupez pas !'**")
        st.info(
            "**Case 1 (Caricature d'Alexander Graham Bell) :** Bell renverse accidentellement de l'acide sur son pantalon dans son laboratoire "
            "et hurle dans son étrange entonnoir en bois : 'Monsieur Watson, venez ici, j'ai besoin de vous !'. "
            "Dans la pièce d'à côté, Watson sursaute en entendant la voix sortir de sa bobine métallique : 'Ça marche !'.\n\n"
            "**Case 2 (Le bouchon des Demoiselles) :** Trente ans plus tard, une immense pièce regorge de fiches et de cordons. "
            "Les 'Demoiselles du téléphone' s'emmêlent les pinceaux sous les cris des abonnés : "
            "'Non Monsieur le Baron, je ne vous branche pas sur la boucherie, c'est une erreur de fiche !'.\n\n"
            "**Case 3 (La jalousie de l'entrepreneur) :** Almon Strowger, un croque-mort furieux de voir l'opératrice (femme de son concurrent) "
            "détourner ses clients, tape du poing sur la table : 'Puisque c'est comme ça, je vais remplacer les demoiselles par un cerveau mécanique !'. "
            "Il conçoit le commutateur automatique.\n\n"
            "**Case 4 (La Modernité) :** Une famille des années 1930 fait tourner fièrement le lourd cadran en bakélite noire de son Socotel : "
            "'Écoute fiston, on tourne le 2, puis le 4... Plus besoin d'opératrice, on appelle directement le voisin sans témoin !'."
        )

    with im_t_t:
        try:
            st.image("premiere_presse.jpg", caption="Combinés et standards téléphoniques anciens")
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'premiere_presse.jpg' absent du serveur.")

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 3 ---
    afficher_atelier_telephone_maison(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    case_certif_tel3 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 3.", key="check_certif_tel3_final", disabled=verrou_at3)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_tel3_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identity dans l'onglet 'Identification'.")
        elif not case_certif_tel3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q3 = 0.0
            if "ordre_quiz_tab3_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel3_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # B. Correction du Texte à trous (10 trous -> 10 pts)
            score_t3 = 0.0
            if "champs_telecom3_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom3_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = st.session_state.get(f"trous_tel3_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t3 += 1.0

            st.session_state.score_suite3_tel_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_tel_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_telecom = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 3 ---
    if st.session_state.get("suite_verrouille_tab3_telecom", False):
        scr1_tel3 = st.session_state.get("score_suite3_tel_p1", 0.0)
        scr2_tel3 = st.session_state.get("score_suite3_tel_p2", 0.0)
        tot_s_tel3 = st.session_state.get("score_final_suite3_telecom", 0.0)
        timestamp_tel3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 3 TÉLÉPHONE FIXE SCELLÉ | Note de session : {tot_s_tel3:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Téléphone Fixe - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 3 : Évolution de la téléphonie domestique filaire et microphone analogique</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_tel3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab3_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel3_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel3_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel3 = preparer_nom_fichier("Rapport_Telephone_Maison").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_tel3,
            file_name=nom_fichier_html_tel3,
            mime="text/html",
            use_container_width=True
        )



with tab4:
    st.header("Les Téléphones Portables : Du Cellulaire au Smartphone")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 4 ---
    if "suite_verrouille_tab4_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab4_telecom = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_telecom

    if "inc_local_tel4" not in st.session_state:
        st.session_state.inc_local_tel4 = 0
        
    if "pos_smart_x" not in st.session_state:
        st.session_state.pos_smart_x = 2.5

    # --- PERSONNAGE CLÉ : MARTIN COOPER ---
    st.subheader("La coupure du cordon : Martin Cooper et le réseau cellulaire")
    st.write(
        "**Le Personnage :** En avril 1973, l'ingénieur américain **Martin Cooper**, alors chercheur chez Motorola, "
        "réalise un geste provocateur historique : il passe le tout premier appel de l'histoire depuis un combiné mobile "
        "dans une rue de New York... en téléphonant directement à son rival direct chez Bell Labs ! Son appareil, le DynaTAC, "
        "pesait plus d'un kilogramme et offrait seulement 20 minutes d'autonomie.\n\n"
        "**Fonctionnement extrêmement détaillé :** Pour permettre à des millions d'utilisateurs de téléphoner en même temps "
        "sans saturer les ondes hertziennes, il a fallu abandonner l'idée d'un émetteur central unique. "
        "L'architecture repose sur le découpage du territoire en une multitude de petites zones géographiques appelées **cellules** "
        "(généralement modélisées sous forme d'hexagones). Chaque cellule possède sa propre **antenne-relais** de faible portée.\n"
        "Lorsqu'un smartphone est allumé, il écoute les balises aériennes et se connecte à l'antenne la plus proche. "
        "Si l'utilisateur se déplace (en voiture ou en train), le smartphone mesure en continu l'affaiblissement du signal. "
        "Dès qu'il traverse la frontière d'une cellule, le cœur de réseau effectue un **handover** : la communication est "
        "transférée à l'antenne suivante en quelques millisecondes, de manière totalement invisible pour l'utilisateur. "
        "La voix est numérisée, compressée, convertie en paquets d'ondes **hyperfréquences**, puis acheminée."
    )


    col_graph4, col_im_4, col_dessin_4 = st.columns(3)

    with col_graph4:
        try:
            # Réduction de la taille en fixant la largeur à 180 pixels maximum
            st.image("Martin_Cooper.jpg", caption="Martin_Cooper", width=300)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'Martin_Cooper.jpg' absent du serveur.")
    with col_im_4:     
        try:
            st.image("telephone_portablebis.jpg", caption="évolution jusqu'aux smartphone", width=300)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'telephone_portablebis.jpg' absent du serveur.")
    with col_dessin_4:     
        try:
            st.image("telephone_portable.jpg", caption="évolution des téléphones portables ", width=300)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'telephone_portable.jpg' absent du serveur.")
            
    st.divider()

    # --- SIMULATEUR INTERACTIF : HANDOVER ET CELLULES HEXAGONALES ---
    st.subheader("Laboratoire de cinématique réseau : Maillage et transfert intercellulaire")
    st.write(
        "Déplacez le curseur de position pour faire circuler le smartphone le long du territoire. "
        "Observez l'antenne active changer de couleur et transférer la liaison radio (handover) au passage des frontières."
    )

    # Curseur cinématique de déplacement du mobile
    x_smartphone = st.slider("Déplacer la position du smartphone le long de la route :", min_value=0.5, max_value=4.5, value=2.5, step=0.1, key="slide_pos_smart")
    st.session_state.pos_smart_x = x_smartphone

    # Rendu Matplotlib du maillage cellulaire
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_cel, ax_cel = plt.subplots(figsize=(6.5, 3.2), facecolor="white")
    ax_cel.set_facecolor("white")
    
    # Dessin des deux cellules (Hexagones schématiques ou zones d'antennes)
    # Zone Antenne 1 (centrée à x=1.5)
    ax_cel.add_patch(patches.RegularPolygon((1.5, 1.2), numVertices=6, radius=1.4, facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.5, zorder=1))
    ax_cel.plot([1.5, 1.5], [1.2, 2.2], color="#475569", linewidth=2.5, zorder=2) # Pylône 1
    ax_cel.add_patch(patches.Circle((1.5, 2.2), 0.06, facecolor="red"))
    
    # Zone Antenne 2 (centrée à x=4.5)
    ax_cel.add_patch(patches.RegularPolygon((4.5, 1.2), numVertices=6, radius=1.4, facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.5, zorder=1))
    ax_cel.plot([4.5, 4.5], [1.2, 2.2], color="#475569", linewidth=2.5, zorder=2) # Pylône 2
    ax_cel.add_patch(patches.Circle((4.5, 2.2), 0.06, facecolor="red"))
    
    # Route de circulation basse
    ax_cel.plot([0.0, 6.0], [0.4, 0.4], color="#1e293b", linewidth=3, zorder=2)
    
    # Logique d'activation de l'antenne (Frontière fixée au milieu à x=3.0)
    if x_smartphone <= 3.0:
        antenne_active = 1
        color_onde1, color_onde2 = "#ef4444", "#94a3b8"
        # Tracé des ondes de liaison vers l'antenne 1
        ax_cel.plot([1.5, x_smartphone], [2.2, 0.55], color="#ef4444", linewidth=2, linestyle=":", zorder=3)
        lbl_net = "Smartphone connecté à l'Antenne Relais 1 (Cellule Ouest). Signal fort."
    else:
        antenne_active = 2
        color_onde1, color_onde2 = "#94a3b8", "#ef4444"
        # Tracé des ondes de liaison vers l'antenne 2
        ax_cel.plot([4.5, x_smartphone], [2.2, 0.55], color="#ef4444", linewidth=2, linestyle=":", zorder=3)
        lbl_net = "Handover effectué ! Connexion transférée à l'Antenne Relais 2 (Cellule Est)."

    # Dessin des arcs d'ondes de diffusion sur les pylônes
    ax_cel.add_patch(patches.Arc((1.5, 2.2), 0.3, 0.3, angle=0, theta1=0, theta2=360, color=color_onde1, linewidth=1.5))
    ax_cel.add_patch(patches.Arc((4.5, 2.2), 0.3, 0.3, angle=0, theta1=0, theta2=360, color=color_onde2, linewidth=1.5))

    # Dessin du smartphone de l'étudiant (petit rectangle vertical qui roule)
    ax_cel.add_patch(patches.Rectangle((x_smartphone - 0.1, 0.45), 0.2, 0.35, facecolor="#1e293b", edgecolor="black", zorder=4))
    # Écran allumé du smartphone
    ax_cel.add_patch(patches.Rectangle((x_smartphone - 0.06, 0.5), 0.12, 0.25, facecolor="#38bdf8", zorder=5))

    ax_cel.set_xlim(0, 6.0)
    ax_cel.set_ylim(0, 2.7)
    ax_cel.axis("off")
    st.pyplot(fig_cel)
    plt.close(fig_cel)
    
    st.info(lbl_net)

    st.divider()

    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ET ILLUSTRATION ---
    col_graph_s, im_t_s = st.columns(2)
    
    with col_graph_s:
        st.write("**La BD humoristique textuelle : L'appel qui venait de la rue**")
        st.info(
            "**Case 1 (Caricature de Martin Cooper) :** Martin Cooper est debout sur le trottoir de la 6e Avenue, "
            "portant à bout de bras une énorme brique beige en plastique munie d'une antenne de trente centimètres. "
            "Les passants le regardent en riant : 'Regardez cet hurluberlu qui parle à sa boîte à chaussures !'.\n\n"
            "**Case 2 (Le coup de fil provocateur) :** Cooper tape le numéro de son rival des Bell Labs, Joel Engel. "
            "Le téléphone d'Engel sonne : 'Dring !'. Engel décroche. Cooper sourit : 'Joel, je t'appelle depuis un vrai "
            "téléphone portable, un téléphone portatif, sans fil !'. Un grand silence glacial s'installe à l'autre bout.\n\n"
            "**Case 3 (L'autoroute des hexagones) :** Trente ans plus tard, un automobiliste file sur l'autoroute à 130 km/h "
            "en parlant à sa famille. En arrière-plan, les pylônes de fer se passent le signal comme un témoin de relais : "
            "'Il quitte ma zone ! Attrape-le Antenne 3, la SIM arrive chez toi !'.\n\n"
            "**Case 4 (Le couteau suisse moderne) :** Un adolescent regarde son smartphone tactile ultra-fin : "
            "'Une brique de un kilo pour juste parler ? Mais comment ils faisaient pour envoyer des messages, "
            "regarder des vidéos et jouer en ligne dans la rue ?'."
        )

    with im_t_s:
        try:
            st.image("caricature_radio.jpg", caption="Évolution des terminaux portables cellulaires")
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'caricature_radio.jpg' absent du serveur.")

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 4 ---
    afficher_atelier_smartphone(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    case_certif_tel4 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 4.", key="check_certif_tel4_final", disabled=verrou_at4)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_tel4_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q4 = 0.0
            if "ordre_quiz_tab4_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel4_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0

            # B. Correction de la Synthèse par texte à trous (10 trous -> 10 pts)
            score_t4 = 0.0
            if "champs_telecom4_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom4_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"trous_tel4_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t4 += 1.0

            st.session_state.score_suite4_tel_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_tel_p2 = round(float(score_t4), 1)
            # Calcul et enregistrement de la note globale de l'Atelier 4 sur 20 points
            st.session_state.score_final_suite4_telecom = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 4 ---
    if st.session_state.get("suite_verrouille_tab4_telecom", False):
        scr1_tel4 = st.session_state.get("score_suite4_tel_p1", 0.0)
        scr2_tel4 = st.session_state.get("score_suite4_tel_p2", 0.0)
        tot_s_tel4 = st.session_state.get("score_final_suite4_telecom", 0.0)
        timestamp_tel4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 4 TÉLÉPHONIE MOBILE SCELLÉ | Note de session : {tot_s_tel4:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Telephonie Mobile - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 4 : Réseaux cellulaires maillés, micro-ondes et handover dynamique</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e293b;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_tel4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab4_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel4_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom4_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel4_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel4 = preparer_nom_fichier("Rapport_Telephone_Mobile").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_tel4,
            file_name=nom_fichier_html_tel4,
            mime="text/html",
            use_container_width=True
        )

with tab5:
    st.header("La Fibre Optique : La Révolution Lumineuse")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab5_telecom = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_telecom

    if "inc_local_tel5" not in st.session_state:
        st.session_state.inc_local_tel5 = 0

    # --- PERSONNAGES CLÉS : TYNDALL ET KAO ---
    st.subheader("Piéger la lumière : John Tyndall et Charles Kao")
    st.write(
        "**Les Personnages :** En 1870, le physicien britannique **John Tyndall** réalise une expérience spectaculaire : "
        "en éclairant l'intérieur d'un réservoir d'eau percé, il démontre que la lumière se courbe en suivant le jet d'eau. "
        "La lumière est prisonnière du fluide ! Près d'un siècle plus tard, en 1966, le chercheur sino-américain **Charles Kao** "
        "comprend que l'on peut remplacer l'eau par un fil de verre microscopique. En purifiant le verre pour éliminer les impuretés, "
        "il réduit l'atténuation du signal et ouvre la voie aux transmissions kilométriques, ce qui lui vaudra le prix Nobel de physique .\n\n"
        "**Fonctionnement extrêmement détaillé :** La fibre optique est un cheveu de verre de haute technologie composé de deux couches concentriques :\n"
        "* **Le Cœur ($n_1$) :** Le cylindre central en silice ultra-pure où est injecté le faisceau laser.\n"
        "* **La Gaine ($n_2$) :** La couche périphérique qui entoure le cœur. Sa caractéristique fondamentale est de posséder un indice de réfraction "
        "strictement inférieur à celui du cœur ($n_2 < n_1$) .\n\n"
        "Lorsque le faisceau laser pénètre dans le cœur avec un angle d'incidence suffisamment rasant, il frappe l'interface cœur-gaine. "
        "En raison de la différence d'indice de réfraction, la lumière subit une **réflexion totale interne** : elle rebondit à 100% sans jamais traverser la gaine. "
        "Le signal lumineux (les photons) se propage ainsi en zigzag à la vitesse de 200 000 km/s dans le verre, insensible aux parasites électriques terrestres."
    )


    col_graph5, col_im_5, col_dessin_5 = st.columns(3)

    with col_graph5:
        try:
            # Réduction de la taille à 150 pixels pour un affichage en colonne harmonieux
            st.image("John_Tyndall.jpg", caption="John Tyndall", width=400)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'John_Tyndall.jpg' absent du serveur.")
            
    with col_im_5:     
        try:
            st.image("Charles_Kao.jpg", caption="Charles Kao", width=400)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'Charles_Kao.jpg' absent du serveur.")
            
    with col_dessin_5:     
        try:
            st.image("lumiere_eau.jpg", caption="Lumière dans un jet d'eau", width=400)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'lumiere_eau.jpg' absent du serveur.")

    st.divider()

    # --- LABORATOIRE INTERACTIF : RÉFLEXION TOTALE INTERNE ---
    st.subheader("Laboratoire d'optique géométrique : Guidage et angle critique")
    st.write(
        "Modifiez le curseur d'angle d'injection du faisceau laser. Observez que si l'angle est trop raide, la lumière traverse "
        "la gaine et se perd. Si l'angle est incliné, la réflexion totale interne s'active et emprisonne le faisceau."
    )

    # Curseur angulaire d'injection laser
    angle_laser = st.slider("Ajuster l'angle d'incidence du faisceau laser (degrés) :", min_value=10, max_value=50, value=25, step=5, key="slide_angle_fibre")

    # Rendu graphique Matplotlib de la fibre optique
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_fb, ax_fib = plt.subplots(figsize=(6.5, 2.4), facecolor="white")
    ax_fib.set_facecolor("white")
    
    # Dessin des couches fixes de la fibre optique (Gaine haute/basse et Cœur central)
    ax_fib.add_patch(patches.Rectangle((0.5, 1.4), 5.5, 0.4, facecolor="#e2e8f0", edgecolor="#cbd5e1", label="Gaine (n2)")) # Gaine supérieure
    ax_fib.add_patch(patches.Rectangle((0.5, 0.6), 5.5, 0.8, facecolor="none", edgecolor="#475569", linewidth=1.5, zorder=2)) # Cœur (n1)
    ax_fib.add_patch(patches.Rectangle((0.5, 0.2), 5.5, 0.4, facecolor="#e2e8f0", edgecolor="#cbd5e1")) # Gaine inférieure
    
    ax_fib.text(5.5, 1.5, "Gaine", fontsize=8, color="#64748b", weight="bold")
    ax_fib.text(5.5, 0.9, "Cœur", fontsize=8, color="#475569", weight="bold")
    
    # 2. ALGORITHME VECTORIEL SYNCHRONE DU FAISCEAU LASER
    # Source du laser à gauche (x=0.5, y=1.0)
    if angle_laser >= 35:
        # Angle trop droit : Réfraction et perte du signal dans la gaine
        rad_f = np.radians(angle_laser)
        x_impact = 0.5 + 0.4 / np.tan(rad_f)
        ax_fib.plot([0.5, x_impact], [1.0, 1.4], color="#ef4444", linewidth=2.5, zorder=3) # Faisceau cœur
        ax_fib.plot([x_impact, x_impact + 0.5], [1.4, 1.7], color="#ef4444", linewidth=1.5, linestyle=":", zorder=3) # Perte gaine
        lbl_fib = "Angle trop raide ! Réfraction ouverte : la lumière s'échappe à travers la gaine optique. Signal perdu."
    else:
        # Réflexion totale interne active : Le faisceau rebondit proprement
        rad_f = np.radians(angle_laser)
        pas_x = 0.4 / np.tan(rad_f)
        
        # Tracé des zigzags successifs par points d'impacts rigoureux
        pts_x = [0.5, 0.5 + pas_x, 0.5 + 3*pas_x, 0.5 + 5*pas_x, 6.0]
        pts_y = [1.0, 1.4, 0.6, 1.4, 1.0]
        
        # Tracé du rayon laser confiné
        ax_fib.plot(pts_x, pts_y, color="#10b981", linewidth=2.5, solid_capstyle="round", zorder=3)
        lbl_fib = "Réflexion totale interne active ! Le faisceau est emprisonné et guidé au centre du cœur de verre."

    ax_fib.set_xlim(0, 6.5)
    ax_fib.set_ylim(0, 2.0)
    ax_fib.axis("off")
    st.pyplot(fig_fb)
    plt.close(fig_fb)
    
    st.info(lbl_fib)

    st.divider()

    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ET ILLUSTRATION ---
    col_graph_f, im_t_f = st.columns(2)
    
    with col_graph_f:
        st.write("**La BD humoristique textuelle : La lumière domestiquée**")
        st.info(
            "**Case 1 (Caricature de John Tyndall) :** Tyndall éclaire un seau d'eau percé dans le noir. L'eau coule et la lumière "
            "suit la courbure du jet pour éclairer le sol : 'Regardez ! J'ai appris à la lumière à tourner les coins !'. "
            "Les spectateurs applaudissent devant ce filet d'eau lumineux.\n\n"
            "**Case 2 (Le défi du verre de Kao) :** Un ingénieur des années 1960 regarde un bloc de verre de fenêtre épais : "
            "'Faire voyager la lumière sur des kilomètres là-dedans ? Mais votre signal va buter dans les bulles et s'éteindre "
            "au bout de deux mètres !'. Charles Kao sort sa formule de purification : 'Pas si on nettoie la silice au niveau atomique !'.\n\n"
            "**Case 3 (Le grand plongeon océanique) :** Un énorme navire câblier déroule des milliers de kilomètres de fibre optique "
            "noire blindée au fond de l'océan Atlantique : 'Attention les requins, poussez-vous ! On installe l'autoroute des photons "
            "entre Paris et New York !'.\n\n"
            "**Case 4 (L'abondance du haut débit) :** Un joueur en ligne télécharge un fichier énorme en deux secondes sur sa box : "
            "'Un fil de verre de la taille d'un cheveu transmet toute l'encyclopédie mondiale en un clin d'œil ? "
            "C'est quand même plus propre que le vieux fil en cuivre !'."
        )

    with im_t_f:
        try:
            st.image("caricature_fibre.jpg", caption="Fabrication et raccordement de la fibre de verre")
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'caricature_fibre.jpg' absent du serveur.")

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 5 ---
    afficher_atelier_fibre_optique(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    case_certif_tel5 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 5.", key="check_certif_tel5_final", disabled=verrou_at5)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_tel5_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q5 = 0.0
            if "ordre_quiz_tab5_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel5_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q5 += 1.0

            # B. Correction de la Synthèse par texte à trous (10 trous -> 10 pts)
            score_t5 = 0.0
            if "champs_telecom5_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom5_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = st.session_state.get(f"trous_tel5_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t5 += 1.0

            st.session_state.score_suite5_tel_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_tel_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_telecom = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 5 ---
    if st.session_state.get("suite_verrouille_tab5_telecom", False):
        scr1_tel5 = st.session_state.get("score_suite5_tel_p1", 0.0)
        scr2_tel5 = st.session_state.get("score_suite5_tel_p2", 0.0)
        tot_s_tel5 = st.session_state.get("score_final_suite5_telecom", 0.0)
        timestamp_tel5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 5 FIBRE OPTIQUE SCELLÉ | Note de session : {tot_s_tel5:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Fibre Optique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 5 : Guidage de faisceau photonique, indices de silice et réflexion totale interne</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #3b82f6;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_tel5:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab5_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel5_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom5_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel5_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel5 = preparer_nom_fichier("Rapport_Fibre_Optique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_tel5,
            file_name=nom_fichier_html_tel5,
            mime="text/html",
            use_container_width=True
        )


with tab6:
    st.header("Le Réseau Satellite : Les Communications Orbitales")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 6 ---
    if "suite_verrouille_tab6_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab6_telecom = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_hydro = st.session_state.suite_verrouille_tab6_telecom  # Robustesse clés

    if "inc_local_tel6" not in st.session_state:
        st.session_state.inc_local_tel6 = 0

    # --- HISTORIQUE ET PHYSIQUE ORBITALE ---
    st.subheader("La conquête des cimes : L'orbite géostationnaire d'Arthur C. Clarke")
    st.write(
        "**Le Concept :** Dès 1945, l'écrivain de science-fiction et inventeur britannique **Arthur C. Clarke** émet une idée "
        "révolutionnaire : si l'on place un satellite artificiel à une altitude exacte de **35 786 kilomètres** au-dessus de l'équateur, "
        "sa période de révolution sera identique à la période de rotation de la Terre (23 heures et 56 minutes). "
        "Vu d'en bas, le satellite restera ainsi éternellement suspendu au même point du ciel, devenant un relais radio permanent.\n\n"
        "**Fonctionnement extrêmement détaillé :** Les satellites de télécommunication GEO font office de miroirs hertziens "
        "géants dans l'espace. La transmission se décompose en trois segments techniques :\n"
        "* **Le segment sol émetteur :** Une station terrestre focalise un faisceau d'ondes **hyperfréquences** directionnel "
        "à l'aide d'une antenne parabolique (assiette) pointée pile vers la position orbitale du satellite (liaison montante).\n"
        "* **Le segment spatial (Le Répéteur) :** À bord du satellite, le répéteur (ou transpondeur) intercepte ce signal "
        "extrêmement affaibli par la traversée de l'atmosphère, le nettoie des bruits de fond, l'amplifie fortement à l'aide d'énergie "
        "captée par de grands panneaux photovoltaïques, puis décale sa fréquence pour éviter tout larsen radio.\n"
        "* **Le segment sol récepteur :** Le satellite renvoie le signal sous la forme d'un cône de couverture vers le continent "
        "(liaison descendante), capté instantanément par les antennes paraboliques individuelles des abonnés."
    )

    st.divider()

    # --- HISTORIQUE GRAPHIQUE EN 3 COLONNES MINIATURES ---
    st.write("**Galerie historique de la conquête hertzienne spatiale**")
    col_g6, col_im_6, col_dessin_6 = st.columns(3)

    with col_g6:
        col_g61, col_g62 = st.columns(2)
        with col_g61:   
            try: st.image("Arthur_C_Clarke.jpg", caption="Arthur C. Clarke", width= 250) # Réutilisation ou témoin
            except Exception: st.warning("Fichier d'illustration indisponible.")
        with col_g62:   
            try: st.image("orbite_geostationnaire.jpg", caption="Orbite", width= 300) # Réutilisation ou témoin
            except Exception: st.warning("Fichier d'illustration indisponible.")            
    with col_im_6:     
        try: st.image("telstar_1.jpg", caption="Telstar 1 (1962)", width=300)
        except Exception: st.warning("Fichier d'illustration indisponible.")
    with col_dessin_6:     
        col_dessin_61, col_dessin_62 = st.columns(2)
        with col_dessin_61:   
            try: st.image("antenne_parabole.jpg", caption="fonctionnement antenne parabole", width= 300) # Réutilisation ou témoin
            except Exception: st.warning("Fichier d'illustration indisponible.")
        with col_dessin_62:   
            try: st.image("antenne.jpg", caption="Parabole Pleumeur-Bodou", width=300)
            except Exception: st.warning("Fichier d'illustration indisponible.") 
    # --- LABORATOIRE INTERACTIF : FAISCEAU ET ANGLE DE LA PARABOLE ---
    st.subheader("Laboratoire de cinématique spatiale : Pointage et cône de couverture")
    st.write(
        "Modifiez le curseur de position orbitale du satellite pour simuler son ajustement de trajectoire par ses micro-propulseurs. "
        "Observez l'impact direct du pointage du faisceau hyperfréquence sur la station réceptrice au sol."
    )

    # Curseur d'ajustement orbital
    pos_satellite_x = st.slider("Ajuster la position orbitale est-ouest du satellite :", min_value=1.5, max_value=4.5, value=3.0, step=0.25, key="slide_pos_sat")

    # Rendu graphique Matplotlib de l'orbite
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_sat, ax_sat = plt.subplots(figsize=(6.5, 3.2), facecolor="white")
    ax_sat.set_facecolor("white")
    
    # Dessin de la Terre (arc de cercle inférieur bleu à y=0)
    ax_sat.add_patch(patches.Arc((3.0, -4.0), 7.0, 5.0, angle=0, theta1=0, theta2=180, color="#1e3a8a", linewidth=3, zorder=1))
    ax_sat.add_patch(patches.Circle((3.0, -4.0), 3.48, facecolor="#eff6ff", zorder=0)) # Continent schématique
    
    # Station fixe au sol (La parabole à x=3.0, y=0.95)
    ax_sat.plot([3.0, 3.0], [0.95, 1.1], color="black", linewidth=2, zorder=2)
    ax_sat.add_patch(patches.Arc((3.0, 1.1), 0.25, 0.2, angle=90, theta1=0, theta2=180, color="#475569", linewidth=2, zorder=3)) # Coupelle
    ax_sat.text(3.0, 0.7, "Station Sol", fontsize=8, color="#1e293b", weight="bold", ha="center")
    
    # Ligne d'orbite géostationnaire en pointillés (haute altitude y=2.6)
    ax_sat.plot([0.5, 5.5], [2.6, 2.6], color="#cbd5e1", linewidth=1.5, linestyle="--", zorder=1)
    
    # DESSIN DU SATELLITE MOBILE REALISTE (Rectangle central + deux panneaux rectangulaires)
    ax_sat.add_patch(patches.Rectangle((pos_satellite_x - 0.15, 2.5), 0.3, 0.2, facecolor="#475569", edgecolor="black", zorder=4)) # Corps
    ax_sat.add_patch(patches.Rectangle((pos_satellite_x - 0.75, 2.55), 0.5, 0.1, facecolor="#38bdf8", edgecolor="black", zorder=3)) # Panneau gauche
    ax_sat.add_patch(patches.Rectangle((pos_satellite_x + 0.25, 2.55), 0.5, 0.1, facecolor="#38bdf8", edgecolor="black", zorder=3)) # Panneau droit
    
    # Logique de liaison descendante synchrone
    if np.abs(pos_satellite_x - 3.0) <= 0.05:
        # Alignement géostationnaire parfait sur la parabole fixe
        ax_sat.plot([3.0, 3.0], [2.5, 1.2], color="#ef4444", linewidth=2.5, linestyle=":", zorder=2) # Faisceau actif
        # Ombrage du cône de couverture au sol
        ax_sat.add_patch(patches.Polygon([[3.0, 2.5], [2.0, 0.96], [4.0, 0.96]], facecolor="#fef08a", alpha=0.3, zorder=0))
        lbl_sat_info = "Pointage aligné à 100% ! Liaison hyperfréquence verrouillée. Versement des flux de données nominal."
    else:
        # Dérive ou désalignement orbital
        ax_sat.plot([pos_satellite_x, pos_satellite_x], [2.5, 1.2], color="#94a3b8", linewidth=1.5, linestyle=":", zorder=2)
        ax_sat.add_patch(patches.Polygon([[pos_satellite_x, 2.5], [pos_satellite_x - 1.0, 0.96], [pos_satellite_x + 1.0, 0.96]], facecolor="#f1f5f9", alpha=0.2, zorder=0))
        lbl_sat_info = f"Désalignement orbital détecté à {np.abs(pos_satellite_x - 3.0)*100:.0f} km de dérive. Signal atténué sur la station sol."

    ax_sat.set_xlim(0.5, 5.5)
    ax_sat.set_ylim(0.4, 3.0)
    ax_sat.axis("off")
    st.pyplot(fig_sat)
    plt.close(fig_sat)
    
    st.info(lbl_sat_info)



    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 6 ---
    afficher_atelier_satellite(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    case_certif_tel6 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 6.", key="check_certif_tel6_final", disabled=verrou_at6)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_tel6_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique
            score_q6 = 0.0
            if "ordre_quiz_tab6_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel6_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q6 += 1.0

            # B. Correction de la Synthèse
            score_t6 = 0.0
            if "champs_telecom6_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom6_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"trous_tel6_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t6 += 1.0

            st.session_state.score_suite6_tel_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_tel_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_telecom = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab6_telecom", False):
        scr1_tel6 = st.session_state.get("score_suite6_tel_p1", 0.0)
        scr2_tel6 = st.session_state.get("score_suite6_tel_p2", 0.0)
        tot_s_tel6 = st.session_state.get("score_final_suite6_telecom", 0.0)
        timestamp_tel6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 6 SATELLITE SCELLÉ | Note de session : {tot_s_tel6:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Reseau Satellite - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 6 : Analyse des liaisons orbitales géostationnaires et répéteurs transpondeurs</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #475569;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s_tel6:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab6_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel6_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel6 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom6_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom6_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel6_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel6 = preparer_nom_fichier("Rapport_Reseau_Satellite").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_tel6,
            file_name=nom_fichier_html_tel6,
            mime="text/html",
            use_container_width=True
        )



with tab7:
    st.header("Le Réseau Sans Fil Local : Le Wi-Fi")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 7 ---
    if "suite_verrouille_tab7_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab7_telecom = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_telecom

    if "inc_local_tel7" not in st.session_state:
        st.session_state.inc_local_tel7 = 0

    # --- HISTORIQUE ET CAHIER DES CHARGES : HEDY LAMARR ET LE 802.11 ---

    try: st.image("Hedy_Lamarr.jpg", caption="Hedy Lamarr", width= 250) # Réutilisation ou témoin
    except Exception: st.warning("Fichier d'illustration indisponible.")
        
    st.subheader("Du secret militaire au grand débit : L'héritage d'Hedy Lamarr")
    st.write(
        "**L'Invention :** Pendant la Seconde Guerre mondiale, la célèbre actrice hollywoodienne et inventrice **Hedy Lamarr**, "
        "révoltée par les torpilles alliées détournées par les signaux radio allemands, conçoit un système "
        "révolutionnaire de **commutation de fréquences** (étalement de spectre par saut de fréquence) . "
        "En synchronisant l'émetteur et le récepteur sur des changements constants de canaux, le signal devenait impossible à brouiller. "
        "Ce principe militaire secret est aujourd'hui le fondement technologique absolu du Wi-Fi, du Bluetooth et du GPS .\n\n"
        "**Fonctionnement extrêmement détaillé :** Le Wi-Fi (norme internationale IEEE **802.11**) permet de déployer un réseau local "
        "haut débit sans fil dans un rayon de quelques dizaines de mètres. Il utilise des ondes radio de type **hyperfréquences** "
        "réparties sur deux bandes spectrales complémentaires :\n"
        "* **La bande des 2,4 GHz :** Plus ancienne, elle offre une excellente portée et traverse mieux les obstacles, mais son débit "
        "est plus faible et elle souffre des interférences des micro-ondes ou des appareils voisins.\n"
        "* **La bande des 5 GHz :** Plus moderne, elle offre des débits binaires colossaux (plusieurs centaines de **Mbps**), "
        "mais sa longueur d'onde très courte absorbe l'énergie au moindre obstacle : sa portée est réduite et elle est fortement atténuée par les cloisons.\n\n"
        "L'onde se propage en ligne droite. Lorsqu'elle rencontre un mur en béton armé, une partie de son énergie est réfléchie, "
        "mais une immense partie est absorbée par les structures métalliques et l'humidité du matériau, provoquant une chute "
        "brutale de la puissance du signal et du débit utile de réception."
    )

    st.divider()

    # --- LABORATOIRE INTERACTIF : ATTÉNUATION ET OBSTACLES ---
    st.subheader("Laboratoire de métrologie d'atténuation hertzienne avancée")
    st.write(
        "Modifiez les curseurs pour configurer l'environnement architectural de test. "
        "Déplacez la borne Wi-Fi à l'intérieur de son local technique fermé et déplacez le smartphone "
        "à l'extérieur pour analyser l'atténuation du signal ($dB$) et la vitesse de transfert brute ($Mbps$)."
    )

    # 1. PARAMÉTRAGE INTERACTIF ET COUPLAGE SUR TROIS COLONNES
    c_phys1, c_param2, c_phys3 = st.columns([0.3, 0.4, 0.3])
    
    with c_phys1:
        pos_box_x = st.slider("Position de la borne Wi-Fi (m) :", min_value=0.2, max_value=2.2, value=1.2, step=0.1, key="slide_box_v3_final")
        pos_smart_x = st.slider("Position du Smartphone externe (m) :", min_value=3.2, max_value=6.2, value=4.8, step=0.1, key="slide_smart_v3_final")
    
    with c_param2:
        materiau_cloison = st.selectbox(
            "Sélectionner le matériau de la cloison intermédiaire :",
            options=[
                "Vitrage simple en PVC (Diélectrique mince)",
                "Double vitrage renforcé (Verre + Gaz Argon)",
                "Cloison alvéolaire en placo / plâtre",
                "Panneau de bois massif / Chêne",
                "Mur en briques creuses de terre cuite",
                "Mur porteur en béton de structure",
                "Béton armé avec ferraillage croisé (Cage de Faraday)",
                "Plaque d'aluminium pur (Feuille miroir)",
                "Blindage en acier de forte nuance"
            ],
            key="select_materiau_wifi_v3"
        )
        
    with c_phys3:
        epaisseur_cm = st.slider("Choisir l'épaisseur de la cloison (cm) :", min_value=1, max_value=50, value=15, step=1, key="slide_epaisseur_wifi_v3")

    # 2. CONFIGURATION DES COEFFICIENTS D'ABSORPTION ET DE RÉFLEXION ÉLECTROMAGNÉTIQUE
    if "PVC" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 0.08, "#38bdf8", "uni"
        debit_max, nom_loi = 600, "Réfraction fluide à travers un polymère diélectrique."
    elif "Double vitrage" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 0.25, "#7dd3fc", "double"
        debit_max, nom_loi = 540, "Double réflexion vitreuse avec atténuation par le gaz interne."
    elif "placo" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 0.35, "#e2e8f0", "uni"
        debit_max, nom_loi = 500, "Faible perte par absorption diélectrique sèche dans le plâtre."
    elif "bois" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 0.60, "#b45309", "bois"
        debit_max, nom_loi = 450, "Pertes moyennes causées par l'humidité naturelle des fibres de cellulose."
    elif "briques" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 0.95, "#f97316", "brique"
        debit_max, nom_loi = 380, "Multi-réflexions et piégeage de l'onde dans les alvéoles d'argile."
    elif "béton de structure" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 2.10, "#94a3b8", "uni"
        debit_max, nom_loi = 120, "Forte atténuation par conduction ohmique dans le ciment hydraté."
    elif "Béton armé" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 3.20, "#475569", "ferraille"
        debit_max, nom_loi = 45, "Absorption sévère de l'eau liée doublée d'une diffraction par la maille d'acier."
    elif "aluminium" in materiau_cloison:
        att_par_cm, color_mur, texture_type = 8.50, "#cbd5e1", "miroir"
        debit_max, nom_loi = 2, "Réflexion quasi-totale des ondes de surface par courants de Foucault."
    else: # Acier blindé
        att_par_cm, color_mur, texture_type = 15.0, "#0f172a", "acier"
        debit_max, nom_loi = 0, "Atténuation exponentielle instantanée par effet de peau métallique."

    # Calcul mathématique rigoureux de l'affaiblissement global (Beer-Lambert cumulé)
    attenu_totale_db = round(float(att_par_cm * epaisseur_cm), 1)
    
    # Établissement de la puissance résiduelle du signal (Correction syntaxe)
    if attenu_totale_db < 8.0:
        debit_base, color_onde_ext, style_line, statut_wifi = debit_max, "#22c55e", "-", "Excellent"
    elif attenu_totale_db < 22.0:
        debit_base, color_onde_ext, style_line, statut_wifi = debit_max * 0.55, "#eab308", "-", "Atténué (Moyen)"
    elif attenu_totale_db < 40.0:
        debit_base, color_onde_ext, style_line, statut_wifi = debit_max * 0.15, "#f97316", "--", "Très Faible"
    else:
        debit_base, color_onde_ext, style_line, statut_wifi = 0.0, "#ef4444", ":", "Hors de portée (Coupé)"

    # Intégration de l'atténuation géométrique en espace libre liée à la position du smartphone
    distance_totale_m = pos_smart_x - pos_box_x
    debit_final_mbps = max(0, int(debit_base * (1.0 - (distance_totale_m / 6.5) * 0.45)))

    # 3. MOTEUR VECTORIEL INTERACTIF (MATPLOTLIB)
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_wf, ax_wf = plt.subplots(figsize=(7, 3.8), facecolor="white")
    ax_wf.set_facecolor("white")
    
    # Sol et plafond de la structure immobilière
    ax_wf.plot([0.0, 6.8], [0.1, 0.1], color="#0f172a", linewidth=3, zorder=2)
    ax_wf.plot([0.0, 6.8], [3.1, 3.1], color="#0f172a", linewidth=1.5, zorder=2)
    
    # A. LOCAL ÉMETTEUR FERMÉ (Cube de confinement étanche à gauche de x=0.1 à x=2.5)
    ax_wf.plot([0.1, 0.1], [0.1, 3.1], color="#475569", linewidth=4, zorder=2) # Mur du fond
    ax_wf.plot([0.1, 2.5], [2.7, 2.7], color="#475569", linewidth=4, zorder=2) # Plafond technique interne
    ax_wf.text(1.3, 2.85, "Local Émetteur (Clos)", fontsize=8, color="#475569", weight="bold", ha="center")
    
    # B. APPAREIL ÉMETTEUR (Borne Wi-Fi active posée au sol à y=0.1)
    ax_wf.add_patch(patches.Rectangle((pos_box_x - 0.12, 0.1), 0.24, 0.4, facecolor="#0f172a", edgecolor="black", zorder=5))
    ax_wf.plot([pos_box_x, pos_box_x], [0.5, 0.85], color="black", linewidth=2, zorder=5) # Antenne omnidirectionnelle
    ax_wf.add_patch(patches.Circle((pos_box_x, 0.85), 0.03, facecolor="#22c55e", zorder=6)) # Diode de synchronisation
    
    # Ondes circulaires intérieures (Zone verte libre de champ)
    for r_int in [0.4, 0.8, 1.2, 1.7]:
        ax_wf.add_patch(patches.Arc((pos_box_x, 0.85), r_int*2, r_int*2, angle=0, theta1=-90, theta2=90, color="#3b82f6", linewidth=1.2, alpha=0.4, zorder=1))

    # C. CLOISON AVEC ÉPAISSEUR GÉOMÉTRIQUE RÉELLE ET TEXTURE (Centrée sur x=2.5)
    # Calibrage graphique : 50 cm d'épaisseur réelle = 0.5 unité graphique sur l'axe X
    largeur_mur_graphique = (epaisseur_cm / 50.0) * 0.5
    x_gauche_mur = 2.5 - (largeur_mur_graphique / 2.0)
    
    ax_wf.add_patch(patches.Rectangle((x_gauche_mur, 0.1), largeur_mur_graphique, 2.6, facecolor=color_mur, edgecolor="black", linewidth=1.2, zorder=3))
    ax_wf.text(2.5, 2.85, f"Cloison\n{epaisseur_cm} cm", fontsize=8, color="#0f172a", weight="bold", ha="center")
    
    # Injection des textures internes réalistes
    if texture_type == "ferraille" and largeur_mur_graphique > 0.04:
        # Treillis métallique croisé anti-ondes
        for y_mesh in np.linspace(0.25, 2.45, 6):
            ax_wf.plot([x_gauche_mur, x_gauche_mur + largeur_mur_graphique], [y_mesh, y_mesh], color="#0f172a", linewidth=1.2, zorder=4)
        ax_wf.plot([2.5, 2.5], [0.1, 2.6], color="#0f172a", linewidth=1.2, zorder=4)
    elif texture_type == "double":
        # Ligne d'air isolante interne du double vitrage
        ax_wf.plot([2.5, 2.5], [0.1, 2.6], color="white", linewidth=1.5, zorder=4)
    elif texture_type == "brique":
        # Lignes d'alvéoles de l'argile cuite
        for x_b in np.linspace(x_gauche_mur + 0.02, x_gauche_mur + largeur_mur_graphique - 0.02, 3):
            ax_wf.plot([x_b, x_b], [0.1, 2.6], color="#c2410c", linewidth=0.8, linestyle=":", zorder=4)

    # D. ZONE EXTÉRIEURE DE RÉCEPTION ET SMARTPHONE MOBILE (À droite de la cloison)
    ax_wf.add_patch(patches.Rectangle((2.5 + (largeur_mur_graphique/2.0), 0.1), 4.2 - (largeur_mur_graphique/2.0), 2.6, facecolor="#f8fafc", zorder=1))
    ax_wf.text(4.8, 2.85, "Espace Extérieur Libre", fontsize=8, color="#475569", weight="bold", ha="center")
    
    # Dessin ultra-réaliste du Smartphone mobile de l'élève (Rectangle vertical à x=pos_smart_x, y=0.85)
    y_smart = 0.85
    ax_wf.add_patch(patches.Rectangle((pos_smart_x - 0.12, y_smart - 0.22), 0.24, 0.44, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=5)) # Châssis métallique
    # Écran LCD rétroéclairé s'allumant si un signal passe
    color_ecran_pc = "#38bdf8" if debit_final_mbps > 0 else "#64748b"
    ax_wf.add_patch(patches.Rectangle((pos_smart_x - 0.09, y_smart - 0.17), 0.18, 0.34, facecolor=color_ecran_pc, zorder=5))
    # Encoche ou haut-parleur haut
    ax_wf.plot([pos_smart_x - 0.03, pos_smart_x + 0.03], [y_smart + 0.19, y_smart + 0.19], color="white", linewidth=1.5, zorder=6)
    ax_wf.text(pos_smart_x, y_smart - 0.4, f"Smartphone\n(x = {pos_smart_x:.1f} m)", fontsize=7, color="#0f172a", weight="bold", ha="center")

    # E. RENDU CINÉMATIQUE DU FAISCEAU D'ONDES ATTÉNUÉ
    if debit_final_mbps > 0:
        # Tracé des arcs d'ondes atténués se propageant et enveloppant le smartphone
        rayon_vers_smart = pos_smart_x - pos_box_x
        ax_wf.add_patch(patches.Arc((pos_box_x, 0.85), rayon_vers_smart * 2, rayon_vers_smart * 2, angle=0, theta1=-35, theta2=35, color=color_onde_ext, linewidth=2.0, linestyle=style_line, zorder=2))
        ax_wf.add_patch(patches.Arc((pos_box_x, 0.85), (rayon_vers_smart + 0.5) * 2, (rayon_vers_smart + 0.5) * 2, angle=0, theta1=-35, theta2=35, color=color_onde_ext, linewidth=1.5, linestyle=style_line, zorder=2))
        msg_resultat = f"LIAISON ÉTABLIE (Statut : {statut_wifi}) | Atténuation de la cloison : -{attenu_totale_db:.1f} dB. Débit reçu par le smartphone : {debit_final_mbps} Mbps."
        type_box_streamlit = "success"
    else:
        ax_wf.arrow(2.3, 1.2, -0.4, 0.3, head_width=0.08, head_length=0.08, fc="#ef4444", ec="#ef4444", linewidth=2.5, zorder=5)
        msg_resultat = f"RUPTURE DE FLUX SPÉCIFIQUEMENT LIÉE À L'ISOLATION | Perte critique : -{attenu_totale_db:.1f} dB (Seuil d'extinction de -40 dB franchi). Débit capté : 0 Mbps."
        type_box_streamlit = "error"

    # Habillage de la figure Matplotlib
    ax_wf.set_xlim(0, 6.8)
    ax_wf.set_ylim(-0.2, 3.3)
    ax_wf.axis("off")
    
    # Rendu à l'écran et fermeture de l'objet graphique
    st.pyplot(fig_wf)
    plt.close(fig_wf)
    
    # 4. EXPERTISES PHYSICO-CHIMIQUES DES FLUX SOUS L'ÉCRAN
    if type_box_streamlit == "success":
        st.success(f"**Données du banc d'essai RF :** {msg_resultat} \n\n*Analyse comportementale :* {nom_loi}")
    else:
        st.error(f"**Données du banc d'essai RF :** {msg_resultat} \n\n*Analyse comportementale :* {nom_loi}")

   
    st.divider()
    col71, col72 = st.columns(2)

    with col71: 
    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ---
        st.write("**La BD humoristique textuelle : Le coup de génie d'Hedy**")
        st.info(
            "**Case 1 (Caricature d'Hedy Lamarr) :** Hedy Lamarr, en robe de soirée hollywoodienne scintillante, dessine des plans "
            "techniques complexes sur un coin de table basse : 'Si on fait sauter les fréquences radio d'une note à l'autre "
            "comme sur un piano mécanique, les navires de guerre ennemis ne pourront jamais intercepter nos commandes !'.\n\n"
            "**Case 2 (Les militaires perplexes) :** Des généraux de l'armée en uniforme regardent le brevet en haussant les sourcils : "
            "'Une actrice de cinéma qui veut guider des torpilles avec des rouleaux de piano en carton ? Renvoyez-la sur ses plateaux de tournage !'. "
            "Le brevet est classé secret défense.\n\n"
            "**Case 3 (Le calvaire du salon moderne) :** Cinquante ans plus tard, un utilisateur en sueur agite son smartphone au milieu de son salon "
            "portant un gros canapé : 'Mais pourquoi ma vidéo coupe dès que je vais dans la cuisine ?! Ma box est juste de l'autre côté !'.\n\n"
            "**Case 4 (La dure loi du béton) :** Les molécules du mur en béton armé rigolent en se tenant les bras : "
            "'Désolé le smartphone, mais tes ondes courtes à 5 GHz ne passeront pas à travers nous ! On absorbe tout ! Rapproche ta Box "
            "ou passe en 2,4 GHz !'."
        )

    with col72:
        try: st.image("caricature_wifi.jpg", caption="WIFI")
        except Exception: st.warning("Fichier d'illustration indisponible.")



        
    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 7 ---
    afficher_atelier_wifi(verrouille=verrou_at7)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")
    case_certif_tel7 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 7.", key="check_certif_tel7_final", disabled=verrou_at7)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_tel7_official", use_container_width=True, disabled=verrou_at7):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel7: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique
            score_q7 = 0.0
            if "ordre_quiz_tab7_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab7_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel7_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q7 += 1.0

            # B. Correction de la Synthèse
            score_t7 = 0.0
            if "champs_telecom7_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom7_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = st.session_state.get(f"trous_tel7_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t7 += 1.0

            st.session_state.score_suite7_tel_p1 = round(float(score_q7), 1)
            st.session_state.score_suite7_tel_p2 = round(float(score_t7), 1)

            # Calcul et enregistrement de la note globale de l'Atelier 7 sur 20 points
            st.session_state.score_final_suite7_telecom = round(float(score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 7 ---
    if st.session_state.get("suite_verrouille_tab7_telecom", False):
        scr1_tel7 = st.session_state.get("score_suite7_tel_p1", 0.0)
        scr2_tel7 = st.session_state.get("score_suite7_tel_p2", 0.0)
        tot_s_tel7 = st.session_state.get("score_final_suite7_telecom", 0.0)
        timestamp_tel7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 7 WI-FI SCELLÉ | Note de session : {tot_s_tel7:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Wi-Fi - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 7 : Analyse des liaisons Wi-Fi locales, bandes spectrales et atténuation des cloisons</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel7:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #16a34a;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel7:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel7:.1f} / 10</strong><br>
                Note Totale de l'Atelier 7 : <strong>{tot_s_tel7:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab7_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel7_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel7 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom7_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom7_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel7_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel7 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel7 = preparer_nom_fichier("Rapport_Wifi").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 7 (.html)",
            data=html_export_tel7,
            file_name=nom_fichier_html_tel7,
            mime="text/html",
            use_container_width=True
        )


with tab8:
    st.header("Le Réseau Personnel Sans Fil : Le Bluetooth")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 8 ---
    if "suite_verrouille_tab8_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab8_telecom = False
    verrou_at8 = st.session_state.suite_verrouille_tab8_telecom

    if "inc_local_tel8" not in st.session_state:
        st.session_state.inc_local_tel8 = 0

    col_g8, col_im_8, col_dessin_8 = st.columns(3)

    with col_g8:     
        try: st.image("caricature_roi_bluetooth.jpg", caption="Harald Gormsson, dit Harald à la Dent bleue", width=500)
        except Exception: st.warning("Fichier d'illustration indisponible.")
    with col_im_8:       
        try: st.image("blutho.jpg", caption="origine du symbole", width= 500) # Réutilisation ou témoin
        except Exception: st.warning("Fichier d'illustration indisponible.")
    with col_dessin_8:
        try: st.image("porte_bluetooth.jpg", caption="portée théorique", width= 500) # Réutilisation ou témoin
        except Exception: st.warning("Fichier d'illustration indisponible.")


    # --- HISTORIQUE ET TECHNIQUE : HARALD BLATAND ET LE SÉCURISATION ---
    st.subheader("L'unification des périphériques : De l'histoire scandinave aux ondes ISM")
    st.write(
        "**L'Invention :** En 1994, les ingénieurs de la firme suédoise Ericsson cherchent une solution sans fil pour remplacer "
        "les câbles reliant les ordinateurs aux périphériques. En hommage au roi viking **Harald Blåtand** (« à la dent bleue ») "
        "qui avait unifié les tribus scandinaves au Xe siècle, ils baptisent cette technologie **Bluetooth** car elle a pour vocation "
        "d'unifier tous les appareils de communication électroniques environnants. Son logo officiel est la superposition directe "
        "des runes vikings de ses initiales (H et B).\n\n"
        "**Fonctionnement extrêmement détaillé :** Le Bluetooth opère dans la bande de fréquences industrielles, scientifiques et médicales "
        "**(ISM) à 2,4 GHz**. Conçu pour créer des réseaux personnels microscopiques à très courte portée appelés **piconets**, il autorise "
        "la connexion d'un équipement maître (ex: un smartphone) avec un maximum de 7 équipements esclaves (ex: des écouteurs).\n"
        "Pour éviter de saturer la bande hertzienne et résister au piratage, le Bluetooth s'appuie sur la technologie **FHSS** : "
        "le signal change de canal radio de façon aléatoire **1600 fois par seconde** sur 79 canaux distincts. "
        "La qualité de la liaison est surveillée en continu par l'indicateur **RSSI** (exprimé en dBm). Plus l'appareil s'éloigne, "
        "plus la puissance chute, entraînant une coupure automatique dès que le seuil de sensibilité est franchi."
    )

    st.divider()

    # --- LABORATOIRE INTERACTIF : APPAIRAGE ET COUPLAGE RSSI ---
    st.subheader("Laboratoire de métrologie WPAN : Portée et indicateur RSSI")
    st.write(
        "Modifiez le curseur pour simuler l'éloignement du smartphone par rapport à son périphérique récepteur. "
        "Sélectionnez le type d'appareil esclave pour observer la variation en temps réel de la puissance RSSI (dBm) et l'état d'appairage."
    )

    # Paramètres interactifs
    type_peripherique = st.selectbox("Sélectionner l'appareil esclave à connecter :", options=["Écouteurs stéréo sans fil (Profil Audio A2DP)", "Montre connectée Fitness (Profil Basse Énergie BLE)", "Enceinte nomade de salon (Profil Audio Fort Débit)"], key="select_periph_bt")
    distance_bt_m = st.slider("Ajuster la distance séparant les deux appareils (mètres) :", min_value=0.5, max_value=15.0, value=3.0, step=0.5, key="slide_dist_bt")

    # Calcul rigoureux du signal RSSI d'école (dBm décroissant)
    # Puissance initiale à 0.5m = -40 dBm, atténuation logarithmique liée à la distance
    rssi_calcule = -40.0 - (20.0 * np.log10(distance_bt_m))
    rssi_calcule = round(max(-100.0, rssi_calcule), 1)

    # Rendu graphique Matplotlib de la liaison Bluetooth
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_bt, ax_bt = plt.subplots(figsize=(6.8, 3.2), facecolor="white")
    ax_bt.set_facecolor("white")
    
    # Sol fixe d'expérimentation
    ax_bt.plot([0.0, 8.0], [0.2, 0.2], color="#0f172a", linewidth=2.5)
    
    # 1. Dessin de l'appareil MAÎTRE fixe à gauche (Smartphone à x=1.0, y=0.8)
    ax_bt.add_patch(patches.Rectangle((0.8, 0.5), 0.4, 0.7, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
    ax_bt.add_patch(patches.Rectangle((0.84, 0.56), 0.32, 0.58, facecolor="#38bdf8", zorder=4)) # Écran
    # Logo Bluetooth runique bleu sur l'écran
    ax_bt.plot([1.0, 1.0], [0.75, 0.95], color="blue", linewidth=1.5, zorder=5)
    ax_bt.plot([1.0, 1.08, 0.92, 1.0, 1.08, 0.92], [0.95, 0.9, 0.8, 0.75, 0.85, 0.9], color="blue", linewidth=1.5, zorder=5)
    ax_bt.text(1.0, 1.35, "Smartphone\n(Maître)", fontsize=8, color="#0f172a", weight="bold", ha="center")
    
    # 2. Dessin de l'appareil ESCLAVE mobile à droite (x dépendant du curseur de distance)
    # Mise à l'échelle graphique de la distance : 15 mètres max = coordonnée x=6.0
    x_esclave = 1.2 + (distance_bt_m / 15.0) * 4.8
    
    if "Écouteurs" in type_peripherique:
        ax_bt.add_patch(patches.Circle((x_esclave - 0.1, 0.8), 0.08, facecolor="#475569", zorder=3))
        ax_bt.add_patch(patches.Circle((x_esclave + 0.1, 0.8), 0.08, facecolor="#475569", zorder=3))
        ax_bt.plot([x_esclave - 0.1, x_esclave + 0.1], [0.85, 0.85], color="#475569", linewidth=2, zorder=3)
        nom_txt = "Écouteurs"
    elif "Montre" in type_peripherique:
        ax_bt.add_patch(patches.Rectangle((x_esclave - 0.1, 0.7), 0.2, 0.2, facecolor="#10b981", zorder=3)) # Cadran
        ax_bt.plot([x_esclave, x_esclave], [0.5, 1.1], color="#334155", linewidth=4, zorder=2) # Bracelet
        nom_txt = "Montre BLE"
    else:
        ax_bt.add_patch(patches.Rectangle((x_esclave - 0.15, 0.4), 0.3, 0.6, facecolor="#ca8a04", zorder=3)) # Enceinte
        ax_bt.add_patch(patches.Circle((x_esclave, 0.6), 0.1, facecolor="black", zorder=4)) # Haut-parleur
        nom_txt = "Enceinte"
        
    ax_bt.text(x_esclave, 1.35, f"{nom_txt}\n(Esclave)", fontsize=8, color="#0f172a", weight="bold", ha="center")

    # 3. DÉTERMINATION DYNAMIQUE DE L'ÉTAT DU PICONET
    if distance_bt_m <= 10.0:
        # Appairage actif : Ondes de couplage représentées en bleu continu
        color_bt_link = "#2563eb"
        style_bt_link = "-"
        ax_bt.plot([1.2, x_esclave - 0.15], [0.85, 0.85], color="#2563eb", linewidth=2, linestyle=":", zorder=1)
        # Petits arcs d'ondes de couplage
        ax_bt.add_patch(patches.Arc(((1.2 + x_esclave)/2, 0.85), 0.4, 0.4, angle=0, theta1=0, theta2=360, color="#2563eb", linewidth=1.2))
        msg_bt_status = f"APPAIRAGE EN COURS | Force du champ RSSI : {rssi_calcule} dBm. Statut : Connecté."
        type_box_bt = "success"
    else:
        # Distance excessive : Rupture de lien, ondes coupées rouges
        color_bt_link = "#ef4444"
        style_bt_link = ":"
        msg_bt_status = f"LIAISON IMPOSSIBLE | RSSI critique : {rssi_calcule} dBm (Limite de sensibilité de -85 dBm franchie). Périphérique déconnecté."
        type_box_bt = "error"

    # Habillage final
    ax_bt.set_xlim(0, 7.0)
    ax_bt.set_ylim(0, 1.8)
    ax_bt.axis("off")
    st.pyplot(fig_bt)
    plt.close(fig_bt)
    
    # Affichage de la boîte de statut
    if type_box_bt == "success":
        st.success(msg_bt_status)
    else:
        st.error(msg_bt_status)

    st.divider()
    col81, col82 = st.columns(2)

    with col81:     
    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ---
        st.write("**La BD humoristique textuelle : L'alliance des runes et de la dent bleue**")
        st.info(
            "**Case 1 (Caricature du Roi Harald) :** Le roi viking Harald Blåtand, une énorme chope de bière à la main, "
            "saute sur la table de banquet : 'Moi, Harald, j'ai unifié le Danemark et la Norvège sous une seule bannière !'. "
            "Un conseiller remarque : 'Majesté, vous avez une dent gâtée toute bleue au fond de la bouche...'.\n\n"
            "**Case 2 (Le casse-tête des fils d'Ericsson) :** Mille ans plus tard, un ingénieur suédois s'emmêle les pieds "
            "dans les lourds câbles noirs reliant sa souris, son clavier et son casque à sa tour d'ordinateur : "
            "'Il faut unifier tout ça par les ondes libres ! Créons le protocole Harald-Dent-Bleue !'.\n\n"
            "**Case 3 (L'énigme du code secret) :** Un utilisateur tente d'appairer ses écouteurs en tapant un code PIN erroné. "
            "Le smartphone rejette la liaison : 'Code incorrect !'. L'utilisateur s'énerve : 'Mais connecte-toi, "
            "je suis à vingt centimètres !'. Les ondes sautent joyeusement d'un canal à l'autre pour trouver la bonne clé.\n\n"
            "**Case 4 (La barrière des dix mètres) :** L'étudiant s'éloigne de son enceinte de salon en musique pour aller "
            "chercher un verre d'eau. Au dixième mètre, le son commence à saccader : 'Crrr... Bzzz...'. "
            "Le signal RSSI s'effondre au fond du canapé, et la dent bleue lâche prise, plongeant la pièce dans le silence."
        )
    with col82:       
        try: st.image("bd_humourharald.jpg", caption="origine de la dent bleue") # Réutilisation ou témoin
        except Exception: st.warning("Fichier d'illustration indisponible.")


    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 8 ---
    afficher_atelier_bluetooth(verrouille=verrou_at8)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 8")
    case_certif_tel8 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 8.", key="check_certif_tel8_final", disabled=verrou_at8)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8", key="btn_export_tel8_official", use_container_width=True, disabled=verrou_at8):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel8: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique
            score_q8 = 0.0
            if "ordre_quiz_tab8_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab8_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel8_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q8 += 1.0

            # B. Correction de la Synthèse par texte à trous (10 trous -> 10 pts)
            score_t8 = 0.0
            if "champs_telecom8_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom8_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = st.session_state.get(f"trous_tel8_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t8 += 1.0

            # Sauvegarde des résultats et verrouillage officiel de l'Atelier 8
            st.session_state.score_suite8_tel_p1 = round(float(score_q8), 1)
            st.session_state.score_suite8_tel_p2 = round(float(score_t8), 1)
            st.session_state.score_final_suite8_telecom = round(float(score_q8 + score_t8), 1)
            st.session_state.suite_verrouille_tab8_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 8 ---
    if st.session_state.get("suite_verrouille_tab8_telecom", False):
        scr1_tel8 = st.session_state.get("score_suite8_tel_p1", 0.0)
        scr2_tel8 = st.session_state.get("score_suite8_tel_p2", 0.0)
        tot_s_tel8 = st.session_state.get("score_final_suite8_telecom", 0.0)
        timestamp_tel8 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 8 BLUETOOTH SCELLÉ | Note de session : {tot_s_tel8:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel8 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Bluetooth - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 8 : Protocoles WPAN, réseaux piconets et modulation FHSS par sauts de fréquence</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel8:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel8:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel8:.1f} / 10</strong><br>
                Note Totale de l'Atelier 8 : <strong>{tot_s_tel8:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab8_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab8_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel8_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel8 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel8 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom8_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom8_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel8_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel8 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel8 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel8 = preparer_nom_fichier("Rapport_Bluetooth").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 8 (.html)",
            data=html_export_tel8,
            file_name=nom_fichier_html_tel8,
            mime="text/html",
            use_container_width=True
        )

with tab9:
    st.header("L'Infrarouge : La Communication Optique à Courte Portée")
    
    # --- SÉCURITÉ DE L'ONGLET 9 ---
    if "suite_verrouille_tab9_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab9_telecom = False
    verrou_at9 = st.session_state.suite_verrouille_tab9_telecom

    if "inc_local_tel9" not in st.session_state:
        st.session_state.inc_local_tel9 = 0

    col_g9, col_im_9 = st.columns(2)

    with col_g9:     
        try: st.image("William_Herschel .jpg", caption="William Herschel", width=250)
        except Exception: st.warning("Fichier d'illustration indisponible.")
    with col_im_9:       
        try: st.image("ir_temperature.jpg", caption="température en fonction de la couleur", width= 500) # Réutilisation ou témoin
        except Exception: st.warning("Fichier d'illustration indisponible.")

    # --- LE COURS SUR L'INFRAROUGE ---
    st.subheader("La lumière invisible : William Herschel et le spectre thermique")
    st.write(
        "**L'Histoire :** En 1800, l'astronome britannique **William Herschel** souhaite mesurer la chaleur apportée par "
        "chaque couleur de la lumière du Soleil. En faisant passer les rayons à travers un prisme en verre, il place des thermomètres "
        "sur chaque couleur. Par curiosité, il en pose un juste après la couleur rouge, là où il n'y a plus aucune lumière visible. "
        "À sa grande surprise, ce thermomètre affiche la température la plus élevée ! Il vient de découvrir un rayonnement invisible "
        "qu'il nomme 'rayons calorifiques' : les **infrarouges**.\n\n"
        "**Fonctionnement extrêmement détaillé :** L'infrarouge est une onde électromagnétique dont la longueur d'onde "
        "est supérieure à celle de la lumière visible, s'étendant juste au-delà du rouge. Dans les applications grand public "
        "comme les télécommandes, on utilise des **impulsions de lumière infrarouge** :\n"
        "1. **L'émetteur (La Diode LED) :** Lorsque vous pressez une touche, le microcontrôleur convertit l'ordre en une suite de données "
        "binaires. Une diode émettrice LED traduit ces 0 et ces 1 en une série de flashs de lumière invisible ultra-rapides, "
        "généralement modulés à une fréquence de 38 kHz pour éviter les interférences avec la lumière ambiante.\n"
        "2. **Le récepteur (La Photodiode) :** Sur le téléviseur, un capteur photoélectrique reçoit ces flashs de photons, "
        "les reconvertit en un signal électrique binaire, puis exécute l'action demandée (changement de volume, extinction).\n\n"
        "La contrainte physique de cette technologie est absolue : la lumière voyage en ligne droite. Il faut un **alignement optique direct** "
        "parfait. Le moindre corps opaque (une main, un livre, un animal passant dans la pièce) absorbe ou réfléchit le faisceau, "
        "interrompant instantanément le transfert de données."
    )

    st.divider()

    # --- LABORATOIRE INTERACTIF : LIGNE DE VISÉE IR ---
    st.subheader("Laboratoire d'optique géométrique : Alignement et masquage du faisceau")
    st.write(
        "Modifiez le curseur de distance pour éloigner la télécommande du téléviseur. "
        "Activez l'insertion de l'obstacle opaque pour analyser le blocage immédiat du flux de photons infrarouges."
    )

    # Paramètres cinématiques
    dist_ir_m = st.slider("Ajuster la distance entre la télécommande et la télévision (mètres) :", min_value=0.5, max_value=8.0, value=3.5, step=0.5, key="slide_dist_ir")
    obstacle_ir = st.radio("Placer un obstacle opaque au milieu du salon :", options=["Axe optique libre (Ligne de visée directe)", "Obstacle inséré (Une main ou un livre coupe le faisceau)"], index=0, horizontal=True)

    # Rendu graphique vectoriel Matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_ir, ax_ir = plt.subplots(figsize=(6.8, 2.6), facecolor="white")
    ax_ir.set_facecolor("white")
    
    # Sol du salon
    ax_ir.plot([0.0, 7.0], [0.1, 0.1], color="#0f172a", linewidth=2.5)
    
    # Dessin de la Télécommande fixe à gauche (x=0.8, y=0.8)
    ax_ir.add_patch(patches.Rectangle((0.5, 0.5), 0.5, 0.4, facecolor="#1e293b", edgecolor="black", zorder=3)) # Boîtier
    ax_ir.add_patch(patches.Circle((1.0, 0.7), 0.05, facecolor="#94a3b8", zorder=4)) # Diode émettrice LED
    ax_ir.text(0.75, 1.05, "Télécommande", fontsize=8, color="#0f172a", weight="bold", ha="center")
    
    # Calcul de l'emplacement du téléviseur mobile à droite sur l'échelle graphique
    x_tv = 1.4 + (dist_ir_m / 8.0) * 4.8
    ax_ir.add_patch(patches.Rectangle((x_tv, 0.3), 0.15, 0.8, facecolor="#334155", zorder=3)) # Écran TV profil
    ax_ir.add_patch(patches.Rectangle((x_tv - 0.04, 0.6), 0.04, 0.15, facecolor="#38bdf8", zorder=4)) # Lentille réceptrice
    ax_ir.text(x_tv, 1.25, "Téléviseur", fontsize=8, color="#0f172a", weight="bold", ha="center")

    # Placement de l'obstacle géométrique au centre du faisceau
    x_milieu_ir = (1.0 + x_tv) / 2.0
    if "inséré" in obstacle_ir:
        ax_ir.add_patch(patches.Rectangle((x_milieu_ir - 0.08, 0.2), 0.16, 1.1, facecolor="#ef4444", edgecolor="black", zorder=4))
        ax_ir.text(x_milieu_ir, 1.4, "Obstacle Opaque", fontsize=8, color="#ef4444", weight="bold", ha="center")

    # Analyse cinématique des photons
    if "libre" in obstacle_ir:
        # Faisceau vert continu unissant la LED à la lentille
        ax_ir.plot([1.0, x_tv - 0.04], [0.7, 0.7], color="#10b981", linewidth=3, solid_capstyle="round", zorder=2)
        # Petits éclairs de transmission
        ax_ir.plot([x_tv - 0.04, x_tv - 0.04], [0.6, 0.75], color="#10b981", linewidth=1.5)
        msg_ir_status = "LIAISON OPTIQUE ACTIVE | Ligne de visée directe respectée. Les paquets de flashs binaires atteignent le récepteur."
        ir_actif = True
    else:
        # Le faisceau bute contre l'obstacle et s'éteint
        ax_ir.plot([1.0, x_milieu_ir - 0.08], [0.7, 0.7], color="#ef4444", linewidth=3, solid_capstyle="round", zorder=2)
        msg_ir_status = "COUPURE PHYSIQUE ÉTABLIE | La lumière ne contourne pas l'obstacle. Zéro photon reçu par la photodiode."
        ir_actif = False

    # Diode témoin d'état sur la TV
    ax_ir.add_patch(patches.Circle((x_tv + 0.07, 0.4), 0.04, facecolor="#22c55e" if ir_actif else "#64748b", zorder=5))

    ax_ir.set_xlim(0, 7.0)
    ax_ir.set_ylim(0, 1.8)
    ax_ir.axis("off")
    st.pyplot(fig_ir)
    plt.close(fig_ir)
    
    if ir_actif: st.success(msg_ir_status)
    else: st.error(msg_ir_status)


    st.divider()
    
    col9a1, col9a2 = st.columns(2)

    with col9a1:    # --- BANDE DESSINÉE / CARICATURE TEXTUELLE ---
        st.write("**La BD humoristique textuelle : Herschel et le rayon de l'ombre**")
        st.info(
            "**Case 1 (Caricature de William Herschel) :** Herschel fait passer la lumière du Soleil à travers un prisme en verre. "
            "Un arc-en-ciel magnifique se projette sur sa table de labo. Il pose des thermomètres sur le violet, le vert, le rouge... "
            "Et un dernier thermomètre tout à droite dans le noir complet ! 'Voyons si le néant est froid !'.\n\n"
            "**Case 2 (La surprise thermique) :** Herschel regarde le thermomètre posé dans le noir absolu. Le mercure grimpe en flèche, "
            "dépassant toutes les autres couleurs : 'Par tous les saints ! Ça chauffe un max là où on ne voit rien ! "
            "Il y a une lumière secrète sous le rouge !'.\n\n"
            "**Case 3 (La guerre de la télécommande) :** Deux siècles plus tard, un père de famille est affalé dans son canapé, "
            "pointant frénétiquement sa télécommande vers la télévision : 'Mais change de chaîne sacrée machine !'. "
            "Devant la TV, le gros chat de la famille s'est assis bien confortablement, bloquant la lucide réceptrice.\n\n"
            "**Case 4 (La dure loi de l'optique) :** Le chat regarde son maître d'un air dédaigneux : 'Tu peux cliquer tant que tu veux "
            "sur ton plastique humain, mais mes poils absorbent tous tes photons infrarouges ! Si tu veux zapper, "
            "il faudra d'abord me donner des croquettes ou lever le bras !'."
        )
    with col9a2:
        try: st.image("caric_temperature.jpg", caption="température en fonction de la couleur") # Réutilisation ou témoin
        except Exception: st.warning("Fichier d'illustration indisponible.")

        
    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 9 ---
    afficher_atelier_infrarouge(verrouille=verrou_at9)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 9")
    case_certif_tel9 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 9.", key="check_certif_tel9_final", disabled=verrou_at9)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9", key="btn_export_tel9_official", use_container_width=True, disabled=verrou_at9):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel9: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q9 = 0.0
            if "ordre_quiz_tab9_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab9_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel9_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q9 += 1.0

            # B. Correction de la Synthèse (10 trous -> 10 pts)
            score_t9 = 0.0
            if "champs_telecom9_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom9_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"trous_tel9_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t9 += 1.0

            # Enregistrement des notes
            st.session_state.score_suite9_tel_p1 = round(float(score_q9), 1)
            st.session_state.score_suite9_tel_p2 = round(float(score_t9), 1)
            # Calcul et enregistrement de la note globale de l'Atelier 9 sur 20 points
            st.session_state.score_final_suite9_telecom = round(float(score_q9 + score_t9), 1)
            st.session_state.suite_verrouille_tab9_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 9 ---
    if st.session_state.get("suite_verrouille_tab9_telecom", False):
        scr1_tel9 = st.session_state.get("score_suite9_tel_p1", 0.0)
        scr2_tel9 = st.session_state.get("score_suite9_tel_p2", 0.0)
        tot_s_tel9 = st.session_state.get("score_final_suite9_telecom", 0.0)
        timestamp_tel9 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 9 INFRAROUGE SCELLÉ | Note de session : {tot_s_tel9:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel9 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Infrarouge - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 9 : Optique des ondes invisibles, spectre thermique d'Herschel et diodes LED émettrices</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel9}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel9:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #06b6d4;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel9:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel9:.1f} / 10</strong><br>
                Note Totale de l'Atelier 9 : <strong>{tot_s_tel9:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab9_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab9_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel9_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel9 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel9 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom9_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom9_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel9_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel9 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel9 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel9 = preparer_nom_fichier("Rapport_Infrarouge").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 9 (.html)",
            data=html_export_tel9,
            file_name=nom_fichier_html_tel9,
            mime="text/html",
            use_container_width=True
        )

with tab10:
    st.header("Les Brouilleurs d'Onde : Guerre Électronique et Cadre Légal")
    
    # --- DÉCLARATION DU VERROU ET SÉCURITÉ DE L'ATELIER 10 ---
    if "suite_verrouille_tab10_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab10_telecom = False
    verrou_at10 = st.session_state.suite_verrouille_tab10_telecom

    if "inc_local_tel10" not in st.session_state:
        st.session_state.inc_local_tel10 = 0

    try: st.image("brouilleur.jpg", caption="Brouilleurs d'ondes", width= 350) # Réutilisation ou témoin
    except Exception: st.warning("Fichier d'illustration indisponible.")

    # --- LE COURS TECHNIQUE ET CONTEXTE ---
    st.subheader("La saturation du spectre : Le principe du bruit blanc")
    st.write(
        "**Le Principe :** Un brouilleur d'ondes (ou jammer) est un émetteur de radiofréquences conçu pour perturber ou bloquer "
        "les communications entre un émetteur légitime et son récepteur. Contrairement à une idée reçue, il ne coupe pas le signal d'origine, "
        "il fait pire : il inonde l'espace aérien d'un bruit radioélectrique de forte puissance sur la même bande de fréquences.\n\n"
        "**Fonctionnement extrêmement détaillé :** Pour comprendre ce phénomène, on utilise le concept de **Rapport Signal sur Bruit (SNR)**. "
        "Pour décoder une information numérique (les bits), un récepteur (comme un smartphone) doit recevoir un signal utile nettement plus "
        "fort que le bruit de fond ambiant. Lorsque le brouilleur s'active, il génère un signal parasite continu (souvent modulé de façon aléatoire). "
        "Le récepteur capte un flot d'ondes chaotiques : son rapport SNR s'effondre en dessous du seuil critique. "
        "Bien qu'interconnecté à l'antenne-relais ou à la box, l'appareil est incapable de distinguer les données des parasites. C'est l'équivalent "
        "d'essayer de tenir une conversation chuchotée au milieu d'un concert de rock métallurgique.\n\n"
        "**Le Cadre Juridique :** En France, la réglementation encadre strictement ces dispositifs. "
        "La vente, la détention et l'utilisation de brouilleurs par un particulier sont **strictement interdites** et passibles de lourdes sanctions "
        "(amendes et emprisonnement). Seuls l'État, l'armée, et les ministères de la Justice (pour neutraliser les portables introduits en prison) ou de l'Intérieur "
        "disposent de dérogations légales pour l'ordre public ou la sécurité nationale."
    )

    st.divider()

    # --- LABORATOIRE INTERACTIF : SATURATION HERTZIENNE ---
    st.subheader("Laboratoire de guerre électronique : Saturation de spectre et calcul du SNR")
    st.write(
        "Activez l'interrupteur du brouilleur d'ondes et modifiez sa puissance de sortie. "
        "Observez l'effondrement immédiat de l'onde sinusoïdale légitime et la coupure réseau sur le smartphone."
    )

    # Commandes du simulateur
    brouilleur_actif = st.checkbox("Activer l'émetteur de brouillage parasite", value=False, key="check_brouilleur")
    puissance_brouilleur_w = st.slider("Puissance d'émission du bruit blanc (Watts) :", min_value=1, max_value=50, value=10, step=1, disabled=not brouilleur_actif)

    # Rendu graphique Matplotlib de la perturbation
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_br, ax_br = plt.subplots(figsize=(6.5, 3.2), facecolor="white")
    ax_br.set_facecolor("white")
    
    # Sol et structures fixes
    ax_br.plot([0.0, 7.0], [0.2, 0.2], color="black", linewidth=2.5)
    
    # Émetteur légitime (Antenne-relais à gauche x=1.0)
    ax_br.plot([1.0, 1.0], [0.2, 1.8], color="#475569", linewidth=3)
    ax_br.add_patch(patches.Circle((1.0, 1.8), 0.05, facecolor="green"))
    ax_br.text(1.0, 2.0, "Antenne\nLégitime", fontsize=8, color="#1e293b", weight="bold", ha="center")
    
    # Récepteur (Smartphone au centre x=3.5, y=0.6)
    ax_br.add_patch(patches.Rectangle((3.3, 0.3), 0.4, 0.7, facecolor="#1e293b", zorder=3))
    color_ecran = "#38bdf8"
    
    # Brouilleur d'ondes (Pylône d'agression à droite x=6.0, y=0.2)
    ax_br.plot([6.0, 6.0], [0.2, 1.5], color="#ef4444" if brouilleur_actif else "#cbd5e1", linewidth=2.5)
    ax_br.add_patch(patches.RegularPolygon((6.0, 1.5), numVertices=3, radius=0.1, facecolor="#ef4444" if brouilleur_actif else "#cbd5e1"))
    ax_br.text(6.0, 1.75, "Brouilleur\n(Contre-mesure)", fontsize=8, color="#ef4444" if brouilleur_actif else "#64748b", weight="bold", ha="center")

    if not brouilleur_actif:
        # Signal propre et stable (Ondes bleues régulières vers le mobile)
        for r_leg in [0.6, 1.2, 1.9, 2.4]:
            ax_br.add_patch(patches.Arc((1.0, 1.8), r_leg*2, r_leg*2, angle=-45, theta1=-45, theta2=45, color="#3b82f6", linewidth=1.5, linestyle="-"))
        msg_br_info = "Spectre hertzien nominal. Rapport SNR à +22 dB. Communication numérique fluide, débit optimal."
    else:
        # Brouilleur en action : Injection d'un bruit blanc chaotique rouge écrasant
        color_ecran = "#64748b" # Écran éteint par déconnexion
        for r_par in np.linspace(0.4, 2.5, 4):
            ax_br.add_patch(patches.Arc((6.0, 1.5), r_par*2, r_par*2, angle=135, theta1=-60, theta2=60, color="#ef4444", linewidth=2.0, linestyle="--"))
            
        snr_chute = 22.0 - (puissance_brouilleur_w * 0.8)
        if snr_chute > 3.0:
            msg_br_info = f"Perturbation détectée. Rapport SNR dégradé à {snr_chute:.1f} dB. Ralentissement des flux de paquets binaires."
            color_ecran = "#f97316" # Écran orange dégradé
        else:
            msg_br_info = f"Rupture totale ! Rapport SNR négatif ({snr_chute:.1f} dB). Le récepteur ne distingue plus les bits. Échec réseau."

    # Rendu de la dalle du smartphone
    ax_br.add_patch(patches.Rectangle((3.34, 0.36), 0.32, 0.58, facecolor=color_ecran, zorder=4))

    ax_br.set_xlim(0, 7.0)
    ax_br.set_ylim(0, 2.4)
    ax_br.axis("off")
    st.pyplot(fig_br)
    plt.close(fig_br)
    
    if not brouilleur_actif: st.success(msg_br_info)
    else: st.error(msg_br_info)

    st.divider()
    col101, col102= st.columns(2)

    with col101: 
    # --- CARICATURE / BD HUMORISTIQUE TEXTUELLE ---
        st.write("**La BD humoristique textuelle : Le silence des ondes**")
        st.info(
            "**Case 1 (L'amphithéâtre bavard) :** Un professeur désespéré tente de faire son cours sur l'histoire des technologies face à un groupe "
            "d'étudiants dont les smartphones vibrent et clignotent sous les notifications de vidéos et de messages : "
            "'S'il vous plaît ! Écoutez-moi !'. Les téléphones crient en chœur : 'Bliiin ! Dring ! Clic !'.\n\n"
            "**Case 2 (Le plan secret) :** Le professeur, un sourire aux lèvres, sort de sa sacoche une petite boîte noire "
            "munie de quatre antennes en fer : 'Puisque la voix de la science ne passe plus, activons le barrage d'électrons !'. "
            "Il presse l'interrupteur.\n\n"
            "**Case 3 (Le chaos silencieux) :** Instantanément, le brouilleur inonde l'amphithéâtre de micro-ondes parasites invisibles. "
            "Les smartphones des élèves affichent tous une croix rouge sur l'antenne : 'Réseau indisponible... Recherche...'. "
            "Les étudiants s'agitent en levant leur boîtier en l'air : 'Plus de réseau ! Plus de Wi-Fi ! On est coupés du monde !'.\n\n"
            "**Case 4 (Le retour à la réalité) :** Un inspecteur officiel des fréquences enfonce la porte de la pièce "
            "avec un récepteur hertzien de contrôle à la main : 'Halte là ! Émettre un bruit blanc de blocage sans licence est un délit ! "
            "C'est une lourde amende réglementaire !'. Le professeur éteint la boîte en soupirant : 'C'était pourtant le plus beau silence de ma carrière'."
        )
        
    with col102:
        try: st.image("carac_ondes.jpg", caption="Le silence des ondes") # Réutilisation ou témoin
        except Exception: st.warning("Fichier d'illustration indisponible.")
        
    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 10 ---
    afficher_atelier_brouilleurs(verrouille=verrou_at10)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 10")
    case_certif_tel10 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 10.", key="check_certif_tel10_final", disabled=verrou_at10)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 10", key="btn_export_tel10_official", use_container_width=True, disabled=verrou_at10):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel10: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique
            score_q10 = 0.0
            if "ordre_quiz_tab10_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab10_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel10_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q10 += 1.0

            # B. Correction de la Synthèse
            score_t10 = 0.0
            if "champs_telecom10_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom10_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"trous_tel10_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t10 += 1.0

            st.session_state.score_suite10_tel_p1 = round(float(score_q10), 1)
            st.session_state.score_suite10_tel_p2 = round(float(score_t10), 1)
            st.session_state.score_final_suite10_telecom = round(float(score_q10 + score_t10), 1)
            st.session_state.suite_verrouille_tab10_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 10 ---
    if st.session_state.get("suite_verrouille_tab10_telecom", False):
        scr1_tel10 = st.session_state.get("score_suite10_tel_p1", 0.0)
        scr2_tel10 = st.session_state.get("score_suite10_tel_p2", 0.0)
        tot_s_tel10 = st.session_state.get("score_final_suite10_telecom", 0.0)
        timestamp_tel10 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 10 BROUILLEURS D'ONDE SCELLÉ | Note de session : {tot_s_tel10:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel10 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Brouilleurs d'onde - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 10 : Guerre électronique, contre-mesures, spectre de barrage et rapport SNR</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel10}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel10:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #ef4444;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel10:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel10:.1f} / 10</strong><br>
                Note Totale de l'Atelier 10 : <strong>{tot_s_tel10:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab10_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab10_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel10_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel10 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel10 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom10_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom10_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel10_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel10 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel10 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel10 = preparer_nom_fichier("Rapport_Brouilleurs").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 10 (.html)",
            data=html_export_tel10,
            file_name=nom_fichier_html_tel10,
            mime="text/html",
            use_container_width=True
        )

with tab11:
    st.header("Synthèse Globale : Le Voyage Complet de l'Onde")
    
    # --- SÉCURITÉ DE L'ONGLET 11 ---
    if "suite_verrouille_tab11_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab11_telecom = False
    verrou_at11 = st.session_state.suite_verrouille_tab11_telecom

    if "inc_local_tel11" not in st.session_state:
        st.session_state.inc_local_tel11 = 0

    st.subheader("La cinématique d'un appel : De l'antenne locale au cœur de réseau")
    st.write(
        "Votre voix effectue un voyage mixte : elle commence par un saut hertzien dans l'air, "
        "voyage sous terre dans des câbles de fibre optique, puis ressort par une antenne-relais à l'autre bout du réseau."
    )

    st.divider()

    # --- SIMULATEUR INTERACTIF DE TRAJET DE L'ONDE ---
    st.subheader("Banc de métrologie cellulaire : Acheminement du signal")
    
    generation_choisie = st.selectbox(
        "Sélectionner la génération de réseau mobile à tester :",
        options=["Réseau 3G (Fréquences basses - Débit limité)", "Réseau 4G (Haut Débit - Usage standard)", "Réseau 5G (Hyperfréquences - Latence ultra-basse)"],
        key="select_generation_reseau_final"
    )
    
    etape_signal = st.slider(
        "Suivre le parcours du signal (étape par étape) :", 
        min_value=1, max_value=5, value=1, key="slide_etape_reseau_final",
        help="1: Émission Tél A / 2: Liaison Montante / 3: Transit Fibre / 4: Liaison Descendante / 5: Réception Tél B"
    )

    # Étalonnage des variables physiques selon la génération
    if "3G" in generation_choisie:
        f_nom, debit_txt, latence_txt, color_onde = "2.1 GHz", "2 Mbps", "100 ms", "#eab308"
    elif "4G" in generation_choisie:
        f_nom, debit_txt, latence_txt, color_onde = "2.6 GHz", "150 Mbps", "30 ms", "#3b82f6"
    else:
        f_nom, debit_txt, latence_txt, color_onde = "3.5 GHz", "1 Gbps", "1 ms", "#22c55e"

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    fig_cel, ax_cel = plt.subplots(figsize=(7.2, 3.8), facecolor="white")
    ax_cel.set_facecolor("white")
    
    # Ligne de sol terrestre
    ax_cel.plot([0.0, 8.0], [0.5, 0.5], color="#1e293b", linewidth=2.5)
    
    # Équipements fixes
    ax_cel.add_patch(patches.Rectangle((0.4, 0.52), 0.2, 0.4, facecolor="#0f172a", zorder=3))
    ax_cel.add_patch(patches.Rectangle((0.44, 0.56), 0.12, 0.32, facecolor="#38bdf8", zorder=4))
    ax_cel.text(0.5, 1.0, "Téléphone A\n(Émetteur)", fontsize=7, weight="bold", ha="center")
    
    ax_cel.add_patch(patches.Rectangle((7.4, 0.52), 0.2, 0.4, facecolor="#0f172a", zorder=3))
    ax_cel.add_patch(patches.Rectangle((7.44, 0.56), 0.12, 0.32, facecolor="#38bdf8", zorder=4))
    ax_cel.text(7.5, 1.0, "Téléphone B\n(Récepteur)", fontsize=7, weight="bold", ha="center")
    
    ax_cel.plot([2.0, 2.0], [0.5, 2.2], color="#475569", linewidth=2, zorder=2)
    ax_cel.add_patch(patches.RegularPolygon((2.0, 2.2), numVertices=3, radius=0.15, facecolor="#475569"))
    ax_cel.text(2.0, 2.45, "Antenne-Relais A", fontsize=7, weight="bold", ha="center")
    
    ax_cel.plot([6.0, 6.0], [0.5, 2.2], color="#475569", linewidth=2, zorder=2)
    ax_cel.add_patch(patches.RegularPolygon((6.0, 2.2), numVertices=3, radius=0.15, facecolor="#475569"))
    ax_cel.text(6.0, 2.45, "Antenne-Relais B", fontsize=7, weight="bold", ha="center")
    
    ax_cel.plot([2.0, 6.0], [0.1, 0.1], color="#cbd5e1", linewidth=4, linestyle="--", zorder=1)
    ax_cel.text(4.0, 0.2, "Fibre Optique Souterraine", color="#64748b", fontsize=7, ha="center")

    # Logique animée du signal
    if etape_signal == 1:
        ax_cel.add_patch(patches.Circle((0.5, 0.72), 0.05, facecolor="#ef4444", zorder=5))
        msg_etape = "Étape 1 : Le processeur du Téléphone A numérise votre voix."
    elif etape_signal == 2:
        ax_cel.plot([0.5, 2.0], [0.72, 2.2], color=color_onde, linewidth=2.5, linestyle=":", zorder=3)
        ax_cel.add_patch(patches.Circle((2.0, 2.2), 0.06, facecolor="#ef4444", zorder=5))
        msg_etape = f"Étape 2 (Liaison Montante) : Voyage des ondes radio ({f_nom}) vers l'antenne-relais A."
    elif etape_signal == 3:
        ax_cel.plot([2.0, 6.0], [0.1, 0.1], color="#ef4444", linewidth=4, zorder=2)
        msg_etape = "Étape 3 (Cœur de Réseau) : Les photons filent dans la fibre optique sous terre."
    elif etape_signal == 4:
        ax_cel.plot([6.0, 7.5], [2.2, 0.72], color=color_onde, linewidth=2.5, linestyle=":", zorder=3)
        ax_cel.add_patch(patches.Circle((6.0, 2.2), 0.06, facecolor="#ef4444", zorder=5))
        msg_etape = "Étape 4 (Liaison Descendante) : L'antenne-relais B réémet le flux hertzien vers le destinataire."
    else:
        ax_cel.add_patch(patches.Circle((7.5, 0.72), 0.07, facecolor="#22c55e", zorder=5))
        ax_cel.add_patch(patches.Arc((7.5, 0.72), 0.3, 0.3, angle=0, theta1=0, theta2=360, color="#22c55e", linewidth=1.5))
        msg_etape = "Étape 5 : Le Téléphone B reçoit l'onde et restitue le signal audio."

    ax_cel.set_xlim(0, 8.0)
    ax_cel.set_ylim(-0.2, 2.8)
    ax_cel.axis("off")
    st.pyplot(fig_cel)
    plt.close(fig_cel)
    
    st.info(msg_etape)
    st.markdown(f"""
    * Fréquence nominale : **{f_nom}**
    * Vitesse de transfert : **{debit_txt}**
    * Temps de réponse : **{latence_txt}**
    """)

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 11 ---
    afficher_atelier_synthese_reseau(verrouille=verrou_at11)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier Final")
    case_certif_tel11 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 11.", 
        key="check_certif_tel11_final_real", 
        disabled=verrou_at11
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 11", key="btn_export_tel11_official_real", use_container_width=True, disabled=verrou_at11):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel11: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (10 questions -> 10 pts)
            score_q11 = 0.0
            if "ordre_quiz_tab11_telecom_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab11_telecom_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_tel11_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q11 += 1.0

            # B. Correction de la Synthèse par texte à trous (10 trous -> 10 pts)
            score_t11 = 0.0
            if "champs_telecom11_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_telecom11_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = st.session_state.get(f"trous_tel11_{cle}_inst_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t11 += 1.0

            st.session_state.score_suite11_tel_p1 = round(float(score_q11), 1)
            st.session_state.score_suite11_tel_p2 = round(float(score_t11), 1)
            st.session_state.score_final_suite11_telecom = round(float(score_q11 + score_t11), 1)
            st.session_state.suite_verrouille_tab11_telecom = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ DE L'ATELIER 11 ---
    if st.session_state.get("suite_verrouille_tab11_telecom", False):
        scr1_tel11 = st.session_state.get("score_suite11_tel_p1", 0.0)
        scr2_tel11 = st.session_state.get("score_suite11_tel_p2", 0.0)
        tot_s_tel11 = st.session_state.get("score_final_suite11_telecom", 0.0)
        timestamp_tel11 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 11 COMPILÉ SCELLÉ | Note de session : {tot_s_tel11:.1f} / 20")

        n_eleve = st.session_state.get("nom_var", "ELEVE").upper()
        p_eleve = st.session_state.get("prenom_var", "PRENOM").upper()
        c_eleve = st.session_state.get("classe_var", "GROUPE").upper()

        html_export_tel11 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Synthèse Réseau - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Télécommunications</h1>
                <p>Atelier 11 : Synthèse globale de l'acheminement des flux de données</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tel11}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_tel11:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_tel11:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_tel11:.1f} / 10</strong><br>
                Note Totale de l'Atelier 11 : <strong>{tot_s_tel11:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab11_telecom_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab11_telecom_aleatoire, 1):
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_tel11_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tel11 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tel11 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_telecom11_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_telecom11_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"trous_tel11_{cle_variable}_inst_{num}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tel11 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tel11 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tel11 = preparer_nom_fichier("Rapport_Synthese_Reseau").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 11 (.html)",
            data=html_export_tel11,
            file_name=nom_fichier_html_tel11,
            mime="text/html",
            use_container_width=True
        )



























        


                    
