import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random
import math
from PIL import ImageGrab
import os
import matplotlib.patches as patches
import time 
# Titre de l'application
st.title("Application de Probabilités")


st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)



# Signature de l'auteur
st.markdown("**Créé et développé par Laurent GALLET**")

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
if "mise" not in st.session_state:
    st.session_state.mise = 1.0  
# CORRECTION : Ajout de la variable date_heure manquante
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")
if "btn_valider_desactive" not in st.session_state:
    st.session_state.btn_valider_desactive = False
if "pari_couleur_eleve" not in st.session_state:
    st.session_state.pari_couleur_eleve = "Rouge"
if "pari_parite_eleve" not in st.session_state:
    st.session_state.pari_parite_eleve = "Pair"
if "pari_numero_eleve" not in st.session_state:
    st.session_state.pari_numero_eleve = 7
if "type_pari" not in st.session_state:
    st.session_state.type_pari = "Couleur"
if "options_pari_affichées" not in st.session_state:
    st.session_state.options_pari_affichées = False
if "total_rotations_roulette" not in st.session_state:
    st.session_state.total_rotations_roulette = 0
    # Initialisation du dictionnaire étendu de 0 à 100
    st.session_state.stats_par_numero_roulette = {num: 0 for num in range(0, 101)}
if "total_lancers_de" not in st.session_state:
    st.session_state.total_lancers_de = 0
if "total_lancers_slot" not in st.session_state:
    st.session_state.total_lancers_slot = 0
if "total_lancers_de" not in st.session_state:
    st.session_state.total_lancers_de = 0
    st.session_state.stats_par_face_de = {face: 0 for face in range(1, 101)}
    st.session_state.historique_logs = []
if "total_lancers_slot" not in st.session_state:
    st.session_state.total_lancers_slot = 0
    st.session_state.cpt_classe_jackpots = 0
    st.session_state.cpt_classe_gagnes = 0
    st.session_state.liste_casino_view1 = []
if "orientation_aiguille" not in st.session_state:
    st.session_state.orientation_aiguille = 0.0
if "total_pari_num" not in st.session_state:
    st.session_state.total_pari_num = 0
    st.session_state.gains_pari_num = 0
    st.session_state.total_pari_coul = 0
    st.session_state.gains_pari_coul = 0
    st.session_state.total_pari_par = 0
    st.session_state.gains_pari_par = 0
if "total_rotations_roulette" not in st.session_state:
    st.session_state.total_rotations_roulette = 0
    st.session_state.stats_par_numero_roulette = {num: 0 for num in range(0, 101)}
if "liste_roulette_view1" not in st.session_state:
    st.session_state.liste_roulette_view1 = []
if "combinaison_active" not in st.session_state:
    st.session_state.combinaison_active = "Rouge"
if "type_pari" not in st.session_state:
    st.session_state.type_pari = "Couleur"
if "type_pari" not in st.session_state:
    st.session_state.type_pari = "Couleur"
if "combinaison_active" not in st.session_state:
    st.session_state.combinaison_active = "Rouge"
if "pari_couleur_eleve" not in st.session_state: st.session_state.pari_couleur_eleve = "Rouge"
if "pari_parite_eleve" not in st.session_state: st.session_state.pari_parite_eleve = "Pair"
if "pari_douzaine_eleve" not in st.session_state: st.session_state.pari_douzaine_eleve = "1st 12"
if "pari_manque_passe_eleve" not in st.session_state: st.session_state.pari_manque_passe_eleve = "1-18"
if "pari_numero_eleve" not in st.session_state: st.session_state.pari_numero_eleve = 0
if "quiz_deja_valide" not in st.session_state:
    st.session_state.quiz_deja_valide = False
if "score_final_quiz" not in st.session_state:
    st.session_state.score_final_quiz = 0
if "reponses_trous" not in st.session_state:
    st.session_state.reponses_trous = {i: "" for i in range(15)}
if "mode_examen_actif" not in st.session_state:
    st.session_state.mode_examen_actif = False
if "solde" not in st.session_state:
    # On définit un solde initial de départ pour l'élève (ajustez le montant si nécessaire)
    st.session_state.solde = 100.0
if "historique" not in st.session_state:
    st.session_state.historique = []
if "mode_examen_actif" not in st.session_state:
    st.session_state.mode_examen_actif = False
if "stats_par_face_de" not in st.session_state:
    # Initialise les compteurs de lancers à 0 pour chaque face de 1 à 6
    st.session_state.stats_par_face_de = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}    
