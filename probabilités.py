import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application de Probabilites",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application de Probabilités")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

# =============================================================================
# INITIALISATION SECURISEE DU SESSION STATE (A l'ouverture de l'application)
# =============================================================================
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
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")
if "roulette_dernier_numero" not in st.session_state:
    st.session_state.roulette_dernier_numero = 0


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
    "1. Jeux de hasard 1",
    "2. Jeux de hasard 2",
    "3. Tableau de probabilités",
    "4. Arbre de probabilités",
    "5. Espérance et variance",
    "6. Loi exponentielle ",
    "7. Loi binomiale ",    
    "8. Loi de Poisson",
    "9. Loi de Gauss (loi normale)"
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

def afficher_questions_atelier1(verrouille=False):
    col_maitre_quiz, col_maitre_trous = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LE QUIZ FRACTIONS DE L'ATELIER 1
    # -------------------------------------------------------------------------
    with col_maitre_quiz:
        st.subheader("Quiz theorique (10 questions)")
        st.write("Repondez aux questions de cours ci-dessous :")

        if "banque_quiz_at1" not in st.session_state:
            st.session_state.banque_quiz_at1 = [
                {"id": "q1", "q": "Question 1 : Si un evenement a 3 chances sur 4 de se realiser, sa probabilite est de :", "opts": ["Choisir...", "0.25", "0.50", "0.75", "1.33"]},
                {"id": "q2", "q": "Question 2 : Quelle est la probabilite d'obtenir un nombre pair (2, 4, 6) avec le de cubique :", "opts": ["Choisir...", "1/6", "2/6", "3/6 (1/2)", "4/6"]},
                {"id": "q3", "q": "Question 3 : Quelle est la probabilite d'obtenir une figure (Valet, Dame, Roi) dans le jeu de 32 cartes :", "opts": ["Choisir...", "4/32", "8/32", "12/32 (3/8)", "16/32"]},
                {"id": "q4", "q": "Question 4 : L'evenement contraire de 'obtenir un 6' au de a pour probabilite :", "opts": ["Choisir...", "0", "1/6", "5/6", "1"]},
                {"id": "q5", "q": "Question 5 : La probabilite d'un evenement est obligatoirement un nombre compris entre :", "opts": ["Choisir...", "-1 et 1", "0 et 1", "0 et 6", "1 et 100"]},
                {"id": "q6", "q": "Question 6 : Si on tire le 7 de Pique, cet evenement is qualifie d'evenement :", "opts": ["Choisir...", "Impossible", "Certain", "Elementaire", "Compose"]},
                {"id": "q7", "q": "Question 7 : Quelle est la probabilite d'obtenir un multiple de 3 (3 ou 6) sur le de :", "opts": ["Choisir...", "1/6", "2/6 (1/3)", "3/6", "4/6"]},
                {"id": "q8_at1", "q": "Question 8 : Quelle est la probabilite de tirer soit un Roi soit un As dans le jeu de 32 cartes :", "opts": ["Choisir...", "2/32", "4/32", "8/32 (1/4)", "12/32"]},
                {"id": "q9", "q": "Question 9 : Un de a 6 faces est truque pour que le 6 sorte plus souvent. La somme des probabilites vaut :", "opts": ["Choisir...", "0.5", "1", "2", "6"]},
                {"id": "q10", "q": "Question 10 : Si la probabilite d'un evenement A est 0.3, celle de son evenement contraire est :", "opts": ["Choisir...", "0", "0.3", "0.7", "1"]}
            ]
            random.shuffle(st.session_state.banque_quiz_at1)

        for item_quiz in st.session_state.banque_quiz_at1:
            cle_q = f"col_g_quiz_{item_quiz['id']}"
            val_precedente = st.session_state.get(cle_q, "Choisir...")
            idx_defaut = item_quiz["opts"].index(val_precedente) if val_precedente in item_quiz["opts"] else 0

            st.selectbox(
                label=item_quiz["q"], 
                options=item_quiz["opts"], 
                index=idx_defaut, 
                key=cle_q,
                disabled=verrouille
            )

    # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LE TEXTE A TROUS DE L'ATELIER 1
    # -------------------------------------------------------------------------
    with col_maitre_trous:
        st.subheader("Texte a trous (10 menus)")
        st.write("Completez le texte d'analyse ci-dessous :")

        if "banque_trous_at1" not in st.session_state:
            st.session_state.banque_trous_at1 = [
                {"id": "t1", "label": "Question A : Nombre de faces d'un de cubique regulier :", "options": ["Choisir...", "2", "4", "6", "8", "12"]},
                {"id": "t2", "label": "Question B : Probabilite theorique d'obtenir la face 6 sur le de :", "options": ["Choisir...", "1/2", "1/4", "1/6", "4/6", "1"]},
                {"id": "t3", "label": "Question C : Nombre total de cartes dans le paquet utilise :", "options": ["Choisir...", "12", "32", "36", "52", "54"]},
                {"id": "t4", "label": "Question D : Nombre de familles (couleurs) differentes dans ce jeu :", "options": ["Choisir...", "1", "2", "3", "4", "8"]},
                {"id": "t5", "label": "Question E : Nombre de cartes par famille (ex: nombre de Piques) :", "options": ["Choisir...", "4", "7", "8", "10", "13"]},
                {"id": "t6", "label": "Question F : Probabilite theorique de tirer un As dans ce jeu :", "options": ["Choisir...", "1/32", "2/32", "4/32 (1/8)", "8/32 (1/4)", "0"]},
                {"id": "t7", "label": "Question G : Probabilite theorique de tirer un Coeur dans ce jeu :", "options": ["Choisir...", "1/32", "4/32 (1/8)", "8/32 (1/4)", "16/32 (1/2)", "1"]},
                {"id": "t8", "label": "Question H : Un evenement dont la probabilite est egale a 1 est un evenement :", "options": ["Choisir...", "Impossible", "Probable", "Incertain", "Certain", "Contraire"]},
                {"id": "t9", "label": "Question I : Un evenement dont la probabilite est egale a 0 est un evenement :", "options": ["Choisir...", "Impossible", "Probable", "Incertain", "Certain", "Contraire"]},
                {"id": "t10", "label": "Question J : La somme des probabilites de toutes les faces distinctes du de vaut :", "options": ["Choisir...", "0", "0.5", "1", "6", "100"]}
            ]
            random.shuffle(st.session_state.banque_trous_at1)

        for item_trous in st.session_state.banque_trous_at1:
            cle_t = f"col_d_trous_{item_trous['id']}"
            val_precedente_t = st.session_state.get(cle_t, "Choisir...")
            idx_defaut_t = item_trous["options"].index(val_precedente_t) if val_precedente_t in item_trous["options"] else 0

            st.selectbox(
                label=item_trous["label"], 
                options=item_trous["options"], 
                index=idx_defaut_t, 
                key=cle_t,
                disabled=verrouille
            )


def afficher_questions_atelier2(verrouille=False):
    col_maitre_quiz_at2, col_double_trous_at2 = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LE QUIZ THEORIQUE DE 10 QUESTIONS MELEES
    # -------------------------------------------------------------------------
    with col_maitre_quiz_at2:
        st.subheader("Quiz theorique (10 questions) - Atelier 2")
        st.write("Repondez aux questions de cours ci-dessous :")

        if "banque_quiz_at2" not in st.session_state:
            st.session_state.banque_quiz_at2 = [
                {"id": "q1_at2", "q": "Question 1 : Combien de cases contient la roulette europeenne :", "opts": ["Choisir...", "36", "37", "38"]},
                {"id": "q2_at2", "q": "Question 2 : Probabilite obtenir le numero 7 unique :", "opts": ["Choisir...", "1/36", "1/37", "1/2"]},
                {"id": "q3_at2", "q": "Question 3 : La probabilite de miser sur la categorie Rouge vaut :", "opts": ["Choisir...", "18/36", "18/37", "1/2"]},
                {"id": "q4_at2", "q": "Question 4 : L'avantage de la roulette pour le casino vient de :", "opts": ["Choisir...", "La case Zero", "Des numeros noirs", "De la bille"]},
                {"id": "q5_at2", "q": "Question 5 : En augmentant les lancers, la frequence rejoint :", "opts": ["Choisir...", "La probabilite theoretique", "Zero", "L'infini"]},
                {"id": "q6_at2", "q": "Question 6 : Cette convergence s'appelle la loi des grands :", "opts": ["Choisir...", "Nombres", "Ecarts", "Calculs"]},
                {"id": "q7_at2", "q": "Question 7 : Sur 3 rouleaux et 7 symboles, la probabilite de Jackpot vaut :", "opts": ["Choisir...", "1/7", "1/49", "1/343"]},
                {"id": "q8_at2", "q": "Question 8 : Obtenir un nombre Pair ou Impair sont deux issues :", "opts": ["Choisir...", "Contraires (hors zero)", "Incompatibles", "Certaines"]},
                {"id": "q9_at2", "q": "Question 9 : Sur 10 lancers, la fluctuation d'echantillonnage est :", "opts": ["Choisir...", "Forte", "Nulle", "Inexistante"]},
                {"id": "q10_at2", "q": "Question 10 : La probabilite d'obtenir la case Verte (le Zero) vaut :", "opts": ["Choisir...", "0", "1/37", "1"]}
            ]
            random.shuffle(st.session_state.banque_quiz_at2)

        for item_quiz in st.session_state.banque_quiz_at2:
            cle_q = f"col_g_quiz_at2_{item_quiz['id']}"
            val_precedente = st.session_state.get(cle_q, "Choisir...")
            idx_defaut = item_quiz["opts"].index(val_precedente) if val_precedente in item_quiz["opts"] else 0

            st.selectbox(
                label=item_quiz["q"], 
                options=item_quiz["opts"], 
                index=idx_defaut, 
                key=cle_q,
                disabled=verrouille
            )

    # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LE TEXTE A TROUS CASINO
    # -------------------------------------------------------------------------
    with col_double_trous_at2:
        st.markdown("##### Analyse de cours Casino (10 menus)")
        
        if "bq_t_at2" not in st.session_state:
            st.session_state.bq_t_at2 = [
                {"id": "t1_at2", "label": "Trou A : Le numero Zero de la roulette porte la couleur :", "options": ["Choisir...", "Rouge", "Noir", "Vert"]},
                {"id": "t2_at2", "label": "Trou B : Le nombre total de compartiments rouges vaut :", "options": ["Choisir...", "12", "18", "36"]},
                {"id": "t3_at2", "label": "Trou C : Le nombre total de compartiments noirs vaut :", "options": ["Choisir...", "12", "18", "36"]},
                {"id": "t4_at2", "label": "Trou D : Les 10 000 lancers demontrent la loi des grands :", "options": ["Choisir...", "Nombres", "Hasards", "Ecarts"]},
                {"id": "t5_at2", "label": "Trou E : La probabilite d'un gain est un nombre entre :", "options": ["Choisir...", "-1 et 0", "0 et 1", "0 et 36"]},
                {"id": "t6_at2", "label": "Trou F : Plus l'echantillon grandit, plus la fluctuation :", "options": ["Choisir...", "Diminue", "Augmente", "S'annule"]},
                {"id": "t7_at2", "label": "Trou G : L'evenement contraire de 'Miser sur le Noir' inclut :", "options": ["Choisir...", "Rouge et Vert", "Passe", "Manque"]},
                {"id": "t8_at2", "label": "Trou H : Plus il y a de rouleaux, plus le Jackpot est :", "options": ["Choisir...", "Facile", "Difficile", "Stable"]},
                {"id": "t9_at2", "label": "Trou I : Tomber sur la face 38 a la roulette est un evenement :", "options": ["Choisir...", "Certain", "Impossible", "Probable"]},
                {"id": "t10_at2", "label": "Trou J : Le tapis de la roulette comporte une case unique pour le :", "options": ["Choisir...", "As", "Jeton", "Zero"]}
            ]
            random.shuffle(st.session_state.bq_t_at2)

        for item_trous in st.session_state.bq_t_at2:
            cle_t = f"col_d_trous_at2_{item_trous['id']}"
            val_precedente_t = st.session_state.get(cle_t, "Choisir...")
            idx_defaut_t = item_trous["options"].index(val_precedente_t) if val_precedente_t in item_trous["options"] else 0

            st.selectbox(
                label=item_trous["label"], 
                options=item_trous["options"], 
                index=idx_defaut_t, 
                key=cle_t,
                disabled=verrouille
            )

