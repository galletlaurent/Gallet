
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application tension électrique",
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
st.title("Application  tension électrique")
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
    "Définition",
    "Appareil de mesure",
    "Tension dans les circuits en série",
    "Tension dans les circuits en dérivation",
    "Tension aux bornes d'une pile",
    "Transport d'énergie et lignes à très haute et haute tension"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]

def afficher_atelier_transport_tension(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Transport réseau) sur deux colonnes."""
    import random

    questions_transport_sources = [
        {"id": "qtr1", "q": "Comment appelle-t-on la déperdition d'énergie sous forme de chaleur dans un câble résistant ?", "options": ["L'effet Joule", "L'induction", "L'effet photovoltaïque"], "rep": "L'effet Joule"},
        {"id": "qtr2", "q": "Quelle formule mathématique régit les pertes par effet Joule dans une ligne ?", "options": ["P = R x I²", "P = U x I", "P = R x U"], "rep": "P = R x I²"},
        {"id": "qtr3", "q": "Pour réduire l'intensité en circulation sans baisser la puissance, on doit :", "options": ["Élever fortement la tension", "Abaisser la tension", "Ouvrir le circuit"], "rep": "Élever fortement la tension"},
        {"id": "qtr4", "q": "Quel appareil électrique modifie la valeur de la tension alternative du réseau ?", "options": ["Le transformateur", "L'alternateur", "Le rhéostat"], "rep": "Le transformateur"},
        {"id": "qtr5", "q": "En France, quelle est la valeur maximale de la Très Haute Tension (THT) sur le réseau ?", "options": ["400 000 Volts", "230 Volts", "20 000 Volts"], "rep": "400 000 Volts"},
        {"id": "qtr6", "q": "Quel gestionnaire gère le réseau des grandes lignes de transport haute tension en France ?", "options": ["RTE", "Enedis", "EDF"], "rep": "RTE"},
        {"id": "qtr7", "q": "Quel matériau compose majoritairement les câbles suspendus des lignes THT ?", "options": ["L'aluminium (allié à de l'acier)", "Le cuivre pur", "Le plomb"], "rep": "L'aluminium (allié à de l'acier)"},
        {"id": "qtr8", "q": "Où trouve-t-on les transformateurs abaisseurs de tension pour le réseau des habitations ?", "options": ["Dans les postes électriques de quartier", "À l'intérieur de la centrale", "Dans le disjoncteur de la maison"], "rep": "Dans les postes électriques de quartier"},
        {"id": "qtr9", "q": "Si l'intensité dans une ligne est divisée par 10, les pertes par effet Joule sont divisées par :", "options": ["100", "10", "2"], "rep": "100"},
        {"id": "qtr10", "q": "Comment qualifie-t-on le grand réseau d'interconnexion des lignes électriques ?", "options": ["Le réseau maillé", "Le réseau en série", "Le réseau passif"], "rep": "Le réseau maillé"}
    ]

    if "ordre_quiz_tab6_aleatoire" not in st.session_state:
        random.shuffle(questions_transport_sources)
        st.session_state.ordre_quiz_tab6_aleatoire = questions_transport_sources

    # Liste de synthèse (Énoncé, Choix, Réponse attendue, Clé session)
    if "champs_tr_tension" not in st.session_state:
        st.session_state.champs_tr_tension = [
            ("1. Le passage du courant fait chauffer les lignes par effet ..........", ["Choisir...", "Joule", "Faraday"], "Joule", "trans_t1_final"),
            ("2. Les pertes thermiques dépendent du carré de l'..........", ["Choisir...", "intensité", "tension"], "intensité", "trans_t2_final"),
            ("3. Augmenter la tension permet de réduire le débit d'..........", ["Choisir...", "électrons", "volts"], "électrons", "trans_t3_final"),
            ("4. À la sortie de la centrale, on trouve un transformateur ..........", ["Choisir...", "élévateur", "abaisseur"], "élévateur", "trans_t4_final"),
            ("5. Les lignes à Très Haute Tension transportent jusqu'à .......... kV.", ["Choisir...", "400", "20"], "400", "trans_t5_final"),
            ("6. Diviser le courant évite que les câbles aériens ne ..........", ["Choisir...", "fondent", "gèlent"], "fondent", "trans_t6_final"),
            ("7. Avant la distribution aux maisons, un poste va .......... la tension.", ["Choisir...", "abaisser", "élever"], "abaisser", "trans_t7_final"),
            ("8. Le transport à basse tension provoquerait un mauvais ..........", ["Choisir...", "rendement", "calibre"], "rendement", "trans_t8_final"),
            ("9. Le réseau national de transport est géré par la société ..........", ["Choisir...", "RTE", "Enedis"], "RTE", "trans_t9_final"),
            ("10. Ce maillage évite les pannes globales appelées un ..........", ["Choisir...", "blackout", "nœud"], "blackout", "trans_t10_final")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ten_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Réseau (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_tr_tension:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_pile_tension(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Décharge de pile) sur deux colonnes."""
    import random

    questions_pile_sources = [
        {"id": "qpi1", "q": "Quelle grandeur est indiquée par le fabricant sur l'étiquette d'une pile ?", "options": ["La tension nominale", "L'intensité maximale", "La résistance interne"], "rep": "La tension nominale"},
        {"id": "qpi2", "q": "Comment évolue la tension d'une pile au cours de son utilisation prolongée ?", "options": ["Elle diminue progressivement", "Elle reste strictement constante", "Elle augmente fortement"], "rep": "Elle diminue progressivement"},
        {"id": "qpi3", "q": "Comment appelle-t-on la mesure de la tension d'une pile neuve quand elle n'est branchée à aucun circuit ?", "options": ["La tension à vide", "La tension de court-circuit", "La tension nominale efficace"], "rep": "La tension à vide"},
        {"id": "qpi4", "q": "Pourquoi la tension aux bornes d'une pile chute-t-elle dès qu'elle débite du courant ?", "options": ["En raison de sa résistance interne", "Car les fils consomment de la tension", "Car l'appareil pousse la tension"], "rep": "En raison de sa résistance interne"},
        {"id": "qpi5", "q": "Quel type d'appareil vide la pile de son énergie de manière quasi instantanée et dangereuse ?", "options": ["Un court-circuit direct", "Une diode led de signalisation", "Un petit moteur électrique"], "rep": "Un court-circuit direct"},
        {"id": "qpi6", "q": "Dans quel sens s'effectue la transformation d'énergie à l'intérieur d'une pile électrique ?", "options": ["De l'énergie chimique vers l'énergie électrique", "De l'énergie mécanique vers l'énergie électrique", "De l'énergie thermique vers l'énergie électrique"], "rep": "De l'énergie chimique vers l'énergie électrique"},
        {"id": "qpi7", "q": "Que devient la courbe caractéristique d'une pile complètement déchargée ?", "options": ["Une ligne horizontale à 0V", "Une droite ascendante", "Une courbe sinusoïdale"], "rep": "Une ligne horizontale à 0V"},
        {"id": "qpi8", "q": "Pour prolonger la durée de vie d'une pile, l'appareil connecté doit posséder :", "options": ["Une forte résistance pour limiter le courant", "Une résistance nulle", "Deux interrupteurs en parallèle"], "rep": "Une forte résistance pour limiter le courant"},
        {"id": "qpi9", "q": "Quelle unité principale quantifie la quantité d'énergie emmagasinée par une pile (capacité) ?", "options": ["L'ampère-heure (Ah)", "Le volt", "L'ohm-mètre"], "rep": "L'ampère-heure (Ah)"},
        {"id": "qpi10", "q": "Une fois usée, une pile classique doit être jetée :", "options": ["Dans un bac de recyclage spécifique", "Dans la poubelle des déchets ménagers", "Dans le bac à compost"], "rep": "Dans un bac de recyclage spécifique"}
    ]

    if "ordre_quiz_tab5_aleatoire" not in st.session_state:
        random.shuffle(questions_pile_sources)
        st.session_state.ordre_quiz_tab5_aleatoire = questions_pile_sources

    # Liste de synthèse (Énoncé, Choix, Réponse attendue, Clé session)
    if "champs_p_tension" not in st.session_state:
        st.session_state.champs_p_tension = [
            ("1. La valeur inscrite par le constructeur est la tension ..........", ["Choisir...", "nominale", "à vide"], "nominale", "pile_t1_final"),
            ("2. Mesurer la tension d'un dipôle isolé donne la tension ..........", ["Choisir...", "à vide", "en surcharge"], "à vide", "pile_t2_final"),
            ("3. En débitant du courant, la tension mesurée ..........", ["Choisir...", "diminue", "augmente"], "diminue", "pile_t3_final"),
            ("4. Ce phénomène de perte de charge dépend de la résistance ..........", ["Choisir...", "interne", "externe"], "interne", "pile_t4_final"),
            ("5. La pile transforme de l'énergie .......... en flux électrique.", ["Choisir...", "chimique", "mécanique"], "chimique", "pile_t5_final"),
            ("6. Relier directement les deux bornes crée un .......... destructeur.", ["Choisir...", "court-circuit", "nœud"], "court-circuit", "pile_t6_final"),
            ("7. Un récepteur de forte résistance induit une décharge ..........", ["Choisir...", "lente", "instantanée"], "lente", "pile_t7_final"),
            ("8. Le suivi graphique U = f(t) donne la courbe de ..........", ["Choisir...", "décharge", "caractéristique"], "décharge", "pile_t8_final"),
            ("9. Quand la tension approche de zéro, la pile est dite ..........", ["Choisir...", "usagée", "chargée"], "usagée", "pile_t9_final"),
            ("10. Les piles contiennent des métaux lourds et imposent le ..........", ["Choisir...", "recyclage", "compostage"], "recyclage", "pile_t10_final")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Conceptuel (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ten_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse sur l'Énergie (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_p_tension:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_tension_derivation(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Tension en dérivation) sur deux colonnes."""
    import random

    questions_tderivation_sources = [
        {"id": "qtd1", "q": "Comment se comporte la tension aux bornes de dipôles branchés en dérivation ?", "options": ["Elle est rigoureusement identique pour chaque branche", "Elle s'additionne d'une branche à l'autre", "Elle diminue à chaque nœud"], "rep": "Elle est rigoureusement identique pour chaque branche"},
        {"id": "qtd2", "q": "Quelle égalité mathématique traduit la loi de la tension en parallèle pour deux récepteurs ?", "options": ["Ug = U1 = U2", "Ug = U1 + U2", "Ug = U1 - U2"], "rep": "Ug = U1 = U2"},
        {"id": "qtd3", "q": "Si le générateur d'une maison délivre 230V, quelle tension reçoit un téléviseur branché en dérivation ?", "options": ["230 V", "115 V", "0 V"], "rep": "230 V"},
        {"id": "qtd4", "q": "Pourquoi les appareils électroménagers d'une maison sont-ils tous montés en dérivation ?", "options": ["Pour recevoir la même tension de 230V et fonctionner indépendamment", "Pour consommer moins de courant", "Pour éviter d'utiliser des fusibles"], "rep": "Pour recevoir la même tension de 230V et fonctionner indépendamment"},
        {"id": "qtd5", "q": "Si une lampe grille dans une branche en dérivation, que devient la tension aux bornes de l'autre branche ?", "options": ["Elle reste inchangée", "Elle tombe immédiatement à zéro", "Elle est doublée"], "rep": "Elle reste inchangée"},
        {"id": "qtd6", "q": "La loi régissant la tension dans un circuit en parallèle s'appelle la loi d' :", "options": ["Unicité des tensions", "Additivité des tensions", "Additivité des intensités"], "rep": "Unicité des tensions"},
        {"id": "qtd7", "q": "Si on connecte une troisième lampe en parallèle sur la pile, la tension à ses bornes vaut :", "options": ["La même tension Ug que la pile", "Le tiers de la tension Ug", "Le triple de la tension Ug"], "rep": "La même tension Ug que la pile"},
        {"id": "qtd8", "q": "Quel est le risque de brancher un trop grand nombre d'appareils en dérivation sur une même multiprise ?", "options": ["Une surcharge d'intensité dans la ligne principale", "Une baisse de la tension générale", "Une surtension aux bornes des appareils"], "rep": "Une surcharge d'intensité dans la ligne principale"},
        {"id": "qtd9", "q": "La tension mesurée aux bornes d'un emplacement vide (sans aucun composant raccordé) d'une branche ouverte est :", "options": ["Égale à la tension du générateur", "Nulle", "Infinie"], "rep": "Égale à la tension du générateur"},
        {"id": "qtd10", "q": "Comment appelle-t-on les lignes conductrices qui relient directement un récepteur en dérivation aux deux bornes de la pile ?", "options": ["Les branches dérivées", "La branche principale", "Les nœuds centraux"], "rep": "Les branches dérivées"}
    ]

    if "ordre_quiz_tab4_aleatoire" not in st.session_state:
        random.shuffle(questions_tderivation_sources)
        st.session_state.ordre_quiz_tab4_aleatoire = questions_tderivation_sources

    # Liste de synthèse nettoyée : Exactement 10 lignes uniques à 4 éléments
    if "champs_d_tension" not in st.session_state:
        st.session_state.champs_d_tension = [
            ("1. Dans un montage en parallèle, la tension est .......... partout.", ["Choisir...", "identique", "différente"], "identique", "vder_t1_final"),
            ("2. La loi d'unicité s'exprime par la relation mathématique Ug = ..........", ["Choisir...", "U1 = U2", "U1 + U2"], "U1 = U2", "vder_t2_final"),
            ("3. Toutes les prises de courant d'une maison reçoivent la .......... tension.", ["Choisir...", "même", "somme"], "même", "vder_t3_final"),
            ("4. Si une branche du circuit s'ouvre, l'autre branche .......... alimentée.", ["Choisir...", "reste", "cesse d'être"], "reste", "vder_t4_final"),
            ("5. Ajouter un récepteur en parallèle ne fait pas .......... la tension.", ["Choisir...", "diminuer", "augmenter"], "diminué", "vder_t5_final"),
            ("6. Les portions parallèles branchées sur la pile sont les branches ..........", ["Choisir...", "dérivées", "principales"], "dérivées", "vder_t6_final"),
            ("7. Chaque appareil relié aux nœuds fonctionne de manière ..........", ["Choisir...", "indépendante", "liée"], "indépendante", "vder_t7_final"),
            ("8. Multiplier les lignes parallèles demande plus d'.......... au générateur.", ["Choisir...", "intensité", "tension"], "intensité", "vder_t8_final"),
            ("9. La tension domestique standard en France est régulée à .......... Volts.", ["Choisir...", "230", "12"], "230", "vder_t9_final"),
            ("10. Quel que soit le nombre de boucles, le voltmètre affiche la .......... valeur.", ["Choisir...", "même", "somme"], "même", "vder_t10_final")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Méthode (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ten_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        # Boucle sécurisée par lecture de ligne complète
        for ligne in st.session_state.champs_d_tension:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
def afficher_atelier_tension_serie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Tension en série) sur deux colonnes."""
    import random

    questions_tserie_sources = [
        {"id": "qts1", "q": "Dans un circuit en série, comment se comporte la tension générale ?", "options": ["Elle s'additionne aux bornes des récepteurs", "Elle reste identique partout", "Elle s'annule au premier nœud"], "rep": "Elle s'additionne aux bornes des récepteurs"},
        {"id": "qts2", "q": "Quelle formule représente la loi de la tension en série avec deux lampes ?", "options": ["Ug = U1 + U2", "Ug = U1 = U2", "Ug = U1 - U2"], "rep": "Ug = U1 + U2"},
        {"id": "qts3", "q": "Si une pile délivre 9V et alimente deux lampes identiques en série, quelle est la tension de chaque lampe ?", "options": ["4,5 V", "9 V", "18 V"], "rep": "4,5 V"},
        {"id": "qts4", "q": "Si U1 = 3V et U2 = 4V dans une boucle en série, que vaut la tension Ug de la pile ?", "options": ["7 V", "1 V", "12 V"], "rep": "7 V"},
        {"id": "qts5", "q": "Que se passe-t-il si la somme des tensions nominales des lampes est très supérieure à celle de la pile ?", "options": ["Les lampes éclairent très faiblement (sous-tension)", "Les lampes grillent", "L'intensité augmente fortement"], "rep": "Les lampes éclairent très faiblement (sous-tension)"},
        {"id": "qts6", "q": "La loi d'additivité des tensions porte également le nom scientifique de :", "options": ["Loi des mailles", "Loi des nœuds", "Loi d'unicité"], "rep": "Loi des mailles"},
        {"id": "qts7", "q": "Si on ajoute une troisième lampe en série dans la boucle, la tension de la pile :", "options": ["Reste la même mais se partage désormais en trois", "Augmente automatiquement", "S'effondre à 0V"], "rep": "Reste la même mais se partage désormais en trois"},
        {"id": "qts8", "q": "Aux bornes d'un simple fil de connexion parfait, la tension mesurée est de :", "options": ["0 V", "La même chose que la pile", "12 V"], "rep": "0 V"},
        {"id": "qts9", "q": "Aux bornes d'un interrupteur ouvert inséré en série, la tension est :", "options": ["Égale à celle du générateur", "Nulle", "Divisée par deux"], "rep": "Égale à celle du générateur"},
        {"id": "qts10", "q": "Modifier l'ordre de placement des récepteurs dans la boucle en série change-t-il leurs tensions ?", "options": ["Non, cela ne modifie pas les valeurs de tension", "Oui, la première lampe prend toujours tout", "Oui, le circuit se coupe"], "rep": "Non, cela ne modifie pas les valeurs de tension"}
    ]

    if "ordre_quiz_tab3_aleatoire" not in st.session_state:
        random.shuffle(questions_tserie_sources)
        st.session_state.ordre_quiz_tab3_aleatoire = questions_tserie_sources

    # Liste de synthèse (Énoncé, Choix, Réponse attendue, Clé session)
    if "champs_s_tension" not in st.session_state:
        st.session_state.champs_s_tension = [
            ("1. Dans une boucle unique, les tensions des récepteurs s'..........", ["Choisir...", "additionnent", "égalent"], "additionnent", "vser_t1_final"),
            ("2. L'expression mathématique s'écrit sous la forme Ug = ..........", ["Choisir...", "U1 + U2", "U1 = U2"], "U1 + U2", "vser_t2_final"),
            ("3. La loi d'additivité porte aussi le nom de loi des ..........", ["Choisir...", "mailles", "nœuds"], "mailles", "vser_t3_final"),
            ("4. Deux lampes identiques en série se .......... la tension de la pile.", ["Choisir...", "partagent", "multiplient"], "partagent", "vser_t4_final"),
            ("5. Aux bornes d'un fil de connexion isolé, la tension vaut ..........", ["Choisir...", "zéro", "douze"], "zéro", "vser_t5_final"),
            ("6. Un interrupteur ouvert en série stoppe le flux et prend .......... la tension.", ["Choisir...", "toute", "aucune"], "toute", "vser_t6_final"),
            ("7. Ajouter un récepteur en série fait .......... la tension des autres.", ["Choisir...", "diminuer", "augmenter"], "diminue", "vser_t7_final"),
            ("8. L'énergie électrique de la pile est entièrement ..........", ["Choisir...", "consommée", "créée"], "consommée", "vser_t8_final"),
            ("9. Une lampe en sous-tension reçoit un potentiel trop ..........", ["Choisir...", "faible", "fort"], "faible", "vser_t9_final"),
            ("10. Quel que soit l'ordre des dipôles, le total mesuré reste ..........", ["Choisir...", "identique", "variable"], "identique", "vser_t10_final")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Conceptuel (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ten_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse d'Application (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_s_tension:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_appareil_voltmetre(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Appareil de mesure de tension) sur deux colonnes."""
    import random

    questions_mesure_tension = [
        {"id": "qme1", "q": "Quel appareil utilise-t-on spécifiquement pour mesurer une tension électrique ?", "options": ["Le voltmètre", "L'ampèremètre", "L'ohmmètre"], "rep": "Le voltmètre"},
        {"id": "qme2", "q": "Comment doit être raccordé un voltmètre par rapport au composant à mesurer ?", "options": ["En dérivation (parallèle)", "En série", "Au choix selon le circuit"], "rep": "En dérivation (parallèle)"},
        {"id": "qme3", "q": "Par quelle borne le courant doit-il entrer dans le voltmètre pour une valeur positive ?", "options": ["La borne V", "La borne COM", "La borne 10A"], "rep": "La borne V"},
        {"id": "qme4", "q": "Quelle borne de l'appareil fait office de borne de sortie pour le courant ?", "options": ["La borne COM", "La borne V", "La borne mA"], "rep": "La borne COM"},
        {"id": "qme5", "q": "Quel symbole géométrique représente un voltmètre sur un schéma électrique ?", "options": ["Un cercle avec la lettre V", "Un cercle avec la lettre A", "Un rectangle"], "rep": "Un cercle avec la lettre V"},
        {"id": "qme6", "q": "Quel est le comportement d'un voltmètre inséré par erreur en série ?", "options": ["Il se comporte comme un interrupteur ouvert et bloque le courant", "Il crée un court-circuit", "Il grille immédiatement le générateur"], "rep": "Il se comporte comme un interrupteur ouvert et bloque le courant"},
        {"id": "qme7", "q": "Quel calibre doit-on privilégier en premier lors d'une mesure inconnue ?", "options": ["Le calibre le plus élevé", "Le calibre le plus bas", "Peu importe"], "rep": "Le calibre le plus élevé"},
        {"id": "qme8", "q": "Que se passe-t-il sur un appareil numérique si le calibre choisi est trop petit ?", "options": ["Il affiche un message de dépassement (ex: 1. ou OL)", "L'appareil explose", "L'écran affiche 0.00 V"], "rep": "Il affiche un message de dépassement (ex: 1. ou OL)"},
        {"id": "qme9", "q": "Quelle est l'unité internationale de mesure de la tension électrique ?", "options": ["Le volt", "L'ampère", "L'ohm"], "rep": "Le volt"},
        {"id": "qme10", "q": "Quel type de courant mesure-t-on de préférence dans la section continue (V=) ?", "options": ["Le courant fourni par une pile ou une batterie", "Le courant d'une prise murale", "Le courant d'une centrale hydraulique"], "rep": "Le courant fourni par une pile ou une batterie"}
    ]

    if "ordre_quiz_tab2_aleatoire" not in st.session_state:
        random.shuffle(questions_mesure_tension)
        st.session_state.ordre_quiz_tab2_aleatoire = questions_mesure_tension

    # Liste de synthèse à 4 éléments (Énoncé, Choix, Réponse attendue, Clé session)
    if "champs_m_tension" not in st.session_state:
        st.session_state.champs_m_tension = [
            ("1. Le voltmètre se monte en .......... aux bornes d'un récepteur.", ["Choisir...", "dérivation", "série"], "dérivation", "volt_t1_final"),
            ("2. Le symbole du voltmètre s'écrit avec la lettre V dans un ..........", ["Choisir...", "cercle", "rectangle"], "cercle", "volt_t2_final"),
            ("3. Pour mesurer une tension, le fil d'entrée se branche sur la borne ..........", ["Choisir...", "V", "COM"], "V", "volt_t3_final"),
            ("4. Le retour vers la borne négative de la pile se fait par la borne ..........", ["Choisir...", "COM", "10A"], "COM", "volt_t4_final"),
            ("5. Les anciens voltmètres de laboratoire utilisaient une .......... mobile.", ["Choisir...", "aiguille", "matrice"], "aiguille", "volt_t5_final"),
            ("6. Pour éviter d'endommager l'appareil, on commence par le plus grand ..........", ["Choisir...", "calibre", "stator"], "calibre", "volt_t6_final"),
            ("7. La très forte résistance interne du voltmètre empêche le passage du ..........", ["Choisir...", "courant", "stator"], "courant", "volt_t7_final"),
            ("8. L'unité abrégée par la lettre majuscule V s'appelle le ..........", ["Choisir...", "volt", "ampère"], "volt", "volt_t8_final"),
            ("9. Un affichage numérique moderne élimine les erreurs de ..........", ["Choisir...", "lecture", "calcul"], "lecture", "volt_t9_final"),
            ("10. L'outil combiné capable de mesurer tension et intensité est le ..........", ["Choisir...", "multimètre", "générateur"], "multimètre", "volt_t10_final")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ten_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse sur l'Appareil (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_m_tension:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_loi_ohm(verrouille=False):
    pass # Conservez vos fonctions existantes intactes

def afficher_atelier_histoire_tension(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Histoire de la tension) sur deux colonnes."""
    import random

    questions_tension_sources = [
        {"id": "qvt1", "q": "Quel scientifique a inventé la première pile électrique en l'an 1800 ?", "options": ["Alessandro Volta", "Luigi Galvani", "Michael Faraday"], "rep": "Alessandro Volta"},
        {"id": "qvt2", "q": "Sur quel animal Luigi Galvani réalisait-il ses expériences d'électricité biologique ?", "options": ["La grenouille", "La torpille", "Le poisson-chat"], "rep": "La grenouille"},
        {"id": "qvt3", "q": "En l'honneur de quel savant l'unité de mesure de la tension (le Volt) a-t-elle été nommée ?", "options": ["Alessandro Volta", "André-Marie Ampère", "James Watt"], "rep": "Alessandro Volta"},
        {"id": "qvt4", "q": "Quels métaux séparaient les disques de feutre salé dans la première pile ?", "options": ["Le cuivre et le zinc", "L'or et l'argent", "Le fer et le plomb"], "rep": "Le cuivre et le zinc"},
        {"id": "qvt5", "q": "Quel phénomène physique, découvert par Faraday, permet de créer une tension ?", "options": ["L'induction électromagnétique", "L'effet Joule", "L'électricité statique"], "rep": "L'induction électromagnétique"},
        {"id": "qvt6", "q": "Comment qualifie-t-on une tension qui change de sens au cours du temps ?", "options": ["Alternative", "Continue", "Statique"], "rep": "Alternative"},
        {"id": "qvt7", "q": "Quelle machine industrielle moderne convertit l'énergie mécanique en tension alternative ?", "options": ["L'alternateur", "La pile chimique", "La bouteille de Leyde"], "rep": "L'alternateur"},
        {"id": "qvt8", "q": "Dans un alternateur de centrale électrique, quelle est la partie mobile qui tourne ?", "options": ["Le rotor", "Le stator", "La bobine fixe"], "rep": "Le rotor"},
        {"id": "qvt9", "q": "Dans un alternateur, comment appelle-t-on l'armature fixe contenant les bobines ?", "options": ["Le stator", "Le collecteur", "Le rotor"], "rep": "Le stator"},
        {"id": "qvt10", "q": "Quel élément du bloc mobile d'un alternateur crée le champ magnétique ?", "options": ["L'aimant ou l'électroaimant", "La bobine de cuivre", "La turbine à eau"], "rep": "L'aimant ou l'électroaimant"}
    ]

    if "ordre_quiz_tab1_aleatoire" not in st.session_state:
        random.shuffle(questions_tension_sources)
        st.session_state.ordre_quiz_tab1_aleatoire = questions_tension_sources

    # Liste de synthèse à 4 éléments (Énoncé, Choix, Réponse attendue, Clé session)
    if "champs_h_tension" not in st.session_state:
        st.session_state.champs_h_tension = [
            ("1. Luigi Galvani pensait que l'électricité provenait de la ..........", ["Choisir...", "grenouille", "pile"], "grenouille", "ten_t1_final"),
            ("2. Alessandro Volta démontre le rôle clé du contact entre les ..........", ["Choisir...", "métaux", "muscles"], "métaux", "ten_t2_final"),
            ("3. La première pile électrique fonctionnait grâce à une solution ..........", ["Choisir...", "salée", "distillée"], "salée", "ten_t3_final"),
            ("4. L'unité officielle de mesure de la tension électrique est le ..........", ["Choisir...", "volt", "ampère"], "volt", "ten_t4_final"),
            ("5. Faire bouger un aimant devant une bobine crée une tension par ..........", ["Choisir...", "induction", "friction"], "induction", "ten_t5_final"),
            ("6. Contrairement à une pile, un alternateur crée une tension ..........", ["Choisir...", "alternative", "continue"], "alternative", "ten_t6_final"),
            ("7. L'élément en rotation relié à l'arbre de la turbine est le ..........", ["Choisir...", "rotor", "stator"], "rotor", "ten_t7_final"),
            ("8. L'armature périphérique immobile qui reçoit le flux s'appelle le ..........", ["Choisir...", "stator", "aimant"], "stator", "ten_t8_final"),
            ("9. Les spires de l'alternateur fixe sont composées de ..........", ["Choisir...", "cuivre", "fer"], "cuivre", "ten_t9_final"),
            ("10. Toutes les grandes centrales de production exploitent un ..........", ["Choisir...", "alternateur", "condensateur"], "alternateur", "ten_t10_final")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Historique et Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ten_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        # Utilisation de la boucle robuste pour tolérer 3 ou 4 éléments
        for ligne in st.session_state.champs_h_tension:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


with tab1:
    st.header("Histoire, découverte et génération de la tension électrique")
    
    # --- SECTION 1 : HISTOIRE ET DÉCOUVERTES ---
    st.subheader("La découverte de la tension : De Galvani à Alessandro Volta")
    st.write(
        "L'histoire de la tension électrique (ou différence de potentiel) prend racine à la fin du dix-huitième siècle "
        "lors d'une célèbre controverse scientifique entre deux savants italiens : Luigi Galvani et Alessandro Volta."
    )
    st.write(
        "Luigi Galvani, en observant les contractions musculaires d'une grenouille disséquée mise en contact avec deux métaux différents, "
        "en déduit l'existence d'une électricité animale d'origine biologique. "
        "Alessandro Volta, quant à lui, démontre que la grenouille ne sert que de simple conducteur. "
        "Pour lui, c'est le contact entre deux métaux de natures différentes qui engendre la force motrice de l'électricité."
    )
    
    # Évolution des générateurs à travers le temps
    st.write("**1. La pile de Alessandro Volta (L'année 1800)**")
    st.write(
        "En empilant des disques de cuivre et de zinc séparés par des rondelles de feutre imbibées d'eau salée, "
        "Volta crée le premier générateur capable de fournir de manière continue une tension électrique stable. "
        "C'est en hommage à son nom que l'unité de mesure de la tension a été baptisée le Volt."
    )
    try:
        st.image("pile_volta.jpg", caption="La première pile électrique à colonne d'Alessandro Volta")
    except Exception:
        st.warning("L'image 'pile_volta.jpg' est introuvable.")
        
    st.write("**2. L'induction électromagnétique de Michael Faraday (1831)**")
    st.write(
        "Michael Faraday découvre qu'en déplaçant un aimant à proximité d'une bobine de fil de cuivre, "
        "on fait apparaître une tension électrique temporaire aux bornes de la bobine. "
        "Ce phénomène physique, appelé l'induction électromagnétique, marque la naissance des générateurs mécaniques."
    )
    try:
        st.image("induction_faraday.jpg", caption="Expérience historique de Faraday sur l'induction")
    except Exception:
        st.warning("L'image 'induction_faraday.jpg' est introuvable.")

    st.write("**3. L'alternateur industriel moderne**")
    st.write(
        "Aujourd'hui, l'immense majorité de la tension électrique distribuée dans le monde est produite par des alternateurs "
        "au sein des centrales électriques (nucléaires, hydrauliques, éoliennes ou thermiques). "
        "Un alternateur convertit l'énergie mécanique de rotation en énergie électrique grâce à deux éléments principaux :\n"
        "* **Le rotor :** Un aimant ou un électroaimant géant qui est mis en rotation par une turbine.\n"
        "* **Le stator :** Une armature fixe contenant d'immenses bobines de cuivre dans lesquelles la tension alternative est induite."
    )
    try:
        st.image("alternateur_moderne.jpg", caption="Vue en coupe d'un alternateur industriel de centrale")
    except Exception:
        st.warning("L'image 'alternateur_moderne.jpg' est introuvable.")

    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES ET VERROUILLAGE DE L'ATELIER 1 ---
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    # Affichage du module de questions spécifique à la tension
    afficher_atelier_histoire_tension(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Histoire et Génération de la tension.",
        key="check_certif_tension_final_net",
        disabled=verrou_at1,
    )

    # Bouton de validation pour bloquer et générer les notes du Tab 1
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_tension_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_aleatoire:
                    reponse_eleve = st.session_state.get(f"ten_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = 0.0
            if "champs_h_tension" in st.session_state:
                for ligne in st.session_state.champs_h_tension:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(cle, "Choisir...") == attendu:
                        score_t1 += 1.0

            st.session_state.score_suite1_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1 = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 1 ---
    if st.session_state.get("suite_verrouille_tab1", False):
        scr1_t1 = st.session_state.get("score_suite1_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1", 0.0)

        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER HISTOIRE ET GÉNÉRATION SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_tension = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Histoire Tension - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 1 : Découverte historique et machines de production de la tension</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab1_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
                saisie = st.session_state.get(f"ten_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tension += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tension += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t1 = preparer_nom_fichier("Rapport_Histoire_Tension").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_tension,
            file_name=nom_fichier_html_t1,
            mime="text/html",
            use_container_width=True
        )








with tab2:
    st.header("L'appareil de mesure de la tension : Le voltmètre")
    
    # --- SECTION 1 : THÉORIE ET APPAREILS ---
    st.subheader("Mesurer une différence de potentiel")
    st.write(
        "Pour mesurer la tension électrique aux bornes d'un dipôle, on utilise un voltmètre. "
        "Tout comme pour l'intensité, les technologies ont évolué au fil du temps."
    )
    
    col_app1, col_app2 = st.columns(2)
    with col_app1:
        st.write("**Les anciens appareils : Le voltmètre analogique**")
        st.write(
            "Il utilise une aiguille mobile qui se déplace devant un cadran gradué. "
            "La lecture nécessite l'application d'une formule mathématique précise dépendant du calibre choisi."
        )
        try:
            st.image("ancien_voltmetre.jpg", caption="Voltmètre analogique mécanique à aiguille")
        except Exception:
            st.warning("L'image 'ancien_voltmetre.jpg' est introuvable.")
            
    with col_app2:
        st.write("**Les nouveaux appareils : Le multimètre numérique**")
        st.write(
            "Plus précis et plus robuste, le multimètre numérique configuré sur le secteur V (Volt) "
            "affiche directement la valeur numérique de la tension sur son écran à cristaux liquides."
        )
        try:
            st.image("multimetre_voltmetre.jpg", caption="Multimètre moderne réglé en mode voltmètre")
        except Exception:
            st.warning("L'image 'multimetre_voltmetre.jpg' est introuvable.")

    st.write("**Le symbole normalisé et la règle absolue de branchement**")
    st.write(
        "Sur un schéma normalisé, le voltmètre est représenté par un cercle contenant la lettre majuscule V.\n\n"
        "**Règle fondamentale :** Contrairement à l'ampèremètre, un voltmètre se branche obligatoirement **en dérivation (en parallèle)** "
        "aux bornes du dipôle dont on souhaite mesurer la tension. Le courant doit entrer par la borne V et ressortir par la borne COM.\n"
        "Il ne faut jamais insérer un voltmètre en série, car sa très forte résistance interne bloquerait la circulation du courant."
    )
    
    col_sym1, col_sym2 = st.columns(2)
    with col_sym1:
        try:
            st.image("symbole_voltmetre.jpg", caption="Symbole normalisé du voltmètre")
        except Exception:
            st.warning("L'image 'symbole_voltmetre.jpg' est introuvable.")
    with col_sym2:
        try:
            st.image("branchement_voltmetre.jpg", caption="Schéma d'un branchement de voltmètre en dérivation")
        except Exception:
            st.warning("L'image 'branchement_voltmetre.jpg' est introuvable.")

    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES ET VERROUILLAGE DE L'ATELIER 2 ---
    if "suite_verrouille_tab2" not in st.session_state:
        st.session_state.suite_verrouille_tab2 = False
    verrou_at2 = st.session_state.suite_verrouille_tab2

    # Affichage du module de questions spécifique au voltmètre
    afficher_atelier_appareil_voltmetre(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur l'appareil de mesure.",
        key="check_certif_volt_final_net",
        disabled=verrou_at2,
    )

    # Bouton de validation pour bloquer et générer les notes du Tab 2
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_volt_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_aleatoire:
                    reponse_eleve = st.session_state.get(f"ten_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = 0.0
            if "champs_m_tension" in st.session_state:
                for ligne in st.session_state.champs_m_tension:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(cle, "Choisir...") == attendu:
                        score_t2 += 1.0

            st.session_state.score_suite2_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2 = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2", False):
        scr1_t2 = st.session_state.get("score_suite2_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2", 0.0)

        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER APPAREIL VOLTMÈTRE SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_voltmetre = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Appareil de Mesure - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 2 : Appareils de mesure de la tension, calibres et branchements</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
                saisie = st.session_state.get(f"ten_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_voltmetre += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_voltmetre += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t2 = preparer_nom_fichier("Rapport_Appareil_Voltmestre").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_voltmetre,
            file_name=nom_fichier_html_t2,
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("La tension dans les circuits en série")
    
    # --- SECTION 1 : THÉORIE ET LOI D'ADDITIVITÉ ---
    st.subheader("La loi d'additivité des tensions")
    st.write(
        "Dans un circuit en série (comportant une seule boucle), la tension aux bornes du générateur "
        "est égale à la somme des tensions aux bornes des différents récepteurs branchés les uns à la suite des autres."
    )
    st.write(
        "Si la tension du générateur est notée Ug, et que le circuit comporte deux lampes en série "
        "aux bornes desquelles on mesure les tensions U1 Gens et U2, la loi s'écrit mathématiquement :\n\n"
        "**Ug = U1 + U2**\n\n"
        "Cette loi est fondamentale et montre que l'énergie électrique fournie par la pile se répartit "
        "entre les différents composants de la boucle unique."
    )

    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF GRAPHIQUE DYNAMIQUE ---
    st.subheader("Animation : Laboratoire de mesure de la tension en série")
    st.write(
        "Modifiez la tension de la pile et choisissez les caractéristiques des lampes branchées en série. "
        "Observez comment les trois voltmètres virtuels (V_pile, V_lampe1, V_lampe2) s'adaptent instantanément "
        "pour vérifier l'additivité."
    )

    # Commandes de contrôle de la simulation
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        tension_gen_s = st.slider(
            "Tension délivrée par la pile (Ug) [V]",
            min_value=0.0,
            max_value=24.0,
            value=12.0,
            step=0.5,
            key="slider_ug_tab3"
        )
    with col_ctrl2:
        repartition_lampes = st.selectbox(
            "Choisir les types de lampes installées :",
            options=["Lampes identiques (Répartition 50% / 50%)", "Lampe 1 plus résistante (Répartition 70% / 30%)", "Lampe 2 plus résistante (Répartition 30% / 70%)"],
            key="select_lampes_tab3"
        )

    # Modélisation physique du partage de la tension
    if repartition_lampes == "Lampes identiques (Répartition 50% / 50%)":
        u_lampe1 = tension_gen_s * 0.50
        u_lampe2 = tension_gen_s * 0.50
    elif repartition_lampes == "Lampe 1 plus résistante (Répartition 70% / 30%)":
        u_lampe1 = tension_gen_s * 0.70
        u_lampe2 = tension_gen_s * 0.30
    else:
        u_lampe1 = tension_gen_s * 0.30
        u_lampe2 = tension_gen_s * 0.70

    # --- CONSTRUCTION GRAPHIQUE DU CIRCUIT SÉRIE (PLOTLY) ---
    fig_tension_s = go.Figure()

    # Déclaration des listes de coordonnées x isolées pour la boucle
    liste_x_boucle = [1, 9, 9, 1, 1]
    liste_y_boucle = [5, 5, 1, 1, 5]

    # Câble électrique principal (Boucle rectangulaire)
    fig_tension_s.add_trace(go.Scatter(
        x=liste_x_boucle, y=liste_y_boucle,
        mode="lines",
        line=dict(color="#475569", width=4),
        showlegend=False, hoverinfo="none"
    ))

    liste_x_v_generateur = [6.5, 6.5, 7.5, 7.5]
    liste_x_v_lampe1     = [0.5, 0.5, 1.5, 1.5]
    liste_x_v_lampe2     = [8.5, 8.5, 9.5, 9.5]

    # Connexions secondaires des voltmètres (Fils de dérivation en pointillés)
    fils_voltmetres = [
        {"x": liste_x_v_generateur, "y": [5.0, 6.0, 6.0, 5.0]}, # Voltmètre Générateur
        {"x": liste_x_v_lampe1,     "y": [3.5, 3.5, 2.5, 2.5]}, # Voltmètre Lampe 1
        {"x": liste_x_v_lampe2,     "y": [3.5, 3.5, 2.5, 2.5]}  # Voltmètre Lampe 2
    ]
    for fil in fils_voltmetres:
        fig_tension_s.add_trace(go.Scatter(
            x=fil["x"], y=fil["y"],
            mode="lines",
            line=dict(color="#94a3b8", width=2, dash="dash"),
            showlegend=False, hoverinfo="none"
        ))

    # Placement des composants physiques (Pile et Lampes)
    # Générateur (Carré rouge en haut)
    fig_tension_s.add_trace(go.Scatter(
        x=[5], y=[5], mode="markers",
        marker=dict(color="#ef4444", size=30, symbol="square"),
        showlegend=False, hoverinfo="none"
    ))
    # Lampe 1 (Cercle jaune à gauche)
    fig_tension_s.add_trace(go.Scatter(
        x=[1], y=[3], mode="markers",
        marker=dict(color="#eab308", size=28, symbol="circle-x"),
        showlegend=False, hoverinfo="none"
    ))
    # Lampe 2 (Cercle jaune à droite)
    fig_tension_s.add_trace(go.Scatter(
        x=[9], y=[3], mode="markers",
        marker=dict(color="#eab308", size=28, symbol="circle-x"),
        showlegend=False, hoverinfo="none"
    ))

    # Placement des pastilles bleues des Voltmètres branchés en parallèle
    fig_tension_s.add_trace(go.Scatter(
        x=[5, 0, 10], y=[6, 3, 3], mode="markers",
        marker=dict(color="#0284c7", size=22),
        showlegend=False, hoverinfo="none"
    ))

    # 1. Légende de la Pile (Le gras est géré par la balise <b> dans le texte)
    fig_tension_s.add_annotation(
        x=5, y=5, text="<b>Pile</b>",
        showarrow=False, yshift=-25, 
        font=dict(color="#ef4444", size=11)
    )
    
    # 2. Valeur Voltmètre Pile (Haut)
    fig_tension_s.add_annotation(
        x=5, y=6, text=f"Voltmètre Ug<br><b>{tension_gen_s:.1f} V</b>",
        showarrow=False, yshift=25, 
        font=dict(color="#0284c7", size=11)
    )
    
    # 3. Valeur Voltmètre Lampe 1 (Gauche)
    fig_tension_s.add_annotation(
        x=0, y=3, text=f"Voltmètre U1<br><b>{u_lampe1:.1f} V</b>",
        showarrow=False, xshift=-45, 
        font=dict(color="#0284c7", size=11)
    )
    fig_tension_s.add_annotation(
        x=1, y=3, text="<b>Lampe 1</b>",
        showarrow=False, xshift=35, 
        font=dict(color="#b45309", size=11)
    )
    
    # 4. Valeur Voltmètre Lampe 2 (Droite)
    fig_tension_s.add_annotation(
        x=10, y=3, text=f"Voltmètre U2<br><b>{u_lampe2:.1f} V</b>",
        showarrow=False, xshift=45, 
        font=dict(color="#0284c7", size=11)
    )
    fig_tension_s.add_annotation(
        x=9, y=3, text="<b>Lampe 2</b>",
        showarrow=False, xshift=-35, 
        font=dict(color="#b45309", size=11)
    )

    # Réglage du plan de vue de la figure
    fig_tension_s.update_layout(
        xaxis=dict(visible=False, range=[-1.5, 11.5]),
        yaxis=dict(visible=False, range=[0.5, 7.2]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        plot_bgcolor="white",
        dragmode=False
    )

    # Affichage du graphe interactif
    st.plotly_chart(fig_tension_s, use_container_width=True, config={"displayModeBar": False})

    st.info(
        f"Vérification de la loi d'additivité : "
        f"{u_lampe1:.1f} V (U1) + {u_lampe2:.1f} V (U2) = {tension_gen_s:.1f} V (Ug). "
        f"La tension globale de la source est bien égale à la somme des tensions consommées."
    )

    st.divider()

    # --- SECTION 3 : ZONE DE QUIZ ET COMMANDE DE VERROUILLAGE ---
    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3

    # Affichage du module de questions spécifique à l'onglet 3
    afficher_atelier_tension_serie(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Tension en série.",
        key="check_certif_tserie_final_net",
        disabled=verrou_at3,
    )

    # Validation du score et blocage de session
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_tension_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_aleatoire:
                    reponse_eleve = st.session_state.get(f"ten_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            score_t3 = 0.0
            if "champs_s_tension" in st.session_state:
                for ligne in st.session_state.champs_s_tension:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(cle, "Choisir...") == attendu:
                        score_t3 += 1.0

            st.session_state.score_suite3_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3 = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3 = True
            st.rerun()

    # --- EXPORTATION DU RAPPORT HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab3", False):
        scr1_t3 = st.session_state.get("score_suite3_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER TENSION EN SÉRIE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_t_serie = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Tension en Série - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0284c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0369a1; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 3 : Lois de la tension dans les circuits en série</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
                Note obtenue au Quiz Conceptuel : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse d'Application : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Traitement des lignes du tableau de résultats
        if "ordre_quiz_tab3_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
                saisie = st.session_state.get(f"ten_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_t_serie += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Clôture du document HTML et téléchargement
        html_export_t_serie += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_t3 = preparer_nom_fichier("Rapport_Tension_Serie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_t_serie,
            file_name=nom_fichier_html_t3,
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("La tension dans les circuits en dérivation")
    
    # --- SECTION 1 : THÉORIE ET LOI D'UNICITÉ ---
    st.subheader("La loi d'unicité des tensions")
    st.write(
        "Dans un circuit en dérivation (comportant plusieurs boucles), la tension est la même "
        "aux bornes du générateur et aux bornes de chacune des branches dérivées branchées en parallèle."
    )
    st.write(
        "Si la tension du générateur est notée Ug, et que deux lampes sont branchées en dérivation sur ce générateur, "
        "les tensions U1 et U2 à leurs bornes respectives vérifient la relation suivante :\n\n"
        "**Ug = U1 = U2**\n\n"
        "Cette loi montre que tous les appareils branchés en dérivation reçoivent la même tension, "
        "ce qui correspond exactement au mode de fonctionnement des installations électriques de nos habitations."
    )

    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF GRAPHIQUE DYNAMIQUE ---
    st.subheader("Animation : Laboratoire de mesure de la tension en dérivation")
    st.write(
        "Modifiez la tension de la pile et choisissez la nature du dipôle de la branche 2. "
        "Observez comment les trois voltmètres virtuels (V_pile, V_lampe1, V_branche2) se mettent à jour "
        "instantanément pour valider la loi d'unicité."
    )

    # Commandes de contrôle de la simulation
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        tension_gen_d = st.slider(
            "Tension délivrée par la pile (Ug) en Volts [V]",
            min_value=0.0,
            max_value=24.0,
            value=12.0,
            step=0.5,
            key="slider_ug_tab4"
        )
    with col_ctrl2:
        choix_dipole_d = st.selectbox(
            "Choisir le dipôle de la branche 2 :",
            options=["Lampe standard (100 Ohms)", "Résistance chauffante (40 Ohms)", "Moteur électrique (24 Ohms)"],
            key="select_dipole_tab4"
        )

    # Modélisation physique : En dérivation, la tension est identique partout
    u_branche1 = tension_gen_d
    u_branche2 = tension_gen_d

    # Détermination de la résistance de la branche 2 pour la légende
    if "100" in choix_dipole_d:
        r_br2_d = 100.0
    elif "40" in choix_dipole_d:
        r_br2_d = 40.0
    else:
        r_br2_d = 24.0

    # --- CONSTRUCTION GRAPHIQUE DU CIRCUIT EN DÉRIVATION (PLOTLY) ---
    fig_tension_d = go.Figure()

    # Déclaration des listes de coordonnées x isolées pour les fils
    liste_x_principale_h = [0, 4, 4]
    liste_x_principale_b = [0, 4, 4]
    liste_x_br1 = [4, 4]
    liste_x_br2 = [4, 8, 8, 4]

    # Câbles électriques (Lignes de fond du circuit en dérivation)
    liste_x_fil_haut_gauche = [0.0, 4.0]
    liste_x_fil_bas_gauche  = [0.0, 4.0]
    liste_x_fil_branche_1   = [4.0, 4.0]
    liste_x_fil_branche_2   = [4.0, 8.0, 8.0, 8.0, 4.0]

    # Câbles électriques (Lignes de fond du circuit en dérivation)
    fils_derivation = [
        {"x": liste_x_fil_haut_gauche, "y": [3.0, 3.0, 5.0]},        # Haut gauche
        {"x": liste_x_fil_bas_gauche,  "y": [3.0, 3.0, 1.0]},        # Bas gauche
        {"x": liste_x_fil_branche_1,   "y": [5.0, 1.0]},             # Branche 1 verticale
        {"x": liste_x_fil_branche_2,   "y": [5.0, 5.0, 2.2, 1.0, 1.0]} # Branche 2 droite
    ]
    for fil in fils_derivation:
        fig_tension_d.add_trace(go.Scatter(
            x=fil["x"], y=fil["y"],
            mode="lines",
            line=dict(color="#475569", width=4),
            showlegend=False, hoverinfo="none"
        ))

    # Connexions secondaires des voltmètres (Fils pointillés de dérivation)
    liste_x_v_pile     = [1.5, 1.5, 2.5, 2.5]
    liste_x_v_branche1 = [2.5, 2.5, 3.5, 3.5]
    liste_x_v_branche2 = [7.5, 7.5, 8.5, 8.5]

    # Connexions secondaires des voltmètres (Fils pointillés de dérivation)
    fils_v_d = [
        {"x": liste_x_v_pile,     "y": [4.5, 4.5, 3.5, 3.5]}, # Voltmètre Pile
        {"x": liste_x_v_branche1, "y": [3.5, 3.5, 2.5, 2.5]}, # Voltmètre Lampe 1
        {"x": liste_x_v_branche2, "y": [3.5, 3.5, 2.5, 2.5]}  # Voltmètre Branche 2
    ]
    for fil in fils_v_d:
        fig_tension_d.add_trace(go.Scatter(
            x=fil["x"], y=fil["y"],
            mode="lines",
            line=dict(color="#94a3b8", width=2, dash="dash"),
            showlegend=False, hoverinfo="none"
        ))

    # Nœuds de dérivation (Points noirs)
    fig_tension_d.add_trace(go.Scatter(
        x=[4, 4], y=[5, 1], mode="markers",
        marker=dict(color="#0f172a", size=14),
        showlegend=False, hoverinfo="none"
    ))

    # Pile (Carré rouge à gauche)
    fig_tension_d.add_trace(go.Scatter(
        x=[0], y=[3], mode="markers",
        marker=dict(color="#ef4444", size=30, symbol="square"),
        showlegend=False, hoverinfo="none"
    ))
    
    # Lampe 1 (Cercle jaune au milieu)
    fig_tension_d.add_trace(go.Scatter(
        x=[4], y=[2.0], mode="markers",
        marker=dict(color="#eab308", size=28, symbol="circle-x"),
        showlegend=False, hoverinfo="none"
    ))
    
    # Dipôle variable 2 (Cercle orange ou hexagone à droite)
    fig_tension_d.add_trace(go.Scatter(
        x=[8], y=[2.0], mode="markers",
        marker=dict(color="#f59e0b", size=28, symbol="circle-x" if "Lampe" in choix_dipole_d else "hexagon"),
        showlegend=False, hoverinfo="none"
    ))

    # Pastilles bleues des Voltmètres
    fig_tension_d.add_trace(go.Scatter(
        x=[2, 3, 9], y=[4.0, 3.0, 3.0], mode="markers",
        marker=dict(color="#0284c7", size=20),
        showlegend=False, hoverinfo="none"
    ))

    # --- AJOUT DES TEXTES ET VALEURS INTERACTIVES ---
    # Légende Pile
    fig_tension_d.add_annotation(
        x=0, y=3, text=f"Pile<br><b>{tension_gen_d:.1f} V</b>",
        showarrow=True, arrowhead=1, ax=-50, ay=0, font=dict(color="#ef4444", size=12)
    )
    # Nœuds
    fig_tension_d.add_annotation(
        x=4, y=5, text="<b>Nœud d'entrée</b>",
        showarrow=True, arrowhead=1, ax=0, ay=35, font=dict(color="#0f172a", size=11)
    )
    fig_tension_d.add_annotation(
        x=4, y=1, text="<b>Nœud de retour</b>",
        showarrow=True, arrowhead=1, ax=0, ay=-35, font=dict(color="#0f172a", size=11)
    )
    # Voltmètre Pile (Gauche)
    fig_tension_d.add_annotation(
        x=2, y=4.0, text=f"Ug = <b>{tension_gen_d:.1f} V</b>",
        showarrow=False, yshift=18, font=dict(color="#0284c7", size=11)
    )
    # Voltmètre Branche 1 (Milieu)
    fig_tension_d.add_annotation(
        x=3, y=3.0, text=f"U1 = <b>{u_branche1:.1f} V</b>",
        showarrow=False, xshift=-45, font=dict(color="#0284c7", size=11)
    )
    fig_tension_d.add_annotation(
        x=4, y=2.0, text="Lampe 1<br>(60 Ω)",
        showarrow=False, xshift=50, font=dict(color="#b45309", size=11)
    )
    # Voltmètre Branche 2 (Droite)
    fig_tension_d.add_annotation(
        x=9, y=3.0, text=f"U2 = <b>{u_branche2:.1f} V</b>",
        showarrow=False, xshift=45, font=dict(color="#0284c7", size=11)
    )
    nom_propre_tab4_v = choix_dipole_d.split(" (")
    fig_tension_d.add_annotation(
        x=8, y=2.0, text=f"{nom_propre_tab4_v}<br>({r_br2_d:.0f} Ω)",
        showarrow=False, xshift=-55, font=dict(color="#b45309", size=11)
    )

    # Réglage des axes
    fig_tension_d.update_layout(
        xaxis=dict(visible=False, range=[-2.0, 11.0]),
        yaxis=dict(visible=False, range=[0.2, 6.5]),
        margin=dict(l=10, r=10, t=10, b=10),
        height=400,
        plot_bgcolor="white",
        dragmode=False
    )

    # Affichage du graphe interactif
    st.plotly_chart(fig_tension_d, use_container_width=True, config={"displayModeBar": False})

    st.info(
        f"Loi d'unicité démontrée : La tension reste rigoureusement identique dans toutes les branches en parallèle, "
        f"soit Ug ({tension_gen_d:.1f} V) = U1 ({u_branche1:.1f} V) = U2 ({u_branche2:.1f} V)."
    )

    st.divider()

    # --- SECTION 3 : ZONE DE QUIZ AND VERROUILLAGE ---
    if "suite_verrouille_tab4" not in st.session_state:
        st.session_state.suite_verrouille_tab4 = False
    verrou_at4 = st.session_state.suite_verrouille_tab4

    # Appel de la fonction d'exercice spécifique
    afficher_atelier_tension_derivation(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Tension en dérivation.",
        key="check_certif_tder_final_net",
        disabled=verrou_at4,
    )

    # Bloc de calcul des scores au clic sur le bouton de scellé
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_tension_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_aleatoire:
                    reponse_eleve = st.session_state.get(f"ten_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            score_t4 = 0.0
            if "champs_d_tension" in st.session_state:
                for ligne in st.session_state.champs_d_tension:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(cle, "Choisir...") == attendu:
                        score_t4 += 1.0

            st.session_state.score_suite4_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4 = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4 = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 4 ---
    if st.session_state.get("suite_verrouille_tab4", False):
        scr1_t4 = st.session_state.get("score_suite4_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER TENSION EN DÉRIVATION SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_t_derivation = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Tension en Dérivation - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0d9488; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #115e59; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 4 : Lois de la tension dans les circuits en dérivation</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
                Note obtenue au Quiz Méthode : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
                saisie = st.session_state.get(f"ten_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_t_derivation += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_t_derivation += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t4 = preparer_nom_fichier("Rapport_Tension_Derivation").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_t_derivation,
            file_name=nom_fichier_html_t4,
            mime="text/html",
            use_container_width=True
        )

with tab5:
    st.header("Tension aux bornes d'une pile et courbe de décharge")
    
    # --- SECTION 1 : THÉORIE ET NOTIONS DE COURS ---
    st.subheader("La tension d'une pile en fonctionnement")
    st.write(
        "Une pile électrique neuve possède une tension à vide (sa force électromotrice) indiquée par le fabricant "
        "(par exemple 1,5 V ou 9 V). Cependant, dès que la pile est branchée dans un circuit fermé et qu'elle débite du courant, "
        "sa tension chute en raison de sa résistance interne.\n\n"
        "Au fur et à mesure de son utilisation, l'énergie chimique de la pile s'épuise. Sa tension diminue progressivement "
        "au cours du temps. Plus l'appareil branché consomme d'intensité (résistance faible), plus la pile se décharge rapidement."
    )

    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF DE DÉCHARGE DYNAMIQUE ---
    st.subheader("Animation : Simulation de la décharge d'une pile de 9V")
    st.write(
        "Modifiez le temps d'utilisation et la résistance de l'appareil connecté pour observer la décharge de la pile. "
        "Le graphique de la tension U = f(t) et le point de fonctionnement se mettent à jour instantanément."
    )

    # Commandes de contrôle du laboratoire
    col_t5_1, col_p5_2 = st.columns(2)
    with col_t5_1:
        temps_heures = st.slider(
            "Temps d'utilisation écoulé en heures [h]",
            min_value=0.0, max_value=50.0, value=0.0, step=1.0,
            key="slider_temps_tab5"
        )
    with col_p5_2:
        appareil_charge = st.selectbox(
            "Appareil connecté à la pile (Résistance de charge) :",
            options=["Lampe témoin led (Forte résistance - Décharge lente)", "Moteur électrique (Moyenne résistance)", "Court-circuit direct (Résistance presque nulle - Décharge instantanée)"],
            key="select_appareil_tab5"
        )

    # Modélisation physique simplifiée de la décharge
    u_initiale = 9.0
    if "led" in appareil_charge:
        facteur_decharge = 0.05
    elif "Moteur" in appareil_charge:
        facteur_decharge = 0.25
    else: # Court-circuit
        facteur_decharge = 2.5

    # Calcul dynamique de la tension actuelle (modèle exponentiel de décharge)
    tension_actuelle = u_initiale * np.exp(-facteur_decharge * (temps_heures / 10.0))
    if tension_actuelle < 0.1:
        tension_actuelle = 0.0

    # Affichage des métriques de diagnostic
    col_m5_1, col_m5_2, col_m5_3 = st.columns(3)
    with col_m5_1:
        st.metric(label="Tension nominale initiale", value="9.0 V")
    with col_m5_2:
        st.metric(label="Temps de fonctionnement", value=f"{temps_heures:.0f} h")
    with col_m5_3:
        if tension_actuelle <= 1.0:
            st.metric(label="Tension mesurée actuelle", value=f"{tension_actuelle:.2f} V", delta="Pile usagée / Morte")
        else:
            st.metric(label="Tension mesurée actuelle", value=f"{tension_actuelle:.2f} V")

    # Génération des données pour tracer la courbe complète de décharge U = f(t)
    axe_temps = np.linspace(0, 50, 100)
    axe_tension = u_initiale * np.exp(-facteur_decharge * (axe_temps / 10.0))
    axe_tension = np.where(axe_tension < 0.1, 0.0, axe_tension)

    df_decharge = pd.DataFrame({
        "Temps (heures)": axe_temps,
        "Tension (V)": axe_tension
    })

    # Affichage de la courbe caractéristique native
    st.line_chart(df_decharge, x="Temps (heures)", y="Tension (V)")
    
    if tension_actuelle <= 1.0:
        st.error("Alerte système : La pile est complètement épuisée. Veuillez la remplacer ou réarmer le curseur de temps à 0.")
    else:
        st.success("Fonctionnement normal : La pile délivre un potentiel suffisant pour alimenter le circuit.")

    st.divider()

    # --- SECTION 3 : ZONE DE QUIZ ET VERROUILLAGE DE L'ATELIER 5 ---
    if "suite_verrouille_tab5" not in st.session_state:
        st.session_state.suite_verrouille_tab5 = False
    verrou_at5 = st.session_state.suite_verrouille_tab5

    # Appel du module de questions spécifique à l'onglet 5
    afficher_atelier_pile_tension(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Tension aux bornes d'une pile.",
        key="check_certif_tpile_final_net",
        disabled=verrou_at5,
    )

    # Bloc de correction et calcul des notes
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_tension_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_aleatoire:
                    reponse_eleve = st.session_state.get(f"ten_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q5 += 1.0

            score_t5 = 0.0
            if "champs_p_tension" in st.session_state:
                for ligne in st.session_state.champs_p_tension:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(cle, "Choisir...") == attendu:
                        score_t5 += 1.0

            st.session_state.score_suite5_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5 = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5 = True
            st.rerun()

    # --- SECTION 4 : COMPILATION DU BILAN HTML POUR L'ONGLET 5 ---
    if st.session_state.get("suite_verrouille_tab5", False):
        scr1_t5 = st.session_state.get("score_suite5_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER TENSION PILE SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_t_pile = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Décharge Pile - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4f46e5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #4f46e5; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 5 : Tension d'une pile, décharge thermique et caractéristiques</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4f46e5;">
                Note obtenue au Quiz Conceptuel : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab5_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_aleatoire, 1):
                saisie = st.session_state.get(f"ten_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                
                # Ajout de la ligne au tableau HTML de correction
                html_export_t_pile += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Fermeture définitive des conteneurs de la table et du fichier HTML
        html_export_t_pile += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Configuration sécurisée du bouton de téléchargement Streamlit pour l'Atelier 5
        nom_fichier_html_t5 = preparer_nom_fichier("Rapport_Tension_Pile").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_t_pile,
            file_name=nom_fichier_html_t5,
            mime="text/html",
            use_container_width=True
        )

with tab6:
    st.header("Transport d'énergie et lignes à haute tension")
    
    # --- SECTION 1 : THÉORIE ET EFFET JOULE ---
    st.subheader("Pourquoi élever la tension pour transporter l'électricité ?")
    st.write(
        "Le transport de l'électricité depuis les centrales de production jusqu'aux habitations "
        "nécessite de parcourir des centaines de kilomètres à travers des câbles conducteurs. "
        "Ces câbles possèdent une résistance électrique qui engendre une perte d'énergie sous forme de chaleur : "
        "c'est le phénomène de l'**effet Joule**."
    )
    st.write(
        "La puissance perdue par effet Joule s'exprime par la formule : P = R x I². "
        "Pour transporter une même quantité d'énergie (P = U x I), si l'on augmente la tension (U), "
        "l'intensité (I) diminue proportionnellement. En divisant l'intensité, on réduit drastiquement les pertes "
        "thermiques lors du transport. C'est le rôle des transformateurs élévateurs de tension placés à la sortie des centrales."
    )

    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF DE TRANSPORT D'ÉNERGIE ---
    st.subheader("Animation : Impact de la tension sur les pertes en ligne")
    st.write(
        "Modifiez la tension de transport à l'aide du curseur pour observer comment l'intensité "
        "dans les câbles s'effondre et comment la puissance perdue par effet Joule est minimisée."
    )

    # Commandes de contrôle du laboratoire
    col_t6_1, col_t6_2 = st.columns(2)
    with col_t6_1:
        puissance_centrale_mw = st.slider(
            "Puissance électrique à transporter en Mégawatts [MW]",
            min_value=10.0, max_value=500.0, value=100.0, step=10.0,
            key="slider_p_tab6"
        )
    with col_t6_2:
        tension_transport_kv = st.slider(
            "Tension de la ligne de transport en Kilovolts [kV]",
            min_value=20.0, max_value=400.0, value=20.0, step=10.0,
            key="slider_u_tab6"
        )

    # Modélisation physique
    # Résistance totale de la ligne fixe à 10 Ohms pour l'étude comparative
    r_ligne = 10.0
    
    # Conversion en unités SI (Watts et Volts)
    puissance_w = puissance_centrale_mw * 1e6
    tension_v = tension_transport_kv * 1e3
    
    # Calcul de l'intensité : I = P / U
    intensite_ligne = puissance_w / tension_v
    
    # Calcul des pertes par effet Joule : P_perte = R * I²
    puissance_perdue_w = r_ligne * (intensite_ligne ** 2)
    puissance_perdue_mw = puissance_perdue_w / 1e6
    
    # Calcul du rendement du transport
    rendement = ((puissance_w - puissance_perdue_w) / puissance_w) * 100.0
    if rendement < 0.0:
        rendement = 0.0

    # Affichage des métriques de diagnostic
    col_m6_1, col_m6_2, col_m6_3 = st.columns(3)
    with col_m6_1:
        st.metric(label="Intensité dans les câbles", value=f"{intensite_ligne:.1f} A")
    with col_m6_2:
        if puissance_perdue_mw > (puissance_centrale_mw * 0.5):
            st.metric(label="Puissance perdue (Chaleur)", value=f"{puissance_perdue_mw:.2f} MW", delta="Pertes critiques !", delta_color="inverse")
        else:
            st.metric(label="Puissance perdue (Chaleur)", value=f"{puissance_perdue_mw:.2f} MW")
    with col_m6_3:
        st.metric(label="Rendement de la ligne", value=f"{rendement:.1f} %")

    # Génération des données pour tracer le graphique d'optimisation
    tensions_courbe_kv = np.linspace(20, 400, 100)
    intensites_courbe = puissance_w / (tensions_courbe_kv * 1e3)
    pertes_courbe_mw = (r_ligne * (intensites_courbe ** 2)) / 1e6

    df_transport = pd.DataFrame({
        "Tension de la ligne (kV)": tensions_courbe_kv,
        "Puissance perdue (MW)": pertes_courbe_mw
    })

    # Affichage de la courbe caractéristique native
    st.line_chart(df_transport, x="Tension de la ligne (kV)", y="Puissance perdue (MW)")
    
    if tension_transport_kv < 100.0:
        st.warning("Constat : À basse tension, l'intensité est trop forte. Les câbles chauffent excessivement et le rendement s'effondre.")
    else:
        st.success("Constat : À Très Haute Tension (THT), l'intensité est minime. Les pertes par effet Joule sont négligeables, le transport est optimisé.")

    st.divider()

    # --- SECTION 3 : ZONE DE QUIZ ET VERROUILLAGE DE L'ATELIER 6 ---
    if "suite_verrouille_tab6" not in st.session_state:
        st.session_state.suite_verrouille_tab6 = False
    verrou_at6 = st.session_state.suite_verrouille_tab6

    # Appel du module de questions spécifique à l'onglet 6
    afficher_atelier_transport_tension(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Transport d'énergie.",
        key="check_certif_ttrans_final_net",
        disabled=verrou_at6,
    )

    # Bloc de correction et calcul des notes
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_tension_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            if "ordre_quiz_tab6_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_aleatoire:
                    reponse_eleve = st.session_state.get(f"ten_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q6 += 1.0

            score_t6 = 0.0
            if "champs_tr_tension" in st.session_state:
                for ligne in st.session_state.champs_tr_tension:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(cle, "Choisir...") == attendu:
                        score_t6 += 1.0

            st.session_state.score_suite6_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6 = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6 = True
            st.rerun()

    # --- SECTION 4 : COMPILATION DU BILAN HTML POUR L'ONGLET 6 ---
    if st.session_state.get("suite_verrouille_tab6", False):
        scr1_t6 = st.session_state.get("score_suite6_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER LIGNES HAUTE TENSION SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_t_transport = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Réseau Électrique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #16a34a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #15803d; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 6 : Transport réseau, effet Joule et très haute tension</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #16a34a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s_t6:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab6_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_aleatoire, 1):
                saisie = st.session_state.get(f"ten_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_t_transport += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_t_transport += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t6 = preparer_nom_fichier("Rapport_Transport_Tension").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_t_transport,
            file_name=nom_fichier_html_t6,
            mime="text/html",
            use_container_width=True
        )

