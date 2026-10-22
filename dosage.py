
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application les différents types de dosage",
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
st.title("Application les différents types de dosage")
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
    "Historique et pourquoi faire des dosages",
    "Dosage colorimétrique",
    "Dosage conductimétrique",
    "Dosage spectrophotométrique",
    "Dosage pH-métrique",
    "Dosage d'oxydoréduction",
    "Dosage par précipitation",
    "Dosage complexométrique",
    "Dosage en retour"
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


def afficher_atelier_en_retour(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 9 (Dosage en retour) sur deux colonnes."""
    import random

    questions_dos9_sources = [
        {"id": "qrt1", "q": "Quelle est la caractéristique principale d'un dosage en retour par rapport à un dosage direct ?", "options": ["On dose l'excès d'un réactif introduit en quantité connue et non l'espèce inconnue elle-même", "On fait réagir les produits en sens inverse", "On chauffe le mélange jusqu'à évaporation totale"], "rep": "On dose l'excès d'un réactif introduit en quantité connue et non l'espèce inconnue elle-même"},
        {"id": "qrt2", "q": "Pourquoi choisit-on de réaliser un dosage en retour plutôt qu'un dosage direct ?", "options": ["Parce que la réaction de base est trop lente ou qu'il n'y a pas d'indicateur coloré direct", "Pour utiliser plus de matériel en verre", "Pour augmenter artificiellement la note de l'exercice"], "rep": "Parce que la réaction de base est trop lente ou qu'il n'y a pas d'indicateur coloré direct"},
        {"id": "qrt3", "q": "Lors de la première étape d'un dosage en retour, le réactif intermédiaire doit obligatoirement être introduit en :", "options": ["Excès connu", "Défaut majeur", "Quantité stœchiométrique exacte"], "rep": "Excès connu"},
        {"id": "qrt4", "q": "Dans le dosage des ions lactate d'un lait par les ions argent, que fait le premier précipité formé ?", "options": ["Il s'isole ou s'ignore pendant qu'on titre les ions argent restants", "Il explose dans le bécher", "Il se transforme en gaz carbonique"], "rep": "Il s'isole ou s'ignore pendant qu'on titre les ions argent restants"},
        {"id": "qrt5", "q": "Quel réactif versé par la burette sert à doser l'excès d'ions argent dans la méthode de Volhard ?", "options": ["Les ions thiocyanate SCN-", "L'acide chlorhydrique", "La soude caustique"], "rep": "Les ions thiocyanate SCN-"},
        {"id": "qrt6", "q": "Quel indicateur coloré spécifique des ions fer III utilise-t-on dans le titrage de Volhard ?", "options": ["L'alun de fer III", "Le bleu de bromothymol", "Le Noir Ériochrome T"], "rep": "L'alun de fer III"},
        {"id": "qrt7", "q": "Quel repère visuel indique l'équivalence finale lors du retour dans la méthode de Volhard ?", "options": ["L'apparition d'une coloration rouge-sang persistante", "Le virage du liquide au bleu azur", "La disparition totale de tout solide"], "rep": "L'apparition d'une coloration rouge-sang persistante"},
        {"id": "qrt8", "q": "Quel complexe soluble coloré est responsable de la teinte rouge à l'équivalence de Volhard ?", "options": ["Le complexe [Fe(SCN)]2+", "Le précipité de chlorure d'argent", "L'ion permanganate"], "rep": "Le complexe [Fe(SCN)]2+"},
        {"id": "qrt9", "q": "Pour trouver la quantité de matière inconnue, quelle opération mathématique effectue-t-on entre la quantité initiale versée et la quantité en excès dosée ?", "options": ["Une soustraction (N_inconnue = N_initiale - N_excès)", "Une multiplication", "Une division par 14"], "rep": "Une soustraction (N_inconnue = N_initiale - N_excès)"},
        {"id": "qrt10", "q": "Le titrage en retour est une méthode d'analyse chimique qualifiée de :", "options": ["Indirecte", "Directe", "Qualitative uniquement"], "rep": "Indirecte"}
    ]

    if "ordre_quiz_tab9_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos9_sources)
        st.session_state.ordre_quiz_tab9_dos_aleatoire = questions_dos9_sources

    champs_mis_a_jour_b9 = [
        ("1. Le titrage en retour est une technique d'analyse quantitative de type ..........", ["Choisir...", "indirecte", "directe"], "indirecte", "dos9_t1"),
        ("2. On applique cette méthode lorsque la réaction directe est beaucoup trop ..........", ["Choisir...", "lente", "rapide"], "lente", "dos9_t2"),
        ("3. La première étape consiste à introduire un réactif en .......... connu.", ["Choisir...", "excès", "défaut"], "excès", "dos9_t3"),
        ("4. La seconde étape consiste à doser la quantité de matière restée en ..........", ["Choisir...", "excès", "stagnation"], "excès", "dos9_t4"),
        ("5. La méthode de .......... est un grand classique des titrages en retour de l'argent.", ["Choisir...", "Volhard", "Mohr"], "Volhard", "dos9_t5"),
        ("6. Le réactif titrant final utilisé pour doser l'excès d'argent est le ..........", ["Choisir...", "thiocyanate", "chlorure"], "thiocyanate", "dos9_t6"),
        ("7. L'indicateur coloré apportant les ions fer III est l'.......... de fer.", ["Choisir...", "alun", "esprit"], "alun", "dos9_t7"),
        ("8. L'équivalence finale est marquée par un complexe de couleur rouge ..........", ["Choisir...", "sang", "brique"], "sang", "dos9_t8"),
        ("9. Déduire l'inconnu repose mathématiquement sur une .......... entre les moles.", ["Choisir...", "soustraction", "addition"], "soustraction", "dos9_t9"),
        ("10. Ce protocole permet de contourner l'absence d'un .......... direct fiable.", ["Choisir...", "indicateur", "conductimètre"], "indicateur", "dos9_t10")
    ]
    st.session_state.champs_dos9_clean = champs_mis_a_jour_b9

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab9_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at9_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 9 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos9_clean:
            # L'index [0] prend uniquement la phrase, l'index [1] prend uniquement la liste
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=f"{cle}_dos9_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_complexometrie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 8 (Dosage complexométrique) sur deux colonnes."""
    import random

    questions_dos8_sources = [
        {"id": "qcx1", "q": "Quel type d'édifice chimique stable se forme lors d'un dosage complexométrique ?", "options": ["Un complexe", "Un précipité solide", "Une molécule de gaz"], "rep": "Un complexe"},
        {"id": "qcx2", "q": "Quelle molécule est le réactif titrant chélatant le plus célèbre pour doser les ions métalliques ?", "options": ["L'EDTA", "Le nitrate d'argent", "La soude caustique"], "rep": "L'EDTA"},
        {"id": "qcx3", "q": "Quels ions sont principalement dosés pour mesurer la dureté (titre hydrotimétrique) d'une eau ?", "options": ["Les ions calcium Ca2+ et magnésium Mg2+", "Les ions sodium et chlorure", "Les ions oxonium et hydroxyde"], "rep": "Les ions calcium Ca2+ et magnésium Mg2+"},
        {"id": "qcx4", "q": "Quel indicateur coloré de métaux utilise-t-on couramment pour le dosage des ions magnésium ?", "options": ["Le Noir Ériochrome T (NET)", "La phénolphtaléine", "Le bleu de bromothymol"], "rep": "Le Noir Ériochrome T (NET)"},
        {"id": "qcx5", "q": "Quelle couleur prend le NET lorsqu'il est lié seul aux ions métalliques avant l'équivalence ?", "options": ["Rose violacé", "Bleu azur", "Incolore"], "rep": "Rose violacé"},
        {"id": "qcx6", "q": "Quelle couleur prend le milieu à l'équivalence exacte lorsque l'EDTA a capturé tous les métaux ?", "options": ["Bleu azur net", "Rouge brique", "Vert bouteille"], "rep": "Bleu azur net"},
        {"id": "qcx7", "q": "Comment qualifie-t-on un indicateur qui change de couleur selon la présence d'ions métalliques libres ?", "options": ["Un indicateur metallochromique", "Un indicateur acido-basique", "Un auto-indicateur redox"], "rep": "Un indicateur metallochromique"},
        {"id": "qcx8", "q": "Une molécule chélatante comme l'EDTA entoure un ion métallique central en établissant plusieurs :", "options": ["Liaisons de coordination (liaisons datives)", "Liaisons covalentes doubles", "Liaisons hydrogène intermoléculaires"], "rep": "Liaisons de coordination (liaisons datives)"},
        {"id": "qcx9", "q": "Pour maintenir l'indicateur NET dans sa zone de sensibilité optimale, le milieu doit être tamponné à un pH de :", "options": ["pH = 10", "pH = 2", "pH = 7"], "rep": "pH = 10"},
        {"id": "qcx10", "q": "Le terme 'chélation' dérive d'un mot grec signifiant 'pince' car le ligand attrape le métal comme :", "options": ["Les pinces d'un crabe", "Les dents d'un rongeur", "Les ailes d'un oiseau"], "rep": "Les pinces d'un crabe"}
    ]

    if "ordre_quiz_tab8_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos8_sources)
        st.session_state.ordre_quiz_tab8_dos_aleatoire = questions_dos8_sources

    champs_mis_a_jour_b8 = [
        ("1. Le titrage complexométrique repose sur la formation d'un .......... stable dissous.", ["Choisir...", "complexe", "précipité"], "complexe", "dos8_t1"),
        ("2. La molécule reine utilisée comme réactif titrant chélatant est l'..........", ["Choisir...", "EDTA", "BBT"], "EDTA", "dos8_t2"),
        ("3. Ce dosage permet de déterminer la .......... totale d'une eau minérale ou du robinet.", ["Choisir...", "dureté", "conductivité"], "dureté", "dos8_t3"),
        ("4. Les ions ciblés par cette analyse sont le calcium et le ..........", ["Choisir...", "magnésium", "sodium"], "magnésium", "dos8_t4"),
        ("5. L'indicateur de métaux de référence est le Noir Ériochrome ..........", ["Choisir...", "T", "B"], "T", "dos8_t5"),
        ("6. Avant l'équivalence, le témoin lié aux ions métalliques arbore une teinte ..........", ["Choisir...", "rose", "bleue"], "rose", "dos8_t6"),
        ("7. Dès que l'EDTA a capturé tout le métal, le témoin libre vire au .......... net.", ["Choisir...", "bleu", "jaune"], "bleu", "dos8_t7"),
        ("8. Le terme chélation évoque l'action d'emprisonner l'ion comme dans une ..........", ["Choisir...", "pince", "cage"], "pince", "dos8_t8"),
        ("9. L'analyse exige de fixer le pH à 10 au moyen d'une solution ..........", ["Choisir...", "tampon", "acide"], "tampon", "dos8_t9"),
        ("10. À l'équivalence, les quantités de matière de ligand et de métal sont ..........", ["Choisir...", "stœchiométriques", "doublées"], "stœchiométriques", "dos8_t10")
    ]
    st.session_state.champs_dos8_clean = champs_mis_a_jour_b8

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab8_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at8_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 8 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos8_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos8_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_precipitation(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 7 (Dosage par précipitation) sur deux colonnes."""
    import random

    questions_dos7_sources = [
        {"id": "qpr1", "q": "Quel phénomène physique caractérise une réaction de précipitation lors d'un dosage ?", "options": ["La formation d'un solide insoluble appelé précipité", "Le dégagement d'un gaz odorant", "L'ébullition spontanée du mélange"], "rep": "La formation d'un solide insoluble appelé précipité"},
        {"id": "qpr2", "q": "Quelle est la couleur classique du précipité de chlorure d'argent (AgCl) formé au cours du titrage ?", "options": ["Blanc", "Bleu azur", "Jaune vif"], "rep": "Blanc"},
        {"id": "qpr3", "q": "Quelle est la particularité physique du précipité de chlorure d'argent lorsqu'il reste exposé à la lumière ?", "options": ["Il noircit à la lumière", "Il se dissout instantanément", "Il devient vert fluo"], "rep": "Il noircit à la lumière"},
        {"id": "qpr4", "q": "Dans la méthode de Mohr, quel ion utilise-t-on comme indicateur coloré pour repérer la fin de la précipitation des chlorures ?", "options": ["L'ion chromate CrO4 2-", "L'ion permanganate", "Le bleu de bromothymol"], "rep": "L'ion chromate CrO4 2-"},
        {"id": "qpr5", "q": "Quelle couleur prend le milieu à l'équivalence exacte dans le cas de la méthode de Mohr ?", "options": ["Une coloration rouge-brique ou orange persistante", "Une transparence totale", "Une couleur violette foncée"], "rep": "Une coloration rouge-brique ou orange persistante"},
        {"id": "qpr6", "q": "Quel solide coloré se forme à l'équivalence lorsque l'indicateur chromate réagit avec les ions argent en excès ?", "options": ["Le chromate d'argent", "Le chlorure d'argent", "Le nitrate de sodium"], "rep": "Le chromate d'argent"},
        {"id": "qpr7", "q": "Pourquoi le précipité rouge-brique ne se forme-t-il qu'après la disparition totale des ions chlorure ?", "options": ["Car le chlorure d'argent est beaucoup moins soluble que le chromate d'argent", "Car l'appareil est éteint", "Car les ions chlorure mangent l'indicateur"], "rep": "Le chlorure d'argent est beaucoup moins soluble que le chromate d'argent"},
        {"id": "qpr8", "q": "Comment appelle-t-on le produit des concentrations des ions élevés à leur puissance stœchiométrique à l'équilibre d'un solide ?", "options": ["Le produit de solubilité Ks", "Le coefficient d'extinction", "La conductance équivalente"], "rep": "Le produit de solubilité Ks"},
        {"id": "qpr9", "q": "Si le produit des concentrations ioniques est inférieur au produit de solubilité Ks, que fait la solution ?", "options": ["Elle reste limpide sans former de précipité", "Elle se met à saturer", "Elle change instantanément de couleur"], "rep": "Elle reste limpide sans former de précipité"},
        {"id": "qpr10", "q": "Le titrage par précipitation des ions chlorure de l'eau de mer par les ions argent est une méthode d'analyse :", "options": ["Quantitative", "Qualitative uniquement", "Thermodynamique"], "rep": "Quantitative"}
    ]

    if "ordre_quiz_tab7_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos7_sources)
        st.session_state.ordre_quiz_tab7_dos_aleatoire = questions_dos7_sources

    champs_mis_a_jour_b7 = [
        ("1. Un titrage par précipitation repose sur l'apparition d'un composé .......... insoluble.", ["Choisir...", "solide", "gazeux"], "solide", "dos7_t1"),
        ("2. Le solide suspendu qui trouble le liquide du bécher est appelé un ..........", ["Choisir...", "précipité", "complexe"], "précipité", "dos7_t2"),
        ("3. La réaction entre les ions argent et les ions chlorure crée un solide de couleur ..........", ["Choisir...", "blanche", "bleue"], "blanche", "dos7_t3"),
        ("4. Une propriété remarquable du chlorure d'argent est qu'il .......... à la lumière.", ["Choisir...", "noircit", "fond"], "noircit", "dos7_t4"),
        ("5. La constante d'équilibre thermodynamique associée à un solide est le produit de ..........", ["Choisir...", "solubilité", "virage"], "solubilité", "dos7_t5"),
        ("6. La méthode de .......... utilise l'ion chromate comme témoin de fin de réaction.", ["Choisir...", "Mohr", "Beer"], "Mohr", "dos7_t6"),
        ("7. L'ion chromate réagit avec l'argent pour former un composé de couleur rouge ..........", ["Choisir...", "brique", "fuchsia"], "brique", "dos7_t7"),
        ("8. Le témoin coloré ne précipite qu'une fois les chlorures entièrement ..........", ["Choisir...", "consommés", "multipliés"], "consommés", "dos7_t8"),
        ("9. Trouver la fin du titrage à l'œil nu correspond à un repérage ..........", ["Choisir...", "colorimétrique", "voltmétrique"], "colorimétrique", "dos7_t9"),
        ("10. À l'équivalence exacte, le mélange respecte les proportions ..........", ["Choisir...", "stœchiométriques", "inverses"], "stœchiométriques", "dos7_t10")
    ]
    st.session_state.champs_dos7_clean = champs_mis_a_jour_b7

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at7_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos7_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos7_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_oxydoreduction(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Dosage d'oxydoréduction) sur deux colonnes."""
    import random

    questions_dos6_sources = [
        {"id": "qox1", "q": "Quel type de transfert de particules caractérise une réaction d'oxydoréduction ?", "options": ["Un transfert d'électrons", "Un transfert de protons", "Un échange de molécules d'eau"], "rep": "Un transfert d'électrons"},
        {"id": "qox2", "q": "Comment appelle-t-on l'espèce chimique capable de capter un ou plusieurs électrons ?", "options": ["L'oxydant", "Le réducteur", "L'indicateur"], "rep": "L'oxydant"},
        {"id": "qox3", "q": "Comment appelle-t-on l'espèce chimique capable de céder un ou plusieurs électrons ?", "options": ["Le réducteur", "L'oxydant", "Le solvant"], "rep": "Le réducteur"},
        {"id": "qox4", "q": "Quelle est la couleur caractéristique des ions permanganate MnO4- en solution ?", "options": ["Violet intense", "Vert pomme", "Incolore"], "rep": "Violet intense"},
        {"id": "qox5", "q": "Lors du titrage des ions ferreux par le permanganate, quelle est la couleur du milieu avant l'équivalence ?", "options": ["Pratiquement incolore", "Violet foncé", "Jaune vif"], "rep": "Pratiquement incolore"},
        {"id": "qox6", "q": "Quel repère visuel précis indique l'équivalence lors du dosage des ions ferreux par le permanganate ?", "options": ["La persistance d'une coloration rose ou violette pâle", "L'apparition d'un précipité blanc", "Le dégagement de bulles de gaz"], "rep": "La persistance d'une coloration rose ou violette pâle"},
        {"id": "qox7", "q": "Comment appelle-t-on la méthode instrumentale consistant à suivre le potentiel électrique (en mV) pour un dosage redox ?", "options": ["La potentiométrie", "La pH-métrie", "La spectrophotométrie"], "rep": "La potentiométrie"},
        {"id": "qox8", "q": "Dans l'équation de dosage des ions ferreux par le permanganate, combien d'électrons sont échangés au total par mole de permanganate ?", "options": ["5 électrons", "1 électron", "2 électrons"], "rep": "5 électrons"},
        {"id": "qox9", "q": "Pourquoi n'est-il pas nécessaire d'ajouter un indicateur coloré externe lors du dosage par le permanganate de potassium ?", "options": ["Car le réactif titrant est lui-même un auto-indicateur grâce à sa couleur violette", "Car la solution se met à bouillir", "Car le pH reste bloqué à 7"], "rep": "Car le réactif titrant est lui-même un auto-indicateur grâce à sa couleur violette"},
        {"id": "qox10", "q": "Une perte d'électrons subie par une espèce chimique au cours d'une transformation s'appelle :", "options": ["Une oxydation", "Une réduction", "Une dilution"], "rep": "Une oxydation"}
    ]

    if "ordre_quiz_tab6_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos6_sources)
        st.session_state.ordre_quiz_tab6_dos_aleatoire = questions_dos6_sources

    champs_mis_a_jour_b6 = [
        ("1. Un titrage d'oxydoréduction repose sur un transfert de .......... entre deux espèces.", ["Choisir...", "électrons", "protons"], "électrons", "dos6_t1"),
        ("2. L'espèce chimique qui capte les particules négatives s'appelle l'..........", ["Choisir...", "oxydant", "réducteur"], "oxydant", "dos6_t2"),
        ("3. L'espèce chimique qui cède ou donne ces particules est le ..........", ["Choisir...", "réducteur", "oxydant"], "réducteur", "dos6_t3"),
        ("4. Une perte d'électrons subie par une entité constitue une ..........", ["Choisir...", "oxydation", "réduction"], "oxydation", "dos6_t4"),
        ("5. Un gain d'électrons au cours d'une transformation est une ..........", ["Choisir...", "réduction", "oxydation"], "réduction", "dos6_t5"),
        ("6. Les ions permanganate possèdent une coloration .......... très prononcée.", ["Choisir...", "violette", "bleue"], "violette", "dos6_t6"),
        ("7. Avant l'équivalence, le permanganate versé est entièrement ..........", ["Choisir...", "consommé", "accumulé"], "consommé", "dos6_t7"),
        ("8. L'équivalence se repère par la persistance d'une coloration ..........", ["Choisir...", "rose", "jaune"], "rose", "dos6_t8"),
        ("9. Suivre ce dosage avec un voltmètre de précision s'appelle la ..........", ["Choisir...", "potentiométrie", "conductimétrie"], "potentiométrie", "dos6_t9"),
        ("10. À l'équivalence, le mélange respecte strictement les proportions ..........", ["Choisir...", "stœchiométriques", "inverses"], "stœchiométriques", "dos6_t10")
    ]
    st.session_state.champs_dos6_clean = champs_mis_a_jour_b6

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos6_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos6_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_phmetrie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Dosage pH-métrique) sur deux colonnes."""
    import random

    questions_dos5_sources = [
        {"id": "qph1", "q": "Quelle grandeur chimique mesure-t-on lors d'un titrage pH-métrique ?", "options": ["Le potentiel hydrogène (pH)", "L'absorbance lumineuse", "La conductivité ionique"], "rep": "Le potentiel hydrogène (pH)"},
        {"id": "qph2", "q": "Quels ions s'associent lors de la neutralisation pour former des molécules d'eau pure ?", "options": ["Les ions oxonium H3O+ et hydroxyde OH-", "Les ions sodium Na+ et chlorure Cl-", "Les molécules de dioxyde de carbone"], "rep": "Les ions oxonium H3O+ et hydroxyde OH-"},
        {"id": "qph3", "q": "Comment s'appelle le changement brutal de la valeur lue sur le graphique au moment de l'équivalence ?", "options": ["Le saut de pH", "Le calibre d'étalonnage", "L'index de virage"], "rep": "Le saut de pH"},
        {"id": "qph4", "q": "Quel est le pH théorique obtenu à l'équivalence lors du titrage d'un acide fort par une base forte ?", "options": ["pH = 7,0", "pH = 4,0", "pH = 10.0"], "rep": "pH = 7,0"},
        {"id": "qph5", "q": "Où place-t-on la solution titrante de concentration connue pour la verser goutte à goutte ?", "options": ["Dans la burette graduée", "Dans le bécher inférieur", "Dans l'éprouvette fixe"], "rep": "Dans la burette graduée"},
        {"id": "qph6", "q": "Quel appareil agite en continu le contenu du bécher pour homogénéiser le mélange ?", "options": ["L'agitateur magnétique", "La sonde de verre", "Le convertisseur"], "rep": "L'agitateur magnétique"},
        {"id": "qph7", "q": "Comment évolue le pH du bécher au tout début du dosage si celui-ci contient un acide initial ?", "options": ["Il augmente très lentement avant l'équivalence", "Il chute immédiatement à zéro", "Il reste fixe à 14,0"], "rep": "Il augmente très lentement avant l'équivalence"},
        {"id": "qph8", "q": "Quelle est la forme de la courbe représentant un dosage pH-métrique complet ?", "options": ["Une courbe en forme de S", "Une droite linéaire parfaite", "Une parabole inversée"], "rep": "Une courbe en forme de S"},
        {"id": "qph9", "q": "Une fois l'équivalence largement dépassée, vers quel type de pH la valeur tend-elle ?", "options": ["Un pH très basique", "Un pH acide proche de zéro", "Un pH neutre égal à 7"], "rep": "Un pH très basique"},
        {"id": "qph10", "q": "Quelle méthode géométrique courante permet de repérer graphiquement le point d'équivalence ?", "options": ["La méthode des tangentes parallèles", "L'intersection des droites de Kohlrausch", "La loi de Beer-Lambert"], "rep": "La méthode des tangentes parallèles"}
    ]

    if "ordre_quiz_tab5_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos5_sources)
        st.session_state.ordre_quiz_tab5_dos_aleatoire = questions_dos5_sources

    champs_mis_a_jour_b5 = [
        ("1. Le titrage pH-métrique suit l'évolution du potentiel .......... de la solution.", ["Choisir...", "hydrogène", "électrique"], "hydrogène", "dos5_t1"),
        ("2. Faire réagir un acide fort et une base forte produit de l'.......... pure.", ["Choisir...", "eau", "hydrogène"], "eau", "dos5_t2"),
        ("3. L'instant où tout l'acide initial est consommé s'appelle l'..........", ["Choisir...", "équivalence", "dilution"], "équivalence", "dos5_t3"),
        ("4. La courbe de titrage prend l'allure caractéristique d'une ligne en ..........", ["Choisir...", "S", "U"], "S", "dos5_t4"),
        ("5. Le moment charnière de la neutralisation se repère par un .......... de pH.", ["Choisir...", "saut", "palier"], "saut", "dos5_t5"),
        ("6. La solution titrante connue s'installe dans la .......... graduée.", ["Choisir...", "burette", "pipette"], "burette", "dos5_t6"),
        ("7. Le bécher de mesure repose sur un agitateur .......... circulaire.", ["Choisir...", "magnétique", "thermique"], "magnétique", "dos5_t7"),
        ("8. À l'équivalence exacte d'un acide fort par une base forte, le pH vaut ..........", ["Choisir...", "7", "14"], "7", "dos5_t8"),
        ("9. Continuer le versement après l'équivalence rend le milieu fortement ..........", ["Choisir...", "basique", "acide"], "basique", "dos5_t9"),
        ("10. La détermination graphique peut utiliser la méthode des .......... parallèles.", ["Choisir...", "tangentes", "droites"], "tangentes", "dos5_t10")
    ]
    st.session_state.champs_dos5_clean = champs_mis_a_jour_b5

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos5_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos5_clean", disabled=verrouille, label_visibility="collapsed")
                

def afficher_atelier_spectrophotometrie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Dosage spectrophotométrique) sur deux colonnes."""
    import random

    questions_dos4_sources = [
        {"id": "qsp1", "q": "Quelle grandeur physique sans unité mesure l'intensité de la lumière absorbée par une solution ?", "options": ["L'absorbance A", "La longueur d'onde lambda", "Le coefficient d'extinction"], "rep": "L'absorbance A"},
        {"id": "qsp2", "q": "Quelle loi stipule que l'absorbance est proportionnelle à la concentration molaire de l'espèce colorée ?", "options": ["La loi de Beer-Lambert", "La loi de Kohlrausch", "La loi de Gay-Lussac"], "rep": "La loi de Beer-Lambert"},
        {"id": "qsp3", "q": "Quel appareil électronique utilise-t-on pour mesurer l'absorbance d'une solution ?", "options": ["Un spectrophotomètre", "Un conductimètre", "Un pH-mètre"], "rep": "Un spectrophotomètre"},
        {"id": "qsp4", "q": "Comment appelle-t-on le petit récipient transparent à faces parallèles où l'on place l'échantillon ?", "options": ["Une cuve", "Un bécher", "Une fiole jaugée"], "rep": "Une cuve"},
        {"id": "qsp5", "q": "Quelle opération essentielle consiste à régler l'appareil sur zéro absorbance avec le solvant pur ?", "options": ["Faire le blanc", "L'étalonnage linéaire", "Le choix de la longueur d'onde"], "rep": "Faire le blanc"},
        {"id": "qsp6", "q": "À quelle longueur d'onde doit-on se placer pour obtenir une sensibilité de mesure maximale ?", "options": ["À la longueur d'onde correspondant au maximum d'absorbance (lambda max)", "À une longueur d'onde prise au hasard", "Dans le domaine de l'infrarouge lointain"], "rep": "À la longueur d'onde correspondant au maximum d'absorbance (lambda max)"},
        {"id": "qsp7", "q": "Que trace-t-on à l'aide de solutions étalons de concentrations connues pour doser un inconnu ?", "options": ["Une droite d'étalonnage", "Une courbe de saut de pH", "Une rupture de pente conductimétrique"], "rep": "Une droite d'étalonnage"},
        {"id": "qsp8", "q": "Quelle est la couleur complémentaire (absorbée au maximum) d'une solution de couleur bleue ?", "options": ["L'orangé", "Le rouge vif", "Le vert"], "rep": "L'orangé"},
        {"id": "qsp9", "q": "Si l'on multiplie par trois la concentration d'une solution diluée, que devient sa valeur d'absorbance ?", "options": ["Elle est multipliée par trois", "Elle reste identique", "Elle est divisée par trois"], "rep": "Elle est multipliée par trois"},
        {"id": "qsp10", "q": "Pourquoi la loi de Beer-Lambert ne s'applique-t-elle plus si la solution est trop concentrée ?", "options": ["Car la proportionnalité n'est vraie que pour les solutions diluées", "Car la solution se solidifie", "Car l'appareil s'éteint automatiquement"], "rep": "Car la proportionnalité n'est vraie que pour les solutions diluées"}
    ]

    if "ordre_quiz_tab4_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos4_sources)
        st.session_state.ordre_quiz_tab4_dos_aleatoire = questions_dos4_sources

    champs_mis_a_jour_b4 = [
        ("1. Le dosage spectrophotométrique exploite la quantité de .......... absorbée.", ["Choisir...", "lumière", "courant"], "lumière", "dos4_t1"),
        ("2. La proportionnalité entre l'absorbance et la concentration est définie par ..........", ["Choisir...", "Beer-Lambert", "Kohlrausch"], "Beer-Lambert", "dos4_t2"),
        ("3. L'appareil de mesure optique utilisé s'appelle un ..........", ["Choisir...", "spectrophotomètre", "conductimètre"], "spectrophotomètre", "dos4_t3"),
        ("4. Le flacon miniature accueillant la solution colorée est une ..........", ["Choisir...", "cuve", "pipette"], "cuve", "dos4_t4"),
        ("5. Régler l'absorbance à zéro en plaçant le solvant seul s'appelle faire le ..........", ["Choisir...", "blanc", "calibre"], "blanc", "dos4_t5"),
        ("6. La mesure s'effectue à la longueur d'onde où l'absorption est la plus ..........", ["Choisir...", "grande", "faible"], "grande", "dos4_t6"),
        ("7. La représentation graphique de cette loi prend l'allure d'une ..........", ["Choisir...", "droite", "courbe"], "droite", "dos4_t7"),
        ("8. Le tracé de référence construit avec des étalons est la courbe d'..........", ["Choisir...", "étalonnage", "neutralisation"], "étalonnage", "dos4_t8"),
        ("9. Cette loi de proportionnalité stricte n'est valable que pour les milieux ..........", ["Choisir...", "dilués", "saturés"], "dilués", "dos4_t9"),
        ("10. L'absorbance A est une grandeur physique qui possède la particularité d'être sans ..........", ["Choisir...", "unité", "limite"], "unité", "dos4_t10")
    ]
    st.session_state.champs_dos4_clean = champs_mis_a_jour_b4

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos4_clean:
            # Extraction précise par index de tuple pour nettoyer l'interface
            enonce = ligne[0]  # Extrait uniquement la phrase de texte propre
            choix = ligne[1]   # Extrait uniquement la liste des mots à choisir
            cle = ligne[-1]    # Extrait la clé unique de session
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos4_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_conductimetrie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Dosage conductimétrique) sur deux colonnes."""
    import random

    questions_dos3_sources = [
        {"id": "qcd1", "q": "Quelle grandeur physique mesure-t-on lors d'un titrage conductimétrique ?", "options": ["La conductance G ou la conductivité sigma", "L'absorbance de la lumière", "Le potentiel d'oxydoréduction"], "rep": "La conductance G ou la conductivité sigma"},
        {"id": "qcd2", "q": "Quel type de soluté est indispensable dans la solution pour pouvoir mener une mesure conductimétrique ?", "options": ["Des ions libres dissous", "Des molécules neutres comme le sucre", "Des gaz incolores"], "rep": "Des ions libres dissous"},
        {"id": "qcd3", "q": "Comment se repère visuellement l'équivalence sur le graphique d'un dosage conductimétrique ?", "options": ["Par une rupture de pente (intersection de deux droites)", "Par un maximum en forme de cloche", "Par un palier parfaitement plat"], "rep": "Par une rupture de pente (intersection de deux droites)"},
        {"id": "qcd4", "q": "Pourquoi ajoute-t-on un grand volume d'eau distillée dans le bécher au début du dosage ?", "options": ["Pour négliger la variation de volume lors des ajouts de la burette", "Pour augmenter la concentration des ions", "Pour modifier la température du milieu"], "rep": "Pour négliger la variation de volume lors des ajouts de la burette"},
        {"id": "qcd5", "q": "Quelle l'unité officielle de mesure de la conductivité d'une solution ?", "options": ["Siemens par mètre (S/m)", "Ohm par centimètre", "Volt par mole"], "rep": "Siemens par mètre (S/m)"},
        {"id": "qcd6", "q": "Comment qualifie-t-on l'appareil électronique muni d'une cellule de mesure que l'on plonge dans le bécher ?", "options": ["Un conductimètre", "Un spectrophotomètre", "Un pH-mètre"], "rep": "Un conductimètre"},
        {"id": "qcd7", "q": "Lors du titrage des ions chlorure par les ions argent, que fait la conductivité avant l'équivalence ?", "options": ["Elle diminue car les ions argent font précipiter les chlorures", "Elle s'envole vers l'infini", "Elle reste rigoureusement fixe"], "rep": "Elle diminue car les ions argent font précipiter les chlorures"},
        {"id": "qcd8", "q": "Que fait la courbe graphique après l'équivalence si l'on continue de verser le réactif titrant ionique ?", "options": ["Elle réaugmente à cause de l'accumulation des ions en excès", "Elle tombe brutalement à zéro", "Elle oscille de façon sinusoïdale"], "rep": "Elle réaugmente à cause de l'accumulation des ions en excès"},
        {"id": "qcd9", "q": "Quel composant de la cellule de mesure conductimétrique est extrêmement sensible aux rayures ?", "options": ["Les plaques de platine platiné", "Le barreau aimanté", "Le robinet de la burette"], "rep": "Les plaques de platine platiné"},
        {"id": "qcd10", "q": "Quelle loi stipule que la conductivité d'une solution diluée est proportionnelle aux concentrations des ions ?", "options": ["La loi de Kohlrausch", "La loi de Beer-Lambert", "La loi de Sorensen"], "rep": "La loi de Kohlrausch"}
    ]

    if "ordre_quiz_tab3_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos3_sources)
        st.session_state.ordre_quiz_tab3_dos_aleatoire = questions_dos3_sources

    # Déclaration explicite et écrasement forcé pour vider l'ancien cache corrompu
    champs_mis_a_jour = [
        ("1. Le titrage conductimétrique mesure la capacité d'une solution à conduire le ..........", ["Choisir...", "courant", "pH"], "courant", "dos3_t1"),
        ("2. Cette technique analytique s'applique uniquement si le milieu contient des ..........", ["Choisir...", "ions", "solvants"], "ions", "dos3_t2"),
        ("3. L'appareil de mesure électronique immergé s'appelle un ..........", ["Choisir...", "conductimètre", "spectrophotomètre"], "conductimètre", "dos3_t3"),
        ("4. L'unité de mesure de la conductivité de la solution est le S par ..........", ["Choisir...", "mètre", "litre"], "mètre", "dos3_t4"),
        ("5. La loi de .......... relie la conductivité à la concentration des ions.", ["Choisir...", "Kohlrausch", "Beer-Lambert"], "Kohlrausch", "dos3_t5"),
        ("6. Ajouter un grand volume d'eau au départ évite l'effet de ..........", ["Choisir...", "dilution", "précipitation"], "dilution", "dos3_t6"),
        ("7. Sur le graphique tracé, l'équivalence correspond à une .......... de pente.", ["Choisir...", "rupture", "stagnation"], "rupture", "dos3_t7"),
        ("8. Avant l'équivalence, la courbe baisse si les ions conducteurs sont ..........", ["Choisir...", "consommés", "accumulés"], "consommés", "dos3_t8"),
        ("9. Après l'équivalence, la courbe remonte car les ions versés sont en ..........", ["Choisir...", "excès", "défaut"], "excès", "dos3_t9"),
        ("10. La cellule de mesure comporte deux plaques parallèles de ..........", ["Choisir...", "platine", "cuivre"], "platine", "dos3_t10")
    ]
    st.session_state.champs_dos3_clean = champs_mis_a_jour

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos3_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos3_clean", disabled=verrouille, label_visibility="collapsed")
def afficher_atelier_colorimetrie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Dosage colorimétrique) sur deux colonnes."""
    import random

    questions_dos2_sources = [
        {"id": "qc1", "q": "Quel repère visuel indique l'équivalence lors d'un titrage colorimétrique ?", "options": ["Le changement persistant de couleur", "L'apparition de bulles de gaz", "Une baisse de la température"], "rep": "Le changement persistant de couleur"},
        {"id": "qc2", "q": "Comment appelle-t-on une substance chimique ajoutée pour colorer le milieu à l'équivalence ?", "options": ["Un indicateur coloré acido-basique", "Un solvant inerte", "Un catalyseur métallique"], "rep": "Un indicateur coloré acido-basique"},
        {"id": "qc3", "q": "Quelle est la couleur du bleu de bromothymol (BBT) dans un milieu neutre (pH = 7) ?", "options": ["Vert", "Jaune", "Bleu"], "rep": "Vert"},
        {"id": "qc4", "q": "Quelle couleur prend la phénolphtaléine lorsque le milieu devient basique ?", "options": ["Rose fuchsia", "Incolore", "Jaune vif"], "rep": "Rose fuchsia"},
        {"id": "qc5", "q": "Comment doit-on verser la solution titrante à l'approche du changement de couleur ?", "options": ["Goutte à goutte", "Par grandes vagues rapides", "En une seule fois"], "rep": "Goutte à goutte"},
        {"id": "qc6", "q": "Dans quel état se trouve la solution si l'indicateur a changé de couleur dès la première goutte ?", "options": ["L'équivalence est dépassée d'avance", "La solution est pure", "Le bécher est vide"], "rep": "L'équivalence est dépassée d'avance"},
        {"id": "qc7", "q": "Quelle propriété de la solution titrée est indispensable pour un dosage colorimétrique direct ?", "options": ["L'espèce dosée ou le réactif doit être coloré ou réagir coloré", "La solution doit être visqueuse", "La solution doit bouillir"], "rep": "L'espèce dosée ou le réactif doit être coloré ou réagir coloré"},
        {"id": "qc8", "q": "Quel est le rôle de la zone de virage d'un indicateur coloré ?", "options": ["L'intervalle de pH où l'indicateur change de teinte", "La vitesse de rotation de l'aimant", "Le volume maximal de la burette"], "rep": "L'intervalle de pH où l'indicateur change de teinte"},
        {"id": "qc9", "q": "Quelle couleur prend l'hélianthine dans un milieu fortement acide ?", "options": ["Rouge", "Jaune", "Incolore"], "rep": "Rouge"},
        {"id": "qc10", "q": "L'équivalence d'un titrage colorimétrique est un état où les réactifs sont mélangés dans des proportions :", "options": ["Stœchiométriques", "Aléatoires", "Inverses"], "rep": "Stœchiométriques"}
    ]

    if "ordre_quiz_tab2_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos2_sources)
        st.session_state.ordre_quiz_tab2_dos_aleatoire = questions_dos2_sources

    if "champs_dos2_clean" not in st.session_state:
        st.session_state.champs_dos2_clean = [
            ("1. Le dosage colorimétrique repose sur la détection visuelle d'un .......... de teinte.", ["Choisir...", "changement", "palier"], "changement", "dos2_t1"),
            ("2. Pour repérer l'équivalence d'un acide incolore, on ajoute un .......... coloré.", ["Choisir...", "indicateur", "solvant"], "indicateur", "dos2_t2"),
            ("3. L'intervalle de pH où le témoin change de couleur s'appelle la zone de ..........", ["Choisir...", "virage", "calibre"], "virage", "dos2_t3"),
            ("4. Le BBT prend une coloration verte caractéristique à la .......... exacte.", ["Choisir...", "neutralité", "basicité"], "neutralité", "dos2_t4"),
            ("5. La phénolphtaléine reste parfaitement .......... en milieu acide.", ["Choisir...", "incolore", "rouge"], "incolore", "dos2_t5"),
            ("6. À l'équivalence, les réactifs sont introduits en proportions ..........", ["Choisir...", "stœchiométriques", "égales"], "stœchiométriques", "dos2_t6"),
            ("7. Dépasser le volume équivalent signifie que la solution titrante est en ..........", ["Choisir...", "excès", "défaut"], "excès", "dos2_t7"),
            ("8. L'observation de la couleur finale doit persister pendant au moins dix ..........", ["Choisir...", "secondes", "heures"], "secondes", "dos2_t8"),
            ("9. L'hélianthine vire au jaune orangé lorsque le milieu devient ..........", ["Choisir...", "basique", "acide"], "basique", "dos2_t9"),
            ("10. Le versement final précis s'effectue obligatoirement au ..........", ["Choisir...", "goutte-à-goutte", "gros-débit"], "goutte-à-goutte", "dos2_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos2_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos2_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_histoire_dosages(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Histoire et intérêts) sur deux colonnes."""
    import random

    questions_dos1_sources = [
        {"id": "qh1", "q": "Quel ingénieur et chimiste français a développé le premier titrage industriel au chlore en 1786 ?", "options": ["Henri Descroizilles", "Louis-Joseph Gay-Lussac", "Antoine Lavoisier"], "rep": "Henri Descroizilles"},
        {"id": "qh2", "q": "Quel outil en verre gradué incontournable du dosage a été inventé et popularisé par Gay-Lussac ?", "options": ["La burette graduée", "Le tube à essai", "Le ballon à fond rond"], "rep": "La burette graduée"},
        {"id": "qh3", "q": "Dans quel secteur économique les premiers dosages ont-ils été inventés au dix-huitième siècle ?", "options": ["Les industries manufacturières (vinaigre, savon, textile)", "La recherche pétrolière", "La pharmacie spatiale"], "rep": "Les industries manufacturières (vinaigre, savon, textile)"},
        {"id": "qh4", "q": "Quel est le but fondamental de toute manipulation de dosage ou de titrage au laboratoire ?", "options": ["Déterminer la concentration inconnue d'une espèce", "Changer la couleur d'une solution pour s'amuser", "Faire bouillir un liquide le plus vite possible"], "rep": "Déterminer la concentration inconnue d'une espèce"},
        {"id": "qh5", "q": "Comment qualifie-t-on l'armoire de stockage contenant le liquide de concentration connue inséré dans la burette ?", "options": ["La solution titrante", "La solution titrée", "L'indicateur coloré"], "rep": "La solution titrante"},
        {"id": "qh6", "q": "Comment qualifie-t-on la solution de concentration inconnue placée dans le bécher inférieur ?", "options": ["La solution titrée", "La solution titrante", "Le solvant distillé"], "rep": "La solution titrée"},
        {"id": "qh7", "q": "Quelle opération menée sur un produit commercial (comme le vinaigre) relève typiquement du dosage ?", "options": ["Le contrôle qualité réglementaire", "La solidification par le gel", "La pesée de l'emballage plastique"], "rep": "Le contrôle qualité réglementaire"},
        {"id": "qh8", "q": "Quel dispositif mécanique permet d'homogénéiser le mélange en continu dans le bécher ?", "options": ["L'agitateur magnétique", "Le robinet en téflon", "Le thermomètre digital"], "rep": "L'agitateur magnétique"},
        {"id": "qh9", "q": "Au dix-huitième siècle, sur quel unique repère reposait la détection de la fin de la réaction ?", "options": ["Un changement visuel de couleur", "Une mesure de tension électrique", "Une analyse par ordinateur"], "rep": "Un changement visuel de couleur"},
        {"id": "qh10", "q": "Doser la présence de nitrates dans une nappe phréatique répond à un impératif de :", "options": ["Sécurité sanitaire et environnementale", "Production industrielle de masse", "Fermentation alcoolique"], "rep": "Sécurité sanitaire et environnementale"}
    ]

    if "ordre_quiz_tab1_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos1_sources)
        st.session_state.ordre_quiz_tab1_dos_aleatoire = questions_dos1_sources

    # Liste de synthèse de texte à trous structurée en tuples
    if "champs_dos1_clean" not in st.session_state:
        st.session_state.champs_dos1_clean = [
            ("1. Déterminer une concentration inconnue au laboratoire constitue un ..........", ["Choisir...", "dosage", "étalonnage"], "dosage", "dos1_t1"),
            ("2. L'inventeur de la burette graduée en verre volumétrique est ..........", ["Choisir...", "Gay-Lussac", "Descroizilles"], "Gay-Lussac", "dos1_t2"),
            ("3. Les besoins historiques initiaux sont nés au cœur des filières de la ..........", ["Choisir...", "vinaigrerie", "pétrochimie"], "vinaigrerie", "dos1_t3"),
            ("4. La solution dont on cherche à mesurer l'inconnue est la solution ..........", ["Choisir...", "titrée", "titrante"], "titrée", "dos1_t4"),
            ("5. La solution de référence connue versée s'appelle la solution ..........", ["Choisir...", "titrante", "titrée"], "titrante", "dos1_t5"),
            ("6. Le réservoir cylindrique supérieur en verre gradué est la ..........", ["Choisir...", "burette", "éprouvette"], "burette", "dos1_t6"),
            ("7. Le récipient de réception inférieur accueillant le barreau est le ..........", ["Choisir...", "bécher", "erlenmeyer"], "bécher", "dos1_t7"),
            ("8. Analyser la conformité d'un article en magasin relève du contrôle ..........", ["Choisir...", "qualité", "thermique"], "qualité", "dos1_t8"),
            ("9. Suivre la pollution des eaux de rivières garantit la sécurité ..........", ["Choisir...", "sanitaire", "commerciale"], "sanitaire", "dos1_t9"),
            ("10. Brasser constamment le milieu requiert un agitateur ..........", ["Choisir...", "magnétique", "manuel"], "magnétique", "dos1_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique et Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_dos_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dos_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_dos1_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_dos1_clean", disabled=verrouille, label_visibility="collapsed")


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
    st.header("Historique et pourquoi faire des dosages")
    
    # --- SECTION COURS : LES FONDEMENTS DE L'ANALYSE ---
    st.subheader("Histoire des Sciences : De la vinaigrerie au laboratoire moderne")
    st.write(
        "L'origine des dosages chimiques remonte au dix-huitième siècle, au cœur de l'essor industriel de l'Europe. "
        "À cette époque, les fabricants de textile, de savon et de vinaigre avaient un besoin crucial de connaître "
        "la pureté et la concentration de leurs matières premières pour garantir la qualité de leur production.\n\n"
        "La première méthode de titrage documentée est attribuée au chimiste français **Henri Descroizilles** en 1786, "
        "qui a développé un appareil pour mesurer la force des solutions de blanchiment à base de chlore. Quelques années "
        "plus tard, le célèbre savant **Louis-Joseph Gay-Lussac** perfectionne radicalement la technique en inventant "
        "la **burette graduée en verre** et la pipette, introduisant ainsi la méthode volumétrique moderne.\n\n"
        "Au départ, ces analyses reposaient uniquement sur l'observation visuelle d'un changement de couleur. "
        "Le vingtième siècle a ensuite révolutionné la discipline en y associant des instruments physiques électroniques "
        "(pH-mètre, conductimètre, spectrophotomètre), permettant d'atteindre une précision microscopique."
    )
    
    st.divider()
    
    st.subheader("Pourquoi faire un dosage ?")
    st.write(
        "Doser (ou titrer) une solution consiste à déterminer la **concentration molaire** ou massique d'une espèce chimique "
        "inconnue présente dans un liquide. C'est une démarche d'analyse quantitative fondamentale qui répond à trois grands objectifs :\n\n"
        "* **Le contrôle qualité :** Vérifier qu'un produit commercial respecte les normes (concentration en acide du vinaigre, taux de chlore de l'eau de Javel, pureté d'un médicament).\n"
        "* **La sécurité sanitaire :** Mesurer la quantité de polluants ou de contaminants dans l'environnement ou l'alimentation (nitrates dans l'eau potable, acidité d'un lait).\n"
        "* **Le suivi d'une transformation :** Comprendre comment évolue un système chimique en mesurant la disparition des réactifs ou l'apparition des produits au cours du temps."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        st.write("**Le concept imagé par la caricature**")
        st.write(
            "Pour comprendre le principe d'un dosage, on peut imaginer la caricature d'une douane microscopique "
            "placée à l'entrée d'un village. Les molécules inconnues dans le bécher représentent une foule de voyageurs. "
            "Le réactif versé par la burette agit comme un agent de contrôle qui distribue un ticket à chaque voyageur. "
            "En comptant exactement le nombre de tickets distribués jusqu'à ce que la foule soit totalement contrôlée, "
            "le chimiste peut déduire le nombre précis d'individus présents à l'origine, sans avoir besoin de les voir un par un."
        )
        try:
            st.image("caricature_histoire_dosage.jpg", caption="Caricature de l'analyse quantitative : Le comptage méthodique des molécules")
        except Exception:
            st.warning("L'image 'caricature_histoire_dosage.jpg' est introuvable.")

    with col_hist2:
        st.write("**Le montage expérimental de référence**")
        st.write(
            "Sur un schéma de laboratoire normalisé, un dosage met toujours en relation deux acteurs clés :\n"
            "1. **La solution titrée :** C'est le liquide contenant l'espèce de concentration inconnue. Elle est placée dans le bécher inférieur.\n"
            "2. **La solution titrante :** C'est le liquide de concentration parfaitement connue, placé dans la burette graduée supérieure.\n\n"
            "L'agitateur magnétique assure l'homogénéisation constante du mélange, tandis que le robinet de la burette permet de verser "
            "le réactif titrant goutte à goutte jusqu'à l'obtention de l'équivalence."
        )
        try:
            st.image("montage_general_dosage.jpg", caption="Schéma normalisé des composants d'un titrage volumétrique classique")
        except Exception:
            st.warning("L'image 'montage_general_dosage.jpg' est introuvable.")
            
    st.divider()

    if "suite_verrouille_tab1_dosages" not in st.session_state:
        st.session_state.suite_verrouille_tab1_dosages = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_dosages

    # Affichage du module de questions spécifique à l'histoire et aux objectifs
    afficher_atelier_histoire_dosages(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")


    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique et intérêts des dosages.",
        key="check_certif_dos1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_dos_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q1 += 1.0

            score_t1 = 0.0
            if "champs_dos1_clean" in st.session_state:
                for ligne in st.session_state.champs_dos1_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_dos1_clean", "Choisir...") == attendu: score_t1 += 1.0

            st.session_state.score_suite1_dos_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_dos_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_dos = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_dosages = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ ---
    if st.session_state.get("suite_verrouille_tab1_dosages", False):
        scr1_t1 = st.session_state.get("score_suite1_dos_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_dos_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_dos", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")


        # AJOUTEZ IMPÉRATIVEMENT CES TROIS LIGNES ICI POUR FIXER LE CRASH :
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
        st.success(f"ATELIER HISTORIQUE ET INTÉRÊTS SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_dos1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Dosages - {n_eleve}</title>
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
                <p>Atelier 1 : Historique des techniques volumétriques et intérêts des dosages</p>
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
        if "ordre_quiz_tab1_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction de la synthèse de texte
        if "champs_dos1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML
        html_export_dos1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos1 = preparer_nom_fichier("Rapport_Histoire_Dosages").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_dos1,
            file_name=nom_fichier_html_dos1,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Dosage colorimétrique")
    
    # --- SECTION COURS : LES PRINCIPES DE LA COLORIMÉTRIE ---
    st.subheader("Principe fondamental du titrage colorimétrique")
    st.write(
        "Le dosage colorimétrique est la méthode d'analyse quantitative la plus visuelle et la plus rapide du laboratoire. "
        "Son principe repose sur un changement brutal et persistant de la **couleur du milieu réactionnel** au moment exact de l'équivalence.\n\n"
        "Pour réaliser ce type de dosage, deux configurations sont possibles :\n"
        "* **Le réactif ou le produit est naturellement coloré :** Par exemple, lors du dosage des ions ferreux par les ions permanganate, "
        "la solution passe instantanément d'un milieu incolore à une teinte violette persistante dès que la première goutte en excès est versée.\n"
        "* **Les réactifs sont totalement incolores (cas des réactions acido-basiques) :** Il est alors obligatoire d'ajouter "
        "quelques gouttes d'un **indicateur coloré**. Cette substance chimique change de structure et de couleur en fonction du pH ou du potentiel "
        "chimique de la solution, matérialisant ainsi l'équivalence aux yeux du manipulateur."
    )
    
    st.divider()
    
    st.subheader("Les indicateurs colorés acido-basiques de référence")
    st.write(
        "Pour choisir le bon indicateur coloré, sa **zone de virage** (l'intervalle de pH dans lequel il change de couleur) "
        "à 25°C doit impérativement englober la valeur du pH attendue à l'équivalence. Voici les trois indicateurs les plus utilisés :"
    )
    
    # Tableau d'inventaire des indicateurs colorés
    dico_indicateurs = {
        "Hélianthine": {"zone": "3,1 - 4,4", "acide": "Rouge", "basique": "Jaune orangé", "usage": "Titrage des acides faibles par des bases fortes."},
        "Bleu de bromothymol (BBT)": {"zone": "6,0 - 7,6", "acide": "Jaune", "basique": "Bleu (Milieu neutre = Vert)", "usage": "Titrage des acides forts par des bases fortes (Équivalence neutre à 7)."},
        "Phénolphtaléine": {"zone": "8,2 - 10,0", "acide": "Incolore", "basique": "Rose fuchsia", "usage": "Titrage des bases faibles par des acides forts."}
    }
    
    data_table_ind = []
    for nom, infos in dico_indicateurs.items():
        data_table_ind.append([nom, infos["zone"], infos["acide"], infos["basique"], infos["usage"]])
    
    df_ind = pd.DataFrame(data_table_ind, columns=["Nom de l'indicateur", "Zone de virage (pH)", "Teinte acide", "Teinte basique", "Usage recommandé"])
    st.dataframe(df_ind, use_container_width=True, hide_index=True)

    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_col1, col_col2 = st.columns(2)
    with col_col1:
        st.write("**Le virage chromatique expliqué par la caricature**")
        st.write(
            "Pour imager le virage d'un indicateur coloré, on peut imaginer la caricature d'un caméléon microscopique "
            "assis au fond du bécher. Tant qu'il est entouré d'atomes d'acide, il garde son habit jaune de protection. "
            "Mais dès que la solution titrante détruit le tout dernier acide à l'équivalence, la moindre goutte de base supplémentaire "
            "le surprend : il change instantanément d'habit pour revêtir sa parure bleue. Le chimiste surveille attentivement "
            "le réveil de ce caméléon pour fermer instantanément le robinet de sa burette."
        )
        try:
            st.image("caricature_dosage_colorimetrique.jpg", caption="Caricature du virage : Le changement d'état visuel instantané")
        except Exception:
            st.warning("L'image 'caricature_dosage_colorimetrique.jpg' est introuvable.")

    with col_col2:
        st.write("**La manipulation et l'observation expérimentale**")
        st.write(
            "La réussite d'un dosage colorimétrique exige un protocole strict. Le versement de la solution titrante "
            "s'effectue rapidement au début, puis s'interrompt pour passer à un versement rigoureux **goutte à goutte** "
            "dès que la couleur commence à s'estomper plus lentement autour du barreau aimanté.\n\n"
            "Le volume équivalent exact (Veq) correspond au volume inscrit sur la burette à l'instant précis où le changement "
            "de couleur se diffuse dans la totalité du bécher et persiste pendant au moins **dix secondes** sous agitation constante."
        )
        try:
            st.image("manipulation_colorimetrie.jpg", caption="Protocole expérimental de détection du volume équivalent à l'œil nu")
        except Exception:
            st.warning("L'image 'manipulation_colorimetrie.jpg' est introuvable.")

    st.subheader("Exemple concret de laboratoire : Détermination de l'acidité d'un vinaigre commercial")
    st.write(
        "Pour contrôler la qualité d'un vinaigre de vin, un technicien réalise le titrage de l'**acide acétique** "
        "(espèce incolore à doser) par une solution titrante de **soude caustique** (hydroxyde de sodium, également incolore).\n\n"
        "La réaction de neutralisation acido-basique s'écrit de la façon suivante :\n"
        "**CH₃COOH + OH⁻ -> CH₃COO⁻ + H₂O**\n\n"
        "Comme les deux réactifs de départ sont totalement transparents comme de l'eau, il est impossible de repérer "
        "la fin de la destruction de l'acide à l'œil nu. Le manipulateur ajoute donc 2 gouttes de **phénolphtaléine** dans son bécher :\n"
        "* **Avant l'équivalence :** Le milieu contient un excès d'acide acétique. La phénolphtaléine reste **parfaitement incolore**. Le liquide est transparent.\n"
        "* **À l'équivalence exacte :** La totalité de l'acide acétique a été consommée par la soude. La solution devient neutre.\n"
        "* **Juste après l'équivalence :** La moindre goutte de soude versée en excès rend le milieu basique. La phénolphtaléine réagit instantanément "
        "et la solution prend une **coloration rose fuchsia persistante**. Le technicien coupe immédiatement le robinet : il a trouvé le volume équivalent."
    )            
    st.divider()

    # --- SECTION LOGIQUE : ZONE D'EXERCICES ET SCELLÉ DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_colorimetrie" not in st.session_state:
        st.session_state.suite_verrouille_tab2_colorimetrie = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_colorimetrie

    # Appel de la fonction d'Atelier
    afficher_atelier_colorimetrie(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Dosage colorimétrique.",
        key="check_certif_dos2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_dos_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q2 += 1.0

            score_t2 = 0.0
            if "champs_dos2_clean" in st.session_state:
                for ligne in st.session_state.champs_dos2_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_dos2_clean", "Choisir...") == attendu: score_t2 += 1.0

            st.session_state.score_suite2_dos_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_dos_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_dos = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_colorimetrie = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ ---
    if st.session_state.get("suite_verrouille_tab2_colorimetrie", False):
        scr1_t2 = st.session_state.get("score_suite2_dos_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_dos_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_dos", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DOSAGE COLORIMÉTRIQUE SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_dos2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Colorimétrie - {n_eleve}</title>
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
                <p>Atelier 2 : Titrages colorimétriques et choix des indicateurs de virage</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
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
        if "ordre_quiz_tab2_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos2 += """
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
        if "champs_dos2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 2
        html_export_dos2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos2 = preparer_nom_fichier("Rapport_Colorimetrie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_dos2,
            file_name=nom_fichier_html_dos2,
            mime="text/html",
            use_container_width=True
        )




with tab3:
    st.header("Dosage conductimétrique")
    
    # --- SECTION COURS : LES PRINCIPES DE LA CONDUCTIMÉTRIE ---
    st.subheader("Principe fondamental du titrage conductimétrique")
    st.write(
        "Le dosage conductimétrique est une méthode d'analyse physique qui consiste à suivre l'évolution de la "
        "**conductivité (sigma)** ou de la conductance (G) de la solution au cours du versement du réactif titrant. "
        "Cette technique repose sur le fait que la capacité d'une solution à conduire le courant dépend de la nature "
        "et de la concentration des ions en mouvement.\n\n"
        "Chaque type d'ion possède une conductivité molaire ionique propre (notée lambda). Lors de la réaction, "
        "le remplacement progressif d'ions très conducteurs par d'autres moins conducteurs (ou la disparition d'ions "
        "sous forme de précipité solide ou de molécules d'eau) modifie de façon linéaire la conductivité globale du milieu."
    )
    
    st.divider()
    
    # --- EXEMPLE CONCRET ET SCANNABLE ---
    st.subheader("Exemple d'application : Titrage des ions chlorure par les ions argent")
    st.write(
        "Prenons l'exemple incontournable du dosage des **ions chlorure (Cl⁻)** contenus dans une eau saumâtre par une solution "
        "de nitrate d'argent, composée d'**ions argent (Ag⁺)** et d'ions nitrate (NO₃⁻).\n\n"
        "La réaction chimique de précipitation s'écrit : **Ag⁺ + Cl⁻ -> AgCl (solide)**\n\n"
        "* **Avant l'équivalence :** Chaque ion argent Ag⁺ versé consomme un ion chlorure Cl⁻ pour former un précipité blanc. "
        "L'ion chlorure disparu est remplacé numériquement dans la solution par un ion nitrate NO₃⁻. Comme la conductivité de NO₃⁻ "
        "est inférieure à celle de Cl⁻, **la conductivité totale de la solution diminue de façon linéaire**.\n"
        "* **Après l'équivalence :** Il n'y a plus aucun ion chlorure Cl⁻ disponible dans le bécher. Les ions argent Ag⁺ et nitrate NO₃⁻ "
        "versés par la burette s'accumulent sans réagir. **La conductivité globale de la solution réaugmente alors brutalement**."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_cond1, col_cond2 = st.columns(2)
    with col_cond1:
        st.write("**Le comportement ionique expliqué par la caricature**")
        st.write(
            "Pour imager le comportement des ions, on peut utiliser la caricature d'un tapis roulant d'usine "
            "qui transporte des colis de tailles différentes. Les ions chlorure Cl⁻ sont comme des déménageurs ultra-rapides. "
            "Les ions argent Ag⁺ sont les inspecteurs qui les attrapent et les figent au sol sous forme de blocs de pierre (le précipité AgCl). "
            "Pendant ce temps, les ions nitrate NO₃⁻, plus lents, s'installent sur le tapis. Comme les travailleurs rapides "
            "sont remplacés par des travailleurs lents, l'activité globale baisse. Une fois tous les chlorures capturés, les inspecteurs "
            "argent s'accumulent sur le tapis, ce qui fait remonter l'activité en flèche."
        )
        try:
            st.image("caricature_dosage_conductimetrique.jpg", caption="Caricature de la substitution ionique microscopique")
        except Exception:
            st.warning("L'image 'caricature_dosage_conductimetrique.jpg' est introuvable.")

    with col_col2:
        st.write("**Le graphique et la détection géométrique**")
        st.write(
            "Contrairement au dosage colorimétrique où l'on s'arrête au changement de couleur, le dosage conductimétrique "
            "impose de mesurer la conductivité pour plusieurs volumes versés avant et après l'équivalence.\n\n"
            "Le graphique présente **deux portions de droites de pentes différentes**. L'intersection exacte de ces deux droites "
            "matérialise une **rupture de pente** qui indique avec précision le volume équivalent (Veq), sans qu'il soit nécessaire "
            "de deviner un virage visuel à l'œil nu."
        )
        try:
            st.image("graphique_conductimetrie.jpg", caption="Détermination géométrique du volume équivalent par rupture de pente")
        except Exception:
            st.warning("L'image 'graphique_conductimetrie.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE D'EXERCICES ET SCELLÉ DE L'ATELIER 3 ---
    if "suite_verrouille_tab3_conductimetrie" not in st.session_state:
        st.session_state.suite_verrouille_tab3_conductimetrie = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_conductimetrie

    # Appel de la fonction d'Atelier
    afficher_atelier_conductimetrie(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Dosage conductimétrique.",
        key="check_certif_dos3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_dos_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q3 += 1.0

            score_t3 = 0.0
            if "champs_dos3_clean" in st.session_state:
                for ligne in st.session_state.champs_dos3_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_dos3_clean", "Choisir...") == attendu: score_t3 += 1.0

            st.session_state.score_suite3_dos_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_dos_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_dos = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_conductimetrie = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ ---
    if st.session_state.get("suite_verrouille_tab3_conductimetrie", False):
        scr1_t3 = st.session_state.get("score_suite3_dos_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_dos_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_dos", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DOSAGE CONDUCTIMÉTRIQUE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_dos3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Conductimétrie - {n_eleve}</title>
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
                <p>Atelier 3 : Suivi conductimétrique des solutions ioniques et ruptures de pentes</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #047857;">
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
        if "ordre_quiz_tab3_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos3 += """
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
        if "champs_dos3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 3
        html_export_dos3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos3 = preparer_nom_fichier("Rapport_Conductimetrie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_dos3,
            file_name=nom_fichier_html_dos3,
            mime="text/html",
            use_container_width=True
        )             


with tab4:
    st.header("Dosage spectrophotométrique")
    
    # --- SECTION COURS : LES PRINCIPES DE LA SPECTROPHOTOMÉTRIE ---
    st.subheader("Principe fondamental de la spectrophotométrie")
    st.write(
        "Le dosage spectrophotométrique est une méthode d'analyse optique indirecte. "
        "Son principe repose sur la mesure de l'**absorbance (A)**, une grandeur physique sans unité qui quantifie "
        "la proportion de lumière qu'une solution colorée absorbe lorsqu'un faisceau lumineux traverse une cuve d'épaisseur donnée.\n\n"
        "Lorsqu'une solution est colorée, elle absorbe préférentiellement certaines longueurs d'onde de la lumière blanche. "
        "Pour maximiser la précision des mesures, le chimiste règle toujours le spectrophotomètre sur la longueur d'onde "
        "où l'absorption est maximale (notée lambda max). Cette valeur se situe généralement dans la couleur complémentaire "
        "de la teinte observée à l'œil nu (par exemple, une solution bleue absorbe un maximum de lumière dans l'orangé)."
    )
    
    st.divider()
    
    # --- LA LOI DE BEER-LAMBERT ---
    st.subheader("La loi de Beer-Lambert")
    st.write(
        "Pour des solutions suffisamment diluées, l'absorbance d'une espèce chimique colorée est strictement proportionnelle "
        "à sa concentration molaire. Cette relation fondamentale s'énonce par la loi de Beer-Lambert :\n\n"
        "$$A = \\epsilon \\cdot l \\cdot C$$\n\n"
        "Où :\n"
        "* **A** est l'absorbance de la solution (sans unité).\n"
        "* $\\epsilon$ (epsilon) est le coefficient d'absorption molaire (en L/mol/cm), dépendant de l'espèce et de la longueur d'onde.\n"
        "* **l** est l'épaisseur de la cuve traversée par la lumière (en cm, généralement égale à 1,0 cm).\n"
        "* **C** est la concentration molaire de l'espèce colorée (en mol/L).\n\n"
        "En regroupant les constantes, la loi s'écrit de manière simplifiée sous la forme d'une fonction linéaire : **A = k * C**. "
        "Le graphique représentant l'absorbance en fonction de la concentration est donc une droite passant par l'origine."
    )
    
    st.subheader("Exemple concret de laboratoire : Dosage du sulfate de cuivre")
    st.write(
        "Pour déterminer la concentration inconnue d'une solution de sulfate de cuivre (de couleur bleue), le manipulateur suit un protocole rigoureux :\n"
        "1. **Préparation d'une gamme d'étalonnage :** Il prépare plusieurs solutions étalons de concentrations connues par dilution d'une solution mère.\n"
        "2. **Réglage du blanc :** Il remplit une cuve avec le solvant seul (eau distillée) et règle l'appareil pour forcer l'absorbance à zéro.\n"
        "3. **Mesure et tracé :** Il mesure l'absorbance de chaque étalon à 620 nm (dans l'orangé) et trace la **droite d'étalonnage**.\n"
        "4. **Détermination de l'inconnu :** Il mesure enfin l'absorbance de la solution inconnue et reporte graphiquement sa valeur sur la droite pour en déduire sa concentration."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_spec1, col_spec2 = st.columns(2)
    with col_spec1:
        st.write("**Le blocage de la lumière expliqué par la caricature**")
        st.write(
            "Pour imager l'absorbance, on peut dessiner la caricature d'une forêt de petits bonshommes bleus "
            "qui barrent la route à des projectiles de peinture orange lancés par une machine. "
            "Si la forêt est très peu dense (solution diluée), la grande majorité des projectiles traversent la cuve "
            "sans obstacle. Si la forêt devient très dense (solution concentrée), les bonshommes interceptent presque "
            "tous les projectiles. L'appareil de détection placé à la sortie compte le nombre de projectiles manquants "
            "pour en déduire instantanément le nombre de bonshommes installés dans la cuve."
        )
        try:
            st.image("caricature_dosage_spectrophotometrique.jpg", caption="Caricature de l'interception des photons par les molécules colorées")
        except Exception:
            st.warning("L'image 'caricature_dosage_spectrophotometrique.jpg' est introuvable.")

    with col_spec2:
        st.write("**Le graphique d'étalonnage linéaire**")
        st.write(
            "Le graphique de référence présente les points expérimentaux alignés le long d'une droite passant par l'origine. "
            "Cette linéarité parfaite confirme le respect de la loi de Beer-Lambert.\n\n"
            "Si l'absorbance d'une solution inconnue est trop élevée (supérieure à 2), la loi ne s'applique plus car les molécules "
            "sont trop proches et s'induisent mutuellement en erreur. Il est alors obligatoire de **diluer précisément** la solution "
            "inconnue avant de procéder à sa mesure."
        )
        try:
            st.image("graphique_spectrophotometrie.jpg", caption="Droite d'étalonnage expérimentale A = f(C) et lecture de l'inconnu")
        except Exception:
            st.warning("L'image 'graphique_spectrophotometrie.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE D'EXERCICES ET SCELLÉ DE L'ATELIER 4 ---
    if "suite_verrouille_tab4_spectrophotometrie" not in st.session_state:
        st.session_state.suite_verrouille_tab4_spectrophotometrie = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_spectrophotometrie

    # Appel de la fonction d'Atelier
    afficher_atelier_spectrophotometrie(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Dosage spectrophotométrique.",
        key="check_certif_dos4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_dos_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q4 += 1.0

            score_t4 = 0.0
            if "champs_dos4_clean" in st.session_state:
                for ligne in st.session_state.champs_dos4_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_dos4_clean", "Choisir...") == attendu: score_t4 += 1.0

            st.session_state.score_suite4_dos_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_dos_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_dos = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_spectrophotometrie = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ POUR L'ATELIER 4 ---
    if st.session_state.get("suite_verrouille_tab4_spectrophotometrie", False):
        scr1_t4 = st.session_state.get("score_suite4_dos_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_dos_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_dos", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DOSAGE SPECTROPHOTOMÉTRIQUE SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_dos4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Spectrophotométrie - {n_eleve}</title>
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
                <p>Atelier 4 : Loi de Beer-Lambert et dosages par étalonnage spectrophotométrique</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #e11d48;">
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
        if "ordre_quiz_tab4_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos4 += """
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
        if "champs_dos4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos4_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 4
        html_export_dos4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos4 = preparer_nom_fichier("Rapport_Spectrophotometrie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_dos4,
            file_name=nom_fichier_html_dos4,
            mime="text/html",
            use_container_width=True
        )



with tab5:
    st.header("Dosage pH-métrique")
    
    # --- SECTION COURS : LES PRINCIPES DU DOSAGE PH-MÉTRIQUE ---
    st.subheader("Histoire des Sciences : La naissance de la volumétrie instrumentale")
    st.write(
        "L'opération de dosage, ou titrage, a été conceptualisée à la fin du dix-huitième siècle. "
        "Avec l'avènement de l'électronique au vingtième siècle, les scientifiques ont remplacé l'œil humain "
        "par la sonde d'un pH-mètre. En versant une base goutte à goutte dans un acide et en mesurant le pH "
        "à chaque ajout, ils ont découvert qu'il existait une brusque variation de la mesure, appelée "
        "**saut de pH**, permettant de déterminer la concentration inconnue avec une précision chirurgicale."
    )
    
    st.divider()
    
    st.subheader("La neutralisation acido-basique")
    st.write(
        "Doser une solution consiste à déterminer sa concentration inconnue en la faisant réagir avec "
        "une autre solution dont on connaît parfaitement la concentration. Lors du dosage d'un acide fort "
        "par une base forte (par exemple, l'acide chlorhydrique mélangé avec de la soude) :\n\n"
        "* **La réaction chimique :** Les ions oxonium $H_3O^+$ responsables de l'acidité s'associent avec "
        "les ions hydroxyde $OH^-$ responsables de la basicité pour former des molécules d'eau pure ($H_2O$). "
        "La formule de la réaction s'écrit : **$H_3O^+ + OH^- \\rightarrow 2 H_2O$**.\n"
        "* **L'équivalence :** C'est l'instant précis où tout l'acide initial a été détruit par la base versée. "
        "À cet endroit exact, la solution devient parfaitement neutre. Pour un mélange d'acide fort et de base forte, "
        "le pH à l'équivalence est **rigoureusement égal à 7,0** à 25°C."
    )
    
    col_dos1, col_dos2 = st.columns(2)
    with col_dos1:
        st.write("**Le protocole expérimental et sa caricature**")
        st.write(
            "Sur un schéma de montage officiel, la solution à doser se place dans un bécher posé sur un agitateur "
            "magnétique, tandis que la solution titrante est versée lentement à l'aide d'une burette graduée.\n\n"
            "Pour imager cette expérience, on peut dessiner la caricature d'un champ de bataille chimique. "
            "Au début, l'acide est maître du terrain (pH très bas). À mesure que l'on verse la base, ses soldats "
            "neutralisent les acides un par un pour former de l'eau inoffensive. À l'équivalence exacte, il n'y a plus "
            "aucun réactif en excès : la neutralité absolue règne (pH = 7,0). Si l'on continue de verser la base, celle-ci devient "
            "majoritaire et le pH s'envole vers 14,0."
        )
        try:
            st.image("circuit_dosage_ph.jpg", caption="Schéma normalisé d'un montage de dosage ph-métrique")
        except Exception:
            st.warning("L'image 'circuit_dosage_ph.jpg' est introuvable.")

    with col_dos2:
        st.write("**Simulation mathématique de la courbe de titrage**")
        st.write(
            "Voici le graphique théorique représentant l'évolution du pH en fonction du volume de base versé. "
            "Vous pouvez observer la forme caractéristique en 'S' avec son saut de pH vertical à l'équivalence."
        )
        
        # --- GRAPHIOUE MATPLOTLIB NATIF DU DOSAGE ---
        import matplotlib.pyplot as plt
        fig_curve, ax_curve = plt.subplots(figsize=(5, 3.8), facecolor="white")
        ax_curve.set_facecolor("white")
        
        # Simulation d'une courbe de titrage acide fort / base forte
        v_base = np.linspace(0, 20, 200)
        ph_sim = []
        for v in v_base:
            if v < 10:
                ph_sim.append(1.0 + 0.5 * (v / 10.0) + 0.5 * np.log10(10.0 / (10.0 - v + 1e-5)))
            elif np.isclose(v, 10):
                ph_sim.append(7.0)
            else:
                ph_sim.append(13.0 - 0.5 * ((20.0 - v) / 10.0) - 0.5 * np.log10(10.0 / (v - 10.0 + 1e-5)))
        
        ph_sim = np.clip(ph_sim, 1.0, 13.0)
        ax_curve.plot(v_base, ph_sim, color="#7c3aed", linewidth=3, label="Courbe pH-métrique")
        
        # Point d'équivalence E
        ax_curve.plot(10, 7, marker="o", color="#ef4444", markersize=8, label="Équivalence E (pH=7)")
        ax_curve.axhline(7, color="#cbd5e1", linestyle="--")
        ax_curve.axvline(10, color="#cbd5e1", linestyle="--")
        
        ax_curve.set_xlabel("Volume de base versé Vb (mL)", fontsize=9)
        ax_curve.set_ylabel("pH de la solution", fontsize=9)
        ax_curve.set_title("Évolution du pH lors du dosage", fontsize=10, weight="bold")
        ax_curve.set_xlim(0, 20)
        ax_curve.set_ylim(0, 14)
        ax_curve.legend(fontsize=8, loc="lower right")
        ax_curve.grid(True, color="#f1f5f9")
        st.pyplot(fig_curve)
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_phmetrie" not in st.session_state:
        st.session_state.suite_verrouille_tab5_phmetrie = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_phmetrie

    # Affichage du module de questions spécifique aux dosages
    afficher_atelier_phmetrie(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les dosages pH-métriques.",
        key="check_certif_dos5_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_dos_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q5 += 1.0

            score_t5 = 0.0
            if "champs_dos5_clean" in st.session_state:
                for ligne in st.session_state.champs_dos5_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_dos5_clean", "Choisir...") == attendu: score_t5 += 1.0

            st.session_state.score_suite5_dos_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_dos_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_dos = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_phmetrie = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 5 ---
    if st.session_state.get("suite_verrouille_tab5_phmetrie", False):
        scr1_t5 = st.session_state.get("score_suite5_dos_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_dos_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_dos", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DOSAGE PH-MÉTRIQUE SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_ph5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport pH-métrie - {n_eleve}</title>
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
                <p>Atelier 5 : Les dosages pH-métriques, saut de pH, équivalence et neutralisation</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #7c3aed;">
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
        if "ordre_quiz_tab5_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_ph5 += """
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
        if "champs_dos5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos5_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos5_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_ph5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 5
        html_export_ph5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph5 = preparer_nom_fichier("Rapport_Dosage_pHmetrique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_ph5,
            file_name=nom_fichier_html_ph5,
            mime="text/html",
            use_container_width=True
        )

with tab6:
    st.header("Dosage d'oxydoréduction")
    
    # --- SECTION COURS : LES PRINCIPES DU DOSAGE REDOX ---
    st.subheader("Principe fondamental des titrages d'oxydoréduction")
    st.write(
        "Le dosage d'oxydoréduction (ou dosage redox) est une méthode d'analyse quantitative basée sur un "
        "**transfert d'électrons** entre l'espèce à doser et l'espèce titrante. Contrairement aux titrages acido-basiques "
        "qui font intervenir des transferts de protons, les réactions redox mettent en scène deux acteurs clés :\n\n"
        "* **L'oxydant :** C'est une entité chimique capable de capter un ou plusieurs électrons au cours de la réaction.\n"
        "* **Le réducteur :** C'est une entité chimique capable de céder un ou plusieurs électrons au cours de la réaction.\n\n"
        "La transformation globale résulte de la combinaison simultanée d'une **oxydation** (perte d'électrons subie par le réducteur dosé) "
        "et d'une **réduction** (gain d'électrons opéré par l'oxydant titrant)."
    )
    
    st.divider()
    
    # --- EXEMPLE CONCRET ET SCANNABLE ---
    st.subheader("Exemple concret de laboratoire : Dosage des ions ferreux par le permanganate de potassium")
    st.write(
        "Un exemple classique consiste à déterminer la concentration en **ions ferreux ($Fe^{2+}$)**, un réducteur incolore placé dans le bécher, "
        "par une solution d'un oxydant puissant : le **permanganate de potassium ($K^+ + MnO_4^-$)** versé par la burette.\n\n"
        "L'ion permanganate $MnO_4^-$ possède une couleur violette intense très caractéristique. L'équation de la réaction s'écrit :\n"
        "**$MnO_4^- + 5 Fe^{2+} + 8 H^+ \\rightarrow Mn^{2+} + 5 Fe^{3+} + 4 H_2O$**\n\n"
        "* **Avant l'équivalence :** Chaque goutte de permanganate violette versée rencontre des ions ferreux $Fe^{2+}$. La réaction a lieu immédiatement. "
        "Les ions produits ($Mn^{2+}$ et $Fe^{3+}$) étant pratiquement incolores à ces concentrations, **la solution dans le bécher reste transparente**.\n"
        "* **À l'équivalence exacte :** Tous les ions ferreux $Fe^{2+}$ initialement présents ont été oxydés. Les deux réactifs ont été mélangés dans les proportions stœchiométriques.\n"
        "* **Après l'équivalence :** Les ions ferreux ayant totalement disparu, le moindre ajout de permanganate de potassium n'a plus de partenaire avec qui réagir. "
        "Les ions $MnO_4^-$ s'accumulent dans le bécher, provoquant un **changement de couleur persistant vers le rose ou violet pâle**. Le manipulateur note alors le volume équivalent (Veq)."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_ox1, col_ox2 = st.columns(2)
    with col_ox1:
        st.write("**Le transfert d'électrons expliqué par la caricature**")
        st.write(
            "Pour comprendre le mécanisme microscopique d'une réaction redox, on peut imaginer la caricature d'un jeu de passes "
            "lors d'un match de sport. Les ions ferreux $Fe^{2+}$ circulent sur le terrain en portant chacun un ballon brillant "
            "(l'électron). Les ions permanganate $MnO_4^-$ agissent comme des intercepteurs surpuissants capables d'attraper "
            "5 ballons à la fois. Dès qu'un intercepteur violet entre sur le terrain, il confisque les ballons de 5 joueurs d'un coup, "
            "les rendant instantanément neutres et invisibles. Le jeu s'arrête dès que l'intercepteur violet reste visible sur le terrain, "
            "signifiant qu'il n'y a plus aucun ballon à confisquer."
        )
        try:
            st.image("caricature_dosage_oxydoreduction.jpg", caption="Caricature du transfert d'électrons : La capture méthodique des charges")
        except Exception:
            st.warning("L'image 'caricature_dosage_oxydoreduction.jpg' est introuvable.")

    with col_ox2:
        st.write("**Le suivi par potentiométrie instrumentale**")
        st.write(
            "Dans les laboratoires modernes, l'œil humain peut être remplacé par un système électronique appelé **titrage potentiométrique**.\n\n"
            "On immerge une électrode de mesure en platine et une électrode de référence reliées à un voltmètre de haute précision. "
            "En traçant la courbe de la différence de potentiel (en mV) en fonction du volume versé, on obtient un graphique en forme de 'S' "
            "très similaire à la courbe pH-métrique. L'équivalence se repère alors mathématiquement par un **saut de potentiel** vertical, "
            "offrant une précision de mesure optimale."
        )
        try:
            st.image("graphique_oxydoreduction.jpg", caption="Courbe potentiométrique E = f(V) avec son saut de potentiel caractéristique")
        except Exception:
            st.warning("L'image 'graphique_oxydoreduction.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 6 ---
    if "suite_verrouille_tab6_oxydoreduction" not in st.session_state:
        st.session_state.suite_verrouille_tab6_oxydoreduction = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_oxydoreduction

    # Affichage du module de questions spécifique aux dosages redox
    afficher_atelier_oxydoreduction(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les dosages d'oxydoréduction.",
        key="check_certif_dos6_final_net",
        disabled=verrou_at6,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_dos_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            if "ordre_quiz_tab6_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q6 += 1.0

            score_t6 = 0.0
            if "champs_dos6_clean" in st.session_state:
                for ligne in st.session_state.champs_dos6_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_dos6_clean", "Choisir...") == attendu: score_t6 += 1.0

            st.session_state.score_suite6_dos_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_dos_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_dos = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_oxydoreduction = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 6 ---
    if st.session_state.get("suite_verrouille_tab6_oxydoreduction", False):
        scr1_t6 = st.session_state.get("score_suite6_dos_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_dos_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6_dos", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER REDOX SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_dos6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Oxydoréduction - {n_eleve}</title>
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
                <p>Atelier 6 : Dosages par oxydoréduction, transferts d'électrons et titrages potentiométriques</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
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
        if "ordre_quiz_tab6_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos6 += """
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
        if "champs_dos6_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos6_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos6_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 6
        html_export_dos6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos6 = preparer_nom_fichier("Rapport_Oxydoreduction").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_dos6,
            file_name=nom_fichier_html_dos6,
            mime="text/html",
            use_container_width=True
        )




with tab7:
    st.header("Dosage par précipitation")
    
    # --- SECTION COURS : LES PRINCIPES DE LA PRÉCIPITATION ---
    st.subheader("Principe fondamental des titrages par précipitation")
    st.write(
        "Le dosage par précipitation est une méthode d'analyse quantitative basée sur la formation d'un "
        "**composé solide insoluble** (appelé précipité) lors de la rencontre entre l'espèce à doser et le réactif titrant.\n\n"
        "Chaque solide ionique est caractérisé par une constante d'équilibre appelée **produit de solubilité ($K_s$)**. "
        "Tant que le produit des concentrations des ions en solution est inférieur à ce $K_s$, la solution reste parfaitement limpide. "
        "Dès que ce produit dépasse le $K_s$, les ions s'assemblent pour former des microcristaux solides qui troublent le milieu."
    )
    
    st.divider()
    
    # --- EXEMPLE CONCRET ET SCANNABLE ---
    st.subheader("Exemple concret de laboratoire : Détermination du taux de sel par la méthode de Mohr")
    st.write(
        "Pour mesurer la concentration en **ions chlorure ($Cl^-$)** d'une eau de consommation ou d'une solution saline, "
        "on utilise une solution titrante de nitrate d'argent, qui apporte des **ions argent ($Ag^+$)**. "
        "La réaction principale de précipitation s'écrit de la façon suivante :\n"
        "**$Ag^+ + Cl^- \\rightarrow AgCl_{\\text{(solide)}}$**\n\n"
        "Le chlorure d'argent ($AgCl$) est un solide de couleur blanche qui possède la propriété remarquable de noircir "
        "lorsqu'il reste exposé à la lumière.\n\n"
        "Pour repérer la fin de la précipitation à l'œil nu, on utilise la **méthode de Mohr** en ajoutant quelques gouttes "
        "de chromate de potassium (ions $CrO_4^{2-}$, de couleur jaune) comme indicateur coloré :\n"
        "* **Avant l'équivalence :** Les ions argent $Ag^+$ versés réagissent en priorité avec les ions chlorure $Cl^-$ pour former "
        "le précipité blanc de $AgCl$. La solution prend une apparence de lait blanc. L'indicateur jaune ne réagit pas.\n"
        "* **À l'équivalence exacte :** La totalité des ions chlorure du bécher a été consommée.\n"
        "* **Après l'équivalence :** Les ions chlorure ayant disparu, les ions argent $Ag^+$ versés en excès se lient instantanément "
        "avec les ions chromate $CrO_4^{2-}$ de l'indicateur. Cela provoque la formation immédiate d'un second solide, le chromate d'argent, "
        "qui arbore une **coloration rouge-brique persistante**. Le manipulateur arrête aussitôt le versement."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_pr1, col_pr2 = st.columns(2)
    with col_pr1:
        st.write("**Le piège de la précipitation expliqué par la caricature**")
        st.write(
            "Pour imager ce mécanisme de précipitation sélective, on peut utiliser la caricature d'un filet de pêche "
            "déployé dans une piscine. Les ions chlorure $Cl^-$ sont comme de petits poissons blancs très agiles qui remplissent le bassin. "
            "Les ions argent $Ag^+$ sont des aimants lancés depuis la surface. Dès qu'un aimant entre dans l'eau, il s'associe "
            "indissociablement avec un poisson blanc, formant un lourd bloc de plâtre qui coule au fond (le précipité blanc). "
            "Pendant ce temps, un crabe jaune (l'ion chromate indicateur) dort sur le côté. Dès que le dernier poisson blanc a été piégé, "
            "l'aimant argent suivant tombe directement sur le crabe jaune : le crabe vire instantanément au rouge-brique de colère, "
            "signalant au pêcheur que le bassin est vide."
        )
        try:
            st.image("caricature_dosage_precipitation.jpg", caption="Caricature de la précipitation sélective : Le signal visuel du témoin")
        except Exception:
            st.warning("L'image 'caricature_dosage_precipitation.jpg' est introuvable.")

    with col_pr2:
        st.write("**L'évolution visuelle au cours du titrage**")
        st.write(
            "Expérimentalement, le suivi de la méthode de Mohr montre une transition visuelle nette. Le liquide initial, "
            "légèrement teinté de jaune par le chromate, se transforme rapidement en une suspension d'un blanc laiteux opaque.\n\n"
            "L'équivalence se détecte à la goutte près par l'apparition d'une **nuance orange ou chamois persistant** dans la masse du solide, "
            "matérialisant la formation microscopique des premiers cristaux de chromate d'argent rouge-brique."
        )
        try:
            st.image("manipulation_precipitation.jpg", caption="Stades visuels du dosage de Mohr : Solution initiale, précipitation blanche et équivalence orange")
        except Exception:
            st.warning("L'image 'manipulation_precipitation.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 7 ---
    if "suite_verrouille_tab7_precipitation" not in st.session_state:
        st.session_state.suite_verrouille_tab7_precipitation = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_precipitation

    # Affichage du module de questions spécifique aux dosages par précipitation
    afficher_atelier_precipitation(verrouille=verrou_at7)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat7 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les dosages par précipitation.",
        key="check_certif_dos7_final_net",
        disabled=verrou_at7,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_suite7_dos_official", use_container_width=True, disabled=verrou_at7):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat7: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q7 = 0.0
            if "ordre_quiz_tab7_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab7_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at7_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q7 += 1.0

            score_t7 = 0.0
            if "champs_dos7_clean" in st.session_state:
                for ligne in st.session_state.champs_dos7_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_dos7_clean", "Choisir...") == attendu: score_t7 += 1.0

            st.session_state.score_suite7_dos_p1 = round(float(score_q7), 1)
            st.session_state.score_suite7_dos_p2 = round(float(score_t7), 1)
            st.session_state.score_final_suite7_dos = round(float(score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_precipitation = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 7 ---
    if st.session_state.get("suite_verrouille_tab7_precipitation", False):
        scr1_t7 = st.session_state.get("score_suite7_dos_p1", 0.0)
        scr2_t7 = st.session_state.get("score_suite7_dos_p2", 0.0)
        tot_s_t7 = st.session_state.get("score_final_suite7_dos", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER PRÉCIPITATION SCELLÉ | Note de session : {tot_s_t7:.1f} / 20")

        html_export_dos7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Précipitation - {n_eleve}</title>
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
                <p>Atelier 7 : Dosage par précipitation, méthode de Mohr et produits de solubilité</p>
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
        if "ordre_quiz_tab7_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at7_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos7 += """
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
        if "champs_dos7_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos7_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos7_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 7
        html_export_dos7 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos7 = preparer_nom_fichier("Rapport_Precipitation").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 7 (.html)",
            data=html_export_dos7,
            file_name=nom_fichier_html_dos7,
            mime="text/html",
            use_container_width=True
        )



with tab8:
    st.header("Dosage complexométrique")
    
    # --- SECTION COURS : LES PRINCIPES DE LA COMPLEXOMÉTRIE ---
    st.subheader("Principe fondamental des titrages complexométriques")
    st.write(
        "Le dosage complexométrique est une méthode d'analyse quantitative basée sur la formation d'un "
        "**complexe soluble stable** entre un ion métallique central (le soluté à doser) et une molécule appelée "
        "ligand ou agent chélatant (le réactif titrant).\n\n"
        "Le terme **chélation** vient du mot grec 'chêlé' qui signifie pince. Les agents chélatants possèdent la particularité "
        "d'établir plusieurs liaisons de coordination simultanées autour de l'ion métallique, l'enfermant dans une véritable "
        "structure moléculaire protectrice. Le ligand le plus utilisé dans les laboratoires est l'**EDTA** (Acide ÉthylèneDiamineTétraAcétique), "
        "une molécule capable de s'agripper fermement à la quasi-totalité des métaux selon une proportion stricte de 1 pour 1."
    )
    
    st.divider()
    
    # --- EXEMPLE CONCRET ET SCANNABLE ---
    st.subheader("Exemple concret de laboratoire : Mesure de la dureté de l'eau (Titre Hydrotimétrique)")
    st.write(
        "Pour contrôler la qualité de l'eau potable ou valider le réglage d'un adoucisseur ménager, on réalise le dosage "
        "des ions **calcium ($Ca^{2+}$)** et **magnésium ($Mg^{2+}$)** responsables du tartre par une solution titrante d'EDTA.\n\n"
        "La réaction globale de complexation s'écrit de la façon suivante :\n"
        "**$Y^{4-} \\text{ (EDTA)} + Mg^{2+} \\rightarrow [MgY]^{2-} \\text{ (Complexe incolore)}$**\n\n"
        "Comme les ions métalliques et l'EDTA sont transparents, on ajoute une petite quantité d'un indicateur métallochromique, "
        "le **Noir Ériochrome T (NET)**, et on introduit une solution tampon pour fixer le pH à 10 :\n"
        "* **Avant l'équivalence :** Le NET s'associe immédiatement avec une partie des ions magnésium libres. Le complexe [Mg-NET] donne "
        "une **coloration rose violacé** à la solution. L'EDTA versé détruit au fur et à mesure les ions métalliques libres restants.\n"
        "* **À l'équivalence exacte :** L'EDTA a consommé tout le métal libre et vient arracher les derniers ions magnésium fixés sur l'indicateur.\n"
        "* **Après l'équivalence :** Libéré de tout lien métallique, le NET retrouve sa structure moléculaire solitaire. La solution vire "
        "à une **coloration bleu azur nette et persistante**, indiquant la fin immédiate du titrage."
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_cx1, col_cx2 = st.columns(2)
    with col_cx1:
        st.write("**Le mécanisme de la pince expliqué par la caricature**")
        st.write(
            "Pour faire comprendre ce phénomène à vos étudiants, on peut dessiner la caricature d'un crabe microscopique "
            "qui nage dans le bécher. Les ions magnésium $Mg^{2+}$ sont des perles brillantes éparpillées dans l'eau. "
            "L'indicateur NET agit comme un petit filet rose collant qui retient quelques perles. "
            "Le réactif titrant EDTA représente une armée de grands crabes affamés qui entrent dans le bassin. Chaque crabe déploie ses "
            "six pinces pour attraper une perle et se refermer hermétiquement dessus. À l'équivalence, le crabe arrache la dernière perle "
            "retenue par le filet rose. Privé de sa perle, le filet se détend et vire instantanément au bleu azur, donnant le signal d'arrêt."
        )
        try:
            st.image("caricature_dosage_complexometrique.jpg", caption="Caricature de la chélation : Le piégeage de l'ion central")
        except Exception:
            st.warning("L'image 'caricature_dosage_complexometrique.jpg' est introuvable.")

    with col_cx2:
        st.write("**La transition visuelle expérimentale**")
        st.write(
            "En pratique, le virage d'un dosage complexométrique au NET est l'un des plus nets observables en chimie des solutions. "
            "La solution passe d'un rouge vineux ou rose violacé sombre à une teinte pourpre à l'approche de l'équivalence.\n\n"
            "Le volume équivalent précis (Veq) est atteint à la goutte près dès que la dernière nuance violacée disparaît pour laisser "
            "place à un **bleu céleste limpide et stable**, matérialisant la libération totale du colorant indicateur."
        )
        try:
            st.image("manipulation_complexometrie.jpg", caption="Teintes du titrage à l'EDTA : Milieu initial rose, zone de transition pourpre et équivalence bleue")
        except Exception:
            st.warning("L'image 'manipulation_complexometrie.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 8 ---
    if "suite_verrouille_tab8_complexometrie" not in st.session_state:
        st.session_state.suite_verrouille_tab8_complexometrie = False
    verrou_at8 = st.session_state.suite_verrouille_tab8_complexometrie

    # Affichage du module de questions spécifique aux dosages complexométriques
    afficher_atelier_complexometrie(verrouille=verrou_at8)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 8")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat8 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les dosages complexométriques.",
        key="check_certif_dos8_final_net",
        disabled=verrou_at8,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8", key="btn_export_suite8_dos_official", use_container_width=True, disabled=verrou_at8):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat8: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q8 = 0.0
            if "ordre_quiz_tab8_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab8_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at8_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q8 += 1.0

            score_t8 = 0.0
            if "champs_dos8_clean" in st.session_state:
                for ligne in st.session_state.champs_dos8_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_dos8_clean", "Choisir...") == attendu: score_t8 += 1.0

            st.session_state.score_suite8_dos_p1 = round(float(score_q8), 1)
            st.session_state.score_suite8_dos_p2 = round(float(score_t8), 1)
            st.session_state.score_final_suite8_dos = round(float(score_q8 + score_t8), 1)
            st.session_state.suite_verrouille_tab8_complexometrie = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 8 ---
    if st.session_state.get("suite_verrouille_tab8_complexometrie", False):
        scr1_t8 = st.session_state.get("score_suite8_dos_p1", 0.0)
        scr2_t8 = st.session_state.get("score_suite8_dos_p2", 0.0)
        tot_s_t8 = st.session_state.get("score_final_suite8_dos", 0.0)
        timestamp_suite8 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER COMPLEXOMÉTRIE SCELLÉ | Note de session : {tot_s_t8:.1f} / 20")

        html_export_dos8 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Complexométrie - {n_eleve}</title>
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
                <p>Atelier 8 : Dosage complexométrique, agents chélatants EDTA et dureté de l'eau</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t8:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0369a1;">
                Note obtenue au Quiz Technique : <strong>{scr1_t8:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t8:.1f} / 10</strong><br>
                Note Totale de l'Atelier 8 : <strong>{tot_s_t8:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab8_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab8_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at8_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos8 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos8 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 8
        if "champs_dos8_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos8_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos8_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos8 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 8
        html_export_dos8 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos8 = preparer_nom_fichier("Rapport_Complexometrie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 8 (.html)",
            data=html_export_dos8,
            file_name=nom_fichier_html_dos8,
            mime="text/html",
            use_container_width=True
        )

with tab9:
    st.header("Dosage en retour")
    
    # --- SECTION COURS : LES PRINCIPES DU TITRAGE INDIRECT ---
    st.subheader("Principe fondamental du titrage en retour")
    st.write(
        "Le dosage en retour (ou titrage indirect) est une stratégie d'analyse de recours. "
        "Contrairement aux dosages directs où le réactif de la burette réagit immédiatement avec l'espèce inconnue, "
        "le dosage en retour se déroule obligatoirement en **deux étapes distinctes** :\n\n"
        "1. **L'introduction de l'excès :** On ajoute dans le bécher contenant l'espèce inconnue une quantité de matière "
        "parfaitement connue et en **excès** d'un réactif intermédiaire. On laisse la réaction se faire jusqu'à disparition totale de l'inconnu.\n"
        "2. **Le titrage de l'excès :** On réalise ensuite un dosage direct pour déterminer la quantité de réactif intermédiaire "
        "qui est **restée en excès** (qui n'a pas réagi). Par une simple soustraction, on en déduit ce qui a été consommé, et donc la quantité initiale d'inconnu."
    )
    
    st.divider()
    
    # --- EXEMPLE CONCRET ET SCANNABLE ---
    st.subheader("Exemple concret de laboratoire : Le dosage des ions chlorure par la méthode de Volhard")
    st.write(
        "La méthode de Volhard est l'illustration parfaite du dosage en retour. Elle permet de doser les **ions chlorure ($Cl^-$)** "
        "en milieu acide, là où la méthode directe de Mohr est inutilisable :\n\n"
        "* **Étape 1 (Réaction par excès) :** On ajoute un volume connu et en excès d'**ions argent ($Ag^+$)** dans le bécher. "
        "Tous les ions chlorure sont consommés pour former un précipité blanc de chlorure d'argent ($AgCl$). Il reste un excès d'ions $Ag^+$ libres dans le liquide.\n"
        "**$Ag^+_{\\text{(excès)}} + Cl^- \\rightarrow AgCl_{\\text{(solide)}}$**\n\n"
        "* **Étape 2 (Titrage en retour de l'excès) :** On installe dans la burette une solution d'**ions thiocyanate ($SCN^-$)**. "
        "Les ions $SCN^-$ versés réagissent avec les ions $Ag^+$ en excès restants pour former un second solide blanc :\n"
        "**$Ag^+_{\\text{(restant)}} + SCN^- \\rightarrow AgSCN_{\\text{(solide)}}$**\n\n"
        "* **Le repérage de l'équivalence :** On introduit de l'**alun de fer III** (ions $Fe^{3+}$) comme indicateur coloré. "
        "Dès que le tout dernier ion argent en excès a été précipité, le premier ion thiocyanate versé de trop réagit avec le fer III "
        "pour former un complexe soluble rouge intense. La solution prend instantanément une **coloration rouge-sang persistante** :\n"
        "**$Fe^{3+} + SCN^- \\rightarrow [Fe(SCN)]^{2+}_{\\text{(soluble rouge)}}$**"
    )
    
    # Configuration des deux colonnes avec vos fichiers images .jpg locaux
    col_ret1, col_ox2 = st.columns(2)
    with col_ret1:
        st.write("**Le calcul à l'envers expliqué par la caricature**")
        st.write(
            "Pour faire comprendre ce raisonnement indirect aux élèves, on peut imaginer la caricature d'un boulanger "
            "qui veut compter combien de brioches un client mystère a mangées en douce dans sa réserve close.\n\n"
            "Le boulanger sait qu'il y avait exactement 50 brioches au départ (l'excès connu introduit). "
            "Le client entre, mange et s'en va. Pour savoir combien de brioches manquent, le boulanger n'a pas besoin de regarder "
            "dans l'estomac du client : il lui suffit de compter méthodiquement les brioches restantes sur l'étagère (le titrage en retour de l'excès). "
            "S'il en reste 38, une simple soustraction ($50 - 38 = 12$) lui donne instantanément la quantité consommée par l'inconnu."
        )
        try:
            st.image("caricature_dosage_en_retour.jpg", caption="Caricature de l'analyse indirecte : La déduction par différence des stocks")
        except Exception:
            st.warning("L'image 'caricature_dosage_en_retour.jpg' est introuvable.")

    with col_ox2:
        st.write("**Le virage final de la méthode de Volhard**")
        st.write(
            "Expérimentalement, l'analyse de Volhard est spectaculaire. Tout au long de la seconde étape, le versement du thiocyanate "
            "génère un second trouble laiteux blanc dans le bécher.\n\n"
            "L'équivalence ne se traduit pas par un changement de couleur du solide, mais par l'apparition soudaine et persistante "
            "d'une **teinte orange-rouge ou sang** dans la solution limpide surnageante, provoquant le signal d'arrêt immédiat du manipulateur."
        )
        try:
            st.image("manipulation_en_retour.jpg", caption="Rendu expérimental du virage de Volhard : Suspension blanche et équivalence rouge-sang")
        except Exception:
            st.warning("L'image 'manipulation_en_retour.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 9 ---
    if "suite_verrouille_tab9_en_retour" not in st.session_state:
        st.session_state.suite_verrouille_tab9_en_retour = False
    verrou_at9 = st.session_state.suite_verrouille_tab9_en_retour

    # Affichage du module de questions spécifique aux dosages en retour
    afficher_atelier_en_retour(verrouille=verrou_at9)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 9")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat9 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les dosages en retour.",
        key="check_certif_dos9_final_net",
        disabled=verrou_at9,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9", key="btn_export_suite9_dos_official", use_container_width=True, disabled=verrou_at9):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat9: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q9 = 0.0
            if "ordre_quiz_tab9_dos_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab9_dos_aleatoire:
                    saisie = st.session_state.get(f"dos_at9_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q9 += 1.0

            score_t9 = 0.0
            if "champs_dos9_clean" in st.session_state:
                for ligne in st.session_state.champs_dos9_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_dos9_clean", "Choisir...") == attendu: score_t9 += 1.0

            st.session_state.score_suite9_dos_p1 = round(float(score_q9), 1)
            st.session_state.score_suite9_dos_p2 = round(float(score_t9), 1)
            st.session_state.score_final_suite9_dos = round(float(score_q9 + score_t9), 1)
            st.session_state.suite_verrouille_tab9_en_retour = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 9 ---
    if st.session_state.get("suite_verrouille_tab9_en_retour", False):
        scr1_t9 = st.session_state.get("score_suite9_dos_p1", 0.0)
        scr2_t9 = st.session_state.get("score_suite9_dos_p2", 0.0)
        tot_s_t9 = st.session_state.get("score_final_suite9_dos", 0.0)
        timestamp_suite9 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER DOSAGE EN RETOUR SCELLÉ | Note de session : {tot_s_t9:.1f} / 20")

        html_export_dos9 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dosage en Retour - {n_eleve}</title>
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
                <p>Atelier 9 : Stratégies de titrages indirects en retour et méthode de Volhard</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite9}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t9:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #475569;">
                Note obtenue au Quiz Technique : <strong>{scr1_t9:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t9:.1f} / 10</strong><br>
                Note Totale de l'Atelier 9 : <strong>{tot_s_t9:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab9_dos_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab9_dos_aleatoire, 1):
                saisie = st.session_state.get(f"dos_at9_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dos9 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_dos9 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 9
        if "champs_dos9_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_dos9_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_dos9_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_dos9 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 9
        html_export_dos9 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_dos9 = preparer_nom_fichier("Rapport_En_Retour").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 9 (.html)",
            data=html_export_dos9,
            file_name=nom_fichier_html_dos9,
            mime="text/html",
            use_container_width=True
        )
