def afficher_questions_atelier3(verrouille=False):
    col_maitre_quiz_at3, col_double_trous_at3 = st.columns(2)

    # Récupération des données dynamiques de l'exercice s'il est généré
    if "solution_courante" in st.session_state:
        sol_m = st.session_state.solution_courante
        val_A = f"{sol_m[(0, 2)]:.2f}"
        val_B = f"{sol_m[(2, 0)]:.2f}"
        val_A_et_B = f"{sol_m[(0, 0)]:.2f}"
        val_A_et_Bbar = f"{sol_m[(0, 1)]:.2f}"
        val_Abar_et_B = f"{sol_m[(1, 0)]:.2f}"
        val_Abar_et_Bbar = f"{sol_m[(1, 1)]:.2f}"
        val_Abar = f"{sol_m[(1, 2)]:.2f}"
    else:
        val_A = val_B = val_A_et_B = val_A_et_Bbar = val_Abar_et_B = val_Abar_et_Bbar = val_Abar = "0.50"

    # Extraction contextuelle de la filière sélectionnée
    filiere_active = st.session_state.get("var_filiere_selectbox", "Conducteur Routier")
    contextes_phrases = {
        "Conducteur Routier": {
            "A": "le camion roule a l'Euro 6 (eco)", "B": "le trajet est regional",
            "phrase_A": "le camion soit un vehicule Euro 6", "phrase_B": "le trajet soit regional"
        },
        "Maintenance des Véhicules": {
            "A": "la panne est d'origine electrique", "B": "le vehicule est un utilitaire leger",
            "phrase_A": "la panne soit d'origine electrique", "phrase_B": "le vehicule soit un utilitaire leger"
        },
        "Travaux Publics (TP)": {
            "A": "le chantier utilise une pelle hydraulique", "B": "le sol est rocheux",
            "phrase_A": "le chantier utilise une pelle hydraulique", "phrase_B": "le sol soit rocheux"
        }
    }
    ctx_courant = contextes_phrases.get(filiere_active, contextes_phrases["Conducteur Routier"])

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LE QUIZ THEORIQUE SYNCHRONISÉ AVEC LE TABLEAU
    # -------------------------------------------------------------------------
    with col_maitre_quiz_at3:
        st.subheader("Quiz theorique (10 questions) - Atelier 3")
        st.write("Repondez aux questions liees aux probabilites de votre enonce :")

        # Régénération de la banque basée sur les vraies probabilités de la grille
        st.session_state.banque_quiz_at3 = [
            {"id": "q1_at3", "q": f"Question 1 : Quelle est la probabilite que {ctx_courant['phrase_A']} ?", "opts": ["Choisir...", val_A, val_B, "1.00"]},
            {"id": "q2_at3", "q": f"Question 2 : Quelle est la probabilite que {ctx_courant['phrase_B']} ?", "opts": ["Choisir...", val_A, val_B, "0.00"]},
            {"id": "q3_at3", "q": "Question 3 : Que vaut la probabilite de l'intersection P(A ∩ B) ?", "opts": ["Choisir...", val_A_et_B, val_A_et_Bbar, "1.00"]},
            {"id": "q4_at3", "q": f"Question 4 : Que vaut la probabilite que {ctx_courant['phrase_A']} et que l'evenement B ne se realise pas ?", "opts": ["Choisir...", val_A_et_B, val_A_et_Bbar, val_Abar_et_Bbar]},
            {"id": "q5_at3", "q": "Question 5 : Par convention, la somme totale de toutes les probabilites de l'univers vaut :", "opts": ["Choisir...", "0.00", "0.50", "1.00"]},
            {"id": "q6_at3", "q": "Question 6 : L'evenement contraire de l'evenement B se note mathematiquement :", "opts": ["Choisir...", "B̄", "Ā", "A ∩ B"]},
            {"id": "q7_at3", "q": "Question 7 : Si deux evenements ne peuvent pas se realiser en même temps, ils sont qualifies d' :", "opts": ["Choisir...", "Incompatibles", "Independants", "Certains"]},
            {"id": "q8_at3", "q": "Question 8 : Que vaut la probabilite de l'intersection P(Ā ∩ B) ?", "opts": ["Choisir...", val_Abar_et_B, val_A_et_B, val_B]},
            {"id": "q9_at3", "q": "Question 9 : Plus le nombre d'enregistrements reels augmente, plus la frequence observee :", "opts": ["Choisir...", "Se rapproche de la probabilite", "S'eloigne vers l'infini", "Reste a zero"]},
            {"id": "q10_at3", "q": "Question 10 : Une probabilite de 0.20 correspond a un pourcentage de :", "opts": ["Choisir...", "2%", "20%", "200%"]}
        ]

        for item_quiz in st.session_state.banque_quiz_at3:
            cle_q = f"col_g_quiz_at3_{item_quiz['id']}"
            val_precedente = st.session_state.get(cle_q, "Choisir...")
            idx_defaut = item_quiz["opts"].index(val_precedente) if val_precedente in item_quiz["opts"] else 0

            st.selectbox(
                label=item_quiz["q"], 
                options=item_quiz["opts"], 
                index=idx_defaut, 
                key=cle_q,
                disabled=verrouille
            )

    # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LE TEXTE A TROUS SYNCHRONISÉ AVEC LE CONTEXTE
    # -------------------------------------------------------------------------
    with col_double_trous_at3:
        st.markdown("##### Analyse de cours (10 menus) - Atelier 3")

        # Régénération de la synthèse basée sur les intitulés et les totaux
        st.session_state.bq_t_at3 = [
            {"id": "t1_at3", "label": "Trou A : Le total de la colonne B se calcule en faisant la somme de P(A ∩ B) et de :", "options": ["Choisir...", "P(Ā ∩ B)", "P(A ∩ B̄)", "1.00"]},
            {"id": "t2_at3", "label": "Trou B : La probabilite globale de l'evenement contraire P(Ā) vaut :", "options": ["Choisir...", val_Abar, "1.00", "0.00"]},
            {"id": "t3_at3", "label": "Trou C : La probabilite de l'intersection des deux contraires P(Ā ∩ B̄) vaut :", "options": ["Choisir...", val_Abar_et_Bbar, val_A_et_B, "1.00"]},
            {"id": "t4_at3", "label": "Trou D : Dans la grille croisee, la valeur finale situee tout en bas a droite vaut toujours :", "options": ["Choisir...", "0.00", "0.50", "1.00"]},
            {"id": "t5_at3", "label": "Trou E : L'intersection de deux evenements utilise le symbole mathematique :", "options": ["Choisir...", "∩ (Inter)", "∪ (Union)", "+"]},
            {"id": "t6_at3", "label": "Trou F : Trouver une valeur manquante dans une ligne se fait par une simple :", "options": ["Choisir...", "Soustraction", "Multiplication", "Division"]},
            {"id": "t7_at3", "label": "Trou G : L'intitule de la ligne de l'evenement A correspond a :", "options": ["Choisir...", ctx_courant["A"], ctx_courant["B"], "Le total"]},
            {"id": "t8_at3", "label": "Trou H : L'intitule de la colonne de l'evenement B correspond a :", "options": ["Choisir...", ctx_courant["B"], ctx_courant["A"], "Le total"]},
            {"id": "t9_at3", "label": "Trou I : Un evenement dont la probabilite calculee est egale a 1 est qualifie d' :", "options": ["Choisir...", "Certain", "Impossible", "Incertain"]},
            {"id": "t10_at3", "label": "Trou J : Toutes les probabilites de la grille croisee sont obligatoirement positives ou :", "options": ["Choisir...", "Nulles", "Negatives", "Infinies"]}
        ]

        for item_trous in st.session_state.bq_t_at3:
            cle_t = f"col_d_trous_at3_{item_trous['id']}"
            val_precedente_t = st.session_state.get(cle_t, "Choisir...")
            idx_defaut_t = item_trous["options"].index(val_precedente_t) if val_precedente_t in item_trous["options"] else 0

            st.selectbox(
                label=item_trous["label"], 
                options=item_trous["options"], 
                index=idx_defaut_t, 
                key=cle_t,
                disabled=verrouille
            )

def afficher_questions_atelier4(verrouille=False):
    col_maitre_quiz_at4, col_double_trous_at4 = st.columns(2)

    # # Récupération des données dynamiques de l'exercice s'il est généré
    if "solution_courante" in st.session_state:
        sol_m = st.session_state.solution_courante
        val_A = f"{sol_m.get('p_A', 0.50):.2f}"
        val_B = f"{sol_m.get('p_B', 0.50):.2f}"
        val_S_A = f"{sol_m.get('p_S_A', 0.10):.2f}"
        val_Sbar_A = f"{sol_m.get('p_Sbar_A', 0.90):.2f}"
        val_S_B = f"{sol_m.get('p_S_B', 0.15):.2f}"
        val_Sbar_B = f"{sol_m.get('p_Sbar_B', 0.85):.2f}"
        val_A_et_S = f"{sol_m.get('p_A_et_S', 0.05):.4f}"
        val_A_et_Sbar = f"{sol_m.get('p_A_et_Sbar', 0.45):.4f}"
    else:
        val_A = val_B = val_S_A = val_Sbar_A = val_S_B = val_Sbar_B = "0.50"
        val_A_et_S = val_A_et_Sbar = "0.2500"

    # # Extraction contextuelle de la filière sélectionnée
    filiere_active = st.session_state.get("var_filiere_selectbox", "Conducteur Routier")
    contextes_phrases = {
        "Conducteur Routier": {
            "phrase_A": "l'equipement soit de type tracteur recent (A)",
            "phrase_B": "l'equipement soit de type tracteur ancien (B)",
            "phrase_S": "rencontrer une anomalie moteur (S)"
        },
        "Maintenance": {
            "phrase_A": "la machine appartienne a l'atelier CN (A)",
            "phrase_B": "la machine appartienne a l'atelier Conditionnement (B)",
            "phrase_S": "subir une panne hydraulique (S)"
        },
        "Travaux Publics": {
            "phrase_A": "l'engin soit une pelleteuse (A)",
            "phrase_B": "l'engin soit une chargeuse (B)",
            "phrase_S": "subir une rupture de flexible (S)"
        }
    }
    ctx_courant = contextes_phrases.get(filiere_active, contextes_phrases["Conducteur Routier"])

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LE QUIZ THEORIQUE SYNCHRONISE AVEC L'ARBRE
    # -------------------------------------------------------------------------
    with col_maitre_quiz_at4:
        st.subheader("Quiz theorique (10 questions) - Atelier 4")
        st.write("Repondez aux questions liees aux probabilites de votre arbre :")

        if "banque_quiz_at4" not in st.session_state:
            liste_brute_q4 = [
                {"id": "q1_at4", "q": f"Question 1 : Quelle est la probabilite que {ctx_courant['phrase_A']} ?", "opts": ["Choisir...", val_A, val_B, "1.00", "0.00"]},
                {"id": "q2_at4", "q": f"Question 2 : Quelle est la probabilite conditionnelle que l'engin vienne a {ctx_courant['phrase_S']} sachant que c'est un profil A ?", "opts": ["Choisir...", val_S_A, val_Sbar_A, val_A]},
                {"id": "q3_at4", "q": f"Question 3 : Quelle est la probabilite de l'intersection contenant A et S simultanement ?", "opts": ["Choisir...", val_A_et_S, val_A_et_Sbar, val_S_A]},
                {"id": "q4_at4", "q": f"Question 4 : Que vaut la probabilite que {ctx_courant['phrase_B']} sachant que P(A) est connue ?", "opts": ["Choisir...", val_B, val_A, "1.00"]},
                {"id": "q5_at4", "q": "Question 5 : Par convention, la somme des probabilites des branches issues d'un meme nœud vaut :", "opts": ["Choisir...", "0", "0.5", "1", "Depend du nœud"]},
                {"id": "q6_at4", "q": "Question 6 : Pour calculer la probabilite d'un chemin complet (intersection), il faut :", "opts": ["Choisir...", "Additionner", "Multiplier", "Soustraire", "Diviser"]},
                {"id": "q7_at4", "q": "Question 7 : Une probabilite inscrite sur une branche de second niveau est qualifiee de :", "opts": ["Choisir...", "Simple", "Conditionnelle", "Intersection", "Marginale"]},
                {"id": "q8_at4", "q": "Question 8 : La formule des probabilites totales s'applique en effectuant la somme de :", "opts": ["Choisir...", "Toutes les branches", "Toutes les intersections menant a l'evenement", "Deux valeurs simples"]},
                {"id": "q9_at4", "q": "Question 9 : Si deux evenements A et B sont independants, alors P_B(A) correspond a :", "opts": ["Choisir...", "P(A)", "P(B)", "P(A ∩ B)", "1"]},
                {"id": "q10_at4", "q": "Question 10 : La somme totale de toutes les feuilles terminales (issues) d'un arbre vaut :", "opts": ["Choisir...", "0", "0.5", "1", "100"]}
            ]
            st.session_state.banque_quiz_at4 = liste_brute_q4

        dict_quiz_at4 = {}
        for item_quiz in st.session_state.banque_quiz_at4:
            cle_q = f"col_g_quiz_at4_{item_quiz['id']}"
            val_precedente = st.session_state.get(cle_q, "Choisir...")
            idx_defaut = item_quiz["opts"].index(val_precedente) if val_precedente in item_quiz["opts"] else 0

            st.selectbox(
                label=item_quiz["q"],
                options=item_quiz["opts"],
                index=idx_defaut,
                key=cle_q,
                disabled=verrouille
            )
            dict_quiz_at4[item_quiz["id"]] = st.session_state[cle_q]

    # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LE TEXTE A TROUS D'ANALYSE DE COURS (ATELIER 4)
    # -------------------------------------------------------------------------
    with col_double_trous_at4:
        st.subheader("Texte a trous (10 menus) - Atelier 4")
        st.write("Completez l'analyse de votre arbre pondere :")

        if "banque_trous_at4" not in st.session_state:
            st.session_state.banque_trous_at4 = [
                {"id": "t1_at4", "label": "Trou A : Un arbre de probabilite est compose de nœuds et de :", "options": ["Choisir...", "Faces", "Branches", "Cases", "Calculs"]},
                {"id": "t2_at4", "label": "Trou B : Le point de depart situe tout a gauche de l'arbre s'appelle le nœud :", "options": ["Choisir...", "Initial (Racine)", "Secondaire", "Final", "Contraire"]},
                {"id": "t3_at4", "label": "Trou C : Le long d'un chemin, les probabilites doivent obligatoirement se :", "options": ["Choisir...", "Additionner", "Soustraire", "Multiplier", "Diviser"]},
                {"id": "t4_at4", "label": "Trou D : Pour reunir plusieurs chemins menant a un meme resultat, on doit les :", "options": ["Choisir...", "Additionner", "Multiplier", "Soustraire", "Ignorer"]},
                {"id": "t5_at4", "label": "Trou E : La somme des probabilites de tous les chemins terminaux vaut toujours :", "options": ["Choisir...", "0", "0.5", "1", "100"]},
                {"id": "t6_at4", "label": "Trou F : P(B sachant A) represente la probabilite de B sachant que A est :", "options": ["Choisir...", "Impossible", "Realise", "Incertain", "Echoue"]},
                {"id": "t7_at4", "label": "Trou G : Si deux evenements ne peuvent pas se produire en meme temps, ils sont :", "options": ["Choisir...", "Independants", "Incompatibles", "Certains", "Contraires"]},
                {"id": "t8_at4", "label": "Trou H : Une branche reliant le premier niveau au second porte une valeur de probabilite :", "options": ["Choisir...", "Simple", "Conditionnelle", "Intersection", "Totale"]},
                {"id": "t9_at4", "label": "Trou I : L'extremite finale complete d'un parcours de branches s'appelle un :", "options": ["Choisir...", "Nœud", "Chemin (Issue)", "Vecteur", "Tapis"]},
                {"id": "t10_at4", "label": "Trou J : Un arbre pondere est un outil visuel servant a denombrer les situations de :", "options": ["Choisir...", "Proportionnalite", "Hasard (Probabilites)", "Geometrie", "Pourcentages"]}
            ]

        dict_trous_at4 = {}
        for item_trous in st.session_state.banque_trous_at4:
            cle_t = f"col_d_trous_at4_{item_trous['id']}"
            val_precedente_t = st.session_state.get(cle_t, "Choisir...")
            idx_defaut_t = item_trous["options"].index(val_precedente_t) if val_precedente_t in item_trous["options"] else 0

            st.selectbox(
                label=item_trous["label"],
                options=item_trous["options"],
                index=idx_defaut_t,
                key=cle_t,
                disabled=verrouille
            )
            dict_trous_at4[item_trous["id"]] = st.session_state[cle_t]

    return dict_quiz_at4, dict_trous_at4


