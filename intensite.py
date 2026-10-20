
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



