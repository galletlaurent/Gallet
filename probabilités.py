import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random
import math
from PIL import ImageGrab
import os
import matplotlib.patches as patches

# Titre de l'application
st.title("Application de Probabilités")
st.title("Application de Probabilités")

st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)


# Création de 3 onglets (indexés de 0 à 2)
tab0, tab1, tab2 = st.tabs(["Identification", "Jeux", "Onglet 2"])

# Signature de l'auteur
st.markdown("**Créé et développé par Laurent GALLET**")

if "identifie" not in st.session_state:
    st.session_state.identifie = False
if "nom" not in st.session_state:
    st.session_state.nom = ""
if "prenom" not in st.session_state:
    st.session_state.prenom = ""
if "classe" not in st.session_state:
    st.session_state.classe = ""
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
    
# Variables de stockage pour figer les configurations aléatoires d'examen
if "slider_faces_n1_valeur" not in st.session_state:
    st.session_state.slider_faces_n1_valeur = 6  # Valeur par défaut initiale
if "slider_shapes_n1_valeur" not in st.session_state:
    st.session_state.slider_shapes_n1_valeur = 7  # Valeur par défaut initiale



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
        combinaison_active = st.session_state.get("combinaison_pariee", "Rouge")
        cpt_gagne = 0

        # Simulation de 2000 lancers indépendants avec votre fonction de vérification
        for _ in range(n_lancers):
            tirage = random.randint(0, 36)
            if verifier_victoire_pari1_pour_numero(tirage):
                cpt_gagne += 1

        labels = ["GAGNE", "PERDU"]
        frequences = [cpt_gagne / n_lancers, (n_lancers - cpt_gagne) / n_lancers]

        # Détermination de la cible de probabilité stricte de Bernoulli
        if combinaison_active.isdigit():
            prob_g = 1.0 / 37.0
        elif combinaison_active in ("1st 12", "2nd 12", "3rd 12"):
            prob_g = 12.0 / 37.0
        else:
            prob_g = 18.0 / 37.0
            
        prob_p = 1.0 - prob_g

        ax.bar(labels, frequences, color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
        ax.axhline(y=prob_g, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Theorie Gagne ({prob_g*100:.1f}%)")
        ax.axhline(y=prob_p, color="#2563eb", linestyle="--", linewidth=1.5, label=f"Theorie Perdu ({prob_p*100:.1f}%)")
        ax.set_title(f"Roulette : Simulation du bloc '{combinaison_active}'", fontweight="bold")

    # Habillage commun du graphique
    ax.set_ylabel("Frequence observee")
    ax.set_ylim(0, max(max(frequences) * 1.25, 0.4))
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)

    # Rendu graphique immédiat dans l'interface de l'application web Streamlit
    st.pyplot(fig, clear_figure=True)


# =====================================================================
# EXEMPLE D'INTÉGRATION DANS L'INTERFACE UTILISATEUR
# =====================================================================
# Sélecteur de type de jeu pour alimenter la simulation
st.session_state.choix_jeu_simule = st.radio(
    "Selectionnez le jeu a simuler :", 
    options=["De", "Slot", "Roulette"],
    horizontal=True
)

# Déclenchement de la fonction lors du clic sur le bouton
if st.button("Lancer la simulation des 2000 tirages"):
    executer_simulation_loi_grands_nombres1()
    
def animer_roue_hasard1():
    """Simule la rotation de la bille, détermine le numéro gagnant et met à jour les stats."""
    
    # 1. ZONE DE DESSIN EN TEMPS RÉEL (Conteneur d'affichage dynamique unique)
    conteneur_graphique = st.empty()
    
    # Configuration cinématique initiale de la rotation
    dynamique_vitesse = 30.0  # Vitesse de départ d'origine
    
    # Boucle de rotation simulée (Remplace le processus récursif .after de Tkinter)
    while dynamique_vitesse > 0.8:
        # Incrémentation de l'angle physique
        st.session_state.orientation_aiguille = (st.session_state.orientation_aiguille + dynamique_vitesse) % 360
        
        # Rafraîchissement du dessin géométrique intermédiaire
        with conteneur_graphique:
            # Appel de votre fonction graphique Matplotlib convertie précédemment
            dessiner_roue_tricolore1(st.session_state.orientation_aiguille, "Animation")
            
        # Décélération progressive identique avec la loi uniforme d'origine
        dynamique_vitesse -= random.uniform(0.8, 2.2)
        time.sleep(0.040)  # Équivalent de l'intervalle de 40 millisecondes

    # 2. PHASE D'ARRÊT ET LOGIQUE GÉOMÉTRIQUE DE RECALAGE
    ordre_officiel = (0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26)
    n_num = 37
    angle_secteur = 360.0 / n_num

    # Détermination exacte de l'index du secteur ciblé par la bille
    index_secteur = int(round((90.0 - angle_secteur - st.session_state.orientation_aiguille) / angle_secteur)) % n_num
    
    # Attribution du numéro gagnant officiel de la roulette européenne
    st.session_state.index_gagnant_roue = ordre_officiel[index_secteur]
    
    # Recalage parfait de la bille au centre de la fente
    st.session_state.orientation_aiguille = (90.0 - angle_secteur - (index_secteur * angle_secteur)) % 360

    # Détermination de la couleur du numéro tiré
    numeros_rouges = (1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36)
    if st.session_state.index_gagnant_roue == 0:
        couleur_gagnante = "Vert"
    elif st.session_state.index_gagnant_roue in numeros_rouges:
        couleur_gagnante = "Rouge"
    else:
        couleur_gagnante = "Noir"

    # 3. VÉRIFICATION DU RÉSULTAT DU PARI EN COURS
    pari_mode = st.session_state.get("type_pari_selectionne", "Couleur")
    
    # Appel de votre fonction logique de vérification pure convertie précédemment
    victoire = verifier_victoire_pari1_pour_numero(st.session_state.index_gagnant_roue)
    v_txt = "Gagne" if victoire else "Perdu"

    # 4. COMPTABILISATION DES STATISTIQUES PAR CATÉGORIE DE PARI
    if pari_mode == "Numero":
        st.session_state.total_pari_num += 1
        if victoire: st.session_state.gains_pari_num += 1
    elif pari_mode == "Couleur":
        st.session_state.total_pari_coul += 1
        if victoire: st.session_state.gains_pari_coul += 1
    elif pari_mode == "Parite":
        st.session_state.total_pari_par += 1
        if victoire: st.session_state.gains_pari_par += 1

    # Incrementations de la table globale de chaque numéro de roulette
    st.session_state.total_rotations_roulette += 1
    st.session_state.stats_par_numero_roulette[st.session_state.index_gagnant_roue] += 1

    # 5. ENREGISTREMENT DE LA LIGNE D'HISTORIQUE (insert 0)
    num_log = len(st.session_state.liste_roulette_view1) + 1
    txt_log = f"Tour n°{num_log:02d} : Sorti = {st.session_state.index_gagnant_roue} ({couleur_gagnante[:3]}) -> {v_txt}"
    st.session_state.liste_roulette_view1.insert(0, txt_log)

    # 6. ENREGISTREMENT DU RÉSULTAT POUR LES EFFETS SECONDAIRES (Confettis)
    st.session_state.victoire_pari = victoire

    # Rendu final stabilisé en mode clôture (Affichage des confettis si victoire)
    with conteneur_graphique:
        dessiner_roue_tricolore1(st.session_state.orientation_aiguille, "Cloture")
        
    # Relance l'actualisation globale de la page pour rafraîchir les étiquettes de statistiques
    st.rerun()

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
    
    # Titre du jeu
    ax.text(20, 52.5, "JEU 2 : SLOT MACHINE GEOMETRIQUE", 
            color="#fbbf24", weight="bold", fontsize=10, va="center", ha="left")
    
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


def dessiner_roue_tricolore1(angle_bille, etat_cycle):
    # AJOUT DES IMPORTATIONS INDISPENSABLES POUR LA ROULETTE
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions materielles fixes verrouillees
    largeur = 770
    hauteur = 320

    # Initialisation de la figure Matplotlib
    fig, ax = plt.subplots(figsize=(7.7, 3.2), dpi=100)
    fig.patch.set_facecolor('#15803d')  # Tapis vert de casino réglementaire
    ax.set_facecolor('#15803d')
    ax.axis('off')
    ax.set_xlim(0, largeur)
    ax.set_ylim(0, hauteur)  # Note: Y va de 0 (bas) à hauteur (haut)

    # Gestion de la pluie de confettis via le st.session_state
    pari = st.session_state.get("pari_couleur_eleve", "Rouge")
    
    # Simulation de la méthode verifier_victoire_pari1 (à adapter selon votre logique)
    victoire = st.session_state.get("victoire_pari", False)

    if etat_cycle == "Cloture" and victoire:
        import random
        if "flocon_confettis" not in st.session_state or len(st.session_state.flocon_confettis) < 100:
            st.session_state.flocon_confettis = []
            for _ in range(100):
                st.session_state.flocon_confettis.append({
                    "x": random.randint(10, largeur - 10),
                    "y": random.randint(hauteur, hauteur + 40), # Part du haut en Matplotlib
                    "v": random.randint(3, 6),
                    "t": random.randint(4, 7),
                    "c": random.choice(["#3b82f6", "#ef4444", "#10b981", "#fbbf24"])
                })
        
        for c in st.session_state.flocon_confettis:
            c["y"] -= c["v"]  # Tombe vers le bas (Y diminue)
            if c["y"] < 0:
                c["y"] = random.randint(hauteur, hauteur + 20)
                c["x"] = random.randint(10, largeur - 10)
            
            # Tracé du confetti
            confetti = patches.Circle((c["x"], c["y"]), c["t"]/2, facecolor=c["c"], edgecolor="none")
            ax.add_patch(confetti)

    # =====================================================================
    # 1. LE CYLINDRE DE LA ROULETTE OFFICIELLE (CÔTÉ GAUCHE)
    # =====================================================================
    cx_roue = int(largeur * 0.22)
    cy_roue = hauteur // 2 + 20  # Inversion de l'axe Y par rapport à Tkinter
    
    # Cylindre extérieur bois et fond sombre
    ax.add_patch(patches.Circle((cx_roue, cy_roue), 115, facecolor="#632205", edgecolor="#451401", linewidth=3))
    ax.add_patch(patches.Circle((cx_roue, cy_roue), 110, facecolor="#111827", edgecolor="none"))

    ordre_officiel = (0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26)
    n_num = 37
    angle_secteur = 360.0 / n_num
    numeros_rouges = (1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36)

    for i in range(n_num):
        num_courant = ordre_officiel[i]
        start_a = 90.0 - (i * angle_secteur) - (angle_secteur / 2)
        
        if num_courant == 0:
            c_sec = "#16a34a"
        elif num_courant in numeros_rouges:
            c_sec = "#dc2626"
        else:
            c_sec = "#111827"

        # Arc de cercle pour le secteur
        arc = patches.Wedge((cx_roue, cy_roue), 110, start_a, start_a + angle_secteur, facecolor=c_sec, edgecolor="#4b5563", linewidth=0.5)
        ax.add_patch(arc)
        
        # Positionnement du texte du numéro
        angle_rad = np.radians(start_a + angle_secteur / 2)
        tx = cx_roue + 95 * np.cos(angle_rad)
        ty = cy_roue + 95 * np.sin(angle_rad)
        ax.text(tx, ty, str(num_courant), color="#ffffff", fontsize=6, weight="bold", va="center", ha="center", rotation=np.degrees(angle_rad)-90)

    # Cônes intérieurs et séparateurs dorés/centraux
    ax.add_patch(patches.Circle((cx_roue, cy_roue), 84, facecolor="#15803d", edgecolor="#166534"))
    
    for i in range(n_num):
        start_a = 90.0 - (i * angle_secteur) - (angle_secteur / 2)
        angle_rad = np.radians(start_a)
        ax.plot([cx_roue + 64 * np.cos(angle_rad), cx_roue + 84 * np.cos(angle_rad)],
                [cy_roue + 64 * np.sin(angle_rad), cy_roue + 84 * np.sin(angle_rad)], color="#166534", linewidth=1)

    ax.add_patch(patches.Circle((cx_roue, cy_roue), 64, facecolor="#d97706", edgecolor="#b45309", linewidth=1))
    ax.add_patch(patches.Circle((cx_roue, cy_roue), 48, facecolor="#fbbf24", edgecolor="none"))
    ax.add_patch(patches.Circle((cx_roue, cy_roue), 32, facecolor="#7c2d12", edgecolor="none"))

    # Bras de la roulette (Pivot)
    angle_pivot_deg = angle_bille * 0.4
    for b in range(4):
        angle_b_rad = np.radians(angle_pivot_deg + (b * 90))
        bx1 = cx_roue + 45 * np.cos(angle_b_rad)
        by1 = cy_roue + 45 * np.sin(angle_b_rad)
        ax.plot([cx_roue, bx1], [cy_roue, by1], color="#fbbf24", linewidth=3)
        ax.add_patch(patches.Circle((bx1, by1), 4, facecolor="#fbbf24", edgecolor="#d97706"))

    ax.add_patch(patches.Circle((cx_roue, cy_roue), 10, facecolor="#fbbf24", edgecolor="#b45309", linewidth=2))
    ax.add_patch(patches.Circle((cx_roue, cy_roue), 4, facecolor="#ffffff", edgecolor="none"))

    # Rendu de la bille blanche orbitale
    r_orb = 97
    rad_bille = np.radians(angle_bille)
    bx = cx_roue + r_orb * np.cos(rad_bille)
    by = cy_roue + r_orb * np.sin(rad_bille)
    ax.add_patch(patches.Circle((bx, by), 4, facecolor="#ffffff", edgecolor="#94a3b8", linewidth=1, zorder=5))

    # =====================================================================
    # 2. LE TAPIS DE NUMÉROS RÉGLEMENTAIRE (CÔTÉ DROIT - POINT FIXE STABLE)
    # =====================================================================
    tx_start = 320
    w_case = 32  
    h_case = 30
    ty_start = cy_roue - int(1.5 * h_case)

    # Case 0 verte
    ax.add_patch(patches.Rectangle((tx_start, ty_start), w_case, 3 * h_case, facecolor="#16a34a", edgecolor="#ffffff", linewidth=1.5))
    ax.text(tx_start + w_case / 2, ty_start + (3 * h_case) / 2, "0", color="#ffffff", fontsize=11, weight="bold", va="center", ha="center")

    # Grille de 36 cases numérique
    for num in range(1, 37):
        colonne = (num - 1) // 3
        ligne = (num - 1) % 3  # Ajusté pour l'orientation de bas en haut de Matplotlib
        x1 = tx_start + w_case + (colonne * w_case)
        y1 = ty_start + (ligne * h_case)
        
        c_case = "#dc2626" if num in numeros_rouges else "#111827"
        ax.add_patch(patches.Rectangle((x1, y1), w_case, h_case, facecolor=c_case, edgecolor="#ffffff", linewidth=1.5))
        ax.text(x1 + w_case / 2, y1 + h_case / 2, str(num), color="#ffffff", fontsize=9, weight="bold", va="center", ha="center")

    # 3. Les Blocs de Paris des Douzaines
    ty_douzaines = ty_start - 24
    w_douzaine_case = (12 * w_case) / 3
    for d in range(3):
        xd = tx_start + w_case + (d * w_douzaine_case)
        ax.add_patch(patches.Rectangle((xd, ty_douzaines), w_douzaine_case, 24, facecolor="#15803d", edgecolor="#ffffff", linewidth=1.5))
        ax.text(xd + w_douzaine_case / 2, ty_douzaines + 12, f"{['1st', '2nd', '3rd'][d]} 12", color="#ffffff", fontsize=8, weight="bold", va="center", ha="center")

    # 4. Les Blocs de Paris des Chances Simples
    ty_chances = ty_douzaines - 26
    w_chance_case = (12 * w_case) / 6
    labels_chances = ["1-18", "Even", "ROUGE", "NOIR", "Odd", "19-36"]
    couleurs_chances = ["#15803d", "#15803d", "#b91c1c", "#111827", "#15803d", "#15803d"]
    
    for idx in range(6):
        xc1 = tx_start + w_case + (idx * w_chance_case)
        ax.add_patch(patches.Rectangle((xc1, ty_chances), w_chance_case, 26, facecolor=couleurs_chances[idx], edgecolor="#ffffff", linewidth=1.5))
        
        if labels_chances[idx] in ["ROUGE", "NOIR"]:
            cx, cy = xc1 + w_chance_case / 2, ty_chances + 13
            # Dessin du losange représentatif de la couleur
            losange = patches.Polygon([[cx, cy - 7], [cx + 12, cy], [cx, cy + 7], [cx - 12, cy]], 
                                      facecolor="#dc2626" if labels_chances[idx] == "ROUGE" else "#111827", edgecolor="#ffffff", linewidth=1)
            ax.add_patch(losange)
        else:
            ax.text(xc1 + w_chance_case / 2, ty_chances + 13, labels_chances[idx], color="#ffffff", fontsize=8, weight="bold", va="center", ha="center")

    # Rendu final de l'image sur l'application Streamlit
    st.pyplot(fig, clear_figure=True)

# Exemple d'appel pour valider l'affichage (angle 45 degrés, cycle en attente)
dessiner_roue_tricolore1(45.0, "Attente")


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
    # Récupération des valeurs saisies
    nom = st.session_state.get("nom_input", "").strip()
    prenom = st.session_state.get("prenom_input", "").strip()
    classe = st.session_state.get("classe_input", "").strip()

    # Vérification que les champs ne sont pas vides
    if not nom or not prenom or not classe:
        st.error("Veuillez compléter entièrement vos données et valider.")
        return False

    # Verrouillage des champs (simulé via session_state)
    st.session_state.nom_verrouille = True
    st.session_state.prenom_verrouille = True
    st.session_state.classe_verrouille = True
    st.session_state.btn_valider_desactive = True

    # Affichage du message de confirmation
    st.success(f"Validation effectuée pour : {nom} {prenom} {classe}\nLe formulaire est maintenant verrouillé.")
    print(f"Nom validé : {nom}")
    return True



# Contenu de l'onglet 0 (équivalent à self.tab0)
with tab0:
    st.markdown("### Contenu de l'onglet 0")
    nom = st.text_input("Nom", placeholder="Entrez votre nom")
    prenom = st.text_input("Prénom", placeholder="Entrez votre prénom")

# Contenu de l'onglet 1


with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Zone 1 : Paramètres")
        # Sélection du type de pari
        st.session_state.type_pari = st.selectbox(
            "Type de pari :",
            ["Couleur", "Parité", "Douzaine", "Manque/Passe", "Numéro"]
        )

        # Affichage des options dynamiques
        if st.session_state.type_pari == "Couleur":
            choix_pari = st.radio("Choisissez une couleur :", ["Rouge", "Noir", "Vert"])
        elif st.session_state.type_pari == "Parité":
            choix_pari = st.radio("Choisissez une parité :", ["Pair", "Impair"])
        elif st.session_state.type_pari == "Douzaine":
            choix_pari = st.radio("Choisissez une douzaine :", ["1-12", "13-24", "25-36"])
        elif st.session_state.type_pari == "Manque/Passe":
            choix_pari = st.radio("Choisissez :", ["Manque (1-18)", "Passe (19-36)"])
        elif st.session_state.type_pari == "Numéro":
            choix_pari = st.number_input("Choisissez un numéro (1-36) :", min_value=1, max_value=36)

        # Saisie de la mise
        st.session_state.mise = st.number_input(
            "Montant de la mise (€) :",
            min_value=1.0,                      # CORRECTION : .0 pour forcer le type float
            max_value=float(st.session_state.solde),  # CORRECTION : conversion explicite en float
            value=float(st.session_state.mise),       # CORRECTION : conversion explicite en float
            step=1.0                            # CORRECTION : .0 pour le pas d'incrémentation
        )

    with col2:
        st.markdown("#### Zone 2 : Roulette")
        # Bouton pour lancer la roulette
        if st.button("Tourner la Roue [R]", key="tourner"):
            if st.session_state.mise > st.session_state.solde:
                st.error("Solde insuffisant pour cette mise.")
            else:
                # Génération d'un numéro aléatoire entre 0 et 36
                numero_gagnant = random.randint(0, 36)
                couleur_gagnante = "Rouge" if numero_gagnant in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36] else "Noir" if numero_gagnant != 0 else "Vert"
                parite_gagnante = "Pair" if numero_gagnant % 2 == 0 else "Impair"
                douzaine_gagnante = "1-12" if 1 <= numero_gagnant <= 12 else "13-24" if 13 <= numero_gagnant <= 24 else "25-36"
                manque_gagnant = "Manque (1-18)" if 1 <= numero_gagnant <= 18 else "Passe (19-36)"

                # Vérification du gain
                gain = 0
                if st.session_state.type_pari == "Couleur" and choix_pari == couleur_gagnante:
                    gain = st.session_state.mise * 2
                elif st.session_state.type_pari == "Parité" and choix_pari == parite_gagnante:
                    gain = st.session_state.mise * 2
                elif st.session_state.type_pari == "Douzaine" and choix_pari == douzaine_gagnante:
                    gain = st.session_state.mise * 3
                elif st.session_state.type_pari == "Manque/Passe" and choix_pari == manque_gagnant:
                    gain = st.session_state.mise * 2
                elif st.session_state.type_pari == "Numéro" and choix_pari == numero_gagnant:
                    gain = st.session_state.mise * 36

                # Mise à jour du solde
                st.session_state.solde += gain - st.session_state.mise

                # Enregistrement de l'historique
                st.session_state.historique.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type_pari": st.session_state.type_pari,
                    "choix": choix_pari,
                    "mise": st.session_state.mise,
                    "numero_gagnant": numero_gagnant,
                    "couleur_gagnante": couleur_gagnante,
                    "gain": gain,
                    "solde_final": st.session_state.solde
                })

                st.success(f"Résultat : {numero_gagnant} ({couleur_gagnante})")
                st.info(f"Gain : {gain} € | Nouveau solde : {st.session_state.solde} €")

    with col3:
        st.markdown("#### Zone 3 : Résultats")
        st.write(f"**Solde actuel** : {st.session_state.solde} €")
        st.write(f"**Dernier résultat** : {st.session_state.historique[-1]['numero_gagnant'] if st.session_state.historique else '-'}")

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
        # Section Roulette
        total_roul = st.session_state.get("total_rotations_roulette", 0)
        cpt_g_roul = st.session_state.get("gains_pari_coul", 0)  # Exemple pour les gains couleur
        cpt_p_roul = total_roul - cpt_g_roul
        
        tx_g_roul = (cpt_g_roul / total_roul * 100) if total_roul > 0 else 0.0
        tx_p_roul = (cpt_p_roul / total_roul * 100) if total_roul > 0 else 0.0
        
        # Pour les statistiques avancées globales
        taux_reussite = st.session_state.get("taux_reussite_global", 0.0)
        moyenne_tour = st.session_state.get("moyenne_par_tour_global", 0.0)

        # 2. Rendu HTML/CSS sécurisé sans émoji
        st.markdown(f'<p style="color:#16a34a; font-family:Arial; font-size:13px; font-weight:bold; margin:1px 0px;">Roulette Gagnes      : {cpt_g_roul}/{total_roul} ({tx_g_roul:.1f}%)</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#dc2626; font-family:Arial; font-size:13px; font-weight:bold; margin:1px 0px;">Roulette Perdus      : {cpt_p_roul}/{total_roul} ({tx_p_roul:.1f}%)</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p style="color:#4b5563; font-family:Arial; font-size:13px; font-weight:bold; margin:5px 0px;">Total                : {cpt_g_roul}/{total_roul} ({tx_g_roul:.1f}%)</p>', unsafe_allow_html=True)

        # Ligne de séparation horizontale native de Streamlit
        st.markdown("---")

        st.markdown(f'<p style="color:#16a34a; font-family:Arial; font-size:13px; font-weight:bold; margin:1px 0px;">Roulette Gagnes      : {cpt_g_roul}/{total_roul} ({tx_g_roul:.1f}%)</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#dc2626; font-family:Arial; font-size:13px; font-weight:bold; margin:1px 0px;">Roulette Perdus      : {cpt_p_roul}/{total_roul} ({tx_p_roul:.1f}%)</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#4b5563; font-family:Arial; font-size:13px; font-weight:bold; margin:5px 0px;">Total                : {cpt_g_roul}/{total_roul} ({tx_g_roul:.1f}%)</p>', unsafe_allow_html=True)

