# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime


# Configuration de la fenetre du navigateur
st.set_page_config(
    page_title="TP verrerie et securite",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Signature de l'auteur en bas de page
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

def obtenir_chemin_absolu(nom_fichier):
    import os
    # Vos images etant au meme niveau que le script, on renvoie directement le nom
    return nom_fichier
# =====================================================================
# MORCEAU 1 : INITIALISATION DES VARIABLES DE SESSION (CORRIGÉ)
# =====================================================================
if "identifie" not in st.session_state:
    st.session_state.identifie = False
if "nom" not in st.session_state:
    st.session_state.nom = ""
if "prenom" not in st.session_state:
    st.session_state.prenom = ""
if "classe" not in st.session_state:
    st.session_state.classe = ""

# CORRECTION : Ajout de la variable date_heure manquante
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")

if "mode_examen" not in st.session_state:
    st.session_state.mode_examen = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_reponses" not in st.session_state:
    st.session_state.quiz_reponses = {}
if "quiz_valide" not in st.session_state:
    st.session_state.quiz_valide = False
if "score" not in st.session_state:
    st.session_state.score = 0

# CREATION OBLIGATOIRE DE LA CLE AVANT LA LIGNE 75
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
banque_questions = [
            {"nom": "Fiole jaugée", "categorie": "Volumétrie", "usages": ["Préparation de solutions de concentration donnée", "Dissolution", "Dilution"], "precis": True},
            {"nom": "Burette graduée", "categorie": "Volumétrie", "usages": ["Dosage par titrage direct", "Ajout précis de réactif titrant"], "precis": True},
            {"nom": "Pipette jaugée (1 ou 2 traits)", "categorie": "Volumétrie", "usages": ["Prélèvement d'un volume fixe ultra-précis"], "precis": True},
            {"nom": "Pipette graduée", "categorie": "Volumétrie", "usages": ["Prélèvement d'un volume variable avec précision moyenne"], "precis": True},
            {"nom": "Propipette", "categorie": "Accessoire", "usages": ["Permet d'aspirer, se met délicatement sur une pipette "], "precis": False},
            {"nom": "pH-mètre", "categorie": "Appareil de mesure", "usages": ["Mesure précise du pH d'une solution", "Suivi d'un titrage acido-basique"], "precis": True},
            {"nom": "Balance de précision (au cg ou mg)", "categorie": "Appareil de mesure", "usages": ["Pesée précise de solutés solides pour dissolution"], "precis": True},
            {"nom": "Thermomètre numérique ou à sonde", "categorie": "Appareil de mesure", "usages": ["Suivi des variations de température", "Étude des réactions endo/exothermiques"], "precis": True},
            {"nom": "Multimètre", "categorie": "Appareil de mesure", "usages": ["Mesure de la tension ou de l'intensité", "Étude des piles et de l'électrolyse"], "precis": True},
            {"nom": "Bécher", "categorie": "Contenant", "usages": ["Récipient intermédiaire", "Contenir la solution titrée", "Agitation"], "precis": False},
            {"nom": "Erlenmeyer", "categorie": "Contenant", "usages": ["Récipient de réaction", "Titrage (évite les éclaboussures grâce au col étroit)"], "precis": False},
            {"nom": "Tube à essai", "categorie": "Contenant", "usages": ["Tests qualitatifs de précipitation ou de couleur à petite échelle"], "precis": False},
            {"nom": "Éprouvette graduée", "categorie": "Mesure indicative", "usages": ["Mesure rapide et approximative de volumes de solvants ou réactifs"], "precis": False},
            {"nom": "Verre à pied / Flacon de stockage", "categorie": "Contenant", "usages": ["Metre des solutions usagées "], "precis": False},
            {"nom": "Verre de montre", "categorie": "Contenant", "usages": ["Pesée de solides", "Séchage ou évaporation d'une goutte de liquide"], "precis": False},
            {"nom": "Cristallisoir", "categorie": "Contenant", "usages": ["Bain-marie", "Bain de glace pour refroidir un milieu réactionnel"], "precis": False},
            {"nom": "Ballon à fond rond", "categorie": "Synthèse", "usages": ["Contenir le mélange réactionnel pour un chauffage à reflux ou distillation"], "precis": False},
            {"nom": "Ballon bicol", "categorie": "Synthèse", "usages": ["Synthèse organique nécessitant l'introduction d'un réactif en cours de chauffage", "Mesure de température"], "precis": False},
            {"nom": "Ampoule à décanter", "categorie": "Séparation", "usages": ["Extraction liquide-liquide", "Séparation de la phase aqueuse et de la phase organique"], "precis": False},
            {"nom": "Papier pH", "categorie": "Consommable de mesure", "usages": ["Estimation rapide et grossière du pH d'une solution (à l'unité près)"], "precis": False},
            {"nom": "Agitateur magnétique et barreau aimanté", "categorie": "Matériel de support", "usages": ["Homogénéiser une solution de manière continue pendant une mesure"], "precis": False},
            {"nom": "Entonnoir à liquide", "categorie": "Accessoire", "usages": ["Transvaser proprement un liquide dans une fiole ou une burette"], "precis": False},
            {"nom": "Agitateur en verre", "categorie": "Accessoire", "usages": ["Mélanger manuellement une solution ou aider au transfert de liquide"], "precis": False},
            {"nom": "Tube en U", "categorie": "Électrochimie", "usages": ["Réalisation d'électrolyses", "Mise en évidence de la migration des ions"], "precis": False}
        ]

reactifs = [
            {"nom": "Acide chlorhydrique", "formule": "H3O+ + Cl- (aq)", "famille": "Acide fort", "etat": "Liquide", "pictogrammes": ["Corrosif", "Irritant"], "usage": "Titrages acido-basiques, attaques de métaux."},
            {"nom": "Acide éthanoïque", "formule": "CH3COOH", "famille": "Acide faible", "etat": "Liquide", "pictogrammes": ["Corrosif", "Inflammable"], "usage": "Étude des équilibres chimiques, estérification."},
            {"nom": "Hydroxyde de sodium (Soude)", "formule": "Na+ + HO- (aq)", "famille": "Base forte", "etat": "Liquide / Pastilles", "pictogrammes": ["Corrosif"], "usage": "Titrage d'acides, précipitation d'ions."},
            {"nom": "Ammoniaque", "formule": "NH3 (aq)", "famille": "Base faible", "etat": "Liquide", "pictogrammes": ["Corrosif", "Dangereux pour l'environnement"], "usage": "Études de complexation (ion céleste)."},
            {"nom": "Permanganate de potassium", "formule": "K+ + MnO4- (aq)", "famille": "Oxydant", "etat": "Solution / Cristaux", "pictogrammes": ["Nocif", "Comburant", "Dangereux pour l'environnement"], "usage": "Dosages d'oxydoréduction (indicateur de fin)."},
            {"nom": "Eau oxygénée", "formule": "H2O2", "famille": "Oxydant", "etat": "Liquide", "pictogrammes": ["Corrosif", "Nocif"], "usage": "Étude cinétique (facteurs cinétiques, catalyse)."},
            {"nom": "Thiosulfate de sodium", "formule": "2Na+ + S2O3(2-)", "famille": "Réducteur", "etat": "Liquide", "pictogrammes": [], "usage": "Titrage de l'iode (iodométrie)."},
            {"nom": "Rouleau de Papier pH", "formule": "Indicateur sec", "famille": "Indicateurs & Tests", "etat": "Papier solide", "pictogrammes": [], "usage": "Test d'acidité rapide sans perte de solution."},
            {"nom": "Bleu de bromothymol (BBT)", "formule": "C27H28Br2O5S", "famille": "Indicateurs & Tests", "etat": "Liquide", "pictogrammes": [], "usage": "Titrages (Jaune acide / Vert neutre / Bleu basique)."},
            {"nom": "Nitrate d'argent", "formule": "Ag+ + NO3- (aq)", "famille": "Indicateurs & Tests", "etat": "Liquide", "pictogrammes": ["Corrosif", "Dangereux pour l'environnement"], "usage": "Test d'identification des ions chlorure (Cl-)."},
            {"nom": "Liqueur de Fehling", "formule": "Mélange Tartrate + Cu2+", "famille": "Indicateurs & Tests", "etat": "Liquide bleu", "pictogrammes": ["Nocif", "Dangereux pour l'environnement"], "usage": "Détection des sucres réducteurs (précipité rouge brique)."},
            {"nom": "Eau iodée (Lugol)", "formule": "I3- (aq)", "famille": "Indicateurs & Tests", "etat": "Liquide brun", "pictogrammes": [], "usage": "Détection de l'amidon (devient bleu-violet)."},
            {"nom": "Solution tampon pH 4,00", "formule": "Étalon", "famille": "Solutions Étalons & Maintenance", "etat": "Liquide (Rouge)", "pictogrammes": [], "usage": "Étalonnage obligatoire du pH-mètre."},
            {"nom": "Solution tampon pH 7,00", "formule": "Étalon", "famille": "Solutions Étalons & Maintenance", "etat": "Liquide (Vert)", "pictogrammes": [], "usage": "Étalonnage obligatoire du pH-mètre (neutre)."},
            {"nom": "Sulfate de cuivre pentahydrate", "formule": "Cu2+ + SO4(2-) (aq)", "famille": "Sels metalliques", "etat": "Solution bleue ou Cristaux bleus", "pictogrammes": ["Nocif", "Irritant", "Dangereux pour l'environnement"], "usage": "Etude des solutions ioniques, conductimetrie et reactions de precipitation."},
            {"nom": "Sulfate de fer II", "formule": "Fe2+ + SO4(2-) (aq)", "famille": "Sels metalliques", "etat": "Solution verte ou Cristaux verts", "pictogrammes": ["Nocif", "Irritant"], "usage": "Reactions d'oxydoreduction (couple Fe3+/Fe2+) et tests de precipitation."},
            {"nom": "Sulfate de zinc", "formule": "Zn2+ + SO4(2-) (aq)", "famille": "Sels metalliques", "etat": "Solution incolore ou Poudre blanche", "pictogrammes": ["Corrosif", "Nocif", "Dangereux pour l'environnement"], "usage": "Realisation de la pile Daniell (demi-pile au zinc) et tests d'identification des ions."},
            {"nom": "Chlorure de fer III", "formule": "Fe3+ + 3Cl- (aq)", "famille": "Sels metalliques", "etat": "Solution jaune-orange / Cristaux", "pictogrammes": ["Corrosif", "Nocif"], "usage": "Tests d'identification des ions hydroxydes (precipite rouille) et catalyseur de reactions."},
            {"nom": "Chlorure de fer II", "formule": "Fe2+ + 2Cl- (aq)", "famille": "Sels metalliques", "etat": "Solution verte / Cristaux", "pictogrammes": ["Nocif", "Irritant"], "usage": "Etude des complexes ferreux et reactions d'oxydoreduction."},
            {"nom": "Éthanol", "formule": "C2H5OH", "famille": "Solvants & Organique", "etat": "Liquide", "pictogrammes": ["Inflammable"], "usage": "Solvant de rinçage, extraction, estérification."},
            {"nom": "Cyclohexane", "formule": "C6H12", "famille": "Solvants & Organique", "etat": "Liquide", "pictogrammes": ["Inflammable", "Danger pour la santé", "Dangereux pour l'environnement"], "usage": "Solvant d'extraction (hydrodistillation de la lavande)."},
            {"nom": "Eau distillée", "formule": "H2O", "famille": "Solvants & Organique", "etat": "Liquide", "pictogrammes": [], "usage": "Préparation, dilution, rinçage final."}
        ]

pictogrammes_sgh = [
        {"nom": "SGH01 - Explosif", "desc": "Substance instable susceptible d'exploser sous l'effet de la chaleur, d'un choc ou d'une etincelle.", "exemples": "Substances explosives, peroxydes organiques.", "img": "SGH01.png", "substance_nom": "Peroxyde", "img_exemple": "pot_substances_explosives.png"},
        {"nom": "SGH02 - Inflammable", "desc": "Le produit peut s'enflammer facilement au contact d'une source d'energie (flamme, etincelle, chaleur).", "exemples": "Ethanol, Cyclohexane, Acetone.", "img": "SGH02.png", "substance_nom": "Ethanol", "img_exemple": "pot_ethanol.png"},
        {"nom": "SGH03 - Comburant", "desc": "Peut provoquer ou aggraver un incendie en fournissant de l'oxygene lors d'une reaction.", "exemples": "Permanganate de potassium, Oxygene pur.", "img": "SGH03.png", "substance_nom": "Permanganate", "img_exemple": "pot_permanganate_de_potassium.png"},
        {"nom": "SGH04 - Gaz sous pression", "desc": "Contenu dans un recipient sous haute pression, peut exploser sous l'effet de la chaleur ou provoquer des gelures.", "exemples": "Bouteilles de gaz comprime, Azote liquide.", "img": "SGH04.png", "substance_nom": "Azote liquide", "img_exemple": "pot_azote_liquide.png"},
        {"nom": "SGH05 - Corrosif", "desc": "Attaque et ronge severement les tissus vivants (peau, yeux) ainsi que les metaux en cas de contact.", "exemples": "Acide chlorhydrique, Hydroxide de sodium.", "img": "SGH05.png", "substance_nom": "Acide chlorhydrique", "img_exemple": "pot_acide_chlorhydrique.png"},
        {"nom": "SGH06 - Toxique aigu", "desc": "Empoisonne rapidement et gravement l'organisme meme a faible dose (par inhalation, ingestion ou contact).", "exemples": "Methanol, Cyanure.", "img": "SGH06.png", "substance_nom": "Methanol", "img_exemple": "pot_methanol.png"},
        {"nom": "SGH07 - Toxique, Irritant", "desc": "Provoque des irritations de la peau, des yeux ou des voies respiratoires. Peut causer des somnolences.", "exemples": "Acide ethanoique, Solutions diluees.", "img": "SGH07.png", "substance_nom": "Acide ethanoique", "img_exemple": "pot_acide_ethanoique.png"},
        {"nom": "SGH08 - Danger pour la sante", "desc": "Risques graves, chroniques ou differes sur la sante (cancerogene, mutagene, toxique pour la reproduction ou les organes).", "exemples": "Cyclohexane (par aspiration), Phenolphtaleine.", "img": "SGH08.png", "substance_nom": "Cyclohexane", "img_exemple": "pot_cyclohexane.png"},
        {"nom": "SGH09 - Danger pour l'environnement", "desc": "Provoque des effets nefastes et durables sur les ecosystemes aquatiques (poissons, algues).", "exemples": "Sulfate de cuivre, Nitrate d'silver.", "img": "SGH09.png", "substance_nom": "Sulfate de cuivre", "img_exemple": "pot_sulfate_de_cuivre_pentahydrate.png"}
    ]


# =====================================================================
# MORCEAU 2 : FONCTION DE GENERATION DU QUIZ (APRES LES BANQUES DE DONNEES)
# =====================================================================
def preparer_quiz():
    liste_fusionnee = []
    
    # 1. Integration de vos 32 materiels avec conversion vers vos fichiers .jpg
    if "banque_questions" in globals() or hasattr(st.session_state, "banque_questions"):
        # On recupere la liste globale definie precdemment
        liste_mat = banque_questions if "banque_questions" in globals() else st.session_state.banque_questions
        for mat in liste_mat:
            liste_usages = mat.get("usages", [])
            usage_texte = random.choice(liste_usages) if isinstance(liste_usages, list) and len(liste_usages) > 0 else "Usage non specifie"
            
            nom_brut = mat.get("nom", "")
            
            # Liens exacts avec vos fichiers reels en .jpg (vus sur votre bureau)
            if "fiole jaugée" in nom_brut.lower():
                nom_fichier_img = "fiole jaugée.jpg"
            elif "bécher" in nom_brut.lower():
                nom_fichier_img = "becher.jpg"
            elif "erlenmeyer" in nom_brut.lower():
                nom_fichier_img = "erlenmeyer.jpg"
            elif "pipette jaugée" in nom_brut.lower():
                nom_fichier_img = "pip jaug.jpg"
            elif "burette" in nom_brut.lower():
                nom_fichier_img = "burette.jpg"
            elif "propipette" in nom_brut.lower():
                nom_fichier_img = "propipette.jpg"
            elif "pissette" in nom_brut.lower():
                nom_fichier_img = "pissette.jpg"
            elif "ballon à fond rond" in nom_brut.lower():
                nom_fichier_img = "ballon à fond rond.jpg"
            elif "ballon à fond plat" in nom_brut.lower():
                nom_fichier_img = "ballon à fond plat.jpg"
            elif "ph-mètre" in nom_brut.lower():
                nom_fichier_img = "ph metre.jpg"
            elif "papier ph" in nom_brut.lower():
                nom_fichier_img = "papier ph.jpg"
            elif "éprouvette graduée" in nom_brut.lower():
                nom_fichier_img = "éprouvette_graduée.jpg"
            elif "tube à essai" in nom_brut.lower():
                nom_fichier_img = "tube à essais.jpg"
            elif "balance de précision" in nom_brut.lower():
                nom_fichier_img = "blance de precision.jpg"
            elif "thermomètre" in nom_brut.lower():
                nom_fichier_img = "thermometre.jpg"
            elif "multimètre" in nom_brut.lower():
                nom_fichier_img = "multimetre.jpg"
            elif "tube en u" in nom_brut.lower():
                nom_fichier_img = "tube en U.jpg"
            elif "agitateur en verre" in nom_brut.lower():
                nom_fichier_img = "agitateur en verre.jpg"
            elif "entonnoir à liquide" in nom_brut.lower():
                nom_fichier_img = "entonnoir à liquide.jpg"
            elif "agitateur magnétique" in nom_brut.lower():
                nom_fichier_img = "agitateur magnetique et barreau aimanté.jpg"
            elif "ampoule à décanter" in nom_brut.lower():
                nom_fichier_img = "ampoule à decanter.jpg"
            elif "ballon bicolore" in nom_brut.lower():
                nom_fichier_img = "ballon bicolore.jpg"
            elif "cristallisoir" in nom_brut.lower():
                nom_fichier_img = "cristallisoir.jpg"
            elif "verre de montre" in nom_brut.lower():
                nom_fichier_img = "verre a montre.jpg"
            elif "verre à pied" in nom_brut.lower():
                nom_fichier_img = "verre a pied.jpg"
            else:
                nom_nettoye = nom_brut.lower().replace("é", "e").replace("è", "e").replace("à", "a")
                nom_fichier_img = f"{nom_nettoye}.jpg"
            
            liste_fusionnee.append({
                "nom": nom_brut,
                "img": nom_fichier_img,
                "usage": usage_texte
            })

    # 2. Integration de vos 9 pictogrammes SGH (qui sont en .png)
    liste_sgh = pictogrammes_sgh if "pictogrammes_sgh" in globals() else []
    for picto in liste_sgh:
        liste_fusionnee.append({
            "nom": picto.get("nom", ""),
            "img": picto.get("img", ""), # Fichiers du type SGH01.png
            "usage": picto.get("desc", "Description non specifiee")
        })

    # 3. Selection aleatoire de 20 questions
    random.shuffle(liste_fusionnee)
    st.session_state.quiz_questions = liste_fusionnee[:20]
    st.session_state.quiz_reponses = {}
    st.session_state.quiz_valide = False

# Securite d'appel automatique au demarrage
if "quiz_questions" not in st.session_state or not st.session_state.quiz_questions:
    preparer_quiz()
    
# Affichage de l'en-tete fixe
st.markdown("### TP Verrerie et Securite")
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Nom :** {st.session_state.nom.upper() if st.session_state.nom else 'Non renseigne'}")
    with col2:
        st.markdown(f"**Prenom :** {st.session_state.prenom.capitalize() if st.session_state.prenom else 'Non renseigne'}")
    with col3:
        st.markdown(f"**Classe :** {st.session_state.classe if st.session_state.classe else 'Non renseigne'}")
    with col4:
        st.markdown(f"**Date et heure :** {st.session_state.date_heure}")

# Gestion de la securite anti-triche : blocage des onglets de révision
if st.session_state.mode_examen:
    st.sidebar.warning("Mode Examen Actif ! Les onglets de revision sont verrouilles.")
    onglets_autorises = ["Identification", "Evaluation Officielle"]
else:
    onglets_autorises = ["Identification", "Armoire de Materiel & Reactifs", "Securite et Pictogrammes", "Evaluation Officielle"]

onglet_actif = st.radio("Menu du Laboratoire", onglets_autorises, horizontal=True)
if onglet_actif == "Identification":
    st.subheader("Identification de l'Eleve")
    
    with st.form("form_identite"):
        nom_input = st.text_input("Nom :", value=st.session_state.nom, disabled=st.session_state.identifie)
        prenom_input = st.text_input("Prenom :", value=st.session_state.prenom, disabled=st.session_state.identifie)
        classe_input = st.text_input("Classe :", value=st.session_state.classe, disabled=st.session_state.identifie)
        
        btn_soumettre = st.form_submit_button("Valider et verrouiller mon profil", disabled=st.session_state.identifie)
        
        if btn_soumettre:
            if nom_input.strip() and prenom_input.strip() and classe_input.strip():
                st.session_state.nom = nom_input
                st.session_state.prenom = prenom_input
                st.session_state.classe = classe_input
                st.session_state.identifie = True
                st.experimental_rerun()
            else:
                st.error("Veuillez completer entierement vos donnees avant de valider.")

    if st.session_state.identifie:
        st.success("Profil enregistre et securise pour l'epreuve.")
        if st.button("Modifier mon profil (Entrainement uniquement)"):
            st.session_state.identifie = False
            sst.experimental_rerun()
            t.session_state.mode_examen = False
            
elif onglet_actif == "Armoire de Materiel & Reactifs":
    st.subheader("Armoire du Laboratoire")
    
    recherche = st.text_input("Rechercher un materiel, une formule ou un usage :").lower()
    col_gauche, col_droite = st.columns(2)
    
    with col_gauche:
        st.markdown("***Verrerie & Appareils de Mesure***")
        for mat in banque_questions:
            # Filtrage de sécurité pour la barre de recherche
            nom_mat = mat.get("nom", "").lower()
            usages_list = mat.get("usages", [])
            usages_joints = " ".join(usages_list).lower() if isinstance(usages_list, list) else ""
            
            if recherche in nom_mat or recherche in usages_joints:
                with st.container():
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"***{mat.get('nom', 'Inconnu')}*** ({mat.get('categorie', 'Verrerie')})")
                        # Affichage propre de la liste des usages
                        if isinstance(usages_list, list):
                            for u in usages_list:
                                st.caption(f"- {u}")
                        else:
                            st.caption(f"- {usages_list}")
                        st.caption("Instrument de precision" if mat.get("precis", False) else "Mesure indicative")
                    
                    with c2:
                        nom_brut_mat = mat.get("nom", "")
                        
                        # TABLE DE CORRESPONDANCE STRICTE AVEC VOS FICHIERS REELS .JPG
                        if "fiole jaugée" in nom_brut_mat.lower():
                            nom_fichier_img = "fiole jaugée.jpg"
                        elif "bécher" in nom_brut_mat.lower():
                            nom_fichier_img = "bécher.jpg"
                        elif "erlenmeyer" in nom_brut_mat.lower():
                            nom_fichier_img = "erlenmeyer.jpg"
                        elif "pipette jaugée" in nom_brut_mat.lower():
                            nom_fichier_img = "pip jaug.jpg"
                        elif "pipette graduée" in nom_brut_mat.lower():
                            nom_fichier_img = "pipette graduée.jpg"
                        elif "burette" in nom_brut_mat.lower():
                            nom_fichier_img = "burette.jpg"
                        elif "propipette" in nom_brut_mat.lower():
                            nom_fichier_img = "propipette.jpg"
                        elif "pissette" in nom_brut_mat.lower():
                            nom_fichier_img = "pissette.jpg"
                        elif "ballon à fond rond" in nom_brut_mat.lower():
                            nom_fichier_img = "ballon à fond rond.jpg"
                        elif "ballon à fond plat" in nom_brut_mat.lower():
                            nom_fichier_img = "ballon à fond plat.jpg"
                        elif "ph-mètre" in nom_brut_mat.lower():
                            nom_fichier_img = "ph metre.jpg"
                        elif "papier ph" in nom_brut_mat.lower():
                            nom_fichier_img = "papier pH.jpg"
                        elif "éprouvette graduée" in nom_brut_mat.lower():
                            nom_fichier_img = "éprouvette_graduée.jpg"
                        elif "tube à essai" in nom_brut_mat.lower():
                            nom_fichier_img = "tube à essais.jpg"
                        elif "balance de précision" in nom_brut_mat.lower():
                            nom_fichier_img = "blance de precision.jpg"
                        elif "thermomètre" in nom_brut_mat.lower():
                            nom_fichier_img = "thermometre.jpg"
                        elif "multimètre" in nom_brut_mat.lower():
                            nom_fichier_img = "multimetre.jpg"
                        elif "tube en u" in nom_brut_mat.lower():
                            nom_fichier_img = "tube en U.jpg"
                        elif "agitateur en verre" in nom_brut_mat.lower():
                            nom_fichier_img = "agitateur en verre.jpg"
                        elif "entonnoir à liquide" in nom_brut_mat.lower():
                            nom_fichier_img = "entonnoir à liquide.jpg"
                        elif "agitateur magnétique" in nom_brut_mat.lower():
                            nom_fichier_img = "agitateur magnetique et barreau aimanté.jpg"
                        elif "ampoule à décanter" in nom_brut_mat.lower():
                            nom_fichier_img = "ampoule à decanter.jpg"
                        elif "ballon bicol" in nom_brut_mat.lower():
                            nom_fichier_img = "ballon bicol.jpg"
                        elif "cristallisoir" in nom_brut_mat.lower():
                            nom_fichier_img = "cristallisoir.jpg"
                        elif "verre de montre" in nom_brut_mat.lower():
                            nom_fichier_img = "verre a montre.jpg"
                        elif "verre à pied" in nom_brut_mat.lower():
                            nom_fichier_img = "verre a pied.jpg"
                        else:
                            nom_nettoye = nom_brut_mat.lower().replace("é", "e").replace("è", "e").replace("à", "a")
                            nom_fichier_img = f"{nom_nettoye}.jpg"

                        try:
                            st.image(nom_fichier_img, width=250)
                        except:
                            st.caption(f"[{nom_fichier_img}]")
    with col_droite:
        st.markdown("***Reserve des Reactifs Chimiques***")
        for pdt in reactifs:
            nom_pdt = pdt.get("nom", "").lower()
            formule_pdt = pdt.get("formule", "").lower()
            danger_pdt = pdt.get("danger", "").lower()
            
            if recherche in nom_pdt or recherche in formule_pdt or recherche in danger_pdt:
                with st.container():
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"***{pdt.get('nom', 'Inconnu')}*** — `[{pdt.get('formule', '')}]`")
                        st.caption(f"Famille : {pdt.get('famille', 'Non specifiee')} | Etat : {pdt.get('etat', 'Non specifie')}")
                        st.markdown(f"<font color='red'>Danger : {pdt.get('danger', 'Se referer aux pictogrammes associes')}</font>", unsafe_allow_html=True)
                    
                    with c2:
                        nom_brut_pdt = pdt.get("nom", "")
                        
                        # CORRESPONDANCE STRICTE AVEC VOS FICHIERS REACTIFS EN .JPG
                        if "chlorhydrique" in nom_brut_pdt.lower():
                            nom_fichier_pot = "acide chlorhydrique.jpg"
                        elif "ethanoique" in nom_brut_pdt.lower():
                            nom_fichier_pot = "acide ethanoique.jpg"
                        elif "hydroxyde" in nom_brut_pdt.lower():
                            nom_fichier_pot = "hydroxyde de sodium.jpg"
                        elif "ammoniaque" in nom_brut_pdt.lower():
                            nom_fichier_pot = "ammoniaque.jpg"
                        elif "permanganate" in nom_brut_pdt.lower():
                            nom_fichier_pot = "permanganate de potassium.jpg"
                        elif "eau oxygenee" in nom_brut_pdt.lower() or "eau oxygénée" in nom_brut_pdt.lower():
                            nom_fichier_pot = "eau oxygenee.jpg"
                        elif "thiosulfate" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Thiosulfate de sodium.jpg"
                        elif "bromothymol" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Bleu de bromothymol (BBT).jpg"
                        elif "nitrate" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Nitrate d'argent.jpg"
                        elif "fehling" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Liqueur de Fehling.jpg"
                        elif "lugol" in nom_brut_pdt.lower() or "iodée" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Eau iodée (Lugol).jpg"
                        elif "tampon 4" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Solution tampon pH 4,00.jpg"
                        elif "tampon 7" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Solution tampon pH 7,00.jpg"
                        elif "cuivre" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Sulfate de cuivre pentahydrate.jpg"
                        elif "fer ii" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Sulfate de fer II.jpg"
                        elif "zinc" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Sulfate de zinc..jpg"
                        elif "fer iii" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Chlorure de fer III.jpg"
                        elif "ethanol" in nom_brut_pdt.lower() or "éthanol" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Éthanol.jpg"
                        elif "cyclohexane" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Cyclohexane.jpg"
                        elif "eau distillee" in nom_brut_pdt.lower() or "eau distillée" in nom_brut_pdt.lower():
                            nom_fichier_pot = "Eau distillée.jpg"
                        else:
                            nom_fichier_pot = f"{nom_brut_pdt}.jpg"

                        try:
                            st.image(nom_fichier_pot, width=250)
                        except:
                            st.caption(f"[{nom_fichier_pot}]")
                                
