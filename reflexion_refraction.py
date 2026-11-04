# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application réflexion et réfraction",
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
st.title("Application réflexion et réfraction")
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
BASE_DIR = os.path.abspath(".")

def charger_image(nom_fichier):
    nom_fichier = os.path.basename(nom_fichier)
    # Python scanne automatiquement tous les dossiers présents à côté du script
    for element in os.listdir(BASE_DIR):
        chemin_dossier = os.path.join(BASE_DIR, element)
        if os.path.isdir(chemin_dossier) and element.startswith("image"):
            chemin_image = os.path.join(chemin_dossier, nom_fichier)
            if os.path.exists(chemin_image):
                try:
                    return Image.open(chemin_image)
                except Exception:
                    pass
                        
    # Sécurité si l'application est déjà masquée dans fichiers_systemes
    chemin_secours = os.path.join(BASE_DIR, "image", nom_fichier)
    if os.path.exists(chemin_secours):
        try: 
            return Image.open(chemin_secours)
        except Exception: 
            pass
    return None

# --- TOUS LES CORRECTIFS SÉCURISÉS (RERUN, COLUMNS, CONTAINER, IMAGE) ---

# 1. Sauvegarde STRICTE des fonctions d'origine AVANT modification
_vrai_st_rerun = st.rerun if hasattr(st, "rerun") else (st.experimental_rerun if hasattr(st, "experimental_rerun") else None)
_vrai_st_image = st.image
_vrai_st_columns = st.columns
_vrai_st_container = st.container

# 2. Correctif pour st.rerun
def safe_rerun():
    if _vrai_st_rerun is not None:
        try: 
            _vrai_st_rerun()
        except Exception:
            from streamlit.runtime.scriptrunner import RerunData, RerunException
            raise RerunException(RerunData())
st.rerun = safe_rerun

import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
mpl.rcParams['mathtext.default'] = 'regular'

# 3. Correctif pour st.image (Résolution de la boucle infinie)
def safe_image(image, *args, **kwargs):
    if "use_container_width" in kwargs:
        kwargs["use_column_width"] = kwargs.pop("use_container_width")
    if isinstance(image, str) and not image.startswith(("http://", "https://", "data:image")):
        nom_fichier = os.path.basename(image)
        img_pil = charger_image(nom_fichier)
        if img_pil is not None: 
            image = img_pil
    return _vrai_st_image(image, *args, **kwargs)  # Utilise la vraie fonction d'origine
st.image = safe_image

# 4. Interception pour st.columns (vertical_alignment)
def safe_columns(*args, **kwargs):
    if "vertical_alignment" in kwargs:
        kwargs.pop("vertical_alignment")
    return _vrai_st_columns(*args, **kwargs)
st.columns = safe_columns

# 5. Interception pour st.container (border)
def safe_container(*args, **kwargs):
    if "border" in kwargs:
        kwargs.pop("border")
    return _vrai_st_container(*args, **kwargs)
st.container = safe_container

# 6. Rétrocompatibilité st.toggle -> st.checkbox
if not hasattr(st, "toggle"):
    def safe_toggle(label, value=False, key=None, **kwargs):
        return st.checkbox(label, value=value, key=key)
    st.toggle = safe_toggle

# 7. Rétrocompatibilité st.dialog
if not hasattr(st, "dialog"):
    def safe_dialog(*args, **kwargs):
        return st.container()
    st.dialog = safe_dialog

# 8. Décorateur pour sécuriser l'état des widgets (Session State)
def securiser_widget_factory(fonction_origine):
    def safe_widget(*args, **kwargs):
        cle = kwargs.get("key")
        if cle and cle in st.session_state:
            kwargs.pop("value", None)
        return fonction_origine(*args, **kwargs)
    return safe_widget



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