if "total_rotations_roulette" not in st.session_state:
    st.session_state.total_rotations_roulette = 0
    # Initialisation du dictionnaire étendu de 0 à 100
    st.session_state.stats_par_numero_roulette = {num: 0 for num in range(0, 101)}

# Récupération sécurisée du nombre de secteurs via votre réglette/curseur Streamlit
# (Remplace self.reglette_secteurs.get() avec une valeur par défaut de 12)
n_secteurs = int(st.session_state.get("reglette_secteurs_valeur", 12))


# 2. LOGIQUE DE CALCUL ET AFFICHAGE DYNAMIQUE (Anciennement actualiser_labels_statistiques_roulette1)
total = st.session_state.total_rotations_roulette

for num in range(0, n_secteurs):
    nb_sorties = st.session_state.stats_par_numero_roulette.get(num, 0)
    taux = (nb_sorties / total * 100) if total > 0 else 0.0
    
    # Gestion stricte de la couleur du libellé d'affichage (Hexadécimaux Tkinter d'origine)
    if num == 0:
        c_texte = "#16a34a"  # Vert
    elif num % 2 == 0:
        c_texte = "#dc2626"  # Rouge
    else:
        c_texte = "#111827"  # Noir/Sombre
        
    lbl_text = f"Numero {num} : {nb_sorties}/{total} ({taux:.1f}%)"
    
    # Rendu HTML sécurisé pour conserver la coloration par numéro
    st.markdown(f'<p style="color:{c_texte}; font-family:Arial; font-size:14px; margin:1px 0px;">{lbl_text}</p>', unsafe_allow_html=True)



