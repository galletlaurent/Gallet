
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application intensité électrique",
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
st.title("Application  intensité électrique")
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
    "Intensité dans les circuits en série",
    "Intensité dans les circuits en dérivation",
    "La loi d'ohm",
    "Les conducteurs d'électrcités"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]



def afficher_atelier_conducteurs(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Conducteurs et Isolants) sur deux colonnes."""
    import random

    questions_cond_sources = [
        {"id": "qcn1", "q": "Lequel de ces matériaux est le meilleur conducteur électrique ?", "options": ["Le cuivre", "Le verre", "Le plastique"], "rep": "Le cuivre"},
        {"id": "qcn2", "q": "Quel matériau utilise-t-on pour envelopper et isoler les fils électriques ?", "options": ["Le plastique", "L'aluminium", "Le fer"], "rep": "Le plastique"},
        {"id": "qcn3", "q": "La mine d'un crayon en graphite (carbone) est un matériau :", "options": ["Conducteur", "Isolant", "Liquide"], "rep": "Conducteur"},
        {"id": "qcn4", "q": "Pourquoi l'or et l'argent ne sont-ils pas utilisés pour les câbles domestiques ?", "options": ["Ils sont trop précieux et coûteux", "Ils sont de mauvais conducteurs", "Ils fondent trop vite"], "rep": "Ils sont trop précieux et coûteux"},
        {"id": "qcn5", "q": "Dans un métal conducteur, qu'est-ce qui se déplace pour créer le courant ?", "options": ["Les électrons libres", "Les molécules d'air", "Les noyaux atomiques"], "rep": "Les électrons libres"},
        {"id": "qcn6", "q": "L'eau pure distillée (sans aucun sel minéral) se comporte comme :", "options": ["Un isolant", "Un excellent conducteur", "Un métal"], "rep": "Un isolant"},
        {"id": "qcn7", "q": "Ajouter du sel dans de l'eau pure a pour conséquence de la rendre :", "options": ["Conductrice grâce aux ions", "Isolante", "Acide"], "rep": "Conductrice grâce aux ions"},
        {"id": "qcn8", "q": "Le corps humain est considéré à l'état physique comme :", "options": ["Un conducteur faible mais dangereux", "Un isolant total", "Un métal de transition"], "rep": "Un conducteur faible mais dangereux"},
        {"id": "qcn9", "q": "Quel élément naturel, lorsqu'il est sec, sert d'isolant mais devient conducteur s'il est mouillé ?", "options": ["Le bois", "Le verre", "Le cuivre"], "rep": "Le bois"},
        {"id": "qcn10", "q": "Le verre est un excellent isolant électrique. Cependant, s'il est chauffé jusqu'à fusion (liquide), il devient :", "options": ["Conducteur", "Plus isolant encore", "Un aimant"], "rep": "Conducteur"}
    ]

    if "ordre_quiz_tab6_aleatoire" not in st.session_state:
        random.shuffle(questions_cond_sources)
        st.session_state.ordre_quiz_tab6_aleatoire = questions_cond_sources

    champs_c = [
        ("1. Dans les métaux solidifiés, le courant provient des électrons ..........", ["Choisir...", "libres", "liés"], "libres", "cond_t1_final"),
        ("2. Les lignes électriques de nos habitations intègrent des fils de ..........", ["Choisir...", "cuivre", "verre"], "cuivre", "cond_t2_final"),
        ("3. La gaine protectrice externe des câbles souples est faite de ..........", ["Choisir...", "plastique", "fer"], "plastique", "cond_t3_final"),
        ("4. Les équipements de protection individuelle en gomme .......... le flux.", ["Choisir...", "bloquent", "facilitent"], "bloquent", "cond_t4_final"),
        ("5. Dans les solutions liquides, les charges mobiles s'appellent des ..........", ["Choisir...", "ions", "électrons"], "ions", "cond_t5_final"),
        ("6. La mine de crayon conduit l'électricité car elle contient du ..........", ["Choisir...", "carbone", "soufre"], "carbone", "cond_t6_final"),
        ("7. Porter des gants adaptés constitue une consigne élémentaire de ..........", ["Choisir...", "sécurité", "vitesse"], "sécurité", "cond_t7_final"),
        ("8. Le danger d'électrisation grandit si l'environnement s'avère ..........", ["Choisir...", "humide", "sec"], "humide", "cond_t8_final"),
        ("9. L'aluminium, le zinc et l'argent font partie de la grande famille des ..........", ["Choisir...", "métaux", "isolants"], "métaux", "cond_t9_final"),
        ("10. La faculté d'un matériau à propager un flux de charges s'appelle la ..........", ["Choisir...", "conductivité", "tension"], "conductivité", "cond_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz de Tri (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"cond_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de Cours (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_c:
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_loi_ohm(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Loi d'Ohm) sur deux colonnes."""
    import random

    questions_ohm_sources = [
        {
            "id": "qo1",
            "q": "Quelle est la formule correcte de la loi d'Ohm ?",
            "options": ["U = R x I", "I = R x U", "R = U x I"],
            "rep": "U = R x I"
        },
        {
            "id": "qo2",
            "q": "Quelle est l'unité de mesure de la résistance électrique ?",
            "options": ["L'ohm", "Le volt", "L'ampère"],
            "rep": "L'ohm"
        },
        {
            "id": "qo3",
            "q": "Si R = 100 Ω et I = 0,2 A, que vaut la tension U ?",
            "options": ["20 V", "10 V", "500 V"],
            "rep": "20 V"
        },
        {
            "id": "qo4",
            "q": "Si U = 12 V et R = 40 Ω, que vaut l'intensité I ?",
            "options": ["0,3 A", "3,33 A", "480 A"],
            "rep": "0,3 A"
        },
        {
            "id": "qo5",
            "q": "Si U = 6 V et I = 0,1 A, que vaut la valeur de la résistance R ?",
            "options": ["60 Ω", "0,6 Ω", "6 Ω"],
            "rep": "60 Ω"
        },
        {
            "id": "qo6",
            "q": "Graphiquement, la caractéristique U = f(I) d'une résistance est :",
            "options": ["Une droite passant par l'origine", "Une courbe parabolique", "Une droite horizontale"],
            "rep": "Une droite passant par l'origine"
        },
        {
            "id": "qo7",
            "q": "Si la tension aux bornes d'une résistance double, l'intensité :",
            "options": ["Double également", "Reste identique", "Est divisée par deux"],
            "rep": "Double également"
        },
        {
            "id": "qo8",
            "q": "Que représente le coefficient directeur de la droite caractéristique U = f(I) ?",
            "options": ["La valeur de la résistance R", "La puissance électrique", "La tension maximale"],
            "rep": "La valeur de la résistance R"
        },
        {
            "id": "qo9",
            "q": "Pour exprimer une intensité de 25 mA dans la formule, quelle valeur écrit-on ?",
            "options": ["0,025 A", "0,25 A", "25 A"],
            "rep": "0,025 A"
        },
        {
            "id": "qo10",
            "q": "Comment varie l'intensité si la résistance augmente pour une tension fixe ?",
            "options": ["L'intensité diminue", "L'intensité augmente", "L'intensité reste constante"],
            "rep": "L'intensité diminue"
        }
    ]

    if "ordre_quiz_tab5_aleatoire" not in st.session_state:
        random.shuffle(questions_ohm_sources)
        st.session_state.ordre_quiz_tab5_aleatoire = questions_ohm_sources

    champs_o = [
        ("1. La tension aux bornes d'un dipôle passif est .......... à l'intensité.", ["Choisir...", "proportionnelle", "inverse"], "proportionnelle", "ohm_t1_final"),
        ("2. La courbe de la caractéristique représente une .......... parfaite.", ["Choisir...", "droite", "ellipse"], "droite", "ohm_t2_final"),
        ("3. Cette droite passe obligatoirement par l'.......... du repère.", ["Choisir...", "origine", "axe"], "origine", "ohm_t3_final"),
        ("4. Pour trouver la tension, le produit R x I est ..........", ["Choisir...", "multiplié", "soustrait"], "multiplié", "ohm_t4_final"),
        ("5. Pour trouver l'intensité, la tension se retrouve .......... par R.", ["Choisir...", "divisée", "additionnée"], "divisée", "ohm_t5_final"),
        ("6. La lettre majuscule A symbolise l'unité nommée l'..........", ["Choisir...", "ampère", "ohm"], "ampère", "ohm_t6_final"),
        ("7. La lettre majuscule V désigne pour sa part le ..........", ["Choisir...", "volt", "watt"], "volt", "ohm_t7_final"),
        ("8. Une résistance est également appelée un .......... ohmique.", ["Choisir...", "conducteur", "isolant"], "conducteur", "ohm_t8_final"),
        ("9. Augmenter le frein d'un matériau au passage du flux .......... l'intensité.", ["Choisir...", "diminue", "accélère"], "diminue", "ohm_t9_final"),
        ("10. La valeur d'une résistance s'identifie au coefficient ..........", ["Choisir...", "directeur", "négatif"], "directeur", "ohm_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz de Calcul (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ohm_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Graphique (Texte à trous - 10 cases - 10 pts)")
        # Cette boucle accepte 3 ou 4 éléments par ligne sans jamais faire planter Streamlit
        for ligne in champs_o:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]  # Récupère automatiquement la clé de session située à la toute fin
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_circuit_derivation(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Circuit en dérivation) sur deux colonnes."""
    import random

    questions_derivation_sources = [
        {"id": "qd1", "q": "Comment appelle-t-il le point de connexion où se rejoignent au moins trois fils électriques ?", "options": ["Un nœud", "Une boucle", "Une branche"], "rep": "Un nœud"},
        {"id": "qd2", "q": "Quelle loi régit les courants au niveau d'une intersection dans un montage en parallèle ?", "options": ["La loi des nœuds", "La loi d'unicité", "La loi d'Ohm"], "rep": "La loi des nœuds"},
        {"id": "qd3", "q": "Si une branche contient une lampe grillée, les dipôles des autres branches :", "options": ["Continuent de fonctionner normalement", "S'éteignent instantanément", "Grillent à leur tour"], "rep": "Continuent de fonctionner normalement"},
        {"id": "qd4", "q": "L'intensité principale vaut 0,8 A et la branche 1 consomme 0,3 A. Que vaut l'intensité de la branche 2 ?", "options": ["0,5 A", "1,1 A", "0,24 A"], "rep": "0,5 A"},
        {"id": "qd5", "q": "Comment appelle-t-on la portion de circuit contenant le générateur ?", "options": ["La branche principale", "La branche dérivée", "Le nœud central"], "rep": "La branche principale"},
        {"id": "qd6", "q": "Dans notre simulation, ajouter un dipôle plus puissant (résistance plus faible) en branche 2 a pour effet de :", "options": ["Faire grimper le courant principal Ig", "Faire chuter le courant principal Ig", "Diminuer l'intensité de la branche 1"], "rep": "Faire grimper le courant principal Ig"},
        {"id": "qd7", "q": "Si deux lampes identiques sont placées en dérivation, l'intensité totale délivrée par le générateur se trouve :", "options": ["Partagée équitablement entre les deux lampes", "Concentrée dans la première lampe", "Doublée dans chaque lampe"], "rep": "Partagée équitablement entre les deux lampes"},
        {"id": "qd8", "q": "Quel terme qualifie un circuit dont les composants sont montés les uns en face des autres sur des lignes distinctes ?", "options": ["En parallèle (dérivation)", "En série", "En court-circuit"], "rep": "En parallèle (dérivation)"},
        {"id": "qd9", "q": "La formule mathématique représentant la répartition du courant pour trois branches en dérivation est :", "options": ["Ig = I1 + I2 + I3", "Ig = I1 = I2 = I3", "Ig = I1 - I2 - I3"], "rep": "Ig = I1 + I2 + I3"},
        {"id": "qd10", "q": "Pourquoi le courant électrique total augmente-t-il lorsque l'on ajoute de nouvelles branches en dérivation ?", "options": ["Car chaque nouvelle branche demande du courant supplémentaire au générateur", "Car la tension générale augmente", "Car les fils chauffent"], "rep": "Car chaque nouvelle branche demande du courant supplémentaire au générateur"}
    ]

    if "ordre_quiz_tab4_aleatoire" not in st.session_state:
        random.shuffle(questions_derivation_sources)
        st.session_state.ordre_quiz_tab4_aleatoire = questions_derivation_sources

    champs_d = [
        ("1. Le point de jonction d'au moins trois conducteurs est un ..........", ["Choisir...", "nœud", "boucle"], "der_t1_final"),
        ("2. La loi d'additivité se nomme également la loi des ..........", ["Choisir...", "nœuds", "mailles"], "der_t2_final"),
        ("3. Le courant principal équivaut à la .......... des courants dérivés.", ["Choisir...", "somme", "différence"], "somme", "der_t3_final"),
        ("4. En dérivation, les différentes boucles de courant sont ..........", ["Choisir...", "indépendantes", "liées"], "indépendantes", "der_t4_final"),
        ("5. La ligne reliée en direct avec la pile est la ligne ..........", ["Choisir...", "principale", "secondaire"], "principale", "der_t5_final"),
        ("6. Les lignes parallèles secondaires sont qualifiées de ..........", ["Choisir...", "dérivées", "série"], "dérivées", "der_t6_final"),
        ("7. Multiplier le nombre de récepteurs en parallèle .......... l'intensité Ig.", ["Choisir...", "augmente", "diminue"], "augmente", "der_t7_final"),
        ("8. Le terme dérivation est synonyme de branchement en ..........", ["Choisir...", "parallèle", "série"], "parallèle", "der_t8_final"),
        ("9. Arrivé à une intersection de câbles, le courant se ..........", ["Choisir...", "divise", "bloque"], "divise", "der_t9_final"),
        ("10. Si un récepteur tombe en panne, l'autre branche .......... sa tâche.", ["Choisir...", "continue", "arrête"], "continue", "der_t10_final")
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Méthode (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"der_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        # Cette boucle accepte 3 ou 4 éléments par ligne sans jamais lever de ValueError
        for ligne in champs_d:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]  # Récupère automatiquement la clé de session à la fin de la ligne
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_circuit_serie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Circuit en série) sur deux colonnes."""
    import random

    questions_serie_sources = [
        {"id": "qs1", "q": "Combien de boucles de courant comporte un circuit en série ?", "options": ["Une seule boucle", "Deux boucles", "Plus de trois boucles"], "rep": "Une seule boucle"},
        {"id": "qs2", "q": "Si une lampe grille dans un circuit en série, que se passe-t-il pour les autres ?", "options": ["Elles s'éteignent toutes", "Elles restent allumées normalement", "Elles éclairent plus fort"], "rep": "Elles s'éteignent toutes"},
        {"id": "qs3", "q": "Quelle loi régit la valeur de l'intensité dans un circuit en série ?", "options": ["La loi d'unicité de l'intensité", "La loi d'additivité des intensités", "La loi des nœuds"], "rep": "La loi d'unicité de l'intensité"},
        {"id": "qs4", "q": "Si le générateur délivre 0,3 A, quelle intensité traverse la seconde lampe en série ?", "options": ["0,3 A", "0,15 A", "0,6 A"], "rep": "0,3 A"},
        {"id": "qs5", "q": "Si on modifie l'ordre des lampes dans la boucle en série, l'intensité :", "options": ["Reste strictement inchangée", "Augmente fortement", "Devient nulle"], "rep": "Reste strictement inchangée"},
        {"id": "qs6", "q": "Qu'arrive-t-il à l'intensité globale si on ajoute une troisième lampe en série ?", "options": ["Elle diminue", "Elle augmente", "Elle reste identique"], "rep": "Elle diminue"},
        {"id": "qs7", "q": "Dans la caricature ferroviaire, à quoi correspondent les électrons ?", "options": ["Aux wagons du train", "Aux rails", "À la gare de triage"], "rep": "Aux wagons du train"},
        {"id": "qs8", "q": "Dans la caricature ferroviaire, le générateur est comparé à :", "options": ["La locomotive qui pousse le train", "Le passager", "Le feu de signalisation"], "rep": "La locomotive qui pousse le train"},
        {"id": "qs9", "q": "Si un circuit en série possède une lampe dévissée, le circuit est dit :", "options": ["Ouvert", "Fermé", "En court-circuit"], "rep": "Ouvert"},
        {"id": "qs10", "q": "L'expression mathématique correcte de la loi en série avec deux lampes est :", "options": ["Ig = I1 = I2", "Ig = I1 + I2", "Ig = I1 - I2"], "rep": "Ig = I1 = I2"}
    ]

    if "ordre_quiz_tab3_aleatoire" not in st.session_state:
        random.shuffle(questions_serie_sources)
        st.session_state.ordre_quiz_tab3_aleatoire = questions_serie_sources

    champs_s = [
        ("1. Un circuit en série ne possède qu'une unique ..........", ["Choisir...", "boucle", "dérivation"], "ser_t1_final"),
        ("2. L'égalité du courant en tout point s'appelle la loi d'..........", ["Choisir...", "unicité", "additivité"], "ser_t2_final"),
        ("3. Dans ce montage, l'intensité totale est .......... partout.", ["Choisir...", "égale", "différente"], "ser_t3_final"),
        ("4. Si l'un des composants est dévissé, les autres s'..........", ["Choisir...", "éteignent", "animent"], "ser_t4_final"),
        ("5. Ajouter des récepteurs en série fait que l'intensité ..........", ["Choisir...", "diminue", "augmente"], "diminue", "ser_t5_final"),
        ("6. La place occupée par un dipôle dans le circuit est ..........", ["Choisir...", "indépendant", "crucial"], "indépendant", "ser_t6_final"),
        ("7. Le générateur agit comme une .......... poussant le flux.", ["Choisir...", "locomotive", "voie"], "locomotive", "ser_t7_final"),
        ("8. Le débit de charge correspond graphiquement à la ..........", ["Choisir...", "vitesse", "longueur"], "vitesse", "ser_t8_final"),
        ("9. Une interruption physique transforme la ligne en chaîne ..........", ["Choisir...", "ouverte", "fermée"], "ouverte", "ser_t9_final"),
        ("10. Quel que soit le point de mesure, le résultat reste ..........", ["Choisir...", "identique", "variable"], "identique", "ser_t10_final")
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Conceptuel (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ser_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse d'Application (Texte à trous - 10 cases - 10 pts)")
        # Cette boucle accepte 3 ou 4 éléments par ligne sans jamais planter
        for ligne in champs_s:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]  # Prend automatiquement le dernier élément comme clé de session
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_appareil_mesure(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Appareil de mesure) sur deux colonnes."""
    
    questions_mesure_sources = [
        {
            "id": "qm1",
            "q": "Comment doit être branché un ampèremètre dans un circuit électrique ?",
            "options": ["En série", "En dérivation (parallèle)", "Peu importe le sens"],
            "rep": "En série"
        },
        {
            "id": "qm2",
            "q": "Par quelle borne le courant électrique doit-il entrer dans l'ampèremètre ?",
            "options": ["La borne A ou 10A", "La borne COM", "La borne V"],
            "rep": "La borne A ou 10A"
        },
        {
            "id": "qm3",
            "q": "Par quelle borne le courant électrique doit-il sortir de l'ampèremètre ?",
            "options": ["La borne COM", "La borne A", "La borne de la résistance"],
            "rep": "La borne COM"
        },
        {
            "id": "qm4",
            "q": "Quel symbole représente l'ampèremètre sur un schéma normalisé ?",
            "options": ["Un cercle contenant la lettre A", "Un rectangle contenant la lettre R", "Un cercle contenant la lettre V"],
            "rep": "Un cercle contenant la lettre A"
        },
        {
            "id": "qm5",
            "q": "Sur un appareil analogique à aiguille, qu'indique la graduation totale du cadran ?",
            "options": ["L'échelle", "Le calibre", "La lecture"],
            "rep": "L'échelle"
        },
        {
            "id": "qm6",
            "q": "Quelle formule permet de calculer l'intensité sur un cadran analogique ?",
            "options": ["(Calibre x Lecture) / Échelle", "(Calibre x Échelle) / Lecture", "Calibre + Lecture - Échelle"],
            "rep": "(Calibre x Lecture) / Échelle"
        },
        {
            "id": "qm7",
            "q": "Quel est le risque de choisir un calibre trop petit pour la mesure ?",
            "options": ["Endommager ou griller le fusible de l'appareil", "Bloquer le générateur", "Diminuer l'intensité totale"],
            "rep": "Endommager ou griller le fusible de l'appareil"
        },
        {
            "id": "qm8",
            "q": "Quel calibre doit-on toujours sélectionner en premier par sécurité ?",
            "options": ["Le calibre le plus grand", "Le calibre le plus petit", "Un calibre au hasard"],
            "rep": "Le calibre le plus grand"
        },
        {
            "id": "qm9",
            "q": "Quelle unité principale mesure l'intensité du courant électrique ?",
            "options": ["L'ampère", "Le volt", "L'ohm"],
            "rep": "L'ampère"
        },
        {
            "id": "qm10",
            "q": "Quel type d'appareil moderne évite d'appliquer la formule de calcul du cadran ?",
            "options": ["Le multimètre numérique", "La pile de Volta", "L'ampèremètre analogique"],
            "rep": "Le multimètre numérique"
        }
    ]

    if "ordre_quiz_tab2_aleatoire" not in st.session_state:
        random.shuffle(questions_mesure_sources)
        st.session_state.ordre_quiz_tab2_aleatoire = questions_mesure_sources

    champs_m = [
        ("1. Pour mesurer le courant, l'ampèremètre s'insère en ..........", ["Choisir...", "série", "dérivation"], "série", "mes_t1_final"),
        ("2. Les anciens ampèremètres affichent la valeur via une ..........", ["Choisir...", "aiguille", "diode"], "aiguille", "mes_t2_final"),
        ("3. Les nouveaux modèles possèdent un écran d'affichage ..........", ["Choisir...", "numérique", "lumineux"], "numérique", "mes_t3_final"),
        ("4. Le symbole de l'ampèremètre s'inscrit au centre d'un ..........", ["Choisir...", "cercle", "carré"], "cercle", "mes_t4_final"),
        ("5. La borne finale de sortie du courant est identifiée par ..........", ["Choisir...", "COM", "10A"], "COM", "mes_t5_final"),
        ("6. La valeur maximale mesurable choisie s'appelle le ..........", ["Choisir...", "calibre", "stator"], "calibre", "mes_t6_final"),
        ("7. La lettre A désigne l'unité de mesure nommée l'..........", ["Choisir...", "ampère", "volt"], "ampère", "mes_t7_final"),
        ("8. Le total des lignes du cadran donne la valeur de la haute ..........", ["Choisir...", "graduation", "tension"], "graduation", "mes_t8_final"),
        ("9. Choisir le bon calibre évite de dépasser la capacité ..........", ["Choisir...", "maximale", "minimale"], "maximale", "mes_t9_final"),
        ("10. L'outil polyvalent regroupant plusieurs fonctions est le ..........", ["Choisir...", "multimètre", "rotor"], "multimètre", "mes_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"mes_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Méthodologique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_m:
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_histoire_electricite(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Histoire et Découverte) sur deux colonnes."""
    
    # 10 questions axées sur l'histoire de l'électricité et ses machines
    questions_histoire_sources = [
        {
            "id": "qh1", 
            "q": "Quelle est l'origine étymologique du mot électricité ?", 
            "options": ["Le mot grec désigne l'ambre jaune", "Le mot latin désigne l'étincelle", "Un mot celte pour le feu"], 
            "rep": "Le mot grec désigne l'ambre jaune"
        },
        {
            "id": "qh2", 
            "q": "Quelle observation de l'Antiquité est à l'origine de cette découverte ?", 
            "options": ["Le frottement de l'ambre qui attire des plumes", "La foudre sur les arbres", "Les poissons électriques du Nil"], 
            "rep": "Le frottement de l'ambre qui attire des plumes"
        },
        {
            "id": "qh3", 
            "q": "Quel savant est célèbre pour son expérience du paratonnerre et du cerf-volant ?", 
            "options": ["Benjamin Franklin", "Alessandro Volta", "Michael Faraday"], 
            "rep": "Benjamin Franklin"
        },
        {
            "id": "qh4", 
            "q": "Sur quel animal Luigi Galvani a-t-il mis en évidence l'électricité biologique ?", 
            "options": ["La grenouille", "Le poisson-chat", "La chauve-souris"], 
            "rep": "La grenouille"
        },
        {
            "id": "qh5", 
            "q": "Quelle invention de l'année 1800 produit le premier courant continu stable ?", 
            "options": ["La pile de Volta", "La bouteille de Leyde", "La dynamo de Gramme"], 
            "rep": "La pile de Volta"
        },
        {
            "id": "qh6", 
            "q": "Quels métaux constituent les disques empilés de la première pile électrique ?", 
            "options": ["Le cuivre et le zinc", "L'or et l'argent", "Le fer et le plomb"], 
            "rep": "Le cuivre et le zinc"
        },
        {
            "id": "qh7", 
            "q": "Quel phénomène physique, découvert par Faraday, est utilisé par les dynamos ?", 
            "options": ["L'induction électromagnétique", "L'effet Joule", "L'effet thermoélectrique"], 
            "rep": "L'induction électromagnétique"
        },
        {
            "id": "qh8", 
            "q": "Quelle est la particularité de la dynamo industrielle perfectionnée par Gramme ?", 
            "options": ["Elle produit un courant continu", "Elle produit un courant alternatif", "Elle accumule de l'électricité statique"], 
            "rep": "Elle produit un courant continu"
        },
        {
            "id": "qh9", 
            "q": "Quelle machine moderne trouve-t-on dans les centrales électriques actuelles ?", 
            "options": ["L'alternateur", "La machine électrostatique", "La pile chimique"], 
            "rep": "L'alternateur"
        },
        {
            "id": "qh10", 
            "q": "Quelles sont les deux parties principales d'un alternateur ?", 
            "options": ["Le rotor et le stator", "L'anode et la cathode", "Le plateau et le frottisseur"], 
            "rep": "Le rotor et le stator"
        },
    ]

    # Mélange aléatoire des questions au premier chargement
    if "ordre_quiz_tab1_aleatoire" not in st.session_state:
        random.shuffle(questions_histoire_sources)
        st.session_state.ordre_quiz_tab1_aleatoire = questions_histoire_sources

    # 10 phrases à trous adaptées à l'histoire et aux machines
    champs_h = [
        ("1. L'ambre frotté produit les premières observations de l'électricité ..........", ["Choisir...", "statique", "dynamique"], "statique", "hist_t1_final"),
        ("2. Benjamin Franklin a démontré la nature électrique de la ...........", ["Choisir...", "foudre", "chaleur"], "foudre", "hist_t2_final"),
        ("3. La pile de Alessandro Volta fonctionne grâce à une réaction ...........", ["Choisir...", "chimique", "magnétique"], "chimique", "hist_t3_final"),
        ("4. Les disques de la première pile étaient séparés par un tissu imbibé d'eau ..........", ["Choisir...", "salée", "distillée"], "salée", "hist_t4_final"),
        ("5. La première machine rotative industrielle mécanique s'appelle la ..........", ["Choisir...", "dynamo", "bouteille"], "dynamo", "hist_t5_final"),
        ("6. Michael Faraday est le découvreur de l'.......... électromagnétique.", ["Choisir...", "induction", "attraction"], "induction", "hist_t6_final"),
        ("7. L'alternateur moderne génère principalement du courant ..........", ["Choisir...", "alternatif", "continu"], "alternatif", "hist_t7_final"),
        ("8. Dans un alternateur, la partie mobile qui tourne est appelée le ..........", ["Choisir...", "rotor", "stator"], "rotor", "hist_t8_final"),
        ("9. La partie fixe contenant les bobines de cuivre s'appelle le ..........", ["Choisir...", "stator", "aimant"], "stator", "hist_t9_final"),
        ("10. Les centrales hydroélectriques ou nucléaires exploitent toutes un ..........", ["Choisir...", "alternateur", "condensateur"], "alternateur", "hist_t10_final"),
    ]

    # Affichage sur deux colonnes
    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Histoire et Découverte (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hist_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse sur les Machines (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_h:
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

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
    st.header("Histoire et découverte de l'électricité")
    
    # --- SECTION 1 : L'HISTOIRE ET LA DÉCOUVERTE ---
    st.subheader("La découverte de l'électricité")
    st.write(
        "L'électricité n'a pas été inventée, elle a été découverte et comprise au fil des siècles. "
        "Le mot provient du grec 'elektron' qui désigne l'ambre jaune. Dès l'Antiquité, les humains "
        "avaient remarqué qu'en frottant de l'ambre, celui-ci attirait des objets légers comme des plumes. "
        "Il s'agissait des premières observations de l'électricité statique."
    )
    
    st.write(
        "Les bases scientifiques modernes ont été posées à partir du dix-huitième siècle grâce aux travaux "
        "de chercheurs comme Benjamin Franklin et son célèbre paratonnerre, ou Luigi Galvani qui a mis en "
        "évidence les phénomènes bioélectriques sur les muscles des grenouilles."
    )
    
    # --- SECTION 2 : LES MACHINES QUI PRODUISENT DE L'ÉLECTRICITÉ ---
    st.subheader("Les machines de production d'électricité")
    st.write(
        "La production d'électricité repose sur l'évolution de différentes machines thermiques, "
        "chimiques ou magnétiques. Voici les grandes étapes techniques de cette histoire :"
    )
    
    # Machine 1
    st.write("**1. Les machines électrostatiques (Dix-huitième siècle)**")
    st.write(
        "Ces premières machines utilisaient le frottement de globes de verre ou de plateaux pour accumuler "
        "des charges électriques de haute tension, permettant de générer des étincelles impressionnantes."
    )
    try:
        st.image("machine_statique.jpg", caption="Machine électrostatique à plateau de verre")
    except Exception:
        st.warning("L'image 'machine_statique.jpg' est introuvable dans le répertoire.")
        
    st.divider()

    # Machine 2
    st.write("**2. La pile de Volta (1800)**")
    st.write(
        "Inventée par Alessandro Volta, cette pile constitue le premier générateur de courant continu stable. "
        "Elle fonctionne par une réaction chimique provoquée par l'empilement de disques de zinc et de cuivre "
        "séparés par des tissus imbibés d'eau salée."
    )
    try:
        st.image("pile_volta.jpg", caption="Représentation de la première pile électrique d'Alessandro Volta")
    except Exception:
        st.warning("L'image 'pile_volta.jpg' est introuvable dans le répertoire.")

    st.divider()

    # Machine 3
    st.write("**3. La dynamo de Gramme (1869)**")
    st.write(
        "Basée sur la découverte de l'induction électromagnétique par Michael Faraday, Zénobe Gramme perfectionne "
        "la dynamo. C'est la première machine rotative industrielle capable de transformer l'énergie mécanique "
        "en énergie électrique sous forme de courant continu."
    )
    try:
        st.image("dynamos.jpg", caption="Dynamo industrielle du dix-neuvième siècle")
    except Exception:
        st.warning("L'image 'dynamos.jpg' est introuvable dans le répertoire.")

    st.divider()

    # Machine 4
    st.write("**4. L'alternateur moderne**")
    st.write(
        "Utilisé aujourd'hui dans les centrales nucléaires, hydroélectriques ou thermiques, l'alternateur produit "
        "du courant alternatif. Il utilise la rotation d'un aimant (rotor) à l'intérieur d'une bobine de cuivre "
        "(stator) pour générer des courants électriques à très grande échelle."
    )
    try:
        st.image("alternateur.jpg", caption="Vue en coupe d'un alternateur de production électrique")
    except Exception:
        st.warning("L'image 'alternateur.jpg' est introuvable dans le répertoire.")

    st.divider()
    st.write("---")        
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    # Appel de la fonction spécifique à l'histoire de l'électricité
    afficher_atelier_histoire_electricite(verrouille=verrou_at1)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # Case à cocher adaptée au thème
    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Histoire et Découverte.",
        key="check_certif_histoire_final_net",
        disabled=verrou_at1,
    )

    # --- BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            # Correction basée sur l'ordre aléatoire stocké dans l'onglet 1
            if "ordre_quiz_tab1_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_aleatoire:
                    reponse_eleve = st.session_state.get(f"hist_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # Correction des 10 trous de la synthèse sur les machines
            score_t1 = sum(
                [
                    st.session_state.get("hist_t1_final") == "statique",
                    st.session_state.get("hist_t2_final") == "foudre",
                    st.session_state.get("hist_t3_final") == "chimique",
                    st.session_state.get("hist_t4_final") == "salée",
                    st.session_state.get("hist_t5_final") == "dynamo",
                    st.session_state.get("hist_t6_final") == "induction",
                    st.session_state.get("hist_t7_final") == "alternatif",
                    st.session_state.get("hist_t8_final") == "rotor",
                    st.session_state.get("hist_t9_final") == "stator",
                    st.session_state.get("hist_t10_final") == "alternateur",
                ]
            )

            st.session_state.score_suite1_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1 = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 1 ---
    if st.session_state.get("suite_verrouille_tab1", False):
        scr1 = st.session_state.get("score_suite1_p1", 0.0)
        scr2 = st.session_state.get("score_suite1_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite1", 0.0)

        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER HISTOIRE ET DÉCOUVERTE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Electricite - {n_eleve}</title>
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
                <p>Atelier 1 : Histoire, découverte et machines de production d'électricité</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Histoire et Découverte : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse sur les machines : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Utilisation de l'ordre d'affichage propre à l'onglet 1 pour la génération du tableau HTML
        if "ordre_quiz_tab1_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
                saisie = st.session_state.get(f"hist_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_suites += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_suites += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html = preparer_nom_fichier("Rapport_Histoire_Electricite").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_suites,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )



with tab2:
    st.header("L'appareil de mesure de l'intensité : L'ampèremètre")
    
    # --- SECTION 1 : HISTORIQUE ET ÉVOLUTION ---
    st.subheader("Évolution des appareils de mesure")
    
    col_app1, col_app2 = st.columns(2)
    with col_app1:
        st.write("**Les anciens appareils : L'ampèremètre analogique**")
        st.write(
            "Les anciens ampèremètres utilisent une aiguille aimantée qui se déplace sur un cadran gradué. "
            "La déviation de l'aiguille est proportionnelle à l'intensité du courant qui traverse l'appareil."
        )
        try:
            st.image("ancien_amperemetre.jpg", caption="Ampèremètre analogique à aiguille")
        except Exception:
            st.warning("L'image 'ancien_amperemetre.jpg' est introuvable.")

    with col_app2:
        st.write("**Les nouveaux appareils : Le multimètre numérique**")
        st.write(
            "Aujourd'hui, on utilise des multimètres numériques configurés en ampèremètre (calibre A ou mA). "
            "La valeur de l'intensité s'affiche directement sur un écran à cristaux liquides, ce qui évite les erreurs de lecture."
        )
        try:
            st.image("multimetre_numerique.jpg", caption="Multimètre moderne en mode ampèremètre")
        except Exception:
            st.warning("L'image 'multimetre_numerique.jpg' est introuvable.")

    st.divider()

    # --- SECTION 2 : BRANCHEMENT ET SYMBOLE ---
    st.subheader("Branchement du circuit et symbole électrique")
    
    col_sym1, col_sym2 = st.columns(2)
    with col_sym1:
        st.write("**Le symbole normalisé**")
        st.write(
            "Dans un schéma électrique, l'ampèremètre est représenté par un cercle contenant la lettre majuscule A. "
            "Il possède deux bornes de connexion principales : la borne d'entrée (A ou 10A) et la borne de sortie (COM)."
        )
        try:
            st.image("symbole_amperemetre.jpg", caption="Symbole normalisé de l'ampèremètre")
        except Exception:
            st.warning("L'image 'symbole_amperemetre.jpg' est introuvable.")

    with col_sym2:
        st.write("**Comment placer l'appareil ?**")
        st.write(
            "Pour mesurer l'intensité qui traverse un dipôle, l'ampèremètre doit obligatoirement être branché **en série** "
            "dans le circuit. Le courant doit entrer par la borne A (ou 10A) et sortir par la borne COM."
        )
        try:
            st.image("branchement_amperemetre.jpg", caption="Schéma d'un branchement en série")
        except Exception:
            st.warning("L'image 'branchement_amperemetre.jpg' est introuvable.")

    st.divider()

    # --- SECTION 3 : LA LECTURE SUR APPAREIL ANALOGIQUE ---
    st.subheader("La méthode de lecture sur un appareil analogique")
    st.write(
        "Pour lire une valeur sur un ampèremètre à aiguille, on applique la formule mathématique suivante :\n\n"
        "**Intensité = (Calibre x Lecture) / Échelle**\n\n"
        "* **Le calibre** représente la valeur maximale que l'appareil peut mesurer sur la borne sélectionnée.\n"
        "* **La lecture** indique la position de l'aiguille sur le cadran.\n"
        "* **L'échelle** correspond au nombre total de graduations du cadran utilisé."
    )

    st.divider()

    # --- SECTION 4 : LE QUIZ ET LA CORRECTION DE L'ATELIER 2 ---
    if "suite_verrouille_tab2" not in st.session_state:
        st.session_state.suite_verrouille_tab2 = False
    verrou_at2 = st.session_state.suite_verrouille_tab2

    # Affichage du module de questions spécifique à l'onglet 2
    afficher_atelier_appareil_mesure(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Appareil de mesure.",
        key="check_certif_mesure_final_net",
        disabled=verrou_at2,
    )

    # Bouton de validation pour bloquer et générer les notes du Tab 2
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_aleatoire:
                    reponse_eleve = st.session_state.get(f"mes_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = sum(
                [
                    st.session_state.get("mes_t1_final") == "série",
                    st.session_state.get("mes_t2_final") == "aiguille",
                    st.session_state.get("mes_t3_final") == "numérique",
                    st.session_state.get("mes_t4_final") == "cercle",
                    st.session_state.get("mes_t5_final") == "COM",
                    st.session_state.get("mes_t6_final") == "calibre",
                    st.session_state.get("mes_t7_final") == "ampère",
                    st.session_state.get("mes_t8_final") == "graduation",
                    st.session_state.get("mes_t9_final") == "maximale",
                    st.session_state.get("mes_t10_final") == "multimètre",
                ]
            )

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
        st.success(f"ATELIER APPAREIL DE MESURE SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_mesure = f"""<!DOCTYPE html>
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
                <p>Atelier 2 : Appareils de mesure, branchements et lectures</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse Méthodologique : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 2. LA BOUCLE PEUT MAINTENANT AJOUTER LES LIGNES SANS ERREUR
        if "ordre_quiz_tab2_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
                saisie = st.session_state.get(f"mes_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mesure += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 3. FERMETURE ET BOUTON DE TÉLÉCHARGEMENT
        html_export_mesure += """
                </tbody>
            </table>
        </body>
        </html>
        """
                
            # Déclaration du bouton de téléchargement
        nom_fichier_html_t2 = preparer_nom_fichier("Rapport_Appareil_Mesure").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_mesure,
            file_name=nom_fichier_html_t2,
            mime="text/html",
            use_container_width=True
        )

with tab3:
    st.header("L'intensité dans les circuits en série")
    
    # --- SECTION 1 : EXPLICATION ET CARICATURE ---
    st.subheader("Qu'est-ce qu'un circuit en série ?")
    st.write(
        "Un circuit est dit en série lorsque les dipôles sont branchés les uns à la suite des autres, "
        "formant une seule et unique boucle de courant. Si un composant tombe en panne ou si une lampe est "
        "dévissée, le circuit s'ouvre et le courant ne passe plus nulle part : tous les autres dipôles s'éteignent."
    )
    
    col_car1, col_car2 = st.columns(2)
    with col_car1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre l'intensité en série, on peut imaginer une caricature avec un train sur un rail fermé. "
            "Le générateur est la locomotive qui pousse les électrons (les wagons). Comme il n'y a qu'une seule voie, "
            "le nombre de wagons qui passe par seconde est strictement le même en tout point du circuit. "
            "La vitesse du train ne change pas, peu importe où l'on se place sur la boucle."
        )
        try:
            st.image("caricature_serie.jpg", caption="Caricature du flux d'intensité dans une seule boucle")
        except Exception:
            st.warning("L'image 'caricature_serie.jpg' est introuvable.")

    with col_car2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "Sur un schéma normalisé, les ampèremètres placés avant, entre ou après les lampes indiquent "
            "exactement la même valeur. C'est la loi fondamentale de ce type de montage."
        )
        try:
            st.image("schema_loi_unicite.jpg", caption="Mesure de l'intensité en différents points")
        except Exception:
            st.warning("L'image 'schema_loi_unicite.jpg' est introuvable.")

    st.divider()

    # --- SECTION 2 : ANIMATION ET SIMULATION INTERACTIVE DYNAMIQUE ---
    st.subheader("Animation : Laboratoire de mesure en série")
    st.write(
        "Ajustez la tension du générateur et ajoutez un dipôle au circuit pour observer la modification "
        "du courant. Les trois ampèremètres virtuels se mettent à jour instantanément pour valider la loi."
    )

    # Commandes de l'animation
    col_anim1, col_anim2 = st.columns(2)
    with col_anim1:
        tension_serie = st.slider(
            "Tension du générateur (U) en Volts [V]",
            min_value=0.0,
            max_value=24.0,
            value=12.0,
            step=0.5,
            key="slider_tension_tab3"
        )
    with col_anim2:
        choix_dipole_serie = st.selectbox(
            "Choisir le dipôle supplémentaire à ajouter en série :",
            options=["Aucun (Lampe seule de 50 Ω)", "Résistance additionnelle (50 Ω)", "Moteur en série (70 Ω)", "Seconde Lampe (50 Ω)"],
            key="select_dipole_tab3"
        )

    # --- CALCULS SIMULATION SÉRIE ---
    # Résistance de base de la première lampe
    r_lampe1 = 50.0
    
    # Résistance additionnelle selon le choix
    if choix_dipole_serie == "Aucun (Lampe seule de 50 Ω)":
        r_total_serie = r_lampe1
    elif choix_dipole_serie == "Résistance additionnelle (50 Ω)":
        r_total_serie = r_lampe1 + 50.0
    elif choix_dipole_serie == "Moteur en série (70 Ω)":
        r_total_serie = r_lampe1 + 70.0
    else:  # Seconde Lampe
        r_total_serie = r_lampe1 + 50.0

    # Loi d'Ohm globale pour la boucle : I = U / R
    intensite_commune = tension_serie / r_total_serie if tension_serie > 0 else 0.0

    # Affichage des ampèremètres
    st.write("**Valeurs relevées par les ampèremètres de la boucle :**")
    col_mes1, col_mes2, col_mes3 = st.columns(3)
    with col_mes1:
        st.metric(label="Ampèremètre 1 (Sortie Générateur)", value=f"{intensite_commune:.3f} A")
    with col_mes2:
        st.metric(label="Ampèremètre 2 (Entre les dipôles)", value=f"{intensite_commune:.3f} A")
    with col_mes3:
        st.metric(label="Ampèremètre 3 (Retour Générateur)", value=f"{intensite_commune:.3f} A")

    # Schéma en caractères mis à jour dynamiquement
    nom_dipole_affiche = choix_dipole_serie.split(" (")[0]
    st.code(
        f"""
      +---[ Ampèremètre 1 : {intensite_commune:.3f} A ]---[ Générateur : {tension_serie:.1f} V ]---+

      |                                                                             |
      |                                                                             |
    [ Lampe 1 : 50 Ω ]                                                              |

      |                                                                             |
      |                                                                             |
      +---[ Ampèremètre 2 : {intensite_commune:.3f} A ]---[ {nom_dipole_affiche} ]---+

      |                                                                             |
      +-------------------------[ Ampèremètre 3 : {intensite_commune:.3f} A ]--------+
        """,
        language="text"
    )

    st.info(
        f"Loi d'unicité démontrée : L'intensité reste strictement égale à {intensite_commune:.3f} A "
        f"dans les trois ampèremètres de la boucle unique (Résistance totale du circuit : {r_total_serie:.0f} Ω)."
    )

    st.divider()

    # --- SECTION 3 : ZONE DE QUIZ ET COMMANDE DE VERROUILLAGE ---
    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3

    afficher_atelier_circuit_serie(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Circuit en série.",
        key="check_certif_serie_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_aleatoire:
                    reponse_eleve = st.session_state.get(f"ser_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            score_t3 = sum(
                [
                    st.session_state.get("ser_t1_final") == "boucle",
                    st.session_state.get("ser_t2_final") == "unicité",
                    st.session_state.get("ser_t3_final") == "égale",
                    st.session_state.get("ser_t4_final") == "éteignent",
                    st.session_state.get("ser_t5_final") == "diminue",
                    st.session_state.get("ser_t6_final") == "indépendant",
                    st.session_state.get("ser_t7_final") == "locomotive",
                    st.session_state.get("ser_t8_final") == "vitesse",
                    st.session_state.get("ser_t9_final") == "ouverte",
                    st.session_state.get("ser_t10_final") == "identique",
                ]
            )

            st.session_state.score_suite3_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3 = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("suite_verrouille_tab3", False):
        scr1_t3 = st.session_state.get("score_suite3_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER CIRCUIT EN SÉRIE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        # Reconstruction propre du squelette HTML et du bandeau d'entête
        html_export_serie = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Circuit en Série - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0284c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
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
                <p>Atelier 3 : Lois de l'intensité dans les circuits en série</p>
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

        # Alignement strict de la boucle de traitement des données de session
        if "ordre_quiz_tab3_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
                saisie = st.session_state.get(f"ser_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                
                # Injection correcte des balises de tableau HTML tr/td manquantes
                html_export_serie += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Fermeture des conteneurs sémantiques HTML
        html_export_serie += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Configuration finale sécurisée du bouton de téléchargement Streamlit
        nom_fichier_html_t3 = preparer_nom_fichier("Rapport_Circuit_Series").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_serie,
            file_name=nom_fichier_html_t3,
            mime="text/html",
            use_container_width=True
        )

with tab4:
    st.header("L'intensité dans les circuits en dérivation")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("Qu'est-ce qu'un circuit en dérivation ?")
    st.write(
        "Un circuit est dit en dérivation (ou en parallèle) lorsqu'il est composé de plusieurs boucles de courant "
        "branchées sur le même générateur. Les points de connexion où le courant se sépare ou se rassemble s'appellent des nœuds. "
        "Si un composant tombe en panne ou si une lampe est dévissée, le circuit reste fermé pour les autres branches : "
        "les autres dipôles continuent de fonctionner indépendamment."
    )
    
    col_der1, col_der2 = st.columns(2)
    with col_der1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre l'intensité en dérivation, on peut imaginer une caricature avec un fleuve qui se sépare "
            "en deux canaux différents avant de se rejoindre plus loin. Le générateur est la pompe principale. "
            "Le débit d'eau total (l'intensité principale) se divise en arrivant au premier croisement (le nœud). "
            "Chaque canal reçoit une quantité d'eau qui dépend de sa largeur, mais la somme des débits des deux "
            "canaux redonne exactement le débit de départ après le second croisement."
        )
        try:
            st.image("caricature_derivation.jpg", caption="Caricature du flux d'intensité se divisant aux nœuds")
        except Exception:
            st.warning("L'image 'caricature_derivation.jpg' est introuvable.")

    with col_der2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "Sur un schéma normalisé, l'ampèremètre placé dans la branche principale (Ig) indique une valeur égale "
            "à la somme des valeurs indiquées par les ampèremètres placés dans les branches dérivées (I1 et I2). "
            "C'est la loi fondamentale de ce type de montage, appelée la loi des nœuds."
        )
        try:
            st.image("schema_loi_noeuds.jpg", caption="Mesure de l'additivité des intensités aux nœuds")
        except Exception:
            st.warning("L'image 'schema_loi_noeuds.jpg' est introuvable.")
            
    st.write(
        "La somme des intensités des courants qui arrivent à un nœud est égale à la somme des intensités "
        "des courants qui en sortent. Pour un circuit simple à deux branches en parallèle, l'intensité de la "
        "branche principale (Ig) est égale à la somme des intensités des branches dérivées (I1 + I2) :\n\n"
        "**Ig = I1 + I2**"
    )

    st.divider()

    # --- SECTION 2 : ANIMATION ET SIMULATION DYNAMIQUE ---
    st.subheader("Animation : Laboratoire de mesure en dérivation")
    st.write(
        "Ajustez la tension du générateur et modifiez la nature du dipôle de la branche 2. "
        "Observez comment les ampèremètres virtuels réagissent en temps réel."
    )

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        tension_gen = st.slider(
            "Tension du générateur (U) en Volts [V]",
            min_value=0.0,
            max_value=24.0,
            value=12.0,
            step=0.5,
            key="slider_tension_tab4"
        )
    with col_ctrl2:
        choix_dipole = st.selectbox(
            "Choisir le dipôle secondaire (Branche 2) :",
            options=["Lampe standard (100 Ohms)", "Résistance chauffante (40 Ohms)", "Moteur électrique (24 Ohms)"],
            key="select_dipole_tab4"
        )

    # Modélisation mathématique du laboratoire virtuel
    r_branche1 = 60.0
    intensite_branche1 = tension_gen / r_branche1 if tension_gen > 0 else 0.0

    if choix_dipole == "Lampe standard (100 Ohms)":
        r_branche2 = 100.0
    elif choix_dipole == "Résistance chauffante (40 Ohms)":
        r_branche2 = 40.0
    else:
        r_branche2 = 24.0
        
    intensite_branche2 = tension_gen / r_branche2 if tension_gen > 0 else 0.0
    intensite_principale = intensite_branche1 + intensite_branche2

    # Affichage des écrans des ampèremètres virtuels
    st.write("**Écran de contrôle des ampèremètres branchés :**")
    col_amp1, col_amp2, col_amp3 = st.columns(3)
    with col_amp1:
        st.metric(label="Ampèremètre Principal (Ig)", value=f"{intensite_principale:.3f} A")
    with col_amp2:
        st.metric(label="Ampèremètre Branche 1 (I1)", value=f"{intensite_branche1:.3f} A", delta="Fixe (60 Ohms)")
    with col_amp3:
        st.metric(label="Ampèremètre Branche 2 (I2)", value=f"{intensite_branche2:.3f} A", delta=f"Variable ({r_branche2:.0f} Ohms)")

    # Maquette textuelle dynamique du circuit
    nom_propre_dipole = choix_dipole.split(" (")[0]
    st.code(
        f"""
         +------[ Générateur : {tension_gen:.1f} V ]------+

         |                                         |
         |---> Ig = {intensite_principale:.3f} A               | Nœud de retour
      (Nœud)------------------------------------+

         |                                      |
         |---> I1 = {intensite_branche1:.3f} A             |---> I2 = {intensite_branche2:.3f} A
   [ Lampe 1 ]                            [ {nom_propre_dipole} ]

         |                                      |
         +--------------------------------------+
         |
         +-----------------------------------------+
        """,
        language="text"
    )
    st.info(f"Vérification : {intensite_branche1:.3f} A (I1) + {intensite_branche2:.3f} A (I2) = {intensite_principale:.3f} A (Ig)")

    st.divider()

    # --- SECTION 3 : ZONE DE QUIZ ET COMMANDE DE VERROUILLAGE ---
    if "suite_verrouille_tab4" not in st.session_state:
        st.session_state.suite_verrouille_tab4 = False
    verrou_at4 = st.session_state.suite_verrouille_tab4

    # Appel de la fonction d'exercice pour l'onglet 4
    afficher_atelier_circuit_derivation(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Circuit en dérivation.",
        key="check_certif_derivation_final_net",
        disabled=verrou_at4,
    )

    # Bloc de correction et calcul des scores
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_official_net", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_aleatoire:
                    reponse_eleve = st.session_state.get(f"der_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            score_t4 = sum(
                [
                    st.session_state.get("der_t1_final") == "nœud",
                    st.session_state.get("der_t2_final") == "additivité",
                    st.session_state.get("der_t3_final") == "somme",
                    st.session_state.get("der_t4_final") == "indépendantes",
                    st.session_state.get("der_t5_final") == "principale",
                    st.session_state.get("der_t6_final") == "dérivées",
                    st.session_state.get("der_t7_final") == "augmente",
                    st.session_state.get("der_t8_final") == "parallèle",
                    st.session_state.get("der_t9_final") == "divise",
                    st.session_state.get("der_t10_final") == "continue",
                ]
            )

            st.session_state.score_suite4_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4 = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4 = True
            st.rerun()

    # --- SECTION 4 : COMPILATION DU BILAN HTML POUR L'ONGLET 4 ---
    if st.session_state.get("suite_verrouille_tab4", False):
        scr1_t4 = st.session_state.get("score_suite4_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER CIRCUIT EN DÉRIVATION SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_derivation = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Circuit en Dérivation - {n_eleve}</title>
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
                <p>Atelier 4 : Lois des intensités dans les circuits en dérivation</p>
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

        # 2. Boucle de récupération des réponses et génération des lignes dynamiques
        if "ordre_quiz_tab4_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
                saisie = st.session_state.get(f"der_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                
                # Ajout de la ligne au tableau HTML
                html_export_derivation += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 3. Fermeture définitive des conteneurs de la table
        html_export_derivation += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # 4. Déclaration du bouton de téléchargement Streamlit
        nom_fichier_html_t4 = preparer_nom_fichier("Rapport_Circuit_Derivation").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_derivation,
            file_name=nom_fichier_html_t4,
            mime="text/html",
            use_container_width=True
        )



            
with tab5:
    st.header("La loi d'Ohm")
    
    # --- SECTION 1 : THÉORIE ET ÉNONCÉ ---
    st.subheader("Définition et énoncé de la loi")
    st.write(
        "La loi d'Ohm est une relation fondamentale de l'électricité. Elle établit que la tension (U) "
        "aux bornes d'un conducteur ohmique (une résistance) est proportionnelle à l'intensité (I) "
        "du courant électrique qui le traverse."
    )
    st.write(
        "L'expression mathématique s'écrit :\n\n"
        "**U = R x I**\n\n"
        "Avec les unités officielles suivantes :\n"
        "* **U** : Tension en Volts (V)\n"
        "* **R** : Résistance en Ohms (Ω)\n"
        "* **I** : Intensité en Ampères (A)"
    )

    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF ET CARACTÉRISTIQUE ---
    st.subheader("Animation : Caractéristique U = f(I) en temps réel")
    st.write(
        "Modifiez les paramètres du conducteur ohmique à l'aide des curseurs. "
        "Le graphique de la caractéristique (droite passant par l'origine) et le point de fonctionnement se mettent à jour instantanément."
    )

    col_tp1, col_tp2 = st.columns(2)
    with col_tp1:
        tension_ohm = st.slider(
            "Tension appliquée (U) en Volts [V]",
            min_value=0.0,
            max_value=24.0,
            value=12.0,
            step=0.5,
            key="slider_u_tab5"
        )
    with col_tp2:
        resistance_ohm = st.slider(
            "Valeur de la résistance (R) en Ohms [Ω]",
            min_value=10.0,
            max_value=500.0,
            value=100.0,
            step=10.0,
            key="slider_r_tab5"
        )

    # Calcul mathématique de l'intensité
    intensite_ohm = tension_ohm / resistance_ohm if tension_ohm > 0 else 0.0

    # Affichage des métriques dynamiques
    col_met1, col_met2, col_met3 = st.columns(3)
    with col_met1:
        st.metric(label="Tension mesurée (U)", value=f"{tension_ohm:.1f} V")
    with col_met2:
        st.metric(label="Résistance choisie (R)", value=f"{resistance_ohm:.0f} Ω")
    with col_met3:
        st.metric(label="Intensité calculée (I)", value=f"{intensite_ohm:.3f} A")

    # Génération des données pour tracer la courbe U = f(I)
    tensions_axe = np.linspace(0, 24, 50)
    intensites_axe = tensions_axe / resistance_ohm
    
    # Création du DataFrame pour le graphique natif Streamlit
    donnees_graphique = pd.DataFrame({
        "Intensité (A)": intensites_axe,
        "Tension (V)": tensions_axe
    })
    
    # Affichage de la courbe caractéristique
    st.line_chart(donnees_graphique, x="Intensité (A)", y="Tension (V)")
    st.info(
        f"Constat expérimental : La courbe obtenue est une droite qui passe par l'origine. "
        f"Le coefficient directeur de cette droite correspond à la valeur de la résistance, soit {resistance_ohm:.0f} Ω."
    )

    st.divider()

    # --- SECTION 3 : ZONE DE EXERCICES ET COMPORTEMENT DE VERROUILLAGE ---
    if "suite_verrouille_tab5" not in st.session_state:
        st.session_state.suite_verrouille_tab5 = False
    verrou_at5 = st.session_state.suite_verrouille_tab5

    # Appel du module de questions spécifique à l'onglet 5
    afficher_atelier_loi_ohm(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la loi d'Ohm.",
        key="check_certif_ohm_final_net",
        disabled=verrou_at5,
    )

    # Bloc de correction et calcul des scores
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_official_net", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_aleatoire:
                    reponse_eleve = st.session_state.get(f"ohm_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q5 += 1.0

            score_t5 = sum(
                [
                    st.session_state.get("ohm_t1_final") == "proportionnelle",
                    st.session_state.get("ohm_t2_final") == "droite",
                    st.session_state.get("ohm_t3_final") == "origine",
                    st.session_state.get("ohm_t4_final") == "multiplié",
                    st.session_state.get("ohm_t5_final") == "divisée",
                    st.session_state.get("ohm_t6_final") == "ampère",
                    st.session_state.get("ohm_t7_final") == "volt",
                    st.session_state.get("ohm_t8_final") == "conducteur",
                    st.session_state.get("ohm_t9_final") == "diminue",
                    st.session_state.get("ohm_t10_final") == "directeur",
                ]
            )

            st.session_state.score_suite5_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5 = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5 = True
            st.rerun()

    # --- SECTION 4 : COMPILATION DU RAPPORT HTML TAB 5 ---
    if st.session_state.get("suite_verrouille_tab5", False):
        scr1_t5 = st.session_state.get("score_suite5_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5", 0.0)

        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER LOI D'OHM SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_ohm = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Loi d'Ohm - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4f46e5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
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
                <p>Atelier 5 : Modélisation et calculs de la loi d'Ohm</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4f46e5;">
                Note obtenue au Quiz de Calcul : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse Graphique : <strong>{scr2_t5:.1f} / 10</strong><br>
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
                saisie = st.session_state.get(f"ohm_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ohm += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ohm += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t5 = preparer_nom_fichier("Rapport_Loi_Ohm").replace(".txt", ".html")
        st.download_button(

        label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
        data=html_export_ohm,
        file_name=nom_fichier_html_t5,
        mime="text/html",
        use_container_width=True
        )




with tab6:
    st.header("Les conducteurs et les isolants d'électricité")
    
    # --- SECTION 1 : THÉORIE ET CLASSIFICATION ---
    st.subheader("Propriétés physiques des matériaux")
    st.write(
        "Tous les matériaux ne se comportent pas de la même manière face au passage du courant électrique. "
        "On les classe en deux grandes familles selon leur capacité à laisser circuler librement les charges électriques "
        "(électrons libres dans les métaux solides ou ions en solutions aqueuses) :"
    )
    
    col_mat1, col_mat2 = st.columns(2)
    with col_mat1:
        st.write("**Les conducteurs**")
        st.write(
            "Un conducteur est un matériau qui possède une grande quantité de porteurs de charges mobiles. "
            "Les métaux (comme l'argent, le cuivre, l'or et l'aluminium), le graphite (le carbone) "
            "ainsi que l'eau salée sont d'excellents conducteurs d'électricité."
        )
    with col_mat2:
        st.write("**Les isolants**")
        st.write(
            "Un isolant est un matériau qui ne possède pas ou très peu de porteurs de charges capables de se déplacer. "
            "Le plastique, le verre, la céramique, le bois parfaitement sec, le caoutchouc et l'air sec "
            "sont des isolants. Ils bloquent le passage du courant électrique."
        )

    st.divider()


with tab6:
    st.header("Propriétés physiques et échauffement des conducteurs")
    st.write(
        "Cette section permet d'étudier l'influence de la nature du matériau, de sa géométrie "
        "et de l'intensité du courant sur la résistance électrique d'un fil conducteur et son échauffement par effet Joule."
    )

    # --- BANQUE DE DONNÉES DES MATÉRIAUX (Résistivité rho à 20°C en Ohm.m) ---
    base_materiaux = {
        "Argent": 1.59e-8,
        "Cuivre": 1.68e-8,
        "Or": 2.44e-8,
        "Aluminium": 2.82e-8,
        "Tungstène": 5.60e-8,
        "Zinc": 5.90e-8,
        "Nickel": 6.99e-8,
        "Fer": 1.00e-7,
        "Platine": 1.06e-7,
        "Étain": 1.09e-7,
        "Plomb": 2.20e-7,
        "Titane": 4.20e-7,
        "Mercure": 9.60e-7,
        "Nichrome (Nickel-Chrome)": 1.10e-6,
        "Constantan": 4.90e-7,
        "Manganine": 4.82e-7,
        "Carbone (Graphite)": 3.50e-5,
        "Acier inoxydable": 7.20e-7,
        "Acier doux": 1.50e-7,
        "Laiton": 7.00e-8,
        "Bronze": 1.50e-7,
        "Magnésium": 4.39e-8,
        "Cobalt": 6.24e-8,
        "Cadmium": 6.83e-8,
        "Chrome": 1.25e-7,
        "Tantale": 1.31e-7,
        "Niobium": 1.52e-7,
        "Bismuth": 1.29e-6,
        "Silicium dopé": 1.00e-3,
        "Eau de mer salée": 2.00e-1
    }

    # --- PANNEAU DE CONTRÔLE INTERACTIF ---
    st.subheader("Paramètres expérimentaux du conducteur")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        nom_materiau = st.selectbox(
            "Sélectionner le matériau du fil :",
            options=list(base_materiaux.keys()),
            key="sb_mat_tab6"
        )
        rho_base = base_materiaux[nom_materiau]
        
    with col_p2:
        diametre_mm = st.slider(
            "Diamètre du fil (d) en millimètres [mm]",
            min_value=0.1,
            max_value=5.0,
            value=1.5,
            step=0.1,
            key="sl_diam_tab6"
        )
        
    with col_p3:
        tension_fil = st.slider(
            "Tension aux bornes du fil (U) en Volts [V]",
            min_value=0.0,
            max_value=12.0,
            value=2.0,
            step=0.1,
            key="sl_u_tab6"
        )

    # --- CALCULS PHYSIQUES ---
    # Longueur arbitraire fixée à 1 mètre pour l'étude comparative
    longueur_m = 1.0
    
    # Calcul de la section du fil : S = pi * r^2
    rayon_m = (diametre_mm / 1000.0) / 2.0
    section_m2 = np.pi * (rayon_m ** 2)
    
    # Résistance du fil à température initiale : R = rho * L / S
    resistance_fil = rho_base * (longueur_m / section_m2)
    
    # Intensité circulant dans le fil (Loi d'Ohm) : I = U / R
    # Limitation technique à 150A pour simuler la disjonction ou fusion du fil
    if resistance_fil > 0:
        intensite_fil = tension_fil / resistance_fil
    else:
        intensite_fil = 0.0

    # Modélisation simplifiée de la température d'équilibre thermique (Effet Joule vs Dissipation air)
    # Puissance dissipée P = U * I
    puissance_joule = tension_fil * intensite_fil
    
    # Surface externe d'échange du fil : A = 2 * pi * r * L
    surface_echange = 2.0 * np.pi * rayon_m * longueur_m
    
    # Coefficient de transfert thermique de l'air ambiant (h)
    coeff_h = 25.0 
    temperature_ambiante = 20.0
    
    # Élévation de température deltaT = P / (h * A)
    if surface_echange > 0:
        elevation_temp = puissance_joule / (coeff_h * surface_echange)
        temperature_finale = temperature_ambiante + elevation_temp
    else:
        temperature_finale = temperature_ambiante

    # --- AFFICHAGE DES RÉSULTATS VISUELS ---
    st.subheader("Diagnostic en temps réel de la ligne")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    
    with col_r1:
        st.metric(
            label="Résistance totale du fil", 
            value=f"{resistance_fil:.4f} Ohms" if resistance_fil >= 0.0001 else f"{resistance_fil * 1000:.3f} mOhms"
        )
    with col_r2:
        if intensite_fil > 100.0:
            st.metric(label="Intensité en circulation", value=f"{intensite_fil:.2f} A", delta="Surcharge critique")
        else:
            st.metric(label="Intensité en circulation", value=f"{intensite_fil:.2f} A")
            
    with col_r3:
        if temperature_finale >= 1200.0:
            st.metric(label="Température estimée du conducteur", value="Fusion du métal !", delta="Danger incendie")
        else:
            st.metric(label="Température estimée du conducteur", value=f"{temperature_finale:.1f} °C")

    # --- COMPOSANT VISUEL : ALERTES SÉCURITÉ ---
    if temperature_finale > 65.0 and temperature_finale < 1200.0:
        st.warning(
            f"Alerte échauffement : Le fil de {nom_materiau} surchauffe significativement. "
            f"La gaine isolante en plastique classique (fondant à 80°C) risque d'être détruite."
        )
    elif temperature_finale >= 1200.0:
        st.error(
            f"Rupture de ligne : L'intensité extrême de {intensite_fil:.1f} A a dépassé le point "
            f"de tolérance thermique du matériau. Le circuit est physiquement détruit."
        )
    else:
        st.success("Fonctionnement normal : Température stabilisée et sécurisée pour l'environnement.")

    st.write(
        f"Note technique : La résistivité du matériau choisi ({nom_materiau}) est de **{rho_base:.2e} Ohm.m**. "
        f"Plus le diamètre augmente, plus la section grandit, ce qui diminue la résistance et limite l'élévation de température."
    )
    # --- SECTION 2 : ZONE DE EXERCICES ET COMMANDE DE VERROUILLAGE ---
    if "suite_verrouille_tab6" not in st.session_state:
        st.session_state.suite_verrouille_tab6 = False
    verrou_at6 = st.session_state.suite_verrouille_tab6

    # Appel du module de questions spécifique à l'onglet 6
    afficher_atelier_conducteurs(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur les conducteurs et les isolants.",
        key="check_certif_cond_final_net",
        disabled=verrou_at6,
    )

    # Bloc de correction et calcul des scores du Tab 6
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_official_net", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            if "ordre_quiz_tab6_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_aleatoire:
                    reponse_eleve = st.session_state.get(f"cond_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q6 += 1.0

            score_t6 = sum(
                [
                    st.session_state.get("cond_t1_final") == "libres",
                    st.session_state.get("cond_t2_final") == "cuivre",
                    st.session_state.get("cond_t3_final") == "plastique",
                    st.session_state.get("cond_t4_final") == "bloquent",
                    st.session_state.get("cond_t5_final") == "ions",
                    st.session_state.get("cond_t6_final") == "carbone",
                    st.session_state.get("cond_t7_final") == "sécurité",
                    st.session_state.get("cond_t8_final") == "humide",
                    st.session_state.get("cond_t9_final") == "métaux",
                    st.session_state.get("cond_t10_final") == "conductivité",
                ]
            )

            st.session_state.score_suite6_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6 = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6 = True
            st.rerun()

    # --- SECTION 3 : COMPILATION DU RAPPORT HTML TAB 6 ---
    if st.session_state.get("suite_verrouille_tab6", False):
        scr1_t6 = st.session_state.get("score_suite6_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6", 0.0)

        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER CONDUCTEURS ET ISOLANTS SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_cond = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Conducteurs Isolants - {n_eleve}</title>
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
                <p>Atelier 6 : Classification des conducteurs et des isolants</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #16a34a;">
                Note obtenue au Quiz de Tri : <strong>{scr1_t6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t6:.1f} / 10</strong><br>
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
                saisie = st.session_state.get(f"cond_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_cond += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cond += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t6 = preparer_nom_fichier("Rapport_Conducteurs").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_cond,
            file_name=nom_fichier_html_t6,
            mime="text/html",
            use_container_width=True
        )





























            
