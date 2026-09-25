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
    col_de_gauche, col_carte_gauche = st.columns(2)

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


with tab2:


    st.header("2. Jeux de hasard 2 : Roulette et Slot Machine")

    # =========================================================================
    # INITIALISATION SÉCURISÉE DES MÉMOIRES DE SESSION (ATELIER 2)
    # =========================================================================
    if "roulette_choix_pari" not in st.session_state:
        st.session_state.roulette_choix_pari = "Rouge"
    if "roulette_dernier_numero" not in st.session_state:
        st.session_state.roulette_dernier_numero = None
    if "roulette_derniere_couleur" not in st.session_state:
        st.session_state.roulette_derniere_couleur = None
    if "roulette_stats_gains" not in st.session_state:
        st.session_state.roulette_stats_gains = {"GAGNE": 0, "PERDU": 0}
    if "slot_dernier_tirage" not in st.session_state:
        st.session_state.slot_dernier_tirage = []
    if "slot_verdict" not in st.session_state:
        st.session_state.slot_verdict = None
    if "roulette_stats_gains" not in st.session_state:
        st.session_state.roulette_stats_gains = {"GAGNE": 0, "PERDU": 0}
    # =========================================================================
    # DISTRIBUTION EN DEUX GRANDES COLONNES PRINCIPALES
    # =========================================================================
    col_master_roulette, col_master_slot = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LA ROULETTE INTERACTIVE
    # -------------------------------------------------------------------------
    with col_master_roulette:
        st.subheader("La Roulette de Casino")
        st.write("Misez sur une categorie ou sur un numero unique :")

        # 1. RECUPERATION ET FORCE DES DROITS DE MISE
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

        # 2. RENDU EN HAUT : LE GRAND TAPIS DE JEU ALIGNÉ ET SA CELLULE JETON
        # On définit une largeur bloquée à 680px pour empêcher le navigateur d'écraser la grille
        html_tapis_regle = f"""
        <div style="background-color: #065f46; border: 4px solid #ffffff; border-radius: 8px; width: 680px; padding: 15px; font-family: Arial, sans-serif; box-shadow: 0 8px 16px rgba(0,0,0,0.3); margin-bottom: 20px;">
            <div style="text-align: center; color: #ffffff; font-size: 16px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px;">
                Tapis des Mises de la Roulette
            </div>
            
            <!-- Structure simplifiée et robuste du quadrillage réglementaire -->
            <table style="width: 100%; border-collapse: collapse; text-align: center; color: #ffffff; font-weight: bold;">
                <tr style="height: 40px;">
                    <td rowspan="3" style="background-color: #16a34a; border: 2px solid #ffffff; width: 50px; font-size: 20px;">0</td>
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
                <tr style="height: 40px;">
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
                <tr style="height: 40px;">
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
                <tr style="height: 35px; font-size: 13px;">
                    <td></td>
                    <td colspan="4" style="border: 2px solid #ffffff;">1st 12</td>
                    <td colspan="4" style="border: 2px solid #ffffff;">2nd 12</td>
                    <td colspan="4" style="border: 2px solid #ffffff;">3rd 12</td>
                </tr>
                <tr style="height: 35px; font-size: 12px;">
                    <td></td>
                    <td colspan="2" style="border: 2px solid #ffffff;">1-18</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">EVEN</td>
                    <td colspan="2" style="background-color: #dc2626; border: 2px solid #ffffff; color: #ffffff;">ROUGE</td>
                    <td colspan="2" style="background-color: #0f172a; border: 2px solid #ffffff; color: #ffffff;">NOIR</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">ODD</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">19-36</td>
                </tr>
            </table>

            <!-- LA CASE JETON : Elle affiche dynamiquement le choix du pari au bas du tapis -->
            <div style="text-align: center; margin-top: 15px;">
                <span style="background-color: #f59e0b; color: #0f172a; padding: 6px 20px; border-radius: 4px; font-size: 13px; font-weight: bold; border: 2px solid #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    JETON ACTUEL : {texte_jeton.upper()}
                </span>
            </div>
        </div>
        """
        st.components.v1.html(html_tapis_regle, height=265)

        # 3. INTERFACE DE COMMANDE DE TIRAGE UNITAIRE
        if st.button("LANCER LA ROULETTE ET LA BILLE", key="btn_lancer_roulette_officiel_at2", use_container_width=True):
            with st.spinner("La roulette tourne... La bille ralentit..."):
                placeholder_bille = st.empty()
                mouvements_couleurs = ["#dc2626", "#0f172a", "#16a34a", "#dc2626", "#0f172a"]
                mouvements_textes = ["32 (Rouge)", "15 (Noir)", "0 (Vert)", "19 (Rouge)", "4 (Noir)"]
                
                for idx_m in range(5):
                    # On affecte proprement la couleur courante de l'animation
                    bg_anim = mouvements_couleurs[idx_m]
                    txt_anim = mouvements_textes[idx_m]
                    
                    html_anim_r = f"""
                    <div style='display: flex; justify-content: center; width: 680px;'>
                        <div style='background-color: {bg_anim}; border: 4px solid #f59e0b; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 8px rgba(0,0,0,0.4); color: #ffffff; font-weight: bold; font-family: Arial; font-size: 14px;'>
                            {txt_anim}
                        </div>
                    </div>
                    """
                    with placeholder_bille: 
                        st.components.v1.html(html_anim_r, height=115)
                    time.sleep(0.12)
                
                placeholder_bille.empty()

            numero_tire = random.randint(0, 36)
            st.session_state.roulette_dernier_numero = numero_tire
            rouges_roulette = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            couleur_finale = "Vert" if numero_tire == 0 else ("Rouge" if numero_tire in rouges_roulette else "Noir")
            st.session_state.roulette_derniere_couleur = couleur_finale

            victoire = False
            if type_pari == "Categorie":
                if pari_selectionne == "Rouge" and couleur_finale == "Rouge": victoire = True
                elif pari_selectionne == "Noir" and couleur_finale == "Noir": victoire = True
                elif pari_selectionne == "Pair (Even)" and numero_tire != 0 and numero_tire % 2 == 0: victoire = True
                elif pari_selectionne == "Impair (Odd)" and numero_tire % 2 != 0: victoire = True
                elif pari_selectionne == "Manque (1-18)" and 1 <= numero_tire <= 18: victoire = True
                elif pari_selectionne == "Passe (19-36)" and 19 <= numero_tire <= 36: victoire = True
            else:
                if numero_tire == numero_choisi: victoire = True

            if victoire:
                st.session_state.roulette_stats_gains["GAGNE"] += 1
                st.session_state.roulette_verdict_texte = f"GAGNE ! (+ {35 if type_pari != 'Categorie' else 1} jetons)"
                log_texte = f"Roulette : Mise sur {pari_selectionne} - Tirage : {numero_tire} ({couleur_finale}) -> GAGNE"
            else:
                st.session_state.roulette_stats_gains["PERDU"] += 1
                st.session_state.roulette_verdict_texte = "PERDU"
                log_texte = f"Roulette : Mise sur {pari_selectionne} - Tirage : {numero_tire} ({couleur_finale}) -> PERDU"

            if "historique_logs" not in st.session_state:
                st.session_state.historique_logs = []
            st.session_state.historique_logs.append(log_texte)
            
            st.rerun()

        # 4. EN DESSOUS : RENDU DE LA ROUE FIXE QUAND LA BILLE S'EST ARRETÉE
        if st.session_state.roulette_dernier_numero is not None:
            num = st.session_state.roulette_dernier_numero
            c_c = st.session_state.roulette_derniere_couleur
            verdict = st.session_state.get("roulette_verdict_texte", "")
            bg_cylindre = "#dc2626" if c_c == "Rouge" else ("#0f172a" if c_c == "Noir" else "#16a34a")
            
            html_roue_fixe = f"""
            <div style='display: flex; flex-direction: column; align-items: center; width: 680px; margin-top: 15px; font-family: Arial, sans-serif;'>
                <div style='background-color: {bg_cylindre}; border: 6px double #f59e0b; border-radius: 50%; width: 130px; height: 130px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 6px 12px rgba(0,0,0,0.4); text-align: center; color: #ffffff;'>
                    <span style='font-size: 10px; text-transform: uppercase; font-weight: bold; color: #f59e0b; letter-spacing: 0.5px;'>Bille</span>
                    <span style='font-size: 38px; font-weight: bold; line-height: 1.1;'>{num}</span>
                    <span style='font-size: 12px; font-weight: bold;'>{c_c.upper()}</span>
                </div>
                <div style='text-align: center; font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px;'>
                    RESULTAT DU TOUR : {verdict}
                </div>
            </div>
            """
            st.components.v1.html(html_roue_fixe, height=190)

                


        if st.button("LANCER LA ROULETTE ET LA BILLE", key="btn_lancer_roulette_officiel_at2", use_container_width=True):
            with st.spinner("Le cylindre tourne... La bille circule..."):
                placeholder_bille = st.empty()
                mouvements_couleurs = ["#dc2626", "#0f172a", "#16a34a", "#dc2626", "#0f172a"]
                mouvements_textes = ["32 (Rouge)", "15 (Noir)", "0 (Vert)", "19 (Rouge)", "4 (Noir)"]
                
                for idx_m in range(5):
                    bg_anim = mouvements_couleurs[idx_m]
                    txt_anim = mouvements_textes[idx_m]
                    html_anim_r = f"""
                    <div style='display: flex; justify-content: center; margin: 15px 0;'>
                        <div style='background-color: {bg_anim}; border: 5px solid #f59e0b; border-radius: 50%; width: 120px; height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); text-align: center; color: #ffffff;'>
                            <span style='font-family: Arial, sans-serif; font-size: 11px; font-weight: bold; color: #f59e0b;'>ROTATION...</span>
                            <span style='font-family: Arial, sans-serif; font-size: 15px; font-weight: bold;'>{txt_anim}</span>
                        </div>
                    </div>
                    """
                    with placeholder_bille: st.components.v1.html(html_anim_r, height=140)
                    time.sleep(0.12)
                placeholder_bille.empty()

            numero_tire = random.randint(0, 36)
            st.session_state.roulette_dernier_numero = numero_tire
            rouges_officiels = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            couleur_finale = "Vert" if numero_tire == 0 else ("Rouge" if numero_tire in rouges_officiels else "Noir")
            st.session_state.roulette_derniere_couleur = couleur_finale

            victoire = False
            if type_pari == "Miser sur une Categorie":
                if pari_selectionne == "Rouge" and couleur_finale == "Rouge": victoire = True
                elif pari_selectionne == "Noir" and couleur_finale == "Noir": victoire = True
                elif pari_selectionne == "Pair (Even)" and numero_tire != 0 and numero_tire % 2 == 0: victoire = True
                elif pari_selectionne == "Impair (Odd)" and numero_tire % 2 != 0: victoire = True
                elif pari_selectionne == "Manque (1-18)" and 1 <= numero_tire <= 18: victoire = True
                elif pari_selectionne == "Passe (19-36)" and 19 <= numero_tire <= 36: victoire = True
            else:
                if numero_tire == numero_choisi: victoire = True

            if victoire:
                st.session_state.roulette_stats_gains["GAGNE"] += 1
                st.session_state.roulette_verdict_texte = f"GAGNE ! (+ {35 if type_pari != 'Miser sur une Categorie' else 1} jetons)"
            else:
                st.session_state.roulette_stats_gains["PERDU"] += 1
                st.session_state.roulette_verdict_texte = "PERDU"
            st.rerun()

        # RENDU DU CYLINDRE FIXE QUAND LA BILLE S'EST ARRETEE DANS SA CASE
        if st.session_state.roulette_dernier_numero is not None:
            num = st.session_state.roulette_dernier_numero
            c_c = st.session_state.roulette_derniere_couleur
            verdict = st.session_state.get("roulette_verdict_texte", "")
            bg_cylindre = "#dc2626" if c_c == "Rouge" else ("#0f172a" if c_c == "Noir" else "#16a34a")
            
            html_roue_fixe = f"""
            <div style='display: flex; justify-content: center; margin: 15px 0;'>
                <div style='background-color: {bg_cylindre}; border: 6px double #f59e0b; border-radius: 50%; width: 140px; height: 140px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(0,0,0,0.5); text-align: center; color: #ffffff;'>
                    <span style='font-family: Arial, sans-serif; font-size: 10px; text-transform: uppercase; font-weight: bold; color: #f59e0b;'>Bille calee</span>
                    <span style='font-family: Arial, sans-serif; font-size: 42px; font-weight: bold; line-height: 1.1;'>{num}</span>
                    <span style='font-family: Arial, sans-serif; font-size: 13px; font-weight: bold; letter-spacing: 0.5px;'>{c_c.upper()}</span>
                </div>
            </div>
            <div style='text-align: center; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; color: #ffffff;'>
                RESULTAT DU TOUR : {verdict}
            </div>
            """
            st.components.v1.html(html_roue_fixe, height=205)

        # 10 000 LANCERS PAR RAPPORT AU PARI SÉLECTIONNÉ
        st.write("---")
        st.markdown("**Simulation de masse (10 000 lancers) :**")
        if type_pari == "Miser sur une Categorie":
            texte_pari_sim = f"la categorie '{pari_selectionne}'"
        else:
            texte_pari_sim = f"le Numero unique {numero_choisi}"

        if st.button("Lancer la simulation (10 000 Roulettes)", key="btn_sim_10000_roulette"):
            n_sim = 10000
            cpt_victoires = 0
            p_theorique = 18.0 / 37.0 if type_pari == "Miser sur une Categorie" else 1.0 / 37.0
            rouges_list = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

            for _ in range(n_sim):
                tirage = random.randint(0, 36)
                victoire_sim = False
                if type_pari == "Miser sur une Categorie":
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

            f_gagne = cpt_victoires / n_sim
            f_perdu = (n_sim - cpt_victoires) / n_sim

            fig_sim_r, ax_sim_r = plt.subplots(figsize=(4.5, 3), dpi=100)
            ax_sim_r.bar(["GAGNE", "PERDU"], [f_gagne, f_perdu], color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
            ax_sim_r.axhline(y=p_theorique, color="#ef4444", linestyle="--", label=f"Theorie Gagne ({p_theorique*100:.2f}%)")
            ax_sim_r.set_title("Convergence Loi des Grands Nombres", fontsize=9, fontweight="bold")
            ax_sim_r.set_ylabel("Frequence observee")
            ax_sim_r.set_ylim(0, 1.1)
            ax_sim_r.legend(loc="upper right", fontsize=7)
            ax_sim_r.grid(axis="y", linestyle=":", alpha=0.5)
            plt.tight_layout()
            
            st.pyplot(fig_sim_r, clear_figure=True)
            st.write(f"Frequence reelle obtenue : **{f_gagne*100:.2f}%** ({cpt_victoires} victoires).")


                
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
















