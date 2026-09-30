# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage du vinaigre",
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
st.title("Application dosage du vinaigre")
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
onglets = st.tabs([
    "Identification",
    "Généralités sur le vinaigre",
    "Dosage colorimétrique du vinaigre",
    "Calcul théorique sur le vinaigre et vérification de l'inscription sur la bouteille"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]


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

# Creation des trois onglets demandés
tab1, tab2, tab3 = st.tabs(["Machine 4 Symboles", "Machine 5 Symboles", "Graphiques Comparatifs"])

# --- ONGLET 1 : MACHINE A 4 SYMBOLES ---
with tab1:
    st.header("Machine a 4 symboles (Chiffres 1 a 4)")
    
    st.metric(label="Budget actuel de Paul", value=f"{st.session_state.budget_paul} EUR")
    
    if st.button("Tirer le levier (4 symboles - Mise 1 EUR)", type="primary"):
        if st.session_state.budget_paul > 0:
            st.session_state.budget_paul -= 1
            c1, c2, c3 = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)
            st.write(f"Resultat direct : [ {c1} ]  [ {c2} ]  [ {c3} ]")
            uniques = len({c1, c2, c3})
            if uniques == 1:
                st.session_state.budget_paul += 10
                st.success("Jackpot ! +10 EUR")
            elif uniques == 2:
                st.session_state.budget_paul += 1
                st.warning("Une paire. Paul recupere sa mise.")
            else:
                st.error("3 symboles differents. Perdu.")
            st.rerun()
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

# --- ONGLET 2 : MACHINE A 5 SYMBOLES ---
with tab2:
    st.header("Machine a 5 symboles (Chiffres 1 a 5)")
    
    st.metric(label="Budget actuel de Paul", value=f"{st.session_state.budget_paul} EUR")
    
    if st.button("Tirer le levier (5 symboles - Mise 1 EUR)", type="primary"):
        if st.session_state.budget_paul > 0:
            st.session_state.budget_paul -= 1
            c1, c2, c3 = random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)
            st.write(f"Resultat direct : [ {c1} ]  [ {c2} ]  [ {c3} ]")
            uniques = len({c1, c2, c3})
            if uniques == 1:
                st.session_state.budget_paul += 10
                st.success("Jackpot ! +10 EUR")
            elif uniques == 2:
                st.session_state.budget_paul += 1
                st.warning("Une paire. Paul recupere sa mise.")
            else:
                st.error("3 symboles differents. Perdu.")
            st.rerun()
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
    
    # 1. Generation des donnees de simulation pour le graphique
    j4, g4, p4 = executer_simulation(10000, 4)
    j5, g5, p5 = executer_simulation(10000, 5)

    pct_4 = [(j4/10000)*100, (g4/10000)*100, (p4/10000)*100]
    pct_5 = [(j5/10000)*100, (g5/10000)*100, (p5/10000)*100]
    categories = ["Jackpot", "Recuperer mise", "Perdu"]

    # 2. Creation du graphique avec Matplotlib (indispensable pour l'export HTML en image)
    fig, ax = plt.subplots(figsize=(7, 4))
    x_indexes = range(len(categories))
    width = 0.35

    ax.bar([x - width/2 for x in x_indexes], pct_4, width, label='4 Symboles', color='#1e3a8a')
    ax.bar([x + width/2 for x in x_indexes], pct_5, width, label='5 Symboles', color='#eab308')

    ax.set_ylabel('Pourcentage (%)')
    ax.set_title("Comparaison des frequences (10 000 tirages)")
    ax.set_xticks(x_indexes)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Affichage du graphique dans Streamlit
    st.pyplot(fig)

    # Encodage de l'image du graphique en Base64 pour l'export HTML
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    
    st.markdown("---")
    st.header("Quiz : Testez vos connaissances sur les probabilites")
    st.write("Repondez aux 20 questions ci-dessous pour verifier votre maitrise des jeux de hasard.")

    # Liste statique des 20 questions
    questions = [
        {"q": "1. Quelle est la probabilite theorique d'obtenir un jackpot avec 4 symboles ?", "o": ["4.00%", "6.25%", "12.50%"], "a": "6.25%"},
        {"q": "2. Combien de combinaisons totales existent sur la machine a 4 symboles ?", "o": ["16", "64", "128"], "a": "64"},
        {"q": "3. Sur la machine a 5 symboles, quelle est la probabilite de perdre (3 chiffres differents) ?", "o": ["37.50%", "48.00%", "50.00%"], "a": "48.00%"},
        {"q": "4. Quel est le nombre total de combinaisons possibles avec 5 symboles ?", "o": ["25", "125", "150"], "a": "125"},
        {"q": "5. Comment s'appelle la loi mathematique qui explique pourquoi les frequences se rapprochent des probabilites avec le temps ?", "o": ["La loi des grands nombres", "La loi de Murphy", "La loi des series"], "a": "La loi des grands nombres"},
        {"q": "6. Si Paul fait 3 lancers perdants de suite a 4 symboles, sa chance de gagner au 4e lancer est-elle :", "o": ["Plus elevee", "Identique", "Moins elevee"], "a": "Identique"},
        {"q": "7. Si l'on passe de 4 a 5 symboles, le jackpot devient :", "o": ["Plus facile a obtenir", "Identique", "Plus difficile a obtenir"], "a": "Plus difficile a obtenir"},
        {"q": "8. Quelle est la formule mathematique pour calculer l'ensemble des issues possibles avec 3 colonnes et N symboles ?", "o": ["N + 3", "N x 3", "N x N x N"], "a": "N x N x N"},
        {"q": "9. Quel pourcentage de chance a-t-on de recuperer sa mise sur la machine a 4 symboles ?", "o": ["48.00%", "56.25%", "6.25%"], "a": "56.25%"},
        {"q": "10. Quel est le gain net de Paul s'il obtient un Jackpot (Gain - Mise) ?", "o": ["10 EUR", "9 EUR", "11 EUR"], "a": "9 EUR"},
        {"q": "11. Quel terme designe le hasard pur utilise par le code via 'random.randint' ?", "o": ["Une fonction deterministe", "Un generateur pseudo-aleatoire", "Une equation lineaire"], "a": "Un generateur pseudo-aleatoire"},
        {"q": "12. Sur 64 combinaisons de la machine a 4 symboles, combien donnent exactement une paire ?", "o": ["4", "24", "36"], "a": "36"},
        {"q": "13. Sur la machine a 5 symboles, la probabilite d'une paire est-elle superieure, egale ou inferieure a celle d'avoir 3 symboles differents ?", "o": ["Superieure", "Egale", "Inferieure"], "a": "Egale"},
        {"q": "14. Quel evenement possede la probabilite la plus faible sur ces deux machines ?", "o": ["Faire une paire", "Faire un jackpot", "Perdre"], "a": "Faire un jackpot"},
        {"q": "15. Quel outil informatique permet de stocker et maintenir le budget de Paul entre les clics ?", "o": ["st.session_state", "st.dataframe", "st.metric"], "a": "st.session_state"},
        {"q": "16. Quel composant Streamlit est utilise pour tracer le graphique en barres ?", "o": ["st.table", "st.bar_chart", "st.dataframe"], "a": "st.bar_chart"},
        {"q": "17. Quel type de donnees est utilise pour generer les tableaux de simulation ?", "o": ["Un DataFrame Pandas", "Une liste simple", "Un dictionnaire imbrique"], "a": "Un DataFrame Pandas"},
        {"q": "18. Quel est le pourcentage de chance theorique d'avoir un jackpot a 5 symboles ?", "o": ["4.00%", "5.00%", "6.00%"], "a": "4.00%"},
        {"q": "19. Si Paul joue infiniement a la machine a 4 symboles avec vos regles, va-t-il statistiquement :", "o": ["Gagner de l'argent", "Rester stable", "Perdre de l'argent"], "a": "Gagner de l'argent"},
        {"q": "20. L'independance des lancers signifie que le resultat precedent :", "o": ["Influence le prochain tirage", "N'a aucun impact sur le prochain tirage", "Bloque le prochain tirage"], "a": "N'a aucun impact sur le prochain tirage"}
    ]

    # Formulaire pour regrouper la validation du quiz
    with st.form(key="quiz_form"):
        reponses_utilisateur = {}
        for idx, item in enumerate(questions):
            reponses_utilisateur[idx] = st.radio(item["q"], options=item["o"], key=f"q_{idx}")
        
        bouton_validation = st.form_submit_button(label="Valider mes reponses")

    # Affichage du score suite au clic et preparation de l'export
    if bouton_validation:
        score = 0
        for idx, item in enumerate(questions):
            if reponses_utilisateur[idx] == item["a"]:
                score += 1
        
        st.subheader(f"Votre score final : {score} / 20")
        if score == 20:
            st.success("Parfait ! Vous maitrisez totalement les probabilites de cet exercice.")
        elif score >= 12:
            st.warning("Bon score ! Vous avez compris l'essentiel du fonctionnement statistique.")
        else:
            st.error("Vous pouvez faire mieux. Relisez attentivement les tableaux statistiques pour comprendre les probabilites.")

    # Code d'assemblage du rapport HTML une fois scelle
    if st.session_state.get("quiz_verrouille", False):
        tot_s = st.session_state.get("score_final_quiz", 0)

        # Construction propre de la structure globale du HTML
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

        # CONVERSIONS ET INJECTIONS DYNAMIQUES HORS DE LA F-STRING GLOBALE
        # Cette technique évite les conflits d'accolades dans la boucle
        for idx_q, item in enumerate(questions):
            saisie = reponses_utilisateur.get(idx_q, "Non repondu")
            attendu = item["a"]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_cls = "status-correct" if str(saisie) == str(attendu) else "status-incorrect"
            
            # Nettoyage des caractères problématiques dans les énoncés
            q_clean = item['q'].replace('"', '&quot;').replace("'", "&apos;")
            saisie_clean = str(saisie).replace('"', '&quot;').replace("'", "&apos;")
            attendu_clean = str(attendu).replace('"', '&quot;').replace("'", "&apos;")

            # Concaténation classique et sécurisée des lignes du tableau HTML
            html_export_quiz += f"""
                    <tr>
                        <td>{idx_q + 1}</td>
                        <td>{q_clean}</td>
                        <td style="text-align:center;">{saisie_clean}</td>
                        <td style="text-align:center;">{attendu_clean}</td>
                        <td style="text-align:center;" class="{v_cls}">{v_lbl}</td>
                    </tr>"""

        # Clôture finale de la structure textuelle HTML
        html_export_quiz += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Composant de téléchargement Streamlit
        st.download_button(
            label="TELECHARGER LE RAPPORT HTML DU QUIZ ET DU GRAPHIQUE",
            data=html_export_quiz,
            file_name=f"Rapport_Quiz_Casino_{n_eleve}_{c_eleve}.html",
            mime="text/html",
            use_container_width=True
        )