# =====================================================================
# 2. DESSIN DU DÉ INDÉPENDANT (Anciennement dessiner_de_independant1)
# =====================================================================
n_faces = int(st.session_state.get("slider_faces_n1_valeur", 6))

# Affichage du sous-titre du dé libre désormais sécurisé
st.subheader(f"JEU 1 : DE LIBRE (A {n_faces} FACES)")

val_de_actuel = st.session_state.get("valeur_de_actuelle1", 1)

# Votre condition d'origine désormais parfaitement sécurisée
if val_de_actuel <= 6:
    # Correspondance textuelle propre pour les faces standards de 1 à 6
    des_unicode = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"}
    symbole_de = des_unicode.get(val_de_actuel, "?")
    
    # Rendu visuel d'un carré blanc avec bordure jaune contenant la valeur
    st.markdown(
        f'<div style="display:inline-block; width:50px; height:50px; line-height:46px; '
        f'text-align:center; background-color:#ffffff; border:2px solid #fbbf24; '
        f'border-radius:6px; color:#1e293b; font-family:Arial; font-size:24px; font-weight:bold;">'
        f'{symbole_de}'
        f'</div>', 
        unsafe_allow_html=True
    )
else:
    # Chiffre numérique brut si la valeur est supérieure à 6
    st.markdown(
        f'<div style="display:inline-block; width:50px; height:50px; line-height:46px; '
        f'text-align:center; background-color:#ffffff; border:2px solid #fbbf24; '
        f'border-radius:6px; color:#1e293b; font-family:Arial; font-size:18px; font-weight:bold;">'
        f'{val_de_actuel}'
        f'</div>', 
        unsafe_allow_html=True
    )


# =====================================================================
# 3. STATISTIQUES DYNAMIQUES (Anciennement actualiser_labels_statistiques_de1)
# =====================================================================
st.write("---")
st.write("Statistiques du dé :")

total = st.session_state.get("total_lancers_de", 0)
# Récupération sécurisée du dictionnaire (renvoie {} s'il n'existe pas)
stats_faces = st.session_state.get("stats_par_face_de", {})

# Génération automatique d'autant de lignes qu'il y a de faces configurées
for face in range(1, n_faces + 1):
    # Lecture dans notre dictionnaire sécurisé
    nb_sorties = stats_faces.get(face, 0)
    taux = (nb_sorties / total * 100) if total > 0 else 0.0
    
    lbl_text = f"Face {face} : {nb_sorties}/{total} ({taux:.1f}%)"
    
    # Rendu HTML fluide avec la couleur violette d'origine #5b21b6
    st.markdown(f'<p style="color:#5b21b6; font-family:Arial; font-size:14px; margin:2px 0px;">{lbl_text}</p>', unsafe_allow_html=True)
# =====================================================================
# 2. SELECTION DYNAMIQUE DU TAPIS (Anciennement actualiser_options_pari_gauche)
# =====================================================================
# Sélecteur principal pour définir le mode (Remplace self.type_pari)
mode = st.selectbox(
    "Type de pari :",
    options=["Couleur", "Parite", "Douzaine", "Manque/Passe", "Numero"],
    key="type_pari_selectionne"
)

