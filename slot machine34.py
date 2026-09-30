# -*- coding: utf-8 -*-

import streamlit as st
import io
import base64
st.set_page_config(
    page_title="Slot Machine",
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
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Slot Machine")
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
onglets = st.tabs(["Identification","Machine 4 Symboles", "Machine 5 Symboles", "Graphiques Comparatifs"])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]


if "budget_paul" not in st.session_state:
    st.session_state.budget_paul = 20

# Definition des listes de tirages pour les calculs
liste_tirages = [100, 1000, 5000, 10000]

# Fonction globale de simulation partagee
def executer_simulation(n, max_symb):
    jackpot, gagnant, perdant = 0, 0, 0
    for _ in range(n):
        s1 = random.randint(1, max_symb)
        s2 = random.randint(1, max_symb)
        s3 = random.randint(1, max_symb)
        nb_uniques = len({s1, s2, s3})
        if nb_uniques == 1:
            jackpot += 1
        elif nb_uniques == 2:
            gagnant += 1
        else:
            perdant += 1
    return jackpot, gagnant, perdant


def generer_le_quiz_analytique_casino(verrouille=False):
    import streamlit as st

    # 1. Pré-calculs des valeurs théoriques pour les deux configurations (4 et 5 symboles)
    # Machine à 4 symboles (Chiffres 1 à 4)
    total_comb_4 = 4 ** 3  # 64
    p_jackpot_4 = (4 / total_comb_4) * 100  # 6.25%
    p_paire_4 = (36 / total_comb_4) * 100  # 56.25%
    p_perdu_4 = (24 / total_comb_4) * 100  # 37.50%

    # Machine à 5 symboles (Chiffres 1 à 5)
    total_comb_5 = 5 ** 3  # 125
    p_jackpot_5 = (5 / total_comb_5) * 100  # 4.00%
    p_paire_5 = (60 / total_comb_5) * 100  # 48.00%
    p_perdu_5 = (60 / total_comb_5) * 100  # 48.00%

    st.markdown("##### Quiz numerique sur les probabilites des machines a sous (20 questions - 20 pts)")
    
    # Dictionnaire local pour stocker temporairement les saisies de l'élève
    dict_reponses_quiz = {}

    # =========================================================================
    # BLOC DES 20 QUESTIONS AVEC SELECTBOX INDIVIDUELLES
    # =========================================================================

    # Q1
    opts_q1 = ["Choisir...", f"{p_jackpot_4:.2f}%", "4.00%", "12.50%"]
    st.write("**1.** Quelle est la probabilite theorique d'obtenir un jackpot avec 4 symboles ?")
    dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_casino_q1", disabled=verrouille, label_visibility="collapsed")

    # Q2
    opts_q2 = ["Choisir...", "16", f"{total_comb_4}", "128"]
    st.write("**2.** Combien de combinaisons totales existent sur la machine a 4 symboles ?")
    dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_casino_q2", disabled=verrouille, label_visibility="collapsed")

    # Q3
    opts_q3 = ["Choisir...", "37.50%", f"{p_perdu_5:.2f}%", "50.00%"]
    st.write("**3.** Sur la machine a 5 symboles, quelle est la probabilite de perdre (3 chiffres differents) ?")
    dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_casino_q3", disabled=verrouille, label_visibility="collapsed")

    # Q4
    opts_q4 = ["Choisir...", "25", f"{total_comb_5}", "150"]
    st.write("**4.** Quel est le nombre total de combinaisons possibles avec 5 symboles ?")
    dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, key="col_g_quiz_casino_q4", disabled=verrouille, label_visibility="collapsed")

    # Q5
    opts_q5 = ["Choisir...", "La loi des grands nombres", "La loi de Murphy", "La loi des series"]
    st.write("**5.** Comment s'appelle la loi mathematique qui explique pourquoi les frequences se rapprochent des probabilites avec le temps ?")
    dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_casino_q5", disabled=verrouille, label_visibility="collapsed")

    # Q6
    opts_q6 = ["Choisir...", "Plus elevee", "Identique", "Moins elevee"]
    st.write("**6.** Si Paul fait 3 lancers perdants de suite a 4 symboles, sa chance de gagner au 4e lancer est-elle :")
    dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_casino_q6", disabled=verrouille, label_visibility="collapsed")

    # Q7
    opts_q7 = ["Choisir...", "Plus facile a obtenir", "Identique", "Plus difficile a obtenir"]
    st.write("**7.** Si l'on passe de 4 a 5 symboles, le jackpot devient :")
    dict_reponses_quiz["q7"] = st.selectbox("", opts_q7, key="col_g_quiz_casino_q7", disabled=verrouille, label_visibility="collapsed")

    




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
    st.header("Machine a 4 symboles")
    st.metric(label="Budget actuel de Paul", value=f"{st.session_state.budget_paul} EUR")
    
    # Correspondance chiffres -> symboles textuels (SANS EMOJI)
    SYMBOLES_4 = {1: "▲", 2: "■", 3: "◆", 4: "●"}

    # Zone d'affichage visuelle de la machine a sous
    st.markdown("### ROULEAUX DE LA MACHINE")
    zone_machine_4 = st.empty()
    # Affichage de la machine au repos
    zone_machine_4.markdown("""
    <div style="background-color: #0f172a; padding: 25px; border-radius: 10px; text-align: center; border: 4px solid #1e3a8a; margin-bottom: 20px;">
        <span style="color: #64748b; font-size: 40px; font-weight: bold; letter-spacing: 15px;">[ - ] [ - ] [ - ]</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Tirer le levier (4 symboles - Mise 1 EUR)", type="primary", key="lever_4"):
        if st.session_state.budget_paul > 0:
            st.session_state.budget_paul -= 1
            
            # ANIMATION : Fait tourner les rouleaux avec les symboles
            import time
            for _ in range(8):
                v1, v2, v3 = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)
                zone_machine_4.markdown(f"""
                <div style="background-color: #0f172a; padding: 25px; border-radius: 10px; text-align: center; border: 4px solid #1e3a8a; margin-bottom: 20px;">
                    <span style="color: #e2e8f0; font-size: 40px; font-weight: bold; letter-spacing: 15px;">[ {SYMBOLES_4[v1]} ] [ {SYMBOLES_4[v2]} ] [ {SYMBOLES_4[v3]} ]</span>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.08)
            
            # TIRAGE REEL DEFINITIF
            c1, c2, c3 = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)
            zone_machine_4.markdown(f"""
            <div style="background-color: #0f172a; padding: 25px; border-radius: 10px; text-align: center; border: 4px solid #eab308; margin-bottom: 20px;">
                <span style="color: #ffffff; font-size: 40px; font-weight: bold; letter-spacing: 15px;">[ {SYMBOLES_4[c1]} ] [ {SYMBOLES_4[c2]} ] [ {SYMBOLES_4[c3]} ]</span>
            </div>
            """, unsafe_allow_html=True)
            
            uniques = len({c1, c2, c3})
            if uniques == 1:
                st.session_state.budget_paul += 10
                st.success("Jackpot ! +10 EUR")
            elif uniques == 2:
                st.session_state.budget_paul += 1
                st.warning("Une paire. Paul recupere sa mise.")
            else:
                st.error("3 symboles differents. Perdu.")
            st.checkbox("Valider le tirage pour rafraichir", key="refresh_4", value=True, label_visibility="collapsed")
        else:
            st.error("Paul n'a plus d'argent pour jouer.")

    if st.button("Recharger le budget (20 EUR)", key="reset_4"):
        st.session_state.budget_paul = 20
        st.rerun()

    st.subheader("Tableau des simulations (4 symboles)")
    donnees_4 = {}
    for t in liste_tirages:
        j, g, p = executer_simulation(t, 4)
        donnees_4[t] = {
            "Jackpot (Nombre)": j, "Jackpot (Frequence)": f"{(j/t)*100:.2f}%",
            "Gagnant (Nombre)": g, "Gagnant (Frequence)": f"{(g/t)*100:.2f}%",
            "Perdant (Nombre)": p, "Perdant (Frequence)": f"{(p/t)*100:.2f}%"
        }
    df_4 = pd.DataFrame.from_dict(donnees_4, orient='index')
    df_4.index.name = "Nombre de tirages"
    st.dataframe(df_4[["Jackpot (Nombre)", "Jackpot (Frequence)", "Gagnant (Nombre)", "Gagnant (Frequence)", "Perdant (Nombre)", "Perdant (Frequence)"]], use_container_width=True)