# Variables de stockage pour figer les configurations aléatoires d'examen
if "slider_faces_n1_valeur" not in st.session_state:
    st.session_state.slider_faces_n1_valeur = 6  # Valeur par défaut initiale
if "slider_shapes_n1_valeur" not in st.session_state:
    st.session_state.slider_shapes_n1_valeur = 7  # Valeur par défaut initiale
if "historique_logs" not in st.session_state:
    st.session_state.historique_logs = []  # Liste vide pour enregistrer l'historique des lancers
if "roulette_gagnes" not in st.session_state:
    st.session_state.roulette_gagnes = 0
if "roulette_perdus" not in st.session_state:
    st.session_state.roulette_perdus = 0
if "slot_jackpots" not in st.session_state:
    st.session_state.slot_jackpots = 0
if "slot_gagnes" not in st.session_state:
    st.session_state.slot_gagnes = 0
if "slot_perdus" not in st.session_state:
    st.session_state.slot_perdus = 0
if "de_total_lancers" not in st.session_state:
    st.session_state.de_total_lancers = 0
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
if "orientation_aiguille" not in st.session_state:
    st.session_state.orientation_aiguille = 0.0
if "index_gagnant_roue" not in st.session_state:
    st.session_state.index_gagnant_roue = 0
if "victoire_pari" not in st.session_state:
    st.session_state.victoire_pari = False
