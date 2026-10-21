
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application puissance et énergie électrique",
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
st.title("Application puissance et énergie électrique")
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
    "Définition de la puissance électrique",
    "Appareil de mesure de la puissance électrique",
    "Définition de l'énergie électrique",
    "Appareil de mesure de l'énergie électrique",
    "Energie consommée par une maison",
    "Production d'énergie"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]


def afficher_atelier_production_energie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (Production énergie) sur deux colonnes."""
    import random

    # 1. Base de données des questions du Quiz
    questions_prod_sources = [
        {"id": "qpr1", "q": "Quel inconvénient majeur possède la production thermique fossile du passé ?", "options": ["Elle rejette de grandes quantités de CO2", "Elle est intermittente", "Elle produit des déchets radioactifs"], "rep": "Elle rejette de grandes quantités de CO2"},
        {"id": "qpr2", "q": "Sur quel principe physique repose le fonctionnement des centrales nucléaires actuelles ?", "options": ["La fission nucléaire d'atomes d'uranium", "La fusion d'isotopes d'hydrogène", "La combustion de gaz naturel"], "rep": "La fission nucléaire d'atomes d'uranium"},
        {"id": "qpr3", "q": "Quelle contrainte technique caractérise l'énergie éolienne et solaire ?", "options": ["L'intermittence liée aux conditions météo", "L'émission massive de fumées toxiques", "La surproduction permanente de nuit"], "rep": "L'intermittence liée aux conditions météo"},
        {"id": "qpr4", "q": "Quelle technologie future propre cherche à reproduire la réaction physique du Soleil ?", "options": ["La fusion nucléaire (projet ITER)", "La fission de l'uranium 235", "La biomasse par gazéification"], "rep": "La fusion nucléaire (projet ITER)"},
        {"id": "qpr5", "q": "Quel composant machine final, présent dans presque toutes les centrales, génère la tension ?", "options": ["L'alternateur", "La turbine", "Le transformateur"], "rep": "L'alternateur"},
        {"id": "qpr6", "q": "Les barrages hydroélectriques exploitent l'énergie cinétique issue du flux :", "options": ["De l'eau", "Du vent", "De la vapeur"], "rep": "De l'eau"},
        {"id": "qpr7", "q": "Quel gaz décarboné est étudié comme solution future pour stocker l'électricité ?", "options": ["L'hydrogène vert", "Le dioxyde de carbone", "Le méthane fossile"], "rep": "L'hydrogène vert"},
        {"id": "qpr8", "q": "L'ensemble des différentes sources exploitées à l'échelle d'un pays forme :", "options": ["Le mix énergétique", "Le circuit en dérivation", "L'index de consommation"], "rep": "Le mix énergétique"},
        {"id": "qpr9", "q": "Quelle source d'énergie d'origine thermique utilise des matières organiques biodégradables ?", "options": ["La biomasse", "Le pétrole brut", "La géothermie"], "rep": "La biomasse"},
        {"id": "qpr10", "q": "Pour maintenir le réseau stable, la production totale disponible doit être :", "options": ["Strictement égale à la demande en temps réel", "Toujours dix fois supérieure à la cible", "Nulle pendant les heures creuses"], "rep": "Strictement égale à la demande en temps réel"}
    ]

    if "ordre_quiz_tab6_prod_aleatoire" not in st.session_state:
        random.shuffle(questions_prod_sources)
        st.session_state.ordre_quiz_tab6_prod_aleatoire = questions_prod_sources

    # 2. INITIALISATION ET DÉCLARATION FORCEE DE LA LISTE DE SYNTHÈSE CONTRE LES KEYERROR
    if "champs_prod_tension_clean" not in st.session_state:
        st.session_state.champs_prod_tension_clean = [
            ("1. Brûler du charbon ou du gaz libère du gaz .......... polluant.", ["Choisir...", "carbonique", "hydrogène"], "carbonique", "prod_t1"),
            ("2. La technologie actuelle des centrales nucléaires exploite la ..........", ["Choisir...", "fission", "fusion"], "fission", "prod_t2"),
            ("3. Les filières propres qui exploitent les flux de la Terre sont ..........", ["Choisir...", "renouvelables", "fossiles"], "renouvelables", "prod_t3"),
            ("4. Le vent et le soleil imposent une gestion de l'..........", ["Choisir...", "intermittence", "continuité"], "intermittence", "prod_t4"),
            ("5. La machine ITER étudie la .......... nucléaire du futur.", ["Choisir...", "fusion", "fission"], "fusion", "prod_t5"),
            ("6. Pour créer l'électricité, la turbine entraîne un ..........", ["Choisir...", "alternateur", "moteur"], "alternateur", "prod_t6"),
            ("7. L'hydrogène vert servira de vecteur de .......... d'énergie.", ["Choisir...", "stockage", "perte"], "stockage", "prod_t7"),
            ("8. L'équilibre du réseau exige d'ajuster la production à la ..........", ["Choisir...", "demande", "tension"], "demande", "prod_t8"),
            ("9. La répartition des filières de production forme le .......... national.", ["Choisir...", "mix", "nœud"], "mix", "prod_t9"),
            ("10. Diversifier les méthodes sécurise l'approvisionnement ..........", ["Choisir...", "électrique", "thermique"], "électrique", "prod_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_prod_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"prod_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_prod_tension_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_prod_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_consommation_maison(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Consommation maison) sur deux colonnes."""
    import random

    questions_mai_sources = [
        {"id": "qm1", "q": "Quelle unité pratique utilise-t-on pour facturer la consommation d'électricité ?", "options": ["Le kilowattheure (kWh)", "Le watt-seconde (Ws)", "Le mégajoule (MJ)"], "rep": "Le kilowattheure (kWh)"},
        {"id": "qm2", "q": "Quels types d'appareils consomment généralement le plus d'énergie dans un logement ?", "options": ["Les appareils thermiques de chauffage et cuisson", "Les ampoules d'éclairage moderne", "Les ordinateurs et chargeurs"], "rep": "Les appareils thermiques de chauffage et cuisson"},
        {"id": "qm3", "q": "Pour calculer l'énergie totale consommée par une maison au cours d'une journée, on doit :", "options": ["Additionner l'énergie consommée par chaque équipement", "Multiplier la tension globale par le temps", "Prendre uniquement la valeur de l'appareil le plus puissant"], "rep": "Additionner l'énergie consommée par chaque équipement"},
        {"id": "qm4", "q": "Comment convertit-on une puissance en Watts (W) vers des Kilowatts (kW) ?", "options": ["On divise la valeur par 1 000", "On multiplie la valeur par 1 000", "On divise la valeur par 3 600"], "rep": "On divise la valeur par 1 000"},
        {"id": "qm5", "q": "Si un radiateur de 2 000 W fonctionne pendant 3 heures, quelle est son énergie consommée ?", "options": ["6 kWh", "600 Wh", "0.66 kWh"], "rep": "6 kWh"},
        {"id": "qm6", "q": "Quelle formule permet d'établir le montant financier d'une facture d'électricité ?", "options": ["Coût = Énergie (kWh) x Prix du kWh", "Coût = Puissance (W) x Prix du kWh", "Coût = Tension (V) x Temps (h)"], "rep": "Coût = Énergie (kWh) x Prix du kWh"},
        {"id": "qm7", "q": "Laquelle de ces actions est considérée comme un éco-geste efficace au foyer ?", "options": ["Éteindre complètement les appareils en veille", "Laisser la lumière allumée dans les pièces vides", "Régler le four à température maximale continue"], "rep": "Éteindre complètement les appareils en veille"},
        {"id": "qm8", "q": "Sur l'étiquette énergie européenne, quelle lettre désigne l'appareil le plus économe ?", "options": ["La lettre A", "La lettre G", "La lettre X"], "rep": "La lettre A"},
        {"id": "qm9", "q": "Un téléviseur de 100 W allumé pendant 5 heures consomme une énergie de :", "options": ["0,5 kWh", "500 kWh", "50 Wh"], "rep": "0,5 kWh"},
        {"id": "qm10", "q": "Que se passe-t-il si trop d'appareils de forte puissance fonctionnent en même temps ?", "options": ["Le disjoncteur principal coupe le courant par surcharge", "Le prix du kWh diminue automatiquement", "La tension du secteur augmente à 400V"], "rep": "Le disjoncteur principal coupe le courant par surcharge"}
    ]

    if "ordre_quiz_tab5_mai_aleatoire" not in st.session_state:
        random.shuffle(questions_mai_sources)
        st.session_state.ordre_quiz_tab5_mai_aleatoire = questions_mai_sources

    # Liste de synthèse structurée à 4 éléments
    if "champs_mai_tension_clean" not in st.session_state:
        st.session_state.champs_mai_tension_clean = [
            ("1. Le coût financier s'obtient en multipliant l'énergie par le ..........", ["Choisir...", "prix", "calibre"], "prix", "mai_t1"),
            ("2. Pour établir le total, on additionne les énergies de chaque ..........", ["Choisir...", "appareil", "nœud"], "appareil", "mai_t2"),
            ("3. Les équipements électriques qui chauffent ont une puissance très ..........", ["Choisir...", "forte", "basse"], "forte", "mai_t3"),
            ("4. Diviser les Watts par mille permet d'obtenir les ..........", ["Choisir...", "kilowatts", "mégawatts"], "kilowatts", "mai_t4"),
            ("5. La consommation d'une habitation se calcule sur une base ..........", ["Choisir...", "temporelle", "statique"], "temporelle", "mai_t5"),
            ("6. Le compteur enregistre les index pour dresser la ..........", ["Choisir...", "facture", "tension"], "facture", "mai_t6"),
            ("7. Remplacer les anciennes ampoules par des .......... réduit P.", ["Choisir...", "leds", "résistances"], "leds", "mai_t7"),
            ("8. L'étiquette énergie guide l'éco-citoyen vers le meilleur ..........", ["Choisir...", "rendement", "ampèremètre"], "rendement", "mai_t8"),
            ("9. Traquer les veilles évite une dépense énergétique ..........", ["Choisir...", "inutile", "nominale"], "inutile", "mai_t9"),
            ("10. Maîtriser sa consommation diminue l'impact sur l'..........", ["Choisir...", "environnement", "générateur"], "environnement", "mai_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_mai_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"mai_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_mai_tension_clean:
            # AJOUTEZ BIEN LES INDEX [0] ET [1] ICI :
            enonce = ligne[0]  # Récupère la phrase de texte propre
            choix = ligne[1]   # Récupère la liste des options du menu déroulant
            cle = ligne[-1]    # Récupère la clé unique de session
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_mai_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_appareil_energie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Appareil de mesure de l'énergie) sur deux colonnes."""
    import random

    questions_cpt_sources = [
        {"id": "qc1", "q": "Quel appareil mesure l'énergie totale cumulée consommée par une habitation ?", "options": ["Le compteur électrique", "Le wattmètre", "L'ohmmètre"], "rep": "Le compteur électrique"},
        {"id": "qc2", "q": "Quelle est l'unité de mesure affichée sur l'écran du compteur électrique ?", "options": ["Le kilowattheure (kWh)", "Le volt (V)", "Le joule (J)"], "rep": "Le kilowattheure (kWh)"},
        {"id": "qc3", "q": "Sur un ancien compteur mécanique, quel élément tourne pour enregistrer la consommation ?", "options": ["Un disque métallique horizontal", "Une aiguille magnétique", "Un rouleau numéroté"], "rep": "Un disque métallique horizontal"},
        {"id": "qc4", "q": "Que représente la constante C indiquée sur un compteur mécanique ?", "options": ["L'énergie consommée par tour de disque", "La puissance maximale de l'installation", "La tension du secteur domestique"], "rep": "L'énergie consommée par tour de disque"},
        {"id": "qc5", "q": "Si un compteur a une constante C = 4 Wh/tr, quelle énergie correspond à 100 tours ?", "options": ["400 Wh", "400 kWh", "25 Wh"], "rep": "400 Wh"},
        {"id": "qc6", "q": "Comment s'appelle le compteur communicant intelligent installé partout en France ?", "options": ["Linky", "Gazpar", "Wattmètre"], "rep": "Linky"},
        {"id": "qc7", "q": "Quel est le principal avantage pratique du compteur Linky pour le fournisseur ?", "options": ["Le relevé automatique de l'index à distance", "L'économie automatique de 50% d'énergie", "La coupure des surtensions de foudre"], "rep": "Le relevé automatique de l'index à distance"},
        {"id": "qc8", "q": "Où est généralement placé le compteur électrique principal d'un logement ?", "options": ["Dans l'armoire technique d'entrée ou en limite de propriété", "À côté du ballon d'eau chaude", "Dans la cuisine près des plaques"], "rep": "Dans l'armoire technique d'entrée ou en limite de propriété"},
        {"id": "qc9", "q": "L'index de consommation lu sur le compteur permet au fournisseur d'établir :", "options": ["La facture d'électricité", "Le bilan de tension", "Le diagnostic thermique"], "rep": "La facture d'électricité"},
        {"id": "qc10", "q": "Si aucun appareil de la maison n'est en marche, le disque du compteur mécanique :", "options": ["Reste immobile", "Tourne très lentement à l'envers", "Continue de tourner à vitesse normale"], "rep": "Reste immobile"}
    ]

    if "ordre_quiz_tab4_cpt_aleatoire" not in st.session_state:
        random.shuffle(questions_cpt_sources)
        st.session_state.ordre_quiz_tab4_cpt_aleatoire = questions_cpt_sources

    # Liste de synthèse structurée à 4 éléments
    if "champs_cpt_tension_clean" not in st.session_state:
        st.session_state.champs_cpt_tension_clean = [
            ("1. Le .......... enregistre l'énergie cumulée de toute la maison.", ["Choisir...", "compteur", "wattmètre"], "compteur", "cpt_t1"),
            ("2. Les chiffres affichés indiquent une valeur en ..........", ["Choisir...", "kilowattheures", "joules"], "kilowattheures", "cpt_t2"),
            ("3. Les anciens modèles utilisaient un .......... métallique rotatif.", ["Choisir...", "disque", "rotor"], "disque", "cpt_t3"),
            ("4. La valeur d'énergie par rotation est la .......... C du compteur.", ["Choisir...", "constante", "puissance"], "constante", "cpt_t4"),
            ("5. La formule d'énergie mécanique associée s'écrit E = ..........", ["Choisir...", "n x C", "n / C"], "n x C", "cpt_t5"),
            ("6. Le compteur jaune intelligent de nouvelle génération est le ..........", ["Choisir...", "Linky", "Stator"], "Linky", "cpt_t6"),
            ("7. Linky utilise la transmission numérique pour envoyer l'..........", ["Choisir...", "index", "calibre"], "index", "cpt_t7"),
            ("8. Plus la consommation instantanée est forte, plus le témoin ..........", ["Choisir...", "clignote vite", "s'éteint"], "clignote vite", "cpt_t8"),
            ("9. Cet appareil s'installe en amont du panneau de ..........", ["Choisir...", "distribution", "production"], "distribution", "cpt_t9"),
            ("10. Suivre son compteur permet de mieux maîtriser ses ..........", ["Choisir...", "dépenses", "tensions"], "dépenses", "cpt_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_cpt_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"cpt_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse sur l'Appareil (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_cpt_tension_clean:
            # AJOUTEZ BIEN LES INDEX [0] ET [1] ICI :
            enonce = ligne[0]  # Récupère la phrase de texte propre
            choix = ligne[1]   # Récupère la liste des options du menu déroulant
            cle = ligne[-1]    # Récupère la clé unique de session
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_cpt_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_definition_energie(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Définition de l'énergie) sur deux colonnes."""
    import random

    questions_ene_sources = [
        {"id": "qe1", "q": "Quelle est l'unité internationale légale de l'énergie ?", "options": ["Le joule", "Le wattheure", "Le watt"], "rep": "Le joule"},
        {"id": "qe2", "q": "Quelle formule relie l'énergie, la puissance et le temps ?", "options": ["E = P x t", "E = P / t", "E = U x I"], "rep": "E = P x t"},
        {"id": "qe3", "q": "Quelle unité d'énergie est principalement utilisée sur les factures d'électricité ?", "options": ["Le kilowattheure (kWh)", "Le joule (J)", "Le mégawatt (MW)"], "rep": "Le kilowattheure (kWh)"},
        {"id": "qe4", "q": "Combien de Joules contient exactement un Wattheure (1 Wh) ?", "options": ["3 600 J", "60 J", "1 000 J"], "rep": "3 600 J"},
        {"id": "qe5", "q": "Un appareil de 500W fonctionne pendant 2 heures. Son énergie consommée vaut :", "options": ["1 000 Wh", "250 Wh", "1 000 J"], "rep": "1 000 Wh"},
        {"id": "qe6", "q": "Pour obtenir une énergie en Joules avec la formule, le temps t doit être en :", "options": ["Secondes", "Heures", "Minutes"], "rep": "Secondes"},
        {"id": "qe7", "q": "Comment exprime-t-on le temps de fonctionnement t en fonction de E et de P ?", "options": ["t = E / P", "t = P / E", "t = E x P"], "rep": "t = E / P"},
        {"id": "qe8", "q": "Si on laisse un appareil allumé deux fois plus longtemps, l'énergie consommée :", "options": ["Est doublée", "Reste la même", "Est divisée par deux"], "rep": "Est doublée"},
        {"id": "qe9", "q": "Un kilowattheure (1 kWh) est équivalent à combien de Joules ?", "options": ["3 600 000 J", "3 600 J", "1 000 J"], "rep": "3 600 000 J"},
        {"id": "qe10", "q": "Quel scientifique a donné son nom à l'unité internationale de l'énergie ?", "options": ["James Prescott Joule", "James Watt", "Marie Curie"], "rep": "James Prescott Joule"}
    ]

    if "ordre_quiz_tab3_ene_aleatoire" not in st.session_state:
        random.shuffle(questions_ene_sources)
        st.session_state.ordre_quiz_tab3_ene_aleatoire = questions_ene_sources

    # Liste de synthèse structurée à 4 éléments
    if "champs_ene_tension_clean" not in st.session_state:
        st.session_state.champs_ene_tension_clean = [
            ("1. L'énergie accumulée dépend de la puissance et du ..........", ["Choisir...", "temps", "calibre"], "temps", "ene_t1"),
            ("2. L'unité légale du système international est le ..........", ["Choisir...", "joule", "wattheure"], "joule", "ene_t2"),
            ("3. La relation s'exprime par l'égalité mathématique E = ..........", ["Choisir...", "P x t", "P / t"], "P x t", "ene_t3"),
            ("4. Pour calculer l'énergie en Joules, la durée doit être en ..........", ["Choisir...", "secondes", "heures"], "secondes", "ene_t4"),
            ("5. L'unité usuelle pratique pour mesurer les factures est le ..........", ["Choisir...", "wattheure", "joule"], "wattheure", "ene_t5"),
            ("6. Pour calculer l'énergie en Wh, la durée s'exprime en ..........", ["Choisir...", "heures", "secondes"], "heures", "ene_t6"),
            ("7. Un groupe de mille wattheures forme un ..........", ["Choisir...", "kilowattheure", "mégajoules"], "kilowattheure", "ene_t7"),
            ("8. Dans l'analogie, l'énergie représente le volume du ..........", ["Choisir...", "bassin", "jet"], "bassin", "ene_t8"),
            ("9. Un wattheure correspond à une quantité de trois mille six cents ..........", ["Choisir...", "joules", "watts"], "joules", "ene_t9"),
            ("10. Réduire le temps d'utilisation permet d'économiser l'..........", ["Choisir...", "énergie", "tension"], "énergie", "ene_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_ene_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ene_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ene_tension_clean:
            # INTERCEPTIONS INDISPENSABLES DES INDEX 0 ET 1 :
            enonce = ligne[0]  # Récupère la phrase de texte propre
            choix = ligne[1]   # Récupère les options de réponse du menu déroulant
            cle = ligne[-1]    # Récupère la clé de session unique
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ene_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_appareil_puissance(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Appareil de mesure) sur deux colonnes."""
    import random

    questions_wat_sources = [
        {"id": "qw1", "q": "Quel appareil utilise-t-on pour mesurer directement la puissance électrique ?", "options": ["Le wattmètre", "Le voltmètre", "L'ampèremètre"], "rep": "Le wattmètre"},
        {"id": "qw2", "q": "Combien de bornes de connexion possède au minimum un wattmètre de laboratoire ?", "options": ["2 bornes", "4 bornes", "3 bornes"], "rep": "4 bornes"},
        {"id": "qw3", "q": "Comment se branche la partie ampèremétrique interne d'un wattmètre ?", "options": ["En série dans le circuit", "En dérivation aux bornes du récepteur", "Peu importe la méthode"], "rep": "En série dans le circuit"},
        {"id": "qw4", "q": "Comment se branche la partie voltmétrique interne d'un wattmètre ?", "options": ["En dérivation aux bornes du récepteur", "En série dans le circuit", "En parallèle sur le générateur uniquement"], "rep": "En dérivation aux bornes du récepteur"},
        {"id": "qw5", "q": "Quel est l'intérêt d'un wattmètre de prise domestique ?", "options": ["Mesurer la consommation en direct sans modifier les fils", "Augmenter la puissance disponible", "Remplacer le disjoncteur"], "rep": "Mesurer la consommation en direct sans modifier les fils"},
        {"id": "qw6", "q": "Un wattmètre de prise affiche une puissance réactive nulle pour un dipôle purement :", "options": ["Résistif", "Inductif", "Capacitif"], "rep": "Résistif"},
        {"id": "qw7", "q": "Si on inverse les bornes du circuit tension d'un wattmètre analogique :", "options": ["L'aiguille dévie à l'envers", "L'appareil explose", "La valeur double"], "rep": "L'aiguille dévie à l'envers"},
        {"id": "qw8", "q": "Un wattmètre permet de détecter quels appareils domestiques ?", "options": ["Les appareils énergivores en veille", "Les fuites d'eau isolées", "La tension des piles usagées"], "rep": "Les appareils énergivores en veille"},
        {"id": "qw9", "q": "Le branchement correct combine simultanément les règles de l'ampèremètre et du :", "options": ["Voltmètre", "Ohmmètre", "Thermomètre"], "rep": "Voltmètre"},
        {"id": "qw10", "q": "Sur les réseaux triphasés industriels, la mesure impose d'utiliser :", "options": ["Plusieurs wattmètres", "Un simple voltmètre", "Un fil de terre"], "rep": "Plusieurs wattmètres"}
    ]

    if "ordre_quiz_tab2_wat_aleatoire" not in st.session_state:
        random.shuffle(questions_wat_sources)
        st.session_state.ordre_quiz_tab2_wat_aleatoire = questions_wat_sources

    # Liste de synthèse structurée à 4 éléments
    if "champs_wat_tension_clean" not in st.session_state:
        st.session_state.champs_wat_tension_clean = [
            ("1. Le .......... donne une lecture de la puissance sans calculs.", ["Choisir...", "wattmètre", "multimètre"], "wattmètre", "wat_t1"),
            ("2. Pour mesurer P, le boîtier doit analyser la tension et l'..........", ["Choisir...", "intensité", "résistance"], "intensité", "wat_t2"),
            ("3. Les quatre bornes du boîtier forment deux .......... de mesure.", ["Choisir...", "circuits", "nœuds"], "circuits", "wat_t3"),
            ("4. La ligne d'intensité s'insère obligatoirement en ..........", ["Choisir...", "série", "dérivation"], "série", "wat_t4"),
            ("5. Les bornes de tension se repiquent en .......... sur le dipôle.", ["Choisir...", "dérivation", "série"], "dérivation", "wat_t5"),
            ("6. Un mauvais câblage du circuit intensité peut créer un ..........", ["Choisir...", "court-circuit", "nœud"], "court-circuit", "wat_t6"),
            ("7. Le boîtier domestique se branche directement sur une ..........", ["Choisir...", "prise", "pile"], "prise", "wat_t7"),
            ("8. L'écran à cristaux liquides donne une mesure numérique ..........", ["Choisir...", "directe", "approchée"], "directe", "wat_t8"),
            ("9. Cet outil aide à traquer le gaspillage des veilles de la ..........", ["Choisir...", "maison", "centrale"], "maison", "wat_t9"),
            ("10. Mesurer P impose de respecter les contraintes de deux ..........", ["Choisir...", "appareils", "générateurs"], "appareils", "wat_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_wat_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"wat_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse sur l'Appareil (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_wat_tension_clean:
            # AJOUTEZ BIEN [0] ET [1] ICI :
            enonce = ligne[0]  # Récupère la phrase propre
            choix = ligne[1]   # Récupère la liste des options du menu
            cle = ligne[-1]    # Récupère la clé unique
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_wat_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_definition_puissance(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Définition de la puissance) sur deux colonnes."""
    import random

    questions_pui_sources = [
        {"id": "qp1", "q": "Quelle est l'unité internationale officielle de la puissance électrique ?", "options": ["Le watt", "Le volt", "L'ampère"], "rep": "Le watt"},
        {"id": "qp2", "q": "Quelle formule mathématique relie la puissance, la tension et l'intensité ?", "options": ["P = U x I", "P = U / I", "P = R x I²"], "rep": "P = U x I"},
        {"id": "qp3", "q": "En hommage à quel ingénieur écossais l'unité de puissance a-t-elle été nommée ?", "options": ["James Watt", "Alessandro Volta", "James Prescott Joule"], "rep": "James Watt"},
        {"id": "qp4", "q": "Une puissance de 2,5 Kilowatts (kW) est rigoureusement égale à :", "options": ["2 500 W", "250 W", "0,0025 W"], "rep": "2 500 W"},
        {"id": "qp5", "q": "Si une lampe de projecteur de 12V est traversée par un courant de 5A, sa puissance vaut :", "options": ["60 W", "17 W", "2.4 W"], "rep": "60 W"},
        {"id": "qp6", "q": "Comment exprime-t-on l'intensité I en fonction de P et de U ?", "options": ["I = P / U", "I = U / P", "I = P x U"], "rep": "I = P / U"},
        {"id": "qp7", "q": "Un radiateur de 2 300 W branché sur le secteur de 230V absorbe une intensité de :", "options": ["10 A", "0.1 A", "529 A"], "rep": "10 A"},
        {"id": "qp8", "q": "Que traduit la puissance nominale indiquée sur l'étiquette d'un appareil ?", "options": ["Sa capacité reçue en fonctionnement normal", "Sa résistance totale à froid", "Sa consommation d'énergie par heure"], "rep": "Sa capacité reçue en fonctionnement normal"},
        {"id": "qp9", "q": "Si on double l'intensité traversant un appareil sans changer la tension, sa puissance :", "options": ["Est doublée", "Reste constante", "Est divisée par quatre"], "rep": "Est doublée"},
        {"id": "qp10", "q": "La puissance électrique d'un appareil en courant alternatif dépend du facteur de puissance appelé :", "options": ["Cosinus phi", "Loi d'Ohm", "Rendement"], "rep": "Cosinus phi"}
    ]

    if "ordre_quiz_tab1_pui_aleatoire" not in st.session_state:
        random.shuffle(questions_pui_sources)
        st.session_state.ordre_quiz_tab1_pui_aleatoire = questions_pui_sources

    # Liste de synthèse structurée à 4 éléments
    if "champs_pui_tension_clean" not in st.session_state:
        st.session_state.champs_pui_tension_clean = [
            ("1. La puissance traduit la vitesse de transformation de l'..........", ["Choisir...", "énergie", "intensité"], "énergie", "pui_t1"),
            ("2. L'unité légale symbole de la puissance s'appelle le ..........", ["Choisir...", "watt", "volt"], "watt", "pui_t2"),
            ("3. L'expression mathématique en continu s'écrit P = ..........", ["Choisir...", "U x I", "U / I"], "U x I", "pui_t3"),
            ("4. Pour trouver la tension nécessaire, on applique U = ..........", ["Choisir...", "P / I", "P x I"], "P / I", "pui_t4"),
            ("5. La valeur inscrite par le constructeur est la puissance ..........", ["Choisir...", "nominale", "efficace"], "nominale", "pui_t5"),
            ("6. Un appareil de forte puissance consomme un grand ..........", ["Choisir...", "courant", "calibre"], "courant", "pui_t6"),
            ("7. Mille watts forment une unité plus grande appelée un ..........", ["Choisir...", "kilowatt", "mégawatt"], "kilowatt", "pui_t7"),
            ("8. Dans l'analogie de l'eau, la puissance est liée à la force du ..........", ["Choisir...", "moulin", "fil"], "moulin", "pui_t8"),
            ("9. À tension constante, la puissance est proportionnelle à l'..........", ["Choisir...", "intensité", "résistance"], "intensité", "pui_t9"),
            ("10. Les radiateurs et plaques de cuisson ont une puissance très ..........", ["Choisir...", "élevée", "faible"], "élevée", "pui_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_pui_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pui_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pui_tension_clean:
            # AJOUTEZ PRÉCISEMENT [0] ET [1] ICI :
            enonce = ligne[0]  # Extrait uniquement la phrase de texte
            choix = ligne[1]   # Extrait uniquement la liste des options ["Choisir...", ...]
            cle = ligne[-1]    # Extrait la clé unique de session
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_final_clean", disabled=verrouille, label_visibility="collapsed")
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
    st.header("Définition de la puissance électrique")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("Qu'est-ce que la puissance électrique ?")
    st.write(
        "La puissance électrique est une grandeur physique qui traduit la capacité d'un appareil à transformer "
        "plus ou moins rapidement l'énergie qu'il reçoit. Elle est notée P et son unité internationale "
        "est le Watt, de symbole majuscule W (en hommage à l'ingénieur écossais James Watt).\n\n"
        "Plus un appareil est puissant, plus il consomme d'électricité pour effectuer son travail "
        "(éclairer plus fort pour une lampe, chauffer plus vite pour un radiateur, ou tourner plus rapidement pour un moteur)."
    )
    
    col_pui1, col_pui2 = st.columns(2)
    with col_pui1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre la puissance, reprenons la caricature de notre rivière de montagne. "
            "Le travail à effectuer consiste à faire tourner une lourde roue de moulin mécanique. "
            "La puissance de rotation finale de la roue dépend de deux facteurs combinés :\n"
            "* **L'intensité (le débit d'eau) :** le nombre de litres d'eau qui frappent les pales chaque seconde.\n"
            "* **La tension (la hauteur de la cascade) :** la force de pression avec laquelle l'eau s'écrase sur la roue.\n\n"
            "Un petit ruisseau tombant de très haut ou un fleuve calme avançant très lentement peuvent déployer "
            "la même puissance sur la roue. C'est l'exact reflet de la formule électrique."
        )
        try:
            st.image("caricature_puissance.jpg", caption="Caricature de la puissance dépendant du débit et de la hauteur de chute")
        except Exception:
            st.warning("L'image 'caricature_puissance.jpg' est introuvable.")

    with col_pui2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "En électricité en courant continu, la puissance consommée par un dipôle récepteur dépend "
            "simultanément de la tension U à ses bornes (mesurée en volts) et de l'intensité I du courant "
            "qui le traverse (mesurée en ampères).\n\n"
            "La loi de la puissance électrique se traduit par la relation fondamentale suivante :\n\n"
            "**P = U x I**\n\n"
            "Cette formule mathématique permet de calculer n'importe quelle grandeur manquante à l'aide des règles de déduction : "
            "U = P / I et I = P / U."
        )
        try:
            st.image("circuit_puissance.jpg", caption="Montage de mesure simultanée de la tension et de l'intensité")
        except Exception:
            st.warning("L'image 'circuit_puissance.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES ET VERROUILLAGE DE L'ATELIER 1 ---
    if "suite_verrouille_tab1_pui" not in st.session_state:
        st.session_state.suite_verrouille_tab1_pui = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_pui

    # Affichage du module de questions spécifique à la puissance
    afficher_atelier_definition_puissance(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Définition de la puissance électrique.",
        key="check_certif_pui_final_net",
        disabled=verrou_at1,
    )

    # Bouton de validation pour bloquer et générer les notes du Tab 1
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_pui_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_pui_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_pui_aleatoire:
                    reponse_eleve = st.session_state.get(f"pui_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = 0.0
            if "champs_pui_tension_clean" in st.session_state:
                for ligne in st.session_state.champs_pui_tension_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_final_clean", "Choisir...") == attendu:
                        score_t1 += 1.0

            st.session_state.score_suite1_pui_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_pui_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_pui = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_pui = True
            st.st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 1 ---
    if st.session_state.get("suite_verrouille_tab1_pui", False):
        scr1_t1 = st.session_state.get("score_suite1_pui_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_pui_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_pui", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DÉFINITION PUISSANCE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_puissance = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Définition Puissance - {n_eleve}</title>
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
                <p>Atelier 1 : Notion de puissance, unité et calculs P = U x I</p>
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

        if "ordre_quiz_tab1_pui_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_pui_aleatoire, 1):
                saisie = st.session_state.get(f"pui_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_puissance += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_puissance += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t1 = preparer_nom_fichier("Rapport_Definition_Puissance").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_puissance,
            file_name=nom_fichier_html_t1,
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("L'appareil de mesure de la puissance électrique : Le wattmètre")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("Mesurer la puissance en temps réel")
    st.write(
        "Pour mesurer directement la puissance électrique consommée par un appareil sans avoir à réaliser "
        "de calcul intermédiaire, on utilise un wattmètre. Puisque la puissance dépend à la fois de la "
        "tension et de l'intensité (P = U x I), le wattmètre est un appareil hybride unique : il combine "
        "en interne les fonctionnalités d'un voltmètre et d'un ampèremètre."
    )
    st.write(
        "**La règle absolue de branchement :**\n"
        "Pour accomplir sa double mission, un wattmètre possède obligatoirement quatre bornes (ou quatre fils de connexion) :\n"
        "* **Le circuit Intensité (Ampèremétrique) :** Se branche **en série** dans la boucle pour mesurer le débit du courant.\n"
        "* **Le circuit Tension (Voltmétrique) :** Se branche **en dérivation (en parallèle)** aux bornes du dipôle pour mesurer la force de poussée."
    )
    
    col_wat1, col_wat2 = st.columns(2)
    with col_wat1:
        st.write("**Les wattmètres de laboratoire**")
        st.write(
            "Dans les laboratoires de sciences, le boîtier comporte des bornes distinctes. "
            "Il faut être très vigilant lors du câblage pour ne pas créer de court-circuit en inversant "
            "les lignes de courant et les lignes de tension."
        )
        try:
            st.image("ancien_wattmetre.jpg", caption="Wattmètre de table de laboratoire")
        except Exception:
            st.warning("L'image 'ancien_wattmetre.jpg' est introuvable.")

    with col_wat2:
        st.write("**Les wattmètres prises grand public**")
        st.write(
            "Aujourd'hui, il existe des wattmètres intégrés directement dans des boîtiers de prise murale. "
            "L'appareil s'intercale simplement entre la prise et l'électroménager. Son écran LCD affiche "
            "instantanément la puissance consommée en Watts, l'intensité en Ampères et la tension du secteur."
        )
        try:
            st.image("wattmetre_prise.jpg", caption="Wattmètre domestique portable sur prise secteur")
        except Exception:
            st.warning("L'image 'wattmetre_prise.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES AND VERROUILLAGE DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_pui" not in st.session_state:
        st.session_state.suite_verrouille_tab2_pui = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_pui

    # Affichage du module de questions spécifique au wattmètre
    afficher_atelier_appareil_puissance(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Appareil de mesure de la puissance.",
        key="check_certif_wat_final_net",
        disabled=verrou_at2,
    )

    # Validation du score et blocage de session
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_wat_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_wat_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_wat_aleatoire:
                    reponse_eleve = st.session_state.get(f"wat_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = 0.0
            if "champs_wat_tension_clean" in st.session_state:
                for ligne in st.session_state.champs_wat_tension_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_wat_clean", "Choisir...") == attendu:
                        score_t2 += 1.0

            st.session_state.score_suite2_wat_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_wat_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_wat = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_pui = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2_pui", False):
        scr1_t2 = st.session_state.get("score_suite2_wat_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_wat_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_wat", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER APPAREIL PUISSANCE SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_wattmetre = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Appareil Puissance - {n_eleve}</title>
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
                <p>Atelier 2 : Appareils de mesure de la puissance électrique et branchements</p>
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

        if "ordre_quiz_tab2_wat_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_wat_aleatoire, 1):
                saisie = st.session_state.get(f"wat_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_wattmetre += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_wattmetre += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t2 = preparer_nom_fichier("Rapport_Appareil_Puissance").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_wattmetre,
            file_name=nom_fichier_html_t2,
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("Définition de l'énergie électrique")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("Qu'est-ce que l'énergie électrique ?")
    st.write(
        "L'énergie électrique correspond à la quantité totale de travail ou de chaleur fournie par un courant "
        "pendant une certaine durée. Contrairement à la puissance (qui est instantanée), l'énergie dépend "
        "directement du temps d'utilisation de l'appareil."
    )
    
    col_ene1, col_ene2 = st.columns(2)
    with col_ene1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre la différence entre puissance et énergie, reprenons l'image de notre moulin. "
            "La puissance est la force instantanée du jet d'eau qui frappe la roue à un moment précis. "
            "L'énergie, elle, représente le **volume total d'eau accumulé** dans le bassin du bas après "
            "plusieurs heures de fonctionnement.\n\n"
            "Un petit jet d'eau (faible puissance) ouvert pendant une journée entière peut remplir un bassin "
            "bien plus grand qu'une immense cascade (forte puissance) ouverte seulement pendant deux secondes."
        )
        try:
            st.image("caricature_energie.jpg", caption="Caricature de l'énergie représentant le cumul du travail au cours du temps")
        except Exception:
            st.warning("L'image 'caricature_energie.jpg' est introuvable.")

    with col_ene2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "L'énergie électrique E consommée par un appareil est égale au produit de sa puissance P "
            "par la durée t de son fonctionnement. La loi s'exprime par la relation fondamentale :\n\n"
            "**E = P x t**\n\n"
            "**Attention aux deux systèmes d'unités :**\n"
            "* **Le système international :** Si la puissance P est en **Watts (W)** et le temps t en **secondes (s)**, l'énergie E s'exprime en **Joules (J)**.\n"
            "* **Le système commercial :** Si la puissance P est en **Watts (W)** ou en Kilowatts (kW) et le temps t en **heures (h)**, l'énergie E s'exprime en **Wattheures (Wh)** ou en Kilovattheures (kWh)."
        )
        try:
            st.image("circuit_energie.jpg", caption="Modélisation de la consommation d'énergie temporelle")
        except Exception:
            st.warning("L'image 'circuit_energie.jpg' est introuvable.")
            
    st.write(
        "Pour passer du système commercial au système légal, on utilise la passerelle de conversion temporelle. "
        "Puisqu'une heure contient 3 600 secondes, un Wattheure équivaut exactement à 3 600 Joules :\n\n"
        "**1 Wh = 3 600 J &nbsp;&nbsp;|&nbsp;&nbsp; 1 kWh = 3 600 000 J**"
    )

    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES ET VERROUILLAGE DE L'ATELIER 3 ---
    if "suite_verrouille_tab3_ene" not in st.session_state:
        st.session_state.suite_verrouille_tab3_ene = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_ene

    # Affichage du module de questions spécifique à l'énergie
    afficher_atelier_definition_energie(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Définition de l'énergie électrique.",
        key="check_certif_ene_final_net",
        disabled=verrou_at3,
    )

    # Validation du score et blocage de session
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_ene_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_ene_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_ene_aleatoire:
                    reponse_eleve = st.session_state.get(f"ene_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            score_t3 = 0.0
            if "champs_ene_tension_clean" in st.session_state:
                for ligne in st.session_state.champs_ene_tension_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ene_clean", "Choisir...") == attendu:
                        score_t3 += 1.0

            st.session_state.score_suite3_ene_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_ene_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_ene = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_ene = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 3 ---
    if st.session_state.get("suite_verrouille_tab3_ene", False):
        scr1_t3 = st.session_state.get("score_suite3_ene_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_ene_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_ene", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DÉFINITION ÉNERGIE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_energie = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Définition Énergie - {n_eleve}</title>
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
                <p>Atelier 3 : Notion d'énergie électrique, unités J/Wh et calculs E = P x t</p>
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
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3_ene_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_ene_aleatoire, 1):
                saisie = st.session_state.get(f"ene_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_energie += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_energie += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t3 = preparer_nom_fichier("Rapport_Definition_Energie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_energie,
            file_name=nom_fichier_html_t3,
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("L'appareil de mesure de l'énergie électrique : Le compteur")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("Mesurer le cumul de la consommation")
    st.write(
        "Pour mesurer la quantité totale d'énergie électrique consommée par une installation au fil du temps, "
        "on utilise un compteur électrique. Cet appareil enregistre en continu et cumule les kilowattheures (kWh) "
        "consommés par l'ensemble des appareils branchés dans la maison. Les technologies ont beaucoup évolué."
    )
    
    col_cpt1, col_cpt2 = st.columns(2)
    with col_cpt1:
        st.write("**Les anciens appareils : Le compteur électromécanique**")
        st.write(
            "Il possède un disque métallique horizontal en rotation. Chaque tour de disque correspond à une quantité "
            "fixe d'énergie consommée, définie par la **constante du compteur C** (exprimée en Wh/tour). "
            "Le disque entraîne mécaniquement un totalisateur à rouleaux qui affiche l'index de consommation."
        )
        try:
            st.image("compteur_disque.jpg", caption="Ancien compteur électrique à disque rotatif mécanique")
        except Exception:
            st.warning("L'image 'compteur_disque.jpg' est introuvable.")

    with col_cpt2:
        st.write("**Les nouveaux appareils : Le compteur intelligent Linky**")
        st.write(
            "Aujourd'hui, le réseau français utilise le compteur communicant Linky. Entièrement électronique, "
            "il mesure l'énergie de manière numérique avec une grande précision. Il transmet automatiquement "
            "les index de consommation à distance sans nécessiter le déplacement d'un technicien."
        )
        try:
            st.image("compteur_linky.jpg", caption="Compteur communicant moderne Linky")
        except Exception:
            st.warning("L'image 'compteur_linky.jpg' est introuvable.")
            
    st.write(
        "**La constante du compteur (C) :**\n"
        "Sur les anciens compteurs, la constante C permet de lier mathématiquement le nombre de tours du disque (n) "
        "à l'énergie consommée (E) par la formule : &nbsp; **E = n x C**.\n"
        "Par exemple, si un compteur possède une constante C = 2 Wh/tr, un total de 500 tours de disque indique "
        "une consommation de 1 000 Wh, soit 1 kWh."
    )

    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES ET VERROUILLAGE DE L'ATELIER 4 ---
    if "suite_verrouille_tab4_cpt" not in st.session_state:
        st.session_state.suite_verrouille_tab4_cpt = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_cpt

    # Affichage du module de questions spécifique au compteur
    afficher_atelier_appareil_energie(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Appareil de mesure de l'énergie.",
        key="check_certif_cpt_final_net",
        disabled=verrou_at4,
    )

    # Validation du score et blocage de session
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_cpt_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_cpt_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_cpt_aleatoire:
                    reponse_eleve = st.session_state.get(f"cpt_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            score_t4 = 0.0
            if "champs_cpt_tension_clean" in st.session_state:
                for ligne in st.session_state.champs_cpt_tension_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_cpt_clean", "Choisir...") == attendu:
                        score_t4 += 1.0

            st.session_state.score_suite4_cpt_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_cpt_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_cpt = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_cpt = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 4 ---
    if st.session_state.get("suite_verrouille_tab4_cpt", False):
        scr1_t4 = st.session_state.get("score_suite4_cpt_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_cpt_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_cpt", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER APPAREIL ÉNERGIE SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_compteur = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Appareil Énergie - {n_eleve}</title>
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
                <p>Atelier 4 : Appareils de mesure de l'énergie électrique, constantes et compteurs</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4_cpt_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_cpt_aleatoire, 1):
                saisie = st.session_state.get(f"cpt_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_compteur += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_compteur += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t4 = preparer_nom_fichier("Rapport_Appareil_Energie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_compteur,
            file_name=nom_fichier_html_t4,
            mime="text/html",
            use_container_width=True
        )

with tab5:
    st.header("Énergie consommée par une maison")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("La gestion de la consommation domestique")
    st.write(
        "Au sein d'une habitation, chaque appareil électroménager possède une puissance nominale propre. "
        "L'énergie totale consommée par le foyer dépend de la puissance de chaque dipôle activé, "
        "multipliée par son temps d'utilisation au cours de la journée. "
        "Pour calculer la facture, on additionne les énergies consommées par chaque équipement."
    )
    
    col_mai1, col_mai2 = st.columns(2)
    with col_mai1:
        st.write("**Les postes énergivores à la maison**")
        st.write(
            "Tous les appareils ne consomment pas la même quantité d'énergie. "
            "Les équipements dotés de résistances thermiques (four électrique, radiateur, chauffe-eau, lave-linge) "
            "nécessitent une puissance très élevée (souvent entre 1 500 W et 3 000 W) et pèsent lourd sur la facture. "
            "À l'inverse, l'informatique et l'éclairage led moderne demandent une puissance faible."
        )
        try:
            st.image("appareils_maison.jpg", caption="Différents types de récepteurs électriques domestiques")
        except Exception:
            st.warning("L'image 'appareils_maison.jpg' est introuvable.")

    with col_mai2:
        st.write("**Le coût de l'électricité**")
        st.write(
            "Le fournisseur d'énergie électrique facture chaque kilowattheure (kWh) consommé à un tarif fixe. "
            "Pour estimer le coût d'utilisation d'un appareil, on applique la formule :\n\n"
            "**Coût = Énergie (en kWh) x Prix du kWh**\n\n"
            "Adopter des éco-gestes (éteindre les veilles, utiliser les modes Éco, privilégier des appareils de classe A) "
            "permet de réduire le cumul d'énergie mesuré par le compteur."
        )
        try:
            st.image("facture_electricite.jpg", caption="Exemple de suivi de consommation sur une facture énergétique")
        except Exception:
            st.warning("L'image 'facture_electricite.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF DE LA MAISON VIRTUELLE ---
    st.subheader("Animation : Simulateur de consommation énergétique du foyer")
    st.write(
        "Cochez les appareils que vous souhaitez allumer dans la maison et ajustez la durée "
        "de fonctionnement à l'aide des curseurs. Observez l'énergie totale cumulée et le coût généré."
    )

    # Paramètres de calcul du laboratoire (Tarif indicatif du kWh)
    PRIX_KWH = 0.25  # 0.25 € par kWh

    col_l5_1, col_l5_2 = st.columns(2)
    
    with col_l5_1:
        st.markdown("##### Configuration des appareils thermiques (Forte puissance)")
        use_four = st.checkbox("Allumer le four de cuisson (Puissance : 2 500 W)", value=False, key="chk_four")
        heures_four = st.slider("Durée d'utilisation du four [heures]", 0.0, 5.0, 1.0, 0.5, key="sld_four", disabled=not use_four)
        
        use_radiateur = st.checkbox("Allumer le radiateur électrique (Puissance : 1 500 W)", value=False, key="chk_rad")
        heures_radiateur = st.slider("Durée de chauffage du radiateur [heures]", 0.0, 24.0, 4.0, 1.0, key="sld_rad", disabled=not use_radiateur)

    with col_l5_2:
        st.markdown("##### Configuration des récepteurs secondaires (Basse puissance)")
        use_ecl = st.checkbox("Activer l'éclairage de la maison (10 lampes LED : Total 100 W)", value=True, key="chk_ecl")
        heures_ecl = st.slider("Durée de fonctionnement de l'éclairage [heures]", 0.0, 24.0, 6.0, 1.0, key="sld_ecl", disabled=not use_ecl)
        
        use_tv = st.checkbox("Allumer la télévision et l'ordinateur (Total : 200 W)", value=True, key="chk_tv")
        heures_tv = st.slider("Durée d'utilisation multimédia [heures]", 0.0, 12.0, 3.0, 0.5, key="sld_tv", disabled=not use_tv)

    # Calcul dynamique des énergies en kWh : E = (P x t) / 1000
    e_four = (2500.0 * heures_four) / 1000.0 if use_four else 0.0
    e_rad  = (1500.0 * heures_radiateur) / 1000.0 if use_radiateur else 0.0
    e_ecl  = (100.0 * heures_ecl) / 1000.0 if use_ecl else 0.0
    e_tv   = (200.0 * heures_tv) / 1000.0 if use_tv else 0.0

    energie_totale_maison_kwh = e_four + e_rad + e_ecl + e_tv
    cout_total_euros = energie_totale_maison_kwh * PRIX_KWH

    # Affichage des indicateurs de la maison
    st.write("**Index du tableau de bord de la maison en temps réel :**")
    col_m5_1, col_m5_2, col_m5_3 = st.columns(3)
    with col_m5_1:
        st.metric(label="Énergie totale consommée", value=f"{energie_totale_maison_kwh:.2f} kWh")
    with col_m5_2:
        st.metric(label="Tarif de référence appliqué", value=f"{PRIX_KWH:.2f} € / kWh")
    with col_m5_3:
        st.metric(label="Coût estimé de la session", value=f"{cout_total_euros:.2f} €")

    # Graphique à barres horizontales pour visualiser le poids de chaque appareil
    donnees_appareils = pd.DataFrame({
        "Équipements domestiques": ["Four", "Radiateur", "Éclairage LED", "Multimédia"],
        "Énergie consommée (kWh)": [e_four, e_rad, e_ecl, e_tv]
    })
    st.bar_chart(donnees_appareils, x="Équipements domestiques", y="Énergie consommée (kWh)")

    if cout_total_euros > 2.50:
        st.error("Alerte consommation : La facture grimpe rapidement ! Essayez de modérer le chauffage ou l'utilisation du four.")
    else:
        st.success("Bilan éco-citoyen : Votre consommation est maîtrisée et reste économique.")

    st.divider()

    # --- SECTION 3 : ZONE DE EXERCICES ET VERROUILLAGE DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_mai" not in st.session_state:
        st.session_state.suite_verrouille_tab5_mai = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_mai

    # Affichage du module de questions spécifique à la maison
    afficher_atelier_consommation_maison(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Énergie consommée par une maison.",
        key="check_certif_mai_final_net",
        disabled=verrou_at5,
    )

    # Validation du score et blocage de session
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_mai_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_mai_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_mai_aleatoire:
                    reponse_eleve = st.session_state.get(f"mai_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q5 += 1.0

            score_t5 = 0.0
            if "champs_mai_tension_clean" in st.session_state:
                for ligne in st.session_state.champs_mai_tension_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_mai_clean", "Choisir...") == attendu:
                        score_t5 += 1.0

            st.session_state.score_suite5_mai_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_mai_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_mai = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab5_mai = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 5 ---
    if st.session_state.get("suite_verrouille_tab5_mai", False):
        scr1_t5 = st.session_state.get("score_suite5_mai_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_mai_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_mai", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ENERGIE MAISON SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_maison = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Énergie Maison - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4f46e5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #4f46e5; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct { color: #10b981; font-weight: bold; text-transform: uppercase; }
                .status-incorrect { color: #ef4444; font-weight: bold; text-transform: uppercase; }
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 5 : Consommation électrique du logement, bilans en kWh et coûts</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4f46e5;">
                Note obtenue au Quiz Technique : <strong>{scr1_t5:.1f} / 10</strong><br>
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

        if "ordre_quiz_tab5_mai_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_mai_aleatoire, 1):
                saisie = st.session_state.get(f"mai_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_maison += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_maison += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t5 = preparer_nom_fichier("Rapport_Energie_Maison").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_maison,
            file_name=nom_fichier_html_t5,
            mime="text/html",
            use_container_width=True
        )


with tab6:
    st.header("Production d'énergie : Passé, présent et futur")
    
    # --- SECTION 1 : EXPLICATION ET COURS ---
    st.subheader("L'évolution des modes de production électrique")
    st.write(
        "Pour répondre aux besoins de la société, l'humanité a développé différentes technologies "
        "pour convertir des sources d'énergie primaires en électricité. Ces modes de production "
        "se classent en trois grandes époques technologiques."
    )
    
    col_prod1, col_prod2 = st.columns(2)
    with col_prod1:
        st.write("**1. Les énergies du passé : Les centrales thermiques fossiles**")
        st.write(
            "Historiquement basées sur la combustion du charbon, du pétrole ou du gaz, ces centrales "
            "brûlent des matières fossiles pour générer de la vapeur haute pression et faire tourner un alternateur. "
            "Bien que très puissantes, elles rejettent d'immenses quantités de dioxyde de carbone (CO2) "
            "et sont progressivement abandonnées pour lutter contre le réchauffement climatique."
        )
        try:
            st.image("centrale_fossile.jpg", caption="Centrale thermique traditionnelle à charbon")
        except Exception:
            st.warning("L'image 'centrale_fossile.jpg' est introuvable.")

        st.write("**3. Les énergies du futur : Fusion nucléaire et hydrogène**")
        st.write(
            "La recherche scientifique prépare les technologies de demain :\n"
            "* **La fusion nucléaire (projet ITER) :** reproduire la réaction physique au cœur du Soleil en fusionnant des isotopes d'hydrogène. Elle promet une énergie quasi infinie, décarbonée et sans déchets radioactifs à longue vie.\n"
            "* **L'hydrogène vert :** utilisé comme vecteur de stockage pour restituer l'électricité via des piles à combustible lors des pics de consommation."
        )
        try:
            st.image("fusion_iter.jpg", caption="Modélisation du réacteur de fusion nucléaire ITER")
        except Exception:
            st.warning("L'image 'fusion_iter.jpg' est introuvable.")

    with col_prod2:
        st.write("**2. Les énergies actuelles : Nucléaire de fission et renouvelables**")
        st.write(
            "Le mix de transition actuel repose sur deux piliers majeurs :\n"
            "* **Le nucléaire de fission :** casse des atomes lourds d'uranium pour produire de la chaleur. Il fournit une puissance colossale et continue sans émettre de CO2, mais pose la question de la gestion des déchets radioactifs.\n"
            "* **Les énergies renouvelables (EnR) :** captent les flux naturels (barrages hydrauliques, parcs éoliens, panneaux solaires photovoltaïques). Elles sont propres mais intermittentes (dépendantes de la météo)."
        )
        try:
            st.image("energies_renouvelables.jpg", caption="Transition énergétique : Éolien et solaire")
        except Exception:
            st.warning("L'image 'energies_renouvelables.jpg' est introuvable.")
            
    st.divider()

    # --- SECTION 2 : LABORATOIRE INTERACTIF DU MIX ÉNERGÉTIQUE ---
    st.subheader("Animation : Simulateur de mix énergétique national")
    st.write(
        "Ajustez la puissance installée pour chaque mode de production et observez si vous parvenez "
        "à couvrir la demande électrique du pays (fixée à 60 000 MW) tout en limitant les émissions de CO2."
    )

    DEMANDE_NATIONALE = 60000.0  # MW

    col_sim_1, col_sim_2 = st.columns(2)
    with col_sim_1:
        st.markdown("##### Énergies pilotables stables")
        p_nucleaire = st.slider("Puissance Nucléaire (Fission) [MW]", 0, 50000, 35000, step=1000, key="sld_prod_nuc")
        p_fossile = st.slider("Puissance Thermique (Charbon/Gaz) [MW]", 0, 20000, 5000, step=1000, key="sld_prod_fos")
    with col_sim_2:
        st.markdown("##### Énergies renouvelables et futures")
        p_renouvelable = st.slider("Puissance Renouvelables (Eau/Vent/Soleil) [MW]", 0, 30000, 15000, step=1000, key="sld_prod_enr")
        p_fusion = st.slider("Puissance Prototype (Fusion nucléaire future) [MW]", 0, 10000, 0, step=1000, key="sld_prod_fus")

    # Calcul des totaux et de l'empreinte carbone indicitative
    production_totale_mw = p_nucleaire + p_fossile + p_renouvelable + p_fusion
    co2_total_t = (p_fossile * 0.9) + (p_nucleaire * 0.01) + (p_renouvelable * 0.02) + (p_fusion * 0.0)

    # Affichage des métriques de performance
    st.write("**Indicateurs de performance du réseau électrique :**")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="Production totale", value=f"{production_totale_mw:,} MW", delta=f"Cible : {DEMANDE_NATIONALE:,} MW")
    with col_res2:
        st.metric(label="Émissions de CO2 estimées", value=f"{co2_total_t:,.0f} t/h", delta="Traque carbone", delta_color="inverse")
    with col_res3:
        equilibre = production_totale_mw - DEMANDE_NATIONALE
        if equilibre < 0:
            st.metric(label="Statut du réseau", value="Pénurie", delta=f"{equilibre:,} MW", delta_color="inverse")
        elif equilibre > 10000:
            st.metric(label="Statut du réseau", value="Surcharge", delta=f"+{equilibre:,} MW", delta_color="off")
        else:
            st.metric(label="Statut du réseau", value="Équilibré", delta=f"+{equilibre:,} MW")

    # Rendu graphique du mix de production
    df_mix = pd.DataFrame({
        "Sources d'énergie": ["Nucléaire", "Fossile", "Renouvelables", "Fusion (Futur)"],
        "Puissance injectée (MW)": [p_nucleaire, p_fossile, p_renouvelable, p_fusion]
    })
    st.bar_chart(df_mix, x="Sources d'énergie", y="Puissance injectée (MW)")

    # Diagnostics d'apprentissage
    if production_totale_mw < DEMANDE_NATIONALE:
        st.error("Alerte réseau : La production est insuffisante pour couvrir les besoins du pays. Risque de blackout ! Augmentez la puissance des centrales.")
    elif p_fossile > 8000:
        st.warning("Alerte environnement : Votre mix énergétique s'appuie trop sur les énergies fossiles du passé. L'empreinte carbone est critique.")
    else:
        st.success("Félicitations : L'approvisionnement électrique est assuré de manière éco-responsable avec un mix équilibré.")

    st.divider()

    # --- SECTION 3 : ZONE DES EXERCICES ET VERROUILLAGE DE L'ATELIER 6 ---
    if "suite_verrouille_tab6_prod" not in st.session_state:
        st.session_state.suite_verrouille_tab6_prod = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_prod

    # Affichage du module de questions spécifique à la production
    afficher_atelier_production_energie(verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Production d'énergie.",
        key="check_certif_prod_final_net",
        disabled=verrou_at6,
    )

    # Validation du score et blocage de session
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_suite6_prod_official", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            if "ordre_quiz_tab6_prod_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_prod_aleatoire:
                    reponse_eleve = st.session_state.get(f"prod_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q6 += 1.0

            score_t6 = 0.0
            if "champs_prod_tension_clean" in st.session_state:
                for ligne in st.session_state.champs_prod_tension_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_prod_clean", "Choisir...") == attendu:
                        score_t6 += 1.0

            st.session_state.score_suite6_prod_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_prod_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_prod = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_prod = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 6 ---
    if st.session_state.get("suite_verrouille_tab6_prod", False):
        scr1_t6 = st.session_state.get("score_suite6_prod_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_prod_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6_prod", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER PRODUCTION ÉNERGIE SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_production = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Production Énergie - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #15803d; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .status-correct { color: #10b981; font-weight: bold; text-transform: uppercase; }
                .status-incorrect { color: #ef4444; font-weight: bold; text-transform: uppercase; }
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 6 : Mix énergétique, filières de production passées, actuelles et futures</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #15803d;">
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

        if "ordre_quiz_tab6_prod_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_prod_aleatoire, 1):
                saisie = st.session_state.get(f"prod_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_production += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_production += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_t6 = preparer_nom_fichier("Rapport_Production_Energie").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_production,
            file_name=nom_fichier_html_t6,
            mime="text/html",
            use_container_width=True
        )


