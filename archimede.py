# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application Archimède ",
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
st.title("Application Archimède")
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


onglets = st.tabs([
    "Identification",
    "Historique",
    "Définition de la poussée d'Archimède",
    "La flottaison des bateaux",
    "Application dans les différents fluides",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier"
])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]
tab6 = onglets[6] 
tab7 = onglets[7] 


def afficher_atelier_transport_routier(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 7 (Transport routier) sur deux colonnes."""
    import random

    questions_arch7_sources = [
        {"id": "qa7_1", "q": "Pourquoi un camion-citerne chargé d'essence (800 kg/m³) pèse-t-il moins lourd qu'un même camion rempli de lait (1030 kg/m³) à volume égal ?", "options": ["Car l'essence possède une masse volumique inférieure à celle du lait, réduisant le poids de la cargaison", "Car l'essence s'évapore en roulant", "Car le lait annule l'effet de l'apesanteur"], "rep": "Car l'essence possède une masse volumique inférieure à celle du lait, réduisant le poids de la cargaison"},
        {"id": "qa7_2", "q": "Quel système mécanique de cloisonnement interne des citernes limite les mouvements dangereux du liquide lors des freinages ?", "options": ["Les cloisons brise-lames (ou parois déflectrices)", "Les buses Venturi", "Les ballasts de fond"], "rep": "Les cloisons brise-lames (ou parois déflectrices)"},
        {"id": "qa7_3", "q": "Comment une jauge pneumatique à bulle embarquée mesure-t-elle la hauteur de fluide dans la citerne ?", "options": ["En mesurant la pression hydrostatique au fond, qui est directement proportionnelle à la hauteur et à la densité du liquide", "En pesant la citerne avec un ressort", "En comptant le nombre de vibrations du réservoir"], "rep": "En mesurant la pression hydrostatique au fond, qui est directement proportionnelle à la hauteur et à la densité du liquide"},
        {"id": "qa7_4", "q": "Quel instrument de pesage officiel utilise-t-on sur les routes pour contrôler la masse totale d'un poids lourd ?", "options": ["Un pont-bascule de pesage par essieu", "Un densitomètre gradué", "Un dynamomètre portable"], "rep": "Un pont-bascule de pesage par essieu"},
        {"id": "qa7_5", "q": "Quelle est la conséquence physique immédiate sur l'essieu arrière si le liquide se déplace vers l'arrière lors d'une forte accélération ?", "options": ["Le poids apparent sur l'essieu arrière augmente par transfert de masse", "La poussée d'Archimède s'annule", "Le camion se met à flotter"], "rep": "Le poids apparent sur l'essieu arrière augmente par transfert de masse"},
        {"id": "qa7_6", "q": "Pourquoi la réglementation du transport routier impose-t-elle une limite de charge maximale autorisée (PTAC) ?", "options": ["Pour préserver l'adhérence des pneumatiques et éviter la destruction des chaussées et des ponts", "Pour limiter le bruit du moteur", "Pour économiser la réserve de carburant"], "rep": "Pour préserver l'adhérence des pneumatiques et éviter la destruction des chaussées et des ponts"},
        {"id": "qa7_7", "q": "Si une citerne contient un volume d'air important (citerne à moitié vide), le véhicule est qualifié de :", "options": ["Instable (sensible au ballottement du liquide)", "Parfaitement sécurisé", "Aérodynamique"], "rep": "Instable (sensible au ballottement du liquide)"},
        {"id": "qa7_8", "q": "La pression exercée par le liquide sur les parois de la citerne au repos dépend de :", "options": ["La profondeur et la masse volumique du liquide (loi de l'hydrostatique)", "De la vitesse de rotation des roues", "Du diamètre des valves de purge"], "rep": "La profondeur et la masse volumique du liquide (loi de l'hydrostatique)"},
        {"id": "qa7_9", "q": "Quelle unité de pression utilise-t-on couramment sur les manomètres de contrôle des circuits de transport ?", "options": ["Le bar (ou le pascal)", "Le newton", "Le kilogramme"], "rep": "Le bar (ou le pascal)"},
        {"id": "qa7_10", "q": "L'étude dynamique du comportement des fluides en mouvement à l'intérieur d'un réservoir routier relève de :", "options": ["La dynamique des fluides (et des transferts de charges)", "L'hydrostatique pure au repos", "La thermodynamique moléculaire"], "rep": "La dynamique des fluides (et des transferts de charges)"}
    ]

    if "ordre_quiz_tab7_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch7_sources)
        st.session_state.ordre_quiz_tab7_arch_aleatoire = questions_arch7_sources

    champs_mis_a_jour_b7 = [
        ("1. Transporter des liquides par route requiert des camions à .......... étanches.", ["Choisir...", "citerne", "plateau"], "citerne", "arch7_t1"),
        ("2. Calculer le poids de la cargaison exige de connaître la .......... volumique du fluide.", ["Choisir...", "masse", "viscosité"], "masse", "arch7_t2"),
        ("3. Réduire les vagues de liquide lors des arrêts utilise des parois ..........", ["Choisir...", "brise-lames", "étalonnées"], "brise-lames", "arch7_t3"),
        ("4. Une citerne partiellement remplie expose le véhicule à une forte ..........", ["Choisir...", "instabilité", "sécurité"], "instabilité", "arch7_t4"),
        ("5. Suivre la hauteur du produit s'appuie sur un capteur de pression ..........", ["Choisir...", "hydrostatique", "atmosphérique"], "hydrostatique", "arch7_t5"),
        ("6. La charge totale du véhicule est mesurée sur un pont-.......... officiel.", ["Choisir...", "bascule", "régulateur"], "bascule", "arch7_t6"),
        ("7. La pression exercée sur le fond dépend de la .......... du liquide stocké.", ["Choisir...", "profondeur", "vitesse"], "profondeur", "arch7_t7"),
        ("8. L'essence étant moins dense que l'eau, son coefficient rho est ..........", ["Choisir...", "inférieur", "supérieur"], "inférieure", "arch7_t8"),
        ("9. Éviter la surcharge des pneumatiques respecte la limite légale du ..........", ["Choisir...", "PTAC", "FRL"], "PTAC", "arch7_t9"),
        ("10. Ce module achève les ateliers pratiques liés à la mécanique des ..........", ["Choisir...", "fluides", "solides"], "fluides", "arch7_t10")
    ]
    st.session_state.champs_arch7_clean = champs_mis_a_jour_b7

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"arch_at7_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch7_clean:
            # Index 0 pour extraire l'énoncé, index 1 pour isoler la liste d'options
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_arch7_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_travaux_publics(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Travaux publics) sur deux colonnes."""
    import random

    questions_arch6_sources = [
        {"id": "qa6_1", "q": "Pourquoi une pelle mécanique de plusieurs tonnes s'enfonce-t-elle moins dans un sol marécageux si elle est équipée de chenilles très larges ?", "options": ["Les chenilles augmentent la surface d'appui, répartissant le poids, tandis que l'enfoncement dans la boue génère une poussée hydrostatique stabilisatrice", "Les chenilles rendent l'acier poreux", "La boue supprime l'effet de la gravité"], "rep": "Les chenilles augmentent la surface d'appui, répartissant le poids, tandis que l'enfoncement dans la boue génère une poussée hydrostatique stabilisatrice"},
        {"id": "qa6_2", "q": "Quel risque majeur d'hydrostatique guette une canalisation de gros diamètre vide enterrée sous une route lors d'une inondation ?", "options": ["Elle subit une forte poussée d'Archimède de l'eau du sol et remonte en soulevant le goudron", "Elle se contracte sous l'effet du froid", "Elle se met à aspirer les voitures"], "rep": "Elle subit une forte poussée d'Archimède de l'eau du sol et remonte en soulevant le goudron"},
        {"id": "qa6_3", "q": "Pour empêcher une structure creuse ou un réservoir enterré de remonter sous l'effet d'une nappe phréatique haute, le bureau d'études TP conçoit :", "options": ["Un radier de lestage en béton lourd pour augmenter le poids total", "Une isolation thermique en mousse", "Un raccordement au réseau électrique"], "rep": "Un radier de lestage en béton lourd pour augmenter le poids total"},
        {"id": "qa6_4", "q": "Quelle est la masse volumique moyenne du béton armé de référence utilisé pour les ouvrages de génie civil ?", "options": ["2500 kg/m³ (Plus lourd que l'eau, il coule)", "1000 kg/m³", "700 kg/m³"], "rep": "2500 kg/m³ (Plus lourd que l'eau, il coule)"},
        {"id": "qa6_5", "q": "Comment qualifie-t-on le phénomène de remontée accidentelle d'un ouvrage provoqué par la pression de l'eau du sol ?", "options": ["Le soulèvement par sous-pression hydrostatique", "La dérive métacentrique", "L'effet Venturi inversé"], "rep": "Le soulèvement par sous-pression hydrostatique"},
        {"id": "qa6_6", "q": "Que fait la valeur de la poussée d'Archimède subie par un coffrage étanche si le niveau de la nappe phréatique monte d'un mètre ?", "options": ["Elle augmente car le volume immergé dans l'eau du sol est plus grand", "Elle reste rigoureusement fixe", "Elle chute instantanément à zéro"], "rep": "Elle augmente car le volume immergé dans l'eau du sol est plus grand"},
        {"id": "qa6_7", "q": "Quelle technique de chantier permet de faire baisser localement le niveau d'eau du sol pour travailler au sec ?", "options": ["Le rabattement de nappe par pompage continu", "La lubrification des blindages", "L'étalonnage des manomètres"], "rep": "Le rabattement de nappe par pompage continu"},
        {"id": "qa6_8", "q": "Si un volume de un mètre cube de béton solide est totalement immergé dans l'eau pure, quelle est la valeur de la force de poussée reçue ?", "options": ["Environ 10 000 newtons", "Environ 25 000 newtons", "Environ 1 000 newtons"], "rep": "Environ 10 000 newtons"},
        {"id": "qa6_9", "q": "Quel instrument de géomètre permet de vérifier l'altitude et la planéité des ouvrages face aux risques de mouvements de terrain ?", "options": ["Un niveau de chantier (lunette optique ou laser)", "Un densitomètre à graduation", "Un manomètre différentiel"], "rep": "Un niveau de chantier (lunette optique ou laser)"},
        {"id": "qa6_10", "q": "Les calculs de stabilité des fondations et des soutènements face à la pression de l'eau font partie de :", "options": ["La géotechnique et la mécanique des sols", "La cinématique des fluides parfaits", "La thermodynamique des structures"], "rep": "La géotechnique et la mécanique des sols"}
    ]

    if "ordre_quiz_tab6_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch6_sources)
        st.session_state.ordre_quiz_tab6_arch_aleatoire = questions_arch6_sources

    champs_mis_a_jour_b6 = [
        ("1. Les structures enterrées subissent la poussée de l'eau des nappes ..........", ["Choisir...", "phréatiques", "atmosphériques"], "phréatiques", "arch6_t1"),
        ("2. Une buse vide inondée subit une force ascendante susceptible de la faire ..........", ["Choisir...", "remonter", "écraser"], "remonter", "arch6_t2"),
        ("3. Contrer le soulèvement d'un réservoir exige d'augmenter son .......... total.", ["Choisir...", "poids", "volume"], "poids", "arch6_t3"),
        ("4. Fixer l'ouvrage au sol s'appuie sur la coulée d'un radier en .......... lourd.", ["Choisir...", "béton", "bois"], "béton", "arch6_t4"),
        ("5. Le béton armé possède une masse volumique de .......... kg/m³.", ["Choisir...", "2500", "1000"], "2500", "arch6_t5"),
        ("6. La poussée verticale s'exerçant sous les fondations est une .......... pression.", ["Choisir...", "sous-pression", "sur-pression"], "sous-pression", "arch6_t6"),
        ("7. Sécuriser les fouilles impose parfois le rabattement de nappe par ..........", ["Choisir...", "pompage", "soufflage"], "pompage", "arch6_t7"),
        ("8. Les calculs de poussée d'eau sur les structures relèvent de la ..........", ["Choisir...", "géotechnique", "spectrométrie"], "géotechnique", "arch6_t8"),
        ("9. L'intensité de la force ascendante dépend du volume de sol ..........", ["Choisir...", "ennoyé", "sec"], "ennoyé", "arch6_t9"),
        ("10. Ce domaine d'application s'inscrit dans le secteur des travaux ..........", ["Choisir...", "publics", "routiers"], "publics", "arch6_t10")
    ]
    st.session_state.champs_arch6_clean = champs_mis_a_jour_b6

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"arch_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch6_clean:
            # Index 0 pour extraire l'énoncé, index 1 pour isoler la liste d'options
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_arch6_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_maintenance(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Maintenance) sur deux colonnes."""
    import random

    questions_arch5_sources = [
        {"id": "qa5_1", "q": "En maintenance industrielle, comment un capteur à plongeur utilise-t-on la poussée d'Archimède pour mesurer un niveau ?", "options": ["La variation de la force de poussée indique la hauteur du liquide immergeant le plongeur", "Le plongeur aspire le fluide par effet Venturi", "Le plongeur fait bouillir la cuve pour compter les bulles"], "rep": "La variation de la force de poussée indique la hauteur du liquide immergeant le plongeur"},
        {"id": "qa5_2", "q": "Si un technicien constate qu'un capteur de niveau hydrostatique dérive après un changement d'huile de machine, quelle en est la cause ?", "options": ["La nouvelle huile possède une masse volumique différente, ce qui modifie l'intensité de la poussée d'Archimède", "L'huile est trop chaude", "L'appareil manque de graisse"], "rep": "La nouvelle huile possède une masse volumique différente, ce qui modifie l'intensité de la poussée d'Archimède"},
        {"id": "qa5_3", "q": "Quelle anomalie d'étanchéité sur un plongeur creux de cuve provoque sa descente immédiate au fond ?", "options": ["Une fissure infiltrant le liquide à l'intérieur, ce qui augmente son poids total", "Une augmentation de la pression atmosphérique", "Un nettoyage excessif de la paroi"], "rep": "Une fissure infiltrant le liquide à l'intérieur, ce qui augmente son poids total"},
        {"id": "qa5_4", "q": "Lors de la maintenance d'une cuve de stockage, une vidange non contrôlée est qualifiée de :", "options": ["Fuite ou perte de confinement", "Saturation stœchiométrique", "Chavirage de carène"], "rep": "Fuite ou perte de confinement"},
        {"id": "qa5_5", "q": "Quel appareil portatif permet de vérifier l'étanchéité des parois métalliques d'une cuve sans la détruire ?", "options": ["Un appareil de contrôle non destructif par ultrasons", "Un dynamomètre à cadran", "Un manomètre à aiguille"], "rep": "Un appareil de contrôle non destructif par ultrasons"},
        {"id": "qa5_6", "q": "Que fait la poussée d'Archimède sur un capteur de niveau si la cuve se vide complètement ?", "options": ["Elle s'annule car il n'y a plus de fluide déplacé", "Elle double d'intensité", "Elle s'inverse vers le bas"], "rep": "Elle s'annule car il n'y a plus de fluide déplacé"},
        {"id": "qa5_7", "q": "Pourquoi la maintenance des réservoirs extérieurs impose-t-elle de purger l'eau accumulée au fond des cuves de carburant ?", "options": ["L'eau étant plus dense que le carburant, elle stagne au fond sous l'effet de la gravité", "L'eau flotte au-dessus", "L'eau s'évapore immédiatement"], "rep": "L'eau étant plus dense que le carburant, elle stagne au fond sous l'effet de la gravité"},
        {"id": "qa5_8", "q": "Comment qualifie-t-on un système mécanique d'arrêt d'urgence basé sur un flotteur fermant une arrivée ?", "options": ["Une vanne de sécurité à flotteur", "Un éjecteur Venturi", "Un régulateur de débit"], "rep": "Une vanne de sécurité à flotteur"},
        {"id": "qa5_9", "q": "Pour étalonner à nouveau un plongeur de niveau, quel fluide témoin universel utilise-t-on ?", "options": ["L'eau distillée pure", "L'huile de friture", "L'azote liquide"], "rep": "L'eau distillée pure"},
        {"id": "qa5_10", "q": "Le suivi régulier des capteurs et l'inspection des cuves pour éviter les pannes relève de la maintenance :", "options": ["Préventive", "Corrective curative", "Aléatoire"], "rep": "Préventive"}
    ]

    if "ordre_quiz_tab5_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch5_sources)
        st.session_state.ordre_quiz_tab5_arch_aleatoire = questions_arch5_sources

    champs_mis_a_jour_b5 = [
        ("1. Suivre les variations de niveau dans les cuves relève de la .......... industrielle.", ["Choisir...", "maintenance", "fabrication"], "maintenance", "arch5_t1"),
        ("2. Les capteurs de niveau exploitent la force de .......... subie par le plongeur.", ["Choisir...", "poussée", "pesanteur"], "poussée", "arch5_t2"),
        ("3. Modifier la nature de l'huile modifie sa .......... volumique et fausse la mesure.", ["Choisir...", "masse", "viscosité"], "masse", "arch5_t3"),
        ("4. Une infiltration de liquide rend un flotteur creux lourd, ce qui le fait ..........", ["Choisir...", "couler", "flotter"], "couler", "arch5_t4"),
        ("5. Inspecter régulièrement le matériel évite les pannes grâce à la maintenance ..........", ["Choisir...", "préventive", "corrective"], "préventive", "arch5_t5"),
        ("6. Détecter l'usure précoce des parois utilise un contrôle non .......... par ultrasons.", ["Choisir...", "destructif", "physique"], "destructif", "arch5_t6"),
        ("7. Une évacuation involontaire de produit liquide constitue une .......... de fluide.", ["Choisir...", "fuite", "saturation"], "fuite", "arch5_t7"),
        ("8. Le fluide le plus lourd décante et s'accumule toujours au .......... de la cuve.", ["Choisir...", "fond", "sommet"], "fond", "arch5_t8"),
        ("9. Isoler automatiquement une conduite s'appuie sur une vanne de sécurité à ..........", ["Choisir...", "flotteur", "tiroir"], "flotteur", "arch5_t9"),
        ("10. Ajuster à nouveau l'indicateur d'un capteur correspond à un .......... de l'appareil.", ["Choisir...", "étalonnage", "confinement"], "étalonnage", "arch5_t10")
    ]
    st.session_state.champs_arch5_clean = champs_mis_a_jour_b5

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"arch_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch5_clean:
            # Index [0] pour la phrase seule, index [1] pour la liste des choix
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_arch5_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_differents_fluides(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Différents fluides) sur deux colonnes."""
    import random

    questions_arch4_sources = [
        {"id": "qa4_1", "q": "Si un même objet volumineux est totalement immergé successivement dans de l'eau puis dans de l'huile, dans quel fluide subit-il la plus forte poussée ?", "options": ["Dans l'eau (car sa masse volumique est supérieure à celle de l'huile)", "Dans l'huile", "La poussée est strictement identique dans les deux fluides"], "rep": "Dans l'eau (car sa masse volumique est supérieure à celle de l'huile)"},
        {"id": "qa4_2", "q": "Quelle est la masse volumique de référence de l'eau douce pure à température ambiante ?", "options": ["1000 kg/m³ (ou 1 g/cm³)", "800 kg/m³", "1260 kg/m³"], "rep": "1000 kg/m³ (ou 1 g/cm³)"},
        {"id": "qa4_3", "q": "Pourquoi un nageur flotte-t-il beaucoup plus facilement et plus haut sans effort dans la Mer Morte ?", "options": ["Car la forte concentration en sel dissous augmente la masse volumique de l'eau, maximisant la poussée", "Car l'eau de la Mer Morte est plus chaude", "Car la gravité y est plus faible au sol"], "rep": "Car la forte concentration en sel dissous augmente la masse volumique de l'eau, maximisant la poussée"},
        {"id": "qa4_4", "q": "Quel fluide parmi les suivants possède une masse volumique très élevée (environ 1260 kg/m³), générant une poussée supérieure à l'eau douce ?", "options": ["La glycérine", "L'huile d'olive", "L'essence de pétrole"], "rep": "La glycérine"},
        {"id": "qa4_5", "q": "Comment évolue la poussée d'Archimède exercée par un gaz (comme l'air) par rapport à un liquide à volume égal ?", "options": ["Elle est beaucoup plus faible car la masse volumique de l'air est infime (environ 1,2 kg/m³)", "Elle est rigoureusement identique", "Elle est trois fois plus forte"], "rep": "Elle è beaucoup plus faible car la masse volumique de l'air est infime (environ 1,2 kg/m³)"},
        {"id": "qa4_6", "q": "Quel gaz très léger remplit les ballons dirigeables pour que la poussée d'Archimède de l'air environnant soit supérieure à leur poids ?", "options": ["L'hélium (ou le dihydrogène)", "Le dioxyde de carbone", "Le krypton lourd"], "rep": "L'hélium (ou le dihydrogène)"},
        {"id": "qa4_7", "q": "Si un solide flotte à la surface d'un liquide, la masse volumique du solide est obligatoirement :", "options": ["Inférieure à celle du liquide", "Supérieure à celle du liquide", "Rigoureusement égale à celle du vide"], "rep": "Inférieure à celle du liquide"},
        {"id": "qa4_8", "q": "La poussée d'Archimède subie par un corps totalement immergé est directement proportionnelle à :", "options": ["La masse volumique du fluide environnant", "La viscosité dynamique du fluide", "La conductivité thermique du solide"], "rep": "La masse volumique du fluide environnant"},
        {"id": "qa4_9", "q": "Comment appelle-t-on l'appareil en verre les laboratoires de chimie pour mesurer directement la densité ou la masse volumique d'un liquide ?", "options": ["Un densitomètre (ou hydromètre à graduation)", "Un manomètre à tube", "Un dynamomètre linéaire"], "rep": "Un densitomètre (ou hydromètre à graduation)"},
        {"id": "qa4_10", "q": "Un fluide dont la masse volumique est de 800 kg/m³ exercera sur un volume d'un litre une poussée d'environ :", "options": ["8 newtons", "10 newtons", "12 newtons"], "rep": "8 newtons"}
    ]

    if "ordre_quiz_tab4_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch4_sources)
        st.session_state.ordre_quiz_tab4_arch_aleatoire = questions_arch4_sources

    champs_mis_a_jour_b4 = [
        ("1. À volume égal, un fluide plus lourd génère une poussée plus ..........", ["Choisir...", "grande", "faible"], "grande", "arch4_t1"),
        ("2. La masse volumique de l'eau pure de référence est de .......... kg/m³.", ["Choisir...", "1000", "800"], "1000", "arch4_t2"),
        ("3. Augmenter la salinité d'une solution aqueuse élève sa .......... volumique.", ["Choisir...", "masse", "viscosité"], "masse", "arch4_t3"),
        ("4. L'huile de moteur possède une densité .......... à celle de l'eau douce.", ["Choisir...", "inférieure", "supérieure"], "inférieure", "arch4_t4"),
        ("5. La glycérine est un fluide visqueux particulièrement ..........", ["Choisir...", "dense", "léger"], "dense", "arch4_t5"),
        ("6. L'air exerce une poussée sur les corps appelée poussée ..........", ["Choisir...", "d'Archimède", "de Plimsoll"], "d'Archimède", "arch4_t6"),
        ("7. La masse volumique de l'air est très faible par rapport à celle des ..........", ["Choisir...", "liquides", "gaz"], "liquides", "arch4_t7"),
        ("8. Faire flotter une montgolfière exige de chauffer l'air pour le rendre moins ..........", ["Choisir...", "dense", "frais"], "dense", "arch4_t8"),
        ("9. L'instrument plongeant servant à lire la densité est le ..........", ["Choisir...", "densitomètre", "manomètre"], "densitomètre", "arch4_t9"),
        ("10. À l'équilibre stœchiométrique, la flottabilité dépend du rapport des ..........", ["Choisir...", "densités", "surfaces"], "densités", "arch4_t10")
    ]
    st.session_state.champs_arch4_clean = champs_mis_a_jour_b4

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"arch_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch4_clean:
            # Index [0] pour isoler la phrase, index [1] pour isoler la liste d'options
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_arch4_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_flottaison_bateaux(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (La flottaison des bateaux) sur deux colonnes."""
    import random

    questions_arch3_sources = [
        {"id": "qa3_1", "q": "À quelle condition mathématique un bateau peut-il flotter en parfait équilibre sur l'eau ?", "options": ["Lorsque l'intensité de sa poussée d'Archimède est rigoureusement égale à son poids total", "Lorsque la poussée est deux fois plus petite que son poids", "Lorsque son poids est nul"], "rep": "Lorsque l'intensité de sa poussée d'Archimède est rigoureusement égale à son poids total"},
        {"id": "qa3_2", "q": "Comment appelle-t-on le centre de gravité de la partie immergée de la coque où s'applique la poussée ?", "options": ["Le centre de carène (ou centre de poussée)", "Le métacentre de surface", "Le centre de gravité solide"], "rep": "Le centre de carène (ou centre de poussée)"},
        {"id": "qa3_3", "q": "Pourquoi un énorme paquebot en acier lourd arrive-t-il à flotter sans couler au fond ?", "options": ["Car sa coque emprisonne un immense volume d'air, ce qui rend sa masse volumique globale inférieure à celle de l'eau", "Car l'acier est traité pour devenir plus léger que l'eau", "Car les hélices poussent le navire vers le haut en continu"], "rep": "Car sa coque emprisonne un immense volume d'air, ce qui rend sa masse volumique globale inférieure à celle de l'eau"},
        {"id": "qa3_4", "q": "Comment appelle-t-on la ligne limite gravée sur la coque indiquant la zone maximale de chargement sécurisé ?", "options": ["La ligne de flottaison (ou marque de Plimsoll)", "Le repère du dynamomètre", "Le calibre d'étalonnage"], "rep": "La ligne de flottaison (ou marque de Plimsoll)"},
        {"id": "qa3_5", "q": "Que fait un navire lorsque l'on rajoute plusieurs tonnes de marchandises dans ses cales ?", "options": ["Il s'enfonce plus profondément pour déplacer un volume d'eau supplémentaire égal au surpoids", "Il remonte vers la surface", "Son volume immergé reste strictement identique"], "rep": "Il s'enfonce plus profondément pour déplacer un volume d'eau supplémentaire égal au surpoids"},
        {"id": "qa3_6", "q": "Dans quel type d'eau un bateau s'enfoncera-t-il le moins à masse de chargement égale ?", "options": ["Dans l'eau de mer salée (car elle est plus dense que l'eau douce)", "Dans l'eau douce d'une rivière", "L'enfoncement est exactement identique partout"], "rep": "Dans l'eau de mer salée (car elle est plus dense que l'eau douce)"},
        {"id": "qa3_7", "q": "Comment appelle-t-on les compartiments inférieurs d'un navire que l'on remplit d'eau pour stabiliser le centre de gravité ?", "options": ["Les ballasts", "Les cales sèches", "Les buses Venturi"], "rep": "Les ballasts"},
        {"id": "qa3_8", "q": "Si le centre de gravité global du navire monte plus haut que le métacentre lors d'un mauvais chargement, le bateau :", "options": ["Risque de chavirer (perte de stabilité)", "Flotte encore mieux", "Devient impossible à ralentir"], "rep": "Risque de chavirer (perte de stabilité)"},
        {"id": "qa3_9", "q": "Quelle force physique tire le navire verticalement vers le fond de l'eau ?", "options": ["La force de pesanteur (le Poids)", "La poussée d'Archimède", "La tension superficielle du fluide"], "rep": "La force de pesanteur (le Poids)"},
        {"id": "qa3_10", "q": "L'analyse physique de la stabilité et de l'équilibre d'un navire au repos relève de :", "options": ["L'architecture navale hydrostatique", "L'aérodynamique des structures", "La cinématique linéaire"], "rep": "L'architecture navale hydrostatique"}
    ]

    if "ordre_quiz_tab3_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch3_sources)
        st.session_state.ordre_quiz_tab3_arch_aleatoire = questions_arch3_sources

    champs_mis_a_jour_b3 = [
        ("1. Un navire reste en équilibre stable si la poussée compense exactement son ..........", ["Choisir...", "poids", "volume"], "poids", "arch3_t1"),
        ("2. La poussée s'applique rigoureusement au centre de .......... de la coque immergée.", ["Choisir...", "carène", "gravité"], "carène", "arch3_t2"),
        ("3. Flotter impose que la masse volumique moyenne du navire soit .......... à celle de l'eau.", ["Choisir...", "inférieure", "supérieure"], "inférieure", "arch3_t3"),
        ("4. Augmenter la cargaison d'un cargo provoque son .......... dans le liquide.", ["Choisir...", "enfoncement", "allègement"], "enfoncement", "arch3_t4"),
        ("5. La marque de charge maximale gravée sur les flancs est la ligne de ..........", ["Choisir...", "flottaison", "calibre"], "flottaison", "arch3_t5"),
        ("6. L'eau salée étant plus dense, elle génère une poussée à volume égal plus ..........", ["Choisir...", "grande", "faible"], "grande", "arch3_t6"),
        ("7. Ajuster la position du centre de gravité s'appuie sur le remplissage des ..........", ["Choisir...", "ballasts", "cuves"], "ballasts", "arch3_t7"),
        ("8. Un mauvais centrage des masses lourdes expose le navire à un ..........", ["Choisir...", "chavirage", "freinage"], "chavirage", "arch3_t8"),
        ("9. L'air enfermé dans la coque creuse assure un grand .......... de carène.", ["Choisir...", "volume", "poids"], "volume", "arch3_t9"),
        ("10. Ce module réalise une application de la mécanique des .......... au repos.", ["Choisir...", "fluides", "solides"], "fluides", "arch3_t10")
    ]
    st.session_state.champs_arch3_clean = champs_mis_a_jour_b3

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"arch_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch3_clean:
            # Indexation stricte pour isoler les chaînes du tuple
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_arch3_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_definition_archimede(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Définition) sur deux colonnes."""
    import random

    questions_arch2_sources = [
        {"id": "qa2_1", "q": "Quelle est la direction et le sens de la poussée d'Archimède ?", "options": ["Verticale, du bas vers le haut", "Horizontale, de gauche à droite", "Verticale, du haut vers le bas"], "rep": "Verticale, du bas vers le haut"},
        {"id": "qa2_2", "q": "La poussée d'Archimède est rigoureusement égale au poids du fluide :", "options": ["Déplacé par l'objet", "Total contenu dans le récipient", "Absorbé par le solide"], "rep": "Le poids du fluide déplacé"},
        {"id": "qa2_3", "q": "Quelle est l'unité internationale de mesure de la force de poussée ?", "options": ["Le newton (N)", "Le pascal (Pa)", "Le kilogramme (kg)"], "rep": "Le newton (N)"},
        {"id": "qa2_4", "q": "Dans la formule de la poussée, que représente le symbole grec 'rho' ?", "options": ["La masse volumique du fluide", "Le volume immergé", "L'intensité de la pesanteur"], "rep": "La masse volumique du fluide"},
        {"id": "qa2_5", "q": "Si un objet est entièrement immergé, de quoi dépend l'intensité de sa poussée ?", "options": ["Uniquement de son volume total", "Uniquement de son poids propre", "De sa couleur de surface"], "rep": "Uniquement de son volume total"},
        {"id": "qa2_6", "q": "Que fait la valeur de la poussée d'Archimède si l'on plonge l'objet deux fois plus profondément dans un liquide homogène ?", "options": ["Elle reste identique", "Elle est doublée", "Elle tombe à zéro"], "rep": "Elle reste identique"},
        {"id": "qa2_7", "q": "Si la poussée d'Archimède est inférieure au poids réel de l'objet, ce dernier :", "options": ["Coule au fond", "Flotte en surface", "Reste entre deux eaux"], "rep": "Coule au fond"},
        {"id": "qa2_8", "q": "Où s'applique le vecteur force de la poussée d'Archimède ?", "options": ["Au centre de gravité du fluide déplacé (centre de poussée)", "Au centre de gravité de l'objet réel", "Tout en haut de la surface du liquide"], "rep": "Au centre de gravité du fluide déplacé (centre de poussée)"},
        {"id": "qa2_9", "q": "Quel instrument de mesure mécanique permet de mesurer l'intensité d'une force de poussée en laboratoire ?", "options": ["Un dynamomètre", "Un manomètre", "Une fiole jaugée"], "rep": "Un dynamomètre"},
        {"id": "qa2_10", "q": "La force d'Archimède s'exerce sur un solide immergé dans :", "options": ["Tout fluide (liquide ou gaz)", "Uniquement de l'eau distillée", "Uniquement les liquides visqueux"], "rep": "Tout fluide (liquide ou gaz)"}
    ]

    if "ordre_quiz_tab2_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch2_sources)
        st.session_state.ordre_quiz_tab2_arch_aleatoire = questions_arch2_sources

    champs_mis_a_jour_b2 = [
        ("1. La poussée d'Archimède est une force mécanique dirigée vers le ..........", ["Choisir...", "haut", "bas"], "haut", "arch2_t1"),
        ("2. L'intensité de cette poussée est égale au poids du fluide ..........", ["Choisir...", "déplacé", "total"], "déplacé", "arch2_t2"),
        ("3. Le symbole mathématique normalisé de la masse volumique est ..........", ["Choisir...", "rho", "epsilon"], "rho", "arch2_t3"),
        ("4. Une force s'exprime obligatoirement dans l'unité du ..........", ["Choisir...", "newton", "pascal"], "newton", "arch2_t4"),
        ("5. Le point d'application de la poussée est le centre de .......... du fluide déplacé.", ["Choisir...", "carène", "gravité"], "carène", "arch2_t5"),
        ("6. Si la poussée équilibre exactement le poids de l'objet, celui-ci ..........", ["Choisir...", "flotte", "coule"], "flotte", "arch2_t6"),
        ("7. Plonger un corps dans un liquide plus dense augmente la force de ..........", ["Choisir...", "poussée", "pesanteur"], "poussée", "arch2_t7"),
        ("8. Le volume pris en compte dans le calcul est le volume de la partie ..........", ["Choisir...", "immergée", "émergée"], "immergée", "arch2_t8"),
        ("9. L'accélération de la pesanteur terrestre est symbolisée par la lettre ..........", ["Choisir...", "g", "P"], "g", "arch2_t9"),
        ("10. L'air exerce également une poussée qualifiée de ..........", ["Choisir...", "atmosphérique", "hydrostatique"], "atmosphérique", "arch2_t10")
    ]
    st.session_state.champs_arch2_clean = champs_mis_a_jour_b2

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"arch_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch2_clean:
            # Extraction stricte par index pour isoler le texte et les choix
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_arch2_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_histoire_archimede(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Historique) sur deux colonnes."""
    import random

    questions_arch1_sources = [
        {"id": "qa1", "q": "Dans quelle cité antique grecque de Sicile est né et a vécu le savant Archimède ?", "options": ["Syracuse", "Athènes", "Sparte"], "rep": "Syracuse"},
        {"id": "qa2", "q": "Quel roi de Syracuse a commandé une couronne d'or et a demandé à Archimède d'en vérifier la pureté ?", "options": ["Le roi Hiéron II", "Le roi Alexandre", "Le roi Léonidas"], "rep": "Le roi Hiéron II"},
        {"id": "qa3", "q": "Quel métal moins dense et moins précieux l'orfèvre malhonnête avait-il mélangé à l'or de la couronne ?", "options": ["L'argent", "Le plomb", "Le cuivre"], "rep": "L'argent"},
        {"id": "qa4", "q": "Où se trouvait Archimède lorsqu'il a compris comment mesurer le volume de la couronne par déplacement de fluide ?", "options": ["Dans sa baignoire publique", "Dans son jardin", "Au sommet d'une tour de guet"], "rep": "Dans sa baignoire publique"},
        {"id": "qa5", "q": "Quel célèbre mot grec signifiant 'J'ai trouvé !' Archimède a-t-il hurlé en s'élançant nu dans la rue ?", "options": ["Eurêka", "Pneuma", "Logos"], "rep": "Eurêka"},
        {"id": "qa6", "q": "Quelle grandeur physique obtenue en divisant la masse par le volume a permis de confondre l'orfèvre ?", "options": ["La masse volumique", "La tension superficielle", "La viscosité dynamique"], "rep": "La masse volumique"},
        {"id": "qa7", "q": "Si un volume d'or pur et un même volume d'argent sont plongés dans l'eau, lequel déplace le plus de liquide ?", "options": ["Ils déplacent exactement le même volume d'eau", "L'or pur en déplace davantage", "L'argent en déplace davantage"], "rep": "Ils déplacent exactement le même volume d'eau"},
        {"id": "qa8", "q": "Quelle invention célèbre Archimède a-t-il conçue pour remonter l'eau des fleuves et irriguer les cultures ?", "options": ["La vis sans fin (vis d'Archimède)", "Le compresseur à piston", "La burette volumétrique"], "rep": "La vis sans fin (vis d'Archimède)"},
        {"id": "qa9", "q": "Au cours de quel conflit historique Archimède a-t-il défendu sa cité à l'aide de miroirs ardents ?", "options": ["Le siège de Syracuse par les Romains", "Les guerres médiques contre les Perses", "La guerre de Troie"], "rep": "Le siège de Syracuse par les Romains"},
        {"id": "qa10", "q": "L'étude quantitative des fluides au repos initialement formalisée par Archimède s'appelle :", "options": ["L'hydrostatique", "L'aérodynamique", "La thermodynamique"], "rep": "L'hydrostatique"}
    ]

    if "ordre_quiz_tab1_arch_aleatoire" not in st.session_state:
        random.shuffle(questions_arch1_sources)
        st.session_state.ordre_quiz_tab1_arch_aleatoire = questions_arch1_sources

    if "champs_arch1_clean" not in st.session_state:
        st.session_state.champs_arch1_clean = [
            ("1. Le savant Archimède a mené ses travaux de recherche à l'époque de l'..........", ["Choisir...", "Antiquité", "Renaissance"], "Antiquité", "arch1_t1"),
            ("2. Le souverain commanditaire de la couronne suspecte était le roi ..........", ["Choisir...", "Hiéron II", "Sorensen"], "Hiéron II", "arch1_t2"),
            ("3. Déterminer la fraude reposait sur la mesure de la masse .......... du corps.", ["Choisir...", "volumique", "moléculaire"], "volumique", "arch1_t3"),
            ("4. Plonger un solide dans un vase plein provoque un .......... de liquide.", ["Choisir...", "déplacement", "gel"], "déplacement", "arch1_t4"),
            ("5. Le cri historique poussé par le savant lors de sa découverte est ..........", ["Choisir...", "Eurêka", "Pneuma"], "Eurêka", "arch1_t5"),
            ("6. Pour tricher, l'artisan avait frauduleusement substitué l'or par de l'..........", ["Choisir...", "argent", "plomb"], "argent", "arch1_t6"),
            ("7. Élever l'eau pour irriguer les terres s'appuie sur la .......... d'Archimède.", ["Choisir...", "vis", "pince"], "vis", "arch1_t7"),
            ("8. L'étude des liquides en parfait équilibre au repos est l'..........", ["Choisir...", "hydrostatique", "cinématique"], "hydrostatique", "arch1_t8"),
            ("9. La poussée s'exerce du bas vers le haut sur tout solide ..........", ["Choisir...", "immergé", "gazeux"], "immergé", "arch1_t9"),
            ("10. Confondu par la science, l'orfèvre a subi une analyse de type ..........", ["Choisir...", "quantitative", "qualitative"], "quantitative", "arch1_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique et Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_arch_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"arch_at1_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_arch1_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_arch1_clean", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Historique")
    
    st.subheader("Histoire des Sciences : L'énigme de la couronne du Roi Hiéron")
    st.write(
        "Au troisième siècle avant notre ère, à Syracuse, le roi Hiéron II commanda une couronne d'or pur "
        "à un orfèvre local. Soupçonnant l'artisan d'avoir volé une partie de l'or pour le remplacer par "
        "de l'argent (un métal moins dense et moins noble), le roi chargea le mathématicien Archimède "
        "de prouver la fraude sans détruire ni fondre le chef-d'œuvre.\n\n"
        "La solution frappa l'esprit d'Archimède alors qu'il s'installait dans une baignoire des bains publics. "
        "En remarquant que le niveau de l'eau montait à mesure que son corps s'immergeait, il comprit que "
        "le volume de liquide déplacé était rigoureusement égal au volume de la partie immergée de son corps. "
        "Submergé par l'excitation, il s'élança nu à travers les rues de la cité en hurlant le mot grec "
        "**'Eurêka !'** (J'ai trouvé !)."
    )
    
    st.divider()
    
    st.subheader("La démonstration scientifique face à la fraude")
    st.write(
        "Pour confondre l'artisan, Archimède utilisa une balance hydrostatique. Il pesa une masse d'or pur "
        "exactement égale au poids de la couronne, puis fit de même avec un lingot d'argent pur.\n\n"
        "En plongeant successivement le lingot d'or pur et la couronne suspecte dans un récipient rempli à ras bord, "
        "il constata que la couronne faisait déborder **plus d'eau** que le lingot d'or pur. L'argent étant moins dense, "
        "il nécessite un volume plus important que l'or pour atteindre la même masse. La couronne possédait donc un volume "
        "anormalement grand : l'orfèvre fut démasqué et condamné grâce à la toute première analyse quantitative de l'histoire."
    )
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.write("**La BD humoristique textuelle : Le bain révélateur**")
        st.info(
            "**Case 1 :** L'orfèvre livre la couronne au palais avec un sourire narquois, pensant avoir réussi le crime parfait.\n\n"
            "**Case 2 :** Archimède glisse dans sa baignoire. L'eau déborde sur les pieds du serviteur qui pousse un soupir. "
            "Archimède fixe le sol, l'œil écarquillé, l'ampoule scientifique s'allume au-dessus de sa tête.\n\n"
            "**Case 3 :** Le savant traverse Syracuse en courant, une éponge à la main, sous les yeux ébahis des marchands de poissons.\n\n"
            "**Case 4 :** Devant le roi, Archimède plonge la couronne. L'eau gicle sur la figure de l'orfèvre qui pâlit instantanément, comprenant "
            "que la physique vient de briser sa supercherie."
        )
        try:
            st.image("caricature_histoire_archimede.jpg", caption="Caricature de la découverte : Le déplacement volumétrique du liquide")
        except Exception:
            st.warning("L'image 'caricature_histoire_archimede.jpg' est introuvable.")

    with col_h2:
        st.write("**Le leg technique d'Archimède**")
        st.write(
            "Au-delà de cette anecdote, Archimède a jeté les bases de l'**hydrostatique** (la science de l'équilibre des fluides au repos). "
            "Il comprit que tout fluide exerce une poussée verticale opposée à la gravité sur les corps immergés.\n\n"
            "On lui doit également de multiples inventions mécaniques majeures, comme la **vis d'Archimède** (une vis sans fin inclinée "
            "toujours exploitée dans le monde moderne pour élever l'eau ou déplacer les céréales) et les systèmes de poulies composées."
        )


        try:
            st.image("montage_general_archimede.jpg", caption="Quelles inventions")
        except Exception:
            st.warning("L'image 'montage_general_archimede.jpg' est introuvable.")
        try:
            st.image("balance_archimede.jpeg", caption="Représentation de la balance hydrostatique d'Archimède pour la mesure des densités")
        except Exception:
            st.warning("balance_archimede.jpeg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE DE L'ATELIER 1 ---
    if "suite_verrouille_tab1_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab1_archimede = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_archimede

    # Affichage du module de questions spécifique à l'histoire d'Archimède
    afficher_atelier_histoire_archimede(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique.",
        key="check_certif_arch1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_arch_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatisée du Quiz
            score_q1 = 0.0
            if "ordre_quiz_tab1_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q1 += 1.0

            # Correction automatisée du Texte à trous (tuples)
            score_t1 = 0.0
            if "champs_arch1_clean" in st.session_state:
                for ligne in st.session_state.champs_arch1_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_arch1_clean", "Choisir...") == attendu: 
                        score_t1 += 1.0

            # Sauvegarde des scores et verrouillage
            st.session_state.score_suite1_arch_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_arch_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_arch = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab1_archimede", False):
        scr1_t1 = st.session_state.get("score_suite1_arch_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_arch_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_arch", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_arch1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Archimède - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 1 : Contexte historique de l'hydrostatique et énigme de la couronne</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab1_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_arch1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_arch1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_arch1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch1 = preparer_nom_fichier("Rapport_Histoire_Archimede").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_arch1,
            file_name=nom_fichier_html_arch1,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Définition de la poussée d'Archimède")
    
    # --- SECTION COURS : LOI PHYSIQUE ---
    st.subheader("Énoncé scientifique officiel")
    st.write(
        "La poussée d'Archimède est la force particulière résultante des pressions exercées par un fluide "
        "(liquide ou gaz) sur un corps immergé. Cet effet mécanique est formalisé par la loi suivante :\n\n"
        "**'Tout corps plongé dans un fluide au repos subit de la part de celui-ci une poussée verticale, "
        "dirigée du bas vers le haut, dont l'intensité est égale au poids du volume de fluide déplacé.'**\n\n"
        "L'équation mathématique vectorielle s'écrit de la forme suivante :"
    )
    
    st.latex(r"\Pi = \rho_{\text{fluide}} \cdot V_{\text{immergé}} \cdot g")
    
    st.write(
        "Où :\n"
        "* **$\\Pi$** (Pi) est l'intensité de la poussée d'Archimède exprimée en **newtons (N)**.\n"
        "* **$\\rho_{\\text{fluide}}$** (rho) est la masse volumique du fluide en **kilogrammes par mètre cube ($\text{kg/m}^3$)**.\n"
        "* **$V_{\\text{immergé}}$** est le volume de la partie du solide qui se trouve sous l'eau en **mètres cubes ($\text{m}^3$)**.\n"
        "* **$g$** est l'intensité du champ de pesanteur terrestre (environ $9{,}81 \text{ N/kg}$)."
    )
    
    st.divider()

    col_graph_arch, col_bd_arch = st.columns([0.55, 0.45])
    
    with col_graph_arch:
        st.write("**La BD humoristique textuelle : La révolte des Molécules**")
        st.info(
            "**Case 1 :** Un bloc de plomb lourd s'apprête à sauter du plongeoir d'une piscine en bombant le torse : 'Je vais fendre l'eau comme un météore !'.\n\n"
            "**Case 2 :** Au fond du bassin, des milliers de petites molécules d'eau en forme de billes bleues se liguent en se tenant les coudes : 'Attention les gars, un intrus arrive ! Préparez la riposte collective !'.\n\n"
            "**Case 3 :** Le bloc percute la surface. Instantanément, toutes les molécules d'eau se bousculent et se mettent à pousser ensemble sous ses fesses vers le haut : 'Allez, tout le monde pousse ! Hisse-ho !'.\n\n"
            "**Case 4 :** Si le bloc est en bois léger, les molécules le rejettent victorieusement à la surface en criant : 'Et un retour à l'envoyeur, un !'. Si le bloc est trop lourd, il descend au fond mais les molécules s'essuient le front : 'On a perdu la bataille de la gravité, mais on lui a quand même retiré pas mal de kilos !'."
        )

    with col_bd_arch:

        try:
            # L'image utilise bien le nom exact configuré dans votre projet
            st.image("archimede_bassin.jpeg", caption="Quelle plongée !", use_container_width=True)
        except Exception:
            st.warning("L'image 'archimede_bassin.jpeg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")
                 

    
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE AVEC FLÈCHES VECTORIELLES ---
    st.subheader("Simulateur dynamique d'équilibre hydrostatique")
    st.write(
        "Modifiez le curseur ci-dessous pour changer la densité de l'objet carré. "
        "Le graphique Matplotlib recalculera immédiatement sa flottaison et tracera les deux forces en présence :\n"
        "* **Le Poids réel (flèche noire $\\vec{P}$)** appliqué au centre de gravité de l'objet, tirant vers le bas.\n"
        "* **La Poussée d'Archimède (flèche bleue $\\vec{\\Pi}$)** appliquée au centre de carène, poussant vers le haut."
    )
    
    # Curseur interactif de masse volumique pour l'élève
    masse_vol_objet = st.slider("Sélectionner la masse volumique du solide (en kg/m³ - Eau = 1000) :", min_value=300, max_value=1800, value=600, step=50, key="slider_density_arch2")
    

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    # Calcul de la position d'équilibre hydrostatique
    # Si densité < 1000, l'objet flotte (partie immergée = ratio_densite)
    # Si densité >= 1000, l'objet coule au fond (immersion totale = 1.0)
    densite_eau = 1000.0
    volume_total = 1.0  # Cube de 1x1
    cote = 1.0
    
    fig_arch, ax_arch = plt.subplots(figsize=(5, 4.2), facecolor="white")
    ax_arch.set_facecolor("white")
    
    # Tracé de la cuve et de l'eau (ligne d'eau fixe à y = 2.0)
    ax_arch.add_patch(patches.Rectangle((0.5, 0), 4.0, 2.0, facecolor="#0284c7", alpha=0.4, label="Eau (1000 kg/m³)", zorder=1))
    ax_arch.axhline(2.0, color="#0284c7", linewidth=2.5, linestyle="-", zorder=2)
    
    if masse_vol_objet < densite_eau:
        # Cas de flottaison : immersion partielle
        fraction_immergee = masse_vol_objet / densite_eau
        y_bas_objet = 2.0 - fraction_immergee
        statut_visu = "L'objet flotte"
        color_bloc = "#e2e8f0"  # Gris clair (bois)
        
        poids_val = volume_total * masse_vol_objet * 9.81 / 1000.0
        poussee_val = poids_val  # Équilibre parfait
    else:
        # Cas de submersion : l'objet coule au fond (y_bas = 0.2)
        y_bas_objet = 0.2
        statut_visu = "L'objet coule au fond"
        color_bloc = "#94a3b8"  # Gris foncé (pierre)
        
        poids_val = volume_total * masse_vol_objet * 9.81 / 1000.0
        poussee_val = volume_total * densite_eau * 9.81 / 1000.0  # Poussee maximale limitée au volume du bloc
        
    # Dessin du bloc solide
    x_gauche_objet = 2.0
    ax_arch.add_patch(patches.Rectangle((x_gauche_objet, y_bas_objet), cote, cote, facecolor=color_bloc, edgecolor="#1e293b", linewidth=2, zorder=3))
    
    # Coordonnées des centres d'applications des forces
    x_centre = x_gauche_objet + 0.5
    y_centre_poids = y_bas_objet + 0.5
    
    # Centre de carène (milieu de la zone immergée)
    if masse_vol_objet < densite_eau:
        hauteur_immergee = fraction_immergee
        y_centre_poussee = y_bas_objet + (hauteur_immergee / 2.0)
    else:
        y_centre_poussee = y_bas_objet + 0.5
        
    # Échelle de tracé pour les vecteurs forces (flèches)
    echelle_fleche = 1 / (volume_total * 1800 * 9.81 / 1000.0)
    longueur_poids = poids_val * echelle_fleche
    longueur_poussee = poussee_val * echelle_fleche
    
    # Tracé des vecteurs forces avec flèches explicites
    # Poids (vers le bas, noir)
    ax_arch.arrow(x_centre, y_centre_poids, 0, -longueur_poids, head_width=0.12, head_length=0.12, fc="#1e293b", ec="#1e293b", linewidth=2.5, length_includes_head=True, zorder=4)
    ax_arch.text(x_centre + 0.15, y_centre_poids - (longueur_poids / 2), r"$\vec{P}$", color="#1e293b", weight="bold", fontsize=12)
    
    # Poussée d'Archimède (vers le haut, bleu roi)
    ax_arch.arrow(x_centre, y_centre_poussee, 0, longueur_poussee, head_width=0.12, head_length=0.12, fc="#1d4ed8", ec="#1e3a8a", linewidth=2.5, length_includes_head=True, zorder=4)
    ax_arch.text(x_centre - 0.35, y_centre_poussee + (longueur_poussee / 2), r"$\vec{\Pi}$", color="#1d4ed8", weight="bold", fontsize=12)
    
    ax_arch.set_xlim(0, 5)
    ax_arch.set_ylim(0, 3.5)
    ax_arch.axis("off")
    st.pyplot(fig_arch)
    st.caption(f"État du système : {statut_visu} (Poids = {poids_val:.1f} N | Poussée = {poussee_val:.1f} N)")


    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab2_archimede = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_archimede

    # Affichage de l'Atelier d'évaluation 2
    afficher_atelier_definition_archimede(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Définition de la poussée d'Archimède.",
        key="check_certif_arch2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_arch_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q2 += 1.0

            score_t2 = 0.0
            if "champs_arch2_clean" in st.session_state:
                for ligne in st.session_state.champs_arch2_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_arch2_clean", "Choisir...") == attendu: score_t2 += 1.0

            st.session_state.score_final_suite2_arch = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ POUR L'ATELIER 2 ---
    if st.session_state.get("suite_verrouille_tab2_archimede", False):
        scr1_t2 = st.session_state.get("score_final_suite2_arch", 0.0) / 2.0  # Exemple de répartition
        scr2_t2 = st.session_state.get("score_final_suite2_arch", 0.0) / 2.0
        tot_s_t2 = st.session_state.get("score_final_suite2_arch", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DÉFINITION SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_arch2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Définition Archimède - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 2 : Définition vectorielle, formule mathématique et forces hydrostatiques</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1d4ed8;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Extraction et injection des lignes de correction du Quiz technique
        if "ordre_quiz_tab2_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_arch2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Extraction et injection des lignes de correction du texte à trous
        if "champs_arch2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 2
        html_export_arch2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch2 = preparer_nom_fichier("Rapport_Definition_Archimede").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_arch2,
            file_name=nom_fichier_html_arch2,
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("La flottaison des bateaux")
    
   
    # --- SECTION COURS : LES PRINCIPES DE LA FLOTTAISON ---
    st.subheader("L'équilibre statique du navire")

    # 1. Création de deux colonnes (60% pour le texte, 40% pour l'image)
    col_texte, col_image = st.columns([3, 2])

    # 2. Contenu de la colonne de gauche (le texte)
    with col_texte:
        st.write(
            "L'application la plus spectaculaire de l'hydrostatique est la flottaison des navires. "
            "Pour qu'un bateau reste immobile à la surface, l'intensité de la **poussée d'Archimède ($\\vec{\\Pi}$)** "
            "développée par l'eau doit équilibrer de manière absolue le **Poids total ($\\vec{P}$)** du navire et de sa cargaison.\n\n"
            "Cet équilibre met en relation deux centres géométriques distincts :\n"
            "* **Le centre de gravité (G) :** Point d'application du Poids, déterminé par la répartition des masses lourdes.\n"
            "* **Le centre de carène (C) :** Point d'application de la poussée d'Archimède, correspondant au centre de gravité "
            "du volume de la coque immergée sous l'eau."
        )

    # 3. Contenu de la colonne de droite (l'image)
    with col_image:
      
        st.image("equilibre_navire.jpg", caption="Schéma des forces G et C", use_container_width=True)

    st.divider()
    
    st.subheader("Le paradoxe de l'acier creux et les lignes de charge")

        # 1. Création de deux colonnes (60% pour le texte, 40% pour l'image)
    col_texte, col_image = st.columns([3, 2])

    # 2. Contenu de la colonne de gauche (le texte)
    with col_texte:
        st.write(
            "Un lingot d'acier coule instantanément car sa masse volumique ($7800 \\text{ kg/m}^3$) est bien supérieure à celle de l'eau ($1000 \\text{ kg/m}^3$). "
            "Pourtant, un cargo construit avec des milliers de tonnes d'acier flotte parfaitement. Le secret réside dans la géométrie de la coque : "
            "en étant large et creuse, elle enferme un immense **volume d'air**. La masse volumique globale du navire (masse totale divisée "
            "par le volume total de la coque) devient inférieure à celle de l'eau, lui permettant de flotter.\n\n"
            "Lorsque l'on charge des conteneurs, le poids augmente. Le bateau s'enfonce alors dans l'eau pour déplacer un volume liquide "
            "supplémentaire, ce qui augmente la poussée d'Archimède jusqu'à retrouver l'équilibre. "
            "Pour éviter la surcharge et le naufrage, les navires portent une marque gravée sur leurs flancs : la **ligne de flottaison** "
            "(ou marque de Plimsoll), indiquant la limite de submersion sécurisée selon la densité de l'eau (l'eau de mer salée étant plus dense "
            "que l'eau douce des fleuves, le navire y flotte plus haut)."
        )

    # 3. Contenu de la colonne de droite (le graphique vectoriel de la marque de Plimsoll)
    with col_image:
        st.caption("**Légende de la marque de Plimsoll :**")
        st.markdown(
            "- <span style='color:#636EFA; font-weight:bold;'>TF / F</span> : Eau douce tropicale / Eau douce (le navire s'enfonce plus, eau moins dense)\n"
            "- <span style='color:#00CC96; font-weight:bold;'>T / S / W</span> : Eau de mer (Tropicale / Été / Hiver)\n"
            "- **WNA** : Hiver dans l'Atlantique Nord (limite la plus stricte, mer difficile)", 
            unsafe_allow_html=True
        )
        
        # Création du graphique Plotly pour simuler la ligne de charge
        fig2 = go.Figure()
        
        # Ligne verticale principale du flanc du navire
        fig2.add_shape(type="line", x0=0, y0=-1.5, x1=0, y1=1.5, line=dict(color="DarkSlateGray", width=5))
        
        # Cercle et ligne horizontale principale (Ligne d'été 'S')
        fig2.add_shape(type="circle", x0=-0.6, y0=-0.3, x1=0.6, y1=0.3, line=dict(color="DarkSlateGray", width=4))
        fig2.add_shape(type="line", x0=-0.9, y0=0, x1=0.9, y1=0, line=dict(color="DarkSlateGray", width=4))
        
        # Lignes de charge à droite (Eau de mer)
        niveaux_mer = [
            (0.6, "T (Tropical)", "#00CC96"),
            (0.0, "S (Été)", "#00CC96"),
            (-0.4, "W (Hiver)", "#00CC96"),
            (-0.9, "WNA", "#00CC96")
        ]
        for y, label, color in niveaux_mer:
            fig2.add_shape(type="line", x0=0, y0=y, x1=0.8, y1=y, line=dict(color=color, width=4))
            fig2.add_annotation(x=0.9, y=y, text=label.split()[0], showarrow=False, font=dict(color=color, size=12), xanchor="left")
            
        # Lignes de charge à gauche (Eau douce)
        niveaux_douce = [
            (0.8, "TF (Tropic Fresh)", "#636EFA"),
            (0.3, "F (Fresh Water)", "#636EFA")
        ]
        for y, label, color in niveaux_douce:
            fig2.add_shape(type="line", x0=-0.8, y0=y, x1=0, y1=y, line=dict(color=color, width=4))
            fig2.add_annotation(x=-0.9, y=y, text=label.split()[0], showarrow=False, font=dict(color=color, size=12), xanchor="right")

        # Ajustement des axes et marges
        fig2.update_layout(
            showlegend=False,
            xaxis=dict(visible=False, range=[-1.5, 1.5]),
            yaxis=dict(visible=False, range=[-1.8, 1.8]),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            template="plotly_white"
        )
        
        st.plotly_chart(fig2, use_container_width=True)

        st.image("paradoxe_creux_plein.jpg", caption="Marque de Plimsoll sur une coque", use_container_width=True)


    col_bd_bathum2, col_bd_bathum3 = st.columns(2)

    with col_bd_bathum2:
        st.write("**La BD humoristique textuelle : Le test du capitaine**")
        st.info(
            "**Case 1 :** Un vieux loup de mer en ciré jaune inspecte son cargo en acier rempli de cales vides : 'Regardez-moi cette merveille, dix mille tonnes de métal et ça flotte comme une plume !'.\n\n"
            "**Case 2 :** Un docker empile une montagne gigantesque de caisses de fonte lourde sur le pont arrière. Le navire commence à pencher dangereusement en grinçant du métal : 'Capitaine ! On est en train de dépasser la marque rouge de sécurité sur la coque !'.\n\n"
            "**Case 3 :** Le capitaine hausse les épaules en ricanant : 'Balivernes ! Archimède est mon ami, il va pousser plus fort par-dessous !'. Les petites bulles d'eau sous la quille grimacent sous le poids écrasant.\n\n"
            "**Case 4 :** Une vague arrive, l'eau dépasse la ligne limite et s'engouffre par les fenêtres. Le navire descend tout droit vers le fond tandis que le capitaine flotte dans sa bouée en caoutchouc en marmonnant : 'D'accord... Le volume d'air était utile, j'ai compris la leçon'."
        )
    with col_bd_bathum3:
        try:
            # L'image utilise bien le nom exact configuré dans votre projet
            st.image("archimede_bateau.jpeg", caption="Vais-je arriver à bon port??? ", use_container_width=True)
        except Exception:
            st.warning("L'image 'archimede_bateau.jpeg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")
        
    st.divider()


    st.subheader("Simulateur dynamique de ligne de flottaison d'un cargo")
    st.write(
        "Utilisez les curseurs pour modifier la masse du chargement et le volume de la coque. "
        "Observez comment un bateau plus large (plus de volume) s'enfonce moins dans l'eau."
    )
    
    # 1. Les deux curseurs de contrôle
    col_param1, col_param2 = st.columns(2)
    with col_param1:
        poids_marchandise = st.slider("Masse de cargaison (en tonnes) :", min_value=0, max_value=1200, value=400, step=100, key="slider_cargo_weight")
    with col_param2:
        largeur_coque = st.slider("Volume / Largeur du bateau (mètres) :", min_value=3.0, max_value=5.5, value=4.5, step=0.5, key="slider_ship_volume")
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    # Paramètres fixes du cargo
    poids_coque_vide = 500.0
    poids_total_cargo = poids_coque_vide + poids_marchandise
    
    # Calcul de la section de la coque (Surface de flottaison proportionnelle à la largeur choisie)
    # Plus la coque est large, plus la surface d'appui est grande
    surface_flottaison = largeur_coque * 100.0 
    
    # Calcul de l'enfoncement (hauteur immergée)
    enfoncement_coque = poids_total_cargo / surface_flottaison
    
    fig_bat, ax_bat = plt.subplots(figsize=(5, 4.2), facecolor="white")
    ax_bat.set_facecolor("white")
    
    # Dessin de l'eau (ligne d'eau fixe à y = 1.8)
    ax_bat.add_patch(patches.Rectangle((0, 0), 6.0, 1.8, facecolor="#0284c7", alpha=0.4, zorder=1))
    ax_bat.axhline(1.8, color="#0284c7", linewidth=2, linestyle="-", zorder=2)
    
    # Positionnement vertical de la coque selon l'enfoncement calculé
    y_fond_coque = 1.8 - enfoncement_coque
    y_haut_coque = y_fond_coque + 1.5  # Hauteur totale de la coque toujours fixe = 1.5
    
    # Calcul de la géométrie horizontale de la coque (centrée sur l'écran)
    x_centre = 3.0
    demi_largeur = largeur_coque / 2.0
    
    x_arriere_bas = x_centre - demi_largeur + 0.4
    x_arriere_haut = x_centre - demi_largeur
    x_avant_bas = x_centre + demi_largeur - 0.4
    x_avant_haut = x_centre + demi_largeur
    
    # Dessin de la coque du navire avec ses nouvelles dimensions dynamiques
    coque_points = [
        [x_arriere_haut, y_haut_coque],       # Arrière haut
        [x_arriere_bas, y_fond_coque],         # Arrière bas
        [x_avant_bas, y_fond_coque],           # Avant bas
        [x_avant_haut, y_haut_coque]           # Avant haut (proue)
    ]
    ax_bat.add_patch(patches.Polygon(coque_points, facecolor="#1e293b", edgecolor="#0f172a", linewidth=2.5, zorder=3))
    
    # Dessin des conteneurs chargés sur le pont (visibles si poids > 0)
    if poids_marchandise > 0:
        nb_blocs = int(poids_marchandise / 200)
        # On ajuste l'écartement des blocs pour qu'ils restent centrés sur le pont mobile
        x_depart_conteneur = x_centre - (max(1, nb_blocs) * 0.7 / 2)
        for b in range(max(1, nb_blocs)):
            ax_bat.add_patch(patches.Rectangle((x_depart_conteneur + b*0.75, y_haut_coque), 0.6, 0.4, facecolor="#b91c1c", edgecolor="white", linewidth=1, zorder=4))
            
    # Calcul des vecteurs forces pour affichage des flèches explicites
    x_g = x_centre
    y_g = y_fond_coque + 0.8  # Centre de gravité
    y_c = y_fond_coque + (enfoncement_coque / 2.0)  # Centre de carène au milieu de la zone immergée
    
    longueur_force = 0.4 + (poids_total_cargo / 1700.0) * 1.0
    
    # Flèche Poids (vers le bas, noir)
    ax_bat.arrow(x_g, y_g, 0, -longueur_force, head_width=0.12, head_length=0.12, fc="black", ec="black", linewidth=2.5, length_includes_head=True, zorder=5)
    ax_bat.text(x_g + 0.15, y_g - (longueur_force / 2), r"$\vec{P}$", color="black", weight="bold", fontsize=12)
    
    # Flèche Poussée d'Archimède (vers le haut, bleu roi)
    ax_bat.arrow(x_g, y_c, 0, longueur_force, head_width=0.12, head_length=0.12, fc="#1d4ed8", ec="#1e3a8a", linewidth=2.5, length_includes_head=True, zorder=5)
    ax_bat.text(x_g - 0.35, y_c + (longueur_force / 2), r"$\vec{\Pi}$", color="#1d4ed8", weight="bold", fontsize=12)
    
    ax_bat.set_xlim(0, 6)
    ax_bat.set_ylim(0, 3.5)
    ax_bat.axis("off")
    st.pyplot(fig_bat)
    st.caption(f"Statut : Poids = {poids_total_cargo:.0f} t (Vide + Charge) | Largeur = {largeur_coque} m | Enfoncement = {enfoncement_coque:.2f} m")
    



    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 3 ---

    if "suite_verrouille_tab3_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab3_archimede = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_archimede
    
    # Affichage de l'Atelier d'évaluation 3
    afficher_atelier_flottaison_bateaux(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier La flottaison des bateaux.",
        key="check_certif_arch3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_arch_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q3 += 1.0

            score_t3 = 0.0
            if "champs_arch3_clean" in st.session_state:
                for ligne in st.session_state.champs_arch3_clean:
                    cle = ligne[-1]
                    # Index [2] pour cibler le mot attendu et non le tuple complet
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_arch3_clean", "Choisir...") == attendu: 
                        score_t3 += 1.0

            st.session_state.score_final_suite3_arch = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 3 ---
    if st.session_state.get("suite_verrouille_tab3_archimede", False):
        scr1_t3 = st.session_state.get("score_final_suite3_arch", 0.0) / 2.0
        scr2_t3 = st.session_state.get("score_final_suite3_arch", 0.0) / 2.0
        tot_s_t3 = st.session_state.get("score_final_suite3_arch", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER FLOTTAISON SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_arch3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Flottaison - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 3 : Architecture coque creuse, centre de carène et flottaison des navires</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab3_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_arch3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 3
        if "champs_arch3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch3_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 3
        html_export_arch3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch3 = preparer_nom_fichier("Rapport_Flottaison_Bateaux").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_arch3,
            file_name=nom_fichier_html_arch3,
            mime="text/html",
            use_container_width=True
        )

with tab4:
    st.header("Application dans les différents fluides")
    
    # --- SECTION COURS : L'INFLUENCE DU FLUIDE ---
    st.subheader("La variabilité de la poussée selon la nature du milieu")
    st.write(
        "L'intensité de la poussée d'Archimède dépend de trois facteurs. Pour un objet de forme et de volume fixes, "
        "la force dépend exclusivement de la **masse volumique ($\\rho$) du fluide** qui l'entoure. "
        "Plus les molécules du fluide sont lourdes et serrées, plus elles s'opposeront à l'immersion du solide "
        "et exerceront une poussée ascendante importante.\n\n"
        "Voici les valeurs de référence des fluides les plus courants étudiés au laboratoire :\n"
        "* **L'huile de moteur :** $\\rho \\approx 800 \\text{ kg/m}^3$ (Plus légère que l'eau, poussée plus faible).\n"
        "* **L'eau douce pure :** $\\rho = 1000 \\text{ kg/m}^3$ (La valeur étalon universelle).\n"
        "* **L'eau de mer saturée en sel :** $\\rho \\approx 1050 \\text{ à } 1200 \\text{ kg/m}^3$ (Plus lourde, poussée supérieure).\n"
        "* **La glycérine pure :** $\\rho = 1260 \\text{ kg/m}^3$ (Très dense, poussée très intense).\n"
        "* **L'air ambiant :** $\\rho \\approx 1{,}2 \\text{ kg/m}^3$ (Masse volumique infime, poussée imperceptible sur les solides lourds)."
    )
    
    st.divider()
    col_graph_fl, col_bd_fl = st.columns([0.55, 0.45])
    
    with col_graph_fl:
        st.write("**La BD humoristique textuelle : Le grand saut des cubes**")
        st.info(
            "**Case 1 :** Un cube en plastique dur de $900 \\text{ kg/m}^3$ se présente devant trois bassins alignés : un pot d'huile, une cuve d'eau pure et un baril de glycérine visqueuse.\n\n"
            "**Case 2 :** Il saute dans le premier pot d'huile lourde. Les molécules d'huile, trop légères ($800 \\text{ kg/m}^3$), s'écartent en panique : 'Ah ! Il est trop dense pour nous, on n'arrive pas à le retenir !'. Le cube frappe le fond du pot dans un bruit sourd.\n\n"
            "**Case 3 :** Il saute dans la cuve d'eau pure ($1000 \\text{ kg/m}^3$). Les molécules d'eau se bousculent et parviennent à le bloquer juste avant la noyade. Le cube flotte timidement, le nez hors de l'eau.\n\n"
            "**Case 4 :** Il plonge enfin dans le baril de glycérine ($1260 \\text{ kg/m}^3$). Les molécules de glycérine, unies comme un mur de briques solides, le repoussent instantanément vers le ciel : 'Pas chez nous, l'ami ! Tu es un poids plume pour nous !'. Le cube se retrouve assis en surface, totalement au sec."
        )

    with col_bd_fl:
        try:
            # L'image utilise bien le nom exact configuré dans votre projet
            st.image("archimede_cube.jpeg", caption="Vais-je me noyer ??? ", use_container_width=True)
        except Exception:
            st.warning("L'image 'archimede_cube.jpeg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")
    
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE COMPARATIF DES FLUIDES ---
    st.subheader("Simulateur dynamique de poussée multi-fluides")
    st.write(
        "Sélectionnez un fluide dans le menu déroulant ci-dessous. Un bloc solide d'une densité fixe "
        "de $900 \\text{ kg/m}^3$ y sera plongé. Observez comment la ligne de flottaison et les vecteurs de forces "
        "s'ajustent instantanément à l'écran."
    )
    
    # Menu déroulant de sélection du fluide actif
    nom_fluide_choisi = st.selectbox(
        "Choisir le fluide de l'échantillon :",
        options=["Huile de moteur (800 kg/m³)", "Eau douce pure (1000 kg/m³)", "Glycérine pure (1260 kg/m³)"],
        key="selectbox_fluid_nature"
    )
    
    # Association de la densité correspondante
    if "Huile" in nom_fluide_choisi:
        rho_fluide_sim = 800.0
        couleur_fluide = "#f59e0b"  # Ambré
    elif "Eau" in nom_fluide_choisi:
        rho_fluide_sim = 1000.0
        couleur_fluide = "#38bdf8"  # Bleu clair
    else:
        rho_fluide_sim = 1260.0
        couleur_fluide = "#cbd5e1"  # Transparent opalin
        

        
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    # Objet fixe de densité 900 kg/m³
    rho_bloc_fixe = 900.0
    cote_b = 1.0
    
    fig_fl, ax_fl = plt.subplots(figsize=(5, 4.2), facecolor="white")
    ax_fl.set_facecolor("white")
    
    # Dessin du fluide sélectionné (niveau à y = 2.0)
    ax_fl.add_patch(patches.Rectangle((0.5, 0), 4.0, 2.0, facecolor=couleur_fluide, alpha=0.5, zorder=1))
    ax_fl.axhline(2.0, color="#475569", linewidth=2, linestyle="-", zorder=2)
    
    if rho_bloc_fixe < rho_fluide_sim:
        # Cas de flottaison partielle
        ratio_imm = rho_bloc_fixe / rho_fluide_sim
        y_base_b = 2.0 - ratio_imm
        statut_fl = "Le bloc flotte à l'équilibre"
        p_val = 1.0 * rho_bloc_fixe * 9.81 / 1000.0
        pi_val = p_val
    else:
        # Cas où le bloc coule (le bloc de 900 coule dans l'huile de 800)
        y_base_b = 0.2
        statut_fl = "Le bloc est trop lourd et COULE au fond"
        p_val = 1.0 * rho_bloc_fixe * 9.81 / 1000.0
        pi_val = 1.0 * rho_fluide_sim * 9.81 / 1000.0
        
    # Dessin du bloc en bois ($900\text{ kg/m}^3$)
    ax_fl.add_patch(patches.Rectangle((2.0, y_base_b), cote_b, cote_b, facecolor="#b45309", edgecolor="#1e293b", linewidth=2, zorder=3))
    
    # Tracé des axes vectoriels
    x_c = 2.5
    y_g = y_base_b + 0.5
    y_car = y_base_b + ((2.0 - y_base_b)/2.0) if rho_bloc_fixe < rho_fluide_sim else y_base_b + 0.5
    
    echelle_f = 0.6 / (900.0 * 9.81 / 1000.0)
    len_p = p_val * echelle_f
    len_pi = pi_val * echelle_f
    
    # Poids (Noir)
    ax_fl.arrow(x_c, y_g, 0, -len_p, head_width=0.12, head_length=0.12, fc="black", ec="black", linewidth=2.5, length_includes_head=True, zorder=4)
    ax_fl.text(x_c + 0.15, y_g - (len_p / 2), r"$\vec{P}$", color="black", weight="bold", fontsize=12)
    
    # Poussée (Bleu)
    ax_fl.arrow(x_c, y_car, 0, len_pi, head_width=0.12, head_length=0.12, fc="#1d4ed8", ec="#1e3a8a", linewidth=2.5, length_includes_head=True, zorder=4)
    ax_fl.text(x_c - 0.35, y_car + (len_pi / 2), r"$\vec{\Pi}$", color="#1d4ed8", weight="bold", fontsize=12)
    
    ax_fl.set_xlim(0, 5)
    ax_fl.set_ylim(0, 3.5)
    ax_fl.axis("off")
    st.pyplot(fig_fl)
    st.caption(f"Résultat : {statut_fl} (Poids = {p_val:.1f} N | Poussée = {pi_val:.1f} N)")


    
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 4 ---
    if "suite_verrouille_tab4_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab4_archimede = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_archimede

    # Affichage de l'Atelier d'évaluation 4
    afficher_atelier_differents_fluides(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Application dans les différents fluides.",
        key="check_certif_arch4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_arch_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q4 += 1.0

            score_t4 = 0.0
            if "champs_arch4_clean" in st.session_state:
                for ligne in st.session_state.champs_arch4_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_arch4_clean", "Choisir...") == attendu: score_t4 += 1.0

            st.session_state.score_final_suite4_arch = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 4 ---
    if st.session_state.get("suite_verrouille_tab4_archimede", False):
        scr1_t4 = st.session_state.get("score_final_suite4_arch", 0.0) / 2.0
        scr2_t4 = st.session_state.get("score_final_suite4_arch", 0.0) / 2.0
        tot_s_t4 = st.session_state.get("score_final_suite4_arch", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MULTI-FLUIDES SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_arch4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Multi-Fluides - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 4 : Influence de la densité des liquides et des gaz sur l'intensité d'Archimède</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #d97706;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab4_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_arch4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 4
        if "champs_arch4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch4_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 4
        html_export_arch4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch4 = preparer_nom_fichier("Rapport_Different_Fluides").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_arch4,
            file_name=nom_fichier_html_arch4,
            mime="text/html",
            use_container_width=True
        )


with tab5:
    st.header("Application le domaine de la maintenance")
    
    # --- SECTION COURS : MAINTENANCE ET HYDROSTATIQUE ---
    st.subheader("Surveillance des réservoirs et capteurs de niveau hydrostatiques")
    st.write(
        "Dans l'industrie chimique, pétrolière ou agroalimentaire, la maintenance préventive des réservoirs "
        "de stockage est un enjeu critique. Pour mesurer en temps réel le volume de fluide confiné dans une cuve "
        "et prévenir tout risque de débordement ou de marche à sec des pompes, les techniciens exploitent directement "
        "la poussée d'Archimède via des **capteurs de niveau à plongeur**.\n\n"
        "Un plongeur cylindrique de volume connu est suspendu à un capteur de force électronique (dynamomètre industriel) "
        "et immergé verticalement dans la cuve. Au fur et à mesure que le niveau du liquide monte, le volume immergé augmente, "
        "ce qui élève l'intensité de la poussée d'Archimède. L'appareil enregistre cette perte de poids apparent "
        "et en déduit avec précision la hauteur du produit liquide."
    )
    
    st.divider()
    
    st.subheader("Diagnostic de pannes et étalonnage")
    st.write(
        "Les équipes de maintenance doivent faire face à deux types d'anomalies courantes sur ces installations :\n"
        "* **Le défaut de dérive de mesure :** Si l'huile ou le produit chimique stocké est remplacé par une formule dont la "
        "masse volumique est différente, la force de poussée d'Archimède s'en trouve modifiée à volume égal. Le capteur donne alors "
        "une fausse indication de niveau. Un **étalonnage** complet de l'appareil avec un fluide témoin est obligatoire.\n"
        "* **La défaillance du flotteur :** Les flotteurs ou plongeurs industriels sont creux pour être légers. Si une fissure de corrosion "
        "apparaît sur la paroi, le fluide pénètre à l'intérieur. Le poids de l'objet augmente brutalement, la force de gravité devient "
        "très supérieure à la poussée d'Archimède, et le plongeur coule au fond de la cuve, déclenchant une fausse alarme de niveau bas."
    )


    col_graph_maint, col_bd_maint = st.columns([0.55, 0.45])
    
    with col_graph_maint:
        st.write("**La BD humoristique textuelle : Le mystère de la Cuve 4**")
        st.info(
            "**Case 1 :** Un technicien de maintenance en bleu de travail consulte sa console de contrôle d'usine. Une alarme rouge clignote en hurlant : 'Alerte ! Cuve 4 vide ! Niveau critique !'.\n\n"
            "**Case 2 :** Courant sur la passerelle avec sa clé à molette, le technicien regarde par le hublot de visite : la cuve est pourtant pleine de liquide jusqu'au sommet ! Il tape sur le cadran de l'indicateur : 'Mais qu'est-ce qui t'arrive, vieux capteur ? Tu as perdu la mémoire ?'.\n\n"
            "**Case 3 :** À l'intérieur du liquide, le plongeur de mesure métallique creux gît lamentablement au fond de la cuve. On voit de petites bulles s'échapper d'une fissure sur sa soudure : 'Glouglou... Je suis percé ! L'eau est entrée en douce... Je pèse dix fois trop lourd désormais !'.\n\n"
            "**Case 4 :** Le technicien remplace le plongeur défaillant par un neuf étanche. Le nouveau plongeur remonte aussitôt comme un bouchon, suspendu à son câble. La flèche bleue d'Archimède se déploie et la console verte s'éteint : 'Anomalie résolue, l'hydrostatique a repris ses droits !'."
        )

    with col_bd_maint:

        try:
            # L'image utilise bien le nom exact configuré dans votre projet
            st.image("archimede_mm.jpeg", caption="Quelle plongée !", use_container_width=True)
        except Exception:
            st.warning("L'image 'archimede_mm.jpeg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")
                
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE DE CUVE ET DÉTECTION DE FUITE ---
    st.subheader("Simulateur dynamique de vidange de cuve et force de poussée")
    st.write(
        "Actionnez le curseur pour simuler le niveau de remplissage de la cuve industrielle. "
        "Observez comment le volume immergé du plongeur de maintenance (le cylindre gris) s'ajuste, "
        "modifiant la taille de la flèche bleue de la poussée d'Archimède."
    )
    
    # Curseur interactif de hauteur de liquide dans la cuve
    hauteur_liquide = st.slider("Ajuster le niveau du liquide dans la cuve (en mètres) :", min_value=0.0, max_value=3.0, value=2.0, step=0.2, key="slider_maintenance_level")
    

    st.divider()

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    fig_mn, ax_mn = plt.subplots(figsize=(5, 4.2), facecolor="white")
    ax_mn.set_facecolor("white")
    
    # Dessin de la cuve industrielle (parois grises)
    ax_mn.plot([1.0, 1.0, 4.0, 4.0], [3.2, 0.2, 0.2, 3.2], color="#475569", linewidth=3, zorder=2)
    
    # Dessin du liquide (hauteur variable)
    if hauteur_liquide > 0:
        ax_mn.add_patch(patches.Rectangle((1.02, 0.22), 2.96, hauteur_liquide, facecolor="#0284c7", alpha=0.5, zorder=1))
        
    # Plongeur de mesure fixe suspendu (x = 2.2, de y = 0.5 à y = 2.5, hauteur = 2.0)
    ax_mn.add_patch(patches.Rectangle((2.2, 0.5), 0.6, 2.0, facecolor="#94a3b8", edgecolor="#1e293b", linewidth=2, zorder=3))
    # Câble de suspension
    ax_mn.plot([2.5, 2.5], [2.5, 3.5], color="#1e293b", linewidth=1.5, linestyle="-", zorder=2)
    
    # Calcul du volume immergé du plongeur
    # Le plongeur s'étend de y=0.5 à y=2.5. Sa hauteur totale est 2.0.
    if hauteur_liquide + 0.2 <= 0.5:
        hauteur_immergee_plongeur = 0.0
    elif hauteur_liquide + 0.2 >= 2.5:
        hauteur_immergee_plongeur = 2.0
    else:
        hauteur_immergee_plongeur = (hauteur_liquide + 0.2) - 0.5
        
    # Intensité des forces pour affichage des flèches vectorielles
    # Poids propre du plongeur fixe (Noir)
    poids_plongeur = 15.0
    poussee_maint = hauteur_immergee_plongeur * 6.0  # Proportionnel au niveau immergé
    
    x_arrow = 2.5
    y_arrow_p = 1.5
    
    # Échelle de tracé
    scale_m = 1.2 / 15.0
    len_p_m = poids_plongeur * scale_m
    len_pi_m = poussee_maint * scale_m
    
    # Flèche Poids (vers le bas)
    ax_mn.arrow(x_arrow, y_arrow_p, 0, -len_p_m, head_width=0.1, head_length=0.1, fc="black", ec="black", linewidth=2.5, length_includes_head=True, zorder=4)
    ax_mn.text(x_arrow + 0.15, y_arrow_p - (len_p_m / 2), r"$\vec{P}$", color="black", weight="bold", fontsize=12)
    
    # Flèche Poussée d'Archimède (vers le haut, s'affiche si la hauteur immergée > 0)
    if len_pi_m > 0:
        ax_mn.arrow(x_arrow, 0.5 + (hauteur_immergee_plongeur / 2.0), 0, len_pi_m, head_width=0.1, head_length=0.1, fc="#1d4ed8", ec="#1e3a8a", linewidth=2.5, length_includes_head=True, zorder=4)
        ax_mn.text(x_arrow - 0.35, 0.5 + (hauteur_immergee_plongeur / 2.0) + (len_pi_m / 2), r"$\vec{\Pi}$", color="#1d4ed8", weight="bold", fontsize=12)
        
    ax_mn.set_xlim(0, 5)
    ax_mn.set_ylim(0, 4)
    ax_mn.axis("off")
    st.pyplot(fig_mn)
    st.caption(f"Bilan de maintenance : Hauteur immergée du plongeur = {hauteur_immergee_plongeur:.2f} m | Poussée d'Archimède = {poussee_maint:.1f} N")



    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab5_archimede = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_archimede

    # Affichage de l'Atelier d'évaluation 5
    afficher_atelier_maintenance(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Application le domaine de la maintenance.",
        key="check_certif_arch5_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_arch_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q5 += 1.0

            score_t5 = 0.0
            if "champs_arch5_clean" in st.session_state:
                for ligne in st.session_state.champs_arch5_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_arch5_clean", "Choisir...") == attendu: score_t5 += 1.0

            st.session_state.score_final_suite5_arch = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 5 ---
    if st.session_state.get("suite_verrouille_tab5_archimede", False):
        scr1_t5 = st.session_state.get("score_final_suite5_arch", 0.0) / 2.0
        scr2_t5 = st.session_state.get("score_final_suite5_arch", 0.0) / 2.0
        tot_s_t5 = st.session_state.get("score_final_suite5_arch", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MAINTENANCE SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_arch5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Maintenance - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 5 : Diagnostic d'avaries de niveau, étalonnage de plongeurs et maintenance de cuves</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #047857;">
                Note obtenue au Quiz Technique : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab5_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_arch5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 5
        if "champs_arch5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch5_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch5_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 5
        html_export_arch5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch5 = preparer_nom_fichier("Rapport_Maintenance_Cuves").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_arch5,
            file_name=nom_fichier_html_arch5,
            mime="text/html",
            use_container_width=True)


with tab6:
    st.header("Application dans le domaine des travaux publics")
    
    # --- SECTION COURS : TRAVAUX PUBLICS ET HYDROSTATIQUE ---
    st.subheader("La problématique des sous-pressions hydrostatiques en génie civil")
    st.write(
        "Dans le domaine des travaux publics (TP) et du génie civil, l'eau contenue dans le sol représente une force "
        "majeure que les ingénieurs doivent impérativement maîtriser. Tout ouvrage d'art enterré ou semi-enterré "
        "(comme un parking souterrain, une piscine municipale vide ou une canalisation de grand diamètre) se comporte "
        "exactement comme la coque d'un navire : il subit la **poussée d'Archimède** de la part de la nappe phréatique environnante.\n\n"
        "Si le poids total de la structure en béton est inférieur à la force ascendante de l'eau déplacée, l'ouvrage subit "
        "un soulèvement accidentel par sous-pression. Ce déplacement peut fissurer les fondations, briser les réseaux "
        "et soulever les revêtements de chaussée de manière destructrice."
    )
    
    st.divider()
    
    st.subheader("Les solutions techniques de lestage et d'ancrage")
    st.write(
        "Pour garantir la stabilité hydrostatique des ouvrages face aux crues, les constructeurs appliquent deux méthodes :\n"
        "* **Le lestage par radier pesant :** On augmente la masse de la structure en coulant une dalle de fondation en béton armé "
        "très épaisse (appelée radier). Le béton possédant une masse volumique élevée ($2500 \\text{ kg/m}^3$), son surpoids compense "
        "la poussée ascendante de l'eau.\n"
        "* **Le rabattement de nappe temporaire :** Pendant la phase de chantier, tant que le béton n'est pas entièrement coulé, "
        "on installe des pompes de forage en continu autour des fouilles pour abaisser artificiellement le niveau de la nappe "
        "et travailler hors d'eau."
    )


    col_graph_tp, col_bd_tp = st.columns([0.55, 0.45])
    
    with col_graph_tp:
        st.write("**La BD humoristique textuelle : Le mystère de la buse volante**")
        st.info(
            "**Case 1 :** Un chef de chantier en casque blanc contemple fièrement une immense tranchée ouverte au milieu de la rue : 'Voilà ! Une magnifique conduite d'évacuation en béton de deux mètres de large, posée bien au sec !'.\n\n"
            "**Case 2 :** Pendant la nuit, un violent orage éclate. Les nappes souterraines débordent et s'infiltrent sous la route. Les petites molécules d'eau souterraines s'agglomèrent sous la buse vide : 'Regardez ce gros cylindre plein d'air ! C'est un vrai ballon de plage ! Tous ensemble, poussez vers le haut !'.\n\n"
            "**Case 3 :** Le lendemain matin, le chef de chantier arrive sur le site et pousse un cri d'effroi. La route en goudron est totalement soulevée et éventrée. La buse en béton flotte tranquillement au milieu d'une mare de boue comme un canard en plastique : 'Par les pouvoirs d'Archimède ! Le tuyau s'est envolé !'.\n\n"
            "**Case 4 :** L'ingénieur conseil arrive en souriant et lui montre le plan : 'Mon ami, un tuyau vide déplace un volume d'eau énorme. Pour le prochain chantier, n'oublie pas de couler un lourd radier de lestage en béton par-dessus pour clouer le tuyau au fond !'."
        )
    with col_bd_tp:

        try:
            st.image("archimede_tp.jpeg", caption="Remontée spectaculaire !", use_container_width=True)
        except Exception:
            st.warning("L'image 'archimede_tp.jpeg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")

        
    
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE DE CANALISATION INONDÉE ---
    st.subheader("Simulateur dynamique de poussée sur une buse de TP enterrée")
    st.write(
        "Faites varier le niveau de la nappe phréatique dans le sol à l'aide du curseur. "
        "Observez l'évolution des forces s'exerçant sur une canalisation d'évacuation vide (le cercle gris) enterrée sous la route."
    )
    
    # Curseur interactif de hauteur de nappe phréatique
    niveau_nappe = st.slider("Ajuster le niveau de la nappe phréatique dans le sol (en mètres) :", min_value=0.0, max_value=2.5, value=1.2, step=0.2, key="slider_civil_engineering_water")
    

    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    fig_tp, ax_tp = plt.subplots(figsize=(5, 4.2), facecolor="white")
    ax_mn.set_facecolor("white") if 'ax_mn' in locals() else ax_tp.set_facecolor("white")
    
    # Dessin du sol (fond brun)
    ax_tp.add_patch(patches.Rectangle((0, 0), 6.0, 3.0, facecolor="#f5e0ce", edgecolor="#854d0e", linewidth=1.5, zorder=1))
    # Ligne de la chaussée (Goudron noir à y = 3.0)
    ax_tp.axhline(3.0, color="#1e293b", linewidth=6, label="Chaussée", zorder=3)
    
    # Dessin de la zone ennoyée par la nappe phréatique (bleu transparent)
    if niveau_nappe > 0:
        ax_tp.add_patch(patches.Rectangle((0, 0), 6.0, niveau_nappe, facecolor="#0284c7", alpha=0.4, zorder=2))
        ax_tp.axhline(niveau_nappe, color="#0284c7", linewidth=1.5, linestyle="--", zorder=2)
        
    # Dessin de la canalisation circulaire vide (centre x = 3.0, y = 1.5, rayon = 0.6)
    rayon_buse = 0.6
    y_centre_buse = 1.5
    ax_tp.add_patch(patches.Circle((3.0, y_centre_buse), rayon_buse, facecolor="#cbd5e1", edgecolor="#475569", linewidth=2.5, zorder=4))
    
    # Calcul de la fraction immergée de la buse dans la nappe
    # La buse s'étend de y = 0.9 à y = 2.1
    y_bas_buse = y_centre_buse - rayon_buse
    y_haut_buse = y_centre_buse + rayon_buse
    
    if niveau_nappe <= y_bas_buse:
        fraction_volume_inonde = 0.0
    elif niveau_nappe >= y_haut_buse:
        fraction_volume_inonde = 1.0
    else:
        fraction_volume_inonde = (niveau_nappe - y_bas_buse) / (2.0 * rayon_buse)
        
    # Intensité des forces fictives
    poids_buse_vide = 6.0
    poussee_tp_val = fraction_volume_inonde * 14.0  # Force ascendante proportionnelle
    
    x_tp_arrow = 3.0
    
    # Échelle graphique
    scale_tp = 1.0 / 14.0
    len_p_tp = poids_buse_vide * scale_tp
    len_pi_tp = poussee_tp_val * scale_tp
    
    # Flèche Poids (vers le bas)
    ax_tp.arrow(x_tp_arrow, y_centre_buse, 0, -len_p_tp, head_width=0.12, head_length=0.12, fc="black", ec="black", linewidth=2.5, length_includes_head=True, zorder=5)
    ax_tp.text(x_tp_arrow + 0.15, y_centre_buse - (len_p_tp / 2), r"$\vec{P}$", color="black", weight="bold", fontsize=12)
    
    # Flèche Poussée d'Archimède (vers le haut)
    if len_pi_tp > 0:
        y_base_poussee_fleche = y_bas_buse + (fraction_volume_inonde * rayon_buse)
        ax_tp.arrow(x_tp_arrow, y_base_poussee_fleche, 0, len_pi_tp, head_width=0.12, head_length=0.12, fc="#1d4ed8", ec="#1e3a8a", linewidth=2.5, length_includes_head=True, zorder=5)
        ax_tp.text(x_tp_arrow - 0.35, y_base_poussee_fleche + (len_pi_tp / 2), r"$\vec{\Pi}$", color="#1d4ed8", weight="bold", fontsize=12)
        
    ax_tp.set_xlim(0, 6)
    ax_tp.set_ylim(0, 3.8)
    ax_tp.axis("off")
    st.pyplot(fig_tp)
    
    statut_tp = "Ouvrage STABLE" if poids_buse_vide >= poussee_tp_val else "RISQUE DE SOULÈVEMENT DE LA ROUTE !"
    st.caption(f"Bilan TP : Volume ennoyé = {fraction_volume_inonde*100:.0f} % | Poussée d'Archimède = {poussee_tp_val:.1f} N | Statut : {statut_tp}")


    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 6 ---
    if "suite_verrouille_tab6_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab6_archimede = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_archimede

    # Affichage de l'Atelier d'évaluation 6
    afficher_atelier_travaux_publics(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    
    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Application dans le domaine des travaux publics.",
        key="check_certif_arch6_final_net",
        disabled=verrou_at6,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_arch_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            if "ordre_quiz_tab6_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q6 += 1.0

            score_t6 = 0.0
            if "champs_arch6_clean" in st.session_state:
                for ligne in st.session_state.champs_arch6_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_arch6_clean", "Choisir...") == attendu: score_t6 += 1.0

            st.session_state.score_final_suite6_arch = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 6 ---
    if st.session_state.get("suite_verrouille_tab6_archimede", False):
        scr1_t6 = st.session_state.get("score_final_suite6_arch", 0.0) / 2.0
        scr2_t6 = st.session_state.get("score_final_suite6_arch", 0.0) / 2.0
        tot_s_t6 = st.session_state.get("score_final_suite6_arch", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRAVAUX PUBLICS SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_arch6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Travaux Publics - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 6 : Analyse des sous-pressions, structures enterrées et dimensionnement de fondations lourdes</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b45309;">
                Note obtenue au Quiz Technique : <strong>{scr1_t6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s_t6:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab6_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_arch6 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 6
        if "champs_arch6_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch6_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch6_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 6
        html_export_arch6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch6 = preparer_nom_fichier("Rapport_Travaux_Publics").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_arch6,
            file_name=nom_fichier_html_arch6,
            mime="text/html",
            use_container_width=True
        )



with tab7:
    st.header("Application dans le domaine du transport routier")
    
    # --- SECTION COURS : TRANSPORT ROUTIER ET HYDROSTATIQUE ---
    st.subheader("La métrologie des fluides et la sécurité des hydrocarbures")
    st.write(
        "Dans le secteur du transport routier logistique, les camions-citernes acheminent quotidiennement "
        "des milliers de litres de fluides dont les masses volumiques varient fortement. Le contrôle de la masse "
        "totale en charge est une obligation légale pour respecter le Poids Total Autorisé en Charge (PTAC) "
        "et préserver l'intégrité des infrastructures routières.\n\n"
        "Pour mesurer le volume embarqué sans installer de balance sous le réservoir, les constructeurs exploitent "
        "la relation fondamentale de l'hydrostatique. Une sonde de pression relative est implantée au point le plus bas "
        "de la citerne. Elle mesure la pression exercée par la colonne de liquide. Cette pression étant directement "
        "proportionnelle à la hauteur ($h$) et à la masse volumique ($\\rho$) du fluide ($P = \\rho \\cdot g \\cdot h$), "
        "l'ordinateur de bord calcule instantanément le volume de carburant restant."
    )
    
    st.divider()
    
    st.subheader("La dynamique du ballottement et la sécurité active")
    st.write(
        "Le transport de matières liquides présente un risque de sécurité majeur : le **ballottement**. "
        "Lorsqu'une citerne n'est pas entièrement remplie, le liquide se déplace brutalement lors des virages, "
        "des accélérations ou des freinages. Ce déplacement déplace instantanément le centre de gravité global "
        "du camion, générant des transferts de charges violents sur les essieux pneumatiques et augmentant les risques "
        "de perte d'adhérence ou de retournement.\n\n"
        "Pour contrer cet effet mécanique dangereux, l'intérieur des citernes routières est sectorisé par des "
        "**cloisons brise-lames**. Ce sont des parois transversales métalliques percées de petits orifices qui "
        "freinent le déplacement du fluide et dissipent l'énergie cinétique de la vague liquide, maintenant le "
        "véhicule stable sur sa trajectoire."
    )


    col_graph_tr, col_bd_tr = st.columns([0.55, 0.45])
    
    with col_graph_tr:
        st.write("**La BD humoristique textuelle : Le coup de frein du laitier**")
        st.info(
            "**Case 1 :** Un chauffeur de camion-citerne transporte une cuve remplie à moitié de lait frais : 'La route est belle, le réservoir est léger, on va arriver en avance pour la livraison !'.\n\n"
            "**Case 2 :** Soudain, un feu passe au rouge. Le chauffeur écrase fermement la pédale de frein. À l'intérieur du réservoir sans cloison, les dix mille litres de lait glissent en bloc vers l'avant, formant une lame de fond géante.\n\n"
            "**Case 3 :** La vague de lait percute violemment la paroi avant de la citerne : 'Boum !'. Le transfert de masse projette le camion vers l'avant, faisant hurler les pneus sur le goudron. Le chauffeur s'agrippe au volant, les yeux ronds de frayeur.\n\n"
            "**Case 4 :** Le camion s'arrête de justesse au milieu du carrefour. Le chauffeur s'essuie le front tandis que le capteur de pression de fond oscille follement : 'Ouf... Demain, je demande un camion équipé de cloisons brise-lames pour calmer cette poussée d'Archimède mouvante !'."
        )


    with col_bd_tr:
        try:
            # L'image utilise bien le nom exact configuré dans votre projet
            st.image("archimede_routier.jpeg", caption="Quelle force !", use_container_width=True)
        except Exception:
            st.warning("L'image 'archimede_routier.jpeg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")

            
    
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE DE CITERNE ET PRESSION AU FOND ---
    st.subheader("Simulateur dynamique de hauteur de cargaison et pression hydrostatique")
    st.write(
        "Modifiez le curseur pour ajuster le niveau de remplissage de la citerne routière. "
        "Le schéma vectoriel calculera la pression s'exerçant sur le capteur de fond (le point rouge) "
        "et adaptera la flèche noire représentant la force de gravité exercée sur l'essieu."
    )
    
    # Curseur interactif de hauteur de carburant
    hauteur_citerne = st.slider("Ajuster le niveau de remplissage de la citerne (en mètres) :", min_value=0.0, max_value=2.0, value=1.5, step=0.1, key="slider_truck_fluid_height")
    

        
    st.divider()


    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    
    fig_tr, ax_tr = plt.subplots(figsize=(5, 4.2), facecolor="white")
    ax_tr.set_facecolor("white")
    
    # Dessin de la silhouette du camion (roues et cabine simplifiées)
    ax_tr.add_patch(patches.Circle((1.5, 0.4), 0.3, facecolor="#1e293b", edgecolor="black", zorder=2)) # Roue avant
    ax_tr.add_patch(patches.Circle((4.0, 0.4), 0.3, facecolor="#1e293b", edgecolor="black", zorder=2)) # Roue arrière
    ax_tr.add_patch(patches.Rectangle((0.6, 0.7), 0.8, 1.2, facecolor="#334155", zorder=2))           # Cabine
    
    # Dessin du réservoir de la citerne (ellipse ou rectangle arrondi, de x=1.5 à x=4.8, y=0.7 à y=2.7)
    ax_tr.add_patch(patches.Rectangle((1.5, 0.7), 3.3, 2.0, facecolor="#f1f5f9", edgecolor="#475569", linewidth=2.5, zorder=3))
    
    # Remplissage de carburant (Masse volumique essence = 800 kg/m³)
    if hauteur_citerne > 0:
        ax_tr.add_patch(patches.Rectangle((1.52, 0.72), 3.26, hauteur_citerne, facecolor="#f59e0b", alpha=0.6, zorder=1))
        
    # Point du capteur hydrostatique de fond (Orifice bas)
    ax_tr.plot(4.6, 0.75, marker="o", color="#b91c1c", markersize=6, zorder=4)
    
    # Calcul de la pression hydrostatique au fond (P = rho * g * h)
    pression_fond_pa = 800.0 * 9.81 * hauteur_citerne
    pression_bar = pression_fond_pa / 100000.0
    
    # Flèche de charge de gravité s'exerçant sur l'essieu arrière (proportionnelle au niveau)
    poids_essieu = 8.0 + (hauteur_citerne * 12.0)
    len_f_tr = poids_essieu * (1.2 / 32.0)
    
    ax_tr.arrow(4.0, 0.4, 0, -len_f_tr, head_width=0.12, head_length=0.12, fc="#b91c1c", ec="#7f1d1d", linewidth=2.5, length_includes_head=True, zorder=5)
    ax_tr.text(4.2, 0.4 - (len_f_tr / 2), r"$\vec{F}_{\text{charge}}$", color="#b91c1c", weight="bold", fontsize=11)
    
    ax_tr.set_xlim(0, 6)
    ax_tr.set_ylim(-1, 3.2)
    ax_tr.axis("off")
    st.pyplot(fig_tr)
    st.caption(f"Mesure embarquée : Pression hydrostatique lue = {pression_bar:.3f} bar | Hauteur de fluide = {hauteur_citerne:.2f} m")



    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 7 ---
    if "suite_verrouille_tab7_archimede" not in st.session_state:
        st.session_state.suite_verrouille_tab7_archimede = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_archimede

    # Affichage de l'Atelier d'évaluation 7
    afficher_atelier_transport_routier(verrouille=verrou_at7)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")
    
    case_certif_stat7 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Application dans le domaine du transport routier.",
        key="check_certif_arch7_final_net",
        disabled=verrou_at7,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_suite7_arch_official", use_container_width=True, disabled=verrou_at7):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat7: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q7 = 0.0
            if "ordre_quiz_tab7_arch_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab7_arch_aleatoire:
                    saisie = st.session_state.get(f"arch_at7_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q7 += 1.0

            score_t7 = 0.0
            if "champs_arch7_clean" in st.session_state:
                for ligne in st.session_state.champs_arch7_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_arch7_clean", "Choisir...") == attendu: score_t7 += 1.0

            st.session_state.score_final_suite7_arch = round(float(score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_archimede = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 7 ---
    if st.session_state.get("suite_verrouille_tab7_archimede", False):
        scr1_t7 = st.session_state.get("score_final_suite7_arch", 0.0) / 2.0
        scr2_t7 = st.session_state.get("score_final_suite7_arch", 0.0) / 2.0
        tot_s_t7 = st.session_state.get("score_final_suite7_arch", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRANSPORT ROUTIER SCELLÉ | Note de session : {tot_s_t7:.1f} / 20")

        html_export_arch7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Transport Routier - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 7 : Métrologie citernes, transferts de charge dynamique et cloisons brise-lames</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t7:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t7:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t7:.1f} / 10</strong><br>
                Note Totale de l'Atelier 7 : <strong>{tot_s_t7:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab7_arch_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_arch_aleatoire, 1):
                saisie = st.session_state.get(f"arch_at7_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_arch7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_arch7 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 7
        if "champs_arch7_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_arch7_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_arch7_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_arch7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 7
        html_export_arch7 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_arch7 = preparer_nom_fichier("Rapport_Transport_Routier").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 7 (.html)",
            data=html_export_arch7,
            file_name=nom_fichier_html_arch7,
            mime="text/html",
            use_container_width=True
        )



























