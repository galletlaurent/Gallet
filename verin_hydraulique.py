
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application verin hydraulique ",
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
st.title("Application verin hydraulique")
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
    "Les distributeurs hydraulique",
    "Le vérin simple effet",
    "Le vérin double effet",
    "Vérins rotatifs et autres actionneurs",
    "Application 1 : presse de compactage industrielle ",
    "Application 2 : Camion-grue "

])

tab0 = onglets[0]
tab1 = onglets[1] 
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4] 
tab5 = onglets[5] 
tab6 = onglets[6] 
tab7 = onglets[7] 



def afficher_atelier_application2(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 7 (Application 2 - Camion-Grue) sur deux colonnes."""
    import random

    questions_sources_ap2 = [
        {"id": "h_ap2_1", "q": "Quel type de machine utilise des béquilles et des vérins hydrauliques pour lever des blocs de béton ?", "options": ["Une grue de chantier (ou camion-grue)", "Un tapis de tri", "Une vis sans fin"], "rep": "Une grue de chantier (ou camion-grue)"},
        {"id": "h_ap2_2", "q": "Que se passe-t-il si un tuyau hydraulique se brise sous la charge ?", "options": ["Le vérin s'effondre instantanément s'il n'y a pas de clapet anti-retour de sécurité", "Le vérin monte au plafond", "L'huile se transforme en glace"], "rep": "Le vérin s'effondre instantanément s'il n'y a pas de clapet anti-retour de sécurité"},
        {"id": "h_ap2_3", "q": "Quel composant mécanique interdit le retour de l'huile et bloque le vérin en position même en cas de panne ?", "options": ["Un clapet anti-retour piloté", "Un silencieux poreux", "Un manomètre"], "rep": "Un clapet anti-retour piloté"},
        {"id": "h_ap2_4", "q": "Comment contrôle-t-on finement la vitesse de levage de la flèche de la grue ?", "options": ["En étranglant le débit d'huile à l'aide d'un étrangleur réglable", "En modifiant la viscosité de l'huile", "En changeant la taille du crochet"], "rep": "En étranglant le débit d'huile à l'aide d'un étrangleur réglable"},
        {"id": "h_ap2_5", "q": "Quelle pièce métallique transmet directement l'effort mécanique à la structure articulée ?", "options": ["La tige du vérin", "Le carter de pompe", "La bague de filtration"], "rep": "La tige du vérin"},
        {"id": "h_ap2_6", "q": "Pourquoi l'hydraulique est-elle préférée à la pneumatique sur un engin de chantier lourds ?", "options": ["Car l'incompressibilité de l'huile garantit un mouvement rigide, ultra-précis et sans à-coups élastiques", "Car l'huile est moins chère que l'air", "Car elle ne fait aucun bruit"], "rep": "Car l'incompressibilité de l'huile garantit un mouvement rigide, ultra-précis et sans à-coups élastiques"},
        {"id": "h_ap2_7", "q": "Le manomètre de la grue indique une pression de 200 bars. Cela correspond environ à :", "options": ["Une pression très élevée d'environ 20 millions de pascals", "La pression d'un pneu de vélo", "La pression atmosphérique normale"], "rep": "Une pression très élevée d'environ 20 millions de pascals"},
        {"id": "h_ap2_8", "q": "Quel phénomène destructeur se produit si des bulles d'air s'infiltrent et explosent dans la pompe ?", "options": ["La cavitation", "La décantation", "La solidification"], "rep": "La cavitation"},
        {"id": "h_ap2_9", "q": "Quel organne permet à l'opérateur de commander manuellement le mouvement depuis sa cabine ?", "options": ["Le manipulateur (ou joystick relié aux distributeurs)", "Le bouchon de remplissage", "Le niveau optique"], "rep": "Le manipulateur (ou joystick relié aux distributeurs)"},
        {"id": "h_ap2_10", "q": "L'ensemble des canalisations rigides et flexibles qui transportent l'huile forment le réseau de :", "options": ["Distribution et transmission", "Conversion d'énergie pure", "Stockage thermique"], "rep": "Distribution et transmission"}
    ]

    if "ordre_quiz_tab7_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_ap2)
        st.session_state.ordre_quiz_tab7_hydro_aleatoire = questions_sources_ap2

    st.session_state.champs_hydro7_clean = [
        ("1. Le camion-grue de chantier déploie des forces énormes pour lever le ..........", ["Choisir...", "béton", "carton"], "béton", "hydro7_t1"),
        ("2. Bloquer solidement le vérin en charge utilise un clapet anti-..........", ["Choisir...", "retour", "fuite"], "retour", "hydro7_t2"),
        ("3. Ajuster la vitesse de levage nécessite de réguler le .......... d'huile.", ["Choisir...", "débit", "volume"], "débit", "hydro7_t3"),
        ("4. L'incompressibilité du fluide évite les rebonds et les à-.......... dangereux.", ["Choisir...", "coups", "vides"], "coups", "hydro7_t4"),
        ("5. La pression de service atteint couramment des valeurs de 200 ..........", ["Choisir...", "bars", "pascals"], "bars", "hydro7_t5"),
        ("6. L'usure des composants provoquée par des bulles implosant est la ..........", ["Choisir...", "cavitation", "décantation"], "cavitation", "hydro7_t6"),
        ("7. Piloter le déploiement depuis la cabine s'appuie sur le .......... de commande.", ["Choisir...", "manipulateur", "manomètre"], "manipulateur", "hydro7_t7"),
        ("8. Le transport du fluide sous pression utilise des tuyaux .......... renforcés.", ["Choisir...", "flexibles", "plastiques"], "flexibles", "hydro7_t8"),
        ("9. Le fluide utilisé est une huile minérale spéciale pour circuit ..........", ["Choisir...", "hydraulique", "pneumatique"], "hydraulique", "hydro7_t9"),
        ("10. Ce protocole clôture l'analyse des actionneurs de transmission de ..........", ["Choisir...", "puissance", "chaleur"], "puissance", "hydro7_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab7_hydro_aleatoire" in st.session_state:
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_hydro_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"hydro_at7_final_g_{q_data['id']}"
                opts_affichees = ["Choisir..."] + q_data["options"]
                st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 cases - 10 pts)")
        if "champs_hydro7_clean" in st.session_state:
            for ligne in st.session_state.champs_hydro7_clean:
                # Découpage strict du tuple pour un affichage propre sans texte vert
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_hydro7_clean", disabled=verrouille, label_visibility="collapsed")
                    

def afficher_atelier_application1(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Application 1 - Compacteur) sur deux colonnes."""
    import random

    questions_sources_ap1 = [
        {"id": "h_ap1_1", "q": "Pourquoi utilise-t-on de l'huile hydraulique sous haute pression dans une presse de compactage ?", "options": ["Pour développer des forces colossales invisibles à l'œil nu", "Pour laver la ferraille", "Pour refroidir le moteur électrique"], "rep": "Pour développer des forces colossales invisibles à l'œil nu"},
        {"id": "h_ap1_2", "q": "Quel organe transforme l'énergie mécanique du moteur en puissance hydraulique (débit d'huile) ?", "options": ["La pompe hydraulique", "Le vérin", "Le réservoir"], "rep": "La pompe hydraulique"},
        {"id": "h_ap1_3", "q": "Quel appareil limite la pression maximale dans le circuit pour éviter l'explosion des tuyaux ?", "options": ["Le limiteur de pression (clapet de décharge)", "Le régleur de débit", "Le filtre"], "rep": "Le limiteur de pression (clapet de décharge)"},
        {"id": "h_ap1_4", "q": "Que fait le fluide lorsque le distributeur 4/2 bistable commute sa position ?", "options": ["Il inverse son sens de circulation vers le vérin", "Il s'évapore dans l'atmosphère", "Il se transforme en solide"], "rep": "Il inverse son sens de circulation vers le vérin"},
        {"id": "h_ap1_5", "q": "Quelle unité exprime la haute pression de service dans ces installations ?", "options": ["Le bar (ou mégapascal)", "Le newton", "Le litre par minute"], "rep": "Le bar (ou mégapascal)"},
        {"id": "h_ap1_6", "q": "Où retourne l'huile qui s'échappe de la chambre avant lors de la sortie du vérin ?", "options": ["Au réservoir (bac à huile)", "Dans la cabine", "Dans la nature"], "rep": "Au réservoir (bac à huile)"},
        {"id": "h_ap1_7", "q": "Si le diamètre du piston est doublé à pression constante, qu'advient-il de la force de compactage ?", "options": ["Elle est multipliée par quatre", "Elle reste identique", "Elle est divisée par deux"], "rep": "Elle est multipliée par quatre"},
        {"id": "h_ap1_8", "q": "Quel composant filtre les micro-particules métalliques pour protéger la pompe hydraulique ?", "options": ["Le filtre de retour", "Le manomètre", "La valve de vidange"], "rep": "Le filtre de retour"},
        {"id": "h_ap1_9", "q": "En hydraulique industrielle, l'huile est considérée comme un fluide :", "options": ["Incompressible (son volume ne varie pas sous la pression)", "Extrêmement compressible", "Gazeux"], "rep": "Incompressible (son volume ne varie pas sous la pression)"},
        {"id": "h_ap1_10", "q": "L'effort exercé par la tige dépend de la formule de la poussée :", "options": ["Force = Pression x Surface", "Force = Pression / Surface", "Force = Débit x Temps"], "rep": "Force = Pression x Surface"}
    ]

    if "ordre_quiz_tab6_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_ap1)
        st.session_state.ordre_quiz_tab6_hydro_aleatoire = questions_sources_ap1

    st.session_state.champs_hydro6_clean = [
        ("1. La presse industrielle utilise un fluide liquide sous haute ..........", ["Choisir...", "pression", "vitesse"], "pression", "hydro6_t1"),
        ("2. Générer le débit d'huile requis est le rôle de la .......... mécanique.", ["Choisir...", "pompe", "soupape"], "pompe", "hydro6_t2"),
        ("3. Protéger les conduites contre les surcharges exige un .......... de pression.", ["Choisir...", "limiteur", "régleur"], "limiteur", "hydro6_t3"),
        ("4. L'actionneur linéaire qui écrase la ferraille est un .......... double effet.", ["Choisir...", "vérin", "moteur"], "vérin", "hydro6_t4"),
        ("5. L'aiguillage de l'huile s'appuie sur un distributeur de type ..........", ["Choisir...", "4/2", "3/2"], "4/2", "hydro6_t5"),
        ("6. L'huile de retour inutilisée est stockée dans le .......... central.", ["Choisir...", "réservoir", "piston"], "réservoir", "hydro6_t6"),
        ("7. Contrairement à l'air, l'huile est un fluide .......... en pratique.", ["Choisir...", "incompressible", "gazeux"], "incompressible", "hydro6_t7"),
        ("8. La force de compactage dépend de la pression et de la .......... du piston.", ["Choisir...", "surface", "longueur"], "surface", "hydro6_t8"),
        ("9. Retenir les impuretés abrasives est assuré par le .......... à huile.", ["Choisir...", "filtre", "bouchon"], "filtre", "hydro6_t9"),
        ("10. Ce montage industriel réalise une application de puissance ..........", ["Choisir...", "hydraulique", "pneumatique"], "hydraulique", "hydro6_t10")
    ]

    if "ordre_quiz_tab6_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_ap1)
        st.session_state.ordre_quiz_tab6_hydro_aleatoire = questions_sources_ap1

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_tab6_hydro_aleatoire" in st.session_state:
            # Récupération de la position courante pour forcer l'unicité de la clé Streamlit
            pos_id = st.session_state.get("pos_ap1_hyd", 0.0)
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_hydro_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                
                # Clé dynamique unique basée sur l'état cinématique de la presse
                cle_select = f"at6_{q_data['id']}_p_{pos_id:.3f}"
                opts_affichees = ["Choisir..."] + q_data["options"]
                st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_hydro6_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_hydro6_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_actionneurs_rotatifs(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Actionneurs rotatifs) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_rot_1", "q": "Quelle est la fonction principale d'un vérin rotatif hydraulique ?", "options": ["Convertir l'énergie de pression en un mouvement de rotation angulaire limité", "Convertir le fluide en rotation continue infinie", "Augmenter la température de l'huile"], "rep": "Convertir l'énergie de pression en un mouvement de rotation angulaire limité"},
        {"id": "h_rot_2", "q": "Comment le mécanisme interne à pignon-crémaillère transforme-t-il le mouvement ?", "options": ["Le déplacement linéaire du piston pousse la crémaillère qui fait pivoter le pignon central", "L'huile fait tourner des hélices", "Le piston vibre pour faire tourner l'axe"], "rep": "Le déplacement linéaire du piston pousse la crémaillère qui fait pivoter le pignon central"},
        {"id": "h_rot_3", "q": "Quelle est l'amplitude de rotation standard la plus courante pour un vérin rotatif à crémaillère ?", "options": ["90 à 180 degrés (Un quart ou un demi-tour)", "3600 degrés sans limite", "Strictement 5 degrés maximum"], "rep": "90 à 180 degrés (Un quart ou un demi-tour)"},
        {"id": "h_rot_4", "q": "Quelle unité normalisée exprime le couple de torsion développé par un actionneur rotatif ?", "options": ["Le Newton-mètre (N.m)", "Le Mégapascal", "Le Litre par minute"], "rep": "Le Newton-mètre (N.m)"},
        {"id": "h_rot_5", "q": "À pression égale, comment augmenter le couple de torsion d'un vérin rotatif ?", "options": ["En augmentant le diamètre du piston ou le rayon primitif du pignon", "En réduisant le débit de la pompe", "En utilisant une huile plus noire"], "rep": "En augmentant le diamètre du piston ou le rayon primitif du pignon"},
        {"id": "h_rot_6", "q": "Quel type d'actionneur hydraulique utilise-t-on si l'on a besoin d'une rotation continue infinie (ex: treuil de navire) ?", "options": ["Un moteur hydraulique", "Un vérin double effet standard", "Un vérin rotatif à palettes"], "rep": "Un moteur hydraulique"},
        {"id": "h_rot_7", "q": "Comment représente-t-on graphiquement la fonction rotative limitée sur un symbole ISO 1219 ?", "options": ["Par un cercle contenant une flèche en arc de cercle à double sens", "Par un triangle noir pointant vers le bas", "Par un carré muni d'un ressort zigzag"], "rep": "Par un cercle contenant une flèche en arc de cercle à double sens"}
    ]

    if "ordre_quiz_tab5_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab5_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro5_clean = [
        ("1. Le vérin rotatif transforme l'énergie fluide en mouvement de .......... limité.", ["Choisir...", "rotation", "translation"], "rotation", "hydro5_t1"),
        ("2. La transformation mécanique s'appuie sur un système à pignon et ..........", ["Choisir...", "crémaillère", "bielle"], "crémaillère", "hydro5_t2"),
        ("3. L'effort de torsion de l'axe de sortie constitue le .......... mécanique.", ["Choisir...", "couple", "débit"], "couple", "hydro5_t3"),
        ("4. Le couple industriel développé s'exprime en ..........-mètres.", ["Choisir...", "Newton", "Pascal"], "Newton", "hydro5_t4"),
        ("5. Les angles de pivotement standard atteignent couramment .......... degrés.", ["Choisir...", "180", "3600"], "180", "hydro5_t5"),
        ("6. Générer une rotation continue infinie requiert l'usage d'un .......... hydraulique.", ["Choisir...", "moteur", "bloqueur"], "moteur", "hydro5_t6"),
        ("7. Les actionneurs rotatifs à pistons opposés possèdent .......... orifices actifs.", ["Choisir...", "deux", "quatre"], "deux", "hydro5_t7"),
        ("8. Le symbole ISO normalisé de cet actionneur est un .......... avec flèche courbe.", ["Choisir...", "cercle", "losange"], "cercle", "hydro5_t8"),
        ("9. Comme les vérins linéaires, l'huile assure une parfaite rigidité sans ..........", ["Choisir...", "jeu", "bruit"], "jeu", "hydro5_t9"),
        ("10. Ce module achève l'étude technologique des .......... de puissance.", ["Choisir...", "actionneurs", "filtres"], "actionneurs", "hydro5_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"hydro_at5_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_hydro5_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_hydro5_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_verin_double_effet_hydraulique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Vérin double effet) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_vde_1", "q": "Quelle est la caractéristique principale d'un vérin double effet hydraulique ?", "options": ["Il peut développer un effort et un mouvement contrôlés dans les deux sens de marche", "Il ne possède qu'un seul orifice d'alimentation", "Il tourne en continu sur 360 degrés"], "rep": "Il peut développer un effort et un mouvement contrôlés dans les deux sens de marche"},
        {"id": "h_vde_2", "q": "Pourquoi la vitesse de rentrée de la tige lourd est-elle supérieure à la vitesse de sortie à débit d'huile égal ?", "options": ["Car le volume à remplir à l'avant est réduit par la présence de la tige", "Car l'huile de retour pousse à l'arrière", "Car la pompe accélère automatiquement au retour"], "rep": "Car le volume à remplir à l'avant est réduit par la présence de la tige"},
        {"id": "h_vde_3", "q": "Pourquoi la force maximale développée en sortie est-elle supérieure à celle développée en rentrée à pression égale ?", "options": ["Car la tige diminue la surface utile du piston du côté de la chambre avant", "Car la gravité aide toujours la sortie", "Car la chambre arrière est plus chaude"], "rep": "Car la tige diminue la surface utile du piston du côté de la chambre avant"},
        {"id": "h_vde_4", "q": "Quel distributeur normalisé à commande électrique est le standard pour piloter un vérin double effet ?", "options": ["Un distributeur 4/2 ou 4/3", "Un distributeur 3/2 monostable", "Un clapet anti-retour simple"], "rep": "Un distributeur 4/2 ou 4/3"},
        {"id": "h_vde_5", "q": "Comment la viscosité de l'huile influence-t-elle le comportement cinématique de la tige ?", "options": ["Une huile plus visqueuse augmente les frottements fluides et ralentit le temps de course", "Une huile visqueuse annule la pression", "Elle rend la tige totalement flexible"], "rep": "Une huile plus visqueuse augmente les frottements fluides et ralentit le temps de course"},
        {"id": "h_vde_6", "q": "Quel composant interne du vérin assure la séparation étanche absolue entre la chambre arrière et la chambre avant ?", "options": ["Les joints de piston dynamiques", "La bague de friction du nez", "L'orifice d'évent"], "rep": "Les joints de piston dynamiques"},
        {"id": "h_vde_7", "q": "Quel appareil permet de mesurer en direct la pression hydrostatique dans une chambre de vérin ?", "options": ["Un manomètre", "Un densitomètre", "Un vacuomètre"], "rep": "Un manomètre"}
    ]

    if "ordre_quiz_tab4_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab4_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro4_clean = [
        ("1. Le vérin double effet possède .......... chambres d'alimentation étanches.", ["Choisir...", "deux", "une"], "deux", "hydro4_t1"),
        ("2. Alimenter l'orifice arrière provoque le mouvement de .......... de la tige.", ["Choisir...", "sortie", "rentrée"], "sortie", "hydro4_t2"),
        ("3. La présence de la tige diminue la surface .......... du piston à l'avant.", ["Choisir...", "utile", "totale"], "utile", "hydro4_t3"),
        ("4. À débit égal, la rentrée est plus .......... que la course de sortie.", ["Choisir...", "rapide", "lente"], "rapide", "hydro4_t4"),
        ("5. À pression égale, l'effort développé en sortie est le plus ..........", ["Choisir...", "grand", "faible"], "grand", "hydro4_t5"),
        ("6. Une huile de forte viscosité engendre des .......... fluides qui ralentissent le piston.", ["Choisir...", "frottements", "vides"], "frottements", "hydro4_t6"),
        ("7. L'étanchéité absolue entre les deux compartiments dépend des .......... de piston.", ["Choisir...", "joints", "bagues"], "joints", "hydro4_t7"),
        ("8. Le pilotage de cet actionneur est assuré par un distributeur .......... ou 4/3.", ["Choisir...", "4/2", "3/2"], "4/2", "hydro4_t8"),
        ("9. Freiner le piston juste avant le choc utilise un .......... de fin de course.", ["Choisir...", "amortisseur", "limiteur"], "amortisseur", "hydro4_t9"),
        ("10. Ce composant convertit la puissance hydraulique en puissance .......... linéaire.", ["Choisir...", "mécanique", "thermique"], "mécanique", "hydro4_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"hydro_at4_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_hydro4_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_hydro4_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_verin_simple_effet_hydraulique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Vérin simple effet) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_vse_1", "q": "Dans combien de directions un vérin simple effet hydraulique peut-il développer un effort moteur sous l'action du fluide ?", "options": ["Un seul sens de marche", "Deux sens opposés", "Uniquement en rotation continue"], "rep": "Un seul sens de marche"},
        {"id": "h_vse_2", "q": "Comment s'effectue généralement la rentrée de la tige sur un cric de levage hydraulique ?", "options": ["Sous l'action d'une charge extérieure (le poids du véhicule) lors de l'ouverture de la purge", "Grâce à une inversion du débit de la pompe", "Par aspiration de l'air ambiant"], "rep": "Sous l'action d'une charge extérieure (le poids du véhicule) lors de l'ouverture de la purge"},
        {"id": "h_vse_3", "q": "Combien d'orifices de raccordement fluidique possède le corps d'un vérin simple effet ?", "options": ["Un seul orifice", "Deux orifices indépendants", "Trois orifices avec drainage"], "rep": "Un seul orifice"},
        {"id": "h_vse_4", "q": "Quel type de distributeur est le standard minimal pour piloter la sortie et la rentrée d'un simple effet ?", "options": ["Un distributeur 3/2", "Un distributeur 4/3", "Un clapet anti-retour double"], "rep": "Un distributeur 3/2"},
        {"id": "h_vse_5", "q": "Quelle pièce cylindrique interne reçoit la poussée de l'huile et sépare les zones du cylindre ?", "options": ["Le piston", "La tige traversante", "Le nez de guidage"], "rep": "Le piston"},
        {"id": "h_vse_6", "q": "Que devient l'huile contenue dans la chambre lors de la rentrée de la tige provoquée par la charge ?", "options": ["Elle est refoulée vers le réservoir (bac à huile)", "Elle s'échappe dans l'atmosphère", "Elle est comprimée et s'échauffe indéfiniment"], "rep": "Elle est refoulée vers le réservoir (bac à huile)"},
        {"id": "h_vse_7", "q": "Pourquoi un vérin hydraulique permet-il un maintien en position fixe parfait par rapport à un vérin pneumatique ?", "options": ["Car l'huile est un fluide incompressible, ce qui empêche tout effet d'élasticité ou de rebond", "Car l'huile colle le piston", "Car la tige est plus lourde"], "rep": "Car l'huile est un fluide incompressible, ce qui empêche tout effet d'élasticité ou de rebond"},
        {"id": "h_vse_8", "q": "Quel est le rôle de l'orifice d'évent situé sur la chambre opposée (sans huile) d'un vérin simple effet ?", "options": ["Permettre à l'air de s'échapper ou d'entrer librement lors des mouvements du piston", "Injecter de la graisse de lubrification", "Mesurer la pression de service"], "rep": "Permettre à l'air de s'échapper ou d'entrer librement lors des mouvements du piston"},
        {"id": "h_vse_9", "q": "Si on applique une pression de 100 bars sur un piston de surface 10 cm², la force de poussée développée est de :", "options": ["10 000 Newtons", "1 000 Newtons", "100 Newtons"], "rep": "10 000 Newtons"},
        {"id": "h_vse_10", "q": "L'usage classique d'un vérin simple effet hydraulique en atelier mécanique concerne :", "options": ["Le levage de charges lourdes (crics, presses d'atelier)", "Les va-et-vient à très haute cadence", "La préhension de pièces légères fragiles"], "rep": "Le levage de charges lourdes (crics, presses d'atelier)"}
    ]

    if "ordre_quiz_tab3_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab3_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro3_clean = [
        ("1. Le vérin simple effet hydraulique ne possède qu'un seul .......... de pression.", ["Choisir...", "orifice", "tiroir"], "orifice", "hydro3_t1"),
        ("2. L'effort moteur développé s'exerce exclusivement dans .......... seul sens.", ["Choisir...", "un", "deux"], "un", "hydro3_t2"),
        ("3. La rentrée de la tige d'un cric exploite le poids de la .......... extérieure.", ["Choisir...", "charge", "pompe"], "charge", "hydro3_t3"),
        ("4. Pendant la rentrée, l'huile de la chambre est refoulée vers le ..........", ["Choisir...", "réservoir", "piston"], "réservoir", "hydro3_t4"),
        ("5. L'incompressibilité de l'huile permet d'obtenir un blocage rigide et ..........", ["Choisir...", "précis", "élastique"], "précis", "hydro3_t5"),
        ("6. L'évacuation ou l'aspiration de l'air interne utilise un orifice d'..........", ["Choisir...", "évent", "pression"], "évent", "hydro3_t6"),
        ("7. Piloter l'alimentation d'un simple effet requiert un distributeur ..........", ["Choisir...", "3/2", "4/3"], "3/2", "hydro3_t7"),
        ("8. La force de levage s'exprime dans l'unité internationale du ..........", ["Choisir...", "newton", "bar"], "newton", "hydro3_t8"),
        ("9. L'étanchéité glissante autour du piston est assurée par des .......... spécifiques.", ["Choisir...", "joints", "bagues"], "joints", "hydro3_t9"),
        ("10. Ce composant convertit la puissance fluide en puissance .......... rectiligne.", ["Choisir...", "mécanique", "thermique"], "mécanique", "hydro3_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        if "champs_hydro3_clean" in st.session_state:
            for ligne in st.session_state.champs_hydro3_clean:
                # Extraction par index pour supprimer le texte brut technique
                enonce = ligne[0]  # Extrait uniquement la phrase de cours propre
                choix = ligne[1]   # Extrait uniquement la liste des options de sélection
                cle = ligne[-1]    # Extrait la clé unique de session
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_hydro3_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_distributeurs_hydrauliques(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Les distributeurs) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_dist_1", "q": "Quelle est la fonction principale d'un distributeur dans un circuit hydraulique de puissance ?", "options": ["Distribuer (aiguiller l'huile sous pression)", "Convertir l'énergie en force", "Filtrer les impuretés du fluide"], "rep": "Distribuer (aiguiller l'huile sous pression)"},
        {"id": "h_dist_2", "q": "Que signifie la désignation d'un distributeur normalisé de type '4/3' ?", "options": ["4 orifices et 3 positions de fonctionnement", "4 bars de pression et 3 L/min de débit", "4 pistons reliés à 3 réservoirs"], "rep": "4 orifices et 3 positions de fonctionnement"},
        {"id": "h_dist_3", "q": "À quoi sert spécifiquement la position centrale (neutre) d'un distributeur 4/3 à centre fermé ?", "options": ["À bloquer instantanément le vérin en coupant la circulation d'huile", "À purger l'huile vers l'extérieur", "À augmenter la vitesse de la pompe"], "rep": "À bloquer instantanément le vérin en coupant la circulation d'huile"},
        {"id": "h_dist_4", "q": "Comment appelle-t-on la pièce cylindrique rectiligne interne qui coulisse pour ouvrir ou fermer les voies ?", "options": ["Le tiroir", "Le clapet de décharge", "La membrane"], "rep": "Le tiroir"},
        {"id": "h_dist_5", "q": "Par quelle lettre normalisée ISO désigne-t-on l'orifice d'entrée relié à la pompe de pression ?", "options": ["P (Pression)", "T (Tank / Réservoir)", "A (Utilisation)"], "rep": "P (Pression)"},
        {"id": "h_dist_6", "q": "Par quelle lettre normalisée ISO désigne-t-on l'orifice de retour relié au réservoir d'huile ?", "options": ["T (Tank)", "P (Pression)", "B (Utilisation)"], "rep": "T (Tank)"},
        {"id": "h_dist_7", "q": "Sur un schéma normalisé, comment modélise-t-on un orifice obturé (voie fermée) ?", "options": ["Par un symbole en forme de T", "Par une flèche oblique", "Par un cercle barré"], "rep": "Par un symbole en forme de T"},
        {"id": "h_dist_8", "q": "Quel type de commande utilise un signal électrique (bobine) pour déplacer mécaniquement le tiroir ?", "options": ["Une commande par électrovanne (solénoïde)", "Une commande par levier manuel", "Une commande par pédale"], "rep": "Une commande par électrovanne (solénoïde)"},
        {"id": "h_dist_9", "q": "Pourquoi les distributeurs hydrauliques de forte puissance possèdent-ils souvent un drainage externe ?", "options": ["Pour évacuer les fuites internes d'huile vers le réservoir sans bloquer le tiroir", "Pour refroidir la bobine", "Pour ajouter de l'huile neuve"], "rep": "Pour évacuer les fuites internes d'huile vers le réservoir sans bloquer le tiroir"},
        {"id": "h_dist_10", "q": "Dans quelle case d'un schéma normalisé à 3 positions raccorde-t-on les tuyaux de l'installation ?", "options": ["Dans la case centrale (position de repos)", "Dans la case de gauche", "Dans la case de droite"], "rep": "Dans la case centrale (position de repos)"}
    ]

    if "ordre_quiz_tab2_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab2_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro2_clean = [
        ("1. Le distributeur assure la fonction de .......... de l'énergie fluide.", ["Choisir...", "distribution", "conversion"], "distribution", "hydro2_t1"),
        ("2. Le premier chiffre d'un symbole normalisé indique le nombre d'..........", ["Choisir...", "orifices", "positions"], "orifices", "hydro2_t2"),
        ("3. Le second chiffre d'un symbole indique le nombre de .......... de fonctionnement.", ["Choisir...", "positions", "voies"], "positions", "hydro2_t3"),
        ("4. La pièce interne mobile qui coulisse pour orienter les flux est le ..........", ["Choisir...", "tiroir", "clapet"], "tiroir", "hydro2_t4"),
        ("5. L'orifice P est directement raccordé à la ligne de .......... de la pompe.", ["Choisir...", "pression", "réservoir"], "pression", "hydro2_t5"),
        ("6. L'huile usagée retourne au réservoir à travers l'orifice ..........", ["Choisir...", "T", "A"], "T", "hydro2_t6"),
        ("7. Un distributeur 4/3 possède rigoureusement .......... positions distinctes.", ["Choisir...", "trois", "deux"], "3", "hydro2_t7"),
        ("8. Le centre fermé permet d'immobiliser et de .......... l'actionneur.", ["Choisir...", "bloquer", "accélérer"], "bloquer", "hydro2_t8"),
        ("9. Une commande électrique s'appuie sur l'excitation d'un ..........", ["Choisir...", "solénoïde", "manomètre"], "solénoïde", "hydro2_t9"),
        ("10. Les flèches internes indiquent le sens de circulation du ..........", ["Choisir...", "fluide", "ressort"], "fluide", "hydro2_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_hydro2_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_hydro2_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_historique_hydraulique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Historique) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_hist_1", "q": "Quelle civilisation antique a largement développé les premiers moulins à eau pour moudre le grain ?", "options": ["Les Romains", "Les Mayas", "Les Vikings"], "rep": "Les Romains"},
        {"id": "h_hist_2", "q": "Quel ingénieur britannique a inventé la première presse hydraulique industrielle en 1795 ?", "options": ["Joseph Bramah", "James Watt", "Nikola Tesla"], "rep": "Joseph Bramah"},
        {"id": "h_hist_3", "q": "Quel savant français a énoncé le principe de transmission de la pression dans les liquides au XVIIe siècle ?", "options": ["Blaise Pascal", "René Descartes", "Antoine Lavoisier"], "rep": "Blaise Pascal"},
        {"id": "h_hist_4", "q": "Dans un moulin à eau traditionnel, quel composant mécanique reçoit directement la force du courant de la rivière ?", "options": ["La roue à aubes", "Le piston", "Le distributeur"], "rep": "La roue à aubes"},
        {"id": "h_hist_5", "q": "Quel est l'avantage historique majeur de la presse hydraulique par rapport aux mécanismes à leviers ?", "options": ["Multiplier les forces de manière considérable dans un espace réduit", "Fonctionner sans aucun fluide", "Produire de l'électricité"], "rep": "Multiplier les forces de manière considérable dans un espace réduit"},
        {"id": "h_hist_6", "q": "Quelle forme d'énergie est initialement captée par une roue hydraulique ?", "options": ["L'énergie cinétique et potentielle de l'eau", "L'énergie thermique du soleil", "L'énergie chimique"], "rep": "L'énergie cinétique et potentielle de l'eau"},
        {"id": "h_hist_7", "q": "Comment appelle-t-on la science qui étudie les fluides sous pression pour transmettre de la puissance ?", "options": ["L'oléohydraulique", "L'aérodynamique", "La thermodynamique"], "rep": "L'oléohydraulique"},
        {"id": "h_hist_8", "q": "Quel joint historique a permis d'assurer l'étanchéité des premiers pistons de Bramah sans bloquer le mouvement ?", "options": ["Le joint en cuir en forme de U", "La bague en plastique", "Le joint en silicone"], "rep": "Le joint en cuir en forme de U"},
        {"id": "h_hist_9", "q": "Les premiers réseaux de distribution d'énergie hydraulique dans les villes au XIXe siècle utilisaient :", "options": ["De l'eau sous pression", "De l'huile synthétique", "Du mercure lourd"], "rep": "De l'eau sous pression"},
        {"id": "h_hist_10", "q": "Le principe de Pascal affirme que dans un fluide incompressible en équilibre, la pression se transmet :", "options": ["Intégralement dans toutes les directions", "Uniquement vers le bas", "Uniquement vers la droite"], "rep": "Intégralement dans toutes les directions"}
    ]

    if "ordre_quiz_tab1_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab1_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro1_clean = [
        ("1. Les Romains utilisons l'énergie des rivières grâce aux moulins à ..........", ["Choisir...", "eau", "vent"], "eau", "hydro1_t1"),
        ("2. Le théorème de transmission de la pression a été formulé par ..........", ["Choisir...", "Pascal", "Bramah"], "Pascal", "hydro1_t2"),
        ("3. L'invention de la presse hydraulique est l'œuvre de Joseph ..........", ["Choisir...", "Bramah", "Watt"], "Bramah", "hydro1_t3"),
        ("4. Capter la force motrice du fluide utilise une roue à ..........", ["Choisir...", "aubes", "tiroirs"], "aubes", "hydro1_t4"),
        ("5. La presse hydraulique permet de multiplier considérablement les ..........", ["Choisir...", "forces", "vitesses"], "forces", "hydro1_t5"),
        ("6. L'huile industrielle moderne sert de fluide .......... pour la puissance.", ["Choisir...", "caloporteur", "transmetteur"], "transmetteur", "hydro1_t6"),
        ("7. Assurer l'étanchéité des premiers pistons utilisait un joint en ..........", ["Choisir...", "cuir", "caoutchouc"], "cuir", "hydro1_t7"),
        ("8. L'étude de l'utilisation technique de l'huile s'appelle l'..........", ["Choisir...", "oléohydraulique", "aéronautique"], "oléohydraulique", "hydro1_t8"),
        ("9. Dans un liquide au repos, la pression s'exerce de manière ..........", ["Choisir...", "isotrope", "unilatérale"], "isotrope", "hydro1_t9"),
        ("10. Ce parcours historique introduit la fonction d'alimentation en ..........", ["Choisir...", "débit", "chaleur"], "débit", "hydro1_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        if "champs_hydro1_clean" in st.session_state:
            for ligne in st.session_state.champs_hydro1_clean:
                # Ajout obligatoire des crochets d'indexation pour découper le tuple
                enonce = ligne[0]  # Extrait uniquement la phrase de cours propre
                choix = ligne[1]   # Extrait uniquement la liste des options ['Choisir...', ...]
                cle = ligne[-1]    # Extrait la clé unique de session
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_hydro1_clean", disabled=verrouille, label_visibility="collapsed")




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
    st.header("Historique de l'hydraulique de puissance")
    
    st.subheader("De l'énergie de l'eau aux forces industrielles")
    st.write(
        "L'histoire de l'hydraulique se divise en deux grandes époques : l'hydraulique naturelle (hydrodynamique) "
        "et l'hydraulique industrielle de puissance (oléohydraulique).\n\n"
        "Dès l'Antiquité, les Romains exploitent l'énergie cinétique des cours d'eau en installant de grands moulins "
        "à eau munis de **roues à aubes**. Cette technologie convertit la puissance du courant en force mécanique rotative "
        "pour actionner des meules à grains ou des martinets de forge, remplaçant la force humaine ou animale.\n\n"
        "La véritable révolution s'opère au dix-huitième siècle. En s'appuyant sur les travaux mathématiques de "
        "**Blaise Pascal** (qui démontra qu'une pression appliquée sur un liquide enfermé se transmet intégralement dans toutes "
        "les directions), l'ingénieur mécanicien anglais **Joseph Bramah** invente en 1795 la première **presse hydraulique**.\n"
        "En injectant de l'eau sous pression à l'aide d'une petite pompe vers un grand piston esclave, Bramah réussit "
        "à multiplier les forces de manière phénoménale, ouvrant la voie aux engins de levage lourds modernes."
    )
    
    st.divider()
    
    # --- SIMULATEUR DYNAMIQUE : LA ROUE À AUBES INTERACTIVE ---
    
    col_graph, col_bd = st.columns([0.55, 0.45])
    
    with col_graph:
        if "angle_roue" not in st.session_state:
            st.session_state.angle_roue = 0.0
        if "animation_active" not in st.session_state:
            st.session_state.animation_active = False

        st.subheader("Simulateur de roue hydraulique en mouvement")
        
        # Commandes de la vanne
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("OUVRIR LES VANNES (LANCER LA ROUE)", key="btn_run_wheel_fluid", use_container_width=True):
                st.session_state.animation_active = True
        with c_btn2:
            if st.button("FERMER LES VANNES (ARRÊTER)", key="btn_stop_wheel_fluid", use_container_width=True):
                st.session_state.animation_active = False

        # Curseur de débit
        debit_riviere = st.slider(
            "Ajuster le débit de la rivière (L/s) :", 
            min_value=0, 
            max_value=200, 
            value=80, 
            step=20, 
            key="slider_debit_h1_fluid"
        )

        # Création de zones réservées pour éviter que le texte et l'image ne sautent
        plot_placeholder = st.empty()
        metric_placeholder = st.empty()

        # Moteur de rendu graphique Matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        def generer_figure_roue(angle):
            fig, ax = plt.subplots(figsize=(5, 3.8), facecolor="white")
            ax.set_facecolor("white")
            
            # Écoulement de l'eau en fond (si la roue tourne)
            if st.session_state.animation_active and debit_riviere > 0:
                ax.add_patch(patches.Rectangle((0, 0), 5, 0.8, facecolor="#38bdf8", alpha=0.5, zorder=1))
            
            # Corps de la roue
            ax.add_patch(patches.Circle((2.5, 1.5), 1.0, facecolor="none", edgecolor="#1e293b", linewidth=3, zorder=2))
            ax.add_patch(patches.Circle((2.5, 1.5), 0.15, facecolor="#475569", zorder=3))
            
            # Les 8 aubes
            nb_aubes = 8
            for a in range(nb_aubes):
                angle_rad = np.radians(a * (360 / nb_aubes) + angle)
                x_aube = 2.5 + 1.2 * np.cos(angle_rad)
                y_aube = 1.5 + 1.2 * np.sin(angle_rad)
                ax.plot([2.5, x_aube], [1.5, y_aube], color="#475569", linewidth=2.5, zorder=2)
                
            ax.set_xlim(0, 5)
            ax.set_ylim(0, 3)
            ax.axis("off")
            return fig

        # --- BOUCLE D'ANIMATION LOCALE SANS RECHARGEMENT DE PAGE ---
        if st.session_state.animation_active and debit_riviere > 0:
            # Tant que l'animation est active, on met à jour uniquement les placeholders locaux
            while st.session_state.animation_active:
                vitesse_rotation = debit_riviere * 0.15
                puissance_recoltee = debit_riviere * 9.81 * 2.0 * 0.7
                
                # Mise à jour de l'image seule
                fig_actuelle = generer_figure_roue(st.session_state.angle_roue)
                plot_placeholder.pyplot(fig_actuelle)
                plt.close(fig_actuelle) # Fermeture immédiate de la figure pour libérer la mémoire RAM
                
                # Mise à jour des valeurs textuelles seules
                with metric_placeholder:
                    st.metric(label="Puissance mécanique récupérée", value=f"{puissance_recoltee:.0f} Watts", delta=f"{vitesse_rotation:.1f} tr/min")
                
                # Calcul du prochain angle
                st.session_state.angle_roue += (debit_riviere / 40.0)
                if st.session_state.angle_roue >= 360.0:
                    st.session_state.angle_roue = 0.0
                    
                # Pause courte pour stabiliser le framerate
                time.sleep(0.02)
        else:
            # Affichage fixe de sécurité si la roue est arrêtée
            fig_statique = generer_figure_roue(st.session_state.angle_roue)
            plot_placeholder.pyplot(fig_statique)
            plt.close(fig_statique)
            with metric_placeholder:
                st.metric(label="Puissance mécanique récupérée", value="0 Watts", delta="0.0 tr/min (Arrêté)")

    with col_bd:
        st.write("**La BD humoristique textuelle : L'astuce de Bramah**")
        st.info(
            "**Case 1 :** Un forgeron londonien du XVIIIe siècle s'épuise à frapper sur une enclume avec un énorme marteau en fer pour aplatir une barre de métal : 'Mes bras vont lâcher, il me faudrait la force de dix hommes !'.\n\n"
            "**Case 2 :** Joseph Bramah arrive dans l'atelier avec un grand sourire et pose une cuve métallique munie de deux tuyaux : 'Laisse ton marteau, l'ami ! On va faire travailler l'eau sous pression !'.\n\n"
            "**Case 3 :** Bramah actionne un tout petit levier de pompe sans aucun effort. À l'autre bout de la conduite, le grand piston descend avec la force d'un éléphant et écrase la barre de fer comme de la pâte à modeler : 'Crac !'.\n\n"
            "**Case 4 :** Le forgeron regarde ses bras musclés puis le piston avec stupéfaction. Bramah clin d'œil : 'C'est le secret de Blaise Pascal : tu pousses un centimètre cube d'eau d'un côté, et ça repousse cent centimètres carrés de l'autre !'."
        )
        
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 1 ---
    if "suite_verrouille_tab1_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab1_hydro = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_hydro

    # Affichage du module de questions spécifique à l'histoire
    afficher_atelier_historique_hydraulique(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.",
        key="check_certif_hydro1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_hydro_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q1 += 1.0

            score_t1 = 0.0
            if "champs_hydro1_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro1_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_hydro1_clean", "Choisir...") == attendu: score_t1 += 1.0

            st.session_state.score_suite1_hydro_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_hydro_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_hydro = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ ---
    if st.session_state.get("suite_verrouille_tab1_hydro", False):
        scr1_t1 = st.session_state.get("score_suite1_hydro_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_hydro_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_hydro", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 1 SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_hydro1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Hydraulique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 1 : Historique de l'hydraulique et théorème de Pascal</p>
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
        if "ordre_quiz_tab1_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_hydro1 += """
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
        if "champs_hydro1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 1
        html_export_hydro1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro1 = preparer_nom_fichier("Rapport_Histoire_Hydraulique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_hydro1,
            file_name=nom_fichier_html_hydro1,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Les distributeurs hydrauliques")
    
    # --- SECTION COURS : LES PRINCIPES DE LA DISTRIBUTION ---
    st.subheader("Rôle et architecture des pré-actionneurs hydrauliques")
    st.write(
        "Dans un circuit hydraulique industrielle de puissance, le distributeur fait office d'aiguilleur. "
        "Il reçoit l'huile sous haute pression en provenance directe de la pompe et l'oriente vers les canalisations "
        "utiles pour commander les actionneurs (vérins ou moteurs), tout en organisant le retour de l'huile viciée "
        "vers le réservoir central (bac).\n\n"
        "L'architecture interne repose sur un **tiroir métallique** rectifié au micron près qui coulisse à l'intérieur "
        "du corps de l'appareil. En se déplaçant, les collets du tiroir viennent masquer ou ouvrir les canaux internes. "
        "L'étanchéité reposant sur le film d'huile entre le tiroir et le corps, un léger débit de fuite interne existe "
        "toujours à haute pression, ce qui nécessite parfois un canal de drainage externe pour éviter le blocage mécanique."
    )
    
    st.divider()
    
    st.subheader("Lecture des symboles ISO normalisés : Le standard 4/3")
    st.write(
        "L'hydraulique utilise massivement des distributeurs à **3 positions (comme le 4/3)** pour permettre le blocage ou "
        "la mise en roue libre des mécanismes lourds. Sa codification s'énonce ainsi :\n"
        "* **Le premier chiffre (4) :** Indique le nombre d'orifices (P pour la Pression de la pompe, T pour le Tank/Réservoir, "
        "A et B pour les conduites reliées aux chambres de l'actionneur).\n"
        "* **Le second chiffre (3) :** Indique le nombre de cases carrées juxtaposées, modélisant les 3 configurations de flux possibles.\n\n"
        "Par convention internationale, les raccordements des canalisations extérieures sont toujours dessinés graphiquement "
        "sur la case centrale représentant la position de **repos / neutre**."
    )
    
    st.divider()
    
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE DU TIROIR COMMUTABLE ---
    st.subheader("Simulateur graphique d'aiguillage de fluide")
    st.write(
        "Sélectionnez la position du distributeur 4/3 à l'aide des boutons ci-dessous. "
        "Le graphique Matplotlib redessinera instantanément la position du tiroir interne et colorera les flux d'huile active."
    )
    
    # Boutons radio horizontaux pour le choix de la position
    pos_choisie = st.radio(
        "Sélectionner l'état de la commande :",
        options=["Position de gauche (Voie croisée)", "Position centrale (Repos - Centre fermé)", "Position de droite (Voie droite)"],
        index=1,
        key="radio_pos_dist_h2",
        horizontal=True
    )
    
    col_dist_graph, col_dist_bd = st.columns([0.55, 0.45])

    with col_dist_graph:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig_ds, ax_ds = plt.subplots(figsize=(5.5, 4.2), facecolor="white")
        ax_ds.set_facecolor("white")
        
        # 1. Dessin du corps externe fixe du distributeur (Chambre d'alésage)
        ax_ds.add_patch(patches.Rectangle((0.8, 1.0), 3.4, 1.2, facecolor="#f8fafc", edgecolor="#475569", linewidth=3, zorder=1))
        
        # 2. Dessin des conduites fixes externes (Canalisations d'usine)
        ax_ds.plot([1.5, 1.5], [0.3, 1.0], color="#334155", linewidth=3, zorder=2) # P
        ax_ds.plot([3.5, 3.5], [0.3, 1.0], color="#334155", linewidth=3, zorder=2) # T
        ax_ds.plot([1.8, 1.8], [2.2, 2.9], color="#334155", linewidth=3, zorder=2) # A
        ax_ds.plot([3.2, 3.2], [2.2, 2.9], color="#334155", linewidth=3, zorder=2) # B
        
        # Lettrage normalisé ISO
        ax_ds.text(1.5, 0.05, "P\n(Pompe)", weight="bold", ha="center", color="#b91c1c", fontsize=10)
        ax_ds.text(3.5, 0.05, "T\n(Réservoir)", weight="bold", ha="center", color="#0284c7", fontsize=10)
        ax_ds.text(1.8, 3.05, "A", weight="bold", ha="center", color="#1e293b", fontsize=11)
        ax_ds.text(3.2, 3.05, "B", weight="bold", ha="center", color="#1e293b", fontsize=11)
        
        # 3. Logique mécanique des positions du tiroir
        if "gauche" in pos_choisie:
            dx_tiroir = -0.5
            annotation_etat = "ALIMENTATION DE B (HAUTE PRESSION) | RETOUR DE A VERS T"
            
            # Flèche Pression : P -> B (Croisé, vers le haut et la droite)
            ax_ds.arrow(1.5, 1.05, 1.6, 1.05, head_width=0.15, head_length=0.15, fc="#b91c1c", ec="#b91c1c", linewidth=4, length_includes_head=True, zorder=4)
            # Flèche Retour : A -> T (Croisé, vers le bas et la droite)
            ax_ds.arrow(1.8, 2.15, 1.6, -1.05, head_width=0.15, head_length=0.15, fc="#0284c7", ec="#0284c7", linewidth=4, length_includes_head=True, zorder=4)
            
        elif "droite" in pos_choisie:
            dx_tiroir = 0.5
            annotation_etat = "ALIMENTATION DE A (HAUTE PRESSION) | RETOUR DE B VERS T"
            
            # Flèche Pression : P -> A (Droit, vers le haut et la droite)
            ax_ds.arrow(1.5, 1.05, 0.25, 1.05, head_width=0.15, head_length=0.15, fc="#b91c1c", ec="#b91c1c", linewidth=4, length_includes_head=True, zorder=4)
            # Flèche Retour : B -> T (Droit, vers le bas et la droite)
            ax_ds.arrow(3.2, 2.15, 0.25, -1.05, head_width=0.15, head_length=0.15, fc="#0284c7", ec="#0284c7", linewidth=4, length_includes_head=True, zorder=4)
            
        else:
            dx_tiroir = 0.0
            annotation_etat = "CENTRE FERMÉ : TOUT EST BLOQUÉ (VÉRIN IMMOBILISÉ)"
            
            # Représentation graphique des symboles de voies obturées (T de blocage)
            # Blocage Pression au seuil inférieur
            ax_ds.plot([1.3, 1.7], [1.1, 1.1], color="#b91c1c", linewidth=4, zorder=5)
            # Blocage Réservoir
            ax_ds.plot([3.3, 3.7], [1.1, 1.1], color="#64748b", linewidth=4, zorder=5)
            # Blocage des orifices d'utilisation au seuil supérieur
            ax_ds.plot([1.6, 2.0], [2.1, 2.1], color="#64748b", linewidth=4, zorder=5)
            ax_ds.plot([3.0, 3.4], [2.1, 2.1], color="#64748b", linewidth=4, zorder=5)
            
        # 4. Dessin de la pièce mobile interne (Axe du tiroir + collets d'étanchéité)
        x_tiroir_base = 1.0 + dx_tiroir
        # Axe central gris
        ax_ds.add_patch(patches.Rectangle((x_tiroir_base - 0.3, 1.45), 3.6, 0.3, facecolor="#64748b", edgecolor="#334155", linewidth=1.5, zorder=3))
        
        # Collets d'étanchéité (Les pistons internes qui ferment physiquement les trous)
        # Collet gauche
        ax_ds.add_patch(patches.Rectangle((x_tiroir_base + 0.3, 1.05), 0.5, 1.1, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
        # Collet droit
        ax_ds.add_patch(patches.Rectangle((x_tiroir_base + 2.2, 1.05), 0.5, 1.1, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
        
        # 5. Habillage du graphique
        ax_ds.set_xlim(0, 5)
        ax_ds.set_ylim(-0.3, 3.5)
        ax_ds.axis("off")
        st.pyplot(fig_ds)
        
        # En-tête textuel coloré dynamique sous le schéma
        if "Centre" in annotation_etat:
            st.error(annotation_etat)
        else:
            st.success(annotation_etat)

    with col_dist_bd:
        st.write("**La BD humoristique textuelle : Le carrefour des vannes**")
        st.info(
            "**Case 1 :** Un groupe de molécules d'huile arrive à toute vitesse dans un tuyau, poussé par la pompe : "
            "'On arrive en ville à 200 bars, ouvrez la route !'. Elles tombent sur une barrière grise fermée.\n\n"
            "**Case 2 :** Un petit aiguilleur en casquette (le solénoïde électrique) appuie sur un bouton. "
            "Le gros tiroir métallique interne glisse latéralement dans un bruit de friction métallique : 'Schliiiit !'.\n\n"
            "**Case 3 :** Les canaux s'alignent. Les molécules d'huile s'engouffrent en ligne droite vers l'orifice A : "
            "'Voie dégagée ! Tout le monde fonce dans la chambre arrière du vérin pour soulever la grue !'.\n\n"
            "**Case 4 :** Soudain, l'automate coupe le courant. Le gros ressort de rappel repousse le tiroir au centre. "
            "Les molécules se retrouvent instantanément bloquées dans une impasse étanche : "
            "'Fin du voyage ! Centre fermé ! Tout le monde s'arrête sur place et maintient la charge en l'air !'."
        )
        
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab2_hydro = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_hydro

    # Affichage du module de questions spécifique aux distributeurs hydrauliques
    afficher_atelier_distributeurs_hydrauliques(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 2.",
        key="check_certif_hydro2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_hydro_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q2 += 1.0

            score_t2 = 0.0
            if "champs_hydro2_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro2_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_hydro2_clean", "Choisir...") == attendu: score_t2 += 1.0

            st.session_state.score_suite2_hydro_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_hydro_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_hydro = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2_hydro", False):
        scr1_t2 = st.session_state.get("score_suite2_hydro_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_hydro_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_hydro", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER DISTRIBUTEURS SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_hydro2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Distributeurs Hydrauliques - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 2 : Organes de distribution, tiroirs micrométriques et symbolisation ISO 4/3</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
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
        if "ordre_quiz_tab2_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_hydro2 += """
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
        if "champs_hydro2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 2
        html_export_hydro2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro2 = preparer_nom_fichier("Rapport_Distributeurs_Hydrauliques").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_hydro2,
            file_name=nom_fichier_html_hydro2,
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("Le vérin simple effet")
    if "suite_verrouille_tab3_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab3_hydro = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_hydro    
    # --- SECTION COURS : LE VÉRIN SIMPLE EFFET ---
    st.subheader("Constitution et loi physique de l'actionneur unidirectionnel")
    st.write(
        "Un vérin simple effet (VSE) hydraulique est un actionneur linéaire conçu pour développer une force "
        "motrice dans **un seul sens de marche**. Le corps du vérin ne comporte qu'une seule chambre étanche "
        "destinée à recevoir l'huile sous haute pression.\n\n"
        "Le mouvement inverse (généralement la rentrée de la tige) n'est pas provoqué par le fluide. Il utilise "
        "soit l'action d'un ressort mécanique interne de rappel, soit l'action d'une **force extérieure** "
        "(comme le poids d'une voiture sur un cric d'atelier ou la gravité sur une table élévatrice).\n\n"
        "L'avantage majeur de l'hydraulique par rapport à la pneumatique réside dans l'**incompressibilité du liquide**. "
        "Lorsqu'on ferme la vanne d'admission, l'huile emprisonnée se comporte comme un bloc d'acier rigide : "
        "le vérin reste parfaitement figé à sa hauteur, sans aucun rebond ni affaissement élastique, garantissant "
        "une sécurité absolue lors du levage de charges lourdes."
    )
    
    st.divider()
    if "pos_vse_hyd" not in st.session_state: st.session_state.pos_vse_hyd = 0.0
    if "vse_mouvement" not in st.session_state: st.session_state.vse_mouvement = "ARRET"
    if "temps_debut_vse" not in st.session_state: st.session_state.temps_debut_vse = 0.0
    if "temps_course_vse" not in st.session_state: st.session_state.temps_course_vse = 0.0

    st.subheader("Simulateur mécanique multi-métiers")
    type_huile_vse = st.selectbox(
        "Sélectionner l'application et le type de fluide hydraulique :",
        options=[
            "Automobile - Cric de levage d'atelier (Huile fluide ISO VG 32 - Course max 200 mm)",
            "Maintenance - Presse hydraulique d'atelier (Huile standard ISO VG 46 - Course max 400 mm)",
            "Agriculture - Vérin de benne de tracteur (Huile épaisse ISO VG 68 - Course max 1200 mm)"
        ],
        key="select_huile_vse_tab3_secured"
    )

    pas_course = 0.05 if "Automobile" in type_huile_vse else (0.03 if "Maintenance" in type_huile_vse else 0.015)
    course_max_reelle_mm = 200.0 if "Automobile" in type_huile_vse else (400.0 if "Maintenance" in type_huile_vse else 1200.0)
    vse_bloque = (st.session_state.vse_mouvement != "ARRET")


    c_cmd1, c_cmd2 = st.columns(2)
    with c_cmd1:
        if st.button("ALIMENTER L'ORIFICE 1 (SORTIE CHRONOMÉTRÉE)", key="btn_push_vse_t3", use_container_width=True, disabled=vse_bloque or st.session_state.pos_vse_hyd >= 1.0):
            st.session_state.vse_mouvement = "SORTIE"
            st.session_state.temps_debut_vse = time.time()
            st.rerun()
    with c_cmd2:
        if st.button("OUVRIR LE RETOUR AU BAC (RENTRÉE CHRONOMÉTRÉE)", key="btn_purge_vse_t3", use_container_width=True, disabled=vse_bloque or st.session_state.pos_vse_hyd <= 0.0):
            st.session_state.vse_mouvement = "RENTREE"
            st.session_state.temps_debut_vse = time.time()
            st.rerun()

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # 1. COUPE MÉCANIQUE DYNAMIQUE
    fig_v, ax_v = plt.subplots(figsize=(6, 2.6), facecolor="white")
    ax_v.set_facecolor("white")
    ax_v.add_patch(patches.Rectangle((0.5, 1.0), 3.0, 1.4, facecolor="#f1f5f9", edgecolor="#475569", linewidth=2.5, zorder=1))
    ax_v.plot([3.5, 3.5], [1.0, 2.4], color="#334155", linewidth=3, zorder=2)
    ax_v.plot([1.0, 1.0], [0.4, 1.0], color="#334155", linewidth=2.5, zorder=2)
    ax_v.text(1.0, 0.15, "Orifice 1", weight="bold", ha="center", fontsize=9)
    ax_v.plot([3.0, 3.0], [2.4, 2.8], color="#64748b", linewidth=1.5, zorder=2)
    
    course_vse_pixels = st.session_state.pos_vse_hyd * 2.6
    x_piston_vse = 0.6 + course_vse_pixels
    color_fluide_vse = "#b91c1c" if st.session_state.vse_mouvement == "SORTIE" else ("#0284c7" if st.session_state.vse_mouvement == "RENTREE" else "#eab308")
    if x_piston_vse > 0.62:
        ax_v.add_patch(patches.Rectangle((0.52, 1.03), x_piston_vse - 0.52, 1.34, facecolor=color_fluide_vse, alpha=0.5, zorder=1))
    ax_v.add_patch(patches.Rectangle((x_piston_vse, 1.03), 0.3, 1.34, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
    ax_v.add_patch(patches.Rectangle((x_piston_vse + 0.3, 1.45), 3.5, 0.5, facecolor="#94a3b8", edgecolor="#334155", linewidth=1.5, zorder=2))
    
    x_bout_tige_vse = x_piston_vse + 3.8
    ax_v.arrow(x_bout_tige_vse + 0.6, 1.7, -0.5, 0, head_width=0.12, head_length=0.12, fc="black", ec="black", linewidth=2.5, length_includes_head=True, zorder=4)
    ax_v.text(x_bout_tige_vse + 0.1, 1.9, r"$\vec{F}_{\text{charge}}$", color="black", weight="bold", fontsize=11)
    ax_v.set_xlim(0, 8.5)
    ax_v.set_ylim(-0.2, 3.2)
    ax_v.axis("off")
    st.pyplot(fig_v)
    plt.close(fig_v)

    # 2. SCHÉMA NORMALISÉ ISO AVEC DISTRIBUTEUR 3/2 ET FLÈCHES DYNAMIQUES
    st.write("**Schéma d'implantation industrielle normalisé (ISO 1219) :**")
    fig_iso3, ax_iso3 = plt.subplots(figsize=(6, 2.2), facecolor="white")
    ax_iso3.set_facecolor("white")
    
    # Pompe et bac
    ax_iso3.add_patch(patches.Circle((2.0, 0.3), 0.2, facecolor="none", edgecolor="black", linewidth=2))
    ax_iso3.plot([2.0, 1.9, 2.1, 2.0], [0.4, 0.48, 0.48, 0.4], color="black", linewidth=2)
    ax_iso3.plot([2.8, 2.8, 3.2, 3.2], [0.3, 0.0, 0.0, 0.3], color="black", linewidth=2) # Reservoir
    
    # Cases distributeur 3/2
    ax_iso3.add_patch(patches.Rectangle((1.5, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
    ax_iso3.add_patch(patches.Rectangle((2.3, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=2, zorder=3))
    
    # Dessin des flèches internes 3/2 selon l'état
    if st.session_state.vse_mouvement == "SORTIE":
        ax_iso3.arrow(2.7, 0.75, 0, 0.5, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
        ax_iso3.plot([1.9, 1.9], [0.75, 1.15], color="#64748b", linewidth=1)
        ax_iso3.plot([1.7, 2.1], [1.15, 1.15], color="#64748b", linewidth=1)
    elif st.session_state.vse_mouvement == "RENTREE":
        ax_iso3.arrow(1.9, 1.35, 0, -0.5, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
        ax_iso3.plot([2.7, 2.7], [0.75, 0.95], color="#64748b", linewidth=1)
        ax_iso3.plot([2.5, 2.9], [0.95, 0.95], color="#64748b", linewidth=1)
    else:
        ax_iso3.plot([1.9, 1.9], [0.75, 1.35], color="#64748b", linewidth=1.2)
        ax_iso3.plot([2.7, 2.7], [0.75, 1.35], color="#64748b", linewidth=1.2)

    # Levier manuel
    ax_iso3.plot([1.5, 1.3], [1.05, 1.35], color="black", linewidth=2.5, zorder=4)
    ax_iso3.add_patch(patches.Circle((1.3, 1.35), 0.05, facecolor="#b91c1c", edgecolor="black", zorder=5))
    
    # Conduites d'interconnexion
    c_pression = "#b91c1c" if st.session_state.vse_mouvement == "SORTIE" else "#0284c7"
    ax_iso3.plot([2.0, 2.0], [0.5, 0.7], color="#b91c1c", linewidth=2.5)
    ax_iso3.plot([3.0, 3.0], [0.3, 0.7], color="#0284c7", linewidth=2.5)
    ax_iso3.plot([2.0, 2.0, 3.5, 3.5], [1.4, 1.6, 1.6, 1.8], color=c_pression, linewidth=2.5)
    
    # Actionneur simple effet symbole
    ax_iso3.add_patch(patches.Rectangle((3.5, 1.8), 2.0, 0.5, facecolor="none", edgecolor="black", linewidth=2))
    x_p_s3 = 3.6 + (st.session_state.pos_vse_hyd * 1.2)
    ax_iso3.plot([x_p_s3, x_p_s3], [1.8, 2.3], color="black", linewidth=2.5)
    ax_iso3.plot([x_p_s3, 6.0], [2.05, 2.05], color="black", linewidth=2.5)
    
    ax_iso3.set_xlim(0.5, 6.5)
    ax_iso3.set_ylim(-0.1, 2.5)
    ax_iso3.axis("off")
    st.pyplot(fig_iso3)
    plt.close(fig_iso3)

    # MACHINE CHRONO VSE
    longueur_sortie_mm = st.session_state.pos_vse_hyd * course_max_reelle_mm
    if st.session_state.vse_mouvement != "ARRET":
        st.session_state.temps_course_vse = time.time() - st.session_state.temps_debut_vse
        if st.session_state.vse_mouvement == "SORTIE":
            st.session_state.pos_vse_hyd = min(1.0, st.session_state.pos_vse_hyd + pas_course)
            if st.session_state.pos_vse_hyd >= 1.0: st.session_state.vse_mouvement = "ARRET"
        elif st.session_state.vse_mouvement == "RENTREE":
            st.session_state.pos_vse_hyd = max(0.0, st.session_state.pos_vse_hyd - (pas_course * 1.2))
            if st.session_state.pos_vse_hyd <= 0.0: st.session_state.vse_mouvement = "ARRET"
        c_m1, c_met2 = st.columns(2)
        c_m1.metric("Chronomètre de course", f"{st.session_state.temps_course_vse:.2f} s", f"Course : {st.session_state.pos_vse_hyd * 100:.0f} %")
        c_met2.metric("Longueur de sortie", f"{longueur_sortie_mm:.1f} mm", "En déplacement")
        time.sleep(0.04)
        st.rerun()
    else:
        c_m1, c_met2 = st.columns(2)
        c_m1.metric("Temps mesuré", f"{st.session_state.temps_course_vse:.2f} s", "Immobile")
        c_met2.metric("Longueur de sortie", f"{longueur_sortie_mm:.1f} mm", "Position verrouillée", delta_color="off")

    st.divider()
    afficher_atelier_verin_simple_effet_hydraulique(verrouille=vse_bloque)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 3.",
        key="check_certif_hydro3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_hydro_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q3 += 1.0

            score_t3 = 0.0
            if "champs_hydro3_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro3_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_hydro3_clean", "Choisir...") == attendu: score_t3 += 1.0

            st.session_state.score_suite3_hydro_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_hydro_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_hydro = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 3 ---
    if st.session_state.get("suite_verrouille_tab3_hydro", False):
        scr1_t3 = st.session_state.get("score_suite3_hydro_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_hydro_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_hydro", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER VÉRIN SIMPLE EFFET SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_hydro3 = f"""<!DOCTYPE html>
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
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 3 : Constitution, incompressibilité et blocage rigide du vérin simple effet</p>
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
        if "ordre_quiz_tab3_hydro_delta" in st.session_state or "ordre_quiz_tab3_hydro_aleatoire" in st.session_state:
            cle_session_quiz = "ordre_quiz_tab3_hydro_aleatoire" if "ordre_quiz_tab3_hydro_aleatoire" in st.session_state else "ordre_quiz_tab3_hydro_delta"
            for num, q_item in enumerate(st.session_state[cle_session_quiz], 1):
                saisie = st.session_state.get(f"hydro_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_hydro3 += """
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
        if "champs_hydro3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 3
        html_export_hydro3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro3 = preparer_nom_fichier("Rapport_Verin_Simple_Effet_Hydraulique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_hydro3,
            file_name=nom_fichier_html_hydro3,
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("Le vérin double effet")
    
    # --- SECTION COURS : LE VÉRIN DOUBLE EFFET ---
    st.subheader("Analyse de la dissymétrie des surfaces and forces hydrauliques")
    st.write(
        "Le vérin double effet (VDE) est l'actionneur de puissance le plus utilisé pour la manutention lourde. "
        "Il possède deux orifices d'alimentation permettant d'injecter le fluide alternativement d'un côté ou "
        "de l'autre du piston, ce qui permet de développer une action motrice **dans les deux sens de déplacement**.\n\n"
        "Cependant, ce pré-actionneur présente une dissymétrie physique fondamentale due à la présence de la tige métallique :\n"
        "* **En poussée (Sortie) :** L'huile agit sur la **surface totale** du piston. La force est maximale.\n"
        "* **En traction (Rentrée) :** L'huile agit sur une **surface utile réduite** (la surface du piston moins la section de la tige). La force est plus faible.\n\n"
        "À débit de pompe rigoureusement constant, cette dissymétrie géométrique inverse le comportement des vitesses : "
        "la chambre avant ayant un volume plus petit à remplir, la tige rentrera toujours plus rapidement qu'elle ne sortira à l'écran."
    )
    
    st.divider()
    
    if "pos_vde_hyd" not in st.session_state: st.session_state.pos_vde_hyd = 0.0
    if "vde_mouvement" not in st.session_state: st.session_state.vde_mouvement = "ARRET"
    if "temps_debut_vde" not in st.session_state: st.session_state.temps_debut_vde = 0.0
    if "temps_course_vde" not in st.session_state: st.session_state.temps_course_vde = 0.0

    huile_vde = st.selectbox(
        "Sélectionner l'application et le type de fluide hydraulique :",
        options=[
            "Automobile - Assistance de direction (Huile fluide ISO VG 32 - Course max 300 mm)",
            "Engins de TP - Articulation de pelle (Huile standard ISO VG 46 - Course max 600 mm)",
            "Tracteurs Agricoles - Relevage lourd (Huile épaisse ISO VG 68 - Course max 1000 mm)"
        ],
        key="select_huile_vde_tab4_secured"
    )
    
    pas_base = 0.06 if "Automobile" in huile_vde else (0.035 if "Engins de TP" in huile_vde else 0.018)
    course_max_reelle_mm_vde = 300.0 if "Automobile" in huile_vde else (600.0 if "Engins de TP" in huile_vde else 1000.0)
    vde_bloque = (st.session_state.vde_mouvement != "ARRET")

    col_vde_graph, col_vde_bd = st.columns([0.55, 0.45])
    with col_vde_graph:
        c_btn_de1, c_btn_de2 = st.columns(2)
        with c_btn_de1:
            if st.button("ALIMENTER EN A (SORTIE DU DOUBLE EFFET)", key="btn_out_vde_t4", use_container_width=True, disabled=vde_bloque or st.session_state.pos_vde_hyd >= 1.0):
                st.session_state.vde_mouvement = "SORTIE"
                st.session_state.temps_debut_vde = time.time()
                st.rerun()
        with c_btn_de2:
            if st.button("ALIMENTER EN B (RENTRÉE DU DOUBLE EFFET)", key="btn_in_vde_t4", use_container_width=True, disabled=vde_bloque or st.session_state.pos_vde_hyd <= 0.0):
                st.session_state.vde_mouvement = "RENTREE"
                st.session_state.temps_debut_vde = time.time()
                st.rerun()

        # Coupe mécanique
        fig_de, ax_de = plt.subplots(figsize=(6, 2.6), facecolor="white")
        ax_de.set_facecolor("white")
        ax_de.add_patch(patches.Rectangle((0.5, 1.0), 3.0, 1.4, facecolor="#f1f5f9", edgecolor="#475569", linewidth=2.5, zorder=1))
        ax_de.plot([3.5, 3.5], [1.0, 2.4], color="#334155", linewidth=3, zorder=2)
        ax_de.plot([0.9, 0.9], [0.4, 1.0], color="#334155", linewidth=2.5, zorder=2)
        ax_de.plot([3.1, 3.1], [0.4, 1.0], color="#334155", linewidth=2.5, zorder=2)
        
        course_vde_pixels = st.session_state.pos_vde_hyd * 2.6
        x_piston_de = 0.6 + course_vde_pixels
        color_ch_arriere = "#b91c1c" if st.session_state.vde_mouvement == "SORTIE" else ("#0284c7" if st.session_state.vde_mouvement == "RENTREE" else "#eab308")
        color_ch_avant = "#0284c7" if st.session_state.vde_mouvement == "SORTIE" else ("#b91c1c" if st.session_state.vde_mouvement == "RENTREE" else "#eab308")
        
        if x_piston_de > 0.62: ax_de.add_patch(patches.Rectangle((0.52, 1.03), x_piston_de - 0.52, 1.34, facecolor=color_ch_arriere, alpha=0.5, zorder=1))
        if x_piston_de + 0.3 < 3.48: ax_de.add_patch(patches.Rectangle((x_piston_de + 0.3, 1.03), 3.48 - (x_piston_de + 0.3), 1.34, facecolor=color_ch_avant, alpha=0.5, zorder=1))
        ax_de.add_patch(patches.Rectangle((x_piston_de, 1.03), 0.3, 1.34, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
        ax_de.add_patch(patches.Rectangle((x_piston_de + 0.3, 1.45), 3.5, 0.4, facecolor="#94a3b8", edgecolor="#334155", linewidth=1.5, zorder=2))
        ax_de.set_xlim(0, 8.5)
        ax_de.set_ylim(-0.2, 3.2)
        ax_de.axis("off")
        st.pyplot(fig_de)
        plt.close(fig_de)

        # Schéma ISO Animé avec flèches internes 4/2
        st.write("**Schéma d'implantation industrielle normalisé (ISO 1219) :**")
        fig_iso4, ax_iso4 = plt.subplots(figsize=(6, 2.2), facecolor="white")
        ax_iso4.set_facecolor("white")
        
        ax_iso4.add_patch(patches.Circle((2.0, 0.3), 0.2, facecolor="none", edgecolor="black", linewidth=2))
        ax_iso4.plot([2.0, 1.9, 2.1, 2.0], [0.4, 0.48, 0.48, 0.4], color="black", linewidth=2)
        ax_iso4.plot([2.8, 2.8, 3.2, 3.2], [0.3, 0.0, 0.0, 0.3], color="black", linewidth=2)
        
        # Boîtiers distributeur 4/2
        ax_iso4.add_patch(patches.Rectangle((1.5, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
        ax_iso4.add_patch(patches.Rectangle((2.3, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
        
        if st.session_state.vde_mouvement == "SORTIE":
            ax_iso4.arrow(2.5, 0.75, 0, 0.5, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso4.arrow(2.9, 1.35, 0, -0.5, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso4.plot([1.7, 2.1], [0.75, 1.35], color="#64748b", linewidth=1)
            ax_iso4.plot([2.1, 1.7], [0.75, 1.35], color="#64748b", linewidth=1)
        elif st.session_state.vde_mouvement == "RENTREE":
            ax_iso4.arrow(1.7, 0.75, 0.4, 0.55, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso4.arrow(1.7, 1.35, 0.4, -0.55, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso4.plot([2.5, 2.5], [0.75, 1.35], color="#64748b", linewidth=1)
            ax_iso4.plot([2.9, 2.9], [0.75, 1.35], color="#64748b", linewidth=1)
        else:
            ax_iso4.plot([1.7, 2.1], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso4.plot([2.1, 1.7], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso4.plot([2.5, 2.5], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso4.plot([2.9, 2.9], [0.75, 1.35], color="#64748b", linewidth=1.2)

        ax_iso4.plot([1.5, 1.3], [1.05, 1.35], color="black", linewidth=2.5, zorder=4)
        ax_iso4.add_patch(patches.Circle((1.3, 1.35), 0.05, facecolor="#b91c1c", edgecolor="black", zorder=5))
        
        c_ligne_A = "#b91c1c" if st.session_state.vde_mouvement == "SORTIE" else "#0284c7"
        c_ligne_B = "#0284c7" if st.session_state.vde_mouvement == "SORTIE" else "#b91c1c"
        if st.session_state.vde_mouvement == "ARRET": c_ligne_A, c_ligne_B = "#eab308", "#eab308"
            
        ax_iso4.plot([2.0, 2.0], [0.5, 0.7], color="#b91c1c", linewidth=2.5)
        ax_iso4.plot([3.0, 3.0], [0.3, 0.7], color="#0284c7", linewidth=2.5)
        ax_iso4.plot([1.8, 1.8, 3.6, 3.6], [1.4, 1.6, 1.6, 1.8], color=c_ligne_A, linewidth=2.5)
        ax_iso4.plot([2.8, 2.8, 5.0, 5.0], [1.4, 1.5, 1.5, 1.8], color=c_ligne_B, linewidth=2.5)
        
        ax_iso4.add_patch(patches.Rectangle((3.5, 1.8), 2.0, 0.5, facecolor="none", edgecolor="black", linewidth=2))
        x_p_s4 = 3.6 + (st.session_state.pos_vde_hyd * 1.6)
        ax_iso4.plot([x_p_s4, x_p_s4], [1.8, 2.3], color="black", linewidth=2.5)
        ax_iso4.plot([x_p_s4, 6.2], [2.05, 2.05], color="black", linewidth=2.5)
        
        f_poussee_kn = 57.3 if st.session_state.vde_mouvement == "SORTIE" else (0.0 if st.session_state.vde_mouvement == "ARRET" else 38.2)
        ax_iso4.text(4.5, 2.45, f"Force active : {f_poussee_kn:.1f} kN", color="black", weight="bold", fontsize=9, ha="center")
        ax_iso4.set_xlim(0.5, 6.5)
        ax_iso4.set_ylim(-0.1, 2.7)
        ax_iso4.axis("off")
        st.pyplot(fig_iso4)
        plt.close(fig_iso4)

    with col_vde_bd:
        st.write("**La BD humoristique textuelle : Le sprint des deux chambres**")
        st.info("**Case 1 :** Un énorme vérin double effet attend sur un tracteur.\n\n**Case 2 :** L'huile entre à l'arrière, la sortie est lourde.\n\n**Case 3 :** Changement de voie ! Le volume avant étant réduit par la tige, l'huile remplit l'espace en un éclair.\n\n**Case 4 :** Rentrée ultra-rapide ! Les molécules rigolent : 'Moins de place égale retour express !'.")

    # MOTEUR REFRESH VDE
    longueur_sortie_mm_vde = st.session_state.pos_vde_hyd * course_max_reelle_mm_vde
    if st.session_state.vde_mouvement != "ARRET":
        st.session_state.temps_course_vde = time.time() - st.session_state.temps_debut_vde
        if st.session_state.vde_mouvement == "SORTIE":
            st.session_state.pos_vde_hyd = min(1.0, st.session_state.pos_vde_hyd + pas_base)
            if st.session_state.pos_vde_hyd >= 1.0: st.session_state.vde_mouvement = "ARRET"
        elif st.session_state.vde_mouvement == "RENTREE":
            st.session_state.pos_vde_hyd = max(0.0, st.session_state.pos_vde_hyd - (pas_base * 1.65))
            if st.session_state.pos_vde_hyd <= 0.0: st.session_state.vde_mouvement = "ARRET"
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Chronomètre Double Effet", f"{st.session_state.temps_course_vde:.2f} s", f"Course : {st.session_state.pos_vde_hyd * 100:.0f} %")
        c_m2.metric("Longueur de sortie", f"{longueur_sortie_mm_vde:.1f} mm", "En déplacement")
        time.sleep(0.04)
        st.rerun()
    else:
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Temps de course mesuré", f"{st.session_state.temps_course_vde:.2f} s", "Immobile")
        c_m2.metric("Longueur de sortie", f"{longueur_sortie_mm_vde:.1f} mm", "Position verrouillée", delta_color="off")

    st.divider()
    afficher_atelier_verin_double_effet_hydraulique(verrouille=vde_bloque)

    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    case_certif_stat4 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 4.", key="check_certif_hydro4_final_net", disabled=vde_bloque)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_hydro_official", use_container_width=True, disabled=vde_bloque):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q4 += 1.0

            score_t4 = 0.0
            if "champs_hydro4_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro4_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_hydro4_clean", "Choisir...") == attendu: score_t4 += 1.0

            st.session_state.score_suite4_hydro_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_hydro_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_arch = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ ---
    if st.session_state.get("suite_verrouille_tab4_hydro", False):
        scr1_t4 = st.session_state.get("score_suite4_hydro_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_hydro_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_arch", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER VÉRIN DOUBLE EFFET SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_hydro4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vérin Double Effet - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #7c3aed; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #7c3aed; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 4 : Différences structurelles, pilotage et frottements visqueux du vérin double effet</p>
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
        if "ordre_quiz_tab4_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hydro4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 2. Injection des lignes de correction du texte à trous de l'Atelier 4
        if "champs_hydro4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro4_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 3. Fermeture définitive du document HTML de l'Atelier 4
        html_export_hydro4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro4 = preparer_nom_fichier("Rapport_Verin_Double_Effet").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_hydro4,
            file_name=nom_fichier_html_hydro4,
            mime="text/html",
            use_container_width=True
        )


with tab5:
    st.header("Vérins rotatifs et autres actionneurs")
    
    # --- SECTION COURS : LES ACTIONNEURS ROTATIFS ---
    st.subheader("Le principe de la transformation de mouvement à crémaillère")
    st.write(
        "Certaines applications industrielles exigent un mouvement de rotation mais sur un angle limité, "
        "avec un couple de torsion extrêmement élevé (par exemple pour faire pivoter le bras d'une pelleteuse, "
        "retourner une charrue agricole ou manipuler des vannes de gros diamètre).\n\n"
        "Pour y parvenir, on utilise un **vérin rotatif hydraulique**. Son fonctionnement interne repose sur un mécanisme "
        "à pignon-crémaillère : le corps de la machine abrite un vérin double effet linéaire dont la tige est taillée "
        "avec des crans (la crémaillère). Lorsque l'huile pousse le piston, la crémaillère translate et engrène un "
        "**pignon central**. Ce pignon transforme instantanément la force linéaire en un couple de rotation rigide "
        "et ultra-précis, généralement sur une plage de **0 à 180 degrés**."
    )
    
    st.divider()
    
    if "pos_rot_hyd" not in st.session_state: st.session_state.pos_rot_hyd = 0.0
    if "rot_mouvement" not in st.session_state: st.session_state.rot_mouvement = "ARRET"
    if "temps_debut_rot" not in st.session_state: st.session_state.temps_debut_rot = 0.0
    if "temps_course_rot" not in st.session_state: st.session_state.temps_course_rot = 0.0

    huile_rot = st.selectbox(
        "Sélectionner l'application et le type de fluide (Actionneur Rotatif) :",
        options=["Automobile - Direction de camion", "Engins de TP - Tourelle", "Agriculture - Relevage"],
        key="select_huile_rot_tab5_secured"
    )
    
    pas_base_rot = 0.06 if "Automobile" in huile_rot else (0.018 if "Agriculture" in huile_rot else 0.035)
    rot_bloque = (st.session_state.rot_mouvement != "ARRET")

    col_rot_graph, col_rot_bd = st.columns([0.55, 0.45])
    with col_rot_graph:
        c_btn_r1, c_btn_r2 = st.columns(2)
        with c_btn_r1:
            if st.button("ALIMENTER EN A (ROTATION HORAIRE)", key="btn_out_rot_t5", use_container_width=True, disabled=rot_bloque or st.session_state.pos_rot_hyd >= 1.0):
                st.session_state.rot_mouvement = "HORAIRE"
                st.session_state.temps_debut_rot = time.time()
                st.rerun()
        with c_btn_r2:
            if st.button("ALIMENTER EN B (ROTATION ANTI-HORAIRE)", key="btn_in_rot_t5", use_container_width=True, disabled=rot_bloque or st.session_state.pos_rot_hyd <= 0.0):
                st.session_state.rot_mouvement = "ANTI_HORAIRE"
                st.session_state.temps_debut_rot = time.time()
                st.rerun()

        # Coupe mécanique
        fig_rot, ax_rot = plt.subplots(figsize=(6, 2.6), facecolor="white")
        ax_rot.set_facecolor("white")
        ax_rot.add_patch(patches.Rectangle((0.5, 0.4), 3.0, 0.8, facecolor="#f1f5f9", edgecolor="#475569", linewidth=2.5, zorder=1))
        ax_rot.plot([0.8, 0.8], [0.0, 0.4], color="#334155", linewidth=2.5, zorder=2)
        ax_rot.plot([3.2, 3.2], [0.0, 0.4], color="#334155", linewidth=2.5, zorder=2)
        
        x_piston_rot = 0.6 + st.session_state.pos_rot_hyd * 2.0
        color_f_a = "#b91c1c" if st.session_state.rot_mouvement == "HORAIRE" else ("#0284c7" if st.session_state.rot_mouvement == "ANTI_HORAIRE" else "#eab308")
        color_f_b = "#0284c7" if st.session_state.rot_mouvement == "HORAIRE" else ("#b91c1c" if st.session_state.rot_mouvement == "ANTI_HORAIRE" else "#eab308")
        
        if x_piston_rot > 0.62: ax_rot.add_patch(patches.Rectangle((0.52, 0.43), x_piston_rot - 0.52, 0.74, facecolor=color_f_a, alpha=0.5, zorder=1))
        if x_piston_rot + 0.3 < 3.48: ax_rot.add_patch(patches.Rectangle((x_piston_rot + 0.3, 0.43), 3.48 - (x_piston_rot + 0.3), 0.74, facecolor=color_f_b, alpha=0.5, zorder=1))
        ax_rot.add_patch(patches.Rectangle((x_piston_rot, 0.43), 0.3, 0.74, facecolor="#1e293b", zorder=3))
        ax_rot.add_patch(patches.Rectangle((x_piston_rot + 0.3, 0.8), 2.0, 0.3, facecolor="#94a3b8", zorder=2))
        
        angle_actuel_deg = st.session_state.pos_rot_hyd * 180.0
        angle_rad_rot = np.radians(angle_actuel_deg)
        ax_rot.add_patch(patches.Circle((2.0, 1.8), 0.45, facecolor="#64748b", edgecolor="black", linewidth=2, zorder=2))
        ax_rot.plot([2.0, 2.0 + 0.4 * np.sin(angle_rad_rot)], [1.8, 1.8 - 0.4 * np.cos(angle_rad_rot)], color="white", linewidth=3, zorder=4)
        ax_rot.set_xlim(0, 5)
        ax_rot.set_ylim(-0.1, 2.6)
        ax_rot.axis("off")
        st.pyplot(fig_rot)
        plt.close(fig_rot)

        # Schéma ISO Animé avec flèches internes 4/2
        st.write("**Schéma d'implantation industrielle normalisé (ISO 1219) :**")
        fig_iso5, ax_iso5 = plt.subplots(figsize=(6, 2.2), facecolor="white")
        ax_iso5.set_facecolor("white")
        
        ax_iso5.add_patch(patches.Circle((2.0, 0.3), 0.2, facecolor="none", edgecolor="black", linewidth=2))
        ax_iso5.plot([2.0, 1.9, 2.1, 2.0], [0.4, 0.48, 0.48, 0.4], color="black", linewidth=2)
        ax_iso5.plot([2.8, 2.8, 3.2, 3.2], [0.3, 0.0, 0.0, 0.3], color="black", linewidth=2)
        
        ax_iso5.add_patch(patches.Rectangle((1.5, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
        ax_iso5.add_patch(patches.Rectangle((2.3, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
        
        if st.session_state.rot_mouvement == "HORAIRE":
            ax_iso5.arrow(2.5, 0.75, 0, 0.5, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso5.arrow(2.9, 1.35, 0, -0.5, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso5.plot([1.7, 2.1], [0.75, 1.35], color="#64748b", linewidth=1)
            ax_iso5.plot([2.1, 1.7], [0.75, 1.35], color="#64748b", linewidth=1)
        elif st.session_state.rot_mouvement == "ANTI_HORAIRE":
            ax_iso5.arrow(1.7, 0.75, 0.4, 0.55, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso5.arrow(1.7, 1.35, 0.4, -0.55, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso5.plot([2.5, 2.5], [0.75, 1.35], color="#64748b", linewidth=1)
            ax_iso5.plot([2.9, 2.9], [0.75, 1.35], color="#64748b", linewidth=1)
        else:
            ax_iso5.plot([1.7, 2.1], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso5.plot([2.1, 1.7], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso5.plot([2.5, 2.5], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso5.plot([2.9, 2.9], [0.75, 1.35], color="#64748b", linewidth=1.2)

        ax_iso5.plot([1.5, 1.3], [1.05, 1.35], color="black", linewidth=2.5, zorder=4)
        ax_iso5.add_patch(patches.Circle((1.3, 1.35), 0.05, facecolor="#b91c1c", edgecolor="black", zorder=5))
        
        c_rot_A = "#b91c1c" if st.session_state.rot_mouvement == "HORAIRE" else "#0284c7"
        c_rot_B = "#0284c7" if st.session_state.rot_mouvement == "HORAIRE" else "#b91c1c"
        if st.session_state.rot_mouvement == "ARRET": c_rot_A, c_rot_B = "#eab308", "#eab308"
            
        ax_iso5.plot([2.0, 2.0], [0.5, 0.7], color="#b91c1c", linewidth=2.5)
        ax_iso5.plot([3.0, 3.0], [0.3, 0.7], color="#0284c7", linewidth=2.5)
        ax_iso5.plot([1.8, 1.8, 4.1], [1.4, 1.6, 1.6], color=c_rot_A, linewidth=2.5)
        ax_iso5.plot([2.8, 2.8, 4.9], [1.4, 1.5, 1.5], color=c_rot_B, linewidth=2.5)
        
        ax_iso5.add_patch(patches.Circle((4.5, 1.6), 0.4, facecolor="none", edgecolor="black", linewidth=2))
        ax_iso5.plot([4.1, 4.1], [1.6, 1.3], color=c_rot_A, linewidth=2.5)
        ax_iso5.plot([4.9, 4.9], [1.5, 1.3], color=c_rot_B, linewidth=2.5)
        
        angle_symb = -35 + (st.session_state.pos_rot_hyd * 70)
        ax_iso5.add_patch(patches.Arc((4.5, 1.6), 0.55, 0.55, angle=0, theta1=angle_symb, theta2=angle_symb + 80, color="black", linewidth=2))
        ax_iso5.add_patch(patches.RegularPolygon((4.5, 1.8), numVertices=3, radius=0.06, orientation=np.radians(180), facecolor="black"))
        
        ax_iso5.set_xlim(0.5, 6.5)
        ax_iso5.set_ylim(-0.1, 2.5)
        ax_iso5.axis("off")
        st.pyplot(fig_iso5)
        plt.close(fig_iso5)

    with col_rot_bd:
        st.write("**La BD humoristique textuelle : Le bras fort**")
        st.info("Pignon-crémaillère : la translation fait pivoter l'axe central sans jeu hydrostatique.")

    # REFRESH CONTINU ROTATIF
    if st.session_state.rot_mouvement != "ARRET":
        st.session_state.temps_course_rot = time.time() - st.session_state.temps_debut_rot
        if st.session_state.rot_mouvement == "HORAIRE":
            st.session_state.pos_rot_hyd = min(1.0, st.session_state.pos_rot_hyd + pas_base_rot)
            if st.session_state.pos_rot_hyd >= 1.0: st.session_state.rot_mouvement = "ARRET"
        elif st.session_state.rot_mouvement == "ANTI_HORAIRE":
            st.session_state.pos_rot_hyd = max(0.0, st.session_state.pos_rot_hyd - pas_base_rot)
            if st.session_state.pos_rot_hyd <= 0.0: st.session_state.rot_mouvement = "ARRET"
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Chronomètre Rotatif", f"{st.session_state.temps_course_rot:.2f} s", f"Pivot : {st.session_state.pos_rot_hyd * 100:.0f} %")
        c_m2.metric("Angle de sortie", f"{angle_actuel_deg:.1f} °", "En rotation")
        time.sleep(0.04)
        st.rerun()
    else:
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Temps mesuré", f"{st.session_state.temps_course_rot:.2f} s", "Immobile")
        c_m2.metric("Angle de sortie", f"{angle_actuel_deg:.1f} °", "Position verrouillée", delta_color="off")

    st.divider()
    afficher_atelier_actionneurs_rotatifs(verrouille=rot_bloque)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    case_certif_stat5 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 5.", key="check_certif_hydro5_final_net", disabled=rot_bloque)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_hydro_official", use_container_width=True, disabled=rot_bloque):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q5 += 1.0

            score_t5 = 0.0
            if "champs_hydro5_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro5_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_hydro5_clean", "Choisir...") == attendu: score_t5 += 1.0

            st.session_state.score_suite5_hydro_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_hydro_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_hydro = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab5_hydro", False):
        scr1_t5 = st.session_state.get("score_suite5_hydro_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_hydro_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_hydro", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER ACTIONNEURS ROTATIFS SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        html_export_hydro5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Actionneurs Rotatifs - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #047857; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #047857; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 5 : Transformation cinématique pignon-crémaillère, couple de torsion et symbolisation ISO rotative</p>
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
        if "ordre_quiz_tab5_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hydro5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "champs_hydro5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro5_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro5_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_hydro5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro5 = preparer_nom_fichier("Rapport_Actionneurs_Rotatifs").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_hydro5,
            file_name=nom_fichier_html_hydro5,
            mime="text/html",
            use_container_width=True
        )


with tab6:
    st.header("Application 1 : Presse de compactage industrielle")
    
    st.subheader("Mise en situation et cahier des charges")
    st.write(
        "Dans un centre de recyclage de métaux, une presse hydraulique verticale doit broyer et compacter "
        "des carrosseries de voitures pour en faire des cubes de ferraille denses. "
        "Pour écraser l'acier, le système requiert un effort de poussée supérieur à **500 000 Newtons**.\n\n"
        "L'installation comprend une motopompe mécanique qui aspire l'huile du réservoir et l'envoie sous une "
        "pression de **250 bars** vers un distributeur 4/2. Le fluide incompressible pénètre dans la grande chambre "
        "du vérin de compactage. Un limiteur de pression taré sécurise le circuit contre l'éclatement."
    )
    
    st.divider()
    
    # --- INITIALISATION DES VARIABLES DE SESSION POUR L'APPLICATION 1 ---
    if "ap1_ecrase" not in st.session_state: st.session_state.ap1_ecrase = False
    if "pos_ap1_hyd" not in st.session_state: st.session_state.pos_ap1_hyd = 0.0
    if "ap1_mouvement" not in st.session_state: st.session_state.ap1_mouvement = "ARRET"
    if "temps_debut_ap1" not in st.session_state: st.session_state.temps_debut_ap1 = 0.0
    if "temps_course_ap1" not in st.session_state: st.session_state.temps_course_ap1 = 0.0

    ap1_bloque = (st.session_state.ap1_mouvement != "ARRET")
    col_ap1_graph, col_ap1_bd = st.columns([0.55, 0.45])
    
    with col_ap1_graph:
        c_btn_ap1_1, c_btn_ap1_2 = st.columns(2)
        with c_btn_ap1_1:
            if st.button("ALIMENTER LA PRESSE (COMPACTAGE)", key="btn_run_ap1_out", use_container_width=True, disabled=ap1_bloque or st.session_state.pos_ap1_hyd >= 1.0):
                st.session_state.ap1_mouvement = "SORTIE"
                st.session_state.temps_debut_ap1 = time.time()
                st.rerun()
        with c_btn_ap1_2:
            if st.button("RELEVER LE COMPACTEUR", key="btn_run_ap1_in", use_container_width=True, disabled=ap1_bloque or st.session_state.pos_ap1_hyd <= 0.0):
                st.session_state.ap1_mouvement = "RENTREE"
                st.session_state.temps_debut_ap1 = time.time()
                st.rerun()

        if st.session_state.pos_ap1_hyd >= 0.95: st.session_state.ap1_ecrase = True
        if st.session_state.pos_ap1_hyd <= 0.02: st.session_state.ap1_ecrase = False

        # Coupe mécanique
        fig_ap1, ax_ap1 = plt.subplots(figsize=(6, 2.8), facecolor="white")
        ax_ap1.set_facecolor("white")
        ax_ap1.plot([0.5, 4.5], [0.1, 0.1], color="#0f172a", linewidth=4, zorder=2)
        ax_ap1.add_patch(patches.Rectangle((1.5, 1.2), 2.0, 1.6, facecolor="#f1f5f9", edgecolor="#475569", linewidth=2.5, zorder=1))
        ax_ap1.plot([1.5, 3.5], [1.2, 1.2], color="#334155", linewidth=3.5, zorder=3)
        
        course_verticale = st.session_state.pos_ap1_hyd * 0.6
        y_piston_ap1 = 2.4 - course_verticale
        color_sup = "#b91c1c" if st.session_state.ap1_mouvement == "SORTIE" else ("#0284c7" if st.session_state.ap1_mouvement == "RENTREE" else "#eab308")
        color_inf = "#0284c7" if st.session_state.ap1_mouvement == "SORTIE" else ("#b91c1c" if st.session_state.ap1_mouvement == "RENTREE" else "#eab308")
        
        if y_piston_ap1 < 2.4: ax_ap1.add_patch(patches.Rectangle((1.52, y_piston_ap1 + 0.25), 1.96, 2.78 - (y_piston_ap1 + 0.25), facecolor=color_sup, alpha=0.5, zorder=1))
        if y_piston_ap1 > 1.22: ax_ap1.add_patch(patches.Rectangle((1.52, 1.22), 1.96, y_piston_ap1 - 1.22, facecolor=color_inf, alpha=0.5, zorder=1))
        
        ax_ap1.add_patch(patches.Rectangle((1.52, y_piston_ap1), 1.96, 0.25, facecolor="#1e293b", edgecolor="black", zorder=3))
        y_bas_tige = y_piston_ap1 - 1.5
        ax_ap1.add_patch(patches.Rectangle((2.2, y_bas_tige), 0.6, 1.5, facecolor="#94a3b8", edgecolor="#334155", linewidth=1.5, zorder=2))
        
        hauteur_rendu_voiture = 0.2 if st.session_state.ap1_ecrase else max(0.2, y_bas_tige - 0.1)
        ax_ap1.add_patch(patches.Rectangle((1.7, 0.1), 1.6, hauteur_rendu_voiture, facecolor="#7f1d1d", edgecolor="black", zorder=3))
        ax_ap1.set_xlim(0, 5)
        ax_ap1.set_ylim(-0.1, 3.2)
        ax_ap1.axis("off")
        st.pyplot(fig_ap1)
        plt.close(fig_ap1)

        # Schéma ISO Animé avec flèches internes 4/2
        st.write("**Schéma d'implantation industrielle normalisé (ISO 1219) :**")
        fig_iso6, ax_iso6 = plt.subplots(figsize=(6, 2.2), facecolor="white")
        ax_iso6.set_facecolor("white")
        
        ax_iso6.add_patch(patches.Circle((2.0, 0.3), 0.2, facecolor="none", edgecolor="black", linewidth=2))
        ax_iso6.plot([2.0, 1.9, 2.1, 2.0], [0.4, 0.48, 0.48, 0.4], color="black", linewidth=2)
        ax_iso6.plot([2.8, 2.8, 3.2, 3.2], [0.3, 0.0, 0.0, 0.3], color="black", linewidth=2)
        
        ax_iso6.add_patch(patches.Rectangle((1.5, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
        ax_iso6.add_patch(patches.Rectangle((2.3, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5, zorder=3))
        
        if st.session_state.ap1_mouvement == "SORTIE":
            ax_iso6.arrow(2.5, 0.75, 0, 0.5, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso6.arrow(2.9, 1.35, 0, -0.5, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso6.plot([1.7, 2.1], [0.75, 1.35], color="#64748b", linewidth=1)
            ax_iso6.plot([2.1, 1.7], [0.75, 1.35], color="#64748b", linewidth=1)
        elif st.session_state.ap1_mouvement == "RENTREE":
            ax_iso6.arrow(1.7, 0.75, 0.4, 0.55, head_width=0.06, head_length=0.08, fc="#b91c1c", ec="#b91c1c", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso6.arrow(1.7, 1.35, 0.4, -0.55, head_width=0.06, head_length=0.08, fc="#0284c7", ec="#0284c7", linewidth=2, length_includes_head=True, zorder=4)
            ax_iso6.plot([2.5, 2.5], [0.75, 1.35], color="#64748b", linewidth=1)
            ax_iso6.plot([2.9, 2.9], [0.75, 1.35], color="#64748b", linewidth=1)
        else:
            ax_iso6.plot([1.7, 2.1], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso6.plot([2.1, 1.7], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso6.plot([2.5, 2.5], [0.75, 1.35], color="#64748b", linewidth=1.2)
            ax_iso6.plot([2.9, 2.9], [0.75, 1.35], color="#64748b", linewidth=1.2)

        ax_iso6.plot([1.5, 1.3], [1.05, 1.35], color="black", linewidth=2.5, zorder=4)
        ax_iso6.add_patch(patches.Circle((1.3, 1.35), 0.05, facecolor="#b91c1c", edgecolor="black", zorder=5))
        
        c_presse_A = "#b91c1c" if st.session_state.ap1_mouvement == "SORTIE" else "#0284c7"
        c_presse_B = "#0284c7" if st.session_state.ap1_mouvement == "SORTIE" else "#b91c1c"
        if st.session_state.ap1_mouvement == "ARRET": c_presse_A, c_presse_B = "#eab308", "#eab308"
            
        ax_iso6.plot([2.0, 2.0], [0.5, 0.7], color="#b91c1c", linewidth=2.5)
        ax_iso6.plot([3.0, 3.0], [0.3, 0.7], color="#0284c7", linewidth=2.5)
        ax_iso6.plot([1.8, 1.8, 3.6, 3.6], [1.4, 1.6, 1.6, 1.8], color=c_presse_A, linewidth=2.5)
        ax_iso6.plot([2.8, 2.8, 5.0, 5.0], [1.4, 1.5, 1.5, 1.8], color=c_presse_B, linewidth=2.5)
        
        ax_iso6.add_patch(patches.Rectangle((3.5, 1.8), 2.0, 0.5, facecolor="none", edgecolor="black", linewidth=2))
        x_p_s6 = 3.6 + (st.session_state.pos_ap1_hyd * 1.6)
        ax_iso6.plot([x_p_s6, x_p_s6], [1.8, 2.3], color="black", linewidth=2.5)
        ax_iso6.plot([x_p_s6, 6.2], [2.05, 2.05], color="black", linewidth=2.5)
        
        f_presse_kn = 512.5 if st.session_state.ap1_mouvement == "SORTIE" else 0.0
        ax_iso6.text(4.5, 2.45, f"Force de compactage : {f_presse_kn:.1f} kN", color="black", weight="bold", fontsize=9, ha="center")
        ax_iso6.set_xlim(0.5, 6.5)
        ax_iso6.set_ylim(-0.1, 2.7)
        ax_iso6.axis("off")
        st.pyplot(fig_iso6)
        plt.close(fig_iso6)

    with col_ap1_bd:
        st.write("**La BD humoristique textuelle : La déformation plastique**")
        st.info("Presse verticale : l'acier s'écrase définitivement sous l'incompressibilité du fluide.")

    # MOTEUR CHRONO AP1
    longueur_sortie_mm_ap1 = st.session_state.pos_ap1_hyd * 500.0
    if st.session_state.ap1_mouvement != "ARRET":
        st.session_state.temps_course_ap1 = time.time() - st.session_state.temps_debut_ap1
        if st.session_state.ap1_mouvement == "SORTIE":
            st.session_state.pos_ap1_hyd = min(1.0, st.session_state.pos_ap1_hyd + 0.04)
            if st.session_state.pos_ap1_hyd >= 1.0: st.session_state.ap1_mouvement = "ARRET"
        elif st.session_state.ap1_mouvement == "RENTREE":
            st.session_state.pos_ap1_hyd = max(0.0, st.session_state.pos_ap1_hyd - 0.065)
            if st.session_state.pos_ap1_hyd <= 0.0: st.session_state.ap1_mouvement = "ARRET"
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Chronomètre Presse", f"{st.session_state.temps_course_ap1:.2f} s", f"Course : {st.session_state.pos_ap1_hyd * 100:.0f} %")
        c_m2.metric("Poinçon bas", f"{longueur_sortie_mm_ap1:.1f} mm", "En déplacement")
        time.sleep(0.04)
        st.rerun()
    else:
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("Temps de compactage", f"{st.session_state.temps_course_ap1:.2f} s", "Immobile")
        c_m2.metric("Poinçon bas", f"{longueur_sortie_mm_ap1:.1f} mm", "Verrouillé", delta_color="off")

    st.divider()
    afficher_atelier_application1(verrouille=ap1_bloque)

    # --- ENREGISTREMENT ET VERROUILLAGE DE L'ATELIER 6 ---
    if "suite_verrouille_tab6_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab6_hydro = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_hydro

    # UN UNIQUE APPEL ICI : L'affichage des deux colonnes (Quiz + Trous) est géré à l'intérieur
    afficher_atelier_application1(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 6.", 
        key="check_certif_hydro6_final_net", 
        disabled=verrou_at6
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_hydro_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (Lecture adaptative par préfixe d'instance)
            score_q6 = 0.0
            if "ordre_quiz_tab6_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_hydro_aleatoire:
                    saisie = "Choisir..."
                    prefixe_cherche = f"quiz_ap1_{q_item['id']}_"
                    for k_session in st.session_state.keys():
                        if k_session.startswith(prefixe_cherche):
                            saisie = st.session_state[k_session]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q6 += 1.0

            # B. Correction du Texte à trous (Synthèse de cours)
            score_t6 = 0.0
            if "champs_hydro6_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro6_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"{cle}_hydro6_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t6 += 1.0

            st.session_state.score_suite6_hydro_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_hydro_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_hydro = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ DE L'ATELIER 6 ---
    if st.session_state.get("suite_verrouille_tab6_hydro", False):
        scr1_t6 = st.session_state.get("score_suite6_hydro_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_hydro_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6_hydro", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 6 SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        html_export_hydro6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Presse Compactage - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 6 : Analyse d'une presse de compactage et puissance des fluides incompressibles</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e293b;">
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

        if "ordre_quiz_tab6_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_hydro_aleatoire, 1):
                # Alignement de la lecture de la table HTML sur la méthode de recherche par préfixe
                saisie = "Choisir..."
                prefixe_cherche = f"quiz_ap1_{q_item['id']}_"
                for k_session in st.session_state.keys():
                    if k_session.startswith(prefixe_cherche):
                        saisie = st.session_state[k_session]
                        break
                        
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hydro6 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_hydro6_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro6_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro6_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_hydro6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro6 = preparer_nom_fichier("Rapport_Presse_Compactage").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_hydro6,
            file_name=nom_fichier_html_hydro6,
            mime="text/html",
            use_container_width=True
        )


with tab7:
    st.header("Application 2 : Système de levage de camion-grue")
    
    st.subheader("Mise en situation et cahier des charges")
    st.write(
        "Sur un chantier de bâtiment, un camion-grue doit décharger des blocs de fondation en béton lourds. "
        "Le déploiement de la flèche télescopique articulée exige un maintien en position irréprochable. "
        "Tout glissement ou affaissement de la tige sous charge provoquerait la chute mortelle du bloc.\n\n"
        "Pour éliminer ce risque, le circuit hydraulique intègre un **clapet anti-retour piloté** directement "
        "vissé sur le nez du vérin. Même si un tuyau flexible d'alimentation se déchire accidentellement sous "
        "une pression de **200 bars**, le clapet se verrouille instantanément, emprisonnant l'huile dans la chambre "
        "et clouant le bras articulé en position de sécurité absolue."
    )
    
    st.divider()
    
    # --- INITIALISATION DES VARIABLES DE SESSION POUR L'APPLICATION 2 ---
    if "pos_ap2_hyd" not in st.session_state:
        st.session_state.pos_ap2_hyd = 0.0
    if "ap2_mouvement" not in st.session_state:
        st.session_state.ap2_mouvement = "ARRET"
    if "temps_debut_ap2" not in st.session_state:
        st.session_state.temps_debut_ap2 = 0.0
    if "temps_course_ap2" not in st.session_state:
        st.session_state.temps_course_ap2 = 0.0

    ap2_bloque = (st.session_state.ap2_mouvement != "ARRET")

    col_ap2_graph, col_ap2_bd = st.columns([0.55, 0.45])
    
    with col_ap2_graph:
        c_btn_ap2_1, c_btn_ap2_2 = st.columns(2)
        with c_btn_ap2_1:
            if st.button("ALIMENTER LA FLÈCHE (LEVAGE)", key="btn_run_ap2_out", use_container_width=True, disabled=ap2_bloque or st.session_state.pos_ap2_hyd >= 1.0):
                st.session_state.ap2_mouvement = "SORTIE"
                st.session_state.temps_debut_ap2 = time.time()
                st.rerun()
        with c_btn_ap2_2:
            if st.button("REVENIR AU REPOS (DESCENTE)", key="btn_run_ap2_in", use_container_width=True, disabled=ap2_bloque or st.session_state.pos_ap2_hyd <= 0.0):
                st.session_state.ap2_mouvement = "RENTREE"
                st.session_state.temps_debut_ap2 = time.time()
                st.rerun()

        # =============================================================================
        # 1. GRAPHIQUE SUPÉRIEUR : ANIMATION DE LA VUE EN COUPE DU SYSTÈME RÉEL
        # =============================================================================
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig_ap2, ax_ap2 = plt.subplots(figsize=(6.5, 4.0), facecolor="white")
        ax_ap2.set_facecolor("white")
        
        # 1. DESSIN DU CAMION PORTEUR
        # Châssis principal (gris foncé)
        ax_ap2.add_patch(patches.Rectangle((0.6, 0.6), 2.0, 0.4, facecolor="#334155", edgecolor="#1e293b", linewidth=1.5, zorder=2))
        # Cabine du chauffeur à l'avant (x=0.6 à x=1.1)
        ax_ap2.add_patch(patches.Rectangle((0.6, 1.0), 0.5, 0.5, facecolor="#0284c7", edgecolor="#0369a1", linewidth=1.5, zorder=2))
        # Vitre de la cabine
        ax_ap2.add_patch(patches.Rectangle((0.65, 1.15), 0.25, 0.25, facecolor="#e0f2fe", edgecolor="#0284c7", zorder=3))
        
        # Roues détaillées avec jantes argentées
        ax_ap2.add_patch(patches.Circle((0.9, 0.4), 0.22, facecolor="#1e293b", zorder=3))
        ax_ap2.add_patch(patches.Circle((0.9, 0.4), 0.10, facecolor="#cbd5e1", edgecolor="black", zorder=4))
        ax_ap2.add_patch(patches.Circle((2.1, 0.4), 0.22, facecolor="#1e293b", zorder=3))
        ax_ap2.add_patch(patches.Circle((2.1, 0.4), 0.10, facecolor="#cbd5e1", edgecolor="black", zorder=4))
        
        # Béquilles de stabilisation hydrauliques (Sécurité chantier au sol y=0.18)
        ax_ap2.add_patch(patches.Rectangle((1.3, 0.18), 0.12, 0.42, facecolor="#64748b", zorder=1))
        ax_ap2.add_patch(patches.Rectangle((1.15, 0.18), 0.42, 0.06, facecolor="#1e293b", zorder=2)) # Semelle au sol
        
        # 2. CALCUL CINÉMATIQUE DE LA FLÈCHE ARTICULÉE (Axe de rotation à x=2.3, y=1.0)
        angle_grue = 15.0 + (st.session_state.pos_ap2_hyd * 42.0)
        rad_grue = np.radians(angle_grue)
        
        # Dimensions de la flèche télescopique
        longueur_fleche = 3.5
        x_base_bras, y_base_bras = 2.3, 1.0
        x_bout_bras = x_base_bras + longueur_fleche * np.cos(rad_grue)
        y_bout_bras = y_base_bras + longueur_fleche * np.sin(rad_grue)
        
        # Dessin de la tourelle pivotante de base (Support bras)
        ax_ap2.add_patch(patches.Polygon([[2.1, 1.0], [2.5, 1.0], [2.4, 1.2], [2.2, 1.2]], facecolor="#475569", zorder=2))
        
        # Structure de la flèche télescopique (Ligne double de forte épaisseur industrielle)
        ax_ap2.plot([x_base_bras, x_bout_bras], [y_base_bras, y_bout_bras], color="#eab308", linewidth=8, solid_capstyle="round", zorder=3)
        ax_ap2.plot([x_base_bras, x_bout_bras], [y_base_bras, y_bout_bras], color="#ca8a04", linewidth=2, linestyle="--", zorder=4) # Ligne d'axe interne
        
        # Poulie de tête de flèche
        ax_ap2.add_patch(patches.Circle((x_bout_bras, y_bout_bras), 0.08, facecolor="#475569", zorder=5))
        
        # 3. VÉRIN HYDRAULIQUE RÉALISTE DE LEVAGE DE FLÈCHE
        # Point d'ancrage bas sur le châssis (x=1.6, y=1.0) et haut sur la flèche (45% de la longueur)
        x_attache_bas, y_attache_bas = 1.6, 1.0
        x_attache_haut = x_base_bras + (longueur_fleche * 0.42) * np.cos(rad_grue)
        y_attache_haut = y_base_bras + (longueur_fleche * 0.42) * np.sin(rad_grue)
        
        # Calcul du vecteur directeur du vérin
        dx_v, dy_v = x_attache_haut - x_attache_bas, y_attache_haut - y_attache_bas
        longueur_verin_courante = np.sqrt(dx_v**2 + dy_v**2)
        ux, uy = dx_v / longueur_verin_courante, dy_v / longueur_verin_courante
        
        # Corps de vérin (Plus épais, couleur bleu roi, prend 55% de la longueur max)
        longueur_corps = 0.8
        x_nez_corps = x_attache_bas + longueur_corps * ux
        y_nez_corps = y_attache_bas + longueur_corps * uy
        ax_ap2.plot([x_attache_bas, x_nez_corps], [y_attache_bas, y_nez_corps], color="#1d4ed8", linewidth=6, solid_capstyle="round", zorder=4)
        # Bague de tête de vérin noire (Nez de guidage)
        ax_ap2.plot([x_nez_corps - 0.02*ux, x_nez_corps + 0.02*ux], [y_nez_corps - 0.02*uy, y_nez_corps + 0.02*uy], color="black", linewidth=8, zorder=5)
        
        # Tige de vérin chromée de longueur fixe qui coulisse à l'intérieur
        ax_ap2.plot([x_nez_corps, x_attache_haut], [y_nez_corps, y_attache_haut], color="#cbd5e1", linewidth=3.5, zorder=3)        
        # 4. CÂBLE ET BLOC DE BÉTON LOURD SCELLÉ
        ax_ap2.plot([x_bout_bras, x_bout_bras], [y_bout_bras, y_bout_bras - 1.1], color="#1e293b", linewidth=1.5, zorder=2) # Câble de levage
        # Bloc de béton (Gris rectifié avec bordure noire)
        ax_ap2.add_patch(patches.Rectangle((x_bout_bras - 0.25, y_bout_bras - 1.5), 0.5, 0.4, facecolor="#94a3b8", edgecolor="#1e293b", linewidth=1.5, zorder=4))
        # Crochets de levage
        ax_ap2.plot([x_bout_bras, x_bout_bras], [y_bout_bras - 1.1, y_bout_bras - 1.15], color="black", linewidth=2.5, zorder=5)
        
        # Ajustement du champ de vision
        ax_ap2.set_xlim(0, 6.5)
        ax_ap2.set_ylim(0, 4.0)
        ax_ap2.axis("off")
        st.pyplot(fig_ap2)
        plt.close(fig_ap2)

        # =============================================================================
        # 2. GRAPHIQUE INFÉRIEUR : SCHÉMA NORMALISÉ ISO DESSINÉ EN DESSOUS
        # =============================================================================
        st.write("**Schéma de raccordement et sécurité hydrostatique (Norme ISO 1219) :**")
        fig_iso7, ax_iso7 = plt.subplots(figsize=(6, 2.4), facecolor="white")
        ax_iso7.set_facecolor("white")
        
        # Centrale hydraulique du camion (Pompe + Réservoir)
        ax_iso7.add_patch(patches.Circle((2.0, 0.3), 0.2, facecolor="none", edgecolor="black", linewidth=2)) # Pompe
        ax_iso7.plot([2.0, 1.9, 2.1, 2.0], [0.4, 0.48, 0.48, 0.4], color="black", linewidth=2) # Triangle HP
        ax_iso7.plot([2.8, 2.8, 3.2, 3.2], [0.3, 0.0, 0.0, 0.3], color="black", linewidth=2) # Tank (T)
        
        # Distributeur 4/2 de levage
        ax_iso7.add_patch(patches.Rectangle((1.5, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5))
        ax_iso7.add_patch(patches.Rectangle((2.3, 0.7), 0.8, 0.7, facecolor="none", edgecolor="black", linewidth=1.5))
        
        # Détermination dynamique des pressions sur les flexibles
        c_grue_A = "#b91c1c" if st.session_state.ap2_mouvement == "SORTIE" else "#0284c7"
        c_grue_B = "#0284c7" if st.session_state.ap2_mouvement == "SORTIE" else "#b91c1c"
        if st.session_state.ap2_mouvement == "ARRET":
            # Sécurité active : l'huile reste piégée sous pression ambrée au seuil du clapet
            c_grue_A, c_grue_B = "#eab308", "#eab308"
            
        # Tracé des conduites d'usine
        ax_iso7.plot([2.0, 2.0], [0.5, 0.7], color="#b91c1c", linewidth=2.5) # Ligne P
        ax_iso7.plot([3.0, 3.0], [0.3, 0.7], color="#0284c7", linewidth=2.5) # Ligne T
        
        # Canalisation de la Voie A transitant par le clapet de sécurité
        ax_iso7.plot([1.8, 1.8, 3.6, 3.6], [1.4, 1.6, 1.6, 1.8], color=c_grue_A, linewidth=2.5) 
        # Canalisation de la Voie B (Retour ou descente forcée)
        ax_iso7.plot([2.8, 2.8, 5.0, 5.0], [1.4, 1.5, 1.5, 1.8], color=c_grue_B, linewidth=2.5) 
        
        # --- DESSIN DU SYMBOLE DU CLAPET ANTI-RETOUR PILOTÉ ---
        # Carré de protection enveloppant le clapet à x=3.6, y=1.6
        ax_iso7.add_patch(patches.Rectangle((3.3, 1.45), 0.6, 0.3, facecolor="none", edgecolor="black", linewidth=1, linestyle="--"))
        # Bille de blocage et siège conique interne
        ax_iso7.add_patch(patches.Circle((3.6, 1.6), 0.05, facecolor="black", zorder=4))
        ax_iso7.plot([3.45, 3.6], [1.5, 1.6], color="black", linewidth=1.5) # Siège
        ax_iso7.plot([3.45, 3.6], [1.7, 1.6], color="black", linewidth=1.5) # Siège
        # Ligne de pilotage pointillée (interconnexion de sécurité croisée)
        ax_iso7.plot([3.6, 4.4], [1.45, 1.45], color="black", linewidth=1.2, linestyle=":")
        
        # Symbole du vérin de flèche linéaire double effet
        ax_iso7.add_patch(patches.Rectangle((3.5, 1.8), 2.0, 0.5, facecolor="none", edgecolor="black", linewidth=2))
        x_p_s7 = 3.6 + (st.session_state.pos_ap2_hyd * 1.6)
        ax_iso7.plot([x_p_s7, x_p_s7], [1.8, 2.3], color="black", linewidth=2.5) # Piston
        ax_iso7.plot([x_p_s7, 6.2], [2.05, 2.05], color="black", linewidth=2.5) # Tige
        
        # Affichage de l'état de sécurité
        txt_securite = "SÉCURITÉ : BLOCAGE HYDROSTATIQUE ACTIF" if st.session_state.ap2_mouvement == "ARRET" else "FLUIDE SOUS PRESSION DIRECTIONNELLE"
        color_txt = "#b45309" if "SÉCURITÉ" in txt_securite else "#1e293b"
        ax_iso7.text(4.5, 2.45, txt_securite, color=color_txt, weight="bold", fontsize=9, ha="center")
        
        ax_iso7.set_xlim(0.5, 6.5)
        ax_iso7.set_ylim(-0.1, 2.7)
        ax_iso7.axis("off")
        st.pyplot(fig_iso7)
        plt.close(fig_iso7)

    with col_ap2_bd:
        st.write("**La BD humoristique textuelle : Le cauchemar du contremaître**")
        st.info(
            "**Case 1 :** Un camion-grue déploie son bras télescopique au-dessus de la cabine de chantier : 'Attention dessous, je déplace un bloc de dix tonnes !'.\n\n"
            "**Case 2 :** Soudain, un grincement strident retentit. Le flexible haute pression frotte contre un angle vif et se déchire dans une immense gerbe d'huile ambrée : 'Pschhh !'. Le contremaître au sol lève les bras au ciel, paniqué.\n\n"
            "**Case 3 :** Au niveau du vérin, le petit clapet anti-retour de sécurité se referme instantanément comme une trappe de château-fort : 'Clac !'. Il bloque les molécules d'huile à double tour : 'Personne ne sort ! Tout le monde reste au poste !'.\n\n"
            "**Case 4 :** Le bras de la grue reste parfaitement immobile et figé en l'air, sauvant les structures. Le chauffeur descend de sa cabine en soupirant de soulagement : 'Heureusement que le clapet de blocage hydrostatique a fait son travail mécanique !'."
        )

    # --- SÉQUENCE CHRONOMÉTRIQUE DE LEVAGE PROFESSIONNEL ---
    # Course maximale réelle de levage = 600 mm
    longueur_sortie_mm_ap2 = st.session_state.pos_ap2_hyd * 600.0

    if st.session_state.ap2_mouvement != "ARRET":
        st.session_state.temps_course_ap2 = time.time() - st.session_state.temps_debut_ap2
        
        if st.session_state.ap2_mouvement == "SORTIE":
            st.session_state.pos_ap2_hyd = min(1.0, st.session_state.pos_ap2_hyd + pas_base)
            if st.session_state.pos_ap2_hyd >= 1.0:
                st.session_state.ap2_mouvement = "ARRET"
        elif st.session_state.ap2_mouvement == "RENTREE":
            st.session_state.pos_ap2_hyd = max(0.0, st.session_state.pos_ap2_hyd - (pas_base * 1.65)) # Rentrée asymétrique rapide
            if st.session_state.pos_ap2_hyd <= 0.0:
                st.session_state.ap2_mouvement = "ARRET"

        c_met_ap1, c_met_ap2 = st.columns(2)
        with c_met_ap1:
            st.metric(label="Chronomètre dynamique Flèche", value=f"{st.session_state.temps_course_ap2:.2f} s", delta=f"Levage : {st.session_state.pos_ap2_hyd * 100:.0f} %")
        with c_met_ap2:
            st.metric(label="Extension de la tige", value=f"{longueur_sortie_mm_ap2:.1f} mm", delta="En déplacement")
        
        time.sleep(0.04)
        st.rerun()
    else:
        c_met_ap1, c_met_ap2 = st.columns(2)
        with c_met_ap1:
            st.metric(label="Temps de course mesuré (Dernier essai)", value=f"{st.session_state.temps_course_ap2:.2f} s", delta=f"Flèche immobile à {st.session_state.pos_ap2_hyd * 100:.0f} %")
        with c_met_ap2:
            st.metric(label="Extension de la tige", value=f"{longueur_sortie_mm_ap2:.1f} mm", delta="Position de sécurité active", delta_color="off")

    st.divider()

    # --- ZONE DES EXERCICES DE L'ATELIER 7 ---
    afficher_atelier_application2(verrouille=ap2_bloque)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")
    case_certif_stat7 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 7.", key="check_certif_hydro7_final_net", disabled=ap2_bloque)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_suite7_hydro_official", use_container_width=True, disabled=ap2_bloque):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat7: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # A. Correction du Quiz Technique (Max 10 points)
            score_q7 = 0.0
            if "ordre_quiz_tab7_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab7_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at7_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q7 += 1.0

            # B. Correction du Texte à trous (Max 10 points)
            score_t7 = 0.0
            if "champs_hydro7_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro7_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"{cle}_hydro7_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t7 += 1.0

            # Sauvegarde des résultats et verrouillage de la session
            st.session_state.score_suite7_hydro_p1 = round(float(score_q7), 1)
            st.session_state.score_suite7_hydro_p2 = round(float(score_t7), 1)
            st.session_state.score_final_suite7_hydro = round(float(score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ DE L'ATELIER 7 ---
    if st.session_state.get("suite_verrouille_tab7_hydro", False):
        scr1_t7 = st.session_state.get("score_suite7_hydro_p1", 0.0)
        scr2_t7 = st.session_state.get("score_suite7_hydro_p2", 0.0)
        tot_s_t7 = st.session_state.get("score_final_suite7_hydro", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 7 SCELLÉ | Note de session : {tot_s_t7:.1f} / 20")

        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        html_export_hydro7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Camion-Grue - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e3a8a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 7 : Analyse des circuits de levage lourds et sécurité active par clapet piloté</p>
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

        if "ordre_quiz_tab7_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at7_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hydro7 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE D'ATELIER (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_hydro7_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro7_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro7_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_hydro7 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro7 = preparer_nom_fichier("Rapport_Camion_Grue").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 7 (.html)",
            data=html_export_hydro7,
            file_name=nom_fichier_html_hydro7,
            mime="text/html",
            use_container_width=True
        )




























