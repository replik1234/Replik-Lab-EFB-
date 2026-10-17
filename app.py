import streamlit as st
import hashlib
import datetime
import pandas as pd
import time

# ==============================================================================
# CONFIGURATION DE LA PAGE & IDENTITÉ VISUELLE DU CABINET REPLIK
# ==============================================================================
st.set_page_config(
    page_title="Cabinet Replik | Protection & Défense Réputationnelle",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .replik-header {
        background: linear-gradient(135deg, #0f1226 0%, #1e1b4b 65%, #e61e6e 100%);
        padding: 22px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .badge-role {
        background-color: rgba(255, 255, 255, 0.18);
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .cert-box {
        font-family: 'Courier New', monospace;
        background-color: #0f1226;
        color: #10b981;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #e61e6e;
        font-size: 0.88em;
        line-height: 1.6;
    }
    .step-card-done {
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        border-top: 4px solid #10b981;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }
    .step-card-wait {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #94a3b8;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }
    .step-card-active {
        background-color: #fdf2f8;
        border: 1px solid #e61e6e;
        border-top: 4px solid #e61e6e;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# DOSSIERS TYPES PRÉ-CONFIGURÉS (POUR FLUIDIFIER LA DÉMONSTRATION)
# ==============================================================================
DOSSIERS_TYPES = [
    {
        "id": "RPK-2026-01",
        "label": "Cas 1 — Montage Deepfake à caractère sexuel (Particulier)",
        "client": "Clara M.",
        "profil": "Particulier (Sans abonnement)",
        "formule": "R3 Preuve authentique (320 € HT) — Constat Commissaire 24h/24 inclus",
        "plateforme": "Telegram & Site web tiers",
        "url": "https://t.me/channel_archive_fr/98234",
        "jours_pub": 3,
        "auteur_connu": False,
        "urgence_nuit": True,
        "faits": "Diffusion sans consentement d'un montage photo/vidéo hypertruqué (deepfake) utilisant le visage de la cliente, associé à son identité réelle et au nom de son établissement.",
        "ia_qualification": "Montage à caractère sexuel sans consentement (Art. 226-8-1 du Code pénal : 2 ans d'emprisonnement et 60 000 € d'amende, porté à 3 ans et 75 000 € en ligne).",
        "ia_actions": "Empreinte probatoire SHA-256 en local, pré-remplissage du signalement prioritaire DSA (Art. 16) et PHAROS, lancement de la veille anti-republication sur 7 jours.",
        "avocat_arbitrage": "Validation du constat par commissaire de justice d'astreinte 24h/24 (R3) et dépôt d'une plainte pénale auprès du Procureur (J2B) avec demande de réquisition IP.",
        "suite_justice": "J2B Plainte au procureur (700 à 1 000 € HT — Constat R3 inclus)"
    },
    {
        "id": "RPK-2026-02",
        "label": "Cas 2 — Raid coordonné de faux avis Google (Entreprise)",
        "client": "SAS Clinique Lumière (Dr. Sophie Martin)",
        "profil": "Abonné P3 Entreprise — Niveau 2 Preuve (299 € HT/mois)",
        "formule": "R4 Retrait judiciaire (1 700 € HT avec remise abonné -15%)",
        "plateforme": "Google Maps (Fiche Établissement)",
        "url": "https://maps.google.com/reviews/clinique_lumiere_id88",
        "jours_pub": 14,
        "auteur_connu": False,
        "urgence_nuit": False,
        "faits": "Publication coordonnée de 12 avis 1 étoile en deux heures : 'Clinique insalubre, utilisation de produits périmés dangereux, la directrice falsifie ses diplômes !'",
        "ia_qualification": "Dénigrement commercial fautif (Art. 1240 du Code civil) et Diffamation publique (Art. 29 al. 1 et 32 de la Loi du 29 juillet 1881).",
        "ia_actions": "Détection de l'anomalie temporelle (raid), capture certifiée R2 (incluse dans l'abonnement P3 Niveau 2), préparation de la mise en demeure Google Ireland.",
        "avocat_arbitrage": "Choix stratégique du fondement : privilégier le dénigrement commercial (Art. 1240 C. civ.) sur la qualité des soins et assigner en référé sous astreinte.",
        "suite_justice": "J1 Justice civile — Action en réparation du préjudice financier (2 800 à 5 150 € HT)"
    },
    {
        "id": "RPK-2026-03",
        "label": "Cas 3 — Voix clonée par IA et faux profil d'influenceur (Personnalité)",
        "client": "Lucas 'SkyVibe' (Créateur de contenu)",
        "profil": "Abonné P2 Personnalité — Niveau 3 Justice (449 € HT/mois)",
        "formule": "Inclus dans l'abonnement P2 Niveau 3 (Constat & Retrait)",
        "plateforme": "TikTok & Instagram Reels",
        "url": "https://tiktok.com/@skyvibe_invest_officiel/video/778899",
        "jours_pub": 1,
        "auteur_connu": False,
        "urgence_nuit": True,
        "faits": "Vidéo utilisant un clone vocal généré par IA et l'image du client pour promouvoir une escroquerie financière auprès de sa communauté.",
        "ia_qualification": "Atteinte à la représentation de la personne par hypertrucage (Art. 226-8 et 226-8-1 C. pén.) et Usurpation d'identité numérique (Art. 226-4-1 C. pén.).",
        "ia_actions": "Alerte remontée par l'IA de veille, figeage probatoire local, préparation des notifications d'urgence Meta et TikTok.",
        "avocat_arbitrage": "Coordination confidentielle avec l'agent de la personnalité (prévention de l'effet Streisand), mobilisation d'un constat R3 inclus dans le forfait P2 Niveau 3.",
        "suite_justice": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "RPK-2026-04",
        "label": "Cas 4 — Diffusion de clichés intimes par un ex-conjoint identifié (Revenge Porn)",
        "client": "Sarah L.",
        "profil": "Particulier (Sans abonnement)",
        "formule": "R3 Preuve authentique (320 € HT) + Urgence Nuit/WE (+150 € HT)",
        "plateforme": "Instagram & Messagerie",
        "url": "https://instagram.com/p/post_id_88219",
        "jours_pub": 2,
        "auteur_connu": True,
        "urgence_nuit": True,
        "faits": "Mise en ligne par l'ex-conjoint (formellement identifié) de photographies intimes sans consentement, avec identification des proches de la victime.",
        "ia_qualification": "Diffusion non consentie d'images à caractère sexuel (Art. 226-2-1 du Code pénal : 2 ans d'emprisonnement et 60 000 € d'amende).",
        "ia_actions": "Traitement 100 % en IA locale (aucune exposition externe des images intimes), empreinte SHA-256, préparation de la notification de retrait immédiat.",
        "avocat_arbitrage": "L'auteur étant identifié, l'avocat déclenche le constat de commissaire d'astreinte (R3) et prépare une Citation Directe (J2A) pour audience correctionnelle rapide.",
        "suite_justice": "J2A Citation directe devant le Tribunal correctionnel (2 700 à 4 200 € HT)"
    },
    {
        "id": "RPK-2026-05",
        "label": "Cas 5 — Cyberharcèlement en meute et divulgation d'adresse (Doxxing)",
        "client": "Mehdi K.",
        "profil": "Abonné P1 Particulier — Niveau 2 Preuve (39 € HT/mois)",
        "formule": "Inclus dans l'abonnement P1 Niveau 2 (6 signalements & captures R2 inclus)",
        "plateforme": "X (Twitter)",
        "url": "https://x.com/thread_attaque/status/189273645",
        "jours_pub": 5,
        "auteur_connu": False,
        "urgence_nuit": False,
        "faits": "Publication de l'adresse personnelle et du numéro de téléphone du client accompagnée d'appels à venir l'intimider à son domicile.",
        "ia_qualification": "Mise en danger par révélation d'informations personnelles / Doxxing (Art. 223-1-1 C. pén.) et Cyberharcèlement (Art. 222-33-2-2 C. pén.).",
        "ia_actions": "Agrégation automatique des messages du raid dans un rapport horodaté unique, préparation des signalements groupés.",
        "avocat_arbitrage": "Qualification du péril imminent et saisine prioritaire du Pôle national de lutte contre la haine en ligne.",
        "suite_justice": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "RPK-2026-06",
        "label": "Cas 6 — Post LinkedIn diffamatoire d'un concurrent identifié (Dirigeant)",
        "client": "Jean-Marc V. (Dirigeant de société)",
        "profil": "Abonné P3 Entreprise — Niveau 1 Veille (229 € HT/mois)",
        "formule": "R2 Preuve horodatée (15 € unité tarif abonné) + Constat R3 (250 €)",
        "plateforme": "LinkedIn",
        "url": "https://linkedin.com/posts/concurrent_99283",
        "jours_pub": 45,
        "auteur_connu": True,
        "urgence_nuit": False,
        "faits": "Publication publique d'un concurrent accusant nommément le dirigeant de détournement de fonds sociaux et de fraude fiscale.",
        "ia_qualification": "Diffamation publique envers une personne physique (Art. 29 al. 1 et 32 de la Loi du 29 juillet 1881).",
        "ia_actions": "Vérification du délai de prescription de 3 mois (45 jours restants), figeage de l'URL et extraction des informations de l'auteur.",
        "avocat_arbitrage": "Formalisme strict de la Loi de 1881 : rédaction par l'avocat d'une plainte avec constitution de partie civile (J2C) pour interrompre valablement la prescription.",
        "suite_justice": "J2C Partie civile directe devant le doyen des juges d'instruction (3 800 à 7 200 € HT)"
    },
    {
        "id": "RPK-2026-07",
        "label": "Cas 7 — Faux compte usurpant l'identité d'une élue locale",
        "client": "Hélène R.",
        "profil": "Abonné P2 Personnalité — Niveau 2 Preuve (349 € HT/mois)",
        "formule": "R4 Retrait judiciaire (1 700 € HT avec remise abonné -15%)",
        "plateforme": "Facebook & TikTok",
        "url": "https://facebook.com/profile.php?id=1000998877",
        "jours_pub": 4,
        "auteur_connu": False,
        "urgence_nuit": False,
        "faits": "Création d'une page imitant le compte officiel de la cliente et diffusant de fausses prises de position publiques.",
        "ia_qualification": "Usurpation d'identité numérique (Art. 226-4-1 du Code pénal).",
        "ia_actions": "Détection par veille d'image, capture certifiée R2 incluse dans le forfait, préparation de la notification Meta.",
        "avocat_arbitrage": "Rédaction de la mise en demeure d'avocat et préparation de l'assignation en référé aux fins de suppression sous astreinte.",
        "suite_justice": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "RPK-2026-08",
        "label": "Cas 8 — Chantage à la vidéo intime (Sextorsion en cours)",
        "client": "Thomas B.",
        "profil": "Particulier (Sans abonnement)",
        "formule": "R2 Preuve horodatée (150 € HT) + Urgence Nuit/WE (+75 € HT)",
        "plateforme": "Instagram & Discord",
        "url": "https://discord.com/channels/9988776655",
        "jours_pub": 1,
        "auteur_connu": False,
        "urgence_nuit": True,
        "faits": "Menace imminente de diffuser un enregistrement intime à la liste de contacts de la victime à défaut d'un virement immédiat de 800 €.",
        "ia_qualification": "Chantage (Art. 312-10 du Code pénal : 5 ans d'emprisonnement et 75 000 € d'amende) et tentative d'extorsion.",
        "ia_actions": "Figeage immédiat des captures d'écran et identifiants des comptes, envoi des consignes conservatoires d'urgence au client.",
        "avocat_arbitrage": "Prise en charge immédiate par l'avocat de permanence 24h/24, demande de gel des comptes auprès des plateformes et dépôt de plainte.",
        "suite_justice": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "RPK-2026-09",
        "label": "Cas 9 — Article diffamatoire publié il y a 105 jours (Prescription 3 mois dépassée)",
        "client": "SARL Atelier Architecture Horizon",
        "profil": "Particulier / Entreprise (Sans abonnement)",
        "formule": "R2 Preuve horodatée (150 € HT)",
        "plateforme": "Blog professionnel",
        "url": "https://blog-urbanisme-info.fr/atelier-horizon",
        "jours_pub": 105,
        "auteur_connu": True,
        "urgence_nuit": False,
        "faits": "Publication il y a plus de trois mois d'un billet accusant l'entreprise de livrer des chantiers non conformes et dangereux.",
        "ia_qualification": "ALERTE PRESCRIPTION : Délai de 3 mois (Art. 65 Loi du 29 juillet 1881) expiré (105 jours écoulés). Irrecevabilité d'une action en diffamation.",
        "ia_actions": "Détection automatique du dépassement du délai de 90 jours et verrouillage préventif des modèles d'actes fondés sur la Loi de 1881.",
        "avocat_arbitrage": "Plus-value décisive de l'avocat : réorientation de l'action sur le fondement du dénigrement commercial (Art. 1240 du Code civil, prescription de 5 ans) visant les prestations de la société.",
        "suite_justice": "J1 Justice civile sur le fondement de l'Art. 1240 C. civ. (2 800 à 5 150 € HT)"
    },
    {
        "id": "RPK-2026-10",
        "label": "Cas 10 — Harcèlement visant l'enfant mineur d'une cliente (Option Pack Proches)",
        "client": "Mme Claire D. (pour son fils mineur Lucas)",
        "profil": "Abonné P2 Personnalité + Option Pack Proches (39 € HT/mois)",
        "formule": "Inclus dans l'Option Pack Proches (Formule P2)",
        "plateforme": "TikTok & Snapchat",
        "url": "https://tiktok.com/@video_college_92/video/112233",
        "jours_pub": 2,
        "auteur_connu": True,
        "urgence_nuit": False,
        "faits": "Diffusion d'une vidéo humiliante visant un élève mineur, repartagée sur plusieurs comptes secondaires.",
        "ia_qualification": "Cyberharcèlement sur mineur (Art. 222-33-2-3 C. pén.) et atteinte au droit à l'image (Art. 226-1 C. pén.).",
        "ia_actions": "Identification de la vidéo source et de 4 comptes miroirs, horodatage certifié et préparation des notifications prioritaires protection des mineurs.",
        "avocat_arbitrage": "Validation de la notification d'urgence et mise en demeure des représentants légaux et de la plateforme.",
        "suite_justice": "J2B Plainte au procureur (700 à 1 000 € HT)"
    }
]

# Initialisation de la mémoire de l'application
if "active_case" not in st.session_state:
    d0 = DOSSIERS_TYPES[0]
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y à %H:%M:%S UTC")
    raw = f"{d0['id']}|{d0['client']}|{d0['url']}|{ts}"
    st.session_state.active_case = {
        **d0,
        "timestamp": ts,
        "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "statut_avocat": "EN ATTENTE DE VALIDATION AVOCAT",
        "acte_valide": False,
        "avocat_signataire": "Me. Associé de Permanence (Barreau de Paris)",
        "acte_final": ""
    }

# ==============================================================================
# BARRE LATÉRALE : GARANTIES DU CABINET REPLIK
# ==============================================================================
with st.sidebar:
    st.markdown("## 🛡️ CABINET REPLIK")
    st.caption("La rigueur juridique, à la vitesse d'Internet.")
    st.divider()
    
    st.markdown("### ⚡ Permanence 24h/24 & 7j/7")
    if st.session_state.active_case["acte_valide"]:
        st.success("🟢 **Dossier actif :** Validé et signé par l'avocat de permanence.")
    else:
        st.warning("🟠 **Dossier actif :** Pré-qualifié par l'IA locale — En attente de validation par l'avocat.")
        
    st.divider()
    st.markdown("### 🔒 Garanties Déontologiques")
    st.markdown("""
    - **Confidentialité absolue :** IA locale hébergée en France (0 donnée sensible envoyée à l'extérieur).
    - **Contrôle humain :** 100 % des actes sont vérifiés et signés par un avocat.
    - **Transparence :** Forfaits fixes connus d'avance, frais de tiers inclus.
    - **Protection durable :** 1 semaine de veille anti-republication dès la formule R1 et conservation des preuves 5 ans.
    """)

# ==============================================================================
# EN-TÊTE PRINCIPAL
# ==============================================================================
st.markdown("""
    <div class="replik-header">
        <span class="badge-role">CABINET D'AVOCATS EN DROIT DU NUMÉRIQUE & DE LA RÉPUTATION</span>
        <h1 style="margin:8px 0 4px 0; color:white;">CABINET REPLIK — Plus vite que la viralité.</h1>
        <p style="margin:0; opacity:0.9; font-size:1.02em;">
            L'IA détecte et prépare en temps réel. L'avocat décide, qualifie et agit 24h/24.
        </p>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# NAVIGATION : ÉCRAN 1 (CLIENT) vs ÉCRANS 2 & 3 (AVOCAT)
# ==============================================================================
tab_client, tab_avocat_dossier, tab_avocat_radar = st.tabs([
    "👤 ÉCRAN 1 : ESPACE CLIENT (Signaler & Suivre mon dossier)",
    "⚖️ ÉCRAN 2 : POSTE AVOCAT (Qualification IA, Prescription & Actes)",
    "📡 ÉCRAN 3 : SUPERVISION CABINET (Radar de Veille & Portefeuille)"
])

# ==============================================================================
# ÉCRAN 1 : INTERFACE 100 % CLIENT (DÉPÔT, ACCUSÉ HORODATÉ & SUIVI EN 5 ÉTAPES)
# ==============================================================================
with tab_client:
    col_c_head1, col_c_head2 = st.columns([2, 1])
    with col_c_head1:
        st.subheader("👤 Portail Client — Signaler une atteinte en ligne")
        st.write("Confiez-nous le retrait de votre contenu et la sauvegarde immédiate de vos preuves. Un avocat de permanence prend le relais 24h/24.")
    with col_c_head2:
        # Sélecteur discret pour pré-remplir le formulaire en 1 clic pendant la présentation
        choix_demo = st.selectbox(
            "⚡ Remplissage rapide (Cas types) :",
            [d["label"] for d in DOSSIERS_TYPES]
        )
        preset = next(d for d in DOSSIERS_TYPES if d["label"] == choix_demo)

    st.divider()
    
    col_form, col_suivi = st.columns([1.05, 1])
    
    # --- COLONNE GAUCHE : FORMULAIRE DE SIGNALEMENT CLIENT ---
    with col_form:
        st.markdown("#### 1. Décrire la situation et choisir votre formule")
        
        c_nom, c_statut = st.columns(2)
        with c_nom:
            input_client = st.text_input("Votre nom ou raison sociale :", value=preset["client"])
        with c_statut:
            input_profil = st.selectbox(
                "Votre situation :",
                [
                    "Particulier (Demande ponctuelle)",
                    "Entreprise / Marque (Demande ponctuelle)",
                    "Abonné Prévention P1 Particulier (29 à 59 € HT/mois)",
                    "Abonné Prévention P2 Personnalité (249 à 449 € HT/mois)",
                    "Abonné Prévention P3 Entreprise (229 à 369 € HT/mois)"
                ]
            )
            
        c_plat, c_date = st.columns([1.4, 1])
        with c_plat:
            input_plat = st.text_input("Plateforme ou site concerné :", value=preset["plateforme"])
        with c_date:
            input_date = st.date_input(
                "Date d'apparition du contenu :",
                value=datetime.date.today() - datetime.timedelta(days=preset["jours_pub"])
            )
            
        input_url = st.text_input("Lien (URL) exact du contenu à faire retirer :", value=preset["url"])
        input_faits = st.text_area(
            "Que se passe-t-il ? (Décrivez brièvement le contenu ou collez le message reçu) :",
            value=preset["faits"],
            height=100
        )
        
        st.file_uploader("Joindre une capture d'écran, photo ou vidéo (Chiffrement local — 0 exposition externe) :", type=["png", "jpg", "jpeg", "mp4", "pdf"])
        
        st.markdown("##### Choisissez votre niveau de protection (Forfait fixe, 0 € de frais cachés) :")
        choix_formule = st.radio(
            "Formule d'intervention :",
            [
                "R1 Essentiel (125 € HT) — Signalement officiel aux plateformes, suivi du retrait et 1 semaine de veille anti-republication",
                "R2 Preuve horodatée (150 € HT) — Formule R1 + Capture certifiée inaltérable et rapport de preuve conservé 5 ans",
                "R3 Preuve authentique (320 € HT) — Formule R1 + Constat officiel par Commissaire de justice d'astreinte 24h/24",
                "R4 Retrait judiciaire (1 700 à 2 650 € HT) — Mise en demeure d'avocat puis assignation en référé devant le Tribunal Judiciaire sous astreinte",
                "Utiliser les crédits inclus dans mon abonnement Prévention (P1 / P2 / P3)"
            ],
            index=1
        )
        
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            input_auteur = st.checkbox("Je connais l'identité de l'auteur", value=preset["auteur_connu"])
        with c_opt2:
            input_nuit = st.checkbox("Intervention urgente Nuit / Week-end / Jour férié (+75 € HT sur R1/R2, +150 € HT sur R3)", value=preset["urgence_nuit"])
            
        if st.button("🛡️ PROTÉGER MES DROITS & GÉNÉRER MON ACCUSÉ HORODATÉ", type="primary", use_container_width=True):
            with st.spinner("Sécurisation de la preuve sur le serveur interne du cabinet et alerte de l'avocat de permanence..."):
                time.sleep(0.8)
                now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y à %H:%M:%S UTC")
                jours_ecoules = (datetime.date.today() - input_date).days
                payload = f"REPLIK|{input_client}|{input_url}|{now_utc}|{input_faits}"
                sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                
                st.session_state.active_case = {
                    **preset,
                    "client": input_client,
                    "profil": input_profil,
                    "formule": choix_formule,
                    "plateforme": input_plat,
                    "url": input_url,
                    "jours_pub": jours_ecoules,
                    "auteur_connu": input_auteur,
                    "urgence_nuit": input_nuit,
                    "faits": input_faits,
                    "timestamp": now_utc,
                    "sha256": sha,
                    "statut_avocat": "EN COURS DE VÉRIFICATION PAR L'AVOCAT DE PERMANENCE",
                    "acte_valide": False,
                    "avocat_signataire": "Me. Associé de Permanence (Barreau de Paris)",
                    "acte_final": ""
                }
                st.success("✅ Votre demande est prise en charge ! Votre accusé horodaté est disponible ci-contre.")

    # --- COLONNE DROITE : ACCUSÉ HORODATÉ & SUIVI DU DOSSIER PAR LE CLIENT ---
    with col_suivi:
        ac = st.session_state.active_case
        st.markdown("#### 2. Votre Accusé de Réception Horodaté")
        st.caption("Ce certificat prouve que le contenu existait à cette date précise, même si son auteur le supprime dans quelques minutes.")
        
        st.markdown(f"""
        <div class="cert-box">
            <b>🛡️ ACCUSÉ DE RÉCEPTION & CERTIFICAT D'HORODATAGE — CABINET REPLIK</b><br>
            -----------------------------------------------------------------------<br>
            <b>N° DE DOSSIER :</b> {ac['id']} | <b>CLIENT :</b> {ac['client']}<br>
            <b>DATE & HEURE CERTIFIÉES :</b> {ac['timestamp']}<br>
            <b>URL CONSTATÉE :</b> {ac['url']}<br>
            <b>EMPREINTE NUMÉRIQUE SHA-256 :</b><br>
            {ac['sha256']}<br>
            <b>CONSERVATION :</b> Coffre-fort interne du cabinet (France) — Durée : 5 ans
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("#### 3. Suivi de votre dossier en temps réel")
        
        # Affichage dynamique des 5 étapes selon que l'avocat a validé ou non sur l'Écran 2
        valide = ac["acte_valide"]
        
        s1, s2, s3, s4, s5 = st.columns(5)
        with s1:
            st.markdown("""<div class="step-card-done"><b>01 Détection</b><br><small>✅ URL & preuves capturées</small></div>""", unsafe_allow_html=True)
        with s2:
            st.markdown("""<div class="step-card-done"><b>02 Préparation</b><br><small>✅ Dossier prêt en interne</small></div>""", unsafe_allow_html=True)
        with s3:
            if valide:
                st.markdown("""<div class="step-card-done"><b>03 Validation</b><br><small>✅ Validé par l'avocat</small></div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="step-card-active"><b>03 Validation</b><br><small>⏳ Avocat 24/7 saisi</small></div>""", unsafe_allow_html=True)
        with s4:
            if valide:
                st.markdown("""<div class="step-card-done"><b>04 Action</b><br><small>🚀 Acte officiel envoyé</small></div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="step-card-wait"><b>04 Action</b><br><small>En attente signature</small></div>""", unsafe_allow_html=True)
        with s5:
            st.markdown("""<div class="step-card-done"><b>05 Suivi 7j</b><br><small>🛡️ Veille anti-republication active</small></div>""", unsafe_allow_html=True)

        st.write("")
        if valide:
            st.success(f"⚖️ **Mise à jour de votre avocat ({ac['avocat_signataire']}) :** Votre dossier a été validé et la démarche officielle de retrait a été engagée. Vous pouvez télécharger la copie de l'acte ci-dessous.")
            st.download_button(
                "📥 Télécharger la copie de l'acte envoyé par mon avocat",
                data=ac["acte_final"],
                file_name=f"Copie_Client_{ac['id']}.txt",
                use_container_width=True
            )
        else:
            st.info("👨‍⚖️ **Prochaine étape :** L'avocat de permanence examine actuellement votre dossier (délai moyen : moins de 15 minutes). Aucune démarche n'est engagée sans son contrôle et sa signature.")

        st.markdown("##### 🔍 Veille anti-republication (Incluse pendant 1 semaine)")
        df_suivi_client = pd.DataFrame([
            {"Cible surveillée": ac["plateforme"], "État du lien": "Retrait exigé" if valide else "Preuve figée", "Republications (Miroirs)": "0 copie détectée"},
            {"Cible surveillée": "Moteurs de recherche & Réseaux", "État du lien": "Surveillance continue", "Republications (Miroirs)": "0 copie détectée"}
        ])
        st.dataframe(df_suivi_client, use_container_width=True, hide_index=True)

# ==============================================================================
# ÉCRAN 2 : POSTE AVOCAT DE PERMANENCE (QUALIFICATION IA LOCALE & VALIDATION)
# ==============================================================================
with tab_avocat_dossier:
    ac = st.session_state.active_case
    
    st.subheader(f"⚖️ Poste de Permanence Avocat — Dossier {ac['id']} ({ac['client']})")
    st.caption("Interface interne réservée aux avocats du Cabinet Replik. Analyse effectuée par l'IA locale du cabinet (aucune donnée transmise à l'extérieur).")
    
    # Bandeau supérieur : Alerte Prescription 3 mois (Loi du 29 juillet 1881)
    jours_ecoules = ac["jours_pub"]
    jours_restants = 90 - jours_ecoules
    date_limite = (datetime.date.today() - datetime.timedelta(days=jours_ecoules)) + datetime.timedelta(days=90)
    
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    col_k1.metric("Ancienneté de la publication", f"{jours_ecoules} jours")
    if jours_restants > 0:
        col_k2.metric("Prescription Presse (3 mois)", f"J - {jours_restants}", f"Échéance : {date_limite.strftime('%d/%m/%Y')}")
    else:
        col_k2.metric("Prescription Presse (3 mois)", "EXPIRÉE", f"Dépassée de {abs(jours_restants)} jours", delta_color="inverse")
    col_k3.metric("Identification de l'auteur", "Connu" if ac["auteur_connu"] else "Anonyme / Pseudonyme")
    col_k4.metric("Permanence Nuit / WE", "Oui (Majoration)" if ac["urgence_nuit"] else "Heures ouvrées")

    if jours_restants <= 0:
        st.error("🚨 **ALERTE IA LOCALE — PRESCRIPTION LOI 1881 ACQUISE :** Le délai de 3 mois est dépassé. Les modèles d'actes 'Diffamation / Injure publique' sont automatiquement verrouillés. Bascule recommandée vers la responsabilité civile de droit commun (Art. 1240 C. civ. — Dénigrement, prescription de 5 ans).")
    elif jours_restants <= 15:
        st.warning(f"⚠️ **URGENCE PROCÉDURALE :** Il ne reste que **{jours_restants} jours** pour interrompre la prescription par un acte d'instruction ou une citation.")

    st.divider()
    
    col_ia, col_val = st.columns([1.1, 1])
    
    # --- COLONNE GAUCHE : PRÉ-ANALYSE DE L'IA LOCALE ---
    with col_ia:
        st.markdown("#### 1. Synthèse préparatoire de l'IA Locale (Étape 02)")
        
        st.markdown("**Faits et contenu figés sous empreinte SHA-256 :**")
        st.info(f"« {ac['faits']} »\n\n🔗 **URL :** `{ac['url']}`\n🔐 **Hash :** `{ac['sha256'][:36]}...`")
        
        st.markdown("**Qualifications juridiques pré-identifiées par l'IA locale :**")
        st.success(f"⚖️ {ac['ia_qualification']}")
        
        st.markdown("**Répartition des tâches (Automatisation n8n locale vs Avocat) :**")
        st.markdown(f"- 🤖 **Traité automatiquement par l'IA locale :** {ac['ia_actions']}")
        st.markdown(f"- 👨‍⚖️ **Point de décision renvoyé à l'avocat :** {ac['avocat_arbitrage']}")
        st.markdown(f"- 💼 **Passerelle Contentieux (Gamme Justice) suggérée :** `{ac['suite_justice']}`")

    # --- COLONNE DROITE : CONTRÔLE HUMAIN & GÉNÉRATION D'ACTES ---
    with col_val:
        st.markdown("#### 2. Validation Déontologique & Signature (Étapes 03 & 04)")
        
        avocat_choix = st.selectbox(
            "Avocat d'astreinte intervenant :",
            [
                "Me. Associé Pénal & Presse (Barreau de Paris — Permanence 24/7)",
                "Me. Associé Contentieux Numérique & Référés (Barreau de Paris — Permanence 24/7)"
            ]
        )
        
        type_acte = st.selectbox(
            "Sélectionner l'acte pré-rédigé à émettre :",
            [
                "1. Notification officielle de contenu illicite à la plateforme (Art. 16 DSA & Art. 6-I-5 LCEN)",
                "2. Mise en demeure d'avocat & Projet d'assignation en référé retrait sous astreinte (Formule R4)",
                "3. Requête aux fins d'identification de l'auteur anonyme (Art. 145 CPC / Réquisition IP)",
                "4. Plainte pénale / Citation directe / Constitution de partie civile (Gamme Justice J2A/J2B/J2C)"
            ]
        )
        
        notes_avocat = st.text_area(
            "Instructions et amendements de l'avocat :",
            value=f"Qualification confirmée. {ac['avocat_arbitrage']}",
            height=90
        )
        
        date_jour = datetime.date.today().strftime("%d/%m/%Y")
        brouillon_acte = f"""CABINET REPLIK — AVOCATS AU BARREAU DE PARIS
Permanence Cyber-Urgence 24h/24 | {avocat_choix}
Dossier n° {ac['id']} — Affaire : {ac['client']}

Paris, le {date_jour}

OBJET : {type_acte}
Destinataire : Service Juridique / Hébergeur de {ac['plateforme']}
URL litigieuse : {ac['url']}

Madame, Monsieur,

Le Cabinet REPLIK est le conseil de {ac['client']}.

1. CONSTATATION ET FIGEAGE PROBATOIRE
En date du {ac['timestamp']}, notre système interne a constaté la publication à l'adresse {ac['url']} du contenu suivant :
« {ac['faits']} »

Ce contenu a fait l'objet d'un figeage probatoire inaltérable (Empreinte SHA-256 : {ac['sha256']}) conservé pour une durée de 5 ans.

2. QUALIFICATION JURIDIQUE VALIDÉE PAR L'AVOCAT
Après vérification par l'avocat soussigné, ces faits caractérisent manifestement :
{ac['ia_qualification']}

Observations complémentaires :
{notes_avocat}

3. DEMANDES FORMELLES (RETRAIT IMMÉDIAT & CONSERVATION DES DONNÉES)
En application de l'article 16 du Règlement européen sur les services numériques (DSA) et de l'article 6-I-5 de la LCEN, la connaissance de l'illicéité du contenu est acquise dès réception de la présente notification par ministère d'avocat.

Nous vous mettons en demeure de :
- Retirer ou rendre inaccessible le contenu visé sans délai et prévenir toute republication ;
- Conserver l'intégralité des données d'identification et de connexion de l'auteur (adresse IP, horodatages, coordonnées de création du compte) conformément à l'article 6-II de la LCEN.

À défaut d'exécution immédiate, nous engagerons toute voie de droit utile (référé sous astreinte et poursuites pénales/civiles).

{avocat_choix}
Signature électronique certifiée — Barreau de Paris"""

        st.text_area("Aperçu de l'acte (modifiable par l'avocat avant signature) :", value=brouillon_acte, height=230)
        
        if st.button("✅ VALIDER LA QUALIFICATION, SIGNER L'ACTE & NOTIFIER LE CLIENT", type="primary", use_container_width=True):
            st.session_state.active_case["acte_valide"] = True
            st.session_state.active_case["avocat_signataire"] = avocat_choix
            st.session_state.active_case["acte_final"] = brouillon_acte
            st.session_state.active_case["statut_avocat"] = "VALIDÉ ET ENVOYÉ PAR L'AVOCAT"
            st.success("✅ Acte signé et transmis ! Le statut du client sur l'Écran 1 est désormais passé au vert.")

# ==============================================================================
# ÉCRAN 3 : SUPERVISION CABINET (RADAR PRÉVENTION & PORTEFEUILLE DES 10 DOSSIERS)
# ==============================================================================
with tab_avocat_radar:
    st.subheader("📡 Supervision du Cabinet — Veille Proactive & Registre des Dossiers")
    st.caption("Vue globale de l'activité du cabinet : surveillance automatisée des abonnés Prévention (P1, P2, P3) et répartition du travail entre l'IA locale et les avocats.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Dossiers traités en test", "10 dossiers", "100 % qualifiés")
    m2.metric("Gain de temps par dossier", "14 sec (IA)", "vs 2h30 de préparation manuelle")
    m3.metric("Données exposées hors cabinet", "0 octet", "IA locale + n8n auto-hébergé")
    m4.metric("Validation humaine avocat", "100 %", "Permanence 24h/24 & 7j/7")
    
    st.divider()
    st.markdown("#### 📋 Registre des 10 dossiers types : Ce que l'IA traite vs Ce que l'Avocat décide")
    st.write("Cliquez sur le bouton à droite d'un dossier pour le charger directement dans le **Poste Avocat (Écran 2)** et l'**Espace Client (Écran 1)**.")
    
    for d in DOSSIERS_TYPES:
        with st.expander(f"📁 {d['id']} — {d['label']} | Client : {d['client']} ({d['profil']})"):
            c_info, c_btn = st.columns([4, 1])
            with c_info:
                st.markdown(f"- **Faits signalés :** {d['faits']}")
                st.markdown(f"- 🤖 **Ce que l'IA locale automatise :** {d['ia_actions']}")
                st.markdown(f"- ⚖️ **Ce que l'Avocat contrôle et tranche :** {d['avocat_arbitrage']}")
                st.markdown(f"- 💶 **Formule Réaction :** `{d['formule']}` | **Suite Justice :** `{d['suite_justice']}`")
            with c_btn:
                if st.button("Charger ce dossier", key=f"btn_{d['id']}", use_container_width=True):
                    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y à %H:%M:%S UTC")
                    raw = f"{d['id']}|{d['client']}|{d['url']}|{now_utc}"
                    st.session_state.active_case = {
                        **d,
                        "timestamp": now_utc,
                        "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                        "statut_avocat": "EN ATTENTE DE VALIDATION AVOCAT",
                        "acte_valide": False,
                        "avocat_signataire": "Me. Associé de Permanence (Barreau de Paris)",
                        "acte_final": ""
                    }
                    st.toast(f"Dossier {d['id']} chargé dans l'application !", icon="✅")
