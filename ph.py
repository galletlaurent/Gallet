
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application le pH",
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
st.title("Application le pH")
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
    "Définition du pH",
    "La mesure du pH",
    "Les produits acides",
    "Les produits basiques",
    "Les dosages pH-métrique",
    "Calcul du pH"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]

def afficher_atelier_dosages_ph(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Les dosages pH-métriques) sur deux colonnes."""
    import random

    questions_ph5_sources = [
        {"id": "qd1", "q": "Quelle opération expérimentale consiste à déterminer la concentration inconnue d'une solution ?", "options": ["Un dosage (ou titrage)", "Une décantation", "Une distillation simple"], "rep": "Un dosage (ou titrage)"},
        {"id": "qd2", "q": "Quel célèbre savant français a développé l'usage de la burette graduée au dix-huitième siècle ?", "options": ["Louis-Joseph Gay-Lussac", "Antoine Lavoisier", "Søren Sorensen"], "rep": "Louis-Joseph Gay-Lussac"},
        {"id": "qd3", "q": "Quels ions s'associent lors de la neutralisation pour former des molécules d'eau pure ?", "options": ["Les ions oxonium H3O+ et hydroxyde OH-", "Les ions sodium Na+ et chlorure Cl-", "Les molécules de dioxyde de carbone"], "rep": "Les ions oxonium H3O+ et hydroxyde OH-"},
        {"id": "qd4", "q": "Comment appelle-t-on le changement brutal de la valeur lue sur le graphique au moment de l'équivalence ?", "options": ["Le saut de pH", "Le calibre d'étalonnage", "L'index d'intermittence"], "rep": "Le saut de pH"},
        {"id": "qd5", "q": "Quel est le pH théorique obtenu à l'équivalence lors du titrage d'un acide fort par une base forte ?", "options": ["pH = 7", "pH = 0", "pH = 14"], "rep": "pH = 7"},
        {"id": "qd6", "q": "Où place-t-on obligatoirement la solution titrante de concentration connue pour la verser goutte à goutte ?", "options": ["Dans la burette graduée", "Dans le bécher inférieur", "Dans l'éprouvette fixe"], "rep": "Dans la burette graduée"},
        {"id": "qd7", "q": "Quel appareil agite en continu le contenu du bécher pour homogénéiser le mélange ?", "options": ["L'agitateur magnétique", "La sonde de verre", "Le convertisseur de tension"], "rep": "L'agitateur magnétique"},
        {"id": "qd8", "q": "Comment évolue le pH du bécher au tout début du dosage si celui-ci contient un acide initial ?", "options": ["Il augmente très lentement avant l'équivalence", "Il chute immédiatement à zéro", "Il reste fixe à 14.0"], "rep": "Il augmente très lentement avant l'équivalence"},
        {"id": "qd9", "q": "Quelle est la forme de la courbe représentant un dosage pH-métrique complet ?", "options": ["Une courbe en forme de S", "Une droite linéaire parfaite", "Une parabole inversée"], "rep": "Une courbe en forme de S"},
        {"id": "qd10", "q": "Une fois l'équivalence largement dépassée, vers quel type de pH la valeur tend-elle ?", "options": ["Un pH très basique (proche de celui de la base titrante)", "Un pH acide proche de zéro", "Un pH neutre égal à 7"], "rep": "Un pH très basique (proche de celui de la base titrante)"}
    ]

    if "ordre_quiz_tab5_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph5_sources)
        st.session_state.ordre_quiz_tab5_ph_aleatoire = questions_ph5_sources

    # Liste de synthèse de texte à trous avec indexations rigoureuses
    if "champs_ph5_clean" not in st.session_state:
        st.session_state.champs_ph5_clean = [
            ("1. Déterminer une concentration inconnue met en œuvre un ..........", ["Choisir...", "dosage", "étalonnage"], "dosage", "ph5_t1"),
            ("2. La burette graduée a été popularisée par le chimiste ..........", ["Choisir...", "Gay-Lussac", "Beckman"], "Gay-Lussac", "ph5_t2"),
            ("3. Faire réagir un acide fort et une base forte produit de l'..........", ["Choisir...", "eau", "hydrogène"], "eau", "ph5_t3"),
            ("4. L'instant où tout l'acide initial est consommé s'appelle l'..........", ["Choisir...", "équivalence", "dilution"], "équivalence", "ph5_t4"),
            ("5. La courbe de titrage prend l'allure d'une ligne en ..........", ["Choisir...", "S", "U"], "S", "ph5_t5"),
            ("6. Le moment charnière de la neutralisation se repère par un .......... de pH.", ["Choisir...", "saut", "palier"], "saut", "ph5_t6"),
            ("7. La solution titrante connue s'installe dans la .......... graduée.", ["Choisir...", "burette", "pipette"], "burette", "ph5_t7"),
            ("8. Le bécher de mesure repose sur un agitateur .......... circulaire.", ["Choisir...", "magnétique", "thermique"], "magnétique", "ph5_t8"),
            ("9. À l'équivalence exacte, le pH du mélange neutre vaut ..........", ["Choisir...", "7", "14"], "7", "ph5_t9"),
            ("10. Continuer le versement après l'équivalence rend le milieu ..........", ["Choisir...", "basique", "acide"], "basique", "ph5_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph5_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph5_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_produits_basiques(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Les produits basiques) sur deux colonnes."""
    import random

    questions_ph4_sources = [
        {"id": "qb1", "q": "Comment qualifie-t-on la concentration en ions hydroxyde dans une solution basique par rapport aux ions oxonium ?", "options": ["Elle est supérieure", "Elle est égale", "Elle est inférieure"], "rep": "Elle est supérieure"},
        {"id": "qb2", "q": "De quel mot de la langue arabe dérive le terme 'alcalin' qui désigne un produit basique ?", "options": ["Al-qaly (les cendres)", "Al-kimia", "Al-jabr"], "rep": "Al-qaly (les cendres)"},
        {"id": "qb3", "q": "Quel produit industriel à base de soude caustique sert à détruire les bouchons des canalisations ?", "options": ["Le déboucheur liquide", "L'esprit de sel", "Le vinaigre blanc"], "rep": "Le déboucheur liquide"},
        {"id": "qb4", "q": "Quelle base faible inoffensive sert de poudre à lever en cuisine et à blanchir les dents ?", "options": ["Le bicarbonate de sodium", "La soude caustique", "L'ammoniaque"], "rep": "Le bicarbonate de sodium"},
        {"id": "qb5", "q": "Quel gaz dissous à l'odeur très piquante est utilisé pour nettoyer les vitres ?", "options": ["L'ammoniaque (NH3)", "Le dioxyde de carbone", "Le chlore"], "rep": "L'ammoniaque (NH3)"},
        {"id": "qb6", "q": "Quel produit ménager désinfectant très répandu possède un caractère basique marqué ?", "options": ["L'eau de Javel", "Le jus de pomme", "L'acide acétique"], "rep": "L'eau de Javel"},
        {"id": "qb7", "q": "Pourquoi les projections cutanées de bases fortes sont-elles particulièrement redoutables ?", "options": ["Elles détruisent les graisses de la peau sans douleur immédiate", "Elles gèlent les cellules", "Elles font bouillir l'eau de la peau"], "rep": "Elles détruisent les graisses de la peau sans douleur immédiate"},
        {"id": "qb8", "q": "Quelle base est utilisée en agriculture sous le nom de 'chaux' pour traiter les sols trop acides ?", "options": ["L'hydroxyde de calcium", "La soude caustique", "Le carbonate de potassium"], "rep": "L'hydroxyde de calcium"},
        {"id": "qb9", "q": "Quelle est la texture caractéristique en bouche ou au toucher d'une solution alcaline faible ?", "options": ["Une texture glissante ou savonneuse", "Un goût piquant", "Une texture croustillante"], "rep": "Une texture glissante ou savonneuse"},
        {"id": "qb10", "q": "Comment varie le pH d'une solution de soude caustique si on lui ajoute un très grand volume d'eau ?", "options": ["Il baisse pour se rapprocher de 7", "Il monte vers 14", "Il stagne rigoureusement à 14"], "rep": "Il baisse pour se rapprocher de 7"}
    ]

    if "ordre_quiz_tab4_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph4_sources)
        st.session_state.ordre_quiz_tab4_ph_aleatoire = questions_ph4_sources

    # Liste de synthèse structurée pour le texte à trous
    if "champs_ph4_clean" not in st.session_state:
        st.session_state.champs_ph4_clean = [
            ("1. Une solution est alcaline ou basique si sa valeur de pH est supérieure à ..........", ["Choisir...", "7", "0"], "7", "ph4_t1"),
            ("2. Les solutions basiques se caractérisent par une dominance d'ions ..........", ["Choisir...", "hydroxyde", "oxonium"], "hydroxyde", "ph4_t2"),
            ("3. Le mot alcalin provient historiquement des cendres de .......... calcinées.", ["Choisir...", "bois", "charbon"], "bois", "ph4_t3"),
            ("4. Le déboucheur de canalisations contient de la .......... caustique.", ["Choisir...", "soude", "chaux"], "soude", "ph4_t4"),
            ("5. Les bases fortes industrielles attaquent les tissus vivants et sont ..........", ["Choisir...", "corrosives", "acides"], "corrosives", "ph4_t5"),
            ("6. Le bicarbonate de sodium est une base .......... utilisée en alimentation.", ["Choisir...", "faible", "forte"], "faible", "ph4_t6"),
            ("7. La formule chimique NH₃ désigne le gaz nettoyant appelé ..........", ["Choisir...", "ammoniaque", "soude"], "ammoniaque", "ph4_t7"),
            ("8. L'hydroxyde de calcium compose la .......... utilisée en bâtiment.", ["Choisir...", "chaux", "potasse"], "chaux", "ph4_t8"),
            ("9. Une projection accidentelle de base impose un .......... immédiat à l'eau.", ["Choisir...", "rinçage", "essuyage"], "rinçage", "ph4_t9"),
            ("10. Diluer un produit très basique fait .......... sa valeur de pH vers 7.", ["Choisir...", "baisser", "monter"], "baisser", "ph4_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at4_final_g_{q_data['id']}"
            opts_affichés = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichés, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph4_clean:
            # AJOUTEZ PRÉCISEMENT LES INDEX [0] ET [1] ICI :
            enonce = ligne[0]  # Extrait uniquement la phrase de texte propre
            choix = ligne[1]   # Extrait uniquement la liste des options ["Choisir...", ...]
            cle = ligne[-1]    # Extrait la clé unique de session
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph4_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_produits_acides(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Les produits acides) sur deux colonnes."""
    import random

    # 1. Base de données des questions du Quiz
    questions_ph3_sources = [
        {"id": "qa1", "q": "Comment qualifie-t-on la concentration en ions oxonium dans une solution acide par rapport aux ions hydroxyde ?", "options": ["Elle est supérieure", "Elle est égale", "Elle est strictement nulle"], "rep": "Elle est supérieure"},
        {"id": "qa2", "q": "Quel goût caractéristique en bouche possèdent les acides alimentaires faibles ?", "options": ["Un goût aigre ou piquant", "Un goût sucré", "Un goût amer et savonneux"], "rep": "Un goût aigre ou piquant"},
        {"id": "qa3", "q": "Quel acide fort industriel compose majoritairement le produit détartrant 'esprit de sel' ?", "options": ["L'acide chlorhydrique", "L'acide citrique", "L'acide acétique"], "rep": "L'acide chlorhydrique"},
        {"id": "qa4", "q": "Quel acide fort très dangereux remplit le compartiment liquide des batteries de voiture ?", "options": ["L'acide sulfurique", "L'acide phosphorique", "L'acide lactique"], "rep": "L'acide sulfurique"},
        {"id": "qa5", "q": "Quel additif acide est incorporé dans les boissons gazeuses au cola ?", "options": ["L'acide phosphorique", "L'acide malique", "L'acide chlorhydrique"], "rep": "L'acide phosphorique"},
        {"id": "qa6", "q": "Quel unique réflexe de sécurité s'impose immédiatement en cas de projection d'un acide fort sur la peau ?", "options": ["Rincer abondamment à l'eau courante", "Essuyer avec un chiffon sec", "Verser une base forte pour annuler"], "rep": "Rincer abondamment à l'eau courante"},
        {"id": "qa7", "q": "Quel est le nom de l'acide organique présent dans le vinaigre commercial ?", "options": ["L'acide acétique", "L'acide citrique", "L'acide ascorbique"], "rep": "L'acide acétique"},
        {"id": "qa8", "q": "Quel composant moléculaire est désigné par une sphère verte dans le détartrant HCl ?", "options": ["L'atome de chlore", "L'atome de soufre", "L'atome d'hydrogène"], "rep": "L'atome de chlore"},
        {"id": "qa9", "q": "Quel type de danger est matérialisé par le pictogramme international représentant une main rongée ?", "options": ["Produit corrosif", "Produit explosif", "Produit inflammable"], "rep": "Produit corrosif"},
        {"id": "qa10", "q": "Quel acide naturel se forme spontanément lorsque le lait tourne ?", "options": ["L'acide lactique", "L'acide malique", "L'acide acétylsalicylique"], "rep": "L'acide lactique"}
    ]

    if "ordre_quiz_tab3_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph3_sources)
        st.session_state.ordre_quiz_tab3_ph_aleatoire = questions_ph3_sources

    # 2. INITIALISATION ET DÉCLARATION FORCÉE DE LA LISTE DE SYNTHÈSE CONTRE LES KEYERROR
    if "champs_ph3_clean" not in st.session_state:
        st.session_state.champs_ph3_clean = [
            ("1. Un produit est acide si son potentiel hydrogène est inférieur à ..........", ["Choisir...", "7", "14"], "7", "ph3_t1"),
            ("2. Les solutions acides se caractérisent par une dominance d'ions ..........", ["Choisir...", "oxonium", "hydroxyde"], "oxonium", "ph3_t2"),
            ("3. L'acide .......... ou vinaigre est un acide faible de la cuisine.", ["Choisir...", "acétique", "sulfurique"], "acétique", "ph3_t3"),
            ("4. L'esprit de sel contient l'acide .......... décapant fort.", ["Choisir...", "chlorhydrique", "phosphorique"], "chlorhydrique", "ph3_t4"),
            ("5. Les acides industriels concentrés attaquent les métaux et sont ..........", ["Choisir...", "corrosifs", "neutres"], "corrosifs", "ph3_t5"),
            ("6. Le pictogramme montre un tube versant du liquide sur une ..........", ["Choisir...", "main", "flamme"], "main", "ph3_t6"),
            ("7. L'atome de chlore est modélisé par une sphère de couleur ..........", ["Choisir...", "verte", "jaune"], "verte", "ph3_t7"),
            ("8. L'acide sulfurique chargé dans les batteries possède l'atome de ..........", ["Choisir...", "soufre", "chlore"], "soufre", "ph3_t8"),
            ("9. Une projection accidentelle impose un .......... immédiat à l'eau.", ["Choisir...", "rinçage", "essuyage"], "rinçage", "ph3_t9"),
            ("10. Diluer un produit très acide fait .......... sa valeur de pH vers 7.", ["Choisir...", "monter", "baisser"], "monter", "ph3_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at3_final_g_{q_data['id']}"
            opts_affichés = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichés, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph3_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph3_clean", disabled=verrouille, label_visibility="collapsed")

                
def afficher_atelier_mesure_ph(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (La mesure du pH) sur deux colonnes."""
    import random

    # 1. Base de données des questions du Quiz
    questions_ph2_sources = [
        {"id": "qm1", "q": "Quel papier indicateur a été inventé au quatorzième siècle à partir de lichens ?", "options": ["Le papier de tournesol", "Le papier pH moderne", "Le papier filtre standard"], "rep": "Le papier de tournesol"},
        {"id": "qm2", "q": "Quel inventeur américain a développé le tout premier pH-mètre électronique en 1934 ?", "options": ["Arnold Beckman", "Søren Sorensen", "Thomas Edison"], "rep": "Arnold Beckman"},
        {"id": "qm3", "q": "Pour quelle industrie fruitière de Californie le premier pH-mètre a-t-il été créé ?", "options": ["L'industrie du jus de citron", "La fermentation du vin", "La culture des pommes"], "rep": "L'industrie du jus de citron"},
        {"id": "qm4", "q": "Avec quoi doit-on rincer la sonde en verre d'un pH-mètre entre deux mesures ?", "options": ["De l'eau distillée", "De l'eau du robinet", "De l'acide"], "rep": "De l'eau distillée"},
        {"id": "qm5", "q": "Quelle épice jaune vire de façon spectaculaire au rouge-brun en milieu basique ?", "options": ["Le curcuma", "Le poivre noir", "Le gingembre"], "rep": "Le curcuma"},
        {"id": "qm6", "q": "Quelle couleur prend l'extrait de chou rouge lorsqu'il rencontre un milieu neutre (pH=7) ?", "options": ["Violet", "Rouge vif", "Jaune"], "rep": "Violet"},
        {"id": "qm7", "q": "Quelle boisson courante s'éclaircit en jaune pâle sous l'action d'un jus d'acide ?", "options": ["Le thé noir", "Le café", "Le lait de vache"], "rep": "Le thé noir"},
        {"id": "qm8", "q": "Que risque-t-on de faire si l'on frotte la membrane sensible de la sonde ?", "options": ["La rayer ou créer des charges parasites faussant la mesure", "La rendre basique", "La dissoudre"], "rep": "La rayer ou créer des charges parasites faussant la mesure"},
        {"id": "qm9", "q": "Le jus de mon fruit vire au vert sombre en milieu basique. De quel fruit s'agit-il ?", "options": ["La myrtille", "Le citron", "La banane"], "rep": "La myrtille"},
        {"id": "qm10", "q": "Comment appelle-t-on le nuancier de couleur de référence du papier pH ?", "options": ["L'échelle des teintes", "Le tableau périodique", "L'étalonnage"], "rep": "L'échelle des teintes"}
    ]

    if "ordre_quiz_tab2_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph2_sources)
        st.session_state.ordre_quiz_tab2_ph_aleatoire = questions_ph2_sources

    # 2. INITIALISATION ET DÉCLARATION FORCÉE DE LA LISTE DE SYNTHÈSE CONTRE LES KEYERROR
    if "champs_ph2_clean" not in st.session_state:
        st.session_state.champs_ph2_clean = [
            ("1. Le papier de .......... vire au rouge avec l'acide depuis le Moyen Âge.", ["Choisir...", "tournesol", "chou"], "tournesol", "ph2_t1"),
            ("2. L'acidimètre électronique de haute précision a été inventé par ..........", ["Choisir...", "Beckman", "Sorensen"], "Beckman", "ph2_t2"),
            ("3. Ce premier pH-mètre a été créé pour analyser le jus de ..........", ["Choisir...", "citron", "pomme"], "citron", "ph2_t3"),
            ("4. L'élément sensible plongé dans le flacon est l'..........", ["Choisir...", "électrode", "agitateur"], "électrode", "ph2_t4"),
            ("5. Nettoyer la sonde demande un rinçage systématique à l'eau ..........", ["Choisir...", "distillée", "salée"], "distillée", "ph2_t5"),
            ("6. Le jus de chou rouge vire au violet stable en milieu ..........", ["Choisir...", "neutre", "acide"], "neutre", "ph2_t6"),
            ("7. Le curcuma déploie une teinte rouge-brun brique en milieu ..........", ["Choisir...", "basique", "acide"], "basique", "ph2_t7"),
            ("8. Frotter la membrane de verre est interdit pour éviter la ..........", ["Choisir...", "rayure", "fusion"], "rayure", "ph2_t8"),
            ("9. L'infusion de thé noir s'éclaircit nettement en présence d'un ..........", ["Choisir...", "acide", "alcalin"], "acide", "ph2_t9"),
            ("10. Garder l'extrémité de la sonde active exige un stockage ..........", ["Choisir...", "humide", "sec"], "humide", "ph2_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique, Historique et Végétal (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph2_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph2_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_definition_ph(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Définition du pH) sur deux colonnes."""
    import random

    # 1. Base de données des questions du Quiz (Sans émoji)
    questions_ph1_sources = [
        {"id": "qph1", "q": "Quel chimiste danois a inventé la notion de pH en 1909 ?", "options": ["Søren Sorensen", "Antoine Lavoisier", "Svante Arrhenius"], "rep": "Søren Sorensen"},
        {"id": "qph2", "q": "Que signifie littéralement l'abréviation de pH introduite par Sorensen ?", "options": ["Potentiel Hydrogène", "Pression Hydrogène", "Pourcentage Hydrogène"], "rep": "Potentiel Hydrogène"},
        {"id": "qph3", "q": "Dans quel laboratoire industriel l'échelle de pH a-t-elle été développée pour la fermentation ?", "options": ["La brasserie Carlsberg", "Les usines Pasteur", "Les laboratoires Solvay"], "rep": "La brasserie Carlsberg"},
        {"id": "qph4", "q": "Comment qualifie-t-on une solution dont la valeur de pH est égale à 3,5 ?", "options": ["Acide", "Basique", "Neutre"], "rep": "Acide"},
        {"id": "qph5", "q": "Quelle formule chimique représente l'ion oxonium responsable de l'acidité ?", "options": ["H3O+", "OH-", "Cl-"], "rep": "H3O+"},
        {"id": "qph6", "q": "Quelle formule chimique représente l'ion hydroxyde responsable de la basicité ?", "options": ["OH-", "H3O+", "Na+"], "rep": "OH-"},
        {"id": "qph7", "q": "Si l'on ajoute un grand volume d'eau pure dans un acide, vers quelle valeur le pH se dirige-t-on ?", "options": ["7", "0", "14"], "rep": "7"},
        {"id": "qph8", "q": "Dans le modèle moléculaire de l'ion oxonium, que représente la boule rouge centrale ?", "options": ["L'atome d'oxygène", "L'atome d'hydrogène", "La charge positive"], "rep": "L'atome d'oxygène"},
        {"id": "qph9", "q": "Combien d'atomes d'hydrogène (boules blanches) comporte l'ion oxonium H3O+ ?", "options": ["3 atomes", "2 atomes", "1 atome"], "rep": "3 atomes"},
        {"id": "qph10", "q": "Quel opérateur mathématique est utilisé devant la concentration pour calculer le pH ?", "options": ["Le logarithme négatif (-log)", "La racine carrée", "La multiplication par 14"], "rep": "Le logarithme négatif (-log)"}
    ]

    if "ordre_quiz_tab1_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph1_sources)
        st.session_state.ordre_quiz_tab1_ph_aleatoire = questions_ph1_sources

    # 2. INITIALISATION ET DÉCLARATION FORCÉE DE LA LISTE DE SYNTHÈSE CONTRE LES KEYERROR
    if "champs_ph1_clean" not in st.session_state:
        st.session_state.champs_ph1_clean = [
            ("1. Le concept historique de pH a été introduit par le chercheur ..........", ["Choisir...", "Sorensen", "Lavoisier"], "Sorensen", "ph1_t1"),
            ("2. Les initiales pH signifient le Potentiel .......... de la solution.", ["Choisir...", "Hydrogène", "Hydrate"], "Hydrogène", "ph1_t2"),
            ("3. Un milieu dont la valeur de pH est inférieure à 7 est ..........", ["Choisir...", "acide", "basique"], "acide", "ph1_t3"),
            ("4. Lorsque le pH est supérieur à 7, la solution aqueuse est ..........", ["Choisir...", "basique", "neutre"], "basique", "ph1_t4"),
            ("5. L'égalité exacte pH = 7 définit la zone de neutralité de l'..........", ["Choisir...", "eau", "acide"], "eau", "ph1_t5"),
            ("6. Diluer une solution acide fait .......... sa valeur de pH vers 7.", ["Choisir...", "augmenter", "diminuer"], "augmenter", "ph1_t6"),
            ("7. L'ion oxonium H3O+ caractérise chimiquement l'..........", ["Choisir...", "acidité", "basicité"], "acidité", "ph1_t7"),
            ("8. L'atome d'oxygène de l'ion oxonium est modélisé par une boule ..........", ["Choisir...", "rouge", "blanche"], "rouge", "ph1_t8"),
            ("9. Les trois hydrogènes sont représentés par des boules ..........", ["Choisir...", "blanches", "noires"], "blanches", "ph1_t9"),
            ("10. Le calcul du pH repose sur l'utilisation mathématique du ..........", ["Choisir...", "logarithme", "calibre"], "logarithme", "ph1_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Historique et Conceptuel (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph1_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph1_clean", disabled=verrouille, label_visibility="collapsed")
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
    st.header("Définition du pH")
    
    # --- FOCUS HISTORIQUE : SØREN SORENSEN ---
    st.subheader("Histoire des Sciences : L'invention du pH")
    st.write(
        "La notion de pH a été inventée en 1909 par le chimiste danois Søren Sorensen "
        "alors qu'il dirigeait les laboratoires de la célèbre brasserie Carlsberg à Copenhague.\n\n"
        "Cherchant un moyen précis de contrôler la fermentation de la bière et la qualité des protéines, "
        "il a eu l'idée de mesurer la concentration des ions hydrogène en solution. "
        "Il a introduit le terme de pH, qui signifie Potentiel Hydrogène.\n\n"
        "Quelques années plus tard, en 1924, la formule moderne et définitive du pH a été formalisée "
        "en fonction de la concentration en ions oxonium [H3O+] exprimée en moles par litre :\n\n"
        "**pH = -log [H3O+]**"
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET DÉFINITION ---
    st.subheader("L'Échelle de pH")
    st.write(
        "Le pH permet de connaître l’acidité d’une solution, il varie entre 0 et 14. "
        "Si le **0 <= pH < 7**, la solution est **acide**. Si le **pH = 7** la solution est **neutre**. "
        "Si **7 < pH <= 14** la solution est **basique**.\n\n"
        "Plus on dilue une solution plus le pH se rapproche de 7.\n\n"
        "Les ions responsables de l’acidité sont les **ions oxonium** (H+ ou H3O+).\n"
        "Les ions responsables de la basicité sont les **ions hydroxyde** (OH-)."
    )
    
    col_ph1, col_ph2 = st.columns(2)
    with col_ph1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre l'échelle de pH, on peut imaginer une caricature représentant une balance chimique. "
            "Dans le camp de l'acidité (pH de 0 à 6), les petits personnages Oxonium (H3O+) sont ultra-majoritaires "
            "et font pencher la balance. Dans le camp de la basicité (pH de 8 à 14), ce sont les personnages Hydroxyde (OH-) "
            "qui dominent le terrain. À la neutralité exacte (pH = 7), c'est une zone de paix parfaite où il y a "
            "autant d'Oxoniums que d'Hydroxydes, formant de l'eau pure."
        )
        try:
            st.image("caricature_ph.jpg", caption="Caricature de la balance entre acidité, neutralité et basicité")
        except Exception:
            st.warning("L'image 'caricature_ph.jpg' est introuvable.")

    with col_ph2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "Sur un schéma normalisé, l'échelle de pH s'organise le long d'une frise de couleurs allant du rouge vif "
            "pour les acides forts, au vert pour les milieux neutres, jusqu'au violet foncé pour les bases fortes.\n\n"
            "La dilution d'une solution acide augmente son pH pour le rapprocher de 7, tandis que la dilution "
            "d'une solution basique diminue son pH pour le rapprocher également de 7. Diluer revient à calmer "
            "l'agressivité chimique en tendant vers la neutralité de l'eau."
        )
        try:
            st.image("echelle_ph.jpg", caption="Échelle scientifique normalisée du pH de 0 à 14")
        except Exception:
            st.warning("L'image 'echelle_ph.jpg' est introuvable.")
            
    st.divider()
    
    # --- FOCUS STRUCTURE MOLÉCULAIRE : L'ION OXONIUM ---
    st.subheader("Structure microscopique : L'ion oxonium H3O+")
    st.write(
        "L'ion oxonium, responsable de l'acidité, est une molécule d'eau (H2O) qui a capturé un ion hydrogène (H+) "
        "supplémentaire. Voici sa modélisation moléculaire tridimensionnelle :"
    )
    
    col_mol1, col_mol2 = st.columns([0.4, 0.6])
    with col_mol1:
        st.markdown("**Données et Légendes Atomiques**")
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1: 
            st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: 
            st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.write(
            "**Formule chimique brute : H3O+**\n\n"
            "L'atome d'oxygène central établit trois liaisons de type covalente simple "
            "avec trois atomes d'hydrogène répartis de façon trigonale pyramidale. "
            "Le signe plus en haut à droite indique une perte globale d'un électron."
        )

    with col_mol2:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig_mol, ax_mol = plt.subplots(figsize=(5, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # Coordonnees geometriques de la pyramide trigonale projetee a plat (Centree sur l'Oxygene)
        c_oxygene = np.array([4.0, 2.5])
        h1_ox = np.array([2.6, 2.5])      # Branche gauche
        h2_ox = np.array([4.7, 3.7])      # Branche haut droite
        h3_ox = np.array([4.7, 1.3])      # Branche bas droite

        # Fonction de tracé des liaisons covalentes
        def tracer_liaison_ph(p1, p2):
            ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Tracé des 3 liaisons covalentes simples O-H
        tracer_liaison_ph(c_oxygene, h1_ox)
        tracer_liaison_ph(c_oxygene, h2_ox)
        tracer_liaison_ph(c_oxygene, h3_ox)

        # Fonction de tracé des atomes spheriques
        def tracer_atome_ph(p, symbole):
            if symbole == 'O': 
                couleur, texte_couleur = "#e74c3c", "white" # Rouge pour l'Oxygene
            elif symbole == 'H': 
                couleur, texte_couleur = "#ecf0f1", "black" # Blanc/Gris pour l'Hydrogene
            else: 
                couleur, texte_couleur = "#95a5a6", "black"
            
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.25, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=11, ha="center", va="center", zorder=3)

        # Rendu des atomes
        tracer_atome_ph(c_oxygene, 'O')
        tracer_atome_ph(h1_ox, 'H')
        tracer_atome_ph(h2_ox, 'H')
        tracer_atome_ph(h3_ox, 'H')

        # Ajout du signe de charge positive globale de l'ion en haut a droite
        ax_mol.text(5.5, 3.8, "+", color="#e74c3c", weight="bold", fontsize=20, ha="center", va="center")

        # Configuration des limites du plan de vue moleculaire
        ax_mol.set_xlim(2.0, 6.0)
        ax_mol.set_ylim(0.8, 4.2)
        ax_mol.axis("off")
        
        # Injection du rendu Matplotlib natif dans Streamlit
        st.pyplot(fig_mol)

    if "suite_verrouille_tab1_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab1_ph = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_ph

    afficher_atelier_definition_ph(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Définition du pH.",
        key="check_certif_ph1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_ph_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_ph_aleatoire:
                    reponse_eleve = st.session_state.get(f"ph_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = 0.0
            if "champs_ph1_clean" in st.session_state:
                for ligne in st.session_state.champs_ph1_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph1_clean", "Choisir...") == attendu:
                        score_t1 += 1.0

            st.session_state.score_suite1_ph_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_ph_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_ph = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 1 ---
    if st.session_state.get("suite_verrouille_tab1_ph", False):
        scr1_t1 = st.session_state.get("score_suite1_ph_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_ph_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_ph", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        # AJOUTEZ IMPÉRATIVEMENT CES TROIS LIGNES ICI POUR FIXER LE CRASH :
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        st.success(f"ATELIER DÉFINITION PH SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_ph1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Définition pH - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Sciences Physiques</h1>
                <p>Atelier 1 : Echelle de pH, acidite, basicite, structures moleculaires et histoire</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #be123c;">
                Note obtenue au Quiz de Cours : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz
        if "ordre_quiz_tab1_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Transition vers le second tableau pour le texte à trous de l'Atelier 1
        html_export_ph1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction de la synthèse de texte
        if "champs_ph1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                
                html_export_ph1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture du rapport HTML de l'Atelier 1
        html_export_ph1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph1 = preparer_nom_fichier("Rapport_Definition_pH").replace(".txt", ".html")
        st.download_button(
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 1 (.html)",
            data=html_export_ph1,
            file_name=nom_fichier_html_ph1,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("La mesure du pH")
    
    # --- FOCUS HISTORIQUE : DU TOURNESOL A BECKMAN ---
    st.subheader("Histoire des Sciences : L'évolution de la mesure")
    st.write(
        "Bien avant l'invention des appareils électriques, les alchimistes et chimistes utilisaient "
        "des substances naturelles pour repérer l'acidité. Le plus célèbre est le **papier de tournesol**, "
        "inventé au quatorzième siècle par le médecin espagnol Arnaldus de Villa Nova à partir d'extraits de lichens. "
        "Ce papier devenait rouge au contact d'un acide et bleu en milieu basique, offrant le tout premier repère visuel.\n\n"
        "La grande révolution technologique a lieu en **1934** en Californie. Le chimiste **Arnold Beckman** "
        "invente le tout premier **pH-mètre électronique** (alors appelé acidimètre). "
        "Conçu à la demande d'un ingénieur de l'industrie des agrumes qui cherchait un moyen fiable de mesurer "
        "l'acidité du jus de citron sans que les pigments ne faussent la lecture visuelle, cet appareil intégrait "
        "une électrode de verre robuste couplée à un amplificateur de courant. Cette invention a fait entrer la chimie "
        "dans l'ère moderne de la haute précision."
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET DISPOSITIFS ---
    st.subheader("Les outils modernes du laboratoire")
    st.write(
        "Pour déterminer expérimentalement la valeur du pH d'une solution aqueuse au laboratoire, "
        "on utilise principalement deux dispositifs aux précisions et aux fonctionnements différents :\n\n"
        "* **Le papier pH :** Il s'agit d'un rouleau de papier imprégné de plusieurs indicateurs colorés. "
        "Au contact d'une goutte de solution, le papier change instantanément de couleur. En comparant "
        "cette couleur avec le nuancier présent sur le boîtier, on obtient une valeur entière de pH (précision à l'unité).\n"
        "* **Le pH-mètre :** C'est un appareil de mesure électronique composé d'une sonde (électrode de verre) "
        "reliée à un boîtier voltmétrique convertisseur. Après étalonnage, la sonde plongée dans le liquide mesure "
        "le potentiel électrique induit par les ions oxonium et affiche une valeur décimale très précise (précision au dixième ou au centième)."
    )
    
    col_mes1, col_mes2 = st.columns(2)
    with col_mes1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre la différence entre ces deux outils, on peut imaginer une caricature comparant "
            "une règle en bois de charpentier et un pied à coulisse digital de haute précision. "
            "Le papier pH est comme l'œil humain qui estime une longueur à la louche selon des nuances de couleurs. "
            "Le pH-mètre, lui, agit comme un compteur d'ions électronique ultra-sensible capable de scanner "
            "le milieu microscopique pour compter chaque particule d'acide au millième près."
        )
        try:
            st.image("caricature_mesure_ph.jpg", caption="Caricature de la précision : Estimation visuelle contre scan électronique")
        except Exception:
            st.warning("L'image 'caricature_mesure_ph.jpg' est introuvable.")

    with col_mes2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "Sur un schéma de montage normalisé, la mesure au papier pH impose l'utilisation d'une coupelle "
            "et d'un agitateur en verre pour déposer une goutte sans contaminer le flacon d'origine.\n\n"
            "La mesure au pH-mètre exige quant à elle une manipulation rigoureuse : l'électrode est extrêmement "
            "fragile. Elle doit obligatoirement être rincée à l'eau distillée entre chaque mesure, essuyée "
            "délicatement avec un papier absorbant sans être frottée, et conservée dans une solution de stockage humide."
        )
        try:
            st.image("circuit_mesure_ph.jpg", caption="Protocole expérimental de mesure au papier pH et au pH-mètre électronique")
        except Exception:
            st.warning("L'image 'circuit_mesure_ph.jpg' est introuvable.")
            
    st.divider()

    # --- FOCUS : LES INDICATEURS COLORÉS NATURELS ---
    st.subheader("Chimie végétale : Les indicateurs colorés naturels")
    st.write(
        "Certaines plantes et végétaux de notre environnement contiennent des pigments naturels sensibles au pH, "
        "appelés anthocyanes. Ces molécules changent de structure géométrique et donc de couleur "
        "selon la concentration en ions oxonium du milieu. Voici 5 exemples incontournables :"
    )
    
    col_ind1, col_ind2 = st.columns(2)
    with col_ind1:
        st.write(
            "**Les 5 indicateurs végétaux sélectionnés :**\n"
            "* **Le chou rouge :** L'indicateur naturel le plus spectaculaire. Il passe du rouge vif en milieu très acide (pH < 3), au violet (pH neutre), puis au bleu, au vert et enfin au jaune en milieu très basique.\n"
            "* **Le thé noir :** Sa solution initialement ambrée s'éclaircit nettement et devient jaune pâle en présence d'un acide (comme le jus de citron) et fonce fortement en milieu basique.\n"
            "* **Le jus de myrtille :** Il arbore une coloration rouge intense dans un milieu acide et vire au vert-olive sombre dès que le milieu devient basique.\n"
            "* **Les pétales de rose rouge :** L'infusion de ces pétales donne un liquide qui passe du rose fuchsia en milieu acide au bleu-vert en milieu basique.\n"
            "* **Le curcuma :** Cette épice jaune vif reste jaune en milieu acide et neutre, mais vire de façon très nette au rouge-brun brique en milieu basique (pH > 8)."
        )
    with col_ind2:
        try:
            st.image("indicateurs_naturels.jpg", caption="Nuancier de coloration des extraits végétaux selon le pH")
        except Exception:
            st.warning("L'image 'indicateurs_naturels.jpg' est introuvable.")

    st.divider()
    
    # --- SECTION 2 : ZONE DE EXERCICES AND VERROUILLAGE DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab2_ph = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_ph

    afficher_atelier_mesure_ph(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier La mesure du pH.",
        key="check_certif_ph2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_ph_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_ph_aleatoire:
                    saisie = st.session_state.get(f"ph_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = 0.0
            if "champs_ph2_clean" in st.session_state:
                for ligne in st.session_state.champs_ph2_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph2_clean", "Choisir...") == attendu:
                        score_t2 += 1.0

            st.session_state.score_suite2_ph_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_ph_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_ph = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2_ph", False):
        scr1_t2 = st.session_state.get("score_suite2_ph_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_ph_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_ph", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER MESURE PH SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_ph2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Mesure pH - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Sciences Physiques</h1>
                <p>Atelier 2 : Techniques de mesure du pH, protocoles et histoire de la mesure</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz
        if "ordre_quiz_tab2_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Transition vers le second tableau pour le texte à trous
        html_export_ph2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous
        if "champs_ph2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                
                html_export_ph2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture propre du document
        html_export_ph2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph2 = preparer_nom_fichier("Rapport_Mesure_pH").replace(".txt", ".html")
        st.download_button(
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 2 (.html)",
            data=html_export_ph2,
            file_name=nom_fichier_html_ph2,
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("Les produits acides")
    
    # --- FOCUS HISTORIQUE : DE L'ANTIQUITÉ AUX ALCHIMISTES ---
    st.subheader("Histoire des Sciences : La découverte des acides")
    st.write(
        "Le mot acide vient du latin 'acidus', qui signifie aigre. Depuis l'Antiquité, les humains "
        "connaissent les acides faibles alimentaires, en particulier le vinaigre (acide acétique) obtenu "
        "par la fermentation naturelle du vin. À cette époque, le vinaigre était le produit le plus acide disponible.\n\n"
        "La grande révolution a lieu au Moyen Âge grâce aux travaux des alchimistes orientaux et occidentaux, "
        "notamment le célèbre savant Jabir ibn Hayyan (connu sous le nom de Geber). En distillant des minéraux comme "
        "le vitriol et le salpêtre, les alchimistes réussissent à synthétiser pour la première fois des **acides forts minéraux** : "
        "l'acide nitrique, l'acide sulfurique (alors appelé huile de vitriol) et l'acide chlorhydrique (esprit de sel).\n\n"
        "Ces découvertes ont bouleversé la métallurgie et la médecine, car ces nouveaux liquides étaient capables "
        "de dissoudre des métaux réputés indestructibles comme le cuivre ou le fer, ouvrant ainsi la voie à la chimie moderne."
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET PROPRIÉTÉS ---
    st.subheader("Propriétés et caractéristiques des acides")
    st.write(
        "Une solution est qualifiée d'acide lorsque sa valeur de pH est strictement inférieure à 7. "
        "A l'échelle microscopique, cela signifie que la concentration en ions oxonium H3O+ est supérieure "
        "à celle des ions hydroxyde OH-.\n\n"
        "Les acides de notre quotidien se partagent en deux grandes catégories :\n"
        "* **Les acides faibles (alimentaires) :** Ils possèdent un pH proche de 7 (entre 3 et 6). Ils ont un goût "
        "aigre ou piquant caractéristique (citron, vinaigre, tomate) et sont inoffensifs à la consommation.\n"
        "* **Les acides forts (industriels) :** Ils possèdent un pH très bas, proche de 0 (acide chlorhydrique, acide sulfurique). "
        "Ils sont extrêmement corrosifs. Ils attaquent les métaux, détruisent les tissus vivants et provoquent de "
        "graves brûlures chimiques. Leur manipulation impose le port obligatoire d'une blouse, de lunettes et de gants."
    )
    
    col_aci1, col_acid2 = st.columns(2)
    with col_aci1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour imaginer le comportement d'un acide fort concentré, on peut utiliser la caricature "
            "de petits rongeurs microscopiques affamés. Plus le pH s'approche de zéro, plus ces petits personnages "
            "Oxonium (H3O+) sont nombreux et s'activent avec ferveur pour grignoter et dissoudre les surfaces "
            "sur lesquelles ils sont déposés (métaux, tissus, peau). Diluer la solution revient à écarter "
            "ces rongeurs en ajoutant de l'eau, diminuant ainsi leur agressivité collective."
        )
        try:
            st.image("caricature_acides.jpg", caption="Caricature de l'agressivité corrosive des ions acides concentrés")
        except Exception:
            st.warning("L'image 'caricature_acides.jpg' est introuvable.")

    with col_acid2:
        st.subheader("Signalisation de sécurité : Les pictogrammes de danger")
        st.write(
            "Sur les flacons de laboratoire ou les produits ménagers concentrés, la présence d'un acide fort "
            "est obligatoirement signalée par des symboles de sécurité internationaux normalisés. "
            "Le premier indique que le produit est **corrosif** (il ronge le métal et la peau) et le second "
            "indique qu'il peut être **toxique** ou irritant pour les voies respiratoires."
        )
        
        try:
            st.image("securite_acides.jpg", caption="Pictogrammes officiels de danger corrosif et irritant")
        except Exception:
            st.warning("L'image 'securite_acides.jpg' est introuvable.")
            
    st.write(
        "En cas de projection accidentelle d'un produit acide sur la peau, le premier réflexe scientifique "
        "consiste à rincer immédiatement et abondamment à l'eau courante pendant plusieurs minutes pour diluer "
        "le produit et remonter le pH le plus vite possible vers 7."
    )

    st.divider()

    # --- SECTION 2 : TABLEAU SCIENTIFIQUE ET MOLÉCULAIRE DES ACIDES ---
    st.subheader("Inventaire moléculaire : 10 produits acides de la vie courante")
    st.write(
        "Voici le tableau de référence listant 10 solutions acides courantes. "
        "Sélectionnez un produit dans le menu pour visualiser sa structure moléculaire dessinée en direct."
    )

    # Dictionnaire des 10 acides de la vie courante
    dico_acides = {
        "Jus de citron (Acide citrique)": {"formula": "C6H8O7", "ph": "2.3", "desc": "Acide organique présent dans les agrumes, utilisé en alimentation.", "type": "O"},
        "Vinaigre (Acide acétique)": {"formula": "C2H4O2", "ph": "2.9", "desc": "Issu de la fermentation du vin, utilisé pour la cuisine et le nettoyage.", "type": "CH3COOH"},
        "Esprit de sel (Acide chlorhydrique)": {"formula": "HCl", "ph": "1.0", "desc": "Acide fort industriel utilisé pour détartrer et décaper les toilettes.", "type": "HCl"},
        "Liquide de batterie (Acide sulfurique)": {"formula": "H2SO4", "ph": "0.5", "desc": "Acide fort industriel ultra-corrosif chargé dans les batteries de voiture.", "type": "H2SO4"},
        "Soda au cola (Acide phosphorique)": {"formula": "H3PO4", "ph": "2.5", "desc": "Additif alimentaire utilisé pour donner le goût acide aux boissons gazeuses.", "type": "H3PO4"},
        "Jus de pomme (Acide malique)": {"formula": "C4H6O5", "ph": "3.5", "desc": "Acide organique naturel présent dans la majorité des fruits à pépins.", "type": "MAL"},
        "Lait tourné (Acide lactique)": {"formula": "C3H6O3", "ph": "4.4", "desc": "Produit par les bactéries lors de la fermentation du lactose dans le lait.", "type": "LAC"},
        "Aspirine (Acide acétylsalicylique)": {"formula": "C9H8O4", "ph": "3.5", "desc": "Médicament anti-inflammatoire et analgésique très répandu.", "type": "ASP"},
        "Vitamine C (Acide ascorbique)": {"formula": "C6H8O6", "ph": "3.0", "desc": "Antioxydant essentiel présent dans les fruits et législations physiologiques.", "type": "ASC"},
        "Limonade (Acide carbonique)": {"formula": "H2CO3", "ph": "4.0", "desc": "Formé par la dissolution du dioxyde de carbone gazeux dans l'eau.", "type": "H2CO3"}
    }

    # Affichage du tableau global
    data_table_acides = []
    for nom, infos in dico_acides.items():
        data_table_acides.append([nom, infos["formula"], infos["ph"], infos["desc"]])
    
    df_acides = pd.DataFrame(data_table_acides, columns=["Nom du produit (Acide associé)", "Formule brute", "pH approximatif", "Description et usage"])
    st.table(df_acides)

    # Selectbox pour le focus moléculaire individuel
    choix_acide_visuel = st.selectbox("Choisir un produit pour dessiner son architecture moléculaire :", options=list(dico_acides.keys()), key="sel_acide_tab3")
    
    col_leg_act, col_graph_act = st.columns([0.4, 0.6])
    with col_leg_act:
        st.markdown("**Légendes des sphères de couleur :**")
        st.write("* Blanc : Hydrogène (H)")
        st.write("* Noir : Carbone (C)")
        st.write("* Rouge : Oxygène (O)")
        st.write("* Vert : Chlore (Cl)")
        st.write("* Jaune : Soufre (S)")
        st.write(f"**Produit :** {choix_acide_visuel}")
        st.write(f"**Formule brute :** {dico_acides[choix_acide_visuel]['formula']}")
        st.write(f"**pH indicatif :** {dico_acides[choix_acide_visuel]['ph']}")

    with col_graph_act:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_ac, ax_ac = plt.subplots(figsize=(6, 5.5), facecolor="white")
        ax_ac.set_facecolor("white")

        tipo = dico_acides[choix_acide_visuel]["formula"]
        
        # --- MOTEUR DE TRACÉ GÉOMÉTRIQUE RIGOUREUX ---
        def bond(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.05
                ax_ac.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_ac.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_ac.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        def atom(p, sym, mobile=False):
            # Tous les hydrogènes restent blancs/gris clair
            col = "#ecf0f1" if sym=='H' else ("#2b3e50" if sym=='C' else ("#e74c3c" if sym=='O' else ("#2ecc71" if sym=='Cl' else ("#f1c40f" if sym=='S' else "#a855f7"))))
            t_col = "black" if sym in ['H','S','P'] else "white"
            
            # Dessin de la sphère de l'atome
            ax_ac.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=col, edgecolor="#1a252f", linewidth=2, zorder=2))
            
            # Si c'est l'hydrogène responsable de l'acidité, on ajoute l'entourage en pointillés rouges
            if mobile and sym == 'H':
                ax_ac.add_patch(patches.Circle((p[0], p[1]), 0.32, fill=False, edgecolor="#ef4444", linewidth=2, linestyle="--", zorder=3))
                
            ax_ac.text(p[0], p[1], sym, color=t_col, weight="bold", fontsize=9, ha="center", va="center", zorder=4)

        # --- REPRÉSENTATION EXHAUSTIVE DES 10 STRUCTURES ACIDES DE LA LISTE ---
        if tipo == "HCl": # 1. Acide chlorhydrique (1 H)
            p_cl, p_h = np.array([3.0, 2.5]), np.array([4.8, 2.5])
            bond(p_cl, p_h)
            atom(p_cl, 'Cl'); atom(p_h, 'H', mobile=True)
            ax_ac.set_xlim(1.5, 6.5); ax_ac.set_ylim(1.0, 4.0)
            
        elif tipo == "C2H4O2": # 2. Acide acétique / Vinaigre (4 H)
            c1, c2 = np.array([2.5, 2.5]), np.array([4.1, 2.5])
            o1, o2 = np.array([4.9, 3.6]), np.array([4.9, 1.4])
            h_o = np.array([6.0, 1.4])
            h1, h2, h3 = np.array([1.4, 2.5]), np.array([2.5, 3.6]), np.array([2.5, 1.4])
            bond(c1, c2); bond(c1, h1); bond(c1, h2); bond(c1, h3)
            bond(c2, o1, double=True); bond(c2, o2); bond(o2, h_o)
            atom(c1, 'C'); atom(c2, 'C'); atom(o1, 'O'); atom(o2, 'O')
            atom(h1, 'H'); atom(h2, 'H'); atom(h3, 'H'); atom(h_o, 'H', mobile=True)
            ax_ac.set_xlim(0.8, 6.6); ax_ac.set_ylim(0.8, 4.2)

        elif tipo == "H2CO3": # 3. Acide carbonique (2 H)
            c = np.array([4.0, 2.5])
            o1, o2, o3 = np.array([4.0, 3.8]), np.array([2.9, 1.7]), np.array([5.1, 1.7])
            h1, h2 = np.array([1.8, 1.7]), np.array([6.2, 1.7])
            bond(c, o1, double=True); bond(c, o2); bond(c, o3); bond(o2, h1); bond(o3, h2)
            atom(c, 'C'); atom(o1, 'O'); atom(o2, 'O'); atom(o3, 'O')
            atom(h1, 'H', mobile=True); atom(h2, 'H', mobile=True)
            ax_ac.set_xlim(1.0, 7.0); ax_ac.set_ylim(0.8, 4.5)
            
        elif tipo == "H2SO4": # 4. Acide sulfurique (2 H)
            s = np.array([4.0, 2.5])
            o1, o2 = np.array([4.0, 3.9]), np.array([4.0, 1.1])
            o3, o4 = np.array([2.6, 2.5]), np.array([5.4, 2.5])
            h1, h2 = np.array([1.5, 2.5]), np.array([6.5, 2.5])
            bond(s, o1, double=True); bond(s, o2, double=True); bond(s, o3); bond(s, o4); bond(o3, h1); bond(o4, h2)
            atom(s, 'S'); atom(o1, 'O'); atom(o2, 'O'); atom(o3, 'O'); atom(o4, 'O')
            atom(h1, 'H', mobile=True); atom(h2, 'H', mobile=True)
            ax_ac.set_xlim(0.8, 7.2); ax_ac.set_ylim(0.5, 4.5)

        elif tipo == "H3PO4": # 5. Acide phosphorique (3 H)
            p = np.array([4.0, 2.5])
            o1, o2, o3, o4 = np.array([4.0, 4.0]), np.array([2.7, 1.8]), np.array([5.3, 1.8]), np.array([4.0, 1.2])
            h1, h2, h3 = np.array([1.6, 1.8]), np.array([6.4, 1.8]), np.array([5.1, 0.5])
            bond(p, o1, double=True); bond(p, o2); bond(p, o3); bond(p, o4); bond(o2, h1); bond(o3, h2); bond(o4, h3)
            atom(p, 'P'); atom(o1, 'O'); atom(o2, 'O'); atom(o3, 'O'); atom(o4, 'O')
            atom(h1, 'H', mobile=True); atom(h2, 'H', mobile=True); atom(h3, 'H', mobile=True)
            ax_ac.set_xlim(1.0, 7.0); ax_ac.set_ylim(0.1, 4.6)

        elif tipo == "C3H6O3": # 6. Acide lactique / Lait tourné (6 H)
            c1, c2, c3 = np.array([1.6, 2.5]), np.array([3.0, 2.5]), np.array([4.4, 2.5])
            o_c2 = np.array([3.0, 3.8])
            h_oc2 = np.array([3.0, 4.9])
            o1_c3, o2_c3 = np.array([5.1, 3.6]), np.array([5.1, 1.4])
            h_oc3 = np.array([6.2, 1.4])
            h1, h2, h3 = np.array([0.5, 2.5]), np.array([1.6, 3.6]), np.array([1.6, 1.4])
            h4 = np.array([4.1, 3.3])
            bond(c1, c2); bond(c2, c3); bond(c2, o_c2); bond(o_c2, h_oc2)
            bond(c3, o1_c3, double=True); bond(c3, o2_c3); bond(o2_c3, h_oc3)
            bond(c1, h1); bond(c1, h2); bond(c1, h3); bond(c2, h4)
            atom(c1, 'C'); atom(c2, 'C'); atom(c3, 'C'); atom(o_c2, 'O'); atom(o1_c3, 'O'); atom(o2_c3, 'O')
            atom(h1, 'H'); atom(h2, 'H'); atom(h3, 'H'); atom(h4, 'H'); atom(h_oc2, 'H'); atom(h_oc3, 'H', mobile=True)
            ax_ac.set_xlim(0.1, 6.8); ax_ac.set_ylim(0.8, 5.4)

        elif tipo == "C4H6O5": # 7. Acide malique / Jus de pomme (6 H)
            c1, c2, c3, c4 = np.array([1.6, 2.5]), np.array([2.8, 1.7]), np.array([4.1, 2.5]), np.array([5.3, 1.7])
            o1, o2 = np.array([1.6, 3.7]), np.array([0.5, 1.8])
            h_o2 = np.array([-0.5, 1.8])
            o_c3 = np.array([4.1, 3.7])
            h_oc3 = np.array([4.1, 4.8])
            o3, o4 = np.array([5.3, 0.5]), np.array([6.4, 2.4])
            h_o4 = np.array([7.4, 2.4])
            h_c2_1, h_c2_2 = np.array([2.8, 0.6]), np.array([3.4, 1.1])
            h_c3 = np.array([4.7, 1.9])
            bond(c1, c2); bond(c2, c3); bond(c3, c4); bond(c1, o1, double=True); bond(c1, o2); bond(o2, h_o2)
            bond(c3, o_c3); bond(o_c3, h_oc3); bond(c4, o3, double=True); bond(c4, o4); bond(o4, h_o4)
            bond(c2, h_c2_1); bond(c2, h_c2_2); bond(c3, h_c3)
            atom(c1, 'C'); atom(c2, 'C'); atom(c3, 'C'); atom(c4, 'C')
            atom(o1, 'O'); atom(o2, 'O'); atom(o_c3, 'O'); atom(o3, 'O'); atom(o4, 'O')
            atom(h_o2, 'H', mobile=True); atom(h_oc3, 'H'); atom(h_o4, 'H', mobile=True)
            atom(h_c2_1, 'H'); atom(h_c2_2, 'H'); atom(h_c3, 'H')
            ax_ac.set_xlim(-0.8, 7.8); ax_ac.set_ylim(0.2, 5.2)

        elif tipo == "C6H8O6": # 8. Vitamine C (8 H)
            o_ring = np.array([4.0, 3.2])
            c1, c2, c3, c4 = np.array([2.8, 2.5]), np.array([3.3, 1.3]), np.array([4.7, 1.3]), np.array([5.2, 2.5])
            o_c1 = np.array([1.7, 2.8])
            o_c2, o_c3 = np.array([2.6, 0.2]), np.array([5.4, 0.2])
            h_o2, h_o3 = np.array([1.6, 0.2]), np.array([6.4, 0.2])
            # Chaîne latérale externe CH(OH)-CH2OH pour compléter la structure de la vitamine C
            c5, c6 = np.array([6.3, 3.2]), np.array([7.4, 2.5])
            o_c5, o_c6 = np.array([6.3, 4.4]), np.array([8.5, 3.2])
            h_o5, h_o6 = np.array([7.1, 4.9]), np.array([9.3, 2.7])
            h_c4, h_c5, h_c6_1, h_c6_2 = np.array([5.5, 1.9]), np.array([6.9, 3.8]), np.array([7.4, 1.5]), np.array([8.0, 2.0])
            bond(c1, o_ring); bond(o_ring, c4); bond(c4, c3); bond(c3, c2); bond(c2, c1)
            bond(c1, o_c1, double=True); bond(c2, o_c2); bond(c3, o_c3); bond(o_c2, h_o2); bond(o_c3, h_o3)
            bond(c4, c5); bond(c5, c6); bond(c5, o_c5); bond(c6, o_c6); bond(o_c5, h_o5); bond(o_c6, h_o6)
            bond(c4, h_c4); bond(c5, h_c5); bond(c6, h_c6_1); bond(c6, h_c6_2)
            atom(o_ring, 'O'); atom(c1, 'C'); atom(c2, 'C'); atom(c3, 'C'); atom(c4, 'C'); atom(c5, 'C'); atom(c6, 'C')
            atom(o_c1, 'O'); atom(o_c2, 'O'); atom(o_c3, 'O'); atom(o_c5, 'O'); atom(o_c6, 'O')
            atom(h_o2, 'H', mobile=True); atom(h_o3, 'H', mobile=True); atom(h_o5, 'H'); atom(h_o6, 'H')
            atom(h_c4, 'H'); atom(h_c5, 'H'); atom(h_c6_1, 'H'); atom(h_c6_2, 'H')
            ax_ac.set_xlim(1.0, 9.8); ax_ac.set_ylim(0.0, 5.4)

        elif tipo == "C6H8O7": # 9. Acide citrique / Citron (8 H)
            c_cent = np.array([4.0, 2.5])
            o_cent = np.array([4.0, 3.8])
            h_ocent = np.array([4.8, 4.3])
            c_left, c_right = np.array([2.7, 2.5]), np.array([5.3, 2.5])
            c_c1, c_c3 = np.array([1.6, 1.5]), np.array([6.4, 1.5])
            o_c1_d, o_c1_s = np.array([1.6, 0.4]), np.array([0.7, 2.1])
            o_c3_d, o_c3_s = np.array([6.4, 0.4]), np.array([7.3, 2.1])
            h_oc1, h_oc3 = np.array([0.1, 1.5]), np.array([7.9, 1.5])
            c_c2 = np.array([4.0, 1.3])
            o_c2_d, o_c2_s = np.array([4.9, 0.6]), np.array([3.1, 0.6])
            h_oc2 = np.array([2.4, 0.9])
            h_l1, h_l2 = np.array([2.7, 3.4]), np.array([2.1, 2.1])
            h_r1, h_r2 = np.array([5.3, 3.4]), np.array([5.9, 2.1])
            bond(c_cent, o_cent); bond(o_cent, h_ocent); bond(c_cent, c_left); bond(c_cent, c_right); bond(c_cent, c_c2)
            bond(c_left, c_c1); bond(c_right, c_c3); bond(c_left, h_l1); bond(c_left, h_l2); bond(c_right, h_r1); bond(c_right, h_r2)
            bond(c_c1, o_c1_d, double=True); bond(c_c1, o_c1_s); bond(o_c1_s, h_oc1)
            bond(c_c3, o_c3_d, double=True); bond(c_c3, o_c3_s); bond(o_c3_s, h_oc3)
            bond(c_c2, o_c2_d, double=True); bond(c_c2, o_c2_s); bond(o_c2_s, h_oc2)
            atom(c_cent, 'C'); atom(o_cent, 'O'); atom(h_ocent, 'H'); atom(c_left, 'C'); atom(c_right, 'C')
            atom(c_c1, 'C'); atom(c_c2, 'C'); atom(c_c3, 'C')
            atom(o_c1_d, 'O'); atom(o_c1_s, 'O'); atom(o_c2_d, 'O'); atom(o_c2_s, 'O'); atom(o_c3_d, 'O'); atom(o_c3_s, 'O')
            atom(h_oc1, 'H', mobile=True); atom(h_oc2, 'H', mobile=True); atom(h_oc3, 'H', mobile=True)
            atom(h_l1, 'H'); atom(h_l2, 'H'); atom(h_r1, 'H'); atom(h_r2, 'H')
            ax_ac.set_xlim(-0.2, 8.2); ax_ac.set_ylim(0.1, 4.9)

        elif tipo == "C9H8O4": # 10. Aspirine (8 H)
            c1, c2, c3, c4, c5, c6 = np.array([3.2, 2.5]), np.array([3.2, 3.7]), np.array([4.3, 4.4]), np.array([5.4, 3.7]), np.array([5.4, 2.5]), np.array([4.3, 1.8])
            c_carb = np.array([2.0, 4.4])
            o_double, o_simple = np.array([2.0, 5.5]), np.array([0.9, 3.8])
            h_o = np.array([0.1, 3.8])
            h_ar3, h_c4, h_c5, h_c6 = np.array([4.3, 5.4]), np.array([6.2, 4.2]), np.array([6.2, 2.0]), np.array([4.3, 0.9])
            # Groupe ester acétyle lié sur C1 pour finir la structure moléculaire réelle de l'aspirine
            o_est = np.array([2.1, 1.6])
            c_est = np.array([1.5, 0.5])
            o_est_d = np.array([2.0, -0.5])
            c_met = np.array([0.1, 0.5])
            h_m1, h_m2, h_m3 = np.array([-0.5, 1.2]), np.array([-0.5, -0.2]), np.array([0.1, -0.3])
            bond(c1, c2, double=True); bond(c2, c3); bond(c3, c4, double=True); bond(c4, c5); bond(c5, c6, double=True); bond(c6, c1)
            bond(c2, c_carb); bond(c_carb, o_double, double=True); bond(c_carb, o_simple); bond(o_simple, h_o)
            bond(c3, h_ar3); bond(c4, h_c4); bond(c5, h_c5); bond(c6, h_c6)
            bond(c1, o_est); bond(o_est, c_est); bond(c_est, o_est_d, double=True); bond(c_est, c_met); bond(c_met, h_m1); bond(c_met, h_m2); bond(c_met, h_m3)
            atom(c1, 'C'); atom(c2, 'C'); atom(c3, 'C'); atom(c4, 'C'); atom(c5, 'C'); atom(c6, 'C'); atom(c_carb, 'C')
            atom(o_double, 'O'); atom(o_simple, 'O'); atom(o_est, 'O'); atom(c_est, 'C'); atom(o_est_d, 'O'); atom(c_met, 'C')
            atom(h_o, 'H', mobile=True); atom(h_ar3, 'H'); atom(h_c4, 'H'); atom(h_c5, 'H'); atom(h_c6, 'H')
            atom(h_m1, 'H'); atom(h_m2, 'H'); atom(h_m3, 'H')
            ax_ac.set_xlim(-0.8, 6.8); ax_ac.set_ylim(-0.8, 6.0)


        ax_ac.axis("off")
        st.pyplot(fig_ac)



            

    if "suite_verrouille_tab3_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab3_ph = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_ph

    # Affichage du module de questions spécifique aux produits acides
    afficher_atelier_produits_acides(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les produits acides.",
        key="check_certif_ph3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_ph_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_ph_aleatoire:
                    saisie = st.session_state.get(f"ph_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            score_t3 = 0.0
            if "champs_ph3_clean" in st.session_state:
                for ligne in st.session_state.champs_ph3_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph3_clean", "Choisir...") == attendu: 
                        score_t3 += 1.0

            st.session_state.score_suite3_ph_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_ph_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_ph = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 3 ---
    if st.session_state.get("suite_verrouille_tab3_ph", False):
        scr1_t3 = st.session_state.get("score_suite3_ph_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_ph_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_ph", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER PRODUITS ACIDES SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_ph3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Produits Acides - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Sciences Physiques</h1>
                <p>Atelier 3 : Etude des produits acides du quotidien, formules, pictogrammes et histoire</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ph3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_ph3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_ph3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ph3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_ph3 = preparer_nom_fichier("Rapport_Produits_Acides").replace(".txt", ".html")
        st.download_button(
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 3 (.html)",
            data=html_export_ph3,
            file_name=nom_fichier_html_ph3,
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("Les produits basiques")
    
    # --- FOCUS HISTORIQUE : DES CENDRES À LA SOUDE MODERNE ---
    st.subheader("Histoire des Sciences : La découverte des bases")
    st.write(
        "Le mot alcalin, souvent utilisé comme synonyme de basique, vient de l'arabe 'al-qaly', qui signifie "
        "les cendres calcinées. Depuis l'Antiquité, les humains ont remarqué que l'eau filtrée à travers des cendres "
        "de bois possédait des propriétés remarquables pour nettoyer, dissoudre les graisses et fabriquer les premiers savons. "
        "Ces solutions contenaient du carbonate de potassium, une base faible.\n\n"
        "Au dix-huitième siècle, les chimistes réussissent à isoler des bases beaucoup plus puissantes à partir du sel de mer "
        "et de minéraux. L'invention du procédé Leblanc, puis du procédé Solvay, a permis de produire de la soude industrielle "
        "à grande échelle. Ces bases fortes sont devenues des piliers indispensables pour l'essor des industries du verre, "
        "du textile, du papier et des produits de nettoyage modernes."
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET PROPRIÉTÉS ---
    st.subheader("Propriétés et caractéristiques des bases")
    st.write(
        "Une solution est qualifiée de basique (ou alcaline) lorsque sa valeur de pH est strictement supérieure à 7. "
        "À l'échelle microscopique, cela signifie que la concentration en ions hydroxyde OH⁻ est supérieure "
        "à celle des ions oxonium H₃O⁺.\n\n"
        "Les produits basiques de notre quotidien se partagent en deux grandes catégories :\n"
        "* **Les bases faibles (ménagères ou médicales) :** Elles possèdent un pH proche de 7 (entre 8 et 10). Elles ont un goût "
        "amer et une texture glissante ou savonneuse au toucher (bicarbonate, eau de mer, savon). Elles servent souvent à apaiser "
        "les brûlures d'estomac causées par les acides.\n"
        "* **Les bases fortes (industrielles) :** Elles possèdent un pH très élevé, proche de 14 (soude caustique, eau de Javel concentrée). "
        "Tout comme les acides forts, elles sont extrêmement corrosives. Elles ont la particularité de dissoudre instantanément les matières "
        "organiques et les graisses. Leur manipulation impose le port obligatoire d'une blouse, de lunettes et de gants."
    )
    
    col_bas1, col_bas2 = st.columns(2)
    with col_bas1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour imaginer l'action d'une base forte concentrée, on peut utiliser la caricature de petits nettoyeurs "
            "microscopiques munis de balais et de solvants surpuissants. Plus le pH s'approche de 14, plus ces personnages "
            "Hydroxyde (OH⁻) sont nombreux et s'attaquent aux graisses et aux tissus pour les décomposer. Diluer la solution "
            "revient à réduire le nombre de ces nettoyeurs en ajoutant des molécules d'eau, ce qui calme leur activité "
            "agressive et ramène le pH vers la neutralité de l'eau."
        )
        try:
            st.image("caricature_bases.jpg", caption="Caricature de l'action corrosive des ions basiques concentrés")
        except Exception:
            st.warning("L'image 'caricature_bases.jpg' est introuvable.")

    with col_acid2:
        st.subheader("Signalisation de sécurité : Les dangers des bases")
        st.write(
            "Les flacons de produits basiques concentrés (comme les déboucheurs de canalisations à la soude) portent "
            "également le pictogramme international du losange blanc bordé de rouge représentant un produit **corrosif**.\n\n"
            "Une idée reçue fréquente consiste à penser que les bases sont inoffensives par rapport aux acides. C'est faux : "
            "les projections de bases fortes sont parfois plus graves que celles des acides, car elles détruisent les graisses "
            "de la peau sans provoquer de douleur immédiate, s'enfonçant ainsi profondément dans les tissus. Un rinçage immédiat "
            "et prolongé à l'eau courante est indispensable."
        )
        try:
            st.image("securite_bases.jpg", caption="Pictogramme corrosif et consignes de sécurité pour les bases fortes")
        except Exception:
            st.warning("L'image 'securite_bases.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION 2 : TABLEAU D'INVENTAIRE ET MOLÉCULES ---
    st.subheader("Inventaire moléculaire : 10 produits basiques de la vie courante")
    st.write(
        "Voici le tableau de référence listant 10 solutions basiques courantes. "
        "Sélectionnez un produit dans le menu pour visualiser sa structure moléculaire."
    )

    # Dictionnaire des 10 bases avec de vrais caractères d'indices Unicode
    dico_bases = {
        "Déboucheur liquide (Soude caustique)": {"formula": "NaOH", "formula_visuelle": "NaOH", "ph": "14.0", "desc": "Base forte industrielle ultra-corrosive utilisée pour détruire les bouchons de cheveux et de graisse."},
        "Eau de Javel (Hypochlorite de sodium)": {"formula": "NaClO", "formula_visuelle": "NaClO", "ph": "11.5", "desc": "Solution désinfectante et blanchissante puissante, à manipuler avec précaution."},
        "Nettoyant ménager (Ammoniaque)": {"formula": "NH3", "formula_visuelle": "NH₃", "ph": "11.5", "desc": "Gaz dissous à l'odeur très piquante, utilisé pour dégraisser les vitres et les sols."},
        "Poudre à lever (Bicarbonate de sodium)": {"formula": "NaHCO3", "formula_visuelle": "NaHCO₃", "ph": "8.4", "desc": "Base faible totalement inoffensive utilisée en cuisine et pour l'hygiène dentaire."},
        "Chaux éteinte (Hydroxyde de calcium)": {"formula": "Ca(OH)2", "formula_visuelle": "Ca(OH)₂", "ph": "12.4", "desc": "Utilisée en bâtiment pour les enduits et en agriculture pour corriger l'acidité des sols."},
        "Médicament anti-acide (Hydroxyde de magnésium)": {"formula": "Mg(OH)2", "formula_visuelle": "Mg(OH)₂", "ph": "10.0", "desc": "Utilisé en pharmacie pour neutraliser l'excès d'acidité dans l'estomac."},
        "Eau de mer": {"formula": "NaCl_mix", "formula_visuelle": "Milieu salin", "ph": "8.2", "desc": "Solution naturelle légèrement basique grâce à la présence de carbonates dissous."},
        "Savon de Marseille": {"formula": "RCOONa", "formula_visuelle": "RCOONa", "ph": "9.5", "desc": "Produit issu de la réaction entre un corps gras et de la soude, alcalin au toucher."},
        "Eau de chaux (Test du CO2)": {"formula": "Ca(OH)2_dil", "formula_visuelle": "Ca(OH)₂", "ph": "11.0", "desc": "Solution limpide qui se trouble spécifiquement en présence de dioxyde de carbone."},
        "Cendres de bois (Carbonate de potassium)": {"formula": "K2CO3", "formula_visuelle": "K₂CO₃", "ph": "11.0", "desc": "Utilisées historiquement pour fabriquer la lessive ancestrale par filtration."}
    }

    # Rendu propre du tableau avec st.dataframe natif
    data_table_bases = []
    for nom, infos in dico_bases.items():
        data_table_bases.append([nom, infos["formula_visuelle"], infos["ph"], infos["desc"]])
    
    df_bases = pd.DataFrame(data_table_bases, columns=["Nom du produit (Base associée)", "Formule brute", "pH approximatif", "Description et usage"])
    st.dataframe(df_bases, use_container_width=True, hide_index=True)

    # Sélecteur pour le focus moléculaire
    choix_base_visuel = st.selectbox("Choisir un produit pour dessiner son architecture moléculaire :", options=list(dico_bases.keys()), key="sel_base_tab4")
    
    col_leg_b, col_graph_b = st.columns([0.4, 0.6])

    
    with col_leg_b:
        st.markdown("**Légendes des sphères de couleur :**")
        st.write("* Blanc : Hydrogène (H)")
        st.write("* Rouge : Oxygène (O)")
        st.write("* Noir : Carbone (C)")
        st.write("* Vert : Chlore (Cl) ou Sodium (Na)")
        st.write("* Bleu foncé : Azote (N)")
        st.markdown(f"**Produit :** {choix_base_visuel}")
        st.write(f"**Formule brute :** {dico_bases[choix_base_visuel]['formula_visuelle']}")
        st.write(f"**pH indicatif :** {dico_bases[choix_base_visuel]['ph']}")

    with col_graph_b:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_ba, ax_ba = plt.subplots(figsize=(6, 5.5), facecolor="white")
        ax_ba.set_facecolor("white")

        tipo_b = dico_bases[choix_base_visuel]["formula"]
        
        # --- MOTEUR DE TRACÉ GÉOMÉTRIQUE RIGOUREUX ---
        def bond_b(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.05
                ax_ba.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_ba.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_ba.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        def atom_b(p, sym, mobile=False):
            # Attribution rigoureuse des couleurs CPK internationales
            if sym == 'H': col, t_col = "#ecf0f1", "black"
            elif sym == 'O': col, t_col = "#e74c3c", "white"
            elif sym == 'C': col, t_col = "#2b3e50", "white"
            elif sym == 'vN': col, t_col = "#1e3a8a", "white"   # Bleu foncé pour l'Azote
            elif sym == 'Na': col, t_col = "#2ecc71", "white"  # Vert pour le Sodium
            elif sym == 'Cl': col, t_col = "#a855f7", "white"  # Violet pour le Chlore
            elif sym == 'Ca': col, t_col = "#f1c40f", "black"  # Jaune pour le Calcium
            elif sym == 'Mg': col, t_col = "#e67e22", "white"  # Orange pour le Magnésium
            elif sym == 'K': col, t_col = "#9b59b6", "white"   # Mauve pour le Potassium
            else: col, t_col = "#95a5a6", "black"
            
            # Correction du label interne d'affichage pour vN
            lbl = 'N' if sym == 'vN' else sym

            # Dessin de la sphère de l'atome
            ax_ba.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=col, edgecolor="#1a252f", linewidth=2, zorder=2))
            
            # Halo en pointillés rouges sur le groupement OH responsable de la basicité
            if mobile and sym in ['O', 'H']:
                ax_ba.add_patch(patches.Circle((p[0], p[1]), 0.32, fill=False, edgecolor="#ef4444", linewidth=2, linestyle="--", zorder=3))
                
            ax_ba.text(p[0], p[1], lbl, color=t_col, weight="bold", fontsize=9, ha="center", va="center", zorder=4)

        # --- DESSIN DES STRUCTURES RÉELLES DE L'INVENTAIRE DES BASES ---
        if tipo_b == "NaOH": # 1. Déboucheur liquide (Soude caustique)
            p_na, p_o, p_h = np.array([2.5, 2.5]), np.array([4.1, 2.5]), np.array([5.6, 2.5])
            bond_b(p_na, p_o); bond_b(p_o, p_h)
            atom_b(p_na, 'Na'); atom_b(p_o, 'O', mobile=True); atom_b(p_h, 'H', mobile=True)
            ax_ba.set_xlim(1.5, 6.5); ax_ba.set_ylim(1.0, 4.0)
            
        elif tipo_b == "NH3": # 2. Nettoyant ménager (Ammoniaque - Pyramide trigonale)
            p_n = np.array([4.0, 2.5])
            p_h1, p_h2, p_h3 = np.array([2.5, 2.5]), np.array([4.7, 3.8]), np.array([4.7, 1.2])
            bond_b(p_n, p_h1); bond_b(p_n, p_h2); bond_b(p_n, p_h3)
            atom_b(p_n, 'vN'); atom_b(p_h1, 'H'); atom_b(p_h2, 'H'); atom_b(p_h3, 'H')
            ax_ba.set_xlim(1.5, 6.0); ax_ba.set_ylim(0.5, 4.5)
            
        elif tipo_b == "NaClO": # 3. Eau de Javel (Hypochlorite de sodium)
            p_na, p_cl, p_o = np.array([2.3, 2.5]), np.array([4.0, 2.5]), np.array([5.7, 2.5])
            bond_b(p_na, p_cl); bond_b(p_cl, p_o)
            atom_b(p_na, 'Na'); atom_b(p_cl, 'Cl'); atom_b(p_o, 'O')
            ax_ba.set_xlim(1.2, 6.8); ax_ba.set_ylim(1.0, 4.0)
            
        elif tipo_b == "NaHCO3": # 4. Bicarbonate de sodium complet avec tous ses atomes
            p_na = np.array([1.4, 2.5])
            p_c = np.array([3.2, 2.5])
            p_o1 = np.array([3.2, 3.9])
            p_o2 = np.array([4.4, 1.6])
            p_o3 = np.array([2.0, 1.6])
            p_h = np.array([2.0, 0.4])
            bond_b(p_na, p_o3); bond_b(p_c, p_o1, double=True); bond_b(p_c, p_o2); bond_b(p_c, p_o3); bond_b(p_o3, p_h)
            atom_b(p_na, 'Na'); atom_b(p_c, 'C'); atom_b(p_o1, 'O'); atom_b(p_o2, 'O'); atom_b(p_o3, 'O'); atom_b(p_h, 'H')
            ax_ba.set_xlim(0.6, 5.5); ax_ba.set_ylim(0.0, 4.6)
            
        elif tipo_b in ["Ca(OH)2", "Ca(OH)2_dil"]: # 5 & 9. Chaux éteinte et Eau de chaux
            p_ca = np.array([4.0, 2.5])
            p_o1, p_h1 = np.array([2.6, 3.4]), np.array([1.4, 4.1])
            p_o2, p_h2 = np.array([5.4, 1.6]), np.array([6.6, 0.9])
            bond_b(p_ca, p_o1); bond_b(p_o1, p_h1); bond_b(p_ca, p_o2); bond_b(p_o2, p_h2)
            atom_b(p_ca, 'Ca')
            atom_b(p_o1, 'O', mobile=True); atom_b(p_h1, 'H', mobile=True)
            atom_b(p_o2, 'O', mobile=True); atom_b(p_h2, 'H', mobile=True)
            ax_ba.set_xlim(0.8, 7.2); ax_ba.set_ylim(0.4, 4.8)
            
        elif tipo_b == "Mg(OH)2": # 6. Médicament anti-acide
            p_mg = np.array([4.0, 2.5])
            p_o1, p_h1 = np.array([2.6, 2.5]), np.array([1.3, 2.5])
            p_o2, p_h2 = np.array([5.4, 2.5]), np.array([6.7, 2.5])
            bond_b(p_mg, p_o1); bond_b(p_o1, p_h1); bond_b(p_mg, p_o2); bond_b(p_o2, p_h2)
            atom_b(p_mg, 'Mg')
            atom_b(p_o1, 'O', mobile=True); atom_b(p_h1, 'H', mobile=True)
            atom_b(p_o2, 'O', mobile=True); atom_b(p_h2, 'H', mobile=True)
            ax_ba.set_xlim(0.5, 7.5); ax_ba.set_ylim(1.0, 4.0)
            
        elif tipo_b == "K2CO3": # 10. Cendres de bois (Carbonate de potassium)
            p_c = np.array([4.0, 2.5])
            p_o1, p_o2, p_o3 = np.array([4.0, 3.9]), np.array([2.8, 1.6]), np.array([5.2, 1.6])
            p_k1, p_k2 = np.array([1.4, 1.6]), np.array([6.6, 1.6])
            bond_b(p_c, p_o1, double=True); bond_b(p_c, p_o2); bond_b(p_c, p_o3); bond_b(p_o2, p_k1); bond_b(p_o3, p_k2)
            atom_b(p_c, 'C'); atom_b(o1, 'O'); atom_b(o2, 'O'); atom_b(o3, 'O'); atom_b(p_k1, 'K'); atom_b(p_k2, 'K')
            ax_ba.set_xlim(0.8, 7.2); ax_ba.set_ylim(0.8, 4.6)
            
        elif tipo_b == "RCOONa": # 8. Savon de Marseille (Oléate de sodium structure vraie simplifiée)
            p_r, p_c, p_o1, p_o2, p_na = np.array([1.6, 2.5]), np.array([3.1, 2.5]), np.array([3.9, 3.7]), np.array([3.9, 1.3]), np.array([5.4, 1.3])
            bond_b(p_r, p_c); bond_b(p_c, p_o1, double=True); bond_b(p_c, p_o2); bond_b(p_o2, p_na)
            atom_b(p_r, 'C'); atom_b(p_c, 'C'); atom_b(p_o1, 'O'); atom_b(p_o2, 'O'); atom_b(p_na, 'Na')
            ax_ba.text(1.6, 1.8, "R-Alkyl", fontsize=8, style="italic", ha="center")
            ax_ba.set_xlim(0.8, 6.2); ax_ba.set_ylim(0.5, 4.5)
            
        else: # 7. Eau de mer (Ions libres entourés de molécules d'eau symbolisées)
            p_na, p_cl = np.array([2.5, 2.5]), np.array([4.8, 2.5])
            atom_b(p_na, 'Na'); atom_b(p_cl, 'Cl')
            ax_ba.text(3.6, 3.2, "Solution saline", fontsize=9, style="italic", ha="center")
            ax_ba.set_xlim(1.2, 6.2); ax_ba.set_ylim(1.5, 3.8)

        ax_ba.axis("off")
        st.pyplot(fig_ba)
            # --- SECTION 3 : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 4 ---

    if "suite_verrouille_tab4_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab4_ph = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_ph

    # Affichage du module de questions spécifique aux produits basiques
    afficher_atelier_produits_basiques(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les produits basiques.",
        key="check_certif_ph4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_ph_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_ph_aleatoire:
                    saisie = st.session_state.get(f"ph_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0
                        
            score_t4 = 0.0
            if "champs_ph4_clean" in st.session_state:
                for ligne in st.session_state.champs_ph4_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph4_clean", "Choisir...") == attendu: 
                        score_t4 += 1.0
                        
            st.session_state.score_suite4_ph_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_ph_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_ph = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 4 ---
    if st.session_state.get("suite_verrouille_tab4_ph", False):
        scr1_t4 = st.session_state.get("score_suite4_ph_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_ph_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_ph", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        # Récupération sécurisée de l'identité de l'élève
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        st.success(f"ATELIER PRODUITS BASIQUES SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")
        
        html_export_ph4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Produits Basiques - {n_eleve}</title>
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
                <p>Atelier 4 : Étude des produits basiques du quotidien, formules, ions hydroxyde et histoire</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
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

        if "ordre_quiz_tab4_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ph4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_ph4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph4_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_ph4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ph4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph4 = preparer_nom_fichier("Rapport_Produits_Basiques").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_ph4,
            file_name=nom_fichier_html_ph4,
            mime="text/html",
            use_container_width=True
        )


with tab5:
    st.header("Les dosages ph-métriques")
    
    # --- FOCUS HISTORIQUE : L'INVENTION DU TITRAGE ---
    st.subheader("Histoire des Sciences : La naissance de la volumétrie")
    st.write(
        "L'opération de dosage, ou titrage, a été conceptualisée à la fin du dix-huitième siècle "
        "par des chimistes industriels français, notamment par Louis-Joseph Gay-Lussac. "
        "Cherchant un moyen de mesurer précisément la pureté des produits chimiques vendus dans le commerce, "
        "il a inventé la burette graduée en verre. À cette époque, le changement de milieu était repéré "
        "uniquement grâce à des indicateurs colorés visuels, une méthode appelée titrage colorimétrique.\n\n"
        "Avec l'avènement de l'électronique au vingtième siècle, les scientifiques ont remplacé l'œil humain "
        "par la sonde d'un pH-mètre. En versant une base goutte à goutte dans un acide et en mesurant le pH "
        "à chaque ajout, ils ont découvert qu'il existait une brusque variation de la mesure, appelée "
        "**saut de pH**, permettant de déterminer la concentration inconnue avec une précision chirurgicale."
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET COURBE DE TITRAGE ---
    st.subheader("La neutralisation acido-basique")
    st.write(
        "Doser une solution consiste à déterminer sa concentration inconnue en la faisant réagir avec "
        "une autre solution dont on connaît parfaitement la concentration. Lors du dosage d'un acide fort "
        "par une base forte (par exemple, l'acide chlorhydrique mélangé avec de la soude) :\n\n"
        "* **La réaction chimique :** Les ions oxonium H₃O⁺ responsables de l'acidité s'associent avec "
        "les ions hydroxyde OH⁻ responsables de la basicité pour former des molécules d'eau pure (H₂O). "
        "La formule s'écrit : **H₃O⁺ + OH⁻ -> 2 H₂O**.\n"
        "* **L'équivalence :** C'est l'instant précis où tout l'acide initial a été détruit par la base versée. "
        "À cet endroit exact, la solution devient parfaitement neutre. Pour un mélange d'acide fort et de base forte, "
        "le pH à l'équivalence est **rigoureusement égal à 7** à 25°C."
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
            "aucun survivant : la neutralité absolue règne (pH = 7). Si l'on continue de verser la base, celle-ci devient "
            "majoritaire et le pH s'envole vers 14."
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
        ax_curve.plot(v_base, ph_sim, color="#7c3aed", linewidth=3, label="Courbe pH-metrique")
        
        # Point d'équivalence E
        ax_curve.plot(10, 7, marker="o", color="#ef4444", markersize=8, label="Equivalence E (pH=7)")
        ax_curve.axhline(7, color="#cbd5e1", linestyle="--")
        ax_curve.axvline(10, color="#cbd5e1", linestyle="--")
        
        ax_curve.set_xlabel("Volume de base verse Vb (mL)", fontsize=9)
        ax_curve.set_ylabel("pH de la solution", fontsize=9)
        ax_curve.set_title("Evolution du pH lors du dosage", fontsize=10, weight="bold")
        ax_curve.set_xlim(0, 20)
        ax_curve.set_ylim(0, 14)
        ax_curve.legend(fontsize=8, loc="lower right")
        ax_curve.grid(True, color="#f1f5f9")
        st.pyplot(fig_curve)
            
    st.divider()

    # --- SECTION 2 : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab5_ph = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_ph

    # Affichage du module de questions spécifique aux dosages
    afficher_atelier_dosages_ph(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Les dosages ph-métriques.",
        key="check_certif_ph5_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_ph_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_ph_aleatoire:
                    saisie = st.session_state.get(f"ph_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q5 += 1.0

            score_t5 = 0.0
            if "champs_ph5_clean" in st.session_state:
                for ligne in st.session_state.champs_ph5_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph5_clean", "Choisir...") == attendu: score_t5 += 1.0

            st.session_state.score_suite5_ph_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_ph_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_ph = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 5 ---
    if st.session_state.get("suite_verrouille_tab5_ph", False):
        scr1_t5 = st.session_state.get("score_suite5_ph_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_ph_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_ph", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        st.success(f"ATELIER DOSAGES PH SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_ph5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dosages pH - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 5 : Les dosages ph-métriques, saut de pH, équivalence et neutralisation</p>
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

        if "ordre_quiz_tab5_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

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

        if "champs_ph5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph5_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph5_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_ph5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ph5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph5 = preparer_nom_fichier("Rapport_Dosages_pH").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_ph5,
            file_name=nom_fichier_html_ph5,
            mime="text/html",
            use_container_width=True
        )



