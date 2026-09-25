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

    # =========================================================================
    # DISTRIBUTION EN DEUX GRANDES COLONNES PRINCIPALES
    # =========================================================================
    col_master_roulette, col_master_slot = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LA ROULETTE INTERACTIVE
    # -------------------------------------------------------------------------
    with col_master_roulette:
        st.subheader("La Roulette de Casino")
        st.write("Choisissez votre pari sur le tapis ci-dessous :")

        # Rendu du tapis de mise interactif
        pari_selectionne = st.radio(
            "Tapis de mise (Placez votre jeton) :",
            options=["Rouge", "Noir", "Pair (Even)", "Impair (Odd)", "Manque (1-18)", "Passe (19-36)", "Numero 0"],
            horizontal=False,
            key="radio_pari_roulette"
        )
        st.session_state.roulette_choix_pari = pari_selectionne

        # Affichage visuel du jeton posé sur le tapis
        st.markdown(
            f"""
            <div style="background-color: #065f46; border: 3px solid #f59e0b; border-radius: 8px; padding: 10px; text-align: center; color: #ffffff; font-weight: bold; margin-bottom: 15px;">
                TAPIS : [JETON] place sur {st.session_state.roulette_choix_pari}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Lancer la Roulette et la Bille", key="btn_lancer_roulette_at2"):
            with st.spinner("La roulette tourne... La bille ralentit..."):
                placeholder_roulette = st.empty()
                # Simulation visuelle du mouvement textuel
                mouvements = ["Numero 32 (Noir)...", "Numero 15 (Rouge)...", "Numero 0 (Vert)...", "Numero 4 (Noir)..."]
                for m in mouvements:
                    placeholder_roulette.markdown(
                        f"""
                        <div style="border: 2px dashed #f59e0b; padding: 15px; text-align: center; font-style: italic; color: #b45309;">
                            {m}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(0.15)
                placeholder_roulette.empty()

            # Tirage réel de la roulette européenne (0 à 36)
            numero_tire = random.randint(0, 36)
            st.session_state.roulette_dernier_numero = numero_tire

            # Détermination de la couleur
            rouges = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            if numero_tire == 0:
                couleur_finale = "Vert"
            else:
                couleur_finale = "Rouge" if numero_tire in rouges else "Noir"
            st.session_state.roulette_derniere_couleur = couleur_finale

            # Analyse des conditions de victoire
            victoire = False
            if pari_selectionne == "Rouge" and couleur_finale == "Rouge": victoire = True
            elif pari_selectionne == "Noir" and couleur_finale == "Noir": victoire = True
            elif pari_selectionne == "Pair (Even)" and numero_tire != 0 and numero_tire % 2 == 0: victoire = True
            elif pari_selectionne == "Impair (Odd)" and numero_tire % 2 != 0: victoire = True
            elif pari_selectionne == "Manque (1-18)" and 1 <= numero_tire <= 18: victoire = True
            elif pari_selectionne == "Passe (19-36)" and 19 <= numero_tire <= 36: victoire = True
            elif pari_selectionne == "Numero 0" and numero_tire == 0: victoire = True

            if victoire:
                st.session_state.roulette_stats_gains["GAGNE"] += 1
                st.session_state.roulette_verdict_texte = "GAGNE !"
            else:
                st.session_state.roulette_stats_gains["PERDU"] += 1
                st.session_state.roulette_verdict_texte = "PERDU"
            st.rerun()

        # Rendu visuel de la bille immobilisée
        if st.session_state.roulette_dernier_numero is not None:
            num = st.session_state.roulette_dernier_numero
            c_c = st.session_state.roulette_derniere_couleur
            bg_color = "#dc2626" if c_c == "Rouge" else ("#0f172a" if c_c == "Noir" else "#16a34a")
            verdict = st.session_state.get("roulette_verdict_texte", "")
            
            st.markdown(
                f"""
                <div style="background-color: {bg_color}; border: 4px solid #f59e0b; border-radius: 12px; padding: 20px; text-align: center; color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <span style="font-size: 14px; font-weight: bold; text-transform: uppercase;">La bille s'est arretee :</span><br>
                    <span style="font-size: 40px; font-weight: bold;">{num} ({c_c})</span><br>
                    <span style="font-size: 18px; font-weight: bold; letter-spacing: 1px;">VERDICT : {verdict}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Tracé de l'histogramme de répartition des gains mis à jour en direct
        st.write("")
        fig_r, ax_r = plt.subplots(figsize=(4.5, 3), dpi=100)
        labels_r = ["GAGNE", "PERDU"]
        counts_r = [st.session_state.roulette_stats_gains["GAGNE"], st.session_state.roulette_stats_gains["PERDU"]]
        ax_r.bar(labels_r, counts_r, color=["#10b981", "#ef4444"], edgecolor="#111827", width=0.4)
        ax_r.set_title("Repartition reelle de vos paris", fontsize=10, fontweight="bold")
        ax_r.set_ylabel("Nombre d'evenements")
        ax_r.grid(axis="y", linestyle=":", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_r, clear_figure=True)
        st.write("---")
        st.markdown("**Simulation de masse de la Roulette (10 000 tirages) :**")
        st.write(f"Ce simulateur va tester 10 000 lancers sur votre pari actuel : **{st.session_state.roulette_choix_pari}**.")

        if st.button("Lancer la simulation (10 000 Roulettes)", key="btn_sim_10000_roulette"):
            n_sim = 10000
            cpt_victoires = 0
            pari_actif = st.session_state.roulette_choix_pari

            # Détermination de la probabilité théorique exacte pour la ligne de repère
            if pari_actif in ["Rouge", "Noir", "Pair (Even)", "Impair (Odd)", "Manque (1-18)", "Passe (19-36)"]:
                p_theorique = 18.0 / 37.0
            else:  # Cas du Numéro 0 seul
                p_theorique = 1.0 / 37.0

            # Simulation mathématique ultra-rapide des 10 000 lancers
            rouges_list = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            for _ in range(n_sim):
                tirage = random.randint(0, 36)
                victoire_sim = False
                
                if tirage == 0:
                    if pari_actif == "Numero 0": victoire_sim = True
                else:
                    is_rouge = tirage in rouges_list
                    if pari_actif == "Rouge" and is_rouge: victoire_sim = True
                    elif pari_actif == "Noir" and not is_rouge: victoire_sim = True
                    elif pari_actif == "Pair (Even)" and tirage % 2 == 0: victoire_sim = True
                    elif pari_actif == "Impair (Odd)" and tirage % 2 != 0: victoire_sim = True
                    elif pari_actif == "Manque (1-18)" and tirage <= 18: victoire_sim = True
                    elif pari_actif == "Passe (19-36)" and tirage > 18: victoire_sim = True

                if victoire_sim:
                    cpt_victoires += 1

            # Calcul des fréquences de la simulation de Bernoulli
            f_gagne = cpt_victoires / n_sim
            f_perdu = (n_sim - cpt_victoires) / n_sim

            # Tracé du graphique Matplotlib de convergence
            fig_sim_r, ax_sim_r = plt.subplots(figsize=(4.5, 3), dpi=100)
            labels_sim_r = ["GAGNE", "PERDU"]
            freqs_sim_r = [f_gagne, f_perdu]
            
            ax_sim_r.bar(labels_sim_r, freqs_sim_r, color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
            ax_sim_r.axhline(y=p_theorique, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Theorie Gagne ({p_theorique*100:.1f}%)")
            ax_sim_r.axhline(y=1.0 - p_theorique, color="#2563eb", linestyle="--", linewidth=1.5, label=f"Theorie Perdu ({(1.0-p_theorique)*100:.1f}%)")
            
            ax_sim_r.set_title(f"Loi des Grands Nombres : Paris {pari_actif}", fontsize=9, fontweight="bold")
            ax_sim_r.set_ylabel("Frequence observee")
            ax_sim_r.set_ylim(0, 1.1)
            ax_sim_r.legend(loc="upper right", fontsize=7)
            ax_sim_r.grid(axis="y", linestyle=":", alpha=0.5)
            plt.tight_layout()
            
            # Rendu immédiat sous le tapis
            st.pyplot(fig_sim_r, clear_figure=True)
            st.write(f"Resultat final : **{cpt_victoires} victoires** sur 10 000 lancers (Frequence : **{f_gagne*100:.2f}%**).")
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
        if st.button("ACTIONNER LE BRAS (SPIN)", key="btn_actionner_slot_premium_v20", use_container_width=True):
            with st.spinner("Defilement des rouleaux mecaniques..."):
                placeholder_slot = st.empty()
                
                # Effet d'animation de rotation
                for _ in range(5):
                    faux_tirage = [str(random.randint(1, n_symboles)) for _ in range(n_rouleaux)]
                    
                    # CORRECTION SOUDEE DU f"""
                    html_animation = "<div style='display: flex; justify-content: center; gap: 15px; margin: 20px 0;'>"
                    for chiffre in faux_tirage:
                        html_animation += f"""
                        <div style='background-color: #27272a; border: 3px solid #eab308; border-radius: 12px; width: 80px; height: 120px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5);'>
                            <span style='font-family: Arial, sans-serif; font-size: 48px; font-weight: bold; color: #a1a1aa;'>{chiffre}</span>
                        </div>
                        """
                    html_animation += "</div>"
                    
                    placeholder_slot.markdown(html_animation, unsafe_allow_html=True)
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
        html_machine = "<div style='display: flex; justify-content: center; gap: 15px; margin: 25px 0;'>"
        for chiffre in affichage_chiffres:
            # CORRECTIF ABSOLU : Le f est soude sans aucun saut de ligne aux guillemets triples
            html_machine += f"""
            <div style='background-color: #2e2e38; border: 4px solid {couleur_cadre}; border-radius: 14px; width: 90px; height: 135px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(0,0,0,0.4);'>
                <span style='font-family: Arial, sans-serif; font-size: 56px; font-weight: bold; color: #ffffff; line-height: 1;'>{chiffre}</span>
            </div>
            """
        html_machine += "</div>"

        # Execution propre du composant web
        st.markdown(html_machine, unsafe_allow_html=True)

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
