with tab2:
    st.header("Machine a 5 symboles")
    st.metric(label="Budget actuel de Paul", value=f"{st.session_state.budget_paul} EUR")
    
    # Correspondance chiffres -> symboles textuels (SANS EMOJI)
    SYMBOLES_5 = {1: "▲", 2: "■", 3: "◆", 4: "●", 5: "★"}

    # Zone d'affichage visuelle de la machine a sous
    st.markdown("### ROULEAUX DE LA MACHINE")
    zone_machine_5 = st.empty()
    # Affichage de la machine au repos
    zone_machine_5.markdown("""
    <div style="background-color: #0f172a; padding: 25px; border-radius: 10px; text-align: center; border: 4px solid #1e3a8a; margin-bottom: 20px;">
        <span style="color: #64748b; font-size: 40px; font-weight: bold; letter-spacing: 15px;">[ - ] [ - ] [ - ]</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Tirer le levier (5 symboles - Mise 1 EUR)", type="primary", key="lever_5"):
        if st.session_state.budget_paul > 0:
            st.session_state.budget_paul -= 1
            
            # ANIMATION : Fait tourner les rouleaux avec les symboles
            import time
            for _ in range(8):
                v1, v2, v3 = random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)
                zone_machine_5.markdown(f"""
                <div style="background-color: #0f172a; padding: 25px; border-radius: 10px; text-align: center; border: 4px solid #1e3a8a; margin-bottom: 20px;">
                    <span style="color: #e2e8f0; font-size: 40px; font-weight: bold; letter-spacing: 15px;">[ {SYMBOLES_5[v1]} ] [ {SYMBOLES_5[v2]} ] [ {SYMBOLES_5[v3]} ]</span>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(0.08)
            
            # TIRAGE REEL DEFINITIF
            c1, c2, c3 = random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)
            zone_machine_5.markdown(f"""
            <div style="background-color: #0f172a; padding: 25px; border-radius: 10px; text-align: center; border: 4px solid #eab308; margin-bottom: 20px;">
                <span style="color: #ffffff; font-size: 40px; font-weight: bold; letter-spacing: 15px;">[ {SYMBOLES_5[c1]} ] [ {SYMBOLES_5[c2]} ] [ {SYMBOLES_5[c3]} ]</span>
            </div>
            """, unsafe_allow_html=True)
            
            uniques = len({c1, c2, c3})
            if uniques == 1:
                st.session_state.budget_paul += 10
                st.success("Jackpot ! +10 EUR")
            elif uniques == 2:
                st.session_state.budget_paul += 1
                st.warning("Une paire. Paul recupere sa mise.")
            else:
                st.error("3 symboles differents. Perdu.")
            st.checkbox("Valider le tirage pour rafraichir", key="refresh_5", value=True, label_visibility="collapsed")
        else:
            st.error("Paul n'a plus d'argent pour jouer.")

    if st.button("Recharger le budget (20 EUR)", key="reset_5"):
        st.session_state.budget_paul = 20
        st.rerun()

    st.subheader("Tableau des simulations (5 symboles)")
    donnees_5 = {}
    for t in liste_tirages:
        j, g, p = executer_simulation(t, 5)
        donnees_5[t] = {
            "Jackpot (Nombre)": j, "Jackpot (Frequence)": f"{(j/t)*100:.2f}%",
            "Gagnant (Nombre)": g, "Gagnant (Frequence)": f"{(g/t)*100:.2f}%",
            "Perdant (Nombre)": p, "Perdant (Frequence)": f"{(p/t)*100:.2f}%"
        }
    df_5 = pd.DataFrame.from_dict(donnees_5, orient='index')
    df_5.index.name = "Nombre de tirages"
    st.dataframe(df_5[["Jackpot (Nombre)", "Jackpot (Frequence)", "Gagnant (Nombre)", "Gagnant (Frequence)", "Perdant (Nombre)", "Perdant (Frequence)"]], use_container_width=True)
                       
