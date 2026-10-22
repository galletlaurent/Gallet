
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

def afficher_atelier_conductimetrie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Dosage conductimétrique) sur deux colonnes."""
    import random

    questions_dos3_sources = [
        {"id": "qcd1", "q": "Quelle grandeur physique mesure-t-on lors d'un titrage conductimétrique ?", "options": ["La conductance G ou la conductivité sigma", "L'absorbance de la lumière", "Le potentiel d'oxydoréduction"], "rep": "La conductance G ou la conductivité sigma"},
        {"id": "qcd2", "q": "Quel type de soluté est indispensable dans la solution pour pouvoir mener une mesure conductimétrique ?", "options": ["Des ions libres dissous", "Des molécules neutres comme le sucre", "Des gaz incolores"], "rep": "Des ions libres dissous"},
        {"id": "qcd3", "q": "Comment se repère visuellement l'équivalence sur le graphique d'un dosage conductimétrique ?", "options": ["Par une rupture de pente (intersection de deux droites)", "Par un maximum en forme de cloche", "Par un palier parfaitement plat"], "rep": "Par une rupture de pente (intersection de deux droites)"},
        {"id": "qcd4", "q": "Pourquoi ajoute-t-on un grand volume d'eau distillée dans le bécher au début du dosage ?", "options": ["Pour négliger la variation de volume lors des ajouts de la burette", "Pour augmenter la concentration des ions", "Pour modifier la température du milieu"], "rep": "Pour négliger la variation de volume lors des ajouts de la burette"},
        {"id": "qcd5", "q": "Quelle est l'unité officielle de mesure de la conductivité d'une solution ?", "options": ["Siemens par mètre (S/m)", "Ohm par centimètre", "Volt par mole"], "rep": "Siemens par mètre (S/m)"},
        {"id": "qcd6", "q": "Comment qualifie-t-on l'appareil électronique muni d'une cellule de mesure que l'on plonge dans le bécher ?", "options": ["Un conductimètre", "Un spectrophotomètre", "Un pH-mètre"], "rep": "Un conductimètre"},
        {"id": "qcd7", "q": "Lors du titrage des ions chlorure par les ions argent, que fait la conductivité avant l'équivalence ?", "options": ["Elle diminue car les ions argent font précipiter les chlorures", "Elle s'envole vers l'infini", "Elle reste rigoureusement fixe"], "rep": "Elle diminue car les ions argent font précipiter les chlorures"},
        {"id": "qcd8", "q": "Que fait la courbe graphique après l'équivalence si l'on continue de verser le réactif titrant ionique ?", "options": ["Elle réaugmente à cause de l'accumulation des ions en excès", "Elle tombe brutalement à zéro", "Elle oscille de façon sinusoïdale"], "rep": "Elle réaugmente à cause de l'accumulation des ions en excès"},
        {"id": "qcd9", "q": "Quel composant de la cellule de mesure conductimétrique est extrêmement sensible aux rayures ?", "options": ["Les plaques de platine platiné", "Le barreau aimanté", "Le robinet de la burette"], "rep": "Les plaques de platine platiné"},
        {"id": "qcd10", "q": "Quelle loi stipule que la conductivité d'une solution diluée est proportionnelle aux concentrations des ions ?", "options": ["La loi de Kohlrausch", "La loi de Beer-Lambert", "La loi de Sorensen"], "rep": "La loi de Kohlrausch"}
    ]

    if "ordre_quiz_tab3_dos_aleatoire" not in st.session_state:
        random.shuffle(questions_dos3_sources)
        st.session_state.ordre_quiz_tab3_dos_aleatoire = questions_dos3_sources

    if "champs_dos3_clean" not in st.session_state:
        st.session_state.champs_dos3_clean = [
            ("1. Le titrage conductimétrique mesure la capacité d'une solution à conduire le ..........", ["Choisir...", "courant", "pH"], "courant", "dos3_t1"),
            ("2. Cette technique analytique s'applique uniquement si le milieu contient des ..........", ["Choisir...", "ions", "solvants"], "ions", "dos3_t2"),
            ("3. L'appareil de mesure électronique immergé s'appelle un ..........", ["Choisir...", "conductimètre", "spectrophotomètre"], "conductimètre", "dos3_t3"),
            ("4. L'unité de mesure de la conductivité de la solution est le S par ..........", ["Choisir...", "mètre", "litre"], "mètre", "dos3_t4"),
            ("5. La loi de .......... relie la conductivité à la concentration des ions.", ["Choisir...", "Kohlrausch", "Beer-Lambert"], "Kohlrausch", "dos3_t5"),
            ("6. Ajouter un grand volume d'eau au départ évite l'effet de ..........", ["Choisir...", "dilution", "précipitation"], "dilution", "dos3_t6"),
            ("7. Sur le graphique tracé, l'équivalence correspond à une .......... de pente.", ["Choisir...", "rupture", "stagnation"], "rupture", "dos3_t7"),
            ("8. Avant l'équivalence, la courbe baisse si les ions conducteurs sont ..........", ["Choisir...", "consommés", "accumulés"], "consommés", "dos3_t8"),
            ("9. Après l'équivalence, la courbe remonte car les ions versés sont en ..........", ["Choisir...", "excès", "défaut"], "excès", "dos3_t7"),
            ("10. La cellule de mesure comporte deux plaques parallèles de ..........", ["Choisir...", "platine", "cuivre"], "platine", "dos3_t10")
        ]

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