if "dernier_statut_roue" not in st.session_state:
    st.session_state.dernier_statut_roue = "Attente"
    
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
</html>
"""

    # 4. PRÉPARATION DU NOM DE FICHIER SÉCURISÉ
    nom_fichier_propre = f"Rapport_Evaluation_Probabilites_{nom_eleve}_{classe_eleve}.html"
    for car in [r"/", r"\\", r"*", r"?", r'"', r"<", r">", r"|", r":"]:
        nom_fichier_propre = nom_fichier_propre.replace(car, "_")

    # 5. BOUTON DE TÉLÉCHARGEMENT NATIF DE STREAMLIT
    st.download_button(
        label="Telecharger le rapport d'evaluation HTML",
        data=html_content,
        file_name=nom_fichier_propre,
        mime="text/html",
        key="btn_telecharger_rapport1"
    )

# Appel de la fonction dans votre interface web
generer_et_telecharger_rapport1()


# =====================================================================
# LOGIQUE ET PROTOCOLE DE PROTECTION (Anciennement basculer_mode_examen_protection1)
# =====================================================================
def basculer_mode_examen_protection1():
    """Protocole de l'Atelier 1 : fige la session, bloque les curseurs et brasse le QCM."""
    # 1. Activation du drapeau de verrouillage dans l'état de la session
    st.session_state.mode_examen_actif = True

    # 2. Verrouillage et tirage aléatoire du nombre de faces du Dé (de 4 à 20 faces)
    st.session_state.slider_faces_n1_valeur = random.randint(4, 20)

    # 3. CORRECTION DU BUG : La liste est maintenant correctement assignée à la variable
    valeurs_possibles = [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    st.session_state.slider_shapes_n1_valeur = int(random.choice(valeurs_possibles))

    # 4. Suppression des données du QCM existant pour forcer le re-brassage au prochain rendu
    if "quiz1_data" in st.session_state:
        del st.session_state.quiz1_data

    # 5. Déclenchement automatique des simulations synchrones requises
    if "executer_simulation_loi_grands_nombres1" in globals():
        executer_simulation_loi_grands_nombres1()

    if "dessiner_roue_tricolore1" in globals():
        dessiner_roue_tricolore1(0, "Attente")


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
    """Dessine le cylindre de la roulette et la position de la bille en mouvement."""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(-110, 110)
    ax.set_ylim(-110, 110)
    ax.axis("off")

    # Dessin du cadran circulaire de la roulette
    cadran = plt.Circle((0, 0), 100, color="#1e293b", ec="#334155", lw=3)
    ax.add_patch(cadran)
    centre_or = plt.Circle((0, 0), 20, color="#e2e8f0", ec="#cbd5e1", lw=1)
    ax.add_patch(centre_or)

    # Tracé des rayons du cylindre pour matérialiser la rotation
    for a in range(0, 360, 30):
        rad = math.radians(a + angle_bille)
        ax.plot(
            [0, 100 * math.cos(rad)], [0, 100 * math.sin(rad)], color="#334155", lw=0.5
        )

    # Positionnement de la bille blanche sur la piste circulaire
    rad_bille = math.radians(angle_bille)
    couleur_bille = "#f43f5e" if phase == "Cloture" else "#ffffff"
    taille_bille = 100 if phase == "Cloture" else 60

    bille = plt.scatter(
        [85 * math.cos(rad_bille)],
        [85 * math.sin(rad_bille)],
        color=couleur_bille,
        s=taille_bille,
        zorder=5,
        edgecolors="black",
    )

    if phase == "Cloture":
        ax.text(
            0,
            0,
            str(st.session_state.index_gagnant_roue),
            color="#0f172a",
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
        )

    st.pyplot(fig, clear_figure=True)


def dessiner_tapis_avec_jeton_grand():
    """Charge le tapis de jeu local et superpose un gros jeton doré sur la zone misée."""
    fig, ax = plt.subplots(figsize=(6, 3.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")

    try:
        img = plt.imread("image_tapis_roulette.jpg")
        ax.imshow(img)
    except:
        # Fond vert de secours si l'image locale a un problème
        ax.add_patch(plt.Rectangle((0, 0), 600, 350, facecolor="#065f46"))

    ax.axis("off")

    # Coordonnées par défaut du jeton sur l'image
    jx, jy = 300, 175  # Centre par défaut (Numéro Plein)
    pari_mode = st.session_state.type_pari
    choix = st.session_state.combinaison_active

    # Ajustement des coordonnées pour voir le jeton se déplacer en grand
    if pari_mode == "Couleur":
        jx = 160 if choix == "Rouge" else 440
        jy = 280
    elif pari_mode == "Parite":
        jx = 250 if choix == "Even" else 350
        jy = 280
    elif pari_mode == "Douzaine":
        if choix == "1st 12":
            jx = 150
        elif choix == "2nd 12":
            jx = 300
        else:
            jx = 450
        jy = 180
    elif pari_mode == "Numero":
        try:
            num = int(choix)
            jx = 100 + ((num - 1) % 12) * 35
            jy = 60 + ((num - 1) // 12) * 40
        except:
            pass

    # Dessin du gros jeton de casino doré avec sa valeur écrite au centre
    jeton_externe = plt.Circle(
        (jx, jy), 22, facecolor="#eab308", edgecolor="#ffffff", lw=2, zorder=10
    )
    jeton_interne = plt.Circle(
        (jx, jy), 15, facecolor="#ca8a04", edgecolor="#eab308", lw=1, zorder=11
    )
    ax.add_patch(jeton_externe)
    ax.add_patch(jeton_interne)

    ax.text(
        jx,
        jy,
        f"{st.session_state.mise}",
        color="white",
        fontsize=8,
        fontweight="bold",
        ha="center",
        va="center",
        zorder=12,
    )

    return fig

    
def animer_roue_hasard1():
    """Simule la rotation de la bille, détermine le numéro gagnant et met à jour les stats."""
    import random

    conteneur_graphique = st.empty()
    dynamique_vitesse = 30.0

    # Boucle de rotation de la bille
    while dynamique_vitesse > 0.8:
        st.session_state.orientation_aiguille = (
            st.session_state.orientation_aiguille + dynamique_vitesse
        ) % 360

        with conteneur_graphique:
            dessiner_roue_tricolore1(
                st.session_state.orientation_aiguille, "Animation"
            )

        dynamique_vitesse -= random.uniform(0.8, 2.2)
        time.sleep(0.040)

    # Calcul de l'arrêt géométrique de la bille
    ordre_officiel = (
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
    )
    n_num = 37
    angle_secteur = 360.0 / n_num

    index_secteur = (
        int(
            round(
                (
                    90.0
                    - angle_secteur
                    - st.session_state.orientation_aiguille
                )
                / angle_secteur
            )
        )
        % n_num
    )
    st.session_state.index_gagnant_roue = ordre_officiel[index_secteur]
    st.session_state.orientation_aiguille = (
        90.0 - angle_secteur - (index_secteur * angle_secteur)
    ) % 360

    # Détermination de la couleur
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
    if st.session_state.index_gagnant_roue == 0:
        couleur_gagnante = "Vert"
        parite_gagnante = "Zero"
        douzaine_gagnante = "Zero"
        intervalle_gagnant = "Zero"
    else:
        couleur_gagnante = (
            "Rouge" if st.session_state.index_gagnant_roue in rouges else "Noir"
        )
        parite_gagnante = (
            "Even" if st.session_state.index_gagnant_roue % 2 == 0 else "Odd"
        )
        if 1 <= st.session_state.index_gagnant_roue <= 12:
            douzaine_gagnante = "1st 12"
        elif 13 <= st.session_state.index_gagnant_roue <= 24:
            douzaine_gagnante = "2nd 12"
        else:
            douzaine_gagnante = "3rd 12"
        intervalle_gagnant = (
            "1-18" if st.session_state.index_gagnant_roue <= 18 else "19-36"
        )

    # Vérification des conditions de victoire
    gagne = False
    type_pari_actif = st.session_state.type_pari
    mise_choisie = st.session_state.combinaison_active

    if type_pari_actif == "Couleur" and mise_choisie == couleur_gagnante:
        gagne = True
    elif type_pari_actif == "Parite" and mise_choisie == parite_gagnante:
        gagne = True
    elif type_pari_actif == "Douzaine" and mise_choisie == douzaine_gagnante:
        gagne = True
    elif type_pari_actif == "Manque/Passe" and mise_choisie == intervalle_gagnant:
        gagne = True
    elif type_pari_actif == "Numero" and mise_choisie == str(
        st.session_state.index_gagnant_roue
    ):
        gagne = True

    st.session_state.victoire_pari = gagne

    # Mise à jour comptable
    if gagne:
        facteur_gain = 35.0 if type_pari_actif == "Numero" else (
            2.0 if type_pari_actif == "Douzaine" else 1.0
        )
        valeur_gain = float(st.session_state.mise) * facteur_gain
        st.session_state.solde += valeur_gain
        st.session_state.roulette_gagnes += 1
        st.session_state.dernier_message_roulette = f"Gagne ! La bille s'est arretee sur : {st.session_state.index_gagnant_roue} ({couleur_gagnante}). Vous gagnez {valeur_gain:.1f} €."
        st.session_state.statut_dernier_lancer = "success"
    else:
        st.session_state.solde -= float(st.session_state.mise)
        st.session_state.roulette_perdus += 1
        st.session_state.dernier_message_roulette = f"Perdu ! La bille s'est arretee sur : {st.session_state.index_gagnant_roue} ({couleur_gagnante})."
        st.session_state.statut_dernier_lancer = "error"

    with conteneur_graphique:
        dessiner_roue_tricolore1(st.session_state.orientation_aiguille, "Cloture")

    st.session_state.dernier_statut_roue = "Fini"
    st.rerun()



def verifier_victoire_pari1():
    """Liaison passerelle pour la compatibilité avec l'animation principale."""
    index_gagnant = st.session_state.get("index_gagnant_roue", 0)
    return verifier_victoire_pari1_pour_numero(index_gagnant)


def verifier_victoire_pari1_pour_numero(num_sorti):
    """Verifie si le numero sorti valide la combinaison du tapis choisie."""
    # Récupération sécurisée depuis st.session_state (avec valeur "Rouge" par défaut si absente)
    combinaison = st.session_state.get("combinaison_active", "Rouge")
    numeros_rouges = (1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36)

    # Le zero fait perdre toutes les chances simples, doubles et douzaines
    if num_sorti == 0:
        return (combinaison == "0")

    # 1. Verification des grilles de numeros pleins
    if combinaison.isdigit():
        return (num_sorti == int(combinaison))

    # 2. Verification des Douzaines
    if combinaison == "1st 12":
        return (1 <= num_sorti <= 12)
    elif combinaison == "2nd 12":
        return (13 <= num_sorti <= 24)
    elif combinaison == "3rd 12":
        return (25 <= num_sorti <= 36)

    # 3. Verification des Passes / Manques
    if combinaison == "1-18":
        return (1 <= num_sorti <= 18)
    elif combinaison == "19-36":
        return (19 <= num_sorti <= 36)

    # 4. Verification des Couleurs
    if combinaison == "Rouge":
        return (num_sorti in numeros_rouges)
    elif combinaison == "Noir":
        return (num_sorti not in numeros_rouges)

    # 5. Verification des Parites


def valider_saisie():
    nom = st.session_state.nom_var.strip()
    prenom = st.session_state.prenom_var.strip()
    classe = st.session_state.classe_var.strip()

    if not nom or not prenom or not classe:
        st.error(
            "Erreur : Veuillez compléter entièrement vos données et valider."
        )
    else:
        st.session_state.verrouille = True
        st.success(
            f"Validation effectuée pour : {nom} {prenom} {classe}. Le formulaire est maintenant verrouillé."
        )


# 2. ÉQUIVALENT DE : capturer_onglet_complet(self)
# Note : Sur le web, on génère un rapport texte/données téléchargeable au lieu d'une capture d'écran graphique.
def preparer_nom_fichier(nom_onglet):
    nom_propre = st.session_state.nom_var.replace(" ", "_")
    prenom_propre = st.session_state.prenom_var.replace(" ", "_")
    classe_propre = st.session_state.classe_var.replace(" ", "_")

    maintenant = datetime.now()
    heure_actuelle = maintenant.strftime("%H-%M-%S")
    date_texte = maintenant.strftime("%Y-%m-%d_%Hh%M")

    nom_fichier = f"{nom_propre}_{prenom_propre}_{classe_propre}_{date_texte}_{heure_actuelle}_{nom_onglet}.txt"
    return nom_fichier

# Déclaration officielle des 10 onglets de navigation
tabs = st.tabs([
    "Identification",
    "1. Jeux de hasard",
    "2. Les différentes lumières",
    "3. Tableau de proportionnalités",
    "4. Artbre de proportionnalités",
    "5. Espérance mathématique et variance",
    "6. Loi exponentielle",
    "7. Exemple 1",
    "8. Exemple 2",
    "9. Exemple 3"
])

# Assignation des variables d'onglets (C'est ici que tab0 est créé !)
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = tabs
with tab0:
        st.subheader("Identification")
        
        # CORRECTION LIGNE 973 : Ajout du chiffre 2 pour creer deux colonnes
        col1, col2 = st.columns(2)

        with col1:
            # Champ de saisie : Nom
            nom_saisi = st.text_input(
                "Nom :",
                value=st.session_state.nom_var,
                disabled=st.session_state.verrouille,
            )
            # Champ de saisie : Prénom
            prenom_saisi = st.text_input(
                "Prénom :",
                value=st.session_state.prenom_var,
                disabled=st.session_state.verrouille,
            )
            # Champ de saisie : Groupe / Classe
            classe_saisie = st.text_input(
                "Groupe / Classe :",
                value=st.session_state.classe_var,
                disabled=st.session_state.verrouille,
            )

            # Sauvegarde immédiate des données dans le session_state
            st.session_state.nom_var = nom_saisi
            st.session_state.prenom_var = prenom_saisi
            st.session_state.classe_var = classe_saisie

            # Espacement avant le bouton
            st.write("")

            # Bouton de validation (simule le bouton Ok)
            if st.button("Ok", disabled=st.session_state.verrouille):
                valider_session()
                st.rerun()
                
def valider_session():
    nom = st.session_state.nom_var.strip()
    prenom = st.session_state.prenom_var.strip()
    groupe = st.session_state.classe_var.strip()  # Correspond à votre champ groupe/classe

    if not nom or not prenom or not groupe:
        st.warning(
            "Identification incomplète : Veuillez remplir l'ensemble des champs avant de commencer vos manipulations."
        )
    else:
        st.session_state.verrouille = True
        st.success(
            f"Session Ouverte : Bienvenue {prenom} {nom}.\nVotre session de TP pour le groupe {groupe} est désormais active."
        )

# Contenu de l'onglet 1

with tab1:
    
    st.subheader("Les jeux de hasards")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("La roulette")
        # 1. INITIALISATION DES COMPTEURS STATISTIQUES (Evite les KeyError)
        if "solde" not in st.session_state:
            st.session_state.solde = 100.0
        if "mise" not in st.session_state:
            st.session_state.mise = 1.0
        if "type_pari" not in st.session_state:
            st.session_state.type_pari = "Couleur"
        if "combinaison_active" not in st.session_state:
            st.session_state.combinaison_active = "Rouge"
            
        # Compteurs pour vos graphiques de gains/pertes (Vert/Rouge sur votre capture)
        if "roulette_gagnes" not in st.session_state:
            st.session_state.roulette_gagnes = 0
        if "roulette_perdus" not in st.session_state:
            st.session_state.roulette_perdus = 0

        # 2. SELECTION DU PARI ET PLACEMENT DU JETON
        st.session_state.mise = st.number_input(
            "Montant de la mise (e) :",
            min_value=1.0,
            max_value=float(st.session_state.solde) if float(st.session_state.solde) > 1.0 else 1.0,
            value=float(st.session_state.mise) if float(st.session_state.mise) <= float(st.session_state.solde) else 1.0,
            step=1.0,
            key="input_montant_mise_roulette_unifie_final",
        )

        mode_roulette = st.selectbox(
            "Type de pari :",
            options=["Couleur", "Parite", "Douzaine", "Manque/Passe", "Numero"],
            key="select_type_pari_roulette_unifie_final",
        )
        st.session_state.type_pari = mode_roulette

        # Affichage du sous-menu pour designer l'emplacement exact du jeton
        if st.session_state.type_pari == "Couleur":
            choix_coul = st.selectbox("Placer le jeton sur la couleur :", options=["Rouge", "Noir"], key="sb_coul_final")
            st.session_state.combinaison_active = choix_coul
        elif st.session_state.type_pari == "Parite":
            choix_par = st.selectbox("Placer le jeton sur :", options=["Pair", "Impair"], key="sb_par_final")
            st.session_state.combinaison_active = "Even" if choix_par == "Pair" else "Odd"
        elif st.session_state.type_pari == "Douzaine":
            choix_douz = st.selectbox("Placer le jeton sur la douzaine :", options=["1st 12", "2nd 12", "3rd 12"], key="sb_douz_final")
            st.session_state.combinaison_active = choix_douz
        elif st.session_state.type_pari == "Manque/Passe":
            choix_mp = st.selectbox("Placer le jeton sur l'intervalle :", options=["1-18", "19-36"], key="sb_mp_final")
            st.session_state.combinaison_active = choix_mp
        elif st.session_state.type_pari == "Numero":
            numero_devine = st.number_input("Placer le jeton sur le numero plein (1 a 36) :", min_value=1, max_value=36, value=1, step=1, key="in_num_final")
            st.session_state.combinaison_active = str(numero_devine)

        # Rappel textuel de l'emplacement du jeton pour l'eleve
        st.info(f"Emplacement du jeton : Case {st.session_state.combinaison_active}")
  
      
    def dessiner_roue_tricolore1(angle_bille, phase="Animation"):
        """Génère un cylindre de roulette circulaire exclusif en gros plan."""
        fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.axis("off")

        # 1. Tracé des anneaux concentriques de fond de la roue
        roue_exterieure = plt.Circle(
            (0, 0), 1.1, color="#1e293b", ec="#334155", lw=3
        )
        piste_bille = plt.Circle((0, 0), 0.95, color="#0f172a", ec="#475569", lw=1)

        ax.add_patch(roue_exterieure)
        ax.add_patch(piste_bille)

        # 2. Séparation géométrique des 37 numéros (Rayons de la roue)
        for i in range(37):
            angle_secteur = math.radians((i * 360.0 / 37) + angle_bille)
            x_bord = 1.1 * math.cos(angle_secteur)
            y_bord = 1.1 * math.sin(angle_secteur)
            ax.plot([0, x_bord], [0, y_bord], color="#334155", lw=0.8)

        # 3. CORRECTIONS DE L'ORDRE : Le centre doré est dessiné APRÈS les rayons pour les masquer
        centre_dore = plt.Circle(
            (0, 0), 0.25, facecolor="#ca8a04", edgecolor="#eab308", lw=1.5, zorder=4
        )
        ax.add_patch(centre_dore)

        # 4. Positionnement de la bille blanche sur la piste circulaire
        rad_bille = math.radians(angle_bille)
        x_bille = 0.95 * math.cos(rad_bille)
        y_bille = 0.95 * math.sin(rad_bille)

        bille = plt.Circle(
            (x_bille, y_bille), 0.06, color="#ffffff", ec="#000000", lw=1, zorder=10
        )
        ax.add_patch(bille)

        # 5. Affichage du numéro gagnant au centre de la roue à l'arrêt
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

            # Remplacement de l'ancien affichage d'image par le tapis vectoriel avec le gros jeton doré
        st.markdown("**Positionnement de votre jeton sur le tapis :**")
        fig_tapis_interactif = dessiner_tapis_avec_jeton_grand()
        st.pyplot(fig_tapis_interactif, clear_figure=True)
        st.markdown(f"**Solde actuel disponible :** {st.session_state.solde:.1f} €")

        if st.button("Tourner la Roue [R]", key="btn_lancer_roulette_animee_finale"):
            st.session_state.dernier_statut_roue = "En cours"
            animer_roue_hasard1()
            st.rerun()

        # 2. AFFICHAGE EXCLUSIF DE LA ROUE SEULE ET DU MESSAGE DE SCORE (Au milieu)
        if st.session_state.dernier_statut_roue == "Fini":
            st.markdown("**Position d'arret de la bille dans le cylindre :**")
            dessiner_roue_tricolore1(
                st.session_state.orientation_aiguille, "Cloture"
            )

            if st.session_state.statut_dernier_lancer == "success":
                st.success(st.session_state.dernier_message_roulette)
            else:
                st.error(st.session_state.dernier_message_roulette)

        # 3. LE GRAND TAPIS INTERACTIF POUR LES CHOIX DES ELEVES (Tout en bas)
        st.markdown("---")
        st.markdown("**Positionnement de votre jeton sur le tapis :**")
        fig_tapis_interactif = dessiner_tapis_avec_jeton_grand()
        st.pyplot(fig_tapis_interactif, clear_figure=True)

        # 4. COMPTEURS STATISTIQUES GLOBAUX
        st.markdown("---")
        total_lancers = st.session_state.roulette_gagnes + st.session_state.roulette_perdus
        pct_gagnes = (st.session_state.roulette_gagnes / total_lancers * 100) if total_lancers > 0 else 0.0
        pct_perdus = (st.session_state.roulette_perdus / total_lancers * 100) if total_lancers > 0 else 0.0

        st.markdown(f":green[Roulette Gagnes : {st.session_state.roulette_gagnes}/{total_lancers} ({pct_gagnes:.1f}%)]")
        st.markdown(f":red[Roulette Perdus : {st.session_state.roulette_perdus}/{total_lancers} ({pct_perdus:.1f}%)]")
        st.caption(f"Total rotations : {total_lancers}")
         



    with col2:
        st.markdown("Machine SLOT")


        # =====================================================================
        # AFFICHAGE DE L'HISTORIQUE DE LA SLOT MACHINE
        # =====================================================================
        historique_casino_actuel = st.session_state.get("liste_casino_view1", [])

        # La condition vérifie si la liste contient des logs avant d'afficher le panneau
        if historique_casino_actuel:
            st.write("---")
            st.subheader("Historique de la machine a sous")
            st.code("\n".join(st.session_state.liste_casino_view1), language="text")

        if st.button("Actionner le levier de la Slot Machine", key="btn_lancer_casino1"):
            with st.spinner("Verification des alignements de la machine..."):
                    # Temps fictif d'arrêt successif des rouleaux
                time.sleep(2.0)
                    
                    # Tirage des 3 éléments (Exemple avec des ID de 1 à 4)
                v1 = random.randint(1, 4)
                v2 = random.randint(1, 4)
                v3 = random.randint(1, 4)
                    
                    # Logique de calcul du verdict
                if v1 == v2 == v3:
                        verdict = "JACKPOT"
                elif v1 == v2 or v2 == v3 or v1 == v3:
                        verdict = "GAGNE"
                else:
                    verdict = "PERDU"
                        
                st.session_state.total_lancers_slot += 1

                # Appel direct de la fonction de rendu graphique Matplotlib convertie précédemment
                # dessiner_machine_casino1(v1, v2, v3, verdict)
            st.text(f"Resultat : {v1} - {v2} - {v3} | Verdict : {verdict}")

        total_slot = st.session_state.get("total_lancers_slot", 0)

        if total_slot == 0:
            cpt_jk, cpt_g, cpt_p = 0, 0, 0
            tx_jk, tx_g, tx_p = 0.0, 0.0, 0.0
        else:
            cpt_jk = st.session_state.get("cpt_classe_jackpots", 0)
            cpt_g = st.session_state.get("cpt_classe_gagnes", 0)
            cpt_p = total_slot - (cpt_jk + cpt_g)
            
            tx_jk = (cpt_jk / total_slot) * 100
            tx_g = (cpt_g / total_slot) * 100
            tx_p = (cpt_p / total_slot) * 100

        # Affichage sécurisé dans Streamlit
        st.text(f"Slot Jackpots (3 id.) : {cpt_jk}/{total_slot} ({tx_jk:.1f}%)")
        st.text(f"Slot Gagnes (2 id.)   : {cpt_g}/{total_slot} ({tx_g:.1f}%)")
        st.text(f"Slot Perdus (0 id.)   : {cpt_p}/{total_slot} ({tx_p:.1f}%)")

                
        def dessiner_machine_casino1(v1, v2, v3, verdict):
            # AJOUT DE L'IMPORTATION MANQUANTE POUR SÉCURISER LES TRACÉS GEOMÉTRIQUES
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            
            # Création d'une figure Matplotlib (équivalent du Canvas de 600x105)
            fig, ax = plt.subplots(figsize=(6, 1.05), dpi=100)
            
            # Configuration du fond et suppression des axes de coordonnées
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')
            ax.axis('off')
            ax.set_xlim(0, 600)
            ax.set_ylim(0, 105)
            w_boite = 50
            h_boite = 50
            y_boite = 52.5 - 25
            espace = 15
            x_start_bloc = 300 - 20
            positions_x = [x_start_bloc, x_start_bloc + w_boite + espace, x_start_bloc + 2*(w_boite + espace)]
            tirages = [v1, v2, v3]
            
            for idx, x_start in enumerate(positions_x):
                # Dessin de la boîte de fond sombre à bordure jaune
                rect_fond = patches.Rectangle((x_start, y_boite), w_boite, h_boite, 
                                              facecolor="#2d2d39", edgecolor="#fbbf24", linewidth=2)
                ax.add_patch(rect_fond)
                
                # Récupération de la forme géométrique associée au tirage
                f_config = FORMES_CASINO.get(tirages[idx], {"nom": "Sept", "couleur": "#ec4899", "type": "oval"})
                cx = x_start + (w_boite / 2)
                cy = y_boite + (h_boite / 2)
                r = 11
                
                # Rendu géométrique selon le type configuré
                if f_config["type"] == "rect":
                    forme = patches.Rectangle((cx - r, cy - r), 2*r, 2*r, facecolor=f_config["couleur"], edgecolor="#ffffff")
                    ax.add_patch(forme)
                elif f_config["type"] == "oval":
                    forme = patches.Circle((cx, cy), r, facecolor=f_config["couleur"], edgecolor="#ffffff")
                    ax.add_patch(forme)
                elif f_config["type"] == "poly":
                    points = [[cx, cy + r], [cx - r, cy - r], [cx + r, cy - r]]
                    forme = patches.Polygon(points, facecolor=f_config["couleur"], edgecolor="#ffffff")
                    ax.add_patch(forme)
                elif f_config["type"] == "diamond":
                    points = [[cx, cy + r], [cx + r, cy], [cx, cy - r], [cx - r, cy]]
                    forme = patches.Polygon(points, facecolor=f_config["couleur"], edgecolor="#ffffff")
                    ax.add_patch(forme)

            # Affichage du verdict textuel en fin de ligne
            if verdict != "":
                couleur_verdict = "#16a34a" if verdict != "PERDU" else "#ef4444"
                ax.text(520, 52.5, verdict, color=couleur_verdict, weight="bold", fontsize=11, va="center", ha="center")
                
            # Rendu graphique immédiat dans l'interface web
            st.pyplot(fig, clear_figure=True)

        # Exemple d'appel de test (v1=1, v2=2, v3=1, verdict="PERDU")
        dessiner_machine_casino1(1, 2, 1, "PERDU")



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


    st.subheader("Parametres du Mode Examen")

    # 1. Vérification de l'identité de l'élève stockée à l'accueil
    nom_eleve = str(st.session_state.get("nom_utilisateur", "")).strip().upper()
    identite_invalide = nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]

    # 2. Dispositif de la case à cocher
    if identite_invalide:
        # Si le nom est manquant, on affiche une case décorative désactivée et un message d'erreur
        st.checkbox("Activer le Mode Examen", value=False, disabled=True, key="chk_examen_bloque")
    else:
        # Si l'identité est valide, la case devient interactive
        # Une fois cochée, le paramètre disabled=True empêche l'élève de la décocher
        mode_examen_coche = st.checkbox(
            "Activer le Mode Examen",
            value=st.session_state.mode_examen_actif,
            disabled=st.session_state.mode_examen_actif,
            key="chk_examen_libre"
        )
        
        # Déclenchement automatique du protocole à la coche
        if mode_examen_coche and not st.session_state.mode_examen_actif:
            basculer_mode_examen_protection1()
            st.rerun()



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
        st.markdown(f"**Question {idx+1} :** {item['q']}")
        
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
                st.markdown(f'<p style="color:#16a34a; margin:2px 0px;">Question {idx+1} : Correct</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color:#dc2626; margin:2px 0px;">Question {idx+1} : Erreur (Votre choix : "{user_rep}" | Reponse attendue : "{correct_rep}")</p>', unsafe_allow_html=True)
                
        st.markdown(f'<h3>Note du Quiz : {score_quiz} / 10</h3>', unsafe_allow_html=True)




























