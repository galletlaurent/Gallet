
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
    "Les brouilleurs d'onde"
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
            st.image("premiere_presse.jpg", caption="Combinés et standards téléphoniques anciens", width=180)
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
            st.image("premiere_radio.jpg", caption="Évolution des terminaux portables cellulaires", width=180)
        except Exception:
            st.warning("Illustration en cours de chargement ou fichier 'premiere_radio.jpg' absent du serveur.")

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
                .header-box {{ background-color: #1e293b; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
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




































                    
