
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application moteurs électriques",
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
st.title("Application moteurs électriques")
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


onglets = st.tabs([
    "identification",
    "Identification et Normes",
    "Historique",
    "Principe General",
    "Moteur CC a Excitation Independante",
    "Moteur CC a Excitation Serie",
    "Moteur CC Shunt",
    "Moteur CC Compound",
    "Moteur CC sans balais (Brushless)",
    "Moteur Asynchrone a Cage d'Ecureuil",
    "Moteur Asynchrone a Rotor Bobine",
    "Moteur Asynchrone Monophase",
    "Moteur Synchrone a Aimants Permanents",
    "Moteur Synchrone a Rotor Bobine",
    "Moteur Synchrone a Reluctance Variable",
    "Moteur Universel",
    "Moteur Pas a Pas",
    "Servomoteur",
    "Moteur Lineaire"
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
tab10 = onglets[10]
tab11 = onglets[11]
tab12 = onglets[12]
tab13 = onglets[13]
tab14 = onglets[14]
tab15 = onglets[15]
tab16 = onglets[16]
tab17 = onglets[17]
tab18 = onglets[18]

def afficher_atelier_tab18(verrouille=False):
    questions_t18 = [
        {"id": "q1", "q": "Quelle est la particularite geometrique fondamentale du moteur lineaire ?", "options": ["Sa structure synchrone ou asynchrone est entierement deployee et etalee a plat", "Il possede un rotor spherique tournant sur trois axes simultanes", "Il fonctionne sans aucun champ magnetique statorique inducteur", "Son entrefer mecanique est compose d'un bain de mercure liquide"], "rep": "Sa structure synchrone ou asynchrone est entierement deployee et etalee a plat"},
        {"id": "q2", "q": "Quel chercheur et ingenieur britannique a developpe les prototypes majeurs dans les annees 1960 ?", "options": ["Eric Laithwaite", "Hendrik Lorentz", "Michael Faraday", "James Clerk Maxwell"], "rep": "Eric Laithwaite"},
        {"id": "q3", "q": "Quel type de mouvement ce moteur genere-t-il de maniere directe ?", "options": ["Une translation rectiligne sans aucun contact ni liaison rotative", "Une rotation angulaire continue a haute vitesse", "Une oscillation vibratoire de type piezo-electrique", "Un mouvement hélicoidal asymétrique"], "rep": "Une translation rectiligne sans aucun contact ni liaison rotative"},
        {"id": "q4", "q": "Comment appelle-t-on le champ magnetique produit le long du stator plan ?", "options": ["Un champ magnetique glissant (ou onde glissante)", "Un champ magnetique purement pulsant monophase", "Un champ magnetique radial constant", "Un flux tournant concentrique"], "rep": "Un champ magnetique glissant (ou onde glissante)"},
        {"id": "q5", "q": "Quel systeme mecanique intermediaire ce moteur permet-il d'eliminer ?", "options": ["Les reducteurs, courroies, bielles et vis sans fin", "Les bobinages de cuivre et les circuits d'acier", "Les onduleurs de puissance et les drivers", "Les capteurs de position et d'effet Hall"], "rep": "Les reducteurs, courroies, bielles et vis sans fin"},
        {"id": "q6", "q": "Quel moyen de transport a haute vitesse celebre exploite cette technologie ?", "options": ["Le train a levitation magnetique type Maglev", "Le tramway urbain filaire classique", "Les navires de croisiere transatlantiques", "Les autobus electriques a recharge sol"], "rep": "Le train a levitation magnetique type Maglev"},
        {"id": "q7", "q": "Quelle est la nature de l'acceleration developpee par un moteur lineaire ?", "options": ["Extremement intense grace a l'absence d'inertie des pieces rotatives", "Tres faible et limitee par les frottements frictionnels", "Strictement dependante du diametre de l'arbre primitif", "Oscillante et instable selon l'epaisseur de la culasse"], "rep": "Extremement intense grace a l'absence d'inertie des pieces rotatives"},
        {"id": "q8", "q": "De quoi est generalement constitue la partie mobile (chariot) d'une version synchrone lineaire ?", "options": ["D'une serie d'aimants permanents alignes", "D'une cage d'ecureuil en aluminium deroulee", "D'un collecteur a lames de cuivre deploye", "D'un simple bloc de plastique amagnetique"], "rep": "D'une serie d'aimants permanents alignes"},
        {"id": "q9", "q": "Quelle formule regit la vitesse lineaire de synchronisme (Vs) en fonction du pas polaire tau ?", "options": ["Vs = 2 x tau x f", "Vs = f / p", "Vs = U / B", "Vs = C x omega"], "rep": "Vs = 2 x tau x f"},
        {"id": "q10", "q": "Dans quel outil d'usinage industriel de haute precision retrouve-t-on ce moteur ?", "options": ["Les machines de decoupe laser et les tables de positionnement", "Les betonnières de chantier", "Les broyeurs de fortes roches minieres", "Les compresseurs de climatisation"], "rep": "Les machines de decoupe laser et les tables de positionnement"}
    ]
    if "ordre_quiz_tab18_aleatoire" not in st.session_state:
        random.shuffle(questions_t18)
        st.session_state.ordre_quiz_tab18_aleatoire = questions_t18

    champs_t18 = [
        ("1. Le moteur lineaire supprime le besoin de transformation du .........", ["Choisir...", "mouvement", "courant"], "mouvement", "t18_c1"),
        ("2. La structure de la machine est deployee à ......... le long du rail.", ["Choisir...", "plat", "l'envers"], "plat", "t18_c2"),
        ("3. Le stator plan genere une onde magnetique qualifiee de .........", ["Choisir...", "glissante", "tournante"], "glissante", "t18_c3"),
        ("4. L'action mecanique appliquee au chariot est une force de .........", ["Choisir...", "poussee", "torsion"], "poussee", "t18_c4"),
        ("5. L'absence de contact direct elimine les frottements et l'......... mecanique.", ["Choisir...", "usure", "induction"], "usure", "t18_c5"),
        ("6. Les accelerations developpees sur l'axe rectiligne sont tres .........", ["Choisir...", "intenses", "modestes"], "intenses", "t18_c6"),
        ("7. La vitesse lineaire depend directement de la ......... du balai onduleur.", ["Choisir...", "frequence", "tension"], "frequence", "t18_c7"),
        ("8. La distance entre deux poles magnetiques consecutifs est le pas .........", ["Choisir...", "polaire", "angulaire"], "polaire", "t18_c8"),
        ("9. Le train Maglev l'utilise pour s'affranchir du contact avec les .........", ["Choisir...", "rails", "phases"], "rails", "t18_c9"),
        ("10. C'est la solution ideale pour la deccoupe industrielle au .........", ["Choisir...", "laser", "disque"], "laser", "t18_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Lineaire (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab18_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t18_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Lineaire (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t18:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t18_h_{cle}", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_tab17(verrouille=False):
    questions_t17 = [
        {"id": "q1", "q": "Qu'est-ce qu'un servomoteur au sens de l'automatisme et de la cybernetique ?", "options": ["Un systeme complet de motorisation fonctionnant en boucle fermee", "Un moteur dote uniquement d'un réducteur mecanique de couple", "Une machine electrique destinee exclusivement au pompage de l'eau", "Un moteur synchrone fonctionnant sans aucun capteur"], "rep": "Un systeme complet de motorisation fonctionnant en boucle fermee"},
        {"id": "q2", "q": "Quel scientifique a activement formalise les outils de stabilite des boucles de retroaction ?", "options": ["Harry Nyquist", "Nikola Tesla", "Thomas Davenport", "Werner von Siemens"], "rep": "Harry Nyquist"},
        {"id": "q3", "q": "Quel capteur interne mesure en temps reel la position de l'axe d'un servomoteur ?", "options": ["Un codeur rotatif (optique ou magnetique)", "Un thermocouple de type K", "Un peson electronique a jauge", "Un debitmetre a turbine"], "rep": "Un codeur rotatif (optique ou magnetique)"},
        {"id": "q4", "q": "Que fait le servomoteur si une force externe tente de modifier sa position de consigne ?", "options": ["Il augmente son courant pour developper un couple correcteur oppose", "Il coupe immediatement son alimentation par securite", "Il passe instantanement en rotation continue libre", "Il annule son champ pour eviter les surcharges"], "rep": "Il augmente son courant pour developper un couple correcteur oppose"},
        {"id": "q5", "q": "Quelle est l'unite de commande standard utilisee pour envoyer la consigne aux petits servomoteurs ?", "options": ["Un signal a modulation d'impulsion en largeur (PWM)", "Une tension continue pure variant de 0 a 10V", "Un courant alternatif de frequence industrielle 50Hz", "Une liaison serie de type hacheur geometrique"], "rep": "Un signal a modulation d'impulsion en largeur (PWM)"},
        {"id": "q6", "q": "Comment appelle-t-on la difference entre la position demandee et la position reelle ?", "options": ["L'erreur (ou l'ecart de consigne)", "Le glissement inductif", "Le pas angulaire discret", "La reluctance minimale"], "rep": "L'erreur (ou l'ecart de consigne)"},
        {"id": "q7", "q": "Quel composant mecanique interne permet d'augmenter le couple au detriment de la vitesse ?", "options": ["Un train d'engrenages reducteur", "Un collecteur a lames de cuivre", "Un arbre creux en aluminium", "Un anneau de court-circuit"], "rep": "Un train d'engrenages reducteur"},
        {"id": "q8", "q": "Quel type de moteur trouve-t-on generalement au coeur des servomoteurs industriels de haute performance ?", "options": ["Un moteur synchrone Brushless", "Un moteur asynchrone monophase", "Un moteur universel a balais", "Un moteur CC a excitation serie"], "rep": "Un moteur synchrone Brushless"},
        {"id": "q9", "q": "Que signifie un asservissement de type PID couramment integre au controleur ?", "options": ["Proportionnel Proportionnel Integrale Derivee", "Potentiel Induction Dynamique", "Position Intensite Dephasage", "Pas Impulsion Distribution"], "rep": "Proportionnel Proportionnel Integrale Derivee"},
        {"id": "q10", "q": "Dans quel secteur le servomoteur est-il l'element d'actionnement principal ?", "options": ["Les bras robotiques industriels et l'aeronautique", "Les appareils de gros electromenager", "La ventilation des batiments tertiaires", "Les lignes de distribution haute tension"], "rep": "Les bras robotiques industriels et l'aeronautique"}
    ]
    if "ordre_quiz_tab17_aleatoire" not in st.session_state:
        random.shuffle(questions_t17)
        st.session_state.ordre_quiz_tab17_aleatoire = questions_t17

    champs_t17 = [
        ("1. Le servomoteur verifie en permanence sa position grace a la .........", ["Choisir...", "retroaction", "induction"], "retroaction", "t17_c1"),
        ("2. L'asservissement compare la mesure reelle avec la ......... demandee.", ["Choisir...", "consigne", "vitesse"], "consigne", "t17_c2"),
        ("3. Le capteur de position le plus repandu est le ......... rotatif.", ["Choisir...", "codeur", "rheostat"], "codeur", "t17_c3"),
        ("4. La commande traite l'ecart pour le ramener vers .........", ["Choisir...", "zero", "le maximum"], "zero", "t17_c4"),
        ("5. La boucle de regulation s'effectue de maniere .........", ["Choisir...", "fermee", "ouverte"], "fermee", "t17_c5"),
        ("6. Le correcteur ajuste instantanement le ......... delivre par le moteur.", ["Choisir...", "couple", "flux"], "couple", "t17_c6"),
        ("7. Les engrenages internes constituent le reducteur de .........", ["Choisir...", "vitesse", "tension"], "vitesse", "t17_c7"),
        ("8. Face a une force externe, le servomoteur developpe une .........", ["Choisir...", "opposition", "annulation"], "opposition", "t17_c8"),
        ("9. Le signal PWM code l'angle voulu par la largeur des .........", ["Choisir...", "impulsions", "phases"], "impulsions", "t17_c9"),
        ("10. C'est l'actionneur indispensable pour les articulations de .........", ["Choisir...", "robots", "pompes"], "robots", "t17_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Servomoteur (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab17_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t17_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Servomoteur (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t17:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t17_h_{cle}", disabled=verrouille, label_visibility="collapsed")






def afficher_atelier_tab16(verrouille=False):
    questions_t16 = [
        {"id": "q1", "q": "Quelle est la principale caracteristique fonctionnelle d'un moteur pas a pas ?", "options": ["Il convertit des impulsions electriques en deplacements angulaires discrets", "Il tourne en continu a vitesse constante des qu'il est relie au secteur", "Il necessite obligatoirement des balais de carbone pour commuter son flux", "Il fonctionne uniquement avec un champ magnetique pulsant monophase"], "rep": "Il convertit des impulsions electriques en deplacements angulaires discrets"},
        {"id": "q2", "q": "Quel domaine technologique a impulse le developpement massif de ce moteur au XXe siecle ?", "options": ["L'informatique, les imprimantes et les automatismes numeriques", "La traction ferroviaire lourde et les tramways", "L'electromenager et le pompage domestique", "La production d'energie dans les centrales"], "rep": "L'informatique, les imprimantes et les automatismes numeriques"},
        {"id": "q3", "q": "Comment appelle-t-on le mode de commande qui permet de doubler la resolution angulaire de l'axe ?", "options": ["Le mode Demi-pas", "Le mode Pas entier", "Le couplage Triangle", "L'excitation Shunt"], "rep": "Le mode Demi-pas"},
        {"id": "q4", "q": "Quel est l'angle de pas standard tres repandu sur la majorite des moteurs industriels ?", "options": ["1.8 degre", "5.0 degres", "45 degres", "90 degres"], "rep": "1.8 degre"},
        {"id": "q5", "q": "Quel phenomene critique apparait si la charge mecanique depasse le couple maximal du moteur ?", "options": ["La perte de pas sans que le calculateur n'en soit averti", "L'emballement destructeur de l'arbre vers l'infini", "Le passage automatique en mode synchrone triphase", "La destruction instantanee des aimants par effet Joule"], "rep": "La perte de pas sans que le calculateur n'en soit averti"},
        {"id": "q6", "q": "Comment evolue le couple utile d'un moteur pas a pas lorsque sa vitesse augmente ?", "options": ["Le couple diminue de maniere significative", "Le couple augmente de facon exponentielle", "Le couple reste rigoureusement constant", "Le couple devient nul puis s'inverse"], "rep": "Le couple diminue de maniere significative"},
        {"id": "q7", "q": "Quel composant est indispensable entre le microcontroleur et le moteur pas a pas ?", "options": ["Un driver ou circuit de puissance", "Un condensateur de demarrage", "Un rheostat triphase", "Un balai frictionnel"], "rep": "Un driver ou circuit de puissance"},
        {"id": "q8", "q": "De quoi est generalement constitue le rotor d'un moteur pas a pas hybride ?", "options": ["D'un aimant permanent dente entouré de couronnes de fer", "D'une simple cage d'ecureuil en aluminium coule", "De bobinages de fils fins relies a des bagues lisses", "D'un bloc d'acier massif sans aucune denture"], "rep": "D'un aimant permanent dente entouré de couronnes de fer"},
        {"id": "q9", "q": "Quel est le comportement energetique de ce moteur lorsqu'il est a l'arret sous tension ?", "options": ["Il consomme du courant pour maintenir son couple de maintien", "Sa consommation devient totalement nulle", "Il renvoie de l'energie reactive vers le reseau", "Il se deconnecte automatiquement par securite"], "rep": "Il consomme du courant pour maintenir son couple de maintien"},
        {"id": "q10", "q": "Dans quelle application moderne grand public ce moteur est-il incontournable ?", "options": ["Les imprimantes 3D et les petites machines CNC", "Les pompes de filtration de piscine", "Les ventilateurs de refroidissement d'usine", "Les alternateurs de secours"], "rep": "Les imprimantes 3D et les petites machines CNC"}
    ]
    if "ordre_quiz_tab16_aleatoire" not in st.session_state:
        random.shuffle(questions_t16)
        st.session_state.ordre_quiz_tab16_aleatoire = questions_t16

    champs_t16 = [
        ("1. Le moteur pas a pas est un actionneur de positionnement .........", ["Choisir...", "numerique", "analogique"], "numerique", "t16_c1"),
        ("2. Le stator est subdivise en plusieurs enroulements appeles .........", ["Choisir...", "phases", "balais"], "phases", "t16_c2"),
        ("3. Chaque impulsion electrique provoque un deplacement angulaire .........", ["Choisir...", "fixe", "variable"], "fixe", "t16_c3"),
        ("4. Le controle de position s'effectue couramment en boucle .........", ["Choisir...", "ouverte", "fermee"], "ouverte", "t16_c4"),
        ("5. En mode demi-pas, le deplacement angulaire est divise par .........", ["Choisir...", "deux", "quatre"], "deux", "t16_c5"),
        ("6. A l'arret, le moteur developpe un couple de ......... important.", ["Choisir...", "maintien", "friction"], "maintien", "t16_c6"),
        ("7. Une charge trop lourde provoque un saut de denture appele perte de .........", ["Choisir...", "pas", "flux"], "pas", "t16_c7"),
        ("8. Le rotor dente s'aligne sur le champ magnetique du .........", ["Choisir...", "stator", "collecteur"], "stator", "t16_c8"),
        ("9. La precision geometrique depend du nombre de ......... du rotor.", ["Choisir...", "dents", "bagues"], "dents", "t16_c9"),
        ("10. Ce moteur est ideal pour la commande des axes d'une imprimante .........", ["Choisir...", "3D", "thermique"], "3D", "t16_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Pas a Pas (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab16_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t16_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Pas a Pas (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t16:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t16_h_{cle}", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_tab15(verrouille=False):
    questions_t15 = [
        {"id": "q1", "q": "Pourquoi le moteur universel est-il capable de fonctionner en courant alternatif ?", "options": ["Le courant change de sens simultanement dans l'inducteur et l'induit, conservant le sens de la force", "Un pont redresseur de diodes secret est moule a l'interieur du carter", "Le moteur se verrouille de facon synchrone sur les 50 Hz du secteur", "Le rotor change de nombre de poles a chaque alternance de ligne"], "rep": "Le courant change de sens simultanement dans l'inducteur et l'induit, conservant le sens de la force"},
        {"id": "q2", "q": "De quelle machine a courant continu le moteur universel est-il une derivee directe ?", "options": ["Le moteur CC a excitation serie", "Le moteur CC à excitation shunt", "Le moteur CC independant", "Le moteur Brushless sans balais"], "rep": "Le moteur CC a excitation serie"},
        {"id": "q3", "q": "Quelle modification constructive indispensable lui permet d'accepter le courant alternatif ?", "options": ["Le feuilletage integral du stator et du rotor pour limiter les courants de Foucault", "L'utilisation exclusive d'aimants permanents en surface du rotor", "La suppression totale des balais et du collecteur mecanique", "L'adjonction d'un condensateur de dephasage haute tension"], "rep": "Le feuilletage integral du stator et du rotor pour limiter les courants de Foucault"},
        {"id": "q4", "q": "Quelle est la plage de vitesse de rotation typique de ce type de moteur ?", "options": ["Tres elevee, pouvant grimper de 10 000 a 20 000 tr/min", "Bridee rigoureusement a 1500 tr/min par la frequence", "Fixe et stable a 3000 tr/min sans aucune variation", "Tres basse, depassant rarement les 100 tr/min"], "rep": "Tres elevee, pouvant grimper de 10 000 a 20 000 tr/min"},
        {"id": "q5", "q": "Quel est l'inconvenient majeur du moteur universel dans l'habitat ?", "options": ["Il est tres bruyant et genere des parasites radioelectriques", "Son couple de demarrage est totalement nul", "Il refuse de fonctionner sur une prise de courant standard", "Il consomme exclusivement de l'energie reactive"], "rep": "Il est tres bruyant et genere des parasites radioelectriques"},
        {"id": "q6", "q": "Dans quel appareil menager de la maison retrouve-t-on massivement ce moteur ?", "options": ["Les aspirateurs, les mixeurs de cuisine et les perceuses filaires", "Les gros refrigerateurs de classe premium", "Les pompes de filtration des piscines exterieures", "Les horloges murales de haute precision"], "rep": "Les aspirateurs, les mixeurs de cuisine et les perceuses filaires"},
        {"id": "q7", "q": "Comment evolue sa vitesse lorsque l'effort resistant mecanique augmente ?", "options": ["La vitesse chute de maniere significative", "La vitesse reste strictement constante", "Le moteur s'accelere de maniere exponentielle", "L'arbre se bloque et change de sens"], "rep": "La vitesse chute de maniere significative"},
        {"id": "q8", "q": "Quelle est la piece d'usure principale qui necessite une maintenance ?", "options": ["Les balais de charbon frottant sur le collecteur", "Les aimants permanents qui se demagnetisent", "Le condensateur de dephasage auxiliaire", "La cage de cuivre moulee"], "rep": "Les balais de charbon frottant sur le collecteur"},
        {"id": "q9", "q": "Le moteur universel peut-il fonctionner sur une batterie de courant continu ?", "options": ["Oui, et il offre generalement un excellent rendement en CC", "Non, le courant continu detruirait ses enroulements", "Oui, mais uniquement si la batterie est triphasee", "Non, les balais bloqueraient le collecteur mecanique"], "rep": "Oui, et il offre generalement un excellent rendement en CC"},
        {"id": "q10", "q": "Pourquoi a-t-il ete invente au debut de l'ere de l'electrification ?", "options": ["Pour s'adapter aux differents reseaux électriques locaux (AC ou DC)", "Pour supprimer le besoin d'utiliser du fil de cuivre", "Pour remplacer la balancoire de Laplace dans les labos", "Pour fonctionner sans aucune carcasse metallique"], "rep": "Pour s'adapter aux differents reseaux électriques locaux (AC ou DC)"}
    ]
    if "ordre_quiz_tab15_aleatoire" not in st.session_state:
        random.shuffle(questions_t15)
        st.session_state.ordre_quiz_tab15_aleatoire = questions_t15

    champs_t15 = [
        ("1. Le moteur universel accepte le courant alternatif et le courant .........", ["Choisir...", "continu", "induit"], "continu", "t15_c1"),
        ("2. Sa structure s'apparente au modele a courant continu de type .........", ["Choisir...", "série", "shunt"], "serie", "t15_c2"),
        ("3. Le fer du stator est ......... pour tolerer les flux variables.", ["Choisir...", "feuilleté", "massif"], "feuillete", "t15_c3"),
        ("4. L'inversion simultanée des courants maintient le sens du .........", ["Choisir...", "couple", "glissement"], "couple", "t15_c4"),
        ("5. La vitesse de rotation de ce moteur est extremement .........", ["Choisir...", "élevée", "basse"], "elevee", "t15_c5"),
        ("6. Le collecteur mecanique frotte en permanence contre des .........", ["Choisir...", "balais", "bagues"], "balais", "t15_c6"),
        ("7. Les etincelles generees creent des perturbations radio.........", ["Choisir...", "électriques", "thermiques"], "electriques", "t15_c7"),
        ("8. Sous forte charge mecanique, sa vitesse de rotation .........", ["Choisir...", "chute", "augmente"], "chute", "t15_c8"),
        ("9. C'est le moteur typique de l'outillage ......... filaire.", ["Choisir...", "électroportatif", "lourd"], "electroportatif", "t15_c9"),
        ("10. Sa forte densite de couple au decollage permet de lancer les .........", ["Choisir...", "aspirateurs", "alternateurs"], "aspirateurs", "t15_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Universel (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab15_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t15_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Universel (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t15:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t15_h_{cle}", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_tab14(verrouille=False):
    questions_t14 = [
        {"id": "q1", "q": "De quoi est constitue le rotor d'un moteur a reluctance variable (SynRM) ?", "options": ["Uniquement d'un bloc de toles d'acier decoupe avec des barrieres d'air", "De bobines de cuivre vernies reliees a des bagues lisses", "D'aimants permanents colles en surface du cylindre", "D'une cage d'aluminium moulee en court-circuit"], "rep": "Uniquement d'un bloc de toles d'acier decoupe avec des barrieres d'air"},
        {"id": "q2", "q": "Quelle est la definition de la reluctance en physique des milieux magnetiques ?", "options": ["La resistance d'un circuit face au passage du flux magnetique", "La conductivite thermique globale de la carcasse de fonte", "Le dephasage angulaire provoque par le glissement de charge", "La force mecanique perpendiculaire donnee par la loi de Laplace"], "rep": "La resistance d'un circuit face au passage du flux magnetique"},
        {"id": "q3", "q": "Quel ingenieur et scientifique a formule les lois de cette machine au debut du XXe siecle ?", "options": ["J.K. Kostko", "Harry Nyquist", "Werner von Siemens", "Nikola Tesla"], "rep": "J.K. Kostko"},
        {"id": "q4", "q": "Comment le rotor parvient-il a se mettre en mouvement de rotation ?", "options": ["Il pivote spontanement pour offrir le chemin de moindre reluctance au flux du stator", "Il subit les forces induites de Foucault dans ses bobinages fermes", "Il est repousse par les aimants alternatifs situes dans le carter", "Il utilise le frottement mecanique des balais de charbon"], "rep": "Il pivote spontanement pour offer le chemin de moindre reluctance au flux du stator"},
        {"id": "q5", "q": "Quel est l'avantage du rotor SynRM concernant les pertes par effet Joule ?", "options": ["Le rotor ne comportant aucun conducteur, ses pertes Joule sont nulles", "Les pertes Joule sont divisees par la constante de Laplace", "Les pertes migrent integralement vers le variateur electronique", "Le rotor refroidit le stator par sa forme de turbine inductive"], "rep": "Le rotor ne comportant aucun conducteur, ses pertes Joule sont nulles"},
        {"id": "q6", "q": "Quelle classe de rendement ce moteur permet-il d'atteindre de facon standard ?", "options": ["IE5 (Ultra Premium)", "IE1 (Standard)", "IE2", "IE3"], "rep": "IE5 (Ultra Premium)"},
        {"id": "q7", "q": "Pourquoi la mise en oeuvre de ce moteur a-t-elle attendu la fin du XXe siecle ?", "options": ["Il exige des algorithmes de calcul complexes geres par des microcontroleurs", "La fabrication des toles d'acier etait interdite auparavant", "Le courant alternatif triphase n'existait pas à son invention", "Il demande obligatoirement un reseau electrique a tension continue"], "rep": "Il exige des algorithmes de calcul complexes geres par des microcontroleurs"},
        {"id": "q8", "q": "Le moteur à reluctance variable possede-t-il un glissement en marche stable ?", "options": ["Non, c'est une machine synchrone, son glissement est nul", "Oui, son glissement est identique au moteur asynchrone", "Oui, son glissement oscille entre 10% et 20%", "Non, son glissement depend de l'usure des balais"], "rep": "Non, c'est une machine synchrone, son glissement est nul"},
        {"id": "q9", "q": "Quel type d'enroulement equipe le stator d'une machine SynRM ?", "options": ["Un bobinage triphase alternatif classique identique a l'asynchrone", "Un enroulement inducteur alimente exclusivement en courant continu", "Une serie d'aimants permanents disposes en couronne fixe", "Des barres de cuivre massives en court-circuit permanent"], "rep": "Un bobinage triphase alternatif classique identique a l'asynchrone"},
        {"id": "q10", "q": "Quel est son interet ecologique majeur face au moteur PMSM ?", "options": ["Il atteint de tres hauts rendements sans utiliser de terres rares", "Il ne consomme absolument aucune puissance active sur la ligne", "Il recycle l'energie thermique emise par les roulements", "Il fonctionne sans aucun lubrifiant ni carcasse de fonte"], "rep": "Il atteint de tres hauts rendements sans utiliser de terres rares"}
    ]
    if "ordre_quiz_tab14_aleatoire" not in st.session_state:
        random.shuffle(questions_t14)
        st.session_state.ordre_quiz_tab14_aleatoire = questions_t14

    champs_t14 = [
        ("1. Le rotor du moteur SynRM est depourvu d'aimants et de .........", ["Choisir...", "bobinages", "toles"], "bobinages", "t14_c1"),
        ("2. La reluctance designe la resistance opposée au flux .........", ["Choisir...", "magnetique", "electrique"], "magnetique", "t14_c2"),
        ("3. Le rotor privilegie l'axe offrant la permeabilite la plus .........", ["Choisir...", "grande", "petite"], "grande", "t14_c3"),
        ("4. Les decoupes geometriques effectuees creent des barrieres d'.........", ["Choisir...", "air", "cuivre"], "air", "t14_c4"),
        ("5. Le moteur a reluctance se classe parmi les machines .........", ["Choisir...", "synchrones", "asynchrones"], "synchrones", "t14_c5"),
        ("6. L'absence d'echauffement au rotor preserve la duree de vie des .........", ["Choisir...", "roulements", "phases"], "roulements", "t14_c6"),
        ("7. Le pilotage requiert l'usage obligatoire d'un ......... de vitesse.", ["Choisir...", "variateur", "rheostat"], "variateur", "t14_c7"),
        ("8. Il represente une alternative economique face aux aimants en terres .........", ["Choisir...", "rares", "cuivrees"], "rares", "t14_c8"),
        ("9. Le rendement de cette technologie atteint la norme energetique .........", ["Choisir...", "IE5", "IE1"], "IE5", "t14_c9"),
        ("10. On le retrouve beaucoup dans les entraînements de ......... industrielles.", ["Choisir...", "pompes", "drones"], "pompes", "t14_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Synchrone Reluctance (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab14_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t14_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Synchrone Reluctance (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t14:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t14_h_{cle}", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_tab13(verrouille=False):
    questions_t13 = [
        {"id": "q1", "q": "Comment remplace-t-on la source de flux magnetique du rotor sur ce moteur ?", "options": ["Par des electroaimants bobines alimentes en courant continu", "Par des barres conductrices d'aluminium en court-circuit", "Par des aimants permanents en alliage de neodyme", "Par un bloc de fer decoupe exploitant l'air"], "rep": "Par des electroaimants bobines alimentes en courant continu"},
        {"id": "q2", "q": "Quel constructeur automobile utilise massivement cette technologie sur ses voitures ?", "options": ["Renault (moteurs de la Zoe et de la Megane E-Tech)", "Tesla (tous les modèles)", "Toyota (hybrides)", "Nissan"], "rep": "Renault (moteurs de la Zoe et de la Megane E-Tech)"},
        {"id": "q3", "q": "Quel est l'avantage strategique majeur de s'affranchir des aimants permanents ?", "options": ["Eviter l'usage de terres rares couteuses et soumises a des monopoles", "Pouvoir supprimer completement l'onduleur de commande", "Diviser par deux l'intensite absorbée au stator", "Annuler completement les pertes fer du stator"], "rep": "Eviter l'usage de terres rares couteuses et soumises a des monopoles"},
        {"id": "q4", "q": "Par quel biais le courant d'excitation continu arrive-t-il au rotor tournant ?", "options": ["Des bagues lisses associees à des balais frotteurs", "Un collecteur a lames de cuivre sectorise", "Un systeme d'induction sans fil haute frequence", "Directement par les roulements a billes lubrifies"], "rep": "Des bagues lisses associees à des balais frotteurs"},
        {"id": "q5", "q": "Quelle opportunite offre le controle en temps reel du courant d'excitation ?", "options": ["Ajuster l'aimantation pour optimiser le rendement a haute vitesse", "Modifier le nombre de poles de la machine en marche", "Inverser le sens de rotation sans toucher au stator", "Supprimer le besoin de ventilation de la carcasse"], "rep": "Ajuster l'aimantation pour optimiser le rendement a haute vitesse"},
        {"id": "q6", "q": "En mode alternateur dans les centrales, cette machine synchrone convertit :", "options": ["L'energie mecanique de la turbine en puissance electrique", "Le courant continu de ligne en courant alternatif fixe", "L'energie thermique directe en flux magnetique", "Le glissement du reseau en puissance reactive"], "rep": "L'energie mecanique de la turbine en puissance electrique"},
        {"id": "q7", "q": "Comment appelle-t-on le regime ou la machine fournit du reactif au reseau ?", "options": ["Regime de compensateur synchrone (sur-excitation)", "Regime de sous-excitation lineaire", "Regime de decollage asynchrone", "Regime de reluctance nominale"], "rep": "Regime de compensateur synchrone (sur-excitation)"},
        {"id": "q8", "q": "Quel est le point faible mecanique lie a la presence des bagues et balais ?", "options": ["Une maintenance periodique liee a l'usure des charbons", "Une chute brutale de la force de Laplace a basse tension", "Une impossibilite d'inverser le sens de rotation de l'arbre", "Une augmentation lineaire du taux de glissement"], "rep": "Une maintenance periodique liee a l'usure des charbons"},
        {"id": "q9", "q": "La vitesse de rotation de cette machine depend-elle de la charge ?", "options": ["Non, elle reste fixee sur le synchronisme de la frequence", "Oui, elle s'effondre des que le couple double", "Oui, elle augmente avec la demande mecanique", "Non, elle depend exclusivement de la tension continue"], "rep": "Non, elle reste fixee sur le synchronisme de la frequence"},
        {"id": "q10", "q": "A haute vitesse sur autoroute, reduire le courant d'excitation permet de :", "options": ["Reduire la f.c.e.m. pour conserver un bon rendement sans saturer", "Bloquer instantanement le rotor pour freiner le vehicule", "Augmenter l'intensite nominale du stator au-dela des limites", "Passer en mode moteur asynchrone a cage d'ecureuil"], "rep": "Reduire la f.c.e.m. pour conserver un bon rendement sans saturer"}
    ]
    if "ordre_quiz_tab13_aleatoire" not in st.session_state:
        random.shuffle(questions_t13)
        st.session_state.ordre_quiz_tab13_aleatoire = questions_t13

    champs_t13 = [
        ("1. Le rotor bobine d'un moteur synchrone fait office d'......... ajustable.", ["Choisir...", "electroaimant", "induit"], "electroaimant", "t13_c1"),
        ("2. Le courant injecte dans le rotor est un courant .........", ["Choisir...", "continu", "alternatif"], "continu", "t13_c2"),
        ("3. L'amenée du courant s'effectue par des balais et des ......... lisses.", ["Choisir...", "bagues", "lames"], "bagues", "t13_c3"),
        ("4. Cette solution technique permet de fabriquer un moteur sans terres .........", ["Choisir...", "rares", "cuivrees"], "rares", "t13_c4"),
        ("5. Ajuster le flux permet de maximiser le ......... a haute vitesse.", ["Choisir...", "rendement", "glissement"], "rendement", "t13_c5"),
        ("6. Dans les centrales electriques, cette machine s'appelle un .........", ["Choisir...", "alternateur", "onduleur"], "alternateur", "t13_c6"),
        ("7. Un moteur synchrone sur-excite fournit de l'energie ......... au reseau.", ["Choisir...", "reactive", "active"], "reactive", "t13_c7"),
        ("8. Contrairement au PMSM, ce rotor subit des pertes par effet .........", ["Choisir...", "Joule", "Laplace"], "Joule", "t13_c8"),
        ("9. La vitesse de rotation reste parfaitement verrouillee sur le .........", ["Choisir...", "synchronisme", "glissement"], "synchronisme", "t13_c9"),
        ("10. L'usure des charbons demande un suivi et un entretien .........", ["Choisir...", "regulier", "nul"], "regulier", "t13_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Synchrone Bobine (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab13_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t13_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Synchrone Bobine (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t13:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t13_h_{cle}", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_tab12(verrouille=False):
    questions_t12 = [
        {"id": "q1", "q": "Quelle est la valeur du glissement sur un moteur synchrone en regime etabli ?", "options": ["Rigoureusement nulle", "Variable entre 2% et 5%", "Proche de 50%", "Dependante uniquement du couple resistant"], "rep": "Rigoureusement nulle"},
        {"id": "q2", "q": "Quelle formule dicte la vitesse synchrone de rotation de l'arbre ?", "options": ["N = f / p", "N = U * I", "N = P / C", "N = f * p"], "rep": "N = f / p"},
        {"id": "q3", "q": "De quel materiau sont faits les aimants de ces machines de haute densite ?", "options": ["Des terres rares (Neodyme-Fer-Bore)", "De la ferrite pure frittee", "De l'aluminium brute brosse", "De l'acier inoxydable de carbone"], "rep": "Des terres rares (Neodyme-Fer-Bore)"},
        {"id": "q4", "q": "Pourquoi ce moteur ne peut-il pas demarrer directement sur un reseau alternatif fixe ?", "options": ["L'inertie du rotor l'empeche de s'accrocher instantanement au champ tournant rapide", "Le bobinage du stator fondrait immediatement sous l'effet du courant", "Les aimants permanents repoussent les frequences de 50 Hz", "La tension de ligne inverserait les poles de maniere definitive"], "rep": "L'inertie du rotor l'empeche de s'accrocher instantanement au champ tournant rapide"},
        {"id": "q5", "q": "Quel equipement d'electronique de puissance est obligatoire pour piloter ce moteur ?", "options": ["Un onduleur de tension ou variateur de vitesse", "Un gradateur monophase a triacs", "Un rheostat de demarrage triphase", "Un condensateur de dephasage serie"], "rep": "Un onduleur de tension ou variateur de vitesse"},
        {"id": "q6", "q": "Quel est le principal avantage du PMSM face au moteur asynchrone ?", "options": ["Une densite de puissance maximale et un excellent rendement", "Un coût de fabrication extremement bas", "La possibilite de se passer d'electronique de commande", "Un couple qui augmente au carre du courant de ligne"], "rep": "Une densite de puissance maximale et un excellent rendement"},
        {"id": "q7", "q": "Comment appelle-t-on la f.e.m. generee lorsque le moteur tourne a haute vitesse ?", "options": ["La force contre-electromotrice (f.c.e.m.)", "La force de Laplace induite", "Le flux de reluctance minimal", "L'inductance de fuite"], "rep": "La force contre-electromotrice (f.c.e.m.)"},
        {"id": "q8", "q": "Ou sont positionnes les aimants permanents dans la structure PMSM standard ?", "options": ["Sur ou inserts dans le rotor mobile", "Repartis le long des encoches du stator", "A l'interieur des balais de charbon", "Sur la plaque a bornes de couplage"], "rep": "Sur ou inserts dans le rotor mobile"},
        {"id": "q9", "q": "Dans quel domaine d'actualite ce moteur est-il la reference incontournable ?", "options": ["La propulsion des vehicules electriques et hybrides", "L'outillage de bricolage grand public", "Les petits ventilateurs domestiques fixes", "Les broyeurs lourds des cimenteries"], "rep": "La propulsion des vehicules electriques et hybrides"},
        {"id": "q10", "q": "Quel est l'inconvenient economique majeur de ce type de motorisation ?", "options": ["Le coût eleve et la dependance geopolitique lies aux terres rares", "L'obligation d'un entretien quotidien des contacts", "Un encombrement de carter superieur a l'asynchrone", "Une instabilite totale de la vitesse sous charge"], "rep": "Le coût eleve et la dependance geopolitique lies aux terres rares"}
    ]
    if "ordre_quiz_tab12_aleatoire" not in st.session_state:
        random.shuffle(questions_t12)
        st.session_state.ordre_quiz_tab12_aleatoire = questions_t12

    champs_t12 = [
        ("1. Le moteur synchrone a aimants possede un glissement strictement .........", ["Choisir...", "nul", "variable"], "nul", "t12_c1"),
        ("2. Le rotor s'accroche de maniere rigide sur la vitesse du ......... tournant.", ["Choisir...", "champ", "balai"], "champ", "t12_c2"),
        ("3. La vitesse mecanique est directement liee a la ......... de l'onduleur.", ["Choisir...", "frequence", "resistance"], "frequence", "t12_c3"),
        ("4. Les aimants haut de gamme utilisent des materiaux dits terres .........", ["Choisir...", "rares", "cuivrees"], "rares", "t12_c4"),
        ("5. Cette technologie offre un ratio couple/poids extremement .........", ["Choisir...", "eleve", "faible"], "eleve", "t12_c5"),
        ("6. Sans variateur electronique, le demarrage sur secteur est .........", ["Choisir...", "impossible", "facile"], "impossible", "t12_c6"),
        ("7. Le rendement energetique global de ces machines frole les .........", ["Choisir...", "95%", "60%"], "95%", "t12_c7"),
        ("8. Le rotor ne contenant pas d'enroulements, il ne subit pas de pertes .........", ["Choisir...", "Joule", "Laplace"], "Joule", "t12_c8"),
        ("9. C'est le moteur privilegie pour la robotique et l'......... moderne.", ["Choisir...", "automobile", "sidérurgie"], "automobile", "t12_c9"),
        ("10. Le nombre de paires de poles de la machine est note .........", ["Choisir...", "p", "f"], "p", "t12_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Synchrone Aimants (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab12_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t12_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Synchrone Aimants (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t12:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t12_h_{cle}", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_tab11(verrouille=False):
    questions_t11 = [
        {"id": "q1", "q": "Pourquoi un moteur asynchrone alimente par une seule phase alternative ne peut-il pas demarrer seul ?", "options": ["Son champ magnetique initial est purement pulsant rectiligne et non tournant", "La tension de 230V est physiquement insuffisante pour vaincre l'inertie du rotor", "Le courant alternatif monophase detruit instantanement le fer de la culasse", "La cage d'ecureuil rejette les flux qui ne proviennent pas d'un reseau triphase"], "rep": "Son champ magnetique initial est purement pulsant rectiligne et non tournant"},
        {"id": "q2", "q": "Quel composant auxiliaire est indispensable pour generer le dephasage necessaire au decollage ?", "options": ["Un condensateur de dephasage", "Un rheostat a curseur lineaire", "Un pont de diodes redresseur", "Un hacheur de tension serie"], "rep": "Un condensateur de dephasage"},
        {"id": "q3", "q": "Comment qualifie-t-on le deuxieme enroulement integre au stator de ce moteur ?", "options": ["L'enroulement auxiliaire (ou de demarrage)", "L'enroulement shunt d'auto-regulation", "L'enroulement de compensation thermique", "L'enroulement d'excitation continue"], "rep": "L'enroulement auxiliaire (ou de demarrage)"},
        {"id": "q4", "q": "Quel est le dephasage electrique ideal recherche entre l'enroulement principal et l'enroulement de demarrage ?", "options": ["90 degres", "120 degres", "180 degres", "0 degre"], "rep": "90 degres"},
        {"id": "q5", "q": "Que se passe-t-il si le condensateur de demarrage devient defectueux ou claque ?", "options": ["Le moteur grogne et vibre sur place sans reussir a s'elancer tout seul", "Le moteur s'emballe de maniere destructive vers les hautes vitesses", "La machine bascule instantanement en courant continu de securite", "Le sens de rotation de l'arbre s'inverse de maniere aleatoire"], "rep": "Le moteur grogne et vibre sur place sans reussir a s'elancer tout seul"},
        {"id": "q6", "q": "Quelle action permet de lancer un moteur monophase dont le condensateur est debranche ?", "options": ["Donner une impulsion mecanique manuelle dans n'importe quel sens", "Augmenter brusquement la tension d'alimentation en ligne", "Inverser les fils de phase et de neutre du bornier", "Court-circuiter l'enroulement auxiliaire directement"], "rep": "Donner une impulsion mecanique manuelle dans n'importe quel sens"},
        {"id": "q7", "q": "Quel systeme mecanique interne coupe parfois l'enroulement auxiliaire une fois la vitesse atteinte ?", "options": ["Un coupleur ou contacteur centrifuge", "Un collecteur a lames de cuivre sectorise", "Un potentiometre de puissance", "Un disjoncteur magneto-thermique"], "rep": "Un coupleur ou contacteur centrifuge"},
        {"id": "q8", "q": "Quelle est la principale limitation d'un moteur asynchrone monophase par rapport au modele triphase ?", "options": ["Un couple de demarrage plus faible et un rendement global modeste", "Une impossibilite absolue de changer son sens de rotation", "Une sensibilite extreme aux variations de temperature", "Une obligation d'utiliser des aimants permanents couteux"], "rep": "Un couple de demarrage plus faible et un rendement global modeste"},
        {"id": "q9", "q": "Dans quel type d'application grand public retrouve-t-on massivement ce moteur ?", "options": ["Les pompes de piscine, les refrigerateurs et les betonnières", "La propulsion des voitures electriques de grande serie", "Les lignes de TGV et la traction ferroviaire lourde", "La robotique industrielle et les bras articules"], "rep": "Les pompes de piscine, les refrigerateurs et les betonnières"},
        {"id": "q10", "q": "Comment inverse-t-on de maniere permanente le sens de rotation de ce moteur ?", "options": ["En inversant les connexions de l'enroulement auxiliaire par rapport au principal", "En inversant simplement la fiche de la prise electrique murale", "En changeant la valeur en microfarads du condensateur", "En supprimant completement le circuit de dephasage auxiliaire"], "rep": "En inversant les connexions de l'enroulement auxiliaire par rapport au principal"}
    ]
    if "ordre_quiz_tab11_aleatoire" not in st.session_state:
        random.shuffle(questions_t11)
        st.session_state.ordre_quiz_tab11_aleatoire = questions_t11

    champs_t11 = [
        ("1. Le moteur asynchrone monophasé s'alimente sur le réseau domestique à deux .........", ["Choisir...", "fils", "phases"], "fils", "t11_c1"),
        ("2. Une seule phase alternative produit un champ magnétique qualifié de .........", ["Choisir...", "pulsant", "tournant"], "pulsant", "t11_c2"),
        ("3. Ce type de champ possède un couple initial de démarrage rigoureusement .........", ["Choisir...", "nul", "important"], "nul", "t11_c3"),
        ("4. Pour créer le champ tournant indispensable, on intègre un deuxième .........", ["Choisir...", "bobinage", "collecteur"], "bobinage", "t11_c4"),
        ("5. Le condensateur est branché en série avec l'enroulement .........", ["Choisir...", "auxiliaire", "principal"], "auxiliaire", "t11_c5"),
        ("6. Sa présence permet de décaler le courant pour simuler une deuxième .........", ["Choisir...", "phase", "tension"], "phase", "t11_c6"),
        ("7. La valeur de ce composant de déphasage s'exprime en .........", ["Choisir...", "microfarads", "millihenrys"], "microfarads", "t11_c7"),
        ("8. Si le moteur ne démarre pas et émet un bruit sourd, il s'agit d'un .........", ["Choisir...", "grognement", "sifflement"], "grognement", "t11_c8"),
        ("9. Le rendement de ces machines domestiques dépasse rarement les .........", ["Choisir...", "75%", "95%"], "75%", "t11_c9"),
        ("10. Ce moteur est parfait pour l'équipement de la ......... et du jardin.", ["Choisir...", "maison", "sidérurgie"], "maison", "t11_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Asynchrone Monophase (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab11_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t11_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse Moteur Asynchrone Monophasé (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t11:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t11_h_{cle}", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_tab10(verrouille=False):
    questions_t10 = [
        {"id": "q1", "q": "Quelle est la principale difference physique au rotor par rapport a la cage d'ecureuil ?", "options": ["Le rotor comporte de vrais bobinages triphases accessibles de l'exterieur", "Le rotor est un bloc d'acier massif monobloc sans conducteurs", "Le rotor integre des aimants permanents au neodyme alternes", "Le rotor est alimente de facon constante en haute tension continue"], "rep": "Le rotor comporte de vrais bobinages triphases accessibles de l'exterieur"},
        {"id": "q2", "q": "Par quel intermediaire mecanique les bobinages du rotor sont-ils relies au circuit externe ?", "options": ["Des bagues lisses rotatives frottant contre des balais fixes", "Un collecteur a lames de cuivre sectorise", "Un systeme d'embrayage centrifuge a billes", "Un transformateur tournant haute frequence sans contact"], "rep": "Des bagues lisses rotatives frottant contre des balais fixes"},
        {"id": "q3", "q": "Quel etait l'objectif technique historique de cette configuration pre-electronique ?", "options": ["Modifier les caracteristiques de demarrage sous forte charge", "Supprimer definitivement l'echauffement du stator", "Fonctionner exclusivement sur des réseaux monophases", "Annuler completement le glissement fonctionnel"], "rep": "Modifier les caracteristiques de demarrage sous forte charge"},
        {"id": "q4", "q": "Qu'insere-t-on temporairement en serie avec le rotor lors de la phase de decollage ?", "options": ["Un banc de resistances triphasees variable nomme rheostat", "Des condensateurs de dephasage haute tension", "Des diodes de redressement de puissance", "Des transformateurs de ligne adaptateurs de tension"], "rep": "Un banc de resistances triphasees variable nomme rheostat"},
        {"id": "q5", "q": "Quel est l'effet direct de l'augmentation de la resistance rotorique sur le courant de demarrage ?", "options": ["Il diminue fortement le pic de courant au stator sur le reseau", "Il augmente l'intensite de ligne au-dela du nominal", "Il bloque instantanement la circulation du flux inducteur", "Il force le courant a devenir purement reactif"], "rep": "Il diminue fortement le pic de courant au stator sur le reseau"},
        {"id": "q6", "q": "Comment evolue le couple de demarrage lorsqu'on insere la bonne valeur de resistance externe ?", "options": ["Il augmente significativement pour atteindre son maximum au decollage", "Il s'effondre immediatement jusqu'a devenir totalement nul", "Il reste identique et rigoureusement invariant", "Il devient oscillant et genere de violents coups de belier"], "rep": "Il augmente significativement pour atteindre son maximum au decollage"},
        {"id": "q7", "q": "Quelle est la valeur de la resistance externe lorsque le moteur tourne en regime normal stable ?", "options": ["Elle est nulle car le rotor est court-circuite", "Elle est maximale pour limiter l'echauffement", "Elle oscille selon la charge mecanique", "Elle est deconnectee ouvrant le circuit"], "rep": "Elle est nulle car le rotor est court-circuite"},
        {"id": "q8", "q": "Quel inconvenient majeur presentent les balais sur ce type de moteur ?", "options": ["Ils s'usent par frottement et generent de la poussiere de carbone", "Ils augmentent de maniere excessive le glissement nominal", "Ils forcent la machine a s'arreter toutes les heures", "Ils annulent le champ magnetique statorique"], "rep": "Ils s'usent par frottement et generent de la poussiere de carbone"},
        {"id": "q9", "q": "Dans quelle application industrielle lourde ce moteur etait-il indispensable ?", "options": ["Les ponts roulants, grues et broyeurs de forte puissance", "Les petits ventilateurs d'ordinateurs personnels", "Les systemes de positionnement de robotique fine", "L'outillage electroportatif de bricolage"], "rep": "Les ponts roulants, grues et broyeurs de forte puissance"},
        {"id": "q10", "q": "Qu'est-ce qui a cause l'obsolescence de ce moteur dans l'industrie moderne ?", "options": ["La generalisation des variateurs de frequence electroniques", "L'interdiction de l'utilisation du cuivre pour les rotors", "L'obligation d'utiliser des reseaux en courant continu", "L'inefficacite totale de son circuit magnetique"], "rep": "La generalisation des variateurs de frequence electroniques"}
    ]
    if "ordre_quiz_tab10_aleatoire" not in st.session_state:
        random.shuffle(questions_t10)
        st.session_state.ordre_quiz_tab10_aleatoire = questions_t10

    champs_t10 = [
        ("1. Le moteur asynchrone a rotor bobine est egalement appele moteur a .........", ["Choisir...", "bagues", "collecteur"], "bagues", "t10_c1"),
        ("2. Les enroulements du rotor sont connectes a un circuit exterieur variable de .........", ["Choisir...", "resistances", "condensateurs"], "resistances", "t10_c2"),
        ("3. L'ensemble externe utilise pour ajuster ces valeurs est un .........", ["Choisir...", "rheostat", "hacheur"], "rheostat", "t10_c3"),
        ("4. Augmenter la resistance au demarrage permet de limiter l'......... de ligne.", ["Choisir...", "intensite", "tension"], "intensite", "t10_c4"),
        ("5. Cette methode de controle ameliore nettement le ......... de demarrage.", ["Choisir...", "couple", "glissement"], "couple", "t10_c5"),
        ("6. Lorsque le moteur atteint sa vitesse stable, le rheostat est mis en .........", ["Choisir...", "court-circuit", "circuit ouvert"], "court-circuit", "t10_c6"),
        ("7. En marche normale court-circuitee, le moteur se comporte comme un modele a .........", ["Choisir...", "cage", "aimants"], "cage", "t10_c7"),
        ("8. Les frottements au niveau des balais generent des pertes mecaniques et de la .........", ["Choisir...", "poussiere", "tension"], "poussiere", "t10_c8"),
        ("9. Cette technologie lourde etait incontournable sur les gros ponts .........", ["Choisir...", "roulants", "statiques"], "roulants", "t10_c9"),
        ("10. L'arrivee des variateurs de ......... a rendu ce systeme obsolete.", ["Choisir...", "frequence", "tension"], "frequence", "t10_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Asynchrone Bagues (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab10_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t10_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthese Moteur Asynchrone Bagues (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t10:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t10_h_{cle}", disabled=verrouille, label_visibility="collapsed")

with tab10:
    st.header("Moteur Asynchrone a Rotor Bobine (Bagues)")
    st.markdown("""
    * **Definition :** Le moteur asynchrone a rotor bobine est une variante de machine a induction ou les enroulements du rotor ne sont pas relies en court-circuit permanent interne, mais debouchent sur trois bagues lisses rotatives frottant contre des balais fixes afin d'y inserer des resistances de reglage externes.
    * **Historique et Personnages :** Developpe intensivement par les ingenieurs industriels de la fin du XIXe siecle (dont les equipes associees aux reseaux triphases de Mikhail Dolivo-Dobrovolsky) pour repondre aux defauts de demarrage direct des fortes puissances.
    * **Fonctionnement detaille :** Le stator triphase genere un champ magnetique tournant synchrone. Au demarrage, l'insertion d'un rheostat en serie avec le rotor augmente sa resistance apparente, ce qui decale la phase du courant rotorique induit. Ce mecanisme ecrase l'appel de courant destructeur sur le reseau electrique tout en deplaçant le couple maximal au moment exact du decollage.
    """)
    st.image("https://unsplash.com", caption="Maintenance et controle des enroulements de cuivre d'un rotor bobine (Format JPG)", use_container_width=True)
    
    st.subheader("Atelier virtuel : Insertion du rheostat et impact sur la ligne")
    rheostat_val = st.slider("Resistance du rheostat externe connectee au rotor (Ohms)", min_value=0, max_value=100, value=80, key="r_t10_sim")
    courant_dem = 500 - (rheostat_val * 4)
    couple_ini = 50 + (rheostat_val * 1.5) if rheostat_val < 70 else 155 - (rheostat_val - 70) * 2 # Courbe de couple simplifiee
    
    st.metric("Pic de courant au demarrage sur la ligne", f"{courant_dem} A")
    st.metric("Couple initial de decollage estime", f"{couple_ini:.1f} Nm")
    st.write("Observation : L'ajout de resistance ecrase l'intensite de ligne au demarrage et deplace le point de couple maximal.")
    
    # Appel de l'atelier de 10 questions et 10 trous specifiques
    afficher_atelier_tab10()
    
    # Bouton d'exportation de l'onglet
    contenu_tab10 = f"Moteur Asynchrone Bagues - Resistance rheostat choisie : {rheostat_val} Ohms, Courant calcule : {courant_dem} A"
    st.download_button("Exporter le rapport AC_Asynchrone_Bobine", contenu_tab10, file_name=preparer_nom_fichier("AC_Asynchrone_Bobine"))


def afficher_atelier_tab9(verrouille=False):
    questions_t9 = [
        {"id": "q1", "q": "Quelle proportion approximative du parc mondial de moteurs industriels cette technologie représente-t-elle ?", "options": ["Environ 80%", "Moins de 20%", "Exactement 50%", "Près de 99%"], "rep": "Environ 80%"},
        {"id": "q2", "q": "Quel ingénieur a inventé et breveté le premier rotor à cage d'écureuil triphasé en 1889 ?", "options": ["Mikhail Dolivo-Dobrovolsky", "Nikola Tesla", "Michael Faraday", "Thomas Edison"], "rep": "Mikhail Dolivo-Dobrovolsky"},
        {"id": "q3", "q": "Qu'est-ce que le phénomène de glissement dans un moteur asynchrone ?", "options": ["L'écart de vitesse entre le champ tournant du stator et le rotor", "La perte par friction mécanique au niveau des roulements à billes", "Le retard électrique provoqué par l'inductance résiduelle", "Le patinage de l'arbre mécanique sous une surcharge"], "rep": "L'écart de vitesse entre le champ tournant du stator et le rotor"},
        {"id": "q4", "q": "De quoi est constitué structurellement un rotor à cage d'écureuil ?", "options": ["De barres conductrices en court-circuit permanent aux extrémités", "De bobinages de fils fins reliés à un collecteur mécanique", "D'aimants permanents disposés de manière alternée", "De tôles d'acier découpées sans aucun élément conducteur"], "rep": "De barres conductrices en court-circuit permanent aux extrémités"},
        {"id": "q5", "q": "Comment évolue le taux de glissement lorsque la charge mécanique sur l'arbre augmente ?", "options": ["Le glissement augmente pour induire plus de courant au rotor", "Le glissement diminue jusqu'à devenir parfaitement nul", "Le glissement reste rigoureusement fixe et invariant", "Le glissement s'inverse et change le sens du moteur"], "rep": "Le glissement augmente pour induire plus de courant au rotor"},
        {"id": "q6", "q": "Quelle est la vitesse théorique maximale (synchronisme) d'un moteur à 4 pôles alimenté en 50 Hz ?", "options": ["1500 tr/min", "3000 tr/min", "1000 tr/min", "750 tr/min"], "rep": "1500 tr/min"},
        {"id": "q7", "q": "Quel est le principal avantage de la cage d'écureuil par rapport aux moteurs CC ?", "options": ["L'absence totale de pièces d'usure mécanique comme les balais", "Un couple de démarrage qui surpasse le moteur série", "Une vitesse rigoureusement indépendante de la fréquence", "La possibilité de fonctionner sans électronique ni réseau"], "rep": "L'absence totale de pièces d'usure mécanique comme les balais"},
        {"id": "q8", "q": "Qu'engendre la circulation du champ tournant du stator à travers le rotor ?", "options": ["La création de courants induits et de forces de Laplace", "Une démagnétisation complète des tôles d'acier", "Un blocage magnétique instantané par réluctance", "Une transformation de la fréquence du réseau de ligne"], "rep": "La création de courants induits et de forces de Laplace"},
        {"id": "q9", "q": "Quelle est la valeur typique du glissement d'un moteur industriel en régime nominal ?", "options": ["Entre 2% et 6%", "Exactement 0%", "Plus de 25%", "Entre 10% et 15%"], "rep": "Entre 2% et 6%"},
        {"id": "q10", "q": "Quel équipement moderne associe-t-on systématiquement pour faire varier sa vitesse ?", "options": ["Un variateur de fréquence (VDF)", "Un hacheur série à transistors", "Un rhéostat de démarrage à bagues", "Un condensateur de déphasage permanent"], "rep": "Un variateur de fréquence (VDF)"}
    ]
    if "ordre_quiz_tab9_aleatoire" not in st.session_state:
        random.shuffle(questions_t9)
        st.session_state.ordre_quiz_tab9_aleatoire = questions_t9

    champs_t9 = [
        ("1. Le stator alimenté par un réseau triphasé génère un champ .........", ["Choisir...", "tournant", "fixe"], "tournant", "t9_c1"),
        ("2. Le rotor tourne toujours à une vitesse ......... à celle du synchronisme.", ["Choisir...", "inférieure", "égale"], "inférieure", "t9_c2"),
        ("3. Le décalage obligatoire entre ces vitesses s'appelle le .........", ["Choisir...", "glissement", "pas"], "glissement", "t9_c3"),
        ("4. Les barres du rotor sont connectées par des anneaux de .........", ["Choisir...", "court-circuit", "connexion"], "court-circuit", "t9_c4"),
        ("5. Les courants créés à l'intérieur de la cage sont des courants de .........", ["Choisir...", "Foucault", "Laplace"], "Foucault", "t9_c5"),
        ("6. La robustesse de ce moteur s'explique par l'absence de .........", ["Choisir...", "contacts", "bobines"], "contacts", "t9_c6"),
        ("7. Au démarrage direct, ce moteur génère un fort appel de .........", ["Choisir...", "courant", "flux"], "courant", "t9_c7"),
        ("8. Pour limiter cet appel de courant historique, on utilisait un démarreur étoile-.........", ["Choisir...", "triangle", "série"], "triangle", "t9_c8"),
        ("9. Le moteur asynchrone absorbe de l'énergie réactive pour créer son .........", ["Choisir...", "champ", "couple"], "champ", "t9_c9"),
        ("10. C'est la véritable bête de somme incontournable de l'......... moderne.", ["Choisir...", "industrie", "domotique"], "industrie", "t9_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Moteur Asynchrone Cage (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab9_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t9_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse Moteur Asynchrone Cage (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t9:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t9_h_{cle}", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_tab8(verrouille=False):
    questions_t8 = [
        {"id": "q1", "q": "Qu'est-ce qui remplace le commutateur mécanique (balais/collecteur) du moteur Brushless ?", "options": ["Une commutation électronique gérée par un driver/onduleur", "Un embrayage centrifuge lubrifié", "Un condensateur de déphasage d'induit", "Un système de bagues lisses en bronze"], "rep": "Une commutation électronique gérée par un driver/onduleur"},
        {"id": "q2", "q": "Où migrent les aimants permanents inducteurs dans un moteur Brushless ?", "options": ["Sur le rotor mobile", "Sur le stator fixe encastré", "Au sein des têtes de balais", "Dans la carte de contrôle externe"], "rep": "Sur le rotor mobile"},
        {"id": "q3", "q": "Quels inventeurs ont jeté les bases du moteur synchrone auto-commuté au XXe siècle ?", "options": ["T.G. Wilson et P.H. Trickey", "Nikola Tesla et Westinghouse", "Thomas Edison et Davenport", "Hans Christian Orsted"], "rep": "T.G. Wilson et P.H. Trickey"},
        {"id": "q4", "q": "Quels capteurs magnétiques internes informent le driver de l'orientation exacte du rotor ?", "options": ["Des capteurs à effet Hall", "Des couples de thermocouples", "Des jauges piézoélectriques", "Des capteurs capacitifs d'air"], "rep": "Des capteurs à effet Hall"},
        {"id": "q5", "q": "Quel avantage découle de la suppression complète des charbons mécaniques ?", "options": ["Aucun entretien, pas d'étincelles et durée de vie accrue", "Alimentation directe sur prise monophasée 230V sans adaptateur", "Suppression totale de tout circuit ferromagnétique", "Évanouissement du champ rémanent de l'induit"], "rep": "Aucun entretien, pas d'étincelles et durée de vie accrue"},
        {"id": "q6", "q": "Quelle est la forme d'onde courante de la force contre-électromotrice d'un moteur BLDC ?", "options": ["Trapézoïdale ou sinusoïdale", "Carrée pure à 100% de rapport cyclique", "Dent de scie asymétrique", "Impulsionnelle logarithmique"], "rep": "Trapézoïdale ou sinusoïdale"},
        {"id": "q7", "q": "Pourquoi le moteur Brushless affiche-t-il une densité de puissance exceptionnelle ?", "options": ["Car les aimants en terres rares génèrent un flux immense pour un faible poids", "Car il ne produit aucun dégagement thermique par effet Joule", "Car il tourne obligatoirement à la fréquence du réseau de 50Hz", "Car sa structure élimine le besoin d'un arbre d'entraînement"], "rep": "Car les aimants en terres rares génèrent un flux immense pour un faible poids"},
        {"id": "q8", "q": "Une application de prédilection des petits moteurs Brushless rapides est :", "options": ["Les drones de loisir et l'outillage sans fil haut de gamme", "Les aspirateurs industriels filaires d'usine", "Les démarreurs lourds de camions diesel", "Les horloges de précision comtoises"], "rep": "Les drones de loisir et l'outillage sans fil haut de gamme"},
        {"id": "q9", "q": "Sans son contrôleur électronique externe (ESC/Driver), le moteur Brushless :", "options": ["Ne peut absolument pas tourner et reste bloqué", "Tourne à sa vitesse maximale de synchronisme", "Consomme uniquement du courant réactif", "Fonctionne comme un moteur shunt classique"], "rep": "Ne peut absolument pas tourner et reste bloqué"},
        {"id": "q10", "q": "La vitesse de rotation angulaire d'un moteur Brushless est directement asservie à :", "options": ["La fréquence des commutations dictée par le driver", "La force de friction appliquée sur les roulements", "Le nombre total de spires de la bobine d'induit", "La tension résiduelle de la batterie de ligne"], "rep": "La fréquence des commutations dictée par le driver"}
    ]
    if "ordre_quiz_tab8_aleatoire" not in st.session_state:
        random.shuffle(questions_t8)
        st.session_state.ordre_quiz_tab8_aleatoire = questions_t8

    champs_t8 = [
        ("1. Le moteur Brushless élimine les frotteurs mécaniques appelés .........", ["Choisir...", "balais", "bagues"], "balais", "t8_c1"),
        ("2. Les aimants permanents de forte puissance occupent le .........", ["Choisir...", "rotor", "stator"], "rotor", "t8_c2"),
        ("3. Les bobinages induits reçoivent le courant au sein du .........", ["Choisir...", "stator", "variateur"], "stator", "t8_c3"),
        ("4. L'onduleur ou ESC orchestre la commutation ......... des phases.", ["Choisir...", "électronique", "mécanique"], "électronique", "t8_c4"),
        ("5. La détection de la position du rotor emploie l'effet .........", ["Choisir...", "Hall", "Joule"], "Hall", "t8_c5"),
        ("6. Son rendement de conversion énergétique surpasse fréquemment .........", ["Choisir...", "90%", "60%"], "90%", "t8_c6"),
        ("7. Les aimants en terres rares exploitent principalement le .........", ["Choisir...", "Néodyme", "Ferrite"], "Néodyme", "t8_c7"),
        ("8. L'absence d'arc électrique autorise l'usage en milieu .........", ["Choisir...", "explosif", "humide"], "explosif", "t8_c8"),
        ("9. T.G. Wilson a activement participé à l'essor de cette .........", ["Choisir...", "technologie", "norme"], "technologie", "t8_c9"),
        ("10. Ce moteur équipe massivement les actionneurs de la ......... moderne.", ["Choisir...", "robotique", "traction"], "robotique", "t8_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz CC Brushless (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab8_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t8_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse CC Brushless (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t8:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t8_h_{cle}", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_tab7(verrouille=False):
    questions_t7 = [
        {"id": "q1", "q": "Quelle est la particularité constructive du stator d'un moteur Compound ?", "options": ["Il possède deux bobinages inducteurs distincts (série et parallèle)", "Il associe des aimants permanents et des balais mobiles", "Il intègre un onduleur hacheur au cœur de la culasse", "Il dispose d'un enroulement triphasé déphasé"], "rep": "Il possède deux bobinages inducteurs distincts (série et parallèle)"},
        {"id": "q2", "q": "Quel compromis technique offre le moteur à excitation composée (Compound) ?", "options": ["Le fort couple du moteur série et la vitesse limitée du moteur shunt", "Une suppression totale des frottements et de l'effet Foucault", "Un fonctionnement sans balais sur batterie monophasée", "Une vitesse infinie associée à un couple nul"], "rep": "Le fort couple du moteur série et la vitesse limitée du moteur shunt"},
        {"id": "q3", "q": "Quelle industrie lourde exploitait massivement le moteur Compound au début du XXe siècle ?", "options": ["Les ponts roulants, presses et ascenseurs", "L'électroménager de cuisine léger", "L'informatique et les têtes de lecture", "Les générateurs d'aviation"], "rep": "Les ponts roulants, presses et ascenseurs"},
        {"id": "q4", "q": "Comment appelle-t-on le montage où le flux du bobinage série renforce le flux du bobinage parallèle ?", "options": ["Le montage compound additif (ou cumulatif)", "Le montage compound soustractif (ou différentiel)", "Le montage shunt pur", "Le raccordement série haché"], "rep": "Le montage compound additif (ou cumulatif)"},
        {"id": "q5", "q": "Que se passe-t-il dans un montage compound différentiel lors d'une forte charge ?", "options": ["La vitesse s'effondre ou la machine peut devenir instable", "Le couple triple instantanément", "Le rendement atteint les performances IE5", "Les balais cessent d'étinceler"], "rep": "La vitesse s'effondre ou la machine peut devenir instable"},
        {"id": "q6", "q": "Le bobinage série d'un moteur Compound est parcouru par :", "options": ["Le courant d'induit total", "Le faible courant du circuit de dérivation", "Un courant continu externe filtré", "Une impulsion alternative de commande"], "rep": "Le courant d'induit total"},
        {"id": "q7", "q": "À vide, le moteur Compound additif adopte un comportement proche de :", "options": ["Un moteur Shunt (vitesse maximale finie et sécurisée)", "Un moteur Série (accélération infinie destructrice)", "Un transformateur en court-circuit", "Un moteur pas à pas bloqué"], "rep": "Un moteur Shunt (vitesse maximale finie et sécurisée)"},
        {"id": "q8", "q": "Le bobinage shunt parallèle évite au moteur Compound de :", "options": ["S'emballer à vide", "Consommer de la puissance active", "Générer de l'échauffement Joule au rotor", "Nécessiter un collecteur de cuivre"], "rep": "S'emballer à vide"},
        {"id": "q9", "q": "La caractéristique mécanique (vitesse en fonction du couple) d'un compound cumulatif est :", "options": ["Plus tombante que le shunt, mais stable à vide", "Strictement horizontale", "Hyperbolique tendant vers l'infini à vide", "Une droite verticale fixe"], "rep": "Plus tombante que le shunt, mais stable à vide"},
        {"id": "q10", "q": "L'inversion du sens de rotation d'un moteur Compound nécessite d' :", "options": ["Inverser uniquement le courant d'induit", "Inverser la totalité de la ligne d'alimentation", "Déconnecter le bobinage shunt parallèle", "Court-circuiter le rhéostat série"], "rep": "Inverser uniquement le courant d'induit"}
    ]
    if "ordre_quiz_tab7_aleatoire" not in st.session_state:
        random.shuffle(questions_t7)
        st.session_state.ordre_quiz_tab7_aleatoire = questions_t7

    champs_t7 = [
        ("1. Le moteur Compound rassemble les bénéfices du série et du .........", ["Choisir...", "shunt", "indépendant"], "shunt", "t7_c1"),
        ("2. Son stator intègre deux bobinages inducteurs de sections .........", ["Choisir...", "différentes", "identiques"], "différentes", "t7_c2"),
        ("3. L'enroulement série confère un excellent ......... initial.", ["Choisir...", "couple", "rendement"], "couple", "t7_c3"),
        ("4. L'enroulement parallèle limite la vitesse de rotation à .........", ["Choisir...", "vide", "charge"], "vide", "t7_c4"),
        ("5. Dans la variante cumulative, les deux flux magnétiques s'.........", ["Choisir...", "ajoutent", "opposent"], "ajoutent", "t7_c5"),
        ("6. La configuration différentielle cherche à maintenir une vitesse .........", ["Choisir...", "constante", "nulle"], "constante", "t7_c6"),
        ("7. Les chocs mécaniques des presses sont amortis par l'effet .........", ["Choisir...", "série", "shunt"], "série", "t7_c7"),
        ("8. Le courant absorbé global est réparti dans les enroulements du .........", ["Choisir...", "stator", "carter"], "stator", "t7_c8"),
        ("9. Le collecteur mécanique central demeure nécessaire à l'.........", ["Choisir...", "induit", "onduleur"], "induit", "t7_c9"),
        ("10. Ce moteur résout le dilemme des démarrages sous lourde .........", ["Choisir...", "charge", "fréquence"], "charge", "t7_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz CC Compound (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t7_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse CC Compound (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t7:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t7_h_{cle}", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_tab6(verrouille=False):
    questions_t6 = [
        {"id": "q1", "q": "Comment est couplé l'enroulement inducteur par rapport à l'induit dans un moteur Shunt ?", "options": ["En parallèle (en dérivation)", "En série direct de ligne", "Sur un onduleur triphasé séparé", "Via un interrupteur centrifuge"], "rep": "En parallèle (en dérivation)"},
        {"id": "q2", "q": "Quel industriel historique a imposé le moteur Shunt dans ses réseaux à tension constante ?", "options": ["Thomas Edison", "Nikola Tesla", "Werner von Siemens", "Eric Laithwaite"], "rep": "Thomas Edison"},
        {"id": "q3", "q": "Quelle est la principale caractéristique de la vitesse d'un moteur Shunt ?", "options": ["Elle s'auto-régule et varie très peu avec la charge", "Elle s'effondre linéairement jusqu'à zéro", "Elle double dès que le moteur chauffe", "Elle s'emballe fatalement à vide"], "rep": "Elle s'auto-régule et varie très peu avec la charge"},
        {"id": "q4", "q": "L'enroulement inducteur Shunt se caractérise constructivement par :", "options": ["Un grand nombre de spires de fil fin", "Une section de cuivre massive en série", "Un noyau magnétique amovible", "Un raccordement direct aux charbons"], "rep": "Un grand nombre de spires de fil fin"},
        {"id": "q5", "q": "Si la tension d'alimentation globale de la ligne baisse, le flux inducteur d'un moteur Shunt :", "options": ["Diminue proportionnellement à la tension", "Reste parfaitement identique et bloqué", "Augmente par compensation thermique", "Devient alternatif haute fréquence"], "rep": "Diminue proportionnellement à la tension"},
        {"id": "q6", "q": "Le courant de ligne total absorbé par un moteur Shunt est égal à :", "options": ["La somme du courant d'induit et d'excitation", "La soustraction des intensités stator/rotor", "Le courant d'induit multiplié par le cos phi", "Une intensité fixe indépendante de la charge"], "rep": "La somme du courant d'induit et d'excitation"},
        {"id": "q7", "q": "Pour modifier de façon externe la vitesse d'un moteur Shunt, on insère un rhéostat :", "options": ["En série avec le circuit inducteur pour l'affaiblir", "En parallèle sur la ligne principale", "Sous les balais pour augmenter la friction", "En série avec le fusible thermique"], "rep": "En série avec le circuit inducteur pour l'affaiblir"},
        {"id": "q8", "q": "À vide, le courant d'induit d'un moteur Shunt est :", "options": ["Très faible, couvrant uniquement les pertes et frottements", "Égal au courant de court-circuit", "Strictement nul", "Identique au courant d'excitation"], "rep": "Très faible, couvrant uniquement les pertes et frottements"},
        {"id": "q9", "q": "Quel avantage présente le Shunt par rapport à l'excitation série ?", "options": ["Aucun risque d'emballement destructeur à vide", "Un couple initial de démarrage dix fois plus grand", "Une absence totale de circuit ferromagnétique", "Une alimentation directe sur le réseau alternatif"], "rep": "Aucun risque d'emballement destructeur à vide"},
        {"id": "q10", "q": "Le couple de torsion maximal d'un moteur Shunt se manifeste :", "options": ["Au démarrage (lorsque le courant d'induit est maximal)", "À la vitesse maximale de synchronisme", "Lorsque l'excitation est coupée", "En régime établi à vide"], "rep": "Au démarrage (lorsque le courant d'induit est maximal)"}
    ]
    if "ordre_quiz_tab6_aleatoire" not in st.session_state:
        random.shuffle(questions_t6)
        st.session_state.ordre_quiz_tab6_aleatoire = questions_t6

    champs_t6 = [
        ("1. Le mot Shunt traduit l'existence d'une connexion en .........", ["Choisir...", "parallèle", "série"], "parallèle", "t6_c1"),
        ("2. L'inducteur absorbe un courant d'excitation indépendant de l'.........", ["Choisir...", "induit", "secteur"], "induit", "t6_c2"),
        ("3. L'alimentation se fait au moyen d'une ......... source de tension.", ["Choisir...", "unique", "double"], "unique", "t6_c3"),
        ("4. Sa bobine inductrice consomme une intensité relativement .........", ["Choisir...", "faible", "importante"], "faible", "t6_c4"),
        ("5. La machine Shunt conserve une ......... presque constante en charge.", ["Choisir...", "vitesse", "température"], "vitesse", "t6_c5"),
        ("6. Thomas Edison préférait ce moteur pour l'outillage des .........", ["Choisir...", "usines", "navires"], "usines", "t6_c6"),
        ("7. À vide, la vitesse est bridée par le flux stable de l'.........", ["Choisir...", "inducteur", "induit"], "inducteur", "t6_c7"),
        ("8. Le couple varie de manière ......... avec le courant du rotor.", ["Choisir...", "linéaire", "quadratique"], "linéaire", "t6_c8"),
        ("9. Un rhéostat de champ permet de régler le flux de l'.........", ["Choisir...", "excitation", "induit"], "excitation", "t6_c9"),
        ("10. Ce moteur est idéal pour l'actionnement des ......... à débit régulier.", ["Choisir...", "pompes", "démarreurs"], "pompes", "t6_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz CC Shunt (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t6_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse CC Shunt (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t6:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t6_h_{cle}", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_tab5(verrouille=False):
    questions_t5 = [
        {"id": "q1", "q": "Quel danger critique guette un moteur série alimenté sans charge (à vide) ?", "options": ["L'emballement mécanique destructeur", "Un blocage magnétique immédiat", "Une fusion instantanée par court-circuit", "Une baisse du couple rémanent"], "rep": "L'emballement mécanique destructeur"},
        {"id": "q2", "q": "Le couple de démarrage du moteur série évolue proportionnellement à :", "options": ["Au carré de l'intensité totale absorbée", "La tension nominale linéaire", "La racine carrée du flux inducteur", "Le nombre de pôles inducteurs"], "rep": "Au carré de l'intensité totale absorbée"},
        {"id": "q3", "q": "Comment sont raccordés l'inducteur et l'induit dans cette topologie ?", "options": ["En série sur la même branche de courant", "En dérivation parallèle", "Sur deux alimentations séparées autonomes", "Via un transformateur tournant de ligne"], "rep": "En série sur la même branche de courant"},
        {"id": "q4", "q": "Quelle application tirait un profit maximal de ce couple de démarrage géant ?", "options": ["La traction ferroviaire et les démarreurs", "Les ventilateurs d'ordinateurs", "Les servomoteurs industriels de précision", "Les horloges murales"], "rep": "La traction ferroviaire et les démarreurs"},
        {"id": "q5", "q": "Dans un moteur série, si le courant traversant l'induit double, le flux inducteur :", "options": ["Double également (avant saturation)", "Reste strictement inchangé", "S'effondre instantanément de moitié", "S'inverse à haute fréquence"], "rep": "Double également (avant saturation)"},
        {"id": "q6", "q": "Pourquoi la vitesse s'effondre-t-elle fortement lorsque le couple résistant augmente ?", "options": ["Car le flux augmente avec le courant absorbé", "Car les balais freinent mécaniquement l'axe", "Car la tension d'alimentation s'écroule", "Car le moteur bascule en mode asynchrone"], "rep": "Car le flux augmente avec le courant absorbé"},
        {"id": "q7", "q": "Pour inverser le sens de rotation d'un moteur série, il est nécessaire d' :", "options": ["Inverser uniquement les bornes de l'induit ou de l'inducteur", "Inverser la polarité de la ligne principale", "Changer le type de balais de graphite", "Ajouter une résistance en dérivation"], "rep": "Inverser uniquement les bornes de l'induit ou de l'inducteur"},
        {"id": "q8", "q": "Qui a mis en œuvre cette machine pour stabiliser les tramways de Richmond ?", "options": ["Frank J. Sprague", "Thomas Edison", "Nikola Tesla", "Mikhail Dolivo-Dobrovolsky"], "rep": "Frank J. Sprague"},
        {"id": "q9", "q": "À l'arrêt (vitesse nulle), la force électromotrice E d'un moteur série vaut :", "options": ["0 V", "La tension maximale de ligne", "Une tension négative d'induction", "La tension d'excitation seule"], "rep": "0 V"},
        {"id": "q10", "q": "Le fil constituant le bobinage inducteur d'un moteur série se caractérise par :", "options": ["Une forte section pour endurer tout le courant", "Un très grand nombre de spires fines", "Une gaine d'aluminium à haute impédance", "Un raccordement direct à un condensateur"], "rep": "Une forte section pour endurer tout le courant"}
    ]
    if "ordre_quiz_tab5_aleatoire" not in st.session_state:
        random.shuffle(questions_t5)
        st.session_state.ordre_quiz_tab5_aleatoire = questions_t5

    champs_t5 = [
        ("1. Dans cette configuration, l'inducteur et l'induit sont en .........", ["Choisir...", "série", "parallèle"], "série", "t5_c1"),
        ("2. Le courant absorbé traverse intégralement l'enroulement du .........", ["Choisir...", "stator", "condensateur"], "stator", "t5_c2"),
        ("3. Le couple initial de ce moteur est extrêmement .........", ["Choisir...", "élevé", "faible"], "élevé", "t5_c3"),
        ("4. Une absence de charge mécanique provoque un ......... de la machine.", ["Choisir...", "emballement", "blocage"], "emballement", "t5_c4"),
        ("5. Le moteur série s'auto-protège contre les calages par son fort .........", ["Choisir...", "couple", "glissement"], "couple", "t5_c5"),
        ("6. Sa vitesse décroît fortement quand l'effort demandé .........", ["Choisir...", "augmente", "diminue"], "augmente", "t5_c6"),
        ("7. Frank J. Sprague l'a exploité avec succès pour la traction .........", ["Choisir...", "ferroviaire", "aérienne"], "ferroviaire", "t5_c7"),
        ("8. L'inducteur possède une résistance interne interne très .........", ["Choisir...", "faible", "grande"], "faible", "t5_c8"),
        ("9. Inverser la tension de ligne n'inverse pas le ......... de rotation.", ["Choisir...", "sens", "rendement"], "sens", "t5_c9"),
        ("10. Ce moteur accepte également le courant alternatif, d'où sa variante .........", ["Choisir...", "universelle", "synchrone"], "universelle", "t5_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz CC Série (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t5_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse CC Série (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t5:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t5_h_{cle}", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_tab4(verrouille=False):
    questions_t4 = [
        {"id": "q1", "q": "Quelle est l'architecture d'alimentation caractéristique de ce moteur ?", "options": ["Deux alimentations distinctes pour le stator et le rotor", "Une seule alimentation de ligne pour le circuit série", "Une alimentation alternative triphasée sur bague", "Une boucle à excitation shunt unique"], "rep": "Deux alimentations distinctes pour le stator et le rotor"},
        {"id": "q2", "q": "Comment réagit la vitesse si la charge mécanique mécanique double sur l'arbre ?", "options": ["La vitesse reste virtuellement constante", "La vitesse s'effondre de moitié", "La vitesse s'emballe instantanément", "Le moteur inverse son sens de marche"], "rep": "La vitesse reste virtuellement constante"},
        {"id": "q3", "q": "Quelle formule définit la force électromotrice E de cette machine ?", "options": ["E = k * phi * Omega", "E = U - R*I", "E = P / I", "E = C * Omega"], "rep": "E = k * phi * Omega"},
        {"id": "q4", "q": "Pour inverser le sens de rotation de ce moteur CC, quelle action suffit ?", "options": ["Inverser la polarité de la tension d'induit", "Augmenter la résistance de la ligne", "Couper l'excitation inductrice", "Ajouter un condensateur de ligne"], "rep": "Inverser la polarité de la tension d'induit"},
        {"id": "q5", "q": "Que provoque une coupure accidentelle du circuit d'excitation (stator) en charge ?", "options": ["Un emballement critique et destructeur du rotor", "Un arrêt immédiat et sécurisé de l'arbre", "Une hausse brutale du rendement global", "Une annulation du courant d'induit"], "rep": "Un emballement critique et destructeur du rotor"},
        {"id": "q6", "q": "La chute de tension dans le rotor est causée par quel paramètre physique ?", "options": ["La résistance interne de l'induit R", "Le frottement mécanique aérodynamique", "La tension nominale d'excitation", "Le nombre de balais de graphite"], "rep": "La résistance interne de l'induit R"},
        {"id": "q7", "q": "Dans quelle industrie lourde utilisait-on principalement ce moteur stable ?", "options": ["Les laminoirs et les machines-outils", "Les aspirateurs grand public", "Les générateurs d'éoliennes", "La motorisation des drones légers"], "rep": "Les laminoirs et les machines-outils"},
        {"id": "q8", "q": "La constante k du moteur dépend intrinsèquement de :", "options": ["La géométrie constructive des enroulements du rotor", "La tension de la source externe", "Le courant absorbé en ligne", "Le couple résistant appliqué"], "rep": "La géométrie constructive des enroulements du rotor"},
        {"id": "q9", "q": "Comment régule-t-on facilement sa vitesse de rotation à flux constant ?", "options": ["En modifiant la tension d'induit U", "En ouvrant l'interrupteur inducteur", "En insérant un rhéostat série", "En augmentant la force des balais"], "rep": "En modifiant la tension d'induit U"},
        {"id": "q10", "q": "Le couple électromagnétique de cette machine est directement proportionnel à :", "options": ["L'intensité du courant d'induit I", "La vitesse de rotation carrée", "La tension nominale d'alimentation", "La chute de tension balais"], "rep": "L'intensité du courant d'induit I"}
    ]
    if "ordre_quiz_tab4_aleatoire" not in st.session_state:
        random.shuffle(questions_t4)
        st.session_state.ordre_quiz_tab4_aleatoire = questions_t4

    champs_t4 = [
        ("1. Ce moteur sépare de façon étanche le circuit inducteur et .........", ["Choisir...", "induit", "série"], "induit", "t4_c1"),
        ("2. L'inducteur fixe est logé au sein de la carcasse appelée .........", ["Choisir...", "stator", "rotor"], "stator", "t4_c2"),
        ("3. Le rotor, ou induit, reçoit son courant via l'ensemble balais-.........", ["Choisir...", "collecteur", "bagues"], "collecteur", "t4_c3"),
        ("4. À flux constant, le couple est directement lié au courant d'.........", ["Choisir...", "induit", "excitation"], "induit", "t4_c4"),
        ("5. La vitesse d'un moteur à excitation séparée est presque .........", ["Choisir...", "constante", "instable"], "constante", "t4_c5"),
        ("6. La tension d'alimentation de l'induit est notée réglementairement .........", ["Choisir...", "U", "E"], "U", "t4_c6"),
        ("7. La f.e.m. s'oppose en permanence à la tension de la source de .........", ["Choisir...", "ligne", "masse"], "ligne", "t4_c7"),
        ("8. Une baisse de tension d'induit engendre une baisse de la .........", ["Choisir...", "vitesse", "résistance"], "vitesse", "t4_c8"),
        ("9. Le flux inducteur doit rester stable pour éviter l'......... de l'axe.", ["Choisir...", "emballement", "blocage"], "emballement", "t4_c9"),
        ("10. Werner von Siemens a grandement démocratisé ces principes au ......... siècle.", ["Choisir...", "XIXe", "XXe"], "XIXe", "t4_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz CC Indépendante (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t4_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse CC Indépendante (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t4:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t4_h_{cle}", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_tab3(verrouille=False):
    questions_t3 = [
        {"id": "q1", "q": "Quelle équation vectorielle régit l'action d'un champ sur un conducteur rectiligne ?", "options": ["La force de Laplace", "La loi d'Ohm", "Le théorème de Gauss", "La loi de Lenz"], "rep": "La force de Laplace"},
        {"id": "q2", "q": "Comment qualifie-t-on l'élément fixe porteur du flux initial de la machine ?", "options": ["Le stator (ou inducteur)", "Le rotor", "L'induit", "Le collecteur"], "rep": "Le stator (ou inducteur)"},
        {"id": "q3", "q": "Quelle règle géométrique permet de déterminer le sens de la force électromécanique ?", "options": ["La règle des trois doigts de la main droite", "Le théorème de Pythagore", "La règle de la main gauche pour l'induction", "La loi des nœuds"], "rep": "La règle des trois doigts de la main droite"},
        {"id": "q4", "q": "Le phénomène d'induction décrit par Faraday stipule qu'un flux magnétique variable crée :", "options": ["Une force électromotrice induite (f.e.m)", "Une augmentation de la résistance électrique", "Une perte de charges statiques", "Un éclatement de l'entrefer"], "rep": "Une force électromotrice induite (f.e.m)"},
        {"id": "q5", "q": "Dans un moteur, le rotor tourne continuellement pour accomplir quelle action géométrique ?", "options": ["S'aligner sur les lignes de flux magnétique", "Fuir le champ magnétique statorique", "Créer un échauffement par friction", "Générer un courant de court-circuit"], "rep": "S'aligner sur les lignes de flux magnétique"},
        {"id": "q6", "q": "La loi de Lenz énonce que les effets de l'induction s'opposent toujours à :", "options": ["La cause qui leur a donné naissance", "La tension nominale du réseau", "L'intensité absolue traversant la ligne", "La constante de couple"], "rep": "La cause qui leur a donné naissance"},
        {"id": "q7", "q": "L'espace d'air séparant mécaniquement le stator fixe et le rotor mobile s'appelle :", "options": ["L'entrefer", "La culasse", "L'encoche", "Le flasque"], "rep": "L'entrefer"},
        {"id": "q8", "q": "La conversion électromécanique est intrinsèquement un processus de transformation :", "options": ["De l'énergie électrique en puissance mécanique", "De la chaleur en énergie cinétique", "Du flux en résistance variable", "Du potentiel en charge statique"], "rep": "De l'énergie électrique en puissance mécanique"},
        {"id": "q9", "q": "Qu'engendre l'interaction de deux flux magnétiques déphasés ou orthogonaux ?", "options": ["Un couple mécanique de rotation", "Une baisse du rendement thermique", "Une annulation du champ résultant", "Un court-circuit magnétique"], "rep": "Un couple mécanique de rotation"},
        {"id": "q10", "q": "Quelle particule élémentaire subit directement la force de Lorentz à l'origine du mouvement ?", "options": ["L'électron en mouvement", "Le neutron libre", "Le proton fixe", "L'atome de cuivre"], "rep": "L'électron en mouvement"}
    ]
    if "ordre_quiz_tab3_aleatoire" not in st.session_state:
        random.shuffle(questions_t3)
        st.session_state.ordre_quiz_tab3_aleatoire = questions_t3

    champs_t3 = [
        ("1. Le stator joue généralement le rôle d'......... en générant le flux.", ["Choisir...", "inducteur", "induit"], "inducteur", "t3_c1"),
        ("2. Le rotor subit les forces et fait office d'......... mobile.", ["Choisir...", "induit", "inducteur"], "induit", "t3_c2"),
        ("3. La force de Laplace est proportionnelle à l'......... magnétique B.", ["Choisir...", "induction", "intensité"], "induction", "t3_c3"),
        ("4. Le conducteur doit être parcouru par un ......... électrique.", ["Choisir...", "courant", "flux"], "courant", "t3_c4"),
        ("5. La force mécanique générée est ......... au plan formé par I et B.", ["Choisir...", "perpendiculaire", "parallèle"], "perpendiculaire", "t3_c5"),
        ("6. L'accumulation des forces radiales se traduit par un ......... moteur.", ["Choisir...", "couple", "glissement"], "couple", "t3_c6"),
        ("7. La f.e.m. induite apparaît dès que le conducteur est en .........", ["Choisir...", "mouvement", "arrêt"], "mouvement", "t3_c7"),
        ("8. Le circuit magnétique est feuilleté pour réduire les courants de .........", ["Choisir...", "Foucault", "Laplace"], "Foucault", "t3_c8"),
        ("9. L'évanouissement du champ magnétique annulerait le ......... mécanique.", ["Choisir...", "couple", "courant"], "couple", "t3_c9"),
        ("10. L'entrefer doit être le plus ......... possible pour maximiser le flux.", ["Choisir...", "faible", "large"], "faible", "t3_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Principe Général (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t3_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse Principe Général (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t3:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t3_h_{cle}", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_tab2(verrouille=False):
    questions_t2 = [
        {"id": "q1", "q": "Quelle découverte fondamentale Hans Christian Orsted a-t-il faite en 1820 ?", "options": ["Un courant électrique dévie l'aiguille d'une boussole", "Le principe de l'induction mutuelle", "L'invention de la pile chimique", "La formulation mathématique de la réluctance"], "rep": "Un courant électrique dévie l'aiguille d'une boussole"},
        {"id": "q2", "q": "Quel physicien a fabriqué le premier mouvement homopolaire continu en 1821 ?", "options": ["Michael Faraday", "André-Marie Ampère", "Thomas Davenport", "Nikola Tesla"], "rep": "Michael Faraday"},
        {"id": "q3", "q": "Qui a obtenu le premier brevet américain pour un moteur CC en 1834 ?", "options": ["Thomas Davenport", "Thomas Edison", "Werner von Siemens", "Frank J. Sprague"], "rep": "Thomas Davenport"},
        {"id": "q4", "q": "Quelle innovation majeure Nikola Tesla a-t-il brevetée en 1888 ?", "options": ["Le moteur asynchrone et le système alternatif polyphasé", "Le collecteur mécanique à balais de carbone", "La génératrice à excitation shunt", "Le transistor de puissance"], "rep": "Le moteur asynchrone et le système alternatif polyphasé"},
        {"id": "q5", "q": "Quel ingénieur a conçu le premier rotor à cage d'écureuil industriel en 1889 ?", "options": ["Mikhail Dolivo-Dobrovolsky", "Werner von Siemens", "Thomas Edison", "William Sturgeon"], "rep": "Mikhail Dolivo-Dobrovolsky"},
        {"id": "q6", "q": "William Sturgeon s'est illustré dans l'histoire de l'électricité pour avoir inventé :", "options": ["L'électroaimant et le premier collecteur commutateur", "La pile à colonne voltaïque", "L'onduleur de tension", "Le transformateur monophasé"], "rep": "L'électroaimant et le premier collecteur commutateur"},
        {"id": "q7", "q": "Quel industriel a fondé sa notoriété sur l'usage intensif des moteurs CC Shunt ?", "options": ["Thomas Edison", "Nikola Tesla", "George Westinghouse", "Eric Laithwaite"], "rep": "Thomas Edison"},
        {"id": "q8", "q": "Qui a développé les moteurs linéaires et les systèmes de lévitation dans les années 1960 ?", "options": ["Eric Laithwaite", "Harry Nyquist", "Hendrik Lorentz", "J.K. Kostko"], "rep": "Eric Laithwaite"},
        {"id": "q9", "q": "La guerre des courants à la fin du XIXe siècle opposait le courant continu d'Edison au courant alternatif de :", "options": ["Westinghouse et Tesla", "Siemens", "Faraday", "Sprague"], "rep": "Westinghouse et Tesla"},
        {"id": "q10", "q": "Quel scientifique a synthétisé les lois mathématiques complètes de l'électromagnétisme ?", "options": ["James Clerk Maxwell", "Pierre-Simon de Laplace", "Hendrik Lorentz", "Hans Christian Orsted"], "rep": "James Clerk Maxwell"}
    ]
    if "ordre_quiz_tab2_aleatoire" not in st.session_state:
        random.shuffle(questions_t2)
        st.session_state.ordre_quiz_tab2_aleatoire = questions_t2

    champs_t2 = [
        ("1. En 1820, Orsted établit la passerelle entre électricité et .........", ["Choisir...", "magnétisme", "thermodynamique"], "magnétisme", "t2_c1"),
        ("2. Le premier prototype de Faraday en 1821 utilisait un bain de .........", ["Choisir...", "mercure", "cuivre"], "mercure", "t2_c2"),
        ("3. Davenport utilisa un moteur pour propulser un petit ......... sur rails.", ["Choisir...", "chariot", "navire"], "chariot", "t2_c3"),
        ("4. L'invention du collecteur mécanique a permis de redresser le .........", ["Choisir...", "courant", "flux"], "courant", "t2_c4"),
        ("5. La distribution de l'énergie à grande échelle a profité de l'alternatif .........", ["Choisir...", "triphasé", "monophasé"], "triphasé", "t2_c5"),
        ("6. Tesla travailla brièvement pour la compagnie continentale d'.........", ["Choisir...", "Edison", "Siemens"], "Edison", "t2_c6"),
        ("7. Le rotor à cage d'écureuil de 1889 a éliminé le besoin de .........", ["Choisir...", "contacts", "bobines"], "contacts", "t2_c7"),
        ("8. Siemens inventa en 1866 la première dynamo à auto-.........", ["Choisir...", "excitation", "induction"], "excitation", "t2_c8"),
        ("9. L'électronique de puissance moderne a relancé les concepts de .........", ["Choisir...", "Tesla", "Davenport"], "Tesla", "t2_c9"),
        ("10. Les lois de Maxwell unifient les découvertes d'Ampère et .........", ["Choisir...", "Faraday", "Orsted"], "Faraday", "t2_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t2_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse Historique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t2:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t2_h_{cle}", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_tab1(verrouille=False):
    questions_t1 = [
        {"id": "q1", "q": "Quelle organisation internationale régit l'harmonisation des plaques signalétiques ?", "options": ["La CEI / IEC", "L'ISO", "L'IEEE", "L'AFNOR"], "rep": "La CEI / IEC"},
        {"id": "q2", "q": "Que désigne explicitement le paramètre Pn inscrit sur le châssis ?", "options": ["La puissance mécanique utile disponible sur l'arbre", "La puissance électrique active consommée", "La puissance réactive magnétisante", "La puissance apparente de ligne"], "rep": "La puissance mécanique utile disponible sur l'arbre"},
        {"id": "q3", "q": "Quelle classe d'efficacité IEC correspond au niveau Super Premium ?", "options": ["IE4", "IE3", "IE2", "IE5"], "rep": "IE4"},
        {"id": "q4", "q": "Quel couplage statorique applique-t-on si la tension réseau correspond à la plus basse valeur de la plaque ?", "options": ["Le couplage Triangle", "Le couplage Étoile", "Le couplage Série", "Le couplage Shunt"], "rep": "Le couplage Triangle"},
        {"id": "q5", "q": "Que mesure le facteur cosinus phi gravé sur la machine ?", "options": ["Le déphasage entre la tension et le courant", "Le taux de glissement rotorique", "La résistance interne des bobines", "La température de claquage thermique"], "rep": "Le déphasage entre la tension et le courant"},
        {"id": "q6", "q": "L'indice de protection IP55 garantit une étanchéité contre :", "options": ["Les poussières et les jets d'eau", "L'immersion totale prolongée", "Les explosions atmosphériques", "Les arcs électriques internes"], "rep": "Les poussières et les jets d'eau"},
        {"id": "q7", "q": "La vitesse nominale Nn exprimée sur la plaque est mesurée :", "options": ["A pleine charge nominale", "A vide sans aucun couple", "Au blocage complet de l'arbre", "En régime de surfréquence"], "rep": "A pleine charge nominale"},
        {"id": "q8", "q": "Quelle classe de rendement représente le sommet de la norme IEC 60034-30-1 ?", "options": ["IE5 (Ultra Premium)", "IE4", "IE3", "IE1"], "rep": "IE5 (Ultra Premium)"},
        {"id": "q9", "q": "Si une plaque indique 230V/400V, quelle tension maximale peut supporter chaque enroulement ?", "options": ["230 V", "400 V", "630 V", "115 V"], "rep": "230 V"},
        {"id": "q10", "q": "Le facteur de service (SF) égal à 1.15 signifie que le moteur peut supporter :", "options": ["Une surcharge temporaire de 15%", "Une hausse de tension de 15%", "Une hausse de fréquence de 15%", "Un glissement permanent de 15%"], "rep": "Une surcharge temporaire de 15%"}
    ]
    if "ordre_quiz_tab1_aleatoire" not in st.session_state:
        random.shuffle(questions_t1)
        st.session_state.ordre_quiz_tab1_aleatoire = questions_t1

    champs_t1 = [
        ("1. La plaque signalétique résume les caractéristiques ......... du constructeur.", ["Choisir...", "nominales", "maximales"], "nominales", "t1_c1"),
        ("2. La puissance utile s'exprime en kilowatts ou en chevaux .........", ["Choisir...", "vapeur", "électriques"], "vapeur", "t1_c2"),
        ("3. Le couplage étoile soumet chaque bobine à la tension ......... du réseau.", ["Choisir...", "simple", "composée"], "simple", "t1_c3"),
        ("4. La norme internationale de classification est la norme .........", ["Choisir...", "IEC", "ISO"], "IEC", "t1_c4"),
        ("5. Un rendement élevé permet de réduire les pertes par effet .........", ["Choisir...", "Joule", "Laplace"], "Joule", "t1_c5"),
        ("6. L'indice IP définit le niveau de protection de l'......... externe.", ["Choisir...", "enveloppe", "arbre"], "enveloppe", "t1_c6"),
        ("7. La vitesse réelle de rotation est toujours indiquée en ......... par minute.", ["Choisir...", "tours", "radians"], "tours", "t1_c7"),
        ("8. Le courant absorbé nominal est l'intensité en ligne notée .........", ["Choisir...", "In", "Un"], "In", "t1_c8"),
        ("9. Le cosinus phi est également appelé facteur de .........", ["Choisir...", "puissance", "glissement"], "puissance", "t1_c9"),
        ("10. La fréquence nominale en Europe est standardisée à 50 .........", ["Choisir...", "Hertz", "Volts"], "Hertz", "t1_c10")
    ]
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Identification (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"t1_q_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
    with col_trous:
        st.markdown("##### Synthèse Identification (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_t1:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"t1_h_{cle}", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Identification et Lecture de Plaque Signaletique")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Parametres Fondamentaux")
        st.markdown("""
        * **Puissance nominale (Pn) :** Puissance mecanique utile delivree sur l'arbre (kW).
        * **Vitesse nominale (Nn) :** Vitesse de l'arbre a charge nominale (tr/min).
        * **Tension (U) et Courant (I) :** Valeurs d'alimentation nominales.
        * **Facteur de puissance (cos phi) :** Rendement de dephasage electrique.
        """)
    with col2:
        st.subheader("Classes d'Efficacite Energetique IEC")
        st.markdown("""
        * **IE1 :** Standard
        * **IE2 :** Eleve
        * **IE3 :** Premium (Obligation industrielle actuelle)
        * **IE4 :** Super Premium
        * **IE5 :** Ultra Premium
        """)
    
    st.image("https://unsplash.com", caption="Exemple de plaque signaletique standard (Format JPG)", use_container_width=True)
    
    contenu_tab1 = "Pn, Nn, U, I, cos phi, Classes IE1 a IE5."
    st.download_button("Exporter Rapport", contenu_tab1, file_name=preparer_nom_fichier("Identification"))

    st.subheader("Atelier virtuel : Simulateur de plaque et calcul de rendement")
    st.write("Deplacez les curseurs pour configurer la puissance absorbee par un moteur triphase.")
    
    u_val = st.slider("Tension d'alimentation (V)", min_value=200, max_value=440, value=400, step=10, key="u_t1")
    i_val = st.slider("Courant nominal (A)", min_value=1.0, max_value=50.0, value=10.0, step=0.5, key="i_t1")
    cos_val = st.slider("Facteur de puissance (cos phi)", min_value=0.50, max_value=0.99, value=0.85, step=0.01, key="cos_t1")
    pn_val = st.slider("Puissance utile de l'arbre Pn (kW)", min_value=1.0, max_value=30.0, value=5.5, step=0.5, key="pn_t1")
    
    # Calcul de la puissance absorbée triphasée : P = U * I * cos(phi) * sqrt(3)
    import math
    pa_calc = (u_val * i_val * cos_val * math.sqrt(3)) / 1000 # en kW
    rendement = (pn_val / pa_calc) * 100 if pa_calc > 0 else 0
    
    st.metric("Puissance electrique absorbee par le reseau (Pa)", f"{pa_calc:.2f} kW")
    st.metric("Rendement global calcule", f"{rendement:.1f} %")
    
    if rendement > 95:
        st.success("Resultat theorique : Niveau de rendement équivalent a la classe IE5 (Ultra Premium)")
    elif rendement > 92:
        st.info("Resultat theorique : Niveau de rendement equivalent a la classe IE4 (Super Premium)")
    elif rendement > 88:
        st.info("Resultat theorique : Niveau de rendement equivalent a la classe IE3 (Premium)")
    else:
        st.warning("Resultat theorique : Rendement faible (IE1 ou hors normes)")


# ==============================================================================
# 2. HISTORIQUE GENERAL
# ==============================================================================
with tab2:
    st.header("Reperes Historiques et Pionniers")
    st.markdown("""
    * **1820 - Hans Christian Orsted :** Decouverte de la deviation de l'aiguille aimantee par un courant electrique.
    * **1821 - Michael Faraday :** Conception de la rotation electromagnetique continue (moteur homopolaire).
    * **1834 - Thomas Davenport :** Creation et brevet du premier moteur CC commercialisable.
    * **1888 - Nikola Tesla :** Brevet fondamental du systeme polyphase et du moteur asynchrone a courant alternatif.
    """)
    st.image("https://unsplash.com", caption="Illustration historique de laboratoire scientifique (Format JPG)", use_container_width=True)
    
    contenu_tab2 = "Historique : Orsted, Faraday, Davenport, Tesla."
    st.download_button("Exporter Rapport", contenu_tab2, file_name=preparer_nom_fichier("Historique"))

    st.subheader("Atelier virtuel : Visualisation de l'intensite du champ d'Orsted")
    st.write("Faites varier l'intensite du courant pour observer la force du champ magnetique cree autour du conducteur.")
    
    courant_orsted = st.slider("Intensite du courant injecte (A)", min_value=0, max_value=20, value=5, key="i_t2")
    # Formule simplifiée du champ B à une distance fixe (B = mu0 * I / 2pi*r)
    champ_b = 0.2 * courant_orsted # valeur arbitraire purement visuelle pour l'exercice
    
    st.write(f"Champ magnetique genere : {champ_b:.1f} microTesla")
    if courant_orsted == 0:
        st.write("Observation : L'aiguille de la boussole reste alignee sur le nord magnetique terrestre.")
    elif courant_orsted < 8:
        st.write("Observation : L'aiguille de la boussole devie legerement de sa trajectoire.")
    else:
        st.write("Observation : Le champ electrique prend le dessus, l'aiguille pivote fermement a 90 degres.")





# ==============================================================================
# 3. PRINCIPE GENERAL
# ==============================================================================
with tab3:
    st.header("Physique de la Conversion Electromecanique")
    st.markdown("""
    * **Le Personnage :** Pierre-Simon de Laplace et Hendrik Lorentz formalisent les actions exercees sur les conducteurs electriques.
    * **Fonctionnement detaille :** Le stator genere un flux magnetique inducteur. Le rotor (induit) est traverse par un courant electrique. D'apres la Loi de Laplace, chaque conducteur subit une force vectorielle tangentielle definie par : F = I x L x B. L'accumulation de ces forces engendre le couple moteur de rotation.
    """)
    st.image("https://unsplash.com", caption="Visualisation de la Force de Laplace entre Stator et Rotor (Format JPG)", use_container_width=True)
    
    contenu_tab3 = "Loi de Laplace : F = I * L x B. Interaction Stator/Rotor."
    st.download_button("Exporter Rapport", contenu_tab3, file_name=preparer_nom_fichier("Principe_General"))

    st.subheader("Atelier virtuel : Vecteur de la Force de Laplace")
    st.write("Modifiez le sens du courant et du champ pour calculer la force induite sur le conducteur.")
    
    sens_courant = st.radio("Sens du courant electrique (I)", ["Positif (Avant)", "Negatif (Arriere)"], key="sens_i_t3")
    sens_champ = st.radio("Orientation du champ magnetique (B)", ["Nord en haut", "Nord en bas"], key="sens_b_t3")
    intensite_f = st.slider("Intensite du flux magnetique", min_value=0, max_value=100, value=50, key="f_t3")
    
    if (sens_courant == "Positif (Avant)" and sens_champ == "Nord en haut") or (sens_courant == "Negatif (Arriere)" and sens_champ == "Nord en bas"):
        direction = "Propulsion vers la DROITE"
    else:
        direction = "Aspiration vers la GAUCHE"
        
    st.info(f"Observation de la balancoire : Force appliquee de {intensite_f} N avec une {direction}.")






with tab4:
    st.header("Moteur CC a Excitation Independante / Separee")
    st.markdown("""
    * **Historique et Personnage :** Developpe par les ingenieurs du XIXe siecle (dont Werner von Siemens) pour stabiliser la vitesse industrielle.
    * **Fonctionnement detaille :** Le bobinage inducteur (stator) et le bobinage induit (rotor) disposent de circuits electriques distincts alimentes par deux sources de tensions autonomes. La vitesse de rotation depend directement de la tension d'induit et reste stable sous charge changeante.
    """)
    st.image("https://unsplash.com", caption="Schema du circuit equivalent a excitation separee (Format JPG)", use_container_width=True)
    
    contenu_tab4 = "CC Independante : Circuits stator/rotor separes. Vitesse stable."
    st.download_button("Exporter Rapport", contenu_tab4, file_name=preparer_nom_fichier("CC_Independante"))
    st.subheader("Atelier virtuel : Controle de vitesse par la tension d'induit")
    u_induit = st.slider("Tension d'induit (V)", min_value=0, max_value=220, value=110, key="u_t4")
    vitesse_calc = u_induit * 13.6 # Constante k arbitraire
    st.metric("Vitesse de rotation de l'arbre", f"{vitesse_calc:.0f} tr/min")
    st.write("Observation : La vitesse de rotation evolue de maniere parfaitement proportionnelle et lineaire a votre curseur de tension.")





# ==============================================================================
# 5. MOTEUR CC A EXCITATION SERIE
# ==============================================================================
with tab5:
    st.header("Moteur CC a Excitation Serie")
    st.markdown("""
    * **Historique et Personnage :** Concu pour la traction ferroviaire initiale et applique par Frank J. Sprague.
    * **Fonctionnement detaille :** L'inducteur et l'induit sont branches en serie sur une seule source. Le courant total traverse le moteur. Le couple augmente au carre du courant absorbe, offrant un couple initial gigantesque. Attention : A vide, sans force resistante, la vitesse s'accelere dangereusement vers l'emballement destructeur.
    """)
    st.image("https://unsplash.com", caption="Schema de cablage en serie et courbe de fonctionnement (Format JPG)", use_container_width=True)
    
    contenu_tab5 = "CC Serie : Inducteur/induit en serie. Couple de demarrage maximal. Emballement a vide."
    st.download_button("Exporter Rapport", contenu_tab5, file_name=preparer_nom_fichier("CC_Serie"))

    st.subheader("Atelier virtuel : Le danger du demarrage a vide")
    couple_resistant = st.slider("Couple resistant applique sur l'arbre (Nm)", min_value=0.0, max_value=50.0, value=25.0, step=1.0, key="c_t5")
    
    if couple_resistant == 0:
        st.error("Observation : Risque critique ! Sans charge resistante, la vitesse s'emballe vers l'infini. Risque de destruction de la machine.")
    elif couple_resistant < 10:
        st.write(f"Observation : Le moteur tourne a un regime tres eleve (environ {5000 / couple_resistant:.0f} tr/min).")
    else:
        st.write(f"Observation : Regime stabilise et securise a {15000 / couple_resistant:.0f} tr/min.")






# ==============================================================================
# 6. MOTEUR CC SHUNT
# ==============================================================================
with tab6:
    st.header("Moteur CC Shunt (Parallele)")
    st.markdown("""
    * **Historique et Personnage :** Ameliore par Thomas Edison pour la distribution d'electricite a tension constante.
    * **Fonctionnement detaille :** L'inducteur et l'induit sont branches en parallele (shunt) sur la meme source d'alimentation. La vitesse de rotation reste virtuellement lineaire et s'auto-regule automatiquement lorsque la charge mecanique augmente.
    """)
    st.image("https://unsplash.com", caption="Machine a courant continu type Shunt industriel (Format JPG)", use_container_width=True)
    
    contenu_tab6 = "CC Shunt : Connexion parallele. Auto-regulation de la vitesse."
    st.download_button("Exporter Rapport", contenu_tab6, file_name=preparer_nom_fichier("CC_Shunt"))

    st.subheader("Atelier virtuel : Stabilite sous charge du moteur Shunt")
    charge_meca = st.slider("Charge mecanique appliquee (%)", min_value=0, max_value=100, value=20, key="c_t6")
    vitesse_shunt = 1500 - (charge_meca * 0.5) # La chute est infime
    st.metric("Vitesse de rotation stable", f"{vitesse_shunt:.1f} tr/min")
    st.write("Observation : Bien que vous augmentiez significativement la charge mecanique, la chute de vitesse est extremement reduite.")





# ==============================================================================
# 7. MOTEUR CC COMPOUND
# ==============================================================================
with tab7:
    st.header("Moteur CC Compound (Compose)")
    st.markdown("""
    * **Historique :** Developpe au tournant du XXe siecle pour resoudre le probleme des surcharges brutales des machines de levage.
    * **Fonctionnement detaille :** Le stator possede deux enroulements inducteurs distincts : un monte en serie avec l'induit, un autre connecte en parallele. Cette architecture combine l'excellent couple de demarrage du moteur serie et la limitation securisee de vitesse du moteur shunt.
    """)
    st.image("https://unsplash.com", caption="Schema structurel d'une machine composee (Format JPG)", use_container_width=True)
    
    contenu_tab7 = "CC Compound : Association serie + shunt. Fort couple sans risque d'emballement."
    st.download_button("Exporter Rapport", contenu_tab7, file_name=preparer_nom_fichier("CC_Compound"))

    st.subheader("Atelier virtuel : Equilibre Compound")
    regime_charge = st.slider("Demande d'effort de traction", min_value=0, max_value=100, value=80, key="c_t7")
    st.write(f"Observation : Le bobinage serie maintient un couple eleve de {regime_charge * 2.5} Nm, tandis que le bobinage shunt bride la vitesse maximale a 1800 tr/min de maniere securisee.")





# ==============================================================================
# 8. MOTEUR CC BRUSHLESS
# ==============================================================================
with tab8:
    st.header("Moteur CC sans balais (Brushless / BLDC)")
    st.markdown("""
    * **Historique et Personnage :** Invente au milieu du XXe siecle grace a l'avenement des semi-conducteurs par T.G. Wilson et P.H. Trickey.
    * **Fonctionnement detaille :** Les aimants permanents sont localises sur le rotor mobile, tandis que les enroulements triphases occupent le stator fixe. Les balais physiques et le collecteur mecanique sont supprimes et remplaces par une commutation electronique sequencee par des capteurs a effet Hall et un driver onduleur.
    """)
    st.image("https://unsplash.com", caption="Vue eclatee simplifiee d'un moteur Brushless (Format JPG)", use_container_width=True)
    
    contenu_tab8 = "Brushless : Commutation electronique par driver. Zero usure, haut rendement."
    st.download_button("Exporter Rapport", contenu_tab8, file_name=preparer_nom_fichier("CC_Brushless"))

    st.subheader("Atelier virtuel : Frequence de la commutation electronique")
    vitesse_drone = st.slider("Position de la manette des gaz du drone (%)", min_value=0, max_value=100, value=50, key="v_t8")
    frequence_hz = vitesse_drone * 4.5
    st.write(f"Observation : Le controleur electronique commute le courant dans les bobines fixes a une frequence precise de {frequence_hz:.1f} Hz pour synchroniser les aimants du rotor.")




with tab9:
    st.header("Moteur Asynchrone a Cage d'Ecureuil (Triphase)")
    st.markdown("""
    * **Historique et Personnage :** Invente parallelement par Nikola Tesla et par l'ingenieur Mikhail Dolivo-Dobrovolsky qui concoit le premier rotor a cage d'ecureuil industriel en 1889.
    * **Fonctionnement detaille :** Le stator alimente en alternatif triphase deploie un champ magnetique tournant synchrone. Ce champ magnetique balaie les barres conductrices en court-circuit du rotor, y induisant des courants de Foucault. Le rotor est entraine en rotation mais tourne a une vitesse necessairement inferieure au champ du stator : c'est le glissement.
    """)
    st.image("https://unsplash.com", caption="Rotor a cage d'ecureuil face a ses enroulements statoriques (Format JPG)", use_container_width=True)
    
    contenu_tab9 = "Asynchrone Cage : Champ tournant inducteur. Courants induits au rotor. Notion de glissement."
    st.download_button("Exporter Rapport", contenu_tab9, file_name=preparer_nom_fichier("AC_Asynchrone_Cage"))

    st.subheader("Atelier virtuel : Calcul et observation du glissement")
    frequence_reseau = st.slider("Frequence du courant industriel (Hz)", min_value=10, max_value=60, value=50, key="f_t9")
    nbr_poles = st.select_slider("Nombre de poles du moteur (p)", options=[2, 4, 6, 8], value=4, key="p_t9")
    charge_induc = st.slider("Couple de freinage applique (Nm)", min_value=0, max_value=100, value=50, key="c_t9")
    
    vitesse_synchrone = (frequence_reseau * 60) / (nbr_poles / 2)
    vitesse_rotor_reelle = vitesse_synchrone - (charge_induc * 0.8)
    glissement_pourcent = ((vitesse_synchrone - vitesse_rotor_reelle) / vitesse_synchrone) * 100
    
    st.metric("Vitesse du champ tournant du stator (Vitesse synchrone)", f"{vitesse_synchrone:.0f} tr/min")
    st.metric("Vitesse de rotation reelle de la cage d'ecureuil", f"{vitesse_rotor_reelle:.0f} tr/min")
    st.metric("Taux de glissement calcule", f"{glissement_pourcent:.2f} %")






# ==============================================================================
# 10. MOTEUR ASYNCHRONE A ROTOR BOBINE
# ==============================================================================
with tab10:
    st.header("Moteur Asynchrone a Rotor Bobine (Bagues)")
    st.markdown("""
    * **Historique :** Developpe a l'ere pre-electronique pour pouvoir moduler le courant et le couple au demarrage des fortes charges d'usines.
    * **Fonctionnement detaille :** Le rotor comporte de vrais bobinages de cuivre connectes a l'exterieur via des bagues lisses et des balais. En connectant un rheostat externe temporaire en serie avec ces bagues, on augmente la resistance du rotor pour limiter le pic d'intensite au demarrage tout en augmentant fortement le couple.
    """)
    st.image("https://unsplash.com", caption="Structure de stator et de rotor bobine a fils fins (Format JPG)", use_container_width=True)
    
    contenu_tab10 = "Asynchrone Bagues : Bobinage rotorique externe accessible via bagues pour rheostat."
    st.download_button("Exporter Rapport", contenu_tab10, file_name=preparer_nom_fichier("AC_Asynchrone_Bobine"))
    st.subheader("Atelier virtuel : Insertion des resistances de rheostat")
    rheostat_val = st.slider("Resistance externe connectee au rotor (Ohms)", min_value=0, max_value=100, value=80, key="r_t10")
    courant_demarrage = 500 - (rheostat_val * 4)
    st.metric("Pic de courant au demarrage", f"{courant_demarrage} A")
    st.write("Observation : Augmenter la resistance externe ecrase le pic de courant sur le reseau electrique au moment de la mise sous tension.")




# ==============================================================================
# 11. MOTEUR ASYNCHRONE MONOPHASE
# ==============================================================================
with tab11:
    st.header("Moteur Asynchrone Monophase")
    st.markdown("""
    * **Historique :** Generalise au milieu du XXe siecle pour equiper l'electromenager et l'habitat non desservis par le reseau triphase.
    * **Fonctionnement detaille :** Une phase unique alternative ne peut generer qu'un champ magnetique pulsant rectiligne, incapable d'initier seul le demarrage du rotor. On ajoute un enroulement auxiliaire dote d'un condensateur de dephasage permanent ou de demarrage pour simuler artificiellement une seconde phase electrique et creer le champ tournant initial.
    """)
    st.image("https://unsplash.com", caption="Moteur a induction asynchrone monophase industriel sectionne (Format JPG)", use_container_width=True)
    
    contenu_tab11 = "Asynchrone Monophase : Champ pulsant. Condensateur requis pour initier le champ tournant."
    st.download_button("Exporter Rapport", contenu_tab11, file_name=preparer_nom_fichier("AC_Asynchrone_Mono"))

    st.subheader("Atelier virtuel : Etat du condensateur")
    condo_etat = st.radio("Branchement du condensateur de dephasage", ["Debranche / Hors service", "Connecte / En service"], key="condo_t11")
    if condo_etat == "Debranche / Hors service":
        st.error("Observation : Le moteur vibre intensement sur place et emet un grognement alternatif, mais le couple initial de demarrage est nul (0 Nm).")
    else:
        st.success("Observation : Le condensateur cree le dephasage requis. Le champ magnetique devient tournant et lance le rotor immediatement.")




# ==============================================================================
# 12. MOTEUR SYNCHRONE A AIMANTS PERMANENTS
# ==============================================================================
with tab12:
    st.header("Moteur Synchrone a Aimants Permanents (PMSM)")
    st.markdown("""
    * **Historique :** Apparu avec l'industrialisation des aimants de synthese modernes (SMC, Samarium, Neodyme-Fer-Bore).
    * **Fonctionnement detaille :** Le rotor contient des aimants puissants fixes. Des que le stator cree son champ tournant alternatif (via un onduleur de puissance), le rotor se verrouille magnetiquement dessus de maniere rigide. La vitesse de rotation du rotor est strictement egale a la vitesse du champ. Il n'y a aucun glissement.
    """)
    st.image("https://unsplash.com", caption="Machine synchrone industrielle de haute densite (Format JPG)", use_container_width=True)
    
    contenu_tab12 = "Synchrone Aimants : Aimants permanents au rotor. Vitesse de rotation synchrone sans glissement."
    st.download_button("Exporter Rapport", contenu_tab12, file_name=preparer_nom_fichier("AC_Synchrone_Aimants"))

    st.subheader("Atelier virtuel : Rigidite de la vitesse synchrone")
    freq_onduleur = st.slider("Frequence de sortie de l'onduleur (Hz)", min_value=10, max_value=150, value=60, key="f_t12")
    charge_pmsm = st.slider("Effort resistant mecanique (Nm)", min_value=0, max_value=200, value=100, key="c_t12")
    vitesse_pmsm = (freq_onduleur * 60) / 2 # hypothese 4 poles
    st.metric("Vitesse mesurée sur l'arbre", f"{vitesse_pmsm:.0f} tr/min")
    st.write("Observation : Peu importe l'effort resistant applique, la vitesse de rotation reste parfaitement bloquee sur la frequence electrique. Le glissement est rigoureusement nul.")






# ==============================================================================
# 13. MOTEUR SYNCHRONE A ROTOR BOBINE
# ==============================================================================
with tab13:
    st.header("Moteur Synchrone a Rotor Bobine")
    st.markdown("""
    * **Personnage et Application moderne :** Exploite historiquement dans les grosses centrales et remis au gout du jour par des constructeurs automobiles comme Renault ou BMW pour s'affranchir des terres rares.
    * **Fonctionnement detaille :** Les aimants permanents du rotor sont remplaces par des bobines formant des electroaimants. Ces derniers sont alimentes en courant continu via des bagues et des balais. L'onduleur ajuste l'intensite de l'aimantation du rotor en temps reel afin d'optimiser le rendement energetique global a haute vitesse.
    """)
    st.image("https://unsplash.com", caption="Exemple d'alimentation d'un inducteur tournant bobine (Format JPG)", use_container_width=True)
    
    contenu_tab13 = "Synchrone Bobine : Electroaimant inducteur mobile. Ajustement dynamique du flux sans terres rares."
    st.download_button("Exporter Rapport", contenu_tab13, file_name=preparer_nom_fichier("AC_Synchrone_Bobine"))

    st.subheader("Atelier virtuel : Ajustement de l'excitation rotorique")
    courant_excitation = st.slider("Courant continu injecte dans l'electroaimant du rotor (A)", min_value=0.0, max_value=10.0, value=4.0, key="i_t13")
    if courant_excitation < 3:
        st.write("Observation : Le moteur est sous-excite. Il absorbe une grande quantite d'energie reactive sur le reseau.")
    elif courant_excitation < 7:
        st.write("Observation : L'equilibre est optimal. Le facteur de puissance cos phi est proche de 1.")
    else:
        st.write("Observation : Le moteur est sur-excite. Il compense les autres machines de l'usine en renvoyant du réactif.")






# ==============================================================================
# 14. MOTEUR SYNCHRONE A RELUCTANCE VARIABLE
# ==============================================================================
with tab14:
    st.header("Moteur Synchrone a Reluctance Variable (SynRM)")
    st.markdown("""
    * **Historique :** Brevete au debut du XXe siecle par J.K. Kostko, sa mise en oeuvre reelle a attendu la puissance de calcul des microcontroleurs modernes.
    * **Fonctionnement detaille :** Le rotor est un simple assemblage de toles d'acier depourvu d'aimants et de bobines, façonne avec des barrieres d'air geometriques. Le champ magnetique cree par le stator cherche en permanence le chemin de moindre resistance magnetique (la reluctance minimale), contraignant le rotor a s'aligner de facon synchrone avec le flux tournant.
    """)
    st.image("https://unsplash.com", caption="Geometrie d'encoches de commande pour machines sans balais (Format JPG)", use_container_width=True)
    
    contenu_tab14 = "SynRM : Rotor ferromagnetique sans aimant. Rotation par recherche de la reluctance minimale."
    st.download_button("Exporter Rapport", contenu_tab14, file_name=preparer_nom_fichier("AC_Reluctance"))

    st.subheader("Atelier virtuel : Orientation des barrieres de reluctance")
    angle_stator = st.slider("Position angulaire du flux statorique (Degres)", min_value=0, max_value=180, value=45, key="a_t14")
    st.write(f"Observation : Le bloc de toles d'acier du rotor pivote de facon instantanee pour venir s'aligner exactement sur l'angle de {angle_stator} degres afin de minimiser la resistance du flux.")
















with tab15:
    st.header("Moteur Universel")
    st.markdown("""
    * **Historique :** Developpe au debut de l'electrification domestique pour tolerer n'importe quel type de reseau disponible.
    * **Fonctionnement detaille :** Il s'agit structuralement d'un moteur a courant continu de type excitation serie. Cependant, son stator et son rotor sont integralement feuilletes de fines epaisseurs d'acier isolantes pour limiter les pertes de fer induites par le courant alternatif. Le moteur accepte indifferemment le CA et le CC en gardant un meme sens de rotation.
    """)
    st.image("https://unsplash.com", caption="Architecture a collecteur et balais d'un moteur universel (Format JPG)", use_container_width=True)
    
    contenu_tab15 = "Universel : Architecture CC Serie feuilletee. Fonctionne en alternatif et continu."
    st.download_button("Exporter Rapport", contenu_tab15, file_name=preparer_nom_fichier("Moteur_Universel"))
    st.subheader("Atelier virtuel : Comportement alternatif vs continu")
    type_alim = st.radio("Nature de la tension appliquee", ["Courant Continu (CC)", "Courant Alternatif (CA) 50Hz"], key="type_t15")
    tension_univ = st.slider("Niveau de tension applique (V)", min_value=0, max_value=230, value=110, key="u_t15")
    
    if type_alim == "Courant Continu (CC)":
        st.write(f"Observation : Rotation stable et silencieuse a {tension_univ * 50:.0f} tr/min. Rendement optimal.")
    else:
        st.write(f"Observation : Le moteur tourne a {tension_univ * 42:.0f} tr/min avec un sifflement sonore caracteristique lie aux variations alternatives du courant.")






# ==============================================================================
# 16. MOTEUR PAS A PAS
# ==============================================================================
with tab16:
    st.header("Moteur Pas a Pas")
    contents_tab16 = "Moteur Pas a Pas\nPrincipe : Activation sequentielle des bobines du stator.\nCaracteristiques : Positionnement precis sans capteur, faible couple rapide.\nUsage : Imprimantes 3D."
    st.markdown("""
    * **Historique :** Developpe massivement au cours de la seconde moitie du XXe siecle pour la bureautique et l'informatique naissante.
    * **Fonctionnement detaille :** Le stator est subdivise en de multiples bobinages independants appeles phases. Le controleur injecte des impulsions de courant successives et ordonnees qui deplace le champ magnetique d'un angle fixe et geometrique. Le rotor dente s'aligne rigoureusement d'un saut angulaire discret appele un pas (ex: 1,8 degre par pas).
    """)
    st.image("https://unsplash.com", caption="Vue interieure des dents d'une machine a pas et capteurs (Format JPG)", use_container_width=True)
    
    st.download_button("Exporter Rapport", contents_tab16, file_name=preparer_nom_fichier("Pas_a_Pas"))
    st.subheader("Atelier virtuel : Mode de commande angulaire")
    mode_pas = st.radio("Configuration de l'alimentation des phases", ["Pas entier", "Demi-pas"], key="mode_t16")
    nbr_impulsions = st.slider("Nombre d'impulsions envoyees par le calculateur", min_value=0, max_value=200, value=100, key="imp_t16")
    
    if mode_pas == "Pas entier":
        angle_total = nbr_impulsions * 1.8
        st.write(f"Observation : L'arbre a pivote de {angle_total:.1f} degres de maniere saccadee (sauts discrets de 1.8°).")
    else:
        angle_total = nbr_impulsions * 0.9
        st.write(f"Observation : L'arbre a pivote de {angle_total:.1f} degres. Le mouvement est deux fois plus fluide (sauts fins de 0.9°).")






# ==============================================================================
# 17. SERVOMOTEUR
# ==============================================================================
with tab17:
    st.header("Servomoteur")
    st.markdown("""
    * **Historique et Personnage :** Theorise par les automaticiens du XXe siecle (dont Harry Nyquist) pour la stabilisation et le guidage de precision.
    * **Fonctionnement detaille :** Le servomoteur constitue un systeme complet en boucle fermee. Il accouple un moteur de base (CC ou Brushless), un capteur de position precis (codeur optique ou resolveur) et une carte d'asservissement electronique locale. Le circuit compare en continu la position reelle mesuree a l'instruction commandee et applique une correction de couple immediate.
    """)
    st.image("https://unsplash.com", caption="Enroulements et capteurs de position integres pour servomoteurs (Format JPG)", use_container_width=True)
    
    contenu_tab17 = "Servomoteur : Moteur + codeur de position + carte d'asservissement. Boucle fermee."
    st.download_button("Exporter Rapport", contenu_tab17, file_name=preparer_nom_fichier("Servomoteur"))

    st.subheader("Atelier virtuel : Boucle de retroaction et correction de position")
    consigne_angle = st.slider("Consigne d'angle demandee (Degres)", min_value=0, max_value=180, value=90, key="ang_t17")
    force_perturbation = st.slider("Force externe appliquee pour faire dévier l'axe (N)", min_value=0, max_value=50, value=0, key="f_t17")
    
    courant_moteur = 0.1 + (force_perturbation * 0.4)
    angle_reel = consigne_angle - (force_perturbation * 0.05) # Le capteur corrige l'erreur presque totalement
    
    st.metric("Position reelle de l'axe", f"{angle_reel:.2f} Degres")
    st.metric("Courant consomme pour contrer la perturbation", f"{courant_moteur:.2f} A")





# ==============================================================================
# 18. MOTEUR LINEAIRE
# ==============================================================================
with tab18:
    st.header("Moteur Lineaire")
    st.markdown("""
    * **Historique et Personnage :** Porte par l'ingenieur britannique Eric Laithwaite dans les annees 1960 pour revolutionner les transports a haute vitesse.
    * **Fonctionnement detaille :** Sa structure correspond a un moteur synchrone ou asynchrone conventionnel que l'on aurait decoupe suivant un rayon et etale a plat le long d'une trajectoire rectiligne. Le champ magnetique glisse horizontalement le long du stator rectiligne et pousse directement le rotor plan, convertissant l'energie electrique en une force de translation rectiligne directe sans liaison mecanique.
    """)
    st.image("https://unsplash.com", caption="Evolution du profil rectiligne et dynamique lineaire (Format JPG)", use_container_width=True)
    
    contenu_tab18 = "Moteur Lineaire : Decoupage et deploiement a plat de l'architecture. Force de translation rectiligne."
    st.download_button("Exporter Rapport", contenu_tab18, file_name=preparer_nom_fichier("Moteur_Lineaire"))
    st.subheader("Atelier virtuel : Vitesse de l'onde de translation")
    frequence_onde = st.slider("Frequence de balayage des enroulements lineaires (Hz)", min_value=10, max_value=200, value=50, key="f_t18")
    pas_polaire = 0.25 # distance entre deux poles en metres
    vitesse_lineaire_ms = 2 * pas_polaire * frequence_onde
    vitesse_kmh = vitesse_lineaire_ms * 3.6
    
    st.metric("Vitesse lineaire de translation du chariot", f"{vitesse_lineaire_ms:.1f} m/s")
    st.metric("Vitesse equivalente en kilometres par heure", f"{vitesse_kmh:.1f} km/h")



    


























    st.write("---")        
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    afficher_atelier_decomposition_complet(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 1")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier Decomposition.",
        key="check_certif_generalites_final_net",
        disabled=verrou_at1,
    )
    
    # --- 4. BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_aleatoire:
                    reponse_eleve = st.session_state.get(f"dec_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # Verification des bonnes reponses du texte a trous adapte a la statique
            score_t1 = sum(
                [
                    st.session_state.get("dec_t1_final") == "orthogonales",
                    st.session_state.get("dec_t2_final") == "chevaucher",
                    st.session_state.get("dec_t3_final") == "cosinus",
                    st.session_state.get("dec_t4_final") == "sinus",
                    st.session_state.get("dec_t5_final") == "rectangle",
                    st.session_state.get("dec_t6_final") == "sens",
                    st.session_state.get("dec_t7_final") == "formules",
                    st.session_state.get("dec_t8_final") == "invariante",
                    st.session_state.get("dec_t9_final") == "verticale",
                    st.session_state.get("dec_t10_final") == "totale",
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
        st.success(f"ATELIER DECOMPOSITION SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Decomposition - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Mecanique - Statique</h1>
                <p>Atelier 1 : Decomposition vectorielle des forces</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Decomposition : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese du cours : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Rectification ici : Appel de la liste de session stockee a l'atelier 1
        if "ordre_quiz_tab1_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
                saisie = st.session_state.get(f"dec_at6_final_g_{q_item['id']}", "Choisir...")
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
        nom_fichier_html = preparer_nom_fichier("Rapport_Atelier_1").replace(".txt", ".html")
        st.download_button(
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 1 (.html)",
            data=html_export_suites,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )

