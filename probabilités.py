from datetime import datetime
import math
import os
import random
import time
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import ImageGrab
import streamlit as st

# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application de Probabilités")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)
# =============================================================================
# INITIALISATION EXCLUSIVE ET SÉCURISÉE DES VARIABLES DE SESSION
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
if "btn_valider_desactive" not in st.session_state:
    st.session_state.btn_valider_desactive = False
if "mode_examen_actif" not in st.session_state:
    st.session_state.mode_examen_actif = False

# 2. Paramètres financiers généraux
if "solde" not in st.session_state:
    st.session_state.solde = 100.0
if "mise" not in st.session_state:
    st.session_state.mise = 1.0

# 3. Configuration et compteurs du module JEU DE DÉ
if "total_lancers_de" not in st.session_state:
    st.session_state.total_lancers_de = 0
if "stats_par_face_de" not in st.session_state:
    # Dictionnaire dynamique initialisé de 1 à 20 pour supporter les dés d'examen
    st.session_state.stats_par_face_de = {face: 0 for face in range(1, 21)}
if "slider_faces_n1_valeur" not in st.session_state:
    st.session_state.slider_faces_n1_valeur = 6

# 4. Configuration et compteurs du module SLOT MACHINE
if "total_lancers_slot" not in st.session_state:
    st.session_state.total_lancers_slot = 0
if "cpt_classe_jackpots" not in st.session_state:
    st.session_state.cpt_classe_jackpots = 0
if "cpt_classe_gagnes" not in st.session_state:
    st.session_state.cpt_classe_gagnes = 0
if "slider_shapes_n1_valeur" not in st.session_state:
    st.session_state.slider_shapes_n1_valeur = 7

# 5. Configuration et compteurs du module ROULETTE EUROPEENNE
if "type_pari" not in st.session_state:
    st.session_state.type_pari = "Couleur"
if "combinaison_active" not in st.session_state:
    st.session_state.combinaison_active = "Rouge"
if "roulette_gagnes" not in st.session_state:
    st.session_state.roulette_gagnes = 0
if "roulette_perdus" not in st.session_state:
    st.session_state.roulette_perdus = 0

# Compteurs géométriques des secteurs réels de la roue
if "stats_roulette_rouge" not in st.session_state:
    st.session_state.stats_roulette_rouge = 0
if "stats_roulette_noir" not in st.session_state:
    st.session_state.stats_roulette_noir = 0
if "stats_roulette_zero" not in st.session_state:
    st.session_state.stats_roulette_zero = 0
if "stats_roulette_even" not in st.session_state:
    st.session_state.stats_roulette_even = 0
if "stats_roulette_odd" not in st.session_state:
    st.session_state.stats_roulette_odd = 0

# Variables cinématiques de l'animation de la bille
if "orientation_aiguille" not in st.session_state:
    st.session_state.orientation_aiguille = 0.0
if "index_gagnant_roue" not in st.session_state:
    st.session_state.index_gagnant_roue = 0
if "victoire_pari" not in st.session_state:
    st.session_state.victoire_pari = False
if "dernier_statut_roue" not in st.session_state:
    st.session_state.dernier_statut_roue = "Attente"

# 6. Exercices écrits (Textes à trous et évaluation)
if "reponses_trous" not in st.session_state:
    st.session_state.reponses_trous = [""] * 15
if "quiz_deja_valide" not in st.session_state:
    st.session_state.quiz_deja_valide = False
if "score_final_quiz" not in st.session_state:
    st.session_state.score_final_quiz = 0

# 7. Journaux d'historique et logs de traçabilité
if "historique_logs" not in st.session_state:
    st.session_state.historique_logs = []
if "liste_casino_view1" not in st.session_state:
    st.session_state.liste_casino_view1 = []
if "entries_tab3" not in st.session_state:
    st.session_state.entries_tab3 = {(i, j): "" for i in range(3) for j in range(3)}
if "cases_initiales" not in st.session_state:
    st.session_state.cases_initiales = []  # Ex: [(0, 1), (1, 0), (2, 1)]
if "solution_courante" not in st.session_state:
    st.session_state.solution_courante = {}  # Stocke {(i, j): float}
if "tableau_corrige" not in st.session_state:
    st.session_state.tableau_corrige = False
labels_h = ["A", "A̅", "Total"]
labels_v = ["B", "B̅", "Total"]
    
FORMES_CASINO = {
    1: {"nom": "Sept", "couleur": "#ec4899", "type": "oval"},
    2: {"nom": "Carre", "couleur": "#3b82f6", "type": "rect"},
    3: {"nom": "Triangle", "couleur": "#10b981", "type": "poly"},
    4: {"nom": "Losange", "couleur": "#f59e0b", "type": "diamond"}
}

solutions_trous1 = [
    "aléatoire", "issues", "univers", "élémentaire", "impossible",
    "certain", "contraire", "incompatibles", "équiprobabilite", "favorables",
    "totales", "fréquence", "convergence", "variable", "loi"
]

fragments = [
    "Une experience dont on ne peut prévoir le résultat est dite ", " . Ses résultats possibles sont appelées ' ",
    " et l'ensemble de ces derniers forme l' ", " . Un évenement ne contenant qu'une seule issue est qualifié d' ",
    " . Si sa probabilite est nulle, il est ", " , tandis qu'elle vaut 1 pour un evenement ",
    " . L'événement non réalisé est noté A-barre, c'est l'événement ", " de A. Deux événements disjoints sont dits ",
    " . S'ils ont la meme chance de se produire, on est en situation d' ", " . On calcule alors p en divisant les issues ",
    " par les issues ", " . En répétant l'essai, la proportion observée s'appelle la ",
    " , et son étude montre une ", " vers la probabilite théorique. Enfin, une fonction numérique associant un gain à une issue est une ",
    " aleatoire, dont l'étude des probabilités associées definit sa ", " de probabilité."
]

# Initialisation du dictionnaire de réponses utilisateur dans le session_state
if "reponses_trous" not in st.session_state:
    st.session_state.reponses_trous = {i: "" for i in range(15)}

def generer_et_telecharger_rapport3():
        """Génère le rapport d'évaluation technique HTML complet conforme aux

        calculs du tableau de contingence de l'Atelier 3.
        """
        import streamlit as st

        # 1. Récupération standard de l'identité validée à l'accueil
        nom_eleve = str(st.session_state.get("nom_var", "")).strip().upper()
        prenom_eleve = str(st.session_state.get("prenom_var", "")).strip().capitalize()
        classe_eleve = str(st.session_state.get("classe_var", "")).strip().upper()

        if nom_eleve in ["", "INCONNU", "NOM", "ELEVE"]:
            st.error("Action interdite : Veuillez d'abord renseigner et valider votre identité sur l'onglet d'accueil.")
            return ""
        sol = st.session_state.get("solution_courante", None)
        if sol and len(sol) >= 8:
            p_A_et_B = sol.get((0, 0), 0.20)
            p_Abar_et_B = sol.get((0, 1), 0.22)
            p_B = sol.get((0, 2), 0.42)
            p_A_et_Bbar = sol.get((1, 0), 0.23)
            p_Abar_et_Bbar = sol.get((1, 1), 0.35)
            p_Bbar = sol.get((1, 2), 0.58)
            p_A = sol.get((2, 0), 0.43)
            p_Abar = sol.get((2, 1), 0.57)
        else:
            # Valeurs par defaut preventives si l'export est clique a blanc
            p_A_et_B = 0.20
            p_Abar_et_B = 0.22
            p_B = 0.42
            p_A_et_Bbar = 0.23
            p_Abar_et_Bbar = 0.35
            p_Bbar = 0.58
            p_A = 0.43
            p_Abar = 0.57
            
        # 2. Récupération des données dynamiques de l'exercice courant
        filiere_texte = st.session_state.get("var_filiere", "Conducteur Routier")
        enonce_exercice = st.session_state.get("lbl_enonce", "Énoncé non généré.")

        # Vérification de la présence des matrices de solutions
        if "solution_courante" not in st.session_state or "cases_initiales" not in st.session_state:
            st.error("Erreur : Aucune donnée d'exercice actif à exporter.")
            return ""

        solution_courante = st.session_state.solution_courante
        cases_initiales = st.session_state.cases_initiales

        # 3. Calcul des points pour la Partie 1 : Le Tableau de contingence (Sur 10)
        score_tableau = 0.0
        cases_calculees_eleve = 0
        lignes_html_tableau_eval = ""
        cases_tableau = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1)]
        
        # Premier passage pour compter combien de cases l'élève devait réellement calculer
        for (i, j) in cases_tableau:
            if (i, j) in cases_initiales:
                continue
            cases_calculees_eleve += 1

        # Attribution des points par case calculable
        valeur_par_case = 10.0 / max(1, cases_calculees_eleve)
        noms_cases = ["P(A ∩ B)", "P(A̅ ∩ B)", "P(B) [Total]", "P(A ∩ B̅)", "P(A̅ ∩ B̅)", "P(B̅) [Total]", "P(A) [Total]", "P(A̅) [Total]"]

        for idx, (i, j) in enumerate(cases_tableau):
            # Lecture depuis la grille de session de l'Atelier 3
            cle_saisie = f"cell_tab3_{i}_{j}"
            val_saisie = str(st.session_state.get(cle_saisie, "")).strip().replace(',', '.')
            
            if " -> " in val_saisie:
                val_saisie = val_saisie.split(" -> ")[0].replace("\u0336", "")
                
            val_attendue = solution_courante.get((i, j), 0.0)
            intitule_case = noms_cases[idx]
            est_initiale = (i, j) in cases_initiales
            
            if est_initiale:
                statut_badge = '<span class="status-pass" style="color: #64748b; background-color: #f1f5f9; padding: 4px 10px; font-weight: bold; border-radius: 4px;">FOURNI</span>'
            else:
                try:
                    if abs(float(val_saisie) - val_attendue) < 0.01:
                        score_tableau += valeur_par_case
                        statut_badge = '<span class="status-pass" style="color: #16a34a; background-color: #dcfce7; padding: 4px 10px; font-weight: bold; border-radius: 4px;">CORRECT</span>'
                    else:
                        statut_badge = '<span class="status-fail" style="color: #dc2626; background-color: #fee2e2; padding: 4px 10px; font-weight: bold; border-radius: 4px;">INCORRECT</span>'
                except ValueError:
                    statut_badge = '<span class="status-fail" style="color: #dc2626; background-color: #fee2e2; padding: 4px 10px; font-weight: bold; border-radius: 4px;">INCORRECT</span>'
                    
            lignes_html_tableau_eval += f"""
            <tr>
                <td style="text-align: center; font-weight: bold; border: 1px solid #cbd5e1; padding: 10px;">{idx+1}</td>
                <td style="border: 1px solid #cbd5e1; padding: 10px;">Cellule {intitule_case} du tableau de contingence</td>
                <td style="border: 1px solid #cbd5e1; padding: 10px;">{val_saisie if val_saisie and not est_initiale else (f"{val_attendue:.2f}" if est_initiale else "Aucune réponse")}</td>
                <td style="font-weight: bold; border: 1px solid #cbd5e1; padding: 10px;">{val_attendue:.2f}</td>
                <td style="text-align: center; border: 1px solid #cbd5e1; padding: 10px;">{statut_badge}</td>
            </tr>"""
        
        note_tableau = round(score_tableau)

        # 4. Génération du tableau QCM (Partie 2 - Sur 10)
        score_qcm = 0
        lignes_html_qcm = ""
        quiz3_data = st.session_state.get("quiz3_data", [])

        for idx, item in enumerate(quiz3_data):
            intitule = item["q"]
            # Récupération de la clé correspondante dans la session
            reponse_saisie = str(st.session_state.get(f"quiz3_select_{idx}", "")).strip()
            valeur_attendue = item["rep"].strip()

            if reponse_saisie == valeur_attendue:
                score_qcm += 1
                statut_badge = '<span class="status-pass" style="color: #16a34a; background-color: #dcfce7; padding: 4px 10px; font-weight: bold; border-radius: 4px;">CORRECT</span>'
            else:
                statut_badge = '<span class="status-fail" style="color: #dc2626; background-color: #fee2e2; padding: 4px 10px; font-weight: bold; border-radius: 4px;">INCORRECT</span>'

            lignes_html_qcm += f"""
            <tr>
                <td style="text-align: center; font-weight: bold; border: 1px solid #cbd5e1; padding: 10px;">{idx+1}</td>
                <td style="text-align: left; border: 1px solid #cbd5e1; padding: 10px;">{intitule}</td>
                <td style="border: 1px solid #cbd5e1; padding: 10px;">{reponse_saisie if reponse_saisie else "Aucune réponse"}</td>
                <td style="font-weight: bold; border: 1px solid #cbd5e1; padding: 10px;">{valeur_attendue}</td>
                <td style="text-align: center; border: 1px solid #cbd5e1; padding: 10px;">{statut_badge}</td>
            </tr>"""
        note_qcm = score_qcm

        # 5. Génération du tableau Texte à trous (Partie 3 - Sur 10)
        score_trous = 0
        lignes_html_trous = ""
        solutions_trous3 = st.session_state.get("solutions_trous3", [])

        for idx, valeur_attendue in enumerate(solutions_trous3):
            cle_saisie_trou = f"trou3_{idx}"
            val_saisie = str(st.session_state.get(cle_saisie_trou, "")).strip()
            
            if " -> " in val_saisie:
                val_saisie = val_saisie.split(" -> ")[0].replace("\u0336", "")

            if val_saisie.lower() == valeur_attendue.lower() and val_saisie != "":
                score_trous += 1
                statut_badge = '<span class="status-pass" style="color: #16a34a; background-color: #dcfce7; padding: 4px 10px; font-weight: bold; border-radius: 4px;">CORRECT</span>'
            else:
                statut_badge = '<span class="status-fail" style="color: #dc2626; background-color: #fee2e2; padding: 4px 10px; font-weight: bold; border-radius: 4px;">INCORRECT</span>'

            lignes_html_trous += f"""
            <tr>
                <td style="text-align: center; font-weight: bold; border: 1px solid #cbd5e1; padding: 10px;">{idx+1}</td>
                <td style="text-align: left; font-style: italic; border: 1px solid #cbd5e1; padding: 10px;">Saisie associee au trou numero {idx+1} du texte de synthese</td>
                <td style="border: 1px solid #cbd5e1; padding: 10px;">{val_saisie if val_saisie else "Aucune reponse"}</td>
                <td style="font-weight: bold; border: 1px solid #cbd5e1; padding: 10px;">{valeur_attendue}</td>
                <td style="text-align: center; border: 1px solid #cbd5e1; padding: 10px;">{statut_badge}</td>
            </tr>"""

        note_qcm = score_qcm
        note_trous = score_trous
        score_global = note_tableau + note_qcm + note_trous
        couleur_note = "#16a34a" if score_global >= 15 else "#dc2626"
        date_h = st.session_state.get("date_heure", datetime.now().strftime("%d/%m/%Y %H:%M"))

        # # 6. REDACTION DU CODE HTML COMPLET CONFORME AU DESIGN REQUIS
        html_content = f"""<!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Rapport d'Evaluation Technique</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #f8fafc; color: #1e293b; }}
                .card {{ background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); position: relative; }}
                .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px 30px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
                .header-title {{ font-size: 24px; font-weight: bold; margin-bottom: 8px; }}
                .meta-info {{ font-size: 14px; line-height: 1.6; }}
                .score-box {{ position: absolute; right: 60px; top: 64px; background-color: #ffffff; color: #1e293b; padding: 10px 20px; border-radius: 6px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-width: 130px; }}
                .score-box .title {{ font-size: 9px; font-weight: bold; color: #64748b; text-transform: uppercase; margin-bottom: 2px; letter-spacing: 0.5px; }}
                .score-box .value {{ font-size: 32px; font-weight: bold; color: {couleur_note}; line-height: 1.1; }}
                .detail-box {{ background-color: #ffffff; border-left: 4px solid #2563eb; padding: 15px 20px; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 13px; line-height: 1.8; }}
                .detail-box .title {{ font-weight: bold; color: #0f172a; margin-bottom: 6px; text-transform: uppercase; }}
                .section-title {{ font-size: 16px; font-weight: bold; color: #1e3a8a; margin-top: 35px; margin-bottom: 15px; text-align: left; }}
                .sub-box {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 20px; font-size: 13px; line-height: 1.6; color: #334155; margin-bottom: 25px; white-space: pre-line; }}
                .contingence-table {{ width: auto; min-width: 400px; margin: 15px 0; border: 2px solid #cbd5e1; border-collapse: collapse; }}
                .contingence-table th {{ background-color: #f1f5f9; color: #1e293b; text-align: center; font-weight: bold; border: 1px solid #cbd5e1; padding: 10px; }}
                .contingence-table td {{ text-align: center; font-size: 14px; font-weight: bold; border: 1px solid #cbd5e1; background-color: #ffffff; padding: 10px; }}
                table {{ width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 30px; }}
                th {{ background-color: #0f172a; color: #ffffff; padding: 12px 14px; font-size: 13px; font-weight: bold; text-align: left; }}
                td {{ padding: 12px 14px; font-size: 13px; color: #334155; border-bottom: 1px solid #f1f5f9; }}
                tr:nth-child(even) td {{ background-color: #f8fafc; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="header-blue">
                    <div class="header-title">Professeur Laurent GALLET</div>
                    <div class="meta-info">
                        <strong>Eleve : </strong> {nom_eleve} {prenom_eleve} ({classe_eleve})<br>
                        <strong>Evaluation : </strong> Atelier 7 - Structure probabiliste : Analyse et contingence
                    </div>
                    <div class="score-box">
                        <div class="title">NOTE GLOBALE</div>
                        <div class="value">{score_global} / 30</div>
                    </div>
                </div>

                <div class="detail-box">
                    <div class="title">DETAIL GENERAL DES POINTS ACQUIS :</div>
                    - Note obtenue sur le Calcul de Tableau de Contingence : {note_tableau} / 10<br>
                    - Note obtenue sur le Questionnaire de fractions (QCM) : {note_qcm} / 10<br>
                    - Note obtenue sur la Synthese de texte a trous : {note_trous} / 10
                </div>

                <div class="section-title">Enonce initial de l'exercice - {filiere_texte}</div>
                <div class="sub-box" style="font-family: 'Segoe UI', sans-serif;">
                    {enonce_exercice}
                </div>

                <div class="section-title">Correction complete du Tableau de Contingence (Probabilites)</div>
                <table class="contingence-table">
                    <thead>
                        <tr>
                            <th></th>
                            <th>A</th>
                            <th>A̅</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="background-color: #f1f5f9;">B</td>
                            <td>{p_A_et_B:.2f}</td>
                            <td>{p_Abar_et_B:.2f}</td>
                            <td style="background-color: #f8fafc;">{p_B:.2f}</td>
                        </tr>
                        <tr>
                            <td style="background-color: #f1f5f9;">B̅</td>
                            <td>{p_A_et_Bbar:.2f}</td>
                            <td>{p_Abar_et_Bbar:.2f}</td>
                            <td style="background-color: #f8fafc;">{p_Bbar:.2f}</td>
                        </tr>
                        <tr>
                            <td style="background-color: #f1f5f9; font-weight: bold;">Total</td>
                            <td style="background-color: #f8fafc;">{p_A:.2f}</td>
                            <td style="background-color: #f8fafc;">{p_Abar:.2f}</td>
                            <td style="background-color: #e2e8f0;">1.00</td>
                        </tr>
                    </tbody>
                </table>

                <div class="section-title">Analyse detaillee des reponses de l'Atelier 3</div>
                
                <h3>Partie 1 : Grille des calculs du Tableau de Contingence</h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 5%; text-align: center;">N°</th>
                            <th style="width: 45%;">Composant Analyse</th>
                            <th style="width: 15%;">Saisie Eleve</th>
                            <th style="width: 15%;">Valeur Attendue</th>
                            <th style="width: 20%; text-align: center;">Resultat</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lignes_html_tableau_eval}
                    </tbody>
                </table>

                <h3>Partie 2 : Questionnaire de fractions (QCM)</h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 5%; text-align: center;">N°</th>
                            <th style="width: 45%;">Intitule de la Question</th>
                            <th style="width: 15%;">Saisie Eleve</th>
                            <th style="width: 15%;">Valeur Attendue</th>
                            <th style="width: 20%; text-align: center;">Resultat</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lignes_html_qcm}
                    </tbody>
                </table>

                <h3>Partie 3 : Synthese de cours (Texte a trous)</h3>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 5%; text-align: center;">N°</th>
                            <th style="width: 45%;">Emplacement de l'analyse</th>
                            <th style="width: 15%;">Saisie Eleve</th>
                            <th style="width: 15%;">Valeur Attendue</th>
                            <th style="width: 20%; text-align: center;">Resultat</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lignes_html_trous}
                    </tbody>
                </table>

                <div style="text-align: center; margin-top: 40px; color: #64748b; font-size: 11px; font-style: italic;">
                    Document genere de maniere automatisee par l'application de TP de Probabilites - Professeur Laurent GALLET.
                </div>
            </div>
        </body>
        </html>"""

        # L'indentation de 4 espaces rattache légitimement la fermeture au bloc def de votre fonction
        return html_content

