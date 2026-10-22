
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

    # --- SECTION 2 : TABLEAU RECONSTRUIT ET NETTOYÉ ---
    st.subheader("Inventaire moléculaire : 10 produits acides de la vie courante")
    st.write(
        "Voici le tableau de référence listant 10 solutions acides courantes."
    )

    dico_acides = {
        "Jus de citron (Acide citrique)": {"formula": "C6H8O7", "formula_visuelle": "C<sub>6</sub>H<sub>8</sub>O<sub>7</sub>", "ph": "2.3", "desc": "Acide organique présent dans les agrumes, utilisé en alimentation."},
        "Vinaigre (Acide acétique)": {"formula": "C2H4O2", "formula_visuelle": "C<sub>2</sub>H<sub>4</sub>O<sub>2</sub>", "ph": "2.9", "desc": "Issu de la fermentation du vin, utilisé pour la cuisine et le nettoyage."},
        "Esprit de sel (Acide chlorhydrique)": {"formula": "HCl", "formula_visuelle": "HCl", "ph": "1.0", "desc": "Acide fort industriel utilisé pour détartrer et décaper les toilettes."},
        "Liquide de batterie (Acide sulfurique)": {"formula": "H2SO4", "formula_visuelle": "H<sub>2</sub>SO<sub>4</sub>", "ph": "0.5", "desc": "Acide fort industriel ultra-corrosif chargé dans les batteries de voiture."},
        "Soda au cola (Acide phosphorique)": {"formula": "H3PO4", "formula_visuelle": "H<sub>3</sub>PO<sub>4</sub>", "ph": "2.5", "desc": "Additif alimentaire utilisé pour donner le goût acide aux boissons gazeuses."},
        "Jus de pomme (Acide malique)": {"formula": "C4H6O5", "formula_visuelle": "C<sub>4</sub>H<sub>6</sub>O<sub>5</sub>", "ph": "3.5", "desc": "Acide organique naturel présent dans la majorité des fruits à pépins."},
        "Lait tourné (Acide lactique)": {"formula": "C3H6O3", "formula_visuelle": "C<sub>3</sub>H<sub>6</sub>O<sub>3</sub>", "ph": "4.4", "desc": "Produit par les bactéries lors de la fermentation du lactose dans le lait."},
        "Aspirine (Acide acétylsalicylique)": {"formula": "C9H8O4", "formula_visuelle": "C<sub>9</sub>H<sub>8</sub>O<sub>4</sub>", "ph": "3.5", "desc": "Médicament anti-inflammatoire et analgésique très répandu."},
        "Vitamine C (Acide ascorbique)": {"formula": "C6H8O6", "formula_visuelle": "C<sub>6</sub>H<sub>8</sub>O<sub>6</sub>", "ph": "3.0", "desc": "Antioxydant essentiel présent dans les fruits."},
        "Limonade (Acide carbonique)": {"formula": "H2CO3", "formula_visuelle": "H<sub>2</sub>CO<sub>3</sub>", "ph": "4.0", "desc": "Formé par la dissolution du dioxyde de carbone gazeux dans l'eau."}
    }

    # Initialisation de la chaîne HTML propre pour éviter de cumuler les anciens bugs
    html_table = """
    <table style="width:100%; border-collapse: collapse; text-align: left; font-family: Arial, sans-serif; font-size: 14px;">
        <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1;">
            <th style="padding: 12px; font-weight: bold; color: #1e293b;">Nom du produit (Acide associé)</th>
            <th style="padding: 12px; font-weight: bold; color: #1e293b;">Formule brute</th>
            <th style="padding: 12px; font-weight: bold; color: #1e293b;">pH approximatif</th>
            <th style="padding: 12px; font-weight: bold; color: #1e293b;">Description et usage</th>
        </tr>
    """

    for nom, infos in dico_acides.items():
        # Utilisation de doubles accolades {{ }} pour le style à l'intérieur d'une f-string Python
        html_table += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 12px; font-weight: bold; color: #334155;">{nom}</td>
            <td style="padding: 12px; font-family: monospace; font-size: 15px; color: #0f172a;">{infos["formula_visuelle"]}</td>
            <td style="padding: 12px; color: #334155;">{infos["ph"]}</td>
            <td style="padding: 12px; color: #475569;">{infos["desc"]}</td>
        </tr>
        """
        
    html_table += "</table><br>"

    # Rendu unique sur l'interface Streamlit avec HTML autorisé
    st.markdown(html_table, unsafe_allow_html=True)

    # Sélecteur pour le focus moléculaire individuel
    choix_acide_visuel = st.selectbox("Choisir un produit pour dessiner son architecture moléculaire :", options=list(dico_acides.keys()), key="sel_acide_tab3")
    
    col_leg_act, col_graph_act = st.columns([0.4, 0.6])
    with col_leg_act:
        st.markdown("**Légendes des sphères de couleur :**")
        st.write("* Blanc : Hydrogène (H)")
        st.write("* Noir : Carbone (C)")
        st.write("* Rouge : Oxygène (O)")
        st.write("* Vert : Chlore (Cl)")
        st.write("* Jaune : Soufre (S)")
        st.markdown(f"**Produit :** {choix_acide_visuel}")
        # Rendu propre également pour la formule de la légende
        st.markdown(f"**Formule brute :** {dico_acides[choix_acide_visuel]['formula_visuelle']}", unsafe_allow_html=True)
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




