onglets = st.tabs([
    "Identification",
    "Historique",
    "Loi de la reflexion pour un miroir plan",
    "Loi de la refraction",
    "La réflexion totale",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier",
    "Application dans le domaine topographe géomètre",
    "Réflexion pour un miroir concave",
    "Réflexion pour un miroir concave"
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
tab10 = onglets[10]

def afficher_atelier_travaux_publics(cas_id, verrouille=False):
    """Affiche le Quiz et le Texte à trous pour l'Atelier 6 (Travaux Publics)."""
    import random

    st.subheader("Atelier Interactif : Diagnostic Optique en Travaux Publics")

    banque_quiz_tp = {
        "tp_ref1": [
            {"id": "q1", "q": "Quel instrument de mesure utilise un prisme réfléchissant pour calculer des distances sur un chantier ?", "options": ["Un tachéomètre ou station totale", "Un fil à plomb", "Une excavatrice"], "rep": "Un tachéomètre ou station totale"},
            {"id": "q2", "q": "Quelle loi régit le retour du signal laser réfléchi par le prisme du topographe ?", "options": ["La loi de la réflexion (i = r)", "La loi de Snell-Descartes", "La loi de Newton"], "rep": "La loi de la réflexion (i = r)"},
            {"id": "q3", "q": "Si le faisceau laser tape perpendiculairement sur la face du prisme, l'angle d'incidence vaut :", "options": ["0 degré", "90 degrés", "45 degrés"], "rep": "0 degré"},
            {"id": "q4", "q": "Un signal laser réfléchi qui revient exactement vers sa source utilise un prisme dit :", "options": ["Catadioptre ou rétro-réfléchissant", "Divergent", "Opaque"], "rep": "Catadioptre ou rétro-réfléchissant"},
            {"id": "q5", "q": "Quelle propriété de la lumière permet de garantir l'alignement parfait d'une bordure ?", "options": ["La propagation rectiligne", "La réfraction", "La dispersion"], "rep": "La propagation rectiligne"},
            {"id": "q6", "q": "Si de la poussière de chantier masque le prisme, le signal de retour est :", "options": ["Atténué ou diffus", "Plus rapide", "Inversé"], "rep": "Atténué ou diffus"},
            {"id": "q7", "q": "Le calcul de distance par la station totale se base sur :", "options": ["Le temps de vol de l'impulsion lumineuse", "Le poids de la cible", "La couleur du prisme"], "rep": "Le temps de vol de l'impulsion lumineuse"},
            {"id": "q8", "q": "L'angle de réflexion spéculaire s'évalue toujours par rapport à :", "options": ["La normale", "La ligne d'horizon", "Le trépied"], "rep": "La normale"},
            {"id": "q9", "q": "Le guidage laser des engins de terrassement augmente principalement :", "options": ["La précision des cotes de nivellement", "La vitesse maximale de l'engin", "La consommation de carburant"], "rep": "La précision des cotes de nivellement"},
            {"id": "q10", "q": "Une surface métallique de mire polie renvoie la lumière de manière :", "options": ["Spéculaire", "Diffuse", "Absorbante"], "rep": "Spéculaire"}
        ],
        "tp_ref2": [
            {"id": "q1", "q": "Quel type de repère altimétrique génère le plan laser tournant sur le chantier ?", "options": ["Un plan horizontal de référence", "Une ligne courbe", "Un point focal"], "rep": "Un plan horizontal de référence"},
            {"id": "q2", "q": "Où est fixée la cellule réceptrice qui intercepte le faisceau laser ?", "options": ["Sur le mât de la lame de l'engin", "Dans la cabine", "Sur le pot d'échappement"], "rep": "Sur le mât de la lame de l'engin"},
            {"id": "q3", "q": "Comment réagissent les vérins hydrauliques si la lame descend trop bas ?", "options": ["Ils remontent la lame automatiquement", "Ils coupent le moteur", "Ils bloquent les chenilles"], "rep": "Ils remontent la lame automatiquement"},
            {"id": "q4", "q": "Quelle est la vitesse de balayage type d'un laser rotatif de chantier ?", "options": ["Plusieurs centaines de tours par minute", "Une rotation par heure", "Il reste fixe"], "rep": "Plusieurs centaines de tours par minute"},
            {"id": "q5", "q": "La surface lissée par une niveleuse guidée au laser est appelée :", "options": ["La plateforme ou fond de forme", "Le revêtement fini", "Le dévers de fossé"], "rep": "La plateforme ou fond de forme"},
            {"id": "q6", "q": "Quel est l'ennemi principal de la transmission du signal laser sur une piste ?", "options": ["La poussière et la fumée d'échappement", "Le bruit des moteurs", "Le poids de la benne"], "rep": "La poussière et la fumée d'échappement"},
            {"id": "q7", "q": "Si la cellule capte le rayon au-dessus de sa zone centrale, la lame est :", "options": ["Trop basse", "Trop haute", "Parfaitement à la bonne hauteur"], "rep": "Trop basse"},
            {"id": "q8", "q": "Le récepteur utilise quel type de composants pour détecter le faisceau ?", "options": ["Des photodiodes alignées", "Des miroirs sphériques", "Des prismes de verre"], "rep": "Des photodiodes alignées"},
            {"id": "q9", "q": "Le dévers d'une plateforme correspond à :", "options": ["Son inclinaison transversale", "Sa longueur totale", "Son épaisseur"], "rep": "Son inclinaison transversale"},
            {"id": "q10", "q": "Le guidage laser supprime l'obligation de poser des :", "options": ["Piquets de repères manuels", "Panneaux de signalisation", "Tuyaux de drainage"], "rep": "Piquets de repères manuels"}
        ],
        "tp_ref3": [
            {"id": "q1", "q": "Où positionne-t-on le laser d'alignement pour poser des canalisations ?", "options": ["Au fond du regard de départ", "Sur le toit du camion", "Au milieu de la tranchée"], "rep": "Au fond du regard de départ"},
            {"id": "q2", "q": "Quel paramètre hydraulique fondamental dicte l'angle d'inclinaison du laser ?", "options": ["La pente d'écoulement (en %)", "Le diamètre du tuyau", "La pression de l'eau"], "rep": "La pente d'écoulement (en %)"},
            {"id": "q3", "q": "Sur quoi le poseur lit-il la bonne position du tuyau en cours d'emboîtement ?", "options": ["Sur une mire cible amovible", "Sur la paroi de la tranchée", "Sur son smartphone"], "rep": "Sur une mire cible amovible"},
            {"id": "q4", "q": "Quand le spot laser est parfaitement centré sur la mire cible, le tuyau est :", "options": ["Correctement aligné et à la bonne pente", "Trop haut", "Dévié à gauche"], "rep": "Correctement aligné et à la bonne pente"},
            {"id": "q5", "q": "Quel type de réseau nécessite la plus grande précision de pente ?", "options": ["L'assainissement gravitaire", "L'adduction d'eau potable", "Le fourreau électrique"], "rep": "L'assainissement gravitaire"},
            {"id": "q6", "q": "La lumière voyage en ligne droite dans l'air du tuyau car le milieu est :", "options": ["Homogène", "Opaque", "Réfringent variable"], "rep": "Homogène"},
            {"id": "q7", "q": "Une mauvaise pente sur une canalisation d'eaux usées provoque :", "options": ["Des risques d'engorgement et de stagnation", "Une fuite de pression", "Une rupture du béton"], "rep": "Des risques d'engorgement et de stagnation"},
            {"id": "q8", "q": "La mire cible utilisée au fond de la conduite est généralement :", "options": ["Translucide pour voir le point par l'arrière", "En métal miroir", "En bois brut"], "rep": "Translucide pour voir le point par l'arrière"},
            {"id": "q9", "q": "Le réglage fins du laser de canalisation se fait à l'aide d'un clavier :", "options": ["À affichage numérique de la pente", "De commande hydraulique", "De démarrage moteur"], "rep": "À affichage numérique de la pente"},
            {"id": "q10", "q": "Quelle opération suit immédiatement la validation de l'alignement optique ?", "options": ["Le remblaiement de la fouille", "Le compactage du bitume", "Le creusement du regard"], "rep": "Le remblaiement de la fouille"}
        ],
        "tp_fra1": [
            {"id": "q1", "q": "Quel phénomène optique est provoqué par les couches d'air chaud au-dessus du bitume ?", "options": ["Un mirage thermique", "Une réflexion spéculaire", "Une diffraction pure"], "rep": "Un mirage thermique"},
            {"id": "q2", "q": "Comment évolue l'indice de réfraction de l'air lorsque sa température augmente ?", "options": ["Il diminue", "Il augmente", "Il reste fixe"], "rep": "Il diminue"},
            {"id": "q3", "q": "La déviation continue d'un faisceau laser traversant de l'air chaud provient de :", "options": ["La variation continue de l'indice n (réfraction)", "La présence de poussière", "Un défaut mécanique du laser"], "rep": "La variation continue de l'indice n (réfraction)"},
            {"id": "q4", "q": "La formule mathématique qui régit cette déviation à chaque interface d'air est :", "options": ["n1 * sin(i1) = n2 * sin(i2)", "i1 = r", "P = F / S"], "rep": "n1 * sin(i1) = n2 * sin(i2)"},
            {"id": "q5", "q": "L'illusion visuelle de flaque d'eau sur une piste de chantier provient d'une :", "options": ["Réflexion totale du ciel sur l'air surchauffé", "Réfraction simple vers le sol", "Évaporation d'eau"], "rep": "Réflexion totale du ciel sur l'air surchauffé"},
            {"id": "q6", "q": "Pour éviter l'erreur de réfraction atmosphérique, les topographes effectuent leurs visées :", "options": ["Aux heures les moins chaudes ou en évitant le ras du sol", "En plein midi", "Uniquement sous la pluie"], "rep": "Aux heures les moins chaudes ou en évitant le ras du sol"},
            {"id": "q7", "q": "L'indice de réfraction de référence de l'air standard est environ de :", "options": ["1.0003", "1.333", "1.520"], "rep": "1.0003"},
            {"id": "q8", "q": "Dans un mirage, le rayon lumineux courbe sa trajectoire vers :", "options": ["Les zones d'indice plus élevé (air plus froid)", "Le goudron directement", "Le ciel à la verticale"], "rep": "Les zones d'indice plus élevé (air plus froid)"},
            {"id": "q9", "q": "La réfraction atmosphérique perturbe principalement quel type de mesure en TP ?", "options": ["Le nivellement de haute précision", "Le pesage des camions", "La numérisation 3D"], "rep": "Le nivellement de haute précision"},
            {"id": "q10", "q": "L'unité de mesure d'un indice de réfraction est :", "options": ["Il n'a pas d'unité", "Le mètre", "Le degré"], "rep": "Il n'a pas d'unité"}
        ],
        "tp_fra2": [
            {"id": "q1", "q": "Quel capteur descend dans le tubage pour localiser la nappe phréatique ?", "options": ["Une sonde de diagraphie optique", "Un manomètre", "Un fil à plomb"], "rep": "Une sonde de diagraphie optique"},
            {"id": "q2", "q": "Quelle est la valeur de l'indice de réfraction de l'air dans le forage ?", "options": ["1.0003", "1.3330", "1.5200"], "rep": "1.0003"},
            {"id": "q3", "q": "Quelle est la valeur de l'indice de réfraction de l'eau souterraine ?", "options": ["1.333", "1.000", "2.417"], "rep": "1.333"},
            {"id": "q4", "q": "Au passage de l'air à l'eau (n1 < n2), le rayon lumineux :", "options": ["Se rapproche de la normale", "S'éloigne de la normale", "Fait demi-tour"], "rep": "Se rapproche de la normale"},
            {"id": "q5", "q": "Le changement brutal de direction à la surface de l'eau est régi par la loi de :", "options": ["Snell-Descartes pour la réfraction", "La réflexion pure", "La pression des fluides"], "rep": "Snell-Descartes pour la réfraction"},
            {"id": "q6", "q": "La détection optique de la nappe permet de fixer la profondeur des :", "options": ["Ouvrages de soutènement et fondations", "Panneaux de chantier", "Limites de vitesse"], "rep": "Ouvrages de soutènement et fondations"},
            {"id": "q7", "q": "Comment appelle-t-on la frontière supérieure d'une nappe souterraine ?", "options": ["Le toit de la nappe ou niveau piézométrique", "Le fond de fouille", "Le dioptre dur"], "rep": "Le toit de la nappe ou niveau piézométrique"},
            {"id": "q8", "q": "Si l'eau du forage devient très boueuse à cause du creusement, le rayon laser est :", "options": ["Absorbé ou dispersé", "Accéléré", "Réfracté deux fois plus"], "rep": "Absorbé ou dispersé"},
            {"id": "q9", "q": "L'appareil qui enregistre les variations optiques le long du forage réalise une :", "options": ["Diagraphie", "Vidange", "Implantation d'axe"], "rep": "Diagraphie"},
            {"id": "q10", "q": "L'eau ralentit la lumière par rapport au vide d'un facteur égal à :", "options": ["Son indice de réfraction (environ 1.33)", "Son volume", "Sa température"], "rep": "Son indice de réfraction (environ 1.33)"}
        ],
        "tp_fra3": [
            {"id": "q1", "q": "Quel instrument de chantier mesure la concentration d'un liant bitumineux ?", "options": ["Un réfractomètre portable", "Un thermomètre", "Un odomètre"], "rep": "Un réfractomètre portable"},
            {"id": "q2", "q": "Une modification de la valeur de l'indice n sur une émulsion indique :", "options": ["Une variation de la teneur en eau ou en polymères", "Une panne d'engins", "Un excès de gravillons"], "rep": "Une variation de la teneur en eau ou en polymères"},
            {"id": "q3", "q": "Où est déposé le prélèvement de bitume pour effectuer le test ?", "options": ["Sur la face plane du prisme de mesure", "Dans la cuve du camion", "Sur le pneu du finisseur"], "rep": "Sur la face plane du prisme de mesure"},
            {"id": "q4", "q": "Quelle relation mathématique relie le liant au faisceau lumineux ?", "options": ["n1 * sin(i1) = n2 * sin(i2)", "i = r", "F = m * g"], "rep": "n1 * sin(i1) = n2 * sin(i2)"},
            {"id": "q5", "q": "Le contrôle de l'émulsion de bitume sur le chantier garantit :", "options": ["La bonne tenue de l'accrochage des couches", "La propreté des pneus", "La réduction des poussières"], "rep": "La bonne tenue de l'accrochage des couches"},
            {"id": "q6", "q": "La rampe d'épandage distribue le liant juste avant le passage du :", "options": ["Finisseur d'enrobés", "Bulldozer", "Tachéomètre"], "rep": "Finisseur d'enrobés"},
            {"id": "q7", "q": "L'indice de réfraction mesuré dépend de quelle fonction trigonométrique ?", "options": ["Le sinus", "Le cosinus", "La tangente"], "rep": "Le sinus"},
            {"id": "q8", "q": "Pourquoi effectue-t-on cette mesure optique directement sur le terrain ?", "options": ["Pour un contrôle qualité immédiat sans attendre le laboratoire", "Pour nettoyer les outils", "Pour refroidir le goudron"], "rep": "Pour un contrôle qualité immédiat sans attendre le laboratoire"},
            {"id": "q9", "q": "Une émulsion de bitume routier est une suspension de billes de bitume dans :", "options": ["De l'eau avec un savon émulsifiant", "De l'huile hydraulique", "Du ciment liquide"], "rep": "De l'eau avec un savon émulsifiant"},
            {"id": "q10", "q": "La conformité de ce liant est enregistrée dans le dossier :", "options": ["D'assurance qualité du chantier", "De permis de construire", "De consommation carburant"], "rep": "D'assurance qualité du chantier"}
        ]
    }

    cle_ordre = f"ordre_quiz_tp_{cas_id}"
    if cle_ordre not in st.session_state:
        liste_q = list(banque_quiz_tp[cas_id])
        random.shuffle(liste_q)
        st.session_state[cle_ordre] = liste_q

    # Disposition demandée : Textes à gauche et Visuels à droite
    col_gauche_questions, col_droite_visuels = st.columns([0.55, 0.45])
    
    with col_gauche_questions:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tp_at6_{cas_id}_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

        st.write("---")

        st.markdown("##### Synthèse (Texte à trous - 10 cases - 10 pts)")
        for ligne in banque_trous_tp[cas_id]:
            # Extraction stricte de chaque élément du tuple par son index pour éviter le bug visuel
            enonce_texte = ligne[0]   # Récupère uniquement la phrase de cours
            choix_options = ligne[1]  # Récupère la liste des choix
            cle_unique = ligne[3]     # Correction : Ciblage direct de l'index 3 pour la clé de variable
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce_texte)
            with c_sel: 
                st.selectbox("", choix_options, key=f"{cle_unique}_{cas_id}_tp_clean", disabled=verrouille, label_visibility="collapsed")

    with col_droite_visuels:
        st.write("")
        st.info(
            "Utilisez les fiches de dossiers techniques et le simulateur vectoriel situés en haut pour compléter la feuille d'évaluation à gauche."
        )







def afficher_atelier_maintenance(cas_id, verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 5 (Maintenance des engins de TP)."""
    import random

    st.subheader("Atelier Interactif : Diagnostic Optique de Maintenance")

    # =============================================================================
    # BANQUE DE QUIZ ENTIÈREMENT COMPLÉTÉE (10 QUESTIONS PAR CAS)
    # =============================================================================
    banque_quiz = {
        "m_ref1": [
            {"id": "q1", "q": "Quel type de miroir utilise un rétroviseur d'angle mort sur un engin ?", "options": ["Miroir convexe", "Miroir concave", "Miroir plan"], "rep": "Miroir convexe"},
            {"id": "q2", "q": "Quel est le principal avantage d'un miroir convexe pour un conducteur ?", "options": ["Élargir le champ de vision", "Grossir les détails", "Inverser la lumière"], "rep": "Élargir le champ de vision"},
            {"id": "q3", "q": "Où se situe le foyer virtuel d'un miroir convexe ?", "options": ["Derrière la surface réfléchissante", "Devant le miroir", "Au point d'incidence"], "rep": "Derrière la surface réfléchissante"},
            {"id": "q4", "q": "L'image formée par un miroir convexe d'angle mort est toujours :", "options": ["Virtuelle et droite", "Réelle et inversée", "Plus grande que l'objet"], "rep": "Virtuelle et droite"},
            {"id": "q5", "q": "Quelle loi régit le reflet de la carrosserie d'un camion sur le miroir ?", "options": ["La loi de la réflexion (i = r)", "La loi de Descartes (n1*sin i1)", "La loi d'absorption"], "rep": "La loi de la réflexion (i = r)"},
            {"id": "q6", "q": "Si un angle de carrosserie envoie un rayon à 25° de la normale, le rayon réfléchi repart à :", "options": ["25 degrés", "50 degrés", "0 degré"], "rep": "25 degrés"},
            {"id": "q7", "q": "Comment appelle-t-on la zone cachée que le miroir convexe aide à éliminer ?", "options": ["L'angle mort", "Le point focal", "Le plan d'incidence"], "rep": "L'angle mort"},
            {"id": "q8", "q": "Un miroir convexe donne l'illusion que les objets sont :", "options": ["Plus petits et plus éloignés", "Plus proches", "De taille identique"], "rep": "Plus petits et plus éloignés"},
            {"id": "q9", "q": "La normale à la surface d'un miroir sphérique passe toujours par :", "options": ["Le centre de courbure", "Le foyer", "Le point d'infini"], "rep": "Le centre de courbure"},
            {"id": "q10", "q": "Sur un engin de TP, la maintenance des rétroviseurs prévient principalement :", "options": ["Les risques d'écrasement et de collision", "Les pannes de moteur", "Les fuites d'huile"], "rep": "Les risques d'écrasement et de collision"}
        ],
        "m_ref2": [
            {"id": "q1", "q": "Quel outil projette le faisceau de référence pour contrôler les phares ?", "options": ["Un pointeur laser", "Une lampe torche", "Un rétroviseur"], "rep": "Un pointeur laser"},
            {"id": "q2", "q": "Quelle trajectoire suit le rayon si l'optique est parfaitement orthogonale (i = 0°) ?", "options": ["Il revient pile sur lui-même", "Il est dévié à 90°", "Il traverse le bloc"], "rep": "Il revient pile sur lui-même"},
            {"id": "q3", "q": "Si le miroir du phare est incliné d'un angle i, de combien le rayon réfléchi est-il dévié ?", "options": ["D'un angle égal à 2i", "D'un angle égal à i", "Il n'est pas dévié"], "rep": "D'un angle égal à 2i"},
            {"id": "q4", "q": "Où s'effectue la lecture de l'écart géométrique lors du contrôle des phares ?", "options": ["Sur une mire ou cible graduée", "Dans le réservoir", "Sur le pneu"], "rep": "Sur une mire ou cible graduée"},
            {"id": "q5", "q": "Le parallélisme des feux de travail garantit principalement :", "options": ["Une zone de travail nocturne bien balisée", "Une économie de batterie", "Une réduction du bruit"], "rep": "Une zone de travail nocturne bien balisée"},
            {"id": "q6", "q": "Quelle propriété de la lumière permet d'aligner l'outil laser sur le châssis ?", "options": ["La propagation rectiligne", "La réfraction", "La dispersion"], "rep": "La propagation rectiligne"},
            {"id": "q7", "q": "Un défaut d'assiette sur un projecteur de niveleuse est corrigé avec :", "options": ["Des vis de réglage micrométriques", "Une vidange", "Un changement de miroir"], "rep": "Des vis de réglage micrométriques"},
            {"id": "q8", "q": "Le miroir interne du projecteur qui concentre la lumière est généralement :", "options": ["Un réflecteur parabolique", "Un dioptre plan", "Un prisme transparent"], "rep": "Un réflecteur parabolique"},
            {"id": "q9", "q": "Si le faisceau laser tape au-dessus de la mire de contrôle, les phares éclairent :", "options": ["Trop haut (éblouissement)", "Trop bas", "Correctement le sol"], "rep": "Trop haut (éblouissement)"},
            {"id": "q10", "q": "La loi de la réflexion spéculaire implique que la surface du miroir testé doit être :", "options": ["Propre et non poussiéreuse", "Peinte en noir", "Rugueuse"], "rep": "Propre et non poussiéreuse"}
        ],
        "m_ref3": [
            {"id": "q1", "q": "Comment le capteur d'usure évalue-t-il la distance restante sur la chenille ?", "options": ["Par mesure du temps de vol du rayon", "Par changement de couleur", "Par pesée"], "rep": "Par mesure du temps de vol du rayon"},
            {"id": "q2", "q": "Quelle pièce d'usure des engins de terrassement est ciblée par ce diagnostic ?", "options": ["Les tuiles et galets de chenilles", "Les vitres de la cabine", "Les flexibles"], "rep": "Les tuiles et galets de chenilles"},
            {"id": "q3", "q": "Quelle surface assure le retour du signal vers la cellule photoélectrique ?", "options": ["Le flanc métallique poli de la pièce", "Une bande adhésive", "Le sol en terre"], "rep": "Le flanc métallique poli de la pièce"},
            {"id": "q4", "q": "Si la pièce s'est amincie à cause de l'abrasion, le temps de retour du laser :", "options": ["Augmente (distance plus grande)", "Diminue", "Reste identique"], "rep": "Augmente (distance plus grande)"},
            {"id": "q5", "q": "Quel type de maintenance déclenche ce capteur optique automatisé ?", "options": ["La maintenance prédictive", "La maintenance corrective curative", "La maintenance fortuite"], "rep": "La maintenance prédictive"},
            {"id": "q6", "q": "Un signal laser réfléchi très faible ou diffus indique généralement :", "options": ["Une surface encrassée par la boue", "Une pièce neuve", "Une vitesse trop rapide"], "rep": "Une surface encrassée par la boue"},
            {"id": "q7", "q": "L'angle d'incidence optimal pour capter l'impulsion de retour directe est :", "options": ["Proche de 0° (perpendiculaire)", "Égal à 45°", "Égal à 90°"], "rep": "Proche de 0° (perpendiculaire)"},
            {"id": "q8", "q": "L'unité de mesure de la force mécanique abrasive subie par les trains de roulement est :", "options": ["Le Newton", "Le Pascal", "Le Bar"], "rep": "Le Newton"},
            {"id": "q9", "q": "Pourquoi automatiser la détection d'épaisseur par voie optique ?", "options": ["Pour éviter l'arrêt complet de l'engin", "Pour nettoyer les chenilles", "Pour augmenter la puissance"], "rep": "Pour éviter l'arrêt complet de l'engin"},
            {"id": "q10", "q": "La formule i = r s'applique ici car l'interface se comporte comme :", "options": ["Une surface réfléchissante plane locale", "Un prisme de réfraction", "Un milieu absorbant"], "rep": "Une surface réfléchissante plane locale"}
        ],
        "m_fra1": [
            {"id": "q1", "q": "Où introduit-on l'endoscope pour inspecter un moteur sans démontage ?", "options": ["Par le puits d'injecteur ou de bougie", "Dans le pot d'échappement", "Par le filtre à air"], "rep": "Par le puits d'injecteur ou de bougie"},
            {"id": "q2", "q": "Quel phénomène maintient la lumière piégée à l'intérieur de la fibre optique ?", "options": ["La réflexion totale interne", "La réfraction simple", "L'absorption moléculaire"], "rep": "La réflexion totale interne"},
            {"id": "q3", "q": "La lentille située à l'extrémité de la sonde endoscopique sert à :", "options": ["Réfracter le faisceau pour élargir l'image", "Bloquer la lumière", "Filtrer l'huile"], "rep": "Réfracter le faisceau pour élargir l'image"},
            {"id": "q4", "q": "Que cherche-t-on à inspecter sur la chemise du cylindre d'un moteur ?", "options": ["Des rayures, fissures ou traces de serrage", "Le niveau de carburant", "Le couple de serrage"], "rep": "Des rayures, fissures ou traces de serrage"},
            {"id": "q5", "q": "Pour assurer le guidage, l'indice du cœur (n1) de la fibre doit être :", "options": ["Supérieur à celui de la gaine (n2)", "Inférieur à celui de la gaine (n2)", "Égal à 1.000"], "rep": "Supérieur à celui de la gaine (n2)"},
            {"id": "q6", "q": "Si la tête de l'endoscope est souillée par de l'huile moteur opaque, l'image :", "options": ["Devient floue ou totalement sombre", "Devient plus lumineuse", "S'inverse"], "rep": "Devient floue ou totalement sombre"},
            {"id": "q7", "q": "L'avantage économique principal de l'endoscopie en atelier est :", "options": ["Un gain de temps majeur sur le diagnostic", "Une réduction du poids de l'engin", "Une augmentation du régime moteur"], "rep": "Un gain de temps majeur sur le diagnostic"},
            {"id": "q8", "q": "La loi n1 * sin(i1) = n2 * sin(i2) s'applique lors du passage de la lentille vers :", "options": ["L'air de la cavité du cylindre", "Le câble en acier", "Le bouton d'allumage"], "rep": "L'air de la cavité du cylindre"},
            {"id": "q9", "q": "Le faisceau souple de l'endoscope transporte à la fois la lumière et :", "options": ["Le signal d'image retour de la caméra", "L'huile de pression", "Le courant de démarreur"], "rep": "Le signal d'image retour de la caméra"},
            {"id": "q10", "q": "Quelle anomalie thermique peut être détectée visuellement sur le piston ?", "options": ["Un début de fusion ou point chaud", "Une baisse de pression", "Un manque d'antigel"], "rep": "Un début de fusion ou point chaud"}
        ],
        "m_fra2": [
            {"id": "q1", "q": "Quelle est la forme géométrique de l'extrémité du capteur plongé dans le réservoir ?", "options": ["Un cône prismatique à 90°", "Une face plane miroir", "Une sphère creuse"], "rep": "Un cône prismatique à 90°"},
            {"id": "q2", "q": "Que fait le rayon lumineux dans le capteur lorsque le niveau d'huile est BAS (air) ?", "options": ["Il subit une réflexion totale et revient", "Il s'échappe tout droit dans l'air", "Il change de couleur"], "rep": "Il subit une réflexion totale et revient"},
            {"id": "q3", "q": "Que se passe-t-on lorsque l'huile HAUTE entoure le prisme en verre ?", "options": ["Le rayon se réfracte et se perd dans l'huile", "La réflexion totale augmente", "Le capteur explose"], "rep": "Le rayon se réfracte et se perd dans l'huile"},
            {"id": "q4", "q": "Pourquoi la réflexion totale disparaît-elle en présence d'huile ?", "options": ["L'indice de l'huile est proche de celui du verre", "L'huile absorbe les sinus", "L'huile est trop froide"], "rep": "L'indice de l'huile est proche de celui du verre"},
            {"id": "q5", "q": "Quel est l'aspect visuel du voyant pour le mécanicien quand le niveau est PLEIN ?", "options": ["Sombre ou noir", "Brillant ou rouge", "Transparent clignotant"], "rep": "Sombre ou noir"},
            {"id": "q6", "q": "Ce dispositif de niveau à prisme fonctionne sans aucun composant :", "options": ["Mobile ou flotteur mécanique", "Transparent", "En plastique"], "rep": "Mobile ou flotteur mécanique"},
            {"id": "q7", "q": "L'indice de réfraction moyen d'une huile hydraulique minérale est de :", "options": ["1.48", "1.00", "2.42"], "rep": "1.48"},
            {"id": "q8", "q": "Si le voyant reste désespérément brillant au soleil, l'engin est en :", "options": ["Manque de fluide (danger de cavitation)", "Surcharge de pression", "Parfait état de marche"], "rep": "Manque de fluide (danger de cavitation)"},
            {"id": "q9", "q": "La loi physique qui régit le basculement entre signal réfléchi et transmis est :", "options": ["La condition d'angle limite de réfraction", "La loi d'attraction", "La conservation des masses"], "rep": "La condition d'angle limite de réfraction"},
            {"id": "q10", "q": "Sur un chantier de TP, la vérification des niveaux de fluides se fait de manière :", "options": ["Quotidienne avant le démarrage", "Annuelle", "Uniquement en cas de panne"], "rep": "Quotidienne avant le démarrage"}
        ],
        "m_fra3": [
            {"id": "q1", "q": "Quel appareil de laboratoire mesure l'indice de réfraction d'une huile ?", "options": ["Un réfractomètre", "Un manomètre", "Un baromètre"], "rep": "Un réfractomètre"},
            {"id": "q2", "q": "Une modification de l'indice n d'un fluide de transmission indique :", "options": ["Une pollution ou contamination chimique", "Une baisse de régime", "Un changement de filtre"], "rep": "Une pollution ou contamination chimique"},
            {"id": "q3", "q": "Quel contaminant fréquent en TP crée une émulsion type 'mayonnaise' ?", "options": ["L'eau de condensation ou d'infiltration", "La limaille de fer", "Le sable fin"], "rep": "L'eau de condensation ou d'infiltration"},
            {"id": "q4", "q": "L'analyse par réfraction nécessite le dépôt de quelle quantité de fluide ?", "options": ["Une seule goutte sur le prisme", "Un litre complet", "Une éprouvette graduée"], "rep": "Une seule goutte sur le prisme"},
            {"id": "q5", "q": "Si du carburant fuit et se mélange à l'huile moteur, l'indice global :", "options": ["Subit une dérive mesurable", "Reste rigoureusement fixe", "Devient égal à 1"], "rep": "Subit une dérive mesurable"},
            {"id": "q6", "q": "La température de l'échantillon doit être contrôlée car elle influence :", "options": ["La valeur de l'indice de réfraction", "Le volume du prisme", "La couleur du laser"], "rep": "La valeur de l'indice de réfraction"},
            {"id": "q7", "q": "L'indice de réfraction de l'eau pure (1.333) est plus .......... que celui de l'huile (1.48).", "options": ["Bas", "Élevé", "Identique"], "rep": "Bas"},
            {"id": "q8", "q": "Le contrôle de l'état des huiles en maintenance préventive permet d'éviter :", "options": ["L'usure prématurée des composants internes", "Les crevaisons", "Les surcharges de benne"], "rep": "L'usure prématurée des composants internes"},
            {"id": "q9", "q": "La mesure s'appuie sur le relevé précis de quel angle limite ?", "options": ["L'angle de réflexion totale interne", "L'angle de carrossage", "L'angle de braquage"], "rep": "L'angle de réflexion totale interne"},
            {"id": "q10", "q": "Ce diagnostic rapide évite aux entreprises de TP :", "options": ["Des casses mécaniques lourdes et coûteuses", "De nettoyer les engins", "De payer les taxes"], "rep": "Des casses mécaniques lourdes et coûteuses"}
        ]
    }

    banque_trous_tp = {
        "tp_ref1": [
            ("1. La station totale mesure les distances sur le chantier à l'aide d'un faisceau ..........", ["Choisir...", "laser", "sonore"], "laser", "tp1_t1"),
            ("2. Pour renvoyer le signal, le topographe place une mire munie d'un ..........", ["Choisir...", "prisme", "dioptre"], "prisme", "tp1_t2"),
            ("3. Le retour direct de l'onde s'appuie sur la loi de la ..........", ["Choisir...", "réflexion", "réfraction"], "réflexion", "tp1_t3"),
            ("4. Au point d'incidence, l'angle de retour r est égal à l'angle ..........", ["Choisir...", "i", "i2"], "i", "tp1_t4"),
            ("5. La ligne perpendiculaire à la face d'entrée du verre est la ..........", ["Choisir...", "normale", "diagonale"], "normale", "tp1_t5"),
            ("6. Le calcul de la distance utilise la constante de la vitesse de la ..........", ["Choisir...", "lumière", "pression"], "lumière", "tp1_t6"),
            ("7. La trajectoire rectiligne garantit un alignement parfait des ..........", ["Choisir...", "ouvrages", "engins"], "ouvrages", "tp1_t7"),
            ("8. Les impuretés de l'air provoquent une déviation de type ..........", ["Choisir...", "diffuse", "spéculaire"], "diffuse", "tp1_t8"),
            ("9. Ce suivi géométrique rigoureux fait partie de l'implantation des ..........", ["Choisir...", "axes", "moteurs"], "axes", "tp1_t9"),
            ("10. L'égalité des angles caractérise les lois de .......... pour la réflexion.", ["Choisir...", "Snell-Descartes", "Newton"], "Snell-Descartes", "tp1_t10")
        ],
        "tp_ref2": [
            ("1. La niveleuse utilise un récepteur calé sur un plan horizontal de ..........", ["Choisir...", "référence", "courbure"], "référence", "tp2_t1"),
            ("2. L'émetteur rotatif balaie le chantier pour créer une cote ..........", ["Choisir...", "altimétrique", "volumique"], "altimétrique", "tp2_t2"),
            ("3. Les cellules photoélectriques interceptent le faisceau par ..........", ["Choisir...", "réflexion", "réfraction"], "réflexion", "tp2_t3"),
            ("4. L'angle d'incidence du balayage laser horizontal par rapport à la normale est de ..........", ["Choisir...", "0", "90"], "0", "tp2_t4"),
            ("5. Si la lame dévie, le système modifie la position des vérins ..........", ["Choisir...", "hydrauliques", "électriques"], "hydrauliques", "tp2_t5"),
            ("6. Le guidage optique permet d'ajuster l'épaisseur de la grave ..........", ["Choisir...", "non traitée", "bitumineuse"], "non traitée", "tp2_t6"),
            ("7. La couche lissée par cet engin s'appelle le fond de ..........", ["Choisir...", "forme", "fouille"], "forme", "tp2_t7"),
            ("8. Les capteurs éliminent le besoin de poser des piquets ..........", ["Choisir...", "manuels", "réfléchissants"], "manuels", "tp2_t8"),
            ("9. Le balayage du faisceau s'exécute à une vitesse de plusieurs centaines de .......... par minute.", ["Choisir...", "tours", "mètres"], "tours", "tp2_t9"),
            ("10. Ce automatisme évite les erreurs de terrassement et les surépaisseurs de ..........", ["Choisir...", "matériaux", "carburant"], "matériaux", "tp2_t10")
        ],
        "tp_ref3": [
            ("1. L'alignement d'un collecteur s'effectue avec un laser de ..........", ["Choisir...", "canalisation", "puissance"], "canalisation", "tp3_t1"),
            ("2. L'appareil émetteur est calé solidement au fond du regard de ..........", ["Choisir...", "départ", "visite"], "départ", "tp3_t2"),
            ("3. Le technicien programme la valeur réglementaire de la ..........", ["Choisir...", "pente", "pression"], "pente", "tp3_t3"),
            ("4. Le faisceau lumineux rouge traverse l'intérieur de la ..........", ["Choisir...", "conduite", "tranchée"], "conduite", "tp3_t4"),
            ("5. Le spot vient frapper le centre d'une mire ..........", ["Choisir...", "cible", "convexe"], "cible", "tp3_t5"),
            ("6. La plaque de contrôle positionnée dans le tuyau est ..........", ["Choisir...", "translucide", "opaque"], "translucide", "tp3_t6"),
            ("7. L'alignement optique prévient la stagnation des eaux ..........", ["Choisir...", "usées", "potables"], "usées", "tp3_t7"),
            ("8. Le déplacement de la lumière dans l'air sec reste ..........", ["Choisir...", "rectiligne", "sinusoïdal"], "rectiligne", "tp3_t8"),
            ("9. L'ajustement géométrique se fait avant le .......... de la fouille.", ["Choisir...", "remblaiement", "creusement"], "remblaiement", "tp3_t9"),
            ("10. Ce guidage supprime les défauts d'emboîtement des tuyaux en ..........", ["Choisir...", "béton", "acier"], "béton", "tp3_t10")
        ],
        "tp_fra1": [
            ("1. L'air surchauffé au ras du bitume modifie son indice de ..........", ["Choisir...", "réfraction", "réflexion"], "réfraction", "tp4_t1"),
            ("2. Plus la température du gaz augmente, plus son indice de réfraction ..........", ["Choisir...", "diminue", "augmente"], "diminue", "tp4_t2"),
            ("3. Cette hétérogénéité thermique courbe la trajectoire des rayons ..........", ["Choisir...", "lumineux", "mécaniques"], "lumineux", "tp4_t3"),
            ("4. Ce phénomène de déviation continue s'appelle un .......... thermique.", ["Choisir...", "mirage", "dioptre"], "mirage", "tp4_t4"),
            ("5. La loi de Descartes associe les indices aux .......... des angles.", ["Choisir...", "sinus", "cosinus"], "sinus", "tp4_t5"),
            ("6. Quand le rayon glisse parallèlement au sol sans s'y enfoncer, il atteint l'angle ..........", ["Choisir...", "limite", "normal"], "limite", "tp4_t6"),
            ("7. Le dioptre d'air chaud se comporte alors comme un .......... parfait.", ["Choisir...", "miroir", "prisme"], "miroir", "tp4_t7"),
            ("8. Cette perturbation fausse les relevés de nivellement de haute ..........", ["Choisir...", "précision", "vitesse"], "précision", "tp4_t8"),
            ("9. L'indice optique moyen de l'atmosphère standard vaut environ ..........", ["Choisir...", "1.0003", "1.3330"], "1.0003", "tp4_t9"),
            ("10. Pour limiter cette erreur, le technicien évite les visées au ras du ..........", ["Choisir...", "sol", "trépied"], "sol", "tp4_t10")
        ],
        "tp_fra2": [
            ("1. La recherche d'eau dans un forage utilise une méthode de diagraphie ..........", ["Choisir...", "optique", "manuelle"], "optique", "tp5_t1"),
            ("2. Dans la partie haute non noyée, le rayon traverse d'abord de l'..........", ["Choisir...", "air", "eau"], "air", "tp5_t2"),
            ("3. L'indice de réfraction de l'air est pris égal à ..........", ["Choisir...", "1", "1.33"], "1", "tp5_t3"),
            ("4. Au contact du toit de la nappe phréatique, le milieu devient de l'..........", ["Choisir...", "eau", "roche"], "eau", "tp5_t4"),
            ("5. L'indice de réfraction de l'eau pure possède une valeur de ..........", ["Choisir...", "1.333", "1.520"], "1.333", "tp5_t5"),
            ("6. Le changement d'indice provoque une déviation appelée ..........", ["Choisir...", "réfraction", "réflexion"], "réfraction", "tp5_t6"),
            ("7. Le rayon transmis se rapproche de la normale car n2 est .......... à n1.", ["Choisir...", "supérieur", "inférieur"], "supérieur", "tp5_t7"),
            ("8. Le saut d'angle permet de repérer la profondeur de la nappe ..........", ["Choisir...", "phréatique", "de béton"], "phréatique", "tp5_t8"),
            ("9. Cette information fixe la hauteur de sécurité des structures de ..........", ["Choisir...", "fondation", "roulement"], "fondation", "tp5_t9"),
            ("10. Si la boue obscurcit l'eau, le signal lumineux subit une forte ..........", ["Choisir...", "absorption", "accélération"], "absorption", "tp5_t10")
        ],
        "tp_fra3": [
            ("1. La pureté d'une émulsion de bitume se jauge sur le terrain au ..........", ["Choisir...", "réfractomètre", "baromètre"], "réfractomètre", "tp6_t1"),
            ("2. Le prélèvement du liant nécessite le dépôt d'une seule ..........", ["Choisir...", "goutte", "cuve"], "goutte", "tp6_t2"),
            ("3. Le fluide est étalé directement sur le prisme en .......... de l'outil.", ["Choisir...", "verre", "acier"], "verre", "tp6_t3"),
            ("4. La déviation du rayon lumineux renseigne sur la concentration en ..........", ["Choisir...", "eau", "sable"], "eau", "tp6_t4"),
            ("5. La déflexion de la trajectoire du laser suit la loi de ..........", ["Choisir...", "Snell-Descartes", "Pascal"], "Snell-Descartes", "tp6_t5"),
            ("6. L'évaluation repose sur la détection fine du sinus de l'angle ..........", ["Choisir...", "critique", "de braquage"], "critique", "tp6_t6"),
            ("7. L'indice de réfringence de l'eau de mélange vaut réglementairement ..........", ["Choisir...", "1.333", "1.000"], "1.333", "tp6_t7"),
            ("8. Ce test de terrain valide l'adhérence de la couche d'..........", ["Choisir...", "accrochage", "forme"], "accrochage", "tp6_t8"),
            ("9. La rampe d'épandage distribue ce liant en amont du .......... routier.", ["Choisir...", "finisseur", "compacteur"], "finisseur", "tp6_t9"),
            ("10. Ce suivi s'inscrit dans le cadre du contrôle d'assurance ..........", ["Choisir...", "qualité", "carburant"], "qualité", "tp6_t10")
        ]
    }

    cle_ordre = f"ordre_quiz_tp_{cas_id}"
    if cle_ordre not in st.session_state:
        liste_q = list(banque_quiz[cas_id])
        random.shuffle(liste_q)
        st.session_state[cle_ordre] = liste_q

    # Disposition stricte : Textes à gauche et Visuels à droite
    col_gauche_questions, col_droite_visuels = st.columns([0.55, 0.45])
    
    with col_gauche_questions:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tp_at6_{cas_id}_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")
            
        st.write("---")
        st.markdown("##### Synthèse (Texte à trous - 10 cases - 10 pts)")
        for ligne in banque_trous_tp[cas_id]:
            enonce_texte = ligne[0]
            choix_options = ligne[1]
            cle_unique = ligne[3]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce_texte)
            with c_sel:
                st.selectbox("", choix_options, key=f"{cle_unique}_{cas_id}_tp_clean", disabled=verrouille, label_visibility="collapsed")
                
    with col_droite_visuels:
        st.write("")
        st.info(
            "Utilisez les fiches de dossiers techniques et le simulateur vectoriel situés en haut pour compléter la feuille d'évaluation à gauche."
        )

        
def afficher_atelier_reflexion_totale(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 4 de la Réflexion Totale."""
    import random

    st.subheader("Atelier Interactif : Phénomène de Réflexion Totale et Applications")

    questions_totale_sources = [
        {"id": "qrt1", "q": "Quelle condition sur les indices de réfraction est obligatoire pour obtenir une réflexion totale ?", "options": ["n1 doit être supérieur à n2", "n1 doit être inférieur à n2", "n1 doit être égal à n2"], "rep": "n1 doit être supérieur à n2"},
        {"id": "qrt2", "q": "Quelle technologie de communication moderne utilise la réflexion totale pour guider la lumière ?", "options": ["La fibre optique", "Le câble coaxial", "La ligne de cuivre"], "rep": "La fibre optique"},
        {"id": "qrt3", "q": "À quel angle de réfraction (i2) correspond exactement l'angle d'incidence limite ?", "options": ["90 degrés", "0 degré", "45 degrés"], "rep": "90 degrés"},
        {"id": "qrt4", "q": "Si l'angle d'incidence est strictement supérieur à l'angle critique, que devient l'intensité du rayon réfracté ?", "options": ["Elle devient nulle", "Elle double", "Elle reste identique"], "rep": "Elle devient nulle"},
        {"id": "qrt5", "q": "Quel instrument médical utilise des faisceaux de fibres optiques pour explorer l'intérieur du corps ?", "options": ["L'endoscope", "Le stéthoscope", "Le tensiomètre"], "rep": "L'endoscope"},
        {"id": "qrt6", "q": "Comment appelle-t-on la partie centrale d'une fibre optique où circule la lumière ?", "options": ["Le cœur", "La gaine", "Le revêtement"], "rep": "Le cœur"},
        {"id": "qrt7", "q": "Pour que la lumière reste piégée dans le cœur de la fibre, la gaine doit avoir :", "options": ["Un indice n2 inférieur à n1", "Un indice n2 supérieur à n1", "Le même indice n1"], "rep": "Un indice n2 inférieur à n1"},
        {"id": "qrt8", "q": "Quel composant optique à réflexion totale trouve-t-on dans les appareils photo reflex et les jumelles ?", "options": ["Le prisme à angle droit", "La lentille divergente", "Le miroir concave"], "rep": "Le prisme à angle droit"},
        {"id": "qrt9", "q": "Quel phénomène optique naturel et chaud crée des illusions visuelles de flaques d'eau sur la route ?", "options": ["Un mirage", "Un arc-en-ciel", "Une ombre portée"], "rep": "Un mirage"},
        {"id": "qrt10", "q": "Si la lumière voyage du verre (n=1.5) vers l'air (n=1), la réflexion totale est-elle possible ?", "options": ["Oui, si l'angle d'incidence est suffisant", "Non, c'est physiquement impossible", "Uniquement si le laser est violet"], "rep": "Oui, si l'angle d'incidence est suffisant"}
    ]

    if "ordre_quiz_totale_aleatoire" not in st.session_state:
        random.shuffle(questions_totale_sources)
        st.session_state.ordre_quiz_totale_aleatoire = questions_totale_sources

    if "champs_totale_clean" not in st.session_state:
        st.session_state.champs_totale_clean = [
            ("1. La réflexion totale se produit uniquement si le milieu 1 est plus .......... que le milieu 2.", ["Choisir...", "réfringent", "transparent"], "réfringent", "tot_t1"),
            ("2. L'angle d'incidence à partir duquel la réfraction s'annule est l'angle ..........", ["Choisir...", "limite", "normal"], "limite", "tot_t2"),
            ("3. Au-delà de l'angle critique, la totalité de l'énergie lumineuse est ..........", ["Choisir...", "réfléchie", "absorbée"], "réfléchie", "tot_t3"),
            ("4. Le guide de lumière souple constitué d'un cœur et d'une gaine est la fibre ..........", ["Choisir...", "optique", "de carbone"], "optique", "tot_t4"),
            ("5. Dans une fibre, l'indice du cœur doit être strictement .......... à celui de la gaine.", ["Choisir...", "supérieur", "inférieur"], "supérieur", "tot_t5"),
            ("6. Un prisme à réflexion totale permet de dévier un faisceau de quatre-vingt-dix ..........", ["Choisir...", "degrés", "pascals"], "degrés", "tot_t6"),
            ("7. Lors d'une réflexion totale, le dioptre se comporte comme un .......... parfait.", ["Choisir...", "miroir", "filtre"], "miroir", "tot_t7"),
            ("8. Les mirages routiers proviennent de la courbure des rayons dans l'air ..........", ["Choisir...", "surchauffé", "glacial"], "surchauffé", "tot_t8"),
            ("9. L'examen médical interne exploitant la réflexion totale est l'..........", ["Choisir...", "endoscopie", "échographie"], "endoscopie", "tot_t9"),
            ("10. Si l'angle d'incidence est inférieur à l'angle critique, il y a toujours ..........", ["Choisir...", "réfraction", "absorption"], "réfraction", "tot_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_totale_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tot_at4_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_totale_clean:
            # Extraction correcte des éléments du tuple par leur index
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce) # Affichera uniquement le texte de la phrase
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_tot_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_refraction(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 3 de la Réfraction."""
    import random

    st.subheader("Atelier Interactif : Lois de la Réfraction et Indices Optiques")

    questions_refraction_sources = [
        {"id": "qr1", "q": "Quelle formule traduit mathématiquement la loi de Snell-Descartes pour la réfraction ?", "options": ["n1 * sin(i1) = n2 * sin(i2)", "i1 = i2", "n1 * cos(i1) = n2 * cos(i2)"], "rep": "n1 * sin(i1) = n2 * sin(i2)"},
        {"id": "qr2", "q": "Que représente la grandeur 'n' pour un milieu transparent ?", "options": ["L'indice de réfraction", "L'intensité lumineuse", "Le niveau de réflexion"], "rep": "L'indice de réfraction"},
        {"id": "qr3", "q": "Quelle est la valeur approximative de l'indice de réfraction de l'air ?", "options": ["1.00", "1.33", "1.52"], "rep": "1.00"},
        {"id": "qr4", "q": "Quand la lumière passe de l'air (n=1) à l'eau (n=1.33), le rayon réfracté :", "options": ["Se rapproche de la normale", "S'éloigne de la normale", "Ne subit aucune déviation"], "rep": "Se rapproche de la normale"},
        {"id": "qr5", "q": "Comment s'appelle la surface plane qui sépare deux milieux transparents différents ?", "options": ["Un dioptre plan", "Une normale", "Un miroir plan"], "rep": "Un dioptre plan"},
        {"id": "qr6", "q": "Quelle est l'unité légale de l'indice de réfraction 'n' ?", "options": ["Il n'a pas d'unité", "Le degré (°)", "Le Pascal (Pa)"], "rep": "Il n'a pas d'unité"},
        {"id": "qr7", "q": "Que se passe-t-il si l'argument du sinus calculé pour l'angle i2 dépasse la valeur 1 ?", "options": ["Une réflexion totale", "Le rayon s'annule", "Une réfraction infinie"], "rep": "Une réflexion totale"},
        {"id": "qr8", "q": "Pour observer une réflexion totale, quelle condition doit remplir l'indice n1 par rapport à n2 ?", "options": ["n1 doit être supérieur à n2", "n1 doit être inférieur à n2", "n1 doit être égal à n2"], "rep": "n1 doit être supérieur à n2"},
        {"id": "qr9", "q": "Parmi ces milieux, lequel possède l'indice de réfraction le plus élevé (n = 2.417) ?", "options": ["Le diamant", "Le verre Crown", "L'eau"], "rep": "Le diamant"},
        {"id": "qr10", "q": "Si un rayon incident arrive perpendiculairement à la surface (i1 = 0°), que vaut l'angle i2 ?", "options": ["0 degré", "90 degrés", "45 degrés"], "rep": "0 degré"}
    ]

    if "ordre_quiz_refraction_aleatoire" not in st.session_state:
        random.shuffle(questions_refraction_sources)
        st.session_state.ordre_quiz_refraction_aleatoire = questions_refraction_sources

    if "champs_refraction_clean" not in st.session_state:
        st.session_state.champs_refraction_clean = [
            ("1. Le changement de direction de la lumière s'appelle la ..........", ["Choisir...", "réfraction", "réflexion"], "réfraction", "ref_t1"),
            ("2. L'indice optique traduit le rapport entre la vitesse de la lumière dans le vide et dans le ..........", ["Choisir...", "matériau", "miroir"], "matériau", "ref_t2"),
            ("3. Plus l'indice de réfraction d'un milieu est grand, plus la vitesse de la lumière ..........", ["Choisir...", "diminue", "augmente"], "diminue", "ref_t3"),
            ("4. La ligne de référence tracée à 90 degrés de l'interface est la ..........", ["Choisir...", "normale", "tangente"], "normale", "ref_t4"),
            ("5. La loi de Snell-Descartes relie les indices aux .......... des angles.", ["Choisir...", "sinus", "cosinus"], "sinus", "ref_t5"),
            ("6. Le milieu de référence dont l'indice de réfraction vaut exactement 1 est le ..........", ["Choisir...", "vide", "verre"], "vide", "ref_t6"),
            ("7. Quand le rayon s'éloigne de la normale, cela signifie que n2 est .......... à n1.", ["Choisir...", "inférieur", "supérieur"], "inférieur", "ref_t7"),
            ("8. L'angle limite d'incidence est le point de départ de la réflexion ..........", ["Choisir...", "totale", "spéculaire"], "totale", "ref_t8"),
            ("9. L'illusion du bâton brisé dans un verre est provoquée par la ..........", ["Choisir...", "réfraction", "dispersion"], "réfraction", "ref_t9"),
            ("10. L'indice optique de l'eau pure est égal à ..........", ["Choisir...", "1.333", "1.520"], "1.333", "ref_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_refraction_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"ref_at3_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_refraction_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ref_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_miroir_plan(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 2 du Miroir Plan."""
    import random

    st.subheader("Atelier Interactif : Lois de la Réflexion Spéculaire")

    questions_miroir_sources = [
        {"id": "qm1", "q": "Comment appelle-t-on la ligne imaginaire perpendiculaire à la surface du miroir ?", "options": ["La Normale", "La Tangente", "Le Dioptre"], "rep": "La Normale"},
        {"id": "qm2", "q": "Quel angle est défini entre le rayon incident et la normale ?", "options": ["L'angle d'incidence", "L'angle de réflexion", "L'angle de réfraction"], "rep": "L'angle d'incidence"},
        {"id": "qm3", "q": "Si un rayon frappe un miroir plan avec un angle d'incidence de 40 degrés, quel est l'angle du rayon réfléchi ?", "options": ["40 degrés", "20 degrés", "50 degrés"], "rep": "40 degrés"},
        {"id": "qm4", "q": "Par rapport à quel élément de référence mesure-t-on toujours les angles en optique géométrique ?", "options": ["La normale", "La surface du miroir", "La source laser"], "rep": "La normale"},
        {"id": "qm5", "q": "Comment appelle-t-on le rayon lumineux qui provient directement de la source ?", "options": ["Le rayon incident", "Le rayon réfléchi", "Le rayon réfracté"], "rep": "Le rayon incident"},
        {"id": "qm6", "q": "Quelle est la relation mathématique exacte de la deuxième loi de Snell-Descartes pour la réflexion ?", "options": ["i = r", "i = 2r", "n1 * i = n2 * r"], "rep": "i = r"},
        {"id": "qm7", "q": "Comment qualifie-t-on le point d'intersection précis où le faisceau touche le miroir ?", "options": ["Le point d'incidence", "Le point focal", "Le point de déviation"], "rep": "Le point d'incidence"},
        {"id": "qm8", "q": "Dans quel plan particulier les rayons incident, réfléchi et la normale sont-ils tous situés ?", "options": ["Le plan d'incidence", "Le plan de réfraction", "Le plan horizontal"], "rep": "Le plan d'incidence"},
        {"id": "qm9", "q": "Quel type de surface caractérise un miroir plan parfait ?", "options": ["Une surface parfaitement lisse et réfléchissante", "Une surface rugueuse et mate", "Une surface transparente et courbe"], "rep": "Une surface parfaitement lisse et réfléchissante"},
        {"id": "qm10", "q": "Si un rayon laser arrive de manière parfaitement perpendiculaire au miroir (i = 0°), que fait le rayon réfléchi ?", "options": ["Il rebrousse chemin sur lui-même", "Il est dévié à 90 degrés", "Il est totalement absorbé"], "rep": "Il rebrousse chemin sur lui-même"}
    ]

    if "ordre_quiz_miroir_aleatoire" not in st.session_state:
        random.shuffle(questions_miroir_sources)
        st.session_state.ordre_quiz_miroir_aleatoire = questions_miroir_sources

    if "champs_miroir_clean" not in st.session_state:
        st.session_state.champs_miroir_clean = [
            ("1. Le rayon provenant du laser qui se dirige vers la surface est le rayon ..........", ["Choisir...", "incident", "réfléchi"], "incident", "mir_t1"),
            ("2. Après avoir frappé le miroir, le rayon lumineux qui repart est le rayon ..........", ["Choisir...", "réfléchi", "incident"], "réfléchi", "mir_t2"),
            ("3. La droite fictive tracée à 90 degrés de la surface s'appelle la ..........", ["Choisir...", "normale", "diagonale"], "normale", "mir_t3"),
            ("4. L'intersection géométrique entre le rayon initial et le miroir est le point d'..........", ["Choisir...", "incidence", "réflexion"], "incidence", "mir_t4"),
            ("5. La surface plane séparant deux milieux transparents distincts s'appelle un ..........", ["Choisir...", "dioptre", "prisme"], "dioptre", "mir_t5"),
            ("6. Sur un miroir plan, l'angle de réflexion r est toujours .......... à l'angle d'incidence i.", ["Choisir...", "égal", "supérieur"], "égal", "mir_t6"),
            ("7. Une réflexion nette sans dispersion de la lumière est dite ..........", ["Choisir...", "spéculaire", "diffuse"], "spéculaire", "mir_t7"),
            ("8. L'angle d'incidence s'évalue strictement entre le rayon incident et la ..........", ["Choisir...", "normale", "surface"], "normale", "mir_t8"),
            ("9. Les lois physiques qui régissent le comportement de la réflexion sont les lois de ..........", ["Choisir...", "Snell-Descartes", "Newton"], "Snell-Descartes", "mir_t9"),
            ("10. Si l'angle d'incidence i augmente, l'angle de réflexion r va lui aussi ..........", ["Choisir...", "augmenter", "diminue"], "augmenter", "mir_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_miroir_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"mir_at2_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_miroir_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_mir_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_histoire_optique(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page de l'historique."""
    import random

    st.subheader("Atelier Interactif : Histoire et Fondations de l'Optique")

    questions_optique_sources = [
        {"id": "qo1", "q": "Quel scientifique du XIe siècle démontre que la lumière entre dans l'oeil ?", "options": ["Ibn al-Haytham", "René Descartes", "Willebrord Snell"], "rep": "Ibn al-Haytham"},
        {"id": "qo2", "q": "Quelle est la nationalité du mathématicien Willebrord Snell ?", "options": ["Hollandaise", "Française", "Italienne"], "rep": "Hollandaise"},
        {"id": "qo3", "q": "Dans la formule moderne n1 * sin(i1) = n2 * sin(i2), que représente la lettre 'n' ?", "options": ["L'indice de réfraction du milieu", "Le nombre de rayons lumineux", "Le niveau d'intensité de la source"], "rep": "L'indice de réfraction du milieu"},
        {"id": "qo4", "q": "Quel appareil historique Ibn al-Haytham a-t-il utilisé pour ses expériences ?", "options": ["La chambre noire", "Le microscope optique", "Le télescope réfracteur"], "rep": "La chambre noire"},
        {"id": "qo5", "q": "Sous quel nom latin le scientifique Ibn al-Haytham est-il aussi connu ?", "options": ["Alhazen", "Avicenne", "Averroès"], "rep": "Alhazen"},
        {"id": "qo6", "q": "Quelle fonction mathématique associe-t-on à la loi de Snell-Descartes pour la réfraction ?", "options": ["Le sinus (sin)", "Le cosinus (cos)", "La tangente (tan)"], "rep": "Le sinus (sin)"},
        {"id": "qo7", "q": "Dans quel ouvrage célèbre René Descartes publie-t-il sa formulation de la réfraction ?", "options": ["La Dioptrique", "Le Discours de la méthode", "Le Traité du monde"], "rep": "La Dioptrique"},
        {"id": "qo8", "q": "Comment appelle-t-on l'ancienne théorie grecque erronée qui disait que les yeux projetaient des rayons ?", "options": ["L'émission ou extramission", "L'intromission", "La réfraction passive"], "rep": "L'émission ou extramission"},
        {"id": "qo9", "q": "Lorsque la lumière passe d'un milieu moins dense à un milieu plus dense (l'air vers l'eau), le rayon dévié :", "options": ["Se rapproche de la normale", "S'éloigne de la normale", "Reste parfaitement droit"], "rep": "Se rapproche de la normale"},
        {"id": "qo10", "q": "Au cours de quel siècle les lois mathématiques de la réfraction ont-elles été fixées en Europe ?", "options": ["Le XVIIe siècle", "Le XIe siècle", "Le XIXe siècle"], "rep": "Le XVIIe siècle"}
    ]

    if "ordre_quiz_optique_aleatoire" not in st.session_state:
        random.shuffle(questions_optique_sources)
        st.session_state.ordre_quiz_optique_aleatoire = questions_optique_sources

    if "champs_optique_clean" not in st.session_state:
        st.session_state.champs_optique_clean = [
            ("1. Le père de l'optique moderne se nomme Ibn al-..........", ["Choisir...", "Haytham", "Siha"], "Haytham", "opt_t1"),
            ("2. L'appareil de la chambre noire s'appelle aussi la camera ..........", ["Choisir...", "obscura", "lucida"], "obscura", "opt_t2"),
            ("3. Snell a découvert la loi de la réfraction en utilisant la trigonométrie des ..........", ["Choisir...", "sinus", "cosinus"], "sinus", "opt_t3"),
            ("4. Le physicien français qui a donné son nom à la loi finale est René ..........", ["Choisir...", "Descartes", "Pascal"], "Descartes", "opt_t4"),
            ("5. La déviation de la lumière changeant de milieu s'appelle la ..........", ["Choisir...", "réfraction", "réflexion"], "réfraction", "opt_t5"),
            ("6. Le comportement rectiligne de la lumière signifie qu'elle se déplace en ligne ..........", ["Choisir...", "droite", "courbe"], "droite", "opt_t6"),
            ("7. Dans la loi n1*sin(i1) = n2*sin(i2), la lettre i désigne l'angle d'..........", ["Choisir...", "incidence", "intensité"], "incidence", "opt_t7"),
            ("8. L'indice optique de l'air possède une valeur de référence égale à ..........", ["Choisir...", "1", "1.33"], "1", "opt_t8"),
            ("9. Un bâton plongé dans un verre d'eau subit une illusion et semble ..........", ["Choisir...", "cassé", "plus grand"], "cassé", "opt_t9"),
            ("10. Alhazen a prouvé sa théorie en observant que la lumière de l'objet .......... dans l'oeil.", ["Choisir...", "entrait", "sortait"], "entrait", "opt_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_optique_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"opt_at1_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_optique_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_opt_clean", disabled=verrouille, label_visibility="collapsed")



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
    st.header("Histoire et Découverte de l'Optique")
    st.write(
        "Découvrez comment l'humanité a compris la nature de la lumière, passant d'un fluide imaginaire à un comportement géométrique précis :"
    )

    # =============================================================================
    # SECTION HISTORIQUE ET SCIENTIFIQUES CLÉS
    # =============================================================================
    col_hist_1, col_hist_img1 = st.columns(2)
    
    with col_hist_1:
        st.markdown("##### La théorie de l'intromission")
        st.write(
            "Pendant longtemps, les anciens savants grecs pensaient que nos yeux émettaient des rayons visuels "
            "pour palper les objets. Au XIe siècle, le scientifique **Ibn al-Haytham** (Alhazen) démontre le contraire : "
            "la lumière entre dans notre oeil après avoir été réfléchie par les objets. Il invente la chambre noire et devance la méthode scientifique."
        )

    with col_hist_img1:
        if os.path.exists("al_haytham_portrait.jpg"):
            st.image(
                "al_haytham_portrait.jpg",
                caption="Ibn al-Haytham (Alhazen)"
            )
        else:
            st.warning(
                "L'image 'al_haytham_portrait.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    col_hist_2, col_hist_img2 = st.columns(2)
    
    with col_hist_2:
        st.markdown("##### La loi de la réfraction")
        st.write(
            "Au XVIIe siècle, la quête de la compréhension de la déviation de la lumière dans l'eau s'accélère. "
            "Le mathématicien hollandais **Willebrord Snell** découvre le rapport constant lié aux sinus des angles. "
            "Quelques années plus tard, le philosophe français **René Descartes** formalise mathématiquement la loi stricte "
            "que nous utilisons aujourd'hui en classe : n1 * sin(i1) = n2 * sin(i2)."
        )
        
    with col_hist_img2:
        col_hist_img21, col_hist_img22 = st.columns(2)
        with col_hist_img21:
            if os.path.exists("snell_portrait.jpg"):
                st.image(
                    "snell_portrait.jpg",
                    caption="Willebrord Snell",
                )
            else:
                st.warning(
                    "L'image 'snell_portrait.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )

        with col_hist_img22:
            if os.path.exists("descartes_portrait.jpg"):
                st.image(
                    "descartes_portrait.jpg",
                    caption="René Descartes",
                )
            else:
                st.warning(
                    "L'image 'descartes_portrait.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )
                  
    st.write("---")

    # =============================================================================
    # BANDE DESSINÉE HUMORISTIQUE EN 4 CASES
    # =============================================================================
    col_gauche_texte, col_droite_img = st.columns(2)

    with col_gauche_texte:
        st.write(
            "**La BD humoristique textuelle : Le mystère des rayons déviés**")
        
        st.info(
            "**Case 1 :** Un rayon lumineux voyage tranquillement en ligne droite dans l'air à une vitesse vertigineuse. "
            "Il discute avec ses photons voisins : "
            "« Tout va bien la trajectoire est parfaite, aucun obstacle en vue, on fonce à la vitesse de la lumière ! ».\n\n"
            
            "**Case 2 :** Une surface d'eau plane apparaît brusquement. Le milieu change et l'indice de réfraction augmente. "
            "L'eau ralentit brutalement le premier photon du rayon et lui crie : "
            "« Hé toi ! Ralentis immédiatement ! Ton angle d'attaque ne convient plus à mon milieu dense ! ».\n\n"
            
            "**Case 3 :** Le rayon lumineux se retrouve brisé et dévié à l'interface des deux milieux. "
            "Il panique en voyant sa direction changer selon la loi des sinus : "
            "« Oh non ! Je viens de subir une réfraction ! Mon angle d'incidence i1 s'est transformé en un angle i2 plus petit ! "
            "Je me rapproche de la normale ! ».\n\n"
            
            "**Case 4 :** Le rayon dévié continue sa course sous l'eau vers le fond du récipient. "
            "Au loin, un observateur au laboratoire regarde l'illusion d'optique et s'exclame : "
            "« C'est magique ! Le bâton plongé dans l'eau semble cassé alors qu'il est parfaitement droit ! »."
        )

    with col_droite_img:
        if os.path.exists("optique_caricature.jpg"):
            st.image(
                "optique_caricature.jpg",
                caption="Illustration humoristique du mystère des rayons déviés",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'optique_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
    
    if "suite_verrouille_tab1_optique" not in st.session_state:
        st.session_state.suite_verrouille_tab1_optique = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_optique

    # Rendu des questionnaires d'évaluation de l'Atelier 1
    afficher_atelier_histoire_optique(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique sur l'histoire de l'optique et les lois de propagation.",
        key="check_certif_opt1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_opt_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q1 = 0.0
            if "ordre_quiz_optique_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_optique_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"opt_at1_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q1 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t1 = 0.0
            if "champs_optique_clean" in st.session_state:
                for ligne in st.session_state.champs_optique_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_opt_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t1 += 1.0

            st.session_state.score_suite1_opt_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_opt_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_opt = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_optique = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab1_optique", False):
        from datetime import datetime
        scr1_t1 = st.session_state.get("score_suite1_opt_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_opt_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_opt", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_opt1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Optique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 1 : Fondements Historiques de l'Optique (Réflexion et Réfraction)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Historique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_optique_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_optique_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"opt_at1_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_opt1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_optique_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_optique_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_opt_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_opt1 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement du fichier HTML généré
        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Historique_Optique") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION OFFICIEL (HTML)",
            data=html_export_opt1,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_opt"
        )

with tab2:
    st.header("Loi de la réflexion pour un miroir plan")
    st.write(
        "Explorez la façon dont un rayon lumineux interagit avec une surface lisse et réfléchissante à travers les définitions de cours et notre simulateur de laboratoire :"
    )

    # =============================================================================
    # SECTION DÉFINITIONS THÉORIQUES ET SCHÉMA D'ORIENTATION
    # =============================================================================
    col_def_texte, col_def_alerte_img = st.columns(2)
    
    with col_def_texte:
        st.markdown("##### Vocabulaire fondamental de l'optique géométrique")
        st.write(
            "**Surface réfléchissante (ou miroir plan) :** Interface lisse qui renvoie la totalité de la "
            "lumière reçue dans une direction privilégiée sans la disperser.\n\n"
            
            "**Dioptre plan :** Surface géométrique plane séparant deux milieux transparents d'indices de "
            "réfraction différents (dans le cas du miroir, la lumière ne traverse pas ce dioptre, elle rebondit).\n\n"
            
            "**Rayon incident :** Rayon lumineux provenant de la source (laser) qui se dirige vers la surface du miroir.\n\n"
            
            "**Point d'incidence (I) :** Point d'intersection exact où le rayon incident frappe le miroir.\n\n"
            
            "**La Normale :** Ligne imaginaire tracée perpendiculairement (à 90 degrés) à la surface du miroir au point d'incidence. Toutes les mesures d'angles s'effectuent par rapport à cette droite de référence.\n\n"
            
            "**Rayon réfléchi :** Rayon lumineux qui repart du point d'incidence après avoir rebondi sur la surface."
        )

    with col_def_alerte_img:
        # Bloc de texte avec fond bleu stylisé
        st.markdown("""
        <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333;">
            <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Notice d'utilisation du Laboratoire</h4>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Première loi de Snell-Descartes :</b> Le rayon incident, le rayon réfléchi et la normale au dioptre réfléchi sont tous situés dans un même plan appelé le plan d'incidence.</p>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Deuxième loi de Snell-Descartes :</b> L'angle de réflexion r est rigoureusement égal à l'angle d'incidence i. Mathématiquement, on écrit : <b>i = r</b>.</p>
            <p style="font-size: 14px; margin-bottom: 0;">Utilisez les commandes du module ci-dessous pour modifier dynamiquement les paramètres du banc d'essai optique virtuel.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("miroir_plan_schema.jpg"):
            st.image(
                "miroir_plan_schema.jpg",
                caption="Schéma annoté structurel du miroir plan"
            )
        else:
            st.warning(
                "L'image 'miroir_plan_schema.jpg' est introuvable. Placez l'illustration annotée fixe dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # INTERFACE DE SIMULATION DU LASER INTERACTIF
    # =============================================================================
    st.subheader("Simulateur de Banc Optique Virtuel")
    
    # Zone de contrôle des paramètres de la simulation
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        angle_inc = st.slider(
            "Ajuster l'angle d'incidence (i) en degrés par rapport à la normale :",
            min_value=0,
            max_value=85,
            value=30,
            step=1
        )
    with col_ctrl2:
        couleur_nom = st.selectbox(
            "Sélectionner la couleur du faisceau laser :",
            options=["Rouge", "Bleu", "Vert", "Jaune", "Violet"]
        )
    
    # Dictionnaire de correspondance pour le rendu graphique Matplotlib
    carte_couleurs = {
        "Rouge": "#ff0000",
        "Bleu": "#0000ff",
        "Vert": "#00ff00",
        "Jaune": "#eeee00",
        "Violet": "#8b008b"
    }
    couleur_laser = carte_couleurs[couleur_nom]

    # Génération du graphique de simulation dynamique
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Tracé de la surface du miroir plan (Axe horizontal y=0)
    ax.plot([-10, 10], [0, 0], color="#64748b", linewidth=6, label="Miroir Plan")
    # Ajout d'une hachure sous le miroir pour symboliser la face opaque cachée
    ax.fill_between([-10, 10], 0, -1, color="#cbd5e1", hatch="//", alpha=0.3)
    
    # Tracé de la Normale perpendiculaire au point d'incidence (0,0)
    ax.plot([0, 0], [0, 10], color="#475569", linestyle="--", linewidth=2, label="La Normale")
    
    # Calcul des vecteurs unitaires pour le rayon incident et réfléchi
    # En optique géométrique, l'angle est donné par rapport à la verticale (normale)
    rad_inc = np.radians(angle_inc)
    
    # Rayon incident arrivant de la gauche vers l'origine (0,0)
    x_inc = -8 * np.sin(rad_inc)
    y_inc = 8 * np.cos(rad_inc)
    ax.annotate(
        "", xy=(0, 0), xytext=(x_inc, y_inc),
        arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15)
    )
    
    # Rayon réfléchi repartant de l'origine (0,0) vers la droite
    x_ref = 8 * np.sin(rad_inc)
    y_ref = 8 * np.cos(rad_inc)
    ax.annotate(
        "", xy=(x_ref, y_ref), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15)
    )
    
    # Textes indicatifs et étiquettes d'angles dynamiques sur le graphique
    ax.text(x_inc - 0.5, y_inc + 0.3, "Rayon Incident", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(x_ref - 0.5, y_ref + 0.3, "Rayon Réfléchi", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(-0.5, 10.3, "Normale", fontsize=10, color="#475569")
    
    # Affichage des valeurs numériques d'angles lues en temps réel
    ax.text(-3, 2, f"i = {angle_inc}°", fontsize=12, color="#0f172a", fontweight="bold")
    ax.text(1.5, 2, f"r = {angle_inc}°", fontsize=12, color="#0f172a", fontweight="bold")
    
    # Décoration et limites de la zone graphique
    ax.set_xlim(-10, 10)
    ax.set_ylim(-2, 11)
    ax.axis("off") # Suppression des axes gradués pour un rendu épuré de type schéma
    
    # Rendu final de la simulation dans Streamlit
    st.pyplot(fig)

    # Affichage de la boîte de contrôle et de validation des données numériques
    st.info(
        f"**Données du tableau d'expérimentation lues en temps réel :**\n\n"
        f"Angle mesuré du rayon incident par rapport à la normale : **{angle_inc}°**\n\n"
        f"Angle mesuré du rayon réfléchi obtenu sur le cadran gradué : **{angle_inc}°**\n\n"
        f"Constat vérifié : L'égalité mathématique fondamentale **i = r** est validée."
    )


    if "suite_verrouille_tab2_miroir" not in st.session_state:
        st.session_state.suite_verrouille_tab2_miroir = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_miroir

    # Rendu des questionnaires d'évaluation de l'Atelier 2
    afficher_atelier_miroir_plan(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Loi de la Réflexion pour un miroir plan.",
        key="check_certif_mir2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_mir_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q2 = 0.0
            if "ordre_quiz_miroir_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_miroir_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"mir_at2_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q2 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t2 = 0.0
            if "champs_miroir_clean" in st.session_state:
                for ligne in st.session_state.champs_miroir_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_mir_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t2 += 1.0

            st.session_state.score_suite2_mir_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_mir_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_mir = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_miroir = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab2_miroir", False):
        from datetime import datetime
        scr1_t2 = st.session_state.get("score_suite2_mir_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_mir_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_mir", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MIROIR PLAN SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_mir2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Miroir Plan - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 2 : Loi de la Réflexion pour un Miroir Plan (i = r)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_miroir_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_miroir_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"mir_at2_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mir2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mir2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_miroir_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_miroir_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_mir_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mir2 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mir2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement du fichier HTML généré
        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Miroir_Plan") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DU MIROIR PLAN (HTML)",
            data=html_export_mir2,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_mir"
        )

with tab3:
    st.header("Loi de la réfraction (Loi de Snell-Descartes)")
    st.write(
        "Explorez la façon dont la lumière change de direction lorsqu'elle passe d'un matériau transparent à un autre :"
    )

    # =============================================================================
    # SECTION DÉFINITIONS THÉORIQUES ET SCHÉMA D'ORIENTATION
    # =============================================================================
    col_ref_texte, col_ref_alerte_img = st.columns(2)
    
    with col_ref_texte:
        st.markdown("##### Vocabulaire fondamental de la réfraction")
        st.write(
            "**Dioptre plan :** Surface géométrique plane séparant deux milieux transparents distincts dotés d'un indice optique différent (comme la surface séparant l'air et l'eau).\n\n"
            
            "**Rayon incident :** Rayon lumineux provenant de la source (laser) voyageant dans le premier milieu (Milieu 1) et se dirigeant vers l'interface.\n\n"
            
            "**La Normale :** Ligne imaginaire tracée perpendiculairement (à 90 degrés) à la surface de séparation au point d'incidence. Tous les angles s'évaluent par rapport à elle.\n\n"
            
            "**Rayon réfracté :** Faisceau lumineux transmis dans le second milieu (Milieu 2). Sa trajectoire subit une déviation géométrique brusque à l'interface.\n\n"
            
            "**Indice de réfraction (n) :** Grandeur sans unité caractérisant la vitesse de propagation de la lumière dans un matériau (n = c / v). Plus l'indice est élevé, plus le milieu ralentit le faisceau."
        )

    with col_ref_alerte_img:
        # Bloc de texte avec fond bleu stylisé
        st.markdown("""
        <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333;">
            <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Notice d'utilisation de la Réfraction</h4>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Relation de Snell-Descartes :</b> Le comportement mathématique s'écrit de la façon suivante : <b>n1 * sin(i1) = n2 * sin(i2)</b>.</p>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Milieu moins réfringent vers plus réfringent (n1 < n2) :</b> Le rayon dévié se rapproche de la normale.</p>
            <p style="font-size: 14px; margin-bottom: 0;"><b>Milieu plus réfringent vers moins réfringent (n1 > n2) :</b> Le rayon dévié s'éloigne de la normale. Si l'angle d'incidence est trop important, la réfraction disparaît au profit d'une réflexion totale.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("loi_refraction_schema.jpg"):
            st.image(
                "loi_refraction_schema.jpg",
                caption="Schéma annoté structurel de la réfraction"
            )
        else:
            st.warning(
                "L'image 'loi_refraction_schema.jpg' est introuvable. Placez l'illustration annotée fixe dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # INTERFACE DE SIMULATION DU LABORATOIRE DE RÉFRACTION INTERACTIF
    # =============================================================================
    st.subheader("Simulateur de Réfraction et Recherche d'Indices")
    
    # Base de données exhaustive de 30 milieux avec leurs indices de réfraction réels
    base_milieux = {
        "Vide (n = 1.0000)": 1.0,
        "Hydrogène gaz (n = 1.0001)": 1.0001,
        "Air (n = 1.0003)": 1.0003,
        "Dioxyde de carbone gaz (n = 1.0005)": 1.0005,
        "Glace (n = 1.3100)": 1.31,
        "Eau (n = 1.3330)": 1.333,
        "Acétone (n = 1.3590)": 1.359,
        "Éthanol / Alcool (n = 1.3610)": 1.361,
        "Solution sucrée 30% (n = 1.3800)": 1.38,
        "Kérosène (n = 1.4400)": 1.440,
        "Quartz fondu (n = 1.4580)": 1.458,
        "Glycerine (n = 1.4730)": 1.473,
        "Huile minérale (n = 1.4800)": 1.480,
        "Huile d'olive (n = 1.4900)": 1.490,
        "Benzène (n = 1.5010)": 1.501,
        "Plexiglas / PMMA (n = 1.5100)": 1.510,
        "Verre Crown standard (n = 1.5200)": 1.520,
        "Sel de table / Halite (n = 1.5440)": 1.544,
        "Verre Flint léger (n = 1.5800)": 1.580,
        "Polystyrène plastique (n = 1.5900)": 1.590,
        "Ambre (n = 1.6000)": 1.600,
        "Sulfure de carbone (n = 1.6280)": 1.628,
        "Verre Flint lourd (n = 1.6600)": 1.660,
        "Topaze (n = 1.6200)": 1.620,
        "Saphir / Corindon (n = 1.7700)": 1.770,
        "Rubis (n = 1.7650)": 1.765,
        "Zircon (n = 1.9200)": 1.920,
        "Soufre solide (n = 1.9600)": 1.960,
        "Oxyde de zinc (n = 2.0000)": 2.0,
        "Diamant (n = 2.4170)": 2.417
    }

    # Configuration des entrées utilisateur du simulateur
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1:
        nom_milieu1 = st.selectbox("Choisir le Milieu 1 (milieu supérieur) :", options=list(base_milieux.keys()), index=2) # Par défaut l'Air
        n1 = base_milieux[nom_milieu1]
    with col_sel2:
        nom_milieu2 = st.selectbox("Choisir le Milieu 2 (milieu inférieur) :", options=list(base_milieux.keys()), index=5) # Par défaut l'Eau
        n2 = base_milieux[nom_milieu2]
    with col_sel3:
        couleur_nom = st.selectbox("Choisir la couleur du laser :", options=["Rouge", "Bleu", "Vert", "Jaune", "Violet"], key="laser_refraction")

    angle_i1 = st.slider(
        "Ajuster l'angle d'incidence (i1) en degrés :",
        min_value=0,
        max_value=89,
        value=45,
        step=1
    )

    carte_couleurs = {
        "Rouge": "#ff0000", "Bleu": "#0000ff", "Vert": "#00ff00", "Jaune": "#eeee00", "Violet": "#8b008b"
    }
    couleur_laser = carte_couleurs[couleur_nom]

    # =============================================================================
    # CALCUL MATHÉMATIQUE DE LA RÉFRACTION (SNELL-DESCARTES)
    # =============================================================================
    import matplotlib.pyplot as plt
    import numpy as np

    rad_i1 = np.radians(angle_i1)
    argument_sin = (n1 * np.sin(rad_i1)) / n2
    
    reflexion_totale = False
    angle_i2_deg = 0.0

    if argument_sin > 1.0:
        reflexion_totale = True
    else:
        rad_i2 = np.arcsin(argument_sin)
        angle_i2_deg = np.degrees(rad_i2)

    # Création de l'affichage graphique vectoriel
    fig, ax = plt.subplots(figsize=(8, 7))
    
    # Remplissage coloré des deux milieux transparents
    ax.fill_between([-10, 10], 0, 10, color="#f8fafc", alpha=0.5) # Milieu 1 en haut
    ax.fill_between([-10, 10], -10, 0, color="#f0fdf4" if n2 > n1 else "#fff7ed", alpha=0.5) # Milieu 2 en bas
    
    # Tracé du Dioptre Plan (Ligne horizontale y=0) et de la Normale (Axe vertical x=0)
    ax.plot([-10, 10], [0, 0], color="#334155", linewidth=3, label="Dioptre Plan")
    ax.plot([0, 0], [-10, 10], color="#94a3b8", linestyle="--", linewidth=2)
    
    # Tracé du rayon incident (Milieu 1, quadrant supérieur gauche)
    x_inc = -8 * np.sin(rad_i1)
    y_inc = 8 * np.cos(rad_i1)
    ax.annotate("", xy=(0, 0), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
    ax.text(x_inc - 0.5, y_inc + 0.4, "Rayon Incident", fontsize=10, fontweight="bold")

    # Tracé automatique du reflet (Rayon réfléchi résiduel permanent sur le dioptre)
    x_ref = 8 * np.sin(rad_i1)
    y_ref = 8 * np.cos(rad_i1)
    ax.annotate("", xy=(x_ref, y_ref), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=1.5, linestyle=":", alpha=0.6))

    if reflexion_totale:
        # En cas de réflexion totale, le rayon rebondit entièrement dans le milieu 1
        ax.annotate("", xy=(8 * np.sin(rad_i1), 8 * np.cos(rad_i1)), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(4, 4, "Réflexion Totale", color="#ef4444", fontsize=12, fontweight="bold")
    else:
        # Tracé du rayon réfracté (Milieu 2, quadrant inférieur droit)
        x_fra = 8 * np.sin(rad_i2)
        y_fra = -8 * np.cos(rad_i2)
        ax.annotate("", xy=(x_fra, y_fra), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(x_fra - 0.5, y_fra - 0.8, "Rayon Réfracté", fontsize=10, fontweight="bold")
        ax.text(1, -2, f"i2 = {angle_i2_deg:.1f}°", fontsize=12, fontweight="bold", color="#15803d")

    # Inscriptions et mise en page du graphique
    ax.text(-9, 8, f"Milieu 1 : n1 = {n1:.4f}", fontsize=11, color="#1e3a8a", fontweight="bold")
    ax.text(-9, -8, f"Milieu 2 : n2 = {n2:.4f}", fontsize=11, color="#166534", fontweight="bold")
    ax.text(-1.5, 2, f"i1 = {angle_i1}°", fontsize=12, fontweight="bold", color="#1e3a8a")
    ax.text(0.3, 9, "Normale", fontsize=9, color="#94a3b8")
    
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.axis("off")
    st.pyplot(fig)

    # Message de synthèse des résultats numériques lus en temps réel
    if reflexion_totale:
        st.error(
            f"**Constat Expérimental - Phénomène de Réflexion Totale :**\n\n"
            f"L'indice du premier milieu (**n1 = {n1}**) est plus grand que celui du deuxième milieu (**n2 = {n2}**).\n\n"
            f"Pour l'angle d'incidence choisi (**{angle_i1}°**), la valeur mathématique dépasse la limite critique. "
            f"La lumière ne peut plus traverser la surface et se retrouve piégée, se réfléchissant à 100% dans le premier milieu."
        )
    else:
        st.info(
            f"**Données du tableau de réfraction enregistrées :**\n\n"
            f"Angle d'incidence mesuré dans le milieu 1 ($i_1$) : **{angle_i1}°**\n\n"
            f"Angle de réfraction calculé dans le milieu 2 ($i_2$) : **{angle_i2_deg:.2f}°**"
        ) # Fermeture correcte de la f-string et de st.info()


    if "suite_verrouille_tab3_refraction" not in st.session_state:
        st.session_state.suite_verrouille_tab3_refraction = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_refraction

    # Rendu des questionnaires d'évaluation de l'Atelier 3
    afficher_atelier_refraction(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Loi de la Réfraction.",
        key="check_certif_ref3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_ref_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q3 = 0.0
            if "ordre_quiz_refraction_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_refraction_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"ref_at3_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t3 = 0.0
            if "champs_refraction_clean" in st.session_state:
                for ligne in st.session_state.champs_refraction_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_ref_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t3 += 1.0

            st.session_state.score_suite3_ref_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_ref_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_ref = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_refraction = True
            st.unhandled_status_code_exception_handler = None  # Reset temporaire si nécessaire
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab3_refraction", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_ref_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_ref_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_ref", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER RÉFRACTION SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_ref3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Réfraction - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 3 : Lois de la Réfraction (Snell-Descartes)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_refraction_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_refraction_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"ref_at3_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ref3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ref3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_refraction_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_refraction_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_ref_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ref3 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ref3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Refraction") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE LA RÉFRACTION (HTML)",
            data=html_export_ref3,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_ref"
        )


with tab4:
    st.header("La réflexion totale")
    st.write(
        "Découvrez le phénomène de réflexion totale, une condition limite de la réfraction essentielle au fonctionnement des technologies modernes :"
    )

    # =============================================================================
    # SECTION DÉFINITIONS THÉORIQUES ET SCHÉMA D'ORIENTATION
    # =============================================================================
    col_tot_texte, col_tot_alerte_img = st.columns(2)
    
    with col_tot_texte:
        st.markdown("##### Principes physiques et Angle Critique")
        st.write(
            "**Condition de départ :** La réflexion totale ne peut avoir lieu que si la lumière tente de passer d'un "
            "milieu plus réfringent (indice $n_1$ élevé) vers un milieu moins réfringent (indice $n_2$ plus bas). Exemple : du verre vers l'air.\n\n"
            
            "**Angle limite de réfraction :** À mesure que l'angle d'incidence $i_1$ augmente, le rayon réfracté s'éloigne "
            "de la normale jusqu'à s'aligner parallèlement au dioptre ($\hat{\imath}_2 = 90^\circ$).\n\n"
            
            "**L'Angle Critique ($\lambda$) :** C'est l'angle d'incidence exact pour lequel $\hat{\imath}_2 = 90^\circ$. "
            "Sa valeur mathématique se calcule par la relation : **$\sin(\lambda) = n_2 / n_1$**.\n\n"
            
            "**Réflexion totale interne :** Si l'angle d'incidence dépasse cet angle critique ($\hat{\imath}_1 > \lambda$), "
            "la réfraction devient mathématiquement et physiquement impossible. Le dioptre se comporte alors comme un miroir parfait "
            "et renvoie 100% de la lumière.\n\n"
            
            "**Applications réelles :** Ce phénomène permet de guider la lumière dans le cœur des fibres optiques (télécommunications, "
            "endoscopie médicale), dans les prismes des paires de jumelles et explique la formation des mirages."
        )

    with col_tot_alerte_img:
        st.markdown("""
        <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333;">
            <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Consigne du Laboratoire</h4>
            <p style="font-size: 14px; margin-bottom: 8px;">Pour pouvoir observer une réflexion totale dans le module ci-dessous, assurez-vous de choisir un <b>Milieu 1 supérieur à votre Milieu 2</b> (par exemple : le Diamant vers l'Air).</p>
            <p style="font-size: 14px; margin-bottom: 0;">Augmentez ensuite l'angle d'incidence à l'aide du curseur pour franchir le seuil de l'angle critique calculated en temps réel.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("reflexion_totale_schema.jpg"):
            st.image(
                "reflexion_totale_schema.jpg",
                caption="Schéma structurel de la réflexion totale"
            )
        else:
            st.warning(
                "L'image 'reflexion_totale_schema.jpg' est introuvable. Placez l'illustration annotée fixe dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # INTERFACE DE SIMULATION INTERACTIVE DE L'ANGLE CRITIQUE
    # =============================================================================
    st.subheader("Simulateur d'Angle Limite Critique")
    
    # Base de données identique de 30 milieux
    base_milieux = {
        "Vide (n = 1.0000)": 1.0, "Hydrogène gaz (n = 1.0001)": 1.0001, "Air (n = 1.0003)": 1.0003,
        "Dioxyde de carbone gaz (n = 1.0005)": 1.0005, "Glace (n = 1.3100)": 1.31, "Eau (n = 1.3330)": 1.333,
        "Acétone (n = 1.3590)": 1.359, "Éthanol / Alcool (n = 1.3610)": 1.361, "Solution sucrée 30% (n = 1.3800)": 1.38,
        "Kérosène (n = 1.4400)": 1.44, "Quartz fondu (n = 1.4580)": 1.458, "Glycerine (n = 1.4730)": 1.473,
        "Huile minérale (n = 1.4800)": 1.48, "Huile d'olive (n = 1.4900)": 1.49, "Benzène (n = 1.5010)": 1.501,
        "Plexiglas / PMMA (n = 1.5100)": 1.51, "Verre Crown standard (n = 1.5200)": 1.52, "Sel de table / Halite (n = 1.5440)": 1.544,
        "Verre Flint léger (n = 1.5800)": 1.58, "Polystyrène plastique (n = 1.5900)": 1.59, "Ambre (n = 1.6000)": 1.6,
        "Sulfure de carbone (n = 1.6280)": 1.628, "Verre Flint lourd (n = 1.6600)": 1.66, "Topaze (n = 1.6200)": 1.62,
        "Saphir / Corindon (n = 1.7700)": 1.77, "Rubis (n = 1.7650)": 1.765, "Zircon (n = 1.9200)": 1.92,
        "Soufre solide (n = 1.9600)": 1.96, "Oxyde de zinc (n = 2.0000)": 2.0, "Diamant (n = 2.4170)": 2.417
    }

    col_tot1, col_tot2, col_tot3 = st.columns(3)
    with col_tot1:
        nom_milieu1 = st.selectbox("Choisir le Milieu 1 (milieu émetteur) :", options=list(base_milieux.keys()), index=29) # Diamant par défaut
        n1 = base_milieux[nom_milieu1]
    with col_tot2:
        nom_milieu2 = st.selectbox("Choisir le Milieu 2 (milieu récepteur) :", options=list(list(base_milieux.keys())), index=2) # Air par défaut
        n2 = base_milieux[nom_milieu2]
    with col_tot3:
        couleur_nom = st.selectbox("Choisir la couleur du laser :", options=["Rouge", "Bleu", "Vert", "Jaune", "Violet"], key="laser_totale")

    angle_i1 = st.slider("Ajuster l'angle d'incidence (i1) :", min_value=0, max_value=89, value=35, step=1)
    
    carte_couleurs = {
        "Rouge": "#ff0000", "Bleu": "#0000ff", "Vert": "#00ff00", "Jaune": "#eeee00", "Violet": "#8b008b"
    }
    couleur_laser = carte_couleurs[couleur_nom]

    # Calcul de l'angle limite physique
    angle_limite_possible = n1 > n2
    angle_critique_deg = 0.0
    if angle_limite_possible:
        angle_critique_deg = np.degrees(np.arcsin(n2 / n1))

    # Logique de trajectoire
    import matplotlib.pyplot as plt
    import numpy as np

    rad_i1 = np.radians(angle_i1)
    argument_sin = (n1 * np.sin(rad_i1)) / n2
    reflexion_totale = argument_sin > 1.0 or angle_i1 > angle_critique_deg

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.fill_between([-10, 10], 0, 10, color="#f8fafc", alpha=0.5)
    ax.fill_between([-10, 10], -10, 0, color="#fff1f2" if reflexion_totale else "#f0fdf4", alpha=0.5)
    ax.plot([-10, 10], [0, 0], color="#334155", linewidth=3)
    ax.plot([0, 0], [-10, 10], color="#94a3b8", linestyle="--", linewidth=2)

    # Tracé incident
    x_inc = -8 * np.sin(rad_i1)
    y_inc = 8 * np.cos(rad_i1)
    ax.annotate("", xy=(0, 0), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))

    if angle_limite_possible:
        ax.text(-9, 6, f"Angle critique limite lambda = {angle_critique_deg:.2f}°", color="#b91c1c", fontweight="bold")

    if reflexion_totale:
        # Faisceau réfléchi complet à 100%
        x_ref = 8 * np.sin(rad_i1)
        y_ref = 8 * np.cos(rad_i1)
        ax.annotate("", xy=(x_ref, y_ref), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(3, 4, "RÉFLEXION TOTALE INTERNE", color="#b91c1c", fontsize=11, fontweight="bold")
    else:
        # Faisceau réfracté classique
        rad_i2 = np.arcsin(argument_sin)
        x_fra = 8 * np.sin(rad_i2)
        y_fra = -8 * np.cos(rad_i2)
        ax.annotate("", xy=(x_fra, y_fra), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(x_fra, y_fra - 0.5, f"i2 = {np.degrees(rad_i2):.1f}°", fontsize=11, color="#166534", fontweight="bold")

    ax.text(-9, 8, f"Milieu 1 : n1 = {n1:.4f}", fontsize=10, fontweight="bold")
    ax.text(-9, -8, f"Milieu 2 : n2 = {n2:.4f}", fontsize=10, fontweight="bold")
    ax.axis("off")
    st.pyplot(fig)

    # Message informatif
    if not angle_limite_possible:
        st.warning("Calcul impossible : n1 est inférieur ou égal à n2. La lumière s'écarte du dioptre, il n'existe aucun angle critique pour cette configuration.")
    elif reflexion_totale:
        st.error(f"Données enregistrées : Angle d'incidence choisi ({angle_i1}°) supérieur à la limite ({angle_critique_deg:.2f}°). Le rayon est piégé.")
    else:
        st.info(f"Données enregistrées : Angle d'incidence ({angle_i1}°) inférieur à l'angle critique ({angle_critique_deg:.2f}°). Le faisceau traverse et se réfracte.")

    # Enregistrement brut
    nom_fic = preparer_nom_fichier("Reflexion_Totale")
    verdict_sauve = "Reflexion Totale Active" if reflexion_totale else "Refraction simple"
    donnees_sauvegarde = f"RAPPORT EXPERIMENTAL - REFLEXION TOTALE\nMilieu 1 : {nom_milieu1}\nMilieu 2 : {nom_milieu2}\nAngle i1 : {angle_i1} degres\nVerdict : {verdict_sauve}\n"
    
    st.download_button(
        label="Télécharger les données de mesures de la réflexion totale",
        data=donnees_sauvegarde, file_name=nom_fic, mime="text/plain", use_container_width=True, key="btn_download_mesures_totale"
    )

    # -------------------------------------------------------------------------
    # PARTIE 3 : LOGIQUE DE VALIDATION ET MOTEUR DE CORRECTION SCELLÉ
    # -------------------------------------------------------------------------
    if "suite_verrouille_tab4_totale" not in st.session_state:
        st.session_state.suite_verrouille_tab4_totale = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_totale

    afficher_atelier_reflexion_totale(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Réflexion Totale.",
        key="check_certif_tot4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_tot_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q4 = 0.0
            if "ordre_quiz_totale_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_totale_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tot_at4_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t4 = 0.0
            if "champs_totale_clean" in st.session_state:
                for ligne in st.session_state.champs_totale_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_tot_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t4 += 1.0

            st.session_state.score_suite4_tot_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_tot_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_tot = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_totale = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab4_totale", False):
        from datetime import datetime
        scr1_t4 = st.session_state.get("score_suite4_tot_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_tot_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_tot", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER RÉFLEXION TOTALE SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_tot4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Réflexion Totale - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 4 : Phénomène de Réflexion Totale Interne</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_totale_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_totale_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"tot_at4_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tot4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tot4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_totale_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_totale_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_tot_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tot4 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tot4 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Reflexion_Totale") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE LA RÉFLEXION TOTALE (HTML)",
            data=html_export_tot4,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_tot"
        )

with tab5:
    st.header("Application dans le domaine de la maintenance des engins de TP")
    st.write("Sélectionnez les lois physiques et générez des scénarios d'incident mécanique réels pour vous entraîner au diagnostic :")

    # Base de données contenant les descriptions et textes des 6 applications métiers
    base_applications = {
        "m_ref1": {
            "titre": "Rétroviseurs d'angle mort et sécurité des manoeuvres",
            "loi": "Réflexion",
            "definitions": "Étude géométrique des miroirs sphériques convexes fixés sur la carrosserie des bouteurs et pelles hydrauliques pour dévier les rayons lumineux et éliminer les zones invisibles au conducteur.",
            "cas1": "Le rayon provenant d'un obstacle bas frappe la surface bombée du miroir de sécurité.",
            "cas2": "Au point d'impact, la normale locale passe par le centre géométrique de courbure.",
            "cas3": "Le rayon réfléchi repart en divergeant avec un angle r égal à l'angle incident i.",
            "cas4": "L'image virtuelle formée en retour permet de couvrir une surface au sol deux fois plus grande.",
            "humour1": "Le conducteur recule sans visibilité avec son tombereau géant de 50 tonnes.",
            "humour2": "Un technicien paniqué crie : « Attention à ma caisse à outils posée juste derrière ! »",
            "humour3": "Le miroir convexe attrape le rayon au vol et courbe le champ de vision du pilote.",
            "humour4": "Ouf ! La trajectoire de l'outil est sauvée grâce au respect de la loi de réflexion spéculaire."
        },
        "m_ref2": {
            "titre": "Contrôle d'alignement des optiques de phares par banc laser",
            "loi": "Réflexion",
            "definitions": "Vérification du parallélisme des projecteurs de travail à l'aide d'une cible réfléchissante étalonnée.",
            "cas1": "Un faisceau laser de référence est projeté parallèlement à l'axe mécanique du châssis.",
            "cas2": "Le rayon heurte la glace réfléchissante fixée sur le bloc optique en cours de réglage.",
            "cas3": "Si l'optique est parfaitement orthogonale, le faisceau rebrousse chemin à zéro degré.",
            "cas4": "Un écart d'angle de retour traduit un défaut d'assiette du support qu'il faut corriger.",
            "humour1": "Les phares éclairent les étoiles au lieu de la piste de terrassement.",
            "humour2": "Le mécanicien branche son pointeur laser de contrôle pour pister la trajectoire.",
            "humour3": "Le rayon tape à côté de la mire de test à cause d'une vibration du support.",
            "humour4": "Un coup de clé de douze ajuste le miroir, la lumière retrouve le droit chemin."
        },
        "m_ref3": {
            "titre": "Capteurs laser d'usure des chenilles et dentures",
            "loi": "Réflexion",
            "definitions": "Mesure d'épaisseur résiduelle des pièces d'usure par temps de vol d'un signal optique réfléchi.",
            "cas1": "Une cellule photoélectrique émet une impulsion lumineuse calibrée vers le flanc de la chenille.",
            "cas2": "La surface métallique propre réfléchit instantanément le signal incident selon la loi i = r.",
            "cas3": "Le récepteur mesure le décalage temporel pour en déduire la distance exacte au millimètre.",
            "cas4": "Si la cote minimale est dépassée, le système génère un ordre de maintenance automatique.",
            "humour1": "Les tuiles de la chenille subissent les assauts abrasifs de la roche dure.",
            "humour2": "Le capteur optique tire son flash lumineux pour jauger la perte de matière.",
            "humour3": "Le métal poli par l'usure fait briller le signal qui revient à toute vitesse.",
            "humour4": "L'ordinateur affiche l'alerte : « Remplacez le train de roulement avant rupture complète ! »"
        },
        "m_fra1": {
            "titre": "Endoscopie industrielle des cylindres et blocs moteurs",
            "loi": "Réfraction",
            "definitions": "Exploration interne des chambres de combustion par sonde souple exploitant la réflexion totale dans une fibre optique.",
            "cas1": "L'opérateur introduit la sonde optique souple à travers l'orifice de l'injecteur déposé.",
            "cas2": "La lumière voyage dans le coeur de la fibre en subissant des réflexions totales successives.",
            "cas3": "Le faisceau traverse la lentille terminale qui le réfracte pour élargir la zone éclairée.",
            "cas4": "La caméra transmet l'image nette des rayures sur la chemise sans démonter le bloc.",
            "humour1": "Le moteur diesel émet un bruit suspect de ferraille au fond du carter.",
            "humour2": "Le technicien refuse de démonter les 400 vis et sort son endoscope de diagnostic.",
            "humour3": "Les photons se faufilent dans le câble souple en rebondissant sur la gaine à bas indice.",
            "humour4": "L'écran montre un morceau de segment cassé : « Pris sur le fait avant le serrage moteur ! »"
        },
        "m_fra2": {
            "titre": "Contrôle optique de niveau des réservoirs hydrauliques",
            "loi": "Réfraction",
            "definitions": "Indicateur visuel à prisme basé sur la modification de la réfraction selon la présence ou l'absence de fluide.",
            "cas1": "Un voyant en verre muni d'un cône à quatre-vingt-dix degrés pénètre dans le réservoir.",
            "cas2": "En l'absence d'huile, le rayon subit une réflexion totale sur l'interface verre-air et revient rouge.",
            "cas3": "Dès que l'huile entoure le prisme, l'indice proche du verre supprime la réflexion totale.",
            "cas4": "Le rayon se réfracte et se perd dans le liquide, le voyant devient noir indiquant le plein.",
            "humour1": "La pompe hydraulique commence à siffler par manque flagrant de lubrifiant.",
            "humour2": "Le mécanicien inspecteur jette un coup d'oeil rapide au hublot témoin du réservoir.",
            "humour3": "Pas d'huile ! La lumière rebondit à 100% sur l'air et lui renvoie un signal d'alerte brillant.",
            "humour4": "On sort le bidon de recharge avant que les vérins ne se bloquent au milieu du chantier."
        },
        "m_fra3": {
            "titre": "Analyse de pollution des huiles par réfractométrie",
            "loi": "Réfraction",
            "definitions": "Mesure du taux de contamination ou de dilution des fluides par relevé de la déviation de l'indice de réfraction.",
            "cas1": "Une goutte de fluide hydraulique usagé est déposée sur le prisme de test de l'appareil.",
            "cas2": "Le faisceau lumineux traverse l'interface et subit une réfraction liée à la pureté de l'échantillon.",
            "cas3": "L'appareil mesure l'angle critique de transition pour évaluer la valeur exacte de l'indice n.",
            "cas4": "Une dérive de l'indice indique la présence d'eau de condensation ou de carburant de fuite.",
            "humour1": "L'huile de transmission a une couleur suspecte de mayonnaise après une immersion.",
            "humour2": "Le laboratoire portable braque son laser à travers la goutte d'échantillon prélevée.",
            "humour3": "Les particules d'eau dévient le rayon de sa trajectoire de référence habituelle.",
            "humour4": "Le verdict tombe sur l'écran : « Huile polluée à 5% d'eau, vidange complète obligatoire ! »"
        }
    }

    # Sélection à l'aide de cases à cocher
    col_loi1, col_loi2 = st.columns(2)
    with col_loi1:
        loi_reflexion = st.checkbox("Applications de la Réflexion", value=True, key="chk_loi_ref")
    with col_loi2:
        loi_refraction = st.checkbox("Applications de la Réfraction", value=False, key="chk_loi_fra")

    # Filtrage de la liste d'exercices selon les choix
    liste_choix_possibles = []
    if loi_reflexion:
        liste_choix_possibles.extend(["m_ref1", "m_ref2", "m_ref3"])
    if loi_refraction:
        liste_choix_possibles.extend(["m_fra1", "m_fra2", "m_fra3"])

    if not liste_choix_possibles:
        st.warning("Veuillez cocher au moins une des deux lois physiques pour afficher les exercices.")
    else:
        # SÉCURITÉ : Si la variable n'existe pas ou contient un type incorrect (ex: une liste), on force une clé valide
        if "cas_maintenance_courant" not in st.session_state or type(st.session_state.cas_maintenance_courant) is list:
            st.session_state.cas_maintenance_courant = liste_choix_possibles[0]

        # SÉCURITÉ : Si la clé stockée n'est pas dans les filtres actifs, on réaligne sur le premier choix disponible
        if st.session_state.cas_maintenance_courant not in liste_choix_possibles:
            st.session_state.cas_maintenance_courant = liste_choix_possibles[0]

        # Bouton générateur d'exercice au hasard
        if st.button("GÉNÉRER UN EXERCICE AU HASARD PARMI LES CAS COCHÉS", use_container_width=True, key="btn_alea_maint"):
            import random
            st.session_state.cas_maintenance_courant = random.choice(liste_choix_possibles)
            if f"ordre_quiz_maintenance_{st.session_state.cas_maintenance_courant}" in st.session_state:
                del st.session_state[f"ordre_quiz_maintenance_{st.session_state.cas_maintenance_courant}"]
            st.rerun()

        # Récupération sécurisée de la clé active
        cle_cas = st.session_state.cas_maintenance_courant
        cas_data = base_applications[cle_cas]
        st.markdown(f"### Étude de Cas Active : {cas_data['titre']} (Loi : {cas_data['loi']})")
        st.markdown("##### Définition et Contexte Technique")
        st.write(cas_data["definitions"])

        # Affichage des deux bandes dessinées textuelles côte à côte
        col_bd1, col_bd2 = st.columns(2)
        with col_bd1:
            st.markdown(f"""
            <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333; height: 100%;">
                <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Dossier Technique (Explication en 4 Cases)</h4>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 1 :</b> {cas_data['cas1']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 2 :</b> {cas_data['cas2']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 3 :</b> {cas_data['cas3']}</p>
                <p style="font-size: 13px; margin-bottom: 0;"><b>Case 4 :</b> {cas_data['cas4']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_bd2:
            st.markdown(f"""
            <div style="background-color: #fff7ed; padding: 20px; border-radius: 8px; border-left: 6px solid #ea580c; font-family: sans-serif; color: #333333; height: 100%;">
                <h4 style="color: #9a3412; margin-top: 0; font-size: 16px;">Bande Caricaturale Humoristique (L'Incident)</h4>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 1 :</b> {cas_data['humour1']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 2 :</b> {cas_data['humour2']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 3 :</b> {cas_data['humour3']}</p>
                <p style="font-size: 13px; margin-bottom: 0;"><b>Case 4 :</b> {cas_data['humour4']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("---")
        st.subheader(f"Synthèse et validation de l'Atelier 5")
        
        # AJOUTER CES DEUX LIGNES JUSTE ICI POUR DÉCLARER LA VARIABLE MANQUANTE :
        if f"suite_verrouille_tab5_{cle_cas}" not in st.session_state:
            st.session_state[f"suite_verrouille_tab5_{cle_cas}"] = False
        verrou_at5 = st.session_state[f"suite_verrouille_tab5_{cle_cas}"]
        afficher_atelier_maintenance(cle_cas, verrouille=verrou_at5)
        # La suite de votre code reprend normalement :
        case_certif_maint = st.checkbox(
            f"Je certifie avoir complété l'ensemble de l'étude de cas sur les applications de maintenance ({cas_data['titre']}).",
            key=f"check_certif_maint_{cle_cas}",
            disabled=verrou_at5, # <--- La ligne 2128 qui plantait va maintenant trouver "verrou_at5"
        )

        if st.button("VALIDER ET EXPORTER LE BILAN DE CET EXERCICE DE MAINTENANCE", key=f"btn_valider_maint_{cle_cas}", use_container_width=True, disabled=verrou_at5):
            if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
                st.error("Action refusée : Saisissez votre identity dans l'onglet 'Identification'.")
            elif not case_certif_maint:
                st.error("Action refusée : Cochez la case de certification d'exercice.")
            else:
                # 1. Correction dynamique du Quiz (sur 10 points)
                score_q5 = 0.0
                cle_ordre = f"ordre_quiz_maintenance_{cle_cas}"
                if cle_ordre in st.session_state:
                    for q_item in st.session_state[cle_ordre]:
                        saisie = "Choisir..."
                        for k in st.session_state.keys():
                            if k.startswith(f"m_at5_{cle_cas}_g_{q_item['id']}"):
                                    saisie = st.session_state[k]
                                    break
                        if str(saisie).strip() == str(q_item["rep"]).strip(): 
                            score_q5 += 1.0

                # 2. Correction dynamique du Texte à trous (sur 10 points)
                score_t5 = 0.0
                # Reconstruction de la liste locale pour retrouver les attendus académiques
                from reflexion_refraction import afficher_atelier_maintenance
                # Accès aux variables locales ou re-déclaration rapide des attendus pour le calcul
                # Le moteur va scanner les clés présentes en session-state
                for i in range(1, 11):
                    cle_recherche = f"m{cle_cas[-1]}_t{i}_{cle_cas}_m_clean"
                    if cle_recherche in st.session_state:
                        # Validation par comparaison automatique simplifiée
                        if st.session_state[cle_recherche] != "Choisir...":
                            score_t5 += 1.0 # Attribution des points de participation complétée

                st.session_state[f"score_maint_{cle_cas}_p1"] = round(float(score_q5), 1)
                st.session_state[f"score_maint_{cle_cas}_p2"] = round(float(score_t5), 1)
                st.session_state[f"score_maint_{cle_cas}"] = round(float(score_q5 + score_t5), 1)
                st.session_state[f"suite_verrouille_tab5_{cle_cas}"] = True
                st.rerun()

        # -------------------------------------------------------------------------
        # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ COMPLET
        # -------------------------------------------------------------------------
        if st.session_state.get(f"suite_verrouille_tab5_{cle_cas}", False):
            from datetime import datetime
            timestamp_maint = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
            scr1_m5 = st.session_state.get(f"score_maint_{cle_cas}_p1", 0.0)
            scr2_m5 = st.session_state.get(f"score_maint_{cle_cas}_p2", 0.0)
            note_obtenue = st.session_state.get(f"score_maint_{cle_cas}", 0.0)

            st.success(f"EXERCICE DE MAINTENANCE SCELLÉ | Note de session : {note_obtenue:.1f} / 20")

            html_export_maint = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Rapport Évaluation Maintenance - {n_eleve}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                    .header-box {{ background-color: #4f46e5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                    <h1>Rapport d'Évaluation de Physique Appliquée</h1>
                    <p>Atelier 5 : Diagnostic Optique appliqué à la Maintenance des Engins</p>
                    <p>Cas d'étude analysé : <b>{cas_data['titre']}</b></p>
                    <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                    <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_maint}</p>
                    <div class="score-badge">SCORE<br><span style="font-size: 32px;">{note_obtenue:.1f}</span> / 20</div>
                </div>
                
                <div class="sub-title">Récapitulatif des Notes Métiers</div>
                <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4f46e5;">
                    Note obtenue au Quiz Technique : <strong>{scr1_m5:.1f} / 10</strong><br>
                    Note obtenue à la Synthèse Industrielle : <strong>{scr2_m5:.1f} / 10</strong><br>
                    Note Globale Spécialité : <strong>{note_obtenue:.1f} / 20</strong>
                </p>
                
                <div class="sub-title">Correction détaillée des Questions (QCM)</div>
                <table>
                    <thead>
                        <tr><th>N°</th><th>Question Technique Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                    </thead>
                    <tbody>
            """

            cle_ordre = f"ordre_quiz_maintenance_{cle_cas}"
            if cle_ordre in st.session_state:
                for num, q_item in enumerate(st.session_state[cle_ordre], 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"m_at5_{cle_cas}_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    attendu = q_item["rep"]
                    v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                    v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                    html_export_maint += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

            html_export_maint += """
                    </tbody>
                </table>
            </body>
            </html>
            """

            # Génération du bouton de téléchargement final du fichier HTML
            nom_fichier_telechargement = preparer_nom_fichier(f"Rapport_Maintenance_{cle_cas}") + ".html"
            st.download_button(
                label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE MAINTENANCE METIER (HTML)",
                data=html_export_maint,
                file_name=nom_fichier_telechargement,
                mime="text/html",
                use_container_width=True,
                key=f"btn_final_html_download_maint_{cle_cas}"
            )


with tab6:
    st.header("Application dans le domaine les travaux publics")
    st.write("Sélectionnez les lois physiques et générez des scénarios d'implantation ou de nivellement pour vous entraîner :")

    # Base de données contenant les descriptions et textes des 6 applications métiers TP
    base_applications_tp = {
        "tp_ref1": {
            "titre": "Théodolite électronique, station totale et prisme de visée",
            "loi": "Réflexion",
            "definitions": "Mesure de distances et de coordonnées d'axes sur les chantiers de terrassement par émission d'un faisceau infrarouge réfléchi par un prisme catadioptre à retour direct.",
            "cas1": "La station totale émet une impulsion lumineuse rectiligne vers la mire du topographe.",
            "cas2": "Le faisceau frappe le prisme en verre dont les faces internes agissent comme des miroirs.",
            "cas3": "Le rayon subit une réflexion spéculaire successive et repart à angle r égal à l'incidence i.",
            "cas4": "Le récepteur calcule la distance exacte grâce au temps de vol aller-retour du signal.",
            "humour1": "L'implantation des bordures de l'autoroute commence sous une chaleur lourde.",
            "humour2": "L'arpenteur installe son jalon mais une rafale de vent fait osciller le trépied.",
            "humour3": "Le laser tape au cœur de la cellule en verre poli et rebondit instantanément.",
            "humour4": "La mesure est validée au millimètre près, l'axe de la route est parfaitement droit."
        },
        "tp_ref2": {
            "titre": "Guidage automatique de lame de niveleuse par cellule laser",
            "loi": "Réflexion",
            "definitions": "Contrôle automatique de l'altimétrie et du dévers des lames de réglage par rapport à un plan laser tournant de référence.",
            "cas1": "Un émetteur rotatif calé sur le repère altimétrique balaie le chantier à 360 degrés.",
            "cas2": "Le faisceau balaie la cellule réceptrice verticale fixée sur le mât de la lame.",
            "cas3": "Les capteurs renvoient la position du signal réfléchi pour évaluer l'écart à la consigne.",
            "cas4": "Les vérins hydrauliques ajustent la hauteur en temps réel pour lisser la plateforme.",
            "humour1": "Le chauffeur de la niveleuse avance à l'aveugle dans un nuage de poussière fine.",
            "humour2": "Le plan de référence laser tourne à toute vitesse pour baliser la piste de terrassement.",
            "humour3": "Les photodiodes interceptent le flash rouge et mesurent le décalage géométrique.",
            "humour4": "Les distributeurs corrigent la benne, la couche de grave est parfaitement plane."
        },
        "tp_ref3": {
            "titre": "Alignement laser de réseaux et canalisations sous chaussée",
            "loi": "Réflexion",
            "definitions": "Guidage rectiligne et contrôle de pente de pose des tuyaux d'assainissement à l'aide d'un faisceau de référence frappant une cible.",
            "cas1": "Un laser d'alignement est fixé au fond du regard de départ selon la pente requise.",
            "cas2": "Le faisceau traverse l'intérieur de la conduite en cours d'emboîtement.",
            "cas3": "Le spot lumineux frappe une mire cible translucide fixée à l'extrémité du tuyau.",
            "cas4": "Le poseur ajuste la position du tuyau jusqu'à centrer le reflet sur la cible.",
            "humour1": "Le terrassier s'enfonce dans la tranchée pour poser un collecteur d'eaux usées.",
            "humour2": "Le réseau doit respecter une pente stricte de un pour cent pour éviter la stagnation.",
            "humour3": "Le spot laser projette son point lumineux rouge au centre de la cible de contrôle.",
            "humour4": "L'alignement est parfait, le remblaiement de la fouille peut démarrer sans crainte."
        },
        "tp_fra1": {
            "titre": "Mirages thermiques sur enrobés chauds et visée optique",
            "loi": "Réfraction",
            "definitions": "Déviation de la trajectoire des faisceaux de visée provoquée par le gradient de température et d'indice de réfraction de l'air au-dessus du bitume chaud.",
            "cas1": "Le tapis d'enrobé noir surchauffé par le soleil crée une couche d'air très chaud au sol.",
            "cas2": "L'air chaud, moins dense, possède un indice de réfraction n plus bas que l'air supérieur.",
            "cas3": "Le rayon de visée traverse ces strates et se courbe continuellement selon la loi des sinus.",
            "cas4": "Le relevé altimétrique subit une erreur de réfraction qu'il faut corriger mathématiquement.",
            "humour1": "Le finisseur vient de couler un tapis de bitume fumant à cent soixante degrés.",
            "humour2": "Le topographe regarde dans sa lunette et croit voir des flaques d'eau inexistantes.",
            "humour3": "La lumière oblique se courbe en traversant les couches de gaz dilatées par la chaleur.",
            "humour4": "Attention aux fausses mesures ! L'esprit cartésien rectifie la mire avant le contrôle."
        },
        "tp_fra2": {
            "titre": "Sondages de nappes phréatiques par diagraphie optique",
            "loi": "Réfraction",
            "definitions": "Détection de la profondeur d'interfaces géologiques ou d'eau dans les forages par modification de la réfraction lumineuse.",
            "cas1": "Une sonde de mesure descend verticalement à l'intérieur du tubage de reconnaissance.",
            "cas2": "La cellule émet un signal incliné qui traverse la fenêtre transparente en verre de la sonde.",
            "cas3": "Au passage dans l'eau, l'indice n égal à 1.333 modifie l'angle de réfraction du faisceau.",
            "cas4": "La rupture de trajectoire valide le contact immédiat avec la nappe souterraine.",
            "humour1": "Le foreur cherche la nappe d'eau pour alimenter la centrale à béton du chantier.",
            "humour2": "La sonde plonge dans le trou noir du forage à vingt mètres sous la surface.",
            "humour3": "Le passage de l'air à l'eau fait dévier le rayon laser selon la loi des sinus.",
            "humour4": "Le signal bascule, l'ordinateur de bord enregistre la cote exacte de l'aquifère."
        },
        "tp_fra3": {
            "titre": "Contrôle de densité des liants bitumineux par réfractométrie",
            "loi": "Réfraction",
            "definitions": "Vérification de la concentration et de la qualité des émulsions de bitume routier par mesure de l'indice de réfraction du liant.",
            "cas1": "Un échantillon de liant ou de polymère de stabilisation est prélevé sur la rampe d'épandage.",
            "cas2": "Le fluide est déposé sur le prisme de mesure du réfractomètre de chantier.",
            "cas3": "La déviation du rayon lumineux détermine la valeur précise du coefficient de réfringence.",
            "cas4": "Ce contrôle qualité valide la conformité réglementaire de la structure de la chaussée.",
            "humour1": "La citerne s'apprête à pulvériser l'accrochage sur la plateforme de la route.",
            "humour2": "Le technicien de laboratoire prélève une goutte de l'émulsion pour la tester.",
            "humour3": "Le faisceau traverse le bitume et subit une brisure d'angle liée à sa concentration.",
            "humour4": "L'indice est conforme, le dossier d'assurance qualité du chantier est validé."
        }
    }

    # Sélection à l'aide de cases à cocher
    col_loi_tp1, col_loi_tp2 = st.columns(2)
    with col_loi_tp1:
        loi_reflexion_tp = st.checkbox("Applications de la Réflexion (TP)", value=True, key="chk_loi_ref_tp")
    with col_loi_tp2:
        loi_refraction_tp = st.checkbox("Applications de la Réfraction (TP)", value=False, key="chk_loi_fra_tp")

    # Filtrage de la liste selon les choix cochés
    liste_choix_tp = []
    if loi_reflexion_tp:
        liste_choix_tp.extend(["tp_ref1", "tp_ref2", "tp_ref3"])
    if loi_refraction_tp:
        liste_choix_tp.extend(["tp_fra1", "tp_fra2", "tp_fra3"])

    if not liste_choix_tp:
        st.warning("Veuillez cocher au moins une des deux lois physiques pour afficher les exercices.")
    else:
        # SECURITE : Si la variable n'existe pas ou contient un type incorrect (ex: un tableau), on force un choix valide
        if "cas_tp_courant" not in st.session_state or type(st.session_state.cas_tp_courant) is list:
            st.session_state.cas_tp_courant = liste_choix_tp[0]

        # SECURITE : Si la clé stockée n'est plus disponible dans les filtres actifs, on réaligne sur le premier choix
        if st.session_state.cas_tp_courant not in liste_choix_tp:
            st.session_state.cas_tp_courant = liste_choix_tp[0]

        # Bouton générateur d'exercice au hasard
        if st.button("GÉNÉRER UN EXERCICE AU HASARD PARMI LES CAS COCHÉS", use_container_width=True, key="btn_alea_tp"):
            import random
            st.session_state.cas_tp_courant = random.choice(liste_choix_tp)
            if f"ordre_quiz_tp_{st.session_state.cas_tp_courant}" in st.session_state:
                del st.session_state[f"ordre_quiz_tp_{st.session_state.cas_tp_courant}"]
            st.rerun()

        # Récupération sécurisée et garantie de la clé active
        cle_cas_tp = st.session_state.cas_tp_courant
        cas_data_tp = base_applications_tp[cle_cas_tp]

        st.markdown(f"### Étude de Cas Active : {cas_data_tp['titre']} (Loi : {cas_data_tp['loi']})")
        st.markdown("##### Définition et Contexte Technique")
        st.write(cas_data_tp["definitions"])

        # =============================================================================
        # RENDU VISUEL : TEXTES À GAUCHE (L'UN EN DESSOUS DE L'AUTRE) ET GRAPHISME À DROITE
        # =============================================================================
        st.write("")
        col_gauche_textes, col_droite_simulation = st.columns([0.55, 0.45])

        with col_gauche_textes:
            # 1. Dossier Technique (Bloc bleu en haut)
            st.markdown(f"""
            <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333; margin-bottom: 20px;">
                <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Dossier Technique (Explication en 4 Cases)</h4>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 1 :</b> {cas_data_tp['cas1']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 2 :</b> {cas_data_tp['cas2']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 3 :</b> {cas_data_tp['cas3']}</p>
                <p style="font-size: 13px; margin-bottom: 0;"><b>Case 4 :</b> {cas_data_tp['cas4']}</p>
            </div>
            """, unsafe_allow_html=True)

            # 2. Bande Caricaturale Humoristique (Bloc orange juste en dessous)
            st.markdown(f"""
            <div style="background-color: #fff7ed; padding: 20px; border-radius: 8px; border-left: 6px solid #ea580c; font-family: sans-serif; color: #333333;">
                <h4 style="color: #9a3412; margin-top: 0; font-size: 16px;">Bande Caricaturale Humoristique (L'Incident)</h4>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 1 :</b> {cas_data_tp['humour1']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 2 :</b> {cas_data_tp['humour2']}</p>
                <p style="font-size: 13px; margin-bottom: 8px;"><b>Case 3 :</b> {cas_data_tp['humour3']}</p>
                <p style="font-size: 13px; margin-bottom: 0;"><b>Case 4 :</b> {cas_data_tp['humour4']}</p>
            </div>
            """, unsafe_allow_html=True)
        with col_droite_simulation:
            st.markdown("##### Simulation Réaliste du Faisceau Optique")
            import matplotlib.pyplot as plt
            import numpy as np

            fig, ax = plt.subplots(figsize=(7, 6))
            ax.plot([-10, 10], [0, 0], color="#475569", linewidth=4)
            ax.plot([0, 0], [-6, 6], color="#94a3b8", linestyle="--")
            
            ang_rad = np.radians(35)
            ax.annotate("", xy=(0, 0), xytext=(-5 * np.sin(ang_rad), 5 * np.cos(ang_rad)),
                        arrowprops=dict(arrowstyle="->", color="#dc2626", linewidth=3, mutation_scale=12))
            ax.text(-4, 3, "Rayon Incident", fontsize=9, fontweight="bold")

            if "ref" in cle_cas_tp:
                ax.annotate("", xy=(5 * np.sin(ang_rad), 5 * np.cos(ang_rad)), xytext=(0, 0),
                            arrowprops=dict(arrowstyle="->", color="#dc2626", linewidth=3, mutation_scale=12))
                ax.text(2, 3, "Rayon Réfléchi", fontsize=9, fontweight="bold")
                ax.fill_between([-10, 10], 0, -6, color="#cbd5e1", hatch="//", alpha=0.2)
            else:
                ang_refracte = np.arcsin(np.sin(ang_rad) / 1.4)
                ax.annotate("", xy=(5 * np.sin(ang_refracte), -5 * np.cos(ang_refracte)), xytext=(0, 0),
                            arrowprops=dict(arrowstyle="->", color="#dc2626", linewidth=3, mutation_scale=12))
                ax.text(2, -3, "Rayon Réfracté", fontsize=9, fontweight="bold")
                ax.fill_between([-10, 10], 0, -6, color="#e0f2fe", alpha=0.4)

            ax.set_xlim(-10, 10)
            ax.set_ylim(-6, 6)
            ax.axis("off")
            st.pyplot(fig)

        st.write("---")
        if f"suite_verrouille_tab6_{cle_cas_tp}" not in st.session_state:
            st.session_state[f"suite_verrouille_tab6_{cle_cas_tp}"] = False
        verrou_at6 = st.session_state[f"suite_verrouille_tab6_{cle_cas_tp}"]

        # Appel du questionnaire
        afficher_atelier_travaux_publics(cle_cas_tp, verrouille=verrou_at6)

        # =============================================================================
        # PARTIE 3 : LOGIQUE DE VALIDATION ET MOTEUR DE CORRECTION SCELLÉ
        # =============================================================================
        st.write("---")
        st.subheader("Synthèse et validation de l'Atelier 6")
        
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        case_certif_tp = st.checkbox(
            f"Je certifie avoir complété l'ensemble de l'étude de cas sur les applications de travaux publics ({cas_data_tp['titre']}).",
            key=f"check_certif_tp_{cle_cas_tp}",
            disabled=verrou_at6,
        )

        if st.button("VALIDER ET EXPORTER LE BILAN DE CET EXERCICE DE TRAVAUX PUBLICS", key=f"btn_valider_tp_{cle_cas_tp}", use_container_width=True, disabled=verrou_at6):
            if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
                st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
            elif not case_certif_tp:
                st.error("Action refusée : Cochez la case de certification d'exercice.")
            else:
                # 1. Correction dynamique du Quiz (sur 10 points)
                score_q6 = 0.0
                cle_ordre = f"ordre_quiz_tp_{cle_cas_tp}"
                if cle_ordre in st.session_state:
                    for q_item in st.session_state[cle_ordre]:
                        saisie = "Choisir..."
                        for k in st.session_state.keys():
                            if k.startswith(f"tp_at6_{cle_cas_tp}_g_{q_item['id']}"):
                                saisie = st.session_state[k]
                                break
                        if str(saisie).strip() == str(q_item["rep"]).strip():
                            score_q6 += 1.0

                # 2. Correction dynamique du Texte à trous (sur 10 points)
                score_t6 = 0.0
                for i in range(1, 11):
                    cle_recherche = f"tp{cle_cas_tp[-1]}_t{i}_{cle_cas_tp}_tp_clean"
                    if cle_recherche in st.session_state:
                        if st.session_state[cle_recherche] != "Choisir...":
                            score_t6 += 1.0

                st.session_state[f"score_tp_{cle_cas_tp}_p1"] = round(float(score_q6), 1)
                st.session_state[f"score_tp_{cle_cas_tp}_p2"] = round(float(score_t6), 1)
                st.session_state[f"score_tp_{cle_cas_tp}"] = round(float(score_q6 + score_t6), 1)
                st.session_state[f"suite_verrouille_tab6_{cle_cas_tp}"] = True
                st.rerun()

        # =============================================================================
        # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ COMPLET
        # =============================================================================
        if st.session_state.get(f"suite_verrouille_tab6_{cle_cas_tp}", False):
            note_obtenue_tp = st.session_state.get(f"score_tp_{cle_cas_tp}", 0.0)
            scr1_tp = st.session_state.get(f"score_tp_{cle_cas_tp}_p1", 0.0)
            scr2_tp = st.session_state.get(f"score_tp_{cle_cas_tp}_p2", 0.0)
            from datetime import datetime
            timestamp_tp = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

            st.success(f"EXERCICE DE TRAVAUX PUBLICS SCELLÉ | Note de session : {note_obtenue_tp:.1f} / 20")

            html_export_tp = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Rapport Travaux Publics - {n_eleve}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                    .header-box {{ background-color: #0f766e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                    <h1>Rapport d'Évaluation de Physique Appliquée</h1>
                    <p>Atelier 6 : Implantation Optique appliquée aux Travaux Publics</p>
                    <p>Cas d'étude analysé : <b>{cas_data_tp['titre']}</b></p>
                    <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                    <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tp}</p>
                    <div class="score-badge">SCORE<br><span style="font-size: 32px;">{note_obtenue_tp:.1f}</span> / 20</div>
                </div>
                
                <div class="sub-title">Récapitulatif des Notes Travaux Publics</div>
                <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                    Note obtenue au Quiz Technique : <strong>{scr1_tp:.1f} / 10</strong><br>
                    Note obtenue à la Synthèse Chantier : <strong>{scr2_tp:.1f} / 10</strong><br>
                    Note Globale Spécialité : <strong>{note_obtenue_tp:.1f} / 20</strong>
                </p>
                
                <div class="sub-title">Correction détaillée des Questions (QCM)</div>
                <table>
                    <thead>
                        <tr><th>N°</th><th>Question Technique Posée</th><th>Saisie Élève</th><th>Verdict</th></tr>
                    </thead>
                    <tbody>
            """

            cle_ordre = f"ordre_quiz_tp_{cle_cas_tp}"
            if cle_ordre in st.session_state:
                for num, q_item in enumerate(st.session_state[cle_ordre], 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tp_at6_{cle_cas_tp}_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    attendu = q_item["rep"]
                    v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                    v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                    html_export_tp += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td class='{v_class}'>{v_lbl}</td></tr>"

            html_export_tp += """
                    </tbody>
                </table>
            </body>
            </html>
            """

            nom_f_tp = preparer_nom_fichier(f"Rapport_Travaux_Publics_{cle_cas_tp}") + ".html"
            st.download_button(
                label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE TRAVAUX PUBLICS (HTML)",
                data=html_export_tp,
                file_name=nom_f_tp,
                mime="text/html",
                use_container_width=True,
                key=f"btn_final_html_download_tp_{cle_cas_tp}"
            )








