# Initialisation par défaut de la combinaison active si elle n'existe pas encore
if "combinaison_active" not in st.session_state:
    st.session_state.combinaison_active = "Rouge"

# Affichage des formulaires conditionnels selon le mode choisi
if mode == "Couleur":
    choix_couleur = st.selectbox("Choisir Couleur :", options=["Rouge", "Noir"])
    st.session_state.combinaison_active = choix_couleur

elif mode == "Parite":
    choix_parite = st.selectbox("Choisir Parite :", options=["Pair", "Impair"])
    # Traduction interne pour correspondre aux mots-clés du vérificateur (Even/Odd)
    st.session_state.combinaison_active = "Even" if choix_parite == "Pair" else "Odd"

elif mode == "Douzaine":
    choix_douzaine = st.selectbox("Choisir Douzaine :", options=["1st 12", "2nd 12", "3rd 12"])
    st.session_state.combinaison_active = choix_douzaine

elif mode == "Manque/Passe":
    choix_intervalle = st.selectbox("Choisir Intervalle :", options=["1-18", "19-36"])
    st.session_state.combinaison_active = choix_intervalle

elif mode == "Numero":
    # Utilisation d'un sélecteur numérique sécurisé borné de 0 à 36
    choix_numero = st.number_input("Choisir Numero (0 a 36) :", min_value=0, max_value=36, value=0)
    st.session_state.combinaison_active = str(choix_numero)


# Affichage de contrôle (Optionnel, utile pour vérifier ce qui est enregistré en mémoire)
st.text(f"Combinaison actuellement enregistrée sur le tapis : {st.session_state.combinaison_active}")

# Curseurs ou paramètres de configuration
n_faces = st.sidebar.number_input("Faces du de :", min_value=2, max_value=100, value=6)


# =====================================================================
# 2. ANIMATION ET LANCER DE DÉ (Anciennement declencher_animation_de1)
# =====================================================================
st.header("Section De Libre")

# Le bouton passe automatiquement en état désactivé durant l'exécution du bloc
if st.button("Lancer le de libre", key="btn_lancer_de1"):
    # Effet visuel d'attente stabilisé (Remplace l'état asynchrone de Tkinter)
    with st.spinner("Calcul de la trajectoire du de..."):
        # Simulation du temps de rotation du dé (1.5 seconde)
        time.sleep(1.5)
        
        # Résultat final et incrémentation des données
        val_de_final = random.randint(1, n_faces)
        st.session_state.total_lancers_de += 1
        
    # Notification du résultat de manière statique après l'animation
    st.success(f"Le de s'est arrete sur la face : {val_de_final}")


st.write("---")


# =====================================================================
# 3. ANIMATION ET SLOT MACHINE (Anciennement declencher_animation_casino1)
# =====================================================================

st.header("Section Slot Machine")

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




# Récupération du nombre de faces configuré par l'utilisateur
n_max = int(st.session_state.get("slider_faces_n1_valeur", 6))


# =====================================================================
# 1. ANIMATION DU DÉ LIBRE (Anciennement faire_tourner_de1 & declencher_animation_de1)
# =====================================================================
st.header("JEU 1 : DE LIBRE")

# Bouton de déclenchement (Streamlit gère nativement le verrouillage anti-double clic pendant l'exécution)
if st.button("Lancer le de libre"    
    # Zone d'affichage dynamique réservée exclusivement pour le dé
    conteneur_de = st.empty()
    
    # Équivalent de la boucle "pas < 12" avec ralentissement progressif (after)
    for pas in range(13):
        valeur_de_actuelle1 = random.randint(1, n_max)
        
        # Rafraîchissement visuel du dé au même emplacement
        with conteneur_de:
            # Appel de la fonction de dessin convertie précédemment
            # dessiner_de_independant1(valeur_de_actuelle1)
            st.text(f"Animation du de... Face temporaire : {valeur_de_actuelle1}")
            
        # Calcul du délai progressif : 40ms + (pas * 15ms) transposé en secondes
        delai = (40 + (pas * 15)) / 1000.0
        time.sleep(delai)
        
    # --- PHASE FINALE : Enregistrement du résultat réel après l'arrêt ---
    st.session_state.total_lancers_de += 1
    st.session_state.stats_par_face_de[valeur_de_actuelle1] += 1
    
    # Ajout du log en haut de la liste (équivalent de insert(0, txt_log))
    num_log = len(st.session_state.historique_logs) + 1
    txt_log = f"Lancer n°{num_log:02d} : Face {valeur_de_actuelle1} est sortie"
    st.session_state.historique_logs.insert(0, txt_log)
    
    # Forcer l'affichage final stabilisé
    with conteneur_de:
        st.success(f"Le de s'est arrete sur la face : {valeur_de_actuelle1}")


# =====================================================================
# 2. DÉCLENCHEMENT DE LA ROULETTE (Anciennement declencher_animation_roue1)
# =====================================================================
st.write("---")
st.header("JEU 2 : ROULETTE")

if st.button("Lancer la roulette", key="btn_lancer_roue1"):
    # Réinitialisation de la pluie de confettis en mémoire tampon
    st.session_state.flocon_confettis = []
    
    # Conteneur d'affichage dynamique dédié à la roulette
    conteneur_roulette = st.empty()
    
    # Appel de votre logique itérative (qui remplacera animer_roue_hasard1)
    # Exemple de boucle de rotation fictive de la roue :
    angle_bille_virtuel = 0.0
    for pas in range(30):
        angle_bille_virtuel = (angle_bille_virtuel + 25.0) % 360
        
        with conteneur_roulette:
            # Appel de la fonction graphique convertie précédemment
            # dessiner_roue_tricolore1(angle_bille_virtuel, "Mouvement")
            st.text(f"Animation de la roue... Angle bille : {angle_bille_virtuel:.1f}°")
        time.sleep(0.05)
        
    with conteneur_roulette:
        st.text("La roue est immobilisee.")


# =====================================================================
# 3. PANNEAU D'AFFICHAGE DE L'HISTORIQUE ET DES LOGS
# =====================================================================
if st.session_state.historique_logs:
    st.write("---")
    st.subheader("Historique des lancers")
    # Affichage du journal des événements sous forme de liste fixe propre
    st.code("\n".join(st.session_state.historique_logs), language="text")

# Récupération sécurisée de la limite de formes (remplace self.slider_shapes_n1.get())
limit_shapes = int(st.session_state.get("slider_shapes_n1_valeur", 7))


# =====================================================================
# LOGIQUE D'ANIMATION ET DE ROTATION (Anciennement faire_tourner_rouleaux1)
# =====================================================================
st.header("JEU 2 : SLOT MACHINE")

# Le bouton gère nativement le blocage anti-double clic durant l'exécution
if st.button("Actionner les rouleaux", key="btn_lancer_casino1"):
    
    # Conteneur d'affichage dynamique réservé exclusivement pour la machine
    conteneur_slot = st.empty()
    
    # Équivalent de la boucle "pas < 15" avec ralentissement progressif
    v1, v2, v3 = 1, 1, 1
    for pas in range(16):
        v1 = random.randint(1, limit_shapes)
        v2 = random.randint(1, limit_shapes)
        v3 = random.randint(1, limit_shapes)
        
        # Rafraîchissement visuel de la machine au même emplacement graphique
        with conteneur_slot:
            # Appel de votre fonction graphique Matplotlib convertie précédemment
            # dessiner_machine_casino1(v1, v2, v3, "")
            st.text(f"Machine en rotation... [{v1}][{v2}][{v3}]")
            
        # Calcul du délai progressif : 40ms + (pas * 15ms) transposé en secondes
        delai = (40 + (pas * 15)) / 1000.0
        time.sleep(delai)
        
    # --- PHASE FINALE : Enregistrement et traitement du résultat réel ---
    if v1 == v2 == v3:
        verdict = "JACKPOT"
    elif v1 == v2 or v2 == v3 or v1 == v3:
        verdict = "GAGNE"
    else:
        verdict = "PERDU"
        
    # Mise à jour des compteurs globaux dans la mémoire persistante
    st.session_state.total_lancers_slot += 1
    if verdict == "JACKPOT":
        st.session_state.cpt_classe_jackpots += 1
    elif verdict == "GAGNE":
        st.session_state.cpt_classe_gagnes += 1
        
    # Enregistrement du log de tirage en haut de la liste (insert(0, txt_log))
    num_log = len(st.session_state.liste_casino_view1) + 1
    txt_log = f"Tirage n°{num_log:02d} : [{v1}][{v2}][{v3}] -> {verdict}"
    st.session_state.liste_casino_view1.insert(0, txt_log)
    
    # Rendu final stabilisé avec le verdict affiché
    with conteneur_slot:
        # dessiner_machine_casino1(v1, v2, v3, verdict)
        st.success(f"Resultat final : [{v1}][{v2}][{v3}] -> {verdict}")
        
    # Déclenche automatiquement la reconstruction de la page
    st.rerun()


# =====================================================================
# AFFICHAGE DE L'HISTORIQUE DE LA SLOT MACHINE
# =====================================================================
if st.session_state.liste_casino_view1:
    st.write("---")
    st.subheader("Historique de la machine a sous")
    st.code("\n".join(st.session_state.liste_casino_view1), language="text")


# =====================================================================
# INTERFACE DE PARI (Remplace la capture de clic sur le tapis graphique)
# =====================================================================
st.subheader("Placer votre jeton sur le tapis")

# 1. Sélection de la grande catégorie de mise
categorie_pari = st.radio(
    "Choisissez la zone du tapis :",
    options=["Chances Simples (Bas)", "Douzaines (Milieu)", "Case Zéro (Gauche)", "Numéro Plein (Centre)"],
    horizontal=True
)

# 2. Traitement des sous-zones (Logique mathématique extraite de vos conditions de coordonnées)
if categorie_pari == "Chances Simples (Bas)":
    # Équivalent de Zone 1
    choix_chance = st.selectbox("Choisir votre chance simple :", ["1-18", "Even", "Rouge", "Noir", "Odd", "19-36"])
    st.session_state.combinaison_active = choix_chance
    
    if choix_chance in ["Rouge", "Noir"]:
        st.session_state.type_pari = "Couleur"
    elif choix_chance in ["Even", "Odd"]:
        st.session_state.type_pari = "Parite"
    else:
        st.session_state.type_pari = "Manque/Passe"

elif categorie_pari == "Douzaines (Milieu)":
    # Équivalent de Zone 2
    choix_douzaine = st.selectbox("Choisir la douzaine :", ["1st 12", "2nd 12", "3rd 12"])
    st.session_state.combinaison_active = choix_douzaine
    st.session_state.type_pari = "Douzaine"

elif categorie_pari == "Case Zéro (Gauche)":
    # Équivalent de Zone 3
    st.session_state.combinaison_active = "0"
    st.session_state.type_pari = "Numero"
    st.info("Jeton posé sur le 0 Vert.")

elif categorie_pari == "Numéro Plein (Centre)":
    # Équivalent de Zone 4 (La grille des 36 numéros)
    numero_devine = st.number_input("Saisir un numéro (1 à 36) :", min_value=1, max_value=36, value=1, step=1)
    st.session_state.combinaison_active = str(numero_devine)
    st.session_state.type_pari = "Numero"

# =====================================================================
# RENDER ET RACCORDEMENT (Anciennement actualiser_options_pari_gauche)
# =====================================================================
st.write("---")
st.text(f"Type de pari détecté : {st.session_state.type_pari}")
st.text(f"Combinaison active enregistree : {st.session_state.combinaison_active}")
# =====================================================================
# INTERFACE DYNAMIQUE (Anciennement actualiser_options_pari_gauche)
# =====================================================================
# 1. Sélection principale du type de pari (Équivalent de mode = self.type_pari.get())
mode = st.selectbox(
    "Type de pari :",
    options=["Couleur", "Parite", "Douzaine", "Manque/Passe", "Numero"],
    index=["Couleur", "Parite", "Douzaine", "Manque/Passe", "Numero"].index(st.session_state.type_pari),
    key="select_type_pari"
)
st.session_state.type_pari = mode

# =====================================================================
# INTERFACE DYNAMIQUE (Vérifiez l'alignement de ce bloc vers la ligne 1480)
# =====================================================================
if mode == "Couleur":
    choix_coul = st.selectbox("Choisir Couleur :", options=["Rouge", "Noir"])
    st.session_state.combinaison_active = choix_coul

elif mode == "Parite":
    choix_par = st.selectbox("Choisir Parite :", options=["Pair", "Impair"])
    st.session_state.combinaison_active = "Even" if choix_par == "Pair" else "Odd"

elif mode == "Douzaine":
    choix_douz = st.selectbox("Choisir Douzaine :", options=["1st 12", "2nd 12", "3rd 12"])
    st.session_state.combinaison_active = choix_douz

elif mode == "Manque/Passe":
    choix_mp = st.selectbox("Choisir Intervalle :", options=["1-18", "19-36"])
    st.session_state.combinaison_active = choix_mp

elif mode == "Numero":
    choix_num = st.selectbox("Choisir Numero (0 a 36) :", options=list(range(0, 37)))
    st.session_state.combinaison_active = str(choix_num)

# =====================================================================
# LIGNE 1486 : LE TITRE DE L'EXERCICE (Revenez bien aligné tout à gauche)
# =====================================================================
st.header("Exercice : Texte a trous de probabilites")

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
st.header("Evaluation : Quiz sur les probabilites")

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


# =====================================================================
# LOGIQUE DE CORRECTION ET SÉCURITÉ (Anciennement valider_tout1)
# =====================================================================
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


# =====================================================================
# INTÉGRATION COMPOSANTS ET DISPOSITIF ANTI-TRICHE
# =====================================================================
# Remplacement de l'alerte askyesno par une case à cocher de confirmation native
if not st.session_state.quiz_deja_valide:
    
    confirmation_soumission = st.checkbox(
        "Je confirme vouloir valider definitivement mes reponses (aucun retour en arriere possible)."
    )
    
    # Le bouton s'affiche mais reste inactif tant que la case n'est pas cochée
    st.button(
        "Valider l'Atelier 1", 
        key="btn_valider1", 
        disabled=not confirmation_soumission,
        on_click=valider_tout1
    )
else:
    # Le bouton passe en état désactivé permanent une fois le quiz soumis
    st.button("Atelier déjà validé et verrouillé", key="btn_valider1_desactive", disabled=True)
    
    # Rappel persistant de la note obtenue en haut du module verrouillé
    st.info(f"Évaluation clôturée pour cet utilisateur. Note enregistrée : {st.session_state.score_final_quiz} / 10")

st.subheader("Parametres du Mode Examen")

# 1. Vérification de l'identité de l'élève stockée à l'accueil
nom_eleve = str(st.session_state.get("nom_utilisateur", "")).strip().upper()
identite_invalide = nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]

# 2. Dispositif de la case à cocher
if identite_invalide:
    # Si le nom est manquant, on affiche une case décorative désactivée et un message d'erreur
    st.checkbox("Activer le Mode Examen", value=False, disabled=True, key="chk_examen_bloque")
    st.error("Saisie obligatoire : Veuillez d'abord renseigner et valider votre identite sur l'onglet d'accueil.")
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























