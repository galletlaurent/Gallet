
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application centre de gravité",
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
st.title("Application centre de gravité")
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


# Déclaration officielle de la barre de navigation
# Les variables d'onglets sont liées à leurs index de liste respectifs
onglets = st.tabs([
    "Identification",
    "Définition",
    "Centre de gravité simple",
    "Centre de gravité complexe",
    "Exemples"    
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]


def afficher_atelier_metiers_etanche(metier_selectionne, verrouille=False):
    """Gère le tirage aléatoire d'un scénario et affiche 10 QCM + 10 textes à trous spécifiques au métier."""
    
    # BANQUE DES SCÉNARIOS ÉTANCHE (2 variantes à 10 QCM et 10 trous par métier)
    banque_cas = {
        "Transport Routier": [
            {
                "id_cas": "routier_A",
                "titre": "Scénario Camion-Citerne (Liquides)",
                "contexte": "Calcul du ballant et de l'effet de carène liquide sur un porteur. Ajustez le volume pour observer le déplacement du liquide.",
                "quiz": [
                    {"id": "rA1", "q": "Quel est le risque majeur lors du freinage d'une citerne compartimentée mal remplie ?", "options": ["Le déplacement du CG vers l'avant (délestage arrière)", "Une augmentation de la pression des pneus arrière", "Une baisse immédiate de la consommation"], "rep": "Le déplacement du CG vers l'avant (délestage arrière)"},
                    {"id": "rA2", "q": "Pour limiter le déplacement du centre de gravité dans les virages, on utilise :", "options": ["Des plaques antiroulis (cloisons brise-flots)", "Un limiteur de vitesse électronique", "Un châssis plus souple"], "rep": "Des plaques antiroulis (cloisons brise-flots)"},
                    {"id": "rA3", "q": "Comment évolue la stabilité d'un camion-citerne à moitié vide par rapport à un camion plein ?", "options": ["Elle diminue fortement à cause de la vague liquide", "Elle augmente car le véhicule est plus léger", "Elle reste strictement identique"], "rep": "Elle diminue fortement à cause de la vague liquide"},
                    {"id": "rA4", "q": "La hauteur du centre de gravité d'une citerne ronde est généralement :", "options": ["Plus haute que celle d'une citerne ovale", "Plus basse que celle d'une citerne ovale", "Au niveau de l'axe des roues"], "rep": "Plus haute que celle d'une citerne ovale"},
                    {"id": "rA5", "q": "Lors d'un virage à droite, le fluide se déplace vers :", "options": ["La gauche de la citerne par force centrifuge", "La droite de la citerne", "Le fond du réservoir"], "rep": "La gauche de la citerne par force centrifuge"},
                    {"id": "rA6", "q": "Quel compartiment faut-il vider en premier pour maintenir la motricité sur un tracteur ?", "options": ["Les compartiments arrière", "Les compartiments avant", "Le compartiment central"], "rep": "Les compartiments arrière"},
                    {"id": "rA7", "q": "L'effet de carène liquide engendre une instabilité :", "options": ["Dynamique lors des changements de trajectoire", "Uniquement à l'arrêt complet", "Inexistante sur route plane"], "rep": "Dynamique lors des changements de trajectoire"},
                    {"id": "rA8", "q": "Le ballant longitudinal affecte principalement :", "options": ["Les distances de freinage et d'arrêt", "La direction en ligne droite constante", "La visibilité des rétroviseurs"], "rep": "Les distances de freinage et d'arrêt"},
                    {"id": "rA9", "q": "Le volume mort (vide) recommandé dans une citerne pour limiter le ressac est de :", "options": ["Moins de 20% ou plus de 80% du volume total", "Exactement 50% dans chaque cuve", "Toujours 100% de vide"], "rep": "Moins de 20% ou plus de 80% du volume total"},
                    {"id": "rA10", "q": "En cas de tangage violent du liquide, le conducteur doit :", "options": ["Maintenir une trajectoire stable et rétrograder souplement", "Donner de violents coups de volant", "Freiner par à-coups rapides"], "rep": "Maintenir une trajectoire stable et rétrograder souplement"}
                ],
                "trous": [
                    ("1. Le mouvement des liquides déplace le centre de ......... en virage.", ["Choisir...", "gravité", "pression"], "gravité", "mr_t1"),
                    ("2. Une citerne pleine est plus stable qu'une citerne ......... remplie.", ["Choisir...", "à moitié", "totalement"], "à moitié", "mr_t2"),
                    ("3. Les cloisons ......... réduisent le mouvement longitudinal du fluide.", ["Choisir...", "brise-flots", "étanches"], "brise-flots", "mr_t3"),
                    ("4. La force ......... pousse le liquide vers l'extérieur de la courbe.", ["Choisir...", "centrifuge", "Coriolis"], "centrifuge", "mr_t4"),
                    ("5. Un transfert de charge trop brusque peut provoquer le ......... du camion.", ["Choisir...", "renversement", "patinage"], "renversement", "mr_t5"),
                    ("6. Le délestage de l'essieu avant diminue la capacité de ......... du porteur.", ["Choisir...", "guidage", "freinage"], "guidage", "mr_t6"),
                    ("7. Une forme de cuve ......... abaisse naturellement le barycentre du fluide.", ["Choisir...", "ovale", "cylindrique"], "ovale", "mr_t7"),
                    ("8. Le ressac désigne l'onde de ......... du liquide contre les parois.", ["Choisir...", "choc", "pression"], "choc", "mr_t8"),
                    ("9. Le calcul de la stabilité prend en compte la ......... du liquide transporté.", ["Choisir...", "densité", "viscosité"], "densité", "mr_t9"),
                    ("10. Conduire un liquide exige une grande ......... dans l'accélération.", ["Choisir...", "souplesse", "fermeté"], "souplesse", "mr_t10")
                ]
            },
            {
                "id_cas": "routier_B",
                "titre": "Scénario Convoi Exceptionnel (Engins lourds)",
                "contexte": "Positionnement analytique d'une charge lourde sur une remorque porte-char pour équilibrer les essieux.",
                "quiz": [
                    {"id": "rB1", "q": "Si le centre de gravité de l'engin est placé trop en arrière de la flèche de la remorque :", "options": ["Il y a un risque de délestage de l'essieu moteur du tracteur", "Le camion freine beaucoup plus court", "Le châssis se courbe vers le bas"], "rep": "Il y a un risque de délestage de l'essieu moteur du tracteur"},
                    {"id": "rB2", "q": "Où doit se situer idéalement le CG de la charge par rapport au centre du train arrière ?", "options": ["Légèrement en avant du centre géométrique des essieux", "Exactement sur le pare-chocs arrière", "Le plus haut possible au-dessus du sol"], "rep": "Légèrement en avant du centre géométrique des essieux"},
                    {"id": "rB3", "q": "La hauteur du CG d'une pelle mécanique sur chenilles impose :", "options": ["Une réduction drastique de la vitesse en courbe", "Un élargissement obligatoire de la chaussée", "L'utilisation de pneus basse pression"], "rep": "Une réduction drastique de la vitesse en courbe"},
                    {"id": "rB4", "q": "Le calcul du report de charge sur la sellette d'attelage dépend :", "options": ["De la distance entre le CG de l'engin et le pivot", "De la couleur du tracteur routier", "Uniquement de la longueur totale du convoi"], "rep": "De la distance entre le CG de l'engin et le pivot"},
                    {"id": "rB5", "q": "Une mauvaise répartition des masses sur un porte-char peut :", "options": ["Faire fissurer ou plier le col de cygne de la remorque", "Inverser le sens de rotation du moteur", "Raccourcir la longueur des câbles électriques"], "rep": "Faire fissurer ou plier le col de cygne de la remorque"},
                    {"id": "rB6", "q": "Pour abaisser le centre de gravité global d'un convoi, on privilégie :", "options": ["Une remorque extra-surbaissée (surbaissée)", "Des madriers en bois sous les chenilles", "Une flèche d'attelage surélevée"], "rep": "Une remorque extra-surbaissée (surbaissée)"},
                    {"id": "rB7", "q": "L'arrimage d'une charge lourde a pour but d'empêcher :", "options": ["Le déplacement du CG sous l'effet des forces d'inertie", "L'oxydation superficielle des pièces en acier", "Une augmentation de la largeur du convoi"], "rep": "Le déplacement du CG sous l'effet des forces d'inertie"},
                    {"id": "rB8", "q": "L'isobarycentre des points d'ancrage des chaînes d'arrimage doit idéalement :", "options": ["S'aligner verticalement avec le CG de la charge", "Être déporté le plus en arrière possible", "Toucher le sol de la route"], "rep": "S'aligner verticalement avec le CG de la charge"},
                    {"id": "rB9", "q": "En cas de surcharge sur l'essieu arrière de la remorque, il faut déplacer la charge :", "options": ["Vers l'avant (vers le tracteur)", "Vers l'arrière", "Sur le côté droit uniquement"], "rep": "Vers l'avant (vers le tracteur)"},
                    {"id": "rB10", "q": "Le passage d'un convoi sur un pont nécessite de connaître la position du CG pour :", "options": ["Calculer la charge linéaire par mètre de tablier", "Vérifier la hauteur des garde-corps", "Éviter les courants d'air sous l'ouvrage"], "rep": "Calculer la charge linéaire par mètre de tablier"}
                ],
                "trous": [
                    ("1. Un chargement trop haut augmente le risque de .........", ["Choisir...", "retournement", "crevaison"], "retournement", "mr_t3"),
                    ("2. Arrimer solidement bloque le déplacement du ......... pendant le transport.", ["Choisir...", "barycentre", "moteur"], "barycentre", "mr_t4"),
                    ("3. Le col de cygne transmet une partie du poids à la ......... d'attelage.", ["Choisir...", "sellette", "cabine"], "sellette", "mr_t5"),
                    ("4. La charge utile doit être répartie proportionnellement à la capacité des .........", ["Choisir...", "essieux", "freins"], "essieux", "mr_t6"),
                    ("5. Un défaut de charge à l'avant entraîne une perte d'......... directionnelle.", ["Choisir...", "adhérence", "vitesse"], "adhérence", "mr_t7"),
                    ("6. Les convois exceptionnels utilisent des remorques ......... pour réduire la hauteur.", ["Choisir...", "surbaissées", "extensibles"], "surbaissées", "mr_t8"),
                    ("3. Le col de cygne transmet une partie du poids à la ......... d'attelage.", ["Choisir...", "sellette", "cabine"], "sellette", "mr_t5"),
                    ("4. La charge utile doit être répartie proportionnellement à la capacité des .........", ["Choisir...", "essieux", "pneus"], "essieux", "mr_t6"),
                    ("5. Un défaut de charge à l'avant entraîne une perte d'......... directionnelle.", ["Choisir...", "adhérence", "vitesse"], "adhérence", "mr_t7"),
                    ("6. Les convois exceptionnels utilisent des remorques ......... pour réduire la hauteur.", ["Choisir...", "surbaissées", "extensibles"], "surbaissées", "mr_t8"),
                    ("7. Dépasser la charge maximale autorisée modifie le comportement ......... du véhicule.", ["Choisir...", "dynamique", "statique"], "dynamique", "mr_t9"),
                    ("8. Le calcul du barycentre prend en compte le poids à ......... du tracteur.", ["Choisir...", "vide", "vide"], "vide", "mr_t10"),
                    ("9. Les forces d'inertie lors du freinage poussent le centre de masse vers l'.........", ["Choisir...", "avant", "arrière"], "avant", "mr_t11"),
                    ("10. Un mauvais arrimage engendre une instabilité lors des changements de .........", ["Choisir...", "direction", "vitesse"], "direction", "mr_t12")
                ]
            }
        ],

        "Travaux Publics": [
            {
                "id_cas": "tp_A",
                "titre": "Scénario Grue à tour (Équilibrage du contre-flèche)",
                "contexte": "Calcul du moment stabilisateur d'une grue face à une charge maximale de béton.",
                "quiz": [
                    {"id": "tpA1", "q": "Que se passe-t-il pour le CG global de la grue lorsque le chariot avance sur la flèche ?", "options": ["Le CG se déplace vers l'avant, augmentant le moment de basculement", "Le CG reste fixe au centre du mât", "Le contre-poids devient plus lourd"], "rep": "Le CG se déplace vers l'avant, augmentant le moment de basculement"},
                    {"id": "tpA2", "q": "Les blocs de béton à la base de la grue servent à :", "options": ["Abaisser le CG global pour ancrer la structure au sol", "Mesurer la hauteur de la tour", "Décorer la zone de chantier"], "rep": "Abaisser le CG global pour ancrer la structure au sol"},
                    {"id": "tpA3", "q": "Quelle grandeur physique mesure le produit de la charge par sa distance au mât ?", "options": ["Le moment de la force", "La pression hydrostatique", "L'énergie cinétique"], "rep": "Le moment de la force"},
                    {"id": "tpA4", "q": "Le moment de basculement maximal d'une grue est atteint lorsque le chariot est :", "options": ["En bout de flèche", "Proche de la cabine", "Au milieu de la flèche"], "rep": "En bout de flèche"},
                    {"id": "tpA5", "q": "Que désigne la 'courbe de charge' d'une grue à tour ?", "options": ["La masse maximale levable en fonction de la portée", "La consommation électrique du moteur", "La trajectoire du crochet"], "rep": "La masse maximale levable en fonction de la portée"},
                    {"id": "tpA6", "q": "Comment compense-t-on le moment généré par la flèche à vide ?", "options": ["Par un contrepoids sur la contre-flèche", "Par des fondations plus larges uniquement", "En inclinant le mât"], "rep": "Par un contrepoids sur la contre-flèche"},
                    {"id": "tpA7", "q": "Lors d'une tempête, la flèche d'une grue doit être laissée :", "options": ["Libre de tourner au vent (girouette)", "Bloquée par un frein d'orientation", "Toujours dirigée vers le nord"], "rep": "Libre de tourner au vent (girouette)"},
                    {"id": "tpA8", "q": "Quel type de fondation utilise-t-il le principe du moment d'inertie de base ?", "options": ["Le massif d'ancrage en béton armé", "Les pieux métalliques minces", "Les patins de caoutchouc"], "rep": "Le massif d'ancrage en béton armé"},
                    {"id": "tpA9", "q": "Le centre de masse de la flèche d'une grue uniforme se situe :", "options": ["Au milieu géométrique de la flèche", "Au niveau de la cabine", "Au niveau du contrepoids"], "rep": "Au milieu géométrique de la flèche"},
                    {"id": "tpA10", "q": "Un dépassement de la charge maximale à une portée donnée engendre :", "options": ["Un risque d'effondrement ou de basculement", "Un ralentissement automatique sans danger", "Une hausse de la tension des câbles sans rupture"], "rep": "Un risque d'effondrement ou de basculement"}
                ],
                "trous": [
                    ("1. Pour rester stable, le moment résiduel doit être compensé par la .........", ["Choisir...", "base", "vireuse"], "base", "mtp_t1"),
                    ("2. Avancer le chariot éloigne le poids du mât, ce qui crée un ......... de force.", ["Choisir...", "bras de levier", "frottement"], "bras de levier", "mtp_t2"),
                    ("3. La flèche et la contre-flèche doivent être en parfait équilibre .........", ["Choisir...", "statique", "dynamique"], "statique", "mtp_t3"),
                    ("4. Le mât de la grue subit principalement des efforts de .........", ["Choisir...", "flexion", "torsion"], "flexion", "mtp_t4"),
                    ("5. Les charges dynamiques comme le vent modifient le centre de ......... global.", ["Choisir...", "gravité", "pression"], "gravité", "mtp_t5"),
                    ("6. L'anémomètre contrôle la vitesse du vent pour stopper le .........", ["Choisir...", "levage", "moteur"], "levage", "mtp_t6"),
                    ("7. Une grue mobile utilise des stabilisateurs pour élargir sa base de .........", ["Choisir...", "sustentation", "roulement"], "sustentation", "mtp_t7"),
                    ("8. Le moment de renversement augmente proportionnellement à la ......... du chariot.", ["Choisir...", "distance", "vitesse"], "distance", "mtp_t8"),
                    ("9. Le lest de base abaisse le barycentre mécanique pour ancrer la .........", ["Choisir...", "structure", "cabine"], "structure", "mtp_t9"),
                    ("10. Avant chaque chantier, une note de calcul valide la stabilité géométrique .........", ["Choisir...", "globale", "partielle"], "globale", "mtp_t10")
                ]
            },
            {
                "id_cas": "tp_B",
                "titre": "Scénario Blindage de fouille (Poussée des terres)",
                "contexte": "Détermination du centre de poussée trapézoïdal pour l'installation de vérins hydrauliques.",
                "quiz": [
                    {"id": "tpB1", "q": "Pour une poussée des terres triangulaire (pression nulle en haut), où est le centre d'application ?", "options": ["Au 1/3 de la hauteur en partant de la base", "Exactement au milieu de la hauteur", "Tout en haut de la tranchée"], "rep": "Au 1/3 de la hauteur en partant de la base"},
                    {"id": "tpB2", "q": "Si les parois reçoivent une charge de nappe phréatique, le barycentre des forces :", "options": ["Se déplace vers le bas de la fouille", "Remonte à la surface", "S'annule complètement"], "rep": "Se déplace vers le bas de la fouille"},
                    {"id": "tpB3", "q": "Le diagramme des pressions sur un blindage de fouille profonde est souvent :", "options": ["Trapézoïdal", "Parfaitement carré", "Inversement proportionnel"], "rep": "Trapézoïdal"},
                    {"id": "tpB4", "q": "Quel facteur augmente la poussée horizontale sur les panneaux de blindage ?", "options": ["La présence d'un stockage de matériaux en bord de fouille", "Le nettoyage de la surface de travail", "Le séchage complet de la terre"], "rep": "La présence d'un stockage de matériaux en bord de fouille"},
                    {"id": "tpB5", "q": "Les vérins hydrauliques d'un blindage doivent être placés préférentiellement :", "options": ["Au niveau du centre de gravité du diagramme des pressions", "Tous en haut de la tranchée pour la visibilité", "Uniquement au fond de la fouille"], "rep": "Au niveau du centre de gravité du diagramme des pressions"},
                    {"id": "tpB6", "q": "La rupture par rupture de butée se produit lorsque le sol :", "options": ["Ne résiste plus à la poussée en pied de paroi", "Devient trop sec et sablonneux", "Glisse parallèlement à la tranchée"], "rep": "Ne résiste plus à la poussée en pied de paroi"},
                    {"id": "tpB7", "q": "Quelle est la fonction première d'une lisse longitudinale sur un blindage ?", "options": ["Répartir la force des vérins sur toute la paroi", "Empêcher les infiltrations d'eau claire", "Servir de passerelle de circulation"], "rep": "Répartir la force des vérins sur toute la paroi"},
                    {"id": "tpB8", "q": "La cohésion d'un sol argileux a pour effet géotechnique de :", "options": ["Réduire temporairement la poussée des terres en surface", "Augmenter la pression hydrostatique", "Rendre le diagramme des pressions instable"], "rep": "Réduire temporairement la poussée des terres en surface"},
                    {"id": "tpB9", "q": "Pour calculer la résultante des forces de poussée, on évalue :", "options": ["L'aire du diagramme des pressions", "La longueur de la tranchée uniquement", "Le périmètre de la fouille"], "rep": "L'aire du diagramme des pressions"},
                    {"id": "tpB10", "q": "Un défaut d'étaiement au centre de poussée engendre un risque immédiat de :", "options": ["Effondrement et ensevelissement des opérateurs", "Glissement de terrain à plus de 500 mètres", "Déstabilisation du réseau électrique aérien"], "rep": "Effondrement et ensevelissement des opérateurs"}
                ],
                "trous": [
                    ("1. La terre exerce une pression hydrostatique dont le barycentre est au ......... inférieur.", ["Choisir...", "tiers", "quart"], "tiers", "mtp_t11"),
                    ("2. Les étais doivent soutenir la paroi au niveau du centre de ......... des forces.", ["Choisir...", "poussée", "torsion"], "poussée", "mtp_t12"),
                    ("3. Une surcharge en bord de fouille modifie la distribution horizontale des .........", ["Choisir...", "charges", "pentes"], "charges", "mtp_t13"),
                    ("4. Le coefficient de poussée dépend directement de l'angle de ......... interne.", ["Choisir...", "frottement", "rotation"], "frottement", "mtp_t14"),
                    ("5. L'eau infiltrée ajoute une composante de pression ......... non négligeable.", ["Choisir...", "hydraulique", "mécanique"], "hydraulique", "mtp_t15"),
                    ("6. La résultante des forces s'applique au ......... de la surface de pression.", ["Choisir...", "barycentre", "périmètre"], "barycentre", "mtp_t16"),
                    ("7. Les parois verticales exigent un système de ......... rigide.", ["Choisir...", "blindage", "mesure"], "blindage", "mtp_t17"),
                    ("8. En tête de fouille, la pression théorique d'un sol pulvérulent est .........", ["Choisir...", "nulle", "maximale"], "nulle", "mtp_t18"),
                    ("9. Les lisses horizontales permettent d'uniformiser la force des ......... hydrauliques.", ["Choisir...", "verins", "cables"], "verins", "mtp_t9"),
                    ("10. La stabilite des talus depend du glissement de la masse de .........", ["Choisir...", "terre", "beton"], "terre", "mtp_t10")
                ]
            }
        ],
        "Maintenance Industrielle": [
            {
                "id_cas": "maint_A",
                "titre": "Scénario Équilibrage de rotor de ventilation",
                "contexte": "Traitement analytique d'un balourd sur un extracteur d'air mécanique d'usine.",
                "quiz": [
                    {"id": "mA1", "q": "Un rotor mal equilibre signifie geometriquement que :", "options": ["Le centre de gravite ne coincide pas avec l'axe de rotation", "La piece est trop lourde pour le moteur", "Le diametre exterieur n'est pas un cercle parfait"], "rep": "Le centre de gravite ne coincide pas avec l'axe de rotation"},
                    {"id": "mA2", "q": "L'ajout d'une masse de correction a 180 degres du defaut permet de :", "options": ["Ramener le centre de gravite sur l'axe de rotation", "Augmenter la vitesse de l'arbre mecanique", "Reduire la consommation electrique de moitie"], "rep": "Ramener le centre de gravite sur l'axe de rotation"},
                    {"id": "mA3", "q": "Quel appareil utilise-t-on pour localiser precisement l'angle d'un balourd ?", "options": ["Un analyseur de vibrations", "Un multimetre", "Un pied a coulisse"], "rep": "Un analyseur de vibrations"},
                    {"id": "mA4", "q": "La force centrifuge generee par un balourd augmente avec :", "options": ["Le carre de la vitesse de rotation", "La longueur de l'arbre uniquement", "La temperature du moteur"], "rep": "Le carre de la vitesse de rotation"},
                    {"id": "mA5", "q": "L'equilibrage dit 'dynamique' s'applique aux rotors :", "options": ["De grande longueur tournant a haute vitesse", "Totalement immobiles", "Parfaitement spheriques"], "rep": "De grande longueur tournant a haute vitesse"},
                    {"id": "mA6", "q": "Une mauvaise repartition des masses sur un arbre moteur provoque :", "options": ["Une usure prematuree des roulements", "Une surchauffe du liquide de refroidissement", "Une augmentation de la tension reseau"], "rep": "Une usure prematuree des roulements"},
                    {"id": "mA7", "q": "En maintenance preventive, la modification du spectre vibratoire indique :", "options": ["L'apparition d'un balourd ou d'un desalignement", "Un manque de carburant", "Une erreur de programmation de l'automate"], "rep": "L'apparition d'un balourd ou d'un desalignement"},
                    {"id": "mA8", "q": "La masse de correction ajoutee doit creer un moment equilibre :", "options": ["Egal et oppose au moment du balourd", "Deux fois plus grand que le defaut", "Strictement nul dans tous les plans"], "rep": "Egal et oppose au moment du balourd"},
                    {"id": "mA9", "q": "Sur une helice de ventilateur, l'isobarycentre geometrique ideal coincide avec :", "options": ["L'axe central de l'alesage", "L'extremite d'une pale", "Le carter de protection"], "rep": "L'axe central de l'alesage"},
                    {"id": "mA10", "q": "Un desequilibre statique peut etre mis en evidence :", "options": ["En laissant le rotor libre sur deux rails horizontaux", "En mesurant la resistance des bobinages", "En observant la couleur de la peinture"], "rep": "En laissant le rotor libre sur deux rails horizontaux"}
                ],
                "trous": [
                    ("1. Le decalage du centre de masse provoque une force ......... centrifuge.", ["Choisir...", "tournante", "statique"], "tournante", "mm_t1"),
                    ("2. L'action corrective consiste a poser un contrepoids pour eliminer le .........", ["Choisir...", "balourd", "frottement"], "balourd", "mm_t2"),
                    ("3. Les vibrations severes endommagent les paliers et les ......... de guidage.", ["Choisir...", "roulements", "courroies"], "roulements", "mm_t3"),
                    ("4. L'equilibrage mecanique modifie la position du centre de ......... du solide.", ["Choisir...", "gravite", "pression"], "gravité", "mm_t4"),
                    ("5. Pour verifier la stabilite, on mesure l'amplitude des ......... de la machine.", ["Choisir...", "vibrations", "temperatures"], "vibrations", "mm_t5"),
                    ("6. Un balourd se caracterise par une masse excentree a une certaine ......... de l'axe.", ["Choisir...", "distance", "vitesse"], "distance", "mm_t6"),
                    ("7. L'unite de mesure du moment de desequilibre residuel est le .........", ["Choisir...", "g.mm", "N.m"], "g.mm", "mm_t7"),
                    ("8. Un rotor asymetrique necessite un equilibrage dans deux ......... distinctes.", ["Choisir...", "plans", "directions"], "plans", "mm_t8"),
                    ("9. La frequence des vibrations dues au balourd est egale a la vitesse de .........", ["Choisir...", "rotation", "coupe"], "rotation", "mm_t9"),
                    ("10. Ramener le barycentre sur l'axe mecanique permet de ......... la structure.", ["Choisir...", "stabiliser", "alourdir"], "stabiliser", "mm_t10")
                ]
            },
            {
                "id_cas": "maint_B",
                "titre": "Scénario Pont Roulant (Chariot de levage)",
                "contexte": "Déplacement du centre de charge sur une poutre d'un hall industriel.",
                "quiz": [
                    {"id": "mB1", "q": "Où la poutre subit-elle la flexion maximale lorsque le chariot souleve une charge ?", "options": ["Lorsque le chariot est positionne au milieu de la portee", "Lorsque le chariot est gare contre un pilier de rive", "La position n'influence pas la flexion mecanique"], "rep": "Lorsque le chariot est positionne au milieu de la portee"},
                    {"id": "mB2", "q": "Les capteurs de surcharge mesurent la repartition du poids au niveau :", "options": ["Des galets de roulement d'extremite", "Du crochet de levage uniquement", "Du cable de commande"], "rep": "Des galets de roulement d'extremite"},
                    {"id": "mB3", "q": "Le deplacement du chariot modifie la position du centre de gravite de l'ensemble :", "options": ["Pont + charge soulevee", "Du batiment complet", "Du crochet uniquement"], "rep": "Pont + charge soulevee"},
                    {"id": "mB4", "q": "Pour calculer les reactions aux appuis verticaux, on applique le principe :", "options": ["Des moments statiques", "De la conservation de l'energie", "De la diffraction de la lumiere"], "rep": "Des moments statiques"},
                    {"id": "mB5", "q": "Si la charge se rapproche de l'appui A, la force exercee sur cet appui :", "options": ["Augmente proportionnellement", "Diminue fortement", "Reste strictement identique"], "rep": "Augmente proportionnellement"},
                    {"id": "mB6", "q": "La fleche maximale d'une poutre de pont roulant est limitee pour :", "options": ["Garantir la rigidite et la securite de la structure", "Reduire la vitesse du chariot", "Eviter le glissement des cables"], "rep": "Garantir la rigidite et la securite de la structure"},
                    {"id": "mB7", "q": "Le poids propre de la poutre principale est considere comme une charge :", "options": ["Uniformement repartie sur toute la longueur", "Concentree en son centre exact", "Negligeable devant la charge utile"], "rep": "Uniformement repartie sur toute la longueur"},
                    {"id": "mB8", "q": "Lors d'une translation rapide, le balancement de la charge deplace le CG de maniere :", "options": ["Dynamique et oscillatoire", "Statique et constante", "Nulle et imperceptible"], "rep": "Dynamique et oscillatoire"},
                    {"id": "mB9", "q": "En mecanique, la condition d'equilibre d'une poutre impose que la somme des forces verticales soit :", "options": ["Nulle", "Egale au moment de torsion", "Positive et superieure a 100 tonnes"], "rep": "Nulle"},
                    {"id": "mB10", "q": "L'isobarycentre geometrique d'une poutre homogene et rectiligne se situe :", "options": ["À la moitie exacte de sa longueur", "Sur le chariot de levage", "Au niveau du moteur de translation"], "rep": "À la moitie exacte de sa longueur"}
                ],
                "trous": [
                    ("1. Le deplacement de la charge modifie la reaction aux ......... du pont.", ["Choisir...", "appuis", "moteurs"], "appuis", "mm_t11"),
                    ("2. Calculer les moments permet d'eviter la rupture par ......... de la poutre.", ["Choisir...", "flexion", "traction"], "flexion", "mm_t12"),
                    ("3. Le chariot translate horizontalement le long de la ......... metallique.", ["Choisir...", "poutre", "colonne"], "poutre", "mm_t13"),
                    ("4. La charge maximale utile est indiquee sur la plaque ......... du pont.", ["Choisir...", "signaletique", "constructeur"], "signaletique", "mm_t14"),
                    ("5. Quand le chariot est au centre, les charges sur les deux piliers sont .........", ["Choisir...", "egales", "differentes"], "egales", "mm_t15"),
                    ("6. L'action du poids propre s'applique au centre de ......... de la poutre.", ["Choisir...", "gravite", "torsion"], "gravite", "mm_t16"),
                    ("7. Lever une charge en biais deplace le barycentre hors du plan de .........", ["Choisir...", "levage", "sol"], "levage", "mm_t17"),
                    ("8. Les chemins de roulement guident les galets dans l'axe ......... d'avance.", ["Choisir...", "longitudinal", "vertical"], "longitudinal", "mm_t18"),
                    ("9. Une surcharge locale risque de faire ......... les structures porteuses.", ["Choisir...", "flechir", "tourner"], "flechir", "mm_t19"),
                    ("10. L'equilibre statique impose un moment resultant strictement ......... aux appuis.", ["Choisir...", "nul", "positif"], "nul", "mm_t20")
                ]
            }
        ],
        "Géomètre": [
            {
                "id_cas": "geo_A",
                "titre": "Scénario Division de parcelle irrégulière",
                "contexte": "Calcul du centre géométrique d'un polygone cadastral par relevé de coordonnées de bornes.",
                "quiz": [
                    {"id": "gA1", "q": "Pour trouver le centre géométrique (isobarycentre) d'un terrain polygonal, on effectue :", "options": ["La moyenne arithmétique des coordonnées de ses sommets", "Le produit des longueurs de tous les côtés", "La mesure de la diagonale la plus longue"], "rep": "La moyenne arithmétique des coordonnées de ses sommets"},
                    {"id": "gA2", "q": "Si la parcelle possède une forme en L, le centre géométrique calculé peut se situer :", "options": ["À l'extérieur des limites réelles du terrain", "Obligatoirement sur la borne principale", "Strictement au milieu du grand côté"], "rep": "À l'extérieur des limites réelles du terrain"},
                    {"id": "gA3", "q": "La formule de Green-Riemann (ou des lacets) permet au géomètre de calculer :", "options": ["L'aire exacte d'un polygone quelconque", "L'altitude moyenne du terrain", "L'erreur de fermeture angulaire"], "rep": "L'aire exacte d'un polygone quelconque"},
                    {"id": "gA4", "q": "Le système de projection officiel utilisé en France métropolitaine est le :", "options": ["RGF93 / Lambert-93", "WGS84 / UTM Nord", "Mercator direct"], "rep": "RGF93 / Lambert-93"},
                    {"id": "gA5", "q": "Pour diviser une parcelle en deux surfaces de valeurs égales, la ligne de partage passe par :", "options": ["Un axe calculé dépendant du barycentre des surfaces", "Le milieu du plus petit côté au hasard", "La borne d'orientation nord"], "rep": "Un axe calculé dépendant du barycentre des surfaces"},
                    {"id": "gA6", "q": "Quelle méthode consiste à diviser un polygone en triangles pour simplifier les calculs ?", "options": ["La triangulation analytique", "La méthode des moindres carrés", "Le polygonation par rayonnement"], "rep": "La triangulation analytique"},
                    {"id": "gA7", "q": "L'appareil de terrain combinant théodolite optique et distancemètre laser s'appelle :", "options": ["Une station totale", "Un niveau de chantier", "Un récepteur GNSS passif"], "rep": "Une station totale"},
                    {"id": "gA8", "q": "Le centre de gravité géométrique d'un triangle parfait correspond à :", "options": ["L'intersection des trois médianes", "L'intersection des trois hauteurs", "Le centre du cercle circonscrit"], "rep": "L'intersection des trois médianes"},
                    {"id": "gA9", "q": "En topographie, une erreur de fermeture plane résiduelle se compense par :", "options": ["Une répartition proportionnelle sur les sommets", "L'effacement pur de la dernière mesure", "Le doublement des distances lues"], "rep": "Une répartition proportionnelle sur les sommets"},
                    {"id": "gA10", "q": "Les fichiers de données géométriques d'échange du Cadastre sont au format :", "options": ["EDIGÉO / DXF", "MP3 / AVI", "XLSX / DOCX"], "rep": "EDIGÉO / DXF"}
                ],
                "trous": [
                    ("1. Le géomètre détermine l'isobarycentre à partir des coordonnées .........", ["Choisir...", "topographiques", "maritimes"], "topographiques", "mg_t1"),
                    ("2. Diviser une surface complexe nécessite une méthode de ......... analytique.", ["Choisir...", "triangulation", "peinture"], "triangulation", "mg_t2"),
                    ("3. Les limites séparatives d'une parcelle sont fixées lors d'un ......... foncier.", ["Choisir...", "bornage", "nivellement"], "bornage", "mg_t3"),
                    ("4. Le plan cadastral attribue à chaque terrain un numéro de ......... unique.", ["Choisir...", "parcelle", "section"], "parcelle", "mg_t4"),
                    ("5. La précision centimétrique est obtenue à l'aide d'un récepteur ......... RTK.", ["Choisir...", "GNSS", "VHF"], "GNSS", "mg_t5"),
                    ("6. L'isobarycentre géométrique coïncide avec le centre de surface si la plaque est .........", ["Choisir...", "homogène", "asymétrique"], "homogène", "mg_t6"),
                    ("7. Les angles horizontaux sont mesurés en grades ou en ......... d'arc.", ["Choisir...", "degrés", "mètres"], "degrés", "mg_t7"),
                    ("8. Le calcul des surfaces par coordonnées utilise la méthode des ......... croisés.", ["Choisir...", "produits", "facteurs"], "produits", "mg_t8"),
                    ("9. Le repère de nivellement donne une référence d'......... NGF stable.", ["Choisir...", "altitude", "pression"], "altitude", "mg_t9"),
                    ("10. Les polygones fermés permettent de contrôler la précision des levés de .........", ["Choisir...", "terrain", "bâtiment"], "terrain", "mg_t10")
                ]
            },
            {
                "id_cas": "geo_B",
                "titre": "Scénario Profil de terrain (Remblais / Déblais)",
                "contexte": "Optimisation des mouvements de terre en équilibrant le centre de masse des déblais.",
                "quiz": [
                    {"id": "gB1", "q": "Pour équilibrer parfaitement un chantier de terrassement, le volume de déblai doit être :", "options": ["Égal au volume de remblai (barycentre des terres optimisé)", "Deux fois supérieur pour tasser le sol", "Totalement évacué en décharge externe"], "rep": "Égal au volume de remblai (barycentre des terres optimisé)"},
                    {"id": "gB2", "q": "La ligne neutre d'un profil en long représente la zone où :", "options": ["La hauteur de déblai est égale à la hauteur de remblai", "La terre est la plus rocheuse", "Les machines ne peuvent pas circuler"], "rep": "La hauteur de déblai est égale à la hauteur de remblai"},
                    {"id": "gB3", "q": "Le coefficient de foisonnement d'un sol mesure l'augmentation de volume après :", "options": ["Excavation (débouchage de la terre)", "Compactage au rouleau vibrant", "Arrosage intensif sur site"], "rep": "Excavation (débouchage de la terre)"},
                    {"id": "gB4", "q": "Le profil en travers d'une route permet de vérifier géométriquement :", "options": ["Les pentes latérales et les fossés d'écoulement", "La distance de visibilité d'arrêt", "La vitesse limite autorisée"], "rep": "Les pentes latérales et les fossés d'écoulement"},
                    {"id": "gB5", "q": "Le centre de gravité d'un volume de déblai correspond au point où s'applique :", "options": ["La résultante de la masse des terres excavées", "La pression de la benne du camion", "L'inclinaison maximale du talus"], "rep": "La résultante de la masse des terres excavées"},
                    {"id": "gB6", "q": "La méthode des profils en travers passe par le calcul d'aires :", "options": ["Entre le terrain naturel et la ligne projet", "Uniquement au-dessus de la ligne neutre", "Par intégration double circulaire"], "rep": "Entre le terrain naturel et la ligne projet"},
                    {"id": "gB7", "q": "Pour compacter efficacement un remblai, le conducteur contrôle :", "options": ["L'optimum Proctor (teneur en eau idéale)", "La couleur de la terre de surface", "La vitesse du vent météo"], "rep": "L'optimum Proctor (teneur en eau idéale)"},
                    {"id": "gB8", "q": "Un terrain présentant une pente raide instable exige un calcul de talutage au ratio :", "options": ["Pente maximale de sécurité (angle de talus naturel)", "1 pour 10 systématique", "Toujours vertical à 90 degrés"], "rep": "Pente maximale de sécurité (angle de talus naturel)"},
                    {"id": "gB9", "q": "Le mouvement des terres est optimisé graphiquement par l'épure de :", "options": ["Lalanne (ou diagramme des mouvements des terres)", "Bassin hydrographique", "Green-Riemann"], "rep": "Lalanne (ou diagramme des mouvements des terres)"},
                    {"id": "gB10", "q": "Un relevé altimétrique par drone génère un nuage de points appelé :", "options": ["MNT (Modèle Numérique de Terrain)", "Fichier CAO vectoriel simple", "Plan topographique orthogonal"], "rep": "MNT (Modèle Numérique de Terrain)"}
                ],
                "trous": [
                    ("1. Éviter les transports inutiles consiste à lisser le cubage des .........", ["Choisir...", "terres", "plans"], "terres", "mg_t11"),
                    ("2. Le centre de masse du sol excavé définit le rayon de ......... moyen.", ["Choisir...", "rotation", "balayage"], "rotation", "mg_t12"),
                    ("3. Le volume d'une terre en place augmente apres son extraction du au .........", ["Choisir...", "foisonnement", "tassement"], "foisonnement", "mg_t13"),
                    ("4. Le compactage mecanique reduit les vides pour augmenter la ......... du sol.", ["Choisir...", "densite", "pente"], "densite", "mg_t14"),
                    ("5. Les profils en long decrivent les variations d'......... sur l'axe du projet.", ["Choisir...", "altitude", "largeur"], "altitude", "mg_t15"),
                    ("6. La surface limite entre deblai et remblai forme la ligne .........", ["Choisir...", "neutre", "rouge"], "neutre", "mg_t16"),
                    ("7. Les engins de terrassement d'un chantier deplacent les volumes d'un point a un .........", ["Choisir...", "autre", "banc"], "autre", "mg_t17"),
                    ("8. Calculer le moment des volumes minimise la distance de ......... des camions.", ["Choisir...", "transport", "pesage"], "transport", "mg_t18"),
                    ("9. Le terrassement modifie de facon irreversible le modele du terrain .........", ["Choisir...", "naturel", "artificiel"], "naturel", "mg_t19"),
                    ("10. La topographie fournit le plan d'etat des lieux avant l'implantation du .........", ["Choisir...", "projet", "cadastre"], "projet", "mg_t20")
                ]
            }
        ]
    }

    # Tirage au sort anti-triche unique par session
    cle_index_aleatoire = f"index_scenario_{metier_selectionne.replace(' ', '_')}"
    
    if cle_index_aleatoire not in st.session_state:
        # random.randint(0, 1) choisit de manière équiprobable 0 (Cas A) ou 1 (Cas B)
        st.session_state[cle_index_aleatoire] = random.randint(0, len(banque_cas[metier_selectionne]) - 1)
    
    # On extrait le cas correspondant à l'index stocké en mémoire de session
    index_attribue = st.session_state[cle_index_aleatoire]
    cas = banque_cas[metier_selectionne][index_attribue]
    
    # Enregistrement pour la correction automatique
    st.session_state.quiz_metier_actif = cas["quiz"]
    st.session_state.trous_metier_actif = cas["trous"]
    if st.button("Tirer un autre scénario au sort (Test)", key=f"btn_alea_{cas['id_cas']}"):
        if cle_index_aleatoire in st.session_state:
            del st.session_state[cle_index_aleatoire]
        st.rerun()
    # Affichage du badge du scénario tiré au sort
    st.success(f"**Cas Pratique Assigné : {cas['titre']}**")
    st.write(f"*Contexte technique* : {cas['contexte']}")

    st.write("Ajustez les paramètres mécaniques pour simuler le comportement :")
    fig, ax = plt.subplots(figsize=(6, 2.5))
    
    # --- METIER 1 : TRANSPORT ROUTIER ---
    if cas["id_cas"] == "routier_A":
        col_citerne1, col_citerne2 = st.columns(2)
        with col_citerne1:
            hauteur_liquide = st.slider("Niveau de remplissage de la citerne (m)", min_value=-0.9, max_value=0.9, value=-0.40, step=0.1, disabled=verrouille, key="slider_remplissage")
        with col_citerne2:
            inclinaison = st.slider("Inclinaison / Gîte du camion dans le virage (°)", min_value=-15, max_value=15, value=-8, step=1, disabled=verrouille, key="slider_inclinaison")
        
        pente = np.tan(np.radians(inclinaison))
        y_gauche = hauteur_liquide - pente * 4
        y_droite = hauteur_liquide + pente * 4
        y_gauche_visuel = max(-1.0, min(1.0, y_gauche))
        y_droite_visuel = max(-1.0, min(1.0, y_droite))
        
        ax.plot([-4, 4, 4, -4, -4], [-1, -1, 1, 1, -1], color="black", lw=2, label="Citerne")
        ax.fill_between([-4, 4], [-1, -1], [y_gauche_visuel, y_droite_visuel], color="skyblue", alpha=0.5, label="Liquide")
        
        h1 = y_gauche_visuel - (-1.0)
        h2 = y_droite_visuel - (-1.0)
        L = 8.0
        
        if h2 <= 0.001 or h1 <= 0.001:
            if h1 > h2:
                x_cg_dynamique = -4.0 + (L / 3.0)
                y_cg_dynamique = -1.0 + (h1 / 3.0)
            else:
                x_cg_dynamique = 4.0 - (L / 3.0)
                y_cg_dynamique = -1.0 + (h2 / 3.0)
        else:
            x_barycentre_relatif = (L / 3.0) * ((h1 + 2 * h2) / (h1 + h2))
            x_cg_dynamique = -4.0 + x_barycentre_relatif
            y_barycentre_relatif = ((h1**2 + h1*h2 + h2**2) / (3 * (h1 + h2)))
            y_cg_dynamique = -1.0 + y_barycentre_relatif
            
        ax.scatter(x_cg_dynamique, y_cg_dynamique, color="red", marker="x", s=150, lw=3, label="G (Fluide)")

    elif cas["id_cas"] == "routier_B":
        # Curseur pour déplacer l'engin lourd sur la remorque
        x_charge = st.slider(
            "Positionnement de la pelle de chantier sur le plateau (m)", 
            min_value=-3.0, 
            max_value=3.0, 
            value=1.0, 
            step=0.1, 
            disabled=verrouille, 
            key="slider_routier_b"
        )
        
        # Tracé de la remorque porte-char (Axe horizontal Y = 0)
        ax.plot([-5.0, 5.0], [0.0, 0.0], color="grey", lw=4, label="Remorque")
        
        # Affichage des essieux du train arrière et avant
        ax.scatter([-4.0, 3.0, 4.0], [-0.5, -0.5, -0.5], color="black", s=120, label="Essieux")
        
        # Représentation de la charge (Pelle de 25 tonnes dessinée avec un rectangle vertical)
        ax.bar([float(x_charge)], [1.5], width=1.8, color="orange", alpha=0.7, bottom=0, label="Charge 25t")
        
        # --- CALCUL BARYCENTRIQUE DU CENTRE DE GRAVITÉ (G) GLOBAL ---
        # Remorque seule de 10t centrée à X = 0 + Pelle de 25t à position variable X = x_charge
        # Masse totale roulante prise en compte pour le convoi = 35 tonnes
        m_remorque = 10.0
        m_pelle = 25.0
        m_totale_convoi = m_remorque + m_pelle
        
        x_g = (m_remorque * 0.0 + m_pelle * float(x_charge)) / m_totale_convoi
        
        # RECTIFICATION DE VISIBILITÉ : Point G placé à Y = 0.8 pour surplomber la scène
        y_g = 0.8
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Global)")
        
        # Stabilisation et cadrage géométrique de la scène de transport
        ax.set_xlim(-6.0, 6.0)
        ax.set_ylim(-1.5, 2.5)

    # --- METIER 2 : TRAVAUX PUBLICS ---
    elif cas["id_cas"] == "tp_A":
        # Curseur pour régler la portée de la benne à béton
        x_chariot = st.slider(
            "Portée / Distance du chariot sur la flèche (m)", 
            min_value=0.5, 
            max_value=4.8, 
            value=3.0, 
            step=0.1, 
            disabled=verrouille, 
            key="slider_tp_a"
        )
        
        # Tracé des structures fixes de la grue à tour
        ax.plot([0.0, 0.0], [0.0, 3.5], color="black", lw=4, label="Mât")
        ax.plot([-2.0, 5.0], [3.5, 3.5], color="blue", lw=3, label="Flèche")
        
        # Blocs de charge appliqués
        ax.scatter([-1.8], [3.5], color="grey", marker="s", s=150, label="Contrepoids 15t")
        ax.scatter(float(x_chariot), 3.5, color="orange", s=100, label="Benne 8t")
        
        # --- CALCUL BARYCENTRIQUE DU CENTRE DE GRAVITÉ (G) ---
        # Contrepoids de 15t à X = -1.8m + Charge mobile de 8t à X réglable
        # Masse totale prise en compte pour l'élément horizontal = 23 tonnes
        m_contrepoids = 15.0
        m_benne = 8.0
        m_totale_fleche = m_contrepoids + m_benne
        
        x_g = (m_contrepoids * -1.8 + m_benne * float(x_chariot)) / m_totale_fleche
        
        # RECTIFICATION DE VISIBILITÉ : Point G placé à Y = 3.8 pour surplomber la flèche
        y_g = 3.8
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Fléchage)")
        
        # Stabilisation des axes de la scène de levage
        ax.set_xlim(-3.0, 6.0)
        ax.set_ylim(-0.5, 5.0)
        
    elif cas["id_cas"] == "tp_B":
        # Curseur pour modifier la profondeur d'excavation du blindage
        hauteur_fouille = st.slider(
            "Profondeur de la tranchée de fouille (m)", 
            min_value=2.0, 
            max_value=5.0, 
            value=4.0, 
            step=0.1, 
            disabled=verrouille, 
            key="slider_tp_b"
        )
        
        # Hauteur maximale supérieure calculée dynamiquement à partir du fond Y = -2
        y_surface_sol = float(hauteur_fouille) - 2.0
        
        # Coloration des massifs de terre gauches et droits (marron)
        ax.fill_between([-3, -2], [-2, -2], [y_surface_sol, y_surface_sol], color="brown", alpha=0.4)
        ax.fill_between([2, 3], [-2, -2], [y_surface_sol, y_surface_sol], color="brown", alpha=0.4, label="Terre")
        
        # Tracé des parois verticales du blindage métallique
        ax.plot([-2, -2], [-2, y_surface_sol], color="black", lw=3)
        ax.plot([2, 2], [-2, y_surface_sol], color="black", lw=3, label="Blindage")
        
        # --- CALCUL SCIENTIFIQUE DU CENTRE DE POUSSÉE (G) ---
        # Loi de répartition triangulaire : G se situe à 1/3 de la hauteur totale en partant du fond (Y = -2)
        y_g = -2.0 + (float(hauteur_fouille) / 3.0)
        
        # L'abscisse reste centrée à X = 0 (axe de symétrie de la tranchée de fouille)
        x_g = 0.0
        
        # Tracé de la croix rouge du centre d'application des forces
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Centre poussée)")
        
        # Verrouillage des limites graphiques pour stabiliser l'animation lors du glissement du curseur
        ax.set_xlim(-4.0, 4.0)
        ax.set_ylim(-2.5, 3.5)


        # --- METIER 3 : MAINTENANCE INDUSTRIELLE ---
    elif cas["id_cas"] == "maint_A":
        # Curseur pour chercher l'angle d'équilibrage de la masse corrective
        angle_correction = st.slider(
            "Ajustement angulaire de la masse de correction (°)", 
            min_value=0, 
            max_value=360, 
            value=180, 
            step=5, 
            disabled=verrouille, 
            key="slider_maint_a"
        )
        
        # Tracé géométrique du rotor de la turbine
        angles = np.linspace(0, 2*np.pi, 100)
        ax.plot(np.cos(angles), np.sin(angles), color="grey", linestyle="--")
        ax.scatter(0, 0, color="black", marker="+", s=100, label="Axe Central")
        
        # Masse fixe du balourd (Masse = 0.5 kg placée à un rayon R = 0.6 m sur l'axe X)
        m_balourd = 0.5
        x_balourd = 0.6
        y_balourd = 0.0
        ax.scatter(x_balourd, y_balourd, color="orange", s=120, label="Balourd (0.5 kg)")
        
        # Position trigonométrique dynamique de la masse corrective ajoutée (Masse = 0.3 kg, R = 0.6 m)
        m_corrective = 0.3
        r_corrective = 0.6
        rad = np.radians(float(angle_correction))
        x_corr = r_corrective * np.cos(rad)
        y_corr = r_corrective * np.sin(rad)
        ax.scatter(x_corr, y_corr, color="blue", marker="o", s=100, label="Contrepoids (0.3 kg)")
        
        # --- CALCUL BARYCENTRIQUE EXACT DU CG RÉSIDUEL GLOBAL ---
        # Masse totale active du système excentré M = 0.5 + 0.3 = 0.8 kg
        m_totale_maint = m_balourd + m_corrective
        x_g = (m_balourd * x_balourd + m_corrective * x_corr) / m_totale_maint
        y_g = (m_balourd * y_balourd + m_corrective * y_corr) / m_totale_maint
        
        # Tracé de la croix du centre de gravité résultant
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Résiduel)")
        
        # Ajustement symétrique de la boîte graphique Matplotlib pour le rotor centré
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        
    elif cas["id_cas"] == "maint_B":
        # Curseur pour translater le chariot du pont roulant
        x_chariot_pont = st.slider(
            "Position du chariot sur la portée de la poutre (m)", 
            min_value=-4.5, 
            max_value=4.5, 
            value=1.5, 
            step=0.1, 
            disabled=verrouille, 
            key="slider_maint_b"
        )
        
        # Tracé de la poutre métallique principale (Axe horizontal Y = 0)
        ax.plot([-5, 5], [0, 0], color="black", lw=3, label="Poutre")
        
        # Affichage du chariot de translation mobile suspendu (Ordonnée à Y = 0)
        ax.scatter(x_chariot_pont, 0, color="orange", marker="v", s=150, label="Chariot")
        
        # --- CALCUL BARYCENTRIQUE DU CG DE L'INSTALLATION GLOBALE ---
        # Poutre uniforme de 5000 kg centrée à X = 0 + Chariot charge de 3000 kg mobile
        # Masse totale active du pont roulant M = 5000 + 3000 = 8000 kg
        m_poutre = 5000.0
        m_chariot = 3000.0
        m_totale_pont = m_poutre + m_chariot
        
        x_g = (m_poutre * 0.0 + m_chariot * float(x_chariot_pont)) / m_totale_pont
        
        # On décale légèrement le point G vers le bas (Y = -0.2) pour qu'il soit parfaitement visible sous le chariot
        y_g = -0.2
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Global)")
        
        # Cadrage vertical pour la clarté du schéma linéaire
        ax.set_ylim(-1.0, 1.0)

    # --- METIER 4 : GÉOMÈTRE ---
    elif cas["id_cas"] == "geo_A":
        # Curseur pour modifier dynamiquement une des bornes du terrain cadastral
        facteur_forme = st.slider(
            "Position en ordonnée de la borne principale Nord (m)", 
            min_value=30, 
            max_value=70, 
            value=56, 
            step=1, 
            disabled=verrouille, 
            key="slider_geo_a"
        )
        
        poly_x = [10.0, 45.0, 30.0, 10.0]
        poly_y = [12.0, 15.0, float(facteur_forme), 12.0]
        ax.plot(poly_x, poly_y, color="green", lw=2, label="Bornes")
        ax.fill(poly_x, poly_y, color="green", alpha=0.1)
        
        # Calcul exact de l'isobarycentre
        x_g = (10.0 + 45.0 + 30.0) / 3.0
        y_g = (12.0 + 15.0 + float(facteur_forme)) / 3.0
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Isobarycentre)")
        
    elif cas["id_cas"] == "geo_B":
        # Curseur pour régler la hauteur de nivellement du projet
        hauteur_projet = st.slider(
            "Hauteur de la ligne neutre du projet (m)", 
            min_value=-0.5, 
            max_value=0.5, 
            value=0.0, 
            step=0.05, 
            disabled=verrouille, 
            key="slider_geo_b"
        )
        
        # Génération du profil du terrain naturel (modèle sinusoïdal amorti)
        x_terr = np.linspace(-5, 5, 50)
        y_terr = 0.3 * np.sin(x_terr) * x_terr
        
        # Tracé des éléments géométriques
        ax.plot(x_terr, y_terr, color="green", lw=2, label="Profil Sol")
        ax.axhline(hauteur_projet, color="black", linestyle=":", label="Niveau Projet")
        
        # Coloration des zones de déblai (orange) et de remblai (bleu)
        ax.fill_between(x_terr, y_terr, hauteur_projet, where=(y_terr > hauteur_projet), color="orange", alpha=0.3, label="Déblai")
        ax.fill_between(x_terr, y_terr, hauteur_projet, where=(y_terr < hauteur_projet), color="blue", alpha=0.3, label="Remblai")
        
        # --- RECTIFICATION DES COORDONNÉES DU POINT G (TERRES) ---
        # Le barycentre se déplace horizontalement et verticalement selon la hauteur de coupe du projet
        x_g = -0.45 - (float(hauteur_projet) * 0.7)
        y_g = float(hauteur_projet) + 0.15 * (1.0 - abs(float(hauteur_projet)))
        
        # Sécurités pour maintenir la croix dans le cadre d'affichage
        x_g = np.clip(x_g, -4.0, 4.0)
        y_g = np.clip(y_g, -0.8, 0.8)
        
        ax.scatter(x_g, y_g, color="red", marker="x", s=150, lw=3, label="G (Terres)")
    ax.legend(loc="upper right", fontsize=8)
    ax.axis("off")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")

    # --- MISE EN PAGE SUR DEUX COLONNES ---
    col_q, col_t = st.columns(2)
    
    with col_q:
        st.markdown("##### QCM de Spécialité Professionnelle")
        for num, q_data in enumerate(cas["quiz"], 1):
            st.write(f"**{num}.** {q_data['q']}")
            cle_rep = f"met_quiz_ans_{cas['id_cas']}_{q_data['id']}"
            choix = ["Choisir..."] + q_data["options"]
            st.selectbox("", choix, key=cle_rep, disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Technique Métier (Texte à trous)")
        for enonce, options, _, cle_trou in cas["trous"]:
            c_enon, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_enon:
                st.write(enonce)
            with c_sel:
                st.selectbox("", options, key=f"met_trou_ans_{cas['id_cas']}_{cle_trou}", disabled=verrouille, label_visibility="collapsed")

                
def afficher_atelier_decomposition_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 1 (Décomposition) sur deux colonnes."""
    questions_decompo_sources = [
        {"id": "qd1", "q": "Les surfaces elementaires issues d'un decoupage geometrique doivent etre :", "options": ["Disjointes (sans chevauchement)", "Superposees", "De tailles identiques"], "rep": "Disjointes (sans chevauchement)"},
        {"id": "qd2", "q": "Si une figure est divisee en trois morceaux, l'aire totale est egale a :", "options": ["La somme des aires des trois morceaux", "Le produit des trois aires", "L'aire du plus grand morceau"], "rep": "La somme des aires des trois morceaux"},
        {"id": "qd3", "q": "Pour calculer l'aire d'un polygone en forme de L, on peut le separer en :", "options": ["Deux rectangles", "Deux triangles equilateraux", "Trois cercles"], "rep": "Deux rectangles"},
        {"id": "qd4", "q": "Quelle methode consiste a calculer une grande surface et a enlever le vide ?", "options": ["La methode par soustraction", "La methode par translation", "La methode par produit"], "rep": "La methode par soustraction"},
        {"id": "qd5", "q": "Lors d'un decoupage, comment trouve-t-on une longueur interne manquante ?", "options": ["Par addition ou soustraction des cotes connus", "En utilisant obligatoirement le nombre Pi", "En mesurant directement a la regle"], "rep": "Par addition ou soustraction des cotes connus"},
        {"id": "qd6", "q": "Un triangle rectangle issu d'un decoupage de base B et de hauteur H a pour aire :", "options": ["(B * H) / 2", "B * H", "B + H"], "rep": "(B * H) / 2"},
        {"id": "qd7", "q": "Le decoupage d'un polygone change-t-il la valeur de sa surface totale ?", "options": ["Non, l'aire reste strictement invariante", "Oui, la surface augmente legerement", "Oui, la surface diminue"], "rep": "Non, l'aire reste strictement invariante"},
        {"id": "qd8", "q": "Une figure complexe qui contient un demi-disque evide (creux) se traite par :", "options": ["Soustraction de l'aire du demi-disque", "Addition de l'aire du cercle complet", "Multiplication des deux surfaces"], "rep": "Soustraction de l'aire du demi-disque"},
        {"id": "qd9", "q": "Pour valider une decomposition, la somme des aires partielles doit etre :", "options": ["Egale a l'aire de la figure initiale", "Plus grande que la figure initiale", "Inferieure a la surface de depart"], "rep": "Egale a l'aire de la figure initiale"},
        {"id": "qd10", "q": "Un polygone regulier a 6 cotes (hexagone) se decomposera plus facilement en :", "options": ["6 triangles", "2 carres", "4 cercles"], "rep": "6 triangles"},
    ]

    if "ordre_quiz_tab1_aleatoire" not in st.session_state:
        random.shuffle(questions_decompo_sources)
        st.session_state.ordre_quiz_tab1_aleatoire = questions_decompo_sources

    # Conservation de vos tuples d'origine à 4 éléments
    champs_d = [
        ("1. Découper sans laisser de vide crée une partition .........", ["Choisir...", "exhaustive", "incomplete"], "exhaustive", "dec_t1_final"),
        ("2. Les morceaux crees lors du decoupage ne doivent pas se ..........", ["Choisir...", "chevaucher", "aligner"], "chevaucher", "dec_t2_final"),
        ("3. L'aire d'un polygone est une grandeur strictement ...........", ["Choisir...", "additive", "multiplicative"], "additive", "dec_t3_final"),
        ("4. La methode par soustraction retire la surface de la zone ......", ["Choisir...", "vide", "pleine"], "vide", "dec_t4_final"),
        ("5. Un rectangle et un triangle forment souvent une figure ........", ["Choisir...", "composite", "reguliere"], "composite", "dec_t5_final"),
        ("6. Trouver une dimension inconnue se fait par ......... de segments.", ["Choisir...", "soustraction", "mesure"], "soustraction", "dec_t6_final"),
        ("7. Diviser une forme complexe facilite l'application des ....... de base.", ["Choisir...", "formules", "angles"], "formules", "dec_t7_final"),
        ("8. L'aire totale demeure .......... peu importe le decoupage choisi.", ["Choisir...", "invariante", "variable"], "invariante", "dec_t8_final"),
        ("9. Un trapeze peut se decomposer en un rectangle et deux ..........", ["Choisir...", "triangles", "disques"], "triangles", "dec_t9_final"),
        ("10. Assembler des sous-surfaces permet d'evaluer une extension.........", ["Choisir...", "totale", "partielle"], "totale", "dec_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Décomposition (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dec_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Décomposition (Texte à trous - 10 cases - 10 pts)")
        # RECTIFICATION ICI : Décompression des 4 éléments avec le symbole _
        for enonce, choix, _, cle in champs_d:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_simple_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 2 (Système Simple) sur deux colonnes."""
    ordre_fixe_tab2 = [
        {"id": "qs1", "q": "Si deux points ont exactement la même masse, où se situe le centre de gravité ?", "options": ["Exactement au milieu des deux points", "Confondu avec le premier point", "À l'extérieur du segment"], "rep": "Exactement au milieu des deux points"},
        {"id": "qs2", "q": "Plus la masse d'un point augmente par rapport aux autres, plus le centre de gravité G :", "options": ["S'éloigne de ce point", "Se rapproche de ce point", "Reste immobile"], "rep": "Se rapproche de ce point"},
        {"id": "qs3", "q": "Dans un champ de pesanteur uniforme, le centre de gravité se confond avec :", "options": ["Le centre de masse", "L'orthocentre", "Le point d'origine (0,0)"], "rep": "Le centre de masse"},
        {"id": "qs4", "q": "Quelle est la valeur de la masse totale M d'un système de 3 points (m1, m2, m3) ?", "options": ["M = m1 + m2 + m3", "M = m1 * m2 * m3", "M = (m1 + m2 + m3) / 3"], "rep": "M = m1 + m2 + m3"},
        {"id": "qs5", "q": "Si un système de 2 points possède une masse totale M, la coordonnée X_G est calculée par :", "options": ["(m1*x1 + m2*x2) / M", "(m1*x1 * m2*x2) / M", "(x1 + x2) / M"], "rep": "(m1*x1 + m2*x2) / M"}
    ]

    if "ordre_quiz_tab2_aleatoire" not in st.session_state:
        random.shuffle(ordre_fixe_tab2)
        st.session_state.ordre_quiz_tab2_aleatoire = ordre_fixe_tab2

    champs_s = [
        ("1. Le principe physique fondamental repose sur la loi du .........", ["Choisir...", "levier", "frottement"], "sim_t1_final"),
        ("2. Quand toutes les masses sont égales, G est l'......... du système.", ["Choisir...", "isobarycentre", "orthocentre"], "sim_t2_final"),
        ("3. Le centre de gravité se déplace vers le point le plus .........", ["Choisir...", "lourd", "léger"], "sim_t3_final"),
        ("4. Pour trouver G, on fait la moyenne ......... des coordonnées.", ["Choisir...", "pondérée", "arithmétique"], "sim_t4_final"),
        ("5. La coordonnée Y_G utilise les masses et les positions .........", ["Choisir...", "verticales", "horizontales"], "sim_t5_final")
    ]

    col_quiz2, col_trous2 = st.columns(2)
    with col_quiz2:
        st.markdown("##### Quiz Centre de Gravité Simple (5 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"sim_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous2:
        st.markdown("##### Synthèse Système Simple (Texte à trous - 5 cases - 10 pts)")
        for enonce, choix, cle in champs_s:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_complexe_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 3 (Système Complexe) sur deux colonnes."""
    ordre_fixe_tab3 = [
        {"id": "qc1", "q": "Pour calculer le centre de gravité d'une plaque percée d'un trou, on utilise :", "options": ["La méthode par soustraction (masse négative)", "La méthode par produit vectoriel", "L'addition simple des surfaces"], "rep": "La méthode par soustraction (masse négative)"},
        {"id": "qc2", "q": "Dans l'espace (3D), le calcul du centre de gravité nécessite en plus la coordonnée :", "options": ["Z_G", "R_G", "L'angle Théta"], "rep": "Z_G"},
        {"id": "qc3", "q": "Si un système possède un axe de symétrie géométrique et massique, le centre G :", "options": ["Se situe obligatoirement sur cet axe", "Est rejeté à l'infini", "Se place au point le plus bas"], "rep": "Se situe obligatoirement sur cet axe"},
        {"id": "qc4", "q": "L'isobarycentre de 4 points disposés aux sommets d'un carré parfait se trouve :", "options": ["À l'intersection des diagonales", "Sur l'un des sommets", "À l'extérieur du carré"], "rep": "À l'intersection des diagonales"},
        {"id": "qc5", "q": "En ingénierie mécanique, un centre de gravité placé très bas garantit :", "options": ["Une meilleure stabilité au renversement", "Une vitesse de pointe plus élevée", "Une diminution du poids total"], "rep": "Une meilleure stabilité au renversement"}
    ]

    # Initialisation unique de l'ordre aléatoire en mémoire de session
    if "ordre_quiz_tab3_aleatoire" not in st.session_state:
        random.shuffle(ordre_fixe_tab3)
        st.session_state.ordre_quiz_tab3_aleatoire = ordre_fixe_tab3

    champs_c = [
        ("1. Un solide évidé possède une zone géométrique appelée .........", ["Choisir...", "creuse", "pleine"], "comp_t1_final"),
        ("2. Multiplier les points massiques complexifie la ......... algébrique.", ["Choisir...", "sommation", "division"], "comp_t2_final"),
        ("3. Le comportement dynamique dépend de la distribution des .........", ["Choisir...", "masses", "volumes"], "comp_t3_final"),
        ("4. Une figure composite réunit plusieurs sous-surfaces .........", ["Choisir...", "élémentaires", "infinies"], "comp_t4_final"),
        ("5. Valider la position de G requiert une grande ......... de saisie.", ["Choisir...", "précision", "vitesse"], "comp_t5_final")
    ]

    col_quiz3, col_trous3 = st.columns(2)
    with col_quiz3:
        st.markdown("##### Quiz Centre de Gravité Complexe (5 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"comp_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous3:
        st.markdown("##### Synthèse Système Complexe (Texte à trous - 5 cases - 10 pts)")
        for enonce, choix, cle in champs_c:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")        

def afficher_atelier_metiers_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier Métiers sur deux colonnes."""
    ordre_fixe_tab4 = [
        {"id": "qm1", "q": "En transport routier, un centre de gravité placé trop haut provoque principalement :", "options": ["Un risque accru de retournement en virage", "Une augmentation de la vitesse maximale", "Une usure prématurée des freins uniquement"], "rep": "Un risque accru de retournement en virage"},
        {"id": "qm2", "q": "En travaux publics, avant le levage d'une structure composite, l'ingénieur doit :", "options": ["Déterminer le centre de gravité pour positionner les élingues", "Augmenter la puissance de la grue au hasard", "Mesurer uniquement la hauteur du sol"], "rep": "Déterminer le centre de gravité pour positionner les élingues"},
        {"id": "qm3", "q": "En maintenance, un défaut d'équilibrage d'une pièce tournante (barycentre excentré) génère :", "options": ["Des vibrations destructrices", "Une baisse immédiate de tension électrique", "Une lubrification automatique"], "rep": "Des vibrations destructrices"},
        {"id": "qm4", "q": "Pour un géomètre, la décomposition en surfaces élémentaires permet de trouver le CG d'un terrain :", "options": ["De forme irrégulière (polygone quelconque)", "Uniquement triangulaire", "Parfaitement circulaire"], "rep": "De forme irrégulière (polygone quelconque)"}
    ]
    st.session_state.ordre_quiz_tab4 = ordre_fixe_tab4

    champs_m = [
        ("1. Le chauffeur routier doit répartir les charges pour stabiliser le .........", ["Choisir...", "camion", "moteur"], "met_t1_final"),
        ("2. En TP, la position des points d'ancrage dépend du centre de .........", ["Choisir...", "gravité", "pression"], "met_t2_final"),
        ("3. En maintenance, réaligner le barycentre élimine le ......... de balourd.", ["Choisir...", "phénomène", "calcul"], "met_t3_final"),
        ("4. Le géomètre utilise des relevés de coordonnées pour sa .........", ["Choisir...", "polygonation", "peinture"], "met_t4_final")
    ]

    col_quiz4, col_trous4 = st.columns(2)
    with col_quiz4:
        st.markdown("##### Quiz Applications Métiers (4 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"met_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous4:
        st.markdown("##### Synthèse Métiers (Texte à trous - 4 cases - 10 pts)")
        for enonce, choix, cle in champs_m:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

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
    st.header("Définition et Principes Théoriques")
    
    # --- SECTION HISTORIQUE ---
    st.subheader("Contexte Historique")
    st.write(
        "Le concept de centre de gravité trouve ses racines dans l'Antiquité. C'est le savant grec "
        "**Archimède de Syracuse** (IIIe siècle av. J.-C.) qui en pose les bases géométriques et mathématiques "
        "dans son traité *Sur l'équilibre des figures planes*. Il définit le barycentre en démontrant "
        "la loi du levier. Plus tard, à l'époque moderne, des physiciens comme **Christiaan Huygens** et "
        "**Isaac Newton** ont généralisé ces principes pour les appliquer à la mécanique céleste et aux "
        "systèmes dynamiques complexes."
    )
    
    st.markdown("---")
    
    # --- SECTION PHYSIQUE ---
    st.subheader("Définition Physique")
    st.write(
        "Le **centre de gravité** d'un corps ou d'un système de points matériels correspond au "
        "point d'application de la résultante des forces de gravité qui s'exercent sur lui. Dans un "
        "champ de pesanteur uniforme (ce qui est le cas à la surface de la Terre pour des objets de taille "
        "courante), le centre de gravité se confond strictement avec le **centre de masse**."
    )
    
    st.markdown("---")
    
    # --- SECTION UTILITÉ ---
    st.subheader("Utilité pratique et domaines d'application")
    st.write(
        "Le calcul du centre de gravité est indispensable dans de nombreuses disciplines industrielles :"
    )
    st.write("- **Ingénierie aéronautique et automobile** : Déterminer la position du centre de gravité d'un avion ou d'une voiture de course est crucial pour garantir sa stabilité aérodynamique, sa tenue de route et éviter les risques de retournement.")
    st.write("- **Génie civil et architecture** : Pour concevoir des ponts, des bâtiments ou des grues, les ingénieurs doivent s'assurer que la ligne d'action du centre de gravité tombe à l'intérieur de la base d'appui (la surface de sustentation) afin d'éviter l'effondrement.")
    st.write("- **Biomécanique et sport** : L'analyse du centre de gravité du corps humain permet d'optimiser l'équilibre des athlètes (gymnastique, judo) ou d'améliorer l'ergonomie des prothèses.")

    st.markdown("---")
    
    # --- SECTION FORMULATION MATHÉMATIQUE ---
    st.subheader("Formulation Mathématique")
    st.write(
        "Pour un système composé de $N$ points matériels, où chaque point $A_i$ possède "
        "une masse $m_i$ et des coordonnées $(x_i, y_i)$, la masse totale $M$ du système est définie par :"
    )
    st.latex(r"M = \sum_{i=1}^{N} m_i = m_1 + m_2 + \dots + m_N")
    
    st.write("Les coordonnées $(X_G, Y_G)$ du centre de gravité $G$ sont données par les relations suivantes :")
    
    col_formule_x, col_formule_y = st.columns(2)
    with col_formule_x:
        st.info("**Coordonnée X_G**")
        st.latex(r"X_G = \frac{1}{M} \sum_{i=1}^{N} m_i x_i = \frac{m_1 x_1 + m_2 x_2 + \dots + m_N x_N}{m_1 + m_2 + \dots + m_N}")
    with col_formule_y:
        st.info("**Coordonnée Y_G**")
        st.latex(r"Y_G = \frac{1}{M} \sum_{i=1}^{N} m_i y_i = \frac{m_1 y_1 + m_2 y_2 + \dots + m_N y_N}{m_1 + m_2 + \dots + m_N}")


    st.write("---")        
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    afficher_atelier_decomposition_complet(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # La case à cocher accède maintenant à la variable sans lever d'erreur
    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Décomposition.",
        key="check_certif_generalites_final_net",
        disabled=verrou_at1,
    )
    # --- 4. BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_aleatoire:
                    reponse_eleve = st.session_state.get(f"dec_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = sum(
                [
                    st.session_state.get("dec_t1_final") == "exhaustive",
                    st.session_state.get("dec_t2_final") == "chevaucher",
                    st.session_state.get("dec_t3_final") == "additive",
                    st.session_state.get("dec_t4_final") == "vide",
                    st.session_state.get("dec_t5_final") == "composite",
                    st.session_state.get("dec_t6_final") == "soustraction",
                    st.session_state.get("dec_t7_final") == "formules",
                    st.session_state.get("dec_t8_final") == "invariante",
                    st.session_state.get("dec_t9_final") == "triangles",
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
        st.success(f"ATELIER DÉCOMPOSITION SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Décomposition - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Géométrie</h1>
                <p>Atelier 1 : Décomposition géométrique des surfaces complexes</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Décomposition : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab6" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6, 1):
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
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_suites,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Centre de Gravité Simple")
    st.write("Cette interface permet de calculer le centre de gravité pour un système de 2 ou 3 points.")

    if "suite_verrouille_tab2" not in st.session_state:
        st.session_state.suite_verrouille_tab2 = False
    verrou_at2 = st.session_state.suite_verrouille_tab2

    # --- 2. ENTRÉE DES DONNÉES ET GRAPHIQUE ---
    nb_points = st.radio("Sélectionnez le nombre de points :", [2, 3], horizontal=True, disabled=verrou_at2)     
    # Initialisation des structures de données
    masses = []
    coords_x = []
    coords_y = []
    
    # Création de colonnes dynamiques pour la saisie des données
    colonnes_saisie = st.columns(nb_points)
    
    for i in range(nb_points):
        with colonnes_saisie[i]:
            st.subheader(f"Point {i+1}")
            m = st.slider(f"Masse m{i+1} (kg)", min_value=1.0, max_value=50.0, value=10.0, step=0.5, key=f"m_simple_{i}")
            x = st.slider(f"Position X{i+1}", min_value=-10.0, max_value=10.0, value=float(i*4 - 4), step=0.5, key=f"x_simple_{i}")
            y = st.slider(f"Position Y{i+1}", min_value=-10.0, max_value=10.0, value=float(i*2 - 2), step=0.5, key=f"y_simple_{i}")
            
            masses.append(m)
            coords_x.append(x)
            coords_y.append(y)
            
    # --- CALCULS ---
    M_totale = sum(masses)
    X_G = sum(m * x for m, x in zip(masses, coords_x)) / M_totale
    Y_G = sum(m * y for m, y in zip(masses, coords_y)) / M_totale
    
    st.markdown("---")
    
    # Affichage des résultats numériques
    st.subheader("Résultats du calcul")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="Masse totale (M)", value=f"{M_totale:.2f} kg")
    with col_res2:
        st.metric(label="Coordonnée X_G", value=f"{X_G:.2f}")
    with col_res3:
        st.metric(label="Coordonnée Y_G", value=f"{Y_G:.2f}")
        
    # --- GRAPHIQUE ---
    st.subheader("Visualisation graphique")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Tracé des points du système (la taille dépend de la masse)
    for i in range(nb_points):
        taille = masses[i] * 10  # Facteur d'échelle pour la visibilité
        ax.scatter(coords_x[i], coords_y[i], s=taille, label=f"Point {i+1} ({masses[i]} kg)", alpha=0.7)
        ax.text(coords_x[i] + 0.3, coords_y[i] + 0.3, f"P{i+1}", fontsize=10, weight='bold')
        
    # Tracé du centre de gravité (représenté par une croix rouge)
    ax.scatter(X_G, Y_G, color='red', marker='x', s=200, linewidths=3, label="Centre de gravité (G)")
    ax.text(X_G + 0.3, Y_G - 0.5, "G", color='red', fontsize=12, weight='bold')
    
    # Paramétrages des axes
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel("Axe X")
    ax.set_ylabel("Axe Y")
    ax.legend(loc="upper left")
    
    # Intégration du graphique dans Streamlit
    st.pyplot(fig)

    
    st.write("---")
    
    # --- 3. APPEL DES QUESTIONS (Maintenant verrou_at2 est bien défini en amont !) ---
    afficher_atelier_simple_complet(verrouille=verrou_at2)

    # --- 4. SYNTHÈSE ET VALIDATION ---
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier Simple")
    
    # (Supprimez le bloc d'initialisation du verrou qui était ici !)
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Simple.",
        key="check_certif_simple_final_net",
        disabled=verrou_at2,
    )



    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (5 questions à 2 points chacune -> Max 10 points)
            score_q2 = 0.0
            if "ordre_quiz_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2:
                    reponse_eleve = st.session_state.get(f"sim_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q2 += 2.0

            # 2. Correction des Textes à trous (5 cases à 2 points chacune -> Max 10 points)
            score_t2 = sum(
                [
                    st.session_state.get("sim_t1_final") == "levier",
                    st.session_state.get("sim_t2_final") == "isobarycentre",
                    st.session_state.get("sim_t3_final") == "lourd",
                    st.session_state.get("sim_t4_final") == "pondérée",
                    st.session_state.get("sim_t5_final") == "verticales",
                ]
            ) * 2.0

            st.session_state.score_suite2_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2 = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 2 ---
    if st.session_state.get("suite_verrouille_tab2", False):
        scr1_2 = st.session_state.get("score_suite2_p1", 0.0)
        scr2_2 = st.session_state.get("score_suite2_p2", 0.0)
        tot_s2 = st.session_state.get("score_final_suite2", 0.0)

        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER SIMPLE SCELLÉ | Note de session : {tot_s2:.1f} / 20")

        html_export_simple = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Barycentre Simple - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0d9488; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique-Mécanique</h1>
                <p>Atelier 2 : Centre de gravité simple</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s2:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
                Note obtenue au Quiz Simple : <strong>{scr1_2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s2:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2, 1):
                saisie = st.session_state.get(f"sim_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_simple += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_simple += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_simple = preparer_nom_fichier("Rapport_Atelier_2").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_simple,
            file_name=nom_fichier_html_simple,
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("Centre de Gravité Complexe")
    st.write("Cette interface permet de gérer un grand nombre de points (de 4 à 10) à l'aide d'un tableau dynamique.")
    
    # --- GESTION DU VERROUILLAGE DE L'ATELIER 3 ---
    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3

    # Curseur pour le nombre de points complexes
    n_points_comp = st.slider("Sélectionnez le nombre de points du système :", min_value=4, max_value=10, value=5, step=1, disabled=verrou_at3)
    
    # Préparation des données par défaut pour le tableau éditable
    import pandas as pd
    if f"df_comp_{n_points_comp}" not in st.session_state:
        donnees_initiales = {
            "Point": [f"P{i+1}" for i in range(n_points_comp)],
            "Masse (kg)": [10.0] * n_points_comp,
            "Position X": [float(i * 2 - n_points_comp) for i in range(n_points_comp)],
            "Position Y": [float(((i**2) % 5) - 2) for i in range(n_points_comp)]
        }
        st.session_state[f"df_comp_{n_points_comp}"] = pd.DataFrame(donnees_initiales)

    # Affichage du tableau de données éditable
    st.write("Modifiez les valeurs directement dans le tableau ci-dessous :")
    df_edite = st.data_editor(
        st.session_state[f"df_comp_{n_points_comp}"],
        use_container_width=True,
        disabled=verrou_at3,
        hide_index=True
    )
    
    # Extraction des données modifiées
    try:
        masses_c = df_edite["Masse (kg)"].tolist()
        coords_xc = df_edite["Position X"].tolist()
        coords_yc = df_edite["Position Y"].tolist()
        
        # --- CALCULS PHYSIQUES ---
        M_totale_c = sum(masses_c)
        if M_totale_c <= 0:
            st.error("Erreur : La masse totale du système doit être strictement supérieure à 0.")
            X_Gc, Y_Gc = 0.0, 0.0
        else:
            X_Gc = sum(m * x for m, x in zip(masses_c, coords_xc)) / M_totale_c
            Y_Gc = sum(m * y for m, y in zip(masses_c, coords_yc)) / M_totale_c
    except Exception as e:
        st.error("Saisie invalide détectée dans le tableau. Veuillez vérifier vos nombres.")
        M_totale_c, X_Gc, Y_Gc = 1.0, 0.0, 0.0

    st.markdown("---")
    
    # Affichage des résultats numériques
    st.subheader("Résultats du calcul")
    col_resc1, col_resc2, col_resc3 = st.columns(3)
    with col_resc1:
        st.metric(label="Masse totale (M)", value=f"{M_totale_c:.2f} kg")
    with col_resc2:
        st.metric(label="Coordonnée X_G", value=f"{X_Gc:.2f}")
    with col_resc3:
        st.metric(label="Coordonnée Y_G", value=f"{Y_Gc:.2f}")
        
    # --- GRAPHIQUE ---
    st.subheader("Visualisation graphique")
    fig, ax = plt.subplots(figsize=(6, 4))
    
    for i in range(n_points_comp):
        # Facteur d'échelle adaptatif pour la taille des points graphiques
        taille = max(10, masses_c[i] * 5)
        ax.scatter(coords_xc[i], coords_yc[i], s=taille, alpha=0.6)
        ax.text(coords_xc[i] + 0.2, coords_yc[i] + 0.2, f"P{i+1}", fontsize=9)
        
    ax.scatter(X_Gc, Y_Gc, color='red', marker='x', s=200, linewidths=3, label="G (Centre de gravité)")
    ax.text(X_Gc + 0.3, Y_Gc - 0.5, "G", color='red', fontsize=12, weight='bold')
    
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel("Axe X")
    ax.set_ylabel("Axe Y")
    st.pyplot(fig)

    
    st.write("---")

    afficher_atelier_complexe_complet(verrouille=verrou_at3)

    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3  # <--- Création de la variable pour la tab2
    
    st.subheader("Questions d'évaluation de l'Atelier Complexe")

    st.write("---")
    st.subheader("Synthèse et validation sur les cercles")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
  
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les mesures et calculs de l'Atelier Centre de Gravité Complexe.",
        key="check_certif_complexe_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Complexe (5 questions x 2 pts -> Max 10 pts)
            score_q3 = 0.0
            if "ordre_quiz_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3:
                    reponse_eleve = st.session_state.get(f"comp_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 2.0

            # 2. Correction des Textes à trous Complexes (5 cases x 2 pts -> Max 10 pts)
            score_t3 = sum(
                [
                    st.session_state.get("comp_t1_final") == "creuse",
                    st.session_state.get("comp_t2_final") == "sommation",
                    st.session_state.get("comp_t3_final") == "masses",
                    st.session_state.get("comp_t4_final") == "élémentaires",
                    st.session_state.get("comp_t5_final") == "précision",
                ]
            ) * 2.0

            st.session_state.score_suite3_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3 = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 3 ---
    if st.session_state.get("suite_verrouille_tab3", False):
        scr1_3 = st.session_state.get("score_suite3_p1", 0.0)
        scr2_3 = st.session_state.get("score_suite3_p2", 0.0)
        tot_s3 = st.session_state.get("score_final_suite3", 0.0)

        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER COMPLEXE SCELLÉ | Note de session : {tot_s3:.1f} / 20")

        html_export_complexe = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Barycentre Complexe - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4338ca; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique-Mécanique</h1>
                <p>Atelier 3 : Centre de gravité complexe (système de {n_points_comp} points)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4338ca;">
                Note obtenue au Quiz Complexe : <strong>{scr1_3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s3:.1f} / 20</strong>
            </p>

            <div class="sub-title">Coordonnées Finales Calculées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4338ca;">
                Masse totale du système (M) : <strong>{M_totale_c:.2f} kg</strong><br>
                Position X_G : <strong>{X_Gc:.2f}</strong><br>
                Position Y_G : <strong>{Y_Gc:.2f}</strong>
            </p>
        </body>
        </html>
        """
        
        nom_fichier_html_complexe = preparer_nom_fichier("Rapport_Atelier_3").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_complexe,
            file_name=nom_fichier_html_complexe,
            mime="text/html",
            use_container_width=True
        )



with tab4:
    st.header("Applications Professionnelles et Métiers")
    st.write("Choisissez votre domaine de spécialité pour charger une étude de cas aléatoire sécurisée.")
    
    # --- 1. SÉCURITÉ DE LECTURE : INITIALISATION DU VERROU TOUT EN HAUT ---
    if "suite_verrouille_tab4" not in st.session_state:
        st.session_state.suite_verrouille_tab4 = False
    verrou_at4 = st.session_state.suite_verrouille_tab4

    # Menu déroulant de sélection du domaine métier
    metier_choisi = st.selectbox(
        "Sélectionnez votre domaine d'activité :",
        ["Transport Routier", "Travaux Publics", "Maintenance Industrielle", "Géomètre"],
        disabled=verrou_at4
    )

    st.markdown("---")

    # --- 2. APPEL DE LA DEF UNIQUE DU MODULE MÉTIER ÉTANCHE ---
    afficher_atelier_metiers_etanche(metier_choisi, verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier Spécialisé")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété l'étude de cas et le questionnaire technique lié à mon métier.",
        key="check_certif_metiers_etanche",
        disabled=verrou_at4,
    )

    # --- 3. COMPOSANT DE CORRECTION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_tab4_etanche", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "ELEVE") in ["ELEVE", ""] or st.session_state.get("prenom_var", "PRENOM") in ["PRENOM", ""]:
            st.error("Action refusée : Renseignez votre identité dans le premier onglet.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Récupération du scénario exact tiré au sort
            cle_session_cas = f"cas_attribue_{metier_choisi.replace(' ', '_')}"
            cas_actif = st.session_state.get(cle_session_cas)

            # A. Correction du QCM (10 questions -> Max 10 points soit 1 pt par bonne réponse)
            score_q4 = 0.0
            for q_item in cas_actif["quiz"]:
                reponse_saisie = st.session_state.get(f"met_quiz_ans_{cas_actif['id_cas']}_{q_item['id']}", "Choisir...")
                if str(reponse_saisie).strip() == str(q_item["rep"]).strip():
                    score_q4 += 1.0

            # B. Correction du Texte à trous (10 cases -> Max 10 points soit 1 pt par case exacte)
            score_t4 = 0.0
            for _, _, rep_attendue, cle_t in cas_actif["trous"]:
                reponse_trou = st.session_state.get(f"met_trou_ans_{cas_actif['id_cas']}_{cle_t}", "Choisir...")
                if str(reponse_trou).strip() == str(rep_attendue).strip():
                    score_t4 += 1.0

            # Enregistrement des scores finaux de la tab4 sur 20 points
            st.session_state.score_suite4_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4 = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4 = True
            st.rerun()

    # --- 4. EXPORTATION GENERALE DU RAPPORT HTML ADAPTATIF ---
    if st.session_state.get("suite_verrouille_tab4", False):
        scr1_4 = st.session_state.get("score_suite4_p1", 0.0)
        scr2_4 = st.session_state.get("score_suite4_p2", 0.0)
        tot_s4 = st.session_state.get("score_final_suite4", 0.0)
        timestamp_suite4 = datetime.datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER MÉTIERS SCELLÉ | Note obtenue pour le domaine {metier_choisi} : {tot_s4:.1f} / 20")

        cle_session_cas = f"cas_attribue_{metier_choisi.replace(' ', '_')}"
        cas_actif = st.session_state.get(cle_session_cas)

        html_export_metiers = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Applications Métiers - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b45309; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation Spécialité Métiers</h1>
                <p>Domaine professionnel sélectionné : {metier_choisi} ({cas_actif['titre']})</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes de l'Atelier</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b45309;">
                Note au QCM de Spécialité : <strong>{scr1_4:.1f} / 10</strong><br>
                Note à la Synthèse Technique : <strong>{scr2_4:.1f} / 10</strong><br>
                Note Globale d'Atelier 4 : <strong>{tot_s4:.1f} / 20</strong>
            </p>

            <div class="sub-title">Correction détaillée des 10 Questions du Quiz Métier</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Parcours adaptatif dynamique des 10 questions tirées au sort
        for num, q_item in enumerate(cas_actif["quiz"], 1):
            saisie = st.session_state.get(f"met_quiz_ans_{cas_actif['id_cas']}_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_metiers += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_metiers += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_metiers = preparer_nom_fichier("Rapport_Atelier_4").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_metiers,
            file_name=nom_fichier_html_metiers,
            mime="text/html",
            use_container_width=True
        )




    