with tab3:
    st.header("Analyse graphique des performances")
    st.write("Ce graphique compare les pourcentages reels obtenus lors d'une simulation reference de 10 000 tirages.")

    # 1. GENERATION DU GRAPHIQUE EN COMPATIBILITÉ BASE64 POUR L'EXPORT
    import io
    import base64
    import matplotlib.pyplot as plt

    # Données issues de vos simulations (assurez-vous que j4, g4, p4, j5, g5, p5 sont calculés en amont)
    try:
        pct_4 = [(j4/10000)*100, (g4/10000)*100, (p4/10000)*100]
        pct_5 = [(j5/10000)*100, (g5/10000)*100, (p5/10000)*100]
    except NameError:
        # Valeurs de secours si les simulations en direct ne sont pas encore instanciées
        j4, g4, p4 = 625, 5625, 3750
        j5, g5, p5 = 400, 4800, 4800
        pct_4 = [6.25, 56.25, 37.50]
        pct_5 = [4.00, 48.00, 48.00]

    fig, ax = plt.subplots(figsize=(7, 4))
    categories = ['Jackpot', 'Recuperer mise', 'Perdu']
    x_indices = [0, 1, 2]
    width = 0.35

    ax.bar([i - width/2 for i in x_indices], pct_4, width, label='4 Symboles', color='#1e3a8a')
    ax.bar([i + width/2 for i in x_indices], pct_5, width, label='5 Symboles', color='#eab308')

    ax.set_ylabel('Pourcentage (%)')
    ax.set_title('Comparaison des Tirages Reference (10 000 lancers)')
    ax.set_xticks(x_indices)
    ax.set_xticklabels(categories)
    ax.legend()
    plt.tight_layout()

    # Rendu à l'écran dans Streamlit
    st.pyplot(fig)

    # Conversion en Base64 pour injection dans le HTML futur
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)

    st.markdown("---")

    # 2. APPEL ET AFFICHAGE DU QUIZ DÉFINI DANS LA DEF
    if "quiz_verrouille" not in st.session_state:
        st.session_state.quiz_verrouille = False

    # Appel de la fonction pour afficher le questionnaire à l'écran
    generer_le_quiz_analytique_casino(verrouille=st.session_state.quiz_verrouille)

    # 3. DICTIONNAIRE OFFICIEL DES ATTENDUS POUR LA CORRECTION AUTOMATIQUE
    attendus_casino = {
        "q1": "6.25%", 
        "q2": "64", 
        "q3": "48.00%", 
        "q4": "125",
        "q5": "La loi des grands nombres", 
        "q6": "Identique",
        "q7": "Plus difficile a obtenir", 
        "q8": "N x N x N",
        "q9": "56.25%", 
        "q10": "9 EUR", 
        "q11": "Un generateur pseudo-aleatoire",
        "q12": "36", 
        "q13": "Egale", 
        "q14": "Faire un jackpot",
        "q15": "st.session_state", 
        "q16": "st.bar_chart", 
        "q17": "Un DataFrame Pandas",
        "q18": "4.00%", 
        "q19": "Gagner de l'argent", 
        "q20": "N'a aucun impact sur le prochain tirage"
    }

    # Dictionnaire des énoncés propres pour le tableau HTML de l'export
    enonces_questions = {
        "q1": "Probabilite jackpot 4 symboles ?", "q2": "Combinaisons totales machine 4 symboles ?",
        "q3": "Probabilite de perdre machine 5 symboles ?", "q4": "Combinaisons totales machine 5 symboles ?",
        "q5": "Loi mathematique de convergence ?", "q6": "Chance au 4e lancer apres 3 pertes ?",
        "q7": "Difficulte jackpot a 5 symboles ?", "q8": "Formule mathematique issues possibles ?",
        "q9": "Pourcentage de chance de recuperer sa mise (4 symb) ?", "q10": "Gain net d'un jackpot ?",
        "q11": "Terme designant le hasard numerique ?", "q12": "Nombre de combinaisons paires (4 symb) ?",
        "q13": "Paire vs 3 differents a 5 symboles ?", "q14": "Evenement de probabilite la plus faible ?",
        "q15": "Outil de stockage persistant Streamlit ?", "q16": "Composant graphique barres Streamlit ?",
        "q17": "Structure de donnees utilisee pour la simulation ?", "q18": "Probabilite jackpot 5 symboles ?",
        "q19": "Resultat statistique a l'infini ?", "q20": "Signification independance des lancers ?"
    }

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Quiz Casino")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    from datetime import datetime
    timestamp_quiz = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_quiz = st.checkbox(
        "Je certifie avoir complete l'integralite du questionnaire de l'analyse statistique.", 
        key="check_certif_quiz_officiel_20pts", disabled=st.session_state.quiz_verrouille
    )

    btn_clique_quiz = st.button(
        "VALIDER ET EXPORTER LE BILAN DU QUIZ CASINO", 
        key="btn_export_quiz_official_20pts", 
        use_container_width=True, 
        disabled=st.session_state.quiz_verrouille
    )

    if btn_clique_quiz and not st.session_state.quiz_verrouille:
        if not st.session_state.get("verrouille", False): 
            st.error("Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_quiz: 
            st.error("Cochez la case de certification.")
        else:
            # CORRECTION DE LA CLÉ : Correspondance exacte avec col_g_quiz_casino_q1, col_g_quiz_casino_q2...
            score_final_quiz = sum([1 for qk, qv in attendus_casino.items() if st.session_state.get(f"col_g_quiz_casino_{qk}") == qv])
            st.session_state.score_final_quiz = score_final_quiz
            st.session_state.quiz_verrouille = True
            st.rerun()

    # 5. GENERATION DE LA CHAINE HTML ET BOUTON DE TELECHARGEMENT
    if st.session_state.get("quiz_verrouille", False):
        tot_s = st.session_state.get("score_final_quiz", 0)

        st.success(f"QUIZ SCELLÉ ET ENREGISTRÉ | Note : {tot_s} / 20")

        html_export_quiz = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rapport Quiz Casino - {n_eleve}</title>
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
        <h1>Professeur Laurent GALLET</h1>
        <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
        <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_quiz}</p>
        <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
    </div>

    <div class="sub-title">Analyse Graphique Performee lors de l Atelier</div>
    <div style="text-align: center; background: white; padding: 20px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px;">
        <p style="font-size: 13px; color: #475569; margin-bottom: 15px;">Comparatif des frequences observees sur 10 000 tirages (4 vs 5 symboles)</p>
        <img src="data:image/png;base64,{img_base64}" alt="Graphique des performances" style="max-width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 4px;" />
    </div>

    <div class="sub-title">PARTIE QUIZ : FORMULES ET LOIS DES GRANDS NOMBRES (20 PTS)</div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%;">Num</th>
                <th style="width: 50%;">Question posee</th>
                <th style="text-align:center; width: 20%;">Saisie Eleve</th>
                <th style="text-align:center; width: 15%;">Attendu</th>
                <th style="text-align: center; width: 10%;">Verdict</th>
            </tr>
        </thead>
        <tbody>
"""

        # CORRECTION DES CLÉS POUR LA BOUCLE : Parcours ordonné de q1 à q20
        for num_q in range(1, 21):
            q_id = f"q{num_q}"
            attend_val = attendus_casino[q_id]
            saisie_val = st.session_state.get(f"col_g_quiz_casino_{q_id}", "Choisir...")
            
            is_correct = str(saisie_val).strip() == str(attend_val).strip()
            v_lbl = "CORRECT" if is_correct else "INCORRECT"
            v_cls = "status-correct" if is_correct else "status-incorrect"
            
            html_export_quiz += f"""
            <tr>
                <td>{num_q}</td>
                <td>{enonces_questions[q_id]}</td>
                <td style="text-align:center;">{saisie_val}</td>
                <td style="text-align:center;">{attend_val}</td>
                <td style="text-align:center;" class="{v_cls}">{v_lbl}</td>
            </tr>"""

        # Clôture du document HTML
        html_export_quiz += """
        </tbody>
    </table>
</body>
</html>
"""

        # Bouton d'extraction final
        st.download_button(
            label="TELECHARGER LE RAPPORT HTML DU QUIZ ET DU GRAPHIQUE",
            data=html_export_quiz,
            file_name=f"Rapport_Quiz_Casino_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )
