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
    "3. Tableau de proportionnalités",
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

        # =========================================================================
        # STRUCTURE EN DEUX COLONNES MAITRESSES : QUIZ A GAUCHE | TEXTE A DROITE

    st.write("---")
    col_maitre_quiz, col_maitre_trous = st.columns(2)

        # -------------------------------------------------------------------------
        # COLONNE DE GAUCHE : LE QUIZ THEORIQUE DE 10 QUESTIONS MELEES
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
                    {"id": "q6", "q": "Question 6 : Si on tire le 7 de Pique, cet evenement est qualifie d'evenement :", "opts": ["Choisir...", "Impossible", "Certain", "Elementaire", "Compose"]},
                    {"id": "q7", "q": "Question 7 : Quelle est la probabilite d'obtenir un multiple de 3 (3 ou 6) sur le de :", "opts": ["Choisir...", "1/6", "2/6 (1/3)", "3/6", "4/6"]},
                    {"id": "q8", "q": "Question 8 : Quelle est la probabilite de tirer soit un Roi soit un As dans le jeu de 32 cartes :", "opts": ["Choisir...", "2/32", "4/32", "8/32 (1/4)", "12/32"]},
                    {"id": "q9", "q": "Question 9 : Un de a 6 faces est truque pour que le 6 sorte plus souvent. La somme des probabilites vaut :", "opts": ["Choisir...", "0.5", "1", "2", "6"]},
                    {"id": "q10", "q": "Question 10 : Si la probabilite d'un evenement A est 0.3, celle de son evenement contraire est :", "opts": ["Choisir...", "0", "0.3", "0.7", "1"]}
                ]
                random.shuffle(st.session_state.banque_quiz_at1)

            dict_reponses_quiz = {}
            for item_quiz in st.session_state.banque_quiz_at1:
                choix_quiz = st.selectbox(
                    label=item_quiz["q"], 
                    options=item_quiz["opts"], 
                    index=0, 
                    key=f"col_g_quiz_{item_quiz['id']}"
                )
                dict_reponses_quiz[item_quiz["id"]] = choix_quiz

            # Extraction ordonnee pour les anciennes variables d'exportation
            quest_1 = dict_reponses_quiz.get("q1", "Choisir...")
            quest_2 = dict_reponses_quiz.get("q2", "Choisir...")
            quest_3 = dict_reponses_quiz.get("q3", "Choisir...")
            quest_4 = dict_reponses_quiz.get("q4", "Choisir...")
            quest_5 = dict_reponses_quiz.get("q5", "Choisir...")
            quest_6 = dict_reponses_quiz.get("q6", "Choisir...")
            quest_7 = dict_reponses_quiz.get("q7", "Choisir...")
            quest_8 = dict_reponses_quiz.get("q8", "Choisir...")
            quest_9 = dict_reponses_quiz.get("q9", "Choisir...")
            quest_10 = dict_reponses_quiz.get("q10", "Choisir...")

        # -------------------------------------------------------------------------
        # COLONNE DE DROITE : LE TEXTE A TROUS (MENUS DEROULANTS MELES)
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

            dict_reponses_trous = {}
            for item_trous in st.session_state.banque_trous_at1:
                choix_eleve = st.selectbox(
                    label=item_trous["label"], 
                    options=item_trous["options"], 
                    index=0, 
                    key=f"col_d_trous_{item_trous['id']}"
                )
                dict_reponses_trous[item_trous["id"]] = choix_eleve

            # Extraction ordonnee pour les anciennes variables d'exportation
            trous_1 = dict_reponses_trous.get("t1")
            trous_2 = dict_reponses_trous.get("t2")
            trous_3 = dict_reponses_trous.get("t3")
            trous_4 = dict_reponses_trous.get("t4")
            trous_5 = dict_reponses_trous.get("t5")
            trous_6 = dict_reponses_trous.get("t6")
            trous_7 = dict_reponses_trous.get("t7")
            trous_8 = dict_reponses_trous.get("t8")
            trous_9 = dict_reponses_trous.get("t9")
            trous_10 = dict_reponses_trous.get("t10")
            
        # =========================================================================
        # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML)
        # =========================================================================
            st.write("---")
            st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

            # Case de certification obligatoire de l'élève
            case_certif_at1 = st.checkbox("Je certifie avoir complete l'integralite des questionnaires de cet atelier.", key="check_certif_at1_officiel")

            if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_at1_premium", use_container_width=True):
                if not st.session_state.get("verrouille", False):
                    st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
                elif not case_certif_at1:
                    st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
                else:
                    # 1. RÉCUPÉRATION DES IDENTIFIANTS DE L'ONGLET 0 ET DU TIMING
                    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
                    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
                    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
                    timestamp_at1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

                    # 2. MOTEUR DE NOTATION DE L'ATELIER 1 (RÉFÉRENTIEL SUR 20 POINTS)
                    # Correction de la Partie 2 : Le Quiz QCM
                    score_quiz = 0
                    verdicts_quiz = {}
                    attendus_quiz = {
                        "q1": "0.75", "q2": "3/6 (1/2)", "q3": "12/32 (3/8)", "q4": "5/6", "q5": "0 et 1",
                        "q6": "Elementaire", "q7": "2/6 (1/3)", "q8": "8/32 (1/4)", "q9": "1", "q10": "0.7"
                    }
                    for q_id, q_correct in attendus_quiz.items():
                        saisie_q = dict_reponses_quiz.get(q_id, "Choisir...")
                        if saisie_q == q_correct:
                            score_quiz += 1
                            verdicts_quiz[q_id] = "CORRECT"
                        else:
                            verdicts_quiz[q_id] = "INCORRECT"

                    # Correction de la Partie 3 : Les Menus Déroulants
                    score_trous = 0
                    verdicts_trous = {}
                    attendus_trous = {
                        "t1": "6", "t2": "1/6", "t3": "32", "t4": "4", "t5": "8",
                        "t6": "4/32 (1/8)", "t7": "8/32 (1/4)", "t8": "Certain", "t9": "Impossible", "t10": "1"
                    }
                    for t_id, t_correct in attendus_trous.items():
                        saisie_t = dict_reponses_trous.get(t_id, "Choisir...")
                        if saisie_t == t_correct:
                            score_trous += 1
                            verdicts_trous[t_id] = "CORRECT"
                        else:
                            verdicts_trous[t_id] = "INCORRECT"

                    note_finale_sur_20 = score_quiz + score_trous

                    # 3. CONVERSION ET CODES DESIGN HTML POUR RETROUVER LE RENDU EXACT DE LA PHOTO
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
                                <th style="width: 150px;">Saisie Eleve</th>
                                <th style="width: 120px;">Valeur Attendue</th>
                                <th style="width: 120px; text-align: center;">Verdict</th>
                            </tr>
                    """

                    # Génération des lignes QCM du tableau HTML
                    questions_mapping = {
                        "q1": "Chances 3 sur 4", "q2": "Probabilite Nombre pair au de",
                        "q3": "Probabilite d'obtenir une Figure", "q4": "Evenement contraire d'obtenir 6",
                        "q5": "Bornes d'une probabilite", "q6": "Nature de l'evenement 7 de Pique",
                        "q7": "Multiple de 3 avec le de cubique", "q8": "Tirer un Roi OU un As",
                        "q9": "De truque : Somme totale des probas", "q10": "Evenement contraire de P(A) = 0.3"
                    }
                    for idx_q, q_key in enumerate(["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10"], 1):
                        saisie = dict_reponses_quiz.get(q_key, "Choisir...")
                        attendu = attendus_quiz[q_key]
                        v_class = "status-correct" if verdicts_quiz[q_key] == "CORRECT" else "status-incorrect"
                        html_export_premium += f"""
                            <tr>
                                <td>{idx_q}</td>
                                <td>{questions_mapping[q_key]}</td>
                                <td>{saisie}</td>
                                <td>{attendu}</td>
                                <td class="{v_class}" style="text-align: center;">{verdicts_quiz[q_key]}</td>
                            </tr>
                        """

                    html_export_premium += """
                        </table>

                        <div class="sub-title">Partie 3 : Synthese de cours (Texte a trous)</div>
                        <table>
                            <tr>
                                <th style="width: 50px;">N°</th>
                                <th>Emplacement de l'Analyse (Texte a trous)</th>
                                <th style="width: 150px;">Saisie Eleve</th>
                                <th style="width: 120px;">Valeur Attendue</th>
                                <th style="width: 120px; text-align: center;">Verdict</th>
                            </tr>
                    """

                    # Génération des lignes Texte à trous du tableau HTML
                    trous_mapping = {
                        "t1": "Nombre de faces du de cubique", "t2": "Probabilite d'obtenir le chiffre 6",
                        "t3": "Nombre total de cartes dans le paquet", "t4": "Nombre de couleurs dans le jeu",
                        "t5": "Nombre de cartes par couleur", "t6": "Probabilite theorique d'un As",
                        "t7": "Probabilite theorique d'un Coeur", "t8": "Nom d'un evenement de probabilite 1",
                        "t9": "Nom d'un evenement de probabilite 0", "t10": "Somme des probabilites totales"
                    }
                    for idx_t, t_key in enumerate(["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10"], 1):
                        saisie = dict_reponses_trous.get(t_key, "Choisir...")
                        attendu = attendus_trous[t_key]
                        v_class = "status-correct" if verdicts_trous[t_key] == "CORRECT" else "status-incorrect"
                        html_export_premium += f"""
                            <tr>
                                <td>{idx_t}</td>
                                <td>{trous_mapping[t_key]}</td>
                                <td>{saisie}</td>
                                <td>{attendu}</td>
                                <td class="{v_class}" style="text-align: center;">{verdicts_trous[t_key]}</td>
                            </tr>
                        """

                    html_export_premium += f"""
                        </table>
                        <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                            Document officiel de correction numerique genere automatiquement &bull; Professeur Laurent GALLET
                        </div>
                    </body>
                    </html>
                    """

                    # Scellé définitif de la page en mémoire de session
                    st.session_state.atelier1_valide = True
                    
                    st.success(f"Bilan HTML genere avec succes pour {p_eleve} {n_eleve} !")
                    st.info(f"Note finale de l'eleve : {note_finale_sur_20} / 20")
                    
                    # Déclenchement du vrai bouton de téléchargement au format de votre choix (.html)
                    st.download_button(
                        label="TELECHARGER LE RAPPORT INTERACTIF ATELIER 1 (.HTML)",
                        data=html_export_premium,
                        file_name=f"Rapport_Atelier1_{n_eleve}.html",
                        mime="text/html",
                        use_container_width=True
                    )




                    
with tab2:


    st.header("2. Jeux de hasard 2 : Roulette et Casino Machine")

    # =========================================================================
    # INITIALISATION UNIFIEE DES MEMOIRES DE SESSION
    # =========================================================================
    if "roulette_stats_gains" not in st.session_state:
        st.session_state.roulette_stats_gains = {"GAGNE": 0, "PERDU": 0}
    if "roulette_dernier_numero" not in st.session_state:
        st.session_state.roulette_dernier_numero = None
    if "roulette_derniere_couleur" not in st.session_state:
        st.session_state.roulette_derniere_couleur = None
    if "slot_dernier_tirage" not in st.session_state:
        st.session_state.slot_dernier_tirage = []
    if "slot_verdict" not in st.session_state:
        st.session_state.slot_verdict = None
    if "slot_stats_gains" not in st.session_state:
        st.session_state.slot_stats_gains = {"JACKPOT": 0, "PETIT GAIN": 0, "PERDU": 0}
    if "roulette_dernier_numero" not in st.session_state:
        st.session_state.roulette_dernier_numero = 0
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
        
        # Détermination dynamique du texte explicatif selon le type de pari actif
        if type_pari == "Categorie":
            texte_pari_sim = f"la categorie '{pari_selectionne}'"
        else:
            texte_pari_sim = f"le Numero unique {numero_choisi}"
            
        st.write(f"Ce simulateur va tester 10 000 lancers consecutifs sur {texte_pari_sim}.")

        if st.button("Lancer la simulation (10 000 Roulettes)", key="btn_sim_10000_roulette_maitre", use_container_width=True):
            n_sim = 10000
            cpt_victoires = 0
            
            # Calcul de la probabilité théorique exacte pour la ligne de repère rouge
            p_theorique = 18.0 / 37.0 if type_pari == "Categorie" else 1.0 / 37.0
            
            # Liste officielle des 18 numéros rouges de la roulette européenne
            rouges_list = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

            # Boucle mathématique de Bernoulli ultra-rapide
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

            # Calcul des fréquences observées
            f_gagne = cpt_victoires / n_sim
            f_perdu = (n_sim - cpt_victoires) / n_sim

            # Tracé du graphique de convergence de la Loi des Grands Nombres
            fig_sim_r, ax_sim_r = plt.subplots(figsize=(4, 2.5), dpi=100)
            ax_sim_r.bar(["GAGNE", "PERDU"], [f_gagne, f_perdu], color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
            ax_sim_r.axhline(y=p_theorique, color="#ef4444", linestyle="--", label=f"Theorie ({p_theorique*100:.1f}%)")
            
            ax_sim_r.set_title("Convergence Loi des Grands Nombres", fontsize=9, fontweight="bold")
            ax_sim_r.set_ylabel("Frequence observee")
            ax_sim_r.set_ylim(0, 1.1)
            ax_sim_r.legend(loc="upper right", fontsize=7)
            ax_sim_r.grid(axis="y", linestyle=":", alpha=0.5)
            plt.tight_layout()
            
            st.pyplot(fig_sim_r, clear_figure=True)
            st.write(f"Resultat de la simulation : **{cpt_victoires} victoires** obtenues (Frequence reelle : **{f_gagne*100:.2f}%**).")

           
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
