# =============================================================================
# ONGLET 0 : FORMULAIRE D'IDENTIFICATION DE L'ÉLÈVE
# =============================================================================
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
            key="btn_validation_identite_maitre",
            disabled=st.session_state.get("verrouille", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("verrouille", False):
                st.rerun()

with tab1:
    # 1. Garde-fou sécurité (Alignement : 4 espaces)


    st.header("1. Jeux de hasard 1 : Dé et Jeu de 32 cartes")
    
    # =========================================================================
    # INITIALISATION SECURISEE DES MEMOIRES DE STATISTIQUES (OBLIGATOIRE)
    # =========================================================================
    if "de_total_lancers" not in st.session_state:
        st.session_state.de_total_lancers = 0
    if "de_stats" not in st.session_state:
        st.session_state.de_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    if "dernier_de" not in st.session_state:
        st.session_state.dernier_de = None

    if "cartes_total_tirages" not in st.session_state:
        st.session_state.cartes_total_tirages = 0
    if "cartes_valeurs_stats" not in st.session_state:
        st.session_state.cartes_valeurs_stats = {"7": 0, "8": 0, "9": 0, "10": 0, "Valet": 0, "Dame": 0, "Roi": 0, "As": 0}
    if "cartes_couleurs_stats" not in st.session_state:
        st.session_state.cartes_couleurs_stats = {"Carreau": 0, "Pique": 0, "Coeur": 0, "Trefe": 0}
    if "derniere_carte" not in st.session_state:
        st.session_state.derniere_carte = None
        
    # =========================================================================
    # CONFIGURATION DES COLONNES ET DES BOUTONS DE JEU
    # =========================================================================

    col_de_gauche, col_de_droite = st.columns(2)

    with col_de_gauche:
        if st.button("Lancer le Dé libre", key="btn_lancer_de_unitaire_at1"):
            with st.spinner("Le de roule sur la table..."):
                placeholder_animation = st.empty()
                faces_animation = ["", "", "", "", "", ""]
                for _ in range(4):
                    faux_tirage = random.choice(faces_animation)
                    placeholder_animation.markdown(
                        f"""
                        <div style="background-color: #f1f5f9; border: 2px dashed #3b82f6; border-radius: 8px; padding: 20px; text-align: center; margin-top: 15px;">
                            <span style="font-size: 16px; font-weight: bold; color: #3b82f6; font-style: italic;">Suspense...</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(0.15)
                placeholder_animation.empty()

            tirage_de = random.randint(1, 6)
            st.session_state.dernier_de = tirage_de
            st.session_state.de_stats[tirage_de] += 1
            st.session_state.de_total_lancers += 1
            st.rerun()

        if st.session_state.get("dernier_de"):
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px; padding: 20px; text-align: center; margin-top: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <span style="font-size: 16px; font-weight: bold; color: #475569;">Resultat du lancer :</span><br>
                    <span style="font-size: 48px; font-weight: bold; color: #2563eb; line-height: 1.5;">[ {st.session_state.dernier_de} ]</span><br>
                    <span style="font-size: 18px; font-weight: bold; color: #1e3a8a; text-transform: uppercase;">Face {st.session_state.dernier_de}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_de_droite:
        st.markdown("**Pourcentages d'obtention du Dé :**")
        total_d = st.session_state.de_total_lancers
        if total_d > 0:
            for face in range(1, 7):
                cpt = st.session_state.de_stats.get(face, 0)
                pct = (cpt / total_d) * 100
                st.write(f"Face {face} : **{pct:.1f}%** ({cpt}/{total_d})")
        else:
            st.write("Aucun lancer effectue.")

    st.write("---")

    # =========================================================================
    # PARTIE B : LE JEU DE CARTES (Visuel à gauche, Statistiques à droite)
    # =========================================================================
    # CORRECTIF CRITIQUE : Déclaration explicite des deux colonnes pour les cartes
    col_carte_gauche, col_carte_droite = st.columns(2)

    with col_carte_gauche:
        if st.button("Tirer une Carte", key="btn_tirer_carte_unitaire_at1"):
            with st.spinner("Melange du paquet de 32 cartes..."):
                placeholder_carte = st.empty()
                for i in range(5):
                    statut_melange = "MELANGE EN COURS" if i % 2 == 0 else "COUPE DU PAQUET"
                    placeholder_carte.markdown(
                        f"""
                        <div style="background-color: #2563eb; border: 3px solid #ffffff; border-radius: 12px; padding: 30px; text-align: center; margin-top: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);">
                            <span style="font-size: 14px; font-weight: bold; color: #ffffff; letter-spacing: 1px; text-transform: uppercase;">{statut_melange}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(0.12)
                placeholder_carte.empty()

            valeurs_32 = ["7", "8", "9", "10", "Valet", "Dame", "Roi", "As"]
            couleurs_32 = ["Carreau", "Pique", "Coeur", "Trefe"]
            v_tiree = random.choice(valeurs_32)
            c_tiree = random.choice(couleurs_32)

            st.session_state.derniere_carte = {"valeur": v_tiree, "couleur": c_tiree}
            st.session_state.cartes_valeurs_stats[v_tiree] += 1
            st.session_state.cartes_couleurs_stats[c_tiree] += 1
            st.session_state.cartes_total_tirages += 1
            st.rerun()

        if st.session_state.get("derniere_carte"):
            v_c = st.session_state.derniere_carte["valeur"]
            c_c = st.session_state.derniere_carte["couleur"]
            couleur_theme = "#dc2626" if c_c in ["Carreau", "Coeur"] else "#0f172a"
            abreviation = "10" if v_c == "10" else v_c
            st.markdown(
                f"""
                <div style="background-color: #ffffff; border: 8px solid {couleur_theme}; border-radius: 16px; padding: 25px; text-align: center; margin-top: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); width: 100%; max-width: 220px; margin-left: auto; margin-right: auto;">
                    <div style="text-align: left; font-size: 18px; font-weight: bold; color: {couleur_theme}; margin-top: -15px; margin-left: -10px;">
                        {abreviation}<br><span style="font-size: 11px; text-transform: uppercase;">{c_c[:4]}</span>
                    </div>
                    <div style="font-size: 22px; font-weight: bold; color: {couleur_theme}; margin: 20px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                        {c_c}
                    </div>
                    <div style="font-size: 26px; font-weight: bold; color: #1e293b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">
                        {v_c}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            
    with col_carte_droite:
        st.markdown("**Pourcentages par Couleur / Valeur :**")
        total_c = st.session_state.cartes_total_tirages
        if total_c > 0:
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Couleurs :**")
                for col in ["Carreau", "Pique", "Coeur", "Trefe"]:
                    cpt = st.session_state.cartes_couleurs_stats[col]
                    st.write(f"{col} : **{(cpt/total_c)*100:.1f}%**")
            with c2:
                st.write("**Valeurs :**")
                for val in [
                    "7",
                    "8",
                    "9",
                    "10",
                    "Valet",
                    "Dame",
                    "Roi",
                    "As",
                ]:
                    cpt = st.session_state.cartes_valeurs_stats[val]
                    st.write(f"{val} : **{(cpt/total_c)*100:.1f}%**")
        else:
            st.write("Aucun tirage effectué. Cliquez sur le bouton.")

    # =========================================================================
    # PARTIE C : LOI DES GRANDS NOMBRES (GRAPHIQUE DES 10 000 LANCERS/TIRAGES)
    # =========================================================================
    st.write("---")
    st.subheader("Loi des Grands Nombres - Simulation de 10 000 événements")
    st.write(
        "Sélectionnez le mode pour observer la convergence des fréquences réelles vers les probabilités théoriques."
    )

    choix_simulation = st.radio(
        "Choisissez l'élément à simuler en masse :",
        options=["Dé (6 faces)", "Carte (Valeurs)", "Carte (Couleurs)"],
        horizontal=True,
        key="radio_choix_sim_10000",
    )

    if st.button(
        "Lancer la grande simulation de 10 000 tirages",
        key="btn_lancer_10000_at1",
    ):
        n_sim = 10000
        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)

        if choix_simulation == "Dé (6 faces)":
            resultats = [random.randint(1, 6) for _ in range(n_sim)]
            labels = ["1", "2", "3", "4", "5", "6"]
            freqs = [resultats.count(f) / n_sim for f in range(1, 7)]
            p_theo = 1.0 / 6.0

            ax.bar(labels, freqs, color="#3b82f6", edgecolor="#1d4ed8", width=0.5)
            ax.axhline(
                y=p_theo,
                color="#ef4444",
                linestyle="--",
                linewidth=1.5,
                label=f"Théorie (1/6 = {p_theo*100:.1f}%)",
            )
            ax.set_title(
                f"Dé libre : Répartition des fréquences sur {n_sim} lancers",
                fontweight="bold",
            )

        elif choix_simulation == "Carte (Valeurs)":
            valeurs = ["7", "8", "9", "10", "Valet", "Dame", "Roi", "As"]
            resultats = [random.choice(valeurs) for _ in range(n_sim)]
            freqs = [resultats.count(v) / n_sim for v in valeurs]
            p_theo = 1.0 / 8.0

            ax.bar(valeurs, freqs, color="#ec4899", edgecolor="#be185d", width=0.55)
            ax.axhline(
                y=p_theo,
                color="#10b981",
                linestyle="--",
                linewidth=1.5,
                label=f"Théorie (1/8 = {p_theo*100:.1f}%)",
            )
            ax.set_title(
                f"Jeu de 32 : Fréquence des Valeurs sur {n_sim} tirages",
                fontweight="bold",
            )

        elif choix_simulation == "Carte (Couleurs)":
            couleurs = ["Carreau", "Pique", "Coeur", "Trefe"]
            resultats = [random.choice(couleurs) for _ in range(n_sim)]
            freqs = [resultats.count(c) / n_sim for c in couleurs]
            p_theo = 1.0 / 4.0

            ax.bar(
                couleurs, freqs, color="#f59e0b", edgecolor="#b45309", width=0.45
            )
            ax.axhline(
                y=p_theo,
                color="#ef4444",
                linestyle="--",
                linewidth=1.5,
                label=f"Théorie (1/4 = {p_theo*100:.1f}%)",
            )
            ax.set_title(
                f"Jeu de 32 : Fréquence des Couleurs sur {n_sim} tirages",
                fontweight="bold",
            )

        ax.set_ylabel("Fréquence observée")
        ax.set_ylim(0, max(freqs) * 1.3)
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)


    if "at1_verrouille" not in st.session_state:
        st.session_state.at1_verrouille = False

    st.write("---")
    
    # Appel de la fonction : Modifiable ou Gelée dynamiquement au clic du bas
    afficher_questions_atelier1(verrouille=st.session_state.at1_verrouille)

        # =========================================================================
        # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML)
        # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at1 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de cet atelier.", 
        key="check_certif_at1_officiel",
        value=True if st.session_state.at1_verrouille else False,
        disabled=st.session_state.at1_verrouille
    )

    btn_clique_at1 = st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", 
        key="btn_export_at1_premium", 
        use_container_width=True,
        disabled=st.session_state.at1_verrouille
    )

    if btn_clique_at1 and not st.session_state.at1_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at1:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        else:
            st.session_state.at1_verrouille = True
            st.rerun()

    if st.session_state.at1_verrouille:
        score_quiz = 0
        verdicts_quiz = {}
        attendus_quiz = {
            "q1": "0.75", "q2": "3/6 (1/2)", "q3": "12/32 (3/8)", "q4": "5/6", "q5": "0 et 1",
            "q6": "Elementaire", "q7": "2/6 (1/3)", "q8_at1": "8/32 (1/4)", "q9": "1", "q10": "0.7"
        }
        for q_id, q_correct in attendus_quiz.items():
            saisie_q = st.session_state.get(f"col_g_quiz_{q_id}", "Choisir...")
            if saisie_q == q_correct:
                score_quiz += 1
                verdicts_quiz[q_id] = "CORRECT"
            else:
                verdicts_quiz[q_id] = "INCORRECT"

        score_trous = 0
        verdicts_trous = {}
        attendus_trous = {
            "t1": "6", "t2": "1/6", "t3": "32", "t4": "4", "t5": "8",
            "t6": "4/32 (1/8)", "t7": "8/32 (1/4)", "t8": "Certain", "t9": "Impossible", "t10": "1"
        }
        for t_id, t_correct in attendus_trous.items():
            saisie_t = st.session_state.get(f"col_d_trous_{t_id}", "Choisir...")
            if saisie_t == t_correct:
                score_trous += 1
                verdicts_trous[t_id] = "CORRECT"
            else:
                verdicts_trous[t_id] = "INCORRECT"

        note_finale_sur_20 = score_quiz + score_trous

        html_export_premium = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 1 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1 style="margin: 0; font-size: 22px;">Professeur Laurent GALLET</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 12px;">Scelle le : {timestamp_at1}</p>
                <div class="score-badge">NOTE<br><span style="font-size: 32px;">{note_finale_sur_20}</span> / 20</div>
            </div>

            <div class="sub-title">Detail des points acquis</div>
            <p style="font-size: 14px; background: white; padding: 12px; border-left: 4px solid #eab308;">
                &bull; Questionnaire de fractions (QCM) : <strong>{score_quiz} / 10</strong><br>
                &bull; Synthese de texte (Texte a trous) : <strong>{score_trous} / 10</strong>
            </p>

            <div class="sub-title">Statistiques des lancers de l'élève en direct</div>
            <p style="font-size: 13px; color: #475569;">
                Total lancers de de : {st.session_state.get("de_total_lancers", 0)} (Derniere face : {st.session_state.get("dernier_de", "Aucun")})<br>
                Total tirages de cartes : {st.session_state.get("cartes_total_tirages", 0)} (Derniere carte : {st.session_state.get("derniere_carte", "Aucune")})
            </p>

            <div class="sub-title">Partie 2 : Questionnaire de fractions (QCM)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule de la Question</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        questions_mapping = {
            "q1": "Chances 3 sur 4", "q2": "Probabilite Nombre pair au de",
            "q3": "Probabilite d'obtenir une Figure", "q4": "Evenement contraire d'obtenir 6",
            "q5": "Bornes d'une probabilite", "q6": "Nature de l'evenement 7 de Pique",
            "q7": "Multiple de 3 avec le de cubique", "q8_at1": "Tirer un Roi OU un As",
            "q9": "De truque : Somme totale des probas", "q10": "Evenement contraire de P(A) = 0.3"
        }

        for idx_q, q_id in enumerate(["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8_at1", "q9", "q10"], 1):
            saisie = st.session_state.get(f"col_g_quiz_{q_id}", "Choisir...")
            attendu = attendus_quiz[q_id]
            verdict = verdicts_quiz.get(q_id, "INCORRECT")
            v_class = "status-correct" if verdict == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_q}</td><td>{questions_mapping[q_id]}</td><td>{saisie}</td><td>{attendu}</td><td style="text-align: center;" class="{v_class}">{verdict}</td></tr>
            """

        html_export_premium += """
            </table>
            <div class="sub-title">Partie 3 : Synthese de texte (Texte a trous)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule du Trou</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        trous_mapping = {
            "t1": "Nombre de faces du de", "t2": "Probabilite face 6",
            "t3": "Nombre total de cartes", "t4": "Nombre de familles",
            "t5": "Nombre de cartes par famille", "t6": "Probabilite As",
            "t7": "Probabilite Coeur", "t8": "Evenement probabilite 1",
            "t9": "Evenement probabilite 0", "t10": "Somme probas faces de"
        }

        for idx_t, t_id in enumerate(["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10"], 1):
            saisie_t = st.session_state.get(f"col_d_trous_{t_id}", "Choisir...")
            attendu_t = attendus_trous[t_id]
            verdict_t = verdicts_trous.get(t_id, "INCORRECT")
            v_class_t = "status-correct" if verdict_t == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_t}</td><td>{trous_mapping[t_id]}</td><td>{saisie_t}</td><td>{attendu_t}</td><td style="text-align: center;" class="{v_class_t}">{verdict_t}</td></tr>
            """

        html_export_premium += """
            </table>
        </body>
        </html>
        """

        st.success("Bilan de l'Atelier 1 verrouille et genere avec succes !")
        st.download_button(
            label="TELECHARGER LE RAPPORT INTERACTIF ATELIER 1 (.HTML)",
            data=html_export_premium,
            file_name=f"Rapport_Atelier1_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )




                    
with tab2:


    st.header("2. Jeux de hasard 2 : Roulette et Casino Machine")

    # =========================================================================
    # INITIALISATION UNIFIEE DES MEMOIRES DE SESSION
    # =========================================================================
    if "atelier2_valide" not in st.session_state:
        st.session_state.atelier2_valide = False
    if "roulette_stats_gains" not in st.session_state:
        st.session_state.roulette_stats_gains = {"GAGNE": 0, "PERDU": 0}
    if "roulette_dernier_numero" not in st.session_state:
        st.session_state.roulette_dernier_numero = 0
    if "roulette_derniere_couleur" not in st.session_state:
        st.session_state.roulette_derniere_couleur = "Vert"
    if "slot_dernier_tirage" not in st.session_state:
        st.session_state.slot_dernier_tirage = []
    if "slot_stats_gains" not in st.session_state:
        st.session_state.slot_stats_gains = {"JACKPOT": 0, "PETIT GAIN": 0, "PERDU": 0}
    # Séparation en deux colonnes maîtresses étanches
    col_master_roulette, col_master_slot = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LA ROULETTE (TAPIS ET ROUE COMPLÈTEMENT ANIMÉE)
    # -------------------------------------------------------------------------
    with col_master_roulette:
        st.subheader("La Roulette de Casino")
        st.write("Misez sur une categorie ou sur un numero unique :")

        type_pari = st.radio(
            "Type de pari :",
            options=["Categorie", "Numero Unique"],
            horizontal=True,
            key="radio_type_pari_at2_final"
        )

        pari_selectionne = ""
        numero_choisi = 0

        if type_pari == "Categorie":
            pari_selectionne = st.selectbox(
                "Selectionnez votre groupe de numeros :",
                options=["Rouge", "Noir", "Pair (Even)", "Impair (Odd)", "Manque (1-18)", "Passe (19-36)"],
                key="selectbox_categorie_roulette"
            )
            texte_jeton = pari_selectionne
        else:
            numero_choisi = st.number_input(
                "Saisissez votre numero unique (0 a 36) :",
                min_value=0, max_value=36, value=7, step=1,
                key="num_input_roulette_at2_unique"
            )
            pari_selectionne = f"{numero_choisi}"
            texte_jeton = f"NUMERO {numero_choisi}"

        # Rendu du Tapis de mise horizontal bloqué en largeur
        html_tapis_regle = f"""
        <div style="background-color: #065f46; border: 4px solid #ffffff; border-radius: 8px; width: 480px; padding: 15px; font-family: Arial, sans-serif; box-shadow: 0 8px 16px rgba(0,0,0,0.3); margin-bottom: 20px;">
            <table style="width: 100%; border-collapse: collapse; text-align: center; color: #ffffff; font-weight: bold;">
                <tr style="height: 35px;">
                    <td rowspan="3" style="background-color: #16a34a; border: 2px solid #ffffff; width: 40px; font-size: 18px;">0</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">3</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">6</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">9</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">12</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">15</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">18</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">21</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">24</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">27</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">30</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">33</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">36</td>
                </tr>
                <tr style="height: 35px;">
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">2</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">5</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">8</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">11</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">14</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">17</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">20</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">23</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">26</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">29</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">32</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">35</td>
                </tr>
                <tr style="height: 35px;">
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">1</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">4</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">7</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">10</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">13</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">16</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">19</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">22</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">25</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">28</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">31</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">34</td>
                </tr>
                <tr style="height: 30px; font-size: 11px;">
                    <td></td>
                    <td colspan="4" style="border: 2px solid #ffffff;">1st 12</td>
                    <td colspan="4" style="border: 2px solid #ffffff;">2nd 12</td>
                    <td colspan="4" style="border: 2px solid #ffffff;">3rd 12</td>
                </tr>
                <tr style="height: 30px; font-size: 10px;">
                    <td></td>
                    <td colspan="2" style="border: 2px solid #ffffff;">1-18</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">EVEN</td>
                    <td colspan="2" style="background-color: #dc2626; border: 2px solid #ffffff;">ROUGE</td>
                    <td colspan="2" style="background-color: #0f172a; border: 2px solid #ffffff;">NOIR</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">ODD</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">19-36</td>
                </tr>
            </table>
            <div style="text-align: center; margin-top: 15px;">
                <span style="background-color: #f59e0b; color: #0f172a; padding: 4px 15px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid #ffffff;">
                    JETON : {texte_jeton.upper()}
                </span>
            </div>
        </div>
        """
        st.components.v1.html(html_tapis_regle, height=250)

        # Structure fixe de la roulette européenne
        ordre_cylindre = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        rouges_roulette = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        pas_angulaire = 360.0 / 37.0

        # ZONE DE L'ANIMATION INTERACTIVE
        placeholder_roue = st.empty()

        # 1. INITIALISATION DE SÉCURITÉ AU REPOS (DÈS LE DÉMARRAGE DU TP)
        if st.session_state.roulette_dernier_numero is None:
            fig_repos, ax_repos = plt.subplots(figsize=(4, 4), dpi=100)
            ax_repos.axis("off")
            fig_repos.patch.set_facecolor('#065f46')
            ax_repos.set_facecolor('#065f46')

            ax_repos.add_patch(plt.Circle((0, 0), radius=1.8, color="#3e2723", zorder=1))
            ax_repos.add_patch(plt.Circle((0, 0), radius=1.5, color="#1a0c00", zorder=2))

            for idx_s, num_case in enumerate(ordre_cylindre):
                theta1 = idx_s * pas_angulaire
                theta2 = (idx_s + 1) * pas_angulaire
                c_seg = "#16a34a" if num_case == 0 else ("#dc2626" if num_case in rouges_roulette else "#0f172a")
                ax_repos.add_patch(patches.Wedge((0, 0), r=1.5, theta1=theta1, theta2=theta2, width=0.35, facecolor=c_seg, edgecolor="none", zorder=3))

                angle_txt = np.radians(theta1 + pas_angulaire / 2.0)
                ax_repos.text(1.32 * np.cos(angle_txt), 1.32 * np.sin(angle_txt), f"{num_case}", color="#ffffff", fontsize=6, fontweight="bold", ha="center", va="center", rotation=(theta1 + pas_angulaire / 2.0) - 90, zorder=5)

            for idx_s in range(38):
                a_rad = np.radians(idx_s * pas_angulaire)
                ax_repos.plot([1.15 * np.cos(a_rad), 1.5 * np.cos(a_rad)], [1.15 * np.sin(a_rad), 1.5 * np.sin(a_rad)], color="#f59e0b", linewidth=1, zorder=4)

            ax_repos.add_patch(plt.Circle((0, 0), radius=1.1, color="#b5651d", zorder=6))
            ax_repos.add_patch(plt.Circle((0, 0), radius=0.8, color="#ffe082", zorder=7))

            angle_zero_rad = np.radians((ordre_cylindre.index(0) * pas_angulaire) + (pas_angulaire / 2.0))
            ax_repos.add_patch(plt.Circle((1.32 * np.cos(angle_zero_rad), 1.32 * np.sin(angle_zero_rad)), radius=0.05, color="#ffffff", zorder=12))
            ax_repos.text(0, -2.2, "ROULETTE PRETE\nMisez sur le tapis puis lancez !", color="#ffffff", fontsize=10, fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#cbd5e1", lw=1.5), zorder=14)

            plt.tight_layout()
            with placeholder_roue:
                st.pyplot(fig_repos, clear_figure=True)

        # 2. DECLENCHEMENT DU BOUTON DE LANCER
        if st.button("LANCER LA ROULETTE", key="btn_lancer_roulette_officiel_at2", use_container_width=True):
            numero_tire = random.randint(0, 36)
            st.session_state.roulette_dernier_numero = numero_tire
            couleur_finale = "Vert" if numero_tire == 0 else ("Red" if numero_tire in rouges_roulette else "Black")
            st.session_state.roulette_derniere_couleur = couleur_finale

            # Animation de la bille en mouvement
            for frame in range(10):
                fig_anim, ax_anim = plt.subplots(figsize=(4, 4), dpi=100)
                ax_anim.axis("off")
                fig_anim.patch.set_facecolor('#065f46')
                ax_anim.set_facecolor('#065f46')

                ax_anim.add_patch(plt.Circle((0, 0), radius=1.8, color="#3e2723", zorder=1))
                ax_anim.add_patch(plt.Circle((0, 0), radius=1.5, color="#1a0c00", zorder=2))

                for idx_s, num_case in enumerate(ordre_cylindre):
                    theta1 = idx_s * pas_angulaire
                    theta2 = (idx_s + 1) * pas_angulaire
                    c_seg = "#16a34a" if num_case == 0 else ("#dc2626" if num_case in rouges_roulette else "#0f172a")
                    ax_anim.add_patch(patches.Wedge((0, 0), r=1.5, theta1=theta1, theta2=theta2, width=0.35, facecolor=c_seg, edgecolor="none", zorder=3))
                    
                    angle_txt = np.radians(theta1 + pas_angulaire / 2.0)
                    ax_anim.text(1.32 * np.cos(angle_txt), 1.32 * np.sin(angle_txt), f"{num_case}", color="#ffffff", fontsize=6, fontweight="bold", ha="center", va="center", rotation=(theta1 + pas_angulaire / 2.0) - 90, zorder=5)

                for idx_s in range(38):
                    a_rad = np.radians(idx_s * pas_angulaire)
                    ax_anim.plot([1.15 * np.cos(a_rad), 1.5 * np.cos(a_rad)], [1.15 * np.sin(a_rad), 1.5 * np.sin(a_rad)], color="#f59e0b", linewidth=1, zorder=4)

                ax_anim.add_patch(plt.Circle((0, 0), radius=1.1, color="#b5651d", zorder=6))
                ax_anim.add_patch(plt.Circle((0, 0), radius=0.8, color="#ffe082", zorder=7))

                angle_bille_anim = np.radians(frame * 72.0)
                ax_anim.add_patch(plt.Circle((1.32 * np.cos(angle_bille_anim), 1.32 * np.sin(angle_bille_anim)), radius=0.06, color="#ffffff", zorder=12))

                plt.tight_layout()
                with placeholder_roue:
                    st.pyplot(fig_anim, clear_figure=True)
                time.sleep(0.08)

            # Analyse des gains unitaires
            victoire = False
            if type_pari == "Categorie":
                if pari_selectionne == "Rouge" and couleur_finale == "Red": victoire = True
                elif pari_selectionne == "Noir" and couleur_finale == "Black": victoire = True
                elif pari_selectionne == "Pair (Even)" and numero_tire != 0 and numero_tire % 2 == 0: victoire = True
                elif pari_selectionne == "Impair (Odd)" and numero_tire % 2 != 0: victoire = True
                elif pari_selectionne == "Manque (1-18)" and 1 <= numero_tire <= 18: victoire = True
                elif pari_selectionne == "Passe (19-36)" and 19 <= numero_tire <= 36: victoire = True
            else:
                if numero_tire == numero_choisi: victoire = True

            if victoire:
                st.session_state.roulette_stats_gains["GAGNE"] += 1
                st.session_state.roulette_verdict_texte = f"GAGNE ! (+ {35 if type_pari != 'Categorie' else 1} jetons)"
            else:
                st.session_state.roulette_stats_gains["PERDU"] += 1
                st.session_state.roulette_verdict_texte = "PERDU"

            # 3. TRACÉ EXCLUSIF DE LA ROULETTE FINALE GAGNANTE (ANTI-CLIGNOTEMENT CRITIQUE)
            fig_fin, ax_fin = plt.subplots(figsize=(4, 4), dpi=100)
            ax_fin.axis("off")
            fig_fin.patch.set_facecolor('#065f46')
            ax_fin.set_facecolor('#065f46')

            ax_fin.add_patch(plt.Circle((0, 0), radius=1.8, color="#3e2723", zorder=1))
            ax_fin.add_patch(plt.Circle((0, 0), radius=1.5, color="#1a0c00", zorder=2))

            index_case_gagnante = 0
            for idx_s, num_case in enumerate(ordre_cylindre):
                theta1 = idx_s * pas_angulaire
                theta2 = (idx_s + 1) * pas_angulaire
                if num_case == numero_tire:
                    index_case_gagnante = idx_s

                c_seg = "#16a34a" if num_case == 0 else ("#dc2626" if num_case in rouges_roulette else "#0f172a")
                ax_fin.add_patch(patches.Wedge((0, 0), r=1.5, theta1=theta1, theta2=theta2, width=0.35, facecolor=c_seg, edgecolor="none", zorder=3))

                angle_txt = np.radians(theta1 + pas_angulaire / 2.0)
                ax_fin.text(1.32 * np.cos(angle_txt), 1.32 * np.sin(angle_txt), f"{num_case}", color="#ffffff", fontsize=6, fontweight="bold", ha="center", va="center", rotation=(theta1 + pas_angulaire / 2.0) - 90, zorder=5)

            for idx_s in range(38):
                a_rad = np.radians(idx_s * pas_angulaire)
                ax_fin.plot([1.15 * np.cos(a_rad), 1.5 * np.cos(a_rad)], [1.15 * np.sin(a_rad), 1.5 * np.sin(a_rad)], color="#f59e0b", linewidth=1, zorder=4)

            ax_fin.add_patch(plt.Circle((0, 0), radius=1.1, color="#b5651d", zorder=6))
            ax_fin.add_patch(plt.Circle((0, 0), radius=0.8, color="#ffe082", zorder=7))

            angle_bille_fixe_rad = np.radians((index_case_gagnante * pas_angulaire) + (pas_angulaire / 2.0))
            ax_fin.add_patch(plt.Circle((1.32 * np.cos(angle_bille_fixe_rad), 1.32 * np.sin(angle_bille_fixe_rad)), radius=0.05, color="#ffffff", zorder=12))

            trad_c = "VERT" if numero_tire == 0 else ("ROUGE" if numero_tire in rouges_roulette else "NOIR")
            bg_badge = "#16a34a" if trad_c == "VERT" else ("#dc2626" if trad_c == "ROUGE" else "#0f172a")
            ax_fin.text(0, -2.2, f"NUMERO : {numero_tire} ({trad_c})\n{st.session_state.roulette_verdict_texte}", color="#ffffff", fontsize=10, fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_badge, edgecolor="#f59e0b", lw=1.5), zorder=14)
            
            plt.tight_layout()
            with placeholder_roue:
                st.pyplot(fig_fin, clear_figure=True)
        # =========================================================================
        # 4. COMPTEUR ET GRAPHIQUE EN DIRECT POUR LES LANCERS UNITAIRES DE LA ROULETTE
        # =========================================================================
        st.write("")
        fig_r, ax_r = plt.subplots(figsize=(4, 2.5), dpi=100)
        labels_r = ["GAGNE", "PERDU"]
        counts_r = [
            st.session_state.roulette_stats_gains.get("GAGNE", 0), 
            st.session_state.roulette_stats_gains.get("PERDU", 0)]
            
        ax_r.bar(labels_r, counts_r, color=["#10b981", "#ef4444"], edgecolor="#111827", width=0.4)
        ax_r.set_title("Bilan lancers unitaires", fontsize=9, fontweight="bold")
        ax_r.grid(axis="y", linestyle=":", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_r, clear_figure=True)

            # Ligne de séparation réglementaire avant la simulation
        st.write("---")

        # =========================================================================
        # 5. SIMULATION DE MASSE INTERACTIVE (10 000 TIRAGES SUR LE PARI EN COURS)
        # =========================================================================
        st.write("---")
        st.markdown("**Simulation de masse (10 000 tirages) :**")
        
        if type_pari == "Categorie":
            texte_pari_sim = f"la categorie '{pari_selectionne}'"
        else:
            texte_pari_sim = f"le Numero unique {numero_choisi}"
            
        st.write(f"Ce simulateur va tester 10 000 lancers consecutifs sur {texte_pari_sim}.")

        if st.button("Lancer la simulation (10 000 Roulettes)", key="btn_sim_10000_roulette_maitre", use_container_width=True):
            n_sim = 10000
            cpt_victoires = 0
            p_theorique = 18.0 / 37.0 if type_pari == "Categorie" else 1.0 / 37.0
            rouges_list = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

            for _ in range(n_sim):
                tirage = random.randint(0, 36)
                victoire_sim = False
                
                if type_pari == "Categorie":
                    if tirage != 0:
                        is_rouge = tirage in rouges_list
                        if pari_selectionne == "Rouge" and is_rouge: victoire_sim = True
                        elif pari_selectionne == "Noir" and not is_rouge: victoire_sim = True
                        elif pari_selectionne == "Pair (Even)" and tirage % 2 == 0: victoire_sim = True
                        elif pari_selectionne == "Impair (Odd)" and tirage % 2 != 0: victoire_sim = True
                        elif pari_selectionne == "Manque (1-18)" and tirage <= 18: victoire_sim = True
                        elif pari_selectionne == "Passe (19-36)" and tirage > 18: victoire_sim = True
                else:
                    if tirage == numero_choisi: 
                        victoire_sim = True
                        
                if victoire_sim: 
                    cpt_victoires += 1

            fig_sim_r, ax_sim_r = plt.subplots(figsize=(4, 2.5), dpi=100)
            ax_sim_r.bar(["GAGNE", "PERDU"], [cpt_victoires/n_sim, (n_sim-cpt_victoires)/n_sim], color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
            ax_sim_r.axhline(y=p_theorique, color="#ef4444", linestyle="--", label=f"Theorie ({p_theorique*100:.1f}%)")
            ax_sim_r.set_ylim(0, 1.1)
            ax_sim_r.legend(loc="upper right", fontsize=7)
            plt.tight_layout()
            
            st.pyplot(fig_sim_r, clear_figure=True)
            st.write(f"Frequence obtenue : **{(cpt_victoires/n_sim)*100:.2f}%** ({cpt_victoires} victoires).")
 # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LA SLOT MACHINE CONFIGURABLE
    # -------------------------------------------------------------------------
    with col_master_slot:
        st.markdown("<h3 style='text-align: center; color: #eab308; font-family: Arial; font-weight: bold;'>CASINO MACHINE</h3>", unsafe_allow_html=True)
        st.write("")

        # Curseurs de configuration dynamique de la machine
        n_rouleaux = st.slider("Nombre de rouleaux (colonnes) :", min_value=3, max_value=5, value=3, step=1, key="slider_slot_rouleaux")
        n_symboles = st.slider("Nombre de symboles disponibles :", min_value=4, max_value=8, value=7, step=1, key="slider_slot_symboles")
        st.write("")

        # BOUTON DU BRAS MÉCANIQUE EN TEXTE BRUT
        # BOUTON DU BRAS MÉCANIQUE EN TEXTE BRUT
        if st.button("ACTIONNER LE BRAS (SPIN)", key="btn_actionner_slot_premium", use_container_width=True):
            with st.spinner("Defilement des rouleaux mecaniques..."):
                placeholder_slot = st.empty()
                
                # Effet d'animation de rotation : les chiffres s'emballent
                for _ in range(5):
                    faux_tirage = [str(random.randint(1, n_symboles)) for _ in range(n_rouleaux)]
                    
                    # Construction propre du conteneur HTML global pour l'animation
                    html_animation = """
                    <div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0;">
                    """
                    
                    for chiffre in faux_tirage:
                        html_animation += f"""
                        <div style="background-color: #27272a; border: 3px solid #eab308; border-radius: 12px; width: 80px; height: 120px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                            <span style="font-family: Arial, sans-serif; font-size: 48px; font-weight: bold; color: #a1a1aa;">{chiffre}</span>
                        </div>
                        """
                    
                    # Fermeture correcte du conteneur global APRES le dessin des chiffres
                    html_animation += "</div>"
                    
                    # CORRECTIF ABSOLU : On utilise st.components.v1.html pour forcer l'affichage graphique réel pendant le mouvement
                    with placeholder_slot:
                        st.components.v1.html(html_animation, height=140)
                    
                    time.sleep(0.10)
                
                placeholder_slot.empty()

            # Tirage réel basé sur la configuration de l'élève
            tirage_reel = [random.randint(1, n_symboles) for _ in range(n_rouleaux)]
            st.session_state.slot_dernier_tirage = tirage_reel

            # Calcul des règles de gains de la machine
            if len(set(tirage_reel)) == 1:
                st.session_state.slot_verdict = "JACKPOT !"
                st.session_state.slot_couleur_theme = "#eab308"
            elif len(set(tirage_reel)) < len(tirage_reel):
                st.session_state.slot_verdict = "PETIT GAIN"
                st.session_state.slot_couleur_theme = "#3b82f6"
            else:
                st.session_state.slot_verdict = "PERDU"
                st.session_state.slot_couleur_theme = "#ef4444"
            st.rerun()

        # RENDU FIXE DE LA MACHINE AU REPOS OU APRES UN TIRAGE (Calque sur l'image)
        if not st.session_state.get("slot_dernier_tirage"):
            affichage_chiffres = ["7" for _ in range(n_rouleaux)]
            verdict_actuel = "Appuyez sur le bras pour lancer !"
            couleur_cadre = "#eab308"
        else:
            affichage_chiffres = [str(x) for x in st.session_state.slot_dernier_tirage]
            verdict_actuel = st.session_state.slot_verdict
            couleur_cadre = st.session_state.slot_couleur_theme

        # Reconstruction propre et etanche du tableau fixe pour eviter l'affichage de code brut
        html_machine = """
        <div style="display: flex; justify-content: center; gap: 15px; margin: 10px 0;">
        """
        
        for chiffre in affichage_chiffres:
            html_machine += f"""
            <div style="background-color: #2e2e38; border: 4px solid {couleur_cadre}; border-radius: 14px; width: 90px; height: 135px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(0,0,0,0.4);">
                <span style="font-family: Arial, sans-serif; font-size: 56px; font-weight: bold; color: #ffffff; line-height: 1;">{chiffre}</span>
            </div>
            """
        
        html_machine += "</div>"

        # CORRECTIF ABSOLU : On force l'affichage graphique reel via st.components.v1.html
        st.components.v1.html(html_machine, height=160)

        # Affichage du bandeau de resultat inferieur
        st.markdown(
            f"""
            <div style='text-align: center; font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; color: #ffffff; letter-spacing: 0.5px; margin-top: 15px;'>
                {verdict_actuel}
            </div>
            """,
            unsafe_allow_html=True
        )

        # COMPTEUR ET GRAPHIQUE EN DIRECT POUR LES SPINS UNITAIRES DE LA SLOT MACHINE
        if "slot_stats_gains" not in st.session_state:
            st.session_state.slot_stats_gains = {"JACKPOT": 0, "PETIT GAIN": 0, "PERDU": 0}

        # Synchronisation au repos après un lancer réel
        if st.session_state.get("slot_dernier_tirage"):
            v_s = st.session_state.slot_verdict
            if v_s == "JACKPOT !":
                st.session_state.slot_stats_gains["JACKPOT"] = st.session_state.slot_stats_gains.get("JACKPOT", 0) + 1
            elif v_s == "PETIT GAIN":
                st.session_state.slot_stats_gains["PETIT GAIN"] = st.session_state.slot_stats_gains.get("PETIT GAIN", 0) + 1
            else:
                st.session_state.slot_stats_gains["PERDU"] = st.session_state.slot_stats_gains.get("PERDU", 0) + 1
            # On vide l'état temporaire pour ne pas incrémenter en boucle au rechargement
            st.session_state.slot_dernier_tirage = []

        st.write("")
        fig_s, ax_s = plt.subplots(figsize=(4.5, 3), dpi=100)
        labels_s = ["JACKPOT", "PETIT GAIN", "PERDU"]
        counts_s = [
            st.session_state.slot_stats_gains.get("JACKPOT", 0),
            st.session_state.slot_stats_gains.get("PETIT GAIN", 0),
            st.session_state.slot_stats_gains.get("PERDU", 0)
        ]
        
        ax_s.bar(labels_s, counts_s, color=["#eab308", "#3b82f6", "#cbd5e1"], edgecolor="#1e293b", width=0.45)
        ax_s.set_title("Bilan cumulé de la Slot Machine", fontsize=10, fontweight="bold")
        ax_s.set_ylabel("Nombre de spins")
        ax_s.grid(axis="y", linestyle=":", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_s, clear_figure=True)
        
        st.write("---")
        st.markdown("**Simulation de masse de la Slot Machine (10 000 lancers) :**")
        st.write(f"Ce simulateur va tester 10 000 spins avec votre configuration : **{n_rouleaux} rouleaux** et **{n_symboles} symboles**.")

        if st.button("Lancer la simulation (10 000 Spins)", key="btn_sim_10000_slot"):
            n_sim = 10000
            cpt_jackpot = 0
            cpt_petit_gain = 0
            cpt_perdu = 0

            # Calcul des probabilités théoriques réelles selon vos curseurs
            p_theorique_jackpot = 1.0 / (n_symboles ** (n_rouleaux - 1))

            # Simulation mathématique en boucle des 10 000 tirages
            for _ in range(n_sim):
                tirage_sim = [random.randint(1, n_symboles) for _ in range(n_rouleaux)]
                nb_uniques = len(set(tirage_sim))
                
                if nb_uniques == 1:
                    cpt_jackpot += 1
                elif nb_uniques < n_rouleaux:
                    cpt_petit_gain += 1
                else:
                    cpt_perdu += 1

            # Calcul des fréquences observées
            f_jackpot = cpt_jackpot / n_sim
            f_petit = cpt_petit_gain / n_sim
            f_perdu = cpt_perdu / n_sim

            # Tracé du graphique Matplotlib
            fig_sim_s, ax_sim_s = plt.subplots(figsize=(4.5, 3), dpi=100)
            labels_sim_s = ["JACKPOT", "PETIT GAIN", "PERDU"]
            freqs_sim_s = [f_jackpot, f_petit, f_perdu]

            ax_sim_s.bar(labels_sim_s, freqs_sim_s, color=["#eab308", "#3b82f6", "#cbd5e1"], edgecolor="#1e293b", width=0.5)
            ax_sim_s.axhline(y=p_theorique_jackpot, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Theorie Jackpot ({p_theorique_jackpot*100:.3f}%)")
            
            ax_sim_s.set_title("Loi des Grands Nombres : Slot Machine", fontsize=9, fontweight="bold")
            ax_sim_s.set_ylabel("Frequence observee")
            ax_sim_s.set_ylim(0, max(freqs_sim_s) * 1.25)
            ax_sim_s.legend(loc="upper right", fontsize=7)
            ax_sim_s.grid(axis="y", linestyle=":", alpha=0.5)
            plt.tight_layout()

            # Rendu immédiat sous le visuel de la slot
            st.pyplot(fig_sim_s, clear_figure=True)
            st.write(f"Resultat final : **{cpt_jackpot} Jackpots** obtenus sur 10 000 spins (Frequence : **{f_jackpot*100:.3f}%**).")

    # =========================================================================
    # CONFIGURATION DES COLONNES DU QUIZ ET DU TEXTE A TROUS - ATELIER 2
    # =========================================================================
    if "at2_verrouille" not in st.session_state:
        st.session_state.at2_verrouille = False

    st.write("---")
    
    afficher_questions_atelier2(verrouille=st.session_state.at2_verrouille)

    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML)
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de cet atelier.", 
        key="check_certif_at2_officiel",
        value=True if st.session_state.at2_verrouille else False,
        disabled=st.session_state.at2_verrouille
    )

    btn_clique = st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", 
        key="btn_export_at2_premium", 
        use_container_width=True,
        disabled=st.session_state.at2_verrouille
    )

    if btn_clique and not st.session_state.at2_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at2:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        else:
            st.session_state.at2_verrouille = True
            st.rerun()

    if st.session_state.at2_verrouille:
        score_quiz_at2 = 0
        verdicts_quiz_at2 = {}
        attendus_quiz_at2 = {
            "q1_at2": "37", "q2_at2": "1/37", "q3_at2": "18/37", "q4_at2": "La case Zero", "q5_at2": "La probabilite theoretique",
            "q6_at2": "Nombres", "q7_at2": "1/343", "q8_at2": "Contraires (hors zero)", "q9_at2": "Forte", "q10_at2": "1/37"
        }
        for q_id, q_correct in attendus_quiz_at2.items():
            saisie_q = st.session_state.get(f"col_g_quiz_at2_{q_id}", "Choisir...")
            if saisie_q == q_correct:
                score_quiz_at2 += 1
                verdicts_quiz_at2[q_id] = "CORRECT"
            else:
                verdicts_quiz_at2[q_id] = "INCORRECT"

        score_trous_at2 = 0
        verdicts_trous_at2 = {}
        attendus_trous_at2 = {
            "t1_at2": "Vert", "t2_at2": "18", "t3_at2": "18", "t4_at2": "Nombres", "t5_at2": "0 et 1",
            "t6_at2": "Diminue", "t7_at2": "Rouge et Vert", "t8_at2": "Difficile", "t9_at2": "Impossible", "t10_at2": "Zero"
        }
        for t_id, t_correct in attendus_trous_at2.items():
            saisie_t = st.session_state.get(f"col_d_trous_at2_{t_id}", "Choisir...")
            if saisie_t == t_correct:
                score_trous_at2 += 1
                verdicts_trous_at2[t_id] = "CORRECT"
            else:
                verdicts_trous_at2[t_id] = "INCORRECT"

        note_finale_sur_20 = score_quiz_at2 + score_trous_at2

        html_export_premium = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1 style="margin: 0; font-size: 22px;">Professeur Laurent GALLET</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 12px;">Scelle le : {timestamp_at2}</p>
                <div class="score-badge">NOTE<br><span style="font-size: 32px;">{note_finale_sur_20}</span> / 20</div>
            </div>

            <div class="sub-title">Detail des points acquis</div>
            <p style="font-size: 14px; background: white; padding: 12px; border-left: 4px solid #eab308;">
                &bull; Questionnaire de la roulette (QCM) : <strong>{score_quiz_at2} / 10</strong><br>
                &bull; Synthese de texte (Texte a trous) : <strong>{score_trous_at2} / 10</strong>
            </p>

            <div class="sub-title">Partie 2 : Questionnaire de la roulette (QCM)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule de la Question</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        for idx_q, q_id in enumerate(["q1_at2", "q2_at2", "q3_at2", "q4_at2", "q5_at2", "q6_at2", "q7_at2", "q8_at2", "q9_at2", "q10_at2"], 1):
            saisie = st.session_state.get(f"col_g_quiz_at2_{q_id}", "Choisir...")
            attendu = attendus_quiz_at2[q_id]
            verdict = verdicts_quiz_at2.get(q_id, "INCORRECT")
            v_class = "status-correct" if verdict == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_q}</td><td>Question {idx_q}</td><td>{saisie}</td><td>{attendu}</td><td style="text-align: center;" class="{v_class}">{verdict}</td></tr>
            """

        html_export_premium += """
            </table>
            <div class="sub-title">Partie 3 : Synthese de texte (Texte a trous)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule du Trou</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        for idx_t, t_id in enumerate(["t1_at2", "t2_at2", "t3_at2", "t4_at2", "t5_at2", "t6_at2", "t7_at2", "t8_at2", "t9_at2", "t10_at2"], 1):
            saisie_t = st.session_state.get(f"col_d_trous_at2_{t_id}", "Choisir...")
            attendu_t = attendus_trous_at2[t_id]
            verdict_t = verdicts_trous_at2.get(t_id, "INCORRECT")
            v_class_t = "status-correct" if verdict_t == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_t}</td><td>Trou {idx_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td style="text-align: center;" class="{v_class_t}">{verdict_t}</td></tr>
            """

        html_export_premium += """
            </table>
        </body>
        </html>
        """

        st.success("Bilan de l'Atelier 2 verrouille et genere avec succes !")
        st.download_button(
            label="TELECHARGER LE RAPPORT INTERACTIF ATELIER 2 (.HTML)",
            data=html_export_premium,
            file_name=f"Rapport_Atelier2_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab3:

    st.header("Atelier 3 - Probabilites Conditionnelles et Filieres")

    # Initialisation des variables d'etat specifiques a l'Atelier 3
    if "at3_verrouille" not in st.session_state:
        st.session_state.at3_verrouille = False

    # Menu deroulant pour le choix de la filiere
    filiere_choisie = st.selectbox(
        "Choisissez votre filiere professionnelle :",
        ["Conducteur Routier", "Maintenance des Vehicules", "Travaux Publics (TP)"],
        key="var_filiere_selectbox",
        disabled=st.session_state.at3_verrouille
    )

    # Bouton pour generer un nouvel exercice aleatoire
    if st.button("GENERER UN NOUVEL EXERCICE", key="btn_generer_at3", disabled=st.session_state.at3_verrouille):
        # 1. Generation controlee des 4 cases interieures pour que la somme fasse strictement 1.00
        p_A_et_B = round(random.uniform(0.15, 0.25), 2)
        p_A_et_Bbar = round(random.uniform(0.20, 0.30), 2)
        p_Abar_et_B = round(random.uniform(0.15, 0.25), 2)
        
        # La 4eme case est deduite pour garantir que le total general fasse exactement 1.00
        p_Abar_et_Bbar = round(1.00 - (p_A_et_B + p_A_et_Bbar + p_Abar_et_B), 2)
        
        # 2. Calcul automatique et exact des totaux marginaux
        p_A = round(p_A_et_B + p_A_et_Bbar, 2)
        p_Abar = round(p_Abar_et_B + p_Abar_et_Bbar, 2)
        p_B = round(p_A_et_B + p_Abar_et_B, 2)
        p_Bbar = round(p_A_et_Bbar + p_Abar_et_Bbar, 2)
        
        # Ajustement microscopique pour eviter les micro-ecarts d'arrondi
        if round(p_A + p_Abar, 2) != 1.00:
            p_Abar = round(1.00 - p_A, 2)
        if round(p_B + p_Bbar, 2) != 1.00:
            p_Bbar = round(1.00 - p_B, 2)

        # 3. Sauvegarde de la matrice de solution officielle (coordonnees x, y)
        st.session_state.solution_courante = {
            (0, 0): p_A_et_B,    (0, 1): p_A_et_Bbar,    (0, 2): p_A,
            (1, 0): p_Abar_et_B, (1, 1): p_Abar_et_Bbar, (1, 2): p_Abar,
            (2, 0): p_B,         (2, 1): p_Bbar,         (2, 2): 1.0
        }

        # Definition des contextes textuels professionnels
        contextes = {
            "Conducteur Routier": {"A": "le camion roule a l'Euro 6 (eco)", "B": "le trajet est regional"},
            "Maintenance des Véhicules": {"A": "la panne est d'origine electrique", "B": "le vehicule est un utilitaire leger"},
            "Travaux Publics (TP)": {"A": "le chantier utilise une pelle hydraulique", "B": "le sol est rocheux"}
        }
        ctx = contextes[filiere_choisie]

        # 4. Selection des scenarios d'enonces (Barres rehaussees via notation $)
        scenario = random.randint(1, 5)
        if scenario == 1:
            texte_donnees = f"- La probabilite de l'intersection $P(A \cap B)$ est de {p_A_et_B:.2f}.\n- La probabilite globale $P(B)$ est de {p_B:.2f}.\n- La probabilite globale $P(A)$ est de {p_A:.2f}."
        elif scenario == 2:
            texte_donnees = f"- La probabilite de l'intersection $P(A \cap \overline{{B}})$ est de {p_A_et_Bbar:.2f}.\n- La probabilite globale $P(A)$ est de {p_A:.2f}.\n- La probabilite globale $P(\overline{{B}})$ est de {p_Bbar:.2f}."
        elif scenario == 3:
            texte_donnees = f"- La probabilite de l'intersection $P(\overline{{A}} \cap \overline{{B}})$ est de {p_Abar_et_Bbar:.2f}.\n- La probabilite globale $P(A)$ est de {p_A:.2f}.\n- La probabilite globale $P(B)$ est de {p_B:.2f}."
        elif scenario == 4:
            texte_donnees = f"- La probabilite de l'intersection $P(\overline{{A}} \cap B)$ est de {p_Abar_et_B:.2f}.\n- La probabilite globale $P(\overline{{A}})$ est de {p_Abar:.2f}.\n- La probabilite globale $P(B)$ est de {p_B:.2f}."
        else:
            texte_donnees = f"- La probabilite de l'intersection $P(A \cap B)$ est de {p_A_et_B:.2f}.\n- La probabilite de l'intersection $P(\overline{{A}} \cap B)$ est de {p_Abar_et_B:.2f}.\n- La probabilite globale $P(\overline{{B}})$ est de {p_Bbar:.2f}."

        # Assemblage final de l'enonce textuel stable
        st.session_state.enonce_textuel_at3 = (
            f"[Enonce Filiere : {filiere_choisie}]\n\n"
            f"Soit l'evenement A : \"{ctx['A']}\" et l'evenement B : \"{ctx['B']}\".\n\n"
            f"Les enregistrements indiquent que :\n"
            f"{texte_donnees}\n\n"
            f"Exercice : Utilisez ces 3 valeurs pour completer la grille ci-dessous."
        )

        # Fixation des banques pour eviter le bug de la note a 0.00
        val_A_str, val_B_str = f"{p_A:.2f}", f"{p_B:.2f}"
        val_A_et_B_str, val_A_et_Bbar_str = f"{p_A_et_B:.2f}", f"{p_A_et_Bbar:.2f}"
        val_Abar_et_B_str, val_Abar_et_Bbar_str = f"{p_Abar_et_B:.2f}", f"{p_Abar_et_Bbar:.2f}"
        val_Abar_str = f"{p_Abar:.2f}"

        st.session_state.banque_quiz_at3 = [
            {"id": "q1_at3", "q": f"Question 1 : Quelle est la probabilite de l'evenement global A ?", "opts": ["Choisir...", val_A_str, val_B_str, "1.00"]},
            {"id": "q2_at3", "q": f"Question 2 : Quelle est la probabilite de l'evenement global B ?", "opts": ["Choisir...", val_A_str, val_B_str, "0.00"]},
            {"id": "q3_at3", "q": "Question 3 : Que vaut la probabilite de l'intersection P(A ∩ B) ?", "opts": ["Choisir...", val_A_et_B_str, val_A_et_Bbar_str, "1.00"]},
            {"id": "q4_at3", "q": "Question 4 : Que vaut la probabilite de l'intersection mixte P(A ∩ B̄) ?", "opts": ["Choisir...", val_A_et_B_str, val_A_et_Bbar_str, val_Abar_et_Bbar_str]},
            {"id": "q5_at3", "q": "Question 5 : Par convention, la somme totale de toutes les probabilites de l'univers vaut :", "opts": ["Choisir...", "0.00", "0.50", "1.00"]},
            {"id": "q6_at3", "q": "Question 6 : L'evenement contraire de l'evenement B se note mathematiquement :", "opts": ["Choisir...", "B̄", "Ā", "A ∩ B"]},
            {"id": "q7_at3", "q": "Question 7 : Si deux evenements ne peuvent pas se realiser en même temps, ils sont qualifies d' :", "opts": ["Choisir...", "Incompatibles", "Independants", "Certains"]},
            {"id": "q8_at3", "q": "Question 8 : Que vaut la probabilite de l'intersection P(Ā ∩ B) ?", "opts": ["Choisir...", val_Abar_et_B_str, val_A_et_B_str, val_B_str]},
            {"id": "q9_at3", "q": "Question 9 : Plus le nombre d'enregistrements reels augmente, plus la frequence observee :", "opts": ["Choisir...", "Se rapproche de la probabilite", "S'eloigne vers l'infini", "Reste a zero"]},
            {"id": "q10_at3", "q": "Question 10 : Une probabilite de 0.20 correspond a un pourcentage de :", "opts": ["Choisir...", "2%", "20%", "200%"]}
        ]

        st.session_state.bq_t_at3 = [
            {"id": "t1_at3", "label": "Trou A : Le total de la colonne B se calcule en faisant la somme de P(A ∩ B) et de :", "options": ["Choisir...", "P(Ā ∩ B)", "P(A ∩ B̄)", "1.00"]},
            {"id": "t2_at3", "label": "Trou B : La probabilite globale de l'evenement contraire P(Ā) vaut :", "options": ["Choisir...", val_Abar_str, "1.00", "0.00"]},
            {"id": "t3_at3", "label": "Trou C : La probabilite de l'intersection des deux contraires P(Ā ∩ B̄) vaut :", "options": ["Choisir...", val_Abar_et_Bbar_str, val_A_et_B_str, "1.00"]},
            {"id": "t4_at3", "label": "Trou D : Dans la grille croisee, la valeur finale situee tout en bas a droite vaut toujours :", "options": ["Choisir...", "0.00", "0.50", "1.00"]},
            {"id": "t5_at3", "label": "Trou E : L'intersection de deux evenements utilise le symbole mathematique :", "options": ["Choisir...", "∩ (Inter)", "∪ (Union)", "+"]},
            {"id": "t6_at3", "label": "Trou F : Trouver une valeur manquante dans une ligne se fait par une simple :", "options": ["Choisir...", "Soustraction", "Multiplication", "Division"]},
            {"id": "t7_at3", "label": "Trou G : L'intitule de la ligne de l'evenement A correspond a :", "options": ["Choisir...", ctx["A"], ctx["B"], "Le total"]},
            {"id": "t8_at3", "label": "Trou H : L'intitule de la colonne de l'evenement B correspond a :", "options": ["Choisir...", ctx["B"], ctx["A"], "Le total"]},
            {"id": "t9_at3", "label": "Trou I : Un evenement dont la probabilite calculee est egale a 1 est qualifie d' :", "options": ["Choisir...", "Certain", "Impossible", "Incertain"]},
            {"id": "t10_at3", "label": "Trou J : Toutes les probabilites de la grille croisee sont obligatoirement positives ou :", "options": ["Choisir...", "Nulles", "Negatives", "Infinies"]}
        ]

        # Réinitialisation des cases élèves
        for i in range(1, 10):
            st.session_state[f"cell_at3_{i}"] = ""
        st.rerun()

    # Affichage de l'enonce courant s'il existe
    if "enonce_textuel_at3" in st.session_state:
        st.info(st.session_state.enonce_textuel_at3)
    else:
        st.warning("Veuillez cliquer sur le bouton ci-dessus pour generer votre enonce d'exercice.")

    st.write("---")
    
    # =========================================================================
    # PARTIE 1 : LA GRILLE INTERACTIVE VIDE A COMPLETER (TABLEAU A DOUBLE ENTREE)
    # =========================================================================
    st.subheader("Grille de probabilites croisees a completer")
    
    # En-tete des colonnes du tableau
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c1: st.markdown("<center>**B**</center>", unsafe_allow_html=True)
    with c2: st.markdown("<center>**<span style='display:inline-block; border-top:2px solid black; padding-top:4px; line-height:1;'>B</span> (Contraire)**</center>", unsafe_allow_html=True)
    with c3: st.markdown("<center>**TOTAL**</center>", unsafe_allow_html=True)

    # Initialisation des verdicts visuels si non valide
    if "verdicts_visuels_at3" not in st.session_state:
        st.session_state.verdicts_visuels_at3 = {}

    # Fonction pour afficher la saisie de l'eleve OU la correction attendue si c'est faux
    def afficher_case_colore(label, cle_cell, coord_solution):
        val_saisie = st.session_state.get(cle_cell, "").strip()
        saisie_affichage = val_saisie if val_saisie != "" else "Vide"
        verdict = st.session_state.verdicts_visuels_at3.get(cle_cell, "NORMAL")
        
        if verdict == "CORRECT":
            st.success(f"{saisie_affichage}")
        elif verdict == "INCORRECT":
            # On recupere la vraie valeur dans la solution courante pour l'afficher
            if "solution_courante" in st.session_state:
                vraie_valeur = st.session_state.solution_courante.get(coord_solution, 0.00)
                st.error(f"{saisie_affichage} -> Attendu : {vraie_valeur:.2f}")
            else:
                st.error(f"{saisie_affichage}")
        else:
            st.text_input(label, key=cle_cell, label_visibility="collapsed", disabled=st.session_state.at3_verrouille)

    # Ligne 1 : Evenement A
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c0: st.markdown("<div style='padding-top:10px;'>**A**</div>", unsafe_allow_html=True)
    with c1: afficher_case_colore("A_B", "cell_at3_1", (0, 0))
    with c2: afficher_case_colore("A_Bbar", "cell_at3_2", (0, 1))
    with c3: afficher_case_colore("A_total", "cell_at3_3", (0, 2))

    # Ligne 2 : Evenement Abar
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c0: st.markdown("<div style='padding-top:10px;'>**<span style='display:inline-block; border-top:2px solid black; padding-top:4px; line-height:1;'>A</span> (Contraire)**</div>", unsafe_allow_html=True)
    with c1: afficher_case_colore("Abar_B", "cell_at3_4", (1, 0))
    with c2: afficher_case_colore("Abar_Bbar", "cell_at3_5", (1, 1))
    with c3: afficher_case_colore("Abar_total", "cell_at3_6", (1, 2))

    # Ligne 3 : Totaux horizontaux
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c0: st.markdown("<div style='padding-top:10px;'>**TOTAL**</div>", unsafe_allow_html=True)
    with c1: afficher_case_colore("B_total", "cell_at3_7", (2, 0))
    with c2: afficher_case_colore("Bbar_total", "cell_at3_8", (2, 1))
    with c3: st.success("1.00")

    st.write("")
    
    # BOUTON DE CORRECTION INTERMEDIAIRE POUR LE TABLEAU
    if st.button("VERIFIER LES REPONSES DU TABLEAU", key="btn_verifier_grille_at3", disabled=st.session_state.at3_verrouille):
        if "solution_courante" not in st.session_state:
            st.error("Veuillez d'abord generer un exercice avec le bouton en haut.")
        else:
            sol = st.session_state.solution_courante
            mapping_cases = {
                "cell_at3_1": (0, 0), "cell_at3_2": (0, 1), "cell_at3_3": (0, 2),
                "cell_at3_4": (1, 0), "cell_at3_5": (1, 1), "cell_at3_6": (1, 2),
                "cell_at3_7": (2, 0), "cell_at3_8": (2, 1)
            }
            
            nouveaux_verdicts = {}
            for cell_k, coord in mapping_cases.items():
                saisie = st.session_state.get(cell_k, "").strip().replace(",", ".")
                try:
                    if abs(float(saisie) - float(sol[coord])) <= 0.01:
                        nouveaux_verdicts[cell_k] = "CORRECT"
                    else:
                        nouveaux_verdicts[cell_k] = "INCORRECT"
                except ValueError:
                    nouveaux_verdicts[cell_k] = "INCORRECT"
            
            st.session_state.verdicts_visuels_at3 = nouveaux_verdicts
            st.rerun()
    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML) - ATELIER 3
    # =========================================================================
    st.write("---")
    afficher_questions_atelier3(verrouille=st.session_state.at3_verrouille)
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at3 = st.checkbox(
        "Je certifie avoir complete l'integralite du tableau et des questionnaires de cet atelier.", 
        key="check_certif_at3_officiel",
        value=True if st.session_state.at3_verrouille else False,
        disabled=st.session_state.at3_verrouille
    )

    btn_clique_at3 = st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", 
        key="btn_export_at3_premium", 
        use_container_width=True,
        disabled=st.session_state.at3_verrouille
    )

    if btn_clique_at3 and not st.session_state.at3_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at3:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        elif "solution_courante" not in st.session_state:
            st.error("Action refusee : Veuillez d'abord generer un exercice en cliquant sur le bouton en haut.")
        else:
            st.session_state.at3_verrouille = True
            st.rerun()

    if st.session_state.at3_verrouille:
        sol = st.session_state.solution_courante
        
        # =========================================================================
        # 1. EVALUATION DE LA GRILLE (10 POINTS MAXIMUM)
        # =========================================================================
        mapping_correction = {
            "cell_at3_1": ((0, 0), "P(A ∩ B)"), 
            "cell_at3_2": ((0, 1), "P(A ∩ B̄)"), 
            "cell_at3_3": ((0, 2), "P(A)"),
            "cell_at3_4": ((1, 0), "P(Ā ∩ B)"), 
            "cell_at3_5": ((1, 1), "P(Ā ∩ B̄)"), 
            "cell_at3_6": ((1, 2), "P(Ā)"),
            "cell_at3_7": ((2, 0), "P(B)"),     
            "cell_at3_8": ((2, 1), "P(B̄)")
        }
        score_tableau = 0.0
        verdicts_tableau = {}
        for key_state, (coordonnees, libelle) in mapping_correction.items():
            saisie_brute = st.session_state.get(key_state, "").strip().replace(",", ".")
            try:
                # 1.25 point par case exacte (Total sur 10 points pour les 8 cases)
                if abs(float(saisie_brute) - float(sol[coordonnees])) <= 0.01:
                    score_tableau += 1.25
                    verdicts_tableau[key_state] = "CORRECT"
                else: 
                    verdicts_tableau[key_state] = "INCORRECT"
            except (ValueError, KeyError): 
                verdicts_tableau[key_state] = "INCORRECT"

        # =========================================================================
        # 2. EVALUATION DU QUIZ QCM (10 POINTS MAXIMUM - LECTURE DIRECTE)
        # =========================================================================
        val_A, val_B = f"{sol[(0, 2)]:.2f}", f"{sol[(2, 0)]:.2f}"
        val_A_et_B, val_A_et_Bbar = f"{sol[(0, 0)]:.2f}", f"{sol[(0, 1)]:.2f}"
        val_Abar_et_B = f"{sol[(1, 0)]:.2f}"
        
        attendus_quiz_at3 = {
            "q1_at3": val_A, "q2_at3": val_B, "q3_at3": val_A_et_B, "q4_at3": val_A_et_Bbar, "q5_at3": "1.00",
            "q6_at3": "B̄", "q7_at3": "Incompatibles", "q8_at3": val_Abar_et_B, "q9_at3": "Se rapproche de la probabilite", "q10_at3": "20%"
        }
        score_quiz = 0.0
        verdicts_quiz = {}
        for q_id, q_correct in attendus_quiz_at3.items():
            # CORRECTION : Lecture directe et securisee dans le session_state globale
            saisie_q = st.session_state.get(f"col_g_quiz_at3_{q_id}", "Choisir...")
            if saisie_q == q_correct:
                score_quiz += 1.0 # 1 point entier par bonne reponse
                verdicts_quiz[q_id] = "CORRECT"
            else: 
                verdicts_quiz[q_id] = "INCORRECT"

        # =========================================================================
        # 3. EVALUATION DU TEXTE A TROUS (10 POINTS MAXIMUM - LECTURE DIRECTE)
        # =========================================================================
        filiere_active = st.session_state.get("var_filiere_selectbox", "Conducteur Routier")
        contextes_phrases = {
            "Conducteur Routier": {"A": "le camion roule a l'Euro 6 (eco)", "B": "le trajet est regional"},
            "Maintenance des Véhicules": {"A": "la panne est d'origine electrique", "B": "le vehicule est un utilitaire leger"},
            "Travaux Publics (TP)": {"A": "le chantier utilise une pelle hydraulique", "B": "le sol est rocheux"}
        }
        ctx_c = contextes_phrases.get(filiere_active, contextes_phrases["Conducteur Routier"])
        val_Abar_et_Bbar = f"{sol[(1, 1)]:.2f}"
        
        attendus_trous_at3 = {
            "t1_at3": "P(Ā ∩ B)", "t2_at3": f"{sol[(1, 2)]:.2f}", "t3_at3": val_Abar_et_Bbar, "t4_at3": "1.00", "t5_at3": "∩ (Inter)",
            "t6_at3": "Soustraction", "t7_at3": ctx_c["A"], "t8_at3": ctx_c["B"], "t9_at3": "Certain", "t10_at3": "Nulles"
        }
        score_trous = 0.0
        verdicts_trous = {}
        for t_id, t_correct in attendus_trous_at3.items():
            # CORRECTION : Lecture directe et securisee dans le session_state globale
            saisie_t = st.session_state.get(f"col_d_trous_at3_{t_id}", "Choisir...")
            if saisie_t == t_correct:
                score_trous += 1.0 # 1 point entier par bonne reponse
                verdicts_trous[t_id] = "CORRECT"
            else: 
                verdicts_trous[t_id] = "INCORRECT"

        # NOTE GLOBALE SUR 30 POINTS EXACTEMENT (10 + 10 + 10)
        note_finale_globale = score_tableau + score_quiz + score_trous

        # 4. GENERATION ET RENDU HTML SYNCHRONISE AVEC LES 3 COMPOSANTS
        html_export_premium = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 3 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1 style="margin: 0; font-size: 22px;">Professeur Laurent GALLET</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 12px;">Scelle le : {timestamp_at3}</p>
                <div class="score-badge">NOTE<br><span style="font-size: 32px;">{note_finale_globale:.2f}</span> / 30</div>
            </div>

            <div class="sub-title">Detail des points acquis</div>
            <p style="font-size: 14px; background: white; padding: 12px; border-left: 4px solid #eab308;">
                &bull; Completement du tableau croise (8 cases) : <strong>{score_tableau:.2f} / 10</strong><br>
                &bull; Quiz de validation de cours (10 QCM) : <strong>{score_quiz:.2f} / 10</strong><br>
                &bull; Synthese de texte casino (10 trous) : <strong>{score_trous:.2f} / 10</strong>
            </p>

            <div class="sub-title">Partie 1 : Grille des probabilites croisees repondue</div>
            <table>
                <tr><th style="width: 50px;">Case</th><th>Definition Mathematique</th><th>Saisie Eleve</th><th>Valeur Attendue</th><th style="text-align: center; width: 120px;">Verdict</th></tr>
        """

        for key_state, (coordonnees, libelle) in mapping_correction.items():
            saisie = st.session_state.get(key_state, "").strip()
            saisie_affichage = saisie if saisie != "" else "Vide"
            attendu = f"{float(sol[coordonnees]):.2f}"
            verdict = verdicts_tableau.get(key_state, "INCORRECT")
            v_class = "status-correct" if verdict == "CORRECT" else "status-incorrect"
            html_export_premium += f"<tr><td>{key_state.replace('cell_at3_', 'N°')}</td><td>{libelle}</td><td>{saisie_affichage}</td><td>{attendu}</td><td style='text-align: center;' class='{v_class}'>{verdict}</td></tr>"

        html_export_premium += """
                <tr><td>N°9</td><td>Total General</td><td>1.00</td><td>1.00</td><td style="text-align: center;" class="status-correct">CORRECT</td></tr>
            </table>

            <div class="sub-title">Partie 2 : Resultats du Questionnaire QCM</div>
            <table>
                <tr><th style="width: 50px;">N°</th><th>Intitule Technique de l'Evaluation</th><th>Saisie Eleve</th><th>Valeur Attendue</th><th style="text-align: center; width: 120px;">Verdict</th></tr>
        """

        questions_intitules = {
            "q1_at3": "Probabilite de l'evenement global A", "q2_at3": "Probabilite de l'evenement global B",
            "q3_at3": "Intersection standard P(A ∩ B)", "q4_at3": "Intersection mixte P(A ∩ B̄)",
            "q5_at3": "Convention totale de l'univers (Omega)", "q6_at3": "Notation mathematique du contraire de B",
            "q7_at3": "Definition d'evenements exclusifs", "q8_at3": "Intersection mixte P(Ā ∩ B)",
            "q9_at3": "Loi de convergence des grands nombres", "q10_at3": "Conversion decimale vers pourcentage"
        }
        for idx_q, q_id in enumerate(["q1_at3", "q2_at3", "q3_at3", "q4_at3", "q5_at3", "q6_at3", "q7_at3", "q8_at3", "q9_at3", "q10_at3"], 1):
            saisie_q = st.session_state.get(f"col_g_quiz_at3_{q_id}", "Choisir...")
            attendu_q = attendus_quiz_at3[q_id]
            verdict_q = verdicts_quiz.get(q_id, "INCORRECT")
            v_class_q = "status-correct" if verdict_q == "CORRECT" else "status-incorrect"
            html_export_premium += f"<tr><td>{idx_q}</td><td>{questions_intitules[q_id]}</td><td>{saisie_q}</td><td>{attendu_q}</td><td style='text-align: center;' class='{v_class_q}'>{verdict_q}</td></tr>"

        html_export_premium += """
            </table>

            <div class="sub-title">Partie 3 : Resultats de la Synthese (Texte a trous)</div>
            <table>
                <tr><th style="width: 50px;">N°</th><th>Intitule Technique du Trou</th><th>Saisie Eleve</th><th>Valeur Attendue</th><th style="text-align: center; width: 120px;">Verdict</th></tr>
        """

        trous_intitules = {
            "t1_at3": "Calcul du total de colonne par marge", "t2_at3": "Probabilite marginale contraire P(Ā)",
            "t3_at3": "Intersection co-marge des contraires", "t4_at3": "Ancre immuable du total de l'univers",
            "t5_at3": "Operateur logique d'intersection", "t6_at3": "Methode de deduction des moustaches",
            "t7_at3": "Contexte lie a la ligne de l'evenement A", "t8_at3": "Contexte lie a la colonne de l'evenement B",
            "t9_at3": "Propriete de l'evenement certain", "t10_at3": "Bornes negatives inferieures autorisees"
        }
        for idx_t, t_id in enumerate(["t1_at3", "t2_at3", "t3_at3", "t4_at3", "t5_at3", "t6_at3", "t7_at3", "t8_at3", "t9_at3", "t10_at3"], 1):
            saisie_t = st.session_state.get(f"col_d_trous_at3_{t_id}", "Choisir...")
            attendu_t = attendus_trous_at3[t_id]
            verdict_t = verdicts_trous.get(t_id, "INCORRECT")
            v_class_t = "status-correct" if verdict_t == "CORRECT" else "status-incorrect"
            html_export_premium += f"<tr><td>{idx_t}</td><td>{trous_intitules[t_id]}</td><td>{saisie_t}</td><td>{attendu_t}</td><td style='text-align: center;' class='{v_class_t}'>{verdict_t}</td></tr>"

        html_export_premium += """
            </table>
        </body>
        </html>
        """

        st.success("Bilan de l'Atelier 3 verrouille et genere avec succes !")
        st.download_button(
            label="TELECHARGER LE RAPPORT INTERACTIF ATELIER 3 (.HTML)",
            data=html_export_premium,
            file_name=f"Rapport_Atelier3_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab4:

    st.header("Atelier 4 - Arbre de probabilités")

    # Initialisation des variables d'etat specifiques a l'Atelier 3
    if "at4_verrouille" not in st.session_state:
        st.session_state.at4_verrouille = False

    col_cmd_at4, col_arbre_at4 = st.columns([1, 3])

    with col_cmd_at4:
        filiere_arbre = st.selectbox(
                "Choisir la filiere :", 
                options=["Choisir...", "Conducteur Routier", "Maintenance", "Travaux Publics"],
                key="sb_filiere_at4_premium"
            )

            # Conteneur de consignes pédagogiques fixe
        st.markdown(
                """<div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 10px; font-size: 12px; margin-bottom: 15px; color: #1e293b;">
                Selectionnez une filiere ci-dessus puis cliquez sur "Generer un exercice".
                </div>""", 
                unsafe_allow_html=True
            )

            # Alignement horizontal des 3 boutons d'action maîtres
        col_btn_1, col_btn_2, col_btn_3 = st.columns(3)
        with col_btn_1:
            btn_gen_at4 = st.button("Generer un exercice", key="btn_at4_gen_opt", use_container_width=True)
        with col_btn_2:
            btn_corr_at4 = st.button("Corriger", key="btn_at4_corr_opt", use_container_width=True)
        with col_btn_3:
            btn_raz_at4 = st.button("Effacer tout", key="btn_at4_raz_opt", use_container_width=True)

            # Gestion des actions des boutons
        if btn_raz_at4:
            st.session_state.atelier4_valide = False
            st.rerun()

        # -------------------------------------------------------------------------
        # GRAND COMPOSANT GRAPHIQUE DE DROITE : L'ARBRE AVEC LES TRAITS DE BRANCHES
        # -------------------------------------------------------------------------
    with col_arbre_at4:
        st.markdown("<h3 style='text-align: center; color: #1e3a8a; font-family: Arial; font-size: 16px; font-weight: bold; margin-bottom: 20px;'>Arbre de Probabilités</h3>", unsafe_allow_html=True)
        
        # 1. CRÉATION DU CONTENEUR MAITRE POSITIONNÉ EN ARRIÈRE-PLAN (EMPECHE LE DECALAGE VISUEL)
        st.markdown(
            """
            <div style="position: relative; width: 100%; height: 500px; background-color: #ffffff; border: 2px solid #cbd5e1; border-radius: 6px; overflow: hidden; margin-bottom: 20px;">
                <!-- LE DESSSIN DES TRAITS BLEUS EN ARRIERE PLAN STRICT -->
                <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1;">
                    <!-- Branches du 1er niveau (Racine vers A et A barre) -->
                    <line x1="50" y1="250" x2="220" y2="105" style="stroke:#1e3a8a; stroke-width:3.5;" />
                    <line x1="50" y1="250" x2="220" y2="385" style="stroke:#1e3a8a; stroke-width:3.5;" />
                    
                    <!-- Branches du 2eme niveau superieur (A vers B et B barre) -->
                    <line x1="430" y1="105" x2="600" y2="45" style="stroke:#1e3a8a; stroke-width:2.5;" />
                    <line x1="430" y1="105" x2="600" y2="165" style="stroke:#1e3a8a; stroke-width:2.5;" />
                    
                    <!-- Branches du 2eme niveau inferieur (A barre vers B et B barre) -->
                    <line x1="430" y1="385" x2="600" y2="325" style="stroke:#1e3a8a; stroke-width:2.5;" />
                    <line x1="430" y1="385" x2="600" y2="445" style="stroke:#1e3a8a; stroke-width:2.5;" />
                </svg>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. INJECTION DES BLOCS STREAMLIT EN DEUX COUCHES SÉPARÉES (MARGES NEGATIVES POUR REMONTER LE CALQUE)
        st.markdown('<div style="position: relative; z-index: 5; margin-top: -510px; padding: 20px; pointer-events: auto;">', unsafe_allow_html=True)

        # --- RANGÉE SUPÉRIEURE : BRANCHE A ET SES COMPOSANTS ---
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                st.write("Probabilité P(A)")
                s_v1 = st.number_input("P(A)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, label_visibility="collapsed", key="v_at4_1", disabled=st.session_state.get("atelier4_valide", False))
            with col_b2:
                st.markdown("<div style='text-align: center; font-weight: bold; color: #1e3a8a; margin-top: 22px; border: 2px solid #1e3a8a; background: #e0f2fe; padding: 6px; border-radius:4px;'>Evénement A</div>", unsafe_allow_html=True)
            with col_b3:
                st.write("P_A(B)")
                s_v3 = st.number_input("P_A(B)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, label_visibility="collapsed", key="v_at4_3", disabled=st.session_state.get("atelier4_valide", False))
                st.write("P_A(B̄)")
                s_v4 = st.number_input("P_A(B_bar)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, label_visibility="collapsed", key="v_at4_4", disabled=st.session_state.get("atelier4_valide", False))
            with col_b4:
                st.markdown("<div style='font-size: 11px; color:#475569; margin-top:10px;'><b>B</b> &nbsp;&nbsp; P(A &cap; B) = </div>", unsafe_allow_html=True)
                s_f1 = st.number_input("F1", min_value=0.0, max_value=1.0, value=0.0, step=0.001, label_visibility="collapsed", key="f_at4_1", disabled=st.session_state.get("atelier4_valide", False))
                st.markdown("<div style='font-size: 11px; color:#475569; margin-top:10px;'><b>B̄</b> &nbsp;&nbsp; P(A &cap; B̄) = </div>", unsafe_allow_html=True)
                s_f2 = st.number_input("F2", min_value=0.0, max_value=1.0, value=0.0, step=0.001, label_visibility="collapsed", key="f_at4_2", disabled=st.session_state.get("atelier4_valide", False))

            # Espace intercalaire de hauteur fixe pour coller à la géométrie du SVG
            st.markdown("<div style='margin-top: 45px;'></div>", unsafe_allow_html=True)

            # --- RANGÉE INFÉRIEURE : BRANCHE Ā ET SES COMPOSANTS ---
            col_b5, col_b6, col_b7, col_b8 = st.columns(4)
            with col_b5:
                st.write("Probabilité P(Ā)")
                s_v2 = st.number_input("P(A_bar)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, label_visibility="collapsed", key="v_at4_2", disabled=st.session_state.get("atelier4_valide", False))
            with col_b6:
                st.markdown("<div style='text-align: center; font-weight: bold; color: #1e3a8a; margin-top: 22px; border: 2px solid #1e3a8a; background: #e0f2fe; padding: 6px; border-radius:4px;'>Evénement Ā</div>", unsafe_allow_html=True)
            with col_b7:
                st.write("P_Ā(B)")
                s_v5 = st.number_input("P_Abar(B)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, label_visibility="collapsed", key="v_at4_5", disabled=st.session_state.get("atelier4_valide", False))
                st.write("P_Ā(B̄)")
                s_v6 = st.number_input("P_Abar(B_bar)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, label_visibility="collapsed", key="v_at4_6", disabled=st.session_state.get("atelier4_valide", False))
            with col_b8:
                st.markdown("<div style='font-size: 11px; color:#475569; margin-top:10px;'><b>B</b> &nbsp;&nbsp; P(Ā &cap; B) = </div>", unsafe_allow_html=True)
                s_f3 = st.number_input("F3", min_value=0.0, max_value=1.0, value=0.0, step=0.001, label_visibility="collapsed", key="f_at4_3", disabled=st.session_state.get("atelier4_valide", False))
                st.markdown("<div style='font-size: 11px; color:#475569; margin-top:10px;'><b>B̄</b> &nbsp;&nbsp; P(Ā &cap; B̄) = </div>", unsafe_allow_html=True)
                s_f4 = st.number_input("F4", min_value=0.0, max_value=1.0, value=0.0, step=0.001, label_visibility="collapsed", key="f_at4_4", disabled=st.session_state.get("atelier4_valide", False))

            st.markdown("</div>", unsafe_allow_html=True)
        # --- APPEL DE LA COMMANDE DE SÉPARATION EN DEUX COLONNES MAITRESSES ---
    st.write("---")
    col_double_quiz_at4, col_double_trous_at4 = st.columns(2)

        # COLONNE DE GAUCHE : LE QUIZ SUR LES ARBRES PONDÉRÉS
    with col_double_quiz_at4:
            st.markdown("##### Quiz theoretique (10 questions)")
            
            if "bq_q_at4" not in st.session_state:
                st.session_state.bq_q_at4 = [
                    {"id": "q1_at4", "q": "Question 1 : La somme des probabilites des branches issues d'un meme nœud vaut toujours :", "opts": ["Choisir...", "0", "0.5", "1"]},
                    {"id": "q2_at4", "q": "Question 2 : Pour calculer la probabilite d'un chemin complet (intersection), il faut :", "opts": ["Choisir...", "Additionner les probabilites", "Multiplier les probabilites entre elles", "Soustraire les branches"]},
                    {"id": "q3_at4", "q": "Question 3 : Une probabilite inscrite sur une branche de second niveau est une probabilite :", "opts": ["Choisir...", "Simple", "Conditionnelle", "Intersection"]},
                    {"id": "q4_at4", "q": "Question 4 : La notation P(A sachant B) correspond mathematiquement a :", "opts": ["Choisir...", "P(A) x P(B)", "P(A et B) / P(B)", "P(A) + P(B)"]},
                    {"id": "q5_at4", "q": "Question 5 : La formule des probabilites totales permet de calculer la probabilite d'un evenement :", "opts": ["Choisir...", "Au premier niveau", "Au second niveau en sommant les chemins menant a lui", "Impossible"]},
                    {"id": "q6_at4", "q": "Question 6 : Si deux evenements A et B sont independants, alors P(A sachant B) est egale a :", "opts": ["Choisir...", "P(B)", "P(A et B)", "P(A)"]},
                    {"id": "q7_at4", "q": "Question 7 : Si un arbre possede 3 branches au 1er niveau et 2 branches au 2eme niveau, combien de chemins totaux y a-t-il :", "opts": ["Choisir...", "5", "6", "9"]},
                    {"id": "q8_at4", "q": "Question 8 : Que signifie l'evenement note avec une barre au-dessus (A barre) :", "opts": ["Choisir...", "L'evenement elementaire", "L'evenement contraire de A", "L'evenement certain"]},
                    {"id": "q9_at4", "q": "Question 9 : Si P(A) = 0.4, quelle est la probabilite de l'evenement contraire P(A barre) :", "opts": ["Choisir...", "0.4", "0.5", "0.6"]},
                    {"id": "q10_at4", "q": "Question 10 : L'evenement 'A et B' correspond graphiquement a :", "opts": ["Choisir...", "Un seul nœud de depart", "La totalite des feuilles", "L'extremite d'un chemin unique"]}
                ]
                random.shuffle(st.session_state.bq_q_at4)
                
            dict_quiz_at4 = {}
            for item in st.session_state.bq_q_at4:
                dict_quiz_at4[item["id"]] = st.selectbox(item["q"], item["opts"], index=0, key=f"q_at4_sb_{item['id']}", disabled=st.session_state.get("atelier4_valide", False))

            quest_at4_1 = dict_quiz_at4.get("q1_at4", "Choisir...")
            quest_at4_2 = dict_quiz_at4.get("q2_at4", "Choisir...")
            quest_at4_3 = dict_quiz_at4.get("q3_at4", "Choisir...")
            quest_at4_4 = dict_quiz_at4.get("q4_at4", "Choisir...")
            quest_at4_5 = dict_quiz_at4.get("q5_at4", "Choisir...")
            quest_at4_6 = dict_quiz_at4.get("q6_at4", "Choisir...")
            quest_at4_7 = dict_quiz_at4.get("q7_at4", "Choisir...")
            quest_at4_8 = dict_quiz_at4.get("q8_at4", "Choisir...")
            quest_at4_9 = dict_quiz_at4.get("q9_at4", "Choisir...")
            quest_at4_10 = dict_quiz_at4.get("q10_at4", "Choisir...")

        # COLONNE DE DROITE : LE TEXTE A TROUS DE L'ATELIER 4
    with col_double_trous_at4:
            st.markdown("##### Analyse de cours Arbres (10 menus)")
            
            if "bq_t_at4" not in st.session_state:
                st.session_state.bq_t_at4 = [
                    {"id": "t1_at4", "label": "Trou A : Un arbre de probabilite est compose de nœuds et de :", "options": ["Choisir...", "Faces", "Branches", "Cases"]},
                    {"id": "t2_at4", "label": "Trou B : Le point de depart situe tout a gauche de l'arbre s'appelle le nœud :", "options": ["Choisir...", "Initial (Racine)", "Secondaire", "Final"]},
                    {"id": "t3_at4", "label": "Trou C : Le long d'un chemin, les probabilites doivent obligatoirement se :", "options": ["Choisir...", "Additionner", "Soustraire", "Multiplier"]},
                    {"id": "t4_at4", "label": "Trou D : Pour reunir plusieurs chemins menant a un meme resultat, on doit les :", "options": ["Choisir...", "Additionner", "Multiplier", "Soustraire"]},
                    {"id": "t5_at4", "label": "Trou E : La somme des probabilites de tous les chemins terminaux vaut toujours :", "options": ["Choisir...", "0", "0.5", "1"]},
                    {"id": "t6_at4", "label": "Trou F : P(B sachant A) represente la probabilite de B sachant que A est :", "options": ["Choisir...", "Impossible", "Realise", "Incertain"]},
                    {"id": "t7_at4", "label": "Trou G : Si deux evenements ne peuvent pas se produire en meme temps, ils sont :", "options": ["Choisir...", "Independants", "Incompatibles", "Certains"]},
                    {"id": "t8_at4", "label": "Trou H : Une branche reliant le premier niveau au second porte une valeur de probabilite :", "options": ["Choisir...", "Simple", "Conditionnelle", "Intersection"]},
                    {"id": "t9_at4", "label": "Trou I : L'extremite finale complete d'un parcours de branches s'appelle un :", "options": ["Choisir...", "Nœud", "Chemin (Issue)", "Vecteur"]},
                    {"id": "t10_at4", "label": "Trou J : Un arbre pondere est un outil visuel servant a denombrer les situations de :", "options": ["Choisir...", "Proportionnalite", "Hasard (Probabilites)", "Geometrie"]}
                ]
                random.shuffle(st.session_state.bq_t_at4)
                
            dict_trous_at4 = {}
            for item in st.session_state.bq_t_at4:
                dict_trous_at4[item["id"]] = st.selectbox(
                    item["label"], 
                    item["options"], 
                    index=0, 
                    key=f"t_at4_sb_{item['id']}", 
                    disabled=st.session_state.get("atelier4_valide", False)
                )

            trous_at4_1 = dict_trous_at4.get("t1_at4", "Choisir...")
            trous_at4_2 = dict_trous_at4.get("t2_at4", "Choisir...")
            trous_at4_3 = dict_trous_at4.get("t3_at4", "Choisir...")
            trous_at4_4 = dict_trous_at4.get("t4_at4", "Choisir...")
            trous_at4_5 = dict_trous_at4.get("t5_at4", "Choisir...")
            trous_at4_6 = dict_trous_at4.get("t6_at4", "Choisir...")
            trous_at4_7 = dict_trous_at4.get("t7_at4", "Choisir...")
            trous_at4_8 = dict_trous_at4.get("t8_at4", "Choisir...")
            trous_at4_9 = dict_trous_at4.get("t9_at4", "Choisir...")
            trous_at4_10 = dict_trous_at4.get("t10_at4", "Choisir...")



        # =========================================================================
        # 2. DISPOSITIF DE SCELLÉ ET DE VALIDATION DEFINITIVE
        # =========================================================================
    st.write("---")
    afficher_questions_atelier4(verrouille=st.session_state.at4_verrouille)
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 4")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at4 = st.checkbox(
            "Je certifie avoir complete l'integralite du tableau et des questionnaires de cet atelier.", 
            key="check_certif_at4_officiel",
            value=True if st.session_state.at4_verrouille else False,
            disabled=st.session_state.at4_verrouille
        )

    btn_clique_at4 = st.button(
            "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", 
            key="btn_export_at4_premium", 
            use_container_width=True,
            disabled=st.session_state.at4_verrouille
        )

    if btn_clique_at4 and not st.session_state.at4_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at4:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        elif "solution_courante" not in st.session_state:
            st.error("Action refusee : Veuillez d'abord generer un exercice en cliquant sur le bouton en haut.")
        else:
            st.session_state.at4_verrouille = True
            st.rerun()

    if st.session_state.at4_verrouille:
        sol = st.session_state.solution_courante
            
            # 1. CALCUL AUTOMATIQUE DES NOTES DE L'EVALUATION ATELIER 4
            # Partie 1 : Validation de l'arbre numerique (8 points)
        score_at4_p1 = 0
        if abs(st.session_state.get("v_at4_1", 0.0) - sol["p_A"]) < 0.01: score_at4_p1 += 1
        if abs(st.session_state.get("v_at4_2", 0.0) - sol["p_B"]) < 0.01: score_at4_p1 += 1
        if abs(st.session_state.get("v_at4_3", 0.0) - sol["p_S_A"]) < 0.01: score_at4_p1 += 1
        if abs(st.session_state.get("v_at4_4", 0.0) - sol["p_Sbar_A"]) < 0.01: score_at4_p1 += 1
        if abs(st.session_state.get("v_at4_5", 0.0) - sol["p_S_B"]) < 0.01: score_at4_p1 += 1
        if abs(st.session_state.get("v_at4_6", 0.0) - sol["p_Sbar_B"]) < 0.01: score_at4_p1 += 1
        if abs(st.session_state.get("f_at4_1", 0.0) - sol["p_A_et_S"]) < 0.001: score_at4_p1 += 1
        if abs(st.session_state.get("f_at4_2", 0.0) - sol["p_A_et_Sbar"]) < 0.001: score_at4_p1 += 1

            # Partie 2 & 3 : Quiz et Trous Casino (10 points + 10 points)
        attendus_q4 = {"q1_at4": "1", "q2_at4": "Multiplier les probabilites entre elles", "q3_at4": "Conditionnelle", "q4_at4": "P(A et B) / P(B)", "q5_at4": "Au second niveau en sommant les chemins menant a lui", "q6_at4": "P(A)", "q7_at4": "6", "q8_at4": "L'evenement contraire de A", "q9_at4": "0.6", "q10_at4": "L'extremite d'un chemin unique"}
        attendus_t4 = {"t1_at4": "Branches", "t2_at4": "Initial (Racine)", "t3_at4": "Multiplier", "t4_at4": "Additionner", "t5_at4": "1", "t6_at4": "Realise", "t7_at4": "Incompatibles", "t8_at4": "Conditionnelle", "t9_at4": "Chemin (Issue)", "t10_at4": "Hasard (Probabilites)"}
            
        score_at4_p2 = sum([1 for qk, qv in attendus_q4.items() if st.session_state.get(f"q_at4_sb_{qk}") == qv])
        score_at4_p3 = sum([1 for tk, tv in attendus_t4.items() if st.session_state.get(f"t_at4_sb_{tk}") == tv])
            
        total_points_at4 = score_at4_p1 + score_at4_p2 + score_at4_p3

        st.success(f"ATELIER 4 SCELLÉ | {p_eleve} {n_eleve} ({c_eleve})")
        st.info(f"NOTE DU COMPTE-RENDU : {total_points_at4} / 28")

            # 2. EMBOUTISSAGE DE LA STRUCTURE HTML INTERACTIVE DE L'ATELIER 4
        html_export_at4 = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Rapport Atelier 4 - {n_eleve}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                    .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                    .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                    .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                    th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                    td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                    .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                    .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
                </style>
            </head>
            <body>
                <div class="header-box">
                    <h1>Professeur Laurent GALLET</h1>
                    <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                    <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_at4}</p>
                    <div class="score-badge">SCORE<br><span style="font-size: 32px;">{total_points_at4}</span> / 28</div>
                </div>

                <div class="sub-title">Detail des points pedagogiques acquis</div>
                <p style="font-size: 14px; background: white; padding: 12px; border-left: 4px solid #eab308;">
                    &bull; Partie 1 : Completion numerique de l'arbre : <strong>{score_at4_p1} / 8</strong><br>
                    &bull; Partie 2 : Questionnaire theoretique (QCM) : <strong>{score_at4_p2} / 10</strong><br>
                    &bull; Partie 3 : Synthese de cours (Texte a trous) : <strong>{score_at4_p3} / 10</strong>
                </p>

                <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                    Document officiel de controle statistique genere automatiquement &bull; Professeur Laurent GALLET
                </div>
            </body>
            </html>
            """

        st.download_button(
                label="TELECHARGER LE RAPPORT INTERACTIF ATELIER 4 (.HTML)",
                data=html_export_at4,
                file_name=f"Rapport_Atelier4_{n_eleve}.html",
                mime="text/html",
                use_container_width=True
            )