elif onglet_actif == "Securite et Pictogrammes":
    st.subheader("Classification des Dangers Chimiques (Systeme SGH)")
    
    st.markdown("**1. Signification des Pictogrammes de Danger**")
    for picto in pictogrammes_sgh:
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                # Calcul du chemin pour l'icone SGH (ex: images/SGH01.png)
                chemin_icone = obtenir_chemin_absolu(picto["img"])
                try: 
                    st.image(chemin_icone, width=55)
                except: 
                    st.caption(f"[{picto['img']}]")
            with c2:
                st.markdown(f"**{picto['nom']}**")
                st.write(picto["desc"])
                st.caption(f"Exemples : {picto.get('exemples', '')}")
            with c3:
                st.caption(picto["substance_nom"])
                # Calcul du chemin pour le flacon d'illustration (ex: images/pot_ethanol.png)
                chemin_flacon = obtenir_chemin_absolu(picto["img_exemple"])
                try: 
                    st.image(chemin_flacon, width=50)
                except: 
                    st.caption(f"[{picto['img_exemple']}]")

            
elif onglet_actif == "Evaluation Officielle":
    st.subheader("Evaluation Individuelle Officielle")
    
    # 1. Gestion et activation du Mode Examen
    if not st.session_state.mode_examen:
        if st.checkbox("Activer le Mode Examen Officiel (Verrouille les onglets de revision)", value=False):
            if not st.session_state.identifie:
                st.error("Action impossible ! Veuillez renseigner votre profil dans l'onglet 'Identification' d'abord.")
            else:
                st.session_state.mode_examen = True
                preparer_quiz()
                st.experimental_rerun()
    else:
        st.info("Epreuve officielle en cours. Consultation des onglets de cours suspendue.")

    st.markdown("---")
    
    # 2. Generation de la liste de tous les choix possibles pour les menus deroulants
    noms_materiels = [item["nom"] for item in banque_questions]
    noms_pictogrammes = [p["nom"] for p in pictogrammes_sgh]
    options_globales = sorted(list(set(noms_materiels + noms_pictogrammes)))
    
    # 3. Boucle de rendu graphique des 20 questions selectionnees
    for idx, q in enumerate(st.session_state.quiz_questions):
        with st.container():
            col_q, col_r = st.columns(2)
            with col_q:
                st.markdown(f"***Question {idx+1} / 20***")
                nom_fichier_image_q = q.get("img", "")
                
                # Alternance : Index pair = Visuel (jpg/png), Index impair = Usage textuel
                if idx % 2 == 0:
                    st.write("Quel est le nom exact de cet element du laboratoire ?")
                    try:
                        st.image(nom_fichier_image_q, width=75)
                    except:
                        st.caption(f"[{nom_fichier_image_q}]")
                else:
                    st.write("Quel element correspond exactement a cette description ou cet usage ?")
                    st.info(f"{q.get('usage', 'Usage non specifie')}")
            
            with col_r:
                cle_unique = f"q_{idx}"
                reponse_precedente = st.session_state.quiz_reponses.get(cle_unique, "")
                
                choix = st.selectbox(
                    "Votre reponse :",
                    [""] + options_globales,
                    key=cle_unique,
                    index=options_globales.index(reponse_precedente) + 1 if reponse_precedente in options_globales else 0,
                    disabled=st.session_state.quiz_valide
                )
                st.session_state.quiz_reponses[cle_unique] = choix

    st.markdown("---")
    
    # 4. Validation de la copie et calcul de la note finale
    if not st.session_state.quiz_valide:
        if st.button("Valider et rendre ma copie definitive", type="primary"):
            if not st.session_state.identifie:
                st.error("Veuillez renseigner votre identite dans le premier onglet avant de soumettre.")
            else:
                note = 0
                for i, question in enumerate(st.session_state.quiz_questions):
                    reponse_eleve = st.session_state.quiz_reponses.get(f"q_{i}", "")
                    reponse_attendue = question.get("nom", "")
                    
                    if reponse_eleve.strip().lower() == reponse_attendue.strip().lower():
                        note += 1
                
                st.session_state.score = note
                st.session_state.quiz_valide = True
                st.experimental_rerun()
    else:
        st.success(f"Copie enregistree ! Note finale pour {st.session_state.nom.upper()} {st.session_state.prenom.capitalize()} : {st.session_state.score} / 20")
        # Rapport texte telechargeable pour l'enseignant
        texte_rapport = f"RAPPORT NOTE\nEleve : {st.session_state.nom.upper()} {st.session_state.prenom.capitalize()}\nClasse : {st.session_state.classe}\nDate : {st.session_state.date_heure}\nScore : {st.session_state.score} / 20"
        st.download_button(
            label="Telecharger le Rapport de Note (Professeur)",
            data=texte_rapport,
            file_name=f"Note_{st.session_state.nom.upper()}.txt",
            mime="text/plain"
        )
    # --- BLOC DE GENERATION ET EXPORTATION DU RAPPORT HTML ---
    if st.session_state.quiz_valide:
        score_final = st.session_state.score
        total_q = len(st.session_state.quiz_questions)
        note_sur_20 = (score_final / total_q) * 20 if total_q > 0 else 0.0

        lignes_html_tableau = ""
        nom_eleve_majuscule = st.session_state.nom.upper()
        prenom_eleve_propre = st.session_state.prenom.capitalize()

        # Boucle de generation des lignes du tableau HTML
        for idx, question in enumerate(st.session_state.quiz_questions):
            cle_q = f"q_{idx}"
            reponse_saisie = st.session_state.quiz_reponses.get(cle_q, "Aucune reponse")
            if reponse_saisie == "":
                reponse_saisie = "Aucune reponse"
                
            valeur_attendue = question["nom"]
            
            # Verification de la validite du texte
            if reponse_saisie.strip().lower() == valeur_attendue.strip().lower():
                statut_badge = '<span class="status-pass">CORRECT</span>'
            else:
                statut_badge = '<span class="status-fail">INCORRECT</span>'

            lignes_html_tableau += f"""
            <tr>
                <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
                <td>Question {idx+1} - Identification liee a : {question.get('usage', 'Visuel graphique')}</td>
                <td style="color: #64748b;">{reponse_saisie}</td>
                <td style="font-weight: 500; color: #1e293b;">{valeur_attendue}</td>
                <td style="text-align: center;">{statut_badge}</td>
            </tr>
            """

        # Construction du document HTML unifie
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Evaluation Chimie Lycee</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: { "#16a34a" if score_final>=(total_q/2) else "#dc2626" }; }}
        .score-box .sub {{ font-size: 11px; color: #64748b; }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px 14px; font-size: 13px; font-weight: bold; }}
        td {{ padding: 14px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #dcfce7; color: #16a34a; border-radius: 4px; }}
        .status-fail {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #fee2e2; color: #ef4444; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">
            <div class="title">NOTE FINALE</div>
            <div class="value">{score_final} / {total_q}</div>
            <div class="sub">({note_sur_20:.2f} / 20)</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Eleve :</strong> {nom_eleve_majuscule} {prenom_eleve_propre}<br>
            <strong>Classe :</strong> {st.session_state.classe}<br>
            <strong>Evaluation type QCM :</strong> Verrerie et Securite SGH
        </div>
    </div>
    <div class="section-title">Resultats et correction du QCM</div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">N°</th>
                <th style="width: 45%;">Intitule de la question posee</th>
                <th style="width: 19%;">Votre reponse saisie</th>
                <th style="width: 19%;">Valeur attendue / Correction</th>
                <th style="width: 12%; text-align: center;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html_tableau}
        </tbody>
    </table>
</body>
</html>
"""

        # Nettoyage de securite pour le nom du fichier de sortie
        nom_fichier_brut = f"Evaluation_Verrerie_Securite_{nom_eleve_majuscule}_{prenom_eleve_propre}.html"
        for caractere in [" ", "*", "?", ":", "/", "\\", "<", ">", "|", '"']:
            nom_fichier_brut = nom_fichier_brut.replace(caractere, "_")

        # Bouton natif de telechargement Streamlit
        st.markdown("### Enregistrement des notes")
        st.download_button(
            label="Telecharger le rapport officiel HTML",
            data=html_content,
            file_name=nom_fichier_brut,
            mime="text/html"
        )