def executer_simulation_loi_grands_nombres1():
            """Effectue la simulation de la loi des grands nombres et trace le graphique."""
            
            # Lecture sécurisée du mode de jeu (Atelier 1) depuis st.session_state
            mode_jeu = st.session_state.get("choix_jeu_simule", "De")
            n_lancers = 2000 

            st.subheader(f"Loi des Grands Nombres - Simulation : {mode_jeu}")

            # Création de la figure Matplotlib
            fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)
            frequences = [0.0]  # Initialisation préventive pour éviter les erreurs de portée

            # ----------------=====================================================
            # CAS 1 : SIMULATION DU DÉ LIBRE
            # ----------------=====================================================
            if mode_jeu == "De":
                n_faces = int(st.session_state.get("slider_faces_n1_valeur", 6))
                resultats = [random.randint(1, n_faces) for _ in range(n_lancers)]
                labels = [f"Face {i}" for i in range(1, n_faces + 1)]
                frequences = [resultats.count(i) / n_lancers for i in range(1, n_faces + 1)]
                prob_theorique = 1.0 / n_faces

                ax.bar(labels, frequences, color="#f43f5e", edgecolor="#b91c1c", width=0.55)
                ax.axhline(y=prob_theorique, color="#2563eb", linestyle="--", linewidth=2, 
                           label=f"Theorie (1/{n_faces} = {prob_theorique*100:.2f}%)")
                ax.set_title(f"Loi des Grands Nombres : De Libre a {n_faces} faces", fontweight="bold")

            # ----------------=====================================================
            # CAS 2 : SIMULATION DE LA SLOT MACHINE
            # ----------------=====================================================
            elif mode_jeu == "Slot":
                limit_shapes = int(st.session_state.get("slider_shapes_n1_valeur", 7))
                resultats = []
                for _ in range(n_lancers):
                    v1 = random.randint(1, limit_shapes)
                    v2 = random.randint(1, limit_shapes)
                    v3 = random.randint(1, limit_shapes)
                    verdict = "JACKPOT" if v1 == v2 == v3 else ("GAGNE" if (v1==v2 or v2==v3 or v1==v3) else "PERDU")
                    resultats.append(verdict)

                labels = ["JACKPOT", "GAGNE", "PERDU"]
                frequences = [resultats.count(lbl) / n_lancers for lbl in labels]
                
                p_jackpot = 1.0 / (limit_shapes ** 2)
                p_gagne = (3.0 * (limit_shapes - 1)) / (limit_shapes ** 2)
                p_perdu = 1.0 - p_jackpot - p_gagne

                ax.bar(labels, frequences, color="#eab308", edgecolor="#b45309", width=0.5)
                ax.axhline(y=p_jackpot, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Theorie Jackpot ({p_jackpot*100:.1f}%)")
                ax.axhline(y=p_gagne, color="#10b981", linestyle="--", linewidth=1.5, label=f"Theorie Gagne ({p_gagne*100:.1f}%)")
                ax.set_title(f"Slot Machine : Convergence de 3 rouleaux ({limit_shapes} formes)", fontweight="bold")

            # ----------------=====================================================
            # CAS 3 : SIMULATION DES PARIS DE LA ROULETTE
            # ----------------=====================================================
            elif mode_jeu == "Roulette":
                # CORRECTION DE LA CLE : Recupere la vraie mise effectuee sur l'interface
                combinaison_active = st.session_state.get("combinaison_active", "Rouge")
                type_pari_actif = st.session_state.get("type_pari", "Couleur")
                cpt_gagne = 0

                # Simulation de 2000 lancers independants
                for _ in range(n_lancers):
                    tirage = random.randint(0, 36)

                    # Verification des conditions de victoire selon les regles reelles
                    if tirage == 0:
                        couleur_gagnante = "Vert"
                        parite_gagnante = "Zero"
                        douzaine_gagnante = "Zero"
                        intervalle_gagnant = "Zero"
                    else:
                        rouges = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
                        couleur_gagnante = "Rouge" if tirage in rouges else "Noir"
                        parite_gagnante = "Even" if tirage % 2 == 0 else "Odd"
                        
                        if 1 <= tirage <= 12:
                            douzaine_gagnante = "1st 12"
                        elif 13 <= tirage <= 24:
                            douzaine_gagnante = "2nd 12"
                        else:
                            douzaine_gagnante = "3rd 12"
                        intervalle_gagnant = "1-18" if tirage <= 18 else "19-36"

                    # Increment du compteur si le tirage virtuel correspond au choix
                    if type_pari_actif == "Couleur" and combinaison_active == couleur_gagnante:
                        cpt_gagne += 1
                    elif type_pari_actif == "Parite" and combinaison_active == parite_gagnante:
                        cpt_gagne += 1
                    elif type_pari_actif == "Douzaine" and combinaison_active == douzaine_gagnante:
                        cpt_gagne += 1
                    elif type_pari_actif == "Manque/Passe" and combinaison_active == intervalle_gagnant:
                        cpt_gagne += 1
                    elif type_pari_actif == "Numero" and combinaison_active == str(tirage):
                        cpt_gagne += 1

                labels = ["GAGNE", "PERDU"]
                frequences = [cpt_gagne / n_lancers, (n_lancers - cpt_gagne) / n_lancers]

                # Determination de la cible de probabilite stricte de Bernoulli
                if type_pari_actif == "Numero" or str(combinaison_active).isdigit():
                    prob_g = 1.0 / 37.0
                    nom_affichage_titre = f"du numero {combinaison_active}"
                elif type_pari_actif == "Douzaine" or combinaison_active in ["1st 12", "2nd 12", "3rd 12"]:
                    prob_g = 12.0 / 37.0
                    nom_affichage_titre = f"de la douzaine {combinaison_active}"
                else:
                    prob_g = 18.0 / 37.0
                    nom_affichage_titre = f"du bloc '{combinaison_active}'"

                prob_p = 1.0 - prob_g

                # Graphique Matplotlib
                ax.bar(labels, frequences, color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
                ax.axhline(y=prob_g, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Theorie Gagne ({prob_g*100:.1f}%)")
                ax.axhline(y=prob_p, color="#2563eb", linestyle="--", linewidth=1.5, label=f"Theorie Perdu ({prob_p*100:.1f}%)")
                
                ax.set_title(f"Roulette : Simulation {nom_affichage_titre}", fontweight="bold")

                # Habillage commun du graphique
                ax.set_ylabel("Frequence observee")
                ax.set_ylim(0, max(max(frequences) * 1.25, 0.4))
                ax.legend(loc="upper right", fontsize=9)
                ax.grid(axis="y", linestyle="--", alpha=0.5)

                st.pyplot(fig, clear_figure=True)



def generer_et_telecharger_rapport1():
    """Génère le rapport d'évaluation technique HTML de la Tab 1 et fournit un bouton de téléchargement."""
    
    # 1. RÉCUPÉRATION DES VARIABLES D'IDENTITÉ DEPUIS LE SESSION STATE
    nom_eleve = str(st.session_state.get("nom_utilisateur", "INCONNU")).strip().upper()
    prenom_eleve = str(st.session_state.get("prenom_utilisateur", "INCONNU")).strip().capitalize()
    classe_eleve = str(st.session_state.get("classe_utilisateur", "INCONNUE")).strip().upper()

    if nom_eleve in ["", "INCONNU", "NOM", "ELEVE"]:
        st.warning("Action interdite : Veuillez d'abord renseigner votre identite sur l'onglet d'accueil.")
        return

    # 2. COLLECTE DES SCORES ET GÉNÉRATION DES LIGNES DU TABLEAU
    score = 0
    lignes_html_tableau = ""
    
    quiz_data = st.session_state.get("quiz1_data", [])
    reponses_user = st.session_state.get("reponses_quiz", {})

    for idx, item in enumerate(quiz_data):
        intitule = item.get("q", "Question probabiliste")
        reponse_saisie = str(reponses_user.get(idx, "")).strip()
        valeur_attendue = str(item.get("rep", "")).strip()

        if reponse_saisie == valeur_attendue:
            score += 1
            statut_badge = '<span class="status-pass">CORRECT</span>'
        else:
            statut_badge = '<span class="status-fail">INCORRECT</span>'

        lignes_html_tableau += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
            <td style="text-align: left; color: #1e293b;">{intitule}</td>
            <td style="color: #64748b;">{reponse_saisie if reponse_saisie else "Aucune reponse"}</td>
            <td style="font-weight: 500; color: #1e293b;">{valeur_attendue}</td>
            <td style="text-align: center;">{statut_badge}</td>
        </tr>"""

    # Calcul des notes de synthèse et récupération des paramètres
    note_sur_20 = (score / 10) * 20
    n_faces = int(st.session_state.get("slider_faces_n1_valeur", 6))

    # 3. LE CONTENU HTML ET CSS STRICT DE VOTRE STYLE
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Evaluation - Probabilites</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            background-color: #ffffff;
            color: #1e293b;
        }}
        .header-blue {{
            background-color: #2563eb;
            color: #ffffff;
            padding: 24px 30px;
            border-radius: 8px;
            position: relative;
            margin-bottom: 35px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header-title {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}
        .meta-info {{
            font-size: 14px;
            line-height: 1.6;
        }}
        .score-box {{
            position: absolute;
            right: 30px;
            top: 24px;
            background-color: #ffffff;
            color: #2563eb;
            padding: 12px 25px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            min-width: 120px;
        }}
        .score-box .title {{
            font-size: 9px;
            font-weight: bold;
            color: #475569;
            text-transform: uppercase;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }}
        .score-box .value {{
            font-size: 28px;
            font-weight: bold;
            color: {"#16a34a" if score>=6 else "#dc2626"};
            line-height: 1.1;
        }}
        .score-box .sub {{
            font-size: 11px;
            color: #64748b;
            margin-top: 2px;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: bold;
            color: #1e40af;
            margin-top: 35px;
            margin-bottom: 20px;
            text-align: left;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background-color: #334155;
            color: #ffffff;
            padding: 14px;
            font-size: 13px;
            font-weight: bold;
            text-align: left;
            border-bottom: 3px solid #1e293b;
        }}
        td {{
            padding: 14px;
            font-size: 13px;
            border-bottom: 1px solid #f1f5f9;
        }}
        tr:nth-child(even) td {{
            background-color: #f8fafc;
        }}
        .status-pass {{
            display: inline-block;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: bold;
            color: #16a34a;
            background-color: #dcfce7;
            border-radius: 4px;
            letter-spacing: 0.5px;
        }}
        .status-fail {{
            display: inline-block;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: bold;
            color: #dc2626;
            background-color: #fee2e2;
            border-radius: 4px;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>

    <div class="header-blue">
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Éleve : </strong> {nom_eleve} {prenom_eleve}<br>
            <strong>Évaluation type Numérique : </strong> Atelier 1 - Simulation probabiliste et jeux de hasard (Dé à {n_faces} faces)
        </div>
        <div class="score-box">
            <div class="title">NOTE FINALE</div>
            <div class="value">{score} / 10</div>
            <div class="sub">soit {note_sur_20:.1f} / 20</div>
        </div>
    </div>

    <div class="section-title">Résultats et correction du QCM - Jeux de hasard</div>
    
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">N°</th>
                <th style="width: 45%; text-align: left;">Intitule du calcul probabiliste demande</th>
                <th style="width: 18%; text-align: left;">Votre reponse saisie</th>
                <th style="width: 18%; text-align: left;">Valeur attendue / Correction</th>
                <th style="width: 14%; text-align: center;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html_tableau}
        </tbody>
    </table>

</body>
</html>"""
        # L'indentation de 4 espaces rattache légitimement la fermeture au bloc def de votre fonction
    return html_content

def basculer_mode_examen_protection3():
    """Protocole de l'Atelier 3 : Fige la session de contingence,

    brasse le QCM et le texte a trous tout en protegeant l'identite de l'eleve.
    """
    import random
    import streamlit as st

    # =========================================================================
    # ENREGISTREMENT ET SAUVEGARDE DE SÉCURITÉ DE L'IDENTITÉ
    # =========================================================================
    # On met precieusement de cote l'identite de l'eleve avant le re-brassage
    nom_sauvegarde = st.session_state.get("nom_var", "")
    prenom_sauvegarde = st.session_state.get("prenom_var", "")
    classe_sauvegarde = st.session_state.get("classe_var", "")
    # =========================================================================

    # 1. Activation officielle du drapeau d'examen de l'Atelier 3
    st.session_state.mode_examen_tab3_actif = True
    st.session_state.verrouille = True  # Maintient l'identification bloquee a l'accueil

    # 2. Re-tirage aleatoire d'une nouvelle filiere metier pour l'examen
    filieres_examen = [
        "Conducteur Routier",
        "Maintenance des Véhicules",
        "Travaux Publics (TP)"
    ]
    st.session_state.var_filiere = random.choice(filieres_examen)

    # 3. Forcer la regeneration immediate d'un nouvel enonce de contingence propre
    if "generer_exercice_filiere" in globals():
        generer_exercice_filiere()

    # 4. Suppression des anciennes questions pour forcer le re-brassage du Quiz 3
    if "quiz3_data" in st.session_state:
        del st.session_state.quiz3_data

    # 5. Reinitialisation complete des reponses aux trous pour l'examen
    if "corrections_visuelles_trous3" in st.session_state:
        del st.session_state.corrections_visuelles_trous3
        
    for i in range(10):
        st.session_state[f"trou3_{i}"] = ""

    # =========================================================================
    # RESTAURATION DE L'IDENTITÉ POUR EMPÊCHER LE RENVOI À L'ACCUEIL
    # =========================================================================
    # On reinjecte les donnees de l'eleve pour que le serveur valide son acces
    st.session_state.nom_var = nom_sauvegarde
    st.session_state.prenom_var = prenom_sauvegarde
    st.session_state.classe_var = classe_sauvegarde
    
def basculer_mode_examen_protection1():
    """Protocole de l'Atelier 1 : Fige la session, bloque les curseurs

    et brasse le QCM tout en protégeant l'identité de l'élève.
    """
    import random
    import streamlit as st

    # =========================================================================
    # EXTRACT ET SAUVEGARDE DE SÉCURITÉ DE L'IDENTITÉ
    # =========================================================================
    # On met précieusement de côté l'identité de l'élève avant le brassage
    nom_sauvegarde = st.session_state.get("nom_var", "")
    prenom_sauvegarde = st.session_state.get("prenom_var", "")
    classe_sauvegarde = st.session_state.get("classe_var", "")
    # =========================================================================

    # 1. Activation officielle du drapeau de verrouillage d'examen
    st.session_state.mode_examen_actif = True
    st.session_state.verrouille = True  # Maintient l'élève verrouillé à l'accueil

    # 2. Tirage aléatoire réglementaire du nombre de faces du Dé (Atelier 1)
    st.session_state.slider_faces_n1_valeur = random.randint(4, 20)

    # 3. Tirage du nombre de formes pour la machine à sous (Atelier 1)
    valeurs_possibles = [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    st.session_state.slider_shapes_n1_valeur = int(
        random.choice(valeurs_possibles)
    )

    # 4. Suppression des anciennes questions pour forcer le re-brassage du Quiz
    if "quiz1_data" in st.session_state:
        del st.session_state.quiz1_data

    # 5. Déclenchement de la simulation mathématique des grands nombres
    if "executer_simulation_loi_grands_nombres1" in globals():
        executer_simulation_loi_grands_nombres1()

    # Initialisation cinématique propre de la roue de la roulette sans appel sauvage
    st.session_state.orientation_aiguille = 0.0
    st.session_state.dernier_statut_roue = "Attente"

    # =========================================================================
    # RESTAURATION DE L'IDENTITÉ POUR EMPÊCHER LE RENVOI À L'ACCUEIL
    # =========================================================================
    # On reinjecte les donnees de l'eleve pour que le serveur valide son acces
    st.session_state.nom_var = nom_sauvegarde
    st.session_state.prenom_var = prenom_sauvegarde
    st.session_state.classe_var = classe_sauvegarde
    # =========================================================================



def valider_tout1():
    """Corrige le QCM, enregistre la note et active le verrouillage de session."""
    
    # 1. Récupération et vérification de l'identité de l'élève
    nom_eleve = str(st.session_state.get("nom_utilisateur", "")).strip().upper()
    
    if nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]:
        st.error("Action interdite : Veuillez d'abord renseigner votre identite sur la page d'accueil.")
        return

    # 2. Calcul du score à partir des réponses enregistrées dans la session
    score = 0
    # On présume que 'quiz1_data' et 'reponses_quiz' ont été initialisés dans setup_quiz1
    quiz_data = st.session_state.get("quiz1_data", [])
    reponses_user = st.session_state.get("reponses_quiz", {})

    st.write("---")
    st.subheader("Correction Detaillee du QCM")

    for idx, item in enumerate(quiz_data):
        user_rep = reponses_user.get(idx, "")
        correct_rep = item["rep"]
        
        if user_rep == correct_rep:
            score += 1
            st.markdown(f'<p style="color:#16a34a; margin:2px 0px;">Question {idx+1} : Correct ({user_rep})</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:#dc2626; margin:2px 0px;">Question {idx+1} : Incorrect (Votre choix : "{user_rep}" | Attendu : "{correct_rep}")</p>', unsafe_allow_html=True)

    # 3. Calcul des notes finales
    note_sur_20 = (score / 10) * 20
    st.session_state.score_final_quiz = score
    
    # 4. Enclenchement du verrouillage définitif
    st.session_state.quiz_deja_valide = True

    # 5. Affichage du bandeau de résultat officiel
    couleur_score = "#16a34a" if score >= 6 else "#dc2626"
    st.markdown(
        f'<div style="padding:10px; background-color:#f5f5f5; border-radius:4px; font-weight:bold; color:{couleur_score};">'
        f'Nom : {nom_eleve} | Note QCM : {score} / 10 (soit {note_sur_20:.1f}/20)'
        f'</div>', 
        unsafe_allow_html=True
    )
    
    st.success(f"Votre evaluation a ete corrigee avec succes ! Note enregistree : {score} / 10.")

def dessiner_roue_tricolore1(angle_bille, phase="Animation"):
    """Dessine géométriquement la vraie roue de roulette européenne

    avec l'alternance réglementaire des numéros et place la bille blanche.
    """
    import math
    import matplotlib.pyplot as plt
    import streamlit as st

    # NETTOYAGE : Aucun code de verrou ici, on commence directement le dessin Matplotlib
    fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.axis("off")

    # Ordre officiel réglementaire des 37 numéros (sens horaire depuis le 0)
    ordre_officiel = [
        0,
        32,
        15,
        19,
        4,
        21,
        2,
        25,
        17,
        34,
        6,
        27,
        13,
        36,
        11,
        30,
        8,
        23,
        10,
        5,
        24,
        16,
        33,
        1,
        20,
        14,
        31,
        9,
        22,
        18,
        29,
        7,
        28,
        12,
        35,
        3,
        26,
    ]
    rouges = [
        1,
        3,
        5,
        7,
        9,
        12,
        14,
        16,
        18,
        19,
        21,
        23,
        25,
        27,
        30,
        32,
        34,
        36,
    ]

    # 1. Structure extérieure en bois et piste circulaire
    ax.add_patch(plt.Circle((0, 0), 1.3, color="#78350f", ec="#451a03", lw=2))
    ax.add_patch(plt.Circle((0, 0), 1.15, color="#1e293b", ec="#334155", lw=2))
    ax.add_patch(plt.Circle((0, 0), 0.85, color="#0f172a", ec="#1e293b", lw=1))

    # 2. Dessin des 37 cases colorées et écriture des numéros de la couronne
    angle_secteur = 2 * math.pi / 37

    for idx, num in enumerate(ordre_officiel):
        # Décalage de 90° (pi/2) pour positionner le 0 au sommet vertical de la roue
        start_a = (math.pi / 2) - (idx * angle_secteur) - (angle_secteur / 2)
        end_a = start_a + angle_secteur

        # Attribution de la couleur officielle
        if num == 0:
            c_case = "#16a34a"  # Vert Zéro
        elif num in rouges:
            c_case = "#dc2626"  # Rouge
        else:
            c_case = "#111827"  # Noir

        # Remplissage de la fente du numéro
        angles_t = [
            start_a + (end_a - start_a) * (k / 10) for k in range(11)
        ]
        x_polygon = [0.85 * math.cos(a) for a in angles_t] + [
            1.15 * math.cos(a) for a in reversed(angles_t)
        ]
        y_polygon = [0.85 * math.sin(a) for a in angles_t] + [
            1.15 * math.sin(a) for a in reversed(angles_t)
        ]
        ax.fill(x_polygon, y_polygon, color=c_case, ec="#334155", lw=0.5)

        # Inscription et orientation du texte face au centre de la fente
        angle_texte = (start_a + end_a) / 2
        xt = 1.0 * math.cos(angle_texte)
        yt = 1.0 * math.sin(angle_texte)

        rot_deg = math.degrees(angle_texte) - 90
        if rot_deg < -90 or rot_deg > 90:
            rot_deg += 180

        ax.text(
            xt,
            yt,
            str(num),
            color="#ffffff",
            fontsize=7,
            fontweight="bold",
            ha="center",
            va="center",
            rotation=rot_deg,
        )

    # 3. Toupie centrale en laiton (Dessinée après les rayons pour masquer les lignes serrées)
    ax.add_patch(
        plt.Circle(
            (0, 0), 0.55, facecolor="#ca8a04", edgecolor="#eab308", lw=1.5, zorder=3
        )
    )
    ax.add_patch(
        plt.Circle(
            (0, 0), 0.35, facecolor="#854d0e", edgecolor="#ca8a04", lw=1, zorder=4
        )
    )

    # Les 4 bras de la toupie dorée
    for angle_bras in [0, 90, 180, 270]:
        rad_b = math.radians(angle_bras)
        ax.plot(
            [0, 0.5 * math.cos(rad_b)],
            [0, 0.5 * math.sin(rad_b)],
            color="#eab308",
            lw=3,
            zorder=5,
        )
        ax.add_patch(
            plt.Circle(
                (0.5 * math.cos(rad_b), 0.5 * math.sin(rad_b)),
                0.04,
                color="#eab308",
                zorder=6,
            )
        )

    # Pivot central blanc opaque
    ax.add_patch(plt.Circle((0, 0), 0.08, color="#ffffff", zorder=7))

    # 4. PLACEMENT DE LA BILLE BLANCHE LUMINEUSE
    if phase == "Animation":
        # Trajectoire circulaire extérieure haute vitesse
        rad_bille = math.radians(angle_bille)
        xb, yb = 1.22 * math.cos(rad_bille), 1.22 * math.sin(rad_bille)
    else:
        # Blocage final au fond de la case du numéro gagnant
        num_gagnant = st.session_state.get("index_gagnant_roue", 0)
        idx_gagnant = (
            ordre_officiel.index(num_gagnant)
            if num_gagnant in ordre_officiel
            else 0
        )
        angle_arret = (math.pi / 2) - (idx_gagnant * angle_secteur)
        xb, yb = 0.72 * math.cos(angle_arret), 0.72 * math.sin(angle_arret)

    # Tracé sphérique de la bille blanche
    ax.add_patch(
        plt.Circle(
            (xb, yb),
            0.045,
            facecolor="#ffffff",
            edgecolor="#94a3b8",
            lw=1,
            zorder=10,
        )
    )

    # 5. ÉCRITURE DU NUMÉRO SUR LE DISQUE CENTRAL À L'ARRÊT
    if phase == "Cloture":
        ax.text(
            0,
            0,
            str(st.session_state.index_gagnant_roue),
            color="#ffffff",
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=12,
        )

    st.pyplot(fig, clear_figure=True)

def dessiner_tapis_avec_jeton_grand():
    """Génère le vrai tapis de la roulette européenne avec ses 37 numéros colorés

    et positionne le jeton de manière chirurgicale.
    """
    fig, ax = plt.subplots(figsize=(10, 4.2), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    # Grille de coordonnées fixe : X de 0 à 1400, Y de 0 à 500
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 500)
    ax.axis("off")

    # Table des 18 numéros rouges officiels
    rouges = [
        1,
        3,
        5,
        7,
        9,
        12,
        14,
        16,
        18,
        19,
        21,
        23,
        25,
        27,
        30,
        32,
        34,
        36,
    ]

    # Fond vert feutre de casino
    ax.add_patch(
        plt.Rectangle(
            (10, 10), 1380, 480, facecolor="#059669", edgecolor="#ffffff", lw=2
        )
    )

    # 1. TRACÉ DE LA CASE 0 (À gauche, triangulaire/rectangulaire verte)
    ax.add_patch(
        plt.Rectangle(
            (30, 200), 70, 240, facecolor="#16a34a", edgecolor="#ffffff", lw=1.5
        )
    )
    ax.text(
        65,
        320,
        "0",
        color="#ffffff",
        fontsize=16,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # 2. TRACÉ DE LA GRILLE DES 36 NUMÉROS (12 colonnes x 3 lignes)
    # Origine de la grille : X = 100, Y = 200. Chaque case fait 100px de large et 80px de haut.
    largeur_c = 100
    hauteur_c = 80
    x_start = 100
    y_start = 200

    coordonnees_numeros = {}

    for num in range(1, 37):
        # Détermination de la colonne (0 à 11) et de la ligne (0 à 2)
        # Ligne 0 = Bas (3, 6, 9...), Ligne 2 = Haut (1, 4, 7...) pour coller au vrai tapis
        col = (num - 1) // 3
        lig = (num - 1) % 3

        x_box = x_start + col * largeur_c
        y_box = y_start + lig * hauteur_c

        # Stockage du centre de la case pour le jeton
        coordonnees_numeros[num] = (
            x_box + largeur_c / 2,
            y_box + hauteur_c / 2,
        )

        # Attribution de la vraie couleur réglementaire
        c_fond = "#dc2626" if num in rouges else "#111827"

        # Dessin de la case numérique
        ax.add_patch(
            plt.Rectangle(
                (x_box, y_box),
                largeur_c,
                hauteur_c,
                facecolor=c_fond,
                edgecolor="#ffffff",
                lw=1.5,
            )
        )
        ax.text(
            x_box + largeur_c / 2,
            y_box + hauteur_c / 2,
            str(num),
            color="#ffffff",
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
        )

    # 3. TRACÉ DES DOUZAINES (Sous la grille des numéros : Y = 130 à 190)
    for d in range(3):
        xd = x_start + d * 400
        ax.add_patch(
            plt.Rectangle(
                (xd, 130), 400, 50, facecolor="#065f46", edgecolor="#ffffff", lw=1.5
            )
        )
    ax.text(
        300,
        155,
        "1st 12",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )
    ax.text(
        700,
        155,
        "2nd 12",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )
    ax.text(
        1100,
        155,
        "3rd 12",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # 4. TRACÉ DES CHANCES SIMPLES (Tout en bas : Y = 60 à 110)
    largeur_cs = 200
    # Manque 1-18
    ax.add_patch(
        plt.Rectangle(
            (100, 60),
            largeur_cs,
            50,
            facecolor="#065f46",
            edgecolor="#ffffff",
            lw=1.5,
        )
    )
    ax.text(
        200,
        85,
        "1 - 18",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # Pair
    ax.add_patch(
        plt.Rectangle(
            (300, 60),
            largeur_cs,
            50,
            facecolor="#065f46",
            edgecolor="#ffffff",
            lw=1.5,
        )
    )
    ax.text(
        400,
        85,
        "PAIR",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # ROUGE (Losange de couleur)
    ax.add_patch(
        plt.Rectangle(
            (500, 60),
            largeur_cs,
            50,
            facecolor="#dc2626",
            edgecolor="#ffffff",
            lw=1.5,
        )
    )
    ax.text(
        600,
        85,
        "ROUGE",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # NOIR (Losange de couleur)
    ax.add_patch(
        plt.Rectangle(
            (700, 60),
            largeur_cs,
            50,
            facecolor="#111827",
            edgecolor="#ffffff",
            lw=1.5,
        )
    )
    ax.text(
        800,
        85,
        "NOIR",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # Impair
    ax.add_patch(
        plt.Rectangle(
            (900, 60),
            largeur_cs,
            50,
            facecolor="#065f46",
            edgecolor="#ffffff",
            lw=1.5,
        )
    )
    ax.text(
        1000,
        85,
        "IMPAIR",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # Passe 19-36
    ax.add_patch(
        plt.Rectangle(
            (1100, 60),
            largeur_cs,
            50,
            facecolor="#065f46",
            edgecolor="#ffffff",
            lw=1.5,
        )
    )
    ax.text(
        1200,
        85,
        "19 - 36",
        color="#ffffff",
        fontsize=11,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # 5. POSITIONNEMENT GÉOMÉTRIQUE STRICT DU GROS JETON D'APRES LE PARI
    pari_mode = st.session_state.type_pari
    choix = st.session_state.combinaison_active

    # Position par défaut de sécurité
    jx, jy = 700, 280

    if pari_mode == "Couleur":
        jx = 600 if choix == "Rouge" else 800
        jy = 85
    elif pari_mode == "Parite":
        jx = 400 if choix == "Even" else 1000
        jy = 85
    elif pari_mode == "Manque/Passe":
        jx = 200 if choix == "1-18" else 1200
        jy = 85
    elif pari_mode == "Douzaine":
        if choix == "1st 12":
            jx = 300
        elif choix == "2nd 12":
            jx = 700
        else:
            jx = 1100
        jy = 155
    elif pari_mode == "Numero":
        try:
            num = int(choix)
            if num == 0:
                jx, jy = 65, 320
            elif 1 <= num <= 36:
                jx, jy = coordonnees_numeros[num]
        except:
            pass

    # Dessin du gros jeton de casino dore
    jeton_bord = plt.Circle(
        (jx, jy), 26, facecolor="#eab308", edgecolor="#ffffff", lw=2, zorder=20
    )
    jeton_coeur = plt.Circle(
        (jx, jy),
        18,
        facecolor="#ca8a04",
        edgecolor="#eab308",
        lw=0.5,
        zorder=21,
    )
    ax.add_patch(jeton_bord)
    ax.add_patch(jeton_coeur)

    # Valeur de la mise sur le jeton
    ax.text(
        jx,
        jy,
        f"{st.session_state.mise}$",
        color="#ffffff",
        fontsize=9,
        fontweight="bold",
        ha="center",
        va="center",
        zorder=22,
    )

    return fig

    
def animer_roue_hasard1():
    """Détermine le numéro gagnant de manière instantanée avec un spinner visuel fluide

    pour éviter tout tremblement ou clignotement à l'écran.
    """
    import random
    import time

    st.session_state.dernier_statut_roue = "En cours"

    # 1. SIMULATION DU TEMPS DE ROULEMENT AVEC UN BANDEAU DE CHARGEMENT PROPRE
    with st.spinner("La roue tourne... La bille est lancée dans le cylindre..."):
        # On fait une pause physique de 1.2 seconde (Garantit aucun clignotement graphique)
        time.sleep(1.2)

    # 2. TIRAGE DU NUMÉRO SÉCURISÉ
    ordre_officiel = (0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26)
    numero_gagnant = random.choice(ordre_officiel)
    st.session_state.index_gagnant_roue = numero_gagnant

    # Calcul de l'angle d'arrêt fixe correspondant au numéro sur le cylindre
    n_num = 37
    angle_secteur = 360.0 / n_num
    idx_gagnant = ordre_officiel.index(numero_gagnant)
    st.session_state.orientation_aiguille = (90.0 - angle_secteur - (idx_gagnant * angle_secteur)) % 360

    # Détermination des propriétés physiques
    rouges = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    couleur_gagnante = "Vert" if numero_gagnant == 0 else ("Rouge" if numero_gagnant in rouges else "Noir")
    parite_gagnante = "Zero" if numero_gagnant == 0 else ("Even" if numero_gagnant % 2 == 0 else "Odd")
    
    if numero_gagnant == 0:
        douzaine_gagnante = "Zero"
        intervalle_gagnant = "Zero"
    else:
        if 1 <= numero_gagnant <= 12:
            douzaine_gagnante = "1st 12"
        elif 13 <= numero_gagnant <= 24:
            douzaine_gagnante = "2nd 12"
        else:
            douzaine_gagnante = "3rd 12"
        intervalle_gagnant = "1-18" if numero_gagnant <= 18 else "19-36"

    # 3. LOGIQUE DE VICTOIRE ET COMPTABILITÉ
    gagne = verifier_victoire_pari1_pour_numero(numero_gagnant)
    st.session_state.victoire_pari = gagne

    type_pari_actif = st.session_state.get("type_pari", "Couleur")
    if gagne:
        facteur_gain = 35.0 if type_pari_actif == "Numero" else (2.0 if type_pari_actif == "Douzaine" else 1.0)
        valeur_gain = float(st.session_state.mise) * facteur_gain
        st.session_state.solde += valeur_gain
        st.session_state.roulette_gagnes += 1
        st.session_state.dernier_message_roulette = f"Gagné ! La bille s'est arrêtée sur : {numero_gagnant} ({couleur_gagnante}). Vous gagnez {valeur_gain:.1f} €."
        st.session_state.statut_dernier_lancer = "success"
    else:
        st.session_state.solde -= float(st.session_state.mise)
        st.session_state.roulette_perdus += 1
        st.session_state.dernier_message_roulette = f"Perdu ! La bille s'est arrêtée sur : {numero_gagnant} ({couleur_gagnante})."
        st.session_state.statut_dernier_lancer = "error"

    st.session_state.dernier_statut_roue = "Fini"
    st.rerun()

def verifier_victoire_pari1():
    """Liaison passerelle pour la compatibilite avec l'animation principale."""
    index_gagnant = st.session_state.get("index_gagnant_roue", 0)
    return verifier_victoire_pari1_pour_numero(index_gagnant)


def verifier_victoire_pari1_pour_numero(num_sorti):
    """Verifie si le numero sorti valide la combinaison du tapis choisie."""
    combinaison = str(st.session_state.get("combinaison_active", "Rouge"))
    numeros_rouges = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

    if num_sorti == 0:
        return (combinaison == "0")

    if combinaison.isdigit():
        return (num_sorti == int(combinaison))

    if combinaison == "1st 12":
        return (1 <= num_sorti <= 12)
    elif combinaison == "2nd 12":
        return (13 <= num_sorti <= 24)
    elif combinaison == "3rd 12":
        return (25 <= num_sorti <= 36)

    if combinaison == "1-18":
        return (1 <= num_sorti <= 18)
    elif combinaison == "19-36":
        return (19 <= num_sorti <= 36)

    if combinaison == "Rouge":
        return (num_sorti in numeros_rouges)
    elif combinaison == "Noir":
        return (num_sorti not in numeros_rouges)
        
    if combinaison == "Even":
        return (num_sorti % 2 == 0)
    elif combinaison == "Odd":
        return (num_sorti % 2 != 0)

    return False


def valider_saisie():
    """Valide et nettoie les données d'identification de l'élève

    en les fixant définitivement dans la mémoire persistante de session.
    """
    import streamlit as st

    # Récupération et nettoyage strict des textes saisis
    nom_clean = str(st.session_state.get("nom_var", "")).strip().upper()
    prenom_clean = str(st.session_state.get("prenom_var", "")).strip().capitalize()
    classe_clean = str(st.session_state.get("classe_var", "")).strip().upper()

    if not nom_clean or not prenom_clean or not classe_clean or nom_clean in ["NOM", "ELEVE", "INCONNU"]:
        st.error("Erreur : Veuillez completer entierement vos donnees et valider.")
        st.session_state.verrouille = False
    else:
        # CORRECTIF CRITIQUE : On enregistre les versions propres dans la session !
        st.session_state.nom_var = nom_clean
        st.session_state.prenom_var = prenom_clean
        st.session_state.classe_var = classe_clean
        st.session_state.verrouille = True
        
        st.success(f"Validation effectuee pour : {nom_clean} {prenom_clean} {classe_clean}. Le formulaire est maintenant verrouille.")


def valider_session():
    """Fonction miroir de sécurité pour l'ouverture des droits d'ateliers."""
    valider_saisie()


def preparer_nom_fichier(nom_onglet):
    """Génère un nom de fichier standardisé pour les rapports d'évaluation."""
    import streamlit as st
    from datetime import datetime

    nom_propre = str(st.session_state.get("nom_var", "ELEVE")).replace(" ", "_")
    prenom_propre = str(st.session_state.get("prenom_var", "PRENOM")).replace(" ", "_")
    classe_propre = str(st.session_state.get("classe_var", "GROUPE")).replace(" ", "_")

    maintenant = datetime.now()
    heure_actuelle = maintenant.strftime("%H-%M-%S")
    date_texte = maintenant.strftime("%Y-%m-%d_%Hh%M")

    nom_fichier = f"{nom_propre}_{prenom_propre}_{classe_propre}_{date_texte}_{heure_actuelle}_{nom_onglet}.txt"
    return nom_fichier


# =============================================================================
# DÉCLARATION OFFICIELLE DES 10 ONGLETS DE NAVIGATION SÉCURISÉS
# =============================================================================
tabs = st.tabs([
    "Identification",
    "1. Jeux de hasard",
    "2. Les differentes lumieres",
    "3. Tableau de proportionnalites",
    "4. Arbre de probabilites",
    "5. Esperance mathematique et variance",
    "6. Loi exponentielle",
    "7. Exemple 1",
    "8. Exemple 2",
    "9. Exemple 3"
])
# Assignation des variables d'onglets (C'est ici que tab0 est créé !)
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = tabs
with tab0:
    st.subheader("Identification")
    
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        # Saisie directe avec la clé persistante de session
        nom_brut = st.text_input(
            "Nom :",
            value=st.session_state.get("nom_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="nom_var_input_persistant"
        )
        prenom_brut = st.text_input(
            "Prénom :",
            value=st.session_state.get("prenom_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="prenom_var_input_persistant"
        )
        classe_brut = st.text_input(
            "Groupe / Classe :",
            value=st.session_state.get("classe_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="classe_var_input_persistant"
        )
        
        # Sauvegarde immédiate
        st.session_state.nom_var = nom_brut.strip().upper()
        st.session_state.prenom_var = prenom_brut.strip().capitalize()
        st.session_state.classe_var = classe_brut.strip().upper()
        
        st.write("")
        
        if st.button("Ok", key="btn_ok_identification_maitre"):
            if st.session_state.nom_var in ["", "NOM", "ELEVE", "INCONNU"]:
                st.error("Veuillez entrer un véritable nom avant de cliquer sur Ok.")
            else:
                st.session_state.verrouille = True
                st.success(f"Bienvenue {st.session_state.nom_var}. Vos Ateliers sont déverrouillés !")
                st.rerun()
with tab1:
    
    st.subheader("Les jeux de hasards")
    col1, col2, col3 = st.columns(3)
    if not st.session_state.get("verrouille", False):
        st.warning(
            "Accès restreint : Veuillez d'abord renseigner votre identité et cliquer sur OK dans l'onglet 'Identification'."
        )
        # On arrête la lecture de cet onglet ici tant que l'élève n'est pas identifié
        st.stop()    
    with col1:
        st.markdown("### La roulette")

        # 1. INITIALISATION DES COMPTEURS STATISTIQUES DE SESSION
        if "solde" not in st.session_state:
            st.session_state.solde = 100.0
        if "mise" not in st.session_state:
            st.session_state.mise = 1.0
        if "type_pari" not in st.session_state:
            st.session_state.type_pari = "Couleur"
        if "combinaison_active" not in st.session_state:
            st.session_state.combinaison_active = "Rouge"
        if "roulette_gagnes" not in st.session_state:
            st.session_state.roulette_gagnes = 0
        if "roulette_perdus" not in st.session_state:
            st.session_state.roulette_perdus = 0
        if "dernier_statut_roue" not in st.session_state:
            st.session_state.dernier_statut_roue = "Attente"

        # 2. ENTRÉE DES PARAMÈTRES PAR L'ÉLÈVE
        st.session_state.mise = st.number_input(
            "Montant de la mise (€) :",
            min_value=1.0,
            max_value=float(st.session_state.solde)
            if float(st.session_state.solde) > 1.0
            else 1.0,
            value=float(st.session_state.mise)
            if float(st.session_state.mise) <= float(st.session_state.solde)
            else 1.0,
            step=1.0,
            key="input_montant_mise_roulette_unique",
        )

        mode_roulette = st.selectbox(
            "Type de pari :",
            options=["Couleur", "Parite", "Douzaine", "Manque/Passe", "Numero"],
            key="select_type_pari_roulette_unique",
        )
        st.session_state.type_pari = mode_roulette

        if st.session_state.type_pari == "Couleur":
            choix_coul = st.selectbox(
                "Placer le jeton sur la couleur :",
                options=["Rouge", "Noir"],
                key="sb_coul_unique",
            )
            st.session_state.combinaison_active = choix_coul
        elif st.session_state.type_pari == "Parite":
            choix_par = st.selectbox(
                "Placer le jeton sur :",
                options=["Pair", "Impair"],
                key="sb_par_unique",
            )
            st.session_state.combinaison_active = (
                "Even" if choix_par == "Pair" else "Odd"
            )
        elif st.session_state.type_pari == "Douzaine":
            choix_douz = st.selectbox(
                "Placer le jeton sur la douzaine :",
                options=["1st 12", "2nd 12", "3rd 12"],
                key="sb_douz_unique",
            )
            st.session_state.combinaison_active = choix_douz
        elif st.session_state.type_pari == "Manque/Passe":
            choix_mp = st.selectbox(
                "Placer le jeton sur l'intervalle :",
                options=["1-18", "19-36"],
                key="sb_mp_unique",
            )
            st.session_state.combinaison_active = choix_mp
        elif st.session_state.type_pari == "Numero":
            numero_devine = st.number_input(
                "Placer le jeton sur le numero plein (1 a 36) :",
                min_value=1,
                max_value=36,
                value=1,
                step=1,
                key="in_num_unique",
            )
            st.session_state.combinaison_active = str(numero_devine)

        st.markdown(
            f"**Solde actuel disponible :** {st.session_state.solde:.1f} €"
        )

        # 3. ACTIONNEUR DE TIRAGE AVEC VERROUILLAGE ÉLECTRONIQUE DE STATUT
        zone_roue_unique = st.empty()

        if st.button("Tourner la Roue [R]", key="btn_lancer_roulette_officielle_unique_v26"):
            animer_roue_hasard1()

        # # 4. RENDU STATIQUE VERROUILLÉ SANS TREMBLEMENT
        statut_actuel = st.session_state.get("dernier_statut_roue", "Attente")

        if statut_actuel == "Fini":
            st.markdown("**Position d'arrêt de la bille dans le cylindre :**")
            dessiner_roue_tricolore1(st.session_state.orientation_aiguille, "Cloture")
            
            if st.session_state.get("statut_dernier_lancer") == "success":
                st.success(st.session_state.dernier_message_roulette)
            else:
                st.error(st.session_state.dernier_message_roulette)
                
        else:
            st.markdown("**Cylindre de la roulette en attente :**")
            dessiner_roue_tricolore1(st.session_state.orientation_aiguille, "Animation")

        # # 5. LE GRAND TAPIS DE JEU INTERACTIF (Placé proprement tout en bas)
        st.markdown("---")
        st.markdown("**Positionnement de votre jeton sur le tapis :**")
        fig_tapis_interactif = dessiner_tapis_avec_jeton_grand()
        st.pyplot(fig_tapis_interactif, clear_figure=True)

        # 6. COMPTEURS STATISTIQUES GLOBALISÉS DE LA ROULETTE
        st.markdown("---")
        total_lancers = (
            st.session_state.roulette_gagnes + st.session_state.roulette_perdus
        )
        pct_gagnes = (
            (st.session_state.roulette_gagnes / total_lancers * 100)
            if total_lancers > 0
            else 0.0
        )
        pct_perdus = (
            (st.session_state.roulette_perdus / total_lancers * 100)
            if total_lancers > 0
            else 0.0
        )

        st.markdown(
            f":green[Roulette Gagnés : {st.session_state.roulette_gagnes}/{total_lancers} ({pct_gagnes:.1f}%)]"
        )
        st.markdown(
            f":red[Roulette Perdus : {st.session_state.roulette_perdus}/{total_lancers} ({pct_perdus:.1f}%)]"
        )


    with col2:
        st.markdown("Machine SLOT")


        if "total_lancers_slot" not in st.session_state:
            st.session_state.total_lancers_slot = 0
        if "cpt_classe_jackpots" not in st.session_state:
            st.session_state.cpt_classe_jackpots = 0
        if "cpt_classe_gagnes" not in st.session_state:
            st.session_state.cpt_classe_gagnes = 0
        if "liste_casino_view1" not in st.session_state:
            st.session_state.liste_casino_view1 = []

        # Déclaration du dictionnaire des formes géométriques de la machine
        if "FORMES_CASINO" not in globals():
            FORMES_CASINO = {
                1: {"nom": "Carre", "couleur": "#ef4444", "type": "rect"},
                2: {"nom": "Cercle", "couleur": "#3b82f6", "type": "oval"},
                3: {"nom": "Triangle", "couleur": "#10b981", "type": "poly"},
                4: {"nom": "Losange", "couleur": "#fbbf24", "type": "diamond"},
            }

        # 1. DÉFINITION PROPRE DE LA FONCTION GRAPHIQUE EN AMONT
        def dessiner_machine_casino1(v1, v2, v3, verdict):
            """Génère le rendu vectoriel des 3 rouleaux alignés de la machine."""
            import matplotlib.patches as patches
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(6, 1.05), dpi=100)
            fig.patch.set_facecolor("#ffffff")
            ax.set_facecolor("#ffffff")
            ax.axis("off")
            ax.set_xlim(0, 600)
            ax.set_ylim(0, 105)

            w_boite = 50
            h_boite = 50
            y_boite = 52.5 - 25
            espace = 15
            x_start_bloc = 180  # Recalage horizontal centré pour le rendu web

            positions_x = [
                x_start_bloc,
                x_start_bloc + w_boite + espace,
                x_start_bloc + 2 * (w_boite + espace),
            ]
            tirages = [v1, v2, v3]

            for idx, x_start in enumerate(positions_x):
                rect_fond = patches.Rectangle(
                    (x_start, y_boite),
                    w_boite,
                    h_boite,
                    facecolor="#2d2d39",
                    edgecolor="#fbbf24",
                    linewidth=2,
                )
                ax.add_patch(rect_fond)

                f_config = FORMES_CASINO.get(
                    tirages[idx],
                    {"nom": "Cercle", "couleur": "#ec4899", "type": "oval"},
                )
                cx = x_start + (w_boite / 2)
                cy = y_boite + (h_boite / 2)
                r = 11

                if f_config["type"] == "rect":
                    forme = patches.Rectangle(
                        (cx - r, cy - r),
                        2 * r,
                        2 * r,
                        facecolor=f_config["couleur"],
                        edgecolor="#ffffff",
                    )
                    ax.add_patch(forme)
                elif f_config["type"] == "oval":
                    forme = patches.Circle(
                        (cx, cy),
                        r,
                        facecolor=f_config["couleur"],
                        edgecolor="#ffffff",
                    )
                    ax.add_patch(forme)
                elif f_config["type"] == "poly":
                    points = [[cx, cy + r], [cx - r, cy - r], [cx + r, cy - r]]
                    forme = patches.Polygon(
                        points, facecolor=f_config["couleur"], edgecolor="#ffffff"
                    )
                    ax.add_patch(forme)
                elif f_config["type"] == "diamond":
                    points = [
                        [cx, cy + r],
                        [cx + r, cy],
                        [cx, cy - r],
                        [cx - r, cy],
                    ]
                    forme = patches.Polygon(
                        points, facecolor=f_config["couleur"], edgecolor="#ffffff"
                    )
                    ax.add_patch(forme)

            if verdict != "":
                couleur_verdict = "#16a34a" if verdict != "PERDU" else "#ef4444"
                ax.text(
                    500,
                    52.5,
                    verdict,
                    color=couleur_verdict,
                    weight="bold",
                    fontsize=11,
                    va="center",
                    ha="center",
                )

            st.pyplot(fig, clear_figure=True)

        # 2. ACTIONNEUR DE TIRAGE (Le levier de la machine)
        if st.button(
            "Actionner le levier de la Slot Machine", key="btn_lancer_casino1"
        ):
            with st.spinner("Verification des alignements de la machine..."):
                import time

                time.sleep(0.5)  # Temporisation web fluide ramenée à 0.5s

                # Tirage aléatoire réel des 3 rouleaux
                v1 = random.randint(1, 4)
                v2 = random.randint(1, 4)
                v3 = random.randint(1, 4)

                # Traitement mathématique du verdict et incrémentation stricte
                if v1 == v2 == v3:
                    verdict = "JACKPOT"
                    st.session_state.cpt_classe_jackpots += 1
                elif v1 == v2 or v2 == v3 or v1 == v3:
                    verdict = "GAGNE"
                    st.session_state.cpt_classe_gagnes += 1
                else:
                    verdict = "PERDU"

                st.session_state.total_lancers_slot += 1

                # Sauvegarde des résultats pour l'affichage persistant après st.rerun
                st.session_state.derniers_rouleaux = (v1, v2, v3, verdict)

                # Ajout d'une ligne horodatée dans le journal d'historique
                num_tour = len(st.session_state.liste_casino_view1) + 1
                st.session_state.liste_casino_view1.insert(
                    0,
                    f"Lancer n°{num_tour:02d} : [{FORMES_CASINO[v1]['nom'][:3]}-{FORMES_CASINO[v2]['nom'][:3]}-{FORMES_CASINO[v3]['nom'][:3]}] -> {verdict}",
                )
                st.rerun()

        # 3. PANNEAU DE RENDU DU RÉSULTAT COURANT
        if "derniers_rouleaux" in st.session_state:
            v1, v2, v3, verdict = st.session_state.derniers_rouleaux
            st.markdown("**Alignement des rouleaux obtenu :**")
            dessiner_machine_casino1(v1, v2, v3, verdict)

        # 4. EXPLOITATION ET AFFICHAGE DES COMPTEURS STATISTIQUES
        total_slot = st.session_state.total_lancers_slot

        if total_slot == 0:
            cpt_jk, cpt_g, cpt_p = 0, 0, 0
            tx_jk, tx_g, tx_p = 0.0, 0.0, 0.0
        else:
            cpt_jk = st.session_state.cpt_classe_jackpots
            cpt_g = st.session_state.cpt_classe_gagnes
            cpt_p = total_slot - (cpt_jk + cpt_g)

            tx_jk = (cpt_jk / total_slot) * 100
            tx_g = (cpt_g / total_slot) * 100
            tx_p = (cpt_p / total_slot) * 100

        st.write("---")
        st.write("### Statistiques cumulées de la machine :")
        st.text(f"Slot Jackpots (3 id.) : {cpt_jk}/{total_slot} ({tx_jk:.1f}%)")
        st.text(f"Slot Gagnes (2 id.)   : {cpt_g}/{total_slot} ({tx_g:.1f}%)")
        st.text(f"Slot Perdus (0 id.)   : {cpt_p}/{total_slot} ({tx_p:.1f}%)")

 
                

    with col3:
        st.markdown("Jeu de dé")
        # =====================================================================
        # 3. STATISTIQUES DYNAMIQUES (Anciennement actualiser_labels_statistiques_de1)
        # =====================================================================
        st.write("---")
        st.write("Statistiques du dé à 6 faces bien équilibré :")

        # 1. BOUTON DE LANCER ET INCRÉMENTATION IMMÉDIATE DU COMPTEUR
        if st.button("Lancer le de libre", key="btn_lancer_de_libre_principal"):
            # Tirage aléatoire de la face (1 à 6)
            valeur_de_actuelle1 = random.randint(1, 6)
            st.session_state.dernier_lancer_de = valeur_de_actuelle1

            # Incrémentation immédiate du compteur de la face obtenue
            st.session_state.stats_par_face_de[valeur_de_actuelle1] += 1
            st.session_state.de_total_lancers += 1

            # Enregistrement dans l'historique global
            st.session_state.historique_logs.append(
                f"Jeu de de : Face {valeur_de_actuelle1} obtenue."
            )

            st.rerun()

        # 2. AFFICHAGE DYNAMIQUE DES STATISTIQUES EN TEMPS RÉEL
        total_lancers_de = st.session_state.get("de_total_lancers", 0)

        # Balayage des 6 faces pour calculer et afficher les pourcentages exacts
        for face in range(1, 7):
            nb_obtenu = st.session_state.stats_par_face_de.get(face, 0)
            pourcentage = (
                (nb_obtenu / total_lancers_de * 100) if total_lancers_de > 0 else 0.0
            )

            # Affichage en violet net conforme à votre thème visuel
            st.markdown(
                f":violet[Face {face} : {nb_obtenu}/{total_lancers_de} ({pourcentage:.1f}%)]"
            )

        # 3. PANNEAU VERT D'AFFICHAGE DU DERNIER LANCER EFFECTUÉ
        if "dernier_lancer_de" in st.session_state:
            st.success(
                f"Le de s'est arrete sur la face : \n\n {st.session_state.dernier_lancer_de}"
            )

    # =============================================================================
    # EXEMPLE D'INTEGRATION DANS L'INTERFACE UTILISATEUR
    # =============================================================================

    # Selecteur de type de jeu pour alimenter la simulation (Aligne tout a gauche)
    st.session_state.choix_jeu_simule = st.radio(
        "Selectionnez le jeu a simuler :",
        options=["De", "Slot", "Roulette"],
        horizontal=True,
        key="radio_choix_jeu_simulation_grands_nombres",
    )

    # Declenchement de la fonction lors du clic sur le bouton (Aligne tout a gauche)
    if st.button(
        "Lancer la simulation des 2000 tirages", key="btn_lancer_sim_2000"
    ):
        executer_simulation_loi_grands_nombres1()


    # =============================================================================
    # 3. PANNEAU D'AFFICHAGE DE L'HISTORIQUE ET DES LOGS
    # =============================================================================
    historique_actuel = st.session_state.get("historique_logs", [])

    # La condition verifie si la liste contient des logs avant d'afficher le panneau
    if historique_actuel:
        st.write("---")
        st.subheader("Historique des lancers")

        # Affichage du journal des evenements sous forme de liste fixe propre
        texte_logs = "\n".join(st.session_state.historique_logs)
        st.code(texte_logs, language="text")    # Récupération sécurisée de la limite de formes (remplace self.slider_shapes_n1.get())
    limit_shapes = int(st.session_state.get("slider_shapes_n1_valeur", 7))


    # -----------------------------------------------------------------
    # 5. PIED DE PAGE : LE BLOC DE CONTRÔLE ET D'EXPORT RAPPORT ATELIER 1
    # -----------------------------------------------------------------
    st.write("---")
    st.subheader("Parametres du Mode Examen")

    # VÉRIFICATION DIRECTE SUR LA MÉMOIRE DE L'ACCUEIL
    identite_invalide_at1 = st.session_state.get("nom_var", "") in ["", "NOM", "ELEVE", "INCONNU"] or not st.session_state.get("verrouille", False)

    if "mode_examen_actif" not in st.session_state:
        st.session_state.mode_examen_actif = False

    if identite_invalide_at1:
        st.checkbox("Activer le Mode Examen", value=False, disabled=True, key="chk_at1_bloq_final_ok")
        st.warning("Action interdite : Veuillez d'abord renseigner votre identite sur l'onglet d'accueil.")
    else:
        def declencher_examen_tab1_local():
            st.session_state.mode_examen_tab1_actif = True
            if "basculer_mode_examen_protection1" in globals():
                basculer_mode_examen_protection1()

        st.checkbox(
            "Mode Examen",
            value=st.session_state.mode_examen_tab1_actif,
            disabled=st.session_state.mode_examen_tab1_actif,
            key="chk_at3_libre_final_ok",
            on_change=declencher_examen_tab1_local,
        )

    st.write("")
    col_btn_valider1, col_btn_exporter1 = st.columns(2)

    with col_btn_valider1:
        if st.button("Valider l'Atelier 1", key="btn_val1_at1_final_ok", disabled=identite_invalide_at1):
            if "valider_tout1" in globals():
                valider_tout1()
            else:
                st.success("Atelier 1 valide avec succes en memoire.")

    with col_btn_exporter1:
        html_data_at1 = "<html><body>Rapport technique de l'Atelier 1 pret.</body></html>"
        if not identite_invalide_at1 and "generer_et_telecharger_rapport1" in globals():
            html_data_at1 = generer_et_telecharger_rapport1()

        st.download_button(
            label="Exporter le rapport HTML",
            data=html_data_at1,
            file_name=f"Rapport_Atelier1_{st.session_state.get('nom_var', 'ELEVE')}.html",
            mime="text/html",
            key="btn_exp1_at1_final_ok",
            disabled=identite_invalide_at1,
        )

    # =====================================================================
    # LIGNE 1486 : LE TITRE DE L'EXERCICE (Revenez bien aligné tout à gauche)
    # =====================================================================

    # Utilisation d'un conteneur avec un style de fond blanc pour rappeler le document d'origine
    with st.container():
        st.markdown(
            """
            <style>
            .zone-cours {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 4px;
                font-family: Arial, sans-serif;
                font-size: 15px;
                line-height: 1.6;
                color: #111827;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        # Afin de garantir une mise en page web stable et l'accessibilité sur mobile, 
        # nous affichons le texte complet avec des repères [Trou X], et plaçons les champs juste en dessous.
        texte_affiche = ""
        for i in range(15):
            texte_affiche += fragments[i] + f" **[Trou {i+1}]** "
        texte_affiche += fragments[15]
        
        st.markdown(f'<div class="zone-cours">{texte_affiche}</div>', unsafe_allow_html=True)

        st.write("---")
        st.subheader("Remplir les trous :")

        # Création de 3 colonnes pour aligner les 15 champs de saisie proprement
        col1, col2, col3 = st.columns(3)

        for i in range(15):
            # Répartition des 15 trous dans les 3 colonnes
            if i % 3 == 0:
                with col1:
                    st.session_state.reponses_trous[i] = st.text_input(f"Trou {i+1} :", key=f"trou_{i}")
            elif i % 3 == 1:
                with col2:
                    st.session_state.reponses_trous[i] = st.text_input(f"Trou {i+1} :", key=f"trou_{i}")
            else:
                with col3:
                    st.session_state.reponses_trous[i] = st.text_input(f"Trou {i+1} :", key=f"trou_{i}")


    # =====================================================================
    # BOUTON DE VALIDATION ET STRATÉGIE (Anciennement valider_texte_a_trous1)
    # =====================================================================
    st.write("---")

    if st.button("Valider le texte a trous", key="btn_valider_trous1"):
        sans_faute = True
        cpt_correct = 0
        
        # Vérification stricte des réponses (insensible à la casse et aux espaces superflus)
        for i in range(15):
            reponse_user = st.session_state.reponses_trous[i].strip().lower()
            solution = solutions_trous1[i].lower()
            
            if reponse_user == solution:
                cpt_correct += 1
            else:
                sans_faute = False
                
        # Affichage du résultat (Remplace result_trous_label1)
        if sans_faute:
            st.success(f"Bravo ! Tout est correct : {cpt_correct}/15")
        else:
            st.error(f"Score : {cpt_correct}/15. Verifiez vos reponses et réessayez.")

    # =====================================================================
    # 2. CONFIGURATION ET AFFICHAGE DU QUIZ (Anciennement setup_quiz1)
    # =====================================================================

    # Récupération dynamique des paramètres des curseurs (variables de session)
    n_faces_de = int(st.session_state.get("slider_faces_n1_valeur", 6))
    n_formes_slot = int(st.session_state.get("slider_shapes_n1_valeur", 7))

    # Initialisation et stabilisation du Quiz en mémoire de session
    if "quiz1_data" not in st.session_state:
        base_questions = [
            {"q": f"Sur le De Libre regle a n = {n_faces_de} faces, quelle est la probabilite d'obtenir la face 1 ?", "options": [f"1 / {n_faces_de}", "1 / 2", "0"], "rep": f"1 / {n_faces_de}"},
            {"q": f"Sur ce meme De Libre a n = {n_faces_de} faces, quelle est la probabilite d'obtenir un nombre strictement superieur a {n_faces_de} ?", "options": ["0 (Evenement impossible)", "1 (Evenement certain)", "0.5"], "rep": "0 (Evenement impossible)"},
            {"q": f"Dans la Slot Machine a {n_formes_slot} formes, combien y a-t-il de combinaisons totales possibles au total ?", "options": [f"{n_formes_slot}^3 = {n_formes_slot**3}", f"{n_formes_slot}^2 = {n_formes_slot**2}", "30"], "rep": f"{n_formes_slot}^3 = {n_formes_slot**3}"},
            {"q": f"Quelle est la probabilite exacte d'obtenir un JACKPOT (3 formes identiques) sur cette machine a {n_formes_slot} formes ?", "options": [f"1 / {n_formes_slot**2}", f"1 / {n_formes_slot**3}", f"3 / {n_formes_slot}"], "rep": f"1 / {n_formes_slot**2}"},
            {"q": "Combien de numeros au total contient la Roulette Europeenne officielle dessinee sur le tapis ?", "options": ["37 numeros (de 0 a 36)", "36 numeros (de 1 a 36)", "38 numeros"], "rep": "37 numeros (de 0 a 36)"},
            {"q": "Quelle est la probabilite theorique stricte de deviner un Numero Plein precis sur cette roulette ?", "options": ["1 / 37", "1 / 36", "18 / 37"], "rep": "1 / 37"},
            {"q": "Combien de cases Rouges contient la couronne de la roulette officielle de casino ?", "options": ["18 cases", "19 cases", "17 cases"], "rep": "18 cases"},
            {"q": "Quelle est la probabilite exacte de gagner en misant sur une Chance Simple (ex: ROUGE ou EVEN) ?", "options": ["18 / 37 (environ 48.6%)", "18 / 36 (50.0%)", "1 / 2"], "rep": "18 / 37 (environ 48.6%)"},
            {"q": "Pourquoi la probabilite d'une couleur n'est-elle pas exactement de 50% a la roulette ?", "options": ["A cause de la case 0 verte (avantage banque)", "Parce qu'il y a plus de noirs", "C'est un bug"], "rep": "A cause de la case 0 verte (avantage banque)"},
            {"q": "Quelle est la probabilite theorique de gagner en placant son jeton dore sur le bloc '1st 12' (premiere douzaine) ?", "options": ["12 / 37", "12 / 36", "1 / 3"], "rep": "12 / 37"}
        ]
        
        # Mélange initial des questions
        random.shuffle(base_questions)
        
        # Mélange initial des options pour chaque question
        for item in base_questions:
            random.shuffle(item["options"])
            
        st.session_state.quiz1_data = base_questions
        st.session_state.reponses_quiz = {idx: "" for idx in range(10)}

    # Rendu de la grille des 10 questions du Quiz
    for idx, item in enumerate(st.session_state.quiz1_data):
        st.markdown(f"** :** {item['q']}")
        
        # Remplacement du ttk.Combobox par un st.selectbox natif
        choix_user = st.selectbox(
            "Selectionnez votre reponse :",
            options=[""] + item["options"], # Ajout d'un choix vide par défaut
            key=f"quiz_select_{idx}"
        )
        st.session_state.reponses_quiz[idx] = choix_user
        st.write("")

    # Bouton de validation du Quiz
    if st.button("Valider les reponses du Quiz", key="btn_valider_quiz1"):
        score_quiz = 0
        st.write("---")
        st.subheader("Correction du Quiz")

        for idx, item in enumerate(st.session_state.quiz1_data):
            user_rep = st.session_state.reponses_quiz[idx]
            correct_rep = item["rep"]

            if user_rep == correct_rep:
                score_quiz += 1
                # CORRECTION ABSOLUE : Les accolades vides parasites ont été supprimées
                st.markdown(
                    f'<p style="color:#16a34a; margin:2px 0px; font-weight:bold;">Correct</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<p style="color:#dc2626; margin:2px 0px; font-weight:bold;">Erreur (Votre choix : "{user_rep}" | Reponse attendue : "{correct_rep}")</p>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            f"<h3>Note du Quiz : {score_quiz} / 10</h3>", unsafe_allow_html=True
        )          
        st.markdown(f'<h3>Note du Quiz : {score_quiz} / 10</h3>', unsafe_allow_html=True)


def reinitialiser():
    st.session_state.entries_tab3 = {(i, j): "" for i in range(3) for j in range(3)}
    st.session_state.tableau_corrige = False
    st.session_state.cases_initiales = []
    st.session_state.solution_courante = {}
    st.session_state.texte_enonce_dynamique = "Sélectionnez une filière ci-dessus puis cliquez sur 'Générer un exercice'."

def generer_exercice_filiere():
    """Génère l'énoncé de l'exercice, laisse le tableau vide et actualise le QCM."""
    import random
    import streamlit as st

    # 1. Appel de la méthode de réinitialisation locale
    if "reinitialiser" in globals():
        reinitialiser()

    contextes = {
        "Conducteur Routier": {
            "A": "le camion roule a l'Euro 6 (eco)",
            "B": "le trajet est regional",
            "phrase_A": "le camion soit un vehicule Euro 6",
            "phrase_B": "le trajet soit regional",
        },
        "Maintenance des Véhicules": {
            "A": "la panne est d'origine electrique",
            "B": "le vehicule est un utilitaire leger",
            "phrase_A": "la panne soit d'origine electrique",
            "phrase_B": "le vehicule soit un utilitaire leger",
        },
        "Travaux Publics (TP)": {
            "A": "le chantier utilise une pelle hydraulique",
            "B": "le sol est rocheux",
            "phrase_A": "le chantier utilise une pelle hydraulique",
            "phrase_B": "le sol soit rocheux",
        },
    }

    # Récupération de la filière sélectionnée depuis la session
    filiere_choisie = st.session_state.get("var_filiere", "Conducteur Routier")

    # Sécurité au cas où la clé de filière d'examen contiendrait une variante de texte
    if filiere_choisie not in contextes:
        filiere_choisie = "Conducteur Routier"

    ctx = contextes[filiere_choisie]

    # Génération de probabilités cohérentes pour la matrice de solution
    p_A_et_B = round(random.uniform(0.15, 0.30), 2)
    p_A_et_Bbar = round(random.uniform(0.20, 0.35), 2)
    p_Abar_et_B = round(random.uniform(0.15, 0.25), 2)

    p_A = round(p_A_et_B + p_A_et_Bbar, 2)
    p_B = round(p_A_et_B + p_Abar_et_B, 2)
    p_Abar = round(1.00 - p_A, 2)
    p_Bbar = round(1.00 - p_B, 2)
    p_Abar_et_Bbar = round(p_Bbar - p_A_et_Bbar, 2)

    # Sauvegarde technique pour la correction finale (QCM + Tableau)
    st.session_state.solution_courante = {
        (0, 0): p_A_et_B,
        (0, 1): p_Abar_et_B,
        (0, 2): p_B,
        (1, 0): p_A_et_Bbar,
        (1, 1): p_Abar_et_Bbar,
        (1, 2): p_Bbar,
        (2, 0): p_A,
        (2, 1): p_Abar,
        (2, 2): 1.00,
    }

    # IMPORTANT : On ne met aucune valeur initiale pour laisser la grille vide
    st.session_state.cases_initiales = []

    # Nettoyage des anciens composants de saisie pour le nouveau tirage
    cases_tableau = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)]
    for i, j in cases_tableau:
        st.session_state[f"cell_tab3_{i}_{j}"] = ""

    scenario = random.randint(1, 5)

    if scenario == 1:
        texte_donnees = (
            f"- La probabilite de l'intersection P(A \u2229 B) est de {p_A_et_B:.2f}.\n"
            f"- La probabilite globale P(B) est de {p_B:.2f}.\n"
            f"- La probabilite globale P(A) est de {p_A:.2f}."
        )
    elif scenario == 2:
        texte_donnees = (
            f"- La probabilite de l'intersection P(A \u2229 B\u0305) est de {p_A_et_Bbar:.2f}.\n"
            f"- La probabilite globale P(A) est de {p_A:.2f}.\n"
            f"- La probabilite globale P(B\u0305) est de {p_Bbar:.2f}."
        )
    elif scenario == 3:
        texte_donnees = (
            f"- La probabilite de l'intersection P(A\u0305 \u2229 B\u0305) est de {p_Abar_et_Bbar:.2f}.\n"
            f"- La probabilite globale P(A) est de {p_A:.2f}.\n"
            f"- La probabilite globale P(B) est de {p_B:.2f}."
        )
    elif scenario == 4:
        texte_donnees = (
            f"- La probabilite de l'intersection P(A\u0305 \u2229 B) est de {p_Abar_et_B:.2f}.\n"
            f"- La probabilite globale P(A\u0305) est de {p_Abar:.2f}.\n"
            f"- La probabilite globale P(B) est de {p_B:.2f}."
        )
    else:
        texte_donnees = (
            f"- La probabilite de l'intersection P(A \u2229 B) est de {p_A_et_B:.2f}.\n"
            f"- La probabilite de l'intersection P(A\u0305 \u2229 B) est de {p_Abar_et_B:.2f}.\n"
            f"- La probabilite globale P(B\u0305) est de {p_Bbar:.2f}."
        )

    # Rédaction dynamique de l'énoncé final
    texte_final = (
        f"**[Enonce Filiere : {filiere_choisie}]**\n\n"
        f"Soit l'evenement A : \"{ctx['A']}\" et l'evenement B : \"{ctx['B']}\".\n\n"
        f"Les enregistrements indiquent que :\n"
        f"{texte_donnees}\n\n"
        f"Exercice : Utilisez ces 3 valeurs pour completer la grille, le texte a trous et le quiz."
    )

    st.session_state.texte_enonce_dynamique = texte_final
    st.session_state.tableau_deja_corrige = False

    # Nettoyage de l'ancien QCM pour forcer son renouvellement avec les nouvelles valeurs
    if "quiz3_data" in st.session_state:
        del st.session_state.quiz3_data

    st.rerun()
    


def setup_quiz3():
    """Génère la grille d'évaluation de 10 questions sur les probabilités

    du tableau de contingence de l'Atelier 3.
    """
    import random
    import streamlit as st

    st.markdown("#### Questionnaire de fractions et probabilités (QCM)")

    # 1. Extraction sécurisée des probabilités de l'exercice courant
    sol = st.session_state.get("solution_courante", None)
    if sol and len(sol) >= 8:
        p_A_et_B = sol.get((0, 0), 0.20)
        p_Abar_et_B = sol.get((0, 1), 0.22)
        p_B = sol.get((0, 2), 0.42)
        p_A_et_Bbar = sol.get((1, 0), 0.23)
        p_Abar_et_Bbar = sol.get((1, 1), 0.35)
        p_Bbar = sol.get((1, 2), 0.58)
        p_A = sol.get((2, 0), 0.43)
        p_Abar = sol.get((2, 1), 0.57)
    else:
        # Valeurs de secours cohérentes avant le tout premier clic de l'élève
        p_A_et_B, p_Abar_et_B, p_B = 0.20, 0.22, 0.42
        p_A_et_Bbar, p_Abar_et_Bbar, p_Bbar = 0.23, 0.35, 0.58
        p_A, p_Abar = 0.43, 0.57

    # Calcul dynamique des probabilités d'unions via la formule P(A) + P(B) - P(A ∩ B)
    p_A_ou_B = round(p_A + p_B - p_A_et_B, 2)
    p_Abar_ou_B = round(p_Abar + p_B - p_Abar_et_B, 2)

    # 2. Stabilisation en mémoire de session de la banque de 10 questions
    if "quiz3_data" not in st.session_state:
        base_questions3 = [
            {"q": "Quelle est la valeur lue ou calculée pour P(A) ?", "options": [f"{p_A:.2f}", f"{p_Abar:.2f}", f"{p_B:.2f}", "1.00"], "rep": f"{p_A:.2f}"},
            {"q": "Quelle est la valeur de la probabilité de l'événement contraire P(A̅) ?", "options": [f"{p_Abar:.2f}", f"{p_A:.2f}", f"{p_Bbar:.2f}", "0.00"], "rep": f"{p_Abar:.2f}"},
            {"q": "Quelle est la valeur de la probabilité globale P(B) ?", "options": [f"{p_B:.2f}", f"{p_Bbar:.2f}", f"{p_A_et_B:.2f}", "1.00"], "rep": f"{p_B:.2f}"},
            {"q": "Quelle est la valeur de la probabilité de l'événement contraire P(B̅) ?", "options": [f"{p_Bbar:.2f}", f"{p_B:.2f}", f"{p_Abar:.2f}", "0.50"], "rep": f"{p_Bbar:.2f}"},
            {"q": "Quelle est la valeur de la probabilité de l'intersection P(A ∩ B) ?", "options": [f"{p_A_et_B:.2f}", f"{p_A_ou_B:.2f}", f"{p_Abar_et_B:.2f}", "0.00"], "rep": f"{p_A_et_B:.2f}"},
            {"q": "Quelle est la valeur calculée pour l'intersection P(A ∩ B̅) ?", "options": [f"{p_A_et_Bbar:.2f}", f"{p_A_et_B:.2f}", f"{p_Abar_et_Bbar:.2f}", f"{p_A:.2f}"], "rep": f"{p_A_et_Bbar:.2f}"},
            {"q": "Quelle est la valeur calculée pour l'intersection P(A̅ ∩ B) ?", "options": [f"{p_Abar_et_B:.2f}", f"{p_A_et_B:.2f}", f"{p_B:.2f}", f"{p_Abar_et_Bbar:.2f}"], "rep": f"{p_Abar_et_B:.2f}"},
            {"q": "Quelle est la valeur calculée pour l'intersection P(A̅ ∩ B̅) ?", "options": [f"{p_Abar_et_Bbar:.2f}", f"{p_A_et_Bbar:.2f}", f"{p_Abar:.2f}", "0.10"], "rep": f"{p_Abar_et_Bbar:.2f}"},
            {"q": "Calculez la probabilité de l'union P(A ∪ B) via la formule P(A) + P(B) - P(A ∩ B) :", "options": [f"{p_A_ou_B:.2f}", f"{p_A_et_B:.2f}", "1.00", f"{round(p_A + p_B, 2):.2f}"], "rep": f"{p_A_ou_B:.2f}"},
            {"q": "Calculez la probabilité de l'union P(A̅ ∪ B) via la formule P(A̅) + P(B) - P(A̅ ∩ B) :", "options": [f"{p_Abar_ou_B:.2f}", f"{p_Abar_et_B:.2f}", f"{p_Bbar:.2f}", f"{p_Abar:.2f}"], "rep": f"{p_Abar_ou_B:.2f}"}
        ]
        
        # Mélange unique de l'ordre des questions et des options au chargement initial
        random.shuffle(base_questions3)
        for item in base_questions3:
            random.shuffle(item["options"])
            
        st.session_state.quiz3_data = base_questions3

    # 3. Rendu visuel stable de la grille des 10 questions du QCM
    for idx, item in enumerate(st.session_state.quiz3_data):
        st.markdown(f"**Question {idx+1} :** {item['q']}")
        
        cle_composant = f"quiz3_select_{idx}"
        valeur_precedente = str(st.session_state.get(cle_composant, "")).strip()
        
        liste_options = [""] + item["options"]
        index_defaut = liste_options.index(valeur_precedente) if valeur_precedente in liste_options else 0

        # CORRECTION SYNTAXIQUE ABSOLUE : Parenthèse proprement refermée avec clé valide
        st.selectbox(
            label=f"Label_Q3_{idx}",
            options=liste_options,
            index=index_defaut,
            disabled=st.session_state.get("tableau_deja_corrige", False),
            label_visibility="collapsed",
            key=cle_composant
        )

def setup_texte_a_trous3():
    """Génère l'exercice de synthèse textuelle à 10 trous pour l'Atelier 3

    conforme à la structure probabiliste du tableau de contingence.
    """
    import streamlit as st

    st.markdown("#### Synthèse de cours à trous")

    # 1. Conservation de la liste ordonnée des 10 mots attendus pour l'export HTML final
    if "solutions_trous3" not in st.session_state:
        st.session_state.solutions_trous3 = [
            "contingence",
            "double",
            "intersection",
            "globales",
            "somme",
            "coherentes",
            "deduire",
            "completer",
            "vert",
            "rouge",
        ]

    fragments = [
        "Pour croiser les donnees des filieres (Routier, Maintenance, TP), on utilise un tableau de ",
        " a ",
        " entree. Chaque case centrale donne la probabilite de l' ",
        " de deux evenements. Les lignes et colonnes de fin indiquent les probabilites ",
        ", tandis que la cellule finale en bas a droite vaut toujours 1, representant la ",
        " totale. L'enonce genere des valeurs mathematiquement ",
        " qui permettent de ",
        " le reste des donnees manquantes. Pour verifier ses calculs, l'eleve clique sur le bouton pour ",
        " la grille. Les bonnes reponses s'affichent alors en ",
        " et les erreurs sont barrees puis affichees en ",
    ]

    # 2. Construction dynamique du paragraphe de cours avec repères visuels
    texte_paragraphe = ""
    for i in range(10):
        texte_paragraphe += fragments[i] + f" **[Trou {i+1}]** "
    texte_paragraphe += " pour guider la correction."

    # Affichage du cours sous forme de feuille blanche stylisée
    st.markdown(
        f"""
        <div style="background-color: #ffffff; color: #1e293b; padding: 15px; 
                    border-radius: 6px; border: 1px solid #cbd5e1; font-family: Arial; 
                    font-size: 13.5px; line-height: 1.6; margin-bottom: 20px;">
            {texte_paragraphe}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Rendu de la grille des 10 champs de saisie pour combler les trous textuels
    st.markdown("**Remplir les zones de texte :**")
    col_t3_1, col_t3_2 = st.columns(2)

    for i in range(10):
        cle_trou = f"trou3_{i}"
        valeur_trou_precedente = str(st.session_state.get(cle_trou, "")).strip()

        if i < 5:
            with col_t3_1:
                st.text_input(
                    f"Trou {i+1} :",
                    value=valeur_trou_precedente,
                    key=cle_trou,
                    disabled=st.session_state.get("tableau_deja_corrige", False),
                )
                # AFFICHAGE DE LA CORRECTION : On affiche la correction en dessous si elle existe
                if st.session_state.get("tableau_deja_corrige", False):
                    txt_corr = st.session_state.corrections_visuelles_trous3.get(i, "")
                    if txt_corr == "Correct":
                        st.markdown(f'<p style="color:#16a34a; font-size:12px; font-weight:bold; margin:-10px 0 10px 5px;">Correct</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p style="color:#dc2626; font-size:12px; font-weight:bold; margin:-10px 0 10px 5px;">{txt_corr}</p>', unsafe_allow_html=True)
        else:
            with col_t3_2:
                st.text_input(
                    f"Trou {i+1} :",
                    value=valeur_trou_precedente,
                    key=cle_trou,
                    disabled=st.session_state.get("tableau_deja_corrige", False),
                )
                # AFFICHAGE DE LA CORRECTION : On affiche la correction en dessous si elle existe
                if st.session_state.get("tableau_deja_corrige", False):
                    txt_corr = st.session_state.corrections_visuelles_trous3.get(i, "")
                    if txt_corr == "Correct":
                        st.markdown(f'<p style="color:#16a34a; font-size:12px; font-weight:bold; margin:-10px 0 10px 5px;">Correct</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p style="color:#dc2626; font-size:12px; font-weight:bold; margin:-10px 0 10px 5px;">{txt_corr}</p>', unsafe_allow_html=True)

def corriger_seul_tableau3():
    """Compare les saisies numériques de la grille de contingence avec les solutions

    et attribue une note sur 10 points pour l'Atelier 3.
    """
    import streamlit as st

    # 1. Vérification préventive pour éviter les erreurs de NameError ou KeyError
    if "solution_courante" not in st.session_state:
        st.error(
            "Erreur : Aucun exercice n'a ete genere. Veuillez cliquer sur 'Generer un exercice'."
        )
        return

    solution_courante = st.session_state.solution_courante
    cases_tableau = [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
    ]

    score_tableau = 0.0
    # Le tableau de filière génère une grille entièrement vide (8 cases à calculer)
    cases_calculees_eleve = 8

    # Barème d'attribution proportionnel (10 points répartis sur les 8 cases)
    valeur_par_case = 10.0 / cases_calculees_eleve

    # 2. Vérification chirurgicale de chaque cellule remplie par l'étudiant
    for i, j in cases_tableau:
        # Lecture dynamique de la clé du composant st.text_input de la grille
        cle_composant = f"cell_tab3_{i}_{j}"
        val_saisie_brute = (
            str(st.session_state.get(cle_composant, ""))
            .strip()
            .replace(",", ".")
        )

        val_attendue = solution_courante[(i, j)]

        try:
            val_saisie_float = float(val_saisie_brute)
            # Tolérance d'arrondi standard de 0.01 pour les probabilités décimales
            if abs(val_saisie_float - val_attendue) < 0.01:
                score_tableau += valeur_par_case
        except ValueError:
            pass  # Case restée vide ou texte non numérique saisi par l'élève

    # 3. Enregistrement de la note finale et marquage des indicateurs de rendu
    st.session_state.note_tableau_contingence = round(score_tableau)
    st.session_state.tableau_deja_corrige = True
    st.session_state.tableau_corrige = True

    st.rerun()

def valider_tout3():
    """Valide definitivement l'Atelier 3 en corrigeant simultanement

    le tableau de contingence, le QCM et le texte a trous de maniere stable.
    """
    import streamlit as st

    nom_eleve = str(st.session_state.get("nom_var", "")).strip().upper()
    classe_eleve = str(st.session_state.get("classe_var", "")).strip().upper()

    if nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]:
        st.error(
            "Action interdite : Veuillez d'abord renseigner et VALIDER votre identite sur l'onglet d'accueil."
        )
        return

    if "solution_courante" not in st.session_state:
        st.error(
            "Erreur : Aucun exercice actif n'a ete trouve. Veuillez generer un exercice."
        )
        return

    solution_courante = st.session_state.solution_courante
    quiz3_data = st.session_state.get("quiz3_data", [])
    solutions_trous3 = st.session_state.get(
        "solutions_trous3",
        [
            "contingence",
            "double",
            "intersection",
            "globales",
            "somme",
            "coherentes",
            "deduire",
            "completer",
            "vert",
            "rouge",
        ],
    )

    # Initialisation preventive du dictionnaire des corrections visuelles
    st.session_state.corrections_visuelles_trous3 = {}

    # =========================================================================
    # 2. CORRECTION DU TEXTE À TROUS (10 TROUS - SECURISEE SANS RE-ECRITURE SUR KEY)
    # =========================================================================
    score_trous = 0
    for idx, reponse_attendue in enumerate(solutions_trous3):
        cle_trou = f"trou3_{idx}"
        reponse_eleve = (
            str(st.session_state.get(cle_trou, "")).strip().lower()
        )

        if reponse_eleve == reponse_attendue.lower():
            score_trous += 1
            st.session_state.corrections_visuelles_trous3[idx] = "Correct"
        else:
            texte_incorrect = reponse_eleve if reponse_eleve != "" else "?"
            texte_barre = "".join([c + "\u0336" for c in texte_incorrect])
            # CORRECTIF : On stocke l'affichage dans un dictionnaire distinct pour couper l'erreur de duplication
            st.session_state.corrections_visuelles_trous3[idx] = (
                f"{texte_barre} -> {reponse_attendue}"
            )

    # =========================================================================
    # 3. CORRECTION DU QCM (10 QUESTIONS - SUR 10 POINTS)
    # =========================================================================
    score_qcm = 0
    valeur_par_qcm = 10.0 / max(1, len(quiz3_data))

    for idx, item in enumerate(quiz3_data):
        cle_quiz = f"quiz3_select_{idx}"
        reponse_eleve = str(st.session_state.get(cle_quiz, "")).strip()
        reponse_attendue = item["rep"].strip()

        if reponse_eleve == reponse_attendue and reponse_eleve != "":
            score_qcm += valeur_par_qcm

    note_qcm_finale = round(score_qcm)

    # =========================================================================
    # 4. CORRECTION DU TABLEAU DE CONTINGENCE (8 CASES - SUR 10 POINTS)
    # =========================================================================
    score_tableau_tk = 0.0
    cases_tableau = [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
    ]

    for i, j in cases_tableau:
        cle_cellule = f"cell_tab3_{i}_{j}"
        val_saisie_str = (
            str(st.session_state.get(cle_cellule, ""))
            .strip()
            .replace(",", ".")
        )
        val_attendue = solution_courante.get((i, j), 0.0)

        try:
            if val_saisie_str != "":
                val_saisie = float(val_saisie_str)
                if abs(val_saisie - val_attendue) < 0.01:
                    score_tableau_tk += 1.25
        except ValueError:
            pass

    note_tableau_finale = round(score_tableau_tk)

    # =========================================================================
    # 5. CONSOLIDATION ET RENDU DU BILAN TEXTUEL
    # =========================================================================
    score_total_30 = note_tableau_finale + score_trous + note_qcm_finale

    st.session_state.note_tableau_contingence = note_tableau_finale
    st.session_state.tableau_deja_corrige = True
    st.session_state.tableau_corrige = True

    st.session_state.texte_affichage_final_evaluation = (
        f"Nom : {nom_eleve} | "
        f"Tableau : {note_tableau_finale}/10 | "
        f"Texte a trous : {score_trous}/10 | "
        f"QCM : {note_qcm_finale}/10 | "
        f"Note Globale : {score_total_30}/30"
    )

    st.rerun()
    
with tab3:
    # 1. INITIALISATION SÉCURISÉE DES VARIABLES DE SESSION DE L'ATELIER 3
    # Placé au tout début pour éviter les plantages de clés manquantes
    if "mode_examen_tab3_actif" not in st.session_state:
        st.session_state.mode_examen_tab3_actif = False
    if "var_filiere" not in st.session_state:
        st.session_state.var_filiere = "Conducteur Routier"
    if "cases_initiales" not in st.session_state:
        st.session_state.cases_initiales = []
    if "solution_courante" not in st.session_state:
        st.session_state.solution_courante = {}
    if "entries_tab3" not in st.session_state:
        st.session_state.entries_tab3 = {(i, j): "" for i in range(3) for j in range(3)}
    if "tableau_corrige" not in st.session_state:
        st.session_state.tableau_corrige = False
    if "tableau_deja_corrige" not in st.session_state:
        st.session_state.tableau_deja_corrige = False

    # 2. RENDU DU TITRE GÉNÉRAL DU CALCULATEUR (Occupant toute la largeur du haut)
    st.markdown('<h1 style="color:#1e3a8a; font-family:Arial; font-weight:bold; margin-bottom: 25px;">Calculateur de Tableau de Contingence (Probabilités)</h1>', unsafe_allow_html=True)
    if not st.session_state.get("verrouille", False):
        st.warning(
            "Accès restreint : Veuillez d'abord renseigner votre identité et cliquer sur OK dans l'onglet 'Identification'."
        )
        # On arrête la lecture de cet onglet ici tant que l'élève n'est pas identifié
        st.stop()
    # 3. DISTRIBUTION PROPRE DE LA MISE EN PAGE WEB (1/3 à gauche, 2/3 à droite)
    col_gauche_config, col_droite_tableau = st.columns([1, 2])

    with col_gauche_config:
        st.subheader("Configuration de l'exercice")

        # Sélection et sécurisation de la filière métier
        filiere_actuelle = st.session_state.get("var_filiere", "Conducteur Routier")
        liste_options = ["Conducteur Routier", "Maintenance des Véhicules", "Travaux Publics (TP)"]

        if filiere_actuelle not in liste_options:
            filiere_actuelle = "Conducteur Routier"

        filiere_choisie = st.selectbox(
            "Choisir la filiere :",
            options=liste_options,
            index=liste_options.index(filiere_actuelle),
            key="select_filiere_tab3_final",
            disabled=st.session_state.get("mode_examen_tab3_actif", False)
        )
        st.session_state.var_filiere = filiere_choisie

        st.write("")

        # 4. ALIGNEMENT DES BOUTONS DE CONTRÔLE INTERACTIFS (Placés idéalement sous la liste)
        col_bouton_g1, col_bouton_g2 = st.columns(2)

        with col_bouton_g1:
            if st.button(
                "Générer un exercice", key="btn_at3_generer_filiere_gauche_final"
            ):
                generer_exercice_filiere()

        with col_bouton_g2:
            if st.button(
                "Corriger le tableau", key="btn_at3_corriger_seul_gauche_final"
            ):
                corriger_seul_tableau3()

        st.write("")

        # 3. ZONE D'AFFICHAGE DE L'ÉNONCÉ DYNAMIQUE (ENCADRÉ INTERACTIF)
        texte_enonce = st.session_state.get(
            "texte_enonce_dynamique",
            "Sélectionnez une filière ci-dessus puis cliquez sur 'Générer un exercice'.",
        )
        st.markdown(
            f"""
            <div style="background-color:#f0f4f8; color:#334155; padding:15px; 
                        border:1px solid #cbd5e1; border-radius:4px; font-family:Arial; 
                        font-style:italic; font-size:14px; line-height:1.5; margin-bottom:15px;">
                {texte_enonce}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4. PANNEAU DE RENDU DE LA NOTE GLOBALISÉE DU TABLEAU DE CONTINGENCE
        if st.session_state.get("tableau_deja_corrige", False):
            note_tab = st.session_state.get("note_tableau_contingence", 0)
            if note_tab >= 5:
                st.success(
                    f"Correction effectuee ! Note obtenue : {note_tab} / 10"
                )
            else:
                st.error(
                    f"Correction effectuee ! Note obtenue : {note_tab} / 10. Relisez les indices."
                )

    with col_droite_tableau:
        st.subheader("Grille de contingence")

        labels_h = ["A", "A̅", "Total"]
        labels_v = ["B", "B̅", "Total"]

        # 1. Construction des en-têtes horizontaux
        cols_h = st.columns(4)
        with cols_h[0]:
            st.write("")
        for j, text in enumerate(labels_h):
            with cols_h[j + 1]:
                weight = "bold" if text == "Total" else "normal"
                st.markdown(
                    f'<p style="font-family:Times New Roman; font-size:18px; font-style:italic; font-weight:{weight}; text-align:center; margin:0;">{text}</p>',
                    unsafe_allow_html=True,
                )

        # 2. Construction dynamique des cellules de données (4 colonnes x 3 lignes)
        for i in range(3):
            cols_v = st.columns(4)
            text_v = labels_v[i]

            with cols_v[0]:
                weight = "bold" if text_v == "Total" else "normal"
                st.markdown(
                    f'<p style="font-family:Times New Roman; font-size:18px; font-style:italic; font-weight:{weight}; text-align:left; line-height:42px; margin:0;">{text_v}</p>',
                    unsafe_allow_html=True,
                )

            for j in range(3):
                with cols_v[j + 1]:
                    if i == 2 and j == 2:
                        # La case Total Général vaut toujours 1 et reste figée au format feutre
                        st.markdown(
                            '<div style="background-color:#e5e7eb; border:1px solid #cbd5e1; border-radius:4px; text-align:center; font-family:Arial; font-size:18px; font-weight:bold; height:42px; line-height:40px; color:#111827;">1</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        cell_key = (i, j)
                        cle_globale_session = f"cell_tab3_{i}_{j}"

                        # Récupération de la valeur stable (Zéro chaîne par défaut si vide)
                        valeur_initiale_affichage = str(
                            st.session_state.get(cle_globale_session, "")
                        ).strip()

                        # Détermination des droits de saisie de l'étudiant
                        cases_initiales = st.session_state.get(
                            "cases_initiales", []
                        )
                        est_initiale = cell_key in cases_initiales
                        tableau_deja_corrige = st.session_state.get(
                            "tableau_deja_corrige", False
                        )

                        # Génération du composant d'entrée numérique natif et persistant
                        val_saisie = st.text_input(
                            label=f"Input_At3_{i}_{j}",
                            value=valeur_initiale_affichage,
                            disabled=est_initiale or tableau_deja_corrige,
                            label_visibility="collapsed",
                            key=cle_globale_session,
                        )

                        # 3. MOTEUR DE CORRECTION EN CASCADE SOUS CHAQUE CASE
                        if tableau_deja_corrige and not est_initiale:
                            val_saisie_clean = val_saisie.strip().replace(
                                ",", "."
                            )
                            val_attendue = (
                                st.session_state.solution_courante.get(
                                    cell_key, 0.0
                                )
                            )

                            try:
                                if val_saisie_clean != "":
                                    val_num = float(val_saisie_clean)
                                    # Tolérance d'écart de 0.01 pour valider la décimale
                                    if abs(val_num - val_attendue) < 0.01:
                                        st.markdown(
                                            f'<p style="color:#16a34a; font-family:Arial; font-size:11px; font-weight:bold; margin:2px 0 0 0; text-align:center;">Correct</p>',
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        texte_barre = "".join(
                                            [c + "\u0336" for c in val_saisie_clean]
                                        )
                                        st.markdown(
                                            f'<p style="color:#dc2626; font-family:Arial; font-size:11px; font-weight:bold; margin:2px 0 0 0; text-align:center;">{texte_barre} -> {val_attendue:.2f}</p>',
                                            unsafe_allow_html=True,
                                        )
                                else:
                                    st.markdown(
                                        f'<p style="color:#dc2626; font-family:Arial; font-size:11px; font-weight:bold; margin:2px 0 0 0; text-align:center;">Vide -> {val_attendue:.2f}</p>',
                                        unsafe_allow_html=True,
                                    )
                            except ValueError:
                                st.markdown(
                                    f'<p style="color:#dc2626; font-family:Arial; font-size:11px; font-weight:bold; margin:2px 0 0 0; text-align:center;">Erreur -> {val_attendue:.2f}</p>',
                                    unsafe_allow_html=True,
                                )

    # -----------------------------------------------------------------
    # 5. PIED DE PAGE : LE BLOC DE CONTRÔLE ET D'EXPORT RAPPORT ATELIER 3
    # -----------------------------------------------------------------
    st.write("---")
    st.subheader("Controle Examen Final")

    # VÉRIFICATION DIRECTE SUR LA MÉMOIRE DE L'ACCUEIL
    identite_invalide_at3 = st.session_state.get("nom_var", "") in ["", "NOM", "ELEVE", "INCONNU"] or not st.session_state.get("verrouille", False)

    if "mode_examen_tab3_actif" not in st.session_state:
        st.session_state.mode_examen_tab3_actif = False

    if identite_invalide_at3:
        st.checkbox("Mode Examen", value=False, disabled=True, key="chk_at3_bloq_final_ok")
        st.warning("Action interdite : Veuillez d'abord renseigner votre identite sur l'onglet d'accueil.")
    else:
        def declencher_examen_tab3_local():
            st.session_state.mode_examen_tab3_actif = True
            if "basculer_mode_examen_protection3" in globals():
                basculer_mode_examen_protection3()

        st.checkbox(
            "Mode Examen",
            value=st.session_state.mode_examen_tab3_actif,
            disabled=st.session_state.mode_examen_tab3_actif,
            key="chk_at3_libre_final_ok",
            on_change=declencher_examen_tab3_local,
        )

    st.write("")
    col_btn_valider3, col_btn_exporter3 = st.columns(2)

    with col_btn_valider3:
        if st.button("Valider l'Atelier", key="btn_val3_at3_final_ok", disabled=identite_invalide_at3):
            if "valider_tout3" in globals():
                valider_tout3()
            else:
                st.success("Atelier 3 valide avec succes.")

    with col_btn_exporter3:
        html_data_at3 = "<html><body>Rapport technique de l'Atelier 3 pret.</body></html>"
        if not identite_invalide_at3 and "generer_et_telecharger_rapport3" in globals():
            html_data_at3 = generer_et_telecharger_rapport3()

        st.download_button(
            label="Exporter le rapport HTML",
            data=html_data_at3,
            file_name=f"Rapport_Atelier3_{st.session_state.get('nom_var', 'ELEVE')}.html",
            mime="text/html",
            key="btn_exp3_at3_final_ok",
            disabled=identite_invalide_at3,
        )






