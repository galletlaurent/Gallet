
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application verin ",
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
st.title("Application verin")
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
    "Historique et production d'air",
    "Les distributeurs pneumatiques",
    "Le vérin simple effet",
    "Le vérin double effet",
    "Vérins rotatifs et autres actionneurs",
    "Application 1 : Serrage",
    "Application 2 : Tri de colis"

])

tab0 = onglets[0] # Identification
tab1 = onglets[1] # Historique et production d'air
tab2 = onglets[2] # Les distributeurs pneumatiques
tab3 = onglets[3] # Le vérin simple effet
tab4 = onglets[4] # Le vérin double effet
tab5 = onglets[5] # Vérins rotatifs et autres actionneurs
tab6 = onglets[6] # Application 1
tab7 = onglets[7] # Application 2



def afficher_atelier_application2(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 7 (Application 2 : Tri de colis) sur deux colonnes."""
    import random

    questions_pneu7_sources = [
        {"id": "qap2_1", "q": "Quel type d'actionneur effectue l'éjection ou le pivotement rapide des colis sur le tapis ?", "options": ["Un vérin double effet de course réduite", "Un vérin simple effet à ressort", "Un moteur à palettes continu"], "rep": "Un vérin double effet de course réduite"},
        {"id": "qap2_2", "q": "Quel type de distributeur est idéal pour assurer le va-et-vient ultra-rapide de ce vérin de tri ?", "options": ["Un distributeur 5/2 monostable (à rappel par ressort)", "Un distributeur 3/2 manuel", "Un distributeur 5/3 à centre fermé"], "rep": "Un distributeur 5/2 monostable (à rappel par ressort)"},
        {"id": "qap2_3", "q": "Quel capteur détecte la présence et la taille du colis avant d'ordonner son éjection ?", "options": ["Un capteur optique (cellule photoélectrique)", "Un manomètre à cadran", "Un thermomètre infrarouge"], "rep": "Un capteur optique (cellule photoélectrique)"},
        {"id": "qap2_4", "q": "Quelle grandeur physique règle-t-on pour augmenter la vitesse d'éjection du bras ?", "options": ["Le débit de l'air sortant", "La pression du manomètre", "La lubrification de l'unité FRL"], "rep": "Le débit de l'air sortant"},
        {"id": "qap2_5", "q": "Dans une commande monostable, que fait la tige du vérin si le courant électrique de l'automate se coupe subitement ?", "options": ["Elle rentre immédiatement en position initiale", "Elle reste bloquée en fin de course", "Elle continue de sortir lentement"], "rep": "Elle rentre immédiatement en position initiale"},
        {"id": "qap2_6", "q": "Pour éviter un choc destructeur du piston en fin de course à haute cadence, on exploite :", "options": ["Des amortisseurs de fin de course intégrés au vérin", "Des capteurs magnétiques", "Une augmentation de la pression"], "rep": "Des amortisseurs de fin de course intégrés au vérin"},
        {"id": "qap2_7", "q": "Quel est le composant du groupe FRL chargé d'arrêter les gouttes d'eau condensée du réseau ?", "options": ["Le filtre (muni d'une purge)", "Le lubrificateur à aiguille", "Le manomètre"], "rep": "Le filtre (muni d'une purge)"},
        {"id": "qap2_8", "q": "Quel élément électrique reçoit l'ordre de l'automate pour déplacer mécaniquement le tiroir du distributeur ?", "options": ["Le solénoïde (bobine électrique)", "Le barreau aimanté", "Le silencieux de vidange"], "rep": "Le solénoïde (bobine électrique)"},
        {"id": "qap2_9", "q": "Pourquoi la vitesse de rentrée de la tige est-elle naturellement plus rapide que sa vitesse de sortie à débit égal ?", "options": ["Car le volume de la chambre avant est plus petit à cause de la tige", "Car l'air est plus chaud", "Car le ressort pousse à l'arrière"], "rep": "Car le volume de la chambre avant é plus petit à cause de la tige"},
        {"id": "qap2_10", "q": "Le traitement global de l'air comprimé au niveau du groupe FRL appartient à quelle fonction ?", "options": ["Alimenter / Distribuer", "Convertir", "Transmettre"], "rep": "Alimenter / Distribuer"}
    ]

    if "ordre_quiz_tab7_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu7_sources)
        st.session_state.ordre_quiz_tab7_dos_aleatoire = questions_pneu7_sources

    champs_mis_a_jour_b7 = [
        ("1. L'éjection dynamique du colis à haute cadence exploite un vérin ..........", ["Choisir...", "double effet", "simple effet"], "double effet", "pneu7_t1"),
        ("2. Assurer un retour automatique immédiat dès la fin du signal utilise un distributeur ..........", ["Choisir...", "monostable", "bistable"], "monostable", "pneu2_t2"),
        ("3. Le distributeur de référence pour cette tâche est un modèle ..........", ["Choisir...", "5/2", "3/2"], "5/2", "pneu7_t3"),
        ("4. Repérer le passage du paquet sur le tapis roulant requiert un capteur ..........", ["Choisir...", "optique", "magnétique"], "optique", "pneu7_t4"),
        ("5. Le signal électrique de commande de l'automate excite la bobine du ..........", ["Choisir...", "solénoïde", "silencieux"], "solénoïde", "pneu7_t5"),
        ("6. Prévenir la rupture des structures lors des chocs utilise des .......... de fin de course.", ["Choisir...", "amortisseurs", "régleurs"], "amortisseurs", "pneu7_t6"),
        ("7. Augmenter la cadence de poussée exige d'ouvrir les régleurs de .......... d'air.", ["Choisir...", "débit", "pression"], "débit", "pneu7_t7"),
        ("8. Éliminer l'humidité présente dans les conduites est assuré par le .......... du FRL.", ["Choisir...", "filtre", "lubrificateur"], "filtre", "pneu7_t8"),
        ("9. Une coupure d'énergie sur ce circuit monostable provoque une rentrée de ..........", ["Choisir...", "sécurité", "blocage"], "sécurité", "pneu7_t9"),
        ("10. Cette étude constitue une application d'analyse quantitative de ..........", ["Choisir...", "système", "matière"], "système", "pneu7_t10")
    ]
    st.session_state.champs_pneu7_clean = champs_mis_a_jour_b7

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at7_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu7_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu7_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_application1(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Application 1 : Serrage) sur deux colonnes."""
    import random

    questions_pneu6_sources = [
        {"id": "qap1_1", "q": "Quel type de vérin est mis en œuvre pour appliquer l'effort de bridage constant sur la pièce à usiner ?", "options": ["Un vérin double effet", "Un vérin simple effet à ressort", "Un vérin rotatif"], "rep": "Un vérin double effet"},
        {"id": "qap1_2", "q": "Quel distributeur normalisé assure le pilotage des mouvements de ce vérin double effet ?", "options": ["Un distributeur 5/2", "Un distributeur 3/2", "Une simple vanne 2/2"], "rep": "Un distributeur 5/2"},
        {"id": "qap1_3", "q": "Quelle grandeur physique doit être ajustée au manomètre pour modifier la force de serrage exercée par la tige ?", "options": ["La pression d'alimentation", "Le débit d'échappement", "Le volume de la chambre"], "rep": "La pression d'alimentation"},
        {"id": "qap1_4", "q": "Quel composant du groupe FRL évite d'endommager les joints du vérin par abrasion ou grippage ?", "options": ["Le lubrificateur (brouillard d'huile)", "Le filtre à impuretés", "Le régulateur à vis"], "rep": "Le lubrificateur (brouillard d'huile)"},
        {"id": "qap1_5", "q": "Comment qualifie-t-on le capteur de fin de course chargé de vérifier que la tige est totalement sortie ?", "options": ["Un capteur de position (ou détecteur de proximité)", "Un manomètre à aiguille", "Un régulateur de débit"], "rep": "Un capteur de position (ou détecteur de proximité)"},
        {"id": "qap1_6", "q": "Si une coupure de pression survient sur un distributeur bistable, que fait le bras de serrage ?", "options": ["Il conserve sa position et maintient le serrage", "Il s'ouvre instantanément", "Il se met à osciller"], "rep": "Il conserve sa position et maintient le serrage"},
        {"id": "qap1_7", "q": "Quel organe mécanique installé sur l'échappement permet de ralentir la vitesse de fermeture du bras ?", "options": ["Un régleur de débit unidirectionnel", "Un limiteur de pression", "Un silencieux poreux"], "rep": "Un régleur de débit unidirectionnel"},
        {"id": "qap1_8", "q": "Pour calculer l'effort théorique de poussée du piston, quelle formule mathématique applique-t-on ?", "options": ["Force = Pression x Surface utile", "Force = Pression / Surface", "Force = Débit x Vitesse"], "rep": "Force = Pression x Surface utile"},
        {"id": "qap1_9", "q": "Pourquoi la face avant du piston développe-t-elle moins d'effort que la face arrière ?", "options": ["Car la tige diminue la surface utile soumise à la pression", "Car l'air refroidit à l'avant", "Car le tuyau avant est plus long"], "rep": "Car la tige diminue la surface utile soumise à la pression"},
        {"id": "qap1_10", "q": "Quel composant d'extrémité poreux attenant au distributeur permet de réduire le bruit de l'air s'échappant ?", "options": ["Un silencieux d'échappement", "Un raccord cannelé", "Un clapet de non-retour"], "rep": "Un silencieux d'échappement"}
    ]

    if "ordre_quiz_tab6_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu6_sources)
        st.session_state.ordre_quiz_tab6_pneu_aleatoire = questions_pneu6_sources

    champs_mis_a_jour_b6 = [
        ("1. Le bridage mécanique de la pièce en bois exploite un actionneur ..........", ["Choisir...", "double effet", "simple effet"], "double effet", "pneu6_t1"),
        ("2. L'aiguillage de l'air comprimé vers ce vérin requiert un distributeur ..........", ["Choisir...", "5/2", "3/2"], "5/2", "pneu6_t2"),
        ("3. Modifier l'intensité de la force de serrage exige d'ajuster la ..........", ["Choisir...", "pression", "vitesse"], "pression", "pneu6_t3"),
        ("4. Lubrifier les parois coulissantes est le rôle du .......... du groupe FRL.", ["Choisir...", "lubrificateur", "filtre"], "lubrificateur", "pneu6_t4"),
        ("5. Confirmer la fermeture totale du bras s'appuie sur un .......... de fin de course.", ["Choisir...", "capteur", "manomètre"], "capteur", "pneu6_t5"),
        ("6. Une coupure d'air sur une commande bistable permet de .......... le blocage.", ["Choisir...", "conserver", "annuler"], "conserver", "pneu6_t6"),
        ("7. Ralentir le mouvement de la bride utilise un régleur de .......... d'échappement.", ["Choisir...", "débit", "calibre"], "débit", "pneu6_t7"),
        ("8. L'effort mécanique de poussée est proportionnel à la surface .......... du piston.", ["Choisir...", "utile", "totale"], "utile", "pneu6_t8"),
        ("9. L'échappement de l'air vicié s'effectue à travers un .......... antibruit.", ["Choisir...", "silencieux", "raccord"], "silencieux", "pneu6_t9"),
        ("10. Ce montage réalise une application industrielle d'analyse ..........", ["Choisir...", "quantitative", "qualitative"], "quantitative", "pneu6_t10")
    ]
    st.session_state.champs_pneu6_clean = champs_mis_a_jour_b6

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu6_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu6_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_autres_actionneurs(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Autres actionneurs) sur deux colonnes."""
    import random

    questions_pneu5_sources = [
        {"id": "qaa1", "q": "Quel type de mouvement mécanique génère spécifiquement un vérin rotatif ?", "options": ["Un mouvement de rotation angulaire limité", "Un mouvement de translation rectiligne infini", "Une oscillation sinusoïdale"], "rep": "Un mouvement de rotation angulaire limité"},
        {"id": "qaa2", "q": "Quel système mécanique interne convertit la translation du piston en rotation sur un vérin rotatif standard ?", "options": ["Un système pignon-crémaillère", "Une bielle-manivelle", "Une vis sans fin"], "rep": "Un système pignon-crémaillère"},
        {"id": "qaa3", "q": "Quelle est la plage de rotation angulaire classique d'un vérin rotatif industriel ?", "options": ["90 degrés, 180 degrés ou 270 degrés", "3600 degrés en continu", "Uniquement 45 degrés"], "rep": "90 degrés, 180 degrés ou 270 degrés"},
        {"id": "qaa4", "q": "Quel actionneur pneumatique utilise des doigts mobiles pour saisir et relâcher des pièces sur un robot ?", "options": ["Une pince pneumatique (ou préhenseur)", "Une ventouse venturi", "Un moteur à palettes"], "rep": "Une pince pneumatique (ou préhenseur)"},
        {"id": "qaa5", "q": "Quel composant d'infrastructure est indispensable pour créer une dépression et faire fonctionner une ventouse ?", "options": ["Un éjecteur (ou buse Venturi)", "Un compresseur à piston décalé", "Un détendeur de sécurité"], "rep": "Un éjecteur (ou buse Venturi)"},
        {"id": "qaa6", "q": "Quel effet physique est exploité dans un éjecteur pour générer du vide à partir d'un flux d'air comprimé ?", "options": ["L'effet Venturi (dépression par accélération de l'air)", "L'effet Joule", "La loi de Beer-Lambert"], "rep": "L'effet Venturi (dépression par accélération de l'air)"},
        {"id": "qaa7", "q": "Quel est l'avantage majeur d'une ventouse par rapport à une pince mécanique ?", "options": ["Elle permet de saisir des objets plats, lisses ou fragiles sans les rayer", "Elle développe une force de serrage infinie", "Elle fonctionne sans aucun tuyau d'air"], "rep": "Elle permet de saisir des objets plats, lisses ou fragiles sans les rayer"},
        {"id": "qaa8", "q": "Comment qualifie-t-on un actionneur capable de tourner à haute vitesse de manière continue (comme une visseuse) ?", "options": ["Un moteur pneumatique (généralement à palettes)", "Un vérin double effet télescopique", "Un préhenseur angulaire"], "rep": "Un moteur pneumatique (généralement à palettes)"},
        {"id": "qaa9", "q": "Quelle unité de mesure exprime la valeur de la dépression (pression inférieure à la pression atmosphérique) pour le vide ?", "options": ["Le pascal (ou le bar négatif / millibar)", "Le watt", "Le siemens par mètre"], "rep": "Le pascal (ou le bar négatif / millibar)"},
        {"id": "qaa10", "q": "Lorsqu'une ventouse lâche une pièce, quelle opération permet d'accélérer la dépose en annulant instantanément le vide ?", "options": ["Le soufflage (injection d'une impulsion d'air)", "L'échappement libre", "La lubrification des joints"], "rep": "Le soufflage (injection d'une impulsion d'air)"}
    ]

    if "ordre_quiz_tab5_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu5_sources)
        st.session_state.ordre_quiz_tab5_pneu_aleatoire = questions_pneu5_sources

    champs_mis_a_jour_b5 = [
        ("1. Le vérin rotatif convertit l'énergie de l'air en un mouvement de ..........", ["Choisir...", "rotation", "translation"], "rotation", "pneu5_t1"),
        ("2. La transformation interne du mouvement s'appuie sur un système pignon-..........", ["Choisir...", "crémaillère", "bielle"], "crémaillère", "pneu5_t2"),
        ("3. Saisir des objets au moyen de doigts mobiles caractérise la .......... pneumatique.", ["Choisir...", "pince", "ventouse"], "pince", "pneu5_t3"),
        ("4. Manipuler des plaques de verre sans contact mécanique utilise une ..........", ["Choisir...", "ventouse", "crémaillère"], "ventouse", "pneu5_t4"),
        ("5. Créer une dépression d'air locale requiert l'usage d'un éjecteur ..........", ["Choisir...", "Venturi", "Kohlrausch"], "Venturi", "pneu5_t5"),
        ("6. La pression d'une zone de vide est strictement .......... à la pression atmosphérique.", ["Choisir...", "inférieure", "supérieure"], "inférieure", "pneu5_t6"),
        ("7. Pour forcer la dépose rapide d'une pièce par la ventouse, on applique un ..........", ["Choisir...", "soufflage", "échappement"], "soufflage", "pneu5_t7"),
        ("8. Un outil tournant à grande vitesse en continu est entraîné par un ..........", ["Choisir...", "moteur", "vérin"], "moteur", "pneu5_t8"),
        ("9. Le préhenseur pneumatique est un actionneur de l'étape de .......... d'énergie.", ["Choisir...", "conversion", "distribution"], "conversion", "pneu5_t9"),
        ("10. Les ventouses sont particulièrement idéales pour soulever des surfaces ..........", ["Choisir...", "planes", "rugueuses"], "planes", "pneu5_t10")
    ]
    st.session_state.champs_pneu5_clean = champs_mis_a_jour_b5

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu5_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu5_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_verin_double_effet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Vérin double effet) sur deux colonnes."""
    import random

    questions_pneu4_sources = [
        {"id": "qde1", "q": "Quelle est la caractéristique principale d'un vérin double effet ?", "options": ["Il développe un effort et un mouvement dans les deux sens de marche", "Il tourne en continu sur lui-même", "Il fonctionne sans aucun apport d'air comprimé"], "rep": "Il développe un effort et un mouvement dans les deux sens de marche"},
        {"id": "qde2", "q": "Combien de chambres d'alimentation étanches indépendantes possède un vérin double effet ?", "options": ["Deux chambres indépendantes", "Une seule chambre arrière", "Quatre compartiments cloisonnés"], "rep": "Deux chambres indépendantes"},
        {"id": "qde3", "q": "Pour faire rentrer la tige d'un double effet, où doit-on injecter l'air sous pression ?", "options": ["Dans l'orifice avant B", "Dans l'orifice arrière A", "Dans les deux orifices simultanément"], "rep": "Dans l'orifice avant B"},
        {"id": "qde4", "q": "Pourquoi l'effort développé lors de la rentrée de la tige est-il inférieur à celui de la sortie ?", "options": ["À cause de la présence de la tige qui réduit la surface utile du piston", "Parce que le ressort interne freine le mouvement de retour", "Parce que l'air injecté à l'avant est moins comprimé"], "rep": "À cause de la présence de la tige qui réduit la surface utile du piston"},
        {"id": "qde5", "q": "Quel distributeur normalisé est le standard requis pour piloter idéalement un vérin double effet ?", "options": ["Un distributeur 5/2 (ou 4/2)", "Un distributeur 3/2", "Un clapet anti-retour simple"], "rep": "Un distributeur 5/2 (ou 4/2)"},
        {"id": "qde6", "q": "Que se passe-t-il si l'on alimente simultanément les orifices A et B à la même pression ?", "options": ["Le vérin sort lentement car la surface arrière est supérieure à la surface avant", "Le vérin reste parfaitement immobile au milieu de sa course", "Le vérin se met à osciller de façon sinusoïdale"], "rep": "Le vérin sort lentement car la surface arrière est supérieure à la surface avant"},
        {"id": "qde7", "q": "Comment contrôle-t-on la vitesse de déplacement de la tige d'un double effet ?", "options": ["En installant des régleurs de débit sur les échappements d'air", "En changeant le diamètre du tube d'alimentation global", "En modifiant la dureté de la tige métallique"], "rep": "En installant des régleurs de débit sur les échappements d'air"},
        {"id": "qde8", "q": "Quel composant mécanique assure l'étanchéité absolue entre les deux chambres intérieures ?", "options": ["Les joints de piston étanches", "Le presse-étoupe du nez de guidage", "La bague de friction en bronze"], "rep": "Les joints de piston étanches"},
        {"id": "qde9", "q": "Dans quelle application industrielle le vérin double effet est-il privilégié ?", "options": ["Pour les transferts, le levage de charges et la manutention contrôlée", "Pour les petits boutons poussoirs d'arrêt d'urgence", "Pour les éjections rapides de pièces par gravité"], "rep": "Pour les transferts, le levage de charges et la manutention contrôlée"},
        {"id": "qde10", "q": "Que devient la position de la tige en cas de coupure de pression si le distributeur est de type bistable ?", "options": ["Le vérin conserve sa dernière position acquise", "Le vérin rentre instantanément à sa course minimale", "Le vérin sort brusquement à sa course maximale"], "rep": "Le vérin conserve sa dernière position acquise"}
    ]

    if "ordre_quiz_tab4_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu4_sources)
        st.session_state.ordre_quiz_tab4_pneu_aleatoire = questions_pneu4_sources

    champs_mis_a_jour_b4 = [
        ("1. Le vérin double effet développe une action motrice dans les .......... sens.", ["Choisir...", "deux", "quatre"], "deux", "pneu4_t1"),
        ("2. Son enveloppe interne comporte deux .......... d'alimentation indépendantes.", ["Choisir...", "chambres", "tiges"], "chambres", "pneu4_t2"),
        ("3. Alimenter l'orifice avant B provoque spécifiquement la .......... de la tige.", ["Choisir...", "rentrée", "sortie"], "rentrée", "pneu4_t3"),
        ("4. La présence de la tige diminue la surface .......... du piston lors du retour.", ["Choisir...", "utile", "totale"], "utile", "pneu4_t4"),
        ("5. Le pilotage d'un actionneur double effet requiert un distributeur ..........", ["Choisir...", "5/2", "3/2"], "5/2", "pneu4_t5"),
        ("6. Régler finement la vitesse de course nécessite des régleurs de ..........", ["Choisir...", "débit", "pression"], "débit", "pneu4_t6"),
        ("7. L'étanchéité absolue entre les compartiments est assurée par un ..........", ["Choisir...", "joint", "barreau"], "joint", "pneu4_t7"),
        ("8. Une commande bistable permet de .......... la position lors d'une coupure.", ["Choisir...", "conserver", "annuler"], "conserver", "pneu4_t8"),
        ("9. Ce composant est l'outil idéal pour le .......... de charges lourdes.", ["Choisir...", "levage", "bridage"], "levage", "pneu4_t9"),
        ("10. Contrairement au simple effet, son corps ne contient aucun ..........", ["Choisir...", "ressort", "piston"], "ressort", "pneu4_t10")
    ]
    st.session_state.champs_pneu4_clean = champs_mis_a_jour_b4

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu4_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu4_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_verin_simple_effet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Vérin simple effet) sur deux colonnes."""
    import random

    questions_pneu3_sources = [
        {"id": "qse1", "q": "Dans combien de sens un vérin simple effet peut-il développer un effort mécanique ?", "options": ["Un seul sens", "Deux sens indépendants", "Uniquement en rotation"], "rep": "Un seul sens"},
        {"id": "qse2", "q": "Quel composant mécanique interne assure le retour de la tige en position initiale ?", "options": ["Un ressort de rappel", "Une seconde entrée de fluide", "Un contrepoids suspendu"], "rep": "Un ressort de rappel"},
        {"id": "qse3", "q": "Combien d'orifices d'alimentation en fluide possède un vérin simple effet ?", "options": ["Un seul orifice", "Deux orifices opposés", "Aucun orifice"], "rep": "Un seul orifice"},
        {"id": "qse4", "q": "Dans quelle situation industrielle privilégie-t-on l'usage d'un simple effet ?", "options": ["Pour des opérations de serrage, bridage ou éjection", "Pour piloter la direction d'un engin", "Pour des levages de charges lourdes bidirectionnels"], "rep": "Pour des opérations de serrage, bridage ou éjection"},
        {"id": "qse5", "q": "Quel est l'avantage majeur du vérin simple effet en cas de coupure de pression accidentelle ?", "options": ["Il revient automatiquement en position de sécurité grâce au ressort", "Il reste bloqué au milieu", "Il explose sous l'effet du vide"], "rep": "Il revient automatiquement en position de sécurité grâce au ressort"},
        {"id": "qse6", "q": "Quel distributeur normalisé utilise-t-on classiquement pour piloter un vérin simple effet ?", "options": ["Un distributeur 3/2", "Un distributeur 5/2", "Un limiteur de pression unidirectionnel"], "rep": "Un distributeur 3/2"},
        {"id": "qse7", "q": "Pourquoi la course d'un vérin simple effet est-elle généralement limitée en longueur ?", "options": ["À cause de l'encombrement mécanique du ressort comprimé", "Parce que l'air s'épuise trop vite", "Pour des raisons de température du métal"], "rep": "À cause de l'encombrement mécanique du ressort comprimé"},
        {"id": "qse8", "q": "Que fait la pression dans la chambre arrière lors de la rentrée de la tige ?", "options": ["Elle chute car la chambre est mise à l'échappement", "Elle augmente exponentiellement", "Elle reste bloquée à 6 bars"], "rep": "Elle chute car la chambre est mise à l'échappement"},
        {"id": "qse9", "q": "Comment appelle-t-on la pièce cylindrique qui sépare les deux zones à l'intérieur du corps ?", "options": ["Le piston", "La tige de poussée", "Le nez de guidage"], "rep": "Le piston"},
        {"id": "qse10", "q": "La consommation d'air d'un simple effet par rapport à un double effet de même taille est :", "options": ["Deux fois moins importante (une seule chambre à remplir)", "Strictement identique", "Trois fois supérieure"], "rep": "Deux fois moins importante (une seule chambre à remplir)"}
    ]

    if "ordre_quiz_tab3_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu3_sources)
        st.session_state.ordre_quiz_tab3_pneu_aleatoire = questions_pneu3_sources

    champs_mis_a_jour_b3 = [
        ("1. Le vérin simple effet ne produit d'effort mécanique que dans .......... sens.", ["Choisir...", "un seul", "deux"], "un seul", "pneu3_t1"),
        ("2. La rentrée de la tige est provoquée automatiquement par un ..........", ["Choisir...", "ressort", "fluide"], "ressort", "pneu3_t2"),
        ("3. Pour l'alimenter, l'enveloppe ne comporte qu'un seul .......... de raccordement.", ["Choisir...", "orifice", "capteur"], "orifice", "pneu3_t3"),
        ("4. Son usage classique en atelier concerne le .......... de pièces à usiner.", ["Choisir...", "serrage", "convoyage"], "serrage", "pneu3_t4"),
        ("5. Le pilotage standard de cet actionneur requiert un distributeur de type ..........", ["Choisir...", "3/2", "5/2"], "3/2", "pneu3_t5"),
        ("6. En cas de panne d'air, le piston reprend sa position de ..........", ["Choisir...", "sécurité", "travail"], "sécurité", "pneu3_t6"),
        ("7. La course totale est restreinte par l'encombrement du ressort ..........", ["Choisir...", "comprimé", "tendu"], "comprimé", "pneu3_t7"),
        ("8. Pour sortir la tige, l'air sous pression pousse directement sur le ..........", ["Choisir...", "piston", "nez"], "piston", "pneu3_t8"),
        ("9. Rentrer la tige impose de mettre la chambre active à l'.......... d'air.", ["Choisir...", "échappement", "alimentation"], "échappement", "pneu3_t9"),
        ("10. Ce composant convertit l'énergie pneumatique en énergie .......... translatrice.", ["Choisir...", "mécanique", "thermique"], "mécanique", "pneu3_t10")
    ]
    st.session_state.champs_pneu3_clean = champs_mis_a_jour_b3

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu3_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu3_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_distributeurs(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Les distributeurs) sur deux colonnes."""
    import random

    questions_pneu2_sources = [
        {"id": "qdi1", "q": "Quelle est la fonction principale d'un distributeur pneumatique dans une chaîne d'énergie ?", "options": ["Distribuer (aiguiller l'air comprimé)", "Convertir l'énergie en force", "Alimenter le réseau en air"], "rep": "Distribuer (aiguiller l'air comprimé)"},
        {"id": "qdi2", "q": "Que signifient les deux chiffres dans la désignation d'un distributeur normalisé (ex: 3/2) ?", "options": ["Nombre d'orifices / Nombre de positions", "Pression en bars / Débit en L/min", "Diamètre du tube / Course de la tige"], "rep": "Nombre d'orifices / Nombre de positions"},
        {"id": "qdi3", "q": "Quel type de distributeur est le standard minimal requis pour piloter un vérin simple effet ?", "options": ["Un distributeur 3/2", "Un distributeur 5/2", "Un distributeur 2/2"], "rep": "Un distributeur 3/2"},
        {"id": "qdi4", "q": "Quel type de distributeur est le standard requis pour piloter un vérin double effet ?", "options": ["Un distributeur 5/2 (ou 4/2)", "Un distributeur 3/2", "Un clapet anti-retour"], "rep": "Un distributeur 5/2 (ou 4/2)"},
        {"id": "qdi5", "q": "Comment appelle-t-on la pièce mécanique mobile interne qui coulisse pour modifier les voies de passage ?", "options": ["Le tiroir", "Le piston", "Le barreau"], "rep": "Le tiroir"},
        {"id": "qdi6", "q": "Quelle est la différence fondamentale entre un distributeur monostable et un distributeur bistable ?", "options": ["Le monostable possède un ressort de rappel pour revenir à sa position initiale", "Le bistable consomme deux fois plus d'air", "Le monostable tourne en continu sur lui-même"], "rep": "Le monostable possède un ressort de rappel pour revenir à sa position initiale"},
        {"id": "qdi7", "q": "Sur un schéma normalisé, comment sont représentées les différentes positions du distributeur ?", "options": ["Par des cases carrées (juxtaposées)", "Par des cercles concentriques", "Par des triangles fléchés"], "rep": "Par des cases carrées (juxtaposées)"},
        {"id": "qdi8", "q": "Dans la désignation des orifices, à quoi correspond généralement l'orifice portant le numéro 1 (ou P) ?", "options": ["À l'alimentation en pression (source d'air)", "À l'échappement vers l'atmosphère", "Au raccordement direct de la tige"], "rep": "À l'alimentation en pression (source d'air)"},
        {"id": "qdi9", "q": "Comment qualifie-t-on un pilotage de distributeur réalisé par un signal pneumatique (air comprimé) ?", "options": ["Un pilotage pneumatique (ou indirect)", "Un pilotage électrique", "Un pilotage mécanique par galet"], "rep": "Un pilotage pneumatique (ou indirect)"},
        {"id": "qdi10", "q": "À quoi servent les symboles en forme de T (ou de flèches fermées) dans les cases d'un schéma ?", "options": ["À indiquer un orifice obturé ou fermé", "À signaler un échappement libre", "À mesurer la pression du manomètre"], "rep": "À indiquer un orifice obturé ou fermé"}
    ]

    if "ordre_quiz_tab2_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu2_sources)
        st.session_state.ordre_quiz_tab2_pneu_aleatoire = questions_pneu2_sources

    champs_mis_a_jour_b2 = [
        ("1. Le distributeur pneumatique remplit la fonction de .......... de l'énergie.", ["Choisir...", "distribution", "conversion"], "distribution", "pneu2_t1"),
        ("2. Dans la désignation d'un distributeur, le premier chiffre donne le nombre d'..........", ["Choisir...", "orifices", "positions"], "orifices", "pneu2_t2"),
        ("3. Le second chiffre d'un symbole normalisé représente le nombre de ..........", ["Choisir...", "positions", "voies"], "positions", "pneu2_t3"),
        ("4. Piloter un vérin simple effet s'effectue couramment à l'aide d'un ..........", ["Choisir...", "3/2", "5/2"], "3/2", "pneu2_t4"),
        ("5. Commander un actionneur double effet requiert au minimum un ..........", ["Choisir...", "5/2", "3/2"], "5/2", "pneu2_t5"),
        ("6. La pièce cylindrique interne qui se déplace pour ouvrir les voies est le ..........", ["Choisir...", "tiroir", "piston"], "tiroir", "pneu2_t6"),
        ("7. Un appareil possédant un ressort de rappel mécanique est qualifié de ..........", ["Choisir...", "monostable", "bistable"], "monostable", "pneu2_t7"),
        ("8. Une commande conservant son état après la disparition du signal est ..........", ["Choisir...", "bistable", "monostable"], "bistable", "pneu2_t8"),
        ("9. Sur le diagramme, la case de droite représente la position de ..........", ["Choisir...", "repos", "travail"], "repos", "pneu2_t9"),
        ("10. L'orifice repéré par le chiffre 1 désigne la conduite de ..........", ["Choisir...", "pression", "échappement"], "pression", "pneu2_t10")
    ]
    st.session_state.champs_pneu2_clean = champs_mis_a_jour_b2

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu2_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu2_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_histoire_pneumatique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Histoire et production d'air) sur deux colonnes."""
    import random

    questions_pneu1_sources = [
        {"id": "qp1", "q": "De quel mot grec provient le terme 'pneumatique' utilisé pour désigner l'énergie de l'air ?", "options": ["Pneuma (souffle / esprit)", "Kinetikos", "Bios"], "rep": "Pneuma (souffle / esprit)"},
        {"id": "qp2", "q": "Quel appareil mécanique transforme la puissance de l'air comprimé en force mécanique rectiligne ?", "options": ["Le vérin", "Le compresseur", "Le distributeur"], "rep": "Le vérin"},
        {"id": "qp3", "q": "Quel appareil mécanique aspire l'air ambiant pour le stocker sous pression dans un réservoir ?", "options": ["Le compresseur", "L'unité FRL", "Le bouton poussoir"], "rep": "Le compresseur"},
        {"id": "qp4", "q": "Dans quelle ville européenne a-t-on installé un réseau urbain complet d'air comprimé en 1888 ?", "options": ["Paris", "Londres", "Berlin"], "rep": "Paris"},
        {"id": "qp5", "q": "Quelle fonction de la chaîne d'énergie est remplie par les distributeurs pneumatiques ?", "options": ["Distribuer", "Convertir", "Alimenter"], "rep": "Distribuer"},
        {"id": "qp6", "q": "Quelle fonction de la chaîne d'énergie est exécutée par les vérins pneumatiques ?", "options": ["Convertir", "Transmettre", "Distribuer"], "rep": "Convertir"},
        {"id": "qp7", "q": "Quelle valeur de pression d'utilisation (en bars) est le standard classique des réseaux d'usines ?", "options": ["6 bars", "1 bar", "150 bars"], "rep": "6 bars"},
        {"id": "qp8", "q": "Quel composant filtre l'humidité, règle la pression et diffuse un brouillard d'huile protecteur ?", "options": ["L'unité FRL", "Le compresseur à piston", "La burette à robinet"], "rep": "L'unité FRL"},
        {"id": "qp9", "q": "Pourquoi la technologie pneumatique est-elle privilégiée dans l'industrie agroalimentaire ?", "options": ["Pour sa propreté (aucun risque de fuite d'huile polluante)", "Parce qu'elle ne fait aucun bruit", "Parce qu'elle consomme moins d'électricité"], "rep": "Pour sa propreté (aucun risque de fuite d'huile polluante)"},
        {"id": "qp10", "q": "À l'échelle microscopique, comment se traduit l'augmentation de la pression de l'air dans un réservoir ?", "options": ["Par les collisions incessantes des molécules contre les parois", "Par le gel instantané des atomes", "Par un changement de couleur du gaz"], "rep": "Par les collisions incessantes des molécules contre les parois"}
    ]

    if "ordre_quiz_tab1_pneu_aleatoire" not in st.session_state:
        random.shuffle(questions_pneu1_sources)
        st.session_state.ordre_quiz_tab1_pneu_aleatoire = questions_pneu1_sources

    # Liste de synthèse de texte à trous structurée en tuples
    if "champs_pneu1_clean" not in st.session_state:
        st.session_state.champs_pneu1_clean = [
            ("1. Déplacer des mécanismes à l'aide d'air comprimé constitue la ..........", ["Choisir...", "pneumatique", "hydraulique"], "pneumatique", "pneu1_t1"),
            ("2. L'appareil chargé d'aspirer et de comprimer l'air ambiant est le ..........", ["Choisir...", "compresseur", "vérin"], "compresseur", "pneu1_t2"),
            ("3. Le mot pneumatique dérive d'une racine grecque signifiant le ..........", ["Choisir...", "souffle", "mouvement"], "souffle", "pneu1_t3"),
            ("4. La fonction 'Distribuer' de la chaîne d'énergie est assurée par le ..........", ["Choisir...", "distributeur", "compresseur"], "distributeur", "pneu1_t4"),
            ("5. Transformer la pression de l'air en effort mécanique revient à ..........", ["Choisir...", "convertir", "alimenter"], "convertir", "pneu1_t5"),
            ("6. L'actionneur rectiligne linéaire le plus classique est le ..........", ["Choisir...", "vérin", "moteur"], "vérin", "pneu1_t6"),
            ("7. Conditionner l'air de l'usine avant son entrée requiert l'unité ..........", ["Choisir...", "FRL", "EDTA"], "FRL", "pneu1_t7"),
            ("8. Le manomètre du régulateur ajuste la valeur de pression d'..........", ["Choisir...", "utilisation", "stockage"], "utilisation", "pneu1_t8"),
            ("9. Filtrer les impuretés élimine les particules de poussière et d'..........", ["Choisir...", "eau", "huile"], "eau", "pneu1_t9"),
            ("10. La bousculade microscopique des molécules d'air crée la ..........", ["Choisir...", "pression", "conductivité"], "pression", "pneu1_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique et Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_pneu_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pneu_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pneu1_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pneu1_clean", disabled=verrouille, label_visibility="collapsed")
with tab1:
    st.header("Historique et principes des systèmes pneumatiques")
    
    # --- SECTION COURS : LES FONDEMENTS DE LA PNEUMATIQUE ---
    st.subheader("Histoire des Sciences : De la force du vent aux usines automatisées")
    st.write(
        "L'utilisation de l'air comprimé par l'humanité remonte à l'Antiquité, avec l'invention des premiers soufflets "
        "de forge pour atteindre les températures nécessaires à la métallurgie. Le mot pneumatique provient d'ailleurs du "
        "grec ancien 'pneuma', qui signifie souffle ou esprit.\n\n"
        "La véritable révolution technologique a lieu au dix-neuvième siècle avec la révolution industrielle. "
        "Des ingénieurs comme Denis Papin et George Medhurst posent les bases du transport et de la transmission de puissance "
        "par air comprimé. En 1888, la ville de Paris installe un réseau urbain de distribution d'air comprimé pour alimenter "
        "les horloges publiques, les ascenseurs et les petites machines des ateliers artisanaux, préfigurant les réseaux industriels actuels.\n\n"
        "Au vingtième siècle, avec l'essor de l'automatisation et de la robotique, l'énergie pneumatique est devenue incontournable "
        "dans les usines. Sa rapidité d'exécution, sa propreté (aucun risque de fuite d'huile polluante) et sa sécurité totale "
        "dans les milieux explosifs ou humides en font la technologie reine pour le déplacement à haute cadence de petites pièces."
    )
    
    st.divider()
    
    st.subheader("La chaîne d'énergie pneumatique")
    st.write(
        "Dans un système automatisé, la transmission de puissance par air comprimé follow une structure normalisée appelée "
        "chaîne d'énergie. Elle est composée de quatre grandes fonctions de base :\n\n"
        "* **Alimenter :** Le compresseur aspire l'air ambiant et le comprime dans un réservoir de stockage.\n"
        "* **Distribuer :** Les distributeurs, pilotés électriquement ou manuellement, agissent comme des aiguillages pour orienter l'air vers les tuyaux utiles.\n"
        "* **Convertir :** Les vérins (actionneurs) transforment l'énergie de l'air comprimé en force mécanique rectiligne ou rotative.\n"
        "* **Transmettre :** La tige du vérin transmet l'effort au mécanisme récepteur (bras de robot, pince, presse de serrage)."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_pneu1, col_pneu2 = st.columns(2)
    with col_pneu1:
        st.write("**Le principe de la pression expliqué par la caricature**")
        st.write(
            "Pour comprendre comment l'air comprimé génère une force, on peut imaginer la caricature d'une multitude de petits personnages "
            "microscopiques très agités et confinés à l'intérieur d'un ballon métallique fermé. "
            "Tant qu'ils ont de l'espace, ils se déplacent tranquillement. Mais si le compresseur en force des milliers d'autres à entrer "
            "dans le même espace, les personnages se retrouvent à l'étroit et s'énervent. "
            "Ils se mettent à frapper avec ferveur et de toutes leurs forces contre les parois du réservoir. Cette bousculade collective "
            "et invisible représente la pression pneumatique. Si on ouvre une vanne, cette poussée s'échappe pour repousser le piston du vérin."
        )
        try:
            st.image("caricature_histoire_pneumatique.jpg", caption="Caricature de la pression : Le comportement microscopique de l'air comprimé")
        except Exception:
            st.warning("L'image 'caricature_histoire_pneumatique.jpg' est introuvable.")

    with col_pneu2:
        st.write("**La structure globale d'une installation**")
        st.write(
            "Une installation industrielle de référence comprend toujours une unité de traitement de l'air située "
            "juste avant les machines, appelée groupe FRL (Filtre, Régulateur, Lubrificateur).\n\n"
            "Ce composant remplit trois rôles indispensables pour protéger les joints des vérins : il filtre les poussières "
            "et l'humidité condensée, régule la pression à une valeur constante (généralement 6 bars) à l'aide d'un manomètre, "
            "et diffuse un léger brouillard d'huile pour lubrifier les pièces mécaniques en mouvement continu."
        )
        try:
            st.image("montage_general_pneumatique.jpg", caption="Schéma normalisé des composants de production et de traitement de l'air")
        except Exception:
            st.warning("L'image 'montage_general_pneumatique.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE D'EXERCICES ET SCELLÉ DE L'ATELIER 1 ---
    if "suite_verrouille_tab1_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab1_pneumatique = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_pneumatique

    # Affichage du module de questions spécifique à l'histoire et à la chaîne d'énergie
    afficher_atelier_histoire_pneumatique(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique et principes de la pneumatique.",
        key="check_certif_pneu1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_pneu_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q1 += 1.0

            score_t1 = 0.0
            if "champs_pneu1_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu1_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_pneu1_clean", "Choisir...") == attendu: score_t1 += 1.0

            st.session_state.score_suite1_pneu_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_pneu_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_pneu = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab1_pneumatique", False):
        scr1_t1 = st.session_state.get("score_suite1_pneu_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_pneu_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_pneu", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HISTORIQUE ET PRINCIPES SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_pneu1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Pneumatique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 1 : Historique et principes de la chaîne d'énergie pneumatique</p>
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

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab1_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_pneu1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 1
        if "champs_pneu1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 1
        html_export_pneu1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu1 = preparer_nom_fichier("Rapport_Histoire_Pneumatique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_pneu1,
            file_name=nom_fichier_html_pneu1,
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Les distributeurs pneumatiques")
    
    # --- SECTION COURS : LES PRINCIPES DE LA DISTRIBUTION ---
    st.subheader("Principe fondamental et rôle du distributeur")
    st.write(
        "Le distributeur pneumatique est l'organe de commande pré-actionneur de la chaîne d'énergie. "
        "Son rôle consiste à aiguiller l'air comprimé sous pression vers les différentes chambres des vérins "
        "ou à relier ces chambres à l'échappement pour évacuer l'air vers l'atmosphère, provoquant ainsi le mouvement.\n\n"
        "À l'intérieur du corps du distributeur, une pièce mobile appelée **tiroir** coulisse de manière rectiligne. "
        "Selon sa position, ce tiroir ouvre ou obture les canaux internes, modifiant instantanément le cheminement du fluide. "
        "La commande du tiroir peut être manuelle (bouton, levier), mécanique (galet), pneumatique (impulsion d'air) ou "
        "électrique (via un électro-aimant appelé solénoïde)."
    )
    
    st.divider()
    
    # --- NORMALISATION ET SYMBOLES ---
    st.subheader("Lecture et codification des symboles normalisés")
    st.write(
        "La désignation d'un distributeur s'énonce sous la forme de deux chiffres (ex: 3/2 ou 5/2) :\n"
        "* **Le premier chiffre** indique le nombre d'**orifices** (voies de raccordement pour les tuyaux).\n"
        "* **Le second chiffre** indique le nombre de **positions** de fonctionnement possibles.\n\n"
        "Sur un schéma normalisé ISO, chaque position est représentée par une **case carrée**. "
        "Le distributeur complet est modélisé par la juxtaposition de ces cases. Les flèches internes indiquent le sens "
        "de circulation de l'air, tandis que les symboles en forme de T figurent des voies fermées (orifices obturés).\n\n"
        "Par convention, les tuyaux d'alimentation et d'utilisation sont toujours raccordés graphiquement sur la case représentant "
        "la position de **repos** (généralement la case de droite pour un appareil à deux positions)."
    )
    
    st.subheader("Les deux grandes familles de comportement")
    st.write(
        "On distingue deux configurations technologiques majeures selon le mode de rappel du tiroir :\n"
        "* **Les distributeurs monostables :** Ils ne possèdent qu'une seule position stable. Un ressort mécanique ramène "
        "systématiquement le tiroir à sa position de repos dès que le signal de commande s'arrête. Ils agissent comme des interrupteurs poussoirs.\n"
        "* **Les distributeurs bistables :** Ils possèdent deux positions stables. Le tiroir reste dans sa configuration actuelle "
        "même après la disparition du signal. Il faut envoyer une impulsion sur la commande opposée pour inverser le cycle. Ils font office de mémoire."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_dist1, col_dist2 = st.columns(2)
    with col_dist1:
        st.write("**Le principe de l'aiguillage expliqué par la caricature**")
        st.write(
            "Pour faire comprendre ce mécanisme aux élèves, on peut dessiner la caricature d'un aiguilleur de chemin de fer "
            "qui actionne un grand levier au milieu des rails. L'air comprimé représente un train de wagons lancés à toute vitesse. "
            "Si le levier est relâché (position monostable au repos), les rails orientent le train vers une voie de garage sans issue (échappement). "
            "Dès que l'électro-aimant s'active, l'aiguilleur pousse le levier avec force : les rails pivotent et le train s'engouffre "
            "directement vers la chambre arrière du vérin, provoquant sa sortie immédiate."
        )
        try:
            st.image("caricature_les_distributeurs.jpg", caption="Caricature de la distribution : La commutation mécanique des voies de passage")
        except Exception:
            st.warning("L'image 'caricature_les_distributeurs.jpg' est introuvable.")

    with col_dist2:
        st.write("**Exemples de schémas normalisés industriels**")
        st.write(
            "Voici les deux symboles fondamentaux étudiés en classe :\n"
            "1. **Le distributeur 3/2 monostable :** Comportant 3 orifices et 2 positions, équipé d'un rappel par ressort. "
            "C'est le standard exclusif pour piloter un vérin simple effet.\n"
            "2. **Le distributeur 5/2 bistable :** Comportant 5 orifices et 2 positions, piloté par deux impulsions opposées. "
            "C'est l'appareil de référence pour commander les mouvements de sortie et de rentrée d'un vérin double effet."
        )
        try:
            st.image("symboles_normalises_distributeurs.jpg", caption="Symboles ISO normalisés des distributeurs 3/2 et 5/2")
        except Exception:
            st.warning("L'image 'symboles_normalises_distributeurs.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES AND VERROUILLAGE DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab2_pneumatique = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_pneumatique

    # Affichage du module de questions spécifique aux distributeurs
    afficher_atelier_distributeurs(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les distributeurs pneumatiques.",
        key="check_certif_pneu2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_pneu_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q2 += 1.0

            score_t2 = 0.0
            if "champs_pneu2_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu2_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_pneu2_clean", "Choisir...") == attendu: score_t2 += 1.0

            st.session_state.score_suite2_pneu_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_pneu_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_pneu = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2_pneumatique", False):
        scr1_t2 = st.session_state.get("score_suite2_pneu_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_pneu_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_pneu", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DISTRIBUTEURS SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_pneu2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Distributeurs Pneumatiques - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 2 : Organes d'aiguillage, tiroirs, monostables et symbolisation normalisée ISO</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
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

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab2_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_pneu2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 2
        if "champs_pneu2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 2
        html_export_pneu2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu2 = preparer_nom_fichier("Rapport_Distributeurs_Pneumatiques").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_pneu2,
            file_name=nom_fichier_html_pneu2,
            mime="text/html",
            use_container_width=True
        )

with tab3:
    st.header("Le vérin simple effet")
    
    # --- SECTION COURS : LES PRINCIPES DU VÉRIN SIMPLE EFFET ---
    st.subheader("Définition et principe de fonctionnement")
    st.write(
        "Un vérin simple effet (VSE) est un actionneur linéaire qui ne peut développer un effort mécanique "
        "que dans **un seul sens de marche** (généralement la sortie de la tige). Il ne possède qu'une seule chambre "
        "d'alimentation étanche pour recevoir le fluide sous pression.\n\n"
        "Le mouvement inverse (la rentrée de la tige) est assuré de manière autonome par un **ressort de rappel mécanique** "
        "intégré à la seconde chambre (chambre avant non alimentée), ou par une force extérieure comme la gravité ou une charge.\n\n"
        "Ce type de vérin est privilégié pour les opérations de serrage, de bridage de pièces ou d'éjection de produits légers, "
        "car il consomme deux fois moins d'air comprimé qu'un vérin double effet et offre une sécurité intrinsèque : "
        "en cas de coupure de pression, le ressort ramène immédiatement le mécanisme à sa position d'origine."
    )
    
    st.divider()
    
    # --- MODULE INTERACTIF : ANIMATION, VISU ET CHRONOMÈTRE ---
    col_vse_visu, col_vse_chrono = st.columns([0.55, 0.45])
    
    with col_vse_visu:
        st.subheader("Visualisation cinématique et structurelle")
        
        # Gestion de la position de la tige dans la session (de 0.0 à 1.0)
        if "pos_vse" not in st.session_state:
            st.session_state.pos_vse = 0.0
            
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        def dessiner_verin_simple_effet(position):
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor="white")
            ax.set_facecolor("white")
            
            # Corps externe étanche du vérin
            ax.add_patch(patches.Rectangle((1, 1), 3, 1.5, facecolor="#f1f5f9", edgecolor="#1e293b", linewidth=2.5, zorder=1))
            # Nez de guidage avant
            ax.plot([4, 4], [1, 2.5], color="#1e293b", linewidth=2.5, zorder=2)
            
            # Fluide sous pression dans la chambre arrière (remplissage bleu azur progressif)
            if position > 0:
                largeur_fluide = 0.2 + position * 2.5
                ax.add_patch(patches.Rectangle((1.02, 1.05), largeur_fluide, 1.4, facecolor="#0284c7", alpha=0.7, zorder=1))
            
            # Orifice d'alimentation d'air arrière (repère 1)
            ax.plot([1.5, 1.5], [0.6, 1], color="#1e293b", linewidth=2.5, zorder=2)
            ax.text(1.5, 0.3, "1", weight="bold", ha="center")
            
            # Piston intérieur mobile muni de ses segments d'étanchéité
            x_piston = 1.2 + position * 2.5
            ax.add_patch(patches.Rectangle((x_piston, 1.05), 0.3, 1.4, facecolor="#475569", edgecolor="#1e293b", linewidth=2, zorder=3))
            
            # Tige métallique de transmission de force
            ax.add_patch(patches.Rectangle((x_piston + 0.3, 1.5), 2.2, 0.4, facecolor="#94a3b8", edgecolor="#1e293b", linewidth=1.5, zorder=2))
            
            # Ressort de rappel mécanique modélisé par des spires compressibles
            nb_spires = 12
            x_debut_ressort = x_piston + 0.3
            x_fin_ressort = 4.0
            x_ressort = np.linspace(x_debut_ressort, x_fin_ressort, nb_spires)
            y_ressort = [1.75 + 0.25 * (-1)**i for i in range(nb_spires)]
            y_ressort[0], y_ressort[-1] = 1.75, 1.75
            ax.plot(x_ressort, y_ressort, color="#64748b", linewidth=2, linestyle="-", zorder=2)
            
            ax.set_xlim(0, 7)
            ax.set_ylim(0, 3)
            ax.axis("off")
            return fig

        plot_vse_placeholder = st.empty()
        plot_vse_placeholder.pyplot(dessiner_verin_simple_effet(st.session_state.pos_vse))

    with col_vse_chrono:
        st.subheader("Chronomètre de course en direct")
        st.write("Pilotez l'admission d'air comprimé pour mesurer la vitesse de déplacement réelle de la tige.")
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            activer_sortie_vse = st.button("ALIMENTER (SORTIE)", key="btn_out_vse", use_container_width=True)
        with c_btn2:
            activer_rentree_vse = st.button("ÉCHAPPEMENT (RESSORT)", key="btn_in_vse", use_container_width=True)
            
        chrono_placeholder = st.empty()
        chrono_placeholder.metric(label="Temps de course mesuré", value="0.00 s")
        
        import time
        
        if activer_sortie_vse:
            temps_debut = time.time()
            # Simulation progressive de la poussée pneumatique (course en 1.2s)
            for i in range(101):
                st.session_state.pos_vse = i / 100.0
                plot_vse_placeholder.pyplot(dessiner_verin_simple_effet(st.session_state.pos_vse))
                temps_ecoule = time.time() - temps_debut
                chrono_placeholder.metric(label="Chronomètre dynamique", value=f"{temps_ecoule:.2f} s")
                time.sleep(0.012)
            chrono_placeholder.metric(label="Temps de course final (Sortie)", value=f"{time.time() - temps_debut:.2f} s")
            
        elif activer_rentree_vse:
            temps_debut = time.time()
            # Le ressort mécanique repousse le tiroir (course retour plus rapide en 0.8s)
            for i in range(100, -1, -1):
                st.session_state.pos_vse = i / 100.0
                plot_vse_placeholder.pyplot(dessiner_verin_simple_effet(st.session_state.pos_vse))
                temps_ecoule = time.time() - temps_debut
                chrono_placeholder.metric(label="Chronomètre dynamique", value=f"{temps_ecoule:.2f} s")
                time.sleep(0.008)
            chrono_placeholder.metric(label="Temps de course final (Rentrée)", value=f"{time.time() - temps_debut:.2f} s")

    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 3 ---
    if "suite_verrouille_tab3_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab3_pneumatique = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_pneumatique

    # Affichage du module de questions spécifique au VSE
    afficher_atelier_verin_simple_effet(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Le vérin simple effet.",
        key="check_certif_pneu3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_pneu_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q3 += 1.0

            score_t3 = 0.0
            if "champs_pneu3_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu3_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_pneu3_clean", "Choisir...") == attendu: score_t3 += 1.0

            st.session_state.score_suite3_pneu_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_pneu_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_pneu = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 3 ---
    if st.session_state.get("suite_verrouille_tab3_pneumatique", False):
        scr1_t3 = st.session_state.get("score_suite3_pneu_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_pneu_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_pneu", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER VÉRIN SIMPLE EFFET SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_pneu3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vérin Simple Effet - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 3 : Constitution, fonctionnement et cinématique du vérin simple effet</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0369a1;">
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
        if "ordre_quiz_tab3_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_pneu3 += """
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
        if "champs_pneu3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 3
        html_export_pneu3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu3 = preparer_nom_fichier("Rapport_Verin_Simple_Effet").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_pneu3,
            file_name=nom_fichier_html_pneu3,
            mime="text/html",
            use_container_width=True
        )

with tab4:
    st.header("Le vérin double effet")
    
    # --- SECTION COURS : LES PRINCIPES DU VÉRIN DOUBLE EFFET ---
    st.subheader("Définition et principe de fonctionnement")
    st.write(
        "Le vérin double effet (VDE) est l'actionneur linéaire le plus répandu dans l'automatisation industrielle. "
        "Contrairement au vérin simple effet, il possède deux chambres d'alimentation étanches indépendantes et peut "
        "développer un effort mécanique et un mouvement contrôlé dans **les deux sens de marche** (en sortie et en rentrée de tige).\n\n"
        "Son fonctionnement repose sur l'inversion des pressions exercées sur les faces du piston :\n"
        "* **Pour faire sortir la tige :** L'air comprimé sous pression est injecté par l'orifice arrière A, tandis que la chambre avant "
        "est reliée à l'échappement pour évacuer l'air résiduel.\n"
        "* **Pour faire rentrer la tige :** Les pressions sont inversées par le distributeur. L'air sous pression pénètre par l'orifice "
        "avant B, poussant le piston vers l'arrière, tandis que la chambre arrière se vide à l'échappement.\n\n"
        "L'absence de ressort interne lui permet d'avoir une course utile beaucoup plus longue et d'exercer une force constante sur "
        "la totalité de son déplacement, le rendant indispensable pour le levage, le transfert de charges et les manipulations robotiques."
    )
    
    st.divider()
    
    # --- MODULE INTERACTIF : ANIMATION, VISU ET CHRONOMÈTRE ---
    col_vde_visu, col_vde_chrono = st.columns([0.55, 0.45])
    
    with col_vde_visu:
        st.subheader("Visualisation cinématique et structurelle")
        
        if "pos_vde" not in st.session_state:
            st.session_state.pos_vde = 0.0
            
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np
        
        def dessiner_verin_double_effet(position, sens_mouvement=None):
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor="white")
            ax.set_facecolor("white")
            
            # Corps externe étanche du vérin
            ax.add_patch(patches.Rectangle((1, 1), 3, 1.5, facecolor="#f1f5f9", edgecolor="#1e293b", linewidth=2.5, zorder=1))
            # Nez de guidage avant
            ax.plot(, [1, 2.5], color="#1e293b", linewidth=2.5, zorder=2)
            
            x_piston = 1.2 + position * 2.3
            
            # Remplissage de fluide dynamique selon le sens d'alimentation active
            if sens_mouvement == "sortie":
                ax.add_patch(patches.Rectangle((1.02, 1.05), x_piston - 1, 1.4, facecolor="#0284c7", alpha=0.7, zorder=1))
            elif sens_mouvement == "rentree":
                ax.add_patch(patches.Rectangle((x_piston + 0.3, 1.05), 4 - (x_piston + 0.3), 1.4, facecolor="#0284c7", alpha=0.7, zorder=1))
            
            # Orifice arrière A (repère 2) et orifice avant B (repère 4)
            ax.plot([1.5, 1.5], [0.6, 1], color="#1e293b", linewidth=2.5, zorder=2)
            ax.text(1.5, 0.3, "2", weight="bold", ha="center")
            
            ax.plot([3.5, 3.5], [0.6, 1], color="#1e293b", linewidth=2.5, zorder=2)
            ax.text(3.5, 0.3, "4", weight="bold", ha="center")
            
            # Piston intérieur étanche mobile
            ax.add_patch(patches.Rectangle((x_piston, 1.05), 0.3, 1.4, facecolor="#475569", edgecolor="#1e293b", linewidth=2, zorder=3))
            
            # Tige métallique de transmission de force traversante
            ax.add_patch(patches.Rectangle((x_piston + 0.3, 1.5), 2.5, 0.4, facecolor="#94a3b8", edgecolor="#1e293b", linewidth=1.5, zorder=2))
            
            ax.set_xlim(0, 7)
            ax.set_ylim(0, 3)
            ax.axis("off")
            return fig

        plot_vde_placeholder = st.empty()
        plot_vde_placeholder.pyplot(dessiner_verin_double_effet(st.session_state.pos_vde))

    with col_vde_chrono:
        st.subheader("Chronomètre de course en direct")
        st.write("Pilotez l'inversion des pressions d'air pour mesurer les temps de déplacement du double effet.")
        
        c_btn_de1, c_btn_de2 = st.columns(2)
        with c_btn_de1:
            activer_sortie_vde = st.button("ALIMENTER EN A (SORTIE)", key="btn_out_vde", use_container_width=True)
        with c_btn_de2:
            activer_rentree_vde = st.button("ALIMENTER EN B (RENTRÉE)", key="btn_in_vde", use_container_width=True)
            
        chrono_de_placeholder = st.empty()
        chrono_de_placeholder.metric(label="Temps de course mesuré", value="0.00 s")
        
        import time
        
        if activer_sortie_vde:
            temps_debut = time.time()
            # Simulation progressive de la poussée sur la grande surface (course en 1.5s)
            for i in range(101):
                st.session_state.pos_vde = i / 100.0
                plot_vde_placeholder.pyplot(dessiner_verin_double_effet(st.session_state.pos_vde, sens_mouvement="sortie"))
                temps_ecoule = time.time() - temps_debut
                chrono_de_placeholder.metric(label="Chronomètre dynamique", value=f"{temps_ecoule:.2f} s")
                time.sleep(0.015)
            chrono_de_placeholder.metric(label="Temps de course final (Sortie)", value=f"{time.time() - temps_debut:.2f} s")
            
        elif activer_rentree_vde:
            temps_debut = time.time()
            # Rentrée sur la surface réduite par la tige (course légèrement plus rapide en 1.3s)
            for i in range(100, -1, -1):
                st.session_state.pos_vde = i / 100.0
                plot_vde_placeholder.pyplot(dessiner_verin_double_effet(st.session_state.pos_vde, sens_mouvement="rentree"))
                temps_ecoule = time.time() - temps_debut
                chrono_de_placeholder.metric(label="Chronomètre dynamique", value=f"{temps_ecoule:.2f} s")
                time.sleep(0.013)
            chrono_de_placeholder.metric(label="Temps de course final (Rentrée)", value=f"{time.time() - temps_debut:.2f} s")

    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 4 ---
    if "suite_verrouille_tab4_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab4_pneumatique = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_pneumatique

    # Affichage du module de questions spécifique au VDE
    afficher_atelier_verin_double_effet(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Le vérin double effet.",
        key="check_certif_pneu4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_pneu_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q4 += 1.0

            score_t4 = 0.0
            if "champs_pneu4_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu4_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_pneu4_clean", "Choisir...") == attendu: score_t4 += 1.0

            st.session_state.score_suite4_pneu_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_pneu_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_pneu = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 4 ---
    if st.session_state.get("suite_verrouille_tab4_pneumatique", False):
        scr1_t4 = st.session_state.get("score_suite4_pneu_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_pneu_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_pneu", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER VÉRIN DOUBLE EFFET SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_pneu4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vérin Double Effet - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 4 : Différences structurelles, pilotage 5/2 et dissymétrie des efforts du double effet</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #7c3aed;">
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
        if "ordre_quiz_tab4_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_pneu4 += """
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
        if "champs_pneu4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu4_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 4
        html_export_pneu4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu4 = preparer_nom_fichier("Rapport_Verin_Double_Effet").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_pneu4,
            file_name=nom_fichier_html_pneu4,
            mime="text/html",
            use_container_width=True
        )




with tab5:
    st.header("Vérins rotatifs et autres actionneurs")
    
    # --- SECTION COURS : LES AUTRES ACTIONNEURS ---
    st.subheader("Les actionneurs rotatifs et de préhension")
    st.write(
        "Si les vérins linéaires simples et doubles effets couvrent la majorité des besoins de translation, les chaînes "
        "d'automatisation moderne imposent l'usage d'autres types de mouvements et d'actionneurs spécifiques de conversion :\n\n"
        "* **Le vérin rotatif :** Cet actionneur convertit l'énergie pneumatique en un mouvement de rotation angulaire limité "
        "(généralement 90 degrés, 180 degrés ou 270 degrés). À l'intérieur, le mouvement rectiligne du piston est transformé "
        "par un système **pignon-crémaillère**. Il est utilisé pour le retournement de colis, l'orientation de bras ou le pivotement de guides.\n"
        "* **La pince pneumatique (ou préhenseur) :** Intégrée à l'extrémité des bras de robots, elle comporte deux ou trois doigts mobiles "
        "synchronisés qui s'ouvrent et se ferment sous l'effet de mini-piston pour assurer la préhension mécanique de pièces rigides.\n"
        "* **Le moteur pneumatique :** Contrairement au vérin rotatif, il génère un mouvement de rotation continu à haute vitesse. "
        "Fonctionnant le plus souvent grâce à un rotor à palettes, il équipe les outils portatifs d'assemblage (visseuses, meuleuses) "
        "car il est léger, insensible à la surchauffe et ne produit aucune étincelle électrique."
    )
    
    st.divider()
    
    # --- LA TECHNIQUE DU VIDE ---
    st.subheader("La manipulation par le vide : Ventouses et Éjecteurs Venturi")
    st.write(
        "Pour manipuler des objets minces, fragiles, bombés ou de grandes dimensions (comme des plaques de verre, des tôle de carrosserie "
        "ou des cartons d'emballage), la préhension mécanique par pince est impossible ou risquée. On utilise alors la **technique du vide** "
        "qui s'appuie sur l'association de deux éléments distincts :\n\n"
        "1. **La ventouse :** Cet organe souple en élastomère ou en silicone vient s'appliquer contre la surface étanche de la pièce à soulever.\n"
        "2. **L'éjecteur (ou buse Venturi) :** N'ayant pas de pompe à vide mécanique, les machines génèrent une dépression locale en utilisant "
        "l'**effet Venturi**. L'air comprimé traverse une buse rétrécie, ce qui provoque une forte accélération de sa vitesse et crée, "
        "par aspiration naturelle, une zone de vide au niveau du raccord de la ventouse.\n\n"
        "La force de maintien dépend directement de la surface de la ventouse et du taux de vide obtenu (exprimé en pascals ou en bars négatifs). "
        "Pour relâcher l'objet instantanément, le distributeur coupe l'aspiration et envoie une brève impulsion d'air comprimé appelée **soufflage** "
        "pour chasser l'air de la ventouse."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_aut1, col_aut2 = st.columns(2)
    with col_aut1:
        st.write("**L'effet Venturi expliqué par la caricature**")
        st.write(
            "Pour faire imaginer ce phénomène aux élèves, on peut dessiner la caricature d'un couloir de métro très étroit "
            "où s'engouffre une foule de voyageurs pressés lancés en ligne droite (le flux d'air comprimé). "
            "À cause du rétrécissement de la buse, les voyageurs courent de plus en plus vite. En passant devant une porte latérale ouverte "
            "qui donne sur une pièce voisine (le tube de la ventouse), leur vitesse d'aspiration est telle qu'ils créent un puissant courant "
            "d'air de succion. Ce courant aspire littéralement tous les petits objets qui s'approchent de la porte, créant un vide d'air "
            "qui plaque fermement la feuille de carton contre la ventouse."
        )
        try:
            st.image("caricature_technique_du_vide.jpg", caption="Caricature de l'effet Venturi : La création du vide par accélération fluidique")
        except Exception:
            st.warning("L'image 'caricature_technique_du_vide.jpg' est introuvable.")

    with col_aut2:
        st.write("**Schémas et architecture d'un préhenseur par le vide**")
        st.write(
            "Sur le plan industriel, un circuit complet de manipulation par le vide comporte un distributeur de commande, "
            "l'éjecteur Venturi compact, et un manomètre inversé (vacuomètre) pour vérifier que la dépression est suffisante "
            "avant de lever la charge.\n\n"
            "Le cycle se termine par l'activation de la voie de soufflage, indispensable pour équilibrer la pression interne "
            "et garantir que la pièce se détache proprement à la cadence nominale du système automatisé."
        )
        try:
            st.image("montage_technique_du_vide.jpg", caption="Schéma structurel normalisé d'une ligne de préhension par ventouse")
        except Exception:
            st.warning("L'image 'montage_technique_du_vide.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab5_pneumatique = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_pneumatique

    # Affichage du module de questions spécifique aux autres actionneurs
    afficher_atelier_autres_actionneurs(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Actionneurs spéciaux et technique du vide.",
        key="check_certif_pneu5_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_pneu_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q5 += 1.0

            score_t5 = 0.0
            if "champs_pneu5_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu5_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_pneu5_clean", "Choisir...") == attendu: score_t5 += 1.0

            st.session_state.score_suite5_pneu_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_pneu_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_pneu = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 5 ---
    if st.session_state.get("suite_verrouille_tab5_pneumatique", False):
        scr1_t5 = st.session_state.get("score_suite5_pneu_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_pneu_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_pneu", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER ACTIONNEURS SPÉCIAUX SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_pneu5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Actionneurs Spéciaux - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 5 : Vérins rotatifs, pignon-crémaillère, préhenseurs et technique du vide par effet Venturi</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0369a1;">
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
        if "ordre_quiz_tab5_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_pneu5 += """
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
        if "champs_pneu5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu5_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu5_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 5
        html_export_pneu5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu5 = preparer_nom_fichier("Rapport_Actionneurs_Speciaux").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_pneu5,
            file_name=nom_fichier_html_pneu5,
            mime="text/html",
            use_container_width=True
        )


with tab6:
    st.header("Application 1 : Serrage")
    
    # --- MISE EN SITUATION INDUSTRIELLE ---
    st.subheader("Cahier des charges et description du système")
    st.write(
        "Dans une ligne de fabrication de mobilier en bois, un centre d'usinage automatisé doit réaliser "
        "des perçages de haute précision. Pour empêcher la pièce de bouger sous l'effet de la mèche en rotation, "
        "on utilise une **presse de bridage pneumatique**.\n\n"
        "Le système comprend un vérin double effet de forte puissance fixé sur un bâti rigide. "
        "Lorsque la pièce arrive sur le convoyeur, l'automate commande le distributeur 5/2 pour alimenter la chambre arrière. "
        "La tige sort, abaisse un bras articulé muni d'un patin en caoutchouc, et applique un effort de maintien "
        "constant. Un détecteur magnétique de fin de course valide le serrage avant d'autoriser le démarrage de la broche."
    )
    
    st.divider()
    
    # --- EXPLICATIONS ET PARAMÈTRES TECHNIQUES ---
    st.subheader("Analyse technique du circuit")
    st.write(
        "Le bon fonctionnement de cette application repose sur le réglage de plusieurs paramètres physiques fondamentaux :\n\n"
        "* **Le contrôle de l'effort :** La force d'immobilisation doit être suffisante pour bloquer la pièce, mais limitée "
        "pour ne pas marquer ou écraser le bois. L'opérateur utilise le régulateur de pression du groupe FRL pour ajuster "
        "la pression du circuit (généralement réglée à 5 bars pour cette application).\n"
        "* **Le contrôle de la vitesse :** Pour éviter un choc brutal du patin sur la pièce, des **régleurs de débit unidirectionnels** "
        "sont installés sur les orifices du vérin. Ils freinent l'air qui s'échappe de la chambre opposée, permettant "
        "une approche fluide et feutrée.\n"
        "* **La sécurité positive :** Le distributeur choisi est de type **bistable**. En cas de coupure de courant ou "
        "de baisse de pression d'urgence, le tiroir conserve sa configuration mécanique, maintenant la bride fermée "
        "pour empêcher la pièce d'être projetée dangereusement par la machine d'usinage."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_ap1_1, col_ap1_2 = st.columns(2)
    with col_ap1_1:
        st.write("**Le maintien mécanique expliqué par la caricature**")
        st.write(
            "Pour illustrer cette opération de blocage, on peut dessiner la caricature d'un athlète microscopique "
            "qui s'installe au-dessus de la pièce en bois. Dès que l'ordre est donné, il s'arc-boute contre le plafond "
            "du bâti et vient plaquer ses deux pieds lourds sur le madrier avec fermeté. "
            "Il maintient sa poussée olympique sans faiblir tout au long du travail de la machine. "
            "Même si la lumière s'éteint dans l'usine (coupure d'énergie), sa position de blocage reste verrouillée au sol, "
            "protégeant l'atelier jusqu'au retour de l'équipe de maintenance."
        )
        try:
            st.image("caricature_application_serrage.jpg", caption="Caricature de la fonction de bridage : L'immobilisation sécurisée de la charge")
        except Exception:
            st.warning("L'image 'caricature_application_serrage.jpg' est introuvable.")

    with col_ap1_2:
        st.write("**Schéma pneumatique normalisé de l'installation**")
        st.write(
            "Sur le plan technique, le schéma montre l'unité FRL reliée à l'orifice 1 du distributeur 5/2 bistable.\n\n"
            "Les orifices d'utilisation 2 et 4 alimentent les chambres du vérin double effet à travers les régleurs de débit. "
            "Les orifices 3 et 5 sont équipés de **silencieux d'échappement** en bronze frrité, indispensables pour dissiper "
            "l'énergie sonore des décharges d'air et protéger l'ouïe des opérateurs travaillant à proximité."
        )
        try:
            st.image("schema_circuit_serrage.jpg", caption="Schéma normalisé ISO du circuit pneumatique de la presse de bridage")
        except Exception:
            st.warning("L'image 'schema_circuit_serrage.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 6 ---
    if "suite_verrouille_tab6_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab6_pneumatique = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_pneumatique

    # Affichage de l'Atelier d'évaluation 6
    afficher_atelier_application1(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    
    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Application 1 : Serrage.",
        key="check_certif_pneu6_final_net",
        disabled=verrou_at6,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_pneu_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            if "ordre_quiz_tab6_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q6 += 1.0

            score_t6 = 0.0
            if "champs_pneu6_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu6_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_pneu6_clean", "Choisir...") == attendu: score_t6 += 1.0

            st.session_state.score_suite6_pneu_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_pneu_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_pneu = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ POUR L'ATELIER 6 ---
    if st.session_state.get("suite_verrouille_tab6_pneumatique", False):
        scr1_t6 = st.session_state.get("score_suite6_pneu_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_pneu_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6_pneu", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER SERRAGE SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_pneu6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Application Serrage - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 6 : Analyse d'une application industrielle de serrage et de bridage par bride mécanique</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #047857;">
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

        if "ordre_quiz_tab6_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_pneu6 += """
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
        if "champs_pneu6_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu6_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu6_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 6
        html_export_pneu6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu6 = preparer_nom_fichier("Rapport_Application_Serrage").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_pneu6,
            file_name=nom_fichier_html_pneu6,
            mime="text/html",
            use_container_width=True
        )

with tab7:
    st.header("Application 2 : Tri de colis")
    
    # --- MISE EN SITUATION INDUSTRIELLE ---
    st.subheader("Cahier des charges et description du système")
    st.write(
        "Dans un centre de dispatching logistique, un tapis convoyeur transporte des colis de tailles différentes "
        "à une cadence élevée de 40 colis par minute. Un système de tri automatique doit orienter les colis "
        "vers deux voies de destination distinctes selon leur code-barres.\n\n"
        "Le système utilise un actuateur pneumatique de type vérin double effet à course courte, équipé d'un volet d'aiguillage. "
        "Lorsqu'une cellule photoélectrique détecte un colis à trier, l'automate envoie un ordre électrique au distributeur. "
        "La tige sort instantanément pour pousser le colis vers la voie secondaire, puis doit revenir immédiatement "
        "dans sa configuration initiale pour ne pas bloquer le colis suivant."
    )
    
    st.divider()
    
    # --- EXPLICATIONS ET PARAMÈTRES TECHNIQUES ---
    st.subheader("Analyse technique du circuit")
    st.write(
        "Pour répondre aux exigences de vitesse et de sécurité de cette application de tri, le circuit pneumatique suit des règles strictes :\n\n"
        "* **Le choix de la commande :** Contrairement à la presse de serrage, on utilise ici un distributeur 5/2 **monostable** à commande électrique. "
        "Tant que la bobine (solénoïde) est alimentée, le vérin reste sorti. Dès que le colis est éjecté, l'automate coupe le signal et le ressort "
        "interne du distributeur ramène instantanément le tiroir. La tige rentre au repos de manière autonome, assurant une sécurité totale "
        "en cas de coupure de courant.\n"
        "* **La gestion de la haute cadence :** Les mouvements rapides répétés créent des chocs importants lorsque le piston percute les flasques "
        "du vérin. On utilise donc un vérin équipé d'**amortisseurs de fin de course pneumatiques réglables**. En fin de trajectoire, "
        "le piston emprisonne un petit volume d'air qui agit comme un coussin amortisseur, protégeant la structure mécanique du système.\n"
        "* **La maintenance de l'air :** Les cadences élevées provoquent une condensation importante de l'humidité dans les conduites. "
        "Le filtre de l'unité FRL élimine l'eau pour empêcher l'oxydation des tiroirs, tandis que le lubrificateur diffuse une micro-goutte "
        "d'huile pour maintenir un glissement parfait des joints à haute vitesse."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_ap2_1, col_ap2_2 = st.columns(2)
    with col_ap2_1:
        st.write("**Le va-et-vient rapide expliqué par la caricature**")
        st.write(
            "Pour faire comprendre ce mouvement de tri à haute vitesse, on peut imaginer la caricature d'un joueur de tennis "
            "microscopique posté au bord du tapis roulant. Dès qu'un colis jaune se présente, son entraîneur lui crie un ordre : "
            "le joueur déploie son bras avec vivacité pour frapper la balle et l'envoyer dans le couloir de droite. "
            "Mais son bras est relié à un gros élastique tendu (le ressort monostable du distributeur). Sitôt le coup de raquette donné, "
            "l'élastique le ramène de force et instantanément dans sa position de garde initiale, la raquette prête à intercepter le paquet suivant."
        )
        try:
            st.image("caricature_application_tri.jpg", caption="Caricature de l'éjection rapide : Le retour autonome de sécurité")
        except Exception:
            st.warning("L'image 'caricature_application_tri.jpg' est introuvable.")

    with col_ap2_2:
        st.write("**Schéma pneumatique normalisé de l'installation**")
        st.write(
            "Le schéma ISO représente le distributeur 5/2 avec son symbole de solénoïde électrique à gauche (borne 14) "
            "et son symbole de ressort mécanique de rappel à droite.\n\n"
            "Les régleurs de débit sont orientés pour contrôler la sortie rapide du vérin double effet. "
            "Les lignes d'échappement intègrent des silencieux pour étouffer le sifflement caractéristique des purges d'air "
            "à haute fréquence, garantissant un environnement de travail conforme aux normes de décibels industrielles."
        )
        try:
            st.image("schema_circuit_tri.jpg", caption="Schéma normalisé ISO du circuit de tri avec distributeur 5/2 monostable")
        except Exception:
            st.warning("L'image 'schema_circuit_tri.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 7 ---
    if "suite_verrouille_tab7_pneumatique" not in st.session_state:
        st.session_state.suite_verrouille_tab7_pneumatique = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_pneumatique

    # Affichage du module de questions spécifique à l'Application 2
    afficher_atelier_application2(verrouille=verrou_at7)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")
    
    case_certif_stat7 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Application 2 : Tri de colis.",
        key="check_certif_pneu7_final_net",
        disabled=verrou_at7,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_suite7_pneu_official", use_container_width=True, disabled=verrou_at7):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat7: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q7 = 0.0
            if "ordre_quiz_tab7_pneu_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab7_pneu_aleatoire:
                    saisie = st.session_state.get(f"pneu_at7_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q7 += 1.0

            score_t7 = 0.0
            if "champs_pneu7_clean" in st.session_state:
                for ligne in st.session_state.champs_pneu7_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_pneu7_clean", "Choisir...") == attendu: score_t7 += 1.0

            st.session_state.score_suite7_pneu_p1 = round(float(score_q7), 1)
            st.session_state.score_suite7_pneu_p2 = round(float(score_t7), 1)
            st.session_state.score_final_suite7_pneu = round(float(score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_pneumatique = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ POUR L'ATELIER 7 ---
    if st.session_state.get("suite_verrouille_tab7_pneumatique", False):
        scr1_t7 = st.session_state.get("score_suite7_pneu_p1", 0.0)
        scr2_t7 = st.session_state.get("score_suite7_pneu_p2", 0.0)
        tot_s_t7 = st.session_state.get("score_final_suite7_pneu", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRI DE COLIS SCELLÉ | Note de session : {tot_s_t7:.1f} / 20")

        html_export_pneu7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Application Tri - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation des Systèmes Pneumatiques</h1>
                <p>Atelier 7 : Analyse d'une application de tri de colis à haute cadence avec commande monostable</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t7:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #c2410c;">
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
        if "ordre_quiz_tab7_pneu_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_pneu_aleatoire, 1):
                saisie = st.session_state.get(f"pneu_at7_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pneu7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_pneu7 += """
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
        if "champs_pneu7_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pneu7_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pneu7_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pneu7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 7
        html_export_pneu7 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pneu7 = preparer_nom_fichier("Rapport_Application_Tri").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 7 (.html)",
            data=html_export_pneu7,
            file_name=nom_fichier_html_pneu7,
            mime="text/html",
            use_container_width=True
        )















        





        






